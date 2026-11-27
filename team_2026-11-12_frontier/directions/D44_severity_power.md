# D44: Severity grading and power-loss estimation from EL (post-evaluation)

Scout: D44, 13 Nov 2026. R = what a paper measured, E = what our files measured, S = my judgement.

## Bottom line (S)
- Very little here will lift crack IoU. Two ideas could lift **inactive**. Both are post-processing steps with no training and close to zero GPU cost:
  1. A crack-isolated-area rule. Find the cell regions that our predicted cracks cut off from the ribbons, and mark the dark ones as inactive (PV-Vision, Chen 2023).
  2. A dark-pixels-near-crack proxy (STC-Net 2026).
  Both use the BRIEF fact that 99% of inactive regions touch a crack. They target BMRK and E1, where the model misses inactive regions.
- A third idea needs training and is a long shot: a loss on per-cell inactive fraction and crack density, modelled on CF-Loss.
- The main value of this direction is for the **benchmark**. Four findings (R) shape how a severity track should be scored:
  - Inactive or isolated area drives power loss.
  - Crack length and crack count do not reliably predict power loss in modern modules.
  - The worst cell dominates a module's power.
  - Pratt's own lab (CSIR, one of our 5 sources) measured EL plus I-V on 680 modules.
- So a severity track should score inactive fraction and isolated area per cell, plus a 3-way crack mode. It should not score crack length.
- Two public EL + power sets exist for an external check:
  - Sandia PV-IV-EL: 438 modules, 613 EL + flash I-V pairs, CC BY 4.0.
  - FAU ELPVPOWER: 718 or 719 modules with Pmpp; the review gives 718 and the Hoffmann paper 719.

## Queries run (24 search calls + snowball)
search_papers (OpenAlex only answered; S2 / Scopus / arXiv were rate-limited or 401 the whole session):
1. electroluminescence power loss prediction deep learning (2020+)
2. crack mode classification inactive area solar cell electroluminescence power loss (2020+)
3. EL image I-V curve prediction photovoltaic module (2020+)
4. fraction of inactive cell area power loss photovoltaic module cracks (2020+)
5. Pratt electroluminescence segmentation module power degradation inactive area quantification (2020+)
6. defect detection and quantification electroluminescence U-net semantic segmentation power (2020+)
7. benchmark dataset defect detection classification EL semantic segmentation (2021+)
8. EL defect power loss module correlation inactive area cracks I-V measurement dataset (2025+)
9. IEC TS 60904-13 electroluminescence defect classification criteria (2018+)
10. power loss simulation cracked solar cell EL busbar isolated area (2019+)
11. solar cell output power prediction from EL image cell-level dataset (2022+)
12. Metrics Reloaded recommendations image analysis validation (2022+)
13. second-life PV module reuse grading electroluminescence (2021+)
14. crack quantification length width error evaluation segmentation skeleton (2021+)
15. electroluminescence power loss estimation segmentation inactive area crack (2025+)
16. XGBoost cell power loss cracks EL MultiSolSegment PVSC (2024+)
17. crack type classification mode A B C deep learning EL (2020+)
18. electrically isolated cell area crack detection module EL severity rating (2022+)
19. deep learning series resistance map luminescence image solar cell (2022+)
20. segmentation evaluation by downstream clinical measurement error rather than Dice (2021+)
21. half-cut cell crack power loss EL module mismatch (2024+)

search_snippets: 5 attempts, all rate-limited (S2 keyless pool).

Snowball:
- get_citations on Hoffmann 2021 (pip.3416, 32 citing) and Chen 2023 (jphotov.2023.3249970, 54 citing).
- similar_papers on Hoffmann + Chen + STC-Net.
- read_paper on STC-Net (power-loss section), Chen 2025 open-data review (EL and I-V dataset sections) and MultiSolSegment (future work).
- fetch_fulltext failed or timed out on Chen 2023, Jaeckel 2024 and the Sandia OSTI report.

