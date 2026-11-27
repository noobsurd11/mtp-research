"""dti_hysteresis (T5 arm 1): dual-threshold hysteresis on the crack margin (FR-UNet's DTI, all connected growth).
crack = 8-connected components of {m > t_lo} that hold at least one px with m > t_hi. t_lo = t_hi = t is the global bias
rule with b = -t. Grid and cross-fitting: scripts/bench_dti.py."""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

CRACK = 14
T_HI = (-1.0, -0.5, 0.0, 0.5, 1.0, 2.0)
T_LO = (-6.0, -5.0, -4.0, -3.0, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0)
S8 = np.ones((3, 3), bool)


def grid() -> list[tuple]:
    return [("dti", th, tl) for th in T_HI for tl in T_LO if tl <= th]


def dti_mask(m: np.ndarray, t_hi: float, t_lo: float) -> np.ndarray:
    assert t_lo <= t_hi, (t_lo, t_hi)
    m = np.asarray(m, np.float32)
    low = m > np.float32(t_lo)
    lab, n = ndi.label(low, structure=S8)
    if n == 0:
        return low
    keep = np.unique(lab[(m > np.float32(t_hi)) & low])
    keep = keep[keep > 0]
    return np.isin(lab, keep)


def dti(m: np.ndarray, oth: np.ndarray, t_hi: float, t_lo: float) -> np.ndarray:
    """Class map (spec form): crack where dti_mask, else oth."""
    return np.where(dti_mask(m, t_hi, t_lo), CRACK, oth).astype(np.uint8)
