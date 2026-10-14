"""MTP mid-term deck builder (python-pptx). Figures are inserted from the research repo as they are."""
import os
import sys

sys.path.insert(0, "/tmp/pptxlib")
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = os.environ.get("MTP_ROOT", "/home/yugma/mtp/research")
DS = os.environ.get("MTP_DS", "/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104")
OUT = os.environ.get("MTP_OUT", ROOT + "/to_human/MTP_midterm_deck.pptx")

HEAD, BODY, MONO = "Archivo Black", "Inter", "JetBrains Mono"
INK = RGBColor.from_string("111111")
PANEL = RGBColor.from_string("142B29")
WHITE = RGBColor.from_string("FFFFFF")
ACCENT = RGBColor.from_string("2A7F78")
SOFT = RGBColor.from_string("9FD3CC")
MUTED = RGBColor.from_string("5E6665")
PANEL_MUTED = RGBColor.from_string("B9C7C5")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
STATE = {"n": 0}

ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def new_slide(number=True):
    s = prs.slides.add_slide(BLANK)
    STATE["n"] += 1
    if number:
        tb(s, 12.33, 7.02, 0.5, 0.25, str(STATE["n"]), size=10, color=MUTED, align="r")
    return s


def bullet(p):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(0.32))))
    pPr.set("indent", str(-int(Inches(0.32))))
    bu = etree.SubElement(pPr, qn("a:buChar"))
    bu.set("char", "•")


def tb(slide, x, y, w, h, paras, size=18, font=BODY, color=INK, bold=False, align="l", anchor="t", after=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ANCHOR[anchor]
    if isinstance(paras, str):
        paras = [paras]
    for i, item in enumerate(paras):
        d = item if isinstance(item, dict) else {"t": item}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[d.get("align", align)]
        sa = d.get("after", after)
        if sa is not None:
            p.space_after = Pt(sa)
        r = p.add_run()
        r.text = d["t"]
        f = r.font
        f.size = Pt(d.get("size", size))
        f.name = d.get("font", font)
        f.bold = d.get("bold", bold)
        f.color.rgb = d.get("color", color)
        if d.get("spc"):
            r._r.get_or_add_rPr().set("spc", str(d["spc"]))
        if d.get("bullet"):
            bullet(p)
    return box


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_w)
    return shp


def tag(slide, label, x=0.6, y=0.42, dark=False):
    tb(slide, x, y, 7.0, 0.3, [{"t": label, "spc": 250}], size=12, bold=True, color=SOFT if dark else ACCENT)


def title(slide, text, x=0.6, y=0.75, w=12.1, size=32, color=INK):
    tb(slide, x, y, w, 0.9, text, size=size, font=HEAD, color=color)


def bigline(slide, text, x, y, w, size=22, color=INK, h=0.6):
    tb(slide, x, y, w, h, text, size=size, font=HEAD, color=color)


def panel_left(slide, text, w=4.7, size=34):
    rect(slide, 0, 0, w, 7.5, fill=PANEL)
    tb(slide, 0.6, 0.8, w - 1.1, 5.9, text, size=size, font=HEAD, color=WHITE, anchor="m")


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


ORDER = ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]


def borders(cell, spec):
    tcPr = cell._tc.get_or_add_tcPr()
    for t in ORDER:
        for old in tcPr.findall(qn(t)):
            tcPr.remove(old)
    for i, t in enumerate(ORDER):
        ln = etree.Element(qn(t))
        s = spec.get(t[-1])
        if s:
            ln.set("w", str(int(Pt(s))))
            sf = etree.SubElement(ln, qn("a:solidFill"))
            c = etree.SubElement(sf, qn("a:srgbClr"))
            c.set("val", "111111")
        else:
            ln.set("w", "0")
            etree.SubElement(ln, qn("a:noFill"))
        tcPr.insert(i, ln)


def table(slide, rows, x, y, w, colw=None, size=18, rowh=0.56, align=None, bold_first_col=False):
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(rowh * nr))
    tbl = gs.table
    tblPr = tbl._tbl.tblPr
    tblPr.set("firstRow", "0")
    tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"
    colw = colw or [1.0] * nc
    tot = float(sum(colw))
    for j, cw in enumerate(colw):
        tbl.columns[j].width = Inches(cw * w / tot)
    for i in range(nr):
        tbl.rows[i].height = Inches(rowh)
        for j in range(nc):
            cell = tbl.cell(i, j)
            cell.fill.background()
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(rows[i][j])
            f = r.font
            f.size = Pt(size)
            f.name = BODY
            f.color.rgb = INK
            f.bold = i == 0 or (bold_first_col and j == 0)
            a = align[j] if align and j < len(align) else ("l" if j == 0 else "c")
            p.alignment = ALIGN[a]
            spec = {}
            if i == 0:
                spec["T"] = 1.5
                spec["B"] = 0.75
            if i == nr - 1:
                spec["B"] = 1.5
            borders(cell, spec)
    return gs


