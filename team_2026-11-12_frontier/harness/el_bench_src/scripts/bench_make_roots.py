"""elbench data roots from a split definition (benchmark/splits/<name>.json, format el_bench_split/1).
= b6_make_roots.py fe70fbaf generalised: the folds come from the JSON (not b6_folds.tsv), the groups from the split's own
groups file, the forbidden list from forbidden_v1.txt; optional per-root mask link folder for label sets that differ
between train and held-out cells (v1.1: train -> masks with ignore 255, held-out -> masks_strict).

Root <out>/<name>_<tag>_f<k> (k = fold index):
  splits/train.txt  fold k 'train' list of the JSON (pool order: legacy train.txt then val.txt)
  splits/val.txt    fold k 'heldout' list
  splits/test.txt   = val.txt (byte-identical): the trainer's end-of-run TEST pass sees the held-out fold only
  labeled           symlink to --labeled (images; and masks_escdd for cards with data.mask_subdir=labeled/masks_escdd)
  <link_dir>/       only with --train-masks / --heldout-masks: one symlink per pool stem, <stem>.png -> the train or
                    held-out mask file (absolute target). Cards then use data.mask_subdir=<link_dir> (resolved as
                    <data.root>/<link_dir> by scripts/train.py).
  SPLITS.md5        md5sum lines of the three split files (md5sum -c from the root)
  DATA_MANIFEST.md5 md5sum lines of labeled/images/<stem>.png and of the mask file each stem reads (532 stems, sorted)
  MASKLINKS.tsv     only with a link folder: stem, role (train / heldout), link target
train.py reads only <root>/splits/{train,val,test}.txt, <root>/labeled/images and <root>/<data.mask_subdir>.

Asserts (any failure stops before anything is written): md5 of the JSON, groups, forbidden list and the legacy split
files (pinned below or given); pool = legacy train.txt + val.txt in that order (stems md5 = JSON pool.stems_md5); per
fold: list md5s = the JSON's, train and held-out disjoint, union = pool, both in pool order; held-outs partition the
pool; groups file folds = the JSON's held-out folds; no group in train and held-out of any fold; 0 forbidden stems in the
pool; every image and mask file present. After writing: re-read every split file and link from disk and re-assert (incl.
link targets), md5sum -c both manifests. Refuses to overwrite an existing root. Writes <out>/ROOTS_<name>_<tag>.md5.
CPU only, stdlib only.

Usage: python scripts/bench_make_roots.py --split cv5v2.json --groups cv5v2_groups.tsv --forbidden forbidden_v1.txt
         --legacy-splits <dir with train/val/test.txt> --labeled <labeled> --out <roots dir> --tag v11
         [--train-masks DIR --heldout-masks DIR --link-dir masks_v11]   (no mask args: masks = labeled/masks_escdd)
       python scripts/bench_make_roots.py ... --check   (re-run every assert on existing roots; writes nothing)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PINNED = {"cv5v2.json": "441d118f865d5642dd6a5e2be80ec753", "cv5v2_groups.tsv": "e44f06684df50607f4660d8d17e568ed",
          "forbidden_v1.txt": "9bb4d919fc16b5b394ce6d71f53903a6"}
LEGACY_MD5 = {"train": "842f27c418106a2095fa642daafec3fc", "val": "9dcccf00662dfca750f0b46628f8d5bb",
              "test": "a31fad14fa27ee28e2a2319b8976aba3"}
BASE_MASKS = "masks_escdd"


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lmd5(stems: list[str]) -> str:
    return hashlib.md5(("\n".join(stems) + "\n").encode()).hexdigest()


def stems_of(p: Path) -> list[str]:
    return [l.strip() for l in open(p) if l.strip()]


def tsv(p: Path) -> list[dict]:
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True)
    ap.add_argument("--groups", required=True)
    ap.add_argument("--forbidden", required=True)
    ap.add_argument("--legacy-splits", required=True)
    ap.add_argument("--labeled", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True, help="label-set tag in the root name, e.g. v11 or v1")
    ap.add_argument("--train-masks", default=None)
    ap.add_argument("--heldout-masks", default=None)
    ap.add_argument("--link-dir", default=None)
    ap.add_argument("--check", action="store_true", help="verify existing roots; write nothing")
    a = ap.parse_args()
    links = a.train_masks is not None
    assert links == (a.heldout_masks is not None) == (a.link_dir is not None), "give all three mask args or none"
    if links:
        assert "/" not in a.link_dir and a.link_dir not in ("labeled", "splits"), "link dir: one plain name"
    out, lab, spl = Path(a.out).resolve(), Path(a.labeled).resolve(), Path(a.legacy_splits)
    tm = Path(a.train_masks).resolve() if links else None
    hm = Path(a.heldout_masks).resolve() if links else None

    # ---- inputs ----
    for p in (a.split, a.groups, a.forbidden):
        n = Path(p).name
        assert n in PINNED and md5(Path(p)) == PINNED[n], f"{p} md5 != pinned"
    for k, v in LEGACY_MD5.items():
        assert md5(spl / f"{k}.txt") == v, f"legacy {k}.txt md5"
    sd = json.loads(Path(a.split).read_text())
    assert sd["format"] == "el_bench_split/1", "split format"
    name = sd["name"]
    tr, va, te = (stems_of(spl / f"{k}.txt") for k in ("train", "val", "test"))
    assert (len(tr), len(va), len(te)) == (478, 54, 50) and len(set(tr + va + te)) == 582
    pool = tr + va
    assert len(pool) == sd["pool"]["n"] == 532 and lmd5(pool) == sd["pool"]["stems_md5"], "pool"
    pos = {s: i for i, s in enumerate(pool)}
    forbidden = set(stems_of(Path(a.forbidden)))
    assert len(forbidden) == sd["forbidden"]["n"] == 167 and set(te) <= forbidden, "forbidden list"
    assert not set(pool) & forbidden, "forbidden stem in the pool"
    folds = sd["folds"]
    fold_of: dict[str, int] = {}
    for k, f in enumerate(folds):
        assert f["id"] == f"f{k}", "fold ids f0..f4 in order"
        t, h = f["train"], f["heldout"]
        assert lmd5(t) == f["train_md5"] and lmd5(h) == f["heldout_md5"], f"fold {k} list md5"
        assert (len(t), len(h)) == (f["n_train"], f["n_heldout"]), f"fold {k} counts"
        assert not set(t) & set(h) and set(t) | set(h) == set(pool) and len(t) + len(h) == 532, f"fold {k} train / held-out"
        assert t == sorted(t, key=pos.get) and h == sorted(h, key=pos.get), f"fold {k} pool order"
        for s in h:
            assert s not in fold_of, f"{s} held out twice"
            fold_of[s] = k
    assert set(fold_of) == set(pool), "held-out folds do not partition the pool"
    g = tsv(Path(a.groups))
    grp = {r["stem"]: r["group"] for r in g}
    assert len(g) == 532 and set(grp) == set(pool), "groups file stems"
    assert all(int(r["fold"]) == fold_of[r["stem"]] for r in g), "groups file folds != JSON folds"
    gf: dict[str, set] = {}
    for s, k in fold_of.items():
        gf.setdefault(grp[s], set()).add(k)
    assert all(len(v) == 1 for v in gf.values()), "a group is split across folds"
    for s in pool:
        assert (lab / "images" / f"{s}.png").is_file(), s
        if links:
            assert (tm / f"{s}.png").is_file() and (hm / f"{s}.png").is_file(), s
        else:
            assert (lab / BASE_MASKS / f"{s}.png").is_file(), s
    roots = [out / f"{name}_{a.tag}_f{k}" for k in range(len(folds))]
    rmd5 = out / f"ROOTS_{name}_{a.tag}.md5"
    mask_rel = (lambda s: f"{a.link_dir}/{s}.png") if links else (lambda s: f"labeled/{BASE_MASKS}/{s}.png")

    # ---- write ----
    if not a.check:
        for r in roots:
            assert not r.exists() and not r.is_symlink(), f"{r} exists (no overwrite)"
        assert not rmd5.exists(), f"{rmd5} exists (no overwrite)"
        out.mkdir(parents=True, exist_ok=True)
        for k, r in enumerate(roots):
            f = folds[k]
            (r / "splits").mkdir(parents=True)
            (r / "splits" / "train.txt").write_text("\n".join(f["train"]) + "\n")
            (r / "splits" / "val.txt").write_text("\n".join(f["heldout"]) + "\n")
            (r / "splits" / "test.txt").write_text("\n".join(f["heldout"]) + "\n")
            os.symlink(lab, r / "labeled")
            if links:
                (r / a.link_dir).mkdir()
                rows = []
                for s in pool:
                    role, src = ("heldout", hm) if fold_of[s] == k else ("train", tm)
                    os.symlink(src / f"{s}.png", r / a.link_dir / f"{s}.png")
                    rows.append(f"{s}\t{role}\t{src / f'{s}.png'}\n")
                (r / "MASKLINKS.tsv").write_text("stem\trole\ttarget\n" + "".join(rows))
            (r / "SPLITS.md5").write_text("".join(f"{md5(r / 'splits' / f'{n}.txt')}  splits/{n}.txt\n"
                                                  for n in ("train", "val", "test")))
            man = []
            for s in sorted(pool):
                man.append(f"{md5(lab / 'images' / f'{s}.png')}  labeled/images/{s}.png\n")
                man.append(f"{md5(r / mask_rel(s))}  {mask_rel(s)}\n")
            (r / "DATA_MANIFEST.md5").write_text("".join(man))

    # ---- re-read and re-assert from disk ----
    union, rows = [], []
    for k, r in enumerate(roots):
        f = folds[k]
        t, v, s_ = (stems_of(r / "splits" / f"{n}.txt") for n in ("train", "val", "test"))
        assert (r / "splits" / "val.txt").read_bytes() == (r / "splits" / "test.txt").read_bytes(), "val != test"
        assert t == f["train"] and v == f["heldout"], f"{r}: lists != JSON fold {k}"
        assert md5(r / "splits" / "train.txt") == f["train_md5"] and md5(r / "splits" / "test.txt") == f["heldout_md5"]
        assert not set(t) & set(v) and set(t) | set(v) == set(pool), "train / held-out"
        assert not (set(t) | set(v) | set(s_)) & forbidden, "forbidden stem in a split file"
        assert not {grp[x] for x in t} & {grp[x] for x in v}, "group in train and held-out"
        assert (r / "labeled").is_symlink() and Path(os.readlink(r / "labeled")) == lab, "labeled link"
        if links:
            ents = sorted(os.listdir(r / a.link_dir))
            assert ents == sorted(f"{s}.png" for s in pool), "link dir entries != pool"
            for s in pool:
                p = r / a.link_dir / f"{s}.png"
                want = (hm if s in set(v) else tm) / f"{s}.png"
                assert p.is_symlink() and Path(os.readlink(p)) == want and p.is_file(), f"link {p}"
        for m in ("SPLITS.md5", "DATA_MANIFEST.md5"):
            rc = subprocess.run(["md5sum", "-c", "--quiet", m], cwd=r).returncode
            assert rc == 0, f"{r}/{m} md5sum -c rc {rc}"
        union += v
        rows.append((r.name, len(t), len(v), len({grp[x] for x in v}), md5(r / "SPLITS.md5")[:8],
                     md5(r / "splits" / "train.txt")[:8], md5(r / "splits" / "test.txt")[:8],
                     md5(r / "DATA_MANIFEST.md5")[:8]))
    assert sorted(union) == sorted(pool), "held-out folds do not partition the pool"
    files = ["splits/train.txt", "splits/val.txt", "splits/test.txt", "SPLITS.md5", "DATA_MANIFEST.md5"] + \
        (["MASKLINKS.tsv"] if links else [])
    text = "".join(f"{md5(r / n)}  {r.name}/{n}\n" for r in roots for n in files)
    if a.check:
        assert rmd5.read_text() == text, f"{rmd5} != files on disk"
        print(f"CHECK OK {rmd5.name} {md5(rmd5)}")
    else:
        rmd5.write_text(text)
    print("root\ttrain\theldout\tgroups\tSPLITS.md5\ttrain.txt\ttest.txt(=val.txt)\tDATA_MANIFEST.md5")
    for row in rows:
        print("\t".join(map(str, row)))
    print(f"{rmd5.name} {md5(rmd5)}; masks: " + (f"{a.link_dir}/ links, train -> {tm}, held-out -> {hm}" if links
                                                  else f"labeled/{BASE_MASKS}"))
    print(f"asserts: OK (0 forbidden of {len(forbidden)}; 0 of {len(gf)} groups split; held-outs partition {len(pool)};"
          f" lists = {name}.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
