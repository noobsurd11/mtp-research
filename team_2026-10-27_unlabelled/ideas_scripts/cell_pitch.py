"""Cell pitch from spacing classes in E-SCDD masks (1 sp multi, 2 sp mono, 3 sp dogbone, 24 sp mono halfcut, 29 sp multi halfcut).
A gap line = a column (row) where >= 25% of non-padding px are spacing; adjacent gap columns merged; pitch = distance
between consecutive gap centres. Also the content extent (non-white) for letterboxed E1. Usage: cell_pitch.py"""
import glob, os, csv, json, numpy as np
from PIL import Image
R = os.path.expanduser('~/mtp/datasets/escdd_full')
SP = [1, 2, 3, 24, 29]
d = json.load(open('/home/yugma/mtp/research/team_2026-10-24_go/trackM/final/final_cells.json'))
ext = set(d['ext']['final_b0.75']); test = set(d['test']['final_b0.75'])
tr = set(l.strip() for l in open(os.path.expanduser('~/mtp/datasets/splits_benchmark/train.txt')))
def gaps(frac):
    idx = np.where(frac >= 0.25)[0]
    if len(idx) == 0: return []
    groups = np.split(idx, np.where(np.diff(idx) > 3)[0] + 1)
    return [g.mean() for g in groups]
res = {}
for mp in glob.glob(R + '/el_masks_*/*.png'):
    st = os.path.basename(mp)[:-4]
    if st[0].isdigit(): continue
    grp = 'E1' if st in ext else 'test' if st in test else 'train' if st in tr else 'rf' if st.endswith('_rf') else None
    if grp is None: continue
    m = np.asarray(Image.open(mp)); hc = bool((m == 29).any())
    src = st.split('_')[0]
    key = (grp, src, 'halfcut' if hc else 'full')
    valid = m != 7
    s = np.isin(m, SP)
    pc = []
    for ax in (0, 1):
        frac = s.sum(ax) / np.maximum(valid.sum(ax), 1)
        g = gaps(frac)
        pc += list(np.diff(g)) if len(g) >= 2 else []
    pc = [p for p in pc if p > 60]
    res.setdefault(key, []).append((np.median(pc) if pc else np.nan, valid.any(1).sum(), valid.any(0).sum()))
for k in sorted(res):
    a = np.array(res[k], dtype=float)
    print('%-28s n %3d  cells with a pitch %3d  median pitch %.0f px  (p25 %.0f, p75 %.0f)  non-padding extent h %.0f w %.0f' %
          (str(k), len(a), np.isfinite(a[:, 0]).sum(), np.nanmedian(a[:, 0]), np.nanpercentile(a[:, 0], 25), np.nanpercentile(a[:, 0], 75), np.median(a[:, 1]), np.median(a[:, 2])))
