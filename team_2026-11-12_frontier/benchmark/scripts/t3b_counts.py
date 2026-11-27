#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Counts for the proposed track T3b (few-shot layout adaptation): group K-fold inside E1.
Ground-truth masks and list files only (benchmark/cells.tsv). No predictions.
Grouping units: (a) image id (71); (b) 'family' = run of CSIR image ids with consecutive numbers (gap <= GAP).
Folds: deterministic greedy, no draw: units sorted by (crack px in half-cut+scuff cells, crack px, cells) descending,
each into the fold with the lowest running load of the same key.
Run: python -I t3b_counts.py BENCH_DIR OUT_DIR"""
import sys, collections, re
import numpy as np
BD, OUT = sys.argv[1], sys.argv[2]
h, *r = [l.rstrip('\n').split('\t') for l in open(f'{BD}/cells.tsv')]
E = [dict(zip(h, x)) for x in r if dict(zip(h, x))['role'] == 'E1']
for c in E:
    for k in ('crack_px', 'inactive_px', 'scuff_px', 'crack_comp20'): c[k] = int(c[k])
    c['hc'] = c['cell_type'].startswith('halfcut'); c['hs'] = c['e1_stratum'] == 'halfcut+scuff'
L = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); L.append(s)
P('T3b counts: E1', len(E), 'cells;', len({c['image_id'] for c in E}), 'image ids; crack cells (>= 20 px)', sum(c['crack_px'] >= 20 for c in E),
  '; crack px', sum(c['crack_px'] for c in E), '; crack components >= 20 px', sum(c['crack_comp20'] for c in E), '; half-cut cells', sum(c['hc'] for c in E),
  '; scuff cells (>= 500 px)', sum(c['scuff_px'] >= 500 for c in E), '; inactive cells', sum(c['inactive_px'] > 0 for c in E))
# concentration
w = collections.Counter(); wc = collections.Counter(); wi = collections.Counter()
for c in E: w[c['image_id']] += c['crack_px']; wc[c['image_id']] += c['crack_px'] >= 20; wi[c['image_id']] += c['inactive_px']
tot = sum(w.values())
P('crack px by image id, top 8:', [(k, v, f'{v / tot:.3f}', f'crack cells {wc[k]}') for k, v in w.most_common(8)])
P('cumulative share of crack px, top 1 / 3 / 5 / 10 image ids:', [round(sum(v for _, v in w.most_common(n)) / tot, 3) for n in (1, 3, 5, 10)])
P('inactive px by image id:', [(k, v) for k, v in wi.most_common(7)])
# families
def fam(gap):
    ids = sorted({c['image_id'] for c in E if c['source'] == 'CSIR'}, key=lambda x: int(x.split('_')[1]))
    f = {}; cur = None; prev = None
    for i in ids:
        n = int(i.split('_')[1])
        if prev is None or n - prev > gap: cur = i
        f[i] = cur; prev = n
    for c in E:
        if c['source'] != 'CSIR': f[c['image_id']] = c['image_id']
    return f
for gap in (1, 2, 5, 10, 20):
    f = fam(gap); n = len(set(f.values()))
    fw = collections.Counter()
    for c in E: fw[f[c['image_id']]] += c['crack_px']
    P(f'families with id gap <= {gap}: {n} units; top-3 share of crack px {sum(v for _, v in fw.most_common(3)) / tot:.3f}; units with crack {sum(v > 0 for v in fw.values())}')
P('image-id numbers of the half-cut + scuff crack cells:', sorted({int(c['image_id'].split('_')[1]) for c in E if c['hs'] and c['crack_px'] >= 20}))
P('image-id numbers of all E1 CSIR cells (min, max):', min(int(c['image_id'].split('_')[1]) for c in E if c['source'] == 'CSIR'), max(int(c['image_id'].split('_')[1]) for c in E if c['source'] == 'CSIR'))

def folds(K, unit):
    U = collections.defaultdict(list)
    for c in E: U[unit[c['image_id']]].append(c)
    key = lambda v: (sum(c['crack_px'] for c in v if c['hs']), sum(c['crack_px'] for c in v), len(v))
    order = sorted(U.items(), key=lambda kv: (tuple(-x for x in key(kv[1])), kv[0]))
    load = [[0, 0, 0, 0] for _ in range(K)]; asg = {}
    for u, v in order:
        hs_px, cr_px, n = key(v)
        if hs_px > 0: k = min(range(K), key=lambda k: (load[k][0], load[k][1], load[k][3]))
        elif cr_px > 0: k = min(range(K), key=lambda k: (load[k][1], load[k][3]))
        elif any(c['hc'] for c in v): k = min(range(K), key=lambda k: (load[k][2], load[k][3]))
        else: k = min(range(K), key=lambda k: load[k][3])
        load[k][0] += hs_px; load[k][1] += cr_px; load[k][2] += sum(c['hc'] for c in v); load[k][3] += n
        asg[u] = k
    return {c['stem']: asg[unit[c['image_id']]] for c in E}
def tab(K, unit, name):
    a = folds(K, unit)
    P(f'\nK = {K}, grouped by {name} ({len(set(unit.values()))} units)')
    P('  fold | held-out cells | units | half-cut cells | scuff cells | crack cells | of which half-cut + scuff | crack px (share) | components >= 20 px | crack-free cells | inactive cells (px) | TRAIN side: cells / half-cut / crack cells / half-cut + scuff crack cells / crack px')
    for k in range(K):
        v = [c for c in E if a[c['stem']] == k]; t = [c for c in E if a[c['stem']] != k]
        P(f"  {k} | {len(v)} | {len({unit[c['image_id']] for c in v})} | {sum(c['hc'] for c in v)} | {sum(c['scuff_px'] >= 500 for c in v)} | {sum(c['crack_px'] >= 20 for c in v)} | "
          f"{sum(c['crack_px'] >= 20 and c['hs'] for c in v)} | {sum(c['crack_px'] for c in v)} ({sum(c['crack_px'] for c in v) / tot:.2f}) | {sum(c['crack_comp20'] for c in v)} | "
          f"{sum(c['crack_px'] < 20 for c in v)} | {sum(c['inactive_px'] > 0 for c in v)} ({sum(c['inactive_px'] for c in v)}) | "
          f"{len(t)} / {sum(c['hc'] for c in t)} / {sum(c['crack_px'] >= 20 for c in t)} / {sum(c['crack_px'] >= 20 and c['hs'] for c in t)} / {sum(c['crack_px'] for c in t)}")
    # top image share inside each held-out fold
    for k in range(K):
        fw = collections.Counter()
        for c in E:
            if a[c['stem']] == k: fw[c['image_id']] += c['crack_px']
        s = sum(fw.values())
        P(f"    fold {k}: largest image id holds {fw.most_common(1)[0][1] / max(1, s):.2f} of the fold's crack px ({fw.most_common(1)[0][0]})")
    return a
ident = {c['image_id']: c['image_id'] for c in E}
a3 = tab(3, ident, 'image id'); a5 = tab(5, ident, 'image id')
f5 = fam(5)
tab(3, f5, 'family (id gap <= 5)'); tab(5, f5, 'family (id gap <= 5)')
with open(f'{OUT}/t3b_draft_folds.tsv', 'w') as fo:
    fo.write('stem\timage_id\tfamily_gap5\te1_stratum\tcrack_px\tk3_fold\tk5_fold\n')
    for c in E: fo.write(f"{c['stem']}\t{c['image_id']}\t{f5[c['image_id']]}\t{c['e1_stratum']}\t{c['crack_px']}\t{a3[c['stem']]}\t{a5[c['stem']]}\n")
open(f'{OUT}/t3b_counts.txt', 'w').write('\n'.join(L) + '\n')
