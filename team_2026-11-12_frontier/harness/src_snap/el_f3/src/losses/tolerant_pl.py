"""Rarity-routed, offset-tolerant pseudo-label loss (P7 arm C; the minimal version of the proposed method).

Motivation (P5, measured on our checkpoints): teacher pseudo-labels for crack land on the right crack but miss the
exact pixels (strict precision 0.27 in the doubly-unsure region, 0.64 within 2 px; 0.59 vs 0.96 at confidence
>= 0.95). A pixel-exact pseudo-label throws that signal away, and a confidence threshold keeps only 8% of crack.

Routing per unlabelled pixel, from the teacher's softmax (weak view):
  * rare-class target (teacher argmax in ``rare_classes``, confident or not): tolerant term
    ``-p_t[r] * log(maxpool_{(2R+1)^2}(p_s[r]))``, i.e. the student is credited for predicting class r anywhere
    within R px of the teacher's pixel. It is weighted by the teacher's probability of r, so unsure targets count less;
  * confident (max-prob >= ``t_pos``) head-class pixel outside an R-px band around rare targets: plain CE to the
    teacher's argmax (FixMatch);
  * everything else: no loss. The band is a "don't care" zone, so confident background next to a teacher crack
    does not punish a student crack that is 1–2 px off.
The sum is divided by the number of unlabelled pixels (FixMatch normalisation, as ``ConfidenceCELoss``).
Teacher logits are detached.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class TolerantPLLoss(nn.Module):
    def __init__(self, t_pos: float = 0.95, rare_classes: tuple[int, ...] = (14, 11), radius: int = 2) -> None:
        super().__init__()
        self.t_pos = float(t_pos)
        self.rare_classes = tuple(int(c) for c in rare_classes)
        self.radius = int(radius)
        self.last_mask_fraction = float("nan")
        self.last_class_counts: torch.Tensor | None = None
        self.last_num_pixels = 0
        self.last_rare_fraction = float("nan")

    def _dilate(self, m: torch.Tensor) -> torch.Tensor:
        k = 2 * self.radius + 1
        return F.max_pool2d(m.float().unsqueeze(1), k, stride=1, padding=self.radius).squeeze(1) > 0

    def forward(self, student_logits: torch.Tensor, teacher_logits: torch.Tensor) -> torch.Tensor:
        s = student_logits.float()
        with torch.no_grad():
            p = torch.softmax(teacher_logits.detach().float(), dim=1)
            conf, label = p.max(dim=1)
            rare_any = torch.zeros_like(conf, dtype=torch.bool)
            for r in self.rare_classes:
                rare_any |= label == r
            band = self._dilate(rare_any) if self.radius > 0 else rare_any
            hard = (conf >= self.t_pos) & ~band
            self.last_mask_fraction = float(hard.float().mean())
            self.last_rare_fraction = float(rare_any.float().mean())
            used = torch.where(hard | rare_any, label, torch.full_like(label, -1))
            self.last_class_counts = torch.bincount(used[used >= 0], minlength=p.shape[1])
            self.last_num_pixels = conf.numel()
        n = conf.numel()
        ce = F.cross_entropy(s, label, reduction="none")
        loss = (ce * hard.float()).sum()
        if rare_any.any():
            ps = torch.softmax(s, dim=1)
            k = 2 * self.radius + 1
            for r in self.rare_classes:
                tgt = label == r
                if not tgt.any():
                    continue
                pr = ps[:, r : r + 1]
                pm = F.max_pool2d(pr, k, stride=1, padding=self.radius).squeeze(1) if self.radius > 0 else pr.squeeze(1)
                w = p[:, r] * tgt.float()
                loss = loss + (-torch.log(pm.clamp_min(1e-6)) * w).sum()
        return loss / n
