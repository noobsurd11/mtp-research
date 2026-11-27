"""F7: label-error candidates of the dataset audit with the AI-rater verdicts (P532 pool cells only).

Sources: dataset_audit/rater/out/candidate_verdicts.tsv (124 candidates, 3 raters, majority; RESULT.md), v1.1 masks
(benchmark/out/masks_v11/masks), the audit's 25-model out-of-fold vote maps dataset_audit/cache/cons/<stem>.npz
(vc, vi = number of the 25 cv5v3 models PF, HOUSE, HRNET, SWADBN, C3X x seeds 5 to 9 that predict crack / inactive;
consensus = at least 13 of 25, the rater panels' rule, rater/scripts/rcommon.py CONS_T).
Window: the rater crop rule (rcommon.crop_window, copied): square around the candidate bbox, side = clip(extent + 48,
96, 288), shifted inside the 512 image.

Selection rule: for class crack and class inactive, and for each majority verdict label_error, model_error, ambiguous,
the candidate with the largest px; ties broken by candidate id. 6 examples.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import figB_common as C  # noqa: E402

NAME = "F7"
VERD = C.T / "dataset_audit" / "rater" / "out" / "candidate_verdicts.tsv"
CONS = C.T / "dataset_audit" / "cache" / "cons"
CONS_T = 13
TYPE = {"MC": "missed crack", "SC": "spurious crack", "MI": "missed inactive", "SI": "spurious inactive"}
VLAB = {"label_error": "label error", "model_error": "model error", "ambiguous": "ambiguous"}


def crop_window(bbox, size=512):  # verbatim rule of rater/scripts/rcommon.py
    y0, x0, y1, x1 = bbox
    ext = max(y1 - y0 + 1, x1 - x0 + 1)
    side = int(np.clip(ext + 48, 96, 288))
    cy, cx = (y0 + y1 + 1) / 2.0, (x0 + x1 + 1) / 2.0
    wy0 = int(round(cy - side / 2.0))
    wx0 = int(round(cx - side / 2.0))
    wy0 = min(max(wy0, 0), size - side)
    wx0 = min(max(wx0, 0), size - side)
    return wy0, wx0, side


def cons(stem):
    C.guard_stem(stem)
    p = CONS / f"{stem}.npz"
    C.guard_path(p)
    C.log_read("cons_npz", p)
    with np.load(p) as z:
        return z["vc"], z["vi"]


def main():
    C.set_fig(NAME)
    plt = C.rcparams()
    from matplotlib.patches import Patch, Rectangle
    rows = list(csv.DictReader(open(VERD), delimiter="\t"))
    picks = []
    for cls in ("crack", "inact"):
        for v in ("label_error", "model_error", "ambiguous"):
            c = [r for r in rows if r["cls"] == cls and r["majority"] == v]
            c.sort(key=lambda r: (-int(r["px"]), r["id"]))
            picks.append((cls, v, c[0], len(c)))
    fig = plt.figure(figsize=(7.0, 4.6))
    gs = fig.add_gridspec(3, 7, width_ratios=[1, 1, 1, 0.12, 1, 1, 1], wspace=0.04, hspace=0.42)
    data = []
    for j, (cls, v, r, n) in enumerate(picks):
        s = r["stem"]
        g, m = C.grey(s), C.mask_v11(s)
        keep = m != C.IGN
        vc, vi = cons(s)
        bb = [int(x) for x in r["bbox"].split(",")]
        wy, wx, side = crop_window(bb)
        sl = (slice(wy, wy + side), slice(wx, wx + side))
        lab = C.overlay(g, (m == C.CRACK) & keep, (m == C.INACT) & keep, crack_dilate=False)[sl]
        con = C.overlay(g, (vc >= CONS_T) & keep, (vi >= CONS_T) & keep, crack_dilate=False)[sl]
        row, col0 = j % 3, 4 * (j // 3)
        tiles = [(np.repeat(g[sl][..., None], 3, 2), "image"), (lab, "label v1.1"), (con, "25-model vote >= 13")]
        for t, (im, ttl) in enumerate(tiles):
            ax = fig.add_subplot(gs[row, col0 + t]); axs = locals().setdefault("axs", {}); axs[t] = ax
            ax.imshow(im, interpolation="none")
            ax.add_patch(Rectangle((bb[1] - wx - 0.5, bb[0] - wy - 0.5), bb[3] - bb[1] + 1, bb[2] - bb[0] + 1, fill=False,
                                   ec=C.COL_BOX, lw=0.9, ls="--"))
            ax.set_xticks([]); ax.set_yticks([])
            if row == 0:
                ax.set_title(ttl, fontsize=C.fs(6.3))
        votes = "/".join(r[k].replace("_error", "").replace("ambiguous", "amb") for k in ("r1", "r2", "r3"))
        axs[1].text(0.5, -0.03, f"{'crack' if cls == 'crack' else 'inactive'}, majority: {VLAB[v]} ({TYPE[r['type']]}, {r['px']} px)\n{s}; raters {votes}",
                    transform=axs[1].transAxes, ha="center", va="top", fontsize=C.fs(5.8))
        data.append([cls, v, n, r["id"], s, r["source"], C.fold_of()[s], r["type"], r["kind"], r["px"], r["bbox"], wy, wx, side,
                     r["r1"], r["r2"], r["r3"], r["majority"], r["label_is"], str(VERD), str(CONS / f"{s}.npz")])
    # no figure-level header text (lead ruling 23 Nov): left block = crack, right block = inactive, stated in the caption
    fig.legend(handles=[Patch(color=C.COL_CRACK, label="crack"),
                        Patch(color=C.COL_INACT, alpha=0.6, label="inactive, 45% tint"),
                        Patch(fill=False, ec=C.COL_BOX, ls="--", label="candidate region (bbox)")],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.subplots_adjust(top=0.95, bottom=0.08)
    C.save(fig, NAME)
    C.write_csv(NAME, ["class", "majority_verdict", "n_candidates_class_verdict", "candidate_id", "stem", "source",
                       "cv5v3_fold", "type", "kind", "px", "bbox_y0x0y1x1", "window_y0", "window_x0", "window_side", "r1", "r2",
                       "r3", "majority", "panel_label_is", "verdict_file", "vote_file"], data)
    for d in data:
        print(d[:12], d[14:18])


if __name__ == "__main__":
    main()
