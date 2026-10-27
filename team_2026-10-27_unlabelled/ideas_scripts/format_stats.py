"""Cell format per image: letterbox (near-white >=250 full rows/cols), content aspect.
Usage: format_stats.py <out.csv> <label>:<listfile_of_paths> ..."""
import sys, csv, numpy as np
from PIL import Image
w = csv.writer(open(sys.argv[1], 'w')); w.writerow(['label', 'path', 'white_rows', 'white_cols', 'content_h', 'content_w', 'aspect'])
for arg in sys.argv[2:]:
    lab, lst = arg.split(':', 1)
    for p in [l.strip() for l in open(lst) if l.strip()]:
        a = np.asarray(Image.open(p).convert('L'), dtype=np.float32)
        if a.shape != (512, 512): a = np.asarray(Image.fromarray(a.astype(np.uint8)).resize((512, 512), Image.BOX), dtype=np.float32)
        wr = (np.mean(a >= 250, axis=1) > 0.98); wc = (np.mean(a >= 250, axis=0) > 0.98)
        ch, cw = int((~wr).sum()), int((~wc).sum())
        w.writerow([lab, p, int(wr.sum()), int(wc.sum()), ch, cw, round(cw / max(ch, 1), 2)])
