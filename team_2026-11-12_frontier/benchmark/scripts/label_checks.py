#!/usr/bin/env python3
"""benchdesign, 12 Nov 2026. (1) B6 groups split by test-cell evidence; (2) BMRK / SDLE duplicate check at full
resolution; (3) mask agreement between images of the same physical cell; (4) per-class presence tables.
CPU; images and ground-truth masks only. Run: python -I label_checks.py DATASETS_DIR RESEARCH_DIR OUT_DIR"""
import sys, collections, itertools
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
DS, RS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
log = open(f'{OUT}/label_checks_summary.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n')
hdr, *rows = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/groups_all.tsv')]
G = {r[0]: dict(zip(hdr, r)) for r in rows}
hdr2, *rows2 = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/cells.tsv')]
CI = {r[0]: dict(zip(hdr2, r)) for r in rows2}
def paths(stem):
    rel = dict(x.split(':') for x in CI[stem]['releases'].split('|'))
    mv = CI[stem]['maskver']
    if mv == 'escdd': b = f"{DS}/escdd_full"; sp = rel['escdd']
    else: b = f"{DS}/BenchmarkEL_releases/dataset_{mv}"; sp = rel[mv]
    return f'{b}/el_images_{sp}/{stem}.png', f'{b}/el_masks_{sp}/{stem}.png'
def img(stem): return np.asarray(Image.open(paths(stem)[0]).convert('L'), dtype=np.float32)
def msk(stem):
    m = np.array(Image.open(paths(stem)[1]))
    return m[..., 0] if m.ndim == 3 else m

# (1)
b6f = {}
for l in list(open(f'{RS}/team_2026-10-31_next/results/b6/b6_folds.tsv'))[1:]:
    a = l.rstrip('\n').split('\t'); b6f[a[0]] = int(a[3])
P('## 1. Frozen B6 folds vs groups that use test-cell evidence')
bg = collections.defaultdict(list)
for s, k in b6f.items(): bg[G[s]['group']].append((s, k))
for gg, v in bg.items():
    if len({k for _, k in v}) > 1:
        P(f'  group {gg}:')
        for k in sorted({k for _, k in v}):
            vv = [s for s, kk in v if kk == k]
            P(f"    fold {k}: {len(vv)} cells, image ids {sorted({G[s]['module'] for s in vv})}, crack px {sum(int(G[s]['crack_px']) for s in vv)}, inactive px {sum(int(G[s]['inactive_px']) for s in vv)}; {vv}")

# (2) BMRK / SDLE full-resolution check of the top screen pairs
P('\n## 2. BMRK / SDLE pairs: full-resolution image correlation for pairs with screen hp_r >= 0.95 or crack IoU >= 0.2')
pr = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/pairs.tsv')][1:]
fl = lambda x: float(x) if x not in ('nan', '') else float('nan')
def ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))
out = []
for r in pr:
    if not r[1].startswith(('BMRK', 'SDLE')): continue
    if float(r[0]) >= 0.95 or fl(r[6]) >= 0.2 or fl(r[5]) >= 0.2:
        a, b = img(r[1]), img(r[3])
        ma, mb = msk(r[1]), msk(r[3])
        nonpad = (ma != 7) & (mb != 7)
        c_all = ncc(a, b); c_np = ncc(a[nonpad], b[nonpad]) if nonpad.sum() > 100 else float('nan')
        mad = float(np.abs(a - b)[nonpad].mean()) if nonpad.sum() else float('nan')
        out.append((c_np, r[1], r[2], r[3], r[4], float(r[0]), c_all, mad, fl(r[6]), fl(r[5]), float((ma == mb).mean())))
out.sort(key=lambda t: -t[0])
P('  ncc_nonpadding | a (role) | b (role) | screen hp_r | ncc_all | mean abs diff (grey) | crack IoU | inactive IoU | share of identical mask px')
for t in out[:25]:
    P(f'  {t[0]:.4f} | {t[1]} ({t[2]}) | {t[3]} ({t[4]}) | {t[5]:.3f} | {t[6]:.4f} | {t[7]:.1f} | {t[8]:.3f} | {t[9]:.3f} | {t[10]:.4f}')
P(f'  pairs checked {len(out)}; with non-padding ncc >= 0.98: {sum(t[0] >= 0.98 for t in out)}; >= 0.90: {sum(t[0] >= 0.90 for t in out)}')

# (3) same physical cell, two images: mask agreement
P('\n## 3. Mask agreement between two images of the same physical cell (same group, same source and position, different image id)')
def best_shift(a, b, R=8):
    best = (-2, 0, 0)
    A = a[32:-32, 32:-32]
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            B = np.roll(np.roll(b, dy, 0), dx, 1)[32:-32, 32:-32]
            c = ncc(A, B)
            if c > best[0]: best = (c, dy, dx)
    return best
def tol(ma, mb, t=2):
    if ma.sum() == 0 or mb.sum() == 0: return float('nan'), float('nan'), float('nan')
    da = ndi.distance_transform_edt(~ma); db = ndi.distance_transform_edt(~mb)
    p = float((da[mb] <= t).mean()); r = float((db[ma] <= t).mean())
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)
def iou(ma, mb):
    u = (ma | mb).sum(); return float((ma & mb).sum() / u) if u else float('nan')
