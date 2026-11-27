"""Feature perturbations for the perturbed (auxiliary) decoder pass.

Faithful ports of ``FeatureDropout`` / ``FeatureNoise`` in the ALHVR reference
(``refs/ALHVR/train_ALHVR/code/networks/unet.py``):

* one coin flip per forward call picks dropout or noise for **all** levels;
* dropout: channel-mean attention map, per image threshold
  ``max(attention) * U(0.7, 0.9)`` (one draw per level, shared by the batch),
  features zeroed where attention < threshold;
* noise: ``x + x * n`` with ``n ~ U(-0.3, 0.3)`` of shape (C, H, W), one draw
  per level shared across the batch.

Noise is drawn on the feature's device (the reference draws on CPU and copies);
the distribution is the same.
"""

from __future__ import annotations

import random

import numpy as np
import torch


def feature_dropout(x: torch.Tensor) -> torch.Tensor:
    attention = x.mean(dim=1, keepdim=True)
    max_val = attention.view(x.size(0), -1).max(dim=1, keepdim=True).values
    threshold = (max_val * np.random.uniform(0.7, 0.9)).view(x.size(0), 1, 1, 1)
    drop_mask = (attention < threshold).to(x.dtype)
    return x * drop_mask


def feature_noise(x: torch.Tensor, uniform_range: float = 0.3) -> torch.Tensor:
    noise = (torch.rand(x.shape[1:], device=x.device, dtype=torch.float32) * 2 - 1) * uniform_range
    return x + x * noise.to(x.dtype).unsqueeze(0)


def perturb_features(feats: list[torch.Tensor]) -> tuple[list[torch.Tensor], str]:
    """Perturb every level with the same randomly chosen perturbation."""
    if random.random() > 0.5:
        return [feature_dropout(f) for f in feats], "dropout"
    return [feature_noise(f) for f in feats], "noise"
