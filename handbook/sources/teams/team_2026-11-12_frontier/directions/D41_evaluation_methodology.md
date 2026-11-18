# D41: Evaluation with small, noisy test sets and thin structures

Scout: D41 literature agent, 13 Nov 2026. Notes trail: `D41_notes_wip.md`.
Legend: (R) = what the paper measured, (E) = what our files measured (BRIEF), (S) = my judgement.

## Bottom line

- (E) Our current instrument: 50 test cells (49 clean), 5 v 5 seeds. Smallest detectable crack IoU change is about 0.012. Inactive is decided by 3 cells. A 1 px shift of a perfect mask scores crack IoU 0.56.
- (R) Eve, Varoquaux and Moreau (arXiv 2606.12552, 2026) show that repeated cross-validation over the available samples acts like a 5x to 15x larger test set for benchmarking variance, and that gains keep growing past K = 5 splits. This is the single most useful paper for problem 5. We already have module-grouped 5-fold roots over 532 train + val cells.
- (R) Christodoulou et al. (MICCAI 2024): the median 95% CI width in MICCAI 2023 segmentation papers was 0.03 Dice, three times the median gap between first and second place. Same order as our 0.012 to 0.02 target effects, so single-split claims in EL papers are almost certainly within noise.
- (S) Recommended instrument for the remaining month: (1) module-grouped repeated CV (K = 10 splits, 2 groupings x 5 folds) on 532 cells as the primary decision tool, paired by split and seed; (2) the 49-cell test and E1 kept as untouched confirmations, reported with hierarchical (module-level) bootstrap CIs; (3) crack scored by a tolerance metric (NSD or relF1 at tau = 2 px, tau set from the measured 2 px annotator agreement) plus strict IoU; (4) inactive and thin classes also aggregated per image (fine-grained mIoU and worst-case) so 3 cells cannot decide the result.
- (S) None of these papers raises the model directly. Their score value is through better decisions (fewer false nulls and false wins) and less noisy validation-based choices (logit bias, checkpoint, ensemble weights chosen on 532 out-of-fold cells instead of 54 val cells).

## Queries run (38 calls)

Research MCP `search_papers` (year_from 2020 unless noted; Scopus, ScienceDirect returned 401, Semantic Scholar was rate-limited for most of the session, so most hits came via OpenAlex and arXiv):
1. Metrics Reloaded
2. evaluation thin structure segmentation tolerance
3. statistical significance segmentation comparison small test set
4. boundary IoU thin structure
5. confidence intervals segmentation benchmarks
6. variance seeds benchmark
7. confidence intervals segmentation performance small test set
8. tolerance-based evaluation thin curvilinear structure segmentation metric
9. normalized surface Dice tolerance segmentation evaluation (no year bound)
10. accounting for variance machine learning benchmarks seeds statistical comparison
11. cross-validation what does it estimate confidence intervals nested
12. inter-rater variability aware evaluation segmentation metric multiple annotations
13. crack segmentation evaluation metric tolerance boundary pixel offset annotation
14. pervasive label errors test sets destabilize benchmarks
15. revisiting evaluation metrics semantic segmentation fine-grained IoU (2022+)
16. Betti matching topological metric segmentation evaluation (2021+)
17. segmentation evaluation metrics label uncertainty annotation noise benchmark (2025+)
18. statistical testing model comparison medical image segmentation paired seeds (2024+)
19. challengeR ranking uncertainty bootstrap
20. hierarchical bootstrap clustered multi-level data
21. overfitting validation set model selection noise small validation
22. noisy ground truth test labels bias segmentation performance estimate
23. boundary IoU segmentation evaluation measure
24. corrected resampled t-test repeated cross-validation
25. pavement crack detection evaluation ODS OIS tolerance
26. how many random seeds statistical power analysis
27. clinically applicable segmentation surface Dice (Nikolov)
28. evaluating segmentation against soft / probabilistic reference labels
29. leakage reproducibility crisis ML-based science (2022+)
30. panoptica instance-wise evaluation (2023+)
31. segmentation benchmark ranking robustness test set size significance (2025+)
32. road extraction completeness correctness buffer (relaxed P/R)

