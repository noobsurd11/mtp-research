"""Run a model over a labelled DataLoader and compute metrics (``metrics.SegmentationMetrics``)."""

from __future__ import annotations

from typing import Any, Callable

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from .metrics import SegmentationMetrics

Rule = Callable[[torch.Tensor], torch.Tensor]  # logits (B, C, H, W) -> class map (B, H, W)


def argmax_rule(logits: torch.Tensor) -> torch.Tensor:
    return logits.argmax(dim=1)


def bg_threshold_rule(threshold: float, background: int = 0) -> Rule:
    """UCF-EL decision rule: background if P(background) >= threshold, else argmax over the other classes."""
    if background != 0:
        raise NotImplementedError("background must be class 0")

    def rule(logits: torch.Tensor) -> torch.Tensor:
        p = torch.softmax(logits.float(), dim=1)
        return torch.where(p[:, 0] >= threshold, 0, p[:, 1:].argmax(dim=1) + 1)
    return rule


@torch.no_grad()
def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    num_classes: int = 24,
    amp: bool = False,
    criterion: nn.Module | None = None,
    amp_dtype: torch.dtype = torch.bfloat16,
    metric_kw: dict[str, Any] | None = None,
    rules: dict[str, Rule] | None = None,
) -> dict[str, Any]:
    """Evaluate ``model`` on ``loader``.

    Without ``rules``: returns ``SegmentationMetrics.compute()`` of the argmax
    prediction (plus ``loss`` if ``criterion`` is given).  With ``rules``
    (name -> logits-to-classes function): one forward pass, and a dict
    ``{name: compute()}``.  ``metric_kw`` configures ``SegmentationMetrics``
    for the dataset (class names, ignore label, defect classes, ...).
    The model is left in eval mode.
    """
    model.eval()
    kw = {"num_classes": num_classes, **(metric_kw or {})}
    named = rules or {"argmax": argmax_rule}
    metrics = {name: SegmentationMetrics(device=device, **kw) for name in named}
    total_loss, n = 0.0, 0
    for batch in loader:
        images = batch["image"].to(device, non_blocking=True)
        masks = batch["mask"].to(device, non_blocking=True)
        with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=amp):
            logits = model(images)
            if criterion is not None:
                total_loss += criterion(logits, masks).item()
                n += 1
        for name, rule in named.items():
            metrics[name].update(rule(logits), masks)
    results = {name: m.compute() for name, m in metrics.items()}
    if criterion is not None:
        for r in results.values():
            r["loss"] = total_loss / max(n, 1)
    return results if rules else results["argmax"]
