"""calib idea 1 (diagnostic; E1 descriptive only, never selection): is E1's crack failure calibration or features?
Reads el_metrics per-cell records (bias sweep b = -4..+12) for FINAL (ensemble, b_dep +0.75) and per-seed arms (b_dep 0).
Reports per set / E1 stratum:
  - curves vs b (pixel R/P, relR@2/relP@2, component R/P);
  - at the deployed b and at the val-chosen OP-rel b;
  - E1 ORACLE global b (best relF1 on E1 itself) and per-module oracle b: upper bounds on any threshold adaptation (diagnostic);
  - "invisible" share: 1 - relR@2 at b = +12 (GT crack px with no px within 2 px reaching margin > -12, i.e. p_c < ~6e-6 * max other).
Usage: python idea1_analysis.py --rec DIR --ctx e1_context.tsv --rfctx rf_context.tsv --out OUTDIR [--figs FIGDIR]
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
ap.add_argument("--figs")
ap.add_argument("--targets", nargs="+", default=["FINAL", "SUPPF5", "SUP5"])
a = ap.parse_args()
R = Path(a.rec); OUT = Path(a.out); OUT.mkdir(parents=True, exist_ok=True)
G = E.GRID
J = lambda b: int(np.argmin(np.abs(G - b)))

ctx = {}
for l in open(a.ctx):
    f = l.rstrip("\n").split("\t")
    if len(f) >= 4:
        ctx[f[0]] = (f[2] == "scuff=1", f[3] == "halfcut=1")
rfx = {}
for i, l in enumerate(open(a.rfctx)):
    f = l.rstrip("\n").split("\t")
    if i:
        rfx[f[0]] = (f[6] == "1", f[5] == "1")
F51 = {l.strip() for l in open(a.f51) if l.strip()}
STRATA = {
    "ext": {"E1 all 106": lambda s: True, "E1 scuff+halfcut 29": lambda s: ctx[s][0] and ctx[s][1],
            "E1 other 77": lambda s: not (ctx[s][0] and ctx[s][1]), "E1 halfcut no-scuff 29": lambda s: ctx[s][1] and not ctx[s][0],
            "E1 halfcut all 58": lambda s: ctx[s][1], "E1 full 48": lambda s: not ctx[s][1]},
    "rf": {"rf all 106": lambda s: True, "rf halfcut 36": lambda s: rfx[s][1], "rf full 70": lambda s: not rfx[s][1], "rf F51": lambda s: s in F51},
    "val": {"val 54": lambda s: True},
}


def members(t):
    fs = sorted(R.glob(f"{t}_m*.val.json"))
    return [f.name.split(".")[0] for f in fs] if (fs and t != "FINAL") else [t]


def load(t, s):
    p = R / f"{t}.{s}.json"
    return json.load(open(p)) if p.exists() else None


def f1(p, r):
    return np.where((p + r) > 0, 2 * p * r / np.maximum(p + r, 1e-9), np.nan)


def module(s):
    return "_".join(s.split("_")[:2])


def oracle_module(cells, stems, b0):
    """Per-module oracle b: coordinate ascent on POOLED relF1@2 over per-module b (start: global oracle b0), 4 sweeps.
    Uses the set's own labels: an upper bound on any per-module threshold rule, diagnostic only."""
    mods = {}
    for s in stems:
        mods.setdefault(module(s), []).append(s)
    A = {m: np.array([np.sum([cells[s]["pred"] for s in ss], 0), np.sum([cells[s]["relp_tp"] for s in ss], 0),
                      np.sum([cells[s]["relr_tp"] for s in ss], 0)], float) for m, ss in mods.items()}
    ng = sum(cells[s]["n_gt"] for s in stems)
    ch = {m: J(b0) for m in mods}
    tot = lambda: sum(A[m][:, ch[m]] for m in mods)
    F = lambda t: 2 * (t[1] / max(t[0], 1)) * (t[2] / max(ng, 1)) / max(t[1] / max(t[0], 1) + t[2] / max(ng, 1), 1e-9)
    for _ in range(4):
        for m in mods:
            base = tot() - A[m][:, ch[m]]
            cand = base[:, None] + A[m]
            P = cand[1] / np.maximum(cand[0], 1); Rr = cand[2] / max(ng, 1)
            f = np.where(P + Rr > 0, 2 * P * Rr / np.maximum(P + Rr, 1e-9), 0)
            ch[m] = int(np.argmax(f))
    t = tot(); P, Rr = t[1] / max(t[0], 1), t[2] / max(ng, 1)
    return {"relP": P, "relR": Rr, "relF1": F(t), "n_modules": len(mods)}


