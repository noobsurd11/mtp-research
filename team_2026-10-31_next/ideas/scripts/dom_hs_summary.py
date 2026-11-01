"""Summarise dom_halfcut_stats outputs per group: median [IQR] per statistic, plus gap-spacing (half-cell row pitch)
from consecutive gaps 120-220 px apart. Usage: python -I dom_hs_summary.py A.tsv [B.tsv ...]"""
import sys, csv, numpy as np, collections
d = collections.defaultdict(list)
for f in sys.argv[1:]:
    for r in csv.DictReader(open(f), delimiter='\t'): d[r['group']].append(r)
K = ['content_h', 'content_w', 'pitch_x', 'pitch_y_short', 'gap_w', 'gap_depth', 'edge_asym_abs', 'bb_period', 'mean', 'sd', 'lap', 'crack_w']
print('%-12s %4s ' % ('group', 'n') + ' '.join('%-17s' % k for k in K + ['row_pitch']))
for g, v in d.items():
    cells = []
    for k in K:
        a = np.array([float(x[k]) for x in v if x.get(k, '') not in ('', 'nan')])
        cells.append('%.3g [%.3g-%.3g]' % (np.median(a), np.percentile(a, 25), np.percentile(a, 75)) if len(a) else '-')
    sp = [int(s) for x in v for s in x.get('gap_spacings', '').split(',') if s and 120 <= int(s) <= 220]
    cells.append('%.0f [%.0f-%.0f] n%d' % (np.median(sp), np.percentile(sp, 25), np.percentile(sp, 75), len(sp)) if sp else '-')
    print('%-12s %4d ' % (g, len(v)) + ' '.join('%-17s' % c for c in cells))
