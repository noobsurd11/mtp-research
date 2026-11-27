"""24-class taxonomy, RGB colour codes, and loss-weight / threshold helpers
for the BenchmarkELimages dataset.

Source: dataset_20211104 of https://github.com/TheMakiran/BenchmarkELimages
        (the canonical 24-class benchmark: 12 intrinsic features + 12 extrinsic
        defects).  Names/RGB codes are taken verbatim from
        ``ListOfClassesAndColorCodes_20211104.csv`` (the Red/Green/Blue columns
        used to colour the GIMP RGB masks).

There are no hard-coded class frequencies: loss weights and SemiCE thresholds
are computed at startup from the labelled training subset in use (see
``get_ce_weights`` / ``get_semice_thresholds`` and
``src/data/class_stats.count_class_pixels``).

The dataset ships the ground-truth masks as single-channel index PNGs
(pixel value == class index 0-23); they are read directly.  The RGB codes are
kept only for visualisation.
"""

from __future__ import annotations

import torch
import numpy as np

# ---------------------------------------------------------------------------
# Class registry
# ---------------------------------------------------------------------------
# Each entry: class index, name, feature/defect kind, RGB colour.
# ---------------------------------------------------------------------------

CLASS_INFO: list[dict] = [
    # idx  name             kind       RGB
    {"id":  0, "name": "background",     "kind": "feature", "rgb": (  0,   0,   0)},
    {"id":  1, "name": "sp_multi",       "kind": "feature", "rgb": (128, 128, 128)},
    {"id":  2, "name": "sp_mono",        "kind": "feature", "rgb": ( 80,  80,  80)},
    {"id":  3, "name": "sp_dogbone",     "kind": "feature", "rgb": (  0,   0, 255)},
    {"id":  4, "name": "ribbons",        "kind": "feature", "rgb": (  0, 255,   0)},
    {"id":  5, "name": "border",         "kind": "feature", "rgb": (100,  50,  50)},
    {"id":  6, "name": "text",           "kind": "feature", "rgb": (225,   0, 100)},
    {"id":  7, "name": "padding",        "kind": "feature", "rgb": (128, 128,   0)},
    {"id":  8, "name": "clamp",          "kind": "feature", "rgb": (255, 215,   0)},
    {"id":  9, "name": "busbars",        "kind": "feature", "rgb": ( 50,  50, 255)},
    {"id": 10, "name": "crack_rbn_edge", "kind": "defect",  "rgb": (  0, 255, 255)},
    {"id": 11, "name": "inactive",       "kind": "defect",  "rgb": (255,   0,   0)},
    {"id": 12, "name": "rings",          "kind": "defect",  "rgb": (255,   0, 255)},
    {"id": 13, "name": "material",       "kind": "defect",  "rgb": (255, 255,   0)},
    {"id": 14, "name": "crack",          "kind": "defect",  "rgb": (255, 255, 255)},
    {"id": 15, "name": "gridline",       "kind": "defect",  "rgb": (255, 165,   0)},
    {"id": 16, "name": "splice",         "kind": "defect",  "rgb": ( 75,   0, 130)},
    {"id": 17, "name": "dead_cell",      "kind": "defect",  "rgb": ( 32,  32,  32)},
    {"id": 18, "name": "corrosion",      "kind": "defect",  "rgb": (  0, 150,   0)},
    {"id": 19, "name": "belt_mark",      "kind": "defect",  "rgb": (218, 165,  32)},
    {"id": 20, "name": "edge_dark",      "kind": "defect",  "rgb": (184, 134,  11)},
    {"id": 21, "name": "frame_edge",     "kind": "feature", "rgb": (127, 255, 215)},
    {"id": 22, "name": "jbox",           "kind": "feature", "rgb": ( 45,  45, 255)},
    {"id": 23, "name": "meas_artifact",  "kind": "defect",  "rgb": ( 50,  50,  50)},
]

NUM_CLASSES: int = len(CLASS_INFO)

# Indices considered "defects" vs "intrinsic features" for separate mIoU.
# Taken from the "feature"/"defect" Class column of the dataset CSV.
DEFECT_CLASSES: list[int] = [c["id"] for c in CLASS_INFO if c["kind"] == "defect"]
FEATURE_CLASSES: list[int] = [c["id"] for c in CLASS_INFO if c["kind"] == "feature"]

