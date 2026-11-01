"""Idea 4 exposure: crack components by extent along the image axes. A component is 'long axis-parallel' if its
bounding box is >= 200 px along one axis and <= 30 px along the other (a straight crack parallel to busbars or
fingers spanning most of a cell). Share of crack px in such components, per set. Usage: python -I dom_crack_orient.py INDEX.tsv"""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['mask'] and r['set'] in ('train', 'val', 'rf')]
acc = {}
for r in rows:
    m = np.asarray(Image.open(r['mask'])) == 14
    if m.sum() < 20: continue
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    a = acc.setdefault(r['set'] + ('_half' if r['halfcut'] == '1' else ''), [0, 0, 0, 0])
    a[0] += int(m.sum()); a[3] += 1; cellhit = 0
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if (h >= 200 and w <= 30) or (w >= 200 and h <= 30):
            a[1] += int((lab[sl] == i).sum()); cellhit = 1
    a[2] += cellhit
for k, (tot, lng, cells, ncell) in acc.items():
    print('%-8s crack cells %3d  crack px %7d  in long axis-parallel comps %6d (%.1f%%)  cells with one %d' % (k, ncell, tot, lng, 100 * lng / tot, cells))
