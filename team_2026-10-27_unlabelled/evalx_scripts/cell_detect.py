"""evalx Q3c: cell-level crack detection on E1 ext (the only set with crack-free cells) and inactive cell detection
on test. Cell positive = GT crack >= 20 px (inactive: >= 0.5% of cell area, E1 definition); predicted positive =
>= 50 px predicted (crack) / >= 0.5% (inactive). FINAL b0.75 and b0, and A100 single models."""
import json, glob
import numpy as np
TM = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
def counts(cells, cls):
    out = {}
    for s, v in cells.items():
        C = np.array(v['conf']).reshape(24, 24); out[s] = (C[cls].sum(), C[:, cls].sum(), C.sum())
    return out
F = json.load(open(TM + 'final/final_cells.json'))
runs = sorted(glob.glob(TM + 'm0/p6_L3_100pct_s*.json')) + sorted(glob.glob(TM + 'm0/p16_A_100pct_s*.json'))
for split, cls, gmin, pmin, name in [('ext', 14, lambda g, a: g >= 20, lambda p, a: p >= 50, 'crack'),
                                     ('test', 11, lambda g, a: g >= 0.005 * a, lambda p, a: p >= 0.005 * a, 'inactive'),
                                     ('ext', 11, lambda g, a: g >= 0.005 * a, lambda p, a: p >= 0.005 * a, 'inactive')]:
    models = [('FINAL b0.75', F[split]['final_b0.75']), ('FINAL b0', F[split]['final_b0'])] + \
             [(r.split('/')[-1][:-5], json.load(open(r))['cells'][split]) for r in runs]
    for mname, cells in models:
        c = counts(cells, cls)
        if split == 'test':
            c = {s: v for s, v in c.items() if s != 'CSIR_00070_r8_c4'}
        tp = sum(gmin(g, a) and pmin(p, a) for g, p, a in c.values()); P = sum(gmin(g, a) for g, p, a in c.values())
        N = sum(g == 0 for g, p, a in c.values()); fa = sum(g == 0 and pmin(p, a) for g, p, a in c.values())
        print(f'{split} {name} {mname}: positive cells {P}, detected {tp} ({tp / max(P, 1):.2f}); GT-free cells {N}, false alarms {fa} ({fa / max(N, 1):.2f})')
