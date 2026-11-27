# D37 Data-centric methods: label error detection, relabelling, selection

Scout: literature agent, 13 Nov 2026 (two sessions; working notes in `D37_notes_wip.md`). Literature phase only: no servers, no test or E1 data read.
Tags: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Scope and split with sibling directions (S)
D15 (noisy-label training), D16 (label refinement / alignment: ADELE, Spatial Correction, Crispness, snakes, SAMRefiner) and D17 (annotator style) already cover how to train through noisy crack labels. D41 covers metrics and statistics. D37 therefore focuses on the data itself:
1. ranking and flagging bad labels in the 478 train cells (and, for the benchmark, the 50 test cells), with no human in the loop;
2. deciding what to do with flagged labels (drop, mask the loss, down-weight, model them as a style);
3. selecting which unlabelled pool cells to pseudo-label (inactive-rich, half-cut, scuff), by learned quality rather than per-pixel thresholds;
4. a minimal-click or tiny-budget route, only for E1, if the user ever accepts it;
5. dataset auditing for the benchmark (test-label errors, leakage between pool, train and test).

Key fact from BRIEF (E): an earlier audit flagged crack label issues in 24 of 239 train cells, nothing was fixed; the 2022 relabelling alone gave +0.05 to +0.08 crack IoU, more than any method. So label quality is the largest lever measured so far, and automatic detection has never been run.

## Queries run (Research MCP search_papers unless marked; Scopus and ScienceDirect always failed, S2 mostly rate-limited, OpenAlex and arXiv answered)
Session 1 (2020+ unless noted):
1. label error detection semantic segmentation
2. confident learning segmentation noisy labels
3. automatic label refinement noisy boundary annotations segmentation
4. thin structure segmentation inaccurate annotations misaligned labels vessel crack
5. misaligned annotations curvilinear structure segmentation
6. noisy crack annotations segmentation label correction
7. active learning semantic segmentation small budget
8. data valuation pruning semantic segmentation training set
9. learning to segment from misaligned and partial labels (2019+)
10. SAM label refinement pseudo label correction thin defects (2023+)
11. adaptive early-learning correction segmentation noisy annotations
12. noisy boundary label alignment edge detection active alignment (2019+)
13. label errors segmentation datasets detection (2025+)
14. crack segmentation noisy labels (2025+)
15. annotator style multi-source annotation convention segmentation
16. spatially varying label smoothing segmentation uncertainty annotation
17. training dynamics identify mislabeled pixels segmentation memorization
18. training set search target domain data selection segmentation domain shift
19. automatic annotation industrial defect segmentation foundation model pseudo labels (2025+)

Session 2:
20. pervasive label errors in test sets benchmark
21. data valuation semantic segmentation influence of training images
22. dataset cartography training dynamics hard noisy samples segmentation
23. coreset data selection pruning dense prediction segmentation training set (2022+)
24. active domain adaptation semantic segmentation region selection (2021+)
25. label errors semantic segmentation detection (2025+)
26. active label correction semantic segmentation (2022+)
27. data leakage near-duplicate images train test split benchmark inflated performance
28. automatic annotation segment anything pseudo masks unlabeled industrial defect (2024+)
29. pixel-wise label quality estimation segmentation annotation quality score
30. active learning crack segmentation annotation efficient
31. evaluating segmentation with noisy ground truth test labels unreliable reference
32. data selection from unlabeled pool target domain similarity self-training segmentation
33. learning to reweight pixels meta-learning noisy segmentation labels (no results)
34. label error detection segmentation (2025+, arXiv and OpenAlex only)
35. mining rare class images from unlabeled pool retrieval long-tail segmentation
36. cold start low budget active learning semantic segmentation foundation model features (2023+)
37. repeat factor sampling rare class oversampling segmentation
38. variance of segmentation benchmark results small test set cross-validation
39. ST++ selective self-training reliable unlabeled images
40. segmentation quality estimation without ground truth per-image Dice prediction