res = []
seen = set()
for r in pr:
    a, b = r[1], r[3]
    if a.startswith(('BMRK', 'SDLE')): continue
    if G[a]['group'] != G[b]['group']: continue
    ia, ib = img(a), img(b)
    c, dy, dx = best_shift(ia, ib)
    ma, mb = msk(a), msk(b)
    mbs = np.roll(np.roll(mb, dy, 0), dx, 1)
    for cls, name in ((14, 'crack'), (11, 'inactive')):
        A, B = ma == cls, mbs == cls
        if A.sum() < 100 or B.sum() < 100: continue
        i0 = iou(ma == cls, mb == cls); i1 = iou(A, B); p, rr, f1 = tol(A, B)
        res.append((name, a, r[2], b, r[4], c, dy, dx, int(A.sum()), int(B.sum()), i0, i1, f1, min(p, rr)))
P('  class | a (role) | b (role) | image ncc after shift | shift dy,dx | px a | px b | IoU raw | IoU after image alignment | tolerant F1 @2 | min(P, R) @2')
for t in sorted(res):
    P(f'  {t[0]} | {t[1]} ({t[2]}) | {t[3]} ({t[4]}) | {t[5]:.3f} | {t[6]},{t[7]} | {t[8]} | {t[9]} | {t[10]:.3f} | {t[11]:.3f} | {t[12]:.3f} | {t[13]:.3f}')
for name in ('crack', 'inactive'):
    v = [t for t in res if t[0] == name]
    if not v: continue
    io = np.array([t[11] for t in v]); f1 = np.array([t[12] for t in v])
    ncopy = int((io >= 0.999).sum())
    P(f'  {name}: pairs {len(v)}; aligned IoU median {np.median(io):.3f} (IQR {np.percentile(io, 25):.3f}-{np.percentile(io, 75):.3f}); tolerant F1@2 median {np.median(f1):.3f} (IQR {np.percentile(f1, 25):.3f}-{np.percentile(f1, 75):.3f}); pairs with IoU >= 0.999 (copied mask): {ncopy}')
    vv = [t for t in v if t[11] < 0.999 and t[5] >= 0.9]
    if vv:
        io = np.array([t[11] for t in vv]); f1 = np.array([t[12] for t in vv])
        P(f'    without copied masks, image ncc >= 0.9: pairs {len(vv)}; aligned IoU median {np.median(io):.3f} (min {io.min():.3f}, max {io.max():.3f}); tolerant F1@2 median {np.median(f1):.3f} (min {f1.min():.3f}, max {f1.max():.3f})')

# (4) class presence: legacy 24 classes (masks_escdd rebuilt) and extra classes in E-SCDD masks
NAMES = ['bckgnd', 'sp multi', 'sp mono', 'sp dogbone', 'ribbons', 'border', 'text', 'padding', 'clamp', 'busbars', 'crack rbn edge', 'inactive',
         'rings', 'material', 'crack', 'gridline', 'splice', 'dead cell', 'corrosion rbn', 'belt mark', 'edge dark', 'frame edge', 'jbox',
         'meas artifact', 'sp mono halfcut', 'scuff', 'corrosion cell', 'brightening', 'star', 'sp multi halfcut']
leg = np.load(f'{OUT}/legacy_classpx.npy'); ls = [l.rstrip('\n').split('\t') for l in open(f'{OUT}/legacy_stems.txt')]
role = np.array([x[1] for x in ls])
P('\n## 4a. Legacy 24 classes on the 582 cells (masks_escdd rebuilt): cells with the class (px) per split')
P('  id | class | train cells (px) | val cells (px) | test cells (px) | train+val groups with the class')
grp = np.array([G[x[0]]['group'] for x in ls])
for k in range(24):
    s = []
    for sp in ('train', 'val', 'test'):
        m = role == sp; s.append(f'{int((leg[m, k] > 0).sum())} ({int(leg[m, k].sum())})')
    m = (role != 'test') & (leg[:, k] > 0)
    P(f'  {k} | {NAMES[k]} | ' + ' | '.join(s) + f' | {len(set(grp[m]))}')
tv = role != 'test'; te = role == 'test'
P('  classes with ground truth in >= 3 test cells:', [NAMES[k] for k in range(24) if (leg[te, k] > 0).sum() >= 3], 'n =', sum((leg[te, k] > 0).sum() >= 3 for k in range(24)))
P('  classes absent from test:', [NAMES[k] for k in range(24) if (leg[te, k] > 0).sum() == 0])
P('  classes in 1-2 test cells:', [NAMES[k] for k in range(24) if 0 < (leg[te, k] > 0).sum() < 3])
P('  classes with >= 10 train+val groups:', [NAMES[k] for k in range(24) if len(set(grp[(role != "test") & (leg[:, k] > 0)])) >= 10])
P('  classes with < 5 train+val groups:', [(NAMES[k], len(set(grp[(role != "test") & (leg[:, k] > 0)]))) for k in range(24) if len(set(grp[(role != "test") & (leg[:, k] > 0)])) < 5])
allpx = np.load(f'{OUT}/classpx.npy'); stems = [r[0] for r in rows2]; roles = np.array([CI[s]['role'] for s in stems])
P('\n## 4b. All 30 classes on E-SCDD / 20221008 masks: cells with the class (px) per role')
P('  id | class | legacy 582 | E1 106 | ext_in_pool 11 | _rf 117')
for k in range(30):
    s = []
    for rs in (('train', 'val', 'test'), ('E1',), ('ext_in_pool',), ('rf_in_pool', 'rf_not_pool')):
        m = np.isin(roles, rs); s.append(f'{int((allpx[m, k] > 0).sum())} ({int(allpx[m, k].sum())})')
    P(f'  {k} | {NAMES[k]} | ' + ' | '.join(s))
# crack / inactive overlap proxy: crack px within 3 px of inactive
log.close()
