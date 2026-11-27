# SANITIZE: every change between the project's files and the staged release (bench_release, 22 Nov 2026)

Tags: E = measured here. Staging code: `staging/stage.py`, `staging/stage_results.py` (rules applied to every staged text
file, line by line, in the order below); this file is written by `staging/make_sanitize.py`.

## 1. Rules

| Rule | Pattern (regex) | Replacement | Why | Hits |
|---|---|---|---|---|
| team_path | `/home/yugma/mtp/research/team_2026-11-12_frontier` | `./local/team` | absolute path of the team folder (user name in the path) | 1 |
| home_work | `/home/noob/work/` | `./local/` | absolute path under a user's home (user name) | 16 |
| home_any | `/home/[A-Za-z0-9_.-]+/` | `./local_home/` | any other home path | 0 |
| tmp_path | `/tmp/noob_el` | `./local_tmp/el` | temporary path naming the user | 0 |
| nas_path | `/mnt/nas/[^\s\"'`)]*` | `<nas-path>` | NAS path | 0 |
| user_tilde | `~/mtp/` | `<datasets-root>/` | home-relative dataset path | 0 |
| host_A | `gaint` | `machA` | server name of the 1-GPU machine | 22 |
| host_B | `cv02` | `machB` | server name of the 8-GPU lab machine | 13 |
| gh_user | `noobsurd11` | `<user>` | GitHub user name | 0 |
| user_1 | `\bnoob\b` | `<user>` | user name | 0 |
| user_2 | `\byugma\b` | `<user>` | user name | 0 |
| ipv4 | `(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])` | `<ip>` | IP address | 0 |
| email | `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | `<email>` | email address | 0 |

machA = the 1-GPU machine (RTX PRO 4500), machB = the 8-GPU lab machine (RTX A6000). No IP address, email address,
GitHub user name or NAS path occurred in the staged sources (0 hits).

## 2. Every substitution (49 lines, 52 substitutions)

| Staged file | Rule | Line | Count |
|---|---|---|---|
| `code/bench/cellmeta.py` | home_work | 29 | 1 |
| `code/bench/cellmeta.py` | home_work | 32 | 1 |
| `code/bench/placement.py` | host_A | 12 | 1 |
| `code/bench/sets.py` | host_A | 3 | 1 |
| `code/bench/sets.py` | host_A | 13 | 1 |
| `code/bench/sets.py` | home_work | 26 | 1 |
| `code/bench/sets.py` | home_work | 28 | 1 |
| `code/bench/sets.py` | home_work | 29 | 1 |
| `code/bench/sets.py` | home_work | 30 | 1 |
| `code/bench/sets.py` | home_work | 32 | 1 |
| `code/bench/sets.py` | home_work | 35 | 1 |
| `code/bench/sets.py` | home_work | 63 | 1 |
| `code/bench/sets.py` | home_work | 64 | 1 |
| `code/bench/sets.py` | home_work | 65 | 1 |
| `code/bench/sets.py` | host_A | 66 | 1 |
| `code/bench/sets/do_not_train.txt` | home_work | 4 | 1 |
| `code/bench/skel.py` | host_A | 1 | 1 |
| `code/bench/udev.py` | home_work | 25 | 1 |
| `code/benchmark_scripts/make_masks_v11.py` | host_A | 19 | 1 |
| `code/benchmark_scripts/make_splits.py` | host_A | 142 | 2 |
| `code/scripts/bench_make_cv5v3.py` | team_path | 47 | 1 |
| `code/scripts/bench_make_cv5v3.py` | home_work | 50 | 1 |
| `code/scripts/bench_read_w1.py` | home_work | 10 | 1 |
| `code/scripts/bench_read_w1.py` | home_work | 11 | 1 |
| `lists/cv5v2.json` | host_A | 58 | 2 |
| `lists/cv5v3.json` | host_A | 273 | 2 |
| `results/BASELINES.md` | host_B | 13 | 1 |
| `results/BASELINES.md` | host_A | 70 | 1 |
| `results/BASELINES.md` | host_B | 70 | 1 |
| `results/BASELINES.md` | host_A | 77 | 1 |
| `results/BASELINES.md` | host_B | 77 | 1 |
| `results/BASELINES.md` | host_B | 81 | 1 |
| `results/BASELINES.md` | host_B | 82 | 1 |
| `results/BASELINES.md` | host_B | 83 | 1 |
| `results/BASELINES.md` | host_B | 84 | 1 |
| `results/BASELINES.md` | host_B | 85 | 1 |
| `results/BASELINES.md` | host_B | 86 | 1 |
| `results/BASELINES.md` | host_B | 87 | 1 |
| `results/BASELINES.md` | host_B | 88 | 1 |
| `results/BASELINES.md` | host_B | 89 | 1 |
| `results/BASELINES.md` | host_B | 90 | 1 |
| `results/BASELINES.md` | host_A | 91 | 1 |
| `results/BASELINES.md` | host_A | 92 | 1 |
| `results/BASELINES.md` | host_A | 93 | 1 |
| `results/BASELINES.md` | host_A | 94 | 1 |
| `results/BASELINES.md` | host_A | 95 | 1 |
| `results/BASELINES.md` | host_A | 96 | 1 |
| `results/BASELINES.md` | host_A | 97 | 1 |
| `results/BASELINES.md` | host_A | 98 | 1 |

