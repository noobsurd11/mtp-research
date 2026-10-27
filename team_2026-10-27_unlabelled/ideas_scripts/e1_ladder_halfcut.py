"""P6 ladder (and Track M FINAL-like refs) on E1 half-cut vs other: recall, precision, IoU, relR@2-like hit share, false alarm
on crack-free cells of the same group (pred >= 50 px), and test crack IoU for reference. Per-seed then mean. Usage: e1_ladder_halfcut.py"""
import json, glob, os, re, numpy as np, collections
from PIL import Image
R = os.path.expanduser('~/mtp/datasets/escdd_full'); D = '/home/yugma/mtp/research/results/e1/raw_v2/'
arms = ['p6_L0_100pct', 'p6_L0_10pct', 'p6_L1_10pct', 'p6_L2_10pct', 'p6_L3_10pct', 'p6_L3_100pct', 'p16_A_100pct', 'p16_Sx_100pct']
hc = None
for a in arms:
    res = []
    for f in sorted(glob.glob(D + a + '_s*.json')):
        d = json.load(open(f))['cells']; ex = d['ext']; te = d['test']
        if hc is None:
            hc = {}
            for st in ex:
                p = glob.glob(R + '/el_masks_*/' + st + '.png'); hc[st] = bool(p) and bool((np.asarray(Image.open(p[0])) == 29).any())
        row = []
        for grp in (True, False):
            t = g = pr = h = 0; fa = n0 = 0
            for st, v in ex.items():
                if hc[st] != grp: continue
                if v['crack_gt'] >= 20: t += v['crack_tp']; g += v['crack_gt']; pr += v['crack_pred']; h += v['crack_r2_hit']
                else: n0 += 1; fa += v['crack_pred'] >= 50
            row += [t / g, t / max(pr, 1), t / (g + pr - t), h / g, fa / n0]
        t = sum(v['crack_tp'] for v in te.values()); g = sum(v['crack_gt'] for v in te.values()); pr = sum(v['crack_pred'] for v in te.values())
        row.append(t / (g + pr - t)); res.append(row)
    x = np.array(res).mean(0)
    print('%-15s n%d | half-cut R %.3f P %.3f IoU %.3f relR2 %.3f FA %.2f | other R %.3f P %.3f IoU %.3f relR2 %.3f FA %.2f | test crack IoU %.3f' % ((a, len(res)) + tuple(x)))
