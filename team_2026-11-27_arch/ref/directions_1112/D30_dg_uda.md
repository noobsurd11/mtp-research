# D30 Domain generalisation and unsupervised domain adaptation for segmentation

Scout: D30 literature agent, 13 Nov 2026. Labels: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 0. Framing for our data (S)

- E1 gap (crack IoU 0.47 -> 0.15) is a layout + confounder shift inside the same sources (101 of 106 E1 cells are CSIR, the same camera family as train). It is not mainly a global style shift. 58 E1 cells are half-cut; training has 0. 75% of E1 crack pixels sit in 20 half-cut cells with scuff streaks (recall 0.13 there); 70% of E1 crack pixels get p(crack) < 0.001.
- So pure appearance randomisation (style, Fourier, random conv) is only half the fix. The other half is (a) target-like unlabelled data that already exists, and (b) breaking spurious "context -> label" rules (a crack needs a full-cell layout around it; a dark streak means "not crack").
- Target-like unlabelled data exists: the server pool has 1,152 multi half-cells (CSIR / ARTS). That makes E1 a real UDA problem with an unlabelled target proxy, which BRIEF section 5 lists as NOT closed ("UDA-style methods aimed at E1 with target-like data").
- Hard rule for every arm below: E1 images are never used as UDA target data and never used for checkpoint or threshold selection. Target = pool half-cells (+ optionally pool CSIR full cells). Selection = val 54 / F51 (+ H36 for inactive only; H36 crack labels are speck-level).
- Baselines: house model and PF variant, same 20k steps, 3 seeds minimum per arm (5 if the first 3 pass). Primary metric for this direction: E1 crack relF1@2 and E1 crack IoU / recall; guard metric: test-clean-49 crack IoU and mIoU_rob (must not drop by more than 0.01).

## 1. Queries run

Research MCP search_papers (year_from 2020 unless stated; limit 10 to 20):
1. domain generalized semantic segmentation
2. masked image consistency domain adaptation semantic segmentation
3. single source domain generalization medical image segmentation
4. style randomization augmentation segmentation domain generalization
5. HRDA high-resolution domain adaptive semantic segmentation DAFormer (2021+)
6. domain generalization crack segmentation unseen domain
7. retinal vessel segmentation domain generalization thin structures unseen dataset (2021+)
8. vision foundation model DGSS parameter-efficient fine-tuning (2025+)
9. Fourier domain adaptation amplitude spectrum swap segmentation
10. electroluminescence solar cell defect domain adaptation cross-dataset (nothing DG-specific for EL found)
11. rare class sampling cross-domain mixing self-training segmentation
12. unsupervised domain adaptation semantic segmentation (2025+)
13. single domain generalization segmentation data augmentation (2025+)
14. spurious correlation shortcut background confounder segmentation counterfactual augmentation (2021+)
15. test-time adaptation semantic segmentation distribution shift (2023+)
16. industrial defect segmentation domain adaptation unseen product (2021+)
17. progressive random convolutions single domain generalization
18. unsupervised domain adaptation crack segmentation self-training (2022+)
19. domain generalized semantic segmentation depth foundation model tokens frozen (2025+)
20. semi-supervised domain generalization segmentation unlabeled target-like data (2022+)
21. geometric shift layout shift domain adaptation segmentation spatial prior (2021+)
22. SWAD domain generalization flat minima weight averaging

search_snippets: 2 attempts (MIC thin-class evidence), both rate-limited by Semantic Scholar; evidence taken from full text instead.
Snowballing: get_citations on MIC (30 citing papers); similar_papers on CIDG (2111.12525) + SLAug (2211.14805).
Full text read: MIC (2212.01322), CIDG GIN+IPA (2111.12525), CrackSegFlow (2601.03637, already in library). Fourier-morphology crack UDA (mice.70127): no open copy, abstract only.
WebSearch (9): 2025 DGSS VFM methods; Rein repo; MIC repo; CIDG repo; DGInStyle repo; Pro-RandConv repo; MiDSS repo; FDA repo; SoMA repo; 2025-2026 thin-structure DG.

## 2. Selected papers

