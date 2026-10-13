"""P18 (EXPLORATORY): rule-1 arithmetic for the BsM recipe at 10/20% and the label-fraction curve, with and without one test cell.

Same method as scripts/p16_excell.py: pooled test metrics from the E1 per-cell counts (results/e1/raw_v2), checked first
against the re-score JSONs; the row without CSIR_00070_r8_c4 is post hoc. Curve: supervised, the tolerant/no-CutMix recipe
(P13 Cs5, P16 S20/S50/Sx100) and the BsM recipe (P13 BsM5, P18 BsM10/BsM20), cv02 only.
Usage: .venv/bin/python scripts/p18_curve.py --out results/p18/fig_p18_curve.png | tee results/p18/p18_curve.txt
"""
import argparse, glob, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--cell", default="CSIR_00070_r8_c4")
ap.add_argument("--out", required=True)
a = ap.parse_args()
X = a.cell

E1 = {os.path.basename(f)[:-5]: json.load(open(f))["cells"]["test"] for f in glob.glob("results/e1/raw_v2/p*_s[0-9].json")}
RS = {}
for d in ("results/p6/raw", "results/p12/raw", "results/p13/raw", "results/p16/raw", "results/p18/raw"):
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


S = lambda pre, seeds: [f"{pre}_s{i}" for i in seeds]
ARMS = {"A5c": S("p12_A_5pct", range(3)) + S("p13_A_5pct", (3, 4)), "Cs5": S("p13_Cs_5pct", range(3)),
        "BsM5": S("p13_BsM_5pct", range(5)),
        "A10": S("p6_L3_10pct", range(3)), "BsM10": S("p18_BsM_10pct", range(3)),
        "A20": S("p6_L3_20pct", range(3)) + S("p16_A_20pct", (3, 4)), "S20": S("p16_S_20pct", range(5)),
        "BsM20": S("p18_BsM_20pct", range(5)),
        "A50": S("p16_A_50pct", range(5)), "S50": S("p16_S_50pct", range(5)),
        "A100": S("p6_L3_100pct", range(3)) + S("p16_A_100pct", (3, 4)), "Sx100": S("p16_Sx_100pct", range(5))}
PAIRS = (("BsM20", "A20"), ("BsM10", "A10"), ("BsM20", "S20"), ("BsM5", "A5c"), ("S20", "A20"))
NAMES = ["crack IoU", "inactive IoU", "crack relF1@2", "crack relP@2"]
missing = [r for rs in ARMS.values() for r in rs if r not in E1 or r not in RS]
if missing:
    raise SystemExit(f"missing E1 or re-score JSONs: {missing}")

err = max(abs(pooled(r)[j] - RS[r][c][m]) for rs in ARMS.values() for r in rs
          for j, (c, m) in enumerate((("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"))))
print(f"sanity: max |E1 pooled - re-score| over all runs and the 4 metrics = {err:.1e}")
print(f"\nCrack FP px on {X} per seed (E1 counts):")
for k in ("A10", "BsM10", "A20", "S20", "BsM20"):
    print(f"  {k:6s} " + ", ".join(f"{r.rsplit('_', 1)[1]} {E1[r][X]['crack_pred'] - E1[r][X]['crack_tp']}" for r in ARMS[k]))

V = {}
for drop, lab in (((), "all 50 cells (as scored)"), ((X,), f"without {X} (post hoc)")):
    print(f"\n## {lab}\n| arm | seeds | " + " | ".join(NAMES) + " |\n|---|---|" + "---|" * len(NAMES))
    V[drop] = {k: np.array([pooled(r, drop) for r in rs]) for k, rs in ARMS.items()}
    for k, v in V[drop].items():
        print(f"| {k} | {len(v)} | " + " | ".join(f"{v[:, j].mean():.3f}±{v[:, j].std(ddof=1):.3f}" for j in range(len(NAMES))) + " |")
    print("\n| contrast (exploratory) | " + " | ".join(NAMES[:3]) + " | rule-1 arithmetic | relP@2 Δ |\n|---|---|---|---|---|---|")
    for s, b in PAIRS:
        cells, sg = [], []
        for j in range(3):
            xa, xb = V[drop][s][:, j], V[drop][b][:, j]; dl = xa.mean() - xb.mean()
            thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            sg.append(1 if dl > thr else -1 if dl < -thr else 0); cells.append(f"{dl:+.4f} ({thr:.4f})")
        w = "passes" if 1 in sg and -1 not in sg else "worse" if -1 in sg and 1 not in sg else "mixed" if 1 in sg else "n.d."
        print(f"| {s} − {b} ({len(V[drop][s])} v {len(V[drop][b])}) | " + " | ".join(cells) + f" | {w} | {V[drop][s][:, 3].mean() - V[drop][b][:, 3].mean():+.4f} |")

SER = (("supervised", "tab:green", "o", {5: "A5c", 10: "A10", 20: "A20", 50: "A50", 100: "A100"}),
       ("SSL: tolerant PL, no CutMix (P13 Cs5, P16)", "tab:red", "s", {5: "Cs5", 20: "S20", 50: "S50", 100: "Sx100"}),
       ("SSL: hard PL + CutMix (P13 BsM5, P18)", "tab:blue", "D", {5: "BsM5", 10: "BsM10", 20: "BsM20"}))
fig, axs = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
for row, (drop, lab) in enumerate((((), "all 50 test cells"), ((X,), f"without {X} (post hoc)"))):
    for j, ax in enumerate(axs[row]):
        for name, col, mk, D in SER:
            fr = sorted(D); v = [V[drop][D[f]][:, j] for f in fr]
            ax.errorbar(fr, [x.mean() for x in v], yerr=[x.std(ddof=1) for x in v], color=col, marker=mk, capsize=3, label=name)
            for f, x in zip(fr, v):
                ax.scatter([f] * len(x), x, color=col, s=8, alpha=0.5)
        ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(["5%", "10%", "20%", "50%", "100%\n(SSL: ext. pool)"])
        ax.set_title(f"{NAMES[j]}: {lab}", fontsize=9); ax.grid(alpha=0.3)
axs[0, 0].legend(fontsize=7)
fig.suptitle("SSL vs supervised by label fraction (cv02, test, revised labels, mean ± sd, dots = seeds). "
             "BsM at 10/20% is exploratory (P18)", fontsize=10)
fig.tight_layout(); fig.savefig(a.out, dpi=150)
print("\nwrote", a.out)
