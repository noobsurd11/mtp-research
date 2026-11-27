#!/usr/bin/env python3
"""bench_release, 22 Nov 2026. Writes release_v1/SANITIZE.md from staging/substitutions.tsv, staging/sources.json and the staged
files. Run last (after any manual edit of staged files): python3 -I make_sanitize.py"""
import hashlib, json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage  # noqa: E402

HERE = Path(__file__).resolve().parent
REL = HERE.parent
OUT = REL / "files"
src = json.load(open(HERE / "sources.json"))
subs = [l.rstrip("\n").split("\t") for l in open(HERE / "substitutions.tsv")][1:]
md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()

WHY = {"team_path": "absolute path of the team folder (user name in the path)",
       "home_work": "absolute path under a user's home (user name)", "home_any": "any other home path",
       "tmp_path": "temporary path naming the user", "nas_path": "NAS path", "user_tilde": "home-relative dataset path",
       "host_A": "server name of the 1-GPU machine", "host_B": "server name of the 8-GPU lab machine",
       "gh_user": "GitHub user name", "user_1": "user name", "user_2": "user name", "ipv4": "IP address", "email": "email address"}
L = ["# SANITIZE: every change between the project's files and the staged release (bench_release, 22 Nov 2026)", "",
     "Tags: E = measured here. Staging code: `staging/stage.py`, `staging/stage_results.py` (rules applied to every staged text",
     "file, line by line, in the order below); this file is written by `staging/make_sanitize.py`.", "",
     "## 1. Rules", "", "| Rule | Pattern (regex) | Replacement | Why | Hits |", "|---|---|---|---|---|"]
cnt = {}
for s in subs:
    cnt[s[1]] = cnt.get(s[1], 0) + int(s[3])
for name, rx, rep in stage.RULES:
    L.append(f"| {name} | `{rx}` | `{rep}` | {WHY[name]} | {cnt.get(name, 0)} |")
L += ["", "machA = the 1-GPU machine (RTX PRO 4500), machB = the 8-GPU lab machine (RTX A6000). No IP address, email address,",
      "GitHub user name or NAS path occurred in the staged sources (0 hits).", "",
      f"## 2. Every substitution ({len(subs)} lines, {sum(int(s[3]) for s in subs)} substitutions)", "",
      "| Staged file | Rule | Line | Count |", "|---|---|---|---|"]
for s in sorted(subs, key=lambda t: (t[0], int(t[2]), t[1])):
    L.append(f"| `{s[0]}` | {s[1]} | {s[2]} | {s[3]} |")
L += ["", "## 3. Consistency edits (hand edits after the rules; E)", "",
      "The staged `lists/cells.tsv` and `lists/cv5v2.json` differ from the originals (sections 2 and 4), so two runtime md5 pins",
      "were moved to the staged files. Without them `w1read.load_exclude` (the score-exclude option) and `cellmeta.load_cells`",
      "refuse the staged table.", "",
      "| Staged file | Line | Before | After |", "|---|---|---|---|",
      "| `code/bench/cellmeta.py` | 34 | `CELLS_MD5 = \"a50521b4\"` | `CELLS_MD5 = \"8998b5f9\"` (comment names the original) |",
      "| `code/bench/udev.py` | 27 | `\"cells.tsv\": \"a50521b4...\", \"cv5v2.json\": \"441d118f...\"` | "
      "`\"cells.tsv\": \"8998b5f9...\", \"cv5v2.json\": \"ec840084...\"` (comment names the originals) |", "",
      "Not edited, on purpose: `code/scripts/bench_make_cv5v3.py` pins its original inputs (cv5v2.json 441d118f, the original",
      "build's mask MANIFEST.md5, a project results table). It is provenance only and does not run on the staged release.",
      "md5 values quoted inside staged files (for example `cv5v3.json` parent `file_md5` 441d118f and `cells_tsv_md5` a50521b4,",
      "`CELLS_README.md` 'md5 a50521b4', the inputs line of `cv5v3_check.txt`, comments in `bench/sets.py`) name the original",
      "files; section 5 maps them to the staged ones.", "",
      "## 4. Content reductions (E)", "",
      "| Staged file | Original | Change |", "|---|---|---|",
      "| `lists/cells.tsv` | `benchmark/cells.tsv` | the 156 rows with role test or E1 keep only the 14 identity columns of the code's own rule "
      "(`bench/udev.py` SAFE_COLS: stem, source, image_id, position, module_group, cell_id, n_images_of_cell, cell_type, label_source, "
      "mask_version, role, bench_set, rf_set, in_unlabelled_pool); 1,727 values blanked; no value was printed while doing it |",
      "| `lists/labels_v11/MANIFEST_pool532.tsv` | `benchmark/out/masks_v11/MANIFEST.tsv` | 50 test rows dropped; 532 train + val rows kept |",
      "| `lists/labels_v11/CHANGES_pool532.tsv` | `benchmark/out/masks_v11/CHANGES.tsv` | 2 test rows dropped; 38 train rows kept |",
      "| `results/BASELINES.md` | `thesis/THESIS_TABLES.md` | sections T5, T6, T7a, T15, T8, T10, T11a copied verbatim under a new header; "
      "test50 tables and all other sections left out |", "",
      "## 5. Original and staged md5 of every changed file (E)", "",
      "| Staged file | Source | Source md5 | Staged md5 |", "|---|---|---|---|"]
same = 0
for p, (s, sm) in sorted(src.items()):
    sm2 = md5(OUT / p)
    if sm2 != sm:
        L.append(f"| `{p}` | `{s}` | {sm} | {sm2} |")
    else:
        same += 1
new = sorted(f.relative_to(OUT).as_posix() for f in OUT.rglob("*") if f.is_file() and ".git" not in f.parts
             and f.relative_to(OUT).as_posix() not in src)
L += ["", f"{same} staged files are byte copies of their source (md5 equal). Files written for the release, with no source: "
      + ", ".join(f"`{n}`" for n in new) + ".", "",
      "## 6. Never copied", "",
      "No credential, `.env`, ssh configuration, token, dataset image, mask, checkpoint, per-cell sealed result, or anything",
      "under `papers/` was read into the staged tree. The staging scripts copy only the paths listed in `sources.json`; the",
      "secrets grep is in LICENCE_AUDIT.md section 6.", ""]
(REL / "SANITIZE.md").write_text("\n".join(L))
print(f"SANITIZE.md: {len(subs)} substitution rows, {len(src) - same} changed files, {same} byte copies, {len(new)} new files")
