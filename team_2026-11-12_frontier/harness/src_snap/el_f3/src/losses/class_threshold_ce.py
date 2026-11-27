"""Confidence CE with per-class thresholds that cap every class's pseudo-label share (PV-S3 v2 classthr).

A pixel of the unlabelled batch is a pseudo-label of class ``c`` (the teacher's argmax) if the
teacher's confidence is at least ``thresholds[c]``.  The thresholds start at ``t_pos`` and are
recomputed by ``update()`` (the trainer calls it every ``logging.pseudo_label_every`` = 500 steps)
from the window's histogram of (argmax class, confidence):

* the raw threshold of class ``c`` is the smallest confidence ``t >= t_pos`` (on a 1/``bins`` grid)
  at which the window's share of unlabelled pixels pseudo-labelled ``c`` is at most
  ``cap`` × the labelled ground-truth pixel share of ``c``; if no ``t <= 1`` achieves it, the class
  gets no pseudo-labels (raw threshold ``DISABLED``);
* ``thresholds <- momentum * thresholds + (1 - momentum) * raw`` (EMA smoothing).

The loss value, its normalisation (masked CE sum / all unlabelled pixels) and the logging
attributes are those of ``ConfidenceCELoss``.  The thresholds (buffer) and the current window's
histogram (extra state) are part of ``state_dict()``, so a resumed run continues exactly.
"""

from __future__ import annotations

from typing import Any, Sequence

import torch
import torch.nn.functional as F

from .confidence_ce import ConfidenceCELoss

DISABLED = 1.01  # above any softmax confidence


class ClassThresholdCELoss(ConfidenceCELoss):
    def __init__(self, gt_share: Sequence[float], t_pos: float = 0.6, cap: float = 2.0, momentum: float = 0.8,
                 bins: int = 1000) -> None:
        super().__init__(t_pos=t_pos)
        share = torch.as_tensor(gt_share, dtype=torch.float64)
        if share.ndim != 1 or (share < 0).any() or abs(float(share.sum()) - 1) > 1e-6:
            raise ValueError("gt_share must be a probability vector over the classes")
        self.register_buffer("thresholds", torch.full((len(share),), float(t_pos), dtype=torch.float32))
        self.gt_share = share
        self.cap, self.momentum, self.bins = float(cap), float(momentum), int(bins)
        self._hist: torch.Tensor | None = None
        self.last_raw: list[float] | None = None

    # window histogram travels with the checkpoint
    def get_extra_state(self) -> Any:
        return {"hist": None if self._hist is None else self._hist.detach().cpu(), "last_raw": self.last_raw}

    def set_extra_state(self, state: Any) -> None:
        self._hist = state["hist"].to(self.thresholds.device) if state["hist"] is not None else None
        self.last_raw = state["last_raw"]

    def forward(self, student_logits: torch.Tensor, teacher_logits: torch.Tensor) -> torch.Tensor:
        C = teacher_logits.shape[1]
        with torch.no_grad():
            p = torch.softmax(teacher_logits.detach().float(), dim=1)
            conf, label = p.max(dim=1)
            mask = (conf >= self.thresholds.to(conf.device)[label]).float()
            self.last_mask_fraction = float(mask.mean())
            self.last_class_counts = torch.bincount(label[mask.bool()], minlength=C)
            self.last_num_pixels = mask.numel()
            b = (conf * self.bins).long().clamp_(0, self.bins - 1)
            h = torch.bincount((label * self.bins + b).flatten(), minlength=C * self.bins)
            self._hist = h if self._hist is None else self._hist + h
        ce = F.cross_entropy(student_logits.float(), label, reduction="none")
        return (ce * mask).sum() / mask.numel()

    @torch.no_grad()
    def update(self) -> list[float] | None:
        """Recompute the thresholds from the window's histogram (see module docstring); returns the raw thresholds."""
        if self._hist is None:
            return None
        C = len(self.gt_share)
        h = self._hist.view(C, self.bins).double().cpu()
        total = float(h.sum())
        above = h.flip(1).cumsum(1).flip(1)                  # above[c, k]: pixels of class c with bin >= k
        edges = torch.arange(self.bins, dtype=torch.float64) / self.bins
        raw = []
        for c in range(C):
            ok = (above[c] <= self.cap * float(self.gt_share[c]) * total) & (edges >= self.t_pos - 1e-12)
            idx = torch.nonzero(ok)
            raw.append(float(edges[idx[0, 0]]) if len(idx) else DISABLED)
        raw_t = torch.tensor(raw, dtype=torch.float32, device=self.thresholds.device)
        self.thresholds.mul_(self.momentum).add_((1 - self.momentum) * raw_t)
        self._hist = None
        self.last_raw = raw
        return raw
