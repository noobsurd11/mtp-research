#!/usr/bin/env python3
"""judge s2_recompute (2 Nov 2026, respawned judge): own-code recompute of protocol_SKR2_HC2 v1.1 opening (E1 opening #5)
from the m0 per-cell JSONs only (argmax, final weights). Imports no s2_* / el_metrics / coach / earlier judge code.
Sections:
  A  co-primaries, rule 1 /3 (5 v 5): test crack IoU / relF1@2 / inactive IoU on all 50 and clean 49 (minus CSIR_00070_r8_c4);
     E1 (106, one set): relF1@2, any-hit comp recall (SKR2), inactive IoU (HC2).
  B  guards: G1 test inactive d <= -0.015 in both sets (both arms); G2 (SKR2) test relP@2 d < -0.03 (all 50) or
     E1 crack px on GT-crack-free cells (seed mean) > 1.5x SUPPF's.
  C  width / volume next to any-hit: pred/GT crack px (test, E1), relP@2 / relR@2, >= 50% comp recall, any-hit, crack-free px,
     E1 strata (29 scuff+half-cut / 29 half-cut no scuff / 48 full); reference rows (HC, SKR w 1.0) descriptive.
  D  seed-aware two-stage bootstrap (clusters + 5 seeds drawn with replacement per arm, shared cluster draw across arms;
     2,000, numpy default_rng(20261102)); test clusters = module (stem tokens 0-1), E1 clusters = source image (tokens 0-1).
  E  HC2 vs HC vs SUPPF on inactive (label cause vs dilution): per seed, rule 1, seed-aware CIs of HC2-SUPPF / HC2-HC,
     recovered share (HC2-HC)/(SUPPF-HC) with its bootstrap distribution; val inactive (m0 val 54, argmax).
  F  E1 inactive concentration: GT inactive px by source image, top-3 share, per-image IoU per arm (seed-pooled),
     leave-top-3-images-out d, image-cluster seed-aware CI.
Usage: s2_recompute.py --arm NAME M0DIR PREFIX [--arm ...] --base NAME --ctx e1_context.tsv
"""
import argparse, json, math
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=3, action='append', required=True, metavar=('NAME', 'M0', 'PREFIX'))
ap.add_argument('--base', required=True)
ap.add_argument('--contrasts', nargs='+', default=['SKR2', 'HC2'])
ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--ctx', default='/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')
ap.add_argument('--nboot', type=int, default=2000)
a = ap.parse_args()
CR, IN, NOISY = 14, 11, 'CSIR_00070_r8_c4'
ctx = {}
for l in open(a.ctx):
    if l.strip():
        t = l.rstrip('\n').split('\t'); ctx[t[0]] = t


def C(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); assert n * n == m.size
    m = m.reshape(n, n)
    if n == 25:  # scuff class 24 -> background (B3 only)
        m = m.copy(); m[0] += m[24]; m[:, 0] += m[:, 24]; m = m[:24, :24]
    assert m.shape == (24, 24)
    return m


ARMS, ORDER = {}, []
for name, d, pre in a.arm:
    runs = []
    for k in a.seeds:
        j = json.load(open(f'{d}/{pre}_100pct_s{k}.json'))
        assert j['step'] == 20000, (name, k, j['step'])
        assert len(j['cells']['test']) == 50 and len(j['cells']['ext']) == 106 and len(j['cells']['val']) == 54, name
        runs.append(j)
    ARMS[name] = runs; ORDER.append(name)
    print(f'# {name}: {pre}_100pct_s{a.seeds}; code_revision {sorted({r["code_revision"] for r in runs})}; run names '
          f'{[r["run"] for r in runs]}')
ST = {s: sorted(ARMS[a.base][0]['cells'][s]) for s in ('test', 'ext', 'val')}
for n in ORDER:
    for r in ARMS[n]:
        for s in ST:
            assert sorted(r['cells'][s]) == ST[s], (n, s)
assert NOISY in ST['test']

# per (arm, seed, set, cell) count vector:
# 0 crack tp, 1 crack pred, 2 crack gt, 3 inact tp, 4 inact pred, 5 inact gt, 6 relP tp, 7 relP pred, 8 relR tp, 9 relR gt,
# 10 gt comps>=20, 11 any-hit comps, 12 >=50% comps, 13 crack px if cell GT-crack-free (else 0), 14 1 if crack-free
NK = 15