def pic(slide, rel, x, y, w, h):
    p = rel if rel.startswith("/") else os.path.join(ROOT, rel)
    if not os.path.exists(p):
        tb(slide, x, y, w, h, "missing figure: " + rel, size=12, color=MUTED, align="c", anchor="m")
        return None
    iw, ih = Image.open(p).size
    s = min(w / iw, h / ih)
    pw, ph = iw * s, ih * s
    return slide.shapes.add_picture(p, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))


# ---------------------------------------------------------------- 1 title
s = new_slide(number=False)
rect(s, 8.6, 0, 4.733, 7.5, fill=PANEL)
pic(s, DS + "/images_train_original/CFVS_00031_r4_c4.png", 9.27, 1.75, 3.4, 3.4)
tb(s, 9.27, 5.3, 3.4, 0.3, "One EL solar cell image", size=12, color=PANEL_MUTED, align="c")
tb(s, 0.8, 0.9, 7.0, 0.35, [{"t": "MTP REPORT", "spc": 300}], size=14, bold=True, color=ACCENT)
tb(s, 0.8, 1.4, 7.4, 2.4, "LEARNING THIN, RARE DEFECTS FROM FEW LABELS", size=40, font=HEAD)
tb(s, 0.8, 3.75, 7.4, 0.9, [
    "Semi-supervised segmentation of electroluminescence (EL) solar cell images",
    {"t": "Part 1: training methodology", "color": MUTED},
], size=18, after=4)
tb(s, 0.8, 5.0, 7.4, 1.9, [
    {"t": "Yash Patil · B23222      Muskan · B23274", "bold": True},
    "Guide: Dr. Praful Hambarde, CAIR",
    "Co-guide: Dr. Dinesh Singh, SCEE",
    {"t": "IIT Mandi", "color": MUTED},
], size=16, after=5)
notes(s, "EL images of solar cells. We segment cracks and dead (inactive) areas with very few labels. This talk covers part 1 of 3: the training methodology.")

# ---------------------------------------------------------------- 2 problem
s = new_slide()
panel_left(s, "THE PROBLEM: FIND DEFECTS THAT COST POWER")
tag(s, "PROBLEM", x=5.4)
tb(s, 5.4, 1.6, 7.3, 3.0, [
    {"t": "EL image: bright = working silicon, dark = no current", "bullet": True},
    {"t": "Crack and inactive area drive power loss", "bullet": True},
    {"t": "Only 582 labelled cells in total", "bullet": True},
], size=22, after=16)
bigline(s, "Two defects. Opposite problems.", 5.4, 4.9, 7.3, size=30)
notes(s, "End use: defect map, then crack length and dead area, then a severity grade. Pixel maps are only the first step, so pixel scores are a stand-in for what matters.")

# ---------------------------------------------------------------- 3 why hard
s = new_slide()
tag(s, "OUR WORK · DATA ANALYSIS")
title(s, "WHY IT IS HARD")
table(s, [
    ["", "Crack", "Inactive"],
    ["Share of train pixels", "0.19%", "0.22%"],
    ["Label vs visible line", "1.75 px on ~4 px", "clean regions"],
    ["Perfect mask shifted 1 px", "IoU 0.56", "IoU 0.94"],
    ["Test cells containing it", "48 of 50", "16 of 50"],
    ["Biggest test cells hold", "1 cell: 12%", "3 cells: 59%"],
    ["Limited by", "label noise", "too few examples"],
], 0.6, 1.9, 7.9, colw=[3.3, 2.1, 2.5], size=18, rowh=0.64)
pic(s, "data_analysis/figs/crack_overlays_3.png", 8.7, 1.45, 4.0, 5.55)
notes(s, "Crack IoU of 0.4 is not bad: a perfect crack mask nudged by 1 px scores only 0.56. Inactive is the opposite: clean labels but very few examples, and 3 test cells hold 59% of its pixels. Noise vs scarcity.")

