"""Arm 4 pre-check on the 532 cv5v2 pool masks (v1.1): orientation coverage, orientation stability under 1 px label shifts,
FIDT target correlation under 1 px shifts (vs binary IoU)."""
import os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
B = os.path.expanduser("~/mtp/research/team_2026-11-12_frontier/benchmark")
rows = [l.rstrip("\n").split("\t") for l in open(f"{B}/cells.tsv")]; h = rows[0]
pool = [dict(zip(h, r))["stem"] for r in rows[1:] if dict(zip(h, r))["bench_set"].startswith("cv5v2:")]
assert len(pool) == 532
Y, X = np.mgrid[0:512, 0:512].astype(np.float64)
def box7(a): return ndi.uniform_filter(a, 7, mode="constant") * 49
def targets(c):
    sk = skeletonize(c)
    if not sk.any(): return None
    d, (iy, ix) = ndi.distance_transform_edt(~sk, return_indices=True)
    f = 1 / (d ** (0.02 * d + 0.75) + 1); f[d > 20] = 0
    S = sk.astype(np.float64); n = box7(S); n1 = np.maximum(n, 1e-9)
    mx, my = box7(S * X) / n1, box7(S * Y) / n1
    sxx = box7(S * X * X) / n1 - mx ** 2; syy = box7(S * Y * Y) / n1 - my ** 2; sxy = box7(S * X * Y) / n1 - mx * my
    th = np.mod(0.5 * np.arctan2(2 * sxy, sxx - syy), np.pi); b = np.minimum((th / (np.pi / 16)).astype(int), 15)
    vs = sk & (n >= 2.5)
    ori = np.where((d <= 2) & vs[iy, ix], b[iy, ix], 255)
    return f, ori
# convention check
t = np.zeros((512, 512), bool); t[100, 50:200] = True; print("horizontal bin", np.unique(targets(t)[1][100, 60:190]))
t = np.zeros((512, 512), bool); t[50:200, 100] = True; print("vertical bin", np.unique(targets(t)[1][60:190, 100]))
cov_n = cov_d = 0; st_n = st_d = 0; fc = []; ious = []
for s in pool:
    m = np.array(Image.open(f"{B}/out/masks_v11/masks/{s}.png")); c = m == 14
    if c.sum() < 20: continue
    T = targets(c); f0, o0 = T
    cov_n += ((o0 != 255) & c).sum(); cov_d += c.sum()
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        cs = np.roll(c, (dy, dx), (0, 1)); f1, o1 = targets(cs)
        v = (o0 != 255) & (o1 != 255); dd = np.abs(o0[v].astype(int) - o1[v].astype(int)); dd = np.minimum(dd, 16 - dd)
        st_n += (dd <= 1).sum(); st_d += v.sum()
        fc.append(np.corrcoef(f0.ravel(), f1.ravel())[0, 1]); ious.append((c & cs).sum() / (c | cs).sum())
print(f"(1) crack px with valid orientation: {cov_n/cov_d:.3f}")
print(f"(2) orientation within +-1 bin under 1 px shift: {st_n/st_d:.3f}")
print(f"(3) FIDT corr under 1 px shift: median {np.median(fc):.3f} mean {np.mean(fc):.3f}; binary IoU median {np.median(ious):.3f}")
