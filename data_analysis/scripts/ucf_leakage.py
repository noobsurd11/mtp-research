"""Q2 leakage / same-physical-cell search across the release (and the 5,213 Test_Images cells outside it).

Descriptor per image: grayscale, area-resized to 64x64, high-pass residual (minus Gaussian sigma 4), standardised.
A plain standardised thumbnail is kept as well. Pairwise normalised cross-correlation (NCC) by chunked matrix
products; top-5 neighbours per image are stored for: release vs release, extra vs release.

Usage: python -I ucf_leakage.py <UCF root> <out dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from ucf_common import dump, pairs  # noqa: E402

root, od = Path(sys.argv[1]), Path(sys.argv[2])
S = 64


def desc(p: Path) -> tuple[np.ndarray, np.ndarray]:
    im = Image.open(p).convert("L").resize((S, S), Image.BOX)
    a = np.asarray(im, np.float32)
    hp = a - ndi.gaussian_filter(a, 4)
    out = []
    for x in (a, hp):
        x = x - x.mean()
        out.append((x / (np.linalg.norm(x) + 1e-6)).ravel())
    return out[0], out[1]


rel = [(s, n) for s in ("train", "test") for n, _ in pairs(root, s)]
relset = {n for _, n in rel}
extra = sorted(p.name for p in (root / "Test_Images").iterdir() if p.name not in relset)
A_r, H_r = zip(*[desc(root / "training" / "data" / s / "images" / n) for s, n in rel])
A_r, H_r = np.stack(A_r), np.stack(H_r)
A_x, H_x = zip(*[desc(root / "Test_Images" / n) for n in extra])
A_x, H_x = np.stack(A_x), np.stack(H_x)
np.savez_compressed(od / "ucf_desc.npz", A_r=A_r, H_r=H_r, A_x=A_x, H_x=H_x)


def topk(Q: np.ndarray, D: np.ndarray, k: int = 5, exclude_self: bool = False) -> tuple[np.ndarray, np.ndarray]:
    idx = np.zeros((len(Q), k), np.int32)
    val = np.zeros((len(Q), k), np.float32)
    for i in range(0, len(Q), 1000):
        sim = Q[i:i + 1000] @ D.T
        if exclude_self:
            for j in range(sim.shape[0]):
                sim[j, i + j] = -9
        part = np.argpartition(-sim, k, axis=1)[:, :k]
        pv = np.take_along_axis(sim, part, 1)
        o = np.argsort(-pv, 1)
        idx[i:i + 1000] = np.take_along_axis(part, o, 1)
        val[i:i + 1000] = np.take_along_axis(pv, o, 1)
    return idx, val


res = {"release_names": [n for _, n in rel], "release_splits": [s for s, _ in rel], "extra_names": extra}
for tag, Q, D, ex in (("RR_hp", H_r, H_r, True), ("RR_plain", A_r, A_r, True), ("XR_hp", H_x, H_r, False), ("XX_hp", H_x, H_x, True)):
    i, v = topk(Q, D, 5, ex)
    res[tag] = {"idx": i.tolist(), "val": np.round(v, 4).tolist()}
    print(tag, "top1 quantiles", np.quantile(v[:, 0], [.5, .9, .99, .999]).round(3))
dump(res, od / "ucf_leakage_neighbours.json")
