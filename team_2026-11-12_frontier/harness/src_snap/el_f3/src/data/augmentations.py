"""Augmentation pipelines (Albumentations 2.x).

Augmentation is split into a geometric stage and photometric stages:

  - Geometric (shared): flips, 90° rotations and a small rotation (±5°) with a
    constant border.  Applied jointly to image and mask so they stay
    pixel-aligned.  The border is filled with 0 in the image and with class 7
    (``padding``) in the mask, which is what the out-of-module area is
    labelled as in the dataset.  No reflect border: reflection would mirror
    cracks and other defects into the corners together with their labels.
  - Weak photometric: normalise only (teacher / evaluation).
  - Strong photometric: blur, brightness/contrast jitter, Gaussian noise,
    normalise (student / supervised training).

The supervised pipeline is geometric + strong photometric in one Compose.  The
SSL pipeline applies the geometric stage once per sample, then the two
photometric stages separately, so student and teacher views share geometry.
"""

from __future__ import annotations

import random

import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2

from .class_info import PADDING_CLASS

# GaussNoise std as a fraction of the max pixel value.  (0.0124, 0.0277) is
# sigma ≈ 3.2–7.1 on the 0–255 scale, i.e. the old var_limit=(10, 50) that
# Albumentations 2.x no longer accepts.
NOISE_STD_RANGE: tuple[float, float] = (0.0124, 0.0277)
ROTATE_LIMIT: float = 5.0


def _geometric_ops(image_size: int) -> list:
    return [
        A.Resize(image_size, image_size),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.Rotate(
            limit=ROTATE_LIMIT,
            border_mode=cv2.BORDER_CONSTANT,
            fill=0,
            fill_mask=PADDING_CLASS,
            p=0.5,
        ),
    ]


def _strong_photometric_ops(p_blur: float, p_jitter: float, p_noise: float) -> list:
    return [
        A.GaussianBlur(blur_limit=(3, 7), p=p_blur),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=p_jitter),
        A.GaussNoise(std_range=NOISE_STD_RANGE, p=p_noise),
    ]


def get_weak_augmentation(
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
    image_size: int = 512,
) -> A.Compose:
    """Evaluation / teacher pipeline: resize + normalise only."""
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_strong_augmentation(
    image_size: int = 512,
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
    p_blur: float = 0.3,
    p_jitter: float = 0.4,
    p_noise: float = 0.3,
) -> A.Compose:
    """Supervised training pipeline: geometric + strong photometric + normalise."""
    return A.Compose(
        _geometric_ops(image_size)
        + _strong_photometric_ops(p_blur, p_jitter, p_noise)
        + [A.Normalize(mean=mean, std=std, max_pixel_value=255.0), ToTensorV2()]
    )


def get_flip_augmentation(
    image_size: int = 512,
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
) -> A.Compose:
    """Pratt et al. (2023) augmentation: 180° rotation, horizontal and vertical flip; nothing photometric.

    A 180° rotation is a horizontal plus a vertical flip, so two independent
    flips (p = 0.5 each) give the identity, mirror, flip and 180° rotation with
    probability 1/4 each: the four images of their offline augmented set.
    """
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_labelsafe_augmentation(
    image_size: int = 512,
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
    p_jitter: float = 0.4,
) -> A.Compose:
    """Label-safe supervised pipeline for 1–2 px labels (P6, arm L1).

    Geometry is limited to exact pixel permutations (flips, 90° rotations), so a
    thin label is never resampled or shifted against its crack. The only
    photometric op is brightness/contrast jitter, which leaves faint cracks
    visible. Compared with ``get_strong_augmentation`` it drops the ±5° rotation,
    the Gaussian blur and the Gaussian noise.
    """
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=p_jitter),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_labelsafe_geometric(image_size: int = 512) -> A.Compose:
    """Shared geometric stage for label-safe SSL (P7): exact pixel permutations only (flips, 90° rotations)."""
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
        ]
    )


