"""F1: one P532 pool cell per source with the v1.1 crack and inactive overlay.

Selection rule (stated before looking at any image): per source, candidates = pool cells (cv5v3 pool, benchmark/cells.tsv)
with crack_px_v11 > 0 and inactive_px_v1 > 0 (inactive is unchanged in v1.1, LABELS_V11.md section 2); a source without
such a cell uses crack_px_v11 > 0 alone. Sort by (crack_px_v11, stem) and take the lower median, index (n - 1) // 2.
Lead ruling 23 Nov: cells flagged dup_image in cells.tsv (the release's one double annotation, CFVS_00015_r7_c4 =
CFVS_00016_r7_c4, same pixels, two masks) are removed from the candidates before the rule is applied.
"""
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import figB_common as C  # noqa: E402

NAME = "F1"
SOURCES = ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]


def select():
    pc = C.pool_cells()
    out = []
    for src in SOURCES:
        rows = [r for r in pc.values() if r["source"] == src]
        skipped = sorted(r["stem"] for r in rows if "dup_image" in r["flags"].split(";"))
        rows = [r for r in rows if "dup_image" not in r["flags"].split(";")]  # lead ruling 23 Nov: no double annotation
        both = [r for r in rows if int(r["crack_px_v11"]) > 0 and int(r["inactive_px_v1"]) > 0]
        cand, rule = (both, "crack and inactive") if both else ([r for r in rows if int(r["crack_px_v11"]) > 0], "crack only")
        cand.sort(key=lambda r: (int(r["crack_px_v11"]), r["stem"]))
        r = cand[(len(cand) - 1) // 2]
        out.append((src, r, rule, len(cand), len(rows), skipped))
    return out


def main():
    C.set_fig(NAME)
    plt = C.rcparams()
    from matplotlib.patches import Patch
    sel = select()
    fo = C.fold_of()
    fig, axes = plt.subplots(1, 5, figsize=(7.0, 1.75))
    rows = []
    for ax, (src, r, rule, n, nsrc, skipped) in zip(axes, sel):
        s = r["stem"]
        g, m = C.grey(s), C.mask_v11(s)
        keep = m != C.IGN
        cr, ia = (m == C.CRACK) & keep, (m == C.INACT) & keep
        ax.imshow(C.overlay(g, cr, ia), interpolation="none")
        ax.set_xticks([]); ax.set_yticks([])
        lab = s if len(s) <= 16 else s[:11] + "\n" + "\n".join(textwrap.wrap(s[11:], 14))
        ax.set_title(f"{src}\n{lab}", fontsize=C.fs(6.5))
        rows.append([NAME, src, s, fo[s], r["role"], r["cell_type"], int(cr.sum()), int(ia.sum()), int(r["crack_px_v11"]),
                     int(r["inactive_px_v1"]), rule, n, nsrc, ";".join(skipped), str(C.IMAGES / f"{s}.png"),
                     str(C.MASKS_V11 / f"{s}.png")])
        assert int(cr.sum()) == int(r["crack_px_v11"]), (s, int(cr.sum()), r["crack_px_v11"])
    fig.legend(handles=[Patch(color=C.COL_CRACK, label="crack (class 14), drawn 1 px dilated"),
                        Patch(color=C.COL_INACT, alpha=0.6, label="inactive (class 11), 45% tint")],
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(wspace=0.04)
    C.save(fig, NAME)
    C.write_csv(NAME, ["figure", "source", "stem", "cv5v3_fold", "legacy_role", "cell_type", "crack_px_mask", "inactive_px_mask",
                       "crack_px_v11_cells_tsv", "inactive_px_v1_cells_tsv", "candidate_rule", "n_candidates", "n_pool_cells_source",
                       "excluded_dup_image", "image_path", "mask_path"], rows)
    for r in rows:
        print(r[:12])


if __name__ == "__main__":
    main()
