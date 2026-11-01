"""judge recompute of S10 on gaint (run with the el venv, CPU, nice 19, 1 thread). Own code: unpack found's model/sam masks,
GT = el_f3 labeled/masks_escdd class 11; a' recomputed by judge (8-conn components >= 100 px of a); c = a & b.
Pooled inactive IoU over the 239 A50-OOF train cells; paired cell bootstrap (2,000, numpy default_rng(0)) of X - ref."""
import numpy as np, os
from PIL import Image
from scipy import ndimage as ndi
S = '/home/noob/work/found/s10'; E = '/home/noob/work/el_f3/data'
tr = [l.strip() for l in open(f'{E}/splits/train.txt') if l.strip()]
lab = set(l.strip() for l in open(f'{E}/splits/seed0/labeled_50pct.txt') if l.strip())
oof = [s for s in tr if s not in lab]
zm, zs = np.load(f'{S}/model.npz'), np.load(f'{S}/sam.npz')
U = lambda z, s: np.unpackbits(z[s])[:512 * 512].reshape(512, 512).astype(bool)
rows = []
for s in oof:
    g = np.array(Image.open(f'{E}/labeled/masks_escdd/{s}.png')) == 11
    a = U(zm, s); b = U(zs, s)
    lb, n = ndi.label(a, np.ones((3, 3))); sz = np.bincount(lb.ravel()); keep = np.where(sz >= 100)[0]; keep = keep[keep > 0]
    a2 = np.isin(lb, keep); c = a & b
    rows.append([[(x & g).sum(), x.sum(), g.sum()] for x in (a, a2, b, c)])
R = np.array(rows, float)  # cells x 4 x (tp, pred, gt)
def iou(T): return T[..., 0] / np.maximum(T[..., 1] + T[..., 2] - T[..., 0], 1)
P = R.sum(0); I = iou(P); names = ['a', "a'", 'b', 'c']
print('cells', len(oof), 'GT-inactive cells', int((R[:, 0, 2] > 0).sum()), 'GT px', int(P[0, 2]))
print('pooled IoU ' + ' '.join(f'{n} {v:.4f}' for n, v in zip(names, I)) + ' | recall/prec ' + ' '.join(f'{n} {P[i,0]/P[i,2]:.3f}/{P[i,0]/max(P[i,1],1):.3f}' for i, n in enumerate(names)))
ref = 0 if I[0] >= I[1] else 1
rng = np.random.default_rng(0); n = len(oof); D = {2: [], 3: []}
for _ in range(2000):
    idx = rng.integers(0, n, n); Q = iou(R[idx].sum(0))
    for x in (2, 3): D[x].append(Q[x] - Q[ref])
for x in (2, 3):
    d = np.array(D[x]); print(f'{names[x]} - {names[ref]}: {I[x]-I[ref]:+.4f}  95% CI [{np.percentile(d,2.5):+.3f}, {np.percentile(d,97.5):+.3f}]')
nog = R[:, :, 2] == 0
print('FP px on no-GT cells: ' + ' '.join(f'{nm} {int(R[nog[:,0], i, 1].sum())}' for i, nm in enumerate(names)), '| no-GT cells', int(nog[:, 0].sum()))
