"""elbench frozen scorer: dumps + ground truth -> per-cell records (m0 schema + rel@1/3) -> run / arm summaries.
CPU only, numpy + scipy + PIL (no torch). DESIGN.md s3.2.

Subcommands
  records  --dumps <run_dir>/<set> --set NAME --out REC.json [--opening P] [--labels set|v11|v1|manifest]
           (x3: --labels picks the ground truth, bench/cellmeta.py; default 'set' = bench/sets.py as before)
           per cell: m0core.cell_stats(pred, gt, keep, p_crack) (line-identical to m0_audit d36f7438) + crack_rel1 / rel3.
           Asserts: manifest md5s (dumpfmt.read_manifest), manifest set == NAME, dumped cells == the set's stem list
           (same order), stems md5 = manifest's.
  refrows  --set NAME --out REF.json [--opening P]
           GT-only label-noise rows: GT shifted 1 px (up / down / left / right) and crack dilated 1 px, scored as predictions.
  summary  --records R.json ... --arms NAME=REGEX ... [--ref REF.json] [--celltypes TSV] [--pairs A=B ...]
           [--boot 2000] [--groups TSV] [--cells-tsv TSV] --out SUM.json
           (x3: --cells-tsv adds meta:src:*, meta:type:*, meta:crackfree, meta:crack, meta:-flagged, meta:flag:* subsets)
           run metrics per subset (all, -noisy, -twins, per source, per cell type); arm mean / sd over runs; R1 per pair
           (ssl_rules.cmp); paired bootstrap per pair over cells, or over groups with --groups (stem -> group TSV).
           Refuses runs of one comparison with different precision, device type, scorer md5 or set list md5.
  ast-check --ref-audit tests/ref/m0_audit_d36f7438.py --ref-analyze tests/ref/m0_analyze_d5adbe6b.py
  compare  --a A.json --b B.json [--a-cells KEY] [--b-cells KEY]
           per-cell records equal? prints only IDENTICAL / DIFF with counts (never values). KEY = path to the
           {stem: record} dict inside the JSON, e.g. cells or cells/heldout or cells/val.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bench import dumpfmt, sets  # noqa: E402
from bench.m0core import CRACK, INACT, NC, cell_stats  # noqa: E402
from bench.score_ext import RADII, SHIFTS, crack_dilated, rel_counts, shifted, subsets, summarize  # noqa: E402

PRIMARY = ("crack_iou", "relF1_2", "inact_iou", "miou_rob")


def md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


def self_md5() -> str:
    return dumpfmt.md5_file(__file__)


def load_gt(S: dict, stem: str):
    gt = np.array(Image.open(S["masks"] / f"{stem}.png"))
    keep = None
    if S["ignore"] is not None:
        keep = ~(np.array(Image.open(S["ignore"] / f"{stem}.png")) > 0)
    return gt, keep


def record(pred, gt, keep, pc) -> dict:
    r = cell_stats(pred, gt, keep, pc)
    r.update(rel_counts(pred, gt, keep, radii=(1, 3)))
    return r


# ---------------------------------------------------------------- records
def cmd_records(a) -> None:
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    doc = dumpfmt.read_manifest(a.dumps, verify=True)
    assert doc["set"] == a.set, (doc["set"], a.set)
    S = sets.resolve(a.set, a.opening)
    assert list(doc["cells"]) == S["stems"], "dumped cell order != the set's stem list"
    assert doc["stems_md5"] == sets.stems_md5(S["stems"]), "stems md5 != manifest"
    cells, ties = {}, 0
    G = None  # x3: --labels other than the default 'set' (bench/cellmeta.py: v11, v1, or from the run manifest)
    if a.labels != "set":
        from bench import cellmeta
        G = cellmeta.gt_source(a.set, a.labels, doc, a.opening)
    for s in S["stems"]:
        d = dumpfmt.read_cell(Path(a.dumps) / f"{s}.npz", check=True)
        gt, keep = load_gt(S, s) if G is None else load_gt(G, s)
        cells[s] = record(d["pred"], gt, keep, d["p_crack"])
        ties += int(dumpfmt.check_cell(d)["ties"])
    res = {"run_id": doc["run_id"], "method": doc["method"], "set": a.set, "seed": doc["seed"], "fold": doc["fold"],
           "precision": doc["precision"], "device": doc["device"], "weights_key": doc["weights_key"],
           "step": doc["step"], "split_md5": doc["split_md5"], "stems_md5": doc["stems_md5"],
           "list_md5": S["list_md5"], "manifest_md5": dumpfmt.md5_file(Path(a.dumps) / "manifest.json"),
           "scorer_md5": self_md5(), "ties": ties, "cells": cells}
    if G is not None:  # x3
        res.update({"labels": G["labels"], "gt_masks": str(G["masks"]), "gt_ignore": None if G["ignore"] is None else str(G["ignore"])})
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res))
    print(f"records {doc['run_id']} {a.set}: {len(cells)} cells, ties {ties} -> {out}")


# ---------------------------------------------------------------- GT-only reference rows
def cmd_refrows(a) -> None:
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    S = sets.resolve(a.set, a.opening)
    rows = {f"shift1_{k}": {} for k in SHIFTS} | {"dil1": {}}
    for s in S["stems"]:
        gt, keep = load_gt(S, s)
        for k, (dy, dx) in SHIFTS.items():
            rows[f"shift1_{k}"][s] = record(shifted(gt, dy, dx), gt, keep, None)
        rows["dil1"][s] = record(crack_dilated(gt, 1), gt, keep, None)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"set": a.set, "list_md5": S["list_md5"], "scorer_md5": self_md5(), "rows": rows}))
    print(f"refrows {a.set}: {len(S['stems'])} cells, rows {sorted(rows)} -> {out}")


# ---------------------------------------------------------------- summary
def _scalar_metrics(m: dict) -> dict:
    return {k: v for k, v in m.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def _mean_sd(vals: list[float]) -> dict:
    v = np.array([x for x in vals if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    if not len(v):
        return {"mean": None, "sd": None, "n": 0}
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0, "n": int(len(v))}


def r1(xa: list[float], xb: list[float]) -> dict:
    """ssl_rules.cmp: delta = mean(B) - mean(A); thr = max(0.01, 2 sqrt((sd_A^2 + sd_B^2) / 3))."""
    sd = lambda x: float(np.std(x, ddof=1)) if len(x) > 1 else 0.0  # noqa: E731
    dl = float(np.mean(xb) - np.mean(xa))
    thr = max(0.01, 2 * math.sqrt((sd(xa) ** 2 + sd(xb) ** 2) / 3))
    return {"delta": dl, "thr": thr, "verdict": "BETTER" if dl > thr else "WORSE" if dl < -thr else "n.d."}


def _pooled_arrays(cells: dict, stems: list[str]) -> dict:
    conf = np.array([cells[s]["conf"] for s in stems], np.int64)            # (n, 576)
    rel2 = np.array([cells[s]["crack_rel2"] for s in stems], np.int64)       # (n, 4)
    return {"conf": conf, "rel2": rel2}


def _metrics_from_pooled(conf: np.ndarray, rel2: np.ndarray) -> dict:
    from bench.score_ext import ROB13
    C = conf.reshape(NC, NC).astype(float)
    tp = np.diag(C); gt = C.sum(1); pr = C.sum(0); den = gt + pr - tp
    iou = np.where(den > 0, tp / np.maximum(den, 1), np.nan)
    P, R = rel2[0] / max(rel2[1], 1), rel2[2] / max(rel2[3], 1)
    rob = [iou[c] for c in ROB13 if gt[c] > 0]
    return {"crack_iou": iou[CRACK], "inact_iou": iou[INACT], "relF1_2": 2 * P * R / max(P + R, 1e-9),
            "miou_rob": float(np.mean(rob)) if rob else float("nan")}


def bootstrap_pair(runsA: list[dict], runsB: list[dict], stems: list[str], groups: dict | None, B: int, seed: int = 0):
    """Paired bootstrap of delta = mean over B-runs - mean over A-runs of the pooled PRIMARY metrics.
    Units: cells, or groups (with multiplicity) when groups are given. random.Random(seed) as b6_verdict."""
    units = sorted({groups[s] for s in stems}) if groups else list(stems)
    idx = {u: [i for i, s in enumerate(stems) if (groups[s] if groups else s) == u] for u in units}
    arrA = [_pooled_arrays(r["cells"], stems) for r in runsA]
    arrB = [_pooled_arrays(r["cells"], stems) for r in runsB]
    rng = random.Random(seed)
    deltas = {k: [] for k in PRIMARY}
    for _ in range(B):
        w = np.zeros(len(stems), np.int64)
        for u in (units[rng.randrange(len(units))] for _ in range(len(units))):
            w[idx[u]] += 1
        mA = [_metrics_from_pooled(w @ x["conf"], w @ x["rel2"]) for x in arrA]
        mB = [_metrics_from_pooled(w @ x["conf"], w @ x["rel2"]) for x in arrB]
        for k in PRIMARY:
            deltas[k].append(float(np.nanmean([m[k] for m in mB]) - np.nanmean([m[k] for m in mA])))
    return {k: {"lo": float(np.percentile(v, 2.5)), "hi": float(np.percentile(v, 97.5))} for k, v in deltas.items()}


def cmd_summary(a) -> None:
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refuse: {out} exists")
    recs = [json.loads(Path(p).read_text()) for p in a.records]
    sets_seen = {r["set"] for r in recs}
    assert len(sets_seen) == 1, f"one set per summary, got {sets_seen}"
    set_name = sets_seen.pop()
    for key in ("precision", "scorer_md5", "list_md5", "stems_md5"):
        vals = {r[key] for r in recs}
        assert len(vals) == 1, f"mixed {key} in one comparison: {vals}"
    dev_types = {r["device"].split(":")[0] for r in recs}
    assert len(dev_types) == 1, f"mixed device types: {dev_types}"
    stems = list(recs[0]["cells"])
    for r in recs:
        assert list(r["cells"]) == stems, f"{r['run_id']}: cell list differs"
    celltypes = sets.load_celltypes(a.celltypes) if a.celltypes else None
    subs = subsets(stems, set_name, sets.NOISY, sets.TWINS, celltypes)
    if a.cells_tsv:  # x3: source / cell type / crack-free / flag subsets from bench_data/meta/cells.tsv
        from bench import cellmeta
        subs.update({f"meta:{k}": v for k, v in cellmeta.subsets(stems, cellmeta.load_cells(a.cells_tsv)).items()})
    arms = {}
    for spec in a.arms:
        name, rx = spec.split("=", 1)
        arms[name] = [r for r in recs if re.fullmatch(rx, r["run_id"])]
        assert arms[name], f"arm {name}: no run matches {rx}"
    res = {"set": set_name, "n_cells": len(stems), "scorer_md5": self_md5(), "precision": recs[0]["precision"],
           "celltypes_md5": dumpfmt.md5_file(a.celltypes) if a.celltypes else None, "arms": {}, "ref": {}, "pairs": {}}
    for name, runs in arms.items():
        res["arms"][name] = {"runs": [r["run_id"] for r in runs], "subsets": {}}
        for sn, f in subs.items():
            per_run = [summarize(r["cells"], f) for r in runs]
            keys = sorted(set().union(*(_scalar_metrics(m) for m in per_run)))
            res["arms"][name]["subsets"][sn] = {"n": per_run[0]["n"],
                                                **{k: _mean_sd([m.get(k) for m in per_run]) for k in keys}}
    if a.ref:
        ref = json.loads(Path(a.ref).read_text())
        assert ref["set"] == set_name and ref["list_md5"] == recs[0]["list_md5"], "reference rows are of another set"
        for sn, f in subs.items():
            sh = [summarize(ref["rows"][f"shift1_{k}"], f) for k in SHIFTS]
            keys = sorted(set().union(*(_scalar_metrics(m) for m in sh)))
            res["ref"].setdefault("shift1_mean4", {})[sn] = {k: float(np.nanmean([m.get(k, np.nan) for m in sh])) for k in keys}
            res["ref"].setdefault("dil1", {})[sn] = _scalar_metrics(summarize(ref["rows"]["dil1"], f))
    groups = None
    if a.groups:
        rows = [l.rstrip("\n").split("\t") for l in open(a.groups) if l.strip()]
        i_s, i_g = rows[0].index("stem"), rows[0].index(a.group_col)
        groups = {r[i_s]: r[i_g] for r in rows[1:]}
        assert all(s in groups for s in stems), "a cell has no group"
    for spec in a.pairs or []:
        A, Bn = spec.split("=", 1)
        pr = {"rule": "R1 (ssl_rules.cmp), all cells", "metrics": {}}
        for sn in ("all", "-noisy"):
            if sn not in subs:
                continue
            ma = [summarize(r["cells"], subs[sn]) for r in arms[A]]
            mb = [summarize(r["cells"], subs[sn]) for r in arms[Bn]]
            pr["metrics"][sn] = {k: r1([m[k] for m in ma], [m[k] for m in mb]) for k in PRIMARY}
        if a.boot:
            pr["bootstrap"] = {"B": a.boot, "unit": "group" if groups else "cell",
                               "ci95": bootstrap_pair(arms[A], arms[Bn], stems, groups, a.boot)}
        res["pairs"][f"{Bn} - {A}"] = pr
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x))
    print(f"summary {set_name}: arms {list(arms)}, subsets {len(subs)}, pairs {len(res['pairs'])} -> {out}")


# ---------------------------------------------------------------- AST identity of the copied m0 code
def _defs(path: Path, names: list[str]) -> dict:
    tree = ast.parse(Path(path).read_text())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            out[node.name] = ast.dump(node, include_attributes=False)
        elif isinstance(node, ast.Assign):
            tg = [t.id for t in node.targets if isinstance(t, ast.Name)]
            tg += [e.id for t in node.targets if isinstance(t, ast.Tuple) for e in t.elts if isinstance(e, ast.Name)]
            for n in tg:
                if n in names:
                    out[n] = ast.dump(node, include_attributes=False)
    return out


def ast_check(ref_audit: Path, ref_analyze: Path) -> list[str]:
    mine = ROOT / "bench" / "m0core.py"
    problems = []
    assert dumpfmt.md5_file(ref_audit) == "d36f7438d0fefb0ffc926c69f6c6af2d", "reference m0_audit.py md5"
    assert dumpfmt.md5_file(ref_analyze) == "d5adbe6bfb84ce251f56ec7494a69663", "reference m0_analyze.py md5"
    for ref, names in ((ref_audit, ["comps", "cell_stats", "BANDS", "NC", "S8"]), (ref_analyze, ["src", "agg", "DEFECT"])):
        a, b = _defs(ref, names), _defs(mine, names)
        for n in names:
            if n not in a or n not in b:
                problems.append(f"{n}: missing ({'ref' if n not in a else 'bench'})")
            elif a[n] != b[n]:
                problems.append(f"{n}: AST differs")
    return problems


def cmd_ast(a) -> None:
    p = ast_check(Path(a.ref_audit), Path(a.ref_analyze))
    print("IDENTICAL (comps, cell_stats, BANDS, NC, S8 vs m0_audit d36f7438; src, agg, DEFECT vs m0_analyze d5adbe6b)"
          if not p else f"DIFF {len(p)}: {p}")
    sys.exit(1 if p else 0)


# ---------------------------------------------------------------- compare (values never printed)
def _cells_at(doc: dict, key: str) -> dict:
    for part in key.split("/"):
        doc = doc[part]
    return doc


def cmd_compare(a) -> None:
    A = _cells_at(json.loads(Path(a.a).read_text()), a.a_cells)
    B = _cells_at(json.loads(Path(a.b).read_text()), a.b_cells)
    if list(A) != list(B):
        print(f"DIFF cell lists: {len(A)} vs {len(B)} cells, {len(set(A) ^ set(B))} not shared")
        sys.exit(1)
    fields = sorted(set().union(*(set(B[s]) for s in B)))
    common = [f for f in fields if all(f in A[s] for s in A)]
    only_b = [f for f in fields if f not in common]
    nd, by_field = 0, {}
    for s in A:
        for f in common:
            if A[s][f] != B[s][f]:
                nd += 1
                by_field[f] = by_field.get(f, 0) + 1
    ncells = sum(1 for s in A if any(A[s][f] != B[s][f] for f in common))
    tag = "IDENTICAL" if nd == 0 else "DIFF"
    print(f"{tag}: {len(A)} cells, {len(common)} shared fields {common}; differing (cell, field) pairs {nd}, "
          f"cells with any difference {ncells}, per field {by_field}; fields only in B (not compared) {only_b}")
    sys.exit(0 if nd == 0 else 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("records"); p.add_argument("--dumps", required=True); p.add_argument("--set", required=True)
    p.add_argument("--out", required=True); p.add_argument("--opening", default=None)
    p.add_argument("--labels", default="set", choices=("set", "v11", "v1", "manifest"))  # x3
    p = sp.add_parser("refrows"); p.add_argument("--set", required=True); p.add_argument("--out", required=True)
    p.add_argument("--opening", default=None)
    p = sp.add_parser("summary"); p.add_argument("--records", nargs="+", required=True)
    p.add_argument("--arms", nargs="+", required=True); p.add_argument("--ref", default=None)
    p.add_argument("--celltypes", default=None); p.add_argument("--pairs", nargs="*", default=[])
    p.add_argument("--cells-tsv", default=None)  # x3
    p.add_argument("--boot", type=int, default=0); p.add_argument("--groups", default=None)
    p.add_argument("--group-col", default="phys_group"); p.add_argument("--out", required=True)
    p = sp.add_parser("ast-check"); p.add_argument("--ref-audit", default=str(ROOT / "tests/ref/m0_audit_d36f7438.py"))
    p.add_argument("--ref-analyze", default=str(ROOT / "tests/ref/m0_analyze_d5adbe6b.py"))
    p = sp.add_parser("compare"); p.add_argument("--a", required=True); p.add_argument("--b", required=True)
    p.add_argument("--a-cells", default="cells"); p.add_argument("--b-cells", default="cells")
    a = ap.parse_args()
    {"records": cmd_records, "refrows": cmd_refrows, "summary": cmd_summary, "ast-check": cmd_ast,
     "compare": cmd_compare}[a.cmd](a)


if __name__ == "__main__":
    main()
