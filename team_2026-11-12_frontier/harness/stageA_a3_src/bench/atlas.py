"""elbench stage A3: ci_error_atlas (T10 spec section A0; shared piece S2 of WAVE3_REVIEW: ONE inactive and weak-class
error atlas for the gates of T6, T8, T10 and T13, plus P-GIN part (d) of the gin_ipa verdict line, guard G20).

Pure numpy / scipy on per-cell arrays (testable without files). The driver is scripts/bench_atlas.py.

Per cell (one stem, all seeds of the arm): `cell_atlas(g, keep, dumps, img)` returns one flat dict of integer counts per
seed (the features; seed-independent GT counts are repeated in every seed), a cell row, region rows and label-issue
candidates. Pooled shares are ratios of sums of features, so every share gets the same two-stage group bootstrap
(330 groups of cv5v2_groups.tsv, then one seed per fold, as crossfit_op.boot_pair), a leave-top-3-groups-out value
(the 3 groups with most GT px of the class the share reads) and per-source and per-fold values.

Notation (T10 A0): G GT index mask, P the dump's pred (OP-A), K = not ignore, GI = G==11 & K, GC = G==14 & K,
PI = P==11 & K, PC = P==14 & K. Components 8-connected. dC = distance to the nearest GT crack px; bI = px within 3 px of
the GT inactive boundary (inside or outside).
"""
from __future__ import annotations

import math
import random

import numpy as np
from scipy import ndimage as ndi

NCLS = 24
BG, PAD, INACT, CRACK = 0, 7, 11, 14
WEAK = {13: "material", 15: "gridline", 16: "splice", 20: "edge_dark"}
LQ = (11, 13, 15, 16, 20)                    # label-quality classes (crack excluded, T10 A0 (e))
P009_CLS = (11, 13, 14, 15, 16, 20)
NAME = {0: "background", 11: "inactive", 13: "material", 14: "crack", 15: "gridline", 16: "splice", 20: "edge_dark"}
SQ = np.ones((3, 3), bool)

R_MIN_INACT, R_MIN_WEAK = 100, 20
BI_RAD, DC_RAD = 3, 3
MISS_COV, SPUR_FRAC = 0.10, 0.10            # T10: region missed if coverage < 10%; spurious if < 10% of px on GI
T6_MISS_COV, T8_MISS_COV = 0.20, 0.50       # T6 inactive_anatomy; T8 C3
T6_NEAR = 3                                 # T6 false region: < 10% of px on GT 11 dilated 3 px
SPUR_PC_RAD = 5
AT_RAD = 2                                  # (b) crack at inactive: GT crack px within 2 px of GI
BIAS_GRID = tuple(float(x) for x in np.round(np.arange(-2.0, 6.0001, 0.25), 2))   # (c) single-class oracle
MH_EDGES = np.arange(-30.0, 2.0001, 0.25)   # (c) margin histogram (values clipped into [-30, 2))
SOFTMIN_T = 0.1
COCO_FL, ML_P, ML_BG, ML_MIN, ML_MIN_INACT = 0.05, 0.9, 0.8, 50, 200
RULE_PC_MIN, RULE_D, HOLE_PI_MIN, HOLE_MIN_INACT = 0.2, (5, 10), 0.05, 50
GT_CR_D = (3, 5, 10)
FN_B = ("ov", "mi", "ca", "bd", "in")       # FN-overlap, FN-missed, FN-crackadj, FN-boundary, FN-interior
FP_B = ("oc", "sp", "ca", "bd", "ot")       # FP-on-crack, FP-spurious, FP-crackadj, FP-boundary, FP-other

# B1 label audit (team_2026-10-29_features/b1_audit/b1_flags_A50.tsv, train inactive FL, 9 cells; agreement only)
B1_INACT_FL = ("ARTS_00024_r2_c1", "CFVS_00016_r7_c4", "CFVS_00021_r5_c2", "CFVS_00045_r4_c3", "CFVS_00126_r5_c3",
               "CFVS_00140_r4_c2", "CFVS_00146_r8_c3", "CSIR_00055_r6_c3", "CSIR_00092_r3_c2")
# Positive control (T10 A0 (e)): v1 crack that v1.1 removed. masks_v11/CHANGES.tsv: E2 wrong mask restored (1 cell) and
# E1_scuff_to_ignore rows with class_from_v1 14 in train (6 cells). The star cell CFVS_00024_r3_c3 is not scuff.
CONTROL_CELLS = ("BMRK_00031_cell0091", "ARTS_00051_r6_c2", "CSIR_00092_r11_c5", "CSIR_00117_r8_c4",
                 "CSIR_00155_r5_c5", "CSIR_00161_r4_c6", "CSIR_00176_r5_c2")
CONTROL_WORST = 0.10


# ---------------------------------------------------------------- small helpers
def comps(mask):
    return ndi.label(mask, structure=SQ)


def csum(lab, n, x) -> np.ndarray:
    """Per-component sum of x (index 0 = outside every component)."""
    return np.bincount(lab.ravel(), weights=np.asarray(x, np.float64).ravel(), minlength=n + 1)


def cmin(lab, n, x) -> np.ndarray:
    if n == 0:
        return np.zeros(0)
    return np.asarray(ndi.minimum(x, lab, index=np.arange(1, n + 1)), np.float64)


def lut(sel) -> np.ndarray:
    t = np.zeros(len(sel) + 1, bool)
    t[1:] = sel
    return t


def dist_to(mask) -> np.ndarray:
    """Euclidean distance of every px to the nearest True px of mask (inf if mask is empty)."""
    if not mask.any():
        return np.full(mask.shape, np.inf)
    return ndi.distance_transform_edt(~mask)