# ---------------------------------------------------------------------------
# Special class ids
# ---------------------------------------------------------------------------

# Out-of-module area.  Used as the mask fill value for rotation borders.
PADDING_CLASS: int = 7
CRACK_CLASS: int = 14
INACTIVE_CLASS: int = 11

# ---------------------------------------------------------------------------
# Colour palette (visualisation only; masks are read as class indices)
# ---------------------------------------------------------------------------

# Colour map as a numpy array [num_classes, 3] for visualisation
CLASS_COLORS: np.ndarray = np.array(
    [c["rgb"] for c in CLASS_INFO], dtype=np.uint8
)

# ---------------------------------------------------------------------------
# Loss weight computation
# ---------------------------------------------------------------------------

def get_ce_weights(
    class_counts: np.ndarray,
    cap_ratio: float = 10.0,
) -> torch.Tensor:
    """Per-class weights for weighted cross-entropy from pixel counts.

    ``w[c] = 1 / sqrt(freq[c])`` for classes with at least one pixel, capped at
    ``cap_ratio`` × the median weight of those classes, then scaled so their
    mean is 1.  Classes with zero pixels get weight 0.

    Args:
        class_counts: Pixel counts (num_classes,) over the labelled training
                      subset in use (train images only).
        cap_ratio:    Cap relative to the median present-class weight.

    Returns:
        Float tensor of shape (num_classes,).
    """
    counts = np.asarray(class_counts, dtype=np.float64)
    if counts.shape != (NUM_CLASSES,):
        raise ValueError(f"class_counts must have shape ({NUM_CLASSES},), got {counts.shape}")
    present = counts > 0
    if not present.any():
        raise ValueError("class_counts is all zero")

    weights = np.zeros(NUM_CLASSES, dtype=np.float64)
    freq = counts[present] / counts.sum()
    w = 1.0 / np.sqrt(freq)
    w = np.minimum(w, cap_ratio * np.median(w))
    weights[present] = w / w.mean()
    return torch.tensor(weights, dtype=torch.float32)


def get_semice_thresholds(
    frequencies: np.ndarray,
    beta: float = 0.5,
    gamma: float = 0.5,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Compute data-driven per-class SemiCE thresholds.

    Thresholds are applied to raw logits:
      - t_pos[c] = beta  * freq[c]         (positive confidence threshold)
      - t_neg[c] = gamma * (1 − freq[c])   (negative confidence magnitude)

    Args:
        frequencies: Per-class pixel frequencies (num_classes,) of the
                     labelled training subset in use.
        beta:        Scale factor for positive thresholds.
        gamma:       Scale factor for negative thresholds.

    Returns:
        Tuple ``(t_pos, t_neg)`` — float tensors of shape (num_classes,).
    """
    freq = torch.tensor(np.asarray(frequencies), dtype=torch.float32)
    t_pos = beta * freq
    t_neg = gamma * (1.0 - freq)
    return t_pos, t_neg


# ---------------------------------------------------------------------------
# Fixed class-weight sets of Pratt et al. (2023), BenchmarkELimages paper
# ---------------------------------------------------------------------------

def pratt_weights(weight_set: str) -> torch.Tensor:
    """Weighted-CE weights of Pratt et al. (2023), Table 2.

    * ``A``: all classes 1.0.
    * ``C``: background 0.2, ribbons 3, gridline 10, inactive 10, crack 20,
      every other class 1.0.
    (Set B, inverse median per-image class share, is not implemented.)
    """
    w = torch.ones(NUM_CLASSES, dtype=torch.float32)
    if weight_set == "A":
        return w
    if weight_set == "C":
        by_name = {c["name"]: c["id"] for c in CLASS_INFO}
        for name, value in (("background", 0.2), ("ribbons", 3.0), ("gridline", 10.0),
                            ("inactive", 10.0), ("crack", 20.0)):
            w[by_name[name]] = value
        return w
    raise ValueError(f"unknown Pratt weight set {weight_set!r} (A | C)")
