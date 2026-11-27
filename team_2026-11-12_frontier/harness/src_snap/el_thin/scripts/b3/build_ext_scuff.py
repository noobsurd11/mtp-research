"""B3 descriptive secondary (spec_b3_scuff.md 4.1): binary scuff masks of the E1 (ext117, 106 evaluated) cells from the raw
E-SCDD masks (class 25). One PNG (0 / 255, mode L) per E1 cell that has scuff; cells without scuff get no file. Writes
MANIFEST.md5 and summary.json. Runs where the raw E-SCDD masks are (the laptop's escdd_full); numpy + PIL only.

Usage: python build_ext_scuff.py --stems stems_eval.txt --raw-glob '~/mtp/datasets/escdd_full/el_masks_*/*.png' --out DIR
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stems", required=True)
    ap.add_argument("--raw-glob", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} exists and is not empty")
    out.mkdir(parents=True, exist_ok=True)
    stems = [l.strip() for l in open(a.stems) if l.strip()]
    raw = {os.path.basename(p)[:-4]: p for p in glob.glob(os.path.expanduser(a.raw_glob))}
    rows, missing = {}, []
    for s in stems:
        if s not in raw:
            missing.append(s); continue
        sc = np.asarray(Image.open(raw[s])) == 25
        if sc.any():
            Image.fromarray((sc * 255).astype(np.uint8), mode="L").save(out / f"{s}.png")
            rows[s] = int(sc.sum())
    man = "".join(f"{hashlib.md5((out / f'{s}.png').read_bytes()).hexdigest()}  {s}.png\n" for s in sorted(rows))
    (out / "MANIFEST.md5").write_text(man)
    summ = {"n_stems": len(stems), "n_with_raw_mask": len(stems) - len(missing), "missing_raw": missing,
            "n_with_scuff": len(rows), "scuff_px": sum(rows.values()), "per_cell": rows,
            "manifest_md5": hashlib.md5(man.encode()).hexdigest()}
    (out / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "per_cell"}))


if __name__ == "__main__":
    main()
