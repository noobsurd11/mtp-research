"""HC mechanism readout on SHV1 (protocol_HC.md v1.1 §4 mechanism kill, §5 readouts). DRAFT (runner's helper, 1 Nov 2026) for coach's
review and FREEZE. CPU only; reads el_metrics records (val = V0, the 54 val cells; synval = SHV1, 108 synthetic half-cut val images,
MANIFEST 63dd5469); val-derived data only (no test, no E1).
Definitions (calib's routing pre-check, routing_precheck.py 06a3ad30, judge-reproduced; el_metrics superset f40a0efe imported):
  pooled per arm   = E.pool_cells over the arm's 5 seeds (counts summed before any ratio), as the pre-check's "SUPPF5 pooled"
  oracle b         = E.oracle_b_relf1: OPGRID b (-4..+12 step 0.1) with the highest pooled relF1@2; ties -> smaller b
  matched relR@2   = max relR@2 over E.GRID (-4..+12 step 0.1 plus 0.75) with relP@2 >= 0.90 (routing_precheck.matched, unchanged)
  MECHANISM (kill) = matched SHV1 relR@2 (pooled), HC - SUPPF < +0.05 -> "mechanism FAILED" (protocol_HC §4)
Reported (never decide): oracle b on V0 / SHV1 / SHV1-p and the bias gaps; relR@2, relP@2, pixel recall at b 0 (and at the deployed b for
refs); matched relR@2 on V0 and SHV1-p (80 images, shv1p_stems_eval.txt 7f651fc7); per-seed values; refs (FINAL: calib's existing records).
Usage: python hc_shv1_read.py --el-metrics DIR --rec DIR --arm SUPPF RUN.. --arm HC RUN.. --base SUPPF --test HC --shv1p LIST \
         [--ref NAME VAL.json SYN.json BDEP] --out OUT.json
       python hc_shv1_read.py --selftest --el-metrics DIR --st-val CALIB/out/rec --st-syn CALIB/out/rec_shv1
         (reproduces the routing pre-check's published values from calib's records: FINAL b_V0 +1.1, b_SHV1 +1.5, matched relR@2
          V0 0.892 / SHV1 0.730; SUPPF s0-4 pooled +2.9, +3.8, 0.876 / 0.694; at the published precision; exit 0 iff all 8 match)
"""
import argparse, hashlib, json, sys
from pathlib import Path

import numpy as np

MD5 = {'el_metrics.py': 'f40a0efe0baa8f3ce419f0c55a70442e', 'shv1p': '7f651fc7348f4dcaa06d404645fa1951'}
ap = argparse.ArgumentParser()
ap.add_argument('--el-metrics', required=True, help='dir holding calib el_metrics.py f40a0efe (synval-capable superset)')
ap.add_argument('--rec'); ap.add_argument('--arm', nargs='+', action='append', default=[], metavar='NAME RUN')
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--test', default='HC')
ap.add_argument('--ref', nargs=4, action='append', default=[], metavar=('NAME', 'VAL', 'SYN', 'BDEP'))
ap.add_argument('--shv1p'); ap.add_argument('--kill', type=float, default=0.05); ap.add_argument('--ptarget', type=float, default=0.90)
ap.add_argument('--out'); ap.add_argument('--selftest', action='store_true'); ap.add_argument('--st-val'); ap.add_argument('--st-syn')
a = ap.parse_args()
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(Path(a.el_metrics) / 'el_metrics.py') == MD5['el_metrics.py'], 'el_metrics.py md5 != f40a0efe'
sys.path.insert(0, a.el_metrics)
import el_metrics as E  # noqa: E402

G = E.GRID
J = lambda b: int(np.argmin(np.abs(G - b)))
ld = lambda p: json.load(open(p))


def matched(c, x):  # routing_precheck.matched (06a3ad30), plus the b where the max is reached (first = smallest b)
    ok = np.where(np.nan_to_num(c['relP'], nan=-1) >= x)[0]
    if not len(ok):
        return {'relR': float('nan'), 'b': float('nan'), 'reachable': False}
    i = ok[int(np.argmax(c['relR'][ok]))]
    return {'relR': float(c['relR'][i]), 'b': float(G[i]), 'reachable': True}


