"""B6 verdict (protocol_B6 v1.0.1 s4): pooled out-of-fold inactive IoU, PF - house, two-stage paired module-cluster bootstrap.

Input: the 20 per-run files written by b6_score.py --mode b6 (<run>.b6.json; 5 folds x 2 arms x 2 seeds), the frozen folds
(results/b6/b6_folds.tsv e2cafce1), judge's groups (judge/out/b6_groups.tsv 5ff33e20), the forbidden list
(b6_forbidden.txt 9bb4d919: real test 50 + ext117 117 stems). Optional: the 20 runs' metrics.json (trainer's end-of-run
TEST block = the held-out fold) for the scorer cross-check (judge item 7). Stdlib only: runs on gaint or the laptop.

Asserts (any failure stops before a number is printed):
  inputs md5-pinned; exactly one file per (fold 0-4, arm house / PF, seed 5 / 6); every file mode b6, step 20000,
  checkpoints/latest.pth, TTA off, sets_scored ['heldout']; its cell set == its fold's stems in b6_folds.tsv;
  its arm (scorer: training.encoder_pf), fold and seed == its run name b6_{SUP,SUPPF}_f<k>_s<seed> (judge ask 1);
  no forbidden stem anywhere; one scorer md5, one device string, one code revision over all 20; per fold, the 4 runs share
  root test.txt / train.txt md5s; the 4 runs per (arm, seed) cover the 532 stems once; GT check: every cell's conf row
  sums for inactive (11) and crack (14) equal b6_folds.tsv inactive_px / crack_px (the frozen masks_escdd counts).

Primary (s4): per (arm, seed), IoU_inact = sum TP / (sum TP + FP + FN) over the 532 out-of-fold cells (counts from conf,
argmax); delta = mean over seeds 5, 6 of PF - mean of house (= mean of the two seed-pair deltas).
CI, two-stage paired bootstrap, B = 2,000, seed 0 (random.Random(0)). Per resample b, in this order:
  (a) draw G = 334 group indices uniformly with replacement from judge's groups (sorted by phys_group name);
  (b) for fold 0..4, for arm (house, PF): draw the seed from (5, 6) uniformly;
  per arm, pool the counts of the drawn groups' cells (with multiplicity), each cell's counts from the run (its fold, the
  arm, the seed drawn for that (fold, arm)); delta* = IoU_PF* - IoU_house*.
  95% percentile CI (linear interpolation between order statistics, numpy's default).
  Note (S): one seed per (fold, arm) per resample is the protocol text; with 2 seeds its expected variance equals the
  variance of the 2-seed mean (plug-in (n-1)/n s^2 = s^2/2), so it is not narrower than the estimator it brackets.
  One-stage CI (reported): the same group draws (a), all four (arm, seed) runs fixed, delta* = mean-seed PF - house.
Verdict: PASS iff CI lo > 0 and delta >= 0.01; FAIL iff CI hi < 0; else n.d. (wording fixed in s4).

Reported (s4, no verdict weight): seed-pair deltas (s5, s6) + same-sign flag; one-stage CI; crack IoU and crack relF1@2;
per source; per fold (5 x 2 x 2 table, per-fold deltas, sign count x / 10); inactive component recall / precision (Track M:
GT comps >= 20 px found iff >= 50% covered; pred comps >= 20 px correct iff any GT overlap); leave-top-3-groups-out (by
inactive px); twin groups (judge's groups holding > 1 image id) vs the rest.

Usage: python3 b6_verdict.py --scores <dir with 20 *.b6.json> --folds b6_folds.tsv --groups b6_groups.tsv \
           --forbidden b6_forbidden.txt --out <prefix> [--metrics <run>/metrics.json ...]
       python3 b6_verdict.py --selftest --folds ... --groups ... --forbidden ... --out <tmp prefix>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path

FOLDS_MD5 = "e2cafce1509bb0f2b95ce6d5db397caf"
GROUPS_MD5 = "5ff33e20d34567c331a1eca56bfbac9b"
FORBIDDEN_MD5 = "9bb4d919fc16b5b394ce6d71f53903a6"
NC, CRACK, INACT, CMIN = 24, 14, 11, 20
ARMS, SEEDS, FOLDS = ("house", "PF"), (5, 6), (0, 1, 2, 3, 4)
B_DEFAULT, BOOT_SEED, FLOOR = 2000, 0, 0.01
WORDING = {
    "PASS": "PF raises in-distribution inactive IoU on held-out physical modules (train + val pool)",
    "FAIL": "PF lowers in-distribution inactive IoU on held-out physical modules (train + val pool)",
    "n.d.": "no in-distribution inactive gain detectable at this power; PF's inactive gain is shown on unseen panels (E1) only"}


def md5(p) -> str:
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def tsv(p) -> list[dict]:
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def q(xs: list[float], p: float) -> float:
    s = sorted(xs)
    h = (len(s) - 1) * p
    lo = math.floor(h)
    return s[lo] + (h - lo) * (s[min(lo + 1, len(s) - 1)] - s[lo])


def iou(t) -> float:
    d = t[0] + t[1] + t[2]
    return t[0] / d if d else math.nan


def relf1(r) -> float:
    P = r[0] / r[1] if r[1] else math.nan
    R = r[2] / r[3] if r[3] else math.nan
    return math.nan if (math.isnan(P) or math.isnan(R) or P + R == 0) else 2 * P * R / (P + R)


def add(a, b, m=1):
    return [x + m * y for x, y in zip(a, b)]


def cell_counts(c: dict) -> dict:
    """Per-cell sufficient statistics from one m0-format record."""
    C = c["conf"]
    row = lambda k: sum(C[k * NC:(k + 1) * NC])
    col = lambda k: sum(C[j * NC + k] for j in range(NC))
    ti, tc = C[INACT * NC + INACT], C[CRACK * NC + CRACK]
    gI = [g for g in c["inact_cc"]["gt"] if g[0] >= CMIN]
    pI = [p for p in c["inact_cc"]["pr"] if p[0] >= CMIN]
    return {"inact": [ti, col(INACT) - ti, row(INACT) - ti], "crack": [tc, col(CRACK) - tc, row(CRACK) - tc],
            "rel": list(c["crack_rel2"]), "gt_inact": row(INACT), "gt_crack": row(CRACK),
            "icc": [sum(g[1] >= 0.5 * g[0] for g in gI), len(gI), sum(p[1] > 0 for p in pI), len(pI)]}


def load(a) -> tuple:
    for p, m in ((a.folds, FOLDS_MD5), (a.groups, GROUPS_MD5), (a.forbidden, FORBIDDEN_MD5)):
        assert md5(p) == m, f"md5 {p}"
    folds = tsv(a.folds)
    fold = {r["stem"]: int(r["fold"]) for r in folds}
    ipx = {r["stem"]: int(r["inactive_px"]) for r in folds}
    cpx = {r["stem"]: int(r["crack_px"]) for r in folds}
    assert len(folds) == len(fold) == 532 and set(fold.values()) == set(FOLDS)
    grows = tsv(a.groups)
    grp = {r["stem"]: r["phys_group"] for r in grows}
    img = {r["stem"]: r["b6_module"] for r in grows}
    assert set(grp) == set(fold) and all(grp[r["stem"]] == r["phys_group"] for r in folds), "groups != folds file"
    fb = {l.strip() for l in open(a.forbidden) if l.strip()}
    assert len(fb) == 167 and not fb & set(fold), "forbidden list"
    files = sorted(Path(a.scores).glob("*.b6.json")) if a.scores else []
    runs, meta = {}, {}
    for f in files:
        r = json.load(open(f))
        key = (int(r["fold"]), r["arm"], int(r["seed"]))
        assert key[0] in FOLDS and key[1] in ARMS and key[2] in SEEDS, (f.name, key)
        assert key not in runs, f"two files for {key}: {f.name}"
        # judge ask 1: the arm label comes from training.encoder_pf; cross-check it (and fold, seed) against the job name
        # (runner's b6_jobs.txt 1fea91f5: b6_{SUP,SUPPF}_f<k>_s<seed>)
        exp_name = f"b6_{'SUPPF' if key[1] == 'PF' else 'SUP'}_f{key[0]}_s{key[2]}"
        assert r["run"] == exp_name, (f.name, r["run"], "!=", exp_name, "arm / fold / seed label vs run name")
        assert r["mode"] == "b6" and int(r["step"]) == 20000 and r["weights_file"] == "checkpoints/latest.pth", f.name
        assert r["tta"] is False and r["sets_scored"] == ["heldout"] and list(r["cells"]) == ["heldout"], f.name
        cells = r["cells"]["heldout"]
        held = {s for s, k in fold.items() if k == key[0]}
        assert set(cells) == held and len(cells) == len(held), (f.name, "cell set != fold")
        assert not set(cells) & fb, (f.name, "forbidden stem")
        runs[key] = {s: cell_counts(c) for s, c in cells.items()}
        meta[key] = {x: r.get(x) for x in ("run", "scorer_md5", "device", "code_revision", "root_test_md5",
                                             "root_train_md5", "weights_md5", "config_md5", "data_root")}
    need = {(k, arm, s) for k in FOLDS for arm in ARMS for s in SEEDS}
    assert set(runs) == need, f"missing runs: {sorted(need - set(runs))}"
    for x in ("scorer_md5", "device", "code_revision"):
        vals = {m[x] for m in meta.values()}
        assert len(vals) == 1, (x, vals)
    for k in FOLDS:
        for x in ("root_test_md5", "root_train_md5"):
            assert len({meta[(k, arm, s)][x] for arm in ARMS for s in SEEDS}) == 1, (k, x)
    assert len({m["weights_md5"] for m in meta.values()}) == 20, "two runs share weights"
    for (k, arm, s), cs in runs.items():
        for st, c in cs.items():
            assert c["gt_inact"] == ipx[st] and c["gt_crack"] == cpx[st], ((k, arm, s), st, "GT px != b6_folds.tsv")
    for arm in ARMS:
        for s in SEEDS:
            u = [st for k in FOLDS for st in runs[(k, arm, s)]]
            assert sorted(u) == sorted(fold), (arm, s, "OOF cover")
    return fold, grp, img, ipx, runs, meta


def pooled(runs, fold, arm, seed, stems, key="inact"):
    t = [0, 0, 0, 0] if key in ("rel", "icc") else [0, 0, 0]
    for st in stems:
        t = add(t, runs[(fold[st], arm, seed)][st][key])
    return t


def analyse(fold, grp, img, ipx, runs, meta, B=B_DEFAULT, seed=BOOT_SEED) -> dict:
    allst = sorted(fold)
    res = {"n_cells": len(allst), "B": B, "boot_seed": seed}
    I = {(arm, s): iou(pooled(runs, fold, arm, s, allst)) for arm in ARMS for s in SEEDS}
    res["inact_iou"] = {f"{arm}_s{s}": v for (arm, s), v in I.items()}
    d_pair = {s: I[("PF", s)] - I[("house", s)] for s in SEEDS}
    delta = sum(I[("PF", s)] for s in SEEDS) / 2 - sum(I[("house", s)] for s in SEEDS) / 2
    res.update(delta=delta, delta_s5=d_pair[5], delta_s6=d_pair[6],
               same_sign=(d_pair[5] > 0) == (d_pair[6] > 0) and d_pair[5] != 0 and d_pair[6] != 0)

    # ---- bootstrap: per group, per (arm, seed), inactive counts summed over the group's cells ----
    groups = sorted(set(grp.values()))
    gst = {g: [st for st in allst if grp[st] == g] for g in groups}
    gfold = {}
    for g, sts in gst.items():
        ks = {fold[st] for st in sts}
        assert len(ks) == 1, (g, "group split across folds")
        gfold[g] = ks.pop()
    GC = {(arm, s): [pooled(runs, fold, arm, s, gst[g]) for g in groups] for arm in ARMS for s in SEEDS}
    G = len(groups)
    rng = random.Random(seed)
    two, one = [], []
    for _ in range(B):
        mult = Counter(rng.randrange(G) for _ in range(G))                       # (a)
        sd = {(k, arm): SEEDS[rng.randrange(2)] for k in FOLDS for arm in ARMS}  # (b), fold-major, house before PF
        t2 = {arm: [0, 0, 0] for arm in ARMS}
        t1 = {(arm, s): [0, 0, 0] for arm in ARMS for s in SEEDS}
        for gi, m in mult.items():
            k = gfold[groups[gi]]
            for arm in ARMS:
                t2[arm] = add(t2[arm], GC[(arm, sd[(k, arm)])][gi], m)
                for s in SEEDS:
                    t1[(arm, s)] = add(t1[(arm, s)], GC[(arm, s)][gi], m)
        two.append(iou(t2["PF"]) - iou(t2["house"]))
        one.append(sum(iou(t1[("PF", s)]) - iou(t1[("house", s)]) for s in SEEDS) / 2)
    lo, hi = q(two, 0.025), q(two, 0.975)
    res.update(ci_two_stage=[lo, hi], ci_one_stage=[q(one, 0.025), q(one, 0.975)],
               boot_sd_two=_sd(two), boot_sd_one=_sd(one), n_groups=G)
    res["verdict"] = "PASS" if (lo > 0 and delta >= FLOOR) else ("FAIL" if hi < 0 else "n.d.")
    res["wording"] = WORDING[res["verdict"]]

    # ---- reported ----
    def dset(stems, key="inact", f=iou):
        v = {(arm, s): f(pooled(runs, fold, arm, s, stems, key)) for arm in ARMS for s in SEEDS}
        return {"house": _m(v[("house", 5)], v[("house", 6)]), "PF": _m(v[("PF", 5)], v[("PF", 6)]),
                "delta": _m(v[("PF", 5)], v[("PF", 6)]) - _m(v[("house", 5)], v[("house", 6)]),
                "delta_s5": v[("PF", 5)] - v[("house", 5)], "delta_s6": v[("PF", 6)] - v[("house", 6)]}
    res["crack_iou"] = dset(allst, "crack")
    res["crack_relF1_2"] = dset(allst, "rel", relf1)
    res["inact_compR"] = dset(allst, "icc", lambda t: t[0] / t[1] if t[1] else math.nan)
    res["inact_compP"] = dset(allst, "icc", lambda t: t[2] / t[3] if t[3] else math.nan)
    src = sorted({st.split("_")[0] for st in allst})
    res["per_source"] = {}
    for sname in src:
        sts = [st for st in allst if st.split("_")[0] == sname]
        res["per_source"][sname] = {"cells": len(sts), "inact_cells": sum(ipx[x] > 0 for x in sts),
                                    "inact_px": sum(ipx[x] for x in sts), **dset(sts)}
    res["per_fold"], signs = {}, 0
    for k in FOLDS:
        sts = [st for st in allst if fold[st] == k]
        v = {f"{arm}_s{s}": iou(pooled(runs, fold, arm, s, sts)) for arm in ARMS for s in SEEDS}
        dd = {s: v[f"PF_s{s}"] - v[f"house_s{s}"] for s in SEEDS}
        signs += sum(x > 0 for x in dd.values())
        res["per_fold"][k] = {"cells": len(sts), "inact_px": sum(ipx[x] for x in sts), **v,
                              "delta_s5": dd[5], "delta_s6": dd[6]}
    res["fold_sign_count"] = f"{signs} / 10"
    gpx = Counter()
    for st in allst:
        gpx[grp[st]] += ipx[st]
    top3 = [g for g, _ in sorted(gpx.items(), key=lambda x: (-x[1], x[0]))[:3]]
    res["leave_top3_groups_out"] = {"groups": top3, "px_share": sum(gpx[g] for g in top3) / sum(gpx.values()),
                                    **dset([st for st in allst if grp[st] not in top3])}
    nimg = {g: len({img[st] for st in gst[g]}) for g in groups}
    twin = [st for st in allst if nimg[grp[st]] > 1]
    rest = [st for st in allst if nimg[grp[st]] == 1]
    res["twin_groups"] = {"n_groups": sum(n > 1 for n in nimg.values()), "cells": len(twin),
                          "inact_px": sum(ipx[x] for x in twin), **dset(twin)}
    res["non_twin"] = {"cells": len(rest), "inact_px": sum(ipx[x] for x in rest), **dset(rest)}
    res["provenance"] = {"scorer_md5": _one(meta, "scorer_md5"), "device": _one(meta, "device"),
                         "code_revision": _one(meta, "code_revision"),
                         "runs": {f"f{k}_{arm}_s{s}": meta[(k, arm, s)]["run"] for k, arm, s in sorted(meta)}}
    return res


def _m(a, b):
    return (a + b) / 2


def _sd(xs):
    mu = sum(xs) / len(xs)
    return math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1))


def _one(meta, x):
    return next(iter({m[x] for m in meta.values()}))


def cross_check(metrics_files, runs, meta, fold) -> list[str]:
    """judge item 7: trainer's end-of-run TEST (final weights) = held-out fold; inactive IoU and GT px vs the scorer."""
    byname = {m["run"]: key for key, m in meta.items()}
    out = []
    for f in metrics_files:
        p = json.load(open(f))
        key = byname[p["run_name"]]
        tf = p["test_final"]
        assert int(tf["step"]) == 20000, f
        mine = iou(pooled(runs, fold, key[1], key[2], [s for s in fold if fold[s] == key[0]]))
        gt = sum(runs[key][s]["gt_inact"] for s in runs[key])
        t_iou, t_gt = tf["per_class_iou"][INACT], tf["per_class_gt_pixels"][INACT]
        out.append(f"{p['run_name']:32s} fold {key[0]} {key[1]:5s} s{key[2]}  scorer {mine:.4f}  trainer {t_iou:.4f}  "
                   f"diff {mine - t_iou:+.5f}  GT px {gt} / {t_gt}{'' if gt == t_gt else '  GT MISMATCH'}")
    return out


