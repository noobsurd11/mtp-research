"""elbench x3: 2-D skeleton without scikit-image (gaint has none). Zhang and Suen (1984) two-subiteration thinning,
vectorised in numpy, computed on the bounding box of the mask only. skimage.morphology.skeletonize (method 'zhang') is the
same algorithm through a lookup table; small differences at junctions are possible, so every width or placement number
made with this function is compared only with numbers made with this function (labels and predictions alike).
"""
from __future__ import annotations

import numpy as np


def skeletonize(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask, bool)
    out = np.zeros_like(mask)
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return out
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    img = np.pad(mask[y0:y1, x0:x1].astype(np.uint8), 1)
    while True:
        changed = False
        for step in (0, 1):
            c = img[1:-1, 1:-1]
            p2, p3, p4 = img[:-2, 1:-1], img[:-2, 2:], img[1:-1, 2:]
            p5, p6, p7 = img[2:, 2:], img[2:, 1:-1], img[2:, :-2]
            p8, p9 = img[1:-1, :-2], img[:-2, :-2]
            seq = (p2, p3, p4, p5, p6, p7, p8, p9, p2)
            B = sum(p.astype(np.int16) for p in seq[:8])
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.int16) for i in range(8))
            if step == 0:
                cond = ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                cond = ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            rm = (c == 1) & (B >= 2) & (B <= 6) & (A == 1) & cond
            if rm.any():
                c[rm] = 0
                changed = True
        if not changed:
            break
    out[y0:y1, x0:x1] = img[1:-1, 1:-1].astype(bool)
    return out
