"""Per-class pixel statistics over a list of index masks."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .benchmark_el import load_index_mask
from .class_info import NUM_CLASSES


def count_class_pixels(mask_dir: str | Path, stems: list[str], ignore_value: int | None = None,
                       num_classes: int | None = None) -> np.ndarray:
    """Return an int64 array (C,) of pixel counts summed over ``stems`` (``ignore_value`` px not counted).

    C = NUM_CLASSES, or ``num_classes`` (B3, opt-in: 25 counts the scuff class 24)."""
    mask_dir = Path(mask_dir)
    nc = NUM_CLASSES if num_classes is None else int(num_classes)
    counts = np.zeros(nc, dtype=np.int64)
    for stem in stems:
        m = load_index_mask(mask_dir / f"{stem}.png", ignore_value, num_classes)
        if ignore_value is not None:
            m = m[m != ignore_value]
        counts += np.bincount(m.ravel(), minlength=nc)
    return counts


def classes_present(mask_dir: str | Path, stem: str) -> set[int]:
    """Set of class ids that occur in one mask."""
    return set(np.unique(load_index_mask(Path(mask_dir) / f"{stem}.png")).tolist())
