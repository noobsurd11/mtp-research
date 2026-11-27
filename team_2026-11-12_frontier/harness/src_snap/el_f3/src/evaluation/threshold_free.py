"""Threshold-free scoring of a run's final weights: pixel-level average precision, plus argmax IoU / P / R.

One forward pass per image list (no augmentation: the eval transform, resize + normalise; bf16 autocast on
the GPU as in the trainer's test path).  Per image it keeps

* the 24 x 24 argmax confusion matrix, and
* for each scored class, histograms of its softmax probability over ``BINS`` equal bins on [0, 1]
  (bin ``floor(p * BINS)``, p = 1 in the last bin), separately for pixels whose ground truth is the class
  (positives) and is not (negatives),

so any image subset (val, test, val + test, labelled / unlabelled train) is scored by summing.

Average precision (``binned_ap``) is the step-wise area under the PR curve with one threshold per bin
edge: AP = sum_k (R_k - R_{k+1}) P_k, with P_k, R_k the precision and recall of "p >= k / BINS".  This is
sklearn's ``average_precision_score`` applied to the probabilities quantised to their bin
(``tests/test_threshold_free.py``).
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from ..data.augmentations import get_weak_augmentation
from ..data.benchmark_el import BenchmarkELDataset
from ..data.class_info import CRACK_CLASS, INACTIVE_CLASS, NUM_CLASSES

BINS = 1000
SCORED = {"crack": CRACK_CLASS, "inactive": INACTIVE_CLASS}


def binned_ap(pos: np.ndarray, neg: np.ndarray) -> float:
    """AP from per-bin positive / negative counts (bin 0 = lowest probability).  NaN without positives."""
    pos, neg = np.asarray(pos, np.float64), np.asarray(neg, np.float64)
    n_pos = pos.sum()
    if n_pos == 0:
        return float("nan")
    tp, fp = np.cumsum(pos[::-1]), np.cumsum(neg[::-1])   # thresholds from the top bin down
    recall = tp / n_pos
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
    d_recall = np.diff(np.concatenate([[0.0], recall]))
    return float((d_recall * precision).sum())


def prf_iou(conf: np.ndarray, c: int) -> dict:
    """Precision, recall, IoU of class ``c`` from a (C, C) [gt, pred] confusion matrix (NaN where undefined)."""
    conf = np.asarray(conf, np.float64)
    tp, pred, gt = conf[c, c], conf[:, c].sum(), conf[c, :].sum()
    nan = float("nan")
    return {"precision": tp / pred if pred else nan, "recall": tp / gt if gt else nan,
            "iou": tp / (pred + gt - tp) if gt else nan, "gt_pixels": int(gt), "pred_pixels": int(pred)}


def eval_loader(cfg: dict, stems: list[str], root: Path, batch_size: int = 8, num_workers: int = 8) -> DataLoader:
    """BenchmarkEL loader over ``stems`` with the evaluation transform (no augmentation), in the given order."""
    d = cfg["data"]
    ds = BenchmarkELDataset(root / "labeled" / "images", root / "labeled" / "masks_coded", stems,
                            get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    return DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)


@torch.no_grad()
def score_images(model: torch.nn.Module, loader: DataLoader, device: torch.device, amp: bool,
                 amp_dtype: torch.dtype) -> dict[str, np.ndarray]:
    """Per image: ``conf`` (N, C, C) argmax confusion, ``hist`` (N, len(SCORED), 2, BINS) [neg, pos] probability histograms."""
    model.eval()
    confs, hists = [], []
    C, K = NUM_CLASSES, len(SCORED)
    for batch in loader:
        x = batch["image"].to(device, non_blocking=True)
        gt = batch["mask"].to(device, non_blocking=True).long()
        with torch.autocast(device_type=device.type, dtype=amp_dtype, enabled=amp):
            logits = model(x)
        logits = logits.float()
        B = gt.shape[0]
        img = torch.arange(B, device=device)[:, None, None].expand_as(gt)
        pred = logits.argmax(1)
        confs.append(torch.bincount((img * C * C + gt * C + pred).flatten(), minlength=B * C * C).view(B, C, C).cpu())
        prob = torch.softmax(logits, dim=1)
        h = []
        for c in SCORED.values():
            b = (prob[:, c] * BINS).long().clamp_(0, BINS - 1)
            key = (img * 2 + (gt == c).long()) * BINS + b
            h.append(torch.bincount(key.flatten(), minlength=B * 2 * BINS).view(B, 2, BINS))
        hists.append(torch.stack(h, 1).cpu())
    return {"conf": torch.cat(confs).numpy(), "hist": torch.cat(hists).numpy()}


def summarise(conf: np.ndarray, hist: np.ndarray) -> dict:
    """Crack / inactive AP, IoU, P, R from summed per-image arrays (``conf`` (C, C), ``hist`` (K, 2, BINS))."""
    out = {}
    for k, (name, c) in enumerate(SCORED.items()):
        out[name] = {"ap": binned_ap(hist[k, 1], hist[k, 0]), **prf_iou(conf, c)}
    ious = [out[n]["iou"] for n in SCORED]
    aps = [out[n]["ap"] for n in SCORED]
    out["defect_miou"] = float(np.nanmean(ious)) if not all(math.isnan(x) for x in ious) else float("nan")
    out["defect_map"] = float(np.nanmean(aps)) if not all(math.isnan(x) for x in aps) else float("nan")
    return out
