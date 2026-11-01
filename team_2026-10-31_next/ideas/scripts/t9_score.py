"""t9_score (found, 31 Oct 2026): applies the T9 pass rule (ideas/t9_prereg.md §5) to el_metrics records of t9_dump outputs.
Written before any T9 outcome. Uses calib's el_metrics (curves, cell_level, choose_op, GRID) unchanged.
Usage: python t9_score.py --rec DIR --fam FINAL --op 0.75 [--fam SUPPF5 --val-rec SUPPF5.val.json] --rf RFDIR --train TRAIN.txt --out OUT.json
Records expected in DIR: {fam}__V0.rf.json, {fam}__V2.rf.json, {fam}__V3.rf.json, optional {fam}__V1.rf.json, {fam}__V0rf.rf.json.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from el_metrics import GRID, cell_level, choose_op, curves  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rec", required=True)
ap.add_argument("--fam", action="append", required=True)
ap.add_argument("--op", action="append", type=float, default=[], help="fixed b per --fam in order; omit for a fam that uses --val-rec")
ap.add_argument("--val-rec", action="append", default=[], help="FAM=PATH: calib's V0 val records; OP-rel b chosen there (A0)")
ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
ap.add_argument("--train", default="/home/noob/work/el_f3/data/splits/train.txt")
ap.add_argument("--boot", type=int, default=2000)
ap.add_argument("--out", required=True)
a = ap.parse_args()
R = Path(a.rec)
mod = lambda s: "_".join(s.split("_")[:2])
rows = [l.rstrip("\n").split("\t") for l in open(Path(a.rf) / "rf_context.tsv") if l.strip()]
H = {h: i for i, h in enumerate(rows[0])}
half = {r[0]: r[H["halfcut"]] == "1" for r in rows[1:]}
tm = {mod(l.strip()) for l in open(a.train) if l.strip()}


def ap_of(cv, rcap=None):
    """Step-wise AP over the bias grid: b ascending = recall non-decreasing; AP = sum P_i (R_i - R_{i-1}), R_0 = 0.
    rcap (judge A2): area only up to recall rcap (last step clipped), not normalised."""
    P, Rr = np.nan_to_num(np.asarray(cv["P"], float)), np.nan_to_num(np.asarray(cv["R"], float))
    cap = 1.0 if rcap is None else rcap
    out, prev = 0.0, 0.0
    for p, r in zip(P, Rr):
        r = min(r, cap)
        if r > prev:
            out += p * (r - prev); prev = r
    return out


def maxr(cv):
    return float(np.nanmax(np.nan_to_num(np.asarray(cv["R"], float)))) if cv["gt_px"] else float("nan")


def dap(C, C0, stems_or_none, cells_c=None, cells_0=None):
    """A2: AP gain on the common recall range [0, R_common] of the two variants on the same cells. Returns (dAP, R_common)."""
    cv = curves(cells_c if cells_c is not None else C, stems_or_none); cv0 = curves(cells_0 if cells_0 is not None else C0, stems_or_none)
    rc = min(maxr(cv), maxr(cv0))
    return ap_of(cv, rc) - ap_of(cv0, rc), rc


def load(fam, v):
    f = R / f"{fam}__{v}.rf.json"
    return json.load(open(f))["cells"] if f.exists() else None


def sets(cells):
    P = [s for s in cells if not half[s] and mod(s) not in tm]
    return {"P": P, "H36": [s for s in cells if half[s]], "F19": [s for s in cells if not half[s] and mod(s) in tm]}


def apset(c, st):
    return ap_of(curves(c, st)) if st else float("nan")


val_ops = dict(x.split("=", 1) for x in a.val_rec)
res = {"grid": [float(GRID.min()), float(GRID.max())], "families": {}}
ops = iter(a.op)
for fam in a.fam:
    if fam in val_ops:
        vr = json.load(open(val_ops[fam])); assert vr["set"] == "val"
        b = choose_op(curves(vr["cells"]), "relR", "relP")["b"]
    else:
        b = next(ops)
    jb = int(np.argmin(np.abs(GRID - b))); assert abs(GRID[jb] - b) < 1e-9
    V0 = load(fam, "V0"); S = sets(V0)
    crack_mods = sorted({mod(s) for s in S["P"] if V0[s]["n_gt"] >= 20})
    Pmods = sorted({mod(s) for s in S["P"]})
    fr = {"op_b": b, "n": {k: len(v) for k, v in S.items()}, "P_modules": len(Pmods), "P_crack_modules": crack_mods, "variants": {}}
    for v in ("V0", "V1", "V2", "V3", "V0rf"):
        C = load(fam, v)
        if C is None:
            continue
        St = sets(C) if v != "V0rf" else {k: [s for s in st if s in C] for k, st in S.items()}
        e = {k: {"ap": apset(C, st), "cell_auroc": cell_level(C, b, st)["auroc"] if st else float("nan")} for k, st in St.items()}
        for k, st in St.items():
            if st:
                cv = curves(C, st)
                e[k].update({"relR_op": float(cv["relR"][jb]), "relP_op": float(cv["relP"][jb]), "compR_op": float(cv["compR"][jb]),
                             "compP_op": float(cv["compP"][jb]), "inactIoU_op": float(cv["inactIoU"][jb]),
                             "fa_px_crackfree_op": int(sum(C[s]["pred"][jb] for s in st if C[s]["n_gt"] == 0)),
                             "n_crackfree": sum(1 for s in st if C[s]["n_gt"] == 0)})
        fr["variants"][v] = e
    # rule (V2, V3 vs V0, eligible pool-copy cells)
    for v in ("V2", "V3"):
        C = load(fam, v)
        if C is None:
            continue
        d_ap, rc = dap(C, V0, S["P"]); maxr_v, maxr_0 = maxr(curves(C, S["P"])), maxr(curves(V0, S["P"]))
        rng = np.random.default_rng(0); bs = []
        by = {m: [s for s in S["P"] if mod(s) == m] for m in Pmods}
        for _ in range(a.boot):
            pick = rng.choice(len(Pmods), len(Pmods), replace=True)
            st = [s for i in pick for s in by[Pmods[i]]]
            # resampled modules may repeat: duplicate stems are counted by passing a multiset through curves via suffixing
            cc = {f"{s}#{n}": C[s] for n, s in enumerate(st)}; c0 = {f"{s}#{n}": V0[s] for n, s in enumerate(st)}
            bs.append(dap(None, None, None, cc, c0)[0])
        lo = float(np.percentile(bs, 2.5))
        signs = {m: dap(C, V0, by[m])[0] for m in crack_mods}
        up = sum(1 for x in signs.values() if x > 0)

        def fa(st):
            return int(sum(C[s]["pred"][jb] for s in st if C[s]["n_gt"] == 0)), int(sum(V0[s]["pred"][jb] for s in st if V0[s]["n_gt"] == 0))
        faH, faH0 = fa(S["H36"]); faP, faP0 = fa(S["P"])
        bound = lambda x0: max(1.5 * x0, x0 + 200)  # judge A3
        percell = {k: {s: [int(V0[s]["pred"][jb]), int(C[s]["pred"][jb])] for s in S[k] if V0[s]["n_gt"] == 0} for k in ("H36", "P")}
        d_f19, rc19 = dap(C, V0, S["F19"])
        terms = {"1_P_dAP>=0.03": (d_ap, d_ap >= 0.03), "2_boot_lo>0": (lo, lo > 0),
                 "3_sign>=7of8": (f"{up}/{len(crack_mods)}", up >= len(crack_mods) - 1),  # prereg: 8 crack modules, >= 7 up
                 "4a_FA_H36<=max(1.5xV0,V0+200)": ((faH, faH0), faH <= bound(faH0)), "4b_FA_P<=max(1.5xV0,V0+200)": ((faP, faP0), faP <= bound(faP0)),
                 "5_F19_dAP>=-0.01": (d_f19, d_f19 >= -0.01)}
        informative = rc >= 0.5
        fr[f"rule_{v}"] = {"R_common_P": round(rc, 4), "maxR_P": {"V": round(maxr_v, 4), "V0": round(maxr_0, 4)}, "R_common_F19": round(rc19, 4),
                           "informative": informative,
                           "terms": {k: [x if not isinstance(x, float) else round(x, 4), bool(ok)] for k, (x, ok) in terms.items()},
                           "per_module_dAP": {m: round(x, 4) for m, x in signs.items()}, "fa_per_cell_V0_V": percell,
                           "pass": informative and all(ok for _, ok in terms.values())}
    res["families"][fam] = fr
res["T9_pass"] = {v: all(res["families"][f].get(f"rule_{v}", {}).get("pass", False) for f in a.fam) for v in ("V2", "V3")}
res["T9_informative"] = {v: all(res["families"][f].get(f"rule_{v}", {}).get("informative", False) for f in a.fam) for v in ("V2", "V3")}
json.dump(res, open(a.out, "w"), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
