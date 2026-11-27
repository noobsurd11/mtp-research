"""Synthetic-case tests of w2b_verdict.py (w2b builder, 17 Nov 2026). No real data: every case builds a read.json-like
dict and two w2b_counts-like dicts in memory, changes one number from an all-pass base, and checks the line verdicts and
the final sentence. Run: python w2b_verdict_test.py  (prints one line per case and 'N of N passed')."""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w2b_verdict as W  # noqa: E402

KEYS = ("crack_iou", "relF1_2", "inact_iou", "miou_rob")
M = {"crack_iou": 0.01, "relF1_2": 0.01, "inact_iou": 0.054, "miou_rob": 0.01}


def ci(d, lo=None, hi=None):
    return {"delta": d, "lo": d - 0.005 if lo is None else lo, "hi": d + 0.005 if hi is None else hi, "se": 0.003}


def contrast(miou=0.0, crack=0.0, rel=0.0, inact=0.0):
    m = {"miou_rob": ci(miou), "crack_iou": ci(crack), "relF1_2": ci(rel), "inact_iou": ci(inact)}
    return {"OP-A": {"metrics": copy.deepcopy(m)}, "OP-F": {"metrics": copy.deepcopy(m)}, "OP-W": {"metrics": copy.deepcopy(m)}}


def summary(width=1.0, fa=300.0):
    subs = ["all"] + [f"src:{s}" for s in W.SOURCES]
    return {"OP-A": {s: {"width_ratio": {"mean": width}, "fa_px": {"mean": fa}} for s in subs}}


def doc_for(arm):
    cons = {f"{arm} - PFC": contrast(miou=0.02), f"{arm} - PF": contrast(miou=0.03)}
    d = {"M": dict(M), "contrasts": cons, "summary": {"PF": summary(), arm: summary()}}
    d["x416"] = {"M": dict(M), "contrasts": copy.deepcopy(cons), "summary": copy.deepcopy(d["summary"])}
    return d


def pts(iou=0.5, area=1.0, fa=100.0, r=(0.6, 0.0, 1000.0, 484.0, 0.75, 0.8, 0.5)):
    p = {"R1_region_recall": r[0], "R1b_region_prec": r[1], "R2_fa_px": r[2], "R2_cells": r[3], "R3_inact_prec": r[4],
         "R4_area_ratio": r[5], "R5_inact_iou": r[6]}
    for c in W.R13:
        p[f"c{c}_iou"], p[f"c{c}_area"], p[f"c{c}_fa_px"] = iou, area, fa
    return p


def counts(arm, excluded=0):
    c = {"excluded": excluded, "points": {"PF": pts(), "PFC": pts(), arm: pts()}, "contrasts": {}}
    if arm == "LCI":
        c["points"]["LCIARG"] = pts()
        c["points"]["LCI"] = pts(r=(0.65, 0.0, 1000.0, 484.0, 0.75, 0.8, 0.52))
        c["contrasts"]["LCI - PFC"] = {"metrics": {"R1_region_recall": ci(0.05, 0.01, 0.09)}}
        c["contrasts"]["LCI - LCIARG"] = {"metrics": {"R5_inact_iou": ci(0.02)}}
    return c


def run(arm, mut=None):
    a = "LACE" if arm == "lace" else "LCI"
    d, c5, c4 = doc_for(a), counts(a), counts(a, excluded=116)
    if mut:
        mut(d, c5, c4)
    v = (W.verdict_lace if arm == "lace" else W.verdict_lci)(d, c5, c4)
    return v.res, v.lines[-1]


def setm(d, path, val):
    x = d
    for p in path[:-1]:
        x = x[p]
    x[path[-1]] = val


CASES = []


def case(name, arm, mut, want_final, want_fail=()):
    CASES.append((name, arm, mut, want_final, tuple(want_fail)))


