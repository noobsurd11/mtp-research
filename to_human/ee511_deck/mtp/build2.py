#!/usr/bin/env python3
"""MTP final deck v2, in the mid-sem deck's style (to_human/build_midterm_deck.py: Archivo Black / Inter,
panel #142B29, accent #2A7F78, booktabs tables). Builds deck2.html from deck2_src.html.
Every number is copied from the file named in the comment (paths relative to to_human/ee511_deck/guide_ctx
or ~/mtp/research). Architecture figures are crops of the original papers' figures (arXiv 1505.04597 Fig. 1,
1807.10165 Fig. 1a, 1802.02611 Fig. 2, 1908.07919 Fig. 2), credited on the slide."""
import html, pathlib

HERE = pathlib.Path(__file__).parent
INK, MUTED, GRID = "#111111", "#5E6665", "#E2E6E5"
ACCENT, RED, GREY, AMBER = "#2A7F78", "#B03A2E", "#9AA3A2", "#C77A32"
FONT = "font-family:Inter,sans-serif"


def esc(s):
    return html.escape(str(s))


def T(x, y, s, size=15, anchor="start", color=INK, weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
            f'font-weight="{weight}" {extra}>{esc(s)}</text>')


def L(x1, y1, x2, y2, col=INK, sw=1.2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"{d}/>'


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="{FONT}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def axes_frame(o, Lm, TOP, W, H, Rm, B):
    o.append(L(Lm, H - B, W - Rm, H - B, INK, 1))
    o.append(L(Lm, TOP, Lm, H - B, INK, 1))


# ---------- SSL label-fraction plot (results/p13/README.md l20-27; results/p16/README.md l36-43) ----------
def ssl_plot():
    fr = ["5%", "20%", "50%", "100%"]
    sl = [(0.253, 0.037), (0.361, 0.037), (0.412, 0.012), (0.436, 0.013)]
    ss = [(0.370, 0.026), (0.390, 0.026), (0.418, 0.027), (0.439, 0.017)]
    W, H, Lm, Rm, TOP, B = 600, 400, 70, 20, 20, 62
    y0, y1 = 0.20, 0.48
    X = lambda i: Lm + 45 + i * (W - Lm - Rm - 90) / 3
    Y = lambda v: TOP + (y1 - v) / (y1 - y0) * (H - TOP - B)
    o = []
    for v in [0.20, 0.30, 0.40]:
        o.append(L(Lm, Y(v), W - Rm, Y(v), GRID, 1))
        o.append(T(Lm - 8, Y(v) + 5, f"{v:.2f}", 13, "end", MUTED))
    axes_frame(o, Lm, TOP, W, H, Rm, B)
    for i, f in enumerate(fr):
        o.append(T(X(i), H - B + 22, f, 14, "middle"))
    o.append(T(Lm + (W - Lm - Rm) / 2, H - 10, "labelled share of the training set", 14, "middle", MUTED))
    o.append(T(16, TOP + (H - TOP - B) / 2, "inactive IoU (test50)", 14, "middle", MUTED,
               extra=f'transform="rotate(-90 16 {TOP + (H - TOP - B) / 2:.1f})"'))
    for data, col, dx, mk in [(sl, GREY, -6, "s"), (ss, ACCENT, 6, "c")]:
        pts = " ".join(f"{X(i)+dx:.1f},{Y(m):.1f}" for i, (m, s) in enumerate(data))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2"/>')
        for i, (m, s) in enumerate(data):
            o.append(L(X(i) + dx, Y(m - s), X(i) + dx, Y(m + s), col, 1.5))
            if mk == "c":
                o.append(f'<circle cx="{X(i)+dx:.1f}" cy="{Y(m):.1f}" r="5" fill="{col}"/>')
            else:
                o.append(f'<rect x="{X(i)+dx-4.5:.1f}" y="{Y(m)-4.5:.1f}" width="9" height="9" fill="{col}"/>')
    o.append(f'<circle cx="{W-232}" cy="{H-B-44}" r="5" fill="{ACCENT}"/>' + T(W - 220, H - B - 39, "semi-supervised (Mean Teacher)", 13))
    o.append(f'<rect x="{W-236.5}" y="{H-B-26.5}" width="9" height="9" fill="{GREY}"/>' + T(W - 220, H - B - 17, "supervised only", 13))
    return svg(W, H, "".join(o))


# ---------- precision vs recall, 2-seed screens (THESIS_TABLES.md T15, training-machine rows; cv5v2, argmax) ----------
def pr_scatter():
    pts = [
        ("U-Net++ baseline (PF)", 0.894, 0.799, INK, True, -10, 20, "end"),
        ("HRNet-W18 + U-Net++", 0.902, 0.814, ACCENT, True, 10, -8, "start"),
        ("plain fine-tune", 0.897, 0.807, GREY, False, 0, 0, ""),
        ("U-Net R34", 0.896, 0.795, GREY, False, 0, 0, ""),
        ("U-Net VGG-16", 0.882, 0.798, GREY, False, 0, 0, ""),
        ("DeepLabV3+ R34", 0.884, 0.791, GREY, False, 0, 0, ""),
        ("Skeleton Recall", 0.884, 0.815, GREY, False, 0, 0, ""),
        ("SegFormer", 0.877, 0.809, GREY, False, 0, 0, ""),
        ("DeepLabV3 R50, stride 8 (UCF-EL)", 0.809, 0.729, RED, True, 10, 5, "start"),
        ("DeepLabV3+, Pratt's weighted CE", 0.648, 0.892, RED, True, -10, -10, "end"),
    ]
    W, H, Lm, Rm, TOP, B = 640, 430, 70, 20, 16, 58
    x0, x1, y0, y1 = 0.70, 0.92, 0.60, 0.95
    X = lambda r: Lm + (r - x0) / (x1 - x0) * (W - Lm - Rm)
    Y = lambda p: TOP + (y1 - p) / (y1 - y0) * (H - TOP - B)
    o = []
    for v in [0.75, 0.80, 0.85, 0.90]:
        o.append(L(X(v), TOP, X(v), H - B, GRID, 1))
    for v in [0.70, 0.80, 0.90]:
        o.append(L(Lm, Y(v), W - Rm, Y(v), GRID, 1))
    for v in [0.70, 0.75, 0.80, 0.85, 0.90]:
        o.append(T(X(v), H - B + 20, f"{v:.2f}", 13, "middle", MUTED))
    for v in [0.60, 0.70, 0.80, 0.90]:
        o.append(T(Lm - 8, Y(v) + 5, f"{v:.2f}", 13, "end", MUTED))
    axes_frame(o, Lm, TOP, W, H, Rm, B)
    for F in [0.75, 0.80, 0.85]:
        seg, r = [], x0
        while r <= x1 + 1e-9:
            p = F * r / (2 * r - F)
            if y0 <= p <= y1:
                seg.append(f"{X(r):.1f},{Y(p):.1f}")
            r += 0.002
        o.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="#B5BDBC" stroke-width="1" stroke-dasharray="3 3"/>')
        rl = 0.905
        o.append(T(X(rl) + 3, Y(F * rl / (2 * rl - F)) - 5, f"F1 = {F:.2f}", 11, "start", MUTED))
    for lab, p, r, col, show, dx, dy, anc in pts:
        o.append(f'<circle cx="{X(r):.1f}" cy="{Y(p):.1f}" r="{5.5 if show else 4}" fill="{col}"/>')
        if show:
            o.append(T(X(r) + dx, Y(p) + dy, lab, 13, anc, col, 600))
    o.append(T(Lm + (W - Lm - Rm) / 2, H - 10, "crack recall, relR@2", 14, "middle", MUTED))
    o.append(T(16, TOP + (H - TOP - B) / 2, "crack precision, relP@2", 14, "middle", MUTED,
               extra=f'transform="rotate(-90 16 {TOP + (H - TOP - B) / 2:.1f})"'))
    o.append(f'<circle cx="{X(0.712):.1f}" cy="{Y(0.622):.1f}" r="4" fill="{GREY}"/>' +
             T(X(0.712) + 10, Y(0.622) + 4, "other screened models", 12, "start", MUTED))
    return svg(W, H, "".join(o))


# ---------- all experiments: four columns, marker colour = outcome ----------
OUT = {"ok": (ACCENT, "helped / confirmed"), "part": (AMBER, "gain, guard failed or narrow"),
       "nd": (GREY, "not detectable"), "bad": (RED, "worse / failed"), "x": ("#D3D8D7", "invalid / stopped")}
EXP = [
    ("Semi-supervised", "7 to 23 Oct · test50, context only", [
        ("x", "first Mean Teacher + SemiCE (bug)"),
        ("nd", "attention gate (SA U-Net++)"),
        ("ok", "Mean Teacher, 5 and 10% labels"),
        ("nd", "Mean Teacher, 20 to 100% labels"),
        ("nd", "external unlabelled pool"),
        ("nd", "shift-tolerant loss"),
        ("bad", "UCF-EL encoder pretraining"),
        ("nd", "decoupled decoder, balanced head"),
        ("bad", "ALHVR"),
    ]),
    ("After SSL", "24 Oct to 14 Nov · test50 and E1", [
        ("ok", "5-model ensemble"),
        ("bad", "Dice on 12 classes"),
        ("bad", "ResNet-50 encoder"),
        ("nd", "2x resolution, +107 cells"),
        ("nd", "MIM and denoising pretraining"),
        ("nd", "crack copy-paste"),
        ("part", "encoder-preserving fine-tune (PF)"),
        ("x", "DINOv3 encoder"),
        ("part", "Skeleton Recall loss"),
        ("bad", "clDice loss, scuff class"),
        ("nd", "synthetic half-cut cells"),
    ]),
    ("Benchmark screens", "14 to 18 Nov · pool, 2 seeds", [
        ("nd", "U-Net R34, U-Net VGG-16"),
        ("nd", "DeepLabV3+ R34, stride 4"),
        ("bad", "DeepLabV3 R50, stride 8"),
        ("bad", "Pratt's weighted CE"),
        ("bad", "SegFormer, rare-class sampling"),
        ("nd", "Skeleton Recall, Jaccard loss"),
        ("nd", "weight EMA, encoder decay"),
        ("nd", "decision layers"),
        ("ok", "HRNet-W18: promoted"),
        ("ok", "SWAD: promoted"),
    ]),
    ("Decided", "18 to 23 Nov · pool 5 seeds; sealed E1", [
        ("part", "HRNet-W18"),
        ("nd", "SWAD"),
        ("part", "HRNet-W18 + SWAD"),
        ("ok", "D4 test-time augmentation"),
        ("ok", "final recipe on E1"),
        ("ok", "few-shot on E1"),
        ("nd", "5-model ensemble on E1"),
    ]),
]


def exp_grid():
    cols = []
    for title, sub, items in EXP:
        li = "".join(f'<div class="ei"><span class="mk" style="background:{OUT[k][0]}"></span>{esc(t)}</div>' for k, t in items)
        cols.append(f'<div class="ec"><div class="eh">{esc(title)}</div><div class="es">{esc(sub)}</div>{li}</div>')
    leg = "".join(f'<span class="lg"><span class="mk" style="background:{c}"></span>{esc(n)}</span>' for c, n in OUT.values())
    return f'<div class="eg">{"".join(cols)}</div><div class="legend">{leg}</div>'


SVGS = {"ssl": ssl_plot, "pr": pr_scatter}

if __name__ == "__main__":
    src = (HERE / "deck2_src.html").read_text()
    for k, f in SVGS.items():
        src = src.replace(f"<!--SVG:{k}-->", f())
    src = src.replace("<!--HTML:exp-->", exp_grid())
    assert "<!--SVG:" not in src and "<!--HTML:" not in src, "unreplaced marker"
    (HERE / "deck2.html").write_text(src)
    print("deck2.html written")
