"""B1 out-of-fold label audit of train (coach_strategy.md appendix, exact rule). CPU inference only; no mask is edited.
Auditor set: 5 run dirs (final weights, step 20,000 asserted), cells = train cells outside the set's labelled list (+ the 54
val cells as the descriptive base rate). 512 native, no TTA, fp32 softmax. GT = labeled/masks_escdd; raw E-SCDD masks
(escdd_masks/{train,val}) give the scuff (25) / star (28) px.
Excluded px (never flagged): GT 7, 5, 21, 22; raw scuff/star px. Crack: GT 10 and px within 2 px of GT crack. Inactive: GT 17
and px within 3 px of the GT inactive region (its edge band outside).
ML (possible missed label), class c: 8-connected components of {all 5 auditors p_c >= 0.9, GT != c, not excluded},
kept if >= 20 px (crack) / >= 200 px (inactive). FL (possible false label): GT components of c (same floors, excluded px
removed) where every auditor has relaxed recall@2 < 0.1 on it and mean p_c over it < 0.1.
Usage: python b1_audit.py --code EL_ROOT --set NAME --runs DIR x5 --labeled LIST --out OUTDIR [--cells-limit N]
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument("--code", required=True)
ap.add_argument("--set", required=True)
ap.add_argument("--runs", nargs=5, required=True)
ap.add_argument("--labeled", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--threads", type=int, default=16)
ap.add_argument("--cells-limit", type=int, default=0)
a = ap.parse_args()
sys.path.insert(0, a.code)
from src.models.model_factory import build_model  # noqa: E402
from src.utils.config import load_config  # noqa: E402

torch.set_num_threads(a.threads)
D = Path(a.code) / "data"
IMG, GT = D / "labeled" / "images", D / "labeled" / "masks_escdd"
RAW = Path("/home/noob/work/el-fault-detection/data/escdd_masks")
OUT = Path(a.out); (OUT / "cache").mkdir(parents=True, exist_ok=True)
rd = lambda p: [ln.strip() for ln in open(p) if ln.strip()]
train, val = rd(D / "splits" / "train.txt"), rd(D / "splits" / "val.txt")
twins = set(rd(D / "splits" / "d7_twin_train_cells.txt"))
lab = set(rd(a.labeled))
assert lab <= set(train)
cells = [(s, "D7 twin" if s in twins else "train") for s in train if s not in lab] + [(s, "val") for s in val]
if a.cells_limit:
    cells = cells[:a.cells_limit] + cells[-2:]
CRACK, INACT = 14, 11
DISK = lambda r: (lambda y, x: (x * x + y * y) <= r * r)(*np.ogrid[-r:r + 1, -r:r + 1])
S8 = np.ones((3, 3), bool)

models = []
for r in a.runs:
    r = Path(r)
    st = torch.load(r / "checkpoints" / "latest.pth", map_location="cpu", weights_only=False)
    assert int(st["step"]) == 20000, (r, st["step"])
    mc = {k: v for k, v in load_config(r / "config_used.yaml")["model"].items() if k not in ("encoder_init", "decoder_init")}
    mc["encoder_weights"] = None
    m = build_model(mc); m.load_state_dict(st["models"]["model"]); m.eval(); models.append(m)
print(f"{a.set}: {len(models)} auditors loaded; {len(cells)} cells "
      f"({sum(c[1] != 'val' for c in cells)} train OOF incl. {sum(c[1] == 'D7 twin' for c in cells)} twins, "
      f"{sum(c[1] == 'val' for c in cells)} val)", flush=True)


def raw_mask(stem, role):
    p = RAW / ("val" if role == "val" else "train") / f"{stem}.png"
    return np.array(Image.open(p)) if p.exists() else None


def comps(mask, floor):
    lb, n = ndimage.label(mask, S8)
    if n == 0:
        return lb, []
    sz = np.bincount(lb.ravel())[1:]
    return lb, [i + 1 for i in range(n) if sz[i] >= floor]


rows, t0 = [], time.time()
for i, (stem, role) in enumerate(cells):
    x = np.array(Image.open(IMG / f"{stem}.png").convert("L"), np.float32) / 255.0
    xt = torch.from_numpy((x - 0.5) / 0.25)[None, None]
    with torch.no_grad():
        probs = [torch.softmax(m(xt).float(), 1)[0].numpy() for m in models]
    P = np.stack(probs)                       # (5, C, H, W)
    am = P.argmax(1)                          # (5, H, W)
    cons = P.mean(0).argmax(0).astype(np.uint8)
    g = np.array(Image.open(GT / f"{stem}.png"))
    raw = raw_mask(stem, role)
    ss = (np.isin(raw, (25, 28)) if raw is not None and raw.shape == g.shape else np.zeros_like(g, bool))
    ex = np.isin(g, (7, 5, 21, 22)) | ss
    flags = np.zeros(g.shape, np.uint8)       # bit0 ML crack, bit1 FL crack, bit2 ML inactive, bit3 FL inactive
    for c, floor, extra_ex, bit in ((CRACK, 20, (g == 10) | ndimage.binary_dilation(g == CRACK, DISK(2)), 0),
                                    (INACT, 200, (g == 17) | ndimage.binary_dilation(g == INACT, DISK(3)), 2)):
        mn = P[:, c].min(0)
        lb, keep = comps((mn >= 0.9) & (g != c) & ~ex & ~extra_ex, floor)
        ml = np.isin(lb, keep) if keep else np.zeros(g.shape, bool)
        if ml.any():
            rows.append(dict(cell=stem, source=stem.split("_")[0], role=role, auditor_set=a.set, cls="crack" if c == CRACK else "inactive",
                             flag="ML", px=int(ml.sum()), components=len(keep)))
            flags |= (ml.astype(np.uint8) << bit)
        lb, keep = comps((g == c) & ~ex, floor)
        fl = np.zeros(g.shape, bool); nfl = 0
        for k in keep:
            cm = lb == k
            bad = all(ndimage.binary_dilation(am[j] == c, DISK(2))[cm].mean() < 0.1 and P[j, c][cm].mean() < 0.1
                      for j in range(len(models)))
            if bad:
                fl |= cm; nfl += 1
        if nfl:
            rows.append(dict(cell=stem, source=stem.split("_")[0], role=role, auditor_set=a.set, cls="crack" if c == CRACK else "inactive",
                             flag="FL", px=int(fl.sum()), components=nfl))
            flags |= (fl.astype(np.uint8) << (bit + 1))
    np.savez_compressed(OUT / "cache" / f"{a.set}_{stem}.npz", cons=cons, flags=flags)
    if (i + 1) % 25 == 0:
        print(f"  {i + 1}/{len(cells)} cells, {time.time() - t0:.0f} s", flush=True)
with open(OUT / f"b1_flags_{a.set}.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, ["cell", "source", "role", "auditor_set", "cls", "flag", "px", "components"], delimiter="\t")
    w.writeheader(); w.writerows(rows)
summ = {}
for r in rows:
    k = f"{r['role'] if r['role'] == 'val' else 'train'}/{r['cls']}/{r['flag']}"
    s = summ.setdefault(k, {"cells": 0, "px": 0, "components": 0}); s["cells"] += 1; s["px"] += r["px"]; s["components"] += r["components"]
json.dump({"set": a.set, "runs": a.runs, "labeled": a.labeled, "n_cells": len(cells), "summary": summ},
          open(OUT / f"b1_summary_{a.set}.json", "w"), indent=1)
print(json.dumps(summ, indent=1)); print(f"done {time.time() - t0:.0f} s")
