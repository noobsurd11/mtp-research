# T4 open papers: 22 scout records the first T4 team did not take (best first)

## P078 | That Label's Got Style: Handling Label Style Bias for Uncertain Image Segmentation
- id arxiv:2303.15850 | 2023 | ICLR | score 62 | bench 45 | dirs D17 | code none found
- mechanism: Condition stochastic segmentation models (Probabilistic U-Net, SSN) on a discrete label-style variable, modelling p(annotation | image, style) instead of p(annotation | image), which removes style-induced area bias.
- scout's adaptation: Style = source. Cheapest form is a one-hot source code into the decoder (shares the arm of the CIN paper); the stochastic variant adds per-source crack sample distributions for calibrated uncertainty and severity flags. Use as small-data evidence and as the probabilistic follow-up.
- evidence: R: ISIC subset, 179 train image-mask pairs over 3 styles; c-Prob.U-Net IoU 0.77/0.78/0.76 vs pooled 0.65/0.65/0.69; PhC-U373 0.92 vs 0.89-0.90. Small data, blob objects. | prior overlap: none

## P184 | The Treasure Beneath Multiple Annotations: An Uncertainty-Aware Edge Detector
- id doi:10.1109/cvpr52729.2023.01488 | 2023 | CVPR | score 52 | bench 30 | dirs D11,D13 | code https://github.com/ZhouCX117/UAED
- mechanism: Model multiple annotations as a learnable per-pixel Gaussian; variance is the uncertainty; loss re-weighted toward uncertain pixels.
- scout's adaptation: Treat the 2021 and 2022 crack label versions as two annotators; sample one per iteration; learn mean and variance; read out the mean. Variance map also feeds a benchmark uncertainty view.
- evidence: R: CVPR 2023 SOTA on multi-annotator edge sets (BSDS); numbers not read. | prior overlap: None; old labels were never used as a second annotator.

## P204 | Training Like a Medical Resident: Context-Prior Learning Toward Universal Medical Image Segmentation (Hermes)
- id doi:10.1109/cvpr52733.2024.01064 | 2024 | CVPR | score 50 | bench 45 | dirs D17 | code none found
- mechanism: A universal segmentation model with learned task and modality prior tokens, trained jointly on many heterogeneous, partially labelled datasets.
- scout's adaptation: Prior tokens for the 5 BenchmarkEL sources plus UCF-EL. UCF-EL's region-style crack (crack plus inactive) then trains jointly without overwriting the thin-crack convention, and the encoder is not erased because training is joint.
- evidence: R: CT/MRI/PET multi-dataset universal segmentation, gains over task-specific and other universal models (abstract level). | prior overlap: UCF-EL pretrain-then-finetune was n.d. or worse, but the fine-tune erased the encoder. Joint training with dataset pr...

## P216 | Probabilistic Modeling of Inter- and Intra-observer Variability in Medical Image Segmentation (Pionono)
- id doi:10.1109/iccv51070.2023.01929 | 2023 | ICCV | score 50 | bench 35 | dirs D17 | code none found
- mechanism: Each rater gets a learned Gaussian in latent space. A sample is fused with image features to give that rater's segmentation, trained end to end by variational inference, so it models both inter-rater style and intra-rater variability.
- scout's adaptation: Rater = source (5 Gaussians); the latent variance captures within-source jitter. Small head on top of the house decoder; use the rater mean at test.
- evidence: R: prostate cancer histopathology with multiple pathologists; beats STAPLE, Probabilistic U-Net and confusion-matrix models. | prior overlap: none

## P240 | MEMO: Human-like Crisp Edge Detection Using Masked Edge Prediction
- id arxiv:2603.20782 | 2026 | CVPR 2026 | score 48 | bench 45 | dirs D13 | code https://github.com/cplusx/MEMO_Edge_Detection
- mechanism: Trains with randomly masked edge maps as an extra input. At inference it starts fully masked and reveals pixels in order of confidence, so thick confidence ridges collapse to thin lines. Uses only cross-entropy, plus synthetic pretraining.
- scout's adaptation: Add a refinement U-Net on frozen house logits, with a second input channel holding a partially revealed crack map. Progressive reveal can link crack fragments (76 to 88% of components are under 20 px). This would be the first refinement-network test on our data.
- evidence: R: better results on crispness-aware evaluations than prior methods without post-processing. Fine-tuning adds 1.2% params. Numbers not read. | prior overlap: Refinement networks are listed as never tried. Open.