# ---------------------------------------------------------------- 4 objectives
s = new_slide()
panel_left(s, "OBJECTIVES (PART 1 OF 3)")
tag(s, "PROBLEM", x=5.4)
tb(s, 5.4, 1.6, 7.3, 3.6, [
    {"t": "1   Find what moves crack and inactive with few labels: labels, recipe, pretraining or unlabelled data"},
    {"t": "2   Test semi-supervised learning (SSL) fairly"},
    {"t": "3   Measure what the use case needs: per cell, on unseen modules"},
], size=22, after=18)
tb(s, 5.4, 6.2, 7.3, 0.4, "Part 2: architecture · Part 3: deployment and severity", size=16, color=MUTED)
notes(s, "The thesis has three parts; everything in this talk is part 1, the training methodology.")

# ---------------------------------------------------------------- 5 data
s = new_slide()
tag(s, "DATA")
title(s, "BENCHMARKEL (PRATT ET AL. 2023)")
table(s, [
    ["Split", "Cells"],
    ["Train", "478"],
    ["Val", "54"],
    ["Test", "50 (hand-picked by the authors)"],
], 0.6, 1.8, 6.4, colw=[1.6, 4.8], size=18)
table(s, [
    ["Labelled", "5%", "10%", "20%", "50%", "100%"],
    ["Cells", "23", "47", "95", "239", "478"],
], 0.6, 4.35, 8.2, colw=[1.7, 1, 1, 1, 1, 1], size=18)
tb(s, 0.6, 5.85, 8.4, 1.2, [
    {"t": "Unlabelled: rest of train (labels hidden) + external pool of 11,938 cells", "bullet": True},
    {"t": "Labels: BenchmarkEL Oct 2022 crack revision, used from P6 on", "bullet": True},
], size=16, after=8)
pic(s, "data_analysis/figs/peek_sources.png", 9.3, 1.45, 3.4, 5.55)
notes(s, "Five sources. The test set was picked by the dataset authors to contain defects, so it is not random. The external pool covers only two of the five sources.")

# ---------------------------------------------------------------- 6 existing work
s = new_slide()
tag(s, "EXISTING WORK")
title(s, "NO COMMON PROTOCOL")
table(s, [
    ["Work", "Data", "Reports", "Catch"],
    ["Pratt 2023", "our 582 cells", "crack 0.25 · gridline 0.20 · inactive 0.38", "per-image median, 1 run"],
    ["SEiPV-Net 2023", "same 50 test cells", "mIoU 0.86", "24 classes, rule unstated"],
    ["Mazen 2024", "29-class release", "mIoU 0.91", "same averaging"],
    ["Torpey 2024", "642-cell release", "mIoU 0.55", "full labels, best-val weights"],
    ["Hanifi 2025", "29-class release", "defect classes 0.33", "only defect-level number"],
], 0.6, 1.8, 12.1, colw=[1.9, 2.2, 4.6, 3.4], size=16, rowh=0.62, align=["l", "l", "l", "l"])
bigline(s, "No SSL segmentation work on this data since 2024.", 0.6, 6.05, 12.1, size=24)
notes(s, "Mazen 2024 is the Attention-Based SegNet paper (IEEE Access). Hanifi 2025 is from the E-SCDD group (IEA/AIE 2025, code public). Numbers across papers use different releases, metrics and class sets. PV-S3 (Jha 2025) claims +30% over Pratt but compares unlike metrics. Our scan found no new semi-supervised segmentation on BenchmarkEL after PV-S3 and Torpey.")

# ---------------------------------------------------------------- 7 rulers
s = new_slide()
tag(s, "OUR WORK · RESCORE")
title(s, "SAME TEST SET, DIFFERENT RULERS")
table(s, [
    ["Model (same 50 test cells)", "Plain class mean", "Pixel-weighted F1", "Per image, absent = 1"],
    ["Ours, supervised 100%", "0.51", "0.93", "0.84"],
    ["Ours, supervised 5%", "0.38", "0.92", "0.73"],
    ["SEiPV-Net (paper)", "not reported", "0.94", "0.86 (mIoU)"],
], 0.6, 1.9, 12.1, colw=[3.6, 2.6, 2.8, 3.1], size=19, rowh=0.72)
bigline(s, "Choose the ruler before comparing.", 0.6, 5.0, 12.1, size=30)
tb(s, 0.6, 5.85, 12.1, 0.8, "Pixel-weighted F1 barely moves from 5% to 100% labels: it does not measure defects.", size=18, color=MUTED)
notes(s, "We rescored our checkpoints with 24-class confusion matrices on the original labels. Their F1 matches our pixel-weighted F1 and their mIoU matches our per-image mean with absent classes scored as perfect. A plain class mean of our best model is 0.51. Their rule is not confirmed, since no code is public.")

