"""Label-free search for long, non-axis-aligned dark ridges (big cracks) in EL cells. CPU.
Score per image = total skeleton length (px, at 512) of dark-ridge components that are >= 60 px long and whose
main orientation is > 12 deg from both image axes. Usage: ridge_search.py <out.csv> <label>:<listfile> ..."""
import sys, csv, numpy as np
from PIL import Image
from skimage.filters import sato
from skimage.measure import label, regionprops
from skimage.morphology import skeletonize, remove_small_objects
w = csv.writer(open(sys.argv[1], 'w')); w.writerow(['label', 'path', 'score', 'ncomp'])
for arg in sys.argv[2:]:
    lab, lst = arg.split(':', 1)
    for p in [l.strip() for l in open(lst) if l.strip()]:
        im = Image.open(p).convert('L')
        if im.size != (512, 512): im = im.resize((512, 512), Image.BOX)
        a = np.asarray(im, dtype=np.float32)
        valid = a < 250
        a = (a - np.median(a[valid])) / (np.percentile(a[valid], 75) - np.percentile(a[valid], 25) + 1e-3)
        r = sato(a, sigmas=[1.5, 3], black_ridges=True); r[~valid] = 0
        thr = np.percentile(r[valid], 99)
        bw = remove_small_objects(r > thr, 40)
        sk = skeletonize(bw); L = label(sk, connectivity=2)
        score = 0; n = 0
        for rp in regionprops(L):
            if rp.area < 60: continue
            ang = abs(np.degrees(rp.orientation)) % 90
            if 12 < ang < 78:
                score += rp.area; n += 1
        w.writerow([lab, p, int(score), n])
