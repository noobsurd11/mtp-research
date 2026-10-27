"""ideas, 27 Oct. CPU only, reads existing files. Why does E1 (unseen modules) lose crack?
Per cell: image stats (grayscale as loader, central 80%), crack darkness vs local ring, crack width
(px / skeleton px), and FINAL (bias +0.75) crack recall and p<0.001 share from final_cells.json.
Masks: BenchmarkEL release 20221008 (crack/inactive identical to E-SCDD, handbook 17).
Usage: e1_shift.py <out.csv>"""
import sys, os, glob, json, csv
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

R = os.path.expanduser('~/mtp/datasets/BenchmarkEL_releases/dataset_20221008')
FC = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'
SPL = os.path.expanduser('~/mtp/datasets/splits_benchmark')
CRACK, INACT, PAD = 14, 11, 7
img = {os.path.basename(p)[:-4]: p for p in glob.glob(R + '/el_images_*/*.png')}
msk = {os.path.basename(p)[:-4]: p for p in glob.glob(R + '/el_masks_*/*.png')}
d = json.load(open(FC))
sets = {'test': list(d['test']['final_b0.75']), 'ext': list(d['ext']['final_b0.75'])}
tr = [l.strip() for l in open(SPL + '/train.txt') if l.strip()]
tr = [os.path.basename(t).replace('.png', '') for t in tr]
sets['train'] = [t for t in tr if t in img]
out = csv.writer(open(sys.argv[1], 'w'))
out.writerow(['set', 'stem', 'src', 'mean', 'sd', 'rsd', 'lap', 'noise', 'crack_px', 'crack_dark', 'crack_rel_dark',
              'crack_width', 'rec', 'p001', 'p95', 'inact_px'])
for s, stems in sets.items():
    for st in stems:
        a = np.asarray(Image.open(img[st]).convert('L'), dtype=np.float32)
        m = np.asarray(Image.open(msk[st]))
        c = a[51:-51, 51:-51]
        q1, q3 = np.percentile(c, [25, 75])
        lap = np.abs(4 * c[1:-1, 1:-1] - c[:-2, 1:-1] - c[2:, 1:-1] - c[1:-1, :-2] - c[1:-1, 2:])
        noise = np.median(lap) / 0.6745 / np.sqrt(20)  # rough MAD noise of the Laplacian
        cr = m == CRACK
        n = int(cr.sum())
        dark = rel = wid = np.nan
        if n >= 20:
            ring = ndi.binary_dilation(cr, iterations=8) & ~ndi.binary_dilation(cr, iterations=3) & (m != PAD) & (m != INACT)
            if ring.sum() > 50:
                bg = np.median(a[ring]); dark = bg - np.median(a[cr]); rel = dark / max(bg, 1)
            sk = skeletonize(cr).sum(); wid = n / max(sk, 1)
        rec = p001 = p95 = np.nan
        if s in ('test', 'ext'):
            v = d[s]['final_b0.75'][st]; cf = np.array(v['conf']).reshape(24, 24)
            if cf[CRACK].sum() >= 20:
                rec = cf[CRACK, CRACK] / cf[CRACK].sum()
                pb = np.array(v['crack_pband_gt'], dtype=float)
                if pb.sum() > 0: p001 = pb[0] / pb.sum(); p95 = pb[-1] / pb.sum()
        out.writerow([s, st, st.split('_')[0], round(float(c.mean()), 2), round(float(c.std()), 2), round(float((q3 - q1) / 1.349), 2),
                      round(float(lap.mean()), 2), round(float(noise), 2), n, round(float(dark), 2), round(float(rel), 4),
                      round(float(wid), 2), round(float(rec), 4), round(float(p001), 4), round(float(p95), 4), int((m == INACT).sum())])
