# T5 family cards: thin-structure inputs and architecture modules (13 Nov 2026)

Analyst T5. Tags: R = from the paper or its repository (what I fetched), E = from our files or a measurement I ran here, S = my judgement. "unverified" = not checked by me.
Tools: the Research MCP was not loaded in this session (only its authenticate stub), so I used WebFetch / WebSearch on arXiv HTML, the eCS PDF and GitHub. Nothing was run on a server or GPU; no test or E1 file was read.
Companion files: `T5_thin_inputs_archs_spec.md` (arms), `ledger/T5.tsv`, `T5_precheck/` (CPU pre-check script and outputs, md5 in section 0.3).

## 0. Facts that frame the whole family

### 0.1 Where thin detail is lost in the house model (E, smp 0.5.0 source in `harness/src_snap/smp050/decoders/unetplusplus/decoder.py`)
- The smp ResNet-34 encoder returns 6 features: input (stride 1), conv1-BN-ReLU (stride 2, 64 ch), layer1 after max-pool (stride 4, 64), layer2 (8, 128), layer3 (16, 256), layer4 (32, 512).
- The U-Net++ decoder drops the stride-1 feature (l.97 `encoder_channels[1:]`, l.145 `features[1:]`). The last node `x_0_4` (l.136-138) upsamples the stride-2 node `x_0_3` (32 ch) by nearest interpolation and applies two 3x3 convs with **no skip**. So the finest skip is one 7x7 stride-2 conv deep (not two downsamplings as the task text says; the max-pool sits before the stride-4 skip), and the full-resolution output never sees full-resolution image detail.
- Decoder widths 256-128-64-32-16; stride-2 level has 4 nested nodes (`x_0_3 .. x_3_3`), full resolution has 1 (`x_0_4`).

### 0.2 CPU pre-checks run for this card (E, `T5_precheck/t5_precheck.out`, 532 cv5v2 pool cells, v1.1 masks, 4 min on the laptop)
**A. Stride quantisation ceiling.** The best block-wise reconstruction of the ground-truth crack mask (an aligned block is "crack" if at least k of its pixels are), pooled over 307,546 crack px:

| Grid | Best k | Oracle crack IoU | pred / GT px |
|---|---|---|---|
| stride 2 (2x2 blocks) | 2 of 4 | **0.692** | 1.25 |
| stride 4 (4x4 blocks) | 6 of 16 | **0.470** | 1.37 |

Reading (S): a decoder that could only paint 2x2 blocks would still be capped at 0.69, above the label ceiling (1 px shift = 0.56, BRIEF 2) and far above the house out-of-fold crack IoU (0.37, PROTOCOL 3.2). A stride-4 painter is capped at 0.47, about the house test IoU. The house has a stride-2 skip, so output resolution is **not shown to be the binding limit**; whether the house actually snaps to the 2x2 grid is the open question (spec arm 5 gate). This agrees with Track M R5 (2x input, n.d., BRIEF 5 "Resolution").

**B. Single-channel cue separability** (pixel AUROC, crack px vs non-crack non-padding px more than 2 px from crack, 229 cells with at least 20 crack px; "lines" = ribbons, border, busbars, gridline px; "low contrast" = crack px less than 2% darker than their 15 px median, 79,832 px = 26% of crack px):

| Cue | AUROC all | vs lines | low contrast | per source ARTS / BMRK / CFVS / CSIR / SDLE | spread |
|---|---|---|---|---|---|
| raw darkness | 0.762 | **0.509** | **0.708** | 0.660 / 0.660 / 0.884 / 0.608 / 0.747 | 0.276 |
| CrackCue coarse (max-pool 8, bilinear up, relative difference) | **0.806** | 0.349 | **0.708** | 0.811 / 0.745 / 0.855 / 0.695 / 0.837 | 0.159 |
| Frangi (sigma 1 to 2.5, dark ridges) | 0.761 | 0.344 | 0.512 | 0.804 / 0.692 / 0.778 / 0.737 / 0.830 | 0.139 |
| Hessian dark ridge (sigma 1 to 3) | 0.750 | 0.239 | 0.588 | 0.820 / 0.710 / 0.773 / 0.714 / 0.793 | 0.110 |
| LIOT count (32 order bits) | 0.725 | **0.517** | 0.445 | 0.763 / 0.720 / 0.719 / 0.755 / 0.817 | **0.099** |
| black-hat 9 px (relative) | 0.707 | 0.276 | 0.407 | | 0.145 |
| black-hat on a crude FFT-notched image | 0.488 | 0.331 | 0.405 | | 0.141 |

