# E-SCDD: full download, audit and analysis (12 Oct 2026)

Requested by the user on 12 Oct: "download the full ESCDD data, audit it analyse it, report it in the handbook, with precise details", and "also look at the E SCDD dataset paper". This is the primary record; the handbook's `17_escdd_dataset_audit.md` teaches the same content. No training or scoring was run. Every number below was measured from the downloaded files with the scripts in `scripts/` (outputs in `out/`), or quoted from the paper where it says "paper".

## 0. Headline findings
1. **E-SCDD's crack and inactive labels are BenchmarkEL `20221008`'s labels, unchanged.** For the 693 images E-SCDD shares with `20221008`, the images are pixel-identical. The masks differ in 66 images, and only between spacing classes (sp multi → sp multi halfcut and similar). **Not one crack (14) or inactive (11) pixel differs.** So the crack-label cleaning that P3 and P14 measured (+0.05 to +0.08 crack IoU) was done by the BenchmarkEL maintainers (Pratt et al.) in their `20221008` release, not by E-SCDD. E-SCDD redistributes those masks.
2. **The release is not the dataset the paper describes.**
   - The paper describes 1,000 annotated images (695 original, 110 new real, 195 synthetic) plus 1,768 unlabelled synthetic.
   - The HuggingFace release has 903 annotated images: 693 original, 117 new real (`_rf` suffix) and 93 synthetic. It contains no unlabelled synthetic images.
3. **E-SCDD's train split contains 93 synthetic diffusion images.** They are named `<k>-<base>_<class>_rf.png`, were generated from only 4 real cells, and carry 11.7% of all E-SCDD crack pixels. Anyone training on E-SCDD must filter them.
4. **100 of the 117 newly annotated real cells are in our external unlabelled pool.** They are pixel-matched to our pool copies (correlation ≥ 0.984). The pool was used as unlabelled training data in P9–P12 "x" arms and in P16 Sx100.
5. **E-SCDD's test split is not a better test set for us.**
   - Inactive appears in only 9 of its 82 test cells, and 3 cells hold 81.5% of the inactive pixels. Our test has 16 inactive cells with a top-3 share of 59%.
   - 48 of its test cells are in our training split.
6. **Our training masks (`masks_escdd`) equal E-SCDD's in 560 of 577 cells.**
   - The other 17 differ only where P6 mapped scuff (25) and star (28) pixels back to their `20211104` labels.
   - That remap added 236 crack pixels (0.26% of test crack pixels) to 2 test cells, which is why our test has 48 crack cells against E-SCDD's own 46.
   - The extra 583rd entry in `masks_escdd` is a `README.txt`.
7. **P3 and F04 do not conflict.** Their crack-agreement numbers use different denominators:
   - P3 pools over all crack images: test 0.745.
   - F04 pools only over images whose mask changed: test 0.693.
   - Both reproduce exactly from the downloaded files.

## 1. What was downloaded (all verified)

