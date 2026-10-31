"""Choose sample rows.

Random part: stratified by shard, K rows per shard drawn uniformly without replacement (seed fixed). Design weight
per row = shard_rows / K. Targeted part (verification only, never used for rate estimates): rows whose stem equals one
of our labelled / E1 / _rf cells, preferring small row_in_rg (cheaper walk).
Random rows are restricted to row_in_rg < MAXPOS (walk cost; row order inside a row group is checked to be
unrelated to module/source in the report).
Usage: python -I select_targets.py <out_dir> <K> <seed> <n_targeted_per_set> [MAXPOS]
Writes targets.tsv (global_row shard rg row_in_rg part set stem label est_bytes) and prints the byte estimate.
"""
import collections
import csv
import json
import random
import sys
from pathlib import Path

out, K, seed, nt = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
MAXPOS = int(sys.argv[5]) if len(sys.argv) > 5 else 100
rows = list(csv.DictReader(open(out / "manifest.tsv"), delimiter="\t"))
prof = json.load(open(out / "manifest_profile.json"))
mb = prof["mean_png_bytes_by_label"]
ov = list(csv.DictReader(open(out / "id_overlap.tsv"), delimiter="\t"))
rng = random.Random(seed)
by_shard = collections.defaultdict(list)
for r in rows:
    by_shard[int(r["shard"])].append(r)
sel = []
for sh in sorted(by_shard):
    elig = [r for r in by_shard[sh] if int(r["row_in_rg"]) < MAXPOS]
    for r in rng.sample(elig, K):
        sel.append((r, "random", ""))
taken = {int(r["global_row"]) for r, _, _ in sel}
for setname in ("test", "val", "e1", "rf17", "train", "rf117", "d7_twins"):
    c = [o for o in ov if o["set"] == setname and int(o["global_row"]) not in taken]
    c.sort(key=lambda o: (int(o["row_in_rg"]), o["stem"]))
    for o in c[:nt]:
        sel.append((rows[int(o["global_row"])], "targeted", setname))
        taken.add(int(o["global_row"]))
# duplicate stems (same stem in two folders): both rows of the 2 cheapest pairs; and module CSIR_00300 (E1 module)
d = collections.defaultdict(list)
for r in rows:
    d[Path(r["file_path"]).stem].append(r)
dps = sorted((v for v in d.values() if len(v) == 2), key=lambda v: max(int(x["row_in_rg"]) for x in v))
for v in dps[:2]:
    for r in v:
        if int(r["global_row"]) not in taken:
            sel.append((r, "targeted", "dup_stem"))
            taken.add(int(r["global_row"]))
m300 = sorted((r for r in rows if Path(r["file_path"]).stem.startswith("CSIR_00300_")), key=lambda r: int(r["row_in_rg"]))
for r in m300[:2]:
    if int(r["global_row"]) not in taken:
        sel.append((r, "targeted", "e1_module_300"))
        taken.add(int(r["global_row"]))
est = 0
with open(out / "targets.tsv", "w") as f:
    f.write("global_row\tshard\trg\trow_in_rg\tpart\tset\tstem\tlabel\test_bytes\n")
    for r, part, s in sorted(sel, key=lambda x: int(x[0]["global_row"])):
        e = mb.get(r["label"], 600_000)
        est += e
        f.write(f"{r['global_row']}\t{r['shard']}\t{r['rg']}\t{r['row_in_rg']}\t{part}\t{s}\t"
                f"{Path(r['file_path']).stem}\t{r['label']}\t{e:.0f}\n")
hops = collections.defaultdict(int)
for r, _, _ in sel:
    k = (r["shard"], r["rg"])
    hops[k] = max(hops[k], int(r["row_in_rg"]))
print(f"selected {len(sel)} rows ({sum(p == 'random' for _, p, _ in sel)} random), est image bytes {est / 1e6:.0f} MB, "
      f"row groups {len(hops)}, total hops {sum(hops.values())}")
