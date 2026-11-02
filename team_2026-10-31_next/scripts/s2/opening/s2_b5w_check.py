"""SKR2 + HC2 B5 on the wider grid: self-checks and the B5 table (protocol_SKR2_HC2 v1.0.1 §3a.2, §6). DRAFT (runner's helper, 2 Nov 2026)
for coach's FREEZE. CPU only; reads el_metrics record / summary JSONs (never a dump, never an image).
  records --pair WIDE OLD [--pair ...]
      el_metrics_w (wide grid -8.0 .. +12.0 + 0.75) records vs el_metrics 6e73ff11 records of the SAME dump: 'set', 'runs', 'dump' and
      the cell stems equal; per cell the key set is exactly the 6e73ff11 cell_record() keys; non-grid keys (n_keep, n_gt, gt_cc, area,
      gt_inact, gt_inact_area, s) equal exactly; per-grid keys (pred, tp, relp_tp, relr_tp, pc20_n, pc20_hit, pc_n, pc_hit, speck_px,
      inact_pred, inact_tp, inact_pred_area) equal exactly at every b of the old grid (matched by exact float value); the wide grid adds
      exactly the 40 tenths -8.0 .. -4.1. exit 0 iff every pair is equal.
  ops --wide-sum DIR --frozen-sum DIR --runs RUN x5
      SUPPF: the OPs chosen on the wide grid (per run: op_comp / op_rel of RUN.{test,test_clean,ext}.json; arm-pooled: pooled_op of
      RUN.{test,test_clean,ext}.pooled.json) equal PF2's frozen 6e73ff11 OPs (b, reachable, edge) (judge: only an OP at -4.0 or an
      unreachable one can move). exit 0 iff all equal; a move is printed as MOVED and the wide OP is the one the protocol uses (§3a.2).
  table --arm NAME SUM_DIR RUN x5 [...] --base SUPPF --coprim SKR01 [--old NAME OLD_SUM_DIR ...] [--json OUT]
      B5 readout at the arm-pooled OP chosen on val over the wide grid (calib's rule, el_metrics_w choose_op): per run test comp recall
      at comp P >= 0.90 (pooled_op.comp_recall_at_opc) and relR@2 at relP@2 >= 0.90 (pooled_op.relR_at_opr), all 50 (RUN.test.pooled.json)
      and clean (RUN.test_clean.pooled.json); rule 1 (/3) per set vs --base (co-primary for --coprim arms, reported for the others);
      the two-set combination is left to coach's recompute (as the test co-primaries). Reported: per-run OPs, OP flags (reachable,
      edge, below -4.0), achieved precisions, E1 (descriptive), and for --old arms the 6e73ff11 pooled OP beside the wide one.
"""
import argparse, json, sys
from pathlib import Path

import numpy as np

PERGRID = {'pred', 'tp', 'relp_tp', 'relr_tp', 'pc20_n', 'pc20_hit', 'pc_n', 'pc_hit', 'speck_px', 'inact_pred', 'inact_tp', 'inact_pred_area'}
SCALAR = {'n_keep', 'n_gt', 'gt_cc', 'area', 'gt_inact', 'gt_inact_area', 's'}
ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
r = sub.add_parser('records'); r.add_argument('--pair', nargs=2, action='append', required=True, metavar=('WIDE', 'OLD'))
o = sub.add_parser('ops'); o.add_argument('--wide-sum', required=True); o.add_argument('--frozen-sum', required=True); o.add_argument('--runs', nargs=5, required=True)
t = sub.add_parser('table'); t.add_argument('--arm', nargs='+', action='append', required=True, metavar='NAME DIR RUN')
t.add_argument('--base', default='SUPPF'); t.add_argument('--coprim', nargs='*', default=[]); t.add_argument('--old', nargs=2, action='append', default=[])
t.add_argument('--json')
a = ap.parse_args()
ld = lambda p: json.load(open(p))


