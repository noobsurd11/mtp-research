"""SKR2 + HC2 guards G1-G3 (protocol_SKR2_HC2 v1.0.1 §3c; pre-registered FAIL rules; a trip FAILS that arm whatever else passes).
DRAFT (runner's helper, 2 Nov 2026) for coach's review and FREEZE. CPU only; reads m0 per-cell JSONs (test + ext cells) and the F51
pass JSON (s2_f51.py). Per-cell fields as hc_e1_coprim / m0_analyze (m0_audit d36f7438 cell_stats, read in the code): conf = bincount
(gt * 24 + pred) over keep px = 24x24 row-major GT x pred; crack_rel2 = [pred crack px within 2 px of GT, pred crack px, GT crack px
within 2 px of pred, GT crack px]; crack_cc['gt'] = [size, hit] per GT crack component (hit = px within 2 px of a prediction).
Class ids: crack 14, inactive 11 (m0_analyze CRACK / INACT).
  G1 inactive (arms in --g1; both arms): test inactive IoU per run = m0_analyze.agg(test cells, keep)["iou"][11] (pooled confusion);
     delta = mean over seeds 5-9 (arm) - mean (SUPPF), in BOTH sets: all 50, and clean = without CSIR_00070_r8_c4 (m0_analyze NOISY).
     TRIP iff delta <= -0.015 in both sets.
  G2 precision (arms in --g2; SKR2): (a) test crack relP@2 per run = agg(test, all 50)["relP2"] = sum crack_rel2[0] / sum crack_rel2[1];
     delta of seed means < -0.03 -> TRIP; OR (b) E1 crack px on crack-free cells per run = sum over the ext cells whose conf row 14 sums
     to 0 (GT crack px 0 in keep) of their conf column 14 sum (predicted crack px in keep); (seed mean arm) > 1.5 x (seed mean SUPPF)
     -> TRIP. SUPPF's seed mean must round to 3,931 (protocol §3c, judge), else exit 1 (the bar would not be the registered one).
  G3 F51 harm (--g3 ARM JSON; HC2): from s2_f51.py's JSON, contrasts[ARM]["boot_hi_97p5"] (97.5th percentile of the 2,000 paired
     36-module bootstrap ARM - SUPPF F51 crack AP differences, rng seed 0); TRIP iff < 0 (recomputed here; must equal the JSON's 'fail').
     Missing or unreadable JSON -> G3 'MISSING', exit 1 (G1 / G2 still written).
Reported only (never a verdict): per arm test pred / GT crack px, test any-hit component recall (gt comps >= 20 px, hit >= 1), test crack
  px on crack-free cells, the clean-set relP@2; E1 pred / GT and relP@2 / relR@2 (also in e1_coprim).
Exit: 0 if every requested guard was computed (tripped or not), 1 if any input is missing or an assert fails.
--selftest: wiring on opened arms vs SUPPF s5-9 (PF2 m0) with judge's numbers (judge/out/skr2hc2_check_out.txt, protocol §3c):
  HC -> G1 TRIP (-0.0228 / -0.0230), G2 relP +0.0017, x0.90 -> ok; SKR w 1.0 -> G1 TRIP (-0.0170 / -0.0161), G2 TRIP (-0.0702, x2.40);
  CLD -> G1 ok (-0.0114 / -0.0106), G2 TRIP (-0.0186, x1.53); SUPPF crack-free px per seed 3,092 / 2,718 / 5,178 / 4,179 / 4,486
  (mean 3,931), test relP@2 mean 0.9417 sd 0.0015. THIN m0 (m0_audit_b3) conf may be 25x25: its 24x24 block is used (judge's convention).
  G3 wiring on synthetic JSONs. Prints flags and these values only.
Usage: python s2_guards.py --trackm DIR --arm SUPPF M0 RUN x5 --arm SKR01 M0 RUN x5 --arm HC2 M0 RUN x5 --base SUPPF \
         --g1 SKR01 HC2 --g2 SKR01 --g3 HC2 F51.json --json OUT.json
       python s2_guards.py --selftest --trackm DIR --pf2-m0 DIR --hc-m0 DIR --thin-m0 DIR
"""
import argparse, hashlib, json, math, sys
import numpy as np

