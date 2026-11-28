"""Task 1, step 1: per-class component post-processing (Extending nnU-Net, arXiv 2208.10791) on COMBO out-of-fold dumps.
POST-HOC ARM: the dumps and the cells were seen before; thresholds are cross-fitted, the arm is still post-hoc.

Rule (on the dump's argmax map `pred`, as the method would see it at inference; ignore px play no role here):
  crack:    8-connected components of pred == 14 whose skeleton length (bench/skel.py px, at least 1) is < L are removed;
            their px take `oth` (the dump's argmax over the 23 non-crack classes).
  inactive: 8-connected components of pred == 11 with < A px are removed; their px become 0 (background; the dumps hold no
            logp, so the runner-up class is unknown; nnU-Net's own removal also writes background).
Per cell and candidate: crack counts (crossfit_op.crack_counts, the read tool's exact 7 counts) and inactive tp / pp / gp
over keep px. Choice (per seed, per held-out fold k, on the out-of-fold cells of the other four folds of the same seed,
never on fold k): L maximising pooled crack relF1@2 (crossfit_op.cmetrics), A maximising pooled inactive IoU; ties ->
the smaller threshold. Outputs OUT/pp/sweep_<run_id>.npz (per-cell cache), OUT/pp/choices.json, OUT/pp/sweep.txt.

  cd /home/yugma/mtp/research/team_2026-11-27_arch/cpu && PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 \
     /home/noob/work/el-fault-detection/.venv/bin/python pp_sweep.py --seeds 5,6 --workers 8
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C  # noqa: E402
from bench import cellmeta, dumpfmt  # noqa: E402
from bench.crossfit_op import CellGT, cmetrics, crack_counts  # noqa: E402
from bench.m0core import CRACK, INACT, S8  # noqa: E402
from bench.skel import skeletonize  # noqa: E402

L_GRID = (0, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60)
A_GRID = (0, 25, 50, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000, 8000)


def crack_comp_len(pc: np.ndarray):
    """(labels, per-label skeleton length) of the 8-connected components of a crack mask; length >= 1."""
    lab, n = ndi.label(pc, S8)
    if not n:
        return lab, np.zeros(1, np.int64)
    sk = skeletonize(pc)
    ln = np.bincount(lab[sk].ravel(), minlength=n + 1)
    ln = np.maximum(ln, 1); ln[0] = 0
    return lab, ln


def inact_comp_size(pi: np.ndarray):
    lab, n = ndi.label(pi, S8)
    sz = np.bincount(lab.ravel(), minlength=n + 1); sz[0] = 0
    return lab, sz


def apply_pp(d: dict, L: int, A: int) -> dict:
    """Post-processed copy of a dump cell (pred, oth, m_crack changed; p_crack, p_inact kept)."""
    pred, oth, m = d["pred"].copy(), d["oth"].copy(), d["m_crack"].copy()
    if L > 0:
        lab, ln = crack_comp_len(pred == CRACK)
        rm = (ln < L)[lab] & (lab > 0)
        pred[rm] = oth[rm]
        m[rm] = np.minimum(m[rm], np.float16(-8.0))          # stays non-crack at every bias of OP_GRID (|b| <= 6)
    if A > 0:
        lab, sz = inact_comp_size(pred == INACT)
        rm = (sz < A)[lab] & (lab > 0)
        pred[rm] = 0
        oth[rm] = 0
    return {"pred": pred, "oth": oth, "m_crack": m, "p_crack": d["p_crack"], "p_inact": d["p_inact"]}


def _cell(a):
    set_dir, stem, gt = a
    d = dumpfmt.read_cell(Path(set_dir) / f"{stem}.npz", check=True)
    g, keep = cellmeta.load_gt(gt, stem)
    G = CellGT(g, keep)
    k = G.k
    lab, ln = crack_comp_len(d["pred"] == CRACK)
    cc = np.zeros((len(L_GRID), 7), np.int64)
    for i, L in enumerate(L_GRID):
        pc = (d["pred"] == CRACK) & ~((ln < L)[lab] & (lab > 0))
        cc[i] = crack_counts(pc, G)
    gi = (g == INACT) & k
    labi, sz = inact_comp_size(d["pred"] == INACT)
    ic = np.zeros((len(A_GRID), 3), np.int64)
    for i, A in enumerate(A_GRID):
        pi = (d["pred"] == INACT) & ~((sz < A)[labi] & (labi > 0)) & k
        ic[i] = (int((pi & gi).sum()), int(pi.sum()), int(gi.sum()))
    return cc, ic, int(len(ln) - 1), int(len(sz) - 1)


def sweep_run(pool, r) -> dict:
    p = C.OUT / "pp" / f"sweep_{r.run_id}_{r.manifest_md5[:8]}.npz"
    if p.exists():
        z = np.load(p)
        return {k: z[k] for k in z.files}
    res = pool.map(_cell, [(str(r.set_dir), s, r.gt) for s in r.stems], chunksize=2)
    out = {"stems": np.array(r.stems), "cc": np.stack([x[0] for x in res]), "ic": np.stack([x[1] for x in res]),
           "n_crack_comp": np.array([x[2] for x in res]), "n_inact_comp": np.array([x[3] for x in res])}
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez(p, **out)
    return out


def iou(v) -> float:
    tp, pp, gp = (float(x) for x in v)
    return tp / (pp + gp - tp) if pp + gp - tp > 0 else float("nan")


def best(vals) -> int:
    v = np.where(np.isfinite(vals), vals, -np.inf)
    return int(np.flatnonzero(v >= v.max() - 1e-12)[0])          # ties -> the first = the smaller threshold


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="5,6")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    C.check_tree()
    seeds = [int(x) for x in a.seeds.split(",")]
    runs = C.combo_runs(seeds)
    pool = get_context("fork").Pool(a.workers)
    data = {}
    for r in runs:
        data[(r.seed, r.fold)] = sweep_run(pool, r)
        print(f"swept {r.run_id} ({len(r.stems)} cells)", flush=True)
    pool.close(); pool.join()
    L = ["# task 1 sweep (post-hoc arm): COMBO swad readout, cv5v3 OOF, seeds " + a.seeds,
         f"# L grid {L_GRID}; A grid {A_GRID}; choice per seed and held-out fold on the other four folds"]
    choices = {}
    for s in seeds:
        for k in range(5):
            fit = [data[(s, j)] for j in range(5) if j != k]
            cc = sum(x["cc"].sum(0) for x in fit)
            ic = sum(x["ic"].sum(0) for x in fit)
            f1 = np.array([cmetrics(c)["relF1_2"] for c in cc])
            io = np.array([iou(c) for c in ic])
            iL, iA = best(f1), best(io)
            choices[f"s{s}_f{k}"] = {"seed": s, "fold": k, "L": L_GRID[iL], "A": A_GRID[iA],
                                     "fit_relF1_2_raw": float(f1[0]), "fit_relF1_2_chosen": float(f1[iL]),
                                     "fit_inact_iou_raw": float(io[0]), "fit_inact_iou_chosen": float(io[iA])}
            L.append(f"s{s} f{k}: L={L_GRID[iL]} (fit relF1@2 {f1[0]:.4f} -> {f1[iL]:.4f}); "
                     f"A={A_GRID[iA]} (fit inactive IoU {io[0]:.4f} -> {io[iA]:.4f})")
    L.append("\n## descriptive curves on ALL out-of-fold cells of each seed (in-sample; not the result)")
    for s in seeds:
        cc = sum(data[(s, k)]["cc"].sum(0) for k in range(5))
        ic = sum(data[(s, k)]["ic"].sum(0) for k in range(5))
        cf = [i for k in range(5) for i in np.flatnonzero(data[(s, k)]["cc"][:, 0, 2] == 0)]
        fa = sum(int(data[(s, k)]["cc"][data[(s, k)]["cc"][:, 0, 2] == 0][:, :, 1].sum(0)[0]) for k in range(5))
        L.append(f"seed {s}: crack-free cells {len(cf)}; raw false crack px on them {fa}")
        L.append("L\trelF1@2\trelP@2\trelR@2\tcrack px\tfa px (crack-free)")
        for i, Lv in enumerate(L_GRID):
            m = cmetrics(cc[i])
            fa_i = sum(int(data[(s, k)]["cc"][data[(s, k)]["cc"][:, 0, 2] == 0][:, i, 1].sum()) for k in range(5))
            L.append(f"{Lv}\t{m['relF1_2']:.4f}\t{m['relP2']:.4f}\t{m['relR2']:.4f}\t{int(cc[i][1])}\t{fa_i}")
        L.append("A\tinactive IoU\tpred px\tGT px")
        for i, Av in enumerate(A_GRID):
            L.append(f"{Av}\t{iou(ic[i]):.4f}\t{int(ic[i][1])}\t{int(ic[i][2])}")
    (C.OUT / "pp" / "choices.json").write_text(json.dumps(choices, indent=1))
    (C.OUT / "pp" / "sweep.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
