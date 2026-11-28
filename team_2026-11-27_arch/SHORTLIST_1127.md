# Shortlist of arms, 27 Nov 2026 sweep

Built from the 8 scout reports (`scouts/<id>/REPORT.md`, `papers.tsv`), the ledger reconciliation (`scouts/ledger/REPORT.md`, `reconcile.tsv`), `CONTEXT.md` and `ref/THESIS_TABLES.md`. Nothing was trained. Paper list: `SWEEP_1127.tsv` (674 unique papers). Gaps: `GAPS.md`.

How to read this file:
- An **arm** is one experiment. Papers that would be tested by the same experiment are grouped into one arm.
- **Comparator** for every arm is C2 (the COMBO card: HRNet-W18 encoder, U-Net++ decoder, PF schedule, SWAD steps 10k to 20k, D4 TTA, v1.1 labels, cv5v3).
- **Failure mode** tags: TL = thin-line precision; UR = unseen-source recall; HC = half-cut layout; INA = rare inactive; GEN = generic.
- **Evidence** is copied from the named scout report (in brackets) and marked [FT] when the scout read the full text, [ABS] when only the abstract. "Project" numbers are ours, copied from `ref/THESIS_TABLES.md` (T-table) or the ledger.
- **Judged on cv5v3?** cv5v3 has no half-cut cells and every source appears in training. An effect that only shows on half-cut cells or on unseen sources cannot be read there. The two instruments that exist are U1 (leave-two-sources-out, CSIR and BMRK held out, 164 cells) and U2 (simulated unseen-module views, 1,064). U1 is weak: Skeleton Recall on U1 gave +0.0206 [-0.0518, +0.0744] (THESIS_TABLES l.562), so its interval is about +-0.06 wide and cannot resolve a +0.01 to +0.04 effect. E1 is training data since 23 Nov, so any new zero-shot claim needs a **new unseen set** (see arm L1).

---

## 1. Ranked arms

Rank = expected value for crack relF1@2 under the protocol (M = 0.010, guards) per unit of cost, given what the evidence says and what we already tested. Tier in brackets.

### A01 FULLRES-SKIP: full-resolution stem skip, optional FFT high-band refinement [WAVE 1, builder on]
- Papers: doi:10.1016/j.autcon.2025.106719 (FACS-net, found by general, thin, med, recipe); doi:10.1016/j.eswa.2025.128144 (HACNet V2); doi:10.1364/boe.522482 (FRD-Net); MASTER P026 (FR-UNet, `fullres_detail_head`, never built), P469 (Dual Super-Resolution Learning, un-parked by ledger).
- Change vs C2: add a stride-1 CNN stem whose full-resolution features skip into the last U-Net++ decoder block. Second variant adds FACS-net's FPCM block (FFT low/high split + CBAM) at that last stage.
- Targets: TL (recall of the faintest cracks). Not UR: the FACS-net authors say the architecture alone did not generalise under domain shift (general and thin reports).
- Evidence: CrackVision12K, width-stratified, 256 px, binary, strict IoU, no seeds. Cracks of 2 px or less: 0-2 px IoU 0.356 (FACS-net) vs 0.160 (Hybrid-Segmentor) vs 0.079 (DeepLabV3+); CTS 0.872 vs 0.585 vs 0.101 [FT, general]. Thin scout: +0.306 IoU and +0.360 CTS over Hybrid-Segmentor on the thinnest cracks [FT, thin]. Project: stride 8 loses 0.077 and HRNet-W18 (which keeps a high-resolution stream) is the only encoder above PF (CONTEXT).
- Cost: code (new stem branch + skip; FPCM is a new block). Code released per the paper (repo not opened).
- Judged on cv5v3: yes.
- Conflicts: Track M (2x input) was n.d.; this is different (a stride-1 path, not a bigger input). D22 suspected smp U-Net++ drops the stride-1 skip (general report), so check first what the current decoder already receives.

### A02 AA-DOWN: anti-aliased or polyphase downsampling in the HRNet stem [WAVE 1, builder on]
- Papers: doi:10.1109/tim.2023.3325514 (CAPS); arxiv:1904.11486 (BlurPool); doi:10.1109/tpami.2025.3592621 (SFM, MASTER P218); MASTER P056 (frequency aliasing, ledger score 3), P064 (Haar wavelet downsampling, un-parked), P126 (subsampling layers discard activations, un-parked).
- Change vs C2: replace the stride-2 convs of the HRNet stem (and optionally the stage transitions) with CAPS polyphase sampling; BlurPool as the control.
- Targets: TL, GEN (shift consistency should also make the D4 vote less noisy, general report).
- Evidence: CAPS, micro surface defects (MSD), same U-Net trained from scratch: mIoU 69.8 to 78.2, recall 83.1 to 93.0; BlurPool 73.2 (recall fell to 80.2), LPS 72.0, APS 68.4; output change under 1 px shifts mvIoU 0.0062 to 0.0010 [FT, general]. SFM: Cityscapes UPerNet-R50 78.1 to 79.5 vs BlurPool 78.8; the downsampling half alone costs -0.5 [FT sections, general].
- Cost: code (stem layers); disturbs pretrained weights, which PF protects.
- Judged on cv5v3: yes.
- Conflicts: none tested. Ledger un-parked P064 and P126 on the same reasoning (encoder-side resolution).

