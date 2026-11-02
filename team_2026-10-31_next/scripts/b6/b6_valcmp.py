"""B6 scorer check (protocol_B6 v1.0.1 s8.2): b6_score.py --mode check output on f3_SUPPF_100pct_s0's 54 val cells vs the
opening-1 m0 file of the same run (el_f3 reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json), VAL BLOCK ONLY.

The m0 file also holds test / ext / val_tta blocks (opened in protocol_100 opening 1); this script indexes only
m0["cells"]["val"] and prints nothing from any other block.

Prints, per metric, both values and the delta, and per-cell equality counts. Stdlib only (runs on gaint or the laptop).
  --expect exact : every per-cell record (conf, crack_rel2, crack_cc, inact_cc, bands, h1000) must be equal (GPU bf16 pass)
  --expect tol   : pooled crack IoU / relP@2 / relR@2 / relF1@2 / inactive IoU / comp R / comp P within --tol (CPU fp32)
Exit code 0 = PASS, 1 = FAIL.

Usage: python3 b6_valcmp.py --b6 <out>/f3_SUPPF_100pct_s0.check.json --m0 <m0 json> --expect tol --tol 0.005
"""
from __future__ import annotations

import argparse
import json
import math
import sys

NC, CRACK, INACT, CMIN = 24, 14, 11, 20
KEYS = ("conf", "crack_rel2", "crack_cc", "inact_cc", "crack_pband_gt", "crack_pband_neg", "crack_h1000_pos", "crack_h1000_neg")


def pooled(cells: dict, stems) -> dict:
    C = [0] * (NC * NC)
    rel = [0, 0, 0, 0]
    gC, pC, gI, pI = [], [], [], []
    for s in stems:
        c = cells[s]
        C = [x + y for x, y in zip(C, c["conf"])]
        rel = [x + y for x, y in zip(rel, c["crack_rel2"])]
        gC += [g for g in c["crack_cc"]["gt"] if g[0] >= CMIN]
        pC += [p for p in c["crack_cc"]["pr"] if p[0] >= CMIN]
        gI += [g for g in c["inact_cc"]["gt"] if g[0] >= CMIN]
        pI += [p for p in c["inact_cc"]["pr"] if p[0] >= CMIN]

    def iou(k):
        tp = C[k * NC + k]
        den = sum(C[k * NC:(k + 1) * NC]) + sum(C[j * NC + k] for j in range(NC)) - tp
        return tp / den if den else math.nan

    dv = lambda a, b: a / b if b else math.nan
    P, R = dv(rel[0], rel[1]), dv(rel[2], rel[3])
    return {"crack_IoU": iou(CRACK), "relP2": P, "relR2": R,
            "relF1_2": math.nan if (math.isnan(P) or math.isnan(R) or P + R == 0) else 2 * P * R / (P + R),
            "inact_IoU": iou(INACT),
            "crack_compR": dv(sum(g[1] >= 0.5 * g[0] for g in gC), len(gC)), "crack_compP": dv(sum(p[1] > 0 for p in pC), len(pC)),
            "inact_compR": dv(sum(g[1] >= 0.5 * g[0] for g in gI), len(gI)), "inact_compP": dv(sum(p[1] > 0 for p in pI), len(pI)),
            "mIoU24": sum(x for x in (iou(k) for k in range(NC)) if x == x) / sum(1 for k in range(NC) if iou(k) == iou(k)),
            "px": sum(C)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b6", required=True)
    ap.add_argument("--m0", required=True)
    ap.add_argument("--expect", choices=["exact", "tol"], required=True)
    ap.add_argument("--tol", type=float, default=0.005)
    a = ap.parse_args()
    b6 = json.load(open(a.b6))
    m0 = json.load(open(a.m0))
    assert b6["mode"] == "check" and b6["fold"] == "val54" and b6["step"] == 20000 and b6["weights_file"] == "checkpoints/latest.pth"
    assert m0["step"] == 20000 and m0["weights"] == "model" and b6["run"] == m0["run"], (b6["run"], m0["run"])
    mine, ref = b6["cells"]["heldout"], m0["cells"]["val"]  # val block only
    assert set(mine) == set(ref) and len(mine) == 54, "cell sets differ"
    stems = sorted(ref)
    print(f"run {b6['run']} | b6 scorer {b6['scorer_md5'][:8]} device {b6['device']} weights {b6['weights_md5'][:8]} | "
          f"m0 code {m0.get('code_revision')} | 54 val cells")
    eq = {k: sum(mine[s][k] == ref[s][k] for s in stems) for k in KEYS}
    print("per-cell records equal (of 54): " + ", ".join(f"{k} {v}" for k, v in eq.items()))
    dpx = [sum(abs(x - y) for x, y in zip(mine[s]["conf"], ref[s]["conf"])) // 2 for s in stems]
    npx = sum(mine[stems[0]]["conf"])
    print(f"conf: cells with any changed px {sum(d > 0 for d in dpx)}; changed px total {sum(dpx)} of {npx * 54} "
          f"({sum(dpx) / (npx * 54):.2e}); max per cell {max(dpx)}")
    P1, P0 = pooled(mine, stems), pooled(ref, stems)
    ok = True
    for k in P0:
        if k == "px":
            continue
        d = P1[k] - P0[k]
        bad = (a.expect == "tol") and not (abs(d) <= a.tol or (math.isnan(P1[k]) and math.isnan(P0[k])))
        ok &= not bad
        print(f"  {k:12s} b6 {P1[k]:.5f}  m0 {P0[k]:.5f}  delta {d:+.6f}{'  FAIL' if bad else ''}")
    if a.expect == "exact":
        ok = all(v == 54 for v in eq.values())
        print("EXACT:", "PASS (all 54 per-cell records identical)" if ok else "FAIL")
    else:
        print(f"TOL {a.tol}:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
