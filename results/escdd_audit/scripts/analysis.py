# E-SCDD audit analysis: class stats, crack morphology, module leakage, near-duplicates, label reconciliation.
import os, sys, json, numpy as np, collections as C
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
ESC, OURS, SPL, META = sys.argv[1:5]
inv = json.load(open(os.path.join(META, 'inv_escdd.json'))); X = {x['file']: x for x in json.load(open(os.path.join(META, 'xref.json')))}
CSV = [l.split(',') for l in open(os.path.join(ESC, 'ListOfClassesAndColorCodes_20221008.csv')).read().strip().split('\n')[1:]]
NAME = {int(r[6]): r[1].strip() for r in CSV}
out = {}
def mask(split, f): return np.array(Image.open(os.path.join(ESC, f'el_masks_{split}', f)))
# A/B. class tables per split x kind
tab = C.defaultdict(lambda: np.zeros((2, 32), np.int64))  # [images, pixels]
for r in inv:
    c = np.array(r['counts'][:32]); k = (r['split'], r['kind'])
    tab[k][0] += c > 0; tab[k][1] += c
out['class_table'] = {f'{s}|{k}': {'n': sum(1 for r in inv if r['split'] == s and r['kind'] == k), 'img': v[0].tolist(), 'px': v[1].tolist()} for (s, k), v in tab.items()}
# C. cell type by spacing class (largest spacing class present)
SPC = {1: 'multi', 2: 'mono', 3: 'IBC dogbone', 24: 'mono halfcut', 29: 'multi halfcut'}
def ctype(cnt):
    s = {k: cnt[k] for k in SPC if cnt[k] > 0}
    return SPC[max(s, key=s.get)] if s else 'none'
out['cell_type'] = {f'{s}|{k}': dict(C.Counter(ctype(r['counts']) for r in inv if r['split'] == s and r['kind'] == k)) for s in ('train', 'val', 'test') for k in ('real', 'real_rf', 'synthetic')}
out['cell_type_mixed'] = sum(1 for r in inv if sum(r['counts'][k] > 0 for k in SPC) > 1)
# D. crack morphology per image: px, skeleton px, width = px/skel, 8-conn fragments
def morph(m):
    a = m == 14
    if not a.any(): return None
    sk = skeletonize(a); lab, n = ndi.label(a, structure=np.ones((3, 3)))
    return dict(px=int(a.sum()), skel=int(sk.sum()), frag=int(n))
mor = {}
for r in inv:
    mm = morph(mask(r['split'], r['file']))
    if mm: mor[r['file']] = mm
ours_mor = {}
for s, sub in (('train', 'train_original'), ('val', 'val'), ('test', 'test')):
    for f in os.listdir(os.path.join(OURS, f'masks_coded_{sub}')):
        mm = morph(np.array(Image.open(os.path.join(OURS, f'masks_coded_{sub}', f))))
        if mm: ours_mor[f] = mm
def summ(d):
    if not d: return None
    px = sum(v['px'] for v in d); sk = sum(v['skel'] for v in d)
    return dict(n=len(d), px=px, width_pooled=round(px / sk, 3), width_median=round(float(np.median([v['px'] / v['skel'] for v in d])), 3),
                frag_median=float(np.median([v['frag'] for v in d])), frag_total=sum(v['frag'] for v in d), px_per_img_median=float(np.median([v['px'] for v in d])))
out['crack_morph'] = {k: summ([mor[r['file']] for r in inv if r['kind'] == k and r['file'] in mor]) for k in ('real', 'real_rf', 'synthetic')}
common = [r['file'] for r in inv if r['kind'] == 'real' and X[r['file']].get('r1104') and r['file'] in mor and r['file'] in ours_mor]
out['crack_morph_common577'] = {'escdd_(=20221008)': summ([mor[f] for f in common]), 'ours_20211104': summ([ours_mor[f] for f in common])}
out['crack_morph_by_source'] = {f'{k}|{s}': summ([mor[r['file']] for r in inv if r['kind'] == k and r['source'] == s and r['file'] in mor]) for k in ('real', 'real_rf') for s in ('ARTS', 'CFVS', 'CSIR', 'BMRK', 'SDLE')}
# E. module leakage across escdd splits (real + rf; module = SRC_#####)
mods = C.defaultdict(set)
for r in inv:
    if r['kind'] != 'synthetic': mods[r['module']].add(r['split'])
