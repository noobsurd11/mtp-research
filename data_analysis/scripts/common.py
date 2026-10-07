"""Shared loaders for the BenchmarkELimages dataset_20211104 analysis (local, read-only)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
from PIL import Image

SPLIT_DIRS = {
    "train": ("images_train_original", "masks_coded_train_original"),
    "val": ("images_val", "masks_coded_val"),
    "test": ("images_test", "masks_coded_test"),
}
CRACK, INACTIVE, GRIDLINE, RIBBONS, BUSBARS, PADDING, BG = 14, 11, 15, 4, 9, 7, 0
CRACK_RBN_EDGE = 10
NUM_CLASSES = 24

NAME_RE = re.compile(r"^(?P<src>[A-Z]+)_(?P<mod>[^_]+)_(?P<rest>.+)$")


def class_names(root: Path) -> list[str]:
    rows = list(csv.DictReader(open(root / "ListOfClassesAndColorCodes_20211104.csv")))
    names = [""] * NUM_CLASSES
    for r in rows:
        names[int(r["Label"])] = r["Desc"].strip()
    return names


def class_kinds(root: Path) -> list[str]:
    rows = list(csv.DictReader(open(root / "ListOfClassesAndColorCodes_20211104.csv")))
    kinds = [""] * NUM_CLASSES
    for r in rows:
        kinds[int(r["Label"])] = r["Class"].strip()
    return kinds


def stems(root: Path, split: str) -> list[str]:
    return sorted(p.stem for p in (root / SPLIT_DIRS[split][0]).glob("*.png"))


def parse_name(stem: str) -> tuple[str, str]:
    """(source, module id) from e.g. ARTS_00001_r4_c2."""
    m = NAME_RE.match(stem)
    if not m:
        return stem.split("_")[0], stem
    return m["src"], f'{m["src"]}_{m["mod"]}'


def load_image(root: Path, split: str, stem: str) -> np.ndarray:
    im = Image.open(root / SPLIT_DIRS[split][0] / f"{stem}.png")
    a = np.asarray(im)
    if a.ndim == 3:  # RGB(A) grayscale-in-colour -> luminance of first channel
        a = a[..., 0]
    return a.astype(np.float32)


def load_mask(root: Path, split: str, stem: str) -> np.ndarray:
    m = np.asarray(Image.open(root / SPLIT_DIRS[split][1] / f"{stem}.png"))
    if m.ndim == 3:
        m = m[..., 0]
    return m.astype(np.uint8)


def read_list(path: Path) -> list[str]:
    return [l.strip() for l in open(path) if l.strip()]
