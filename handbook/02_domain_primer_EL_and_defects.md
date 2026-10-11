# 02. Domain primer: EL imaging, solar cells, and the defects we segment

## What this covers
The physical side of the project, for a reader with no photovoltaics (PV) background. It covers:
- what an electroluminescence (EL) image of a solar cell is and how to read one;
- what a BenchmarkEL image looks like, and the 24 label classes;
- the two classes the project is about: **crack (class 14)** and **inactive area (class 11)**;
- why thin cracks make both labels and pixel metrics unreliable;
- the five image sources (CSIR, ARTS, CFVS, BMRK, SDLE);
- how defects link to severity and power loss, and why power loss is out of scope for now.

Dataset counts and splits are in `03_datasets_and_splits.md`. This doc only uses numbers where they explain the physics or the labels.

Claims marked **General background** are standard PV knowledge, not measured in this project and not taken from a project file. Everything else cites a file.

## Sources
- `~/mtp/research/data_analysis/benchmark_el_report.md`: first-hand analysis of BenchmarkEL `dataset_20211104` (8 Oct 2026). Raw outputs in `data_analysis/out/`, figures in `data_analysis/figs/`.
- `~/mtp/research/data_analysis/ucf_el_report.md`: the same analysis for UCF-EL.
- `~/mtp/datasets/BenchmarkELimages/README.md`: the dataset authors' README.
- `~/mtp/datasets/BenchmarkELimages/dataset_20211104/ListOfClassesAndColorCodes_20211104.csv`: the official class list.
- gaint `/home/noob/work/el-fault-detection/src/data/class_info.py`: the class registry the code uses.
- `~/mtp/research/literature/notes/F04_el_datasets_census.md`: dataset census; BMRK = ELPV finding; severity and throughput notes.
- `~/mtp/research/literature/notes/A01_pratt2023_benchmarkel.md`, `A06_pratt_thesis_and_power.md`.
- `~/mtp/research/to_human/proposal_reframe_2026-10-11.md`: the WattCycle value chain and its evidence table.
- `~/mtp/research/to_human/directions_2026-10-10.md`.
- `~/mtp/MTP_session_handoff_2026-10-07.md`: section 3 data facts.
- The phase 0 / phase 1 handoffs the user pasted on 11 Oct 2026: `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md` (a copy of the chat paste). This is not a project file; the guide should treat it as the user's own record.
- `~/mtp/research/results/p6/README.md`, section 4: inactive pixels per cell.

---

## 1. Why anyone images solar cells with EL

**The project's use case.** WattCycle wants three things from EL images, on deployable hardware (`to_human/proposal_reframe_2026-10-11.md` §1; phase 0/1 handoffs):
1. detect defects;
2. grade their severity;
3. estimate power loss.

The faculty advisor separately wants a paper and a lightweight model (about 2M parameters was mentioned; phase 0/1 handoffs).

**The value chain** (`proposal_reframe_2026-10-11.md` §1):

> EL image → defect maps → per-cell quantities (crack length and connectivity, isolated area, inactive area fraction) → severity grade (Köntges A/B/C) → power-loss band.

This project (thesis part 1, "training methodology") works on the first arrow only: **EL image → defect map**. The user split the thesis into three parts on 7 Oct 2026 (`sources/chat/user_messages_2026-10-07_to_11.md`):
1. training methodology (current);
2. architecture;
3. real-time deployment concerns (severity detection and others).

## 2. Solar cell and module anatomy (General background, with project facts where they exist)

- **Cell.** A crystalline silicon wafer, about 156 to 210 mm on a side in modern modules, that turns light into current.
- **Mono vs multi.** Cells are mono-crystalline (uniform texture, often with cut corners, a "pseudo-square" shape) or multi-crystalline (visible grain patchwork). BenchmarkEL has "a roughly equal number of images from multi-crystalline and mono-crystalline cells" (`datasets/BenchmarkELimages/README.md`).
- **Fingers.** Thin printed metal lines on the front that collect current. They run perpendicular to the busbars.
- **Busbars.** Thicker metal strips that gather current from the fingers.
- **Ribbons (interconnects).** Soldered strips that carry current from one cell to the next. In BenchmarkEL images they are the vertical dark lines (`benchmark_el_report.md` §1).
- **Module.** A grid of cells wired in series strings (for example 60, 72 or 144 cells), laminated under glass in an aluminium frame, with a junction box (jbox) on the back.
- **Half-cells.** Cells cut in two to reduce resistive loss. The external unlabelled pool contains a `multi_half_cells` group (`03_datasets_and_splits.md`).

