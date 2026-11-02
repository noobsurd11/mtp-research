"""SKR2 + HC2 F51 / H36 readout and guard G3 (protocol_SKR2_HC2 v1.0.1 §3c G3, §4): F51 crack AP, ARM - SUP100-PF, paired
module-cluster bootstrap over F51's 36 modules (2,000 resamples, rng seed 0); G3 (HC2 only, --decide): FAIL iff the upper end
(97.5th percentile) < 0. SKR2 and the reference arm (HC p 0.35, opened) are reported. DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE.
From hc_f51.py (c9b4bdec, frozen HC): verdict(), selftest(), the loader and gt_keep() kept; changed: arms are '--arm NAME DUMP_DIR
REC_DIR RUN x5' (SUPPF and HC read from the HC opening's syn_work dumps / post records, new runs from this opening's), one rule() call
per test / reference arm vs --base, FA px also at b 0 (protocol §4), output keyed by arm ('contrasts'), G3 block.
CPU only. Reads calib-format dumps (val, rf) and el_metrics f40a0efe records (val, rf); no test, no E1.
Reuse: found's a8_screen_score.py (8eba76e5, imported from --a8, NOT modified): cell_hist (1,000-bin p(crack) histograms), binned_ap
and rule() (per-run AP, arm means, the paired module bootstrap with rng seed 0, boot_hi = 97.5th percentile, per-module dAP, sign
count, FA px on crack-free H36 / F51 cells at each run's val b_rel). rule() keys its arms "A8" / "A8c": here A8 := the test arm,
A8c := SUPPF. Its terms 1a / 1b / 2 / 3 are the A8 screen's GO terms, NOT s2 terms: stored under "a8_terms_not_used".
G3 (HC2): FAIL iff boot_hi < 0 (boot_hi = 97.5th percentile of the 2,000 resampled HC2 - SUPPF F51 AP differences). Reported: d, boot
lo / hi, per-run AP on F51 / H36 / F19 / val, cell AUROC, FA px at val b_rel and at b 0 (H36 = the 36 half-cut cells, 19 crack-free;
F51 crack-free 34), inactive IoU at b_rel, sign count. b_rel from el_metrics f40a0efe choose_op (OPGRID -4..+12).
--check-ref HC <HC opening f51/hc_f51.json> 349c3d90...: the HC reference contrast (same dumps, records, modules, seed 0) must equal
the frozen HC opening's d / boot_hi / fail exactly; exit 3 if not (JSON still written; the G3 numbers are then for coach to judge).
Usage: python s2_f51.py --a8 found/a8_screen_score.py --el-metrics calib_syn --arm SUPPF DUMP REC RUN x5 --arm HC2 DUMP REC RUN x5 \
         --arm SKR01 ... [--arm HC ...] --base SUPPF --test HC2 SKR01 --decide HC2 [--ref HC] [--check-ref HC HC_POST/f51/hc_f51.json MD5] \
         --code /home/noob/work/el_f3 \
         --rf /home/noob/work/calib/data/rf --rf-sets /home/noob/work/found/t9/rf_sets.tsv --out OUT.json
       python s2_f51.py --selftest --a8 ... --el-metrics ...   (synthetic: a8's own selftest + the verdict wiring; reads no data)
"""
from __future__ import annotations

import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

import numpy as np

MD5 = {'a8_screen_score.py': '8eba76e5bb0783e9d4ecc432dea4a785', 'el_metrics.py': 'f40a0efe0baa8f3ce419f0c55a70442e',
       'rf_sets.tsv': '14771356ef7c99f567c5f80dad2e48dd', 'rf_stems': '3a65c2fb0ecaf32e91377d4ad249029a'}
