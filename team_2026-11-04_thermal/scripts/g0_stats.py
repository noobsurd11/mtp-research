"""G0 per pick1/plan_pick1.md (R3 + Amendments 1-3). usage: python -I g0_stats.py <set_dir_with_orient_subdirs> <primary_orient> <out.json> [<set2_dir> <primary2> ...]
Cells: ir_dT (module-centred), el_dark_frac. Positive = el_dark_frac >= 0.05. QA: module excluded if EL or IR res_rms_pct_cell > 5.
Stats: Spearman rho(dT, dark); AUROC of -dT for positives (predicted: cooler); inner cells only beside; 4-orientation table;
best-of-4 permutation null (1,000 within-module permutations, seed 20261104)."""
import csv, glob, json, os, sys
import numpy as np
from scipy.stats import spearmanr, rankdata
ORI = ["id", "fliph", "flipv", "rot180"]

def auroc(score, y):
    y = np.asarray(y, bool); s = np.asarray(score, float)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0: return float("nan")
    r = rankdata(s)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

fl = lambda x: float(x) if x not in ("", "nan", "NaN") else float("nan")

def load(d):
    mods = {}
    for f in sorted(glob.glob(os.path.join(d, "*_cells.tsv"))):
        reg = json.load(open(f.replace("_cells.tsv", "_reg.json")))
        q = {m: reg["modalities"][m]["qa"]["res_rms_pct_cell"] for m in ("el", "ir")}
        rows = list(csv.DictReader(open(f), delimiter="\t"))
        nr, nc = reg["grid_expected"]
        mods[rows[0]["module"]] = {"qa": q, "nr": nr, "nc": nc, "orient": reg.get("orient", {}).get("ir"),
            "cells": [(int(r["row"]), int(r["col"]), fl(r["el_dark_frac"]), fl(r["ir_dT"])) for r in rows]}
    return mods

def rc_centre(mods):
    out = {}
    for m, M in mods.items():
        g = np.full((M["nr"], M["nc"]), np.nan); A = {}
        for i, j, a, t in M["cells"]:
            if i < M["nr"] and j < M["nc"]: g[i, j] = t; A[(i, j)] = a
        g = g - np.nanmedian(g, axis=1, keepdims=True)
        g = g - np.nanmedian(g, axis=0, keepdims=True)
        out[m] = dict(M, cells=[(i, j, A[(i, j)], float(g[i, j])) for i, j, a, t in M["cells"] if i < M["nr"] and j < M["nc"]])
    return out

def stats(mods, keep):
    dT, dk, inner = [], [], []
    for m in keep:
        M = mods[m]
        for i, j, a, t in M["cells"]:
            if np.isfinite(a) and np.isfinite(t):
                dT.append(t); dk.append(a); inner.append(0 < i < M["nr"] - 1 and 0 < j < M["nc"] - 1)
    dT, dk, inner = map(np.array, (dT, dk, inner))
    out = {}
    for name, sel in (("all", np.ones_like(inner, bool)), ("inner", inner)):
        y = dk[sel] >= 0.05
        rho = float(spearmanr(dT[sel], dk[sel]).statistic) if sel.sum() > 2 else float("nan")
        au = auroc(-dT[sel], y) if y.sum() >= 5 else float("nan")
        out[name] = {"n_cells": int(sel.sum()), "n_pos": int(y.sum()), "rho": rho, "auroc_cooler": au,
                     "auroc_warmer": (1 - au) if np.isfinite(au) else float("nan")}
    return out

def verdict(s):
    a, r = s["auroc_cooler"], s["rho"]
    if not np.isfinite(a): return "no AUROC (n_pos < 5); rho only"
    if a >= 0.8: return "GO (AUROC >= 0.8, predicted sign)"
    if a <= 0.2: return "signal, opposite sign"
    if abs(r) < 0.3 and a < 0.7: return "null (|rho| < 0.3 and AUROC < 0.7)"
    return "between (no go, no null)"

