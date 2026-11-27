"""elbench x3: the shared operating-point module (WAVE2_REVIEW X3, X4, section 5). Every arm and the baseline use it.

Operating points (per arm, per seed; a choice is made for each held-out fold k on the OTHER folds' out-of-fold cells of
the same seed, never on fold k):
  OP-A  argmax (the dump's pred). Primary.
  OP-F  crack bias b (crack where m_crack + b > 0, else oth) maximising pooled relF1@2 on the fit cells, among biases whose
        pooled relP@2 is not below the argmax relP@2 on the same fit cells minus 0.05.
  OP-W  crack bias whose pooled width ratio (predicted / GT crack px) on the fit cells is closest to the BASELINE arm's
        argmax width ratio on the same fit cells (same seed if the baseline has it, else the mean over its seeds).
  Frontier (descriptive, all out-of-fold cells): relR@2 at the baseline's argmax relP@2, and relP@2 at its relR@2,
  read off each arm's bias curve by linear interpolation.
Ties: the candidate with the smaller priority (|b| for biases) wins, then the earlier one.

Per-cell crack counts (exact; = m0 / bench_score formulas on (gt == 14) & keep and (map == 14) & keep):
  CNT = tp (strict), pp (pred px), gp (GT px), p1, g1, p2, g2 (pred px within r of GT; GT px within r of pred; r = 1, 2).
Guards from full records (records()): width ratio, mean predicted width (px per skeleton px, bench/skel.py), relP@2 beside
relR@2, relF1@1, false-alarm px on crack-free cells and the share of crack-free cells with >= 50 predicted crack px,
component recall / precision, any-hit recall, inactive P / R / region precision, mIoU-R13; per source and per cell type.
Uncertainty: two-stage paired bootstrap (B6 verdict rule): (a) the bootstrap groups (cv5v2_groups.tsv) with replacement;
(b) per fold and arm one seed drawn uniformly from the arm's seeds; metric pooled over the drawn cells.
"""
from __future__ import annotations

import hashlib
import math
import random

import numpy as np
from scipy import ndimage as ndi

from .m0core import CRACK, INACT, NC, cell_stats
from .score_ext import ROB13, rel_counts, summarize
from .skel import skeletonize

CNT = ("tp", "pp", "gp", "p1", "g1", "p2", "g2")
OP_GRID = tuple(float(b) for b in np.arange(-6.0, 6.0001, 0.25))
OPF_RELP_DROP = 0.05
HEADLINE = ("crack_iou", "relF1_2", "inact_iou", "miou_rob")
GUARD_KEYS = ("relP2", "relR2", "relF1_1", "relF1_2", "crack_iou", "width_ratio", "mean_width", "fa_px", "fa_share50",
              "cc_rec50_20", "cc_recany_20", "cc_prec_20", "inact_iou", "inact_prec", "inact_rec", "in_cc_rec50",
              "in_cc_prec", "miou_rob")
CROSS = ndi.generate_binary_structure(2, 1)
SQ = np.ones((3, 3), bool)


# ---------------------------------------------------------------- candidates (picklable specs)
def bias_cands(grid=OP_GRID) -> list[tuple]:
    return [("argmax",)] + [("bias", float(b)) for b in grid]


def priority(c: tuple) -> float:
    if c[0] == "argmax":
        return -1.0
    if c[0] == "bias":
        return abs(c[1])
    if c[0] == "dti":                     # less growth first, then the smaller seed threshold
        return abs(c[1] - c[2]) * 100 + abs(c[1])
    if c[0] == "morph":
        return {"none": 0, "erode1_cross": 1, "dilate1_cross": 1, "dilate1_3x3": 2}[c[1]]
    raise ValueError(c)


def cname(c: tuple) -> str:
    if c[0] == "argmax":
        return "argmax"
    if c[0] == "bias":
        return f"b{c[1]:+.2f}"
    if c[0] == "dti":
        return f"dti{c[1]:+g}/{c[2]:+g}"
    return f"morph:{c[1]}"


def crack_mask(c: tuple, d: dict) -> np.ndarray:
    """Crack px of candidate c on one cell's dump d (keys pred, oth, m_crack)."""
    if c[0] == "argmax":
        return d["pred"] == CRACK
    if c[0] == "bias":
        return (d["m_crack"].astype(np.float32) + np.float32(c[1])) > 0
    if c[0] == "dti":
        from .postproc.hysteresis import dti_mask
        return dti_mask(d["m_crack"].astype(np.float32), c[1], c[2])
    if c[0] == "morph":
        from .postproc.src_calib import morph
        return morph(d["pred"] == CRACK, c[1])
    raise ValueError(c)


