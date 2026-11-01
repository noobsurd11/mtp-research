"""Idea 5 premise: does the current model fail on NON-E1 half-cuts? Reads calib's read-only margin dumps
(calib_dump.py: margin = log p_crack - max other log p; crack iff margin + b > 0) for the Hanifi _rf hygiene set
(106) and val (54). Strata: rf half-cut crack cells, rf full crack cells, val crack cells (GT crack >= 20 px).
Pooled per stratum: pixel recall / precision / IoU, relR@2 (GT px within 2 px of a prediction), relP@2; cell
detection = relR@2 >= 0.2; crack px predicted per crack-free cell; crack px predicted on ignore (scuff etc.) px.
Ignore px (calib data/rf/ignore) excluded from all counts. No E1, no test. Usage:
python -I dom_rf_halfcut_baseline.py DUMPDIR CALIB_RF_DIR VAL_MASK_DIR MODEL[:bias] ..."""
import sys, csv, numpy as np
from PIL import Image
from scipy import ndimage as ndi
D, RF, VM = sys.argv[1], sys.argv[2], sys.argv[3]
ctx = {r['stem']: r for r in csv.DictReader(open(RF + '/rf_context.tsv'), delimiter='\t')}
disk = np.array([[1 if (i - 2) ** 2 + (j - 2) ** 2 <= 4 else 0 for j in range(5)] for i in range(5)], bool)
def stats(pred, gt, ign):
    v = ~ign; p = pred & v; g = gt & v
    tp = (p & g).sum(); fp = (p & ~g).sum(); fn = (~p & g).sum()
    pd = ndi.binary_dilation(p, disk); gd = ndi.binary_dilation(g, disk)
    return dict(tp=tp, fp=fp, fn=fn, rr=(g & pd).sum(), gn=g.sum(), rp=(p & gd).sum(), pn=p.sum(), ign_pred=(pred & ign).sum())
for spec in sys.argv[4:]:
    name, b = (spec.split(':') + ['0'])[:2]; b = float(b)
    agg = {}
    for sset in ('rf', 'val'):
        try:
            z = np.load(f'{D}/{name}.{sset}.npz')
        except FileNotFoundError:
            print(name, sset, 'missing'); continue
        for i, st in enumerate(z['stems']):
            st = str(st); pred = z['margin'][i].astype(np.float32) + b > 0
            if sset == 'rf':
                m = np.asarray(Image.open(f'{RF}/masks/{st}.png')); ign = np.asarray(Image.open(f'{RF}/ignore/{st}.png')) > 0
                hc = ctx[st]['halfcut'] == '1'; grp = 'rf_half' if hc else 'rf_full'
            else:
                m = np.asarray(Image.open(f'{VM}/{st}.png')); ign = np.zeros(m.shape, bool); grp = 'val'
            gt = m == 14; s = stats(pred, gt, ign)
            key = grp + ('_crack' if s['gn'] >= 20 else ('_free' if s['gn'] == 0 else '_tiny'))
            a = agg.setdefault(key, {'n': 0, 'det': 0, 'cells_pred': 0, **{k: 0 for k in s}})
            a['n'] += 1; a['det'] += int(s['gn'] >= 20 and s['rr'] / max(s['gn'], 1) >= 0.2); a['cells_pred'] += int(s['pn'] >= 20)
            for k in s: a[k] += s[k]
    print(f'== {name} bias {b}')
    for k in sorted(agg):
        a = agg[k]
        if k.endswith('_crack'):
            print('  %-14s n %3d  recall %.3f  prec %.3f  IoU %.3f  relR@2 %.3f  relP@2 %.3f  cells det %d/%d  gt px %d  pred-on-ignore px %d' % (
                k, a['n'], a['tp'] / max(a['tp'] + a['fn'], 1), a['tp'] / max(a['tp'] + a['fp'], 1), a['tp'] / max(a['tp'] + a['fp'] + a['fn'], 1),
                a['rr'] / max(a['gn'], 1), a['rp'] / max(a['pn'], 1), a['det'], a['n'], a['gn'], a['ign_pred']))
        else:
            print('  %-14s n %3d  pred crack px per cell %.0f  cells with >=20 pred px %d  pred-on-ignore px %d' % (k, a['n'], a['pn'] / a['n'], a['cells_pred'], a['ign_pred']))
