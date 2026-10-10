import json, os, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
SP, LOCAL = sys.argv[1], sys.argv[2]
idx = json.load(open(os.path.join(SP, 'escdd_code', 'index.json')))
sub = {'train': 'train_original', 'val': 'val', 'test': 'test'}
CR, IN = 14, 11
agg = {c: np.zeros(3) for c in ('crack', 'inactive')}  # inter, union, n_img
img_same = []; mask_identical = 0; per_img = []; shapes = set(); newcls = 0; rel = np.zeros(4)
for n in idx['over']:
    ls = idx['local_split'][n]
    m0 = np.array(Image.open(os.path.join(LOCAL, f"masks_coded_{sub[ls]}", n)))
    m1 = np.array(Image.open(os.path.join(SP, 'escdd_data', idx['esc'][n]['masks'][1])))
    i0 = np.array(Image.open(os.path.join(LOCAL, f"images_{sub[ls]}", n)).convert('L')).astype(float)
    i1 = np.array(Image.open(os.path.join(SP, 'escdd_data', idx['esc'][n]['images'][1])).convert('L')).astype(float)
    shapes.add((m0.shape, m1.shape, m1.dtype.str, int(m1.max())))
    if m0.shape != m1.shape: continue
    img_same.append(float(np.abs(i0 - i1).mean()))
    mask_identical += int((m0 == m1).all()); newcls += int((m1 > 23).any())
    row = {'name': n, 'split0': ls, 'split1': idx['esc'][n]['masks'][0], 'pix_agree': float((m0 == m1).mean())}
    for c, k in ((CR, 'crack'), (IN, 'inactive')):
        a, b = m0 == c, m1 == c
        if a.any() or b.any():
            I, U = (a & b).sum(), (a | b).sum(); agg[k] += (I, U, 1)
            row[k] = float(I / U); row[k + '_px'] = (int(a.sum()), int(b.sum()))
    a, b = m0 == CR, m1 == CR
    if a.any() and b.any():  # relaxed 2px agreement
        da, db = ndi.distance_transform_edt(~a), ndi.distance_transform_edt(~b)
        rel += ((db[a] <= 2).sum(), a.sum(), (da[b] <= 2).sum(), b.sum())
    per_img.append(row)
print('shapes', list(shapes)[:5])
print('n compared', len(per_img), 'image mean abs diff: median', np.median(img_same), 'max', np.max(img_same))
print('masks fully identical', mask_identical, ' masks using new classes (>23)', newcls)
for k, (I, U, nimg) in agg.items(): print(k, 'dataset IoU between versions', round(I / U, 3), 'over', int(nimg), 'images')
cr = [r for r in per_img if 'crack' in r]
ch = [r for r in cr if r['crack'] < 0.999]
print('crack images', len(cr), 'with changed crack mask', len(ch))
if ch: print('changed-crack per-image IoU median', np.median([r['crack'] for r in ch]), 'quartiles', np.percentile([r['crack'] for r in ch], [25, 75]))
print('relaxed 2px: recall old->new', round(rel[0] / max(rel[1], 1), 3), 'new->old', round(rel[2] / max(rel[3], 1), 3))
for s in ('train', 'val', 'test'):
    rr = [r for r in cr if r['split0'] == s]; ch_s = [r for r in rr if r['crack'] < 0.999]
    print(s, 'crack imgs', len(rr), 'changed', len(ch_s))
json.dump(per_img, open(os.path.join(SP, 'escdd_code', 'per_img.json'), 'w'))
