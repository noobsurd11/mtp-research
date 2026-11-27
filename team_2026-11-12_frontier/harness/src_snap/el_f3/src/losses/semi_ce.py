"""SemiCE loss for semi-supervised segmentation consistency.

For each class *c* and each spatial position, the teacher's logit for class c
drives a selective binary cross-entropy on the student:

  positive loss: student is penalised for NOT predicting c
                 at positions where teacher_logit[c] > t_pos[c]

  negative loss: student is penalised for predicting c
                 at positions where teacher_logit[c] < −t_neg[c]

Positions that are neither confidently positive nor negative are ignored,
which prevents the student from learning from uncertain teacher predictions.

Thresholds can be supplied either as fixed scalars or as per-class tensors.
Data-driven thresholds are computed in ``class_info.get_semice_thresholds()``.
"""

from __future__ import annotations

from typing import Union

import torch
import torch.nn as nn
import torch.nn.functional as F


class SemiCELoss(nn.Module):
    """Semi-supervised consistency loss using per-class logit thresholds.

    Args:
        t_pos: Positive threshold tensor of shape (C,) or scalar.
               Pixels where teacher_logit[c] > t_pos[c] contribute a
               positive BCE loss.
        t_neg: Negative threshold magnitude of shape (C,) or scalar.
               Pixels where teacher_logit[c] < −t_neg[c] contribute a
               negative BCE loss.
        reduction: ``'mean'`` averages over all contributing pixels and
                   classes; ``'sum'`` sums them.
    """

    def __init__(
        self,
        t_pos: Union[torch.Tensor, float] = 0.5,
        t_neg: Union[torch.Tensor, float] = 0.5,
        reduction: str = "mean",
    ) -> None:
        super().__init__()
        if isinstance(t_pos, (int, float)):
            t_pos = torch.tensor(float(t_pos))
        if isinstance(t_neg, (int, float)):
            t_neg = torch.tensor(float(t_neg))
        self.register_buffer("t_pos", t_pos)
        self.register_buffer("t_neg", t_neg)
        self.reduction = reduction

    def forward(
        self,
        student_logits: torch.Tensor,
        teacher_logits: torch.Tensor,
    ) -> torch.Tensor:
        """Compute SemiCE loss.

        Args:
            student_logits: Raw logits from the student network (B, C, H, W).
            teacher_logits: Raw logits from the EMA teacher network (B, C, H, W).
                            The teacher's output is treated as pseudo-labels;
                            its graph is detached internally.

        Returns:
            Scalar loss tensor.
        """
        teacher_logits = teacher_logits.detach()
        B, C, H, W = student_logits.shape

        t_pos = self.t_pos.to(student_logits.device)  # (C,) or scalar
        t_neg = self.t_neg.to(student_logits.device)

        # Broadcast threshold tensors to (1, C, 1, 1) for easy comparison
        if t_pos.ndim == 1:
            t_pos = t_pos.view(1, C, 1, 1)
        if t_neg.ndim == 1:
            t_neg = t_neg.view(1, C, 1, 1)

        pos_mask = teacher_logits > t_pos          # (B, C, H, W) bool
        neg_mask = teacher_logits < -t_neg         # (B, C, H, W) bool

        # Binary targets: 1.0 for positive pixels, 0.0 for negative pixels
        pos_targets = torch.ones_like(student_logits)
        neg_targets = torch.zeros_like(student_logits)

        # BCE loss per element (no reduction)
        bce_all = F.binary_cross_entropy_with_logits(
            student_logits, pos_targets, reduction="none"
        )  # cost of predicting the class
        bce_neg = F.binary_cross_entropy_with_logits(
            student_logits, neg_targets, reduction="none"
        )  # cost of NOT predicting the class

        # Select losses by mask
        loss_pos = bce_all * pos_mask.float()
        loss_neg = bce_neg * neg_mask.float()

        total = loss_pos + loss_neg
        n_active = (pos_mask | neg_mask).float().sum().clamp(min=1.0)

        if self.reduction == "mean":
            return total.sum() / n_active
        return total.sum()

    def update_thresholds(
        self,
        t_pos: torch.Tensor,
        t_neg: torch.Tensor,
    ) -> None:
        """Replace stored thresholds (e.g. after recomputing from data).

        Args:
            t_pos: New positive thresholds (C,).
            t_neg: New negative threshold magnitudes (C,).
        """
        self.t_pos = t_pos.to(self.t_pos.device)
        self.t_neg = t_neg.to(self.t_neg.device)
