"""Weighted cross-entropy loss with configurable per-class weights."""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class WeightedCrossEntropyLoss(nn.Module):
    """Cross-entropy loss with per-class weights and an ignore index.

    Same value as ``nn.CrossEntropyLoss(weight, ignore_index)`` with ``'mean'``
    reduction, i.e. ``sum_i w[y_i] * ce_i / sum_i w[y_i]`` over non-ignored
    pixels, but the reduction is done here.  PyTorch's weighted
    ``nll_loss2d`` forward on CUDA accumulates with atomics and is not
    deterministic; the per-pixel (``reduction='none'``) loss and ``sum`` are.
    The loss is computed in float32 whatever the input dtype.

    Args:
        weight:       Float tensor of shape (num_classes,).  ``None``: all 1.
        ignore_index: Pixels with this label are excluded from the loss.
        reduction:    ``'mean'`` | ``'sum'`` | ``'none'``.
        label_smoothing: Label-smoothing epsilon (applied by ``F.cross_entropy``).
    """

    def __init__(
        self,
        weight: Optional[torch.Tensor] = None,
        ignore_index: int = 255,
        reduction: str = "mean",
        label_smoothing: float = 0.0,
    ) -> None:
        super().__init__()
        if reduction not in ("mean", "sum", "none"):
            raise ValueError(f"unknown reduction {reduction!r}")
        # Kept for introspection (``criterion.weight``); not used in forward.
        self.criterion = nn.CrossEntropyLoss(weight=weight, ignore_index=ignore_index,
                                             reduction=reduction, label_smoothing=label_smoothing)
        self.ignore_index = ignore_index
        self.reduction = reduction
        self.label_smoothing = label_smoothing

    @property
    def weight(self) -> Optional[torch.Tensor]:
        return self.criterion.weight

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """Compute weighted cross-entropy.

        Args:
            logits:  Raw model output of shape (B, C, H, W).
            targets: Ground-truth class indices of shape (B, H, W).

        Returns:
            Scalar loss (or a per-pixel tensor if ``reduction='none'``).
        """
        ce = F.cross_entropy(logits.float(), targets, reduction="none",
                             ignore_index=self.ignore_index, label_smoothing=self.label_smoothing)
        valid = targets != self.ignore_index
        if self.weight is None:
            w = valid.float()
        else:
            w = self.weight.to(ce.device)[torch.where(valid, targets, 0)] * valid
        if self.reduction == "none":
            return ce * w
        if self.reduction == "sum":
            return (ce * w).sum()
        return (ce * w).sum() / w.sum()
