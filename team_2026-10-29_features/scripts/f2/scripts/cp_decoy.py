#!/usr/bin/env python
"""F2 / CP5 seam/decoy control (spec_cp5 §7.5, review E3). Read-only inference.

On the held-out pool cells (never backgrounds), one composite per cell is made twice with identical placements:
(i) real: the library components as in training; (ii) decoy: the same mask shape M with a residual taken from a
crack-free spot of the same source cell (same normalised-convolution recipe, no crack, edge or >20% inactive in the
spot's dilate(M, 8)). For each checkpoint: share of placed-M pixels predicted crack (argmax 14) on the real composite,
on the decoy composite, and on the untouched background at the same pixels. A shortcut is flagged if a CP checkpoint's
decoy rate exceeds 2x the matched A5c checkpoint's decoy rate or 0.05 absolute.
Usage: python scripts/cp_decoy.py --runs DIR [DIR ...] --out JSON [--heldout LIST] [--seed 0]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.copy_paste import (CRACK, EDGE_CLASSES, INACTIVE, build_library, compose_one, dilate,  # noqa: E402
                                 load_grey, prepare_variants, read_list, robust_sd)


def decoy_items(kept: list[dict], img_dir: Path, msk_dir: Path, seed: int = 0, tries: int = 2000) -> list:
    """Per kept component: a decoy with M's shape and a residual from a crack-free spot of the same cell, or None."""
    out = []
    for it in kept:
        src = load_grey(img_dir / f"{it['stem']}.png").astype(np.float64)
        msk = np.array(Image.open(msk_dir / f"{it['stem']}.png"))
        H, W = src.shape
        Mc = np.pad(it["M"], 8)
        h, w = Mc.shape
        rng = np.random.default_rng([seed, int(hashlib.md5(it["stem"].encode()).hexdigest()[:8], 16), it["cid"]])
        got = None
        for _ in range(tries):
            y, x = int(rng.integers(0, H - h + 1)), int(rng.integers(0, W - w + 1))
            M = np.zeros((H, W), bool); M[y:y + h, x:x + w] = Mc
            D1, T, D8 = dilate(M, 1), dilate(M, 2), dilate(M, 8)
            R8 = D8 & ~D1
            if (msk[D8] == CRACK).any() or np.isin(msk[D8], EDGE_CLASSES).any() or (msk[R8] == INACTIVE).mean() > 0.2:
                continue
            wgt = 1.0 - T.astype(np.float64)
            bg = ndi.gaussian_filter(src * wgt, 3.0) / np.maximum(ndi.gaussian_filter(wgt, 3.0), 1e-6)
            r = np.where(T, src - bg, 0.0)[y:y + h, x:x + w][8:-8, 8:-8]
            got = dict(stem=it["stem"], cid=it["cid"], area=it["area"], sd_src=robust_sd(src[R8]),
                       M=it["M"].copy(), r=r.astype(np.float32), at=(y, x))
            break
        out.append(got)
    return out


@torch.no_grad()
def crack_rate(model, imgs: list[np.ndarray], Ms: list[np.ndarray], dev) -> float:
    hit = tot = 0
    for i in range(0, len(imgs), 8):
        x = torch.from_numpy(np.stack(imgs[i:i + 8])[:, None].astype(np.float32) / 255.0)
        x = ((x - 0.5) / 0.25).to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            pred = model(x).float().argmax(1).cpu().numpy()
        for p, M in zip(pred, Ms[i:i + 8]):
            hit += int((p[M] == CRACK).sum()); tot += int(M.sum())
    return hit / max(tot, 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--heldout", default="/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt")
    ap.add_argument("--labeled", default="data/splits/seed0/labeled_5pct.txt")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    root = Path("data")
    img_dir, msk_dir = root / "labeled" / "images", root / "labeled" / "masks_escdd"
    kept, _ = build_library(img_dir, msk_dir, read_list(Path(a.labeled)))
    dec = decoy_items(kept, img_dir, msk_dir, a.seed)
    pairs = [(k, d) for k, d in zip(kept, dec) if d is not None]
    real_lib, dec_lib = [p[0] for p in pairs], [p[1] for p in pairs]
    rv, dv = [prepare_variants(x) for x in real_lib], [prepare_variants(x) for x in dec_lib]
    held = read_list(Path(a.heldout))
    comp_r, comp_d, comp_b, Ms = [], [], [], []
    for i, rel in enumerate(held):
        bg = load_grey(root / rel)
        r1 = compose_one(bg, real_lib, rv, np.random.default_rng([a.seed, 17, i]))
        r2 = compose_one(bg, dec_lib, dv, np.random.default_rng([a.seed, 17, i]))
        if r1 is None or r2 is None:
            continue
        assert r1[3] == r2[3], "placements differ between real and decoy"
        assert np.array_equal(r1[1] == 1, r2[1] == 1)
        comp_r.append(r1[0]); comp_d.append(r2[0]); comp_b.append(bg); Ms.append(r1[1] == 1)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    from src.models.model_factory import build_model
    from src.utils.config import load_config
    res = {"n_cells": len(Ms), "n_components": len(pairs), "n_no_decoy_spot": sum(d is None for d in dec),
           "m_px": int(sum(M.sum() for M in Ms)), "runs": {}}
    for run in map(Path, a.runs):
        cfg = load_config(run / "config_used.yaml")
        st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
        mcfg = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}
        mcfg["encoder_weights"] = None
        m = build_model(mcfg).to(dev); m.load_state_dict(st["models"]["model"]); m.eval()
        res["runs"][run.name] = {"step": int(st.get("step", -1)), "real": crack_rate(m, comp_r, Ms, dev),
                                 "decoy": crack_rate(m, comp_d, Ms, dev), "background": crack_rate(m, comp_b, Ms, dev)}
        print(run.name, res["runs"][run.name], flush=True)
        del m; torch.cuda.empty_cache()
    Path(a.out).write_text(json.dumps(res, indent=1))
    print({k: v for k, v in res.items() if k != "runs"})


if __name__ == "__main__":
    main()
