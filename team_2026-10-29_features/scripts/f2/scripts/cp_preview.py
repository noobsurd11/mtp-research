#!/usr/bin/env python
"""F2 / CP5 preview (CPU, read-only): library recount on the server masks (spec_cp5 §7.3) and a PNG of N stream
samples before augmentation (background, composed image, target map: crack red, ring green, ignore black), plus
per-sample stats. Usage: python scripts/cp_preview.py --out DIR [--n 32] (A5c data opts; cp lists as in the protocol)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.copy_paste import build_cp_stream, load_grey  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--n", type=int, default=32)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--pool_list", default="/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt")
ap.add_argument("--heldout", default="/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt")
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
cfg = {"data": {"root": "data", "mask_subdir": "labeled/masks_escdd", "labeled_fraction": 0.05, "input_size": 512},
       "cp": {"lambda": 1.0, "batch": 4, "bg_pool_list": a.pool_list, "heldout_list": a.heldout,
              "bg_train_exclude": "data/splits/d7_twin_train_cells.txt"}}
info = {"labeled_split": "data/splits/seed0/labeled_5pct.txt", "split_seed": 0}
stream, records, summary = build_cp_stream(cfg, info, a.seed, 0, False)
ds = stream.dataset
kept = [r for r in records if r["kept"]]
lib_txt = "".join(f"{r['stem']}\t{r['cid']}\t{r['area']}\t{r['contrast']}\n" for r in kept)
(out / "cp_library_kept.tsv").write_text(lib_txt)
(out / "cp_library_all.json").write_text(json.dumps({"summary": summary, "components": records}, indent=1))
reasons = {}
for r in records:
    reasons[r["reason"] or "kept"] = reasons.get(r["reason"] or "kept", 0) + 1
print("summary", summary)
print("candidates by outcome", reasons)
print("kept per source", {s: sum(1 for r in kept if r["stem"].startswith(s)) for s in ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE")})
print("kept list md5", hashlib.md5(lib_txt.encode()).hexdigest())
rows, stats = [], []
for i in range(a.n):
    img, tmap, st, p = ds.compose(1_000_003 * a.seed + i)
    bg = load_grey(Path(p))
    col = np.zeros(tmap.shape + (3,), np.uint8); col[tmap == 1] = (255, 0, 0); col[tmap == 2] = (0, 200, 0)
    g3 = lambda x: np.repeat(x[..., None], 3, 2)
    rows.append(np.concatenate([g3(bg), g3(img), col], 1)[::2, ::2])
    stats.append(dict(i=i, bg=str(p), **st))
grid = np.concatenate([np.concatenate(rows[k:k + 4], 1) for k in range(0, len(rows), 4)], 0)
Image.fromarray(grid).save(out / "cp_preview.png")
(out / "cp_preview_stats.json").write_text(json.dumps(stats, indent=1))
for k in ("placed", "fails", "crack_px", "ring_px", "s", "ring_med", "redraws"):
    v = np.array([s[k] for s in stats], float)
    print(f"{k}: mean {v.mean():.2f} min {v.min():.2f} max {v.max():.2f}")
print("pool backgrounds", sum(1 for s in stats if "unlabeled/" in s["bg"]), "of", len(stats))