Snowballing: get_citations on Rottmann 2023, Rill-Garcia 2022 and Lad 2023; similar_papers on {A2LC, Lad, Penquitt} and on {Crispness, STEAL, Rill-Garcia}.
Full text read (2 of 3 allowed): HyperSORT (arxiv:2506.21430), Nogueira et al. 2026 (arxiv:2603.00604).
WebSearch: A2LC code; label error detection crack 2026; SAM2 / SAM3 label cleaning for cracks; HyperSORT repo; RIPU repo; cleanlab segmentation docs (session 1).

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1016/j.neucom.2026.134891 (arXiv 2603.00604) Nogueira et al., label-noise ranking | 2026 | Neurocomputing | github.com/keillernogueira/label_noise_segmentation (stated in abstract, not opened) | Rank training images by noise: an augmented ensemble (or cross-validated ensemble with rising L2) predicts each image; noise score = 1 - IoU(pred, given label), optionally weighted by ensemble variance. Train on the least-noisy part. | Use the existing module-grouped 5-fold roots so every train cell gets out-of-fold predictions from a multi-seed ensemble. Score each cell per class: crack noise = 1 - relF1@2 (tolerant, so 1 px jitter does not dominate) plus a missed-component count; inactive noise = 1 - IoU. Do not drop cells (only 209 crack cells, 42 inactive): ignore the crack loss on the worst-ranked cells or components, keep all other classes. Check the ranking against the 24 audit-flagged cells first (free). | 72 | 65 |
| 2 | doi:10.1007/978-3-032-05169-1_27 (arXiv 2506.21430) HyperSORT | 2025 | MICCAI | github.com/ImFusionGmbH/HyperSORT (repo listing seen; needs a free ImFusion SDK licence key) | A hypernetwork maps a learned per-sample latent (2-D, L1-pulled to 0) to U-Net weights. Systematic label styles and errors move to outlying latents; latent 0 gives a model of the majority style. | Replace the full hypernetwork with FiLM on the U-Net++ decoder driven by a learned 2 to 4-D latent per train cell (cheap, no SDK). Inspect whether latents cluster by source (label width ARTS 1.5 px to SDLE 3.25 px) and whether outliers match the 24 audit-flagged cells. Infer with latent 0, or with the per-source centroid (test source is known), a form of the never-tried source-conditional prediction. | 62 | 45 |
| 3 | doi:10.1109/wacv56688.2023.00323 (arXiv 2207.06104) Rottmann and Reese | 2023 | WACV | unverified | Lift uncertainty to predicted connected components; a meta-classifier on component features flags predicted components with no label (missing labels). R: detects most dropped labels on Cityscapes and CARLA while controlling false alarms. | Crack components are small (76 to 88% under 20 px), so features must include size, mean p(crack), ridge contrast along the line, distance to nearest label, source and inactive adjacency. Train the meta-classifier on val cells, apply out-of-fold on train. Target: under-annotated crack segments, which a 1 - IoU score confuses with jitter. Output feeds arm 1 (ignore those pixels, or soft positive). | 58 | 55 |
| 4 | arxiv:2406.00327 Quality Sentinel | 2024 | arXiv | "data and model are released" (abstract); repo not verified | A regressor takes (image, label) and predicts the label's Dice against a correct label; trained on 4M synthetic corruptions. R: r = 0.902 with true quality; training on high-quality pseudo-labels only gave 33 to 88% gains over entropy-based selection. | Train a small quality regressor on our 532 labelled cells with synthetic crack-label corruptions that mimic our noise (1 to 3 px shifts, width 1 to 4 px, dropped and spurious segments, inactive boundary errors), target = relF1@2 and inactive IoU. Use it (a) as a second opinion on train labels, (b) to choose, image by image, which of the 11.9k pool pseudo-labels to train on. | 55 | 35 |
| 5 | arxiv:2307.05080 Lad and Mueller (cleanlab segmentation), with doi:10.1613/jair.1.12125 Confident Learning | 2023 / 2021 | arXiv / JAIR | cleanlab `segmentation.filter.find_label_issues` (cleanlab docs, checked in session 1) | Image label-quality score = soft-minimum of the model's out-of-sample likelihood of each pixel's given class; confident-learning per-class thresholds for pixel issues. R: best of 7 scores on SYNTHIA error detection. | Feed the same out-of-fold softmax maps from arm 1 into cleanlab: zero extra training. Standard baseline beside arm 1. Expect weakness on crack: Nogueira et al. measured cleanlab Kendall tau 0.17 vs 0.61 for ensemble ranking, worst on deletions (R). | 50 | 65 |
| 6 | arxiv:2508.17930 Penquitt et al., learning to detect label errors by making them | 2025 | arXiv | unverified | Inject typed label errors into ground truth, then train an instance-segmentation network on (image, label, prediction) to find error regions. Releases 459 real Cityscapes errors. | Inject the error types the audit saw (dropped crack segments, spurious lines, shifted tracing, crack vs inactive swaps) into train cells, train a small detector on [EL image, given label, OOF prediction], apply to all 532 cells. More work than arms 1 and 3 for the same output. | 45 | 55 |
| 7 | doi:10.1609/aaai.v40i7.37445 (arXiv 2506.11599) A2LC | 2026 | AAAI | github.com/ngbrjyj/A2LC (listed in AAAI version, repo not opened) | Cascaded active plus automatic label correction: a human answers a few correction queries, an automatic stage propagates each correction to similar unqueried regions, with tail-class-balanced acquisition. R: +27.23% over prior ALC at equal budget on Cityscapes; same accuracy with 20% of the budget. | Only if the user accepts a few minutes of yes/no clicks: show the top 100 flagged crack components from arms 1 and 3 as "crack: yes / no", propagate each answer to components with similar features in all cells. A click is far cheaper than drawing. Without clicks it reduces to arm 1. | 40 | 45 |
| 8 | doi:10.1109/cvpr52688.2022.00790 (arXiv 2111.12940) RIPU | 2022 | CVPR | github.com/BIT-DA/RIPU (per search results, not opened) | Active domain adaptation: pick target regions by region impurity (entropy of predicted classes in a neighbourhood) times prediction uncertainty. R: 69.6 mIoU GTAV to Cityscapes with 2.2% of pixels labelled vs 66.6 for LabOR. | E1 is context-limited (0 half-cut train cells, crack IoU 0.15). Without labels: rank the 1,152 pool half-cells by RIPU score and pseudo-label the top ones. If a minimal labelling case is ever made: 20 to 30 RIPU-chosen half-cell regions with scuff and cut-line context. | 38 | 30 |
| 9 | doi:10.1109/wacvw65960.2025.00120 (arXiv 2409.15486) VLMine | 2025 | WACVW | unverified | Find rare examples in an unlabelled corpus by rank-combining several mining signals (VLM keyword rarity, model uncertainty). R: 10 to 50% gains over baselines on ImageNet-LT, Places-LT, Waymo. | General VLMs do not read EL; replace the VLM signal with (a) predicted inactive area fraction from the 5-seed ensemble, (b) ensemble disagreement, (c) embedding novelty vs the train set. Mine the 159k pool for inactive-rich cells and half-cut scuff cells, pseudo-label only those. Targets inactive (42 train cells) and E1. | 40 | 15 |
| 10 | arxiv:2308.01189 Data-Centric Diet | 2023 | arXiv | unverified | Per-sample importance from training dynamics on target regions (Dynamic Average Dice over epochs) for multi-centre pruning; loss-gradient-norm scores failed on segmentation. | Log per-cell crack and inactive Dice at saved checkpoints of existing runs (no new training). Cells whose crack Dice never rises and whose relF1@2 stays low are noise candidates (cross-check with arm 1). Gives per-source dynamics for the 5 sources. | 42 | 25 |
| 11 | arxiv:2608.09101 Contrastive Mask Fidelity | 2026 | arXiv | unverified | Reference-free audit: build "keep" and "erase" counterfactual views of a mask and ask a frozen judge whether class evidence is inside the mask and absent outside; arbitrate between human and candidate masks. R: matches 3-annotator consensus on 81% of pairs; class-wise arbitration improved cross-domain transfer. | Bold bet. The judge must know EL: train an image-level crack classifier (train cells + ELPV image labels), inpaint the masked line with local background, measure the drop in p(crack). A label on the dark ridge gives a large drop; a tracing 1 px beside it a small one. Use it per segment to choose the human line or the model line, mainly for auditing test labels. | 30 | 45 |
| 12 | arxiv:2103.14749 Northcutt et al., pervasive test-set label errors | 2021 | arXiv (NeurIPS D&B track) | cleanlab | Test sets of 10 common benchmarks contain many label errors; on corrected test sets, model rankings change. | Benchmark: run arms 1, 3, 5 on the 50 test and 106 E1 cells (labels only, after models are frozen), count crack and inactive errors, score every method on original and audited labels. Does not raise the model; decides whether a 0.012 IoU difference is real. | 25 | 75 |
| 13 | arxiv:2508.17416 Data Leakage in Visual Datasets | 2025 | ICCVW | unverified | Measures leakage (evaluation images seen in training) in vision datasets by near-duplicate retrieval. | The pool (11.9k on servers, 159k on Dropbox / HF) comes from the same CSIR and ARTS sources as test and E1. Before any pool pretraining or SSL result enters the benchmark, run near-duplicate search (embedding plus pixel correlation) between pool, train, val, test and E1, and across BenchmarkEL releases. Also flags same-module pairs across splits. | 25 | 75 |
| 14 | arxiv:2606.12552 Cross-validation reduces benchmarking variance | 2026 | arXiv | unverified | Cross-validated evaluation cuts the variance of method comparisons strongly compared with a single split. | Supports moving the main comparison to the existing module-grouped 5-fold CV over 532 cells (problem 5), with clean-49 test and E1 as held-out reports. Arm 1's OOF predictions come free from the same runs. | 20 | 65 |
| 15 | arxiv:2607.22697 TTCov, test-conditioned data curation | 2026 | arXiv | unverified | Curate a training subset whose concept distribution matches unlabelled deployment samples. R: driving data with an LLM-built concept atlas. | Bold bet. Replace the concept atlas with simple EL descriptors (half-cut, mono / multi, busbar count, scuff present, contrast) from the pool and from F51 / H36 (not E1, to keep E1 unseen). Select pool cells whose descriptor mix matches the target, pseudo-label, train. Distant evidence. | 28 | 25 |