### A03 MIRO: mutual-information regulariser to the pretrained encoder, on top of SWAD [MISSING FROM WAVE 1, recommend adding]
- Papers: doi:10.1007/978-3-031-20050-2_26 (MIRO); related doi:10.1016/j.artmed.2021.102078 (Karimi 2021), arxiv:2211.09359 (fine-tune with SGD).
- Change vs C2: add a loss that keeps the HRNet-W18 stage outputs informative about a frozen ImageNet copy; SWAD unchanged.
- Targets: UR, GEN. It is a soft, always-on form of the PF finding that plain fine-tuning erases pretrained deep layers (recipe report).
- Evidence: DomainBed RN50 average 65.9 vs ERM 64.2; **MIRO+SWAD 68.1 vs ERM+SWAD 66.9** (TerraIncognita 52.9 vs 50.0) [FT, recipe]. The only recipe in the sweep shown to add on top of SWAD. Classification only.
- Cost: new loss, about 1.3x step time (recipe).
- Judged on cv5v3: in-distribution effect yes; the DG part needs U1 or the new unseen set.
- Conflicts: none tested; PF already freezes the encoder for 1,000 steps, so the gain may be smaller than in DomainBed.

### A04 ENS-MERGE: post-hoc weight merge and ensemble of averages on existing seeds [WAVE 1, builder on; inference half]
- Papers: doi:10.1007/978-3-031-72784-9_12 (Model Stock); doi:10.52202/068431-0601 (EoA); arxiv:2203.05482 (model soups, MASTER P122, un-parked); arxiv:2205.09739 (DiWA, P211).
- Change vs C2: merge the 5 C2 seeds layer by layer (Model Stock ratio toward the ImageNet weights for the encoder, plain average for the decoder, BN statistics recomputed); uniform soup as control. EoA = ensemble of the 5 SWAD models, which is C3.
- Targets: GEN, INA.
- Evidence: Model Stock: 2 CLIP fine-tunes beat Model Soup on ImageNet and 5 OOD sets [method read, recipe]. EoA: DomainBed RN50 68.0% vs ERM about 64% [ABS, recipe]. Project: C3 (5-seed C2 ensemble) minus C2 on E1 crack relF1@2 -0.0025 [-0.0254, +0.0157], inactive IoU +0.0274 [-0.0321, +0.0786] (T-table l.299); E-PF minus E-house on E1 inactive IoU +0.2141 [+0.0303, +0.3820] PASS (l.722); Track M 5-seed ensemble minus single +0.018 [+0.013, +0.025] supported (l.711).
- Cost: config / inference only (minutes).
- Judged on cv5v3: yes.
- Conflicts: same-architecture ensembles PF2E and SKR2E failed as deployables (with crack bias); C3 added nothing on E1 crack. A merge cannot exceed what C3 gives, so read C3 minus C2 on cv5v3 relF1@2 first.

### A05 POSTPROC-CV: per-class component cutoffs tuned on out-of-fold predictions [MISSING FROM WAVE 1, CPU only, recommend tonight]
- Papers: arxiv:2208.10791 (Extending nnU-Net); arxiv:2411.17213 (Scaling nnU-Net for CBCT).
- Change vs C2: no training. On the cv5v3 out-of-fold predictions, choose a minimum crack-component length and a minimum inactive area per class, selected on relF1@2 (never on IoU), with a held-out split for the cutoff.
- Targets: TL (false crack pixels on crack-free cells, a guard), INA (spurious inactive blobs).
- Evidence: AMOS-2022 winner: residual encoder, larger batch and patch, 15-model ensemble and per-class postprocessing chosen on 5-fold CV [FT, med]. CBCT: per-class cutoffs on 5-fold CV; authors warn the CV numbers are optimistic [FT, med]. No numbers isolate the postprocessing gain.
- Cost: config / CPU.
- Judged on cv5v3: yes (nested split needed).
- Conflicts: DTI hysteresis closed (+0.0011 [-0.0016, +0.0062], ledger); risk of deleting short true cracks and lowering relR on unseen modules.

### A06 UPSAMPLER: guided upsampling in the U-Net++ decoder [WAVE 1, builder on: "content-aware upsampler"]
- Papers: doi:10.1007/s11263-024-02191-8 (FADE); doi:10.52202/068431-1519 (SAPA); doi:10.1109/iccv.2019.00310 (CARAFE) and doi:10.1109/tpami.2021.3074370 (CARAFE++); arxiv:2511.11015 (SUPER, P038); doi:10.1109/tpami.2024.3449959 (FreqFusion, P299; also P151).
- Change vs C2: replace the bilinear/transposed upsampling steps of U-Net++ with FADE (and SAPA in the same screen); SUPER only if FADE shows a signal.
- Targets: TL.
- Evidence: inside FACS-net (CrackVision12K, 256 px, strict IoU, no seeds): 0-2 px IoU 0.356 (FACS default) to 0.373 (CARAFE), 0.397 (FADE), 0.451 (SUPER) [FT of SUPER, general]. FADE: ADE20K SegFormer-B1 boundary IoU 27.80 to 31.68 [ABS + tables, general]. SAPA: boundary IoU 30.96 vs 27.80 [ABS, general].
- Cost: config (FADE, SAPA have code); SUPER code not found.
- Judged on cv5v3: yes.
- Conflicts: no decoder effect detected so far (U-Net vs U-Net++, CONTEXT); the ledger scores decoder-only arms down (P151 at 2, P038 at 1).

