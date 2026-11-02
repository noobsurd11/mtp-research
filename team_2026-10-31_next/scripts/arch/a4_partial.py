"""arch A4 premise (DESCRIPTIVE; val + _rf records only): are GT crack components (>= 20 px) missed whole, or found in
fragments? From el_metrics gt_cc = [size, v50, vany]: found50 at b iff v50 + b > 0; any-hit iff vany + b > 0.
partial = any-hit and not found50. At b 0 and each run's val b_rel (a6_gate rule). Seed means. Size-weighted share also."""
import sys, json
from pathlib import Path
import numpy as np
T = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(T / "scripts/arch")); import a6_gate as G
ARMS = {
  "SUPPF s5-9": [(G.REC_HC / f"pf2_SUPPF_100pct_s{k}.val.json", G.REC_HC / f"pf2_SUPPF_100pct_s{k}.rf.json") for k in range(5, 10)],
  "HC s5-9": [(G.REC_HC / f"hc_HC_100pct_s{k}.val.json", G.REC_HC / f"hc_HC_100pct_s{k}.rf.json") for k in range(5, 10)],
  "SKR w1 s5-9": [(G.REC_THIN / f"thin_SKR_100pct_s{k}.val.json", None) for k in range(5, 10)],
  "CLD s5-9": [(G.REC_THIN / f"thin_CLD_100pct_s{k}.val.json", None) for k in range(5, 10)],
}
out = []
for arm, runs in ARMS.items():
    acc = {}
    for vp, rp in runs:
        dv, gv = G.load(vp); cv = dv["cells"]; ib, _ = G.choose_brel(cv, sorted(cv), gv); bb = float(gv[ib])
        sets = {"val": [cv[s] for s in cv]}
        if rp:
            dr, _ = G.load(rp); sets["F51"] = [dr["cells"][s] for s in dr["cells"] if G.RFSET.get(s) == "F51"]
        for sn, cells in sets.items():
            cc = [x for c in cells for x in c["gt_cc"] if x[0] >= 20]
            for lab, b in (("b0", 0.0), ("brel", bb)):
                n = len(cc); f50 = sum(1 for x in cc if x[1] + b > 0); anyh = sum(1 for x in cc if x[2] + b > 0)
                px = sum(x[0] for x in cc); ppx = sum(x[0] for x in cc if x[2] + b > 0 and not x[1] + b > 0)
                mpx = sum(x[0] for x in cc if not x[2] + b > 0)
                acc.setdefault((sn, lab), []).append((n, f50 / n, anyh / n, (anyh - f50) / n, ppx / px, mpx / px))
    out.append(f"## {arm}")
    for (sn, lab), v in acc.items():
        m = lambda j: sum(x[j] for x in v) / len(v)
        out.append(f"  [{sn:3s} {lab:4s}] comps {v[0][0]} | found>=50% {m(1):.3f} any-hit {m(2):.3f} partial {m(3):.3f} | GT px share in partial comps {m(4):.3f}, in missed comps {m(5):.3f}")
open(T / "ideas/arch_out/a4_partial.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