Snowballing: `get_citations` on El Jurdi ISBI 2023; `similar_papers` on El Jurdi MedIA 2025 + Bouthillier 2021 (this found Eve et al. 2026 and Christodoulou 2024). `search_snippets` tried 4 times, rate-limited each time. `fetch_fulltext` once (arXiv 2606.12552, sections 4 and 5 read).
WebSearch: thin-structure tolerance metrics 2025; MetricsReloaded repo; boundary-iou-api repo; surface-distance repo; challengeR repo.

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2606.12552 (Eve, Varoquaux, Moreau) | 2026 | arXiv | Benchopt used; paper code unverified | Repeated CV splits reduce benchmarking variance far more than expected ("sample gain" 5 to 15x at K = 20); early-stop CV from a redundancy score after 2 to 3 splits | Module-grouped repeated CV over the 532 train + val cells (existing fold roots), 2 groupings x 5 folds; paired deltas per split and seed; keep test-49 and E1 as untouched confirmation | 72 | 92 |
| 2 | arxiv:2103.03098 (Bouthillier et al.) | 2021 | arXiv (MLSys 2021 per memory, unverified) | no | Randomise all variance sources (data split, init, data order, augmentation) in each run; this estimator is closer to the ideal one at far lower cost; report P(A > B) with a CI | Each run draws a new grouped fold split and seed; compare arms by P(A > B) over paired runs, not mean of 5 seeds on one split | 55 | 85 |
| 3 | arxiv:1806.08295 (Colas et al.) | 2018 | arXiv | yes, in paper (unverified) | Power analysis to choose the number of seeds for a target effect size; Welch t-test and bootstrap CI | Use our 5-seed SDs to compute seeds needed to detect 0.01 crack IoU or 0.02 inactive IoU at power 0.8, per instrument (test-49 vs CV) | 45 | 60 |
| 4 | doi:10.1016/j.media.2025.103565 (El Jurdi, Varoquaux, Colliot), with ISBI 2023 doi:10.1109/isbi53787.2023.10230401 | 2025 | MedIA | no | CI width of mean Dice vs test size and spread; parametric vs bootstrap CIs. (R) about 8 Dice points CI width for 20 test cases at SD 0.10 | Per-cell crack IoU on 49 cells has a large SD (many tiny cracks); report bootstrap CIs and show readers the CI width at n = 49 and n = 532 OOF | 40 | 80 |
| 5 | doi:10.1016/j.media.2026.104349 (André et al.; arXiv 2601.17103) | 2027 | MedIA | no | Large-scale CI study, 24 tasks, 19 models each: sample size for reliable CI ranges from dozens to thousands; macro aggregation needs more cases than micro; CI method matters; decision tree | Choose CI method and aggregation (dataset-level pooled IoU vs per-cell mean) per metric using their decision tree; flag inactive (16 test cells) as below their reliable-coverage range | 40 | 85 |
| 6 | doi:10.1007/978-3-031-72117-5_12 (Christodoulou et al.; arXiv 2409.17763) | 2024 | MICCAI | no | SD of Dice approximated by a quadratic in mean Dice; reconstructs CIs for papers that report none. (R) median CI 0.03, 60% of second-ranked methods inside first-ranked CI | Reconstruct approximate CIs for published EL segmentation numbers (Pratt, Fioresi, E-SCDD) in the benchmark's related-work table to show which claimed gains are inside noise | 25 | 75 |
| 7 | doi:10.1038/s41592-023-02151-z (Metrics Reloaded) and doi:10.1038/s41592-023-02150-0 (pitfalls) | 2024 | Nature Methods | github.com/Project-MONAI/MetricsReloaded (verified; a fork says unmaintained since 2023) | Problem fingerprint drives metric choice (target size, structure shape, reference noise, class imbalance); catalogue of metric pitfalls | Write an EL fingerprint: crack = thin, tiny, noisy reference; inactive = blob, rare, few cells; 24 classes with many empty-in-test. Map to metric set: overlap + boundary/tolerance + per-component detection. Use as the benchmark's justification text | 35 | 92 |
| 8 | doi:10.2196/26151 (Nikolov et al., normalized surface Dice; arXiv 1809.04430) | 2021 | JMIR | github.com/google-deepmind/surface-distance (verified) | Surface Dice at tolerance tau, tau set from inter-observer variation | Set tau = 2 px from our measured 2 px annotator agreement (0.82 to 0.99 within 2 px). Report NSD@1, @2 for crack, @2 for inactive and thin structural classes (gridline, busbar, ribbon edges) | 50 | 88 |
| 9 | arxiv:2310.19252 (Wang, Berman, ..., Blaschko) | 2023 | arXiv (NeurIPS 2023 per memory, unverified) | github.com/zifuwanggg/JDTLosses (stated in abstract) | Fine-grained mIoU (per image, per class per image) plus worst-case (lowest k%) variants; less bias to large objects; benchmark of 15 models on 12 datasets | Report per-cell crack and inactive IoU means and worst-10% alongside dataset-level IoU; stops 3 cells (59% of inactive pixels) from deciding inactive; worst-case matches the "almost all cracks" goal | 55 | 85 |
| 10 | arxiv:2007.07797 (Saravanan, Berman, Sober) | 2020 | bioRxiv / arXiv | yes, in paper (unverified) | Hierarchical bootstrap: resample top level (subjects) then lower level (trials) for correct CIs on nested data | Resample modules then cells; essential for E1 (106 cells from 67 modules) and for the CV pool (cells from the same module are correlated) | 40 | 75 |
| 11 | doi:10.1080/01621459.2023.2197686 (Bates, Hastie, Tibshirani; arXiv 2104.00673) | 2023 | JASA | nestedcv R package (unverified) | Naive CV CIs under-cover because fold errors are correlated; nested CV gives a variance estimate with near-nominal coverage | Use their result to inflate naive CV standard errors on our grouped-CV deltas; full nested CV is too costly for deep nets, so use it only as a correction factor estimated once | 30 | 65 |
| 12 | arxiv:2103.14749 (Northcutt, Athalye, Mueller) | 2021 | arXiv (NeurIPS 2021 D&B per memory, unverified) | cleanlab (unverified for this paper) | Test-set label errors are common and can flip model rankings, especially for higher-capacity models | Flag test/val cells whose crack or inactive labels disagree strongly with the 5-fold OOF ensemble (already one known case: CSIR_00070_r8_c4). Report ranks with and without flagged cells; no relabelling | 45 | 75 |
| 13 | doi:10.1016/j.neucom.2022.01.051 (Rill-García, Dokládalová; Syncrack) | 2022 | Neurocomputing | unverified | Synthetic crack set with exact ground truth plus controlled inaccurate annotations; (R) inaccurate labels cut F-measure by up to 20%; label correction recovers up to 12% | Build an EL synthetic crack test bed (pasted synthetic cracks with exact GT) and re-annotate it by simulating each source's convention (width 1.5 to 3.25 px, 1 to 2 px offset). Measure which metric ranks models by true accuracy | 40 | 70 |
| 14 | arxiv:2509.05670 (MeshMetrics) and arxiv:2410.02630 (Podobnik, Vrtovec) | 2025 | arXiv | github.com/gasperpodobnik/MeshMetrics (stated in abstract) | Distance-metric implementations differ by up to 30 pct-points in NSD on identical masks; mesh-based computation is more exact | Fix one reference implementation for relF1@2 / NSD in the benchmark; check our in-house relF1 against surface-distance and MeshMetrics on 2D contours | 15 | 70 |
| 15 | arxiv:2103.16562 (Boundary IoU) | 2021 | CVPR | github.com/bowenc0221/boundary-iou-api (verified) | IoU restricted to a band of width d around both contours; more sensitive to boundary error on large objects | Useful for inactive and large structural classes. (S) For 1 to 2 px cracks, Boundary IoU at d >= 2 equals mask IoU, so it adds nothing for crack | 25 | 65 |
| 16 | doi:10.1038/s41598-021-82017-6 (Wiesenfarth et al., challengeR) | 2021 | Sci Rep | github.com/wiesenfa/challengeR (verified via mirrors; R package) | Bootstrap ranking stability, Kendall tau, significance maps for multi-method benchmarks | Rank the benchmark's method suite per metric with bootstrap over cells (and over modules for E1); publish ranking-stability plots | 15 | 80 |
| 17 | arxiv:2607.08203 (Urooj et al., polyp audit) | 2026 | arXiv | no | Audit of 27 polyp papers: 5 incompatible split protocols on the same data, 26 of 27 without significance tests; rankings reverse across random splits; reporting checklist | Same audit for EL papers (D01 to D03 lists): split, release, class list, metric, tolerance, test size. Directly supports the "unorganised field" claim | 15 | 85 |
| 18 | arxiv:2603.00163 (Korcynski, whiteboard strokes) | 2026 | arXiv | no | Protocol: region + boundary metrics, thin-subset equity analysis, per-image median, IQR and worst case, seeded multi-run with non-parametric tests | Thin subset = crack components < 20 px (76 to 88% of components); report each metric on thin vs long cracks and per source | 20 | 60 |

