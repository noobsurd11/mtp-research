"""Bars (test, revised labels, mean ± sd over seeds, seed dots) for any set of arms; optional bin-0 share print.

Usage: python ssl_figure.py --dirs results/p9/raw results/p8/raw results/p6/raw --out results/p9/fig_p9_bars.png \
          --title "P9: external pool (11,938 cells), L3 base, 10% labels" \
          --arms "p6:L3_10pct=A sup." "p8:D_10pct=D (431)" "p9:Dx_10pct=Dx (12k)" ... [--hist results/p9/hist_revised.npz]
"""
import argparse, glob, json, os, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--dirs", nargs="+", required=True)
ap.add_argument("--arms", nargs="+", required=True, help="exp:arm=label")
ap.add_argument("--out", required=True)
ap.add_argument("--title", default="")
ap.add_argument("--hist", nargs="*", default=[])
a = ap.parse_args()

R = {}
for d in a.dirs:
    for f in sorted(glob.glob(os.path.join(d, "p*_s[0-9]*.json"))):
        for key, v in json.load(open(f)).items():
            split, run = key.split("/", 1)
            m = re.match(r"^(p\d+)_(.+)_s(\d+)$", run)
            if m and split == "test":
                R.setdefault(f"{m.group(1)}:{m.group(2)}", {})[int(m.group(3))] = v["new_escdd"]
arms = [(k, n) for k, n in (s.split("=", 1) for s in a.arms) if k in R]
mets = [("crack", "iou"), ("inactive", "iou"), ("crack", "rel_f1_2"), ("crack", "ap"), ("inactive", "ap")]


def colour(k, n):
    if "100pct" in k or "50pct" in k:
        return "#98df8a"
    if n.startswith("A"):
        return "#bdbdbd"
    return {"D": "#7f7f7f", "B": "#1f77b4", "C": "#d62728"}.get(k.split(":")[1][0], "#2ca02c")


fig, axs = plt.subplots(1, len(mets), figsize=(3.3 * len(mets), 3.9))
for ax, (c, m) in zip(axs, mets):
    for i, (k, n) in enumerate(arms):
        v = np.array([R[k][s][c][m] for s in sorted(R[k])])
        hatch = "//" if re.search(r"x_", k) else None
        ax.bar(i, v.mean(), yerr=v.std(ddof=1) if len(v) > 1 else 0, capsize=3, color=colour(k, n), hatch=hatch, edgecolor="white")
        ax.scatter(np.full(len(v), i) + np.linspace(-0.15, 0.15, len(v)), v, s=8, color="k", zorder=3)
    ax.set_xticks(range(len(arms))); ax.set_xticklabels([n for _, n in arms], fontsize=7, rotation=45, ha="right")
    lo = min(min(R[k][s][c][m] for s in R[k]) for k, _ in arms)
    ax.set_ylim(max(0, lo - 0.05), None); ax.set_title(f"{c} {m.replace('rel_f1_2', 'relaxed F1@2')}", fontsize=9); ax.grid(axis="y", alpha=0.3)
fig.suptitle(f"{a.title}  (test, revised labels, mean ± sd, dots = seeds; hatched = external pool)", fontsize=9.5)
fig.tight_layout(); fig.savefig(a.out, dpi=170)
print("wrote", a.out)

for h in a.hist:
    H = dict(np.load(h))
    print(f"\nbin-0 share (GT px scored < 0.001), test, mean over seeds ({h}):")
    for k in sorted({re.match(r"^test/(p\d+_.+)_s\d+$", x).group(1) for x in H if x.startswith("test/")}):
        v = [[H[x][ci, 0, 0] / H[x][ci, 0].sum() for ci in (0, 1)] for x in H if re.match(rf"^test/{k}_s\d+$", x)]
        print(f"  {k:18s} crack {np.mean(v, 0)[0]:.3f}  inactive {np.mean(v, 0)[1]:.3f}")
