"""Track M rung analysis (protocols r2, r3 Part B, r4): arm B (5 seeds) vs comparator A (SUP100, 5 seeds), from M0-format
JSONs (m0_audit.py outputs). CPU only.

Prints: per-arm means; rule 1 per primary on all 50 and without the noisy cell with the design §1/C6 pass rule; val
inclusion rule (C1); paired-by-image bootstrap (2,000, seed 0) and leave-top-3-out; cell sets -twins, -both; per source with
FP px of subset-absent classes; per class; crack capture; named secondaries (per-source crack AP from 1,000-bin
histograms, BMRK crack recall/relR@2, CSIR/ARTS crack IoU); E1 ext; grad-norm summary if logs are given.
Usage: python m2_rung.py --a <A json ...> --b <B json ...> [--ext-drop STEM] [--label NAME]
"""
from __future__ import annotations

import argparse, json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m0_analyze import agg, NAMES, NOISY, TWINS, NC  # noqa: E402
from m1_analyze import boot, thr, PRIM, CL, TL  # noqa: E402

VL = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21]
SETS = {"all": lambda s: True, "-noisy": lambda s: s != NOISY, "-twins": lambda s: s not in TWINS,
        "-both": lambda s: s not in TWINS and s != NOISY}


def ap_from(pos, neg):
    """binned AP as the P-series threshold_free.binned_ap: sweep thresholds from the top bin down."""
    pos, neg = pos[::-1].astype(float), neg[::-1].astype(float)
    tp, fp = np.cumsum(pos), np.cumsum(neg)
    P = tp / np.maximum(tp + fp, 1); R = tp / max(pos.sum(), 1)
    dR = np.diff(np.concatenate([[0], R]))
    return float((P * dR).sum())


def src_ap(cells, src):
    st = [s for s in cells if s.startswith(src)]
    if not st or "crack_h1000_pos" not in cells[st[0]]:
        return np.nan
    return ap_from(np.sum([cells[s]["crack_h1000_pos"] for s in st], 0), np.sum([cells[s]["crack_h1000_neg"] for s in st], 0))


