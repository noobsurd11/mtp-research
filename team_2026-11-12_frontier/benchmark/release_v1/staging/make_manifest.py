#!/usr/bin/env python3
"""bench_release, 22 Nov 2026. release_v1/MANIFEST.tsv: one row per staged file (staged = yes) plus the candidates that were
considered and not staged (staged = no). md5 / bytes of the staged copy; source and source md5 from staging/sources.json.
Run after stage.py, stage_results.py and the README: python3 -I make_manifest.py"""
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = HERE.parent
OUT = REL / "files"
SRC = json.load(open(HERE / "sources.json"))

U = {  # licence references (verified by fetch on 22 Nov 2026 unless marked)
    "bel": "https://github.com/TheMakiran/BenchmarkELimages (no LICENSE file; GitHub API license null; README asks for citation only)",
    "esc": "https://huggingface.co/datasets/snt-ubix/escdd (card license: mit)",
    "elpv": "https://github.com/zae-bayern/elpv-dataset (images CC BY-NC-SA 4.0; code Apache-2.0)",
    "own": "project code / project lists; release licence not chosen (LICENCE_AUDIT D2)",
}
CLEAR_ID = ("clear", "identifiers, hashes, fold or group assignments and image-derived evidence made by the project; no image or "
            "label content", U["own"] + "; ids name BenchmarkEL files: " + U["bel"])
UNCLEAR_LBL = ("unclear", "holds statistics derived from BenchmarkEL label pixels (counts, classes); BenchmarkEL states no licence. "
               "S: counts are facts and low risk; ask the authors (EMAIL_PRATT_DRAFT)", U["bel"] + "; " + U["esc"])


def meta(p: str):
    """(what, terms_status, reason, licence_ref) for a staged path."""
    n = p.split("/")[-1]
    if p == "README.md":
        return ("release README", "clear", "written for the release", U["own"])
    if p.startswith("results/"):
        return ("baseline and final-model result tables (thesis tables T5, T6, T7a, T15, T8, T10, T11a; aggregates only)",
                "clear", "the project's own measurements; some rows used research-only weights (SegFormer MiT-B2), which "
                "its licence allows for research or evaluation", U["own"] + "; https://github.com/NVlabs/SegFormer/blob/master/LICENSE")
    if p.startswith("code/tools/"):
        return ("release helper: legacy lists, CV roots, v1.1 pixel-md5 check", "clear", "written for the release", U["own"])
    if p.startswith("code/benchmark_scripts/"):
        what = {"make_masks_v11.py": "mask-building script: label set v1.1 from public BenchmarkEL + E-SCDD masks",
                "corpus_build.py": "provenance: corpus census -> intermediate cell table",
                "groups_folds.py": "provenance: physical-module groups and draft folds",
                "make_splits.py": "provenance: cv5v2 / legacy split files (needs project-internal B6 folds to rerun)",
                "make_cells_table.py": "provenance: the 816-row cell table (needs project-internal inputs to rerun)"}[n]
        return (what, "clear", "project code; no third-party code inside", U["own"])
    if p.startswith("code/bench/sets/"):
        if n == "celltypes.tsv":
            return ("cell type per cell (816 rows; from mask spacing classes)",) + UNCLEAR_LBL
        what = {"do_not_train.txt": "stems never trained on (U4 pack, pool half-cells)", "e1_106_stems.txt": "E1 stem list (106)",
                "f51.txt": "E-SCDD _rf full-cell dev set (51 stems)", "h36.txt": "E-SCDD _rf half-cell dev set (36 stems)",
                "masks_v0_pool532.md5": "md5 of the 532 pool v0 masks (dataset_20211104 masks_coded)"}.get(
                    n, "E1 few-shot (T3b) fold list")
        return (what,) + CLEAR_ID
    if p.startswith("code/"):
        role = "scorer / read code" if not n.startswith("bench_make") and n != "cv5v3.py" else "provenance: cv5v3 split builder"
        return (role, "clear", "project code; 'copied from' notes refer to the project's own earlier files", U["own"])
    if n in ("cells.tsv",):
        return ("cell table, 816 rows x 29 columns; 156 sealed rows (test, E1) reduced to 14 identity columns",) + UNCLEAR_LBL
    if n in ("CHANGES_pool532.tsv",):
        return ("v1.1 edit list, pool cells only (38 rows)",) + UNCLEAR_LBL
    if n in ("cv5v2_check.txt", "cv5v3_check.txt"):
        return ("split check report (includes per-fold crack / inactive cell counts)",) + UNCLEAR_LBL
    if n == "MANIFEST_pool532.tsv":
        return ("v1.1 pixel md5s (v1, v1.1, v1.1 strict) for the 532 pool cells",) + CLEAR_ID
    if n == "CELLS_README.md":
        return ("column documentation of cells.tsv", "clear", "project text", U["own"])
    what = {"cv5v3.json": "final split: module-grouped 5-fold CV over the 532 pool cells (285 groups)",
            "cv5v3_groups.tsv": "cv5v3 bootstrap groups", "cv5v3_proposal.tsv": "provenance: cv5v3 proposal (builder input)",
            "cv5v2.json": "screen split cv5v2 (330 groups)", "cv5v2_groups.tsv": "cv5v2 bootstrap groups",
            "cv5v2_vs_b6.tsv": "cv5v2 diff against the earlier B6 folds (4 rows)",
            "legacy.json": "BenchmarkEL 478 / 54 / 50 split and the sealed test50 stem list",
            "forbidden_v1.txt": "167 stems no training list may contain", "dup_crossfold_v1.tsv": "2 same-cell pairs across cv5v2 folds",
            "score_exclude_v2.txt": "cv5v2 score-exclude list (91)", "score_exclude_v2c.txt": "cv5v2 score-exclude list (99)",
            "score_exclude_v3.txt": "cv5v2 clean-cell list in force (116 excluded, 416 scored)",
            "module_identity_v3.tsv": "physical-module identity of all 700 image ids",
            "pool532_manifest.tsv": "md5 of the 532 pool images (file and grey pixels)",
            "pool_t9_v2.txt": "unlabelled pool list after the leakage rules (4,949 stems)"}[n]
    return (what,) + CLEAR_ID


