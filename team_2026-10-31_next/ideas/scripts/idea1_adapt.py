"""calib idea 1: label-free per-module threshold adaptation, pre-stated before any rf / E1 number of it was seen.
Selection / measurement set: Hanifi _rf (106, hygiene). E1: descriptive only. No E1 label chooses anything.
Per member (run or ensemble), with b_OP = the val-chosen OP-rel b (max val relR@2 s.t. val relP@2 >= 0.90):
  A0  global: b = b_OP everywhere (reference).
  A1  per-module quantile (Om): f_val = val pooled predicted-crack px fraction at b_OP; per module M, b_M = smallest grid b with
      pooled frac_M(b) >= f_val (clipped to the grid). Label-free: uses only the module's own eval cells' margins.
  A2  per-module tail shift: q = 1e-4; b_M = b_OP + (bq_M - bq_val), bq = smallest b with pooled frac(b) >= q (clipped).
  A3  cell-type routing: half-cut cells get b_half = argmax relF1@2 on the rf half-cut cells (labelled, non-E1, allowed for selection);
      full cells keep b_OP. Half-cut flag = geometry (label-free at deployment). rf numbers for A3 are in-sample.
Reported: pooled relR@2, relP@2, relF1@2, comp recall / precision, crack px predicted on crack-free cells, per set / stratum.
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
ap.add_argument("--ctx", required=True)
ap.add_argument("--rfctx", required=True)
ap.add_argument("--f51", required=True, help="F51 stems: _rf full cells from modules not in train (= t9_prereg P set)")
ap.add_argument("--out", required=True)
ap.add_argument("--targets", nargs="+", default=["FINAL", "SUPPF5", "SUP5"])
a = ap.parse_args()
R = Path(a.rec); G = E.GRID
ctx = {f[0]: (f[2] == "scuff=1", f[3] == "halfcut=1") for f in (l.rstrip("\n").split("\t") for l in open(a.ctx)) if len(f) >= 4}
rfx = {}
for i, l in enumerate(open(a.rfctx)):
    f = l.rstrip("\n").split("\t")
    if i:
        rfx[f[0]] = (f[6] == "1", f[5] == "1")
F51 = {l.strip() for l in open(a.f51) if l.strip()}
half = lambda s, sp: (ctx[s][1] if sp == "ext" else rfx[s][1])
STRATA = {"ext": {"E1 all": lambda s: True, "E1 scuff+halfcut 29": lambda s: ctx[s][0] and ctx[s][1], "E1 other 77": lambda s: not (ctx[s][0] and ctx[s][1]),
                  "E1 halfcut 58": lambda s: ctx[s][1], "E1 full 48": lambda s: not ctx[s][1]},
          "rf": {"rf all": lambda s: True, "rf halfcut 36": lambda s: rfx[s][1], "rf full 70": lambda s: not rfx[s][1], "rf F51": lambda s: s in F51}}
module = lambda s: "_".join(s.split("_")[:2])


def frac(cells, stems):
    return np.sum([cells[s]["pred"] for s in stems], 0) / max(sum(cells[s]["n_keep"] for s in stems), 1)


def bq(fr, q):
    i = np.where(fr >= q)[0]
    return float(G[i[0]]) if len(i) else float(G[-1])


def pooled(cells, bmap):
    t = dict(pred=0, rp=0, rr=0, ng=0, gc=0, gf=0, n20=0, h20=0, fa_px=0, fa_cells=0, neg=0)
    for s, b in bmap.items():
        c = cells[s]; j = int(np.argmin(np.abs(G - b)))
        t["pred"] += c["pred"][j]; t["rp"] += c["relp_tp"][j]; t["rr"] += c["relr_tp"][j]; t["ng"] += c["n_gt"]
        g20 = [x for x in c["gt_cc"] if x[0] >= E.CMIN]; t["gc"] += len(g20); t["gf"] += sum(x[1] + b > 0 for x in g20)
        t["n20"] += c["pc20_n"][j]; t["h20"] += c["pc20_hit"][j]
        if c["n_gt"] == 0:
            t["neg"] += 1; t["fa_px"] += c["pred"][j]; t["fa_cells"] += int(c["s"]["20"] + b > 0)
    P = t["rp"] / max(t["pred"], 1); Rr = t["rr"] / max(t["ng"], 1)
    return {"relR": Rr, "relP": P, "relF1": 2 * P * Rr / max(P + Rr, 1e-9), "compR": t["gf"] / max(t["gc"], 1), "compP": t["h20"] / max(t["n20"], 1),
            "fa_px_per_negcell": t["fa_px"] / max(t["neg"], 1), "fa_cell_rate": t["fa_cells"] / max(t["neg"], 1)}


def members(t):
    fs = sorted(R.glob(f"{t}_m*.val.json"))
    return [f.name.split(".")[0] for f in fs] if (fs and t != "FINAL") else [t]


res = []
for t in a.targets:
    for m in members(t):
        if not (R / f"{m}.val.json").exists():
            continue
        V = json.load(open(R / f"{m}.val.json"))["cells"]
        cv = E.curves(V); op = E.choose_op(cv, "relR", "relP"); bop = op["b"]
        fv = frac(V, list(V)); f_val = fv[op["j"]]; bq_val = bq(fv, 1e-4)
        RF = json.load(open(R / f"{m}.rf.json"))["cells"] if (R / f"{m}.rf.json").exists() else None
        b_half = None
        if RF:
            hs = [s for s in RF if rfx[s][1]]
            ch = E.curves(RF, hs); F = 2 * ch["relP"] * ch["relR"] / np.maximum(ch["relP"] + ch["relR"], 1e-9)
            b_half = float(G[int(np.nanargmax(F))])
        for sp in ("rf", "ext"):
            p = R / f"{m}.{sp}.json"
            if not p.exists():
                continue
            C = json.load(open(p))["cells"]
            mods = {}
            for s in C:
                mods.setdefault(module(s), []).append(s)
            b1, b2 = {}, {}
            for M, ss in mods.items():
                fr = frac(C, ss)
                for s in ss:
                    b1[s] = bq(fr, f_val)
                    b2[s] = float(np.clip(bop + (bq(fr, 1e-4) - bq_val), G[0], G[-1]))
            schemes = {"A0 global b_OP": {s: bop for s in C}, "A1 module quantile": b1, "A2 module tail shift": b2}
            if b_half is not None:
                schemes["A3 halfcut routing"] = {s: (b_half if half(s, sp) else bop) for s in C}
            for sn, fn in STRATA[sp].items():
                st = [s for s in C if fn(s)]
                for k, bm in schemes.items():
                    r = pooled(C, {s: bm[s] for s in st})
                    res.append({"target": t, "member": m, "set": sp, "stratum": sn, "scheme": k, "b_OP": bop, "b_half": b_half, "f_val": float(f_val),
                                "n_modules": len({module(s) for s in st}), "b_mean": float(np.mean([bm[s] for s in st])), **r})
json.dump(res, open(Path(a.out) / "idea1_adapt.json", "w"), indent=0)
L = ["idea 1 label-free adaptation (calib). rf = selection set (Hanifi labels, noisy crack); E1 = DESCRIPTIVE. mean (sd) over members.", ""]
for t in a.targets:
    for sp in ("rf", "ext"):
        for sn in STRATA[sp]:
            for k in ("A0 global b_OP", "A1 module quantile", "A2 module tail shift", "A3 halfcut routing"):
                rs = [r for r in res if r["target"] == t and r["stratum"] == sn and r["scheme"] == k]
                if not rs:
                    continue
                f = lambda key: f"{np.mean([r[key] for r in rs]):.3f}" + (f" ({np.std([r[key] for r in rs], ddof=1):.3f})" if len(rs) > 1 else "")
                L.append(f"{t} {sn} | {k}: relR {f('relR')} relP {f('relP')} relF1 {f('relF1')} compR {f('compR')} compP {f('compP')} "
                         f"FA px/neg cell {f('fa_px_per_negcell')} FA cell rate {f('fa_cell_rate')} mean b {f('b_mean')} (modules {rs[0]['n_modules']})")
            L.append("")
(Path(a.out) / "idea1_adapt.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))