Reading (S): (1) the training-free CrackCue coarse cue is the only fixed cue that beats raw darkness overall (+0.044) and in 4 of 5 sources, with equal low-contrast AUROC; (2) LIOT is the most source-invariant cue (spread 0.099 vs 0.276) and the only one as good as raw against line structures, but weak on low-contrast cracks; (3) every ridge-type cue scores line structures (busbars, gridlines, ribbons, borders) above cracks (AUROC vs lines < 0.5), so false alarms on lines are the shared risk; (4) my FFT notch is a crude proxy (zero every axis frequency above 5x the axis median), so it does **not** test eCS or MPTCE. A per-pixel AUROC cannot show what a CNN adds on top of raw input; these numbers rank cues and flag risks, they do not predict a gain.

**C. Cue constants** (E, `T5_precheck/t5_cue_stats.out`, label-free, 532 pool images, I in [0, 1]): CrackCue coarse mean 0.0945 sd 0.1494; LIOT channels left / right / top / bottom mean 0.3905 / 0.3896 / 0.3723 / 0.3732, sd 0.4460 / 0.4459 / 0.4308 / 0.4308.

### 0.3 Provenance
`T5_precheck/t5_precheck.py` 41164dd8, `.out` 40bd3772, `t5_cue_stats.py` 3d7ff873, `.out` ef6aac00, `t5_geom_precheck.py` faa633b8, `.out` de9f3a60 (arm 4 targets: 99.2% of crack px get an orientation target; 95.8% keep their bin within +-1 under a 1 px label shift; FIDT target correlation under a 1 px shift median 0.919 vs binary IoU 0.548). Run with `~/mtp/research/.venv/bin/python -I` (numpy 2.5.3, scipy 1.18.1, scikit-image 0.26.0). Images from `~/mtp/datasets/BenchmarkELimages/dataset_20211104/images_{train_original,val}`, masks from `benchmark/out/masks_v11/masks`; the script asserts 532 stems, none in test50 or e1_106.

---

## 1. Cards (ordered by status, then scout rank)

### 1.1 rank 14: Full-Resolution Network and Dual-Threshold Iteration (FR-UNet), JBHI 2022
- Ids: doi:10.1109/jbhi.2022.3188710. Code: https://github.com/lseventeen/FR-UNet (R: README says MIT licence, official PyTorch code; verified by fetch).
- Claims (R, abstract via search results; paper full text not retrieved): best Sen, AUC, F1, IoU on most of DRIVE, CHASE_DB1, STARE, DCA1, CHUAC with fewer parameters; DTI "greatly improves" sensitivity and connectivity. No DTI ablation number retrieved (unverified). Third-party leaderboard numbers exist but I did not verify them against the paper, so I do not cite them.
- Evidence check (R, code read): `config.yaml` uses threshold 0.5, threshold_low 0.3, DTI true, fast_DTI false, 40 epochs, Adam 1e-4, BCE. In `utils/helpers.py` the DTI loop compares `gbin_pre.all() != gbin.all()` after aliasing `gbin_pre = gbin`, so it makes **one raster pass** (in-place, so growth propagates along the scan direction only); the "fast" variant starts from the low-threshold mask and returns it unchanged. So the published DTI is a one-pass, scan-order hysteresis, not full hysteresis (S from code reading).
- Hypothesis for our data (S): house crack predictions break long cracks into pieces and miss faint segments next to confident ones (E1: 70% of crack px at p < 0.001; in-distribution relR@2 0.866 at relP@2 0.930). Growing low-margin pixels that touch high-margin crack, instead of shifting the whole threshold (the val-chosen bias, already run: BRIEF 5 "Inference"), should raise relR@2 at fixed relP@2, since new pixels are only added next to existing detections. The full-resolution stream is the second mechanism: our decoder has no full-resolution skip (0.1), but the oracle ceiling (0.2 A) and R5 say resolution is not the binding limit.
- Overlap: the global logit bias was run (Track M FINAL, +0.75); a connectivity-conditional threshold was not. No full-resolution branch was run; R5 (2x input) is the closest null but also changed every receptive field relative to the image.
- Status: **RUN_NOW** (arm `dti_hysteresis`, CPU only on wave-1 dumps). The full-resolution branch is arm `fullres_detail_head`, **RUN_AFTER_GATE** (gate: the grid-snap pre-check on W1a dumps, spec arm 5).