Score = value for raising OUR scores (rubric in task). Bench = value for the benchmark suite / protocol.

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | arxiv:2111.12525 (GIN + IPA, Ouyang et al.) | 2022 | IEEE TMI | official repo not found (unverified); ~60 lines to write | Random shallow conv nets (4 layers, 2 hidden ch.) re-map intensity/texture each step (GIN); two GIN outputs are blended with a smooth random spatial map (IPA) so neighbouring regions get independent appearance, cutting confounder-to-label shortcuts; KL consistency between the two views | 1-ch EL fits directly (designed for gray MRI/CT). Use 1x1 or 3x3 kernels only (3x3 can blur 1-2 px cracks: cap blend alpha, never wider). IPA control lattice at 8 to 16 cells per 512 px so that streak-like regions (scuff analogue) get their own appearance. No geometry change, so 1-2 px labels stay aligned. Apply to crack/inactive images too, keep house aug on top | 72 | 55 |
| 2 | arxiv:2211.14805 (SLAug) | 2023 | AAAI | github.com/Kaiseem/SLAug (from paper abstract) | Global and class-wise random Bezier intensity curves (location-scale per class region), fused with a saliency map from the gradient so augmentation lands where the model relies on it | Class-wise curves only on structural classes (busbar, ribbon, gridline, border, background, padding, frame). Never on crack or inactive: with 1 px jittered labels a class-wise transform paints a line at the label, not at the dark ridge, and teaches a shortcut. Expected effect: crack must be found under any busbar/background contrast, which is what CSIR half-cuts change | 65 | 50 |
| 3 | arxiv:2212.01322 (MIC) | 2023 | CVPR | github.com/lhoyer/MIC (verified by web) | UDA plug-in: EMA teacher labels the full target image, student must predict the same from a patch-masked target image, forcing context use. R: +1.2 to +4.7 mIoU across UDA methods on GTA->CS; largest gains on thin/low classes pole, traffic sign, fence; mask patch 64, ratio 0.7 best; only +0.3 in plain supervised training | Target = 1,152 pool half-cells (not E1). Patch 32 to 64 px at 512 px, ratio 0.5 to 0.7. Teacher confidence weighting is essential (R: -1.6 without); for crack use a lower threshold or tolerant pseudo-labels since crack pixels are <1%. Risk (S): the teacher sees 70% of E1-like cracks at p<0.001, so pseudo-labels miss them; MIC helps only if context, not local contrast, is what fails | 58 | 80 |
| 4 | arxiv:2111.14887 (DAFormer) + arxiv:2304.13615 (TPAMI DG extension) | 2022 / 2023 | CVPR / TPAMI | github.com/lhoyer/MIC contains DAFormer/HRDA (verified); DAFormer repo itself unverified | Recipe: MiT transformer encoder + context-aware fusion decoder, rare class sampling (RCS), ImageNet feature-distance regulariser, LR warmup; DACS cross-domain mixing self-training. TPAMI extension shows the same recipe as a DG method | RCS: sample training cells by rarity of crack / inactive / splice / gridline (only 42 inactive cells). FD regulariser is a cousin of PF (keeps ImageNet features); PF already showed encoder preservation helps E1 inactive 0.05 -> 0.24, so FD is a soft version worth one arm. MiT-B5 at 512 px, 1-ch input replicated to 3 | 55 | 85 |
| 5 | doi:10.1111/mice.70127 (Fourier-Morphology blending + uncertainty self-training, crack UDA) | 2025 | Comput.-Aided Civil Infrastr. Eng. | unverified | Fourier low-frequency style transfer plus morphological operators that match crack width/geometry between domains (2 parameters), then dual-network uncertainty-guided self-training on target. R: up to +18.5% F1 over baselines cross-domain | The morphology half is the novel bit for us: our label width differs by source (ARTS 1.5 px, BMRK 3.0, SDLE 3.25). Dilate/erode source crack labels toward the target convention while swapping low-frequency amplitude from pool half-cells. Self-training half overlaps BRIEF s5 pseudo-label SSL (n.d. at 100%); test the blending half first | 58 | 45 |
| 6 | arxiv:2004.05498 (FDA) | 2020 | CVPR | YanchaoYang/FDA (from paper footnote via web; repo not opened) | Swap the low-frequency amplitude spectrum of a source image with that of a random target image; phase (edges, cracks) kept | Zero-cost: beta 0.01 to 0.05, target amplitudes from pool half-cells and CSIR cells. Cracks are high-frequency, so labels stay valid. Covers module-level illumination, vignetting, contrast. Does not model scuff streaks (spatial, mid-frequency); expect inactive and CSIR gains more than crack | 52 | 55 |
| 7 | arxiv:2404.08951 (MiDSS) | 2024 | CVPR | github.com/MQinghe/MiDSS (verified by web) | Labelled data from one domain, unlabelled from many: unified copy-paste between labelled and unlabelled images builds intermediate domains, plus training-progress-aware random amplitude mixup and symmetric guidance. R: +13.57% Dice on Prostate over SOTA | Exactly our pool shape (478 labelled full cells; unlabelled pool mixes mono, multi, half-cells). Copy-paste half-cell regions (with cut line and scuffs) into labelled full cells and labelled crack regions into half-cells. Overlap: BRIEF s5 MT + CutMix + external pool was n.d. at 100%; the new parts are amplitude mixup and the half-cell target, so only one arm | 48 | 45 |
| 8 | arxiv:2304.00424 (Pro-RandConv) | 2023 | CVPR | not found (unverified) | Repeatedly apply one small random conv block (with deformable offsets and affine) to grow augmentation strength progressively without losing semantics | Drop or zero the deformable offsets (they shift 1-2 px cracks off their labels). Use as an alternative to GIN in the same arm family; pick whichever survives val. Used inside the IDA 2026 industrial defect winner-style pipeline (row 9) | 45 | 40 |
| 9 | arxiv:2610.19540 (IDA 2026 cross-scenario industrial defects) | 2026 | arXiv (challenge report) | github.com/GZHU-DVL/Dikai (from abstract) | Cross-scenario robust normalisation, DSU-style feature-statistic perturbation, Pro-RandConv, NWD loss for small defects, VFL score calibration, SWAD variant with metric-aligned checkpoint selection. R: Track 1 score 0.564 on a hidden test; no per-module ablation in abstract | Closest domain in this search (boards with surface contaminants = our scuffs). Take DSU (feature-stat perturbation in encoder layer1/2) and metric-aligned checkpoint selection on val relF1@2, not loss. Detection-specific parts (NWD, VFL) do not transfer | 45 | 40 |
| 10 | arxiv:2102.08604 (SWAD) | 2021 | NeurIPS | unverified | Dense stochastic weight averaging over the low-loss region of training gives flatter minima and better unseen-domain accuracy | BRIEF s5: EMA / SWA never varied. Average weights every 200 steps from step 10k to 20k (BN recomputed on train). Near-free; may also cut the "1 run in 6 is wrecked" seed variance. Compare to 5-seed ensemble gain (+0.014 to +0.018 crack IoU) | 55 | 50 |
| 11 | arxiv:2312.04265 (Rein) + arxiv:2508.01667 (Rein++) | 2024 / 2026 | CVPR / TPAMI | github.com/w1oves/Rein (verified by web) | Learnable instance-aware tokens refine every layer of a frozen VFM (DINOv2/EVA02/SAM), <1% params; Rein++ adds UDA (Rein-A) and SAM boundary transfer. R: DGSS SOTA on GTA/CS -> unseen sets | BRIEF s5: frozen probes and one ConvNeXt-T fine-tune showed no gain; ViT-L + Rein is untested. Patch 14 at 512 px gives 37x37 tokens, too coarse for 1-2 px cracks: run at 1022-1036 px input or fuse with the U-Net++ detail decoder. Rein-A target = pool half-cells | 48 | 85 |
| 12 | arxiv:2412.04077 (SoMA) | 2025 | CVPR | github.com/ysj9909/SoMA (from arXiv HTML via web) | Fine-tune only the minor singular components of each weight, freeze the major ones and early DG-friendly blocks, annealed weight decay | Same spirit as PF (keep pretrained encoder) but finer. Apply to ResNet-34 conv weights (SVD on reshaped kernels) or to a DINOv2/v3 backbone. Cheap way to test "encoder preservation" beyond PF | 42 | 60 |
| 13 | arxiv:2601.03637 (CrackSegFlow) | 2026 | Automation in Construction | unverified | Mask-conditioned flow-matching renderer for thin cracks; background-guided crack injection into crack-free backgrounds to expose confounders; target-guided mask statistics. R: cross-domain +13.0 mIoU / +14.7 F1 averaged over 5 crack sets; CFD-source avg 21.7 -> 42.5 mIoU | Bold bet. Train the renderer on our 209 crack cells, inject masks into pool half-cells with scuff streaks -> labelled half-cut + scuff crack data, the exact E1 condition training lacks. Overlap: crack copy-paste onto pool cells was n.d. (more decoys) and synthetic half-cut views n.d.; learned rendering (realistic crack contrast in scuff context) is untested | 45 | 30 |
| 14 | arxiv:2501.03466 (DGSSA) | 2025 | Neural Networks | unverified | Structural aug (space-colonisation synthetic vessel trees rendered with Pix2Pix) + PixMix stylistic aug with uncertainty perturbation, for thin-vessel DG. R: avg DSC 77.98 across 4 fundus sets | PixMix half is cheap: mix EL cells with fractal/pool images at low weight. Structural half = synthetic crack trees (branching, dendritic) rendered into cells; overlaps row 13 | 40 | 35 |
| 15 | arxiv:2512.01510 (semantic-aware RandConv + source matching) | 2026 | IEEE Access | github.com/imigraz/SRCSM_Domain_Generalization (from abstract) | Different random convs per labelled region at train time; at test time map target intensities toward source | Train half is a RandConv version of SLAug (row 2), same crack/inactive exclusion rule. Test-time intensity mapping overlaps BRIEF s5 "intensity normalisation (fail)", so skip it | 38 | 35 |
| 16 | arxiv:2312.03048 (DGInStyle) | 2024 | ECCV | github.com/prs-eth/dginstyle (verified by web) | Fine-tune latent diffusion + ControlNet on source masks, generate mask-aligned images with style swap and multi-resolution latent fusion; trains DG segmenters. R: up to +2.5 mIoU over prior DG SOTA | Moonshot: SD is RGB natural-image prior; needs fine-tuning on 478 + pool EL cells; multi-resolution fusion matters for thin cracks. Likely covered by the generative-data direction; listed because it is the reference DG-by-generation baseline | 30 | 55 |
| 17 | arxiv:2204.13132 (HRDA) | 2022 | ECCV | in lhoyer/MIC repo (verified) | Low-res context crop + high-res detail crop with learned scale attention; UDA self-training on both | Our images are 512 px; HRDA only pays off with native-resolution pool sources (1200 px). 2x input was n.d. at 4x compute (BRIEF s5); HRDA is the cheaper form of the same idea. Benchmark baseline value is higher than score value | 30 | 70 |