def rule(a, b):
    t = thr(a, b); d = np.mean(b) - np.mean(a)
    return d, t, (1 if d > t else -1 if d < -t else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", nargs=5, required=True); ap.add_argument("--b", nargs="+", required=True)
    ap.add_argument("--ext-drop", default=None); ap.add_argument("--label", default="B")
    a = ap.parse_args()
    A = [json.load(open(f)) for f in a.a]; B = [json.load(open(f)) for f in a.b]
    for X in A + B:
        assert X["step"] == 20000, X["run"]
    print(f"A = {[x['run'] for x in A]}\nB ({a.label}) = {[x['run'] for x in B]}")
    # ---- VAL inclusion (C1)
    print("\n## VAL inclusion rule (val list; rule 1 on crack IoU, relF1@2, mIoU_rob; inactive reported only)")
    vA = [agg(x["cells"]["val"], lambda s: True, (VL, VL)) for x in A]; vB = [agg(x["cells"]["val"], lambda s: True, (VL, VL)) for x in B]
    inc = []
    for nm, f in PRIM:
        d, t, v = rule([f(x) for x in vA], [f(x) for x in vB])
        print(f"  {nm:9s} A {np.mean([f(x) for x in vA]):.4f} B {np.mean([f(x) for x in vB]):.4f} d {d:+.4f} thr {t:.4f} -> {['WORSE', 'n.d.', 'BETTER'][v + 1]}")
        if nm != "inact_iou":
            inc.append(v)
    print(f"  VAL INCLUSION: {'INCLUDE' if (1 in inc and -1 not in inc) else 'EXCLUDE'}")
    # ---- TEST rule 1, two sets
    T = "test"
    verd = {}
    for setn in ("all", "-noisy", "-twins", "-both"):
        kf = SETS[setn]
        tA = [agg(x["cells"][T], kf, CL) for x in A]; tB = [agg(x["cells"][T], kf, CL) for x in B]
        print(f"\n## TEST {setn} (n={tA[0]['n']})  metric | A mean±sd | B mean±sd | d | thr | verdict")
        for nm, f in PRIM:
            xa, xb = [f(x) for x in tA], [f(x) for x in tB]
            d, t, v = rule(xa, xb); verd[(setn, nm)] = (d, v)
            print(f"  {nm:9s} | {np.mean(xa):.4f}±{np.std(xa, ddof=1):.4f} | {np.mean(xb):.4f}±{np.std(xb, ddof=1):.4f} | {d:+.4f} | {t:.4f} | {['WORSE', 'n.d.', 'BETTER'][v + 1]}")
        for k in ("prec", "rec"):
            print(f"  crack {k} A {np.mean([x[k][14] for x in tA]):.3f} B {np.mean([x[k][14] for x in tB]):.3f} | inactive {k} A {np.mean([x[k][11] for x in tA]):.3f} B {np.mean([x[k][11] for x in tB]):.3f}")
        print(f"  relP2 A {np.mean([x['relP2'] for x in tA]):.3f} B {np.mean([x['relP2'] for x in tB]):.3f} | relR2 A {np.mean([x['relR2'] for x in tA]):.3f} B {np.mean([x['relR2'] for x in tB]):.3f} | "
              f"crack comp rec A {np.mean([x['cc_rec50_20'] for x in tA]):.3f} B {np.mean([x['cc_rec50_20'] for x in tB]):.3f} | comp prec A {np.mean([x['cc_prec_20'] for x in tA]):.3f} B {np.mean([x['cc_prec_20'] for x in tB]):.3f} | "
              f"inact comp rec A {np.mean([x['in_cc_rec50'] for x in tA]):.3f} B {np.mean([x['in_cc_rec50'] for x in tB]):.3f}")
        if setn in ("all", "-noisy"):
            stems = [s for s in sorted(A[0]["cells"][T]) if kf(s)]
            full, lo, hi, pp = boot([x["cells"][T] for x in A], [x["cells"][T] for x in B], stems)
            print("  bootstrap B-A: " + " | ".join(f"{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i, (nm, _) in enumerate(PRIM)))
            # leave-top-3-out (by GT area of the class) for crack and inactive
            for c, nm in ((14, "crack"), (11, "inactive")):
                gt = {s: np.array(A[0]["cells"][T][s]["conf"]).reshape(NC, NC)[c].sum() for s in stems}
                top = set(sorted(stems, key=lambda s: -gt[s])[:3])
                kk = lambda s, kf=kf, top=top: kf(s) and s not in top
                da = np.mean([agg(x["cells"][T], kk, CL)["iou"][c] for x in B]) - np.mean([agg(x["cells"][T], kk, CL)["iou"][c] for x in A])
                print(f"  leave-top-3-out {nm} IoU d {da:+.4f}")
    # pass rule
    print("\n## RUNG VERDICT (design §1/C6)")
    any_worse = any(verd[(s, nm)][1] == -1 for s in ("all", "-noisy") for nm, _ in PRIM)
    passes = []
    for nm, _ in PRIM:
        v1, v2 = verd[("all", nm)], verd[("-noisy", nm)]
        if (v1[1] == 1 and v2[1] == 1) or (v1[1] == 1 and v2[1] == 0 and v2[0] > 0) or (v2[1] == 1 and v1[1] == 0 and v1[0] > 0):
            passes.append(nm)
    print(f"  worse anywhere: {any_worse}; passing primaries: {passes}; VERDICT: {'WORSE' if any_worse else 'PASS' if passes else 'n.d.'}")
    # per source + secondaries
    print("\n## per source (test): source/set | n | crack IoU A B | crack R A B | relR2 A B | crack AP A B | inact IoU A B | mIoU_rob A B | FP absent px A B | dead_cell(17) px A B")
    for so in ("ARTS", "BMRK", "CFVS", "CSIR", "SDLE"):
        for tag, kf in (("all", lambda s, so=so: s.startswith(so)), ("-noisy", lambda s, so=so: s.startswith(so) and s != NOISY)):
            if tag == "-noisy" and so != "CSIR":
                continue
            ga = [agg(x["cells"][T], kf, CL) for x in A]; gb = [agg(x["cells"][T], kf, CL) for x in B]
            m = lambda G, k, c=None: np.nanmean([g[k][c] if c is not None else g[k] for g in G])
            apa = np.nanmean([src_ap({s: v for s, v in x["cells"][T].items() if kf(s)}, so) for x in A])
            apb = np.nanmean([src_ap({s: v for s, v in x["cells"][T].items() if kf(s)}, so) for x in B])
            print(f"| {so} {tag} | {ga[0]['n']} | {m(ga, 'iou', 14):.3f} {m(gb, 'iou', 14):.3f} | {m(ga, 'rec', 14):.3f} {m(gb, 'rec', 14):.3f} | {m(ga, 'relR2'):.3f} {m(gb, 'relR2'):.3f} | "
                  f"{apa:.3f} {apb:.3f} | {m(ga, 'iou', 11):.3f} {m(gb, 'iou', 11):.3f} | {m(ga, 'miou_rob'):.3f} {m(gb, 'miou_rob'):.3f} | {m(ga, 'fp_absent_px'):.0f} {m(gb, 'fp_absent_px'):.0f} | "
                  f"{m(ga, 'pr', 17):.0f} {m(gb, 'pr', 17):.0f} |")
    # named secondaries: rule-1 arithmetic
    print("\n## named secondaries, rule-1 arithmetic (descriptive)")
    for setn in ("all", "-noisy"):
        sk = SETS[setn]
        defs = {"BMRK crack AP": lambda x: src_ap({s: v for s, v in x["cells"][T].items() if sk(s)}, "BMRK"),
                "BMRK crack recall": lambda x: agg(x["cells"][T], lambda s: sk(s) and s.startswith("BMRK"), CL)["rec"][14],
                "BMRK relR2": lambda x: agg(x["cells"][T], lambda s: sk(s) and s.startswith("BMRK"), CL)["relR2"],
                "CSIR crack IoU": lambda x: agg(x["cells"][T], lambda s: sk(s) and s.startswith("CSIR"), CL)["iou"][14],
                "CSIR inact IoU": lambda x: agg(x["cells"][T], lambda s: sk(s) and s.startswith("CSIR"), CL)["iou"][11],
                "ARTS crack IoU": lambda x: agg(x["cells"][T], lambda s: sk(s) and s.startswith("ARTS"), CL)["iou"][14]}
        for k, f in defs.items():
            d, t, v = rule([f(x) for x in A], [f(x) for x in B])
            print(f"  {setn:7s} {k:18s} A {np.mean([f(x) for x in A]):.4f} B {np.mean([f(x) for x in B]):.4f} d {d:+.4f} thr {t:.4f} {['WORSE', 'n.d.', 'BETTER'][v + 1]}")
    # per class
    print("\n## per class (test -noisy, val): class | GT cells | A IoU | B IoU | A P | B P | A R | B R || val A IoU | val B IoU")
    kf = SETS["-noisy"]
    tA = [agg(x["cells"][T], kf, CL) for x in A]; tB = [agg(x["cells"][T], kf, CL) for x in B]
    for c in TL + [9, 18]:
        m = lambda G, k: np.nanmean([g[k][c] for g in G])
        print(f"| {c} {NAMES[c]} | {tA[0]['gt_cells'][c]} | {m(tA, 'iou'):.3f} | {m(tB, 'iou'):.3f} | {m(tA, 'prec'):.3f} | {m(tB, 'prec'):.3f} | {m(tA, 'rec'):.3f} | {m(tB, 'rec'):.3f} || "
              f"{m(vA, 'iou'):.3f} | {m(vB, 'iou'):.3f} |")
    # E1 ext
    if "ext" in A[0]["cells"] and "ext" in B[0]["cells"]:
        print("\n## E1 ext (secondary): set | crack IoU A B | crack R A B | inact IoU A B | mIoU (ext GT list) A B")
        e0 = agg(A[0]["cells"]["ext"], lambda s: True)
        el = ([c for c in range(NC) if e0["gt"][c] > 0], [c for c in range(NC) if e0["gt_cells"][c] >= 3])
        for tag, kf in (("all 106", lambda s: True), (f"-{a.ext_drop}", lambda s: s != a.ext_drop)):
            if tag.startswith("-") and not a.ext_drop:
                continue
            ga = [agg(x["cells"]["ext"], kf, el) for x in A]; gb = [agg(x["cells"]["ext"], kf, el) for x in B]
            m = lambda G, k, c=None: np.nanmean([g[k][c] if c is not None else g[k] for g in G])
            print(f"  {tag} | {m(ga, 'iou', 14):.3f} {m(gb, 'iou', 14):.3f} | {m(ga, 'rec', 14):.3f} {m(gb, 'rec', 14):.3f} | {m(ga, 'iou', 11):.3f} {m(gb, 'iou', 11):.3f} | {m(ga, 'miou_rob'):.3f} {m(gb, 'miou_rob'):.3f}")


if __name__ == "__main__":
    main()
