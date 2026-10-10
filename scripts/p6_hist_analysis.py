"""EXPLORATORY analysis of P6 score histograms (scripts_gaint/score_histograms.py output).

1. Sanity: per-split AP from the histograms must equal the re-score JSON AP.
2. Rule 3 computed literally: AP on the pooled val+test pixels (histograms summed), base@100% - base@10%.
3. Score saturation: share of GT pixels the model scores < 0.001 (bin 0, tied with most background, so unrankable),
   recall reachable at score >= 0.5, and AP restricted to the ranked part.
Usage: python p6_hist_analysis.py hist_revised.npz raw/ > hist_analysis.txt
"""
import glob, json, os, re, sys
import numpy as np


def binned_ap(pos, neg):  # identical to src/evaluation/threshold_free.binned_ap
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64)
    tp, fp = np.cumsum(pos[::-1]), np.cumsum(neg[::-1])
    recall = tp / pos.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    return float((np.diff(np.concatenate([[0.0], recall])) * precision).sum())


H = dict(np.load(sys.argv[1]))
J = {}
for f in glob.glob(os.path.join(sys.argv[2], "p6_*.json")):
    J.update(json.load(open(f)))
CL = ("crack", "inactive")

# 1. sanity
worst = max(abs(binned_ap(*H[k][ci]) - J[k]["new_escdd"][c]["ap"]) for k in H for ci, c in enumerate(CL))
print(f"sanity: max |AP(hist) - AP(rescore json)| over {len(H)} run-splits x 2 classes = {worst:.2e}")

arms = {}
for k in H:
    split, run = k.split("/")
    arm, s = re.match(r"^p6_(.+)_s(\d+)$", run).groups()
    arms.setdefault(arm, set()).add(int(s))


def seeds(arm, fn):
    return np.array([fn(arm, s) for s in sorted(arms[arm])])


def pooled(arm, s):
    h = H[f"test/p6_{arm}_s{s}"] + H[f"val/p6_{arm}_s{s}"]
    return np.mean([binned_ap(*h[ci]) for ci in range(2)])


print("\nRule 3, literal (AP on pooled val+test pixels, mean of crack and inactive):")
for arm in ("L0_10pct", "L0_100pct", "L3_10pct", "L3_100pct"):
    v = seeds(arm, pooled); print(f"  {arm:10s} {v.mean():.4f} ± {v.std(ddof=1):.4f}  seeds {np.round(v, 4)}")
d = seeds("L0_100pct", pooled).mean() - seeds("L0_10pct", pooled).mean()
print(f"  headroom L0 (selected base): {d:+.4f}  (threshold 0.02)")
d3 = seeds("L3_100pct", pooled).mean() - seeds("L3_10pct", pooled).mean()
print(f"  headroom L3 (for reference only): {d3:+.4f}")

print("\nScore saturation on test (revised labels), mean over seeds:")
print("  arm        class     GT px in bin0 (p<0.001)  bg px in bin0  recall@p>=0.5  AP")
for arm in ("L0_10pct", "L1_10pct", "L2_10pct", "L3_10pct", "L3_20pct", "L0_100pct", "L3_100pct"):
    for ci, c in enumerate(CL):
        g0 = seeds(arm, lambda a, s: H[f"test/p6_{a}_s{s}"][ci, 0, 0] / H[f"test/p6_{a}_s{s}"][ci, 0].sum())
        b0 = seeds(arm, lambda a, s: H[f"test/p6_{a}_s{s}"][ci, 1, 0] / H[f"test/p6_{a}_s{s}"][ci, 1].sum())
        r5 = seeds(arm, lambda a, s: H[f"test/p6_{a}_s{s}"][ci, 0, 500:].sum() / H[f"test/p6_{a}_s{s}"][ci, 0].sum())
        apv = seeds(arm, lambda a, s: binned_ap(*H[f"test/p6_{a}_s{s}"][ci]))
        print(f"  {arm:10s} {c:9s} {g0.mean():.3f}                    {b0.mean():.3f}          {r5.mean():.3f}          {apv.mean():.3f}")
