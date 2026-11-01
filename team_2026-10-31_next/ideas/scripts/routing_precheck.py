"""calib: half-cut routing pre-check (judge condition 3b + R1), exactly as ideas/routing_precheck.md (rule md5 dcaa3bd5, written and
approved before any number; Amendment A: the primary synthetic set is domain's frozen SHV1; synvar V4 is a non-deciding sensitivity row).
Non-E1, non-test: V0 = the 54 val cells, "V4" in the code = the synthetic half-cut set read from --recsyn (SHV1 = primary).
Usage: python routing_precheck.py --rec DIR(val records) --recsyn DIR(SHV1 records) [--recsyn-sens DIR(synvar V4 records)] --out OUT.txt
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import el_metrics as E  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--rec", required=True)
ap.add_argument("--recsyn", required=True)
ap.add_argument("--recsyn-sens")
ap.add_argument("--out", required=True)
ap.add_argument("--json")
ap.add_argument("--fig")
a = ap.parse_args()
G = E.GRID
J = lambda b: int(np.argmin(np.abs(G - b)))


def f1curve(cells, stems=None):
    c = E.curves(cells, stems)
    F = np.where((c["relP"] + c["relR"]) > 0, 2 * c["relP"] * c["relR"] / np.maximum(c["relP"] + c["relR"], 1e-9), 0.0)
    return np.nan_to_num(F, nan=0.0), c


def src(stem):  # V4 stem "<val stem>__V4h0" -> source val stem
    return stem.split("__")[0]


def folds(val_cells):
    """judge R1: 2 folds of the 54 source val cells, stratified by crack yes/no (GT crack >= 20 px), rng(0): crack stratum first."""
    rng = np.random.default_rng(0); fa = {}
    for stratum in (sorted(s for s, c in val_cells.items() if c["n_gt"] >= 20), sorted(s for s, c in val_cells.items() if c["n_gt"] < 20)):
        perm = [stratum[i] for i in rng.permutation(len(stratum))]
        for i, s in enumerate(perm):
            fa[s] = "AB"[i % 2]
    return fa


def matched(c, x):
    ok = np.where(np.nan_to_num(c["relP"], nan=-1) >= x)[0]
    return float(np.max(c["relR"][ok])) if len(ok) else float("nan")


def analyse(name, v_recs, s_recs, bdep):
    """v_recs / s_recs: lists of records (one per member to pool). Pooled counts across members."""
    V = E.pool_cells(v_recs, "val"); S = E.pool_cells(s_recs, "synval")
    ov, osy = E.oracle_b_relf1(V), E.oracle_b_relf1(S)
    bV0, bV4 = ov["b"], osy["b"]; db = bV4 - bV0
    FS, cS = f1curve(S); FV, cV = f1curve(V)
    Gin = float(FS[J(bV4)] - FS[J(bV0)])
    # cross-fit (judge R1): folds on the source val cells of the FIRST member (stems are the same for every member)
    fa = folds(v_recs[0]["cells"])
    key_fold = lambda k: fa[src(k.split(":", 1)[1])]
    gains = []
    for kf in "AB":
        Sk = [k for k in S if key_fold(k) == kf]; So = [k for k in S if key_fold(k) != kf]
        bk = E.oracle_b_relf1(S, Sk)["b"]
        Fo, _ = f1curve(S, So)
        gains.append(float(Fo[J(bk)] - Fo[J(bV0)]))
    Gcf = float(np.mean(gains))
    # FA guard on crack-free V4 half-images, at b_V0 vs b_V4
    neg = [k for k, c in S.items() if c["n_gt"] == 0]
    fa_ = lambda b: (float(np.mean([S[k]["pred"][J(b)] for k in neg])), float(np.mean([S[k]["s"][str(E.MFLAG)] + b > 0 for k in neg])))
    # mixed-set view: V0 cells at b_V0, V4 cells at b_V4 vs all at b_V0
    mix = {**{("v", k): (V[k], bV0) for k in V}, **{("s", k): (S[k], bV4) for k in S}}
    def mixed(route):
        t = np.zeros(4)
        for (kind, k), (c, b) in mix.items():
            bb = b if route else bV0; j = J(bb)
            t += [c["relp_tp"][j], c["pred"][j], c["relr_tp"][j], c["n_gt"]]
        P, R = t[0] / max(t[1], 1), t[2] / max(t[3], 1); return 2 * P * R / max(P + R, 1e-9)
    res = {"model": name, "b_V0": bV0, "b_V4": bV4, "delta_b": db, "G_insample": Gin, "G_cf": Gcf, "G_cf_folds": gains,
           "relF1_V0_at_bV0": float(FV[J(bV0)]), "relF1_V4_at_bV0": float(FS[J(bV0)]), "relF1_V4_at_bV4": float(FS[J(bV4)]),
           "at": {lab: {"V0": {"relR": float(cV["relR"][J(b)]), "relP": float(cV["relP"][J(b)]), "relF1": float(FV[J(b)])},
                        "V4": {"relR": float(cS["relR"][J(b)]), "relP": float(cS["relP"][J(b)]), "relF1": float(FS[J(b)])}}
                  for lab, b in (("b_V0", bV0), ("b_V4", bV4), ("b_dep", bdep))},
           "fa_V4_crackfree": {"n": len(neg), "at_bV0": fa_(bV0), "at_bV4": fa_(bV4)},
           "mixed_relF1": {"unrouted": mixed(False), "routed": mixed(True)},
           "matched_relR": {x: {"V0": matched(cV, x), "V4": matched(cS, x)} for x in (0.9, 0.8)},
           "curves": {"V0": FV.tolist(), "V4": FS.tolist()}}
    res["pass"] = {"db>=1.0": db >= 1.0, "G>=0.02": Gin >= 0.02, "Gcf>=0.01": Gcf >= 0.01}
    res["pass_all"] = all(res["pass"].values())
    return res


R, RS = Path(a.rec), Path(a.recsyn)
ld = lambda p: json.load(open(p))
out = {"FINAL": analyse("FINAL", [ld(R / "FINAL.val.json")], [ld(RS / "FINAL.synval.json")], 0.75),
       "SUPPF5_pooled": analyse("SUPPF5 pooled", [ld(R / f"SUPPF5_m{k}.val.json") for k in range(5)],
                                [ld(RS / f"SUPPF5_m{k}.synval.json") for k in range(5)], 0.0)}
out["SUPPF5_per_seed"] = [analyse(f"SUPPF5 s{k}", [ld(R / f"SUPPF5_m{k}.val.json")], [ld(RS / f"SUPPF5_m{k}.synval.json")], 0.0) for k in range(5)]
if a.recsyn_sens:  # non-deciding sensitivity row: synvar V4 (fixed 154/24 intensity)
    RV = Path(a.recsyn_sens)
    out["SENS_V4_FINAL"] = analyse("SENS synvar V4 FINAL", [ld(R / "FINAL.val.json")], [ld(RV / "FINAL.synval.json")], 0.75)
    out["SENS_V4_SUPPF5_pooled"] = analyse("SENS synvar V4 SUPPF5 pooled", [ld(R / f"SUPPF5_m{k}.val.json") for k in range(5)],
                                           [ld(RV / f"SUPPF5_m{k}.synval.json") for k in range(5)], 0.0)
verdict = out["FINAL"]["pass_all"] and out["SUPPF5_pooled"]["pass_all"]
L = ["routing pre-check (judge 3b + R1 + Amendment A), rule ideas/routing_precheck.md; non-E1, non-test. Synthetic set: SHV1 (primary).",
     "PASS needs all three terms for FINAL and SUPPF5 pooled on SHV1. SENS rows (synvar V4) never decide.", ""]
for k in [x for x in ("FINAL", "SUPPF5_pooled", "SENS_V4_FINAL", "SENS_V4_SUPPF5_pooled") if x in out]:
    r = out[k]
    L.append(f"{r['model']}: b_V0 {r['b_V0']:+.1f}  b_V4 {r['b_V4']:+.1f}  delta_b {r['delta_b']:+.1f} ({'>= 1.0' if r['pass']['db>=1.0'] else '< 1.0: routing = no-op'}); "
             f"G in-sample {r['G_insample']:+.4f}; G_cf {r['G_cf']:+.4f} (folds {r['G_cf_folds'][0]:+.4f} / {r['G_cf_folds'][1]:+.4f}) -> {'PASS' if r['pass_all'] else 'FAIL'} {r['pass']}")
    for lab in ("b_V0", "b_V4", "b_dep"):
        x = r["at"][lab]
        L.append(f"   at {lab}: V0 relR {x['V0']['relR']:.3f} relP {x['V0']['relP']:.3f} relF1 {x['V0']['relF1']:.3f} | V4 relR {x['V4']['relR']:.3f} relP {x['V4']['relP']:.3f} relF1 {x['V4']['relF1']:.3f}")
    f = r["fa_V4_crackfree"]
    L.append(f"   FA guard, {f['n']} crack-free V4 half-images: crack px/image {f['at_bV0'][0]:.1f} -> {f['at_bV4'][0]:.1f}; flagged {f['at_bV0'][1]:.3f} -> {f['at_bV4'][1]:.3f}")
    L.append(f"   mixed V0+V4 relF1: unrouted {r['mixed_relF1']['unrouted']:.4f} routed {r['mixed_relF1']['routed']:.4f}")
    L.append(f"   matched precision, max relR@2: relP>=0.90 V0 {r['matched_relR'][0.9]['V0']:.3f} V4 {r['matched_relR'][0.9]['V4']:.3f}; "
             f"relP>=0.80 V0 {r['matched_relR'][0.8]['V0']:.3f} V4 {r['matched_relR'][0.8]['V4']:.3f}")
L.append("SUPPF5 per seed (reported, not deciding): " + "; ".join(f"s{i} b_V0 {r['b_V0']:+.1f} b_V4 {r['b_V4']:+.1f} db {r['delta_b']:+.1f} G {r['G_insample']:+.3f} Gcf {r['G_cf']:+.3f}"
                                                              for i, r in enumerate(out["SUPPF5_per_seed"])))
L.append(f"VERDICT: {'PASS' if verdict else 'FAIL'}")
Path(a.out).write_text("\n".join(L) + "\n"); print("\n".join(L))
if a.json:
    json.dump(out, open(a.json, "w"))
if a.fig:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for i, k in enumerate(("FINAL", "SUPPF5_pooled")):
        r = out[k]
        ax[i].plot(G, r["curves"]["V0"], color="#1f77b4", label=f"V0 val (b* {r['b_V0']:+.1f})")
        ax[i].plot(G, r["curves"]["V4"], color="#d62728", label=f"SHV1 synthetic half-cut (b* {r['b_V4']:+.1f})")
        ax[i].axvline(r["b_V0"], color="#1f77b4", lw=0.7, ls="--"); ax[i].axvline(r["b_V4"], color="#d62728", lw=0.7, ls="--")
        ax[i].set_title(r["model"], fontsize=9); ax[i].set_xlabel("crack logit bias b"); ax[i].set_ylabel("pooled relF1@2"); ax[i].legend(fontsize=7)
        ax[i].set_ylim(0.4, 1.0)
    fig.suptitle("routing pre-check: relF1@2 vs bias on V0 (val) and SHV1 (synthetic half-cut val); no E1, no test", fontsize=9)
    fig.tight_layout(); fig.savefig(a.fig, dpi=90)
