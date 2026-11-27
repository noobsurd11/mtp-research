"""SK1: SKCDF's auxiliary balanced segmentation head (ABSH; Zhang et al., CVPR 2025, Sec. 3.3), adapted to EL cells.

Official code (github.com/yinguanchun/SKCDF @ 12f807d, ``code/train_skcdf.py``): a second head on each decoder whose
loss sees each pixel only with probability p_c by its (pseudo-)label class (``:205``, ``:254-259``, ``:267-276``);
masked pixels get zero gradient. The main heads follow the balanced heads by a parameter EMA every iteration
(``:220-238``). Adaptations for 2-D EL cells (design.md section 4):

* p_c = min(1, N_ref / N_c), N_ref = min over ``ref_classes`` (crack, inactive) of their pixel counts in the labelled
  cells; classes with N_c = 0 get p = 1 (they never occur in a label).  SKCDF uses the min over all classes.
* pixels within ``band_radius`` px (Chebyshev) of a ref-class target are always kept, so a thin crack's width is
  still supervised by its neighbours (``band_radius = 0``: SKCDF's mask).
* CE is summed over kept pixels and divided by all pixels (SKCDF's effective scaling); Dice over kept pixels only.
* Bernoulli draws are a pure function of (seed, stream, step).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import torch
import torch.nn.functional as F

from ..data.stream import mix_seed

STREAM_LAB, STREAM_UNL = 3, 4  # mix_seed streams (CutMix uses 2)


def keep_probs(class_counts: Sequence[int] | np.ndarray, ref_classes: Sequence[int]) -> torch.Tensor:
    """Per-class keep probability p_c = min(1, N_ref / N_c); N_ref = min over ``ref_classes``; p = 1 where N_c = 0."""
    n = torch.as_tensor(np.asarray(class_counts, dtype=np.float64))
    n_ref = min(float(n[c]) for c in ref_classes)
    if n_ref <= 0:
        raise ValueError(f"absh: a reference class {list(ref_classes)} has no labelled pixel: counts {n.tolist()}")
    p = torch.ones_like(n)
    nz = n > 0
    p[nz] = torch.clamp(n_ref / n[nz], max=1.0)
    return p.float()


def annealed(p: torch.Tensor, step: int, total_steps: int) -> torch.Tensor:
    """SKCDF's unlabelled schedule (``:267``): 1 at step 0, linearly to p at ``total_steps``."""
    t = min(max(step / max(total_steps, 1), 0.0), 1.0)
    return 1.0 - t * (1.0 - p)


def band(target: torch.Tensor, ref_classes: Sequence[int], radius: int, valid: torch.Tensor | None = None) -> torch.Tensor:
    """Bool (B, H, W): pixels within ``radius`` px (Chebyshev) of a ref-class pixel of ``target`` (incl. those pixels)."""
    rare = torch.zeros_like(target, dtype=torch.bool)
    for c in ref_classes:
        rare |= target == c
    if valid is not None:
        rare &= valid
    if radius <= 0:
        return rare
    k = 2 * radius + 1
    return F.max_pool2d(rare.float().unsqueeze(1), k, stride=1, padding=radius).squeeze(1) > 0


def balanced_keep(target: torch.Tensor, p: torch.Tensor, ref_classes: Sequence[int], radius: int, seed: int,
                  stream: int, step: int, valid: torch.Tensor | None = None) -> torch.Tensor:
    """Bool keep mask: Bernoulli(p[target]) OR the ref-class band, AND ``valid``."""
    g = torch.Generator(device=target.device).manual_seed(mix_seed(seed, stream, step))
    u = torch.rand(target.shape, generator=g, device=target.device)
    tgt = target.clamp(0, p.numel() - 1)
    keep = u < p.to(target.device)[tgt]
    keep |= band(target, ref_classes, radius, valid)
    if valid is not None:
        keep &= valid
    return keep


def masked_ce_dice(logits: torch.Tensor, target: torch.Tensor, keep: torch.Tensor, dice_classes: Sequence[int],
                   dice_weight: float) -> torch.Tensor:
    """``ce_dice`` restricted to ``keep``: CE summed over kept pixels / all pixels, soft Dice over kept pixels."""
    logits = logits.float()
    kf = keep.float()
    ce = F.cross_entropy(logits, target.clamp(min=0, max=logits.shape[1] - 1), reduction="none")
    ce = (ce * kf).sum() / kf.numel()
    if not dice_classes or dice_weight == 0:
        return ce
    prob = torch.softmax(logits, 1)
    dice = []
    for c in dice_classes:
        pc, yc = prob[:, c] * kf, (target == c).float() * kf
        dice.append(1 - (2 * (pc * yc).sum() + 1) / (pc.sum() + yc.sum() + 1))
    return ce + dice_weight * torch.stack(dice).mean()


def masked_ce(logits: torch.Tensor, target: torch.Tensor, keep: torch.Tensor) -> torch.Tensor:
    """CE to ``target`` summed over ``keep`` / all pixels (as ``confidence_ce``)."""
    ce = F.cross_entropy(logits.float(), target, reduction="none")
    return (ce * keep.float()).sum() / keep.numel()


@torch.no_grad()
def ema_into(dst: torch.nn.Module, src: torch.nn.Module, omega: float) -> None:
    """dst ← ω · dst + (1 − ω) · src, parameters only."""
    dp, sp = list(dst.parameters()), list(src.parameters())
    assert len(dp) == len(sp)
    for a, b in zip(dp, sp):
        a.mul_(omega).add_(b, alpha=1.0 - omega)
