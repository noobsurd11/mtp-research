"""Q2 same-physical-cell detection at the module level, and re-annotation agreement of twin cells.

M-series names are M<module>C<cell:3><flags:3>. A physical module imaged twice gets two module IDs with the same
cell indices. For every pair of module IDs that share >= 5 cell indices, compute the per-cell NCC of a refined
descriptor (128 px, band-pass DoG(1, 6), row/column means removed so full-length busbars/edges cancel) and take the
median over shared cells: true re-images score near 1 for all cells, different modules do not.
Named sessions (Bent/Control/Flat ... _C###, raw vs '_output_' versions) are handled the same way with the session
as the module.  Twin cells across splits are counted; for twin pairs the masks are compared after aligning the
images (phase correlation at a common size) -> per-class IoU between two independently annotated copies.

Usage: python -I ucf_twins.py <UCF root> <out dir> <figs dir>
"""

from __future__ import annotations

import collections
import itertools
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import IGNORE, dump, pairs  # noqa: E402

root, od, figs = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
S = 128


def key(n: str) -> tuple[str, int] | None:
    m = re.match(r"^M(\d+)C(\d{3})\d{3}\.(jpg|png)$", n)
    if m:
        return ("M" + m[1] + ("p" if m[3] == "png" else ""), int(m[2]))
    m = re.match(r"^(.+?) TestName_(\d{8}_[\d.]+)(_output_\d+_\d+(_altered)?)?_C(\d+)\.jpg$", n)
    if m:
        return (f"{m[1]}|{m[2]}|{'output' if m[3] else 'raw'}", int(m[5]))
    return None


def refined(p: Path) -> np.ndarray:
    a = np.asarray(Image.open(p).convert("L").resize((S, S), Image.BOX), np.float32)
    b = ndi.gaussian_filter(a, 1) - ndi.gaussian_filter(a, 6)
    b = b - b.mean(0, keepdims=True) - b.mean(1, keepdims=True) + b.mean()
    b -= b.mean()
    return (b / (np.linalg.norm(b) + 1e-6)).ravel().astype(np.float32)


rel = [(s, n, a) for s in ("train", "test") for n, a in pairs(root, s)]
relset = {n for _, n, _ in rel}
extra = sorted(p.name for p in (root / "Test_Images").iterdir() if p.name not in relset)
items = [(s, n, a) for s, n, a in rel] + [("extra", n, None) for n in extra]
path = lambda s, n: (root / "Test_Images" / n) if s == "extra" else (root / "training" / "data" / s / "images" / n)  # noqa: E731
mods = collections.defaultdict(dict)  # module -> cell -> item index
for i, (s, n, a) in enumerate(items):
    k = key(n)
    if k:
        mods[k[0]][k[1]] = i
D = np.stack([refined(path(s, n)) for s, n, _ in items])
np.save(od / "ucf_refined_desc.npy", D)

mnames = sorted(mods)
cellsets = {m: set(mods[m]) for m in mnames}
scores = []
for a, b in itertools.combinations(mnames, 2):
    common = cellsets[a] & cellsets[b]
    if len(common) < 5:
        continue
    ia = [mods[a][c] for c in sorted(common)]
    ib = [mods[b][c] for c in sorted(common)]
    ncc = np.einsum("ij,ij->i", D[ia], D[ib])
    scores.append((a, b, len(common), float(np.median(ncc)), float(np.quantile(ncc, 0.25))))
sc = np.array([s[3] for s in scores])
print("module pairs compared:", len(scores), "median-NCC quantiles", np.quantile(sc, [.5, .9, .99, .999, 1]).round(3))
hist, edges = np.histogram(sc, bins=40, range=(-0.2, 1.0))
print("histogram of module-pair median NCC:")
for h, e in zip(hist, edges):
    if h:
        print(f"  {e:+.2f} {h}")
dump({"module_pairs": scores}, od / "ucf_module_pairs.json")


# ---- pass 2: crack-mask overlap per module pair (cracks are unique fingerprints) ----
mask_of = {}
for i, (s, n, a) in enumerate(items):
    if a is not None:
        m = np.asarray(Image.open(root / "training" / "data" / s / "annotations" / a))
        mask_of[i] = np.asarray(Image.fromarray(((m == 1) * 255).astype(np.uint8)).resize((S, S), Image.BOX)) > 127
pair2 = []
for a, b, n, med, q in scores:
    common = sorted(cellsets[a] & cellsets[b])
    ious, ncc_c = [], []
    for c in common:
        i, j = mods[a][c], mods[b][c]
        if i in mask_of and j in mask_of and (mask_of[i].any() or mask_of[j].any()):
            mi, mj = ndi.binary_dilation(mask_of[i], iterations=2), ndi.binary_dilation(mask_of[j], iterations=2)
            ious.append((mi & mj).sum() / max((mi | mj).sum(), 1))
            ncc_c.append(float(D[i] @ D[j]))
    pair2.append((a, b, n, med, len(ious), float(np.mean(ious)) if ious else None, float(np.median(ncc_c)) if ncc_c else None))
dump({"module_pairs": pair2, "fields": ["a", "b", "n_shared", "median_ncc_all", "n_crack_cells", "mean_crack_iou_dil2", "median_ncc_crack_cells"]},
     od / "ucf_module_pairs.json")
v = np.array([(p[3], p[5]) for p in pair2 if p[5] is not None and p[4] >= 3])
print("pairs with >=3 crack cells:", len(v))
for lo, hi in ((-1, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .6), (.6, .7), (.7, .8), (.8, 1.01)):
    sel = v[(v[:, 0] >= lo) & (v[:, 0] < hi)]
    if len(sel):
        print(f"median NCC [{lo:.1f},{hi:.1f}): n={len(sel):5d}  crack-mask IoU quantiles 50/90/99%: {np.quantile(sel[:, 1], [.5, .9, .99]).round(3)}")
hist, e = np.histogram(v[:, 1], bins=20, range=(0, 1))
print("crack-mask IoU histogram:", list(zip(e[:-1].round(2), hist)))
