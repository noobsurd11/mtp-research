#!/usr/bin/env python3
"""judge_s2c.py (judge, 14 Nov 2026): own recompute of the deciding numbers of the SKR2C opening (E1 opening #7).
Reads only the copied raw per-cell files (results/s2c/raw_r, raw_d) and the real split lists. numpy only.
Imports nothing from the coach, the runner, the frozen set or Track M.
Written AFTER reading verify_skr2c.md (the task order), so it is a check of stated numbers, not a blind recompute.

 0 inputs: real lists (md5), stems of every file used, run names, step, revision, tau0 = default
 1 verdict R: test co-primaries (two-set rule) and E1 co-primaries by rule 1 /3; guards G1 and G2 (ruling 1 bar)
 2 named claim, condition 1: seed-aware two-stage bootstrap of E1 relF1@2 (71 clusters x 5 runs per arm, 2,000, seed 0;
   draw order of the pattern the protocol names: clusters, then SUPPF runs, then SKR01 runs)
 3 verdict D: test primaries (paired cell bootstrap, all 50 / clean 49) and E1 primaries (71-cluster bootstrap), 2,000, seed 0;
   guards G2a, G2b, G1t, G1e
 4 checks of the coach's reported statements that the rulings (c) and (d) rest on (no bar or set changed)
Delta = SKR01 - SUPPF (R) and E-SKR2' - E-SUPPF' (D) throughout.
Usage: judge_s2c.py [OUT_TXT]
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

T = Path('/home/yugma/mtp/research/team_2026-10-31_next')
RAW_R, RAW_D = T / 'results/s2c/raw_r', T / 'results/s2c/raw_d'
LISTS = {'test': ('/home/noob/work/el_f3/data/splits/test.txt', 'a31fad14fa27ee28e2a2319b8976aba3', 50),
         'val': ('/home/noob/work/el_f3/data/splits/val.txt', '9dcccf00662dfca750f0b46628f8d5bb', 54),
         'ext': ('/home/noob/work/el_f1/reports/f1/ext117/stems_eval.txt', '5266806b559f74bcf9eae167bb076b95', 106)}
TRAIN_ROOT_TEST = '/home/noob/work/s2c_root/splits/test.txt'
SEEDS = [10, 11, 12, 13, 14]
ARMS = {'SUPPF': 's2c_SUPPF_100pct_s', 'SKR01': 's2c_SKR01_100pct_s'}
REV = {'SUPPF': 'e544133', 'SKR01': 'c9bbb02'}
CR, IN, NOISY = 14, 11, 'CSIR_00070_r8_c4'
MOD = lambda s: re.sub(r'(_r\d+_c\d+|_cell\d+)$', '', s)
NB = 2000

out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
LINES = []


def P(s=''):
    print(s)
    LINES.append(s)


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


# ---------------------------------------------------------------- 0 inputs
P('## 0 inputs')
REAL = {}
for k, (p, m, n) in LISTS.items():
    st = [l.strip() for l in open(p) if l.strip()]
    got = md5(p)
    assert got == m, (k, got)
    assert len(st) == n == len(set(st)), (k, len(st))
    REAL[k] = sorted(st)
    P(f'  real {k} list {p}: md5 {got[:8]} (expected {m[:8]}), {n} stems')
root_test = sorted(l.strip() for l in open(TRAIN_ROOT_TEST) if l.strip())
P(f'  training root test.txt md5 {md5(TRAIN_ROOT_TEST)[:8]}; equals real val list: {root_test == REAL["val"]}; '
  f'stems shared with the real test list: {len(set(root_test) & set(REAL["test"]))}')
assert NOISY in REAL['test']


def vec(c):
    m = np.asarray(c['conf'], np.int64)
    n = math.isqrt(m.size)
    assert n == 24 and n * n == m.size
    m = m.reshape(n, n)  # rows GT, cols prediction
    g = [e for e in c['crack_cc']['gt'] if e[0] >= 20]
    r = c['crack_rel2']
    return np.array([m[CR, CR], m[:, CR].sum(), m[CR, :].sum(),      # 0 crack tp, 1 crack pred px, 2 crack GT px
                     m[IN, IN], m[:, IN].sum(), m[IN, :].sum(),      # 3 inact tp, 4 inact pred px, 5 inact GT px
                     r[0], r[1], r[2], r[3],                         # 6 relP tp, 7 relP den, 8 relR tp, 9 relR den
                     len(g), sum(1 for e in g if e[1] >= 1)], float)  # 10 GT comps >= 20 px, 11 comps hit


def met(S):
    S = np.asarray(S, float)
    d = lambda a, b: np.where(b > 0, a / np.where(b > 0, b, 1.0), 0.0)
    p, r = d(S[..., 6], S[..., 7]), d(S[..., 8], S[..., 9])
    return {'crack': d(S[..., 0], S[..., 1] + S[..., 2] - S[..., 0]), 'inact': d(S[..., 3], S[..., 4] + S[..., 5] - S[..., 3]),
            'relP': p, 'relR': r, 'relF1': d(2 * p * r, p + r), 'anyhit': d(S[..., 11], S[..., 10]),
            'predGT': d(S[..., 1], S[..., 2])}


RUNS = {}
for arm, pre in ARMS.items():
    L = []
    for k in SEEDS:
        f = RAW_R / 'm0' / arm / f'{pre}{k}.json'
        j = json.load(open(f))
        assert j['run'] == f'{pre}{k}' and j['step'] == 20000 and j['code_revision'] == REV[arm], (f, j['run'], j['step'])
        for sp in ('test', 'val', 'ext'):
            assert sorted(j['cells'][sp]) == REAL[sp], (f, sp)
        t0 = json.load(open(RAW_R / 'm0' / arm / f'{pre}{k}.tau0.json'))
        assert t0['run'] == j['run'] and t0['step'] == 20000
        same = all(t0['cells'][sp][s]['conf'] == j['cells'][sp][s]['conf'] and t0['cells'][sp][s]['crack_rel2'] == j['cells'][sp][s]['crack_rel2']
                   and t0['cells'][sp][s]['crack_cc'] == j['cells'][sp][s]['crack_cc'] for sp in ('test', 'ext') for s in REAL[sp])
        assert same, (f, 'tau0 != default')
        L.append(j)
    RUNS[arm] = L
    P(f'  {arm}: runs {[r["run"] for r in L]}; step 20000; revision {REV[arm]}; test / val / E1 stems = the real lists; tau0 cells = default cells')
others = sorted(p.name for a in ARMS for p in (RAW_R / 'm0' / a).glob('*.json') if not re.fullmatch(ARMS[a] + r'1[0-4](\.tau[01])?\.json', p.name))
P(f'  m0 JSONs that are not one of the 10 fresh runs: {others if others else "none"}')

X = {a: {sp: np.stack([np.stack([vec(r['cells'][sp][s]) for s in REAL[sp]]) for r in RUNS[a]]) for sp in ('test', 'ext', 'val')} for a in ARMS}
for sp in ('test', 'ext', 'val'):  # GT-only columns must not depend on arm or run
    g = X['SUPPF'][sp][0][:, [2, 5, 9, 10]]
    assert all((X[a][sp][i][:, [2, 5, 9, 10]] == g).all() for a in ARMS for i in range(5)), sp
TEST, EXT = REAL['test'], REAL['ext']
clean = np.array([s != NOISY for s in TEST])
free = X['SUPPF']['ext'][0][:, 2] == 0
P(f'  GT-only columns equal over the 10 runs; E1 GT comps >= 20 px {int(X["SUPPF"]["ext"][0][:, 10].sum())}; '
  f'E1 crack-free cells {int(free.sum())}; test GT comps {int(X["SUPPF"]["test"][0][:, 10].sum())}; '
  f'E1 clusters {len({MOD(s) for s in EXT})}; test modules {len({MOD(s) for s in TEST})}')
assert int(free.sum()) == 74 and int(X['SUPPF']['ext'][0][:, 10].sum()) == 296 and len({MOD(s) for s in EXT}) == 71


def rule1(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


def perseed(arm, sp, keep=None):
    x = X[arm][sp] if keep is None else X[arm][sp][:, keep]
    return met(x.sum(1))


# ---------------------------------------------------------------- 1 verdict R
P('\n## 1 verdict R (singles, seed means, rule 1 /3, 5 v 5)')
PS = {a: {'t50': perseed(a, 'test'), 't49': perseed(a, 'test', clean), 'e1': perseed(a, 'ext')} for a in ARMS}
LAB = {}
for name, k in (('test crack IoU', 'crack'), ('test crack relF1@2', 'relF1'), ('test inactive IoU', 'inact')):
    r50, r49 = rule1(PS['SUPPF']['t50'][k], PS['SKR01']['t50'][k]), rule1(PS['SUPPF']['t49'][k], PS['SKR01']['t49'][k])
    # two-set rule (review_spec_cp5_v1.md l.7: "pass on both, or on one with a same-sign n.d. on the other; worse on either fails")
    better = (r50[2] == 'BETTER' and r49[2] == 'BETTER') or (r50[2] == 'BETTER' and r49[0] > 0) or (r49[2] == 'BETTER' and r50[0] > 0)
    worse = 'WORSE' in (r50[2], r49[2])
    reg = 'WORSE' if worse else ('BETTER' if better else 'n.d.')
    either = 'WORSE' if worse else ('BETTER' if 'BETTER' in (r50[2], r49[2]) else 'n.d.')  # loosest reading: one set alone may label
    LAB[name] = (reg, either)
    P(f'  {name:20s} SUPPF {PS["SUPPF"]["t50"][k].mean():.4f} +- {PS["SUPPF"]["t50"][k].std(ddof=1):.4f}  SKR01 {PS["SKR01"]["t50"][k].mean():.4f} +- '
      f'{PS["SKR01"]["t50"][k].std(ddof=1):.4f} | all 50 d {r50[0]:+.4f} (thr {r50[1]:.4f}) {r50[2]} | clean 49 d {r49[0]:+.4f} (thr {r49[1]:.4f}) {r49[2]} '
      f'| two-set label: {reg}; if one set alone could label: {either}')
for name, k in (('E1 crack relF1@2', 'relF1'), ('E1 any-hit', 'anyhit')):
    r = rule1(PS['SUPPF']['e1'][k], PS['SKR01']['e1'][k])
    LAB[name] = (r[2], r[2])
    P(f'  {name:20s} SUPPF {PS["SUPPF"]["e1"][k].mean():.4f} +- {PS["SUPPF"]["e1"][k].std(ddof=1):.4f}  SKR01 {PS["SKR01"]["e1"][k].mean():.4f} +- '
      f'{PS["SKR01"]["e1"][k].std(ddof=1):.4f} | d {r[0]:+.6f} (thr {r[1]:.6f}) {r[2]}; margin d - thr {r[0] - r[1]:+.6f}')
for a in ARMS:
    P(f'    per seed {a}: E1 relF1@2 ' + ' / '.join(f'{v:.4f}' for v in PS[a]['e1']['relF1']) + ' | test inactive (50) '
      + ' / '.join(f'{v:.4f}' for v in PS[a]['t50']['inact']) + ' | test relP@2 (50) ' + ' / '.join(f'{v:.4f}' for v in PS[a]['t50']['relP'])
      + ' | test relP@2 (49) ' + ' / '.join(f'{v:.4f}' for v in PS[a]['t49']['relP']))
g1 = [PS['SKR01'][s]['inact'].mean() - PS['SUPPF'][s]['inact'].mean() for s in ('t50', 't49')]
G1 = all(v <= -0.015 for v in g1)
P(f'  G1 test inactive IoU d: all 50 {g1[0]:+.6f}, clean 49 {g1[1]:+.6f}; trip iff <= -0.015 in both sets -> {"TRIP" if G1 else "ok"}')
drp = PS['SKR01']['t50']['relP'].mean() - PS['SUPPF']['t50']['relP'].mean()
fpx = {a: X[a]['ext'][:, free, 1].sum(1) for a in ARMS}
ratio = fpx['SKR01'].mean() / fpx['SUPPF'].mean()
G2t, G2e = drp < -0.03, fpx['SKR01'].mean() > 1.5 * fpx['SUPPF'].mean()
P(f'  G2 test arm: relP@2 d (all 50) {drp:+.6f} ({PS["SUPPF"]["t50"]["relP"].mean():.4f} -> {PS["SKR01"]["t50"]["relP"].mean():.4f}); '
  f'trip iff < -0.03 -> {"TRIP" if G2t else "ok"}')
P(f'  G2 E1 arm: crack px on the 74 crack-free cells, seed means SKR01 {fpx["SKR01"].mean():.1f} vs fresh SUPPF {fpx["SUPPF"].mean():.1f} '
  f'= x{ratio:.4f}; bar 1.5 x = {1.5 * fpx["SUPPF"].mean():.1f} px (ruling 1); fixed s5-9 bar 5,896 px decides nothing -> {"TRIP" if G2e else "ok"}')
P(f'    per seed crack-free px SUPPF ' + ' / '.join(f'{v:.0f}' for v in fpx['SUPPF']) + ' | SKR01 ' + ' / '.join(f'{v:.0f}' for v in fpx['SKR01']))
G2 = G2t or G2e
for mode, ix in (('two-set rule', 0), ('one set alone may label', 1)):
    nb, nw = sum(v[ix] == 'BETTER' for v in LAB.values()), sum(v[ix] == 'WORSE' for v in LAB.values())
    vr = 'FAIL' if (nw or G1 or G2) else ('PASS' if nb else 'n.d.')
    P(f'  verdict R from the 5 m0 co-primaries + guards ({mode}): {nb} BETTER, {nw} WORSE, G1 {"TRIP" if G1 else "ok"}, G2 {"TRIP" if G2 else "ok"} -> {vr} '
      f'(the 2 B5 co-primaries are not in this script; with a guard tripped they cannot change FAIL)')

# ---------------------------------------------------------------- 2 named claim, condition 1
P('\n## 2 named claim, condition 1: seed-aware two-stage bootstrap of E1 relF1@2 (10 fresh singles)')
cl = sorted({MOD(s) for s in EXT})
ci_ = np.array([cl.index(MOD(s)) for s in EXT])
CS = {a: np.stack([np.stack([X[a]['ext'][i][ci_ == j].sum(0) for j in range(len(cl))]) for i in range(5)]) for a in ARMS}  # run x cluster x K


def two_stage(seed, nb=NB, order='registered'):
    rng = np.random.default_rng(seed)
    n = len(cl)
    o = np.empty(nb)
    for t in range(nb):
        if order == 'registered':  # clusters, then SUPPF runs, then SKR01 runs
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            sa = rng.integers(0, 5, 5)
            sb = rng.integers(0, 5, 5)
        else:  # another order of the same three draws (runs first): a stream check, not the registered CI
            sb = rng.integers(0, 5, 5)
            sa = rng.integers(0, 5, 5)
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        fa = np.einsum('c,rck->rk', w, CS['SUPPF'][sa])
        fb = np.einsum('c,rck->rk', w, CS['SKR01'][sb])
        o[t] = met(fb)['relF1'].mean() - met(fa)['relF1'].mean()
    return o


pt = PS['SKR01']['e1']['relF1'].mean() - PS['SUPPF']['e1']['relF1'].mean()
v = two_stage(0)
lo, hi = np.percentile(v, [2.5, 97.5])
P(f'  registered form (seed 0, 2,000): estimate {pt:+.4f}, 95% CI [{lo:+.6f}, {hi:+.6f}], P(d > 0) {np.mean(v > 0):.4f}; '
  f'wholly above 0: {bool(lo > 0)}')
los = []
for s in list(range(1, 21)) + [20261102]:
    los.append(np.percentile(two_stage(s), 2.5))
P(f'  stream check, registered order, seeds 1..20 and 20261102: lower bound min {min(los):+.4f} max {max(los):+.4f}; above 0 in {sum(x > 0 for x in los)} of {len(los)}')
v2 = two_stage(0, order='other')
P(f'  stream check, other draw order, seed 0: [{np.percentile(v2, 2.5):+.4f}, {np.percentile(v2, 97.5):+.4f}]')

# ---------------------------------------------------------------- 3 verdict D
P('\n## 3 verdict D (E-SKR2\' vs E-SUPPF\', both at b 0)')
DJ = {}
for nm, fn, mem, rev in (('E-SUPPF', 'E-SUPPF.b0.json', 'SUPPF', 'e544133'), ('E-SKR2', 'E-SKR2.b0.json', 'SKR01', 'c9bbb02')):
    j = json.load(open(RAW_D / fn))
    assert j['members'] == [f'{ARMS[mem]}{k}' for k in SEEDS] and j['step'] == 20000 and float(j['bias']) == 0.0, fn
    assert j['code_revision'] == rev and j['model_code_revision'] == 'e544133', fn
    for sp in ('test', 'val', 'ext'):
        assert sorted(j['cells'][sp]) == REAL[sp], (fn, sp)
    DJ[nm] = j
    P(f'  {nm}: members {j["members"][0]} .. {j["members"][-1]} (5), bias {j["bias"]}, step 20000, model code {j["model_code_revision"]}; '
      f'test / val / E1 stems = the real lists')
XD = {nm: {sp: np.stack([vec(DJ[nm]['cells'][sp][s]) for s in REAL[sp]]) for sp in ('test', 'ext')} for nm in DJ}
for sp in ('test', 'ext'):
    assert (XD['E-SUPPF'][sp][:, [2, 5, 9, 10]] == XD['E-SKR2'][sp][:, [2, 5, 9, 10]]).all()
    assert (XD['E-SUPPF'][sp][:, [2, 5, 9, 10]] == X['SUPPF'][sp][0][:, [2, 5, 9, 10]]).all()
KEYS = ('crack', 'relF1', 'inact', 'anyhit', 'relP')


def boot(A, B, groups=None, nb=NB, seed=0):
    if groups is not None:
        gs = sorted(set(groups))
        gi = np.array([gs.index(g) for g in groups])
        A = np.stack([A[gi == i].sum(0) for i in range(len(gs))])
        B = np.stack([B[gi == i].sum(0) for i in range(len(gs))])
    n = len(A)
    ma, mb = met(A.sum(0)), met(B.sum(0))
    full = {k: float(mb[k] - ma[k]) for k in KEYS}
    rng = np.random.default_rng(seed)
    D = {k: np.empty(nb) for k in KEYS}
    for t in range(nb):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        ma, mb = met(w @ A), met(w @ B)
        for k in KEYS:
            D[k][t] = mb[k] - ma[k]
    return {k: dict(d=full[k], lo=float(np.percentile(D[k], 2.5)), hi=float(np.percentile(D[k], 97.5)), draws=D[k]) for k in KEYS}, n


A, B = XD['E-SUPPF'], XD['E-SKR2']
r50, n50 = boot(A['test'], B['test'])
r49, n49 = boot(A['test'][clean], B['test'][clean])
re1, ne1 = boot(A['ext'], B['ext'], groups=[MOD(s) for s in EXT])
assert (n50, n49, ne1) == (50, 49, 71)
PRIM = {}
for name, k in (('test crack IoU', 'crack'), ('test crack relF1@2', 'relF1'), ('test inactive IoU', 'inact')):
    a, c = r50[k], r49[k]
    pas = (a['lo'] > 0 and c['lo'] > 0) or (a['lo'] > 0 and c['d'] > 0) or (c['lo'] > 0 and a['d'] > 0)
    fail = a['hi'] < 0 or c['hi'] < 0
    PRIM[name] = 'pass' if pas else ('fail' if fail else 'n.d.')
    P(f'  {name:20s} all 50 d {a["d"]:+.4f} [{a["lo"]:+.4f}, {a["hi"]:+.4f}] | clean 49 d {c["d"]:+.4f} [{c["lo"]:+.4f}, {c["hi"]:+.4f}] -> {PRIM[name]}')
for name, k in (('E1 crack relF1@2', 'relF1'), ('E1 any-hit', 'anyhit')):
    a = re1[k]
    PRIM[name] = 'pass' if a['lo'] > 0 else ('fail' if a['hi'] < 0 else 'n.d.')
    P(f'  {name:20s} d {a["d"]:+.4f} [{a["lo"]:+.6f}, {a["hi"]:+.6f}] (71 clusters) -> {PRIM[name]}')
ah = re1['anyhit']['draws']
srt = np.sort(ah)
P(f'    E1 any-hit hits {int(A["ext"][:, 11].sum())} -> {int(B["ext"][:, 11].sum())} of {int(A["ext"][:, 10].sum())}; draws below 0 {int((ah < 0).sum())}, '
  f'exactly 0 {int((ah == 0).sum())}, above 0 {int((ah > 0).sum())}; sorted draws [49] {srt[49]!r} [50] {srt[50]!r}; lower bound == 0.0: {bool(re1["anyhit"]["lo"] == 0.0)}; '
  f'lower bound > 0: {bool(re1["anyhit"]["lo"] > 0)}')
fa, fb = A['ext'][free, 1].sum(), B['ext'][free, 1].sum()
GD = {'G2a': r50['relP']['d'] < -0.03, 'G2b': fb > 1.5 * fa, 'G1t': r50['inact']['d'] <= -0.015 and r49['inact']['d'] <= -0.015, 'G1e': re1['inact']['hi'] < 0}
P(f'  G2a test relP@2 d (all 50) {r50["relP"]["d"]:+.4f} ({float(met(A["test"].sum(0))["relP"]):.4f} -> {float(met(B["test"].sum(0))["relP"]):.4f}); trip iff < -0.03 -> {"TRIP" if GD["G2a"] else "ok"}')
P(f'  G2b E1 crack px on the 74 crack-free cells {fb:.0f} vs {fa:.0f} = x{fb / fa:.4f}; bar {1.5 * fa:.1f} px -> {"TRIP" if GD["G2b"] else "ok"}')
P(f'  G1t test inactive IoU d: all 50 {r50["inact"]["d"]:+.6f}, clean 49 {r49["inact"]["d"]:+.6f}; trip iff <= -0.015 in both sets -> {"TRIP" if GD["G1t"] else "ok"}')
P(f'  G1e E1 inactive IoU d {re1["inact"]["d"]:+.4f}, cluster CI [{re1["inact"]["lo"]:+.4f}, {re1["inact"]["hi"]:+.4f}]; trip iff wholly below 0 -> {"TRIP" if GD["G1e"] else "ok"}')
npass = [k for k, v_ in PRIM.items() if v_ == 'pass']
nfail = [k for k, v_ in PRIM.items() if v_ == 'fail']
trips = [k for k, v_ in GD.items() if v_]
VD = 'FAIL' if (nfail or trips) else ('PASS' if npass else 'n.d.')
P(f'  verdict D: passing {npass or "-"}; failing {nfail or "-"}; guards tripped {trips or "-"} -> {VD}')
PRIM2 = dict(PRIM)
if re1['anyhit']['lo'] >= 0:
    PRIM2['E1 any-hit'] = 'pass'
np2 = [k for k, v_ in PRIM2.items() if v_ == 'pass']
P(f'  other reading (a bound of exactly 0 counted as above 0): passing {np2}; verdict D {"FAIL" if (nfail or trips) else "PASS"}')

# ---------------------------------------------------------------- 4 checks behind rulings (c) and (d)
P('\n## 4 checks of reported statements (no bar or set changed; none of this is a verdict)')
i_n = TEST.index(NOISY)
P(f'  noisy cell {NOISY}: GT crack px {int(X["SUPPF"]["test"][0][i_n, 2])}; predicted crack px per run SUPPF '
  + ' / '.join(f'{int(v_)}' for v_ in X['SUPPF']['test'][:, i_n, 1]) + ' | SKR01 ' + ' / '.join(f'{int(v_)}' for v_ in X['SKR01']['test'][:, i_n, 1])
  + f' | E-SUPPF\' {int(A["test"][i_n, 1])}, E-SKR2\' {int(B["test"][i_n, 1])}')
s13 = SEEDS.index(13)
tot13 = X['SKR01']['test'][s13][:, 1].sum()
P(f'  SKR01 s13: share of its test crack px on that cell {X["SKR01"]["test"][s13][i_n, 1] / tot13:.3f}; relP@2 all 50 {PS["SKR01"]["t50"]["relP"][s13]:.4f}, '
  f'clean 49 {PS["SKR01"]["t49"]["relP"][s13]:.4f}')
P(f'  cells of module {MOD(NOISY)} in test: {[s for s in TEST if MOD(s) == MOD(NOISY)]}')
d49 = PS['SKR01']['t49']['relP'].mean() - PS['SUPPF']['t49']['relP'].mean()
keep4 = [i for i in range(5) if i != s13]
dno13 = PS['SKR01']['t50']['relP'][keep4].mean() - PS['SUPPF']['t50']['relP'].mean()
P(f'  relP@2 d on the clean 49 {d49:+.4f}; all 50 without SKR01 s13 {dno13:+.4f} (the guard is registered on all 50 with all 5 seeds: {drp:+.4f})')
P('  guards over the 10 leave-one-seed-out drops (G1 d50 / d49, G2 relP d, E1 px ratio):')
nfail_drops = 0
for arm in ARMS:
    for i, k in enumerate(SEEDS):
        kp = [q for q in range(5) if q != i]
        sel = {a: (kp if a == arm else list(range(5))) for a in ARMS}
        a50 = PS['SKR01']['t50']['inact'][sel['SKR01']].mean() - PS['SUPPF']['t50']['inact'][sel['SUPPF']].mean()
        a49 = PS['SKR01']['t49']['inact'][sel['SKR01']].mean() - PS['SUPPF']['t49']['inact'][sel['SUPPF']].mean()
        rp = PS['SKR01']['t50']['relP'][sel['SKR01']].mean() - PS['SUPPF']['t50']['relP'][sel['SUPPF']].mean()
        rt = fpx['SKR01'][sel['SKR01']].mean() / fpx['SUPPF'][sel['SUPPF']].mean()
        t1, t2 = (a50 <= -0.015 and a49 <= -0.015), (rp < -0.03 or rt > 1.5)
        nfail_drops += bool(t1 or t2)
        P(f'    without {arm} s{k}: G1 {a50:+.4f} / {a49:+.4f} {"TRIP" if t1 else "ok"} | G2 {rp:+.4f}, x{rt:.3f} {"TRIP" if t2 else "ok"}')
P(f'  a guard trips in {nfail_drops} of 10 seed drops')
tp = {a: X[a]['test'][:, :, 3].sum(1).mean() for a in ARMS}
fp_ = {a: (X[a]['test'][:, :, 4] - X[a]['test'][:, :, 3]).sum(1).mean() for a in ARMS}
gt_in = X['SUPPF']['test'][0][:, 5]
P(f'  test inactive: GT px {int(gt_in.sum())} in {int((gt_in > 0).sum())} of 50 cells; n_eff cells {gt_in.sum() ** 2 / (gt_in ** 2).sum():.1f}; '
  f'seed-mean true positives SUPPF {tp["SUPPF"]:.0f} -> SKR01 {tp["SKR01"]:.0f}; inactive predicted on other GT {fp_["SUPPF"]:.0f} -> {fp_["SKR01"]:.0f}')

# ---------------------------------------------------------------- 5 the same guards under other readings of the text
P('\n## 5 guards under other readings of the text (the registered form is section 1 / 3; nothing here replaces it)')
pool = {a: {'t50': met(X[a]['test'].sum((0, 1))), 't49': met(X[a]['test'][:, clean].sum((0, 1)))} for a in ARMS}
p50, p49 = [float(pool['SKR01'][s]['inact'] - pool['SUPPF'][s]['inact']) for s in ('t50', 't49')]
prp = float(pool['SKR01']['t50']['relP'] - pool['SUPPF']['t50']['relP'])
P(f'  R, counts pooled over the 5 seeds instead of seed means: G1 {p50:+.4f} / {p49:+.4f} -> {"TRIP" if (p50 <= -0.015 and p49 <= -0.015) else "ok"}; '
  f'G2 relP@2 (all 50) {prp:+.4f} -> {"TRIP" if prp < -0.03 else "ok"}')
P(f'  R, G2 E1 arm against the fixed s5-9 bar 5,896 px (reference line of ruling 1): SKR01 mean {fpx["SKR01"].mean():.1f} -> {"TRIP" if fpx["SKR01"].mean() > 5896 else "ok"}')
ra, rb = met(A['test'][clean].sum(0)), met(B['test'][clean].sum(0))
P(f'  D, G2a on the clean 49 (3b names no set; all 50 is the frozen scorer\'s and SKR2E\'s form): relP@2 d {float(rb["relP"] - ra["relP"]):+.4f} -> '
  f'{"TRIP" if float(rb["relP"] - ra["relP"]) < -0.03 else "ok"}')
ti = r50['inact']['draws']
P(f'  D, test inactive primary, all 50: draws above 0 {int((ti > 0).sum())} of {NB} (upper bound {r50["inact"]["hi"]:+.6f}); '
  f'clean 49: {int((r49["inact"]["draws"] > 0).sum())} of {NB} (upper bound {r49["inact"]["hi"]:+.6f})')
P(f'  SKR01 test relP@2 (all 50) seed sd {PS["SKR01"]["t50"]["relP"].std(ddof=1):.4f}, SUPPF {PS["SUPPF"]["t50"]["relP"].std(ddof=1):.4f} '
  f'(S2 3c calibrated G2\'s "null trip ~0" on a seed sd of 0.0015)')
if out_path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(LINES) + '\n')
