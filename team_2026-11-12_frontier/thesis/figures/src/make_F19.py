"""F19: cost against quality for the E1 candidates. (a) GFLOPs per cell, (b) GPU s per cell (cv02 RTX A6000, fp32, batch 1,
median), each against E1 crack relF1@2 (OP-A; mean over seeds 5 to 9 with the range over seeds for C1, C1-D4, C2; one
ensemble each for E-PF and C3). Log x axes; one y axis per panel (no dual axis).

Sources: thesis/INFERENCE_COST.md (md5 1e5a9002) l61 to l65 (section 3.3, GFLOPs per cell) and l73 to l78 (section 3.4, GPU);
results/final_opening_read/read_e1/read.txt (R8) l6 to l11 (= TT T11a).
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

import figA_common as C  # noqa: E402

IC = "thesis/INFERENCE_COST.md"
R8 = "results/final_opening_read/read_e1/read.txt"
with open(os.path.join(C.T, IC), "rb") as fh:
    assert hashlib.md5(fh.read()).hexdigest().startswith("1e5a9002"), "INFERENCE_COST.md changed"
C.setup()

ARMS = [("C1", "C1", "C1", 5), ("C1-D4", "C1-D4", "C1D4", 5), ("E-PF", "E-PF", "EPF", 1), ("C2", "C2", "C2", 5),
        ("C3", "C3", "C3", 1)]
S33 = r"^### 3\.3 Headline"
S34 = r"^### 3\.4 cv02 GPU"
data = []
for arm, ic_key, r8_key, nmod in ARMS:
    g = C.find(IC, rf"^\| {ic_key} \| (\d+) \| ([\d,]+) \| ", section=S33)
    t = C.find(IC, rf"^\| {ic_key} \| (\d+) \| ({C.NUM}) \(({C.NUM})\) \[(\d+)\] \| ", section=S34)
    q = C.find(R8, rf"^\| {r8_key} \| {nmod} \| ({C.NUM}) \[({C.NUM}), ({C.NUM})\] \|", section=r"^## subset all: ")
    data.append((arm, g, t, q, nmod))

fig, axs = plt.subplots(1, 2, figsize=(C.WIDTH, 7.0 * C.CM), sharey=True, layout="constrained")
OFFS = {"C1": (6, -10), "C1-D4": (6, -11), "E-PF": (6, 3), "C2": (-8, 5), "C3": (-8, -12)}
for ax, which, xl in ((axs[0], "g", "GFLOPs per cell (log scale)"),
                      (axs[1], "t", "GPU s per cell, batch 1, median (log scale)")):
    for arm, g, t, q, nmod in data:
        x = float(g.groups[1].replace(",", "")) if which == "g" else t.f(1)
        y, lo, hi = q.f(0), q.f(1), q.f(2)
        col, mk = C.ARM_COLOR[arm], C.ARM_MARK[arm]
        if nmod == 5:
            ax.plot([x, x], [lo, hi], color=col, lw=1.0, zorder=2)
        ax.plot([x], [y], marker=mk, color=col, ms=6, ls="none", zorder=3)
        dx, dy = OFFS[arm]
        ax.annotate(arm, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=8,
                    ha="left" if dx > 0 else "right", va="center", color=C.DARK)
    ax.set_xscale("log")
    ax.set_xlabel(xl)
    ax.grid(True, which="major")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
axs[0].set_xlim(80, 16000)
axs[1].set_xlim(0.006, 1.6)
axs[0].set_ylabel("Crack relF1@2 on E1 (OP-A)")
axs[0].set_ylim(0.415, 0.515)
for ax, t in ((axs[0], "a"), (axs[1], "b")):
    ax.text(0.0, 1.02, t, transform=ax.transAxes, fontweight="bold", ha="left", va="bottom")
C.save(fig, "F19")

rows = []
for arm, g, t, q, nmod in data:
    rows.append([arm, g.groups[0], g.groups[1], g.src, t.groups[1], t.groups[2], t.groups[3], t.src,
                 q.groups[0], f"{q.groups[1]} to {q.groups[2]}" if nmod == 5 else "one ensemble, no range", nmod, q.src])
C.write_csv("F19", ["arm", "forwards_per_cell", "GFLOPs_per_cell", "source_GFLOPs", "GPU_s_per_cell_b1_median",
                    "GPU_s_p90", "GPU_n_cells", "source_GPU", "E1_relF1@2", "range_over_seeds", "models",
                    "source_relF1"], rows)
print("F19 ok", len(rows) * 3, "values")
