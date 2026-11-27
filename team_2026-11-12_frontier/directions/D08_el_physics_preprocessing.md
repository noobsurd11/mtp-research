# D08: EL image formation, preprocessing and physics priors

Scout: D08 literature agent. First pass 12 Nov 2026, revised 13 Nov 2026 (re-run: every id below was re-retrieved by a tool in the 13 Nov session; new items added, unverified rejects dropped).
Literature phase only: no servers, no GPUs, no test or E1 predictions read.
Labels: R = what the paper measured, E = what our files measured (from BRIEF), S = my judgement.

## 1. Queries run

Research MCP `search_papers` (30 on 13 Nov; Scopus and ScienceDirect returned HTTP 401 and Semantic Scholar was rate-limited almost all session, so hits are mostly OpenAlex / arXiv):
1. electroluminescence image preprocessing solar cell segmentation perspective correction (2020+)
2. electroluminescence image enhancement photovoltaic (2020+)
3. half-cut cell electroluminescence defect detection (2020+)
4. micro-crack detection solar cell anisotropic diffusion electroluminescence (2015+)
5. busbar finger removal electroluminescence crack detection frequency domain (2012+)
6. vesselness Frangi filter input channel crack segmentation deep learning (2020+)
7. electroluminescence solar cell crack detection (2025+)
8. multi-bias electroluminescence images low current high current defect quantification (2018+)
9. electroluminescence image denoising super-resolution photovoltaic module (2019+)
10. scratch marks electroluminescence photovoltaic module glass backsheet artifact (2015+)
11. golden template reference image subtraction defect detection periodic texture solar wafer (2015+)
12. Fourier image reconstruction defect detection solar cell electroluminescence fingers busbars
13. micro-crack detection multicrystalline solar cells anisotropic diffusion
14. single source domain generalization segmentation random convolution intensity augmentation (2021+)
15. FreeCOS fractal synthetic curvilinear self-supervised segmentation crack (2023+)
16. photovoltaic module EL image perspective correction cell extraction automatic (2022+)
17. Hessian line detector crack enhancement electroluminescence solar cell
18. electroluminescence image quality SNR IEC 60904-13 camera
19. The Devil is in the Crack Orientation crack detection (2023+)
20. PVEL-AD near-infrared EL anomaly dataset scratch thick line (2021+)
21. template matching defect-free reference cell subtraction electroluminescence anomaly (2019+)
22. simulation of EL images cracked cells isolated area busbar series resistance (2015+)
23. periodic texture removal Fourier defect detection deep learning preprocessing (2020+)
24. crack segmentation thin structure physics-informed EL inactive area prediction (2024+)
25. EL photovoltaic preprocessing augmentation domain shift different cameras (2025+)
26. Frangi-Net differentiable vesselness prior network thin structure (2018+)
27. morphological black-hat top-hat prior channel crack segmentation generalization (2021+)
28. super-resolution electroluminescence solar cell images crack segmentation (2019+)
29. pixel difference convolution edge detection thin structure contrast robust (2021+)
30. TOPCon half-cell module EL crack inspection deep learning busbar (2024+)

`search_snippets` x5 (scuff / scratch appearance, LIOT cross-dataset gains, half-cell crack visibility): all rate-limited, no result.
Snowball: `get_citations` on LIOT (doi:10.1109/tip.2022.3155954, 70 citing papers, 30 read); `similar_papers` on LIOT + CrackCue and on Deitsch 2021 + Chen 2023. Full text read: STC-Net (arXiv 2608.01714) sections 5, 12; CrackCue (arXiv 2507.16851) sections 1, 7, 11, 13. `fetch_fulltext` failed for Jaeckel 2024 (no PDF) and SIKD (timeout).
WebSearch x6: CrackCue code, LIOT repo, half-cut / multi-busbar EL work 2026, PV-Vision isolated-area code, scratch / scuff appearance in EL, SIKD and GIN-IPA repos.

## 2. What the search says about our five problems (S)

