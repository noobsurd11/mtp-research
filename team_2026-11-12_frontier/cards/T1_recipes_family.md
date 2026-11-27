# T1 Training recipe and fine-tuning: paper cards (13 Nov 2026)

Analyst T1. Tags: R = from the paper (retrieved this session), E = from our files, S = my judgement.
Research MCP tools were not available in this session; papers were read through arXiv pages and PDFs (WebFetch) and the official repositories.
Arms are specified in `T1_recipes_spec.md`; one line per paper in `ledger/T1.tsv`.

## 0. What our files say about the recipe (E)
- House optimizer is `torch.optim.Adam(lr 1e-3, weight_decay 1e-4)` (`harness/src_snap/el_f3/scripts/train.py` l.108-131). Adam's `weight_decay` is a coupled L2 term that passes through Adam's normalisation. It is not AdamW.
- The house fine-tune erases ResNet-34 layer3 / layer4 (cosine to init 0.005 to 0.018 / -0.001 to 0.001 at 20k; norms 2 to 9% of init; direction lost before step 2,000). PF keeps 0.93 / 0.94 at 20k (handbook 11 row 23, 19 §4). PF changed nothing on test; E1 inactive 0.05 to 0.24 (BRIEF §3, §5).
- Mechanism noted in handbook 11 row 23 (S there): BN-followed convs are scale-invariant, so coupled L2 shrinks their norm and raises the effective step. The decoder still runs under coupled wd 1e-4 in PF; its norms were never measured.
- Schedule: 200-step warmup, cosine to 0 at 20k (`trainer.py` l.85-107). 20k x 8 = 160k samples = about 375 epochs of 425 fold-train cells.
- No supervised EMA, no weight averaging, no class-aware sampling: the sampler is a seeded uniform permutation per epoch (`src/data/stream.py` `SeededSampler`). `EMAUpdater` exists only for Mean Teacher (`src/trainers/ema.py`; it EMAs BN buffers too).
- CV5-G on P532 (B6, 2 seeds): house out-of-fold crack IoU 0.37, relF1@2 0.83, inactive IoU 0.50 to 0.52; SE of an inactive contrast 0.038 to 0.039 (PROTOCOL_DRAFT §3.2). So inactive changes under about 0.1 are not resolvable by a 2-seed CV screen; paired within-run readouts (arms that only change the weights read out) are much more sensitive.

## 1. Cards

### 009 SPD: Rethinking Weight Decay for Robust Fine-Tuning of Foundation Models (Selective Projection Decay)
- Id: arXiv:2411.01713 (NeurIPS 2024). https://arxiv.org/abs/2411.01713 , https://arxiv.org/html/2411.01713
- Claims (R, full text read, Table 4 and Algorithm 2): Adam step first, then for each parameter tensor c_t = -g_t^T (theta_{t-1} - theta_0); if c_t < 0, theta_t = theta~_t - lambda r_t (theta~_t - theta_0) with r_t = max(0, gamma_t - gamma_{t-1}) / gamma_t, gamma = ||theta - theta_0||. PASCAL-Context, Swin-T IN-22k + SegFormer head, 60 epochs, lr 1e-4, lambda 2.2: mIoU clean / mean of 4 corruptions: vanilla FT 66.03 / 44.00, L2-SP 73.47 / 56.70, LLRD 72.09 / 54.47, TPGM 72.56 / 56.96, FTP 73.79 / 58.45, Adam-SPD 74.27 / 60.06. DomainNet lambda sweep 0 to 2.1: deviation 0.59 to 0.31, OOD 41.34 to 45.67, ID flat (79.9 to 81.3); correlation OOD vs deviation -0.96. Paper recommends starting at lambda 1. Memory: one copy of the pretrained weights; no runtime numbers.
- Evidence check (S): numbers match the scout record. One segmentation table, one seed count not stated in what I read. The paper's §3.3 and Algorithm 2 index c_t differently (g_{t+1} vs g_t); I follow Algorithm 2 and the code. The gain over vanilla FT in that table is mostly the gain of any preservation (L2-SP gets 7.4 of SPD's 8.2 clean points); our PF already plays that role.
- Code: https://github.com/GT-RIPL/Selective-Projection-Decay (verified to exist), PyTorch-style `adamSPD.py` class `AdamSPD(param_group with 'pre' anchors, lr, weight_decay=lambda)`; per tensor; `.item()`-style branch per tensor (a GPU sync each). Licence not stated on the page (unverified), so we re-implement from Algorithm 2 instead of copying.
- Hypothesis (S): PF damps every encoder tensor uniformly (0.1x lr). SPD at the full house lr lets tensors whose descent keeps pushing outward adapt (stem, layer1: the EL contrast regime) and holds tensors where the loss no longer pushes outward. Expected: equal or better in-distribution crack, and the PF-like gain on unseen modules kept or raised (F51 / H36 inactive and crack). Encoder anchor = ImageNet with the RGB-summed 1-channel conv1 (as built).
- Status: **RUN_NOW**, arm `encoder_spd`.

