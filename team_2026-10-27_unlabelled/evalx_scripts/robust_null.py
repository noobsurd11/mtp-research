"""evalx Q1b: is the P16 crack null robust to (a) dropping twins too, (b) keeping all 50 cells but using the seed
median, (c) combining seed and cell noise in one interval?"""
import numpy as np
from common import load, pooled, subset
rng = np.random.default_rng(0)
for a, b in [('A100', 'Sx100'), ('A50', 'S50'), ('A20', 'S20')]:
    ca, XA, _ = load(a); cb, XB, _ = load(b)
    for s in ['all', 'clean', 'clean_notwin']:
        idx = subset(ca, s)
        for m in ['crack_iou', 'relF1', 'crack_rec', 'inact_iou']:
            pa, pb = pooled(XA, idx)[m], pooled(XB, idx)[m]
            d = pb.mean() - pa.mean(); dmed = np.median(pb) - np.median(pa)
            se = np.sqrt(pa.var(ddof=1) / len(pa) + pb.var(ddof=1) / len(pb))
            B = idx[rng.integers(0, len(idx), size=(2000, len(idx)))]
            bd = np.array([pooled(XB, i)[m].mean() - pooled(XA, i)[m].mean() for i in B])
            tot = np.sqrt(se**2 + bd.var())
            print(f'{b}-{a} {s:13s} {m:9s} n={len(idx)} d_mean {d:+.4f} d_median {dmed:+.4f} '
                  f'cellCI [{np.percentile(bd, 2.5):+.4f},{np.percentile(bd, 97.5):+.4f}] seed+cell 95% [{d - 1.96 * tot:+.4f},{d + 1.96 * tot:+.4f}]')
