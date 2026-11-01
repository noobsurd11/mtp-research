"""Idea 11: per-cell appearance stats, split into what the house labelsafe jitter (I' = a*I + b*255, a in [0.8,1.2],
b in [-0.2,0.2], p 0.4) can move (mean, sd) and what it cannot (ratios invariant to a linear map):
  shape = (p50 - p5) / (p95 - p5)    histogram shape / gamma proxy
  sharp = mean|Laplacian| / sd       sharpness relative to contrast (blur proxy)
  noise = 1.4826 MAD(I - median5(I)) / sd   fine-noise relative to contrast
Content = non-white rows/cols (letterbox rule of ideas F6) and, with a mask, not padding class 7.
Usage: python -I dom_appearance.py LIST.tsv OUT.tsv   (LIST: group<TAB>img<TAB>mask-or-empty)"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
w = csv.writer(open(sys.argv[2], 'w'), delimiter='\t')
w.writerow(['group', 'img', 'mean', 'sd', 'p5', 'p50', 'p95', 'shape', 'sharp', 'noise', 'content_frac'])
for l in open(sys.argv[1]):
    if not l.strip(): continue
    g, ip, mp = (l.rstrip('\n').split('\t') + [''])[:3]
    I = np.asarray(Image.open(ip).convert('L'), dtype=np.float64)
    wr = np.mean(I >= 250, axis=1) > 0.98; wc = np.mean(I >= 250, axis=0) > 0.98
    v = (~wr[:, None]) & (~wc[None, :])
    if mp: v &= np.asarray(Image.open(mp)) != 7
    if v.sum() < 5000: continue
    x = I[v]; p5, p50, p95 = np.percentile(x, [5, 50, 95]); sd = x.std()
    lap = np.abs(ndi.laplace(I))[ndi.binary_erosion(v, iterations=2)].mean()
    r = (I - ndi.median_filter(I, 5))[ndi.binary_erosion(v, iterations=3)]; nz = 1.4826 * np.median(np.abs(r - np.median(r)))
    w.writerow([g, ip, round(x.mean(), 2), round(sd, 2), p5, p50, p95, round((p50 - p5) / max(p95 - p5, 1), 4),
                round(lap / max(sd, 1), 4), round(nz / max(sd, 1), 4), round(v.mean(), 3)])
