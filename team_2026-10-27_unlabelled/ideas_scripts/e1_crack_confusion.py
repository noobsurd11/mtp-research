"""Where do GT crack px go? Row 14 of the summed confusion matrix, E1 half-cut vs other vs test, FINAL b0.75 and SUP100 (mean of 5).
Also GT inactive (row 11). Usage: e1_crack_confusion.py"""
import json, glob, os, numpy as np
from PIL import Image
R = os.path.expanduser('~/mtp/datasets/escdd_full')
names = ['bg', 'sp_multi', 'sp_mono', 'sp_dogbone', 'ribbons', 'border', 'text', 'padding', 'clamp', 'busbars', 'crack_rbn_edge', 'inactive', 'rings',
         'material', 'crack', 'gridline', 'splice', 'dead_cell', 'corrosion_rbn', 'belt_mark', 'edge_dark', 'frame_edge', 'jbox', 'meas_artifact']
d = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))
hc = {}
for st in d['ext']['final_b0.75']:
    p = glob.glob(R + '/el_masks_*/' + st + '.png'); hc[st] = bool(p) and bool((np.asarray(Image.open(p[0])) == 29).any())
def rows(cells, sel, cls):
    S = np.zeros(24)
    for st, v in cells.items():
        if sel(st): S += np.array(v['conf']).reshape(24, 24)[cls]
    return S
for key in ['final_b0.75']:
    for lab, cells, sel in [('test', d['test'][key], lambda s: True), ('E1 halfcut', d['ext'][key], lambda s: hc[s]), ('E1 other', d['ext'][key], lambda s: not hc[s])]:
        for cls in (14, 11):
            r = rows(cells, sel, cls); tot = r.sum()
            if tot == 0: continue
            top = np.argsort(-r)[:5]
            print('%-10s GT %-8s px %6d -> ' % (lab, names[cls], tot) + ', '.join('%s %.2f' % (names[i], r[i] / tot) for i in top))