| What | Source and revision | Files | Size | Verification | Local path |
|---|---|---|---|---|---|
| E-SCDD (canonical) | HuggingFace `snt-ubix/escdd`, commit `8c8cba9a18d65fda8c319d186b1db9f1b804b71e`, last modified 2025-11-24, MIT | 1,810: 903 images + 903 masks + `README.md`, `ListOfClassesAndColorCodes_20221008.csv`, `class_explanation.json`, `.gitattributes` | 222.6 MB | every file's size and LFS sha256 matched the HF API listing | `~/mtp/datasets/escdd_full/` (API listing: `~/mtp/datasets/escdd_full_hf_api.json`) |
| E-SCDD mirror | HuggingFace `shivahanifi/extended-scdd`, commit `06fc294ae2cacfdd7966783d59dd4db771c5dd38`, 2025-11-10 (the link in the paper's GitHub README) | 3,481 | 487.3 MB | size + sha256 | `~/mtp/datasets/escdd_mirror_shivahanifi/` |
| BenchmarkEL `20221008` and `20220723` releases | GitHub `TheMakiran/BenchmarkELimages` tree `768b5e7` (2024-03-10). Originals only: the `flip_`/`mirror_`/`rotate_` train copies were excluded. | 2,086 and 1,927 | about 420 and 407 MB with copies on the server | copied from gaint's clone of the same commit; every file's git blob SHA-1 matched the GitHub tree | `~/mtp/datasets/BenchmarkEL_releases/` (tree: `github_tree_768b5e7.json`) |
| Paper | arXiv 2511.09604v1 (12 Nov 2025), PDF and LaTeX source | 1 PDF | 19.5 MB | – | `~/mtp/research/papers/hanifi2025_escdd_2511.09604.pdf` (local only, do not redistribute); note: `literature/notes/A09_hanifi2025_escdd.md` |

**Mirror vs canonical.**
- **Base files.** The mirror's 903 base images, 903 masks, CSV and JSON are byte-identical (md5) to `snt-ubix/escdd`.
- **Extras.** The mirror adds two folders. Neither is used by anything in this project.
  - **`removed_padding/`: 789 images and 789 masks (train 615, val 90, test 84), all 512 × 512 RGBA.**
    - 433 are `_no_padding` versions, with the padding cropped away and the cell rescaled.
    - 352 are byte-identical copies of base files (cells without padding).
    - 4 test files are neither.
    - 32 of the masks still contain padding (class 7): train 23, val 4, test 5.
  - **`revised_binary_masks/`: 94 per-class binary masks** (e.g. `..._no_padding_bckgnd.png`).
- **URL.** The paper's link `huggingface.co/datasets/snt-ubix/e-scdd` redirects (HTTP 307) to `snt-ubix/escdd`.

## 2. The paper, and how the release differs from it
**Paper.** Hanifi, Jafarnejad, Köntges, Wentnagel, Kokkas, Frank, "Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anomaly Generation in Photovoltaic Electroluminescence Images", arXiv 2511.09604 (eess.IV), 8 pages.
- **Affiliations:** University of Luxembourg (SnT), ISFH Hamelin, SolarCleano.
- **Main contribution:** PV-DDPM, a mask-conditioned diffusion model that generates EL images. E-SCDD is the dataset contribution.
- **"SCDD"** in the paper is BenchmarkEL (Pratt et al. 2023). Its 695 images and 29 classes are the `20221008` release.

| Item | Paper | HF release (measured) |
|---|---|---|
| Annotated images | 1,000 = 695 SCDD + 110 new real + 195 synthetic | **903** = 693 SCDD + 117 new real (`_rf`) + 93 synthetic |
| SCDD images dropped | none mentioned | 2 of `20221008`'s 695 are absent: `BMRK_02125_cell1223` (one of our train cells) and `CSIR_00308_r5_c3` (one of E1's 106) |
| New real images by cell type | 40 multi, 43 multi half-cut, 14 mono, 13 IBC dogbone | 40 multi, 43 multi half-cut, 18 mono, 16 IBC dogbone (cell type = largest spacing class in the mask) |
| Synthetic annotated, by type | 195: 80 IBC, 65 mono, 30 half-cut multi, 20 multi | **93**: 50 IBC, 35 mono, 8 multi, 0 half-cut |
| Unlabelled synthetic | 1,768 (abstract), 1,786 (introduction), 1,788 generated (results) | **none** |
| Classes | 30: 16 defects + 14 features; new feature `sp multi halfcut` (29) | CSV ids 0–29; identical to `20221008`'s CSV plus id 29. Ids 0–23 match our `20211104` CSV except a rename: 18 "corrosion" → "corrosion rbn" |
| "Refined pixel-level annotations" (HF card) | the only refinement described is relabelling half-cut multi spacing from `sp multi` to `sp multi halfcut` | confirmed: see §4 |
| Splits | each synthetic image placed in its base image's split ("standardized splits" is the HF card's phrase, not the paper's) | = `20221008` splits except 3 cells (§5). All 93 synthetic images and their 4 bases are in train |

**How the paper says the 110 new real cells were annotated:**
- **Selection.** They were chosen from BenchmarkEL's unlabelled pool, "selected randomly" per cell type after a quality screen.
- **Annotation.** On Roboflow, using Smart Polygon, a Segment Anything model fine-tuned on SCDD.
- **Review in three stages:** an annotator; a CV specialist with PV expertise; a senior PV expert's QA.
- **Tool.** The paper says an annotation-assistant tool with class definitions is in the GitHub repo `sntubix/pv-ddpm`. The repo tree (last push 2025-11-17, saved in `out/provenance/`) shows no such tool. It has the diffusion code, `dataset.py`, `utils/` and a copy of the dataset.

