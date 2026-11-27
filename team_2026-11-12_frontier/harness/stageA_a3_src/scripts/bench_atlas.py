"""elbench stage A3: ci_error_atlas (T10 spec A0; WAVE3_REVIEW Y4, S2, guard G20, gin_ipa verdict P-GIN (d)).

One inactive and weak-class error atlas on the out-of-fold PF v1.1 dumps (cv5v2, all folds, every seed of one arm),
read by the gates of T6 (vfm_ctx gate 1), T8 (C3, UCF step B, C-BMRK), T10 (G-rules, G-layer, G-paste, G-refine,
G-bias, arm 1 pre-check) and T13 (SAM gate, ICL readability), each at its own threshold, plus P-GIN (d).
Every gate share: point (seed mean of pooled counts), 95% two-stage group bootstrap interval (330 groups, then one
seed per fold; B = 2000, seed 0), leave-top-3-groups-out value, region-count value, per-source and per-fold values.
Optional --control: the T10 positive control on W1-C3 (PF on v1 masks, scored on v1 masks); the label-issue list
(label_issues_t10.tsv) is written only if the control passes.

CPU only: CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 nice -n 19, at most 8 workers. Reads open cv5v2 OOF dumps of the
532 pool cells only; sealed sets and sealed stems are refused (bench/w1read.py, bench/derived.assert_open, and the
pool check below). Refuses to write into an existing non-empty --out. Deterministic.
  python scripts/bench_atlas.py --arm PF=<method dir>:'w1g_pf_v11_f[0-4]_s[56]' --labels v11 \
      --control PFV1=<method dir>:'w1c3_pf_v1_f[0-4]_s[56]' --workers 8 --out <dir>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import atlas as AT  # noqa: E402
from bench import cellmeta, derived, dumpfmt, sets, w1read  # noqa: E402

B1_FLAGS = Path("/home/yugma/mtp/research/team_2026-10-29_features/b1_audit/b1_flags_A50.tsv")


def parse(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, help="NAME=<method dir>:<run_id regex> (one arm, every seed)")
    ap.add_argument("--labels", default="v11", choices=cellmeta.LABEL_SETS)
    ap.add_argument("--control", default=None, help="NAME=<method dir>:<run_id regex> of PF on v1 masks (W1-C3)")
    ap.add_argument("--control-labels", default="v1", choices=cellmeta.LABEL_SETS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--allow-partial", action="store_true")
    return ap.parse_args(argv)


def pool_stems() -> set:
    cells = cellmeta.load_cells()
    return {s for s, r in cells.items() if (r.get("bench_set") or "").startswith("cv5v2")}


def check_open(runs, stems):
    pool = pool_stems()
    assert len(pool) == 532, f"pool size {len(pool)} != 532"
    for r in runs:
        derived.assert_open(r.set_name, r.stems)
        assert set(r.stems) <= pool, f"{r.run_id}: stems outside the 532 pool"
    derived.assert_open(None, stems)
    assert set(stems) <= pool


def _job(a):
    stem, set_dirs, gt, img_dir = a
    g, keep = cellmeta.load_gt(gt, stem)
    dumps = [dumpfmt.read_cell(Path(sd) / f"{stem}.npz", check=True) for sd in set_dirs]
    for d in dumps:
        assert "logp" in d, f"{stem}: dump without logp ({set_dirs})"
    img = np.array(Image.open(Path(img_dir) / f"{stem}.png").convert("L"), dtype=np.uint8)
    return stem, AT.cell_atlas(g, keep, dumps, img, stem)


def _cjob(a):
    stem, set_dirs, gt = a
    g, keep = cellmeta.load_gt(gt, stem)
    pcs = [np.load(Path(sd) / f"{stem}.npz")["p_crack"] for sd in set_dirs]
    return stem, AT.control_cell(g, keep, pcs)


def load_arm(spec, labels, allow_partial, groups):
    runs = w1read.discover([spec], labels)
    w1read.check_comparable(runs, dry=False)
    arms, fold_of, stems, notes = w1read.assemble(runs, groups, allow_partial=allow_partial)
    assert len(arms) == 1
    by_seed = next(iter(arms.values()))
    seeds = sorted(by_seed)
    where = {}
    for sd in seeds:
        for r in by_seed[sd]:
            for s in r.stems:
                where.setdefault(s, {})[sd] = r
    return runs, seeds, fold_of, stems, notes, where


def fmt(x, nd=3):
    if x is None:
        return "n/a"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return "n/a" if not math.isfinite(x) else f"{x:.{nd}f}"


def main(argv=None):
    a = parse(argv)
    t0 = time.time()
    out = Path(a.out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"refuse: {out} exists and is not empty")
    assert 1 <= a.workers <= 8
    groups = cellmeta.load_groups()
    cells_meta = cellmeta.load_cells()
    runs, seeds, fold_of, stems, notes, where = load_arm(a.arm, a.labels, a.allow_partial, groups)
    check_open(runs, stems)
    gt = runs[0].gt
    assert all(r.gt == gt for r in runs)
    img_dir = sets.resolve(runs[0].set_name)["images"]
    md5s = {"cells.tsv": cellmeta.md5(cellmeta.CELLS_TSV), "cv5v2_groups.tsv": cellmeta.md5(cellmeta.GROUPS_TSV),
            "masks_v11 MANIFEST.md5": cellmeta.md5(sets.MASKS_V11 / "MANIFEST.md5"),
            "b1_flags_A50.tsv": cellmeta.md5(B1_FLAGS) if B1_FLAGS.exists() else "missing",
            "atlas.py": cellmeta.md5(ROOT / "bench" / "atlas.py"), "bench_atlas.py": cellmeta.md5(Path(__file__))}
    man = {r.run_id: r.manifest_md5 for r in runs}
    print(f"[atlas] arm {a.arm} labels {a.labels}: {len(runs)} runs, seeds {seeds}, {len(stems)} cells", flush=True)
    for k, v in sorted(man.items()):
        print(f"[atlas] manifest md5 {k} {v}", flush=True)
    for k, v in md5s.items():
        print(f"[atlas] input md5 {k} {v}", flush=True)
    for n in notes:
        print(f"[atlas] NOTE {n}", flush=True)

    jobs = [(s, [str(where[s][sd].set_dir) for sd in seeds], gt, str(img_dir)) for s in stems]
    ctx = get_context("fork")
    with ctx.Pool(a.workers) as pool:
        res = dict(pool.imap(_job, jobs, chunksize=2))
        print(f"[atlas] cells done {time.time() - t0:.0f} s", flush=True)
        control = None
        if a.control:
            cr, cseeds, cfold, cstems, cnotes, cwhere = load_arm(a.control, a.control_labels, a.allow_partial, groups)
            check_open(cr, cstems)
            cgt = cr[0].gt
            cj = [(s, [str(cwhere[s][sd].set_dir) for sd in cseeds], cgt) for s in cstems]
            cres = dict(pool.imap(_cjob, cj, chunksize=8))
            control = AT.control_verdict(cres)
            control.update(arm=a.control, labels=cgt["labels"], seeds=cseeds, notes=cnotes,
                           manifests={r.run_id: r.manifest_md5 for r in cr}, scores=cres)
            print(f"[atlas] control done {time.time() - t0:.0f} s: pass={control['pass']}", flush=True)

    # ---------------------------------------------------------------- features
    names = sorted({k for s in stems for f in res[s]["feats"] for k in f})
    F = np.zeros((len(stems), len(seeds), len(names)))
    idx = {k: i for i, k in enumerate(names)}
    for i, s in enumerate(stems):
        for j, f in enumerate(res[s]["feats"]):
            for k, v in f.items():
                F[i, j, idx[k]] = v
    src = {s: cellmeta.source(s) for s in stems}
    sources = [f"src:{x}" for x in sorted(set(src.values()))]
    shape = np.array([res[s]["cell"]["shape"] for s in stems])
    thr = float(np.nanquantile(shape, 0.9))
    top = np.where(np.isfinite(shape), shape >= thr, False)
    rest = np.isfinite(shape) & ~top
    topw = np.zeros(len(stems), bool)
    for so in sources:
        m = np.array([f"src:{src[s]}" == so for s in stems]) & np.isfinite(shape)
        if m.any():
            topw |= m & (shape >= np.nanquantile(shape[m], 0.9))
    restw = np.isfinite(shape) & ~topw
    subsets = {"all": np.ones(len(stems), bool), "pg_top": top, "pg_rest": rest, "pgw_top": topw, "pgw_rest": restw}
    for so in sources:
        m = np.array([f"src:{src[s]}" == so for s in stems])
        subsets[so] = m
        subsets[f"pg_top&{so}"] = m & top
        subsets[f"pg_rest&{so}"] = m & rest
    folds = sorted(set(fold_of[s] for s in stems))
    for k in folds:
        subsets[f"fold:{k}"] = np.array([fold_of[s] == k for s in stems])
    P = AT.Pooled(stems, seeds, names, F, fold_of, groups, subsets)

    vpt = P.point()
    rule_d = 10 if (AT.ratio(vpt["all"]["gt_cr5"], vpt["all"]["gt_r100"]) < 0.97) else 5
    S = AT.stat_defs(sources, folds, rule_d)
    stats = {k: v[0] for k, v in S.items()}
    for k, (fn, topf, kind) in S.items():
        if kind == "inact":
            for so in sources:
                stats[f"{k} @{so}"] = AT.scoped(fn, so)
    print(f"[atlas] bootstrap {a.boot} draws, {len(stats)} stats, {len(names)} features", flush=True)
    boot = P.boot(stats, n_boot=a.boot, seed=0)
    print(f"[atlas] bootstrap done {time.time() - t0:.0f} s", flush=True)

    per_seed = [P.point(seed_idx=j) for j in range(len(seeds))]
    table = {}
    for k, (fn, topf, kind) in S.items():
        sub = "src:BMRK" if k.startswith("C-BMRK") and "src:BMRK" in subsets else "all"
        tg = P.top_groups(topf, sub)
        lt3 = fn(P.point(drop=P.drop_mask(tg)))
        row = {"point": fn(vpt), "lo": boot["stats"][k]["lo"], "hi": boot["stats"][k]["hi"],
               "se": boot["stats"][k]["se"], "lt3": lt3, "lt3_groups": tg, "kind": kind,
               "per_seed": {str(sd): fn(per_seed[j]) for j, sd in enumerate(seeds)}}
        if kind == "inact":
            row["by_source"] = {so: {"point": AT.scoped(fn, so)(vpt), "lo": boot["stats"][f"{k} @{so}"]["lo"],
                                     "hi": boot["stats"][f"{k} @{so}"]["hi"]} for so in sources}
            row["by_fold"] = {str(f): AT.scoped(fn, f"fold:{f}")(vpt) for f in folds}
        table[k] = row

    # ---------------------------------------------------------------- gates
    def val(stat, which="point"):
        return table[stat][which]

    gates = []
    for name, owner, conds, comb, words, rcs in AT.GATES:
        cp = [AT.holds(val(st), op, th) for _, st, op, th in conds]
        cl = [AT.holds(val(st, "lt3"), op, th) for _, st, op, th in conds]
        gates.append({"gate": name, "owner": owner, "outcome": AT.gate_outcome(cp, cl, comb, words), "combine": comb,
                      "conditions": [{"label": lb, "stat": st, "op": op, "thr": th, **{x: table[st][x] for x in
                                      ("point", "lo", "hi", "lt3", "lt3_groups")},
                                      "region_count": table[rcs[lb]]["point"] if lb in rcs else None,
                                      "region_count_lt3": table[rcs[lb]]["lt3"] if lb in rcs else None}
                                     for lb, st, op, th in conds]})
    # G-bias (T10): in-sample single-class oracle gain >= 0.05 on gridline or splice (closes nothing)
    gb = [AT.holds(val(f"w{c} oracle_gain"), ">=", 0.05) for c in (15, 16)]
    gbl = [AT.holds(val(f"w{c} oracle_gain", "lt3"), ">=", 0.05) for c in (15, 16)]
    gates.append({"gate": "G-bias", "owner": "T10 arm 2 classbias_xfit (expectation only)",
                  "outcome": AT.gate_outcome(gb, gbl, "any", ("MET", "NOT MET")),
                  "conditions": [{"label": f"{AT.WEAK[c]} oracle gain", "stat": f"w{c} oracle_gain", "op": ">=",
                                  "thr": 0.05, **{x: table[f"w{c} oracle_gain"][x] for x in
                                                  ("point", "lo", "hi", "lt3", "lt3_groups")}} for c in (15, 16)]})
    la = [val(f"w{c} oracle_gain") for c in AT.WEAK]
    la_note = ("some weak class gains >= +0.02 in-sample" if any(x >= 0.02 for x in la if math.isfinite(x))
               else "no weak class gains >= +0.02 in-sample: 'decision-limited share small', la_ce stays closed")
    # G-rules (T10): GT-only; variant d
    gr, grl = val("G-rules gt_cr5"), val("G-rules gt_cr5", "lt3")
    d_pt, d_lt = (10 if gr < 0.97 else 5), (10 if grl < 0.97 else 5)
    gates.append({"gate": "G-rules", "owner": "T10 arm 1 ci_rules_posthoc (variant d)",
                  "outcome": f"d = {d_pt}" if d_pt == d_lt else f"LEAD DECIDES (d = {d_pt} on all, {d_lt} without top 3)",
                  "conditions": [{"label": "GT inactive comps with GT crack within 5 px", "stat": "G-rules gt_cr5",
                                  "op": "<", "thr": 0.97, **{x: table["G-rules gt_cr5"][x] for x in
                                                             ("point", "lo", "hi", "lt3", "lt3_groups")}}]})
    # arm 1 pre-check (part d): R-a deletes >= 3% at precision <= 0.40; R-b adds >= 3% at precision >= 0.50
    for nm, cs in ((f"P-rules R-a (d = {rule_d})", [(f"R-a{rule_d} share", ">=", 0.03), (f"R-a{rule_d} prec", "<=", 0.40)]),
                   ("P-rules R-b", [("R-b share", ">=", 0.03), ("R-b prec", ">=", 0.50)])):
        cp = [AT.holds(val(st), op, th) for st, op, th in cs]
        cl = [AT.holds(val(st, "lt3"), op, th) for st, op, th in cs]
        gates.append({"gate": nm, "owner": "T10 arm 1 ci_rules_posthoc (spend the 2 build h)",
                      "outcome": AT.gate_outcome(cp, cl, "all", ("PASS (variant built)", "FAIL (variant dropped)")),
                      "conditions": [{"label": st, "stat": st, "op": op, "thr": th, **{x: table[st][x] for x in
                                      ("point", "lo", "hi", "lt3", "lt3_groups")}} for st, op, th in cs]})
    # T6 vfm_ctx gate 1
    t6p = AT.t6_outcome(val("T6 miss px"), val("T6 false px"))
    t6l = AT.t6_outcome(val("T6 miss px", "lt3"), val("T6 false px", "lt3"))
    gates.append({"gate": "T6 gate 1 (inactive_anatomy)", "owner": "T6 vfm_ctx_r34_pf",
                  "outcome": t6p if t6p == t6l else f"LEAD DECIDES ({t6p} on all cells, {t6l} without the top 3 groups)",
                  "conditions": [{"label": lb, "stat": st, "op": ">= 0.5 build / < 0.3 park", "thr": None,
                                  **{x: table[st][x] for x in ("point", "lo", "hi", "lt3", "lt3_groups")},
                                  "region_count": table[rc]["point"], "region_count_lt3": table[rc]["lt3"]}
                                 for lb, st, rc in (("region-miss share of FN", "T6 miss px", "T6 miss rc"),
                                                    ("false-region share of FP", "T6 false px", "T6 false rc"))]})
    # T8 C-BMRK (arm parked by the critic: informational)
    if "src:BMRK" in subsets:
        c1 = AT.holds(val("C-BMRK fa50"), ">=", 0.20)
        c2 = (val("C-BMRK inact FP-FN") > 0) and bool(AT.holds(val("C-BMRK inact prec"), "<", 0.5))
        c3 = AT.holds(val("C-BMRK relP2 gap"), ">=", 0.05)
        l1 = AT.holds(val("C-BMRK fa50", "lt3"), ">=", 0.20)
        l2 = (val("C-BMRK inact FP-FN", "lt3") > 0) and bool(AT.holds(val("C-BMRK inact prec", "lt3"), "<", 0.5))
        l3 = AT.holds(val("C-BMRK relP2 gap", "lt3"), ">=", 0.05)
        gates.append({"gate": "C-BMRK", "owner": "T8 elpv_bmrk_negatives (DROPPED / parked by the critic; record only)",
                      "outcome": AT.gate_outcome([c1, c2, c3], [l1, l2, l3], "any", ("PASS", "PARK")),
                      "conditions": [{"label": st, "stat": st, **{x: table[st][x] for x in
                                      ("point", "lo", "hi", "lt3", "lt3_groups")}}
                                     for st in ("C-BMRK fa50", "C-BMRK inact FP-FN", "C-BMRK inact prec",
                                                "C-BMRK relP2 gap")]})
    # T13 ICL readability (arm parked): >= 8 PF-missed inactive regions
    nm_pt = val("n_missed_regions")
    gates.append({"gate": "ICL readability", "owner": "T13 icl_oof_probe (DROPPED / parked; record only)",
                  "outcome": "READABLE" if nm_pt >= 8 else "NOT READABLE",
                  "conditions": [{"label": "missed GT inactive regions (seed mean)", "stat": "n_missed_regions",
                                  **{x: table["n_missed_regions"][x] for x in ("point", "lo", "hi", "lt3", "lt3_groups")}}]})
    # P-GIN (d): deficit = point < 0, interval wholly below 0, and < 0 without the top 3 crack groups
    pg = table["P-GIN dR2"]
    if not math.isfinite(pg["point"]):
        pgo = "NOT READABLE"
    elif pg["point"] < 0 and pg["hi"] < 0 and pg["lt3"] < 0:
        pgo = "DEFICIT (photometric half has support)"
    elif pg["point"] < 0 and pg["hi"] < 0:
        pgo = "LEAD DECIDES (deficit on all cells, not without the top 3 groups)"
    else:
        pgo = "NO DEFICIT (photometric half of gin_ipa has no support here)"
    gates.append({"gate": "P-GIN (d)", "owner": "T7 gin_ipa (critic's addition)", "outcome": pgo,
                  "conditions": [{"label": "relR@2 top decile - rest", "stat": "P-GIN dR2", "op": "< 0, hi < 0",
                                  "thr": 0.0, **{x: pg[x] for x in ("point", "lo", "hi", "lt3", "lt3_groups")}}]})

    # ---------------------------------------------------------------- label issues (published only if control passes)
    issues = [r for s in stems for r in res[s]["issues"]]
    fl_in_cells = sorted({r["stem"] for r in issues if r["class"] == "inactive" and r["type"] == "FL"})
    b1_overlap = sorted(set(fl_in_cells) & set(AT.B1_INACT_FL))
    published = bool(control and control["pass"])

    # ---------------------------------------------------------------- write
    out.mkdir(parents=True, exist_ok=True)
    head = (f"ci_error_atlas (stage A3). arm {a.arm}, labels {a.labels}, seeds {seeds}, {len(stems)} cells, "
            f"{len(runs)} runs; bootstrap B = {a.boot}, seed 0, {boot['units']} groups; point = seed mean of pooled "
            f"counts; lt3 = leave the 3 groups with most GT px of the class read; rc = region-count share.")
    L = [head, f"elapsed {time.time() - t0:.0f} s; inputs: " + ", ".join(f"{k} {v}" for k, v in md5s.items())]
    L += [f"manifest md5 {k} {v}" for k, v in sorted(man.items())] + [f"NOTE {n}" for n in notes]
    L.append("")
    L.append("== Gates (thresholds as each team wrote them; Y4: opens only if it also holds without the top 3 groups)")
    for gte in gates:
        L.append(f"{gte['gate']} [{gte['owner']}]: {gte['outcome']}")
        for c in gte["conditions"]:
            rc = (f"; rc {fmt(c['region_count'])} (lt3 {fmt(c.get('region_count_lt3'))})"
                  if c.get("region_count") is not None else "")
            thr_s = f" {c.get('op', '')} {c['thr']}" if c.get("thr") is not None else (f" {c.get('op')}" if c.get("op") else "")
            L.append(f"  {c['label']}{thr_s}: {fmt(c['point'])} [{fmt(c['lo'])}, {fmt(c['hi'])}], "
                     f"lt3 {fmt(c['lt3'])} (drop {','.join(c['lt3_groups'])}){rc}")
    L.append(f"G-bias note: {la_note}")
    o2, o15 = table["O2"]["point"], table["O1+O5"]["point"]
    L.append(f"D2 pointer (critic: the trained inactive arm whose gate opens with the larger oracle gain): "
             f"O2 (paste) {fmt(o2)}, O1+O5 (layered_ci) {fmt(o15)}")
    L.append("")

    def line(k, nd=3):
        r = table[k]
        ps = " ".join(f"s{sd} {fmt(v, nd)}" for sd, v in r["per_seed"].items())
        return (f"  {k}: {fmt(r['point'], nd)} [{fmt(r['lo'], nd)}, {fmt(r['hi'], nd)}] lt3 {fmt(r['lt3'], nd)}; {ps}")

    L.append("== (a) Inactive error buckets (px shares), oracles, regions")
    for k in ["inact_iou", "inact_prec", "inact_rec"] + [f"fn_{b}/fn" for b in AT.FN_B] + \
             [f"fp_{b}/fp" for b in AT.FP_B] + [f"fn_{b}/err" for b in AT.FN_B] + [f"fp_{b}/err" for b in AT.FP_B] + \
             [f"rc_fn_{b}/rc" for b in AT.FN_B] + [f"rc_fp_{b}/rc" for b in AT.FP_B] + \
             ["O1", "O2", "O3", "O4", "O5", "O1+O5", "region_recall50", "region_recall_any", "region_prec100",
              "n_gt_regions100", "n_missed_regions", "T6 blind share"] + \
             (["T6 false BMRK share"] if "T6 false BMRK share" in table else []):
        L.append(line(k))
    v = vpt["all"]
    L.append("  px (seed mean): FN " + ", ".join(f"{b} {v['fn_' + b]:.0f}" for b in AT.FN_B) + f"; total {v['fn']:.0f}")
    L.append("  px (seed mean): FP " + ", ".join(f"{b} {v['fp_' + b]:.0f}" for b in AT.FP_B) + f"; total {v['fp']:.0f}")
    L.append("  FP-spurious split (seed mean px): " + ", ".join(
        f"{x} {v['fp_sp_' + x]:.0f}" for x in ("gi_pc", "gi_nopc", "nogi_pc", "nogi_nopc")))
    take = {k: v[f"t6_take_{k}"] for k in range(AT.NCLS) if v[f"t6_take_{k}"]}
    L.append("  T6 region-miss px taken by class: " + ", ".join(f"{k} {x:.0f}" for k, x in
                                                              sorted(take.items(), key=lambda t: -t[1])))
    L.append("G20: per source (point [95% interval]) and per fold (point) of the inactive gate shares")
    for k in ("inact_iou", "G-layer px", "G-paste px", "G-refine px", "G-sam px", "T6 miss px", "T6 false px",
              "T8 a px", "T8 b px", "T8 c px", "O1+O5", "O2", "O4", "region_recall50"):
        r = table[k]
        L.append(f"  {k}: " + "; ".join(f"{so[4:]} {fmt(x['point'])} [{fmt(x['lo'])}, {fmt(x['hi'])}]"
                                         for so, x in r["by_source"].items())
                 + " | folds " + " ".join(f"{f}:{fmt(x)}" for f, x in r["by_fold"].items()))
    L.append("")
    L.append("== (b) Crack at the overlap (GT crack px within 2 px of GT inactive)")
    for k in ("crack_at_share", "crack_at_p14", "crack_at_p11", "crack_at_p0", "crack_at_relR2", "crack_el_p14",
              "crack_el_p11", "crack_el_relR2", "crack_fn_as_inact"):
        L.append(line(k))
    L.append("")
    L.append("== (c) Weak classes")
    for c, nm in AT.WEAK.items():
        L.append(f"{nm} ({c}): GT px {v[f'w{c}_gp']:.0f}, groups with GT px "
                 f"{len({P.group[i] for i in range(len(stems)) if F[i, 0, idx.get(f'w{c}_gp', 0)] > 0}) if f'w{c}_gp' in idx else 0}")
        for k in (f"w{c} iou", f"w{c} comp_missed", f"w{c} err_bnd2", f"w{c} oracle_gain", f"T6w{c} miss px",
                  f"T6w{c} false px"):
            L.append(line(k))
        gain, bb, i0 = AT.weak_oracle(v, c)
        L.append(f"  oracle (seed mean counts): IoU at b=0 {fmt(i0)}, best b {bb:+.2f}, gain {fmt(gain)}")
        fnby = {k: v[f"w{c}_fnby{k}"] for k in range(AT.NCLS) if v[f"w{c}_fnby{k}"]}
        fpby = {k: v[f"w{c}_fpby{k}"] for k in range(AT.NCLS) if v[f"w{c}_fpby{k}"]}
        tfn, tfp = sum(fnby.values()) or 1, sum(fpby.values()) or 1
        L.append("  FN by predicted class (top 5): " + ", ".join(
            f"{k} {x / tfn:.3f}" for k, x in sorted(fnby.items(), key=lambda t: -t[1])[:5]))
        L.append("  FP by GT class (top 5): " + ", ".join(
            f"{k} {x / tfp:.3f}" for k, x in sorted(fpby.items(), key=lambda t: -t[1])[:5]))
        h = np.array([v[f"w{c}_mh{i}"] for i in range(len(AT.MH_EDGES) - 1)])
        if h.sum():
            cdf = np.cumsum(h) / h.sum()
            q = [AT.MH_EDGES[1:][np.searchsorted(cdf, x)] for x in (0.25, 0.5, 0.75)]
            below6 = h[AT.MH_EDGES[1:] <= -6.0].sum() / h.sum()
            L.append(f"  FN margin logp_c - max other (nats, bin 0.25, upper edges): q25 {q[0]:.2f}, median {q[1]:.2f}, "
                     f"q75 {q[2]:.2f}; share below -6: {below6:.3f}")
    L.append("")
    L.append("== (d) Co-occurrence rule statistics (arm 1 pre-check)")
    for k in ["G-rules gt_cr3", "G-rules gt_cr5", "G-rules gt_cr10"] + \
             [f"R-a{d_} {x}" for d_ in AT.RULE_D for x in ("share", "prec", "comps")] + ["R-b share", "R-b prec"]:
        L.append(line(k))
    L.append(f"  px (seed mean): pred inactive {v['pi_px']:.0f}; R-a5 {v['ra5_px']:.0f} ({v['ra5_n']:.1f} comps), "
             f"R-a10 {v['ra10_px']:.0f} ({v['ra10_n']:.1f}); R-b holes {v['rb_px']:.0f} px in {v['rb_n']:.1f} comps")
    L.append("")
    L.append("== (e) Label quality")
    if control:
        L.append(f"positive control: arm {control['arm']} labels {control['labels']} seeds {control['seeds']}; "
                 f"{control['n_ranked']} cells with GT crack ranked by crack softmin; worst 10% = rank <= "
                 f"{control['cut_rank']}: {'PASS' if control['pass'] else 'FAIL'}")
        for r in control["rows"]:
            L.append(f"  {r['stem']}: rank {r['rank']} of {r['of']}, score {fmt(r['score'], 4)}, in worst 10% {r['in_worst']}")
        for k, x in sorted(control["manifests"].items()):
            L.append(f"  control manifest md5 {k} {x}")
    else:
        L.append("positive control: not run (no --control); the label-issue list is withheld")
    cnt = {}
    for r in issues:
        cnt[(r["class"], r["type"])] = cnt.get((r["class"], r["type"]), 0) + 1
    L.append("candidates (components): " + ", ".join(f"{c} {t} {n}" for (c, t), n in sorted(cnt.items())))
    L.append(f"inactive FL candidate cells {len(fl_in_cells)}; overlap with the B1 audit's 9 inactive-FL cells: "
             f"{len(b1_overlap)}" + (f" ({', '.join(b1_overlap)})" if published else ""))
    L.append("label_issues_t10.tsv: " + ("written" if published else "WITHHELD (positive control did not pass)"))
    L.append("")
    L.append("== P-GIN (d): PF OOF crack relR@2, top decile of histogram shape (p50-p5)/(p95-p5) vs the rest")
    L.append(f"  shape threshold (p90 over {int(np.isfinite(shape).sum())} pool cells) {thr:.4f}; cells top {int(top.sum())} "
             f"(with crack {int((top & (np.array([res[s]['cell']['gc_px'] for s in stems]) > 0)).sum())}), rest {int(rest.sum())}")
    for k in ("P-GIN relR2 top", "P-GIN relR2 rest", "P-GIN dR2", "P-GIN dR2 within-source decile") + \
             tuple(f"P-GIN dR2 {so}" for so in sources):
        L.append(line(k))
    L.append("  cells per source in the top decile: " + ", ".join(
        f"{so[4:]} {int(subsets[f'pg_top&{so}'].sum())}" for so in sources))
    L.append("")
    L.append("== Other sources' crack relP@2 (C-BMRK input)")
    for so in sources:
        L.append(line(f"relP2 {so}"))
    text = "\n".join(L) + "\n"

    w1read.write_once(out / "summary.txt", text)
    jdoc = {"arm": a.arm, "labels": a.labels, "seeds": seeds, "n_cells": len(stems), "manifests": man, "inputs": md5s,
            "notes": notes, "boot": {k: boot[k] for k in ("B", "boot_seed", "units")}, "rule_d": rule_d,
            "pgin_threshold": thr, "gates": gates, "stats": table, "la_note": la_note,
            "control": None if control is None else {k: control[k] for k in control if k != "scores"},
            "label_issues_published": published, "b1_overlap_n": len(b1_overlap)}
    w1read.write_once(out / "gates.json", json.dumps(jdoc, indent=1, default=float))
    cols = ["stem", "source", "fold", "group", "gi_px", "gc_px", "shape", "softmin", "crack_softmin"] + \
           [f"p009_{c}{x}" for c in AT.P009_CLS for x in ("", "_sd")]
    rows = ["\t".join(cols)]
    for s in stems:
        c = res[s]["cell"]
        rows.append("\t".join([s, src[s], str(fold_of[s]), groups[s]] +
                              [fmt(c[k], 5) if isinstance(c[k], float) else str(c[k]) for k in cols[4:]]))
    w1read.write_once(out / "cells.tsv", "\n".join(rows) + "\n")
    rg = [r for s in stems for r in res[s]["regions"]]
    gk = ["stem", "comp", "px", "d_crack_min", "coco", "fl", "cov"]
    pk = ["stem", "seed_idx", "comp", "px", "on_gi", "near_gi3", "d_pc_min", "spurious"]
    w1read.write_once(out / "regions_gt.tsv", "\n".join(["\t".join(gk + ["seeds"])] + [
        "\t".join([str(r[k]) for k in gk] + [",".join(map(str, seeds))]) for r in rg if r["kind"] == "gt"]) + "\n")
    w1read.write_once(out / "regions_pred.tsv", "\n".join(["\t".join(pk + ["seed"])] + [
        "\t".join([str(r[k]) for k in pk] + [str(seeds[r["seed_idx"]])]) for r in rg if r["kind"] == "pred"]) + "\n")
    bk = ["scope", "seed", "bucket", "px", "share_of_side", "share_of_err"]
    brow = ["\t".join(bk)]
    for scope in ["all"] + sources + [f"fold:{k}" for k in folds]:
        for sd, V in [("mean", vpt)] + [(str(seeds[j]), per_seed[j]) for j in range(len(seeds))]:
            x = V[scope]
            for side, bs in (("fn", AT.FN_B), ("fp", AT.FP_B)):
                for b in bs:
                    brow.append("\t".join([scope, sd, f"{side}_{b}", f"{x[f'{side}_{b}']:.1f}",
                                           fmt(AT.ratio(x[f'{side}_{b}'], x[side]), 4),
                                           fmt(AT.ratio(x[f'{side}_{b}'], x['fn'] + x['fp']), 4)]))
    w1read.write_once(out / "buckets.tsv", "\n".join(brow) + "\n")
    if control:
        crow = ["stem\tgt_crack_px_v1\tcrack_softmin"] + [f"{s}\t{v_[0]}\t{fmt(v_[1], 6)}"
                                                          for s, v_ in sorted(control["scores"].items())]
        w1read.write_once(out / "control_crack_softmin.tsv", "\n".join(crow) + "\n")
    if published:
        ik = ["stem", "class", "type", "px", "score", "seeds_agreeing"]
        w1read.write_once(out / "label_issues_t10.tsv", "\n".join(["\t".join(ik)] + [
            "\t".join(str(r[k]) for k in ik) for r in issues]) + "\n")
    print(text, flush=True)
    print(f"[atlas] DONE {time.time() - t0:.0f} s -> {out}", flush=True)


if __name__ == "__main__":
    main()
