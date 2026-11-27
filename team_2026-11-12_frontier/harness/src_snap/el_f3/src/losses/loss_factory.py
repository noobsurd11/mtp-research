"""Factory that builds loss functions from a config dict."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from .weighted_ce import WeightedCrossEntropyLoss
from .ce_dice import CEDiceLoss
from .semi_ce import SemiCELoss
from .confidence_ce import ConfidenceCELoss
from .tolerant_pl import TolerantPLLoss
from .class_threshold_ce import ClassThresholdCELoss
import numpy as np

from ..data.class_info import get_ce_weights, get_semice_thresholds, pratt_weights


def build_losses(
    cfg: dict[str, Any],
    class_counts: np.ndarray | None,
) -> dict[str, nn.Module]:
    """Construct supervised and (optionally) consistency loss modules.

    Args:
        cfg:         The ``loss`` section of the experiment config.
        class_counts: Per-class pixel counts of the labelled training subset
                      in use (train images only).  Drives the CE weights and
                      the data-driven SemiCE thresholds.

    Returns:
        Dict with keys:
          ``'supervised'``   → WeightedCrossEntropyLoss
          ``'consistency'``  → SemiCELoss  (only when ssl is enabled)
    """
    losses: dict[str, nn.Module] = {}
    sup = cfg.get("supervised", "weighted_ce")
    con = cfg.get("consistency", "semi_ce") or "none"  # None (YAML null) = no consistency loss
    needs_counts = (sup == "weighted_ce" and cfg.get("weight_set", "computed") == "computed") or (
        con == "semi_ce" and cfg.get("threshold_mode", "data_driven") == "data_driven")
    if needs_counts and class_counts is None:
        raise ValueError("these losses need the labelled subset's class pixel counts")
    if class_counts is not None:
        counts = np.asarray(class_counts, dtype=np.float64)
        freq = counts / counts.sum()

    # ---- Supervised loss ----
    if sup == "ce":
        # Plain (unweighted) CE, e.g. UCF-EL with its ignore label 128.
        losses["supervised"] = WeightedCrossEntropyLoss(weight=None, ignore_index=int(cfg.get("ignore_index", 255)))
    elif sup == "ce_dice":
        # Plain CE + batch soft Dice on the rare defect classes (P1 arm C; P6 arm L3).
        losses["supervised"] = CEDiceLoss(dice_classes=tuple(cfg.get("dice_classes", (14, 11))),
                                          dice_weight=float(cfg.get("dice_weight", 1.0)))
    elif sup == "weighted_ce":
        weight_set = cfg.get("weight_set", "computed")
        if weight_set == "computed":
            weights = get_ce_weights(counts, cap_ratio=cfg.get("weight_cap_ratio", 10.0))
        else:
            weights = pratt_weights(weight_set)
        losses["supervised"] = WeightedCrossEntropyLoss(weight=weights)
    else:
        raise ValueError(f"Unknown supervised loss: {cfg['supervised']}")

    # ---- Consistency loss ----
    if con == "none":
        pass
    elif con == "confidence_ce":
        losses["consistency"] = ConfidenceCELoss(t_pos=cfg.get("t_pos", 0.6), t_neg=cfg.get("t_neg", 0.0),
                                                 exclude_classes=tuple(cfg.get("pl_exclude_classes", ())))
    elif con == "tolerant_pl":
        losses["consistency"] = TolerantPLLoss(t_pos=cfg.get("t_pos", 0.95),
                                               rare_classes=tuple(cfg.get("rare_classes", (14, 11))),
                                               radius=int(cfg.get("tolerance_radius", 2)))
    elif con == "class_threshold_ce":
        if class_counts is None:
            raise ValueError("class_threshold_ce needs the labelled subset's class pixel counts")
        losses["consistency"] = ClassThresholdCELoss(
            gt_share=(counts / counts.sum()).tolist(), t_pos=cfg.get("t_pos", 0.6),
            cap=cfg.get("share_cap", 2.0), momentum=cfg.get("thr_momentum", 0.8))
    elif con == "semi_ce":
        mode = cfg.get("threshold_mode", "data_driven")
        if mode == "data_driven":
            beta = cfg.get("beta", 0.5)
            gamma = cfg.get("gamma", 0.5)
            t_pos, t_neg = get_semice_thresholds(freq, beta=beta, gamma=gamma)
        else:
            t_pos = torch.tensor(cfg.get("t_pos_fixed", 0.5))
            t_neg = torch.tensor(cfg.get("t_neg_fixed", 0.5))
        losses["consistency"] = SemiCELoss(t_pos=t_pos, t_neg=t_neg)
    else:
        raise ValueError(f"unknown loss.consistency {con!r} (semi_ce | confidence_ce | class_threshold_ce | none)")

    return losses