MD5 = {'m0_analyze.py': 'd5adbe6bfb84ce251f56ec7494a69663'}
NC, CR, IN, CMIN = 24, 14, 11, 20
G1_BAR, G2_RELP, G2_X, SUPPF_FREE = -0.015, -0.03, 1.5, 3931

ap = argparse.ArgumentParser()
ap.add_argument('--trackm', required=True)
ap.add_argument('--arm', nargs='+', action='append', default=[], metavar='NAME M0 RUN')
ap.add_argument('--base', default='SUPPF'); ap.add_argument('--g1', nargs='*', default=[]); ap.add_argument('--g2', nargs='*', default=[])
ap.add_argument('--g3', nargs=2, action='append', default=[], metavar=('ARM', 'F51_JSON')); ap.add_argument('--json')
ap.add_argument('--selftest', action='store_true'); ap.add_argument('--pf2-m0'); ap.add_argument('--hc-m0'); ap.add_argument('--thin-m0')
a = ap.parse_args()
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(f'{a.trackm}/m0_analyze.py') == MD5['m0_analyze.py'], 'm0_analyze.py md5'
sys.path.insert(0, a.trackm)
from m0_analyze import agg, NOISY  # noqa: E402
assert NOISY == 'CSIR_00070_r8_c4'


def to24(cells, strict):
    """conf -> 24x24 (strict: must already be 24x24; else a 25x25 m0_audit_b3 conf is cut to its 24x24 GT x pred block)."""
    out = {}
    for s, c in cells.items():
        n = math.isqrt(len(c['conf'])); assert n * n == len(c['conf']) and (n == NC if strict else n in (24, 25)), (s, len(c['conf']))
        out[s] = c if n == NC else dict(c, conf=np.asarray(c['conf'], np.int64).reshape(n, n)[:NC, :NC].ravel().tolist())
    return out


def per_run(j, strict=True):
    t, e = to24(j['cells']['test'], strict), to24(j['cells']['ext'], strict)
    assert len(t) == 50 and len(e) == 106, (j['run'], len(t), len(e))
    A, Ac, Ae = agg(t, lambda s: True), agg(t, lambda s: s != NOISY), agg(e, lambda s: True)
    assert Ac['n'] == 49, 'clean set must drop exactly CSIR_00070_r8_c4'

    def free(cells):  # crack px on crack-free cells (conf route); for 24x24 arms asserted equal to the crack_rel2 route
        M = {s: np.asarray(c['conf'], np.int64).reshape(NC, NC) for s, c in cells.items()}
        fr = [s for s in cells if M[s][CR].sum() == 0]
        px = int(sum(M[s][:, CR].sum() for s in fr))
        if strict:  # a cut 25x25 conf drops GT class-24 rows, so the two routes may differ there (judge used the conf route)
            assert px == sum(cells[s]['crack_rel2'][1] for s in cells if cells[s]['crack_rel2'][3] == 0), 'conf vs crack_rel2 crack-free px'
        return px, len(fr)
    g = [c for x in t.values() for c in x['crack_cc']['gt'] if c[0] >= CMIN]
    (efp, efn), (tfp, tfn) = free(e), free(t)
    return {'run': j['run'], 'test_inact_all': float(A['iou'][IN]), 'test_inact_clean': float(Ac['iou'][IN]),
            'test_relP2_all': float(A['relP2']), 'e1_crackfree_px': efp, 'e1_n_crackfree': efn,
            'rep_test_relP2_clean': float(Ac['relP2']), 'rep_test_pred_over_gt': float(A['pr'][CR] / max(A['gt'][CR], 1)),
            'rep_test_anyhit': float(np.mean([c[1] >= 1 for c in g])) if g else float('nan'), 'rep_test_crackfree_px': tfp,
            'rep_test_n_crackfree': tfn, 'rep_e1_pred_over_gt': float(Ae['pr'][CR] / max(Ae['gt'][CR], 1)),
            'rep_e1_relP2': float(Ae['relP2']), 'rep_e1_relR2': float(Ae['relR2'])}


mean = lambda rows, k: float(np.mean([r[k] for r in rows]))


def g1(rows, base):
    d = {s: mean(rows, f'test_inact_{s}') - mean(base, f'test_inact_{s}') for s in ('all', 'clean')}
    return {'delta_all': d['all'], 'delta_clean': d['clean'], 'bar': G1_BAR, 'trip': bool(d['all'] <= G1_BAR and d['clean'] <= G1_BAR)}


