# T10 family cards: inactive and the weak classes (long-tail, multi-label / structured outputs, refinement, label-error detection)

Analyst T10, 13 Nov 2026. Tags: R = from the paper (read through the Research MCP), E = from our files, S = my judgement.
Full text read (method and results/ablations): P027, P453, P045, P015, P196, P090 (6). Abstract or scout record only for the rest. Repositories were not opened by me: every code line below says whether the URL came from the paper text (R) or from the scout record (unverified).
Spec: `cards/T10_rare_classes_spec.md`. Ledger: `cards/ledger/T10.tsv` (all 79 papers).

## 0. What our files say about the two problems (E, used by every card)

| Fact | Value | Source |
|---|---|---|
| Inactive in P532 (train + val) | 48 cells, 34 module groups, effective n 13.2 (px-weighted groups); per fold 10 / 8 / 7 / 15 / 8 cells | PROTOCOL 3.2 |
| Inactive IoU contrast on CV5-G at 2 seeds | SE 0.038 to 0.039 (groups 0.031, seeds 0.022): about 0.11 needed for 80% power | PROTOCOL 3.2, 5.4 |
| Inactive px share (P532) | 0.204% of px (285,020 px); crack 0.222% (309,040 px, 229 cells) | `benchmark/out/classpx.npy`, my count |
| Weak R13 classes, P532 cells with GT / px share | gridline 359 cells / 0.612%; material 116 / 0.547%; edge_dark 43 / 0.502%; splice 60 / 0.045% | same |
| Test IoU (house, clean 49) | inactive 0.449 (R 0.61, P 0.63), gridline 0.283 (R 0.33, P 0.68), splice 0.000, edge_dark 0.306, material 0.411 | BRIEF 3, handbook 18 M0 |
| Crack / inactive co-occurrence | inactive never without crack; 99% of inactive regions touch a crack label; 20% of train crack px lie in or at inactive | BRIEF 2, PROTOCOL 4.4 |
| Scoring convention at the overlap | single-label masks scored as they are; a multi-label model is converted by "crack over inactive" | PROTOCOL 4.4 |
| Dice on gridline already run | R2c (Dice on crack, inactive, gridline, w 1.5): gridline 0.283 -> 0.357 (R 0.326 -> 0.491, P 0.680 -> 0.568), mIoU_rob +0.0051 [-0.0043, +0.0172], n.d. R2 (Dice on 12 classes, w 6): gridline 0.381, crack worse, clip-driven | handbook 18 M2 |
| Label audit already run (detection only) | B1: five 50%-label models on 239 train cells; inactive FL 9 cells, 13,725 px, 19 components; crack FL 15 cells, ML 10 cells; nothing fixed | handbook 19 §8.1 |
| Dumps available | PF v1.1 OOF dumps for all 532 cells, 2 seeds, keys `pred`, `oth`, `m_crack`, `p_crack`, `p_inact`, `logp` (24 x 512 x 512 float16) | LEAD_INSTRUCTIONS 13 Nov update; task text |

---

## Cards: papers I build arms on (RUN_NOW and RUN_AFTER_GATE)

