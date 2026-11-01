"""el_metrics (calib, idea 7 + B5): cell-level and operating-point metrics for EL crack / inactive segmentation.

Input: a margin dump (calib_dump.py) per model or ensemble and cell set: npz with stems, margin (float16), oth (uint8).
  margin m = log p_crack - max_{k != crack} log p_k (mean softmax for ensembles); at crack bias b, crack is predicted
  iff m + b > 0 (= argmax after adding b to log p_crack, as m9_final / d_infer / LA); elsewhere the prediction is oth.
Every metric is computed EXACTLY at every b of the grid from one pass per cell (sorted counts; one radius-2 max filter).

Definitions (agreed with coach; see idea07_metrics.md):
  keep      = not ignored (E1 ext117 / Hanifi ignore masks); all px for val/test.
  relP@2    = predicted crack px within 2 px (EDT) of GT crack / predicted crack px  (pooled over cells)
  relR@2    = GT crack px within 2 px of a predicted crack px / GT crack px           (pooled)
  comp rec  = share of GT crack components (8-conn) >= 20 px with >= 50% of px within 2 px of a prediction (Track M cc_rec50_20)
  comp prec = share of predicted crack components >= 20 px with >= 1 px within 2 px of GT crack (Track M cc_prec_20)
  OP-comp   = per run, the grid b (-4..+12 step 0.1) maximising VAL comp recall s.t. VAL comp prec >= 0.90 (ties: smaller b;
              none: argmax prec, flagged; b >= 11.5 flagged edge). Pooled variant: the same rule on the pooled val counts of all seeds.
  OP-rel    = per run, the grid b maximising VAL relR@2 s.t. VAL relP@2 >= 0.90 (same rules)
  cell pos  = GT crack px in keep >= 20; 1-19 px = ambiguous, excluded; 0 = negative
  cell flag = >= 20 predicted crack px in keep; score s20 = 20th largest margin in keep (flag at b <=> s20 + b > 0); AUROC on s20
  inactive area % error = |pred inact - GT inact| / area * 100, area = keep px with GT != 7 (padding), at the deployed b

CLI:
  records  --dump NPZ --set val|ext|rf|test --code EL_F3 [--ext DIR] [--rf DIR] --out REC.json [--m0 M0.json --m0-set S]
           [--tol-profile exact|cpu]  (per-cell records; with --m0 the b = 0 self-check runs first and records are written only on PASS;
           REC.json.selfcheck.txt always; exact = 0.0005 all six (cuda bf16 path); cpu = coach fallback: crack IoU / relP / relR / inactive IoU
           0.01, component recall / precision 0.025, used only with ALL runs of ALL arms dumped on CPU)
  summary  --val REC_val.json --target REC_x.json [--deployed-b 0] --out SUM.json [--allow-unchecked] [--exclude STEM ...]
           [--pooled-val V1 .. V5] (also the arm-level OP: one b on the pooled val of all seeds) [--e1ctx TSV] (E1 sh29 oracle)
           (val-chosen OPs applied; refuses unless both self-checks PASS, or UNCHECKED with --allow-unchecked; never on FAIL)
  selfcheck --rec REC.json --m0 M0_RUN.json --m0-set val|test|ext [--tol-profile exact|cpu]      (b = 0 vs the opening's m0 JSON)
  routing  --val-pooled V1..V5 --synval-pooled S1..S5 --target E1_1..E1_5 [--e1ctx TSV] --out R.json
           (protocol_PF2 §13, descriptive: b_full / b_hc = pooled oracle relF1@2 b on real val / synthetic half-cut val; E1 routed vs not)
The scorer never chooses anything on a non-val set: OPs come only from the --val records.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

CRACK, INACT, PAD = 14, 11, 7
S8 = np.ones((3, 3), bool)
DISK2 = np.array([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]], bool)  # EDT <= 2
GRID = np.unique(np.round(np.concatenate([np.arange(-40, 121) / 10.0, [0.75]]), 2))  # b = -4.0 .. +12.0 step 0.1, + 0.75 (diagnostics)
OPGRID = (GRID >= -4.0 - 1e-9) & (GRID <= 12.0 + 1e-9) & (np.abs(np.round(GRID * 10) - GRID * 10) < 1e-6)  # OP choice: -4.0..+12.0 step 0.1 (coach, 31 Oct)
EDGE_B = 11.5  # a chosen b >= 11.5 is flagged "edge" (coach)
NEG = np.float32(-1e4)
CMIN, NCELL, MFLAG, PTARGET = 20, 20, 20, 0.90


def _count_gt(arr: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """#(arr + b > 0) for every b in grid, i.e. #(arr > -b)."""
    s = np.sort(arr.astype(np.float32))
    return (len(s) - np.searchsorted(s, -grid, side="right")).astype(np.int64)


