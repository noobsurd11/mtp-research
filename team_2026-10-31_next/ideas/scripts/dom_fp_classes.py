"""Ideas 3/4 premise: does the deployed model confuse busbars/ribbons/gaps with cracks? From calib's FINAL dump:
crack FP px by GT class (val; Hanifi _rf full / half), and missed crack px (FN) within 3 px of busbar/ribbon/spacing
vs all crack px within 3 px of them. Bias +0.75 (FINAL). Usage: python -I dom_fp_classes.py DUMPDIR CALIB_RF VAL_MASKS"""
import sys, csv, collections, numpy as np
from PIL import Image
from scipy import ndimage as ndi
D, RF, VM = sys.argv[1:4]
ctx = {r['stem']: r for r in csv.DictReader(open(RF + '/rf_context.tsv'), delimiter='\t')}
NAMES = {0: 'bckgnd', 1: 'sp multi', 2: 'sp mono', 3: 'sp dogbone', 4: 'ribbons', 5: 'border', 7: 'padding', 9: 'busbars', 11: 'inactive', 13: 'material', 15: 'gridline'}
for sset in ('val', 'rf'):
    z = np.load(f'{D}/FINAL.{sset}.npz'); acc = collections.defaultdict(lambda: collections.Counter())
    for i, st in enumerate(z['stems']):
        st = str(st); pr = z['margin'][i].astype(np.float32) + 0.75 > 0
        if sset == 'val':
            m = np.asarray(Image.open(f'{VM}/{st}.png')); ign = np.zeros(m.shape, bool); g = 'val'
        else:
            m = np.asarray(Image.open(f'{RF}/masks/{st}.png')); ign = np.asarray(Image.open(f'{RF}/ignore/{st}.png')) > 0
            g = 'rf_half' if ctx[st]['halfcut'] == '1' else 'rf_full'
        gt = m == 14; v = ~ign; fp = pr & ~gt & v
        c = acc[g]
        for k, n in zip(*np.unique(m[fp], return_counts=True)): c['fp_' + NAMES.get(int(k), str(int(k)))] += int(n)
        c['fp'] += int(fp.sum())
        near = ndi.binary_dilation(np.isin(m, [1, 2, 3, 4, 9]), iterations=3)
        fn = gt & ~pr & v; c['fn'] += int(fn.sum()); c['fn_near'] += int((fn & near).sum()); c['gt'] += int((gt & v).sum()); c['gt_near'] += int((gt & v & near).sum())
    for g, c in acc.items():
        top = sorted([(k[3:], n) for k, n in c.items() if k.startswith('fp_')], key=lambda t: -t[1])[:6]
        print('%-8s crack FP px %6d by GT class: %s' % (g, c['fp'], ', '.join('%s %.0f%%' % (k, 100 * n / max(c['fp'], 1)) for k, n in top)))
        print('         FN px %6d, %.0f%% within 3 px of busbar/ribbon/spacing; all GT crack px %.0f%% within 3 px' % (c['fn'], 100 * c['fn_near'] / max(c['fn'], 1), 100 * c['gt_near'] / max(c['gt'], 1)))
