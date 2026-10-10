"""Mid-term figures that need no server: P5 offset finding and the tolerant-routing schematic.

Usage: python midterm_figures.py   (writes to results/p5_region_pl/ and results/figures/)
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

# 1. P5: teacher crack pseudo-labels hit the crack, not the pixels (revised labels, global gamma, 2 ALHVR runs pooled)
d = json.load(open(os.path.join(ROOT, "results/p5_region_pl/p5_region_pl_precision.json")))
g, ref = d["variants"]["global"], d["reference_pl095"]["new/crack"]
rows = [("r1\nboth sure", g["new/crack/r1"]), ("r2a\none sure", g["new/crack/r2a"]), ("r2b\none sure", g["new/crack/r2b"]),
        ("r3\nboth unsure", g["new/crack/r3"]), ("teacher\nprob ≥ 0.95", {"prec": ref["prec"], "relprec2": ref["relprec2"], "gt_share": None})]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
x = np.arange(len(rows)); w = 0.38
ax.bar(x - w / 2, [r["prec"] for _, r in rows], w, color="#9e9e9e", label="strict precision (exact pixel)")
ax.bar(x + w / 2, [r["relprec2"] for _, r in rows], w, color="#2ca02c", label="relaxed precision (within 2 px)")
for i, (_, r) in enumerate(rows):
    ax.text(i - w / 2, r["prec"] + 0.02, f"{r['prec']:.2f}", ha="center", fontsize=8)
    ax.text(i + w / 2, r["relprec2"] + 0.02, f"{r['relprec2']:.2f}", ha="center", fontsize=8)
    note = f"{r['gt_share']:.0%} of GT crack" if r["gt_share"] is not None else f"covers {ref['recall_of_all_gt']:.0%} of GT crack"
    ax.text(i, -0.2, note, ha="center", fontsize=7.5, color="#555")
ax.set_xticks(x); ax.set_xticklabels([n for n, _ in rows], fontsize=8.5); ax.set_ylim(0, 1.08)
ax.set_ylabel("crack pseudo-label precision"); ax.legend(fontsize=8, loc="upper left", ncol=2, frameon=False)
ax.set_title("P5: crack pseudo-labels point at the right crack but miss its pixels", fontsize=10)
fig.tight_layout(); fig.subplots_adjust(bottom=0.24)
fig.savefig(os.path.join(ROOT, "results/p5_region_pl/fig_p5_offset.png"), dpi=170); plt.close(fig)

# 2. tolerant routing schematic: (a) teacher map, (b) loss routing, (c) per-pixel loss vs offset
H, W, R = 24, 36, 2
yy, xx = np.mgrid[:H, :W]
crack = np.abs(yy - (8 + 0.25 * xx).astype(int)) == 0          # thin teacher crack line
conf = np.ones((H, W), bool); conf[16:, 24:] = False; conf[:5, :8] = False   # two low-confidence patches
pad = np.pad(crack, R)                                           # (2R+1)^2 max-pool, as in TolerantPLLoss
band = np.zeros_like(crack)
for dy in range(2 * R + 1):
    for dx in range(2 * R + 1):
        band |= pad[dy:dy + H, dx:dx + W]
teach = np.where(crack, 2, np.where(conf, 0, 1))               # 0 confident bg, 1 unsure, 2 rare-class argmax
route = np.where(crack, 2, np.where(band, 1, np.where(conf, 0, 1)))  # 0 CE, 1 no loss, 2 tolerant rare term
fig, axs = plt.subplots(1, 3, figsize=(12, 3.5), gridspec_kw={"width_ratios": [1, 1, 1.1]})
axs[0].imshow(teach, cmap=ListedColormap(["#c7c7c7", "#ffffff", "#d62728"]), vmin=0, vmax=2)
axs[0].set_title("(a) teacher: argmax + confidence", fontsize=9.5)
axs[0].legend(handles=[Patch(color="#d62728", label="rare class (crack) argmax"), Patch(color="#c7c7c7", label="confident head class (≥ t_pos)"),
                       Patch(facecolor="#ffffff", edgecolor="#999", label="unsure")], fontsize=7, loc="lower left", framealpha=0.9)
axs[1].imshow(route, cmap=ListedColormap(["#1f77b4", "#ffffff", "#d62728"]), vmin=0, vmax=2)
axs[1].set_title(f"(b) loss routing (band R = {R} px)", fontsize=9.5)
axs[1].legend(handles=[Patch(color="#d62728", label="−p_t·log maxpool₅ₓ₅(p_s)  (tolerant)"), Patch(color="#1f77b4", label="CE on teacher label"),
                       Patch(facecolor="#ffffff", edgecolor="#999", label="no loss (band / unsure)")], fontsize=7, loc="lower left", framealpha=0.9)
for a in axs[:2]:
    a.set_xticks([]); a.set_yticks([])
    for s in a.spines.values():
        s.set_visible(True); s.set_color("#999")
off = np.arange(0, 9)
p_on, p_off = 0.9, 0.05      # student crack prob on its own (shifted) line / elsewhere
strict = np.where(off == 0, -np.log(p_on), -np.log(p_off))
toler = np.where(off <= R, -np.log(p_on), -np.log(p_off))
axs[2].plot(off, strict, "o-", color="#7f7f7f", label="pixel-exact pseudo-label CE")
axs[2].plot(off, toler, "s-", color="#d62728", label=f"tolerant term (max-pool {2 * R + 1}×{2 * R + 1})")
axs[2].set_xlabel("student crack offset from teacher crack (px)"); axs[2].set_ylabel("loss at a teacher crack pixel")
axs[2].set_title("(c) a 1–2 px offset is not punished", fontsize=9.5); axs[2].legend(fontsize=7.5); axs[2].grid(alpha=0.3)
fig.tight_layout(); os.makedirs(os.path.join(ROOT, "results/figures"), exist_ok=True)
fig.savefig(os.path.join(ROOT, "results/figures/fig_method_routing.png"), dpi=170); plt.close(fig)
print("wrote results/p5_region_pl/fig_p5_offset.png results/figures/fig_method_routing.png")
