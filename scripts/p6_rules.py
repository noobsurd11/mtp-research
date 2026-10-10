"""Apply the locked P6 decision rules (protocols/P6_corrected_baseline.md) to re-score JSONs."""
import glob, json, os, re, sys
import numpy as np

d = sys.argv[1]
R = {}  # arm -> seed -> split -> class -> metrics
for f in sorted(glob.glob(os.path.join(d, "p6_*.json"))):
    for key, v in json.load(open(f)).items():
        split, run = key.split("/", 1)
        arm, seed = re.match(r"^p6_(.+)_s(\d+)$", run).groups()
        R.setdefault(arm, {}).setdefault(int(seed), {})[split] = v["new_escdd"]

def vals(arm, split, cls, m="ap"):
    return np.array([R[arm][s][split][cls][m] for s in sorted(R[arm])])

print("Rule 1: ladder steps (test, revised labels; helps if |delta| > 0.01 and > 2*sqrt((sa^2+sb^2)/3))")
for a, b in [("L0_10pct", "L1_10pct"), ("L1_10pct", "L2_10pct"), ("L2_10pct", "L3_10pct"),
             ("L0_10pct", "L0_100pct"), ("L3_10pct", "L3_20pct"), ("L3_10pct", "L3_100pct")]:
    for cls in ("crack", "inactive"):
        for m in ("ap", "iou", "rel_f1_2"):
            xa, xb = vals(a, "test", cls, m), vals(b, "test", cls, m)
            dlt = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1)**2 + xb.std(ddof=1)**2) / 3))
            verdict = ("HELPS" if dlt > 0 else "HURTS") if abs(dlt) > thr else "no detectable effect"
            tag = "" if m == "ap" else "  (secondary)"
            print(f"  {a:>9} -> {b:<9} {cls:8} {m:8} delta {dlt:+.3f}  thr {thr:.3f}  {verdict}{tag}")

print("\nRule 2: base = 10% arm with highest val mean (crack AP + inactive AP)/2")
score = {}
for arm in ("L0_10pct", "L1_10pct", "L2_10pct", "L3_10pct"):
    per_seed = (vals(arm, "val", "crack") + vals(arm, "val", "inactive")) / 2
    score[arm] = per_seed.mean()
    print(f"  {arm}: {per_seed.mean():.4f} (seeds {np.round(per_seed, 3)})")
base = max(score, key=score.get); print("  -> base:", base)

print("\nRule 3: headroom = base@100% - base@10%, mean (crack AP + inactive AP)/2 over val and test")
b100 = base.replace("10pct", "100pct")
for arm in (base, b100):
    t = (vals(arm, "test", "crack") + vals(arm, "test", "inactive")).mean() / 2
    v = (vals(arm, "val", "crack") + vals(arm, "val", "inactive")).mean() / 2
    R[arm]["_pool"] = ((t + v) / 2, (50 * t + 54 * v) / 104)
    print(f"  {arm}: test {t:.4f} val {v:.4f}  split-mean {R[arm]['_pool'][0]:.4f}  n-weighted {R[arm]['_pool'][1]:.4f}")
for i, lab in enumerate(("split-mean", "n-weighted")):
    print(f"  headroom ({lab}): {R[b100]['_pool'][i] - R[base]['_pool'][i]:+.4f}  (threshold 0.02)")
