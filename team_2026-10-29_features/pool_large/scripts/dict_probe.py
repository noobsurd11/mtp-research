"""Exact within-row-group duplicate PNG count for the whole HF dataset, from parquet dictionary page headers.

The image column is dictionary-encoded per row group, so rows - dictionary entries = rows whose PNG bytes are
byte-identical to an earlier row of the same row group. Reads ~160 bytes per row group; for row groups with
duplicates also reads the small index page to list the duplicate rows.
Usage: python -I dict_probe.py <rowgroups.json> <manifest.tsv> <out.json> [threads]
"""
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pq_lite as P  # noqa: E402
import sampler as S  # noqa: E402


def probe(item):
    name, m = item
    url = S.resolve(name)
    res = []
    g0 = m["first_global_row"]
    for rg in m["rowgroups"]:
        b = P.http_range(url, rg["img_dict_off"], rg["img_dict_off"] + 160)
        h = P.TReader(b).struct()
        nd = h[7][1]
        rec = dict(shard=name, rg=rg["rg"], rows=rg["rows"], ndict=nd, first_global_row=g0)
        if nd != rg["rows"]:
            idx = S.read_indices(url, rg)
            seen = {}
            pairs = []
            for i, d in enumerate(idx):
                if d in seen:
                    pairs.append((g0 + seen[d], g0 + i))
                else:
                    seen[d] = i
            rec["dup_pairs"] = pairs
        res.append(rec)
        g0 += rg["rows"]
    return res


def main():
    meta = json.load(open(sys.argv[1]))
    man = {int(r["global_row"]): r for r in csv.DictReader(open(sys.argv[2]), delimiter="\t")}
    th = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    out = []
    with ThreadPoolExecutor(th) as ex:
        for res in ex.map(probe, sorted(meta.items())):
            out.extend(res)
    pairs = [(a, b, man[a]["file_path"], man[b]["file_path"]) for r in out for a, b in r.get("dup_pairs", [])]
    summ = dict(row_groups=len(out), rows=sum(r["rows"] for r in out), dict_entries=sum(r["ndict"] for r in out),
                rgs_with_dups=sum(r["ndict"] != r["rows"] for r in out), dup_rows=sum(r["rows"] - r["ndict"] for r in out),
                pairs=pairs, requests=P.REQUESTS[0] + S.P.REQUESTS[0], bytes=P.BYTES_READ[0])
    json.dump(dict(summary=summ, per_rg=out), open(sys.argv[3], "w"), indent=0)
    print(json.dumps({k: v for k, v in summ.items() if k != "pairs"}), "pairs:", pairs[:40])


if __name__ == "__main__":
    main()
