"""Minimal parquet helpers for range reads over HTTP (stdlib only).

Thrift compact decoder (footer, page headers, offset index), snappy decompressor, PLAIN byte-array decoder and an
HTTP range reader that counts bytes. Used by the large-pool audit; no third-party code.
"""
import struct
import time
import urllib.request

BYTES_READ = [0]
REQUESTS = [0]


def http_range(url, start, end_incl, tries=6):
    """Return bytes [start, end_incl] of url (follows redirects). Counts bytes."""
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end_incl}",
                                                       "User-Agent": "mtp-poolscout/1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                if r.status not in (200, 206):
                    raise IOError(f"status {r.status}")
                b = r.read()
            REQUESTS[0] += 1
            BYTES_READ[0] += len(b)
            if r.status == 200:  # server ignored Range: refuse silently large reads
                raise IOError("server ignored Range header")
            if len(b) != end_incl - start + 1:
                raise IOError(f"short read {len(b)} != {end_incl - start + 1}")
            return b
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


class TReader:
    def __init__(self, b, pos=0):
        self.b, self.p = b, pos

    def byte(self):
        v = self.b[self.p]
        self.p += 1
        return v

    def varint(self):
        s = r = 0
        while True:
            x = self.byte()
            r |= (x & 0x7F) << s
            s += 7
            if not x & 0x80:
                return r

    def zz(self):
        n = self.varint()
        return (n >> 1) ^ -(n & 1)

    def binary(self):
        n = self.varint()
        v = self.b[self.p:self.p + n]
        self.p += n
        return bytes(v)

    def value(self, t):
        if t == 1:
            return True
        if t == 2:
            return False
        if t == 3:
            v = self.byte()
            return v - 256 if v > 127 else v
        if t in (4, 5, 6):
            return self.zz()
        if t == 7:
            v = struct.unpack("<d", self.b[self.p:self.p + 8])[0]
            self.p += 8
            return v
        if t == 8:
            return self.binary()
        if t in (9, 10):
            h = self.byte()
            n, et = h >> 4, h & 0x0F
            if n == 15:
                n = self.varint()
            out = []
            for _ in range(n):
                if et in (1, 2):
                    out.append(self.byte() == 1)
                else:
                    out.append(self.value(et))
            return out
        if t == 11:
            n = self.varint()
            if n == 0:
                return {}
            kv = self.byte()
            kt, vt = kv >> 4, kv & 0x0F
            return {self.value(kt): self.value(vt) for _ in range(n)}
        if t == 12:
            return self.struct()
        raise ValueError(f"thrift type {t}")

    def struct(self):
        out, last = {}, 0
        while True:
            h = self.byte()
            if h == 0:
                return out
            d, t = h >> 4, h & 0x0F
            fid = last + d if d else self.zz()
            last = fid
            out[fid] = self.value(t)


def parse_footer(tail):
    """tail ends with <len><PAR1>; returns (FileMetaData dict, footer_len)."""
    assert tail[-4:] == b"PAR1", "not parquet"
    n = struct.unpack("<I", tail[-8:-4])[0]
    fm = TReader(tail[-8 - n:-8]).struct()
    return fm, n


def snappy_decompress(b):
    r = TReader(b)
    n = r.varint()
    out = bytearray()
    p = r.p
    while p < len(b):
        tag = b[p]
        p += 1
        t = tag & 3
        if t == 0:
            ln = tag >> 2
            if ln >= 60:
                k = ln - 59
                ln = int.from_bytes(b[p:p + k], "little")
                p += k
            ln += 1
            out += b[p:p + ln]
            p += ln
        else:
            if t == 1:
                ln = ((tag >> 2) & 7) + 4
                off = ((tag >> 5) << 8) | b[p]
                p += 1
            elif t == 2:
                ln = (tag >> 2) + 1
                off = int.from_bytes(b[p:p + 2], "little")
                p += 2
            else:
                ln = (tag >> 2) + 1
                off = int.from_bytes(b[p:p + 4], "little")
                p += 4
            st = len(out) - off
            for i in range(ln):  # overlapping copies allowed
                out.append(out[st + i])
    assert len(out) == n, (len(out), n)
    return bytes(out)


def rle_hybrid(b, bit_width, count):
    """Decode RLE/bit-packed hybrid (no length prefix) into count ints."""
    r = TReader(b)
    out = []
    bw = (bit_width + 7) // 8
    while len(out) < count and r.p < len(b):
        h = r.varint()
        if h & 1:
            ng = h >> 1
            nbytes = ng * bit_width
            chunk = int.from_bytes(b[r.p:r.p + nbytes], "little")
            r.p += nbytes
            mask = (1 << bit_width) - 1
            for i in range(ng * 8):
                out.append((chunk >> (i * bit_width)) & mask)
        else:
            run = h >> 1
            v = int.from_bytes(b[r.p:r.p + bw], "little")
            r.p += bw
            out.extend([v] * run)
    return out[:count]


def plain_byte_arrays(b, n):
    out, p = [], 0
    for _ in range(n):
        ln = struct.unpack("<I", b[p:p + 4])[0]
        out.append(bytes(b[p + 4:p + 4 + ln]))
        p += 4 + ln
    return out, p