def at(c, b):
    j = J(b)
    return {k: float(c[k][j]) for k in ('relR', 'relP', 'R', 'P', 'IoU')} | {'b': float(G[j])}


def readout(vrecs, srecs, bdep=0.0, pstems=None):
    V = E.pool_cells(vrecs, 'val'); S = E.pool_cells(srecs, 'synval')
    cV, cS = E.curves(V), E.curves(S)
    oV, oS = E.oracle_b_relf1(V), E.oracle_b_relf1(S)
    r = {'n_runs': len(vrecs), 'n_V0': len(V), 'n_SHV1': len(S),
         'V0': {'oracle_b': oV, 'matched_relR': matched(cV, a.ptarget), 'at_b0': at(cV, 0.0), 'at_bdep': at(cV, bdep)},
         'SHV1': {'oracle_b': oS, 'matched_relR': matched(cS, a.ptarget), 'at_b0': at(cS, 0.0), 'at_bdep': at(cS, bdep)},
         'bias_gap_SHV1_minus_V0': oS['b'] - oV['b']}
    if pstems is not None:
        Sp = [k for k in S if k.split(':', 1)[1] in pstems]
        assert len(Sp) == len(pstems) * len(srecs), ('SHV1-p', len(Sp))
        cSp = E.curves(S, Sp); oSp = E.oracle_b_relf1(S, Sp)
        r['SHV1p'] = {'n': len(Sp), 'oracle_b': oSp, 'matched_relR': matched(cSp, a.ptarget), 'at_b0': at(cSp, 0.0)}
        r['bias_gap_SHV1p_minus_V0'] = oSp['b'] - oV['b']
    return r


if a.selftest:
    sv, ss = Path(a.st_val), Path(a.st_syn)
    exp = {'FINAL': (1.1, 1.5, 0.892, 0.730), 'SUPPF5 pooled s0-4': (2.9, 3.8, 0.876, 0.694)}
    got = {'FINAL': readout([ld(sv / 'FINAL.val.json')], [ld(ss / 'FINAL.synval.json')], 0.75),
           'SUPPF5 pooled s0-4': readout([ld(sv / f'SUPPF5_m{k}.val.json') for k in range(5)], [ld(ss / f'SUPPF5_m{k}.synval.json') for k in range(5)])}
    ok = True
    for k, (bv, bs, mv, ms) in exp.items():
        g = got[k]
        t = (round(g['V0']['oracle_b']['b'], 1) == bv, round(g['SHV1']['oracle_b']['b'], 1) == bs,
             round(g['V0']['matched_relR']['relR'], 3) == mv, round(g['SHV1']['matched_relR']['relR'], 3) == ms)
        ok &= all(t)
        print(f"selftest {k}: b_V0 {g['V0']['oracle_b']['b']:+.1f} (exp {bv:+.1f}) {t[0]} | b_SHV1 {g['SHV1']['oracle_b']['b']:+.1f} (exp {bs:+.1f}) {t[1]} | "
              f"matched relR@2 V0 {g['V0']['matched_relR']['relR']:.3f} (exp {mv:.3f}) {t[2]} | SHV1 {g['SHV1']['matched_relR']['relR']:.3f} (exp {ms:.3f}) {t[3]}")
    print('SELFTEST', 'PASS' if ok else 'FAIL', '(routing pre-check values reproduced from calib records)')
    sys.exit(0 if ok else 1)

assert md5(a.shv1p) == MD5['shv1p'], 'shv1p_stems_eval.txt md5 != 7f651fc7'
P = {l.strip() for l in open(a.shv1p) if l.strip()}; assert len(P) == 80, len(P)
arms = {x[0]: x[1:] for x in a.arm}; assert {a.base, a.test} <= set(arms) and all(len(v) == 5 for v in arms.values()), arms
R = Path(a.rec); out = {'label': 'protocol_HC §4-5 SHV1 mechanism readout (val-derived only; no test, no E1)', 'ptarget': a.ptarget,
                        'kill': a.kill, 'arms': {}, 'per_seed': {}, 'refs': {}, 'selfcheck_val': {},
                        'md5': {'el_metrics.py': MD5['el_metrics.py'], 'shv1p': MD5['shv1p'], 'this_file': md5(__file__)}}