### 032 L2-SP: Explicit Inductive Bias for Transfer Learning with Convolutional Networks
- Id: arXiv:1802.01483 (ICML 2018 per arXiv comment). https://arxiv.org/abs/1802.01483
- Claims (R, abstract only): an L2 penalty toward the pretrained weights instead of toward zero; recommended as the baseline for transfer. No numbers in the abstract. Segmentation number from SPD's Table 4 (R, read): L2-SP 73.47 clean / 56.70 OOD vs SPD 74.27 / 60.06. SPD's DomainNet Table 2(a) (R, as extracted): stronger L2-SP does not improve OOD and lowers ID.
- Evidence check: abstract only; numbers come from the SPD paper's reproduction.
- Code: no official repository retrieved (unverified). Trivial to write.
- Hypothesis (S): same family as PF and SPD (pull toward ImageNet). Uniform pull, no selectivity, one more hyperparameter (alpha) that the SPD paper reports as hard to set.
- Status: **PARKED**. Not run first because SPD dominates it in the only segmentation table we have and both need the same anchor plumbing; the `encoder_spd` arm's code makes it a 10-line add (`spd_lambda` replaced by `l2sp_alpha`). Stays open: run it if `encoder_spd` passes, as the simpler benchmark row, or if SPD fails its mechanism check.

### 030 EMA of weights: Dynamics and Benefits
- Id: arXiv:2411.18704 (TMLR). https://arxiv.org/abs/2411.18704 , https://arxiv.org/html/2411.18704
- Claims (R, HTML read to about 90%; appendix end not read): decay usually 0.9 to 0.9999, task dependent; experiments keep 5 EMAs at alpha 0.968 to 0.998 updated every 16 steps; warm-up decay min(alpha, (t+1)/(t+10)). BN "breaks" the EMA model as the window grows; recomputing BN statistics after training recovers it and "always improves generalization". Label noise (ResNet-34, as extracted): CIFAR-10N EMA 86.71 vs CE 77.69; CIFAR-100N 65.15 vs 55.50. Transfer (Tiny-ImageNet to CIFAR-100 linear eval) 52.77 to 57.30 / 57.78. ECE lower on 4 of 5 settings. EMA "requires less learning rate decay"; with a step decay EMA only matched SGD near the end, when lr was small.
- Evidence check (S): classification only, no segmentation. The label-noise baseline appears to be plain CE without early stopping, which flatters EMA. The lr-decay remark matters: our cosine reaches 0, so an EMA of the last few thousand steps averages near-identical weights (lr is under 7.4% of peak over the last 3,500 steps, E from the schedule formula). Prediction (S): small effect under cosine, larger under a constant tail.
- Code: none linked (unverified). timm 1.0.30 `ModelEmaV3` is installed (E, DESIGN §1.10); I spec our own averager to control BN and checkpoint keys.
- Hypothesis (S): crack labels are jittered by 1 to 2 px (label noise); EMA weights smooth logits near thin structures, may raise relP@2 and lower false alarms. Cheap and paired: readouts from the same run, so seed and fold noise cancel.
- Status: **RUN_NOW**, arm `ema_wise_posthoc` (cosine schedule) and arm `swad_const` (constant tail, EMA readout there too).