score = value for our metrics (rubric in the task); bench = value for the benchmark (BRIEF section 1).

### Minimum experiments and prior overlap
1. **Nogueira 2026, ensemble ranking.** R: Augmented Ensemble Ranking Kendall tau 0.61 / Spearman 0.77 vs CleanLab 0.17 / 0.24 and uncertainty 0.13 / 0.14; U-Net trained on the top-ranked 50% got F1 80.34 vs 78.26 on all noisy data (oracle 80.98). Shrink / expand boundary noise was the hardest type for every method. S: our crack noise is mostly that type (jitter, width), so the score must be tolerant (relF1@2) and the arm should target omissions and spurious lines, not width.
   - Arm: house model with crack loss ignored within 3 px of label segments and on predicted-but-unlabelled components, in the worst 10% of cells by OOF crack noise (OOF from 5 folds x 3 seeds). Baseline: house model and PF variant, 5 seeds each. Metric: clean-49 crack relF1@2 and strict IoU, F51 crack AP, 5-fold CV crack IoU. Kill: ranking overlap with the 24 audit cells no better than random, or no gain of 0.01 relF1@2 on CV and 0.012 test crack IoU. About 35 GPU-h.
   - Prior overlap: BRIEF "Labels" row: audit done, nothing fixed; automatic label refinement never run. Open.
