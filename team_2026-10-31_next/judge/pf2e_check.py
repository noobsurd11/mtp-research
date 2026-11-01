#!/usr/bin/env python3
"""judge (1 Nov): independent PF2E check on the pulled opening files (laptop; own code, no Track M import).
1. Members: each E-*.json 'members' == pf2_{SUP,SUPPF}_100pct_s5..9; step 20000; revision e544133.
2. D2 re-derived from the val sweep in pf2e_val_decisions.json (smallest b in 0..3/0.25 with relR2 >= 0.90, used if relP2 >= 0.90,
   else max relF1; headline 0 if crack_P(b0) - crack_P(b) > 0.05), and the sweep re-derived from the val cells at every b that
   has a file (val cells are stored per b): |d| must be 0.
3. Test: own paired image bootstrap (2,000, seed 0, own RNG use) for crack IoU / relF1@2 / inactive IoU, all 50 and clean.
   E1: own paired module-cluster bootstrap (cluster = stem minus _rN_cM / _cellN), relF1@2 and inactive IoU; plus a
   leave-one-cluster-out range and a cell-level (unclustered) CI for comparison.
Usage: pf2e_check.py OUT_DIR [--verdict-b headline|chosen]   |   pf2e_check.py --selftest PF2_M0_DIR"""
import json, re, sys, math
from pathlib import Path
import numpy as np

CR, IN, NOISY = 14, 11, 'CSIR_00070_r8_c4'
MOD = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)

def counts(cells, stems):
    X = np.zeros((len(stems), 10))
    for i, s in enumerate(stems):
        c = cells[s]; m = np.asarray(c['conf'], np.int64); n = int(math.isqrt(m.size)); m = m.reshape(n, n)[:24, :24]
        X[i, :3] = m[CR, CR], m[:, CR].sum() - m[CR, CR], m[CR, :].sum() - m[CR, CR]
        X[i, 3:6] = m[IN, IN], m[:, IN].sum() - m[IN, IN], m[IN, :].sum() - m[IN, IN]
        X[i, 6:10] = c['crack_rel2']
    return X

def prim(S):  # crack IoU, relF1@2, inactive IoU from summed counts
    ci = S[0] / max(S[0] + S[1] + S[2], 1); ii = S[3] / max(S[3] + S[4] + S[5], 1)
    P, R = S[6] / max(S[7], 1), S[8] / max(S[9], 1)
    return np.array([ci, 2 * P * R / max(P + R, 1e-12), ii])

def boot(A, B, stems, key=None, n=2000, seed=0):
    XA, XB = counts(A, stems), counts(B, stems)
    groups = sorted({key(s) for s in stems}) if key else None
    idx = [[i for i, s in enumerate(stems) if key(s) == g] for g in groups] if key else None
    full = prim(XB.sum(0)) - prim(XA.sum(0)); rng = np.random.default_rng(seed); out = np.empty((n, 3))
    for t in range(n):
        if key:
            ix = np.concatenate([idx[j] for j in rng.integers(0, len(groups), len(groups))])
        else:
            ix = rng.integers(0, len(stems), len(stems))
        out[t] = prim(XB[ix].sum(0)) - prim(XA[ix].sum(0))
    lo, hi = np.percentile(out, [2.5, 97.5], 0)
    loo = None
    if key:
        loo = np.array([prim(XB[np.setdiff1d(np.arange(len(stems)), idx[j])].sum(0)) - prim(XA[np.setdiff1d(np.arange(len(stems)), idx[j])].sum(0)) for j in range(len(groups))])
    return full, lo, hi, (out > 0).mean(0), (len(groups) if key else len(stems)), loo

if '--selftest' in sys.argv:
    d = Path(sys.argv[sys.argv.index('--selftest') + 1])
    A = json.load(open(d / 'pf2_SUP_100pct_s5.json'))['cells']; B = json.load(open(d / 'pf2_SUPPF_100pct_s5.json'))['cells']
    st = sorted(A['test']); f, lo, hi, p, n, _ = boot(A['test'], B['test'], st)
    print('selftest test s5 vs s5 (crack IoU, relF1, inact):', np.round(f, 4), np.round(lo, 4), np.round(hi, 4), n)
    e = sorted(A['ext']); f, lo, hi, p, n, loo = boot(A['ext'], B['ext'], e, key=MOD)
    print('selftest E1 module clusters:', n, 'full', np.round(f, 4), 'CI', np.round(lo, 4), np.round(hi, 4), 'LOO range relF1', np.round([loo[:, 1].min(), loo[:, 1].max()], 4))
    f0, *_ = boot(A['ext'], A['ext'], e, key=MOD); print('identical arms -> 0:', np.allclose(f0, 0)); sys.exit()

