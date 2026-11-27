"""F3: the images are about 3 x 3 cell windows; most labelled crack / inactive px lie outside the centre cell.

Panels a to c: one P532 pool cell per windowed source (ARTS, CFVS, CSIR) with the v1.1 overlay and the centre cell drawn by
the audit's rule (central_rect, copied verbatim from dataset_audit/scripts/labels_audit.py, md5 f0214464).
Panel d: share of v1.1 crack and inactive px outside the centre cell, per source and pooled, copied from
dataset_audit/out/labels_audit.txt section b5 (= REPORT.md F3).

Selection rule: per source, candidates = pool cells in dataset_audit/out/labels_percell.tsv with gaps_found True and
v1.1 crack px (crack_n) >= 200; pick the cell whose crack share outside the centre cell (crack_out / crack_n) is closest to
the source's pooled share in labels_audit.txt b5 (ARTS 0.678, CFVS 0.624, CSIR 0.721); ties broken by stem.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import figB_common as C  # noqa: E402

NAME = "F3"
PERCELL = C.T / "dataset_audit" / "out" / "labels_percell.tsv"
B5 = C.T / "dataset_audit" / "out" / "labels_audit.txt"
SPACING = (1, 2, 3)
PAD = 7


def central_rect(gt):  # verbatim from labels_audit.py
    sp = np.isin(gt, SPACING)
    nonpad = gt != PAD
    ys, xs = np.nonzero(nonpad)
    if not len(ys):
        return (0, 511, 0, 511), False
    py0, py1, px0, px1 = ys.min(), ys.max(), xs.min(), xs.max()
    rowf = sp.sum(1) / np.maximum(nonpad.sum(1), 1)
    colf = sp.sum(0) / np.maximum(nonpad.sum(0), 1)
    gr = np.nonzero(rowf > 0.2)[0]
    gc = np.nonzero(colf > 0.2)[0]
    c = 256
    y0 = max([y for y in gr if y < c - 20], default=py0)
    y1 = min([y for y in gr if y > c + 20], default=py1)
    x0 = max([x for x in gc if x < c - 20], default=px0)
    x1 = min([x for x in gc if x > c + 20], default=px1)
    return (int(y0), int(y1), int(x0), int(x1)), bool(len(gr) or len(gc))


def read_b5():
    """{source: (crack_out, crack_all, inact_out, inact_all)} from labels_audit.txt b5."""
    out, on = {}, False
    for line in open(B5):
        if line.startswith("## b5."):
            on = True; continue
        if on and line.startswith("## "):
            break
        if on and " | " in line and not line.startswith("source"):
            f = [x.strip() for x in line.split("|")]
            co, ca = f[4].split(" (")[0].split(" of ")
            io, ia = f[5].split(" (")[0].split(" of ")
            out[f[0]] = (int(co), int(ca), int(io), int(ia))
    return out


def main():
    C.set_fig(NAME)
    plt = C.rcparams()
    from matplotlib.patches import Patch, Rectangle
    b5 = read_b5()
    target = {s: round(b5[s][0] / b5[s][1], 3) for s in ("ARTS", "CFVS", "CSIR")}
    assert target == {"ARTS": 0.678, "CFVS": 0.624, "CSIR": 0.721}, target
    rows = list(csv.DictReader(open(PERCELL), delimiter="\t"))
    P = C.pool()
    picks = []
    for src in ("ARTS", "CFVS", "CSIR"):
        cand = [r for r in rows if r["src"] == src and r["gaps_found"] == "True" and int(r["crack_n"]) >= 200]
        for r in cand:
            assert r["stem"] in P
        cand.sort(key=lambda r: (abs(int(r["crack_out"]) / int(r["crack_n"]) - target[src]), r["stem"]))
        picks.append((src, cand[0], len(cand)))
    fig = plt.figure(figsize=(7.0, 2.05))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.25], wspace=0.06)
    data = []
    for i, (src, r, n) in enumerate(picks):
        s = r["stem"]
        g, m = C.grey(s), C.mask_v11(s)
        keep = m != C.IGN
        cr, ia = (m == C.CRACK) & keep, (m == C.INACT) & keep
        (y0, y1, x0, x1), ok = central_rect(m)
        inside = np.zeros_like(cr); inside[y0:y1 + 1, x0:x1 + 1] = True
        co, io = int((cr & ~inside).sum()), int((ia & ~inside).sum())
        assert co == int(r["crack_out"]) and int(cr.sum()) == int(r["crack_n"]), (s, co, r["crack_out"])
        ax = fig.add_subplot(gs[0, i])
        ax.imshow(C.overlay(g, cr, ia), interpolation="none")
        ax.add_patch(Rectangle((x0 - 0.5, y0 - 0.5), x1 - x0 + 1, y1 - y0 + 1, fill=False, ec=C.COL_BOX, lw=1.2, ls="--"))
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"({'abc'[i]}) {src}\n{s}\ncrack px outside\n{co} of {int(cr.sum())}", fontsize=C.fs(6.3))
        data.append(["cell", src, s, C.fold_of()[s], y0, y1, x0, x1, co, int(cr.sum()), io, int(ia.sum()),
                     f"{co / max(int(cr.sum()), 1):.3f}", n, str(C.IMAGES / f"{s}.png"), str(C.MASKS_V11 / f"{s}.png")])
    ax = fig.add_subplot(gs[0, 3])
    srcs = ["ARTS", "CFVS", "CSIR", "ALL"]
    x = np.arange(len(srcs))
    cs = [b5[s][0] / b5[s][1] for s in srcs]
    ins = [b5[s][2] / b5[s][3] for s in srcs]
    ax.bar(x - 0.19, cs, 0.36, color=C.COL_CRACK, label="crack px")
    ax.bar(x + 0.19, ins, 0.36, color=C.COL_INACT, label="inactive px")
    for xi, a, b in zip(x, cs, ins):
        ax.text(xi - 0.19, a + 0.015, f"{a:.2f}", ha="center", fontsize=C.fs(5.5))
        ax.text(xi + 0.19, b + 0.015, f"{b:.2f}", ha="center", fontsize=C.fs(5.5))
    ax.set_xticks(x, srcs)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("share outside the centre cell", fontsize=C.fs(6.5))
    ax.yaxis.set_label_position("right"); ax.yaxis.tick_right()
    ax.set_title("(d) v1.1 px outside the centre cell\n(all 532 pool cells)", fontsize=C.fs(6.3))
    ax.tick_params(labelsize=C.fs(6.5))
    for s in srcs:
        data.append(["share", s, "", "", "", "", "", "", b5[s][0], b5[s][1], b5[s][2], b5[s][3], f"{b5[s][0] / b5[s][1]:.3f}",
                     "", str(B5), ""])
    fig.legend(handles=[Patch(color=C.COL_CRACK, label="crack, drawn 1 px dilated"),
                        Patch(color=C.COL_INACT, alpha=0.6, label="inactive, 45% tint"),
                        Patch(fill=False, ec=C.COL_BOX, ls="--", label="centre cell (audit rule)")],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.42, -0.07))
    C.save(fig, NAME)
    C.write_csv(NAME, ["row", "source", "stem", "cv5v3_fold", "centre_y0", "centre_y1", "centre_x0", "centre_x1",
                       "crack_px_outside", "crack_px_all", "inactive_px_outside", "inactive_px_all", "crack_share_outside",
                       "n_candidates", "source_file", "mask_path"], data)
    for d in data:
        print(d[:14])


if __name__ == "__main__":
    main()
