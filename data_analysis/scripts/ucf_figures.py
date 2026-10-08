"""Figures for the UCF-EL report: class overlays, twin re-annotation pairs, crack subtypes.

Usage: python -I ucf_figures.py <UCF root> <out dir> <figs dir>
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import pairs  # noqa: E402

root, od, figs = (Path(x) for x in sys.argv[1:4])
COL = {1: (255, 40, 40), 2: (255, 220, 0), 3: (0, 230, 255), 4: (255, 0, 255), 128: (150, 150, 150)}
per = json.load(open(od / "ucf_per_image.json"))["per_image"]
rng = np.random.default_rng(1)


def panel(s, n, a, size=230, outline=True):
    img = np.asarray(Image.open(root / "training/data" / s / "images" / n).convert("L"))
    m = np.asarray(Image.open(root / "training/data" / s / "annotations" / a))
    rgb = np.stack([img] * 3, -1).copy()
    for c, col in COL.items():
        b = m == c
        if not b.any():
            continue
        e = b & ~ndi.binary_erosion(b) if outline else b
        rgb[e] = col
    k = size / max(img.shape)
    im = Image.fromarray(rgb).resize((round(img.shape[1] * k), round(img.shape[0] * k)), Image.NEAREST)
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    canvas.paste(im, (0, 0))
    return np.asarray(canvas), np.asarray(Image.fromarray(np.stack([img] * 3, -1)).resize(im.size).crop((0, 0, size, size)))


def grid(tiles, cols, pad=4):
    h, w = tiles[0].shape[:2]
    rows = []
    for i in range(0, len(tiles), cols):
        row = tiles[i:i + cols] + [np.full_like(tiles[0], 255)] * (cols - len(tiles[i:i + cols]))
        rows.append(np.hstack([np.hstack([t, np.full((h, pad, 3), 255, np.uint8)]) for t in row]))
    return np.vstack([np.vstack([r, np.full((pad, r.shape[1], 3), 255, np.uint8)]) for r in rows])


ann = {n: (s, a) for s in ("train", "test") for n, a in pairs(root, s)}
# 1) overlays: 24 images: 6 crack-heavy, 6 contact-only, 4 interconnect, 4 corrosion, 2 ignore-heavy, 2 named-session
sel = collections.OrderedDict()
cands = {
    "crack": [n for n, p in per.items() if p["px"][1] > 3000],
    "contact": [n for n, p in per.items() if p["px"][2] > 0 and p["px"][1] == 0],
    "interconnect": [n for n, p in per.items() if p["px"][3] > 0],
    "corrosion": [n for n, p in per.items() if p["px"][4] > 0],
    "ignore": [n for n, p in per.items() if p["px"][5] > 5000],
    "named": [n for n, p in per.items() if p["family"].startswith("named") and (p["px"][1] + p["px"][2]) > 0]}
for k, q in (("crack", 6), ("contact", 6), ("interconnect", 4), ("corrosion", 4), ("ignore", 2), ("named", 2)):
    for n in rng.choice(cands[k], q, replace=False):
        sel[n] = k
tiles, labels = [], []
for n, k in sel.items():
    s, a = ann[n]
    o, raw = panel(s, n, a)
    tiles += [raw, o]
    labels.append(f"{k}: {s}/{n}")
Image.fromarray(grid(tiles, 8)).save(figs / "ucf_class_overlays.png")
(figs / "ucf_class_overlays.txt").write_text("pairs (raw | outline) left to right, top to bottom; red crack, yellow contact, cyan interconnect, "
                                              "magenta corrosion, grey ignore 128\n" + "\n".join(labels))

# 2) twin re-annotation pairs (tier A, near-identical)
det = json.load(open(od / "ucf_twins_detail_tierA.json"))
ex = det["examples"][:6]
tiles = []
lab2 = []
for sa, n, aa, sb, t, ab, dy, dx, ncc in ex:
    o1, _ = panel(sa, n, aa, outline=False)
    o2, _ = panel(sb, t, ab, outline=False)
    tiles += [o1, o2]
    lab2.append(f"{sa}/{n} | {sb}/{t} (NCC {ncc:.2f}, shift {dy},{dx})")
if tiles:
    Image.fromarray(grid(tiles, 4)).save(figs / "ucf_twin_reannotation.png")
    (figs / "ucf_twin_reannotation.txt").write_text("filled masks of the same physical cell in two images; " + "\n".join(lab2))

# 3) crack subtypes: one image dominated by each subtype, outline of each subtype in its own colour
rows = collections.defaultdict(list)
for r in csv.DictReader(open(root / "AnnotationsCombined.csv", newline="")):
    rows[r["filename"]].append(r)
subcol = {"Crack_Closed": (255, 40, 40), "Crack_Resistive": (255, 140, 0), "Crack_Isolated": (0, 255, 0)}
tiles, lab3 = [], []
for sub in subcol:
    cand = [n for n in ann if any(json.loads(r["region_attributes"] or "{}").get("Defect_Class") == sub for r in rows[n])]
    for n in rng.choice(cand, 2, replace=False):
        s, a = ann[n]
        img = np.asarray(Image.open(root / "training/data" / s / "images" / n).convert("L"))
        rgb = np.stack([img] * 3, -1).copy()
        for r in rows[n]:
            c = json.loads(r["region_attributes"] or "{}").get("Defect_Class")
            if c in subcol:
                sh = json.loads(r["region_shape_attributes"])
                im = Image.new("L", img.shape[::-1], 0)
                d = ImageDraw.Draw(im)
                if sh["name"] == "polygon":
                    d.polygon(list(zip(sh["all_points_x"], sh["all_points_y"])), outline=1)
                elif sh["name"] == "rect":
                    d.rectangle([sh["x"], sh["y"], sh["x"] + sh["width"], sh["y"] + sh["height"]], outline=1)
                rgb[np.asarray(im, bool)] = subcol[c]
        k = 260 / max(img.shape)
        t = np.asarray(Image.fromarray(rgb).resize((round(img.shape[1] * k), round(img.shape[0] * k))))
        c2 = np.full((260, 260, 3), 255, np.uint8)
        c2[:t.shape[0], :t.shape[1]] = t
        tiles.append(c2)
        lab3.append(f"{sub}: {s}/{n}")
Image.fromarray(grid(tiles, 6)).save(figs / "ucf_crack_subtypes.png")
(figs / "ucf_crack_subtypes.txt").write_text("CSV polygon outlines: red Closed, orange Resistive, green Isolated\n" + "\n".join(lab3))
print("\n".join(labels + lab2 + lab3))