## 3. What an EL image is (General background)

- **How it is made.**
  - The module is put in the dark.
  - A forward current is driven through it, as if it were an LED.
  - Silicon then emits weak near-infrared light (around 1,100 to 1,200 nm) wherever charge carriers recombine radiatively.
  - A silicon or InGaAs camera records that light.
- **How to read it.**
  - Brightness is roughly proportional to local voltage and carrier lifetime.
  - So bright areas are healthy, electrically connected silicon.
  - Dark areas emit little. Possible reasons:
    - no current reaches them (electrically isolated);
    - they recombine carriers non-radiatively (crystal defects, contamination);
    - they are shaded by metal (busbars, ribbons).
- **What defects look like.**
  - **Crack:** a dark line, usually because the crack locally disturbs current flow.
  - **Inactive area:** a fully dark region, because a crack has cut a piece of the cell off from the busbars.
  - **Finger interruptions:** short dark streaks along a finger, because current can no longer be collected there.
- **Scale.** A real crack is far narrower than a pixel. The project's proposal cites a crack width of about 3.4 µm against about 300 µm per pixel, marked as a literature value (`proposal_reframe_2026-10-11.md` §1). What the camera sees is the dark halo of disturbed current around the crack, a few pixels wide, not the crack itself. Annotated crack width is therefore a **labelling convention**, not a physical measurement.

## 4. What a BenchmarkEL image looks like (measured)

All facts in this section are from `data_analysis/benchmark_el_report.md` §1 unless stated otherwise.

- **Size and content.** Every image is 512 × 512 pixels and is a **module crop**: one central cell plus fragments of its neighbours. Cracks are labelled in the neighbour fragments too.
- **Padding.**
  - BMRK and SDLE cells are downscaled to roughly a quarter of the frame and surrounded by padding (class 7).
  - That is why padding is 17.3% of all train pixels (`MTP_session_handoff_2026-10-07.md` §3.1).
- **BMRK cells are ELPV cells** (`literature/notes/F04_el_datasets_census.md` §1b; 4 of 4 checked, normalised cross-correlation 1.000).
  - ELPV is the public ZAE Bayern cell dataset.
  - Each BMRK image is the ELPV cell with the same number, rotated 90° and downscaled from 300 to 256 px inside a 512 × 512 padded canvas.
- **Stem names** encode source, module and position:
  - `CFVS_00031_r4_c4` = source CFVS, module 00031, row 4, column 4 of the module;
  - BMRK stems look like `BMRK_00073_cell0253`.
- **Figures to show the user:**
  - `data_analysis/figs/peek_sources.png`: one sample per source;
  - `data_analysis/figs/crack_overlays_1.png` to `_4.png`: labels drawn over images, 24 images across splits and sources;
  - `data_analysis/figs/inspect_closeups.png`.

## 5. The 24 classes

The official list is `dataset_20211104/ListOfClassesAndColorCodes_20211104.csv`. The code registry (`src/data/class_info.py` on gaint) copies it.
- **12 "features":** intrinsic parts of a module.
- **12 "defects":** extrinsic faults.
- Masks are single-channel index PNGs: pixel value = class id 0 to 23.

