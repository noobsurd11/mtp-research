"""judge hc_test_inact (2 Nov 2026): test inactive IoU HC vs SUPPF (descriptive robustness of the rule-1 n.d. -0.023):
seed-pooled paired module-cluster bootstrap (module = first two stem tokens; 2,000, seed 0), leave-top-3-inactive-cells-out,
per inactive cell IoU per arm, per-seed sign. Own code on m0 JSONs. Usage: python hc_test_inact.py PF2_M0 HC_M0"""
import json, math, sys
import numpy as np
PM, HM = sys.argv[1], sys.argv[2]; S = range(5, 10); IN = 11
L = lambda d, p, a, k: json.load(open(f'{d}/{p}_{a}_100pct_s{k}.json'))['cells']['test']
A = {'SUPPF': [L(PM, 'pf2', 'SUPPF', k) for k in S], 'HC': [L(HM, 'hc', 'HC', k) for k in S]}
st = sorted(A['SUPPF'][0]); assert all(sorted(r) == st for v in A.values() for r in v)
def tfn(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); m = m.reshape(n, n)[:24, :24]
    return np.array([m[IN, IN], m[:, IN].sum() - m[IN, IN], m[IN].sum() - m[IN, IN]], float)
X = {a: np.stack([[tfn(r[s]) for s in st] for r in v]) for a, v in A.items()}  # seeds x cells x 3
iou = lambda t: t[..., 0] / np.maximum(t.sum(-1), 1)
per_seed = {a: iou(X[a].sum(1)) for a in X}
print('per-seed test inactive IoU', {a: np.round(v, 4).tolist() for a, v in per_seed.items()}, 'd mean', round(per_seed['HC'].mean() - per_seed['SUPPF'].mean(), 4))
C = {a: X[a].sum(0) for a in X}  # seed-pooled per cell
gt = C['SUPPF'][:, 0] + C['SUPPF'][:, 2]
mods = sorted({'_'.join(s.split('_')[:2]) for s in st}); mi = np.array([mods.index('_'.join(s.split('_')[:2])) for s in st])
M = {a: np.stack([C[a][mi == j].sum(0) for j in range(len(mods))]) for a in C}
d0 = iou(M['HC'].sum(0)) - iou(M['SUPPF'].sum(0))
rng = np.random.default_rng(0); bs = []
for _ in range(2000):
    w = np.bincount(rng.integers(0, len(mods), len(mods)), minlength=len(mods)).astype(float)
    bs.append(iou(w @ M['HC']) - iou(w @ M['SUPPF']))
bs = np.array(bs)
print(f'seed-pooled d {d0:+.4f}; module bootstrap ({len(mods)} modules) 95% [{np.percentile(bs, 2.5):+.4f}, {np.percentile(bs, 97.5):+.4f}] P(d*<0) {np.mean(bs < 0):.3f}')
idx = np.argsort(-gt)[:3]; keep = np.ones(len(st), bool); keep[idx] = False
print('top-3 inactive cells', [st[i] for i in idx], 'px share', round(gt[idx].sum() / gt.sum(), 3),
      '| leave-top-3-out d', round(iou(C['HC'][keep].sum(0)) - iou(C['SUPPF'][keep].sum(0)), 4))
for i in np.argsort(-gt):
    if gt[i] == 0: break
    print(f'  {st[i]:22s} GT inact px/seed {gt[i] / 5:8.0f} | IoU SUPPF {iou(C["SUPPF"][i]):.3f} HC {iou(C["HC"][i]):.3f} d {iou(C["HC"][i]) - iou(C["SUPPF"][i]):+.3f}')