def vec(c):
    m = C(c); r = c['crack_rel2']; g = [x for x in c['crack_cc']['gt'] if x[0] >= 20]
    free = m[CR].sum() == 0
    return np.array([m[CR, CR], m[:, CR].sum(), m[CR].sum(), m[IN, IN], m[:, IN].sum(), m[IN].sum(), r[0], r[1], r[2], r[3],
                     len(g), sum(x[1] >= 1 for x in g), sum(x[1] >= math.ceil(0.5 * x[0]) for x in g),
                     m[:, CR].sum() if free else 0, 1 if free else 0], float)


V = {n: {s: np.stack([np.stack([vec(r['cells'][s][st]) for st in ST[s]]) for r in ARMS[n]]) for s in ST} for n in ORDER}  # seeds x cells x NK


def met(t):  # t: (..., NK) summed counts
    f = lambda x, y: x / np.maximum(y, 1e-12)
    P, R = f(t[..., 6], t[..., 7]), f(t[..., 8], t[..., 9])
    return dict(crackIoU=f(t[..., 0], t[..., 1] + t[..., 2] - t[..., 0]), inact=f(t[..., 3], t[..., 4] + t[..., 5] - t[..., 3]),
                relF1=f(2 * P * R, P + R), relP=P, relR=R, pxP=f(t[..., 0], t[..., 1]), pxR=f(t[..., 0], t[..., 2]),
                predGT=f(t[..., 1], t[..., 2]), anyhit=f(t[..., 11], t[..., 10]), half=f(t[..., 12], t[..., 10]), freepx=t[..., 13],
                nfree=t[..., 14], ncomp=t[..., 10])


def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float); d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


def per_seed(n, s, keep=None):
    x = V[n][s] if keep is None else V[n][s][:, keep]
    return met(x.sum(1))


def mask(s, f):
    return np.array([f(st) for st in ST[s]])


SETS = {'test50': ('test', None), 'test49': ('test', mask('test', lambda st: st != NOISY)), 'E1': ('ext', None),
        'E1 scuff+halfcut 29': ('ext', mask('ext', lambda st: ctx[st][1] == 'scuff_halfcut')),
        'E1 halfcut no-scuff 29': ('ext', mask('ext', lambda st: ctx[st][3] == 'halfcut=1' and ctx[st][1] != 'scuff_halfcut')),
        'E1 full 48': ('ext', mask('ext', lambda st: ctx[st][3] == 'halfcut=0')), 'val54': ('val', None)}
PS = {n: {lab: per_seed(n, s, k) for lab, (s, k) in SETS.items()} for n in ORDER}
B = a.base

print('\n## A. co-primaries (rule 1 /3, 5 v 5; per-seed values)')
for n in ORDER:
    print(f'{n:6s} test50 crackIoU {PS[n]["test50"]["crackIoU"].mean():.4f} relF1 {PS[n]["test50"]["relF1"].mean():.4f} '
          f'inact {PS[n]["test50"]["inact"].mean():.4f} | test49 crackIoU {PS[n]["test49"]["crackIoU"].mean():.4f} relF1 '
          f'{PS[n]["test49"]["relF1"].mean():.4f} inact {PS[n]["test49"]["inact"].mean():.4f} | E1 relF1 {PS[n]["E1"]["relF1"].mean():.4f} '
          f'any-hit {PS[n]["E1"]["anyhit"].mean():.4f} inact {PS[n]["E1"]["inact"].mean():.4f}')
for n in ORDER:
    print(f'  per-seed {n}: test50 crackIoU ' + ' '.join(f'{x:.4f}' for x in PS[n]['test50']['crackIoU'])
          + ' | relF1 ' + ' '.join(f'{x:.4f}' for x in PS[n]['test50']['relF1'])
          + ' | inact ' + ' '.join(f'{x:.4f}' for x in PS[n]['test50']['inact'])
          + ' | E1 relF1 ' + ' '.join(f'{x:.4f}' for x in PS[n]['E1']['relF1'])
          + ' | E1 any-hit ' + ' '.join(f'{x:.4f}' for x in PS[n]['E1']['anyhit'])
          + ' | E1 inact ' + ' '.join(f'{x:.4f}' for x in PS[n]['E1']['inact']))
