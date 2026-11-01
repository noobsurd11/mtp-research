#!/usr/bin/env python3
"""judge (1 Nov): THIN-B3 adversarial readouts (descriptive; never a verdict). Own code on opening files.
1. SKR test crack IoU: the 7 D6 twin cells vs the other 43 (IoU, pixel P / R, pred/GT volume), rule-1 arithmetic on each subset,
   paired image bootstrap of the all-50 delta (5-seed pooled counts), leave-top-3-cells-out by |contribution|.
2. E1 component recall, any-hit (>= 1 GT px within 2 px of a prediction) vs >= 50% (the protocol's), GT comps >= 20 px:
   separates detection from coverage (width).
3. Matched TEST precision (descriptive, test-oracle, chooses nothing): max test relR@2 s.t. test relP@2 >= 0.90 per run on the
   B5 records grid; and test relR@2 at a common b.
Usage: thin_skr_check.py THIN_RAW PF2_RAW"""
import json, math, sys, numpy as np
T, P = sys.argv[1], sys.argv[2]
TW = ['CFVS_00006_r5_c5', 'CFVS_00033_r8_c4', 'CFVS_00035_r8_c4', 'CFVS_00042_r8_c4', 'CFVS_00018_r4_c4', 'CFVS_00027_r4_c4', 'ARTS_00020_r5_c1']
S = range(5, 10)
def m0(arm, k):
    d, p = (P, 'pf2') if arm == 'SUPPF' else (T, 'thin'); return json.load(open(f'{d}/m0/{p}_{arm}_100pct_s{k}.json'))['cells']
def cc(c):
    m = np.asarray(c['conf'], np.int64); n = int(math.isqrt(m.size)); m = m.reshape(n, n)[:24, :24]
    return np.array([m[14, 14], m[:, 14].sum() - m[14, 14], m[14].sum() - m[14, 14]], float)  # tp fp fn
A = {a: [m0(a, k) for k in S] for a in ('SUPPF', 'SKR', 'CLD')}
stems = sorted(A['SUPPF'][0]['test'])
X = {a: np.array([[cc(r['test'][s]) for s in stems] for r in A[a]]) for a in A}  # seeds x cells x 3
iou = lambda Z: Z[..., 0].sum(-1) / Z.sum(-1).sum(-1) if Z.ndim == 3 else None
def sub(a, keep):
    Z = X[a][:, keep, :]; t, f, n = Z[..., 0].sum(1), Z[..., 1].sum(1), Z[..., 2].sum(1)
    return t / (t + f + n), t / (t + f), t / (t + n), (t + f) / (t + n)
print('## 1. SKR test crack IoU by subset (5 seeds; per-seed pooled)')
for lab, keep in (('all 50', np.ones(len(stems), bool)), ('7 D6 twins', np.isin(stems, TW)), ('43 others', ~np.isin(stems, TW))):
    for a in ('SKR', 'CLD'):
        i0, p0, r0, v0 = sub('SUPPF', keep); i1, p1, r1, v1 = sub(a, keep)
        d = i1.mean() - i0.mean(); thr = max(0.01, 2 * math.sqrt((i0.var(ddof=1) + i1.var(ddof=1)) / 3))
        print(f'  {lab:10s} {a}: IoU {i0.mean():.4f} -> {i1.mean():.4f} ({d:+.4f}, thr {thr:.4f}) | P {p0.mean():.3f} -> {p1.mean():.3f} | R {r0.mean():.3f} -> {r1.mean():.3f} | pred/GT {v0.mean():.2f} -> {v1.mean():.2f} | GT px {int(X["SUPPF"][0, keep, 0].sum() + X["SUPPF"][0, keep, 2].sum())}')
# paired image bootstrap on the all-50 SKR delta, + leave-top-3-out
XA, XB = X['SUPPF'].sum(0), X['SKR'].sum(0)  # seeds pooled counts per cell
f = lambda Z: Z[:, 0].sum() / Z.sum()
full = f(XB) - f(XA); rng = np.random.default_rng(0); bs = []
for _ in range(2000):
    ix = rng.integers(0, len(stems), len(stems)); bs.append(f(XB[ix]) - f(XA[ix]))
lo, hi = np.percentile(bs, [2.5, 97.5])
contrib = [(full - (f(np.delete(XB, i, 0)) - f(np.delete(XA, i, 0))), stems[i]) for i in range(len(stems))]
top = sorted(contrib, key=lambda x: -abs(x[0]))[:3]; keep = [i for i in range(len(stems)) if stems[i] not in [t[1] for t in top]]
print(f'  SKR - SUPPF crack IoU (seed-pooled counts): {full:+.4f}, paired image bootstrap [{lo:+.4f}, {hi:+.4f}], P<0 {np.mean(np.array(bs) < 0):.2f}; '
      f'leave-top-3-out {f(XB[keep]) - f(XA[keep]):+.4f} (top: ' + ', '.join(f'{s} {c:+.4f}' for c, s in top) + ')')
print('\n## 2. E1 component recall (GT comps >= 20 px): >= 50% covered (protocol) vs any-hit (>= 1 px within 2 px)')
for a in ('SUPPF', 'SKR', 'CLD'):
    r50, rany = [], []
    for r in A[a]:
        g = [x for c in r['ext'].values() for x in c['crack_cc']['gt'] if x[0] >= 20]
        r50.append(np.mean([x[1] >= math.ceil(0.5 * x[0]) for x in g])); rany.append(np.mean([x[1] >= 1 for x in g]))
    print(f'  {a:6s} compR50 {np.mean(r50):.4f} | any-hit {np.mean(rany):.4f} | n GT comps {len(g)}')
print('\n## 3. Matched TEST precision (descriptive, test-oracle, chooses nothing): max test relR@2 with test relP@2 >= 0.90 per run')
for a in ('SUPPF', 'SKR', 'CLD', 'B3'):
    d, p = (P, 'pf2') if a == 'SUPPF' else (T, 'thin'); vals = []
    for k in S:
        cs = list(json.load(open(f'{d}/b5/rec/{p}_{a}_100pct_s{k}.test.json'))['cells'].values())
        Sm = lambda key: np.sum([np.asarray(c[key], float) for c in cs], 0)
        rp, rr = Sm('relp_tp') / np.maximum(Sm('pred'), 1), Sm('relr_tp') / sum(c['n_gt'] for c in cs)
        ok = rp >= 0.90; vals.append(rr[ok].max() if ok.any() else np.nan)
    print(f'  {a:6s} {np.nanmean(vals):.4f} (seeds ' + ' '.join(f'{v:.3f}' for v in vals) + ')')
