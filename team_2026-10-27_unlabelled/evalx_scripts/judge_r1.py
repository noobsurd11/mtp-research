"""evalx, answers to judge round 1 (items 2 and 5) and ideas Q1.
(2) E1 crack cells by {scuff >= 500 px, half-cut (E-SCDD class 29)}: share of GT crack px within 3 px of scuff px,
    crack width (px / skeleton px), darkness of GT crack px vs a 3-8 px ring around the crack, FINAL recall.
    References: our 50 test cells and our train CSIR cells (E-SCDD masks), same width and darkness measures.
(5) twin pair ARTS_00081_r5_c1 (train) / ARTS_00020_r5_c1 (test): crack IoU on old (20211104) and E-SCDD masks."""
import json, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
E = '/home/yugma/mtp/datasets/escdd_full/'
B8 = '/home/yugma/mtp/datasets/BenchmarkEL_releases/dataset_20221008/'
OLD = '/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104/'
SPL = '/home/yugma/mtp/datasets/splits_benchmark/'
fin = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))['ext']['final_b0.75']


def find(stem, kind):
    for root in [E + f'el_{kind}_', B8 + f'el_{kind}_']:
        for sp in ['train', 'val', 'test']:
            f = f'{root}{sp}/{stem}.png'
            if os.path.exists(f):
                return f
    return None


def feats(stem):
    m = np.array(Image.open(find(stem, 'masks')))
    im = np.array(Image.open(find(stem, 'images')).convert('L')).astype(float)
    g = m == 14
    if g.sum() == 0:
        return None
    sc = m == 25
    d_sc = ndi.distance_transform_edt(~sc) if sc.any() else np.full(g.shape, np.inf)
    sk = skeletonize(g)
    dg = ndi.distance_transform_edt(~g)
    ring = (dg >= 3) & (dg <= 8) & (m != 7) & (m != 25)
    return dict(px=int(g.sum()), near_sc=int((d_sc[g] <= 3).sum()), sk=int(sk.sum()), scuff=int(sc.sum()),
                halfcut=bool((m == 29).any()), crack_grey=im[g].mean(), ring_grey=im[ring].mean() if ring.any() else np.nan)


groups = {}
for s in fin:
    C = np.array(fin[s]['conf']).reshape(24, 24)
    if C[14].sum() < 20:
        continue
    f = feats(s)
    if f is None:
        continue
    key = ('scuff' if f['scuff'] >= 500 else 'no-scuff') + '+' + ('halfcut' if f['halfcut'] else 'not-halfcut')
    f['tp'] = C[14, 14]; f['gt'] = C[14].sum()
    groups.setdefault(key, []).append(f)


def summ(name, L):
    px = sum(x['px'] for x in L)
    w = px / max(sum(x['sk'] for x in L), 1)
    near = sum(x['near_sc'] for x in L) / px
    dark = np.nanmean([x['ring_grey'] - x['crack_grey'] for x in L])
    rec = sum(x.get('tp', 0) for x in L) / max(sum(x.get('gt', 0) for x in L), 1) if 'tp' in L[0] else np.nan
    print(f'{name}: cells {len(L)}, crack px {px}, share within 3 px of scuff {near:.3f}, width {w:.2f} px, '
          f'ring - crack grey {dark:.1f}, FINAL recall {rec:.3f}')


print('# (2) E1 crack cells (GT crack >= 20 px), E-SCDD masks; scuff = class 25 >= 500 px; halfcut = class 29 present')
for k in sorted(groups):
    summ('E1 ' + k, groups[k])
summ('E1 all', [x for L in groups.values() for x in L])
for name, lst in [('test (ours, 50)', 'test.txt'), ('train CSIR (ours)', 'train.txt')]:
    stems = [l.strip() for l in open(SPL + lst) if l.strip()]
    if 'CSIR' in name:
        stems = [s for s in stems if s.startswith('CSIR')]
    L = [f for f in (feats(s) for s in stems if find(s, 'masks')) if f]
    summ(name, L)
    print(f'   {name}: cells with any scuff px {sum(x["scuff"] > 0 for x in L)}, halfcut cells {sum(x["halfcut"] for x in L)}')

print('\n# (5) twin pair crack IoU')
for lab, fa, fb in [('old 20211104 masks', OLD + 'masks_coded_train_original/ARTS_00081_r5_c1.png', OLD + 'masks_coded_test/ARTS_00020_r5_c1.png'),
                    ('E-SCDD masks', find('ARTS_00081_r5_c1', 'masks'), find('ARTS_00020_r5_c1', 'masks'))]:
    a = np.array(Image.open(fa)) == 14; b = np.array(Image.open(fb)) == 14
    print(f'{lab}: px {a.sum()} vs {b.sum()}, IoU {(a & b).sum() / (a | b).sum():.3f}')

print('\n# (2b) distance of GT crack px to nearest scuff px, scuff+halfcut and scuff-only E1 cells')
for k in ['scuff+halfcut', 'scuff+not-halfcut']:
    D_all = []
    for s in fin:
        C = np.array(fin[s]['conf']).reshape(24, 24)
        if C[14].sum() < 20:
            continue
        m = np.array(Image.open(find(s, 'masks')))
        sc = m == 25
        key = ('scuff' if sc.sum() >= 500 else 'no-scuff') + '+' + ('halfcut' if (m == 29).any() else 'not-halfcut')
        if key != k:
            continue
        D_all.append(ndi.distance_transform_edt(~sc)[m == 14])
    D = np.concatenate(D_all)
    print(k, 'share of crack px within', {t: round(float((D <= t).mean()), 3) for t in [1, 3, 5, 10, 20, 40]}, 'median dist', round(float(np.median(D)), 1))
