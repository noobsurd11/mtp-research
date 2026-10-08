"""Q3 geometry, label margin vs visible crack, Q4 metric ceiling, Q5 contact-rectangle content.

A. Per released image (native and resized to shorter side 295, nearest): crack components (area, skeleton length,
   width = area / skeleton length, median 2*EDT-1 on the skeleton), contact / interconnect / corrosion component areas.
B. Per CSV crack region (rasterised alone, native): subtype, area, width.  For Crack_Closed regions: at skeleton points
   of the polygon, the image profile along the normal (+-10 px, image smoothed sigma 0.7): visible dip FWHM, label
   extent along the same normal, and the offset of the darkest point from the label centre.
C. Dataset-level IoU of each class with a 1 px shifted / dilated / eroded copy of itself (test + every 4th train
   image), at 295 and native resolution.
D. Contact rectangles: share of rectangle pixels darker than 0.9 x the median of a 3 px ring around it.

Usage: python -I ucf_geometry.py <UCF root> <out.json>
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import CLASSES, dump, pairs  # noqa: E402

root, out = Path(sys.argv[1]), Path(sys.argv[2])
SQ = np.ones((3, 3), bool)
CROSS = ndi.generate_binary_structure(2, 1)
T = np.arange(-10, 10.0001, 0.25)
rows = collections.defaultdict(list)
for r in csv.DictReader(open(root / "AnnotationsCombined.csv", newline="")):
    rows[r["filename"]].append(r)


def shift(a, dy, dx):
    o = np.zeros_like(a)
    H, W = a.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    o[yd, xd] = a[ys, xs]
    return o


PERT = {"shift1_mean4": lambda b: [shift(b, *d) for d in ((1, 0), (-1, 0), (0, 1), (0, -1))],
        "shift1_diag": lambda b: [shift(b, 1, 1)],
        "shift2_mean4": lambda b: [shift(b, *d) for d in ((2, 0), (-2, 0), (0, 2), (0, -2))],
        "dilate1_sq": lambda b: [ndi.binary_dilation(b, SQ)],
        "erode1_cross": lambda b: [ndi.binary_erosion(b, CROSS)]}


def comps(mask):
    lab, n = ndi.label(mask, SQ)
    if n == 0:
        return []
    sk = skeletonize(mask)
    edt = ndi.distance_transform_edt(mask)
    outl = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        c = lab[sl] == i
        s = sk[sl] & c
        L = max(int(s.sum()), 1)
        d = edt[sl][s] if s.any() else edt[sl][c]
        outl.append((int(c.sum()), L, float(c.sum() / L), float(np.median(2 * d - 1))))
    return outl


def draw(sh, w, h):
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    if sh["name"] == "polygon" and len(sh["all_points_x"]) >= 3:
        d.polygon(list(zip(sh["all_points_x"], sh["all_points_y"])), fill=1)
    elif sh["name"] == "rect":
        d.rectangle([sh["x"], sh["y"], sh["x"] + sh["width"] - 1, sh["y"] + sh["height"] - 1], fill=1)
    else:
        return None
    return np.asarray(im, bool)


def tangent(skel, y, x, r=3):
    H, W = skel.shape
    win = skel[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
    py, px = np.nonzero(win)
    if len(py) < 4:
        return None
    ev, evec = np.linalg.eigh(np.cov(np.vstack([py, px]).astype(float)))
    if ev[-1] < 2 * max(ev[0], 1e-9):
        return None
    return evec[:, -1]


def work(job):
    s, n, a, k = job
    m = np.asarray(Image.open(root / "training/data" / s / "annotations" / a))
    img = np.asarray(Image.open(root / "training/data" / s / "images" / n).convert("L"), np.float32)
    h, w = m.shape
    sc = 295 / min(h, w)
    m295 = np.asarray(Image.fromarray(m).resize((round(w * sc), round(h * sc)), Image.NEAREST))
    res = {"split": s, "scale295": sc,
           "crack_native": comps(m == 1), "crack_295": comps(m295 == 1),
           "area_native": {c: [x[0] for x in comps(m == c)] for c in (2, 3, 4)} if k % 2 == 0 else None}
    # C: ceiling (test + every 4th train)
    if s == "test" or k % 4 == 0:
        ce = {}
        for tag, mm in (("295", m295), ("native", m)):
            for c in (1, 2, 3, 4):
                g = mm == c
                if not g.any():
                    continue
                for p, f in PERT.items():
                    I = U = 0
                    for b in f(g):
                        I += int((g & b).sum()); U += int((g | b).sum())
                    ce[f"{tag}|{c}|{p}"] = (I, U)
        res["ceiling"] = ce
    # B and D: regions
    reg, prof, cont = [], [], []
    img_s = ndi.gaussian_filter(img, 0.7)
    for r in rows[n]:
        if r["region_shape_attributes"] in ("", "{}"):
            continue
        sh = json.loads(r["region_shape_attributes"])
        cls = json.loads(r["region_attributes"] or "{}").get("Defect_Class", "")
        if cls.startswith("Crack_"):
            b = draw(sh, w, h)
            if b is None or not b.any():
                continue
            cs = comps(b)
            if not cs:
                continue
            area, L, wid, wedt = max(cs, key=lambda t: t[0])
            reg.append((cls, area, L, wid, wedt))
            if cls == "Crack_Closed" and len(prof) < 40:
                sk = skeletonize(b)
                edt = ndi.distance_transform_edt(b)
                ys, xs = np.nonzero(sk)
                for i in range(0, len(ys), 4):
                    y, x = ys[i], xs[i]
                    t = tangent(sk, y, x)
                    if t is None:
                        continue
                    nrm = np.array([-t[1], t[0]])
                    cy, cx = y + T * nrm[0], x + T * nrm[1]
                    p = ndi.map_coordinates(img_s, [cy, cx], order=1, mode="nearest")
                    inl = ndi.map_coordinates(b.astype(np.float32), [cy, cx], order=0, mode="constant")
                    if inl.sum() == 0:
                        continue
                    half = inl.sum() * 0.25 / 2  # label extent along the normal (px), / 2
                    base = np.median(np.r_[p[np.abs(T) >= 8]])
                    win = np.abs(T) <= half + 1.5
                    jmin = np.argmin(np.where(win, p, np.inf))
                    pmin = p[jmin]
                    depth = (base - pmin) / max(base, 1)
                    if depth < 0.03:
                        prof.append((float(inl.sum() * 0.25), None, None, float(depth)))
                        continue
                    thr = (base + pmin) / 2
                    lo = jmin
                    while lo > 0 and p[lo - 1] < thr:
                        lo -= 1
                    hi = jmin
                    while hi < len(p) - 1 and p[hi + 1] < thr:
                        hi += 1
                    prof.append((float(inl.sum() * 0.25), float((hi - lo + 1) * 0.25), float(T[jmin]), float(depth)))
        elif cls in ("Contact_FrontGridInterruption", "Contact_NearSolderPad") and sh["name"] == "rect" and len(cont) < 30:
            b = draw(sh, w, h)
            if b is None or b.sum() < 6:
                continue
            ring = ndi.binary_dilation(b, SQ, iterations=3) & ~b & (m == 0)
            if ring.sum() < 10:
                continue
            bg = float(np.median(img[ring]))
            cont.append((int(b.sum()), float((img[b] < 0.9 * bg).mean()), float(np.median(img[b]) / max(bg, 1))))
    res["regions"], res["profiles"], res["contact"] = reg, prof, cont
    return res


if __name__ == "__main__":
    jobs = [(s, n, a, k) for s in ("train", "test") for k, (n, a) in enumerate(pairs(root, s))]
    with Pool(14) as pool:
        R = pool.map(work, jobs, chunksize=40)
    o = {}
    for sp in ("train", "test"):
        rs = [r for r in R if r["split"] == sp]
        for tag in ("native", "295"):
            cc = [c for r in rs for c in r[f"crack_{tag}"]]
            A = np.array(cc) if cc else np.zeros((0, 4))
            big = A[A[:, 1] >= 15] if len(A) else A
            o[f"{sp}_crack_{tag}"] = {
                "components": len(A), "share_lt20px": float((A[:, 0] < 20).mean()),
                "width_area_over_len_lenweighted": float((big[:, 2] * big[:, 1]).sum() / big[:, 1].sum()),
                "width_edt_median_q": np.quantile(big[:, 3], [.25, .5, .75]).tolist(),
                "area_q": np.quantile(A[:, 0], [.25, .5, .75, .9]).tolist()}
        if sp == "train":
            for c in (2, 3, 4):
                v = [x for r in rs if r["area_native"] for x in r["area_native"][c]]
                o[f"train_{CLASSES[c]}_component_area_native_q"] = (np.quantile(v, [.1, .5, .9]).tolist() if v else None, len(v))
        reg = [x for r in rs for x in r["regions"]]
        for cls in ("Crack_Closed", "Crack_Resistive", "Crack_Isolated"):
            v = np.array([x[1:] for x in reg if x[0] == cls])
            if len(v):
                o[f"{sp}_{cls}"] = {"n": len(v), "area_q": np.quantile(v[:, 0], [.1, .5, .9]).tolist(),
                                    "width_area_over_len_q": np.quantile(v[:, 2], [.1, .5, .9]).tolist(),
                                    "width_edt_q": np.quantile(v[:, 3], [.1, .5, .9]).tolist()}
        pr = [x for r in rs for x in r["profiles"]]
        vis = np.array([x for x in pr if x[1] is not None])
        o[f"{sp}_closed_crack_profiles"] = {
            "points": len(pr), "with_dip_gt3pct": len(vis),
            "label_extent_q": np.quantile([x[0] for x in pr], [.25, .5, .75]).tolist(),
            "visible_fwhm_q": np.quantile(vis[:, 1], [.25, .5, .75]).tolist(),
            "margin_per_side_q": np.quantile((vis[:, 0] - vis[:, 1]) / 2, [.1, .25, .5, .75, .9]).tolist(),
            "darkest_offset_abs_le1": float((np.abs(vis[:, 2]) <= 1).mean()),
            "darkest_offset_abs_le2": float((np.abs(vis[:, 2]) <= 2).mean()),
            "dip_depth_median": float(np.median(vis[:, 3]))}
        ct = np.array([x for r in rs for x in r["contact"]])
        o[f"{sp}_contact_rect"] = {"n": len(ct), "area_q": np.quantile(ct[:, 0], [.1, .5, .9]).tolist(),
                                   "dark_share_q": np.quantile(ct[:, 1], [.1, .25, .5, .75, .9]).tolist(),
                                   "median_ratio_inside_vs_ring_q": np.quantile(ct[:, 2], [.1, .5, .9]).tolist(),
                                   "share_rects_with_dark_lt_10pct": float((ct[:, 1] < 0.1).mean())}
        acc = collections.defaultdict(lambda: [0, 0])
        for r in rs:
            for kk, (I, U) in r.get("ceiling", {}).items():
                acc[kk][0] += I; acc[kk][1] += U
        o[f"{sp}_ceiling"] = {kk: round(I / U, 4) for kk, (I, U) in sorted(acc.items())}
    dump(o, out)
    print(json.dumps(o, indent=1)[:9000])