def band(mask, r) -> np.ndarray:
    """px within r px of the boundary of mask, inside or outside."""
    if not mask.any():
        return np.zeros(mask.shape, bool)
    if mask.all():
        return np.zeros(mask.shape, bool)
    din = ndi.distance_transform_edt(mask)
    dout = ndi.distance_transform_edt(~mask)
    return (mask & (din <= r)) | (~mask & (dout <= r))


def softmin(s, t=SOFTMIN_T) -> float:
    s = np.asarray(s, np.float64).ravel()
    if s.size == 0:
        return float("nan")
    w = np.exp(-(s - s.min()) / t)
    return float((s * w).sum() / w.sum())


def hist_shape(img, content) -> float:
    """(p50 - p5) / (p95 - p5) on content px (idea 11 / T7 P-GIN (b)); nan if degenerate."""
    v = np.asarray(img, np.float64)[content]
    if v.size < 100:
        return float("nan")
    p5, p50, p95 = np.percentile(v, [5, 50, 95])
    return float((p50 - p5) / (p95 - p5)) if p95 > p5 else float("nan")


def top2(L):
    a1 = L.argmax(0)
    m1 = np.take_along_axis(L, a1[None], 0)[0]
    L2 = L.copy()
    np.put_along_axis(L2, a1[None], -np.inf, 0)
    return a1, m1, L2.max(0)


def margin(L, c, a1, m1, m2) -> np.ndarray:
    """logp_c - max_{k != c} logp_k."""
    return L[c] - np.where(a1 == c, m2, m1)


def n_above(sorted_vals, grid) -> np.ndarray:
    """For each b in grid: number of values v with v + b > 0."""
    return len(sorted_vals) - np.searchsorted(sorted_vals, -np.asarray(grid, np.float64), side="right")


def crack_counts(pc, gc) -> dict:
    """tp, pp, gp, p2, g2 on already-kept masks (= crossfit_op.crack_counts at r = 2)."""
    pp, gp = int(pc.sum()), int(gc.sum())
    o = {"ck_pp": pp, "ck_gp": gp, "ck_tp": 0, "ck_p2": 0, "ck_g2": 0}
    if pp and gp:
        o["ck_tp"] = int((pc & gc).sum())
        o["ck_p2"] = int((dist_to(gc)[pc] <= 2).sum())
        o["ck_g2"] = int((dist_to(pc)[gc] <= 2).sum())
    return o