| id | Name | Kind | What it is |
|---|---|---|---|
| 0 | background (bckgnd) | feature | healthy cell area |
| 1 | sp multi | feature | dark spacing between multi-crystalline cells (`benchmark_el_report.md` §1) |
| 2 | sp mono | feature | dark spacing between mono cells |
| 3 | sp dogbone | feature | spacing with the "dogbone" shape left by mono cells' cut corners (shape name; not described in project files) |
| 4 | ribbons | feature | vertical interconnect ribbons |
| 5 | border | feature | cell or module border; not described further in project files |
| 6 | text | feature | printed text or labels visible in the image |
| 7 | padding | feature | out-of-module area; added around downscaled BMRK/SDLE cells; also the fill value for rotation borders in augmentation (`class_info.py`) |
| 8 | clamp | feature | clamp (General background: a holding or contacting clamp visible in the image) |
| 9 | busbars | feature | busbars |
| 10 | crack rbn edge | defect | crack along a ribbon edge. 5 train components, 104 px in all; "not learnable as a class from this data" (`benchmark_el_report.md` §2) |
| **11** | **inactive** | **defect** | **electrically isolated, dark cell region** (section 7) |
| 12 | rings | defect | rings (General background: concentric ring patterns from wafer growth) |
| 13 | material | defect | material (General background: intrinsic wafer material defects such as dislocation clusters) |
| **14** | **crack** | **defect** | **crack line** (section 6) |
| 15 | gridline | defect | short horizontal finger interruptions (`benchmark_el_report.md` §1) |
| 16 | splice | defect | splice (not described in project files) |
| 17 | dead cell | defect | dead cell (General background: a cell that is entirely dark) |
| 18 | corrosion | defect | corrosion (not described in project files) |
| 19 | belt mark | defect | belt mark (General background: marks left by conveyor belts in manufacturing) |
| 20 | edge dark | defect | edge dark (General background: a darkened cell edge) |
| 21 | frame edge | feature | module frame edge |
| 22 | jbox | feature | junction box |
| 23 | meas artifact | defect | measurement artifact (not described further in project files) |

Where the "What it is" column only repeats the class name, the project files give no further description. The guide should say so rather than invent one.

**How rare the classes are** (train, `MTP_session_handoff_2026-10-07.md` §3.1, confirmed by `benchmark_el_report.md` §0):

| Class | Share of train pixels |
|---|---|
| background | 69.2% |
| padding | 17.3% |
| background + padding together | 86.5% |
| **crack** | **0.186%** |

- Four classes have under 1,300 pixels in all 478 train images: clamp, crack rbn edge (104 px), rings and meas artifact.
- 7 classes are absent from val and 8 from test.
- So "mIoU over 24 classes" is really over 16 or 17 classes, and not the same set on val and test.

**The project's focus.** It reports only crack and inactive as primary classes.
- Phase 0 already made "defect mIoU" (mean IoU of crack and inactive) the headline and excluded gridline as noisy (phase 0 handoff).
- The P-series (P6 onward) reports three primaries: crack IoU, inactive IoU and crack relaxed F1@2. See `07_methodology_rules_and_statistics.md`.

## 6. Crack (class 14): thin, jittered, and source-dependent

### 6.1 What the labels look like (measured on the old masks, `benchmark_el_report.md` §0 and §2)

| Property | Value |
|---|---|
| Train images with crack | 205 of 478 (42.9%) |
| Val images with crack | 22 of 54 (40.7%) |
| Test images with crack | 50 of 50 (48 of 50 on the revised masks; `results/p6/README.md` §4) |
| Label width (per point, 9,302 skeleton points) | median **1.75 px** (IQR 1.25–2.5) |
| Visible dark line width (FWHM) | median **4.0 px** (IQR 3.0–4.75) |
| Points where the visible line is at least 1 px wider than its label | 77% |
| Crack components under 20 px | 76% train, 59% val, 88% test |
| Orientation, train | 62% diagonal, 34% vertical (parallel to ribbons), 4% horizontal |

- **The label is narrower than what you see.** The annotators traced a 1 to 2 px line down the middle of a dark line about 4 px wide.
- **Label width depends on the source.** It is a convention, not only the crack:

| Source | Visible FWHM median | Label width median |
|---|---|---|
| ARTS | 3.0 | 1.5 |
| BMRK | 5.0 | 3.0 |
| CFVS | 4.25 | 1.75 |
| CSIR | 3.5 | 1.75 |
| SDLE | 4.5 | 3.25 |

Source: `benchmark_el_report.md` §2.