### 023 SWAD: Domain Generalization by Seeking Flat Minima
- Id: arXiv:2102.08604 (NeurIPS 2021). https://arxiv.org/abs/2102.08604
- Claims (R, PDF read): dense averaging (every iteration) of weights between a start t_s (validation loss stops falling for N_s = 3 evaluations) and an end t_e (validation loss above r = 1.3 x the minimum for N_e = 6 evaluations); constant lr (Adam 5e-5), ResNet-50, BN statistics frozen during training, 5,000 iterations (15,000 DomainNet). PACS out-of-domain / in-domain: ERM 85.3 / 96.6, EMA 85.5 / 97.0, SAM 85.5 / 97.4, SWA 85.9 / 97.1, SWAD 87.1 / 97.7. Ablation (Table 5, PACS+VLCS avg OOD): SWA cyclic 81.2, SWA const 81.6, SWAD without dense sampling 82.2, SWAD with fixed window 4000 to 5000 81.7, SWAD averaging to the end 82.4, window fit on validation 82.4, full SWAD 83.0. ImageNet-C mCE 57.6 ERM, 56.8 SWA, 55.7 SWAD.
- Evidence check (S): classification only. The overfit-aware window is worth about 1.3 of the 1.8 points over SWA-const in the ablation; with a fixed window the method is close to SWA. Our held-out fold is the scored set, so the window cannot be fit on it; a fixed, pre-declared window is the honest version, at the cost of part of the reported gain. SWAD needs a constant lr; our cosine schedule removes most of the iterate diversity.
- Code: https://github.com/khanrc/swad (verified), MIT licence (README), PyTorch 1.7, DomainBed-based.
- Hypothesis (S): E1-like shift (new modules, half-cut, scuff) is a domain shift; flatter solutions should transfer better. Read on F51 / H36 for unseen modules, CV for in-distribution.
- Status: **RUN_NOW**, arm `swad_const`.

### 077 WiSE-FT: Robust fine-tuning of zero-shot models
- Id: arXiv:2109.01903 (CVPR 2022). https://arxiv.org/abs/2109.01903
- Claims (R, abstract): weight-space ensemble of zero-shot and fine-tuned CLIP; "4 to 6 percentage points" under ImageNet distribution shifts over prior work, ImageNet +1.6 pp, "2 to 23 pp" on six other shifts, "0.8 to 3.3 pp" over standard fine-tuning on seven transfer datasets.
- Evidence check (S): abstract only. Classification with a zero-shot head; our decoder has no pretrained counterpart, so only the encoder can be interpolated toward ImageNet, or two fine-tunes from the same init (house and PF share the init when the seed is the same; to be checked) can be interpolated. Linear connectivity is not established for our case.
- Code: https://github.com/mlfoundations/wise-ft (verified to exist; licence file present, type not read; framework not stated). Not needed: interpolation is a few lines.
- Hypothesis (S): moving the PF encoder part of the way back to ImageNet trades in-distribution fit for unseen-module robustness (E1 inactive moved 0.05 to 0.24 when the encoder was kept). Zero training cost, readouts on W1a checkpoints.
- Status: **RUN_AFTER_GATE**, arm `ema_wise_posthoc`. Gate: W1a `house_r34_unetpp` and `house_r34_unetpp_pf` on cv5v2_v11 trained (same fold, same seed), plus the CPU loss-barrier pre-check passing.

