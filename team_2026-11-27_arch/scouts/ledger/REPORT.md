# Ledger reconciliation: 12 Nov paper ledger against what ran up to 27 Nov

Scout `ledger`, 27 Nov 2026. Read only; nothing trained or written on any server. Row-level detail in `reconcile.tsv` (105 rows, one per MASTER.tsv row with status RUN_NOW or RUN_AFTER_GATE).

**Sources.** `ref/MASTER.tsv`, `ref/THESIS_TABLES.md` (T6, T7a, T15, T16a, T16b, T18, T21), `ref/thesis_27nov.txt` (Appendix H.3 to H.7). On the server, read only, `team_2026-11-12_frontier/`: `log.md`, `cards/WAVE2_REVIEW.md`, `cards/WAVE3_REVIEW.md`, the `results/*_READ.md` files, `results/stageA/*`, `results/stageB/*`, `results/stageC/GAP_CENSUS.md`, `results/severity/*`, `results/t3b_open9_read/verdict.txt`, and `harness/t3b/T3B_RULE.md`. In the TSV, `frontier/` stands for that folder.

**Scope note.** The ledger has **0 PROMOTE rows**. The 10 PROMOTE papers were carded on 15 Nov (T14) and became 4 RUN_AFTER_GATE, 1 PROTOCOL, 1 BENCH_ONLY and 4 PARKED rows. The 4 RUN_AFTER_GATE rows are included here (P044, P117, P166, P210). So the active set is 44 RUN_NOW plus 61 RUN_AFTER_GATE, 105 rows in all. Two rows have pid `EXTRA`: STEAL is RUN_NOW and ADELE is RUN_AFTER_GATE.

## 1. Counts

| status_1112 | ran: yes | partly | no | total |
|---|---|---|---|---|
| RUN_NOW | 10 | 5 | 29 | 44 |
| RUN_AFTER_GATE | 5 | 3 | 53 | 61 |
| **all** | **15** | **8** | **82** | **105** |