### 1.2 rank 7: CrackCue, coarse-to-fine crack cue, Pattern Recognition 2025
- Ids: doi:10.1016/j.patcog.2025.112107, arXiv 2507.16851 (full text read, HTML).
- Claims (R): coarse background = max-pool k 8 then 8x upsample; a skip-free encoder-decoder (10 + 10 conv layers) refines it, trained with L_rec = mean((1 - Y_d) * (I - B_f)^2), Y_d = GT dilated to width 4 (needs pixel labels); cue Q = |I - B_f| concatenated to the image; loss BCE + 1.0 * L_rec. Trained on CrackTree260, 512 px, 700 epochs, Adam 1e-4. Cross-dataset average ODS: U-Net 0.870 to 0.905, CrackFormer 0.832 to 0.900, DeepCrack 0.901 to 0.924. Low contrast: U-Net 0.668 to 0.842; defocus 0.739 to 0.795. **Ablation on CrackLS315 (U-Net, ODS, baseline 0.790): coarse cue without refinement 0.833, refined 0.847, median 0.816, black-hat 0.799, Canny 0.779; pool k 4 / 8 / 12 = 0.825 / 0.847 / 0.819.**
- Evidence check (R/S): the ablations were run on a reported test set (CrackLS315), so the hyperparameters were tuned on test; numbers are single runs, no seeds. Still, most of the gain (0.043 of 0.057) comes from the **training-free coarse cue**, which needs no labels and no extra network. Our pre-check (0.2 B, E) agrees in direction: the coarse cue is the best fixed cue (AUROC 0.806 vs raw 0.762) and the most even across sources after LIOT.
- Code: none released ("will be publicly available", R). Implementation is a few lines (max-pool, interpolate).
- Hypothesis (S): EL cracks are thin dark lines on a brighter cell; a cue that is high where a pixel is darker than its 8 px neighbourhood maximum normalises source contrast (CSIR, BMRK weak) and gives the stem a crack-shaped signal before the first stride. Fingers, busbars and borders also light it up (AUROC vs lines 0.349, E), so the raw channel must stay.
- Status: **RUN_NOW** (arm `crackcue_input`, coarse cue only). The learned refinement (per fold, crack + inactive masked, train stems only) is a follow-up gated on that arm passing.

### 1.3 rank 18: LIOT, Local Intensity Order Transformation, IEEE TIP 2022
- Ids: doi:10.1109/tip.2022.3155954, arXiv 2202.12587 (full text read). Code: https://github.com/TY-Shi/LIOT (from the paper; licence unverified).
- Claims (R): 4 channels (left, right, top, bottom), each sum over distances i = 1..8 of [f(p) > f(n_i)] * 2^(i-1), values 0 to 255; **replaces** the raw image (no raw + LIOT variant, no ablation on neighbour count). IterNet backbone, 128 px crops. In-dataset F1: CrackTree 0.754 to 0.790, DRIVE 0.821 to 0.814, STARE 0.826 to 0.810, CHASE 0.811 to 0.792 (average 0.803 to 0.801). Under universal perturbations F1 0.455 to 0.691. Cross-retina average F1 0.735 to 0.767, specificity 0.969 to 0.966. Retina to CrackTree F1 0.110 to 0.499.
- Evidence check (S): the gains are under shift and perturbation, not in-distribution (in-distribution is flat or slightly worse on retina). CrackCue's Table 1 / 2 (R) report LIOT between baseline and CrackCue and LIOT dropping under blur for CrackFormer (0.697 to 0.597).
- Our pre-check (E): LIOT has the smallest per-source AUROC spread (0.099 vs raw 0.276) and is the only cue as good as raw against line structures (0.517), but weak on low-contrast cracks (0.445).
- Hypothesis (S): our in-distribution CV screen will show at best a small gain; the case for LIOT is source and module shift (E1 CSIR half-cuts, BMRK). It therefore needs the perturbation probe in the spec (held-out fold images under gamma / contrast / blur changes) as its main secondary, since E1 is sealed.
- Overlap: inference-time intensity normalisation failed (BRIEF 5 "Inference"); that is a different mechanism (a fixed rescale at test, not a learned order code at train and test). The house already trains with brightness / contrast jitter of 0.2, which covers part of the invariance (S).
- Status: **RUN_NOW** (arm `liot_input`, raw + LIOT through a zero-initialised side conv).

