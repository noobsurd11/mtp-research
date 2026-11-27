"""Track M, M0: tables from m0_audit.py JSONs (CPU only).

IoU per class is pooled over the cells of a set. mIoU24: mean over the 24 classes of IoU, where a class with no GT and no
prediction in the set is excluded (NaN) and a class with no GT but some prediction scores 0. mIoU_gt: mean over classes
with GT in the set. Seeds are averaged after computing each run's metric.
"""
from __future__ import annotations

import argparse, json, re
from pathlib import Path

import numpy as np

NAMES = ["background", "sp_multi", "sp_mono", "sp_dogbone", "ribbons", "border", "text", "padding", "clamp", "busbars",
         "crack_rbn_edge", "inactive", "rings", "material", "crack", "gridline", "splice", "dead_cell", "corrosion",
         "belt_mark", "edge_dark", "frame_edge", "jbox", "meas_artifact"]
DEFECT = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23]
NC, CRACK, INACT = 24, 14, 11
NOISY = "CSIR_00070_r8_c4"
TWINS = ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4", "CFVS_00018_r4_c4",
         "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]


def src(s):
    return s.split("_")[0]


def agg(cells: dict, keep, cl=None) -> dict:
    st = [s for s in cells if keep(s)]
    C = sum(np.array(cells[s]["conf"], np.int64).reshape(NC, NC) for s in st)
    tp = np.diag(C).astype(float); gt = C.sum(1); pr = C.sum(0)
    den = gt + pr - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    prec = np.where(pr > 0, tp / np.maximum(pr, 1), np.nan)
    rec = np.where(gt > 0, tp / np.maximum(gt, 1), np.nan)
    rel = np.sum([cells[s]["crack_rel2"] for s in st], 0)
    rP, rR = rel[0] / max(rel[1], 1), rel[2] / max(rel[3], 1)
    out = {"n": len(st), "iou": iou, "prec": prec, "rec": rec, "gt": gt, "pr": pr,
           "miou24": np.nanmean(iou), "miou_gt": np.nanmean(np.where(gt > 0, iou, np.nan)),
           "miou_fix": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[0]]) if cl else np.nan,
           "miou_rob": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[1]]) if cl else np.nan,
           "miou_rob_no07": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in cl[1] if c not in (0, 7)]) if cl else np.nan,
           "miou_gt_no07": np.nanmean([iou[c] if gt[c] > 0 and c not in (0, 7) else np.nan for c in range(NC)]),
           "fp_absent_px": int(sum(pr[c] for c in range(NC) if gt[c] == 0)),
           "gt_cells": np.array([sum(1 for s in st if np.array(cells[s]["conf"]).reshape(NC, NC)[c].sum() > 0) for c in range(NC)]),
           "pband_gt": np.sum([cells[s].get("crack_pband_gt", [0] * 5) for s in st], 0),
           "pband_neg": np.sum([cells[s].get("crack_pband_neg", [0] * 5) for s in st], 0),
           "miou_def_gt": np.nanmean([iou[c] if gt[c] > 0 else np.nan for c in DEFECT]),
           "relP2": rP, "relR2": rR, "relF1": 2 * rP * rR / max(rP + rR, 1e-9)}
    # crack components: GT comp "found" if >= 50% of its px within 2 px of a prediction; also any-hit
    g = [c for s in st for c in cells[s]["crack_cc"]["gt"]]
    p = [c for s in st for c in cells[s]["crack_cc"]["pr"]]
    for mn in (1, 20):
        gg = [c for c in g if c[0] >= mn]
        out[f"cc_rec50_{mn}"] = np.mean([c[1] >= 0.5 * c[0] for c in gg]) if gg else np.nan
        out[f"cc_recany_{mn}"] = np.mean([c[1] > 0 for c in gg]) if gg else np.nan
        out[f"cc_n_{mn}"] = len(gg)
        pp = [c for c in p if c[0] >= mn]
        out[f"cc_prec_{mn}"] = np.mean([c[1] > 0 for c in pp]) if pp else np.nan
    gi = [c for s in st for c in cells[s]["inact_cc"]["gt"] if c[0] >= 100]
    out["in_cc_rec50"] = np.mean([c[1] >= 0.5 * c[0] for c in gi]) if gi else np.nan
    out["in_cc_n"] = len(gi)
    pi = [c for s in st for c in cells[s]["inact_cc"]["pr"] if c[0] >= 100]
    out["in_cc_prec"] = np.mean([c[1] > 0 for c in pi]) if pi else np.nan
    return out