2. **HyperSORT.** R: on AMOS with synthetic erosion / dilation styles, latents formed separate clusters; on TotalSegmentator it surfaced systematic biases and erroneous cases.
   - Arm: U-Net++ with FiLM(latent_i) on decoder blocks, 4-D latent per cell, 2 L1 weights, inference at latent 0 and at source centroid. Baseline: house model, 5 seeds. Metric: per-source crack IoU (BMRK, CFVS), clean-49 crack IoU and relF1@2, mIoU_rob. Kill: no source-centroid gain on BMRK / CFVS and no overall gain at latent 0. About 15 GPU-h.
   - Prior overlap: none; source-conditional prediction and annotator modelling are listed as never tried.
3. **Rottmann and Reese.** Arm: gradient-boosting meta-classifier on predicted crack components of OOF maps, trained on val cells against "overlaps a label within 2 px"; flagged high-confidence unlabelled components in train set to ignore (or soft 0.5). Baseline: house, 5 seeds. Metric: crack relR@2, components >= 20 px found, strict IoU. Kill: flagged set below 30% precision on a 30-cell automatic check (ridge darkness) or no relR@2 gain. About 20 GPU-h. Prior overlap: none.
4. **Quality Sentinel.** Arm: quality regressor (ResNet-18, input = image + label) on synthetic corruptions of the 532 labelled cells; pick the top 1,000 pool cells by predicted pseudo-label quality from the 5-seed teacher; train house + these offline pseudo-labels. Baseline: house model, and the earlier pool SSL setting. Metric: E1 crack relF1@2 and inactive IoU, clean-49 crack IoU. Kill: Spearman between predicted and true quality on held-out real val labels below 0.5, or no gain over the earlier pool run. About 25 GPU-h. Prior overlap: BRIEF "Pseudo-label SSL" row ran hard / tolerant per-pixel thresholds at 100% with the pool (n.d.); image-level learned quality selection was not run. Partly open.
5. **cleanlab.** Same OOF maps as arm 1, run `find_label_issues`, compare precision at 24 against the audit cells. No training. Baseline row for the benchmark. Prior overlap: none.
6. **Penquitt.** Inject 5 error types into 300 train cells, train the detector, evaluate on held-out injected errors and on the 24 audit cells. Kill: precision at 24 not better than arm 1. About 10 GPU-h. Prior overlap: none.
7. **A2LC.** Needs user consent for clicks: 100 yes/no crack queries, propagation by feature similarity, retrain. Baseline: arm 1 without clicks. Kill: gain over arm 1 under 0.01 relF1@2. Conflicts with the no-manual-labelling rule; low priority.
8. **RIPU.** No-label version: rank 1,152 pool half-cells by RIPU score, pseudo-label the top 300 with the PF ensemble, train PF + these. Baseline: PF variant. Metric: E1 crack relF1@2, E1 inactive IoU. Kill: E1 gain under 0.02 relF1@2. About 15 GPU-h. Prior overlap: synthetic half-cut views were tried (n.d.); real half-cut pool selection was not.
9. **VLMine-style mining.** Mine 500 inactive-rich pool cells by predicted inactive fraction plus disagreement, pseudo-label, train house + these. Metric: CV and clean-49 inactive IoU, BMRK inactive, E1 inactive. Kill: inactive IoU gain under 0.02 on CV folds. About 15 GPU-h. Prior overlap: pool SSL used the pool without targeted mining. Partly open.
10. **Data-Centric Diet.** Recompute per-cell Dice dynamics from saved checkpoints of existing house runs, correlate with arm 1 and the audit cells. Kill: weaker agreement with audit flags than arm 1. Near-zero GPU.
11. **CMF-style judge.** Crack classifier plus inpainting judge; score human vs model line per segment on 100 train cells. Kill: judge prefers the darkest-ridge line in under 70% of synthetic 1 to 2 px shifts. About 5 GPU-h.
12 to 14. Benchmark rows, no training of their own.
15. **TTCov.** Descriptor-matched 1,000 pool cells vs random 1,000, same teacher. Kill: no E1 gain vs random. About 15 GPU-h.

