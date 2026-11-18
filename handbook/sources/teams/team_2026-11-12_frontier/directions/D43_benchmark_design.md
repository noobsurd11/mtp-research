# D43: How trusted segmentation and inspection benchmarks are built

Scout: D43, 13 Nov 2026. Literature only: no servers, no test or E1 predictions read.
Tags: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Bottom line (S)

- Most papers here shape how the benchmark is built and scored. Few of them raise scores directly. Three score arms come out of this direction:
  1. **Module-grouped 5-fold fold ensemble over the 532 train+val cells** (nnU-Net practice). It gives 54 more training cells, 5 diverse members, and out-of-fold (OOF) predictions on 532 cells for picking the crack logit bias and for the measurement problem. About 6 GPU-h. This is the cheapest arm in this direction that could raise the score.
  2. **nnU-Net v2 2D (ResEnc preset) as an auto-configured arm and a required benchmark baseline.** On OmniCrack30k it beat every other method by at least 10 points of clIoU@4px (R). It has never been run here (E, BRIEF section 5 "never tried: nnU-Net style auto-configuration").
  3. **Cross-domain crack pretraining (OmniCrack30k, 30k images) kept by the PF fine-tune.** UCF-EL pretraining failed because the house fine-tune erased the encoder (E). Crack-domain pretraining with PF has not been run.
- For the benchmark itself: use module-grouped CV plus a sealed test, report CIs and bootstrap rank stability, add tolerance metrics and E1 as an OOD split, run a leakage audit (near-duplicates and twins), and check the test labels. The sources: Isensee 2024, Metrics Reloaded, El Jurdi 2025, Andre 2026, challengeR, WILDS, Kapoor 2023, Northcutt 2021, MVTec AD 2, Konrad 2026.
- Past EL "benchmarks" (Hanifi 2025, Hijjawi 2025, Bayat 2026) share the flaws the user describes: random or image-level splits, a leaky UCF-EL split, old baselines, and no CIs. Bayat 2026 itself says module-level grouped validation is still needed.

## 2. Queries run (about 34)

search_papers (year_from 2019 to 2025, limit 8 to 20):
1. nnU-Net revisited rigorous validation medical image segmentation (2020+)
2. data leakage train test split group-wise evaluation machine learning reproducibility
3. leakage and the reproducibility crisis in machine-learning-based science
4. WILDS benchmark in-the-wild distribution shifts
5. photovoltaic electroluminescence defect segmentation benchmark comparison deep learning models
6. crack segmentation benchmark dataset unified OmniCrack30k CrackSeg9k
7. OmniCrack30k crack segmentation benchmark
8. CrackSeg9k collection and benchmark crack segmentation datasets
9. Medical Segmentation Decathlon generalisable segmentation benchmark (timed out, then retried as "Medical Segmentation Decathlon")
10. industrial anomaly detection benchmark MVTec VisA evaluation protocol critique
11. confidence intervals performance estimates medical image segmentation test set size
12. challenge ranking robustness bootstrap visualization challengeR
13. multiple annotators inter-rater variability segmentation evaluation ground truth uncertainty
14. tolerance-based evaluation thin structure segmentation relaxed precision recall boundary metric
15. benchmark semantic segmentation fair comparison baselines tuned equally rethinking progress
16. pervasive label errors in test sets destabilize machine learning benchmarks
17. datasheets for datasets documentation
18. surface defect segmentation dataset benchmark industrial KolektorSDD mixed supervision
19. segmentation benchmark evaluation leakage near-duplicate images train test overlap
20. benchmark segmentation methods small dataset rigorous evaluation statistical significance multiple seeds (2025+)
21. nnU-Net baseline outperforms transformer Mamba segmentation 2D benchmark revisited (2025+, timed out)
22. solar cell crack defect dataset electroluminescence annotated segmentation benchmark E-SCDD (2024+)
23. module-wise split photovoltaic deep learning generalization unseen modules evaluation electroluminescence
24. crack detection evaluation inter-annotator variability tolerance annotation width
25. meta-analysis overfitting test set reuse holdout adaptive Kaggle
26. spatial cross-validation overoptimistic map accuracy spatial autocorrelation
27. Are we done with ImageNet reassessed labels
28. crack segmentation benchmark unified protocol cross-dataset generalization evaluation (2025+)
29. rethinking evaluation industrial anomaly segmentation metrics benchmark flaws (2024+)
30. nnU-Net a self-configuring method (id lookup)

