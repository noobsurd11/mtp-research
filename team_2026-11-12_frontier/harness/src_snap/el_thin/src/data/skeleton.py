"""Ground-truth skeletons for the thin-crack losses (numpy + scipy only; scikit-image is not installed in the training venv).

``skeletonize_2d``: a vectorised numpy port of scikit-image's 2-D ``skeletonize`` (method "zhang",
``skimage.morphology._skeletonize_various_cy._fast_skeletonize``, scikit-image BSD-3-Clause licence; the look-up table
below is copied from it). It is the Zhang-Suen parallel thinning variant that the Skeleton Recall paper uses for 2-D
inputs (Kirchhoff et al., ECCV 2024, Sec. 3.2 and their ref. [42], computed "using libraries such as scikit-image").
Each iteration has two sub-passes over a copy of the image padded with one background pixel; in a sub-pass every
foreground pixel whose 8-neighbourhood code has LUT value 3, or 1 (first sub-pass) or 2 (second sub-pass), is removed
at once; iterate until nothing is removed. Output equals ``skimage.morphology.skeletonize`` exactly (checked on 400
random blobs and all 423 E-SCDD crack masks, scikit-image 0.26; tests/test_thin_crack.py checks toy masks).

``tubed_skeleton``: Skeleton Recall's target (their Algorithm 1) for one class: skeleton of the class mask, dilated with
a diamond of radius 2, multiplied by the class mask (so the tube never leaves the labelled class).
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

# Neighbour code as scikit-image: NW 1, N 2, NE 4, E 8, SE 16, S 32, SW 64, W 128.
# ndi.correlate: out[i, j] = sum_kl W[k, l] * img[i + k - 1, j + l - 1], so W[0, 0] weighs the north-west pixel.
_W = np.array([[1, 2, 4], [128, 0, 8], [64, 32, 16]], dtype=np.int32)

# scikit-image _fast_skeletonize look-up table (BSD-3-Clause, (c) the scikit-image team), verbatim.
_LUT = np.array([0, 0, 0, 1, 0, 0, 1, 3, 0, 0, 3, 1, 1, 0,
                 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0,
                 3, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 2, 0, 0, 0, 3, 0, 2, 2, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0,
                 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0,
                 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0,
                 2, 0, 0, 0, 3, 1, 0, 0, 1, 3, 0, 0, 0, 0,
                 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 1, 3,
                 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 2, 3, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                 0, 0, 3, 3, 0, 1, 0, 0, 0, 0, 2, 2, 0, 0,
                 2, 0, 0, 0], dtype=np.uint8)
assert _LUT.size == 256
_DEL_PASS = ((_LUT == 1) | (_LUT == 3), (_LUT == 2) | (_LUT == 3))  # removable in sub-pass 1, sub-pass 2


def skeletonize_2d(mask: np.ndarray) -> np.ndarray:
    """Skeleton (bool, same shape) of a 2-D binary mask; equals ``skimage.morphology.skeletonize(mask)``."""
    m = np.asarray(mask).astype(bool)
    if m.ndim != 2:
        raise ValueError("skeletonize_2d needs a 2-D mask")
    out = np.zeros(m.shape, bool)
    if not m.any():
        return out
    # Work on the bounding box plus the 1-px background border (pixels outside the box are background and never change,
    # and the code of a pixel only reads its 3x3 neighbourhood, so the result equals the full-image run).
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    img = np.pad(m[y0:y1, x0:x1], 1).astype(np.int32)
    removed = True
    while removed:
        removed = False
        for dele in _DEL_PASS:
            code = ndi.correlate(img, _W, mode="constant", cval=0)
            d = dele[code] & (img == 1)
            if d.any():
                img[d] = 0
                removed = True
    out[y0:y1, x0:x1] = img[1:-1, 1:-1].astype(bool)
    return out


def diamond(radius: int) -> np.ndarray:
    """Diamond (L1 ball) structuring element of the given radius."""
    r = int(radius)
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return (np.abs(y) + np.abs(x)) <= r


def tubed_skeleton(mask: np.ndarray, cls: int = 14, radius: int = 2) -> np.ndarray:
    """Skeleton Recall target for class ``cls``: skeletonize_2d(mask == cls) dilated by diamond(radius), times
    (mask == cls). uint8 {0, 1}, shape of ``mask``. ``radius`` 0 returns the bare skeleton. Ignore pixels (any value
    other than ``cls``) are never in the tube."""
    m = np.asarray(mask) == cls
    if not m.any():
        return np.zeros(m.shape, np.uint8)
    sk = skeletonize_2d(m)
    if radius > 0:
        sk = ndi.binary_dilation(sk, structure=diamond(radius))
    return (sk & m).astype(np.uint8)