## Notable papers rejected
- arxiv:2403.10820 Active Label Correction with foundation models (Kim et al.): superseded by A2LC; needs human queries; Grounded-SAM pseudo-labels do not fit 1 to 2 px EL cracks.
- arxiv:2308.00883 SAM pseudo-label correction (medical): starts from SAM masks; SAM2 probes showed no signal on our cracks (BRIEF section 5); Quality Sentinel covers the selection idea.
- arxiv:2410.09409 Distribution-aware noisy-label crack segmentation (SAM-Adapter + GMM): a training method, belongs to D15.
- doi:10.1109/tai.2024.3365093 CTRL loss-curve clustering: classification only; Data-Centric Diet is the segmentation form of the same signal.
- arxiv:2510.22229 Diffusion two-stage low-budget AL (NeurIPS 2025, code github.com/jn-kim/two-stage-edald per abstract): needs human pixel labels; RIPU fits the E1 shift better.
- doi:10.1007/s11263-025-02372-z Mittal et al., realistic AL evaluation: AL gains shrink against strong SSL baselines and we have no labelling budget.
- arxiv:2502.07547 Instance-dependent early stopping: compute saving, not accuracy.
- arxiv:2503.00828 training-free dataset pruning for instance segmentation: pruning a 478-cell set is the wrong direction.
- arxiv:2607.11214 ARLA (adaptive-resolution evaluation on noisy labels): metric design, D41 territory; keep for the benchmark.
- doi:10.1016/j.media.2024.103392 Zenk et al., failure detection benchmarking: post-evaluation / deployment, not score.
- arxiv:2604.12832 VOG detection and refurbishment (echo): U-Net robust up to 50% systematic errors; weaker evidence than arm 1.
- arxiv:2406.20081 UnSAM: unsupervised whole-image masks; no thin-line evidence.
- arxiv:2305.08069 instance-aware repeat factor sampling: D19 already covers rare-class sampling.

## Gaps
- No paper found on label error detection for 1 to 2 px curvilinear labels; all detectors were validated on blob-like objects. Tolerant scoring (relF1@2) and separate omission / commission flags are our own adaptation; check against the 24 audit cells first.
- No evidence found that cleaning training labels raises strict IoU when test labels are equally noisy. The benchmark should report against original and audited test labels (rows 11, 12).
- Leakage between the 159k pool and the test / E1 cells has not been checked anywhere in the project; any pool-based gain is unverified until it is (row 13).
- S2 full-text snippets were rate-limited all session, so evidence numbers come from abstracts and 2 full texts only.
- Sub-direction worth its own search: EL-aware reference-free label judges (inpainting or counterfactual evidence for thin lines).