for name, runs in arms.items():
    vr, sr = [ld(R / f'{r}.val.json') for r in runs], [ld(R / f'{r}.synval.json') for r in runs]
    assert all(x['set'] == 'val' and len(x['cells']) == 54 for x in vr) and all(x['set'] == 'synval' and len(x['cells']) == 108 for x in sr)
    assert set(P) <= set(sr[0]['cells']), 'SHV1-p stems not in SHV1'
    out['arms'][name] = readout(vr, sr, 0.0, P)
    out['per_seed'][name] = {r: readout([v], [s], 0.0, P) for r, v, s in zip(runs, vr, sr)}
    out['selfcheck_val'][name] = {r: E._sc_status(R / f'{r}.val.json') for r in runs}
for name, v, s, b in a.ref:
    out['refs'][name] = readout([ld(v)], [ld(s)], float(b), P) | {'inputs': {v: md5(v), s: md5(s)}, 'bdep': float(b)}
mt, mb = out['arms'][a.test]['SHV1']['matched_relR']['relR'], out['arms'][a.base]['SHV1']['matched_relR']['relR']
d = mt - mb
reading = ('UNDEFINED (relP@2 >= 0.90 unreachable on SHV1 for an arm): coach decides' if np.isnan(d)
           else (f'mechanism FAILED ({a.test} - {a.base} < +{a.kill})' if d < a.kill else f'mechanism gain >= +{a.kill} (not failed)'))
out['mechanism'] = {'test': a.test, 'base': a.base, 'matched_SHV1_relR_test': mt, 'matched_SHV1_relR_base': mb, 'delta': d, 'reading': reading,
                    'reported_SHV1p_delta': out['arms'][a.test]['SHV1p']['matched_relR']['relR'] - out['arms'][a.base]['SHV1p']['matched_relR']['relR'],
                    'reported_V0_delta': out['arms'][a.test]['V0']['matched_relR']['relR'] - out['arms'][a.base]['V0']['matched_relR']['relR']}
L = ['## SHV1 mechanism readout (protocol_HC §4-5); val-derived only; pooled over the 5 seeds per arm; refs = calib records',
     'row | V0 oracle b | SHV1 oracle b | gap | SHV1-p oracle b | matched relR@2 (relP>=0.90) V0 / SHV1 / SHV1-p | SHV1 at b0 relR relP R']
for name, r in list(out['arms'].items()) + list(out['refs'].items()):
    L.append(f"{name} | {r['V0']['oracle_b']['b']:+.1f} | {r['SHV1']['oracle_b']['b']:+.1f} | {r['bias_gap_SHV1_minus_V0']:+.1f} | "
             f"{r['SHV1p']['oracle_b']['b']:+.1f} | {r['V0']['matched_relR']['relR']:.4f} / {r['SHV1']['matched_relR']['relR']:.4f} / "
             f"{r['SHV1p']['matched_relR']['relR']:.4f} | {r['SHV1']['at_b0']['relR']:.4f} {r['SHV1']['at_b0']['relP']:.4f} {r['SHV1']['at_b0']['R']:.4f}")
for name in arms:
    L.append(f'{name} per seed, matched SHV1 relR@2: ' + ' '.join(f"{v['SHV1']['matched_relR']['relR']:.4f}" for v in out['per_seed'][name].values())
             + ' | SHV1 oracle b: ' + ' '.join(f"{v['SHV1']['oracle_b']['b']:+.1f}" for v in out['per_seed'][name].values()))
    L.append(f'{name} val records self-check vs m0 (cpu profile, reported): {out["selfcheck_val"][name]}')
L.append(f"MECHANISM: matched SHV1 relR@2 {a.test} {mt:.4f} - {a.base} {mb:.4f} = {d:+.4f} -> {reading}")
L.append(f"(reported) SHV1-p delta {out['mechanism']['reported_SHV1p_delta']:+.4f}; V0 delta {out['mechanism']['reported_V0_delta']:+.4f}")
print('\n'.join(L))
if a.out:
    json.dump(out, open(a.out, 'w'), indent=1)