### A07 GEOM-AUX: training-only thin-geometry auxiliary heads [MISSING FROM WAVE 1, recommend wave 1 or early wave 2]
- Papers: doi:10.1038/s41592-022-01711-z (local shape descriptors); MASTER P028 (FIDT maps), P062 (orientation + segmentation) under `thin_geometry_aux`, ledger score 3.
- Change vs C2: add regression heads for distance-to-crack, local direction and width around cracks; dropped at inference.
- Targets: TL, UR (component recall).
- Evidence: LSD gave consistent gains across EM specimens, imaging techniques and resolutions and brought affinity methods level with flood-filling networks [ABS, thin]. Project pre-checks passed: FIDT correlation 0.919 under a 1 px shift vs binary IoU 0.548; orientation 95.8% within +-1 bin (MASTER notes). Ledger: gap_census OPEN gives room for continuity arms.
- Cost: new head or loss + precomputed targets.
- Judged on cv5v3: yes.
- Conflicts: our auxiliary heads (inactive aux, Skeleton Recall) helped single models but not ensembles (thin report).

### A08 POOL-ST: offline self-training on the unlabelled pool with rare-class centroid crops [WAVE 1, builder on]
- Papers: doi:10.1109/tpami.2021.3138337 (CSST); MASTER P005, P051, P080, P157, P180, P014, P022 (`pool_ens_distill`, ledger score 3); P473 (ECOCSeg, robust pseudo-label rule).
- Change vs C2: fold-safe C2 ensemble writes pseudo-labels on the unlabelled pool (the unsup scout says 11.9k cells including 1,152 half-cells; the ledger says a 4,949-cell pool including half-cut cells; check which pool the builder uses); crops centred on pseudo crack and inactive components; pseudo:real ratio up to 7:1.
- Targets: UR, HC, INA.
- Evidence: at FULL Cityscapes labels, 78.1 to 79.3 at 1:1 and 80.0 at 7:1; students of other architectures +1.7 to +3.9; centroid sampling worth +1.1, and without it pseudo-labels hurt (78.9 to 78.7) [FT, unsup]. Ledger: P1 gate opened, ensemble edge over a single model +0.0116 strict crack IoU [+0.0080, +0.0155] (strict IoU decides nothing).
- Cost: precompute (teacher inference on the pool) + config (sampler).
- Judged on cv5v3: only the in-distribution part. The half-cut part cannot be read (no half-cut cells in the pool); U1 for the source part (low power); new unseen half-cut set for HC.
- Conflicts: Mean Teacher and pseudo-labels helped only at 5 and 10% labels; the 11,938-cell external pool was already used in SSL (CONTEXT). Ledger: "70% of E1 crack px get p < 0.001", so teacher labels on half-cut cells may teach background on cracks.

### A09 VFM-CTX: frozen foundation-model features as a side input to the house net [WAVE 2, strongest arm missing from wave 1]
- Papers: doi:10.1002/mp.17481 (nnSAM); arxiv:2603.01115 (LUMOS); arxiv:2611.14519 (Kutlusan and Li); doi:10.1016/j.solener.2025.114145 (PV-SAM, side-network design); doi:10.1109/cvpr52729.2023.01862 (EVP); doi:10.3390/s26144597 (HCFNet); doi:10.1016/j.procs.2024.09.452 (ladder SAM); MASTER P030, P043 (`vfm_ctx_r34_pf`, ledger score 3, T6 gate 1 BUILD never acted on), P190 (DINOv3).
- Change vs C2: frozen VFM (SAM2 Hiera-B+, DINOv3-L or C-RADIOv4) embeds the cell; the embedding is resized and concatenated into the U-Net++ decoder. HRNet + U-Net++ remain the pixel path.
- Targets: UR, INA; not TL.
- Evidence: nnSAM, 20 training images, brain white matter DSC 82.8 vs nnU-Net 79.3, gain grows as data shrinks from 20 to 5 [FT, vfm]. Kutlusan and Li: DINOv2 + LoRA beats nnU-Net-recipe U-Nets on all 8 external sets (U-Net deficits -0.008 to -0.107 DSC), level in distribution (0.8803 vs 0.8780), but misses small lesions (up to 13 empty polyp predictions) and draws coarser boundaries [FT, vfm and med]. PV-SAM on UCF-EL random split: ViT-H 54.6% mIoU [FT, vfm]. Ledger: P030 frozen DINOv2 DG Dice 31 vs 2.
- Cost: precompute (frozen features) + new head.
- Judged on cv5v3: only non-inferiority on crack; its purpose (UR) needs U1 or the new unseen set.
- Conflicts: A8 DINOv3 ConvNeXt-T encoder was a KILL, but that was a fine-tuned encoder swap, not a frozen side branch (ledger).

