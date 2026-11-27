#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Final cell table of the benchmark: benchmark/cells.tsv (816 rows) + cells.md5.
Inputs: out/cells.tsv, out/groups_all.tsv, out/pairs.tsv, out/classpx.npy, out/legacy_*.npy/txt (corpus_build.py,
groups_folds.py), splits/cv5v2_groups.tsv (make_splits.py), out/masks_v11/MANIFEST.tsv + masks (make_masks_v11.py),
judge/out/rf_sets.tsv, the local images (noise sigma only). No predictions, no result files.
Run: python -I make_cells_table.py DATASETS_DIR RESEARCH_DIR OUT_DIR SPLITS_DIR BENCH_DIR"""
import sys, os, collections, hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
DS, RS, OUT, SP, BD = sys.argv[1:6]
def tsv(p):
    h, *r = [l.rstrip('\n').split('\t') for l in open(p)]
    return [dict(zip(h, x)) for x in r]
C = tsv(f'{OUT}/cells.tsv'); G = {g['stem']: g for g in tsv(f'{OUT}/groups_all.tsv')}
px = np.load(f'{OUT}/classpx.npy'); idx = {c['stem']: i for i, c in enumerate(C)}
fold = {r['stem']: int(r['fold']) for r in tsv(f'{SP}/cv5v2_groups.tsv')}
leg = np.load(f'{OUT}/legacy_classpx.npy'); ls = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/legacy_stems.txt')]
lpx = {s: leg[i] for i, (s, _) in enumerate(ls)}
man = {r['stem']: r for r in tsv(f'{OUT}/masks_v11/MANIFEST.tsv')}
rfset = {r['stem']: r['set'] for r in tsv(f'{RS}/team_2026-10-31_next/judge/out/rf_sets.tsv')}
pool = {l.strip() for l in open(f'{DS}/splits_benchmark/external_unlabeled.txt') if l.strip()}
# group names = smallest image id in the group
mem = collections.defaultdict(set)
for g in G.values(): mem[g['group']].add(g['module'])
gname = {k: min(v) for k, v in mem.items()}

def ipath(c):
    rel = dict(x.split(':') for x in c['releases'].split('|')); mv = c['maskver']
    if mv == 'escdd': return f"{DS}/escdd_full/el_images_{rel['escdd']}/{c['stem']}.png"
    if mv == '20211104_or_20220723' or mv == '20220723': return f"{DS}/BenchmarkEL_releases/dataset_20220723/el_images_{rel['20220723']}/{c['stem']}.png"
    return f"{DS}/BenchmarkEL_releases/dataset_{mv}/el_images_{rel[mv]}/{c['stem']}.png"
def sigma(c):
    im = np.asarray(Image.open(ipath(c)).convert('L'), dtype=np.float32)
    return float(np.median(np.abs(im - ndi.median_filter(im, size=5))) * 1.4826)   # scripts/cell_noise_rank.py (P16)

TW_TEST = {'CFVS_00006_r5_c5', 'CFVS_00033_r8_c4', 'CFVS_00035_r8_c4', 'CFVS_00042_r8_c4', 'CFVS_00018_r4_c4', 'CFVS_00027_r4_c4', 'ARTS_00020_r5_c1'}
TW_TRAIN = {'CFVS_00003_r5_c5', 'CFVS_00037_r8_c4', 'CFVS_00032_r8_c4', 'CFVS_00020_r4_c4', 'CFVS_00022_r4_c4', 'CFVS_00031_r4_c4', 'ARTS_00081_r5_c1'}
CAND = {'CFVS_00063_r3_c1', 'ARTS_00030_r8_c6'}
pairs = tsv(f'{OUT}/pairs.tsv')
fl = lambda x: float(x) if x not in ('nan', '') else float('nan')
copy_exact, copy_near = set(), set()
for r in pairs:
    a, b = r['a'], r['b']
    if a[:4] in ('BMRK', 'SDLE') or G[a]['group'] != G[b]['group']: continue
    ci = fl(r['crack_iou'])
    if int(r['crack_a']) >= 100 and int(r['crack_b']) >= 100:
        if ci >= 0.999: copy_exact |= {a, b}
        elif ci >= 0.85: copy_near |= {a, b}
byh = collections.Counter(c['img_md5'] for c in C)
e1groups = {G[c['stem']]['group'] for c in C if c['role'] == 'E1'}
grp_roles = collections.defaultdict(set)
for c in C: grp_roles[G[c['stem']]['group']].add((c['role'], c['module']))
cellkey = {}
for c in C:
    g = gname[G[c['stem']]['group']]
    cellkey[c['stem']] = f"{g}_r{c['pos'].strip('()').split(', ')[0]}_c{c['pos'].strip('()').split(', ')[1]}" if c['pos'] != 'None' else c['stem']
ncell = collections.Counter(cellkey.values())

rows = []
for c in C:
    s = c['stem']; p = px[idx[s]]; role = c['role']; g = G[s]['group']
    legacy = role in ('train', 'val', 'test')
    if role in ('train', 'val'): bset = f'cv5v2:f{fold[s]}'
    elif role == 'test': bset = 'test50'
    elif role == 'E1': bset = 'e1_106'
    elif role == 'ext_in_pool': bset = 'aux_ext11'
    else: bset = 'aux_rf117'
    stratum = ''
    if role == 'E1':
        stratum = ('halfcut' if c['celltype'].startswith('halfcut') else 'full') + ('+scuff' if int(c['scuff_px']) >= 500 else '')
    sg = sigma(c)
    fl_ = []
    if sg > 10: fl_.append('noisy')
    if s in TW_TEST: fl_.append('twin_test_d6')
    if s in TW_TRAIN: fl_.append('twin_train_d7')
    if role == 'test' and s not in TW_TEST and any(r in ('train', 'val') and m != c['module'] for r, m in grp_roles[g]):
        fl_.append('module_link_test')
    if s in CAND: fl_.append('twin_candidate_unchecked')
    if byh[c['img_md5']] > 1: fl_.append('dup_image')
    if s in copy_exact: fl_.append('mask_copy_exact')
    elif s in copy_near: fl_.append('mask_copy_near')
    if s == 'BMRK_00031_cell0091': fl_.append('wrong_mask_v1')
    if s == 'BMRK_00075_cell0255': fl_.append('mask_donor')
    if legacy and int(man[s]['ignore_px']) > 0:
        fl_.append('scuff_or_star_v1')
        if int(lpx[s][14]) > int(p[14]) and s != 'BMRK_00031_cell0091': fl_.append('scuff_or_star_as_crack_v1')
    if rfset.get(s) == 'H36': fl_.append('rf_speck_crack_labels')
    if role.startswith('rf') and p[11] > 0 and p[14] == 0: fl_.append('inactive_without_crack')
    if role in ('rf_in_pool', 'rf_not_pool', 'ext_in_pool') and g in e1groups: fl_.append('same_module_as_e1')
    if '20221008' not in c['releases'] and legacy: fl_.append('dropped_from_20221008')
    if 'escdd' not in c['releases']: fl_.append('not_in_escdd')
    v11c = v11i = ''
    if legacy:
        m = np.array(Image.open(f'{OUT}/masks_v11/masks/{s}.png'))
        v11c = int((m == 14).sum()); v11i = int((m == 255).sum())
    nonpad = 262144 - int(p[7])
    rows.append(dict(
        stem=s, source=c['source'], image_id=c['module'], position=('r%s_c%s' % tuple(c['pos'].strip('()').split(', '))) if c['pos'] != 'None' else '-',
        module_group=gname[g], cell_id=cellkey[s], n_images_of_cell=ncell[cellkey[s]], cell_type=c['celltype'],
        label_source='hanifi' if s.endswith('_rf') else 'pratt', mask_version={'escdd': 'escdd', '20221008': '20221008', '20220723': '20211104'}[c['maskver']],
        role=role, bench_set=bset, rf_set=rfset.get(s, 'excluded' if s.endswith('_rf') else ''), e1_stratum=stratum,
        in_unlabelled_pool=int((s[:-3] if s.endswith('_rf') else s) in pool),
        has_crack=int(p[14] > 0), has_inactive=int(p[11] > 0), has_scuff=int(p[25] > 0),
        crack_px=int(p[14]), inactive_px=int(p[11]), scuff_px=int(p[25]), crack_comp20=c['crack_comp20'],
        inactive_area_pct=f'{100 * p[11] / max(1, nonpad):.3f}',
        crack_px_v1=int(lpx[s][14]) if legacy else '', inactive_px_v1=int(lpx[s][11]) if legacy else '', crack_px_v11=v11c, ignore_px_v11=v11i,
        noise_sigma=f'{sg:.2f}', flags=';'.join(fl_)))
cols = list(rows[0].keys())
with open(f'{BD}/cells.tsv', 'w') as f:
    f.write('\t'.join(cols) + '\n')
    for r in rows: f.write('\t'.join(str(r[k]) for k in cols) + '\n')
md5 = hashlib.md5(open(f'{BD}/cells.tsv', 'rb').read()).hexdigest()
open(f'{BD}/cells.md5', 'w').write(f'{md5}  cells.tsv\n')
print('rows', len(rows), 'cols', len(cols), 'md5', md5)
print('bench_set', dict(collections.Counter(r['bench_set'] for r in rows)))
fc = collections.Counter()
for r in rows:
    for x in r['flags'].split(';'):
        if x: fc[(x, r['role'])] += 1
for k in sorted(fc): print('  flag', k, fc[k])
sg = np.array([float(r['noise_sigma']) for r in rows])
print('noise sigma, 816 cells: median %.2f, 95th pct %.2f; cells > 10:' % (np.median(sg), np.percentile(sg, 95)), [(r['stem'], r['role'], r['noise_sigma']) for r in rows if float(r['noise_sigma']) > 10])
print('next highest:', sorted([(float(r['noise_sigma']), r['stem'], r['role']) for r in rows if float(r['noise_sigma']) <= 10], reverse=True)[:6])
print('unique cell_id', len({r['cell_id'] for r in rows}), 'unique module_group', len({r['module_group'] for r in rows}), 'unique image_id', len({r['image_id'] for r in rows}))
print('cv5v2 held-out cells with ignore px per fold:', {k: sum(1 for r in rows if r['bench_set'] == f'cv5v2:f{k}' and r['ignore_px_v11'] not in ('', 0)) for k in range(5)},
      '; wrong_mask cell fold:', [r['bench_set'] for r in rows if 'wrong_mask_v1' in r['flags']])
