"""F9: protocol flow: 2-seed screen (cv5v2) -> 5-seed row (cv5v3) -> registered E1 opening. Rules from
benchmark/PROTOCOL_v0.2.md l7 to l19, l116 to l118 and thesis/THESIS_TABLES.md T4; outcomes from TT T6, T7a, T8, T16a.
Every number printed is asserted to occur in its source file. No sealed data read.
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figB_common as C  # noqa: E402

NAME = "F9"
TT = C.T / "thesis" / "THESIS_TABLES.md"
P02 = C.BENCH / "PROTOCOL_v0.2.md"

CHECKS = {TT: ["M = max(0.01, 2 x SE of the A/A contrast), per machine", "Screen = 2 seeds; table row = 5 seeds",
               "pass band 0.85 to 1.15 x the baseline's", "false crack px on crack-free cells against PF (max 1.5)",
               "allowed drop 0.0100", "relF1@2 0.0087 / 0.0071 / 0.0055 at 2 / 3 / 5 seeds",
               "the 71 clusters are drawn with replacement", "M = 0.010",
               "| HRNET - PF | +0.0104 [+0.0012, +0.0203]", "| SWADBN - PF (primary readout) | +0.0070 [-0.0007, +0.0156]",
               "| COMBO - PF (c3x HRNet + SWAD, swad_bn, primary) | +0.0154 [+0.0065, +0.0260]",
               "| CS_D4 - PF (the C2 recipe on CV5; selection-biased) | +0.0222 [+0.0138, +0.0308]",
               "+0.0134 [+0.0066, +0.0207]", "+0.0430 [+0.0013, +0.1043]", "285 groups, none spans folds",
               "330 physical-module groups", "106 cells, 71 image ids", "| segformer_mitb2_pf (SegFormer MiT-B2)",
               "| skr01_pf_v11 (Skeleton Recall loss)", "| rcs (rare-class sampling)", "+0.0102 [-0.0094, +0.0291]",
               "+0.0039 [-0.0027, +0.0115]", "-0.0135 [-0.0259, -0.0005]", "-0.0085 [-0.0187, -0.0004]",
               "101 of 106 cells CSIR"],
          P02: ["A screen pass is a promotion to a 5-seed confirmation, never a result",
                "It counts only if it holds at OP-A and at OP-W inside the width band, with delta at least M and the 95% interval above 0",
                "0 of 15 A/A splits would be promoted on any headline metric",
                "One registered opening near the end, at most 3 candidates"]}


def main():
    C.set_fig(NAME)
    for f, snips in CHECKS.items():
        txt = open(f).read()
        for s in snips:
            assert s in txt, (f.name, s)
    plt = C.rcparams()
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")
    EDGE = "#333333"
    STAGE = ["#DCEBF7", "#DCEBF7", "#FBE3D2"]

    def box(x, y, w, h, fc, title, body, ls="-", fs=5.1):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.8", fc=fc, ec=EDGE, lw=0.8, ls=ls))
        ax.text(x + 1, y + h - 0.9, title, ha="left", va="top", fontsize=C.fs(6.0), weight="bold")
        body = "\n".join(textwrap.fill(l, int(w * 1.3), subsequent_indent="  " if l.startswith("  ") else "")
                         for l in body.split("\n"))
        ax.text(x + 1, y + h - 3.9, body, ha="left", va="top", fontsize=C.fs(fs), linespacing=1.32)

    def arrow(x0, y0, x1, y1, txt=None, tx=0, ty=0):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, lw=0.9, color=EDGE))
        if txt:
            ax.text((x0 + x1) / 2 + tx, (y0 + y1) / 2 + ty, txt, fontsize=C.fs(5.6), ha="center", va="bottom", style="italic")

    box(0.5, 31, 31, 28.5, STAGE[0], "1. Screen: 2 seeds, cv5v2",
        "532 pool cells, 5 folds, 330 groups;\neach cell scored once out of fold\n"
        "crack relF1@2 decides at OP-A and\nOP-W (tolerance 2 px); strict IoU\ndecides nothing\n"
        "M = max(0.01, 2 x SE of the A/A\ncontrast), per machine; 0 of 15 A/A\nsplits would be promoted\n"
        "smallest detectable effect 0.0087\n(2 seeds)\na screen pass is a promotion, never\na result")
    box(34.5, 31, 31, 28.5, STAGE[1], "2. Row: 5 seeds, cv5v3",
        "corrected split: 285 groups, none\nspans folds; 532 and 416 clean cells\nboth read\n"
        "a gain counts only if delta >= M and\nthe 95% interval is above 0, at OP-A\nand OP-W\n"
        "guards: width 0.85 to 1.15 x PF\n(pooled and per source); false crack\npx <= 1.5 x PF on crack-free cells;\n"
        "mIoU-R13 drop <= 0.0100\nsmallest detectable effect 0.0055\n(5 seeds)")
    box(68.5, 31, 31, 28.5, STAGE[2], "3. Registered E1 opening",
        "candidates and rule frozen and\nreviewed before any sealed dump;\nat most 3 candidates\n"
        "106 cells, 71 image-id clusters;\nOP-A only\nseed-aware two-stage cluster\nbootstrap\n"
        "CONFIRMED: Delta >= M (0.010), lower\nend of the 95% interval > 0, guards\nG1 to G4\n"
        "test50: continuity table, decides\nnothing", ls="--")
    arrow(31.8, 45, 34.2, 45, "pass", 0, 0.6)
    arrow(65.8, 45, 68.2, 45, "freeze", 0, 0.6)
    box(0.5, 0.5, 31, 27, "#F2F2F2", "Closed at the screen",
        "e.g. SegFormer MiT-B2 (OP-W -0.0135),\nSkeleton Recall (+0.0039, n.d.),\nRCS (-0.0085), JML, encoder_spd,\n"
        "LA-CE, layered inactive head,\nper-source bias, DTI; EL-paper\nmodels below PF")
    box(34.5, 0.5, 31, 27, "#F2F2F2", "5-seed rows vs PF",
        "relF1@2 - PF, 532 cells, OP-A:\nHRNET +0.0104 [+0.0012, +0.0203]\n  NOT CONFIRMED (guards fail)\n"
        "SWADBN +0.0070 [-0.0007, +0.0156]\n  NOT CONFIRMED\nCOMBO +0.0154 [+0.0065, +0.0260]\n  NOT CONFIRMED (guards fail)\n"
        "PF_D4 +0.0134 [+0.0066, +0.0207]\n  CONFIRMED\nCS_D4 (C2 recipe) +0.0222\n  [+0.0138, +0.0308], passes its CV5\n"
        "  check (selection-biased)", fs=4.9)
    box(68.5, 0.5, 31, 27, "#F2F2F2", "E1 opening #8",
        "C2 - C1 crack relF1@2 +0.0430\n[+0.0013, +0.1043], guards pass:\nCONFIRMED; recipe, seeds 5 to 9;\n"
        "OP-A only; 101 of 106 cells CSIR;\nfull cells carry it\ntest50 #19: C2 - C1 +0.0102\n[-0.0094, +0.0291], context only")
    for x in (16, 50, 84):
        arrow(x, 30.7, x, 27.8)
    C.save(fig, NAME)
    rows = []
    for f, snips in CHECKS.items():
        for s in snips:
            rows.append([f.name, s])
    C.write_csv(NAME, ["source_file", "text_used_verbatim"], rows)


if __name__ == "__main__":
    main()