### A10 ENS-DISTIL: distil the C2 ensemble (with D4) into one C2 student [WAVE 1, builder on; training half]
- Papers: doi:10.1109/iccv48922.2021.00526 (CWD); doi:10.1117/1.jmi.9.5.052407 (Noothout, P014); arxiv:2604.25530 (canonical KD, P022); MASTER P061 (patient teacher), P040 (`ens_kd_jml`, gate G5 passed, never built).
- Change vs C2: add a channel-wise KD loss against cached teacher logits (C3 + D4, fold-safe) on the labelled pool.
- Targets: GEN, INA.
- Evidence: CWD PSPNet-R18 +5.81 mIoU on Cityscapes [ABS, recipe]; Noothout: seed ensembles distil into one CNN without loss (recipe, via P014). Project: as A04, the teacher C3 adds -0.0025 [-0.0254, +0.0157] crack relF1@2 over C2 on E1.
- Cost: new loss + teacher logit cache, about 1.5x training.
- Judged on cv5v3: yes.
- Conflicts: same-size distillation gains are smaller than the reported small-student gains (recipe); teacher errors on E1 transfer.

### A11 LOWFREEZE: keep the HRNet stem and stage 1 frozen for the whole run [MISSING FROM WAVE 1, config only]
- Papers: doi:10.1109/cvpr52734.2025.00435 (The Devil is in Low-Level Features); doi:10.1007/978-3-030-87199-4_20 (SpotTUnet); arxiv:2211.09359 (fine-tune with SGD); arxiv:2210.11466 (surgical fine-tuning, P166); MASTER P179 (fine-tuning hyperparameters, un-parked).
- Change vs C2: PF freezes the encoder for 1,000 steps; this keeps the stem and stage 1 frozen for all 20k steps. Second step: phase-preserving RandConv on stem features (LEM).
- Targets: UR, GEN.
- Evidence: fixing ResNet stages 1 and 2 beats training all stages (57.21 vs 56.64 average mIoU, CD-FSS); LEM + test-time calibration +3.71 / +5.34 mIoU at 1 and 5 shots [FT, dg]. SpotTUnet: encoder blocks are chosen most often under shift [FT, dg]. Freezing only the stem closes the AdamW vs SGD gap under shift [ABS, recipe].
- Cost: config (freeze); LEM is code.
- Judged on cv5v3: in-distribution yes; the DG claim needs U1 or the new set.
- Conflicts: supports PF rather than contradicting it; not tested as a full-run freeze.

### A12 CC-LOSS: per-component crack loss [MISSING FROM WAVE 1, cheap]
- Papers: MASTER P115 (CC-DiceCE, `cc_dicece_crack`, ledger score 3); arxiv:2304.06229 (ICI loss); P129 (multi-class follow-up).
- Change vs C2: add an instance-wise Dice/CE term on crack components (components merged across gaps of 2 px or less, per MASTER note).
- Targets: UR (whole faint segments missed), INA.
- Evidence: ICI loss on ATLAS R2.0 beat Dice loss by 1.7 to 3.7% and blob loss by 0.6 to 5.0% Dice [ABS, med].
- Cost: new loss.
- Judged on cv5v3: yes.
- Conflicts: none run; Skeleton Recall (a recall-side loss) helped singly on E1 but did not replicate (SKR2C).

### A13 DG-APPEARANCE: GIN+IPA and its siblings [WAVE 1, builder on: "GIN+IPA"]
- Papers: doi:10.1109/tmi.2022.3224067 (GIN+IPA, P012, RUN_NOW, never run); doi:10.1016/j.media.2023.102789 (SynthSeg) and doi:10.59275/j.melba.2026-6e4e (FetalSynthSeg); arxiv:2104.02008 (MixStyle); arxiv:2202.03958 (DSU); doi:10.1007/978-3-030-01225-0_29 (IBN-Net); doi:10.26599/cvm.2025.9450470 (soft label down-sampling, a prerequisite for resolution randomisation); MASTER P057 (SLAug).
- Change vs C2: GIN intensity remap (1x1 or 3x3 kernels, capped blend) plus IPA spatial mixing of two views; siblings: label-conditioned intensity + blur/down-up randomisation (SynthSeg hybrid), feature-statistics perturbation (MixStyle, DSU).
- Targets: UR (contrast change from a new manufacturer), HC (the scuff-streak confounder, dg report).
- Evidence: GIN+IPA is built for grey-scale CT/MRI single-source DG; the 12 Nov direction D30 read the full text; this sweep read the abstract only and copied no number [ABS, dg]. Ledger: expected +0.01 to +0.04. SynthSeg: making intensity priors realistic cost 1.4 to 2.6 Dice, removing bias field 3.7, removing deformation 4.3 [FT, data]. MixStyle and DSU: abstract previews, classification and driving scenes [ABS, dg].
- Cost: config / small code.
- Judged on cv5v3: **no** for its purpose (by design flat in distribution); cv5v3 can only show it does no harm. U1 cannot resolve +0.01 to +0.04 (interval about +-0.06). Needs the new unseen set.
- Conflicts: per-source calibration and intensity normalisation were null (CONTEXT, med report); 3x3 kernels can blur 1 to 2 px cracks.

