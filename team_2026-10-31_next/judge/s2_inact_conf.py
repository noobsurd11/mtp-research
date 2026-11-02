#!/usr/bin/env python3
"""judge s2_inact_conf (2 Nov 2026): where do GT-inactive px go? From m0 per-cell confusion (rows = GT, cols = pred), per arm, 5 seeds
pooled: share of GT inactive (11) px predicted as inactive / crack (14) / background (0) / other, on test 50, val 54, E1 106 and E1 strata;
and crack px predicted on GT-inactive px per run. Descriptive. Usage: s2_inact_conf.py NAME M0DIR PREFIX [NAME M0DIR PREFIX ...]"""
import json, math, sys
import numpy as np
ctx = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in open('/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv') if l.strip()}
args = sys.argv[1:]; arms = [args[i:i + 3] for i in range(0, len(args), 3)]
def C(c):
    m = np.asarray(c['conf'], np.int64); n = math.isqrt(m.size); return m.reshape(n, n)[:24, :24]
SETS = [('test50', 'test', lambda s: True), ('val54', 'val', lambda s: True), ('E1 106', 'ext', lambda s: True),
        ('E1 scuff+halfcut', 'ext', lambda s: ctx[s][1] == 'scuff_halfcut'), ('E1 halfcut no-scuff', 'ext', lambda s: ctx[s][3] == 'halfcut=1' and ctx[s][1] != 'scuff_halfcut'),
        ('E1 full', 'ext', lambda s: ctx[s][3] == 'halfcut=0')]
for lab, st, kp in SETS:
    print(f'-- {lab}: GT inactive px -> pred share [inact, crack, bg, other] (5 seeds pooled) | crack px on GT-inactive per run | pred-inactive px on GT-non-inactive per run')
    for name, d, pre in arms:
        M = np.zeros((24, 24), np.int64)
        for k in range(5, 10):
            cells = json.load(open(f'{d}/{pre}_100pct_s{k}.json'))['cells'][st]
            for s, c in cells.items():
                if kp(s): M += C(c)
        row = M[11]; t = row.sum()
        oth = t - row[11] - row[14] - row[0]
        print(f'   {name:6s} GT {t / 5:8.0f}/run: [{row[11] / t:.3f}, {row[14] / t:.3f}, {row[0] / t:.3f}, {oth / t:.3f}] | {row[14] / 5:7.0f} | {(M[:, 11].sum() - M[11, 11]) / 5:7.0f}')
