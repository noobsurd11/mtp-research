"""Wave 2b post-read table: inactive count readouts (R1 to R5) and per-class prior-shift columns (G4, G5) with the
two-stage group bootstrap (w2b builder, 17 Nov 2026; harness/w2b/READ_PLAN_w2b.md sections 1 and 2).

Reads a FINISHED bench_read_w1.py read folder (<read>/read/read.json and the argmax records in <read>/cache_c/cache/,
as harness/w2a/read/w2a_class_guard.py does); reads no dump and no label. Per cell, from the record's 24 x 24 confusion
and its inactive components (the reviewed scorer bench_wt_b b5bf0ae bench/m0core.py: components >= 100 px):
  R1 inactive region recall  = GT regions >= 100 px with >= 50% of px predicted inactive / GT regions >= 100 px
  R1b inactive region precision = predicted regions >= 100 px that touch GT inactive / predicted regions >= 100 px
  R2 predicted inactive px on the cells without GT inactive (and their count)
  R3 inactive precision, R4 predicted / GT inactive px, R5 inactive IoU (pooled)
  per class c: IoU, pred / GT px, pred px on cells without GT c
Point = mean over seeds of the pooled value; contrast B - A with a two-stage bootstrap exactly as bench_wt_b
bench/crossfit_op.boot_pair (groups with replacement, then one seed per fold: one draw per (fold, arm), or one shared draw
with ':paired' for two readouts of the same runs), 2,000 draws, seed 0.
Usage (from anywhere; CPU):
  python w2b_counts.py --read <read folder> --pair PFC=LCI --pair LCIARG=LCI:paired [--classes 11,13,15,16,20]
         [--exclude <stem list>] --out <file>
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

NC, INACT = 24, 11
GROUPS = "/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/cv5v2_groups.tsv"
NF = 9 + 4 * NC     # 9 inactive columns, then per class: TP, pred, GT, pred on cells without GT of the class


def features(rec: dict) -> np.ndarray:
    C = np.asarray(rec["conf"], np.int64).reshape(NC, NC)      # rows GT, columns prediction (scored px)
    gt, pr, tp = C.sum(1), C.sum(0), np.diag(C)
    gi = [c for c in rec["inact_cc"]["gt"] if c[0] >= 100]
    pi = [c for c in rec["inact_cc"]["pr"] if c[0] >= 100]
    v = np.zeros(NF, np.int64)
    v[0], v[1] = len(gi), sum(c[1] >= 0.5 * c[0] for c in gi)
    v[2], v[3] = len(pi), sum(c[1] > 0 for c in pi)
    v[4], v[5], v[6] = tp[INACT], pr[INACT], gt[INACT]
    v[7] = pr[INACT] if gt[INACT] == 0 else 0
    v[8] = int(gt[INACT] == 0)
    o = 9
    v[o:o + NC], v[o + NC:o + 2 * NC], v[o + 2 * NC:o + 3 * NC] = tp, pr, gt
    v[o + 3 * NC:o + 4 * NC] = np.where(gt == 0, pr, 0)
    return v


def metrics(v: np.ndarray, classes: list[int]) -> dict:
    d = lambda a, b: float(a / b) if b else float("nan")  # noqa: E731
    m = {"R1_region_recall": d(v[1], v[0]), "R1b_region_prec": d(v[3], v[2]), "R2_fa_px": float(v[7]),
         "R2_cells": float(v[8]), "R3_inact_prec": d(v[4], v[5]), "R4_area_ratio": d(v[5], v[6]),
         "R5_inact_iou": d(v[4], v[5] + v[6] - v[4])}
    o = 9
    for c in classes:
        tp, pr, gt, fa = v[o + c], v[o + NC + c], v[o + 2 * NC + c], v[o + 3 * NC + c]
        m[f"c{c}_iou"], m[f"c{c}_area"], m[f"c{c}_fa_px"] = d(tp, pr + gt - tp), d(pr, gt), float(fa)
    return m


def load(read: Path, exclude: set) -> tuple[dict, dict, list, dict]:
    doc = json.loads((read / "read" / "read.json").read_text())
    arms, fold_of = {}, {}
    for r in doc["runs"]:
        fs = sorted((read / "cache_c" / "cache" / r["arm"] / r["run_id"]).glob("rec_argmax_*.json"))
        assert len(fs) == 1, (r["arm"], r["run_id"], len(fs))
        rec = json.loads(fs[0].read_text())
        d = arms.setdefault(r["arm"], {}).setdefault(int(r["seed"]), {})
        for s, x in rec.items():
            assert s not in d, (r["arm"], r["seed"], s)
            d[s] = x
            assert fold_of.setdefault(s, int(r["fold"])) == int(r["fold"]), s
    stems = sorted(s for s in fold_of if s not in exclude)
    for a, by in arms.items():
        for sd, d in by.items():
            assert set(stems) <= set(d), f"{a} seed {sd}: {len(set(stems) - set(d))} cells missing"
    return doc, arms, stems, fold_of


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--read", required=True)
    ap.add_argument("--pair", action="append", default=[], help="A=B or A=B:paired (contrast B - A)")
    ap.add_argument("--classes", default="11,13,15,16,20")
    ap.add_argument("--exclude", default=None, help="stem list to leave out (e.g. score_exclude_v3.txt)")
    ap.add_argument("--groups", default=GROUPS)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    jout = Path(str(out) + ".json")     # the same numbers, machine-readable (read by w2b_verdict.py)
    if out.exists() or jout.exists():
        sys.exit(f"refuse: {out} or {jout} exists")
    excl = set(Path(a.exclude).read_text().split()) if a.exclude else set()
    classes = [int(c) for c in a.classes.split(",")]
    doc, arms, stems, fold_of = load(Path(a.read), excl)
    rows = [l.split("\t") for l in Path(a.groups).read_text().splitlines() if l.strip()]
    gi = rows[0].index("group")
    groups = {r[0]: r[gi] for r in rows[1:]}             # cv5v2_groups.tsv: stem, legacy_split, group, fold
    assert doc.get("groups_md5") in (None, __import__("hashlib").md5(Path(a.groups).read_bytes()).hexdigest()), \
        "groups file differs from the read's"
    X = {arm: {sd: np.stack([features(c[s]) for s in stems]) for sd, c in by.items()} for arm, by in arms.items()}
    L = [f"# w2b_counts on {a.read} (read tool {doc['tool_md5'][:8]}); {len(stems)} cells"
         f"{f' (excluded {len(excl & set(fold_of))})' if excl else ''}; point = mean over seeds of pooled values"]
    pts = {}
    for arm, by in X.items():
        per = [metrics(x.sum(0), classes) for x in by.values()]
        pts[arm] = {k: float(np.nanmean([p[k] for p in per])) for k in per[0]}
    keys = list(next(iter(pts.values())))
    L.append("arm\tseeds\t" + "\t".join(keys))
    for arm in pts:
        L.append(f"{arm}\t{sorted(X[arm])}\t" + "\t".join(f"{pts[arm][k]:.6f}" for k in keys))
    J = {"read": str(a.read), "tool_md5": doc["tool_md5"], "n_cells": len(stems), "excluded": len(excl & set(fold_of)),
         "exclude_file": a.exclude, "classes": classes, "boot": a.boot, "points": pts, "contrasts": {}}
    folds = sorted(set(fold_of[s] for s in stems))
    fidx = {k: np.array([i for i, s in enumerate(stems) if fold_of[s] == k]) for k in folds}
    units = sorted({groups[s] for s in stems})
    uidx = {u: [i for i, s in enumerate(stems) if groups[s] == u] for u in units}
    for pr in a.pair:
        spec, _, mode = pr.partition(":")
        A, B = spec.split("=")
        paired = mode == "paired"
        sA, sB = sorted(X[A]), sorted(X[B])
        if paired:
            assert sA == sB, (sA, sB)
        rng = random.Random(0)
        draws = {k: [] for k in keys}
        for _ in range(a.boot):
            w = np.zeros(len(stems), np.int64)
            for _u in range(len(units)):
                w[uidx[units[rng.randrange(len(units))]]] += 1
            va, vb = np.zeros(NF, np.int64), np.zeros(NF, np.int64)
            for k in folds:
                da = sA[rng.randrange(len(sA))]
                db = da if paired else sB[rng.randrange(len(sB))]
                ix = fidx[k]
                va += w[ix] @ X[A][da][ix]
                vb += w[ix] @ X[B][db][ix]
            ma, mb = metrics(va, classes), metrics(vb, classes)
            for k in keys:
                draws[k].append(mb[k] - ma[k])
        L.append(f"\n## {B} - {A} ({'paired seeds' if paired else 'seeds drawn per arm'}; {len(units)} groups; "
                 f"{a.boot} draws): delta [2.5%, 97.5%], ratio B / A")
        cj = J["contrasts"][f"{B} - {A}"] = {"A": A, "B": B, "paired": paired, "metrics": {}}
        for k in keys:
            v = np.array([x for x in draws[k] if np.isfinite(x)])
            lo, hi = (np.percentile(v, 2.5), np.percentile(v, 97.5)) if len(v) else (np.nan, np.nan)
            ratio = pts[B][k] / pts[A][k] if pts[A][k] else float("nan")
            L.append(f"{k}\t{pts[B][k] - pts[A][k]:+.4f} [{lo:+.4f}, {hi:+.4f}]\tratio {ratio:.3f}")
            cj["metrics"][k] = {"delta": pts[B][k] - pts[A][k], "lo": float(lo), "hi": float(hi), "ratio": ratio}
    out.write_text("\n".join(L) + "\n")
    nan = lambda x: None if isinstance(x, float) and not np.isfinite(x) else x  # noqa: E731
    clean = lambda o: {k: clean(v) for k, v in o.items()} if isinstance(o, dict) else nan(o)  # noqa: E731
    jout.write_text(json.dumps(clean(J), indent=1))
    print(f"wrote {out} ({len(L)} lines)")


if __name__ == "__main__":
    main()
