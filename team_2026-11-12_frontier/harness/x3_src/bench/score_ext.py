"""elbench scorer extensions beyond the m0 record (numpy + scipy only).

- relaxed crack counts at radius r (same formula as m0's crack_rel2, radius 1 and 3 added: lead, 12 Nov);
- the GT-only label-noise reference "predictions": GT shifted by 1 px (4 directions; edge rows / columns replicated) and
  GT with crack dilated by 1 px (EDT <= 1, i.e. the 4-neighbour cross, overwriting other classes);
- binned AP (copied from src/evaluation/threshold_free.py binned_ap at e544133, numpy only);
- run-level summary on top of m0core.agg: fixed class lists, rel@1/2/3, AP and bin-0 share, subsets.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

from .m0core import CRACK, INACT, NC, agg

# Track M decision list (trackM/baseline.md s1): classes with GT in >= 3 of the 50 test cells. Fixed for every set.
ROB13 = [0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21]
FIX15 = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 18, 20, 21]
RADII = (1, 2, 3)
SHIFTS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}


def rel_counts(pred: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, radii=RADII) -> dict:
    """{'crack_rel{r}': [pred px within r of GT, pred px, GT px within r of pred, GT px]} for r in radii (m0 formula)."""
    k = np.ones_like(gt, bool) if keep is None else keep
    g, p = (gt == CRACK) & k, (pred == CRACK) & k
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    return {f"crack_rel{r}": [int((dg[p] <= r).sum()), int(p.sum()), int((dp[g] <= r).sum()), int(g.sum())]
            for r in radii}


def shifted(gt: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """GT moved by (dy, dx) px; the vacated border row / column repeats the nearest row / column."""
    h, w = gt.shape
    ys = np.clip(np.arange(h) - dy, 0, h - 1)
    xs = np.clip(np.arange(w) - dx, 0, w - 1)
    return gt[ys][:, xs]


CROSS = ndi.generate_binary_structure(2, 1)


def crack_dilated(gt: np.ndarray, r: int = 1) -> np.ndarray:
    """GT with the crack class dilated by r px (EDT <= r for r = 1: the 4-neighbour cross), over other classes."""
    out = gt.copy()
    out[ndi.binary_dilation(gt == CRACK, CROSS, iterations=r)] = CRACK
    return out


def binned_ap(pos: np.ndarray, neg: np.ndarray) -> float:
    """AP from per-bin positive / negative counts (bin 0 = lowest probability).  NaN without positives."""
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64)
    n_pos = pos.sum()
    if n_pos == 0:
        return float("nan")
    tp, fp = np.cumsum(pos[::-1]), np.cumsum(neg[::-1])   # thresholds from the top bin down
    recall = tp / n_pos
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    d_recall = np.diff(np.concatenate([[0.0], recall]))
    return float((d_recall * precision).sum())


def _f1(P, R):
    return 2 * P * R / max(P + R, 1e-9)


def summarize(cells: dict, keep_stem=lambda s: True) -> dict:
    """Run-level metrics over the cells passing keep_stem. agg() is m0_analyze's, with the fixed lists (FIX15, ROB13)."""
    st = [s for s in cells if keep_stem(s)]
    if not st:
        return {"n": 0}
    A = agg(cells, keep_stem, (FIX15, ROB13))
    out = {"n": A["n"], "miou_rob": A["miou_rob"], "miou_rob_no07": A["miou_rob_no07"], "miou_fix": A["miou_fix"],
           "miou24": A["miou24"], "fp_absent_px": A["fp_absent_px"],
           "per_class": {c: {"iou": A["iou"][c], "prec": A["prec"][c], "rec": A["rec"][c], "gt_px": int(A["gt"][c]),
                             "gt_cells": int(A["gt_cells"][c])} for c in range(NC)},
           "classes_without_gt": [c for c in ROB13 if A["gt"][c] == 0]}
    for name, c in (("crack", CRACK), ("inact", INACT)):
        out[f"{name}_iou"], out[f"{name}_prec"], out[f"{name}_rec"] = A["iou"][c], A["prec"][c], A["rec"][c]
    for r in RADII:
        key = f"crack_rel{r}"
        if all(key in cells[s] for s in st):
            v = np.sum([cells[s][key] for s in st], 0)
            P, R = v[0] / max(v[1], 1), v[2] / max(v[3], 1)
            out[f"relP{r}"], out[f"relR{r}"], out[f"relF1_{r}"] = P, R, _f1(P, R)
    for k in ("cc_rec50_20", "cc_recany_20", "cc_prec_20", "cc_n_20", "in_cc_rec50", "in_cc_prec", "in_cc_n"):
        out[k] = A[k]
    if all("crack_h1000_pos" in cells[s] for s in st):
        pos = np.sum([cells[s]["crack_h1000_pos"] for s in st], 0)
        neg = np.sum([cells[s]["crack_h1000_neg"] for s in st], 0)
        out["crack_ap"] = binned_ap(pos, neg)
        out["crack_bin0_share"] = float(pos[0] / max(pos.sum(), 1))
        out["crack_pband_gt_share"] = (A["pband_gt"] / max(A["pband_gt"].sum(), 1)).tolist()
    return out


def subsets(stems: list[str], set_name: str, noisy: dict, twins: dict, celltypes: dict | None) -> dict:
    """Named stem filters: all, -noisy, -twins, -twins-noisy (lists fixed per set), per source, per cell type."""
    nz, tw = set(noisy.get(set_name, [])), set(twins.get(set_name, []))
    out = {"all": lambda s: True}
    if nz:
        out["-noisy"] = lambda s, nz=nz: s not in nz
    if tw:
        out["-twins"] = lambda s, tw=tw: s not in tw
        out["-twins-noisy"] = lambda s, tw=tw, nz=nz: s not in tw and s not in nz
    for so in sorted({s.split("_")[0] for s in stems}):
        out[f"src:{so}"] = lambda s, so=so: s.split("_")[0] == so
    if celltypes is not None:
        for ct in sorted({celltypes.get(s, "unknown") for s in stems}):
            out[f"type:{ct}"] = lambda s, ct=ct: celltypes.get(s, "unknown") == ct
    return out
