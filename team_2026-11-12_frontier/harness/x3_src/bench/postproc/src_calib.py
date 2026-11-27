"""src_calib (T4 arm 1): per-source output calibration of the crack class, chosen by cross-fitting (bench/crossfit_op).
Variants per (seed, held-out fold k), all fitted on the other folds' out-of-fold cells of that seed:
  argmax     the dump's pred
  glob_bias  one crack bias for all sources, argmax pooled strict crack IoU over BIAS
  src_bias   per source s: argmax IoU over BIAS on the fit cells of s if s has >= MIN_CRACK_CELLS crack cells there,
             else glob_bias (SDLE falls back); a bias that more than doubles the crack px on crack-free fit cells of s
             (against argmax; floor 1 px per crack-free cell, so a zero argmax count does not refuse everything) is refused
  src_morph  per source: argmax IoU over OPS (morphology on pred == crack) if enough crack cells, else 'none'
Uses source metadata (the stem prefix) at test time: reported as its own 'uses source metadata' row.
Contrasts: src_bias - glob_bias (primary), src_morph - argmax."""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

BIAS = tuple(float(b) for b in np.arange(-4.0, 4.0001, 0.25))          # 33 values, subset of crossfit_op.OP_GRID
OPS = ("erode1_cross", "none", "dilate1_cross", "dilate1_3x3")
MIN_CRACK_CELLS = 20
FA_FACTOR = 2.0
CROSS = ndi.generate_binary_structure(2, 1)
SQ = np.ones((3, 3), bool)


def src_of(stem: str) -> str:
    s = stem.split("_")[0]
    if s not in ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE"):
        raise ValueError(f"unknown source {s!r}")
    return s


def morph(crack: np.ndarray, op: str) -> np.ndarray:
    if op == "none":
        return crack.copy()
    if op == "erode1_cross":
        return ndi.binary_erosion(crack, CROSS)
    if op == "dilate1_cross":
        return ndi.binary_dilation(crack, CROSS)
    if op == "dilate1_3x3":
        return ndi.binary_dilation(crack, SQ)
    raise ValueError(op)


def cands() -> list[tuple]:
    return [("argmax",)] + [("bias", b) for b in BIAS] + [("morph", o) for o in OPS]


def fit(counts: np.ndarray, stems: list[str], folds: np.ndarray, cl: list[tuple]) -> dict:
    """Choices per held-out fold: {'glob_bias': {k: i}, 'src_bias': {k: {src: i}}, 'src_morph': {k: {src: i}},
    'n_crack': {k: {src: n}}, 'fallback': {k: [src]}}. counts (n, K, 7) over cl."""
    from ..crossfit_op import choose
    src = np.array([src_of(s) for s in stems])
    gp = counts[:, 0, 2]
    ib = [i for i, c in enumerate(cl) if c[0] == "bias"]
    im = [i for i, c in enumerate(cl) if c[0] == "morph"]
    ia = [i for i, c in enumerate(cl) if c[0] == "argmax"][0]
    bias_ok = np.zeros(len(cl), bool); bias_ok[ib] = True
    morph_ok = np.zeros(len(cl), bool); morph_ok[im] = True
    out = {"glob_bias": {}, "src_bias": {}, "src_morph": {}, "n_crack": {}, "fallback": {}, "fa_refused": {}}
    for k in sorted(set(int(f) for f in folds)):
        fitm = folds != k
        g = choose(counts[fitm].sum(0), cl, "crack_iou", allowed=bias_ok)
        out["glob_bias"][k] = g
        out["src_bias"][k], out["src_morph"][k], out["n_crack"][k] = {}, {}, {}
        out["fallback"][k], out["fa_refused"][k] = [], []
        for s in sorted(set(src)):
            ms = fitm & (src == s)
            n = int(((gp > 0) & ms).sum())
            out["n_crack"][k][s] = n
            if n < MIN_CRACK_CELLS:
                out["src_bias"][k][s] = g
                out["src_morph"][k][s] = [i for i in im if cl[i][1] == "none"][0]
                out["fallback"][k].append(s)
                continue
            pooled = counts[ms].sum(0)
            cf = ms & (gp == 0)
            fa = counts[cf][:, :, 1].sum(0) if cf.any() else np.zeros(len(cl), np.int64)
            fa_ok = fa <= FA_FACTOR * max(int(fa[ia]), int(cf.sum()))   # floor: 1 px per crack-free cell
            if not (bias_ok & fa_ok).any():
                fa_ok = np.ones(len(cl), bool)
            out["fa_refused"][k] += [f"{s}:{(bias_ok & ~fa_ok).sum()}"] if (bias_ok & ~fa_ok).any() else []
            out["src_bias"][k][s] = choose(pooled, cl, "crack_iou", allowed=bias_ok & fa_ok)
            out["src_morph"][k][s] = choose(pooled, cl, "crack_iou", allowed=morph_ok)
    return out


def choice_per_cell(ch: dict, variant: str, stems: list[str], folds: np.ndarray, cl: list[tuple]) -> list[tuple]:
    ia = [i for i, c in enumerate(cl) if c[0] == "argmax"][0]
    out = []
    for s, k in zip(stems, folds):
        k = int(k)
        if variant == "argmax":
            out.append(cl[ia])
        elif variant == "glob_bias":
            out.append(cl[ch["glob_bias"][k]])
        else:
            out.append(cl[ch[variant][k][src_of(s)]])
    return out