print(f'  E1 GT comps >= 20 px per run: {sorted(set(PS[B]["E1"]["ncomp"].tolist()))}; E1 crack-free cells {sorted(set(PS[B]["E1"]["nfree"].tolist()))}')
COP = {'SKR2': [('test50', 'crackIoU'), ('test49', 'crackIoU'), ('test50', 'relF1'), ('test49', 'relF1'), ('test50', 'inact'),
                ('test49', 'inact'), ('E1', 'relF1'), ('E1', 'anyhit')],
       'HC2': [('test50', 'crackIoU'), ('test49', 'crackIoU'), ('test50', 'relF1'), ('test49', 'relF1'), ('test50', 'inact'),
               ('test49', 'inact'), ('E1', 'relF1'), ('E1', 'inact')]}
for n in a.contrasts:
    if n not in ARMS: continue
    print(f'\n{n} - {B}:')
    for lab, k in COP.get(n, COP["HC2"]):
        d, thr, v = rule(PS[B][lab][k], PS[n][lab][k]); print(f'  {lab:7s} {k:9s} d {d:+.4f} thr {thr:.4f} {v}')

print('\n## B. guards')
for n in a.contrasts:
    if n not in ARMS: continue
    g1 = [PS[n][lab]['inact'].mean() - PS[B][lab]['inact'].mean() for lab in ('test50', 'test49')]
    print(f'{n} G1 test inactive d all {g1[0]:+.4f} clean {g1[1]:+.4f} -> {"TRIP" if all(x <= -0.015 for x in g1) else "ok"}')
    if n == 'SKR2':
        drp = PS[n]['test50']['relP'].mean() - PS[B]['test50']['relP'].mean()
        fr = PS[n]['E1']['freepx'].mean() / PS[B]['E1']['freepx'].mean()
        print(f'{n} G2 test relP@2 d {drp:+.4f} (trip < -0.03) | E1 crack-free px {PS[n]["E1"]["freepx"].mean():.0f} vs '
              f'{PS[B]["E1"]["freepx"].mean():.0f} ratio x{fr:.3f} (trip > 1.5) -> {"TRIP" if (drp < -0.03 or fr > 1.5) else "ok"}')
        print(f'   per-seed E1 crack-free px {n} ' + ' '.join(f'{x:.0f}' for x in PS[n]['E1']['freepx'])
              + f' | {B} ' + ' '.join(f'{x:.0f}' for x in PS[B]['E1']['freepx']))

print('\n## C. width / volume (arm means over seeds; rule-1 d for the contrasts; reference rows descriptive)')
KEYS = ['relF1', 'relP', 'relR', 'crackIoU', 'pxP', 'pxR', 'predGT', 'anyhit', 'half', 'freepx', 'inact']
for lab in SETS:
    print(f'-- {lab} (GT comps>=20 per run {int(PS[B][lab]["ncomp"][0])}, crack-free cells {int(PS[B][lab]["nfree"][0])})')
    print('   arm    ' + ' '.join(f'{k:>8s}' for k in KEYS))
    for n in ORDER:
        print(f'   {n:6s} ' + ' '.join((f'{PS[n][lab][k].mean():8.0f}' if k == 'freepx' else f'{PS[n][lab][k].mean():8.4f}') for k in KEYS))
    for n in a.contrasts:
        if n in ARMS:
            print(f'   {n}-{B}: ' + ' | '.join(f'{k} {rule(PS[B][lab][k], PS[n][lab][k])[0]:+.4f} ({rule(PS[B][lab][k], PS[n][lab][k])[1]:.4f})'
                                         for k in ('relF1', 'relP', 'relR', 'anyhit', 'half', 'predGT', 'inact')))

# ---------- D/E/F: two-stage bootstrap ----------
rng = np.random.default_rng(20261102)


def clusters(s, keep=None):
    st = ST[s] if keep is None else [x for x, k in zip(ST[s], keep) if k]
    keys = sorted({'_'.join(x.split('_')[:2]) for x in st})
    idx = np.array([keys.index('_'.join(x.split('_')[:2])) for x in st])
    return keys, idx


def clsum(n, s, keep=None):  # seeds x clusters x NK
    keys, idx = clusters(s, keep)
    x = V[n][s] if keep is None else V[n][s][:, keep]
    out = np.zeros((x.shape[0], len(keys), NK))
    for j in range(len(keys)):
        out[:, j] = x[:, idx == j].sum(1)
    return keys, out


