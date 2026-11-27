#!/usr/bin/env python3
"""judge_s2c_b5.py (judge, 14 Nov 2026): the two B5 co-primaries of verdict R (protocol_SKR2C section 3a item 2) on the wide grid.
Own code: the cv / op / rule functions are copied from the judge's earlier judge/s2_b5w.py 67f03055 (opening #5); its descriptive
E1 width part is left out on purpose (no new analysis of sealed cells). Imports no coach / runner / frozen / Track M code.
Starts from the opening's per-b count records (rec_w), like the coach; the dump-to-record step is not recomputed.
  OP rule (calib): on b = -8.0 .. +12.0 step 0.1, max pooled val recall s.t. pooled val precision >= 0.90, ties -> smaller b.
  Arm-pooled OP = the 5 seeds' val cells pooled. Each seed's test value is read at that b. Rule 1 /3, two-set rule.
Usage: judge_s2c_b5.py [OUT_TXT]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

T = Path('/home/yugma/mtp/research/team_2026-10-31_next')
REC = {'SUPPF': (T / 'results/s2c/raw_r/b5/SUPPF/rec_w', 's2c_SUPPF'), 'SKR01': (T / 'results/s2c/raw_r/b5/SKR01/rec_w', 's2c_SKR01')}
REALP = {'test': '/home/noob/work/el_f3/data/splits/test.txt', 'val': '/home/noob/work/el_f3/data/splits/val.txt',
         'ext': '/home/noob/work/el_f1/reports/f1/ext117/stems_eval.txt'}
REAL = {k: sorted(l.strip() for l in open(p) if l.strip()) for k, p in REALP.items()}
SEEDS = [10, 11, 12, 13, 14]
NOISY = 'CSIR_00070_r8_c4'
LINES = []


def P(s=''):
    print(s)
    LINES.append(s)


R, GRID = {}, None
for name, (d, pre) in REC.items():
    R[name] = {}
    for st in ('val', 'test'):
        L = []
        for k in SEEDS:
            j = json.load(open(d / f'{pre}_100pct_s{k}.{st}.json'))
            g = np.array(j['grid'], float)
            if GRID is None:
                GRID = g
            assert np.array_equal(g, GRID), (name, st, k)
            assert sorted(j['cells']) == REAL[st], (name, st, k)
            L.append(j['cells'])
        R[name][st] = L
    P(f'# {name}: {pre}_100pct_s{SEEDS}; val / test cells {[len(R[name][s][0]) for s in ("val", "test")]} = the real lists')
OPG = (GRID >= -8 - 1e-9) & (GRID <= 12 + 1e-9) & (np.abs(np.round(GRID * 10) - GRID * 10) < 1e-6)
P(f'# grid {len(GRID)} points {GRID[0]} .. {GRID[-1]}; OP grid {int(OPG.sum())} points ({GRID[OPG][0]} .. {GRID[OPG][-1]})')


def cv(cellsets, keep=lambda s: True):
    cs = [c for cells in cellsets for s, c in cells.items() if keep(s)]
    S = lambda k: np.sum([np.asarray(c[k], np.int64) for c in cs], 0)
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp')
    ng = sum(c['n_gt'] for c in cs)
    gc = [x for c in cs for x in c['gt_cc'] if x[0] >= 20]
    v50 = np.array([x[1] for x in gc])
    f50 = np.array([(v50 + b > 0).mean() for b in GRID]) if len(gc) else np.full(len(GRID), np.nan)
    dv = lambda x, y: np.where(y > 0, x / np.maximum(y, 1), np.nan)
    return dict(relP=dv(rp, pred), relR=rr / max(ng, 1), compR=f50, compP=dv(S('pc20_hit'), S('pc20_n')))


def op(c, rk, pk):
    cand = np.where(OPG)[0]
    Pv = np.nan_to_num(c[pk][cand], nan=-1)
    ok = cand[Pv >= 0.90]
    if len(ok):
        best = c[rk][ok].max()
        return min(i for i in ok if c[rk][i] == best), True
    best = Pv.max()
    return min(i for i, p in zip(cand, Pv) if p == best), False


def rule(xa, xb):
    xa, xb = np.asarray(xa, float), np.asarray(xb, float)
    d = xb.mean() - xa.mean()
    thr = max(0.01, 2 * math.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
    return d, thr, 'BETTER' if d > thr else ('WORSE' if d < -thr else 'n.d.')


SETS = (('all 50', lambda s: True), ('clean 49', lambda s: s != NOISY))
OUT = {}
for n in R:
    pv = cv(R[n]['val'])
    jc, rc = op(pv, 'compR', 'compP')
    jr, rr_ = op(pv, 'relR', 'relP')
    OUT[n] = {}
    for lab, kp in SETS:
        vals = []
        for i in range(5):
            c = cv([R[n]['test'][i]], kp)
            vals.append((c['compR'][jc], c['relR'][jr]))
        OUT[n][lab] = np.array(vals)
    P(f'{n}: arm-pooled val OP b_comp {GRID[jc]:+.1f} (reachable {rc}; val comp P {pv["compP"][jc]:.4f}), b_rel {GRID[jr]:+.1f} '
      f'(reachable {rr_}; val relP@2 {pv["relP"][jr]:.4f})')
P('\n## B5 co-primaries of verdict R (SKR01 - SUPPF, rule 1 /3)')
for iv, nm in ((0, 'comp recall @ comp P >= 0.90'), (1, 'relR@2 @ relP@2 >= 0.90')):
    r = {lab: rule(OUT['SUPPF'][lab][:, iv], OUT['SKR01'][lab][:, iv]) for lab, _ in SETS}
    a, c = r['all 50'], r['clean 49']
    better = (a[2] == 'BETTER' and c[2] == 'BETTER') or (a[2] == 'BETTER' and c[0] > 0) or (c[2] == 'BETTER' and a[0] > 0)
    lab2 = 'WORSE' if 'WORSE' in (a[2], c[2]) else ('BETTER' if better else 'n.d.')
    P(f'  {nm}: SUPPF {OUT["SUPPF"]["all 50"][:, iv].mean():.4f} +- {OUT["SUPPF"]["all 50"][:, iv].std(ddof=1):.4f}  SKR01 '
      f'{OUT["SKR01"]["all 50"][:, iv].mean():.4f} +- {OUT["SKR01"]["all 50"][:, iv].std(ddof=1):.4f} | all 50 d {a[0]:+.4f} (thr {a[1]:.4f}) {a[2]} '
      f'| clean 49 d {c[0]:+.4f} (thr {c[1]:.4f}) {c[2]} | two-set label {lab2}')
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text('\n'.join(LINES) + '\n')
