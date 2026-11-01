"""Idea 5 extension spec: scuff morphology from NON-E1 labels (train 12 cells with class 25 in E-SCDD masks; Hanifi
_rf cells with scuff). Per scuff component >= 50 px: area, length (skeleton px), width (area / skeleton), bbox
extent, darkness = (median ring - median scuff) / median ring (ring = dilate 8 - dilate 3, non-defect px);
crack px within 15 px of scuff, and median crack-to-scuff distance per cell. Usage: python -I dom_scuff_morph.py INDEX.tsv"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['set'] in ('train', 'rf') and r['mask'] and int(r['scuff_px'] or 0) > 0]
out = []
for r in rows:
    I = np.asarray(Image.open(r['img']).convert('L'), dtype=float); m = np.asarray(Image.open(r['mask']))
    sc = m == 25; cr = m == 14; neg = np.isin(m, [0, 1, 2, 3, 4, 5, 9])
    lab, n = ndi.label(sc, structure=np.ones((3, 3)))
    dist = ndi.distance_transform_edt(~sc)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        c = lab == i
        if c.sum() < 50: continue
        sk = skeletonize(c).sum(); ring = ndi.binary_dilation(c, iterations=8) & ~ndi.binary_dilation(c, iterations=3) & neg
        dk = (np.median(I[ring]) - np.median(I[c])) / max(np.median(I[ring]), 1) if ring.sum() > 20 else np.nan
        out.append((r['set'] + ('_half' if r['halfcut'] == '1' else ''), r['stem'], int(c.sum()), int(sk), c.sum() / max(sk, 1),
                    max(sl[0].stop - sl[0].start, sl[1].stop - sl[1].start), dk, int((cr & (dist <= 15)).sum()), int(cr.sum()),
                    float(np.median(dist[cr])) if cr.any() else np.nan))
groups = sorted(set(o[0] for o in out))
for g in groups:
    v = [o for o in out if o[0] == g]; a = np.array([o[2:] for o in v], dtype=float)
    print('%-9s comps %2d cells %2d | area med %.0f [%.0f-%.0f] | length med %.0f | width med %.1f [%.1f-%.1f] | extent med %.0f | darkness med %.2f [%.2f-%.2f] | cells with crack within 15 px of scuff: %d' % (
        g, len(v), len(set(o[1] for o in v)), np.median(a[:, 0]), a[:, 0].min(), a[:, 0].max(), np.median(a[:, 1]), np.median(a[:, 2]), np.percentile(a[:, 2], 10), np.percentile(a[:, 2], 90),
        np.median(a[:, 3]), np.nanmedian(a[:, 4]), np.nanpercentile(a[:, 4], 10), np.nanpercentile(a[:, 4], 90), len(set(o[1] for o in v if o[7] > 0))))
