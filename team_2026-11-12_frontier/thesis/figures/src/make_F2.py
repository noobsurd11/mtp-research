"""F2: crack label geometry on the pool (v1.1, 229 crack cells): strict crack IoU of the label against itself shifted by 1 and
2 px (mean of 8 directions), reduced to its 1 px centreline, and redrawn 3 px wide; pooled bars and per-source points.

Source: dataset_audit/out/labels_audit.txt section f1 (l77 to l86).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

LA = "dataset_audit/out/labels_audit.txt"
C.setup()
SEC = r"^## f1\. Strict crack IoU of the v1\.1 label against itself"
hdr = C.find(LA, r"^## f1\. .*pooled over the (\d+) crack cells; mean of (\d+) directions\)$")
VARS = [("sh1", "shifted 1 px"), ("sh2", "shifted 2 px"), ("skel", "1 px centreline"), ("w3", "redrawn 3 px wide")]
TICK = {"sh1": "shifted\n1 px", "sh2": "shifted\n2 px", "skel": "reduced to\n1 px centreline", "w3": "redrawn\n3 px wide"}
pooled = {k: C.find(LA, rf"^{k}: IoU ({C.NUM})$", section=SEC) for k, _ in VARS}
SRCS = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]
per = {s: C.find(LA, rf"^  {s}: shift 1 px ({C.NUM}); skeleton ({C.NUM}); 3-px redraw ({C.NUM})$", section=SEC)
       for s in SRCS}
PER_IDX = {"sh1": 0, "skel": 1, "w3": 2}
MK = {"ARTS": "o", "BMRK": "s", "CFVS": "^", "CSIR": "D", "SDLE": "v"}

fig, ax = plt.subplots(figsize=(C.WIDTH * 0.85, 6.4 * C.CM), layout="constrained")
xs = range(len(VARS))
for x, (k, lab) in zip(xs, VARS):
    v = pooled[k].f(0)
    ax.bar(x, v, width=0.6, color=C.BLUE, zorder=2)
    ax.text(x - 0.32, v + 0.012, pooled[k].groups[0], ha="left", va="bottom", fontsize=8)
    if k in PER_IDX:
        for j, s in enumerate(SRCS):
            ax.plot([x + 0.18 + (j - 2) * 0.045], [per[s].f(PER_IDX[k])], marker=MK[s], ms=4, ls="none",
                    markerfacecolor="white", markeredgecolor=C.DARK, markeredgewidth=0.8, zorder=3)
ax.set_xticks(list(xs))
ax.set_xticklabels([TICK[v[0]] for v in VARS])
ax.set_ylim(0, 1.0)
ax.set_ylabel("Strict crack IoU\nagainst the v1.1 label")
ax.grid(axis="y")
hs = [Line2D([], [], color=C.BLUE, lw=6, label=f"pooled, {hdr.groups[0]} crack cells")]
hs += [Line2D([], [], marker=MK[s], ls="none", ms=4, markerfacecolor="white", markeredgecolor=C.DARK, label=s)
       for s in SRCS]
ax.legend(handles=hs, loc="upper left", ncol=3, columnspacing=1.0)
C.save(fig, "F2")

rows = [[lab, "pooled", pooled[k].groups[0], pooled[k].src] for k, lab in VARS]
for s in SRCS:
    for k, lab in VARS:
        if k in PER_IDX:
            rows.append([lab, s, per[s].groups[PER_IDX[k]], per[s].src])
C.write_csv("F2", ["variant", "set", "strict_crack_IoU", "source"], rows)
print("F2 ok", len(rows), "values")
