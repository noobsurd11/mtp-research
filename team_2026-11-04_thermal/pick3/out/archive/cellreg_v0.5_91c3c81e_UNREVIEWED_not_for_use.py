#!/usr/bin/env python3
"""cellreg.py: register EL, IR (and UVF) images of one PV module to a common cell grid.

Owner: ideas (pick 3), shared with datascout (pick 1, G0). CPU only. numpy / scipy / skimage / PIL.
Run with:  ~/mtp/research/.venv/bin/python -I scripts/cellreg.py ...   (never from inside a data folder)

Method (plan_pick3.md section 2):
 1. module quad: smooth, Otsu threshold, largest component, hull, 4 diagonal-extreme corners
 2. rectify with the corner homography to a canonical grid (cols x rows cells, S px per cell)
 3. cell grid: fit a uniform grid (offset, pitch) to the row / column profiles (gaps are extrema),
    then refine each line locally (+-0.15 pitch); polarity (dark or bright gaps) chosen by contrast
 4. refined homography: least squares from ideal intersections to detected intersections (image px)
 5. QA: RMS and max residual at intersections, also leave-one-point-out, as % of the median cell side
Features (plan sections 3.2, 3.3) are computed on each modality rectified with its refined homography.

Usage:
  single module:
    cellreg.py --module ID --grid 4x9 --el EL.tif --ir IR.txt [--uvf UVF.jpg] --out DIR
  batch (TSV with columns module, grid, el, ir, uvf; empty fields allowed):
    cellreg.py --manifest m.tsv --out DIR
  synthetic self-test (no data):
    cellreg.py --selftest --out DIR
"""
import argparse
import json
import os
import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import filters, measure, morphology, transform

VERSION = "cellreg 0.5 (4 Nov 2026): pitch searched +-2% in iteration 1 only (limits, does not prevent, drift); grid-vs-quad QA; --grid-ir uniform; transposed modality grids rejected; --orient; --quad full"
Image.MAX_IMAGE_PIXELS = None

# ----------------------------------------------------------------------------- readers

def _jpeg_candidates(buf):
    """Yield (start, end) of embedded JPEG streams (SOI ... EOI) in a byte buffer."""
    pos = 0
    while True:
        s = buf.find(b"\xff\xd8\xff", pos)
        if s < 0:
            return
        e = buf.find(b"\xff\xd9", s + 3)
        # a JPEG can contain nested thumbnails; take the last EOI before the next SOI
        nxt = buf.find(b"\xff\xd8\xff", s + 3)
        while e >= 0 and nxt >= 0 and e > nxt:
            e2 = buf.find(b"\xff\xd9", e + 2)
            if e2 < 0:
                break
            e = e2
            nxt = buf.find(b"\xff\xd8\xff", nxt + 3)
        if e < 0:
            return
        yield s, e + 2
        pos = s + 3


def read_nef_preview(path):
    """Largest decodable embedded JPEG in a Nikon NEF (no raw decoder installed)."""
    import io
    buf = open(path, "rb").read()
    best, best_px = None, 0
    for s, e in _jpeg_candidates(buf):
        if e - s < 50_000:
            continue
        try:
            im = Image.open(io.BytesIO(buf[s:e]))
            im.load()
        except Exception:
            continue
        px = im.size[0] * im.size[1]
        if px > best_px:
            best, best_px = im, px
    if best is None:
        raise ValueError(f"no decodable JPEG preview in {path}")
    arr = np.asarray(best.convert("L"), dtype=np.float32)
    return arr, {"reader": "nef_jpeg_preview", "shape": list(arr.shape),
                 "note": "8-bit camera-processed preview, tone-mapped, not linear"}