### 086 SAM: Sharpness-Aware Minimization for Efficiently Improving Generalization
- Id: arXiv:2010.01412 (arXiv; v3 Apr 2021). https://arxiv.org/abs/2010.01412
- Claims (R, abstract): minimise the worst-case loss in a rho-ball; better generalisation on CIFAR-10/100, ImageNet and fine-tuning; label-noise robustness. Repository examples (R, README): rho 0.05 from scratch (WRN-28-10), rho 0.1 for EfficientNet fine-tuning.
- Evidence check (S): abstract and README only. SWAD's Table 3 (R, read) has SAM at 85.5 vs ERM 85.3 OOD on PACS, not significant, while SWAD gives 87.1. No segmentation evidence retrieved.
- Code: https://github.com/google-research/sam (verified), Apache-2.0, JAX / Flax. Not usable directly; the PyTorch version is short and I spec it.
- Hypothesis (S): crack label jitter acts as label noise; SAM resists fitting it. Costs 2x per step; BN with batch 8 needs care.
- Status: **RUN_NOW** at lowest priority (arm `sam`). GPUs are idle and compute is unlimited (BRIEF §6); the build is the cost. If engineering time runs short, it is the first arm to drop to PARKED.

### 021 DAFormer (Rare Class Sampling)
- Id: arXiv:2111.14887 (CVPR 2022; doi 10.1109/cvpr52688.2022.00969). https://arxiv.org/abs/2111.14887
- Claims (R, PDF read): f_c = pixel fraction of class c over the source set; P(c) = softmax((1 - f_c) / T), T = 0.01; draw c, then an image uniformly from those containing c. GTA to Cityscapes, SegFormer, 3 seeds (Table 5): warmup only 58.2 +/- 0.9, class-balanced T = inf 62.0 +/- 1.5, RCS T = 0.01 64.0 +/- 2.4. DeepLabV2 / ResNet-101 (Table S1): 54.2 to 55.7 with RCS. T sensitivity (Table S2): 65.6 to 66.8 for T 0.001 to 0.1 (stable within factor 5). Without self-training (pure source training, Table S3) RCS + FD: 45.6 to 50.7.
- Evidence check (S): numbers match the scout record. The large gain is for a transformer under UDA self-training; the CNN gain is +1.5 mIoU. The code (R, `uda_dataset.py`) keeps an image in a class list only if it has more than `rcs_min_pixels` px of the class, and retries random crops; we have no random crops.
- Our pre-check (E, `cards/T1_rcs_precheck.py` md5 6b4c60d0 on `benchmark/out/legacy_classpx.npy` md5 0d75969d, P532, masks_escdd): the paper's rule over all 24 classes LOWERS the inactive and crack pixel share (0.81x, 0.82x uniform) because classes in 1 to 4 cells take the mass and single cells get drawn 34x. Restricted to the fixed R13 class list at T = 0.01: inactive px share 2.49x, splice 2.08x, crack 1.68x, edge_dark 1.59x, gridline 1.15x, material 1.16x; max per-cell multiplier 3.2; effective n 340 of 532; 2 cells never drawn; crack-free cells get 0.49 of draws (uniform 0.56); SDLE drops to 0.004 of draws (uniform 0.032).
- Code: https://github.com/lhoyer/DAFormer (verified), Apache-2.0, mmseg 0.16 / mmcv 1.3.7. Not used directly; the sampler is about 60 lines in our stream.
- Hypothesis (S): inactive (48 cells in P532) and splice / edge_dark / material are data-limited; seeing them 2 to 2.5x more often raises their IoU and mIoU-R13. Crack prior shifts up, so crack recall and width rise and precision falls; compare at a matched operating point.
- Status: **RUN_NOW**, arm `rcs`.

