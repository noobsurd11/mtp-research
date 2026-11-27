#!/usr/bin/env python3
"""Build deck.html from deck_src.html: replace <!--SVG:name--> markers with inline SVG plots.
Every number below is copied from the cited file (paths relative to ~/mtp/research or the gaint tree)."""
import html, pathlib

HERE = pathlib.Path(__file__).parent
INK, MUTED, GRID = "#1B1B1B", "#6A6A6A", "#E3E3E3"
LAV, BLUE, GREEN, PEACH, GREY = "#6B63B5", "#3E7CC4", "#4E9A52", "#D9773E", "#8A8A8A"
FONT = "font-family:'IBM Plex Sans',sans-serif"


def esc(s):
    return html.escape(str(s))


def T(x, y, s, size=16, anchor="start", color=INK, weight=400, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}" '
            f'font-weight="{weight}" {extra}>{esc(s)}</text>')


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="{FONT}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


# ---------- 1. SSL label-fraction plot (results/p13/README.md l20-27; results/p16/README.md l36-43) ----------
def ssl_plot():
    # inactive IoU on legacy test50, mean +- sd over seeds
    fr = ["5%", "20%", "50%", "100%"]
    sl = [(0.253, 0.037), (0.361, 0.037), (0.412, 0.012), (0.436, 0.013)]
    ss = [(0.370, 0.026), (0.390, 0.026), (0.418, 0.027), (0.439, 0.017)]
    gap = ["+0.117", "+0.029", "+0.006", "+0.003"]
    W, H, L, R, TOP, B = 760, 470, 80, 40, 30, 70
    y0, y1 = 0.20, 0.48
    X = lambda i: L + 40 + i * (W - L - R - 80) / 3
    Y = lambda v: TOP + (y1 - v) / (y1 - y0) * (H - TOP - B)
    o = []
    for v in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45]:
        o.append(f'<line x1="{L}" x2="{W-R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        o.append(T(L - 10, Y(v) + 5, f"{v:.2f}", 15, "end", MUTED))
    for i, f in enumerate(fr):
        o.append(T(X(i), H - B + 28, f, 17, "middle"))
    o.append(T(L + (W - L - R) / 2, H - 14, "labelled fraction of the training set", 16, "middle", MUTED))
    o.append(T(22, TOP + (H - TOP - B) / 2, "inactive IoU, legacy test50", 16, "middle", MUTED,
               extra=f'transform="rotate(-90 22 {TOP + (H - TOP - B) / 2:.1f})"'))
    for data, col, dx in [(sl, GREY, -7), (ss, LAV, 7)]:
        pts = " ".join(f"{X(i)+dx:.1f},{Y(m):.1f}" for i, (m, s) in enumerate(data))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"/>')
        for i, (m, s) in enumerate(data):
            o.append(f'<line x1="{X(i)+dx:.1f}" x2="{X(i)+dx:.1f}" y1="{Y(m-s):.1f}" y2="{Y(m+s):.1f}" stroke="{col}" stroke-width="2"/>')
            if col == LAV and i == 0:  # 5% SSL arm used CutMix: own marker
                cx, cy = X(i) + dx, Y(m)
                o.append(f'<polygon points="{cx},{cy-10} {cx+10},{cy} {cx},{cy+10} {cx-10},{cy}" fill="{col}"/>')
            else:
                o.append(f'<circle cx="{X(i)+dx:.1f}" cy="{Y(m):.1f}" r="7" fill="{col}"/>')
    for i, g in enumerate(gap):
        o.append(T(X(i), Y(max(ss[i][0] + ss[i][1], sl[i][0] + sl[i][1])) - 14, g, 18, "middle", LAV, 700))
    o.append(f'<circle cx="{W-250}" cy="{H-B-52}" r="7" fill="{LAV}"/>' + T(W - 236, H - B - 46, "semi-supervised (Mean Teacher)", 16))
    o.append(f'<circle cx="{W-250}" cy="{H-B-24}" r="7" fill="{GREY}"/>' + T(W - 236, H - B - 18, "supervised only", 16))
    cx, cy = W - 250, H - B - 80
    o.append(f'<polygon points="{cx},{cy-9} {cx+9},{cy} {cx},{cy+9} {cx-9},{cy}" fill="{LAV}"/>' + T(W - 236, cy + 6, "5% arm: with CutMix", 16))
    return svg(W, H, "".join(o))


# ---------- generic forest plot ----------
def forest(rows, lo, hi, W=620, rowh=46, left=250, M=0.010, ticks=None, xlabel="", tagw=0):
    """rows: (label, delta, lo, hi, colour, tag, filled)"""
    H = 40 + rowh * len(rows) + 56
    R = W - tagw - 20
    X = lambda v: left + (v - lo) / (hi - lo) * (R - left)
    o = []
    ticks = ticks or []
    for t in ticks:
        o.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="24" y2="{H-50}" stroke="{GRID}"/>')
        o.append(T(X(t), H - 30, f"{t:+.2f}" if t else "0", 14, "middle", MUTED))
    o.append(f'<line x1="{X(0):.1f}" x2="{X(0):.1f}" y1="20" y2="{H-50}" stroke="{INK}" stroke-width="1.5"/>')
    if M is not None:
        o.append(f'<line x1="{X(M):.1f}" x2="{X(M):.1f}" y1="20" y2="{H-50}" stroke="{INK}" stroke-dasharray="5 4"/>')
        o.append(T(X(M) + 4, 16, f"M {M:.3f}", 13, "start", MUTED))
    for i, (lab, d, a, b, col, tag, filled) in enumerate(rows):
        y = 40 + rowh * i + rowh / 2
        o.append(T(left - 14, y + 6, lab, 16, "end"))
        o.append(f'<line x1="{X(a):.1f}" x2="{X(b):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="3"/>')
        fill = col if filled else "#fff"
        o.append(f'<circle cx="{X(d):.1f}" cy="{y:.1f}" r="7.5" fill="{fill}" stroke="{col}" stroke-width="2.5"/>')
        if tag:
            o.append(T(R + 14, y + 6, tag, 14, "start", col, 600))
    if xlabel:
        o.append(T(left + (R - left) / 2, H - 6, xlabel, 15, "middle", MUTED))
    return svg(W, H, "".join(o))


# ---------- 2. CV5 5-seed contrasts vs PF (THESIS_TABLES.md T6 / T7a; crack relF1@2, 532 cells, OP-A) ----------
def cv5_forest():
    rows = [
        ("plain fine-tune", 0.0059, -0.0043, 0.0152, GREY, "no verdict (printed only)", True),
        ("HRNet-W18", 0.0104, 0.0012, 0.0203, PEACH, "NOT CONFIRMED (guards fail)", True),
        ("SWAD", 0.0070, -0.0007, 0.0156, GREY, "NOT CONFIRMED", True),
        ("HRNet + SWAD", 0.0154, 0.0065, 0.0260, PEACH, "NOT CONFIRMED (guards fail)", True),
        ("baseline + D4 TTA", 0.0134, 0.0066, 0.0207, GREEN, "CONFIRMED", True),
        ("final recipe *", 0.0222, 0.0138, 0.0308, GREEN, "passes its CV5 check *", False),
    ]
    return forest(rows, -0.01, 0.035, W=660, left=160, tagw=215, ticks=[-0.01, 0, 0.01, 0.02, 0.03],
                  xlabel="crack relF1@2, arm minus baseline (95% CI)")


# ---------- 3. E1 contrasts (results/final_opening_read/read_e1/read.txt; FINAL_OPENING_READ.md) ----------
def e1_forest():
    rows = [
        ("final - baseline", 0.0430, 0.0013, 0.1043, GREEN, "decides: CONFIRMED", True),
        ("final - (baseline + D4)", 0.0451, 0.0173, 0.0699, BLUE, "", True),
        ("(baseline + D4) - baseline", -0.0021, -0.0423, 0.0575, GREY, "", True),
        ("one final model - baseline", 0.0189, -0.0403, 0.1068, GREY, "", True),
        ("A/A: baseline seeds", 0.0022, -0.0425, 0.0507, GREY, "noise", False),
    ]
    return forest(rows, -0.06, 0.12, W=680, rowh=40, left=230, tagw=170, ticks=[-0.05, 0, 0.05, 0.10],
                  xlabel="crack relF1@2 difference on E1 (seed-aware 95% CI)")


# ---------- 4. Few-shot (results/t3b_open9_read/verdict.txt; read_t3b/read.txt) ----------
def fewshot_bars():
    arms = [("zero-shot", [0.4656, 0.5067, 0.4920], GREY), ("+ half of\nE1 images", [0.7005, 0.6969, 0.6797], BLUE),
            ("+ all other-fold\nE1 cells", [0.7309, 0.7030, 0.6943], GREEN)]
    W, H, L, B, TOP = 420, 430, 64, 80, 20
    Y = lambda v: TOP + (0.8 - v) / 0.8 * (H - TOP - B)
    o = []
    for v in [0, 0.2, 0.4, 0.6, 0.8]:
        o.append(f'<line x1="{L}" x2="{W-10}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{GRID}"/>')
        o.append(T(L - 8, Y(v) + 5, f"{v:.1f}", 14, "end", MUTED))
    bw = 82
    for i, (name, vals, col) in enumerate(arms):
        x = L + 30 + i * 112
        m = sum(vals) / 3
        o.append(f'<rect x="{x}" y="{Y(m):.1f}" width="{bw}" height="{Y(0)-Y(m):.1f}" fill="{col}" opacity="0.85"/>')
        o.append(T(x + bw / 2, Y(m) + 34, f"{m:.3f}", 18, "middle", "#fff", 700))
        for j, v in enumerate(vals):
            o.append(f'<circle cx="{x + 22 + j*19:.1f}" cy="{Y(v):.1f}" r="4" fill="#fff" stroke="{INK}" stroke-width="1.3"/>')
        for k, line in enumerate(name.split("\n")):
            o.append(T(x + bw / 2, H - B + 22 + k * 18, line, 14.5, "middle"))
    o.append(T(18, TOP + (H - TOP - B) / 2, "crack relF1@2 on E1", 15, "middle", MUTED,
               extra=f'transform="rotate(-90 18 {TOP + (H - TOP - B) / 2:.1f})"'))
    return svg(W, H, "".join(o))


def fewshot_strata():
    rows = [
        ("all E1 cells (106)", 0.2213, 0.0977, 0.3504, GREEN, "", True),
        ("full cells (44)", 0.1525, 0.0260, 0.4423, GREY, "", True),
        ("half-cut cells (62)", 0.2530, 0.0878, 0.3885, GREY, "", True),
        ("half-cut + scuff (29)", 0.3002, 0.1445, 0.4748, GREY, "", True),
        ("half-cut, no scuff (33)", -0.0701, -0.3019, 0.0517, GREY, "", True),
    ]
    return forest(rows, -0.35, 0.5, W=500, rowh=46, left=200, M=None, tagw=0, ticks=[-0.2, 0, 0.2, 0.4],
                  xlabel="all-cells model minus zero-shot (95% CI)")


# qualitative figures (fig/QUAL_NOTES.md) and slide captions
QUAL = {
    "QIMG1": "qual_pool_methods.png",
    "QIMG2": "qual_e1_final.png",
    "QIMG3": "qual_e1_fewshot.png",
    "<!--CAP:q1-->": "Pool cells, out of fold, seed 5. Rows by rule: median, 25th percentile and largest loss of our gain over the three EL-paper models.<br><br>Typical cells: every model finds the crack; Pratt's weighted loss draws it too wide. Loss row: most of our seeds miss this small crack (seed 5 finds it).<br><br><span style='font-size:14px;color:#5E5E5E'>EL-paper models re-implemented under our training; split cv5v2.</span>",
    "<!--CAP:q2-->": "<b>E1 illustration after the registered read; decides nothing.</b> Seed 5. Rows by rule: 90th pct, median, 25th pct, largest loss of final minus baseline. Final gains on a full cell; most cells change little; cracks along dark scuff streaks stay hard.",
    "<!--CAP:q3-->": "<b>E1 illustration after the registered read; decides nothing.</b> Out of fold, seed 5. Rows by rule: 90th pct, median, 25th pct, largest loss of few-shot minus zero-shot. Few-shot finds cracks along scuff streaks; easy cells unchanged; worst cell drops a crack at a busbar.",
}

SVGS = {"ssl": ssl_plot, "cv5": cv5_forest, "e1": e1_forest, "fs_bars": fewshot_bars, "fs_strata": fewshot_strata}

if __name__ == "__main__":
    src = (HERE / "deck_src.html").read_text()
    for k, f in SVGS.items():
        src = src.replace(f"<!--SVG:{k}-->", f())
    for k, v in QUAL.items():
        src = src.replace(k, v)
    assert "<!--SVG:" not in src, "unreplaced marker"
    (HERE / "deck.html").write_text(src)
    print("deck.html written")