ap = argparse.ArgumentParser()
ap.add_argument('--a8', required=True); ap.add_argument('--el-metrics', required=True); ap.add_argument('--out')
ap.add_argument('--arm', nargs='+', action='append', default=[], metavar='NAME DUMP REC RUN')
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--test', nargs='+', default=[]); ap.add_argument('--decide', default=None)
ap.add_argument('--ref', nargs='*', default=[])
ap.add_argument('--code', default='/home/noob/work/el_f3'); ap.add_argument('--rf', default='/home/noob/work/calib/data/rf')
ap.add_argument('--rf-sets', default='/home/noob/work/found/t9/rf_sets.tsv'); ap.add_argument('--boot', type=int, default=2000)
ap.add_argument('--selftest', action='store_true')
ap.add_argument('--check-ref', nargs=3, metavar=('NAME', 'HC_F51_JSON', 'MD5'), help='the reference contrast must equal the frozen HC opening (exact)')
a = ap.parse_args()
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(a.a8) == MD5['a8_screen_score.py'], 'a8_screen_score.py md5 != 8eba76e5'
assert md5(Path(a.el_metrics) / 'el_metrics.py') == MD5['el_metrics.py'], 'el_metrics.py md5 != f40a0efe'
spec = importlib.util.spec_from_file_location('a8_screen_score', a.a8); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
sys.path.insert(0, a.el_metrics)
from el_metrics import GRID, choose_op, curves  # noqa: E402  (OP grid -4..+12 step 0.1, as a8_score.sh's frozen import)


def verdict(res):  # hc_f51.verdict, labels generalised (HC -> the test arm)
    d = res['arms']['A8']['F51']['crack_ap'] - res['arms']['A8c']['F51']['crack_ap']
    hi = float(res['boot_hi']); lo = res['terms']['1b_F51_module_boot_lo>0'][0]
    return {'d_F51_crack_ap': float(d), 'boot_lo_2p5_rounded4': lo, 'boot_hi_97p5': hi,
            'verdict': 'FAIL (upper 95% bound < 0: worse on F51)' if hi < 0 else 'guard passed (upper 95% bound >= 0)', 'fail': bool(hi < 0)}


def selftest():  # hc_f51.selftest, unchanged except the d key name
    A.selftest()  # found's own synthetic test of rule() (prints SELFTEST OK)
    CR = A.CR
    stems = [f'CSIR_{100 + m:05d}_r{c}_c1_rf' for m in range(12) for c in range(3)]
    sets = {'F51': stems[:24], 'H36': stems[24:30], 'F19': stems[30:33], 'val': stems[33:]}
    modules = {s: '_'.join(s.split('_')[:2]) for s in stems}
    gts = {}
    for i, s in enumerate(stems):
        g = np.zeros((64, 64), np.uint8)
        if i % 3 == 0:
            g[20:22, 4:60] = CR
        gts[s] = g

    def maps(sep, seed):
        r = np.random.default_rng(seed); o = {}
        for s in stems:
            z = r.normal(-3, 1, (64, 64)); z[gts[s] == CR] += sep; o[s] = 1 / (1 + np.exp(-z))
        return o
    keep = np.ones((64, 64), bool)
    H = {f'{n}_s{k}': {s: A.cell_hist(m[s], gts[s], keep) for s in stems}
         for n, sep in (('good', 4.0), ('bad', 1.0)) for k in (0, 1) for m in [maps(sep, 7 + k)]}
    fa = {r: {'H36': 0.0, 'F51': 0.0} for r in H}
    good, bad = ['good_s0', 'good_s1'], ['bad_s0', 'bad_s1']
    v1 = verdict(A.rule(H, sets, modules, {'A8': good, 'A8c': bad}, fa, boot=300))   # test arm better -> not FAIL
    v2 = verdict(A.rule(H, sets, modules, {'A8': bad, 'A8c': good}, fa, boot=300))   # test arm worse  -> FAIL
    v3 = verdict(A.rule(H, sets, modules, {'A8': good, 'A8c': good}, fa, boot=300))  # identical -> d 0, hi 0, not FAIL
    ap_direct = lambda runs: np.mean([A.binned_ap(np.sum([H[r][s][0] for s in sets['F51']], 0), np.sum([H[r][s][1] for s in sets['F51']], 0)) for r in runs])
    r4 = A.rule(H, sets, modules, {'A8': good, 'A8c': bad}, fa, boot=300)
    ok = (not v1['fail'] and v1['d_F51_crack_ap'] > 0 and v2['fail'] and v3['d_F51_crack_ap'] == 0 and not v3['fail']
          and abs(v1['d_F51_crack_ap'] - (ap_direct(good) - ap_direct(bad))) < 1e-12 and r4['boot_hi'] == v1['boot_hi_97p5'])
    print('s2_f51 selftest:', {'better': v1['verdict'], 'worse': v2['verdict'], 'identical': v3['verdict']},
          '| d == direct AP difference, bootstrap reproducible (seed 0):', ok)
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if a.selftest:
    sys.exit(selftest())

