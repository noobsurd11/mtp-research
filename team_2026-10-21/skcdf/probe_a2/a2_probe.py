"""Agent 2 probe (b), inference only: confident crack misses on the 448-cell unlabelled pool, true miss vs offset.

Thresholds locked in skcdf/second_opinion_a2.md (addendum) before running.
Run from /tmp/noob_el/el_sk1 (code 0ea71df):
  python a2_probe.py --out probe.json
Per run: GT crack px, bin-0 (p_crack < 0.001), true miss (bin-0 and > 2 px from any argmax-crack px in the cell),
offset (bin-0 within 2 px), confident-bg PL (max p >= 0.95 and argmax bg) among true misses; split by source.
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage
from torch.utils.data import DataLoader

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from rescore_logit_adjust import log_prior  # noqa: E402
from src.data.augmentations import get_weak_augmentation  # noqa: E402
from src.data.benchmark_el import BenchmarkELDataset  # noqa: E402
from src.data.class_info import CRACK_CLASS  # noqa: E402
from src.data.splits import load_split  # noqa: E402
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

DATA = ROOT / "data"
IMG, MSK_CODED, MSK_NEW = DATA / "labeled" / "images", DATA / "labeled" / "masks_coded", DATA / "labeled" / "masks_escdd"
RUNS = ([("A5c", f"/tmp/noob_el/el_p11/experiments/p12_A_5pct_s{i}") for i in range(3)]
        + [("A5c", f"/tmp/noob_el/el_p13/experiments/p13_A_5pct_s{i}") for i in (3, 4)]
        + [("BsD5", f"/tmp/noob_el/el_sk1/experiments/sk1_BsD_5pct_s{i}") for i in range(5)]
        + [("BsDBn5", f"/tmp/noob_el/el_sk1/experiments/sk1_BsDBn_5pct_s{i}") for i in range(5)])
SRC_A = ("CSIR", "ARTS")


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    dev = torch.device("cuda")
    excl = set(load_split(ROOT / "d7_twin_train_cells.txt"))
    stems = sorted(s for s in load_split(DATA / "splits" / "seed0" / "unlabeled_5pct.txt") if s not in excl)
    assert len(stems) == 448, len(stems)
    gts = {s: np.array(Image.open(MSK_NEW / f"{s}.png")) for s in stems}
    res = {"n_cells": len(stems), "runs": {}}
    for arm, rdir in RUNS:
        rdir = Path(rdir)
        cfg = load_config(rdir / "config_used.yaml"); d = cfg["data"]
        st = torch.load(rdir / "checkpoints" / "latest.pth", map_location=dev, weights_only=False)
        key = "teacher" if cfg.get("method") == "mean_teacher" and "teacher" in st["models"] else "model"
        m = build_model(cfg["model"]).to(dev); m.load_state_dict(st["models"][key]); m.eval()
        lp, _ = log_prior(cfg); lp = lp.to(dev).view(1, -1, 1, 1)
        ds = BenchmarkELDataset(IMG, MSK_CODED, stems, get_weak_augmentation(d.get("mean", [0.5]), d.get("std", [0.25]), d["input_size"]))
        dl = DataLoader(ds, batch_size=8, shuffle=False, num_workers=2)
        variants = {arm: 0.0} if arm != "BsD5" else {"BsD5": 0.0, "BsD5+LA": 1.0}
        acc = {v: {g: np.zeros(5, np.int64) for g in ("all", "CSIR/ARTS", "CFVS/BMRK/SDLE")} for v in variants}
        for b in dl:
            with torch.autocast("cuda", dtype=torch.bfloat16):
                lg = m(b["image"].to(dev)).float()
            for v, tau in variants.items():
                sm = torch.softmax(lg - tau * lp, 1)
                pc = sm[:, CRACK_CLASS].cpu().numpy(); am = sm.argmax(1).cpu().numpy(); mx = sm.max(1).values.cpu().numpy()
                for i, s in enumerate(b["stem"]):
                    t = gts[s] == CRACK_CLASS
                    if not t.any():
                        continue
                    pred = am[i] == CRACK_CLASS
                    dist = ndimage.distance_transform_edt(~pred) if pred.any() else np.full(t.shape, np.inf)
                    bin0 = t & (pc[i] < 0.001)
                    true_miss = bin0 & (dist > 2)
                    cbg = (mx[i] >= 0.95) & (am[i] == 0)
                    row = np.array([t.sum(), bin0.sum(), true_miss.sum(), (bin0 & (dist <= 2)).sum(), (true_miss & cbg).sum()])
                    grp = "CSIR/ARTS" if s.startswith(SRC_A) else "CFVS/BMRK/SDLE"
                    acc[v]["all"] += row; acc[v][grp] += row
        for v in variants:
            run = f"{v}:{rdir.name}"
            res["runs"][run] = {"arm": v, "weights": key, "step": int(st.get("step", -1)),
                                **{g: dict(zip(["gt", "bin0", "true_miss", "offset", "true_miss_confbg"], map(int, x)))
                                   for g, x in acc[v].items()}}
            r = res["runs"][run]["all"]
            print(f"{run:34s} step {res['runs'][run]['step']} gt {r['gt']} bin0 {r['bin0']/r['gt']:.3f} "
                  f"true_miss {r['true_miss']/r['gt']:.3f} offset {r['offset']/r['gt']:.3f} "
                  f"confbg|true_miss {r['true_miss_confbg']/max(r['true_miss'],1):.3f}", flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1)); print("wrote", a.out)


if __name__ == "__main__":
    main()