def cmp_records(wp, op_):
    W, O = ld(wp), ld(op_)
    for k in ('set', 'runs', 'dump'):
        if W[k] != O[k]:
            return f'{k} differs'
    gw, go = list(map(float, W['grid'])), list(map(float, O['grid']))
    try:
        idx = [gw.index(b) for b in go]
    except ValueError as e:
        return f'old grid value not in wide grid ({e})'
    extra = sorted(set(gw) - set(go))
    tenths = sorted({int(round(b * 10)) for b in extra})
    if (len(gw) - len(go) != 40 or len(extra) != 40 or tenths != list(range(-80, -40))
            or any(abs(b * 10 - round(b * 10)) > 1e-6 for b in extra)):
        return f'wide grid adds {len(gw) - len(go)} values, not exactly -8.0 .. -4.1'
    if set(W['cells']) != set(O['cells']):
        return 'cell stems differ'
    for s in O['cells']:
        cw, co = W['cells'][s], O['cells'][s]
        if set(cw) != PERGRID | SCALAR or set(co) != PERGRID | SCALAR:
            return f'{s}: cell keys {sorted(set(cw) ^ (PERGRID | SCALAR))} / {sorted(set(co) ^ (PERGRID | SCALAR))} unexpected'
        for k in SCALAR:
            if cw[k] != co[k]:
                return f'{s}: {k} differs'
        for k in PERGRID:
            if len(cw[k]) != len(gw) or len(co[k]) != len(go):
                return f'{s}: {k} length'
            if [cw[k][i] for i in idx] != co[k]:
                return f'{s}: {k} differs on the old grid'
    return None


if a.cmd == 'records':
    bad = 0
    for wp, op_ in a.pair:
        e = cmp_records(wp, op_); bad += e is not None
        print(f"{Path(wp).name} vs {Path(op_).name}: {'EQUAL on -4..+12 (+0.75); wide adds -8.0..-4.1' if e is None else 'DIFFER: ' + e}")
    print(f"records sub-grid check: {len(a.pair) - bad}/{len(a.pair)} equal")
    sys.exit(1 if bad else 0)

if a.cmd == 'ops':
    W, Fz, bad, expl = Path(a.wide_sum), Path(a.frozen_sum), 0, 0
    f = lambda op: (op['b'], op['reachable'], op['edge'])
    # coach ruling 3 (2 Nov): a move is EXPLAINED (rc 0, reported) iff the wide OP is below -4.0 or PF2's frozen OP was the unreachable
    # fallback; any other move is UNEXPLAINED (flag, rc 1, no abort). The wide OP is the one used either way (protocol §3a.2).
    for run in a.runs:
        for S in ('test', 'test_clean', 'ext'):
            w, z = ld(W / f'{run}.{S}.json'), ld(Fz / f'{run}.{S}.json')
            wp, zp = ld(W / f'{run}.{S}.pooled.json')['pooled_op'], ld(Fz / f'{run}.{S}.pooled.json')['pooled_op']
            for lab, x, y in (('per-run comp', w['op_comp'], z['op_comp']), ('per-run rel', w['op_rel'], z['op_rel']),
                              ('pooled comp', wp['op_comp'], zp['op_comp']), ('pooled rel', wp['op_rel'], zp['op_rel'])):
                eq = f(x) == f(y); ex = (not eq) and (x['b'] < -4.0 - 1e-9 or not y['reachable'])
                bad += (not eq) and not ex; expl += ex
                print(f"{run} {S} {lab} OP: wide b {x['b']:+.1f} (reachable {x['reachable']}) frozen b {y['b']:+.1f} (reachable {y['reachable']}) -> "
                      f"{'equal' if eq else ('MOVED, explained (wide b < -4.0 or frozen OP unreachable)' if ex else 'MOVED, UNEXPLAINED')}")
    print(f"SUPPF wide-grid OPs vs PF2's frozen OPs: {expl} explained moves, {bad} unexplained moves (the wide OP is used, protocol §3a.2; "
          f"coach ruling 3: rc 1 iff any unexplained move)")
    sys.exit(1 if bad else 0)

# ---- table ----
arms = {x[0]: (Path(x[1]), x[2:]) for x in a.arm}
assert a.base in arms and all(len(v[1]) == 5 for v in arms.values()) and set(a.coprim) <= set(arms) - {a.base}
old = {n: Path(d) for n, d in a.old}


