#!/usr/bin/env python3
"""judge recompute for idea 10 §1: speck share and local contrast of crack/inactive/scuff components,
Hanifi _rf vs Pratt (20221008, non-_rf) labels in local E-SCDD (crack 14, inactive 11, scuff 25). 8-connected.
Contrast: |mean inside - mean of a 3..8 px dilation ring| (grey, PIL 'L'), components >= 20 px. Independent code."""
import os, re, numpy as np
from PIL import Image
from scipy import ndimage as ndi
E = os.path.expanduser('~/mtp/datasets/escdd_full')
loc = {}
for sp in ('train', 'val', 'test'):
    for f in os.listdir(f'{E}/el_masks_{sp}'):
        loc[f[:-4]] = (f'{E}/el_images_{sp}/{f}', f'{E}/el_masks_{sp}/{f}')
stems = [s for s in loc if not re.match(r'^\d+-', s)]
st = {'rf': [s for s in stems if s.endswith('_rf')], 'pratt': [s for s in stems if not s.endswith('_rf') and not s.startswith(('synth', 'gen'))]}
K = np.ones((3, 3))
for name, ss in st.items():
    ncomp = nspeck = 0; pxsmall = pxall = 0; per = []; con = {14: [], 11: [], 25: []}
    for s in ss:
        ip, mp = loc[s]
        if not os.path.exists(ip): continue
        m = np.array(Image.open(mp)); im = np.asarray(Image.open(ip).convert('L'), float)
        g = m == 14
        if g.any():
            lab, n = ndi.label(g, K); sz = np.bincount(lab.ravel())[1:]
            ncomp += n; nspeck += (sz < 5).sum(); pxsmall += sz[sz < 20].sum(); pxall += sz.sum(); per.append(n)
        for c in con:
            lab, n = ndi.label(m == c, K)
            for i, sl in enumerate(ndi.find_objects(lab), 1):
                comp = lab == i
                if comp.sum() < 20: continue
                ring = ndi.binary_dilation(comp, iterations=8) & ~ndi.binary_dilation(comp, iterations=3) & (m != 7)
                if ring.sum() < 10: continue
                con[c].append(abs(im[comp].mean() - im[ring].mean()))
    print(f'{name:5s} cells {len(ss)} crack cells {len(per)} comps {ncomp} specks<5px {nspeck} ({nspeck/max(ncomp,1):.2f}) '
          f'crack px in comps<20 {pxsmall/max(pxall,1):.3f} comps/cell median {np.median(per):.0f} p90 {np.percentile(per,90):.0f} max {max(per)}')
    print('      |dGL| median (p25), n comps>=20: ' + '; '.join(f'{ {14:"crack",11:"inactive",25:"scuff"}[c]} {np.median(v):.1f} ({np.percentile(v,25):.1f}) n={len(v)}' for c, v in con.items() if v))