WebSearch (9 searches):
- verified code: elpvpower, PV-Vision, pvcracks
- looked for STC-Net code and found none
- checked the Jost 2026 title and the CF-Loss code: neither found
- found the Pratt 2025 680-module paper
- found the Sandia PV-IV-EL details
- found the Jaeckel classification table

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/jphotov.2023.3249970 (Chen, Karin et al., PV-Vision) | 2023 | IEEE JPV | github.com/hackingmaterials/pv-vision (pip pv-vision) | Segment cracks and busbars, then compute the crack-isolated area: cell regions that cracks cut off from every busbar, plus their brightness and the crack length | Use our predicted crack + ribbons (+ busbars where present) + border. Components of the cell interior that touch no ribbon pixel are isolated. If an isolated part is darker than a source-wise threshold fitted on train, call it inactive and OR it with the model's inactive. Half-cut E1 cells need the cut edge as an extra barrier | 52 | 85 |
| 2 | arxiv:2608.01714 (STC-Net) | 2026 | arXiv / MERCon | no link found ("GitHub" label only) | Crack net with edge + spectral priors and a boundary-topology refinement module. Inactive proxy = pixels below a percentile in a dilated predicted-crack zone, cleaned by morphology. Power loss modelled as linear in inactive fraction | Use only the proxy as a second post-processing arm. Fit the percentile and dilation radius per source on train/val, because BMRK and SDLE contrast differ. R: PVEL-S binary, train mIoU 95.98 vs test 72.52, so their network gives no evidence for our thin-crack IoU | 45 | 60 |
| 3 | doi:10.1016/j.media.2024.103098 (CF-Loss) | 2024 | Medical Image Analysis | not verified | Adds to the pixel loss a loss on clinically used features computed from the soft mask (vessel density, box-count fractal dimension) | Per-cell L1 on the soft inactive fraction and on the soft crack density (pixels per cell area) against GT, weight 0.1 to 1, on top of PF. Pushes the model to get the amount of inactive right in BMRK and E1 cells. Thin vessels are the nearest domain to cracks | 38 | 30 |
| 4 | doi:10.1016/j.solener.2026.114469 (MultiSolSegment) | 2026 | Solar Energy | in sandialabs/pvcracks per the paper and docs (repo not opened); weights and data on DuraMAT DataHub | Multi-channel U-Net with independent crack, busbar, dark-area and non-cell maps, so a crack can sit inside a dark area. The authors feed these maps to a VAE + XGBoost power model | Same arm as D27 row 2 (3 sigmoid channels for crack / inactive / dark). This fixes the 20% of crack pixels lost at inactive regions. For D44 the output gives clean crack and inactive inputs to rows 1 and 2. D27 reported no code; the paper says the code is in pvcracks | 55 | 70 |
| 5 | doi:10.1002/pip.3416 (Hoffmann et al.) | 2021 | Prog. Photovolt. | github.com/ma0ho/elpvpower; data doi 10.26165/JUELICH-DATA/TVWUUP | ResNet regressor from module EL to Pmpp: MAE 7.3 Wp (3.2%) on 719 modules. CAM variant gives power loss per cell. Inactive regions and fractures dominate the prediction; cracks matter less | External task-level check. Crop cells (PV-Vision preprocessing), resize to 512, run our models, sum the predicted inactive fraction per module, then rank-correlate with measured Pmpp loss. The module images are 900 x 1500, so cells are about 150 px: a 3x upsample and a domain gap | 22 | 80 |
| 6 | doi:10.1109/jphotov.2025.3562931 (Byford et al.) | 2025 | IEEE JPV | not verified | Swin transformer from EL to the full I-V curve. MPP, Isc and Voc errors < 1%; Rs error 5.19% | Reference for the Sandia PV-IV-EL set: 438 modules, 613 EL + flash I-V pairs, EL at 20% and 80% Isc, CC BY 4.0 per OpenEI 8378. Use the set as a second external power check for our predicted inactive fraction. Not a method for our masks | 15 | 70 |
| 7 | doi:10.1016/j.solcom.2026.100196 (Dhimish & Lee) | 2026 | Solar Compass | none found | Two stages: segment cracks and low-luminescence regions (Dice 0.86), turn the spatial features into module power loss (R2 0.93, MAE 0.0183, 500 half-cut modules), then rebuild I-V with a single-diode model | Template for a half-cut severity stage. E1 has 58 half-cut cells and training has 0. Their point that defect shape alone does not show severity in half-cut modules (current redistribution) argues for a separate half-cut severity rule | 22 | 75 |
| 8 | doi:10.3390/en19040876 (Dhimish, Benatto, Vieira, Poulsen: EL-to-IV) | 2026 | Energies | none found | CNN maps a pair of EL images (20% and 80% Isc) to the I-V curve on 438 modules; MPP and FF error < 2%; still works with one EL image | Same module count and bias levels as Sandia PV-IV-EL (match likely, unverified). We have one EL image per cell and no I-V, so it is useful only as a benchmark reference row for "power from EL" | 12 | 55 |
| 9 | doi:10.1109/ictas64866.2025.11155421 (Pratt, May, Mkasi) | 2025 | ICTAS | no | Pratt's 29-class DeepLabV3 retrained with a new "brightening" class. Applied to 48,960 cells of 680 CSIR-lab modules with EL + I-V. Brightening fraction vs module FF: r2 0.42 (exponential decay model) | Closest data to ours: same lab and class scheme, CSIR source. If Pratt shares the 680 module EL + I-V, it becomes the benchmark's power track on the E1-like domain. Ask; do not assume | 15 | 80 |
| 10 | doi:10.1051/epjpv/2026017 (Hashem et al.) | 2026 | EPJ PV | n/a | 230 mini-modules (PERC full-cell, TOPCon half-cut, 2 to 12 busbars). Line cracks without isolation: crack length and count are not universal predictors of power loss. Moderate correlation only for PERC at 200 W/m2; none for TOPCon | Benchmark rule: do not use crack length or count as the severity target. Score isolated or inactive area instead, and keep crack detection as a separate safety and progression item | 8 | 70 |
| 11 | doi:10.1051/epjpv/2024039 (Jaeckel et al., PV-Riss nomenclature) | 2024 | EPJ PV | n/a | Industry and lab nomenclature for EL observations: single cracks, multi-cracks, electrical-circuit anomalies, miscellaneous. Classification proposal combines the risk of power loss beyond warranty with the electrical safety risk, per inspection stage | Map our 12 defect classes onto the 4 categories. Use its classification as the severity label scheme for the benchmark instead of inventing one. Full text not retrieved: thresholds unverified | 8 | 75 |
| 12 | doi:10.3390/s24051479 (Saborido-Barba et al.) | 2024 | Sensors | n/a | Method following IEC TS 60904-13: % of Type-C crack area per cell to module power loss. Checked with I-V after repeated impacts; cell-level estimates beat substring or module level. The most damaged cell dominates | Per-cell severity in our benchmark = inactive fraction. A module-level proxy = max over cells, not the mean. Applies to E1 (67 modules) if module grouping is kept | 12 | 70 |
| 13 | doi:10.1016/j.solener.2026.114394 (Saborido-Barba et al.) | 2026 | Solar Energy | n/a | Automatic crack segmentation + Type-C quantification on 100 modules after 11 years. Power loss follows a GEV distribution, mean 12.77%; concentrated Type-C in one cell drives loss | Gives a realistic prior for power-loss bands, for example <5%, 5 to 20%, >20%, for a severity confusion matrix | 8 | 55 |
| 14 | doi:10.2172/17198208 (Jost et al., Sandia report) | 2025 | OSTI report | sandialabs/pvcracks (docs: VAE, XGBoost per-cell dPmpp, pvspice_lite) | Crack, dark and busbar masks are compressed by a VAE; XGBoost predicts power loss per cell | Bold option for the benchmark: once their cell EL + I-V data is released (listed as pending), score our masks by how well their power model, fed with our masks, matches the I-V. Until then, reference only | 10 | 65 |
| 15 | doi:10.4229/wcpec-82022-3bo.11.6 (Del Prado Santamaria et al., DTU) | 2022 | WCPEC-8 | no | Cell power from inactive area + histogram moments with busbar count as a categorical input: R2 0.869, max error 0.17 | Simplest physics-light severity regressor for our cells: inactive fraction + busbar layout. Usable only with paired I-V | 10 | 55 |
| 16 | doi:10.1109/pvsc59419.2025.11132985 (Del Prado Santamaria et al.) | 2025 | IEEE PVSC | no | Benchmarks an analytic power-loss model (bELMO) and a learned one (DTU ML) under lab, daylight and low-resolution InGaAs imaging. Both good at low loss; error grows for severe cracks; bELMO lower error overall | Design guide for our severity track: report error per severity band, not one pooled number. Our BMRK cells (downscaled ELPV) are the low-resolution case | 8 | 65 |