# ---------------------------------------------------------------- 8 methods built on
s = new_slide()
tag(s, "EXISTING WORK")
title(s, "METHODS WE BUILT ON")
boxes = [
    ("Mean Teacher", "NeurIPS 2017", "EMA teacher labels the unlabelled images"),
    ("CutMix consistency", "BMVC 2020", "mask-based mixing for segmentation"),
    ("ALHVR", "ICCV 2025", "value ≠ confidence; routes uncertain pixels"),
    ("SKCDF", "CVPR 2025", "keeps pseudo-labels out of the labelled decoder"),
]
bx, bw, gap = 0.6, 2.55, 0.62
for i, (name, venue, line) in enumerate(boxes):
    x = bx + i * (bw + gap)
    rect(s, x, 2.1, bw, 2.6, line=INK, line_w=1.0)
    tb(s, x + 0.2, 2.3, bw - 0.4, 2.2, [
        {"t": name, "bold": True, "size": 19, "after": 4},
        {"t": venue, "color": MUTED, "size": 14, "after": 14},
        {"t": line, "size": 15},
    ])
    if i < 3:
        tb(s, x + bw, 3.05, gap, 0.6, "→", size=28, color=MUTED, align="c")
bigline(s, "Borrowed from medical SSL, tested on thin cracks.", 0.6, 5.4, 12.1, size=24)
notes(s, "ALHVR was the starting inspiration. Our probe P5 later showed that confidence routing struggles on 1 to 2 px cracks.")

# ---------------------------------------------------------------- 9 approach
s = new_slide()
panel_left(s, "ONE CHANGE AT A TIME")
tag(s, "OUR WORK · APPROACH", x=5.4)
tb(s, 5.4, 1.5, 7.3, 2.6, [
    {"t": "Protocol locked before any run", "bullet": True},
    {"t": "Every SSL arm has a loss-off twin", "bullet": True},
    {"t": "Same 20,000 steps, final weights, 3 to 5 seeds", "bullet": True},
], size=22, after=14)
rect(s, 5.4, 4.45, 7.3, 1.45, line=INK, line_w=1.0)
tb(s, 5.6, 4.6, 7.0, 1.2, [
    "B beats A if Δ > max(0.01, 2·√((sdA² + sdB²)/3))",
    "then check: bootstrap over test cells, leave-top-3-out",
], size=15, font=MONO, after=8)
notes(s, "A gap must be about twice what seed luck alone produces. Why so strict: the next slide.")

# ---------------------------------------------------------------- 10 early results
s = new_slide()
tag(s, "OUR WORK · PHASE 0–1")
title(s, "EARLY SSL WINS WERE NOT REAL")
table(s, [
    ["Arm (20% labels, old masks)", "Test defect mIoU"],
    ["Supervised", "0.344"],
    ["Mean Teacher", "0.366"],
    ["Mean Teacher, loss off", "0.365"],
    ["ALHVR", "0.372"],
    ["ALHVR, loss off", "0.364"],
], 0.6, 1.8, 6.8, colw=[4.1, 2.7], size=18, rowh=0.58)
tb(s, 7.7, 1.9, 5.0, 3.4, [
    {"t": "The unlabelled losses did nothing", "bullet": True},
    {"t": "ALHVR loss reached full weight only at the last step", "bullet": True},
    {"t": "17 silent bugs, e.g. noise augmentation 16× too strong", "bullet": True},
], size=20, after=16)
bigline(s, "So we restarted: analysis first.", 0.6, 5.8, 12.1, size=28)
notes(s, "The loss-off controls scored the same as the SSL arms, so the gain did not come from learning on unlabelled data. The Mean Teacher loss used then (SemiCE) also marked every pixel positive for two or more classes.")