- **Conflict to know about.**
  - `MTP_session_handoff_2026-10-07.md` §3.4 said "BenchmarkEL cracks are 2 to 3 px wide". The data report marks this **partly wrong**: most labels are 1–2 px (`benchmark_el_report.md` §0).
  - `proposal_reframe_2026-10-11.md` §1 says "median width of 2 px".
  - The length-weighted area/skeleton width is 2.17 (train), 1.93 (val) and 2.66 (test) (`benchmark_el_report.md` §2).
  - The numbers differ by method; all say "about 2 px or less".

### 6.2 Where labels sit (measured, `benchmark_el_report.md` §4.2)
At 61,176 skeleton points, the darkest pixel along the normal lies:

| Within | Of label points | Random background points (null) |
|---|---|---|
| ±0.5 px | 27% | 5.5% |
| ±1 px | 48% | 11% |
| ±2 px | 64% | 21% |
| > 2 px | 36% | 79% |

- Labels are clearly on the cracks, far above chance.
- But **half of label points are more than 1 px from the darkest line**.
- ARTS is the best source (75% within 1 px); BMRK is the worst (38%).

### 6.3 Other label problems (measured or visual, `benchmark_el_report.md` §4.3–4.6)
- **Low contrast.** 7.2% of crack components are less than 2% darker than their surroundings (essentially invisible), and 4.9% are brighter. CSIR is worst: 16% of its components are under 2% darker.
- **Dotted labels.** In 14 train, 3 val and 5 test images, ≥ 30% of crack pixels sit in components ≤ 10 px: a continuous visible crack labelled as a dashed trace. A model that predicts the continuous crack is scored as wrong on every gap.
- **Missed cracks.** Visible cracks are sometimes left unlabelled. Example: `train/CSIR_00094_r16_c5` has two parallel cracks, only one labelled. No reliable missed-crack rate could be measured.
- **Two annotations of the same image disagree a lot.**
  - The dataset contains two duplicate pairs with independent masks; their crack IoU is **0.257** and **0.210**.
  - At 2 px tolerance they agree much better: tolerance-F1 0.82 and 0.99.
  - Caveat: n = 2 pairs (`benchmark_el_report.md` §4.1; figure `data_analysis/figs/duplicate_pairs_masks.png`).

### 6.4 Why this breaks strict pixel IoU (the central fact of the project)

**IoU (intersection over union).** Overlap between predicted and labelled pixels divided by their union. A full definition is in `04_glossary_and_naming.md`.

Take a *perfect* crack mask, shift it by one pixel, and score it against the original (`benchmark_el_report.md` §3):

| Perturbation of a perfect mask | Crack IoU, test | Inactive IoU, test |
|---|---|---|
| shift 1 px (mean of 4 directions) | **0.559** | 0.943 |
| shift 1 px diagonal | 0.434 | 0.909 |
| dilate 1 px | 0.461 | 0.897 |
| erode 1 px | 0.296 | 0.902 |
| shift 2 px | 0.336 | 0.891 |

