# D09: Crack segmentation architectures (pavement, concrete, steel), 2021 to 2026

Scout: D09 literature agent. First pass 12 Nov 2026, second pass 13 Nov 2026 (added RIFT, Fourier-morphology UDA, re-verified ids and code). Literature only: no servers, no test data read.
Labels: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Queries run

Research MCP `search_papers` (OpenAlex + arXiv answered; Scopus and ScienceDirect returned 401; Semantic Scholar was rate-limited in both passes, so every `search_snippets` call failed).

Pass 1 (12 Nov):
1. crack segmentation transformer (2020+)
2. crack segmentation Mamba state space (2024+)
3. OmniCrack30k universal crack segmentation benchmark (2020+)
4. CrackSeg9k crack segmentation dataset (2020+)
5. CrackFormer thin crack detection transformer (2020+)
6. thin crack segmentation high resolution (2021+)
7. segment anything crack segmentation adapter fine-tuning (2023+)
8. CrackFormer self-attention network fine-grained crack detection (2021 to 2023)
9. crack segmentation (2025+, min 15 citations)
10. curvilinear structure segmentation thin vessels cracks (2024+)
11. electroluminescence solar cell crack segmentation transformer (2022+)
12. local intensity order transformation robust curvilinear object segmentation (2021+)
13. diffusion model crack segmentation (2023+)
14. nnU-Net crack segmentation cross-dataset generalization (2022+)
15. DINOv2 crack segmentation foundation model (2024+)
16. crack segmentation noisy annotations inaccurate labels (2021+)
17. crack detection edge detection network pixel difference convolution (2021+)
18. hybrid CNN transformer crack segmentation fine-grained (2025+)
19. crack segmentation evaluation metric tolerance centerline IoU topology benchmark protocol (2022+)
20. crack segmentation domain generalization unseen datasets robustness (2025+)
21. crack segmentation transformer (2025+, min 5 citations)
22. SAM2-UNet Hiera encoder adapter U-Net segmentation (2024+)
23. fatigue crack segmentation steel images thin cracks (2022+)

Pass 2 (13 Nov): crack segmentation transformer (2020+); crack segmentation Mamba (2024+); OmniCrack30k universal crack segmentation (2020+); CrackFormer thin crack detection transformer; exact CrackFormer title; CrackSeg9k benchmark (2021+); thin crack segmentation high resolution tolerance metric (2021+); crack segmentation 2025 lightweight structure-aware (2025+); SAM fine-tuning crack adapter LoRA (2023+); crack benchmark cross-dataset generalization (2023+); crack inaccurate annotations label noise (2021+); crack DINOv2 foundation thin structures (2024+); EL solar cell crack transformer (2022+); curvilinear thin vessel crack topology (2025+); crack transformer hybrid (2025+, arXiv); dynamic snake convolution tubular crack (2023+); "Pushing the envelope of thin crack detection". Two further queries (DconnNet, Mamba thin-crack scanning 2025+) failed with HTTP 502.

Snowballing: `get_citations` on OmniCrack30k (43 citing) and SCSegamba (104 citing), both passes; `similar_papers` on CrackCue + Segment Any Crack + FMS2 (pass 1).
Full text read (arXiv copies): CrackCue (sections 3.2, 4.1, 4.3), RIFT (settings, main results, B.1, D.3 cross-dataset), FMS2 (3.2, 4.1, 4.2).
WebSearch (pass 1: 11, pass 2: 9): code checks for OmniCrack30k weights, CrackCue, FMS2, CrackSegFlow, Segment Any Crack, Hybrid-Segmentor, SAM2-UNet, SCSegamba, DSCNet, DconnNet, LIOT, CrackFormer-II, MixerCSeg.

Overlap with sibling directions: LIOT is in D11 / D12; FMS2 is in D06 / D11 / D12; CrackSegFlow is a D06 / D33 item; CoRe-SAM3, CrackSAM, UCS are D14 / D24 items; DconnNet is a D11 item. I keep crack-specific architectures here because they are the core of the benchmark method suite.

## 2. Three things that matter most for us (S)

