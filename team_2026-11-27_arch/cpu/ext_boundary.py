"""Task 4 boundary check (descriptive, IN-SAMPLE on all OOF cells of seeds 5, 6; not a result): the cross-fit chose t = -8,
the lowest grid value, in all 10 fits. Same walk / bridge code as ext.py (imported), k 4, ang 50, d 0, L (6, 12, 24),
t in (-8, -12, -20, -1e9 = geometry only). Prints pooled relF1@2, relP@2, relR@2, width ratio, added px, false px on crack-free cells.
  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> ext_boundary.py
"""
import sys
from multiprocessing import get_context
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C, ext as E
from bench import cellmeta, dumpfmt
from bench.crossfit_op import CellGT, cmetrics, crack_counts
from bench.m0core import CRACK, S8
TS = (-8.0, -12.0, -20.0, -1e9); LS = (6, 12, 24)
CS = [(t, L) for t in TS for L in LS]
def _cell(a):
    set_dir, stem, gt = a
    d = dumpfmt.read_cell(Path(set_dir) / f"{stem}.npz", check=True)
    g, keep = cellmeta.load_gt(gt, stem); G = CellGT(g, keep)
    P = d["pred"] == CRACK; m = d["m_crack"].astype(np.float32); lab, _ = ndi.label(P, S8); eps = E.endpoints(P)
    out = np.zeros((1 + len(CS), 8), np.int64); out[0, :7] = crack_counts(P, G)
    for t in TS:
        W = [E.walk(p, 4, t, 50, m, lab, max(LS)) for p in eps]
        for L in LS:
            add = [q for s in W for q in s[:L] if q is not None]
            M = np.zeros(P.shape, bool)
            if add:
                ys, xs = zip(*add); M[list(ys), list(xs)] = True
            M &= ~P
            out[1 + CS.index((t, L)), :7] = crack_counts(P | M, G); out[1 + CS.index((t, L)), 7] = M.sum()
    return out
C.check_tree()
pool = get_context("fork").Pool(8)
for s in (5, 6):
    X = []
    for r in C.combo_runs([s]):
        X += pool.map(_cell, [(str(r.set_dir), st, r.gt) for st in r.stems], chunksize=1)
    X = np.stack(X); T = X.sum(0); cf = X[X[:, 0, 2] == 0][:, :, 1].sum(0)
    for i, name in enumerate(["identity"] + [f"t{t:g} L{L}" for t, L in CS]):
        mm = cmetrics(T[i, :7])
        print(f"s{s}\t{name}\trelF1@2 {mm['relF1_2']:.4f}\trelP@2 {mm['relP2']:.4f}\trelR@2 {mm['relR2']:.4f}\twidth {mm['width_ratio']:.4f}\tadded {T[i, 7]}\tfa {cf[i]}", flush=True)
pool.close(); pool.join()