# ---------------------------------------------------------------- one cell, all seeds
def cell_atlas(g, keep, dumps, img=None, stem: str = "") -> dict:
    """g (H, W) uint8 GT; keep bool (H, W) or None; dumps = [per-seed dict with pred, p_crack, p_inact, logp].
    img (H, W) grey image or None (P-GIN (d) histogram shape)."""
    g = np.asarray(g)
    K = np.ones(g.shape, bool) if keep is None else np.asarray(keep, bool)
    assert int(g[K].max(initial=0)) < NCLS, f"{stem}: GT class >= {NCLS} on a kept px"
    GI, GC = (g == INACT) & K, (g == CRACK) & K
    dC = dist_to(GC)
    bI = band(GI, BI_RAD)
    dGI = dist_to(GI)
    nearGI3 = dGI <= T6_NEAR
    glab, gn = comps(GI)
    gsize = csum(glab, gn, np.ones_like(GI))[1:]
    gbig = gsize >= R_MIN_INACT
    gdc = cmin(glab, gn, dC)
    L = [np.maximum(np.asarray(d["logp"], np.float32), np.float32(-1e4)) for d in dumps]
    E = [np.exp(x) for x in L]
    pb = np.mean(E, axis=0)

    # (e) CoCo of GT inactive components (needed by G-paste) and of the weak classes
    issues, regions = [], []
    coco_in = (csum(glab, gn, pb[INACT])[1:] / np.maximum(gsize, 1)) if gn else np.zeros(0)
    coco_in_s = [csum(glab, gn, e[INACT])[1:] / np.maximum(gsize, 1) for e in E] if gn else [np.zeros(0)] * len(E)
    fl_in = gbig & (coco_in < COCO_FL) & np.all([c < COCO_FL for c in coco_in_s], axis=0) if gn else np.zeros(0, bool)
    for c in LQ:
        if c == INACT:
            lab, n, size, cc, ccs, rmin = glab, gn, gsize, coco_in, coco_in_s, R_MIN_INACT
        else:
            lab, n = comps((g == c) & K)
            size = csum(lab, n, np.ones(g.shape))[1:]
            cc = csum(lab, n, pb[c])[1:] / np.maximum(size, 1)
            ccs = [csum(lab, n, e[c])[1:] / np.maximum(size, 1) for e in E]
            rmin = R_MIN_WEAK
        for j in range(n):
            if size[j] >= rmin:
                agree = int(sum(x[j] < COCO_FL for x in ccs))
                if cc[j] < COCO_FL and agree == len(E):
                    issues.append({"stem": stem, "class": NAME[c], "type": "FL", "px": int(size[j]),
                                   "score": round(float(cc[j]), 5), "seeds_agreeing": agree})
    pa = pb.argmax(0)
    for c in LQ:
        lab, n = comps((pa == c) & K)
        if not n:
            continue
        size = csum(lab, n, np.ones(g.shape))[1:]
        onbg = csum(lab, n, (g == BG) & K)[1:]
        mp = csum(lab, n, pb[c])[1:] / np.maximum(size, 1)
        mps = [csum(lab, n, e[c])[1:] / np.maximum(size, 1) for e in E]
        rmin = ML_MIN_INACT if c == INACT else ML_MIN
        for j in range(n):
            if size[j] >= rmin and onbg[j] >= ML_BG * size[j] and mp[j] >= ML_P:
                issues.append({"stem": stem, "class": NAME[c], "type": "ML", "px": int(size[j]),
                               "score": round(float(mp[j]), 5), "seeds_agreeing": int(sum(x[j] >= ML_P for x in mps))})

    # seed-independent GT features
    base = {"gi_px": int(GI.sum()), "gc_px": int(GC.sum()), "gt_r100": int(gbig.sum()), "n_cell": 1,
            "has_gi": int(GI.any())}
    for d_ in GT_CR_D:
        base[f"gt_cr{d_}"] = int((gbig & (gdc <= d_)).sum())
    for c in WEAK:
        base[f"w{c}_gp"] = int(((g == c) & K).sum())
    at = GC & (dGI <= AT_RAD)
    el = GC & ~at

    feats, covs = [], []
    for si, d in enumerate(dumps):
        P = np.asarray(d["pred"])
        f = dict(base)
        PI, PC = (P == INACT) & K, (P == CRACK) & K
        TP, FN, FP = GI & PI, GI & ~PI, PI & ~GI
        f.update(tp=int(TP.sum()), fn=int(FN.sum()), fp=int(FP.sum()), pi_px=int(PI.sum()))
        cov = (csum(glab, gn, TP)[1:] / np.maximum(gsize, 1)) if gn else np.zeros(0)
        covs.append(cov)
        missed = gbig & (cov < MISS_COV)
        inm = lut(missed)[glab]
        # (a) FN buckets, first that applies
        rem = FN.copy()
        fnb = {}
        for b, m in (("ov", P == CRACK), ("mi", inm), ("ca", dC <= DC_RAD), ("bd", bI)):
            fnb[b] = rem & m
            rem &= ~m
        fnb["in"] = rem
        # predicted inactive components
        plab, pn = comps(PI)
        psize = csum(plab, pn, np.ones_like(PI))[1:]
        pongi = csum(plab, pn, GI)[1:]
        spur = pongi < SPUR_FRAC * psize
        insp = lut(spur)[plab]
        rem = FP.copy()
        fpb = {}
        for b, m in (("oc", GC), ("sp", insp), ("ca", dC <= DC_RAD), ("bd", bI)):
            fpb[b] = rem & m
            rem &= ~m
        fpb["ot"] = rem
        for b in FN_B:
            f[f"fn_{b}"] = int(fnb[b].sum())
        for b in FP_B:
            f[f"fp_{b}"] = int(fpb[b].sum())
        dPC = dist_to(PC)
        pnear = cmin(plab, pn, dPC) <= SPUR_PC_RAD
        for nm, sel in (("pc", pnear), ("nopc", ~pnear)):
            f[f"fp_sp_{'gi' if GI.any() else 'nogi'}_{nm}"] = int((fpb["sp"] & lut(sel)[plab]).sum())
        # oracle inputs
        f["fn_in_missed_all"] = int((FN & inm).sum())
        f["fp_in_spur_all"] = int((FP & insp).sum())
        f["tp_in_spur"] = int((TP & insp).sum())
        # region counts: majority error bucket per component
        if gn:
            fnc = np.stack([csum(glab, gn, fnb[b])[1:] for b in FN_B])
            has = fnc.sum(0) > 0
            maj = fnc.argmax(0)
            f["rc_fn_has"] = int(has.sum())
            for i, b in enumerate(FN_B):
                f[f"rc_fn_{b}"] = int((has & (maj == i)).sum())
        else:
            f["rc_fn_has"] = 0
        if pn:
            fpc = np.stack([csum(plab, pn, fpb[b])[1:] for b in FP_B])
            has = fpc.sum(0) > 0
            maj = fpc.argmax(0)
            f["rc_fp_has"] = int(has.sum())
            for i, b in enumerate(FP_B):
                f[f"rc_fp_{b}"] = int((has & (maj == i)).sum())
            f["rc_spur"] = int((spur & has).sum())
            f["p_r100"] = int((psize >= R_MIN_INACT).sum())
            f["p_r100_true"] = int(((psize >= R_MIN_INACT) & ~spur).sum())
        else:
            f["rc_fp_has"] = 0
        f["r_missed"] = int(missed.sum())
        f["r_found50"] = int((gbig & (cov >= 0.5)).sum())
        f["r_missed_fl"] = int((missed & fl_in).sum()) if gn else 0
        f["fn_mi_fl"] = int((fnb["mi"] & lut(fl_in)[glab]).sum()) if gn else 0
        # T6 inactive_anatomy
        t6m = gbig & (cov < T6_MISS_COV)
        t6miss = FN & lut(t6m)[glab]
        f["t6_fn_miss"] = int(t6miss.sum())
        f["t6_r_miss"] = int(t6m.sum())
        pnear3 = csum(plab, pn, nearGI3 & PI)[1:]
        t6f = (psize >= R_MIN_INACT) & (pnear3 < 0.10 * psize)
        f["t6_fp_false"] = int((FP & lut(t6f)[plab]).sum())
        f["t6_r_false"] = int(t6f.sum())
        blind = float(np.asarray(d["p_inact"], np.float32)[K].max(initial=0)) < 0.1
        f["t6_fn_miss_blind"] = f["t6_fn_miss"] if blind else 0
        if f["t6_fn_miss"]:
            for k, v in enumerate(np.bincount(P[t6miss], minlength=256)[:NCLS]):
                if v:
                    f[f"t6_take_{k}"] = int(v)
        for c in WEAK:
            Gc, Pc = (g == c) & K, (P == c) & K
            lab, n = comps(Gc)
            sz = csum(lab, n, np.ones(g.shape))[1:]
            cv = csum(lab, n, Gc & Pc)[1:] / np.maximum(sz, 1)
            mm = (sz >= R_MIN_INACT) & (cv < T6_MISS_COV)
            f[f"t6w{c}_fn"] = int((Gc & ~Pc).sum())
            f[f"t6w{c}_fnmiss"] = int((Gc & ~Pc & lut(mm)[lab]).sum())
            ql, qn = comps(Pc)
            qs = csum(ql, qn, np.ones(g.shape))[1:]
            qnear = csum(ql, qn, (dist_to(Gc) <= T6_NEAR) & Pc)[1:]
            ff = (qs >= R_MIN_INACT) & (qnear < 0.10 * qs)
            f[f"t6w{c}_fp"] = int((Pc & ~Gc).sum())
            f[f"t6w{c}_fpfalse"] = int((Pc & ~Gc & lut(ff)[ql]).sum())
        # T8 C3
        t8m = gbig & (cov < T8_MISS_COV)
        f["t8_fn_miss50"] = int((FN & lut(t8m)[glab]).sum())
        f["t8_r_miss50"] = int(t8m.sum())
        # (b) crack at the overlap
        dPCm = dPC
        for nm, M in (("at", at), ("el", el)):
            f[f"{nm}_n"] = int(M.sum())
            f[f"{nm}_p14"] = int((M & (P == CRACK)).sum())
            f[f"{nm}_p11"] = int((M & (P == INACT)).sum())
            f[f"{nm}_p0"] = int((M & (P == BG)).sum())
            f[f"{nm}_r2"] = int((M & (dPCm <= 2)).sum())
        f["crack_fn"] = int((GC & ~PC).sum())
        f["crack_fn_p11"] = int((GC & ~PC & (P == INACT)).sum())
        cc = crack_counts(PC, GC)
        f.update(cc)
        f["cf"] = int(cc["ck_gp"] == 0)
        f["fa50"] = int(cc["ck_gp"] == 0 and cc["ck_pp"] >= 50)
        # (c) weak classes
        a1, m1, m2 = top2(L[si])
        for c in WEAK:
            Gc, Pc = (g == c) & K, (P == c) & K
            f[f"w{c}_tp"], f[f"w{c}_fn"], f[f"w{c}_fp"] = int((Gc & Pc).sum()), int((Gc & ~Pc).sum()), int((Pc & ~Gc).sum())
            for k, v in enumerate(np.bincount(P[Gc & ~Pc], minlength=256)[:NCLS]):
                if v:
                    f[f"w{c}_fnby{k}"] = int(v)
            for k, v in enumerate(np.bincount(g[Pc & ~Gc], minlength=256)[:NCLS]):
                if v:
                    f[f"w{c}_fpby{k}"] = int(v)
            lab, n = comps(Gc)
            sz = csum(lab, n, np.ones(g.shape))[1:]
            cv = csum(lab, n, Gc & Pc)[1:] / np.maximum(sz, 1)
            f[f"w{c}_r20"] = int((sz >= R_MIN_WEAK).sum())
            f[f"w{c}_r20miss"] = int(((sz >= R_MIN_WEAK) & (cv < MISS_COV)).sum())
            err = (Gc ^ Pc) & K
            f[f"w{c}_err"] = int(err.sum())
            f[f"w{c}_errbnd"] = int((err & band(g == c, 2)).sum())
            m = margin(L[si], c, a1, m1, m2)
            fnm = np.clip(m[Gc & ~Pc], -30.0, 1.999)
            h = np.histogram(fnm, bins=MH_EDGES)[0]
            for i in np.nonzero(h)[0]:
                f[f"w{c}_mh{i}"] = int(h[i])
            tpb = n_above(np.sort(m[Gc]), BIAS_GRID)
            ppb = n_above(np.sort(m[K]), BIAS_GRID)
            for i in range(len(BIAS_GRID)):
                f[f"w{c}_or_tp{i}"], f[f"w{c}_or_pp{i}"] = int(tpb[i]), int(ppb[i])
        # (d) co-occurrence rules (rule a works on pred == 11 as ci_rules.rule_a; px counted in K)
        ev = (P == CRACK) | (np.asarray(d["p_crack"], np.float32) >= RULE_PC_MIN)
        rl, rn = comps(P == INACT)
        rmin_ev = cmin(rl, rn, dist_to(ev))
        f["ra_ncomp"] = int(rn)
        for dd in RULE_D:
            sel = lut(rmin_ev > dd)[rl]
            f[f"ra{dd}_n"] = int((rmin_ev > dd).sum())
            f[f"ra{dd}_px"] = int((sel & K).sum())
            f[f"ra{dd}_gi"] = int((sel & GI).sum())
        U = (P == INACT) | (P == CRACK)
        ul, un = comps(U)
        H = np.zeros(g.shape, bool)
        if un:
            npi = csum(ul, un, P == INACT)[1:]
            objs = ndi.find_objects(ul)
            for k in np.nonzero(npi >= HOLE_MIN_INACT)[0]:
                sl = objs[k]
                Uk = ul[sl] == (k + 1)
                H[sl] |= ndi.binary_fill_holes(Uk) & ~Uk
        H &= (np.asarray(d["p_inact"], np.float32) >= HOLE_PI_MIN) & (P != CRACK)
        f["rb_px"], f["rb_gi"], f["rb_n"] = int((H & K).sum()), int((H & GI).sum()), int(comps(H & K)[1])
        feats.append(f)
        pdpc = cmin(plab, pn, dPC)
        for j in range(pn):
            regions.append({"kind": "pred", "stem": stem, "seed_idx": si, "comp": j + 1, "px": int(psize[j]),
                            "on_gi": round(float(pongi[j] / psize[j]), 4),
                            "near_gi3": round(float(pnear3[j] / psize[j]), 4),
                            "d_pc_min": round(float(pdpc[j]), 2), "spurious": int(spur[j])})
    for j in range(gn):
        regions.append({"kind": "gt", "stem": stem, "comp": j + 1, "px": int(gsize[j]),
                        "d_crack_min": round(float(gdc[j]), 2) if np.isfinite(gdc[j]) else "inf",
                        "coco": round(float(coco_in[j]), 5), "fl": int(bool(fl_in[j])),
                        "cov": ";".join(f"{c[j]:.4f}" for c in covs)})

    # cell row: label-quality scores (e) and P-GIN shape
    s = np.take_along_axis(pb, np.where(K, g, 0)[None].astype(np.int64), 0)[0][K]
    row = {"stem": stem, "gi_px": base["gi_px"], "gc_px": base["gc_px"], "softmin": softmin(s),
           "crack_softmin": softmin(pb[CRACK][GC]) if GC.any() else float("nan"),
           "shape": hist_shape(img, (g != PAD)) if img is not None else float("nan")}
    for c in P009_CLS:
        Gc = (g == c) & K
        def one_minus_iou(pred):
            Pc = (pred == c) & K
            u = int((Gc | Pc).sum())
            return 1.0 - int((Gc & Pc).sum()) / u if u else float("nan")
        row[f"p009_{c}"] = one_minus_iou(pa)
        per = [one_minus_iou(np.asarray(d["pred"])) for d in dumps]
        row[f"p009_{c}_sd"] = float(np.std(per, ddof=1)) if len(per) > 1 and all(np.isfinite(per)) else float("nan")
    return {"feats": feats, "cell": row, "regions": regions, "issues": issues}


