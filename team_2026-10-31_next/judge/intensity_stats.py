#!/usr/bin/env python3
"""judge helper: per-cell grey-level stats (PIL convert('L'), as the loader) for train/val/test (20211104 images)
and E1 (20221008 release images). Pixels with mask class 7 (padding) excluded; E1 uses release masks.
Output: judge/out/intensity_stats.tsv + summary. CPU, read-only. Descriptive only (E1 never for selection)."""
import os, numpy as np, csv, sys
from PIL import Image
D = os.path.expanduser('~/mtp/datasets'); R = '/home/yugma/mtp/research'
OUT = f'{R}/team_2026-10-31_next/judge/out'; os.makedirs(OUT, exist_ok=True)
B = f'{D}/BenchmarkELimages/dataset_20211104'; REL = f'{D}/BenchmarkEL_releases/dataset_20221008'
def rd(p): return [l.strip() for l in open(p) if l.strip()]
items = []
for sp, img, msk in (('train', 'images_train_original', 'masks_coded_train_original'), ('val', 'images_val', 'masks_coded_val'), ('test', 'images_test', 'masks_coded_test')):
    for s in rd(f'{D}/splits_benchmark/{sp}.txt'):
        items.append((sp, s, f'{B}/{img}/{s}.png', f'{B}/{msk}/{s}.png'))
ctx = {l.split('\t')[0]: l.strip().split('\t')[1:] for l in open(f'{R}/team_2026-10-29_features/scripts/e1_context.tsv')}
loc = {}
for sp in ('train', 'val', 'test'):
    for f in os.listdir(f'{REL}/el_images_{sp}'): loc[f[:-4]] = sp
for s in ctx:
    items.append(('e1', s, f'{REL}/el_images_{loc[s]}/{s}.png', f'{REL}/el_masks_{loc[s]}/{s}.png'))
rows = []
for sp, s, ip, mp in items:
    a = np.asarray(Image.open(ip).convert('L'), dtype=np.float32)
    m = np.asarray(Image.open(mp))
    v = a[m != 7] if (m != 7).sum() > 1000 else a.ravel()
    p = np.percentile(v, [1, 5, 50, 95, 99])
    # local contrast: robust sd of a high-pass (img - 7x7 box mean) on non-padding px
    from scipy.ndimage import uniform_filter
    hp = (a - uniform_filter(a, 7))[m != 7] if (m != 7).sum() > 1000 else (a - uniform_filter(a, 7)).ravel()
    mad = 1.4826 * np.median(np.abs(hp - np.median(hp)))
    rows.append(dict(set=sp, stem=s, src=s[:4], ctx=('|'.join(ctx[s]) if s in ctx else ''), mean=v.mean(), sd=v.std(),
                     p1=p[0], p5=p[1], p50=p[2], p95=p[3], p99=p[4], hp_mad=mad, frac_pad=float((m == 7).mean())))
with open(f'{OUT}/intensity_stats.tsv', 'w') as f:
    w = csv.DictWriter(f, list(rows[0].keys()), delimiter='\t'); w.writeheader()
    for r in rows: w.writerow({k: (f'{v:.3f}' if isinstance(v, float) else v) for k, v in r.items()})
import collections
def summ(sel, name):
    if not sel: return
    a = {k: np.array([r[k] for r in sel]) for k in ('mean', 'sd', 'p50', 'p99', 'hp_mad')}
    print(f'{name:28s} n={len(sel):4d} ' + ' '.join(f'{k}={np.median(v):6.1f}[{np.percentile(v,10):5.1f},{np.percentile(v,90):5.1f}]' for k, v in a.items()))
for sp in ('train', 'val', 'test', 'e1'):
    summ([r for r in rows if r['set'] == sp], sp)
for sp in ('train', 'test'):
    for src in ('ARTS', 'BMRK', 'CFVS', 'CSIR', 'SDLE'):
        summ([r for r in rows if r['set'] == sp and r['src'] == src], f'{sp} {src}')
summ([r for r in rows if r['set'] == 'e1' and 'halfcut=1' in r['ctx'] and 'scuff=1' in r['ctx']], 'e1 halfcut+scuff')
summ([r for r in rows if r['set'] == 'e1' and 'halfcut=1' in r['ctx'] and 'scuff=0' in r['ctx']], 'e1 halfcut noscuff')
summ([r for r in rows if r['set'] == 'e1' and 'halfcut=0' in r['ctx']], 'e1 full')
summ([r for r in rows if r['set'] == 'e1' and r['src'] == 'CSIR'], 'e1 CSIR')
