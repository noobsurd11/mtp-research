"""calib idea 2: does mapping each cell's intensity into the train distribution at TEST time move the models? (diagnostic)
Written 31 Oct ~14:50 IST, before any test-time-mapping number existed. Variants (calib_dump --tt, content px only, F6 letterbox rule):
  none      the plain dump (reference)
  cellz     per-cell affine: content mean / sd -> train content mean / sd
  modz      per-module affine (module stats over the set's own cells of that module; E1 modules have 1-2 cells)
  cellhist  per-cell histogram matching of content px to the pooled train content histogram (fixes shape, domain's gap)
Models: FINAL (ensemble, deployed b +0.75) and SUP100-PF (5 seeds, b 0). Sets: val (guard), Hanifi _rf F51 (selection set), E1 (descriptive).
Per variant the OP-rel b is re-chosen on that variant's own val records (deploy = normalise everything, pick b on val).
Reported: relR@2 / relP@2 / relF1@2 at the deployed b and at the variant's OP-rel b; oracle relF1@2 (ranking only, own labels,
diagnostic); cell AUROC; per stratum (E1 sh29 / other 77).
PRE-STATED READ (GO / NO-GO for a normalisation TRAINING arm):
  GO only if some variant, for BOTH FINAL and the SUP100-PF seed mean, (a) does not lower val relF1@2 at OP-rel by > 0.01 and
  (b) raises _rf F51 relF1@2 at OP-rel by >= 0.02. Otherwise NO-GO (S caveat: a test-time mapping is a weaker test than training
  with the normalisation; stated in the report).
  AMENDED 31 Oct ~17:35 IST, BEFORE any test-time-mapping number was read: the original (b) also allowed "or raises E1 sh29
  oracle relF1@2 by >= 0.03". Dropped because the user made E1 a second test set (never for selection); E1 is reported only.
Usage: python idea2_tt.py --rec DIR_with_plain_records --rectt DIR_with_tt_records --ctx e1_context.tsv --f51 F51.txt --out OUT.txt
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import el_metrics as E  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rec", required=True)
ap.add_argument("--rectt", required=True)
ap.add_argument("--ctx", required=True)
ap.add_argument("--f51", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
G = E.GRID
J = lambda b: int(np.argmin(np.abs(G - b)))
ctx = {f[0]: (f[2] == "scuff=1", f[3] == "halfcut=1") for f in (l.rstrip("\n").split("\t") for l in open(a.ctx)) if len(f) >= 4}
F51 = [l.strip() for l in open(a.f51) if l.strip()]
SUB = {"val": ("val", None), "F51": ("rf", F51), "E1": ("ext", None),
       "E1 sh29": ("ext", [s for s in ctx if ctx[s][0] and ctx[s][1]]), "E1 other77": ("ext", [s for s in ctx if not (ctx[s][0] and ctx[s][1])])}
VARS = ["none", "cellz", "modz", "cellhist"]


def path(member, var, sp):
    if var == "none":
        return Path(a.rec) / f"{member}.{sp}.json"
    base, _, m = member.partition("_m")
    name = f"{base}__{var}" + (f"_m{m}" if m else "")
    return Path(a.rectt) / f"{name}.{sp}.json"


def f1(p, r):
    return 2 * p * r / max(p + r, 1e-9)


res = {}
for arm, members, bdep in (("FINAL", ["FINAL"], 0.75), ("SUPPF5", [f"SUPPF5_m{i}" for i in range(5)], 0.0)):
    for var in VARS:
        for m in members:
            pv = path(m, var, "val")
            if not pv.exists():
                continue
            V = json.load(open(pv))["cells"]
            op = E.choose_op(E.curves(V), "relR", "relP")
            for sname, (sp, st) in SUB.items():
                p = path(m, var, sp)
                if not p.exists():
                    continue
                C = V if sp == "val" else json.load(open(p))["cells"]
                c = E.curves(C, st)
                F = 2 * c["relP"] * c["relR"] / np.maximum(c["relP"] + c["relR"], 1e-9)
                cl = E.cell_level(C, bdep, st)
                res.setdefault((arm, var, sname), []).append({
                    "relF1_dep": float(F[J(bdep)]), "relR_dep": float(c["relR"][J(bdep)]), "relP_dep": float(c["relP"][J(bdep)]),
                    "relF1_opr": float(F[op["j"]]), "relR_opr": float(c["relR"][op["j"]]), "relP_opr": float(c["relP"][op["j"]]),
                    "oracle_relF1": float(np.nanmax(np.nan_to_num(F, nan=0))), "b_opr": op["b"], "cell_auroc": cl["auroc"],
                    "fa_dep": cl["fa_rate"]})
L = [__doc__.split("Usage")[0].strip(), "", "results: mean (sd over seeds for SUPPF5); deltas vs 'none' in brackets", ""]
keys = ["relF1_opr", "relR_opr", "relP_opr", "relF1_dep", "oracle_relF1", "cell_auroc", "fa_dep", "b_opr"]
go = {}
for arm in ("FINAL", "SUPPF5"):
    for sname in SUB:
        base = res.get((arm, "none", sname))
        for var in VARS:
            rs = res.get((arm, var, sname))
            if not rs:
                continue
            parts = []
            for k in keys:
                v = np.array([r[k] for r in rs]); b0 = np.array([r[k] for r in base]) if base else None
                s = f"{k} {np.nanmean(v):.3f}" + (f"({np.nanstd(v, ddof=1):.3f})" if len(v) > 1 else "")
                if base is not None and var != "none":
                    s += f" [{np.nanmean(v) - np.nanmean(b0):+.3f}]"
                parts.append(s)
            L.append(f"{arm:6s} {sname:10s} {var:8s}: " + "; ".join(parts))
            if base is not None and var != "none":
                d = lambda k: float(np.nanmean([r[k] for r in rs]) - np.nanmean([r[k] for r in base]))
                go.setdefault((arm, var), {})[sname] = {"relF1_opr": d("relF1_opr"), "oracle_relF1": d("oracle_relF1")}
        L.append("")
L.append("pre-stated read per variant (needs BOTH FINAL and SUPPF5):")
for var in VARS[1:]:
    ok_all = True
    for arm in ("FINAL", "SUPPF5"):
        g = go.get((arm, var), {})
        if not g:
            ok_all = False; continue
        a_ok = g.get("val", {}).get("relF1_opr", -1) >= -0.01
        b_ok = g.get("F51", {}).get("relF1_opr", -1) >= 0.02  # E1 branch removed (amendment above)
        ok_all &= a_ok and b_ok
        L.append(f"  {var} {arm}: val relF1@OPr {g.get('val', {}).get('relF1_opr', float('nan')):+.3f} (>= -0.01: {a_ok}); "
                 f"F51 relF1@OPr {g.get('F51', {}).get('relF1_opr', float('nan')):+.3f} -> {a_ok and b_ok}; "
                 f"(E1 sh29 oracle relF1 {g.get('E1 sh29', {}).get('oracle_relF1', float('nan')):+.3f}, descriptive, not in the rule)")
    L.append(f"  => {var}: {'GO' if ok_all else 'NO-GO'}")
Path(a.out).write_text("\n".join(L) + "\n")
print("\n".join(L))
