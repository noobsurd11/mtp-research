"""Label-free per-channel mean / sd of the two GPU cue definitions (spec arms crackcue_input, liot_input) over the 532 cv5v2
pool images. I in [0, 1]. Torch-free numpy re-implementation of the spec pseudo-code."""
import os, numpy as np
from PIL import Image
from scipy import ndimage as ndi
B = os.path.expanduser("~/mtp/research/team_2026-11-12_frontier/benchmark")
IMG = os.path.expanduser("~/mtp/datasets/BenchmarkELimages/dataset_20211104")
rows = [l.rstrip("\n").split("\t") for l in open(f"{B}/cells.tsv")]; h = rows[0]
pool = [dict(zip(h, r))["stem"] for r in rows[1:] if dict(zip(h, r))["bench_set"].startswith("cv5v2:")]
assert len(pool) == 532
def path(s):
    for d in ("images_train_original", "images_val"):
        p = f"{IMG}/{d}/{s}.png"
        if os.path.exists(p): return p
def cue(I):
    mp = I.reshape(64, 8, 64, 8).max((1, 3))           # max_pool2d(k=8, s=8)
    Bc = ndi.zoom(mp, 8, order=1, grid_mode=True, mode="nearest")  # ~ bilinear x8, align_corners=False
    return np.clip((Bc - I) / (Bc + 0.02), 0, 1)
def liot(I):
    P = np.pad(I, 8, mode="edge"); out = []
    for dirn in ((0, -1), (0, 1), (-1, 0), (1, 0)):   # left, right, top, bottom
        c = np.zeros(I.shape, np.float32)
        for d in range(1, 9):
            dy, dx = dirn[0] * d, dirn[1] * d
            c += (I > P[8 + dy:520 + dy, 8 + dx:520 + dx]) * 2 ** (d - 1)
        out.append(c / 255.0)
    return out
acc = {k: [0.0, 0.0, 0] for k in ["cue", "liot_l", "liot_r", "liot_t", "liot_b"]}
for s in pool:
    I = np.asarray(Image.open(path(s)).convert("L"), np.float32) / 255.0
    for k, v in zip(acc, [cue(I)] + liot(I)):
        acc[k][0] += v.sum(); acc[k][1] += (v.astype(np.float64) ** 2).sum(); acc[k][2] += v.size
for k, (s1, s2, n) in acc.items():
    m = s1 / n; print(f"{k}: mean {m:.4f} sd {np.sqrt(s2 / n - m * m):.4f}")
