# 17. E-SCDD: the full download, the paper, and what the audit found

## What this covers
On 12 Oct 2026 the user asked: "download the full ESCDD data, audit it analyse it, report it in the handbook, with precise details", then "also look at the E SCDD dataset paper it might give useful insights". This doc covers:
- **what E-SCDD is,** and where it sits in the family of BenchmarkEL label sets;
- **what its paper claims,** and what the released data actually contains;
- **every audit finding,** with numbers;
- **what changes in this handbook** as a result (corrections);
- **what it could mean for the project.** These are options only; the user decides.

No model was trained or scored for this. Every number was measured from the downloaded files, except where marked "paper".

## Sources
- **`results/escdd_audit/README.md`:** the primary record, with full tables (copy in `sources/results/escdd_audit__README.md`).
- `results/escdd_audit/out/*.json`: raw outputs.
- `results/escdd_audit/scripts/`: the scripts.
- `results/escdd_audit/escdd_samples.png`: example images.
- `literature/notes/A09_hanifi2025_escdd.md`: notes on the paper (copy in `sources/literature/notes/`).
- `~/mtp/research/papers/hanifi2025_escdd_2511.09604.pdf`: the paper. Local only; do not redistribute.
- `~/mtp/datasets/BenchmarkELimages/README.md` (copy in `sources/data_analysis/BenchmarkELimages_README.md`): the line about corrections in later releases.
- Earlier context:
  - `results/p3_label_versions/README.md`;
  - `literature/notes/F04_el_datasets_census.md` §1a;
  - `03_datasets_and_splits.md` §3;
  - `08_experiments_P1_P7_diagnostics.md` (P3).

---

## 1. The short version
- **BenchmarkEL has three releases.** Our project uses the oldest, `20211104` (582 cells).
- **The crack cleaning came from BenchmarkEL itself.** The maintainers (Pratt et al.) later published `20221008` (695 cells). In it they corrected many crack labels: dotted labels joined, lines widened.
- **E-SCDD is a third party's repackaging of `20221008`,** by Hanifi et al. (2025). It:
  - renames one spacing class for half-cut cells;
  - adds 117 newly labelled real cells;
  - adds 93 AI-generated (synthetic) cells.
- **We got our revised labels from E-SCDD.** Since P6 we have trained and scored on these "E-SCDD revised masks".
- **The audit shows E-SCDD did not touch a single crack or inactive pixel of `20221008`.** So the "revised labels" that moved crack IoU by +0.05 to +0.08 (P3, P14) are BenchmarkEL's own `20221008` corrections, delivered through E-SCDD.
- **No experiment result changes.** What changes is how the source of the labels should be described and cited.

## 2. Family tree of the label sets

| Label set | Made by | Cells | What changed vs its parent | Role here |
|---|---|---|---|---|
| BenchmarkEL `20211104` ("old", `masks_coded`) | Pratt et al. | 582 (478 / 54 / 50) | – | our images and split; old-era labels |
| BenchmarkEL `20220723` | Pratt et al. | 642 | more cells, reshuffled splits; classes 24–27 added | not used |
| BenchmarkEL `20221008` | Pratt et al. | 695 (553 / 70 / 72) | more cells; **crack labels corrected** (joined, widened); class 28 (star) added | source of the crack/inactive labels we use; E1's 106 extension cells |
| **E-SCDD** (HF `snt-ubix/escdd`) | Hanifi et al., Univ. Luxembourg + ISFH + SolarCleano | 903 files: 693 + 117 + 93 | class 29 `sp multi halfcut`; 117 new real cells (`_rf`); 93 synthetic cells; 2 cells dropped; 3 cells moved split | where we downloaded the revised masks (P3, P6) |
| **our `masks_escdd`** | us (P6, 10 Oct) | 582 | 577 E-SCDD masks + 5 old masks; scuff/star pixels mapped back to their old labels in 17 cells | training and scoring labels for all P-series runs from P6 on |

**The source for the `20221008` corrections.** The BenchmarkEL README says the later releases "include additional images, additional classes, and corrections to earlier versions of the same images". It does not describe how the corrections were made.