def get_labelsafe_strong_photometric(
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
    p_jitter: float = 0.8,
    p_noise: float = 0.3,
) -> A.Compose:
    """Student-branch photometric stage for label-safe SSL (P7).

    Brightness/contrast jitter (±0.25) and mild Gaussian noise. Unlike ``get_strong_photometric`` there is no blur,
    which erases 1–2 px cracks.
    """
    return A.Compose(
        [
            A.RandomBrightnessContrast(brightness_limit=0.25, contrast_limit=0.25, p=p_jitter),
            A.GaussNoise(std_range=NOISE_STD_RANGE, p=p_noise),
            A.Normalize(mean=mean, std=std, max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def get_geometric_augmentation(image_size: int = 512) -> A.Compose:
    """Shared geometric stage for the SSL student/teacher branches.

    Emits a uint8 image (H, W, 1) and an int mask (H, W); normalisation happens
    in the per-branch photometric stage.
    """
    return A.Compose(_geometric_ops(image_size))


def get_weak_photometric(
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
) -> A.Compose:
    """Teacher-branch photometric stage: normalise + ToTensor only."""
    return A.Compose([A.Normalize(mean=mean, std=std, max_pixel_value=255.0), ToTensorV2()])


def get_strong_photometric(
    mean: list[float] = (0.5,),
    std: list[float] = (0.25,),
    p_blur: float = 0.3,
    p_jitter: float = 0.4,
    p_noise: float = 0.3,
) -> A.Compose:
    """Student-branch photometric stage: intensity perturbations + normalise.

    Contains no geometric ops; geometry is drawn once by
    ``get_geometric_augmentation`` and shared with the teacher.
    """
    return A.Compose(
        _strong_photometric_ops(p_blur, p_jitter, p_noise)
        + [A.Normalize(mean=mean, std=std, max_pixel_value=255.0), ToTensorV2()]
    )


# ---------------------------------------------------------------------------
# CutMix (batch-level)
# ---------------------------------------------------------------------------

def apply_cutmix(
    images: "torch.Tensor",
    masks: "torch.Tensor",
    alpha: float = 1.0,
) -> tuple["torch.Tensor", "torch.Tensor"]:
    """Apply CutMix to a batch of images and their segmentation masks.

    For each sample in the batch, a random rectangular region is replaced
    with the corresponding region from a randomly chosen other sample.
    The same cut is applied to the mask so labels remain consistent.

    Args:
        images: Float tensor (B, C, H, W), already normalised.
        masks:  Long tensor (B, H, W) of class indices.
        alpha:  Beta distribution parameter for λ sampling.

    Returns:
        Augmented ``(images, masks)`` tensors of the same shape.
    """
    import torch

    B, C, H, W = images.shape
    lam = float(np.random.beta(alpha, alpha))

    rand_index = torch.randperm(B)
    cut_w = int(W * (1.0 - lam) ** 0.5)
    cut_h = int(H * (1.0 - lam) ** 0.5)
    cx = random.randint(0, W)
    cy = random.randint(0, H)

    x1 = max(cx - cut_w // 2, 0)
    x2 = min(cx + cut_w // 2, W)
    y1 = max(cy - cut_h // 2, 0)
    y2 = min(cy + cut_h // 2, H)

    images_aug = images.clone()
    masks_aug = masks.clone()

    images_aug[:, :, y1:y2, x1:x2] = images[rand_index, :, y1:y2, x1:x2]
    masks_aug[:, y1:y2, x1:x2] = masks[rand_index, y1:y2, x1:x2]

    return images_aug, masks_aug


# ---------------------------------------------------------------------------
# DataLoader worker seeding
# ---------------------------------------------------------------------------

def seed_worker(worker_id: int) -> None:
    """``worker_init_fn`` that gives every DataLoader worker its own RNG streams.

    Albumentations 2.x Compose objects carry their own generators, created in
    the main process; forked workers would otherwise all replay the same
    augmentation sequence (and repeat it on every pass over the data).  The
    seed is derived from ``torch.initial_seed()``, which differs per worker
    and per iterator, and stays reproducible under a fixed global seed.
    """
    import torch

    seed = torch.initial_seed() % 2**32
    np.random.seed(seed)
    random.seed(seed)
    info = torch.utils.data.get_worker_info()
    if info is not None:
        from .stream import find_composes, seed_pipeline

        seed_pipeline(find_composes(info.dataset), seed)
