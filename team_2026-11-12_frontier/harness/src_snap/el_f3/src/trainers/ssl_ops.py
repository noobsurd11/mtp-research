"""Batch-level operations for the Mean Teacher step (P13 switches; see ``Trainer._ssl_losses_split``).

* ``cutmix_boxes`` / ``mix_with_next``: CutMix on the unlabelled batch (French et al. 2020, BMVC: segmentation
  consistency needs mask-based mixing). Box sampling follows UniMatch (Yang et al. 2023): per image with probability
  ``p`` one axis-aligned box of area fraction U(0.02, 0.4) and aspect ratio U(0.3, 1/0.3), fully inside the image.
  Image ``i`` takes the box from image ``i+1`` (cyclic). The same box is applied to the student's strong view and
  to the teacher's logits, so a pseudo-label always sits on the pixels it was predicted for: pasting copies pixels,
  it never resamples them, which keeps 1-2 px crack targets exact.
* ``frozen_bn_stats``: a context in which train-mode forwards still normalise with batch statistics but leave every
  BatchNorm running mean / var / count exactly as they were.
"""

from __future__ import annotations

import math
from contextlib import contextmanager

import torch
import torch.nn as nn


def cutmix_boxes(n: int, h: int, w: int, p: float, generator: torch.Generator,
                 size_min: float = 0.02, size_max: float = 0.4, ratio: float = 0.3) -> torch.Tensor:
    """``(n, h, w)`` bool masks: one box per image with probability ``p``, else all False (CPU, from ``generator``)."""
    box = torch.zeros(n, h, w, dtype=torch.bool)
    for i in range(n):
        u = torch.rand(4, generator=generator).tolist()
        if u[0] >= p:
            continue
        area = (size_min + (size_max - size_min) * u[1]) * h * w
        r = ratio + (1.0 / ratio - ratio) * u[2]
        bw = min(max(int(math.sqrt(area / r)), 1), w)
        bh = min(max(int(math.sqrt(area * r)), 1), h)
        x = int(torch.randint(0, w - bw + 1, (1,), generator=generator))
        y = int(torch.randint(0, h - bh + 1, (1,), generator=generator))
        box[i, y:y + bh, x:x + bw] = True
    return box


def mix_with_next(x: torch.Tensor, box: torch.Tensor) -> torch.Tensor:
    """``x[i]`` with the pixels of ``box[i]`` taken from ``x[i+1]`` (cyclic); ``x`` is ``(n, c, h, w)``."""
    return torch.where(box.unsqueeze(1), torch.roll(x, shifts=-1, dims=0), x)


@contextmanager
def frozen_bn_stats(model: nn.Module):
    """Restore every BatchNorm running statistic on exit (the forward itself still uses batch statistics)."""
    saved = [(m, m.running_mean.clone(), m.running_var.clone(), m.num_batches_tracked.clone())
             for m in model.modules()
             if isinstance(m, nn.modules.batchnorm._BatchNorm) and m.track_running_stats and m.running_mean is not None]
    try:
        yield
    finally:
        # Rebind instead of copy_: the forward saved the old buffers for backward, and an in-place write would bump
        # their version and break the backward pass.
        for m, rm, rv, nb in saved:
            m.running_mean, m.running_var, m.num_batches_tracked = rm, rv, nb
