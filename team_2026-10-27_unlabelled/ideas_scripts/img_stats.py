"""CPU image statistics (ideas, 27 Oct). Usage: img_stats.py <label> <listfile_of_paths> <out.csv>
Per image: grayscale (PIL convert L, as the loader), size, mean, sd, robust sd (IQR/1.349),
mean |Laplacian| (4-neighbour), on the central 80% to avoid padding/frame."""
import sys, csv, numpy as np
from PIL import Image
label, lst, out = sys.argv[1:4]
paths = [l.strip() for l in open(lst) if l.strip()]
w = csv.writer(open(out, 'w')); w.writerow(['label','path','w','h','mean','sd','rsd','lap','frac_dark'])
for p in paths:
    im = Image.open(p).convert('L'); W, H = im.size
    if (W, H) != (512, 512): im = im.resize((512, 512), Image.BOX)
    a = np.asarray(im, dtype=np.float32)
    c = a[51:-51, 51:-51]
    q1, q3 = np.percentile(c, [25, 75])
    lap = np.abs(4*c[1:-1,1:-1] - c[:-2,1:-1] - c[2:,1:-1] - c[1:-1,:-2] - c[1:-1,2:]).mean()
    w.writerow([label, p, W, H, round(float(c.mean()),2), round(float(c.std()),2), round(float((q3-q1)/1.349),2), round(float(lap),2), round(float((c<20).mean()),4)])
