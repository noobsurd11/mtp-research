#!/usr/bin/env python3
"""pick3b_r12.py: pick 3b readouts 3b-R1 and 3b-R2 (plan_pick3b.md v1, md5 eaec6f26, sections 2-3).

Inputs:  pick 1's frozen A3 module table (S_IR, EL dark fraction, I-V csv path, module type, defect folder)
         and the A3 STC I-V csv files (read for Pmax / FF only).
Modes:   --discover  : prints I-V file structure facts only (columns, rows), no statistics
         --run       : applies the frozen rules
Run:     ~/mtp/research/.venv/bin/python -I scripts/pick3b_r12.py --table pick1/out/A3_module_table.tsv \
             --root ~/mtp/datasets/thermal_public/A3_dtu/extracted --out pick3/out/b --run
"""
import argparse
import csv
import json
import os
import re
import sys

import numpy as np
from scipy import stats

PNOM = {"305": 305.0, "295": 295.0, "540": 540.0}   # nameplate W by module type (R via check: DTU slides)
B = 2000
RNG = np.random.default_rng(20261104)


def read_table(path):
    rows = [r for r in csv.DictReader((l for l in open(path) if not l.startswith("#")), delimiter="\t")]
    return rows


def iv_numeric(path):
    """Numeric matrix + header tokens from an I-V csv (comma / semicolon / tab)."""
    txt = open(path, errors="replace").read().splitlines()
    hdr, rows = [], []
    for line in txt:
        toks = [t.strip() for t in re.split(r"[,;\t]", line) if t.strip() != ""]
        if not toks:
            continue
        try:
            rows.append([float(t) for t in toks])
        except ValueError:
            hdr.append(toks)
    return hdr, rows


def pmax_ff(path):
    """Pmax and FF from an I-V csv. Prefers explicit Pmax / FF fields if present in the header block;
    else computes from V, I columns (Pmax = max V*I; FF = Pmax / (Voc * Isc))."""
    hdr, rows = iv_numeric(path)
    flat = " ".join(" ".join(h) for h in hdr).lower()
    # explicit key-value lines like "Pmax, 280.1"
    kv = {}
    for line in open(path, errors="replace"):
        toks = [t.strip() for t in re.split(r"[,;\t:]", line) if t.strip() != ""]
        if len(toks) >= 2:
            try:
                kv[toks[0].lower()] = float(toks[1])
            except ValueError:
                pass
    pm = next((v for k, v in kv.items() if k in ("pmax", "pmp", "pmpp", "p_max", "pmax (w)", "pmp (w)")), None)
    ff = next((v for k, v in kv.items() if k in ("ff", "fill factor", "ff (%)")), None)
    if pm is not None:
        if ff is not None and ff > 1.5:
            ff = ff / 100.0
        return pm, ff, "explicit fields"
    if not rows:
        return None, None, "no numeric rows"
    lens = [len(r) for r in rows]
    mode = max(set(lens), key=lens.count)
    M = np.array([r for r in rows if len(r) == mode])
    if M.shape[1] < 2:
        return None, None, "one column"
    # assume the first two columns are V and I unless the header says otherwise
    vi, ii = 0, 1
    if hdr:
        h = [t.lower() for t in hdr[-1]]
        vcands = [k for k, t in enumerate(h) if t.startswith("v") or "volt" in t]
        icands = [k for k, t in enumerate(h) if t.startswith("i") or "curr" in t or "amp" in t]
        if vcands and icands:
            vi, ii = vcands[0], icands[0]
    V, I = M[:, vi], M[:, ii]
    if np.nanmedian(I) < 0:
        I = -I
    P = V * I
    pm = float(np.nanmax(P))
    isc = float(I[np.argmin(np.abs(V))])
    voc = float(V[np.argmin(np.abs(I))])
    ff = pm / (voc * isc) if voc > 0 and isc > 0 else None
    return pm, ff, f"computed from columns {vi},{ii}"


