#!/usr/bin/env python3
"""bench_release e2e check (22 Nov 2026): oracle dumps for OPEN pool folds (cv5v3_f<k>), to check that the staged scorer
runs from the staged lists. pred = the v1.1 strict mask (ignore px carry their v1 label and are not scored), optionally
shifted by --shift px to the right. Pool cells only; no sealed set is touched (dumpfmt refuses sealed names anyway).
Run (CPU): python -I make_oracle_dumps.py --code <files/code> --lists <files/lists> --masks <masks_v11 dir> --out <dir> --run <id> [--shift 1]
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
for k in ("--code", "--lists", "--masks", "--out", "--run"):
    ap.add_argument(k, required=True)
ap.add_argument("--shift", type=int, default=0)
ap.add_argument("--fold", type=int, default=0)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
sys.path.insert(0, a.code)
from bench import dumpfmt, sets  # noqa: E402

js = json.load(open(Path(a.lists) / "cv5v3.json"))
K = a.fold
f0 = js["folds"][K]
held = f0["heldout"]
assert sets.stems_md5(held) == f0["heldout_md5"]
root = Path(a.out) / "roots" / f"cv5v3_v11_f{K}" / "splits"
root.mkdir(parents=True, exist_ok=True)
if not (root / "test.txt").exists():
    (root / "test.txt").write_text("\n".join(held) + "\n")
set_dir = Path(a.out) / "dumps" / "e2e" / "oracle" / a.run / f"cv5v3_f{K}"
cells = {}
for s in held:
    m = np.array(Image.open(Path(a.masks) / "masks_strict" / f"{s}.png"))
    assert m.ndim == 2 and m.max() < 24
    pred = np.roll(m, a.shift, axis=1) if a.shift else m
    oth = np.where(pred == 14, 0, pred).astype(np.uint8)
    mc = np.where(pred == 14, 5.0, -5.0)
    cells[s] = dumpfmt.write_cell(set_dir / f"{s}.npz", pred, oth, mc, (pred == 14).astype(np.float32),
                                  (pred == 11).astype(np.float32))
meta = {k: None for k in dumpfmt.MANIFEST_KEYS}
meta.update({"bench": "e2e", "method": "oracle", "run_id": a.run, "seed": a.seed, "split_def": f"cv5v3_v11_f{K}",
             "split_md5": "n/a", "fold": K, "set": f"cv5v3_f{K}", "stems_md5": sets.stems_md5(held), "code_repo": "release_v1",
             "code_commit": "staged", "checkpoint": "none", "checkpoint_md5": "none", "step": 0, "weights_key": "none",
             "device": "cpu", "precision": "fp32", "tta": "none", "decision_rule": "argmax", "card": "none",
             "card_md5": "none", "writer": "make_oracle_dumps.py", "set_kind": "open", "opening": None})
dumpfmt.write_manifest(set_dir, meta, cells)
print(f"wrote {len(cells)} oracle cells (shift {a.shift}) to {set_dir}")
