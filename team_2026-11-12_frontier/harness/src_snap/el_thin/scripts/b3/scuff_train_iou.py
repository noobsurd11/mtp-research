"""B3 readout on the train cells that carry scuff (spec_b3_scuff.md 6; protocol_thin_b3 s8: the 2k smoke and the per-seed
20k readout). No val / test / E1 cell is read.

Cells: the train cells whose ``--scuff-masks`` mask (default this worktree's data/labeled/masks_escdd_s) holds class 24
(12 cells, 3,246 px). Works for a B3 run (25 channels) and for its comparator (24 channels: scuff positions still come from
``--scuff-masks``). Read-only inference of a checkpoint (latest.pth by default; weak view; bf16 on CUDA, fp32 on CPU; the
model / student weights).

Reported, pooled over the cells and per cell:
- ``crack_on_scuff``: px predicted crack (argmax 14) on GT scuff px (both arm types);
- ``gt_scuff_predicted_as``: argmax histogram on GT scuff px;
- 25-channel runs only: scuff IoU / precision / recall (argmax 24 vs GT 24; pre-stated "< 0.10 IoU = not learned"),
  mean / p90 softmax p(scuff) on GT scuff px, mean p(scuff) on the other px of the same cells, their ratio, and the share
  of GT scuff px with p(scuff) > 0.1.

Usage: python scripts/b3/scuff_train_iou.py --run <run dir> [--ckpt latest.pth] [--device cuda|cpu] [--out f.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

SCUFF, CRACK = 24, 14


@torch.no_grad()
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ckpt", default="latest.pth")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--scuff-masks", default=str(ROOT / "data" / "labeled" / "masks_escdd_s"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    run, dev, msk = Path(a.run), torch.device(a.device), Path(a.scuff_masks)
    cfg = load_config(run / "config_used.yaml")
    d = cfg["data"]
    stems = [s for s in load_split(ROOT / "data" / "splits" / "train.txt")
             if (np.array(Image.open(msk / f"{s}.png")) == SCUFF).any()]
    ds = BenchmarkELDataset(ROOT / "data" / "labeled" / "images", msk, stems,
                            get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]),
                            num_classes=SCUFF + 1)
    st = torch.load(run / "checkpoints" / a.ckpt, map_location="cpu", weights_only=False)
    mcfg = {k: v for k, v in cfg["model"].items() if k != "encoder_init"}
    mcfg["encoder_weights"] = None
    m = build_model(mcfg).to(dev); m.load_state_dict(st["models"]["model"]); m.eval()
    nc = int(cfg["model"]["num_classes"])
    b3 = nc == SCUFF + 1
    tot = {"gt_px": 0, "tp": 0, "fp": 0, "fn": 0, "crack_on_scuff": 0}
    hist = np.zeros(nc, np.int64)
    p_sc, p_other, cells = [], [], {}
    for b in DataLoader(ds, batch_size=4, shuffle=False, num_workers=0):
        with torch.autocast(dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            lg = m(b["image"].to(dev)).float()
        pr = lg.argmax(1).cpu().numpy()
        ps = torch.softmax(lg, 1)[:, SCUFF].cpu().numpy() if b3 else None
        for i, (s, p, g) in enumerate(zip(b["stem"], pr, b["mask"].numpy())):
            gs = g == SCUFF
            c = {"gt_px": int(gs.sum()), "crack_on_scuff": int((p[gs] == CRACK).sum())}
            if b3:
                ps_ = p == SCUFF
                c.update(tp=int((gs & ps_).sum()), fp=int((~gs & ps_).sum()), fn=int((gs & ~ps_).sum()),
                         p_scuff_on_scuff_mean=float(ps[i][gs].mean()), p_scuff_other_mean=float(ps[i][~gs].mean()))
                p_sc.append(ps[i][gs]); p_other.append(ps[i][~gs])
                for k in ("tp", "fp", "fn"):
                    tot[k] += c[k]
            tot["gt_px"] += c["gt_px"]; tot["crack_on_scuff"] += c["crack_on_scuff"]
            hist += np.bincount(p[gs], minlength=nc)
            cells[s] = c
    res = {"run": run.name, "ckpt": a.ckpt, "step": int(st.get("step", -1)), "channels": nc, "n_cells": len(stems),
           "scuff_px": tot["gt_px"], "crack_on_scuff": tot["crack_on_scuff"],
           "gt_scuff_predicted_as": {int(k): int(v) for k, v in enumerate(hist) if v}}
    if b3:
        a_, o_ = np.concatenate(p_sc), np.concatenate(p_other)
        res.update(scuff_iou=tot["tp"] / max(tot["tp"] + tot["fp"] + tot["fn"], 1),
                   scuff_precision=tot["tp"] / max(tot["tp"] + tot["fp"], 1),
                   scuff_recall=tot["tp"] / max(tot["tp"] + tot["fn"], 1), tp=tot["tp"], fp=tot["fp"], fn=tot["fn"],
                   p_scuff_on_scuff_mean=float(a_.mean()), p_scuff_on_scuff_p90=float(np.percentile(a_, 90)),
                   p_scuff_other_mean=float(o_.mean()), p_scuff_ratio=float(a_.mean() / max(o_.mean(), 1e-12)),
                   share_scuff_px_p_gt_0_1=float((a_ > 0.1).mean()))
    res["cells"] = cells
    print(json.dumps({k: v for k, v in res.items() if k != "cells"}))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
