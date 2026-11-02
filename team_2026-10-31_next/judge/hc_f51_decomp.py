"""judge hc_f51_decomp (2 Nov 2026): F51 crack AP (1,000-bin, rf keep) decomposed: all 51 cells vs the 12 crack cells only vs
crack cells + the 34 crack-free cells swapped between arms (negatives from the other arm), per arm seed mean. Own code on the
HC opening's rf dumps. Usage: python hc_f51_decomp.py DUMP_DIR RF_DIR RF_SETS"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
D, RF, SETS = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
rows = [l.rstrip("\n").split("\t") for l in open(SETS) if l.strip()][1:]
SET = {r[0]: r[1] for r in rows}
ARMS = {"SUPPF": [f"pf2_SUPPF_100pct_s{k}" for k in range(5, 10)], "HC": [f"hc_HC_100pct_s{k}" for k in range(5, 10)]}
def ap(pos, neg):
    tp = np.cumsum(pos[::-1]).astype(float); fp = np.cumsum(neg[::-1]).astype(float)
    pr = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    return float(np.sum(pr * np.diff(np.concatenate([[0.0], tp / pos.sum()]))))
GT = {}; H = {}
for arm, runs in ARMS.items():
    for r in runs:
        z = np.load(D / f"{r}.rf.npz"); st = [str(s) for s in z["stems"]]; H[r] = {}
        for i, s in enumerate(st):
            if SET[s] != "F51": continue
            if s not in GT:
                GT[s] = (np.array(Image.open(RF / "masks" / f"{s}.png")), ~(np.array(Image.open(RF / "ignore" / f"{s}.png")) > 0))
            g, k = GT[s]; t = (g == 14) & k
            b = np.clip((z["pc"][i].astype(np.float32) * 1000).astype(int), 0, 999)
            H[r][s] = (np.bincount(b[t], minlength=1000), np.bincount(b[k & ~t], minlength=1000), int(t.sum()))
F51 = sorted(H[ARMS["HC"][0]]); crack = [s for s in F51 if H[ARMS["HC"][0]][s][2] >= 20]; free = [s for s in F51 if H[ARMS["HC"][0]][s][2] == 0]
amb = [s for s in F51 if 0 < H[ARMS["HC"][0]][s][2] < 20]
P = lambda r, S: np.sum([H[r][s][0] for s in S], 0); N = lambda r, S: np.sum([H[r][s][1] for s in S], 0)
print(f"F51 {len(F51)} cells: crack {len(crack)}, ambiguous {len(amb)}, crack-free {len(free)}")
for lab, f in (("all 51", lambda r, o: ap(P(r, F51), N(r, F51))),
               ("12 crack cells only", lambda r, o: ap(P(r, crack), N(r, crack))),
               ("crack+amb cells with the OTHER arm's crack-free negatives", lambda r, o: ap(P(r, crack + amb), N(r, crack + amb) + N(o, free)))):
    v = {}
    for arm, runs in ARMS.items():
        other = ARMS["HC" if arm == "SUPPF" else "SUPPF"]
        v[arm] = np.mean([f(r, o) for r, o in zip(runs, other)])
    print(f"{lab}: SUPPF {v['SUPPF']:.4f} HC {v['HC']:.4f} d {v['HC'] - v['SUPPF']:+.4f}")
neg_hi = {arm: np.mean([N(r, free)[900:].sum() for r in runs]) for arm, runs in ARMS.items()}
print(f"crack-free F51 px with p(crack) >= 0.9 (seed mean): SUPPF {neg_hi['SUPPF']:.0f} HC {neg_hi['HC']:.0f}")
