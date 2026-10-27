"""E1 crack metrics on half-cut multi cells vs other cells, per Track M rung (5 seeds each), plus cell-level detection.
Half-cut = E-SCDD class 29 present in the cell's mask. Usage: e1_halfcut_rungs.py"""
import json, glob, os, numpy as np
from PIL import Image
T = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
R = os.path.expanduser('~/mtp/datasets/escdd_full')
rungs = {'SUP100': sorted(glob.glob(T + 'm0b/*.json')), 'R3_rn50': sorted(glob.glob(T + 'r3b/*.json')),
         'R4_+107': sorted(glob.glob(T + 'r4/*.json')), 'R5_x2': sorted(glob.glob(T + 'r5/*.json'))}
hc = None
def cells(f):
    d = json.load(open(f)); return d['cells']['ext']
for name, fs in rungs.items():
    acc = {True: [], False: []}
    for f in fs:
        ex = cells(f)
        if hc is None:
            hc = {}
            for st in ex:
                p = glob.glob(R + '/el_masks_*/' + st + '.png'); hc[st] = bool(p) and bool((np.asarray(Image.open(p[0])) == 29).any())
        for grp in (True, False):
            tp = gt = pr = 0; det = n = 0
            for st, v in ex.items():
                if hc[st] != grp: continue
                cf = np.array(v['conf']).reshape(24, 24); g = cf[14].sum()
                if g >= 20:
                    tp += cf[14, 14]; gt += g; pr += cf[:, 14].sum(); n += 1
                    det += cf[14, 14] >= 20  # cell-level: >= 20 GT crack px hit
            acc[grp].append((tp / gt, tp / max(pr, 1), tp / (gt + pr - tp), det / n))
    for grp in (True, False):
        a = np.array(acc[grp])
        print('%-8s %-7s n_seeds %d  recall %.3f (sd %.3f)  prec %.3f  IoU %.3f (sd %.3f)  cells hit %.2f' %
              (name, 'halfcut' if grp else 'other', len(a), a[:, 0].mean(), a[:, 0].std(ddof=1), a[:, 1].mean(), a[:, 2].mean(), a[:, 2].std(ddof=1), a[:, 3].mean()))
