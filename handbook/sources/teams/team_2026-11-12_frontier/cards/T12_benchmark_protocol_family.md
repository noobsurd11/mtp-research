# T12 family card: benchmark protocol v0.2 (evaluation of thin structures on small noisy sets, benchmark construction, severity, other modalities)

Analyst T12, 13 Nov 2026. Tags: R = from the paper (what I read is stated per card), E = from our files (path given), S = my judgement.
Research MCP tools were not available in this session (ToolSearch found none); papers were read through arXiv / GitHub pages with WebFetch. Publisher pages (Elsevier, IEEE, EDP) returned 403 or were not tried; for those the scout record is the only source and is marked "scout record".
Ledger: `cards/ledger/T12.tsv` (56 papers: PROTOCOL 24, RUN_AFTER_GATE 2, PARKED 30). Spec: `cards/T12_benchmark_protocol_spec.md`.
Nothing launched. No GPU, no server, no sealed data touched.

## 0. What this family changes, in one paragraph (S)
None of these papers raises a score. They decide whether the numbers that every other family reports can be trusted: the pass margin (A/A calibration of the two-stage bootstrap), which crack metric leads (known-answer probes against width inflation and annotation jitter), how stable a method ranking is (rank intervals), which tolerance is justified (95th percentile of distances between two drawings of one crack), what leaks (pool vs E1 modules, ELPV vs ELPVPower), and whether a severity output is worth showing (only inactive area fraction is supported by the power literature; crack length is not). Seven of the eight items are CPU only on dumps that exist tonight or after the W1-C relay.

---

## 1. Papers read in full or in part (cards)

### P133 Accounting for Variance in Machine Learning Benchmarks (Bouthillier et al.)
- arXiv:2103.03098 (MLSys 2021). https://arxiv.org/abs/2103.03098. Read: HTML full text, first 100k characters.
- **Claims (R):** variance sources studied: data sampling (bootstrap of the dataset), augmentation, weight init, dropout, data order, hyperparameter optimisation. "Bootstrapping data stands out as the most important source of variance"; init variance is generally under 50% of the bootstrap variance, on par with data order. Benchmark variance is "on the order of magnitude of the individual increments" of published improvements. Recommendation: randomise as many sources as possible; prefer several data splits to one fixed test set; compare with P(A>B): significant if the lower bound > 0.5, meaningful if the upper bound > gamma = 0.75. A cheaper biased estimator that randomises more sources is 51x cheaper than the ideal one.
- **Evidence check (S):** five case studies, classification and segmentation-style tasks with large test sets; the qualitative point (split variance > seed variance) is likely stronger for us (330 groups, inactive in 34 groups). Our screen randomises seeds only, on one fixed split (cv5v2).
- **Code:** none needed.
- **Hypothesis for our data (S):** between-split variance of pooled OOF inactive IoU exceeds between-seed variance; if so, a 5-seed table on one split understates uncertainty, and the final table should give each seed its own grouped fold assignment.
- **Status:** PROTOCOL (arm `aa_calibration`, optional split-variance probe).

### P188 Surface Dice at tolerance tau (Nikolov et al.)
- doi:10.2196/26151 (JMIR 2021); arXiv:1809.04430. Read: HTML v3, first 100k characters.
- **Claims (R):** surface DSC at tolerance tau = (|S_i within tau of S_j| + |S_j within tau of S_i|) / (|S_i| + |S_j|). Tau per organ = "the 95th percentile of the distances collected across multiple segmentations from a subset of seven TCIA scans" (the results text says three consultant oncologists on the validation subset; the paper is inconsistent on this). Volumetric DSC "weighs all regions of misplaced delineation equally and independently of their distance from the surface" and is biased to large organs. No tau values in mm in the part I read.
- **Code:** github.com/deepmind/surface-distance (R: released by the paper; licence not checked). Pure numpy / scipy (S, not installed).
- **Evidence check (S):** for a 1 to 2 px line, the surface is the whole mask, so our relF1@2 is surface Dice at tau = 2 up to the boundary definition (pixel set vs surface elements). What we lack is the paper's rule for tau: our 2 px came from "0.82 to 0.99 agreement within 2 px" (E BRIEF 2), not from a percentile of distances.
- **Hypothesis:** the 95th percentile of distances between two drawings of the same crack, on our train + val same-cell pairs, lies at or below 2 px; if it lies near 3 px, relF1@3 is the principled headline.
- **Status:** PROTOCOL (arm `tau_from_annotators`).

