"""Track M R1 analysis (protocol_r1.md). CPU only, from r1/r1_cells.json and m0/<run>.json.

Prints: identity check vs M0; R1a (TTA vs plain, rule 1 + paired per-seed + bootstrap); R1b (ensemble vs mean single seed,
paired bootstrap, LOO spread); R1axb (TTA ensemble vs plain ensemble, descriptive); R1c (bias, descriptive); cell sets
(all, -noisy, -twins, -both), per source, per class, crack capture, noisy-cell check.
"""
from __future__ import annotations

import json, sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m0_analyze import agg, NAMES, NOISY, TWINS, NC  # noqa: E402

TL = [0, 1, 2, 4, 5, 7, 11, 13, 14, 15, 16, 20, 21]
CL = ([0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 18, 20, 21], TL)
PRIM = [("crack_iou", lambda A: A["iou"][14]), ("inact_iou", lambda A: A["iou"][11]), ("relF1", lambda A: A["relF1"]),
        ("miou_rob", lambda A: A["miou_rob"])]
SETS = {"all": lambda s: True, "-noisy": lambda s: s != NOISY, "-twins": lambda s: s not in TWINS,
        "-both": lambda s: s not in TWINS and s != NOISY}


def thr(a, b):
    return max(0.01, 2 * np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 3))


def counts(cells, stems):
    """per-cell arrays for bootstrap: conf [n,24,24], rel [n,4]"""
    return (np.stack([np.array(cells[s]["conf"], np.int64).reshape(NC, NC) for s in stems]),
            np.stack([np.array(cells[s]["crack_rel2"], np.int64) for s in stems]))


def prim_from(C, R):
    tp = np.diag(C).astype(float); g = C.sum(1); p = C.sum(0); den = g + p - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    rP, rR = R[0] / max(R[1], 1), R[2] / max(R[3], 1)
    rob = np.nanmean([iou[c] if g[c] > 0 else np.nan for c in TL])
    return np.array([iou[14], iou[11], 2 * rP * rR / max(rP + rR, 1e-9), rob])


def boot(armA: list, armB: list, stems, n=2000, seed=0):
    """paired image bootstrap of mean(B) - mean(A); armX = list of cells dicts (one per member/seed)."""
    rng = np.random.default_rng(seed)
    cA = [counts(c, stems) for c in armA]; cB = [counts(c, stems) for c in armB]
    full = np.mean([prim_from(C.sum(0), R.sum(0)) for C, R in cB], 0) - np.mean([prim_from(C.sum(0), R.sum(0)) for C, R in cA], 0)
    out = np.empty((n, 4))
    for i in range(n):
        ix = rng.integers(0, len(stems), len(stems))
        b = np.mean([prim_from(C[ix].sum(0), R[ix].sum(0)) for C, R in cB], 0)
        a = np.mean([prim_from(C[ix].sum(0), R[ix].sum(0)) for C, R in cA], 0)
        out[i] = b - a
    lo, hi = np.nanpercentile(out, [2.5, 97.5], 0)
    return full, lo, hi, np.nanmean(out > 0, 0)


def row(cells, kf):
    A = agg(cells, kf, CL)
    return A


