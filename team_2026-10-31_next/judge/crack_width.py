#!/usr/bin/env python3
"""judge recompute for idea 8 §1 (crack vs stride) and crack width by set, from LOCAL 20221008 release masks
(crack = 14; for our cells, crack/inactive in masks_escdd come from 20221008, handbook 11 conventions).
Independent of found's gaint copy. Width estimators: (a) 2*EDT at skeleton px (found's), (b) area/skeleton-length per cell.
Stride stats: share of crack px whose s x s block is < 25% crack; ceil IoU = |gt| / |maxpool-up(gt)|. Descriptive."""
import os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
D = os.path.expanduser('~/mtp/datasets'); R = '/home/yugma/mtp/research'
REL = f'{D}/BenchmarkEL_releases/dataset_20221008'
loc = {}
for sp in ('train', 'val', 'test'):
    for f in os.listdir(f'{REL}/el_masks_{sp}'): loc[f[:-4]] = f'{REL}/el_masks_{sp}/{f}'
def rd(p): return [l.strip() for l in open(p) if l.strip()]
ctx = {l.split('\t')[0]: l.strip().split('\t')[1:] for l in open(f'{R}/team_2026-10-29_features/scripts/e1_context.tsv')}
sets = {'train': rd(f'{D}/splits_benchmark/train.txt'), 'val': rd(f'{D}/splits_benchmark/val.txt'),
        'E1': list(ctx), 'E1_halfcut': [s for s in ctx if ctx[s][2] == 'halfcut=1'], 'E1_full': [s for s in ctx if ctx[s][2] == 'halfcut=0']}
for name, stems in sets.items():
    W, AL, n, miss = [], [0, 0], 0, 0
    dil = {s: 0 for s in (2, 4, 16)}; up = {s: 0 for s in (2, 4, 16)}
    for st in stems:
        if st not in loc: miss += 1; continue
        g = np.array(Image.open(loc[st])) == 14
        if not g.any(): continue
        n += g.sum()
        sk = skeletonize(g); W += (2 * ndi.distance_transform_edt(g)[sk]).tolist()
        AL[0] += g.sum(); AL[1] += sk.sum()
        for s in dil:
            b = g.reshape(512 // s, s, 512 // s, s).mean((1, 3))
            dil[s] += (g & (np.kron(b, np.ones((s, s))) < 0.25)).sum()
            up[s] += (b > 0).sum() * s * s
    W = np.array(W)
    print(f'{name:11s} cells {len(stems)} (missing in release {miss}) crack px {n}: width 2*EDT median {np.median(W):.2f} p90 {np.percentile(W,90):.2f} | area/skeleton {AL[0]/AL[1]:.2f} | '
          + ' '.join(f's{s}: dil<25% {dil[s]/n:.3f} ceilIoU {n/up[s]:.3f}' for s in dil))
