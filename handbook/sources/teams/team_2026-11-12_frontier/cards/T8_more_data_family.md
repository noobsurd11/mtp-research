# T8 More supervision: public EL datasets, multi-dataset and weak-label training, synthetic data (family cards, 13 Nov 2026)

Analyst T8. Tags: R = from the paper or the dataset page, E = measured in our files (path given), S = my judgement. Spec: `T8_more_data_spec.md`. Ledger: `ledger/T8.tsv` (all 64 papers). Pre-check scripts and outputs: `cards/T8_precheck/` (run with `~/mtp/research/.venv/bin/python -I`; P532 cells only, no test or E1 file opened).

Read in full (method and results): P037 (marginal / exclusion loss), P011 (MultiTalent), P077 (NLL+ over a universal taxonomy), P042 (PV-DDPM / E-SCDD), P079 (mixed supervision). Read in part or by page: P021 (abstract page and pvcracks repo), P136 (MSPS repo page), P363 (PVEL-AD repo page), ELPV repo page, PV-Vision and MultiSolSegment OSTI pages, P054, P119, P199 (abstracts). All others: scout record plus abstract.

---

## 0. Four measurements made for this family (E, all new)

| # | Check | Result | File |
|---|---|---|---|
| E1 | Cell size in our 512 px images (largest connected cell-area component, 478 train masks v1.1) | median bounding box 253 x 250 px in ARTS, CFVS, CSIR; 251 x 249 BMRK; 249 x 248 SDLE. UCF-EL cells are about 296 x 295 px (mode). Scale UCF by 0.85 to match cell size; the visible crack FWHM then becomes 5.0 x 0.85 = 4.25 px against our about 4 px (UCF FWHM from `data_analysis/ucf_el_report.md` 4.1) | `T8_precheck/c_scale.out` |
| E2 | Darkness of inactive regions: median intensity in the region / median of class 0 in the same image | ours (48 P532 inactive cells): median 0.319, IQR 0.22 to 0.46, 90th pct 0.60 (CFVS 0.31, CSIR 0.45, BMRK 0.19, ARTS 0.64 on 2 cells). UCF-EL `Crack_Isolated` (280 sampled images, polygon eroded 2 px): median 0.561, IQR 0.46 to 0.69, 57% at or below 0.60. `Crack_Resistive`: 0.903 (4% at or below 0.60). `Crack_Closed`: 0.917 | `c_phys.out`, `c_int_ucf.out` |
| E3 | UCF-EL images per crack subtype (VIA CSV, released images only) | train 9,562: Closed 2,127 images, Isolated 1,423, Resistive 2,470; test 2,289: Closed 513, Isolated 332, Resistive 617. So about 1,000 UCF images carry an isolated region as dark as our inactive (57% of 1,755), against 42 inactive train cells here | `ucf_sub.out` |
| E4 | Physics rule "region cut off from every ribbon / busbar by a crack" on our labels (P199 / P088 idea) | on the 48 P532 inactive cells: the rule recovers 27% of inactive px at precision 0.58; per-cell IoU median 0.25, 14 cells at IoU >= 0.5. On 180 crack cells without inactive it isolates >= 0.5% of the cell in 18 cells only. Closing gaps by dilating the crack 3 px makes it worse (recall 0.18) | `c_phys.out`, `c_phys_d3.out` |
| E5 | Provenance of the 93 synthetic cells shipped in E-SCDD train | 35 from `CFVS_00114_r2_c5` (a **legacy test** cell), 38 from two **F51** cells (`CSIR_00038_r11_c3_rf`, `CSIR_00067_r4_c3_rf`), 20 from an F19 cell (`CSIR_00094_r3_c5_rf`). None is an inactive variant | `escdd_synth.out` |

Readings (S):
- E1 makes UCF-EL usable with one fixed geometric transform; crack widths then agree within about 10%.
- E2 shows that UCF `Crack_Isolated` is a lighter version of our inactive and `Crack_Resistive` is not inactive at all. A region-wise darkness threshold (keep isolated regions at ratio <= 0.60, our 90th percentile) aligns the two conventions with data, not by name.
- E4 kills the plain physics renderer (too few donor cells, and the rule explains only a quarter of the labelled inactive area). It does not kill inactive synthesis from real inactive shapes (spec arm 2).
- E5: the E-SCDD synthetic cells must never be trained on (they leak the legacy test set and F51). The released PV-DDPM weights were "initially trained on the complete dataset" (R, P042 section IV.A.3), which contains our legacy test and E1 cells, so they are also unusable, even as initialisation.

---

## 1. Dataset census for this family (what is verified)