Snowball: get_citations on nnU-Net Revisited (30 citing papers; found nnWNet CVPR 2025). similar_papers on {nnU-Net Revisited, Metrics Reloaded, Kapoor leakage}.
search_snippets: 3 attempts, all rate-limited by Semantic Scholar (keyless pool). No snippet evidence was used.
Full text: nnU-Net Revisited section 2 (already local), El Jurdi 2025 (arXiv 2307.10926) sections 1 and 4.
WebSearch (4): MVTec AD 2 private test server; MedSegBench; OmniCrack30k repo and nnU-Net result; MetricsReloaded / challengeR / nnU-Net / KolektorSDD2 repos.

## 3. Selected papers

Score = value for raising OUR scores. Bench = value for the benchmark vision.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1038/s41592-020-01008-z | 2020 | Nature Methods | github.com/MIC-DKFZ/nnUNet | Self-configuring U-Net pipeline. The final model is the ensemble of the 5 cross-validation fold models, and the OOF predictions are used for configuration choices | Use the existing module-grouped 5-fold roots over the 532 train+val cells. Train the house recipe once per fold and ensemble the 5. Choose the crack logit bias on the 532 OOF predictions, not on 54 val cells. Report OOF CV metrics as the benchmark's development score | 72 | 90 |
| 2 | doi:10.1007/978-3-031-72114-4_47 (arXiv 2404.09556) | 2024 | MICCAI (LNCS) | github.com/MIC-DKFZ/nnUNet | Validation pitfalls: confounded boosters (ensembles, extra data, pretraining, compute), ill-configured baselines, unsuitable datasets (high statistical variance or low systematic variance), selective class reporting. Recommends nnU-Net ResEnc baselines and 5-fold CV with a separate test pool | nnU-Net v2 2D, ResEnc-M/L preset, 1-channel PNG at 512, all 24 labels, splits_final.json = our module-grouped folds. Run one arm with nnU-Net's default augmentation (it has rotation, scaling and elastic deformation, which resample 1-2 px cracks) and one with our label-safe augmentation. Every method in the suite is compared at matched compute and with no ensemble, plus one separate "with ensemble" table | 68 | 95 |
| 3 | doi:10.1109/cvprw63382.2024.00392 | 2024 | CVPR Workshops (VAND) | unverified (third-party listing gives github.com/ben-z-original/omnicrack30k) | 30k crack images from more than 20 datasets in one benchmark. The metric is centerline IoU with a 4 px tolerance (clIoU4px). nnU-Net reaches 64% and beats all others by at least 10 points; transfer learning works for cracks | (a) Metric: add tolerance clIoU at 1, 2 and 4 px next to relF1@2, because our labels jitter by 1 to 2 px. (b) Score arm: pretrain the U-Net++ encoder and decoder on OmniCrack30k as binary crack (images to grayscale, 512 crops), then fine-tune with PF so the encoder is kept | 52 | 85 |
| 4 | doi:10.1038/s41592-023-02151-z (arXiv 2206.01653) | 2024 | Nature Methods | github.com/Project-MONAI/MetricsReloaded (may be unmaintained) | A problem fingerprint (structure size, tubularity, annotation imprecision, class imbalance) chooses the metrics. Tolerance and boundary metrics (NSD), clDice for tubular structures, and object-level detection metrics for small rare structures | Fingerprint: crack = tubular, 1-2 px, imprecise annotation, so use clDice / tolerance F1 / component recall rather than strict IoU as the headline. Inactive = blobby and reliable, so use IoU plus per-cell detection. Other classes = mIoU_rob with a fixed class list. Write the fingerprint into the benchmark spec | 25 | 92 |
| 5 | doi:10.1016/j.media.2025.103565 (arXiv 2307.10926) | 2025 | Medical Image Analysis | github.com/rosanajurdi/SegVal | Parametric CIs match bootstrap CIs for segmentation. A 1% wide CI needs 100 to 200 test cases when the per-case SD is about 3%; SD 12-13% (brain tumour) needs more than 1000 | Compute per-cell crack IoU SD on clean-49 and the CI half-width. Derive how many cells the sealed test needs for a +/-0.01 CI. This puts a number on BRIEF problem 5 and sets the size of the new test and E1 sets | 35 | 85 |
| 6 | doi:10.1016/j.media.2026.104349 (arXiv 2601.17103) | 2026 | Medical Image Analysis | none found | 24 tasks, 19 models each: CI coverage depends on metric, aggregation (macro needs more cases than micro) and CI method. Gives a decision tree | Our crack IoU is pooled over pixels (micro), and inactive is decided by 3 cells. Report both micro (pooled) and macro (per-cell) values with the CI method the decision tree picks. State the aggregation in the protocol | 30 | 80 |
| 7 | doi:10.1038/s41598-021-82017-6 (arXiv 1910.05121) | 2021 | Scientific Reports | github.com/wiesenfa/challengeR | Bootstrap ranking stability, significance maps, and blob plots for comparing many methods on per-case scores | The leaderboard ranks methods by per-cell scores over the sealed test plus E1. Publish the rank stability (Kendall tau over 1000 bootstrap resamples) and call methods tied when ranks flip | 20 | 85 |
| 8 | arXiv:2012.07421 | 2020 | arXiv / ICML 2021 | wilds.stanford.edu | Group-defined splits (hospital, camera, region). Report ID and OOD separately with a standard package and fixed evaluation; ERM stays a strong baseline | Groups = module and source. Splits: ID test (modules seen), OOD-module test (E1: new modules, half-cut cells), and leave-one-source-out (BMRK, SDLE). Report the worst-source score next to the mean. The unlabeled pool is the WILDS-unlabeled analogue (arXiv:2112.05090) | 30 | 88 |
| 9 | doi:10.1016/j.patter.2023.100804 (arXiv 2207.07048) | 2023 | Patterns | none | A taxonomy of 8 leakage types across 294 affected papers, and "model info sheets" that argue train/test independence | Leakage audit for EL: the same module in train and test, CFVS train "twins", BMRK = ELPV cells (shared modules with other ELPV-derived sets), UCF-EL train/test overlap, and the pool overlapping test modules (SSL leakage). Publish a model info sheet with each split | 22 | 88 |
| 10 | arXiv:2312.07273 | 2023 | arXiv | none verified | Pretrained embeddings (DINOv2 and others) with cosine thresholds detect near-duplicate medical images that bias evaluation | Embed every cell (582 + E1 + F51/H36 + UCF-EL + pool) with the DINOv2/v3 encoders already used in our linear probes. Flag cross-split pairs above the threshold and check the flagged pairs against module ids | 20 | 82 |
| 11 | arXiv:2103.14749 | 2021 | NeurIPS Datasets and Benchmarks | none verified | Confident-learning flags test label errors (an average of 3.3% across 10 test sets). Corrected test sets change model rankings | Rank test and E1 cells by disagreement between the OOF ensemble and the label (crack component level). Re-check only the top few with minimal human review, as the no-labelling rule allows. Report rankings on the original and the corrected labels. CSIR_00070 is the known case | 30 | 78 |
| 12 | doi:10.59275/j.melba.2022-db5c (arXiv 2202.07550) | 2023 | MELBA | ivadomed.org | With several raters, compares STAPLE, label averaging and random rater sampling per iteration. SoftSeg (regression on soft labels) keeps or improves Dice and is better calibrated | Where a cell has two crack label versions (2021 original vs 2022 revised, or E-SCDD re-annotations), train the crack class on soft averaged labels or by sampling a rater each iteration. Score on revised labels and on the union | 35 | 50 |
| 13 | arXiv:2405.18435 | 2024 | arXiv (QUBIQ challenge) | none verified | Scores segmentation against the distribution of several raters (soft Dice over thresholds of the averaged label) | For crack, the benchmark test score uses the label-version distribution where two versions exist, so a method is not ranked on one annotator's 1-2 px trace | 15 | 65 |
| 14 | doi:10.1007/s11263-026-02743-0 (arXiv 2503.21622) | 2026 | IJCV | none (server) | Public test plus a private test whose labels are hidden and scored only by the server (2 submissions per 30 days, per a third-party page), plus a "private_mixed" lighting-shift split. The metric is threshold-dependent SegF1 | Sealed EL test: keep E1 and a new held-out module set off the public release, publish only the images, score through a script the maintainers hold. Fixed threshold chosen on val (no test-time threshold tuning). Add an "unseen module and cut type" split like private_mixed | 8 | 82 |
| 15 | doi:10.1016/j.bspc.2026.111226 (arXiv 2509.05892) | 2026 | Biomed. Signal Proc. Control | none verified | 10 models on a tiny dataset: bootstrap CIs of the top models overlap, rankings change between ID and OOD and across datasets, and results are sensitive to the split even after Bayesian HPO | Our regime (478 cells, 3 cells decide inactive) is the same. Require several seeds and several folds per method and report rank intervals, not single numbers | 15 | 75 |
| 16 | doi:10.1007/978-981-96-8892-0_4 | 2025 | LNCS | github.com/sntubix/pv-defect-segmentation | Prior EL semantic-seg baseline on the 29-class E-SCDD EL set. VGG16-UNet with class weights: feature mIoU 0.663, defect mIoU 0.326 | Include it as the "prior EL baseline" in the suite, re-run under our splits and metrics. Its numbers show why scores are not comparable: different class list (29 vs 24), different splits | 15 | 70 |
| 17 | doi:10.1016/j.solener.2025.114083 | 2025 | Solar Energy | stated public, URL not found | Instance-seg benchmark (Mask R-CNN, ConvNeXt, ConvNeXt-V2, Mask2Former, MMDetection) on UCF-EL: ConvNeXt-V2 mAP50 0.602, mIoU 0.650 | Flaw to document: UCF-EL has heavy train/test leakage (E). Useful as a method entry: run Mask2Former / ConvNeXt-V2 semantic or instance variants under our protocol | 20 | 62 |
| 18 | doi:10.3390/s26123775 | 2026 | Sensors | none | Controlled EL classification benchmark: 6 backbones, identical pipeline, stratified 5-fold, 150 runs. ConvNeXt-T macro-F1 93.1%. The authors say module-level grouped validation is still needed | Evidence that the EL field sees the gap. Copy its "identical pipeline, all folds, mean +/- SD" reporting, but with module-grouped folds and pixel-level metrics | 5 | 55 |