def control_cell(g, keep, p_cracks) -> tuple[int, float]:
    """Positive control: (GT crack px, crack softmin over GT crack px of the seed-mean p_crack)."""
    K = np.ones(g.shape, bool) if keep is None else keep
    GC = (np.asarray(g) == CRACK) & K
    if not GC.any():
        return 0, float("nan")
    pbar = np.mean([np.asarray(p, np.float32) for p in p_cracks], axis=0)
    return int(GC.sum()), softmin(pbar[GC])


def control_verdict(scores: dict, controls=CONTROL_CELLS, worst=CONTROL_WORST) -> dict:
    """scores {stem: (gp, softmin)}; rank among cells with GT crack, ascending (worst first)."""
    cand = sorted([(v[1], s) for s, v in scores.items() if v[0] > 0 and math.isfinite(v[1])])
    n = len(cand)
    cut = math.ceil(worst * n)
    rank = {s: i + 1 for i, (_, s) in enumerate(cand)}
    rows = []
    for s in controls:
        r = rank.get(s)
        rows.append({"stem": s, "rank": r, "of": n, "score": scores.get(s, (0, float("nan")))[1],
                     "in_worst": bool(r is not None and r <= cut)})
    present = [r for r in rows if r["rank"] is not None]
    ok = bool(present) and len(present) == len(controls) and all(r["in_worst"] for r in present)
    return {"n_ranked": n, "cut_rank": cut, "rows": rows, "pass": ok}


