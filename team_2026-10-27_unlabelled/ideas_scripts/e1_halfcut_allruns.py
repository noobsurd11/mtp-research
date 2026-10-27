"""E1 half-cut vs other crack recall for every run in results/e1/raw_v2 (per-cell crack_gt/tp/pred), grouped by arm
(run name minus _sN). Half-cut = E-SCDD class 29 in mask. Usage: e1_halfcut_allruns.py"""
import json, glob, os, re, numpy as np, collections
from PIL import Image
R = os.path.expanduser('~/mtp/datasets/escdd_full')
D = '/home/yugma/mtp/research/results/e1/raw_v2/'
hc = None; arms = collections.defaultdict(list)
for f in sorted(glob.glob(D + '*.json')):
    d = json.load(open(f))
    if 'ext' not in d.get('cells', {}): continue
    ex = d['cells']['ext']
    if hc is None:
        hc = {}
        for st in ex:
            p = glob.glob(R + '/el_masks_*/' + st + '.png'); hc[st] = bool(p) and bool((np.asarray(Image.open(p[0])) == 29).any())
    out = []
    for grp in (True, False):
        t = g = pr = 0
        for st, v in ex.items():
            if hc.get(st) != grp or v['crack_gt'] < 20: continue
            t += v['crack_tp']; g += v['crack_gt']; pr += v['crack_pred']
        out.append((t / g, t / (g + pr - t)))
    arm = re.sub(r'_s\d+$', '', os.path.basename(f)[:-5])
    arms[arm].append(out)
print('%-28s %3s  %-22s %-22s' % ('arm', 'n', 'half-cut recall / IoU', 'other recall / IoU'))
for a in sorted(arms):
    x = np.array(arms[a])
    print('%-28s %3d  %.3f / %.3f            %.3f / %.3f' % (a, len(x), x[:, 0, 0].mean(), x[:, 0, 1].mean(), x[:, 1, 0].mean(), x[:, 1, 1].mean()))
