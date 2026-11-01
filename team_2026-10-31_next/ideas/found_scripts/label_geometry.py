"""found, 31 Oct 2026 (idea 10): how SAM-friendly are crack, inactive and scuff regions, and how noisy are Hanifi's
SAM-assisted (_rf) crack labels? CPU, local E-SCDD copy (~/mtp/datasets/escdd_full; 30-class masks: crack 14, inactive 11,
scuff 25). Sets: the 693 real non-_rf cells (Pratt 20221008 labels) and the 117 real _rf cells (Hanifi, SAM-assisted).
Per labelled component (8-conn, >= 20 px unless stated):
  contrast  = |mean(I in comp) - mean(I in a 3-8 px ring outside it, unlabelled-by-this-class px only)| / robust sd of the cell
  thinness  = skeleton px / area (1 = 1-px line, ~0.5 = 2-px, small = blob)
  branch    = skeleton branch points per 100 skeleton px (tree-likeness proxy)
Per crack cell: components, share of components < 5 px (specks), share of crack px in components < 20 px.
"""
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

R = Path.home() / "mtp/datasets/escdd_full"
CLS = {"crack": 14, "inactive": 11, "scuff": 25}
K8 = np.ones((3, 3))


def cells():
    out = []
    for sp in ("train", "val", "test"):
        for f in sorted(os.listdir(R / f"el_masks_{sp}")):
            if not re.match(r"^(CSIR|ARTS|BMRK|CFVS|SDLE)_", f):
                continue  # synthetic images have numeric names
            out.append((f[:-4], R / f"el_images_{sp}" / f, R / f"el_masks_{sp}" / f))
    return out


def img_of(p):
    a = np.array(Image.open(p))
    return (a.mean(2) if a.ndim == 3 else a).astype(np.float32)


stats = {g: {c: {"contrast": [], "thin": [], "branch": [], "area": [], "dgl": []} for c in CLS} for g in ("pratt", "rf")}
crk = {g: {"cells": 0, "comps": 0, "specks": 0, "px": 0, "px_small": 0, "comps_per_cell": []} for g in ("pratt", "rf")}
for stem, ip, mp in cells():
    g = "rf" if stem.endswith("_rf") else "pratt"
    m = np.array(Image.open(mp))
    if m.ndim == 3:
        m = m[..., 0]
    if not ip.exists():
        continue
    I = img_of(ip)
    sd = max(1.4826 * np.median(np.abs(I - np.median(I))), 0.5 * float(I.std()), 1.0)  # MAD can be 0 on flat cells
    for cname, cid in CLS.items():
        mask = m == cid
        if not mask.any():
            continue
        lab, n = ndi.label(mask, K8)
        sizes = ndi.sum(np.ones_like(mask), lab, range(1, n + 1))
        if cname == "crack":
            c = crk[g]; c["cells"] += 1; c["comps"] += n; c["specks"] += int((sizes < 5).sum())
            c["px"] += int(mask.sum()); c["px_small"] += int(sizes[sizes < 20].sum()); c["comps_per_cell"].append(n)
        for i, z in enumerate(sizes, 1):
            if z < 20:
                continue
            comp = lab == i
            ring = ndi.binary_dilation(comp, iterations=8) & ~ndi.binary_dilation(comp, iterations=3) & ~mask
            if ring.sum() < 10:
                continue
            sk = skeletonize(comp)
            nsk = max(int(sk.sum()), 1)
            nb = ndi.convolve(sk.astype(int), K8, mode="constant") - 1
            bp = int((sk & (nb >= 3)).sum())
            s = stats[g][cname]
            d = abs(I[comp].mean() - I[ring].mean()); s["contrast"].append(d / sd); s.setdefault("dgl", []).append(d)
            s["thin"].append(nsk / z); s["branch"].append(100 * bp / nsk); s["area"].append(z)

for g in ("pratt", "rf"):
    c = crk[g]
    print(f"\n[{g}] crack cells {c['cells']}: components/cell median {np.median(c['comps_per_cell']):.0f} "
          f"(p90 {np.percentile(c['comps_per_cell'], 90):.0f}, max {max(c['comps_per_cell'])}); specks (<5 px) "
          f"{c['specks']}/{c['comps']} = {c['specks']/max(c['comps'],1):.2f} of components; crack px in comps < 20 px {c['px_small']/max(c['px'],1):.3f}")
    print("  class      n_comp>=20  contrast/sd(med, p25)  |dGL|(med, p25)  thinness(med)  share_with_branchpt  area(med)")
    for cname in CLS:
        s = stats[g][cname]
        if not s["area"]:
            print(f"  {cname:9s} 0"); continue
        print(f"  {cname:9s} {len(s['area']):10d}  {np.median(s['contrast']):8.2f}, {np.percentile(s['contrast'], 25):5.2f}      "
              f"{np.median(s['dgl']):6.1f}, {np.percentile(s['dgl'], 25):5.1f}   {np.median(s['thin']):12.2f}  {np.mean(np.array(s['branch'])>0):19.2f}  {np.median(s['area']):9.0f}")
