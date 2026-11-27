"""UCF-EL defect segmentation dataset (Fioresi et al., IEEE JPV 2022).

Layout (the UCF repo's ``training/`` folder, symlinked as ``data/ucf_el``)::

    data/ucf_el/
    ├── train_images.csv, test_images.csv     # imagename, annotatedname
    └── data/{train,test}/{images,annotations}/

Image-mask pairs come only from the CSVs (filenames contain spaces and '+').
Masks are class indices 0..4 (background, crack, contact, interconnect,
corrosion); 128 is UCF's own ignore label (also their crop-padding fill).
Images are read as 3-channel RGB (ImageNet encoder), as in the UCF code.

Split files (committed, ``data/splits/ucf_el/``) list image names, one per
line; ``scripts/make_ucf_splits.py`` writes them and ``manifest.json``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable, Optional

import albumentations as A
import cv2
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from PIL import Image
from torch.utils.data import Dataset

UCF_CLASSES: list[str] = ["background", "crack", "contact", "interconnect", "corrosion"]
UCF_NUM_CLASSES = 5
UCF_IGNORE = 128
UCF_DEFECTS = [1, 2, 3, 4]
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# SegmentationMetrics keyword arguments for UCF-EL.
UCF_METRIC_KW = dict(num_classes=UCF_NUM_CLASSES, ignore_index=UCF_IGNORE, class_names=UCF_CLASSES,
                     defect_classes=UCF_DEFECTS, headline_classes=UCF_DEFECTS, crack_class=1,
                     background_class=0, pratt_classes=UCF_DEFECTS)


def read_pairs(root: str | Path, split: str) -> dict[str, str]:
    """``{imagename: annotatedname}`` from ``<split>_images.csv``; hard error on a missing file or pair."""
    root = Path(root)
    path = root / f"{split}_images.csv"
    if not path.is_file():
        raise FileNotFoundError(f"UCF-EL csv not found: {path}")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    pairs = {r["imagename"]: r["annotatedname"] for r in rows}
    if len(pairs) != len(rows):
        raise ValueError(f"{path}: duplicate image names")
    return pairs


def load_ucf_mask(path: str | Path) -> np.ndarray:
    m = Image.open(path)
    if m.mode not in ("L", "P"):
        raise ValueError(f"{path}: expected a single-channel mask, got mode {m.mode}")
    mask = np.array(m, dtype=np.int64)
    bad = ~(((mask >= 0) & (mask < UCF_NUM_CLASSES)) | (mask == UCF_IGNORE))
    if bad.any():
        raise ValueError(f"{path}: mask values outside 0..4 / 128: {sorted(np.unique(mask[bad]).tolist())}")
    return mask


class UCFELDataset(Dataset):
    """Image-mask pairs of one official split, restricted to ``names``.

    Args:
        root:       ``data/ucf_el``.
        split:      ``'train'`` or ``'test'`` (official folders and csv).
        names:      Image names (from a committed split file); every one must be in the csv.
        transform:  Albumentations pipeline (image + mask), or None.
        labeled:    False: return no ``'mask'`` key (unlabelled pool, masks hidden).
        return_raw: Return the raw uint8 image (H, W, 3) and mask, ignoring ``transform``.
    """

    def __init__(self, root: str | Path, split: str, names: list[str], transform: Optional[Callable] = None,
                 labeled: bool = True, return_raw: bool = False) -> None:
        if not names:
            raise ValueError("UCFELDataset needs a non-empty list of image names")
        self.root = Path(root)
        pairs = read_pairs(self.root, split)
        missing = [n for n in names if n not in pairs]
        if missing:
            raise ValueError(f"{len(missing)} names not in {split}_images.csv, e.g. {missing[:3]}")
        self.img_dir = self.root / "data" / split / "images"
        self.msk_dir = self.root / "data" / split / "annotations"
        self.names = list(names)
        self.masks = [pairs[n] for n in self.names]
        self.transform, self.labeled, self.return_raw = transform, labeled, return_raw

    def __len__(self) -> int:
        return len(self.names)

    def __getitem__(self, idx: int) -> dict:
        name = self.names[idx]
        image = np.array(Image.open(self.img_dir / name).convert("RGB"), dtype=np.uint8)
        sample: dict = {"stem": name}
        mask = load_ucf_mask(self.msk_dir / self.masks[idx]) if self.labeled else None
        if mask is not None and mask.shape != image.shape[:2]:
            raise ValueError(f"{name}: image {image.shape[:2]} vs mask {mask.shape}")
        if self.return_raw:
            sample["image"] = image
            if mask is not None:
                sample["mask"] = mask
            return sample
        if mask is not None:
            out = self.transform(image=image, mask=mask) if self.transform else {"image": image, "mask": mask}
            sample["image"], sample["mask"] = out["image"], torch.as_tensor(out["mask"]).long()
        else:
            sample["image"] = self.transform(image=image)["image"] if self.transform else image
        return sample


def count_ucf_class_pixels(root: str | Path, names: list[str], split: str = "train") -> np.ndarray:
    """Per-class pixel counts (0..4, ignore 128 excluded) of the given images' masks, at full resolution."""
    pairs = read_pairs(root, split)
    counts = np.zeros(UCF_NUM_CLASSES, dtype=np.int64)
    for n in names:
        m = load_ucf_mask(Path(root) / "data" / split / "annotations" / pairs[n])
        counts += np.bincount(m[m != UCF_IGNORE].ravel(), minlength=UCF_NUM_CLASSES)[:UCF_NUM_CLASSES]
    return counts