def spearman_ci(x, y, groups=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return {"n": int(n), "rho": None}
    rho = stats.spearmanr(x, y).statistic
    bs = []
    for _ in range(B):
        k = RNG.integers(0, n, n)
        if len(np.unique(k)) < 3:
            continue
        r = stats.spearmanr(x[k], y[k]).statistic
        if np.isfinite(r):
            bs.append(r)
    lo, hi = np.percentile(bs, [2.5, 97.5]) if bs else (None, None)
    return {"n": int(n), "rho": float(rho), "ci95": [float(lo), float(hi)]}


def loo_r2(X, y):
    """Leave-one-module-out R^2 of an OLS model with intercept."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    n = len(y)
    pred = np.empty(n)
    for k in range(n):
        m = np.ones(n, bool)
        m[k] = False
        A = np.c_[np.ones(m.sum()), X[m]]
        beta, *_ = np.linalg.lstsq(A, y[m], rcond=None)
        pred[k] = np.r_[1.0, X[k]] @ beta
    ss = np.sum((y - y.mean()) ** 2)
    return 1 - np.sum((y - pred) ** 2) / ss if ss > 0 else float("nan")


def r12(rows, label_key):
    el = np.array([float(r["el_dark"]) for r in rows])
    ir = np.array([float(r["S_IR"]) for r in rows])
    y = np.array([float(r[label_key]) for r in rows])
    out = {"R1_rho_ELdark_vs_label": spearman_ci(el, y), "R2a_rho_SIR_vs_label": spearman_ci(ir, y)}
    if len(y) >= 6:
        r2_el = loo_r2(el[:, None], y)
        r2_both = loo_r2(np.c_[el, ir], y)
        bs = []
        n = len(y)
        for _ in range(B):
            k = RNG.integers(0, n, n)
            if len(np.unique(k)) < 6:
                continue
            a, b = loo_r2(el[k][:, None], y[k]), loo_r2(np.c_[el[k], ir[k]], y[k])
            if np.isfinite(a) and np.isfinite(b):
                bs.append(b - a)
        out["R2b_looR2_EL"] = float(r2_el)
        out["R2b_looR2_EL_plus_IR"] = float(r2_both)
        out["R2b_dR2"] = float(r2_both - r2_el)
        out["R2b_dR2_ci95"] = [float(x) for x in np.percentile(bs, [2.5, 97.5])] if bs else None
    return out


def verdicts(res):
    def lab(r, hi=0.5, lo=0.3):
        if r.get("rho") is None or r["n"] < 15:
            return "not computed (n < 15)"
        if r["rho"] >= hi and r["ci95"][0] > 0:
            return "valid / proxy"
        if r["rho"] < lo:
            return "invalid / not a proxy"
        return "weak"
    v = {"3b-R1": lab(res["R1_rho_ELdark_vs_label"]), "3b-R2a": lab(res["R2a_rho_SIR_vs_label"])}
    if "R2b_dR2" in res:
        d, ci = res["R2b_dR2"], res["R2b_dR2_ci95"]
        v["3b-R2b"] = ("IR adds" if (d >= 0.10 and ci and ci[0] > 0) else
                       "no added value" if d < 0.05 else "in between")
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--discover", action="store_true")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    T = read_table(a.table)
    if a.discover:
        facts = {"table_columns": list(T[0].keys()) if T else [], "n_rows": len(T), "iv_files": []}
        for r in T[:3]:
            p = os.path.join(a.root, r.get("iv_csv", "") or "")
            if os.path.isfile(p):
                hdr, rows = iv_numeric(p)
                facts["iv_files"].append({"file": r.get("iv_csv"), "header_lines": [h[:8] for h in hdr[:6]],
                                          "n_numeric_rows": len(rows),
                                          "row_lengths": sorted({len(x) for x in rows})})
        json.dump(facts, open(os.path.join(a.out, "r12_discover.json"), "w"), indent=1)
        print(json.dumps(facts, indent=1))
        return
    mods = []
    for r in T:
        if (r.get("defect", "") or "").lower().startswith("soil"):
            continue
        p = os.path.join(a.root, r.get("iv_csv", "") or "")
        if not os.path.isfile(p) or r.get("el_dark") in (None, "", "nan") or r.get("S_IR") in (None, "", "nan"):
            continue
        pm, ff, how = pmax_ff(p)
        if pm is None:
            continue
        mt = re.search(r"(305|295|540)", r.get("module_type", "") or "")
        dP = 1 - pm / PNOM[mt.group(1)] if mt else float("nan")
        mods.append({"module": r.get("module"), "defect": r.get("defect"), "type": mt.group(1) if mt else "",
                     "el_dark": r["el_dark"], "S_IR": r["S_IR"], "Pmax": pm, "FF": ff if ff is not None else float("nan"),
                     "dP": dP, "iv_how": how})
    ffm = np.nanmedian([m["FF"] for m in mods]) if mods else float("nan")
    for m in mods:
        m["FFloss"] = 1 - m["FF"] / ffm if np.isfinite(m["FF"]) else float("nan")
    with_dp = [m for m in mods if np.isfinite(m["dP"])]
    label = "dP" if len(with_dp) >= 15 else "FFloss"
    base = with_dp if label == "dP" else [m for m in mods if np.isfinite(m["FFloss"])]
    res = {"plan": "plan_pick3b.md v1 eaec6f26", "label": label, "n_modules_total": len(mods),
           "n_with_dP": len(with_dp), "FF_median": float(ffm)}
    for name, subset in (("all_non_soiling", base),
                         ("non_diode", [m for m in base if "diode" not in (m["defect"] or "").lower()])):
        rr = r12(subset, label)
        res[name] = {"n": len(subset), **rr, "verdicts": verdicts(rr)}
        rr_ff = r12([m for m in subset if np.isfinite(m["FFloss"])], "FFloss")
        res[name]["FFloss_secondary"] = {k: v for k, v in rr_ff.items()}
        # within module type (plan section 2: "all modules and within module type"), descriptive
        res[name]["within_type"] = {}
        for t in sorted({m["type"] for m in subset if m["type"]}):
            sub = [m for m in subset if m["type"] == t]
            res[name]["within_type"][t] = {
                "n": len(sub),
                "R1_rho_ELdark_vs_label": spearman_ci([float(m["el_dark"]) for m in sub], [m[label] for m in sub]),
                "R2a_rho_SIR_vs_label": spearman_ci([float(m["S_IR"]) for m in sub], [m[label] for m in sub])}
    with open(os.path.join(a.out, "r12_modules.tsv"), "w") as f:
        keys = list(mods[0].keys()) if mods else []
        f.write("\t".join(keys) + "\n")
        for m in mods:
            f.write("\t".join(str(m[k]) for k in keys) + "\n")
    json.dump(res, open(os.path.join(a.out, "r12_summary.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
