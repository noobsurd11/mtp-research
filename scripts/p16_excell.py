"""P16 post-hoc sensitivity (NOT a locked rule): the P8 rule-1 arithmetic and the label-fraction curve with one test cell removed.

Why: in 4 of the 24 P16 test runs (and P6 L0 10% s1) the model labels about 15-30% of the very noisy test cell
CSIR_00070_r8_c4 as crack (40k-80k FP px), which alone moves pooled crack IoU by up to -0.17. Val is unaffected.
This script shows what the contrasts look like without that cell. It uses the E1 per-cell counts (results/e1/raw_v2),
whose pooled values are first checked against the re-score JSONs.
Usage: .venv/bin/python scripts/p16_excell.py --out results/p16/fig_p16_curve_excell.png | tee results/p16/sensitivity_excell.txt
"""
import argparse, glob, json, os, re
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
for d in ("results/p6/raw", "results/p12/raw", "results/p13/raw", "results/p16/raw"):
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


ARMS = {"A5": ["p12_A_5pct_s0", "p12_A_5pct_s1", "p12_A_5pct_s2", "p13_A_5pct_s3", "p13_A_5pct_s4"],
        "S5 (P13 Cs5)": [f"p13_Cs_5pct_s{i}" for i in range(3)],
        "A10": [f"p6_L3_10pct_s{i}" for i in range(3)],
        "A20": ["p6_L3_20pct_s0", "p6_L3_20pct_s1", "p6_L3_20pct_s2", "p16_A_20pct_s3", "p16_A_20pct_s4"],
        "S20": [f"p16_S_20pct_s{i}" for i in range(5)], "A50": [f"p16_A_50pct_s{i}" for i in range(5)],
        "S50": [f"p16_S_50pct_s{i}" for i in range(5)],
        "A100": ["p6_L3_100pct_s0", "p6_L3_100pct_s1", "p6_L3_100pct_s2", "p16_A_100pct_s3", "p16_A_100pct_s4"],
        "Sx100": [f"p16_Sx_100pct_s{i}" for i in range(5)]}
NAMES = ["crack IoU", "inactive IoU", "crack relF1@2", "crack relP@2"]

err = max(abs(pooled(r)[j] - RS[r][c][m]) for rs in ARMS.values() for r in rs
          for j, (c, m) in enumerate((("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "rel_p2"))))
print(f"sanity: max |E1 pooled - re-score| over all runs and the 4 metrics = {err:.1e}")
print(f"\nCrack FP px on {X} per seed (E1 counts: crack_pred - crack_tp on that cell):")
for k, rs in ARMS.items():
    print(f"  {k:13s} " + ", ".join(f"{r.rsplit('_', 1)[1]} {E1[r][X]['crack_pred'] - E1[r][X]['crack_tp']}" for r in rs))

V = {}
for drop, lab in (((), "all 50 cells (the locked numbers)"), ((X,), f"without {X} (post hoc)")):
    print(f"\n## {lab}\n| arm | seeds | " + " | ".join(NAMES) + " |\n|---|---|" + "---|" * len(NAMES))
    V[drop] = {k: np.array([pooled(r, drop) for r in rs]) for k, rs in ARMS.items()}
    for k, v in V[drop].items():
        print(f"| {k} | {len(v)} | " + " | ".join(f"{v[:, j].mean():.3f}±{v[:, j].std(ddof=1):.3f}" for j in range(len(NAMES))) + " |")
    print("\n| contrast | " + " | ".join(NAMES[:3]) + " | rule-1 arithmetic |\n|---|---|---|---|---|")
    for s, b in (("S20", "A20"), ("S50", "A50"), ("Sx100", "A100")):
        cells, sg = [], []
        for j in range(3):
            xa, xb = V[drop][s][:, j], V[drop][b][:, j]; dl = xa.mean() - xb.mean()
            thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            sg.append(1 if dl > thr else -1 if dl < -thr else 0); cells.append(f"{dl:+.4f} ({thr:.4f})")
        w = "passes" if 1 in sg and -1 not in sg else "worse" if -1 in sg and 1 not in sg else "mixed" if 1 in sg else "n.d."
        print(f"| {s} − {b} | " + " | ".join(cells) + f" | {w} |")

FR = {5: ("A5", "S5 (P13 Cs5)"), 10: ("A10", None), 20: ("A20", "S20"), 50: ("A50", "S50"), 100: ("A100", "Sx100")}
fig, axs = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
for row, (drop, lab) in enumerate((((), "all 50 test cells (locked)"), ((X,), f"without {X} (post hoc)"))):
    for j, ax in enumerate(axs[row]):
        for col, mk, i, name in (("tab:green", "o", 0, "supervised"), ("tab:red", "s", 1, "SSL (sep. BN, tolerant PL, no CutMix)")):
            fr = [f for f in FR if FR[f][i]]
            v = [V[drop][FR[f][i]][:, j] for f in fr]
            ax.errorbar(fr, [x.mean() for x in v], yerr=[x.std(ddof=1) for x in v], color=col, marker=mk, capsize=3, label=name)
            for f, x in zip(fr, v):
                ax.scatter([f] * len(x), x, color=col, s=8, alpha=0.5)
        ax.set_xscale("log"); ax.set_xticks([5, 10, 20, 50, 100]); ax.set_xticklabels(["5%", "10%", "20%", "50%", "100%\n(SSL: ext. pool)"])
        ax.set_title(f"{NAMES[j]}: {lab}", fontsize=9); ax.grid(alpha=0.3)
axs[0, 0].legend(fontsize=8)
fig.suptitle("P16: SSL vs supervised by label fraction (cv02, test, revised labels). Bottom row is a post-hoc sensitivity check", fontsize=10)
fig.tight_layout(); fig.savefig(a.out, dpi=150)
print("\nwrote", a.out)
