#!/usr/bin/env python3
"""judge hc_width_check (2 Nov 2026): HC E1 / test readouts that the co-primaries do not show (descriptive; never a verdict).
Own code on opening m0 JSONs (argmax, final weights). E1 crack GT is ~1.5x wider than train (3.66 vs 2.41 px area/skeleton), so
pixel recall / IoU on E1 reward fatter predictions: read relF1@2 and any-hit component recall first.
Per arm (5 seeds, mean +- sd; rule-1 threshold shown):
  E1 106 and strata (29 scuff+half-cut / 29 half-cut no scuff / 48 full): relF1@2, relP@2, relR@2, crack IoU, pixel P / R, pred/GT px,
  any-hit comp recall (GT comps >= 20 px with >= 1 px within 2 px of a prediction), >= 50% comp recall, crack px on crack-free cells,
  inactive IoU (pooled conf);
  test 50: pred/GT px, relP@2, crack px on crack-free cells (precision guard);
  E1 source-image cluster bootstrap (2,000, seed 0; seed-pooled counts) for d relF1@2 and d inactive IoU; leave-top-3 inactive
  images out; E1 inactive by cell (GT inactive px, IoU per arm).
Usage: hc_width_check.py --base NAME M0DIR PREFIX --test NAME M0DIR PREFIX [--seeds 5 6 7 8 9] [--ctx e1_context.tsv]
"""
import argparse, json, math
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--base', nargs=3, required=True); ap.add_argument('--test', nargs=3, required=True)
ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--ctx', default='/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')
a = ap.parse_args()
CR, IN = 14, 11
ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(a.ctx) if l.strip()}


def conf(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); return m.reshape(n, n)[:24, :24]


def load(name, d, pre):
    R = []
    for k in a.seeds:
        j = json.load(open(f'{d}/{pre}_{name}_100pct_s{k}.json'))
        assert j['step'] == 20000 and len(j['cells']['ext']) == 106 and len(j['cells']['test']) == 50, (name, k)
        R.append(j['cells'])
    return R


A = {a.base[0]: load(*a.base), a.test[0]: load(*a.test)}
BN, TN = a.base[0], a.test[0]
ext = sorted(A[BN][0]['ext']); assert all(sorted(r['ext']) == ext for v in A.values() for r in v)


def stats(cells, S):
    M = sum(conf(cells[s]) for s in S)
    r = np.sum([cells[s]['crack_rel2'] for s in S], 0).astype(float)
    P, R = r[0] / max(r[1], 1), r[2] / max(r[3], 1)
    gc = [g for s in S for g in cells[s]['crack_cc']['gt'] if g[0] >= 20]
    free = [s for s in S if conf(cells[s])[CR].sum() == 0]
    iou = lambda k: M[k, k] / max(M[k].sum() + M[:, k].sum() - M[k, k], 1)
    return dict(relF1=2 * P * R / max(P + R, 1e-12), relP=P, relR=R, IoU=iou(CR), pxP=M[CR, CR] / max(M[:, CR].sum(), 1),
                pxR=M[CR, CR] / max(M[CR].sum(), 1), predGT=M[:, CR].sum() / max(M[CR].sum(), 1),
                anyhit=np.mean([g[1] >= 1 for g in gc]) if gc else np.nan, half=np.mean([g[1] >= math.ceil(0.5 * g[0]) for g in gc]) if gc else np.nan,
                freepx=float(sum(conf(cells[s])[:, CR].sum() for s in free)), inact=iou(IN), ngc=len(gc), nfree=len(free))


def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float); d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


STRATA = [('E1 106', lambda s: True), ('E1 scuff+half-cut 29', lambda s: ctx[s][1] == 'scuff_halfcut'),
          ('E1 half-cut no scuff 29', lambda s: ctx[s][3] == 'halfcut=1' and ctx[s][1] != 'scuff_halfcut'),
          ('E1 full 48', lambda s: ctx[s][3] == 'halfcut=0')]
