"""Idea 11 coverage table: per group median [p10-p90] of mean, sd, shape, sharp, noise; and for each non-train group,
the share of cells outside the train envelope under the house jitter: mean/sd reachable if some train cell (m, s)
maps to within 5% via a in [0.8,1.2], b in [-51,51]; invariant ratios: outside train p2.5-p97.5.
Usage: python -I dom_ap_summary.py A.tsv [B.tsv]"""
import sys, csv, numpy as np, collections
d = collections.defaultdict(list)
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f), delimiter='\t'): d[r['group']].append({k: float(v) for k, v in r.items() if k not in ('group', 'img')})
tr = [x for g, v in d.items() if g.startswith('train_') for x in v]; d['train_all'] = tr
K = ['mean', 'sd', 'shape', 'sharp', 'noise']
print('%-11s %4s ' % ('group', 'n') + ' '.join('%-21s' % k for k in K))
for g in sorted(d):
    v = d[g]; print('%-11s %4d ' % (g, len(v)) + ' '.join('%-21s' % ('%.3g [%.3g-%.3g]' % (np.median([x[k] for x in v]), np.percentile([x[k] for x in v], 10), np.percentile([x[k] for x in v], 90))) for k in K))
TM = np.array([[x['mean'], x['sd']] for x in tr])
def reach(m, s):
    a = s / TM[:, 1]; ok = (a >= 0.8 * 0.95) & (a <= 1.2 * 1.05); b = m - a * TM[:, 0]
    return bool(np.any(ok & (np.abs(b) <= 51 * 1.05 + 0.05 * m)))
lo = {k: np.percentile([x[k] for x in tr], 2.5) for k in K}; hi = {k: np.percentile([x[k] for x in tr], 97.5) for k in K}
print('\nshare of cells outside the train envelope (house jitter for mean/sd; train p2.5-p97.5 for the invariant ratios)')
for g in sorted(d):
    if g.startswith('train'): continue
    v = d[g]; out = {k: np.mean([(x[k] < lo[k]) or (x[k] > hi[k]) for x in v]) for k in ('shape', 'sharp', 'noise')}
    print('%-11s n %4d  mean/sd unreachable %.2f | shape %.2f  sharp %.2f  noise %.2f' % (g, len(v), np.mean([not reach(x['mean'], x['sd']) for x in v]), out['shape'], out['sharp'], out['noise']))
