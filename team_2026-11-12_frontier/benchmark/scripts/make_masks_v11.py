#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Label set v1.1 for the 582 legacy cells (BenchmarkEL dataset_20211104 stems).

v1 (= the project's `masks_escdd`, rebuilt here from public files):
  E-SCDD mask where the cell is in E-SCDD (577 cells), with pixels of classes >= 24 set back to the dataset_20211104
  label at those pixels; the dataset_20211104 mask for the 5 cells missing from E-SCDD.
v1.1 = v1 with three mechanical edits (no hand-drawn change):
  E1  pixels that E-SCDD labels scuff (25) or star (28) -> IGNORE (255)   [v1 gave them their 2021 label]
  E2  BMRK_00031_cell0091 -> its dataset_20220723 mask                     [its 20221008 / E-SCDD mask is the mask of
                                                                            BMRK_00075_cell0255, another image]
  E3  no mask change: noise flags only (cells.tsv), image-only rule sigma > 10
Outputs under OUT_DIR (a new folder; existing mask folders are never written):
  masks/<stem>.png         v1.1, uint8, values 0..23 and 255 (ignore)       -> training (data.mask_ignore_value=255) and scoring
  masks_strict/<stem>.png  v1.1 with the ignore pixels carrying their v1 label (values 0..23 only) -> for loaders that refuse 255
  ignore/<stem>.png        uint8, 255 where v1.1 is ignore, else 0           -> scorer ignore mask (as ext117/ignore)
  CHANGES.tsv              stem, legacy split, edit, class_from (v1), class_to (v1.1), px
  MANIFEST.tsv             stem, split, pixel md5 of v1 (rebuilt), v1.1, v1.1 strict   (md5 of the raw uint8 512x512 bytes)
  SUMMARY.txt              counts per split
Optional --base-masks DIR: a real masks_escdd folder (e.g. on gaint); the rebuilt v1 is then asserted equal to it, pixel
for pixel, for every stem (any difference stops the script before anything is written).
CPU, numpy + PIL. Run: python -I make_masks_v11.py --datasets DATASETS_DIR --out OUT_DIR [--base-masks DIR]
  DATASETS_DIR holds BenchmarkELimages/dataset_20211104, BenchmarkEL_releases/dataset_20220723, escdd_full, splits_benchmark.
"""
import argparse, os, sys, hashlib, collections
import numpy as np
from PIL import Image

IGN = 255
NAMES = ['bckgnd', 'sp multi', 'sp mono', 'sp dogbone', 'ribbons', 'border', 'text', 'padding', 'clamp', 'busbars', 'crack rbn edge', 'inactive',
         'rings', 'material', 'crack', 'gridline', 'splice', 'dead cell', 'corrosion rbn', 'belt mark', 'edge dark', 'frame edge', 'jbox',
         'meas artifact', 'sp mono halfcut', 'scuff', 'corrosion cell', 'brightening', 'star', 'sp multi halfcut']
SWAPPED = 'BMRK_00031_cell0091'      # carries the mask of BMRK_00075_cell0255 in 20221008 / E-SCDD
DONOR = 'BMRK_00075_cell0255'

def rmask(p):
    m = np.array(Image.open(p))
    if m.ndim == 3: m = m[..., 0]
    assert m.shape == (512, 512), (p, m.shape)
    return m.astype(np.uint8)
def pmd5(a): return hashlib.md5(np.ascontiguousarray(a, dtype=np.uint8).tobytes()).hexdigest()
rd = lambda p: [l.strip() for l in open(p) if l.strip()]

ap = argparse.ArgumentParser()
ap.add_argument('--datasets', required=True); ap.add_argument('--out', required=True); ap.add_argument('--base-masks', default=None)
a = ap.parse_args()
DS, OUT = a.datasets, a.out
if os.path.exists(OUT) and os.listdir(OUT): sys.exit(f'refusing to write into non-empty {OUT}')
b21 = f'{DS}/BenchmarkELimages/dataset_20211104'
split = {}
for sp in ('train', 'val', 'test'):
    for s in rd(f'{DS}/splits_benchmark/{sp}.txt'): split[s] = sp
assert len(split) == 582
esc = {}
for sp in ('train', 'val', 'test'):
    for f in os.listdir(f'{DS}/escdd_full/el_masks_{sp}'):
        if f.endswith('.png'): esc[f[:-4]] = f'{DS}/escdd_full/el_masks_{sp}/{f}'
def old(s): return rmask(f"{b21}/masks_coded_{'train_original' if split[s] == 'train' else split[s]}/{s}.png")
def find(rel, s):
    for sp in ('train', 'val', 'test'):
        p = f'{DS}/BenchmarkEL_releases/dataset_{rel}/el_masks_{sp}/{s}.png'
        if os.path.exists(p): return p
    raise FileNotFoundError((rel, s))

v1, v11, ign, raw = {}, {}, {}, {}
changes = []   # (stem, edit, from, to, px)
for s in sorted(split):
    o = old(s)
    assert o.max() < 24, s
    if s in esc:
        e = rmask(esc[s]); raw[s] = e
        assert e.max() < 30, s
        hi = e >= 24
        assert set(np.unique(e[hi]).tolist()) <= {25, 28}, (s, np.unique(e[hi]))   # only scuff / star occur in the 582
        m1 = e.copy(); m1[hi] = o[hi]
        m2 = e.copy(); m2[hi] = IGN
        ig = hi.copy()
    else:
        m1 = o.copy(); m2 = o.copy(); ig = np.zeros_like(o, bool); raw[s] = None
    v1[s] = m1
    if s == SWAPPED:
        m = rmask(find('20220723', s)); assert m.max() < 24
        assert (rmask(esc[s]) == rmask(esc[DONOR])).all(), 'expected the swapped cell to carry the donor mask'
        assert not ig.any()
        m2 = m.copy()
    v11[s], ign[s] = m2, ig
    d = m1 != m2
    if d.any():
        edit = 'E2_wrong_mask_restored' if s == SWAPPED else 'E1_scuff_star_to_ignore'
        cnt = collections.Counter(zip(m1[d].tolist(), m2[d].tolist()))
        if s != SWAPPED:  # split E1 by the E-SCDD class that triggers it
            for k in (25, 28):
                dd = d & (raw[s] == k)
                for (f, t), n in sorted(collections.Counter(zip(m1[dd].tolist(), m2[dd].tolist())).items()):
                    changes.append((s, f'E1_{NAMES[k]}_to_ignore', f, t, n))
        else:
            for (f, t), n in sorted(cnt.items()): changes.append((s, edit, f, t, n))

if a.base_masks:
    bad = [s for s in sorted(split) if not (rmask(f'{a.base_masks}/{s}.png') == v1[s]).all()]
    if bad: sys.exit(f'rebuilt v1 differs from --base-masks in {len(bad)} cells: {bad[:10]}')
    print(f'rebuilt v1 == --base-masks for all {len(split)} cells')

for d in ('masks', 'masks_strict', 'ignore'): os.makedirs(f'{OUT}/{d}')
for s in sorted(split):
    strict = v11[s].copy(); strict[ign[s]] = v1[s][ign[s]]
    assert strict.max() < 24 and set(np.unique(v11[s]).tolist()) <= set(range(24)) | {IGN}
    Image.fromarray(v11[s], 'L').save(f'{OUT}/masks/{s}.png')
    Image.fromarray(strict, 'L').save(f'{OUT}/masks_strict/{s}.png')
    Image.fromarray((ign[s] * 255).astype(np.uint8), 'L').save(f'{OUT}/ignore/{s}.png')
    # re-read check
    assert (rmask(f'{OUT}/masks/{s}.png') == v11[s]).all() and (rmask(f'{OUT}/masks_strict/{s}.png') == strict).all()
with open(f'{OUT}/CHANGES.tsv', 'w') as f:
    f.write('stem\tlegacy_split\tedit\tclass_from_v1\tclass_to_v11\tpx\n')
    for s, e, fr, to, n in changes:
        f.write(f"{s}\t{split[s]}\t{e}\t{fr}:{NAMES[fr]}\t{'255:ignore' if to == IGN else f'{to}:{NAMES[to]}'}\t{n}\n")
with open(f'{OUT}/MANIFEST.tsv', 'w') as f:
    f.write('stem\tlegacy_split\tv1_pixmd5\tv11_pixmd5\tv11_strict_pixmd5\tignore_px\n')
    for s in sorted(split):
        strict = v11[s].copy(); strict[ign[s]] = v1[s][ign[s]]
        f.write(f'{s}\t{split[s]}\t{pmd5(v1[s])}\t{pmd5(v11[s])}\t{pmd5(strict)}\t{int(ign[s].sum())}\n')

L = []
def P(*x):
    t = ' '.join(str(y) for y in x); print(t); L.append(t)
P('Label set v1.1, 582 legacy cells (make_masks_v11.py). v1 = masks_escdd rebuilt from public files.')
P('cells whose mask changed:', len({c[0] for c in changes}), '; change rows:', len(changes))
P('\nper split | cells | changed cells | px -> ignore (scuff / star) | of which v1 crack / material / bckgnd / other | wrong-mask cell px changed')
for sp in ('train', 'val', 'test'):
    st = [s for s in split if split[s] == sp]
    ch = {c[0] for c in changes if split[c[0]] == sp}
    e1 = [c for c in changes if split[c[0]] == sp and c[1].startswith('E1')]
    sc = sum(c[4] for c in e1 if 'scuff' in c[1]); star = sum(c[4] for c in e1 if 'star' in c[1])
    by = collections.Counter()
    for c in e1: by[c[2]] += c[4]
    oth = sum(v for k, v in by.items() if k not in (14, 13, 0))
    e2 = sum(c[4] for c in changes if split[c[0]] == sp and c[1].startswith('E2'))
    P(f'  {sp} | {len(st)} | {len(ch)} | {sc + star} ({sc} / {star}) | {by[14]} / {by[13]} / {by[0]} / {oth} | {e2}')
P('\nper split | crack cells v1 -> v1.1 | crack px v1 -> v1.1 | inactive cells v1 -> v1.1 | inactive px v1 -> v1.1 | cells with ignore px | ignore px')
for sp in ('train', 'val', 'test'):
    st = [s for s in split if split[s] == sp]
    c1 = sum((v1[s] == 14).any() for s in st); c2 = sum((v11[s] == 14).any() for s in st)
    p1 = sum(int((v1[s] == 14).sum()) for s in st); p2 = sum(int((v11[s] == 14).sum()) for s in st)
    i1 = sum((v1[s] == 11).any() for s in st); i2 = sum((v11[s] == 11).any() for s in st)
    q1 = sum(int((v1[s] == 11).sum()) for s in st); q2 = sum(int((v11[s] == 11).sum()) for s in st)
    P(f'  {sp} | {c1} -> {c2} | {p1} -> {p2} | {i1} -> {i2} | {q1} -> {q2} | {sum(ign[s].any() for s in st)} | {sum(int(ign[s].sum()) for s in st)}')
P('\ncells that lose all crack in v1.1:', [(s, split[s], int((v1[s] == 14).sum())) for s in sorted(split) if (v1[s] == 14).any() and not (v11[s] == 14).any()])
P('E1 cells (stem, split, ignore px, of which v1 crack):')
for s in sorted(split):
    if ign[s].any(): P(f'  {s}\t{split[s]}\t{int(ign[s].sum())}\t{int((v1[s][ign[s]] == 14).sum())}')
m1, m2 = v1[SWAPPED], v11[SWAPPED]
P(f'E2 {SWAPPED} ({split[SWAPPED]}): crack px {int((m1 == 14).sum())} -> {int((m2 == 14).sum())}; px changed {int((m1 != m2).sum())}; '
  f'v1.1 mask == dataset_20211104 mask: {bool((m2 == old(SWAPPED)).all())}; donor {DONOR} ({split[DONOR]}) unchanged')
P('strict variant differs from v1 in cells:', [s for s in sorted(split) if not ((lambda x: x)(np.where(ign[s], v1[s], v11[s])) == v1[s]).all()])
open(f'{OUT}/SUMMARY.txt', 'w').write('\n'.join(L) + '\n')
