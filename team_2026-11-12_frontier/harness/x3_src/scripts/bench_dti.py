"""elbench x3: dti_hysteresis (T5 arm 1) on out-of-fold dumps. Hysteresis on the crack margin (bench/postproc/hysteresis.py;
60 (t_hi, t_lo) pairs). Per seed and held-out fold, the pair maximising pooled relF1@2 on the other folds is applied to the
fold. Comparators, chosen the same way on the same fit cells: OP-F (bench/crossfit_op.py: bias with the relP@2 guard;
the review's primary comparator) and the unguarded bias point. Printed beside relF1@2: relF1@1, strict IoU, width ratio,
mean width, relP@2 / relR@2, component recall (50% and any-hit) and precision, crack-free false alarms.
Width guard: DTI width ratio <= 1.15 x OP-F's. Frontier (all OOF cells): best relR@2 among candidates with relP@2 >= P,
for P = 0.90 and P = the arm's argmax relP@2, over the DTI grid and over the bias grid.

  python scripts/bench_dti.py --arm PF=<method dir>:<regex> --labels v11 --out DIR [--cache DIR]
CPU only; nice -n 19, CUDA_VISIBLE_DEVICES="", <= 8 workers. Refuses to overwrite <out>/dti.{json,txt}.
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
from bench import w1read  # noqa: E402
from bench.crossfit_op import OPF_RELP_DROP, bias_cands, boot_pair, cmetrics, cname, crossfit, guards  # noqa: E402
from bench.postproc import hysteresis as H  # noqa: E402
from bench.w1read import fmt, rkey  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from bench_src_calib import _mean_over_seeds, _np, common_args, setup  # noqa: E402

WIDTH_GUARD = 1.15


def best_r_at_p(pooled: np.ndarray, p_min: float) -> float:
    v = [cmetrics(r) for r in pooled]
    ok = [m["relR2"] for m in v if m["relP2"] >= p_min]
    return float(max(ok)) if ok else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    common_args(ap)
    a = ap.parse_args()
    t0 = time.time()
    out, cache, runs, groups, arms, fold_of, stems, notes = setup(a, ("dti.json", "dti.txt"))
    pool = w1read.Pool(a.workers)
    bc = bias_cands()
    dc = [("argmax",)] + H.grid()
    folds = np.array([fold_of[s] for s in stems])
    res = {"tool": "bench_dti.py", "tool_md5": w1read.dumpfmt.md5_file(__file__), "labels": a.labels,
           "n_stems": len(stems), "notes": notes, "grid_pairs": len(dc) - 1, "arms": {}}
    for arm, by in arms.items():
        cb, cd = {}, {}
        for r in [r for rs in by.values() for r in rs]:
            cb[rkey(r)] = w1read.sweep(pool, cache, r, bc, "op")
            cd[rkey(r)] = w1read.sweep(pool, cache, r, dc, "dti")
        R = {v: {} for v in ("argmax", "OP-F", "bias_F", "DTI")}
        chosen, front = {}, {}
        for sd, rs in by.items():
            Cb, Cd = w1read.oof_counts(cb, rs, stems), w1read.oof_counts(cd, rs, stems)
            ch = {"OP-F": (bc, crossfit(Cb, folds, bc, "relF1_2", relp_guard=OPF_RELP_DROP)),
                  "bias_F": (bc, crossfit(Cb, folds, bc, "relF1_2")),
                  "DTI": (dc, crossfit(Cd, folds, dc, "relF1_2"))}
            chosen[sd] = {v: {k: cname(cl[i]) for k, i in c.items()} for v, (cl, c) in ch.items()}
            tag = {"OP-F": "opF", "bias_F": "biasF", "DTI": "dti"}
            for v in R:
                rr = {}
                for r in rs:
                    if v == "argmax":
                        rr[rkey(r)] = w1read.records(pool, cache, r, ("argmax",), "argmax")
                    else:
                        cl, c = ch[v]
                        rr[rkey(r)] = w1read.records(pool, cache, r, w1read.per_cell_choice(r, fold_of, c, cl), tag[v])
                R[v][sd] = w1read.oof_records(rr, rs, stems)
            pa = cmetrics(Cb.sum(0)[0])["relP2"]
            front[sd] = {"argmax_relP2": pa,
                         **{f"{g}_relR2_at_P{lab}": best_r_at_p(C.sum(0)[1:], p) for g, C in (("dti", Cd), ("bias", Cb))
                            for lab, p in (("0.90", 0.90), ("argmax", pa))},
                         "dti_best_tlo_per_thi": {th: max(((cname(c), cmetrics(row)) for c, row in zip(dc[1:], Cd.sum(0)[1:])
                                                           if c[1] == th), key=lambda x: x[1]["relF1_2"])[0]
                                                  for th in H.T_HI}}
        tab = {v: _mean_over_seeds([guards(R[v][sd]) for sd in R[v]]) for v in R}
        con = {f"DTI - {c}": boot_pair(R[c], R["DTI"], stems, fold_of, groups, a.boot, paired_seeds=True)
               for c in ("OP-F", "bias_F", "argmax")}
        wF, wD = tab["OP-F"]["width_ratio"], tab["DTI"]["width_ratio"]
        res["arms"][arm] = {"seeds": sorted(by), "chosen": chosen, "table": tab, "contrasts": con, "frontier": front,
                            "width_guard": {"dti": wD, "op_f": wF, "limit_x": WIDTH_GUARD,
                                            "ok": None if wF is None or wD is None else wD <= WIDTH_GUARD * wF}}
        print(f"[{time.time() - t0:.0f}s] dti arm {arm}: {len(by)} seeds", flush=True)
    pool.close()
    res["seconds"] = round(time.time() - t0)
    w1read.write_once(out / "dti.json", json.dumps(res, indent=1, default=_np))
    w1read.write_once(out / "dti.txt", report(res))
    print(f"dti done -> {out / 'dti.txt'}", flush=True)


def report(res: dict) -> str:
    L = [f"# dti_hysteresis ({res['tool']} {res['tool_md5'][:8]}); labels {res['labels']}; {res['n_stems']} OOF stems; "
         f"{res['grid_pairs']} pairs"]
    L += [f"NOTE {n}" for n in res["notes"]]
    keys = ("relF1_2", "relF1_1", "crack_iou", "relP2", "relR2", "width_ratio", "mean_width", "cc_rec50_20",
            "cc_prec_20", "fa_px", "fa_share50", "miou_rob")
    for arm, d in res["arms"].items():
        L.append(f"\n## arm {arm} (seeds {d['seeds']}), mean over seeds")
        L.append("point\t" + "\t".join(keys))
        for v, g in d["table"].items():
            L.append(f"{v}\t" + "\t".join(fmt(g[k]) for k in keys))
        L.append(f"width guard (DTI <= {d['width_guard']['limit_x']} x OP-F): DTI {fmt(d['width_guard']['dti'])}, "
                 f"OP-F {fmt(d['width_guard']['op_f'])}, ok {d['width_guard']['ok']}")
        for name, b in d["contrasts"].items():
            L.append(f"{name}\t" + "\t".join(
                f"{k} {fmt(b['metrics'][k]['delta'])} [{fmt(b['metrics'][k]['lo'])}, {fmt(b['metrics'][k]['hi'])}]"
                for k in ("relF1_2", "relF1_1", "crack_iou", "relP2", "relR2", "width_ratio")))
        for sd, c in d["chosen"].items():
            L.append(f"chosen s{sd}: {c}")
        for sd, f in d["frontier"].items():
            L.append(f"frontier s{sd}: " + ", ".join(f"{k} {fmt(v) if not isinstance(v, dict) else v}" for k, v in f.items()))
    L.append("\nPrimary: relF1@2 of DTI against OP-F at the cross-fitted point (drop if below M_F, or the frontier gain at "
             "relP@2 0.90 and at the argmax relP@2 is below 0.01, or the width ratio exceeds 1.15).")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