| Dataset | Where | Licence | Labels | Crack convention | Overlap with BenchmarkEL / sealed sets | Status of the facts |
|---|---|---|---|---|---|---|
| UCF-EL (Fioresi 2022) | GitHub `ucf-photovoltaics/UCF-EL-Defect`; local copy `~/mtp/datasets/UCF-EL-Defect` at 3ebfc6bb (E) | no licence file (E) | VIA polygons / rectangles with subtypes Crack_Closed / Resistive / Isolated, Contact x2, Interconnect x3, Corrosion, Unknown (E); released masks merge them into 4 classes + ignore 128 | region class; Closed polygons 3.5 to 5 px wide, +0.5 px margin per side (spread -1.75 to +4.75), 51% of points within 1 px of the dark ridge (ours 48%) (E `ucf_el_report.md` 4.1) | different lab (S); a duplicate search against our 816 stems has not been run (spec C0) | E for counts and geometry; licence ambiguous |
| ELPV (Deitsch, Buerhop) | GitHub `zae-bayern/elpv-dataset` (E, page) | CC BY-NC-SA 4.0 (E, page) | image-level defect probability and mono / poly type, 2,624 cells, 300 x 300, 8-bit (E, page) | none | **contains our BMRK cells** (4 of 4 checked at NCC 1.000, E `F04` 1b; BMRK = ELPV cell rotated 90 deg, 300 -> 256 px, padded to 512). 44 modules but no module ids (E, page), so module-level overlap with the 10 BMRK test and 5 BMRK E1 cells cannot be checked | not downloaded |
| MultiSolSegment (Sanghi 2026) | DuraMAT, DOI 10.21948/2587738 (E, OSTI page); code `sandialabs/pvcracks`, BSD-3 (E, page); weights DOI 10.21948/2997859 (E, page) | dataset licence not stated on the OSTI page (E); the arXiv page shows CC BY-NC-ND 4.0, probably for the paper (unverified for the data) | multi-label: crack, busbar, dark, non-cell (R); 585 images: CWRU 373, ASU 92, LBNL 120 (R, scout and `A07`) | unknown, not measured | **CWRU is our SDLE source** (E `F04` 2): hash / NCC check against the 18 SDLE cells needed; LBNL may overlap PV-Vision | not downloaded; image count not on the OSTI page |
| PV-Vision crack benchmark (Chen, LBNL) | OSTI DOI 10.21948/1871275 (E, page) | not stated (E, page: "Availability: Public") | crack (+ busbar, R scout) | unknown | LBNL field modules; possible overlap with MultiSolSegment LBNL 120 | count and split (1,272 / 206 / 359, scout) unverified |
| PVEL-AD (Su 2021 / 2023) | GitHub `binyisu/PVEL-AD`; hand-signed request form, institutional email (E, page) | repo Apache-2.0; data terms not given (E, page) | boxes; crack 1,260 / 2,797, star_crack 135 / 83, black_core 1,028 / 3,877 (columns as printed on the page); test labels now public (E, page) | boxes only; no inactive class | production-line NIR mono cells; overlap low (S) | **needs the user's signature: listed for the user** |
| MSPS (2026) | GitHub `wch313/MSPS-Dataset`, Zenodo 10.5281/zenodo.21549573 (E, page) | CC BY 4.0 (E, page) | **binary** defect masks (crack, busbar break, black spot merged), 1,500 cells 640 x 590, 1,000 / 500, two annotators + adjudicator (E, page) | unknown | production-line mono; overlap low (S) | paper (DACN) under review; no model numbers |
| E-SCDD synthetic cells | HF `snt-ubix/escdd` (MIT, E) | MIT | 30-class masks | Hanifi | derived from a legacy test cell and F51 cells (E5) | **excluded** |
| PVEL-S | named in STC-Net (P177) only | unknown | binary masks, 840 / 360 (R scout) | unknown | unknown | source not found (E `F04` 2) |
| OpenUVF | not in my paper list; not checked | | | | | unverified |

---

## 2. Cards for the papers that matter

### P037 Marginal loss and exclusion loss for partially supervised multi-organ segmentation (RUN_NOW, arm `ucf_partial_joint`)
- arXiv 2007.03868, doi:10.1016/j.media.2021.101979 (MedIA 2021). Full text read (sections 3, 4.1 to 4.4).
- Claims (R): one network trained on a fully labelled set F (MALBCV, 24 training CTs) and four single-organ sets. The marginal CE / Dice sums the softmax probabilities of the classes a partial dataset merged into one label; the exclusion loss penalises probability on classes known to be absent. Joint training with the marginal loss: average Dice 0.921 against 0.874 for the F-only multi-class model; on F's own test images liver 0.965 against 0.960, pancreas 0.807 against 0.802 (small), on the partial sets' images much larger (liver 0.954 against 0.850). Exclusion adds about +1.0 Dice point; total 0.931 against 0.900. Training was two-stage: F only first, then joint with 500 patches per dataset per epoch.
- Evidence check (S): the gain on the fully labelled set's own test images (our situation: we score BenchmarkEL) is 0.005 Dice for two of four organs; the large gains are on the external sets' domains. For us that means the in-distribution CV gain may be small and the unseen-module gain is where it should show. Their "background" of a partial set is a merged class, which is exactly our UCF background (all 22 classes that are not crack or inactive).
- Code: none found (scout); the loss is 15 lines.
- Hypothesis here: UCF-EL isolated regions (about 1,000 images) supervise the inactive logit directly, and UCF background supervises "not crack and not inactive" without forcing any structural class.