rows, curves_out = [], {}
for t in a.targets:
    ms = members(t)
    bdep = 0.75 if t == "FINAL" else 0.0
    for m in ms:
        recv = load(m, "val")
        if recv is None:
            continue
        cv = E.curves(recv["cells"])
        opr, opc = E.choose_op(cv, "relR", "relP"), E.choose_op(cv, "compR", "compP")
        for s in ("val", "ext", "rf"):
            rec = recv if s == "val" else load(m, s)
            if rec is None:
                continue
            for sname, fn in STRATA[s].items():
                st = [x for x in rec["cells"] if fn(x)]
                c = E.curves(rec["cells"], st)
                F = f1(c["relP"], c["relR"])
                jo = int(np.argmax(np.nan_to_num(F, nan=0.0)))
                row = {"target": t, "member": m, "set": s, "stratum": sname, "n": len(st), "gt_px": int(c["gt_px"]), "gt_comp20": c["gt_comp20"],
                       "b_dep": bdep, "b_opr": opr["b"], "b_opc": opc["b"]}
                for lab, j in (("dep", J(bdep)), ("opr", opr["j"]), ("opc", opc["j"]), ("b4", J(4.0)), ("b12", J(12.0))):
                    row.update({f"{k}_{lab}": float(c[k][j]) for k in ("R", "P", "relR", "relP", "compR", "compP")})
                row.update({"oracle_b": float(G[jo]), "oracle_relF1": float(F[jo]), "oracle_relR": float(c["relR"][jo]), "oracle_relP": float(c["relP"][jo]),
                            "relF1_dep": float(F[J(bdep)]), "relF1_opr": float(F[opr["j"]]), "invisible_b12": float(1 - c["relR"][J(12.0)])})
                if s != "val":
                    om = oracle_module(rec["cells"], st, float(G[jo]))
                    row.update({"modoracle_relF1": om["relF1"], "modoracle_relR": om["relR"], "modoracle_relP": om["relP"]})
                rows.append(row)
                curves_out[f"{m}|{sname}"] = {k: np.asarray(c[k], float).tolist() for k in ("R", "P", "relR", "relP", "compR", "compP")}
json.dump({"grid": G.tolist(), "rows": rows, "curves": curves_out}, open(OUT / "idea1_rows.json", "w"))

# --------- text summary: per target, mean (sd) over members
keys = ["n", "gt_px", "relR_dep", "relP_dep", "relF1_dep", "relR_opr", "relP_opr", "relF1_opr", "compR_opc", "compP_opc", "R_dep", "P_dep",
        "oracle_b", "oracle_relF1", "oracle_relR", "oracle_relP", "modoracle_relF1", "modoracle_relR", "modoracle_relP", "relR_b4", "relP_b4", "invisible_b12"]
L = ["idea 1 (calib, diagnostic). E1 and Hanifi rf rows are DESCRIPTIVE; oracle columns use the set's own labels (upper bounds, never selection).",
     "dep = deployed b (FINAL +0.75, single runs 0); opr = val-chosen OP-rel b; opc = val-chosen OP-comp b; b4 = +4; invisible = 1 - relR@2 at b = +12.",
     "values: mean over members (sd) for per-seed arms; FINAL = the 5-model ensemble.", ""]