def rule1(xb, xa):  # hc_e1_coprim.rule1
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return {'delta': float(d), 'thr': float(thr), 'reading': 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')}


V, OPS, L = {}, {}, ['## B5 on the wide grid (-8.0 .. +12.0), arm-pooled OP chosen on val (calib rule; el_metrics_w)']
for n, (d, runs) in arms.items():
    V[n] = {}
    for S in ('test', 'test_clean', 'ext'):
        P = [ld(d / f'{r}.{S}.pooled.json')['pooled_op'] for r in runs]; Q = [ld(d / f'{r}.{S}.json') for r in runs]
        assert all(p['op_comp'] == P[0]['op_comp'] and p['op_rel'] == P[0]['op_rel'] for p in P), (n, S, 'pooled OP differs between runs')
        V[n][S] = {'compR_at_pooled_opc': [p['comp_recall_at_opc'] for p in P], 'compP_at_pooled_opc': [p['comp_prec_at_opc'] for p in P],
                   'relR_at_pooled_opr': [p['relR_at_opr'] for p in P], 'relP_at_pooled_opr': [p['relP_at_opr'] for p in P],
                   'compR_at_run_opc': [q['comp_recall_at_opc'] for q in Q], 'relR_at_run_opr': [q['relR_at_opr'] for q in Q],
                   'run_b_comp': [q['op_comp']['b'] for q in Q], 'run_b_rel': [q['op_rel']['b'] for q in Q]}
    OPS[n] = {'pooled_op_comp': P[0]['op_comp'], 'pooled_op_rel': P[0]['op_rel']}
    fl = lambda op: f"b {op['b']:+.1f}" + ('' if op['reachable'] else ' UNREACHABLE (max-precision b)') + (' edge' if op['edge'] else '') + (' below -4.0 (outside the old grid)' if op['b'] < -4.0 - 1e-9 else '')
    L.append(f"{n:6s} pooled OP comp {fl(P[0]['op_comp'])} | rel {fl(P[0]['op_rel'])} | per-run b_comp {V[n]['test']['run_b_comp']} b_rel {V[n]['test']['run_b_rel']}")
    if n in old:
        z = ld(old[n] / f'{runs[0]}.test.pooled.json')['pooled_op']
        OPS[n]['old_grid_pooled'] = {'op_comp': z['op_comp'], 'op_rel': z['op_rel']}
        L.append(f"{n:6s} (reported) 6e73ff11 pooled OP on -4..+12: comp b {z['op_comp']['b']:+.1f} (reachable {z['op_comp']['reachable']}), rel b "
                 f"{z['op_rel']['b']:+.1f} (reachable {z['op_rel']['reachable']}) -> wide {'same' if (z['op_comp']['b'], z['op_rel']['b']) == (P[0]['op_comp']['b'], P[0]['op_rel']['b']) else 'MOVED'}")
out = {'label': 'protocol_SKR2_HC2 §3a.2 B5 wide grid', 'base': a.base, 'coprim': a.coprim, 'values': V, 'ops': OPS, 'rule1': {}}
L.append(f'\n## rule 1 (/3) vs {a.base} per set (two-set combination: coach); co-primary for {a.coprim}, reported otherwise')
for n in arms:
    if n == a.base:
        continue
    out['rule1'][n] = {}
    for m, lab in (('compR_at_pooled_opc', 'test comp recall at comp P >= 0.90 (pooled OP)'), ('relR_at_pooled_opr', 'test relR@2 at relP@2 >= 0.90 (pooled OP)')):
        for S in ('test', 'test_clean'):
            rr = rule1(V[n][S][m], V[a.base][S][m]); out['rule1'][n][f'{m}|{S}'] = rr
            L.append(f"{n} - {a.base} | {'CO-PRIMARY' if n in a.coprim else '(reported)'} {lab} | {'all 50' if S == 'test' else 'clean 49'} | "
                     f"{n} {np.mean(V[n][S][m]):.4f}±{np.std(V[n][S][m], ddof=1):.4f} | {a.base} {np.mean(V[a.base][S][m]):.4f}±{np.std(V[a.base][S][m], ddof=1):.4f} | "
                     f"delta {rr['delta']:+.4f} | thr {rr['thr']:.4f} | {rr['reading']}")
    for m in ('compR_at_run_opc', 'relR_at_run_opr'):
        out['rule1'][n][f'{m}|test (reported)'] = rule1(V[n]['test'][m], V[a.base]['test'][m])
    L.append(f"{n} - {a.base} | (reported) per-run OPs, all 50: comp recall d {out['rule1'][n]['compR_at_run_opc|test (reported)']['delta']:+.4f}, relR@2 d "
             f"{out['rule1'][n]['relR_at_run_opr|test (reported)']['delta']:+.4f} | E1 (descriptive) at pooled OP: comp recall d "
             f"{np.mean(V[n]['ext']['compR_at_pooled_opc']) - np.mean(V[a.base]['ext']['compR_at_pooled_opc']):+.4f}, relR@2 d "
             f"{np.mean(V[n]['ext']['relR_at_pooled_opr']) - np.mean(V[a.base]['ext']['relR_at_pooled_opr']):+.4f}")
print('\n'.join(L))
if a.json:
    json.dump(out, open(a.json, 'w'), indent=1)