# ---------------------------------------------------------------- 11 diagnosis
s = new_slide()
tag(s, "OUR WORK · P1, P3, P14")
title(s, "DIAGNOSIS: LABELS AND RECIPE")
table(s, [
    ["Finding", "Number"],
    ["Blur + rotation, crack AP on train images", "0.93 → 0.59"],
    ["CE + Dice vs CE, crack fit IoU", "0.86 vs 0.68"],
    ["Rescore on revised labels", "+0.05 to +0.07"],
    ["Train on revised vs old labels", "+0.082"],
], 0.6, 1.8, 7.8, colw=[5.1, 2.7], size=18, rowh=0.66)
pic(s, "results/p1/zoom_crackpanel_A_CFVS_00031.png", 8.9, 1.5, 3.8, 3.8)
bigline(s, "The labels moved crack more than any SSL loss.", 0.6, 5.8, 12.1, size=26)
notes(s, "P1 overfit 10 images and found no pipeline bug: augmentation capped crack fitting. The Oct 2022 label revision joined dotted crack traces and widened them; training on it gives +0.082 crack IoU, robust.")

# ---------------------------------------------------------------- 12 probe 1
s = new_slide()
panel_left(s, "PROBE 1: PRETRAINED FEATURES")
tag(s, "OUR WORK · P4", x=5.4)
tb(s, 5.4, 0.95, 7.3, 0.4, "Frozen encoder + one linear layer, 47 labelled images", size=16, color=MUTED)
table(s, [
    ["Frozen encoder", "Crack AP", "Inactive AP"],
    ["Random", "0.03", "0.10"],
    ["ImageNet ResNet-50", "0.32", "0.42"],
    ["ImageNet ConvNeXt-T", "0.33", "0.38"],
    ["DINOv2 ViT-S", "0.18", "0.38"],
    ["Our old encoder (all 478 labels)", "0.24", "0.27"],
], 5.4, 1.55, 7.3, colw=[3.9, 1.7, 1.7], size=18, rowh=0.6)
bigline(s, "ImageNet CNN features beat our own trained encoder.", 5.4, 5.55, 7.3, size=24, h=1.1)
notes(s, "This led to the ImageNet ResNet-34 encoder in our baseline, and to CNN over ViT for thin cracks.")

# ---------------------------------------------------------------- 13 probe 2
s = new_slide()
tag(s, "OUR WORK · P5")
title(s, "PROBE 2: RIGHT CRACK, WRONG PIXELS")
table(s, [
    ["Crack pseudo-labels", "Strict", "Within 2 px"],
    ["Both unsure (72% of crack)", "0.27", "0.64"],
    ["Confidence ≥ 0.95 (8%)", "0.59", "0.96"],
], 0.6, 1.9, 6.9, colw=[3.9, 1.3, 1.7], size=18, rowh=0.8)
pic(s, "results/p5_region_pl/fig_p5_offset.png", 7.9, 1.8, 4.8, 3.6)
bigline(s, "Pseudo-labels find the crack, not its exact pixels.", 0.6, 5.8, 12.1, size=26)
notes(s, "This motivated the tolerant pseudo-label: the student gets credit for predicting crack anywhere within 2 px of the teacher crack.")

# ---------------------------------------------------------------- 14 baseline
s = new_slide()
tag(s, "OUR WORK · P6")
title(s, "A FAIR SUPERVISED BASELINE")
table(s, [
    ["Recipe (10% labels)", "Crack IoU", "Inact. IoU", "F1 ±2 px"],
    ["L0 old recipe", "0.319", "0.439", "0.746"],
    ["L1 + label-safe augmentation", "0.368", "0.473", "0.806"],
    ["L2 + ImageNet encoder", "0.392", "0.383", "0.806"],
    ["L3 + CE + Dice", "0.396", "0.294", "0.814"],
], 0.6, 1.8, 8.1, colw=[3.6, 1.5, 1.5, 1.5], size=17, rowh=0.66)
table(s, [
    ["10→100%", "Crack", "Inact."],
    ["L0", "+0.017", "−0.048"],
    ["L3", "+0.075", "+0.135"],
], 9.1, 1.8, 3.6, colw=[1.4, 1.1, 1.1], size=17, rowh=0.66)
bigline(s, "SSL can only close a gap that exists.", 0.6, 5.8, 12.1, size=28)
notes(s, "L3 became the baseline for all SSL work. Open issue: L3 costs inactive at 10% labels. The L1 inactive number rests on 3 test cells.")

