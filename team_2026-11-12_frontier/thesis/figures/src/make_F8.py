"""F8: timeline of the project's beliefs, 7 Oct to 21 Nov 2026 (rows in date order, not to scale).
Sources (OUTLINE section 4): handbook 11 (H11) l514 to l520 timeline table and claim rows; THESIS_TABLES.md T17 (E1
openings), T21 (legacy-split rows), T2, T6, T7a, T8; log.md l224, l291. Each event's key text is asserted to occur in its
source file. No sealed data read.
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figB_common as C  # noqa: E402

NAME = "F8"
H11 = Path("/home/yugma/mtp/research/handbook/11_results_synthesis_and_claims.md")
TT = C.T / "thesis" / "THESIS_TABLES.md"
LOG = C.T / "log.md"
LANES = {"legacy": ("legacy split: SSL and recipe work", C.OI["sky"], "o"),
         "e1": ("registered E1 openings", C.OI["vermillion"], "D"),
         "proto": ("benchmark protocol (P532, cv5v3)", C.OI["green"], "s")}
# (date, lane, belief or question, what the evidence said, source file, source pointer, snippet that must occur)
EV = [
    ("7 to 8 Oct", "legacy", "the training pipeline may have bugs",
     "P1: the pipeline is exact; blur and rotation on 1 to 2 px labels destroy crack fitting",
     H11, "l515", "P1: the pipeline is exact"),
    ("10 Oct", "legacy", "SSL with tolerant pseudo-labels should help at 10% labels",
     "P7/P8: no loss passes at 10%", H11, "l516", "P7/P8: no loss passes at 10%"),
    ("11 Oct", "legacy", "more unlabelled data or fewer labels shows the effect",
     "P9: a 28x pool does not amplify; P10: no gain at 5%", H11, "l517", "P9: a 28× pool does not amplify"),
    ("11 Oct", "legacy", "tolerance may fix human label noise",
     "P14: tolerance recovers 0% of the label-noise gap; P13: with separate BN, SSL beats supervised at 5%",
     H11, "l520", "P14: tolerance recovers 0% of the label-noise gap"),
    ("12 Oct", "legacy", "SSL helps at higher label fractions",
     "P16: n.d. at 20%, 50%, 100%", TT, "T21 P16 row", "n.d. at 20%, 50%, 100%"),
    ("23 Oct", "legacy", "ALHVR(-EL) helps rare EL defects",
     "AL1: WORSE on all three primaries in all four cell sets", H11, "row 17 (l90)", "**WORSE** on all three primaries"),
    ("30 Oct", "legacy", "a 5-seed ensemble beats one model (Track M)",
     "FINAL - single +0.018 [+0.013, +0.025] crack IoU: supported", TT, "T21 Track M row", "+0.018 [+0.013, +0.025]"),
    ("30 Oct", "legacy", "the house fine-tune keeps the encoder",
     "encoder audit: cosine to init layer3 0.005 to 0.018, layer4 -0.001 to 0.001: erased", TT, "T21 encoder audit row",
     "layer3 0.005 to 0.018, layer4 −0.001 to 0.001"),
    ("1 Nov", "e1", "PF raises E1 inactive IoU (opening #1)",
     "+0.189 BETTER (replicated); crack recall n.d.", TT, "T17 #1", "E1 inactive IoU +0.189 BETTER (replicated)"),
    ("1 Nov", "e1", "Skeleton Recall improves crack (opening #2)",
     "E1 +0.059 BETTER but test crack IoU WORSE: FAIL", TT, "T17 #2", "SKR FAIL (test crack IoU WORSE)"),
    ("2 Nov", "e1", "synthetic half-cuts help (#3); SKR2 at w 0.1 (#5)",
     "HC n.d.; SKR2 PASS by 0.0013 (E1 +0.0364, thr 0.0351); SKR2E ensembles FAIL (#6)", TT, "T17 #3, #5, #6",
     "SKR2 PASS (E1 crack relF1@2 +0.0364, thr 0.0351, BETTER)"),
    ("14 Nov", "e1", "the SKR E1 gain replicates on fresh seeds (#7)",
     "REPLICATED does not hold (seed-aware CI [-0.0015, +0.0590])", TT, "T17 #7", "REPLICATED does not hold"),
    ("15 Nov", "proto", "cv5v2 keeps modules within one fold",
     "24 physical modules span two folds (91 cells); cv5v3: 285 groups, none spans folds", TT, "T1, T2; date cv5v3.json created",
     "24 physical modules span two folds; 91 pool cells"),
    ("16 to 18 Nov", "proto", "HRNet, SWAD or both beat PF (5-seed rows)",
     "HRNET +0.0104, SWADBN +0.0070, COMBO +0.0154: all NOT CONFIRMED", TT, "T6; dates H11 l25",
     "| HRNET - PF | +0.0104 [+0.0012, +0.0203]"),
    ("21 Nov 00:22", "proto", "strict crack IoU can decide",
     "ruling: relF1@2 decides; strict IoU only with its convention band", LOG, "l224", "**\"relF1@2 decides\"**"),
    ("21 Nov 08:00", "proto", "D4 TTA helps PF on cv5v3",
     "PF_D4 - PF +0.0134 [+0.0066, +0.0207] CONFIRMED", TT, "T7a; time FINAL_TTA_READ.md l5", "+0.0134 [+0.0066, +0.0207]"),
    ("21 Nov 12:06", "e1", "the C2 recipe beats PF on unseen modules (#8)",
     "+0.0430 [+0.0013, +0.1043] CONFIRMED (OP-A; 101 of 106 cells CSIR; full cells carry it)", TT, "T17 #8, T8",
     "CONFIRMED; Delta +0.0430 [+0.0013, +0.1043]"),
    ("21 Nov 14:38", "proto", "E1 stays a zero-shot set",
     "decision: run T3b; E1 becomes training data for T3b models after opening #9", LOG, "l291",
     "E1 becomes training data for T3b models"),
]


def main():
    C.set_fig(NAME)
    lines = {f: open(f).read().splitlines() for f in (H11, TT, LOG)}
    for d, lane, b, e, f, ptr, snip in EV:
        txt = "\n".join(lines[f])
        assert snip in txt, (d, f.name, snip)
    assert "P1: the pipeline is exact" in lines[H11][514] and "P14: tolerance recovers" in lines[H11][519]
    assert "relF1@2 decides" in lines[LOG][223] and "E1 becomes training data" in lines[LOG][290]
    plt = C.rcparams()
    from matplotlib.lines import Line2D
    n = len(EV)
    fig, ax = plt.subplots(figsize=(7.0, 0.36 * n + 0.6))
    ax.set_xlim(0, 100); ax.set_ylim(n - 0.4, -0.9); ax.axis("off")
    xl = {"legacy": 14.5, "e1": 17.0, "proto": 19.5}
    for lane, x in xl.items():
        ax.plot([x, x], [-0.3, n - 0.6], color=LANES[lane][1], lw=0.6, alpha=0.5, zorder=0)
    prev = None
    for i, (d, lane, b, e, f, ptr, snip) in enumerate(EV):
        name, col, mk = LANES[lane]
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="#F4F4F4", zorder=-1, lw=0)
        ax.text(0.5, i, d if d != prev else "", va="center", fontsize=C.fs(6.2), weight="bold")
        prev = d
        ax.scatter([xl[lane]], [i], s=22, marker=mk, color=col, zorder=3, edgecolor="black", lw=0.4)
        ax.text(22.5, i, textwrap.fill(b, 36), va="center", fontsize=C.fs(5.9), linespacing=1.15)
        ax.text(57.0, i, textwrap.fill(e, 50), va="center", fontsize=C.fs(5.6), color="#222222", linespacing=1.15)
    ax.text(22.5, -0.75, "belief or question", fontsize=C.fs(6.4), weight="bold", va="center")
    ax.text(57.0, -0.75, "what the evidence said", fontsize=C.fs(6.4), weight="bold", va="center")
    ax.text(0.5, -0.75, "date (2026)", fontsize=C.fs(6.4), weight="bold", va="center")
    handles = [Line2D([], [], marker=v[2], color=v[1], markeredgecolor="black", markeredgewidth=0.4, ls="", label=v[0])
               for v in LANES.values()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=C.fs(6.2))
    C.save(fig, NAME)
    C.write_csv(NAME, ["row", "date", "lane", "belief_or_question", "evidence", "source_file", "source_pointer",
                       "verbatim_snippet_checked"],
                [[i, d, lane, b, e, str(f), ptr, snip] for i, (d, lane, b, e, f, ptr, snip) in enumerate(EV)])


if __name__ == "__main__":
    main()
