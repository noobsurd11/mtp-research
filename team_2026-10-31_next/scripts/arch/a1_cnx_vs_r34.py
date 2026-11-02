"""arch A1 side check (DESCRIPTIVE, cross-protocol, not pre-registered): ConvNeXt-T-PF 4k screen runs (A8 DINOv3 / A8c IN-1k,
el_f8, seeds 0-1) vs R34 SUP100-PF 20k (PF2 seeds 5-9) and HC s5-9, from EXISTING val + _rf records only (no test, no E1).
Confounds (stated before computing): 4k vs 20k steps; PF freeze 200/ramp 200 vs 1,000; el_f8 vs el_f3 code (house identity
IDENTICAL per review_f8_wrapper); 2 vs 5 seeds; CPU dumps both. Readouts: pooled crack IoU, relR@2 / relP@2 / relF1@2 at b 0
and at each run's val b_rel (calib rule), crack px on crack-free cells; sets val, F51, H36."""
import sys, json
from pathlib import Path
T = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(T / "scripts/arch"))
import a6_gate as G
import numpy as np
A8 = T / "results/a8/raw/rec"
ARMS = {
  "A8 DINOv3 CNX-T-PF 4k s0-1": [(A8 / f"f8_A8_4k_s{k}.val.json", A8 / f"f8_A8_4k_s{k}.rf.json") for k in (0, 1)],
  "A8c IN-1k CNX-T-PF 4k s0-1": [(A8 / f"f8_A8c_4k_s{k}.val.json", A8 / f"f8_A8c_4k_s{k}.rf.json") for k in (0, 1)],
  "SUPPF R34 20k s5-9": [(G.REC_HC / f"pf2_SUPPF_100pct_s{k}.val.json", G.REC_HC / f"pf2_SUPPF_100pct_s{k}.rf.json") for k in range(5, 10)],
  "HC R34 20k s5-9": [(G.REC_HC / f"hc_HC_100pct_s{k}.val.json", G.REC_HC / f"hc_HC_100pct_s{k}.rf.json") for k in range(5, 10)],
}
out = []
for arm, runs in ARMS.items():
    acc = {}
    for vp, rp in runs:
        assert vp.name.endswith(".val.json") and rp.name.endswith(".rf.json")
        dv, gv = G.load(vp); cv = dv["cells"]; vst = sorted(cv)
        ib, reach = G.choose_brel(cv, vst, gv); i0 = int(np.argmin(np.abs(gv)))
        dr, gr = G.load(rp); cr = dr["cells"]
        sets = {"val": (cv, vst), "F51": (cr, sorted(s for s in cr if G.RFSET.get(s) == "F51")), "H36": (cr, sorted(s for s in cr if G.RFSET.get(s) == "H36"))}
        for sn, (cells, st) in sets.items():
            for lab, i in (("b0", i0), ("brel", ib)):
                acc.setdefault((sn, lab), []).append(G.metrics_at(cells, st, i))
        acc.setdefault(("b_rel", ""), []).append(float(gv[ib]) if reach else float("nan"))
    out.append(f"## {arm}: b_rel {acc[('b_rel','')]}")
    for (sn, lab), M in acc.items():
        if sn == "b_rel":
            continue
        m = lambda k: G.mean([x[k] for x in M])
        out.append(f"  [{sn:3s} {lab:4s}] IoU {m('iou'):.4f} relR {m('relR'):.4f} relP {m('relP'):.4f} relF1 {m('relF'):.4f} pred/GT {m('pred_gt'):.3f} FApx {m('fa_px'):.1f}")
open(T / "ideas/arch_out/a1_cnx_vs_r34.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