### P134 Fine-grained IoU (Wang, Blaschko et al.)
- arXiv:2310.19252 (NeurIPS 2023 per scout). Read: HTML, first 100k characters. Code github.com/zifuwanggg/JDTLosses (R: link in paper; not opened).
- **Claims (R):** mIoU^D (dataset), mIoU^I (per image over non-NULL classes), mIoU^C (per class over images where the class is not NULL), mIoU^K (per instance, FP shared by instance size), worst-case mIoU^{C^q} (mean of the lowest q% per-image IoUs of a class). A class absent from the GT is NULL whatever the prediction; present in GT and absent from the prediction scores 0. Rankings: "only minor local rank discrepancies" between mIoU^C and mIoU^D; none between mIoU^C and mIoU^I; worst-case metrics change the order (UNet-ResNet101 drops on mIoU^{C^5}). Cityscapes truck: UNet 65.58 vs DeepLabV3 81.48 on mIoU^D but 68.78 vs 69.09 on mIoU^C. For small datasets q >= 5 is advised.
- **Evidence check (S):** natural-image datasets with thousands of images; our crack cells are 229 (P532), so q = 10% means 23 cells, which is still noisy.
- **Hypothesis:** per-cell crack IoU (mIoU^C style) and worst-10% per-cell relF1@2 give the same method order as pooled metrics except where a method fails on a subset of cells (BMRK, faint cracks): exactly the "almost all cracks" goal.
- **Status:** PROTOCOL (arm `metric_validity_probe`, candidate metrics; arm `rank_stability`).

### P578 challengeR: methods and toolkit for challenge results (Wiesenfarth et al.)
- doi:10.1038/s41598-021-82017-6; arXiv:1910.05121. Read: PDF pages 4 to 9.
- **Claims (R):** ranking stability is shown by bootstrapping test cases (b = 1000), blob plots (frequency of each rank per algorithm with 95% bootstrap rank intervals), violin plots of Kendall's tau between the full-data ranking and each bootstrap ranking, significance maps (one-sided Wilcoxon signed rank, Holm-adjusted, 5%), and line plots of rank across ranking methods (mean-then-rank, median-then-rank, rank-then-mean, rank-then-median, test-based). Example: on a Decathlon task with 10 test cases (T2) every algorithm reached rank 1 in at least one bootstrap sample; the 95% interval of A5 covered ranks 4 to 13; mean-then-rank differed from test-based ranking because of outlying cases.
- **Code:** github.com/wiesenfa/challengeR (R; R language, not Python; licence not checked). We reimplement the few pieces in numpy on our bootstrap (S).
- **Hypothesis:** with 330 module groups our crack ranking among methods within M of each other is unstable (median bootstrap Kendall tau < 0.8), and inactive ranking is unstable for nearly all pairs.
- **Status:** PROTOCOL (arm `rank_stability`).

### P358 Hierarchical bootstrap for multi-level data (Saravanan, Berman, Sober)
- arXiv:2007.07797. Read: abstract page.
- **Claims (R):** traditional tests on nested data can give "a false positive rate of over 45%" at a nominal 5%; summarising per higher level fixes the false positives but "greatly reduces the statistical power"; the hierarchical bootstrap (resample the top level, then the lower levels) keeps the error rate near nominal with more power.
- **Evidence check (S):** our two-stage bootstrap (groups, then one seed per fold and arm) is a hierarchical bootstrap; it has never been checked against an A/A null.
- **Status:** PROTOCOL (arm `aa_calibration`).

