# D31 Test-time adaptation (TTA) and test-time augmentation for segmentation

Scout: D31 literature agent, 12 to 13 Nov 2026 (two sessions; working notes in `D31_notes_wip.md`).
Labels: R = what a paper measured, E = what our own files measured (BRIEF, handbook), S = my judgement.

## 0. What our own files already say (E), and what that means for this direction (S)

- D4 test-time augmentation (8 views, flips + rot90) was run (handbook doc 18, M1/R1, 24 Oct): single model crack IoU +0.0104 on clean 49 (on the 0.01 floor), on top of the 5-seed ensemble -0.0001, val chose TTA off, and TTA made one seed's noisy-cell failure worse (75k to 103k crack px). So plain dihedral TTA is closed for in-distribution test on the house model. It was not scored on E1, and multi-scale TTA was never run.
- Test-time BN statistics were run twice and failed: global BN-HC (raises false alarms) and per-panel AdaBN (T9, doc 20 s3.2: dAP <= +0.016 vs a +0.03 bar, crack-free false alarms on H36 up to 70x). TENT was dropped without a run.
- On E1, 70% of crack pixels get p(crack) < 0.001 and within strata the failure is ranking, not threshold (doc 20 s2.1). E1 crack labels are about 1.5x wider than train labels.
- S: methods that only recalibrate (BN statistics, entropy minimisation, logit or prior correction) can at best move the threshold, which is not the E1 problem, and on a rare thin class entropy minimisation pushes toward background (R evidence below: SGP-TTA ablation, BAPA, TTAP). TTA methods that can change ranking are (a) those that change the input scale or view so the model sees the crack at a scale it knows, (b) self-supervised test-time training (masked or denoising reconstruction) that updates features on the target image, and (c) structure-aware self-training with a consensus target. Expected gains for (b) and (c) are small and uncertain; they are cheap to test because they run on existing checkpoints.
- S, benchmark: the benchmark must fix a TTA protocol. Recommended: report every method with "no TTA" as the primary number, D4 flip TTA as a second fixed number, and put any method that updates weights on unlabelled test images in a separate transductive track (episodic per image, or continual per module), never mixed with the main table. MedSeg-TTA (row 13) and PIE (row 1) are the templates.

Common protocol for every min_experiment below (S):
- Checkpoints: FINAL (house model, 5 seeds) and SUP100-PF (5 seeds). No retraining unless the row says so.
- Hyperparameter choice: val 54 + F51 only; crack-free false alarms checked on H36 (crack labels unusable, but crack-free cells are usable as a false-alarm check) and on unlabelled pool half-cells (predicted crack area drift). E1 and test are read once, at the end.
- Metrics: test clean 49 crack IoU, relF1@2, component recall, inactive IoU, mIoU_rob; E1 crack relF1@2, recall, inactive IoU.
- Default kill line: on test clean 49, crack IoU or mIoU_rob drops more than 0.005 vs the same checkpoints without TTA, or E1 crack relF1@2 gains less than +0.02 (5 v 5 seeds, paired cell bootstrap), or H36 crack-free false alarms rise more than 2x.

## 1. Queries run

Research MCP `search_papers` (OpenAlex mostly; Semantic Scholar was rate-limited for most of both sessions; Scopus and ScienceDirect returned 401):
1. test-time adaptation semantic segmentation (2020+, and again 2025+)
2. test-time training masked autoencoders / masked autoencoder (2020+)
3. source-free domain adaptation medical image segmentation (2021+)
4. source-free domain adaptation semantic segmentation (2020+)
5. test-time augmentation segmentation uncertainty (2019+, 2020+)
6. continual test-time adaptation CoTTA ... (2022+) and continual TTA segmentation (2020+)
7. test-time adaptation thin curvilinear structures (2021+)
8. test-time adaptation segmentation class imbalance / collapse (2023+, twice with different wording)
9. visual prompt test-time adaptation medical segmentation low-frequency (2023+)
10. benchmark TTA realistic evaluation hyperparameter selection
11. multi-scale test-time augmentation small objects / scale selection (twice; nothing useful)
12. test-time adaptation crack segmentation domain shift (crack UDA only)
13. electroluminescence solar cell defect domain adaptation unsupervised (nothing for EL TTA)
14. diffusion-driven input adaptation test time
15. test-time training self-supervised auxiliary branch segmentation; TTT auxiliary task denoising autoencoder normalization
16. test-time adaptable networks denoising autoencoder normalization module
17. test-time adaptation defect segmentation industrial inspection
18. sharpness-aware entropy minimization batch size one (SAR family)
19. Tent fully test-time adaptation by entropy minimization
20. test-time training dense prediction segmentation self-supervised reconstruction (2025+)