def cell_record(margin: np.ndarray, oth: np.ndarray, gt: np.ndarray, keep: np.ndarray | None, grid: np.ndarray = GRID) -> dict:
    k = np.ones(gt.shape, bool) if keep is None else keep.astype(bool)
    mk = np.where(k, margin.astype(np.float32), NEG)
    g = (gt == CRACK) & k
    ng = int(g.sum())
    dg = ndi.distance_transform_edt(~g) if ng else np.full(gt.shape, np.inf)
    near_g = (dg <= 2) & k
    M2 = ndi.grey_dilation(mk, footprint=DISK2, mode="constant", cval=NEG)
    r = {"n_keep": int(k.sum()), "n_gt": ng,
         "pred": _count_gt(mk[k], grid), "tp": _count_gt(mk[g], grid),
         "relp_tp": _count_gt(mk[near_g], grid), "relr_tp": _count_gt(M2[g], grid)}
    # GT components: found at b iff b > -v50 (>= 50% of px within 2 px of a prediction); any-hit iff b > -vany
    lg, n = ndi.label(g, S8)
    gc = []
    if n:
        for i, sl in enumerate(ndi.find_objects(lg), 1):
            v = np.sort(M2[sl][lg[sl] == i])[::-1]
            gc.append([int(len(v)), float(v[math.ceil(0.5 * len(v)) - 1]), float(v[0])])
    r["gt_cc"] = gc
    # predicted components >= 20 px and their hits, per b (crop to where any b of the grid predicts crack)
    bmax = float(grid.max())
    act = mk > -bmax
    n20 = np.zeros(len(grid), np.int64); h20 = np.zeros(len(grid), np.int64); nall = np.zeros(len(grid), np.int64)
    hall = np.zeros(len(grid), np.int64); speck = np.zeros(len(grid), np.int64)
    if act.any():
        ys, xs = np.where(act)
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        mc, nc = mk[sl], near_g[sl]
        for j, b in enumerate(grid):
            P = mc > -b
            if not P.any():
                continue
            lab, npc = ndi.label(P, S8)
            sz = np.bincount(lab.ravel(), minlength=npc + 1)[1:]
            ht = np.bincount(lab[nc].ravel(), minlength=npc + 1)[1:]
            big = sz >= CMIN
            n20[j], h20[j], nall[j] = int(big.sum()), int((big & (ht > 0)).sum()), npc
            hall[j], speck[j] = int((ht > 0).sum()), int(sz[~big].sum())
    # coach A1 speck guard: all predicted components (>= 1 px) with their hits; crack px in components < 20 px
    r["pc20_n"], r["pc20_hit"], r["pc_n"], r["pc_hit"], r["speck_px"] = n20, h20, nall, hall, speck
    # inactive at every b: prediction is oth where crack is not predicted
    oi, gi = (oth == INACT) & k, (gt == INACT) & k
    area = k & (gt != PAD)
    r["area"], r["gt_inact"], r["gt_inact_area"] = int(area.sum()), int(gi.sum()), int((gi & area).sum())
    r["inact_pred"] = int(oi.sum()) - _count_gt(mk[oi], grid)
    r["inact_tp"] = int((oi & gi).sum()) - _count_gt(mk[oi & gi], grid)
    r["inact_pred_area"] = int((oi & area).sum()) - _count_gt(mk[oi & area], grid)
    # cell scores: M-th largest margin in keep
    srt = np.sort(mk[k])[::-1]
    r["s"] = {str(M): float(srt[M - 1]) if len(srt) >= M else float(NEG) for M in (1, 20, 50)}
    return r


# ---------------------------------------------------------------- set loading
SYNVAL_DEFAULT = Path("/home/noob/work/domain_scratch/shv1")  # domain's frozen synthetic half-cut val SHV1 (PF2 §13); --synval overrides
SYNVAL_MANIFEST = "63dd5469cc4eeaf21025e98669d635e3"  # md5 of SHV1's MANIFEST.md5


def gt_paths(set_: str, code: Path, ext: Path, rf: Path, synval: Path = SYNVAL_DEFAULT):
    if set_ == "synval":  # domain's transformed masks; ignore/ if present (SHV1: all zero)
        ig = (synval / "ignore").is_dir()
        return lambda s: (synval / "masks" / f"{s}.png", (synval / "ignore" / f"{s}.png") if ig else None)
    if set_ in ("val", "test"):  # labeled/masks_escdd = the scoring truth (handbook 14 / 17: gaint escdd_masks/test holds scuff at 2 cells)
        return lambda s: (code / "data" / "labeled" / "masks_escdd" / f"{s}.png", None)
    root = ext if set_ == "ext" else rf
    return lambda s: (root / "masks" / f"{s}.png", root / "ignore" / f"{s}.png")