### P265 Pervasive label errors in test sets (Northcutt, Athalye, Mueller)
- arXiv:2103.14749 (NeurIPS 2021 Datasets and Benchmarks). Read: abstract page.
- **Claims (R):** at least 3.3% label errors on average across 10 test sets; at least 6% on ImageNet val; ResNet-18 overtakes ResNet-50 if the share of mislabelled test examples rises by about 6%; VGG-11 overtakes VGG-19 on CIFAR-10 at about 5%.
- **Evidence check (E):** our held-out labels have known problems: one cell carried another cell's mask (fixed in v1.1), mask copies between stages, dotted labels in 22 cells, label audit flagged 24 of 239 train crack cells (BRIEF 5). Nothing systematic for CV held-out cells.
- **Hypothesis:** removing the cells whose labels the out-of-fold ensemble flags (no manual relabelling) changes the order of near-tied methods.
- **Status:** PROTOCOL (subset axis in `rank_stability`; flags come from T10 A0(e) for inactive and from T3 `oof_selective_ignore` for crack, not re-built here).

### P595 Metrics or Mirage? Polyp segmentation benchmark audit (Urooj, Abdien, Madan)
- arXiv:2607.08203 (July 2026, ECCV Workshops submission). Read: abstract page. No code stated.
- **Claims (R):** 27 papers 2015 to 2026; at least 5 incompatible split protocols on Kvasir-SEG / CVC-ClinicDB; 25 of 27 omit Hausdorff distance; 26 of 27 have no significance test; 4 papers after Metrics Reloaded repeat the problems; under a uniform scorer the "best" model changes with the metric and near-tied rankings reverse across random splits; a 5-point reporting checklist (items not listed in the abstract).
- **Evidence check (S):** the same pattern is documented for EL in PROTOCOL_DRAFT section 1 (12 rows, E). This paper is the closest template for writing it up as an audit.
- **Status:** PROTOCOL (arms `rank_stability`, `reporting_governance`).

### P601 MeshMetrics (Podobnik, Vrtovec)
- arXiv:2509.05670. Read: abstract page. Code github.com/gasperpodobnik/MeshMetrics (R; licence not stated on the page).
- **Claims (R):** open-source tools disagree on the same masks by more than 100 mm Hausdorff and 30 percentage points NSD; mesh-based computation avoids distance quantisation.
- **Evidence check (S):** on a 2-D pixel grid at tau = 2 px the main ambiguity is the distance convention (Euclidean distance transform vs square or cross dilation; distance <= 2 vs < 2). Our relF1@2 uses one convention (m0 `cell_stats`). The benchmark must state it and give a unit test; a mesh tool is not needed (S).
- **Status:** PROTOCOL (unit tests inside `metric_validity_probe`).

### P263 Module power prediction from EL (Hoffmann et al., elpvpower)
- doi:10.1002/pip.3416; arXiv:2009.14712. Read: HTML v2 (methods and results text; result tables did not render), repo README.
- **Claims (R):** 719 EL measurements of 137 module instances, 3 module types (T1, T3 poly 60 cells; T2 72 cells), Greateyes 2048 x 2048 camera; Pmpp from I-V curves extrapolated to STC (indoor flasher 1.45% uncertainty, on-site at least 5%). 5-fold CV grouped by module, stratified on 20 relative-power bins. Abstract: SVR baseline (mean / sd intensity + ResNet18 features) MAE 9.0 +- 3.7 W (4.0%), ResNet18 MAE 7.3 +- 2.7 W (3.2%). "Thresholding on inactive area gives an MAE of 8.5 +- 21 Wp", on par with the baseline. CAM variant: per-cell loss "roughly proportional to inactive area"; cracks of minor importance on this data. Trained on T1, it generalises to T2 but not T3.
- **Code / data:** github.com/ma0ho/elpvpower (Python, `train.py`, `inference.py`, released checkpoints incl. a CAM model; no licence file shown; README: "free to use ... please cite"). Data: Jülich DATA doi:10.26165/JUELICH-DATA/TVWUUP (landing page 403 to me; licence and size unverified).
- **Evidence check (S):** the only public set I found with module EL and measured power. Module-level, so our cell masks must be summed per module. Same lab family as ELPV (our BMRK cells): a module overlap with BMRK training cells is possible and must be checked before any use.
- **Hypothesis:** module sum of predicted inactive area fraction correlates with relative power loss (Spearman >= 0.6) and better than predicted crack length does.
- **Status:** RUN_AFTER_GATE (arm `severity_external_elpvpower`; gate in the spec).

