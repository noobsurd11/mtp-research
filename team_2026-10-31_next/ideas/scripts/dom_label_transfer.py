"""Idea 5 label-transfer check: crack CNR (median ring - median crack, / 1.4826 MAD ring; ring = dilate6 - dilate2,
non-defect px) in each synthetic image vs its source; a misaligned mask would lower CNR towards 0. Also: crack
fragment count ratio (8-connectivity) out/src restricted to cells with crack in the output, inactive area ratio,
and mask value range / mode (loader needs single-channel 0..23).
Usage: python -I dom_label_transfer.py SYNTH_DIR INDEX.tsv"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
D = sys.argv[1]
idx = {r['stem']: r for r in csv.DictReader(open(sys.argv[2]), delimiter='\t')}
def cnr(I, M):
    c = M == 14
    if c.sum() < 20: return np.nan
    neg = np.isin(M, [0, 1, 2, 3, 4, 5, 9]); ring = ndi.binary_dilation(c, iterations=6) & ~ndi.binary_dilation(c, iterations=2) & neg
    if ring.sum() < 20: return np.nan
    r = I[ring]; mr = np.median(r); return (mr - np.median(I[c])) / (1.4826 * np.median(np.abs(r - mr)) + 1e-6)
res = []; bad = 0
for r in csv.DictReader(open(D + '/synth_log.tsv'), delimiter='\t'):
    O = np.asarray(Image.open(f'{D}/images/{r["out"]}.png'), dtype=float); mi = Image.open(f'{D}/masks/{r["out"]}.png')
    OM = np.asarray(mi)
    if mi.mode != 'L' or OM.max() > 23 or O.shape != (512, 512): bad += 1
    s = idx[r['src']]; I = np.asarray(Image.open(s['img']).convert('L'), dtype=float); M = np.asarray(Image.open(s['mask']))
    a, b = cnr(I, M), cnr(O, OM)
    fs = ndi.label(M == 14, structure=np.ones((3, 3)))[1]; fo = ndi.label(OM == 14, structure=np.ones((3, 3)))[1]
    res.append((a, b, fs, fo, int(r['crack_out']), int(r['inact_src']), int(r['inact_out'])))
a = np.array(res, dtype=float); ok = np.isfinite(a[:, 0]) & np.isfinite(a[:, 1])
print('images', len(a), 'loader-format violations', bad)
print('crack CNR src median %.2f, synth median %.2f, paired median ratio %.2f (n %d)' % (np.median(a[ok, 0]), np.median(a[ok, 1]), np.median(a[ok, 1] / a[ok, 0]), ok.sum()))
print('cells with crack: src %d, synth %d; synth crack px median %d' % ((a[:, 2] > 0).sum(), (a[:, 4] > 0).sum(), np.median(a[a[:, 4] > 0, 4])))
w = a[:, 4] > 0
print('fragments out/src median %.2f' % np.median(a[w, 3] / np.maximum(a[w, 2], 1)))
wi = a[:, 6] > 0
print('inactive cells src %d, synth %d; synth inactive px median %d' % ((a[:, 5] > 0).sum(), wi.sum(), np.median(a[wi, 6]) if wi.any() else 0))
