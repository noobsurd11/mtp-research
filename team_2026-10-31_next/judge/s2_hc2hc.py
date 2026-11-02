#!/usr/bin/env python3
"""judge s2_hc2hc (2 Nov 2026): how strongly does HC2 vs HC speak to 'label cause'? Test inactive IoU, seed-aware two-stage bootstrap
(48 modules + 5 seeds per arm with replacement; shared module draw; 4,000; rng 7): P(HC2 - HC >= full recovery (SUPPF - HC point, +0.0228)),
P(HC2 - HC >= half recovery), and the same for all 50 / clean 49. Also HC-family (HC + HC2, 10 seeds) vs SUPPF (descriptive, post hoc pool).
Usage: s2_hc2hc.py PF2_M0 HC_M0 HC2_M0"""
import json, math, sys
import numpy as np
P, H, H2 = sys.argv[1:4]
L = lambda d, p: [json.load(open(f'{d}/{p}_100pct_s{k}.json'))['cells']['test'] for k in range(5, 10)]
A = {'SUPPF': L(P, 'pf2_SUPPF'), 'HC': L(H, 'hc_HC'), 'HC2': L(H2, 'hc2_HCig')}
st = sorted(A['SUPPF'][0])
def t(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); m = m.reshape(n, n)[:24, :24]
    return np.array([m[11, 11], m[:, 11].sum() - m[11, 11], m[11].sum() - m[11, 11]], float)
iou = lambda x: x[..., 0] / np.maximum(x.sum(-1), 1)
for lab, keep in (('all 50', [True] * 50), ('clean 49', [s != 'CSIR_00070_r8_c4' for s in st])):
    S = [s for s, k in zip(st, keep) if k]
    mods = sorted({'_'.join(s.split('_')[:2]) for s in S}); mi = np.array([mods.index('_'.join(s.split('_')[:2])) for s in S])
    X = {a: np.stack([np.stack([np.stack([t(r[s]) for s in S])[mi == j].sum(0) for j in range(len(mods))]) for r in v]) for a, v in A.items()}  # seeds x mods x 3
    pt = {a: iou(X[a].sum(1)).mean() for a in X}; full = pt['SUPPF'] - pt['HC']
    rng = np.random.default_rng(7); nb = 4000; d = np.empty(nb); dfam = np.empty(nb)
    for b in range(nb):
        w = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)).astype(float)
        v = {}
        for a in X:
            sd = rng.integers(0, 5, 5); v[a] = iou(np.einsum('m,smk->sk', w, X[a][sd]))
        d[b] = v['HC2'].mean() - v['HC'].mean()
        fam = np.concatenate([v['HC'], v['HC2']]); sd2 = rng.integers(0, 10, 10)
        dfam[b] = fam[sd2].mean() - v['SUPPF'].mean()
    fam_pt = np.concatenate([iou(X['HC'].sum(1)), iou(X['HC2'].sum(1))]).mean() - pt['SUPPF']
    print(f'{lab}: point HC2-HC {pt["HC2"] - pt["HC"]:+.4f}; full recovery would be {full:+.4f} | seed-aware HC2-HC [{np.percentile(d, 2.5):+.4f}, {np.percentile(d, 97.5):+.4f}] '
          f'P(>= full) {np.mean(d >= full):.3f} P(>= half) {np.mean(d >= full / 2):.3f} P(> 0) {np.mean(d > 0):.3f} | HC-family (10 seeds) - SUPPF {fam_pt:+.4f} '
          f'[{np.percentile(dfam, 2.5):+.4f}, {np.percentile(dfam, 97.5):+.4f}] P(<0) {np.mean(dfam < 0):.3f} (post hoc pool, descriptive)')
