"""EXPLORATORY robustness of arm differences to WHICH test cells are in the split (per_image_scores.py output).

For each pair A:B and class: dataset-level IoU difference (mean over seeds), the same with the top-3 cells (by GT area of
that class, fixed per split) removed, and a 95% image-bootstrap interval (cells resampled with replacement, paired across
arms and seeds). The locked rules use seeds only; this adds the test-sampling dimension they ignore.

Usage: python per_image_analysis.py --json results/p6/per_image.json [more.json] --check results/p6/raw \
          --pairs p6:L0_10pct=p6:L1_10pct p6:L1_10pct=p6:L2_10pct ... [--split test] [--B 2000]
"""
import argparse, glob, json, os, re
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--json", nargs="+", required=True)
ap.add_argument("--check", default=None, help="dir of re-score JSONs to verify summed IoU against")
ap.add_argument("--pairs", nargs="+", required=True, help="exp:arm=exp:arm (B minus A is reported)")
ap.add_argument("--split", default="test")
ap.add_argument("--B", type=int, default=2000)
ap.add_argument("--merge", nargs="*", default=[], help="NEW=ARM1+ARM2: pool the seeds of two arms")
ap.add_argument("--keep", default=None, help="regex: only test cells whose stem matches (e.g. ^(CSIR|ARTS)_ for the P9 source split)")
a = ap.parse_args()

P = {}
for f in a.json:
    P.update(json.load(open(f)))
arms = {}  # "exp:arm" -> {seed: {stem: counts}}
for key, v in P.items():
    split, run = key.split("/", 1)
    if split != a.split:
        continue
    exp, arm, s = re.match(r"^(p\d+)_(.+)_s(\d+)$", run).groups()
    arms.setdefault(f"{exp}:{arm}", {})[int(s)] = v

if a.check:
    ref = {}
    for f in glob.glob(os.path.join(a.check, "*.json")):
        ref.update(json.load(open(f)))
    worst = 0.0
    for key, v in P.items():
        if key in ref:
            t = np.array(list(v.values())).sum(0)
            for i, c in ((0, "crack"), (3, "inactive")):
                worst = max(worst, abs(t[i] / max(t[i:i + 3].sum(), 1) - ref[key]["new_escdd"][c]["iou"]))
    print(f"sanity: max |summed per-image IoU - re-score IoU| = {worst:.2e}")

for mg in a.merge:
    new, parts = mg.split("=")
    pooled = {}
    for part in parts.split("+"):
        if set(pooled) & set(arms.get(part, {})):
            raise SystemExit(f"--merge {mg}: overlapping seeds")
        pooled.update(arms.get(part, {}))
    arms[new] = pooled
stems = sorted(next(iter(next(iter(arms.values())).values())))
if a.keep:
    stems = [st for st in stems if re.match(a.keep, st)]
C = {k: np.array([[arms[k][s][st] for st in stems] for s in sorted(arms[k])], float) for k in arms}  # seeds x imgs x 6
gt = {0: C[next(iter(C))][0][:, [0, 2]].sum(1), 3: C[next(iter(C))][0][:, [3, 5]].sum(1)}  # tp+fn = GT px per image
top3 = {i: set(np.argsort(-gt[i])[:3]) for i in gt}


def iou(cnt, i, w):  # cnt: seeds x imgs x 6; w: image weights (counts of each image in the resample)
    t = np.einsum("sjk,j->sk", cnt[:, :, i:i + 3], w)
    return (t[:, 0] / np.maximum(t.sum(1), 1)).mean()


rng = np.random.default_rng(0)
n = len(stems)
W = np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(a.B)]).astype(float)
print(f"split {a.split}: {n} cells; top-3 cells hold crack {gt[0][list(top3[0])].sum() / gt[0].sum():.0%}, "
      f"inactive {gt[3][list(top3[3])].sum() / gt[3].sum():.0%} of GT px; {a.B} bootstrap resamples")
print("| B − A | class | Δ IoU (all cells) | Δ without top-3 cells | 95% image-bootstrap CI | P(Δ>0) |")
print("|---|---|---|---|---|---|")
for pr in a.pairs:
    A, B = pr.split("=")
    for i, cls in ((0, "crack"), (3, "inactive")):
        ones = np.ones(n); drop = np.array([0.0 if j in top3[i] else 1.0 for j in range(n)])
        d = iou(C[B], i, ones) - iou(C[A], i, ones)
        dd = iou(C[B], i, drop) - iou(C[A], i, drop)
        bs = np.array([iou(C[B], i, w) - iou(C[A], i, w) for w in W])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"| {B} − {A} | {cls} | {d:+.3f} | {dd:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {(bs > 0).mean():.2f} |")