def boot(lab, metric, arms, nb=a.nboot):
    s, keep = SETS[lab]
    K = {n: clsum(n, s, keep) for n in arms}
    nc = len(K[arms[0]][0]); ns = len(a.seeds)
    res = {n: np.empty(nb) for n in arms}
    for b in range(nb):
        w = np.bincount(rng.integers(0, nc, nc), minlength=nc).astype(float)
        for n in arms:
            sd = rng.integers(0, ns, ns)
            t = np.einsum('c,sck->sk', w, K[n][1][sd])
            res[n][b] = met(t)[metric].mean()
    return nc, res


def ci(x):
    return f'[{np.percentile(x, 2.5):+.4f}, {np.percentile(x, 97.5):+.4f}]'


print(f'\n## D. seed-aware two-stage bootstrap ({a.nboot}; clusters + seeds per arm; rng 20261102)')
for n in a.contrasts:
    if n not in ARMS: continue
    for lab, k in [('test50', 'crackIoU'), ('test50', 'relF1'), ('test50', 'inact'), ('test49', 'inact'), ('E1', 'relF1'),
                   ('E1', 'anyhit' if n == 'SKR2' else 'inact'), ('E1', 'predGT'), ('E1', 'freepx')]:
        nc, r = boot(lab, k, [B, n]); d = r[n] - r[B]
        extra = f' ratio {ci(r[n] / np.maximum(r[B], 1e-9))[1:-1]}' if k == 'freepx' else ''
        print(f'{n}-{B} {lab:7s} {k:8s} ({nc} clusters): CI {ci(d)} P(d<0) {np.mean(d < 0):.3f}{extra}')

if all(x in ARMS for x in ('HC2', 'HC')):
    print('\n## E. HC2 vs HC vs SUPPF (inactive: label cause vs dilution)')
    for lab in ('test50', 'test49', 'val54', 'E1'):
        x = {n: PS[n][lab]['inact'] for n in (B, 'HC', 'HC2')}
        print(f'-- {lab} inactive per seed: ' + ' | '.join(f'{n} ' + ' '.join(f'{v:.4f}' for v in x[n]) + f' (mean {x[n].mean():.4f}, sd {x[n].std(ddof=1):.4f})' for n in x))
        for p, q in (('HC2', B), ('HC2', 'HC'), ('HC', B)):
            d, thr, v = rule(x[q], x[p]); print(f'   {p}-{q}: d {d:+.4f} thr {thr:.4f} {v}')
        den = x[B].mean() - x['HC'].mean()
        print(f'   recovered share (HC2-HC)/(SUPPF-HC) = {(x["HC2"].mean() - x["HC"].mean()) / den if abs(den) > 1e-9 else float("nan"):+.2f}'
              f'  (1 = back to SUPPF: label cause; 0 = stays at HC: dilution)')
        print(f'   paired-by-seed HC2-HC: ' + ' '.join(f'{v:+.4f}' for v in x['HC2'] - x['HC']) + f'; corr(HC, HC2) over seeds {np.corrcoef(x["HC"], x["HC2"])[0, 1]:+.2f}')
        if lab != 'val54':
            nc, r = boot(lab, 'inact', [B, 'HC', 'HC2'])
            d1, d2, d3 = r['HC2'] - r[B], r['HC2'] - r['HC'], r['HC'] - r[B]
            rec = (r['HC2'] - r['HC']) / np.where(np.abs(r[B] - r['HC']) > 1e-9, r[B] - r['HC'], np.nan)
            print(f'   seed-aware ({nc} clusters): HC2-SUPPF {ci(d1)} P(<0) {np.mean(d1 < 0):.3f} | HC2-HC {ci(d2)} P(>0) {np.mean(d2 > 0):.3f}'
                  f' | HC-SUPPF {ci(d3)} P(<0) {np.mean(d3 < 0):.3f} | recovered share median {np.nanmedian(rec):+.2f} '
                  f'IQR [{np.nanpercentile(rec, 25):+.2f}, {np.nanpercentile(rec, 75):+.2f}] (only draws with SUPPF>HC: '
                  f'{np.mean(r[B] > r["HC"]):.2f} of draws)')
    for lab in ('test50', 'E1'):
        x = {n: PS[n][lab]['crackIoU'] for n in (B, 'HC', 'HC2')}
        y = {n: PS[n][lab]['relF1'] for n in (B, 'HC', 'HC2')}
        print(f'-- {lab} crack IoU means ' + ' '.join(f'{n} {x[n].mean():.4f}' for n in x) + ' | relF1 ' + ' '.join(f'{n} {y[n].mean():.4f}' for n in y)
              + f' | HC2-HC crackIoU {rule(x["HC"], x["HC2"])[0]:+.4f} (thr {rule(x["HC"], x["HC2"])[1]:.4f}) relF1 {rule(y["HC"], y["HC2"])[0]:+.4f} (thr {rule(y["HC"], y["HC2"])[1]:.4f})')
    # test inactive cells: per cell seed-pooled IoU per arm
    gt = V[B]['test'][0][:, 5]; order = np.argsort(-gt)
    pool = {n: V[n]['test'].sum(0) for n in (B, 'HC', 'HC2')}
    ci_ = lambda t: t[3] / max(t[4] + t[5] - t[3], 1)
    print('-- test inactive cells (seed-pooled IoU): stem GTpx SUPPF HC HC2 | HC2-SUPPF HC2-HC')
    dn = {('HC', B): 0, ('HC2', B): 0, ('HC2', 'HC'): 0}
    for i in order:
        if gt[i] == 0: break
        v = {n: ci_(pool[n][i]) for n in pool}
        for (p, q) in dn: dn[(p, q)] += v[p] < v[q]
        print(f'   {ST["test"][i]:22s} {gt[i]:7.0f} {v[B]:.3f} {v["HC"]:.3f} {v["HC2"]:.3f} | {v["HC2"] - v[B]:+.3f} {v["HC2"] - v["HC"]:+.3f}')
    print(f'   cells down: HC<SUPPF {dn[("HC", B)]}, HC2<SUPPF {dn[("HC2", B)]}, HC2<HC {dn[("HC2", "HC")]} of {int((gt > 0).sum())}')