def _rec_one(args):
    s, m, o, gp, ip = args
    gt = np.array(Image.open(gp))
    keep = None if ip is None else ~(np.array(Image.open(ip)) > 0)
    rec = cell_record(m, o, gt, keep)
    return s, {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in rec.items()}


def make_records(dump: Path, set_: str, code: Path, ext: Path, rf: Path, procs: int = 1, synval: Path = SYNVAL_DEFAULT) -> dict:
    z = np.load(dump)
    stems = [str(s) for s in z["stems"]]
    gp = gt_paths(set_, code, ext, rf, synval)
    jobs = [(s, z["margin"][i], z["oth"][i], *gp(s)) for i, s in enumerate(stems)]
    if procs > 1:
        from multiprocessing import Pool
        with Pool(procs) as p:
            out = dict(p.map(_rec_one, jobs, chunksize=2))
    else:
        out = dict(map(_rec_one, jobs))
    return {"dump": str(dump), "set": set_, "grid": GRID.tolist(), "runs": [str(r) for r in z["runs"]], "cells": out}


# ---------------------------------------------------------------- aggregation
def curves(cells: dict, stems=None) -> dict:
    """Pooled curves over the grid for a subset of cells."""
    cs = [cells[s] for s in (stems if stems is not None else cells)]
    S = lambda key: np.sum([np.asarray(c[key], np.int64) for c in cs], 0) if cs else np.zeros(len(GRID), np.int64)
    pred, tp, rp, rr = S("pred"), S("tp"), S("relp_tp"), S("relr_tp")
    ng = sum(c["n_gt"] for c in cs)
    gc = [x for c in cs for x in c["gt_cc"] if x[0] >= CMIN]
    found = np.array([[x[1] + b > 0 for b in GRID] for x in gc]) if gc else np.zeros((0, len(GRID)), bool)
    n20, h20 = S("pc20_n"), S("pc20_hit")
    old = cs and "pc_hit" not in cs[0]  # records made before coach's A1 speck guard
    nall, hall, spk = (S("pc_n"), np.full(len(GRID), -1), np.full(len(GRID), -1)) if old else (S("pc_n"), S("pc_hit"), S("speck_px"))
    div = lambda a, b: np.where(b > 0, a / np.maximum(b, 1), np.nan)
    ip, it = S("inact_pred"), S("inact_tp")
    gi = sum(c["gt_inact"] for c in cs)
    return {"n_cells": len(cs), "gt_px": ng, "gt_comp20": len(gc),
            "P": div(tp, pred), "R": div(tp, np.full_like(tp, ng)), "IoU": div(tp, pred + ng - tp),
            "relP": div(rp, pred), "relR": div(rr, np.full_like(rr, ng)),
            "compR": found.mean(0) if len(gc) else np.full(len(GRID), np.nan), "compP": div(h20, n20), "pred_px": pred,
            "compP_all": div(hall, nall), "speck_share": div(spk, pred),
            "inactIoU": div(it, ip + gi - it)}


def choose_op(cv: dict, rec_key: str, prec_key: str, target: float = PTARGET) -> dict:
    """OP on the protocol grid (-4.0..+12.0 step 0.1): max recall s.t. precision >= target; ties -> smaller b;
    unreachable -> the max-precision b (ties -> smaller b), flagged; b >= 11.5 flagged "edge"."""
    R, P = np.asarray(cv[rec_key], float), np.asarray(cv[prec_key], float)
    cand = np.where(OPGRID)[0]
    ok = cand[np.nan_to_num(P[cand], nan=-1) >= target]
    if len(ok):
        j = ok[np.argmax(R[ok])]  # argmax returns the first (smallest b) among ties
        return {"b": float(GRID[j]), "j": int(j), "reachable": True, "edge": bool(GRID[j] >= EDGE_B), "val_R": float(R[j]), "val_P": float(P[j])}
    j = int(cand[np.argmax(np.nan_to_num(P[cand], nan=-1))])
    return {"b": float(GRID[j]), "j": j, "reachable": False, "edge": bool(GRID[j] >= EDGE_B), "val_R": float(R[j]), "val_P": float(P[j])}


def pool_cells(recs: list, require_set: str = "val") -> dict:
    """Pool several runs' val records into one cell dict (keys run-index:stem) for an arm-level OP (coach, 31 Oct)."""
    out = {}
    for i, r in enumerate(recs):
        assert r["set"] == require_set, f"the pooled OP is chosen on {require_set} only"
        out.update({f"{i}:{s}": c for s, c in r["cells"].items()})
    return out


