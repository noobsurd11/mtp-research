"""Task 3: error census of COMBO (c3x HRNet-W18 U-Net++ PF + SWAD, swad readout) on the cv5v3 out-of-fold dumps, seeds
5 to 9 (25 runs, 532 cells per seed). Adds to the 15 Nov gap_census (PF, cv5v2) what it did not have; argmax (OP-A).

Per cell (k = not ignore; g = (gt == 14) & k; p = (pred == 14) & k; dp = EDT(~p); dg = EDT(~g)):
  missed = g & (dp > 2) (exactly the relR@2 miss of m0core.cell_stats); missed length = skeleton px of g (bench/skel.py,
    skeleton of the whole GT crack mask) with dp > 2.
  GT components: 8-connected (m0core.S8); length = skeleton px in the component (>= 1);
    length bucket LB = [1,10) [10,25) [25,50) [50,100) [100,200) [200,400) [400,inf);
    touch: busbar = within 2 px of GT busbars (9) or ribbons (4); edge = within 2 px of the image border or of GT
    border (5), padding (7) or frame_edge (21) px (ignore px count as their GT class here: GT is read raw for touch);
    categories none / busbar only / edge only / both.
  gap_census.census_cell (the 15 Nov buckets small / whole / gap / end, unchanged) on the same cell.
  False crack px: p & ~g by GT class (24 classes; ignore px separately: pred crack & ~k, i.e. scuff / star px of v1.1,
    not scored); and the same beyond 2 px of GT crack (p & (dg > 2): the relP@2 loss).
Counts are summed over cells and seeds; shares are ratios of sums. Intervals: gap_census.boot (two-stage group bootstrap,
cv5v3 groups, one seed per fold, 2,000 draws, Random(0)) with its FIELDS / STATS / ratios swapped for this census.

  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> census.py --seeds 5,6,7,8,9 --workers 8
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
import bench.gap_census as GC  # noqa: E402
from bench import cellmeta  # noqa: E402
from bench.cv5v3 import CLASS_NAMES  # noqa: E402
from bench.m0core import CRACK, NC, S8  # noqa: E402
from bench.skel import skeletonize  # noqa: E402

GC_FIELDS, GC_RATIOS = GC.FIELDS, GC.ratios                # originals (main() swaps the module attributes for GC.boot)

LB = (1, 10, 25, 50, 100, 200, 400, 10 ** 9)
LBN = tuple(f"[{a},{b})" if b < 10 ** 9 else f">={a}" for a, b in zip(LB[:-1], LB[1:]))
TN = ("none", "busbar", "edge", "both")
BUSBAR, EDGE = (4, 9), (5, 7, 21)
SRC = ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE")
CQ = ("g", "miss", "gsk", "msk", "nc", "ncw")              # per (bucket, touch): px, missed px, skel, missed skel, comps, whole-missed comps
NB, NT, NQ = len(LBN), len(TN), len(CQ)
OFF_COMP = 0
OFF_SRC = NB * NT * NQ                                      # per source: g, miss, gsk, msk
OFF_FP = OFF_SRC + len(SRC) * 4                             # FP strict by GT class (24)
OFF_FP2 = OFF_FP + NC                                       # FP beyond 2 px by GT class (24)
OFF_IGN = OFF_FP2 + NC                                      # pred crack on ignore px: all, beyond 2 px
OFF_GC = OFF_IGN + 2                                        # gap_census FIELDS
OFF_PP = OFF_GC + len(GC_FIELDS)                            # pred crack px in keep
NF = OFF_PP + 1
FIELDS = tuple(f"f{i}" for i in range(NF))


def ci(b, t, q):
    return OFF_COMP + (b * NT + t) * NQ + q


def _cell(a):
    set_dir, stem, gt_src = a
    d = GC.read_cell_lite(Path(set_dir) / f"{stem}.npz")
    gt, keep = cellmeta.load_gt(gt_src, stem)
    k = np.ones(gt.shape, bool) if keep is None else keep
    v = np.zeros(NF, np.int64)
    pred = d["pred"]
    g = (gt == CRACK) & k
    p = (pred == CRACK) & k
    v[OFF_PP] = int(p.sum())
    dp = ndi.distance_transform_edt(~p) if p.any() else np.full(g.shape, np.inf)
    dg = ndi.distance_transform_edt(~g) if g.any() else np.full(g.shape, np.inf)
    miss = g & (dp > 2)
    si = SRC.index(stem.split("_")[0])
    if g.any():
        sk = skeletonize(g)
        lab, n = ndi.label(g, S8)
        H, W = g.shape
        bb = np.isin(gt, BUSBAR)
        ed = np.isin(gt, EDGE)
        ed[0, :] = ed[-1, :] = True; ed[:, 0] = ed[:, -1] = True         # the image border row / column
        dbb = ndi.distance_transform_edt(~bb) if bb.any() else np.full(g.shape, np.inf)
        ded = ndi.distance_transform_edt(~ed)
        for i, sl in enumerate(ndi.find_objects(lab), start=1):
            Cm = lab[sl] == i
            ln = max(int((sk[sl] & Cm).sum()), 1)
            b = int(np.searchsorted(LB, ln, side="right") - 1)
            t = int((dbb[sl][Cm] <= 2).any()) + 2 * int((ded[sl][Cm] <= 2).any())
            gp, mp = int(Cm.sum()), int((miss[sl] & Cm).sum())
            v[ci(b, t, 0)] += gp
            v[ci(b, t, 1)] += mp
            v[ci(b, t, 2)] += ln
            v[ci(b, t, 3)] += int((sk[sl] & Cm & miss[sl]).sum())
            v[ci(b, t, 4)] += 1
            v[ci(b, t, 5)] += int(mp == gp)
        v[OFF_SRC + si * 4:OFF_SRC + si * 4 + 4] = (int(g.sum()), int(miss.sum()), int(sk.sum()), int((sk & miss).sum()))
    fp = p & ~g
    v[OFF_FP:OFF_FP + NC] = np.bincount(gt[fp].astype(np.int64), minlength=NC)[:NC]
    v[OFF_FP + CRACK] = 0
    fp2 = p & (dg > 2)
    v[OFF_FP2:OFF_FP2 + NC] = np.bincount(gt[fp2].astype(np.int64), minlength=NC)[:NC]
    pi = (pred == CRACK) & ~k
    v[OFF_IGN] = int(pi.sum()); v[OFF_IGN + 1] = int((pi & (dg > 2)).sum())
    gcv = GC.census_cell(pred, gt, keep, d["p_crack"])
    v[OFF_GC:OFF_GC + len(GC_FIELDS)] = GC.vec(gcv)
    return v


FPCAT = (("gridline", (15,)), ("busbar+ribbons", BUSBAR), ("background", (0,)), ("inactive", (11,)),
         ("material", (13,)), ("edge_dark", (20,)), ("spacing sp_*", (1, 2, 3)))


def ratios(x: np.ndarray) -> dict:
    x = x.astype(float)
    q = lambda a, b: a / b if b else float("nan")  # noqa: E731
    o = {}
    G = sum(x[ci(b, t, 0)] for b in range(NB) for t in range(NT))
    M = sum(x[ci(b, t, 1)] for b in range(NB) for t in range(NT))
    MS = sum(x[ci(b, t, 3)] for b in range(NB) for t in range(NT))
    o["relR2"] = q(G - M, G)
    for b in range(NB):
        mb = sum(x[ci(b, t, 1)] for t in range(NT)); gb = sum(x[ci(b, t, 0)] for t in range(NT))
        o[f"len{b}_share_miss"] = q(mb, M)
        o[f"len{b}_share_misssk"] = q(sum(x[ci(b, t, 3)] for t in range(NT)), MS)
        o[f"len{b}_missrate"] = q(mb, gb)
        o[f"len{b}_share_gt"] = q(gb, G)
    for t in range(NT):
        mt = sum(x[ci(b, t, 1)] for b in range(NB)); gt_ = sum(x[ci(b, t, 0)] for b in range(NB))
        o[f"touch{t}_share_miss"] = q(mt, M)
        o[f"touch{t}_share_misssk"] = q(sum(x[ci(b, t, 3)] for b in range(NB)), MS)
        o[f"touch{t}_missrate"] = q(mt, gt_)
        o[f"touch{t}_share_gt"] = q(gt_, G)
    for i, s in enumerate(SRC):
        gs, ms, gk, mk = x[OFF_SRC + i * 4:OFF_SRC + i * 4 + 4]
        o[f"src{i}_share_miss"] = q(ms, M)
        o[f"src{i}_share_misssk"] = q(mk, MS)
        o[f"src{i}_missrate"] = q(ms, gs)
        o[f"src{i}_share_gt"] = q(gs, G)
    for tag, off, io in (("fp", OFF_FP, OFF_IGN), ("fp2", OFF_FP2, OFF_IGN + 1)):
        tot = x[off:off + NC].sum() + x[io]
        o[f"{tag}_ignore"] = q(x[io], tot)
        rest = tot - x[io]
        for name, cl in FPCAT:
            s = sum(x[off + c] for c in cl)
            o[f"{tag}_{name}"] = q(s, tot); rest -= s
        o[f"{tag}_other"] = q(rest, tot)
        o[f"{tag}_px_per_seedcell"] = tot
    f0 = GC.FIELDS
    GC.FIELDS = GC_FIELDS                                   # GC.ratios reads its module FIELDS; restore it for this call
    try:
        gr = GC_RATIOS(x[OFF_GC:OFF_GC + len(GC_FIELDS)])
    finally:
        GC.FIELDS = f0
    for kk in ("share_small", "share_whole", "share_gap", "share_end", "bound_gap", "bound_end", "bound_whole"):
        o[f"gc_{kk}"] = gr[kk]
    return o


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="5,6,7,8,9")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    C.check_tree()
    od = C.OUT / "census"
    assert not (od / "census.txt").exists(), "refuse: census.txt exists"
    od.mkdir(parents=True, exist_ok=True)
    runs = C.combo_runs([int(x) for x in a.seeds.split(",")])
    pool = get_context("fork").Pool(a.workers)
    X, fold_of = {}, {}
    for r in runs:
        cp = od / f"cells_{r.run_id}_{r.manifest_md5[:8]}.npy"
        if cp.exists():
            V = np.load(cp)
        else:
            V = np.stack(pool.map(_cell, [(str(r.set_dir), s, r.gt) for s in r.stems], chunksize=2))
            np.save(cp, V)
        for s in r.stems:
            fold_of[s] = r.fold
        X.setdefault(r.seed, {}).update(dict(zip(r.stems, V)))
        print(f"census {r.run_id}", flush=True)
    pool.close(); pool.join()
    stems = sorted(fold_of, key=lambda s: (fold_of[s], s))
    Xs = {sd: np.stack([d[s] for s in stems]) for sd, d in X.items()}
    tot = sum(x.sum(0) for x in Xs.values())
    pt = ratios(tot)
    # gap_census.boot with this census's vector and ratios (module attributes swapped; the bootstrap code is unchanged)
    GC.FIELDS, GC.STATS, GC.ratios = FIELDS, tuple(pt), ratios
    bt = GC.boot(Xs, stems, fold_of, C.groups(), n_boot=a.boot)["stats"]
    f = lambda k: f"{bt[k]['value']:.3f} [{bt[k]['lo']:.3f}, {bt[k]['hi']:.3f}]"  # noqa: E731
    nsd = len(Xs)
    L = [f"# task 3 census: COMBO swad readout, cv5v3 OOF, seeds {a.seeds} ({nsd} x {len(stems)} cells); argmax; "
         "share = of all missed GT crack px (relR@2 miss) summed over cells and seeds; [95% CI] two-stage group bootstrap",
         f"relR@2 {f('relR2')}; GT crack px per seed {tot[[ci(b, t, 0) for b in range(NB) for t in range(NT)]].sum() / nsd:.0f}; "
         f"missed px per seed {tot[[ci(b, t, 1) for b in range(NB) for t in range(NT)]].sum() / nsd:.0f}",
         "\n## missed crack by GT component length (skeleton px)",
         "bucket\tcomps/seed\twhole-missed comps/seed\tshare of GT px\tmiss rate (1 - relR@2 in bucket)\tshare of missed px\tshare of missed skeleton length"]
    for b in range(NB):
        nc = sum(tot[ci(b, t, 4)] for t in range(NT)) / nsd; nw = sum(tot[ci(b, t, 5)] for t in range(NT)) / nsd
        L.append(f"{LBN[b]}\t{nc:.1f}\t{nw:.1f}\t{f(f'len{b}_share_gt')}\t{f(f'len{b}_missrate')}\t{f(f'len{b}_share_miss')}\t"
                 f"{f(f'len{b}_share_misssk')}")
    L += ["\n## missed crack by contact (component within 2 px of busbar / ribbon GT, of the cell edge (image border, border, padding, frame_edge GT))",
          "contact\tcomps/seed\tshare of GT px\tmiss rate\tshare of missed px\tshare of missed skeleton length"]
    for t in range(NT):
        nc = sum(tot[ci(b, t, 4)] for b in range(NB)) / nsd
        L.append(f"{TN[t]}\t{nc:.1f}\t{f(f'touch{t}_share_gt')}\t{f(f'touch{t}_missrate')}\t{f(f'touch{t}_share_miss')}\t"
                 f"{f(f'touch{t}_share_misssk')}")
    L.append("\nlength x contact: share of missed px (point)")
    L.append("bucket\t" + "\t".join(TN))
    M = tot[[ci(b, t, 1) for b in range(NB) for t in range(NT)]].sum()
    for b in range(NB):
        L.append(f"{LBN[b]}\t" + "\t".join(f"{tot[ci(b, t, 1)] / M:.3f}" for t in range(NT)))
    L += ["\n## missed crack by source", "source\tshare of GT px\tmiss rate\tshare of missed px\tshare of missed skeleton length"]
    for i, s in enumerate(SRC):
        L.append(f"{s}\t{f(f'src{i}_share_gt')}\t{f(f'src{i}_missrate')}\t{f(f'src{i}_share_miss')}\t{f(f'src{i}_share_misssk')}")
    L += ["\n## 15 Nov gap_census buckets on COMBO (bench/gap_census.census_cell unchanged)",
          "\t".join(f"{k} {f('gc_' + k)}" for k in ("share_small", "share_whole", "share_gap", "share_end")),
          "\t".join(f"{k} {f('gc_' + k)}" for k in ("bound_gap", "bound_end", "bound_whole"))]
    for tag, title in (("fp", "false crack px = pred crack px not on GT crack"),
                       ("fp2", "false crack px beyond 2 px of GT crack (the relP@2 loss)")):
        L += [f"\n## {title}, by the GT class under them (ignore = v1.1 scuff / star px, not scored)",
              f"total per seed {bt[f'{tag}_px_per_seedcell']['value'] / nsd:.0f} px"]
        for name in ("gridline", "busbar+ribbons", "ignore", "background", "inactive", "material", "edge_dark",
                     "spacing sp_*", "other"):
            L.append(f"{name}\t{f(f'{tag}_{name}')}")
        off = OFF_FP if tag == "fp" else OFF_FP2
        L.append("per class (point): " + ", ".join(f"{CLASS_NAMES[c]} {tot[off + c] / max(tot[off:off + NC].sum() + tot[OFF_IGN + (tag == 'fp2')], 1):.3f}"
                                                for c in np.argsort(-tot[off:off + NC]) if tot[off + c] > 0))
    (od / "census.json").write_text(json.dumps({"point": pt, "boot": bt, "seeds": sorted(Xs), "n_stems": len(stems)},
                                               indent=1, default=float))
    (od / "census.txt").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
