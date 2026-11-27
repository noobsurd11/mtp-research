"""F12: crack relP@2 against relR@2 on cv5v3 (532 pool cells, out of fold) for PF, PF_D4, CS, CS_D4 at three operating points
(OP-A argmax, OP-W width-matched bias, OP-F cross-fitted F1 bias), mean (SD) over seeds 5 to 9, with the 0.90 / 0.90 target region.
The read files hold no full bias curve: per arm only these three points and, per seed, the two frontier points
(relR@2 at PF's OP-A relP@2 and relP@2 at PF's OP-A relR@2), drawn small.

Sources: results/final_tta_read/read.txt (RT) l5 to l16 (levels) and l323 to l342 (frontier); BRIEF.md l57 (target).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import figA_common as C  # noqa: E402

RT = "results/final_tta_read/read.txt"
C.setup()
SEC = r"^## headline and guards, mean \(sd\) over seeds, all OOF cells$"
hdr = C.find(RT, r"^arm\top\tseeds\tcrack_iou\trelF1_2\tinact_iou\tmiou_rob\trelP2\trelR2\t", section=SEC)
cols = hdr.text.split("\t")
iP, iR = cols.index("relP2"), cols.index("relR2")
tgt = C.find("BRIEF.md", rf"^\"Almost all cracks\" target set earlier: relR@2 >= ({C.NUM}) at relP@2 >= ({C.NUM})\.")
TR, TP = tgt.f(0), tgt.f(1)

ARMS = ["PF", "PF_D4", "CS", "CS_D4"]
LAB = {"PF": "PF", "PF_D4": "PF_D4", "CS": "CS *", "CS_D4": "CS_D4 (C2 recipe) *"}
OPS = {"OP-A": "o", "OP-W": "s", "OP-F": "^"}
fig, ax = plt.subplots(figsize=(C.WIDTH, 8.6 * C.CM), layout="constrained")
ax.add_patch(Rectangle((TR, TP), 1 - TR, 1 - TP, facecolor=C.BAND, edgecolor=C.DARK, lw=0.7, ls=(0, (4, 2.5)),
                       zorder=0))
ax.text(TR + 0.002, 0.938, f"target\nrelR@2 >= {tgt.groups[0]}\nrelP@2 >= {tgt.groups[1]}", ha="left", va="top",
        fontsize=8)
rows = []
SECF = r"^## frontier \(bias curve, all OOF cells\)"
for arm in ARMS:
    col = C.ARM_COLOR[arm]
    for op, mk in OPS.items():
        h = C.find(RT, rf"^{arm}\t{op}\t5\t", section=SEC)
        f = h.text.split("\t")
        (p, ps), (r, rs) = [x.replace(")", "").split(" (") for x in (f[iP], f[iR])]
        rows.append([arm, op, "mean (sd) over 5 seeds", p, ps, r, rs, h.src])
        ax.errorbar(float(r), float(p), xerr=float(rs), yerr=float(ps), fmt=mk, ms=6 if op == "OP-A" else 5,
                    color=col, markerfacecolor=col if op == "OP-A" else "white", markeredgewidth=1.1, elinewidth=0.8,
                    zorder=4 if op == "OP-A" else 3)
    for s in (5, 6, 7, 8, 9):
        h = C.find(RT, rf"^{arm}\ts{s}\t({C.NUM}) @P ({C.NUM})\t({C.NUM}) @R ({C.NUM})$", section=SECF)
        rows.append([arm, f"frontier seed {s}: relR@2 at PF relP@2", "per seed", h.groups[1], "", h.groups[0], "", h.src])
        rows.append([arm, f"frontier seed {s}: relP@2 at PF relR@2", "per seed", h.groups[2], "", h.groups[3], "", h.src])
        if arm != "PF":
            ax.plot([h.f(0), h.f(3)], [h.f(1), h.f(2)], ls="none", marker=".", ms=3.5, color=col, alpha=0.7, zorder=2)
ax.set_xlim(0.79, 0.925)
ax.set_ylim(0.865, 0.94)
ax.set_xlabel("Crack relR@2 (532 pool cells, out of fold)")
ax.set_ylabel("Crack relP@2")
ax.grid(True)
h1 = [Line2D([], [], marker="o", ls="none", ms=6, color=C.ARM_COLOR[a], label=LAB[a]) for a in ARMS]
h2 = [Line2D([], [], marker=mk, ls="none", ms=5, color=C.MUTED, markerfacecolor=C.MUTED if op == "OP-A" else "white",
             label={"OP-A": "OP-A (argmax)", "OP-W": "OP-W (width-matched)", "OP-F": "OP-F (F1 bias)"}[op])
      for op, mk in OPS.items()]
h3 = [Line2D([], [], marker=".", ls="none", ms=5, color=C.MUTED, label="per seed, at PF's OP-A\nrelP@2 or relR@2")]
fig.legend(handles=h1 + h2 + h3, loc="outside right upper", ncol=1, fontsize=8)
C.save(fig, "F12")
C.write_csv("F12", ["arm", "point", "stat", "relP@2", "relP@2_sd", "relR@2", "relR@2_sd", "source"],
            rows + [["target", "relR@2 >= 0.90 at relP@2 >= 0.90", "", tgt.groups[1], "", tgt.groups[0], "", tgt.src]])
print("F12 ok", len(rows), "values")
