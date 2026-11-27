"""Thin-crack losses on the crack class, added on top of the house CE + Dice (thin worktree, opt-in, default off).

* Skeleton Recall (Kirchhoff et al., ECCV 2024; Research MCP doi:10.1007/978-3-031-72980-5_13, arXiv 2404.03010):
  ``L_srec = 1 - (sum p_c * T + s) / (sum T + s)``, the soft recall of the crack probability on the tubed skeleton T of
  the ground truth (``src/data/skeleton.tubed_skeleton``: skeleton, diamond radius 2, times the crack mask), summed
  over the whole batch (nnU-Net ``batch_dice``), s = 1e-5 (their trainer). The paper's Eq. 2 adds it as
  ``L_generic + w * L_srec``; their code default is w = 1 (``nnUNetTrainerSkeletonRecall.weight_srec``).
* soft-clDice (Shit et al., CVPR 2021; Research MCP doi:10.1109/cvpr46437.2021.01629, arXiv 2003.07311):
  ``Tprec = (|S(p) o y| + s) / (|S(p)| + s)``, ``Tsens = (|S(y) o p| + s) / (|S(y)| + s)``,
  ``L_cl = 1 - 2 Tprec Tsens / (Tprec + Tsens)``; S = soft-skeleton (their Alg. 1 / App. G.2: k iterations of 3x3
  min / max pooling), on the foreground (crack) channel only (their Sec. 4.3), s = 1 (their code). Applied here as
  ``L_house + w * L_cl``, the form the Skeleton Recall paper uses for its clDice baseline (their Eq. 2).

``p_c`` is the float32 softmax probability of the crack class, ignore pixels excluded from the prediction and from the
targets; both terms are computed in float32 with autocast disabled. A batch without crack gives L_srec = 0 exactly (empty
tube) and a finite L_cl (the paper's smoothed form then penalises predicted crack-skeleton mass, like the house Dice on an
absent class). With both weights 0 the factory never builds this wrapper, so the house loss object is unchanged.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..data.skeleton import tubed_skeleton


# ---- soft skeleton (clDice paper, App. G.2) ----
def soft_erode(img: torch.Tensor) -> torch.Tensor:
    p1 = -F.max_pool2d(-img, (3, 1), (1, 1), (1, 0))
    p2 = -F.max_pool2d(-img, (1, 3), (1, 1), (0, 1))
    return torch.min(p1, p2)


def soft_dilate(img: torch.Tensor) -> torch.Tensor:
    return F.max_pool2d(img, (3, 3), (1, 1), (1, 1))


def soft_open(img: torch.Tensor) -> torch.Tensor:
    return soft_dilate(soft_erode(img))


def soft_skel(img: torch.Tensor, iters: int) -> torch.Tensor:
    """Soft skeleton of a (B, 1, H, W) map in [0, 1] (clDice Alg. 1)."""
    img1 = soft_open(img)
    skel = F.relu(img - img1)
    for _ in range(int(iters)):
        img = soft_erode(img)
        img1 = soft_open(img)
        delta = F.relu(img - img1)
        skel = skel + F.relu(delta - skel * delta)
    return skel


def soft_cldice_loss(p: torch.Tensor, y: torch.Tensor, iters: int, smooth: float = 1.0) -> torch.Tensor:
    """1 - soft-clDice of probability map ``p`` and binary target ``y`` (both (B, 1, H, W)), sums over the batch."""
    sp, sy = soft_skel(p, iters), soft_skel(y, iters)
    tprec = ((sp * y).sum() + smooth) / (sp.sum() + smooth)
    tsens = ((sy * p).sum() + smooth) / (sy.sum() + smooth)
    return 1.0 - 2.0 * tprec * tsens / (tprec + tsens)


def skeleton_recall_loss(p: torch.Tensor, tube: torch.Tensor, smooth: float = 1e-5) -> torch.Tensor:
    """1 - soft recall of ``p`` on the tubed skeleton ``tube`` (same shape), sums over the batch (Skeleton Recall Eq. 1)."""
    tube = tube.to(p.dtype)
    return 1.0 - ((p * tube).sum() + smooth) / (tube.sum() + smooth)


def tubes_from_targets(targets: torch.Tensor, cls: int, radius: int) -> torch.Tensor:
    """CPU tubed skeletons of a (B, H, W) target batch (used when the batch carries no precomputed ``skel_tube``)."""
    t = targets.detach().cpu().numpy()
    return torch.from_numpy(np.stack([tubed_skeleton(m, cls, radius) for m in t])).to(targets.device)


class ThinCrackLoss(nn.Module):
    """``base(logits, targets) + w_srec * L_srec + w_cl * L_cl`` on class ``crack_class``.

    ``base`` is the house ``CEDiceLoss`` and is called unchanged, so its value is bit-identical to the house loss.
    ``forward(..., tube=...)`` takes the batch's precomputed tubed skeletons (``TubedSkeletonDataset``); without them
    (e.g. the val loss) they are computed on the CPU from ``targets``. ``last_terms`` holds the detached terms of the
    last call for the training log.
    """

    def __init__(self, base: nn.Module, crack_class: int = 14, srec_weight: float = 0.0, srec_radius: int = 2,
                 srec_smooth: float = 1e-5, cldice_weight: float = 0.0, cldice_iters: int = 5,
                 cldice_smooth: float = 1.0) -> None:
        super().__init__()
        if srec_weight < 0 or cldice_weight < 0 or (srec_weight == 0 and cldice_weight == 0):
            raise ValueError("ThinCrackLoss needs a positive srec or cldice weight (both 0 = house loss, no wrapper)")
        self.base = base
        self.crack_class = int(crack_class)
        self.srec_weight, self.srec_radius, self.srec_smooth = float(srec_weight), int(srec_radius), float(srec_smooth)
        self.cldice_weight, self.cldice_iters = float(cldice_weight), int(cldice_iters)
        self.cldice_smooth = float(cldice_smooth)
        self.ignore_index = getattr(base, "ignore_index", 255)
        self.last_terms: dict[str, torch.Tensor] = {}

    # train.py logs ``criterion.weight``; the trainer's absh path reads dice_classes / dice_weight (absh + thin refused).
    @property
    def criterion(self) -> nn.Module:
        return self.base.criterion

    @property
    def weight(self) -> None:
        return None

    @property
    def dice_classes(self) -> tuple[int, ...]:
        return self.base.dice_classes

    @property
    def dice_weight(self) -> float:
        return self.base.dice_weight

    @property
    def needs_tube(self) -> bool:
        return self.srec_weight > 0

    def forward(self, logits: torch.Tensor, targets: torch.Tensor, tube: torch.Tensor | None = None) -> torch.Tensor:
        loss = self.base(logits, targets)
        terms: dict[str, torch.Tensor] = {}
        with torch.autocast(device_type=logits.device.type, enabled=False):  # thin terms in float32
            valid = (targets != self.ignore_index).float()
            p = (torch.softmax(logits.float(), 1)[:, self.crack_class] * valid)[:, None]  # (B, 1, H, W) float32
            if self.srec_weight > 0:
                if tube is None:
                    tube = tubes_from_targets(targets, self.crack_class, self.srec_radius)
                ls = skeleton_recall_loss(p, tube[:, None], self.srec_smooth)
                loss = loss + self.srec_weight * ls
                terms["loss_srec"] = ls.detach()
            if self.cldice_weight > 0:
                y = ((targets == self.crack_class).float() * valid)[:, None]
                lc = soft_cldice_loss(p, y, self.cldice_iters, self.cldice_smooth)
                loss = loss + self.cldice_weight * lc
                terms["loss_cldice"] = lc.detach()
        self.last_terms = terms
        return loss