- Our cells are already cropped and roughly registered. Module-level registration, perspective, lens and vignetting correction (Deitsch, Sovetkin, Bedrich, Koelblin, Hoffmann) has little to give the scores. It matters for the benchmark (how cells are cut out of the 159k pool and new module images) and for severity (power-loss maps).
- The live mechanisms for this direction are input-side or physics-side priors:
  (a) a learned crack-free background and its difference image (CrackCue = a learned golden cell);
  (b) contrast-invariant encodings (LIOT);
  (c) appearance randomisation and Fourier style transfer for the E1 gap (GIN-IPA, FDA, RaffeSDG, Fourier-Morphology blending, SIKD);
  (d) fixed edge / high-pass priors (STC-Net, anisotropic diffusion, defect-aware banding);
  (e) an unsupervised reconstruction prior trained on normal cells (EI-AE);
  (f) a circuit prior for inactive: a cell region becomes inactive only when cracks cut it off from the busbars (Chen 2022 isolated-area algorithm). This is the only physics prior found that speaks to problem 2 (inactive) and it is new in this revision.
- None of these is closed by BRIEF section 5. Closest rows: "intensity normalisation (fail)" and "per-panel BN adaptation (fail)" at inference; "label-safe augmentation (flips, rot90, brightness / contrast only)" in training; pseudo-label SSL with the 11.9k external pool (n.d. at 100%). Learned or contrast-invariant input channels, random-network appearance augmentation, Fourier style transfer, anomaly priors and circuit-based inactive priors were never run ("never tried": refinement networks, anomaly-detection priors, physics simulation).
- No EL paper was found on half-cut or multi-busbar layout normalisation for segmentation, on scuff streaks, or on multi-bias input for segmentation. Hashem 2026 (R) shows crack length and count do not predict power loss in half-cut TOPCon / multi-busbar modules, which matters for the severity track and for E1 (58 half-cut cells).

## 3. Selected papers

Score = value for raising our scores (rubric). Bench = value for the benchmark. "Code" lists only repositories confirmed by a tool result (abstract text or web search); anything else is "unverified".

