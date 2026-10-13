"""Qualitative panel (descriptive): predictions on fixed test cells against the revised labels.

Cells fixed by GT area only (prediction-independent): the 2 test cells with the most inactive px and the 2 with the most
crack px. Seed 3 for every arm (the first seed all four arms share in cv02 el_p13). Crack red, inactive blue.
Usage: .venv/bin/python scripts/qualitative_panel.py --npz results/qualitative/preds_p13_s3.npz --out results/qualitative/fig_qualitative_5pct.png
"""
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("--npz", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
Z = np.load(a.npz)
stems = [k.split("/", 1)[1] for k in Z.files if k.startswith("img/")]
runs = list(dict.fromkeys(k.split("/")[1] for k in Z.files if k.startswith("pred/")))
LAB = {"p13_A_5pct_s3": "supervised 5% (A5c)", "p13_CsM_5pct_s3": "SSL 5%: tolerant PL + CutMix (CsM5)",
       "p13_BsM_5pct_s3": "SSL 5%: hard PL + CutMix (BsM5)", "p16_A_100pct_s3": "supervised 100%"}
CR, IN = 14, 11


def overlay(img, m):
    g = img.astype(float); g = (g - g.min()) / max(np.ptp(g), 1); rgb = np.stack([g] * 3, -1) * 0.8
    rgb[m == CR] = [1, 0.1, 0.1]; rgb[m == IN] = rgb[m == IN] * 0.4 + np.array([0.1, 0.4, 1.0]) * 0.6
    return rgb


def iou(p, g, c):
    u = ((p == c) | (g == c)).sum()
    return ((p == c) & (g == c)).sum() / u if u else float("nan")


fig, axs = plt.subplots(len(stems), 2 + len(runs), figsize=(2.6 * (2 + len(runs)), 2.7 * len(stems)))
for i, s in enumerate(stems):
    img, gt = Z[f"img/{s}"], Z[f"gt/{s}"]
    if img.ndim == 3: img = img[..., 0]
    ys, xs = np.where(gt != 7)  # crop to the cell (padding is class 7); scores use the same crop, padding holds no crack/inactive
    cy, cx = slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1)
    img, gt = img[cy, cx], gt[cy, cx]
    axs[i, 0].imshow(overlay(img, np.zeros_like(gt))); axs[i, 0].set_ylabel(s, fontsize=7)
    axs[i, 1].imshow(overlay(img, gt))
    for j, r in enumerate(runs):
        p = Z[f"pred/{r}/{s}"][cy, cx]
        axs[i, 2 + j].imshow(overlay(img, p))
        axs[i, 2 + j].set_xlabel(f"crack IoU {iou(p, gt, CR):.2f}  inactive IoU {iou(p, gt, IN):.2f}", fontsize=6.5)
    if i == 0:
        for j, t in enumerate(["EL image", "revised labels"] + [LAB.get(r, r) for r in runs]):
            axs[0, j].set_title(t, fontsize=7.5)
for ax in axs.ravel():
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle("Test cells with the most inactive (rows 1-2) and crack (rows 3-4) pixels; seed 3; crack red, inactive blue. "
             "Per-cell IoU under each panel", fontsize=8.5)
fig.tight_layout(); fig.savefig(a.out, dpi=170); print("wrote", a.out)