### A14 PIXCON: cross-image pixel contrast [WAVE 1, builder on]
- Papers: doi:10.1109/tpami.2024.3367952 (TPAMI version of P275).
- Change vs C2: supervised pixel-to-pixel and pixel-to-region contrastive loss with memory banks and hard anchors (missed crack and inactive pixels).
- Targets: INA, UR.
- Evidence: HRNetV2-W48 Cityscapes val 78.1 to 81.0 (40k-iteration ablation); test +1.0, PASCAL-Context +1.1, COCO-Stuff +0.6, CamVid +0.5, all at full labels [FT, unsup]. Gains are mIoU on large classes.
- Cost: new loss.
- Judged on cv5v3: yes.
- Conflicts: the ledger kept P275 parked because the atlas G-bias says weak-class errors are decision-limited (bias oracle +0.06 to +0.09), not representation-limited. Embeddings at 1/4 resolution may blur 1 to 2 px lines (unsup report).

### A15 RECALL-LOSS: focal Tversky / Tversky / recall loss [WAVE 1, builder on: "focal Tversky"]
- Papers: doi:10.1109/isbi.2019.8759329 (focal Tversky); doi:10.1007/978-3-319-67389-9_44 (Tversky); MASTER P120 (Recall loss, un-parked by ledger), P401 (recall in pavement cracks, un-parked, no code).
- Change vs C2: train-time false-negative weight on the crack channel.
- Targets: UR (E1 relR 0.416 vs relP 0.600, CONTEXT).
- Evidence: Tversky improves F2, Dice and PR-AUC on MS lesions [ABS, recipe]. Focal Tversky +25.7% BUS and +3.6% ISIC vs U-Net, confounded with an improved attention U-Net [ABS, recipe].
- Cost: loss only.
- Judged on cv5v3: yes for the loss; the E1-style recall gain it aims at is an unseen-source effect (U1 or new set).
- Conflicts: la_ce (train-time logit offsets) DROP, -0.0022 [-0.0112, +0.0060] mIoU-R13 (T-table l.557); post-hoc crack bias raised recall but tripped the width and crack-free guards (PF2E, SKR2E). classbias_xfit PASSED and is the OP-C comparator, so this arm must beat C2 + OP-C, not plain C2.

### A16 BDRY-LOSS: signed-distance boundary loss [WAVE 1, builder on]
- Papers: doi:10.1016/j.media.2020.101851 (Kervadec boundary loss).
- Change vs C2: add the integral of the GT signed distance map weighted by predicted crack probability, ramped in, next to the existing loss.
- Targets: TL (false cracks far from any GT crack, guard G2b).
- Evidence: "significant gains and more stable training on highly unbalanced problems"; datasets not read [ABS, recipe]. No number in the scout report.
- Cost: new loss + precomputed distance maps.
- Judged on cv5v3: yes.
- Conflicts: soft band JML and its variants failed (ledger); the recipe scout notes it gives a weak recall signal on its own, and recall is the weak point.

### A17 U-HRNET: HRNet successor encoder [WAVE 2]
- Papers: arxiv:2210.07140 (U-HRNet); doi:10.1016/j.rineng.2026.112287 (Crack-UHRNet, named in general report); MASTER P366 (HRNet+OCR, un-parked), P198 (BiRefNet, un-parked).
- Change vs C2: swap HRNet-W18 for U-HRNet (same interface, extra low-resolution stages).
- Targets: UR, HC, INA (more semantic context).
- Evidence: gains on several segmentation sets under identical training at "almost no" extra cost [ABS, general]. No thin-structure numbers.
- Cost: new backbone (PaddleSeg weights need porting).
- Judged on cv5v3: yes.
- Conflicts: encoder swaps without thin evidence are ranked down by the general scout (controlled SSM benchmark arxiv:2604.18721: boundary mIoU about 30 points below interior for every strong encoder [FT, general]).

### A18 PRESERVE-HARD: keep uncertain labelled pixels, inpaint the rest [WAVE 2]
- Papers: arxiv:2606.31603 (Preserve the Hard, Regenerate the Rest).
- Change vs C2: offline pass keeps crack (plus about a 4 px band) and inactive pixels exact, inpaints the rest with LaMa or a fold-safe PV-DDPM (P042); inpainted pixels are ignored by the loss; 1:1 synthetic:real.
- Targets: UR, HC, INA.
- Evidence: Cityscapes 10%, 5 seeds: 69.60 to 71.67 mIoU, rare classes up to +11.9 IoU; keeping hard pixels without new context gave only 70.13; three iterations 72.24 [FT, data].
- Cost: precompute (inpainting) + config (ignore mask).
- Judged on cv5v3: the in-distribution part yes; the HC part needs the new set.
- Conflicts: crack copy-paste (CP100 seam decoys) and synthetic half-cuts HC (n.d.) and HC2 (FAIL); here generated pixels are never supervised, which is the difference.

