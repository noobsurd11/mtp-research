"""found, 1 Nov 2026 (HC review, protocol_HC section 3 label mapping, judge condition 4). CPU, laptop, no model, no E1.
Pixel check of the E-SCDD spacing-class mapping against raw E-SCDD index masks (HF snt-ubix/escdd, laptop
datasets/escdd_full, L-mode labels 0-29):
  (a) Hanifi _rf (calib's 106-cell build, gaint calib/data/rf): raw 29 -> 1, raw 24 -> 2, raw 25-28 -> ignore, else equal;
  (b) house train masks (labeled/masks_escdd, the masks HC copies the gap band from): raw 29 -> ?, raw 24 -> ?, 25-28 -> ?
      (expect 29 -> 1 and 24 -> 2), and no label > 23.
Usage: python -I hc_labelmap_check.py RAW_ROOT LM_DIR OUT.json"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

raw_root, lm, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
RAW = {}
for sp in ("train", "val", "test"):
    for f in (raw_root / f"el_masks_{sp}").glob("*.png"):
        RAW.setdefault(f.stem, f)


def load(f):
    a = np.array(Image.open(f))
    assert a.ndim == 2, (f, a.shape)
    return a


def table(pairs):
    """pairs: (raw, mapped, ignore or None). Returns {raw_class: {mapped_class or 'ign': px}} for raw >= 24, and the
    number of px with raw <= 23 that changed (outside ignore)."""
    t, changed_le23, ign_outside_2528 = {}, 0, 0
    for r, m, ig in pairs:
        ig = np.zeros_like(r, bool) if ig is None else ig
        for c in range(24, 30):
            sel = r == c
            if not sel.any():
                continue
            d = t.setdefault(c, {})
            n_ig = int((sel & ig).sum())
            if n_ig:
                d["ign"] = d.get("ign", 0) + n_ig
            v, n = np.unique(m[sel & ~ig], return_counts=True)
            for vv, nn in zip(v, n):
                d[int(vv)] = d.get(int(vv), 0) + int(nn)
        le = (r <= 23) & ~ig
        changed_le23 += int((r[le] != m[le]).sum())
        ign_outside_2528 += int((ig & ~((r >= 25) & (r <= 28))).sum())
    return {str(k): {str(kk): vv for kk, vv in sorted(v.items(), key=lambda x: str(x[0]))} for k, v in sorted(t.items())}, \
        changed_le23, ign_outside_2528


R = {}
# (a) _rf
stems = [l.strip() for l in open(lm / "rf" / "stems_eval.txt") if l.strip()]
pairs, miss, maxlab = [], [], 0
for s in stems:
    if s not in RAW:
        miss.append(s); continue
    r, m = load(RAW[s]), load(lm / "rf" / "masks" / f"{s}.png")
    ig = load(lm / "rf" / "ignore" / f"{s}.png") > 0
    maxlab = max(maxlab, int(m.max()))
    pairs.append((r, m, ig))
t, ch, igo = table(pairs)
R["rf"] = {"n_cells": len(pairs), "missing_raw": miss, "raw_ge24_to_mapped_px": t, "px_raw_le23_changed": ch,
           "ignore_px_outside_raw25_28": igo, "max_label": maxlab,
           "cells_with_raw29": sum(int((p[0] == 29).any()) for p in pairs),
           "cells_with_raw24": sum(int((p[0] == 24).any()) for p in pairs)}
print("rf", json.dumps(R["rf"]), flush=True)

# (b) house train masks
train = [l.strip() for l in open(lm / "house" / "train.txt") if l.strip()]
pairs, miss, maxlab = [], [], 0
for s in train:
    m = load(lm / "house" / "masks" / f"{s}.png")
    maxlab = max(maxlab, int(m.max()))
    if s not in RAW:
        miss.append(s); continue
    pairs.append((load(RAW[s]), m, None))
t, ch, _ = table(pairs)
R["house_train"] = {"n_cells": len(train), "with_raw": len(pairs), "missing_raw": miss, "raw_ge24_to_mapped_px": t,
                    "px_raw_le23_changed": ch, "max_label": maxlab,
                    "cells_with_raw29": sum(int((p[0] == 29).any()) for p in pairs),
                    "cells_with_raw24": sum(int((p[0] == 24).any()) for p in pairs)}
print("house_train", json.dumps(R["house_train"]), flush=True)
json.dump(R, open(out, "w"), indent=1)
print("DONE")
