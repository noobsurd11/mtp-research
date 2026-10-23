"""Locked rule-1 / width / gap-closed checks for any SSL contrast (P8-style rules, used for P9 and P10).

Rule (P8 rule 1): A helps vs B if mean(A) - mean(B) > max(0.01, 2*sqrt((sd_A^2 + sd_B^2)/3)) on any primary metric and
no primary metric is worse by the same threshold. Width check: crack relaxed precision@2 drop > 0.05 is flagged.
Gap closed: (A - B) / (REF - B). Interaction: (A1 - B1) - (A2 - B2) for "--interact A1=B1,A2=B2".

Usage: python ssl_rules.py --dirs results/p9/raw results/p8/raw results/p6/raw \
          --arms p6:L3_10pct p9:Dx_10pct p9:Bx_10pct p9:Cx_10pct p6:L3_100pct \
          --pairs p9:Cx_10pct=p9:Dx_10pct p9:Bx_10pct=p9:Dx_10pct p9:Cx_10pct=p9:Bx_10pct \
          --ref p6:L3_100pct --interact p9:Cx_10pct=p9:Dx_10pct,p8:C_10pct=p8:D_10pct
"""
import argparse, glob, json, os, re
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--dirs", nargs="+", required=True)
ap.add_argument("--arms", nargs="+", required=True)
ap.add_argument("--pairs", nargs="*", default=[])
ap.add_argument("--ref", default=None)
ap.add_argument("--interact", nargs="*", default=[])
ap.add_argument("--merge", nargs="*", default=[], help="NEW=ARM1+ARM2: pool the seeds of two arms (seed sets must be disjoint)")
ap.add_argument("--prim", nargs="+", default=["crack:iou", "inactive:iou", "crack:rel_f1_2"])
a = ap.parse_args()

R = {}
for d in a.dirs:
    for f in sorted(glob.glob(os.path.join(d, "p*_s[0-9]*.json")) + glob.glob(os.path.join(d, "sk*_s[0-9]*.json"))):
        for key, v in json.load(open(f)).items():
            split, run = key.split("/", 1)
            m = re.match(r"^(p\d+|sk\d+)_(.+)_s(\d+)$", run)
            if m:
                R.setdefault(f"{m.group(1)}:{m.group(2)}", {}).setdefault(int(m.group(3)), {})[split] = v["new_escdd"]

for mg in a.merge:
    new, parts = mg.split("=")
    pooled = {}
    for part in parts.split("+"):
        if set(pooled) & set(R.get(part, {})):
            raise SystemExit(f"--merge {mg}: overlapping seeds")
        pooled.update(R.get(part, {}))
    R[new] = pooled


def x(arm, c, m, split="test"):
    return np.array([R[arm][s][split][c][m] for s in sorted(R[arm])])


def cmp(A, B, c, m):
    xa, xb = x(A, c, m), x(B, c, m)
    sd = lambda v: v.std(ddof=1) if len(v) > 1 else float("nan")
    dl = xa.mean() - xb.mean()
    thr = max(0.01, 2 * np.sqrt((sd(xa) ** 2 + sd(xb) ** 2) / 3))
    return dl, thr, (1 if dl > thr else -1 if dl < -thr else 0)


prim = [tuple(p.split(":")) for p in a.prim]
cols = [("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"), ("crack", "ap"), ("inactive", "ap")]
print("| arm | seeds | " + " | ".join(f"{c} {m}" for c, m in cols) + " | val crack iou | val inactive iou |")
print("|" + "---|" * (len(cols) + 4))
for arm in a.arms:
    if arm not in R:
        print(f"| {arm} | missing |"); continue
    cell = lambda v: f"{v.mean():.3f}±{v.std(ddof=1):.3f}" if len(v) > 1 else f"{v.mean():.3f}"
    print(f"| {arm} | {sorted(R[arm])} | " + " | ".join(cell(x(arm, c, m)) for c, m in cols) + " | "
          + " | ".join(cell(x(arm, c, "iou", "val")) for c in ("crack", "inactive")) + " |")

word = {1: "BETTER", -1: "WORSE", 0: "n.d."}
for pr in a.pairs:
    A, B = pr.split("=")
    if A not in R or B not in R:
        print(f"\n{A} vs {B}: missing"); continue
    print(f"\n{A} vs {B} (test, revised; primary {a.prim}; seeds {sorted(R[A])} / {sorted(R[B])})")
    res = [cmp(A, B, c, m) for c, m in prim]
    for (c, m), (dl, thr, s) in zip(prim, res):
        print(f"  {c:8s} {m:8s} {dl:+.4f}  thr {thr:.4f}  {word[s]}")
    sg = [s for *_, s in res]
    print(f"  => {A} better than {B} under rule 1: {any(s == 1 for s in sg) and not any(s == -1 for s in sg)}"
          + ("  (some primary WORSE)" if any(s == -1 for s in sg) else ""))
    dp = x(A, "crack", "rel_p2").mean() - x(B, "crack", "rel_p2").mean()
    print(f"  width check: crack relP@2 {dp:+.4f} -> {'FLAG possible fattening' if dp < -0.05 else 'ok'}")
    if a.ref and a.ref in R:
        for c, m in prim:
            g = x(a.ref, c, m).mean() - x(B, c, m).mean()
            print(f"  gap closed {c:8s} {m:8s}: gap {g:+.4f}, closed {(x(A, c, m).mean() - x(B, c, m).mean()) / g:+.2f}")

for it in a.interact:
    (A1, B1), (A2, B2) = [p.split("=") for p in it.split(",")]
    if not all(k in R for k in (A1, B1, A2, B2)):
        print(f"\ninteraction {it}: missing"); continue
    print(f"\nInteraction ({A1} - {B1}) - ({A2} - {B2}), test (secondary, descriptive):")
    for c, m in prim:
        d1 = x(A1, c, m).mean() - x(B1, c, m).mean(); d2 = x(A2, c, m).mean() - x(B2, c, m).mean()
        print(f"  {c:8s} {m:8s} {d1:+.4f} vs {d2:+.4f} -> {d1 - d2:+.4f}")