### A19 AD-PRIOR: reference or batch anomaly maps as an extra input or flag [WAVE 2, start with a no-training kill check]
- Papers: doi:10.52202/079017-1257 (MetaUAS); doi:10.1109/tpami.2026.3688174 (MuSc-V2; v1 is P272); doi:10.1109/cvpr52733.2024.01681 (SegAD, P449); doi:10.1109/cvpr52729.2023.02346 (BGAD); doi:10.1007/s10845-025-02778-z (ISP-AD).
- Change vs C2: MetaUAS map (prompt = clean same-layout pool cell) as an input channel or 6th member; MuSc-V2 per-module batch map as an inactive prior; BGAD as an auxiliary flow head.
- Targets: UR, HC (layout-agnostic "differs from normal"), INA.
- Evidence: MetaUAS 1-prompt MVTec pixel AP 59.3 vs UniAD 44.7; VisA 42.7 vs 34.3; VisA PRO 60.4 vs PatchCore 84.6 [FT, unsup]. SegAD: AD maps added to a supervised classifier FPR@95TPR 32.8 to 16.4 [FT, unsup]. BGAD: pixel AUROC holds when trained on one anomaly class (carpet 0.994 to 0.995) [FT, unsup]. No paper fuses an AD prior into a supervised multi-class pixel segmenter at full labels (unsup NOT_FOUND).
- Cost: precompute (maps) + new input channel; kill check is inference only: if under 30% of crack components of 20 px or more that C2 misses fall in the top 1% of the map, kill (unsup report).
- Judged on cv5v3: the kill check yes; the HC benefit needs the new set.
- Conflicts: ledger scored the kNN AD-prior arm 1: on half-cut cells the whole layout is anomalous against a full-cell bank. MetaUAS with a same-layout prompt and MuSc batch scoring are the answers to that objection.

### A20 GMMSEG: generative mixture classifier head [WAVE 2]
- Papers: doi:10.52202/068431-2274 (GMMSeg).
- Change vs C2: replace the softmax head with per-class Gaussian mixtures updated by EM.
- Targets: INA, UR, TL (likelihood as an "unknown region" map against false cracks).
- Evidence: +0.8 (HRNetV2-W48 OCR, Cityscapes), +1.5 / +1.6 (ADE20K / COCO-Stuff) at full labels; Fishyscapes L&F AP 43.5 vs 6.0 for MSP [FT, unsup].
- Cost: new head; code unknown.
- Judged on cv5v3: yes.
- Conflicts: none tested; EM on few crack pixels may be noisy.

### A21 FLAT-OPT: flatness optimisers beside SWAD [WAVE 2]
- Papers: doi:10.1109/iccv51070.2023.00479 (FAD); arxiv:2102.11600 (ASAM); arxiv:2010.01412 (SAM, P142, reopen condition met per ledger).
- Change vs C2: optimiser swap, SWAD kept.
- Targets: UR, GEN.
- Evidence: FAD 67.6 vs GAM 66.6, SAM 66.4, AdamW 66.0 averaged over 6 DG sets [FT results, recipe]; the SWAD-combination table was not read.
- Cost: config, 2 to 3x step cost.
- Judged on cv5v3: in distribution yes; DG part U1 or new set.
- Conflicts: ledger scores P142 at 1 (SWAD covers flat minima).

### A22 AVG-TRAIN: Lookaround with D4 views; Model Ratatouille; IMWA [WAVE 2]
- Papers: doi:10.52202/075280-1247 (Lookaround); arxiv:2212.10445 (Ratatouille); doi:10.1016/j.patcog.2024.111293 (IMWA, P169).
- Change vs C2: Lookaround trains k copies on the 8 D4 transforms and averages; Ratatouille initialises from auxiliary fine-tunes (E-SCDD, UCF-EL) and averages.
- Targets: GEN, UR.
- Evidence: Lookaround beats SWA-type baselines on CIFAR and ImageNet [FT experiments, recipe]; Ratatouille improves DomainBed state of the art [ABS, recipe]. No dense-prediction evidence.
- Cost: new pipeline; k-fold compute (fits 8 GPUs).
- Judged on cv5v3: yes.
- Conflicts: UCF-EL pretraining as an init was worse (ledger P15 note); Ratatouille uses it as a recycled average, which was not tested.

### A23 TRACK-REFINE: post-hoc iterative tracking of crack fragments [WAVE 2]
- Papers: doi:10.1016/j.patcog.2025.112797 (Curvi-Tracker); MASTER P117 (TRACE, partly run: gap_census passed, loss never built).
- Change vs C2: a patch tracker trained on our crack masks extends fragmented C2 cracks after inference.
- Targets: UR (fragmented cracks), TL risk.
- Evidence: after U-Net, U-Net++ and clDice models on DRIVE, Massachusetts Roads, CrackTree200, about 10% average gain on topology metrics scored with a 2 px slack; Completeness up, Correctness slightly down [FT, thin].
- Cost: new pipeline.
- Judged on cv5v3: yes (watch the 1.5x crack-free guard: trackers follow look-alike lines such as fingers and busbars).

### A24 EQUIV-DEC: rotation-and-scale equivariant convs in the decoder [WAVE 2]
- Papers: doi:10.1109/tnnls.2025.3560082 (RSF-Conv).
- Change vs C2: replace decoder 3x3 convs with RSF-Conv; encoder keeps pretrained HRNet weights.
- Targets: UR (main gain reported out of domain), TL.
- Evidence: in-domain F1 over plain U-Net +0.27 (DRIVE), +1.12 (STARE), +1.10 (CHASE); out-of-domain "significant margin" stated in prose, table values not extracted [FT, thin].
- Cost: new layers (code yes).
- Judged on cv5v3: in distribution only; UR claim needs U1 or new set.