## Minimum experiments (one per paper, cheapest decisive)

All arms use the house model or PF variant. No test data is touched until a ranking decision is frozen. GPU-h are rough on an RTX A6000 (1.1 GPU-h per house run).

1. **Grouped repeated CV (Eve 2026).** Arm: house and PF trained on 10 grouped splits (2 groupings x 5 folds over 532 cells), 1 seed each, paired per split. Baseline: current 5 v 5 seeds on test-49. Metric: SE of the paired delta in pooled out-of-fold crack IoU, and the resulting minimum detectable effect (MDE, 2.8 x SE). Kill: if CV MDE is not <= 0.008 (vs about 0.012 now), CV is not worth the 10x compute as the main instrument. About 22 GPU-h.
2. **All-source randomisation (Bouthillier).** Arm: 10 runs per method each with a new split and seed. Baseline: 10 runs with seed-only variation on a fixed split. Metric: share of delta variance from data split vs seed. Kill: if split variance is < 25% of seed variance, seed-only protocols stay. Shares runs with experiment 1; about 11 extra GPU-h.
3. **Seeds needed (Colas).** Arm: power calculation on existing 5-seed numbers (val and OOF only). Baseline: none. Metric: seeds needed for 0.01 crack IoU and 0.02 inactive IoU at power 0.8. Kill: if more than 20 seeds are needed on test-49, stop using test-49 for decisions under 0.02. 0 GPU-h.
4. **CI width (El Jurdi).** Arm: bootstrap CI of per-cell crack IoU on 54 val cells and on 532 OOF cells. Metric: CI width. Kill: none (reporting); decides how CIs are shown. 0 GPU-h.
5. **Aggregation choice (André).** Arm: dataset-level pooled IoU vs per-cell mean IoU for crack and inactive on OOF predictions of house vs PF. Metric: paired-delta t statistic. Kill: keep the aggregation with the higher t as primary; if they differ by < 10%, keep pooled. 0 GPU-h beyond experiment 1.
6. **Reconstructed CIs (Christodoulou).** Arm: apply their SD-from-mean-Dice fit to published EL tables. Metric: share of claimed gains inside the reconstructed CI. Kill: none (reporting). 0 GPU-h.
7. **Fingerprint (Metrics Reloaded).** Arm: fill the online fingerprint for crack, inactive, structural classes. Kill: adopt only metrics it selects that we do not already report. 0 GPU-h.
8. **NSD tau (Nikolov).** Arm: NSD@1, @2, @3 px for crack on OOF predictions. Baseline: strict crack IoU. Metric: paired t statistic for a known real effect (5-seed ensemble vs single model, +0.014 to +0.018 strict IoU). Kill: if NSD@2 does not give a higher t than strict IoU, it is a reporting metric only, not a decision metric. 0 GPU-h beyond existing predictions.
9. **Fine-grained IoU (Wang 2023).** Arm: per-cell mean and worst-10% IoU for crack and inactive. Baseline: dataset-level IoU. Metric: paired-delta SE for house vs PF on OOF. Kill: if neither cuts the SE / |delta| ratio by >= 20%, keep dataset-level as primary and report the others. 0 GPU-h.
10. **Hierarchical bootstrap (Saravanan).** Arm: module-then-cell bootstrap on E1 and on OOF. Baseline: cell-level bootstrap. Metric: CI width. Kill: if module-level CI is < 10% wider, cell-level is fine. 0 GPU-h.
11. **Nested CV correction (Bates).** Arm: compare naive CV SE with the empirical spread of deltas across the 2 groupings from experiment 1. Kill: if the ratio is < 1.2, no correction. 0 GPU-h.
12. **Test label audit (Northcutt).** Arm: flag val and test cells where the 5-fold OOF ensemble disagrees with labels at high confidence (rank by crack and inactive disagreement area). Baseline: clean-49. Metric: rank change of house vs PF vs ensemble with flagged cells removed. Kill: if no rank flip and |delta change| < 0.005, test label noise does not affect rankings. 0 GPU-h (needs test predictions, so only in the evaluation phase).
13. **Synthetic EL truth (Syncrack idea).** Arm: 300 synthetic-crack cells with exact GT and source-style jittered labels; score 3 existing models. Metric: Kendall tau between ranking under exact GT and under jittered labels, for strict IoU, NSD@2, relF1@2. Kill: if strict IoU ranking matches exact-GT ranking as well as NSD@2 does (tau within 0.1), tolerance metrics are not needed for ranking. About 2 GPU-h for inference plus synthesis work (reuse D06 / D33 generators).
14. **Implementation check (MeshMetrics).** Arm: relF1@2 and NSD@2 from our code, surface-distance and MeshMetrics on 54 val cells. Kill: if differences < 0.005, implementation is not an issue. 0 GPU-h.
15. **Boundary IoU.** Arm: Boundary IoU d = 3 px for inactive, gridline, busbar. Kill: if it never changes a ranking vs mask IoU on OOF, drop it. 0 GPU-h.
16. **Ranking stability (challengeR).** Arm: bootstrap ranks of the method suite. Kill: none (reporting). 0 GPU-h; R needs installing, so only after the literature phase and with the user's OK.
17. **EL audit (Urooj).** Arm: table of EL papers by split, release, class list, metric, tolerance, test size, significance test. Kill: none. 0 GPU-h.
18. **Thin subset (Korcynski).** Arm: metrics on crack components < 20 px vs >= 20 px, per source. Kill: if the ranking is the same in both subsets for all arms, report the overall metric only. 0 GPU-h.

