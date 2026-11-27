# D15: Segmentation from noisy, misaligned or incomplete pixel labels

Scout: literature agent, 13 Nov 2026. Literature phase only: no servers, no test data read.
Tags: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## Why this direction matters here (S)
BRIEF section 2 and 5 show crack strict IoU is close to a labelling ceiling: 1 px shift of a perfect mask gives IoU 0.56, two annotations agree at 0.21 to 0.26, label width differs by source (1.5 to 3.25 px), and 70% of IoU loss lies within 2 px (E). Section 5 lists "automatic label refinement, noise-robust training, annotator / source-style modelling" and "noisy-label methods" as never tried. Only offset-tolerant CE (n.d.), soft clDice and Skeleton Recall touched this area.

One point every arm below must respect (S): test labels are noisy too. Training on cleaner labels can raise relF1@2, crispness and component recall while lowering strict IoU against jittered test labels. Every arm must report both strict crack IoU and relF1@2 on clean-49, and the best ones should also be scored against a refined copy of the test labels (benchmark track, not a replacement).

## Queries run (Research MCP unless marked; Scopus, S2 and arXiv back-ends mostly failed, OpenAlex answered)
1. noisy label semantic segmentation early learning adaptive correction (2020+)
2. noisy annotations thin structure segmentation vessel misalignment (2020+)
3. robust loss noisy segmentation labels T-Loss Student-t (2020+)
4. boundary label noise segmentation misaligned annotations (2020+)
5. road extraction misaligned labels noisy alignment segmentation (2020+)
6. crack segmentation noisy labels inaccurate annotation (2020+)
7. edge detection noisy labels thin edge alignment annotation uncertainty (2019+)
8. disentangling annotator error segmentation multiple annotators confusion matrices (2020+)
9. positive unlabeled learning semantic segmentation missing annotations incomplete labels (2020+)
10. spatially varying label smoothing segmentation boundary uncertainty (2020+)
11. Devil is in the edges semantic thinning edge alignment learning noisy annotations (2018+)
12. confident learning pixel label error detection segmentation (2020+)
13. segmentation with noisy labels (2025+)
14. curvilinear structure segmentation label noise skeleton annotation offset (2023+)
15. co-teaching noisy labels medical image segmentation pixel-wise sample selection (2020+)
16. optimal transport loss misaligned annotations segmentation shift-tolerant (2020+, nothing useful)
17. crack annotation uncertainty soft label pixel tolerance thin crack segmentation loss (2022+, nothing useful)
18. label refinement noisy masks foundation model SAM correct annotations (2024+)
19. noisy labels thin structures segmentation (2025+)
20. annotator-specific segmentation conditional annotation style personalized multi-rater (2022+)
21. jointly learn label alignment displacement field segmentation misregistered annotations (2020+, nothing useful)
22. incomplete annotations missing positives segmentation online label correction (2022+)
- Snowball: get_citations on ADELE (doi:10.1109/cvpr52688.2022.00263); similar_papers on PNT-Edge + Study Group Learning.
- search_snippets x2: rate-limited (S2 keyless pool), no result.
- WebSearch x7: 2025 thin-structure noisy-label code; STEAL repo; SGL repo; Crispness code; PNT-Edge repo; SVLS repo; Zhang 2020 repo; Syncrack code.
- Full text read: PNT-Edge (results tables), Delving into Crispness (noise study, method), NSegment+ (method, LNL comparison, code listing).

