"""Re-score existing checkpoints against two label versions of the same BenchmarkEL images.

Read-only inference. Old labels: data/labeled/masks_coded (dataset_20211104). New labels: E-SCDD masks
(huggingface snt-ubix/escdd, MIT; "refined pixel-level annotations"), same 512x512 images, copied to
data/escdd_masks/<split>/<stem>.png. Images are pixel-identical between versions (checked locally).
Per run and label version: crack / inactive dataset-level IoU, P, R, binned pixel AP, relaxed F1 at 1/2 px.

Usage: .venv/bin/python scripts/rescore_label_versions.py --runs sl_10pct_b8_s0 sl_100pct_b8_s0 ...
"""
from __future__ import annotations

import argparse, json, os, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.evaluation.threshold_free import binned_ap  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK, NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "escdd_masks"
BINS = 1000


def relaxed(pred, gt, r):
    d_gt = ndi.distance_transform_edt(~gt) if gt.any() else np.full(gt.shape, np.inf)
    d_pr = ndi.distance_transform_edt(~pred) if pred.any() else np.full(gt.shape, np.inf)
    return np.array([(d_gt[pred] <= r).sum(), pred.sum(), (d_pr[gt] <= r).sum(), gt.sum()], np.int64)


def score(probs, preds, gts, c):
    tp = fp = fn = 0
    pos, neg = np.zeros(BINS, np.int64), np.zeros(BINS, np.int64)
    rel = {1: np.zeros(4, np.int64), 2: np.zeros(4, np.int64)}
    for pr, pd, g in zip(probs, preds, gts):
        p, t = pd == c, g == c
        tp += int((p & t).sum()); fp += int((p & ~t).sum()); fn += int((~p & t).sum())
        b = np.clip((pr * BINS).astype(int), 0, BINS - 1)
        pos += np.bincount(b[t], minlength=BINS); neg += np.bincount(b[~t], minlength=BINS)
        for r in rel: rel[r] += relaxed(p, t, r)
    out = {"iou": tp / max(tp + fp + fn, 1), "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1),
           "ap": float(binned_ap(pos, neg)), "gt_px": tp + fn}
    for r, v in rel.items():
        P, R = v[0] / max(v[1], 1), v[2] / max(v[3], 1)
        out[f"rel_f1_{r}"] = 2 * P * R / max(P + R, 1e-9); out[f"rel_p{r}"] = P; out[f"rel_r{r}"] = R
    return {k: float(v) for k, v in out.items()}


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--splits", nargs="+", default=["test", "val"])
    ap.add_argument("--out", default="reports/probes/rescore_label_versions.json")
    a = ap.parse_args()
    dev = torch.device("cuda")
    res = {}
    for split in a.splits:
        stems = sorted(load_split(DATA / "splits" / f"{split}.txt"))
        stems = [s for s in stems if (NEW / split / f"{s}.png").exists()]
        new = [np.array(Image.open(NEW / split / f"{s}.png")) for s in stems]
        for run in a.runs:
            cfg = load_config(ROOT / "experiments" / run / "config_used.yaml")
            d = cfg["data"]
            ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
            dl = DataLoader(ds, batch_size=8, shuffle=False, num_workers=2)
            st = torch.load(ROOT / "experiments" / run / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
            key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
            m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
            probs = {CRACK_CLASS: [], INACTIVE_CLASS: []}; preds, old, got = [], [], []
            for b in dl:
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    lg = m(b["image"].to(dev)).float()
                sm = torch.softmax(lg, 1)
                for c in probs: probs[c] += list(sm[:, c].cpu().numpy())
                preds += list(lg.argmax(1).cpu().numpy()); old += list(b["mask"].numpy()); got += list(b["stem"])
            assert got == stems
            r = {}
            for lab, gts in (("old_20211104", old), ("new_escdd", new)):
                r[lab] = {name: score(probs[c], preds, gts, c) for name, c in (("crack", CRACK_CLASS), ("inactive", INACTIVE_CLASS))}
            res[f"{split}/{run}"] = {"n": len(stems), "weights": key, "step": int(st.get("step", -1)), **r}
            o, n = r["old_20211104"]["crack"], r["new_escdd"]["crack"]
            print(f"{split:5s} {run:22s} crack IoU old {o['iou']:.3f} new {n['iou']:.3f} | AP {o['ap']:.3f}/{n['ap']:.3f} | "
                  f"relF1@2 {o['rel_f1_2']:.3f}/{n['rel_f1_2']:.3f} | inactive IoU {r['old_20211104']['inactive']['iou']:.3f}/"
                  f"{r['new_escdd']['inactive']['iou']:.3f}", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
