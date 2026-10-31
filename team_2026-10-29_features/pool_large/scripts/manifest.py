"""Full row manifest of HF sasan/scdd-unlabeled without downloading images.

Per shard: read the parquet footer (range read), then per row group read only the small column chunks
image.path, label and file_path (contiguous, about 3 KB), decode them with pq_lite (stdlib only).
Writes <out>/manifest.tsv (global_row, shard, rg, row_in_rg, label, file_path, image_path) and
<out>/rowgroups.json (per row group: rows, image.bytes chunk offsets and sizes), <out>/manifest_log.txt.
Usage: python -I manifest.py <hf_api.json> <out_dir> [threads]
"""
import json
import struct
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pq_lite as P  # noqa: E402

REV = "7c4e73d8590ad7fa026b472b6745bb9b2ca9b671"
BASE = f"https://huggingface.co/datasets/sasan/scdd-unlabeled/resolve/{REV}/"


def decode_chunk(buf, base_off, start, length, max_def, codec):
    """Decode a BYTE_ARRAY column chunk (dictionary + data pages). Returns list of values (None for nulls)."""
    p = start - base_off
    end = p + length
    dic, vals = None, []
    while p < end:
        r = P.TReader(buf, p)
        h = r.struct()
        hl = r.p - p
        csz = h[3]
        raw = buf[p + hl:p + hl + csz]
        p += hl + csz
        ptype = h[1]
        if ptype == 2:  # dictionary page
            data = P.snappy_decompress(raw) if codec == 1 else raw
            assert codec in (0, 1)
            dic, _ = P.plain_byte_arrays(data, h[7][1])
        elif ptype == 0:  # data page v1
            data = P.snappy_decompress(raw) if codec == 1 else raw
            dh = h[5]
            n = dh[1]
            q = 0
            if max_def > 0:
                ln = struct.unpack("<I", data[q:q + 4])[0]
                defs = P.rle_hybrid(data[q + 4:q + 4 + ln], max_def.bit_length(), n)
                q += 4 + ln
            else:
                defs = [0] * n
            nn = sum(d == max_def for d in defs)
            enc = dh[2]
            if enc in (8, 2):  # RLE_DICTIONARY / PLAIN_DICTIONARY
                bw = data[q]
                idx = P.rle_hybrid(data[q + 1:], bw, nn)
                nv = [dic[i] for i in idx]
            elif enc == 0:
                nv, _ = P.plain_byte_arrays(data[q:], nn)
            else:
                raise ValueError(f"encoding {enc}")
            it = iter(nv)
            vals.extend(next(it) if d == max_def else None for d in defs)
        else:
            raise ValueError(f"page type {ptype}")
    return vals


def resolve(url, tries=6):
    import urllib.request
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Range": "bytes=0-3", "User-Agent": "mtp-poolscout/1"})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                P.REQUESTS[0] += 1
                P.BYTES_READ[0] += len(b)
                assert b == b"PAR1", b
                return r.geturl()
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))


CACHE = None


def do_shard_cached(item):
    f = CACHE / (item[0].split("/")[-1] + ".json")
    if f.exists():
        return tuple(json.load(open(f)))
    r = do_shard(item)
    json.dump(r, open(f, "w"))
    return r


def do_shard(item):
    name, size = item
    url = resolve(BASE + name)
    tl = min(size, 16384)
    tail = P.http_range(url, size - tl, size - 1)
    n = struct.unpack("<I", tail[-8:-4])[0]
    if n + 8 > tl:
        tail = P.http_range(url, size - n - 8, size - 1)
    fm, _ = P.parse_footer(tail)
    cols = [".".join(x.decode() for x in c[3][3]) for c in fm[4][0][1]]
    assert cols == ["image.bytes", "image.path", "label", "file_path"], cols
    rows, rgs = [], []
    for gi, rg in enumerate(fm[4]):
        cc = [c[3] for c in rg[1]]

        def span(m):
            s = m.get(11) if m.get(11) is not None else m[9]
            return s, m[7]
        sp = [span(m) for m in cc]
        lo = min(s for s, _ in sp[1:])
        hi = max(s + ln for s, ln in sp[1:])
        buf = P.http_range(url, lo, hi - 1)
        ipath = decode_chunk(buf, lo, *sp[1], 2, cc[1][4])
        lab = decode_chunk(buf, lo, *sp[2], 1, cc[2][4])
        fp = decode_chunk(buf, lo, *sp[3], 1, cc[3][4])
        nr = rg[3]
        assert len(ipath) == len(lab) == len(fp) == nr, (name, gi, len(ipath), len(lab), len(fp), nr)
        for i in range(nr):
            rows.append((gi, i, (lab[i] or b"").decode(), (fp[i] or b"").decode(), (ipath[i] or b"").decode()))
        m0 = cc[0]
        rgs.append(dict(rg=gi, rows=nr, img_dict_off=m0.get(11), img_data_off=m0[9], img_comp=m0[7],
                        img_unc=m0[6], img_codec=m0[4], img_enc=m0[2]))
    return name, size, fm[3], fm.get(6, b"").decode(), rows, rgs


def main():
    api, out = sys.argv[1], Path(sys.argv[2])
    th = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    out.mkdir(parents=True, exist_ok=True)
    sib = json.load(open(api))["siblings"]
    shards = sorted((s["rfilename"], s["size"]) for s in sib if s["rfilename"].startswith("data/train-"))
    assert len(shards) == 302
    global CACHE
    CACHE = out / "shard_cache"
    CACHE.mkdir(exist_ok=True)
    t0 = time.time()
    res = {}
    with ThreadPoolExecutor(th) as ex:
        for k, r in enumerate(ex.map(do_shard_cached, shards)):
            res[r[0]] = r
            if k % 25 == 0:
                print(f"{k + 1}/302 shards, {P.REQUESTS[0]} req, {P.BYTES_READ[0] / 1e6:.2f} MB, "
                      f"{time.time() - t0:.0f}s", flush=True)
    g = 0
    meta = {}
    with open(out / "manifest.tsv", "w") as f:
        f.write("global_row\tshard\trg\trow_in_rg\tlabel\tfile_path\timage_path\n")
        for name, size in shards:
            _, sz, nrows, cb, rows, rgs = res[name]
            si = int(name.split("-")[1])
            meta[name] = dict(shard=si, size=sz, rows=nrows, created_by=cb, rowgroups=rgs, first_global_row=g)
            for gi, i, lab, fp, ip in rows:  # noqa
                f.write(f"{g}\t{si}\t{gi}\t{i}\t{lab}\t{fp}\t{ip}\n")
                g += 1
    json.dump(meta, open(out / "rowgroups.json", "w"))
    msg = (f"shards 302, rows {g}, requests {P.REQUESTS[0]}, bytes {P.BYTES_READ[0]} "
           f"({P.BYTES_READ[0] / 1e6:.2f} MB), {time.time() - t0:.0f}s")
    print(msg)
    (out / "manifest_log.txt").write_text(msg + "\n")


if __name__ == "__main__":
    main()