### P617 Impact of cell cracks on performance with current cell technologies (Hashem et al.)
- doi:10.1051/epjpv/2026017 (EPJ PV 17, 25, 2026). Read: abstract via search snippet; full text page returned 403.
- **Claims (R, abstract):** 230 mono-Si mini-modules, full-cell PERC and half-cut TOPCon, 2 to 12 busbars, EL plus I-V at 200 and 1000 W/m2, line cracks that do not isolate cell parts only. Crack length and number are not universal predictors of power loss; crack sensitivity is governed by irradiance, busbar count and cell architecture.
- **Consequence (S):** a severity output from our masks must not use crack length as a power proxy. Only isolated (inactive) area has support (P263 CAM, P628 R2 0.85 per scout, Gabor 2022 thresholds via handbook 05 section 15).
- **Status:** PROTOCOL (arm `t5_post_eval`).

### P609 Crack modes and hot spots (Dhimish et al.)
- doi:10.1038/s41598-021-03498-z (Sci Rep 2021). Scout record only.
- **Claims (R, scout):** 12 cells; four crack modes (free, micro-crack, shaded / isolated area, breakdown); modes 1 to 2 no hot spot; modes 3 to 4 heat from 25 C to 100 C; worst at 40 to 60% shading ratio (105 C).
- **Use (S):** defines the label-free "isolation risk" quantity of `t5_post_eval` (a crack that, with the cell border, cuts a region off from every ribbon). It also says why thermal cannot replace EL for thin cracks (modes 1 to 2 are thermally silent).
- **Status:** PROTOCOL.

### P492 WILDS (Koh et al.)
- arXiv:2012.07421. Scout record (well-known paper; not re-read).
- **Claims (R, scout):** 10 datasets with group-defined splits; ID and OOD reported separately; standard training is lower OOD on every dataset; worst-group metrics.
- **Use (S):** a worst-source relF1@2 (sources with >= 40 CV cells: ARTS, BMRK, CFVS, CSIR) as a secondary metric; LOSO stays as T7's U1 and PROTOCOL 3.4.
- **Status:** PROTOCOL.

### P570 Leakage and the reproducibility crisis (Kapoor, Narayanan) and P579 near-duplicate detection with pretrained embeddings, P631 SolarFCD
- doi:10.1016/j.patter.2023.100804; arXiv:2312.07273; arXiv:2604.23662. Scout records.
- **Claims (R, scout):** P570: 8 leakage types across 294 papers in 17 fields; model info sheets. P579: foundation-model embeddings with cosine thresholds find near-duplicates that bias evaluation. P631: merged 4,435 thermal / RGB images with near-duplicate removal, but an 80:10:10 random split that mixes plants.
- **Evidence (E):** our known leaks are module-level (PROTOCOL 1 row 5; 3.1); the module rule uses positions, crack-mask IoU and CFVS high-pass correlation. Pool vs E1 is checked by image id only (T7 spec line 160, 225). BMRK cells have no module id.
- **Status:** PROTOCOL (arm `leakage_audit_v02`).

### P439 Metrics Reloaded (Maier-Hein et al.)
- doi:10.1038/s41592-023-02151-z; arXiv:2206.01653. Scout record and the alternative D43 note. Code github.com/Project-MONAI/MetricsReloaded (scout; not opened).
- **Claims (R, scout):** Delphi consensus; problem fingerprint (structure size, reference quality, imbalance) drives metric choice; no empirical score gain.
- **Use (S):** our fingerprint is written into `metric_validity_probe`. The alternative note's rule (keep a metric only if its seed SD is below a known real gap) is the core of that arm, made stricter with width and jitter probes.
- **Status:** PROTOCOL.