# ---- la_ce
case("lace all pass", "lace", None, "PROMOTE")
case("P1 at M exactly passes", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(0.010)), "PROMOTE")
case("P1 532 below M, point > 0", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(0.008)), "PARK", ["P1 532"])
case("P1 532 CI low <= 0", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(0.012, -0.001)), "PARK", ["P1 532"])
case("P1 416 fails only (leak-driven pass)", "lace", lambda d, a, b: setm(d, ["x416", "contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(0.004)), "PARK", ["P1 416"])
case("P1 532 point <= 0 -> drop", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(0.0)), "DROP", ["P1 532"])
case("P1 416 point < 0 -> drop", "lace", lambda d, a, b: setm(d, ["x416", "contrasts", "LACE - PFC", "OP-A", "metrics", "miou_rob"], ci(-0.002)), "DROP", ["P1 416"])
case("P2 532 fails", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PF", "OP-A", "metrics", "miou_rob"], ci(0.009)), "PARK", ["P2 532"])
case("P2 416 CI low <= 0", "lace", lambda d, a, b: setm(d, ["x416", "contrasts", "LACE - PF", "OP-A", "metrics", "miou_rob"], ci(0.03, 0.0)), "PARK", ["P2 416"])
case("G1 crack IoU OP-A at -M passes", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PF", "OP-A", "metrics", "crack_iou"], ci(-0.010)), "PROMOTE")
case("G1 crack IoU OP-A below -M -> drop", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PF", "OP-A", "metrics", "crack_iou"], ci(-0.011)), "DROP", ["G1 crack_iou OP-A"])
case("G1 relF1 OP-W below -M -> drop", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PF", "OP-W", "metrics", "relF1_2"], ci(-0.02)), "DROP", ["G1 relF1_2 OP-W"])
case("G1 judged on 532 only (416 crack loss printed)", "lace", lambda d, a, b: setm(d, ["x416", "contrasts", "LACE - PF", "OP-A", "metrics", "crack_iou"], ci(-0.05)), "PROMOTE")
case("G2 inactive below -M_inact", "lace", lambda d, a, b: setm(d, ["contrasts", "LACE - PFC", "OP-A", "metrics", "inact_iou"], ci(-0.06)), "PARK", ["G2 inactive IoU"])
case("G3 one class -0.031", "lace", lambda d, a, b: a["points"]["LACE"].update({"c16_iou": 0.469}), "PARK", ["G3 per R13 class"])
case("G3 crack class counts too", "lace", lambda d, a, b: a["points"]["LACE"].update({"c14_iou": 0.46}), "PARK", ["G3 per R13 class"])
case("G4 area 1.16 x", "lace", lambda d, a, b: a["points"]["LACE"].update({"c15_area": 1.16}), "PARK", ["G4 area ratio x PFC"])
case("G4 area 0.84 x", "lace", lambda d, a, b: a["points"]["LACE"].update({"c13_area": 0.84}), "PARK", ["G4 area ratio x PFC"])
case("G4 area 1.15 x passes", "lace", lambda d, a, b: a["points"]["LACE"].update({"c13_area": 1.15}), "PROMOTE")
case("G5 false px 1.51 x", "lace", lambda d, a, b: a["points"]["LACE"].update({"c16_fa_px": 151.0}), "PARK", ["G5 px on cells without class"])
case("G5 false px 1.5 x passes (not 1.15)", "lace", lambda d, a, b: a["points"]["LACE"].update({"c16_fa_px": 150.0}), "PROMOTE")
case("G5 PFC 0, LACE > 0 fails", "lace", lambda d, a, b: (a["points"]["PFC"].update({"c20_fa_px": 0.0}), a["points"]["LACE"].update({"c20_fa_px": 1.0})), "PARK", ["G5 px on cells without class"])
case("width outside band is a flag only", "lace", lambda d, a, b: setm(d, ["summary", "LACE", "OP-A", "src:ARTS", "width_ratio", "mean"], 1.3), "PROMOTE")
case("drop wins over promotion lines", "lace", lambda d, a, b: (setm(d, ["contrasts", "LACE - PF", "OP-W", "metrics", "crack_iou"], ci(-0.03))), "DROP", ["G1 crack_iou OP-W"])
# ---- layered_ci
case("lci all pass", "lci", None, "PROMOTE")
case("L1 532 CI low <= 0", "lci", lambda d, a, b: a["contrasts"]["LCI - PFC"]["metrics"].update({"R1_region_recall": ci(0.03, -0.001)}), "PARK", ["L1 532"])
case("L1 416 fails", "lci", lambda d, a, b: b["contrasts"]["LCI - PFC"]["metrics"].update({"R1_region_recall": ci(0.02, -0.01)}), "PARK", ["L1 416"])
case("L1 point 0", "lci", lambda d, a, b: a["contrasts"]["LCI - PFC"]["metrics"].update({"R1_region_recall": ci(0.0, 0.0)}), "PARK", ["L1 532"])
case("L2 false alarms 1.16 x", "lci", lambda d, a, b: a["points"]["LCI"].update({"R2_fa_px": 1160.0}), "PARK", ["L2 false-alarm px"])
case("L2 1.15 x passes", "lci", lambda d, a, b: a["points"]["LCI"].update({"R2_fa_px": 1150.0}), "PROMOTE")
case("L3 precision -0.021", "lci", lambda d, a, b: a["points"]["LCI"].update({"R3_inact_prec": 0.729}), "PARK", ["L3 inactive precision"])
case("L4 area 1.2 x", "lci", lambda d, a, b: a["points"]["LCI"].update({"R4_area_ratio": 0.96}), "PARK", ["L4 area"])
case("L4 area 0.8 x", "lci", lambda d, a, b: a["points"]["LCI"].update({"R4_area_ratio": 0.64}), "PARK", ["L4 area"])
case("L5 IoU equal: park", "lci", lambda d, a, b: a["points"]["LCI"].update({"R5_inact_iou": 0.5}), "PARK", ["L5 direction"])
case("L5 IoU lower: drop", "lci", lambda d, a, b: a["points"]["LCI"].update({"R5_inact_iou": 0.49}), "DROP", ["L5 direction"])
case("L6 mechanism <= 0: drop", "lci", lambda d, a, b: a["contrasts"]["LCI - LCIARG"]["metrics"].update({"R5_inact_iou": ci(0.0)}), "DROP", ["L6 mechanism"])
case("L7 crack IoU OP-W: drop", "lci", lambda d, a, b: setm(d, ["contrasts", "LCI - PF", "OP-W", "metrics", "crack_iou"], ci(-0.02)), "DROP", ["L7 crack_iou OP-W"])
case("L7 relF1 OP-A: drop", "lci", lambda d, a, b: setm(d, ["contrasts", "LCI - PF", "OP-A", "metrics", "relF1_2"], ci(-0.011)), "DROP", ["L7 relF1_2 OP-A"])
case("L7 width pooled: drop", "lci", lambda d, a, b: setm(d, ["summary", "LCI", "OP-A", "all", "width_ratio", "mean"], 1.2), "DROP", ["L7 width pooled"])
case("L7 width BMRK: drop", "lci", lambda d, a, b: setm(d, ["summary", "LCI", "OP-A", "src:BMRK", "width_ratio", "mean"], 0.8), "DROP", ["L7 width BMRK"])
case("L7 false crack px 1.6 x: drop", "lci", lambda d, a, b: setm(d, ["summary", "LCI", "OP-A", "all", "fa_px", "mean"], 480.0), "DROP", ["L7 false crack px"])
case("L7 false crack px 1.5 x passes", "lci", lambda d, a, b: setm(d, ["summary", "LCI", "OP-A", "all", "fa_px", "mean"], 450.0), "PROMOTE")


def main() -> int:
    ok_n = 0
    for name, arm, mut, want_final, want_fail in CASES:
        res, final = run(arm, mut)
        fails = sorted(n for n, ok in res.items() if not ok)
        ok = f": {want_final}" in final and fails == sorted(want_fail)
        ok_n += ok
        print(f"{'OK  ' if ok else 'FAIL'} {arm:4s} {name}: {final.split(' (')[0]}; failed lines {fails}")
    # the CLI refuses a 416 counts file that is not the clean set, and a c532 file that excludes cells
    try:
        W.main(["--arm", "lace", "--read", "/nonexistent", "--c532", "/x", "--c416", "/y"])
        cli = False
    except (FileNotFoundError, AssertionError):
        cli = True
    print(f"{'OK  ' if cli else 'FAIL'} cli: missing inputs refuse")
    total = len(CASES) + 1
    print(f"{ok_n + cli} of {total} passed")
    return 0 if ok_n + cli == total else 1


if __name__ == "__main__":
    sys.exit(main())