def oracle_relf1(cells: dict, stems=None) -> dict:
    """max over the grid of pooled relF1@2 on the set's own labels: an ORACLE UPPER BOUND, chooses nothing, descriptive."""
    c = curves(cells, stems)
    F = np.where((c["relP"] + c["relR"]) > 0, 2 * c["relP"] * c["relR"] / np.maximum(c["relP"] + c["relR"], 1e-9), 0)
    F = np.nan_to_num(F, nan=0.0); j = int(np.argmax(F))
    return {"oracle_relF1": float(F[j]), "at_b": float(GRID[j]), "relR": float(c["relR"][j]), "relP": float(c["relP"][j]),
            "label": "oracle upper bound, chooses nothing, descriptive"}


def _auroc(pos: list, neg: list) -> float:
    if not pos or not neg:
        return float("nan")
    a = np.concatenate([pos, neg])
    order = np.argsort(a, kind="mergesort"); rk = np.empty(len(a)); rk[order] = np.arange(1, len(a) + 1)
    # average ranks for ties
    _, inv, cnt = np.unique(a, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=rk); rk = (sums / cnt)[inv]
    return float((rk[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cell_level(cells: dict, b: float, stems=None) -> dict:
    cs = {s: cells[s] for s in (stems if stems is not None else cells)}
    pos = [s for s, c in cs.items() if c["n_gt"] >= NCELL]; neg = [s for s, c in cs.items() if c["n_gt"] == 0]
    amb = [s for s, c in cs.items() if 0 < c["n_gt"] < NCELL]
    fl = {s: cs[s]["s"][str(MFLAG)] + b > 0 for s in pos + neg}
    tp = sum(fl[s] for s in pos); fa = sum(fl[s] for s in neg)
    return {"b": b, "n_pos": len(pos), "n_neg": len(neg), "n_ambiguous": len(amb),
            "recall": tp / len(pos) if pos else float("nan"), "fa_rate": fa / len(neg) if neg else float("nan"),
            "precision": tp / (tp + fa) if (tp + fa) else float("nan"),
            "auroc": _auroc([cs[s]["s"][str(MFLAG)] for s in pos], [cs[s]["s"][str(MFLAG)] for s in neg])}


def inactive_err(cells: dict, b: float, stems=None) -> dict:
    j = int(np.argmin(np.abs(GRID - b))); assert abs(GRID[j] - b) < 1e-9, b
    e, sg, has, no = [], [], [], []
    for s in (stems if stems is not None else cells):
        c = cells[s]
        if not c["area"]:
            continue
        ag, ap_ = c["gt_inact_area"] / c["area"], c["inact_pred_area"][j] / c["area"]
        e.append(abs(ap_ - ag) * 100); sg.append((ap_ - ag) * 100)
        (has if ag >= 0.005 else no).append(abs(ap_ - ag) * 100)
    m = lambda x: float(np.mean(x)) if x else float("nan")
    return {"b": b, "mae_all": m(e), "mae_inactive_cells": m(has), "n_inactive_cells": len(has), "mae_other": m(no),
            "signed_mean": m(sg), "max_err": float(max(e)) if e else float("nan")}


def summarize(val_rec: dict, tgt_rec: dict, deployed_b: float = 0.0, stems=None, pooled_val: list | None = None, strata: dict | None = None) -> dict:
    vc = curves(val_rec["cells"])
    op_c, op_r = choose_op(vc, "compR", "compP"), choose_op(vc, "relR", "relP")
    tc = curves(tgt_rec["cells"], stems)
    extra = {}
    if pooled_val:  # arm-level OP: one b on the pooled val counts of all seeds, applied to this run's target (coach, 31 Oct)
        pc = curves(pool_cells(pooled_val))
        pop_c, pop_r = choose_op(pc, "compR", "compP"), choose_op(pc, "relR", "relP")
        extra["pooled_op"] = {"n_runs": len(pooled_val), "op_comp": pop_c, "op_rel": pop_r,
                              "comp_recall_at_opc": float(tc["compR"][pop_c["j"]]), "comp_prec_at_opc": float(tc["compP"][pop_c["j"]]),
                              "relR_at_opr": float(tc["relR"][pop_r["j"]]), "relP_at_opr": float(tc["relP"][pop_r["j"]]),
                              "speck_guard": {lab: {"compP_all": float(tc["compP_all"][op["j"]]), "speck_share": float(tc["speck_share"][op["j"]])}
                                              for lab, op in (("opc", pop_c), ("opr", pop_r))}}
    if tgt_rec["set"] == "ext":  # coach (3): E1 all and E1 sh29 oracle relF1@2, descriptive
        extra["oracle_upper_bound"] = {"E1 all": oracle_relf1(tgt_rec["cells"], stems)}
        for k, st in (strata or {}).items():
            st = [x for x in st if x in tgt_rec["cells"] and (stems is None or x in set(stems))]
            if st:
                extra["oracle_upper_bound"][k] = oracle_relf1(tgt_rec["cells"], st)
    jd = int(np.argmin(np.abs(GRID - deployed_b)))
    at = lambda j: {k: (float(tc[k][j]) if np.ndim(tc[k]) else tc[k]) for k in ("P", "R", "IoU", "relP", "relR", "compR", "compP", "compP_all", "speck_share", "inactIoU")}
    return {"set": tgt_rec["set"], "n_cells": tc["n_cells"], "gt_comp20": tc["gt_comp20"], "op_comp": op_c, "op_rel": op_r,
            "comp_recall_at_opc": float(tc["compR"][op_c["j"]]), "comp_prec_at_opc": float(tc["compP"][op_c["j"]]),
            "relR_at_opr": float(tc["relR"][op_r["j"]]), "relP_at_opr": float(tc["relP"][op_r["j"]]),
            "speck_guard": {lab: {"compP_all": float(tc["compP_all"][op["j"]]), "speck_share": float(tc["speck_share"][op["j"]])}
                            for lab, op in (("opc", op_c), ("opr", op_r))},
            "deployed_b": deployed_b, "at_deployed": at(jd),
            "cell_deployed": cell_level(tgt_rec["cells"], deployed_b, stems), "cell_at_opc": cell_level(tgt_rec["cells"], op_c["b"], stems),
            "cell_b0": cell_level(tgt_rec["cells"], 0.0, stems),
            "inactive_area_err": inactive_err(tgt_rec["cells"], deployed_b, stems), **extra}


TOL_PROFILES = {  # coach ruling 31 Oct (protocol_PF2 §4.1): exact = cuda bf16 path; cpu = numerics fallback, ALL runs of ALL arms on CPU
    "exact": {"IoU": 0.0005, "relP": 0.0005, "relR": 0.0005, "inactIoU": 0.0005, "compR": 0.0005, "compP": 0.0005},
    "cpu": {"IoU": 0.01, "relP": 0.01, "relR": 0.01, "inactIoU": 0.01, "compR": 0.025, "compP": 0.025},
}


def oracle_b_relf1(cells: dict, stems=None) -> dict:
    """PF2 §13 / routing pre-check: the OPGRID b (-4..+12 step 0.1) with the highest pooled relF1@2; ties -> smaller b."""
    c = curves(cells, stems)
    F = np.where((c["relP"] + c["relR"]) > 0, 2 * c["relP"] * c["relR"] / np.maximum(c["relP"] + c["relR"], 1e-9), 0.0)
    F = np.nan_to_num(F, nan=0.0)
    cand = np.where(OPGRID)[0]
    j = int(cand[np.argmax(F[cand])])  # first max = smallest b among ties
    return {"b": float(GRID[j]), "j": j, "relF1": float(F[j]), "relR": float(c["relR"][j]), "relP": float(c["relP"][j]), "edge": bool(GRID[j] >= EDGE_B)}


def routed_counts(cells: dict, bmap: dict) -> dict:
    """Pooled relR@2 / relP@2 / relF1@2 and the crack-free false-alarm side with a per-cell bias map (stem -> b)."""
    t = dict(pred=0, rp=0, rr=0, ng=0, neg=0, fa_px=0, fa_cells=0)
    for s_, b in bmap.items():
        c = cells[s_]; j = int(np.argmin(np.abs(GRID - b))); assert abs(GRID[j] - b) < 1e-9, b
        t["pred"] += c["pred"][j]; t["rp"] += c["relp_tp"][j]; t["rr"] += c["relr_tp"][j]; t["ng"] += c["n_gt"]
        if c["n_gt"] == 0:
            t["neg"] += 1; t["fa_px"] += c["pred"][j]; t["fa_cells"] += int(c["s"][str(MFLAG)] + b > 0)
    P = t["rp"] / t["pred"] if t["pred"] else float("nan"); R = t["rr"] / t["ng"] if t["ng"] else float("nan")
    F = 2 * P * R / (P + R) if (t["pred"] and t["ng"] and P + R > 0) else 0.0
    return {"relF1": F, "relR": R, "relP": P, "fa_px_per_negcell": t["fa_px"] / max(t["neg"], 1), "fa_cell_rate": t["fa_cells"] / max(t["neg"], 1), "n_neg": t["neg"]}


def routing(val_recs: list, syn_recs: list, tgt_recs: list, halfcut: set) -> dict:
    """protocol_PF2 §13 (descriptive): b_full = pooled real-val oracle relF1@2 b, b_hc = pooled synthetic-half-cut-val oracle b
    (one pair per arm); per run, E1 crack relF1@2 / relR@2 / relP@2 with half-cut cells at b_hc and full cells at b_full ("routed")
    vs every cell at b_full ("unrouted"). Cell type = known (e1_context from the E1 masks). Never selects anything."""
    assert len(val_recs) == len(syn_recs) == len(tgt_recs) and all(t["set"] == "ext" for t in tgt_recs)
    bf = oracle_b_relf1(pool_cells(val_recs, "val")); bh = oracle_b_relf1(pool_cells(syn_recs, "synval"))
    db = bh["b"] - bf["b"]
    runs = []
    for t in tgt_recs:
        C = t["cells"]
        un = routed_counts(C, {s_: bf["b"] for s_ in C}); ro = routed_counts(C, {s_: (bh["b"] if s_ in halfcut else bf["b"]) for s_ in C})
        runs.append({"runs": t.get("runs"), "unrouted": un, "routed": ro, "delta_relF1": ro["relF1"] - un["relF1"]})
    def arith(k):
        a = np.array([r["routed"][k] for r in runs], float); b_ = np.array([r["unrouted"][k] for r in runs], float)
        if len(runs) < 2:
            return {"routed": float(a.mean()), "unrouted": float(b_.mean()), "delta": float(a.mean() - b_.mean())}
        thr = max(0.01, 2 * np.sqrt((a.std(ddof=1) ** 2 + b_.std(ddof=1) ** 2) / 3))
        d = float(a.mean() - b_.mean())
        return {"routed": float(a.mean()), "unrouted": float(b_.mean()), "delta": d, "threshold_rule1": float(thr),
                "reading": "BETTER" if d > thr else ("WORSE" if d < -thr else "n.d.")}
    return {"label": "DESCRIPTIVE half-cut routing readout (protocol_PF2 §13); cell type known from e1_context (E1 masks); chooses nothing",
            "b_full": bf, "b_hc": bh, "delta_b": db, "no_op": bool(db < 1.0), "n_runs": len(runs), "n_halfcut_cells": len(halfcut & set(tgt_recs[0]["cells"])),
            "per_run": runs, "arm": {k: arith(k) for k in ("relF1", "relR", "relP", "fa_px_per_negcell", "fa_cell_rate")}}


def selfcheck(rec: dict, m0_cells: dict, tol=0.0005) -> tuple[bool, list[str]]:
    """coach (protocol_PF2): at b = 0 the records must reproduce the opening's m0 per-cell JSON (argmax) pooled metrics
    within |delta| <= tol: crack IoU, relP@2, relR@2, inactive IoU, component recall / precision (Track M rules).
    tol: a float (all six) or a dict per metric (TOL_PROFILES)."""
    tl = tol if isinstance(tol, dict) else {k: tol for k in TOL_PROFILES["exact"]}
    j = int(np.argmin(np.abs(GRID - 0.0)))
    cs = rec["cells"]
    assert set(cs) == set(m0_cells), "cell sets differ"
    mine = curves(cs)
    NC = 24
    C = sum(np.array(m0_cells[s]["conf"], np.int64).reshape(NC, NC) for s in cs)
    rel = np.sum([m0_cells[s]["crack_rel2"] for s in cs], 0)
    g = [c for s in cs for c in m0_cells[s]["crack_cc"]["gt"] if c[0] >= CMIN]
    pp = [c for s in cs for c in m0_cells[s]["crack_cc"]["pr"] if c[0] >= CMIN]
    dv = lambda x, y: x / y if y > 0 else np.nan  # undefined (0/0) on both sides counts as agreement
    ref = {"IoU": dv(C[CRACK, CRACK], C[CRACK].sum() + C[:, CRACK].sum() - C[CRACK, CRACK]),
           "relP": dv(rel[0], rel[1]), "relR": dv(rel[2], rel[3]),
           "inactIoU": dv(C[INACT, INACT], C[INACT].sum() + C[:, INACT].sum() - C[INACT, INACT]),
           "compR": np.mean([c[1] >= 0.5 * c[0] for c in g]) if g else np.nan, "compP": np.mean([c[1] > 0 for c in pp]) if pp else np.nan}
    ok, L = True, []
    for k, v in ref.items():
        d = float(mine[k][j]) - float(v)
        bad = not (abs(d) <= tl[k] or (np.isnan(float(mine[k][j])) and np.isnan(float(v))))
        ok &= not bad
        L.append(f"  {k}: records {float(mine[k][j]):.4f} m0 {float(v):.4f} delta {d:+.5f} (tol {tl[k]}){'  FAIL' if bad else ''}")
    return ok, L


def _md5(p):
    import hashlib
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def _sc_path(rec_path):
    return Path(str(rec_path) + ".selfcheck.txt")


def _sc_status(rec_path):
    p = _sc_path(rec_path)
    if not p.exists():
        return "MISSING"
    last = p.read_text().strip().splitlines()[-1]
    return "PASS" if last == "SELFCHECK PASS" else ("UNCHECKED" if last.startswith("SELFCHECK UNCHECKED") else "FAIL")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("records"); r.add_argument("--dump", required=True); r.add_argument("--set", required=True, choices=["val", "ext", "rf", "test", "synval"])
    r.add_argument("--synval", default=str(SYNVAL_DEFAULT), help="domain's frozen synthetic half-cut val (SHV1)")
    r.add_argument("--synval-manifest", default=SYNVAL_MANIFEST, help="md5 of SHV1's MANIFEST.md5, verified with every file before reading ('' = no check)")
    r.add_argument("--code", default="/home/noob/work/el_f3"); r.add_argument("--ext", default="/home/noob/work/el_f1/reports/f1/ext117")
    r.add_argument("--rf", default="/home/noob/work/calib/data/rf"); r.add_argument("--out", required=True); r.add_argument("--procs", type=int, default=1)
    r.add_argument("--m0", help="coach A4: the run's m0 per-cell JSON; records are written only if the b = 0 self-check passes")
    r.add_argument("--m0-set", help="key in the m0 JSON cells (val | test | ext); default = --set")
    r.add_argument("--tol-profile", default="exact", choices=list(TOL_PROFILES), help="exact (cuda bf16 path, 0.0005) | cpu (coach fallback)")
    s = sub.add_parser("summary"); s.add_argument("--val", required=True); s.add_argument("--target", required=True)
    s.add_argument("--deployed-b", type=float, default=0.0); s.add_argument("--out", required=True)
    s.add_argument("--exclude", nargs="*", default=[], help="target stems to drop (e.g. the clean set without CSIR_00070_r8_c4); OPs still from val")
    s.add_argument("--pooled-val", nargs="+", help="val records of ALL seeds of the arm: also report the arm-level pooled OP (one b per arm)")
    s.add_argument("--e1ctx", default="/home/noob/work/el_f3/reports/d/e1_context.tsv", help="E1 strata for the sh29 oracle readout")
    s.add_argument("--allow-unchecked", action="store_true", help="accept records whose self-check is UNCHECKED (no m0 JSON exists, e.g. Hanifi rf, ensembles); a FAIL is never accepted")
    c = sub.add_parser("selfcheck"); c.add_argument("--rec", required=True); c.add_argument("--m0", required=True, help="m0 per-cell JSON of the same run")
    c.add_argument("--m0-set", required=True, help="key in m0 cells: val | test | ext")
    c.add_argument("--tol-profile", default="exact", choices=list(TOL_PROFILES))
    q = sub.add_parser("routing", help="protocol_PF2 §13 half-cut routing readout (descriptive)")
    q.add_argument("--val-pooled", nargs="+", required=True); q.add_argument("--synval-pooled", nargs="+", required=True)
    q.add_argument("--target", nargs="+", required=True, help="E1 (ext) records, one per run, same order as --val-pooled")
    q.add_argument("--e1ctx", default="/home/noob/work/el_f3/reports/d/e1_context.tsv"); q.add_argument("--out", required=True)
    q.add_argument("--allow-unchecked", action="store_true", help="accept UNCHECKED val / target self-checks (never FAIL); synval is always UNCHECKED (no m0)")
    a = ap.parse_args()
    if a.cmd == "routing":
        for p in list(a.val_pooled) + list(a.target):
            st = _sc_status(p)
            if st in ("FAIL", "MISSING") or (st == "UNCHECKED" and not a.allow_unchecked):
                print(f"routing REFUSED: self-check of {p} is {st}; nothing written"); return 4
        for p in a.synval_pooled:
            if _sc_status(p) in ("FAIL", "MISSING"):
                print(f"routing REFUSED: {p} has no self-check file or FAIL; nothing written"); return 4
        cx = [l.rstrip("\n").split("\t") for l in open(a.e1ctx) if l.strip()]
        hc = {f[0] for f in cx if len(f) >= 4 and f[3] == "halfcut=1"}
        assert len(hc) == 58, len(hc)
        out = routing([json.load(open(p)) for p in a.val_pooled], [json.load(open(p)) for p in a.synval_pooled],
                      [json.load(open(p)) for p in a.target], hc)
        out["inputs"] = {"val": a.val_pooled, "synval": a.synval_pooled, "target": a.target, "e1ctx": a.e1ctx, "e1ctx_md5": _md5(a.e1ctx)}
        out["el_metrics_md5"] = _md5(__file__)
        json.dump(out, open(a.out, "w"), indent=1)
        print(json.dumps({k: out[k] for k in ("b_full", "b_hc", "delta_b", "no_op", "arm")}, indent=1))
        return 0
    if a.cmd == "records" and a.set == "synval" and a.synval_manifest:
        import hashlib
        md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
        mf = Path(a.synval) / "MANIFEST.md5"
        assert md5(mf) == a.synval_manifest, f"synval MANIFEST md5 {md5(mf)} != {a.synval_manifest}"
        for line in open(mf):
            if line.strip():
                h, f = line.split(None, 1)
                assert md5(Path(a.synval) / f.strip()) == h, f"synval file changed: {f.strip()}"
    if a.cmd == "records":
        rec = make_records(Path(a.dump), a.set, Path(a.code), Path(a.ext), Path(a.rf), a.procs, Path(a.synval))
        sc = _sc_path(a.out)
        if a.m0:
            ok, L = selfcheck(rec, json.load(open(a.m0))["cells"][a.m0_set or a.set], TOL_PROFILES[a.tol_profile])
            sc.write_text(f"el_metrics {_md5(__file__)} records selfcheck at b = 0, tol profile {a.tol_profile}\ndump {a.dump}\nm0 {a.m0} md5 {_md5(a.m0)} set {a.m0_set or a.set}\n"
                          + "\n".join(L) + "\nSELFCHECK " + ("PASS" if ok else "FAIL") + "\n")
            print(sc.read_text())
            if not ok:
                print("records NOT written: self-check failed (coach A4)")
                return 4
        else:
            sc.write_text(f"el_metrics {_md5(__file__)} dump {a.dump}\nSELFCHECK UNCHECKED (no m0 JSON given)\n")
        json.dump(rec, open(a.out, "w"))
    elif a.cmd == "selfcheck":
        ok, L = selfcheck(json.load(open(a.rec)), json.load(open(a.m0))["cells"][a.m0_set], TOL_PROFILES[a.tol_profile])
        txt = f"el_metrics {_md5(__file__)} selfcheck at b = 0, tol profile {a.tol_profile}\nrec {a.rec}\nm0 {a.m0} md5 {_md5(a.m0)} set {a.m0_set}\n" + "\n".join(L) + "\nSELFCHECK " + ("PASS" if ok else "FAIL") + "\n"
        _sc_path(a.rec).write_text(txt); print(txt)
        return 0 if ok else 4
    else:
        for p in [a.val, a.target] + list(a.pooled_val or []):
            st = _sc_status(p)
            if st == "FAIL" or st == "MISSING" or (st == "UNCHECKED" and not a.allow_unchecked):
                print(f"summary REFUSED: self-check of {p} is {st} (coach A4); nothing written")
                return 4
        v, t = json.load(open(a.val)), json.load(open(a.target))
        assert v["set"] == "val", "operating points are chosen on val only"
        keep = [x for x in t["cells"] if x not in set(a.exclude)] if a.exclude else None
        assert not a.exclude or len(keep) == len(t["cells"]) - len(set(a.exclude) & set(t["cells"])), "exclude"
        strata = None
        if t["set"] == "ext" and Path(a.e1ctx).exists():
            cx = [l.rstrip("\n").split("\t") for l in open(a.e1ctx) if l.strip()]
            strata = {"E1 sh29": [f[0] for f in cx if len(f) >= 4 and f[2] == "scuff=1" and f[3] == "halfcut=1"]}
        pv = [json.load(open(p)) for p in a.pooled_val] if a.pooled_val else None
        out = summarize(v, t, a.deployed_b, keep, pv, strata)
        out["excluded"] = sorted(set(a.exclude) & set(t["cells"]))
        out["selfcheck"] = {"val": _sc_status(a.val), "target": _sc_status(a.target)}
        out["descriptive"] = t["set"] in ("ext", "rf")  # coach A5: E1 / rf numbers at the val-chosen b are descriptive
        out["el_metrics_md5"] = _md5(__file__)
        json.dump(out, open(a.out, "w"), indent=1); print(json.dumps({k: out[k] for k in ("set", "op_comp", "op_rel", "comp_recall_at_opc", "relR_at_opr", "selfcheck", "descriptive")}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
