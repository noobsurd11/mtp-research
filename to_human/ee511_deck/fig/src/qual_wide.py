"""Landscape (16:9 friendly) versions of Q2 and Q3: same cells, rule and scores as qual_make.py v2; layout only.
2 x 2 grid of examples (row-major), each example = Image | Ground truth | model A | model B. CPU only; writes to out/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import qual_make as Q  # noqa: E402

FOOT = "E1 illustration after the registered read; decides nothing."
CAPFONT = "Liberation Sans Narrow"   # score lines: the full "relF1@2 x.xx (mean x.xx)" fits one panel width at ~16 pt


def figure_wide(examples, titles, path, footer=FOOT, note=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    W, lm, g, G = 16.0, 0.06, 0.05, 0.42
    pw = (W - 2 * lm - 6 * g - G) / 8
    t_fs, s_fs, h_fs, c_fs = 19, 15, 18, 17
    caps = [c for ex in examples for _, c in ex["panels"] if c]
    import matplotlib.font_manager as fm
    from matplotlib.textpath import TextPath
    fp = fm.FontProperties(family=CAPFONT)
    while c_fs > 9:   # largest size at which the longest score line fits inside one panel (0.06 in margin)
        wmax = max(TextPath((0, 0), c, size=c_fs, prop=fp).get_extents().width for c in caps) / 72
        if wmax <= pw - 0.06:
            break
        c_fs -= 0.5
    print("score line font", CAPFONT, c_fs, "pt")
    top = 0.12 + t_fs / 72 * 1.2 + s_fs / 72 * 1.3 + 0.12
    hh, ch, rg = h_fs / 72 * 1.7, c_fs / 72 * 1.5 + 0.06, 0.4
    leg, foot = 0.75, 0.5
    H = top + 2 * (hh + pw + ch) + rg + leg + foot
    fig = plt.figure(figsize=(W, H), dpi=150, facecolor="white")

    def x0(col, j):
        return lm + col * (4 * pw + 3 * g + G) + j * (pw + g)

    for col in range(2):
        for j, (t, sub) in enumerate(titles):
            cx = (x0(col, j) + pw / 2) / W
            fig.text(cx, 1 - 0.1 / H, t, ha="center", va="top", fontsize=t_fs, fontweight="bold")
            if sub:
                fig.text(cx, 1 - (0.1 + t_fs / 72 * 1.2) / H, sub, ha="center", va="top", fontsize=s_fs)
    for i, ex in enumerate(examples):
        r, col = divmod(i, 2)
        ytop = H - top - r * (hh + pw + ch + rg)
        gx = (x0(col, 0) + x0(col, 3) + pw) / 2 / W
        fig.text(gx, (ytop - 0.02) / H, ex["header"], ha="center", va="top", fontsize=h_fs, fontweight="bold",
                 color="#222222")
        y = ytop - hh - pw
        for j, (im, cap) in enumerate(ex["panels"]):
            ax = fig.add_axes([x0(col, j) / W, y / H, pw / W, pw / H])
            ax.imshow(im, interpolation="antialiased")
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color("#8c8c8c"); sp.set_linewidth(0.8)
            if cap:
                fig.text((x0(col, j) + pw / 2) / W, (y - 0.06) / H, cap, ha="center", va="top", fontsize=c_fs,
                         fontfamily=CAPFONT)
    fig.legend(handles=[Patch(color=Q.COL_CRACK / 255, label="crack (class 14)"),
                        Patch(color=Q.COL_INACT / 255, alpha=0.6, label="inactive area (class 11)"),
                        Patch(facecolor=(Q.PADV / 255,) * 3, edgecolor="#8c8c8c", label="padding (outside the cell)")],
               loc="lower center", ncol=3, frameon=False, fontsize=19, bbox_to_anchor=(0.5, (foot + 0.02) / H),
               handlelength=1.6, handleheight=1.0, columnspacing=2.5)
    fig.text(0.5, 0.14 / H, (note + "   " if note else "") + footer, ha="center", va="bottom", fontsize=15,
             color="#444444", style="italic")
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)


def kind_of(t):
    return "half-cut + scuff" if t["hard"] else t["kind"]


def main():
    # Q2
    picks, n, pooled = Q.q2_select()
    exs = []
    for lab, t in picks:
        s = t["stem"]
        gt, keep = Q.e1_gt(s)
        g = Q.padg(Q.grey(Q.E1 / "images" / f"{s}.png"), gt)
        c1 = np.load(Q.c1_dump(s))["pred"]
        c2 = np.load(Q.c2_dump(s))["pred"]
        assert abs(Q.f1(Q.rel2(c1, gt, keep)) - t["c1s5"]) < 1e-9 and abs(Q.f1(Q.rel2(c2, gt, keep)) - t["c2s5"]) < 1e-9
        exs.append(dict(header=f"{Q.src_of(s)} {kind_of(t)} cell, {lab}",
                        panels=[(np.repeat(g[..., None], 3, 2), ""), (Q.ov(g, gt, keep), ""),
                                (Q.ov(g, c1, keep), f"relF1@2 {t['c1s5']:.2f} (mean {t['c1']:.2f})"),
                                (Q.ov(g, c2, keep), f"relF1@2 {t['c2s5']:.2f} (mean {t['c2']:.2f})")]))
        print("Q2", lab, s)
    figure_wide(exs, [("Image", ""), ("Ground truth", ""), ("Baseline", "PF (C1)"), ("Final", "HRNet+SWAD+D4")],
                Q.OUT / "qual_e1_final_wide.png", note="Maps: seed 5; mean over seeds 5 to 9.")
    # Q3
    picks, n, pooled = Q.q3_select()
    fold = Q.t3b_fold()
    exs = []
    for lab, t in picks:
        s = t["stem"]
        gt, keep = Q.e1_gt(s)
        g = Q.padg(Q.grey(Q.E1 / "images" / f"{s}.png"), gt)
        zs = np.load(Q.c2_dump(s))["pred"]
        al = np.load(Q.all_dump(s, fold[s]))["pred"]
        Q.oof_check(s, fold[s])
        assert abs(Q.f1(Q.rel2(zs, gt, keep)) - t["zss5"]) < 1e-9 and abs(Q.f1(Q.rel2(al, gt, keep)) - t["als5"]) < 1e-9
        exs.append(dict(header=f"{Q.src_of(s)} {kind_of(t)} cell, {lab}",
                        panels=[(np.repeat(g[..., None], 3, 2), ""), (Q.ov(g, gt, keep), ""),
                                (Q.ov(g, zs, keep), f"relF1@2 {t['zss5']:.2f} (mean {t['zs']:.2f})"),
                                (Q.ov(g, al, keep), f"relF1@2 {t['als5']:.2f} (mean {t['al']:.2f})")]))
        print("Q3", lab, s)
    figure_wide(exs, [("Image", ""), ("Ground truth", ""), ("Zero-shot", "final model C2"), ("Few-shot", "fine-tuned on E1")],
                Q.OUT / "qual_e1_fewshot_wide.png", note="Maps: seed 5; mean over seeds 5 to 7; few-shot out-of-fold.")
    print("DONE")


if __name__ == "__main__":
    main()