## P248 | Transformer-Based Annotation Bias-Aware Medical Image Segmentation (TAB)
- id doi:10.1007/978-3-031-43901-8_3 | 2023 | MICCAI | score 48 | bench 35 | dirs D17 | code https://github.com/Merrical/TAB
- mechanism: A transformer with one learnable query per annotator extracts preference features, so one head outputs each annotator's segmentation. A separate term models stochastic annotation error.
- scout's adaptation: One query per source in a light transformer block at the U-Net++ bottleneck; each source's images supervise only its own output. Re-implement, because the repo targets PyTorch 1.7.
- evidence: R: RIGA optic disc/cup with six annotators; beats prior annotator-bias models (abstract). | prior overlap: none

## P293 | Diversified and Personalized Multi-Rater Medical Image Segmentation (D-Persona)
- id doi:10.1109/cvpr52733.2024.01090 | 2024 | CVPR | score 45 | bench 40 | dirs D17 | code https://github.com/ycwu1997/D-Persona
- mechanism: Stage 1 trains a Probabilistic U-Net on multi-rater labels to build a shared latent space. Stage 2 attention heads extract expert-specific prompts for personalized masks.
- scout's adaptation: Use label versions as raters: the 2021 original and 2022 revised crack/inactive masks exist for the same cells. Train on both and output the revised-style persona, so the old labels add signal instead of being discarded.
- evidence: R: NPC-170 (in-house) and LIDC-IDRI; better diversity and personalized accuracy than multi-rater baselines (abstract). | prior overlap: label version change gave +0.05 to +0.08 crack IoU, but no run trained on both versions jointly

## P302 | U-Harmony: Enhancing Joint Training for Segmentation Models with Universal Harmonization
- id arxiv:2601.14605 | 2026 | arXiv | score 45 | bench 35 | dirs D17 | code none found
- mechanism: Per-instance feature harmonization, then restoration layers that reinject dataset-specific statistics into the decoder. A domain-gated head infers each domain's contribution from prototypes, so no dataset ID is needed at test.
- scout's adaptation: A source-gated decoder for the case where the source is unknown or shifted (E1 half-cut CSIR, benchmark new-module track). Check whether the gate picks CSIR on E1.
- evidence: R: cross-institution brain lesion datasets; a secondary summary reports up to +8.4% DSC (unverified against the full paper). | prior overlap: per-panel BN adaptation failed, but that was test-time BN statistics, not learned dataset-gated restoration

## P310 | Segmentation Style Discovery: Application to Skin Lesion Images
- id doi:10.1007/978-3-031-77610-6_3 | 2024 | MICCAI ISIC workshop (LNCS 2025) | score 45 | bench 30 | dirs D17 | code https://github.com/sfu-mial/StyleSeg
- mechanism: StyleSeg: M output heads plus a style classifier on (image, mask); winner-take-all Dice plus classifier-weighted Dice discovers M consistent styles without annotator IDs.
- scout's adaptation: M = 3 crack heads combined with source ID, to discover within-source annotator styles; after training pick each source's majority style head from train cells and use it at test.
- evidence: R: outperforms competing methods on four skin-lesion datasets; strong alignment of discovered styles with annotator preferences on ISIC-MultiAnnot. | prior overlap: none

## P330 | Pixel Difference Networks for Efficient Edge Detection (PiDiNet)
- id doi:10.1109/iccv48922.2021.00507 | 2021 | ICCV | score 42 | bench 60 | dirs D13 | code https://github.com/hellozhuo/pidinet
- mechanism: Pixel difference convolutions fold classic gradient operators into conv layers, giving an accurate edge detector under 1M params trained from scratch.
- scout's adaptation: Swap the 3x3 convs in the first two ResNet-34 stages for PDC variants, or add a full-resolution PDC side branch fused into the U-Net++ decoder. Crack and gridline contrast are local intensity differences, and 7% of cracks are under 2% darker than their surroundings. Also a lightweight member of t...
- evidence: R: BSDS500 ODS 0.807 at 100 FPS with under 1M params; a variant under 0.1M params runs at 200 FPS. | prior overlap: Only the ResNet-34/50 U-Net++ backbones were tested. Open.