## 3. The paper, in plain words
Hanifi et al., "Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anomaly Generation in Photovoltaic Electroluminescence Images", arXiv 2511.09604, Nov 2025. Full notes: `literature/notes/A09_hanifi2025_escdd.md`.

**Main idea.** A diffusion model (PV-DDPM) that paints a new EL cell image from a "layout" mask.
- The mask says where ribbons, cell gaps and defects should be, and the model fills in a realistic-looking image.
- It can be told to draw one defect type or several.
- It was fine-tuned separately for 4 cell types: mono, multi, half-cut multi, and IBC "dogbone" (back-contact cells).

**What "diffusion model" means here, briefly.** It learns to remove noise from images step by step. Starting from pure noise plus the layout mask, it denoises into a new image that respects the mask.

**The dataset contribution (E-SCDD)**, as the paper describes it:
- **1,000 labelled images:** 695 BenchmarkEL `20221008` + 110 new real cells + 195 synthetic.
- **1,768 unlabelled synthetic images.**
- **30 classes:** a new class 29 for the gaps between half-cut multi cells.

**How the new real cells were labelled.**
- They used Roboflow's Smart Polygon, a Segment Anything model they fine-tuned on BenchmarkEL.
- Three reviews followed: annotator, then a CV specialist with PV expertise, then a senior PV expert.

**The evidence that E-SCDD helps** is one comparison with AA-CLIP, a vision-language anomaly detector. Training on E-SCDD instead of BenchmarkEL gave:
- pixel AP 55.47 vs 47.13;
- pixel AUC 94.96 vs 93.26.

**Weak points of that evidence:**
- one number per setting, with no seeds;
- different test sets;
- E-SCDD is worse at 16 and 32 shots (pixel AP 19.69 vs 39.25; 25.69 vs 36.66);
- BenchmarkEL's full-shot image AUC is 52.11, near chance;
- no segmentation experiment at all.

## 4. What was downloaded (all verified)

