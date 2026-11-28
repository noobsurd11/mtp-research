"""Task 4: post-hoc ENDPOINT EXTENSION + GAP BRIDGING on COMBO out-of-fold dumps (arm EXT). POST-HOC ARM: these dumps and
cells were read before (c3x, final_tta, x4 posctl, the census that motivated this arm).

Input per cell: pred (argmax), m_crack = log s_crack - max_{k != crack} log s_k (float16 in the dump; the crack margin).
P = pred == 14; S = skeleton of P (bench/skel.py); endpoints = S px with exactly one 8-neighbour in S. From each endpoint
the skeleton is traced back over up to 8 px (unique unvisited S neighbour; stops at a junction); endpoints with fewer than
2 traced px behind them are skipped (no direction).
  extension (k, t, ang, L): direction v = endpoint - (traced px k back, or the last one); at each step the candidates are the
    8-neighbours n of the current px whose offset is within ang degrees of v; the one with the largest margin is taken if its
    margin > t; a px of P of the endpoint's own component is walked through (not added), a px of another component or a
    px outside the image ends the walk (joined / edge); otherwise n is added. v is re-estimated over the last k px of the
    path (trace + walk). At most L steps.
  bridging (k, t, ang, d): endpoints e1, e2 of different P components, |e1 e2| <= d, facing: angle(v1, e2 - e1) <= ang and
    angle(v2, e1 - e2) <= ang; the straight segment's px not in P all have margin > t -> the segment is added.
  Every walk and bridge starts from the ORIGINAL P (they do not see each other's additions); the result is P | added.
Grid: k (4, 8) x t (-8, -5, -3, -2, -1.5, -1, -0.5) x ang (30, 50) x L (0, 3, 6, 12, 24) x d (0, 4, 8, 16) = 560, plus
identity. (t down to -8 because the smoke test showed the margin falls below -5 within 2 to 3 px of most endpoints.)
Choice: per seed and held-out fold k, the candidate maximising pooled crack relF1@2 (crossfit_op.cmetrics on the exact
crossfit_op.crack_counts) on the out-of-fold cells of the other four folds of the same seed; ties -> the earlier candidate
(identity first). Derived dump: pred = 14 on added px, m_crack = max(m, +0.0005) there (dumpfmt consistency; any
negative crack bias removes them again), oth / p_crack / p_inact unchanged.

  sweep:  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> ext.py sweep --seeds 5,6 --workers 8
  write:  ... ext.py write --seeds 5,6 --workers 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C  # noqa: E402
from bench import cellmeta, dumpfmt  # noqa: E402
from bench.crossfit_op import CellGT, cmetrics, crack_counts  # noqa: E402
from bench.m0core import CRACK, S8  # noqa: E402
from bench.skel import skeletonize  # noqa: E402

KS, TS, ANGS, LS, DS = (4, 8), (-8.0, -5.0, -3.0, -2.0, -1.5, -1.0, -0.5), (30, 50), (0, 3, 6, 12, 24), (0, 4, 8, 16)
TRACE = 8
OFFS = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0)]
CANDS = [("id",)] + [("ext", k, t, a, L, d) for k in KS for t in sorted(TS, reverse=True) for a in ANGS for L in LS
                     for d in DS]
IDX = {c: i for i, c in enumerate(CANDS)}
EPS_M = np.float16(0.0005)
OUT = C.OUT / "ext"


def cname(c):
    return "identity" if c[0] == "id" else f"k{c[1]} t{c[2]:+g} ang{c[3]} L{c[4]} d{c[5]}"


def endpoints(P: np.ndarray):
    """[(endpoint (y, x), traced path [endpoint, ...] up to TRACE px back)] of the skeleton of P."""
    S = skeletonize(P)
    nb = ndi.convolve(S.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - S.astype(np.uint8)
    out = []
    H, W = S.shape
    for y, x in zip(*np.nonzero(S & (nb == 1))):
        path = [(int(y), int(x))]
        seen = {path[0]}
        while len(path) <= TRACE:
            cy, cx = path[-1]
            nx = [(cy + dy, cx + dx) for dy, dx in OFFS if 0 <= cy + dy < H and 0 <= cx + dx < W
                  and S[cy + dy, cx + dx] and (cy + dy, cx + dx) not in seen]
            if len(nx) != 1:
                break
            path.append(nx[0]); seen.add(nx[0])
        if len(path) >= 3:
            out.append(path)
    return out


def _dir(hist, k):
    a, b = hist[-1], hist[max(len(hist) - 1 - k, 0)]
    v = np.array([a[0] - b[0], a[1] - b[1]], float)
    n = np.hypot(*v)
    return v / n if n > 0 else None


def walk(path, k, t, ang, m, lab, Lmax):
    """List over steps of the added px (or None for a walked-through own px); stops early."""
    H, W = m.shape
    own = lab[path[0]]
    hist = list(reversed(path))
    cos_a = math.cos(math.radians(ang))
    steps, added = [], set()
    for _ in range(Lmax):
        v = _dir(hist, k)
        if v is None:
            break
        cy, cx = hist[-1]
        best, bm = None, -np.inf
        for dy, dx in OFFS:
            if (dy * v[0] + dx * v[1]) / math.hypot(dy, dx) < cos_a - 1e-9:
                continue
            ny, nx = cy + dy, cx + dx
            if not (0 <= ny < H and 0 <= nx < W) or (ny, nx) in added or (ny, nx) in hist[-3:]:
                continue
            if m[ny, nx] > bm:
                best, bm = (ny, nx), m[ny, nx]
        if best is None or bm <= t:
            break
        if lab[best] and lab[best] != own:
            break
        if lab[best]:
            steps.append(None)
        else:
            steps.append(best); added.add(best)
        hist.append(best)
    return steps


def line(a, b):
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
    return [(int(round(a[0] + (b[0] - a[0]) * i / n)), int(round(a[1] + (b[1] - a[1]) * i / n))) for i in range(1, n)]


def bridges(eps, k, t, ang, m, lab, dmax):
    """[(dist, [px])] of the bridges allowed at (k, t, ang) with dist <= dmax."""
    cos_a = math.cos(math.radians(ang))
    info = [(p[0], _dir(list(reversed(p)), k), lab[p[0]]) for p in eps]
    out = []
    for i in range(len(info)):
        e1, v1, l1 = info[i]
        for j in range(i + 1, len(info)):
            e2, v2, l2 = info[j]
            if l1 == l2 or v1 is None or v2 is None:
                continue
            w = np.array([e2[0] - e1[0], e2[1] - e1[1]], float)
            dd = float(np.hypot(*w))
            if dd > dmax or dd == 0:
                continue
            w /= dd
            if w @ v1 < cos_a or -w @ v2 < cos_a:
                continue
            px = [q for q in line(e1, e2) if not lab[q]]
            if all(m[q] > t for q in px):
                out.append((dd, px))
    return out


def added_masks(d: dict):
    """{candidate index: added px mask (bool) or None for no change} for one cell."""
    P = d["pred"] == CRACK
    m = d["m_crack"].astype(np.float32)
    lab, _ = ndi.label(P, S8)
    eps = endpoints(P)
    res = {}
    for k in KS:
        for t in TS:
            for a in ANGS:
                W = [walk(p, k, t, a, m, lab, max(LS)) for p in eps]
                B = bridges(eps, k, t, a, m, lab, max(DS))
                for L in LS:
                    for dm in DS:
                        add = [q for s in W for q in s[:L] if q is not None] + [q for dd, px in B if dd <= dm for q in px]
                        i = IDX[("ext", k, t, a, L, dm)]
                        if add:
                            M = np.zeros(P.shape, bool)
                            ys, xs = zip(*add)
                            M[list(ys), list(xs)] = True
                            res[i] = M & ~P
                        else:
                            res[i] = None
    return res, len(eps)


def _cell(a):
    set_dir, stem, gt = a
    d = dumpfmt.read_cell(Path(set_dir) / f"{stem}.npz", check=True)
    g, keep = cellmeta.load_gt(gt, stem)
    G = CellGT(g, keep)
    P = d["pred"] == CRACK
    base = crack_counts(P, G)
    out = np.zeros((len(CANDS), 8), np.int64)          # 7 crack counts + added px
    out[:, :7] = base
    am, ne = added_masks(d)
    memo = {}
    for i, M in am.items():
        if M is None:
            continue
        key = hashlib.md5(np.packbits(M).tobytes()).digest()
        if key not in memo:
            memo[key] = (crack_counts(P | M, G), int(M.sum()))
        out[i, :7], out[i, 7] = memo[key]
    return out, ne


def sweep(a) -> int:
    seeds = [int(x) for x in a.seeds.split(",")]
    runs = C.combo_runs(seeds)
    OUT.mkdir(parents=True, exist_ok=True)
    pool = get_context("fork").Pool(a.workers)
    data = {}
    for r in runs:
        p = OUT / f"sweep_{r.run_id}_{r.manifest_md5[:8]}.npz"
        if not p.exists():
            res = pool.map(_cell, [(str(r.set_dir), s, r.gt) for s in r.stems], chunksize=1)
            np.savez(p, cnt=np.stack([x[0] for x in res]), n_ep=np.array([x[1] for x in res]), stems=np.array(r.stems))
        data[(r.seed, r.fold)] = np.load(p)["cnt"]
        print(f"swept {r.run_id}", flush=True)
    pool.close(); pool.join()
    L = [f"# task 4 sweep (post-hoc arm EXT): COMBO swad readout, cv5v3 OOF, seeds {a.seeds}; {len(CANDS)} candidates "
         "(identity + 560); choice per seed and held-out fold on the other four folds, max pooled relF1@2"]
    ch = {}
    for s in seeds:
        for k in range(5):
            cc = sum(data[(s, j)][:, :, :7].sum(0) for j in range(5) if j != k)
            f1 = np.array([cmetrics(c)["relF1_2"] for c in cc])
            i = int(np.flatnonzero(f1 >= f1.max() - 1e-12)[0])
            m0, m1 = cmetrics(cc[0]), cmetrics(cc[i])
            ch[f"s{s}_f{k}"] = {"seed": s, "fold": k, "cand": list(CANDS[i]), "index": i, "fit_raw": m0, "fit_chosen": m1}
            L.append(f"s{s} f{k}: {cname(CANDS[i])}; fit relF1@2 {m0['relF1_2']:.4f} -> {m1['relF1_2']:.4f} "
                     f"(relP@2 {m0['relP2']:.4f} -> {m1['relP2']:.4f}, relR@2 {m0['relR2']:.4f} -> {m1['relR2']:.4f})")
    L.append("\n## descriptive, in-sample on all OOF cells (not the result): top 15 candidates by relF1@2 per seed, and "
             "the best per (L, d) at each t")
    for s in seeds:
        X = sum(data[(s, k)].sum(0) for k in range(5))
        cf = np.concatenate([data[(s, k)][data[(s, k)][:, 0, 2] == 0] for k in range(5)])   # crack-free cells
        fa = cf[:, :, 1].sum(0)
        met = [cmetrics(c[:7]) for c in X]
        o = np.argsort([-x["relF1_2"] for x in met], kind="stable")
        L.append(f"seed {s}: identity relF1@2 {met[0]['relF1_2']:.4f} relP@2 {met[0]['relP2']:.4f} relR@2 "
                 f"{met[0]['relR2']:.4f}; fa px on {len(cf)} crack-free cells {fa[0]}")
        L.append("cand\trelF1@2\trelP@2\trelR@2\twidth\tadded px\tfa px crack-free")
        for i in o[:15]:
            L.append(f"{cname(CANDS[i])}\t{met[i]['relF1_2']:.4f}\t{met[i]['relP2']:.4f}\t{met[i]['relR2']:.4f}\t"
                     f"{met[i]['width_ratio']:.4f}\t{X[i][7]}\t{fa[i]}")
        L.append("t\tbest ext-only (d 0)\tbest bridge-only (L 0)\tbest both")
        for t in TS:
            def bst(f):
                ix = [i for i, c in enumerate(CANDS) if c[0] == "ext" and c[2] == t and f(c)]
                j = max(ix, key=lambda i: met[i]["relF1_2"])
                return f"{cname(CANDS[j])} {met[j]['relF1_2']:.4f} (P {met[j]['relP2']:.4f} R {met[j]['relR2']:.4f}, +{X[j][7]} px)"
            L.append(f"{t:+g}\t{bst(lambda c: c[5] == 0 and c[4] > 0)}\t{bst(lambda c: c[4] == 0 and c[5] > 0)}\t"
                     f"{bst(lambda c: c[4] > 0 and c[5] > 0)}")
    (OUT / "choices.json").write_text(json.dumps(ch, indent=1))
    (OUT / "sweep.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def _w(a):
    src, dst, stem, ci = a
    d = dumpfmt.read_cell(Path(src) / f"{stem}.npz", check=True)
    q = {k: d[k] for k in dumpfmt.REQUIRED}
    if CANDS[ci][0] != "id":
        am, _ = added_masks(d)
        M = am[ci]
        if M is not None:
            q["pred"] = q["pred"].copy(); q["m_crack"] = q["m_crack"].copy()
            q["pred"][M] = CRACK
            q["m_crack"][M] = np.maximum(q["m_crack"][M], EPS_M)
    return stem, dumpfmt.write_cell(Path(dst) / f"{stem}.npz", **q)


def write(a) -> int:
    ch = json.loads((OUT / "choices.json").read_text())
    me = hashlib.md5(Path(__file__).read_bytes()).hexdigest()
    pool = get_context("fork").Pool(a.workers)
    for r in C.combo_runs([int(x) for x in a.seeds.split(",")]):
        c = ch[f"s{r.seed}_f{r.fold}"]
        rid = f"{r.run_id}.ext"
        dst = OUT / "dumps" / "elbench1" / C.MX / rid / r.set_name
        assert not dst.exists(), f"refuse: {dst} exists"
        dst.mkdir(parents=True)
        res = dict(pool.map(_w, [(str(r.set_dir), str(dst), s, c["index"]) for s in r.stems], chunksize=1))
        meta = {k: v for k, v in r.manifest.items()
                if k not in ("format", "n_cells", "cells", "ties_total", "bytes_total", "written")}
        meta["run_id"] = rid
        meta["derivation"] = (f"ext: endpoint extension + gap bridging on the crack margin, {cname(CANDS[c['index']])}; "
                              f"cross-fitted on the other 4 folds of seed {r.seed} (post-hoc arm)")
        meta["derived_from"] = {"set_dir": str(r.set_dir), "manifest_md5": r.manifest_md5, "ext_md5": me,
                                "cand": c["cand"]}
        dumpfmt.write_manifest(dst, meta, {s: res[s] for s in r.stems})
        print(f"wrote {dst} ({cname(CANDS[c['index']])})", flush=True)
    pool.close(); pool.join()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("sweep", "write"))
    ap.add_argument("--seeds", default="5,6")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    C.check_tree()
    return sweep(a) if a.mode == "sweep" else write(a)


if __name__ == "__main__":
    sys.exit(main())
