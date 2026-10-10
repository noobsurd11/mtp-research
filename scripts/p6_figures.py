"""Mid-term figures for P6 (results/p6). Usage: python p6_figures.py results/p6"""
import glob, json, os, re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = sys.argv[1]
R = {}
for f in glob.glob(os.path.join(D, "raw", "p6_*.json")):
    for key, v in json.load(open(f)).items():
        split, run = key.split("/", 1)
        arm, s = re.match(r"^p6_(.+)_s(\d+)$", run).groups()
        R.setdefault(arm, {}).setdefault(int(s), {})[split] = v["new_escdd"]
H = dict(np.load(os.path.join(D, "hist_revised.npz")))


def ms(arm, cls, m, split="test"):
    v = np.array([R[arm][s][split][cls][m] for s in sorted(R[arm])]); return v.mean(), v.std(ddof=1)


def pooled_ap(arm, ci):
    out = []
    for s in sorted(R[arm]):
        pos, neg = (H[f"test/p6_{arm}_s{s}"] + H[f"val/p6_{arm}_s{s}"])[ci].astype(float)
        tp, fp = np.cumsum(pos[::-1]), np.cumsum(neg[::-1])
        out.append((np.diff(np.concatenate([[0], tp / pos.sum()])) * np.where(tp + fp > 0, tp / np.maximum(tp + fp, 1), 0)).sum())
    return np.mean(out), np.std(out, ddof=1)


plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
C = {"ap": "#1f77b4", "iou": "#d62728", "rel_f1_2": "#2ca02c"}

# 1. ladder at 10% labels: AP vs IoU disagree
ladder = ["L0_10pct", "L1_10pct", "L2_10pct", "L3_10pct"]
names = ["L0\nold recipe", "L1\n+label-safe aug", "L2\n+ImageNet enc.", "L3\n+CE+Dice"]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, cls in zip(axs, ("crack", "inactive")):
    for m, lab in (("ap", "pixel AP (threshold-free)"), ("iou", "IoU (argmax)")) + ((("rel_f1_2", "relaxed F1 @2px"),) if cls == "crack" else ()):
        mu, sd = zip(*[ms(a, cls, m) for a in ladder])
        ax.errorbar(range(4), mu, yerr=sd, marker="o", capsize=3, color=C[m], label=lab)
    ax.set_xticks(range(4)); ax.set_xticklabels(names, fontsize=8.5); ax.set_title(f"{cls}: test, revised labels, 10% labels")
    ax.grid(alpha=0.3); ax.set_ylim(0.2, 0.9)
axs[0].legend(fontsize=8, loc="upper left"); axs[0].set_ylabel("mean ± sd over 3 seeds")
fig.tight_layout(); fig.savefig(os.path.join(D, "fig_ladder.png"), dpi=170); plt.close(fig)

# 2. label efficiency: old recipe vs L3
fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
for ax, (title, fn) in zip(axs, (("crack IoU (test)", lambda a: ms(a, "crack", "iou")),
                                  ("inactive IoU (test)", lambda a: ms(a, "inactive", "iou")),
                                  ("mean AP, pooled val+test", lambda a: tuple(np.mean([pooled_ap(a, 0), pooled_ap(a, 1)], 0))))):
    for rec, fr, col in (("L0", (10, 100), "#7f7f7f"), ("L3", (10, 20, 100), "#9467bd")):
        mu, sd = zip(*[fn(f"{rec}_{f}pct") for f in fr])
        ax.errorbar(fr, mu, yerr=sd, marker="o", capsize=3, color=col, label={"L0": "old recipe (L0)", "L3": "ImageNet + CE+Dice (L3)"}[rec])
    ax.set_xscale("log"); ax.set_xticks([10, 20, 100]); ax.set_xticklabels(["10%", "20%", "100%"]); ax.set_title(title); ax.grid(alpha=0.3)
axs[0].legend(fontsize=8); axs[0].set_xlabel("labelled fraction of train (47 / 95 / 478 images)")
fig.tight_layout(); fig.savefig(os.path.join(D, "fig_label_scaling.png"), dpi=170); plt.close(fig)

# 3. score saturation: share of GT pixels scored below t
edges = np.arange(1, 1001) / 1000.0
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
cols = {"L0_10pct": "#7f7f7f", "L1_10pct": "#1f77b4", "L2_10pct": "#ff7f0e", "L3_10pct": "#9467bd", "L3_100pct": "#2ca02c"}
for ax, (ci, cls) in zip(axs, enumerate(("crack", "inactive"))):
    for arm, col in cols.items():
        cdf = np.mean([np.cumsum(H[f"test/p6_{arm}_s{s}"][ci, 0]) / H[f"test/p6_{arm}_s{s}"][ci, 0].sum() for s in sorted(R[arm])], 0)
        ax.plot(edges, cdf, color=col, label=arm.replace("_", " "), ls="--" if arm == "L3_100pct" else "-")
    ax.set_xscale("log"); ax.set_xlim(1e-3, 1); ax.axvline(0.5, color="k", lw=0.6, ls=":")
    ax.set_title(f"GT {cls} pixels: share scored below t (test)"); ax.set_xlabel("softmax score threshold t"); ax.grid(alpha=0.3)
axs[0].set_ylabel("cumulative share of GT pixels"); axs[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig_saturation.png"), dpi=170); plt.close(fig)
print("wrote fig_ladder.png fig_label_scaling.png fig_saturation.png")