D = Path(sys.argv[1]); vb = sys.argv[sys.argv.index('--verdict-b') + 1] if '--verdict-b' in sys.argv else 'headline'
dec = json.load(open(D / 'pf2e_val_decisions.json'))
J = {}
for f in sorted(D.glob('E-*.b*.json')):
    j = json.load(open(f)); J[(j['run'], float(j['bias']))] = j
print('# files:', sorted(f'{k} b{b:g}' for k, b in J))
# 1 members
for (k, b), j in J.items():
    arm = {'E-g': 'SUP', 'E-PF': 'SUPPF'}[k]
    ok = j['members'] == [f'pf2_{arm}_100pct_s{q}' for q in range(5, 10)] and j['step'] == 20000 and j['code_revision'] == 'e544133'
    print(f'  members {k} b{b:g}: {j["members"]} ok={ok}')
print('  decisions meta:', {k: v for k, v in dec['meta'].items() if k != 'E-g' and k != 'E-PF'})
# 2 D2
def summ(cells):
    S = counts(cells, sorted(cells)).sum(0); P, R = S[6] / max(S[7], 1), S[8] / max(S[9], 1)
    return dict(crack_iou=S[0] / max(S[:3].sum(), 1), crack_P=S[0] / max(S[0] + S[1], 1), relP2=P, relR2=R, relF1=2 * P * R / max(P + R, 1e-12), inact_iou=S[3] / max(S[3:6].sum(), 1))
for k in ('E-g', 'E-PF'):
    sw = {float(b): v for b, v in dec[k]['sweep'].items()}; G = sorted(sw)
    ok = [b for b in G if sw[b]['relR2'] >= 0.90]
    if ok and sw[ok[0]]['relP2'] >= 0.90: b, why = ok[0], 'smallest b relR>=.90 & relP>=.90'
    else: b, why = max(G, key=lambda x: sw[x]['relF1']), 'max relF1'
    drop = sw[0.0]['crack_P'] - sw[b]['crack_P']; hb = 0.0 if drop > 0.05 else b
    print(f'  D2 {k}: mine b {b} ({why}), drop {drop:+.4f}, headline {hb} | file b {dec[k]["bias"]}, headline {dec[k]["headline_bias"]} | '
          f'agree {b == dec[k]["bias"] and hb == dec[k]["headline_bias"]}')
    print('    val sweep relR2 ' + ' '.join(f'{x:g}:{sw[x]["relR2"]:.3f}/{sw[x]["relP2"]:.3f}' for x in G))
    for (kk, bb), j in J.items():
        if kk == k:
            m = summ(j['cells']['val']); dmax = max(abs(m[q] - sw[bb][q]) for q in m)
            print(f'    val cells at b{bb:g} re-summed vs sweep: max |d| {dmax:.2e}')
# 3 verdict
pick = lambda k: dec[k]['headline_bias'] if vb == 'headline' else dec[k]['bias']
for tag, bg, bp in (('VERDICT ' + vb, pick('E-g'), pick('E-PF')), ('b 0', 0.0, 0.0)):
    A, B = J[('E-g', float(bg))]['cells'], J[('E-PF', float(bp))]['cells']
    print(f'\n## {tag}: E-g b {bg} vs E-PF b {bp}')
    for sn, f in (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY)):
        st = sorted(s for s in A['test'] if f(s)); full, lo, hi, p, n, _ = boot(A['test'], B['test'], st)
        print(f'  test {sn}: ' + ' | '.join(f'{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {p[i]:.2f}' for i, nm in enumerate(('crack IoU', 'relF1@2', 'inact IoU'))))
    e = sorted(A['ext']); full, lo, hi, p, n, loo = boot(A['ext'], B['ext'], e, key=MOD)
    print(f'  E1 ({n} clusters): relF1@2 {full[1]:+.4f} [{lo[1]:+.4f}, {hi[1]:+.4f}] P>0 {p[1]:.2f} | inact IoU {full[2]:+.4f} [{lo[2]:+.4f}, {hi[2]:+.4f}] P>0 {p[2]:.2f}'
          f' | LOCO relF1 [{loo[:, 1].min():+.4f}, {loo[:, 1].max():+.4f}] inact [{loo[:, 2].min():+.4f}, {loo[:, 2].max():+.4f}]')
    f2, lo2, hi2, *_ = boot(A['ext'], B['ext'], e)
    print(f'  E1 cell-level (unclustered, comparison only): relF1 [{lo2[1]:+.4f}, {hi2[1]:+.4f}] inact [{lo2[2]:+.4f}, {hi2[2]:+.4f}]')
