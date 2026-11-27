"""Segmentation metrics: the single implementation used for validation, test,
``scripts/evaluate.py`` and the probes, for every dataset.

One pass accumulates a confusion matrix *per image* (one ``bincount``); every
convention below is computed from it.  Pixels whose ground truth is the
ignore label never enter any count.

Conventions (``compute()["conventions"]``):

* ``standard``: one global confusion matrix over all pixels of all images.
  Per class IoU = TP/(TP+FP+FN), precision = TP/(TP+FP), recall = TP/(TP+FN),
  F1 = 2TP/(2TP+FP+FN).  ``defect_mean`` averages the defect classes,
  ``all_mean`` all classes.
* ``pvs3``: the same, but pixels whose ground truth is background are dropped
  before the confusion matrix is built (the background row is removed).
  Recall per class is therefore identical to ``standard``; precision rises
  because false positives on background pixels no longer count; background
  itself has no ground-truth pixels and is absent.
* ``pratt_median``: IoU per image per class, then the median over images, for
  ``pratt_classes`` (BenchmarkEL: crack, gridline, inactive) and their mean.
  Images where the class is absent from the ground truth are handled by three
  rules: ``A`` exclude the image, ``B`` score 0 (primary), ``C`` score 1 if the
  class is also not predicted there, else 0.

A class with no ground-truth pixels in the evaluated pixels is *absent*: its
global metrics are NaN and it is excluded from every mean (never scored as 0).
A class present but never predicted has precision NaN (0/0) and IoU = F1 = 0.
Means are NaN when none of their classes is present.

Top-level keys (``standard`` convention; the names predate the conventions):
  * ``defect_miou``      headline: mean IoU over ``headline_classes``
                         (BenchmarkEL: crack 14 and inactive 11)
  * ``miou_defects_all`` mean IoU over all defect classes
  * ``miou_all``         mean IoU over all classes
  * ``crack_recall``          plain pixel recall of crack
  * ``crack_recall_relaxed``  a ground-truth crack pixel counts as found if a
    predicted crack pixel lies within ``relax_radius`` px (Euclidean, default 2)
  * ``crack_fpr_image``  image-level crack false positive rate: among images
    with no ground-truth crack pixel, the share with at least
    ``fp_min_pixels`` (default 20) predicted crack pixels
"""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
import torch
import torch.nn.functional as F

from ..data.class_info import (
    CLASS_INFO,
    CRACK_CLASS,
    DEFECT_CLASSES,
    INACTIVE_CLASS,
    NUM_CLASSES,
)

HEADLINE_CLASSES: list[int] = [CRACK_CLASS, INACTIVE_CLASS]
BENCHMARK_PRATT_CLASSES: list[int] = [
    next(c["id"] for c in CLASS_INFO if c["name"] == n) for n in ("crack", "gridline", "inactive")
]
PRATT_RULES = ("A", "B", "C")


def disk_kernel(radius: int) -> torch.Tensor:
    """(1, 1, 2r+1, 2r+1) float kernel of offsets with Euclidean norm <= radius."""
    r = torch.arange(-radius, radius + 1, dtype=torch.float32)
    d2 = r[:, None] ** 2 + r[None, :] ** 2
    return (d2 <= radius ** 2).float()[None, None]


def _nanmean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    values = values[~np.isnan(values)]
    return float(values.mean()) if values.size else float("nan")