## Selected papers

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2007.15963 | 2020 | NeurIPS 2020 (web) | github.com/moucheng2017/Learn_Noisy_Labels_Medical_Images (web, not opened) | Two coupled CNNs: one predicts the true label distribution, the other a pixel-wise confusion matrix per annotator; trace regulariser makes annotators "maximally unreliable" so the clean head stays clean. | Treat the 5 sources (ARTS, CFVS, CSIR, BMRK, SDLE) as 5 annotators. Confusion head only over {bg, crack, inactive, other} to keep it small; source id is known at test time, so report both the clean head and the source-specific head. The source head can learn BMRK/SDLE 3 px width vs ARTS 1.5 px. | 70 | 55 |
| 2 | doi:10.1007/978-3-030-87193-2_6 | 2021 | MICCAI 2021 | github.com/SHI-Labs/SGL-Retinal-Vessel-Segmentation (web) | K-fold "study group": train K models on K-1 folds, each relabels its held-out fold, then train on original + cross-fold labels (distillation). Designed for tiny, noisy thin-vessel sets (DRIVE, CHASE_DB1). | Use the existing module-grouped 5-fold roots over 532 cells. Each fold model predicts soft crack/inactive maps on its held-out cells; final model trained on mix of hard labels and out-of-fold soft labels (weight 0.5). Also yields a single model that carries part of the 5-seed ensemble gain. | 72 | 45 |
| 3 | doi:10.1145/3581783.3612136 | 2023 | ACM MM 2023 | github.com/DREAMXFAR/PNT-Edge (named in paper, not opened) | Pixel-wise Shift Learning: a side branch predicts a displacement field that warps the clean prediction onto the noisy label; loss is on the warped map, so the main head learns un-shifted edges. | Add a 2-channel flow head on the decoder, bounded to +/-3 px (tanh x 3), applied only to crack (and inactive boundary) channels; edge-density term replaced by a smoothness penalty along the crack. Inference uses the unwarped head. | 62 | 40 |
| 4 | doi:10.1109/tip.2023.3289296 | 2023 | IEEE TIP | not found (unverified) | Refine human edge labels by keeping the subset of over-detected Canny edges that best align with them, inpainting gaps iteratively; trains crisper detectors. Shows label offset, not loss, drives thick predictions. | Replace Canny with a dark-ridge detector (multi-scale Frangi / Hessian on inverted EL) at low threshold; snap each crack label pixel to the nearest ridge pixel within 2 px; keep the original label where no ridge exists (faint cracks); then restore source width (dilate to source median). Pure preprocessing, CPU only. | 65 | 60 |
| 5 | doi:10.1109/cvpr.2019.01133 | 2019 | CVPR 2019 | github.com/nv-tlabs/STEAL (web; inference + refinement notebook) | STEAL: thinning layer plus NMS-style loss for crisp boundaries, and "active alignment" that moves noisy label curves toward the predicted boundary during training (level-set evolution). | Apply active alignment to crack labels every 2k steps: move each label pixel to the argmax of p(crack) within a 2 px window along the local normal, keep connectivity. Distinct from the tried offset-tolerant CE because the label itself is updated and kept, not min-pooled per step. | 58 | 35 |
| 6 | doi:10.1016/j.neucom.2022.01.051 | 2022 | Neurocomputing | none found (unverified) | Road-crack study: inaccurate annotations cost up to 20% F; weakly supervised label correction gives up to +12% on Syncrack, transfers to CrackForest / Aigle-RN. Syncrack generator adds controlled annotation noise. | Closest domain evidence for label correction on 1 to 3 px cracks. Use its protocol to build an EL "synthetic jitter" probe: perturb train crack labels by known offsets and measure how strict IoU vs relF1@2 degrade; tells us whether arms 1 to 5 can even move strict IoU. | 55 | 70 |
| 7 | doi:10.1016/j.ress.2025.110909 | 2025 | Reliab. Eng. Syst. Saf. | not found | SelectSeg: deep-ensemble uncertainty flags noisily annotated samples, which are then used as unlabelled data in SSL; selective prediction abstains on hard cases. Crack data, limited data. | We already have 5-seed ensembles. Rank train cells by ensemble disagreement with the label (crack only); drop labels of the top 10% (about 24 cells, matching the audit count) and train them with the MT consistency branch already in the codebase. Selective prediction gives a coverage vs crack-F curve for the benchmark. | 55 | 55 |
| 8 | doi:10.1007/978-3-030-78191-0_52 | 2021 | IPMI 2021 | github.com/mobarakol/SVLS (web) | Spatially Varying Label Smoothing: soft target = Gaussian-weighted average of one-hot labels in a 3x3 window, so uncertainty sits only at boundaries. | For cracks the whole object is a boundary: use SVLS with sigma 0.7 to 1.0 only on the crack channel, giving a soft 3 to 4 px band that matches the 4 px FWHM dark line; keep Dice on the hard label. Soft-label losses are listed as untried in BRIEF section 5. | 55 | 30 |
| 9 | arxiv:2508.10383 | 2025 | arXiv | inline code in the paper appendix (cv2.remap) | NSegment+: elastic deformation applied to the label only, image untouched, resampled every epoch; small segments are exempted. Beats AIO2, L2B, UCE, Compensation Learning on Vaihingen / Cityscapes. | Invert the small-object rule: apply a smooth sub-pixel to 1.5 px deformation to crack and inactive labels only (alpha small, sigma 4 to 8 px), never to structural classes, p=0.5. Cheap 1-line dataloader change. | 50 | 40 |
| 10 | doi:10.1109/cvpr52688.2022.00263 | 2022 | CVPR 2022 | github.com/Kangningthu/ADELE (in abstract) | Detects per-class start of memorisation from the training IoU curve; after that, replaces labels where the model is confident; adds multi-scale consistency. | Per-class trigger on crack, inactive, gridline, splice, edge_dark separately (rare classes memorise at different times); only allow corrections within 2 px of existing crack labels (no new crack components) to protect recall. | 52 | 50 |
| 11 | doi:10.1016/j.media.2025.103735 | 2025 | Medical Image Analysis | robust-tloss.github.io (in abstract) | T-Loss: negative log-likelihood of a Student-t; one learnable nu controls how much large residuals are down-weighted. | Replace CE on crack and inactive channels with T-Loss (separate nu per class), keep soft Dice. One-day change. | 45 | 55 |
| 12 | doi:10.1109/tmi.2024.3524253 | 2024 | IEEE TMI | github.com/Erjian96/CLCS (in abstract) | CLCS: two-branch co-training with a discrepancy loss votes on pixel cleanliness; curriculum dynamic threshold so minority classes are not filtered out; robust loss on suspected noisy pixels instead of dropping them. | Class-balanced threshold is the relevant part for 0.19% crack pixels. Implement as two U-Net++ decoders on one ResNet-34 encoder; select only crack / inactive pixels for noise handling. | 45 | 45 |
| 13 | arxiv:2504.14795 | 2025 | arXiv | github.com/pfnet-research/Bayesian_SpatialCorr (in abstract) | ECCD: variational model of spatially correlated label errors via a latent Gaussian field with KMS covariance; misalignment and omission handled as correlated flips. | Model the crack label as the true crack with spatially correlated flips along the crack direction (1D correlation length about 10 px). Most principled match to "jitter along a traced line" but highest implementation risk. | 40 | 30 |
| 14 | doi:10.1016/j.engappai.2026.115849 | 2026 | Eng. Appl. AI | not found | Trust-region refinement for ultra-thin fracture lines: foundation-model masks act only inside a narrow band around expert labels, an IoU gate rejects bad cases, closing repairs gaps. Unconstrained MedSAM supervision hurt. Adds a skeleton-aware metric (centerline coverage minus halo). | Use our 5-seed ensemble (or SAM2 prompted by label skeleton points) as the proposal; accept only within a 2 px band around each crack label, gate per component at IoU >= 0.3 with the label. The skeleton metric is a candidate benchmark metric next to relF1@2. | 52 | 60 |
| 15 | doi:10.1109/tgrs.2024.3373908 | 2024 | IEEE TGRS | github.com/zhu-xlab/AIO2 (in abstract) | AIO2: adaptive correction trigger from the mean-teacher accuracy curve plus online object-wise label correction for incomplete (missing) labels. | For missing crack annotations: add a teacher-predicted crack component to the label only if p>0.9, length >= 20 px, and not inside a scuff/edge_dark region. Targets the audit's missed cracks and H36 speck labels. | 42 | 35 |
| 16 | doi:10.1109/wacv56688.2023.00323 | 2023 | WACV 2023 | not checked | Component-level uncertainty (meta-classification) on predicted connected components flags label errors; benchmarked by dropping labels from Cityscapes / CARLA. | Run on train+val with out-of-fold predictions to produce a ranked list of suspected crack / inactive label errors per source. For the benchmark: quantify label error rate per source and per test cell, which decides which test cells count as "clean". | 35 | 75 |
| 17 | arxiv:2509.02419 | 2026 | Medical Image Analysis (doi:10.1016/j.media.2026.104130) | github.com/ortonwang/GSD-Net (web, not opened) | GSD-Net: pixel loss weights set by geometric distance to the object boundary plus structural guidance, for boundary-concentrated label noise. | Distance weighting must be inverted for cracks: down-weight background pixels 1 to 2 px from a crack label (likely mislabelled true crack) rather than crack boundary pixels. | 40 | 30 |
| 18 | arxiv:2406.10891 | 2024 | arXiv | not checked | COCO-N / Cityscapes-N / COCO-WAN: benchmark of segmentation under simulated and semi-automated annotation noise; finds popular LNL methods give little. | No model change. Template for a "noisy-label robustness" track in the EL benchmark: train-label perturbation levels (offset, width, omission) with fixed test. | 20 | 60 |