## 4. Minimum experiments (score arms first)

All arms use the house recipe unless stated. Main metrics: clean-49 crack IoU, relF1@2, inactive IoU, mIoU_rob, and E1 crack relF1@2 / inactive IoU.

1. **Fold ensemble (paper 1).** Arm: 5 house models (and a PF copy) trained on 4/5 of the module-grouped 532 cells each, then ensembled. Logit bias chosen on the 532 OOF predictions. Baseline: the 5-seed ensemble on the 478 train cells (crack IoU 0.485 to 0.488 at argmax, 0.492 with bias; inactive 0.456). Kill: argmax crack IoU < 0.488 AND inactive IoU < 0.456 on clean-49. About 6 GPU-h per variant. Side product: OOF CV scores for every later method.
2. **nnU-Net v2 2D ResEnc (paper 2).** Arm: nnU-Net 2D ResEnc-M, 5 folds = our folds, fold ensemble; variant with label-safe augmentation. Baseline: the paper-1 fold ensemble (same data, same ensemble size, so no confounded booster). Kill: crack IoU more than 0.01 below the baseline AND inactive more than 0.02 below; it stays in the suite as a baseline either way. Roughly 60 to 100 GPU-h (1000 epochs x 5 folds x 2). Needs nnunetv2 on the servers (an install, so the user must OK it).
3. **OmniCrack30k pretraining (paper 3).** Arm: U-Net++/ResNet-34 trained on OmniCrack30k binary crack (grayscale), then PF fine-tune on EL with 5 seeds. Baseline: PF 5-seed mean. Kill: crack IoU gain < +0.01 AND E1 crack relF1@2 gain < +0.02. About 15 GPU-h. Dataset download size and licence unverified.
4. **Soft multi-version crack labels (paper 12).** Arm: crack target = mean of the available label versions (soft), or a random version per iteration, on cells with 2 versions. Baseline: house on revised labels. Metric: relF1@2 and crack IoU on revised labels. Kill: relF1@2 below the baseline by more than 0.005. About 6 GPU-h. First check how many train cells have two independent versions.

