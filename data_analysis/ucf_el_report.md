# UCF-EL (Fioresi et al.): first-hand data analysis

Date: 2026-10-08. Local analysis of the public repo `ucf-photovoltaics/UCF-EL-Defect` at `3ebfc6bb` ("use test set for val"),
copied from gaint. It covers the segmentation release (`training/data/{train,test}`, 9,562 / 2,289 image–mask pairs), the VIA export
`AnnotationsCombined.csv`, the annotation guide (`annotation_guide.pdf`), `Test_Images/` (17,064 cells) and our split lists (cv02).
Scripts: `data_analysis/scripts/ucf_*.py` (run `python -I <script> <data> ...`). Raw outputs: `data_analysis/out/ucf_*.json`.
Figures: `data_analysis/figs/ucf_*.png`. Convention: **measured** = computed here; **interpretation** = marked as such.
Companion report: `benchmark_el_report.md`.

## 0. Verdict on the handoff's UCF facts

| Handoff claim | Here | Status |
|---|---|---|
| 9,562 train / 2,289 test; classes bg, crack, contact, interconnect, corrosion; ignore 128 | same; mask values exactly {0, 1, 2, 3, 4, 128} | confirmed |
| sl20 = 1,912, sl5 = 478, sl1 = 96, nested; 1% has no corrosion | same; sl1 has 0 corrosion images and 2 interconnect images | confirmed |
| Crack GT width median 9 px train / 7 px test at shorter side 295 | per-component median of the skeleton width (2·EDT−1): **9.2 px in both splits** (IQR 4.7–23). Not 7 for test with this method | partly confirmed (the method differs) |
| Jha's lists put 1,769 test images into training lists | not re-checked here (lists not local) | – |
| The official code validates on the test set | `training/train.py` builds `dataset_val` from `set="test"`; the repo's last commit is "use test set for val" | **confirmed** |

## 1. Provenance: how the released masks were made (measured, `out/ucf_provenance.json`)

- **Origin of the release.** All 11,851 released images are in the VIA CSV (16,941 files) and in `Test_Images` (17,064), byte-identical (md5, 298/298 sampled).
  - The release is exactly the cells with at least one annotated region.
  - The 5,090 CSV cells left out have no regions (5 have a few), i.e. they were annotated as defect-free.
  - `Test_Images` holds 123 further cells that are not in the CSV.
- **Mapping of fine VIA classes to mask values** (majority value inside each region, every region of every released image):

| VIA class | regions | → mask value | share of its pixels with that value |
|---|---:|---|---:|
| Crack_Closed / Crack_Resistive / Crack_Isolated | 8,464 / 7,968 / 4,453 | **1 crack** | 0.93 / 0.98 / 0.98 |
| Contact_FrontGridInterruption / Contact_NearSolderPad | 40,511 / 20,359 | **2 contact** | 0.89 / 0.90 |
| Interconnect_HighlyResistive | 895 | **3 interconnect** | 0.88 |
| Contact_Corrosion | 145 | **4 corrosion** | 0.98 |
| Interconnect_Disconnected, Interconnect_BrightSpot, Unknown, Contact_BeltMarks | 361, 675, 127, 16 | **128 ignore** | 0.94–0.99 |

  So "interconnect" is only *HighlyResistive*. A **disconnected** cell is ignored, not labelled interconnect.
