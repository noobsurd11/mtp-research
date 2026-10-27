"""Post hoc, descriptive: rung - SUP100 on E1 half-cut crack cells (26). Rule-1 arithmetic over 5 v 5 seeds, and a paired
cell bootstrap (2,000) of pooled recall and IoU with per-cell counts summed over seeds. Usage: e1_halfcut_boot.py"""
import json, glob, os, numpy as np
from PIL import Image
T = '/home/yugma/mtp/research/team_2026-10-24_go/trackM/'
R = os.path.expanduser('~/mtp/datasets/escdd_full')
rungs = {'SUP100': 'm0b', 'R3_rn50': 'r3b', 'R4_+107': 'r4', 'R5_x2': 'r5'}
def load(dirn):
    out = []
    for f in sorted(glob.glob(T + dirn + '/*.json')):
        ex = json.load(open(f))['cells']['ext']; out.append(ex)
    return out
runs = {k: load(v) for k, v in rungs.items()}
stems = list(runs['SUP100'][0])
hc = []
for st in stems:
    p = glob.glob(R + '/el_masks_*/' + st + '.png')
    if p and (np.asarray(Image.open(p[0])) == 29).any():
        cf = np.array(runs['SUP100'][0][st]['conf']).reshape(24, 24)
        if cf[14].sum() >= 20: hc.append(st)
def counts(ex_list):  # per cell [tp, gt, pred] summed over seeds; and per-seed pooled metrics
    C = np.zeros((len(hc), 3)); per = []
    for ex in ex_list:
        c = np.array([[np.array(ex[s]['conf']).reshape(24, 24)[14, 14], np.array(ex[s]['conf']).reshape(24, 24)[14].sum(),
                       np.array(ex[s]['conf']).reshape(24, 24)[:, 14].sum()] for s in hc], dtype=float)
        C += c; t, g, p = c.sum(0); per.append((t / g, t / (g + p - t)))
    return C, np.array(per)
base_C, base_p = counts(runs['SUP100'])
rng = np.random.default_rng(0)
idx = rng.integers(0, len(hc), (2000, len(hc)))
def met(C, i):
    t, g, p = C[i].sum(1).T if C[i].ndim == 3 else C[i].sum(0); return t / g, t / (g + p - t)
for k in ['R3_rn50', 'R4_+107', 'R5_x2']:
    C, per = counts(runs[k])
    for j, name in enumerate(['recall', 'IoU']):
        d = per[:, j].mean() - base_p[:, j].mean()
        thr = max(0.01, 2 * np.sqrt(per[:, j].var(ddof=1) / 5 + base_p[:, j].var(ddof=1) / 5))
        bs = []
        for ii in idx:
            a = C[ii].sum(0); b = base_C[ii].sum(0)
            ma = (a[0] / a[1], a[0] / (a[1] + a[2] - a[0])); mb = (b[0] / b[1], b[0] / (b[1] + b[2] - b[0]))
            bs.append(ma[j] - mb[j])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print('%-8s %-6s delta %+.3f  rule-1 thr %.3f  cell-bootstrap 95%% CI [%+.3f, %+.3f]' % (k, name, d, thr, lo, hi))
print('half-cut crack cells', len(hc), 'modules', len(set('_'.join(s.split('_')[:2]) for s in hc)))
