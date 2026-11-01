#!/usr/bin/env python3
"""judge helper: paired cell bootstrap of E1 (ext 106) contrasts from per-cell 24x24 confusions (m0 JSONs).
Usage: e1_boot.py A=<dir>:<glob-prefix> B=<dir>:<glob-prefix> [--group all|scuff_halfcut|other|halfcut|full]
Arm value per resample = mean over seeds of pooled metric over resampled cells. 2000 resamples, seed 0.
Descriptive only: E1 is never for selection."""
import json, sys, glob, numpy as np
NC, CR, IN = 24, 14, 11
CTX = '/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv'
ctx = {l.split('\t')[0]: l.strip().split('\t')[1:] for l in open(CTX)}
args = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a and not a.startswith('--'))
grp = next((a.split('=')[1] for a in sys.argv[1:] if a.startswith('--group=')), 'all')
split = next((a.split('=')[1] for a in sys.argv[1:] if a.startswith('--split=')), 'ext')
def load(spec):
    d, pre = spec.split(':')
    fs = sorted(f for f in glob.glob(f'{d}/{pre}*.json') if '.tau' not in f)
    return fs, [json.load(open(f)) for f in fs]
keep = {'all': lambda s: True, 'scuff_halfcut': lambda s: ctx[s][0] == 'scuff_halfcut', 'other': lambda s: ctx[s][0] == 'other',
        'halfcut': lambda s: ctx[s][2] == 'halfcut=1', 'full': lambda s: ctx[s][2] == 'halfcut=0',
        'halfcut_noscuff': lambda s: ctx[s][2] == 'halfcut=1' and ctx[s][1] == 'scuff=0'}[grp] if split == 'ext' else (lambda s: True)
arms = {}
for name, spec in args.items():
    fs, ds = load(spec)
    cells = sorted(s for s in ds[0]['cells'][split] if keep(s))
    T = np.stack([[np.asarray(d['cells'][split][s]['conf'], float).reshape(NC, NC) for s in cells] for d in ds])  # seeds x cells x 24 x 24
    arms[name] = (cells, T, fs)
names = list(arms)
assert arms[names[0]][0] == arms[names[1]][0]
cells = arms[names[0]][0]; n = len(cells)
def metr(T, idx):
    C = T[:, idx].sum(1)  # seeds x 24 x 24
    tp = C[:, CR, CR]; g = C[:, CR, :].sum(1); p = C[:, :, CR].sum(1)
    tpi = C[:, IN, IN]; gi = C[:, IN, :].sum(1); pi = C[:, :, IN].sum(1)
    with np.errstate(invalid='ignore', divide='ignore'):
        return {'crack_recall': (tp / g).mean(), 'crack_prec': (tp / p).mean(), 'crack_iou': (tp / (g + p - tp)).mean(),
                'inact_iou': (tpi / (gi + pi - tpi)).mean()}
full = np.arange(n)
print(f'split={split} group={grp} cells={n}; ' + '; '.join(f'{k}: {len(arms[k][2])} seeds' for k in names))
base = {k: metr(arms[k][1], full) for k in names}
rng = np.random.default_rng(0)
bs = {m: [] for m in base[names[0]]}
for _ in range(2000):
    idx = rng.integers(0, n, n)
    a, b = metr(arms[names[0]][1], idx), metr(arms[names[1]][1], idx)
    for m in bs: bs[m].append(b[m] - a[m])
for m in bs:
    v = np.array(bs[m]); v = v[np.isfinite(v)]
    print(f'{m:13s} {names[0]} {base[names[0]][m]:.3f} -> {names[1]} {base[names[1]][m]:.3f}  delta {base[names[1]][m]-base[names[0]][m]:+.3f}  95% CI [{np.percentile(v,2.5):+.3f}, {np.percentile(v,97.5):+.3f}]  P(>0) {np.mean(v>0):.2f}')
# leave-top-3-out by GT crack px
gt = arms[names[0]][1][0][:, CR, :].sum(1)
top = set(np.argsort(-gt)[:3]); idx = np.array([i for i in range(n) if i not in top])
a, b = metr(arms[names[0]][1], idx), metr(arms[names[1]][1], idx)
print('leave-top-3-crack-out: ' + ', '.join(f'{m} {b[m]-a[m]:+.3f}' for m in a))
