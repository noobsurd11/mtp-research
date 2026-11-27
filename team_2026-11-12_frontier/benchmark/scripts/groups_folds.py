#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Physical-module groups over the whole labelled corpus, checks against the
frozen B6 groups / folds, and draft fold tables. CPU; reads list files and ground-truth masks only.
Run: python -I groups_folds.py DATASETS_DIR RESEARCH_DIR OUT_DIR   (after corpus_build.py)"""
import sys, collections
import numpy as np
from PIL import Image
DS, RS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
log = open(f'{OUT}/groups_folds_summary.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n')
hdr, *rows = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/cells.tsv')]
C = [dict(zip(hdr, r)) for r in rows]
for c in C:
    for k in ('crack_px', 'inactive_px', 'scuff_px', 'halfcut_sp_px', 'crack_comp', 'crack_comp20'): c[k] = int(c[k])
by = {c['stem']: c for c in C}
fl = lambda x: float(x) if x not in ('nan', '') else float('nan')
pairs = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/pairs.tsv')][1:]

# ---- legacy 24-class masks (masks_escdd rebuilt): E-SCDD mask, classes >= 24 put back to the old label; 5 cells old mask
def legacy_mask(stem):
    b21 = f'{DS}/BenchmarkELimages/dataset_20211104'
    sp = by[stem]['role']
    old = np.array(Image.open(f"{b21}/masks_coded_{'train_original' if sp == 'train' else sp}/{stem}.png"))
    if old.ndim == 3: old = old[..., 0]
    rel = dict(x.split(':') for x in by[stem]['releases'].split('|'))
    if 'escdd' not in rel: return old
    m = np.array(Image.open(f"{DS}/escdd_full/el_masks_{rel['escdd']}/{stem}.png"))
    if m.ndim == 3: m = m[..., 0]
    m = m.copy(); hi = m >= 24; m[hi] = old[hi]
    return m
leg = {}
for c in C:
    if c['role'] in ('train', 'val', 'test'):
        m = legacy_mask(c['stem']); px = np.bincount(m.ravel(), minlength=24)
        leg[c['stem']] = px
        c['leg_crack'], c['leg_inact'] = int(px[14]), int(px[11])
P('## A. Legacy masks_escdd rebuilt locally (check against handbook 03 §2.2: crack 209 / 23 / 48, inactive 42 / 6 / 16)')
for sp in ('train', 'val', 'test'):
    v = [c for c in C if c['role'] == sp]
    P(f"  {sp}: cells {len(v)}; crack cells {sum(c['leg_crack'] > 0 for c in v)} (E-SCDD own masks {sum(c['crack_px'] > 0 for c in v)}); "
      f"inactive cells {sum(c['leg_inact'] > 0 for c in v)}; crack px {sum(c['leg_crack'] for c in v)} (E-SCDD own {sum(c['crack_px'] for c in v)}); crack-free cells {sum(c['leg_crack'] == 0 for c in v)}")
np.save(f'{OUT}/legacy_classpx.npy', np.stack([leg[c['stem']] for c in C if c['stem'] in leg]))
with open(f'{OUT}/legacy_stems.txt', 'w') as f:
    for c in C:
        if c['stem'] in leg: f.write(f"{c['stem']}\t{c['role']}\n")

# ---- groups: union-find over image ids (module field)
par = {}
def f(x):
    par.setdefault(x, x)
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
def u(a, b): par[f(a)] = f(b)
for c in C: f(c['module'])
edges = []
for r in pairs:
    hr, a, b, ii, ci = float(r[0]), r[1], r[3], fl(r[5]), fl(r[6])
    if a.startswith(('BMRK', 'SDLE')): continue
    if (ii >= 0.2) or (ci >= 0.2) or (a.startswith('CFVS') and hr >= 0.90):
        edges.append((hr, a, b, ii, ci)); u(by[a]['module'], by[b]['module'])
D6 = [('CFVS_00032_r8_c4', 'CFVS_00037_r8_c4'), ('CFVS_00017_r4_c4', 'CFVS_00031_r4_c4'), ('CFVS_00009_r7_c4', 'CFVS_00012_r7_c4'),
      ('ARTS_00061_r1_c6', 'ARTS_00040_r1_c6'), ('CFVS_00006_r5_c5', 'CFVS_00003_r5_c5'), ('CFVS_00033_r8_c4', 'CFVS_00037_r8_c4'),
      ('CFVS_00035_r8_c4', 'CFVS_00037_r8_c4'), ('CFVS_00042_r8_c4', 'CFVS_00037_r8_c4'), ('CFVS_00018_r4_c4', 'CFVS_00020_r4_c4'),
      ('CFVS_00027_r4_c4', 'CFVS_00031_r4_c4'), ('ARTS_00020_r5_c1', 'ARTS_00081_r5_c1')]
for a, b in D6:
    u(by[a]['module'], by[b]['module'])
for c in C: c['grp'] = f(c['module'])
P(f"\n## B. Physical-module groups, whole corpus (rule of judge/b6_groups.py extended; edges {len(edges)} + {len(D6)} listed D6 pairs)")
P(f"  image ids {len({c['module'] for c in C})} -> groups {len({c['grp'] for c in C})}")
g = collections.defaultdict(list)
for c in C: g[c['grp']].append(c)
multi = {k: v for k, v in g.items() if len({c['module'] for c in v}) > 1}
P(f"  groups spanning > 1 image id: {len(multi)}; cells in them {sum(len(v) for v in multi.values())}")
for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1])):
    P(f"    {sorted({c['module'] for c in v})}: cells {len(v)}, roles {dict(collections.Counter(c['role'] for c in v))}, inactive px {sum(c['inactive_px'] for c in v)}, crack px {sum(c['crack_px'] for c in v)}")
# check against frozen B6 groups on the 532
b6 = {}
for l in list(open(f'{RS}/team_2026-10-31_next/judge/out/b6_groups.tsv'))[1:]:
    a = l.rstrip('\n').split('\t'); b6[a[0]] = a[3]
mine = collections.defaultdict(set); theirs = collections.defaultdict(set)
for s, gg in b6.items(): theirs[gg].add(s); mine[by[s]['grp']].add(s)
same = {frozenset(v) for v in mine.values()} == {frozenset(v) for v in theirs.values()}
P(f"  partition of the 532 train + val cells equal to judge's b6_groups.tsv: {same} (mine {len(mine)} groups, judge {len(theirs)})")
if not same:
    for v in mine.values():
        gs = {b6[s] for s in v}
        if len(gs) > 1: P('    my group merges B6 groups', sorted(gs), 'via', sorted({by[s]['module'] for s in v}))
    for v in theirs.values():
        gs = {by[s]['grp'] for s in v}
        if len(gs) > 1: P('    B6 group split in mine', sorted(gs))
# leakage by role pairs at group level
def roles(v): return {c['role'] for c in v}
tw = [c for c in C if c['role'] == 'test' and any(o['role'] in ('train', 'val') and o['module'] != c['module'] for o in g[c['grp']])]
P(f"  test cells in a group with a train / val cell of ANOTHER image id (twin candidates by this rule): {len(tw)}: {[c['stem'] for c in tw]}")
P(f"    their crack px {sum(c['leg_crack'] for c in tw)} of {sum(c['leg_crack'] for c in C if c['role'] == 'test')} (legacy masks); inactive px {sum(c['leg_inact'] for c in tw)} of {sum(c['leg_inact'] for c in C if c['role'] == 'test')}")
sm = [c for c in C if c['role'] == 'test' and any(o['role'] in ('train',) for o in g[c['grp']])]
P(f"  test cells whose group (image id or twin) has a train cell: {len(sm)}; with a val cell: {len([c for c in C if c['role'] == 'test' and any(o['role'] == 'val' for o in g[c['grp']])])}")
vm = [c for c in C if c['role'] == 'val' and any(o['role'] == 'train' for o in g[c['grp']])]
P(f"  val cells whose group has a train cell: {len(vm)}")
e1g = {c['grp'] for c in C if c['role'] == 'E1'}
P(f"  E1: image ids {len({c['module'] for c in C if c['role'] == 'E1'})}, groups {len(e1g)}; E1 groups that also hold: "
  + ', '.join(f"{r} cells {sum(1 for c in C if c['role'] == r and c['grp'] in e1g)}" for r in ('train', 'val', 'test', 'ext_in_pool', 'rf_in_pool', 'rf_not_pool')))
for r in ('rf_in_pool', 'rf_not_pool', 'ext_in_pool'):
    gs = {c['grp'] for c in C if c['role'] == r}
    P(f"  {r}: groups {len(gs)}; groups shared with train {len(gs & {c['grp'] for c in C if c['role'] == 'train'})}, val {len(gs & {c['grp'] for c in C if c['role'] == 'val'})}, test {len(gs & {c['grp'] for c in C if c['role'] == 'test'})}, E1 {len(gs & e1g)}")
# unresolved candidates: non-CFVS same-position pairs with hp_r >= 0.9 and no mask evidence, involving test or E1
cand = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in pairs if not r[1].startswith(('BMRK', 'SDLE', 'CFVS')) and float(r[0]) >= 0.9
        and by[r[1]]['grp'] != by[r[3]]['grp'] and ({r[2], r[4]} & {'test', 'E1'}) and len({r[2], r[4]}) > 1]
P(f"  ungrouped non-CFVS same-position pairs with hp_r >= 0.90 touching test or E1 (visual check needed): {len(cand)}: {cand}")
bm = [(r[0], r[1], r[2], r[3], r[4], r[6]) for r in pairs if r[1].startswith('BMRK') and fl(r[6]) >= 0.2]
P(f"  BMRK pairs with crack-mask IoU >= 0.2 (not grouped; BMRK has no module id): {bm}")

# ---- pools
POOL = {
 'P532 train+val': lambda c: c['role'] in ('train', 'val'),
 'P582 legacy all': lambda c: c['role'] in ('train', 'val', 'test'),
 'P593 Pratt labels, no E1': lambda c: c['role'] in ('train', 'val', 'test', 'ext_in_pool'),
 'P693 no E1, no rf_not_pool': lambda c: c['role'] in ('train', 'val', 'test', 'ext_in_pool', 'rf_in_pool'),
 'P699 all Pratt labels': lambda c: c['role'] in ('train', 'val', 'test', 'ext_in_pool', 'E1'),
 'P816 all real': lambda c: True}
def neff(w):
    w = np.array([x for x in w if x > 0], float)
    return float(w.sum() ** 2 / (w ** 2).sum()) if len(w) else 0.0
P('\n## C. Candidate pools (E-SCDD / 20221008 masks; crack cell = any crack px)')
P('  pool | cells | groups | crack cells | crack-free cells | crack comps >= 20 px | inactive cells | inactive groups | n_eff inactive by group (px-weighted) | top-3 group share of inactive px | half-cut cells | sources')
for name, fn in POOL.items():
    v = [c for c in C if fn(c)]
    wi = collections.Counter(); 
    for c in v: wi[c['grp']] += c['inactive_px']
    w = sorted([x for x in wi.values() if x > 0], reverse=True)
    P(f"  {name} | {len(v)} | {len({c['grp'] for c in v})} | {sum(c['crack_px'] > 0 for c in v)} | {sum(c['crack_px'] == 0 for c in v)} | {sum(c['crack_comp20'] for c in v)} | "
      f"{sum(c['inactive_px'] > 0 for c in v)} | {len(w)} | {neff(w):.1f} | {sum(w[:3]) / max(1, sum(w)):.3f} | {sum(c['celltype'].startswith('halfcut') for c in v)} | {dict(collections.Counter(c['source'] for c in v))}")

# ---- frozen B6 folds on the 532, re-tabulated
b6f = {}
for l in list(open(f'{RS}/team_2026-10-31_next/results/b6/b6_folds.tsv'))[1:]:
    a = l.rstrip('\n').split('\t'); b6f[a[0]] = int(a[3])
def foldtab(title, assign, maskkey=('crack_px', 'inactive_px')):
    ck, ik = maskkey
    P(f'\n{title}')
    P('  fold | cells | groups | crack cells | crack-free cells | crack px | inactive cells | inactive px | half-cut | mono / multi / dogbone / no_spacing / halfcut | per source')
    for k in sorted(set(assign.values())):
        v = [by[s] for s, ff in assign.items() if ff == k]
        ct = collections.Counter('halfcut' if c['celltype'].startswith('halfcut') else c['celltype'] for c in v)
        P(f"  {k} | {len(v)} | {len({c['grp'] for c in v})} | {sum(c[ck] > 0 for c in v)} | {sum(c[ck] == 0 for c in v)} | {sum(c[ck] for c in v)} | {sum(c[ik] > 0 for c in v)} | {sum(c[ik] for c in v)} | "
          f"{ct['halfcut']} | {ct['mono']} / {ct['multi']} / {ct['dogbone']} / {ct['no_spacing']} / {ct['halfcut']} | {dict(sorted(collections.Counter(c['source'] for c in v).items()))}")
    split_groups = sum(1 for gg in {by[s]['grp'] for s in assign} if len({assign[s] for s in assign if by[s]['grp'] == gg}) > 1)
    P(f'  groups split across folds: {split_groups}')
foldtab('## D. Frozen B6 folds (md5 e2cafce1) on the 532 cells, legacy masks_escdd rebuilt', b6f, ('leg_crack', 'leg_inact'))

# ---- draft extension: keep the frozen fold of every B6 group; place other groups greedily
def extend(fn, title):
    assign = dict(b6f)
    gf = {}
    conflict = []
    for s, k in b6f.items():
        gg = by[s]['grp']
        if gg in gf and gf[gg] != k: conflict.append((gg, gf[gg], k))
        gf.setdefault(gg, k)
    new = collections.defaultdict(list)
    for c in C:
        if fn(c) and c['stem'] not in assign:
            if c['grp'] in gf: assign[c['stem']] = gf[c['grp']]
            else: new[c['grp']].append(c)
    load = lambda k, key: sum(key(by[s]) for s, ff in assign.items() if ff == k)
    order = sorted(new.items(), key=lambda kv: (-sum(c['inactive_px'] for c in kv[1]), -sum(c['crack_px'] > 0 for c in kv[1]), -len(kv[1]), kv[0]))
    for gg, v in order:
        src = v[0]['source']; hcg = any(c['celltype'].startswith('halfcut') for c in v)
        if sum(c['inactive_px'] for c in v) > 0:
            k = min(range(5), key=lambda k: (load(k, lambda c: c['inactive_px'] if c['stem'] not in b6f else 0), load(k, lambda c: 1)))
        elif hcg:
            k = min(range(5), key=lambda k: (load(k, lambda c: c['celltype'].startswith('halfcut')), load(k, lambda c: 1)))
        elif any(c['crack_px'] > 0 for c in v):
            k = min(range(5), key=lambda k: (load(k, lambda c: (c['crack_px'] > 0) and c['stem'] not in b6f and c['source'] == src), load(k, lambda c: 1)))
        else:
            k = min(range(5), key=lambda k: (load(k, lambda c: c['source'] == src and c['stem'] not in b6f), load(k, lambda c: 1)))
        for c in v: assign[c['stem']] = k
    P(f'\n  [{title}] B6 groups with cells already in two frozen folds through new links: {conflict}')
    foldtab(f'## {title}', assign)
    return assign
a582 = extend(POOL['P582 legacy all'], 'E. DRAFT extension of the frozen folds to P582 (test cells placed with their group, else greedy)')
a693 = extend(POOL['P693 no E1, no rf_not_pool'], 'F. DRAFT extension to P693')
with open(f'{OUT}/draft_folds_P693.tsv', 'w') as fo:
    fo.write('stem\trole\tgroup\tfold\n')
    for s in sorted(a693): fo.write(f"{s}\t{by[s]['role']}\t{by[s]['grp']}\t{a693[s]}\n")
with open(f'{OUT}/groups_all.tsv', 'w') as fo:
    fo.write('stem\trole\tsource\tmodule\tgroup\tcelltype\tcrack_px\tinactive_px\n')
    for c in C: fo.write(f"{c['stem']}\t{c['role']}\t{c['source']}\t{c['module']}\t{c['grp']}\t{c['celltype']}\t{c['crack_px']}\t{c['inactive_px']}\n")

# ---- leave-one-source-out
P('\n## G. Leave-one-source-out over P582 (legacy masks) and over P693 (E-SCDD masks): held-out source = test')
for name, fn, ck, ik in (('P582', POOL['P582 legacy all'], 'leg_crack', 'leg_inact'), ('P693', POOL['P693 no E1, no rf_not_pool'], 'crack_px', 'inactive_px')):
    v = [c for c in C if fn(c)]
    for src in ('ARTS', 'BMRK', 'CFVS', 'CSIR', 'SDLE'):
        t = [c for c in v if c['source'] == src]; tr = [c for c in v if c['source'] != src]
        P(f"  {name} hold out {src}: test {len(t)} cells, crack {sum(c[ck] > 0 for c in t)}, inactive {sum(c[ik] > 0 for c in t)} | train {len(tr)} cells, crack {sum(c[ck] > 0 for c in tr)}, inactive {sum(c[ik] > 0 for c in tr)}")

# ---- E1 strata
P('\n## H. E1 (106) strata (E-SCDD masks; scuff = class 25)')
e1 = [c for c in C if c['role'] == 'E1']
def st(c):
    hcx = c['celltype'].startswith('halfcut'); sc = c['scuff_px'] >= 500
    return ('halfcut' if hcx else 'full') + ('+scuff' if sc else '')
for k in sorted({st(c) for c in e1}):
    v = [c for c in e1 if st(c) == k]
    P(f"  {k}: cells {len(v)}, image ids {len({c['module'] for c in v})}, crack cells {sum(c['crack_px'] >= 20 for c in v)}, crack px {sum(c['crack_px'] for c in v)}, crack-free {sum(c['crack_px'] < 20 for c in v)}, inactive cells {sum(c['inactive_px'] > 0 for c in v)}, inactive px {sum(c['inactive_px'] for c in v)}")
wm = collections.Counter()
for c in e1: wm[c['module']] += c['crack_px']
w = sorted(wm.values(), reverse=True)
P(f"  E1 crack px by image id: top-3 share {sum(w[:3]) / sum(w):.3f}, n_eff {neff(w):.1f}; crack image ids {sum(x > 0 for x in w)}")
wi = collections.Counter()
for c in e1: wi[c['module']] += c['inactive_px']
w = sorted(wi.values(), reverse=True)
P(f"  E1 inactive px by image id: top-3 share {sum(w[:3]) / sum(w):.3f}, n_eff {neff(w):.1f}; inactive image ids {sum(x > 0 for x in w)}")
log.close()
