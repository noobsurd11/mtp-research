"""elbench x3: D0, the placement diagnostic (WAVE2_REVIEW X5). Per cell with GT crack (v1.1, keep px only):
(a) share of skeleton points (components >= 15 px; at most 400 points per cell, fixed per-stem draw) whose darkest point
    along the normal (|offset| <= 4 px, 0.25 px steps, image smoothed with sigma 0.7) lies within 1 px, among points where
    the dip is visible (depth > 0.03). Measured on the prediction's crack mask and on the GT label (the reference; the
    0.48 of annotation_consistency.py was measured the same way on the 20211104 labels with skimage's skeleton).
(b) strict crack IoU counts of the prediction against the original labels, and against snapped labels when a folder of
    snapped masks is given (T3 P-RS4; the snap script is not part of this build).
(c) mean p_crack along the normal as a function of signed distance from the ridge (the darkest point), at GT label points
    with a visible dip and the ridge >= 1 px from the label; positive distance = toward the label. Also the mean p_crack
    at the ridge and at the label point.
Code from data_analysis/scripts/annotation_consistency.py (tangents, profiles, the depth rule), numpy + scipy; the skeleton
is bench/skel.py (no scikit-image on gaint).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from .skel import skeletonize

CRACK = 14
SQ = np.ones((3, 3), bool)
T = np.arange(-5, 5.0001, 0.25)
SEARCH = np.abs(T) <= 4
DIP = 0.03
MIN_COMP = 15
MAX_PTS = 400
D = np.arange(-4, 4.0001, 0.5)


def tangents(skel, lab, ys, xs, r: int = 3) -> np.ndarray:
    """annotation_consistency.tangents: unit tangent (dy, dx) by PCA of same-component skeleton points within radius r."""
    H, W = skel.shape
    out = np.full((len(ys), 2), np.nan)
    for i, (y, x) in enumerate(zip(ys, xs)):
        y0, y1, x0, x1 = max(0, y - r), min(H, y + r + 1), max(0, x - r), min(W, x + r + 1)
        win = skel[y0:y1, x0:x1] & (lab[y0:y1, x0:x1] == lab[y, x])
        py, px = np.nonzero(win)
        if len(py) < 4:
            continue
        c = np.cov(np.vstack([py, px]).astype(float))
        ev, evec = np.linalg.eigh(c)
        if ev[-1] < 2 * max(ev[0], 1e-9):
            continue
        out[i] = evec[:, -1]
    return out


def sample(img, cy, cx) -> np.ndarray:
    return ndi.map_coordinates(img, [cy.ravel(), cx.ravel()], order=1, mode="nearest").reshape(cy.shape)


def ridge_points(img_s: np.ndarray, mask: np.ndarray, stem: str, tag: str):
    """(ys, xs, normals, t*, visible) for the skeleton points of mask (components >= MIN_COMP px)."""
    if not mask.any():
        return None
    skel = skeletonize(mask)
    lab, n = ndi.label(mask, SQ)
    sizes = ndi.sum(mask, lab, index=np.arange(1, n + 1))
    big = np.isin(lab, 1 + np.nonzero(sizes >= MIN_COMP)[0]) & skel
    ys, xs = np.nonzero(big)
    if len(ys) > MAX_PTS:
        rng = np.random.default_rng(int(hashlib.md5(f"{stem}|{tag}".encode()).hexdigest()[:8], 16))
        k = np.sort(rng.choice(len(ys), MAX_PTS, replace=False))
        ys, xs = ys[k], xs[k]
    if not len(ys):
        return None
    tg = tangents(skel, lab, ys, xs)
    ok = ~np.isnan(tg[:, 0])
    ys, xs, tg = ys[ok], xs[ok], tg[ok]
    if not len(ys):
        return None
    nrm = np.stack([-tg[:, 1], tg[:, 0]], 1)
    cy = ys[:, None] + T[None, :] * nrm[:, 0:1]
    cx = xs[:, None] + T[None, :] * nrm[:, 1:2]
    pr = sample(img_s, cy, cx)
    ps = pr[:, SEARCH]
    tstar = T[SEARCH][np.argmin(ps, 1)]
    far = pr[:, np.abs(T) >= 4].mean(1)
    depth = (far - ps.min(1)) / np.maximum(far, 1e-6)
    return ys, xs, nrm, tstar, depth > DIP


def load_image(images: str, stem: str) -> np.ndarray:
    a = np.asarray(Image.open(Path(images) / f"{stem}.png"))
    if a.ndim == 3:
        a = a[..., 0]
    return a.astype(np.float32)


def _share(rp) -> list:
    if rp is None:
        return [0, 0, 0, 0]
    _, _, _, t, vis = rp
    a = np.abs(t[vis])
    return [int(len(t)), int(vis.sum()), int((a <= 1).sum()), int((a <= 0.5).sum())]


def d0_cell(d: dict, gt: np.ndarray, keep, payload: dict) -> dict:
    k = np.ones_like(gt, bool) if keep is None else keep
    g = (gt == CRACK) & k
    p = (d["pred"] == CRACK) & k
    out = {"gp": int(g.sum()), "orig": [int((p & g).sum()), int(p.sum()), int(g.sum())], "snap": None}
    if payload.get("snapped"):
        sm = np.array(Image.open(Path(payload["snapped"]) / f"{payload['stem']}.png"))
        gs = (sm == CRACK) & k
        out["snap"] = [int((p & gs).sum()), int(p.sum()), int(gs.sum())]
    if not g.any():
        return out
    img_s = ndi.gaussian_filter(load_image(payload["images"], payload["stem"]), 0.7)
    out["pred"] = _share(ridge_points(img_s, p, payload["stem"], "pred"))
    rg = ridge_points(img_s, g, payload["stem"], "gt")
    out["gt"] = _share(rg)
    prof, n, pr_sum, pl_sum = np.zeros(len(D)), 0, 0.0, 0.0
    if rg is not None:
        ys, xs, nrm, t, vis = rg
        sel = vis & (np.abs(t) >= 1)
        if sel.any():
            ys, xs, nrm, t = ys[sel], xs[sel], nrm[sel], t[sel]
            s = -np.sign(t)                                   # unit direction from the ridge toward the label
            base_y, base_x = ys + t * nrm[:, 0], xs + t * nrm[:, 1]   # ridge position
            cy = base_y[:, None] + D[None, :] * (s * nrm[:, 0])[:, None]
            cx = base_x[:, None] + D[None, :] * (s * nrm[:, 1])[:, None]
            pc = d["p_crack"].astype(np.float32)
            prof = sample(pc, cy, cx).sum(0)
            n = int(sel.sum())
            pr_sum = float(sample(pc, base_y[:, None], base_x[:, None]).sum())
            pl_sum = float(pc[ys, xs].sum())
    out.update({"prof_sum": prof.tolist(), "prof_n": n, "p_ridge_sum": pr_sum, "p_label_sum": pl_sum})
    return out


def aggregate(cells: dict, keep_stem=lambda s: True) -> dict:
    st = [s for s in cells if keep_stem(s) and cells[s]["gp"] > 0]
    if not st:
        return {"n_cells": 0}
    P = np.sum([cells[s]["pred"] for s in st], 0)
    G = np.sum([cells[s]["gt"] for s in st], 0)
    o = np.sum([cells[s]["orig"] for s in st], 0)
    n = sum(cells[s]["prof_n"] for s in st)
    prof = np.sum([cells[s]["prof_sum"] for s in st], 0) / max(n, 1)
    iou = lambda c: c[0] / (c[1] + c[2] - c[0]) if (c[1] + c[2] - c[0]) > 0 else float("nan")  # noqa: E731
    out = {"n_cells": len(st), "pred_points": int(P[0]), "pred_visible": int(P[1]),
           "pred_share_le1": P[2] / P[1] if P[1] else float("nan"), "pred_share_le05": P[3] / P[1] if P[1] else float("nan"),
           "gt_points": int(G[0]), "gt_visible": int(G[1]),
           "gt_share_le1": G[2] / G[1] if G[1] else float("nan"), "gt_share_le05": G[3] / G[1] if G[1] else float("nan"),
           "iou_orig": iou(o), "prof_n": n, "prof_d": D.tolist(), "prof_mean_pcrack": prof.tolist(),
           "p_at_ridge": sum(cells[s]["p_ridge_sum"] for s in st) / max(n, 1),
           "p_at_label": sum(cells[s]["p_label_sum"] for s in st) / max(n, 1)}
    if all(cells[s]["snap"] is not None for s in st):
        out["iou_snapped"] = iou(np.sum([cells[s]["snap"] for s in st], 0))
    return out


def reading(share: float) -> str:
    if not np.isfinite(share):
        return "n/a"
    if share >= 0.75:
        return "ON RIDGE (>= 0.75): placement arms act only through confidence; run merged ridge_snap + soft_band_jml first"
    if share <= 0.60:
        return "FOLLOWS JITTER / BLURRED (<= 0.60): all placement arms keep their priority"
    return "BETWEEN 0.60 and 0.75: the lead decides"