# ---------------------------------------------------------------------------
# Fioresi recipe transforms
# ---------------------------------------------------------------------------

def _resize(resize: int) -> A.SmallestMaxSize:
    # Shorter side to ``resize``, aspect kept; image bilinear, mask nearest.
    return A.SmallestMaxSize(max_size=resize, interpolation=cv2.INTER_LINEAR, mask_interpolation=cv2.INTER_NEAREST)


def ucf_geometric(resize: int = 295, crop: int = 256, random_rescale: tuple[float, float] | None = None,
                  rot90: bool = False) -> list:
    """Resize the shorter side to ``resize``, random ``crop``×``crop`` crop, horizontal and vertical flips.

    The two options switch on augmentations of the UCF reference code that the
    reproduction arms leave off: ``random_rescale=(0.6, 1.5)`` resizes the
    shorter side to a random integer in [0.6, 1.5] × ``resize`` instead of
    ``resize`` (padding with image 0 / mask 128 when smaller than the crop), and
    ``rot90`` adds a random 90° rotation (p = 0.5).
    """
    if random_rescale is not None:
        lo, hi = int(random_rescale[0] * resize), int(random_rescale[1] * resize)
        sizing = A.SmallestMaxSize(max_size=list(range(lo, hi + 1)), interpolation=cv2.INTER_LINEAR,
                                   mask_interpolation=cv2.INTER_NEAREST)
    else:
        sizing = _resize(resize)
    return [
        sizing,
        A.PadIfNeeded(crop, crop, border_mode=cv2.BORDER_CONSTANT, fill=0, fill_mask=UCF_IGNORE),
        A.RandomCrop(crop, crop),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
    ] + ([A.RandomRotate90(p=0.5)] if rot90 else [])


def ucf_normalize() -> list:
    return [A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD, max_pixel_value=255.0), ToTensorV2()]


def get_ucf_train_transform(resize: int = 295, crop: int = 256, random_rescale=None, rot90: bool = False,
                            photometric: str | None = None) -> A.Compose:
    """Supervised training transform.  ``photometric``: ``None`` (the SL arms) or a strong-view version
    (``"v1"`` / ``"v2"``) applied after the geometry, e.g. the strong-view supervision diagnostic."""
    photo = ucf_strong_ops(photometric) if photometric else []
    return A.Compose(ucf_geometric(resize, crop, random_rescale, rot90) + photo + ucf_normalize())


def get_ucf_eval_transform(resize: int = 295) -> A.Compose:
    """Shorter side to ``resize`` (aspect kept) and normalise; metrics are computed at this resolution."""
    return A.Compose([_resize(resize)] + ucf_normalize())


def get_ucf_geometric(resize: int = 295, crop: int = 256, random_rescale=None, rot90: bool = False) -> A.Compose:
    """Shared geometric stage for the PV-S3 student/teacher views (uint8 out)."""
    return A.Compose(ucf_geometric(resize, crop, random_rescale, rot90))


def get_ucf_weak_photometric() -> A.Compose:
    """Teacher view: normalise only."""
    return A.Compose(ucf_normalize())


# Strong (student) photometric view, Jha et al.: colour jitter up to ±50 %, random greyscale, Gaussian
# blur kernel 1–5 / sigma 0.1–2.0.  Photometric only; CutMix is left out (it is not photometric).
# Application probabilities (jitter, grey, blur) per version:
#   v1: 1.0, 0.2, 1.0 (ucf_pvs3_ssl20_s0, the failed recipe: jitter and blur on every image)
#   v2: 0.8, 0.2, 0.5 (PV-S3 v2)
STRONG_PROBS = {"v1": (1.0, 0.2, 1.0), "v2": (0.8, 0.2, 0.5)}


def ucf_strong_ops(version: str = "v1") -> list:
    if version not in STRONG_PROBS:
        raise ValueError(f"unknown strong view version {version!r} ({' | '.join(STRONG_PROBS)})")
    p_jitter, p_grey, p_blur = STRONG_PROBS[version]
    return [
        A.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5, hue=0.0, p=p_jitter),
        A.ToGray(p=p_grey),
        A.GaussianBlur(blur_limit=(1, 5), sigma_limit=(0.1, 2.0), p=p_blur),
    ]


def get_ucf_strong_photometric(version: str = "v1") -> A.Compose:
    """Student view on top of the shared geometry: strong photometric ops (``STRONG_PROBS``) + normalise."""
    return A.Compose(ucf_strong_ops(version) + ucf_normalize())


def collate_eval(batch: list[dict]) -> dict:
    """Eval batches of size 1 keep their own image size."""
    if len(batch) != 1:
        raise ValueError("UCF-EL evaluation uses batch size 1 (variable image sizes)")
    b = batch[0]
    return {"image": b["image"][None], "mask": b["mask"][None], "stem": [b["stem"]]}
