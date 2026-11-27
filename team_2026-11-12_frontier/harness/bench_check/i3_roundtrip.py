"""I3: per-cell m0 records from `pred` vs from where(m_crack > 0, 14, oth): counts of differing cells / fields and ties only."""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/noob/work/el_bench")
import numpy as np
from bench import dumpfmt, sets
from bench.m0core import cell_stats
d = Path(sys.argv[1]); S = sets.resolve(sys.argv[2])
nd = ncell = ties = 0
for s in S["stems"]:
    c = dumpfmt.read_cell(d / f"{s}.npz")
    gt = np.array(__import__("PIL.Image").Image.open(S["masks"] / f"{s}.png"))
    implied = np.where(c["m_crack"].astype(np.float32) > 0, 14, c["oth"]).astype(np.uint8)
    t = int((implied != c["pred"]).sum()); ties += t
    a, b = cell_stats(c["pred"], gt, None, c["p_crack"]), cell_stats(implied, gt, None, c["p_crack"])
    k = sum(a[f] != b[f] for f in a); nd += k; ncell += k > 0
print(f"{'IDENTICAL' if nd == 0 else 'DIFF'}: {len(S['stems'])} cells; tie px {ties}; cells with a differing record {ncell}; differing fields {nd}")
