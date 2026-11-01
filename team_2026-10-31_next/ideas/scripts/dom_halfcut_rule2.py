"""Rule R2b for the label-free half-cut detector (features from dom_halfcut_detector2.py md5 afa6af10), developed after
R1 failed (FP 9.45%) and after a peak-dominance variant failed on DEV (train FP 32% at delta 0). Disclosed as
developed on DEV. Rule: half-cut iff max(F_x, F_y) < a AND max(S_x, S_y) >= b, where F = autocorrelation peak at the
full-cell pitch (240-272 px) and S = peak at the half-cell row pitch (140-190 px); NaN F counts as 1 (not routed).
Selection, stated before running: (a, b) on the grid a in 0.06..0.40 (0.02), b in 0.04..0.40 (0.02) maximising DEV
recall (pool half-cells of modules CSIR_00297-00299) subject to FP <= 0.5% on train (478); ties -> larger a, then
smaller b. HELD-OUT check (not used to choose): val 54, pool half 00301/00333-00335, pool full cells (extra), Hanifi
_rf 106. Test listed by ID if routed (structure only, never scored). No E1.
Usage: python -I dom_halfcut_rule2.py det2_feats.tsv OUT_ROUTED.tsv"""
import sys, csv, re, os, numpy as np, collections
R = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
def fv(r, k):
    try: return float(r[k])
    except ValueError: return float('nan')
for r in R:
    Fx, Fy = fv(r, 'F_x'), fv(r, 'F_y'); Sx, Sy = fv(r, 'S_x'), fv(r, 'S_y')
    F = np.nanmax([Fx, Fy]) if np.isfinite([Fx, Fy]).any() else 1.0
    if not (np.isfinite(Fx) and np.isfinite(Fy)): F = max(F, 1.0) if not np.isfinite([Fx, Fy]).all() else F
    S = np.nanmax([Sx, Sy]) if np.isfinite([Sx, Sy]).any() else -1.0
    r['_F'], r['_S'] = F, S
def rule(r, a, b): return int(r['_F'] < a and r['_S'] >= b)
def mod(r): m = re.search(r'(CSIR_\d+)_r', os.path.basename(r['img'])); return m.group(1) if m else ''
DEVPOS = {'CSIR_00297', 'CSIR_00298', 'CSIR_00299'}
neg = [r for r in R if r['group'].startswith('train_')]; pos = [r for r in R if r['group'] == 'pool_half' and mod(r) in DEVPOS]
best = None
for a in np.round(np.arange(0.06, 0.401, 0.02), 2):
    for b in np.round(np.arange(0.04, 0.401, 0.02), 2):
        fp = np.mean([rule(r, a, b) for r in neg]); rc = np.mean([rule(r, a, b) for r in pos])
        if fp <= 0.005:
            key = (rc, a, -b)
            if best is None or key > best[0]: best = (key, a, b, fp, rc)
_, A, B, fp, rc = best
print('chosen a = %.2f, b = %.2f (DEV train FP %.4f, DEV recall %.4f)' % (A, B, fp, rc))
groups = collections.OrderedDict()
groups['DEV train (neg)'] = neg; groups['DEV pool half 297-299 (pos)'] = pos
groups['HELD val (neg)'] = [r for r in R if r['group'].startswith('val_')]
groups['HELD pool half 301/333-335 (pos)'] = [r for r in R if r['group'] == 'pool_half' and mod(r) not in DEVPOS]
groups['HELD pool full mono (neg)'] = [r for r in R if r['group'] == 'pool_full_mono']
groups['HELD pool full multi (neg)'] = [r for r in R if r['group'] == 'pool_full_multi']
groups['HELD Hanifi half (pos)'] = [r for r in R if r['group'] == 'rf_half']
groups['HELD Hanifi full (neg)'] = [r for r in R if r['group'] == 'rf_full']
groups['TARGET pool half 1,008 (pos)'] = [r for r in R if r['group'] == 'pool_half']
groups['TARGET labelled train+val+test (neg)'] = [r for r in R if r['group'].split('_')[0] in ('train', 'val', 'test')]
for k, v in groups.items():
    h = sum(rule(r, A, B) for r in v); print('%-38s routed half-cut %5d / %5d = %.4f' % (k, h, len(v), h / max(len(v), 1)))
test = [r for r in R if r['group'].startswith('test_')]
print('test (structure only, not scored): routed', [os.path.basename(r['img'])[:-4] for r in test if rule(r, A, B)])
print('train/val routed:', [os.path.basename(r['img'])[:-4] for r in R if r['group'].split('_')[0] in ('train', 'val') and rule(r, A, B)])
print('pool half missed:', [os.path.basename(r['img'])[:-4] for r in groups['TARGET pool half 1,008 (pos)'] if not rule(r, A, B)][:20])
with open(sys.argv[2], 'w') as o:
    o.write('# rule R2b a=%.2f b=%.2f\ngroup\tstem\thalfcut\tFmax\tSmax\n' % (A, B))
    for r in R: o.write(f"{r['group']}\t{os.path.basename(r['img'])[:-4]}\t{rule(r, A, B)}\t{r['_F']:.4f}\t{r['_S']:.4f}\n")