# ---------------------------------------------------------------- 15 handicap
s = new_slide()
panel_left(s, "A HIDDEN HANDICAP")
tag(s, "OUR WORK · P8", x=5.4)
table(s, [
    ["10% labels", "Crack IoU", "Inact. IoU", "F1 ±2 px"],
    ["Supervised", "0.396", "0.294", "0.814"],
    ["SSL pipeline, loss off", "0.383", "0.194", "0.796"],
    ["Hard pseudo-labels", "0.389", "0.219", "0.806"],
    ["Tolerant pseudo-labels", "0.392", "0.253", "0.811"],
], 5.4, 1.25, 7.3, colw=[3.1, 1.4, 1.4, 1.4], size=17, rowh=0.66)
bigline(s, "With the loss switched off, SSL was worse than supervised.", 5.4, 5.0, 7.3, size=26, h=1.3)
notes(s, "F1 ±2 px: a predicted crack pixel counts if it lies within 2 px of a labelled crack pixel, and vice versa. No loss passed. A 28 times larger unlabelled pool (P9) and fewer labels (P10) did not change that.")

# ---------------------------------------------------------------- 16 tracing
s = new_slide()
tag(s, "OUR WORK · P11, P12, AUDIT")
title(s, "TRACING THE HANDICAP")
table(s, [
    ["Fix: labelled images get the supervised augmentation", "Loss vs its control", "SSL vs supervised", "Left-over crack handicap"],
    ["10% labels", "passes", "passes", "−0.007"],
    ["5% labels", "passes", "fails", "−0.017"],
], 0.6, 1.8, 12.1, colw=[4.9, 2.4, 2.4, 2.4], size=18, rowh=0.72)
tb(s, 0.6, 4.25, 12.1, 1.3, [
    {"t": "Recomputing BatchNorm statistics after training did not help: the damage is in the weights", "bullet": True},
    {"t": "Last suspect: labelled and unlabelled images sharing BatchNorm", "bullet": True},
], size=19, after=12)
bigline(s, "At 5%, the handicap ate the gain.", 0.6, 5.85, 12.1, size=28)
notes(s, "At 5%, the loss beat its control by +0.023 crack, but the control sat 0.017 below supervised, so the net gain was only +0.006.")

# ---------------------------------------------------------------- 17 fix
s = new_slide()
tag(s, "OUR WORK · P13")
title(s, "THE FIX: SEPARATE BATCHNORM + CUTMIX")
table(s, [
    ["5% labels, 5 seeds", "Crack IoU", "Inact. IoU", "F1 ±2 px"],
    ["Supervised 5%", "0.304", "0.253", "0.720"],
    ["SSL, tolerant PL", "0.317", "0.370", "0.752"],
    ["SSL, hard PL", "0.333", "0.360", "0.764"],
    ["Supervised 10% (reference)", "0.396", "0.294", "0.814"],
    ["Supervised 100% (reference)", "0.471", "0.429", "0.876"],
], 0.6, 1.75, 8.1, colw=[3.5, 1.4, 1.5, 1.7], size=16, rowh=0.52)
tb(s, 9.0, 1.9, 3.7, 2.6, [
    {"t": "SSL beats supervised at 5%", "font": HEAD, "size": 22, "after": 10},
    {"t": "inactive +0.117, robust over test cells", "size": 17, "after": 6},
    {"t": "5% + SSL beats 10% supervised on inactive", "size": 17, "color": MUTED},
])
pic(s, "results/p13/fig_p13_bars.png", 0.6, 5.1, 12.1, 1.8)
notes(s, "Separate forward: labelled and unlabelled images go through BatchNorm separately. CutMix gives a stronger perturbation. Crack IoU is not detectably better with tolerant PL; hard PL gives +0.029 with 5 seeds.")

# ---------------------------------------------------------------- 18 qualitative
s = new_slide()
rect(s, 9.4, 0, 3.933, 7.5, fill=PANEL)
tb(s, 9.85, 0.42, 3.2, 0.3, [{"t": "OUR WORK", "spc": 250}], size=12, bold=True, color=SOFT)
tb(s, 9.85, 1.0, 3.1, 3.0, "WHAT IT LOOKS LIKE", size=32, font=HEAD, color=WHITE, anchor="m")
tb(s, 9.85, 4.5, 3.1, 2.4, [
    {"t": "One cell: inactive IoU 0.28 supervised, 0.62 to 0.69 SSL", "after": 12},
    "Largest inactive cell: every model misses it",
], size=15, color=PANEL_MUTED)
pic(s, "results/qualitative/fig_qualitative_5pct.png", 0.45, 0.5, 8.6, 6.4)
notes(s, "Supervised 5%, SSL tolerant, SSL hard, supervised 100%, seed 3, on the two largest-inactive and two largest-crack test cells, chosen by ground-truth area before looking at predictions.")

