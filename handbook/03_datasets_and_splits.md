# 03. Datasets, mask versions, splits and data locations

## What this covers
Every dataset the project touches and exactly how it is cut up:
- **BenchmarkEL `dataset_20211104`:** the main dataset, 582 labelled cells;
- its two **mask versions:** the old `masks_coded` and the revised E-SCDD `masks_escdd`;
- the **labelled fractions** (5/10/20/50/100%) and the in-domain unlabelled pools that go with them;
- the **val and test sets**, and why their composition dominates the statistics;
- the **external unlabelled pool** (11,938 CSIR/ARTS cells);
- the **106-cell unseen-module extension** used by E1;
- **UCF-EL**, the second dataset, used in the old era and for P15 pretraining;
- other datasets that were considered but not used;
- preprocessing, and where every file lives (local, gaint, cv02);
- a list of common confusions.

For what the images and classes *mean* physically, read `02_domain_primer_EL_and_defects.md` first.

## Sources
- `~/mtp/research/data_analysis/benchmark_el_report.md` and `ucf_el_report.md`: first-hand analyses (8 Oct 2026).
- `~/mtp/datasets/BenchmarkELimages/README.md`, `dataset_20211104/` (images, old masks, class CSV).
- `~/mtp/datasets/splits_benchmark/`: `splits_meta.json`, `train/val/test.txt`, `seed{0,1,2}/`, `external_unlabeled.txt`, `external_unlabeled_meta.csv`.
- `~/mtp/datasets/splits_ucf_cv02/`: `manifest.json`, `manifest_cv02_subsets.json`, split lists.
- gaint `/home/noob/work/el-fault-detection/`:
  - `scripts/make_splits.py`;
  - `src/data/class_info.py`, `src/data/benchmark_el.py`;
  - `reports/split_class_pixel_counts.md`, `reports/external_pool.md`;
  - `data/README.md`, `configs/base.yaml`.
- `~/mtp/research/results/p3_label_versions/README.md`: old vs revised masks.
- `~/mtp/research/results/p6/README.md` §4: inactive concentration in val/test.
- `~/mtp/research/results/e1/README.md`: the 106-cell extension.
- `~/mtp/research/protocols/P6_corrected_baseline.md`, `P14_tolerant_supervision.md`, `P15_ucf_encoder_transfer.md`, `P16_label_fraction_curve.md`.
- `~/mtp/research/literature/notes/F04_el_datasets_census.md`: releases, E-SCDD, BMRK = ELPV, other datasets.
- `~/mtp/MTP_session_handoff_2026-10-07.md` §3: data facts from the earlier era.
- `sources/chat/claude_session_summaries_2026-10-07_to_11.md` (E-SCDD provenance, mask-set construction) and `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`.
- Counts marked "(cv02 count, 11 Oct)" were made for this handbook, read-only. They used `/tmp/noob_el/el_p13/data` on cv02, a symlink to `/tmp/noob_el/el_p7/data`, the data every P-series run on cv02 reads.

---

## 1. Map of all datasets

| Dataset | Role in the project | Size | Status |
|---|---|---|---|
| **BenchmarkEL `dataset_20211104`** (Pratt et al.) | the main labelled dataset; every P-series result | 478 train / 54 val / 50 test = **582** cells, 512 × 512 | used throughout |
| **E-SCDD revised masks** (HuggingFace `snt-ubix/escdd`, MIT) | replacement masks for the same 582 images; training and evaluation labels from P6 on | covers 577 of our 582 | used from P6 on |
| BenchmarkEL `dataset_20220723`, `dataset_20221008` | newer releases with more images, reshuffled splits and cleaned crack labels | 642 and 695 originals | only the 106 extra `20221008` cells are used (E1 extension) |
| **External unlabelled pool** (CSIR/ARTS cells from the BenchmarkEL Dropbox) | unlabelled data for "x" arms (P9–P12) and for Sx100 (P16) | **11,938** cells | used |
| **ext106 extension** | out-of-distribution test of trained models (E1) | 106 cells from 67 modules | used |
| **UCF-EL** (Fioresi et al.) | old-era reproduction and SSL work; P15 encoder pretraining | 9,562 train / 2,289 test | used |
| ELPV (ZAE Bayern) | = BenchmarkEL's BMRK cells; possible weak labels | 2,624 cells | not used |
| PVEL-AD, PV-Vision, MultiSolSegment, others | candidates for weak supervision or extra data | see §9 | not used |

---

## 2. BenchmarkEL `dataset_20211104`

