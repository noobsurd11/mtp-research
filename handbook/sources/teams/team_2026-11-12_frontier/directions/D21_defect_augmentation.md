# D21 Defect and rare-class augmentation

Scout: literature agent. First pass 12 Nov 2026 (Research MCP went down mid-run); completed 13 Nov 2026 with the failed queries, snowballing and three full-text reads.
Tags: R = the paper measured it, E = our files show it, S = my judgement.
Overlap note: D06 (EL synthesis) and D33 (generative data) cover generative renderers (CrackSegFlow, PV-DDPM as a generator, FMS2, FreeCOS, SeaS, AnomalyDiffusion, SIGAN). This file covers sampling, mixing, copy-paste, defect removal by inpainting, synthetic anomalies and procedural cracks, and cross-refers where they meet.

## 1. Bottom line (S)

1. **Cheapest untested levers: sampling.** The house sampler is uniform over 478 cells; inactive is in 42, splice is never predicted. DAFormer Rare Class Sampling gave +5.8 mIoU in its ablation (R). About 20 lines of code. Run first, on PF, judged by module-grouped CV for inactive. A 2026 paper (episodic sampling) warns that sampling gains on small data can come from the iteration budget; our runs are step-matched (20k steps), so that confound is already controlled.
2. **Supervised CutMix between labelled cells has never been run here.** Our CutMix was inside Mean Teacher on the unlabelled stream (n.d. at 100%). "Cut to the Mix" (MICCAI 2024) measured on 20 training volumes: CutMix +4.8 macro Dice over nnU-Net with its own augmentation, larger than CarveMix (+2.5) and AnatoMix (+3.2), and ObjectAug collapsed (64.3 vs 88.1 micro Dice) (R, full text). CutMix seams are labelled from both sides, so they teach "an intensity discontinuity is not a crack", the opposite of what CP100 taught.
3. **New EL-specific evidence against additive copy-paste and for subtractive edits.** Generative Defect Isolation (Solar Energy 2026, UCF-EL) removes defects with LaMa inpainting. On EL multi-label classification it beat a mask-exact random copy-paste on all three backbones; copy-paste lowered EfficientNetV2-L F1 0.767 to 0.746 while GDI raised it to 0.774 (R, full text, Table 5). The authors attribute the copy-paste failure to location dependence of EL defects and seam discontinuities, the same diagnosis as our CP100 decoys. For segmentation this gives a new arm: inpaint cracks out of labelled cells to create exact-location hard negatives.
4. **What CP100 actually closed (E, `protocol_cp5.md`, handbook row 26):** crack components only, pasted onto *unlabelled pool* cells, residual transfer of darkness on dilate(M,2), random placement anywhere in the eroded cell, loss only on the mask and a 2 to 6 px ring, house fine-tune. Result n.d., decoys 4.4x, false crack on clean val cells 178 to 389 px. It did not test: pasting between *labelled* cells with full supervision, same-location ROI transfer with context (CarveMix), **inactive** copy-paste, learned or rule-based placement, defect removal, CutMix of labelled cells, or confidence-weighted synthetic loss.
5. **Inactive copy-paste is the best augmentation bet for problem 2.** Inactive is blobby and well labelled (1 px shift IoU 0.94), so pastes are not hurt by label jitter. Paste the inactive region together with its bounding crack (CarveMix-style ROI with a context margin, at the same position in a same-source, same-cell-type target), so "inactive always touches crack" holds. Soft-CP +10.2% DSC at full data on KiTS19 (R); TumorCP +7.12% tumor Dice (R).
6. Poisson blending alone is not worth testing: Synth4Seg saw no gain from Poisson over direct paste (R).
7. Synthetic-anomaly methods (NSA, DRAEM, SuperSimpleNet) are long shots for our scores but belong in the benchmark suite as "few or no defect labels" baselines. SuperSimpleNet (2025, code) is the one recent model that trains in unsupervised, weak, mixed and full supervision, which fits a benchmark that also wants ELPV image labels.
8. Thin-line-safe geometry: the house already restricts geometry to exact pixel permutations (E). I still found no paper that tests sub-pixel elastic deformation on 1 to 2 px labels. Safe route: deform a synthetic skeleton before rasterising the label (DP crack synthesis).

## 2. Prior overlap (E)