Snowballing: `similar_papers` on SGP-TTA + TopoTTA; `get_citations` on TTT-MAE (174 citing papers, top 25 read). `search_snippets` was rate-limited every time. One full text read (SGP-TTA), one partial (BAPA).
WebSearch (11): CTTA seg 2025 code; TTA flip / multi-scale failure on rare classes; SGP-TTA code; VPTTA code; CoTTA + SAR code; PIE code; 2026 TTA rare classes thin structures; SAR code; MedSeg-TTA repo; TTT-MAE code; DeTTA + A3-TTA code.

## 2. Selected papers

Score = value for raising OUR scores (rubric in the task). Bench = value for the benchmark suite or its protocol.

| # | id | Year | Venue | Code | Mechanism | Adaptation to our data | Score | Bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2609.21412 (PIE) | 2026 | arXiv | none found (web) | Frozen weights and frozen BN; average softmax over scale + flip views mapped back; R: M&Ms vendor stream 0.7786 Dice vs source 0.7680 vs 5 online CTTA methods 0.7388 to 0.7416; saturates at 28 views; class-prior correction, CC filtering, morphology gave no gain or hurt; keeps thin structures | Flip part already run (E, +0.01 single, 0 on ensemble). New part is scale: views at 0.75, 1.0, 1.25, 1.5 (bilinear on image, logits resized back before softmax). The house model has no scale augmentation, so a second arm retrains with mild scale jitter (0.8 to 1.25, label-safe nearest-neighbour masks) so scale views are in distribution. BMRK cells are downscaled ELPV, so scale views may help that weak source | 48 | 70 |
| 2 | arxiv:2310.16783 (S3-TTA) | 2023 | arXiv | not verified | Per image, pick the scale and style transform whose prediction is most consistent under further transforms; R: +3.4% cell seg, +1.3% lung | Per cell, choose among scales {0.75 .. 1.5} and gamma {0.8, 1, 1.25} by flip-consistency of crack + inactive probability maps; addresses source-dependent contrast (5 sources) and BMRK scale. Pure inference on existing checkpoints | 40 | 35 |
| 3 | arxiv:2610.11104 (SGP-TTA) | 2026 | arXiv | not found (project page only) | ProgBN moves BN stats from source to target by sample count; Consensus Skeleton Recall (CSR) builds a skeleton target from 6 aligned views (id, flips, rot90/180/270) and updates only BN affine params, 1 Adam step per image, lr 1e-3. R (full text): cross-modality vessel / road gains large (DRIVE to STARE 51.3 to 74.2 Dice); when source is already good (CNDS 85.56) TENT / CoTTA / SAR / EATA fall to 62 to 63, SGP holds 85.27; adding an entropy term hurt (retina 65.22 to 62.36, road 59.15 to 44.98); MVC alone tiny (53.51 to 53.93) | Drop ProgBN (our T9 / BN-HC failed); keep CSR on BN affine only, per E1 module (continual within a module, reset between modules). Skeleton of the crack consensus with dilation r = 2 matches our 2 px label jitter. Our Skeleton Recall loss at training (w 0.1) was a narrow E1 pass, so a test-time version is a natural next step | 40 | 50 |
| 4 | doi:10.1109/iccv51701.2025.02236 (TopoTTA) | 2025 | ICCV | none official (per SGP-TTA authors; unverified) | Stage 1: topological meta difference convolutions added beside frozen convs; stage 2: synthesise pseudo-breaks in confident tubular predictions and align predictions on these hard samples; R: +31.81% clDice average over 10 datasets | Insert difference-conv adapters into U-Net++ decoder only; pseudo-breaks = mask out 5 to 15 px segments of predicted crack skeletons on test images and train the adapter to reconnect them. Targets broken crack predictions on E1 scuffed half-cuts. Needs our own implementation | 35 | 45 |
| 5 | doi:10.1109/wacv57701.2024.00052 (DeY-Net / DeTTA) | 2024 | WACV | github.com/WenRuxue/DeTTA (named in abstract; page not reached) | Train U-Net with an auxiliary denoising decoder (Y-Net); at test time adapt the shared encoder per sample with the denoising loss; R: liver seg DG gains over baseline (numbers not retrieved) | Add a 1-channel denoising decoder to U-Net++ during the house 20k-step training (Gaussian + EL-like shot noise), then per-cell or per-module denoising TTT on E1 and test. Differs from DDeP (decoder pretraining, n.d.) because the aux head is trained jointly and used at test time | 35 | 35 |
| 6 | doi:10.1109/cvpr52733.2024.02707 (Continual-MAE / ADMA) | 2024 | CVPR | project page only (sites.google.com/view/continual-mae); not verified | Distribution-aware masking of uncertain tokens, consistency between masked and unmasked target predictions, reconstruct HOG features at masked positions; SOTA on classification and segmentation CTTA | Mask 16 px patches where crack / inactive uncertainty is high, require prediction consistency with the unmasked view, reconstruct HOG of the 1-channel EL patch through a light head on the ResNet-34 encoder. Per-module continual on E1 | 30 | 45 |
| 7 | doi:10.52202/068431-2130 (TTT-MAE) | 2022 | NeurIPS | github.com/yossigandelsman/test_time_training_mae (verified) | Per test image, train the MAE encoder on reconstruction of masked patches, then predict with the updated encoder; R: gains on ImageNet-C and others | Needs a ViT MAE encoder (our ResNet-34 does not fit). Pairs with any ViT segmenter the D23 / D24 directions build: MAE-pretrain on the 11.9k pool, fine-tune for segmentation with frozen-encoder head, run TTT per E1 cell. Moonshot, 2 to 3 weeks | 25 | 40 |
| 8 | doi:10.1109/tip.2025.3644789 (A3-TTA) | 2025 | TIP | github.com/HiLab-git/A3-TTA ("will be made public"; unverified) | Pick target images with compact class-density as anchors, build pseudo-labels guided by anchors, boundary-aware entropy, self-adaptive EMA; R: +10.40 to +17.68 Dice over source on heart / prostate multi-domain | Anchors = E1 cells whose crack / inactive feature density is close to the train prototype (likely the 40 plain full cells); pseudo-labels for half-cut scuff cells guided by those. Class-balanced selection must be added for crack (BAPA row 11) | 30 | 40 |
| 9 | arxiv:2512.08569 (CoTICA, instance-aware CTTA) | 2025 | arXiv | not verified | Per-image, per-class confidence-adaptive pseudo-label thresholds; re-weights classes most hurt by the shift | Per-cell threshold on crack from the cell's own confidence quantiles instead of a global 0.95; directly targets the "confident background on faint cracks" null seen in our SSL work. Use as the pseudo-label rule inside rows 3 or 8 | 28 | 35 |
| 10 | doi:10.1109/cvpr52688.2022.00706 (CoTTA) | 2022 | CVPR | github.com/qinenergy/cotta (verified; includes Segformer seg code, TENT script) | Weight- and augmentation-averaged teacher pseudo-labels, stochastic restore of source weights | Run as the standard CTTA baseline on E1, module by module, with the house U-Net++ (port the loss; their seg code is Segformer). Expected to hurt crack (S), which is itself a benchmark finding | 22 | 65 |
| 11 | arxiv:2609.21743 (BAPA) | 2026 | arXiv | not verified | Shows entropy minimisation collapses imbalanced binary segmentation toward the majority class; fix: class-balanced anchors with equal total loss per class, prompt-only updates on a frozen VLM; best mean Dice over 4 domains | Not a method for our CNN; the transferable part is CBA: every self-training TTA arm here must select crack anchors separately and give crack equal total weight, otherwise background wins. Guidance row, cheap to apply inside rows 3, 8, 9 | 25 | 40 |
| 12 | arxiv:2302.12400 (SAR) | 2023 | ICLR | github.com/mr-eggplant/SAR (verified) | Entropy minimisation only on reliable low-entropy samples, sharpness-aware update, model recovery on collapse; designed for batch 1 and mixed shifts | Batch-1 per cell on E1 with BN affine (or GroupNorm) params; per-pixel reliability mask, collapse reset. Benchmark baseline for the entropy family; S: expected to move crack the wrong way | 18 | 55 |
| 13 | arxiv:2512.02497 (MedSeg-TTA) | 2025 | arXiv | github.com/wenjing-gg/MedSeg-TTA (named in abstract; page not reached) | 20 TTA methods, 7 modalities, one backbone and protocol; R: no paradigm wins everywhere; input-level methods most stable under mild shift; feature / output-level help boundary metrics; several degrade under large shifts | Template for the benchmark's TTA track: fixed backbone, same preprocessing, region + boundary metrics, report degradations. Reuse their implementations for TENT / SAR / CoTTA / VPTTA ports | 15 | 75 |
| 14 | doi:10.1109/cvpr52733.2024.01063 (VPTTA) | 2024 | CVPR | github.com/Chen-Ziyang/VPTTA (verified) | Frozen model; per-image low-frequency Fourier prompt trained in one iteration by BN-statistics alignment, memory bank init; widely used medical CTTA baseline | Prompt the amplitude spectrum of each 512 px EL cell; loss is BN alignment, which is the same signal that failed in T9, so low expected gain (S). Include as a baseline in the TTA track | 18 | 55 |
| 15 | arxiv:2006.10726 (Tent) | 2020 | arXiv (ICLR 2021 per memory, unverified) | in CoTTA repo (verified) | Minimise prediction entropy by updating BN affine params with test-batch statistics | The canonical baseline; never run here (dropped by expectation). One inference-time run on E1 settles it for the thesis and the benchmark | 12 | 60 |
| 16 | arxiv:2310.05341 (TTAP, critical look at classic TTA in seg) | 2023 | arXiv | github.com/ycarobot/TTAP (named in abstract; unverified) | Study: BN updating gives slight gain or harm in segmentation, teacher-student is stable but no gain over source on complex shifts, severe long-tail imbalance breaks seg TTA even with accurate pseudo-labels; proposes visual prompt TTA | Failure-mode evidence for rare classes; use to justify the benchmark rule "TTA reported separately" and the class-balanced selection in rows 3, 8, 9 | 15 | 45 |

