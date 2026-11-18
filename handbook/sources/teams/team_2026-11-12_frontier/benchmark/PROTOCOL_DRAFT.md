# Benchmark protocol, draft v0

benchdesign, 12 Nov 2026. First draft for the lead and the user. Nothing here is locked.
Local work only: no server, no GPU, no test or E1 prediction read, no per-run result JSON read. Ground-truth masks and images were counted on CPU.

**Tags.** E = measured in our files (path given). R = from a paper or a scout file. S = my judgement.
**Short paths.** `H03` = `handbook/03_...md` (same for other numbers). `out/` = `team_2026-11-12_frontier/benchmark/out/`. `eval.md` = `team_2026-10-27_unlabelled/eval.md`. `decision.md` = `team_2026-10-21/data/decision.md`.
**My scripts** (`benchmark/scripts/`, run with `python -I`): `corpus_build.py`, `groups_folds.py`, `label_checks.py`. Outputs: `out/corpus_summary.txt`, `out/groups_folds_summary.txt`, `out/label_checks_summary.txt`, `out/extra_counts.txt`, `out/bmrk_pair_check.txt`, `out/cells.tsv` (one row per cell), `out/groups_all.tsv`, `out/pairs.tsv`.

## 0. The design in ten lines (S, from the numbers below)
1. **Corpus:** 816 real labelled cells exist across the three BenchmarkEL releases and E-SCDD (787 unique physical cells). 699 carry Pratt labels, 117 carry Hanifi `_rf` labels. The 93 synthetic files are excluded everywhere.
2. **Three evaluation sets, one optional:**
   - **CV5-G:** module-grouped 5-fold cross-validation over the 532 legacy train + val cells (folds exist, frozen for B6). Development set and the in-distribution table.
   - **L-test:** the legacy 50 test cells, reported three ways (all 50, clean 49, clean without twins 42). Continuity with every past result. Sealed.
   - **U-test:** the 106 E1 cells (unseen modules, 62 half-cut cells, zero half-cut cells in training). Reported in two strata. Sealed.
   - **LOSO-4 (optional):** leave one source out, for the baseline and the final models only.
3. **Classes:** train on the 24 legacy classes. Headline balance metric = mIoU over 13 robust classes (R13). All-class mIoU is reported only with the number of classes that have ground truth.
4. **Headline card (4 numbers per set):** crack relF1@2 (with relP@2 and relR@2), strict crack IoU (shown beside its label ceiling 0.48 to 0.60), inactive IoU, mIoU-R13. Component, cell-level and per-source tables are secondary.
5. **Rules:** final-step weights, argmax primary, at most one val-chosen crack bias with a width guard, 5 seeds, cell or group bootstrap, results with and without the noisy cell and the twins.
6. **Tracks:** full labels, label efficiency (5 to 100%), unseen module, deployment cost, and a light post-evaluation track (per-cell inactive area and crack length from the same predictions). No power-loss track: no electrical ground truth exists.
7. **No manual labelling is required for v1.** Three mechanical label fixes are proposed (section 2.5).

## 1. Why published EL segmentation numbers cannot be compared

| # | Problem | Evidence | Tag |
|---|---|---|---|
| 1 | Different releases of the same dataset | BenchmarkEL has 582, 642 and 695 cells in releases `20211104`, `20220723`, `20221008`; E-SCDD ships 903 files. Pratt 2023 says 593 cells (repo: 582). Torpey 2024 uses 642. PV-DDPM / E-SCDD call the 695 release "SCDD". Hanifi 2025 uses an unreleased 551 / 67 / 77 split. PV-S3's "CSB" S2 / S3 counts (2,109 / 2,282) include augmented copies (unverified) | E `out/corpus_summary.txt` §1; R `H05` §3.4, §16, §19 |
| 2 | Splits were reshuffled between releases | `20211104` to `20220723`: 186 of 582 cells change split (48 train to test, 38 test to train). To `20221008`: 184 of 578. E-SCDD against the legacy split: 185 of 577; 48 of E-SCDD's 82 test cells are legacy train cells; 39 of the 50 legacy test cells are in E-SCDD train | E `out/corpus_summary.txt` §2; E `H17` §5.6 |
| 3 | Augmented copies sit in the train folders | The BenchmarkEL README says the train subfolders hold flipped, rotated and mirrored copies. Pratt 2023 trains on 1,912 = 4 x 478 images. A val split drawn by file from such a folder leaks | E `datasets/BenchmarkELimages/README.md`; R `H05` §3.1 |
| 4 | Synthetic images sit in a train split | E-SCDD train holds 93 diffusion images made from 4 base cells; they carry 11.7% of E-SCDD crack px; one base cell was moved from test to train to follow its copies | E `H17` §5.4 |
| 5 | Train / test twins and shared modules | Legacy split: 24 of 50 test cells share an image id with train cells; 28 of 50 once re-imaged modules are linked. 7 test cells are the same physical cell as a train cell and hold 39.5% of test crack px. E-SCDD: 44 of 82 test cells from train modules. UCF-EL: 291 of 358 module ids in both splits; 25 to 44% of test cells have their physical twin in train | E `out/groups_folds_summary.txt` §B; E `decision.md` D6; E `H17` §5.6; E `data_analysis/ucf_el_report.md` §3 |
| 6 | Validation = test, or test used for tuning | UCF-EL `train.py` builds its val set from the test split (last commit "use test set for val"). Fioresi tunes a 0.54 background threshold by "hit and trial" on one held-out set. PV-S3's released lists put 1,769 of 2,289 public test images in train. Pratt's class weights come from a 16-run DOE on an unstated split | E `ucf_el_report.md` §0; R, E `H05` §4; R `analysis/papers_metrics.md` §1.5 |
| 7 | Different metric conventions | Pratt: per-image IoU, median over 50 test images, absent-class rule not stated (the rule alone moves the mean about 3x, 0.15 to 0.49). Fioresi: dataset-level P / R / F1; its "57.3 mIoU" is likely a 5-class mean with background. PV-S3: background pixels dropped; the same model scores 0.050 with background and 0.828 without; an all-crack predictor scores crack IoU 0.766. PV-S3 Table 6 compares its dataset-level 3-class IoU with Pratt's per-image medians ("+30%") | R, E `analysis/papers_metrics.md` §0, §1.5, §3.4 |
| 8 | Different class lists | 24 classes (Pratt), 29 (`20221008`), 30 (E-SCDD), 3 defects scored (PV-S3 on CSB), 4 defects (UCF-EL, where "crack" is a region class = crack + inactive). 9 of the 24 legacy classes have no ground truth in the legacy test set, so "mIoU over 24 classes" covers different sets on different splits | E `out/label_checks_summary.txt` §4a; E `ucf_el_report.md` §4 |
| 9 | Strict IoU on 1 to 2 px labels | A perfect crack mask shifted by 1 px scores IoU 0.56 on test (0.43 diagonal); the per-image median IoU under a 1 px shift is 0.12. One pixel-identical image labelled twice: crack IoU 0.26. The label revision alone moves every model by +0.05 to +0.07 crack IoU | E `data_analysis/benchmark_el_report.md` §3, §4.1; E `H03` §3.3 |
| 10 | Hand-picked test cells | Pratt 2023: "Fifty images with a prevalence of cracks, gridline defects, and inactive areas were assigned to testing". 48 of 50 test cells contain crack against 44% of train cells; test cracks are darker (0.187 against 0.140). Same recipe, held-out train + val cells (B6, 2 seeds, 425 training cells): crack IoU 0.37, against 0.47 on the clean test | R `H03` §2.2; E `team_2026-10-31_next/verify_b6.md` l.64; E `H18` §M0 |
| 11 | Single runs, no intervals | Pratt 2023, Fioresi 2022, PV-S3 (journal), SA-UNet++ report one run per setting. Our seed sd alone is 0.002 to 0.011 crack IoU and one noisy test cell can move a 5-seed mean by 0.04 | R `H05` §3 to §5; E `H13` A11 |
| 12 | Label errors travel with the release | In `20221008` (and E-SCDD) the cell `BMRK_00031_cell0091` carries, pixel for pixel, the whole mask of `BMRK_00075_cell0255`, a different image (in-cell correlation 0.50). In the legacy split the first is a train cell and the second a test cell | E `out/bmrk_pair_check.txt`; first noted in `results/escdd_audit/README.md` §5 |

