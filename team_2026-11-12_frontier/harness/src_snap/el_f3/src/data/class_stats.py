"""Per-class pixel statistics over a list of index masks."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .benchmark_el import load_index_mask
from .class_info import NUM_CLASSES


def count_class_pixels(mask_dir: str | Path, stems: list[str], ignore_value: int | None = None) -> np.ndarray:
    """Return an int64 array (NUM_CLASSES,) of pixel counts summed over ``stems`` (``ignore_value`` px not counted)."""
    mask_dir = Path(mask_dir)
    counts = np.zeros(NUM_CLASSES, dtype=np.int64)
    for stem in stems:
        m = load_index_mask(mask_dir / f"{stem}.png", ignore_value)
        if ignore_value is not None:
            m = m[m != ignore_value]
        counts += np.bincount(m.ravel(), minlength=NUM_CLASSES)
    return counts


def classes_present(mask_dir: str | Path, stem: str) -> set[int]:
    """Set of class ids that occur in one mask."""
    return set(np.unique(load_index_mask(Path(mask_dir) / f"{stem}.png")).tolist())