### A25 LOWRANK-BG: deep-unfolded robust PCA background branch [WAVE 2]
- Papers: doi:10.1109/tpami.2026.3697815 (RPCANet++).
- Change vs C2: auxiliary crack branch or input decomposition that models fingers and busbars as low-rank background.
- Targets: TL (gridline false cracks), UR (contrast shift).
- Evidence: NEU-Seg IoU 80.3 vs U-Net 79.3 [FT, thin]; vessel table values truncated.
- Cost: new pipeline.
- Judged on cv5v3: yes.

### A26 SYN-INACTIVE: rule-based inactive (and faint crack) renderer [WAVE 2]
- Papers: doi:10.1109/cvpr52729.2023.00717 (Label-Free Liver Tumor); doi:10.1109/cvpr52733.2024.01060 (DiffTumor); arxiv:2511.09604 (PV-DDPM / E-SCDD, P042).
- Change vs C2: render inactive regions cut off by a drawn crack, darkened by the source-measured ratio, onto clean pool cells.
- Targets: INA, UR (faint short cracks).
- Evidence: synthetic tumours DSC 59.77 vs 57.51 for real labels (U-Net, LiTS); small-tumour recall collapses without synthetic small tumours [FT, data].
- Cost: new pipeline (renderer, no generator training).
- Judged on cv5v3: yes for inactive (module-grouped).
- Conflicts: inactive_grid_paste gate closed; HC / HC2 synthetic half-cuts n.d. / FAIL (ledger).

### A27 SOFT-WIDTH: multi-width soft crack target [WAVE 2, low]
- Papers: doi:10.1016/j.media.2025.103473 (contrast-agnostic soft spinal cord).
- Change vs C2: each crack's target = average of its skeleton rendered at every source's width convention, regression loss.
- Targets: TL, UR.
- Evidence: lower cross-contrast variability (p<0.05) and better generalisation to unseen sites [ABS, data].
- Cost: new loss + precompute.
- Conflicts: **soft_band_jml failed and the ledger scores its variants 0**; relF1@2 moved at most 0.003 under any label variant (ledger). Low prior.

### A28 REFERENCE ROWS (benchmark, not expected to beat C2) [WAVE 2]
- nnU-Net ResEnc 2D (P006, P020; ledger score 3; from scratch on 478 cells is a risk); SAM2-UNet Hiera-B+ in the HR-stem U-Net++ (P002, ledger score 3, config only, tempered by A8 KILL); HACNet V2 as a heterogeneous ensemble member (doi:10.1016/j.eswa.2025.128144, supported by "Why is the Winner the Best", arxiv:2303.17719: winners ensembled heterogeneous models 2.5x more often [FT, med]); Frepa high-frequency MIM pretraining on the EL pool (doi:10.1109/tmi.2025.3559402, P208: +7 to +15% DSC on fine structures with frozen encoders [FT, vfm]; differs from our null SparK).

### A29 TTA readouts (inference only) [WAVE 2, cheap]
- Papers: MASTER P047 (learned TTA aggregation, un-parked), P384 (S3-TTA, un-parked), arxiv:2005.10821 (HMSA), doi:10.1109/iccv48922.2021.00681 (local temperature scaling).
- Note: multi-scale TTA is not new: B5 D4MS (24 views) minus PLAIN relF1@2 +0.0142 [+0.0079, +0.0202] (T-table l.259). The new part is learned per-view or per-pixel weights on existing D4 dumps.

---

## 2. LATER (needs new data, a new unseen set, or a user decision)

- **L1 NEW-UNSEEN-SET (user decision, first).** doi:10.1016/j.solcom.2026.100196 (Dhimish and Lee 2026, P572): 1,000 module EL images of 144-half-cell mono PERC modules with crack and low-luminescence pixel masks; U-Net R34 crack Dice 0.82; data "available on reasonable request"; licence unknown [FT, data]. Also doi:10.1016/j.apenergy.2026.128093 (DSDINet: public poly-Si set PSCDE, hosting not found) [ABS, data]. Without this, A08, A09, A13, A15 (recall side), A18, A19, A24 and every half-cut claim stay unjudged.
- **L2 FEWSHOT-ADAPT (needs a new labelled layout).** WiSE-FT (P123): +4 to 6 pp under shift on ImageNet [ABS, dg]; SpotTUnet layer policy [FT, dg]; surgical fine-tuning (P166; ledger: few-shot ALL minus ZS +0.2213 [+0.0977, +0.3504] CONFIRMED, partial-freeze rules never tried); Cellpose replay of a 5 to 10% source slice (arxiv:2511.04803) [ABS, med]; SSDA dual-level mixing (doi:10.1109/cvpr46437.2021.01087) [ABS, dg]; ABCDFSS 1-shot CD-FSS 60.7 vs 56.1 [FT, dg].
- **L3 ACTIVE (needs an unlabelled new layout and labelling time).** RIPU (P427, un-parked): 2.2% of regions gives 69.6 vs 70.2 fully supervised, thin class 'pole' lags 43.8 vs 47.6 [FT, dg]; D2ADA under 5% target labels about full supervision [ABS, dg]; Best Practices in AL: Coreset beats uncertainty on redundant pools [FT, dg]; COLosSAL; partial annotations (doi:10.1016/j.autcon.2024.105828). Ledger: few-shot HALF matched ALL (ALL minus HALF +0.0171 [-0.0246, +0.0625]).
- **L4 GEN-HALFCUT (judge only on a new half-cut set).** Shim 2025 (doi:10.1111/mice.13517): DreamBooth crack inpainting, F1 +25.82% and +17.83% on two target domains [ABS, dg]; YoloCurvSeg (doi:10.1016/j.media.2023.102937); DiffCrack (doi:10.1016/j.patcog.2026.113771: synthetic images raised precision but lowered recall [FT, data]); vesselFM (real only 65.45 Dice, + domain randomisation 69.38, + flow samples 74.66 [FT, data]); CrackSegFlow (P024).
- **L5 NUISANCE-OOD.** RPL (doi:10.1109/iccv51070.2023.00112): about 10% FPR and 7% AuPRC better on anomaly benchmarks with inliers untouched [FT, unsup]. Needs an E1-like nuisance source and a new set.
- **L6 EXTERNAL LABELS (user request forms).** PVEL-AD (P363) with BoxInst (P290), both un-parked; UCF-EL joint partial-label training (P037, P077, P011, P223, ledger score 3, never run).
- **L7 Moonshots.** DiffDIS (arxiv:2410.10105, P538): DIS5K max F 0.911 vs 0.908 [FT, vfm]; stride-8 latent is too coarse for 1 to 2 px cracks. Cellpose3 restorer (doi:10.1038/s41592-025-02595-5) [ABS, med].