# ---------------------------------------------------------------- pooled statistics and the bootstrap
class Vec:
    """Named view of a summed feature vector."""

    def __init__(self, v, idx):
        self.v, self.idx = v, idx

    def __getitem__(self, k):
        i = self.idx.get(k)
        return 0.0 if i is None else float(self.v[i])

    def s(self, *ks):
        return sum(self[k] for k in ks)


def ratio(a, b) -> float:
    return a / b if b else float("nan")


class Pooled:
    """F: (n cells, n seeds, n features) feature array; subsets: {name: bool mask over cells}."""

    def __init__(self, stems, seeds, names, F, fold_of, group_of, subsets):
        self.stems, self.seeds, self.names = list(stems), list(seeds), list(names)
        self.idx = {k: i for i, k in enumerate(self.names)}
        self.F = np.asarray(F, np.float64)
        self.fold = np.array([fold_of[s] for s in self.stems])
        self.group = [group_of[s] for s in self.stems]
        self.sub_names = list(subsets)
        self.M = np.stack([np.asarray(subsets[k], np.float64) for k in self.sub_names])

    def _vecs(self, V):
        return {k: Vec(V[i], self.idx) for i, k in enumerate(self.sub_names)}

    def point(self, seed_idx=None, drop=None):
        """Mean over seeds of the summed features per subset (or one seed); drop = bool mask of cells left out."""
        M = self.M if drop is None else self.M * (~drop)[None]
        X = self.F.mean(1) if seed_idx is None else self.F[:, seed_idx]
        return self._vecs(M @ X)

    def top_groups(self, feat: str, sub: str = "all", k: int = 3) -> list:
        col = self.F[:, 0, self.idx[feat]] if feat in self.idx else np.zeros(len(self.stems))
        m = self.M[self.sub_names.index(sub)] > 0
        tot = {}
        for i, gname in enumerate(self.group):
            if m[i]:
                tot[gname] = tot.get(gname, 0.0) + col[i]
        return [gname for gname, v in sorted(tot.items(), key=lambda t: (-t[1], t[0]))[:k] if v > 0]

    def drop_mask(self, groups) -> np.ndarray:
        gs = set(groups)
        return np.array([gname in gs for gname in self.group])

    def boot(self, stats: dict, n_boot=2000, seed=0) -> dict:
        """stats {name: fn(vecs) -> float}; two-stage: groups with replacement, then one seed per fold."""
        units = sorted(set(self.group))
        uidx = {u: [] for u in units}
        for i, gname in enumerate(self.group):
            uidx[gname].append(i)
        folds = sorted(set(self.fold.tolist()))
        rng = random.Random(seed)
        draws = {k: [] for k in stats}
        ns = len(self.seeds)
        for _ in range(n_boot):
            w = np.zeros(len(self.stems))
            for _u in range(len(units)):
                w[uidx[units[rng.randrange(len(units))]]] += 1
            sel = np.zeros(len(self.stems), np.int64)
            for k in folds:
                sel[self.fold == k] = rng.randrange(ns)
            X = self.F[np.arange(len(self.stems)), sel]
            vecs = self._vecs((self.M * w[None]) @ X)
            for k, fn in stats.items():
                draws[k].append(fn(vecs))
        out = {}
        for k, v in draws.items():
            a = np.array([x for x in v if x is not None and math.isfinite(x)])
            out[k] = {"lo": float(np.percentile(a, 2.5)) if len(a) else float("nan"),
                      "hi": float(np.percentile(a, 97.5)) if len(a) else float("nan"),
                      "se": float(a.std(ddof=1)) if len(a) > 1 else float("nan"), "n_finite": int(len(a))}
        return {"B": n_boot, "boot_seed": seed, "units": len(units), "stats": out}


