"""F6: crack label width per source on the pool (v1.1), box plot of per-cell width = crack px / skeleton px for cells with at
least 50 skeleton px (the definition of labels_audit.txt b1).

Sources: dataset_audit/out/labels_percell.tsv (532 pool cells; columns area = crack px, sklen = skeleton px, v1.1);
check against dataset_audit/out/labels_audit.txt b1 (l5 to l11): per-source cell medians and n 207 must match.
The per-cell width is derived (area / sklen) as the audit defines it; it is the only computed quantity in this figure.
"""
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402

import figA_common as C  # noqa: E402

PC = "dataset_audit/out/labels_percell.tsv"
LA = "dataset_audit/out/labels_audit.txt"
C.setup()
ls = C.lines(PC)
head = ls[0].split("\t")
iS, iSrc, iA, iL = head.index("stem"), head.index("src"), head.index("area"), head.index("sklen")
SRCS = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]
w = {s: [] for s in SRCS}
rows = []
n_all = 0
for ln, t in enumerate(ls[1:], start=2):
    if not t.strip():
        continue
    f = t.split("\t")
    n_all += 1
    a, k = int(f[iA]), int(f[iL])
    if k >= 50:
        v = a / k
        w[f[iSrc]].append(v)
        rows.append([f[iS], f[iSrc], a, k, f"{v:.4f}", f"{PC}:{ln}"])
assert n_all == 532, n_all
SB1 = r"^## b1\. Crack label width"
eta = C.find(LA, rf"^eta\^2 .*cells with >= 50 skeleton px, n (\d+)\): ({C.NUM})$", section=SB1)
assert len(rows) == int(eta.groups[0]), (len(rows), eta.groups[0])
chk = []
for s in SRCS:
    b = C.find(LA, rf"^{s} \| (\d+) \| ({C.NUM}) \| ({C.NUM}) \| ", section=SB1)
    med = statistics.median(w[s])
    assert abs(med - b.f(2)) < 6e-4, (s, med, b.groups[2])
    chk.append([s, len(w[s]), f"{med:.4f}", b.groups[2], b.groups[1], b.src])

fig, ax = plt.subplots(figsize=(C.WIDTH * 0.75, 6.4 * C.CM), layout="constrained")
BOX = [s for s in SRCS if len(w[s]) >= 10]  # SDLE has 2 cells: drawn as points, not as a box
data = [w[s] for s in BOX]
bp = ax.boxplot(data, positions=[SRCS.index(s) for s in BOX], widths=0.5, whis=1.5, patch_artist=True, showfliers=True,
                medianprops=dict(color=C.DARK, lw=1.4), boxprops=dict(facecolor="#cfe3f1", edgecolor=C.BLUE, lw=0.9),
                whiskerprops=dict(color=C.BLUE, lw=0.9), capprops=dict(color=C.BLUE, lw=0.9),
                flierprops=dict(marker="o", ms=3, markerfacecolor="none", markeredgecolor=C.MUTED, markeredgewidth=0.6))
for i, s in enumerate(SRCS):
    if s not in BOX:
        ax.plot([i] * len(w[s]), w[s], marker="o", ms=4, ls="none", markerfacecolor=C.BLUE, markeredgecolor=C.BLUE)
    ax.text(i, 0.02, f"n {len(w[s])}", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=8,
            color=C.MUTED)
ax.set_xticks(range(len(SRCS)))
ax.set_xticklabels(SRCS)
ax.set_ylabel("Crack label width\n(label px per centreline px)")
ax.set_ylim(0, 5.3)
ax.grid(axis="y")
C.save(fig, "F6")
C.write_csv("F6", ["stem", "source", "crack_px", "skeleton_px", "width", "source_line"], rows)
C.write_csv("F6_check", ["source", "n_cells", "median_width_here", "median_width_b1", "pooled_width_b1", "b1_line"], chk)
print("F6 ok", len(rows), "cells; medians match b1:", [c[0] + " " + c[2] for c in chk], "eta^2 line", eta.src)
