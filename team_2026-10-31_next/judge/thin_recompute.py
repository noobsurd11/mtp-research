#!/usr/bin/env python3
"""judge (1 Nov): independent recompute for THIN-B3's opening (protocol_thin_b3 §4-5). Own code; reads only opening files.
- test co-primaries from m0 per-cell JSONs: crack IoU (class 14), inactive IoU (11) from the per-cell confusion matrix
  (24x24 or 25x25; for B3 the scuff class 24 is folded into background 0 if present), crack relF1@2 from crack_rel2
  [pred near GT, pred, GT near pred, GT]; all 50 and clean (minus CSIR_00070_r8_c4); rule 1 /3 vs base.
- E1 co-primary: relF1@2 over all 106 ext cells pooled per run; E1 strata (e1_context.tsv).
- precision side at argmax: crack P, relP@2, crack px on crack-free cells (test / val / E1), m0 component precision.
- B5 (from calib-format records rec/<run>.<set>.json): per-run OP and arm-pooled OP (pooled 5-seed val curves; max val
  recall s.t. val precision >= 0.90 over OPGRID -4..+12 step 0.1, ties -> smaller b, unreachable -> max-precision b),
  component recall at the comp OP and relR@2 at the rel OP on test (all / clean) and E1; speck share + all-size comp
  precision at each OP (A1); rule 1 /3 vs base.
Usage: thin_recompute.py --arm NAME M0_DIR PREFIX REC_DIR [--arm ...] --base NAME [--seeds 5 6 7 8 9] [--ctx e1_context.tsv]
"""
import argparse, json, math
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--arm', nargs=4, action='append', metavar=('NAME', 'M0', 'PREFIX', 'REC'))
ap.add_argument('--base', required=True); ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--ctx', default='/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv')
ap.add_argument('--no-b5', action='store_true')
a = ap.parse_args()
NOISY = 'CSIR_00070_r8_c4'; CR, IN = 14, 11
ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open(a.ctx) if l.strip()}

def conf(c):
    m = np.asarray(c['conf'], np.int64); n = int(round(math.sqrt(m.size))); m = m.reshape(n, n)
    if n == 25:  # fold scuff (24) into background before 24-class metrics
        m = m.copy(); m[0, :] += m[24, :]; m[:, 0] += m[:, 24]; m[0, 0] -= 0; m = m[:24, :24]
    return m

def agg(cells, keep=lambda s: True):
    S = [s for s in cells if keep(s)]
    M = sum(conf(cells[s]) for s in S)
    iou = lambda k: M[k, k] / max(M[k, :].sum() + M[:, k].sum() - M[k, k], 1)
    r = np.sum([cells[s]['crack_rel2'] for s in S], 0).astype(float)
    P, R = r[0] / max(r[1], 1), r[2] / max(r[3], 1)
    gtc = [g for s in S for g in cells[s]['crack_cc']['gt'] if g[0] >= 20]
    prc = [p for s in S for p in cells[s]['crack_cc']['pr'] if p[0] >= 20]
    prall = [p for s in S for p in cells[s]['crack_cc']['pr']]
    free = [s for s in S if conf(cells[s])[CR, :].sum() == 0]
    return dict(crackIoU=iou(CR), inactIoU=iou(IN), relF1=2 * P * R / max(P + R, 1e-12), relP=P, relR=R,
                crackP=M[CR, CR] / max(M[:, CR].sum(), 1), crackR=M[CR, CR] / max(M[CR, :].sum(), 1),
                compR=np.mean([g[1] >= math.ceil(0.5 * g[0]) for g in gtc]) if gtc else np.nan,
                compP=np.mean([p[1] >= 1 for p in prc]) if prc else np.nan,
                compP_all=np.mean([p[1] >= 1 for p in prall]) if prall else np.nan,
                free_px=np.mean([conf(cells[s])[:, CR].sum() for s in free]) if free else np.nan, n_free=len(free), n=len(S))

def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean(); thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')