for t in a.targets:
    for sname in [k for s in ("val", "ext", "rf") for k in STRATA[s]]:
        rs = [r for r in rows if r["target"] == t and r["stratum"] == sname]
        if not rs:
            continue
        parts = []
        for k in keys:
            v = [r[k] for r in rs if k in r]
            if not v:
                continue
            parts.append(f"{k} {np.mean(v):.3f}" + (f" ({np.std(v, ddof=1):.3f})" if len(v) > 1 else "") if k not in ("n", "gt_px") else f"{k} {int(v[0])}")
        L.append(f"{t} [{len(rs)}] {sname}: " + "; ".join(parts))
    L.append("")
(OUT / "idea1_summary.txt").write_text("\n".join(L) + "\n")
print("\n".join(L))

if a.figs:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FG = Path(a.figs); FG.mkdir(parents=True, exist_ok=True)
    col = {"val 54": "#1f77b4", "E1 other 77": "#2ca02c", "E1 scuff+halfcut 29": "#d62728", "rf F51": "#8c564b"}
    for t in a.targets:
        ms = members(t)
        fig, ax = plt.subplots(1, 4, figsize=(17, 3.8))
        for sname, cc in col.items():
            cs = [curves_out.get(f"{m}|{sname}") for m in ms]
            cs = [c for c in cs if c]
            if not cs:
                continue
            for k, axi, ls in (("relR", 0, "-"), ("relP", 0, "--")):
                y = np.nanmean([c[k] for c in cs], 0)
                ax[axi].plot(G, y, ls, color=cc, label=f"{sname} {k}" if axi == 0 else None, lw=1.4)
            rr = np.nanmean([c["relR"] for c in cs], 0); pp = np.nanmean([c["relP"] for c in cs], 0)
            ax[1].plot(rr, pp, color=cc, label=sname, lw=1.4)
            ax[1].plot(rr[J(0.75 if t == "FINAL" else 0)], pp[J(0.75 if t == "FINAL" else 0)], "o", color=cc, ms=4)
            cr = np.nanmean([c["compR"] for c in cs], 0); cp = np.nanmean([c["compP"] for c in cs], 0)
            ax[2].plot(cr, cp, color=cc, label=sname, lw=1.4)
            ax[3].plot(G, np.nanmean([c["R"] for c in cs], 0), ":", color=cc, lw=1.4)
            ax[3].plot(G, rr, "-", color=cc, lw=1.4, label=sname)
            ax[3].plot(G, cr, "-.", color=cc, lw=1.2)
        ax[0].set_xlabel("crack logit bias b (higher = lower threshold)"); ax[0].set_ylabel("relR@2 (solid), relP@2 (dashed)")
        ax[0].axvline(0.75 if t == "FINAL" else 0, color="grey", lw=0.6); ax[0].legend(fontsize=6, ncol=2)
        ax[1].set_xlabel("relR@2"); ax[1].set_ylabel("relP@2"); ax[1].set_title("pixel (2 px) PR over b; dot = deployed b", fontsize=8)
        ax[1].axhline(0.9, color="grey", lw=0.6); ax[1].legend(fontsize=6)
        ax[2].set_xlabel("component recall (>=20 px, 50%)"); ax[2].set_ylabel("component precision (>=20 px)")
        ax[2].axhline(0.9, color="grey", lw=0.6)
        for x in ax[1:3]:
            x.set_xlim(0, 1); x.set_ylim(0, 1)
        ax[3].set_xlabel("crack logit bias b"); ax[3].set_ylabel("recall: pixel (dotted), relR@2 (solid), component (dash-dot)", fontsize=7)
        ax[3].set_ylim(0, 1); ax[3].axvline(0.75 if t == "FINAL" else 0, color="grey", lw=0.6); ax[3].legend(fontsize=6)
        fig.suptitle(f"{t}: val vs E1 strata (E1 descriptive) vs Hanifi _rf; mean over {len(ms)} member(s)", fontsize=9)
        fig.tight_layout(); fig.savefig(FG / f"idea1_{t}.png", dpi=90); plt.close(fig)