# ---------------------------------------------------------------- statistic definitions (fixed before any read)
def iou(v, tp="tp", fn="fn", fp="fp") -> float:
    return ratio(v[tp], v[tp] + v[fn] + v[fp])


def oracle(v, a=0.0, b=0.0, t_loss=0.0) -> float:
    """IoU after a FN px become TP, b FP px are removed and t_loss TP px become FN, minus the IoU before."""
    u = v["tp"] + v["fn"] + v["fp"]
    return ratio(v["tp"] + a - t_loss, u - b) - ratio(v["tp"], u)


def weak_oracle(v, c) -> tuple[float, float, float]:
    """(best IoU - IoU at b = 0, best b, IoU at b = 0) of the single-class bias oracle for class c."""
    gp = v[f"w{c}_gp"]
    vals = []
    for i in range(len(BIAS_GRID)):
        tp, pp = v[f"w{c}_or_tp{i}"], v[f"w{c}_or_pp{i}"]
        vals.append(ratio(tp, gp + pp - tp))
    i0 = BIAS_GRID.index(0.0)
    arr = np.array([x if math.isfinite(x) else -1 for x in vals])
    best = max(range(len(vals)), key=lambda i: (arr[i], -abs(BIAS_GRID[i])))
    return arr[best] - arr[i0], BIAS_GRID[best], vals[i0]


def err(v):
    return v["fn"] + v["fp"]


def rc_all(v):
    return v["rc_fn_has"] + v["rc_fp_has"]


