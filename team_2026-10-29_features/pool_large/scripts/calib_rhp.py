"""Reproduce the team's r_hp (neardup.json lab_pairs) on local labelled images; pick the matching variant.

Usage: python -I calib_rhp.py <neardup.json> [n_pairs]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path("/home/yugma/mtp/datasets/BenchmarkELimages/dataset_20211104")
SPLIT = {"train": "images_train_original", "val": "images_val", "test": "images_test"}


def load(stem, split):
    return np.asarray(Image.open(ROOT / SPLIT[split] / f"{stem}.png").convert("L"), dtype=np.float64)


def down(a, n, how):
    if how == "box":
        f = a.shape[0] // n
        return a.reshape(n, f, n, f).mean(axis=(1, 3))
    m = {"bilinear": Image.BILINEAR, "pil_box": Image.BOX, "lanczos": Image.LANCZOS}[how]
    return np.asarray(Image.fromarray(a.astype(np.uint8)).resize((n, n), m), dtype=np.float64)


def desc(a, n, how, sig, mode):
    d = down(a, n, how)
    h = d - ndimage.gaussian_filter(d, sig, mode=mode)
    return (h - h.mean()) / (h.std() + 1e-8)


def r(a, b):
    return float((a * b).mean())


if __name__ == "__main__":
    nd = json.load(open(sys.argv[1]))
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    pairs = nd["lab_pairs"][:: max(1, len(nd["lab_pairs"]) // n)][:n]
    imgs = {}
    for p in pairs:
        for s, sp in ((p["a"], p["sa"]), (p["b"], p["sb"])):
            if s not in imgs:
                imgs[s] = load(s, sp)
    best = []
    for how in ("box", "pil_box", "bilinear"):
        for sig in (2, 3, 4, 5, 8):
            for mode in ("reflect", "nearest"):
                err = [abs(r(desc(imgs[p["a"]], 128, how, sig, mode), desc(imgs[p["b"]], 128, how, sig, mode)) - p["r_hp"])
                       for p in pairs]
                best.append((max(err), how, sig, mode))
    best.sort()
    for b in best[:6]:
        print(f"max |err| {b[0]:.2e}  resize={b[1]} sigma={b[2]} mode={b[3]}")
