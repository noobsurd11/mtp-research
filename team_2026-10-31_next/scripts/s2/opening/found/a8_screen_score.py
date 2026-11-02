"""a8_screen_score (found, 31 Oct 2026): the GO / KILL rule of protocol_A8screen.md §3 for the 2-seed PF screen (A8 vs A8c),
fixed before any screen number. Reads calib-format dumps (calib_dump.py: stems, margin, pc, oth) and el_metrics records of the
four screen runs on val and Hanifi _rf; no test, no E1.

Rule (seed means; GO only if all hold):
  1. F51 crack AP (1,000-bin p(crack), full range): A8 - A8c > 0, and a paired module-cluster bootstrap over F51's modules
     (2,000 resamples, seed 0) gives a lower 95% bound > 0;
  2. val crack AP: A8 >= A8c - 0.02 (val inactive is reported only);
  3. false alarms at each run's val-chosen b_rel (el_metrics.choose_op(relR, relP), calib's OP rule): crack px on H36's
     crack-free cells and on F51's crack-free cells, seed mean per arm: A8 <= max(1.5 x A8c, A8c + 200 px), each set.
Reported: per-seed values, F51 sign count over its crack modules, cell AUROC (max p vs >= 20 px), F19 crack AP, inactive IoU
at b_rel (records; the dumps carry no p(inactive)), and the optional SUP100-PF short-schedule reference.
Usage: python a8_screen_score.py --dump DIR --rec DIR --arm A8=RUN,RUN --arm A8c=RUN,RUN [--arm REF=RUN,RUN] --out OUT.json
       python a8_screen_score.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

CR, BINS = 14, 1000


def binned_ap(pos, neg):
    tp, fp = np.cumsum(pos[::-1]).astype(float), np.cumsum(neg[::-1]).astype(float)
    P = np.where(tp + fp > 0, tp / np.maximum(tp + fp, 1), 0.0); R = tp / max(pos.sum(), 1)
    return float(np.sum(P * np.diff(np.concatenate([[0.0], R]))))


def auroc(pos, neg):
    if not pos or not neg:
        return float("nan")
    v = np.array(pos + neg, float); r = v.argsort().argsort() + 1.0
    _, inv, cnt = np.unique(v, return_inverse=True, return_counts=True); r = (np.bincount(inv, r) / cnt)[inv]
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def cell_hist(pc, gt, keep):
    t = (gt == CR) & keep
    b = np.clip((pc.astype(np.float32) * BINS).astype(int), 0, BINS - 1)
    return np.bincount(b[t], minlength=BINS), np.bincount(b[keep & ~t], minlength=BINS), int(t.sum()), float(pc[keep].max())


def rule(H, sets, modules, arms, fa, boot=2000):
    """H[run][stem] = (pos, neg, n_gt, maxp); sets: name -> stems; modules: stem -> module; arms: name -> runs;
    fa[run][set] = crack px on crack-free cells at that run's b_rel. Returns the result dict."""
    def ap(run, stems):
        return binned_ap(np.sum([H[run][s][0] for s in stems], 0), np.sum([H[run][s][1] for s in stems], 0))
    res = {"per_run": {}, "arms": {}}
    for arm, runs in arms.items():
        for r in runs:
            res["per_run"][r] = {k: {"crack_ap": ap(r, st),
                                     "cell_auroc": auroc([H[r][s][3] for s in st if H[r][s][2] >= 20], [H[r][s][3] for s in st if H[r][s][2] == 0]),
                                     "fa_px_crackfree_at_brel": fa.get(r, {}).get(k)} for k, st in sets.items()}
        mean = lambda v: float(np.nanmean(v)) if v else None
        res["arms"][arm] = {k: {m: mean([res["per_run"][r][k][m] for r in runs if res["per_run"][r][k][m] is not None])
                                for m in ("crack_ap", "cell_auroc", "fa_px_crackfree_at_brel")} for k in sets}
    A, B = res["arms"]["A8"], res["arms"]["A8c"]
    d_f51 = A["F51"]["crack_ap"] - B["F51"]["crack_ap"]
    mods = sorted({modules[s] for s in sets["F51"]}); by = {m: [s for s in sets["F51"] if modules[s] == m] for m in mods}
    rng = np.random.default_rng(0); bs = []
    for _ in range(boot):
        st = [s for i in rng.integers(0, len(mods), len(mods)) for s in by[mods[i]]]  # multiset of stems
        d = np.mean([ap(r, st) for r in arms["A8"]]) - np.mean([ap(r, st) for r in arms["A8c"]])
        bs.append(d)
    lo = float(np.percentile(bs, 2.5))
    crack_mods = [m for m in mods if any(H[arms["A8"][0]][s][2] >= 20 for s in by[m])]
    sign = {m: float(np.mean([ap(r, by[m]) for r in arms["A8"]]) - np.mean([ap(r, by[m]) for r in arms["A8c"]])) for m in crack_mods}
    d_val = A["val"]["crack_ap"] - B["val"]["crack_ap"]
    bound = lambda x0: max(1.5 * x0, x0 + 200)
    t3 = {k: (A[k]["fa_px_crackfree_at_brel"], B[k]["fa_px_crackfree_at_brel"],
              A[k]["fa_px_crackfree_at_brel"] <= bound(B[k]["fa_px_crackfree_at_brel"])) for k in ("H36", "F51")}
    terms = {"1a_F51_dAP>0": [round(d_f51, 4), d_f51 > 0], "1b_F51_module_boot_lo>0": [round(lo, 4), lo > 0],
             "2_val_dAP>=-0.02": [round(d_val, 4), d_val >= -0.02],
             "3_FA_H36": [t3["H36"][:2], bool(t3["H36"][2])], "3_FA_F51": [t3["F51"][:2], bool(t3["F51"][2])]}
    res.update({"terms": terms, "GO": all(v[1] for v in terms.values()), "F51_modules": len(mods),
                "F51_sign_up": f"{sum(1 for v in sign.values() if v > 0)}/{len(sign)}", "F51_per_module_dAP": sign,
                "boot_hi": float(np.percentile(bs, 97.5))})
    return res