| Mechanism | Tested? | Under which conditions |
|---|---|---|
| Crack copy-paste onto pool cells | yes, n.d., decoy FLAG | CP100, house optimizer, 100% labels, residual transfer, random placement, partial loss |
| Crack or inactive copy-paste between labelled cells, full labels | no | |
| Same-location ROI transfer with context margin (CarveMix) | no | |
| Supervised CutMix of labelled cells | no | SSL CutMix only (unlabelled stream, n.d. at 100%) |
| Defect removal by inpainting (hard negatives) | no | |
| Rare class / image oversampling | no (no run in handbook) | |
| Synthetic half-cut views | yes, n.d. on test / E1 | layout change, no new defects |
| Logit bias at inference | yes, part of best ensemble | inference only; training-time asymmetric methods not tried |
| Synthetic anomalies (NSA / DRAEM / SuperSimpleNet) | no | "anomaly-detection priors" listed as never tried |
| Procedural crack synthesis | no | |

## 3. Queries run

Session 1 (12 Nov), Research MCP search_papers: (1) copy-paste augmentation semantic segmentation blending context; (2) natural synthetic anomalies self-supervised anomaly localization; (3) DRAEM discriminatively trained reconstruction embedding; (4) synthetic crack generation procedural augmentation crack segmentation; (5) electroluminescence solar cell synthetic defect generation data augmentation; (6) rare class augmentation semantic segmentation class-balanced sampling long-tail. Then Cloudflare 502 for the rest of the session. WebFetch of arXiv pages and repos listed in the table.

Session 2 (13 Nov), search_papers (OpenAlex answered; S2 mostly rate-limited, Scopus / ScienceDirect 401):
7. copy-paste augmentation rare class semantic segmentation (2025+)
8. CarveMix lesion-aware data augmentation (2020+)
9. few-shot defect image generation diffusion segmentation augmentation industrial (2024+)
10. thin structure segmentation data augmentation vessel synthetic curvilinear (2021+)
11. Poisson blending copy-paste defect segmentation data augmentation (2020+)
12. synthetic crack image generation crack segmentation training procedural (2023+)
13. electroluminescence solar cell defect augmentation copy-paste synthetic crack (2022+)
14. rare class sampling domain adaptive segmentation class-balanced image sampling (2022+)
15. object removal inpainting augmentation segmentation negative samples defect-free background (2021+)
16. synthetic anomaly generation discriminative anomaly segmentation surface defect (2025+)
17. CutMix supervised semantic segmentation small dataset augmentation gain (2022+)
18. elastic deformation augmentation thin structures label topology preservation (2020+)
19. SinGAN crack texture blending synthesis limited data (2023+)
20. nnU-Net foreground oversampling patch sampling class imbalance ablation (2020+)
21. defect placement location-aware synthetic defect pasting realistic position segmentation (2024+)

Snowballing: similar_papers on Synth4Seg + Soft-CP (found TumorCP, LesionMix, Defect Transfer GAN); get_citations on CarveMix (found Cut to the Mix, LesionMix, ARHNet, CarveMix-RC). search_snippets: 4 attempts, all rate-limited by Semantic Scholar.
Full text read: Cut to the Mix (arxiv:2602.03555, sections 2 to 3), GDI (arxiv:2608.12725, sections 3.2.3, 4.1, 4.8, 5.3). SuperSimpleNet fetch timed out.
WebSearch: LesionMix code, GDI code, Synth4Seg code, 2026 copy-paste crack work. WebFetch verification: github.com/mueez-overflow/generative-defect-isolation (code present, LaMa via Inpaint-Anything, no license file), github.com/ZhangxinruBIT/CarveMix (code present, nnU-Net, NIfTI), HF card UCF-EL-GDI, arXiv pages 2107.09843 (TumorCP code link), 2308.09026 (LesionMix code "will be released"), 2602.03555, 2508.19060.

## 4. Selected papers

