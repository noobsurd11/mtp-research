"""PyTorch Dataset for the BenchmarkELimages dataset (``dataset_20211104``).

Expected directory layout (created by ``scripts/link_data.py``):

    data/
    ├── labeled/
    │   ├── images/        # 512×512 EL images (PNG, symlinks)
    │   └── masks_coded/   # 512×512 index masks, pixel value == class id 0–23 (symlinks)
    └── splits/            # committed split files (see scripts/make_splits.py)

Masks are read as-is: the shipped single-channel index PNGs already hold the
class id per pixel, so there is no colour decoding step.

For labeled samples the Dataset:
  1. Loads the image as uint8 grayscale (H, W, 1).
  2. Loads the index mask as an int64 (H, W) array and checks every value is a
     valid class id.
  3. Applies the supplied Albumentations transform jointly to image and mask.
  4. Returns ``{'image': tensor, 'mask': tensor, 'stem': str}``.

For unlabeled samples the mask key is absent from the returned dict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

from .class_info import NUM_CLASSES


def load_index_mask(path: str | Path, ignore_value: int | None = None) -> np.ndarray:
    """Load a single-channel index mask as an int64 (H, W) array.

    ``ignore_value`` (Track M, opt-in, default None): this one extra value is also accepted (e.g. 255 for pixels of
    classes outside the 24-class taxonomy, which the losses then ignore). With None the check is unchanged.

    Raises:
        ValueError: If the PNG is not single-channel or holds a value outside
                    ``0..NUM_CLASSES-1`` (or ``ignore_value``).
    """
    im = Image.open(path)
    if im.mode not in ("L", "P", "I"):
        raise ValueError(f"{path}: expected a single-channel index mask, got mode {im.mode}")
    mask = np.array(im, dtype=np.int64)
    if mask.ndim != 2:
        raise ValueError(f"{path}: expected a 2-D mask, got shape {mask.shape}")
    chk = mask if ignore_value is None else mask[mask != ignore_value]
    if chk.size and (chk.min() < 0 or chk.max() >= NUM_CLASSES):
        raise ValueError(
            f"{path}: mask values must be in 0..{NUM_CLASSES - 1}, "
            f"found {sorted(np.unique(mask).tolist())}"
        )
    return mask


class BenchmarkELDataset(Dataset):
    """Dataset for BenchmarkELimages labeled or unlabeled splits.

    Args:
        image_dir:   Directory containing EL image PNGs.
        mask_dir:    Directory containing index mask PNGs.  Pass ``None``
                     for unlabeled data (``__getitem__`` omits 'mask').
        stem_list:   Image stems (without extension) that make up this split.
                     Required and must be non-empty: there is deliberately no
                     "use every file in the directory" fallback.
        transform:   Albumentations ``Compose`` pipeline applied jointly to
                     image and mask.
        return_raw:  If True, return the raw uint8 image (H, W, 1) and int64
                     mask (H, W) as numpy arrays, ignoring ``transform``.
    """

    def __init__(
        self,
        image_dir: str | Path,
        mask_dir: Optional[str | Path],
        stem_list: list[str],
        transform: Optional[Callable] = None,
        return_raw: bool = False,
        ignore_value: int | None = None,
    ) -> None:
        self.ignore_value = ignore_value  # Track M: see load_index_mask
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir) if mask_dir is not None else None
        self.transform = transform
        self.labeled = mask_dir is not None
        # When True, __getitem__ returns the RAW uint8 image (H, W, 1) and raw
        # int mask (H, W) as numpy arrays instead of applying `transform`.
        # Used by the SSL pipeline, which applies a shared geometric transform
        # to image+mask jointly (see augmentations.get_geometric_augmentation).
        self.return_raw = return_raw

        if not stem_list:
            raise ValueError(
                f"BenchmarkELDataset needs a non-empty stem_list (image_dir={self.image_dir})."
            )
        self.stems = list(stem_list)

    def __len__(self) -> int:
        return len(self.stems)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor | str]:
        stem = self.stems[idx]

        image = np.array(Image.open(self.image_dir / f"{stem}.png").convert("L"), dtype=np.uint8)
        image = image[:, :, np.newaxis]  # (H, W, 1)
        mask = load_index_mask(self.mask_dir / f"{stem}.png", self.ignore_value) if self.labeled else None

        sample: dict = {"stem": stem}

        if self.return_raw:
            sample["image"] = image
            if mask is not None:
                sample["mask"] = mask
            return sample

        if mask is not None:
            if self.transform is not None:
                augmented = self.transform(image=image, mask=mask)
                image, mask = augmented["image"], augmented["mask"]
            else:
                image = torch.from_numpy(image.transpose(2, 0, 1)).float() / 255.0
                mask = torch.from_numpy(mask)
            sample["image"] = image
            sample["mask"] = torch.as_tensor(mask).long()
        else:
            if self.transform is not None:
                image = self.transform(image=image)["image"]
            else:
                image = torch.from_numpy(image.transpose(2, 0, 1)).float() / 255.0
            sample["image"] = image

        return sample
