"""elbench x3: src_calib (T4 arm 1) on out-of-fold dumps; a 'uses source metadata' row with its own interval.
Variants and fit rules: bench/postproc/src_calib.py. Cross-fitting per seed on the other folds (bench/crossfit_op.py).
Reports per arm: guards at argmax / glob_bias / src_bias / src_morph (all cells, per source); per-source width table
(GT mean width, predicted mean width and width ratio at argmax and src_bias); b_src per fold and its spread (> 1.0 logit =
unstable); paired two-stage bootstrap of src_bias - glob_bias (primary), src_morph - argmax, glob_bias - argmax, and the
per-source src_bias - glob_bias for sources with >= 40 cells; the T4 pass / gate flags.

  python scripts/bench_src_calib.py --arm PF=<method dir>:<regex> [--arm HOUSE=...] --labels v11 --out DIR [--cache DIR]
CPU only; nice -n 19, CUDA_VISIBLE_DEVICES="", <= 8 workers. Refuses to overwrite <out>/src_calib.{json,txt}.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import cellmeta, w1read  # noqa: E402
from bench.crossfit_op import boot_pair, cname, guards  # noqa: E402
from bench.postproc import src_calib as SC  # noqa: E402
from bench.w1read import fmt, rkey  # noqa: E402

VARIANTS = ("argmax", "glob_bias", "src_bias", "src_morph")
M_SRC = 0.03        # T4 provisional M_src (strict crack IoU on one source with >= 40 pool cells); the lead's M replaces it


def common_args(ap):
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--runs-tsv", default=None)
    ap.add_argument("--labels", default="v11", choices=cellmeta.LABEL_SETS)
    ap.add_argument("--groups", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--pseudo-folds", type=int, default=0)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--dry", action="store_true")


def setup(a, outs: tuple):
    out = Path(a.out)
    for f in outs:
        if (out / f).exists():
            sys.exit(f"refuse: {out / f} exists")
    runs = w1read.runs_from_tsv(a.runs_tsv, a.labels) if a.runs_tsv else w1read.discover(a.arm, a.labels)
    w1read.check_comparable(runs, a.dry)
    groups = cellmeta.load_groups(a.groups)
    arms, fold_of, stems, notes = w1read.assemble(runs, groups, a.pseudo_folds, a.allow_partial)
    return out, Path(a.cache) if a.cache else out, runs, groups, arms, fold_of, stems, notes


def main() -> None:
    ap = argparse.ArgumentParser()
    common_args(ap)
    a = ap.parse_args()
    t0 = time.time()
    out, cache, runs, groups, arms, fold_of, stems, notes = setup(a, ("src_calib.json", "src_calib.txt"))
    pool = w1read.Pool(a.workers)
    cl = SC.cands()
    folds = np.array([fold_of[s] for s in stems])
    srcs = sorted({SC.src_of(s) for s in stems})
    res = {"tool": "bench_src_calib.py", "tool_md5": w1read.dumpfmt.md5_file(__file__), "labels": a.labels,
           "n_stems": len(stems), "notes": notes, "row_label": "src_calib (uses source metadata)", "arms": {}}
    for arm, by in arms.items():
        cnt, rec = {}, {}
        for r in [r for rs in by.values() for r in rs]:
            cnt[rkey(r)] = w1read.sweep(pool, cache, r, cl, "src")
        R = {v: {} for v in VARIANTS}
        fits = {}
        for sd, rs in by.items():
            C = w1read.oof_counts(cnt, rs, stems)
            ch = SC.fit(C, stems, folds, cl)
            fits[sd] = {"glob_bias": {k: cname(cl[i]) for k, i in ch["glob_bias"].items()},
                        "src_bias": {k: {s: cname(cl[i]) for s, i in d.items()} for k, d in ch["src_bias"].items()},
                        "src_morph": {k: {s: cname(cl[i]) for s, i in d.items()} for k, d in ch["src_morph"].items()},
                        "n_crack": ch["n_crack"], "fallback": ch["fallback"], "fa_refused": ch["fa_refused"]}
            for v in VARIANTS:
                rr = {}
                for r in rs:
                    fr = np.array([fold_of.get(s, -1) for s in r.stems])
                    per = [c if s in fold_of else ("argmax",) for s, c in
                           zip(r.stems, SC.choice_per_cell(ch, v, r.stems, np.where(fr < 0, 0, fr), cl))]
                    rr[rkey(r)] = w1read.records(pool, cache, r, ("argmax",) if v == "argmax" else per,
                                                 "argmax" if v == "argmax" else f"src_{v}")
                R[v][sd] = w1read.oof_records(rr, rs, stems)
        # stability of b_src: spread over folds per seed and source
        spread = {}
        for sd, f in fits.items():
            for s in srcs:
                bs = [float(f["src_bias"][k][s][1:]) for k in f["src_bias"] if f["src_bias"][k][s].startswith("b")]
                spread.setdefault(s, []).append(max(bs) - min(bs) if bs else float("nan"))
        subs = {"all": lambda s: True} | {f"src:{so}": (lambda s, so=so: SC.src_of(s) == so) for so in srcs}
        tab = {v: {sn: _mean_over_seeds([guards(R[v][sd], f) for sd in R[v]]) for sn, f in subs.items()} for v in VARIANTS}
        gtw = {}
        for sn, f in subs.items():
            c0 = next(iter(R["argmax"].values()))
            gp = sum(np.asarray(c0[s]["conf"]).reshape(24, 24)[14].sum() for s in stems if f(s))
            gsk = sum(c0[s]["crack_skel"][1] for s in stems if f(s))
            gtw[sn] = float(gp / gsk) if gsk else float("nan")
        con = {}
        for A, B in (("glob_bias", "src_bias"), ("argmax", "src_morph"), ("argmax", "glob_bias")):
            con[f"{B} - {A}"] = boot_pair(R[A], R[B], stems, fold_of, groups, a.boot, paired_seeds=True)
        n_src = {s: sum(1 for x in stems if SC.src_of(x) == s) for s in srcs}
        con_src = {}
        for s in srcs:
            if n_src[s] >= 40:
                st = [x for x in stems if SC.src_of(x) == s]
                con_src[s] = boot_pair(R["glob_bias"], R["src_bias"], st, fold_of, groups, a.boot, paired_seeds=True)
        big = [s for s in srcs if n_src[s] >= 40]
        wr_a = {s: tab["argmax"][f"src:{s}"]["width_ratio"] for s in big}
        wr_s = {s: tab["src_bias"][f"src:{s}"]["width_ratio"] for s in big}
        flags = {"implicit_conditioning_present": all(w is not None and 0.9 <= w <= 1.1 for w in wr_a.values()),
                 "src_film_gate_width_unrepaired": [s for s in big if wr_a[s] is not None and not 0.85 <= wr_a[s] <= 1.15
                                                    and (wr_s[s] is None or not 0.85 <= wr_s[s] <= 1.15)]}
        p = con["src_bias - glob_bias"]["metrics"]["crack_iou"]
        src_pass = [s for s, b in con_src.items() if b["metrics"]["crack_iou"]["delta"] >= M_SRC
                    and b["metrics"]["crack_iou"]["lo"] > 0 and b["metrics"]["relP2"]["delta"] >= -0.03]
        flags["pass_src_branch_provisional"] = src_pass
        flags["primary_ci_above_0"] = p["lo"] > 0
        res["arms"][arm] = {"seeds": sorted(by), "fits": fits, "b_src_spread": spread, "unstable": [
            s for s, v in spread.items() if any(x > 1.0 for x in v if np.isfinite(x))], "table": tab, "gt_mean_width": gtw,
            "contrasts": con, "contrasts_per_source": con_src, "flags": flags, "n_src": n_src}
        print(f"[{time.time() - t0:.0f}s] src_calib arm {arm}: {len(by)} seeds", flush=True)
    pool.close()
    res["seconds"] = round(time.time() - t0)
    w1read.write_once(out / "src_calib.json", json.dumps(res, indent=1, default=_np))
    w1read.write_once(out / "src_calib.txt", report(res))
    print(f"src_calib done -> {out / 'src_calib.txt'}", flush=True)


def _np(x):
    return x.item() if isinstance(x, np.generic) else None


def _mean_over_seeds(gs: list[dict]) -> dict:
    keys = ("n", "crack_iou", "relF1_2", "relF1_1", "relP2", "relR2", "width_ratio", "mean_width", "fa_px", "fa_share50",
            "cc_rec50_20", "cc_prec_20", "inact_iou", "miou_rob")
    out = {}
    for k in keys:
        v = [g.get(k) for g in gs if g.get(k) is not None and np.isfinite(g.get(k))]
        out[k] = float(np.mean(v)) if v else None
    return out


def report(res: dict) -> str:
    L = [f"# {res['row_label']} ({res['tool']} {res['tool_md5'][:8]}); labels {res['labels']}; {res['n_stems']} OOF stems"]
    L += [f"NOTE {n}" for n in res["notes"]]
    keys = ("crack_iou", "relF1_2", "relF1_1", "relP2", "relR2", "width_ratio", "mean_width", "fa_px", "fa_share50",
            "inact_iou", "miou_rob")
    for arm, d in res["arms"].items():
        L.append(f"\n## arm {arm} (seeds {d['seeds']}), mean over seeds; uses source metadata for src_* rows")
        L.append("variant\tsubset\tn\t" + "\t".join(keys))
        for v, t in d["table"].items():
            for sn, g in t.items():
                L.append(f"{v}\t{sn}\t{g['n']}\t" + "\t".join(fmt(g[k]) for k in keys))
        L.append("width table: subset\tGT mean width\tpred mean width argmax\tsrc_bias\twidth ratio argmax\tsrc_bias")
        for sn, w in d["gt_mean_width"].items():
            L.append(f"  {sn}\t{fmt(w)}\t{fmt(d['table']['argmax'][sn]['mean_width'])}\t{fmt(d['table']['src_bias'][sn]['mean_width'])}"
                     f"\t{fmt(d['table']['argmax'][sn]['width_ratio'])}\t{fmt(d['table']['src_bias'][sn]['width_ratio'])}")
        for sd, f in d["fits"].items():
            L.append(f"fits s{sd}: glob {f['glob_bias']}; fallback {f['fallback']}; FA-refused {f['fa_refused']}")
            for k, m in f["src_bias"].items():
                L.append(f"  fold {k}: src_bias {m}; src_morph {f['src_morph'][k]}; crack cells in fit {f['n_crack'][k]}")
        L.append(f"b_src spread over folds (per seed): {d['b_src_spread']}; unstable (> 1.0): {d['unstable']}")
        L.append("contrasts (paired seeds), delta [95% CI]:")
        for name, b in list(d["contrasts"].items()) + [(f"src_bias - glob_bias [{s}]", b) for s, b in
                                                       d["contrasts_per_source"].items()]:
            L.append("  " + name + "\t" + "\t".join(
                f"{k} {fmt(b['metrics'][k]['delta'])} [{fmt(b['metrics'][k]['lo'])}, {fmt(b['metrics'][k]['hi'])}]"
                for k in ("crack_iou", "relF1_2", "relP2", "relR2", "width_ratio")))
        L.append(f"flags: {d['flags']} (M_src provisional {M_SRC}; primary = src_bias - glob_bias strict crack IoU >= M with "
                 f"CI above 0)")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
