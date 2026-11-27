"""F14: E1 opening #8, P = C2 - C1 (crack relF1@2, OP-A) by stratum, seed-aware 95% intervals; strata decide nothing.

Sources: results/final_opening_read/verdict.txt (V8) l10 to l11 (all cells), l53 to l57 (strata).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as mtransforms  # noqa: E402

import figA_common as C  # noqa: E402

V8 = "results/final_opening_read/verdict.txt"
C.setup()

hdr = C.find(V8, r"^## E1 opening #8: the primary contrast P = C2 - C1 \(crack relF1@2, OP-A, (\d+) cells, (\d+) clusters\)$")
p = C.find(V8, rf"^Delta ({C.NUM}), seed-aware 95% interval \[({C.NUM}), ({C.NUM})\] \(SE ({C.NUM})\); M ({C.NUM})$")
M = p.f(4)
rows = [("All cells", hdr.groups[0], hdr.groups[1], p.groups[:3], p.src + "; n " + hdr.src, "all")]
SEC = r"^## E1 strata \(decide nothing\)"
for lab, key in [("Full cells", "type:full"), ("Half-cut cells", "type:halfcut"), ("CSIR cells", "src:CSIR"),
                 ("BMRK cells", "src:BMRK"), ("Crack cells", "crack_cells")]:
    h = C.find(V8, rf"^{key}\t(\d+) / (\d+)\trelF1@2 " + C.IV, section=SEC)
    rows.append((lab, h.groups[0], h.groups[1], h.groups[2:5], h.src, key))

n = len(rows)
fig = plt.figure(figsize=(C.WIDTH, 6.4 * C.CM), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[2.25, 1.0])
ax = fig.add_subplot(gs[0])
axt = fig.add_subplot(gs[1], sharey=ax)
ys = list(range(n))[::-1]
for (lab, nc, ncl, (d, lo, hi), src, key), y in zip(rows, ys):
    d, lo, hi = C.num(d), C.num(lo), C.num(hi)
    col = C.BLUE if key == "all" else C.MUTED
    ax.plot([lo, hi], [y, y], color=col, lw=1.6 if key == "all" else 1.0, solid_capstyle="butt", zorder=3)
    ax.plot([d], [y], marker="s" if key == "all" else "o", color=col, ms=5.5 if key == "all" else 4.5, ls="none",
            zorder=4)
    axt.text(0.0, y, f"{d:+.4f} [{lo:+.4f}, {hi:+.4f}]", va="center", ha="left", fontsize=8,
             color=C.DARK if key == "all" else C.MUTED)
C.zero_line(ax)
ax.axvline(M, color=C.DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)
tr = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
ax.text(M, 1.005, "M 0.010", transform=tr, ha="left", va="bottom", fontsize=8)
ax.axhline(ys[0] - 0.5, color=C.GRID, lw=0.8, zorder=0)
ax.set_yticks(ys)
ax.set_yticklabels([f"{r[0]} ({r[1]} / {r[2]})" for r in rows])
ax.get_yticklabels()[0].set_fontweight("bold")
ax.set_ylim(-0.6, n - 0.4)
ax.set_xlim(-0.6, 0.27)
ax.set_xlabel("C2 - C1, crack relF1@2 (E1, OP-A), seed-aware 95% interval")
ax.grid(axis="x")
axt.set_axis_off()
axt.text(0.0, 1.005, "delta [seed-aware 95%]", transform=axt.transAxes, ha="left", va="bottom", fontsize=8,
         color=C.MUTED)
C.save(fig, "F14")

C.write_csv("F14", ["row", "stratum", "cells", "clusters", "delta", "lo95", "hi95", "source"],
            [[i + 1, r[0], r[1], r[2], *r[3], r[4]] for i, r in enumerate(rows)]
            + [[n + 1, "M (decision margin)", "", "", p.groups[4], "", "", p.src]])
print("F14 ok", n, "strata")
