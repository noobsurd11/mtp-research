"""Fetch selected rows' PNG bytes from sasan/scdd-unlabeled without reading whole row groups.

Each row group stores its 100 images as one snappy-compressed PLAIN dictionary page ([u32 len][png] per row, in row
order). Snappy works in independent 64 KiB fragments; for PNG data almost every fragment is a single literal
(3-byte header), with a few short copies near PNG headers. So:
  walk: from the page start, hop image to image: predict the compressed position of the next [len][\\x89PNG...]
        assuming literal fragments, read a ~600-byte window, find the PNG signature, read len. One request per hop.
  fetch: for a target row, identify the start of the fragment holding its first byte (literal tag check), then
        snappy-decode fragment by fragment (exact tag parsing) up to the image end.
  verify: every PNG chunk CRC32 is recomputed; IEND must close the image; the image must decode in PIL.
Bytes are written to <sample_dir>/r<global_row>.png (untrusted data; never executed). Logs every request count.
Usage: python -I sampler.py <rowgroups.json> <targets.tsv: global_row shard rg row_in_rg> <sample_dir> <log.jsonl> [threads] [byte_cap]
"""
import json
import struct
import sys
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pq_lite as P  # noqa: E402

REV = "7c4e73d8590ad7fa026b472b6745bb9b2ca9b671"
BASE = f"https://huggingface.co/datasets/sasan/scdd-unlabeled/resolve/{REV}/"
SIG = b"\x89PNG\r\n\x1a\n"
FR = 65536
LOCK = threading.Lock()
CAP = 10**12


def resolve(name, tries=6):
    import urllib.request
    for k in range(tries):
        try:
            req = urllib.request.Request(BASE + name, headers={"Range": "bytes=0-3", "User-Agent": "mtp-poolscout/1"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                with LOCK:
                    P.REQUESTS[0] += 1
                    P.BYTES_READ[0] += len(b)
                assert b == b"PAR1"
                return r.geturl()
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))


def lit_hdr_len(tag):
    ln = tag >> 2
    return 1 if ln < 60 else 1 + (ln - 59)


def snappy_fragment(b, p, need, want=None):
    """Parse one fragment's tags from b[p:] until `need` output bytes (or `want` bytes, for a final partial
    fragment); returns (bytes, next_p) or raises."""
    want = need if want is None else want
    out = bytearray()
    while len(out) < want:
        if p >= len(b):
            raise EOFError
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
            if p + ln > len(b):
                if want < need and len(out) + len(b) - p >= want:
                    out += b[p:]
                    return bytes(out[:want]), len(b)
                raise EOFError
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
            if off == 0 or off > len(out):
                raise ValueError("bad copy offset")
            st = len(out) - off
            for i in range(ln):
                out.append(out[st + i])
    if want == need and len(out) != need:
        raise ValueError("fragment overrun")
    return bytes(out[:want]), p


def png_ok(png):
    """Recompute every chunk CRC; True if the PNG is complete and consistent."""
    if png[:8] != SIG:
        return False, "sig"
    q = 8
    while q + 12 <= len(png):
        ln = struct.unpack(">I", png[q:q + 4])[0]
        ct = png[q + 4:q + 8]
        if q + 12 + ln > len(png):
            return False, "trunc"
        if zlib.crc32(png[q + 4:q + 8 + ln]) != struct.unpack(">I", png[q + 8 + ln:q + 12 + ln])[0]:
            return False, f"crc {ct}"
        q += 12 + ln
        if ct == b"IEND":
            return q == len(png), "tail" if q != len(png) else "ok"
    return False, "noiend"


def read_indices(url, meta):
    """Row -> dictionary index for the image.bytes column (data page v1, RLE_DICTIONARY, max def level 2)."""
    off = meta["img_data_off"]
    end = meta["img_dict_off"] + meta["img_comp"]
    b = P.http_range(url, off, end - 1)
    r = P.TReader(b)
    h = r.struct()
    hl = r.p
    assert h[1] == 0, h
    raw = b[hl:hl + h[3]]
    data = P.snappy_decompress(raw) if meta["img_codec"] == 1 else raw
    n = h[5][1]
    ln = struct.unpack("<I", data[:4])[0]
    defs = P.rle_hybrid(data[4:4 + ln], 2, n)
    q = 4 + ln
    nn = sum(d == 2 for d in defs)
    idx = P.rle_hybrid(data[q + 1:], data[q], nn)
    it = iter(idx)
    return [next(it) if d == 2 else None for d in defs]


