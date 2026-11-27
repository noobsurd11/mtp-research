"""B3 masks ``masks_escdd_s`` (spec_b3_scuff.md 3): masks_escdd with the raw E-SCDD scuff px (class 25) set to the new
class 24 "scuff", in train cells only. Val and test masks are byte-identical copies. Deterministic.

Inputs: --base (masks_escdd, 24-class), --raw (raw E-SCDD train masks with class 25), --splits (train/val/test.txt).
Outputs in --out: one PNG per stem of train + val + test (copied bytes, or re-encoded mode-L PNG for a changed cell),
``../masks_escdd_s.diff.tsv`` (stem, scuff px, px taken from each masks_escdd class), ``../masks_escdd_s.MANIFEST.md5``
(md5 of every output PNG) and ``../masks_escdd_s.summary.json``.

Usage: python scripts/b3/build_masks_escdd_s.py --base data/labeled/masks_escdd \
         --raw /home/noob/work/el-fault-detection/data/escdd_masks/train --splits data/splits \
         --out data/labeled/masks_escdd_s
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

SCUFF_RAW, SCUFF_NEW = 25, 24


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--splits", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    base, raw, out = Path(a.base), Path(a.raw), Path(a.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} exists and is not empty; refusing to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    split = {s: [l.strip() for l in open(Path(a.splits) / f"{s}.txt") if l.strip()] for s in ("train", "val", "test")}
    rows, n_train_raw = [], 0
    for sp, stems in split.items():
        for s in stems:
            src = base / f"{s}.png"
            rp = raw / f"{s}.png"
            sc = None
            if sp == "train" and rp.exists():
                n_train_raw += 1
                r = np.array(Image.open(rp))
                sc = r == SCUFF_RAW
            if sc is not None and sc.any():
                m = np.array(Image.open(src))
                assert m.shape == sc.shape and m.dtype == np.uint8 and m.max() < SCUFF_NEW, (s, m.dtype, m.max())
                u, c = np.unique(m[sc], return_counts=True)
                m2 = m.copy(); m2[sc] = SCUFF_NEW
                Image.fromarray(m2, mode="L").save(out / f"{s}.png")
                rows.append((s, int(sc.sum()), {int(k): int(v) for k, v in zip(u, c)}))
            else:
                shutil.copyfile(src, out / f"{s}.png")  # unchanged: same bytes
    # checks: every unchanged file is byte-identical, every changed one differs only on scuff px (now 24)
    changed = {r[0] for r in rows}
    for sp, stems in split.items():
        for s in stems:
            if s in changed:
                m, m2 = np.array(Image.open(base / f"{s}.png")), np.array(Image.open(out / f"{s}.png"))
                d = m != m2
                assert sp == "train" and (m2[d] == SCUFF_NEW).all() and int((m2 == SCUFF_NEW).sum()) == \
                    dict((r[0], r[1]) for r in rows)[s]
            else:
                assert md5(base / f"{s}.png") == md5(out / f"{s}.png"), s
    tot = sum(r[1] for r in rows)
    frm: dict[int, int] = {}
    for r in rows:
        for k, v in r[2].items():
            frm[k] = frm.get(k, 0) + v
    (out.parent / f"{out.name}.diff.tsv").write_text(
        "stem\tscuff_px\tfrom_classes\n" + "".join(f"{s}\t{n}\t{json.dumps(f)}\n" for s, n, f in rows))
    files = sorted(out.glob("*.png"))
    (out.parent / f"{out.name}.MANIFEST.md5").write_text("".join(f"{md5(f)}  {f.name}\n" for f in files))
    summ = {"n_files": len(files), "n_train": len(split["train"]), "n_val": len(split["val"]),
            "n_test": len(split["test"]), "train_cells_with_raw_mask": n_train_raw, "cells_changed": len(rows),
            "scuff_px": tot, "from_classes": {str(k): v for k, v in sorted(frm.items())},
            "manifest_md5": md5(out.parent / f"{out.name}.MANIFEST.md5")}
    (out.parent / f"{out.name}.summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
