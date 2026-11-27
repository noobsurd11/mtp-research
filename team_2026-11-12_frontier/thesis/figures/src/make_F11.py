"""F11: guard values per arm on cv5v3 (5 seeds, OP-A), each against PF as registered: false crack px on the crack-free cells
as a multiple of PF (bound 1.5 x), and the crack width ratio arm / PF pooled and on ARTS (band 0.85 to 1.15); 532 and
416 clean cells.

Sources: results/HOUSEPF_READ.md l23 to l27; results/C3HRNET_READ.md l15 to l19; results/c3swad_read/verdict.txt;
results/c3x_read/verdict.txt; results/final_tta_read/verdict.txt (VT) sections (a) and (c).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

C.setup()
CELLS = {"532": "532 cells", "416": "416 clean cells"}


def from_verdict(rel, section):
    out = {}
    for k, cells in CELLS.items():
        wp = C.find(rel, rf"^(PASS|FAIL)\twidth_pooled\t{cells}\tOP-A\tall \(n \d+\): width {C.NUM} / {C.NUM} = ({C.NUM}) ",
                    section=section)
        wa = C.find(rel, rf"^(PASS|FAIL)\twidth_source\t{cells}\tOP-A\tsrc:ARTS \(n \d+\): width {C.NUM} / {C.NUM} = ({C.NUM}) ",
                    section=section)
        fa = C.find(rel, rf"^(PASS|FAIL)\tfalse_alarm\t{cells}\tOP-A\tfalse crack px on crack-free cells (?:\S+ )?(\d+) "
                         rf"against (?:PF )?(\d+) = ({C.NUM}) x", section=section)
        out[("fa", k)] = (fa.groups[3], fa.groups[0], fa.src)
        out[("wpool", k)] = (wp.groups[1], wp.groups[0], wp.src)
        out[("warts", k)] = (wa.groups[1], wa.groups[0], wa.src)
    return out


def from_md(rel, arm):
    hdr = C.find(rel, r"^\| Guard \| 532, OP-A \| 532, OP-W \| 416, OP-A \| 416, OP-W \|$")
    wp = C.find(rel, rf"^\| width ratio pooled \({arm} / PF")
    wa = C.find(rel, r"^\| width per source \(?ARTS / BMRK / CFVS / CSIR\)? \|")
    fa = C.find(rel, r"^\| false crack px on crack-free cells \(303 / 226 cells")
    assert hdr.line < wp.line and hdr.line < wa.line and hdr.line < fa.line

    def cells(h):
        return [c.strip() for c in h.text.strip().strip("|").split("|")][1:]

    out = {}
    for k, col in (("532", 0), ("416", 2)):  # columns 532 OP-A and 416 OP-A
        out[("wpool", k)] = (cells(wp)[col], "", wp.src)
        out[("warts", k)] = (cells(wa)[col].split("/")[0].replace("*", "").strip(), "", wa.src)
        f = cells(fa)[col].replace("*", "")
        out[("fa", k)] = (f.split("=")[1].replace("x", "").strip(), "", fa.src)
    return out


C3S = "results/c3swad_read/verdict.txt"
C3X = "results/c3x_read/verdict.txt"
VT = "results/final_tta_read/verdict.txt"
arms = [
    ("HOUSE", from_md("results/HOUSEPF_READ.md", "HOUSE"), ""),
    ("HRNET", from_md("results/C3HRNET_READ.md", "HRNET"), ""),
    ("SWADBN", from_verdict(C3S, r"^## SWADBN \(primary, swad_bn\)$"), ""),
    ("SWAD", from_verdict(C3S, r"^## SWAD \(declared secondary, swad\)$"), ""),
    ("COMBO", from_verdict(C3X, r"^## COMBO = COMBO \(swad_bn\) against PF \(primary\)$"), ""),
    ("CS", from_verdict(C3X, r"^## COMBO_SWAD = COMBO\.swad \(swad\) against PF"), "sb"),
    ("PF_D4", from_verdict(VT, r"^## \(a\) PF_D4 - PF: "), ""),
    ("CS_D4 (C2 recipe)", from_verdict(VT, r"^## \(c\) CS_D4 - PF: "), "sb"),
]

fig, (axa, axb) = plt.subplots(1, 2, figsize=(C.WIDTH, 7.6 * C.CM), sharey=True, layout="constrained",
                               gridspec_kw={"width_ratios": [1, 1.15]})
n = len(arms)
ys = list(range(n))[::-1]
dy = {"532": 0.14, "416": -0.14}
for (arm, d, note), y in zip(arms, ys):
    for k in ("532", "416"):
        filled = k == "532"
        v = C.num(d[("fa", k)][0])
        axa.plot([v], [y + dy[k]], marker="s", ls="none", ms=5, markeredgecolor=C.DARK, markeredgewidth=1.0,
                 markerfacecolor=C.DARK if filled else "white", zorder=3)
        for key, col, mk in (("wpool", C.BLUE, "o"), ("warts", C.VERM, "^")):
            v = C.num(d[(key, k)][0])
            axb.plot([v], [y + dy[k]], marker=mk, ls="none", ms=5, markeredgecolor=col, markeredgewidth=1.0,
                     markerfacecolor=col if filled else "white", zorder=3)
# panel a: false crack px multiple of PF; bound 1.5 x, PF = 1
axa.set_xscale("log")
axa.set_xlim(0.1, 5)
axa.set_xticks([0.1, 0.2, 0.5, 1, 2, 5])
axa.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5"])
axa.minorticks_off()
axa.axvline(1.0, color=C.GREY, lw=1.0, zorder=1)
axa.axvline(1.5, color=C.DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)
axa.axvspan(0.1, 1.5, color=C.BAND, zorder=0)
axa.text(1.5, 1.005, "1.5", transform=axa.get_xaxis_transform(), ha="center", va="bottom", fontsize=8)
axa.set_xlabel("False crack px on crack-free cells,\nmultiple of PF (bound 1.5)")
axa.grid(axis="x")
# panel b: width ratio arm / PF; band 0.85 to 1.15
axb.axvspan(0.85, 1.15, color=C.BAND, zorder=0)
axb.axvline(1.0, color=C.GREY, lw=1.0, zorder=1)
axb.set_xlim(0.8, 1.42)
axb.set_xticks([0.9, 1.0, 1.1, 1.2, 1.3, 1.4])
axb.set_xlabel("Crack width ratio, arm / PF\n(band 0.85 to 1.15)")
axb.grid(axis="x")
axa.set_yticks(ys)
axa.set_yticklabels([a[0] + (" *" if a[2] == "sb" else "") for a in arms])
axa.set_ylim(-0.6, n - 0.4)
for ax, t in ((axa, "a"), (axb, "b")):
    ax.text(0.0, 1.02, t, transform=ax.transAxes, fontweight="bold", ha="left", va="bottom")
handles = [Line2D([], [], marker="s", ls="none", ms=5, color=C.DARK, label="false crack px"),
           Line2D([], [], marker="o", ls="none", ms=5, color=C.BLUE, label="width, pooled"),
           Line2D([], [], marker="^", ls="none", ms=5, color=C.VERM, label="width, ARTS"),
           Line2D([], [], marker="o", ls="none", ms=5, markerfacecolor=C.MUTED, markeredgecolor=C.MUTED,
                  label="532 cells (filled)"),
           Line2D([], [], marker="o", ls="none", ms=5, markerfacecolor="white", markeredgecolor=C.MUTED,
                  label="416 clean cells (open)")]
fig.legend(handles=handles, loc="outside lower center", ncol=5, handletextpad=0.3, columnspacing=1.0)
C.save(fig, "F11")

rows = []
for arm, d, note in arms:
    for key, lab in (("fa", "false crack px, multiple of PF"), ("wpool", "width ratio pooled, arm / PF"),
                     ("warts", "width ratio ARTS, arm / PF")):
        for k in ("532", "416"):
            v, pf, src = d[(key, k)]
            rows.append([arm, "yes" if note == "sb" else "no", lab, k, "OP-A", v, src])
C.write_csv("F11", ["arm", "selection_biased", "guard", "cells", "op", "value", "source"], rows)
print("F11 ok", len(rows), "values")
