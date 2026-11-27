"""Visualisation utilities for segmentation predictions on EL images."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from ..data.class_info import CLASS_COLORS, NUM_CLASSES


def class_mask_to_rgb(
    mask: "np.ndarray",
    num_classes: int = NUM_CLASSES,
) -> np.ndarray:
    """Convert a (H, W) integer class mask to an (H, W, 3) RGB image.

    Args:
        mask:        Integer array of class indices, shape (H, W).
        num_classes: Total number of classes.

    Returns:
        Uint8 RGB array (H, W, 3).
    """
    h, w = mask.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for cls_id in range(num_classes):
        rgb[mask == cls_id] = CLASS_COLORS[cls_id]
    return rgb


def overlay_segmentation(
    image: "np.ndarray",
    pred_mask: "np.ndarray",
    gt_mask: Optional["np.ndarray"] = None,
    alpha: float = 0.45,
) -> np.ndarray:
    """Overlay segmentation colourmap on a grayscale EL image.

    Produces a side-by-side layout: ``[EL | Prediction | GT (optional)]``.

    Args:
        image:     Grayscale EL image (H, W) or (H, W, 1), uint8 or float.
        pred_mask: Predicted class indices (H, W).
        gt_mask:   Ground-truth class indices (H, W).  Omit for unlabeled.
        alpha:     Opacity of the segmentation overlay (0=transparent, 1=opaque).

    Returns:
        Uint8 RGB array of the composite visualisation.
    """
    if image.ndim == 3:
        image = image[:, :, 0]
    if image.dtype != np.uint8:
        image = (image * 255).clip(0, 255).astype(np.uint8)

    h, w = image.shape
    # Convert grayscale to 3-channel
    el_rgb = np.stack([image] * 3, axis=-1)

    pred_rgb = class_mask_to_rgb(pred_mask)
    pred_overlay = (
        (1 - alpha) * el_rgb.astype(float) + alpha * pred_rgb.astype(float)
    ).astype(np.uint8)

    panels = [el_rgb, pred_overlay]
    if gt_mask is not None:
        gt_rgb = class_mask_to_rgb(gt_mask)
        gt_overlay = (
            (1 - alpha) * el_rgb.astype(float) + alpha * gt_rgb.astype(float)
        ).astype(np.uint8)
        panels.append(gt_overlay)

    return np.concatenate(panels, axis=1)


def save_visualisation(
    image: "np.ndarray",
    pred_mask: "np.ndarray",
    out_path: str | Path,
    gt_mask: Optional["np.ndarray"] = None,
    alpha: float = 0.45,
) -> None:
    """Save overlay visualisation to disk as PNG.

    Args:
        image:     Grayscale EL image.
        pred_mask: Predicted class indices.
        out_path:  Output file path (parent must exist).
        gt_mask:   Optional ground-truth class indices.
        alpha:     Overlay opacity.
    """
    composite = overlay_segmentation(image, pred_mask, gt_mask, alpha)
    Image.fromarray(composite).save(str(out_path))
