"""F16: E1 per-class IoU of the 13 robust classes, C1 against C2 (OP-A, arm means over seeds 5 to 9). Decides nothing.

Source: results/final_opening_read/verdict.txt (V8) l63 to l75 (columns C1, C2 of the per-class table).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

V8 = "results/final_opening_read/verdict.txt"
C.setup()
SEC = r"^## E1 per-class IoU of the 13 robust classes"
head = C.find(V8, r"^\| class \| C1 \| C2 \| C3 \| EPF \| C2S5 \| C1D4 \|$", section=SEC)
ls = C.lines(V8)
rows = []
i = head.line + 1  # skip the |---| line
while True:
    t = ls[i]
    if not t.startswith("| "):
        break
    cells = [c.strip() for c in t.strip("|").split("|")]
    if cells[0].startswith("---"):
        i += 1
        continue
    rows.append((cells[0], cells[1], cells[2], f"{V8}:{i + 1}"))
    i += 1
assert len(rows) == 13, len(rows)

fig, ax = plt.subplots(figsize=(C.WIDTH * 0.72, 8.2 * C.CM), layout="constrained")
n = len(rows)
ys = list(range(n))[::-1]
for (cls, c1, c2, src), y in zip(rows, ys):
    v1 = C.num(c1)
    if c2 != "n/a":
        v2 = C.num(c2)
        ax.plot([v1, v2], [y, y], color=C.GRID if abs(v2 - v1) < 1e-9 else "#bbbbbb", lw=1.6, zorder=2,
                solid_capstyle="butt")
        ax.plot([v2], [y], marker="s", color=C.BLUE, ms=4.5, ls="none", zorder=3)
    else:
        ax.text(v1 + 0.03, y, "C2 n/a", va="center", ha="left", fontsize=8, color=C.MUTED)
    ax.plot([v1], [y], marker="o", ms=7.5, ls="none", zorder=4, markerfacecolor="none", markeredgecolor=C.GREY,
            markeredgewidth=1.3)
ax.set_yticks(ys)
ax.set_yticklabels([r[0] for r in rows])
ax.set_ylim(-0.6, n - 0.4)
ax.set_xlim(-0.02, 1.02)
ax.set_xlabel("IoU on E1 (OP-A, mean over seeds 5 to 9)")
ax.grid(axis="x")
ax.legend(handles=[Line2D([], [], marker="o", ls="none", ms=7.5, markerfacecolor="none", markeredgecolor=C.GREY,
                          markeredgewidth=1.3, label="C1 (PF)"),
                   Line2D([], [], marker="s", color=C.BLUE, ls="none", ms=4.5, label="C2 (final recipe)")],
          loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0.2)
C.save(fig, "F16")
C.write_csv("F16", ["class", "C1_IoU", "C2_IoU", "source"], [list(r) for r in rows])
print("F16 ok", n, "classes")
