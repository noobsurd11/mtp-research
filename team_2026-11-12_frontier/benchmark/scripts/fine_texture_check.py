#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. Second, independent evidence for "same physical cell": fine-scale texture correlation.
For every same-source same-position pair with screen hp_r >= 0.80 (pairs.tsv): high-pass both grey images at full
resolution (image - gaussian sigma 2), normalise, FFT cross-correlation, max over shifts of at most 8 px.
Grain texture and small marks are cell-specific; shared shading and layout are removed by the fine high-pass.
Images only (no masks, no predictions). Run: python -I fine_texture_check.py DATASETS_DIR OUT_DIR"""
import sys, collections
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
DS, OUT = sys.argv[1], sys.argv[2]
hdr, *rows = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/cells.tsv')]
C = {r[0]: dict(zip(hdr, r)) for r in rows}
hg, *rg = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/groups_all.tsv')]
G = {r[0]: dict(zip(hg, r)) for r in rg}
def ipath(stem):
    rel = dict(x.split(':') for x in C[stem]['releases'].split('|')); mv = C[stem]['maskver']
    if mv == 'escdd': return f"{DS}/escdd_full/el_images_{rel['escdd']}/{stem}.png"
    return f"{DS}/BenchmarkEL_releases/dataset_{mv}/el_images_{rel[mv]}/{stem}.png"
cache = {}
def desc(stem):
    if stem not in cache:
        a = np.asarray(Image.open(ipath(stem)).convert('L'), dtype=np.float32)
        h = (a - ndi.gaussian_filter(a, 2.0))[16:-16, 16:-16]
        h = h - h.mean(); h /= (np.sqrt((h * h).sum()) + 1e-9)
        cache[stem] = np.fft.rfft2(h)
    return cache[stem]
def fine(a, b, R=8):
    c = np.fft.irfft2(desc(a) * np.conj(desc(b)), s=(480, 480))
    c = np.roll(np.roll(c, R, 0), R, 1)[:2 * R + 1, :2 * R + 1]
    i = np.unravel_index(np.argmax(c), c.shape)
    return float(c[i]), i[0] - R, i[1] - R
pr = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/pairs.tsv')][1:]
res = []
for r in pr:
    a, b = r[1], r[3]
    if a.startswith(('BMRK', 'SDLE')) or float(r[0]) < 0.80: continue
    f, dy, dx = fine(a, b)
    res.append((f, a, r[2], b, r[4], float(r[0]), r[5], r[6], G[a]['group'] == G[b]['group'], dy, dx, C[a]['celltype']))
res.sort(key=lambda t: -t[0])
with open(f'{OUT}/fine_ncc_pairs.tsv', 'w') as fo:
    fo.write('fine_ncc\ta\ta_role\tb\tb_role\tscreen_hp_r\tinact_iou\tcrack_iou\tsame_group\tdy\tdx\tcelltype_a\n')
    for t in res: fo.write('\t'.join(f'{x:.3f}' if isinstance(x, float) else str(x) for x in t) + '\n')
same = np.array([t[0] for t in res if t[8]]); diff = np.array([t[0] for t in res if not t[8]])
print(f'pairs {len(res)}; grouped {len(same)}: fine ncc min {same.min():.3f} median {np.median(same):.3f} max {same.max():.3f}')
print(f'ungrouped {len(diff)}: fine ncc median {np.median(diff):.3f}, 95th pct {np.percentile(diff, 95):.3f}, 99th {np.percentile(diff, 99):.3f}, max {diff.max():.3f}')
print('grouped pairs with fine ncc < 0.15 (weak second evidence):')
for t in res:
    if t[8] and t[0] < 0.15: print('  ', f'{t[0]:.3f}', t[1], t[2], t[3], t[4], 'screen', t[5], 'iou inact/crack', t[6], t[7], t[11])
print('ungrouped pairs with fine ncc >= 0.15 (possible same cell):')
for t in res:
    if (not t[8]) and t[0] >= 0.15: print('  ', f'{t[0]:.3f}', t[1], t[2], t[3], t[4], 'screen', t[5], 'iou inact/crack', t[6], t[7], t[11], 'shift', t[9], t[10])
want = [('CFVS_00021_r3_c1', 'CFVS_00063_r3_c1'), ('ARTS_00030_r8_c6', 'ARTS_00164_r8_c6'), ('ARTS_00030_r8_c6', 'ARTS_00146_r8_c6'), ('CSIR_00059_r6_c1', 'CSIR_00201_r6_c1'),
        ('CSIR_00222_r6_c2', 'CSIR_00231_r6_c2'), ('CSIR_00059_r5_c2', 'CSIR_00176_r5_c2'), ('CSIR_00221_r6_c2', 'CSIR_00231_r6_c2'), ('CSIR_00221_r6_c2', 'CSIR_00222_r6_c2'),
        ('ARTS_00020_r9_c6', 'ARTS_00081_r9_c6'), ('ARTS_00020_r5_c1', 'ARTS_00081_r5_c1'), ('CFVS_00015_r7_c4', 'CFVS_00016_r7_c4'), ('CFVS_00007_r3_c1', 'CFVS_00021_r3_c1'),
        ('CFVS_00007_r3_c1', 'CFVS_00063_r3_c1'), ('ARTS_00040_r1_c6', 'ARTS_00061_r1_c6')]
print('named pairs:')
for a, b in want:
    f, dy, dx = fine(a, b); print(f'   {a} ({C[a]["role"]}) vs {b} ({C[b]["role"]}): fine ncc {f:.3f} at shift {dy},{dx}; type {C[a]["celltype"]}')
