# For thumbnail candidates (NCC >= 0.97), full-res mean abs diff at the best dihedral transform; duplicates have MAD of a few grey levels.
import os, sys, json, numpy as np
from PIL import Image
ESC, OURS, META = sys.argv[1:4]
P = [p for p in json.load(open(os.path.join(META, 'analysis.json')))['near_dups_095'] if p[0] >= 0.97]
def path(split, f):
    if split.startswith('ours_'):
        s = split[5:]; return os.path.join(OURS, f"images_{'train_original' if s == 'train' else s}", f)
    return os.path.join(ESC, f'el_images_{split}', f)
L = lambda s, f: np.asarray(Image.open(path(s, f)).convert('L'), np.float32)
res = []
for s, sa, fa, sb, fb in P:
    A, B = L(sa, fa), L(sb, fb); best = 1e9
    for k in range(4):
        for fl in (False, True):
            Bt = np.rot90(B, k); Bt = Bt[:, ::-1] if fl else Bt
            best = min(best, float(np.abs(A - Bt).mean()))
    res.append((best, s, sa, fa, sb, fb))
res.sort()
json.dump(res, open(os.path.join(META, 'dups_mad.json'), 'w'))
print('MAD hist', np.histogram([r[0] for r in res], [0, 1, 3, 5, 8, 12, 20, 300])[0])
for r in res[:15]: print(round(r[0], 2), round(r[1], 4), r[2], r[3], r[4], r[5])
