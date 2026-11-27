"""elbench x3: cell metadata (bench_data/meta/cells.tsv), label sets for scoring, bootstrap groups. Stdlib + numpy + PIL.

Label sets (which ground truth a held-out cell is scored against):
  set       = what bench/sets.py resolves for the set name (cv5v2_f<k>: v1.1 masks + ignore; others: their own GT). Default.
  v11       = <MASKS_V11>/masks (255 at ignore px) + <MASKS_V11>/ignore (ignore px not scored); MANIFEST.md5 md5 pinned.
  v1        = <labeled>/masks_escdd, no ignore (the label-fix ablation view).
  manifest  = taken from the run's dump manifest: the data root the run was trained on (manifest key split_def) names its
              label set (cv5v2_v11_f<k> -> v11, cv5v2_v1_f<k> or b6_root_<k> -> v1); anything else refuses.
cells.tsv subsets: src:<SOURCE>, type:<cell_type>, crackfree / crack (v1.1 crack px on the cell), flag:<f> and -flagged.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
from PIL import Image

from . import sets

META = Path(os.environ.get("BENCH_META", "/home/noob/work/bench_data/meta"))
CELLS_TSV = META / "cells.tsv"
GROUPS_TSV = META / "cv5v2_groups.tsv"
CELLS_MD5 = "a50521b4"            # prefix, BUILD_LOG 13 Nov 09:32
GROUPS_MD5 = "e44f0668"
MASKS_V11_MANIFEST_MD5 = "9c0e0687"
LABEL_SETS = ("set", "v11", "v1", "manifest")
SOURCES = ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE")


def md5(p) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def _tsv(p) -> list[dict]:
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def load_cells(path=None, check_md5: bool = True) -> dict[str, dict]:
    path = Path(path or CELLS_TSV)
    if check_md5 and path == CELLS_TSV:
        assert md5(path).startswith(CELLS_MD5), (path, md5(path))
    return {r["stem"]: r for r in _tsv(path)}


def load_groups(path=None, col: str = "group", check_md5: bool = True) -> dict[str, str]:
    path = Path(path or GROUPS_TSV)
    if check_md5 and path == GROUPS_TSV:
        assert md5(path).startswith(GROUPS_MD5), (path, md5(path))
    return {r["stem"]: r[col] for r in _tsv(path)}


def source(stem: str) -> str:
    s = stem.split("_")[0]
    if s not in SOURCES:
        raise ValueError(f"unknown source {s!r} of {stem}")
    return s


def flags(row: dict) -> list[str]:
    return [f for f in (row.get("flags") or "").replace(",", ";").split(";") if f]


def subsets(stems: list[str], cells: dict[str, dict]) -> dict:
    """Named stem filters from cells.tsv (every stem must be in it)."""
    miss = [s for s in stems if s not in cells]
    assert not miss, f"{len(miss)} stems not in cells.tsv, e.g. {miss[:3]}"
    out = {}
    for so in sorted({cells[s]["source"] for s in stems}):
        out[f"src:{so}"] = lambda s, so=so: cells[s]["source"] == so
    for ct in sorted({cells[s]["cell_type"] or "unknown" for s in stems}):
        out[f"type:{ct}"] = lambda s, ct=ct: (cells[s]["cell_type"] or "unknown") == ct
    out["crackfree"] = lambda s: int(cells[s]["crack_px_v11"] or 0) == 0
    out["crack"] = lambda s: int(cells[s]["crack_px_v11"] or 0) > 0
    out["-flagged"] = lambda s: not flags(cells[s])
    for f in sorted({f for s in stems for f in flags(cells[s])}):
        out[f"flag:{f}"] = lambda s, f=f: f in flags(cells[s])
    return out


# ---------------------------------------------------------------- label sets
def label_set_of_root(root: str) -> str | None:
    b = Path(str(root).rstrip("/")).name
    if "_v11_f" in b:
        return "v11"
    if "_v1_f" in b or b.startswith("b6_root_"):
        return "v1"
    return None


def gt_source(set_name: str, labels: str = "set", manifest: dict | None = None, opening: str | None = None) -> dict:
    """{'labels', 'masks', 'ignore'} for scoring set_name under a label set (module doc)."""
    assert labels in LABEL_SETS, labels
    S = sets.resolve(set_name, opening)
    if labels == "manifest":
        assert manifest is not None, "--labels manifest needs the dump manifest"
        ls = label_set_of_root(manifest.get("split_def", ""))
        if ls is None:
            raise ValueError(f"cannot tell the label set from the run root {manifest.get('split_def')!r}")
        labels = ls
    if labels == "set":
        return {"labels": "set", "masks": S["masks"], "ignore": S["ignore"]}
    if labels == "v11":
        mf = sets.MASKS_V11 / "MANIFEST.md5"
        assert md5(mf).startswith(MASKS_V11_MANIFEST_MD5), (mf, md5(mf))
        return {"labels": "v11", "masks": sets.MASKS_V11 / "masks", "ignore": sets.MASKS_V11 / "ignore"}
    return {"labels": "v1", "masks": sets.LABELED / "masks_escdd", "ignore": None}


def load_gt(G: dict, stem: str):
    """(gt uint8, keep bool or None) exactly as bench_score.load_gt for the chosen directories."""
    gt = np.array(Image.open(Path(G["masks"]) / f"{stem}.png"))
    keep = None
    if G["ignore"] is not None:
        keep = ~(np.array(Image.open(Path(G["ignore"]) / f"{stem}.png")) > 0)
    return gt, keep