Measurement and benchmark checks (no new training; run when the protocol is drafted):
5. CI sizing (papers 5, 6): per-cell crack IoU SD on clean-49 for the 5 house seeds, CI half-width under micro and macro aggregation. Decision line: if the half-width is above 0.02, the headline score must be OOF CV over 532 cells plus E1, not test-49 alone.
6. Rank stability (papers 7, 15): once 5 or more suite methods exist, compute bootstrap Kendall tau. Two methods whose ranks swap in more than 30% of resamples are reported as tied.
7. Leakage audit (papers 9, 10): DINOv2/v3 cosine near-duplicates across splits, plus module-id cross-check. Report the house model score on test cells with and without a near-duplicate in train (CFVS cells without a twin already score 0.397 vs 0.474, E).
8. Test label check (paper 11): OOF-vs-label disagreement ranking. Report rankings on original vs corrected labels. Decision line: if any pair of methods flips, publish both.

## 5. Benchmark design implications (S)

- Splits: module-grouped 5-fold CV over the 532 development cells (exists). A sealed test of new modules, kept as E1 plus any new labelled cells, never used for selection. A leave-one-source-out table. Twins and near-duplicates kept inside one fold.
- Metrics (Metrics Reloaded fingerprint): crack is headlined by tolerance F1 / clIoU at 2 px and component recall at or above 20 px, with strict IoU secondary. Inactive by IoU plus per-cell detection. All classes by mIoU_rob with a fixed class list. Threshold fixed on dev OOF.
- Reporting: mean +/- SD over seeds and folds, 95% CI (parametric or bootstrap per Andre 2026), worst-source score, bootstrap rank intervals, and a separate leaderboard for "with ensemble/TTA" (Isensee P1, P4).
- Baseline suite at matched compute: house U-Net++ R34, PF, nnU-Net 2D ResEnc, the Hanifi 2025 VGG16-UNet, one transformer / mask-classification model (Mask2Former, as in Hijjawi), one foundation-model fine-tune. Each comes with adaptation instructions (Isensee R2).
- Documentation: a datasheet (Gebru, doi:10.1145/3458723) and a model info sheet (Kapoor). Label-version history and the per-source label-width table from BRIEF section 2 go in the datasheet.

