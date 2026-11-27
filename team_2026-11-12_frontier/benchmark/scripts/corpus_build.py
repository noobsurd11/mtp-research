#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Corpus census for the benchmark protocol draft. CPU, read-only on data.
Run: python -I corpus_build.py DATASETS_DIR RESEARCH_DIR OUT_DIR
Reads images and ground-truth masks only (no predictions, no result JSONs).
Outputs OUT_DIR/cells.tsv (one row per real labelled cell), classpx.npy (cells x 30 px counts),
pairs.tsv (same-source same-position near-duplicate screen), corpus_summary.txt."""
import os, re, sys, hashlib, itertools, collections
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

DS, RS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
log = open(f'{OUT}/corpus_summary.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n')
rd = lambda p: [l.strip() for l in open(p) if l.strip()]
SYN = re.compile(r'^\d+-.+_rf$')

def ls(d):
    return sorted(f[:-4] for f in os.listdir(d) if f.endswith('.png'))

# ---------- 1. enumerate releases
rel = {}  # release -> {stem: (split, image path, mask path)}
b21 = f'{DS}/BenchmarkELimages/dataset_20211104'
rel['20211104'] = {}
for sp, idir, mdir in (('train', 'images_train_original', 'masks_coded_train_original'),
                       ('val', 'images_val', 'masks_coded_val'), ('test', 'images_test', 'masks_coded_test')):
    for s in ls(f'{b21}/{idir}'):
        rel['20211104'][s] = (sp, f'{b21}/{idir}/{s}.png', f'{b21}/{mdir}/{s}.png')
for r in ('20220723', '20221008'):
    b = f'{DS}/BenchmarkEL_releases/dataset_{r}'
    rel[r] = {}
    for sp in ('train', 'val', 'test'):
        for s in ls(f'{b}/el_images_{sp}'):
            rel[r][s] = (sp, f'{b}/el_images_{sp}/{s}.png', f'{b}/el_masks_{sp}/{s}.png')
be = f'{DS}/escdd_full'
rel['escdd'] = {}; syn = {}
for sp in ('train', 'val', 'test'):
    for s in ls(f'{be}/el_images_{sp}'):
        t = (sp, f'{be}/el_images_{sp}/{s}.png', f'{be}/el_masks_{sp}/{s}.png')
        (syn if SYN.match(s) else rel['escdd'])[s] = t
P('## 1. Files per release (real cells; synthetic listed apart)')
for r, d in rel.items():
    c = collections.Counter(v[0] for v in d.values())
    P(f'  {r}: {len(d)} cells; split {dict(c)}')
P(f'  escdd synthetic files: {len(syn)}; split {dict(collections.Counter(v[0] for v in syn.values()))}; '
  f'base cells {dict(collections.Counter(re.sub(r"^[0-9]+-", "", s).rsplit("_", 2)[0] if False else re.match(r"^[0-9]+-((?:[A-Z]+_[0-9]+_r[0-9]+_c[0-9]+)(?:_rf)?)_", s).group(1) for s in syn))}')
rf = {s for s in rel['escdd'] if s.endswith('_rf')}
P(f'  escdd real: {len(rel["escdd"])} = {len(rel["escdd"]) - len(rf)} non-rf + {len(rf)} _rf')

ours = {s: 'train' for s in rd(f'{DS}/splits_benchmark/train.txt')}
ours.update({s: 'val' for s in rd(f'{DS}/splits_benchmark/val.txt')})
ours.update({s: 'test' for s in rd(f'{DS}/splits_benchmark/test.txt')})
assert set(ours) == set(rel['20211104']), 'split lists != 20211104 folders'
pool = set(rd(f'{DS}/splits_benchmark/external_unlabeled.txt'))
poolgrp = {}
for l in rd(f'{DS}/splits_benchmark/external_unlabeled_meta.csv')[1:]:
    a = l.split(','); poolgrp[a[0]] = a[2]
rfset = {}
for l in rd(f'{RS}/team_2026-10-31_next/judge/out/rf_sets.tsv')[1:]:
    a = l.split('\t'); rfset[a[0]] = a[1]

allst = set().union(*[set(d) for d in rel.values()])
P(f'\n## 2. Union of real labelled stems over all releases: {len(allst)}')
names = ['20211104', '20220723', '20221008', 'escdd']
memb = collections.Counter(tuple(int(s in rel[r]) for r in names) for s in allst)
P('  membership pattern (20211104, 20220723, 20221008, escdd): count')
for k, v in sorted(memb.items(), key=lambda kv: -kv[1]): P(f'    {k}: {v}')
rf_base_clash = [s for s in rf if s[:-3] in allst]
P(f'  _rf cells whose base stem (without _rf) is also a labelled stem: {len(rf_base_clash)} {rf_base_clash[:5]}')
P(f'  our 582 not in 20221008: {sorted(set(ours) - set(rel["20221008"]))}')
P(f'  our 582 not in escdd: {sorted(set(ours) - set(rel["escdd"]))}')
P(f'  20221008 not in escdd: {sorted(set(rel["20221008"]) - set(rel["escdd"]))}')
P(f'  20220723 not in 20221008: {sorted(set(rel["20220723"]) - set(rel["20221008"]))}')
P(f'  20211104 not in 20220723: {len(set(ours) - set(rel["20220723"]))}')
ext = set(rel['20221008']) - set(ours)
e1 = ext - pool
P(f'  20221008 cells not among our 582: {len(ext)}; of these in the 11,938 pool: {len(ext & pool)}; E1 = {len(e1)}')
P(f'  _rf cells with base stem in the 11,938 pool: {sum(s[:-3] in pool for s in rf)} of {len(rf)}')
# split moves between releases
for a, b in (('20211104', '20220723'), ('20211104', '20221008'), ('20220723', '20221008'), ('20221008', 'escdd'), ('20211104', 'escdd')):
    com = set(rel[a]) & set(rel[b])
    mv = collections.Counter((rel[a][s][0], rel[b][s][0]) for s in com if rel[a][s][0] != rel[b][s][0])
    P(f'  split changes {a} -> {b}: common {len(com)}, in a different split {sum(mv.values())}; {dict(mv)}')

# ---------- 2. per-cell record
def key(stem):
    s = stem[:-3] if stem.endswith('_rf') else stem
    m = re.match(r'^(.*)_r(\d+)_c(\d+)$', s)
    if m: return m.group(1), (int(m.group(2)), int(m.group(3)))
    m = re.match(r'^(.*?)[_-]cell(\d+)$', s)
    if m: return m.group(1), None
    return s, None

def rmask(p):
    m = np.array(Image.open(p))
    if m.ndim == 3: m = m[..., 0]
    return m

cells = []
for s in sorted(allst):
    if s in rel['escdd']: mv = 'escdd'
    elif s in rel['20221008']: mv = '20221008'
    elif s in rel['20220723']: mv = '20220723'
    else: mv = '20211104'
    sp, ip, mp = rel[mv][s]
    m = rmask(mp)
    px = np.bincount(m.ravel(), minlength=30)[:30]
    assert m.max() < 30, (s, m.max())
    mod, pos = key(s)
    base = s[:-3] if s.endswith('_rf') else s
    if s in ours: role = ours[s]
    elif s in e1: role = 'E1'
    elif s in ext: role = 'ext_in_pool'
    elif s in rf: role = 'rf_in_pool' if base in pool else 'rf_not_pool'
    else: role = 'other'
    lab, ncc = ndi.label(m == 14, structure=np.ones((3, 3)))
    sizes = np.bincount(lab.ravel())[1:] if ncc else np.array([])
    img = np.asarray(Image.open(ip).convert('L'))
    cells.append(dict(stem=s, src=s[:4], module=mod, pos=pos, role=role, maskver=mv, px=px, ip=ip, mp=mp,
                      rfset=rfset.get(s, ''), poolgrp=poolgrp.get(base, ''), ncomp=int(ncc),
                      ncomp20=int((sizes >= 20).sum()), imd5=hashlib.md5(img.tobytes()).hexdigest(),
                      shape=img.shape, splits='|'.join(f'{r}:{rel[r][s][0]}' for r in names if s in rel[r])))
P(f'\n## 3. Cells: {len(cells)}; image shapes {collections.Counter(c["shape"] for c in cells).most_common(3)}')
P('  mask version used per cell:', dict(collections.Counter(c['maskver'] for c in cells)))
P('  role:', dict(collections.Counter(c['role'] for c in cells)))

# cell type from spacing classes: 1 sp multi, 2 sp mono, 3 sp dogbone, 24 sp mono halfcut, 29 sp multi halfcut
def ctype(c, hc_min=1):
    px = c['px']; hm, hmu = int(px[24]), int(px[29])
    mono, multi, dog = int(px[2]), int(px[1]), int(px[3])
    if hm + hmu >= hc_min: return 'halfcut_mono' if hm >= hmu else 'halfcut_multi'
    if dog > max(mono, multi): return 'dogbone'
    if mono == 0 and multi == 0: return 'no_spacing'
    return 'mono' if mono > multi else 'multi'
for c in cells: c['ctype'] = ctype(c)
hc = sorted(int(c['px'][24] + c['px'][29]) for c in cells if c['px'][24] + c['px'][29] > 0)
P(f'  cells with any half-cut spacing px (24 or 29): {len(hc)}; px quantiles min/10/50/90/max: '
  f'{hc[0]} / {hc[len(hc)//10]} / {hc[len(hc)//2]} / {hc[9*len(hc)//10]} / {hc[-1]}; <500 px: {sum(h < 500 for h in hc)}')
P('  cell type x pool group label (for cells with a pool copy):',
  dict(collections.Counter((c['ctype'], c['poolgrp']) for c in cells if c['poolgrp'])))

np.save(f'{OUT}/classpx.npy', np.stack([c['px'] for c in cells]))
with open(f'{OUT}/cells.tsv', 'w') as f:
    f.write('stem\tsource\tmodule\tpos\trole\trfset\tcelltype\tmaskver\tcrack_px\tinactive_px\tscuff_px\thalfcut_sp_px\tcrack_comp\tcrack_comp20\timg_md5\treleases\n')
    for c in cells:
        f.write(f"{c['stem']}\t{c['src']}\t{c['module']}\t{c['pos']}\t{c['role']}\t{c['rfset']}\t{c['ctype']}\t{c['maskver']}\t"
                f"{int(c['px'][14])}\t{int(c['px'][11])}\t{int(c['px'][25])}\t{int(c['px'][24] + c['px'][29])}\t{c['ncomp']}\t{c['ncomp20']}\t{c['imd5']}\t{c['splits']}\n")

def tab(title, rows, keyf, cols=('n', 'crack', 'inact', 'modules')):
    P(f'\n{title}')
    g = collections.defaultdict(list)
    for c in rows: g[keyf(c)].append(c)
    P('  key | cells | crack cells (>0 px) | crack cells >=20 px | inactive cells | modules (image ids) | crack px | inactive px')
    for k in sorted(g, key=str):
        v = g[k]
        P(f"  {k} | {len(v)} | {sum(c['px'][14] > 0 for c in v)} | {sum(c['px'][14] >= 20 for c in v)} | {sum(c['px'][11] > 0 for c in v)} | "
          f"{len({c['module'] for c in v})} | {int(sum(c['px'][14] for c in v))} | {int(sum(c['px'][11] for c in v))}")
    v = rows
    P(f"  ALL | {len(v)} | {sum(c['px'][14] > 0 for c in v)} | {sum(c['px'][14] >= 20 for c in v)} | {sum(c['px'][11] > 0 for c in v)} | "
      f"{len({c['module'] for c in v})} | {int(sum(c['px'][14] for c in v))} | {int(sum(c['px'][11] for c in v))}")

tab('## 4a. By role (benchmark mask version: E-SCDD / 20221008 where it exists)', cells, lambda c: c['role'])
tab('## 4b. By source', cells, lambda c: c['src'])
tab('## 4c. By cell type', cells, lambda c: c['ctype'])
tab('## 4d. By source x cell type', cells, lambda c: (c['src'], c['ctype']))
tab('## 4e. By role x cell type', cells, lambda c: (c['role'], c['ctype']))
tab('## 4f. By role x source', cells, lambda c: (c['role'], c['src']))
tab('## 4g. _rf cells by judge set (F51 / H36 / F19 / not in sets)', [c for c in cells if c['stem'] in rf], lambda c: c['rfset'] or 'excluded_by_hygiene')
P('\n  inactive without crack (cells):', sum(c['px'][11] > 0 and c['px'][14] == 0 for c in cells),
  [c['stem'] for c in cells if c['px'][11] > 0 and c['px'][14] == 0][:10])
P('  scuff (25) cells / px by role:', {r: (sum(c['px'][25] > 0 for c in cells if c['role'] == r), int(sum(c['px'][25] for c in cells if c['role'] == r))) for r in sorted({c['role'] for c in cells})})

# ---------- 3. duplicates
byh = collections.defaultdict(list)
for c in cells: byh[c['imd5']].append(c['stem'])
ident = [v for v in byh.values() if len(v) > 1]
P(f'\n## 5. Pixel-identical images under different stems (grey md5): {len(ident)} groups: {ident}')

def hp(c):
    a = np.asarray(Image.open(c['ip']).convert('L'), dtype=np.float32)
    a = np.asarray(Image.fromarray(a).resize((128, 128), Image.BILINEAR), dtype=np.float32)
    h = a - ndi.gaussian_filter(a, 4)
    h = (h - h.mean()) / (h.std() + 1e-6)
    return h.ravel()
def miou(a, b, cls):
    ma = rmask(a['mp']) == cls; mb = rmask(b['mp']) == cls
    u = (ma | mb).sum()
    return float((ma & mb).sum() / u) if u else float('nan')
cache = {}
def H(c):
    if c['stem'] not in cache: cache[c['stem']] = hp(c)
    return cache[c['stem']]
bypos = collections.defaultdict(list)
for c in cells:
    if c['pos'] is not None: bypos[(c['src'], c['pos'])].append(c)
pairs = []
for k, rr in bypos.items():
    for a, b in itertools.combinations(rr, 2):
        if a['module'] == b['module']: continue   # same image id and position = _rf vs base (none expected)
        pairs.append((float(np.dot(H(a), H(b)) / H(a).size), a, b))
for src in ('BMRK', 'SDLE'):
    rr = [c for c in cells if c['src'] == src]
    for a, b in itertools.combinations(rr, 2):
        pairs.append((float(np.dot(H(a), H(b)) / H(a).size), a, b))
pairs.sort(key=lambda t: -t[0])
with open(f'{OUT}/pairs.tsv', 'w') as f:
    f.write('hp_r\ta\ta_role\tb\tb_role\tinact_iou\tcrack_iou\tcrack_a\tcrack_b\tinact_a\tinact_b\n')
    for r, a, b in pairs:
        if r < 0.5: break
        f.write(f"{r:.3f}\t{a['stem']}\t{a['role']}\t{b['stem']}\t{b['role']}\t{miou(a, b, 11):.3f}\t{miou(a, b, 14):.3f}\t"
                f"{int(a['px'][14])}\t{int(b['px'][14])}\t{int(a['px'][11])}\t{int(b['px'][11])}\n")
P(f'  near-duplicate screen: {len(pairs)} same-source same-position pairs (plus all BMRK / SDLE pairs); hp_r >= 0.9: {sum(p[0] >= 0.9 for p in pairs)}, >= 0.8: {sum(p[0] >= 0.8 for p in pairs)}')
P('  pairs.tsv written (hp_r >= 0.5)')
log.close()
