"""Confidence-thresholded pseudo-label CE (the PV-S3 SemiCE as specified for this repo).

For every unlabelled pixel the teacher's softmax gives a confidence (max
probability) and a pseudo-label (argmax).  Where the confidence is at least
``t_pos`` the student gets cross-entropy towards the pseudo-label; elsewhere
nothing.  ``t_neg = 0`` switches the negative term off (the only setting
implemented).

Normalisation: the masked sum is divided by the number of unlabelled pixels
(all of them, confident or not), as in FixMatch; the term therefore shrinks
when few pixels are confident.  The teacher logits are detached.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConfidenceCELoss(nn.Module):
    def __init__(self, t_pos: float = 0.6, t_neg: float = 0.0, exclude_classes: tuple = ()) -> None:
        super().__init__()
        # SK2 switch (opt-in; empty keeps the old loss bit for bit): confident pixels whose pseudo-label is in
        # ``exclude_classes`` get no loss. ``last_mask_fraction`` stays the share passing t_pos (comparable with older
        # runs); ``last_used_fraction`` is the share actually used; class counts stay pre-exclusion.
        self.exclude_classes = tuple(int(c) for c in exclude_classes)
        self.last_used_fraction = float("nan")
        if t_neg != 0:
            raise NotImplementedError("only t_neg = 0 (negative term off) is implemented")
        self.t_pos = float(t_pos)
        self.last_mask_fraction = float("nan")
        self.last_class_counts: torch.Tensor | None = None
        self.last_num_pixels = 0

    def forward(self, student_logits: torch.Tensor, teacher_logits: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            p = torch.softmax(teacher_logits.detach().float(), dim=1)
            conf, label = p.max(dim=1)
            mask = (conf >= self.t_pos).float()
            self.last_mask_fraction = float(mask.mean())
            # per-class counts of the pseudo-labels actually used (stays on the device; read every N steps)
            self.last_class_counts = torch.bincount(label[mask.bool()], minlength=p.shape[1])
            self.last_num_pixels = mask.numel()
            if self.exclude_classes:
                for c in self.exclude_classes:
                    mask = mask * (label != c).float()
                self.last_used_fraction = float(mask.mean())
        ce = F.cross_entropy(student_logits.float(), label, reduction="none")
        return (ce * mask).sum() / mask.numel()