class RG:
    def __init__(self, url, meta):
        self.url = url
        off = meta["img_dict_off"]
        hdr = P.http_range(url, off, off + 160)
        r = P.TReader(hdr)
        h = r.struct()
        hl = r.p
        assert h[1] == 2, h
        self.ndict = h[7][1]
        self.row2dict = list(range(meta["rows"]))
        if self.ndict != meta["rows"]:  # duplicate PNG bytes inside the row group: map rows via the index page
            self.row2dict = read_indices(url, meta)
        self.U, self.C = h[2], h[3]
        r2 = P.TReader(hdr, hl)
        assert r2.varint() == self.U
        self.F0 = off + r2.p  # fragment 0 start (absolute)
        tag = hdr[r2.p]
        assert tag & 3 == 0
        self.anchor = (0, self.F0 + lit_hdr_len(tag))  # (uncompressed offset, absolute compressed position)
        self.rows = meta["rows"]
        self.starts = {}  # row -> (o, c, len)

    def predict(self, o):
        oa, ca = self.anchor
        return ca + (o - oa) + 3 * (o // FR - oa // FR)

    def probe(self, o, w_back=384, w_fwd=128):
        """Find [len][SIG] for the image starting at uncompressed o; returns (c_of_len, len)."""
        for wb, wf in ((w_back, w_fwd), (8192, 1024), (65536, 4096)):
            c = self.predict(o)
            lo, hi = max(self.F0, c - wb), c + 12 + wf
            b = P.http_range(self.url, lo, hi)
            for j in [None] + [x for x in range(len(b)) if b[x:x + 3] == b"\xf4\xff\xff"]:
                bb = b if j is None else b[:j] + b[j + 3:]  # stitch across one fragment header
                cands = []
                i = bb.find(SIG)
                while i >= 0:
                    cands.append(i)
                    i = bb.find(SIG, i + 1)
                cands = [i for i in cands if i >= 4]
                if cands:
                    i = min(cands, key=lambda q: abs(lo + q - 4 - c))
                    ln = struct.unpack("<I", bb[i - 4:i])[0]
                    pos = lo + i - 4
                    if j is not None and i - 4 >= j:
                        pos += 3
                    return pos, ln
        raise LookupError(f"no PNG signature near uncompressed {o}")

    def walk_to(self, row, cache):
        """Return (o, c, len) of `row` (via its dictionary entry), hopping from the nearest known entry."""
        row = self.row2dict[row]
        known = [k for k in cache if k <= row]
        k = max(known) if known else 0
        if k == 0 and 0 not in cache:
            c, ln = self.probe(0)
            cache[0] = (0, c, ln)
        o, c, ln = cache[k]
        self.anchor = (o, c)
        while k < row:
            o2 = o + 4 + ln
            c2, ln2 = self.probe(o2)
            if not (100 < ln2 < 50_000_000 and o2 + 4 + ln2 <= self.U):
                raise ValueError(f"implausible len {ln2} at row {k + 1}")
            k, o, c, ln = k + 1, o2, c2, ln2
            self.anchor = (o, c)
            cache[k] = (o, c, ln)
        return cache[row]

    def fetch(self, o, c, ln):
        """Decode [len][png] at uncompressed o (compressed c) exactly; returns png bytes."""
        k0, r = o // FR, o % FR
        nfr = (o + 4 + ln - 1) // FR - k0 + 1
        lo = c - r - 3 - 4096  # copies can make the fragment prefix longer or shorter than r + 3
        hi = c + 4 + ln + 3 * nfr + 2048
        b = P.http_range(self.url, max(self.F0, lo), min(hi, self.F0 + self.C))
        base = max(self.F0, lo)
        need_total = r + 4 + ln
        # fragment k0 start: pure-literal prediction first (c - r - 3), then nearby positions, nearest first
        # (copies earlier in fragment k0 make its compressed prefix shorter or longer than r + 3)
        if k0 > 0:
            cand = [c - r - 3 - base] + [c - r - base + d for d in sorted(range(-4096, 1200), key=abs)]
        else:
            cand = [self.F0 - base]
        seen = set()
        for s in cand:
            if s in seen:
                continue
            seen.add(s)
            if s < 0 or s >= len(b) or b[s] & 3 != 0:
                continue
            try:
                out, p = bytearray(), s
                kk = k0
                while len(out) < need_total:
                    need = min(FR, self.U - kk * FR)
                    frag, p = snappy_fragment(b, p, need, min(need, need_total - len(out)))
                    out += frag
                    kk += 1
                if bytes(out[r:r + 4]) != struct.pack("<I", ln) or bytes(out[r + 4:r + 12]) != SIG:
                    continue
                png = bytes(out[r + 4:r + 4 + ln])
                ok, why = png_ok(png)
                if ok:
                    return png
            except (ValueError, EOFError, IndexError):
                continue
        raise ValueError("could not decode image bytes")


def run_group(args):
    name, rgmeta, rows, sample_dir = args
    res = []
    try:
        url = resolve(name)
        rg = RG(url, rgmeta)
    except Exception as e:
        for row_in_rg, grow in rows:
            res.append(dict(global_row=grow, shard=name, rg=rgmeta["rg"], row_in_rg=row_in_rg, ok=False,
                            err=f"rg init {type(e).__name__}: {e}"))
        return res, []
    cache = {}
    for row_in_rg, grow in sorted(rows):
        t0 = time.time()
        rec = dict(global_row=grow, shard=name, rg=rgmeta["rg"], row_in_rg=row_in_rg)
        if P.BYTES_READ[0] > CAP:
            rec.update(ok=False, err="byte cap reached")
            res.append(rec)
            continue
        try:
            o, c, ln = rg.walk_to(row_in_rg, cache)
            png = rg.fetch(o, c, ln)
            (Path(sample_dir) / f"r{grow}.png").write_bytes(png)
            rec.update(ok=True, png_bytes=len(png), unc_offset=o, comp_pos=c)
        except Exception as e:  # recorded, row skipped
            rec.update(ok=False, err=f"{type(e).__name__}: {e}")
        rec["secs"] = round(time.time() - t0, 1)
        res.append(rec)
    g0 = rows[0][1] - rows[0][0] if rows else 0  # global row of row_in_rg 0
    inv = {}
    for i, d in enumerate(rg.row2dict):
        inv.setdefault(d, i)
    walked = [dict(global_row=g0 + inv[k], dict_entry=k, png_len=v[2], unc_offset=v[0], ndict=rg.ndict)
              for k, v in sorted(cache.items())]
    return res, walked


def main():
    rgj, tg, sd, logp = sys.argv[1:5]
    th = int(sys.argv[5]) if len(sys.argv) > 5 else 6
    global CAP
    CAP = int(float(sys.argv[6])) if len(sys.argv) > 6 else CAP  # stop fetching once this many bytes were read
    meta = json.load(open(rgj))
    by = {}
    done = set()
    if Path(logp).exists():
        done = {json.loads(x)["global_row"] for x in open(logp) if x.strip() and json.loads(x).get("ok")}
    for ln in open(tg):
        if not ln.strip() or ln.startswith("global_row"):
            continue
        g, sh, rgi, ri = ln.split("\t")[:4]
        g, sh, rgi, ri = int(g), int(sh), int(rgi), int(ri)
        if g in done:
            continue
        name = f"data/train-{sh:05d}-of-00302.parquet"
        by.setdefault((name, rgi), []).append((ri, g))
    jobs = [(name, meta[name]["rowgroups"][rgi], rows, sd) for (name, rgi), rows in sorted(by.items())]
    Path(sd).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    n = 0
    with ThreadPoolExecutor(th) as ex, open(logp, "a") as f, open(str(logp) + ".walked", "a") as fw:
        for res, walked in ex.map(run_group, jobs):
            for rec in res:
                f.write(json.dumps(rec) + "\n")
                n += 1
            for w in walked:
                fw.write(json.dumps(w) + "\n")
            f.flush()
            fw.flush()
            print(f"{n} rows, {P.REQUESTS[0]} req, {P.BYTES_READ[0] / 1e6:.1f} MB, {time.time() - t0:.0f}s", flush=True)
    print(f"done: {n} rows, requests {P.REQUESTS[0]}, bytes {P.BYTES_READ[0]}")


if __name__ == "__main__":
    main()
