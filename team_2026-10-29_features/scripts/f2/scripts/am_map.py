#!/usr/bin/env python
"""Direction AM (directions.md §3.4): is the MIM reconstruction-error map a crack-recall aid? VAL ONLY, read-only.

Map: for each val cell, --passes random masks (ratio and patch of the MIM run, seeded by cell index); per pixel the
mean |reconstruction - per-patch-normalised target| over the passes where the pixel was masked (0 if never masked).
Scores:
  1. pixel AP of the map for val crack (all val pixels), against the crack base rate;
  2. threshold theta = the lowest map value whose relaxed precision (share of map > theta px within 2 px of GT crack)
     is >= 0.5 over val;
  3. for each given model run: its missed val crack components (8-connected, >= 20 px, relaxed recall@2 < 0.5 by the
     run's argmax) and the share of them the thresholded map recovers (>= 50% of the component's px within 2 px of
     map > theta). Reported per run and as the mean per group (A5c, SUP100).
Kill (pre-stated): recovered share < 0.05 at precision >= 0.5, or map AP <= 2x the base rate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pretrain.spark import SparKResNet, patchify, unpatchify  # noqa: E402

CRACK = 14
S8 = np.ones((3, 3), bool)


def load_spark(ckpt: Path, args_json: Path, dev) -> SparKResNet:
    import segmentation_models_pytorch as smp
    ar = json.loads(Path(args_json).read_text())
    enc = smp.encoders.get_encoder("resnet34", in_channels=1, depth=5, weights=None)
    m = SparKResNet(enc, list(enc.out_channels)[2:], width=ar["width"], patch=ar["patch"], mask_ratio=ar["mask_ratio"])
    st = torch.load(ckpt, map_location="cpu", weights_only=False)
    m.load_state_dict(st["model"])
    return m.to(dev).eval()


@torch.no_grad()
def error_map(m: SparKResNet, img: np.ndarray, passes: int, seed: int, dev) -> np.ndarray:
    x = torch.from_numpy(img[None, None].astype(np.float32) / 255.0)
    x = ((x - 0.5) / 0.25).to(dev)
    H, W = img.shape
    g = torch.Generator().manual_seed(seed)
    acc = torch.zeros(1, 1, H, W, device=dev); cnt = torch.zeros_like(acc)
    p = m.patch
    for _ in range(passes):
        mask = m.random_mask(1, H, W, generator=g, device=dev)
        with torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            _, rec = m(x, mask)
        inp, out = patchify(x.float(), p), patchify(rec.float(), p)
        tgt = (inp - inp.mean(-1, keepdim=True)) / (inp.var(-1, keepdim=True) + 1e-6) ** 0.5
        err = unpatchify((out - tgt).abs(), p, 1, H, W)
        hid = 1.0 - mask.float().repeat_interleave(p, 2).repeat_interleave(p, 3)
        acc += err * hid; cnt += hid
    return (acc / cnt.clamp(min=1)).squeeze().cpu().numpy()


def average_precision(score: np.ndarray, pos: np.ndarray) -> float:
    o = np.argsort(-score, kind="stable")
    y = pos[o].astype(np.float64)
    tp = np.cumsum(y); prec = tp / np.arange(1, len(y) + 1)
    return float((prec * y).sum() / max(y.sum(), 1))


@torch.no_grad()
def predict(run: Path, imgs: list[np.ndarray], dev) -> list[np.ndarray]:
    from src.models.model_factory import build_model
    from src.utils.config import load_config
    cfg = load_config(run / "config_used.yaml")
    st = torch.load(run / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st.get("step", -1)) == 20000, run
    mc = {k: v for k, v in cfg["model"].items() if k not in ("encoder_init", "decoder_init")}
    mc["encoder_weights"] = None
    m = build_model(mc).to(dev); m.load_state_dict(st["models"]["model"]); m.eval()
    out = []
    for i in range(0, len(imgs), 8):
        x = torch.from_numpy(np.stack(imgs[i:i + 8])[:, None].astype(np.float32) / 255.0)
        x = ((x - 0.5) / 0.25).to(dev)
        with torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            out += list((m(x).float().argmax(1) == CRACK).cpu().numpy())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mim_ckpt", required=True)
    ap.add_argument("--mim_args", required=True)
    ap.add_argument("--a5", nargs="*", default=[])
    ap.add_argument("--sup", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--passes", type=int, default=8)
    ap.add_argument("--max_cells", type=int, default=0, help="smoke only")
    a = ap.parse_args()
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    root = Path("data")
    stems = sorted(ln.strip() for ln in (root / "splits" / "val.txt").read_text().splitlines() if ln.strip())
    if a.max_cells:
        stems = stems[:a.max_cells]
    imgs = [np.array(Image.open(root / "labeled" / "images" / f"{s}.png").convert("L")) for s in stems]
    gts = [np.array(Image.open(root / "escdd_masks" / "val" / f"{s}.png")) == CRACK for s in stems]
    m = load_spark(Path(a.mim_ckpt), Path(a.mim_args), dev)
    maps = [error_map(m, im, a.passes, 1000 + i, dev) for i, im in enumerate(imgs)]
    del m
    allmap, allpos = np.concatenate([x.ravel() for x in maps]), np.concatenate([g.ravel() for g in gts])
    base = float(allpos.mean()); ap_map = average_precision(allmap, allpos)
    near_gt = [ndi.distance_transform_edt(~g) <= 2 if g.any() else np.zeros_like(g) for g in gts]
    allnear = np.concatenate([x.ravel() for x in near_gt])
    qs = np.quantile(allmap, np.linspace(0.5, 0.9999, 400))
    theta, best = None, None
    for t in qs:  # lowest threshold reaching relaxed precision 0.5
        sel = allmap > t
        if sel.sum() and allnear[sel].mean() >= 0.5:
            theta = float(t); best = float(allnear[sel].mean()); break
    res = dict(n_cells=len(stems), base_rate=base, map_ap=ap_map, ap_over_base=ap_map / max(base, 1e-12),
               theta=theta, rel_precision_at_theta=best, runs={})
    near_map = [ndi.distance_transform_edt(~(x > theta)) <= 2 if theta is not None else None for x in maps]
    for grp, runs in (("A5c", a.a5), ("SUP100", a.sup)):
        for run in map(Path, runs):
            preds = predict(run, imgs, dev)
            missed = rec = 0
            for g, p, nm in zip(gts, preds, near_map):
                lab, n = ndi.label(g, S8)
                dp = ndi.distance_transform_edt(~p) <= 2 if p.any() else np.zeros_like(p)
                for c in range(1, n + 1):
                    comp = lab == c
                    if comp.sum() < 20 or dp[comp].mean() >= 0.5:
                        continue
                    missed += 1
                    if nm is not None and nm[comp].mean() >= 0.5:
                        rec += 1
            res["runs"][run.name] = dict(group=grp, missed=missed, recovered=rec, share=rec / max(missed, 1))
            print(run.name, res["runs"][run.name], flush=True)
    for grp in ("A5c", "SUP100"):
        v = [r["share"] for r in res["runs"].values() if r["group"] == grp]
        res[f"{grp}_mean_share"] = float(np.mean(v)) if v else None
    res["kill"] = bool(theta is None or ap_map <= 2 * base or
                       all((res.get(f"{g}_mean_share") or 0) < 0.05 for g in ("A5c", "SUP100")))
    Path(a.out).write_text(json.dumps(res, indent=1))
    print({k: v for k, v in res.items() if k != "runs"})


if __name__ == "__main__":
    main()
