"""Summarise e1_shift.csv (no pandas). Usage: e1_summary.py e1_shift.csv"""
import csv, sys, numpy as np
from scipy.stats import spearmanr
rows = list(csv.DictReader(open(sys.argv[1])))
def f(r, k):
    try: return float(r[k])
    except: return np.nan
cols = ['mean', 'sd', 'rsd', 'lap', 'noise']
ccols = ['crack_px', 'crack_dark', 'crack_rel_dark', 'crack_width', 'rec', 'p001']
groups = {}
for r in rows: groups.setdefault((r['set'], r['src']), []).append(r)
for s in ['train', 'test', 'ext']: groups[(s, 'ALL')] = [r for r in rows if r['set'] == s]
print('group n | ' + ' '.join(cols) + ' || crack cells: n ' + ' '.join(ccols))
for k in sorted(groups):
    g = groups[k]; gc = [r for r in g if f(r, 'crack_px') >= 20]
    a = [np.nanmedian([f(r, c) for r in g]) for c in cols]
    b = [np.nanmedian([f(r, c) for r in gc]) if gc else np.nan for c in ccols]
    print(k, len(g), ' '.join('%.2f' % x for x in a), '||', len(gc), ' '.join('%.3f' % x for x in b))
for s in ['test', 'ext']:
    x = [r for r in rows if r['set'] == s and not np.isnan(f(r, 'rec'))]
    rec = np.array([f(r, 'rec') for r in x])
    print(s, 'cells', len(x), 'mean per-cell rec %.3f' % rec.mean(), 'median %.3f' % np.median(rec), 'share rec<0.1: %.2f' % (rec < 0.1).mean())
    for c in ['sd', 'lap', 'noise', 'mean', 'crack_dark', 'crack_rel_dark', 'crack_width', 'crack_px']:
        v = np.array([f(r, c) for r in x]); ok = ~np.isnan(v)
        rr = spearmanr(v[ok], rec[ok]); print('   rec ~ %-15s rho %+.2f p %.3f' % (c, rr.correlation, rr.pvalue))