### 2.1 What it is
- **Authors and papers.** Pratt, Govender, Klein 2021 (Renewable Energy) and Pratt, Mattheus, Klein 2023 (Systems and Soft Computing). Public GitHub `TheMakiran/BenchmarkELimages` (`datasets/BenchmarkELimages/README.md`).
- **Classes.** 24 classes: 12 features and 12 defects. Class list and ids are in `02_domain_primer_EL_and_defects.md` §5. Crack = 14, inactive = 11.
- **Folder layout we use** (`~/mtp/datasets/BenchmarkELimages/dataset_20211104/`):
  - `images_train_original`, `images_val`, `images_test`;
  - `masks_coded_train_original`, `masks_coded_val`, `masks_coded_test` (index PNGs, pixel value = class id);
  - `ListOfClassesAndColorCodes_20211104.csv`.
- **Do not train on augmented copies.** The README says the train subfolders of the releases include augmented copies (flip, rotate, mirror). Our split uses only `images_train_original`. The handoff rule: "label fractions must be sampled by cell, never by file, and only from `images_train_original`" (`MTP_session_handoff_2026-10-07.md` §3.1).
- **Images.**
  - All 512 × 512.
  - Stored as RGBA with alpha 255 everywhere, near-grey (`gaint reports/external_pool.md`).
  - The loader converts them to 8-bit grayscale with PIL `convert("L")` (`src/data/benchmark_el.py`).
- **Masks** are read directly. Any value outside 0–23, or a non-single-channel PNG, is an error. A missing split file is an error: the code never falls back to "all images in the folder" (gaint `data/README.md`). Phase 0 found that the inherited old code silently trained on all 582 images, test included, when a split file was missing (`MTP_session_handoff_2026-10-07.md` §4.2).

### 2.2 Official split: 478 / 54 / 50

| Split | Cells | Modules | With crack (old masks) | With inactive (old masks) | With crack (revised) | With inactive (revised) |
|---|---|---|---|---|---|---|
| train | 478 | 322 | 205 (42.9%) | 43 (9.0%) | 209 | 42 |
| val | 54 | 49 | 22 (40.7%) | 5 (9.3%) | 23 | 6 |
| test | 50 | 48 | **50 (100%)** | 17 (34.0%) | **48** | **16** |

- Old-mask columns: gaint `reports/split_class_pixel_counts.md` and `benchmark_el_report.md` §0. Revised columns: cv02 count, 11 Oct. Test revised 48 and 16 also match `results/p6/README.md` §4. Module counts: `benchmark_el_report.md` §0.
- **The test set was hand-picked.** Pratt 2023: "Fifty images with a prevalence of cracks, gridline defects, and inactive areas were assigned to testing" (`literature/notes/A01_pratt2023_benchmarkel.md`).
  - So test is not representative: every test cell has a crack (old masks), and inactive is in 34% of test cells against about 9% elsewhere.
  - Test cracks are also darker and more visible: median relative darkness 0.187 vs 0.140 in train (`benchmark_el_report.md` §4.3).
  - Consequence: almost no test cell is crack-free, so a "false alarm on crack-free cells" metric is uninformative on test (`results/e1/README.md`).

**Per source** (counted from the image folders for this handbook; train matches `benchmark_el_report.md` §0):

| Source | Train | Val | Test | Total |
|---|---|---|---|---|
| ARTS | 162 | 20 | 13 | 195 |
| CFVS | 146 | 23 | 18 | 187 |
| CSIR | 111 | 3 | 8 | 122 |
| BMRK | 42 | 8 | 10 | 60 |
| SDLE | 17 | 0 | 1 | 18 |
| all | 478 | 54 | 50 | 582 |

The totals match the labelled-per-source column of gaint `reports/external_pool.md`.

**Module sharing and duplicates** (`benchmark_el_report.md` §5):
- 20 of 54 val cells and 24 of 50 test cells come from modules that also have train cells. 9 modules are shared between val and test.
- One cross-split duplicate: `train/ARTS_00081_r5_c1` ≈ `test/ARTS_00020_r5_c1`. It is the same cell (correlation 0.9999), but the masks differ: crack IoU 0.21 between them.
- One within-train duplicate: `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`, pixel-identical, with different masks.

### 2.3 Class pixel shares and the loss signal
- **Train pixel shares:** background 69.2%, padding 17.3%, crack 0.186% (`MTP_session_handoff_2026-10-07.md` §3.1).
- **Crack GT pixels:** train 232,914, val 27,873, test 70,626 (old masks; same source, confirmed in `benchmark_el_report.md` §0).

**Old-era weighted cross-entropy.** The old-era recipe weighted each class by 1/√frequency, capped at 10× the median and normalised to mean 1, with weight 0 for absent classes. The weights then depend on the labelled subset (`benchmark_el_report.md` §6; seed 0):