## Rejected (notable)

- Kapoor and Narayanan, leakage taxonomy (doi:10.1016/j.patter.2023.100804): correct but generic; the EL-specific leakage (UCF-EL train/test, BenchmarkEL releases) is already known; covered by the Urooj-style audit.
- Topological metrics, Betti matching (arxiv:2211.15272), clDice (doi:10.1109/cvpr46437.2021.01629) as metrics: crack components are short (76 to 88% under 20 px), so Betti numbers mostly count fragments; clDice as a metric on 1 to 2 px labels is near the label noise. Low value for a metric, but clDice may be included as a secondary benchmark metric because the field uses it.
- Panoptica (arxiv:2312.02608): instance-wise 3D medical toolkit; our component-level detection is already computed; nothing new for 2D.
- Weighted IoU (doi:10.1016/j.patrec.2024.07.011): boundary-weighted IoU; does not handle label offset better than NSD.
- PySODMetrics decomposition framework (arxiv:2607.00886): useful taxonomy for binary metrics; no evidence on thin or noisy labels.
- Conformal segmentation for industrial defects (doi:10.3390/math13152430): risk control at deployment, not a comparison instrument; belongs to deployment, not D41.
- TwinTrack (arxiv:2604.15950) and other multi-rater calibration work: needs multiple annotations per image; we have two annotations only for a few cells.
- Górriz "Is K-fold CV the best?" (doi:10.1016/j.inffus.2026.104404): small-sample neuroimaging classification; Eve 2026 is the more direct evidence.
- Schulz-Kümpel CI generalization error benchmark (arxiv:2409.18836): tabular, cheap learners; methods need hundreds of refits.
- Benchmark Lottery (arxiv:2107.07002): position paper; cite in the thesis, no experiment.

## Gaps

- No paper found that measures metric reliability on 1 to 2 px structures with known label jitter. The synthetic-EL experiment (13) would be a contribution in itself.
- `search_snippets` was rate-limited all session, so specific recommendation text inside Metrics Reloaded (for example which metrics it recommends for tubular structures) is not verified by snippet; the mapping in row 7 is my judgement.
- No 2025 or 2026 work found on statistical comparison specific to segmentation with seed plus split variance; Bouthillier 2021 and Eve 2026 are the closest.
- Deserves its own search: "learning curves / data scaling for benchmark design" (how many labelled cells a benchmark needs), and "severity metric validation" (agreement metrics for inactive area fraction vs power loss), which D41 did not cover.
- Code for Eve 2026, Colas, Saravanan, Bates (nestedcv) not verified on GitHub.
