#!/usr/bin/env python3
"""judge helper: per-cell count of same-module neighbour cells available in each local source.
Read-only; CPU; stdlib only. Output: judge/out/module_avail.tsv and a summary to stdout.
Module key = stem minus the trailing cell part (_rN_cM, _cellNNNN, -cellNN)."""
import os, re, csv, collections, sys
R = '/home/yugma/mtp/research'
D = os.path.expanduser('~/mtp/datasets')
OUT = f'{R}/team_2026-10-31_next/judge/out'; os.makedirs(OUT, exist_ok=True)

def module(stem):
    s = re.sub(r'_rf$', '', stem)
    m = re.match(r'^(.*)_r(\d+)_c(\d+)$', s)
    if m: return m.group(1), int(m.group(2)), int(m.group(3))
    m = re.match(r'^(BMRK_\d+)_cell(\d+)$', s)
    if m: return m.group(1), None, int(m.group(2))
    m = re.match(r'^(SDLE_\d+_.*?)-cell(\d+)$', s)
    if m: return m.group(1), None, int(m.group(2))
    return s, None, None

def rd(p): return [l.strip() for l in open(p) if l.strip()]
sets = {}
sets['train'] = rd(f'{D}/splits_benchmark/train.txt')
sets['val'] = rd(f'{D}/splits_benchmark/val.txt')
sets['test'] = rd(f'{D}/splits_benchmark/test.txt')
sets['e1'] = [l.split('\t')[0] for l in rd(f'{R}/team_2026-10-29_features/scripts/e1_context.tsv')]
sets['pool11938'] = rd(f'{D}/splits_benchmark/external_unlabeled.txt')
rel = []
for sp in ('train', 'val', 'test'):
    rel += [f[:-4] for f in os.listdir(f'{D}/BenchmarkEL_releases/dataset_20221008/el_images_{sp}') if f.endswith('.png')]
sets['rel20221008'] = rel
esc = []
for sp in ('train', 'val', 'test'):
    p = f'{D}/escdd_full/el_images_{sp}'
    if os.path.isdir(p): esc += [f[:-4] for f in os.listdir(p) if f.endswith('.png')]
sets['escdd_rf'] = [s for s in esc if s.endswith('_rf')]
hf = []
mp = f'{R}/team_2026-10-29_features/pool_large/out/manifest.tsv'
if os.path.exists(mp):
    with open(mp) as f:
        next(f)
        for l in f:
            hf.append(l.rstrip('\n').split('\t')[6][:-4])
sets['hf159k'] = hf
cellsets = {k: set(v) for k, v in sets.items()}
modcells = {k: collections.defaultdict(set) for k in sets}
for k, v in sets.items():
    for s in v: modcells[k][module(s)[0]].add(re.sub(r'_rf$', '', s))
print('set sizes:', {k: len(v) for k, v in sets.items()})
print('distinct modules:', {k: len(modcells[k]) for k in sets})
rows = []
for tgt in ('train', 'val', 'test', 'e1'):
    for s in sets[tgt]:
        mod = module(s)[0]
        r = {'set': tgt, 'stem': s, 'module': mod}
        for k in sets:
            r['n_' + k] = len(modcells[k].get(mod, set()) - {s})
        allc = set()
        for k in sets: allc |= modcells[k].get(mod, set())
        r['n_any'] = len(allc - {s})
        rows.append(r)
keys = list(rows[0].keys())
with open(f'{OUT}/module_avail.tsv', 'w') as f:
    w = csv.DictWriter(f, keys, delimiter='\t'); w.writeheader(); w.writerows(rows)
ctx = {l.split('\t')[0]: l.strip().split('\t')[1:] for l in open(f'{R}/team_2026-10-29_features/scripts/e1_context.tsv')}
for tgt in ('train', 'val', 'test', 'e1'):
    rr = [r for r in rows if r['set'] == tgt]
    for thr in (1, 3, 8):
        print(f'{tgt:5s} cells with >= {thr} same-module neighbours anywhere: {sum(r["n_any"] >= thr for r in rr)}/{len(rr)}', end='; ')
    print()
    for k in ('train','val','test','e1','pool11938','rel20221008','hf159k'):
        print(f'   via {k:12s}: >=3 {sum(r["n_"+k] >= 3 for r in rr):4d}  >=8 {sum(r["n_"+k] >= 8 for r in rr):4d}  median {sorted(r["n_"+k] for r in rr)[len(rr)//2]}')
e1r = [r for r in rows if r['set'] == 'e1']
for grp in ('halfcut=1', 'halfcut=0'):
    rr = [r for r in e1r if grp in ctx[r['stem']]]
    print(f'E1 {grp}: n={len(rr)}; >=3 nbrs any {sum(r["n_any"]>=3 for r in rr)}; >=8 {sum(r["n_any"]>=8 for r in rr)}; modules {len(set(r["module"] for r in rr))}')