def stat_defs(sources, folds, rule_d: int) -> dict:
    """{name: (fn(vecs) -> float, top-3 feature, kind)}; kind 'inact' stats also get per-source / per-fold values."""
    S = {}

    def add(name, fn, top="gi_px", kind="inact"):
        S[name] = (fn, top, kind)

    A = "all"
    add("inact_iou", lambda V: iou(V[A]))
    add("inact_prec", lambda V: ratio(V[A]["tp"], V[A]["tp"] + V[A]["fp"]))
    add("inact_rec", lambda V: ratio(V[A]["tp"], V[A]["tp"] + V[A]["fn"]))
    for b in FN_B:
        add(f"fn_{b}/fn", lambda V, b=b: ratio(V[A][f"fn_{b}"], V[A]["fn"]))
        add(f"fn_{b}/err", lambda V, b=b: ratio(V[A][f"fn_{b}"], err(V[A])))
        add(f"rc_fn_{b}/rc", lambda V, b=b: ratio(V[A][f"rc_fn_{b}"], rc_all(V[A])))
    for b in FP_B:
        add(f"fp_{b}/fp", lambda V, b=b: ratio(V[A][f"fp_{b}"], V[A]["fp"]))
        add(f"fp_{b}/err", lambda V, b=b: ratio(V[A][f"fp_{b}"], err(V[A])))
        add(f"rc_fp_{b}/rc", lambda V, b=b: ratio(V[A][f"rc_fp_{b}"], rc_all(V[A])))
    add("O1", lambda V: oracle(V[A], a=V[A]["fn_ov"], b=V[A]["fp_oc"]))
    add("O2", lambda V: oracle(V[A], a=V[A]["fn_in_missed_all"]))
    add("O3", lambda V: oracle(V[A], b=V[A]["fp_in_spur_all"], t_loss=V[A]["tp_in_spur"]))
    add("O4", lambda V: oracle(V[A], a=V[A]["fn_bd"], b=V[A]["fp_bd"]))
    add("O5", lambda V: oracle(V[A], a=V[A]["fn_ca"], b=V[A]["fp_ca"]))
    add("O1+O5", lambda V: S["O1"][0](V) + S["O5"][0](V))
    add("region_recall50", lambda V: ratio(V[A]["r_found50"], V[A]["gt_r100"]))
    add("region_recall_any", lambda V: ratio(V[A]["gt_r100"] - V[A]["r_missed"], V[A]["gt_r100"]))
    add("region_prec100", lambda V: ratio(V[A]["p_r100_true"], V[A]["p_r100"]))
    add("n_missed_regions", lambda V: V[A]["r_missed"])
    add("n_gt_regions100", lambda V: V[A]["gt_r100"])
    # T10 gates
    add("G-layer px", lambda V: ratio(V[A].s("fn_ov", "fp_oc", "fn_ca", "fp_ca"), err(V[A])))
    add("G-layer rc", lambda V: ratio(V[A].s("rc_fn_ov", "rc_fp_oc", "rc_fn_ca", "rc_fp_ca"), rc_all(V[A])))
    add("G-paste px", lambda V: ratio(V[A]["fn_mi"], V[A]["fn"]))
    add("G-paste rc", lambda V: ratio(V[A]["r_missed"], V[A]["rc_fn_has"]))
    add("G-paste FL px", lambda V: ratio(V[A]["fn_mi_fl"], V[A]["fn_mi"]))
    add("G-paste FL rc", lambda V: ratio(V[A]["r_missed_fl"], V[A]["r_missed"]))
    add("G-refine px", lambda V: ratio(V[A].s("fn_bd", "fp_bd"), err(V[A])))
    add("G-refine rc", lambda V: ratio(V[A].s("rc_fn_bd", "rc_fp_bd"), rc_all(V[A])))
    for d_ in GT_CR_D:
        add(f"G-rules gt_cr{d_}", lambda V, d_=d_: ratio(V[A][f"gt_cr{d_}"], V[A]["gt_r100"]))
    for d_ in RULE_D:
        add(f"R-a{d_} share", lambda V, d_=d_: ratio(V[A][f"ra{d_}_px"], V[A]["pi_px"]))
        add(f"R-a{d_} prec", lambda V, d_=d_: ratio(V[A][f"ra{d_}_gi"], V[A][f"ra{d_}_px"]))
        add(f"R-a{d_} comps", lambda V, d_=d_: ratio(V[A][f"ra{d_}_n"], V[A]["ra_ncomp"]))
    add("R-b share", lambda V: ratio(V[A]["rb_px"], V[A]["pi_px"]))
    add("R-b prec", lambda V: ratio(V[A]["rb_gi"], V[A]["rb_px"]))
    # T13 SAM gate
    add("G-sam px", lambda V: ratio(V[A].s("fn_bd", "fp_bd", "fn_in", "fp_sp"), err(V[A])))
    add("G-sam rc", lambda V: ratio(V[A].s("rc_fn_bd", "rc_fp_bd", "rc_fn_in", "rc_fp_sp"), rc_all(V[A])))
    # T6 inactive_anatomy
    add("T6 miss px", lambda V: ratio(V[A]["t6_fn_miss"], V[A]["fn"]))
    add("T6 false px", lambda V: ratio(V[A]["t6_fp_false"], V[A]["fp"]))
    add("T6 miss rc", lambda V: ratio(V[A]["t6_r_miss"], V[A]["rc_fn_has"]))
    add("T6 false rc", lambda V: ratio(V[A]["t6_r_false"], V[A]["rc_fp_has"]))
    add("T6 blind share", lambda V: ratio(V[A]["t6_fn_miss_blind"], V[A]["t6_fn_miss"]))
    if "src:BMRK" in sources:
        add("T6 false BMRK share", lambda V: ratio(V["src:BMRK"]["t6_fp_false"], V[A]["t6_fp_false"]), kind="desc")
    # T8 C3 and the UCF step-B condition
    add("T8 a px", lambda V: ratio(V[A]["t8_fn_miss50"], err(V[A])))
    add("T8 c px", lambda V: ratio(V[A]["fp_in_spur_all"], err(V[A])))
    add("T8 b px", lambda V: 1 - S["T8 a px"][0](V) - S["T8 c px"][0](V))
    add("T8 a+c px", lambda V: S["T8 a px"][0](V) + S["T8 c px"][0](V))
    add("T8 a rc", lambda V: ratio(V[A]["t8_r_miss50"], rc_all(V[A])))
    add("T8 c rc", lambda V: ratio(V[A]["rc_spur"], rc_all(V[A])))
    add("T8 b rc", lambda V: 1 - S["T8 a rc"][0](V) - S["T8 c rc"][0](V))
    add("T8 a+c rc", lambda V: S["T8 a rc"][0](V) + S["T8 c rc"][0](V))
    # (b) crack at the overlap
    for nm in ("at", "el"):
        add(f"crack_{nm}_share", lambda V, nm=nm: ratio(V[A][f"{nm}_n"], V[A]["at_n"] + V[A]["el_n"]), "gc_px", "crack")
        for p in ("p14", "p11", "p0"):
            add(f"crack_{nm}_{p}", lambda V, nm=nm, p=p: ratio(V[A][f"{nm}_{p}"], V[A][f"{nm}_n"]), "gc_px", "crack")
        add(f"crack_{nm}_relR2", lambda V, nm=nm: ratio(V[A][f"{nm}_r2"], V[A][f"{nm}_n"]), "gc_px", "crack")
    add("crack_fn_as_inact", lambda V: ratio(V[A]["crack_fn_p11"], V[A]["crack_fn"]), "gc_px", "crack")
    # (c) weak classes
    for c in WEAK:
        add(f"w{c} iou", lambda V, c=c: iou(V[A], f"w{c}_tp", f"w{c}_fn", f"w{c}_fp"), f"w{c}_gp", "weak")
        add(f"w{c} comp_missed", lambda V, c=c: ratio(V[A][f"w{c}_r20miss"], V[A][f"w{c}_r20"]), f"w{c}_gp", "weak")
        add(f"w{c} err_bnd2", lambda V, c=c: ratio(V[A][f"w{c}_errbnd"], V[A][f"w{c}_err"]), f"w{c}_gp", "weak")
        add(f"w{c} oracle_gain", lambda V, c=c: weak_oracle(V[A], c)[0], f"w{c}_gp", "weak")
        add(f"T6w{c} miss px", lambda V, c=c: ratio(V[A][f"t6w{c}_fnmiss"], V[A][f"t6w{c}_fn"]), f"w{c}_gp", "weak")
        add(f"T6w{c} false px", lambda V, c=c: ratio(V[A][f"t6w{c}_fpfalse"], V[A][f"t6w{c}_fp"]), f"w{c}_gp", "weak")
    # T8 C-BMRK (arm parked by the critic; printed for the record)
    if "src:BMRK" in sources:
        B = "src:BMRK"
        add("C-BMRK fa50", lambda V: ratio(V[B]["fa50"], V[B]["cf"]), "gc_px", "desc")
        add("C-BMRK inact FP-FN", lambda V: V[B]["fp"] - V[B]["fn"], "gi_px", "desc")
        add("C-BMRK inact prec", lambda V: ratio(V[B]["tp"], V[B]["tp"] + V[B]["fp"]), "gi_px", "desc")
        others = [s for s in sources if s != B]
        add("C-BMRK relP2 gap", lambda V: min(ratio(V[s]["ck_p2"], V[s]["ck_pp"]) for s in others)
            - ratio(V[B]["ck_p2"], V[B]["ck_pp"]), "gc_px", "desc")
    for s in sources:
        add(f"relP2 {s}", lambda V, s=s: ratio(V[s]["ck_p2"], V[s]["ck_pp"]), "gc_px", "desc")
    # P-GIN (d): crack relR@2 in the top decile of histogram shape minus the rest
    add("P-GIN dR2", lambda V: ratio(V["pg_top"]["ck_g2"], V["pg_top"]["ck_gp"])
        - ratio(V["pg_rest"]["ck_g2"], V["pg_rest"]["ck_gp"]), "gc_px", "pgin")
    add("P-GIN relR2 top", lambda V: ratio(V["pg_top"]["ck_g2"], V["pg_top"]["ck_gp"]), "gc_px", "pgin")
    add("P-GIN relR2 rest", lambda V: ratio(V["pg_rest"]["ck_g2"], V["pg_rest"]["ck_gp"]), "gc_px", "pgin")
    add("P-GIN dR2 within-source decile", lambda V: ratio(V["pgw_top"]["ck_g2"], V["pgw_top"]["ck_gp"])
        - ratio(V["pgw_rest"]["ck_g2"], V["pgw_rest"]["ck_gp"]), "gc_px", "pgin")
    for s in sources:
        add(f"P-GIN dR2 {s}", lambda V, s=s: ratio(V[f"pg_top&{s}"]["ck_g2"], V[f"pg_top&{s}"]["ck_gp"])
            - ratio(V[f"pg_rest&{s}"]["ck_g2"], V[f"pg_rest&{s}"]["ck_gp"]), "gc_px", "pgin")
    return S


