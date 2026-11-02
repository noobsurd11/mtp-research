"""arch A3 premise (DESCRIPTIVE; Hanifi _rf only, no test, no E1): where do SUPPF s5-9 and HC s5-9 put crack false positives
on real unseen-module cells, by GT structure class, and how much of the half-cut cut-line confusion has HC already removed?
Adapted from domain's dom_fp_classes.py (527e6073; same class names, same 3-px 'near structure' rule).
Rule (fixed before any number): pred crack = margin + b > 0 inside keep (ignore excluded); FP = pred & GT != crack(14);
b = 0 and each run's val b_rel from the HC opening's hc_f51.json (calib el_metrics rule); sets H36 (36 half-cut) and F51 (51);
reported per arm (sum over its 5 runs / 5): FP px by GT class, FP px on crack-free cells, FN px within 3 px of
busbar/ribbon/spacing (classes 1,2,3,4,9) vs all GT crack px within 3 px.
Usage: python -I a3_fp_struct.py DUMPDIR RFDIR SETS_TSV HC_F51_JSON"""
import sys, csv, json, collections, numpy as np
from PIL import Image
from scipy import ndimage as ndi
D, RF, SETS, HJ = sys.argv[1:5]
NAMES = {0: 'bckgnd', 1: 'sp multi', 2: 'sp mono', 3: 'sp dogbone', 4: 'ribbons', 5: 'border', 7: 'padding', 9: 'busbars', 11: 'inactive', 13: 'material', 15: 'gridline'}
SET = {r['stem']: r['set'] for r in csv.DictReader(open(SETS), delimiter='\t')}
brel = json.load(open(HJ))['b_rel_val']
ARMS = {'SUPPF': [f'pf2_SUPPF_100pct_s{k}' for k in range(5, 10)], 'HC': [f'hc_HC_100pct_s{k}' for k in range(5, 10)]}
cache = {}
for arm, runs in ARMS.items():
    acc = collections.defaultdict(collections.Counter)
    for r in runs:
        z = np.load(f'{D}/{r}.rf.npz')
        for i, st in enumerate(z['stems']):
            st = str(st); g = SET.get(st)
            if g not in ('H36', 'F51'):
                continue
            if st not in cache:
                m = np.asarray(Image.open(f'{RF}/masks/{st}.png')); ign = np.asarray(Image.open(f'{RF}/ignore/{st}.png')) > 0
                near = ndi.binary_dilation(np.isin(m, [1, 2, 3, 4, 9]), iterations=3)
                cache[st] = (m, ~ign, near)
            m, v, near = cache[st]; gt = (m == 14) & v; cf = int(gt.sum()) == 0
            mg = z['margin'][i].astype(np.float32)
            for lab, b in (('b0', 0.0), ('brel', float(brel[r]))):
                pr = (mg + b > 0) & v; fp = pr & ~gt; c = acc[(g, lab)]
                for k, n in zip(*np.unique(m[fp], return_counts=True)):
                    c['fp_' + NAMES.get(int(k), str(int(k)))] += int(n)
                c['fp'] += int(fp.sum()); c['fp_cf'] += int(fp.sum()) if cf else 0
                fn = gt & ~pr; c['fn'] += int(fn.sum()); c['fn_near'] += int((fn & near).sum())
                c['gt'] += int(gt.sum()); c['gt_near'] += int((gt & near).sum()); c['tp'] += int((pr & gt).sum())
    for (g, lab), c in sorted(acc.items()):
        n = len(runs)
        top = sorted([(k[3:], v_) for k, v_ in c.items() if k.startswith('fp_') and k != 'fp_cf'], key=lambda t: -t[1])[:7]
        print('%-5s %-3s %-4s FP px/run %7.1f (on crack-free cells %7.1f) by GT class: %s' % (arm, g, lab, c['fp'] / n, c['fp_cf'] / n,
              ', '.join('%s %.0f%% (%.0f)' % (k, 100 * v_ / max(c['fp'], 1), v_ / n) for k, v_ in top)))
        print('                FN px/run %7.1f, %.0f%% within 3 px of busbar/ribbon/spacing; GT crack px %d/run, %.0f%% within 3 px; TP px/run %.1f' % (
              c['fn'] / n, 100 * c['fn_near'] / max(c['fn'], 1), c['gt'] / n, 100 * c['gt_near'] / max(c['gt'], 1), c['tp'] / n))
