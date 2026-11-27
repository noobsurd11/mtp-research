"""Wave 2a, post-read table for the rcs read guard of LAUNCH_REQUEST_w2a.md section 8 ("per-class IoU splice / edge_dark /
material"; builder, 17 Nov 2026). bench_read_w1.py at b5bf0ae prints inactive precision (inact_prec) and inactive region
precision (in_cc_prec) per arm, but no per-class IoU of other classes. Its cache holds, per run, the argmax record of
every cell with the 24 x 24 confusion matrix. This script only tabulates those records with the read tree's own
bench.score_ext.summarize (the function the read's guards use): per arm and class the IoU, precision and recall pooled
over the out-of-fold cells, mean (sd) over seeds, and the difference of the means to the baseline arm. Descriptive: no
interval, no pass flag. Operating point: argmax (OP-A); OP-F and OP-W move only crack against the other classes.

It needs a FINISHED read folder of run_read_w2a.sh (<read>/read/read.json and <read>/cache_c/cache/). It reads no dump
and no label. The table goes to --out (refuses to overwrite); nothing but the file name is printed.

  cd /home/noob/work/bench_wt_b && CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 \
    /home/noob/work/el-fault-detection/.venv/bin/python <this file> --read /home/noob/work/bench_reads/w2a \
    --out /home/noob/work/bench_reads/w2a/class_guard.txt [--classes 13,16,20,11] [--baseline PF]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RB = Path("/home/noob/work/bench_wt_final")
sys.path.insert(0, str(RB))
from bench.atlas import NAME  # noqa: E402
from bench.score_ext import summarize  # noqa: E402


def ms(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return (float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0, len(v)) if v else (float("nan"), float("nan"), 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True, help="output folder of run_read_w2a.sh")
    ap.add_argument("--out", required=True)
    ap.add_argument("--classes", default="13,16,20,11")
    ap.add_argument("--baseline", default="PF")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    rd = Path(a.read)
    doc = json.loads((rd / "read" / "read.json").read_text())
    classes = [int(c) for c in a.classes.split(",")]
    cells = {}                                             # (arm, seed) -> {stem: record}
    for r in doc["runs"]:
        fs = sorted((rd / "cache_c" / "cache" / r["arm"] / r["run_id"]).glob("rec_argmax_*.json"))
        assert len(fs) == 1, f"{r['arm']} {r['run_id']}: expected one argmax record file in the cache, found {len(fs)}"
        rec = json.loads(fs[0].read_text())
        d = cells.setdefault((r["arm"], r["seed"]), {})
        assert not (set(d) & set(rec)), f"{r['arm']} seed {r['seed']}: a cell is in two runs"
        d.update(rec)
    n = doc["n_stems"]
    assert all(len(d) == n for d in cells.values()), {k: len(d) for k, d in cells.items()}
    arms = list(dict.fromkeys(r["arm"] for r in doc["runs"]))
    assert a.baseline in arms, (a.baseline, arms)
    excl = set(doc.get("score_exclude", {}).get("stems", []))
    L = [f"# per-class guard table from the argmax records of {rd} (read tool {doc['tool_md5'][:8]}); {n} OOF cells; "
         f"IoU / precision / recall pooled over cells, mean (sd) over seeds; delta = arm mean - {a.baseline} mean; descriptive"]
    for title, keep in ((f"all {n} cells", lambda s: True),) + (((f"{n - len(excl)} clean cells", lambda s: s not in excl),) if excl else ()):
        L.append(f"\n## {title}")
        L.append("arm\tseeds\tclass\tname\tGT px (mean)\tIoU mean (sd)\tdelta IoU\tprecision mean\trecall mean")
        res = {}
        for arm in arms:
            per = [summarize(d, keep)["per_class"] for (x, _), d in sorted(cells.items()) if x == arm]
            res[arm] = {c: {k: ms([p[c][k] for p in per]) for k in ("iou", "prec", "rec", "gt_px")} for c in classes}
        for arm in arms:
            for c in classes:
                v, b = res[arm][c], res[a.baseline][c]
                L.append(f"{arm}\t{v['iou'][2]}\t{c}\t{NAME.get(c, c)}\t{v['gt_px'][0]:.0f}\t{v['iou'][0]:.4f} ({v['iou'][1]:.3f})\t"
                         f"{v['iou'][0] - b['iou'][0]:+.4f}\t{v['prec'][0]:.4f}\t{v['rec'][0]:.4f}")
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out} ({len(L)} lines; arms {arms}; classes {classes})")


if __name__ == "__main__":
    main()