| # | id | year | venue | code | mechanism (R) | adaptation to our data (S) | score | bench |
|---|---|---|---|---|---|---|---|---|
| 1 | doi:10.1016/j.patcog.2025.112107 (arXiv 2507.16851) CrackCue | 2025 | Pattern Recognition | unverified ("will be publicly available"; web search found none) | Max-pool k=8 + upsample removes thin dark cracks; an encoder-decoder without skips (10+10 conv layers) refines this to a crack-free background, trained only on non-crack pixels (GT dilated to d=4 px and masked). The difference image is the "crack cue", concatenated as input. R: cross-dataset ODS U-Net 0.790 to 0.847, CrackFormer 0.811 to 0.887, DeepCrack 0.848 to 0.890; under contrast perturbation U-Net +17.4% ODS vs +14.6% for LIOT; under defocus blur +5.6% vs -1.6% for LIOT. Median-filter and black-hat cues help less, Canny cue hurts. | Learned golden cell. Mask crack AND inactive from the reconstruction loss; dilate crack to about 5 px (dark line FWHM is about 4 px, label 1 to 2 px). Keep k=8 at 512 px (also try 12). Fingers, busbars and grain are in the loss, so the cue learns to ignore them. Input becomes 2 channels; init conv1 channel 2 from the mean ImageNet filter. Risk on E1: scuff streaks are dark and absent from training, so the cue may fire on them (watch E1 precision). | 72 | 45 |
| 2 | doi:10.1109/tmi.2022.3224067 GIN-IPA | 2022 | IEEE TMI | github.com/cheng-01037/Causality-Medical-Image-Domain-Generalization (seen via a third-party repo listing; GitHub page not opened) | GIN: augment each training image with a randomly weighted shallow conv net (new intensity and texture each step). IPA: resample the appearance of correlated regions independently to break spurious correlations. R (web summary of paper): Dice 86.3 / 85.0 / 70.4 for GIN+IPA vs 86.0 / 83.8 / 65.1 GIN only on abdominal / cardiac / prostate cross-domain tasks. | Our augmentation is brightness / contrast only. GIN with 1x1 and 3x3 kernels on 1-channel EL keeps 1 to 2 px lines in place, so labels stay valid. IPA masks: structural classes (ribbons, border, frame_edge, sp_multi grain) are the "objects" so the model cannot use their look as a crack or inactive cue. Aimed at E1 and the weak BMRK / CSIR sources. | 66 | 45 |
| 3 | doi:10.1109/tip.2022.3155954 LIOT | 2022 | IEEE TIP | github.com/TY-Shi/LIOT (named in abstract; web search confirms) | Grey image becomes a contrast-invariant 4-channel code: intensity order of each pixel vs neighbours along 4 directions. R: better cross-dataset vessel segmentation and vessel-to-crack transfer. | Our 5 sources differ in gain and contrast; E1 is CSIR with a new layout. Feed [EL, LIOT x4] (5 channels) instead of LIOT alone, so in-distribution signal is kept. Neighbour range about 8 px to span a 4 px crack. BMRK (downscaled, blurrier) is the risk case, given LIOT's drop under blur in the CrackCue tables. | 62 | 50 |
| 4 | doi:10.1109/pvsc48317.2022.9938503 Chen, Karin, Jain: crack segmentation and maximum inactive area prediction | 2022 | IEEE PVSC | github.com/hackingmaterials/pv-vision (web-verified; PyPI listing names "maximum isolated area prediction") | UNet segments crack lines, cross cracks, busbars and dark areas (1,272 train cells; test F1 0.875, IoU 0.782), then an algorithm predicts the worst-case inactive area: cell regions cut off from all busbars by the detected cracks. | Circuit prior for problem 2. From house predictions of crack + ribbons (+ border) compute the cell components (minus closed crack pixels) not connected to any ribbon; this "isolatable area" map is (a) an extra input channel for a small second-stage inactive head, and (b) a post-hoc gate: inactive pixels outside any isolatable region are suppressed, dark pixels inside one are lowered in threshold. E fits it: 99% of inactive regions touch a crack, inactive never occurs without a crack. Needs gap closing (crack predictions break at 1 to 2 px). On half-cut E1 cells the ribbon geometry changes, which the algorithm handles natively. | 58 | 60 |
| 5 | doi:10.1111/mice.70127 Fourier-Morphology blending UDA | 2025 | Computer-Aided Civil and Infrastructure Eng. | unverified | Fourier style transfer plus morphological operators, two parameters, align style and crack geometry (width) between domains; uncertainty-guided dual-network self-training on target. R: F1 up to +18.5% over baselines in cross-domain crack sets. | (a) Target domain = CSIR half-cell pool (1,152 multi half-cells look like E1). (b) The morphology half can align label width across sources (BMRK 3.0, SDLE 3.25 vs ARTS 1.5 px). Run the blending first without self-training, since pool self-training at 100% labels was n.d. | 55 | 35 |
| 6 | arxiv:2608.01714 STC-Net | 2026 | arXiv (MERCon 2026, doi:10.1109/mercon71835.2026.11691399) | unverified | EL crack segmentation with two fixed prior branches injected into the decoder: Sobel gradient-magnitude pyramid and FFT radial high-pass residual pyramid; plus boundary-topology refinement and a crack-derived inactive-area proxy for power loss. R: PVEL-S test mIoU 72.5, mDice 80.2; no ablation of the priors in the text read. | Add the two prior pyramids to U-Net++ decoder stages. Sobel fires on both flanks of a 4 px dark line while the label sits on one ridge; use a LoG (sigma about 1.5) ridge prior instead. Weak evidence, but a 2026 EL method, so a benchmark slot. | 52 | 50 |
| 7 | doi:10.1109/cvpr42600.2020.00414 FDA | 2020 | CVPR | github.com/YanchaoYang/FDA (web-verified in first pass; not re-checked) | Swap the low-frequency amplitude spectrum of a source image with a target image's; no training for the alignment. | Targets from the CSIR half-cell pool. beta 0.01 to 0.05 so the finger period is untouched. S: E1 gap is mostly content (half-cut, scuff), not global style, so expect a small effect; cheap. | 48 | 35 |
| 8 | doi:10.1039/d5ee05042a EI-AE | 2025 | Energy & Environmental Science | unverified | Enhanced iterative autoencoder trained only on normal EL images gives unsupervised pixel-level defect maps; few-shot extension with a few masks. | Bold bet for E1: train on pool half and full cells (scuffs are common there, so the AE learns them as normal); residual map as an extra input channel. Opposite of CrackCue, whose background net never sees scuffs. Also a label-free baseline for the benchmark. | 48 | 55 |
| 9 | arxiv:2405.01228 RaffeSDG | 2024 | arXiv | github.com/liamheng/Non-IID_Medical_Image_Segmentation (named in abstract) | Random frequency-filter augmentation plus blending of homologous samples, and a Gaussian-filter structural-saliency consistency term. R: better out-of-domain segmentation over 3 tissues, 4 modalities. | Single-source DG for E1. Keep random filtering below about 1/16 px^-1 so 4 px crack bands are untouched. Competes with GIN; run only if GIN shows a signal. | 45 | 30 |
| 10 | doi:10.1109/iccv51070.2023.00087 FreeCOS | 2023 | ICCV | github.com/TY-Shi/FreeCOS (first pass, from abstract) | Fractal curves composited into unlabelled images with FDA, plus intensity-order alignment and contrastive losses, for label-free curvilinear segmentation. R: beats unsupervised baselines on XCAD, DRIVE, STARE, CrackTree. | Pretext stage on pool half-cells so the model sees thin dark curves on half-cut, scuff-bearing backgrounds. Differs from the closed "crack copy-paste" row (real crack patches, more decoys): curves are procedural, alignment is order-based. Overlaps D06. | 45 | 35 |
| 11 | doi:10.1007/s11704-024-40462-2 (arXiv 2409.17503) SIKD shape-intensity distillation | 2025 | Frontiers of Computer Science | github.com/whdong-whu/SIKD (web search) | Teacher trained on class-wise averaged training images (each labelled region replaced by its mean intensity), so it learns shape-intensity relations without texture; knowledge distilled into a same-size student. R (web summary): gains on 5 medical tasks and better unseen-dataset generalisation. | Class-wise averaging of an EL cell removes grain, finger texture and source gain, leaving "idealised EL". Teacher on averaged cells with all 24 classes; distil into the house student. Crack regions are 1 to 2 px so averaging them is near identity; the effect will be on background / structural classes and inactive, and on E1 texture shift. Same lab as LIOT and CrackCue. | 42 | 30 |
| 12 | doi:10.3390/app16042148 Defect-aware RGB | 2026 | Applied Sciences | unverified | Local contrast enhancement, then grey ranges mapped to 3 channels (crack / inactive dark, healthy emission, conductive paths). R: higher ELPV classification accuracy, at lower resolution too. | Our ImageNet encoder gets 1 channel. A physics-banded 3-channel input uses the full pretrained conv1. Bands set per source by percentiles, not fixed grey values. Classification evidence only. | 40 | 30 |
| 13 | doi:10.1186/1687-5281-2014-15 Anwar and Abdullah | 2014 | EURASIP JIVP | none | Improved anisotropic diffusion smooths multicrystalline grain while keeping crack edges, then segmentation. | Classical prior channel for multi cells (sp_multi is a large share). Offline, cheap. CrackCue ablation (R) says classical cues give moderate gains, so expect less than #1. Also the classical baseline in the benchmark. | 35 | 35 |
| 14 | doi:10.1109/jphotov.2023.3249970 PV-Vision crack segmentation and features | 2023 | IEEE JPV | github.com/hackingmaterials/pv-vision (web-verified) | Crack segmentation (about 0.18 s per cell, VGG16 UNet, test F1 0.875 / IoU 0.782) plus crack-isolated area, brightness in that area, crack length; module-to-cell cropping with perspective transform; crack dataset doi:10.21948/1871275. | Must-have published EL baseline for the benchmark; its features feed severity. For scores: its crack set is extra data (D02 / D03 territory). | 35 | 85 |
| 15 | doi:10.1002/advs.202300206 Luminescence denoising (Liu, Dwivedi, Trupke, Hameiri) | 2023 | Advanced Science | unverified | Deep denoiser for luminescence images of Si cells. R: PSNR +30%, SSIM +39% vs noisy input; beats classical denoisers. | For noisy CSIR cells (E: one test cell wrecks 1 run in 6). Risk: 7% of crack components are less than 2% darker than surroundings and can be erased. Only as a second channel or a test-time variant. | 30 | 25 |
| 16 | doi:10.1007/s00138-021-01191-9 Deitsch et al. | 2021 | Machine Vision and Applications | unverified | Cell segmentation in uncalibrated EL module images: ridge detection of busbars and cell borders, lens-distortion and perspective correction. | Score side: busbar / border ridge map as a layout channel, or locating the cut line in E1 half-cut cells. Benchmark side: a documented way to cut cells from the 159k pool and new module images. | 30 | 55 |
| 17 | doi:10.1051/epjpv/2026017 Hashem et al., crack impact in current cell technologies | 2026 | EPJ Photovoltaics | n/a | 230 mono-Si mini-modules, full-cell PERC and half-cut TOPCon, 2 to 12 busbars, line cracks that do not isolate cell parts. R: crack length and count are not universal power-loss predictors; PERC moderate correlation at 200 W/m2 that weakens at 1000 W/m2; TOPCon no meaningful correlation. | No direct score use. Severity: grade by isolated / inactive area (#4) rather than crack length, and make the grade layout-aware (half-cut, busbar count). E1 is half-cut heavy, so severity results there must not reuse full-cell rules. | 12 | 60 |
| 18 | doi:10.1051/epjpv/2024039 EL nomenclature (Jaeckel et al.) | 2024 | EPJ Photovoltaics | n/a | Consensus categories: single cracks, multi-cracks, electrical-circuit anomalies, miscellaneous; independent of cell size and shape (full, half, third, x-cut); classification proposal combining power-loss risk and safety risk. | Defines crack modes and severity classes for the benchmark's severity track, and the "miscellaneous" bucket is the reference for non-crack dark marks such as scuffs on E1. Full text not fetchable off campus. | 15 | 75 |

Also kept as severity references, not scored as selections: QELA, Bedrich et al. 2018 (doi:10.1109/jphotov.2018.2846665: camera / perspective correction then power-loss map from two EL images, rRMSE 1 to 3%) and Saborido-Barba et al. 2024 (doi:10.3390/s24051479: IEC TS 60904-13 type C crack area per cell to power loss; cell level beats substring / module level).

### Minimum experiments

All on the house U-Net++ / ResNet-34 recipe, 20k steps, 5 seeds per arm unless noted (about 5.5 GPU-h per arm). Inactive and E1 inactive arms also run on PF, since E1 inactive is 0.05 (house) vs 0.24 (PF). Detectable crack IoU change on test is about 0.012 (E); inactive is decided by 3 test cells, so inactive arms should also be read on the existing module-grouped 5-fold CV roots.

1. CrackCue. Arm: house + background net (k=8) + |I - B| channel, joint loss weight 1. Baseline: house. Metrics: test-clean crack IoU and relF1@2; E1 crack relF1@2, and recall in the 20 scuff half-cut cells. Kill: E1 relF1@2 gain < +0.03 AND test crack IoU gain < +0.012. About 15 GPU-h.
2. GIN-IPA. Arm: house + GIN (p=0.5) + IPA on structural classes. Baselines: house and PF. Metrics: E1 crack relF1@2, E1 inactive IoU, test mIoU_rob. Kill: E1 relF1@2 < +0.03 and E1 inactive IoU < +0.03 on the PF arm, or test mIoU_rob drop > 0.01. About 12 GPU-h.
3. LIOT. Arm: [EL, LIOT x4] input. Baseline: house. Metrics as #1 plus per-source crack IoU (BMRK, CFVS). Kill: E1 relF1@2 < +0.03, or test crack IoU drop > 0.012. About 11 GPU-h.
4. Isolated-area inactive prior. Step 1 (no training, about 1 GPU-h): from existing PF 5-seed ensemble predictions on val and CV folds, compute isolatable regions from crack + ribbons and apply the gate. Metric: inactive IoU, precision and recall on 5-fold CV and val; E1 inactive IoU read once at the end. Kill: CV inactive IoU gain < +0.02. Step 2 only if step 1 passes: second-stage inactive head with the isolatable map as input, same kill line on top of step 1.
5. Fourier-Morphology blending (no self-training first). Target: CSIR half-cell pool. Baseline: house. Metric: E1 crack relF1@2. Kill: < +0.03. Add self-training only if it passes.
6. STC-Net priors. Arm: LoG + FFT high-pass pyramids into the U-Net++ decoder. Baseline: house. Metrics: test crack IoU, relF1@2, comp >= 20 px recall. Kill: < +0.012 crack IoU and no relF1@2 gain.
7. FDA. Arm: house + FDA style from CSIR half-cell pool (beta 0.01 / 0.05), 3-seed screen. Metric: E1 crack relF1@2. Kill: < +0.02.
8. EI-AE residual. Arm: AE on about 6k pool cells (half and full), residual as channel 2. Baseline: house. Metric: E1 crack precision and relF1@2 in scuff cells. Kill: < +0.03 relF1@2.
9. RaffeSDG, only if #2 shows a signal. Kill: not better than GIN by 0.02 E1 relF1@2.
10. FreeCOS pretext on pool half-cells, then PF fine-tune. Baseline: PF. Metrics: E1 relF1@2 and crack false-positive pixels per half-cut cell. Kill: < +0.03 relF1@2.
11. SIKD. Teacher on class-averaged cells, feature distillation into house student. Baseline: house. Metrics: mIoU_rob, E1 crack relF1@2. Kill: mIoU_rob < +0.01 and E1 relF1@2 < +0.02.
12. Defect-aware RGB. Per-source percentile 3-band input into the full ImageNet conv1. Kill: mIoU_rob < +0.01 and crack IoU < +0.012.
13. Anisotropic-diffusion residual channel. Metric: test crack IoU on sp_multi cells. Kill: < +0.012.
14. Denoiser as test-time second channel. Kill: any drop in comp >= 20 px recall, or no gain on noisy CSIR cells.
15 to 18. Benchmark / severity, no training arm: run PV-Vision's released model under our protocol; adopt the nomenclature (#18), isolated-area grading (#4) and layout-aware severity (#17); keep QELA and IEC TS 60904-13 area-to-power as the physics reference for power-loss bands.

## 4. Notable papers rejected (one line each)

- doi:10.3390/en14092508 Koelblin 2021, outdoor EL preprocessing for PV parks: module-level outdoor registration; our cells are already cropped.
- doi:10.3233/ica-180588 (arXiv 1807.10820) Sovetkin and Steland 2018, cell extraction: same reason; Deitsch kept as the benchmark reference.
- doi:10.25593/open-fau-2855 Hoffmann 2026 thesis: module detection, weak crack segmentation, multi-frame super-resolution, power regression; MFSR needs several frames per cell, which we do not have.
- doi:10.1016/j.solener.2021.03.058 Otamendi 2021, module-to-cell anomaly pipeline: pipeline paper, no new prior.
- doi:10.3390/en14020374 Xue 2021, Laplace pyramid + wavelet + FCM crack extraction: classical full pipeline, superseded by #13 as a channel and by CrackCue.
- arxiv:2208.05994 SeMaCNN, HJT anomaly segmentation: production-line HJT cells, no preprocessing idea.
- doi:10.1007/s44443-026-00566-0 YOLO-PVELAD 2026: DCT high-frequency FPN and directional attention for box detection; architecture idea, belongs to D09 / D28.
- arxiv:2603.14282 TexWDS / MPTCE 2026 (wafer periodic-texture suppression): dropped from the table this revision because D28 (frequency priors) covers it; the idea (periodic-suppressed image as extra channel, never as replacement since gridline and ribbons are classes) still stands.
- doi:10.1109/iccv51701.2025.02236 TopoTTA (ICCV 2025): test-time adaptation for tubular structures, relevant to E1 but covered by D10 / D12.
- doi:10.1109/tpami.2023.3322735 dual-stream SR segmentation: auxiliary SR needs high-res targets; 2x input was already n.d.
- doi:10.1002/ese3.858 Dix-Peek 2021, injection-dependent EL: needs multi-bias images we do not have.
- doi:10.1109/jphotov.2025.3542829 Drir 2025, DCGAN + perceptual loss: generation for classification, belongs to D06.
- arxiv:2603.13337 MultiSolSegment 2026: multi-label EL segmentation (cracks crossing busbars); a formulation, covered by D01 / D27.

## 5. Gaps

- No paper found on half-cut or multi-busbar layout normalisation for EL segmentation, or on scuff / backsheet-scratch appearance with images (web search returned only general EL texts). Jaeckel 2024 (open access, EPJ PV) should be read on campus for its "miscellaneous" observations and half-cell notes.
- Multi-bias EL as model input: physics is clear (QELA, Dix-Peek) but there is no segmentation paper and no multi-bias data in our sets. Only relevant if WattCycle's rig captures two currents.
- Self-supervised denoising (Noise2Void-style) for EL was not found; Liu 2023 is supervised.
- Two learned golden-cell priors should be compared head to head: supervised background (CrackCue) vs unsupervised normal-cell AE (EI-AE). The scuff question decides between them.
- The isolated-area circuit prior (#4) has no paper that uses it as a training signal or input channel for segmentation; it is used only for post-hoc power-loss estimation. A dedicated search on "connectivity / circuit-consistent" inactive segmentation is worth one more scout.
- Semantic Scholar snippet search was rate-limited both sessions, so evidence questions were answered from abstracts, two full texts and web summaries.
