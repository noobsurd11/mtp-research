"""Load a finished run for evaluation: its eval loader and its weights."""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ..data.augmentations import get_weak_augmentation
from ..data.benchmark_el import BenchmarkELDataset
from ..data.splits import load_split
from ..data.ucf_el import UCF_METRIC_KW, UCFELDataset, get_ucf_eval_transform
from ..models.model_factory import build_model


def eval_loader(cfg: dict, split: str, num_workers: int = 8) -> tuple[DataLoader, dict]:
    """(loader, metric_kw) for ``split`` of the run's dataset."""
    d = cfg["data"]
    if d.get("dataset", "benchmark_el") == "ucf_el":
        if split != "test":
            raise ValueError("UCF-EL reproduction runs are evaluated on the official test split only")
        names = load_split(Path(d["splits"]) / "test.txt")
        ds = UCFELDataset(d["root"], "test", names, get_ucf_eval_transform(int(d.get("resize_size", 295))))
        return DataLoader(ds, batch_size=1, shuffle=False, num_workers=num_workers), UCF_METRIC_KW
    root = Path(d["root"])
    if split == "valtest":  # val + test pooled (BenchmarkEL: 54 + 50 = 104 images); final-step weights only
        stems = load_split(root / "splits" / "val.txt") + load_split(root / "splits" / "test.txt")
    else:
        stems = load_split(root / "splits" / f"{split}.txt")
    ds = BenchmarkELDataset(root / "labeled" / "images", root / "labeled" / "masks_coded", stems,
                            get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    return DataLoader(ds, batch_size=8, shuffle=False, num_workers=num_workers), {}


def load_weights(run: Path, cfg: dict, which: str, device: torch.device) -> tuple[torch.nn.Module, int]:
    """The evaluation model of a run (teacher for MT / PV-S3, network A for ALHVR) and its step."""
    model = build_model({**cfg["model"], "encoder_weights": None}).to(device)
    if which == "best":
        st = torch.load(run / "checkpoints/best.pth", map_location=device, weights_only=False)
        model.load_state_dict(st["model_state_dict"])
        return model, int(st["step"])
    if which == "final":
        st = torch.load(run / "checkpoints/latest.pth", map_location=device, weights_only=False)
        total = int(cfg["training"]["total_steps"])
        if int(st["step"]) != total:
            raise ValueError(f"{run}: latest.pth is at step {st['step']}, the run is not finished ({total})")
        key = "teacher" if "teacher" in st["models"] else "model"
        model.load_state_dict(st["models"][key])
        return model, int(st["step"])
    raise ValueError(f"--weights must be best or final, got {which!r}")
