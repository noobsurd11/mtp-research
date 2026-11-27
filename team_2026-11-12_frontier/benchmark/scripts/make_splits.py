#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Split definitions for the benchmark harness.
Writes benchmark/splits/{cv5v2.json, legacy.json, forbidden_v1.txt, cv5v2_groups.tsv, cv5v2_vs_b6.tsv,
pool532_manifest.tsv, cv5v2_check.txt, SPLITS.md5}.
cv5v2 = the frozen B6 folds (b6_folds.tsv e2cafce1) with 4 cells moved to fold 1 (lead decision D2, 12 Nov).
CPU, list files + local images / masks only. Run after corpus_build.py and groups_folds.py:
  python -I make_splits.py DATASETS_DIR RESEARCH_DIR OUT_DIR SPLITS_DIR
"""
import sys, os, json, hashlib, collections
import numpy as np
from PIL import Image

DS, RS, OUT, SP = sys.argv[1:5]
os.makedirs(SP, exist_ok=True)
MOVED = {'ARTS_00081_r5_c1': 1, 'ARTS_00081_r9_c6': 1, 'CFVS_00033_r1_c4': 1, 'CFVS_00033_r5_c3': 1}
B6_FOLDS_MD5 = 'e2cafce1509bb0f2b95ce6d5db397caf'
B6_FORB_MD5 = '9bb4d919fc16b5b394ce6d71f53903a6'
SPLIT_MD5 = {'train': '842f27c418106a2095fa642daafec3fc', 'val': '9dcccf00662dfca750f0b46628f8d5bb', 'test': 'a31fad14fa27ee28e2a2319b8976aba3'}
ORDER_RULE = ("every stem list is in pool order: the legacy train.txt order, then the legacy val.txt order (the B6 rule, "
              "b6_make_roots.py); a root's splits/train.txt = 'train', splits/val.txt = splits/test.txt = 'heldout'")
LIST_MD5_RULE = "md5 of the UTF-8 bytes of '\\n'.join(stems) + '\\n' (= md5sum of the split file a root writes, one stem per line)"

def fmd5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
def lmd5(stems): return hashlib.md5(('\n'.join(stems) + '\n').encode()).hexdigest()
rd = lambda p: [l.strip() for l in open(p) if l.strip()]

spl = f'{DS}/splits_benchmark'
train, val, test = (rd(f'{spl}/{s}.txt') for s in ('train', 'val', 'test'))
for s in ('train', 'val', 'test'): assert fmd5(f'{spl}/{s}.txt') == SPLIT_MD5[s], s
pool = train + val
assert len(pool) == 532 and len(set(pool)) == 532 and not (set(pool) & set(test))
b6p = f'{RS}/team_2026-10-31_next/results/b6/b6_folds.tsv'
assert fmd5(b6p) == B6_FOLDS_MD5
b6 = {}
for l in list(open(b6p))[1:]:
    a = l.rstrip('\n').split('\t'); b6[a[0]] = int(a[3])
assert set(b6) == set(pool)
forb_src = f'{RS}/team_2026-10-31_next/results/b6/b6_forbidden.txt'
assert fmd5(forb_src) == B6_FORB_MD5
forb = rd(forb_src)
assert set(test) <= set(forb) and len(forb) == 167 and not (set(forb) & set(pool))
with open(f'{SP}/forbidden_v1.txt', 'wb') as f: f.write(open(forb_src, 'rb').read())
assert fmd5(f'{SP}/forbidden_v1.txt') == B6_FORB_MD5

# groups (whole-corpus rule incl. test-cell links), renamed to the smallest image id of the group
hdr, *rows = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/groups_all.tsv')]
G = {r[0]: dict(zip(hdr, r)) for r in rows}
members = collections.defaultdict(set)
for g in G.values(): members[g['group']].add(g['module'])
gname = {k: min(v) for k, v in members.items()}
grp = {s: gname[g['group']] for s, g in G.items()}

fold = dict(b6)
for s, k in MOVED.items():
    assert s in fold, s
    fold[s] = k

def straddle(assign):
    by = collections.defaultdict(set)
    for s, k in assign.items(): by[grp[s]].add(k)
    return {g: sorted(v) for g, v in by.items() if len(v) > 1}
chk = open(f'{SP}/cv5v2_check.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); chk.write(s + '\n')
P('cv5v2 check (make_splits.py). Groups: physical-module groups over all 816 labelled cells, test-cell links included.')
P('pool 532 = legacy train 478 + val 54; groups in the pool:', len({grp[s] for s in pool}))
P('groups cut across folds, frozen B6 folds:', straddle(b6))
P('groups cut across folds, cv5v2:', straddle(fold), '-> count', len(straddle(fold)))
assert not straddle(fold)
P('forbidden stems (test 50 + ext117 117) in the pool:', len(set(forb) & set(pool)))
# informational: same-position pairs with screen correlation >= 0.90 that are NOT grouped and sit in different folds
pr = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/pairs.tsv')][1:]
info = collections.Counter(); ex = []
for r in pr:
    a, b = r[1], r[3]
    if a in fold and b in fold and float(r[0]) >= 0.90 and grp[a] != grp[b] and fold[a] != fold[b]:
        info[a[:4]] += 1
        if a[:4] not in ('BMRK', 'SDLE', 'ARTS'): ex.append((r[0], a, b, r[5], r[6]))
P('ungrouped same-position pairs with high-pass correlation >= 0.90 in different cv5v2 folds, by source:', dict(info))
P('  (ARTS: clean edge cells that look alike, left ungrouped as in protocol_B6 s7; BMRK / SDLE: no module ids, all pairs screened, smooth images inflate the score)')
P('  non-ARTS, non-BMRK/SDLE cases:', ex)

leg = np.load(f'{OUT}/legacy_classpx.npy'); ls = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/legacy_stems.txt')]
lpx = {s: leg[i] for i, (s, _) in enumerate(ls)}
def table(assign, title):
    P(title)
    P('  fold | cells (train / val) | groups | crack cells | crack-free | crack px | inactive cells | inactive px | ARTS / BMRK / CFVS / CSIR / SDLE')
    for k in range(5):
        v = [s for s in pool if assign[s] == k]
        src = collections.Counter(s[:4] for s in v)
        P(f"  {k} | {len(v)} ({sum(s in set(train) for s in v)} / {sum(s in set(val) for s in v)}) | {len({grp[s] for s in v})} | {sum(lpx[s][14] > 0 for s in v)} | {sum(lpx[s][14] == 0 for s in v)} | "
          f"{sum(int(lpx[s][14]) for s in v)} | {sum(lpx[s][11] > 0 for s in v)} | {sum(int(lpx[s][11]) for s in v)} | {src['ARTS']} / {src['BMRK']} / {src['CFVS']} / {src['CSIR']} / {src['SDLE']}")
table(b6, 'frozen B6 folds (masks_escdd rebuilt locally):')
table(fold, 'cv5v2 folds (masks_escdd rebuilt locally):')
# classes with zero training px in a fold
names = ['bckgnd', 'sp multi', 'sp mono', 'sp dogbone', 'ribbons', 'border', 'text', 'padding', 'clamp', 'busbars', 'crack rbn edge', 'inactive', 'rings', 'material',
         'crack', 'gridline', 'splice', 'dead cell', 'corrosion rbn', 'belt mark', 'edge dark', 'frame edge', 'jbox', 'meas artifact']
for k in range(5):
    tr = np.sum([lpx[s] for s in pool if fold[s] != k], axis=0); ho = np.sum([lpx[s] for s in pool if fold[s] == k], axis=0)
    z = [names[c] for c in range(24) if tr[c] == 0 and ho[c] > 0]
    if z: P(f'  cv5v2 fold {k}: classes with held-out px but 0 training px: {z}')

with open(f'{SP}/cv5v2_vs_b6.tsv', 'w') as f:
    f.write('stem\tlegacy_split\tgroup\tb6_fold\tcv5v2_fold\n')
    for s in pool:
        if b6[s] != fold[s]: f.write(f"{s}\t{'train' if s in set(train) else 'val'}\t{grp[s]}\t{b6[s]}\t{fold[s]}\n")
with open(f'{SP}/cv5v2_groups.tsv', 'w') as f:
    f.write('stem\tlegacy_split\tgroup\tfold\n')
    for s in pool: f.write(f"{s}\t{'train' if s in set(train) else 'val'}\t{grp[s]}\t{fold[s]}\n")

# pool manifest: image file md5 (BenchmarkEL repo clone) and mask pixel md5 (masks_escdd rebuilt)
b21 = f'{DS}/BenchmarkELimages/dataset_20211104'
def imgpath(s): return f"{b21}/images_{'train_original' if s in set(train) else 'val' if s in set(val) else 'test'}/{s}.png"
with open(f'{SP}/pool532_manifest.tsv', 'w') as f:
    f.write('stem\tlegacy_split\timage_file_md5\timage_grey_pixel_md5\n')
    for s in pool:
        g = np.asarray(Image.open(imgpath(s)).convert('L'))
        f.write(f"{s}\t{'train' if s in set(train) else 'val'}\t{fmd5(imgpath(s))}\t{hashlib.md5(g.tobytes()).hexdigest()}\n")

common = {'format': 'el_bench_split/1',
          'format_notes': {'folds': "list of {id, train, heldout, n_train, n_heldout, train_md5, heldout_md5}", 'order_rule': ORDER_RULE, 'list_md5_rule': LIST_MD5_RULE,
                           'roots': "bench_make_roots writes <ROOTS>/<name>_<id>/splits/train.txt = train, val.txt = test.txt = heldout; labeled symlink as for B6",
                           'forbidden': "stems that must never appear in any train / heldout list of a development root, and that the scorer refuses outside a registered opening"},
          'created': '2026-11-12', 'author': 'benchdesign',
          'forbidden': {'file': 'forbidden_v1.txt', 'n': len(forb), 'md5': B6_FORB_MD5, 'content': 'legacy test 50 + ext117 117 (E1 106 + 11 pool cells), sorted; byte copy of b6_forbidden.txt'},
          'source_lists': {'train_txt_md5': SPLIT_MD5['train'], 'val_txt_md5': SPLIT_MD5['val'], 'test_txt_md5': SPLIT_MD5['test']}}
folds = []
for k in range(5):
    ho = [s for s in pool if fold[s] == k]; tr = [s for s in pool if fold[s] != k]
    assert not (set(ho) & set(tr)) and len(ho) + len(tr) == 532 and not (set(forb) & set(ho + tr))
    folds.append({'id': f'f{k}', 'n_train': len(tr), 'n_heldout': len(ho), 'train_md5': lmd5(tr), 'heldout_md5': lmd5(ho), 'train': tr, 'heldout': ho})
assert sorted(sum([f['heldout'] for f in folds], [])) == sorted(pool)
cv = dict(common)
cv.update({'name': 'cv5v2', 'version': 2,
           'description': 'module-grouped 5-fold CV over the 532 legacy train + val cells; = frozen B6 folds (b6_folds.tsv) with 4 cells moved to fold 1 so that no physical module is cut across folds once test-cell links are counted',
           'parent': {'name': 'b6_folds (cv5v1)', 'file_md5': B6_FOLDS_MD5, 'moved': [{'stem': s, 'from': b6[s], 'to': k} for s, k in MOVED.items()]},
           'pool': {'n': 532, 'definition': 'legacy train.txt (478) then val.txt (54)', 'stems_md5': lmd5(pool), 'manifest_file': 'pool532_manifest.tsv',
                    'manifest_md5': fmd5(f'{SP}/pool532_manifest.tsv'), 'gaint_reference': 'B6 DATA_MANIFEST.md5 2630f630 covers the same 532 stems (file-level md5s on gaint; not re-checked here)'},
           'groups': {'file': 'cv5v2_groups.tsv', 'md5': fmd5(f'{SP}/cv5v2_groups.tsv'), 'n_groups': len({grp[s] for s in pool}),
                      'rule': 'same image id; or same source and position with crack or inactive mask IoU >= 0.2; or CFVS same position with 128-px high-pass correlation >= 0.90; plus the twins of team_2026-10-21/data/decision.md D6, test-cell links included'},
           'sealed_sets': 'none inside this split; legacy test and E1 are in forbidden_v1.txt',
           'folds': folds})
json.dump(cv, open(f'{SP}/cv5v2.json', 'w'), indent=1)
lg = dict(common)
lg.update({'name': 'legacy', 'version': 1,
           'description': 'BenchmarkEL dataset_20211104 official split, 478 / 54 / 50; one fold: train = train.txt, heldout = val.txt. Development roots set test.txt = val.txt (the s2c_root pattern). test50 is sealed: scored only by the frozen scorer at a registered opening (benchmark/test_openings.md)',
           'pool': {'n': 532, 'definition': 'legacy train.txt (478) then val.txt (54)', 'stems_md5': lmd5(pool), 'manifest_file': 'pool532_manifest.tsv', 'manifest_md5': fmd5(f'{SP}/pool532_manifest.tsv')},
           'folds': [{'id': 'legacy', 'n_train': len(train), 'n_heldout': len(val), 'train_md5': lmd5(train), 'heldout_md5': lmd5(val), 'train': train, 'heldout': val}],
           'sealed_sets': {'test50': {'n': len(test), 'md5': lmd5(test), 'stems': test,
                                      'subsets': {'noisy': ['CSIR_00070_r8_c4'],
                                                  'twins_d6': ['CFVS_00006_r5_c5', 'CFVS_00033_r8_c4', 'CFVS_00035_r8_c4', 'CFVS_00042_r8_c4', 'CFVS_00018_r4_c4', 'CFVS_00027_r4_c4', 'ARTS_00020_r5_c1']}}},
           'unlabelled_pool_exclusions_d7': ['CFVS_00003_r5_c5', 'CFVS_00037_r8_c4', 'CFVS_00032_r8_c4', 'CFVS_00020_r4_c4', 'CFVS_00022_r4_c4', 'CFVS_00031_r4_c4', 'ARTS_00081_r5_c1']})
assert lmd5(train) == SPLIT_MD5['train'] and lmd5(val) == SPLIT_MD5['val'] and lmd5(test) == SPLIT_MD5['test'], 'list md5 rule != md5sum of the split files'
json.dump(lg, open(f'{SP}/legacy.json', 'w'), indent=1)
P('list md5 rule reproduces md5sum of the legacy train / val / test files: True')
P('cv5v2 fold sizes (heldout):', [f['n_heldout'] for f in folds], 'train:', [f['n_train'] for f in folds])
for f in folds: P(f"  {f['id']}: train_md5 {f['train_md5']} heldout_md5 {f['heldout_md5']}")
chk.close()
with open(f'{SP}/SPLITS.md5', 'w') as f:
    for n in ('cv5v2.json', 'legacy.json', 'forbidden_v1.txt', 'cv5v2_groups.tsv', 'cv5v2_vs_b6.tsv', 'pool532_manifest.tsv', 'cv5v2_check.txt'):
        f.write(f"{fmd5(f'{SP}/{n}')}  {n}\n")
print(open(f'{SP}/SPLITS.md5').read())
