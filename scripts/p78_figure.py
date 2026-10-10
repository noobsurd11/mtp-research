"""Result bars for P7 / P8 (test, revised labels, mean ± sd over seeds) plus bin-0 share from score histograms.

Usage: python p78_figure.py p8 results/p8/raw results/p6/raw [results/p8/hist_revised.npz]
"""
import glob, json, os, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

exp, d, p6 = sys.argv[1:4]
hist = sys.argv[4] if len(sys.argv) > 4 else None
R = {}
for f in sorted(glob.glob(os.path.join(d, f"{exp}_*.json"))) + sorted(glob.glob(os.path.join(p6, "p6_*.json"))):
    for key, v in json.load(open(f)).items():
        split, run = key.split("/", 1)
        if split != "test":
            continue
        pre, arm, s = re.match(r"^(p\d+)_(.+)_s(\d+)$", run).groups()
        R.setdefault(f"{pre}:{arm}", {})[int(s)] = v["new_escdd"]
base = "L0" if exp == "p7" else "L3"
arms = [(f"p6:{base}_10pct", f"A: supervised\n({base}, 10%)"), (f"{exp}:D_10pct", "D: MT, loss off"),
        (f"{exp}:B_10pct", "B: hard PL\n(conf ≥ 0.95)"), (f"{exp}:C_10pct", "C: tolerant PL\n(proposed)"),
        (f"p6:{base}_100pct", f"{base} @ 100%\n(upper ref.)")]
arms = [(k, n) for k, n in arms if k in R]
mets = [("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "ap"), ("inactive", "ap")]
fig, axs = plt.subplots(1, len(mets), figsize=(3.0 * len(mets), 3.6))
cols = {"A": "#9e9e9e", "D": "#7f7f7f", "B": "#1f77b4", "C": "#d62728"}
for ax, (c, m) in zip(axs, mets):
    for i, (k, n) in enumerate(arms):
        v = np.array([R[k][s][c][m] for s in sorted(R[k])])
        ax.bar(i, v.mean(), yerr=v.std(ddof=1), capsize=3, color=cols.get(n[0], "#2ca02c"), alpha=0.9 if n[0] != "L" else 0.5)
    ax.set_xticks(range(len(arms))); ax.set_xticklabels([n.split(":")[0].split(" @")[0] if n[0] in "ABCD" else "100%" for _, n in arms], fontsize=8.5)
    lo = min(np.mean([R[k][s][c][m] for s in R[k]]) for k, _ in arms)
    ax.set_ylim(max(0, lo - 0.1), None); ax.set_title(f"{c} {m.replace('rel_f1_2', 'relaxed F1@2')}", fontsize=9); ax.grid(axis="y", alpha=0.3)
prim = "primary: crack/inactive AP (P7 pilot)" if exp == "p7" else "primary: crack IoU, inactive IoU, crack relaxed F1@2"
fig.suptitle(f"{exp.upper()} (test, revised labels, mean ± sd over 3 seeds; {prim})", fontsize=9.5)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=cols.get(n[0], "#2ca02c"), alpha=0.9 if n[0] != "L" else 0.5, label=n.replace("\n", " ")) for _, n in arms],
           loc="lower center", ncol=len(arms), fontsize=8, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1)); out = os.path.join(os.path.dirname(d.rstrip("/")), f"fig_{exp}_bars.png"); fig.savefig(out, dpi=170)
print("wrote", out)

if hist:
    H = dict(np.load(hist))
    print("\nbin-0 share (GT px scored < 0.001), test, mean over seeds:")
    for k in sorted({re.match(r"^test/(p\d+_.+)_s\d+$", x).group(1) for x in H if x.startswith("test/")}):
        v = [[H[x][ci, 0, 0] / H[x][ci, 0].sum() for ci in (0, 1)] for x in H if re.match(rf"^test/{k}_s\d+$", x)]
        print(f"  {k:16s} crack {np.mean(v, 0)[0]:.3f}  inactive {np.mean(v, 0)[1]:.3f}")