- **A 1 px wide line shifted by 1 px loses about half its IoU.** The per-image median under a 1 px shift is 0.12 (Pratt's per-image-median convention).
- So for a model with test crack IoU around 0.3 to 0.47 (the project's range; see `11_results_synthesis_and_claims.md`), much of the remaining "error" can be label jitter rather than model failure.
- **What the project did about it:**
  - used **tolerance metrics**: relaxed precision, recall and F1 within 2 px, written relP@2 and relF1@2;
  - adopted the **revised (E-SCDD) masks**, which join dotted labels and widen them (`03_datasets_and_splits.md` §3);
  - tested **offset-tolerant losses**: tolerant pseudo-labels in P7 onward, and a tolerant supervised loss in P14.
- Old vs revised masks agree at 0.73–0.81 crack IoU but 0.98 within 2 px (`results/p3_label_versions/README.md`; `to_human/proposal_reframe_2026-10-11.md` §1).

**Reading** (from `benchmark_el_report.md` §7, marked interpretation there): differences of ±0.03 in strict crack IoU between methods are hard to interpret without a tolerance-aware metric.

## 7. Inactive area (class 11): blobby, consistent, but in very few cells

**Physical meaning** (General background, consistent with the sources).
- A crack can cut part of a cell off from the busbars. Current then cannot flow in or out of that part.
- In EL it shows as a dark region with sharp, crack-shaped borders.
- An inactive part produces no power, so it is the defect most directly tied to power loss (section 9).

**Measured** (`benchmark_el_report.md` §1 and §0).
- **Inactive never occurs in an image without a crack label**, in any split.
- **99% of inactive components touch a crack label within 3 px** (train 440/445, val 18/18, test 51/52). Inactive regions are bounded by cracks.
- **Cracks are often labelled inside inactive regions too.** 20% of train crack pixels (16% test) lie in or at inactive regions.
- **Test inactive regions are darker relative to their surroundings than train ones:** median inside/ring ratio 0.34 vs 0.55. 6% of train inactive area is barely darker than its surroundings; none in val/test.
- **Label quality is good, the opposite of crack:**
  - 1 px shift IoU is 0.943 (section 6.4);
  - the duplicate-pair inactive IoU is 0.64, with tolerance-F1 0.92 at 2 px.
- **The problem is scarcity.**
  - Inactive is in 43 of 478 train images, 5 of 54 val and 17 of 50 test (old masks; `benchmark_el_report.md` §0).
  - With the revised masks: 16 of 50 test cells and 6 of 54 val cells.
  - The top 3 cells hold 59% (test) and 89% (val) of all inactive pixels.
  - One test cell, `BMRK_00073_cell0253`, alone holds 23% (`results/p6/README.md` §4).
  - So any dataset-level inactive number is decided by about three cells. This drives many caveats later in the handbook.

**Reading** (`benchmark_el_report.md` §7.4): crack and inactive have opposite problems. Crack is noise-limited (thin, jittered labels). Inactive is data-limited (few examples). A method that treats them the same way will struggle on one of them.

## 8. The five image sources of BenchmarkEL

From `datasets/BenchmarkELimages/README.md`:
- three private sources:
  - CSIR Energy Centre (a PV module test lab in South Africa, where the dataset was built);
  - CFV Labs (a US test lab);
  - ARTsolar (a South African manufacturer);
- two public sources:
  - images selected from CWRU SDLE;
  - images selected from ZAE Bayern.

Per-split counts below were counted from the dataset folders for this handbook (`~/mtp/datasets/BenchmarkELimages/dataset_20211104/images_{train_original,val,test}`). The train counts match `benchmark_el_report.md` §0.

| Stem prefix | Origin | Train | Val | Test | Notes |
|---|---|---|---|---|---|
| ARTS | ARTsolar (manufacturer, South Africa) | 162 | 20 | 13 | best label placement (75% within 1 px); in the external pool (2,734 cells) |
| CFVS | CFV Labs (test lab, USA) | 146 | 23 | 18 | not in the external pool |
| CSIR | CSIR Energy Centre (South Africa) | 111 | 3 | 8 | lowest contrast (median intensity sd 24 vs 34–48); 16% of crack components nearly invisible; in the external pool (9,204 cells) |
| BMRK | ZAE Bayern via ELPV (verified identical cells, F04) | 42 | 8 | 10 | downscaled, padded; thick labels (about 3 px); worst label placement |
| SDLE | CWRU SDLE Research Center | 17 | 0 | 1 | downscaled, padded; thick labels (about 3.25 px) |

- **Source groups in later analyses.** The P-series bootstrap splits test cells into two groups (`results/p13/README.md` and others):
  - "CSIR/ARTS" (21 test cells): the sources the external unlabelled pool covers;
  - "CFVS/BMRK/SDLE" (29 test cells).
- **The `MultiSolSegment` dataset includes a CWRU subset.** The census flags it as possibly the same as BenchmarkEL's SDLE source, unverified (`F04_el_datasets_census.md` §2).

## 9. Severity and power loss (context; out of scope for now)

- **Crack modes after Köntges et al.** (`F04_el_datasets_census.md` §4; primary sources not read yet per that note):
  - **A:** no inactive area;
  - **B:** partly disconnected;
  - **C:** fully inactive.
- **Power loss tracks the inactive or disconnected area, not crack length.** Cited as literature: Chen PVSC 2022, Pratt ICTAS 2025, Hoffmann Prog. PV 2021 (`F04_el_datasets_census.md` §4); "Power loss tracks the isolated and inactive area, not crack pixels" (`proposal_reframe_2026-10-11.md` §1, marked **lit**).
- **Pratt's power-degradation study** (`literature/notes/A06_pratt_thesis_and_power.md`; abstract only, venue not confirmed):
  - 680 fielded modules, 48,960 cells, 29 classes;
  - a new "brightening" defect correlates with module fill factor, r² = 0.42.
- **No paired I-V data exists in this project.** Power loss could only rely on published correlations (phase 1 handoff).
- **Consequence the project drew** (`F04_el_datasets_census.md` §4; `proposal_reframe_2026-10-11.md`): for severity, errors in **inactive** and in crack **connectivity** (whether a crack closes off an area) matter more than pixel-exact crack IoU. This is why E1 added per-cell metrics such as inactive area error and crack length error (`10_experiments_P13_P16_E1.md`).
- **User decision, 11 Oct 2026:** power loss is "not part of this project unless we get some valid data" (`sources/chat/user_messages_2026-10-07_to_11.md`). WattCycle data available to the project: none (the user's answer "5. none" on 11 Oct 2026, `sources/chat/user_messages_2026-10-07_to_11.md`, message of 07:16 UTC; the question list it answers is in `sources/chat/claude_session_summaries_2026-10-07_to_11.md`).

## 10. UCF-EL defines "crack" differently

UCF-EL (Fioresi et al. 2022) is the second public dataset used here. Details are in `03_datasets_and_splits.md` §8. The domain point is the class definitions (`ucf_el_report.md` §1 and §4).

**Classes:** background, crack, contact, interconnect, corrosion, plus ignore (value 128).

**UCF "crack" is a region class.** It merges three annotated subtypes:

| Subtype | What is outlined | Median width |
|---|---|---|
| Crack_Closed | a thin polygon around the crack line | 3.5 px (2·EDT−1) |
| Crack_Resistive | the whole darkened region | 21 px |
| Crack_Isolated | an isolated, dark cell part | 11 px |

- So UCF crack ≈ BenchmarkEL crack + inactive.
- Its strict-IoU ceiling under a 1 px shift is 0.954, against 0.47–0.56 on BenchmarkEL (train 0.503, val 0.469, test 0.559; `benchmark_el_report.md` §3; `ucf_el_report.md` writes 0.50–0.56).
- **Contact** = finger interruptions and near-solder-pad contact faults, drawn as loose boxes. It is UCF's noisiest class: twin-copy IoU 0.25.
- **Interconnect** = only "HighlyResistive" interconnects. A *disconnected* cell is labelled ignore.

So "crack IoU" on UCF and on BenchmarkEL measure different things. Cross-dataset claims about "cracks" must say which (`ucf_el_report.md` §10.3).

## 11. Takeaways for the guide
1. EL shows electrical activity: dark means "no current or no emission here".
2. A crack label is a 1–2 px convention on a ~4 px visible line on a µm-scale physical crack. Strict pixel IoU on it has a low, noisy ceiling (about 0.5 for a perfect mask shifted 1 px).
3. Inactive is the physically important class (power loss), well labelled, but present in very few cells. Its metrics are decided by about 3 test cells.
4. Five sources with different label conventions and contrast; the unlabelled pool covers only two of them (CSIR, ARTS).
5. Severity and power loss are the end goal, but out of scope until real data exists.

## Related docs
- `00_START_HERE.md`
- `01_project_overview_and_scope.md`
- `03_datasets_and_splits.md`: counts, splits, mask versions, unlabelled pool, extension set, UCF-EL
- `04_glossary_and_naming.md`: IoU, relaxed F1@2, AP and other metric terms
- `05_literature_and_baselines.md`: Pratt, Fioresi and the other papers
- `07_methodology_rules_and_statistics.md`: primary metrics and rules
- `08_experiments_P1_P7_diagnostics.md`: P1 (fitting cracks), P3 (label versions), P5 (pseudo-label precision)
- `10_experiments_P13_P16_E1.md`: E1 per-cell metrics
- `13_problems_pitfalls_open_issues.md`