def run(setdir, prim):
    res = {"set": setdir, "primary": prim, "orient": {}}
    allm = {o: load(os.path.join(setdir, o)) for o in ORI}
    base = allm[prim]
    keep = [m for m, M in base.items() if M["qa"]["el"] <= 5 and M["qa"]["ir"] <= 5]
    if os.environ.get("G0_KEEP"):   # co-signed keep list is authoritative (it already applies the residual rule; sensitivity B adds borderline modules back)
        vis = {r["module"]: r["keep"] for r in csv.DictReader(open(os.environ["G0_KEEP"]), delimiter="\t")}
        keep = [m for m in base if vis.get(m) == "yes"]
    res["modules"] = len(base); res["kept"] = len(keep)
    res["excluded"] = {m: base[m]["qa"] for m in base if m not in keep}
    res["qa"] = {m: base[m]["qa"] for m in base}
    for o in ORI:
        res["orient"][o] = stats(allm[o], keep)
    res["rc_centred_primary"] = stats(rc_centre(allm[prim]), keep)
    p = res["orient"][prim]
    res["verdict_all"] = verdict(p["all"]); res["verdict_inner"] = verdict(p["inner"])
    res["verdict"] = res["verdict_all"] if res["verdict_all"] == res["verdict_inner"] else "inconclusive (edge-sensitive): all=%s; inner=%s" % (res["verdict_all"], res["verdict_inner"])
    # best-of-4 null: permute the identity-orientation IR cell values within module, then apply each orientation map
    rng = np.random.default_rng(20261104)
    ids = allm["id"]
    def ori_map(i, j, nr, nc, o):
        return {"id": (i, j), "fliph": (i, nc - 1 - j), "flipv": (nr - 1 - i, j), "rot180": (nr - 1 - i, nc - 1 - j)}[o]
    obs_best = max(res["orient"][o]["all"]["auroc_cooler"] for o in ORI)
    null = []
    for _ in range(1000):
        best = -1
        perm = {}
        for m in keep:
            M = ids[m]; cells = {(i, j): t for i, j, a, t in M["cells"]}
            keys = [k for k in cells if np.isfinite(cells[k])]; vals = np.array([cells[k] for k in keys]); rng.shuffle(vals)
            perm[m] = dict(zip(keys, vals))
        for o in ORI:
            dT, y = [], []
            for m in keep:
                M = ids[m]
                for i, j, a, t in M["cells"]:
                    k = ori_map(i, j, M["nr"], M["nc"], o)
                    if np.isfinite(a) and k in perm[m] and np.isfinite(perm[m][k]): dT.append(perm[m][k]); y.append(a >= 0.05)
            if sum(y) >= 5: best = max(best, auroc(-np.array(dT), y))
        null.append(best)
    null = np.array(null)
    res["best_of_4"] = {"observed": obs_best, "argmax": max(ORI, key=lambda o: res["orient"][o]["all"]["auroc_cooler"]),
                        "null_p": float((1 + (null >= obs_best).sum()) / (1 + len(null))), "null_q95": float(np.quantile(null, 0.95))}
    alt = [o for o in ORI if o != prim and res["orient"][o]["all"]["auroc_cooler"] - p["all"]["auroc_cooler"] > 0.15]
    res["orientation_unresolved"] = bool(alt and res["best_of_4"]["null_p"] < 0.01)
    return res

if __name__ == "__main__":
    a = sys.argv[1:]; out = a[2]
    sets = [(a[0], a[1])] + [(a[i], a[i + 1]) for i in range(3, len(a), 2)]
    R = [run(d, p) for d, p in sets]
    if len(sets) > 1:   # pooled, primary orientation of each set, QA-kept modules only
        pooled = {}; keep = []
        for (d, p), r in zip(sets, R):
            mods = load(os.path.join(d, p))
            for m in mods:
                if m not in r["excluded"]: pooled[m] = mods[m]; keep.append(m)
        ps = stats(pooled, keep)
        va, vi = verdict(ps["all"]), verdict(ps["inner"])
        R.append({"set": "pooled", "primary": "per set", "kept": len(keep), "modules": len(keep), "orient": {"primary": ps},
                  "verdict": va if va == vi else "inconclusive (edge-sensitive): all=%s; inner=%s" % (va, vi),
                  "best_of_4": None, "orientation_unresolved": None})
    json.dump(R, open(out, "w"), indent=1, default=float)
    for r in R:
        print(r["set"], "kept", r["kept"], "/", r["modules"], "| primary", r["primary"], r["orient"].get(r["primary"], r["orient"].get("primary")), "|", r["verdict"], "| best4", r["best_of_4"], "| unresolved", r["orientation_unresolved"])