## P371 | Resolving Inconsistent Semantics in Multi-Dataset Image Segmentation
- id arxiv:2409.09893 | 2024 | arXiv | score 40 | bench 50 | dirs D17 | code none found
- mechanism: Trains one segmentation model on several datasets whose class definitions conflict, by reconciling label semantics instead of forcing one label space.
- scout's adaptation: Map UCF-EL, MultiSolSegment and PVEL-S classes onto our 24 classes with per-dataset label spaces, for joint training and for the benchmark's cross-dataset track.
- evidence: R: natural-image multi-dataset segmentation (abstract level). | prior overlap: joint multi-dataset training is open in BRIEF section 5

## P372 | SAUGE: Taming SAM for Uncertainty-Aligned Multi-Granularity Edge Detection
- id doi:10.1609/aaai.v39i6.32615 | 2025 | AAAI | score 40 | bench 50 | dirs D13 | code https://github.com/Star-xing1/SAUGE
- mechanism: Frozen SAM with a 1.5% adapter that fuses intermediate SAM layers coarse to fine; linearly blended labels give granularity pseudo-labels.
- scout's adaptation: Frozen SAM/SAM2 encoder with multi-layer adapter fusion and crack-only head on 1-channel EL replicated to 3, aimed at E1 half-cut cells and scuff confounders.
- evidence: R: strong cross-dataset generalisation, SOTA on BSDS500, Multicue, NYUDv2 (abstract). | prior overlap: Partial: frozen SAM2 Hiera-T linear probe showed no gain, but that was single layer, no adapter, no decoder; adapters...

## P416 | EasyControlEdge: A Foundation-Model Fine-Tuning For Edge Detection
- id arxiv:2602.16238 | 2026 | ICIP 2026 | score 38 | bench 40 | dirs D13 | code none found
- mechanism: Lightweight condition injection on a frozen FLUX.1-dev rectified-flow model, pixel-space weighted CE through a proxy gradient, guidance scale controls edge density at inference.
- scout's adaptation: EL replicated to 3 channels at 512 px, frozen backbone, crack-only target; guidance scale as a recall knob for E1 and the almost-all-cracks target. Gated FLUX download needs user OK. First check VAE reconstruction of GT crack maps since the 8x latent may erase 1 px cracks.
- evidence: R: BIPED with 20 training images CEval ODS 0.875 vs DiffusionEdge 0.851, GED 0.746; BSDS CEval ODS 0.807; CubiCasa walls strong at 42 images. | prior overlap: None; generative foundation models and adapters are listed as open. Frozen linear probes of DINO/SAM do not cover this.

## P432 | Multi-style conversion for semantic segmentation of lesions in fundus images by adversarial attacks
- id arxiv:2410.13822 | 2024 | arXiv | score 38 | bench 25 | dirs D17 | code none found
- mechanism: A linear probe on encoder features detects dataset origin. An adversarial input perturbation toward a chosen dataset makes the frozen model segment in that dataset's annotation style, with no retraining.
- scout's adaptation: Train a source probe on the frozen house encoder, then at test take a few PGD steps that push each cell toward its own source (or toward ARTS for thin output). Measure the change in crack width and IoU.
- evidence: R: diabetic retinopathy lesion datasets with different annotation protocols; continuous style conversion shown (numbers not retrieved). | prior overlap: none

## P442 | DiffusionEdge: Diffusion Probabilistic Model for Crisp Edge Detection
- id doi:10.1609/aaai.v38i7.28490 | 2024 | AAAI | score 35 | bench 65 | dirs D13 | code https://github.com/GuHuangAI/DiffusionEdge
- mechanism: A latent diffusion edge detector. A pixel-level, uncertainty-aware cross-entropy is distilled into the latent space, with an adaptive Fourier filter, and it predicts crisp edges without NMS.
- scout's adaptation: Train on binary crack and gridline maps with the 1-channel EL image replicated, at 512 px. First check that the autoencoder can reconstruct the 1 px GT crack maps, a cheap test. Mainly a benchmark baseline for generative thin-structure methods.
- evidence: R: on NYUDv2, ODS +30.2%, OIS +28.1% and AC +65.1% over the second best without post-processing. Trained on benchmark-sized sets of a few hundred to a thousand images. | prior overlap: Diffusion segmenters are listed as never tried. Open.

