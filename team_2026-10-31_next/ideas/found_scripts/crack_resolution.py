"""found, 31 Oct 2026 (idea 6): how much GT crack survives at encoder strides 2, 4, 8, 16. CPU, masks only.
Sets: train (478), val (54); E1 (106, descriptive only, ignore px removed; split half-cut / full).
Masks: gaint el_f3/data/labeled/masks_escdd (= el-fault-detection/data/labeled/masks_escdd), ext117 masks/ignore,
copied to the scratchpad (path in argv[1]). Crack = class 14.
Measures per stride s (s x s blocks):
  lost_major : share of GT crack px in blocks where crack is < 50% of the block (a block-level majority label says "not crack")
  diluted25  : share of GT crack px in blocks where crack is < 25% of the block (area/bilinear downsampling dilutes it below 1/4)
  ceilIoU    : IoU of a perfect block-level predictor upsampled by nearest = |gt| / |up(maxpool_s(gt))| (pixel-IoU ceiling w/o sub-block localisation)
  mixed      : share of GT crack px in blocks that also hold a busbar, ribbon, spacing, gridline, inactive or padding px
  merged     : share of GT crack components (8-conn, >= 5 px) that share a maxpooled component with another GT component
Width: 2*EDT at skeleton px (px), median and p90.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

ROOT = Path(sys.argv[1])
CTX = Path("/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv")
CR = 14
OTHER = [1, 2, 4, 7, 9, 11, 15]  # sp_multi, sp_mono, ribbons, padding, busbars, inactive, gridline
S = (2, 4, 8, 16)


def blocks(a, s):
    h, w = a.shape
    return a[: h // s * s, : w // s * s].reshape(h // s, s, w // s, s)


def cell(gt, keep):
    g = (gt == CR) & keep
    n = int(g.sum())
    out = {"n": n}
    if n == 0:
        return out
    oth = np.isin(gt, OTHER) & keep
    lab, nc = ndi.label(g, np.ones((3, 3)))
    sizes = ndi.sum(np.ones_like(g), lab, range(1, nc + 1))
    big = {i + 1 for i, z in enumerate(sizes) if z >= 5}
    for s in S:
        b = blocks(g, s).mean((1, 3))  # crack fraction per block
        bu = np.kron(b, np.ones((s, s)))  # back to pixels
        gg = g[: bu.shape[0], : bu.shape[1]]
        out[f"lost_major{s}"] = int((gg & (bu < 0.5)).sum())
        out[f"diluted25_{s}"] = int((gg & (bu < 0.25)).sum())
        mp = b > 0
        out[f"up{s}"] = int(mp.sum()) * s * s
        ob = np.kron(blocks(oth, s).any((1, 3)), np.ones((s, s), bool))
        out[f"mixed{s}"] = int((gg & ob).sum())
        lab_s, _ = ndi.label(mp, np.ones((3, 3)))
        lab_up = np.kron(lab_s, np.ones((s, s), int))
        comp_to_s = {}
        L = lab[: lab_up.shape[0], : lab_up.shape[1]]
        for c in big:
            m = L == c
            if m.any():
                comp_to_s[c] = int(np.bincount(lab_up[m]).argmax())
        vals = list(comp_to_s.values())
        out[f"merged{s}"] = sum(1 for v in vals if vals.count(v) > 1)
        out[f"ncomp{s}"] = len(vals)
    sk = skeletonize(g)
    dt = ndi.distance_transform_edt(g)
    out["w"] = (2 * dt[sk]).tolist()
    return out


def run(name, items):
    tot = {}
    W = []
    for gt, keep in items:
        c = cell(gt, keep)
        W += c.pop("w", [])
        for k, v in c.items():
            tot[k] = tot.get(k, 0) + v
    n = tot.get("n", 0)
    print(f"\n{name}: cells {len(items)}, crack cells {sum(1 for gt, k in items if ((gt == CR) & k).any())}, GT crack px {n}")
    if n == 0:
        return
    W = np.array(W)
    print(f"  width (2*EDT on skeleton, px): median {np.median(W):.2f}, p75 {np.percentile(W, 75):.2f}, p90 {np.percentile(W, 90):.2f}")
    print("  stride  lost_major  diluted<25%  ceilIoU  mixed_with_other_class  merged_components")
    for s in S:
        print(f"  1/{s:<5d} {tot[f'lost_major{s}']/n:10.3f}  {tot[f'diluted25_{s}']/n:11.3f}  {n/tot[f'up{s}']:7.3f}  {tot[f'mixed{s}']/n:22.3f}  "
              f"{tot[f'merged{s}']}/{tot[f'ncomp{s}']} = {tot[f'merged{s}']/max(tot[f'ncomp{s}'],1):.3f}")


def load(p):
    return np.array(Image.open(p))


tr = [l.strip() for l in open(ROOT / "splits/train.txt") if l.strip()]
va = [l.strip() for l in open(ROOT / "splits/val.txt") if l.strip()]
M = ROOT / "labeled/masks_escdd"
run("train (478)", [(load(M / f"{s}.png"), np.ones((512, 512), bool)) for s in tr])
run("val (54)", [(load(M / f"{s}.png"), np.ones((512, 512), bool)) for s in va])
ctx = {}
for l in open(CTX):
    if l.strip():
        r = l.rstrip("\n").split("\t"); ctx[r[0]] = r[3] == "halfcut=1"
e1 = {s: (load(ROOT / "masks" / f"{s}.png"), ~(load(ROOT / "ignore" / f"{s}.png") > 0)) for s in ctx}
run("E1 all 106 (descriptive)", list(e1.values()))
run("E1 half-cut 58 (descriptive)", [v for s, v in e1.items() if ctx[s]])
run("E1 full 48 (descriptive)", [v for s, v in e1.items() if not ctx[s]])
