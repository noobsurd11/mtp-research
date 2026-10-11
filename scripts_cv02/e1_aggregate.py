"""E1 aggregation: per-arm task metrics with image-bootstrap CIs, and paired contrasts (definitions: results/e1/README.md).

Usage: python e1_aggregate.py <raw dir> [--pairs A=B ...] [--merge NEW=ARM1+ARM2 ...] > table.txt
An arm is a run name without its ``_s<seed>`` suffix. Per bootstrap resample the metric is computed per run on the
resampled cells, then averaged over the arm's seeds; contrasts reuse the same resample for both arms (paired).
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

B, RNG = 2000, np.random.default_rng(0)
FIELDS = ["crack_gt", "crack_pred", "crack_tp", "crack_p2_hit", "crack_r2_hit", "crack_len_gt", "crack_len_pred",
          "area", "inact_gt", "inact_pred", "inact_tp", "inact_union"]


def arrays(cells: dict, stems: list[str]) -> dict:
    return {k: np.array([cells[s].get(k, 0) for s in stems], dtype=np.float64) for k in FIELDS}


def metrics(a: dict, idx: np.ndarray) -> dict:
    g = {k: v[idx] for k, v in a.items()}
    out = {}
    cm = g["crack_gt"] >= 20
    P = np.where(g["crack_pred"] > 0, g["crack_p2_hit"] / np.maximum(g["crack_pred"], 1), 0.0)
    R = g["crack_r2_hit"] / np.maximum(g["crack_gt"], 1)
    F = np.where(P + R > 0, 2 * P * R / np.maximum(P + R, 1e-12), 0.0)
    out["crack_tolF1"] = F[cm].mean() if cm.any() else np.nan
    le = np.abs(g["crack_len_pred"] - g["crack_len_gt"]) / np.maximum(g["crack_len_gt"], 1)
    out["crack_len_err"] = np.median(le[cm]) if cm.any() else np.nan
    neg = g["crack_gt"] < 20
    out["crack_false_alarm"] = (g["crack_pred"][neg] >= 50).mean() if neg.any() else np.nan
    tp, gt, pr = g["crack_tp"].sum(), g["crack_gt"].sum(), g["crack_pred"].sum()
    out["crack_iou_pooled"] = tp / max(gt + pr - tp, 1)
    rp, rr = g["crack_p2_hit"].sum() / max(pr, 1), g["crack_r2_hit"].sum() / max(gt, 1)
    out["crack_relF1_2_pooled"] = 2 * rp * rr / max(rp + rr, 1e-12)
    ag, ap = g["inact_gt"] / g["area"], g["inact_pred"] / g["area"]
    out["inact_area_err_pp"] = 100 * np.abs(ap - ag).mean()
    gp, pp = ag >= 0.005, ap >= 0.005
    tpd = (gp & pp).sum()
    out["inact_det_F1"] = 2 * tpd / max(gp.sum() + pp.sum(), 1)
    out["inact_cell_iou"] = (g["inact_tp"][gp] / np.maximum(g["inact_union"][gp], 1)).mean() if gp.any() else np.nan
    itp, igt, ipr = g["inact_tp"].sum(), g["inact_gt"].sum(), g["inact_pred"].sum()
    out["inact_iou_pooled"] = itp / max(igt + ipr - itp, 1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--sets", nargs="+", default=["test", "ext", "both"])
    ap.add_argument("--pairs", nargs="*", default=[])
    ap.add_argument("--arms", nargs="*", default=None, help="regexes of arms to tabulate (default all)")
    ap.add_argument("--merge", nargs="*", default=[], help="NEW=ARM1+ARM2: pool the seeds of two arms (seed sets must be disjoint)")
    a = ap.parse_args()
    runs = defaultdict(dict)  # arm -> seed -> cells
    for f in sorted(Path(a.raw).glob("*.json")):
        d = json.loads(f.read_text())
        m = re.match(r"(.+)_s(\d+)$", d["run"])
        runs[m.group(1)][int(m.group(2))] = d["cells"]
    for mg in a.merge:
        new, parts = mg.split("=")
        for part in parts.split("+"):
            if set(runs[new]) & set(runs[part]):
                raise SystemExit(f"--merge {mg}: overlapping seeds")
            runs[new].update(runs[part])
    arms = sorted(runs)
    if a.arms:
        arms = [x for x in arms if any(re.search(p, x) for p in a.arms)]
    for set_name in a.sets:
        def cells_of(c):
            if set_name == "both":
                return {**{f"t/{k}": v for k, v in c["test"].items()}, **{f"e/{k}": v for k, v in c["ext"].items()}}
            return c[set_name]
        first = cells_of(next(iter(runs[arms[0]].values())))
        stems = sorted(first)
        n = len(stems)
        boots = RNG.integers(0, n, size=(B, n))
        full = np.arange(n)
        arrs = {arm: [arrays(cells_of(c), stems) for c in runs[arm].values()] for arm in runs}
        names = list(metrics(arrs[arms[0]][0], full))
        def arm_metric(arm, idx):
            ms = [metrics(x, idx) for x in arrs[arm]]
            return {k: float(np.nanmean([m[k] for m in ms])) for k in names}
        print(f"\n## {set_name} ({n} cells): mean over seeds, [95% bootstrap half-width]")
        print("| arm | seeds | " + " | ".join(names) + " |")
        print("|---|---|" + "---|" * len(names))
        cache = {}
        for arm in arms:
            pt = arm_metric(arm, full)
            bs = [arm_metric(arm, idx) for idx in boots[:300]]  # 300 resamples for the per-arm half-widths
            cache[arm] = pt
            hw = {k: (np.nanpercentile([b[k] for b in bs], 97.5) - np.nanpercentile([b[k] for b in bs], 2.5)) / 2 for k in names}
            print(f"| {arm} | {len(arrs[arm])} | " + " | ".join(f"{pt[k]:.3f} [{hw[k]:.3f}]" for k in names) + " |")
        if a.pairs:
            print(f"\n### {set_name}: paired contrasts A − B, Δ [95% CI] (P(Δ>0)), {B} resamples")
            print("| contrast | " + " | ".join(names) + " |")
            print("|---|" + "---|" * len(names))
            for pr in a.pairs:
                A, Bn = pr.split("=")
                if A not in runs or Bn not in runs:
                    print(f"| {A} − {Bn} | missing |")
                    continue
                d0 = {k: arm_metric(A, full)[k] - arm_metric(Bn, full)[k] for k in names}
                ds = []
                for idx in boots:
                    ma, mb = arm_metric(A, idx), arm_metric(Bn, idx)
                    ds.append({k: ma[k] - mb[k] for k in names})
                cells_ = []
                for k in names:
                    v = np.array([x[k] for x in ds])
                    lo, hi = np.nanpercentile(v, [2.5, 97.5])
                    cells_.append(f"{d0[k]:+.3f} [{lo:+.3f}, {hi:+.3f}] ({np.nanmean(v > 0):.2f})")
                print(f"| {A} − {Bn} | " + " | ".join(cells_) + " |")
            # leave-top-3-out: drop the 3 cells with the most GT px of that class (GT is the same for every run)
            g0 = arrays(cells_of(next(iter(runs[arms[0]].values()))), stems)
            keep = {c: np.setdiff1d(full, np.argsort(-g0[f"{c}_gt"])[:3]) for c in ("crack", "inact")}
            ks = ["crack_iou_pooled", "crack_relF1_2_pooled", "inact_iou_pooled"]
            print(f"\n### {set_name}: Δ without the top-3 cells of that class (by GT px)")
            print("| contrast | " + " | ".join(ks) + " |\n|---|" + "---|" * len(ks))
            for pr in a.pairs:
                A, Bn = pr.split("=")
                if A in runs and Bn in runs:
                    d3 = [arm_metric(A, keep[k.split("_")[0]])[k] - arm_metric(Bn, keep[k.split("_")[0]])[k] for k in ks]
                    print(f"| {A} − {Bn} | " + " | ".join(f"{v:+.3f}" for v in d3) + " |")


if __name__ == "__main__":
    main()
