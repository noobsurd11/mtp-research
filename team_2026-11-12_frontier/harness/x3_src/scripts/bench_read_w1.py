"""elbench x3: the wave 1 read. Pooled out-of-fold (OOF) metrics per arm at the three shared operating points
(bench/crossfit_op.py: OP-A argmax, OP-F cross-fitted relF1@2 bias with the relP@2 guard, OP-W cross-fitted width match to
the baseline), the guards of WAVE2_REVIEW section 5, per-source and cells.tsv subsets, the frontier read, paired two-stage
group bootstrap per arm contrast, and the A/A null (seeds {5,6} against {7,8} of one arm) with the pass margin
M(metric) = max(0.01, 2 x SE of the A/A difference).

CPU only (numpy, scipy). Run with nice -n 19, CUDA_VISIBLE_DEVICES="", at most 8 workers. Inputs are dumps of open
cv5v2 held-out folds only; sealed sets are refused by bench/w1read.py.

  python scripts/bench_read_w1.py --arm PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:'w1g_pf_v11_f[0-4]_s[0-9]+' \
      --baseline PF --labels v11 --out /home/noob/work/bench_reads/w1g_read --workers 8
Dry test (one dump, pseudo folds, the same dump as several seeds): --runs-tsv RUNS.tsv --pseudo-folds 5 --dry.
Outputs (refuses to overwrite): <out>/read.json, <out>/read.txt; caches in <out>/cache/.
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
from bench.crossfit_op import (BOOT_KEYS, GUARD_KEYS, HEADLINE, bias_cands, boot_pair, cmetrics, cname,  # noqa: E402
                               frontier, guards, margins, operating_points, width_from_records)
from bench.w1read import fmt, rkey  # noqa: E402

OPS = ("OP-A", "OP-F", "OP-W")


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[], help="NAME=<method dir>:<run_id regex> (repeat)")
    ap.add_argument("--runs-tsv", default=None, help="dry tests: arm<TAB>seed<TAB>set dir")
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--pair", action="append", default=[], help="A=B: contrast B - A (default: baseline = every other arm)")
    ap.add_argument("--aa", default=None, help="ARM:5,6:7,8 (default: baseline:5,6:7,8 when those seeds exist)")
    ap.add_argument("--labels", default="v11", choices=cellmeta.LABEL_SETS)
    ap.add_argument("--groups", default=None)
    ap.add_argument("--cells-tsv", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default=None, help="cache root shared by the x3 tools (default: --out)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--pseudo-folds", type=int, default=0)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--dry", action="store_true", help="dry test: allows non-cv5v2 sets and mixed precision")
    return ap.parse_args()


def load_all(a, out: Path):
    runs = w1read.runs_from_tsv(a.runs_tsv, a.labels) if a.runs_tsv else w1read.discover(a.arm, a.labels)
    w1read.check_comparable(runs, a.dry)
    groups = cellmeta.load_groups(a.groups)
    arms, fold_of, stems, notes = w1read.assemble(runs, groups, a.pseudo_folds, a.allow_partial)
    assert a.baseline in arms, f"baseline {a.baseline} not among arms {list(arms)}"
    return runs, groups, arms, fold_of, stems, notes


def main() -> None:
    a = parse()
    t0 = time.time()
    out = Path(a.out)
    for f in ("read.json", "read.txt"):
        if (out / f).exists():
            sys.exit(f"refuse: {out / f} exists")
    runs, groups, arms, fold_of, stems, notes = load_all(a, out)
    cells_meta = cellmeta.load_cells(a.cells_tsv)
    pool = w1read.Pool(a.workers)
    cache = Path(a.cache) if a.cache else out
    cands = bias_cands()
    recA, cnt = {}, {}
    for r in runs:
        recA[rkey(r)] = w1read.records(pool, cache, r, ("argmax",), "argmax")
        cnt[rkey(r)] = w1read.sweep(pool, cache, r, cands, "op")
    print(f"[{time.time() - t0:.0f}s] argmax records + bias sweeps: {len(runs)} runs", flush=True)
    # baseline argmax width ratio on each fold's fit cells (same seed; else the mean over the baseline's seeds)
    base = arms[a.baseline]
    bw = {sd: {k: width_from_records(w1read.oof_records(recA, rs, stems), [s for s in stems if fold_of[s] != k])
               for k in sorted(set(fold_of[s] for s in stems))} for sd, rs in base.items()}
    bw_mean = {k: float(np.mean([bw[sd][k] for sd in bw])) for k in next(iter(bw.values()))}
    folds = np.array([fold_of[s] for s in stems])
    choices, recs, curves = {}, {}, {}
    for arm, by in arms.items():
        for sd, rs in by.items():
            C = w1read.oof_counts(cnt, rs, stems)
            ops = operating_points(C, folds, cands, bw.get(sd, bw_mean) if arm != a.baseline else bw[sd])
            choices[(arm, sd)] = {op: {k: cname(cands[i]) for k, i in ch.items()} for op, ch in ops.items()}
            curves[(arm, sd)] = C.sum(0)
            for op, ch in ops.items():
                rr = {}
                for r in rs:
                    tag = {"OP-A": "argmax", "OP-F": "opF", "OP-W": "opW"}[op]
                    rr[rkey(r)] = recA[rkey(r)] if op == "OP-A" else \
                        w1read.records(pool, cache, r, w1read.per_cell_choice(r, fold_of, ch, cands), tag)
                recs[(arm, op, sd)] = w1read.oof_records(rr, rs, stems)
    pool.close()
    print(f"[{time.time() - t0:.0f}s] operating points and their records", flush=True)
    # ---- tables
    subs = {"all": lambda s: True}
    for so in sorted({s.split("_")[0] for s in stems}):
        subs[f"src:{so}"] = lambda s, so=so: s.split("_")[0] == so
    subs.update({k: v for k, v in cellmeta.subsets(stems, cells_meta).items() if not k.startswith("src:")})
    table = {}
    for (arm, op, sd), cells in recs.items():
        for sn, f in subs.items():
            g = guards(cells, f)
            table.setdefault(arm, {}).setdefault(op, {}).setdefault(sn, {})[sd] = \
                {k: g.get(k) for k in ("n",) + GUARD_KEYS}
    summ = {arm: {op: {sn: {k: _ms([v[k] for v in per.values()]) for k in GUARD_KEYS} | {"n": next(iter(per.values()))["n"]}
                       for sn, per in d2.items()} for op, d2 in d1.items()} for arm, d1 in table.items()}
    # ---- frontier (descriptive): each arm's bias curve against the baseline's argmax relP@2 / relR@2, same seed or mean
    fr = {}
    for (arm, sd), cv in curves.items():
        bsd = sd if sd in base else None
        refs = [curves[(a.baseline, x)][0] for x in ([bsd] if bsd is not None else base)]
        rp = float(np.mean([cmetrics(x)["relP2"] for x in refs])); rr_ = float(np.mean([cmetrics(x)["relR2"] for x in refs]))
        fr.setdefault(arm, {})[sd] = frontier(cv, cands, rp, rr_)
    # ---- contrasts
    pairs = a.pair or [f"{a.baseline}={x}" for x in arms if x != a.baseline]
    contrasts = {}
    for spec in pairs:
        A, B = spec.split("=", 1)
        for op in OPS:
            contrasts.setdefault(f"{B} - {A}", {})[op] = boot_pair(
                {sd: recs[(A, op, sd)] for sd in arms[A]}, {sd: recs[(B, op, sd)] for sd in arms[B]},
                stems, fold_of, groups, a.boot)
    aa, M = None, None
    aa_spec = a.aa or f"{a.baseline}:5,6:7,8"
    arm_aa, s1, s2 = aa_spec.split(":")
    s1 = [int(x) for x in s1.split(",")]; s2 = [int(x) for x in s2.split(",")]
    if arm_aa in arms and set(s1 + s2) <= set(arms[arm_aa]):
        aa = {op: boot_pair({sd: recs[(arm_aa, op, sd)] for sd in s1}, {sd: recs[(arm_aa, op, sd)] for sd in s2},
                            stems, fold_of, groups, a.boot) for op in OPS}
        M = margins(aa["OP-A"])
    else:
        notes.append(f"A/A {aa_spec}: seeds missing (have {sorted(arms.get(arm_aa, {}))}); no margin M from this read")
    doc = {"tool": "bench_read_w1.py", "tool_md5": w1read.dumpfmt.md5_file(__file__), "labels": a.labels,
           "n_stems": len(stems), "folds": sorted(set(fold_of.values())), "pseudo_folds": a.pseudo_folds, "dry": a.dry,
           "notes": notes, "runs": [{"arm": r.arm, "seed": r.seed, "run_id": r.run_id, "set": r.set_name, "fold": r.fold,
                                    "manifest_md5": r.manifest_md5, "precision": r.manifest["precision"],
                                    "device": r.manifest["device"], "code_commit": r.manifest["code_commit"]} for r in runs],
           "choices": {f"{arm}|{sd}": ch for (arm, sd), ch in choices.items()}, "summary": summ, "per_seed": table,
           "frontier": fr, "contrasts": contrasts, "aa": aa, "M": M, "aa_spec": aa_spec,
           "groups_md5": cellmeta.md5(a.groups or cellmeta.GROUPS_TSV), "seconds": round(time.time() - t0)}
    w1read.write_once(out / "read.json", json.dumps(doc, indent=1, default=_nan))
    w1read.write_once(out / "read.txt", report(doc, a.baseline))
    print(f"[{time.time() - t0:.0f}s] wave 1 read: {len(arms)} arms, {len(stems)} OOF stems, {len(contrasts)} contrasts, "
          f"A/A {'yes' if aa else 'no'} -> {out / 'read.txt'}", flush=True)


def _nan(x):
    return x.item() if isinstance(x, np.generic) else None


def _ms(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    if not v:
        return {"mean": None, "sd": None, "n": 0}
    return {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)) if len(v) > 1 else 0.0, "n": len(v)}


def report(doc: dict, baseline: str) -> str:
    L = [f"# wave 1 read ({doc['tool']} {doc['tool_md5'][:8]}); labels {doc['labels']}; {doc['n_stems']} OOF stems; "
         f"folds {doc['folds']}{' (pseudo)' if doc['pseudo_folds'] else ''}; baseline {baseline}"]
    L += [f"NOTE {n}" for n in doc["notes"]]
    keys = ("crack_iou", "relF1_2", "inact_iou", "miou_rob", "relP2", "relR2", "relF1_1", "width_ratio", "mean_width",
            "fa_share50", "fa_px", "cc_rec50_20", "cc_recany_20", "cc_prec_20", "inact_prec", "inact_rec", "in_cc_prec")
    L.append("\n## headline and guards, mean (sd) over seeds, all OOF cells")
    L.append("arm\top\tseeds\t" + "\t".join(keys))
    for arm, d in doc["summary"].items():
        for op, d2 in d.items():
            g = d2["all"]
            L.append(f"{arm}\t{op}\t{g['crack_iou']['n']}\t" + "\t".join(
                f"{fmt(g[k]['mean'])} ({fmt(g[k]['sd'], 3)})" if k in g else "n/a" for k in keys))
    L.append("\n## per source and cells.tsv subsets (OP-A and OP-W): crack IoU, relF1@2, relP@2, relR@2, width, FA share50")
    for arm, d in doc["summary"].items():
        for op in ("OP-A", "OP-W"):
            for sn, g in d[op].items():
                if sn == "all":
                    continue
                L.append(f"{arm}\t{op}\t{sn}\tn={g['n']}\t" + "\t".join(
                    fmt(g[k]["mean"]) for k in ("crack_iou", "relF1_2", "relP2", "relR2", "width_ratio", "fa_share50")))
    L.append("\n## cross-fitted choices (per seed: fold -> candidate)")
    for k, ch in doc["choices"].items():
        L.append(f"{k}\tOP-F {ch['OP-F']}\tOP-W {ch['OP-W']}")
    L.append("\n## frontier (bias curve, all OOF cells): relR@2 at the baseline's argmax relP@2 / relP@2 at its relR@2")
    for arm, d in doc["frontier"].items():
        for sd, f in d.items():
            L.append(f"{arm}\ts{sd}\t{fmt(f['relR2_at_ref_relP2'])} @P {fmt(f['ref_relP2'])}\t"
                     f"{fmt(f['relP2_at_ref_relR2'])} @R {fmt(f['ref_relR2'])}")
    M = doc["M"]
    if doc["aa"]:
        L.append(f"\n## A/A null {doc['aa_spec']} (two-stage group bootstrap): delta [95% CI] SE; M = max(0.01, 2 SE) at OP-A")
        for op, b in doc["aa"].items():
            for k in BOOT_KEYS:
                v = b["metrics"][k]
                L.append(f"AA\t{op}\t{k}\t{fmt(v['delta'])} [{fmt(v['lo'])}, {fmt(v['hi'])}] SE {fmt(v['se'])}"
                         + (f"\tM {fmt(M[k])}" if op == "OP-A" else ""))
    L.append("\n## contrasts (B - A), two-stage group bootstrap 95% CI" + ("; PASS* = delta >= M and CI low > 0" if M else
                                                                       "; no M yet (A/A seeds missing)"))
    for name, d in doc["contrasts"].items():
        for op, b in d.items():
            for k in HEADLINE + ("relF1_1", "width_ratio", "relP2", "relR2"):
                v = b["metrics"][k]
                tag = ""
                if M and k in HEADLINE and M.get(k) is not None:
                    tag = "\tPASS*" if v["delta"] >= M[k] and v["lo"] > 0 else ""
                L.append(f"{name}\t{op}\t{k}\t{fmt(v['delta'])} [{fmt(v['lo'])}, {fmt(v['hi'])}]{tag}")
    L.append("\nRules (WAVE2_REVIEW X3, X4): a crack gain counts only if present at OP-A and OP-W; width ratio must stay "
             "within 0.85 to 1.15 x the baseline's, pooled and per source with >= 40 cells. PASS* is a screen flag, not a result.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
