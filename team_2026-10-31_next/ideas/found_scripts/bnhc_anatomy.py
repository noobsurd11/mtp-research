"""found, 31 Oct 2026: anatomy of BN-HC routed vs FINAL on E1 (descriptive only; E1 never for selection).
Input: team_2026-10-29_features/d_checks/d_cells.json (per-cell 24x24 confusions, rel2 counts, p(crack) bands).
CPU, read-only. Usage: python bnhc_anatomy.py
"""
import json
from pathlib import Path
import numpy as np

R = Path("/home/yugma/mtp/research/team_2026-10-29_features")
d = json.load(open(R / "d_checks/d_cells.json"))
ctx = {}
for l in open(R / "scripts/e1_context.tsv"):
    if l.strip():
        r = l.rstrip("\n").split("\t"); ctx[r[0]] = {"scuff": r[2] == "scuff=1", "halfcut": r[3] == "halfcut=1"}
NC, CR = 24, 14
NAMES = ["background", "sp_multi", "sp_mono", "sp_dogbone", "ribbons", "border", "text", "padding", "clamp", "busbars",
         "crack_rbn_edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead_cell", "corrosion",
         "belt_mark", "edge_dark", "frame_edge", "jbox", "meas_artifact"]
BANDS = [0, 0.001, 0.1, 0.5, 0.95, 1.0]
E = d["ext"]
groups = {"halfcut58": lambda s: ctx[s]["halfcut"], "target29": lambda s: ctx[s]["scuff"] and ctx[s]["halfcut"],
          "hc_noscuff29": lambda s: ctx[s]["halfcut"] and not ctx[s]["scuff"], "full48": lambda s: not ctx[s]["halfcut"]}


def agg(var, b, sel):
    cs = {s: v for s, v in E[var][b].items() if sel(s)}
    C = sum(np.array(v["conf"], np.int64).reshape(NC, NC) for v in cs.values())
    rel = np.sum([v["crack_rel2"] for v in cs.values()], 0)
    bg = np.sum([v["crack_pband_gt"] for v in cs.values()], 0); bn = np.sum([v["crack_pband_neg"] for v in cs.values()], 0)
    return cs, C, rel, bg, bn


for b in ("0.0", "0.75"):
    print(f"\n===== bias {b} =====")
    for gname, sel in groups.items():
        for var in ("FINAL", "BNHC_global"):
            cs, C, rel, bg, bn = agg(var, b, sel)
            tp, fp, fn = C[CR, CR], C[:, CR].sum() - C[CR, CR], C[CR].sum() - C[CR, CR]
            P, Rr = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
            near = rel[0]; far = rel[1] - rel[0]
            crackfree = [s for s, v in cs.items() if np.array(v["conf"]).reshape(NC, NC)[CR].sum() == 0]
            fp_cf = sum(np.array(cs[s]["conf"]).reshape(NC, NC)[:, CR].sum() for s in crackfree)
            print(f"{gname:13s} {var:12s} n={len(cs):3d} gt={tp+fn:6d} tp={tp:6d} fp={fp:6d} P={P:.3f} R={Rr:.3f} IoU={tp/max(tp+fp+fn,1):.3f} "
                  f"relP2={rel[0]/max(rel[1],1):.3f} relR2={rel[2]/max(rel[3],1):.3f} pred_far>2px={far:6d} crackfree_cells={len(crackfree)} fp_on_crackfree={fp_cf}")
            if gname == "halfcut58":
                col = C[:, CR].astype(int); top = np.argsort(-col)[:6]
                print("    pred-crack px by GT class:", ", ".join(f"{NAMES[i]} {col[i]}" for i in top))
                # p(crack) band shares
                print("    GT crack px by p(crack) band", [f"{x:.3f}" for x in bg / max(bg.sum(), 1)], " neg px >=0.5:", int(bn[3] + bn[4]))
                # coarse PR at band thresholds (only meaningful at bias 0: pc = raw p)
                for i, t in ((2, 0.1), (3, 0.5), (4, 0.95)):
                    tpt = bg[i:].sum(); fpt = bn[i:].sum()
                    print(f"    p>={t}: P={tpt/max(tpt+fpt,1):.3f} R={tpt/max(bg.sum(),1):.3f} (tp {tpt}, fp {fpt})")
    # per-cell concentration of extra FP on half-cut cells (BN-HC routed = BN-HC global on half-cut cells)
    F = E["FINAL"][b]; G = E["BNHC_global"][b]
    dfp = {}
    for s in F:
        if ctx[s]["halfcut"]:
            cf, cg = np.array(F[s]["conf"]).reshape(NC, NC), np.array(G[s]["conf"]).reshape(NC, NC)
            dfp[s] = (cg[:, CR].sum() - cg[CR, CR]) - (cf[:, CR].sum() - cf[CR, CR])
    v = np.array(sorted(dfp.values(), reverse=True)); tot = v.sum()
    print(f"  extra FP on 58 half-cut cells: total {tot}, top-5 cells share {v[:5].sum()/tot:.2f}, cells with more FP {int((v>0).sum())}, fewer {int((v<0).sum())}")
    print("  top cells:", sorted(dfp.items(), key=lambda kv: -kv[1])[:5])
