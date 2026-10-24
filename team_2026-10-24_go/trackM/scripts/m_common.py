"""Track M shared scoring helpers (copied verbatim from m0_audit.py, which M0 used; no change in logic)."""
from __future__ import annotations

import numpy as np
import torch
from scipy import ndimage as ndi

NC, CRACK, INACT = 24, 14, 11
S8 = np.ones((3, 3), bool)


def comps(gt_m: np.ndarray, pr_m: np.ndarray, near_pr: np.ndarray | None, near_gt: np.ndarray | None):
    """GT components: [size, hit] where hit = px of the component covered (by pred, or within 2 px of pred if near_pr).
    Pred components: [size, hit] with hit = px overlapping GT (or within 2 px of GT if near_gt)."""
    out = {}
    lg, ng = ndi.label(gt_m, S8)
    cov = near_pr if near_pr is not None else pr_m
    if ng:
        sz = np.bincount(lg.ravel(), minlength=ng + 1)[1:]
        ht = np.bincount(lg[cov].ravel(), minlength=ng + 1)[1:]
        out["gt"] = np.stack([sz, ht], 1).tolist()
    else:
        out["gt"] = []
    lp, npc = ndi.label(pr_m, S8)
    cov = near_gt if near_gt is not None else gt_m
    if npc:
        sz = np.bincount(lp.ravel(), minlength=npc + 1)[1:]
        ht = np.bincount(lp[cov].ravel(), minlength=npc + 1)[1:]
        out["pr"] = np.stack([sz, ht], 1).tolist()
    else:
        out["pr"] = []
    return out


BANDS = [0, 0.001, 0.1, 0.5, 0.95, 1.0001]


def cell_stats(pred: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, pc: np.ndarray | None = None) -> dict:
    k = np.ones_like(gt, bool) if keep is None else keep
    assert gt[k].max() < NC and pred.max() < NC, "label id out of range"
    conf = np.bincount(gt[k].astype(np.int64) * NC + pred[k], minlength=NC * NC)
    g, p = (gt == CRACK) & k, (pred == CRACK) & k
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    rel = [int((dg[p] <= 2).sum()), int(p.sum()), int((dp[g] <= 2).sum()), int(g.sum())]
    o = {"conf": conf.tolist(), "crack_rel2": rel,
         "crack_cc": comps(g, p, (dp <= 2) & k, (dg <= 2) & k)}
    gi, pi = (gt == INACT) & k, (pred == INACT) & k
    o["inact_cc"] = comps(gi, pi, None, None)
    if pc is not None:  # p(crack) bands on GT crack px and on GT non-crack px
        o["crack_pband_gt"] = np.histogram(pc[g], BANDS)[0].tolist()
        o["crack_pband_neg"] = np.histogram(pc[k & ~g], BANDS)[0].tolist()
    return o


def dihedral(x: torch.Tensor, i: int, inv: bool = False) -> torch.Tensor:
    r, f = i % 4, i // 4
    if not inv:
        x = torch.rot90(x, r, (2, 3))
        return torch.flip(x, (3,)) if f else x
    if f:
        x = torch.flip(x, (3,))
    return torch.rot90(x, -r, (2, 3))