from PIL import Image  # noqa: E402
assert md5(a.rf_sets) == MD5['rf_sets.tsv'] and md5(Path(a.rf) / 'stems_eval.txt') == MD5['rf_stems'], 'rf_sets / rf stems md5'
arms = {x[0]: (Path(x[1]), Path(x[2]), x[3:]) for x in a.arm}
assert a.base in arms and set(a.test) | set(a.ref) <= set(arms) - {a.base} and (a.decide is None or a.decide in a.test), (list(arms), a.test, a.ref)
assert all(len(v[2]) == 5 for v in arms.values()), 'need 5 runs per arm'
allruns = [r for v in arms.values() for r in v[2]]; assert len(set(allruns)) == len(allruns), 'a run appears in two arms'
rows = [l.rstrip('\n').split('\t') for l in open(a.rf_sets) if l.strip()][1:]
rfset = {r[0]: r[1] for r in rows}; modules = {r[0]: r[3] for r in rows}
D = Path(a.code) / 'data'; RF = Path(a.rf); GT = {}
J0 = int(np.argmin(np.abs(GRID - 0.0))); assert abs(GRID[J0]) < 1e-9


def gt_keep(sp, s):
    if (sp, s) not in GT:
        if sp == 'val':
            g = np.array(Image.open(D / 'labeled' / 'masks_escdd' / f'{s}.png')); k = np.ones(g.shape, bool)
        else:
            g = np.array(Image.open(RF / 'masks' / f'{s}.png')); k = ~(np.array(Image.open(RF / 'ignore' / f'{s}.png')) > 0)
        GT[(sp, s)] = (g, k)
    return GT[(sp, s)]


H, fa, fa0, brel, inact = {}, {}, {}, {}, {}
sets = vstems = None
for name, (dd, rd, runs) in arms.items():
    for r in runs:
        H[r] = {}
        for sp in ('val', 'rf'):
            z = np.load(dd / f'{r}.{sp}.npz'); st = [str(s) for s in z['stems']]; pcs = z['pc']
            for i, s in enumerate(st):
                g, k = gt_keep(sp, s); H[r][s] = A.cell_hist(pcs[i], g, k)
            if sp == 'rf':
                s3 = {g_: [s for s in st if rfset[s] == g_] for g_ in ('F51', 'H36', 'F19')}
                assert sets is None or s3 == sets, ('rf stems differ between runs', r); sets = s3
            else:
                assert vstems is None or st == vstems, ('val stems differ between runs', r); vstems = st
        vr = json.load(open(rd / f'{r}.val.json')); assert vr['set'] == 'val'
        op = choose_op(curves(vr['cells']), 'relR', 'relP'); brel[r] = op['b']; j = op['j']
        rr = json.load(open(rd / f'{r}.rf.json'))['cells']
        fa[r] = {g_: float(sum(rr[s]['pred'][j] for s in sets[g_] if rr[s]['n_gt'] == 0)) for g_ in ('H36', 'F51')}
        fa0[r] = {g_: float(sum(rr[s]['pred'][J0] for s in sets[g_] if rr[s]['n_gt'] == 0)) for g_ in ('H36', 'F51')}
        inact[r] = {'val': float(curves(vr['cells'])['inactIoU'][j]), **{g_: float(curves(rr, sets[g_])['inactIoU'][j]) for g_ in sets}}
assert len(vstems) == 54 and len(sets['F51']) == 51 and len(sets['H36']) == 36 and len(sets['F19']) == 19, 'set sizes'
sets['val'] = vstems
out = {'label': 'protocol_SKR2_HC2 §3c G3 + §4 F51 / H36: F51 crack AP, ARM - SUPPF, paired module-cluster bootstrap (36 modules, '
                f'{a.boot} resamples, seed 0); G3 (HC2) FAIL iff upper 95% bound < 0', 'base': a.base, 'decide': a.decide,
       'contrasts': {}, 'b_rel_val': brel, 'fa_px_crackfree_at_brel': fa, 'fa_px_crackfree_at_b0': fa0, 'inactive_iou_at_brel': inact,
       'md5': {**MD5, 'this_file': md5(__file__)}, 'argv': sys.argv}
