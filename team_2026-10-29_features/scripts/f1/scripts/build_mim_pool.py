#!/usr/bin/env python
"""F1 / MIM5: build the pretraining image list (paths relative to the data root).

Pool = external unlabelled cells (data/splits/external_unlabeled.txt, data/unlabeled/images_512) minus the exclusions
below, plus train cells (data/splits/train.txt, data/labeled/images) minus the D7 train twins of test cells
(data/splits/d7_twin_train_cells.txt). External exclusions (coach_mim5.md B, review_mim5_v0 C1):
  R1 module: every pool cell whose (source, module id) is the module of a val, test or E1 (106) cell;
  R2 ext117: the ext117 stems that are in the pool (11);
  R3 content: every pool cell with high-pass r >= --hp_thr to any val, test or ext117 query, from the near-dup
     outputs (neardup.json hp_pairs: 128 px high-pass, any position; samepos_pool.json: full-res high-pass, same
     source and cell position);
  R4 twin copies: every pool cell with r_hp >= --twin_thr to one of the 7 D7 train twins (neardup.json hp_pairs);
  --exclude: extra stems (none needed once R1-R4 apply).
Then --monitor pool cells (fixed seed) are held out for a reconstruction-loss monitor only (written to --monitor_out).
Hard checks: no val, test or E1 stem in either list. Prints counts per rule and the md5 of the written lists.
Module id = the first two '_' fields of the stem (e.g. CSIR_00298 of CSIR_00298_r8_c6).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


def read_stems(p: Path) -> list[str]:
    return [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]


def module(stem: str) -> str:
    return "_".join(stem.split("_")[:2])


def build(data_root: Path, e1_manifest: Path | None, exclude: list[str], neardup: Path | None = None,
          samepos: Path | None = None, hp_thr: float = 0.85, twin_thr: float = 0.95, monitor: int = 0,
          monitor_seed: int = 0) -> tuple[list[str], list[str], dict]:
    sp = data_root / "splits"
    ext, train = read_stems(sp / "external_unlabeled.txt"), read_stems(sp / "train.txt")
    val, test = set(read_stems(sp / "val.txt")), set(read_stems(sp / "test.txt"))
    twins = read_stems(sp / "d7_twin_train_cells.txt")
    e1, ext117 = set(), set()
    if e1_manifest is not None:
        rows = list(csv.DictReader(open(e1_manifest)))
        ext117 = {r["stem"] for r in rows}
        e1 = {r["stem"] for r in rows if r["in_external_pool"] == "0"}  # the 106 evaluated E1 cells
        if len(e1) != 106 or len(ext117) != 117:
            raise ValueError(f"expected 117 ext117 / 106 E1 cells, got {len(ext117)} / {len(e1)}")
    if len(twins) != 7 or not set(twins) <= set(train):
        raise ValueError(f"D7 twins must be 7 train cells: {twins}")
    ext_set = set(ext)
    drop: dict[str, set] = {}
    held_mods = {module(x) for x in val | test | e1}
    drop["R1_module"] = {x for x in ext if module(x) in held_mods}
    drop["R2_ext117_in_pool"] = ext117 & ext_set
    r3, r4 = set(), set()
    if neardup is not None:
        for p in json.load(open(neardup))["hp_pairs"]:
            if p["split"] in ("val", "test", "ext117") and p["r_hp"] >= hp_thr:
                r3.add(p["pool"])
            if p["q"] in twins and p["r_hp"] >= twin_thr:
                r4.add(p["pool"])
    if samepos is not None:
        for split, q, pool_stem, r in json.load(open(samepos)):
            if split in ("val", "test", "ext117") and r >= hp_thr:
                r3.add(pool_stem)
    drop["R3_content"] = r3 & ext_set
    drop["R4_twin_copies"] = r4 & ext_set
    missing = [x for x in exclude if x not in ext_set]
    if missing:
        raise ValueError(f"--exclude stems not in the external pool: {missing}")
    drop["extra"] = set(exclude)
    all_drop = set().union(*drop.values())
    keep_ext = [x for x in ext if x not in all_drop]
    mon: list[str] = []
    if monitor:
        mon = sorted(random.Random(monitor_seed).sample(keep_ext, monitor))
        keep_ext = [x for x in keep_ext if x not in set(mon)]
    keep_train = [x for x in train if x not in set(twins)]
    stems = keep_ext + keep_train
    bad = (set(stems) | set(mon)) & (val | test | e1)
    if bad:
        raise ValueError(f"val/test/E1 stems in the pool: {sorted(bad)[:10]}")
    if len(set(stems)) != len(stems):
        raise ValueError("a stem is both external and train")
    rels = [f"unlabeled/images_512/{x}.png" for x in keep_ext] + [f"labeled/images/{x}.png" for x in keep_train]
    mon_rels = [f"unlabeled/images_512/{x}.png" for x in mon]
    info = dict(external=len(ext), held_modules=len(held_mods),
                per_rule={k: len(v) for k, v in drop.items()},
                per_rule_unique={k: len(v - set().union(*(w for j, w in drop.items() if j != k))) for k, v in drop.items()},
                external_dropped=len(all_drop), monitor=len(mon), external_kept=len(keep_ext), train=len(train),
                twins=twins, train_kept=len(keep_train), total=len(rels), e1_checked=len(e1))
    return rels, mon_rels, info


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data_root", default="data")
    p.add_argument("--e1_manifest", default=None, help="ext117 manifest.csv (stem, in_external_pool, ...)")
    p.add_argument("--neardup", default=None, help="neardup.json (hp_pairs)")
    p.add_argument("--samepos", default=None, help="samepos_pool.json ([split, query, pool, r])")
    p.add_argument("--hp_thr", type=float, default=0.85)
    p.add_argument("--twin_thr", type=float, default=0.95)
    p.add_argument("--exclude", default="", help="comma list of extra external stems to drop")
    p.add_argument("--monitor", type=int, default=0, help="pool cells held out for the reconstruction monitor")
    p.add_argument("--monitor_seed", type=int, default=0)
    p.add_argument("--out", required=True)
    p.add_argument("--monitor_out", default=None)
    a = p.parse_args()
    rels, mon, info = build(Path(a.data_root), Path(a.e1_manifest) if a.e1_manifest else None,
                            [x for x in a.exclude.split(",") if x], Path(a.neardup) if a.neardup else None,
                            Path(a.samepos) if a.samepos else None, a.hp_thr, a.twin_thr, a.monitor, a.monitor_seed)
    missing = [r for r in rels + mon if not (Path(a.data_root) / r).exists()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} listed images missing, e.g. {missing[:3]}")
    Path(a.out).write_text("".join(r + "\n" for r in rels))
    print(json.dumps(info, indent=1))
    print("list md5", hashlib.md5(Path(a.out).read_bytes()).hexdigest(), a.out)
    if a.monitor_out:
        Path(a.monitor_out).write_text("".join(r + "\n" for r in mon))
        print("monitor md5", hashlib.md5(Path(a.monitor_out).read_bytes()).hexdigest(), a.monitor_out)


if __name__ == "__main__":
    main()