### 043 DAFormer (RCS + ImageNet feature distance + warmup)
- Id: arXiv:2111.14887 (same paper as 021). Code as 021; FD in `mmseg/models/uda/dacs.py`; config `dacs_a999_fdthings.py` (R, read): `imnet_feature_dist_lambda=0.005`, thing classes only, `scale_min_ratio=0.75`.
- Claims (R, PDF read): FD = L2 between bottleneck features of the model and a frozen ImageNet copy, only on bottleneck cells whose downsampled label is a thing class with ratio > 0.75; lambda_FD 0.005. SegFormer (Table 5): +FD 61.7 +/- 2.6 vs 58.2; FD on all classes only 58.8; RCS + FD 66.2. DeepLabV2: +FD 55.5 vs 54.2 (Table S1). lambda_FD stable within factor 2 (Table S2). Warmup (Table 4): SegFormer UDA 51.8 to 58.2, oracle 72.9 to 76.4; DeepLabV2 49.1 to 54.2, oracle 67.4 to 72.1. Recipe: AdamW, encoder lr 6e-5, decoder 6e-4 (10x), wd 0.01, linear warmup 1.5k, linear decay, 40k iterations, batch 2.
- Evidence check (S): FD's gain depends on thing classes that ImageNet knows (all-class FD gives +0.6 instead of +3.5). EL classes are not ImageNet things, so the paper's own ablation predicts the all-class variant, the only one we could run, to be weak. Encoder preservation is already in place (PF, cosine 0.93 at 20k, E). The DAFormer recipe's 10x decoder/encoder lr ratio equals PF's 0.1x (E); the warmup and AdamW wd 0.01 are what we do not have.
- Status: **RUN_NOW** for RCS (arm `rcs`) and for the recipe parts (arm `modern_recipe`: AdamW wd 0.01 + 1.5k warmup). FD itself: **PARKED** (cheapest decider: PF + FD on crack / inactive / splice bottleneck cells, lambda 0.005, 1 fold-0 pre-screen then the 10-run screen, about 13 GPU-h; open; raise priority only if `encoder_spd` or WiSE readouts show that more encoder preservation moves F51 / H36).

### 033 Domain Adaptive and Generalizable Network Architectures and Training Strategies (DAFormer / HRDA, TPAMI)
- Id: arXiv:2304.13615 (TPAMI 2023). https://arxiv.org/abs/2304.13615 ; code https://github.com/lhoyer/HRDA (link verified from the abstract page; licence not read)
- Claims (R, abstract): DAFormer and HRDA improve the state of the art by more than 10 mIoU on 5 UDA / DG benchmarks; training strategies RCS, thing-class FD, warmup; HRDA multi-resolution crops with learned scale attention.
- Evidence check: abstract only; the per-strategy numbers I use are from the CVPR paper (021 / 043), read in full.
- Hypothesis (S): no mechanism beyond 021 / 043 for this family. HRDA multi-resolution crops belong to the architecture / resolution family (not T1).
- Status: **RUN_NOW** through arm `rcs` (same mechanism, covered); FD part PARKED as in 043.

## 2. Family-level decisions (S)
- **Own arm (needs to be interpretable alone):** RCS (changes the data distribution and the class prior, so it shifts the crack operating point), SPD (changes encoder preservation; compared against both PF and house), constant-lr dense averaging (changes the schedule, and its raw weights are expected to be worse), SAM (2x cost, BN subtleties).
- **Free readouts on any run:** EMA and BN recalibration do not change the trajectory, so they ride on every run of every arm as extra weights keys (paired).
- **Stackable as one "modern recipe" arm:** AdamW with decoupled wd 0.01 on the decoder and a 1.5k warmup (both from the DAFormer recipe; each expected to be small and both act on the decoder's optimisation). EMA readout on top.
- **Parked:** L2-SP, ImageNet feature distance, schedule length. Length: 20k x 8 = 160k samples is already 2x DAFormer's 40k x 2 = 80k; no paper in this family argues for longer. Cheapest decider: PF at 30k, 5 folds x 1 seed (about 8 GPU-h), run only after the stack.
- **Final model:** the stack of all arms that pass alone, built once the screens are read; it is a lead decision, not an arm here.