L = []
for name in list(a.test) + list(a.ref):
    res = A.rule(H, sets, modules, {'A8': arms[name][2], 'A8c': arms[a.base][2]}, fa, boot=a.boot)
    assert res['F51_modules'] == 36, ('F51 modules', res['F51_modules'])
    v = verdict(res)
    role = 'DECISION (G3)' if name == a.decide else ('reference (opened), not a contrast' if name in a.ref else 'reported')
    m0 = lambda runs, g_: float(np.mean([fa0[r][g_] for r in runs]))
    out['contrasts'][name] = {**v, 'role': role, 'boot': a.boot, 'F51_modules': res['F51_modules'], 'F51_sign_up': res['F51_sign_up'],
                              'F51_per_module_dAP': res['F51_per_module_dAP'], 'arms': {name: res['arms']['A8'], a.base: res['arms']['A8c']},
                              'per_run': res['per_run'], 'fa_px_crackfree_at_b0_arm_means': {n: {g_: m0(arms[n][2], g_) for g_ in ('H36', 'F51')} for n in (name, a.base)},
                              'a8_terms_not_used': {'note': 'a8 screen GO terms (A8 = test arm, A8c = SUPPF here); not s2 terms', 'terms': res['terms'], 'GO': res['GO']}}
    L.append(f"[{role}] {name} - {a.base}: F51 crack AP {res['arms']['A8']['F51']['crack_ap']:.4f} vs {res['arms']['A8c']['F51']['crack_ap']:.4f} | "
             f"d {v['d_F51_crack_ap']:+.4f} | boot lo {v['boot_lo_2p5_rounded4']:+.4f} hi {v['boot_hi_97p5']:+.4f} | "
             + (v['verdict'] if name == a.decide else '(no verdict role)') + f" | sign up {res['F51_sign_up']} | 36 modules, {a.boot} resamples")
    L.append(f'  per run F51 AP: ' + ' '.join(f"{r} {res['per_run'][r]['F51']['crack_ap']:.4f}" for r in arms[name][2] + arms[a.base][2]))
    L.append(f"  FA px on crack-free cells (H36 / F51), arm means: at val b_rel {name} {[res['arms']['A8'][k]['fa_px_crackfree_at_brel'] for k in ('H36', 'F51')]} "
             f"{a.base} {[res['arms']['A8c'][k]['fa_px_crackfree_at_brel'] for k in ('H36', 'F51')]} | at b 0 {name} {[m0(arms[name][2], k) for k in ('H36', 'F51')]} "
             f"{a.base} {[m0(arms[a.base][2], k) for k in ('H36', 'F51')]}")
if a.decide:
    out['G3'] = {'arm': a.decide, **{k: out['contrasts'][a.decide][k] for k in ('d_F51_crack_ap', 'boot_hi_97p5', 'fail', 'verdict')}}
    L.append(f"G3 ({a.decide}): {out['G3']['verdict']}")
rc = 0
if a.check_ref:  # integration check on real data: same dumps / records / rng seed as hc_f51.py -> identical d and boot_hi
    n, pth, m5 = a.check_ref; assert md5(pth) == m5, (pth, 'md5')
    hj = json.load(open(pth)); c = out['contrasts'][n]
    ok = (c['d_F51_crack_ap'] == hj['HC_minus_SUPPF_F51_crack_ap'] and c['boot_hi_97p5'] == hj['boot_hi_97p5'] and c['fail'] == hj['fail'])
    out['check_ref'] = {'name': n, 'json': pth, 'md5': m5, 'equal': bool(ok)}; rc = 0 if ok else 3
    L.append(f'check: reference contrast {n} reproduces the frozen HC opening F51 result exactly (d, boot_hi, fail): {ok}')
json.dump(out, open(a.out, 'w'), indent=1, default=float)
print('\n'.join(L))
sys.exit(rc)
