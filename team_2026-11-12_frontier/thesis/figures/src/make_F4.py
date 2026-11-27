"""F4: schematic of the cell sets and splits. Counts copied from thesis/THESIS_TABLES.md T1 (and T2 for the cv5v2 leak),
plus the bench_set counts of benchmark/cells.tsv (CELLS_README.md 'Counts to check'), which this script re-counts and
asserts. No image, mask, label or prediction is read.
"""
import csv
import textwrap
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figB_common as C  # noqa: E402

NAME = "F4"
TT = C.T / "thesis" / "THESIS_TABLES.md"


def tt_check(snippets):
    txt = open(TT).read()
    for s in snippets:
        assert s in txt, f"not in THESIS_TABLES.md: {s}"


def main():
    C.set_fig(NAME)
    plt = C.rcparams()
    from matplotlib.patches import FancyBboxPatch, Rectangle
    # numbers used, each checked against its source text
    tt_check(["816 real labelled cells, 787 unique physical cells", "463 physical-module groups",
              "582 cells = 478 train / 54 val / 50 test", "ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17",
              "116 excluded, 416 left", "5 folds with held-out sizes 107 / 111 / 104 / 104 / 106", "330 physical-module groups",
              "Held-out sizes 107 / 110 / 103 / 101 / 111; 47 cells move", "285 groups, none spans folds",
              "106 cells, 71 image ids: 66 CSIR, 5 BMRK; 101 of 106 cells CSIR, 62 half-cut cells (the pool has none)",
              "50 cells, 48 image ids", "167 stems: legacy test 50 + ext117 117", "0 half-cut cells",
              "24 physical modules span two folds; 91 pool cells", "Counted openings (24 Oct to 21 Nov 2026): 19",
              "8 | OPENING_RULE.md (final)"])
    bs = {}
    for r in csv.DictReader(open(C.CELLS_TSV), delimiter="\t"):
        bs[r["bench_set"]] = bs.get(r["bench_set"], 0) + 1
    cnt = {"pool": sum(v for k, v in bs.items() if k.startswith("cv5v2")), "test50": bs["test50"], "e1": bs["e1_106"],
           "ext11": bs["aux_ext11"], "rf117": bs["aux_rf117"]}
    assert cnt == {"pool": 532, "test50": 50, "e1": 106, "ext11": 11, "rf117": 117} and sum(bs.values()) == 816, cnt

    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 62.5); ax.axis("off")
    POOL, SEAL, AUX, EDGE = "#DCEBF7", "#FBE3D2", "#EEEEEE", "#333333"

    def box(x, y, w, h, fc, text, fs=5.8, bold_first=True, ls="-"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.8", fc=fc, ec=EDGE, lw=0.8, ls=ls))
        lines = text.split("\n")
        ax.text(x + 1.0, y + h - 1.0, lines[0], ha="left", va="top", fontsize=C.fs(fs + 0.5), weight="bold" if bold_first else None)
        if len(lines) > 1:
            body = "\n".join(textwrap.fill(l, int(w * 1.08)) for l in lines[1:])
            ax.text(x + 1.0, y + h - 4.0, body, ha="left", va="top", fontsize=C.fs(fs), linespacing=1.35)

    box(1, 49, 98, 12.5, AUX, "Labelled corpus: 816 real cells (787 physical cells, 463 module groups)\n"
        "= P532 pool 532 + test50 50 + E1 106 + 11 cells new in release 20221008 + 117 E-SCDD cells (Hanifi labels)\n"
        "BenchmarkEL dataset_20211104 = 582 cells = 478 train / 54 val / 50 test, 24 classes (pool and test50 come from it)")
    box(1, 1, 60, 45, POOL, "Development pool P532 = legacy train 478 + val 54\n"
        "ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17; 0 half-cut cells\n"
        "every pool cell is scored once out of fold;\nfull-pool training of C1 and C2 uses all 532")
    # fold bars
    def foldbar(y, sizes, label, note, moved=None):
        x0, W = 4, 54
        tot = sum(sizes)
        ax.text(x0, y + 5.0, label, fontsize=C.fs(6.0), weight="bold", va="bottom")
        ax.text(x0, y - 1.0, note, fontsize=C.fs(5.6), va="top")
        x = x0
        cols = ["#FFFFFF", "#C6DBEF", "#FFFFFF", "#C6DBEF", "#FFFFFF"]
        for k, n in enumerate(sizes):
            w = W * n / tot
            ax.add_patch(Rectangle((x, y), w, 4.2, fc=cols[k], ec=EDGE, lw=0.7))
            ax.text(x + w / 2, y + 2.1, f"f{k}: {n}", ha="center", va="center", fontsize=C.fs(5.8))
            x += w
    foldbar(27, [107, 111, 104, 104, 106], "cv5v2 (2-seed screens): 5 folds, 330 module groups",
            "module leak found later: 24 physical modules span two folds\n(91 pool cells)")
    foldbar(11, [107, 110, 103, 101, 111], "cv5v3 (corrected split; 5-seed rows, CV5 TTA read)\n285 module groups, none spans folds",
            "47 cells moved from cv5v2; 416 clean cells (116 excluded)\nare read beside all 532")
    ax.text(4, 2.6, "bars: held-out fold sizes; for fold fK the other four folds train", fontsize=C.fs(5.4), style="italic")
    box(64, 27.5, 35, 19.5, SEAL, "E1 (sealed): unseen modules\n106 cells, 71 image ids (clusters)\n"
        "image ids: 66 CSIR, 5 BMRK\ncells: 101 CSIR, 5 BMRK\n62 half-cut cells (the pool has none)\n"
        "registered openings #1 to #8;\n#8 = the final read", ls="--")
    box(64, 14, 35, 12, SEAL, "test50 (sealed): legacy test\n50 cells, 48 image ids\ncontinuity only, decides nothing\n"
        "19 counted openings\n(24 Oct to 21 Nov 2026)", ls="--")
    box(64, 0.5, 35, 12, AUX, "Forbidden stems: 167\n= legacy test 50 + ext117 117\n(ext117 = E1 106 + the 11 cells new in 20221008)\n"
        "no training list may contain them")
    C.save(fig, NAME)
    rows = [["corpus_cells", 816, "TT T1"], ["physical_cells", 787, "TT T1"], ["module_groups_corpus", 463, "TT T1"],
            ["dataset_20211104", "582 = 478/54/50", "TT T1"], ["pool_P532", 532, "TT T1; cells.tsv bench_set cv5v2:f0..f4"],
            ["pool_by_source", "ARTS 182, BMRK 50, CFVS 169, CSIR 114, SDLE 17", "TT T1"],
            ["cv5v2_heldout", "107/111/104/104/106", "TT T1"], ["cv5v2_groups", 330, "TT T1"],
            ["cv5v2_leak", "24 modules, 91 pool cells", "TT T2"], ["cv5v3_heldout", "107/110/103/101/111", "TT T1"],
            ["cv5v3_groups", 285, "TT T1"], ["cv5v3_moved", 47, "TT T1"], ["clean_cells", "416 (116 excluded)", "TT T1"],
            ["E1", "106 cells, 71 image ids, 66 CSIR / 5 BMRK ids, 101 CSIR cells, 62 half-cut", "TT T1"],
            ["E1_openings", "#1 to #8", "TT T17"], ["test50", "50 cells, 48 image ids", "TT T1"],
            ["test50_openings", 19, "TT T1"], ["forbidden", "167 = 50 + 117", "TT T1; cv5v3.json forbidden"],
            ["aux_ext11", 11, "cells.tsv bench_set"], ["aux_rf117", 117, "cells.tsv bench_set"]]
    C.write_csv(NAME, ["item", "value", "source"], rows)


if __name__ == "__main__":
    main()
