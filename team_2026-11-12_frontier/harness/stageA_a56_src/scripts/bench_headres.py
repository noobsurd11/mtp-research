"""elbench stage A5: head_res_ceiling (T11 spec A0 + wave 3 critic's GT-side lower bound). CPU only, deterministic.

Subcommands (each refuses to overwrite its outputs; prints the input manifests' md5s):
  dumps  derived dumps of a simulated stride-s head from each run's float16 logp (bench/headres.py), one method dir per
         stride: <dumps>/<bench>/headres_s<s>/<run_id>_hs<s>/<set>/ (bench/dumpfmt format, derived_from in the manifest).
         Read them with the reviewed scripts/bench_read_w1.py (--arm S1=<dumps>/<bench>/headres_s1:'.*' ...).
  gt     GT-side ceilings on the 532 cv5v2 out-of-fold cells (v1.1 strict GT + ignore): (a) crack fraction pooled to
         stride s, bilinear up, threshold swept over 0.05..0.95 for the best pooled crack IoU (critic: the stated lower
         bound of the ceiling); (b) the spec's one-hot ceiling (argmax, ties to the GT class) with full records.
  report one table from the read.json files of the model-side reads and gt.json, with the fixed bands of A5 section 1.

  python scripts/bench_headres.py dumps --arm PF=<method dir>:'w1g_pf_v11_f[0-4]_s[56]' --strides 1,2,4,8 \
      --dumps /home/noob/work/bench_reads/stageA/headres/dumps_w1g --workers 8
  python scripts/bench_headres.py gt --strides 1,2,4,8 --out /home/noob/work/bench_reads/stageA/headres/gt --workers 8
  python scripts/bench_headres.py report --read W1G=<read dir> [--read W1C1=<read dir>] --gt <gt dir> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import cellmeta, derived, dumpfmt, headres, sets  # noqa: E402
from bench.crossfit_op import CellGT, cmetrics, crack_counts, guards, record  # noqa: E402

GRIDLINE = 15
BANDS = {"binds": "head binds (s=4 loses >= 0.05 crack IoU or >= 0.02 relF1@2)",
         "free": "head does not bind (s=4 loses < 0.01 on both)", "between": "in between: printed, no rule"}


def git_state(root: Path) -> str:
    try:
        h = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True,
                           check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, check=True).stdout.strip()
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def band(d_iou: float, d_f1: float) -> str:
    """Spec A0 bands on s=4 minus s=1 (negative = loss)."""
    if -d_iou >= 0.05 or -d_f1 >= 0.02:
        return "binds"
    if -d_iou < 0.01 and -d_f1 < 0.01:
        return "free"
    return "between"


# ---------------------------------------------------------------- dumps
def _dump_cell(job):
    src_dir, stem, outs = job
    d = derived.load_maps(Path(src_dir) / f"{stem}.npz", logp=True)
    res = {}
    for s, out_path in outs:
        m = headres.stride_maps(d["logp"], s)
        info = dumpfmt.write_cell(out_path, m["pred"], m["oth"], m["m_crack"], m["p_crack"], m["p_inact"])
        info["diff_px"] = int((m["pred"] != d["pred"]).sum())
        info["diff_crack_px"] = int(((m["pred"] == dumpfmt.CRACK) != (d["pred"] == dumpfmt.CRACK)).sum())
        info["crack_px"] = int((m["pred"] == dumpfmt.CRACK).sum())
        res[s] = info
    return stem, res


def cmd_dumps(a) -> None:
    t0 = time.time()
    if a.workers > 8:
        sys.exit("at most 8 workers")
    strides = [int(x) for x in a.strides.split(",")]
    assert all(s in headres.STRIDES for s in strides), strides
    name, rest = a.arm.split("=", 1)
    mdir, rx = rest.rsplit(":", 1)
    runs = []
    for rd in sorted(Path(mdir).iterdir()):
        if not (rd.is_dir() and re.fullmatch(rx, rd.name)):
            continue
        sds = [p for p in sorted(rd.iterdir()) if (p / "manifest.json").exists()]
        assert len(sds) == 1, f"{rd}: expected one set dir with a manifest, found {len(sds)}"
        doc = dumpfmt.read_manifest(sds[0], verify=True)
        runs.append((sds[0], doc, dumpfmt.md5_file(sds[0] / "manifest.json")))
    assert runs, f"no run under {mdir} matches {rx}"
    fb = derived.forbidden()
    writer = f"bench_headres.py {dumpfmt.md5_file(__file__)} headres.py {dumpfmt.md5_file(ROOT / 'bench' / 'headres.py')}"
    commit = git_state(ROOT)
    plans = []
    for sd, doc, h in runs:
        stems = list(doc["cells"])
        derived.assert_open(doc["set"], stems, fb)
        outs = {}
        for s in strides:
            od = dumpfmt.cell_path(a.dumps, a.bench, f"headres_s{s}", f"{doc['run_id']}_hs{s}", doc["set"], "x").parent
            if od.exists():
                sys.exit(f"refuse: {od} exists")
            meta = derived.derived_meta([doc], [h], [str(sd)], method=f"headres_s{s}", run_id=f"{doc['run_id']}_hs{s}",
                                        seed_id=int(doc["seed"]), derivation=f"avgpool{s}_bilinear_of_logp",
                                        writer=writer, code_repo=str(ROOT), code_commit=commit,
                                        decision_rule="argmax24_of_pooled_upsampled_logp")
            outs[s] = (od, meta)
        plans.append((sd, doc, h, stems, outs))
    print(f"inputs: arm {name}, {len(plans)} runs, strides {strides}; writer {writer}; code {commit}", flush=True)
    for sd, doc, h, *_ in plans:
        print(f"  manifest {h} {doc['run_id']} f{doc['fold']} s{doc['seed']} {sd}", flush=True)
    pool = get_context("fork").Pool(a.workers) if a.workers > 1 else None
    for sd, doc, h, stems, outs in plans:
        jobs = [(str(sd), st, [(s, outs[s][0] / f"{st}.npz") for s in strides]) for st in stems]
        res = pool.map(_dump_cell, jobs, chunksize=2) if pool else [_dump_cell(j) for j in jobs]
        for s in strides:
            od, meta = outs[s]
            cells = {st: {k: r[s][k] for k in ("md5", "ties", "bytes")} for st, r in res}
            assert list(cells) == stems
            mf = dumpfmt.write_manifest(od, meta, cells)
            dpx = sum(r[s]["diff_px"] for _, r in res)
            dcr = sum(r[s]["diff_crack_px"] for _, r in res)
            cpx = sum(r[s]["crack_px"] for _, r in res)
            print(f"[{time.time() - t0:.0f}s] {doc['run_id']} s={s}: {len(cells)} cells, ties "
                  f"{sum(c['ties'] for c in cells.values())}, px differing from the fp32 dump pred {dpx} "
                  f"(crack px {dcr}), crack px {cpx}, manifest {dumpfmt.md5_file(mf)}", flush=True)
    if pool:
        pool.close(); pool.join()
    print(f"[{time.time() - t0:.0f}s] done", flush=True)


# ---------------------------------------------------------------- GT side
def _gt_cell(job):
    stem, G, strides = job
    gt, keep = cellmeta.load_gt(G, stem)
    CG = CellGT(gt, keep)
    out = {}
    for s in strides:
        f = headres.crack_fraction_up(gt, keep, s)
        cnt = np.stack([crack_counts(f > t, CG) for t in headres.T_GRID])
        oh = headres.onehot_ceiling(gt, s)
        out[s] = {"cnt": cnt.tolist(), "rec_onehot": record(oh, gt, keep, None)}
    return stem, out


def _gt_rec_at(job):
    stem, G, s, t = job
    gt, keep = cellmeta.load_gt(G, stem)
    f = headres.crack_fraction_up(gt, keep, s)
    base = np.where((gt < dumpfmt.NC) & (gt != dumpfmt.CRACK), gt, 0)          # GT crack removed, then re-predicted
    cmap = np.where(f > t, dumpfmt.CRACK, base).astype(np.uint8)
    return stem, record(cmap, gt, keep, None)


def _summ(cells: dict, keep_stem=lambda s: True) -> dict:
    g = guards(cells, keep_stem)
    if g.get("n", 0) == 0:
        return {"n": 0}
    keys = ("n", "crack_iou", "relF1_1", "relF1_2", "relP2", "relR2", "width_ratio", "cc_rec50_20", "cc_recany_20",
            "inact_iou", "miou_rob")
    out = {k: g.get(k) for k in keys}
    out["gridline_iou"] = g["per_class"][GRIDLINE]["iou"]
    return out


def cmd_gt(a) -> None:
    t0 = time.time()
    out = Path(a.out)
    for f in ("gt.json", "gt.txt"):
        if (out / f).exists():
            sys.exit(f"refuse: {out / f} exists")
    if a.workers > 8:
        sys.exit("at most 8 workers")
    strides = [int(x) for x in a.strides.split(",")]
    fb = derived.forbidden()
    jobs, stems, fold_of = [], [], {}
    print(f"inputs: labels {a.labels}; code {git_state(ROOT)}; script {dumpfmt.md5_file(__file__)}", flush=True)
    for k in range(5):
        set_name = f"cv5v2_f{k}"
        S = sets.resolve(set_name)
        derived.assert_open(set_name, S["stems"], fb)
        G = cellmeta.gt_source(set_name, a.labels)
        print(f"  {set_name}: {len(S['stems'])} stems, list {S['list_file']} md5 {S['list_md5']}; masks {G['masks']}", flush=True)
        for st in S["stems"]:
            jobs.append((st, {k2: (str(v) if v is not None else None) for k2, v in G.items()}, strides))
            stems.append(st); fold_of[st] = k
    assert len(stems) == len(set(stems)) == 532, len(stems)
    pool = get_context("fork").Pool(a.workers) if a.workers > 1 else None
    mp = pool.map if pool else map
    res = dict(mp(_gt_cell, jobs))
    doc = {"tool": "bench_headres.py gt", "tool_md5": dumpfmt.md5_file(__file__), "labels": a.labels,
           "t_grid": list(headres.T_GRID), "strides": strides, "n": len(stems), "frac": {}, "onehot": {}}
    srcs = sorted({cellmeta.source(s) for s in stems})
    for s in strides:
        cnt = np.array([res[st][s]["cnt"] for st in stems], np.int64)          # (n, T, 7)
        pooled = cnt.sum(0)
        curve = [cmetrics(r) for r in pooled]
        ious = np.array([c["crack_iou"] for c in curve])
        ib = int(np.nanargmax(ious))
        tb = headres.T_GRID[ib]
        recs = dict(mp(_gt_rec_at, [(st, j[1], s, tb) for st, j in zip(stems, jobs)]))
        doc["frac"][str(s)] = {"t_best": tb, "curve": [{"t": t, **c} for t, c in zip(headres.T_GRID, curve)],
                               "all": _summ(recs), "per_source": {x: _summ(recs, lambda q, x=x: cellmeta.source(q) == x)
                                                                  for x in srcs}}
        oh = {st: res[st][s]["rec_onehot"] for st in stems}
        doc["onehot"][str(s)] = {"all": _summ(oh), "per_source": {x: _summ(oh, lambda q, x=x: cellmeta.source(q) == x)
                                                                  for x in srcs}}
        print(f"[{time.time() - t0:.0f}s] s={s}: frac best t {tb} crack IoU {ious[ib]:.4f}; one-hot crack IoU "
              f"{doc['onehot'][str(s)]['all']['crack_iou']:.4f}", flush=True)
    if pool:
        pool.close(); pool.join()
    lines = [f"# head_res_ceiling, GT side (bench_headres.py gt {doc['tool_md5'][:8]}); labels {a.labels}; "
             f"{len(stems)} cv5v2 OOF cells; no prediction involved",
             "## (a) critic's lower bound: GT crack fraction pooled to stride s, bilinear up, best threshold t",
             "s\tt_best\tcrack_iou\trelF1_1\trelF1_2\trelP2\trelR2\twidth_ratio\tcc_rec50_20"]
    for s in strides:
        v = doc["frac"][str(s)]
        x = v["all"]
        lines.append(f"{s}\t{v['t_best']}\t" + "\t".join(f"{x[k]:.4f}" for k in
                     ("crack_iou", "relF1_1", "relF1_2", "relP2", "relR2", "width_ratio", "cc_rec50_20")))
    lines.append("## (a) per source, crack IoU at each s's t_best")
    lines.append("s\t" + "\t".join(srcs))
    for s in strides:
        v = doc["frac"][str(s)]["per_source"]
        lines.append(f"{s}\t" + "\t".join(f"{v[x]['crack_iou']:.4f}" for x in srcs))
    lines.append("## (b) spec's one-hot ceiling (argmax, ties to GT class)")
    lines.append("s\tcrack_iou\trelF1_1\trelF1_2\trelP2\trelR2\twidth_ratio\tcc_rec50_20\tinact_iou\tmiou_rob\tgridline_iou")
    for s in strides:
        x = doc["onehot"][str(s)]["all"]
        lines.append(f"{s}\t" + "\t".join(f"{x[k]:.4f}" for k in ("crack_iou", "relF1_1", "relF1_2", "relP2", "relR2",
                     "width_ratio", "cc_rec50_20", "inact_iou", "miou_rob", "gridline_iou")))
    lines.append("## (b) per source, one-hot crack IoU / inactive IoU")
    lines.append("s\t" + "\t".join(srcs))
    for s in strides:
        v = doc["onehot"][str(s)]["per_source"]
        lines.append(f"{s}\t" + "\t".join(f"{v[x]['crack_iou']:.4f}/{v[x]['inact_iou']:.4f}" for x in srcs))
    doc["seconds"] = round(time.time() - t0, 1)
    out.mkdir(parents=True, exist_ok=True)
    (out / "gt.json").write_text(json.dumps(doc, indent=1, default=float))
    (out / "gt.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)


# ---------------------------------------------------------------- report
def gridline_from_cache(cache: Path, arm: str) -> dict:
    """Mean over seeds of pooled gridline IoU at OP-A, from the read's cached argmax records (cache/<arm>/<run>/rec_argmax_*)."""
    conf = {}
    for p in sorted((cache / "cache" / arm).glob("*/rec_argmax_*.json")):
        m = re.search(r"_s(\d+)_hs\d+$", p.parent.name)
        if not m:
            continue
        sd = m.group(1)
        for rec in json.loads(p.read_text()).values():
            C = np.asarray(rec["conf"], np.int64).reshape(dumpfmt.NC, dumpfmt.NC)
            conf[sd] = conf.get(sd, 0) + C
    v = []
    for sd, C in sorted(conf.items()):
        den = C[GRIDLINE].sum() + C[:, GRIDLINE].sum() - C[GRIDLINE, GRIDLINE]
        v.append(C[GRIDLINE, GRIDLINE] / den if den else float("nan"))
    return {"mean": float(np.mean(v)) if v else None, "seeds": sorted(conf)}


