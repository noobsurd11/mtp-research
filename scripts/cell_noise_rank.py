"""Rank the 582 BenchmarkEL 20211104 cells by pixel noise: robust sigma (1.4826 * median |x - median5x5(x)|) of the
grey image. Used in P16 to show how unusual test cell CSIR_00070_r8_c4 is.
Usage: .venv/bin/python scripts/cell_noise_rank.py | tee results/p16/cell_noise_rank.txt
"""
import glob, os
import numpy as np
from PIL import Image
from scipy import ndimage

R = os.path.expanduser("~/mtp/datasets/BenchmarkELimages/dataset_20211104")
rows = []
for d, sp in (("images_train_original", "train"), ("images_val", "val"), ("images_test", "test")):
    for f in sorted(glob.glob(f"{R}/{d}/*.png")):
        im = np.asarray(Image.open(f).convert("L"), dtype=np.float32)
        rows.append((os.path.basename(f)[:-4], sp, float(np.median(np.abs(im - ndimage.median_filter(im, size=5))) * 1.4826)))
rows.sort(key=lambda r: -r[2])
v = np.array([r[2] for r in rows])
print(f"{len(rows)} cells; noise sigma median {np.median(v):.2f}, 95th percentile {np.quantile(v, 0.95):.2f}, max {v.max():.2f}")
print("| rank | cell | split | noise sigma |\n|---|---|---|---|")
for i, r in enumerate(rows[:10]):
    print(f"| {i + 1} | {r[0]} | {r[1]} | {r[2]:.2f} |")