def selftest():
    rng = np.random.default_rng(1)
    stems = [f"CSIR_{100 + m:05d}_r{c}_c1_rf" for m in range(12) for c in range(3)]
    sets = {"F51": stems[:24], "H36": stems[24:30], "F19": stems[30:33], "val": stems[33:]}
    modules = {s: "_".join(s.split("_")[:2]) for s in stems}
    gts = {}
    for i, s in enumerate(stems):
        g = np.zeros((64, 64), np.uint8)
        if i % 3 == 0:
            g[20:22, 4:60] = CR
        gts[s] = g

    def run_maps(sep):
        r = np.random.default_rng(7); out = {}
        for s in stems:
            z = r.normal(-3, 1, (64, 64)); z[gts[s] == CR] += sep
            out[s] = 1 / (1 + np.exp(-z))
        return out
    H = {}
    for name, sep in (("a8_s0", 4.0), ("a8_s1", 4.0), ("c_s0", 2.0), ("c_s1", 2.0)):
        maps = run_maps(sep); keep = np.ones((64, 64), bool)
        H[name] = {s: cell_hist(maps[s], gts[s], keep) for s in stems}
    fa = {r: {"H36": 100.0, "F51": 300.0} for r in H}
    out = rule(H, sets, modules, {"A8": ["a8_s0", "a8_s1"], "A8c": ["c_s0", "c_s1"]}, fa, boot=200)
    assert out["GO"] and out["terms"]["1a_F51_dAP>0"][0] > 0, out["terms"]
    out2 = rule(H, sets, modules, {"A8": ["c_s0", "c_s1"], "A8c": ["a8_s0", "a8_s1"]}, fa, boot=200)
    assert not out2["GO"], out2["terms"]
    fa_bad = {**fa, "a8_s0": {"H36": 1000.0, "F51": 300.0}, "a8_s1": {"H36": 1000.0, "F51": 300.0}}
    assert not rule(H, sets, modules, {"A8": ["a8_s0", "a8_s1"], "A8c": ["c_s0", "c_s1"]}, fa_bad, boot=50)["GO"]
    print("SELFTEST OK", out["terms"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dump"); ap.add_argument("--rec"); ap.add_argument("--out")
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--code", default="/home/noob/work/el_f8")
    ap.add_argument("--rf", default="/home/noob/work/calib/data/rf")
    ap.add_argument("--rf-sets", default="/home/noob/work/found/t9/rf_sets.tsv")
    ap.add_argument("--el-metrics", default="/home/noob/work/found/t9")
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    from PIL import Image
    sys.path.insert(0, a.el_metrics)
    from el_metrics import GRID, choose_op, curves  # calib's scorer (copy md5 recorded in the output)
    arms = {k: v.split(",") for k, v in (x.split("=", 1) for x in a.arm)}
    assert {"A8", "A8c"} <= set(arms), arms
    rows = [l.rstrip("\n").split("\t") for l in open(a.rf_sets) if l.strip()][1:]
    rfset = {r[0]: r[1] for r in rows}; modules = {r[0]: r[3] for r in rows}
    D = Path(a.code) / "data"; RF = Path(a.rf)
    H, fa, brel, inact = {}, {}, {}, {}
    sets = None
    for runs in arms.values():
        for r in runs:
            H[r] = {}
            for sp in ("val", "rf"):
                z = np.load(Path(a.dump) / f"{r}.{sp}.npz"); st = [str(s) for s in z["stems"]]
                for i, s in enumerate(st):
                    if sp == "val":
                        gt = np.array(Image.open(D / "labeled" / "masks_escdd" / f"{s}.png")); keep = np.ones(gt.shape, bool)
                    else:
                        gt = np.array(Image.open(RF / "masks" / f"{s}.png")); keep = ~(np.array(Image.open(RF / "ignore" / f"{s}.png")) > 0)
                    H[r][s] = cell_hist(z["pc"][i], gt, keep)
                if sets is None and sp == "rf":
                    sets = {g: [s for s in st if rfset[s] == g] for g in ("F51", "H36", "F19")}
                if sp == "val":
                    vstems = st
            vr = json.load(open(Path(a.rec) / f"{r}.val.json")); assert vr["set"] == "val"
            op = choose_op(curves(vr["cells"]), "relR", "relP"); brel[r] = op["b"]; j = op["j"]
            rr = json.load(open(Path(a.rec) / f"{r}.rf.json"))["cells"]
            fa[r] = {g: float(sum(rr[s]["pred"][j] for s in sets[g] if rr[s]["n_gt"] == 0)) for g in ("H36", "F51")}
            inact[r] = {"val": float(curves(vr["cells"])["inactIoU"][j]), **{g: float(curves(rr, sets[g])["inactIoU"][j]) for g in sets}}
    sets["val"] = vstems
    res = rule(H, sets, modules, arms, fa, boot=a.boot)
    res.update({"b_rel": brel, "inactive_iou_at_brel": inact, "argv": sys.argv})
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print(json.dumps({"GO": res["GO"], "terms": res["terms"], "F51_sign_up": res["F51_sign_up"]}, indent=1, default=float))


if __name__ == "__main__":
    sys.exit(main())