In distinct arms, about 60 arms sit behind the 105 rows. Arms that trained a model after 12 Nov:
- wave 2a: rcs, ema_wise_posthoc (only the EMA readout), soft_band_jml with its jml_hard control, swad_const, encoder_spd
- wave 2b: la_ce, layered_ci
- the few-shot track (E1 opening #9)

CPU-only arms that ran: classbias_xfit, dti_hysteresis, src_calib, msc_tta, ci_error_atlas, gap_census, the ci_rules pre-check, and the severity analyses. **Of everything that ran, only swad_const and msc_tta (as D4) reached the final recipe C2.** classbias_xfit passed and became the OP-C comparator. Everything else failed, was null, or was parked. Wave 2b's crack arms and all of wave 3's GPU arms were never built. The 17 Nov log line reads: "Not built (specs only): layered_ci, la_ce, ens_kd_jml, pool_ens_distill, gin_ipa, dec_gn_pf, label_jitter_crack, trace_crack and other wave-2 crack arms (pre-checks mostly not run), benchmark rows C3, t3b_fewshot". layered_ci and la_ce ran later that day. On 22 Nov the user ruled "no new experiments after the few-shot track".

Gates that **opened but were never acted on**:
- P1 (pool_ens_distill): the ensemble's edge over a single model was +0.0116 strict crack IoU [+0.0080, +0.0155], above M = 0.010.
- G5 (ens_kd_jml): passed.
- gap_census: OPEN (trace_crack, and room for continuity arms in general).
- T6 gate 1 (vfm_ctx): BUILD on W1-C1, LEAD DECIDES on W1-G.
- P298's gate (an architecture passes its screen): met by HRNet-W18.
- P142 sam's reopen condition (swad_const passes): met.

## 2. Never-run items ranked by still_promising (0 to 5)

How the scores were set: what we have learned since 12 Nov moves each arm up or down.
- Up: an encoder-side resolution lever (stride 8 loses 0.077, stride 4 loses about 0.01 to 0.02, HRNet-W18 is the only encoder that wins). Up: unseen-module recall (E1 relR@2 0.42) or the half-cut layout gap. Up: the arm uses the 8 free GPUs with config-only work.
- Down: decoder-only changes (no decoder effect was detected). Down: label-placement and strict-IoU devices (relF1@2 contrasts move at most 0.003 under any label variant). Down: semi-supervised or pseudo-label routes at full labels (they helped only at 5 to 10% labels). Down: foundation encoders fine-tuned as plain encoders (A8 DINOv3 ConvNeXt-T was a KILL).
- No row scores 4 or 5. No never-run arm has project evidence of a crack gain; the 3s are untested bets aimed at the known weak points.

Within a score, the order is my judgement (architecture and resolution first, then data that adds unseen layouts, then losses).

**Score 3**

- P002 (RUN_NOW, `hiera_bp_unetpp_pf`) SAM2-UNet: segment anything 2 makes strong encoder for natural and med: hierarchical stride-4 encoder in the HR-stem U-Net++ = config only on a free machine; encoder-side change is where the only win (HRNet) came from; tempered by A8 DINOv3 ConvNeXt-T KILL and the stride-4 head penalty (A5); arm 4 frozen+adapters ~2
- P006 (RUN_AFTER_GATE, `nnunet_resenc_2d`) nnU-Net: a self-configuring method for deep learning-based biomedical : stride-1 full-resolution U-Net with deep supervision, long schedule and its own augmentation: the strongest untested reference row; from scratch on 478 cells is a risk (ImageNet init mattered)
- P020 (RUN_AFTER_GATE, `nnunet_resenc_2d`) nnU-Net Revisited: A Call for Rigorous Validation in 3D Medical Image : stride-1 full-resolution U-Net with deep supervision, long schedule and its own augmentation: the strongest untested reference row; from scratch on 478 cells is a risk (ImageNet init mattered)
- P030 (RUN_AFTER_GATE, `vfm_ctx_r34_pf`) Do Vision Foundation Models Enhance Domain Generalization in Medical I: frozen foundation-model context beside a CNN: strongest DG evidence for unseen domains (P030 frozen DINOv2 DG Dice 31 vs 2); A8 KILL tested a fine-tuned DINOv3 ConvNeXt-T encoder, not a frozen ViT context branch; Dino U-Net keeps a conv HR spatial branch
- P043 (RUN_AFTER_GATE, `vfm_ctx_r34_pf`) Dino U-Net: Exploiting High-Fidelity Dense Features from Foundation Mo: frozen foundation-model context beside a CNN: strongest DG evidence for unseen domains (P030 frozen DINOv2 DG Dice 31 vs 2); A8 KILL tested a fine-tuned DINOv3 ConvNeXt-T encoder, not a frozen ViT context branch; Dino U-Net keeps a conv HR spatial branch
- P005 (RUN_NOW, `pool_ens_distill`) Naive-Student: Leveraging Semi-Supervised Learning in Video Sequences : only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P080 (RUN_NOW, `pool_ens_distill`) Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P051 (RUN_NOW, `pool_ens_distill`) Rethinking Pre-training and Self-training: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P022 (RUN_NOW, `pool_ens_distill`) The Surprising Effectiveness of Canonical Knowledge Distillation for S: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P157 (RUN_NOW, `pool_ens_distill`) Data Distillation: Towards Omni-Supervised Learning: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P180 (RUN_NOW, `pool_ens_distill`) Self-Training With Noisy Student Improves ImageNet Classification: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P014 (RUN_NOW, `pool_ens_distill`) Knowledge distillation with ensembles of convolutional neural networks: only arm family with an open gate that uses the 4,949-cell unlabelled pool, including half-cut cells absent from the labelled pool; C2+D4 ensemble is a stronger teacher than the PF pair; but SSL/pseudo-labels helped only at 5-10% labels and the 5-seed ensemble added nothing on E1
- P037 (RUN_NOW, `ucf_partial_joint`) Marginal loss and exclusion loss for partially supervised multi-organ : joint partial-label training with UCF-EL adds labelled cells from other modules and cell types; unseen-module recall is the weak point and labelled layout data was the one big lever (few-shot +0.22); UCF pretrain-then-finetune was worse (P15), joint training untested
- P077 (RUN_NOW, `ucf_partial_joint`) Multi-domain semantic segmentation with overlapping labels: joint partial-label training with UCF-EL adds labelled cells from other modules and cell types; unseen-module recall is the weak point and labelled layout data was the one big lever (few-shot +0.22); UCF pretrain-then-finetune was worse (P15), joint training untested
- P011 (RUN_NOW, `ucf_partial_joint`) MultiTalent: A Multi-Dataset Approach to Medical Image Segmentation: joint partial-label training with UCF-EL adds labelled cells from other modules and cell types; unseen-module recall is the weak point and labelled layout data was the one big lever (few-shot +0.22); UCF pretrain-then-finetune was worse (P15), joint training untested
- P223 (RUN_NOW, `ucf_partial_joint`) Combining partially labelled binary datasets: other-class positives as: joint partial-label training with UCF-EL adds labelled cells from other modules and cell types; unseen-module recall is the weak point and labelled layout data was the one big lever (few-shot +0.22); UCF pretrain-then-finetune was worse (P15), joint training untested
- P034 (RUN_AFTER_GATE, `mic_halfcell`) MIC: Masked Image Consistency for Context-Enhanced Domain Adaptation: UDA self-training on unlabelled pool half-cut cells directly targets the missing half-cut layout; risk: 70% of E1 crack px get p < 0.001, so pseudo-labels may teach background on cracks
- P056 (RUN_AFTER_GATE, `fullres_detail_head`) When Semantic Segmentation Meets Frequency Aliasing: parameter-free de-aliasing in the encoder stride-2 stages: an encoder-side resolution fix, the side where HRNet won; cheap
- P028 (RUN_NOW, `thin_geometry_aux`) Focal Inverse Distance Transform Maps for Crowd Localization: training-only aux heads (distance map, orientation) aimed at crack component recall; gap_census OPEN says continuity/recall has room; zero inference cost; fits on C2
- P062 (RUN_NOW, `thin_geometry_aux`) Improved Road Connectivity by Joint Learning of Orientation and Segmen: training-only aux heads (distance map, orientation) aimed at crack component recall; gap_census OPEN says continuity/recall has room; zero inference cost; fits on C2
- P115 (RUN_NOW, `cc_dicece_crack`) Learning to Look Closer: A New Instance-Wise Loss for Small Cerebral L: per-component (instance-aware) Dice/CE targets missed small cracks, i.e. crack recall, the weak point; cheap loss change on C2

**Score 2**

- P129 (RUN_AFTER_GATE, `cc_dicece_multi`) Instance Awareness of Multi-class Semantic Segmentation Loss Functions: multi-class follow-up
- P107 (RUN_NOW, `clce_crack`) The Centerline-Cross Entropy Loss for Vessel-Like Structure Segmentati: Skeleton Recall (its recall half) helped E1 singly (SKR2 +0.036) but failed as ensembles and did not replicate (SKR2C); clce adds the clDice half, which failed
- P060 (RUN_NOW, `coletra_crack`) Disconnect to Connect: A Data Augmentation Method for Improving Topolo: connectivity augmentation; gap_census OPEN gives continuity room, but primary relR@2 shares the census ceiling caveat
- P040 (RUN_AFTER_GATE, `ens_kd_jml`) TopoMortar: A dataset to evaluate image segmentation methods focused o: labelled-set distillation of an ensemble that gave +0.011 in-distribution; E1 ensemble gain n.d.
- P151 (RUN_AFTER_GATE, `fullres_detail_head`) Frequency-aware Feature Fusion for Dense Image Prediction: decoder upsampler; no decoder effect detected (U-Net vs U-Net++)
- P012 (RUN_NOW, `gin_ipa`) Causality-Inspired Single-Source Domain Generalization for Medical Ima: appearance randomisation for unseen sources; no instrument can see its expected +0.01 to +0.04 (E1 is now training data); needs the new unseen set
- P092 (RUN_AFTER_GATE, `hiera_bp_unetpp_pf`) Fracture-Informed CNN-Transformer Ensemble for Multiclass Photovoltaic: CPU readout; HRNet + PF dumps now exist so a hetero pair is free, but the 5-seed ensemble added nothing on E1 (-0.0025)
- P410 (RUN_AFTER_GATE, `icl_oof_probe`) SANSA: Unleashing the Hidden Semantics in SAM2 for Few-Shot Segmentati: few-shot SAM2 adapters; same as above
- P033 (RUN_NOW, `liot_input`) Local Intensity Order Transformation for Robust Curvilinear Object Seg: contrast-invariant input channels could help unseen sources (CSIR contrast), but in-distribution flat by design and no instrument for the robustness claim
- P008 (RUN_NOW, `matched_crack_head`) MatchED: Crisp Edge Detection Using End-to-End, Matching-based Supervi: one-to-one matching loss for 1-2 px cracks; placement undecided (D0 0.60); headline already tolerant
- P394 (RUN_AFTER_GATE, `mic_halfcell (follow-up)`) HRDA: Context-Aware High-Resolution Domain-Adaptive Semantic Segmentat: high-res detail + context fusion inside UDA; resolution matters, but only after mic works
- P019 (RUN_NOW, `oof_soft_distill`) Study Group Learning: Improving Retinal Vessel Segmentation Trained wi: out-of-fold soft teachers; addresses label jitter, which the tolerant headline already absorbs
- P061 (RUN_AFTER_GATE, `pool_ens_distill`) Knowledge distillation: A good teacher is patient and consistent: online function-matching follow-up of arm 1
- P298 (RUN_AFTER_GATE, `pool_ens_distill`) Distilling Knowledge from Heterogeneous Architectures for Semantic Seg: heterogeneous teacher; HRNet now is the student-side architecture, so little left to transfer
- P327 (RUN_NOW, `sam_prompt_refine`) Exploring few-shot defect segmentation in general industrial scenarios: SAM2 video-mode few-shot labeller: relevant to labelling new layouts cheaply, not to the zero-shot model
- P021 (RUN_AFTER_GATE, `ucf_partial_joint`) MultiSolSegment: Multi-channel segmentation of overlapping features in: second external set (dark ~ inactive); licence unknown
- P069 (RUN_AFTER_GATE, `vfm_ctx_r34_pf`) Stronger, Fewer, & Superior: Harnessing Vision Foundation Models for D: follow-up variants (Rein tokens, dual-branch PEFT) of an arm that never ran
- P145 (RUN_AFTER_GATE, `vfm_ctx_r34_pf`) DINOv3-PEFT: A Dual-Branch Collaborative Network with Parameter-Effici: follow-up variants (Rein tokens, dual-branch PEFT) of an arm that never ran
- P190 (RUN_AFTER_GATE, `vfm_ctx_r34_pf`) DINOv3: DINOv3 ViT-L as context backbone; gated licence (user OK); behind arm 2

**Score 1**

- P377 (RUN_AFTER_GATE, `-`) Near, far: Patch-ordering enhances vision foundation models' scene und: dense post-pretraining of a ViT that was never adopted
- P112 (RUN_AFTER_GATE, `ad_prior`) Accurate Industrial Anomaly Detection and Localization Using Weakly-Su: kNN anomaly map; on half-cut cells the whole layout is anomalous against a full-cell bank
- P266 (RUN_NOW, `ad_prior`) SuperADD: Training-free Class-agnostic Anomaly Segmentation (CVPR 2026: kNN anomaly map; on half-cut cells the whole layout is anomalous against a full-cell bank
- P325 (RUN_NOW, `ad_prior`) AnomalyDINO: Boosting Patch-based Few-Shot Anomaly Detection with DINO: kNN anomaly map; on half-cut cells the whole layout is anomalous against a full-cell bank
- EXTRA (RUN_AFTER_GATE, `adele_confident_add`) ADELE: Adaptive Early-Learning Correction for Segmentation from Noisy : merged into oof_add; label errors are a minority
- P016 (RUN_NOW, `crackcue_input`) Coarse-to-fine crack cue for robust crack detection (CrackCue): no faint-crack advantage; only a smaller per-source spread
- P044 (RUN_AFTER_GATE, `dec_gn_pf`) Foreground Sampling and Spatial Support in Pavement Crack Segmentation: decoder normalisation change; no decoder effect detected
- P079 (RUN_AFTER_GATE, `elpv_bmrk_negatives`) Mixed supervision for surface-defect detection: from weakly to fully s: leak cannot be excluded
- P312 (RUN_AFTER_GATE, `elpv_bmrk_negatives`) Weakly Supervised Segmentation of Cracks on Solar Cells using Normaliz: leak cannot be excluded
- P123 (RUN_AFTER_GATE, `ema_wise_posthoc`) Robust fine-tuning of zero-shot models (WiSE-FT): PF already preserves the encoder; post-hoc, cheap, but no evidence it moves recall
- P185 (RUN_AFTER_GATE, `ema_wise_posthoc`) LiNeS: Post-training Layer Scaling Prevents Forgetting and Enhances Mo: PF already preserves the encoder; post-hoc, cheap, but no evidence it moves recall
- P395 (RUN_AFTER_GATE, `fm_align_pool`) RS-MTDF: Multi-Teacher Distillation and Fusion for Remote Sensing Semi: distil frozen VFM features into R34; behind two unbuilt gates
- P057 (RUN_AFTER_GATE, `gin_ipa (fallback)`) Rethinking Data Augmentation for Single-Source Domain Generalization i: same reason as gin_ipa, weaker
- P233 (RUN_AFTER_GATE, `inactive_grid_paste`) Long-Tail Challenges in Electroluminescence-Based Photovoltaic Defect : gate closed; inactive only
- P127 (RUN_AFTER_GATE, `iternet_refine (follow-up)`) IterNet: Retinal Image Segmentation Utilizing Structural Redundancy in: gate closed
- P081 (RUN_AFTER_GATE, `matched_crack_head`) PNT-Edge: Towards Robust Edge Detection with Noisy Labels by Learning : placement noise is random, not a smooth field
- P010 (RUN_AFTER_GATE, `oof_selective_ignore`) Adaptive Early-Learning Correction for Segmentation from Noisy Annotat: crack label errors are a minority (rater 0.244) and ignoring all candidates moved no contrast by > 0.003 (audit F5)
- P035 (RUN_AFTER_GATE, `oof_selective_ignore`) SelectSeg: Uncertainty-based selective training and prediction for acc: crack label errors are a minority (rater 0.244) and ignoring all candidates moved no contrast by > 0.003 (audit F5)
- P032 (RUN_AFTER_GATE, `oof_snap`) Pixel-accurate road crack detection in presence of inaccurate annotati: label alignment from model peaks; headline insensitive to label placement
- P073 (RUN_AFTER_GATE, `oof_snap`) Beyond prompt-only segmentation: Foundation model-guided trust-region : label alignment from model peaks; headline insensitive to label placement
- P042 (RUN_AFTER_GATE, `pvddpm_fold_synth`) Bridging the Data Gap: Spatially Conditioned Diffusion Model for Anoma: generative synthesis of inactive; G-paste closed; synthetic half-cuts were n.d. (HC) / FAIL (HC2)
- P095 (RUN_AFTER_GATE, `pvddpm_fold_synth`) FreeMask: Synthetic Images with Dense Annotations Make Stronger Segmen: generative synthesis of inactive; G-paste closed; synthetic half-cuts were n.d. (HC) / FAIL (HC2)
- P001 (RUN_NOW, `ridge_snap`) Delving Into Crispness: Guided Label Refinement for Crisp Edge Detecti: label placement: relF1@2 already tolerates 2 px and every relF1@2 contrast moved <= 0.003 under label variants (audit F1/F5); targets strict IoU, which decides nothing
- P063 (RUN_AFTER_GATE, `ridge_snap`) Weakly-Supervised Crack Detection: variant of ridge_snap (myopic evidence); same reason
- EXTRA (RUN_NOW, `ridge_snap_labels`) STEAL: Learning Semantic Boundaries From Noisy Annotations: (STEAL / ridge_snap_labels) merged into ridge_snap; same reason
- P319 (RUN_AFTER_GATE, `ridge_snap_labels`) DragOSM: Extract Building Roofs and Footprints from Aerial Images by A: learned label snapper; same reason, more build
- P142 (RUN_NOW, `sam`) Sharpness-Aware Minimization for Efficiently Improving Generalization: weak prior, 2x cost; SWAD covers flat minima
- P046 (RUN_NOW, `scnp_cedice`) Towards High-Quality Image Segmentation: Improving Topology Accuracy b: paper shows Dice = baseline on Crack500
- P004 (RUN_AFTER_GATE, `src_film`) Rethinking Generalization: The Impact of Annotation Style on Medical I: source conditioning: output-side per-source correction already null; a new unseen module has no source id
- P050 (RUN_AFTER_GATE, `src_film`) MuGE: Multiple Granularity Edge Detection: source conditioning: output-side per-source correction already null; a new unseen module has no source id
- P078 (RUN_AFTER_GATE, `src_film`) That Label's Got Style: Handling Label Style Bias for Uncertain Image : source conditioning: output-side per-source correction already null; a new unseen module has no source id
- P038 (RUN_AFTER_GATE, `super_decoder_x03`) SUPER Module for Detail-Sensitive and Cost-Efficient U-Net Variant Dec: decoder module; no decoder effect detected

**Score 0**

- P082 (RUN_AFTER_GATE, `inact_refiner (parked arm)`) rNCA: Self-Repairing Segmentation Masks: gate closed
- P183 (RUN_AFTER_GATE, `inact_refiner (parked arm)`) Multiclass Boundary Refinement with Neural Cellular Automata for Remot: gate closed
- P314 (RUN_AFTER_GATE, `inact_refiner (parked arm)`) Convolutional CRFs for Semantic Segmentation: gate closed
- P210 (RUN_AFTER_GATE, `label_jitter_crack`) Unlocking Robust Semantic Segmentation Performance via Label-only Elas: label jitter = soft band in expectation; parent failed
- P031 (RUN_AFTER_GATE, `soft_band_jml`) Image-Level Regression for Uncertainty-Aware Retinal Image Segmentatio: variants of a failed parent
- P206 (RUN_AFTER_GATE, `soft_band_jml`) Dice Semimetric Losses: Optimizing the Dice Score with Soft Labels: variants of a failed parent
- P332 (RUN_AFTER_GATE, `soft_band_jml`) Boundary-Local Soft Supervision for Reliable Calibration in Defect Seg: variants of a failed parent
- P099 (RUN_AFTER_GATE, `soft_band_jml_geo`) GeoLS: an Intensity-based, Geodesic Soft Labeling for Image Segmentati: variants of a failed parent
- P432 (RUN_AFTER_GATE, `src_calib`) Multi-style conversion for semantic segmentation of lesions in fundus : parent null
- P025 (RUN_AFTER_GATE, `src_cm`) Disentangling Human Error from the Ground Truth in Segmentation of Med: not identifiable with one label per cell; gate closed
### Partly-run rows with an open remainder (not in the list above)
- **P117 trace_crack (3).** The gap_census CPU check passed, with room on both machines. The loss itself was never built: no code, and the equations were never retrieved.
- **P166 surgical partial-freeze rules (3).** The few-shot track ran with plain C2: ALL minus ZS +0.2213 [+0.0977, +0.3504] CONFIRMED, and HALF gave the same gain. Partial-freeze rules for few labels of a new layout were never tried.
- **P026 fullres_detail_head (2).** DTI is closed. The full-resolution head was never built; its grid-snap gate was never computed.
- **P017 / P040 ens_kd_jml (2).** G5 passed. Never built.
- **P068 modern_recipe (1), P003 longer averaging window (1), P045 la_ce_full (1).** Small leftovers.

## 3. PARKED rows (396) whose parking reason no longer holds

I scanned the `note` column of all 396 PARKED rows. 18 rows qualify because their stated reopen condition has since been met, or their reason has been overtaken by a measured result:

| pid | title (short) | parked because (12 Nov note) | why the reason no longer holds |
|---|---|---|---|
| P047 | Better Aggregation in Test-Time Augmentation | covered by msc_tta; "reopen as a cross-fitted readout if msc_tta passes" | msc_tta PASSED its full score claim (D4MS - PLAIN relF1@2 +0.0142 [+0.0079, +0.0202]) and D4 is in C2; learned view weights are a free CPU readout on existing D4 dumps |
| P126 | Deep Nets with Subsampling Layers Unwittingly Discard Useful Activations | "covered by msc_tta infrastructure; 1 px phase-shift views are a 0.5 build-h add-on" | that infrastructure now exists and TTA is the largest crack gain measured. Aliasing matters: A5 found that a stride-4 head binds |
| P384 | S3-TTA: Scale-Style Selection for TTA | "reopens if msc_tta per-scale reads differ by cell type" | msc_tta passed, and its caveat is that TTA cuts half-cell crack volume to 0.18 to 0.51x; per-image scale selection is aimed at exactly that |
| P366 | OCR: Object-Contextual Representations | "HRNet row first; reopen as HRNet+OCR if hrnet_w18_unetpp_pf is competitive" | HRNet-W18 is the winning encoder (screen pass; in C2, which is CONFIRMED on E1). Tempered by "no decoder effect" |
| P198 | BiRefNet (high-resolution dichotomous segmentation) | "lower prior than hrnet_w18 ... as high-resolution rows; reopen if cv02 frees up" | resolution is now the one axis shown to matter, and the 8-GPU training machine is free |
| P469 (+P475) | Dual Super-Resolution Learning | "2x input (BRIEF 5) n.d." | stride-8 -0.077 and the HRNet win show resolution matters; DSRL is a training-only high-res branch with no inference cost (P475 has no code) |
| P064 | Haar Wavelet Downsampling | "no thin-structure numbers; variant of super_decoder_x03 if it passes" | the gain was encoder-side resolution (HRNet), so a lossless drop-in for stride-2 downsampling is now a direct test, not a decoder variant; code exists |
| P122 (+P211) | Model soups (and DiWA) | "soups of forked runs reopen only if those [ema / swad] pass" | swad_const passed its screen and SWAD is in the confirmed C2. A soup costs one forward pass; the C3 5-seed ensemble costs 77x C1 and added nothing on E1 (-0.0025) |
| P179 | Rethinking the Hyperparameters for Fine-tuning | "cost ... Reopen after encoder_spd" | encoder_spd has been read (gate failed). HRNet-W18 under PF has never had its encoder lr or momentum tuned, and the cost argument is gone with 8 free GPUs |
| P338 | Training Beyond Convergence (longer schedules) | "schedule length parked after the stack; 4x to 8x cost" | the stack (C2) exists and the machine is free; a longer run also widens the SWAD window |
| P401 | Enhancing recall in asphalt pavement crack segmentation | "Reopen if dti_hysteresis fails to lift relR@2" | DTI closed (+0.0011 [-0.0016, +0.0062]); recall on unseen modules (0.42) is the weak point. No code |
| P120 | Recall Loss for Semantic Segmentation | "reopen if classbias passes and la_ce fails" | both happened: classbias_xfit PASS, la_ce DROP. Recall is the weak point |
| P363 | PVEL-AD dataset | "user action; crack boxes only; lower prior than UCF joint; reopen after arm 1" | UCF joint never ran. The few-shot result (+0.22) shows labelled data of new layouts is the largest lever, and a large multi-module EL set is the zero-shot counterpart. Needs the user's request form |
| P290 | BoxInst (box-supervised loss) | "needs PVEL-AD; reopen with P363" | reopens with P363: the loss that turns PVEL-AD crack boxes into mask supervision |
| P427 | Active learning via region impurity | "unseen-module pool selection; problem 3 owner" | the owner never acted; few-shot HALF matched ALL (ALL - HALF +0.0171 [-0.0246, +0.0625]), so choosing which new-layout cells to label is now worth doing |
| P375 | A2LC: Active and Automated Label Correction | "needs human correction clicks; conflicts with no-manual-labelling rule" | the rule no longer holds: the user labelled label_pack_U4 (15 Nov) and E1 labels are training data since 23 Nov |
| P414 | AOI-SSL (kNN retrieval head) | "belongs to the E1 few-shot track T3b (last week)" | the few-shot track now exists and is CONFIRMED; a retrieval head is a cheap few-shot add-on for the next new layout |
| P217 | SAGM (sharpness-aware gradient matching) | "Reopen with sam if soft_band_jml or swad_const passes" | swad_const passed its screen. Low prior; listed for completeness |

Groups I did **not** un-park (the reason still holds, but the lead should know):
- **"Covered by gin_ipa"** (P110, P149, P162, P242/P422, P291, P295, P308, P339, P349, P420) and **"covered by mic_halfcell"** (P239, P347, P429, P515, P539). The covering arms never ran, so in practice none of these were tested. They are waiting on the new unseen-module set, because E1 can no longer judge zero-shot.
- **Feature upsamplers** (P093 AnyUp, P096, P160, P226, P253) are "behind a ViT row". If this sweep proposes a ViT or foundation row, resolution matters, so these become its natural add-on.
- **Weak-class representation arms** (P138, P200, P237, P275) stay parked: the atlas G-bias says weak-class errors are decision-limited (bias oracle +0.06 to +0.09), not representation-limited.
- **SAM3 rows** (P041, P175, P273, P383) still need gated weights.
