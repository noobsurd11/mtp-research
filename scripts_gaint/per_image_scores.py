"""Per-image crack/inactive confusion counts at argmax, revised labels (EXPLORATORY, read-only).

Same inference as scripts/rescore_label_versions.py (final weights, weak view, bf16; EMA teacher for mean_teacher).
Output JSON: {"<split>/<run>": {"<stem>": [crack tp, fp, fn, inactive tp, fp, fn]}}. Summing over stems reproduces the
dataset-level IoU of the re-score JSONs; per-image counts allow leave-cells-out and image-bootstrap checks.

Usage: .venv/bin/python scripts/per_image_scores.py --runs p6_L0_10pct_s0 ... --out reports/p6/per_image.json
"""
from __future__ import annotations

import argparse, json, os, sys
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


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--splits", nargs="+", default=["test", "val"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--weights", default="auto", choices=["auto", "model"], help="auto: EMA teacher for mean_teacher (as the rescore); model: the student")
    a = ap.parse_args()
    dev = torch.device("cuda")
    res = {}
    for split in a.splits:
        stems = [s for s in sorted(load_split(DATA / "splits" / f"{split}.txt")) if (NEW / split / f"{s}.png").exists()]
        new = [np.array(Image.open(NEW / split / f"{s}.png")) for s in stems]
        for run in a.runs:
            cfg = load_config(ROOT / "experiments" / run / "config_used.yaml"); d = cfg["data"]
            ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
            st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
            key = "teacher" if a.weights == "auto" and cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
            m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
            out, i = {}, 0
            for b in DataLoader(ds, batch_size=8, shuffle=False, num_workers=2):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    pr = m(b["image"].to(dev)).float().argmax(1).cpu().numpy()
                for k in range(pr.shape[0]):
                    g, row = new[i], []
                    for c in (CRACK_CLASS, INACTIVE_CLASS):
                        p, t = pr[k] == c, g == c
                        row += [int((p & t).sum()), int((p & ~t).sum()), int((~p & t).sum())]
                    out[stems[i]] = row; i += 1
            assert i == len(stems)
            res[f"{split}/{run}" + ("" if key != "model" or cfg.get("method") != "mean_teacher" else "@student")] = out
            tot = np.array(list(out.values())).sum(0)
            print(f"{split} {run} {key} crack IoU {tot[0] / max(tot[:3].sum(), 1):.4f} inactive IoU {tot[3] / max(tot[3:].sum(), 1):.4f}", flush=True)
            del m; torch.cuda.empty_cache()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
