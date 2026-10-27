"""Same image stats as e1_shift.py for pool images. Usage: pool_stats.py <img_dir> <meta.csv> <out.csv>"""
import sys, os, glob, csv, numpy as np
from PIL import Image
d, metaf, outf = sys.argv[1:4]
meta = {r['stem']: r for r in csv.DictReader(open(metaf))}
w = csv.writer(open(outf, 'w')); w.writerow(['stem', 'src', 'group', 'orig_w', 'mod', 'mean', 'sd', 'rsd', 'lap', 'noise'])
for p in sorted(glob.glob(d + '/*.png')):
    st = os.path.basename(p)[:-4]; a = np.asarray(Image.open(p).convert('L'), dtype=np.float32); c = a[51:-51, 51:-51]
    q1, q3 = np.percentile(c, [25, 75])
    lap = np.abs(4 * c[1:-1, 1:-1] - c[:-2, 1:-1] - c[2:, 1:-1] - c[1:-1, :-2] - c[1:-1, 2:])
    m = meta[st]
    w.writerow([st, st.split('_')[0], m['group'], m['orig_w'], int(st.split('_')[1]), round(float(c.mean()), 2), round(float(c.std()), 2),
                round(float((q3 - q1) / 1.349), 2), round(float(lap.mean()), 2), round(float(np.median(lap) / 0.6745 / np.sqrt(20)), 2)])