Scores: score = expected gain on our metrics x probability x feasibility (rubric in task). bench = value for the benchmark vision.

## Minimum experiments (house = U-Net++ ResNet-34, 20k steps; PF where stated; 5 seeds unless noted; clean-49 test and E1 scored only after the arm is frozen on val / folds)

1. Source-annotator confusion heads (arxiv:2007.15963): arm = house + 5 source confusion heads, clean head scored; second readout = source head. Baseline = house, 5 seeds. Metric = clean-49 crack IoU and relF1@2; per-source crack IoU for BMRK / CFVS. Kill if clean-head crack IoU < house - 0.005 and source-head crack IoU < house + 0.012 (the detectable change). About 6 GPU-h.
2. Study Group distillation (MICCAI 2021): arm = 5 fold models (existing fold roots) produce out-of-fold soft labels; final single model trained on 0.5 hard + 0.5 soft. Baseline = house single model and house 5-seed ensemble. Metric = crack IoU, relF1@2, inactive IoU. Kill if single-model crack IoU gain < +0.008 (less than half the ensemble gain). About 12 GPU-h.
3. Ridge-snapped labels (Crispness, TIP 2023): arm = house trained on snapped crack labels (CPU preprocessing). Baseline = house. Metric = relF1@2 and relP@2 primary, strict crack IoU vs original test labels secondary. Kill if relF1@2 gain < +0.01 or strict IoU drops > 0.02. About 6 GPU-h.
4. PNT-Edge flow head: arm = house + bounded flow head on crack channel. Baseline = house. Metric = strict crack IoU and component recall >= 20 px. Kill if strict IoU < house and relF1@2 not up by >= 0.01. About 6 GPU-h plus 2 days code.
5. STEAL-style active alignment: arm = label update every 2k steps within 2 px. Baseline = house. Kill as arm 3.
6. SVLS on crack (IPMI 2021): arm = SVLS sigma 0.8 on crack CE. Baseline = house. Kill if crack IoU and relF1@2 both < house + 0.005.
7. Label-only jitter (NSegment+ inverted): arm = elastic jitter on crack/inactive labels only. Baseline = house. Kill as arm 6.
8. Synthetic-jitter probe (Rill-Garcia 2022 protocol): train house on train labels with added known 1 px / 2 px offsets; measure the drop in strict IoU and relF1@2. If an extra 1 px jitter costs < 0.01 strict IoU, label-noise arms cannot move strict IoU and should be judged on relF1@2 only. 10 runs, about 11 GPU-h. Run this first.
9. SelectSeg-style filtering: arm = top-10% disagreement cells unlabelled for crack, MT branch. Baseline = house. Kill if crack IoU < house + 0.008.
10. ADELE / T-Loss / CLCS: one 3-seed screen each on 5-fold CV crack IoU (better instrument than 50 test cells); promote only if fold-mean gain >= +0.01.