def arm_of(run):
    return re.sub(r"_s\d+$", "", run)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--arms", nargs="+", help="NAME=regex")
    a = ap.parse_args()
    runs = {json.loads(f.read_text())["run"]: json.loads(f.read_text()) for f in sorted(Path(a.dir).glob("*.json"))}
    arms = {}
    for spec in a.arms:
        n, rx = spec.split("=", 1)
        arms[n] = sorted(r for r in runs if re.fullmatch(rx, r))
    subsets = {"all": lambda s: True, "-noisy": lambda s: s != NOISY, "-twins": lambda s: s not in TWINS,
               "-twins-noisy": lambda s: s not in TWINS and s != NOISY}
    for sp in ("test", "val", "val_tta", "ext"):
        print(f"\n## {sp}")
        for arm, rs in arms.items():
            print(f"\n### {arm} ({len(rs)} runs: {', '.join(rs)})")
            A0 = agg(runs[rs[0]]["cells"][sp], lambda s: True)
            cl = ([c for c in range(NC) if A0["gt"][c] > 0], [c for c in range(NC) if A0["gt_cells"][c] >= 3])
            print(f"class list (GT in all cells of {sp}): {cl[0]}; robust (>=3 cells): {cl[1]}")
            keys = ["miou_rob", "miou_rob_no07", "miou_fix", "miou24", "fp_absent_px", "miou_gt_no07", "miou_def_gt", "relP2", "relR2", "relF1", "cc_rec50_20", "cc_recany_20", "cc_prec_20",
                    "cc_rec50_1", "in_cc_rec50", "in_cc_prec"]
            sub = subsets if sp == "test" else {"all": subsets["all"]}
            print("| set | n | " + " | ".join(["crack IoU", "crack P", "crack R", "inact IoU", "inact P", "inact R"] + keys) + " |")
            print("|" + "---|" * (14 + len(keys) - 6 + 2))
            for nm, kf in sub.items():
                A = [agg(runs[r]["cells"][sp], kf, cl) for r in rs]
                miss = [c for c in cl[0] if A[0]["gt"][c] == 0]
                if miss: print(f"  ({nm}: no GT for classes {miss}, NaN)")
                def ms(f):
                    v = np.array([f(x) for x in A], float)
                    return f"{np.nanmean(v):.3f}±{np.nanstd(v, ddof=1) if len(v) > 1 else 0:.3f}"
                row = [ms(lambda x: x["iou"][CRACK]), ms(lambda x: x["prec"][CRACK]), ms(lambda x: x["rec"][CRACK]),
                       ms(lambda x: x["iou"][INACT]), ms(lambda x: x["prec"][INACT]), ms(lambda x: x["rec"][INACT])]
                row += [ms(lambda x, k=k: x[k]) for k in keys]
                print(f"| {nm} | {A[0]['n']} | " + " | ".join(row) + " |")
            # per-class table
            A = [agg(runs[r]["cells"][sp], subsets["all"]) for r in rs]
            print("\nper class (all cells): class | GT px | GT cells | IoU mean±sd | P | R")
            for c in range(NC):
                v = np.array([x["iou"][c] for x in A]); P = np.array([x["prec"][c] for x in A]); R = np.array([x["rec"][c] for x in A])
                fl = " (<3 cells)" if 0 < A[0]["gt_cells"][c] < 3 else ""
                print(f"| {c} {NAMES[c]} | {int(A[0]['gt'][c])} | {A[0]['gt_cells'][c]}{fl} | {np.nanmean(v):.3f}±{np.nanstd(v, ddof=1) if len(v) > 1 else 0:.3f} | "
                      f"{np.nanmean(P):.3f} | {np.nanmean(R):.3f} |" if not np.all(np.isnan(v)) else f"| {c} {NAMES[c]} | 0 | absent | | |")
            pb = np.mean([x["pband_gt"] / max(x["pband_gt"].sum(), 1) for x in A], 0)
            pn = np.mean([x["pband_neg"] for x in A], 0)
            print("\ncrack p-bands on GT crack px (<.001, .001-.1, .1-.5, .5-.95, >=.95):", " / ".join(f"{v:.3f}" for v in pb),
                  "| GT-neg px per band:", " / ".join(f"{v:.0f}" for v in pn))
            # per source
            if sp in ("test", "val", "ext"):
                print("\nper source: source | n | crack IoU | crack R | crack relR2 | crack relP2 | inact IoU | inact R | mIoU_rob (fixed list, NaN classes dropped)")
                for so in sorted({src(s) for s in runs[rs[0]]["cells"][sp]}):
                    for tw in (("all", lambda s, so=so: src(s) == so), ("-twins-noisy", lambda s, so=so: src(s) == so and s not in TWINS and s != NOISY)):
                        if sp != "test" and tw[0] != "all":
                            continue
                        A = [agg(runs[r]["cells"][sp], tw[1], cl) for r in rs]
                        if A[0]["n"] == 0:
                            continue
                        f = lambda k, c=None: np.nanmean([x[k][c] if c is not None else x[k] for x in A])
                        print(f"| {so} {tw[0]} | {A[0]['n']} | {f('iou', CRACK):.3f} | {f('rec', CRACK):.3f} | {f('relR2'):.3f} | {f('relP2'):.3f} | "
                              f"{f('iou', INACT):.3f} | {f('rec', INACT):.3f} | {f('miou_rob'):.3f} |")


if __name__ == "__main__":
    main()