# ---------------------------------------------------------------- 19 other ideas
s = new_slide()
tag(s, "OUR WORK · P14, P15, P17")
title(s, "OTHER IDEAS WE TESTED")
table(s, [
    ["Idea", "Result"],
    ["Tolerant loss on human labels", "recovers 0% of the old-vs-revised label gap"],
    ["Encoder pretrained on UCF-EL instead of ImageNet", "equal at 5%, worse at 10%"],
    ["Separate decoder for pseudo-labels (SKCDF-style)", "same as without: the gain enters through the encoder"],
], 0.6, 1.8, 12.1, colw=[5.4, 6.7], size=19, rowh=0.8, align=["l", "l"])
bigline(s, "Failed ideas, clear reasons.", 0.6, 5.6, 12.1, size=30)
notes(s, "UCF crack labels are 9 to 15 px wide against our 2 px, a likely reason the transfer failed (untested). Self-supervised pretraining is still untested.")

# ---------------------------------------------------------------- 20 more labels, unseen modules
s = new_slide()
tag(s, "OUR WORK · P16, P18, E1")
title(s, "MORE LABELS, AND UNSEEN MODULES")
tb(s, 0.6, 1.75, 5.6, 0.4, "SSL minus supervised", size=16, color=MUTED)
table(s, [
    ["Labels", "Crack IoU", "Inactive IoU"],
    ["5%", "+0.007", "+0.109"],
    ["20%", "+0.002", "+0.029"],
    ["50%", "+0.002", "+0.002"],
    ["100%", "−0.002", "+0.002"],
], 0.6, 2.2, 5.8, colw=[1.6, 2.1, 2.1], size=18, rowh=0.56)
tb(s, 6.9, 1.75, 5.8, 0.4, "Crack IoU on unseen modules (106 cells, 67 modules)", size=16, color=MUTED)
table(s, [
    ["Model", "Test", "Unseen"],
    ["Supervised 100%", "0.471", "0.152"],
    ["Supervised 10%", "0.396", "0.080"],
], 6.9, 2.2, 5.8, colw=[3.0, 1.4, 1.4], size=18, rowh=0.56)
bigline(s, "SSL helps most when labels are scarce.", 0.6, 5.45, 12.1, size=24, h=0.5)
bigline(s, "Test scores overstate field performance.", 0.6, 6.05, 12.1, size=24, h=0.5)
notes(s, "Noisy test cell removed in the first table. P18 (exploratory) shows the hard-PL recipe still gains inactive at 10% (+0.132) and 20% (+0.060). On unseen modules SSL lifts inactive cell IoU from 0.03 to 0.50.")

# ---------------------------------------------------------------- 21 where we stand
s = new_slide()
tag(s, "OUR WORK")
title(s, "WHERE WE STAND")
tb(s, 0.6, 1.65, 12.1, 0.4, "In the Pratt 2023 convention (median IoU per image)", size=16, color=MUTED)
table(s, [
    ["Model", "Crack", "Gridline", "Inactive", "Mean"],
    ["Pratt 2023 headline", "0.25", "0.20", "0.38", "0.28"],
    ["Ours, supervised 100%", "0.354", "0.303", "0.443", "0.367"],
    ["Ours, SSL 5%", "0.194", "0.173", "0.352", "0.239"],
    ["Ours, supervised 5%", "0.193", "0.147", "0.160", "0.167"],
], 0.6, 2.1, 8.5, colw=[3.3, 1.3, 1.3, 1.3, 1.3], size=17, rowh=0.54)
tb(s, 9.5, 2.1, 3.2, 3.0, [
    {"t": "Not claimed yet", "bold": True, "size": 19, "after": 10},
    {"t": "SSL improves crack in general", "bullet": True, "after": 6},
    {"t": "SSL helps above 10% (confirmed)", "bullet": True, "after": 6},
    {"t": "State of the art", "bullet": True},
], size=17)
tb(s, 0.6, 4.95, 12.1, 0.4, "Rule inferred, Pratt numbers read from his figure, our models trained on revised masks. One split, 50 test cells.", size=13, color=MUTED)
bigline(s, "Labels and recipe outweigh the unlabelled loss.", 0.6, 5.85, 12.1, size=26)
notes(s, "What we learned: labels and recipe matter most; always run the loss-off control; with the BatchNorm fix, SSL helps at 5%, mostly on inactive; every model drops sharply on unseen modules.")

