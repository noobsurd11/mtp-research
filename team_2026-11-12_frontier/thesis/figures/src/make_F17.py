"""F17: domain-gap ladder, crack relF1@2 of the PF recipe across instruments (rows of TT T14), plus C2 on E1.

Levels of different models and sets, no interval. Sources (as cited by thesis/SOURCES.tsv for T14):
results/final_tta_read/verdict.txt (VT) l222, l234; results/stageB/U2U4_READ.md l17; results/U1_READ.md l12;
results/final_opening_read/verdict.txt (V8) l120, l130; results/final_opening_read/read_e1/read.txt (R8) l6, l7, l60, l78.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import figA_common as C  # noqa: E402

VT = "results/final_tta_read/verdict.txt"
V8 = "results/final_opening_read/verdict.txt"
R8 = "results/final_opening_read/read_e1/read.txt"
C.setup()


def r8(arm, sub):
    return C.find(R8, rf"^\| {arm} \| 5 \| ({C.NUM}) \[({C.NUM}), ({C.NUM})\] \|", section=rf"^## subset {sub}: ")


SEC_T50 = r"^### Ours on v1\.1 \(our protocol\)"
spec = [
    ("CV5 cv5v3, 532 pool cells", "PF, 5 seeds, out of fold", "cv5",
     C.find(VT, rf"^level\t532 cells\tOP-A\tPF\tcrack_iou {C.NUM}\trelF1_2 ({C.NUM})\t")),
    ("CV5 cv5v3, 416 clean cells", "PF, 5 seeds, out of fold", "cv5",
     C.find(VT, rf"^level\t416 clean cells\tOP-A\tPF\tcrack_iou {C.NUM}\trelF1_2 ({C.NUM})\t")),
    ("U2: unseen-module views (1,064)", "PF W1-G, seeds 5 to 8", "u",
     C.find("results/stageB/U2U4_READ.md", rf"^PF levels on U2: crack IoU {C.NUM}, relF1@2 ({C.NUM}) ")),
    ("U1: held-out CSIR, BMRK (164)", "PF, seeds 5 to 8", "u",
     C.find("results/U1_READ.md", rf"^\| crack relF1@2 \| ({C.NUM}) \| {C.NUM} \|$")),
    ("test50, all 50 cells", "C1 (full-pool PF), 5 seeds", "t50",
     C.find(V8, rf"^all \(50 cells\)\tC1\t({C.NUM})\t", section=SEC_T50)),
    ("test50, nolink16 (16 cells)", "C1 (full-pool PF), 5 seeds", "t50",
     C.find(V8, rf"^nolink16 \(16 cells\)\tC1\t({C.NUM})\t", section=SEC_T50)),
    ("E1, all 106 cells", "C1 (full-pool PF), 5 seeds", "e1", r8("C1", "all")),
    ("E1, 44 full cells", "C1 (full-pool PF), 5 seeds", "e1", r8("C1", r"type:full")),
    ("E1, 62 half-cut cells", "C1 (full-pool PF), 5 seeds", "e1", r8("C1", r"type:halfcut")),
    ("E1, all 106 cells, C2", "C2 (final recipe), 5 seeds", "e1c2", r8("C2", "all")),
]

n = len(spec)
fig, ax = plt.subplots(figsize=(C.WIDTH, 8.0 * C.CM), layout="constrained")
ys = list(range(n))[::-1]
for (lab, model, grp, h), y in zip(spec, ys):
    v = h.f(0)
    if grp == "e1c2":
        kw = dict(color=C.BLUE)
    elif grp == "t50":
        kw = dict(color="#d4d4d4", hatch="////", edgecolor=C.GREY, linewidth=0)
    else:
        kw = dict(color=C.GREY)
    ax.barh(y, v, height=0.62, zorder=2, **kw)
    ax.text(v + 0.008, y, f"{h.groups[0]}", va="center", ha="left", fontsize=8, color=C.DARK)
for i in (2, 4, 6):  # separators above rows 3, 5, 7 (top-down)
    ax.axhline(ys[i] + 0.5, color=C.GRID, lw=0.8, zorder=0)
ax.set_yticks(ys)
ax.set_yticklabels([s[0] for s in spec])
ax.set_ylim(-0.6, n - 0.4)
ax.set_xlim(0, 1.0)
ax.set_xlabel("Crack relF1@2 (OP-A); level, no interval")
ax.grid(axis="x")
ax.legend(handles=[Patch(color=C.GREY, label="PF recipe (CV5, U2, U1: fold models; E1: C1)"),
                   Patch(facecolor="#d4d4d4", hatch="////", edgecolor=C.GREY, linewidth=0,
                         label="PF recipe on test50 (C1; in-distribution, known leakage)"),
                   Patch(color=C.BLUE, label="C2 (final recipe) on E1")],
          loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1, borderaxespad=0.2)
C.save(fig, "F17")

rows = []
for i, (lab, model, grp, h) in enumerate(spec):
    rng = f"{h.groups[1]} to {h.groups[2]}" if len(h.groups) >= 3 else ""
    rows.append([i + 1, lab, model, h.groups[0], rng, h.src])
C.write_csv("F17", ["row", "instrument", "model", "relF1@2", "range over seeds (E1 only; not drawn)", "source"], rows)
print("F17 ok", n, "levels")