| Labelled subset | n | w(crack) | crack : bg weight | crack share of weighted loss | zero-weight classes |
|---|---|---|---|---|---|
| 100% | 478 | 0.351 | 19.3 | 1.8% | 0 |
| 50% | 239 | 0.356 | 18.2 | 1.9% | 2 |
| 20% | 95 | 0.559 | 16.0 | 2.1% | 6 |
| 10% | 47 | 0.738 | 15.2 | 2.2% | 7 |
| 5% | 23 | 1.440 | 19.2 | 1.7% | 10 |
| 2% | 9 | 1.668 | 14.7 | 2.3% | 12 |

- Crack gets only about 2% of the loss signal; background and structural classes get 80–88%.
- The "same" loss is a different operating point at every fraction.
- The P-series base recipe (L3, from P6) replaced weighted CE with CE + soft Dice on crack and inactive. See `08_experiments_P1_P7_diagnostics.md` (P6).

---

## 3. Mask versions: old (`masks_coded`) vs revised (E-SCDD, `masks_escdd`)

### 3.1 What the revised masks are
**E-SCDD.** HuggingFace `snt-ubix/escdd`, MIT licence, 903 images, 29 classes, described as having "refined pixel-level annotations". It is built on BenchmarkEL `20221008` (`results/p3_label_versions/README.md`; `sources/chat/claude_session_summaries_2026-10-07_to_11.md`).
- It contains **577 of our 582** images. 185 of them sit in a different split there; we keep our own split (`results/p3_label_versions/README.md`).
- Images are pixel-identical between versions (576 of 577 checked, same source).

**How `masks_escdd` was built** (`protocols/P6_corrected_baseline.md`; `sources/chat/claude_session_summaries_2026-10-07_to_11.md`):
- 577 masks come from E-SCDD.
- The 5 train stems missing from E-SCDD keep their old masks. None of the 5 is in the 10% subset.
- E-SCDD classes 24–29, which do not exist in our 24-class taxonomy, are mapped back to the old label at those pixels.
- The same mask set is used for training, val, test and class weights.
- **Locations:**
  - training labels: `data/labeled/masks_escdd/`;
  - evaluation copies: `data/escdd_masks/{train,val,test}/`, which the re-score scripts read;
  - On cv02, `data/labeled/masks_escdd` is a symlink to `/tmp/noob_el/masks_escdd`. That directory lists 583 entries against 582 masks expected. The extra entry is unknown; check that directory.

### 3.2 How they differ

**From P3** (`results/p3_label_versions/README.md`, E-SCDD vs our old masks):
- 361 of 577 masks are identical.
- 129 of the 281 crack images have a changed crack mask, including 34 of the 50 test images.
- Changed crack masks have a median of 1.67× more crack pixels and lie almost entirely within 2 px of the old labels: relaxed agreement 0.98 / 0.98.

| Split | Crack IoU between versions | Inactive IoU |
|---|---|---|
| test | 0.745 | 0.93–0.96 (range over splits) |
| val | 0.732 | |
| train | 0.81 | |

- **Reading (P3):** this is a cleaning, not an independent re-annotation. Dotted labels are joined and labels are widened.

**From the census** (`literature/notes/F04_el_datasets_census.md` §1a). This compares BenchmarkEL's own `20221008` release (not E-SCDD) with our `20211104` masks:

| Split | Masks changed | Crack-label changes | Crack IoU old/new | Crack px change |
|---|---|---|---|---|
| train (474 common) | 156 | 81 images | 0.567 | +51% |
| val (54) | 18 | 14 images | 0.638 | |
| test (50) | 42 | 35 images | 0.693 | +39% |

- On changed images (`20220723` → `20221008`): mean label width 1.82 → 2.55 px; crack fragments 3,707 → 549 (a 7× drop: dotted labels joined); median 100% of new crack pixels within 1.5 px of the old label.

**Conflict to know about.** P3 (E-SCDD vs ours) and F04 (`20221008` vs ours) give different agreement numbers: test crack IoU 0.745 vs 0.693, train 0.81 vs 0.567. They compare different mask sets, and why E-SCDD differs from `20221008` is not documented. Check `results/p3_label_versions/` (its `compare.py` output) and `F04_el_datasets_census.md` before quoting either as "the" agreement. Both agree on the main point: the revision is a 1–2 px cleaning of the same labels.

### 3.3 What the label version does to scores