# ---------------------------------------------------------------- 22 next steps
s = new_slide()
tag(s, "NEXT")
title(s, "NEXT STEPS")
table(s, [
    ["Step", "Why"],
    ["Add 233 extra labelled cells, keep the same 50 test cells", "labels are the biggest lever"],
    ["Pretraining comparison, incl. self-supervised (MIM)", "needed for a fair SOTA claim"],
    ["Recent SSL methods: DCA, SKCDF, CGS, UniMatch V2, a fair ALHVR run", "beyond Mean Teacher"],
    ["One-protocol baselines: reproduce SEiPV-Net, run Hanifi 2025 code", "comparable numbers"],
    ["Locked test of the best SSL recipe at 20 to 50% labels", "P18 was exploratory"],
    ["Report gridline as a third class", "comparable with Pratt"],
    ["Diagnose the unseen-module drop", "field use"],
], 0.6, 1.7, 12.1, colw=[8.6, 3.5], size=17, rowh=0.58, align=["l", "l"])
tb(s, 0.6, 6.7, 12.1, 0.4, "Then part 2 (architecture) and part 3 (deployment, severity)", size=16, color=MUTED)
notes(s, "DCA: CVPR 2026. SKCDF: CVPR 2025 (only its decoupling was tried in P17). CGS: TMI 2025. UniMatch V2: TPAMI 2025. Hanifi 2025 has public code on the 29-class release.")

# ---------------------------------------------------------------- 23 thank you
s = new_slide(number=False)
tb(s, 0.8, 5.3, 11.0, 1.2, "THANK YOU", size=54, font=HEAD)
tb(s, 0.8, 6.45, 11.0, 0.4, "Questions", size=18, color=MUTED)

# ---------------------------------------------------------------- backups
s = new_slide()
tag(s, "BACKUP")
title(s, "THE PASS RULE, WORKED (P13 INACTIVE)")
table(s, [
    ["Step", "Value"],
    ["Mean gap, SSL minus supervised (5 vs 5 seeds)", "+0.117"],
    ["Seed spread, supervised / SSL", "0.037 / 0.026"],
    ["Bar = max(0.01, 2·√((0.037² + 0.026²)/3))", "0.052"],
    ["Verdict", "passes"],
    ["Bootstrap over test cells, 95% interval", "[+0.042, +0.189]"],
    ["Without the 3 largest-inactive cells", "+0.103"],
], 0.6, 1.9, 9.6, colw=[6.6, 3.0], size=16, rowh=0.52)

s = new_slide()
tag(s, "BACKUP")
title(s, "ONE NOISY TEST CELL")
table(s, [
    ["CSIR_00070_r8_c4", ""],
    ["Runs that call 15 to 31% of it crack", "4 of 24 (2 supervised, 2 SSL)"],
    ["False crack pixels vs true crack", "39k to 80k vs 787"],
    ["Image noise level vs median cell", "46 vs 1.5"],
    ["Verdicts without it", "unchanged"],
], 0.6, 1.9, 10.4, colw=[5.4, 5.0], size=16, rowh=0.55, align=["l", "l"])

s = new_slide()
tag(s, "BACKUP")
title(s, "E-SCDD AUDIT")
table(s, [
    ["Finding", "Number"],
    ["Files in the release", "903 = 693 + 117 new real + 93 synthetic"],
    ["Crack or inactive pixels changed by E-SCDD", "0"],
    ["Our 50 test cells inside its train split", "39"],
    ["Real labelled cells new to us", "233"],
], 0.6, 1.9, 10.4, colw=[5.4, 5.0], size=16, rowh=0.55, align=["l", "l"])

s = new_slide()
tag(s, "BACKUP")
title(s, "P17: DECOUPLED DECODER")
table(s, [
    ["5% labels, 5 seeds", "Crack IoU", "Inactive IoU", "F1 ±2 px"],
    ["Supervised", "0.304", "0.253", "0.720"],
    ["SSL, hard PL (BsM5)", "0.333", "0.360", "0.764"],
    ["Same, decoupled decoder (BsD5)", "0.327", "0.371", "0.756"],
], 0.6, 1.9, 10.4, colw=[4.4, 2.0, 2.0, 2.0], size=16, rowh=0.55)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("saved", OUT, "slides", len(prs.slides))
