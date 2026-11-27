"""F5: strict crack IoU against relF1@2 under label conventions. (a) PF levels; (b) strict crack IoU and (c) relF1@2 contrasts
of four arms against PF with 95% two-stage group-bootstrap intervals, each scored on the 1 px centreline labels, the
BenchmarkEL 20211104 labels, v1.1 and labels redrawn 3 px wide (same predictions: 25 out-of-fold cv5v3 models, 532 pool cells,
argmax). The candidate-ignore variant (candign) is not drawn.

Source: dataset_audit/out/contrasts.txt l2 (M), l6 to l29 (levels), l39 to l54 (contrasts).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

CT = "dataset_audit/out/contrasts.txt"
C.setup()
M = C.find(CT, rf"^# two-stage group bootstrap: .* M = ({C.NUM})\.$")
SL = r"^## Levels \(mean over 5 seeds of the pooled metric\), per label variant$"
SC = r"^## Contrasts X minus PF per label variant"
VAR = [("skel", "1 px centreline", C.VERM, "v"), ("old", "20211104 release", C.PURPLE, "D"),
       ("v11", "v1.1 (benchmark)", C.BLUE, "o"), ("w3", "3 px redraw", C.GREEN, "s")]
CON = [("HOUSE-PF", "HOUSE - PF"), ("HRNET-PF", "HRNET - PF"), ("SWADBN-PF", "SWADBN - PF"), ("C3X-PF", "COMBO (C3X) - PF")]
lev = {v: C.find(CT, rf"^{v} \| PF \| ({C.NUM}) \| ({C.NUM}) \| ", section=SL) for v, *_ in VAR}
IVP = r"([+-]\d+\.\d+) \[([+-]\d+\.\d+), ([+-]\d+\.\d+)\] (?:PASS|-)"
con = {(v, c): C.find(CT, rf"^{v} \| {c} \| {IVP} \| {IVP} \| ", section=SC) for v, *_ in VAR for c, _ in CON}

fig = plt.figure(figsize=(C.WIDTH, 7.4 * C.CM), layout="constrained")
gs = fig.add_gridspec(1, 3, width_ratios=[0.8, 1.15, 1.15])
axa = fig.add_subplot(gs[0])
axb = fig.add_subplot(gs[1])
axc = fig.add_subplot(gs[2], sharey=axb, sharex=axb)
# (a) PF levels
w = 0.19
for i, (metric, gi) in enumerate((("strict crack IoU", 0), ("relF1@2", 1))):
    for j, (v, lab, col, mk) in enumerate(VAR):
        axa.bar(i + (j - 1.5) * w, lev[v].f(gi), width=w * 0.92, color=col, zorder=2)
axa.set_xticks([0, 1])
axa.set_xticklabels(["strict\ncrack IoU", "relF1@2"])
axa.set_ylim(0, 1.0)
axa.set_ylabel("PF level (532 pool cells)")
axa.grid(axis="y")
# (b), (c) contrasts
ny = len(CON)
ys = list(range(ny))[::-1]
for ax, gi in ((axb, 0), (axc, 3)):
    for (c, clab), y in zip(CON, ys):
        for j, (v, lab, col, mk) in enumerate(VAR):
            h = con[(v, c)]
            d, lo, hi = h.f(gi), h.f(gi + 1), h.f(gi + 2)
            yy = y + (1.5 - j) * 0.17
            ax.plot([lo, hi], [yy, yy], color=col, lw=1.0, solid_capstyle="butt", zorder=3)
            ax.plot([d], [yy], marker=mk, color=col, ms=4, ls="none", zorder=4)
    C.zero_line(ax)
    ax.axvline(M.f(0), color=C.DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)
    ax.text(M.f(0), 1.005, "M", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
    ax.grid(axis="x")
axb.set_yticks(ys)
axb.set_yticklabels([c[1] for c in CON])
axb.set_ylim(-0.6, ny - 0.4)
axb.set_xlim(-0.03, 0.055)
plt.setp(axc.get_yticklabels(), visible=False)
axb.set_xlabel("Strict crack IoU,\narm - PF, 95% CI")
axc.set_xlabel("Crack relF1@2,\narm - PF, 95% CI")
for ax, t in ((axa, "a"), (axb, "b"), (axc, "c")):
    ax.text(0.0, 1.02, t, transform=ax.transAxes, fontweight="bold", ha="left", va="bottom")
fig.legend(handles=[Line2D([], [], marker=mk, color=col, ms=4.5, lw=1.0, label=lab) for v, lab, col, mk in VAR],
           loc="outside lower center", ncol=4, title=None)
C.save(fig, "F5")

rows = []
for v, lab, *_ in VAR:
    rows.append(["PF level", lab, "strict crack IoU", lev[v].groups[0], "", "", lev[v].src])
    rows.append(["PF level", lab, "relF1@2", lev[v].groups[1], "", "", lev[v].src])
for c, clab in CON:
    for v, lab, *_ in VAR:
        h = con[(v, c)]
        rows.append([clab, lab, "strict crack IoU", *h.groups[0:3], h.src])
        rows.append([clab, lab, "relF1@2", *h.groups[3:6], h.src])
rows.append(["M", "", "", M.groups[0], "", "", M.src])
C.write_csv("F5", ["row", "label_variant", "metric", "value", "lo95", "hi95", "source"], rows)
print("F5 ok", len(rows) - 1, "values")