def scoped(fn, scope: str):
    """Re-target a stat written on subset 'all' to another subset (per source / per fold values)."""
    def g(V):
        W = dict(V)
        W["all"] = V[scope]
        return fn(W)
    return g


# ---------------------------------------------------------------- gates (thresholds as each team wrote them)
def holds(v, op, thr) -> bool | None:
    if v is None or not math.isfinite(v):
        return None
    return {">=": v >= thr, "<": v < thr, ">": v > thr, "<=": v <= thr}[op]


GATES = [
    # name, owner, conditions [(label, stat, op, thr)], combine, outcome words (true, false), region stats
    ("G-layer", "T10 arm 3 layered_ci", [("err share", "G-layer px", ">=", 0.25), ("O1+O5", "O1+O5", ">=", 0.04)],
     "any", ("OPEN", "CLOSED"), {"err share": "G-layer rc"}),
    ("G-paste", "T10 arm 4 inact_paste (merged paste arm)", [("FN-missed share", "G-paste px", ">=", 0.35),
                                                             ("FL share of FN-missed", "G-paste FL px", "<", 0.50)],
     "all", ("OPEN", "CLOSED"), {"FN-missed share": "G-paste rc", "FL share of FN-missed": "G-paste FL rc"}),
    ("G-refine", "T10 parked inact_refiner", [("boundary share", "G-refine px", ">=", 0.40), ("O4", "O4", ">=", 0.05)],
     "all", ("OPEN", "CLOSED"), {"boundary share": "G-refine rc"}),
    ("G-sam", "T13 sam_prompt_refine", [("bd+int+spur share", "G-sam px", ">=", 0.30)],
     "all", ("OPEN", "CLOSED"), {"bd+int+spur share": "G-sam rc"}),
    ("UCF step B (atlas part)", "T8 ucf_partial_joint (WAVE3 verdict (2))",
     [("missed+false share", "T8 a+c px", ">=", 0.30)], "all", ("OPEN", "CLOSED"), {"missed+false share": "T8 a+c rc"}),
    ("T8 C3 null reading", "T8 ucf_partial_joint C3", [("found-region boundary share (b)", "T8 b px", ">", 0.70)],
     "all", ("EXPECT NULL", "NO NULL EXPECTED"), {"found-region boundary share (b)": "T8 b rc"}),
]


def gate_outcome(conds_point, conds_lt3, combine, words):
    """Y4: a gate opens only if it also holds without the top 3 groups; otherwise the lead decides."""
    f = all if combine == "all" else any
    if any(c is None for c in conds_point):
        return "NOT READABLE"
    pt = f(conds_point)
    lt = f(c for c in conds_lt3 if c is not None) if all(c is not None for c in conds_lt3) else None
    if pt and lt:
        return words[0]
    if pt and not lt:
        return f"LEAD DECIDES ({words[0]} on all cells, not without the top 3 groups)"
    return words[1]


def t6_outcome(miss, false):
    if miss is None or false is None or not (math.isfinite(miss) and math.isfinite(false)):
        return "NOT READABLE"
    if miss >= 0.5 or false >= 0.5:
        return "BUILD"
    if miss < 0.3 and false < 0.3:
        return "PARK"
    return "LEAD DECIDES"
