"""Scuff (E-SCDD class 25) checks. (1) In the 4 largest E1 half-cut crack cells: px of class 25 vs 14, and share of the
darkest long structure that is 25. (2) Scuff counts by group: our train/test (E-SCDD masks), _rf (pool modules), E1.
(3) Crack-scuff cross-tab in E1 with FINAL recall. Usage: scuff_check.py"""
import glob, os, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
R = os.path.expanduser('~/mtp/datasets/escdd_full')
d = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))
ext = d['ext']['final_b0.75']; test = set(d['test']['final_b0.75'])
tr = set(l.strip() for l in open(os.path.expanduser('~/mtp/datasets/splits_benchmark/train.txt')))
M = {os.path.basename(p)[:-4]: p for p in glob.glob(R + '/el_masks_*/*.png') if not os.path.basename(p)[0].isdigit()}
def m(st): return np.asarray(Image.open(M[st]))
# (1)
rows = []
for st in ext:
    if st not in M: continue
    a = m(st)
    if (a == 29).any() and (a == 14).sum() >= 20: rows.append((st, int((a == 14).sum()), int((a == 25).sum())))
rows.sort(key=lambda r: -r[1])
print('(1) 4 largest E1 half-cut crack cells: stem, crack px, scuff px, crack px within 3 px of scuff, median dist crack->scuff')
for st, c, s in rows[:4]:
    a = m(st); dist = ndi.distance_transform_edt(a != 25) if s else None
    near = int((dist[a == 14] <= 3).sum()) if s else 0; med = float(np.median(dist[a == 14])) if s else np.nan
    print('   ', st, c, s, near, round(med, 1))
# (2)
grp = {'train': [], 'test': [], 'rf_halfcut': [], 'rf_other': [], 'E1': []}
for st, p in M.items():
    g = 'E1' if st in ext else 'test' if st in test else 'train' if st in tr else None
    if g is None and st.endswith('_rf'):
        g = 'rf_halfcut' if (m(st) == 29).any() else 'rf_other'
    if g is None: continue
    a = m(st); grp[g].append(((a == 25).sum(), (a == 14).sum()))
print('(2) group: cells, cells with scuff >= 500 px, of which crack >= 20 px')
for g, v in grp.items():
    v = np.array(v); s = v[:, 0] >= 500; print('   %-11s %3d  %3d  %3d' % (g, len(v), s.sum(), (s & (v[:, 1] >= 20)).sum()))
