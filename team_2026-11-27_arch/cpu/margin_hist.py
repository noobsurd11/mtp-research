"""Task 4 diagnostic: where the crack margin m = log s_crack - max_other log s (dump key m_crack) sits on the px a margin-guided
post-process could add. COMBO swad readout, cv5v3 OOF, seeds 5, 6, argmax P = pred == 14; k = not ignore.
Pools (keep px only): MISS = GT crack px with no P px within 2 px (the relR@2 miss); MISS_NEAR = MISS px within 8 px of P
(reachable by a short extension or bridge); NEG_NEAR = non-GT-crack px more than 2 px from GT crack and 1 to 8 px from P
(what a walk could add that costs relP@2). Histogram of m in 0.5 bins over [-30, 10] (values clipped), summed over cells and
seeds; printed: share of each pool with m >= t (0.5 bins), and the ratio NEG_NEAR / MISS_NEAR px above t (false px per recoverable px).

  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> margin_hist.py --seeds 5,6 --workers 8
"""
from __future__ import annotations

import argparse
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C  # noqa: E402
from bench import cellmeta, dumpfmt  # noqa: E402
from bench.m0core import CRACK  # noqa: E402

EDGES = np.arange(-30.0, 10.0001, 0.5)
POOLS = ("MISS", "MISS_NEAR", "NEG_NEAR", "COVERED_GT")
TS = (-8.0, -5.0, -3.0, -2.0, -1.5, -1.0, -0.5, 0.0)


def _cell(a):
    set_dir, stem, gt = a
    d = dumpfmt.read_cell(Path(set_dir) / f"{stem}.npz", check=True)
    g, keep = cellmeta.load_gt(gt, stem)
    k = np.ones(g.shape, bool) if keep is None else keep
    m = np.clip(d["m_crack"].astype(np.float32), -29.999, 9.999)
    P = d["pred"] == CRACK
    G = (g == CRACK) & k
    dP = ndi.distance_transform_edt(~P) if P.any() else np.full(g.shape, np.inf)
    dG = ndi.distance_transform_edt(~G) if G.any() else np.full(g.shape, np.inf)
    pools = {"MISS": G & (dP > 2), "MISS_NEAR": G & (dP > 2) & (dP <= 8), "NEG_NEAR": k & (dG > 2) & (dP > 0) & (dP <= 8),
             "COVERED_GT": G & (dP <= 2)}
    return np.stack([np.histogram(m[pools[p]], EDGES)[0] for p in POOLS])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="5,6")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    C.check_tree()
    out = C.OUT / "ext" / "margin_hist.txt"
    assert not out.exists(), f"refuse: {out} exists"
    pool = get_context("fork").Pool(a.workers)
    H = 0
    for r in C.combo_runs([int(x) for x in a.seeds.split(",")]):
        H = H + sum(pool.map(_cell, [(str(r.set_dir), s, r.gt) for s in r.stems], chunksize=2))
    pool.close(); pool.join()
    np.save(C.OUT / "ext" / "margin_hist.npy", H)
    lo = EDGES[:-1]
    L = [f"# margin of COMBO (swad) on candidate px, seeds {a.seeds}, 532 cells each; px counts summed over seeds",
         "pool\tpx\tmedian m\t" + "\t".join(f"share m>={t:g}" for t in TS)]
    for i, p in enumerate(POOLS):
        h = H[i]; n = h.sum(); cdf = np.cumsum(h) / max(n, 1)
        med = lo[np.searchsorted(cdf, 0.5)] + 0.25
        L.append(f"{p}\t{n}\t{med:+.2f}\t" + "\t".join(f"{h[lo >= t].sum() / max(n, 1):.3f}" for t in TS))
    L.append("\nt\tMISS_NEAR px m>=t\tNEG_NEAR px m>=t\tNEG / MISS ratio")
    for t in TS:
        a1, b1 = H[1][lo >= t].sum(), H[2][lo >= t].sum()
        L.append(f"{t:+g}\t{a1}\t{b1}\t{b1 / max(a1, 1):.2f}")
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