M0 = {}
for name, d, pre, rec in a.arm:
    runs = []
    for k in a.seeds:
        j = json.load(open(f'{d}/{pre}_{name}_100pct_s{k}.json'))
        assert j['step'] == 20000, (name, k)
        assert len(j['cells']['test']) == 50 and len(j['cells']['ext']) == 106, (name, k)
        runs.append(j)
    M0[name] = runs
    print(f'# {name}: {pre}_{name}_100pct_s{a.seeds} code_revision {sorted({r["code_revision"] for r in runs})}')

SETS = [('test all 50', 'test', lambda s: True), ('test clean 49', 'test', lambda s: s != NOISY),
        ('E1 all 106', 'ext', lambda s: True), ('E1 scuff+half-cut 29', 'ext', lambda s: ctx[s][1] == 'scuff_halfcut'),
        ('E1 other 77', 'ext', lambda s: ctx[s][1] == 'other'),
        ('E1 half-cut 58', 'ext', lambda s: ctx[s][3] == 'halfcut=1'), ('E1 full 48', 'ext', lambda s: ctx[s][3] == 'halfcut=0'),
        ('val 54', 'val', lambda s: True)]
KEYS = ['crackIoU', 'relF1', 'inactIoU', 'relP', 'relR', 'crackP', 'crackR', 'compR', 'compP', 'compP_all', 'free_px']
T = {name: {lab: [agg(r['cells'][st], kp) for r in runs] for lab, st, kp in SETS} for name, runs in M0.items()}
for lab, _, _ in SETS:
    print(f'\n## {lab} (argmax, m0 JSONs; per arm mean over seeds; free_px = mean crack px per crack-free cell)')
    print('arm     ' + ' '.join(f'{k:>9s}' for k in KEYS) + '  n_free')
    for name in T:
        v = T[name][lab]
        print(f'{name:7s} ' + ' '.join(f'{np.nanmean([x[k] for x in v]):9.4f}' for k in KEYS) + f'  {v[0]["n_free"]}')
    for name in T:
        if name == a.base: continue
        out = []
        for k in (['crackIoU', 'relF1', 'inactIoU'] if lab.startswith('test') else ['relF1', 'inactIoU', 'crackR', 'relR', 'relP', 'compR']):
            d, thr, v = rule([x[k] for x in T[a.base][lab]], [x[k] for x in T[name][lab]])
            out.append(f'{k} {d:+.4f} (thr {thr:.4f}) {v}')
        rp = np.mean([x['relP'] for x in T[name][lab]]) - np.mean([x['relP'] for x in T[a.base][lab]])
        print(f'  {name}-{a.base}: ' + ' | '.join(out) + f' | relP@2 d {rp:+.4f}' + (' FLAG(>0.05 drop)' if rp < -0.05 else ''))
    if lab.startswith('E1 all') or lab.startswith('test'):
        for name in T:
            print(f'  per-seed {name}: relF1 ' + ' '.join(f'{x["relF1"]:.4f}' for x in T[name][lab])
                  + ' | crackIoU ' + ' '.join(f'{x["crackIoU"]:.4f}' for x in T[name][lab])
                  + ' | inact ' + ' '.join(f'{x["inactIoU"]:.4f}' for x in T[name][lab]))

if a.no_b5: raise SystemExit
GRID = None
def L(rec, run, st): return json.load(open(f'{rec}/{run}.{st}.json'))
def curves(cellsets):
    cs = [c for cells in cellsets for c in cells.values()]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cs)
    gc = [x for c in cs for x in c['gt_cc'] if x[0] >= 20]
    found = np.array([[x[1] + b > 0 for b in GRID] for x in gc]) if gc else np.zeros((0, len(GRID)), bool)
    n20, h20, nall, hall, spk = S('pc20_n'), S('pc20_hit'), S('pc_n'), S('pc_hit'), S('speck_px')
    dv = lambda x, y: np.where(y > 0, x / np.maximum(y, 1), np.nan)
    return dict(relP=dv(rp, pred), relR=dv(rr, np.full_like(rr, ng)), compR=found.mean(0) if len(gc) else np.full(len(GRID), np.nan),
                compP=dv(h20, n20), compP_all=dv(hall, nall), speck=dv(spk, pred))
