"""judge arch_a3_check (2 Nov 2026): crack FP px by GT class on Hanifi H36 / F51 at b 0 and at each run's val b_rel (own OP from the
val records), SUPPF s5-9 vs HC s5-9, from the HC opening's rf dumps (margin) + rf masks / ignore. Own code. Usage: python arch_a3_check.py"""
import json
from collections import Counter
import numpy as np
from PIL import Image
D = "/home/noob/work/el_hc/reports/hc/syn_work"; RF = "/home/noob/work/calib/data/rf"
SET = {l.split("\t")[0]: l.split("\t")[1] for l in list(open("/home/noob/work/found/t9/rf_sets.tsv"))[1:]}
def op(cells, grid):
    S = lambda k: np.sum([np.asarray(c[k]) for c in cells.values()], 0)
    pred, rp, rr = S("pred"), S("relp_tp"), S("relr_tp"); ng = sum(c["n_gt"] for c in cells.values()); g = np.asarray(grid)
    cand = np.where((g >= -4 - 1e-9) & (g <= 12 + 1e-9) & (np.abs(np.round(g * 10) - g * 10) < 1e-6))[0]
    P = np.where(pred > 0, rp / np.maximum(pred, 1), -1.0); ok = cand[P[cand] >= 0.90]
    return float(g[ok[np.argmax(rr[ok] / ng)]]) if len(ok) else float(g[cand[np.argmax(P[cand])]])
GT = {}
for arm, pre in (("SUPPF", "pf2_SUPPF"), ("HC", "hc_HC")):
    acc = {}
    for k in range(5, 10):
        r = f"{pre}_100pct_s{k}"; v = json.load(open(f"{D}/rec/{r}.val.json")); brel = op(v["cells"], v["grid"])
        z = np.load(f"{D}/dump/{r}.rf.npz"); st = [str(s) for s in z["stems"]]
        for i, s in enumerate(st):
            if SET[s] not in ("H36", "F51"): continue
            if s not in GT:
                GT[s] = (np.array(Image.open(f"{RF}/masks/{s}.png")), ~(np.array(Image.open(f"{RF}/ignore/{s}.png")) > 0))
            g, kp = GT[s]; m = z["margin"][i].astype(np.float32)
            for lab, b in (("b0", 0.0), ("brel", brel)):
                fp = (m + b > 0) & kp & (g != 14)
                acc.setdefault((SET[s], lab), Counter()).update(Counter(g[fp].tolist()))
    for (st, lab), c in sorted(acc.items()):
        tot = sum(c.values()) / 5
        print(f"{arm:5s} {st} {lab:4s} FP px/run {tot:7.1f} | class 1 {c[1] / 5:6.1f} | class 2 {c[2] / 5:6.1f} | top " +
              ", ".join(f"{k}:{v / 5:.0f}" for k, v in c.most_common(6)))
