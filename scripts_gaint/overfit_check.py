"""P1 overfit check: what caps crack when the model is asked to memorise a handful of training images?

Protocol: ~/mtp/research/protocols/P1_overfit_check.md (locked before running).

10 train images that contain crack (the first 10, sorted, of ``data/splits/seed0/labeled_10pct.txt`` with crack
pixels), batch 8 drawn with replacement, 3,000 steps, Adam lr 1e-3 (200-step linear warm-up, then constant),
weight decay 1e-4, grad clip 1, U-Net++ exactly as in the SL runs (base.yaml model section), training seed 0.

  A  weighted CE (weights of the 10 % subset, as SL-10)   no augmentation       bf16 autocast
  B  plain CE                                             no augmentation       bf16
  C  plain CE + soft Dice (crack, inactive)               no augmentation       bf16
  D  plain CE                                             no augmentation       fp32
  E  weighted CE                                          training augmentation bf16

Every 500 steps, eval mode, on the same 10 images with the evaluation transform: crack and inactive IoU, precision,
recall, pixel AP (dataset-level, ``src/evaluation/threshold_free.py``), and relaxed (Euclidean 1 px and 2 px)
precision / recall / F1. Final overlays for 3 images. Step 0 checks that the loader returns the raw files exactly.

Usage::

    .venv/bin/python scripts/overfit_check.py --arm A
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from scipy import ndimage as ndi
from torch.utils.data import DataLoader, RandomSampler

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from src.data.augmentations import get_strong_augmentation, get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset, load_index_mask  # noqa: E402
from src.data.class_info import CRACK_CLASS, INACTIVE_CLASS, get_ce_weights  # noqa: E402
from src.data.class_stats import count_class_pixels  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.evaluation.threshold_free import score_images, summarise  # noqa: E402
from src.losses.weighted_ce import WeightedCrossEntropyLoss  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

ARMS = {
    "A": dict(loss="wce", aug=False, amp=True),
    "B": dict(loss="ce", aug=False, amp=True),
    "C": dict(loss="ce_dice", aug=False, amp=True),
    "D": dict(loss="ce", aug=False, amp=False),
    "E": dict(loss="wce", aug=True, amp=True),
}
DATA = ROOT / "data"
IMG, MSK = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded"


def pick_images(n: int = 10) -> list[str]:
    stems = sorted(load_split(DATA / "splits" / "seed0" / "labeled_10pct.txt"))
    out = [s for s in stems if (load_index_mask(MSK / f"{s}.png") == CRACK_CLASS).any()]
    return out[:n]


def relaxed(pred: np.ndarray, gt: np.ndarray, r: float) -> tuple[int, int, int, int]:
    """Counts for relaxed precision / recall: (pred within r of gt, n pred, gt within r of pred, n gt)."""
    if pred.any():
        d_gt = ndi.distance_transform_edt(~gt) if gt.any() else np.full(gt.shape, np.inf)
        p_hit = int((d_gt[pred] <= r).sum())
    else:
        p_hit = 0
    if gt.any():
        d_pr = ndi.distance_transform_edt(~pred) if pred.any() else np.full(gt.shape, np.inf)
        g_hit = int((d_pr[gt] <= r).sum())
    else:
        g_hit = 0
    return p_hit, int(pred.sum()), g_hit, int(gt.sum())


@torch.no_grad()
def predict(model, loader, dev, amp) -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    model.eval()
    preds, gts, stems = [], [], []
    for b in loader:
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=amp):
            lg = model(b["image"].to(dev))
        preds += list(lg.float().argmax(1).cpu().numpy())
        gts += list(b["mask"].numpy())
        stems += list(b["stem"])
    return preds, gts, stems


def evaluate(model, loader, dev, amp) -> dict:
    s = score_images(model, loader, dev, amp=amp, amp_dtype=torch.bfloat16)
    out = summarise(s["conf"].sum(0), s["hist"].sum(0))
    preds, gts, _ = predict(model, loader, dev, amp)
    for name, c in (("crack", CRACK_CLASS), ("inactive", INACTIVE_CLASS)):
        for r in (1, 2):
            tot = np.zeros(4, np.int64)
            for p, g in zip(preds, gts):
                tot += np.array(relaxed(p == c, g == c, r))
            P = tot[0] / tot[1] if tot[1] else float("nan")
            R = tot[2] / tot[3] if tot[3] else float("nan")
            out[name][f"relaxed_p{r}"] = float(P)
            out[name][f"relaxed_r{r}"] = float(R)
            out[name][f"relaxed_f1_{r}"] = float(2 * P * R / (P + R)) if P + R > 0 else 0.0
    return out


def overlay(model, loader, dev, amp, out_dir: Path, arm: str, stems_keep: list[str]) -> None:
    preds, gts, stems = predict(model, loader, dev, amp)
    for p, g, s in zip(preds, gts, stems):
        if s not in stems_keep:
            continue
        img = np.array(Image.open(IMG / f"{s}.png").convert("L"))
        panels = [np.stack([img] * 3, -1)]
        for c, (tp, fp, fn) in ((CRACK_CLASS, ((0, 255, 0), (255, 0, 0), (0, 128, 255))),
                                (INACTIVE_CLASS, ((0, 255, 255), (255, 0, 255), (255, 255, 0)))):
            o = np.stack([img] * 3, -1).copy()
            pc, gc = p == c, g == c
            o[pc & gc], o[pc & ~gc], o[~pc & gc] = tp, fp, fn
            panels.append(o)
        Image.fromarray(np.concatenate(panels, 1).astype(np.uint8)).save(out_dir / f"overlay_{arm}_{s}.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--eval_every", type=int, default=500)
    ap.add_argument("--out", default="reports/overfit_check")
    a = ap.parse_args()
    arm = ARMS[a.arm]
    out_dir = ROOT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT / "configs" / "supervised.yaml")
    d = cfg["data"]
    mean, std, size = d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]
    dev = torch.device("cuda")
    torch.manual_seed(0)
    np.random.seed(0)
    torch.backends.cudnn.benchmark = True

    stems = pick_images(10)
    crack_px = {s: int((load_index_mask(MSK / f"{s}.png") == CRACK_CLASS).sum()) for s in stems}
    eval_ds = BenchmarkELDataset(IMG, MSK, stems, get_weak_augmentation(mean, std, size))
    eval_loader = DataLoader(eval_ds, batch_size=5, shuffle=False, num_workers=2)

    # step 0: the evaluation loader returns the raw files (mask exactly, image up to normalisation)
    align = {}
    for i, s in enumerate(stems):
        smp = eval_ds[i]
        raw_m = load_index_mask(MSK / f"{s}.png")
        raw_i = np.array(Image.open(IMG / f"{s}.png").convert("L"), dtype=np.float32)
        back = smp["image"][0].numpy() * std[0] * 255.0 + mean[0] * 255.0
        align[s] = {"mask_equal": bool((smp["mask"].numpy() == raw_m).all()), "image_max_abs_diff": float(np.abs(back - raw_i).max())}
    assert all(v["mask_equal"] for v in align.values()), align

    counts = count_class_pixels(MSK, load_split(DATA / "splits" / "seed0" / "labeled_10pct.txt"))
    weights = get_ce_weights(counts, cap_ratio=cfg["loss"].get("weight_cap_ratio", 10.0)).to(dev)
    crit = WeightedCrossEntropyLoss(weight=weights if arm["loss"] == "wce" else None).to(dev)

    if arm["aug"]:
        train_ds = BenchmarkELDataset(IMG, MSK, stems, get_strong_augmentation(size, mean, std))
        loader = DataLoader(train_ds, batch_size=8, num_workers=4, drop_last=True,
                            sampler=RandomSampler(train_ds, replacement=True, num_samples=8 * a.steps,
                                                  generator=torch.Generator().manual_seed(0)))
        it = iter(loader)
        next_batch = lambda: next(it)  # noqa: E731
    else:
        X = torch.stack([eval_ds[i]["image"] for i in range(len(stems))]).to(dev)
        Y = torch.stack([eval_ds[i]["mask"] for i in range(len(stems))]).to(dev)
        g = torch.Generator(device="cpu").manual_seed(0)

        def next_batch():
            idx = torch.randint(0, len(stems), (8,), generator=g)
            return {"image": X[idx], "mask": Y[idx]}

    model = build_model(cfg["model"]).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 200))
    evals, train_log, t0 = [], [], time.time()
    for step in range(1, a.steps + 1):
        model.train()
        b = next_batch()
        x, y = b["image"].to(dev, non_blocking=True), b["mask"].to(dev, non_blocking=True).long()
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=arm["amp"]):
            logits = model(x)
        loss = crit(logits, y)
        if arm["loss"] == "ce_dice":
            prob = torch.softmax(logits.float(), 1)
            dl = []
            for c in (CRACK_CLASS, INACTIVE_CLASS):
                pc, yc = prob[:, c], (y == c).float()
                dl.append(1 - (2 * (pc * yc).sum() + 1) / (pc.sum() + yc.sum() + 1))
            loss = loss + torch.stack(dl).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 100 == 0:
            train_log.append({"step": step, "loss": float(loss)})
        if step % a.eval_every == 0 or step == a.steps:
            r = evaluate(model, eval_loader, dev, arm["amp"])
            evals.append({"step": step, **r})
            cr, ia = r["crack"], r["inactive"]
            print(f"[{a.arm}] step {step} loss {float(loss):.4f} | crack IoU {cr['iou']:.3f} P {cr['precision']:.3f} "
                  f"R {cr['recall']:.3f} AP {cr['ap']:.3f} relF1@1 {cr['relaxed_f1_1']:.3f} @2 {cr['relaxed_f1_2']:.3f} | "
                  f"inactive IoU {ia['iou']:.3f} AP {ia['ap']:.3f} | {time.time() - t0:.0f}s", flush=True)
    keep = sorted(stems, key=lambda s: -crack_px[s])[:3]
    overlay(model, eval_loader, dev, arm["amp"], out_dir, a.arm, keep)
    res = {"arm": a.arm, **arm, "steps": a.steps, "images": stems, "crack_px": crack_px, "alignment": align,
           "class_weights": weights.tolist(), "crack_weight": float(weights[CRACK_CLASS]), "bg_weight": float(weights[0]),
           "evals": evals, "train_log": train_log, "overlay_images": keep, "seconds": round(time.time() - t0)}
    (out_dir / f"arm_{a.arm}.json").write_text(json.dumps(res, indent=1))
    print(f"wrote {out_dir / f'arm_{a.arm}.json'}")


if __name__ == "__main__":
    main()
