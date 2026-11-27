"""Exponential Moving Average (EMA) weight update for the teacher network."""

from __future__ import annotations

import torch
import torch.nn as nn


class EMAUpdater:
    """Maintains an EMA copy of a student model's parameters.

    In Mean Teacher SSL the teacher's parameters θ_t are updated each
    training step via:

        θ_t ← α · θ_t + (1 − α) · θ_s

    where θ_s are the student parameters and α is the decay factor.

    Buffer states (BatchNorm running statistics) are also EMA-updated so
    the teacher remains a valid model for inference.

    Args:
        student: The model being trained (source of updates).
        teacher: The EMA model used for generating pseudo-labels.
        alpha:   EMA decay rate (e.g. 0.999).  Higher = slower update.
    """

    def __init__(
        self,
        student: nn.Module,
        teacher: nn.Module,
        alpha: float = 0.999,
    ) -> None:
        self.student = student
        self.teacher = teacher
        self.alpha = alpha
        # Initialise teacher with student weights
        self._copy_params()

    def _copy_params(self) -> None:
        """Hard-copy student parameters to teacher (used at initialisation)."""
        for t_param, s_param in zip(
            self.teacher.parameters(), self.student.parameters()
        ):
            t_param.data.copy_(s_param.data)
        # Also copy buffers (e.g. BatchNorm running mean/var)
        for t_buf, s_buf in zip(
            self.teacher.buffers(), self.student.buffers()
        ):
            t_buf.data.copy_(s_buf.data)

    @torch.no_grad()
    def step(self) -> None:
        """Perform one EMA update step.

        Should be called once per training iteration *after* the student's
        optimiser step.
        """
        for t_param, s_param in zip(
            self.teacher.parameters(), self.student.parameters()
        ):
            t_param.data.mul_(self.alpha).add_(s_param.data, alpha=1.0 - self.alpha)
        for t_buf, s_buf in zip(
            self.teacher.buffers(), self.student.buffers()
        ):
            # Only float buffers (e.g. BatchNorm running mean/var) can be EMA'd.
            # Integer buffers such as `num_batches_tracked` are hard-copied to
            # avoid "Float can't be cast to Long" on the in-place mul.
            if t_buf.dtype.is_floating_point:
                t_buf.data.mul_(self.alpha).add_(s_buf.data, alpha=1.0 - self.alpha)
            else:
                t_buf.data.copy_(s_buf.data)