### 1.4 rank 16: FIDT maps, IEEE TMM 2022
- Ids: doi:10.1109/tmm.2022.3203870, arXiv 2102.07925 (abstract read). Code: https://github.com/dk-liang/FIDTM (linked from the abstract page, R; licence unverified).
- Claims (R): focal inverse distance transform maps replace Gaussian density maps for crowd localisation; an I-SSIM loss; local-maxima read-out; state of the art on six crowd sets and one vehicle set. The exact formula constants were not in the abstract page (unverified; the scout wrote 1 / (d^(a d + b) + c)).
- Hypothesis (S): a crack label jittered by 1 px changes a binary target completely but a distance-based target only slightly. Regressing a peaked distance map of the crack skeleton as an **auxiliary, training-only** head gives the shared decoder a jitter-tolerant signal about where the crack centreline is, without changing the argmax read-out. The scout's ridge-NMS read-out at per-source width is kept out of the screen (it needs the source at inference and would mostly change width, S).
- Overlap: offset-tolerant CE (n.d.) and Skeleton Recall (w 1.0 wider, w 0.1 narrow E1 pass) tolerate shift in the loss of the main head (BRIEF 5 "Loss"); none added a regression head. Not the same mechanism.
- Status: **RUN_NOW**, stacked with orientation in arm `thin_geometry_aux` (argued in the spec).

