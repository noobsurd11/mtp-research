# T9 family cards: the unlabelled pool, teachers and ensembles (14 Nov 2026)

Tags: R = from the paper, E = from our files, S = my judgement. "Read" says what I actually retrieved: full text (arXiv HTML), abstract page, or repository README. The Research MCP was not available in this session (not authenticated); I used arXiv / ar5iv pages and GitHub READMEs. Several fetches timed out; those papers rely on the abstract plus the scout record and are marked so.
Statuses for all 84 papers: `cards/ledger/T9.tsv`. Arms: `cards/T9_pool_teachers_spec.md`.

Counts: RUN_NOW 9, RUN_AFTER_GATE 5, BENCH_ONLY 7, PROTOCOL 9, PARKED 52, VOID 2.

---

## A. Arm 1 `pool_ens_distill` (frozen ensemble teacher, noised student, soft pool targets)

### P005 Naive-Student (arXiv 2005.10266, ECCV 2020) - RUN_NOW (arm 1)
- Links: https://arxiv.org/abs/2005.10266 ; read: full text (ar5iv).
- R: teacher pseudo-labels with multi-scale {0.5 to 2.0} + left-right flip TTA, **hard** labels, **no confidence threshold**; student trained on pseudo-labels only, then fine-tuned on human labels; repeated. Cityscapes val (Table 1): iteration 0 X-71 82.5 mIoU; iteration 1 student WR-41 85.7; iteration 2 (WR-41 teacher and student) 86.5 (86.1 in Table 5, inconsistent in the paper).
- Evidence check (S): the +3.2 at iteration 1 mixes self-training with a backbone change (X-71 -> WR-41); the clean same-architecture step is iteration 2, +0.8. Full Cityscapes labels, so it is a high-label-fraction result. About 109k unlabelled frames.
- Code: none found (scout); not checked further.
- Hypothesis for us: an offline TTA-ensemble teacher on the pool lifts a same-size student at 100% labels, unlike our EMA teacher (E P16 Sx100 n.d.). We use soft targets instead of hard (1 to 2 px cracks are lost by hard thresholding of averaged maps) and a joint loss instead of pretrain-then-fine-tune (cheaper; S).

### P051 Rethinking Pre-training and Self-training (arXiv 2006.06882, NeurIPS 2020) - RUN_NOW (arm 1)
- Links: https://arxiv.org/abs/2006.06882 ; read: abstract page.
- R: "self-training is always helpful when using stronger data augmentation, in both low-data and high-data regimes"; COCO +1.3 to +3.4 AP across data sizes; PASCAL segmentation 90.5 mIoU, +1.5 over the previous best, with self-training on top of pre-training.
- Evidence check: abstract-level; the per-size COCO table not read.
- Code: not checked.
- Hypothesis: the missing ingredient in our P16 run was strong augmentation (E: CutMix off by val pick, label-safe aug only). Soft targets let the pool cells take geometric and photometric perturbation.

### P080 Depth Anything (arXiv 2401.10891, CVPR 2024) - RUN_NOW (arm 1 perturbation part; arm 3 feature part)
- Links: https://arxiv.org/abs/2401.10891 ; read: full text (arXiv HTML), Tables 9 and 12.
- R: with 1.5M labelled images, plain self-training failed ("we failed to gain improvements with such a self-training pipeline"). Table 9 AbsRel: labelled only KITTI 0.085 / NYU 0.053; + unlabelled, no perturbation 0.085 / 0.054; + strong perturbation (colour jitter, Gaussian blur, CutMix) 0.081 / 0.048; + feature alignment to frozen DINOv2 0.076 / 0.043. Margin alpha: 1.00 -> 0.188, 0.85 -> 0.175, 0.70 -> 0.178 (mean AbsRel).
- Evidence check (S): the cleanest published ablation that matches our situation (many labels, plain self-training null); depth, not segmentation; 62M unlabelled images, far more than our 10k.
- Code: github LiheYoung/Depth-Anything (scout; not checked).
- Hypothesis: perturbation turns pool pseudo-labels from null into a gain (arm 1); the feature loss is a separate mechanism (arm 3, gated).