def g2(rows, base):
    drp = mean(rows, 'test_relP2_all') - mean(base, 'test_relP2_all'); x = mean(rows, 'e1_crackfree_px') / mean(base, 'e1_crackfree_px')
    return {'delta_test_relP2_all': drp, 'e1_crackfree_px_arm': mean(rows, 'e1_crackfree_px'), 'e1_crackfree_px_base': mean(base, 'e1_crackfree_px'),
            'ratio': x, 'trip_relP': bool(drp < G2_RELP), 'trip_e1': bool(x > G2_X), 'trip': bool(drp < G2_RELP or x > G2_X)}


def g3(path, arm):
    try:
        c = json.load(open(path))['contrasts'][arm]; hi = float(c['boot_hi_97p5'])
    except Exception as ex:  # noqa: BLE001
        return {'status': f'MISSING ({type(ex).__name__}: {ex})', 'trip': None}
    assert bool(hi < 0) == bool(c['fail']), ('G3: fail flag in the F51 JSON disagrees with boot_hi < 0', hi, c['fail'])
    return {'status': 'computed', 'boot_hi_97p5': hi, 'd_F51_crack_ap': float(c['d_F51_crack_ap']), 'trip': bool(hi < 0), 'source': path,
            'source_md5': md5(path)}


def load(d, runs, strict=True):
    return [per_run(json.load(open(f'{d}/{r}.json')), strict) for r in runs]


if a.selftest:
    import tempfile, os
    st = lambda p: [f'{p}{k}' for k in range(5, 10)]
    B = load(a.pf2_m0, st('pf2_SUPPF_100pct_s'))
    T = {'HC': load(a.hc_m0, st('hc_HC_100pct_s')), 'SKR w 1.0': load(a.thin_m0, st('thin_SKR_100pct_s'), False),
         'CLD': load(a.thin_m0, st('thin_CLD_100pct_s'), False)}
    # judge's numbers: G1 delta all / clean, G1 trip, G2 relP delta, G2 E1 ratio, G2 trip
    exp = {'HC': (-0.0228, -0.0230, True, +0.0017, 0.90, False), 'SKR w 1.0': (-0.0170, -0.0161, True, -0.0702, 2.40, True),
           'CLD': (-0.0114, -0.0106, False, -0.0186, 1.53, True)}
    ok = True
    for k, rows in T.items():
        r1, r2 = g1(rows, B), g2(rows, B); e = exp[k]
        got = (round(r1['delta_all'], 4), round(r1['delta_clean'], 4), r1['trip'], round(r2['delta_test_relP2_all'], 4), round(r2['ratio'], 2), r2['trip'])
        t = (got[0] == e[0] and got[1] == e[1], got[2] == e[2], got[3] == e[3], got[4] == e[4], got[5] == e[5])
        ok &= all(t)
        print(f"selftest {k}: G1 delta {got[0]:+.4f} / {got[1]:+.4f} (exp {e[0]:+.4f} / {e[1]:+.4f}) {t[0]}, {'TRIP' if got[2] else 'ok'} "
              f"(exp {'TRIP' if e[2] else 'ok'}) {t[1]} | G2 relP {got[3]:+.4f} (exp {e[3]:+.4f}) {t[2]}, E1 crack-free x{got[4]:.2f} "
              f"(exp x{e[4]:.2f}) {t[3]}, {'TRIP' if got[5] else 'ok'} (exp {'TRIP' if e[5] else 'ok'}) {t[4]}")
    fr = [r['e1_crackfree_px'] for r in B]
    t = (fr == [3092, 2718, 5178, 4179, 4486], round(float(np.mean(fr))) == SUPPF_FREE,
         round(mean(B, 'test_relP2_all'), 4) == 0.9417, round(float(np.std([r['test_relP2_all'] for r in B], ddof=1)), 4) == 0.0015)
    ok &= all(t)
    print(f'selftest SUPPF: E1 crack-free px per seed {fr} (exp [3092, 2718, 5178, 4179, 4486]) {t[0]} | mean {np.mean(fr):.0f} (exp 3931) {t[1]} | '
          f"test relP@2 mean {mean(B, 'test_relP2_all'):.4f} (exp 0.9417) {t[2]} sd (exp 0.0015) {t[3]}")
    with tempfile.TemporaryDirectory() as td:
        for nm, hi, fl in (('pass', 0.01, False), ('fail', -0.001, True), ('zero', 0.0, False)):
            json.dump({'contrasts': {'X': {'boot_hi_97p5': hi, 'fail': fl, 'd_F51_crack_ap': 0.0}}}, open(os.path.join(td, nm), 'w'))
        t = (g3(os.path.join(td, 'pass'), 'X')['trip'] is False, g3(os.path.join(td, 'fail'), 'X')['trip'] is True,
             g3(os.path.join(td, 'zero'), 'X')['trip'] is False, g3(os.path.join(td, 'none'), 'X')['trip'] is None)
    ok &= all(t)
    print(f'selftest G3 wiring (synthetic): hi > 0 ok {t[0]} | hi < 0 TRIP {t[1]} | hi == 0 ok {t[2]} | missing -> MISSING {t[3]}')
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)

