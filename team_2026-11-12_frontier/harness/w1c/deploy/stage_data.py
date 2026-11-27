#!/usr/bin/env python3
"""Stage the cv02 data deploy on gaint (read-only on every source; writes only the new stage dir).
Out: <stage>/bench_data/{labeled/{images,masks_escdd}, masks_v11/{masks,masks_strict,ignore,MANIFEST.md5}, meta/, DEPLOY.md5}
holding ONLY the 532 pool stems (legacy train.txt + val.txt; stems md5 pinned = cv5v2.json pool.stems_md5).
Asserts: pool 532 unique, stems md5; 0 pool stems in forbidden_v1.txt or legacy test.txt; every copied file md5 = source;
masks_v11/MANIFEST.md5 = exactly the lines of gaint's MANIFEST.md5 for the 3 x 532 pool files; 0 staged png whose stem is
forbidden or in legacy test.txt; refuses an existing stage dir. Prints counts and the DEPLOY.md5 md5.
Usage: python3 -I stage_data.py <stage dir> <legacy splits dir>
"""
import hashlib, json, os, shutil, sys
from pathlib import Path

LAB = Path("/home/noob/work/el-fault-detection/data/labeled")
BD = Path("/home/noob/work/bench_data")
POOL_MD5 = "d374fd843598f10fd4ba9101435986c8"
META = {"cv5v2.json": "441d118f865d5642dd6a5e2be80ec753", "cv5v2_groups.tsv": "e44f06684df50607f4660d8d17e568ed",
        "forbidden_v1.txt": "9bb4d919fc16b5b394ce6d71f53903a6", "cells.tsv": "a50521b4d0648766b28cc297869603ec"}


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def lines(p):
    return [l.strip() for l in open(p) if l.strip()]


def main(stage, spl):
    out = Path(stage) / "bench_data"
    assert not out.exists(), f"{out} exists (no overwrite)"
    spl = Path(spl)
    pool = lines(spl / "train.txt") + lines(spl / "val.txt")
    assert hashlib.md5(("\n".join(pool) + "\n").encode()).hexdigest() == POOL_MD5, "pool stems md5"
    assert len(pool) == 532 and len(set(pool)) == 532, len(pool)
    for f, m in META.items():
        assert md5(BD / "meta" / f) == m, f
    forb = set(lines(BD / "meta" / "forbidden_v1.txt")) | set(lines(spl / "test.txt"))
    assert len(set(pool) & forb) == 0, "pool holds forbidden stems"
    pairs = []
    for s in pool:
        pairs += [(LAB / "images" / f"{s}.png", f"labeled/images/{s}.png"),
                  (LAB / "masks_escdd" / f"{s}.png", f"labeled/masks_escdd/{s}.png")]
        for d in ("masks", "masks_strict", "ignore"):
            pairs.append((BD / "masks_v11" / d / f"{s}.png", f"masks_v11/{d}/{s}.png"))
    for f in META:
        pairs.append((BD / "meta" / f, f"meta/{f}"))
    pairs.append((BD / "meta" / "META.md5", "meta/META.md5"))
    out.mkdir(parents=True)
    for src, rel in pairs:
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        assert md5(dst) == md5(src), rel
    want = {f"{d}/{s}.png" for s in pool for d in ("masks", "masks_strict", "ignore")}
    man = [l for l in open(BD / "masks_v11" / "MANIFEST.md5") if l.split(None, 1)[1].strip() in want]
    assert len(man) == 3 * 532, len(man)
    (out / "masks_v11" / "MANIFEST.md5").write_text("".join(man))
    bad = [p for p in out.rglob("*.png") if p.stem in forb]
    assert not bad, bad[:3]
    stems = {p.stem for p in out.rglob("*.png")}
    assert stems == set(pool), (len(stems), len(set(pool)))
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    (out / "DEPLOY.md5").write_text("".join(f"{md5(out / f)}  {f}\n" for f in files))
    n = {d: len(list((out / d).iterdir())) for d in ("labeled/images", "labeled/masks_escdd", "masks_v11/masks",
                                                     "masks_v11/masks_strict", "masks_v11/ignore", "meta")}
    print(f"staged {out}: {n}; png stems {len(stems)} = pool 532; forbidden / test stems staged 0; "
          f"MANIFEST.md5 {len(man)} lines (subset of gaint's), md5 {md5(out / 'masks_v11' / 'MANIFEST.md5')}; "
          f"DEPLOY.md5 {len(files)} files, md5 {md5(out / 'DEPLOY.md5')}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