def cmd_report(a) -> None:
    out = Path(a.out)
    if (out / "headres.txt").exists():
        sys.exit(f"refuse: {out / 'headres.txt'} exists")
    gt = json.loads((Path(a.gt) / "gt.json").read_text())
    lines = [f"# head_res_ceiling report (bench_headres.py {dumpfmt.md5_file(__file__)[:8]}); gt.json "
             f"{dumpfmt.md5_file(Path(a.gt) / 'gt.json')[:8]}"]
    doc = {"reads": {}, "gt_md5": dumpfmt.md5_file(Path(a.gt) / "gt.json")}
    keys = ("crack_iou", "relF1_1", "relF1_2", "relP2", "relR2", "width_ratio", "mean_width", "cc_rec50_20",
            "inact_iou", "miou_rob")
    ckeys = ("crack_iou", "relF1_2", "relF1_1", "width_ratio", "relP2", "relR2", "inact_iou", "miou_rob")
    for spec in a.read:
        tag, rd = spec.split("=", 1)
        rd = Path(rd)
        r = json.loads((rd / "read.json").read_text())
        D = doc["reads"][tag] = {"md5": dumpfmt.md5_file(rd / "read.json"), "rows": {}, "contrasts": {}, "notes": r["notes"]}
        lines.append(f"## model side {tag}: {rd}/read.json {D['md5'][:8]}; mean (sd) over seeds; all 532 OOF cells")
        lines += [f"NOTE {n}" for n in r["notes"]]
        lines.append("arm\top\tseeds\t" + "\t".join(keys) + "\tgridline_iou(OP-A)")
        for arm, v in r["summary"].items():
            gl = gridline_from_cache(Path(a.cache_of.get(tag, rd)) if a.cache_of else rd, arm)
            for op in ("OP-A", "OP-F", "OP-W"):
                g = v[op]["all"]
                row = {k: g[k]["mean"] for k in keys if k in g}
                row["sd"] = {k: g[k]["sd"] for k in keys if k in g}
                row["gridline_iou"] = gl["mean"] if op == "OP-A" else None
                D["rows"][f"{arm}|{op}"] = row
                lines.append(f"{arm}\t{op}\t{g['crack_iou']['n']}\t" + "\t".join(
                    f"{g[k]['mean']:.4f} ({g[k]['sd']:.3f})" if k in g and g[k]["mean"] is not None else "n/a" for k in keys)
                    + (f"\t{gl['mean']:.4f}" if op == "OP-A" and gl["mean"] is not None else "\t"))
            lines.append(f"{arm}\tper source OP-A crack IoU / relF1@2 / width: " + "; ".join(
                f"{sn[4:]} {g['crack_iou']['mean']:.4f} / {g['relF1_2']['mean']:.4f} / {g['width_ratio']['mean']:.3f}"
                for sn, g in v["OP-A"].items() if sn.startswith("src:")))
        lines.append(f"## contrasts {tag}: B - A, two-stage group bootstrap 95% CI (read.json)")
        for name, d in r["contrasts"].items():
            for op, b in d.items():
                D["contrasts"][f"{name}|{op}"] = {k: b["metrics"][k] for k in ckeys}
                lines.append(f"{name}\t{op}\t" + "\t".join(
                    f"{k} {b['metrics'][k]['delta']:+.4f} [{b['metrics'][k]['lo']:+.4f}, {b['metrics'][k]['hi']:+.4f}]"
                    for k in ckeys))
        lines.append(f"## band {tag} (T11 A0 bands on S4 - S1 at OP-A; critic's fix: printed beside stride-4 rows, bars nothing)")
        c = D["contrasts"].get("S4 - S1|OP-A")
        if c is None:
            lines.append("band not computed: no contrast 'S4 - S1' at OP-A in this read")
        else:
            di, df = c["crack_iou"]["delta"], c["relF1_2"]["delta"]
            b = band(di, df)
            D["band"] = {"d_crack_iou": di, "d_relF1_2": df, "band": b}
            lines.append(f"S4 - S1 at OP-A: crack IoU {di:+.4f}, relF1@2 {df:+.4f} -> {BANDS[b]}")
    lines.append("## GT side: (a) lower bound of the ceiling (pooled GT crack fraction, bilinear, best t); "
                 "(b) spec's one-hot ceiling (argmax, ties to GT)")
    lines.append("s\ta_t\ta_crack_iou\ta_relF1_1\ta_relF1_2\ta_width\tb_crack_iou\tb_relF1_1\tb_relF1_2\tb_width\t"
                 "b_inact_iou\tb_miou_rob\tb_gridline")
    for s in gt["strides"]:
        fa, ob = gt["frac"][str(s)], gt["onehot"][str(s)]["all"]
        lines.append(f"{s}\t{fa['t_best']}\t{fa['all']['crack_iou']:.4f}\t{fa['all']['relF1_1']:.4f}\t"
                     f"{fa['all']['relF1_2']:.4f}\t{fa['all']['width_ratio']:.4f}\t{ob['crack_iou']:.4f}\t"
                     f"{ob['relF1_1']:.4f}\t{ob['relF1_2']:.4f}\t{ob['width_ratio']:.4f}\t{ob['inact_iou']:.4f}\t"
                     f"{ob['miou_rob']:.4f}\t{ob['gridline_iou']:.4f}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "headres.json").write_text(json.dumps(doc, indent=1, default=float))
    (out / "headres.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dumps")
    d.add_argument("--arm", required=True, help="NAME=<method dir>:<run_id regex>")
    d.add_argument("--strides", default="1,2,4,8")
    d.add_argument("--dumps", required=True)
    d.add_argument("--bench", default="elbench1")
    d.add_argument("--workers", type=int, default=8)
    g = sub.add_parser("gt")
    g.add_argument("--strides", default="1,2,4,8")
    g.add_argument("--labels", default="v11", choices=("v11",))
    g.add_argument("--out", required=True)
    g.add_argument("--workers", type=int, default=8)
    r = sub.add_parser("report")
    r.add_argument("--read", action="append", required=True, help="TAG=<read dir with read.json>")
    r.add_argument("--gt", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--cache", action="append", default=[], help="TAG=<cache root of that read> (default: the read dir)")
    a = ap.parse_args(argv)
    if a.cmd == "report":
        a.cache_of = dict(x.split("=", 1) for x in a.cache)
    {"dumps": cmd_dumps, "gt": cmd_gt, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
