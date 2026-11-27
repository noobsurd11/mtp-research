"""F10: forest plot, crack relF1@2 contrast of every arm against PF (532 pool cells, out of fold, OP-A), 95% two-stage group
bootstrap intervals; 5-seed rows (cv5v3) and 2-seed screens (cv5v2) marked apart; margin M = 0.010.

Sources: the contrasts block of each read.txt (results/rows1_read, rows2_full_read, w2a_read, w2a_spd_read, w2b_lace_read,
w2b_lci_read, c3hrnet_read, c3swad_read, c3x_read, final_tta_read) and results/HOUSEPF_READ.md l12 (HOUSE - PF on cv5v3).
Arms whose primary contrast has another comparator (EMA - RAWBN, SOFTBAND - JMLHARD) are not drawn (see FIGURES_A.md).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.transforms as mtransforms  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import figA_common as C  # noqa: E402

C.setup()
SEC = r"^## contrasts \(B - A\), two-stage group bootstrap 95% CI"


def rd(folder, name, ref="PF"):
    rel = f"results/{folder}/read.txt"
    return C.find(rel, rf"^{name} - {ref}\tOP-A\trelF1_2\t" + C.IV, section=SEC)


G5 = "5-seed rows, cv5v3, training machine"
GT = "2-seed screens, cv5v2, training machine"
GS = "2-seed screens, cv5v2, second machine"
spec = [
    (G5, "HOUSE (plain fine-tune)", C.find("results/HOUSEPF_READ.md", r"^\| crack relF1@2 \| " + C.IV + r" \|"), ""),
    (G5, "HRNET (HRNet-W18 U-Net++)", rd("c3hrnet_read", "HRNET"), ""),
    (G5, "SWADBN (SWAD, swad_bn readout)", rd("c3swad_read", "SWADBN"), ""),
    (G5, "SWAD (SWAD, swad readout)", rd("c3swad_read", "SWAD"), ""),
    (G5, "COMBO (HRNet + SWAD, swad_bn)", rd("c3x_read", "COMBO"), ""),
    (G5, "CS (HRNet + SWAD, swad)", rd("final_tta_read", "CS"), "sb"),
    (G5, "PF_D4 (PF + D4 TTA)", rd("final_tta_read", "PF_D4"), ""),
    (G5, "CS_D4 (C2 recipe on CV5)", rd("final_tta_read", "CS_D4"), "sb"),
    (GT, "HOUSE (plain fine-tune)", rd("rows1_read", "HOUSE"), ""),
    (GT, "U-Net / ResNet-34", rd("rows1_read", "unet_r34_pf"), ""),
    (GT, "U-Net / VGG-16 (Hanifi et al.)", rd("rows1_read", "hanifi_vgg16_unet_pf"), ""),
    (GT, "DeepLabV3+ / ResNet-34", rd("rows1_read", "dlv3p_r34_pf"), ""),
    (GT, "DeepLabV3 / ResNet-50 (UCF-EL)", rd("rows1_read", "ucf_dlv3_r50_pf"), ""),
    (GT, "DeepLabV3+, weighted CE (Pratt)", rd("rows1_read", "pratt_dlv3p_wcec"), ""),
    (GT, "HRNet-W18 U-Net++", rd("rows2_full_read", "hrnet_w18_unetpp_pf"), ""),
    (GT, "SegFormer MiT-B2", rd("rows2_full_read", "segformer_mitb2_pf"), ""),
    (GT, "Skeleton Recall loss", rd("rows2_full_read", "skr01_pf_v11"), ""),
    (GS, "SWAD (swad_bn readout)", rd("w2a_read", "SWADBN"), ""),
    (GS, "SWAD (swad readout)", rd("w2a_read", "SWAD"), ""),
    (GS, "Rare-class sampling (RCS)", rd("w2a_read", "RCS"), ""),
    (GS, "JML loss (hard)", rd("w2a_read", "JMLHARD"), ""),
    (GS, "encoder_spd", rd("w2a_spd_read", "SPD"), ""),
    (GS, "LA-CE (train-time logit offsets)", rd("w2b_lace_read", "LACE"), ""),
    (GS, "Layered inactive head (LCI)", rd("w2b_lci_read", "LCI"), ""),
]
M = C.find("results/final_tta_read/read.txt", rf"^AA\tOP-A\trelF1_2\t{C.IV} SE {C.NUM}\tM ({C.NUM})$")

# rows with group headers
items = []
for g in (G5, GT, GS):
    items.append(("hdr", g))
    items += [("row", s) for s in spec if s[0] == g]
n = len(items)
fig, ax = plt.subplots(figsize=(C.WIDTH, 13.2 * C.CM), layout="constrained")
ys = list(range(n))[::-1]
labels = []
for (kind, it), y in zip(items, ys):
    if kind == "hdr":
        labels.append(it)
        if y != ys[0]:
            ax.axhline(y + 0.5, color=C.GRID, lw=0.8, zorder=0)
        continue
    g, lab, h, note = it
    d, lo, hi = h.f(0), h.f(1), h.f(2)
    col = C.BLUE if g == G5 else C.VERM
    mk = "s" if g == G5 else "o"
    face = "white" if note == "sb" else col
    ax.plot([lo, hi], [y, y], color=col, lw=1.1, solid_capstyle="butt", zorder=3)
    ax.plot([d], [y], marker=mk, ms=4.8, ls="none", zorder=4, markerfacecolor=face, markeredgecolor=col,
            markeredgewidth=1.1)
    labels.append(lab + (" *" if note == "sb" else ""))
C.zero_line(ax)
ax.axvline(M.f(3), color=C.DARK, lw=0.8, ls=(0, (4, 2.5)), zorder=1)
tr = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
ax.text(M.f(3), 1.003, "M 0.010", transform=tr, ha="left", va="bottom", fontsize=8)
ax.set_yticks(ys)
ax.set_yticklabels(labels)
for (kind, _), tl in zip(items, ax.get_yticklabels()):
    if kind == "hdr":
        tl.set_fontweight("bold")
ax.tick_params(axis="y", length=0)
ax.set_ylim(-0.6, n - 0.4)
ax.set_xlim(-0.115, 0.036)
ax.set_xticks([-0.10, -0.05, 0.0])
ax.xaxis.set_minor_locator(plt.MultipleLocator(0.01))
ax.set_xlabel("Arm - PF, crack relF1@2 (OP-A), 95% interval")
ax.grid(axis="x")
ax.legend(handles=[Line2D([], [], marker="s", color=C.BLUE, ls="-", lw=1.1, ms=4.8, label="5-seed row (cv5v3)"),
                   Line2D([], [], marker="s", color=C.BLUE, ls="-", lw=1.1, ms=4.8, markerfacecolor="white",
                          label="5-seed row, selection-biased (*)"),
                   Line2D([], [], marker="o", color=C.VERM, ls="-", lw=1.1, ms=4.8, label="2-seed screen (cv5v2)")],
          loc="lower left", bbox_to_anchor=(0.0, 0.0), borderaxespad=0.4)
C.save(fig, "F10")

rows = []
for i, (g, lab, h, note) in enumerate(spec):
    rows.append([i + 1, g, lab, "yes" if note == "sb" else "no", *h.groups[:3], h.src])
rows.append([len(spec) + 1, "margin", "M (A/A of the cv5v3 read)", "", M.groups[3], "", "", M.src])
C.write_csv("F10", ["row", "group", "arm", "selection_biased", "delta", "lo95", "hi95", "source"], rows)
print("F10 ok", len(spec), "contrasts")
