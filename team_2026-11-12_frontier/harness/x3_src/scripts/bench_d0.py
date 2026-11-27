"""elbench x3: D0 placement diagnostic on out-of-fold dumps (bench/placement.py). Per arm, per seed and pooled over
seeds: (a) share of predicted crack skeleton points within 1 px of the dark ridge (visible dip only) beside the same share
for the GT labels, (b) strict crack IoU against original labels (and snapped labels with --snapped DIR), (c) mean p_crack
against signed distance from the ridge (positive = toward the label), all cells with GT crack, per source.
The fixed reading (WAVE2_REVIEW X5) is printed for the pooled prediction share.

  python scripts/bench_d0.py --arm PF=<method dir>:<regex> --labels v11 --out DIR [--cache DIR] [--snapped DIR]
CPU only; nice -n 19, CUDA_VISIBLE_DEVICES="", <= 8 workers. Refuses to overwrite <out>/d0.{json,txt}.
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
from bench import sets, w1read  # noqa: E402
from bench.placement import aggregate, reading  # noqa: E402
from bench.w1read import _cache, _key, fmt  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
from bench_src_calib import _np, common_args, setup  # noqa: E402


def d0_run(pool, cache: Path, r, snapped: str | None) -> dict:
    p = _cache(cache, r, "d0", _key(r.manifest_md5, r.gt, snapped, "d0v1")).with_suffix(".json")
    if p.exists():
        return json.loads(p.read_text())
    images = str(sets.resolve(r.set_name)["images"])
    jobs = [(str(r.set_dir), s, r.gt, "d0", {"images": images, "stem": s, "snapped": snapped}) for s in r.stems]
    doc = dict(zip(r.stems, pool.map(jobs)))
    p.write_text(json.dumps(doc))
    return doc


def main() -> None:
    ap = argparse.ArgumentParser()
    common_args(ap)
    ap.add_argument("--snapped", default=None, help="folder of snapped held-out masks (<stem>.png), optional")
    a = ap.parse_args()
    t0 = time.time()
    out, cache, runs, groups, arms, fold_of, stems, notes = setup(a, ("d0.json", "d0.txt"))
    pool = w1read.Pool(a.workers)
    srcs = sorted({s.split("_")[0] for s in stems})
    subs = {"all": lambda s: True} | {f"src:{so}": (lambda s, so=so: s.split("_")[0] == so) for so in srcs}
    keep = set(stems)
    res = {"tool": "bench_d0.py", "tool_md5": w1read.dumpfmt.md5_file(__file__), "labels": a.labels,
           "n_stems": len(stems), "notes": notes, "snapped": a.snapped, "arms": {}}
    for arm, by in arms.items():
        per_seed, pooled = {}, {}
        for sd, rs in by.items():
            cells = {}
            for r in rs:
                cells.update({s: v for s, v in d0_run(pool, cache, r, a.snapped).items() if s in keep})
            per_seed[sd] = {sn: aggregate(cells, f) for sn, f in subs.items()}
            for s, v in cells.items():
                pooled[f"{sd}|{s}"] = v
        allp = {sn: aggregate(pooled, (lambda k, f=f: f(k.split("|", 1)[1]))) for sn, f in subs.items()}
        res["arms"][arm] = {"seeds": sorted(by), "per_seed": per_seed, "pooled_over_seeds": allp,
                            "reading": reading(allp["all"].get("pred_share_le1", float("nan")))}
        print(f"[{time.time() - t0:.0f}s] d0 arm {arm}: {len(by)} seeds", flush=True)
    pool.close()
    res["seconds"] = round(time.time() - t0)
    w1read.write_once(out / "d0.json", json.dumps(res, indent=1, default=_np))
    w1read.write_once(out / "d0.txt", report(res))
    print(f"d0 done -> {out / 'd0.txt'}", flush=True)


def report(res: dict) -> str:
    L = [f"# D0 placement ({res['tool']} {res['tool_md5'][:8]}); labels {res['labels']}; {res['n_stems']} OOF stems; "
         f"snapped labels: {res['snapped'] or 'none (b) only against original labels'}"]
    L += [f"NOTE {n}" for n in res["notes"]]
    for arm, d in res["arms"].items():
        L.append(f"\n## arm {arm} (seeds {d['seeds']}); reading of the pooled prediction share: {d['reading']}")
        L.append("scope\tsubset\tcells\tpred share<=1px\tGT share<=1px\tpred <=0.5\tGT <=0.5\tpred pts vis\tGT pts vis\t"
                 "IoU orig\tIoU snapped\tp@ridge\tp@label")
        rows = [("pooled", d["pooled_over_seeds"])] + [(f"s{sd}", v) for sd, v in d["per_seed"].items()]
        for scope, t in rows:
            for sn, g in t.items():
                if not g.get("n_cells"):
                    continue
                L.append(f"{scope}\t{sn}\t{g['n_cells']}\t{fmt(g['pred_share_le1'])}\t{fmt(g['gt_share_le1'])}\t"
                         f"{fmt(g['pred_share_le05'])}\t{fmt(g['gt_share_le05'])}\t{g['pred_visible']}\t{g['gt_visible']}\t"
                         f"{fmt(g['iou_orig'])}\t{fmt(g.get('iou_snapped'))}\t{fmt(g['p_at_ridge'])}\t{fmt(g['p_at_label'])}")
        g = d["pooled_over_seeds"]["all"]
        if g.get("n_cells"):
            L.append("mean p_crack by signed distance from the ridge (px; + = toward the label; GT points with the ridge "
                     f">= 1 px off, n = {g['prof_n']}):")
            L.append("  " + "  ".join(f"{x:+.1f}:{y:.3f}" for x, y in zip(g["prof_d"], g["prof_mean_pcrack"])))
    L.append("\nReading (fixed, WAVE2_REVIEW X5): pred share >= 0.75 on ridge; <= 0.60 follows the jitter or is blurred; "
             "in between the lead decides. D0 orders the placement arms; it closes none.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