**Old-era models re-scored on both mask versions** (P3, `results/p3_label_versions/README.md`). These are old-era models: from-scratch U-Net++, weighted CE, batch 8, trained on old masks. Crack, test, mean ± sd over 3 seeds:

| Run (old era) | Crack IoU old → new | Crack AP old → new |
|---|---|---|
| SL-10% b8 | 0.304±0.005 → 0.355±0.005 | 0.492±0.004 → 0.527±0.001 |
| SL-100% b8 | 0.283±0.003 → 0.339±0.006 | 0.457±0.006 → 0.541±0.001 |

- The label version alone moves crack IoU by **+0.05 to +0.07** for every model. That is larger than any SSL effect measured on cv02 (`to_human/results_2026-10-12.md`, evidence row 1).
- Training on old vs revised masks (P-series, P14): L3 (revised) − L3o (old), at 10% labels, scored on revised labels, gives crack IoU **+0.082** (`results/p14/README.md`). Details in `10_experiments_P13_P16_E1.md`.

### 3.4 Which experiments use which masks

| Experiments | Training masks | Evaluation masks |
|---|---|---|
| Old era (phase 0/1, handoff runs up to 7 Oct) | old `masks_coded` | old |
| P3 (re-score only) | old (existing checkpoints) | both |
| P6 onward (all P-series training) | revised `masks_escdd` | revised (primary), old (secondary in some) |
| P14 arms L3o and L3To | **old** `masks_coded` (the point of the experiment) | revised |
| E1 extension (ext106) | – | the `20221008` release's own masks (cleaned like E-SCDD), see §6 |

---

## 4. Labelled fractions and in-domain unlabelled pools

### 4.1 How the subsets are drawn
From gaint `scripts/make_splits.py` (docstring) and `splits_meta.json`:
- **Size.** Subset size = int(478 × fraction): 239 / 95 / 47 / 23 / 9 for 50 / 20 / 10 / 5 / 2%. The 100% "subset" is `train.txt` (478).
- **Stratified** on two flags: contains crack (14), contains inactive (11). Inactive never occurs without crack, so there are 3 strata, not 4:

  | Stratum | Train cells |
  |---|---|
  | no crack, no inactive | 273 |
  | crack, no inactive | 162 |
  | crack and inactive | 43 |

- **Largest-remainder rounding** of the proportional quota per stratum.
- **Nested.** Within a stratum, train cells are shuffled once per seed and each fraction takes a prefix: 2% ⊂ 5% ⊂ 10% ⊂ 20% ⊂ 50%.
- **Unlabelled pool** = train minus the labelled subset (`unlabeled_<P>pct.txt`). This is the "in-domain" pool.
- **Split seeds 0, 1, 2 exist. Every run in the project uses split seed 0** (`data.split_seed=0`). The `_s0/_s1/...` suffix in a run name is the **training** seed, not the split seed (`MTP_session_handoff_2026-10-07.md` §3.2).
- **The stratification flags were computed on the old masks.** With the revised masks the per-subset counts shift slightly (next table).

### 4.2 The table to remember

| Fraction | Labelled cells | Crack cells, old / revised | Inactive cells, old / revised | In-domain unlabelled pool | Zero-pixel classes (old masks, seed 0) |
|---|---|---|---|---|---|
| 2% | 9 | 4 / – | 1 / – | 469 | 12 |
| **5%** | **23** | 10 / 9 | **2 / 2** | **455** | 10 |
| **10%** | **47** | 20 / 19 | **4 / 4** | **431** | 7 |
| **20%** | **95** | 41 / 42 | **9 / 9** | **383** | 6 |
| **50%** | **239** | 102 / 102 | **21 / 20** | **239** | 2 |
| **100%** | **478** | 205 / 209 | **43 / 42** | **0** | 0 |

Sources:
- old-mask counts and zero-pixel classes: gaint `reports/split_class_pixel_counts.md` and `splits_meta.json`;
- revised counts and pool sizes: cv02 count, 11 Oct;
- pool sizes 455/431/383/239/0 and revised inactive 2/4/9/20 also appear in `protocols/P16_label_fraction_curve.md`;
- 2% pool: 478 − 9, not used by any P-series run.

**Conflict note.** Inactive at 50% is 21 cells with the old masks (`splits_meta.json`) and 20 with the revised masks (`P16_label_fraction_curve.md`; cv02 count). Both are correct for their mask version.

**Why this matters (Reading).**
- At 5% and 10%, inactive is learned from **2 and 4** labelled cells.
- The SSL series P8–P13 ran at 5–10%. That made inactive unmeasurable by construction, which is the reason P16 was added at 20/50/100% (`protocols/P16_label_fraction_curve.md` "Why this exists").
- The user raised this on 11 Oct: "why we using 5 or 10% for ssl? they are really low" (`sources/chat/user_messages_2026-10-07_to_11.md`).