def op(cv, rk, pk):
    ok = np.where(OPG & (np.nan_to_num(cv[pk], nan=-1) >= 0.90))[0]
    if len(ok):
        best = np.nanmax(cv[rk][ok]); i = min([j for j in ok if cv[rk][j] == best], key=lambda j: GRID[j]); return i, True
    cand = np.where(OPG)[0]; best = np.nanmax(cv[pk][cand]); return min([j for j in cand if cv[pk][j] == best], key=lambda j: GRID[j]), False

B5 = {}
for name, d, pre, rec in a.arm:
    runs = [f'{pre}_{name}_100pct_s{k}' for k in a.seeds]
    V = {r: L(rec, r, 'val')['cells'] for r in runs}; Te = {r: L(rec, r, 'test')['cells'] for r in runs}; E = {r: L(rec, r, 'ext')['cells'] for r in runs}
    if GRID is None:
        GRID = np.array(L(rec, runs[0], 'val')['grid'], float)
        OPG = (GRID >= -4 - 1e-9) & (GRID <= 12 + 1e-9) & (np.abs(np.round(GRID * 10) - GRID * 10) < 1e-6)
    pv = curves(list(V.values())); ic, rc_ = op(pv, 'compR', 'compP'); ir, rr_ = op(pv, 'relR', 'relP')
    res = {'pooled': {'b_comp': GRID[ic], 'b_rel': GRID[ir], 'reach': (rc_, rr_)}, 'per_run': []}
    for mode in ('pooled', 'per_run'):
        rows = []
        for r in runs:
            if mode == 'per_run':
                cv = curves([V[r]]); jc, _ = op(cv, 'compR', 'compP'); jr, _ = op(cv, 'relR', 'relP')
            else:
                jc, jr = ic, ir
            row = {'bc': GRID[jc], 'br': GRID[jr]}
            for lab, D, keep in (('test', Te, lambda s: True), ('test_clean', Te, lambda s: s != NOISY), ('E1', E, lambda s: True)):
                cv = curves([{s: c for s, c in D[r].items() if keep(s)}])
                row[lab] = dict(compR=cv['compR'][jc], relR=cv['relR'][jr], compP=cv['compP'][jc], relP=cv['relP'][jr],
                                speck=cv['speck'][jr], compP_all=cv['compP_all'][jc])
            rows.append(row)
        res[mode] = rows if mode == 'per_run' else {**res['pooled'], 'rows': rows}
    B5[name] = res
print('\n## B5 (records; OPGRID -4..+12; P target 0.90 on val)')
for name, res in B5.items():
    p = res['pooled']
    print(f"{name}: pooled b_comp {p['b_comp']:.1f} b_rel {p['b_rel']:.1f} reach {p['reach']} | per-run b_comp "
          + '/'.join(f"{x['bc']:.1f}" for x in res['per_run']) + ' b_rel ' + '/'.join(f"{x['br']:.1f}" for x in res['per_run']))
for mode in ('pooled', 'per_run'):
    for lab in ('test', 'test_clean', 'E1'):
        for k, pk in (('compR', 'compP'), ('relR', 'relP')):
            g = lambda n: [x[lab][k] for x in (B5[n]['pooled']['rows'] if mode == 'pooled' else B5[n]['per_run'])]
            gp = lambda n: np.mean([x[lab][pk] for x in (B5[n]['pooled']['rows'] if mode == 'pooled' else B5[n]['per_run'])])
            sp = lambda n: np.mean([x[lab]['speck'] for x in (B5[n]['pooled']['rows'] if mode == 'pooled' else B5[n]['per_run'])])
            ca = lambda n: np.mean([x[lab]['compP_all'] for x in (B5[n]['pooled']['rows'] if mode == 'pooled' else B5[n]['per_run'])])
            line = f'{mode:7s} {lab:10s} {k}: ' + ' '.join(f'{n} {np.mean(g(n)):.4f} ({pk} {gp(n):.3f}, speck {sp(n):.3f}, compP_all {ca(n):.3f})' for n in B5)
            for n in B5:
                if n != a.base:
                    d, thr, v = rule(g(a.base), g(n)); line += f' || {n}-{a.base} {d:+.4f} thr {thr:.4f} {v}'
            print(line)