rows = []
for f in sorted(OUT.rglob("*")):
    if f.is_dir() or ".git" in f.parts:
        continue
    p = f.relative_to(OUT).as_posix()
    b = f.read_bytes()
    src, smd5 = SRC.get(p, ("written for the release (bench_release)", "-"))
    what, st, why, lic = meta(p)
    rows.append([f"files/{p}", hashlib.md5(b).hexdigest(), str(len(b)), what, src, smd5, "yes", st, why, lic])

NO = [
    ("benchmark/out/masks_v11/{masks,masks_strict,ignore}/*.png (1,746 files)", "v1.1 label masks", "forbidden",
     "release rule: masks are rebuilt by script, never shipped; derived from BenchmarkEL labels (no licence) and, for BMRK cells, "
     "from CC BY-NC-SA images", U["bel"] + "; " + U["elpv"]),
    ("dataset images (BenchmarkEL, E-SCDD, ELPV-derived BMRK, SDLE) and the unlabelled pool images", "images", "forbidden",
     "release rule: no images; BenchmarkEL states no licence; ELPV images are CC BY-NC-SA 4.0", U["bel"] + "; " + U["elpv"]),
    ("model checkpoints (C1, C2 full-pool models, all CV5 runs)", "trained weights", "forbidden",
     "release rule: no checkpoints; trained on BMRK cells (CC BY-NC-SA) and on ImageNet weights with unverified terms",
     U["elpv"] + "; https://huggingface.co/smp-hub/resnet34.imagenet (license: other)"),
    ("results/final_opening_read/read_e1/read.json, read_t50_v0/read.json, read_t50_v11/read.json", "per-cell scores of sealed sets",
     "forbidden", "release rule: no E1 or test50 per-cell data; aggregates only (results/BASELINES.md)", U["own"]),
    ("benchmark/cells.tsv label columns of the 156 sealed rows (test50, E1)", "label summaries of sealed cells", "forbidden",
     "release rule: no E1 or test50 labels; the staged cells.tsv keeps identity columns only (bench/udev.py SAFE_COLS)", U["own"]),
    ("benchmark/out/masks_v11/MANIFEST.tsv and CHANGES.tsv rows of the 50 test cells; SUMMARY.txt", "sealed label hashes and counts",
     "forbidden", "release rule: no test50 labels; staged as pool-only files", U["own"]),
    ("benchmark/scripts/t3b_counts.py", "E1 few-shot track counts", "clear",
     "not proposed: computes and prints E1 label statistics; out of the release scope", U["own"]),
    ("benchmark/scripts/label_checks.py, fine_texture_check.py", "analysis scripts", "clear",
     "not proposed: development analyses, not needed to rebuild or score", U["own"]),
    ("benchmark/PROTOCOL_v0.2.md", "protocol working text", "clear",
     "not proposed: internal working text full of team-file references; a public protocol text is owed (README gives the rules)", U["own"]),
    ("UCF-EL lists (datasets/splits_benchmark/ucf_el, extra-data track)", "extra-data track lists", "unclear",
     "not proposed: UCF-EL states no licence; the extra-data track redistributes nothing",
     "https://github.com/ucf-photovoltaics/UCF-EL-Defect (no LICENSE file; GitHub API license null)"),
    ("scripts/bench_infer.py and src/ (training and inference code)", "model code", "clear",
     "not proposed: outside 'scorer and read code'; the README gives the dump format any code can write (LICENCE_AUDIT D5)", U["own"]),
]
for path, what, st, why, lic in NO:
    rows.append([path, "-", "-", what, path.split(" ")[0], "-", "no", st, why, lic])

hdr = ["path", "md5", "bytes", "what", "source", "source_md5", "staged", "terms_status", "terms_reason", "licence_text_or_url"]
with open(REL / "MANIFEST.tsv", "w") as f:
    f.write("\t".join(hdr) + "\n")
    for r in rows:
        assert len(r) == len(hdr) and not any("\t" in x or "\n" in x for x in r)
        f.write("\t".join(r) + "\n")
st = {}
for r in rows:
    st.setdefault((r[6], r[7]), 0); st[(r[6], r[7])] += 1
print(f"MANIFEST.tsv: {len(rows)} rows; staged files {sum(r[6] == 'yes' for r in rows)}")
for k in sorted(st):
    print(f"  staged={k[0]} {k[1]}: {st[k]}")
