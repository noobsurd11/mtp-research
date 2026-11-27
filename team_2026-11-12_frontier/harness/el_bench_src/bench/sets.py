"""elbench cell sets: names -> (ordered stems, image dir, GT mask dir, ignore dir or None). Stdlib only.

Paths are gaint's; override any of them with the environment (BENCH_LABELED, BENCH_LEGACY_SPLITS, BENCH_CV_ROOTS,
BENCH_EXT, BENCH_RF) on another machine. Order matters for exact identity with the legacy scorers (batch composition):
  val54 / test50   sorted(<legacy splits>/<split>.txt)            (m0_audit / rescore convention)
  cv5v1_f<k>       <BENCH_CV_ROOTS>/b6_root_<k>/splits/test.txt, file order   (b6_score convention)
  cv5v2_f<k>       <BENCH_CV5V2_ROOTS>/cv5v2_v11_f<k>/splits/test.txt, file order (= cv5v2.json held-out k, md5 pinned);
                   GT = label set v1.1: <BENCH_MASKS_V11>/masks (255 at ignore px) + <BENCH_MASKS_V11>/ignore (not scored)
  e1_106 / rf106   <dir>/stems_eval.txt, file order                (m0_audit ext / calib convention)
  f51 / h36        bench/sets/<name>.txt (sorted; from benchmark/out/cells.tsv rfset, md5 in SET_LIST_MD5)
GT for the 582 legacy cells is <labeled>/masks_escdd (handbook 14: gaint's own escdd_masks/test holds scuff at 2 cells,
so it is never used). E1 and rf have masks/ and ignore/ (ignore > 0 = not scored).
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .dumpfmt import check_set

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
LABELED = Path(os.environ.get("BENCH_LABELED", "/home/noob/work/el-fault-detection/data/labeled"))
LEGACY_SPLITS = Path(os.environ.get("BENCH_LEGACY_SPLITS", str(REPO / "data" / "splits")))
CV_ROOTS = {"cv5v1": Path(os.environ.get("BENCH_CV_ROOTS", "/home/noob/work/b6")),
            "cv5v2": Path(os.environ.get("BENCH_CV5V2_ROOTS", "/home/noob/work/bench_data/roots"))}
CV_ROOT_NAME = {"cv5v1": "b6_root_{k}", "cv5v2": "cv5v2_v11_f{k}"}
MASKS_V11 = Path(os.environ.get("BENCH_MASKS_V11", "/home/noob/work/bench_data/masks_v11"))
# held-out list md5 per fold (cv5v2.json 441d118f folds[k].heldout_md5); cv5v1 lists are checked by the b6 roots' SPLITS.md5
CV_LIST_MD5 = {"cv5v2": ("7e107038577873e39ae46e61de0c2e03", "975b880051860db93ac34827079e8098",
                         "a82e08cc5461ec0c2a31a34ddc416a36", "769baffcb380ad69908b9a2a2b859553",
                         "40cda7efa17060cf602c28534674e1e0")}
EXT = Path(os.environ.get("BENCH_EXT", "/home/noob/work/el_f1/reports/f1/ext117"))
RF = Path(os.environ.get("BENCH_RF", "/home/noob/work/calib/data/rf"))
# md5 of the list files each set is read from (gaint values; checked when a set is resolved)
LEGACY_MD5 = {"train": "842f27c418106a2095fa642daafec3fc", "val": "9dcccf00662dfca750f0b46628f8d5bb",
              "test": "a31fad14"}  # test: prefix only (sealed; checked by prefix)
SET_LIST_MD5 = {"f51": "a2abc5f43f52060b2f0db6a65b8d8d3c", "h36": "3d3593b95f9389712f2c028ff98c5971"}
NOISY = {"test50": ["CSIR_00070_r8_c4"]}          # the fixed noisy-cell list per set (BRIEF s2); others: none yet
TWINS = {"test50": ["CFVS_00006_r5_c5", "CFVS_00033_r8_c4", "CFVS_00035_r8_c4", "CFVS_00042_r8_c4",
                    "CFVS_00018_r4_c4", "CFVS_00027_r4_c4", "ARTS_00020_r5_c1"]}   # m0_analyze TWINS
SIZES = {"val54": 54, "test50": 50, "e1_106": 106, "rf106": 106, "f51": 51, "h36": 36}


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _lines(p: Path) -> list[str]:
    return [l.strip() for l in open(p) if l.strip()]


def resolve(name: str, opening: str | None = None) -> dict:
    """{'name', 'kind', 'stems', 'images', 'masks', 'ignore', 'list_file', 'list_md5'} for a set name.
    Sealed sets need an opening protocol name (dumpfmt.check_set)."""
    kind = check_set(name, opening)
    ign = None
    if name in ("val54", "test50"):
        sp = {"val54": "val", "test50": "test"}[name]
        lf = LEGACY_SPLITS / f"{sp}.txt"
        m = _md5(lf)
        assert m.startswith(LEGACY_MD5[sp]), (lf, m)
        stems = sorted(_lines(lf))
        images, masks = LABELED / "images", LABELED / "masks_escdd"
    elif name.startswith("cv"):
        cv, k = name.rsplit("_f", 1)
        assert cv in CV_ROOTS, f"unknown CV split definition {cv}"
        lf = CV_ROOTS[cv] / CV_ROOT_NAME[cv].format(k=int(k)) / "splits" / "test.txt"
        m = _md5(lf)
        stems = _lines(lf)
        images, masks = LABELED / "images", LABELED / "masks_escdd"
        if cv in CV_LIST_MD5:
            assert m == CV_LIST_MD5[cv][int(k)], (lf, m)
        if cv == "cv5v2":
            masks, ign = MASKS_V11 / "masks", MASKS_V11 / "ignore"
    elif name in ("e1_106", "rf106"):
        d = EXT if name == "e1_106" else RF
        lf = d / "stems_eval.txt"
        m = _md5(lf)
        stems = _lines(lf)
        images, masks, ign = d / "images", d / "masks", d / "ignore"
    elif name in ("f51", "h36"):
        lf = HERE / "sets" / f"{name}.txt"
        m = _md5(lf)
        assert m == SET_LIST_MD5[name], (lf, m)
        stems = _lines(lf)
        assert set(stems) <= set(_lines(RF / "stems_eval.txt")), f"{name} has stems outside rf stems_eval"
        images, masks, ign = RF / "images", RF / "masks", RF / "ignore"
    else:
        raise ValueError(name)
    assert len(set(stems)) == len(stems), f"{name}: duplicate stems"
    if name in SIZES:
        assert len(stems) == SIZES[name], (name, len(stems))
    return {"name": name, "kind": kind, "stems": stems, "images": images, "masks": masks, "ignore": ign,
            "list_file": str(lf), "list_md5": m}


def stems_md5(stems: list[str]) -> str:
    return hashlib.md5(("\n".join(stems) + "\n").encode()).hexdigest()


def load_celltypes(path: str | Path) -> dict[str, str]:
    """TSV with columns stem, celltype (header line). Returns {stem: celltype}."""
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]
    i_s, i_c = rows[0].index("stem"), rows[0].index("celltype")
    return {r[i_s]: (r[i_c] or "unknown") for r in rows[1:]}