def class_map(c: tuple, d: dict) -> np.ndarray:
    if c[0] == "argmax":
        return d["pred"]
    return np.where(crack_mask(c, d), CRACK, d["oth"]).astype(np.uint8)


# ---------------------------------------------------------------- per-cell counts
class CellGT:
    """GT side of one cell, computed once: crack mask in keep, its EDT, GT px."""

    def __init__(self, gt: np.ndarray, keep: np.ndarray | None):
        self.k = np.ones_like(gt, bool) if keep is None else keep
        self.g = (gt == CRACK) & self.k
        self.gp = int(self.g.sum())
        self.dg = ndi.distance_transform_edt(~self.g) if self.gp else None


def crack_counts(p_raw: np.ndarray, G: CellGT) -> np.ndarray:
    p = p_raw & G.k
    pp = int(p.sum())
    out = np.zeros(7, np.int64)
    out[1], out[2] = pp, G.gp
    if pp == 0 or G.gp == 0:
        return out
    out[0] = int((p & G.g).sum())
    dgp = G.dg[p]
    out[3], out[5] = int((dgp <= 1).sum()), int((dgp <= 2).sum())
    u = p | G.g                                           # every p px lies in this box, so the crop EDT is exact
    ys, xs = np.nonzero(u)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    dp = ndi.distance_transform_edt(~p[y0:y1, x0:x1])
    dpg = dp[G.g[y0:y1, x0:x1]]
    out[4], out[6] = int((dpg <= 1).sum()), int((dpg <= 2).sum())
    return out


def sweep_cell(d: dict, G: CellGT, cands: list[tuple]) -> np.ndarray:
    """(K, 7) counts; identical crack masks are counted once."""
    res = np.zeros((len(cands), 7), np.int64)
    cache = {}
    for i, c in enumerate(cands):
        m = crack_mask(c, d)
        key = hashlib.md5(np.packbits(m).tobytes()).digest()
        if key not in cache:
            cache[key] = crack_counts(m, G)
        res[i] = cache[key]
    return res


# ---------------------------------------------------------------- pooled metrics from counts
def cmetrics(c) -> dict:
    tp, pp, gp, p1, g1, p2, g2 = (float(x) for x in c)
    P1, R1, P2, R2 = p1 / max(pp, 1), g1 / max(gp, 1), p2 / max(pp, 1), g2 / max(gp, 1)
    f = lambda P, R: 2 * P * R / max(P + R, 1e-9)  # noqa: E731
    den = pp + gp - tp
    return {"crack_iou": tp / den if den > 0 else float("nan"), "relP2": P2, "relR2": R2, "relF1_2": f(P2, R2),
            "relP1": P1, "relR1": R1, "relF1_1": f(P1, R1), "width_ratio": pp / gp if gp else float("nan")}


def _vec(pooled: np.ndarray, key: str) -> np.ndarray:
    return np.array([cmetrics(r)[key] for r in pooled], float)


def choose(pooled: np.ndarray, cands: list[tuple], objective: str, target: float | None = None,
           allowed: np.ndarray | None = None) -> int:
    """Index of the best candidate on pooled (K, 7) counts. objective: 'relF1_2', 'crack_iou', 'width' (closest to target)."""
    if objective == "width":
        assert target is not None and math.isfinite(target)
        v = -np.abs(_vec(pooled, "width_ratio") - target)
    else:
        v = _vec(pooled, objective)
    v = np.where(np.isfinite(v), v, -np.inf)
    if allowed is not None:
        v = np.where(allowed, v, -np.inf)
    best = np.max(v)
    assert np.isfinite(best), "no admissible candidate"
    tied = [i for i in range(len(cands)) if v[i] >= best - 1e-12]
    return min(tied, key=lambda i: (priority(cands[i]), i))


def crossfit(counts: np.ndarray, folds: np.ndarray, cands: list[tuple], objective: str,
             cell_mask: np.ndarray | None = None, target_by_fold: dict | None = None,
             relp_guard: float | None = None) -> dict:
    """{fold k: candidate index} chosen on cells with fold != k (and cell_mask). counts (n, K, 7), folds (n,)."""
    out = {}
    for k in sorted(set(int(f) for f in folds)):
        fit = folds != k
        if cell_mask is not None:
            fit = fit & cell_mask
        assert not (fit & (folds == k)).any()
        pooled = counts[fit].sum(0)
        allowed = None
        if relp_guard is not None:
            ia = [i for i, c in enumerate(cands) if c[0] == "argmax"][0]
            allowed = _vec(pooled, "relP2") >= cmetrics(pooled[ia])["relP2"] - relp_guard
        out[k] = choose(pooled, cands, objective, target_by_fold[k] if target_by_fold else None, allowed)
    return out