out['modules'] = {'n': len(mods), 'multi_split': sum(len(v) > 1 for v in mods.values()),
    'test_cells_module_in_train': sum(1 for r in inv if r['split'] == 'test' and r['kind'] != 'synthetic' and 'train' in mods[r['module']]),
    'val_cells_module_in_train': sum(1 for r in inv if r['split'] == 'val' and r['kind'] != 'synthetic' and 'train' in mods[r['module']]),
    'test_modules': len({r['module'] for r in inv if r['split'] == 'test'}), 'shared_val_test_modules': sum(1 for v in mods.values() if {'val', 'test'} <= v)}
# F. near-duplicates: 64x64 z-normalised thumbnails, NCC under 8 dihedral transforms; add our 5 cells absent from escdd
items = [(r['split'], r['file'], os.path.join(ESC, f"el_images_{r['split']}", r['file'])) for r in inv]
for s, sub in (('train', 'train_original'), ('val', 'val'), ('test', 'test')):
    for f in os.listdir(os.path.join(OURS, f'images_{sub}')):
        if not any(it[1] == f for it in items): items.append((f'ours_{s}', f, os.path.join(OURS, f'images_{sub}', f)))
def thumb(p):
    a = np.asarray(Image.open(p).convert('L').resize((64, 64), Image.BILINEAR), np.float32); a = a - a.mean(); return a / (np.linalg.norm(a) + 1e-6)
T = np.stack([thumb(p) for _, _, p in items])
best = np.full((len(items), len(items)), -1.0, np.float32)
A = T.reshape(len(items), -1)
for k in range(4):
    for fl in (False, True):
        B = np.rot90(T, k, axes=(1, 2)); B = B[:, :, ::-1] if fl else B
        best = np.maximum(best, A @ B.reshape(len(items), -1).T)
np.fill_diagonal(best, -1)
iu = np.argwhere(np.triu(best >= 0.95, 1))
pairs = sorted([(float(best[i, j]), items[i][0], items[i][1], items[j][0], items[j][1]) for i, j in iu], reverse=True)
out['near_dups_095'] = pairs
# G. reconcile P3 vs F04: our masks vs escdd (= 20221008) crack IoU on our test/val/train
rec = {}
for s in ('train', 'val', 'test'):
    I = U = Ich = Uch = 0; nch = nimg = 0
    for x in X.values():
        if x['kind'] == 'real' and x.get('r1104') and x['r1104']['split'] == s:
            i, u, a, b = x['r1104']['crack']
            if u: I += i; U += u; nimg += 1
            if u and i < u: Ich += i; Uch += u; nch += 1
    rec[s] = dict(pooled_all=round(I / U, 3), n_crack_imgs=nimg, pooled_changed_only=round(Ich / max(Uch, 1), 3), n_changed=nch)
out['ours_vs_escdd_crack_iou'] = rec
# H. classes 24-29 inside our 577 (what P6 mapped back)
h = C.Counter(); himg = C.Counter()
for x in X.values():
    if x['kind'] == 'real' and x.get('r1104'):
        r = next(r for r in inv if r['file'] == x['file'])
        for c in range(24, 30):
            if r['counts'][c]: h[c] += r['counts'][c]; himg[c] += 1
out['our577_new_classes'] = {NAME[c]: [himg[c], h[c]] for c in sorted(h)}
# I. synthetic masks vs base mask
syn = {}
for r in inv:
    if r['kind'] != 'synthetic': continue
    b = next(q for q in inv if q['file'][:-4] == r['base'] and q['kind'] != 'synthetic')
    ms, mb = mask(r['split'], r['file']), mask(b['split'], b['file'])
    cs, cb = ms == 14, mb == 14
    syn[r['file']] = dict(pix_agree=float((ms == mb).mean()), same=bool((ms == mb).all()), crack_px=int(cs.sum()), base_crack_px=int(cb.sum()),
                          crack_iou_vs_base=float((cs & cb).sum() / max((cs | cb).sum(), 1)), classes=sorted(np.unique(ms).tolist()))
out['synthetic'] = syn
# J. concentration of inactive / crack in escdd test & val (real+rf)
def conc(split, c):
    v = sorted([r['counts'][c] for r in inv if r['split'] == split and r['kind'] != 'synthetic' and r['counts'][c] > 0], reverse=True)
    return dict(cells=len(v), px=sum(v), top3_share=round(sum(v[:3]) / max(sum(v), 1), 3), top1_share=round(v[0] / sum(v), 3) if v else None)
out['concentration'] = {f'{s}|{n}': conc(s, c) for s in ('val', 'test') for c, n in ((11, 'inactive'), (14, 'crack'))}
json.dump(out, open(os.path.join(META, 'analysis.json'), 'w'))
print('done; near-dup pairs', len(pairs))