def main():
    d = json.load(open(sys.argv[1]))
    m0 = Path(sys.argv[2])
    runs = d["runs"]
    # identity vs M0
    mx = 0
    for sp in ("test", "val"):
        ref = {r: json.load(open(m0 / f"{r}.json"))["cells"][sp] for r in runs}
        for r in runs:
            for s, v in d[sp][f"single_plain/{r}"].items():
                mx = max(mx, int(np.abs(np.array(v["conf"]) - np.array(ref[r][s]["conf"])).max()))
    print(f"IDENTITY single_plain vs M0 (test+val, per-cell confusion): max |diff| = {mx}")
    dec = json.load(open(Path(sys.argv[1]).parent / "r1_val_decisions.json"))
    print("VAL decisions:", {k: v for k, v in dec.items() if k != "sweep"})
    fin = [k for k in d["test"] if k.startswith("r1_final")][0]
    T = d["test"]; stems = sorted(T["ens_plain"])
    P = [T[f"single_plain/{r}"] for r in runs]; Q = [T[f"single_tta/{r}"] for r in runs]
    for setn, kf in SETS.items():
        st = [s for s in stems if kf(s)]
        print(f"\n######## TEST, cell set {setn} (n={len(st)})")
        fP = [agg(c, kf, CL) for c in P]; fQ = [agg(c, kf, CL) for c in Q]
        print("R1a TTA - plain (5 v 5): metric | plain mean±sd | tta mean±sd | delta | thr | verdict | paired per-seed d (mean, min, max, n>0)")
        for nm, f in PRIM:
            a = np.array([f(x) for x in fP]); b = np.array([f(x) for x in fQ]); t = thr(a, b); dl = b.mean() - a.mean()
            v = "BETTER" if dl > t else "WORSE" if dl < -t else "n.d."
            pd = b - a
            print(f"  {nm:9s} | {a.mean():.4f}±{a.std(ddof=1):.4f} | {b.mean():.4f}±{b.std(ddof=1):.4f} | {dl:+.4f} | {t:.4f} | {v} | {pd.mean():+.4f} {pd.min():+.4f} {pd.max():+.4f} {int((pd > 0).sum())}/5")
        if setn in ("all", "-noisy"):
            full, lo, hi, pp = boot(P, Q, st)
            print("  bootstrap TTA-plain:", " | ".join(f"{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i, (nm, _) in enumerate(PRIM)))
        E = agg(T["ens_plain"], kf, CL); ET = agg(T["ens_tta"], kf, CL)
        loo = [agg(T[f"loo_plain/-{r}"], kf, CL) for r in runs]
        print("R1b ensemble(plain) vs mean single seed(plain):")
        for nm, f in PRIM:
            print(f"  {nm:9s} single mean {np.mean([f(x) for x in fP]):.4f} | ensemble {f(E):.4f} | LOO4 {min(f(x) for x in loo):.4f}..{max(f(x) for x in loo):.4f} | ens+TTA {f(ET):.4f}")
        if setn in ("all", "-noisy"):
            full, lo, hi, pp = boot(P, [T["ens_plain"]], st)
            print("  bootstrap ENS-single:", " | ".join(f"{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}] P>0 {pp[i]:.2f}" for i, (nm, _) in enumerate(PRIM)))
            full, lo, hi, pp = boot([T["ens_plain"]], [T["ens_tta"]], st)
            print("  bootstrap ENS_TTA-ENS (descriptive):", " | ".join(f"{nm} {full[i]:+.4f} [{lo[i]:+.4f}, {hi[i]:+.4f}]" for i, (nm, _) in enumerate(PRIM)))
        F = agg(T[fin], kf, CL)
        def cap(A):
            return (f"crack P {A['prec'][14]:.3f} R {A['rec'][14]:.3f} IoU {A['iou'][14]:.3f} relP2 {A['relP2']:.3f} relR2 {A['relR2']:.3f} "
                    f"relF1 {A['relF1']:.3f} cc_rec {A['cc_rec50_20']:.3f} cc_prec {A['cc_prec_20']:.3f} | inact P {A['prec'][11]:.3f} R {A['rec'][11]:.3f} "
                    f"IoU {A['iou'][11]:.3f} in_cc_rec {A['in_cc_rec50']:.3f} | mIoU_rob {A['miou_rob']:.3f} no07 {A['miou_rob_no07']:.3f}")
        print("R1c (descriptive):\n  ens bias 0 :", cap(E), f"\n  {fin}:", cap(F))
        print("  single plain mean:", " ".join(f"{k} {np.mean([x[k] for x in fP]):.3f}" for k in ("relP2", "relR2", "cc_rec50_20", "cc_prec_20", "miou_rob")))
    # per source, per class for ensemble vs single
    print("\n######## per source (test, all cells): source | n | single crack IoU | ens | final | single inact | ens | final | single mIoU_rob | ens | final | FP px absent (ens)")
    for so in ["ARTS", "BMRK", "CFVS", "CSIR", "SDLE"]:
        kf = lambda s, so=so: s.startswith(so)
        fP = [agg(c, kf, CL) for c in P]; E = agg(T["ens_plain"], kf, CL); F = agg(T[fin], kf, CL)
        m = lambda k, c=None: np.nanmean([x[k][c] if c is not None else x[k] for x in fP])
        print(f"| {so} | {E['n']} | {m('iou', 14):.3f} | {E['iou'][14]:.3f} | {F['iou'][14]:.3f} | {m('iou', 11):.3f} | {E['iou'][11]:.3f} | {F['iou'][11]:.3f} | "
              f"{m('miou_rob'):.3f} | {E['miou_rob']:.3f} | {F['miou_rob']:.3f} | {E['fp_absent_px']} |")
    print("\n######## per class (test, all / -noisy): class | single IoU | ens IoU | final IoU | ens P | ens R | final P | final R")
    for kn, kf in (("all", SETS["all"]), ("-noisy", SETS["-noisy"])):
        fP = [agg(c, kf, CL) for c in P]; E = agg(T["ens_plain"], kf, CL); F = agg(T[fin], kf, CL)
        print(f"## {kn}")
        for c in TL + [9, 18]:
            print(f"| {c} {NAMES[c]} | {np.nanmean([x['iou'][c] for x in fP]):.3f} | {E['iou'][c]:.3f} | {F['iou'][c]:.3f} | {E['prec'][c]:.3f} | {E['rec'][c]:.3f} | {F['prec'][c]:.3f} | {F['rec'][c]:.3f} |")
    print("\n######## noisy cell px (crack 14 / border 5 / text 6 predicted on CSIR_00070_r8_c4)")
    for nm, c in [*(("plain " + r, T[f"single_plain/{r}"]) for r in runs), *(("tta " + r, T[f"single_tta/{r}"]) for r in runs),
                  ("ens_plain", T["ens_plain"]), ("ens_tta", T["ens_tta"]), (fin, T[fin])]:
        C = np.array(c[NOISY]["conf"]).reshape(NC, NC)
        print(f"  {nm:28s} crack {C[:, 14].sum():6d} border {C[:, 5].sum():6d} text {C[:, 6].sum():6d}")
    # val summary
    V = d["val"]; VL = [0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 15, 16, 21]
    print("\n######## VAL (val list): variant | crack | relF1 | mIoU_rob | inact")
    for k in ["ens_plain", "ens_tta"] + [k for k in V if k.startswith("r1_final")]:
        A = agg(V[k], lambda s: True, (VL, VL))
        print(f"  {k:24s} {A['iou'][14]:.4f} {A['relF1']:.4f} {A['miou_rob']:.4f} {A['iou'][11]:.4f}")
    for var in ("single_plain", "single_tta"):
        A = [agg(V[f"{var}/{r}"], lambda s: True, (VL, VL)) for r in runs]
        print(f"  {var:24s} " + " ".join(f"{np.mean(x):.4f}" for x in ([a['iou'][14] for a in A], [a['relF1'] for a in A], [a['miou_rob'] for a in A], [a['iou'][11] for a in A])))


if __name__ == "__main__":
    main()