## 3. Consistency edits (hand edits after the rules; E)

The staged `lists/cells.tsv` and `lists/cv5v2.json` differ from the originals (sections 2 and 4), so two runtime md5 pins
were moved to the staged files. Without them `w1read.load_exclude` (the score-exclude option) and `cellmeta.load_cells`
refuse the staged table.

| Staged file | Line | Before | After |
|---|---|---|---|
| `code/bench/cellmeta.py` | 34 | `CELLS_MD5 = "a50521b4"` | `CELLS_MD5 = "8998b5f9"` (comment names the original) |
| `code/bench/udev.py` | 27 | `"cells.tsv": "a50521b4...", "cv5v2.json": "441d118f..."` | `"cells.tsv": "8998b5f9...", "cv5v2.json": "ec840084..."` (comment names the originals) |

Not edited, on purpose: `code/scripts/bench_make_cv5v3.py` pins its original inputs (cv5v2.json 441d118f, the original
build's mask MANIFEST.md5, a project results table). It is provenance only and does not run on the staged release.
md5 values quoted inside staged files (for example `cv5v3.json` parent `file_md5` 441d118f and `cells_tsv_md5` a50521b4,
`CELLS_README.md` 'md5 a50521b4', the inputs line of `cv5v3_check.txt`, comments in `bench/sets.py`) name the original
files; section 5 maps them to the staged ones.

## 4. Content reductions (E)

| Staged file | Original | Change |
|---|---|---|
| `lists/cells.tsv` | `benchmark/cells.tsv` | the 156 rows with role test or E1 keep only the 14 identity columns of the code's own rule (`bench/udev.py` SAFE_COLS: stem, source, image_id, position, module_group, cell_id, n_images_of_cell, cell_type, label_source, mask_version, role, bench_set, rf_set, in_unlabelled_pool); 1,727 values blanked; no value was printed while doing it |
| `lists/labels_v11/MANIFEST_pool532.tsv` | `benchmark/out/masks_v11/MANIFEST.tsv` | 50 test rows dropped; 532 train + val rows kept |
| `lists/labels_v11/CHANGES_pool532.tsv` | `benchmark/out/masks_v11/CHANGES.tsv` | 2 test rows dropped; 38 train rows kept |
| `results/BASELINES.md` | `thesis/THESIS_TABLES.md` | sections T5, T6, T7a, T15, T8, T10, T11a copied verbatim under a new header; test50 tables and all other sections left out |

## 5. Original and staged md5 of every changed file (E)

| Staged file | Source | Source md5 | Staged md5 |
|---|---|---|---|
| `code/bench/cellmeta.py` | `git cba7fbd:bench/cellmeta.py` | 72ca7200babe091b59c5f518a6e4c311 | 6db6791d4196f795a632fddc2454d4a5 |
| `code/bench/placement.py` | `git cba7fbd:bench/placement.py` | 8699d9c3a41757a5fc3119789f758287 | 98794799b05329210f6af143851684bd |
| `code/bench/sets.py` | `git cba7fbd:bench/sets.py` | 92ef7db3cbe1fe74fe1823cc71844db1 | 6dc945ddae66bf0a51023a2d1aba73fb |
| `code/bench/sets/do_not_train.txt` | `git cba7fbd:bench/sets/do_not_train.txt` | 5a22e8cce1ca2768b28504c1f2333a47 | 99adceddb5699fcff57f5958cf010860 |
| `code/bench/skel.py` | `git cba7fbd:bench/skel.py` | 804e4162fd9e208723575e2ffb0d62db | 2244127dbeaf66524941ecd7541b31ee |
| `code/bench/udev.py` | `git cba7fbd:bench/udev.py` | af547717486a207b3a63cf17e05caf1f | c6ae01f423ddcefb9a614acbb8000a2d |
| `code/benchmark_scripts/make_masks_v11.py` | `benchmark/scripts/make_masks_v11.py` | 4467261c848bc06467cf445d9f11bf0e | 318339f53ad4d5618c2c20756709a9a6 |
| `code/benchmark_scripts/make_splits.py` | `benchmark/scripts/make_splits.py` | cfd6199782d50183b50e6f0ba3a0bdd7 | 28587a7a9a0e8a5dbca3597d16b7f350 |
| `code/scripts/bench_make_cv5v3.py` | `git cba7fbd:scripts/bench_make_cv5v3.py` | d6c2eea3d044bd788c4b1343ae5a5186 | 2671fc1596d97d4d6b4c7cfef5c60132 |
| `code/scripts/bench_read_w1.py` | `git cba7fbd:scripts/bench_read_w1.py` | fdb56b786578a7b7cae5c764bd894fd1 | 86b532902a2b48e84a99e3cd4926ac45 |
| `lists/cells.tsv` | `benchmark/cells.tsv` | a50521b4d0648766b28cc297869603ec | 8998b5f978bd87b3a7dd94e053176ca8 |
| `lists/cv5v2.json` | `benchmark/splits/cv5v2.json` | 441d118f865d5642dd6a5e2be80ec753 | ec840084b0c0a0eab1aa69a14b59b87c |
| `lists/cv5v3.json` | `benchmark/splits/cv5v3.json` | 7a700b0032a6305ab2c2c570453283af | 5649ed1911779fb783ea62c8049067eb |
| `lists/labels_v11/CHANGES_pool532.tsv` | `benchmark/out/masks_v11/CHANGES.tsv` | da2315bb35ad39189a58265de3a10414 | fb815cf9a30ad78c2e3a325612a01bef |
| `lists/labels_v11/MANIFEST_pool532.tsv` | `benchmark/out/masks_v11/MANIFEST.tsv` | f88907f227333e60684c51e0a12ea63d | 5fd84e496c848fe9c8159e0a24e61ed8 |
| `results/BASELINES.md` | `thesis/THESIS_TABLES.md (sections T5. T6. T7a. T15. T8. T10. T11a.)` | 707c7c46e9bb649d51a0b1074acf2be0 | 585177a552408c0f9c1543d831ce6f54 |

45 staged files are byte copies of their source (md5 equal). Files written for the release, with no source: `README.md`, `code/tools/prepare.py`.

## 6. Never copied

No credential, `.env`, ssh configuration, token, dataset image, mask, checkpoint, per-cell sealed result, or anything
under `papers/` was read into the staged tree. The staging scripts copy only the paths listed in `sources.json`; the
secrets grep is in LICENCE_AUDIT.md section 6.
