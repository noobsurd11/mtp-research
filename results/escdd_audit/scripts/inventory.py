# Per-file inventory of an E-SCDD copy: name category, formats, mask classes, pixel counts, image stats.
import os, sys, re, json, hashlib, numpy as np
from PIL import Image
ROOT, OUT = sys.argv[1], sys.argv[2]
SYN = re.compile(r'^(\d+)-(.+?)_(bckgnd|crack-rbn-edge-|crack|inactive|rings|material|gridline|splice|dead-cell|corrosion-rbn|belt-mark|edge-dark|meas-artifact|scuff|corrosion-cell|brightening|star|[a-z-]+)_rf$')
def cat(stem):
    m = SYN.match(stem)
    if m: return 'synthetic', m.group(2), m.group(3), int(m.group(1))
    if stem.endswith('_rf'): return 'real_rf', stem[:-3], None, None
    return 'real', stem, None, None
rows = []
for split in ('train', 'val', 'test'):
    for f in sorted(os.listdir(os.path.join(ROOT, f'el_images_{split}'))):
        if not f.endswith('.png'): continue
        stem = f[:-4]; kind, base, cond, idx = cat(stem)
        ip, mp = os.path.join(ROOT, f'el_images_{split}', f), os.path.join(ROOT, f'el_masks_{split}', f)
        im, mk = Image.open(ip), Image.open(mp)
        g = np.array(im.convert('L')); m = np.array(mk)
        alpha = None
        if im.mode in ('RGBA', 'LA'):
            a = np.array(im)[..., -1]; alpha = [int(a.min()), int(a.max())]
        rgb_grey = None
        if im.mode in ('RGB', 'RGBA'):
            a = np.array(im)[..., :3].astype(int); rgb_grey = int(np.abs(a[..., 0] - a[..., 1]).max() + np.abs(a[..., 1] - a[..., 2]).max())
        src = base.split('_')[0]
        mod = '_'.join(base.split('_')[:2])
        cnt = np.bincount(m.ravel() if m.ndim == 2 else m[..., 0].ravel(), minlength=32)
        rows.append(dict(split=split, file=f, kind=kind, base=base, cond=cond, syn_idx=idx, source=src, module=mod,
            img_mode=im.mode, img_size=list(im.size), mask_mode=mk.mode, mask_shape=list(m.shape), mask_dtype=str(m.dtype),
            mask_max=int(m.max()), alpha=alpha, rgb_maxdiff=rgb_grey,
            img_md5=hashlib.md5(g.tobytes()).hexdigest(), mask_md5=hashlib.md5(m.tobytes()).hexdigest(),
            img_mean=float(g.mean()), img_sd=float(g.std()), counts=cnt.tolist()))
json.dump(rows, open(OUT, 'w'))
print('rows', len(rows))