KEYS = ['relF1', 'relP', 'relR', 'IoU', 'pxP', 'pxR', 'predGT', 'anyhit', 'half', 'freepx', 'inact']
for lab, keep in STRATA:
    S = [s for s in ext if keep(s)]
    T = {n: [stats(r['ext'], S) for r in v] for n, v in A.items()}
    print(f'\n## {lab} (n {len(S)}; GT comps>=20 {T[BN][0]["ngc"]}; crack-free cells {T[BN][0]["nfree"]})')
    print('arm     ' + ' '.join(f'{k:>8s}' for k in KEYS))
    for n in (BN, TN):
        print(f'{n:7s} ' + ' '.join(f'{np.nanmean([x[k] for x in T[n]]):8.4f}' if k != 'freepx' else f'{np.mean([x[k] for x in T[n]]):8.0f}' for k in KEYS))
    print('  d ' + ' | '.join(f'{k} {rule([x[k] for x in T[BN]], [x[k] for x in T[TN]])[0]:+.4f} (thr {rule([x[k] for x in T[BN]], [x[k] for x in T[TN]])[1]:.4f})'
                            for k in ('relF1', 'inact', 'anyhit', 'relP', 'relR', 'IoU', 'pxR', 'predGT')))
    if lab == 'E1 106':
        print('  per seed ' + ' || '.join(f'{n}: relF1 ' + ' '.join(f'{x["relF1"]:.4f}' for x in T[n]) + ' inact ' + ' '.join(f'{x["inact"]:.4f}' for x in T[n]) for n in (BN, TN)))

print('\n## test 50 precision guard (argmax)')
St = sorted(A[BN][0]['test'])
T = {n: [stats(r['test'], St) for r in v] for n, v in A.items()}
for n in (BN, TN):
    print(f'{n:7s} predGT {np.mean([x["predGT"] for x in T[n]]):.3f} relP@2 {np.mean([x["relP"] for x in T[n]]):.4f} pxP {np.mean([x["pxP"] for x in T[n]]):.4f} '
          f'crack px on crack-free cells {np.mean([x["freepx"] for x in T[n]]):.0f} (n {T[n][0]["nfree"]})')

# ---- E1 source-image cluster bootstrap, seed-pooled counts
img = lambda s: '_'.join(s.split('_')[:2])  # source module image id (CSIR_01637, BMRK_01502)
imgs = sorted({img(s) for s in ext}); byi = {i: [s for s in ext if img(s) == i] for i in imgs}


def cnt(n, S):
    v = np.zeros(7)
    for r in A[n]:
        for s in S:
            c = r['ext'][s]; m = conf(c); rr = c['crack_rel2']
            v += [rr[0], rr[1], rr[2], rr[3], m[IN, IN], m[:, IN].sum(), m[IN].sum()]
    return v


CI = {n: np.stack([cnt(n, byi[i]) for i in imgs]) for n in (BN, TN)}


def met(v):
    P, R = v[0] / max(v[1], 1), v[2] / max(v[3], 1)
    return 2 * P * R / max(P + R, 1e-12), v[4] / max(v[5] + v[6] - v[4], 1)


w = np.ones(len(imgs)); d0 = np.subtract(met(w @ CI[TN]), met(w @ CI[BN]))
rng = np.random.default_rng(0); bs = []
for _ in range(2000):
    w = np.bincount(rng.integers(0, len(imgs), len(imgs)), minlength=len(imgs)).astype(float)
    bs.append(np.subtract(met(w @ CI[TN]), met(w @ CI[BN])))
bs = np.array(bs)
print(f'\n## E1 image-cluster bootstrap ({len(imgs)} source images, 2,000, seed 0; seed-pooled counts; descriptive)')
for j, k in enumerate(('relF1@2', 'inactive IoU')):
    print(f'{k}: d {d0[j]:+.4f} 95% [{np.percentile(bs[:, j], 2.5):+.4f}, {np.percentile(bs[:, j], 97.5):+.4f}] P(d*>0) {np.mean(bs[:, j] > 0):.3f}')
gi = {i: sum(int(conf(A[BN][0]['ext'][s])[IN].sum()) for s in byi[i]) for i in imgs}
top = [i for i, v in sorted(gi.items(), key=lambda x: -x[1]) if v > 0]
print(f'E1 inactive images (GT inactive px > 0): {len(top)}; top-3 share {sum(gi[i] for i in top[:3]) / max(sum(gi.values()), 1):.3f}')
w = np.array([0.0 if i in top[:3] else 1.0 for i in imgs])
print(f'leave-top-3-inactive-images-out d inactive IoU {met(w @ CI[TN])[1] - met(w @ CI[BN])[1]:+.4f}; d relF1@2 {met(w @ CI[TN])[0] - met(w @ CI[BN])[0]:+.4f}')
for i in top:
    v = {n: met(CI[n][imgs.index(i)])[1] for n in (BN, TN)}
    print(f'  {i}: cells {len(byi[i])} GT inactive px {gi[i]} | inact IoU {BN} {v[BN]:.3f} {TN} {v[TN]:.3f} d {v[TN] - v[BN]:+.3f} | '
          f'strata {sorted({ctx[s][1] + "/" + ctx[s][3] for s in byi[i]})}')
