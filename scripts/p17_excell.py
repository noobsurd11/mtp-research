"""P17 post-hoc sensitivity (NOT a locked rule): P8 rule-1 arithmetic on the P17/P13 5% contrasts with and without one test cell.

Same method as scripts/p16_excell.py: pooled test metrics from the E1 per-cell counts (results/e1/raw_v2), checked first
against the re-score JSONs, then the seed-level rule with the cell dropped. The P17 protocol requires this report.
Usage: .venv/bin/python scripts/p17_excell.py | tee results/p17/sensitivity_excell.txt
"""
import argparse, glob, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--cell", default="CSIR_00070_r8_c4")
a = ap.parse_args()
X = a.cell

E1 = {os.path.basename(f)[:-5]: json.load(open(f))["cells"]["test"] for f in glob.glob("results/e1/raw_v2/p*_s[0-9].json")}
RS = {}
for d in ("results/p12/raw", "results/p13/raw", "results/p17/raw"):
    for f in glob.glob(os.path.join(d, "p*_s[0-9].json")):
        for k, v in json.load(open(f)).items():
            if k.startswith("test/"):
                RS[k[5:]] = v["new_escdd"]


def pooled(run, drop=()):
    c = [v for s, v in E1[run].items() if s not in drop]
    t = {k: sum(x.get(k, 0) for x in c) for k in ("crack_tp", "crack_gt", "crack_pred", "crack_p2_hit", "crack_r2_hit", "inact_tp", "inact_union")}
    ci = t["crack_tp"] / (t["crack_gt"] + t["crack_pred"] - t["crack_tp"])
    ii = t["inact_tp"] / t["inact_union"]
    p, r = t["crack_p2_hit"] / max(t["crack_pred"], 1), t["crack_r2_hit"] / t["crack_gt"]
    return np.array([ci, ii, 2 * p * r / (p + r), p])


ARMS = {"A5c": ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"],
        "BsM5": [f"p13_BsM_5pct_s{i}" for i in range(5)],
        "BsD5": [f"p17_BsD_5pct_s{i}" for i in range(5)],
        "CsM5": [f"p13_CsM_5pct_s{i}" for i in range(5)]}
PAIRS = (("BsD5", "BsM5"), ("BsD5", "A5c"), ("BsM5", "A5c"), ("CsM5", "BsM5"), ("CsM5", "A5c"))
NAMES = ["crack IoU", "inactive IoU", "crack relF1@2", "crack relP@2"]
missing = [r for rs in ARMS.values() for r in rs if r not in E1 or r not in RS]
if missing:
    raise SystemExit(f"missing E1 or re-score JSONs: {missing}")

err = max(abs(pooled(r)[j] - RS[r][c][m]) for rs in ARMS.values() for r in rs
          for j, (c, m) in enumerate((("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"))))
print(f"sanity: max |E1 pooled - re-score| over all runs and the 4 metrics = {err:.1e}")
print(f"\nCrack FP px on {X} per seed (E1 counts: crack_pred - crack_tp on that cell):")
for k, rs in ARMS.items():
    print(f"  {k:5s} " + ", ".join(f"{r.rsplit('_', 1)[1]} {E1[r][X]['crack_pred'] - E1[r][X]['crack_tp']}" for r in rs))

for drop, lab in (((), "all 50 cells (the locked numbers)"), ((X,), f"without {X} (post hoc)")):
    print(f"\n## {lab}\n| arm | seeds | " + " | ".join(NAMES) + " |\n|---|---|" + "---|" * len(NAMES))
    V = {k: np.array([pooled(r, drop) for r in rs]) for k, rs in ARMS.items()}
    for k, v in V.items():
        print(f"| {k} | {len(v)} | " + " | ".join(f"{v[:, j].mean():.3f}±{v[:, j].std(ddof=1):.3f}" for j in range(len(NAMES))) + " |")
    print("\n| contrast | " + " | ".join(NAMES[:3]) + " | rule-1 arithmetic | relP@2 Δ |\n|---|---|---|---|---|---|")
    for s, b in PAIRS:
        cells, sg = [], []
        for j in range(3):
            xa, xb = V[s][:, j], V[b][:, j]; dl = xa.mean() - xb.mean()
            thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            sg.append(1 if dl > thr else -1 if dl < -thr else 0); cells.append(f"{dl:+.4f} ({thr:.4f})")
        w = "passes" if 1 in sg and -1 not in sg else "worse" if -1 in sg and 1 not in sg else "mixed" if 1 in sg else "n.d."
        print(f"| {s} − {b} | " + " | ".join(cells) + f" | {w} | {V[s][:, 3].mean() - V[b][:, 3].mean():+.4f} |")