def report(res) -> str:
    f = lambda x: "nan" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.4f}"
    g = lambda x: "nan" if isinstance(x, float) and math.isnan(x) else f"{x:.4f}"
    L = [f"B6 verdict (protocol_B6 v1.0.1 s4): {res['verdict']}: {res['wording']}",
         f"primary: pooled OOF inactive IoU, {res['n_cells']} cells, {res['n_groups']} groups",
         "  " + "  ".join(f"{k} {g(v)}" for k, v in res["inact_iou"].items()),
         f"  delta (mean over seeds, PF - house) {f(res['delta'])}; two-stage 95% CI [{f(res['ci_two_stage'][0])}, "
         f"{f(res['ci_two_stage'][1])}] (B {res['B']}, seed {res['boot_seed']}, boot sd {res['boot_sd_two']:.4f})",
         f"  rule: PASS iff lo > 0 and delta >= {FLOOR}; FAIL iff hi < 0",
         f"reported: seed pairs s5 {f(res['delta_s5'])}, s6 {f(res['delta_s6'])} (same sign: {res['same_sign']}; weak, "
         f"~25% under the null); one-stage CI [{f(res['ci_one_stage'][0])}, {f(res['ci_one_stage'][1])}] "
         f"(sd {res['boot_sd_one']:.4f})"]
    for k in ("crack_iou", "crack_relF1_2", "inact_compR", "inact_compP"):
        v = res[k]
        L.append(f"  {k:14s} house {g(v['house'])}  PF {g(v['PF'])}  delta {f(v['delta'])} (s5 {f(v['delta_s5'])}, s6 {f(v['delta_s6'])})")
    L.append("per source (inactive IoU, mean over seeds):")
    for s, v in res["per_source"].items():
        L.append(f"  {s:5s} cells {v['cells']:3d} inact cells {v['inact_cells']:2d} px {v['inact_px']:7d}  house {g(v['house'])}  "
                 f"PF {g(v['PF'])}  delta {f(v['delta'])}")
    L.append(f"per fold (inactive IoU; fold-seed sign count {res['fold_sign_count']}):")
    for k, v in res["per_fold"].items():
        L.append(f"  fold {k} cells {v['cells']} px {v['inact_px']:6d}  house s5 {g(v['house_s5'])} s6 {g(v['house_s6'])}  "
                 f"PF s5 {g(v['PF_s5'])} s6 {g(v['PF_s6'])}  delta s5 {f(v['delta_s5'])} s6 {f(v['delta_s6'])}")
    v = res["leave_top3_groups_out"]
    L.append(f"leave top-3 groups out ({', '.join(v['groups'])}; {v['px_share']:.3f} of px): delta {f(v['delta'])}")
    v, w = res["twin_groups"], res["non_twin"]
    L.append(f"twin groups ({v['n_groups']} groups, {v['cells']} cells, px {v['inact_px']}): delta {f(v['delta'])}; "
             f"rest ({w['cells']} cells, px {w['inact_px']}): delta {f(w['delta'])}")
    p = res["provenance"]
    L.append(f"provenance: scorer {p['scorer_md5']}, device {p['device']}, code {p['code_revision']}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ self-test (synthetic records, no model, no data)
def _fake_cell(rng, gi, gc, tp_frac, fp_px):
    C = [0] * (NC * NC)
    ti = int(gi * tp_frac); tc = int(gc * 0.5)
    C[INACT * NC + INACT], C[INACT * NC + 0] = ti, gi - ti
    C[CRACK * NC + CRACK], C[CRACK * NC + 0] = tc, gc - tc
    C[0 * NC + INACT] = fp_px
    C[0] = 512 * 512 - sum(C)
    gcc = [[gi, ti]] if gi >= CMIN else []
    pcc = ([[ti, ti]] if ti else []) + ([[fp_px, 0]] if fp_px else [])
    return {"conf": C, "crack_rel2": [tc, tc + rng.randrange(5), tc + rng.randrange(3), gc],
            "crack_cc": {"gt": [], "pr": []}, "inact_cc": {"gt": gcc, "pr": pcc}}


def _write_fake(d: Path, fold, ipx, cpx, frac, seedvar=0.0, rng_seed=1, drop=None, extra_stem=None, swap=None):
    rng = random.Random(rng_seed)
    d.mkdir(parents=True, exist_ok=True)
    for k in FOLDS:
        for arm in ARMS:
            for s in SEEDS:
                if drop == (k, arm, s):
                    continue
                fr = frac[arm] + (seedvar if (s == 6 and arm == "PF") else 0.0)
                cells = {st: _fake_cell(random.Random(f"{st}|{rng_seed}"), ipx[st], cpx[st], fr,
                                        5 if ipx[st] == 0 and st.endswith("c4") else 0)
                         for st in sorted(fold) if fold[st] == k}
                if extra_stem:
                    cells[extra_stem] = cells.pop(next(iter(cells)))
                name = f"b6_{'SUPPF' if arm == 'PF' else 'SUP'}_f{k}_s{s}"
                lab = {"house": "PF", "PF": "house"}[arm] if swap == (k, s) else arm  # config says the other arm
                rec = {"run": name, "mode": "b6", "fold": k, "seed": s, "arm": lab, "weights": "model",
                       "weights_file": "checkpoints/latest.pth", "weights_md5": f"w{k}{arm}{s}", "step": 20000,
                       "data_root": f"/r/b6_root_{k}", "root_test_md5": f"t{k}", "root_train_md5": f"r{k}",
                       "config_md5": "c", "scorer_md5": "S", "device": "cuda", "tta": False, "code_revision": "e544133",
                       "sets_scored": ["heldout"], "cells": {"heldout": cells}}
                (d / f"{name}.b6.json").write_text(json.dumps(rec))


def selftest(a) -> int:
    import shutil
    import tempfile
    base = Path(tempfile.mkdtemp(prefix="b6v_", dir=os.environ.get("TMPDIR")))
    a2 = argparse.Namespace(**vars(a))
    folds = tsv(a.folds)
    fold = {r["stem"]: int(r["fold"]) for r in folds}
    ipx = {r["stem"]: int(r["inactive_px"]) for r in folds}
    cpx = {r["stem"]: int(r["crack_px"]) for r in folds}
    ok = True

    def run(name, frac, B=200, expect_err=None, **kw):
        nonlocal ok
        d = base / name
        _write_fake(d, fold, ipx, cpx, frac, **kw)
        a2.scores = str(d)
        try:
            r = analyse(*load(a2), B=B)
        except AssertionError as e:
            good = expect_err is not None and expect_err in str(e)
            ok &= good
            print(f"  {name}: assert '{str(e)[:90]}' -> {'OK (expected)' if good else 'UNEXPECTED'}")
            return None
        if expect_err:
            ok = False
            print(f"  {name}: expected an assert ({expect_err}), got none -> FAIL")
        return r

    # 1. identical arms: delta 0, both CIs [0, 0], n.d.
    r = run("null", {"house": 0.5, "PF": 0.5})
    c = r and r["delta"] == 0 and r["ci_two_stage"] == [0, 0] and r["ci_one_stage"] == [0, 0] and r["verdict"] == "n.d."
    ok &= bool(c); print(f"  null: delta {r['delta']} CI {r['ci_two_stage']} {r['verdict']} -> {'OK' if c else 'FAIL'}")
    # 2. planted gain, no seed noise: pooled IoU by hand (TP / (GT + FP)), PASS, one- and two-stage CIs equal
    r = run("gain", {"house": 0.5, "PF": 0.6})
    tp = lambda fr: sum(int(ipx[s] * fr) for s in fold)
    fp = sum(5 for s in fold if ipx[s] == 0 and s.endswith("c4"))
    gt = sum(ipx.values())
    hand = tp(0.6) / (gt + fp) - tp(0.5) / (gt + fp)
    c = r and abs(r["delta"] - hand) < 1e-12 and r["verdict"] == "PASS" and r["ci_two_stage"] == r["ci_one_stage"]
    ok &= bool(c); print(f"  gain: delta {r['delta']:.6f} hand {hand:.6f} CI [{r['ci_two_stage'][0]:.4f}, "
                         f"{r['ci_two_stage'][1]:.4f}] {r['verdict']} -> {'OK' if c else 'FAIL'}")
    # 3. seed noise only in PF: two-stage CI wider than one-stage; seed-pair deltas differ
    r = run("seednoise", {"house": 0.5, "PF": 0.5}, seedvar=0.08)
    c = r and (r["ci_two_stage"][1] - r["ci_two_stage"][0]) > (r["ci_one_stage"][1] - r["ci_one_stage"][0]) \
        and r["delta_s5"] == 0 and r["delta_s6"] > 0
    ok &= bool(c); print(f"  seednoise: two-stage {[round(x, 4) for x in r['ci_two_stage']]} one-stage "
                         f"{[round(x, 4) for x in r['ci_one_stage']]} -> {'OK' if c else 'FAIL'}")
    # 4. loss: FAIL
    r = run("loss", {"house": 0.6, "PF": 0.45})
    c = r and r["verdict"] == "FAIL"
    ok &= bool(c); print(f"  loss: delta {r['delta']:.4f} {r['verdict']} -> {'OK' if c else 'FAIL'}")
    # 5. asserts
    run("missing", {"house": 0.5, "PF": 0.5}, B=10, expect_err="missing runs", drop=(3, "PF", 6))
    run("swapped", {"house": 0.5, "PF": 0.5}, B=10, expect_err="arm / fold / seed label", swap=(2, 5))
    fb = sorted(l.strip() for l in open(a.forbidden) if l.strip())
    run("forbidden", {"house": 0.5, "PF": 0.5}, B=10, expect_err="cell set != fold", extra_stem=fb[0])
    shutil.rmtree(base)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores")
    ap.add_argument("--folds", required=True)
    ap.add_argument("--groups", required=True)
    ap.add_argument("--forbidden", required=True)
    ap.add_argument("--out", required=True, help="output prefix: <out>.json and <out>.txt")
    ap.add_argument("--metrics", nargs="*", default=[])
    ap.add_argument("--boot", type=int, default=B_DEFAULT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a)
    assert a.boot == B_DEFAULT, "the protocol fixes B = 2,000"
    fold, grp, img, ipx, runs, meta = load(a)
    res = analyse(fold, grp, img, ipx, runs, meta)
    txt = report(res)
    if a.metrics:
        cc = cross_check(a.metrics, runs, meta, fold)
        res["trainer_test_crosscheck"] = cc
        txt += "trainer TEST block (final weights = held-out fold) vs scorer, reported only:\n" + "\n".join(cc) + "\n"
    res["script_md5"] = md5(__file__)
    Path(a.out + ".json").write_text(json.dumps(res, indent=1))
    Path(a.out + ".txt").write_text(txt)
    print(txt, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