### Other PROTOCOL papers (scout records only)
- P355 (CI coverage study, MedIA 2026) and P357 (CI width vs test size; companion ISBI: about 8 Dice points CI width at 20 cases, SD 0.10): CI method and aggregation choice; both support printing intervals on the L-test (49 cells) and E1. Arm `aa_calibration`.
- P501 (Bates, Hastie, Tibshirani, JASA 2023): naive CV intervals under-cover because fold errors correlate. We do not run nested CV (cost); we calibrate our bootstrap against A/A splits instead.
- P271 (How many seeds?): power analysis per metric. Arm `aa_calibration`.
- P598 (small-organ benchmark, 2026): overlapping CIs and unstable ranks in low-data benchmarks. Arm `rank_stability`.
- P545 (CIs uncovered, MICCAI 2024): over 50% of 221 MICCAI 2023 papers report no variability; median CI width 0.03, three times the median gap between first and second. Arm `reporting_governance`.
- P582 (whiteboard stroke protocol, 2026): thin-subset equity analysis and per-image worst case. Candidate metric in `metric_validity_probe` (crack components < 20 px as a stratum).
- P443 (open PV reliability data sets, Applied Energy 2025; scout read the full text): inventory of EL, IR, PL, UVF sets (OpenUVF 3,000 labelled / 21,600 unlabelled cells; NREL field PL 856 half-cut images). List of external EL sets for the leakage audit and the modality notes.
- P637 (imaging-based inspection benchmark review, RSER 2027): states that reported IR / EL / UVF accuracies come from different data and protocols and are not comparable. Cited in `reporting_governance`.

### RUN_AFTER_GATE besides P263
- P564 (Data in Brief 2026): pixel-aligned EL, NIR and visible images of a few poly cells after staged mechanical, thermal and electrical damage, with Isc / Voc per stage; CC BY (scout). Cell-level electrical data, tiny. Second external check in `severity_external_elpvpower`, same gate plus download check.

---

## 2. Severity and post-evaluation: decision with evidence

**What the literature supports (R):** power loss follows isolated (inactive) area, not crack length: P263 CAM per-cell loss roughly proportional to inactive area, inactive-area thresholding about as good as an SVR on image features (8.5 vs 9.0 W MAE); P617 crack length and count are not universal predictors for non-isolating cracks; P628 (scout) cell power from inactive area plus busbar count, linear R2 0.85; Gabor 2022 (via handbook 05 section 15) "critical" > 1% isolated area, "very critical" > 20%; P609 only isolated / breakdown modes heat up.

**What our labels allow (E, PROTOCOL 6 T5):** inactive area bands on P532: 0% 484 cells, < 0.5% 10, 0.5 to 1% 7, 1 to 20% 31, >= 20% 0. Inactive never occurs without crack in Pratt labels. Crack mode A vs C is therefore just "cell has inactive or not"; mode B (partly disconnected, dark gradient) has no label. No cell in our sets has electrical data.

**Computable from predicted masks without new labels (S):**
1. Per-cell inactive area fraction (of non-padding px), its error against GT, 3-band agreement (0, < 1%, >= 1%), cell-level inactive detection.
2. Crack length (skeleton px) per cell. Reported, but not as a severity proxy (P617).
3. Crack orientation relative to ribbons: principal angle of each crack component vs the ribbon direction from the predicted ribbons class (ribbons IoU 0.647 on test, E BRIEF 3). Descriptive only.
4. Isolation risk: area of cell regions that predicted crack components (with the cell border) separate from every ribbon. Untested; it becomes a reported quantity only if it predicts GT inactive on GT masks (pre-check in the spec).

**Published power relations and what they need (R / S):** P263 (module EL + Pmpp, public), P628 (cell EL + cell I-V, not public per scout), P626 Sandia pvcracks (cell EL + I-V pending release), P600 / P621 (module EL at two biases + I-V; Sandia PV-IV-EL per scout, unverified), P572 (half-cut modules, private), P629 (calibrated luminescence intensity). All need electrical data we do not have for our cells.