### 4.3 Pixel counts of the small subsets
Old masks, seed 0 (gaint `reports/split_class_pixel_counts.md`):

| Class | 10% (47 cells) | 5% (23) | 2% (9) |
|---|---|---|---|
| crack px | 34,944 | 10,029 | 6,203 |
| inactive px | 30,494 | 20,479 | 6,981 |
| background px | 8,089,804 | 3,705,067 | 1,342,606 |
| padding px | 2,544,675 | 1,593,865 | 738,816 |

Split seeds 1 and 2 have very different crack pixel counts at 10% (15,705 and 11,984 vs 34,944), but they were never used.

---

## 5. Val and test: small, and dominated by a few cells

**Inactive** (revised masks, `results/p6/README.md` §4; val crack figures: cv02 count, 11 Oct):

| Split | Cells with any inactive | Share of inactive px held by the top 3 cells | Largest single cell |
|---|---|---|---|
| test | 16 of 50 | **59%** | `BMRK_00073_cell0253`, 23% |
| val | 6 of 54 | **89%** | `CFVS_00143_r4_c3`, 35% |

**Crack** (revised masks; the test largest cell is from `results/p6/README.md` §4):

| Split | Cells with crack | Top-3 share of crack px | Largest single cell |
|---|---|---|---|
| test | 48 of 50 | 32% | 12% |
| val | 23 of 54 | 44% | – |

**Consequences** used throughout the handbook (see `07_methodology_rules_and_statistics.md` and `13_problems_pitfalls_open_issues.md`):
- Any dataset-level inactive metric is decided by about 3 cells. Every P-series README reports a "leave-top-3-out" Δ and an image bootstrap for this reason.
- **Val is nearly useless for inactive.** In P13, val inactive IoU went the opposite way from test: A5c 0.106 vs CsM5 0.081 on val (`results/p13/README.md`). P16's CutMix setting was chosen on val (the user's choice), so this matters there too.
- **Final weights, not best-val checkpoints.** Phase 0 found that best-val selection on 54 cells flips the sign of several comparisons (`MTP_session_handoff_2026-10-07.md` §4.2), so final-step weights are primary.

---

## 6. The external unlabelled pool (11,938 cells)

**Origin** (`datasets/BenchmarkELimages/README.md`; gaint `reports/external_pool.md`; `MTP_session_handoff_2026-10-07.md` §3.3):
- The BenchmarkEL README links a Dropbox folder of more than 150,000 cell-level EL images, cropped from 2,573 module images. Over 2,000 of those images come from one module supplier, from a 911 kWp rooftop installation at the CSIR (2018).
- 11,993 files were downloaded: seed 42, spread evenly over 9 leaf folders, 7 failed. Raw files are on gaint at `/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/images`.
- **Filtering** (6 Oct 2026):
  - 55 files dropped because the cell is a labelled image (48 train, 6 val, 1 test).
  - **11,938 kept.** Only exact cell-ID matches were dropped.
  - 1,979 / 196 / 88 kept cells come from modules that also have train / val / test cells.
- **Conversion.**
  - Grayscale with the same PIL call as the labelled images.
  - 1200 px images area-downsampled to 512 × 512; 512 px images unchanged.
  - Written to `data/unlabeled/images_512/` and listed in `data/splits/external_unlabeled.txt`, with provenance in `external_unlabeled_meta.csv`.
- **No intensity harmonisation** was applied.

**Composition** (`~/mtp/datasets/splits_benchmark/external_unlabeled_meta.csv`, counted for this handbook):

| By source | Cells | By cell type | Cells | By native size | Cells |
|---|---|---|---|---|---|
| CSIR | 9,204 | mono | 6,163 | 512 px | 6,834 |
| ARTS | 2,734 | multi | 4,623 | 1200 px | 5,104 |
| CFVS, BMRK, SDLE | 0 | multi half-cells | 1,152 | | |

**Mismatches with the labelled images** (gaint `reports/external_pool.md`):
1. **Only two sources.** 205 of the 478 labelled train cells (43%) are CFVS, BMRK or SDLE, with no counterpart in the pool.
2. **Contrast.** The native 512 px images (57% of the pool) have about half the contrast of labelled images: median per-image sd 26–29 vs 43–50.
3. **Sharpness.** It differs most for multi cells and for ARTS (mean |Laplacian| 5.4 vs 9.4 for ARTS).
4. **Brightness.** ARTS pool cells are brighter (170 vs 134). CSIR matches (141 vs 142).