arms = {x[0]: (x[1], x[2:]) for x in a.arm}
assert a.base in arms and all(len(v[1]) == 5 for v in arms.values()), 'need 5 runs per arm'
assert all(r.endswith(f'_s{k}') for v in arms.values() for r, k in zip(v[1], range(5, 10))), 'runs must be s5..s9 in order'
assert set(a.g1) | set(a.g2) | {x[0] for x in a.g3} <= set(arms) - {a.base}
V = {n: load(d, runs) for n, (d, runs) in arms.items()}
B = V[a.base]
fr = mean(B, 'e1_crackfree_px')
if round(fr) != SUPPF_FREE:
    print(f'G2 REFUSED: {a.base} E1 crack-free px seed mean {fr:.1f} does not round to the registered {SUPPF_FREE}'); sys.exit(1)
out = {'label': 'protocol_SKR2_HC2 §3c guards (pre-registered FAIL rules)', 'base': a.base, 'per_run': V, 'G1': {}, 'G2': {}, 'G3': {},
       'md5': {'m0_analyze.py': MD5['m0_analyze.py'], 'this_file': md5(__file__)}}
L = ['## guards (protocol_SKR2_HC2 §3c); 5-seed means; a trip FAILS the arm']
for n in a.g1:
    out['G1'][n] = r = g1(V[n], B)
    L.append(f"G1 inactive | {n} - {a.base} | test inactive IoU delta all 50 {r['delta_all']:+.4f}, clean {r['delta_clean']:+.4f} | "
             f"TRIP iff <= {G1_BAR} in both | {'TRIP' if r['trip'] else 'ok'}")
for n in a.g2:
    out['G2'][n] = r = g2(V[n], B)
    L.append(f"G2 precision | {n} - {a.base} | test crack relP@2 delta (all 50) {r['delta_test_relP2_all']:+.4f} (TRIP if < {G2_RELP}) | "
             f"E1 crack px on {V[n][0]['e1_n_crackfree']} crack-free cells {r['e1_crackfree_px_arm']:.0f} vs {r['e1_crackfree_px_base']:.0f} = x{r['ratio']:.2f} "
             f"(TRIP if > {G2_X}) | {'TRIP' if r['trip'] else 'ok'}")
for n, p in a.g3:
    out['G3'][n] = r = g3(p, n)
    L.append(f"G3 F51 harm | {n} - {a.base} | " + (f"F51 crack AP d {r['d_F51_crack_ap']:+.4f}, boot upper 97.5% {r['boot_hi_97p5']:+.4f} (TRIP if < 0) | "
             f"{'TRIP' if r['trip'] else 'ok'}" if r['trip'] is not None else r['status']))
L.append('\n## reported only (never a verdict): seed means per arm')
RK = [k for k in V[a.base][0] if k.startswith('rep_')] + ['test_inact_all', 'test_inact_clean', 'test_relP2_all', 'e1_crackfree_px']
for n, rows in V.items():
    L.append(f'{n:6s} ' + ' | '.join(f'{k[4:] if k.startswith("rep_") else k} {mean(rows, k):.4f}' for k in RK))
print('\n'.join(L))
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1)
miss = [n for n, r in out['G3'].items() if r['trip'] is None]
sys.exit(1 if miss else 0)
