"""E1 crack recall split by cell type (half-cut multi = E-SCDD class 29 present) for FINAL b0.75 and b0.
Usage: e1_halfcut_recall.py"""
import json, glob, os, numpy as np
from PIL import Image
R = os.path.expanduser('~/mtp/datasets/escdd_full')
d = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))
hc = {}
for st in d['ext']['final_b0.75']:
    p = glob.glob(R + '/el_masks_*/' + st + '.png')
    hc[st] = bool(p) and bool((np.asarray(Image.open(p[0])) == 29).any())
for key in ['final_b0.75', 'final_b0']:
    for grp in [True, False]:
        tp = gt = pr = n = 0; pb = np.zeros(5); fa = fan = 0
        for st, v in d['ext'][key].items():
            if hc[st] != grp: continue
            cf = np.array(v['conf']).reshape(24, 24)
            g = cf[14].sum()
            if g >= 20:
                tp += cf[14, 14]; gt += g; pr += cf[:, 14].sum(); n += 1; pb += np.array(v['crack_pband_gt'])
            else:
                fan += 1; fa += cf[:, 14].sum() >= 50
        print(key, 'halfcut' if grp else 'other  ', 'crack cells', n, 'GT px', gt, 'recall %.3f' % (tp / gt), 'precision %.3f' % (tp / max(pr, 1)),
              'IoU %.3f' % (tp / (gt + pr - tp)), 'p<.001 share %.2f' % (pb[0] / pb.sum()), '| crack-free cells', fan, 'false alarm %.2f' % (fa / max(fan, 1)))
