"""E1: per-cell task metrics for crack (14) and inactive (11), read-only inference (final weights).

Sets: BenchmarkEL test (50 cells, E-SCDD revised masks) and the extension of 106 cells (BenchmarkEL 20221008 cells not
in our 582 and not in the external unlabelled pool; /tmp/noob_el/ext117, ``stems_eval.txt``). Prediction = argmax.

Per cell (definitions fixed before any E1 number was seen; see results/e1/README.md):
  crack:    GT and predicted pixel counts, TP, relaxed P/R within 2 px, skeleton lengths (skimage skeletonize)
  inactive: GT and predicted area as a share of the cell's non-padding pixels (GT class != 7), TP, union

Usage: PYTHONPATH=<skimage dir> python e1_task_metrics.py --code <repo> --out <dir> --runs <run dir> ...
Writes <out>/<run>.json; existing outputs are skipped.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ext", default="/tmp/noob_el/ext117")
ap.add_argument("--runs", nargs="+", required=True)
a = ap.parse_args()
CODE = Path(a.code).resolve()
sys.path.insert(0, str(CODE))
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from PIL import Image  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from skimage.morphology import skeletonize  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

CRACK, INACT, PAD = 14, 11, 7
DEV = torch.device("cuda")
DATA = CODE / "data"


def cell(pred: np.ndarray, gt: np.ndarray, ign: np.ndarray | None = None) -> dict:
    """``ign``: pixels of defect classes outside our taxonomy (ext set: release classes 25-28); scored neither way."""
    keep = np.ones_like(gt, bool) if ign is None else ~ign
    g, p = (gt == CRACK) & keep, (pred == CRACK) & keep
    o = {"crack_gt": int(g.sum()), "crack_pred": int(p.sum()), "crack_tp": int((g & p).sum())}
    if ign is not None:
        o["crack_pred_on_ignored"] = int(((pred == CRACK) & ign).sum())
        o["inact_pred_on_ignored"] = int(((pred == INACT) & ign).sum())
        o["ignored_px"] = int(ign.sum())
    if g.any():
        dg = ndi.distance_transform_edt(~g)
        dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
        o["crack_p2_hit"] = int((dg[p] <= 2).sum())
        o["crack_r2_hit"] = int((dp[g] <= 2).sum())
        o["crack_len_gt"] = int(skeletonize(g).sum())
        o["crack_len_pred"] = int(skeletonize(p).sum()) if p.any() else 0
    area = max(int(((gt != PAD) & keep).sum()), 1)
    ig, ip = (gt == INACT) & keep, (pred == INACT) & keep
    o.update(area=area, inact_gt=int(ig.sum()), inact_pred=int(ip.sum()), inact_tp=int((ig & ip).sum()),
             inact_union=int((ig | ip).sum()))
    return o


@torch.no_grad()
def predict(m, img_dir: Path, msk_dir: Path, stems: list[str], cfg: dict) -> list[np.ndarray]:
    d = cfg["data"]
    ds = BenchmarkELDataset(img_dir, msk_dir, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
    out = []
    for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=4):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out += list(m(b["image"].to(DEV)).float().argmax(1).cpu().numpy())
    return out


def main() -> None:
    torch.backends.cudnn.deterministic, torch.backends.cudnn.benchmark = True, False
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    test = sorted(load_split(DATA / "splits" / "test.txt"))
    test = [s for s in test if (DATA / "escdd_masks" / "test" / f"{s}.png").exists()]
    ext_dir = Path(a.ext)
    ext = [l.strip() for l in open(ext_dir / "stems_eval.txt") if l.strip()]
    sets = {
        "test": (DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", test,
                 [np.array(Image.open(DATA / "escdd_masks" / "test" / f"{s}.png")) for s in test], [None] * len(test)),
        "ext": (ext_dir / "images", ext_dir / "masks", ext, [np.array(Image.open(ext_dir / "masks" / f"{s}.png")) for s in ext],
                [np.array(Image.open(ext_dir / "ignore" / f"{s}.png")) > 0 for s in ext]),
    }
    for run in map(Path, a.runs):
        f = out_dir / f"{run.name}.json"
        if f.exists():
            continue
        t0 = time.time()
        cfg = load_config(run / "config_used.yaml")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}
        mcfg["encoder_weights"] = None  # weights come from the checkpoint
        m = build_model(mcfg).to(DEV)
        m.load_state_dict(st["models"][key])
        m.eval()
        res = {"run": run.name, "weights": key, "step": int(st.get("step", -1)), "cells": {}}
        for name, (img_dir, msk_dir, stems, gts, igns) in sets.items():
            preds = predict(m, img_dir, msk_dir, stems, cfg)
            res["cells"][name] = {s: cell(p, g, i) for s, p, g, i in zip(stems, preds, gts, igns)}
        f.write_text(json.dumps(res))
        print(f"{run.name:24s} {key:7s} ({time.time() - t0:.0f}s)", flush=True)
        del m


if __name__ == "__main__":
    main()
