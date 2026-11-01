"""Check: per-image counts (dom_score_synvar v2 --percell) re-aggregate to the pooled V-series numbers in synvar.log
(crack cells = GT >= 20 px; recall, precision, IoU, relR@2 pooled; inactive IoU over all images); also paired
per-source-cell deltas V0 -> V3/V4 (crack recall per source cell, summed over both halves).
Usage: python -I dom_synvar_check.py synvar_percell.tsv"""
import sys, csv, collections, numpy as np
R = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
agg = collections.defaultdict(lambda: collections.Counter())
for r in R:
    k = (r['group'], r['bias'], r['variant']); c = agg[k]; gt = int(r['gt_crack'])
    if gt >= 20:
        c['n'] += 1
        for f in ('tp', 'fp', 'fn', 'relR2_hit', 'relP2_hit', 'pred_px'): c[f] += int(r[f])
        c['gn'] += gt
    for f in ('itp', 'ifp', 'ifn'): c[f] += int(r[f])
for k in sorted(agg):
    c = agg[k]
    print('%-7s b %-4s %s n %3d recall %.3f prec %.3f IoU %.3f relR@2 %.3f inactive IoU %.3f' % (k + (c['n'], c['tp'] / max(c['tp'] + c['fn'], 1),
          c['tp'] / max(c['tp'] + c['fp'], 1), c['tp'] / max(c['tp'] + c['fp'] + c['fn'], 1), c['relR2_hit'] / max(c['gn'], 1), c['itp'] / max(c['itp'] + c['ifp'] + c['ifn'], 1))))
# paired per source cell (V0 vs V3/V4), recall on source cells with crack in both
for g in sorted(set(r['group'] for r in R)):
    for b in ('0.75',):
        d = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
        for r in R:
            if r['group'] != g or r['bias'] != b: continue
            v = d[r['src']][r['variant']]; v[0] += int(r['tp']); v[1] += int(r['gt_crack'])
        for vn in ('V3', 'V4'):
            x = [(s[vn][0] / s[vn][1]) - (s['V0'][0] / s['V0'][1]) for s in d.values() if s['V0'][1] >= 20 and s[vn][1] >= 20]
            print('%s b %s paired per-cell recall %s - V0: n %d, median %+.3f, mean %+.3f, cells worse %d' % (g, b, vn, len(x), np.median(x), np.mean(x), sum(1 for z in x if z < 0)))