print('\n## F. E1 inactive concentration (by source image = stem tokens 0-1; GT px seed-invariant)')
keys, idx = clusters('ext')
gti = np.array([V[B]['ext'][0][idx == j, 5].sum() for j in range(len(keys))])
tot = gti.sum(); oi = np.argsort(-gti); nz = int((gti > 0).sum())
print(f'E1 GT inactive px {tot:.0f} in {nz} images ({int((V[B]["ext"][0][:, 5] > 0).sum())} cells); top-3 images share {gti[oi[:3]].sum() / tot:.3f}; '
      f'top-1 {gti[oi[0]] / tot:.3f}; effective n images (1/sum w^2) {1 / np.sum((gti / tot) ** 2):.2f}')
arms_f = [n for n in ORDER]
cp = {n: np.stack([V[n]['ext'][:, idx == j].sum(1) for j in range(len(keys))], 1) for n in arms_f}  # seeds x images x NK
for j in oi[:nz]:
    ncell = int((V[B]['ext'][0][idx == j, 5] > 0).sum())
    print(f'   {keys[j]:12s} GT {gti[j]:7.0f} ({gti[j] / tot:.3f}, {ncell} inact cells) ' + ' '.join(
        f'{n} {met(cp[n][:, j].sum(0))["inact"]:.3f}' for n in arms_f) + ' | per-seed ' + ' ; '.join(
        f'{n} ' + '/'.join(f'{x:.2f}' for x in met(cp[n][:, j])['inact']) for n in arms_f if n in (B, 'HC2', 'SKR2', 'HC')))
keep_imgs = np.ones(len(keys), bool); keep_imgs[oi[:3]] = False
for n in a.contrasts + (['HC'] if 'HC' in ARMS else []):
    if n not in ARMS: continue
    full = met(cp[n].sum(1))['inact'].mean() - met(cp[B].sum(1))['inact'].mean()
    lo = met(cp[n][:, keep_imgs].sum(1))['inact'] - met(cp[B][:, keep_imgs].sum(1))['inact']
    print(f'{n}-{B} E1 inactive d all {full:+.4f} | leave-top-3-images-out d {lo.mean():+.4f} (remaining GT px {gti[keep_imgs].sum():.0f})')
