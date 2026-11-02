#!/usr/bin/env python3
"""judge arch_a6_check (2 Nov 2026): own recompute of arch_A6's claims (stdlib; el_metrics-format val / rf records only; no test / E1).
(a) val off-GT crack px (pred - tp) at b 0 on crack cells (n_gt >= 20) and crack-free cells (n_gt == 0), seed means: SKR w1.0 vs SUPPF (bf16 pair).
(b) F51 crack-free FA px at each run's val b_rel (calib OP rule), ungated vs gated (gate g = s['1'], t = min g over val crack cells - 1e-3;
    gated crack-free cells keep 0 px), seed means: SUPPF s5-9, SUPPF s0-4, HC s5-9.
(c) cell AUROC on s['1'] (pos n_gt >= 20, neg n_gt == 0): val, F51, H36.
Usage: python3 arch_a6_check.py TEAM_DIR"""
import json, sys
from statistics import mean
T = sys.argv[1]
SET = {l.split('\t')[0]: l.split('\t')[1] for l in list(open(f'{T}/judge/out/rf_sets.tsv'))[1:]}
L = lambda p: json.load(open(p))


def op(cells, grid):
    S = lambda k: [sum(c[k][j] for c in cells.values()) for j in range(len(grid))]
    pred, rp, rr = S('pred'), S('relp_tp'), S('relr_tp'); ng = sum(c['n_gt'] for c in cells.values())
    cand = [j for j, b in enumerate(grid) if -4 - 1e-9 <= b <= 12 + 1e-9 and abs(round(b * 10) - b * 10) < 1e-6]
    ok = [j for j in cand if pred[j] > 0 and rp[j] / pred[j] >= 0.90]
    if ok:
        best = max(rr[j] for j in ok); return min((j for j in ok if rr[j] == best), key=lambda j: grid[j])
    P = {j: (rp[j] / pred[j] if pred[j] else -1) for j in cand}; best = max(P.values())
    return min((j for j in cand if P[j] == best), key=lambda j: grid[j])


def auroc(pos, neg):
    if not pos or not neg:
        return float('nan')
    w = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return w / (len(pos) * len(neg))


print('## (a) val off-GT px at b 0, seed means (bf16 b5 records)')
for arm, d, pre in (('SUPPF', f'{T}/results/pf2/raw/b5/rec', 'pf2_SUPPF'), ('SKR', f'{T}/results/thin/raw/b5/rec', 'thin_SKR'), ('CLD', f'{T}/results/thin/raw/b5/rec', 'thin_CLD')):
    on, off, au = [], [], []
    for k in range(5, 10):
        r = L(f'{d}/{pre}_100pct_s{k}.val.json'); g = r['grid']; j0 = min(range(len(g)), key=lambda i: abs(g[i])); c = r['cells']
        on.append(sum(x['pred'][j0] - x['tp'][j0] for x in c.values() if x['n_gt'] >= 20))
        off.append(sum(x['pred'][j0] for x in c.values() if x['n_gt'] == 0))
        au.append(auroc([x['s']['1'] for x in c.values() if x['n_gt'] >= 20], [x['s']['1'] for x in c.values() if x['n_gt'] == 0]))
    print(f'{arm}: off-GT px on crack cells {mean(on):.0f} | crack px on crack-free cells {mean(off):.1f} | val cell AUROC s1 {mean(au):.3f}')

print('\n## (b, c) _rf at val b_rel, gate t = min val-positive s1 - 1e-3')
ARMS = [('SUPPF s5-9', f'{T}/results/hc/raw/shv1/rec', [f'pf2_SUPPF_100pct_s{k}' for k in range(5, 10)]),
        ('SUPPF s0-4', f'{T}/ideas/calib_out/rec', [f'SUPPF5_m{k}' for k in range(5)]),
        ('HC s5-9', f'{T}/results/hc/raw/shv1/rec', [f'hc_HC_100pct_s{k}' for k in range(5, 10)])]
for name, d, runs in ARMS:
    acc = {}
    for r in runs:
        v = L(f'{d}/{r}.val.json'); g = v['grid']; j = op(v['cells'], g)
        t = min(x['s']['1'] for x in v['cells'].values() if x['n_gt'] >= 20) - 1e-3
        rf = L(f'{d}/{r}.rf.json')['cells']
        for st in ('F51', 'H36'):
            free = [x for s, x in rf.items() if SET.get(s) == st and x['n_gt'] == 0]
            acc.setdefault(st + '_fa', []).append(sum(x['pred'][j] for x in free))
            acc.setdefault(st + '_fag', []).append(sum(x['pred'][j] for x in free if x['s']['1'] >= t))
            acc.setdefault(st + '_auc', []).append(auroc([x['s']['1'] for s, x in rf.items() if SET.get(s) == st and x['n_gt'] >= 20],
                                                         [x['s']['1'] for x in free]))
        acc.setdefault('b', []).append(g[j]); acc.setdefault('t', []).append(round(t, 2))
    print(f"{name}: b_rel {acc['b']} t {acc['t']} | F51 FA {mean(acc['F51_fa']):.0f} -> gated {mean(acc['F51_fag']):.0f}; AUROC {mean(acc['F51_auc']):.3f} "
          f"| H36 FA {mean(acc['H36_fa']):.1f} -> {mean(acc['H36_fag']):.1f}; AUROC {mean(acc['H36_auc']):.3f}")