## 3. Minimal experiments (one per row; all on gaint or cv02, inference-only unless stated)

1. PIE scale TTA. Arm A: FINAL and SUP100-PF, views = D4 x scales {0.75, 1.0, 1.25, 1.5} (32 views), mean softmax. Arm B: retrain house and PF with scale jitter 0.8 to 1.25 (5 seeds each, 11 GPU-h), same TTA. Baseline: same checkpoints with D4 TTA (the R1 setting) and without TTA. Metric: test clean 49 crack IoU and component recall >= 20 px; E1 relF1@2; BMRK crack IoU. Kill: no gain >= +0.01 crack IoU (single model) or >= +0.005 on the ensemble, or E1 relF1@2 < +0.02. About 1 GPU-h for A, 12 for B.
2. S3-TTA. Arm: per-cell scale + gamma selection by flip consistency on FINAL. Baseline: FINAL plain and D4. Metric: per-source crack IoU (BMRK, CFVS, CSIR) and E1 relF1@2. Kill: no source gains >= +0.02 and overall crack IoU not up by >= +0.005. Under 1 GPU-h.
3. SGP-TTA CSR without ProgBN. Arm: SUP100-PF, BN affine only, 1 Adam step per cell (lr 1e-3, sweep 1e-4 to 1e-3 on F51), 6-view consensus skeleton, dilation 2, continual within an E1 module, reset per module; episodic per cell on test. Baseline: SUP100-PF no TTA. Metric: E1 relF1@2, component recall; test crack IoU guard. Kill: default. About 2 GPU-h.
4. TopoTTA. Arm: decoder difference-conv adapters + pseudo-break reconnection on E1 modules. Baseline: SUP100-PF. Metric: E1 component recall and relF1@2. Kill: E1 relF1@2 < +0.02 or test crack IoU -0.005. 3 to 4 days of coding, about 3 GPU-h.
5. DeTTA. Arm: house model + joint denoising decoder (5 seeds, 6 GPU-h), then 10-step denoising TTT per cell on encoder. Baselines: same model without TTT, and the house model (to check the aux head itself does not hurt). Metric: E1 relF1@2 and inactive IoU; test guard. Kill: default, and aux head alone must not cost more than 0.005 crack IoU.
6. Continual-MAE. Arm: HOG-reconstruction head on ResNet-34 trained jointly (5 seeds), plus uncertainty-masked consistency TTA per E1 module. Baseline: SUP100-PF. Kill: default. About 8 GPU-h.
7. TTT-MAE. Only if D23 / D24 produce a ViT segmenter that is within 0.01 of FINAL on test. Arm: per-cell MAE TTT (20 steps). Baseline: that ViT segmenter without TTT. Kill: E1 relF1@2 < +0.03. About 20 GPU-h plus pretraining.
8. A3-TTA. Arm: anchors among E1 cells by density, class-balanced pseudo-labels for others, EMA. Baseline: SUP100-PF. Kill: default. About 2 GPU-h.
9. CoTICA threshold rule. Arm: replace the fixed pseudo-label threshold in row 3 or 8 with per-cell, per-class quantile thresholds. Baseline: the same row with a fixed threshold. Kill: E1 relF1@2 gain < +0.01 over the parent arm.
10. CoTTA. Arm: CoTTA on E1, per module, then on test. Baseline: same checkpoints, no TTA. Metric: all. Kill: none needed; this is a benchmark row. About 2 GPU-h.
11. BAPA's CBA. Applied inside rows 3, 8, 9 as an ablation: class-balanced anchors on vs off. Kill: no difference in crack recall on E1 (>= +0.02).
12. SAR. Arm: batch-1 SAR with BN affine. Baseline: no TTA. Benchmark row. Under 1 GPU-h.
13. MedSeg-TTA. Not an experiment: copy its table layout and metric pair (region + boundary) into the benchmark's TTA track.
14. VPTTA. Arm: per-cell low-frequency prompt (official code ported to 1-channel). Baseline: no TTA. Benchmark row. Under 1 GPU-h.
15. Tent. Arm: BN affine entropy minimisation, batch = one E1 module. Baseline: no TTA. Benchmark row and thesis closure. Under 1 GPU-h.
16. TTAP. Not an experiment: cited for the protocol and failure mode.