### P077 Multi-domain semantic segmentation with overlapping labels (RUN_NOW, arm `ucf_partial_joint`)
- arXiv 2108.11224, WACV 2022. Sections 3.6, 4.1, 4.2 read.
- Claims (R): one softmax over a universal taxonomy; a dataset class is a set of universal classes; loss NLL+ = -log sum over the set. Gradients show NLL+ "favours peaky subdistributions": the model picks one class inside the set when other data supports it. Joint WD2 + Vistas: 56.2 / 44.4 mIoU against 55.3 / 43.1 naive concatenation; cross-dataset Cityscapes 71.4 against 69.0.
- Evidence check (S): within-dataset gains are 0.3 to 1.3 points; the paper's case for the method is cross-domain, again our E1 / F51 situation.
- Code: none verified. The arm uses NLL+ with a single "allowed set" code; it equals P037's marginal CE.

### P011 MultiTalent (RUN_NOW for its sampling and loss rules; its sigmoid-head design is the fallback variant 1b)
- arXiv 2303.14444, MICCAI 2023. Sections 2.2, 2.3, 3 read. Code: `MIC-DKFZ/MultiTalent` (scout; not opened).
- Claims (R): shared backbone, one sigmoid head per class, BCE + batch Dice computed only on classes a dataset annotates, losses summed over classes, case sampling probability proportional to 1 / sqrt(n). 13 CT datasets: +1.26 Dice (Resenc U-Net) and +1.05 (U-Net) averaged over datasets against per-dataset training; larger on "difficult" and cancer classes. As pretraining it beat self-supervised baselines (BTCV 84.41 against 84.01 for U-Net).
- Evidence check (S): gains are modest on average and concentrated on hard classes; inactive is our hard data-limited class.
- Use here: batch Dice only on the dataset that labels the class (our Dice on crack / inactive stays on BenchmarkEL samples only); summed losses; external sampling fixed per batch. Variant 1b (separate sigmoid heads, conventions never mixed) is specified as a fallback only (spec arm 1, "variant 1b").

### P223 Combining partially labelled binary datasets: other-class positives as negatives (RUN_NOW, folded into arm 1)
- arXiv 2402.19340, IJCARS 2024; abstract only. Claims (R): +4.4% Dice over a per-class ensemble. Used here as the rule that UCF contact, corrosion and interconnect pixels count as "not crack, not inactive" (the NEG code), and that UCF background never supervises classes UCF does not label.

### P021 MultiSolSegment (RUN_AFTER_GATE: second external dataset for arm 1)
- doi:10.1016/j.solener.2026.114469, arXiv 2603.13337. Page and repo read.
- Claims (R): multi-channel sigmoid U-Net (crack, busbar, dark, non-cell), 98% pixel accuracy, mean per-class IoU 0.384 (from `A07`).
- Code / data (E, pages): `sandialabs/pvcracks` BSD-3; data DOI 10.21948/2587738 with no licence on the OSTI page; weights DOI 10.21948/2997859.
- Hypothesis: the "dark" class is a third inactive-like source (1.03% of px, R). Gate: arm 1 screen read; download; licence confirmed; CWRU against SDLE duplicate check; darkness ratio of "dark" regions measured as in E2.

### P042 PV-DDPM / E-SCDD (RUN_AFTER_GATE, arm `pvddpm_fold_synth`)
- arXiv 2511.09604. Abstract, sections III, IV.A, V.A read. Code `sntubix/pv-ddpm` (E, page: no licence shown, weights on Google Drive via gdown, `train.py --dataset_path --resume_weight`; framework and resolution not stated).
- Claims (R): DDPM with the binary conditioning mask concatenated to the noisy image; cosine schedule, Adam 5e-4, batch 8, EMA, L2 loss; trained on all cell types then fine-tuned per type; FID 4.10, KID 0.0023 (custom feature extractor fine-tuned on E-SCDD); AA-CLIP pixel AP +8.34 when trained on E-SCDD against SCDD. No segmentation experiment with the synthetic images.
- Evidence check (E5, R): the shipped synthetic cells and the released weights both saw our sealed cells. Never evaluated as segmentation training data. Expert-picked "20 most realistic samples" per category: the quality numbers describe a filtered subset.
- Hypothesis: a generator trained per fold on the 425 fold-train cells can render new inactive layouts on real cell structures; gated behind a cost pathfinder and a crack / inactive visibility check.

