"""elbench prediction dump format (numpy only; any codebase can import this single file).

One compressed npz per cell: <DUMPS>/<bench>/<method>/<run_id>/<set>/<cell_id>.npz, cell_id = image stem.
Keys (DESIGN.md s3.1; p_crack is float32, see below):
  pred     uint8   (512, 512)  final class map at the method's declared decision rule (argmax over 24 for softmax heads)
  oth      uint8   (512, 512)  argmax over the 23 non-crack classes (crack-bias sweeps are exact from m_crack + oth)
  m_crack  float16 (512, 512)  log(s_crack + 1e-12) - max_{k != crack} log(s_k + 1e-12)   (calib_dump c172717e `maps`)
  p_crack  float32 (512, 512)  crack score in [0, 1]. float32, not float16: m0's p-bands and 1,000-bin histograms are
                               computed on float32 softmax, and the identity check must be exact (lead's I1a rule).
  p_inact  float16 (512, 512)  inactive score in [0, 1]
  logp     float16 (24, 512, 512), optional: log scores for ensembling / 24-class bias studies (val / dev sets only)
Per run: <run_id>/manifest.json (written by write_manifest) with the run metadata and one md5 per cell file.

Sealed sets (test50, e1_106) are refused unless an opening protocol name is given.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import time
from pathlib import Path

import numpy as np

FORMAT = "elbench-dump-1"
NC, CRACK, INACT = 24, 14, 11
HW = (512, 512)
SEALED = ("test50", "e1_106")
OPEN_FIXED = ("val54", "f51", "h36", "rf106")
OPEN_PATTERN = re.compile(r"^cv[0-9a-z]+_f[0-9]+$")   # held-out fold k of a CV split definition, e.g. cv5v1_f0
TIE_EPS = 1e-3          # |m_crack| below this: pred and the margin may disagree (float16 / softmax ties); counted, allowed
REQUIRED = ("pred", "oth", "m_crack", "p_crack", "p_inact")
DTYPES = {"pred": np.uint8, "oth": np.uint8, "m_crack": np.float16, "p_crack": np.float32, "p_inact": np.float16,
          "logp": np.float16}


class SealedSetError(RuntimeError):
    pass


def set_kind(name: str) -> str:
    if name in SEALED:
        return "sealed"
    if name in OPEN_FIXED or OPEN_PATTERN.match(name):
        return "open"
    raise ValueError(f"unknown set name {name!r} (sealed {SEALED}; open {OPEN_FIXED} or cv<id>_f<k>)")


def check_set(name: str, opening: str | None) -> str:
    """'open' or 'sealed'; a sealed set without an opening protocol name raises SealedSetError."""
    k = set_kind(name)
    if k == "sealed" and not opening:
        raise SealedSetError(f"set {name} is sealed: pass --opening <protocol> at a pre-registered opening")
    return k


def cell_path(dumps: str | Path, bench: str, method: str, run_id: str, set_name: str, stem: str) -> Path:
    for part in (bench, method, run_id, set_name, stem):
        if not part or "/" in part or part.startswith("."):
            raise ValueError(f"bad path part {part!r}")
    return Path(dumps) / bench / method / run_id / set_name / f"{stem}.npz"


def maps_from_scores(s: np.ndarray) -> dict:
    """Numpy version of calib_dump.maps for external codebases: s = per-class scores (24, H, W), float, >= 0.
    Returns oth, m_crack, p_crack, p_inact (pred is the caller's: its own decision rule). Same formula as calib_dump;
    not guaranteed bit-equal to the torch path used by scripts/bench_infer.py."""
    s = np.asarray(s, np.float32)
    assert s.shape[0] == NC and s.shape[1:] == HW, s.shape
    lq = np.log(s + np.float32(1e-12))
    pc = lq[CRACK].copy()
    lq[CRACK] = np.float32(-1e30)
    oth = lq.argmax(0)
    mo = np.take_along_axis(lq, oth[None], 0)[0]
    return {"oth": oth.astype(np.uint8), "m_crack": (pc - mo).astype(np.float16),
            "p_crack": s[CRACK].astype(np.float32), "p_inact": s[INACT].astype(np.float16)}


def check_cell(d: dict) -> dict:
    """Validate one cell's arrays; returns {'ties': n} (pred != where(m > 0, crack, oth) where |m| < TIE_EPS).
    Raises AssertionError on anything else."""
    for k in REQUIRED:
        assert k in d, f"missing key {k}"
        assert d[k].shape == HW, (k, d[k].shape)
        assert d[k].dtype == DTYPES[k], (k, d[k].dtype)
    if "logp" in d:
        assert d["logp"].shape == (NC, *HW) and d["logp"].dtype == DTYPES["logp"], ("logp", d["logp"].shape)
    assert int(d["pred"].max()) < NC and int(d["oth"].max()) < NC, "class id out of range"
    assert not (d["oth"] == CRACK).any(), "oth holds crack"
    for k in ("p_crack", "p_inact"):
        v = d[k]
        assert np.isfinite(v).all() and float(v.min()) >= 0.0 and float(v.max()) <= 1.0 + 1e-3, f"{k} outside [0, 1]"
    m = d["m_crack"].astype(np.float32)
    assert np.isfinite(m).all(), "m_crack not finite"
    implied = np.where(m > 0, CRACK, d["oth"]).astype(np.uint8)
    bad = implied != d["pred"]
    hard = bad & (np.abs(m) >= TIE_EPS)
    if hard.any():
        # pred is not crack and not oth, or disagrees with a clear margin: the dump is inconsistent
        raise AssertionError(f"pred disagrees with where(m_crack > 0, 14, oth) at {int(hard.sum())} px with |m| >= {TIE_EPS}")
    return {"ties": int(bad.sum())}


def write_cell(path: str | Path, pred, oth, m_crack, p_crack, p_inact, logp=None) -> dict:
    """Validate and write one cell (np.savez_compressed, atomic rename). Returns {'md5', 'ties', 'bytes'}.
    Refuses to overwrite an existing file."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    d = {"pred": np.asarray(pred).astype(np.uint8, copy=False), "oth": np.asarray(oth).astype(np.uint8, copy=False),
         "m_crack": np.asarray(m_crack).astype(np.float16, copy=False),
         "p_crack": np.asarray(p_crack).astype(np.float32, copy=False),
         "p_inact": np.asarray(p_inact).astype(np.float16, copy=False)}
    if logp is not None:
        d["logp"] = np.asarray(logp).astype(np.float16, copy=False)
    info = check_cell(d)
    buf = io.BytesIO()
    np.savez_compressed(buf, format=np.array(FORMAT), **d)
    data = buf.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp{os.getpid()}")
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return {"md5": hashlib.md5(data).hexdigest(), "ties": info["ties"], "bytes": len(data)}