## Notable papers rejected
- doi:10.1109/cvpr46437.2021.01223 (ProDA): UDA pseudo-label denoising; belongs to an E1 / UDA direction, not label noise.
- arxiv:2002.07394 (DivideMix): classification; segmentation versions covered by CLCS / SelectSeg.
- doi:10.1016/j.media.2023.102937 (YoloCurvSeg): weak skeleton labels to masks; we already have pixel labels, its noisy-skeleton synthesis is less direct than arm 4.
- doi:10.1007/978-3-030-01219-9_24 (SEAL, ECCV 2018): same alignment idea as STEAL; kept STEAL because it has code. SEAL's bipartite-matching alignment is a valid simpler implementation of arm 5.
- arxiv:2503.12218 (adaptive label correction, 2025) and doi:10.1109/tmi.2025.3589058 (region uncertainty, 2025): medical organ / 3D volumes, blobby targets, no thin-structure evidence; mechanism overlaps ADELE / CLCS.
- arxiv:2511.18894 (pixel-wise meta-learning, 2025): needs a clean meta set; we have none that is cleaner than train.
- doi:10.1109/cvpr52733.2024.01090 (D-Persona multi-rater): needs several annotations per image; we have one per cell. Arm 1 covers source styles.
- doi:10.1109/iccv51070.2023.01165 (SILT shadows): missing / extra blob labels; inactive is well labelled (1 px shift IoU 0.94), so little to gain.
- arxiv:2604.11162 (Boxes2Pixels): boxes to pixels with SAM; only relevant if PVEL-AD boxes are used (another direction).
- doi:10.1109/tcsvt.2025.3525629, doi:10.3389/fmed.2025.1653865, doi:10.1007/978-3-032-05169-1_51: domain-specific variants of co-teaching / correction without thin-structure evidence.
- arxiv:2603.13659 (FMS2 flow matching thin structures): architecture, not label noise; pass to the architecture direction.

