"""elbench x3: shared plumbing for the CPU tools on prediction dumps (wave 1 read, src_calib, dti, D0).

Runs come from dump folders (<method dir>/<run_id>/<set>/manifest.json, written by scripts/bench_infer.py) or, for dry
tests, from a runs TSV (arm, seed, set dir). Every per-cell computation runs in a process pool (fork; numpy / scipy;
OMP 1 thread per worker) and is cached under <out>/cache/<arm>/<run_id>/ by a key that holds the manifest md5, the label
set and the candidate list or per-cell choice. Out-of-fold (OOF) assembly: one record per pool stem per (arm, seed), the
stem's fold = its run's held-out fold (manifest), or a pseudo fold (md5 of the stem's bootstrap group mod N) in dry tests.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from multiprocessing import get_context
from pathlib import Path

import numpy as np

from . import cellmeta, dumpfmt, sets
from .crossfit_op import CellGT, class_map, record, sweep_cell

SEALED = dumpfmt.SEALED


@dataclass
class Run:
    arm: str
    seed: int
    run_id: str
    set_dir: Path
    set_name: str
    fold: int | None
    manifest: dict = field(repr=False)
    manifest_md5: str = ""
    stems: list = field(default_factory=list)
    gt: dict = field(default_factory=dict)


def _load_run(arm: str, set_dir: Path, labels: str, seed: int | None = None) -> Run:
    doc = dumpfmt.read_manifest(set_dir, verify=True)
    sname = doc["set"]
    if sname in SEALED:
        raise dumpfmt.SealedSetError(f"{set_dir}: sealed set {sname}; these tools never read sealed sets")
    S = sets.resolve(sname, None)
    assert list(doc["cells"]) == S["stems"], f"{set_dir}: dumped cells != the set's stem list"
    assert doc["stems_md5"] == sets.stems_md5(S["stems"]), f"{set_dir}: stems md5"
    G = cellmeta.gt_source(sname, labels, doc)
    fold = int(sname.rsplit("_f", 1)[1]) if sname.startswith("cv") else None
    return Run(arm, int(doc["seed"] if seed is None else seed), doc["run_id"], Path(set_dir), sname, fold, doc,
               dumpfmt.md5_file(Path(set_dir) / "manifest.json"), list(S["stems"]),
               {"labels": G["labels"], "masks": str(G["masks"]), "ignore": None if G["ignore"] is None else str(G["ignore"])})


def discover(specs: list[str], labels: str) -> list[Run]:
    """specs: NAME=<method dir>:<run_id regex>. Each matching run dir must hold exactly one set dir with a manifest."""
    runs = []
    for spec in specs:
        name, rest = spec.split("=", 1)
        mdir, rx = rest.rsplit(":", 1)
        found = 0
        for rd in sorted(Path(mdir).iterdir()):
            if not (rd.is_dir() and re.fullmatch(rx, rd.name)):
                continue
            sds = [p for p in sorted(rd.iterdir()) if (p / "manifest.json").exists()]
            assert len(sds) == 1, f"{rd}: expected one set dir with a manifest, found {len(sds)}"
            runs.append(_load_run(name, sds[0], labels)); found += 1
        assert found, f"arm {name}: no run dir under {mdir} matches {rx}"
    return runs


def runs_from_tsv(path: str, labels: str) -> list[Run]:
    """Dry tests: TSV lines 'arm<TAB>seed<TAB>set dir' (no header); the same dump may serve several seeds or arms."""
    out = []
    for line in open(path):
        if line.strip() and not line.startswith("#"):
            arm, seed, sd = line.rstrip("\n").split("\t")
            out.append(_load_run(arm, Path(sd), labels, int(seed)))
    return out


def check_comparable(runs: list[Run], dry: bool) -> None:
    for key in ("precision",):
        vals = {r.manifest[key] for r in runs}
        if len(vals) > 1 and not dry:
            raise AssertionError(f"mixed {key} in one comparison: {vals}")
    dev = {"cpu" if r.manifest["device"] == "cpu" else "cuda" for r in runs}
    if len(dev) > 1 and not dry:
        raise AssertionError(f"mixed device types: {dev}")
    lab = {r.gt["labels"] for r in runs}
    assert len(lab) == 1, f"mixed label sets: {lab}"
    if not dry:
        for r in runs:
            assert r.set_name.startswith("cv5v2_f"), f"{r.run_id}: wave 1 reads only cv5v2 out-of-fold sets ({r.set_name})"


# ---------------------------------------------------------------- per-cell jobs
def _job(a):
    set_dir, stem, gt, task, payload = a
    d = dumpfmt.read_cell(Path(set_dir) / f"{stem}.npz", check=True)
    g, keep = cellmeta.load_gt(gt, stem)
    if task == "sweep":
        return sweep_cell(d, CellGT(g, keep), payload)
    if task == "rec":
        return record(class_map(payload, d), g, keep, d["p_crack"])
    if task == "d0":
        from .placement import d0_cell
        return d0_cell(d, g, keep, payload)
    raise ValueError(task)


class Pool:
    def __init__(self, workers: int):
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        self.p = get_context("fork").Pool(workers) if workers > 1 else None

    def map(self, jobs):
        if self.p is None:
            return [_job(j) for j in jobs]
        return self.p.map(_job, jobs, chunksize=4)

    def close(self):
        if self.p is not None:
            self.p.close(); self.p.join()


def _key(*parts) -> str:
    return hashlib.md5(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:12]


def _cache(out: Path, r: Run, name: str, key: str) -> Path:
    p = out / "cache" / r.arm / r.run_id / f"{name}_{key}"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def sweep(pool: Pool, out: Path, r: Run, cands: list[tuple], tag: str) -> np.ndarray:
    """(n stems, K, 7) crack counts of run r for every candidate."""
    p = _cache(out, r, f"sweep_{tag}", _key(r.manifest_md5, r.gt, cands)).with_suffix(".npy")
    if p.exists():
        return np.load(p)
    res = np.stack(pool.map([(str(r.set_dir), s, r.gt, "sweep", cands) for s in r.stems]))
    np.save(p, res)
    return res


def records(pool: Pool, out: Path, r: Run, choice: list[tuple] | tuple, tag: str) -> dict:
    """{stem: full record} for run r; choice = one candidate for all cells or one per cell (r.stems order)."""
    per = [choice] * len(r.stems) if isinstance(choice, tuple) else list(choice)
    assert len(per) == len(r.stems)
    p = _cache(out, r, f"rec_{tag}", _key(r.manifest_md5, r.gt, per)).with_suffix(".json")
    if p.exists():
        return json.loads(p.read_text())
    res = pool.map([(str(r.set_dir), s, r.gt, "rec", c) for s, c in zip(r.stems, per)])
    doc = dict(zip(r.stems, res))
    p.write_text(json.dumps(doc))
    return doc


# ---------------------------------------------------------------- out-of-fold assembly
def pseudo_fold(group: str, n: int) -> int:
    return int(hashlib.md5(group.encode()).hexdigest(), 16) % n


def assemble(runs: list[Run], groups: dict, pseudo_folds: int = 0, allow_partial: bool = False):
    """-> arms {arm: {seed: [Run]}}, fold_of {stem: k}, stems (common OOF stem list, fold order), notes [str]."""
    arms, notes = {}, []
    for r in runs:
        arms.setdefault(r.arm, {}).setdefault(r.seed, []).append(r)
    fold_of = {}
    per_arm_seed_stems = {}
    for a, by in arms.items():
        for sd, rs in by.items():
            seen = []
            for r in rs:
                for s in r.stems:
                    k = pseudo_fold(groups[s], pseudo_folds) if pseudo_folds else r.fold
                    assert k is not None, f"{r.run_id}: no fold (not a CV set); use --pseudo-folds for a dry test"
                    assert fold_of.setdefault(s, k) == k, f"{s}: fold differs between runs"
                    seen.append(s)
            assert len(seen) == len(set(seen)), f"arm {a} seed {sd}: a stem is held out by two runs"
            if not pseudo_folds:
                fl = sorted({r.fold for r in rs})
                if fl != list(range(5)):
                    msg = f"arm {a} seed {sd}: folds {fl} (not 0..4)"
                    if not allow_partial:
                        raise AssertionError(msg + "; pass --allow-partial to read a partial set")
                    notes.append("PARTIAL " + msg)
            per_arm_seed_stems[(a, sd)] = set(seen)
    common = set.intersection(*per_arm_seed_stems.values())
    if any(v != common for v in per_arm_seed_stems.values()):
        msg = "arms / seeds cover different stems; the read uses the common stems only"
        if not allow_partial:
            raise AssertionError(msg)
        notes.append("PARTIAL " + msg)
    stems = sorted(common, key=lambda s: (fold_of[s], s))
    return arms, fold_of, stems, notes


def rkey(r: Run) -> str:
    return f"{r.arm}|{r.seed}|{r.run_id}"


def oof_records(rec_by_run: dict, runs: list[Run], stems: list[str]) -> dict:
    """{stem: record} over the given runs of one (arm, seed), restricted to stems. rec_by_run is keyed by rkey()."""
    out = {}
    for r in runs:
        for s, v in rec_by_run[rkey(r)].items():
            out[s] = v
    return {s: out[s] for s in stems}


def oof_counts(cnt_by_run: dict, runs: list[Run], stems: list[str]) -> np.ndarray:
    idx = {}
    for r in runs:
        for i, s in enumerate(r.stems):
            idx[s] = (rkey(r), i)
    return np.stack([cnt_by_run[idx[s][0]][idx[s][1]] for s in stems])


def per_cell_choice(r: Run, fold_of: dict, choice_by_fold: dict, cands: list[tuple]) -> list[tuple]:
    return [cands[choice_by_fold[fold_of[s]]] if s in fold_of else ("argmax",) for s in r.stems]


def fmt(x, nd=4) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


def write_once(p: Path, text: str) -> None:
    if p.exists():
        raise FileExistsError(f"refuse: {p} exists")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