### 1.5 rank 37: Joint learning of orientation and segmentation (road connectivity), CVPR 2019
- Ids: doi:10.1109/cvpr.2019.01063. Code: https://github.com/anilbatra2185/road_connectivity (scout; I did not open it, unverified). CVF page returned 403 to my fetch, so the claims are the scout's: better APLS connectivity on SpaceNet and DeepGlobe with the orientation task (numbers not read, unverified).
- Hypothesis (S): orientation of a crack skeleton is stable under 1 to 2 px label jitter, so a binned orientation target on and near the skeleton is a clean auxiliary signal for long thin structures; most of our crack components are short (76 to 88% under 20 px, BRIEF 2), so the expected effect is on long cracks and component recall, not on pixel IoU.
- Status: **RUN_NOW**, in arm `thin_geometry_aux`. The gridline extension (scout's second target) stays parked until the crack version is read.

### 1.6 rank 22: SUPER module, arXiv 2025
- Ids: arXiv 2511.11015 (full text read, HTML). Code: none ("will be made available", no link, R).
- Claims (R): replaces a U-Net decoder block's upsample + refine: 1x1 compress the skip to C_d / 4, orthonormal Haar DWT (4 subbands), add h(deeper decoder) to LL (or concat), band-wise GroupNorm, decoder block F_d, CBAM, tanh, times a learnable per-channel scale, subtract from the subbands, inverse DWT, 1x1 expand. FACS-Net on CrackVision12K: **IoU on 0 to 2 px cracks 0.356 to 0.451**, 2 to 4 px 0.398 to 0.415, average 0.629 to 0.646; decoder MACs 156.6 G to 53.7 G.
- Evidence check (R/S): the step-by-step ablation is on depth estimation only, not on cracks; the paper does not say which decoder stages get the module, nor the training resolution, schedule or seeds. Wavelet U-Net++ is listed with a higher 2 to 4 px IoU (0.417). Single numbers, no variance.
- Hypothesis (S): suppression in the detail subbands at the stride-2 node could remove finger / texture responses and keep crack detail, improving strict crack IoU and pixel precision. Given 0.2 A, I expect less than the paper's 0 to 2 px gain.
- Status: **RUN_AFTER_GATE** (arm `super_decoder_x03`; gate: the grid-snap pre-check of spec arm 5 passes, or arm `fullres_detail_head` passes on strict crack IoU).

### 1.7 rank 79: IterNet, WACV 2020
- Ids: arXiv 1912.05763 (abstract read). Code: https://github.com/conscienceli/IterNet (scout; abstract page says code is available, URL unverified by me).
- Claims (R): a shared-weight mini-UNet iterated on the segmentation output with skip connections; AUC DRIVE 0.9816, CHASE-DB1 0.9851, STARE 0.9881, from 10 to 20 labelled images.
- Hypothesis (S): a learned completion stage could join broken crack segments. It is the learned version of DTI; if rule-based growth at matched precision does not pay on our dumps, a learned grower is unlikely to pay more for its build cost.
- Status: **RUN_AFTER_GATE** (gate: `dti_hysteresis` passes). Sketch in spec section 8.

### 1.8 rank 67: Dynamic Snake Convolution (DSCNet), ICCV 2023
- Ids: doi:10.1109/iccv51070.2023.00558, arXiv 2307.08388 (abstract read). Code: https://github.com/YaoleiQi/DSCNet (R: MIT licence, PyTorch; 2D code in `DSCNet_2D_opensource`; verified by fetch).
- Claims: abstract (R) states better accuracy and continuity on 2D and 3D sets without numbers on the abstract page; the scout's full-text numbers (DRIVE Dice 82.06, clDice 82.07; roads Dice 78.21) are unverified by me.
- Hypothesis (S): snake kernels follow long tortuous lines; 76 to 88% of our crack components are under 20 px, and deformable sampling at stride 1 to 2 on 512 px is costly in memory. Expected effect on our best score is small; as an official, widely cited thin-structure method it belongs in the benchmark suite.
- Status: **BENCH_ONLY** (official 2D DSCNet under the protocol, step-matched). An in-house DSConv decoder at the stride-2 node would follow only if arm 5 or 6 passes (same gate as SUPER).

### 1.9 rank 52: Enhanced Crack Segmentation (eCS), IEEE J. Photovoltaics 2019
- Ids: doi:10.1109/JPHOTOV.2019.2895808. Full text PDF (FAU) pages 2 to 5 read. Code: `ecs_algorithm_v1.zip` on the FAU page (R: Python 3.5.4, skimage 0.13.0, OpenCV 3.4.3; licence unverified).
- Claims (R): 47 multicrystalline EL images of 1024 px (40 test, 7 val); preprocessing = Fourier filter zeroing gridline frequencies, cell / busbar masking by morphology, histogram equalisation, bilateral filter; then an **anisotropic** Hessian vesselness (asymmetry n, sigma_a) with a global threshold. Parameters by grid search: beta 0.5, c 0.05, n 1.5, sigma_a 2.0, t 0.9. ROC AUC: eCS1.5 0.9114, Frangi (sigma 1, 2) 0.9094, global threshold 0.2266.
- Evidence check (S): the eCS gain over plain Frangi is 0.002 AUC on 40 images. It is the field's only published, code-released classical reference for EL cracks, so it is the right non-learned floor for a benchmark.
- Our pre-check (E): fixed Frangi has AUROC 0.761 on our pool, equal to raw darkness, and fires on line structures (0.344).
- Status: **BENCH_ONLY** (classical reference row; also tells readers what learning adds). The Fourier notch as an input channel is parked with MPTCE (1.12).

### 1.10 rank 87: XNet v2, arXiv 2024
- Ids: arXiv 2409.00947 (abstract read). Code: https://github.com/Yanfeng-Zhou/XNetv2 (R: linked from the abstract; licence unverified).
- Claims: abstract (R) reports state-of-the-art semi-supervised and competitive fully supervised results on 3 2D and 2 3D sets, no numbers on the page; the scout's supervised numbers (GlaS 81.54 to 84.03 etc.) are unverified by me.
- Hypothesis (S): the LF / HF image remix is a label-safe augmentation that might help BMRK and inactive, but it is an augmentation, not a thin-structure module; the full three-branch model is a wavelet-based baseline for the suite.
- Status: **BENCH_ONLY** (supervised XNet v2 under the protocol). The remix augmentation is parked (belongs to an augmentation family).

### 1.11 rank 80: Frangi-Net, arXiv 2017
- Ids: arXiv 1711.03345 (abstract read). Code: none found.
- Claims (R): Frangi vesselness rewritten as a pre-weighted network, equivalent to the filter at init; after training on 45 fundus images, F1 up to +17% over the fixed filter.
- Our pre-check (E): the fixed dark-ridge Frangi is no better than raw darkness on our pool (0.761 vs 0.762), and below the CrackCue coarse cue (0.806); it fires on lines (0.344).
- Status: **PARKED** (cost: a trainable Hessian branch for a cue that does not beat the cheaper one; reopen as the learned variant if `crackcue_input` passes and its false alarms are on lines).

### 1.12 rank 66: Multi-Period Texture Contrast Enhancement (MPTCE / TexWDS), arXiv 2026
- Ids: arXiv 2603.14282 (abstract read; sole author Zihan Zhang). Code: none found.
- Claims (R, abstract): wafer defects; +8.3% mAP50-95, +7.7% recall, about 8.6% fewer false positives for the full framework. The module-only numbers (recall 71.2 to 73.7 etc.) are the scout's, unverified by me.
- Hypothesis (S): fingers and busbars are periodic and cracks are not, so periodic suppression should cut line false alarms, which is exactly the shared risk of every input cue (0.2 B). But no code, YOLO detection base, RGB wafers; a frequency-domain feature module needs careful per-image peak picking for half-cut layouts.
- Status: **PARKED** (priority; reopen if the input arms pass but their false alarms concentrate on fingers / busbars / gridlines in the per-class FP table).

### 1.13 rank 39: Haar Wavelet Downsampling (HWD), Pattern Recognition 2023
- Ids: doi:10.1016/j.patcog.2023.109819. Code: https://github.com/apple1986/HWD (R: `HWD.py` defines `Down_wt` = pytorch_wavelets Haar DWT (J 1, zero padding), concat LL + 3 detail bands (4 x C), 1x1 conv, BN, ReLU; licence not shown on the page, unverified; needs `pytorch_wavelets`, but a Haar DWT is 4 fixed 2x2 kernels and needs no package).
- Claims: the README names CamVid and Synapse but shows no numbers (R); abstract-level gains reported by the scout, no thin-structure numbers.
- Hypothesis (S): replacing the ResNet max-pool (before the stride-4 skip) keeps high-frequency detail in subband channels. But the max-pool acts on post-ReLU features in which a dark-line detector responds positively, so max-pool does not obviously erase cracks there; and the stride-2 skip already bypasses it. Expected gain small.
- Status: **PARKED** (priority; cheap to add later as a variant of arm 6 if SUPER passes).

### 1.14 rank 71: FMS2, flow matching for segmentation and synthesis of thin structures, arXiv 2026
- Ids: arXiv 2603.13659 (abstract read). Code: none linked (R).
- Claims (R, abstract): SegFlow (2.96 M parameters) mean IoU 0.511 to 0.599 on five crack and vessel sets; Betti matching error 82.1 to 51.5; SynFlow pairs reach near-full performance with 25% of labels; cross-domain IoU +0.11.
- Hypothesis (S): mainly a synthesis method (data family); SegFlow would be a benchmark entry if code appears. Rebuilding both from the paper is weeks of work.
- Status: **PARKED** (no code; re-check for a release before the suite is frozen).

---

## 2. Summary

| Rank | Paper | Status | Arm |
|---|---|---|---|
| 14 | FR-UNet (DTI; full-res stream) | RUN_NOW | dti_hysteresis; fullres_detail_head (gated) |
| 7 | CrackCue | RUN_NOW | crackcue_input |
| 18 | LIOT | RUN_NOW | liot_input |
| 16 | FIDT maps | RUN_NOW | thin_geometry_aux |
| 37 | Orientation + segmentation | RUN_NOW | thin_geometry_aux |
| 22 | SUPER | RUN_AFTER_GATE | super_decoder_x03 |
| 79 | IterNet | RUN_AFTER_GATE | iternet_refine (follow-up) |
| 67 | DSCNet | BENCH_ONLY | suite |
| 52 | eCS | BENCH_ONLY | suite |
| 87 | XNet v2 | BENCH_ONLY | suite |
| 80 | Frangi-Net | PARKED | |
| 66 | MPTCE | PARKED | |
| 39 | HWD | PARKED | |
| 71 | FMS2 | PARKED | |

No paper is VOID: none of these mechanisms appears in BRIEF section 5 under the same conditions. The nearest rows are Track M R5 (2x input, n.d.) for the full-resolution stream and the val-chosen logit bias for DTI; both differ in mechanism (0.1, 1.1).
