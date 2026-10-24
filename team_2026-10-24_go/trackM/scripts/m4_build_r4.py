"""Track M R4 data build (laptop): the 107 leakage-free E-SCDD cells (MC data_addendum.md) with masks mapped to our
24-class scheme. Writes <out>/images/<stem>.png (copied bytes, unchanged), <out>/masks_escdd/<stem>.png (uint8 L, ids 0-23),
<out>/train_extra.txt, <out>/class_hist.tsv (cells and px per class, before and after mapping), <out>/md5.txt.
Mapping (MC ruling, 24 Oct): 24 -> 2 (sp mono), 29 -> 1 (sp multi), 25-28 -> 255 (ignore; needs data.mask_ignore_value=255,
el_m commit 0642889); 0-23 unchanged.
Usage: .venv/bin/python -I m4_build_r4.py <eligible.tsv> <escdd_full dir> <out dir>
"""
import csv, hashlib, shutil, sys
from pathlib import Path

import numpy as np
from PIL import Image

MAP = {24: 2, 29: 1, 25: 255, 26: 255, 27: 255, 28: 255}
tsv, src, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
(out / "images").mkdir(parents=True, exist_ok=True); (out / "masks_escdd").mkdir(exist_ok=True)
rows = list(csv.DictReader(open(tsv), delimiter="\t"))
assert len(rows) == 107, len(rows)
before, after = np.zeros((256, 2), np.int64), np.zeros((256, 2), np.int64)
md5 = []
for r in rows:
    st = r["stem"]
    sp = next(s for s in ("train", "val", "test") if (src / f"el_masks_{s}" / f"{st}.png").exists())
    im, mk = src / f"el_images_{sp}" / f"{st}.png", src / f"el_masks_{sp}" / f"{st}.png"
    m = np.array(Image.open(mk)); assert m.shape == (512, 512) and m.dtype == np.uint8
    b = np.bincount(m.ravel(), minlength=256); before[:, 0] += b > 0; before[:, 1] += b
    o = m.copy()
    for k, v in MAP.items():
        o[m == k] = v
    assert set(np.unique(o).tolist()) <= set(range(24)) | {255}
    b = np.bincount(o.ravel(), minlength=256); after[:, 0] += b > 0; after[:, 1] += b
    shutil.copyfile(im, out / "images" / f"{st}.png")
    Image.fromarray(o, mode="L").save(out / "masks_escdd" / f"{st}.png")
    g = np.array(Image.open(out / "images" / f"{st}.png").convert("L")); assert g.shape == (512, 512)
    for f in (out / "images" / f"{st}.png", out / "masks_escdd" / f"{st}.png"):
        md5.append(f"{hashlib.md5(f.read_bytes()).hexdigest()}  {f.relative_to(out)}")
(out / "train_extra.txt").write_text("\n".join(r["stem"] for r in rows) + "\n")
(out / "md5.txt").write_text("\n".join(md5) + "\n")
with open(out / "class_hist.tsv", "w") as f:
    f.write("class\tcells_before\tpx_before\tcells_after\tpx_after\n")
    for c in range(256):
        if before[c, 1] or after[c, 1]:
            f.write(f"{c}\t{before[c, 0]}\t{before[c, 1]}\t{after[c, 0]}\t{after[c, 1]}\n")
print(open(out / "class_hist.tsv").read())