## Gaps
- No paper found with label-noise results on 1 to 2 px structures with real (not synthetic) jitter and a strict-IoU metric. Closest: retinal vessels (SGL), road cracks (Rill-Garcia), semantic edges (STEAL, PNT-Edge). Expect evidence to come from our own synthetic-jitter probe (arm 8).
- search_snippets (Semantic Scholar) was rate-limited the whole session, so effect sizes for SGL, ADELE, T-Loss and CLCS are from abstracts only, not tables.
- Code for Crispness, Rill-Garcia / Syncrack and SelectSeg not found. PNT-Edge, GSD-Net, Zhang 2020 repos named but not opened.
- Sub-direction worth its own search: source-conditional prediction (conditioning on source id at test) as a benchmark protocol question: is it fair to use the source id at test time? The unseen-module set E1 is mostly CSIR, so a source head is usable there.
- Sub-direction: label-noise-aware evaluation metrics (expected IoU under annotator jitter, skeleton coverage with halo penalty) belongs to the benchmark-metrics direction; arxiv:2406.10891 and doi:10.1016/j.engappai.2026.115849 are inputs.
- Positive-unlabelled segmentation proper (nnPU loss on pixels) gave no segmentation paper with thin-structure evidence in OpenAlex; AIO2 is the closest.