Scores: score = expected gain on our metrics x probability x feasibility. bench = value for the benchmark.

## Minimum experiments (ordered by cost)

1. **Isolated-area and dark-near-crack inactive rules** (rows 1, 2). CPU post-processing on existing predictions.
   - Arms:
     - (a) PV-Vision isolation rule, ORed with the model's inactive.
     - (b) STC-Net dark-in-dilated-crack rule, ORed.
     - (c) Both rules ANDed with p(inactive) > 0.05, to limit false positives.
   - Baseline: PF single model and PF 5-seed ensemble.
   - Fit the thresholds on the module-grouped 5-fold CV over 532 cells. Report on CV and E1. Test only once at the end.
   - Metrics: inactive IoU, inactive pixel P / R, inactive IoU on BMRK cells.
   - Kill: CV inactive IoU gain < +0.02, or inactive precision drop > 0.05.
   - Cost: under 2 GPU-h, for CV inference only.
2. **Severity-feature loss** (row 3).
   - Arm: PF + per-cell L1 on the soft inactive fraction (w 0.3) and the soft crack density (w 0.1).
   - Baseline: PF, 5 seeds.
   - Metrics: inactive IoU (CV), per-cell inactive-fraction MAE, crack IoU (clean 49).
   - Kill: inactive IoU gain < 0.015 and fraction MAE not reduced by >= 20%, or crack IoU drop > 0.012.
   - Cost: about 6 GPU-h.