1. **Cross-domain crack work speaks to E1; in-domain architecture work mostly does not.** Nearly every new crack architecture (Mamba, hybrid, mixer) is measured in-dataset on pavement sets with strict F1 / mIoU, gains of 1 to 3 points, and no evidence on 1 to 2 px jittered labels. The papers that train on one set and test on others (CrackCue, RIFT appendix D.3, Segment Any Crack, OmniCrack30k, the Fourier-morphology UDA paper) are the ones relevant to our E1 gap (crack IoU 0.47 to 0.15).
2. **Small data is normal in this literature.** CrackCue trains on CrackTree260 (260 images); FMS2 trains on 400 crack-centred patches per set; RIFT's sets (DeepCrack, CrackMap, CamCrack789, Crack500) are hundreds to low thousands. The crack-specific models are tiny (0.5 to 3 M parameters) and are trained from scratch. So our 478 cells are not unusually few; what is unusual is our 24-class head and label jitter.
3. **Tolerance metrics.** R: CrackCue (DeepCrack protocol) scores ODS / OIS / AP with a 3 px tolerance; OmniCrack30k reports clIoU at 4 px (clIoU4px); Rill-Garcia 2022 shows inaccurate annotations cost up to 20% F. RIFT and MixerCSeg report ODS / OIS plus "mIoU" that averages crack and background (so 0.85 there is not comparable with our crack IoU 0.47); tolerance for their ODS not stated in the parts read (unverified). SCSegamba, Hybrid-Segmentor and Segment Any Crack report strict F1 / IoU. S: our relF1@2 belongs to the detection tradition; the benchmark should report strict crack IoU, relF1@k and a clIoU@k, and must never average crack with background.

## 3. Selected papers

score = value for raising OUR numbers (rubric in the task); bench = value for the benchmark. Code: "verified" = repo named in the paper abstract or confirmed by web search; otherwise "unverified".

