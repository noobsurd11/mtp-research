"""Shared loaders for the UCF-EL analysis (local, read-only). Data root passed on the command line."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

CLASSES = ["background", "crack", "contact", "interconnect", "corrosion"]
BG, CRACK, CONTACT, INTERCONNECT, CORROSION = range(5)
IGNORE = 128
NAME_RE = re.compile(r"^(?P<cond>.+?) TestName_(?P<date>\d{8})_(?P<time>[\d.]+)_C(?P<cell>\d+)\.jpg$")


def pairs(root: Path, split: str) -> list[tuple[str, str]]:
    """[(imagename, annotatedname)] from training/<split>_images.csv, in file order."""
    with open(root / "training" / f"{split}_images.csv", newline="") as f:
        return [(r["imagename"], r["annotatedname"]) for r in csv.DictReader(f)]


def parse_name(name: str) -> dict:
    """condition (e.g. 'Bent Cure 0Pa'), session (date_time = one module image), cell index."""
    m = NAME_RE.match(name)
    if not m:
        return {"cond": None, "session": None, "cell": None}
    return {"cond": m["cond"], "session": f'{m["date"]}_{m["time"]}', "cell": int(m["cell"])}


def load_image(root: Path, split: str, name: str) -> np.ndarray:
    im = Image.open(root / "training" / "data" / split / "images" / name).convert("L")
    return np.asarray(im, dtype=np.float32)


def load_mask(root: Path, split: str, ann: str) -> np.ndarray:
    return np.asarray(Image.open(root / "training" / "data" / split / "annotations" / ann))


def load_split_list(path: Path) -> list[str]:
    return [l.strip() for l in open(path) if l.strip()]


def dump(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