Reading (S): no published EL segmentation number states release, split, class list, metric convention, operating-point rule and seed count together. The benchmark has to fix all six.

## 2. Corpus

### 2.1 What exists (E, `out/corpus_summary.txt`)
| Release | Real cells | Split (train / val / test) | Notes |
|---|---|---|---|
| BenchmarkEL `20211104` | 582 | 478 / 54 / 50 | the legacy split; old masks |
| BenchmarkEL `20220723` | 642 | 511 / 65 / 66 | contains all 582 |
| BenchmarkEL `20221008` | 695 | 553 / 70 / 72 | drops 4 legacy cells, adds 117; crack labels corrected |
| E-SCDD (HF `snt-ubix/escdd`) | 810 (+ 93 synthetic) | 638 / 90 / 82 (+ 93 synthetic in train) | 693 of the 695, plus 117 new `_rf` cells |
| **Union** | **816 stems** | | = 582 legacy + 117 added by `20221008` (60 of them already in `20220723`) + 117 `_rf`. 577 cells are in all four releases |

- The 117 cells added by `20221008`: 106 form E1 and 11 are in the 11,938-cell unlabelled pool. The 117 `_rf` cells: 100 are in that pool, 17 are not.
- **De-duplication.** 816 stems, 815 distinct images (`CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`, pixel-identical), **787 unique physical cells**: 16 physical cells (12 CFVS, 4 ARTS) were imaged 2 to 6 times at different stress stages, 45 images in all. 5 of those physical cells have one image in the legacy test set and another in train or val (E `out/extra_counts.txt` (i)).
- **Physical modules.** 491 image ids collapse to 463 physical-module groups (rule of `judge/b6_groups.py`, extended to all 816 cells: same position with crack or inactive mask IoU >= 0.2, or CFVS high-pass correlation >= 0.90, plus the twins listed in `decision.md` D6). 15 groups span more than one image id, 82 cells (E `out/groups_folds_summary.txt` §B). BMRK and SDLE cells are single-cell crops with no module id; each is its own group.

### 2.2 Per source and per cell type (E, `out/corpus_summary.txt` §4; masks: E-SCDD / `20221008`)
| Source | Cells | Crack cells | Inactive cells | Image ids | Cell types |
|---|---|---|---|---|---|
| ARTS | 198 | 60 | 3 | 109 | multi 169, mono 29 |
| CFVS | 187 | 116 | 36 | 112 | mono 147, multi 39, 1 without spacing class |
| CSIR | 348 | 142 | 33 | 187 | multi 112, half-cut multi 105, mono 101, dogbone (IBC) 26, half-cut mono 4 |
| BMRK (= ELPV cells) | 65 | 41 | 12 | 65 | 56 without spacing class, mono 7, dogbone 2 |
| SDLE | 18 | 3 | 0 | 18 | 17 without spacing class, multi 1 |
| **All** | **816** | **362** (356 with >= 20 px) | **84** | 491 | mono 284, multi 321, half-cut 109, dogbone 28, no spacing class 74 |