def width_from_records(cells: dict, stems) -> float:
    pp = gp = 0
    for s in stems:
        C = np.asarray(cells[s]["conf"], np.int64).reshape(NC, NC)
        pp += int(C[:, CRACK].sum()); gp += int(C[CRACK].sum())
    return pp / gp if gp else float("nan")


def operating_points(counts, folds, cands, base_width_by_fold: dict) -> dict:
    """{'OP-A', 'OP-F', 'OP-W'} -> {fold: candidate index} for one arm and seed (cands = bias_cands())."""
    ia = [i for i, c in enumerate(cands) if c[0] == "argmax"][0]
    return {"OP-A": {int(k): ia for k in sorted(set(int(f) for f in folds))},
            "OP-F": crossfit(counts, folds, cands, "relF1_2", relp_guard=OPF_RELP_DROP),
            "OP-W": crossfit(counts, folds, cands, "width", target_by_fold=base_width_by_fold)}


def frontier(curve_counts: np.ndarray, cands: list[tuple], ref_relp: float, ref_relr: float) -> dict:
    """Bias curve (pooled over all out-of-fold cells): relR@2 at relP@2 = ref_relp and relP@2 at relR@2 = ref_relr."""
    pts = sorted((cmetrics(r)["relP2"], cmetrics(r)["relR2"]) for r, c in zip(curve_counts, cands) if c[0] == "bias")
    P = np.array([p for p, _ in pts]); R = np.array([r for _, r in pts])
    def at(x, xs, ys):
        o = np.argsort(xs)
        xs, ys = xs[o], ys[o]
        if x < xs[0] or x > xs[-1]:
            return float("nan")
        return float(np.interp(x, xs, ys))
    return {"relR2_at_ref_relP2": at(ref_relp, P, R), "relP2_at_ref_relR2": at(ref_relr, R, P),
            "ref_relP2": ref_relp, "ref_relR2": ref_relr}


# ---------------------------------------------------------------- full records and guards
def record(cmap: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, pc: np.ndarray | None) -> dict:
    """bench_score.record (m0 cell_stats + crack_rel1 / rel3) plus crack_skel = [pred skeleton px, GT skeleton px]."""
    r = cell_stats(cmap, gt, keep, pc)
    r.update(rel_counts(cmap, gt, keep, radii=(1, 3)))
    k = np.ones_like(gt, bool) if keep is None else keep
    r["crack_skel"] = [int(skeletonize((cmap == CRACK) & k).sum()), int(skeletonize((gt == CRACK) & k).sum())]
    return r


def guards(cells: dict, keep_stem=lambda s: True) -> dict:
    st = [s for s in cells if keep_stem(s)]
    if not st:
        return {"n": 0}
    m = summarize(cells, keep_stem)
    pp = gp = fa = n_cf = n50 = sk = 0
    for s in st:
        C = np.asarray(cells[s]["conf"], np.int64).reshape(NC, NC)
        p, g = int(C[:, CRACK].sum()), int(C[CRACK].sum())
        pp += p; gp += g
        if g == 0:
            n_cf += 1; fa += p; n50 += p >= 50
        sk += cells[s].get("crack_skel", [0, 0])[0]
    m["width_ratio"] = pp / gp if gp else float("nan")
    m["mean_width"] = pp / sk if sk else float("nan")
    m["fa_px"], m["fa_cells"], m["fa_share50"] = fa, n_cf, (n50 / n_cf if n_cf else float("nan"))
    return m


# ---------------------------------------------------------------- bootstrap (two-stage, groups then seed per fold x arm)
def _features(cells: dict, stems: list[str]) -> np.ndarray:
    rows = []
    for s in stems:
        c = cells[s]
        C = np.asarray(c["conf"], np.int64)
        pp = int(C.reshape(NC, NC)[:, CRACK].sum()); gp = int(C.reshape(NC, NC)[CRACK].sum())
        cf = int(gp == 0)
        rows.append(np.concatenate([C, c["crack_rel2"], c.get("crack_rel1", [0, 0, 0, 0]),
                                    [cf, cf * pp, cf * int(pp >= 50)]]))
    return np.array(rows, np.int64)


