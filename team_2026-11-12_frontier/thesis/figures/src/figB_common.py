"""fig_maker_B shared helpers: paths, the pool-only guard, loaders, overlay colours, figure saving.

Rules: pool cells only (P532 = cv5v3 pool). Every image / mask / dump read goes through guard_stem() and guard_path().
guard_path() refuses any path containing test50, e1_106, /e1/ or _e1 (case-insensitive). Every read is appended to
logs_B/readlog_<fig>.tsv, so the sealed-path check can be re-run over the logs. CPU only; no write outside thesis/figures/.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

T = Path("/home/yugma/mtp/research/team_2026-11-12_frontier")
FIG = T / "thesis" / "figures"
SRC = FIG / "src"
LOGS = SRC / "logs_B"
BENCH = T / "benchmark"
CELLS_TSV = BENCH / "cells.tsv"
CV5V3 = BENCH / "splits" / "cv5v3.json"
POOL_MANIFEST = BENCH / "splits" / "pool532_manifest.tsv"
FORBIDDEN = BENCH / "splits" / "forbidden_v1.txt"
LEGACY_JSON = BENCH / "splits" / "legacy.json"
IMAGES = Path("/home/noob/work/el-fault-detection/data/labeled/images")
MASKS_V11 = BENCH / "out" / "masks_v11" / "masks"          # v1.1, 0..23 and 255 = ignore (LABELS_V11.md section 3)
SEALED_TOKENS = ("test50", "e1_106", "/e1/", "_e1")
CRACK, INACT, IGN, PAD = 14, 11, 255, 7

# Okabe-Ito colour-blind safe palette
OI = {"orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
      "vermillion": "#D55E00", "purple": "#CC79A7", "black": "#000000", "grey": "#999999"}
COL_CRACK = OI["vermillion"]
COL_INACT = OI["blue"]
COL_BOX = OI["yellow"]
SRC_COL = {"ARTS": OI["orange"], "BMRK": OI["sky"], "CFVS": OI["green"], "CSIR": OI["vermillion"], "SDLE": OI["purple"]}
SRC_MARK = {"ARTS": "o", "BMRK": "s", "CFVS": "^", "CSIR": "D", "SDLE": "v"}

_FIGNAME = os.environ.get("FIGB_NAME", "unknown")
FSCALE = 9 / 8   # base font 9 pt (was 8 pt), to match fig_maker_A; every explicit size scales with it


def fs(x: float) -> float:
    return round(x * FSCALE, 2)


def set_fig(name: str) -> None:
    global _FIGNAME
    _FIGNAME = name
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / f"readlog_{name}.tsv").write_text("kind\tpath\n")


def log_read(kind: str, path) -> None:
    with open(LOGS / f"readlog_{_FIGNAME}.tsv", "a") as f:
        f.write(f"{kind}\t{path}\n")


def guard_path(path) -> str:
    p = str(path)
    low = p.lower()
    for tok in SEALED_TOKENS:
        if tok in low:
            raise RuntimeError(f"REFUSED (sealed token {tok!r}): {p}")
    return p


def _sealed() -> set:
    s = {l.strip() for l in open(FORBIDDEN) if l.strip()}
    d = json.load(open(LEGACY_JSON))
    for v in d.get("sealed_sets", {}).values():
        if isinstance(v, list):
            s |= set(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    s |= set(vv)
    return s


_POOL = None
_FOLD = None


def pool() -> set:
    """532 pool stems = union of cv5v3 held-out folds; must equal pool532_manifest.tsv; none sealed; none test50 / e1_106."""
    global _POOL, _FOLD
    if _POOL is None:
        d = json.load(open(CV5V3))
        fold = {}
        for f in d["folds"]:
            for s in f["heldout"]:
                assert s not in fold
                fold[s] = int(f["id"][1:])
        man = [r[0] for r in csv.reader(open(POOL_MANIFEST), delimiter="\t")][1:]
        assert len(fold) == 532 and set(fold) == set(man), "cv5v3 held-out union != pool manifest"
        bad = set(fold) & _sealed()
        assert not bad, f"sealed stems in pool: {sorted(bad)[:5]}"
        for r in cells_rows():
            if r["stem"] in fold:
                assert r["bench_set"] not in ("test50", "e1_106") and r["role"] in ("train", "val"), r["stem"]
        _POOL, _FOLD = set(fold), fold
    return _POOL


def fold_of() -> dict:
    pool()
    return dict(_FOLD)


def guard_stem(stem: str) -> str:
    if stem not in pool():
        raise RuntimeError(f"REFUSED: {stem} is not a P532 pool cell")
    guard_path(stem)
    return stem


_CELLS = None


def cells_rows() -> list[dict]:
    global _CELLS
    if _CELLS is None:
        _CELLS = list(csv.DictReader(open(CELLS_TSV), delimiter="\t"))
    return _CELLS


def pool_cells() -> dict:
    """cells.tsv rows of the 532 pool stems only."""
    P = pool()
    return {r["stem"]: r for r in cells_rows() if r["stem"] in P}


def grey(stem: str) -> np.ndarray:
    guard_stem(stem)
    p = IMAGES / f"{stem}.png"
    guard_path(p)
    log_read("image", p)
    return np.array(Image.open(p).convert("L"), dtype=np.uint8)


def mask_v11(stem: str) -> np.ndarray:
    guard_stem(stem)
    p = MASKS_V11 / f"{stem}.png"
    guard_path(p)
    log_read("mask_v11", p)
    return np.array(Image.open(p))


def load_npz(path, stem: str, keys=("pred",)) -> dict:
    guard_stem(stem)
    guard_path(path)
    assert Path(path).name == f"{stem}.npz", path
    log_read("npz", path)
    with np.load(path) as z:
        return {k: z[k] for k in keys}


def hexrgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def dilate1(m: np.ndarray) -> np.ndarray:
    from scipy import ndimage as ndi
    return ndi.binary_dilation(m, structure=np.ones((3, 3), bool)) if m.any() else m


def overlay(g: np.ndarray, crack: np.ndarray | None = None, inact: np.ndarray | None = None,
            alpha_inact: float = 0.45, crack_dilate: bool = True) -> np.ndarray:
    """RGB uint8 at native resolution: grey image, inactive tinted blue (alpha), crack opaque vermillion
    (dilated by 1 px, 3 x 3, for visibility when crack_dilate)."""
    rgb = np.repeat(g[..., None].astype(np.float32), 3, axis=2)
    if inact is not None and inact.any():
        rgb[inact] = (1 - alpha_inact) * rgb[inact] + alpha_inact * hexrgb(COL_INACT)
    if crack is not None and crack.any():
        c = dilate1(crack) if crack_dilate else crack
        rgb[c] = hexrgb(COL_CRACK)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def rcparams():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": fs(8), "axes.titlesize": fs(8), "axes.labelsize": fs(8),
                         "xtick.labelsize": fs(7), "ytick.labelsize": fs(7), "legend.fontsize": fs(7), "pdf.fonttype": 42,
                         "savefig.bbox": "tight", "savefig.pad_inches": 0.03, "image.interpolation": "none"})
    return plt


def save(fig, name: str) -> None:
    pdf, png = FIG / f"{name}.pdf", FIG / f"{name}.png"
    fig.savefig(pdf, metadata={"Creator": f"fig_maker_B src/make_{name}.py", "CreationDate": None})
    fig.savefig(png, dpi=200)


def write_csv(name: str, header: list[str], rows: list) -> None:
    with open(FIG / f"{name}_data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
