"""PF2 opening, REPORTED ONLY (protocol_PF2.md section 3b addendum, judge: E1 GT crack is ~1.5x wider than train): E1 relR@2, relP@2,
relF1@2, component recall (GT comps >= 20 px with >= 50% of px within 2 px of a prediction) and component precision (pred comps
>= 20 px with >= 1 px within 2 px of GT), per run from the m0 per-cell JSONs (crack_rel2, crack_cc), computed by Track M's own
m0_analyze.agg (imported, not re-implemented); per arm mean +- sd and rule-1 arithmetic (/3) for the given contrasts.
Groups: E1 all 106, half-cut 58 / full 48, scuff+half-cut 29 / other 77 (e1_context.tsv). Never a verdict.
Usage: python pf2_e1_width.py M0_DIR E1_CONTEXT ARM ... [--prefix pf2] [--seeds 5 6 7 8 9] [--contrasts SUPPF-SUP RN50PF-SUPPF]
"""
import argparse, json, sys
import numpy as np

sys.path.insert(0, '/home/yugma/mtp/research/team_2026-10-24_go/trackM/scripts')
from m0_analyze import agg  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('m0'); ap.add_argument('ctx'); ap.add_argument('arms', nargs='+')
ap.add_argument('--prefix', default='pf2'); ap.add_argument('--seeds', nargs='+', type=int, default=[5, 6, 7, 8, 9])
ap.add_argument('--contrasts', nargs='*', default=['SUPPF-SUP', 'RN50PF-SUPPF'])
a = ap.parse_args()
ctx = {}
for l in open(a.ctx):
    if l.strip():
        f = l.rstrip('\n').split('\t'); ctx[f[0]] = dict([('ctx', f[1])] + [x.split('=') for x in f[2:4]])
G = [('E1 all 106', lambda s: True), ('E1 half-cut', lambda s: ctx[s]['halfcut'] == '1'), ('E1 full', lambda s: ctx[s]['halfcut'] == '0'),
     ('E1 scuff_halfcut', lambda s: ctx[s]['ctx'] == 'scuff_halfcut'), ('E1 other', lambda s: ctx[s]['ctx'] == 'other')]
K = [('relR2', 'relR@2'), ('relP2', 'relP@2'), ('relF1', 'relF1@2'), ('cc_rec50_20', 'comp recall'), ('cc_prec_20', 'comp precision')]
R = {}
for arm in a.arms:
    runs = [json.load(open(f'{a.m0}/{a.prefix}_{arm}_100pct_s{k}.json')) for k in a.seeds]
    assert all(r['step'] == 20000 for r in runs)
    R[arm] = {g: [agg(r['cells']['ext'], keep) for r in runs] for g, keep in G}
    assert len(runs[0]['cells']['ext']) == 106
print(f'## E1 width-robust crack metrics (REPORTED ONLY), seeds {a.seeds}: mean±sd over seeds')
print('group | n | arm | ' + ' | '.join(lab for _, lab in K))
for g, _ in G:
    for arm in a.arms:
        v = R[arm][g]
        print(f'{g:17s} | {v[0]["n"]:3d} | {arm:6s} | ' + ' | '.join(f'{np.mean([x[k] for x in v]):.4f}±{np.std([x[k] for x in v], ddof=1):.4f}' for k, _ in K))
print('\n## rule-1 arithmetic (/3), E1 all 106 and strata (reported, not a verdict)')
for c in a.contrasts:
    b, aa = c.split('-')
    if aa not in R or b not in R:
        continue
    for g, _ in G:
        for k, lab in K:
            xa = np.array([x[k] for x in R[aa][g]]); xb = np.array([x[k] for x in R[b][g]])
            d = xb.mean() - xa.mean(); thr = max(0.01, 2 * np.sqrt((xa.std(ddof=1) ** 2 + xb.std(ddof=1) ** 2) / 3))
            print(f'{b} - {aa} | {g:17s} | {lab:15s} | delta {d:+.4f} | thr {thr:.4f} | {"BETTER" if d > thr else ("WORSE" if d < -thr else "n.d.")}')