## 3. Minimum experiments (one per row; all 3 seeds, judged on E1 crack relF1@2 and recall, guarded by test-clean-49 crack IoU and mIoU_rob; selection never on E1)

1. GIN+IPA: PF + GIN/IPA (p=0.5, alpha~U(0,1)) vs PF. Kill if E1 crack relF1@2 gain < +0.03 or test crack IoU drops > 0.01. ~4 GPU-h.
2. SLAug structural-only: PF + SLAug (crack/inactive excluded) vs PF. Same kill line. ~5 GPU-h.
3. MIC: PF + MIC (target pool half-cells, patch 64, r 0.7) vs PF and vs PF + EMA-teacher self-training without masking (isolates masking). Kill if E1 crack relF1@2 gain < +0.03 over the no-mask arm. ~12 GPU-h.
4. DAFormer recipe: (a) house + RCS; (b) house + FD regulariser vs PF. Kill (a) if test inactive IoU and E1 inactive IoU gains < +0.02; kill (b) if not better than PF on E1. ~8 GPU-h. MiT-B5 DAFormer only as a benchmark entry.
5. Fourier-morphology: PF + FDA(pool half-cells) + label width matching to CSIR (1.75 px) vs PF + FDA. Kill if no E1 IoU gain >= 0.02 at equal relF1@2. ~6 GPU-h.
6. FDA: PF + FDA beta in {0.01, 0.03} vs PF. Kill if E1 inactive and crack relF1@2 both < +0.02. ~6 GPU-h.
7. MiDSS: PF + UCP + TP-RAM (pool half-cells) vs PF + MT/CutMix (the BRIEF s5 config). Kill if E1 crack relF1@2 gain < +0.03. ~15 GPU-h.
8. Pro-RandConv (no offsets) vs GIN arm; keep whichever is better on val/F51. ~4 GPU-h.
9. DSU feature perturbation in layer1-2 on PF vs PF. Kill at < +0.03 E1 relF1@2. ~4 GPU-h.
10. SWAD: PF + dense averaging 10k-20k vs PF final checkpoint. Kill if test crack IoU gain < +0.01 and E1 relF1@2 gain < +0.02. ~4 GPU-h (no extra training, just checkpoint saves).
11. Rein: DINOv2-L (or DINOv3-L) + Rein + Mask2Former at ~1024 px input vs PF U-Net++. Kill if test crack IoU < 0.45 or E1 relF1@2 not > PF. ~40 GPU-h.
12. SoMA on ResNet-34 vs PF. Kill if E1 inactive IoU < PF and crack unchanged. ~4 GPU-h.
13. CrackSegFlow-style injection into 2,000 scuffed half-cells (+ real) vs PF. Kill if E1 crack recall in scuff cells gain < +0.10 or test crack precision falls > 0.03. ~60 GPU-h (renderer + seg runs).
14. PixMix half of DGSSA vs PF. Kill at < +0.02 E1 relF1@2. ~4 GPU-h.
15. As row 2 with RandConv per region; run only if row 2 passes.
16. DGInStyle: only after row 13 shows synthetic half-cuts help. ~150 GPU-h.
17. HRDA: benchmark entry only; score run only if native-res pool crops are prepared for another direction.

