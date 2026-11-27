"""Plain cross-entropy plus batch soft Dice on selected rare classes (P1 arm C; P6 arm L3)."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class CEDiceLoss(nn.Module):
    """``CE + dice_weight * mean_c (1 - soft Dice_c)`` over ``dice_classes``.

    The CE is unweighted and reduced here (per-pixel loss then mean), as in
    ``WeightedCrossEntropyLoss``, so the forward is deterministic on CUDA. The
    soft Dice of class c is ``(2 Σ p_c y_c + 1) / (Σ p_c + Σ y_c + 1)``, summed over the
    whole batch, on float32 softmax probabilities. A class absent from the batch
    then contributes ``1 - 1 / (Σ p_c + 1)``, which pushes its predicted mass down.
    This is the arm C loss of the P1 overfit check.

    Args:
        dice_classes: class ids that get a Dice term (default crack 14, inactive 11).
        dice_weight:  weight of the mean Dice loss.
        ignore_index: pixels with this label are excluded from CE and Dice.
    """

    def __init__(self, dice_classes: tuple[int, ...] = (14, 11), dice_weight: float = 1.0,
                 ignore_index: int = 255) -> None:
        super().__init__()
        self.dice_classes = tuple(int(c) for c in dice_classes)
        self.dice_weight = dice_weight
        self.ignore_index = ignore_index
        # train.py logs ``criterion.weight``; this loss is unweighted.
        self.criterion = nn.CrossEntropyLoss(weight=None, ignore_index=ignore_index)

    @property
    def weight(self) -> None:
        return None

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        logits = logits.float()
        valid = targets != self.ignore_index
        ce = F.cross_entropy(logits, targets, reduction="none", ignore_index=self.ignore_index)
        ce = ce[valid].sum() / valid.sum().clamp(min=1)
        prob = torch.softmax(logits, 1)
        vf = valid.float()
        dice = []
        for c in self.dice_classes:
            p, y = prob[:, c] * vf, (targets == c).float() * vf
            dice.append(1 - (2 * (p * y).sum() + 1) / (p.sum() + y.sum() + 1))
        return ce + self.dice_weight * torch.stack(dice).mean()
