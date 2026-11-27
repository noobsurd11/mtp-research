"""elbench m0 core: the Track M per-cell record and its pooled aggregation, copied LINE-IDENTICAL from
m0_audit.py d36f7438 (comps, BANDS, cell_stats; = m0_audit_tau d77241bb = b6_score 981b5f29) and m0_analyze.py d5adbe6b
(src, agg). tests/test_bench_m0core_ast.py asserts the identity by AST against the vendored copies in tests/ref/.
Do not edit the copied block; extensions live in bench/score_ext.py.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

NC, CRACK, INACT = 24, 14, 11
S8 = np.ones((3, 3), bool)


# ---- copied from m0_audit.py d36f7438 (lines from `def comps` to before `def dihedral`) ----
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
        b = np.clip((pc * 1000).astype(int), 0, 999)  # 1,000-bin histograms as the P-series binned AP (per source AP)
        o["crack_h1000_pos"] = np.bincount(b[g], minlength=1000).tolist()
        o["crack_h1000_neg"] = np.bincount(b[k & ~g], minlength=1000).tolist()
    return o


# ---- copied from m0_analyze.py d5adbe6b (`def src` and `def agg`) ----
DEFECT = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23]


def src(s):
    return s.split("_")[0]


def agg(cells: dict, keep, cl=None) -> dict:
    st = [s for s in cells if keep(s)]
    C = sum(np.array(cells[s]["conf"], np.int64).reshape(NC, NC) for s in st)
    tp = np.diag(C).astype(float); gt = C.sum(1); pr = C.sum(0)
    den = gt + pr - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    prec = np.where(pr > 0, tp / np.maximum(pr, 1), np.nan)
    rec = np.where(gt > 0, tp / np.maximum(gt, 1), np.nan)
    rel = np.sum([cells[s]["crack_rel2"] for s in st], 0)
    rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    out = {"n": len(st), "iou": iou, "prec": prec, "rec": rec, "gt": gt, "pr": pr,
           "miou24": np.nanmean(iou), "miou_gt": np.nanmean(np.where(gt > 0, iou, np.nan)),
           "miou_fix": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[0]]) if cl else np.nan,
           "miou_rob": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[1]]) if cl else np.nan,
           "miou_rob_no07": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[1] if c not in (0, 7)]) if cl else np.nan,
           "miou_gt_no07": np.nanmean([iou[c] if gt[c] > 0 and c not in (0, 7) else np.nan for c in range(NC)]),
           "fp_absent_px": int(sum(pr[c] for c in range(NC) if gt[c] == 0)),
           "gt_cells": np.array([sum(1 for s in st if np.array(cells[s]["conf"]).reshape(NC, NC)[c].sum() > 0) for c in range(NC)]),
           "pband_gt": np.sum([cells[s].get("crack_pband_gt", [0] * 5) for s in st], 0),
           "pband_neg": np.sum([cells[s].get("crack_pband_neg", [0] * 5) for s in st], 0),
           "miou_def_gt": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in DEFECT]),
           "relP2": rP, "relR2": rR, "relF1": 2 * rP * rR / max(rP + rR, 1e-9)}
    # crack components: GT comp "found" if >= 50% of its px within 2 px of a prediction; also any-hit
    g = [c for s in st for c in cells[s]["crack_cc"]["gt"]]
    p = [c for s in st for c in cells[s]["crack_cc"]["pr"]]
    for mn in (1, 20):
        gg = [c for c in g if c[0] >= mn]
        out[f"cc_rec50_{mn}"] = np.mean([c[1] >= 0.5 * c[0] for c in gg]) if gg else np.nan
        out[f"cc_recany_{mn}"] = np.mean([c[1] > 0 for c in gg]) if gg else np.nan
        out[f"cc_n_{mn}"] = len(gg)
        pp = [c for c in p if c[0] >= mn]
        out[f"cc_prec_{mn}"] = np.mean([c[1] > 0 for c in pp]) if pp else np.nan
    gi = [c for s in st for c in cells[s]["inact_cc"]["gt"] if c[0] >= 100]
    out["in_cc_rec50"] = np.mean([c[1] >= 0.5 * c[0] for c in gi]) if gi else np.nan
    out["in_cc_n"] = len(gi)
    pi = [c for s in st for c in cells[s]["inact_cc"]["pr"] if c[0] >= 100]
    out["in_cc_prec"] = np.mean([c[1] > 0 for c in pi]) if pi else np.nan
    return out