**Where it is used.**
- External-pool SSL arms ("x" suffix):
  - P9 at 10% (Dx, Bx, Cx);
  - P10 at 5% (Dx5, Cx5);
  - P11 (Dmx, Cmx);
  - P12 (Dmx5, Cmx5);
  - P16 Sx100: at 100% labels the in-domain pool is empty, so SSL can only use this pool.
- In the old era: the MT-20-ext queue on gaint, held since 8 Oct 01:18 IST (19:48 UTC on 7 Oct) and never relaunched (`sources/chat/user_messages_2026-10-07_to_11.md`, crontab edit).

**Result in one line** (`to_human/results_2026-10-12.md`, evidence row 5): no loss effect from this pool in P9, P11 or P12. (Strictly, P9's Cx − Dx passed the seed rule on inactive, +0.056 against a threshold of 0.046, but the pass was not robust over cells, CI [−0.013, +0.117], and was no larger than P8's in-domain effect; `results/p9/README.md`.) In P10/P12, crack got worse on the pool's own sources. Details in `09_experiments_P8_P12_ssl_series.md`.

---

## 7. The 106-cell unseen-module extension (E1)

From `results/e1/README.md`.
- **Origin.** Cells of BenchmarkEL release `20221008` that are:
  - not among our 582;
  - not in the external pool. The release has 117 extra cells; 11 were in the pool and are dropped.
- **Composition.** 101 CSIR and 5 BMRK; 32 contain crack and 10 contain inactive.
- **Modules.** 67 modules, of which only 1 has cells among our 582. So the set measures **transfer to unseen modules**, not in-distribution performance. Visually it looks different from our cells (`results/e1/ext_montage.png`).
- **Masks.** The release's own (cleaned, like E-SCDD).
  - Class 24 (sp mono halfcut) is remapped to sp mono.
  - Classes 25–28 (scuff, corrosion cell, brightening, star) do not exist in our taxonomy. They are marked **ignore**, excluded from the cell area and scored neither way. This is an amendment after a first pass that mapped them to background. It is disclosed in the README.
- **Files.** cv02 `/tmp/noob_el/ext117/{images,masks,ignore,stems_eval.txt}`; `stems_eval.txt` has 106 lines (cv02 count, 11 Oct). The manifest is `results/e1/ext117_manifest.csv`.
- **The regime is very different.** L3 at 100% labels drops from crack IoU 0.471 on test to 0.152 on the extension (`results/e1/README.md`).
- **Count conflict, resolved.** `to_human/proposal_reframe_2026-10-11.md` (E1 row) planned "117 cells (112 CSIR, 5 BMRK; 35 with crack, 10 with inactive)". The scored set is the 106 after removing the 11 pool cells.

---

## 8. UCF-EL (Fioresi et al. 2022)

### 8.1 What it is
From `data_analysis/ucf_el_report.md` and `literature/notes/A03_fioresi2022_ucfel.md`.
- **Release.** Public repo `ucf-photovoltaics/UCF-EL-Defect`, analysed at commit `3ebfc6bb`. 9,562 train and 2,289 test image/mask pairs. The paper describes 17,064 images; the release is the 11,851 cells with at least one annotated region.
- **Classes.** Background 0, crack 1, contact 2, interconnect 3, corrosion 4; ignore 128.
  - Crack merges Crack_Closed, Crack_Resistive and Crack_Isolated, so it is a region class ≈ BenchmarkEL crack + inactive. See `02_domain_primer_EL_and_defects.md` §10.
  - Contact = front-grid interruptions and near-solder-pad faults (loose boxes).
  - Interconnect = HighlyResistive only; disconnected cells are ignore.
- **Masks** are the annotators' polygons and rectangles rasterised with no margin (99.6% pixel agreement on rebuild).
- **Image sizes vary.** Shorter side 190–600 px, mode 290 × 290. The project trains at shorter side 295.

### 8.2 Inventory
Pixel shares at shorter side 295 (`ucf_el_report.md` §2):

| | train | test |
|---|---|---|
| images | 9,562 | 2,289 |
| crack px | 6.51% | 6.61% |
| contact px | 1.83% | 1.90% |
| interconnect px | 0.084% | 0.071% |
| corrosion px | 0.057% | 0.051% |
| images with crack / contact / interconnect / corrosion | 3,788 / 8,052 / 203 / 55 | 918 / 1,984 / 44 / 12 |

- Only 230 train images have no defect class, so false positives on clean cells are barely measured.

### 8.3 Our UCF splits
`~/mtp/datasets/splits_ucf_cv02/`; manifests give sha256 and per-class counts.