def read_cell(path: str | Path, check: bool = True) -> dict:
    with np.load(path, allow_pickle=False) as z:
        assert str(z["format"]) == FORMAT, (path, str(z["format"]))
        d = {k: z[k] for k in z.files if k != "format"}
    if check:
        check_cell(d)
    return d


def md5_file(p: str | Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


MANIFEST_KEYS = ("bench", "method", "run_id", "seed", "split_def", "split_md5", "fold", "set", "stems_md5",
                 "code_repo", "code_commit", "checkpoint", "checkpoint_md5", "step", "weights_key", "device",
                 "precision", "tta", "decision_rule", "card", "card_md5", "writer", "set_kind", "opening")


def write_manifest(set_dir: str | Path, meta: dict, cells: dict) -> Path:
    """<set_dir>/manifest.json: meta (all MANIFEST_KEYS) + per-cell {md5, ties, bytes} + totals; refuses to overwrite."""
    set_dir = Path(set_dir)
    missing = [k for k in MANIFEST_KEYS if k not in meta]
    assert not missing, f"manifest keys missing: {missing}"
    out = set_dir / "manifest.json"
    if out.exists():
        raise FileExistsError(out)
    doc = {"format": FORMAT, **meta, "n_cells": len(cells), "cells": cells,
           "ties_total": int(sum(c["ties"] for c in cells.values())),
           "bytes_total": int(sum(c["bytes"] for c in cells.values())),
           "written": time.strftime("%Y-%m-%d %H:%M:%S")}
    out.write_text(json.dumps(doc, indent=1, sort_keys=False))
    return out


def read_manifest(set_dir: str | Path, verify: bool = True) -> dict:
    """Load a set's manifest; with verify, every listed cell file must exist with the recorded md5 and no extra npz."""
    set_dir = Path(set_dir)
    doc = json.loads((set_dir / "manifest.json").read_text())
    assert doc.get("format") == FORMAT, doc.get("format")
    if verify:
        on_disk = sorted(p.stem for p in set_dir.glob("*.npz"))
        assert on_disk == sorted(doc["cells"]), "cell files on disk != manifest"
        bad = [s for s, c in doc["cells"].items() if md5_file(set_dir / f"{s}.npz") != c["md5"]]
        assert not bad, f"md5 mismatch: {bad[:5]}"
    return doc