## 4. Notable papers rejected

- doi:10.1109/cvpr46437.2021.00127 (SFDA for semantic segmentation, Liu 2021) and other source-free DA (S4T, Generalize-then-Adapt, AdaMI doi:10.1016/j.media.2022.102617): we have the source data, so source-available UDA on pool half-cells (D30) dominates source-free variants.
- doi:10.1109/cvpr52729.2023.01134 (DDA, diffusion-driven input adaptation) and doi:10.1016/j.media.2025.103902 (test-time generative augmentation): the E1 shift is layout and scuff, not appearance (E: E1 content intensity matches train); a diffusion model that maps E1 to train style would also need training on EL. Generative data is D33's job.
- doi:10.1109/cvpr52729.2023.02307 (DIGA, backward-free BN + prototype mixing): BN statistics mixing is the T9 mechanism; prototype classifier mixing for a 0.19% class is fragile.
- doi:10.1109/wacv57701.2024.00254 (ROID, prior correction) and doi:10.1007/978-3-031-16440-8_70 (Bateson shape-moment / class-ratio TTA): prior or class-ratio correction is a calibration fix; E1 failure is ranking. PIE also found class-prior correction gave no gain.
- doi:10.1109/iccv48922.2021.00125 (better TTA aggregation): learned view weights over D4 views; D4 itself gives 0 on the ensemble here, so learned weights cannot add much.
- doi:10.52202/068431-2799 (MEMO, marginal entropy over augmentations): entropy family, built for classification; collapse risk on rare class (row 11, 16).
- arxiv:2403.11691 (TTT-KD, test-time distillation from foundation models, 3D): interesting, but our frozen DINOv2 / v3 / SAM2 probes showed no sign of crack signal (BRIEF s5), so a foundation teacher at test time has nothing to distil for cracks.
- doi:10.1016/j.media.2025.103859 (SicTTA), doi:10.1109/tip.2026.3732647 (SAM-aware TTA), doi:10.1109/iccv51701.2025.02074 (progressive energy TTA), doi:10.1016/j.inffus.2025.103300 (CertainTTA), doi:10.1609/aaai.v39i3.32244 (GraTa): strong medical TTA papers but each is an organ-scale method (large structures); none adds a mechanism for thin rare classes beyond rows 3, 8, 9.
- arxiv:2309.14052 (single-image TTA for segmentation): +1.7 to +3.5% from self-supervised losses plus adversarial mask refinement; useful as a reference for per-cell episodic TTA, no distinct mechanism beyond rows 3 and 8.
- Multi-modal / point-cloud / video / open-vocabulary TTA (MM-TTA, APCoTTA, AuxAdapt, OVSS TTA): wrong modality or setting.
- arxiv:2408.09494 (source-free TTA for online surface-defect detection): detection with boxes, not segmentation.

## 5. Gaps

- No EL, PV or crack paper uses TTA for segmentation (searched EL / PV / crack TTA and UDA; only crack UDA papers in civil engineering).
- No paper measures multi-scale TTA on 1 to 2 px structures. Its value here must be measured (row 1).
- `search_snippets` was rate-limited in both sessions, so evidence on flip / scale TTA for thin structures comes from PIE and SGP-TTA only.
- Code not verified for PIE, SGP-TTA, S3-TTA, TopoTTA, CoTICA, A3-TTA (announced), Continual-MAE. DeTTA and MedSeg-TTA repos are named in the abstracts, but the pages were not reached.
- Sub-direction worth its own search: transductive self-training on the E1-like unlabelled pool half-cells is UDA, covered by D30; the TTA track here should share D30's half-cell proxy for hyperparameter choice so E1 is never used for selection.
- Open benchmark question (S): whether a transductive TTA track on E1 should be per cell (episodic), per module (continual) or per dataset. My recommendation is per module, because a deployed inspector sees one module at a time.