| List | n | How made |
|---|---|---|
| `train.txt` / `test.txt` | 9,562 / 2,289 | official release split |
| `val957_seed0.txt` | 957 | carved from train |
| `sl20_seed0.txt` | 1,912 | 20% labelled, from train minus val |
| `sl5_seed0.txt` | 478 | nested in sl20 |
| `sl1_seed0.txt` | 96 | nested in sl5; **no corrosion image, 2 interconnect images** |
| `unlabeled_sl{20,5,1}_seed0.txt` | 7,650 / 9,084 / 9,466 | train minus the labelled subset (includes val images) |

- Stratified on the per-image defect-presence signature (`manifest.json`).
- We use our own lists: Jha's released lists put 1,769 of the 2,289 public test images into their training lists (`MTP_session_handoff_2026-10-07.md` §3.4).

### 8.4 Problems with UCF-EL (`ucf_el_report.md` §3, §6, §10)
- **Leakage.**
  - The official split is by cell, not module: 291 of 358 module IDs have cells in both splits.
  - The same physical cell often appears under different module IDs.
  - **25% (confirmed tier) to 44% (possible tier) of test cells have their physical twin in train.**
  - The report says a physical-module-disjoint re-split is needed before claiming a methodology gain. No re-split list exists in `~/mtp/datasets/splits_ucf_cv02/` as of 11 Oct 2026.
- **Validation = test in the official code.** `train.py` builds its val set from the test split; the repo's last commit is "use test set for val".
- **Label agreement between twin copies:** crack IoU 0.57, contact 0.25.
- **Strict-IoU ceiling under a 1 px shift:** crack 0.954.

### 8.5 How the project used UCF-EL
- **Old era** (pre-reset and phase 1). Reproductions of Fioresi, Jha PV-S3 and others, plus SL and Mean Teacher runs at 20/5/1%.
  - Old-era numbers: label gap 0.54 (100%) → 0.41 (5%) → 0.23 (1%) (`MTP_session_handoff_2026-10-07.md` §1).
  - It is mostly a rare-class gap: interconnect and corrosion explain 64–78% of it (`ucf_el_report.md` §7).
  - The old UCF Mean Teacher results used SemiCE and are **invalid** (see `06_history_phase0_phase1.md`).
- **P15** (`protocols/P15_ucf_encoder_transfer.md`):
  - one DeepLabV3+ (ResNet-34) pretraining run on **all 9,562 UCF train cells** with the reproduced Fioresi recipe;
  - its encoder then initialises BenchmarkEL fine-tuning at 5% and 10% on gaint;
  - leakage check: UCF train vs BenchmarkEL val+test, maximum normalised correlation 0.79, none ≥ 0.90.
  - Results pending at the time of writing.

---

## 9. Datasets considered but not used
From `literature/notes/F04_el_datasets_census.md` §2 and `to_human/directions_2026-10-10.md`.

| Dataset | Why it came up | Why not used (so far) |
|---|---|---|
| BenchmarkEL `20220723` (642), `20221008` (695) | more labels; cleaned cracks | splits were reshuffled (48 of our train moved to test, 38 of our test to train), so numbers are not comparable; only the 106 new `20221008` cells are used (E1) |
| E-SCDD full set (903 images) | more cleaned labels | only its masks for our 577 cells were used. A full download was not done; the user's answer "conside rit" was ambiguous (`sources/chat/claude_session_summaries_2026-10-07_to_11.md`) |
| ELPV (2,624 cells, image-level labels) | = BMRK cells; free weak labels | not an independent pool or test set; weak supervision not run |
| PVEL-AD (36,543 NIR cells, boxes) | weak supervision, unlabelled data | access by request form; NIR, mostly poly cells, a domain shift |
| PV-Vision, MultiSolSegment (585, multi-label) | extra sources | possible overlap with SDLE (CWRU) and LBNL; not checked |
| Dropbox pool beyond 11,938 (>150k) | more unlabelled data | only 11,938 downloaded |

---

## 10. Preprocessing and input pipeline (brief)
Details are in `14_code_and_infrastructure.md`.

**BenchmarkEL**
- Grayscale uint8 via PIL `convert("L")`.
- Input size 512.
- Normalisation mean 0.5, std 0.25 (`configs/base.yaml` on gaint).
- One input channel. ImageNet encoders get their first convolution summed over RGB, as `smp` does (`protocols/P15_ucf_encoder_transfer.md`).