- **The released masks are the CSV shapes rasterised, with no margin added.**
  - Rebuilding every mask from the CSV with that mapping reproduces the release at **99.6% pixel agreement**, median per-image disagreement 0.27%.
  - Per-class IoU of the rebuild against the release: crack 0.978, contact 0.896 (0.938 with exclusive rectangle ends, the release's convention), interconnect 0.92, corrosion 0.98, ignore 0.994.
  - Dilating, eroding or shifting the rebuild by 1 px lowers every IoU, so there is no systematic offset or dilation.
  - Label geometry is therefore entirely the annotator's polygon or rectangle.
- **What the annotation guide prescribes** (`annotation_guide.pdf`):
  - "Only use 2D bounded regions, do not use the polyline (for cracks)".
  - "Outline each defect precisely ... include only a bit of its surrounding".
  - "When labeling cracks, include busbars".
  - Shapes in the CSV: contact 94% rectangles; crack 99% polygons; interconnect 92% rectangles.
- **Name structure** (measured):
  - 11,381 names are `M<module:4>C<cell:3><flags:3>` (358 module IDs, cells 1–62); 247 of them are `M9000`-series `.png` (600 × 600 grayscale, a different cell technology, **train only**).
  - 470 names are named stress-test sessions (`Bent Cure 0Pa`, `Bent+120C_relax 0Pa`, `Control 0Pa`, `Flat cure-oven 0Pa`, each with a raw and an `_output_` set of about 60 cells).
  - The 3-digit flag code is not a defect code. For example, `001` and `101` cells carry ignore in 99–100% of cases.
- **`defect_percentages/cell<N>.json` are model predictions** (from `ELDefectSegmentation.py`, threshold 0.52), indexed by an unordered `os.listdir` position. They cannot be mapped back to file names reliably. Not used.

## 2. Inventory (measured, `out/ucf_inventory.json`; pixel shares at shorter side 295, our training resolution)

| | train | test | sl20 | sl5 | sl1 | val957 |
|---|---:|---:|---:|---:|---:|---:|
| images | 9,562 | 2,289 | 1,912 | 478 | 96 | 957 |
| module IDs | 358 | 299 | 296 | 221 | 82 | 265 |
| background | 89.9% | 91.2% | 89.5% | 89.5% | 89.8% | 89.6% |
| **crack** | **6.51%** | 6.61% | 6.80% | 6.67% | 6.61% | 6.56% |
| contact | 1.83% | 1.90% | 1.93% | 1.88% | 1.37% | 2.03% |
| interconnect | 0.084% | 0.071% | 0.068% | 0.071% | 0.031% | 0.073% |
| corrosion | 0.057% | 0.051% | 0.041% | 0.050% | 0 | 0.094% |
| ignore 128 | 1.63% | 0.18% | 1.65% | 1.80% | 2.16% | 1.62% |
| images with crack / contact / interconnect / corrosion | 3,788 / 8,052 / 203 / 55 | 918 / 1,984 / 44 / 12 | 757 / 1,609 / 41 / 11 | 188 / 402 / 10 / 3 | 38 / 81 / **2** / **0** | 380 / 807 / 20 / 5 |

- **Image sizes vary.** Shorter side 190–600 px: 290 × 290 is the mode (6,675); the 600 × 600 png set; 190 × 190 (395 images); others.
- **Defect-free cells are almost absent.** Only 230 train images have no defect class, so false positives on clean cells are barely measured.
- **Co-occurrence (train):** 68% of crack images also have contact, and 82% of interconnect images have contact.
- **Train vs test shift:**
  - Class shares are close.
  - Ignore is 9× more common in train (1.63% vs 0.18%), mostly because the 247 M9000 png cells are train only. 145 of them are > 50% ignore (disconnected cells), none has crack.
  - `Interconnect_Disconnected` occurs in 230 train images and **no** test image.
- **Crack subtypes per split:** Closed / Resistive / Isolated region counts are train 6,847 / 6,350 / 3,614 and test 1,615 / 1,607 / 838 (same mix).

## 3. Leakage: same physical cells in train and test (measured, `out/ucf_twins_tier{A,B}.json`, figures `ucf_nn_samples_plain.png`, `ucf_twin_check.png`, `ucf_family_check.png`)

- **The official split is by cell, not by module.** 291 of 358 module IDs have cells in both train and test. Per M-series module the test share has median 19% (10–90%: 0–32%); 52 of 347 M-series modules have no test cell.
- **The same physical module appears under several module IDs**, imaged at different times or stress stages. It is the same cell index, same texture and same cracks, often with cracks that have grown between images. Examples:
  - test `M0400C009000` = train `M0378C009000`, pixel-level identical cracks;
  - test `M0334` = train `M0323` (cell 57);
  - test `M0134` = train `M0296` (cell 17);
  - train `M0131` vs test `M0133`: same cell with a new crack.
- **Detection.**
  - For every pair of module IDs sharing ≥ 5 cell indices, two measures are computed:
    - the median NCC of a structure-cancelling descriptor (128 px, DoG band-pass, row/column means removed);
    - the mean crack-mask overlap (IoU at 128 px with 2 px dilation) over shared cells with cracks.
  - Unrelated module pairs: NCC ≈ 0 (90th percentile 0.10), crack IoU 99th percentile 0.19.
  - Visual checks show that for uniform, near-defect-free cells high NCC can come from the same cell type, so the evidence is split into two tiers.

| | Tier A (confirmed): crack-mask IoU ≥ 0.4 over ≥ 3 crack cells (71 module pairs) | Tier B (possible): A or median NCC ≥ 0.6 (352 pairs) |
|---|---:|---:|
| **test images whose same physical cell is in train** | **572 / 2,289 (25.0%)** | 1,009 (44.1%) |
| test crack images with a twin in train | 404 / 918 (44%) | 496 (54%) |
| test contact images with a twin in train | 453 / 1,984 (23%) | 854 (43%) |
| test interconnect / corrosion images with a twin in train | 4 / 44; 0 / 12 | 8 / 44; 7 / 12 |
| our `val957` with a twin in the rest of train | 207 (21.6%) | 401 (41.9%) |
| our sl20 / sl5 / sl1 images with a twin in test | 182 (9.5%) / 33 / 3 | 429 / 89 / 17 |
| our `val957` with a twin in test | 77 | 206 |
| extra pool (5,213 cells outside the release) with a twin in test | 111 (2.1%) | 646 (12.4%) |

- **What the tiers cover.**
  - Tier A only finds modules where cracks match. It undercounts modules without cracks, and it misses twins where cracks grew a lot.
  - Tier B overcounts if same-type modules look alike.
  - The true leakage is between 25% and 44% of the test set.
- No transitive chaining is used: a twin needs direct pair evidence. An earlier union-find variant chained up to 43 module IDs and was discarded.
- **Named sessions:** the raw and `_output_` copies of the four sessions are **not** one-to-one copies of each other (best matches collapse onto 9–17 cells, crack-mask IoU 0). Not resolved; there is no duplicate evidence.

## 4. Geometry (measured, `out/ucf_geometry.json`, `figs/ucf_crack_subtypes.png`)

The UCF "crack" class is a **region** class. It merges three annotation types of very different geometry:

| subtype (CSV polygons, native) | median area | median width (area / skeleton length) | median width (2·EDT−1) | what it outlines (visual) |
|---|---:|---:|---:|---|
| Crack_Closed | 214 px | 5.3 px | 3.5 px | a thin polygon around a visible crack line |
| Crack_Resistive | 3,139 px | 24 px | 21 px | the whole darkened region bounded by a crack |
| Crack_Isolated | 731 px | 12 px | 11 px | an isolated, dark (inactive) cell part |

- **Crack-class components** (8-connected, test, at 295): median area 1,144 px, length-weighted width 27 px, per-component median width 9.2 px (IQR 4.7–23). Only 2% of components are < 20 px (BenchmarkEL: 76–88%).
- **UCF "crack" corresponds to BenchmarkEL crack + inactive.**
- **Contact components:** median 224 px (10–90%: 64–929). **Interconnect:** median 271 px (n = 390). **Corrosion:** median 4,065 px (n = 51).

### 4.1 Closed-crack polygons against the visible crack (measured, profiles at 91,782 train / 23,315 test skeleton points)

| | train | test |
|---|---|---|
| label extent along the normal, median (IQR) | 6.25 px (4.25–9.75) | 6.0 px (4.25–9.25) |
| visible dark-line FWHM, median (IQR) | 5.0 px (4.25–6.5) | 5.0 px (4.25–6.5) |
| margin per side = (label − visible) / 2, median (10–90%) | **+0.5 px (−1.75 to +4.75)** | +0.4 px (−1.75 to +4.0) |
| darkest point within ±1 / ±2 px of the label centre | 51% / 71% | 53% / 73% |
| dip depth (median) | 10.6% | 10.5% |

- On average, closed-crack polygons hug the visible crack, with about ½ px of margin per side.
- **The margin is inconsistent:** from 1.75 px too tight to 4–5 px too loose per side (10–90%).
- Centring is similar to BenchmarkEL: about half of the points are within 1 px of the darkest line.

### 4.2 Contact rectangles against visible darkening (measured, 45,826 train / 11,041 test rectangles)

| | train | test |
|---|---:|---:|
| rectangle area, median | 224 px | 228 px |
| share of rectangle pixels darker than 0.9 × the surrounding ring, median (IQR) | 11% (0–41%) | 8.8% (0–38%) |
| rectangles with < 10% such pixels | **48%** | **52%** |
| median intensity inside / ring, median | 0.96 | 0.96 |

- Half of the contact rectangles contain almost no visibly darker pixels by this simple measure.
- Contact labels are loose **boxes** around finger interruptions, not pixel outlines. Visually, many boxes sit around faint vertical streaks; in a bright cell about 50 boxes cover a mottled area (`figs/ucf_class_overlays.png`, row 3).
- Strict IoU on contact therefore partly measures box filling.

## 5. Metric ceiling (measured, dataset-level, test; train within ±0.02)

| perturbation of a perfect mask | crack | contact | interconnect | corrosion |
|---|---:|---:|---:|---:|
| shift 1 px (mean of 4), at 295 | **0.954** | 0.875 | 0.881 | 0.947 |
| shift 1 px diagonal, at 295 | 0.931 | 0.771 | 0.777 | 0.919 |
| dilate 1 px (3 × 3), at 295 | 0.916 | 0.783 | 0.795 | 0.902 |
| erode 1 px (cross), at 295 | 0.926 | 0.747 | 0.751 | 0.916 |
| shift 2 px (mean of 4), at 295 | 0.913 | 0.766 | 0.775 | 0.899 |
| shift 1 px, native | 0.954 | 0.895 | 0.923 | 0.949 |

Unlike BenchmarkEL (crack 1 px shift: 0.50–0.56), strict IoU on UCF crack is barely affected by 1–2 px jitter. Contact and interconnect, which are small boxes, lose 10–25%.

## 6. Annotation consistency (measured + visual)

### 6.1 Re-annotation agreement from twin cells (Tier A pairs with descriptor NCC ≥ 0.8, aligned by phase correlation; 702 pairs; `figs/ucf_twin_reannotation.png`)

| class | pooled IoU between the two masks | median tolerance F1 at 2 px (pairs with the class in either) |
|---|---:|---|
| crack | **0.57** | 0.83 (490 pairs) |
| contact | **0.25** | 0.48 (564 pairs) |
| interconnect | 0.0 | 0.0 (9 pairs) |
| corrosion | – (no pairs) | – |

- **Caveat: these are not controlled inter-annotator pairs.** The two images can differ by real defect change between stress stages, which the NCC ≥ 0.8 filter reduces but does not remove. Whether each copy was annotated independently is unknown.
- Some crack polygons are near-identical in both copies, which suggests reuse or a careful re-trace. Others differ completely, e.g. a crack drawn as a large rectangle in one image and as a polygon in the other.
- Contact boxes differ in number and position in most pairs.
- **Reading (interpretation):**
  - The label noise on UCF crack (0.57) is much smaller than on BenchmarkEL crack (0.21–0.26).
  - The label noise on UCF contact (0.25) is about as large as BenchmarkEL crack.
  - Interconnect agreement cannot be estimated (9 pairs, all disagreeing).

### 6.2 Visual audit (`figs/ucf_class_overlays.png`, 24 images, plus `figs/ucf_crack_subtypes.png`)

- **Crack:** polygons follow the visible crack or the boundary of the dark region it creates. Resistive and isolated outlines include large grey or dark areas and sometimes run straight across busbars or the cell edge ("include busbars"). Labelling style varies between images: thin traces in some, generous region outlines in others.
- **Contact:** narrow vertical boxes around dark finger streaks; several boxes with no visible streak; dense box clusters in bright, mottled cells.
- **Interconnect:** rectangles along a busbar segment, with large grey (ignore) bright-spot polygons next to them.
- **Corrosion:** dark mottled bands along busbars, outlined consistently; mostly one module family (`M0005`).
- **M9000 png cells:** a different, striped grayscale technology; mostly whole-cell ignore.
- **Unlabelled defects:** no systematic search was done. In the sample, faint finger streaks without boxes and boxes without streaks both occur, so contact has both missed and spurious labels.

## 7. Where the label gap comes from (measured counts + handoff IoUs, §6.9 of the handoff)

Share of the 4-class mean-IoU drop (relative to 100%) contributed by each class:

| labels | 4-class drop | crack | contact | interconnect | corrosion | labelled images with interconnect / corrosion |
|---|---:|---:|---:|---:|---:|---|
| 20% | 0.043 | 14% | 21% | **50%** | 14% | 41 / 11 |
| 5% | 0.122 | 12% | 15% | **34%** | **39%** | 10 / 3 |
| 1% | 0.310 | 12% | 10% | 25% | **53%** (absent → IoU 0) | 2 / 0 |

- **The UCF label gap is mostly a rare-class gap.** Interconnect and corrosion together account for 64% (20%), 73% (5%) and 78% (1%) of it.
  - These classes rest on 44 interconnect and 12 corrosion **test** images.
  - Their labels are boxes (interconnect) or come largely from a single module family (corrosion).
- **Crack and contact contribute about 0.03–0.04 of mean IoU each at 1%.**
  - Crack 0.675 → 0.529, contact 0.479 → 0.351.
  - At 1% the labelled set still holds 38 crack images (558k crack pixels at 295) and 81 contact images.

## 8. Unlabelled pool for SSL on UCF (measured + interpretation)

- **Candidates.**
  - (a) The 5,213 `Test_Images` cells outside the release: 5,194 M-series jpg, 10 named-session and 9 png cells.
  - (b) For the 1–20% protocols, train minus the labelled subset, as we use now.
- **Composition of (a).** 5,085 were annotated as **defect-free**: CSV rows with no region; 5 have a few regions; 123 are not in the CSV. The official model's predictions for them exist but cannot be matched to files. (a) is therefore an in-domain pool that is almost entirely clean cells. It adds little rare-class signal and is a test of false-positive control rather than of defect learning (interpretation).
- **Contamination.** 111 (Tier A) to 646 (Tier B) of the 5,213 are the same physical cells as test images. Removing all Tier-B twins of test leaves **≈ 4,567** cells.
- **Pool (b) inherits the split's problem.** 25–44% of test cells have a twin in train, so an unlabelled pool drawn from train contains test cells' twins too. The same holds for the labelled subsets: 9.5–22% of sl20 depending on tier.

## 9. Side by side: UCF-EL against BenchmarkEL

| | BenchmarkEL `dataset_20211104` | UCF-EL public release |
|---|---|---|
| images | 478 / 54 / 50, 512 × 512 module crops | 9,562 / 2,289 cells, 190–600 px, mostly ≈ 290 |
| classes scored | 24 (crack, inactive + 22 structural / rare) | 4 defects + background, ignore 128 |
| crack label style | 1–2 px line traces (median 1.75 px); visible line ≈ 4 px | polygons: thin outlines (closed, 3.5–5 px) **plus** dark-region outlines (resistive, isolated, 11–24 px) |
| what "crack" means | the crack line (inactive is a separate class) | crack + the area it darkens or isolates (≈ crack ∪ inactive) |
| crack pixel share | 0.19% | 6.5% |
| label centring on the visible crack | 48% of points within ±1 px | 51–53% within ±1 px |
| label margin | label thinner than the visible line by ≈ 2 px | ≈ +0.5 px per side on average, spread −1.75 to +4.75 px |
| 1 px shift IoU ceiling, crack | 0.50–0.56 (per-image median 0.12) | **0.95** |
| re-annotation agreement, crack | IoU 0.21–0.26 (n = 2 pairs) | IoU 0.57, tolerance F1 0.83 (702 twin pairs; real change not fully excluded) |
| weakest-labelled class | crack | contact (boxes; IoU 0.25 between twin copies) |
| test set design | 50 hand-picked images, all with crack | random by cell, but drawn from the same modules; validation = test in the official code |
| leakage | 1 duplicate cell across splits; 24 / 50 test from train modules | **25–44% of test cells have the same physical cell in train**; 291 / 358 modules in both splits |
| images without the main defect / without any defect | 57% of train without crack | 2.4% of train without any defect (defect-free cells excluded from the release) |
| class imbalance that matters | crack 0.19%, inactive rare; 7–12 classes empty at low labels | interconnect 0.08%, corrosion 0.06% of pixels, in 203 / 55 train images |
| observed label gap (our runs) | flat 10–100%, breaks at 2% | 0.54 → 0.23 (100 → 1%), mostly interconnect + corrosion |

## 10. What each dataset can and cannot support for a training-methodology claim (INTERPRETATION)

1. **UCF-EL can support "fewer labels hurt, and method X recovers some of it", but only with a corrected split.**
   - The label gap is real and reproducible (seed sd ≈ 0.003).
   - A quarter to almost half of the test cells have their physical twin in train. Any method that memorises cell appearance is rewarded, and the gain of a "better" method may partly be twin recall.
   - A **module-disjoint (physical-module-disjoint) re-split** is needed before claiming a methodology gain. Group module IDs by the twin evidence; Tier B as the conservative grouping.
   - Our current sl20/sl5/sl1 subsets and `val957` share physical cells with test (Tier A: 9.5% of sl20), so they should be regenerated as well.
2. **On UCF, a rare-class method would be judged mostly on interconnect and corrosion,** which rest on 44 and 12 test images, are box-labelled (interconnect) or come largely from one module family (corrosion), and appear in only 2 / 0 images at 1%.
   - Report per class with confidence intervals over images, not only the 4-class mean.
   - Do not average a class with no labelled examples into the headline as 0 (judge 1% on 3 classes, as the handoff says).
3. **UCF "crack" is not BenchmarkEL "crack".**
   - UCF crack is a region class with a high strict-IoU ceiling (0.95) and moderate label noise (0.57 between twin copies).
   - BenchmarkEL crack is a 1–2 px line class whose strict IoU is dominated by jitter.
   - Thin-structure losses and tolerance metrics matter for BenchmarkEL crack and for UCF *closed* cracks, but much less for UCF crack as a whole.
   - Cross-dataset claims about "cracks" need to say which.
4. **UCF contact is the noisiest UCF label** (twin-copy IoU 0.25; half of the boxes show no visible darkening). Strict contact IoU gains of a few points are within label noise, and a pseudo-label method will inherit box-shaped targets.
5. **BenchmarkEL supports measurement and label-noise claims** (crack metric ceiling, annotation jitter, the inactive generalisation gap). It does not support a label-efficiency claim above 10%. **UCF supports label-efficiency claims** once re-split. **Neither** measures false positives on defect-free cells well; UCF almost excludes them, though the 5,085 defect-free cells outside the release could serve as a dedicated false-positive test set.
6. **Unlabelled data on UCF is plentiful but not useful for rare classes as released.**
   - The extra 5k cells are defect-free.
   - Within-train unlabelled data contains test twins.
   - An SSL comparison on UCF must remove test twins from every pool (labelled and unlabelled) to avoid counting memorisation as label efficiency.