## 6. Notable papers rejected (one line each)

- doi:10.1038/s41592-023-02150-0 Reinke metric pitfalls: covered by Metrics Reloaded (row 4). Keep as a reference for the spec.
- doi:10.1038/s41467-022-30695-9 Medical Segmentation Decathlon: lesson (rank consistency across tasks) is already captured by rows 2, 7, 15; 3D medical, no transferable mechanism.
- doi:10.1109/cvpr52734.2025.01942 nnWNet (CVPR 2025): calls for a unified benchmark inside nnU-Net; architecture belongs to the D23/D22 scouts; code github.com/yanfeng-zhou/nnWNet (from abstract).
- doi:10.1007/978-3-031-25082-8_12 CrackSeg9k: older merged crack set, superseded by OmniCrack30k.
- doi:10.1016/j.autcon.2026.106938 CrackSegFlow 50k crack benchmark with flow-matching synthesis: belongs to the generative data scout (D33).
- doi:10.1016/j.compind.2021.103459 KolektorSDD2 mixed supervision (code github.com/vicoslab/mixed-segdec-net-comind2021): weak labels, covered by D36.
- arXiv:2608.01714 STC-Net: EL crack seg with an inactive-area power-loss proxy. Train mIoU 95.98 vs test 72.52 on PVEL-S. Relevant to severity, not to benchmark design.
- doi:10.3390/math13152430 conformal segmentation for industrial defects: could give a recall-guaranteed operating point for "relR@2 >= 0.90". Close to the val-chosen logit bias already run, so lower priority.
- doi:10.1016/j.ecolmodel.2021.109692 Wadoux, spatial CV critique: argues for probability sampling of the test set. Worth one line in the protocol rationale; no mechanism for us.
- arXiv:2107.07002 Benchmark Lottery and openalex:W2991486856 Roelofs test-reuse meta-analysis: background for the sealed-test argument only.
- doi:10.3390/s26134256 Sahin 2026 EL benchmark: binary classification, not segmentation.
- doi:10.1016/j.engappai.2025.111790 Jha semi-supervised EL (UCF-EL): SSL line, and the split is leaky.
- MedSegBench (Scientific Data 2024, via web only, no tool id): standard 128/256/512 resolutions and fixed splits across 35 sets; useful pattern, not retrieved through the Research MCP.

## 7. Gaps

- search_snippets was rate-limited all session, so evidence questions were not answered from full text (for example how OmniCrack30k defines clIoU4px, or how much nnU-Net 5-fold ensembling gains over a single fold).
- No paper reports a module-grouped vs random split comparison on EL images. That is a gap the benchmark itself can fill: retrain the house model on a random split and on the module split, and report the gap.
- OmniCrack30k repo, licence and download size are unverified.
- Multi-annotator EL crack labels: no public EL set with independent double annotation was found. Whether BenchmarkEL 2021 vs 2022 counts as two "raters" or as a correction needs checking in handbook 03.
- Severity benchmarks (crack mode, inactive fraction, power-loss band) need their own search: STC-Net, Chen 2023 JPV (doi:10.1109/jphotov.2023.3249970), and Pradhan 2026 crack-width tolerance (doi:10.3390/s26185853) are leads.
- VisA and the MVTec AD 1 evaluation critiques were not retrieved separately; MVTec AD 2 covers the sealed-test idea.