**Other results in the paper** (not reproduced; these are claims):
- **PV-DDPM.** A DDPM with a cosine schedule, conditioned on binary masks concatenated with the noisy image.
  - Training: Adam, lr 5e-4, batch 8, EMA, early stopping on val loss.
  - It is fine-tuned per cell type. Padding was removed to avoid dark-edge artefacts.
  - It generates 10 samples per conditioning mask.
- **Image quality** is measured by FID/KID with a DeepLabv3-ResNet101 fine-tuned on E-SCDD as the feature extractor. FID ranges from 2.46 (multi) to 6.42 (IBC), average 4.10.
- **Downstream test: AA-CLIP (a vision-language anomaly detector) trained on SCDD vs E-SCDD.** Full-shot, E-SCDD vs SCDD:
  - pixel AUC 94.96 vs 93.26;
  - pixel AP 55.47 vs 47.13 (+8.34);
  - image AUC 79.60 vs 52.11.
  - **Caveats (measured or read from the paper's own table):**
    - one number per setting, with no seeds or variance reported;
    - the two test sets differ: in the released E-SCDD, the test adds 11 new cells, drops 2 (both dropped cells were `20221008` test cells) and moves 3. The paper's 1,000-image version may differ again;
    - at 16 and 32 shots E-SCDD is worse on pixel AP (19.69 vs 39.25; 25.69 vs 36.66);
    - SCDD's full-shot image AUC of 52.11 is near chance.
  - Reading: so the comparison does not isolate the effect of the added data.
- **A segmentation baseline exists elsewhere.** Hanifi et al. 2026 (LNCS, DOI 10.1007/978-981-96-8892-0_4) segments SCDD's 29 classes with several encoder-decoders. That paper was not read.

## 3. Inventory and file checks (`out/inv_escdd.json`)

| Split | Files | Original (`20221008`) | New real (`_rf`) | Synthetic |
|---|---|---|---|---|
| train | 731 | 552 | 86 | 93 |
| val | 90 | 70 | 20 | 0 |
| test | 82 | 71 | 11 | 0 |
| all | **903** | **693** | **117** | **93** |

**Naming**
- Original cells use BenchmarkEL stems, e.g. `CSIR_00391_r2_c5`.
- New real cells add `_rf`, e.g. `CSIR_00067_r4_c3_rf`.
- Synthetic files are `<k>-<base stem>_<conditioning class>_rf.png` with k = 1–10, e.g. `10-CFVS_00114_r2_c5_crack_rf.png`. Regex for filtering: `^\d+-.+_rf\.png$`.

**Formats**
- Every image and mask is paired, with none orphaned.
- All 903 images are RGBA 512 × 512 with alpha 255 everywhere.
- 194 CSIR images (143 original, 51 `_rf`) carry some colour.
  - Per-image channel spread (max \|R−G\| + max \|G−B\|): median 16, maximum 110 grey levels, e.g. `CSIR_00092_r12_c5` (mean spread 7.0).
  - 113 of them are among our 582. Our copies are the same images, so this was already true of our data.
  - Our loader converts to grey with PIL `convert("L")`.
- All masks are mode L, uint8, 512 × 512, with values within 0–29.

**Sources** (original + `_rf`, train / val / test):

| Source | Train | Val | Test |
|---|---|---|---|
| ARTS | 161 | 17 | 19 |
| BMRK | 53 | 6 | 5 |
| CFVS | 143 | 22 | 22 |
| CSIR | 267 | 43 | 34 |
| SDLE | 14 | 2 | 2 |

**Cell types** of the original cells, train / val / test, by the largest spacing class in the mask:

| Type | Train | Val | Test |
|---|---|---|---|
| multi | 228 | 24 | 26 |
| mono | 207 | 28 | 28 |
| multi half-cut | 47 | 8 | 7 |
| IBC dogbone | 10 | 1 | 1 |
| mono half-cut | 2 | 1 | 1 |
| no spacing class | 58 | 8 | 8 |

No mask mixes spacing types.

### 3.1 Classes: cells / pixels per split (original + `_rf`; synthetic separately)

| id | Class | Train | Val | Test | Synthetic (train) |
|---|---|---|---|---|---|
| 0 | bckgnd | 638 / 112,043,240 | 90 / 15,780,147 | 82 / 14,899,610 | 93 / 20,879,247 |
| 1 | sp multi | 257 / 2,864,347 | 32 / 327,975 | 29 / 332,799 | 8 / 65,410 |
| 2 | sp mono | 219 / 2,536,050 | 32 / 398,564 | 30 / 384,025 | 35 / 410,794 |
| 3 | sp dogbone | 21 / 418,642 | 3 / 62,041 | 4 / 103,215 | 50 / 1,293,920 |
| 4 | ribbons | 608 / 7,147,982 | 85 / 1,067,789 | 77 / 960,384 | 43 / 716,046 |
| 5 | border | 348 / 3,365,831 | 50 / 523,443 | 36 / 355,302 | 0 |
| 6 | text | 12 / 9,119 | 2 / 2,368 | 2 / 1,406 | 0 |
| 7 | padding | 352 / 31,973,614 | 53 / 4,440,394 | 39 / 3,593,235 | 0 |
| 8 | clamp | 1 / 1,238 | 0 | 0 | 0 |
| 9 | busbars | 69 / 301,085 | 6 / 19,426 | 5 / 20,192 | 0 |
| 10 | crack rbn edge | 36 / 3,674 | 9 / 767 | 3 / 229 | 29 / 3,587 |
| **11** | **inactive** | **65 / 301,708** | **9 / 48,092** | **9 / 69,978** | 11 / 17,213 |
| 12 | rings | 7 / 22,151 | 1 / 2,856 | 2 / 11,901 | 24 / 22,924 |
| 13 | material | 180 / 885,477 | 33 / 169,568 | 21 / 116,096 | 67 / 194,122 |
| **14** | **crack** | **275 / 323,907** | **39 / 59,340** | **45 / 74,883** | 64 / 60,587 |
| 15 | gridline | 371 / 847,259 | 55 / 123,298 | 48 / 118,698 | 42 / 134,952 |
| 16 | splice | 53 / 53,033 | 5 / 5,423 | 7 / 9,683 | 0 |
| 17 | dead cell | 5 / 169,426 | 1 / 29,876 | 1 / 43,164 | 14 / 480,433 |
| 18 | corrosion rbn | 13 / 125,099 | 3 / 26,602 | 2 / 19,389 | 0 |
| 19 | belt mark | 8 / 79,767 | 2 / 6,421 | 0 | 0 |
| 20 | edge dark | 44 / 641,129 | 6 / 63,365 | 4 / 46,337 | 25 / 74,659 |
| 21 | frame edge | 147 / 1,356,257 | 23 / 178,462 | 14 / 130,584 | 0 |
| 22 | jbox | 7 / 6,026 | 0 | 2 / 1,738 | 0 |
| 23 | meas artifact | 4 / 107 | 1 / 476 | 1 / 13 | 1 / 11 |
| 24 | sp mono halfcut | 2 / 20,234 | 1 / 8,803 | 1 / 17,533 | 0 |
| 25 | scuff | 50 / 73,052 | 7 / 10,162 | 7 / 12,134 | 0 |
| 26 | corrosion cell | 18 / 294,754 | 4 / 27,177 | 2 / 30,616 | 0 |
| 27 | brightening | 29 / 398,672 | 6 / 57,370 | 3 / 46,452 | 7 / 23,732 |
| 28 | star | 26 / 8,412 | 4 / 883 | 6 / 1,060 | 9 / 1,755 |
| 29 | sp multi halfcut | 81 / 976,580 | 14 / 151,872 | 10 / 95,152 | 0 |

Synthetic masks have no padding, border, frame or busbar pixels: the paper removed padding for generation.

### 3.2 Crack and inactive per split and group

| Split | Group | Cells | With crack | Crack px | With inactive | Inactive px |
|---|---|---|---|---|---|---|
| train | original | 552 | 241 | 305,554 | 56 | 264,383 |
| train | `_rf` | 86 | 34 | 18,353 | 9 | 37,325 |
| train | synthetic | 93 | 64 | 60,587 | 11 | 17,213 |
| val | original | 70 | 29 | 57,756 | 8 | 45,908 |
| val | `_rf` | 20 | 10 | 1,584 | 1 | 2,184 |
| test | original | 71 | 37 | 69,981 | 9 | 69,978 |
| test | `_rf` | 11 | 8 | 4,902 | 0 | 0 |

**Concentration** (original + `_rf`):

| Split | Class | Cells | Total px | Top-1 share | Top-3 share |
|---|---|---|---|---|---|
| test | inactive | 9 | 69,978 | 43.5% | **81.5%** |
| test | crack | 45 | 74,883 | 17.9% | 46.1% |
| val | inactive | 9 | 48,092 | 40.1% | 80.9% |
| val | crack | 39 | 59,340 | 18.4% | 50.0% |

For comparison, our test (revised masks) has inactive in 16 cells with a top-3 share of 58.8%, and crack in 48 cells with a top-3 share of 32.4% (`results/p6/README.md` §4; recomputed here).

## 4. E-SCDD vs BenchmarkEL `20221008` (`out/xref.json`)
**Images.** The 693 original cells are pixel-identical to `20221008` after grey conversion: mean absolute difference 0 for all 693.

**Masks.** 627 are identical and 66 differ.

| Change (`20221008` → E-SCDD) | Images | Pixels |
|---|---|---|
| 1 sp multi → 29 sp multi halfcut | 62 | 552,426 |
| 2 sp mono → 1 sp multi | 1 | 15,861 |
| 1 sp multi → 2 sp mono | 2 | 12,801 |
| 3 sp dogbone → 1 sp multi | 1 | 1,580 |
| any change to crack (14) or inactive (11) | **0** | **0** |

- The 66 changed masks are 64 CSIR, 1 CFVS and 1 ARTS. Only 3 of them are among our 577.
- Of our 577 cells, 574 masks are pixel-identical to `20221008`'s (573 are also byte-identical files; `CFVS_00180_r8_c6` was re-encoded).
- **So for crack and inactive, "E-SCDD masks" = "BenchmarkEL `20221008` masks".** The BenchmarkEL README says the later releases include "corrections to earlier versions of the same images". The correction procedure itself is not documented there.

**Membership.**
- 4 of our 582 cells (`ARTS_00057_r2_c5`, `CSIR_00178_r7_c1`, `CSIR_00179_r12_c4`, `CSIR_00179_r6_c1`) are in `20220723` but were dropped by `20221008`.
- `BMRK_02125_cell1223` is in `20221008` but was dropped by E-SCDD.
- These 5 are the 5 "train stems missing from E-SCDD" that keep their old masks in our `masks_escdd`.

## 5. Splits

**E-SCDD vs `20221008`.** Identical except for 3 cells:
- `CFVS_00114_r2_c5` moved test → train. It is the base of 35 synthetic images.
- `CSIR_00163_r1_c1` and `CSIR_00305_r7_c3` moved train → test.

**E-SCDD vs our split** (the 577 shared cells):

| Our split → E-SCDD split | train | val | test | Total |
|---|---|---|---|---|
| our train (473 present) | 379 | 46 | **48** | 473 |
| our val (54) | 45 | 6 | 3 | 54 |
| our test (50) | **39** | 4 | 7 | 50 |

- 185 of 577 cells sit in a different split (matches P3).
- **E-SCDD test (82 cells) = 7 of our test + 48 of our train + 3 of our val + 13 cells from the E1 extension (11 evaluated + 2 pool) + 11 `_rf` cells.**
- **So models trained on our split cannot be scored on E-SCDD's test, and the reverse also holds.**

**Module leakage inside E-SCDD** (module = `SRC_#####`; original + `_rf`):
- 487 modules, of which 70 have cells in more than one split.
- 44 of 82 test cells and 40 of 90 val cells come from modules that also have train cells.
- 22 modules are shared by val and test.

**Duplicates** (`scripts/analysis.py`, `scripts/dups_mad.py`). Method: 64 × 64 thumbnails with NCC ≥ 0.97 under 8 rotations/flips gave 1,281 candidate pairs. For these, full-resolution mean absolute difference (MAD) was computed, then correlation inside the non-padding cell area.

| Pair | Splits in E-SCDD | Evidence | Verdict |
|---|---|---|---|
| `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4` | train, train | pixel-identical | duplicate (known from `data_analysis/benchmark_el_report.md` §5; different masks) |
| `ARTS_00020_r5_c1` ≈ `ARTS_00081_r5_c1` | **train, val** | MAD 2.42, in-cell r 0.996 | the same cell. Ours has it as train ↔ test (known) |
| BMRK `cell2156`, `cell2169`, `cell2192`, `cell2197`, `cell2203` | all train | in-cell r 0.93–0.99 (depends on how padding is excluded), MAD 2.0–5.1 | **unresolved:** possibly similar but distinct cells; no split impact |

- All other candidates are explained by shared padding and frame structure (as in `benchmark_el_report.md` §5).
- `BMRK_00075_cell0255` (train) and `BMRK_00031_cell0091` (val) have byte-identical masks but different images.

## 6. Crack-label morphology (`out/analysis.json`, `crack_morph*`)
Definitions:
- width = crack pixels / skeleton pixels;
- fragments = 8-connected crack components.

| Set | Crack cells | Crack px | Width (pooled; median) | Fragments (total; median per cell) | Median px per cell |
|---|---|---|---|---|---|
| Our 577 shared cells, **E-SCDD (= `20221008`) masks** | 265 | 396,572 | 2.52; 2.46 | 1,288; 3 | 616 |
| Same cells, **our old `20211104` masks** | 265 | 327,754 | 2.17; 1.79 | 5,391; 4 | 532 |
| All 693 original E-SCDD cells | 307 | 433,291 | 2.59; 2.61 | 1,645; 3 | 629 |
| New `_rf` cells | 52 | 24,839 | 2.68; 2.33 | 928; 2 | 89.5 |
| Synthetic | 64 | 60,587 | 3.90; 3.62 | 256; 2 | 678 |

- **On the same cells, the `20221008` labels have 21% more crack pixels and 4.2× fewer fragments than ours, and are 0.35 px wider (pooled).** This is the "joined and widened" cleaning described in P3 and F04.
- **Width by source** (original cells): ARTS 1.78, CFVS 2.42, CSIR 2.88, BMRK 3.47, SDLE 2.05 (n = 3).
- **The new `_rf` annotations are inconsistent:**
  - the 3 ARTS `_rf` cells are 1-px lines (width 1.0, median 8 fragments);
  - 9 `_rf` cells have ≥ 10 fragments, and 3 have 128 to 380. Examples: `CSIR_00087_r10_c5_rf` has 380 fragments in 982 px, 324 of them ≤ 3 px; `CSIR_00127_r7_c5_rf` has 160; `CSIR_00087_r4_c4_rf` has 128.
  - In total 655 crack fragments of ≤ 3 px are in `_rf` masks. These are specks, not lines.
- **Synthetic crack labels are the widest** (3.9 px).

## 7. Synthetic images (`out/analysis.json`, `synthetic`)

| Base cell (split) | Cell type | Synthetic images | Conditioning classes |
|---|---|---|---|
| `CFVS_00114_r2_c5` (train; was test in `20221008`) | mono | 35 | bckgnd 8, gridline 10, material 9, crack 8 |
| `CSIR_00067_r4_c3_rf` (train) | IBC dogbone | 30 | crack 10, rings 7, material 7, bckgnd 6 |
| `CSIR_00094_r3_c5_rf` (train) | IBC dogbone | 20 | bckgnd 8, crack 7, rings 5 |
| `CSIR_00038_r11_c3_rf` (train) | multi | 8 | crack-rbn-edge 3, crack 3, material 1, bckgnd 1 |

- **The masks were re-annotated, not copied from the base.**
  - Pixel agreement with the base mask: median 0.94, minimum 0.65.
  - For crack-conditioned images, crack IoU with the base crack: median 0.436.
  - Two images (`7-` and `8-CSIR_00094_r3_c5_rf_crack_rf`) have identical masks.
- **Crack content:** 64 synthetic images contain crack and 11 contain inactive. Together they hold 60,587 crack pixels, 11.7% of all E-SCDD crack pixels, all in train.
- **What they look like.** The base's cell structure and defects stay in place, but global brightness and contrast change (`escdd_samples.png`, rows 1–3).

## 8. Relation to our data
Every E-SCDD file falls into exactly one group:

| Group | Cells | With crack | With inactive (px) | E-SCDD split (tr/va/te) | Sources |
|---|---|---|---|---|---|
| Our 582 (577 present) | 577 | 272* | 63 (371,111) | 463 / 56 / 58 | ARTS 194, CFVS 187, CSIR 119, BMRK 59, SDLE 18 |
| E1's 106-cell extension (105 present; `CSIR_00308_r5_c3` absent) | 105 | 32 | 10 (9,158) | 81 / 13 / 11 | CSIR 100, BMRK 5 |
| ext117 cells that are in our pool (E1 dropped these 11) | 11 | 3 | 0 | 8 / 1 / 2 | CSIR 11 |
| `_rf` cells in our external pool | 100 | 46 | 10 (39,509) | 74 / 16 / 10 | CSIR 97, ARTS 3 |
| `_rf` cells not in our pool | 17 | 6 | 0 | 12 / 4 / 1 | CSIR 17 |
| Synthetic | 93 | 64 | 11 (17,213) | 93 / 0 / 0 | CFVS 35, CSIR 58 (by base name) |

\* By E-SCDD's own masks. With our `masks_escdd` (§9) these cells give train 206 / val 23 / test 48 crack cells (train 209 when the 5 train stems absent from E-SCDD are included).

**The 100 `_rf` cells in our pool are the same images.**
- They were compared with our converted copies on gaint (`data/unlabeled/images_512/`):
  - Pearson r 0.984 to 0.99994 (9 in [0.95, 0.99), 55 in [0.99, 0.999), 36 ≥ 0.999);
  - same orientation;
  - median MAD 0.87 grey levels for cells native at 512 px, 1.74 for 1200 px cells that we downsampled.
- By our pool metadata they are 43 multi half-cells, 31 multi and 26 mono.

**Modules.** 23 of the 117 `_rf` cells come from modules that have cells in our 582 (19 train, 3 val, 1 train + test). 4 of the 122 cells that are neither in our 582 nor in our pool (E1's 105 + 17 `_rf`) share a module with our 582.

**New labelled cells available to us.** 233 real cells are not in our 582 (116 original + 117 `_rf`), +49% over our 478 train. Of these:
- 87 contain crack and 20 contain inactive;
- 111 are in our external pool;
- 105 are E1's evaluation set.

**If the test set were enlarged** (descriptive only, not a plan; the user decides):

| Candidate test set | Cells | Inactive cells | Inactive px | Inactive top-3 share | Crack cells | Crack top-3 share |
|---|---|---|---|---|---|---|
| Our test | 50 | 16 | 92,125 | 58.8% | 48 | 32.4% |
| A: our test + E1's 105 + 17 `_rf` not in pool (never trained on by any arm) | 172 | 26 | 101,283 | 53.5% | 86 | 23.9% |
| B: A + the 111 cells in our pool (clean only for arms that never used the external pool) | 283 | 36 | 140,792 | 42.7% | 135 | 21.2% |

- **Inactive pixels added by A are small** (9,158 px over 10 cells), so a pooled inactive IoU would still be about half decided by 3 cells.
- **A and B are mostly CSIR cells from unseen modules,** a different regime: L3 100% scores crack IoU 0.471 on test and 0.152 on the E1 extension (`results/e1/README.md`).

## 9. Our training masks (`masks_escdd`) vs E-SCDD
Copied read-only from gaint `data/labeled/masks_escdd/`: 582 masks plus `README.txt`. The README states the build: "577/582 from E-SCDD; 5 train stems absent from E-SCDD keep their 20211104 mask ... E-SCDD classes 24-29 ... are replaced by the 20211104 label at those pixels (17 images)".
- **Equal to E-SCDD in 560 of 577 cells.** In the other 17, only scuff (25) and star (28) pixels differ:

  | Remap | Pixels |
  |---|---|
  | 25 → 13 | 1,390 |
  | 25 → 0 | 1,207 |
  | 25 → 14 (crack) | 885 |
  | 28 → 0 | 176 |
  | 28 → 14 (crack) | 54 |
  | 28 → 1 | 8 |

- **Crack pixels added by the remap:** train 703, val 0, test 236.
  - 236 is 0.26% of the 92,074 test crack pixels.
  - 2 test cells (`ARTS_00047_r3_c1`, 34 px; `ARTS_00051_r3_c2`, 202 px) and 3 train cells (`ARTS_00051_r6_c2`, `CSIR_00117_r8_c4`, `CSIR_00176_r5_c2`) have crack only through this remap.
  - So our test has 48 crack cells, against 46 by E-SCDD's own masks.
- Inactive pixels are identical (train 266,709; val 12,277; test 92,125).
- The 5 non-E-SCDD stems equal their `20211104` masks.
- **The "583rd entry" on cv02 and gaint is this `README.txt`.** This closes the open question in handbook doc 03 §3.1.

## 10. P3 vs F04, reconciled
Crack IoU between our `20211104` masks and E-SCDD (= `20221008`) masks, pooled two ways:

| Split | Pooled over all crack images (P3's way) | Pooled over images whose mask changed (F04's way) |
|---|---|---|
| train | 0.81 (208 images) | 0.567 (156 images) |
| val | 0.732 (23) | 0.638 (18) |
| test | 0.745 (50) | 0.693 (42) |

Both reproduce the published numbers exactly. There is no conflict between the label sets: E-SCDD crack is identical to `20221008` crack.

Note on `out/analysis.json`: its `ours_vs_escdd_crack_iou.pooled_changed_only` pools over images whose *crack* changed (81 / 14 / 35 images), giving 0.55 / 0.638 / 0.68. The F04 column above pools over images whose *mask* changed (156 / 18 / 42), which is F04's definition and reproduces 0.567 / 0.638 / 0.693 (re-derived independently, 12 Oct).

## 11. Reading (interpretation; nothing here is a locked result)
- **Attribution.** The label cleaning behind P3 (+0.05 to +0.07 crack IoU from re-scoring) and P14 (+0.082 from training) is BenchmarkEL's own `20221008` correction, which E-SCDD redistributes. A thesis should cite Pratt et al.'s `20221008` release as the source of the revised crack labels and E-SCDD as where we got them. The experiments themselves are unaffected.
- **E-SCDD's own split is unusable with our models** (48 of its test cells are in our train), and its test is weaker for inactive than ours.
- **Extra labelled data exists (233 cells),** but it overlaps our external pool (111) and our E1 set (105). It is mostly CSIR from unseen modules, so it is a distribution shift rather than "more of the same". The `_rf` annotations are noisier for crack (specks, 1-px ARTS lines).
- **The synthetic images are not a usable augmentation source for our question.** There are only 93, from 4 bases, mostly IBC/mono. The paper's evidence that they help is one uncontrolled AA-CLIP comparison.
- **A method idea from the paper, not tested here:** a SAM model fine-tuned on SCDD as an annotation assistant (Smart Polygon), with tiered review. For WattCycle it is a possible route to cheaper pixel labels. The speckled `_rf` masks suggest the assistant's crack output needs cleaning.

## Files
- `scripts/download.py`: HF download with size and sha256 checks (argument: the API JSON).
- `scripts/download_bel.py`: BenchmarkEL release originals with git-blob SHA-1 checks.
- `scripts/inventory.py`: per-file inventory → `out/inv_escdd.json`.
- `scripts/crossref.py`: links to `20221008`, `20220723`, `20211104`, the external pool and ext117 → `out/xref.json`.
- `scripts/analysis.py`: class tables, cell types, crack morphology, modules, near-duplicate candidates, P3/F04 reconciliation, synthetic, concentration → `out/analysis.json`.
- `scripts/dups_mad.py`: full-resolution MAD for duplicate candidates → `out/dups_mad.json`.
- `out/provenance/`: the paper's GitHub README (links the mirror) and repo tree, fetched 12 Oct. The BenchmarkEL GitHub tree used for verification is `~/mtp/datasets/BenchmarkEL_releases/github_tree_768b5e7.json`.
- `scripts/montage.py`: `escdd_samples.png`, showing 3 synthetic sets with their bases and 3 `_rf` cells (crack red, inactive blue).
- `scripts/ours_vs_escdd.py`: produces `out/ours_vs_escdd.json`, covering:
  - §9 (`masks_escdd` vs E-SCDD);
  - the §8 pool pixel check and the enlarged-test table;
  - the mirror's padding count and the colour check.
  - Arguments: E-SCDD dir, mirror dir, a read-only copy of gaint `data/labeled/masks_escdd/`, read-only copies of the 100 pool images from gaint `data/unlabeled/images_512/`, `splits_benchmark/`, this folder.
- Run every script with `~/mtp/research/.venv/bin/python -I`. Fetch the inputs read-only (rsync from gaint).
