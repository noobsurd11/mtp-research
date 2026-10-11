# Cross-reference every E-SCDD file with BenchmarkEL 20221008, 20220723, our 20211104, the external pool and ext117.
import os, sys, json, csv, numpy as np
from PIL import Image
ESC, REL, OURS, SPL, EXT, OUT = sys.argv[1:7]
inv = json.load(open(os.path.join(os.path.dirname(OUT), 'inv_escdd.json')))
def load_release(root, img_fmt, msk_fmt, splits):
    d = {}
    for s, sub in splits.items():
        for f in os.listdir(os.path.join(root, img_fmt.format(sub))):
            if f.endswith('.png'): d[f[:-4]] = (s, os.path.join(root, img_fmt.format(sub), f), os.path.join(root, msk_fmt.format(sub), f))
    return d
r1008 = load_release(os.path.join(REL, 'dataset_20221008'), 'el_images_{}', 'el_masks_{}', {'train': 'train', 'val': 'val', 'test': 'test'})
r0723 = load_release(os.path.join(REL, 'dataset_20220723'), 'el_images_{}', 'el_masks_{}', {'train': 'train', 'val': 'val', 'test': 'test'})
r1104 = load_release(OURS, 'images_{}', 'masks_coded_{}', {'train': 'train_original', 'val': 'val', 'test': 'test'})
pool = set(open(os.path.join(SPL, 'external_unlabeled.txt')).read().split())
ext = {r['stem']: r for r in csv.DictReader(open(EXT))}
lab = {p: set(open(os.path.join(SPL, 'seed0', f'labeled_{p}pct.txt')).read().split()) for p in (5, 10, 20, 50)}
g = lambda p: np.array(Image.open(p).convert('L')).astype(np.int16)
m = lambda p: np.array(Image.open(p))
def cmp(a_img, a_msk, b_img, b_msk):
    ia, ib = g(a_img), g(b_img); ma, mb = m(a_msk), m(b_msk)
    o = {'img_mad': float(np.abs(ia - ib).mean()), 'mask_same': bool((ma == mb).all()), 'pix_agree': float((ma == mb).mean())}
    ch = ma != mb
    if ch.any():
        pairs, n = np.unique(np.stack([ma[ch], mb[ch]], 1), axis=0, return_counts=True)
        o['trans'] = {f'{int(p[0])}->{int(p[1])}': int(k) for p, k in zip(pairs, n)}  # a -> b
    for c, k in ((14, 'crack'), (11, 'inactive')):
        A, B = ma == c, mb == c
        o[k] = [int((A & B).sum()), int((A | B).sum()), int(A.sum()), int(B.sum())]
    return o
rows = []
for r in inv:
    e_img = os.path.join(ESC, f"el_images_{r['split']}", r['file']); e_msk = os.path.join(ESC, f"el_masks_{r['split']}", r['file'])
    stem = r['base'] if r['kind'] != 'synthetic' else r['file'][:-4]
    o = {'file': r['file'], 'split': r['split'], 'kind': r['kind'], 'stem': stem,
         'in_pool': stem in pool, 'in_ext117': stem in ext, 'ext_split1008': ext[stem]['split_20221008'] if stem in ext else None}
    if r['kind'] != 'synthetic':
        for name, rel in (('r1008', r1008), ('r0723', r0723), ('r1104', r1104)):
            if stem in rel:
                s, ip, mp = rel[stem]; o[name] = {'split': s, **cmp(ip, mp, e_img, e_msk)}
        o['our_labeled'] = [p for p in (5, 10, 20, 50) if stem in lab[p]]
    rows.append(o)
json.dump(rows, open(OUT, 'w'))
print('rows', len(rows))
# release-side coverage
esc_stems = {r['stem'] for r in rows}
print('20221008 not in escdd:', sorted(set(r1008) - esc_stems))
print('20211104 not in escdd:', sorted(set(r1104) - esc_stems))
print('20220723 not in escdd:', len(set(r0723) - esc_stems), sorted(set(r0723) - esc_stems)[:20])
