"""Reproducibility: set all random seeds consistently."""

from __future__ import annotations

import os
import random

import numpy as np
import torch


def set_seed(seed: int = 42, deterministic: bool | str = True) -> None:
    """Set all random seeds for reproducible experiments.

    Args:
        seed:          Integer seed value.
        deterministic: ``True``: cuDNN deterministic, benchmark off (training
                       runs; a few CUDA kernels such as the bilinear-upsampling
                       backward still accumulate with atomics, so runs are not
                       bitwise reproducible).  ``"strict"``: additionally
                       ``torch.use_deterministic_algorithms(True)``: bitwise
                       reproducible, an op without a deterministic kernel
                       raises; about 5x slower for U-Net++ at 512 px, so used
                       for tests only.  ``False``: none of this.  ``"strict"``
                       needs ``CUBLAS_WORKSPACE_CONFIG`` set before CUDA
                       initialises (``scripts/train.py`` sets it).
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    if deterministic not in (True, False, "strict"):
        raise ValueError(f"deterministic must be true, false or 'strict', got {deterministic!r}")
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    if deterministic == "strict":
        torch.use_deterministic_algorithms(True)
