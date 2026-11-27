#!/usr/bin/env python3
"""MTP deck: build deck.html from deck_src.html by replacing <!--SVG:name--> markers with inline SVG.
Every number is copied from the file named in the comment (paths relative to to_human/ee511_deck/guide_ctx
or ~/mtp/research). Style: flat, no rounded corners, no boxed values."""
import html, math, pathlib

HERE = pathlib.Path(__file__).parent
INK, MUTED, GRID = "#1B1B1B", "#6A6A6A", "#E3E3E3"
GREEN, AMBER, GREY, RED, BLUE, LIGHT = "#2E7D4F", "#D9773E", "#9A9A9A", "#B8322A", "#2F6DB5", "#CFCFCF"
CRACK = "#D55E00"
FILL1, FILL2, FILL3 = "#E8EEF6", "#F3E9DF", "#EAF2E6"
FONT = "font-family:'IBM Plex Sans',sans-serif"


def esc(s):
    return html.escape(str(s))


def T(x, y, s, size=16, anchor="start", color=INK, weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
            f'font-weight="{weight}" {extra}>{esc(s)}</text>')


def R(x, y, w, h, fill, stroke="none", sw=1.2):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def L(x1, y1, x2, y2, col=INK, sw=1.5, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"{d}/>'


def ARW(x1, y1, x2, y2, col=INK, sw=1.6):
    ang = math.atan2(y2 - y1, x2 - x1)
    a, s = 7, 0.45
    p1 = (x2 - a * math.cos(ang - s), y2 - a * math.sin(ang - s))
    p2 = (x2 - a * math.cos(ang + s), y2 - a * math.sin(ang + s))
    return (L(x1, y1, x2, y2, col, sw) +
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="{FONT}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


# ---------- SSL label-fraction plot (results/p13/README.md l20-27; results/p16/README.md l36-43; as in EE511 build.py) ----------
def ssl_plot():
    fr = ["5%", "20%", "50%", "100%"]
    sl = [(0.253, 0.037), (0.361, 0.037), (0.412, 0.012), (0.436, 0.013)]
    ss = [(0.370, 0.026), (0.390, 0.026), (0.418, 0.027), (0.439, 0.017)]
    gap = ["+0.117", "+0.029", "+0.006", "+0.003"]
    W, H, Lm, Rm, TOP, B = 780, 460, 80, 30, 30, 70
    y0, y1 = 0.20, 0.48
    X = lambda i: Lm + 50 + i * (W - Lm - Rm - 100) / 3
    Y = lambda v: TOP + (y1 - v) / (y1 - y0) * (H - TOP - B)
    o = []
    for v in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]:
        o.append(L(Lm, Y(v), W - Rm, Y(v), GRID, 1))
        o.append(T(Lm - 10, Y(v) + 5, f"{v:.2f}", 15, "end", MUTED))
    for i, f in enumerate(fr):
        o.append(T(X(i), H - B + 30, f, 18, "middle"))
    o.append(T(Lm + (W - Lm - Rm) / 2, H - 12, "share of the training set that is labelled", 16, "middle", MUTED))
    o.append(T(22, TOP + (H - TOP - B) / 2, "inactive IoU (test50)", 16, "middle", MUTED,
               extra=f'transform="rotate(-90 22 {TOP + (H - TOP - B) / 2:.1f})"'))
    for data, col, dx in [(sl, GREY, -7), (ss, BLUE, 7)]:
        pts = " ".join(f"{X(i)+dx:.1f},{Y(m):.1f}" for i, (m, s) in enumerate(data))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        for i, (m, s) in enumerate(data):
            o.append(L(X(i) + dx, Y(m - s), X(i) + dx, Y(m + s), col, 2))
            o.append(f'<circle cx="{X(i)+dx:.1f}" cy="{Y(m):.1f}" r="7" fill="{col}"/>')
    for i, g in enumerate(gap):
        o.append(T(X(i), Y(max(ss[i][0] + ss[i][1], sl[i][0] + sl[i][1])) - 14, g, 19, "middle", BLUE, 700))
    o.append(f'<circle cx="{W-262}" cy="{H-B-50}" r="7" fill="{BLUE}"/>' + T(W - 248, H - B - 44, "semi-supervised (Mean Teacher)", 16))
    o.append(f'<circle cx="{W-262}" cy="{H-B-22}" r="7" fill="{GREY}"/>' + T(W - 248, H - B - 16, "supervised only", 16))
    return svg(W, H, "".join(o))


# ---------- generic forest plot ----------
def forest(rows, lo, hi, W=660, rowh=50, left=250, M=0.010, ticks=None, xlabel="", tagw=0, gaps=()):
    """rows: (label, delta, lo, hi, colour, tag, filled); gaps: row indices preceded by extra space"""
    H = 40 + rowh * len(rows) + 22 * len(gaps) + 56
    Rr = W - tagw - 20
    X = lambda v: left + (v - lo) / (hi - lo) * (Rr - left)
    o = []
    for t in ticks or []:
        o.append(L(X(t), 24, X(t), H - 50, GRID, 1))
        o.append(T(X(t), H - 30, f"{t:+.2f}" if t else "0", 14, "middle", MUTED))
    o.append(L(X(0), 20, X(0), H - 50, INK, 1.5))
    if M is not None:
        o.append(L(X(M), 20, X(M), H - 50, INK, 1.2, "5 4"))
        o.append(T(X(M) + 4, 15, "margin 0.010", 13, "start", MUTED))
    y = 40
    for i, (lab, d, a, b, col, tag, filled) in enumerate(rows):
        if i in gaps:
            y += 22
        yc = y + rowh / 2
        o.append(T(left - 14, yc + 6, lab, 16, "end"))
        o.append(L(X(a), yc, X(b), yc, col, 3))
        fill = col if filled else "#fff"
        o.append(f'<circle cx="{X(d):.1f}" cy="{yc:.1f}" r="7.5" fill="{fill}" stroke="{col}" stroke-width="2.5"/>')
        if tag:
            o.append(T(Rr + 14, yc + 6, tag, 14, "start", col, 600))
        y += rowh
    if xlabel:
        o.append(T(left + (Rr - left) / 2, H - 6, xlabel, 15, "middle", MUTED))
    return svg(W, H, "".join(o))


# ---------- architecture study: 2-seed screens vs PF (THESIS_TABLES.md T16a; thesis s7.2, s7.3; cv5v2, training machine) ----------
def arch_forest():
    rows = [
        ("HRNet-W18 + U-Net++", 0.0114, 0.0032, 0.0203, GREEN, "promoted", True),
        ("U-Net, ResNet-34", -0.0016, -0.0110, 0.0073, GREY, "", True),
        ("SegFormer MiT-B2", -0.0026, -0.0132, 0.0095, GREY, "", True),
        ("U-Net, VGG-16 (Hanifi)", -0.0064, -0.0189, 0.0042, GREY, "", True),
        ("DeepLabV3+, stride 4", -0.0093, -0.0204, 0.0019, GREY, "", True),
        ("DeepLabV3, stride 8 (UCF-EL)", -0.0773, -0.0892, -0.0594, RED, "worse", True),
    ]
    return forest(rows, -0.10, 0.03, W=640, rowh=44, left=250, tagw=80, ticks=[-0.10, -0.05, 0, 0.02],
                  xlabel="crack relF1@2 minus baseline U-Net++ (95% CI)")


# ---------- CV5 5-seed rows vs PF (THESIS_TABLES.md T6 / T7a; 532 cells, OP-A) ----------
def cv5_forest():
    rows = [
        ("HRNet-W18", 0.0104, 0.0012, 0.0203, AMBER, "gain, guards fail", True),
        ("SWAD", 0.0070, -0.0007, 0.0156, GREY, "not confirmed", True),
        ("HRNet + SWAD", 0.0154, 0.0065, 0.0260, AMBER, "gain, guards fail", True),
        ("baseline + D4 views", 0.0134, 0.0066, 0.0207, GREEN, "CONFIRMED", True),
        ("final recipe *", 0.0222, 0.0138, 0.0308, GREEN, "passes (*biased)", False),
    ]
    return forest(rows, -0.01, 0.035, W=780, rowh=72, left=200, tagw=170, ticks=[-0.01, 0, 0.01, 0.02, 0.03],
                  xlabel="crack relF1@2 minus baseline, pool cells out of fold (95% CI)")


# ---------- E1 (guide_ctx/FINAL_OPENING_READ.md, ERRATA; thesis s1.5, s12.1; t3b_verdict.txt) ----------
def e1_forest():
    rows = [
        ("final - baseline, 106 cells", 0.0430, 0.0013, 0.1043, GREEN, "CONFIRMED", True),
        ("full cells (44)", 0.1464, 0.0420, 0.2278, GREY, "", True),
        ("half-cut cells (62)", 0.0110, -0.0289, 0.0722, GREY, "n.d.", True),
        ("few-shot - zero-shot, 106", 0.2213, 0.0977, 0.3504, GREEN, "CONFIRMED", True),
    ]
    return forest(rows, -0.05, 0.40, W=720, rowh=52, left=230, tagw=110, ticks=[0, 0.1, 0.2, 0.3, 0.4],
                  xlabel="crack relF1@2 difference on E1 (seed-aware 95% CI)", gaps=(3,))


# ---------- strict IoU vs relF1@2 of a correct label redrawn (thesis s2.3, Fig. 2.2; 229 pool crack cells, v1.1) ----------
def shift_bars():
    cats = [("moved 1 px", 0.483), ("moved 2 px", 0.249), ("thinned to 1 px", 0.465), ("redrawn 3 px", 0.605)]
    W, H, Lm, B, TOP = 600, 380, 60, 60, 20
    Y = lambda v: TOP + (1.05 - v) / 1.05 * (H - TOP - B)
    o = []
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        o.append(L(Lm, Y(v), W - 10, Y(v), GRID, 1))
        o.append(T(Lm - 8, Y(v) + 5, f"{v:.2f}", 14, "end", MUTED))
    bw, gw = 46, (W - Lm - 20) / 4
    for i, (c, v) in enumerate(cats):
        x = Lm + 18 + i * gw
        o.append(R(x, Y(v), bw, Y(0) - Y(v), CRACK))
        o.append(T(x + bw / 2, Y(v) - 8, f"{v:.2f}", 15, "middle", CRACK, 700))
        o.append(R(x + bw + 6, Y(1.0), bw, Y(0) - Y(1.0), BLUE))
        o.append(T(x + bw + 6 + bw / 2, Y(1.0) - 8, "1.00", 15, "middle", BLUE, 700))
        o.append(T(x + bw + 3, H - B + 24, c, 15, "middle"))
    return svg(W, H, "".join(o))


# ---------- module-grouped folds sketch (thesis s4.3: 24 modules spanned two cv5v2 folds, 91 cells; cv5v3 285 groups) ----------
def fold_sketch():
    W, H = 470, 300
    o = []
    for r, (name, fixed) in enumerate([("first split", False), ("corrected split", True)]):
        y0 = 30 + r * 140
        o.append(T(0, y0 - 8, name, 16, "start", INK, 600))
        for f in range(5):
            x = 10 + f * 90
            o.append(R(x, y0, 80, 80, "#F4F4F4", "#BDBDBD", 1))
            o.append(T(x + 40, y0 + 100, f"fold {f+1}", 13, "middle", MUTED))
        # one physical module: two cells
        a = (30, y0 + 25)
        b = (30 + 90 + 30, y0 + 25) if not fixed else (30 + 30, y0 + 25)
        col = RED if not fixed else GREEN
        o.append(R(a[0], a[1], 22, 22, col))
        o.append(R(b[0], b[1], 22, 22, col))
        if not fixed:
            o.append(L(a[0] + 22, a[1] + 11, b[0], b[1] + 11, col, 2, "4 3"))
    return svg(W, H, "".join(o))


# ---------- precision vs recall, 2-seed screens (THESIS_TABLES.md T15, training-machine rows; cv5v2, argmax) ----------
def pr_scatter():
    pts = [  # label, relP@2, relR@2, colour, show label, label dx, dy
        ("baseline U-Net++", 0.894, 0.799, INK, True, -12, 22),
        ("HRNet-W18", 0.902, 0.814, GREEN, True, 12, -10),
        ("plain fine-tune", 0.897, 0.807, GREY, False, 0, 0),
        ("U-Net R34", 0.896, 0.795, GREY, False, 0, 0),
        ("U-Net VGG-16", 0.882, 0.798, GREY, False, 0, 0),
        ("DeepLabV3+", 0.884, 0.791, GREY, False, 0, 0),
        ("Skeleton Recall", 0.884, 0.815, GREY, False, 0, 0),
        ("SegFormer", 0.877, 0.809, GREY, False, 0, 0),
        ("DeepLabV3, stride 8 (UCF-EL)", 0.809, 0.729, RED, True, 12, 5),
        ("Pratt weighted loss", 0.648, 0.892, RED, True, -12, -12),
    ]
    W, H, Lm, Rm, TOP, B = 640, 470, 74, 24, 20, 62
    x0, x1, y0, y1 = 0.70, 0.92, 0.60, 0.95
    X = lambda r: Lm + (r - x0) / (x1 - x0) * (W - Lm - Rm)
    Y = lambda p: TOP + (y1 - p) / (y1 - y0) * (H - TOP - B)
    o = []
    for v in [0.70, 0.75, 0.80, 0.85, 0.90]:
        o.append(L(X(v), TOP, X(v), H - B, GRID, 1))
        o.append(T(X(v), H - B + 22, f"{v:.2f}", 14, "middle", MUTED))
    for v in [0.60, 0.70, 0.80, 0.90]:
        o.append(L(Lm, Y(v), W - Rm, Y(v), GRID, 1))
        o.append(T(Lm - 8, Y(v) + 5, f"{v:.2f}", 14, "end", MUTED))
    for F in [0.75, 0.80, 0.85]:  # iso-F1 curves: P = F R / (2R - F)
        seg = []
        r = x0
        while r <= x1 + 1e-9:
            p = F * r / (2 * r - F)
            if y0 <= p <= y1:
                seg.append(f"{X(r):.1f},{Y(p):.1f}")
            r += 0.002
        o.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="#B9B9B9" stroke-width="1.2" stroke-dasharray="4 4"/>')
        rl = 0.905
        o.append(T(X(rl) + 4, Y(F * rl / (2 * rl - F)) - 6, f"F1 {F:.2f}", 12, "start", MUTED))
    for lab, p, r, col, show, dx, dy in pts:
        o.append(f'<circle cx="{X(r):.1f}" cy="{Y(p):.1f}" r="{7 if show else 5}" fill="{col}"/>')
        if show:
            anc = "end" if dx < 0 else "start"
            o.append(T(X(r) + dx, Y(p) + dy, lab, 15, anc, col, 600))
    o.append(T(Lm + (W - Lm - Rm) / 2, H - 14, "crack recall relR@2", 16, "middle", MUTED))
    o.append(T(18, TOP + (H - TOP - B) / 2, "crack precision relP@2", 16, "middle", MUTED,
               extra=f'transform="rotate(-90 18 {TOP + (H - TOP - B) / 2:.1f})"'))
    o.append(f'<circle cx="{X(0.712):.1f}" cy="{Y(0.625):.1f}" r="5" fill="{GREY}"/>' +
             T(X(0.712) + 12, Y(0.625) + 5, "other screened models", 14, "start", MUTED))
    return svg(W, H, "".join(o))


# ---------- architecture sketches (schematic, drawn by us) ----------
ENC, DEC, MID, HEAD = "#C9D7EC", "#F2D3BD", "#E6E6E6", "#CFE3C4"


def _enc_dec(nested=False, W=270, H=190):
    o = []
    lv = 4
    hs = [60, 44, 30, 18]
    xs_e = [14, 44, 74, 104]
    xs_d = [W - 34, W - 64, W - 94, W - 124]
    cy = [40 + i * 34 for i in range(lv)]
    for i in range(lv):
        o.append(R(xs_e[i], cy[i] - hs[i] / 2 + 0, 18, hs[i] / 1.6, ENC, INK, 1))
        if i < lv - 1:
            o.append(R(xs_d[i], cy[i] - hs[i] / 2, 18, hs[i] / 1.6, DEC, INK, 1))
    # bottleneck
    o.append(R(W / 2 - 9, cy[3] - 6, 18, 14, ENC, INK, 1))
    for i in range(lv - 1):
        o.append(L(xs_e[i] + 9, cy[i] + hs[i] / 3.2 - hs[i] / 2 + hs[i] / 3.2, xs_e[i + 1] + 9, cy[i + 1] - hs[i + 1] / 2, MUTED, 1.2))
        o.append(L(xs_d[i + 1] + 9 if i + 1 < lv - 1 else W / 2, cy[i + 1] - hs[i + 1] / 2, xs_d[i] + 9, cy[i] + hs[i] / 3.2 - hs[i] / 2 + hs[i] / 3.2, MUTED, 1.2))
        ys = cy[i] - hs[i] / 2 + hs[i] / 3.2
        if not nested:
            o.append(ARW(xs_e[i] + 18, ys, xs_d[i] - 2, ys, BLUE, 1.4))
        else:
            n = lv - 1 - i
            pos = [xs_e[i] + 18 + (xs_d[i] - xs_e[i] - 18) * (k + 1) / (n + 1) for k in range(n)]
            prev = xs_e[i] + 18
            for px in pos:
                o.append(ARW(prev, ys, px - 6, ys, BLUE, 1.2))
                o.append(R(px - 6, ys - 6, 12, 12, MID, INK, 1))
                prev = px + 6
            o.append(ARW(prev, ys, xs_d[i] - 2, ys, BLUE, 1.2))
    return o


def arch_unet():
    W, H = 270, 175
    o = _enc_dec(False, W, H)
    return svg(W, H, "".join(o))


def arch_unetpp():
    W, H = 270, 175
    o = _enc_dec(True, W, H)
    return svg(W, H, "".join(o))


def arch_deeplab():
    W, H = 270, 175
    o = []
    xs = [14, 44, 74, 104]
    hs = [60, 44, 30, 22]
    ys = [40, 74, 108, 130]
    for i in range(4):
        o.append(R(xs[i], ys[i] - hs[i] / 2, 18, hs[i] / 1.6, ENC, INK, 1))
        if i < 3:
            o.append(L(xs[i] + 9, ys[i] - hs[i] / 2 + hs[i] / 1.6, xs[i + 1] + 9, ys[i + 1] - hs[i + 1] / 2, MUTED, 1.2))
    # ASPP: parallel branches
    ax = 140
    for k in range(4):
        o.append(R(ax, 108 + k * 11, 34, 8, MID, INK, 1))
    o.append(ARW(xs[3] + 18, 130, ax - 2, 125, MUTED, 1.2))
    # decoder at stride 4
    o.append(R(200, 52, 18, 30, DEC, INK, 1))
    o.append(ARW(ax + 34, 120, 207, 84, MUTED, 1.2))
    o.append(ARW(xs[1] + 18, 66, 198, 66, BLUE, 1.3))
    o.append(ARW(218, 66, 252, 66, MUTED, 1.2))
    o.append(T(235, 54, "x4", 12, "middle", MUTED))
    o.append(T(157, 165, "ASPP", 12, "middle", MUTED))
    return svg(W, H, "".join(o))


def arch_hrnet(W=270, H=175):
    o = []
    rows = [(30, 18), (66, 14), (98, 10), (124, 7)]
    starts = [10, 70, 130, 190]
    for i, (y, h) in enumerate(rows):
        x0 = starts[i] if i else 10
        o.append(R(x0, y - h / 2, W - 22 - x0, h, ENC if i else "#A9C2E4", INK, 1))
    for xc in [70, 130, 190]:
        for i in range(3):
            if starts[i + 1] <= xc:
                o.append(L(xc - 6, rows[i][0] + rows[i][1] / 2, xc + 6, rows[i + 1][0] - rows[i + 1][1] / 2, MUTED, 1.1))
                o.append(L(xc + 6, rows[i + 1][0] - rows[i + 1][1] / 2, xc + 16, rows[i][0] + rows[i][1] / 2, MUTED, 1.1))
    o.append(T(8, 14, "high resolution", 11, "start", MUTED))
    o.append(T(W - 18, 148, "low resolution", 11, "end", MUTED))
    return svg(W, H, "".join(o))


def final_diagram():
    W, H = 1150, 250
    o = []
    # input
    o.append(f'<image href="../fig/title_cell.png" x="0" y="40" width="160" height="160"/>')
    o.append(T(80, 225, "EL cell, 512 x 512", 14, "middle", MUTED))
    o.append(ARW(168, 120, 208, 120))
    # HRNet encoder
    enc = arch_hrnet(300, 175).replace('<svg ', '<svg x="215" y="32" ', 1)
    o.append(enc)
    o.append(T(365, 225, "HRNet-W18 encoder (ImageNet)", 15, "middle", INK, 600))
    o.append(T(365, 22, "keeps a high-resolution stream", 13, "middle", MUTED))
    o.append(ARW(520, 120, 560, 120))
    dec = arch_unetpp().replace('<svg ', '<svg x="565" y="38" ', 1)
    o.append(dec)
    o.append(T(700, 225, "U-Net++ decoder", 15, "middle", INK, 600))
    o.append(T(700, 22, "nested skip connections", 13, "middle", MUTED))
    o.append(ARW(845, 120, 885, 120))
    # output map sketch
    o.append(R(895, 45, 150, 150, "#F4F4F4", "#BDBDBD", 1))
    o.append(f'<polyline points="930,60 955,105 948,140 975,185" fill="none" stroke="{CRACK}" stroke-width="3"/>')
    o.append(f'<polygon points="1000,50 1040,50 1040,110 1010,95" fill="#6FA8DC" opacity="0.8"/>')
    o.append(T(970, 225, "24-class map", 15, "middle", INK, 600))
    o.append(T(1062, 105, "crack", 13, "start", CRACK, 600))
    o.append(T(1062, 75, "inactive", 13, "start", BLUE, 600))
    return svg(W, H, "".join(o))


# ---------- all experiments: four columns, marker colour = outcome ----------
OUT = {"ok": (GREEN, "helped / confirmed"), "part": (AMBER, "gain, but guard fails or narrow"),
       "nd": (GREY, "not detectable"), "bad": (RED, "worse / failed"), "x": (LIGHT, "invalid / stopped")}
EXP = [
    ("Semi-supervised (Oct)", "test50, context only", [
        ("x", "first Mean Teacher + SemiCE (bug)"),
        ("nd", "attention gate (SA U-Net++)"),
        ("ok", "Mean Teacher, 5% labels"),
        ("nd", "Mean Teacher, 20 to 100%"),
        ("nd", "external unlabelled pool"),
        ("nd", "shift-tolerant loss"),
        ("bad", "UCF-EL encoder pretraining"),
        ("nd", "decoupled decoder, balanced head"),
        ("bad", "ALHVR"),
    ]),
    ("After SSL (late Oct)", "test50 and E1 reads", [
        ("ok", "5-model ensemble"),
        ("bad", "Dice on 12 classes"),
        ("bad", "ResNet-50 encoder"),
        ("nd", "2x resolution, +107 cells"),
        ("nd", "MIM, denoising pretraining"),
        ("nd", "crack copy-paste"),
        ("part", "encoder-preserving fine-tune (PF)"),
        ("x", "DINOv3 encoder"),
        ("part", "Skeleton Recall loss"),
        ("bad", "clDice loss, scuff class"),
        ("nd", "synthetic half-cut cells"),
    ]),
    ("Benchmark screens (Nov)", "pool, 2 seeds", [
        ("nd", "U-Net, VGG-16 U-Net"),
        ("nd", "DeepLabV3+, stride 4"),
        ("bad", "DeepLabV3, stride 8 (UCF-EL)"),
        ("bad", "Pratt's weighted loss"),
        ("bad", "SegFormer, rare-class sampling"),
        ("nd", "Skeleton Recall, Jaccard loss"),
        ("nd", "weight EMA, encoder decay"),
        ("nd", "decision layers"),
        ("ok", "HRNet-W18: promoted"),
        ("ok", "SWAD: promoted"),
    ]),
    ("Decided (Nov)", "pool 5 seeds; sealed E1", [
        ("part", "HRNet-W18"),
        ("nd", "SWAD"),
        ("part", "HRNet + SWAD"),
        ("ok", "D4 test-time views"),
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


SVGS = {"ssl": ssl_plot, "arch": arch_forest, "cv5": cv5_forest, "e1": e1_forest, "shift": shift_bars,
        "folds": fold_sketch, "pr": pr_scatter, "a_unet": arch_unet, "a_unetpp": arch_unetpp,
        "a_deeplab": arch_deeplab, "a_hrnet": arch_hrnet, "final": final_diagram}

if __name__ == "__main__":
    src = (HERE / "deck_src.html").read_text()
    for k, f in SVGS.items():
        src = src.replace(f"<!--SVG:{k}-->", f())
    src = src.replace("<!--HTML:exp-->", exp_grid())
    assert "<!--SVG:" not in src and "<!--HTML:" not in src, "unreplaced marker"
    (HERE / "deck.html").write_text(src)
    print("deck.html written")