def read_image(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".nef":
        return read_nef_preview(path)
    if ext == ".txt":
        return read_matrix_txt(path)
    im = Image.open(path)
    meta = {"reader": f"PIL:{im.mode}", "shape": None}
    if im.mode in ("I;16", "I;16B", "I;16L", "I", "F"):
        arr = np.asarray(im, dtype=np.float32)
    elif im.mode in ("RGB", "RGBA", "P", "CMYK", "YCbCr", "LA"):
        arr = np.asarray(im.convert("L"), dtype=np.float32)
        meta["note"] = "converted to luminance (L)"
    else:
        arr = np.asarray(im, dtype=np.float32)
    if arr.ndim == 3:
        arr = arr.mean(axis=2)
    meta["shape"] = list(arr.shape)
    return arr, meta


_SPLIT = re.compile(r"[\s,;]+")


def read_matrix_txt(path):
    """Numeric matrix from text: tokens split on whitespace / comma / semicolon; non-numeric
    lines are skipped; rows whose length is not the modal length are dropped (reported)."""
    rows = []
    skipped = 0
    with open(path, "r", errors="replace") as f:
        for line in f:
            toks = [t for t in _SPLIT.split(line.strip()) if t]
            if not toks:
                continue
            vals = []
            ok = True
            for t in toks:
                try:
                    vals.append(float(t))
                except ValueError:
                    ok = False
                    break
            if ok:
                rows.append(vals)
            else:
                skipped += 1
    if not rows:
        raise ValueError(f"no numeric rows in {path}")
    lens = np.array([len(r) for r in rows])
    mode = int(np.bincount(lens).argmax())
    keep = [r for r in rows if len(r) == mode]
    arr = np.asarray(keep, dtype=np.float32)
    return arr, {"reader": "txt_matrix", "shape": list(arr.shape),
                 "header_lines_skipped": skipped, "rows_dropped_len": int((lens != mode).sum())}

# ----------------------------------------------------------------------------- geometry

def _norm(img):
    lo, hi = np.percentile(img, [1, 99])
    if hi <= lo:
        hi = lo + 1.0
    return np.clip((img - lo) / (hi - lo), 0, 1)


def find_quad(img, invert=False, maxdim=1000):
    """Four module corners (x, y) ordered TL, TR, BR, BL, from the largest bright component.
    Computed on a copy downsampled to <= maxdim px (speed), corners scaled back."""
    k = max(1, int(np.ceil(max(img.shape) / maxdim)))
    if k > 1:
        H, W = (img.shape[0] // k) * k, (img.shape[1] // k) * k
        small = img[:H, :W].reshape(H // k, k, W // k, k).mean(axis=(1, 3))
        q, info = find_quad(small, invert=invert, maxdim=maxdim)
        q = (q + 0.5) * k - 0.5
        info["downsample"] = k
        return q, info
    a = _norm(img)
    if invert:
        a = 1.0 - a
    sig = max(1.0, 0.01 * min(a.shape))
    a = ndi.gaussian_filter(a, sig)
    th = filters.threshold_otsu(a)
    mask = a > th
    # close gaps, inner dark bands and cracks so the module is one blob (radius 3% of the short side)
    rc = max(2, int(0.03 * min(a.shape)))
    mask = ndi.binary_closing(mask, structure=morphology.disk(rc), iterations=1)
    mask = ndi.binary_fill_holes(mask)
    lab = measure.label(mask)
    if lab.max() == 0:
        raise ValueError("no foreground component")
    props = max(measure.regionprops(lab), key=lambda p: p.area)
    comp = lab == props.label
    hull = morphology.convex_hull_image(comp)
    ys, xs = np.nonzero(hull)
    s, d = xs + ys, xs - ys
    tl = (xs[s.argmin()], ys[s.argmin()])
    br = (xs[s.argmax()], ys[s.argmax()])
    tr = (xs[d.argmax()], ys[d.argmax()])
    bl = (xs[d.argmin()], ys[d.argmin()])
    quad = np.array([tl, tr, br, bl], dtype=np.float64)
    return quad, {"otsu": float(th), "fg_frac": float(comp.mean())}


def orient_grid(quad, rows, cols):
    """Assign the larger cell count to the longer quad side. Returns (nrows, ncols) in image orientation."""
    w = 0.5 * (np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[3]))
    h = 0.5 * (np.linalg.norm(quad[3] - quad[0]) + np.linalg.norm(quad[2] - quad[1]))
    big, small = max(rows, cols), min(rows, cols)
    return (small, big) if w >= h else (big, small)


def canonical_corners(nr, nc, S):
    W, H = nc * S, nr * S
    return np.array([[0, 0], [W, 0], [W, H], [0, H]], dtype=np.float64)


def rectify(img, tform, nr, nc, S):
    return transform.warp(img, tform, output_shape=(nr * S, nc * S), order=1,
                          mode="constant", cval=np.nan, preserve_range=True)


def _fit_lines(profile, n, S, m, pitch_rng=(0.98, 1.02), off_rng=0.06):
    """Fit the n-1 inner grid lines of a 1-D profile laid out as [m margin | n*S cells | m margin].
    A uniform grid (offset, pitch) is fitted first, then each line is refined locally (+-0.15 pitch).
    Gaps can be minima (dark) or maxima (bright); the polarity with the larger normalised contrast wins.
    Returns inner line positions in canonical coords (margin removed)."""
    L = len(profile)
    p = np.nan_to_num(profile, nan=np.nanmedian(profile))
    p = ndi.gaussian_filter1d(p, max(1.0, 0.02 * S))
    core = p[m:L - m] if L > 2 * m + 2 else p
    best = None
    for pol in (+1, -1):          # +1: gaps are minima, -1: gaps are maxima
        q = pol * p
        qc = pol * core
        med, sd = np.median(qc), np.std(qc) + 1e-9
        pitches = [S] if pitch_rng[0] == pitch_rng[1] else np.linspace(pitch_rng[0] * S, pitch_rng[1] * S, 9)
        for pitch in pitches:
            for off in np.linspace(-off_rng * S, off_rng * S, 13):
                pos = m + off + pitch * np.arange(1, n)
                if pos.min() < 0 or pos.max() >= L - 1:
                    continue
                v = np.interp(pos, np.arange(L), q)
                score = (med - v.mean()) / sd
                if best is None or score > best[0]:
                    best = (score, pol, pitch, off)
    score, pol, pitch, off = best
    q = pol * p
    lines, flags = [], 0
    for k in range(1, n):
        c = m + off + pitch * k
        lo, hi = int(max(0, c - 0.10 * pitch)), int(min(L - 1, c + 0.10 * pitch))
        seg = q[lo:hi + 1]
        j = lo + int(np.argmin(seg))
        # sub-pixel: parabola through the minimum and its neighbours
        if lo < j < hi:
            y0, y1, y2 = q[j - 1], q[j], q[j + 1]
            den = (y0 - 2 * y1 + y2)
            dj = 0.5 * (y0 - y2) / den if den > 1e-12 else 0.0
            dj = float(np.clip(dj, -0.5, 0.5))
        else:
            dj = 0.0
        wlo, whi = int(max(0, c - 0.5 * pitch)), int(min(L - 1, c + 0.5 * pitch))
        win = q[wlo:whi + 1]
        if q[j] < np.median(win) - 0.25 * np.std(win):
            lines.append(j + dj - m)
        else:
            lines.append(c - m)
            flags += 1
    return np.array(lines, dtype=np.float64), {"polarity": "dark_gaps" if pol > 0 else "bright_gaps",
                                              "pitch": float(pitch), "offset": float(off),
                                              "lines_fallback": flags, "fit_score": float(score)}


def rectify_margin(img, t, nr, nc, S, m):
    """Rectify with a margin of m px around the canonical grid (output px (u, v) = canonical + m)."""
    def inv(coords):
        return t(coords - m)
    return transform.warp(img, inv, output_shape=(nr * S + 2 * m, nc * S + 2 * m), order=1,
                          mode="constant", cval=np.nan, preserve_range=True)


def detect_grid(rect, nr, nc, S, m, pitch_rng=(0.98, 1.02), off_rng=0.06):
    H, W = rect.shape
    band = 0.1
    colprof = np.nanmean(rect[int(m + band * nr * S):int(H - m - band * nr * S), :], axis=0)
    rowprof = np.nanmean(rect[:, int(m + band * nc * S):int(W - m - band * nc * S)], axis=1)
    xs, ix = _fit_lines(colprof, nc, S, m, pitch_rng, off_rng)
    ys, iy = _fit_lines(rowprof, nr, S, m, pitch_rng, off_rng)
    return xs, ys, {"x": ix, "y": iy}


def register(img, rows, cols, S=64, invert=False, iters=3, quad_mode="otsu", grid_mode="detect"):
    if quad_mode == "full":
        h, w = img.shape
        quad = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float64)
        qinfo = {"mode": "full frame (module-only crop)"}
    else:
        quad, qinfo = find_quad(img, invert=invert)
    nr, nc = orient_grid(quad, rows, cols)
    if nr < 3 or nc < 3:
        raise ValueError("grid needs >= 3 cells per side for inner-intersection registration")
    can = canonical_corners(nr, nc, S)
    t = transform.ProjectiveTransform()
    t.estimate(can, quad)                        # canonical -> image
    if grid_mode == "uniform":
        # plain uniform grid inside the quad (used for module-only crops); no line detection
        P = t(np.array([[j * S, i * S] for i in range(nr + 1) for j in range(nc + 1)], dtype=np.float64))
        P = P.reshape(nr + 1, nc + 1, 2)
        sides = np.r_[np.linalg.norm(np.diff(P, axis=1), axis=2).ravel(),
                      np.linalg.norm(np.diff(P, axis=0), axis=2).ravel()]
        cell_side = float(np.median(sides))
        qa = {"rows": nr, "cols": nc, "S": S, "quad": quad.tolist(), "grid_mode": "uniform",
              "grid_corners": t(can).tolist(), "cell_side_px": cell_side,
              "res_rms_px": 0.0, "res_max_px": 0.0, "res_rms_pct_cell": float("nan"),
              "res_max_pct_cell": float("nan"), "loo_rms_pct_cell": float("nan"),
              "lines_fallback": 0, "grid_vs_quad_max_pct_cell": 0.0,
              "note": "uniform grid: residual undefined (no detected lines); judge by visual QA", "quad_info": qinfo}
        return t, qa
    m = int(round(0.25 * S))
    ideal = np.array([[j * S, i * S] for i in range(1, nr) for j in range(1, nc)], dtype=np.float64)
    hist = []
    for it in range(iters):
        rect = rectify_margin(img, t, nr, nc, S, m)
        # iteration 0: small global search anchored to the quad; later: fixed pitch, local refinement only
        if it == 0:
            xs, ys, ginfo = detect_grid(rect, nr, nc, S, m, pitch_rng=(0.98, 1.02), off_rng=0.06)
        else:
            xs, ys, ginfo = detect_grid(rect, nr, nc, S, m, pitch_rng=(1.0, 1.0), off_rng=0.03)
        gx, gy = np.meshgrid(xs, ys)
        det_img = t(np.c_[gx.ravel(), gy.ravel()])   # detected inner intersections, image px
        t_new = transform.ProjectiveTransform()
        t_new.estimate(ideal, det_img)
        res = np.linalg.norm(t_new(ideal) - det_img, axis=1)
        hist.append(float(np.sqrt(np.mean(res ** 2))))
        t = t_new
    t1 = t
    # leave-one-point-out
    loo = []
    for k in range(len(ideal)):
        msk = np.ones(len(ideal), bool)
        msk[k] = False
        tk = transform.ProjectiveTransform()
        tk.estimate(ideal[msk], det_img[msk])
        loo.append(float(np.linalg.norm(tk(ideal[k:k + 1]) - det_img[k:k + 1])))
    # median cell side in image px
    full = np.array([[j * S, i * S] for i in range(nr + 1) for j in range(nc + 1)], dtype=np.float64)
    P = t1(full).reshape(nr + 1, nc + 1, 2)
    sides = np.r_[np.linalg.norm(np.diff(P, axis=1), axis=2).ravel(),
                  np.linalg.norm(np.diff(P, axis=0), axis=2).ravel()]
    cell_side = float(np.median(sides))
    qa = {"rows": nr, "cols": nc, "S": S, "quad": quad.tolist(),
          "grid_corners": t1(canonical_corners(nr, nc, S)).tolist(),
          "cell_side_px": cell_side,
          "res_rms_px": float(np.sqrt(np.mean(res ** 2))), "res_max_px": float(res.max()),
          "res_rms_pct_cell": float(100 * np.sqrt(np.mean(res ** 2)) / cell_side),
          "res_max_pct_cell": float(100 * res.max() / cell_side),
          "loo_rms_pct_cell": float(100 * np.sqrt(np.mean(np.square(loo))) / cell_side),
          "lines_fallback": ginfo["x"]["lines_fallback"] + ginfo["y"]["lines_fallback"],
          "res_rms_px_by_iter": hist, "n_points": int(len(ideal)), "grid_mode": "detect",
          "grid_vs_quad_max_pct_cell": float(100 * np.max(np.linalg.norm(
              t1(canonical_corners(nr, nc, S)) - quad, axis=1)) / cell_side),
          "grid": ginfo, "quad_info": qinfo}
    return t1, qa

# ----------------------------------------------------------------------------- features

def cell_slices(nr, nc, S, inner):
    pad = int(round(S * (1 - inner) / 2))
    for i in range(nr):
        for j in range(nc):
            yield i, j, slice(i * S + pad, (i + 1) * S - pad), slice(j * S + pad, (j + 1) * S - pad)


def el_features(rect, nr, nc, S, thr=0.5, open_frac=0.02, inner=0.9):
    meds = np.array([np.nanmedian(rect[ys, xs]) for _, _, ys, xs in cell_slices(nr, nc, S, inner)])
    mod_med = float(np.nanmedian(meds))
    dark = rect < thr * mod_med
    r = max(1, int(round(open_frac * S)))
    dark_open = morphology.binary_opening(np.nan_to_num(dark, nan=0).astype(bool), morphology.disk(r))
    out = {}
    for i, j, ys, xs in cell_slices(nr, nc, S, inner):
        blk = rect[ys, xs]
        valid = np.isfinite(blk)
        out[(i, j)] = {"el_med": float(np.nanmedian(blk)),
                       "el_p99": float(np.nanpercentile(blk, 99)),
                       "el_rel": float(np.nanmedian(blk) / mod_med) if mod_med else float("nan"),
                       "el_dark_frac": float(dark_open[ys, xs][valid].mean()) if valid.any() else float("nan")}
    return out, {"el_module_median": mod_med, "thr": thr, "open_radius_px": r}


def ir_features(rect, nr, nc, S, inner=0.8):
    meds = {}
    hot = {}
    for i, j, ys, xs in cell_slices(nr, nc, S, inner):
        blk = rect[ys, xs]
        meds[(i, j)] = float(np.nanmedian(blk))
        hot[(i, j)] = float(np.nanpercentile(blk, 95) - np.nanmedian(blk))
    mod_med = float(np.nanmedian(list(meds.values())))
    out = {k: {"ir_med": v, "ir_dT": v - mod_med, "ir_hot": hot[k]} for k, v in meds.items()}
    return out, {"ir_module_median": mod_med}


def uvf_features(rect, nr, nc, S, inner=0.9):
    meds = {}
    for i, j, ys, xs in cell_slices(nr, nc, S, inner):
        meds[(i, j)] = float(np.nanmedian(rect[ys, xs]))
    mod_med = float(np.nanmedian(list(meds.values())))
    return {k: {"uvf_med": v, "uvf_rel": v / mod_med if mod_med else float("nan")} for k, v in meds.items()}, {}

# ----------------------------------------------------------------------------- overlays

def overlay(img, t1, nr, nc, S, path, maxdim=1200):
    a = (_norm(img) * 255).astype(np.uint8)
    rgb = np.stack([a, a, a], axis=-1)
    for i in range(nr + 1):
        pts = t1(np.c_[np.linspace(0, nc * S - 1, 400), np.full(400, min(i * S, nr * S - 1))])
        _draw(rgb, pts)
    for j in range(nc + 1):
        pts = t1(np.c_[np.full(400, min(j * S, nc * S - 1)), np.linspace(0, nr * S - 1, 400)])
        _draw(rgb, pts)
    im = Image.fromarray(rgb)
    sc = maxdim / max(im.size)
    if sc < 1:
        im = im.resize((int(im.size[0] * sc), int(im.size[1] * sc)))
    im.save(path)


def _draw(rgb, pts):
    H, W = rgb.shape[:2]
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= yi + dy < H and 0 <= xi + dx < W:
                    rgb[yi + dy, xi + dx] = (255, 0, 0)

# ----------------------------------------------------------------------------- driver

ORIENTS = ("id", "fliph", "flipv", "rot180")


def orient_key(k, nr, nc, how):
    """Map a (row, col) cell of a non-EL modality onto the EL grid. A uniform grid is symmetric under
    rot180 and the two mirrors, so independent registration cannot fix this; it is a declared choice."""
    i, j = k
    if how == "id":
        return (i, j)
    if how == "fliph":
        return (i, nc - 1 - j)
    if how == "flipv":
        return (nr - 1 - i, j)
    if how == "rot180":
        return (nr - 1 - i, nc - 1 - j)
    raise ValueError(how)


def process_module(mod, grid, paths, outdir, S_el=128, S_ir=48, S_uvf=96, orient="id", orient_uvf=None,
                   quad_modes=None, grid_modes=None):
    quad_modes = quad_modes or {}
    grid_modes = grid_modes or {}
    rows, cols = grid
    os.makedirs(outdir, exist_ok=True)
    rep = {"module": mod, "version": VERSION, "grid_expected": [rows, cols], "modalities": {}}
    feats = {}
    for name, S in (("el", S_el), ("ir", S_ir), ("uvf", S_uvf)):
        p = paths.get(name)
        if not p:
            continue
        img, meta = read_image(p)
        t1, qa = register(img, rows, cols, S=S, quad_mode=quad_modes.get(name, "otsu"),
                          grid_mode=grid_modes.get(name, "detect"))
        qa["quad_mode"] = quad_modes.get(name, "otsu")
        nr, nc = qa["rows"], qa["cols"]
        rect = rectify(img, t1, nr, nc, S)
        if name == "el":
            f, fm = el_features(rect, nr, nc, S)
        elif name == "ir":
            f, fm = ir_features(rect, nr, nc, S)
        else:
            f, fm = uvf_features(rect, nr, nc, S)
        overlay(img, t1, nr, nc, S, os.path.join(outdir, f"{mod}_{name}_overlay.png"))
        rep["modalities"][name] = {"path": p, "meta": meta, "qa": qa, "feat_meta": fm}
        if name != "el" and "el" in feats and (nr, nc) != (feats["el"][1], feats["el"][2]):
            # portrait vs landscape: the rot90 direction is unknown, so the modality is rejected, not guessed
            rep["modalities"][name]["rejected"] = f"grid {nr}x{nc} transposed vs EL {feats['el'][1]}x{feats['el'][2]}"
            continue
        if name != "el":
            how = orient if name == "ir" else (orient_uvf or orient)
            f = {orient_key(k, nr, nc, how): v for k, v in f.items()}
            rep["modalities"][name]["orient_to_el"] = how
        feats[name] = (f, nr, nc)
    # consistency of grid orientation across modalities
    shapes = {k: (v[1], v[2]) for k, v in feats.items()}
    rep["grid_shapes"] = {k: list(v) for k, v in shapes.items()}
    rep["grid_consistent"] = len(set(shapes.values())) <= 1
    rep["orient"] = {"ir": orient, "uvf": orient_uvf or orient}
    keys = sorted(set().union(*[set(v[0].keys()) for v in feats.values()])) if feats else []
    cols_out = ["module", "row", "col"]
    rows_out = []
    for k in keys:
        r = {"module": mod, "row": k[0], "col": k[1]}
        for name, (f, _, _) in feats.items():
            r.update(f.get(k, {}))
        rows_out.append(r)
    allcols = cols_out + sorted({c for r in rows_out for c in r} - set(cols_out))
    with open(os.path.join(outdir, f"{mod}_cells.tsv"), "w") as f:
        f.write("\t".join(allcols) + "\n")
        for r in rows_out:
            f.write("\t".join(str(r.get(c, "")) for c in allcols) + "\n")
    with open(os.path.join(outdir, f"{mod}_reg.json"), "w") as f:
        json.dump(rep, f, indent=1)
    return rep

# ----------------------------------------------------------------------------- self-test

def _synth_module(nr, nc, S, rng, inactive=None, busbars=2, gap=0.06, bright=1.0, band=0.0, band_pos=0.42):
    H, W = nr * S, nc * S
    img = np.full((H, W), bright, np.float32)
    g = max(1, int(gap * S))
    for i in range(nr + 1):
        img[max(0, i * S - g // 2):min(H, i * S + g // 2 + 1), :] = 0.15
    for j in range(nc + 1):
        img[:, max(0, j * S - g // 2):min(W, j * S + g // 2 + 1)] = 0.15
    for j in range(nc):
        for b in range(1, busbars + 1):
            x = int(j * S + b * S / (busbars + 1))
            img[:, x:x + max(1, S // 60)] *= 0.4
    if band > 0:   # resistive-style dark band in the middle of every cell (A1-like), depth `band`
        for j in range(nc):
            x0 = int(j * S + band_pos * S)
            img[:, x0:x0 + int(0.15 * S)] *= (1 - band)
    if inactive is not None:
        i, j, frac = inactive
        x0 = int(j * S + (1 - frac) * S)
        img[i * S + g:(i + 1) * S - g, x0:(j + 1) * S - g] *= 0.2
    img += rng.normal(0, 0.03, img.shape).astype(np.float32)
    return img


def _embed(img, rng, canvas=(1400, 2600), angle=4.0, persp=0.0004):
    H, W = img.shape
    ch, cw = canvas
    src = np.array([[0, 0], [W, 0], [W, H], [0, H]], np.float64)
    a = np.deg2rad(angle)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    c = np.array([W / 2, H / 2])
    dst = (src - c) @ R.T * 0.9 + np.array([cw / 2, ch / 2])
    dst += rng.normal(0, 6, dst.shape)
    t = transform.ProjectiveTransform()
    t.estimate(dst, src)  # canvas -> module
    out = transform.warp(img, t, output_shape=canvas, order=1, cval=0.05, preserve_range=True)
    out += rng.normal(0, 0.02, out.shape)
    return out.astype(np.float32), dst


def selftest(outdir):
    rng = np.random.default_rng(0)
    os.makedirs(outdir, exist_ok=True)
    results = []
    nr, nc = 4, 9
    for trial in range(3):
        el = _synth_module(nr, nc, 200, rng, inactive=(1, 3, 0.4))
        el_c, el_q = _embed(el, rng, canvas=(1300, 2400), angle=3 + trial)
        ir = ndi.gaussian_filter(_synth_module(nr, nc, 30, rng, inactive=(1, 3, 0.4), busbars=0), 1.5) * 4 + 30
        ir_c, ir_q = _embed(ir, rng, canvas=(240, 320) if trial == 0 else (300, 420), angle=-2 - trial)
        ir_c = np.where(ir_c < 1, 20.0, ir_c)
        np.save(os.path.join(outdir, f"syn{trial}_el.npy"), el_c)
        p_el = os.path.join(outdir, f"syn{trial}_el.tif")
        Image.fromarray(np.clip(el_c * 20000, 0, 65535).astype(np.uint16)).save(p_el)
        p_ir = os.path.join(outdir, f"syn{trial}_ir.txt")
        np.savetxt(p_ir, ir_c, fmt="%.2f", delimiter="\t", header="synthetic IR degC", comments="# ")
        rep = process_module(f"syn{trial}", (nr, nc), {"el": p_el, "ir": p_ir}, outdir)
        out = {"trial": trial}
        for m, q_true in (("el", el_q), ("ir", ir_q)):
            qa = rep["modalities"][m]["qa"]
            quad = np.array(qa["grid_corners"])
            out[f"{m}_corner_err_px"] = float(np.max(np.linalg.norm(quad - q_true, axis=1)))
            out[f"{m}_corner_err_pct_cell"] = 100 * out[f"{m}_corner_err_px"] / qa["cell_side_px"]
            out[f"{m}_res_rms_pct_cell"] = qa["res_rms_pct_cell"]
            out[f"{m}_lines_fallback"] = qa["lines_fallback"]
            out[f"{m}_grid"] = [qa["rows"], qa["cols"]]
        # the synthetic inactive cell (row 1, col 3) must be the darkest EL cell and the coolest IR cell
        rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(outdir, f"syn{trial}_cells.tsv"))]
        hdr, body = rows[0], rows[1:]
        ci = {c: k for k, c in enumerate(hdr)}
        darkest = max(body, key=lambda r: float(r[ci["el_dark_frac"]]))
        coolest = min(body, key=lambda r: float(r[ci["ir_dT"]]))
        out["el_darkest_cell"] = [int(darkest[ci["row"]]), int(darkest[ci["col"]])]
        out["el_darkest_frac"] = float(darkest[ci["el_dark_frac"]])
        out["ir_coolest_cell"] = [int(coolest[ci["row"]]), int(coolest[ci["col"]])]
        results.append(out)
    # orientation test: IR content mirrored left-right; --orient fliph must map its coolest cell to EL (1, 3)
    el = _synth_module(nr, nc, 200, rng, inactive=(1, 3, 0.4))
    el_c, _ = _embed(el, rng, canvas=(1300, 2400), angle=2)
    ir = ndi.gaussian_filter(_synth_module(nr, nc, 30, rng, inactive=(1, 3, 0.4), busbars=0), 1.5) * 4 + 30
    ir_c, _ = _embed(np.fliplr(ir).copy(), rng, canvas=(300, 420), angle=-2)
    ir_c = np.where(ir_c < 1, 20.0, ir_c)
    p_el = os.path.join(outdir, "synflip_el.tif")
    Image.fromarray(np.clip(el_c * 20000, 0, 65535).astype(np.uint16)).save(p_el)
    p_ir = os.path.join(outdir, "synflip_ir.txt")
    np.savetxt(p_ir, ir_c, fmt="%.2f", delimiter="\t")
    orient_res = {}
    for how in ORIENTS:
        process_module(f"synflip_{how}", (nr, nc), {"el": p_el, "ir": p_ir}, outdir, orient=how)
        rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(outdir, f"synflip_{how}_cells.tsv"))]
        hdr, body = rows[0], rows[1:]
        ci = {c: k for k, c in enumerate(hdr)}
        coolest = min(body, key=lambda r: float(r[ci["ir_dT"]]))
        orient_res[how] = [int(coolest[ci["row"]]), int(coolest[ci["col"]])]
    orient_ok = orient_res["fliph"] == [1, 3] and orient_res["id"] != [1, 3]
    # module-only crop test (like A1 _cropped.txt): IR array = module only, 3 x 12, ~11 px per cell
    nr2, nc2 = 3, 12
    el2 = _synth_module(nr2, nc2, 200, rng, inactive=(1, 7, 0.4))
    el2_c, _ = _embed(el2, rng, canvas=(900, 2800), angle=1.5)
    ir2 = ndi.gaussian_filter(_synth_module(nr2, nc2, 11, rng, inactive=(1, 7, 0.4), busbars=0), 1.0) * 4 + 30
    p_el2 = os.path.join(outdir, "syncrop_el.tif")
    Image.fromarray(np.clip(el2_c * 20000, 0, 65535).astype(np.uint16)).save(p_el2)
    p_ir2 = os.path.join(outdir, "syncrop_ir.txt")
    np.savetxt(p_ir2, ir2, fmt="%.2f", delimiter="\t")
    rep2 = process_module("syncrop", (nr2, nc2), {"el": p_el2, "ir": p_ir2}, outdir,
                          quad_modes={"ir": "full"})
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(outdir, "syncrop_cells.tsv"))]
    hdr, body = rows[0], rows[1:]
    ci = {c: k for k, c in enumerate(hdr)}
    coolest = min(body, key=lambda r: float(r[ci["ir_dT"]]))
    darkest = max(body, key=lambda r: float(r[ci["el_dark_frac"]]))
    crop_res = {"ir_res_rms_pct_cell": rep2["modalities"]["ir"]["qa"]["res_rms_pct_cell"],
                "el_res_rms_pct_cell": rep2["modalities"]["el"]["qa"]["res_rms_pct_cell"],
                "ir_grid": [rep2["modalities"]["ir"]["qa"]["rows"], rep2["modalities"]["ir"]["qa"]["cols"]],
                "ir_coolest": [int(coolest[ci["row"]]), int(coolest[ci["col"]])],
                "el_darkest": [int(darkest[ci["row"]]), int(darkest[ci["col"]])]}
    crop_ok = crop_res["ir_coolest"] == [1, 7] and crop_res["el_darkest"] == [1, 7]
    # inner-band test (A1-like resistive pattern): 3 x 12, dark band in every cell; the grid must not drift
    band_res = []
    for depth, pos in ((0.5, 0.42), (0.7, 0.42), (0.5, 0.10), (0.7, 0.10)):
        el3 = _synth_module(3, 12, 200, rng, band=depth, band_pos=pos)
        el3_c, q3 = _embed(el3, rng, canvas=(900, 2800), angle=1.0)
        p_el3 = os.path.join(outdir, f"synband{int(depth*10)}_{int(pos*100)}_el.tif")
        Image.fromarray(np.clip(el3_c * 20000, 0, 65535).astype(np.uint16)).save(p_el3)
        img3, _ = read_image(p_el3)
        t3, qa3 = register(img3, 3, 12, S=128)
        err = float(np.max(np.linalg.norm(np.array(qa3["grid_corners"]) - q3, axis=1)) / qa3["cell_side_px"] * 100)
        band_res.append({"depth": depth, "band_pos": pos, "corner_err_pct_cell": err, "res_rms_pct_cell": qa3["res_rms_pct_cell"],
                         "grid_vs_quad_max_pct_cell": qa3["grid_vs_quad_max_pct_cell"]})
    band_ok = all(b["corner_err_pct_cell"] < 5.0 for b in band_res)
    crop_res["band_test"] = band_res
    crop_ok = crop_ok and band_ok
    orient_ok = orient_ok and crop_ok
    ok = orient_ok and all(r["el_corner_err_pct_cell"] < 5.0 and r["ir_corner_err_pct_cell"] < 10.0 and
             r["el_res_rms_pct_cell"] < 1.0 and r["ir_res_rms_pct_cell"] < 2.0 and
             r["el_darkest_cell"] == [1, 3] and r["ir_coolest_cell"] == [1, 3] for r in results)
    with open(os.path.join(outdir, "selftest.json"), "w") as f:
        json.dump({"version": VERSION, "pass": ok, "results": results, "orient_test": orient_res,
                   "crop_test": crop_res, "orient_and_crop_ok": orient_ok}, f, indent=1)
    print(json.dumps({"pass": ok, "orient_test": orient_res, "crop_test": crop_res, "orient_and_crop_ok": orient_ok,
                      "results": results}, indent=1))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module")
    ap.add_argument("--grid", default="4x9", help="rows x cols, e.g. 4x9 (orientation is auto-assigned)")
    ap.add_argument("--el")
    ap.add_argument("--ir")
    ap.add_argument("--uvf")
    ap.add_argument("--orient", default="id", choices=ORIENTS,
                    help="IR (and UVF unless --orient-uvf) cell mapping onto the EL grid; written to reg.json")
    ap.add_argument("--orient-uvf", default=None, choices=ORIENTS)
    ap.add_argument("--quad-ir", default="otsu", choices=("otsu", "full"),
                    help="full: the IR array is a module-only crop, corners = image corners")
    ap.add_argument("--quad-uvf", default="otsu", choices=("otsu", "full"))
    ap.add_argument("--grid-ir", default="detect", choices=("detect", "uniform"),
                    help="uniform: plain uniform grid inside the IR quad (module-only crops)")
    ap.add_argument("--manifest")
    ap.add_argument("--out", required=True)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest(a.out) else 1)
    jobs = []
    if a.manifest:
        lines = [l.rstrip("\n").split("\t") for l in open(a.manifest) if l.strip()]
        hdr = lines[0]
        for l in lines[1:]:
            d = dict(zip(hdr, l + [""] * (len(hdr) - len(l))))
            g = tuple(int(x) for x in d.get("grid", a.grid).lower().split("x"))
            jobs.append((d["module"], g, {k: d.get(k) or None for k in ("el", "ir", "uvf")}))
    else:
        g = tuple(int(x) for x in a.grid.lower().split("x"))
        jobs.append((a.module, g, {"el": a.el, "ir": a.ir, "uvf": a.uvf}))
    summary = []
    for mod, g, paths in jobs:
        try:
            rep = process_module(mod, g, paths, a.out, orient=a.orient, orient_uvf=a.orient_uvf,
                                 quad_modes={"ir": a.quad_ir, "uvf": a.quad_uvf},
                                 grid_modes={"ir": a.grid_ir})
            row = {"module": mod, "grid_consistent": rep["grid_consistent"], "orient": rep["orient"],
                   "rejected": {m: v["rejected"] for m, v in rep["modalities"].items() if "rejected" in v}}
            for m, v in rep["modalities"].items():
                row[f"{m}_grid_vs_quad_max_pct_cell"] = round(v["qa"].get("grid_vs_quad_max_pct_cell", float("nan")), 2)
                row[f"{m}_res_rms_pct_cell"] = round(v["qa"]["res_rms_pct_cell"], 3)
                row[f"{m}_res_max_pct_cell"] = round(v["qa"]["res_max_pct_cell"], 3)
                row[f"{m}_lines_fallback"] = v["qa"]["lines_fallback"]
            summary.append(row)
        except Exception as e:  # report, continue
            summary.append({"module": mod, "error": repr(e)})
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