def fmetrics(v: np.ndarray) -> dict:
    C = v[:NC * NC].reshape(NC, NC).astype(float)
    r2, r1 = v[NC * NC:NC * NC + 4].astype(float), v[NC * NC + 4:NC * NC + 8].astype(float)
    cf, fa, f50 = v[-3:].astype(float)
    tp = np.diag(C); gt = C.sum(1); pr = C.sum(0); den = gt + pr - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    rob = [iou[c] for c in ROB13 if gt[c] > 0]
    f = lambda P, R: 2 * P * R / max(P + R, 1e-9)  # noqa: E731
    P2, R2 = r2[0] / max(r2[1], 1), r2[2] / max(r2[3], 1)
    P1, R1 = r1[0] / max(r1[1], 1), r1[2] / max(r1[3], 1)
    return {"crack_iou": iou[CRACK], "relF1_2": f(P2, R2), "inact_iou": iou[INACT],
            "miou_rob": float(np.mean(rob)) if rob else float("nan"), "relP2": P2, "relR2": R2, "relF1_1": f(P1, R1),
            "width_ratio": pr[CRACK] / gt[CRACK] if gt[CRACK] else float("nan"),
            "fa_share50": f50 / cf if cf else float("nan")}


BOOT_KEYS = ("crack_iou", "relF1_2", "inact_iou", "miou_rob", "relP2", "relR2", "relF1_1", "width_ratio", "fa_share50")


def point(arm: dict, stems: list[str]) -> dict:
    """Mean over seeds of the pooled metrics; arm = {seed: {stem: record}}."""
    per = [fmetrics(_features(c, stems).sum(0)) for c in arm.values()]
    return {k: float(np.nanmean([p[k] for p in per])) for k in BOOT_KEYS}


def boot_pair(A: dict, B: dict, stems: list[str], fold_of: dict, groups: dict, n_boot: int = 2000, seed: int = 0,
              paired_seeds: bool = False) -> dict:
    """delta = point(B) - point(A) with a two-stage bootstrap interval and SE (sd of the bootstrap deltas).
    A, B = {seed: {stem: record}} out-of-fold over the same stems. paired_seeds: one seed draw per fold for both (two
    readouts of the same runs, e.g. src_bias vs glob_bias); else one draw per (fold, arm) as b6_verdict."""
    folds = sorted({fold_of[s] for s in stems})
    fidx = {k: np.array([i for i, s in enumerate(stems) if fold_of[s] == k]) for k in folds}
    XA = {sd: _features(c, stems) for sd, c in A.items()}
    XB = {sd: _features(c, stems) for sd, c in B.items()}
    sA, sB = sorted(XA), sorted(XB)
    if paired_seeds:
        assert sA == sB, (sA, sB)
    units = sorted({groups[s] for s in stems})
    uidx = {u: [] for u in units}
    for i, s in enumerate(stems):
        uidx[groups[s]].append(i)
    rng = random.Random(seed)
    pa, pb = point(A, stems), point(B, stems)
    dl = {k: pb[k] - pa[k] for k in BOOT_KEYS}
    draws = {k: [] for k in BOOT_KEYS}
    for _ in range(n_boot):
        w = np.zeros(len(stems), np.int64)
        for _u in range(len(units)):
            w[uidx[units[rng.randrange(len(units))]]] += 1
        va = np.zeros(XA[sA[0]].shape[1], np.int64); vb = np.zeros_like(va)
        for k in folds:
            da = sA[rng.randrange(len(sA))]
            db = da if paired_seeds else sB[rng.randrange(len(sB))]
            ix = fidx[k]
            va += w[ix] @ XA[da][ix]
            vb += w[ix] @ XB[db][ix]
        ma, mb = fmetrics(va), fmetrics(vb)
        for k in BOOT_KEYS:
            draws[k].append(mb[k] - ma[k])
    out = {}
    for k in BOOT_KEYS:
        v = np.array([x for x in draws[k] if np.isfinite(x)])
        out[k] = {"delta": dl[k], "lo": float(np.percentile(v, 2.5)) if len(v) else float("nan"),
                  "hi": float(np.percentile(v, 97.5)) if len(v) else float("nan"),
                  "se": float(v.std(ddof=1)) if len(v) > 1 else float("nan")}
    return {"B": n_boot, "boot_seed": seed, "units": len(units), "paired_seeds": paired_seeds,
            "seeds_A": sA, "seeds_B": sB, "metrics": out}


def margins(aa: dict) -> dict:
    """M(metric) = max(0.01, 2 x SE of the A/A difference)."""
    return {k: max(0.01, 2 * v["se"]) if math.isfinite(v["se"]) else None for k, v in aa["metrics"].items()}
