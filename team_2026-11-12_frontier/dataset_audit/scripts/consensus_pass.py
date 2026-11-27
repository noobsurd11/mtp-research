"""Axis a, d, f (model side): one pass over the 532 pool cells. For each cell: load the 25 cv5v3 out-of-fold dumps and the 4 cv5v2
W1-G PF dumps (pred, p_crack, p_inact only), build the consensus maps, find the label-error candidates of PLAN.md section 1a, and score
every model against the label variants (v1.1, 20211104, skeleton, skeleton drawn 3 px wide, v1.1 with candidates ignored).
Writes cache/cons/<stem>.npz (consensus maps, uint8) and out/pass_records.pkl. CPU only.
Usage: nice -n 19 python -I consensus_pass.py [--workers 8] [--limit N]"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402

import common as C  # noqa: E402

PADDING = 7
VAR = ("v11", "old", "skel", "w3", "candign")
NM = len(C.MODELS)


def edt_le2(m: np.ndarray) -> np.ndarray:
    """bool: px within 2 px (Euclidean) of m; all False if m is empty."""
    if not m.any():
        return np.zeros(m.shape, bool)
    return ndi.distance_transform_edt(~m) <= 2


def crack_counts(p: np.ndarray, g: np.ndarray, k: np.ndarray, near_p=None, near_g=None) -> list:
    """[tp, fp, fn, relP_hit, relP_n, relR_hit, relR_n] on keep k; p and g already restricted to k."""
    near_g = edt_le2(g) if near_g is None else near_g
    near_p = edt_le2(p) if near_p is None else near_p
    tp = int((p & g).sum()); np_ = int(p.sum()); ng = int(g.sum())
    return [tp, np_ - tp, ng - tp, int((p & near_g).sum()), np_, int((g & near_p).sum()), ng]


def inact_counts(p: np.ndarray, g: np.ndarray) -> list:
    tp = int((p & g).sum())
    return [tp, int(p.sum()) - tp, int(g.sum()) - tp]


def comp_list(lab: np.ndarray, n: int) -> list:
    return [lab == i for i in range(1, n + 1)]


def do_cell(args):
    stem, pool, relay_paths, w1g_paths = args
    C.guard(stem, pool)
    gt = C.mask_v11(stem)
    old = C.mask_old(stem)
    gry = C.grey(stem)
    keep = gt != C.IGN
    valid = keep & (gt != PADDING)
    g = (gt == C.CRACK) & keep
    gi = (gt == C.INACT) & keep
    # ---- 25 models
    preds = np.empty((NM, 512, 512), np.uint8)
    qc = np.zeros((512, 512), np.float32)
    qi = np.zeros((512, 512), np.float32)
    for j, p in enumerate(relay_paths):
        d = C.load_dump(p)
        preds[j] = d["pred"]
        qc += d["p_crack"].astype(np.float32)
        qi += d["p_inact"].astype(np.float32)
    qc /= NM
    qi /= NM
    pc = (preds == C.CRACK) & keep[None]
    pi = (preds == C.INACT) & keep[None]
    vc = pc.sum(0).astype(np.uint8)
    vi = pi.sum(0).astype(np.uint8)
    near_p = np.stack([edt_le2(pc[j]) for j in range(NM)])
    ncov = near_p.sum(0).astype(np.uint8)            # models with a crack prediction within 2 px
    # ---- W1-G (cv5v2) replication set
    w4 = np.zeros((512, 512), np.uint8)
    w4i = np.zeros((512, 512), np.uint8)
    w1g_rec = []
    near_g = edt_le2(g)
    for p in w1g_paths:
        pr = C.load_dump(p, ("pred",))["pred"]
        a = (pr == C.CRACK) & keep
        w4 += a
        w4i += (pr == C.INACT) & keep
        w1g_rec.append(crack_counts(a, g, keep, near_g=near_g) + inact_counts((pr == C.INACT) & keep, gi))
    # ---- candidates (PLAN 1a)
    near_g_strict = near_g                             # v1.1 crack within 2 px
    excl_c = g | (vc >= 13)
    cands = []
    ign = np.zeros((512, 512), bool)
    # missed crack
    kcons = (vc >= 20) & keep
    lk, nk = ndi.label(kcons, C.S8)
    mc = kcons & ~near_g_strict
    lm, nm_ = ndi.label(mc, C.S8)
    if nm_:
        sz = np.bincount(lm.ravel(), minlength=nm_ + 1)
        touch = np.zeros(nk + 1, bool)
        if nk:
            touch[np.unique(lk[kcons & near_g_strict])] = True
        for i in range(1, nm_ + 1):
            if sz[i] < 20:
                continue
            comp = lm == i
            parents = np.unique(lk[comp])
            kind = "extension" if touch[parents].any() else "whole"
            cls = np.bincount(gt[comp].astype(np.int64), minlength=256)
            cls = {int(c): int(n) for c, n in enumerate(cls) if n}
            w4hit = float((w4[comp] >= 3).mean())
            cands.append({"type": "MC", "kind": kind, "px": int(sz[i]), "meanV": float(vc[comp].mean()),
                          "meanQ": float(qc[comp].mean()), "z": C.contrast_z(gry, comp, excl_c, valid),
                          "classes": cls, "repl": w4hit >= 0.5, "repl_share": w4hit,
                          "bbox": [int(x) for x in np.argwhere(comp).min(0)] + [int(x) for x in np.argwhere(comp).max(0)]})
            ign |= comp
    # spurious crack
    v2 = ndi.maximum_filter(vc, size=5)
    w2 = ndi.maximum_filter(w4, size=5)
    lg, ngc = ndi.label(g, C.S8)
    gcomp_stats = []
    for i in range(1, ngc + 1):
        comp = lg == i
        n = int(comp.sum())
        share_low = float((v2[comp] <= 2).mean())
        z = C.contrast_z(gry, comp, excl_c, valid) if n >= 20 else float("nan")
        gcomp_stats.append([n, share_low, z, float((ncov[comp] >= 13).mean())])
        if n >= 20 and share_low >= 0.9:
            cands.append({"type": "SC", "kind": "component", "px": n, "meanV": float(vc[comp].mean()),
                          "meanQ": float(qc[comp].mean()), "z": z, "classes": {14: n},
                          "repl": bool((w2[comp] <= 0).mean() >= 0.9), "repl_share": float((w2[comp] <= 0).mean()),
                          "bbox": [int(x) for x in np.argwhere(comp).min(0)] + [int(x) for x in np.argwhere(comp).max(0)]})
            ign |= comp
    # missed inactive
    excl_i = gi | (vi >= 13)
    ki = (vi >= 20) & keep
    li, ni = ndi.label(ki, C.S8)
    for i in range(1, ni + 1):
        comp = li == i
        n = int(comp.sum())
        if n < 100 or gi[comp].mean() >= 0.1:
            continue
        cls = np.bincount(gt[comp].astype(np.int64), minlength=256)
        cls = {int(c): int(m) for c, m in enumerate(cls) if m}
        cands.append({"type": "MI", "kind": "region", "px": n, "meanV": float(vi[comp].mean()), "meanQ": float(qi[comp].mean()),
                      "z": C.contrast_z(gry, comp, excl_i, valid), "classes": cls,
                      "repl": bool((w4i[comp] >= 3).mean() >= 0.5), "repl_share": float((w4i[comp] >= 3).mean()),
                      "bbox": [int(x) for x in np.argwhere(comp).min(0)] + [int(x) for x in np.argwhere(comp).max(0)]})
        ign |= comp
    # spurious inactive
    lgi, ngi = ndi.label(gi, C.S8)
    icomp_stats = []
    for i in range(1, ngi + 1):
        comp = lgi == i
        n = int(comp.sum())
        share_low = float((vi[comp] <= 2).mean())
        z = C.contrast_z(gry, comp, excl_i, valid) if n >= 100 else float("nan")
        icomp_stats.append([n, share_low, z, float((vi[comp] >= 13).mean())])
        if n >= 100 and share_low >= 0.9:
            cands.append({"type": "SI", "kind": "region", "px": n, "meanV": float(vi[comp].mean()), "meanQ": float(qi[comp].mean()),
                          "z": z, "classes": {11: n}, "repl": bool((w4i[comp] <= 0).mean() >= 0.9),
                          "repl_share": float((w4i[comp] <= 0).mean()),
                          "bbox": [int(x) for x in np.argwhere(comp).min(0)] + [int(x) for x in np.argwhere(comp).max(0)]})
            ign |= comp
    # ---- label variants (crack)
    sk = C.skeletonize(g) & keep
    w3 = ndi.binary_dilation(sk, structure=S3) & keep if sk.any() else sk
    go = (old == C.CRACK) & keep
    gio = (old == C.INACT) & keep
    keep2 = keep & ~ign
    gvar = {"v11": (g, keep), "old": (go, keep), "skel": (sk, keep), "w3": (w3, keep), "candign": (g & keep2, keep2)}
    near_gv = {k: (near_g if k == "v11" else edt_le2(v[0])) for k, v in gvar.items()}
    giv = {"v11": gi, "old": gio, "skel": gi, "w3": gi, "candign": gi & keep2}
    rec = np.zeros((NM + 1, len(VAR), 10), np.int64)  # models + consensus (vc >= 13)
    errdec = np.zeros((NM, 12), np.int64)
    cons_p = (vc >= 13) & keep
    for j in range(NM + 1):
        pj = pc[j] if j < NM else cons_p
        npj = near_p[j] if j < NM else edt_le2(cons_p)
        pij = pi[j] if j < NM else ((vi >= 13) & keep)
        for vk, var in enumerate(VAR):
            gg, kk = gvar[var]
            if var == "candign":
                pp = pj & kk
                npp = edt_le2(pp) if ign.any() else npj
                rec[j, vk, :7] = crack_counts(pp, gg, kk, near_p=npp, near_g=near_gv[var])
                rec[j, vk, 7:] = inact_counts(pij & kk, giv[var])
            else:
                rec[j, vk, :7] = crack_counts(pj, gg, kk, near_p=npj, near_g=near_gv[var])
                rec[j, vk, 7:] = inact_counts(pij, giv[var])
        if j < NM:
            fn = g & ~npj
            fp = pj & ~near_g
            ifn = gi & ~pij
            ifp = pij & ~gi
            errdec[j] = [int((fn & (ncov <= 5)).sum()), int((fn & (ncov >= 6) & (ncov <= 19)).sum()), int((fn & (ncov >= 20)).sum()),
                         int((fp & (ncov >= 20)).sum()), int((fp & (ncov >= 6) & (ncov <= 19)).sum()), int((fp & (ncov <= 5)).sum()),
                         int((fn & ign).sum()), int((fp & ign).sum()),
                         int((ifn & (vi <= 5)).sum()), int((ifn & (vi > 5)).sum()), int((ifp & (vi >= 20)).sum()), int((ifp & (vi < 20)).sum())]
    # ---- soft-min (Lad & Mueller) on binary self-confidence, crack and inactive
    def softmin(s):
        s = s[keep].astype(np.float64)
        w = np.exp(-(s - s.min()) / 0.1)
        return float((s * w).sum() / w.sum())
    sm_c = softmin(np.where(g, qc, 1 - qc))
    sm_i = softmin(np.where(gi, qi, 1 - qi))
    os.makedirs(C.CACHE / "cons", exist_ok=True)
    np.savez_compressed(C.CACHE / "cons" / f"{stem}.npz", vc=vc, vi=vi, ncov=ncov, w4=w4,
                        qc=np.round(qc * 250).astype(np.uint8), qi=np.round(qi * 250).astype(np.uint8), ign=ign)
    return stem, {"rec": rec, "w1g": np.array(w1g_rec, np.int64), "errdec": errdec, "cands": cands,
                  "gcomp": gcomp_stats, "icomp": icomp_stats, "softmin_c": sm_c, "softmin_i": sm_i,
                  "n_ign": int(ign.sum()), "g_px": int(g.sum()), "gi_px": int(gi.sum())}


S3 = np.ones((3, 3), bool)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=str(C.OUT / "pass_records.pkl"))
    a = ap.parse_args()
    assert a.workers <= 8
    stems = C.pool_stems()
    pool = set(stems)
    ri, wi = C.relay_index(), C.w1g_index()
    jobs = [(s, pool, [ri[m][s] for m in C.MODELS], [wi[("W1G_PF", sd)][s] for sd in (5, 6, 7, 8)]) for s in stems]
    if a.limit:
        jobs = jobs[: a.limit]
    t = time.time()
    out = {}
    import multiprocessing as mp
    with mp.get_context("fork").Pool(a.workers) as P:
        for i, (s, r) in enumerate(P.imap_unordered(do_cell, jobs, chunksize=1)):
            out[s] = r
            if (i + 1) % 50 == 0:
                print(f"{i + 1}/{len(jobs)} {time.time() - t:.0f}s", flush=True)
    meta = {"models": C.MODELS, "variants": VAR, "rec_cols": ["tp", "fp", "fn", "relP_hit", "relP_n", "relR_hit", "relR_n",
                                                               "i_tp", "i_fp", "i_fn"],
            "errdec_cols": ["fn_sys", "fn_var", "fn_own", "fp_sys", "fp_var", "fp_own", "fn_in_cand", "fp_in_cand",
                            "ifn_sys", "ifn_other", "ifp_sys", "ifp_other"],
            "w1g_cols": "same 10 cols, v11 only, seeds 5..8"}
    pickle.dump({"meta": meta, "cells": out}, open(a.out, "wb"))
    print("done", len(out), f"{time.time() - t:.0f}s", a.out)


if __name__ == "__main__":
    main()