| What | Where it now is | Check |
|---|---|---|
| E-SCDD, HF `snt-ubix/escdd` at commit `8c8cba9a...`: 1,810 files, 222.6 MB | `~/mtp/datasets/escdd_full/` | size and sha256 of every file |
| Mirror HF `shivahanifi/extended-scdd` at `06fc294a...`: 3,481 files, 487.3 MB. It has the same 903 base files byte-for-byte, plus no-padding variants and per-class binary masks. | `~/mtp/datasets/escdd_mirror_shivahanifi/` | size + sha256; md5 equality of the base files |
| BenchmarkEL `20221008` and `20220723`, original cells only, GitHub tree `768b5e7` | `~/mtp/datasets/BenchmarkEL_releases/` | git blob SHA-1 of every file (copied from gaint's clone of the same commit) |
| The paper (PDF) | `~/mtp/research/papers/hanifi2025_escdd_2511.09604.pdf` | – |

All of this is on the user's machine only. Nothing was copied to cv02 or gaint.

## 5. Audit findings
Each finding gives the number and where it comes from (sections of `results/escdd_audit/README.md`).

### 5.1 The release is not the dataset described in the paper (§2)

| | Paper | Released (measured) |
|---|---|---|
| Labelled images | 1,000 = 695 + 110 + 195 | **903 = 693 + 117 + 93** |
| Unlabelled synthetic | 1,768 (abstract), 1,786 (introduction), 1,788 (results) | **0** |
| Synthetic by cell type | 80 IBC, 65 mono, 30 half-cut multi, 20 multi | 50 IBC, 35 mono, 8 multi, 0 half-cut |
| New real by cell type | 40 multi, 43 half-cut multi, 14 mono, 13 IBC | 40, 43, 18, 16 |

- **Two `20221008` cells are missing from E-SCDD:**
  - `BMRK_02125_cell1223`, one of our train cells;
  - `CSIR_00308_r5_c3`, one of E1's 106 cells.

### 5.2 Crack and inactive labels are exactly `20221008`'s (§4)
- **Images.** All 693 shared images are pixel-identical to `20221008`.
- **Masks.** 627 masks are identical. The other 66 differ only between cell-gap ("spacing") classes:
  - 62 masks: sp multi → sp multi halfcut, 552,426 px;
  - 4 masks: swaps among sp mono, sp multi and sp dogbone.
- **Crack and inactive pixels changed: 0.**
- **Our cells.** 574 of our 577 shared cells have masks pixel-identical to `20221008`'s.

### 5.3 What P6 did to E-SCDD's masks (our `masks_escdd`) (§9)
- **Equal to E-SCDD in 560 of 577 cells.**
- **In 17 cells, P6 replaced E-SCDD's scuff (25) and star (28) pixels with the old label at those pixels,** to keep our 24-class scheme.
- **Side effect:** 939 crack pixels came back from the old masks (train 703, test 236).
  - In the test set that is 0.26% of crack pixels.
  - 2 test cells have crack only because of this: `ARTS_00047_r3_c1` (34 px) and `ARTS_00051_r3_c2` (202 px).
  - That is why our test counts 48 crack cells where E-SCDD's own masks give 46.
  - Inactive is untouched.
- **The mysterious 583rd entry** in `masks_escdd` (doc 03 §3.1) is a `README.txt` describing this build. Solved.

### 5.4 Synthetic images sit inside E-SCDD's train split (§3, §7)
- **93 files,** named like `10-CFVS_00114_r2_c5_crack_rf.png`: sample 10, generated from base cell `CFVS_00114_r2_c5`, conditioned on the crack layout.
- **Only 4 base cells:**
  - `CFVS_00114_r2_c5`: 35 images;
  - `CSIR_00067_r4_c3_rf`: 30;
  - `CSIR_00094_r3_c5_rf`: 20;
  - `CSIR_00038_r11_c3_rf`: 8.
- **All 93 and their bases are in train.**
  - `CFVS_00114_r2_c5` was a *test* cell in `20221008`. E-SCDD moved it to train, likely so its synthetic copies sit in the same split.
- **They hold 11.7% of all E-SCDD crack pixels.**
- **Their masks were redrawn, not copied:** crack IoU with the base crack has a median of 0.436 for crack-conditioned images.
- **Their crack labels are the widest in the set:** 3.9 px.
- **Anyone training on E-SCDD must decide whether to keep them.** Filter regex: `^\d+-.+_rf\.png$`.

### 5.5 The 117 new real cells (§3, §6, §8)
- **Sources:** 114 CSIR, 3 ARTS.
- **Content:** 52 contain crack, 10 contain inactive.
- **100 of them are in our external unlabelled pool** (the 11,938 cells used by the "x" SSL arms P9–P12 and P16 Sx100). They are the same images: Pearson r ≥ 0.984 against our pool copies, same orientation.
- **Their crack labels are less consistent than `20221008`'s:**
  - 3 cells have 128 to 380 crack fragments, most of them ≤ 3 px specks;
  - the 3 ARTS cells are 1-px lines;
  - median crack size is small: 89.5 px per cell.

### 5.6 Splits and leakage (§5)
- **E-SCDD's split = `20221008`'s,** except 3 cells moved: `CFVS_00114_r2_c5` test → train; `CSIR_00163_r1_c1` and `CSIR_00305_r7_c3` train → test.
- **Against our split (577 shared cells):**
  - 185 cells are in a different split;
  - 48 of E-SCDD's 82 test cells are in our train;
  - 39 of our 50 test cells are in E-SCDD's train.
  - So models trained on our split must never be scored on E-SCDD's test, and the reverse also holds.
- **Inside E-SCDD:** 44 of 82 test cells come from modules that also have train cells.
- **Duplicates:**
  - `CFVS_00015_r7_c4` = `CFVS_00016_r7_c4`, both train;
  - `ARTS_00020_r5_c1` ≈ `ARTS_00081_r5_c1`, train vs **val** in E-SCDD (train vs test in ours, already known);
  - a cluster of 5 BMRK train cells is very similar but unresolved.

### 5.7 E-SCDD's test set would not fix our inactive problem (§3.2, §8)
- **E-SCDD test:** 82 cells. Inactive is in 9, and 3 cells hold 81.5% of inactive pixels.
- **Our test:** 50 cells. Inactive is in 16, top-3 share 58.8%.

**Larger test sets that could be built** (descriptive; not a plan):

| Option | Cells | Inactive cells | Inactive top-3 share | Caveat |
|---|---|---|---|---|
| Our test only | 50 | 16 | 58.8% | – |
| A: + E1's 105 + 17 new cells not in our pool | 172 | 26 | 53.5% | mostly CSIR from unseen modules; added inactive is small (9,158 px over 10 cells) |
| B: A + 111 cells in our pool | 283 | 36 | 42.7% | not clean for arms that trained on the external pool |

### 5.8 P3 and F04 do not conflict (§10)
Doc 03 §3.2 flagged that P3 gives test crack IoU 0.745 between old and revised labels, while F04 gives 0.693. Both are right; they pool over different images.

| Pooled over | Test | Val | Train |
|---|---|---|---|
| all crack images (P3) | 0.745 | 0.732 | 0.81 |
| only images whose mask changed (F04) | 0.693 | 0.638 | 0.567 |

Recomputed from the downloaded files, all six numbers match.

### 5.9 Crack-label shape, old vs `20221008` (§6)
Same 265 cells, crack labels on both versions:

| | Old `20211104` | `20221008` (= E-SCDD) |
|---|---|---|
| Crack pixels | 327,754 | 396,572 (+21%) |
| Width, px (pooled) | 2.17 | 2.52 |
| Width, px (median per cell) | 1.79 | 2.46 |
| Fragments | 5,391 | 1,288 (4.2× fewer) |

This is the "joined and widened" cleaning, measured directly.

### 5.10 Smaller facts
- **Classes and formats.**
  - 30 classes (0–29). Ids 0–23 match our scheme; one name change, 18 "corrosion" → "corrosion rbn".
  - Masks are 8-bit single-channel 512 × 512. Images are RGBA 512 × 512.
- **Colour.** 194 CSIR images carry some colour (spread up to 110 grey levels), 113 of them among our 582. Our loader converts to grey anyway.
- **Mirror extras.** The mirror's no-padding variants crop the padding and rescale the cell to 512 px. This changes crack width, so it is not comparable with our data.

## 6. Corrections this makes to the rest of the handbook
- **"E-SCDD revised masks"** throughout the docs means BenchmarkEL `20221008` crack/inactive labels obtained via E-SCDD, plus our P6 build (§5.3). The name `masks_escdd` stays; it is a path in the code.
- **Doc 03 §3.1:**
  - "903 images, 29 classes" → 903 files (693 + 117 + 93 synthetic), 30 classes.
  - "Refined" annotations = spacing relabel only.
  - The 583rd entry is `README.txt`.
- **Doc 03 §3.2:** the P3 vs F04 "conflict" is resolved (§5.8).
- **Doc 08 (P3 caveat) and doc 13 (A-label issue): "E-SCDD's annotation provenance is not documented"** becomes: the crack/inactive labels are BenchmarkEL's own `20221008` corrections. *How* those corrections were made is still not documented.
- **Doc 13 E10:** the download is done. Whether to use the extra labelled cells or enlarge the test set is now a user decision (doc 15).

## 7. What it could mean (Reading; interpretation, not results)
- **Thesis wording.** Credit the revised crack labels to BenchmarkEL `20221008` (Pratt et al.), obtained via E-SCDD (Hanifi et al. 2025). The P3/P14 conclusion ("the label version is a bigger lever than any SSL effect") is unchanged.
- **More labelled data exists:** 233 real cells we never trained on with labels, a 49% increase over 478 train. Constraints:
  - 111 of them were used as unlabelled data in the x-arms;
  - 105 are E1's evaluation set;
  - most are CSIR cells from modules we never saw;
  - the newest annotations are noisier for crack.
  - **Using them would start a new base recipe,** not extend the existing P-series results. Mixing would break the "one change per arm" and "same data across arms" rules.
- **A larger test set would help crack more than inactive** (§5.7). Inactive stays decided by a handful of cells.
- **The synthetic images are not a useful resource for this project as released:** 93 images from 4 cells. Mask-conditioned diffusion as an *idea* for generating rare inactive examples is open, but the paper gives no segmentation evidence.
- **Annotation workflow idea for WattCycle:** a SAM-type model fine-tuned on EL masks as a labelling assistant, with tiered review. The speckled crack masks in the new cells show its crack output needs cleaning before use.

**Decisions waiting on the user** (also in doc 15):
1. Use the extra labelled cells or not, and if so for what (a new base, a held-out selection set, a larger test).
2. Enlarge the test set (options A/B above) or keep the 50 cells.
3. How to word the label attribution in the thesis and deck.

## 8. Terms

| Term | Meaning |
|---|---|
| **SCDD** | The E-SCDD paper's name for BenchmarkEL (its `20221008` release, 695 cells, 29 classes) |
| **E-SCDD** | "Extended SCDD": `20221008` + class 29 + 117 new real cells + 93 synthetic (as released) |
| **`_rf` suffix** | Marks E-SCDD's newly annotated real cells (e.g. `CSIR_00067_r4_c3_rf`); also ends every synthetic file name |
| **Synthetic file name** | `<k>-<base stem>_<conditioning class>_rf.png`; k = sample index 1–10 |
| **PV-DDPM** | The paper's mask-conditioned diffusion model |
| **Conditioning mask** | The layout image the diffusion model must respect. "bckgnd" = all non-background structure (multi-defect output); "<class>" = features plus that one defect |
| **Spacing classes** | Gaps between cells: sp multi (1), sp mono (2), sp dogbone (3), sp mono halfcut (24), sp multi halfcut (29). Their shapes reveal the cell type |
| **IBC dogbone** | Back-contact cells joined by dog-bone-shaped interconnects; no front ribbons |
| **Module leakage** | Cells from the same physical module in both train and test; the model may learn module-specific appearance |

## 9. Likely questions

**"So were we wrong to call them E-SCDD masks?"**
Not wrong about where we got them: we downloaded them from E-SCDD. But the crack and inactive cleaning was done by BenchmarkEL's maintainers in `20221008`. E-SCDD changed only cell-gap classes in 66 masks. Reading: for a thesis, cite both (§2, §5.2).

**"Can we just use E-SCDD's train/test split instead of ours?"**
Not without retraining everything:
- 48 of E-SCDD's test cells are in our train;
- its test has only 9 inactive cells (§5.6, §5.7).

**"Are the synthetic images a free win for rare classes?"**
No evidence for that here:
- there are only 93, from 4 cells;
- the paper never tests segmentation;
- its one downstream comparison is uncontrolled (§3, §5.4).

**"Did any synthetic image leak into our training?"**
No.
- Our `masks_escdd` was built by exact name match on our 582 stems, which never match the synthetic names.
- 560 of our 577 E-SCDD-sourced masks are pixel-identical to E-SCDD's; the other 17 differ only by the P6 remap (§5.3).

**"Did any new `_rf` cell leak into our test?"**
No: none of the 117 is among our 582. But 100 of them are in our unlabelled external pool, so the x-arms saw their images, without labels, during training.

**"What does this do to P3 and P14?"**
Nothing to their numbers. It clarifies that the label effect is the BenchmarkEL `20221008` correction (§6, §7).

## Related docs
- `03_datasets_and_splits.md`: datasets, mask versions, splits (updated with this audit)
- `08_experiments_P1_P7_diagnostics.md`: P3 (label-version re-score)
- `10_experiments_P13_P16_E1.md`: P14 (training on old vs revised labels), E1 (the 106-cell extension)
- `05_literature_and_baselines.md` §7: the E-SCDD paper among the literature
- `13_problems_pitfalls_open_issues.md`: label noise (A-series), E10
- `15_status_remaining_work.md`: decisions waiting on the user
