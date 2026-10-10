"""Qualitative overlays for the mid-term (EXPLORATORY, read-only inference on final weights).

Rows: 3 test cells chosen by a fixed rule, not by model output: the two with the most revised-label crack pixels and
the one with the most revised-label inactive pixels (excluding the first two).
Columns: image, old label (20211104), revised label (E-SCDD), then argmax predictions of the given runs.
Colours: crack red, inactive blue. Inference as rescore_label_versions.py (weak view, bf16 autocast).

Usage: .venv/bin/python scripts/overlay_figure.py --runs p6_L0_10pct_s0 p6_L1_10pct_s0 p6_L3_10pct_s0 p6_L3_100pct_s0 --out reports/p6/fig_overlays.png
"""
from __future__ import annotations

import argparse, os, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks" / "test"


def overlay(ax, img, lab, title=None):
    rgb = np.repeat(img[..., None], 3, -1).astype(float)
    for c, col in ((CRACK_CLASS, (1.0, 0.1, 0.1)), (INACTIVE_CLASS, (0.15, 0.45, 1.0))):
        m = lab == c
        rgb[m] = 0.45 * rgb[m] + 0.55 * np.array(col)
    ax.imshow(rgb); ax.set_xticks([]); ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=9)


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    stems = [s for s in sorted(load_split(DATA / "splits" / "test.txt")) if (NEW / f"{s}.png").exists()]
    new = {s: np.array(Image.open(NEW / f"{s}.png")) for s in stems}
    by_crack = sorted(stems, key=lambda s: -(new[s] == CRACK_CLASS).sum())[:2]
    by_inact = [s for s in sorted(stems, key=lambda s: -(new[s] == INACTIVE_CLASS).sum()) if s not in by_crack][:1]
    pick = by_crack + by_inact
    dev = torch.device("cuda")
    preds = {}
    for run in a.runs:
        cfg = load_config(ROOT / "experiments" / run / "config_used.yaml"); d = cfg["data"]
        ds = BenchmarkELDataset(IMG, MSK, pick, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
        st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
        for i in range(len(pick)):
            b = ds[i]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                preds[(run, pick[i])] = m(b["image"][None].to(dev)).float().argmax(1)[0].cpu().numpy()
            if run == a.runs[0]:
                preds[("old", pick[i])] = b["mask"].numpy()
        del m; torch.cuda.empty_cache()
    names = a.labels or a.runs
    fig, axs = plt.subplots(len(pick), 3 + len(a.runs), figsize=(2.1 * (3 + len(a.runs)), 2.25 * len(pick)))
    for r, s in enumerate(pick):
        img = np.array(Image.open(IMG / f"{s}.png").convert("L"))
        if img.shape != new[s].shape:
            img = np.array(Image.fromarray(img).resize(new[s].shape[::-1]))
        img = img / 255.0
        ys, xs = np.where(img < 0.98)  # crop white padding (BMRK cells are padded to the 512 canvas)
        cy, cx = slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)
        img = img[cy, cx]
        overlay(axs[r, 0], img, np.zeros_like(new[s][cy, cx]), "image" if r == 0 else None)
        overlay(axs[r, 1], img, preds[("old", s)][cy, cx], "old label" if r == 0 else None)
        overlay(axs[r, 2], img, new[s][cy, cx], "revised label (E-SCDD)" if r == 0 else None)
        for j, (run, nm) in enumerate(zip(a.runs, names)):
            overlay(axs[r, 3 + j], img, preds[(run, s)][cy, cx], nm if r == 0 else None)
        axs[r, 0].set_ylabel(s, fontsize=7)
    fig.suptitle("Test cells (fixed rule: top-2 by GT crack area, top-1 by GT inactive area). Red = crack, blue = inactive. Seed 0, final weights.", fontsize=8.5)
    fig.tight_layout(); Path(a.out).parent.mkdir(parents=True, exist_ok=True); fig.savefig(a.out, dpi=150)
    print("wrote", a.out, "stems", pick)


if __name__ == "__main__":
    main()
