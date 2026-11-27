"""Wave 2b screen verdict (w2b builder, 17 Nov 2026): applies the pre-registered rules of harness/w2b/READ_PLAN_w2b.md
(la_ce: P1, P2, G1 to G5; layered_ci: L1 to L7; lead's rulings log.md "17 Nov 17:33" and the K0 to K4 / Q6 rulings received between
19:10 and 19:16) to the outputs of run_read_w2b.sh. Reads only JSON; prints one line per element with PASS / FAIL and its numbers,
then exactly one of "VERDICT <arm>: PROMOTE ...", "VERDICT <arm>: DROP ...", "VERDICT <arm>: PARK ...".

Inputs: --read <read folder> (<read>/read/read.json of bench_read_w1, with its x416 part), --c532 and --c416 (the JSON
of w2b_counts.py on all cells and with score_exclude_v3.txt). Margins: read.json "M" (532 cells) and x416 "M" (416).
Contrast keys follow the tools: bench_read_w1 "B - A"; w2b_counts "B - A". Points are means over seeds.

la_ce (arm LACE; comparators PF = OP-A, PFC = OP-C):
  P1  mIoU-R13 LACE - PFC at OP-A: delta >= M and CI low > 0, on 532 AND on 416 cells
  P2  mIoU-R13 LACE - PF  at OP-A: delta >= M and CI low > 0, on 532 AND on 416 cells
  G1  LACE - PF strict crack IoU and relF1@2 >= -M at OP-A and at OP-W (points, 532)       (drop guard)
  G2  inactive IoU LACE - PFC >= -M_inact (point, 532)
  G3  every R13 class: IoU LACE - PFC >= -0.03 (point, 532; S: the 0.03 is spec l.150's classbias rule)
  G4  every FREE class: pred / GT px of LACE within 0.85 to 1.15 x PFC's (points, 532)
  G5  every FREE class: LACE pred px on cells without the class <= 1.5 x PFC's (points, 532; PFC 0 -> LACE must be 0)
  PROMOTE: all of P1, P2 (both cell sets) and G1 to G5. DROP: P1 point <= 0 on either cell set (S: "either"), or a G1
  line fails. PARK: anything else (no promotion at 2 seeds).
layered_ci (arms LCI, LCIARG, LCIUNI; comparators PF, PFC; counts from w2b_counts pairs PFC=LCI, LCIARG=LCI:paired):
  L1  R1 region recall LCI - PFC > 0 and CI low > 0, on 532 AND on 416 cells
  L2  R2 inactive false-alarm px LCI <= 1.15 x PFC (points, 532)
  L3  R3 inactive precision LCI - PFC >= -0.02 (point, 532)
  L4  R4 pred / GT inactive px LCI / PFC within 0.85 to 1.15 (points, 532)
  L5  R5 inactive IoU LCI - PFC > 0 (point, 532)
  L6  R5 LCI - LCIARG > 0 (point, 532, paired seeds; CI printed)                           (drop guard)
  L7  LCI - PF crack IoU and relF1@2 >= -M at OP-A and OP-W (points, 532); crack width ratio of LCI within 0.85 to
      1.15 x PF's at OP-A, pooled and per source with >= 40 cells (ARTS, BMRK, CFVS, CSIR); false crack px on the
      crack-free cells LCI <= 1.5 x PF (OP-A)                                                (drop guard)
  PROMOTE: L1 (both cell sets) and L2 to L7. DROP: L6 fails, or R5 LCI - PFC < 0 (point, 532), or an L7 line fails.
  PARK: anything else.
Usage: python w2b_verdict.py --arm lace|lci --read <folder> --c532 <json> --c416 <json> [--out <file>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

R13 = (0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21)
FREE = (1, 2, 4, 5, 7, 11, 13, 15, 16, 20, 21)
SOURCES = ("ARTS", "BMRK", "CFVS", "CSIR")      # sources with >= 40 pool cells (PROTOCOL v0.2 l.89)


class V:
    def __init__(self):
        self.lines: list[str] = []
        self.res: dict[str, bool] = {}

    def add(self, name: str, ok: bool, text: str) -> bool:
        self.res[name] = bool(ok)
        self.lines.append(f"{name}\t{'PASS' if ok else 'FAIL'}\t{text}")
        return bool(ok)

    def note(self, text: str) -> None:
        self.lines.append(f"\t\t{text}")


def con(doc: dict, b: str, a: str, op: str, k: str) -> dict:
    c = doc["contrasts"].get(f"{b} - {a}")
    if c is None:
        raise KeyError(f"contrast '{b} - {a}' not in read.json ({sorted(doc['contrasts'])})")
    return c[op]["metrics"][k]


def summ(doc: dict, arm: str, op: str, sub: str, k: str) -> float:
    return doc["summary"][arm][op][sub][k]["mean"]


def ci_rule(v: V, name: str, c: dict, m: float) -> bool:
    return v.add(name, c["delta"] >= m and c["lo"] > 0, f"delta {c['delta']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}], M {m:.4f}")


def crack_lines(v: V, doc: dict, arm: str, M: dict, tag: str) -> list[str]:
    names = []
    for op in ("OP-A", "OP-W"):
        for k in ("crack_iou", "relF1_2"):
            c = con(doc, arm, "PF", op, k)
            n = f"{tag} {k} {op}"
            v.add(n, c["delta"] >= -M[k], f"{arm} - PF delta {c['delta']:+.4f} >= -M {-M[k]:+.4f} [CI {c['lo']:+.4f}, {c['hi']:+.4f}]")
            names.append(n)
    return names


def verdict_lace(doc: dict, c532: dict, c416: dict) -> V:
    v = V()
    M, x = doc["M"], doc["x416"]
    p1 = [ci_rule(v, "P1 532", con(doc, "LACE", "PFC", "OP-A", "miou_rob"), M["miou_rob"]),
          ci_rule(v, "P1 416", con(x, "LACE", "PFC", "OP-A", "miou_rob"), x["M"]["miou_rob"])]
    p2 = [ci_rule(v, "P2 532", con(doc, "LACE", "PF", "OP-A", "miou_rob"), M["miou_rob"]),
          ci_rule(v, "P2 416", con(x, "LACE", "PF", "OP-A", "miou_rob"), x["M"]["miou_rob"])]
    g1 = crack_lines(v, doc, "LACE", M, "G1")
    for op in ("OP-A", "OP-W"):
        for k in ("crack_iou", "relF1_2"):
            c = con(x, "LACE", "PF", op, k)
            v.note(f"G1 printed, 416 cells: {k} {op} delta {c['delta']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}]")
    c = con(doc, "LACE", "PFC", "OP-A", "inact_iou")
    v.add("G2 inactive IoU", c["delta"] >= -M["inact_iou"],
          f"LACE - PFC {c['delta']:+.4f} >= -M_inact {-M['inact_iou']:+.4f} [CI {c['lo']:+.4f}, {c['hi']:+.4f}]")
    pl, pc = c532["points"]["LACE"], c532["points"]["PFC"]
    worst = min(((pl[f"c{k}_iou"] - pc[f"c{k}_iou"]), k) for k in R13)
    v.add("G3 per R13 class", worst[0] >= -0.03, f"worst class {worst[1]}: IoU LACE - PFC {worst[0]:+.4f} >= -0.03")
    bad4, bad5 = [], []
    for k in FREE:
        r = pl[f"c{k}_area"] / pc[f"c{k}_area"] if pc[f"c{k}_area"] else float("inf")
        if not 0.85 <= r <= 1.15:
            bad4.append(f"{k}:{r:.3f}")
        fa_l, fa_c = pl[f"c{k}_fa_px"], pc[f"c{k}_fa_px"]
        if fa_l > 1.5 * fa_c:
            bad5.append(f"{k}:{fa_l:.0f}>{1.5 * fa_c:.0f}")
    v.add("G4 area ratio x PFC", not bad4, f"FREE classes outside 0.85 to 1.15: {bad4 or 'none'}")
    v.add("G5 px on cells without class", not bad5, f"FREE classes above 1.5 x PFC: {bad5 or 'none'}")
    for sub in ("all",) + tuple(f"src:{so}" for so in SOURCES):
        wp, wl = summ(doc, "PF", "OP-A", sub, "width_ratio"), summ(doc, "LACE", "OP-A", sub, "width_ratio")
        v.note(f"flag (printed, decides nothing; READ_PLAN 1): crack width ratio {sub} LACE {wl:.3f} / PF {wp:.3f} = "
               f"{wl / wp:.3f}{'' if 0.85 <= wl / wp <= 1.15 else '  OUTSIDE 0.85 to 1.15'}")
    fp, fl = summ(doc, "PF", "OP-A", "all", "fa_px"), summ(doc, "LACE", "OP-A", "all", "fa_px")
    v.note(f"flag (printed): false crack px on crack-free cells LACE {fl:.0f}, PF {fp:.0f}"
           f"{'' if fl <= 1.5 * fp else '  ABOVE 1.5 x PF'}")
    for k in (15, 16):
        v.note(f"printed: class {k} IoU LACE {pl[f'c{k}_iou']:.4f} PFC {pc[f'c{k}_iou']:.4f}; px on cells without it "
               f"LACE {pl[f'c{k}_fa_px']:.0f} PFC {pc[f'c{k}_fa_px']:.0f}")
    drop_p1 = [n for n, xx in (("532", doc), ("416", x)) if con(xx, "LACE", "PFC", "OP-A", "miou_rob")["delta"] <= 0]
    drop_g1 = [n for n in g1 if not v.res[n]]
    if drop_p1 or drop_g1:
        v.lines.append(f"VERDICT la_ce: DROP (primary delta <= 0 on {drop_p1 or 'no set'}; crack guards failed: "
                       f"{drop_g1 or 'none'})")
    elif all(p1 + p2) and all(v.res[n] for n in v.res if n[0] == "G"):
        v.lines.append("VERDICT la_ce: PROMOTE to the 5-seed confirmation (P1, P2 on 532 and 416 cells; G1 to G5 hold)")
    else:
        fails = [n for n, ok in v.res.items() if not ok]
        v.lines.append(f"VERDICT la_ce: PARK (no promotion at 2 seeds; failed: {fails})")
    return v


def verdict_lci(doc: dict, c532: dict, c416: dict) -> V:
    v = V()
    M = doc["M"]
    c1a = c532["contrasts"]["LCI - PFC"]["metrics"]["R1_region_recall"]
    c1b = c416["contrasts"]["LCI - PFC"]["metrics"]["R1_region_recall"]
    l1 = [v.add(f"L1 {n}", c["delta"] > 0 and c["lo"] > 0, f"R1 LCI - PFC {c['delta']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}]")
          for n, c in (("532", c1a), ("416", c1b))]
    pl, pc = c532["points"]["LCI"], c532["points"]["PFC"]
    v.add("L2 false-alarm px", pl["R2_fa_px"] <= 1.15 * pc["R2_fa_px"],
          f"R2 LCI {pl['R2_fa_px']:.0f} <= 1.15 x PFC {1.15 * pc['R2_fa_px']:.0f} (cells without inactive {pl['R2_cells']:.0f})")
    d3 = pl["R3_inact_prec"] - pc["R3_inact_prec"]
    v.add("L3 inactive precision", d3 >= -0.02, f"R3 LCI - PFC {d3:+.4f} >= -0.02")
    r4 = pl["R4_area_ratio"] / pc["R4_area_ratio"] if pc["R4_area_ratio"] else float("inf")
    v.add("L4 area", 0.85 <= r4 <= 1.15, f"R4 LCI / PFC {r4:.3f} in [0.85, 1.15]")
    d5 = pl["R5_inact_iou"] - pc["R5_inact_iou"]
    v.add("L5 direction", d5 > 0, f"R5 LCI - PFC {d5:+.4f} > 0")
    c6 = c532["contrasts"]["LCI - LCIARG"]["metrics"]["R5_inact_iou"]
    v.add("L6 mechanism", c6["delta"] > 0, f"R5 LCI - LCIARG {c6['delta']:+.4f} > 0 (paired CI {c6['lo']:+.4f}, {c6['hi']:+.4f}; promotes nothing)")
    l7 = crack_lines(v, doc, "LCI", M, "L7")
    w_pf, w_l = summ(doc, "PF", "OP-A", "all", "width_ratio"), summ(doc, "LCI", "OP-A", "all", "width_ratio")
    l7.append("L7 width pooled")
    v.add("L7 width pooled", 0.85 * w_pf <= w_l <= 1.15 * w_pf, f"LCI {w_l:.3f} vs PF {w_pf:.3f} x [0.85, 1.15]")
    for so in SOURCES:
        n = f"L7 width {so}"
        wp, wl = summ(doc, "PF", "OP-A", f"src:{so}", "width_ratio"), summ(doc, "LCI", "OP-A", f"src:{so}", "width_ratio")
        v.add(n, 0.85 * wp <= wl <= 1.15 * wp, f"LCI {wl:.3f} vs PF {wp:.3f} x [0.85, 1.15]")
        l7.append(n)
    fp, fl = summ(doc, "PF", "OP-A", "all", "fa_px"), summ(doc, "LCI", "OP-A", "all", "fa_px")
    v.add("L7 false crack px", fl <= 1.5 * fp, f"LCI {fl:.0f} <= 1.5 x PF {1.5 * fp:.0f}")
    l7.append("L7 false crack px")
    for name in ("LCIARG", "LCIUNI", "PF"):
        if name in c532["points"]:
            q = c532["points"][name]
            v.note(f"printed: {name} R1 {q['R1_region_recall']:.4f} R2 {q['R2_fa_px']:.0f} R3 {q['R3_inact_prec']:.4f} "
                   f"R4 {q['R4_area_ratio']:.4f} R5 {q['R5_inact_iou']:.4f}")
    drops = [n for n in ["L6 mechanism"] + l7 if not v.res[n]] + (["R5 LCI - PFC < 0"] if d5 < 0 else [])
    if drops:
        v.lines.append(f"VERDICT layered_ci: DROP ({drops})")
    elif all(l1) and all(v.res[n] for n in v.res if n[:2] in ("L2", "L3", "L4", "L5", "L6", "L7")):
        v.lines.append("VERDICT layered_ci: PROMOTE to the 5-seed confirmation (L1 on 532 and 416 cells; L2 to L7 hold)")
    else:
        fails = [n for n, ok in v.res.items() if not ok]
        v.lines.append(f"VERDICT layered_ci: PARK (no promotion at 2 seeds; failed: {fails})")
    return v


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["lace", "lci"])
    ap.add_argument("--read", required=True)
    ap.add_argument("--c532", required=True)
    ap.add_argument("--c416", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    doc = json.loads((Path(a.read) / "read" / "read.json").read_text())
    c532, c416 = (json.loads(Path(f).read_text()) for f in (a.c532, a.c416))
    assert c532["excluded"] == 0 and c416["excluded"] > 0, "c532 must be all cells, c416 the clean cells"
    v = (verdict_lace if a.arm == "lace" else verdict_lci)(doc, c532, c416)
    text = "\n".join(v.lines) + "\n"
    if a.out:
        if Path(a.out).exists():
            sys.exit(f"refuse: {a.out} exists")
        Path(a.out).write_text(text)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