Score = value for our metrics. Bench = value for the benchmark. All arms run on PF (encoder-preserving fine-tune), 5 seeds, same commit and data as the PF baseline, unless stated. Inactive claims use the module-grouped 5-fold CV over 532 train + val cells, because 3 test cells hold 59% of test inactive pixels. All synthetic or mixed samples are built from train-fold cells only.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1109/cvpr52688.2022.00969 DAFormer Rare Class Sampling | 2022 | CVPR | github.com/lhoyer/DAFormer | P(c) = softmax((1 - f_c)/T), T = 0.01, then a uniform image containing c. Ablation 58.2 to 64.0 mIoU (+5.8), better than class-balanced T = inf (R) | f_c over the 24 classes from train masks; candidates only classes in >= 3 train cells; cap any cell's draw rate at 10x uniform so the 42 inactive cells are not memorised; same 20k steps | 68 | 45 |
| 2 | arxiv:2605.20405 Episodic (class-balanced batch) sampling | 2026 | arXiv | github.com/iasonsky/episodic-sampling (from abstract) | Build every batch so that each class appears; full data: equal to random (0.882 vs 0.878 Dice); low data: 0.787 vs 0.758, mostly from 12x more iterations; under matched budgets random overfits earlier (R) | Batch of 8 = at least 2 crack, 2 inactive, 1 cell from a rare-structure class, rest uniform. Mainly a design rule: compare sampling arms at matched steps (we do) and report the overfitting curve on val | 42 | 40 |
| 3 | doi:10.1109/tmi.2020.3046692 Li, Kamnitsas, Glocker | 2020 | IEEE TMI | unverified | Under imbalance the rare-class logits shift across the boundary at test time (under-segmentation); asymmetric augmentation, mixup, focal and large-margin losses applied to the rare foreground only (R) | Fits our symptoms (inactive recall 0.61; on E1 70% of crack px get p < 0.001). Strong photometric augmentation (contrast, gamma, noise, simulated downscale for BMRK) applied only inside dilated crack and inactive masks; asymmetric margin on classes 11 and 14 | 52 | 35 |
| 4 | doi:10.1007/978-3-031-72111-3_14 Cut to the Mix | 2024 | MICCAI (LNCS) | stated public, URL not found | Supervised CutMix between labelled images (box size ~ Beta(0.5, 0.5)); 20 training CT volumes, 16 organs: +4.8 macro Dice with nnU-Net augmentation, beats CarveMix and AnatoMix; ObjectAug collapses (R, full text) | CutMix between two labelled train cells of the same cell type (mono / multi), box aligned to the cell grid so busbars line up; labels copied with the box; 50% of batches. Do not mix across BMRK and others at first (different label widths). Gives class-aware variety for splice, gridline, edge_dark, material at no labelling cost | 60 | 45 |
| 5 | doi:10.1016/j.neuroimage.2023.120041 CarveMix | 2023 | NeuroImage (MICCAI 2021 orig.) | github.com/ZhangxinruBIT/CarveMix (verified, nnU-Net, 3D NIfTI) | Carve an ROI around the lesion with a random context margin from one labelled image and place it at the same coordinates in another labelled image; label follows; harmonise if sources differ (R, abstract) | EL cells of one type share geometry, so same-location transfer is natural. ROI = crack or inactive component dilated by a random 8 to 40 px margin, source and target same source and cell type, target labelled. The seam lies in background on both sides and is labelled, so seams are not tied to defects | 58 | 30 |
| 6 | arxiv:2203.10507 Soft-CP (and TumorCP arxiv:2107.09843) | 2022 | arXiv | Soft-CP unverified; TumorCP github.com/YaoZhang93/TumorCP | Lesion copy-paste with a soft object blend that keeps edge information; offline 3 : 1 real : synthetic. Soft-CP +10.2% DSC at full data on KiTS19; TumorCP +7.12% tumor Dice (R, abstracts) | Inactive library from the 42 train cells, each cut with its bounding crack pixels; paste onto labelled cells of the same source / cell type where the region meets a cell edge or busbar, intensity matched by the per-source inactive / active ratio, 3 px soft edge; target labels kept, pasted region overrides | 58 | 35 |
| 7 | doi:10.1016/j.solener.2026.114943 Generative Defect Isolation (GDI) | 2026 | Solar Energy | github.com/mueez-overflow/generative-defect-isolation (verified; LaMa via Inpaint-Anything; no license file) | Remove selected defects from EL images by LaMa inpainting using the annotation masks (15x15 dilation), creating single-defect and defect-free samples. On UCF-EL classification it beat mask-exact random copy-paste on all 3 backbones (R, full text) | Segmentation version: for a labelled crack cell, inpaint chosen crack components (mask dilated to cover the ~4 px dark line plus 3 px) and relabel them background; keep the rest. Hard negatives at the exact spots where cracks live. Also remove inactive but keep its crack (physical; crack-only cells are common). Never remove a crack and keep its inactive. Check grid-line restoration on 30 samples first | 62 | 50 |
| 8 | doi:10.1007/978-3-031-58171-7_8 LesionMix | 2024 | MICCAI DALI workshop | "will be released" at github.com/dogabasaran/lesionmix (unverified) | Lesion-level augmentation that controls lesion load distribution, shape, location and intensity; supports populating and inpainting lesions (R, abstract via arXiv page) | Combine rows 6 and 7 under one controlled load: per training cell, sample the number of crack components and inactive area from the train distribution of its source, then add (paste) or remove (inpaint) to reach it | 45 | 30 |
| 9 | doi:10.1109/tase.2025.3583713 Synth4Seg | 2025 | IEEE T-ASE | none found (Apple project page, no repo) | Online cut-and-paste onto labelled images; bi-level optimisation learns a pasting-location map and source weights from val loss. Learned location +18.3% (Screw), +12.2% (Capsule) over random; Poisson no gain (R) | Cheap form first: crack paste between labelled cells with a rule location map (start points near busbars / cell edges, orientation histogram per source from train masks; GDI cites that 50% of cracks run parallel to busbars). Bi-level form only if cheap form passes, location net tuned on the 54 val cells | 52 | 35 |
| 10 | arxiv:2102.00221 ObjectAug | 2021 | IJCNN | unverified | Lift objects by the label, inpaint the hole, transform and re-place each object | Within one cell: lift a crack, inpaint (row 7 inpainter), re-place by a dihedral move. Score lowered: Cut to the Mix measured ObjectAug at 64.3 vs 88.1 micro Dice (inpainting and transform artifacts) (R). Only worth running as the "move" half of row 7 | 30 | 20 |
| 11 | doi:10.1007/s41062-026-02792-x DP + elastic synthetic cracks | 2026 | Innovative Infrastructure Solutions | unverified | Min / max cumulative-energy paths on noise fields give 1 px crack strands; variable-width dilation and elastic deformation; F1 up to 0.79 on Cracks-200 / CDLN / DeepCrack with synthetic data only (R, abstract) | Deform the skeleton, then rasterise the label at each source's measured width (ARTS 1.5, CFVS / CSIR 1.75, BMRK 3.0, SDLE 3.25) and render a dark profile ~4 px FWHM with per-source contrast, including sub-2% contrast cracks. Render onto labelled cells and onto pool multi half-cut cells (strand + ring loss only) for E1. Exact labels, no jitter | 46 | 30 |
| 12 | arxiv:2609.12431 End-to-end controllable crack data synthesis | 2026 | arXiv | unverified | Bezier skeletons, GAN masks, dual-ControlNet rendering; ensemble agreement gives pixel-wise label confidence that weights the synthetic loss (beats threshold filtering at every threshold); POD width at 90% / 95% fell 8.0 to 4.3 px (R) | Take only the confidence weighting (house 5-seed ensemble scores every pasted, carved or rendered pixel) and apply it to rows 5, 6, 9, 11. Benchmark: report POD vs crack contrast and length on test and E1 | 45 | 70 |
| 13 | doi:10.1109/wacv57701.2024.00844 Cracktal / CAP-Net | 2024 | WACV | none (simulator "will be" on Zenodo) | Fractal crack simulator with exact labels; U-Net on simulation beat U-Net on 950 real multi-source images, attributed to inconsistent real annotation styles (R) | Same failure mode as ours (5 sources, 5 conventions). Second skeleton source next to row 11; AdaIN-style per-source intensity statistics when rendering | 38 | 30 |
| 14 | arxiv:2511.09604 PV-DDPM / E-SCDD | 2025 | arXiv | github.com/sntubix/pv-ddpm (opened; weights via gdown; no license file) | Pixel DDPM conditioned on layout masks; 4 cell types incl. half-cut multi; FID 4.10 (R). See D06 | Retrain on our train cells only (leakage), use as a domain-specific inpainter for row 7 (GDI's own limitation section asks for a PV-aware inpainter) and for half-cut layouts with edited crack masks | 45 | 65 |
| 15 | doi:10.1007/978-3-031-19821-2_27 NSA | 2022 | ECCV | github.com/hmsch/natural-synthetic-anomalies | Poisson-blend scaled patches from other images into normal images; train a localiser; MVTec AUROC 97.2 (R) | Auxiliary head on pool cells (incl. 1,152 multi half-cut) that predicts NSA patches, shared encoder with the segmenter; aim is a defect prior that transfers to E1 | 35 | 45 |
| 16 | doi:10.1109/iccv48922.2021.00822 DRAEM | 2021 | ICCV | github.com/VitjanZ/DRAEM (MIT) | Perlin-noise masks blend texture into normal images; reconstruction net plus discriminative net segments the synthetic anomalies | Benchmark "no defect labels" baseline: train on crack-free train cells, report crack / inactive AP and relF1@2 on test and E1. For scores: dark-line and dark-blob primitives instead of DTD textures; long shot | 30 | 60 |
| 17 | doi:10.1007/s10845-025-02680-8 SuperSimpleNet | 2025 | J. Intelligent Manufacturing | github.com/blaz-r/SuperSimpleNet (from abstract) | SimpleNet-based discriminative model with a new synthetic-anomaly generator; trains under unsupervised, weak (image label), mixed and full supervision; < 10 ms inference (R, abstract; numbers not read) | Benchmark baseline across supervision levels: full masks, image-level labels (ELPV-style), and mixed. For scores: its synthetic-anomaly stage as a regulariser on pool cells; long shot | 30 | 65 |
| 18 | doi:10.1109/cvpr46437.2021.00294 Simple Copy-Paste | 2021 | CVPR | github.com/tensorflow/tpu (models tree) | Random paste of instances is strong for instance segmentation at all COCO fractions (R) | Our CP100 is close to this. Only as the benchmark's plain copy-paste baseline, with the decoy test reported | 15 | 55 |

Bets: rows 1, 4, 5, 6, 7 safe or near-safe; rows 3, 9, 11, 12 medium; rows 14, 15, 16, 17 moonshots for scores (benchmark value).

## 5. Minimal experiments (arm, baseline, metric, kill line)

1. **RCS:** PF+RCS vs PF. Metrics: CV inactive IoU (5 folds), test mIoU_rob, splice / gridline IoU, test crack IoU as guard. Kill: CV inactive gain < +0.02 and mIoU_rob gain < +0.005, or crack IoU drop > 0.012. About 6 GPU-h (test, 5 seeds) + 25 GPU-h (CV).
2. **Episodic batches:** PF+EP vs PF+RCS vs PF, same 20k steps. Same metrics and kill as arm 1. Run in the same sweep as arm 1 (+6 GPU-h).
3. **Supervised CutMix of labelled cells:** PF+CM vs PF. Metrics: mIoU_rob, per-class IoU for splice / gridline / edge_dark / material, test crack IoU and false crack px on 31 crack-free val cells. Kill: mIoU_rob < +0.005 and crack IoU change within +-0.012. About 6 GPU-h.
4. **GDI hard negatives (inpaint cracks out):** PF+GDI vs PF. Pre-check without training: 30 inpainted cells inspected for grid-line restoration; house ensemble p(crack) on inpainted spots must fall below 0.1 (else the inpaint left a visible line). Metrics: test crack relP@2 and IoU, false crack px on val, E1 relF1@2 (scuff confounders). Kill: relP@2 gain < +0.01 and crack IoU gain < +0.012. About 6 GPU-h plus LaMa offline pass (< 1 GPU-h for 478 cells x 4 variants).
5. **CarveMix same-location ROI transfer (crack + inactive):** PF+CVM vs PF. Metrics: CV inactive IoU, test crack IoU, decoy rate as in CP100 E3b. Kill: CV inactive gain < +0.02 and crack IoU gain < +0.012, or decoy rate > 2x PF. About 31 GPU-h.
6. **Inactive + bounding-crack Soft-CP onto labelled cells:** PF+ICP vs PF. Metrics: CV inactive IoU, false inactive px on crack-only cells, crack IoU guard. Kill: CV inactive gain < +0.02, or false inactive px up > 50%. About 31 GPU-h. Pre-check: 32 composites against real inactive cells.
7. **Asymmetric rare-class augmentation:** PF + photometric / downscale augmentation only inside crack and inactive regions vs PF. Metrics: CV inactive IoU, BMRK inactive IoU, E1 crack recall@2. Kill: CV inactive < +0.015 and E1 recall@2 < +0.02. About 31 GPU-h.
8. **Crack paste between labelled cells with rule location map (Synth4Seg cheap form):** PF+CPL vs PF. Metrics: test crack IoU and relF1@2, decoy rate, false crack px on 31 crack-free val cells. Kill: crack IoU gain < +0.012, or decoy rate > 2x PF. About 6 GPU-h.
9. **LesionMix load control:** best of arms 4, 5, 6 with per-source load sampling vs the same arm without. Kill: < +0.01 on that arm's main metric.
10. **Confidence-weighted synthetic loss:** arm 5, 6, 8 or 11 with vs without ensemble-confidence weights. Kill: < +0.01 on that arm's metric.
11. **Procedural strands (DP, then Cracktal skeletons) at source widths:** PF+PROC vs PF. Metrics: E1 relF1@2 and recall@2 (half-cut scuff subset), test crack IoU guard, recall of cracks under 2% contrast. Kill: E1 relF1@2 < +0.02 or test crack IoU drop > 0.012. About 7 GPU-h plus 2 days of renderer code (shared with D06).
12. **PV-DDPM retrained as inpainter for arm 4:** PF+GDI(DDPM) vs PF+GDI(LaMa). Kill: not above arm 4. About 60 GPU-h generator + 6.
13. **NSA auxiliary head on pool cells:** PF+NSA-aux vs PF. Metric: E1 crack recall@2 and relF1@2. Kill: E1 relF1@2 < +0.02. About 10 GPU-h.
14. **DRAEM, SuperSimpleNet, Simple Copy-Paste:** benchmark baselines under the fixed protocol; report crack / inactive AP and relF1@2 on test and E1, and for Simple Copy-Paste the decoy test. No kill.

Suggested order: arms 1+2 and 3 in one sweep (day 1), arm 4 (day 2 to 3), arms 5 and 6 on CV (days 3 to 5). Stack winners only after each passes alone.

## 6. Rejected or demoted (one line each)

- arxiv:2110.05474 AEL adaptive CutMix / copy-paste: an SSL framework; its class-adaptive sampling is covered by arm 1, its paste by arms 3 and 5.
- doi:10.1109/cvpr46437.2021.00954 CutPaste: thin "scar" strips are an anomaly pretext; DRAEM and SuperSimpleNet already cover the benchmark slot.
- arxiv:2508.03143 SARD region-constrained diffusion: no numbers on the abstract page, no code; row 14 covers region-preserving insertion.
- arxiv:2609.35195 CarveMix-RC: BraTS-MET challenge entry, gains mixed with losses and post-processing; CarveMix itself is row 5.
- doi:10.1109/access.2025.3576335 SinGAN crack blending: pavement / pipe textures; DP and Cracktal give exact labels at lower cost.
- arxiv:2606.08033 masonry real / synthetic ratio: classification-style evidence (20% synthetic best), one data point for mixing ratios, not a mechanism.
- doi:10.32604/cmc.2026.088467 mask-guided copy-paste on 447 railway images: no numbers retrievable, same mechanism as CP100.
- arxiv:2609.37314 FLASH (VLM + generator, defect bank, blending): image-level F1 on MVTec AD 2; latent generation and blending, no thin-structure evidence.
- arxiv:2503.13985 DefectFill, arxiv:2507.02314 MAGIC, arxiv:2507.09619 GAA, doi:10.1109/cvpr52734.2025.02832 DualAnoDiff: latent-diffusion anomaly inpainting on MVTec; 8x latent downsampling blurs 1 to 2 px cracks; possible only for inactive (see D06 / D33).
- arxiv:2407.08151 context-aware copy-paste (BLIP + SAM + YOLO): RGB natural images, no numbers on the page.
- arxiv:2212.03863 X-Paste: CLIP / SD instances for natural-image instance segmentation.
- doi:10.1109/cvpr52733.2024.01580 RealNet (SDAS): anomaly-detection model; strength-controlled anomalies covered by D06 renderers.
- arxiv:2407.03961 DIAG: training-free latent inpainting on KSDD2 (+18% / +28% AP, R); latent blur; inactive only.
- doi:10.1109/access.2026.3731600 "MSDA effects are class dependent": classification; supports reporting per-class effects in the benchmark, no new arm.
- doi:10.1016/j.inffus.2024.102741 HSMix, arxiv:2007.07936 ClassMix: superpixel or SSL mixing; not class-aware for thin structures, ClassMix's SSL setting already n.d.

## 7. Gaps

- search_snippets never worked in either session (Semantic Scholar keyless pool rate-limited), so no passage-level check of Soft-CP blending details, Li et al.'s datasets, or LesionMix numbers.
- SuperSimpleNet full text timed out; its KSDD2 / mixed-supervision numbers are not read.
- No paper tests elastic or sub-pixel geometric augmentation on 1 to 2 px labels. Our label-safe rule stays; deform synthetic skeletons before rasterising instead.
- No paper on synthesis of isolated (inactive) regions in EL apart from D06's circuit model; arms 5 and 6 are our own construction from medical lesion methods.
- GDI is classification evidence. Whether removal-based hard negatives help pixel segmentation of thin cracks is untested anywhere I found; arm 4 is the decisive test.
- Official code not found for Synth4Seg, Soft-CP, ObjectAug, Li et al., Cut to the Mix (paper says public). All are short to implement.
