"""Skeleton Recall targets in the data workers (thin worktree, opt-in via ``loss.skel_recall.weight > 0``).

``TubedSkeletonDataset`` wraps the labelled training dataset and adds ``skel_tube`` (uint8 (H, W)): the tubed skeleton of
the crack class of the *augmented* mask (Skeleton Recall computes it after augmentation, during data loading). The
wrapped sample's image and mask are returned unchanged, and the wrapper draws no random numbers, so the batch stream
(``BatchStream`` seeds every Albumentations transform it finds through dataset attributes, ``stream.find_composes``)
yields exactly the images and masks of the unwrapped dataset.
"""

from __future__ import annotations

import torch
from torch.utils.data import Dataset

from .skeleton import tubed_skeleton


class TubedSkeletonDataset(Dataset):
    def __init__(self, ds: Dataset, crack_class: int = 14, radius: int = 2) -> None:
        self.ds = ds
        self.crack_class, self.radius = int(crack_class), int(radius)

    def __len__(self) -> int:
        return len(self.ds)

    def __getitem__(self, idx: int) -> dict:
        s = self.ds[idx]
        s["skel_tube"] = torch.from_numpy(tubed_skeleton(s["mask"].numpy(), self.crack_class, self.radius))
        return s
