"""dataset_audit common: paths, the pool cell list with the sealed-set guard, loaders. CPU only, numpy / scipy / PIL.
Every reader of masks or dumps goes through pool_stems(), which fails closed on any sealed or forbidden stem."""
from __future__ import annotations

import glob
import hashlib
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "/home/noob/work/bench_wt_b")       # read-only import of the frozen skeleton (bench/skel.py)
from bench.skel import skeletonize  # noqa: E402

AUDIT = Path("/home/yugma/mtp/research/team_2026-11-12_frontier/dataset_audit")
OUT = AUDIT / "out"
CACHE = AUDIT / "cache"
BENCH = Path("/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark")
LABELED = Path("/home/noob/work/el-fault-detection/data/labeled")
IMAGES = LABELED / "images"
MASKS_OLD = LABELED / "masks_coded"                      # BenchmarkEL 20211104
MASKS_V11 = Path("/home/noob/work/bench_data/masks_v11/masks")
POOL_MANIFEST = BENCH / "splits" / "pool532_manifest.tsv"
FORBIDDEN = BENCH / "splits" / "forbidden_v1.txt"
LEGACY_JSON = BENCH / "splits" / "legacy.json"
G3 = Path("/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv")
G2 = Path("/home/noob/work/bench_data/meta/cv5v2_groups.tsv")
RELAY = Path("/home/noob/work/bench_relay")
W1G = Path("/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11")
CRACK, INACT, IGN = 14, 11, 255
S8 = np.ones((3, 3), bool)

RECIPES = {  # name: (relay group, run prefix, method folder); primary readouts (no '.swad' suffix)
    "PF": ("c3base", "c3_pf_v11", "house_r34_unetpp_pf_v11"),
    "HOUSE": ("c3base", "c3_house_v11", None),
    "HRNET": ("c3hrnet", "c3h_hrnet_w18_unetpp_pf", None),
    "SWADBN": ("c3swad", "c3s_swad_v11", "swad_const_pf_v11"),
    "C3X": ("c3x", "c3x_hrnet_swad_v11", "hrnet_w18_unetpp_swad_const_pf_v11"),
}
SEEDS = (5, 6, 7, 8, 9)
MODELS = [(r, s) for r in RECIPES for s in SEEDS]       # 25 models, fixed order


def md5f(p) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def _sealed() -> set:
    import json
    sealed = {l.strip() for l in open(FORBIDDEN) if l.strip()}
    d = json.load(open(LEGACY_JSON))
    s = d.get("sealed_sets", {})
    for v in s.values():
        if isinstance(v, list):
            sealed |= set(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, list):
                    sealed |= set(vv)
    return sealed


def pool_stems() -> list[str]:
    rows = [l.rstrip("\n").split("\t") for l in open(POOL_MANIFEST) if l.strip()]
    stems = [r[0] for r in rows[1:]]
    assert len(stems) == 532 and len(set(stems)) == 532, len(stems)
    bad = set(stems) & _sealed()
    assert not bad, f"sealed stems in pool list: {sorted(bad)[:5]}"
    g3 = groups(G3)
    assert set(g3) == set(stems), "cv5v3 group file and pool manifest differ"
    return stems


def groups(path=G3) -> dict:
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]
    h = rows[0]
    return {r[0]: dict(zip(h, r)) for r in rows[1:]}


def guard(stem: str, pool: set) -> None:
    if stem not in pool:
        raise RuntimeError(f"refused: {stem} is not a pool cell")


def grey(stem: str) -> np.ndarray:
    return np.array(Image.open(IMAGES / f"{stem}.png").convert("L"), dtype=np.uint8)


def mask_v11(stem: str) -> np.ndarray:
    return np.array(Image.open(MASKS_V11 / f"{stem}.png"))


def mask_old(stem: str) -> np.ndarray:
    return np.array(Image.open(MASKS_OLD / f"{stem}.png"))


def relay_index() -> dict:
    """{(recipe, seed): {stem: npz path}} for the 25 cv5v3 models; asserts 532 cells per model, each once."""
    idx = {}
    for (rec, seed) in MODELS:
        grp, pre, _ = RECIPES[rec]
        d = {}
        for k in range(5):
            run = f"{pre}_f{k}_s{seed}"
            pat = str(RELAY / grp / run / "dumps" / "elbench1" / "*" / run / f"cv5v3_f{k}" / "*.npz")
            for p in glob.glob(pat):
                st = os.path.basename(p)[:-4]
                assert st not in d, (rec, seed, st)
                d[st] = p
        assert len(d) == 532, (rec, seed, len(d))
        idx[(rec, seed)] = d
    return idx


def w1g_index() -> dict:
    idx = {}
    for seed in (5, 6, 7, 8):
        d = {}
        for k in range(5):
            for p in glob.glob(str(W1G / f"w1g_pf_v11_f{k}_s{seed}" / f"cv5v2_f{k}" / "*.npz")):
                st = os.path.basename(p)[:-4]
                assert st not in d
                d[st] = p
        assert len(d) == 532, (seed, len(d))
        idx[("W1G_PF", seed)] = d
    return idx


def load_dump(p: str, keys=("pred", "p_crack", "p_inact")) -> dict:
    with np.load(p) as z:
        return {k: z[k] for k in keys}


def contrast_z(g: np.ndarray, comp: np.ndarray, exclude: np.ndarray, valid: np.ndarray) -> float:
    """(median grey on comp - median grey on a ring 3..6 px away) / (1.4826 MAD of the ring). exclude: px kept out of the ring."""
    from scipy import ndimage as ndi
    d = ndi.distance_transform_edt(~comp)
    ring = (d >= 3) & (d <= 6) & ~exclude & valid
    if ring.sum() < 10 or comp.sum() == 0:
        return float("nan")
    r = g[ring].astype(np.float32)
    mad = 1.4826 * np.median(np.abs(r - np.median(r)))
    return float((np.median(g[comp].astype(np.float32)) - np.median(r)) / max(mad, 1.0))