| # | id | year | venue | code | mechanism | adaptation to our data | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1061/jccee5.cpeng-7090 (Segment Any Crack, arXiv 2504.14138) | 2026 | J. Computing in Civil Eng. | unverified | Fine-tune only normalization affine parameters of a foundation model (plus head); beats full fine-tuning in-domain and on 3 zero-shot sets (OmniCrack30k IoU 0.441). | (a) house ResNet-34: freeze conv weights, train BN affine + decoder (a stricter PF); (b) frozen large encoder (SAM / DINOv3 ViT-L) with norm-only tuning and a U-Net++ style decoder, 24-class head. Targets E1, where PF already moved inactive 0.05 to 0.24. | 66 | 60 |
| 2 | doi:10.1016/j.patcog.2025.112107 (CrackCue, arXiv 2507.16851) | 2025 | Pattern Recognition | promised, not found | Max-pool (k=8) + upsample removes thin dark cracks; a skip-free encoder-decoder rebuilds a crack-free background (loss masked on dilated labels); abs(image minus background) is a cue channel concatenated to any segmenter. R: trained on 260 images, cross-dataset ODS +2.3 to +6.8 points at 3 px tolerance on U-Net, DeepCrack, CrackFormer; beats LIOT. | 1-channel EL fits the "thin and darker" prior. Dilate crack labels to about 5 px (FWHM 4 px); mask inactive too in the recon loss. Fingers and busbars are also thin dark lines: the recon net must learn to rebuild them, so inspect cue maps on mono vs multi and on half-cut / scuff E1-like pool cells before training. Second input channel to U-Net++ PF. | 64 | 55 |
| 3 | doi:10.1016/j.neucom.2022.01.051 (Rill-Garcia, Syncrack) | 2022 | Neurocomputing | unverified | Synthetic Syncrack set with controlled annotation errors; inaccurate annotations cut F by up to 20%; weakly-supervised label-noise correction recovers part of the loss. | Our crack labels are 1 to 2 px lines placed off the dark ridge. Run a correction loop on train crack labels only: fold-held-out models re-place label pixels onto the predicted ridge within 2 px, then retrain. Evaluate on original test labels (strict IoU) and relF1@2. | 60 | 50 |
| 4 | doi:10.1109/cvprw63382.2024.00392 (OmniCrack30k) | 2024 | CVPRW | weights unverified; dataset public per paper | 30k images from 20+ crack sets (asphalt, concrete, ceramic, masonry, steel); nnU-Net transfer learning wins with mean clIoU4px 64%, 10+ points above others. | (a) Pretrain the ResNet-34 U-Net++ crack channel on OmniCrack30k in grayscale, then PF fine-tune on EL so the pretraining survives (UCF-EL pretraining was erased by the house fine-tune). (b) nnU-Net v2 auto-configured on our 24 classes as a benchmark row. (c) Adopt clIoU@k as a benchmark metric. | 55 | 95 |
| 5 | doi:10.1007/s44267-025-00106-w (SAM2-UNet, arXiv 2408.08870) | 2026 | Visual Intelligence | verified: github.com/WZH0120/SAM2-UNet | SAM2 Hiera encoder with inserted adapters feeding a plain U-shaped decoder; strong on 5 dense tasks. | Gray to 3 channels; 512 px; Hiera-B+ or L. Hiera's first stage is stride 4, so add a full-resolution conv skip from the raw image or 1 to 2 px cracks are lost. 24-class head, house CE + Dice. Differs from the frozen Hiera-T linear probe in BRIEF section 5. | 55 | 80 |
| 6 | arxiv:2605.31048 (RIFT) | 2026 | arXiv | verified: github.com/xauat-liushipeng/RIFT (in abstract) | Crack segmentation as sparse structural recovery: local-evidence blocks, large directional strip kernels (k=13) that aggregate continuity along orientations, light multi-scale decoder; 0.47 to 1.69 M params. R: best or tied-best on 16 metrics over 4 sets, 3 seeds, BCE-Dice at 512 px; best cross-dataset average mIoU (77.0 vs SCSegamba 74.6, MixerCSeg 71.0). | Two uses. (a) Benchmark row: train RIFT-B on crack + inactive + background at 512 px, 1-channel stem. (b) Model arm: graft the directional strip block as a crack-only branch on the U-Net++ decoder at strides 1 and 2, or fuse RIFT crack logits with the house model (a heterogeneous ensemble, untested here). Watch strip kernels firing on busbars and fingers, which are long straight lines. | 50 | 80 |
| 7 | doi:10.1111/mice.70127 (Fourier-morphology UDA) | 2025 | Computer-Aided Civil and Infrastructure Eng. | unverified | Unsupervised domain adaptation for cracks: Fourier amplitude style transfer plus morphological operators that change crack width / geometry toward the target domain (two parameters), plus uncertainty-guided dual-network self-training on unlabelled target data; up to +18.5% F1 cross-domain. | Target = E1-like cells: the pool's 1,152 multi half-cells and CSIR cells. Fourier-swap labelled train cells toward half-cut / scuffed pool cells; morph crack labels to the CSIR width (1.75 px); then dual-network self-training with uncertainty masks on the pool. Score on E1 only after the recipe is frozen on F51 / H36 (val). | 50 | 40 |
| 8 | arxiv:2511.11015 (SUPER) | 2025 | arXiv | unverified | Wavelet-domain decoder block: perfect-reconstruction path with learned bounded suppression of high-frequency bands, replacing spatial upsampling in U-Net decoders. R: improves average IoU and the 0 to 2 px crack regime on FACS-Net. | Swap the U-Net++ decoder upsampling blocks for SUPER blocks; encoder unchanged. Report crack IoU binned by component width and size. Pure architecture, cheap. | 50 | 30 |
| 9 | arxiv:2501.18855 (FlexiCrackNet) | 2025 | arXiv | unverified | Task encoder-decoder plus a frozen EdgeSAM encoder as a generic feature extractor, fused by gated attention; better zero-shot and robustness. | Keep house ResNet-34 U-Net++; add a frozen side encoder (EdgeSAM or the DINOv3 ConvNeXt-T already on disk) fused at each skip by a learned gate. The frozen branch cannot be erased by fine-tuning: the PF lesson made structural. | 50 | 35 |
| 10 | arxiv:2606.23486 (PEPA, LNCS doi:10.1007/978-3-032-37627-5_22) | 2026 | LNCS | unverified | Post-encoder plug-in adapter for curvilinear segmentation: target-conditioned snake upsampling plus target-adaptive differentiable thresholding; 0.26 M params. | Attach to the PF decoder. The threshold half is a learned version of our val-chosen crack logit bias, so the snake upsampling half is the new part. | 46 | 30 |
| 11 | arxiv:2611.13511 (TMAL) | 2026 | arXiv | verified: github.com/suho-han/TMAL (in abstract) | Soft directional affinities at several offsets (weights emphasize thin regions) plus an auxiliary segmentation branch; best Dice / IoU / clDice on DeepCrack and DRIVE, lower component error. | Add an affinity head for crack only (offsets 1, 2, 4 px, 8 directions) on U-Net++; final crack map fuses affinity and seg branch. Jitter makes 1 px offsets noisy, so weight larger offsets more. Distinct from Skeleton Recall / clDice (losses, tested). | 45 | 40 |
| 12 | doi:10.1016/j.autcon.2026.107190 (CrackGeoFM, arXiv 2606.05641) | 2026 | Automation in Construction | unverified | Frozen foundation backbone + frequency-guided crack enhancement + crack-domain adapter + multi-task decoder (mask, skeleton, uncertainty); SOTA across 20 crack sets, few-shot with 5 images. | Frozen DINOv3 / SAM2 encoder, 24-class mask head + crack skeleton head + aleatoric head. The uncertainty head gives calibrated crack confidence for the severity step. Skeleton head partly overlaps Skeleton Recall (tested). | 44 | 50 |
| 13 | doi:10.1016/j.autcon.2024.105960 (Hybrid-Segmentor, arXiv 2409.02866) | 2025 | Automation in Construction | verified: github.com/junegoo94/Hybrid-Segmentor (weights + CrackVision12K) | CNN path for fine local detail plus transformer path for global crack pattern, fused decoder; trained on 13 merged sets; IoU 0.631, F1 0.774 (strict). | Benchmark baseline with public crack weights. Crack-only: init from their weights, add our head; gray to 3 channels. Expect weaker "other classes" than U-Net++. | 42 | 65 |
| 14 | doi:10.1109/cvpr52734.2025.02738 (SCSegamba, arXiv 2503.01113) | 2025 | CVPR | verified: github.com/Karl1109/SCSegamba | Lightweight vision Mamba (2.8 M params): gated bottleneck conv for morphology plus structure-aware scanning for continuity; F1 0.839, 2-class mIoU 0.848 on a multi-scenario set. | Must-have benchmark entry (most cited 2025 crack segmenter, 104 citations). Needs mamba-ssm CUDA kernels (install needs the user's OK). Train crack + inactive + background and 24-class variants from scratch at 512 px. | 40 | 90 |
| 15 | doi:10.1016/j.autcon.2024.105845 (CrackMamba, arXiv 2410.19894) | 2024 | Automation in Construction | verified: github.com/shengyu27/CrackMamba (in abstract) | ImageNet-pretrained VMambaV2 encoder, snake-scan reshaping of feature sequences, snake-conv VSS blocks; SOTA on CrackSeg9k and SewerCrack. | Pretrained encoder matters at 478 images, so this is the Mamba entry most likely to compete. Gray to 3 channels, 24-class decoder, house loss, PF-style encoder lr. | 40 | 55 |
| 16 | arxiv:2603.01361 (MixerCSeg) | 2026 | arXiv (CVPR 2026 per first pass, unverified) | verified: github.com/spiderforest/MixerCSeg (in abstract) | One encoder that splits into CNN-like local, transformer-like global and Mamba-like sequential paths (TransMixer), plus direction-guided edge-gated conv; 2.54 M params. | Benchmark entry as a newest crack-specific SOTA. Same adaptation as SCSegamba. R (from RIFT): weaker cross-dataset transfer than SCSegamba (71.0 vs 74.6). | 36 | 75 |
| 17 | doi:10.22260/isarc2025/0140 (DSCformer, arXiv 2411.09371) | 2025 | ISARC | unverified (DSConv itself: DSCNet, ICCV 2023, arXiv 2307.08388, code per web search) | Dual branch: enhanced dynamic snake convolution plus SegFormer; IoU 59.22 on Crack3238. | Snake convs are on BRIEF's never-tried list. Replace the last two U-Net++ decoder conv blocks with DSConv for crack features; keep the encoder. | 36 | 35 |
| 18 | arxiv:2610.14274 (Inspect Any Crack) | 2026 | arXiv | unverified | SACv2-Tiny segmenter (OmniCrack30k IoU 0.455, zero-shot F1 0.699), then width and area from masks, and a bounded Crack Severity Index (0 to 100) from max width and affected-area ratio; 7.33% width error at 41 caliper points. | Template for the severity step: replace width (meaningless on EL, the crack is sub-pixel) with crack length, crack mode (dendritic / parallel to busbar / cross) and isolated-area fraction, combined into a bounded index checked against inactive area. | 15 | 55 |

## 4. Minimum experiments

All on house U-Net++ ResNet-34 PF unless said; 3 seeds per arm; decide on module-grouped 5-fold CV over the 532 train + val cells and on E1; clean-49 test as secondary. "n.d." under the team seed rule.

1. **Norm-only tuning (row 1)**: arms (a) BN-affine-only encoder + full decoder, (b) DINOv3 ViT-L frozen, LN-only tuning, U-Net++ style decoder; baseline PF. Metric E1 crack relF1@2 and E1 inactive IoU, CV crack IoU. Kill if neither arm beats PF by +0.03 E1 relF1@2 or +0.05 E1 inactive IoU with CV crack IoU within 0.01. About 15 GPU-h.
2. **CrackCue (row 2)**: arm 2-channel input (EL, cue), recon net trained on train folds; baseline PF. Metric E1 crack relF1@2 and recall; CV crack IoU. Kill if E1 relF1@2 gain < +0.03 or CV crack IoU drops > 0.01. Add a LIOT input arm (D11 / D12) in the same batch. About 10 GPU-h.
3. **Label correction (row 3)**: arm train on ridge-snapped crack labels (2 rounds, fold-held-out proposals within 2 px); baseline PF on original labels. Metric strict test crack IoU on original labels, relF1@2. Kill if strict IoU drops > 0.01 and relF1@2 n.d. About 25 GPU-h.
4. **OmniCrack30k (row 4)**: arm crack-binary pretraining on OmniCrack30k (gray, 512 crops, 20k steps) then PF fine-tune; baseline PF from ImageNet. Metric E1 crack relF1@2, CV crack IoU, CV components >= 20 px found. Kill if E1 relF1@2 < +0.02 and CV crack IoU n.d. Separately nnU-Net v2 on 24 classes as a benchmark row. About 25 + 40 GPU-h.
5. **SAM2-UNet (row 5)**: arm Hiera-B+ with adapters, U-Net decoder, extra full-res skip, 24 classes; baseline PF. Metric CV crack IoU, E1 crack relF1@2, mIoU_rob. Kill if CV crack IoU < PF minus 0.01 and E1 n.d. About 20 GPU-h.
6. **RIFT (row 6)**: arm A = RIFT-B, 3 classes, 1-channel stem, official recipe at 512 px; arm B = PF + RIFT crack logits averaged (heterogeneous ensemble); baseline PF single and PF 2-seed ensemble (same member count as arm B). Metric CV crack IoU, E1 crack relF1@2. Kill arm A as a model if CV crack IoU < PF minus 0.02 (keep as benchmark row); kill arm B if it does not beat the 2-seed PF ensemble by +0.01 CV crack IoU or +0.03 E1 relF1@2. About 12 GPU-h.
7. **Fourier-morphology UDA (row 7)**: arm FDA-style amplitude swap toward pool half-cells + label width morphing + uncertainty-gated dual-network self-training on 11.9k pool; baseline PF. Metric E1 crack relF1@2 and recall, E1 inactive IoU; CV crack IoU must stay within 0.01. Kill if E1 relF1@2 < +0.03. Note the BRIEF Mean Teacher pool run was n.d. on test, not aimed at E1. About 30 GPU-h.
8. **SUPER (row 8)**: arm SUPER decoder blocks; baseline PF. Metric crack recall on components under 20 px, CV crack IoU. Kill if small-component recall gain < +0.03. About 8 GPU-h.
9. **Frozen side encoder (row 9)**: arm house + frozen DINOv3 ConvNeXt-T side encoder with gated fusion; baseline PF. Kill as in 1. About 12 GPU-h.
10. **PEPA snake upsampling (row 10)**: arm TCSU on PF decoder, thresholding off (bias known); baseline PF + val bias. Metric CV crack IoU. Kill if < +0.01. About 10 GPU-h.
11. **TMAL head (row 11)**: arm U-Net++ + multi-offset affinity head for crack; baseline PF. Metric CV components >= 20 px found, relF1@2, strict IoU. Kill if components found gain < +0.02 and IoU n.d. About 10 GPU-h.
12. **CrackGeoFM uncertainty head (row 12)**: arm aleatoric crack head; baseline PF. Metric crack ECE within 2 px, CV crack IoU unchanged. Kill if ECE not lower. About 20 GPU-h.
13. **Hybrid-Segmentor, SCSegamba, CrackMamba, MixerCSeg (rows 13 to 16)**: official code, 3 classes and 24 classes; baseline PF. Metric CV crack IoU, relF1@2. Kill as models if CV crack IoU < PF minus 0.02; keep all as benchmark rows. About 10 to 12 GPU-h each.
14. **DSConv decoder (row 17)**: arm DSConv in last two decoder blocks; baseline PF. Kill if CV crack IoU < +0.01 and components found n.d. About 10 GPU-h.
15. **Severity index (row 18)**: post-hoc on PF predictions; compare index between cells with and without inactive. Inference only.

## 5. Notable papers rejected (one line each)

- CrackFormer (doi:10.1109/iccv48922.2021.00376) and CrackFormer-II (doi:10.1109/tits.2023.3266776): superseded; R (CrackCue table 1) CrackFormer transfers worse than U-Net cross-dataset; classic benchmark row only if code is found (repo unverified).
- FMS2 / SegFlow (arxiv:2603.13659): flow-matching image to mask transport, mean IoU 0.511 to 0.599 over 5 thin-structure sets with 400 training patches each; a real bold bet, but no public code (promised after acceptance) and covered by D06 / D11 / D12.
- CrackSegFlow / CSF-50K (doi:10.1016/j.autcon.2026.106938): mask-to-image flow-matching synthesis, +13.0 mIoU cross-domain; a data method, belongs to D06 / D33; code not found.
- CoRe-SAM3 (arxiv:2609.05816): SAM3 crack adaptation with 18.9 K trainable parameters, crack IoU 62.3 to 70.5 over 5 domains; belongs to D14 / D24.
- CrackSAM (doi:10.1016/j.conbuildmat.2024.136573): SAM adapter / LoRA; same family as rows 1 and 5.
- Loss function inversion, steel bridges (doi:10.1016/j.autcon.2024.105896): background-patch loss against crack-like false positives; we train on whole cells; the useful finding (bigger patches and global context help) is already our setup.
- Pushing the Envelope of Thin Crack Detection (arxiv:2101.03326) and Weakly-Supervised Crack Detection (doi:10.1109/tits.2023.3286934): sub-pixel / weak-label crack training on concrete; relevant to D13 / D15 rather than architecture.
- LIOT (doi:10.1109/tip.2022.3155954): folded into experiment 2 as a comparison arm; covered by D11 / D12.
- DconnNet (CVPR 2023, code github.com/Zyun-Y/DconnNet per web search): directional connectivity; FMS2 table shows it below Mask2Former on two of three crack sets; covered by D11.
- CrackSegDiff, CrossDiff, CrackdiffNet, Crack Diffusion Model: diffusion segmenters, slow, no small-data or thin-label evidence.
- EfficientCrackNet, LiteCrackSeg, CrackScopeNet and other lightweight models: optimise speed, not accuracy.
- CrackSeg9k (doi:10.1007/978-3-031-25082-8_12): OmniCrack30k supersedes it.
- Cracks in the Foundation, CiF (arxiv:2605.18413): 150k civil tiles; benchmark-design reference (specialised models plateau at about 25% mAP) but RGB instance data, far from EL.
- Many 2025 to 2026 MDPI / Sci. Rep. hybrid CNN-transformer / Mamba variants (Crack-ConvT, SGL-Mamba, CONTI-CrackNet, CCMamba, LiBiNet, SECrackSeg): in-dataset pavement gains of 1 to 3 points, no distinct mechanism beyond rows 6 and 13 to 16.
- EL papers found (SEiPV-Net, instance segmentation benchmark doi:10.1016/j.solener.2025.114083, MultiSolSegment): D01 / D02 items, not crack architectures.

## 6. Gaps

- Semantic Scholar was rate-limited in both passes: no snippet-level check of which crack papers use tolerance metrics beyond CrackCue (3 px), OmniCrack30k (clIoU 4 px) and Rill-Garcia. Re-run "tolerance" snippet queries for SCSegamba, MixerCSeg, RIFT, Hybrid-Segmentor before the benchmark protocol is fixed.
- OmniCrack30k full text and nnU-Net weights not retrieved (IEEE, off campus; no official repo found). Need the clIoU4px definition to copy it exactly.
- FACS-net and CT-loss (doi:10.1016/j.autcon.2025.106719): thin-crack network plus topology loss for 0 to 2 px cracks; abstract not retrievable; worth a dedicated look.
- No crack architecture paper tests on a few hundred images with 1 to 2 px jittered labels from several sources plus a 24-class head. Every row's evidence comes from a different regime; this is why most scores sit at 40 to 66.
- Source-conditional prediction (ARTS 1.5 px vs SDLE 3.25 px label conventions) is not addressed by any crack paper found (D17 territory).
- Mamba rows (14 to 16) need mamba-ssm CUDA kernel builds; confirm the user allows installs on cv02. RIFT (row 6) is plain PyTorch convolution and avoids this.
- Frequency-aware anisotropic serialization for thin-structure SSMs (arxiv:2603.28503) found via SCSegamba citations; abstract not retrievable.