3. **Benchmark severity track.** Scoring code only, no training.
   - Per cell, from GT and predicted masks:
     - inactive fraction (MAE)
     - isolated area (MAE)
     - a 3-way mode: no crack / crack without inactive (A or B) / inactive bounded by crack (C), scored by macro-F1
     - a power-loss proxy band on inactive fraction: 0, (0, 5%], (5, 20%], > 20%, scored by quadratic weighted kappa
   - Module level on E1: max-cell band.
   - Run it on at least 6 existing checkpoints (house, PF, ensembles, Skeleton Recall arms).
   - Kill: if the Kendall tau between the severity ranking and the inactive-IoU ranking is > 0.9 on both test and E1, the track adds no information; then put it in an appendix only.
   - Cost: under 1 GPU-h.
4. **External power check** (rows 5, 6).
   - Download ELPVPOWER and Sandia PV-IV-EL. Both are public, but ask the user before downloading, as for any large external data.
   - Crop cells with PV-Vision, run the house, PF and ensemble models, sum the predicted inactive fraction per module, and compute Spearman against measured Pmpp loss.
   - Kill: if no model reaches Spearman > 0.3, drop the power track as dominated by the domain gap.
   - Cost: about 3 GPU-h plus a day of preprocessing.

## Notable papers rejected
- doi:10.3390/en11051172 Kropp 2018 (ELMO): needs two EL images at different currents to get an Rs map. We have one image per cell.
- doi:10.1002/pip.3348 Kikelj 2020 (quasi-SPICE from EL damage): accurate (0.12% on one cell), but needs per-cell electrical calibration. Reference only.
- doi:10.1016/j.enconman.2024.118866 Ozturk 2024: module power from cell-level fault features (nMAE 0.035). It uses image-level fault classes, not masks, and no public data was found.
- doi:10.1002/pip.3484 Buratti 2021 (LumiNet efficiency binning): end-of-line cells, not field cracks.
- doi:10.1016/j.joule.2022.05.001 Buratti 2022 (GAN reconstruction for efficiency-loss analysis): interesting as an anomaly prior, but no abstract retrieved and the domain is end-of-line PL/EL. Belongs to D39.
- doi:10.1016/j.solmat.2023.112621 Luer 2023 (what physics a power CNN learned): no abstract or full text retrieved. Possibly useful to confirm "inactive drives power"; unverified.
- doi:10.1016/j.apenergy.2025.126132 Chen 2025 open-data review: used as a dataset map (ELPVPOWER, EPRI 36 modules with flash I-V, Sandia VAE masks). Not a method.
- doi:10.3390/solar4040034 Lofstad-Lie 2024: replacement cost-effectiveness at 1%, 10% and 33% loss. Useful only to justify the band edges.
- doi:10.1016/j.solmat.2026.114629 Ernst 2026 (I-V screening for second-life modules): relevant to WattCycle's business, but I-V based, not EL masks.
- doi:10.1007/s10278-026-02156-y downstream-aware QC (ADPKD MRI): accept / reject / rework classification. Too far from our setting.
- doi:10.1038/s41592-023-02151-z Metrics Reloaded: already covered by D41 / D43.

## Gaps
- Not read directly; text unverified:
  - IEC TS 60904-13. The standard is paywalled, and no paper retrieved its exact crack-classification thresholds.
  - VDE SPEC 90031 v1.0, "EL of PV modules: terms and classification". Seen in web results only.
- Jaeckel 2024 full text failed. Its risk-category thresholds are unverified.
- No paper does Koentges crack mode A / B / C classification with deep learning; queries 2 and 17 found none. If we want mode labels, derive them from our masks: inactive touching crack = C, crack only = A or B. B cannot be told from A without an intensity rule.
- The STC-Net code link was not found. CF-Loss code was not verified. Whether the Byford and EL-to-IV papers both use Sandia PV-IV-EL is unverified.
- Pratt 2025 (680 CSIR modules with EL + I-V): the data is not public. This is the single most valuable dataset for a power track on our domain; ask Pratt or CSIR.
- The pvcracks cell-level EL + electrical dataset is listed as pending release.
- search_snippets was rate-limited the whole session, so the evidence questions were not answered:
  - the slope of power loss vs inactive fraction
  - the crack-isolated-area algorithm details
