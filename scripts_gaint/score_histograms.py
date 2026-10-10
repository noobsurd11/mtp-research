"""Dump per-bin positive/negative pixel counts of crack/inactive softmax scores (EXPLORATORY, read-only).

Same inference as scripts/rescore_label_versions.py (final weights, weak view, bf16, 1000 uniform bins), but saves
the histograms so that (a) AP can be computed on pooled splits exactly and (b) score saturation can be inspected.

Usage: .venv/bin/python scripts/score_histograms.py --runs p6_L0_10pct_s0 ... --out reports/p6/hist.npz
"""
from __future__ import annotations

import argparse, os, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks"
BINS = 1000


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--splits", nargs="+", default=["test", "val"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dev = torch.device("cuda")
    out = {}
    for split in a.splits:
        stems = sorted(load_split(DATA / "splits" / f"{split}.txt"))
        stems = [s for s in stems if (NEW / split / f"{s}.png").exists()]
        new = [np.array(Image.open(NEW / split / f"{s}.png")) for s in stems]
        for run in a.runs:
            cfg = load_config(ROOT / "experiments" / run / "config_used.yaml")
            d = cfg["data"]
            ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
            st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
            key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
            m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
            h = np.zeros((2, 2, BINS), np.int64)  # class (crack, inactive) x (pos, neg) x bin, revised labels
            i = 0
            for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    sm = torch.softmax(m(b["image"].to(dev)).float(), 1)
                for k in range(sm.shape[0]):
                    g = new[i]; i += 1
                    for ci, c in enumerate((CRACK_CLASS, INACTIVE_CLASS)):
                        bn = np.clip((sm[k, c].cpu().numpy() * BINS).astype(int), 0, BINS - 1)
                        h[ci, 0] += np.bincount(bn[g == c], minlength=BINS)
                        h[ci, 1] += np.bincount(bn[g != c], minlength=BINS)
            assert i == len(stems)
            out[f"{split}/{run}"] = h
            print(split, run, key, "crack pos", h[0, 0].sum(), "inactive pos", h[1, 0].sum(), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