**Diagnostics worth running tonight (inference only, no arm):** score C2 on pool cells cropped or shifted into half-cut geometry (Position, Padding and Predictions, doi:10.1007/s11263-024-02069-9 [FT, dg]); per-class D4 label-safety audit (CBCT: disabling only left/right mirroring raised F-case Dice 0.7445 to 0.9083 [FT, med]); the A19 AD kill check; C3 minus C2 on cv5v3 relF1@2 from existing dumps (gates A04 and A10).

---

## 3. Tiers

### WAVE 1 (start tonight; builders already on)
| Arm | Lead's label | Evidence verdict |
|---|---|---|
| A01 FULLRES-SKIP | full-resolution skip | **supported**: the only width-stratified thin-crack evidence (0-2 px IoU 0.356 vs 0.079 / 0.160) |
| A02 AA-DOWN | anti-aliased downsampling | **supported if CAPS**; **not if BlurPool alone** (BlurPool lowered recall 83.1 to 80.2 in the CAPS table) |
| A04 ENS-MERGE | ensemble / Model Stock inference | supported for inactive (E-PF +0.2141 PASS), **not for crack**: C3 minus C2 on E1 crack -0.0025 [-0.0254, +0.0157] |
| A10 ENS-DISTIL | ensemble distillation | **weak**: the teacher's own crack gain over C2 is n.d. on E1; the open P1 gate is on strict IoU (+0.0116), which decides nothing. Gate on C3 minus C2 cv5v3 relF1@2 first |
| A08 POOL-ST | pool self-training with rare-class crops | supported as a recipe (CSST, full labels, +1.2 to +1.9); **its target (half-cut) cannot be judged on cv5v3** |
| A06 UPSAMPLER | content-aware upsampler | thin-crack evidence exists but is weak (strict IoU, 256 px, no seeds) and we saw no decoder effect; **CARAFE is the weakest of the three (0.373); use FADE, then SUPER** |
| A16 BDRY-LOSS | signed-distance boundary loss | **weak**: abstract only, no number, blob boundaries; aims at precision, while recall is the weak point |
| A15 RECALL-LOSS | focal Tversky | **not supported**: abstract only and confounded with an architecture change; la_ce DROP and the guard trips of the crack bias predict the same failure; must beat C2 + OP-C |
| A13 DG-APPEARANCE | GIN+IPA | evidence fine for the purpose, but **no instrument can judge it**: flat on cv5v3 by design, U1 too weak (+-0.06), E1 is training data |
| A14 PIXCON | pixel contrast | **not supported for us**: mIoU gains on large classes; conflicts with the ledger's atlas finding that weak-class errors are decision-limited (bias oracle +0.06 to +0.09) |

Recommended additions to wave 1 (strong, cheap, missing):
1. **A05 POSTPROC-CV**: CPU only on existing out-of-fold predictions; no GPU needed.
2. **A03 MIRO**: the only recipe shown to add on top of SWAD (68.1 vs 66.9).
3. **A07 GEOM-AUX**: training-only, pre-checks passed, ledger score 3.
4. **A11 LOWFREEZE**: config only.
5. **A12 CC-LOSS**: cheap, ledger score 3, never run.
The four inference-only diagnostics in section 2.

### WAVE 2 (more code or a precompute)
A09 VFM-CTX (the strongest arm missing from wave 1; frozen features precompute), A17 U-HRNet (weight port), A18 PRESERVE-HARD (inpainting pass), A19 AD-PRIOR (after its kill check), A20 GMMSEG, A21 FLAT-OPT, A22 AVG-TRAIN, A23 TRACK-REFINE, A24 EQUIV-DEC, A25 LOWRANK-BG, A26 SYN-INACTIVE, A27 SOFT-WIDTH (low), A28 reference rows, A29 TTA readouts.

### LATER
L1 new unseen set (request the Dhimish 2026 half-cut data: user decision, and the gate for most UR/HC arms), L2 few-shot adaptation, L3 active learning, L4 generative half-cut data, L5 nuisance OOD head, L6 external labelled data, L7 moonshots.
