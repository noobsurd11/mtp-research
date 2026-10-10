"""Apply the locked P7 / P8 decision rules (protocols/P7_tolerant_pl_pilot.md, protocols/P8_tolerant_pl_on_l3.md).

Usage: python p78_rules.py p7 <dir with p7_*.json> <P6 raw dir>
       python p78_rules.py p8 <dir with p8_*.json> <P6 raw dir>
"""
import glob, json, os, re, sys
import numpy as np

exp, d, p6 = sys.argv[1], sys.argv[2], sys.argv[3]
R = {}  # arm -> seed -> split -> label -> class -> metrics
for f in sorted(glob.glob(os.path.join(d, f"{exp}_*.json"))) + sorted(glob.glob(os.path.join(p6, "p6_*.json"))):
    for key, v in json.load(open(f)).items():
        split, run = key.split("/", 1)
        pre, arm, seed = re.match(r"^(p\d)_(.+)_s(\d+)$", run).groups()
        arm = arm if pre == exp else f"P6:{arm}"
        R.setdefault(arm, {}).setdefault(int(seed), {})[split] = {"rev": v["new_escdd"], "old": v["old_20211104"], "w": v["weights"], "step": v["step"]}

ref = "P6:L0_10pct" if exp == "p7" else "P6:L3_10pct"
arms = [a for a in ("B_10pct", "C_10pct", "D_10pct") if a in R]


def x(arm, cls, m, split="test", lab="rev"):
    return np.array([R[arm][s][split][lab][cls][m] for s in sorted(R[arm])])


def cmp(a, b, cls, m):
    xa, xb = x(a, cls, m), x(b, cls, m)
    dl = xa.mean() - xb.mean()
    thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return dl, thr, (1 if dl > thr else -1 if dl < -thr else 0)


print(f"{exp.upper()}: seeds per arm", {a: sorted(R[a]) for a in arms},
      "| weights", {R[a][s]["test"]["w"] for a in arms for s in R[a]}, "| steps", {R[a][s]["test"]["step"] for a in arms for s in R[a]})
cols = [("crack", "ap"), ("inactive", "ap"), ("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2")]
print("\n| arm | " + " | ".join(f"test {c} {m}" for c, m in cols) + " | val crack ap | val inactive ap | val crack iou | val inactive iou |")
print("|" + "---|" * (len(cols) + 5))
for a in [ref] + arms + (["P6:L3_100pct"] if exp == "p8" else ["P6:L0_100pct"]):
    cells = [f"{x(a, c, m).mean():.3f}±{x(a, c, m).std(ddof=1):.3f}" for c, m in cols]
    cells += [f"{x(a, c, m, 'val').mean():.3f}±{x(a, c, m, 'val').std(ddof=1):.3f}" for c, m in (("crack", "ap"), ("inactive", "ap"), ("crack", "iou"), ("inactive", "iou"))]
    print(f"| {a} | " + " | ".join(cells) + " |")

prim = [("crack", "ap"), ("inactive", "ap")] if exp == "p7" else [("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2")]
print(f"\nPrimary metrics (test, revised): {prim}")
word = {1: "BETTER", -1: "WORSE", 0: "n.d."}
verdict = {}
for a, b in (("C_10pct", "D_10pct"), ("B_10pct", "D_10pct"), ("C_10pct", "B_10pct")):
    if a not in R or b not in R:
        continue
    res = [cmp(a, b, c, m) for c, m in prim]
    for (c, m), (dl, thr, s) in zip(prim, res):
        print(f"  {a[0]} - {b[0]}  {c:8s} {m:8s} {dl:+.4f}  thr {thr:.4f}  {word[s]}")
    signs = [s for _, _, s in res]
    ok = any(s == 1 for s in signs) and (exp == "p7" or not any(s == -1 for s in signs))
    verdict[a[0] + b[0]] = ok
    print(f"  => {a[0]} {'beats' if b[0] == 'B' else 'helps vs'} {b[0]}: {ok}")

if "C_10pct" in R and "D_10pct" in R:
    dp = x("C_10pct", "crack", "rel_p2").mean() - x("D_10pct", "crack", "rel_p2").mean()
    print(f"\nWidth check: crack relP@2 C - D = {dp:+.4f}  -> {'FLAG possible fattening' if dp < -0.05 else 'ok'}")
if exp == "p7":
    print("Rule 4: P6 rule 3 (literal pooled AP) headroom = -0.001 < 0.02 -> all P7 outcomes are reported as a PILOT.")
if exp == "p8" and "C_10pct" in R and "D_10pct" in R:
    print("\nRule 4: share of the label gap closed, (C - D) / (L3@100% - D), test:")
    for c, m in prim:
        g = x("P6:L3_100pct", c, m).mean() - x("D_10pct", c, m).mean()
        for a in ("B_10pct", "C_10pct"):
            if a in R:
                print(f"  {a[0]} {c:8s} {m:8s} gap {g:+.4f}  closed {(x(a, c, m).mean() - x('D_10pct', c, m).mean()) / g:+.2f}")
