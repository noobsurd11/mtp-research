"""Q0 provenance: how the released UCF-EL masks relate to the VIA CSV regions.

1. For every region of every released image: rasterise the region alone and record the released mask values inside
   it -> per fine VIA class, the distribution of mask values (the class mapping) and how fully the region is covered.
2. Rebuild whole masks from the CSV with that mapping (CSV row order, later regions overwrite earlier ones) and
   compare with the released masks per class, also after shifting / dilating / eroding the rebuilt mask by 1 px
   (detects a systematic rasterisation offset or margin).
3. Flag code of the M####C###XYZ names against the classes present.

Usage: python -I ucf_provenance.py <UCF root> <out.json>
"""

from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import IGNORE, dump, pairs  # noqa: E402

root, out = Path(sys.argv[1]), Path(sys.argv[2])
rows = collections.defaultdict(list)
for r in csv.DictReader(open(root / "AnnotationsCombined.csv", newline="")):
    rows[r["filename"]].append(r)


def draw_region(shape: dict, size: tuple[int, int]) -> np.ndarray | None:
    w, h = size
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    n = shape.get("name")
    if n == "rect":
        x, y, ww, hh = shape["x"], shape["y"], shape["width"], shape["height"]
        d.rectangle([x, y, x + ww, y + hh], fill=1)
    elif n == "polygon":
        pts = list(zip(shape["all_points_x"], shape["all_points_y"]))
        if len(pts) < 3:
            return None
        d.polygon(pts, fill=1)
    elif n == "circle":
        cx, cy, r = shape["cx"], shape["cy"], shape["r"]
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=1)
    elif n == "ellipse":
        cx, cy, rx, ry = shape["cx"], shape["cy"], shape["rx"], shape["ry"]
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=1)
    else:
        return None
    return np.asarray(im, dtype=bool)


def regions(name: str) -> list[tuple[str, dict]]:
    out = []
    for r in rows[name]:
        s, a = r["region_shape_attributes"], r["region_attributes"]
        if s in ("", "{}"):
            continue
        out.append((json.loads(a or "{}").get("Defect_Class", "None"), json.loads(s)))
    return out


rel = [(s, n, a) for s in ("train", "test") for n, a in pairs(root, s)]
# pass 1: mapping
val_hist = collections.defaultdict(collections.Counter)      # fine class -> mask value -> pixels
maj_hist = collections.defaultdict(collections.Counter)      # fine class -> majority value -> regions
shape_hist = collections.defaultdict(collections.Counter)
region_px = collections.defaultdict(list)
oob = 0
for s, n, a in rel:
    m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
    h, w = m.shape
    for cls, sh in regions(n):
        shape_hist[cls][sh.get("name")] += 1
        r = draw_region(sh, (w, h))
        if r is None or not r.any():
            oob += 1
            continue
        v, c = np.unique(m[r], return_counts=True)
        for x, y in zip(v, c):
            val_hist[cls][int(x)] += int(y)
        maj_hist[cls][int(v[np.argmax(c)])] += 1
        region_px[cls].append(int(r.sum()))
mapping = {}
for cls, hist in maj_hist.items():
    mapping[cls] = hist.most_common(1)[0][0]
res = {"n_release": len(rel), "regions_empty_or_out_of_image": oob,
       "mapping_majority_value": mapping,
       "region_majority_value_counts": {k: dict(v) for k, v in maj_hist.items()},
       "pixel_value_share_inside_regions": {k: {str(x): round(y / sum(v.values()), 4) for x, y in v.most_common()} for k, v in val_hist.items()},
       "shapes_per_class": {k: dict(v) for k, v in shape_hist.items()},
       "region_px_quantiles": {k: np.quantile(v, [.1, .5, .9]).tolist() for k, v in region_px.items()}}
print(json.dumps(res["mapping_majority_value"], indent=1))
print(json.dumps(res["pixel_value_share_inside_regions"], indent=1))


# pass 2: rebuild and compare (all images), with perturbations of the rebuilt mask
def shift(a: np.ndarray, dy: int, dx: int) -> np.ndarray:
    o = np.zeros_like(a)
    ys, yd = (slice(dy, None), slice(None, -dy)) if dy > 0 else ((slice(None, dy), slice(-dy, None)) if dy < 0 else (slice(None), slice(None)))
    xs, xd = (slice(dx, None), slice(None, -dx)) if dx > 0 else ((slice(None, dx), slice(-dx, None)) if dx < 0 else (slice(None), slice(None)))
    o[ys, xs] = a[yd, xd]
    return o


PERT = {"as_is": lambda b: b, "dilate1": lambda b: ndi.binary_dilation(b, np.ones((3, 3), bool)),
        "erode1": lambda b: ndi.binary_erosion(b, np.ones((3, 3), bool)),
        "shift_x+1": lambda b: shift(b, 0, 1), "shift_x-1": lambda b: shift(b, 0, -1),
        "shift_y+1": lambda b: shift(b, 1, 0), "shift_y-1": lambda b: shift(b, -1, 0)}
inter = collections.defaultdict(lambda: collections.Counter())
union = collections.defaultdict(lambda: collections.Counter())
agree = tot = 0
exact = 0
per_img_dis = []
for s, n, a in rel:
    m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
    h, w = m.shape
    rb = np.zeros((h, w), np.uint8)
    for cls, sh in regions(n):
        r = draw_region(sh, (w, h))
        if r is not None:
            rb[r] = mapping.get(cls, 0)
    agree += int((rb == m).sum())
    tot += m.size
    exact += int((rb == m).all())
    per_img_dis.append(float((rb != m).mean()))
    for c in (1, 2, 3, 4, IGNORE):
        gt = m == c
        b = rb == c
        if not gt.any() and not b.any():
            continue
        for k, f in PERT.items():
            bb = f(b)
            inter[c][k] += int((gt & bb).sum())
            union[c][k] += int((gt | bb).sum())
res["rebuild_pixel_agreement"] = agree / tot
res["rebuild_exact_images"] = exact
res["rebuild_per_image_disagreement_quantiles"] = np.quantile(per_img_dis, [.5, .9, .99, 1]).tolist()
res["rebuild_iou_per_class_and_perturbation"] = {str(c): {k: round(inter[c][k] / max(union[c][k], 1), 4) for k in PERT} for c in inter}
print(json.dumps(res["rebuild_iou_per_class_and_perturbation"], indent=1), res["rebuild_pixel_agreement"], exact)

# pass 3: flag code vs classes present
flag_cls = collections.defaultdict(collections.Counter)
flag_n = collections.Counter()
for s, n, a in rel:
    mm = re.match(r"^M(\d+)C(\d{3})(\d{3})\.", n)
    if not mm:
        continue
    f = mm[3]
    flag_n[f] += 1
    m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
    for c in (1, 2, 3, 4, IGNORE):
        flag_cls[f][c] += int((m == c).any())
res["flag_code_class_presence"] = {f: {"n": flag_n[f], **{str(c): round(flag_cls[f][c] / flag_n[f], 3) for c in (1, 2, 3, 4, IGNORE)}} for f in flag_n}
print(json.dumps(res["flag_code_class_presence"], indent=1))
dump(res, out)
