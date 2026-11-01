"""T9 gate (found, 31 Oct): are the scored _rf images identical to their pool copies (the BN siblings' source)?
Compares calib's rf images (/home/noob/work/calib/data/rf/images, as scored) with data/unlabeled/images_512/<stem without _rf>.png.
Read-only, CPU. Prints per-cell max |diff|, mean |diff|, Pearson r, and a summary; also counts siblings per module."""
import collections
from pathlib import Path
import numpy as np
from PIL import Image
RF = Path("/home/noob/work/calib/data/rf"); POOL = Path("/home/noob/work/el-fault-detection/data/unlabeled/images_512")
pool = {p.stem for p in POOL.glob("*.png")}
stems = [l.strip() for l in open(RF / "stems_eval.txt") if l.strip()]
rows = []
for s in stems:
    b = s[:-3] if s.endswith("_rf") else s
    if b not in pool:
        rows.append((s, None)); continue
    x = np.array(Image.open(RF / "images" / f"{s}.png").convert("L"), np.float64)
    y = np.array(Image.open(POOL / f"{b}.png").convert("L"), np.float64)
    if x.shape != y.shape:
        rows.append((s, ("shape", x.shape, y.shape))); continue
    d = np.abs(x - y)
    r = np.corrcoef(x.ravel(), y.ravel())[0, 1]
    rows.append((s, (d.max(), d.mean(), r, x.mean(), y.mean(), x.std(), y.std())))
have = [r for r in rows if r[1] is not None and r[1][0] != "shape"]
shp = [r for r in rows if r[1] is not None and r[1][0] == "shape"]
print(f"rf cells {len(stems)}; with pool copy {len(have) + len(shp)}; shape mismatch {len(shp)}; no pool copy {sum(1 for r in rows if r[1] is None)}")
if have:
    mx = np.array([r[1][0] for r in have]); mn = np.array([r[1][1] for r in have]); rr = np.array([r[1][2] for r in have])
    print(f"identical (max|d|=0): {int((mx == 0).sum())}; max|d| median {np.median(mx):.1f} max {mx.max():.1f}; mean|d| median {np.median(mn):.3f} max {mn.max():.3f}; r min {rr.min():.5f} median {np.median(rr):.5f}")
    bad = sorted(have, key=lambda r: -r[1][1])[:8]
    for s, v in bad:
        print(f"  {s}: max|d| {v[0]:.0f} mean|d| {v[1]:.2f} r {v[2]:.4f} mean rf/pool {v[3]:.1f}/{v[4]:.1f} sd {v[5]:.1f}/{v[6]:.1f}")
for s, v in shp[:5]:
    print("  shape", s, v)
mod = lambda s: "_".join(s.split("_")[:2])
pm = collections.Counter(mod(p) for p in pool)
ctx = {}
for l in open(RF / "rf_context.tsv"):
    if l.strip():
        ctx[l.split("\t")[0]] = l.rstrip("\n")
print("rf_context sample:", list(ctx.values())[:2])
sib = collections.Counter()
for s in stems:
    sib[pm.get(mod(s), 0) >= 20] += 1
print(f"rf cells in modules with >= 20 pool siblings: {sib[True]} of {len(stems)}")