Cell type is read from the spacing classes in the mask (1 sp multi, 2 sp mono, 3 sp dogbone, 24 / 29 half-cut). BMRK and SDLE crops show one padded cell with no spacing, so the mask gives no type (ELPV's own type labels are not on disk).

| Role in the project | Cells | Crack cells | Inactive cells | Half-cut cells | Label source |
|---|---|---|---|---|---|
| legacy train | 478 | 206 (209 with `masks_escdd`) | 42 | 0 | Pratt |
| legacy val | 54 | 23 | 6 | 0 | Pratt |
| legacy test | 50 | 46 (48 with `masks_escdd`) | 16 | 0 | Pratt |
| E1 (new in `20221008`, not in pool) | 106 | 32 | 10 | 62 | Pratt |
| new in `20221008`, in pool | 11 | 3 | 0 | 4 | Pratt |
| `_rf`, in pool | 100 | 46 | 10 | 43 | Hanifi |
| `_rf`, not in pool | 17 | 6 (3 with >= 20 px) | 0 | 0 | Hanifi |

`_rf` sets used so far (E `H20` §0, `judge/out/rf_sets.tsv`): F51 = 51 full cells from 36 modules not in train (12 crack cells >= 20 px, 4 inactive cells); H36 = 36 half-cuts from 7 image ids; F19 = 19 full cells from train modules; 11 dropped by hygiene (7 share image id `CSIR_00300` with E1).

### 2.3 Licences and redistribution
| Item | Status | Tag |
|---|---|---|
| BenchmarkEL (all releases) | no licence file in the repo; the README asks for two citations | E `H03` §13; `datasets/BenchmarkELimages/` |
| E-SCDD | MIT on Hugging Face. It re-hosts BenchmarkEL images, whose own licence is unstated | E `datasets/escdd_full/README.md` |
| BMRK cells = ELPV | ELPV images reported as CC BY-NC-SA 4.0 (web summary in scout D02; not opened) | R `directions/D02`; unverified |
| SDLE cells = CWRU (OSF `4qrtv`) | not checked | not measured |
| Unlabelled pool (Dropbox; HF `sasan/scdd-unlabeled`) | no licence | E `H20` §7 |
| UCF-EL | no licence file in the local copy | E `datasets/UCF-EL-Defect/` |

Recommendation (S): the benchmark releases **lists and code only**: the cell table (stem, source, module group, cell type, role, flags), fold lists, exclusion lists, the mask-patch script and the scorer. Users download images and masks from the original hosts. No image or mask is re-hosted unless Pratt agrees in writing.

### 2.4 Which mask each cell uses ("label set v1")
| Cells | Mask | Why |
|---|---|---|
| 810 cells in E-SCDD | E-SCDD mask | for crack and inactive it equals `20221008` pixel for pixel (E `H17` §5.2); it adds class 29 for half-cut multi spacing |
| `BMRK_02125_cell1223` (train), `CSIR_00308_r5_c3` (E1) | `20221008` mask | missing from E-SCDD; for the first, old and new masks are identical (E `out/extra_counts.txt` (iv)) |
| `ARTS_00057_r2_c5`, `CSIR_00178_r7_c1`, `CSIR_00179_r12_c4`, `CSIR_00179_r6_c1` | `20211104` mask (= `20220723`, identical) | dropped from `20221008` without a stated reason |
| 24-class view of all of the above | classes 24 to 29 mapped as in section 4.3 | the legacy code has 24 classes |

The project's current training and scoring masks (`masks_escdd`) are this set with one difference: scuff (25) and star (28) pixels were set back to their old label. My local rebuild of that rule reproduces the handbook counts exactly: crack cells 209 / 23 / 48, inactive 42 / 6 / 16 (E `out/groups_folds_summary.txt` §A).

### 2.5 Unresolved label issues
| # | Issue | Size | Proposed handling (S) |
|---|---|---|---|
| 1 | Scuff and star pixels labelled as their old class | legacy: scuff in 14 cells, 3,482 px (12 train, 2 test); star in 3 cells, 238 px. In `masks_escdd` 649 scuff px are crack in 6 train cells and 236 px are crack in 2 test cells; 939 crack px in all were restored by the remap (E `H17` §5.3, §5.11; `out/label_checks_summary.txt` §4b) | v1.1: mark scuff and star as ignore (no loss, not scored). Legacy test also reported on the unchanged masks |
| 2 | A train cell with another cell's mask | `BMRK_00031_cell0091`: 1,560 crack px that belong to `BMRK_00075_cell0255`; under that mask its own image is not darker than its surroundings (-0.023), the other image is (0.027) (E `out/bmrk_pair_check.txt`) | v1.1: give it back its `20220723` mask (66 crack px) |
| 3 | Masks copied between stages of the same cell | 44 same-cell crack mask pairs; 2 are exact copies (4,923 and 10,915 px); about 10 more have IoU >= 0.85 before image alignment and 0.4 to 0.7 after a 1 px alignment, so the mask was reused and sits about 1 px off in one image (E `out/label_checks_summary.txt` §3) | keep; all copies stay in one fold; list the pairs |
| 4 | Two masks for one image | `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`, both train, crack IoU 0.26 between masks | keep both (it is the only clean double annotation); same fold |
| 5 | Hanifi `_rf` crack labels | H36: 1,792 crack px over 17 cells, 75% of components < 5 px (E `H13` A16). 3 `_rf` cells have inactive without crack, which never happens in Pratt labels (E `out/corpus_summary.txt` §4) | `_rf` cells are never scored for crack. Allowed as declared extra training data only |
| 6 | E1 label convention | crack labels 1.5x wider than train (3.66 against 2.41 px); classes 25 to 28 present (scuff in 38 cells, 84,511 px) (E `H13` A17; `out/label_checks_summary.txt` §4b) | classes 25 to 28 are ignore; width-robust metrics are primary on E1 |
| 7 | Noisy images | image-only rule, robust noise sigma > 10: `CSIR_00070_r8_c4` (test), `CSIR_00070_r7_c2` and `CSIR_00069_r7_c1` (train) (E `eval.md` §4) | every table with and without flagged cells |
| 8 | Dotted labels and unlabelled cracks | dotted labels in 22 cells on the old masks; no rate of missed cracks was measured (E `benchmark_el_report.md` §4.4, §4.5) | none; stated as a limit |

## 3. Split design

### 3.1 Option (a): the legacy split, kept as the continuity track
| Set | Cells | Crack cells | Inactive cells | Crack-free cells | Sources |
|---|---|---|---|---|---|
| train | 478 | 209 | 42 | 269 | ARTS 162, CFVS 146, CSIR 111, BMRK 42, SDLE 17 |
| val | 54 | 23 | 6 | 31 | ARTS 20, CFVS 23, CSIR 3, BMRK 8 |
| test, all | 50 | 48 | 16 | 2 | CFVS 18, ARTS 13, BMRK 10, CSIR 8, SDLE 1 |
| test, clean | 49 | 47 | 15 | 2 | without `CSIR_00070_r8_c4` (it holds 787 crack px and 3,815 inactive px) |
| test, clean, no twins | 42 | 40 | 12 | 2 | also without the 7 twins of `decision.md` D6; 54,882 crack px and 77,190 inactive px remain |

(`masks_escdd` rebuilt locally; E `H03` §2.2, `out/groups_folds_summary.txt` §A, my count of the subsets.)

- **Leakage, as measured.** 7 test cells are the same physical cell as a train cell (36,405 of 92,074 test crack px, 39.5%; 12.1% of inactive px) (E `decision.md` D6). With the module rule extended to the whole corpus, 11 test cells sit in a physical module that also has train or val cells under another image id (51.8% of test crack px, 33.0% of inactive px): the 7 twins plus `ARTS_00020_r7_c3`, `CFVS_00114_r2_c5`, `CFVS_00114_r6_c5` (module level only) and `CFVS_00063_r3_c1` (CFVS correlation rule only; its crack mask does not match its candidate twin at all, so it needs a visual check). 28 of 50 test cells and 26 of 54 val cells have a train cell in their physical module (E `out/groups_folds_summary.txt` §B).
- **Checks still needed:** a visual check of `CFVS_00063_r3_c1` against `CFVS_00021_r3_c1`, and of `ARTS_00030_r8_c6` against `ARTS_00164_r8_c6` / `ARTS_00146_r8_c6` (correlation 0.94 to 0.95, no shared defect). The screen compares equal positions only; a module re-imaged upside down would be missed (not checked).
- **Measures:** scores on hand-picked, crack-rich, partly seen modules. **Cannot measure:** false alarms on crack-free cells (2 cells), per-source performance (BMRK 10 cells, SDLE 1), inactive beyond about 3 cells (top 3 hold 59% of px), transfer.
- **Past results:** every P-series, Track M, protocol_100, PF2, THIN-B3, HC and SKR2 number is on this split and enters unchanged.
- **Reads so far.** No single ledger exists for test. Counted openings since 24 Oct: 17 (Track M 7; MIM5 and DDeP5 2; protocol_100 2; PF2, THIN-B3, PF2E, HC, SKR2_HC2, SKR2E 6). Before that, every P-series experiment (P6 to P19, SK1, AL1, Track D) scored its runs on test, uncounted. The trainer also evaluates test at the end of every run (E `H18` §M7, `H19` §3.4, `H12` D49, `team_2026-10-31_next/e1_openings.md`, `H13` C18). Test was never used for training; one operating-point choice and all rung selections used val.

### 3.2 Option (b): module-grouped K-fold (CV5-G)
Candidate pools (E `out/groups_folds_summary.txt` §C; E-SCDD masks):

| Pool | Cells | Physical groups | Crack cells | Crack-free cells | Crack components >= 20 px | Inactive cells | Inactive groups | Effective n, inactive (px-weighted groups) | Half-cut cells |
|---|---|---|---|---|---|---|---|---|---|
| **P532** train + val | 532 | 330 | 229 | 303 | 989 | 48 | 34 | 13.2 | 0 |
| P582 + legacy test | 582 | 349 | 275 | 307 | 1,175 | 64 | 44 | 15.7 | 0 |
| P693 + 11 pool cells + 100 `_rf` | 693 | 383 | 324 | 369 | 1,276 | 74 | 53 | 18.2 | 47 |
| P816 everything | 816 | 463 | 362 | 454 | 1,576 | 84 | 60 | 19.0 | 109 |

The frozen B6 folds on P532 (`team_2026-10-31_next/results/b6/b6_folds.tsv`, md5 e2cafce1; `masks_escdd`; E `protocol_B6.md` §2 and my re-count):

| Fold | Cells | Groups | Crack cells | Crack-free cells | Inactive cells | Inactive px (share) | mono / multi / no spacing | ARTS / BMRK / CFVS / CSIR / SDLE |
|---|---|---|---|---|---|---|---|---|
| 0 | 107 | 66 | 52 | 55 | 10 | 56,753 (0.199) | 47 / 47 / 11 | 36 / 10 / 34 / 23 / 4 |
| 1 | 107 | 67 | 44 | 63 | 8 | 57,565 (0.202) | 47 / 46 / 13 | 37 / 10 / 34 / 22 / 4 |
| 2 | 106 | 64 | 47 | 59 | 7 | 57,142 (0.200) | 38 / 56 / 12 | 37 / 10 / 33 / 23 / 3 |
| 3 | 106 | 68 | 47 | 59 | 15 | 56,785 (0.199) | 53 / 41 / 12 | 36 / 10 / 34 / 23 / 3 |
| 4 | 106 | 67 | 42 | 64 | 8 | 56,775 (0.199) | 56 / 39 / 11 | 36 / 10 / 34 / 23 / 3 |

Crack px is not balanced (fold 3 holds 100,201 of 309,743).

- **Leakage found in the frozen folds (E, new).** The B6 groups were built from train + val evidence only. Adding the test-cell links shows two physical modules cut across folds: image ids `ARTS_00020` (5 cells, fold 1) and `ARTS_00081` (2 cells, fold 3) are the same module; `CFVS_00033` (2 cells, fold 2) belongs to the `r8_c4` chain in fold 1. Four cells are on the small sides, with 2,278 crack px and no inactive px (E `out/label_checks_summary.txt` §1). Small, but a benchmark should not ship it.
- **Other checks needed:** BMRK has no module ids, so two BMRK cells of one ELPV module can sit in different folds (not checkable from the names); classes with all their pixels in one group get zero training pixels in that fold (B6: belt mark, rings, clamp).
- **Measures:** in-distribution accuracy on cells that were not hand-picked; 4.8x the crack cells of the test set; 300 crack-free cells, so a cell-level false-alarm rate exists; per-source tables with 50 BMRK and 17 SDLE cells; per-cell-type tables. **Cannot measure:** unseen layouts (0 half-cut cells); the 7 classes with fewer than 5 groups.
- **What it showed already (E `H21` §3, `verify_b6.md`):** house recipe out-of-fold crack IoU 0.37, relF1@2 0.83, inactive IoU 0.50 to 0.52 (2 seeds). The measured standard error of an inactive IoU contrast was 0.038 to 0.039 (groups 0.031, seeds about 0.022 at 2 seeds), twice the planned 0.020, because each fold's cells are scored by a different model pair. So CV5-G is **not** a more powerful inactive instrument than the test set; its value is leakage control, coverage and false alarms.
- **Cost (E `eval.md` §4):** 5 folds x 1.1 GPU-h = 5.5 GPU-h per seed; 27.5 GPU-h per arm at 5 seeds.
- **Past results:** only B6's 20 runs (house and PF, seeds 5 and 6) are CV5-G results. No P-series run maps onto it.
- **Larger pools.** P582 would add 16 inactive cells but puts test labels into development. P693 adds `_rf` cells whose crack labels are not scoreable and cells that the pool-based arms saw unlabelled. Draft extensions of the frozen folds to both pools are tabulated in `out/groups_folds_summary.txt` §E, §F (list: `out/draft_folds_P693.tsv`); not recommended for v1.

### 3.3 Option (c): the unseen-module, unseen-layout test (U-test = E1)
| Stratum (E `out/groups_folds_summary.txt` §H) | Cells | Image ids | Crack cells | Crack px | Crack-free cells | Inactive cells |
|---|---|---|---|---|---|---|
| half-cut + scuff (>= 500 px) | 29 | 17 | 20 | 24,246 (75%) | 9 | 7 |
| half-cut, no scuff | 33 | 31 | 6 | 2,491 | 27 | 1 |
| full cell + scuff | 8 | 3 | 2 | 4,068 | 6 | 0 |
| full cell, no scuff | 36 | 21 | 4 | 1,489 | 32 | 2 |
| **all** | **106** | **71** | **32** | 32,294 | 74 | 10 |

- 101 CSIR and 5 BMRK cells. Cell types: half-cut multi 58, half-cut mono 4, multi 38, other 6. Training has 0 half-cut cells.
- **Concentration:** the top 3 image ids hold 50% of crack px (effective n 8.6 over 21 crack image ids); inactive is 9,158 px in 7 image ids, top 3 hold 87%, effective n 3.3 (E, same file; agrees with `H13` A18).
- **Leakage check (E):** no E1 physical group holds a legacy cell or one of the 11 pool cells. 7 `_rf` cells share image id `CSIR_00300` with E1 and must never be trained on. (`H03` §7 says 67 modules with 1 shared with the 582; by image-id prefix I count 71 and 0. The 71 is the cluster count used in the PF2E bootstrap.)
- **Measures:** transfer to new modules of a seen source, with a cell layout and a defect context (scuff streaks) absent from training. **Cannot measure:** inactive (3 images); a pure module shift (layout, a 1.5x wider label convention and fainter cracks all change together).
- **Reads so far (E `e1_openings.md`):** many descriptive reads before 31 Oct (every P-series README from P13, Track M rungs, the 27 Oct diagnostics, protocol_100's two openings); 6 registered openings since; opening 7 (SKR2C) is registered and not opened. FINAL and protocol_100 seeds 0 to 4 are not blind on E1.
- **Development reads without E1:** F51 (unseen-module full cells) and H36 (half-cuts, false alarms on its 19 crack-free cells only). The 17 `_rf` cells outside the pool were never used (6 crack cells, 229 crack px: too small to be a test set).

### 3.4 Option (d): leave one source out (E `out/groups_folds_summary.txt` §G, pool P582)
| Held-out source | Test cells | Test crack / inactive cells | Train cells | Train crack / inactive cells |
|---|---|---|---|---|
| ARTS | 195 | 60 / 3 | 387 | 220 / 61 |
| CFVS | 187 | 116 / 36 | 395 | 164 / 28 |
| CSIR | 122 | 61 / 13 | 460 | 219 / 51 |
| BMRK | 60 | 40 / 12 | 522 | 240 / 52 |
| SDLE | 18 | 3 / 0 | 564 | 277 / 64 |

- **Measures:** transfer to a source with its own camera, contrast and label width (ARTS 1.5 px, BMRK 3.0 px). **Confounds:** holding out CFVS removes 36 of 64 inactive cells from training, so that row measures data starvation; SDLE is too small to be a test; strict IoU on a held-out source partly scores its label convention, so tolerant metrics must lead.
- **Cost:** one training per source and seed (4 x 5 x 1.1 = 22 GPU-h per method at 5 seeds). **Past results:** none; no leave-one-source-out run exists.

### 3.5 Recommendation (S)
| Set | Role | Rule |
|---|---|---|
| **CV5-G on P532** | development, and the in-distribution table of the benchmark | use the frozen folds after moving the 4 straddling cells (section 8, decision 2); out-of-fold scores pooled over folds; group bootstrap |
| **L-test** | continuity and final confirmation | never used for selection; one read per locked protocol; always all 50 / clean 49 / clean no-twin 42 |
| **U-test (E1)** | unseen module and layout | never trained on, tuned on or selected on; one read per locked protocol; always the two strata "half-cut + scuff" and "rest" with a 71-cluster bootstrap |
| LOSO-4 (ARTS, CFVS, CSIR, BMRK) | secondary table | only for the baseline and the final models |

**Stays sealed:** the L-test and E1 labels (for training, tuning and selection), the 7 `CSIR_00300` `_rf` cells, the 17 unused `_rf` cells. **Start a test ledger** like `e1_openings.md`; it does not exist.

## 4. Class list and label policy

### 4.1 The 24 legacy classes, by how much evidence they have (E `out/label_checks_summary.txt` §4a; `masks_escdd`)
| Group | Classes (train + val physical groups / test cells with the class) |
|---|---|
| Robust, 13 classes: ground truth in >= 3 test cells and >= 33 train + val groups | background (330 / 50), ribbons (323 / 50), padding (238 / 24), border (236 / 24), gridline (225 / 45), sp mono (148 / 24), crack (138 / 48), sp multi (121 / 14), material (92 / 11), frame edge (79 / 8), splice (36 / 4), inactive (34 / 16), edge dark (33 / 3) |
| Trainable, thin test evidence | busbars (46 / 1), corrosion rbn (15 / 1), text (13 / 0), jbox (9 / 0) |
| Not evaluable, fewer than 5 groups | sp dogbone (2), crack rbn edge (3; 166 px in the whole legacy set), meas artifact (3; 554 px), dead cell (2), clamp (1), rings (1), belt mark (1); none is in the test set |

9 classes have no ground truth in the legacy test set; 2 more are in one test cell each.

### 4.2 Reporting rules (S)
1. **Train on all 24 classes** (continuity; the structure classes carry context).
2. **mIoU-R13** = mean IoU over the 13 robust classes. It is the project's existing mIoU_rob, so past numbers carry over (house 0.580, clean test). It is the balance metric on the L-test and on CV5-G.
3. **All-class mIoU** is printed only as "mIoU over the k classes with ground truth in this set", with k. An absent class is never scored 0 or 1. The 7 not-evaluable classes are listed, not averaged.
4. **A per-class table** (IoU, precision, recall, ground-truth px, cells) is mandatory. Weak classes today: gridline 0.283 (recall 0.33), splice 0.000, edge dark 0.306 (E `BRIEF.md` §3).

### 4.3 Extra classes of the later releases
| Class | Where (E `out/label_checks_summary.txt` §4b) | Policy (S) |
|---|---|---|
| 24 sp mono halfcut, 29 sp multi halfcut | E1 62 cells, `_rf` 43, pool cells 4; legacy 0 | map to sp mono / sp multi (structure) |
| 25 scuff | legacy 14 cells, 3,482 px; E1 38 cells, 84,511 px; `_rf` 12 cells | ignore in scoring; count predicted crack px on scuff as a separate line. Not a class of its own yet: with 649 training px it was not learned (B3, `H20` §6.0) |
| 26 corrosion cell, 27 brightening, 28 star | E1 10 / 20 / 30 cells; legacy star 3 cells, 238 px | ignore |

### 4.4 Crack inside and beside inactive
- 20% of train crack px lie in or at inactive regions; 99% of inactive regions touch a crack label; in Pratt labels inactive never occurs without crack (E `benchmark_el_report.md` §1).
- Policy v1 (S): score the single-label masks as they are. A model with multi-label outputs is converted by one fixed rule, crack over inactive where both fire, which is the annotators' convention. The post-evaluation track (section 6, T5) uses a derived "inactive region" = labelled inactive plus the crack pixels it encloses, stated as derived.

## 5. Metric suite

### 5.1 Definitions (all pooled over the scored set unless marked per cell; argmax; `H18` §M0, `H10` §E1, `eval.md` §3)
| Metric | Definition | Role |
|---|---|---|
| strict IoU, per class | TP / (TP + FP + FN) from one confusion matrix over all pixels, background included, ignore excluded | primary for crack and inactive, with ceilings beside |
| relP@2, relR@2, relF1@2 (crack) | P = share of predicted crack px within 2 px of ground-truth crack; R = share of ground-truth crack px within 2 px of a prediction | **primary crack capture metric**; never R without P |
| component recall / precision (crack) | ground-truth components >= 20 px, found if >= 50% of their px lie within 2 px of a prediction; precision the same way from predicted components | secondary; one count per crack |
| any-hit component recall | a component is found if any prediction touches it within 2 px | secondary; robust to width |
| centreline F1@2 | skeleton of the prediction against the 2 px-dilated ground truth and the reverse (clDice with a tolerance) | proposed width-insensitive measure; **not measured yet** |
| predicted / ground-truth crack px, predicted width | area ratio; area / skeleton length | width flag (house 0.95 on test; Skeleton Recall w 1.0 gave 1.54) |
| inactive region recall | regions >= 100 px, found if >= 50% covered | secondary |
| crack length error (per cell) | \|L_pred - L_gt\| / L_gt on skeleton px, cells with >= 20 px of crack | post-evaluation |
| crack cell flag (per cell) | positive = ground truth >= 20 px; flagged = prediction >= 50 px; sensitivity and false-alarm rate | CV5-G and E1 only (L-test has 2 crack-free cells) |
| inactive area error, detection, cell IoU (per cell) | area in % of non-padding px; detected at >= 0.5%; IoU on cells with >= 0.5% | post-evaluation |
| AP | pixel average precision | secondary only: 42% of crack ground truth sits below p 0.001 (E `H07` §4) |

Every table is repeated per source and per cell type on CV5-G; on the L-test those splits are descriptive.

### 5.2 Label-noise ceilings, printed next to model scores
| Ceiling | Crack | Inactive | Tag |
|---|---|---|---|
| perfect mask shifted 1 px (x; x and y), revised test masks | IoU 0.547; 0.498 (relF1@2 1.00) | 0.943 (old masks) | E `eval.md` §2.2; `benchmark_el_report.md` §3 |
| perfect mask dilated 1 px (cross; 3 x 3); eroded; 1 px centreline; 3 px line | 0.603; 0.525; 0.481; 0.340; 0.745 | not measured | E `eval.md` §2.2 |
| one image, two masks (`CFVS_00015` = `CFVS_00016`) | IoU 0.259, tolerant F1@2 0.83 | IoU 0.83 | E `out/label_checks_summary.txt` §3; old masks 0.257 in `benchmark_el_report.md` §4.1 |
| one cell, two images (`ARTS_00020` / `ARTS_00081`) | IoU 0.534 (0.210 on the old masks), relF1@2 0.997 | none | E `eval.md` §2.2 |
| same cell at two stages, 22 pairs that are not mask copies (image correlation >= 0.9) | aligned IoU median 0.457 (0.127 to 0.931); tolerant F1@2 median 0.965 (0.527 to 0.997) | 13 pairs: IoU median 0.807 (0.427 to 0.979) | E `out/label_checks_summary.txt` §3. Caveat: cracks grow between stages and about 10 pairs are near copies |
| old against revised masks, test | IoU 0.745, 0.98 within 2 px | 0.93 to 0.96 | E `H03` §3.2 |
| best model (5-seed ensemble), clean test | IoU 0.492; 70% of the loss lies within 2 px; IoU 0.80 if near errors are forgiven | 0.456 | E `eval.md` §2.1 |

Reading (S): a strict crack IoU of 0.48 to 0.60 is what a perfect detector with another drawing convention scores. The benchmark prints that band on every crack IoU table.

### 5.3 Operating point and selection rules (S, taken from the project's own failures)
1. **Final-step weights.** No best-validation checkpoint (it flipped signs in the old era, `H07` §9).
2. **Argmax is the primary operating point.**
3. **One optional tuned point:** a crack logit bias chosen on val (or on out-of-fold development cells) by a rule written before the test read: the smallest bias whose component precision is >= 0.90, else the bias with the best relF1@2; refused if relP@2 falls by more than 0.05 (the width guard). Both points are reported. The precision-recall curve on test is shown, never used to choose.
4. **Arms are compared at the same or a matched operating point** (`H13` C20).
5. **Ensembles and test-time augmentation** are separate entries with member count and inference cost. The only clear win so far is a 5-seed ensemble (+0.014 to +0.018 crack IoU).
6. **Declared resources:** pretraining data, extra labelled data, unlabelled pools (with the 7 train twins of test cells removed, `decision.md` D7), compute.

### 5.4 Statistics and what each set can detect
- **Seeds:** >= 5 per arm for single-model claims; one machine per comparison (cv02 and gaint differ by up to 0.056 on inactive IoU, `H07` §3).
- **Decision rule:** the seed rule in use (difference > max(0.01, 2 x sqrt((sdA^2 + sdB^2) / 3))) plus a paired bootstrap over cells (L-test), over physical groups then seeds (CV5-G), over the 71 image ids (E1); leave-top-3-out for inactive.
- **Always with and without** the noisy cell, and with and without the twins. Dropping the noisy cell also drops one of the 16 inactive test cells.
- **Multiplicity:** state the number of contrasts and of set openings; no correction has been applied so far (`H13` C8, C19).

| Set | Crack IoU | Crack relF1@2 | Crack recall | Inactive IoU | Tag |
|---|---|---|---|---|---|
| L-test clean 49, 100% labels, 5 v 5 seeds: true effect detected 80% of the time by the seed rule | 0.012 | 0.013 | 0.018 | 0.032 | E `eval.md` §1.2 |
| same, seed + cell noise, two-sided 5% | 0.007 (floor 0.01 applies) | 0.011 | 0.018 | 0.037 | E `eval.md` §1.2 |
| L-test all 50 (noisy cell in): seed-rule threshold | 0.091 | 0.122 | 0.014 | 0.025 | E `eval.md` §1.2 |
| L-test clean, 5% labels, seed + cell noise | 0.025 | 0.038 | 0.038 | 0.133 | E `eval.md` §1.2 |
| L-test component metrics, threshold | component recall 0.020 (187 components) | | | region recall 0.030 (45 regions) | E `eval.md` §3 |
| E1, module-cluster bootstrap | about 0.02 | thresholds used 0.035 to 0.043 | not measured | not usable (sd 0.05 to 0.09) | E `eval.md` §5; `e1_openings.md` |
| CV5-G P532, 2 seeds per arm | not measured | not measured | not measured | SE 0.038 to 0.039, so about 0.11 for 80% power | E `H21` §3 |

### 5.5 Primary and secondary (S)
- **Primary (the headline card):** crack relF1@2 with relP@2 / relR@2; strict crack IoU; inactive IoU; mIoU-R13.
- **Target line** for "almost all cracks": relR@2 >= 0.90 at relP@2 >= 0.90. Best so far 0.866 at 0.930.
- **Secondary:** component recall and precision, any-hit recall, centreline F1@2, width flag, cell-level flags, per-cell inactive IoU, per-source and per-cell-type tables, per-class table, AP, E1 strata, crack px predicted on ignored scuff.

## 6. Tracks and what a submission reports

| Track | Sets | A submission must report |
|---|---|---|
| **T1 full labels** | CV5-G, L-test, U-test | headline card on each set; per-class table; per-source table on CV5-G; 5 seeds with sd; bootstrap intervals; with / without noisy cell and twins; operating-point rule; parameters and training compute |
| **T2 label efficiency** | L-test (CV5-G optional) | fractions 5, 10, 20, 50, 100% of the 478 train cells (nested lists exist, `datasets/splits_benchmark/seed0`); a supervised arm with the same number of optimiser steps; a loss-off control for any unlabelled loss; the unlabelled pool used; 5 seeds. Rare-class count per fraction printed (inactive is in 2, 4, 9, 20, 42 labelled cells) |
| **T3 unseen module** | U-test | headline card on the two strata; any-hit component recall; false-alarm rate on the 74 crack-free cells; crack px predicted on scuff; statement that no E1 cell, no `CSIR_00300` cell and no half-cut label was used |
| **T4 deployment** | L-test, U-test | parameters, GFLOPs at 512 px, latency per cell on a named device at batch 1, memory; accuracy of the single model and of any ensemble at its true cost |
| **T5 post-evaluation** | CV5-G, L-test | from the same predictions, per cell: inactive area error, inactive band agreement, crack length error, crack cell flag |

Notes per track:
- **T2** is where the project already has the most results (clean-test crack IoU: 5% 0.306, 10% 0.399, 50% 0.448, 100% 0.474; 5% with pseudo-labels 0.335; E `eval.md` §2.1). Limit: all on split seed 0; split seeds 1 and 2 exist and were never used (E `H13` A9). S: add split seeds 1 and 2 at 5% and 20% for the supervised baseline before calling it a benchmark curve.
- **T3** is zero-shot by design: no labelled half-cut crack cell exists outside E1 (E `H13` A16).
- **T4** reference points (E `H18` §M4, §M5): house U-Net++ / ResNet-34 26.1M parameters, 148.0 GFLOPs; ResNet-50 49.0M, 460.4 GFLOPs; 2x input 591.9 GFLOPs; a 5-seed ensemble costs 5 forward passes. Latency is not measured in any file I read. R: inline testers allow about 0.2 s per cell (`H05` §15).
- **T5, is it worth having?** Yes as post-evaluation, no as a severity benchmark.
  - For: it costs no training and no labels; the per-cell inactive IoU separated more contrasts than the pooled one (9 against 7 on test, 17 against 10 on E1; E `H10` §E1); power loss is reported to follow inactive area, not crack length (R `H05` §15); it is the quantity WattCycle would act on.
  - Against a full severity track: there is no electrical ground truth (user decision 11 Oct: no power-loss work without valid data, `H02` §9); the cells per severity band are few. Inactive area bands (0 / < 0.5% / 0.5 to 1% / 1 to 20% / >= 20% of the cell): P532 484 / 10 / 7 / 31 / 0; L-test 34 / 3 / 1 / 10 / 2; E1 96 / 4 / 2 / 4 / 0 (E `out/extra_counts.txt` (ii)). Two cells in the whole labelled set reach the 20% "very critical" band (R Gabor 2022, via `H05` §15). A crack-mode (A / B / C) classifier cannot be scored on that.
  - Per-cell crack metrics were not more sensitive than pooled ones on test (8 against 13 contrasts; E `H10` §E1), so they stay descriptive.

## 7. Baseline suite skeleton

| Family | Members the benchmark should hold | Exists here? | Enters as is? Caveats |
|---|---|---|---|
| House reference | U-Net++ / ResNet-34, CE + Dice on crack and inactive, 20k steps | yes: 5 seeds cv02 (A100), 5 seeds gaint (pf2_SUP s5 to 9), CV5-G 2 seeds (B6) | yes on L-test and E1 (E1 not blind for seeds 0 to 4). Never mix machines in one comparison |
| Encoder-preserving fine-tune (PF) | same model, frozen 1k steps, 0.1x encoder lr | yes: gaint seeds 0 to 9; CV5-G 2 seeds | yes |
| Published EL methods | Pratt 2023 U-Net / DeepLabv3+ with weight sets A and C | old era only (old masks, per-image medians: 0.303 / 0.276 against the paper's 0.19 / 0.13, `H05` §3.1) | no: re-run under the protocol |
| | Hanifi 2025 VGG16-UNet | reproduced with their code on the release split (P19, `H05` §16) | only as a "their protocol" row; re-run for the tables |
| | PV-S3 (Mean Teacher + SemiCE) | released code and a re-implementation on UCF-EL (0.050 standard; 0.276) | no: needs a BenchmarkEL run with background scored |
| | Fioresi DeepLabv3 (COCO), Torpey DeepLabV3 / COCO, SA-UNet++ | UCF-EL reproduction of Fioresi only; SA gate old era | no: re-run |
| Other architectures | ResNet-50, EfficientNet-B4, ConvNeXt-T (U-Net), 2x resolution | R50: 5 seeds cv02 and gaint; B4 and ConvNeXt-T: one val-only pilot each; 2x: 5 seeds | R50 and 2x yes; pilots no |
| | DeepLabv3+, SegFormer, Mask2Former, UPerNet, a Mamba model, nnU-Net | none | to run (list from scout D01 §4) |
| Losses | weighted CE, Dice on 3 / 12 classes, clDice, Skeleton Recall (w 1.0, w 0.1), offset-tolerant CE | all run; Skeleton Recall w 0.1 replication trained, not scored | yes, except offset-tolerant CE (10% labels only) |
| Foundation models | fine-tuned DINO-family or SAM-family backbones | frozen probes and one 2-seed, 4k-step screen | no: screens are not benchmark entries |
| Pretraining | MIM, decoder denoising, UCF-EL encoder | 5% labels (n.d.), MIM at 100% with PF (protocol_100) | 100% arm yes; 5% arms as T2 entries |
| Semi-supervised | Mean Teacher variants, hard and tolerant pseudo-labels, CutMix, decoupled decoder, CPS, ALHVR port, SKCDF head | 5 to 100% labels, cv02, mostly 5 seeds | yes for T2. Caveat: runs before 21 Oct kept the train twins of test cells in the unlabelled pool; report the "without twins" line |
| Data | +107 E-SCDD cells, crack copy-paste, synthetic half-cut views, scuff class | all run at 100% | yes |
| Inference | 5-seed ensemble, test-time augmentation, crack bias | yes (FINAL: crack IoU 0.492, relF1@2 0.897, clean test) | yes, as separate entries; bias was chosen on val |

Common caveats for every existing row (E `H07`, `H13`): legacy split only; `masks_escdd` labels (scuff remap in, `BMRK_00031` error in); split seed 0; inclusion decisions made on a 54-cell val set; no existing run has the full metric suite (component and cell-level metrics exist for Track M and later runs only).

## 8. Risks and open decisions

| # | Decision | Options | My recommendation (S) |
|---|---|---|---|
| 1 | Pool for CV5-G | P532; P582 (+ test); P693 (+ `_rf` and pool cells) | **P532.** It keeps the test set out of development and the folds exist. Revisit P582 only for a final appendix table |
| 2 | The 4 cells that straddle folds | keep the frozen folds and disclose; or move `ARTS_00081_r5_c1`, `ARTS_00081_r9_c6` to fold 1 and `CFVS_00033_r1_c4`, `CFVS_00033_r5_c3` to fold 1 | **Move them now**, before any frontier screening run, and re-freeze with a new md5. B6's 20 runs then carry a one-line caveat |
| 3 | Label set | keep `masks_escdd` (v1); or v1.1 = scuff and star to ignore, `BMRK_00031_cell0091` back to its `20220723` mask, noise flags | **v1.1 for all new CV5-G training and scoring; L-test scored on both.** All three edits are mechanical; none needs a person to draw anything. Needs the lead's OK because it removes 2,263 crack px from the training labels (649 scuff, 54 star, 1,560 on `BMRK_00031`) and restores 66 |
| 4 | Legacy test | keep sealed; or fold into CV | **Keep sealed.** It is the only link to past results |
| 5 | E1 | keep zero-shot and sealed; or train on part of it | **Keep.** Opening 7 (SKR2C) is still pending the user's OK |
| 6 | Redistribution | re-host data; or lists and code only | **Lists and code only**, and one email to Pratt about the missing licence; check the ELPV and CWRU terms before any public release |
| 7 | Headline metric order | relF1@2 first; or strict IoU first | **relF1@2 first**, strict IoU beside its ceiling band |
| 8 | Severity | full track; light post-evaluation; none | **Light post-evaluation (T5).** No power or crack-mode ranking |
| 9 | Seeds on CV5-G | 2 (11 GPU-h per arm) for screening; 5 (27.5 GPU-h) for table entries | **2 to screen, 5 for anything that enters a table** |
| 10 | UCF-EL as a second benchmark dataset | include; or leave for v2 | **v2.** It needs a physical-module-disjoint re-split that does not exist (`ucf_el_report.md` §10) |
| 11 | A test ledger | none today | **Start one now**, same format as `e1_openings.md` |

Risks:
- **Inactive stays under-powered everywhere** (L-test about 0.04, CV5-G about 0.11, E1 unusable). No split of the existing data fixes it. Claims on inactive need large effects.
- **E1 is one source and mostly one defect context.** A method tuned to scuff streaks on half-cut CSIR cells may not transfer further. The benchmark says so on the U-test page.
- **The benchmark is built by one team on one dataset family.** Its credibility rests on releasing the lists, the checks and the scorer, and on re-running the published baselines under it.
- **One month.** The minimum credible table is house, PF, 2 to 3 published EL methods and 2 to 3 recent architectures on all three sets: about 8 arms x (27.5 CV + 5.5 legacy) GPU-h = about 265 GPU-h at 5 seeds.

Manual labelling (S): **none is needed for v1.** Three things would add value and are optional:
1. **Visual check of 4 twin candidates and the BMRK mask swap:** inspection, not labelling; about 0.5 h.
2. **A second crack annotation of about 30 CV5-G cells** to replace the n = 1 clean double annotation with a real inter-annotator ceiling: about 4 to 5 h at 8 to 10 minutes per cell. Worth it only if the ceiling becomes a headline claim of the paper.
3. **Cleaning the 36 half-cut `_rf` crack masks** (2 to 3 h, judge's estimate, `H13` A16): would give a half-cut development set, but is not expected to show E1's scuff context. Not recommended now.

## 9. What I still need from the scouts
Read: D01 (EL segmentation; its section 4 fed section 7) and D02 (dataset census, in progress; fed section 2.3). Not on disk when this draft was written: D41, D43, D44.
- **D41 (evaluation methodology):** published definitions and tolerances for boundary and centreline metrics (NSD, clDice with tolerance, ODS / OIS), so the centreline F1@2 here follows a cited definition; guidance on bootstrap for clustered images.
- **D43 (benchmark design):** how other small-data benchmarks handle grouped cross-validation plus a held-out set, hidden test labels, and versioning of label fixes.
- **D44 (severity, power):** any public set with cell-level electrical ground truth and masks; published inactive-area thresholds with their sources, to replace the two second-hand ones used in T5.
- **D02:** verified licences for ELPV and the CWRU set; whether MSPS (1,500 double-annotated mono cells, unverified) is real and usable as a second dataset in v2.
