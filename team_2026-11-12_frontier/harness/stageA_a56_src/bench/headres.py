"""elbench stage A5: head_res_ceiling (T11 spec section A0 + the wave 3 critic's GT-side fix). CPU only.

Model side: from a dump's float16 logp (24, 512, 512), simulate a stride-s head:
  z = avg_pool2d(logp, s); z_up = bilinear(z, 512, align_corners=False); pred = argmax z_up;
  oth = argmax over the 23 non-crack classes; m_crack = z_up[14] - z_up[oth]; p = softmax(z_up) -> p_crack, p_inact.
  s = 1 is the identity (pred = argmax logp exactly).
GT side (lower bound of the ceiling, critic's fix): crack fraction of the GT mask (ignore px = 0) average-pooled to
stride s, upsampled bilinearly, thresholded at t; the caller sweeps t.
GT side (spec's one-hot ceiling): one-hot GT pooled and upsampled the same way, argmax, ties to the GT class.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from .dumpfmt import CRACK, HW, INACT, NC

STRIDES = (1, 2, 4, 8)
T_GRID = tuple(round(0.05 * i, 2) for i in range(1, 20))      # 0.05 .. 0.95


def pool_up(x: np.ndarray, s: int) -> np.ndarray:
    """(C, H, W) float -> average-pooled to stride s and bilinearly upsampled back, float32. s = 1: float32 copy."""
    x = np.asarray(x, np.float32)
    assert x.ndim == 3 and x.shape[1:] == HW, x.shape
    if s == 1:
        return x.copy()
    assert HW[0] % s == 0 and HW[1] % s == 0, s
    with torch.no_grad():
        t = torch.from_numpy(x)[None]
        z = F.avg_pool2d(t, kernel_size=s, stride=s)
        u = F.interpolate(z, size=HW, mode="bilinear", align_corners=False)
    return u[0].numpy().astype(np.float32, copy=False)


def maps_from_logits(z: np.ndarray) -> dict:
    """Dump maps (dumpfmt keys) from per-class scores z (24, H, W) on a log scale; pred = argmax z."""
    assert z.shape == (NC, *HW), z.shape
    pred = z.argmax(0).astype(np.uint8)
    zo = z.copy()
    zo[CRACK] = -np.inf
    oth = zo.argmax(0)
    m = z[CRACK] - np.take_along_axis(z, oth[None], 0)[0]
    zz = z - z.max(0, keepdims=True)
    e = np.exp(zz)
    p = e / e.sum(0, keepdims=True)
    return {"pred": pred, "oth": oth.astype(np.uint8), "m_crack": m.astype(np.float16),
            "p_crack": np.clip(p[CRACK], 0.0, 1.0).astype(np.float32), "p_inact": np.clip(p[INACT], 0.0, 1.0).astype(np.float16)}


def stride_maps(logp: np.ndarray, s: int) -> dict:
    return maps_from_logits(pool_up(logp, s))


def crack_fraction_up(gt: np.ndarray, keep: np.ndarray | None, s: int) -> np.ndarray:
    """GT crack mask (ignore px counted as non-crack) pooled to stride s and upsampled bilinearly: (H, W) float32."""
    g = (gt == CRACK)
    if keep is not None:
        g = g & keep
    return pool_up(g[None].astype(np.float32), s)[0]


def onehot_ceiling(gt: np.ndarray, s: int) -> np.ndarray:
    """Spec's GT-only ceiling: one-hot GT (classes 0..23; other values all-zero rows) pooled and upsampled, argmax with
    ties to the GT class. Returns a uint8 class map."""
    oh = np.zeros((NC, *HW), np.float32)
    valid = gt < NC
    ys, xs = np.nonzero(valid)
    oh[gt[valid].astype(np.int64), ys, xs] = 1.0
    z = pool_up(oh, s)
    pred = z.argmax(0).astype(np.uint8)
    zmax = z.max(0)
    gz = np.take_along_axis(z, np.where(valid, gt, 0).astype(np.int64)[None], 0)[0]
    tie = valid & (gz >= zmax)
    pred[tie] = gt[tie]
    return pred