**Augmentation names** (`protocols/P6_corrected_baseline.md`):
- `strong` (old era): flips, rot90, ±5° rotation, blur, noise, brightness/contrast.
- `labelsafe` (P6 onward): flips, rot90, brightness/contrast only.
  - Rotation resamples 1–2 px cracks; blur and noise can erase them.
  - Phase 0 found that a GaussNoise argument bug made noise erase cracks; the pre-fix results are invalid (`sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`).

**UCF-EL** (reproduced Fioresi recipe, P15): shorter side 295, 256 crops, CE with ignore 128.

---

## 11. Where the data lives

| What | Local (`yugma` machine) | gaint (`noob@172.18.22.20`) | cv02 (`cv02@10.8.1.106`) |
|---|---|---|---|
| BenchmarkEL clone | `~/mtp/datasets/BenchmarkELimages/` | `/home/noob/work/datasets/BenchmarkELimages/` | no clone; labelled images and old masks in `/tmp/noob_el/el-fault-detection/data/labeled/{images,masks_coded}` |
| Repo data dir (symlinks) | – | `/home/noob/work/el-fault-detection/data/` | `/tmp/noob_el/el_p7/data`; the `el_p13` and `el_p16` worktrees' `data` link to it; its `labeled/images` and `labeled/masks_coded` link to `/tmp/noob_el/el-fault-detection/data/labeled/`, and `labeled/masks_escdd` links to `/tmp/noob_el/masks_escdd` |
| Old masks | `dataset_20211104/masks_coded_*` | `data/labeled/masks_coded/` | same path in `data/` |
| Revised masks | – | `data/labeled/masks_escdd/`, `data/escdd_masks/{train,val,test}/` | `/tmp/noob_el/masks_escdd` (as `data/labeled/masks_escdd`), plus `data/escdd_masks/{val,test}/` |
| Split lists | `~/mtp/datasets/splits_benchmark/` (copy) | `data/splits/` (committed in git) | `data/splits/` |
| External pool | lists only (`splits_benchmark/external_unlabeled*.{txt,csv}`) | raw: `/home/noob/work/sa-unetpp-ssl-el/data/unlabeled/images`; converted: `data/unlabeled/images_512/` | `data/unlabeled/images_512/` (11,938 files) |
| ext106 extension | – | – | `/tmp/noob_el/ext117/` |
| UCF-EL | `~/mtp/datasets/UCF-EL-Defect/` (repo files, annotation guide), `~/mtp/datasets/splits_ucf_cv02/` | `/home/noob/work/datasets/UCF-EL-Defect/` | `/tmp/noob_el/datasets/UCF-EL-Defect/training`, linked as `data/ucf_el` |

- cv02 keeps everything under `/tmp/noob_el`. Treat it as non-permanent storage: it is `/tmp`.
- `data/` is not in git except `data/splits/` and `data/README.md`.

---

## 12. Common confusions (for the guide to correct)
1. **"592 images".** The user wrote this on 11 Oct. The labelled dataset is **582** cells: 478 + 54 + 50.
2. **"Trained on 47 images and tested on the same 47."** 47 is the 10% labelled subset (int(478 × 0.1)). The user's first message (7 Oct) describes a model trained on 47 images and scored on the same 47 at about 0.3 crack IoU. That was the "can it even fit the training images?" question, which P1 tested. See `08_experiments_P1_P7_diagnostics.md`.
3. **Fractions are of the 478 train cells,** not of all 582. Val and test are never used for training.
4. **Run-name seed vs split seed.** `_s3` is training seed 3; the labelled subset is always split seed 0.
5. **"Test has 50/50 crack cells" vs "48/50".** Old masks give 50; revised masks give 48. Inactive: 17 (old) vs 16 (revised).
6. **UCF crack ≠ BenchmarkEL crack** (region vs line). Never compare their IoUs directly.
7. **The external pool is not "more of the same".** Two of five sources, different contrast, never harmonised.

## Related docs
- `00_START_HERE.md`
- `01_project_overview_and_scope.md`
- `02_domain_primer_EL_and_defects.md`: what the classes and images mean
- `04_glossary_and_naming.md`: arm names (A, D, B, C, m, x, s, M, g, S)
- `06_history_phase0_phase1.md`: old-era data handling and invalid results
- `07_methodology_rules_and_statistics.md`: how val/test composition shapes the rules
- `08_experiments_P1_P7_diagnostics.md`: P3 label versions, P6 baseline
- `09_experiments_P8_P12_ssl_series.md`: external pool arms
- `10_experiments_P13_P16_E1.md`: P14 (old vs revised masks), P15 (UCF pretraining), P16 (fractions), E1 (extension)
- `13_problems_pitfalls_open_issues.md`
- `14_code_and_infrastructure.md`: loaders, configs, paths