## P505 | Label Noise in Segmentation Networks: Mitigation Must Deal with Bias
- id doi:10.1007/978-3-030-88210-5_25 | 2021 | MICCAI UNSURE workshop | score 30 | bench 55 | dirs D17 | code none found
- mechanism: Evidence paper: segmentation nets are robust to unbiased label errors (random warp, crop) but sensitive to biased errors (constant shift), so mitigation must target bias.
- scout's adaptation: Not an arm. Frames which part of our crack IoU loss is recoverable: per-source width and any per-source constant offset (biased) vs within-source jitter (unbiased). Motivates the zero-GPU per-source offset / width diagnostics and a benchmark report of biased-error sensitivity.
- evidence: R: BraTS-type tumour masks; constant 5 px shift cost about 10% Dice for supervised, MT and AE models; random warps barely hurt. | prior overlap: none

## P519 | Stochastic Segmentation Networks: Modelling Spatially Correlated Aleatoric Uncertainty
- id arxiv:2006.06015 | 2020 | NeurIPS | score 30 | bench 40 | dirs D17 | code none found
- mechanism: Models logits as a low-rank multivariate Gaussian, giving spatially coherent mask samples at little extra cost.
- scout's adaptation: Replace the crack logit head with a low-rank Gaussian head. Average the samples, or pick the sample with the highest expected IoU, and use the variance as a calibrated crack uncertainty for review flags and severity.
- evidence: R: LIDC lung nodule and BraTS; better sample diversity and quality than Probabilistic U-Net (abstract). | prior overlap: none

## P526 | Practical Edge Detection via Robust Collaborative Learning (PEdger)
- id doi:10.1145/3581783.3612099 | 2023 | ACM MM | score 30 | bench 25 | dirs D13 | code none found
- mechanism: Collaborative learning between models from different training moments and heterogeneous architectures (recurrent and not) to resist noisy labels, with no pretraining.
- scout's adaptation: An EMA teacher plus a second architecture trained on labelled data only, with crack consistency used as label denoising at 100% labels.
- evidence: R: better accuracy, speed and size on BSDS500 and NYUD without pretraining. Numbers not read. | prior overlap: Partly closed: Mean Teacher at 100% with the pool was n.d., and CPS at 5% was worse. Its use for denoising labelled d...

## P561 | Generative Edge Detection with Stable Diffusion (GED)
- id doi:10.1145/3830018 | 2026 | ACM TOMM | score 25 | bench 40 | dirs D13 | code none found
- mechanism: Fine-tunes the Stable Diffusion denoising U-Net to predict latent edge maps in one step, with granularity as a condition and a granularity regularisation.
- scout's adaptation: Same VAE-latent risk as DiffusionEdge for 1 px cracks, so the reconstruction gate comes first. Use source label style as the granularity condition.
- evidence: R: BSDS ODS 0.870, OIS 0.880. | prior overlap: Not tested. Open.

## P575 | A Probabilistic U-Net for Segmentation of Ambiguous Images
- id arxiv:1806.05034 | 2018 | NeurIPS | score 22 | bench 45 | dirs D17 | code none found
- mechanism: A conditional VAE prior/posterior pair over a latent code gives a distribution of plausible masks from a U-Net.
- scout's adaptation: Reference baseline for the multi-rater family and the base of the D-Persona arm. Use the latent code to represent trace placement ambiguity.
- evidence: R: LIDC-IDRI and Cityscapes; well-calibrated sample distributions (abstract). | prior overlap: none

## P581 | Evaluating medical AI systems in dermatology under uncertain ground truth
- id doi:10.1016/j.media.2025.103556 | 2025 | Medical Image Analysis | score 20 | bench 70 | dirs D17 | code none found
- mechanism: Treats ground truth as a distribution aggregated from annotators and reports metrics with ground-truth uncertainty, instead of against one label.
- scout's adaptation: Benchmark scoring: treat each crack label as a distribution (two label versions, 2 px tolerance band) and report strict IoU, relF1@2 and a ground-truth-uncertainty interval per method.
- evidence: R: dermatology classification with multiple raters; shows that ground-truth uncertainty changes the evaluated accuracy (abstract not retrieved in full). | prior overlap: none

## P587 | Tiny and Efficient Model for the Edge Detection Generalization (TEED)
- id doi:10.1109/iccvw60793.2023.00147 | 2023 | ICCV Workshops | score 20 | bench 50 | dirs D13 | code https://github.com/xavysp/TEED
- mechanism: A 58K-parameter edge detector that trains in under 30 min and gives crisp edge maps.
- scout's adaptation: A benchmark suite member for the efficiency and deployment axis on crack. Optionally an auxiliary high-resolution crack-edge branch.
- evidence: R: 58K params, trains on BIPED in under 30 min, adds a new generalization test set. | prior overlap: Not tested. Open.