## 4. Notable papers rejected (one line each)

- arxiv:2504.12753 DepthForge (2025): relies on Depth Anything geometry; EL cells are flat, depth cue is meaningless.
- arxiv:2504.03193 Mamba as a Bridge (CVPR 2025) and Causal-Tune arxiv:2512.16567: VLM/CLIP text priors on driving classes; no text semantics for EL classes; covered by Rein row for the benchmark.
- doi:10.1109/cvpr52733.2024.01063 VPTTA: per-image low-frequency prompt trained by BN-statistics alignment, close to per-panel BN adaptation which failed (BRIEF s5).
- arxiv:2309.13604 and other continual TTA: video / changing-stream setting, no stream in our use.
- doi:10.1111/mice.13315 Bayesian self-training with spatial priors (crack UDA): spatial prior is concrete-wall specific; self-training part overlaps BRIEF s5 SSL.
- arxiv:2412.15637 CrackUDA: incremental UDA for civil-structure datasets; adversarial alignment, weaker than MIC-style self-training on our setting.
- doi:10.1109/cvpr46437.2021.00682 FSDR and arxiv:2212.00979 Pasta: frequency randomisation for synthetic-to-real; FDA row covers the mechanism with real target spectra available.
- arxiv:2409.04768 RAS3, arxiv:2405.01228 RaffeSDG, arxiv:2307.09005 FreqMix: medical Fourier SDG variants; same mechanism family as FDA/GIN, keep as fallbacks only.
- doi:10.1109/cvpr52688.2022.00970 WildNet, doi:10.1109/cvpr46437.2021.01141 RobustNet: whitening / wild-style with ImageNet content; designed for RGB street scenes, superseded by VFM methods.
- arxiv:2603.13659 FMS2: flow-matching segmentation head is an architecture change (other direction); its synthesis half is covered by row 13.
- arxiv:2501.04741 "one image as one domain": per-image style decoupling with weak evidence and no code found.

## 5. Gaps

- No DG or UDA paper on EL, PL or any PV imaging was found; all evidence is from driving, medical, concrete cracks or industrial boards.
- No paper studies a pure layout shift (cell cut geometry) with fixed style. The closest are IPA (spurious context) and MIC (context learning). A cheap internal diagnostic is missing: run the PF model on E1 cells with the scuff region inpainted or with the half-cut region mirrored to a full-cell layout, to split "layout" from "confounder" error before choosing among rows 1, 3, 13.
- Shape-bias / texture-debias methods for thin structures (e.g. stylised-ImageNet-style pretraining on gray images) were not searched in depth.
- Semantic Scholar snippet search was rate-limited all session; per-class thin-structure evidence for SLAug, GIN and FDA comes from abstracts only.
- Benchmark design (S): E1 should be reported as a separate unseen-module track with a fixed "no target images, no E1 selection" rule and an optional UDA track whose only allowed target data is the public unlabelled pool. DGSS literature (Rein, MIC, DAFormer) always reports source-only and adaptation tracks separately; the EL benchmark should do the same.