### P079 Mixed supervision for surface-defect detection (RUN_AFTER_GATE, arm `elpv_bmrk_negatives`)
- arXiv 2104.06064, Computers in Industry 2021 (420 citations). Sections 3.1, 3.2, 5.3 read.
- Claims (R): segmentation + classification network; "For non-anomalous (negative) training samples, the segmentation output should always be zero for all pixels, therefore, segmentation learning can still be performed"; positives without masks train only the classifier. KolektorSDD2: AP 73.3 with no pixel labels, 83.2 with 16 segmented samples, 95.4 with all.
- Use here: ELPV cells with defect probability 0 become fully labelled negatives for crack and inactive (NEG code over the cell), in exact BMRK geometry. Positives (MIL) are a later variant (P312).

### P233 Long-tail challenges in EL defect detection (RUN_AFTER_GATE, arm `inactive_grid_paste`)
- doi:10.4229/eupvsec2026/3do.16.5; scout record only. Claims (R): 2,894 images, 14 classes, YOLOv11; rare classes fail by being predicted as background; only cell-grid-aware copy-paste lifted tail AP (ring_defect 0.145 to 0.288).
- Use here: paste real inactive regions with their bounding crack onto other labelled train cells at the same relative cell position and source, never onto unlabelled pool cells (the opposite of the CP100 run that failed).

### P095 FreeMask (RUN_AFTER_GATE, inside arm 4)
- NeurIPS 2023, code `LiheYoung/FreeMask` (scout). Claims (R, scout's web summary, not re-read): filtering synthetic pixels by a real-trained model's per-class loss, ADE20K 48.7 to 52.0 mIoU. Used as the noise filter for generated pairs.

### P199 Spatially resolved electrical modelling of cracks (PARKED, E4)
- doi:10.1002/pip.3348 (Prog. PV 2020), abstract read. Claims (R): quasi-SPICE model of active and inactive microcracks from EL damage maps; 0.12% power-loss error on one complexly damaged cell.
- E4: the isolation rule explains 27% of labelled inactive px; it fires on 18 of 180 crack-only cells. A renderer driven by it has under 20 donor cells. Reopen with a finger-direction-aware rule (current along fingers to the nearest busbar) if arm 2 passes.

### P088 PV-Vision (BENCH_ONLY)
- doi:10.1109/jphotov.2023.3249970; data DOI 10.21948/1871275 (E, page). Claims (R scout): UNet-VGG16 crack F1 0.875, IoU 0.782 on its own 359-cell test; "crack-isolated area" as worst-case inactive area.
- Use: an external, zero-shot crack test set for a cross-dataset row of the benchmark (tolerant metrics only, conventions differ), and the isolated-area definition for the T5 post-evaluation track (E4 shows it is not the same as labelled inactive: report it as derived).

### P136 MSPS (BENCH_ONLY)
- Zenodo 10.5281/zenodo.21549573, CC BY 4.0, 1,500 binary-mask cells, double annotation with adjudication (E, page). As training data its binary label merges crack with black spots and busbar breaks (S: weak for inactive). As a benchmark item it is the cleanest-licensed external test set; its double annotation could give an inter-annotator ceiling on a second dataset if the two raw annotations are released (not stated).

### P363 PVEL-AD (PARKED: access and prior)
- Needs a hand-signed form from an institutional address (E, page). Crack boxes only; no inactive. Box supervision (P290 BoxInst projection loss) would act on crack, which is noise-limited here. Reopen after arm 1 if crack transfer to F51 moves. **Listed for the user** as a gated download.

### P493 PV-S3, P189 Torpey, P170 Hanifi VGG16-UNet, P262 instance benchmark (BENCH_ONLY)
- Published EL methods that the benchmark suite re-runs under its protocol (PROTOCOL 7). Not data routes.

### P599 EL nomenclature, P625 CNN / transformer classification benchmark (PROTOCOL)
- P599: crack-mode categories for the post-evaluation track. P625: module-grouped CV recommendation, already adopted (cv5v2).

### Generative papers not taken (PARKED, reasons in the ledger)
P147 GenSeg, P155 UnAICorN, P161 CycleGAN-Turbo, P219, P224 ContourDiff, P228 StyleSPADE, P278 SeaS, P283 SatSynth, P286, P294, P297, P300, P303, P317, P334, P380, P391, P393, P397, P398, P412, P454, P513, P514, P518, P556. Common reasons (S): latent models downsample 8x (a 64 x 64 latent cannot carry 1 to 2 px cracks), most have no verified code, each needs a generator trained per CV fold (5 generators per screen) to avoid seeing held-out cells, and none was evaluated on EL segmentation. The one generative route kept (arm 4) is the only EL-native generator with code.
