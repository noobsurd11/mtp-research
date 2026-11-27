"""F15: E1 crack relF1@2 per trained model (seeds 5 to 9) for C1, C2, C1-D4 at OP-A, with the arm means. Decides nothing.

Sources: results/final_opening_read/verdict.txt (V8) l23 to l32, l36 to l40 (per model);
results/final_opening_read/read_e1/read.txt (R8) l6, l7, l11 (arm mean over the 5 models).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402

import figA_common as C  # noqa: E402

V8 = "results/final_opening_read/verdict.txt"
R8 = "results/final_opening_read/read_e1/read.txt"
C.setup()
SEC = r"^## E1 per model \(OP-A\)"
ARMS = [("C1", "C1", "C1\n(PF, 1 view)"), ("C1-D4", "C1D4", "C1-D4\n(PF, D4)"), ("C2", "C2", "C2\n(final recipe)")]
SEEDS = [5, 6, 7, 8, 9]
OFF = {s: (s - 7) * 0.07 for s in SEEDS}

rows = []
fig, ax = plt.subplots(figsize=(C.WIDTH * 0.72, 6.8 * C.CM), layout="constrained")
for xi, (arm, key, lab) in enumerate(ARMS):
    col = C.ARM_COLOR[arm]
    for s in SEEDS:
        h = C.find(V8, rf"^{key}\tseed {s}\t({C.NUM})\t", section=SEC)
        rows.append([arm, s, h.groups[0], "per-model value", h.src])
        ax.plot([xi + OFF[s]], [h.f(0)], marker=C.ARM_MARK[arm], color=col, ms=5, ls="none", zorder=3,
                markeredgecolor="white", markeredgewidth=0.5)
    m = C.find(R8, rf"^\| {key} \| 5 \| ({C.NUM}) \[({C.NUM}), ({C.NUM})\] \|", section=r"^## subset all: ")
    rows.append([arm, "mean of 5", m.groups[0], "arm mean (range over seeds " + m.groups[1] + " to " + m.groups[2] + ")",
                 m.src])
    ax.plot([xi - 0.22, xi + 0.22], [m.f(0)] * 2, color=C.DARK, lw=1.2, zorder=2)
    ax.text(xi + 0.25, m.f(0), f"{m.f(0):.4f}", va="center", ha="left", fontsize=8, color=C.DARK)
ax.set_xticks(range(len(ARMS)))
ax.set_xticklabels([a[2] for a in ARMS])
ax.set_xlim(-0.5, len(ARMS) - 0.35)
ax.set_ylabel("Crack relF1@2 on E1 (OP-A)")
ax.set_ylim(0.415, 0.515)
ax.grid(axis="y")
C.save(fig, "F15")
C.write_csv("F15", ["arm", "seed", "relF1@2", "kind", "source"], rows)
print("F15 ok", len(rows), "values")
