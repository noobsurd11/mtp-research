"""Label-free proposer for scuff(+crack) cells, tested on E1 where labels exist. Signals use model outputs only:
(a) L3 100% (3 seeds) total predicted crack px incl. px on ignored classes; (b) FINAL +0.75 largest predicted crack
component (px). Targets: scuff >= 500 px; scuff >= 500 AND crack >= 20. AUROC (Mann-Whitney) and precision of top-k.
Usage: scuff_proposer.py"""
import glob, os, json, numpy as np
from PIL import Image
from scipy.stats import mannwhitneyu
R = os.path.expanduser('~/mtp/datasets/escdd_full')
f = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))['ext']['final_b0.75']
runs = [json.load(open(p))['cells']['ext'] for p in sorted(glob.glob('/home/yugma/mtp/research/results/e1/raw_v2/p6_L3_100pct_s*.json'))]
rows = []
for st in f:
    p = glob.glob(R + '/el_masks_*/' + st + '.png')
    if not p: continue
    a = np.asarray(Image.open(p[0])); sc = (a == 25).sum() >= 500; cr = (a == 14).sum() >= 20; hc = (a == 29).any()
    tot = np.mean([r[st]['crack_pred'] + r[st]['crack_pred_on_ignored'] for r in runs])
    onign = np.mean([r[st]['crack_pred_on_ignored'] for r in runs])
    big = max([c[0] for c in f[st]['crack_cc']['pr']] or [0])
    rows.append((sc, sc and cr, hc, tot, big, onign))
x = np.array(rows, dtype=float)
def auc(s, y):
    a, b = s[y == 1], s[y == 0]; return mannwhitneyu(a, b).statistic / (len(a) * len(b))
for name, j in [('L3 total pred crack px', 3), ('FINAL largest pred component', 4)]:
    for tname, t in [('scuff', 0), ('scuff+crack', 1)]:
        y = x[:, t]; s = x[:, j]; order = np.argsort(-s)
        print('%-30s target %-11s AUROC %.2f  prec@10 %.2f  prec@20 %.2f  (base rate %.2f, n %d)' %
              (name, tname, auc(s, y), y[order[:10]].mean(), y[order[:20]].mean(), y.mean(), len(y)))
hcmask = x[:, 2] == 1
y = x[hcmask, 0]; s = x[hcmask, 4]; print('within half-cut cells only: FINAL largest component vs scuff AUROC %.2f (n %d, base %.2f)' % (auc(s, y), hcmask.sum(), y.mean()))
print('L3 crack px on ignored (scuff etc.) per run, sum over E1: %.0f' % x[:, 5].sum())