**Decision (S):** a severity track does not add real value now. A power-loss band cannot be scored on our cells (no electrical ground truth; 0 cells in the >= 20% band; 31 cells in 1 to 20%). The cheapest honest version is the light post-evaluation already in PROTOCOL v0 (T5), corrected by the literature: inactive area fraction is the severity quantity, crack length is descriptive only, isolation risk is added only if its GT pre-check passes. The one route to a real power link is ELPVPower (P263), gated (spec arm 8), and best done after the final model exists. Power-loss modelling is parked.

---

## 3. Other modalities: what a future track would need (no experiments)

**Thermal IR (drone or handheld, sunlit).** Sees what dissipates power: hot cells from isolated areas (P609 modes 3 to 4), bypass diode faults, interconnect breaks from about 600 W/m2, heavy soiling; cracked but connected cells are hard to tell from healthy ones (P614, scout) and thin cracks are invisible (handbook 22). A track would need: module- or cell-registered IR with labels at the level IR can resolve (hot cell / hot spot / diode / string), a cross-plant split (P445 and P632 show plant shift is the main gap; P631's random split is the counter-example), irradiance and wind recorded per image (P614), and a delta-T severity rule (P611: hot spot > 5 C above neighbours, bands up to >= 15 C). Public candidates: PVF-10 (P632, licence unverified), InfraredSolarModules, DTU A3 with EL on the same induced faults (on disk, `datasets/thermal_public/`). WattCycle owns a drone IR camera; a pilot flight with a module ID map (P634 PV-Hawk) would be the first real data. Link to this benchmark: an EL-to-IR mapping table (which EL classes have a thermal signature), not a shared metric.

**Photoluminescence (PL).** Contactless; outdoor and aerial PL exist (P590: 13.6 modules per minute, verified against indoor EL; P638: 5 of 7 defect types detected, cracks only under some conditions, interconnect failures not at all). PL without current flow does not show electrically isolated area as dark the way EL does, so the EL / PL contrast could separate inactive (disconnected) from recombination-dark material (P591 decomposes one EL into PL-like and Rs-like images, simulation only, no weights). A track would need registered EL + PL pairs of the same cells (none public that I verified; NREL field PL has 856 half-cut images without EL pairing, P443) and a crack label protocol for PL. Not feasible before December.

**UV fluorescence (UVF).** Daylight-free night imaging of encapsulant fluorescence; crack lines appear after months of field exposure as dark lines where oxygen bleached the EVA. OpenUVF (P443): 3,000 labelled and 21,600 unlabelled cell images for cracks. Fast (P637: > 91% crack detection at 10 to 15x EL throughput, different data and protocols). Limits: only old cracks in aged modules, no inactive area, depends on encapsulant. A track would need OpenUVF's licence and split by module, a crack-only class list, and a tolerant metric; a joint EL + UVF model (P396) is a training idea, parked.

**Daylight / drone EL.** P566: drone EL at 120 fps with modulated bias in daylight, SNR_avg 4.6. Resolution and SNR fall like E1's shift. A cheap proxy track (degrade CV cells to drone-EL resolution and noise, measure the drop) belongs to the robustness probes (T5 / T7), not to this benchmark version.

---

## 4. PARKED papers with reasons (short)
See `ledger/T12.tsv`. Main reasons: no electrical data for our cells (P572, P600, P621, P626, P627, P628, P629, P636); other families own the mechanism (P153 by T4 src_film; P388, P470 anomaly priors; P423 by T10; P445 by T7; P451 by T2 soft_band_jml; P365 SegFormer by T6 P260); future modality tracks without data or with unverified licences (P566, P590, P591, P592, P611, P613, P614, P632, P633, P634, P638, P639); P552 has no pixel output; P602 needs an independent second rater; P396 needs OpenUVF and a two-modality trainer.