### P022 Canonical KD for segmentation (arXiv 2604.25530, 2026) - RUN_NOW (arm 1)
- Links: https://arxiv.org/abs/2604.25530 ; read: full text (arXiv HTML).
- R: at matched compute, plain logit / feature KD beats segmentation-specific KD (CIRKD 73.5 at 30.2 GPU-h vs feature KD 73.7 at 9.2 GPU-h). Feature KD PSPNet-R18 79.0 Cityscapes (99% of the R101 teacher's 79.8) in 55 GPU-h; supervised saturates at 76.3. "Pure KD" with 20k Train-Extra images (labels ignored) reaches 79.0 after 320 GPU-h; feature KD does not benefit from the extra images (no number). Mask2Former teacher: 77.8 vs 77.7 at about 3x compute; weaker students on ADE20K; "architectural compatibility matters more than raw teacher accuracy". Temperature T in [1, 4].
- Evidence check (S): the unlabelled-image gain needed very long schedules (4,500 epochs). Our arm runs 20k steps; it will see each pool cell about 17 times (20k x 8 / 9.6k), so it tests the cheap end of this effect.
- Code: not stated in the paper text I read.
- Hypothesis: logit KD keeps scaling with unlabelled inputs; keep the teacher in the U-Net++ R34 family (arm 1), and treat a heterogeneous teacher as a later variant (P298).

### P014 Ensemble KD for medical segmentation (doi:10.1117/1.jmi.9.5.052407, JMI 2022) - RUN_NOW (arm 1)
- Read: scout record only (publisher; not fetched). R (scout): distilled single networks matched seed / architecture ensembles on CT, brain MRI and cardiac MRI and beat the same network trained on reference labels.
- Code: none found.
- Hypothesis: the labelled-cell half of this is T2 `ens_kd_jml`; arm 1 is the pool half. Read as a pair.

### P157 Data Distillation (CVPR 2018) and P180 Noisy Student (CVPR 2020) - RUN_NOW (arm 1)
- Read: scout records and my own knowledge of the methods only (not fetched). R (scout): P157 labels unlabelled data by ensembling one model over transforms; P180 ImageNet 88.4% top-1 with a noised student on soft pseudo-labels, iterated.
- Use: P157 = D4-view averaging in the teacher; P180 = noise on the student's pool inputs. Iteration (P180) is parked until arm 1 passes.

### P061 A good teacher is patient and consistent (arXiv 2106.05237, CVPR 2022) - RUN_AFTER_GATE (arm 1 pass)
- Read: abstract page only (full text timed out). R: ResNet-50 student 82.8% ImageNet top-1; design choices "may drastically affect the effectiveness of distillation".
- The claim that precomputed fixed-view teacher targets are worse than consistent online views is in the scout record and widely cited, but I did not verify it in the text (unverified).
- Gate: arm 1 pass, then an online function-matching variant (about 30 GPU-h) against the offline arm.

### P298 Heterogeneous-architecture KD (arXiv 2504.07691, AAAI 2025) - RUN_AFTER_GATE (arm 1 variant)
- Read: scout record. Gate: any T6 / T11 model passes its screen; it then replaces the R34 ensemble as the pool labeller (1 build h). P022 (R) warns that aligned architectures distil better, so this is a variant, not the default.

---

## B. Arm 2 `ad_prior` and the anomaly-detection track

### P325 AnomalyDINO (doi:10.1109/wacv61041.2025.00136, arXiv 2405.14529, WACV 2025) - RUN_NOW (arm 2 stage A)
- Links: https://arxiv.org/abs/2405.14529 ; https://github.com/dammsi/AnomalyDINO ; read: abstract page and README.
- R: training-free patch nearest-neighbour scoring on DINOv2 features; one-shot MVTec AD AUROC 93.1 to 96.6 (abstract). README: compares DINOv2-S/14 and DINOv3-S/16 at 448/672 and 512/768 to match 32 and 48 patches per side; last block by default; similarity search with FAISS; reference augmentation by rotation; masking only calibrated for DINOv2.
- Code: Apache-2.0 (verified, README), PyTorch, DINOv3 via timm, needs faiss (we replace it with chunked torch matmul; nothing installed).
- Evidence check (S): no thin-structure or EL evidence; one 14 px patch holds a 1 to 2 px crack as about 10% of its pixels, so crack sensitivity is the open question; inactive regions are patch-scale.
- Hypothesis: a kNN map against normal patches of the training folds (all five sources, labels used only to exclude defect patches) flags misses of the PF model; the cross-fitted stacking test decides.

### P266 SuperADD (arXiv 2605.14808, CVPR 2026 VAND 4.0) - RUN_NOW (arm 2 stage A ingredients)
- Links: https://arxiv.org/abs/2605.14808 ; code https://github.com/LukasRoom/SuperADD (named on the arXiv page; licence not checked). Read: abstract page (full text timed out).
- R: DINOv3 memory bank, intensity augmentation for illumination shift, improved bank subsampling for coverage; MVTec AD 2 segmentation F1 62.61 / 57.42 / 54.35 (public / private / private-mixed test).
- Use: gamma-augmented bank copies and coverage-based subsampling in stage A; a SuperADD row (DINOv3 ViT-S/16 is local, not gated) in the AD track.

### P112 WeakREST (doi:10.1109/tip.2026.3659337, arXiv 2306.03492) - RUN_AFTER_GATE (arm 2 stage B)
- Read: scout record. R (scout): residual between a patch feature and its nearest normal feature fed to a supervised segmenter; MVTec AD supervised AP 87.6 (prior best 86.0); box-only labels 87.1. Code github BeJane/Semi_REST (not checked).
- Gate: stage A pass. Our form: the kNN map injected through zero-initialised 1x1 convs at encoder strides 2, 4, 8 of the house U-Net++.

### AD track rows (BENCH_ONLY)
| pid | Method | Code (status) | Role in the track |
|---|---|---|---|
| P495 | PatchCore (CVPR 2022) | anomalib (scout; not checked) | canonical bank-kNN row |
| P440 | Dinomaly2 (arXiv 2510.17611) | separate repo linked from the Dinomaly README (verified the link note, not the code) | strongest multi-class reconstruction row |
| P441 | Dinomaly (CVPR 2025) | github guojiajeremy/Dinomaly, Apache-2.0, PyTorch (verified README) | fallback if Dinomaly2 code does not run |
| P479 | EfficientAD (WACV 2024) | anomalib (scout) | fast row for the deployment track |
| P267 | INP-Former (CVPR 2025) | github luow23/INPFormer (scout) | no external references: half-cut relevant |
| P272 | MuSc (ICLR 2024) | github xrli-U/MuSc (scout) | zero-shot, transductive per module group |
Each is trained on `pool_t9.txt` clean cells plus crack-free training-fold cells, scored by the stage A reads (pixel AUROC, AU-PRO, relF1@2 at a cross-fitted threshold, cell-level recall at 5% cell false alarms). S: none is expected to approach the supervised PF row in-distribution; their value is the label-free reference line and the unseen-layout reading at the final opening.

---

## C. Arm 3 `fm_align_pool` (gated)

### P395 RS-MTDF (arXiv 2506.08772, IEEE TGRS 2025) - RUN_AFTER_GATE (arm 3)
- Read: scout record. R (scout): frozen DINOv2 / CLIP feature teachers aligned with the student encoder during SSL; SOTA or comparable on Potsdam, LoveDA, DeepGlobe. Code github earth-insights/RS-MTDF (scout; not checked).
- Gate: T6 `vfm_ctx_r34_pf` passes, or arm 1 passes. Hypothesis: carry a frozen DINOv2-L's context into ResNet-34 on pool cells, at no inference cost.

### P377 NeCo (arXiv 2408.11054, ICLR 2025) - RUN_AFTER_GATE (not one of my arms)
- Read: scout record. R (scout): dense post-pretraining, +5.5 ADE20k in-context, 19 GPU-h; code github vpariza/NeCo.
- Gate: T6 `vfm_ctx_r34_pf` passes; then the cheapest continued-SSL route for that ViT on pool cells.

---

## D. Papers read for the decision but not run

### P230 Self-training with pre-contrast subtraction (arXiv 2610.40302, 2026) - PARKED
- Read: abstract page. R: ignore label for pixels only the physical cue sees; XCAD macro Dice +2.7 (95% CI 2.3 to 3.2), same-epoch control -0.6, a second round gave no gain; "the benefit of self-training depends largely on the sensitivity of the model that generates the initial pseudo-labels"; XACV did not improve where main vessels were missed.
- Why parked (E/S): our analogue of the physical cue is a ridge filter, and T5's crackcue pre-check found it no better than raw darkness on faint crack pixels (AUROC 0.708 both, E WAVE2_REVIEW). Its sensitivity finding supports arm 1's P2 rule (do not self-train where the teacher is blind). Reopens as an arm 1 variant on pool half-cells if arm 1 passes on the unseen-module proxies.

### P616 SparK and P604 dermoscopy SSL comparison - VOID
- Same mechanism as the closed run: in-domain masked reconstruction on a ResNet-34 U-Net after ImageNet, our 11.9k pool, PF, 100% labels, n.d. (BRIEF 5 row "Pool feature learning"; handbook 11 row 25, MIM100-PF minus SUP100-PF crack +0.0048 against a threshold of 0.0113). The MIM100-PF row enters the benchmark pretraining table as it is.

### Weight averaging and TTA papers (P122, P169, P211, P047, P126) - PARKED
- Covered by named arms on the same checkpoints: T1 `ema_wise_posthoc` and `swad_const` (averaging), T7 `msc_tta` (D4 + scale views). P126's 1 px phase-shift views are a 0.5 build-h add-on to T7's `bench/tta.py` (readout only).

### P150 ExPLoRA, P483 DINOCell, P174 / P288 ConvNeXt V2 FCMAE, P364 LeJEPA - PARKED
- Encoder SSL on the pool for a new backbone: cost (ExPLoRA ViT-L scout estimate 250 GPU-h; DINOCell about 100 h on 8 L40S, R per scout) and each needs its backbone to win a supervised row first (T6 / T11). Our MIM and DDeP nulls on ResNet-34 (E) lower the prior for pool encoder pretraining but do not close other backbones.

### P186 FFPN (Frangi-target pretraining) and P527 SARATR-X (gradient targets) - PARKED
- Thin-structure-aware dense targets are open per BRIEF 5, but the cue they teach (dark ridge response) was measured by T5's pre-check as no better than raw darkness on faint cracks (E). Lower prior than arm 1; reopen if crackcue_input passes.