def class_metrics(conf: np.ndarray) -> dict[str, np.ndarray]:
    """Per-class IoU / precision / recall / F1 (+ counts) from a (C, C) [gt, pred] confusion matrix."""
    conf = np.asarray(conf, dtype=np.float64)
    tp = np.diag(conf)
    gt = conf.sum(axis=1)
    pred = conf.sum(axis=0)
    fp, fn = pred - tp, gt - tp
    present = gt > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        iou = tp / (tp + fp + fn)
        precision = tp / pred
        recall = tp / gt
        f1 = 2 * tp / (2 * tp + fp + fn)
    for arr in (iou, precision, recall, f1):
        arr[~present] = np.nan
    precision[present & (pred == 0)] = np.nan  # present but never predicted: undefined, not 0
    return {"iou": iou, "precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn, "gt_pixels": gt, "pred_pixels": pred, "present": present}


def convention_summary(conf: np.ndarray, names: Sequence[str], defect_classes: Sequence[int]) -> dict:
    """``{'per_class': {name: {...}}, 'defect_mean': {...}, 'all_mean': {...}}`` for one confusion matrix."""
    m = class_metrics(conf)
    keys = ("iou", "precision", "recall", "f1")
    per_class = {
        n: {**{k: float(m[k][i]) for k in keys},
            "gt_pixels": int(m["gt_pixels"][i]), "pred_pixels": int(m["pred_pixels"][i])}
        for i, n in enumerate(names)
    }
    d = list(defect_classes)
    return {
        "per_class": per_class,
        "defect_mean": {k: _nanmean(m[k][d]) for k in keys},
        "all_mean": {k: _nanmean(m[k]) for k in keys},
        "n_present_classes": int(m["present"].sum()),
    }


def pratt_median(per_image: np.ndarray, classes: Sequence[int], names: Sequence[str]) -> dict:
    """Median over images of the per-image IoU, under rules A / B / C (module docstring).

    Args:
        per_image: (N, C, 3) int array of per-image (TP, FP, FN).
    """
    tp, fp, fn = per_image[..., 0].astype(np.float64), per_image[..., 1], per_image[..., 2]
    gt_present = (tp + fn) > 0
    pred_present = (tp + fp) > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        iou_present = tp / (tp + fp + fn)
    out = {"classes": [names[c] for c in classes]}
    for rule in PRATT_RULES:
        scores = {}
        for c in classes:
            g = gt_present[:, c]
            if rule == "A":
                vals = iou_present[g, c]
            elif rule == "B":
                vals = np.where(g, iou_present[:, c], 0.0)
            else:
                vals = np.where(g, iou_present[:, c], np.where(pred_present[:, c], 0.0, 1.0))
            scores[names[c]] = {"median_iou": float(np.median(vals)) if vals.size else float("nan"),
                                "n_images": int(vals.size)}
        out[rule] = {"per_class": scores,
                     "mean": _nanmean(np.array([scores[names[c]]["median_iou"] for c in classes]))}
    out["n_images"] = int(per_image.shape[0])
    out["n_images_with_class"] = {names[c]: int(gt_present[:, c].sum()) for c in classes}
    return out


class SegmentationMetrics:
    """Online accumulator for all metric conventions.  Defaults describe BenchmarkEL (24 classes).

    Args:
        num_classes:      Total number of classes.
        device:           Device for the accumulators.
        ignore_index:     Ground-truth value excluded from all metrics.
        relax_radius:     Tolerance in pixels for ``crack_recall_relaxed``.
        fp_min_pixels:    Predicted crack pixels needed to flag a crack-free image.
        class_names:      Names used in the per-class tables.
        defect_classes:   Classes averaged by ``defect_mean`` / ``miou_defects_all``.
        headline_classes: Classes averaged by ``defect_miou``.
        crack_class:      Class for the crack-specific metrics (``None``: skipped).
        background_class: Class dropped by the ``pvs3`` convention.
        pratt_classes:    Classes of the ``pratt_median`` mean (``None``: all defect classes).
    """

    def __init__(
        self,
        num_classes: int = NUM_CLASSES,
        device: torch.device | None = None,
        ignore_index: int = 255,
        relax_radius: int = 2,
        fp_min_pixels: int = 20,
        class_names: Sequence[str] | None = None,
        defect_classes: Sequence[int] | None = None,
        headline_classes: Sequence[int] | None = None,
        crack_class: int | None = CRACK_CLASS,
        background_class: int = 0,
        pratt_classes: Sequence[int] | None = None,
    ) -> None:
        benchmark = num_classes == NUM_CLASSES and class_names is None
        self.num_classes = num_classes
        self.device = device or torch.device("cpu")
        self.ignore_index = ignore_index
        self.relax_radius = relax_radius
        self.fp_min_pixels = fp_min_pixels
        self.class_names = list(class_names) if class_names is not None else (
            [c["name"] for c in CLASS_INFO] if benchmark else [str(i) for i in range(num_classes)])
        self.defect_classes = list(defect_classes) if defect_classes is not None else (
            DEFECT_CLASSES if benchmark else [c for c in range(num_classes) if c != background_class])
        self.headline_classes = list(headline_classes) if headline_classes is not None else (
            HEADLINE_CLASSES if benchmark else self.defect_classes)
        self.crack_class = crack_class
        self.background_class = background_class
        self.pratt_classes = list(pratt_classes) if pratt_classes is not None else (
            BENCHMARK_PRATT_CLASSES if benchmark else self.defect_classes)
        self._kernel = disk_kernel(relax_radius).to(self.device)
        self.reset()

    def reset(self) -> None:
        """Clear all accumulated counts."""
        C = self.num_classes
        self.conf = torch.zeros(C, C, dtype=torch.long, device=self.device)
        self._per_image: list[np.ndarray] = []
        self.crack_gt = 0
        self.crack_found_relaxed = 0
        self.crack_free_images = 0
        self.crack_free_flagged = 0

    @torch.no_grad()
    def update(self, preds: torch.Tensor, targets: torch.Tensor) -> None:
        """Accumulate a batch.

        Args:
            preds:   Predicted class indices (B, H, W) or (H, W).
            targets: Ground-truth class indices, same shape as ``preds``.
        """
        if preds.shape != targets.shape:
            raise ValueError(f"shape mismatch: preds {tuple(preds.shape)} vs targets {tuple(targets.shape)}")
        if preds.dim() == 2:
            preds, targets = preds[None], targets[None]
        preds = preds.to(self.device).long()
        targets = targets.to(self.device).long()
        valid = targets != self.ignore_index
        C, B = self.num_classes, preds.shape[0]

        t = targets[valid]
        p = preds[valid]
        if t.numel() and (t.min() < 0 or t.max() >= C):
            raise ValueError("target values outside 0..num_classes-1")
        if p.numel() and (p.min() < 0 or p.max() >= C):
            raise ValueError("prediction values outside 0..num_classes-1")
        img = torch.arange(B, device=self.device)[:, None, None].expand_as(targets)[valid]
        per_img = torch.bincount(img * C * C + t * C + p, minlength=B * C * C).view(B, C, C)
        self.conf += per_img.sum(0)
        tp = per_img.diagonal(dim1=1, dim2=2)
        fp = per_img.sum(1) - tp
        fn = per_img.sum(2) - tp
        self._per_image.append(torch.stack([tp, fp, fn], dim=-1).cpu().numpy())

        if self.crack_class is None:
            return
        cc = self.crack_class
        # Relaxed crack recall: dilate the predicted crack map by a disk.
        gt_crack = (targets == cc) & valid
        pred_crack = (preds == cc).float()[:, None]
        near = F.conv2d(pred_crack, self._kernel, padding=self.relax_radius)[:, 0] > 0
        self.crack_gt += int(gt_crack.sum())
        self.crack_found_relaxed += int((gt_crack & near).sum())

        # Image-level false positives on crack-free images.
        crack_free = gt_crack.flatten(1).sum(1) == 0
        flagged = ((preds == cc) & valid).flatten(1).sum(1) >= self.fp_min_pixels
        self.crack_free_images += int(crack_free.sum())
        self.crack_free_flagged += int((crack_free & flagged).sum())

    def compute(self) -> dict:
        """Return per-class and aggregate metrics (NaN where undefined) for every convention."""
        conf = self.conf.double().cpu().numpy()
        m = class_metrics(conf)
        iou, present = m["iou"], m["present"]
        nan = float("nan")
        cc = self.crack_class

        pvs3_conf = conf.copy()
        pvs3_conf[self.background_class, :] = 0
        per_image = (np.concatenate(self._per_image) if self._per_image
                     else np.zeros((0, self.num_classes, 3), np.int64))
        crack_relaxed = self.crack_found_relaxed / self.crack_gt if self.crack_gt else nan
        return {
            "defect_miou": _nanmean(iou[self.headline_classes]),
            "miou_defects_all": _nanmean(iou[self.defect_classes]),
            "miou_all": _nanmean(iou),
            "crack_iou": float(iou[cc]) if cc is not None else nan,
            "inactive_iou": float(iou[INACTIVE_CLASS]) if self.num_classes == NUM_CLASSES else nan,
            "crack_recall": float(m["recall"][cc]) if cc is not None else nan,
            "crack_recall_relaxed": float(crack_relaxed),
            "crack_fpr_image": (
                self.crack_free_flagged / self.crack_free_images if self.crack_free_images else nan
            ),
            "n_crack_free_images": self.crack_free_images,
            "pixel_accuracy": float(m["tp"].sum() / conf.sum()) if conf.sum() else nan,
            "n_present_classes": int(present.sum()),
            "n_images": int(per_image.shape[0]),
            "per_class_iou": iou.tolist(),
            "per_class_precision": m["precision"].tolist(),
            "per_class_recall": m["recall"].tolist(),
            "per_class_f1": m["f1"].tolist(),
            "per_class_present": present.tolist(),
            "per_class_gt_pixels": m["gt_pixels"].astype(np.int64).tolist(),
            "conventions": {
                "standard": convention_summary(conf, self.class_names, self.defect_classes),
                "pvs3": convention_summary(pvs3_conf, self.class_names, self.defect_classes),
                "pratt_median": pratt_median(per_image, self.pratt_classes, self.class_names),
            },
            "confusion_matrix": conf.astype(np.int64).tolist(),
        }


AGGREGATE_KEYS = [
    "defect_miou",
    "miou_defects_all",
    "miou_all",
    "crack_iou",
    "inactive_iou",
    "crack_recall",
    "crack_recall_relaxed",
    "crack_fpr_image",
    "pixel_accuracy",
]


def scalar_metrics(results: dict) -> dict[str, float]:
    """The scalar (non per-class, non nested) entries of ``compute()``."""
    return {k: v for k, v in results.items() if not isinstance(v, (list, dict))}


def format_table(results: dict, class_names: Sequence[str] | None = None, convention: str = "standard") -> str:
    """Human-readable per-class + aggregate table for one convention.  Absent classes show '-'."""
    def fmt(x: float) -> str:
        return "       -" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:>8.4f}"

    conv = results["conventions"][convention]
    names = list(class_names) if class_names is not None else list(conv["per_class"])
    header = f"{'idx':>3}  {'class':<16}{'IoU':>8}{'Prec':>8}{'Recall':>8}{'F1':>8}{'GT px':>13}"
    rows = [f"[{convention}]", header, "-" * len(header)]
    for i, n in enumerate(names):
        c = conv["per_class"][n]
        rows.append(f"{i:>3}  {n:<16}{fmt(c['iou'])}{fmt(c['precision'])}{fmt(c['recall'])}{fmt(c['f1'])}"
                    f"{c['gt_pixels']:>13,}")
    rows.append("-" * len(header))
    for mean in ("defect_mean", "all_mean"):
        v = conv[mean]
        rows.append(f"{mean:<21}{fmt(v['iou'])}{fmt(v['precision'])}{fmt(v['recall'])}{fmt(v['f1'])}")
    if convention == "standard":
        for k in AGGREGATE_KEYS:
            rows.append(f"{k:<24}{fmt(results[k])}")
        rows.append(f"{'present classes':<24}{results['n_present_classes']:>8}")
    return "\n".join(rows)
