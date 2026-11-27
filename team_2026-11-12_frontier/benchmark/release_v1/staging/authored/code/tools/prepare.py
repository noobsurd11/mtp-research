#!/usr/bin/env python3
"""Release helper (release_v1, 22 Nov 2026). Stdlib + numpy + Pillow. Three steps, each checked against pinned md5s:

  legacy-lists --lists LISTS --out DIR
      writes DIR/{train,val,test}.txt (the BenchmarkEL dataset_20211104 split, 478 / 54 / 50) from LISTS/legacy.json and
      checks each file's md5 against legacy.json source_lists. make_masks_v11.py reads them as <datasets>/splits_benchmark.
  cv-roots --lists LISTS --split cv5v3 --out ROOTS
      writes ROOTS/<split>_v11_f<k>/splits/{train,val,test}.txt from LISTS/<split>.json (val = test = held-out fold k) and
      checks every list md5 against the JSON. Point BENCH_CV5V3_ROOTS (or BENCH_CV5V2_ROOTS) at ROOTS.
  check-v11 --lists LISTS --masks V11_DIR
      compares the pixel md5 (md5 of the raw uint8 512 x 512 array) of V11_DIR/masks/<stem>.png and masks_strict/<stem>.png
      with LISTS/labels_v11/MANIFEST_pool532.tsv for the 532 pool cells. Prints the number of matches and mismatches.
"""
import argparse, hashlib, json, sys
from pathlib import Path


def lmd5(stems):
    return hashlib.md5(("\n".join(stems) + "\n").encode()).hexdigest()


def write(p: Path, stems, want: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        sys.exit(f"refusing to overwrite {p}")
    p.write_text("\n".join(stems) + "\n")
    got = hashlib.md5(p.read_bytes()).hexdigest()
    assert got == want, f"{p}: md5 {got} != {want}"


def legacy_lists(a):
    d = json.load(open(Path(a.lists) / "legacy.json"))
    f, src = d["folds"][0], d["source_lists"]
    out = Path(a.out)
    write(out / "train.txt", f["train"], src["train_txt_md5"])
    write(out / "val.txt", f["heldout"], src["val_txt_md5"])
    write(out / "test.txt", d["sealed_sets"]["test50"]["stems"], src["test_txt_md5"])
    print(f"wrote train / val / test lists (478 / 54 / 50) to {out}; md5s match legacy.json")


def cv_roots(a):
    d = json.load(open(Path(a.lists) / f"{a.split}.json"))
    for f in d["folds"]:
        k = f["id"] if isinstance(f["id"], int) else int(str(f["id"]).lstrip("f"))
        sp = Path(a.out) / f"{a.split}_v11_f{k}" / "splits"
        assert lmd5(f["train"]) == f["train_md5"] and lmd5(f["heldout"]) == f["heldout_md5"], k
        write(sp / "train.txt", f["train"], f["train_md5"])
        for n in ("val.txt", "test.txt"):
            write(sp / n, f["heldout"], f["heldout_md5"])
        print(f"fold {k}: train {len(f['train'])}, held out {len(f['heldout'])}")


def check_v11(a):
    import numpy as np
    from PIL import Image

    def pmd5(p):
        m = np.array(Image.open(p))
        m = m[..., 0] if m.ndim == 3 else m
        assert m.shape == (512, 512), (p, m.shape)
        return hashlib.md5(np.ascontiguousarray(m, dtype=np.uint8).tobytes()).hexdigest()

    rows = [l.rstrip("\n").split("\t") for l in open(Path(a.lists) / "labels_v11" / "MANIFEST_pool532.tsv")]
    h = rows[0]
    ok = bad = 0
    for r in rows[1:]:
        r = dict(zip(h, r))
        for sub, col in (("masks", "v11_pixmd5"), ("masks_strict", "v11_strict_pixmd5")):
            if pmd5(Path(a.masks) / sub / f"{r['stem']}.png") == r[col]:
                ok += 1
            else:
                bad += 1
                print("MISMATCH", sub, r["stem"])
    print(f"check-v11: {len(rows) - 1} pool cells, {ok} files match, {bad} mismatch")
    sys.exit(1 if bad else 0)


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("legacy-lists"); p.add_argument("--lists", required=True); p.add_argument("--out", required=True)
p = sub.add_parser("cv-roots"); p.add_argument("--lists", required=True); p.add_argument("--out", required=True)
p.add_argument("--split", default="cv5v3", choices=("cv5v3", "cv5v2"))
p = sub.add_parser("check-v11"); p.add_argument("--lists", required=True); p.add_argument("--masks", required=True)
a = ap.parse_args()
{"legacy-lists": legacy_lists, "cv-roots": cv_roots, "check-v11": check_v11}[a.cmd](a)
