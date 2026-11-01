"""B6 fold roots (protocol_B6 v1.0.1 s3 and s8.2): one data root per held-out fold for e544133's scripts/train.py.

Root k (k = 0..4, the fold numbers of results/b6/b6_folds.tsv):
  splits/train.txt  the 532 train + val cells NOT in fold k, in the original train.txt order, then val.txt order
  splits/val.txt    fold k's cells (same order rule)
  splits/test.txt   = val.txt (byte-identical): the trainer's unconditional end-of-run TEST pass sees fold k only
  labeled           symlink to --labeled (gaint: el_f3 data/labeled); cv02 gets a fresh copy of the 532 stems (runner)
  SPLITS.md5        md5sum lines of the three split files (relative paths; md5sum -c from the root)
  DATA_MANIFEST.md5 md5sum lines of labeled/images/<stem>.png and labeled/masks_escdd/<stem>.png, 532 stems (sorted)
train.py reads only <root>/splits/{train,val,test}.txt and <root>/labeled/{images,<mask_subdir>} (l.329-466 at e544133).

Asserts (any failure stops before anything is written): input md5s; 532 stems = train.txt + val.txt; phys_group of every
stem = judge's groups file; no group split across folds; 0 stems of the real test.txt and 0 of ext117 (stems_eval 106 and
stems 117) in the pool; every image / mask present. After writing: re-read every split file from disk and re-assert
(train and held-out disjoint, union 532, held-out = fold k, 0 forbidden stems in any file), and md5sum -c both manifests.
Writes b6_forbidden.txt (sorted real-test + ext117 stems; the scorer's refusal list) and ROOTS.md5 in --out.
CPU only, no torch. Refuses to overwrite an existing root.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

FOLDS_MD5 = "e2cafce1509bb0f2b95ce6d5db397caf"
GROUPS_MD5 = "5ff33e20d34567c331a1eca56bfbac9b"
SPLIT_MD5 = {"train": "842f27c418106a2095fa642daafec3fc", "val": "9dcccf00662dfca750f0b46628f8d5bb",
             "test": "a31fad14fa27ee28e2a2319b8976aba3"}
E1_EVAL_MD5 = "5266806b559f74bcf9eae167bb076b95"
MASK_SUBDIR = "masks_escdd"
NFOLD = 5


def md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stems_of(p: Path) -> list[str]:
    return [l.strip() for l in open(p) if l.strip()]


def tsv(p: Path) -> list[dict]:
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", required=True)
    ap.add_argument("--groups", required=True)
    ap.add_argument("--splits", required=True, help="el_f3 data/splits (train / val / test .txt)")
    ap.add_argument("--labeled", required=True, help="el_f3 data/labeled (images + masks_escdd)")
    ap.add_argument("--e1-eval", required=True, help="ext117 stems_eval.txt (106)")
    ap.add_argument("--e1-all", required=True, help="ext117 stems.txt (117)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out, lab, spl = Path(a.out).resolve(), Path(a.labeled).resolve(), Path(a.splits)

    # ---- inputs ----
    assert md5(Path(a.folds)) == FOLDS_MD5, "folds md5"
    assert md5(Path(a.groups)) == GROUPS_MD5, "groups md5"
    for k, v in SPLIT_MD5.items():
        assert md5(spl / f"{k}.txt") == v, f"{k}.txt md5"
    assert md5(Path(a.e1_eval)) == E1_EVAL_MD5, "E1 stems_eval md5"
    tr, va, te = (stems_of(spl / f"{k}.txt") for k in ("train", "val", "test"))
    assert (len(tr), len(va), len(te)) == (478, 54, 50) and len(set(tr + va + te)) == 582
    e1 = stems_of(Path(a.e1_eval)) + stems_of(Path(a.e1_all))
    assert len(stems_of(Path(a.e1_eval))) == 106 and len(set(stems_of(Path(a.e1_all)))) == 117
    forbidden = sorted(set(te) | set(e1))

    folds = tsv(Path(a.folds))
    fold = {r["stem"]: int(r["fold"]) for r in folds}
    assert len(folds) == 532 == len(fold), "532 unique stems"
    assert set(fold) == set(tr) | set(va), "pool = train + val"
    assert all((r["split"] == "train") == (r["stem"] in set(tr)) for r in folds), "split column"
    assert set(fold.values()) == set(range(NFOLD)), "folds 0..4"
    grp = {r["stem"]: r["phys_group"] for r in tsv(Path(a.groups))}
    assert set(grp) == set(fold) and all(grp[s] == r["phys_group"] for s, r in ((r["stem"], r) for r in folds)), "groups"
    gf: dict[str, set] = {}
    for s, k in fold.items():
        gf.setdefault(grp[s], set()).add(k)
    assert all(len(v) == 1 for v in gf.values()), "a group is split across folds"
    assert not set(fold) & set(forbidden), "test / E1 stem in the pool"
    for s in fold:
        assert (lab / "images" / f"{s}.png").is_file() and (lab / MASK_SUBDIR / f"{s}.png").is_file(), s

    pool = tr + va  # original order: train.txt, then val.txt
    roots = [out / f"b6_root_{k}" for k in range(NFOLD)]
    for r in roots:
        assert not r.exists(), f"{r} exists (no overwrite)"

    # ---- write ----
    out.mkdir(parents=True, exist_ok=True)
    (out / "b6_forbidden.txt").write_text("\n".join(forbidden) + "\n")
    man = []
    for s in sorted(fold):
        for sub in ("images", MASK_SUBDIR):
            man.append(f"{md5(lab / sub / f'{s}.png')}  labeled/{sub}/{s}.png\n")
    for k, r in enumerate(roots):
        (r / "splits").mkdir(parents=True)
        held = [s for s in pool if fold[s] == k]
        trn = [s for s in pool if fold[s] != k]
        (r / "splits" / "train.txt").write_text("\n".join(trn) + "\n")
        (r / "splits" / "val.txt").write_text("\n".join(held) + "\n")
        (r / "splits" / "test.txt").write_text("\n".join(held) + "\n")
        os.symlink(lab, r / "labeled")
        (r / "SPLITS.md5").write_text("".join(f"{md5(r / 'splits' / f'{n}.txt')}  splits/{n}.txt\n"
                                              for n in ("train", "val", "test")))
        (r / "DATA_MANIFEST.md5").write_text("".join(man))

    # ---- re-read and re-assert from disk ----
    fb, union, rows = set(forbidden), [], []
    for k, r in enumerate(roots):
        t, v, s_ = (stems_of(r / "splits" / f"{n}.txt") for n in ("train", "val", "test"))
        assert (r / "splits" / "val.txt").read_bytes() == (r / "splits" / "test.txt").read_bytes(), "val != test"
        assert set(v) == {s for s in fold if fold[s] == k} and len(v) == len(set(v)), "held-out != fold k"
        assert not set(t) & set(v) and set(t) | set(v) == set(fold) and len(t) == len(set(t)), "train / held-out"
        assert not (set(t) | set(v) | set(s_)) & fb, "forbidden stem in a split file"
        assert not {grp[x] for x in t} & {grp[x] for x in v}, "group in train and held-out"
        for m in ("SPLITS.md5", "DATA_MANIFEST.md5"):
            rc = subprocess.run(["md5sum", "-c", "--quiet", m], cwd=r).returncode
            assert rc == 0, f"{r}/{m} md5sum -c rc {rc}"
        union += v
        rows.append((k, len(t), len(v), len({grp[x] for x in v}), md5(r / "SPLITS.md5"),
                     md5(r / "splits" / "train.txt"), md5(r / "splits" / "test.txt")))
    assert sorted(union) == sorted(fold), "held-out folds do not partition the pool"
    with open(out / "ROOTS.md5", "w") as f:
        for k, r in enumerate(roots):
            for n in ("splits/train.txt", "splits/val.txt", "splits/test.txt", "SPLITS.md5", "DATA_MANIFEST.md5"):
                f.write(f"{md5(r / n)}  b6_root_{k}/{n}\n")
        f.write(f"{md5(out / 'b6_forbidden.txt')}  b6_forbidden.txt\n")
    print("fold\ttrain\theldout\tgroups\tSPLITS.md5\ttrain.txt\ttest.txt(=val.txt)")
    for row in rows:
        print("\t".join(map(str, row)))
    print(f"DATA_MANIFEST.md5 {md5(roots[0] / 'DATA_MANIFEST.md5')} ({len(man)} lines, identical in all roots)")
    print(f"b6_forbidden.txt {md5(out / 'b6_forbidden.txt')} ({len(forbidden)} stems: test {len(te)} + ext117 "
          f"{len(set(e1))}); ROOTS.md5 {md5(out / 'ROOTS.md5')}")
    print("asserts: OK (0 test / 0 E1 stems in any root; 0 of", len(gf), "groups split; partition of 532)")


if __name__ == "__main__":
    sys.exit(main())
