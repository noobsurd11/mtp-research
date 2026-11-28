"""Task 2: D4 label-safety audit, per class, from the registered final TTA read (bench_reads/final_tta, read tool
fdb56b78, 532 cv5v3 OOF cells, seeds 5 to 9). Reads ONLY that read's read.json and its cached argmax records
(final_tta/cache_c/cache/<arm>/<run_id>/rec_argmax_*.json: 24 x 24 confusion per cell, the records the read scored);
no dump, no label, nothing sealed.

Per class c (0..23) and pair (A -> A_D4; same checkpoints, D4 = 8 flips / rotations at test time):
  IoU pooled over the 532 cells, mean over seeds (bench.score_ext.summarize per_class, as final_class_guard.py);
  delta = A_D4 - A with a 95% interval from crossfit_op.boot_pair (the read's two-stage group bootstrap, cv5v3 groups
  d880a769, 2,000 draws, seed 0) with per-class IoU added to its metric function (fmetrics wrapped, nothing else
  changed). paired_seeds=True (two readouts of the same runs: one seed draw per fold for both); the unpaired interval
  (the read's default for contrasts) is printed beside it.
Flag: LOWERS if delta < 0 and the paired interval's upper end < 0; 'down, n.d.' if delta < 0 with the interval covering 0.
Primary pair CS -> CS_D4 (COMBO swad readout = the C2 recipe without / with D4); PF -> PF_D4 and CB -> CB_D4 beside it.

  PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= nice -n 19 <venv python> d4_audit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cpu_common as C  # noqa: E402
import bench.crossfit_op as co  # noqa: E402
from bench.cv5v3 import CLASS_NAMES  # noqa: E402
from bench.m0core import NC  # noqa: E402
from bench.score_ext import summarize  # noqa: E402

RD = Path("/home/noob/work/bench_reads/final_tta")
PAIRS = (("CS", "CS_D4"), ("PF", "PF_D4"), ("CB", "CB_D4"))
_F0 = co.fmetrics
CK = tuple(f"iou_{c}" for c in range(NC))


def fm(v):
    out = _F0(v)
    Cm = v[:NC * NC].reshape(NC, NC).astype(float)
    tp = np.diag(Cm); den = Cm.sum(1) + Cm.sum(0) - tp
    for c in range(NC):
        out[f"iou_{c}"] = tp[c] / den[c] if den[c] > 0 else float("nan")
    return out


co.fmetrics = fm
co.BOOT_KEYS = tuple(co.BOOT_KEYS) + CK


def main() -> int:
    C.check_tree()
    out = C.OUT / "d4" / "d4_audit.txt"
    assert not out.exists(), f"refuse: {out} exists"
    doc = json.loads((RD / "read" / "read.json").read_text())
    cells, fold_of = {}, {}
    for r in doc["runs"]:
        fs = sorted((RD / "cache_c" / "cache" / r["arm"] / r["run_id"]).glob("rec_argmax_*.json"))
        assert len(fs) == 1, (r["arm"], r["run_id"], len(fs))
        rec = json.loads(fs[0].read_text())
        d = cells.setdefault(r["arm"], {}).setdefault(r["seed"], {})
        assert not set(d) & set(rec)
        d.update(rec)
        for s in rec:
            assert fold_of.setdefault(s, r["fold"]) == r["fold"]
    stems = sorted(fold_of, key=lambda s: (fold_of[s], s))
    assert len(stems) == doc["n_stems"] == 532, len(stems)
    G = C.groups()
    L = [f"# task 2: D4 per-class audit from {RD} (read.json md5 e9692e7e per final_tta/MD5.txt); 532 cv5v3 OOF cells; "
         "seeds 5 to 9; argmax (OP-A) records; IoU pooled over cells, mean over seeds; delta = D4 - plain; "
         "95% CI two-stage group bootstrap (crossfit_op.boot_pair, cv5v3 groups, 2,000 draws), paired seeds | unpaired",
         "# training augmentation of all three arms: labelsafe = HFlip, VFlip, RandomRotate90 (D4 already seen in training)"]
    res = {}
    for A, B in PAIRS:
        bp = co.boot_pair(cells[A], cells[B], stems, fold_of, G, 2000, 0, paired_seeds=True)
        bu = co.boot_pair(cells[A], cells[B], stems, fold_of, G, 2000, 0, paired_seeds=False)
        pc = {arm: [summarize(cells[arm][sd])["per_class"] for sd in sorted(cells[arm])] for arm in (A, B)}
        L.append(f"\n## {A} -> {B}")
        L.append("class\tname\tGT px\tGT cells\tIoU plain\tIoU D4\tdelta\tpaired 95% CI\tunpaired 95% CI\tprec plain -> D4\t"
                 "rec plain -> D4\tflag")
        rows = []
        for c in range(NC):
            gp = pc[A][0][c]["gt_px"]; gc = pc[A][0][c]["gt_cells"]
            ia = np.nanmean([p[c]["iou"] for p in pc[A]]) if gp else float("nan")
            ib = np.nanmean([p[c]["iou"] for p in pc[B]]) if gp else float("nan")
            pa = np.nanmean([p[c]["prec"] for p in pc[A]]); pb = np.nanmean([p[c]["prec"] for p in pc[B]])
            ra = np.nanmean([p[c]["rec"] for p in pc[A]]); rb = np.nanmean([p[c]["rec"] for p in pc[B]])
            v, u = bp["metrics"][f"iou_{c}"], bu["metrics"][f"iou_{c}"]
            if not gp:
                flag = "no GT in pool"
            elif v["delta"] < 0 and v["hi"] < 0:
                flag = "LOWERS"
            elif v["delta"] < 0:
                flag = "down, n.d."
            elif v["lo"] > 0:
                flag = "raises"
            else:
                flag = "up, n.d."
            rows.append({"class": c, "name": CLASS_NAMES[c], "gt_px": gp, "gt_cells": gc, "iou_plain": ia, "iou_d4": ib,
                         "paired": v, "unpaired": u, "flag": flag})
            L.append(f"{c}\t{CLASS_NAMES[c]}\t{gp}\t{gc}\t{ia:.4f}\t{ib:.4f}\t{v['delta']:+.4f}\t"
                     f"[{v['lo']:+.4f}, {v['hi']:+.4f}]\t[{u['lo']:+.4f}, {u['hi']:+.4f}]\t{pa:.3f} -> {pb:.3f}\t"
                     f"{ra:.3f} -> {rb:.3f}\t{flag}")
        res[f"{A}->{B}"] = rows
    out.parent.mkdir(parents=True, exist_ok=True)
    (C.OUT / "d4" / "d4_audit.json").write_text(json.dumps(res, indent=1, default=float))
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