### P015 Chan, Rottmann, Hüger, Schlicht, Gottschalk: Application of Decision Rules for Handling Class Imbalance in Semantic Segmentation
- **Id / links:** arXiv 1901.08394 (https://arxiv.org/abs/1901.08394). Full text read (sections 3, 4.2).
- **Claim (R):** replacing the Bayes rule (argmax of the posterior) by the maximum-likelihood rule (posterior divided by a per-pixel class prior, priors smoothed with a Gaussian sigma 80 and floored at 1e-5) on a 20k-frame street-scene set: rare-class (person, info sign) instance recall up by about 23%, instance precision down by about 25%, and **mIoU more than 5% lower than Bayes** (Table 1). Bayes segments of rare classes lie inside the ML segments; ML produces more connected components than ground truth, Bayes fewer.
- **Evidence check (S):** the paper itself shows that a full prior correction trades IoU for recall. So for an IoU-scored benchmark the correction must be fitted (a per-class bias chosen to maximise IoU), not set to the prior. This is the main design point of arm `classbias_xfit`.
- **Code:** none in the paper; the rule is 3 lines. Nothing to verify.
- **Hypothesis for our data (S):** gridline (recall 0.33, precision 0.68) and splice (never predicted) are under-called by argmax; a cross-fitted per-class bias on the out-of-fold log-probabilities raises their IoU without retraining. Position priors are not used (cells are rotated by the label-safe augmentation, so position is weak evidence; edge classes already sit at the border).
- **Status:** RUN_NOW, arm `classbias_xfit` (CPU only).

### P045 Menon, Jayasumana, Rawat, Jain, Veit, Kumar: Long-tail learning via logit adjustment (ICLR 2021)
- **Id / links:** arXiv 2007.07314. Full text read (4.1, 5.1, 5.3, 6.2).
- **Claim (R):** post-hoc adjustment `argmax f_y(x) - tau log pi_y` and the logit-adjusted loss `CE(f(x) + tau log pi)` are both Fisher-consistent for the balanced error. ImageNet-LT ResNet-50 balanced error: ERM 53.11, post-hoc (tau = 1) 49.66, post-hoc (tau*) 49.56, loss (tau = 1) 48.89. iNaturalist: 38.66, 33.98, 33.80, 33.64. The loss version is only slightly better than post-hoc; the authors state that combining the loss with a post-hoc adjustment is "not statistically coherent" and "expected to be harmful" (5.3).
- **Evidence check (S):** the target is balanced error (mean per-class recall), not IoU; a crack prior of 0.0022 gives an offset of about 5.7 nats at tau 1, far beyond the crack bias the project ever used (+0.75). The post-hoc result says most of the gain is available without retraining, which is what we can test for free.
- **Code:** none needed for the post-hoc rule; training-time version is one line.
- **Hypothesis (S):** the same as P015, with the bias fitted rather than set to tau log pi. The training-time version (`la_ce`) is gated on the post-hoc result, with its offsets taken from the fitted biases (offset_c = -b_c), not from the priors.
- **Status:** RUN_NOW (post-hoc part inside `classbias_xfit`); training-time `la_ce` gated (see P152).

### P152 Generalised Balanced Softmax (Pattern Recognition 2026)
- **Id:** doi:10.1016/j.patcog.2026.114961. Scout record and abstract only.
- **Claim (R, abstract via scout):** beta = 1 in `z + beta log N_c` is not the best on most long-tailed benchmarks; beta is a finite-data hyperparameter.
- **Evidence check (S):** consistent with P015 and P045: the strength of the correction must be tuned. Our `classbias_xfit` fits one value per class, which subsumes a single beta.
- **Code:** none found (scout). Not needed.
- **Status:** RUN_AFTER_GATE, follow-up `la_ce` of arm `classbias_xfit`; gate = `classbias_xfit` passes its screen rule.

### P196 Lad, Mueller: Estimating label quality and errors in semantic segmentation data via any model (2023)
- **Id / links:** arXiv 2307.05080. Full text read (3, 4.1, 4.3, 5, 6).
- **Claim (R):** per-pixel self-confidence s_ij = p(given label); image score = softmin over pixels with temperature 0.1. On SYNTHIA with three injected error types (drop 20% of images, swap 30%, shift 20%), softmin AUROC 0.951 / 0.947 (drop), 0.998 (swap), 0.863 / 0.828 (shift) for DeepLabV3+ / FPN; best or second of 7 scores. Shift errors are hardest (AUPRC 0.46 to 0.55). Component-level scoring (CoCo) is better for shift with FPN only. They score held-out images and note cross-validation would give scores for every image.
- **Evidence check (S):** synthetic errors only; shift is the error type closest to our crack jitter and it is the one detected worst. For inactive (blobby, well labelled) and for gridline / material / edge_dark (region classes), drop and swap are the relevant types.
- **Code:** the scout found none; the method is 10 lines on our dumps (I do not rely on the cleanlab package, unverified).
- **Hypothesis (S):** on out-of-fold `logp`, a per-component score (mean p of the annotated class over the GT component) and an "unlabelled confident component" score flag inactive and weak-class label errors. This gives the benchmark a label-quality list and gates a later ignore arm. Crack is excluded: T3 `oof_selective_ignore` owns crack label flags.
- **Status:** RUN_NOW inside `ci_error_atlas` (CPU).

### P009 Data-centric benchmark for label noise estimation and ranking (Neurocomputing 2026)
- **Id:** doi:10.1016/j.neucom.2026.134891. Scout record only (publisher full text not fetched).
- **Claim (R, scout):** a cross-validated or augmented ensemble score 1 - IoU(pred, label) ranks noisy building labels with Kendall tau 0.61 vs 0.17 for cleanlab; training on the top-ranked 50% F1 80.34 vs 78.26 on all (oracle 80.98). Boundary shrink / expand noise is hardest.
- **Evidence check (S):** remote sensing, binary. The main lesson for us: ensemble disagreement over out-of-fold models is a better ranker than single-model confidence. We have 2 seeds now and 5 on cv02.
- **Code:** none found (scout).
- **Status:** RUN_NOW inside `ci_error_atlas` (per-cell 1 - IoU for inactive and the weak classes, seed-mean and seed-min).

### P252 Gupta et al.: Learning Topological Interactions for Multi-Class Medical Image Segmentation (ECCV 2022)
- **Id / links:** arXiv 2207.09654. Abstract only (scout); code https://github.com/TopoXLab/TopoInteraction (scout, unverified).
- **Claim (R, abstract):** a convolutional module finds pixels that violate containment or exclusion rules between classes and adds loss on them; validated on 2D and 3D CT and ultrasound. No numbers on the abstract page.
- **Evidence check (S):** the rule we need ("inactive must touch crack") is an adjacency rule, not containment or exclusion, so the paper's module does not encode it as is. The cheapest test of whether the rule carries information is to apply it at inference on the dumps; the training-time loss is only worth building if that test shows the rule removes real false alarms.
- **Hypothesis (S):** inactive precision 0.63: part of the false inactive area sits in components with no predicted crack nearby; deleting them raises precision. Filling the area enclosed by predicted crack + inactive raises recall where the region was found in part.
- **Status:** RUN_NOW as the post-hoc arm `ci_rules_posthoc`; the training-loss version stays parked behind it.

### P027 Isensee, Jäger, Full, Vollmuth, Maier-Hein: nnU-Net for Brain Tumor Segmentation (BraTS 2020)
- **Id / links:** arXiv 2011.00848. Full text read (2.3, 2.4, 3.1, 3.2). Code: nnU-Net (MIC-DKFZ); region training is a configuration of nnU-Net, URL not opened (unverified).
- **Claim (R):** region-based training (sigmoid per overlapping region, BCE + Dice per region, regions = evaluation regions) on 369 cases, 5-fold CV: mean Dice 86.09 (BL*, batch 5) -> 86.73 (BL* + R); whole tumour 91.85 -> 91.75, core 86.24 -> 87.24, enhancing 80.18 -> 82.21. Validation set (125 cases) 83.76 -> 84.13. Single configuration change, 5 folds, no seeds reported.
- **Evidence check (S):** the gain is on the nested inner regions (+1.0, +2.0 Dice) and the outer region is flat; the comparison is one run per fold, so the +0.64 mean is within what seed noise could give. It is the best available evidence that letting overlapping regions be learned as regions helps the inner, rarer one.
- **Hypothesis (S):** our softmax inactive target has "holes" where a crack line crosses or bounds the region, and the crack labels there are jittered by 1 to 2 px. A sigmoid "inactive region" channel trained on the filled region (inactive + the crack px in or at it) learns the region as one blob; the decision then writes inactive where the region channel fires and crack did not win. Expected effect on inactive IoU: 0 to +0.04 (S), which a 2-seed CV screen cannot detect (needs about 0.08 to 0.11).
- **Status:** RUN_AFTER_GATE, arm `layered_ci`; gate = `ci_error_atlas` part (a) (overlap and crack-adjacent errors carry enough of the inactive error).

### P453 Islam, Tabassum: Brain Metastases Segmentation for BraTS 2026 Task 1: A Multi-Architecture Comparison
- **Id / links:** arXiv 2609.24769. Full text read (2.2 to 2.5). Code https://github.com/mahdiislam79/BraTS_METS_2026 (scout, unverified).
- **Claim (R):** region-based vs label-based training with patient-grouped 5-fold CV. Region reconstruction writes regions in a declared order, each overwriting the previous; a wrong order (inner region before outer) inflated one label and collapsed tumour-core Dice (scout's figures from the results table: TC 0.400 region vs 0.742 label; ET 0.713 vs 0.710 when the order did not matter). Found by a voxel-count comparison against the label-based model.
- **Evidence check (S):** this is a negative-control paper: with the order right, region training gave no ET gain (0.713 vs 0.710). So P027's gain is not universal. The write-order bug is exactly the risk in our decision rule.
- **Hypothesis (S):** none of its own; it fixes the decision order in `layered_ci` (crack always last, never overwritten) and adds a unit test that compares predicted class pixel counts of the layered decision against the softmax decision on the same dump.
- **Status:** RUN_AFTER_GATE with `layered_ci` (same gate).

### P183 Multiclass Boundary Refinement with Neural Cellular Automata (2026) and P082 rNCA: Self-Repairing Segmentation Masks (MIDL 2026)
- **Ids:** arXiv 2610.30007 (P183, code none found); arXiv 2512.13397 (P082, code https://github.com/maltesilber/rnca, scout, unverified). Scout records only.
- **Claims (R, scout):** P183: an NCA updates class log-probabilities of a frozen segmenter; mean boundary IoU 46.63 -> 48.99, +8.5 boundary IoU on the most irregular class. P082: 12k-parameter NCA, 64 steps, on DRIVE: Dice 0.761 -> 0.777, clDice 0.802 -> 0.820, fragments (beta0 error) 0.965 -> 0.532; SegFix 0.759, SegRefiner 0.760, DenseCRF 0.760 in the same table.
- **Evidence check (S):** gains are boundary-level and small in Dice; DRIVE is 20 images. A refiner trained on out-of-fold maps can only fix the error type that dominates; `ci_error_atlas` says whether inactive errors are boundary errors.
- **Status:** RUN_AFTER_GATE, arm `inact_refiner` (not specified in this wave); gate = atlas boundary share >= 40% of inactive error px and an oracle boundary fix worth >= +0.05 inactive IoU.

### P314 Teichmann, Cipolla: Convolutional CRFs for Semantic Segmentation
- **Id:** arXiv 1805.04777; code https://github.com/MarvinTeichmann/ConvCRF (scout, unverified).
- **Claim (R, abstract via scout):** local mean-field CRF as convolutions, over 100x faster than FullCRF. DenseCRF on DRIVE thin vessels: Dice 0.761 -> 0.760 (from P082's table).
- **Status:** RUN_AFTER_GATE as the zero-training control of `inact_refiner` (same gate). Bilateral intensity kernels suit inactive (uniformly dark) and not cracks.

---

## Cards: benchmark-only and protocol papers

### P090 Wang et al.: Balancing Logit Variation for Long-Tailed Semantic Segmentation (CVPR 2023)
- **Id / links:** arXiv 2306.02061; code https://github.com/grantword8/BLV (R: stated in the paper). Full text read (3.1, 4.1, 4.4, Algorithm 1).
- **Claim (R):** add category-dependent Gaussian noise to the logits during training only. Cityscapes fully supervised: +0.24 to +1.20 mIoU over 7 backbone / head pairs; ViT-B + UperHead 77.7 mIoU, tail 66.2, ahead of Lovasz and logit adjustment in their Table 5.
- **Evidence check (S):** the text says variance is larger for tail classes; the pseudo-code adds `|noise| * freq / freq.max()` to every logit, which is larger for head classes, that is, a stochastic logit adjustment that favours tail classes at test. The two descriptions disagree in form but agree in effect. Gains are 0.2 to 1.2 mIoU on 19 classes with thousands of images; at our scale this is below any detectable margin unless the rare classes are decision-limited, which `classbias_xfit` measures for free.
- **Status:** BENCH_ONLY (long-tail row of the benchmark loss suite, one line of code); not expected to beat `la_ce` on our score.

### P269 AUCSeg (NeurIPS 2024)
- **Id:** doi:10.52202/079017-4029; code https://github.com/boyuh/AUCSeg (scout, unverified). Scout record only.
- **Claim (R, scout):** pixel AUC loss with a tail-class memory bank; tail gains on Cityscapes, ADE20K, COCO-Stuff.
- **Status:** BENCH_ONLY (recent long-tail method for the suite; memory bank of tail crops is a sampling change that overlaps T1 `rcs`).

### P029 BiCC, P326 blob loss
- **Ids:** arXiv 2609.30223 (code https://github.com/TIO-IKIM/BiCC-Loss, scout, unverified); doi:10.1007/978-3-031-34048-2_58 (code https://github.com/neuronflow/blob_loss, scout, unverified).
- **Claims (R, scout):** BiCC: lesion F1 above DiceCE on 3 of 5 datasets, tie on 2; blob loss: F1 +2 to +5% vs soft Dice, but lower precision on 4 of 5 datasets in BiCC's comparison.
- **Status:** BENCH_ONLY (component-wise loss rows; T2 `cc_dicece_crack` tests the mechanism on crack). For inactive, components are few (48 cells), so a component loss on inactive has little signal (S).

### P436 SAMRefiner, P509 CascadePSP, P487 SegRefiner
- **Ids:** arXiv 2502.06756 (code https://github.com/linyq2117/SAMRefiner, unverified); doi:10.1109/cvpr42600.2020.00891 (https://github.com/hkchengrex/CascadePSP, unverified); doi:10.52202/075280-3492 (https://github.com/MengyuWang826/SegRefiner, unverified).
- **Claims (R, scout):** class-agnostic mask refiners; SegRefiner on DRIVE thin vessels 0.761 -> 0.760 (P082 table).
- **Status:** BENCH_ONLY: zero-training refinement track entries for inactive masks (blobby, well labelled). Weights: SAM and CascadePSP weights are public downloads (unverified per URL; none gated as far as the scout records say).

### Protocol papers: P571 CC-Metrics, P549 Boundary IoU, P618 Panoptica, P007 cross-validation variance, P546 data leakage, P610 simple baselines under imbalance
- P571 (doi:10.1609/aaai.v39i4.32408; code https://github.com/alexanderjaus/CC-Metrics, unverified): per-component Dice on Voronoi cells removes the large-component bias. Use: per-region inactive scores (3 test cells hold 59% of inactive px, BRIEF 2).
- P549 (arXiv 2103.16562; code https://github.com/bowenc0221/boundary-iou-api, unverified): boundary IoU for inactive and large classes, useless for 1 to 2 px crack (equals mask IoU at d >= 2).
- P618 (arXiv 2312.02608): tooling for instance-wise scores.
- P007 (arXiv 2606.12552): repeated CV enlarges the effective test set (sample gain about 5 to 20 at K = 20 on real data). Use: a second grouping of the 532 cells for inactive, the one class where CV5-G is not more powerful than the test set.
- P546 (arXiv 2508.17416): near-duplicate leakage audit.
- P610 (doi:10.1007/978-3-032-31673-8_35): tuned plain CE stays within 0.8 to 3.3 mIoU of 11 imbalance methods; report the tuning budget of every method. This supports fitting the decision layer for every entry before crediting a long-tail loss.
- **Status:** PROTOCOL.

---

## Extra paper used outside the digest
- **Ghiasi et al.: Simple Copy-Paste is a Strong Data Augmentation Method for Instance Segmentation (CVPR 2021)**, arXiv 2012.07177 (doi:10.1109/cvpr46437.2021.00294). Abstract read (R): random pasting of objects is enough; COCO +0.6 mask AP over the previous state of the art; LVIS rare categories +3.6 mask AP over the 2020 challenge winner (not an ablation). Used as the mechanism reference for arm `inact_paste`; our arm departs from it on purpose by pasting in place (same source, same cell type, same cell coordinates), because inactive regions are bounded by cracks and busbars and their context is the cell layout. Project evidence against naive paste (E, BRIEF 5): crack copy-paste onto pool cells was n.d. and added decoys.

## Status summary
RUN_NOW 5 (P015, P045, P196, P009, P252), RUN_AFTER_GATE 6 (P027, P453, P152, P183, P082, P314), BENCH_ONLY 7 (P090, P269, P029, P326, P436, P509, P487), PROTOCOL 6 (P571, P549, P618, P007, P546, P610), PARKED 55, VOID 0. No paper in the list repeats a BRIEF 5 run under the same conditions: the nearest are R2c (Dice on gridline, a loss weight, not a decision rule or a recall-adaptive weight) and B1 (label-error detection without any training change).
