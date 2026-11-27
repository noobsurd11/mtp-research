"""Checkpoint save / load utilities."""

from __future__ import annotations

import logging
import os
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


def save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    step: int,
    metrics: dict[str, Any],
    path: str | Path,
) -> None:
    """Save model weights, optimiser state, step, and metrics to disk.

    Args:
        model:     Model whose state_dict is saved.
        optimizer: Optimiser whose state_dict is saved.
        step:      Number of optimizer steps taken.
        metrics:   Dict of validation metrics to embed in the checkpoint.
        path:      Output file path (parent directories are created).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "step": step,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "metrics": metrics,
    }
    torch.save(state, path)
    logger.debug("Checkpoint saved to %s (step %d)", path, step)


def load_checkpoint(
    path: str | Path,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    device: torch.device | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    """Load a checkpoint into a model (and optionally an optimiser).

    Args:
        path:      Path to the ``.pth`` checkpoint file.
        model:     Model to load weights into.
        optimizer: If provided, the optimiser state is also restored.
        device:    Target device for weight mapping.  Defaults to CPU.
        strict:    Whether to require an exact match of parameter names.

    Returns:
        The full checkpoint dict (contains ``step`` and ``metrics``).

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")

    map_location = device or torch.device("cpu")
    state = torch.load(path, map_location=map_location, weights_only=False)

    model.load_state_dict(state["model_state_dict"], strict=strict)
    if optimizer is not None and "optimizer_state_dict" in state:
        optimizer.load_state_dict(state["optimizer_state_dict"])

    logger.info(
        "Loaded checkpoint from %s (step %s, defect_miou=%.4f)",
        path,
        state.get("step"),
        state.get("metrics", {}).get("defect_miou", float("nan")),
    )
    return state


# ---------------------------------------------------------------------------
# Training-state (resume) helpers
# ---------------------------------------------------------------------------

def atomic_save(obj: Any, path: str | Path) -> None:
    """``torch.save`` to a temporary file, then rename: a crash mid-write never leaves a truncated file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(obj, tmp)
    os.replace(tmp, path)


def rng_state() -> dict[str, Any]:
    """Every RNG the training loop can draw from: python, numpy, torch CPU and all CUDA devices."""
    state = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
    }
    if torch.cuda.is_available():
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state


def set_rng_state(state: dict[str, Any]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])
    if "cuda" in state:
        if not torch.cuda.is_available():
            raise RuntimeError("checkpoint has CUDA RNG state but CUDA is not available")
        torch.cuda.set_rng_state_all(state["cuda"])


def to_cpu(obj: Any) -> Any:
    """Deep copy of a (nested) state dict with every tensor cloned to CPU."""
    if isinstance(obj, torch.Tensor):
        return obj.detach().to("cpu", copy=True)
    if isinstance(obj, dict):
        return {k: to_cpu(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(to_cpu(v) for v in obj)
    return obj
