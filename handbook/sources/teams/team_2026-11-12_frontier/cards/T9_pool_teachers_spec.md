# T9 spec: the unlabelled pool, teachers and ensembles (14 Nov 2026)

Tags: R = from the paper (what I read is said per paper in the family file), E = from our files, S = my judgement. Nothing here was run. No server, no GPU, no sealed data touched.

## 0. Common frame and what is already closed

- Baseline: card `house_r34_unetpp_pf_v11` (E). Screen: cv5v2, folds 0 to 4, seeds 5 and 6, pooled OOF, two-stage bootstrap (330 groups, then seeds); pass = delta >= M (M = max(0.01, 2 x SE of the A/A PF {5,6} v {7,8} contrast)) with interval above 0, which only promotes to seeds 7 to 9. Operating points from `crossfit_op` (OP-A primary, OP-F, OP-W); a crack gain counts only at OP-A and OP-W. Every arm reports the WAVE2_REVIEW section 5 guards 1 to 12. One comparison stays on one machine (cv02 W1-C1 is the table comparator; gaint W1-G is the development comparator).
- **Closed here, do not re-propose (E, BRIEF 5, handbook 11 rows 5, 10, 22, 25):** online Mean Teacher (EMA of itself, same ResNet-34) with hard, tolerant or class-threshold pseudo-labels, with or without CutMix and separate BN, on the 11.9k pool at 100% labels (P16 Sx100: n.d. on test and unseen modules); MIM (SparK-style) and DDeP on ResNet-34 with the 11.9k pool, also under PF at 100% (n.d.). These close "same backbone, same-strength teacher, hard labels, weak augmentation". They do not close: a frozen teacher stronger than the student, soft targets, strong perturbation of the student's pool inputs, anomaly priors, or SSL on other backbones.
- **Existing arms this family must not duplicate (E, WAVE2_REVIEW, T6, T7, T11 specs):**
  - T2 `ens_kd_jml`: online 2-teacher PF ensemble distilled on the **labelled training cells only** (soft CE + JML).
  - T3 `oof_soft_distill`: out-of-fold single teachers, soft crack / inactive targets on the **labelled cells only**.
  - T7 `mic_halfcell`: EMA-teacher self-training with masked consistency on the **1,008 pool half-cells only**, thresholded hard labels.
  - T7 `msc_tta`: D4 and multi-scale TTA readout. T11 `suite_hetero_ens`: heterogeneous 2-member ensembles (CPU readout). T1 `ema_wise_posthoc`, `swad_const`: weight averaging.
  - T6 `vfm_ctx_r34_pf`: frozen DINOv2 ViT-L context branch at inference.
- **What this family adds:** (1) the pool as **input volume** for distilling a frozen, stronger teacher with strong perturbation (arm 1); (2) a **reference-based anomaly map** as a label-free prior and as the benchmark's anomaly-detection track (arm 2); (3) **foundation-model feature distillation on the pool**, which would carry a T6 gain into the plain ResNet-34 at no inference cost (arm 3, gated).

## Priority table

| # | Arm | Papers | Problem | Primary (pre-declared) | Route | Build h | GPU-h (pathfinder + screen) | Gate | Priority |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `pool_ens_distill` | P005, P014, P022, P051, P080 (perturbation part), P157, P180 | crack | strict crack IoU at OP-A (must also hold at OP-W) | training_recipe | 11 | 1.5 labelling + 2.2 + 22 = about 26 | P1 (CPU, tonight's dumps) and P2 (pool teacher sanity, inside the labelling job) | 72 |
| 2 | `ad_prior` | P325, P266, P112 (stage B), AD track rows P495 P440 P441 P479 P267 P272 | crack (unseen-module reading beside it) + benchmark_row | stage A: stacked minus PF crack relF1@2 at OP-W; stage B: crack relF1@2 at OP-A (and OP-W) | analysis_only, then new_model_code | 5.5 (A) + 4 (B) | 0 (A); 1.2 + 11.5 (B) | stage A decides stage B | 55 |
| 3 | `fm_align_pool` | P080 (feature part), P395 | inactive | inactive IoU at OP-A | new_loss | 5 (after arm 1's pool loader) | 2.6 + 26 | T6 `vfm_ctx_r34_pf` screen pass, or arm 1 pass | 30 |

**First arm by expected gain per build hour: arm 1.** Reason (S): it is the only route in this family with a measured upper reference here (the ensemble is our only clear win, +0.014 to +0.018 crack IoU, E), it uses mostly existing harness parts (PF card, `data.unlabeled_pool: external` loader with its clash assert, `BatchStream` stream ids, `jml1` from `src/losses/soft_ce_jml.py`, `bench_infer.py` dumps, `crossfit_op`), and its cheapest kill (P1) runs on CPU tonight. Arm 2 stage A is CPU only and can run in parallel without touching any GPU queue; it is second because its in-distribution prior is lower and its E1 value cannot be read before the final opening.

---

## Arm 1. `pool_ens_distill`: frozen PF ensemble with D4 views labels the pool; noised PF student learns from labels plus soft pool targets

**Papers:** P005 Naive-Student, P014 ensemble KD, P022 canonical KD, P051 self-training with strong augmentation, P080 Depth Anything (perturbation ablation), P157 data distillation, P180 Noisy Student.
**Problem:** crack (in-distribution), with inactive and the unseen-module proxies as guards. **Primary:** strict crack IoU, arm minus PF, CV5 pooled OOF, at OP-A; must also hold at OP-W (same primary as `ens_kd_jml`, so the two read as a pair).

**Hypothesis (S, from R and E).** Our pool SSL failed with an EMA teacher of the same strength, hard pseudo-labels and weak augmentation (E). The papers that report self-training gains at full labels all use a teacher that is better than the student at labelling time and a student whose pool inputs are strongly perturbed: Depth Anything measured that unlabelled images without perturbation give nothing (KITTI AbsRel 0.085 -> 0.085) and with colour jitter, blur and CutMix they help (0.081) (R); Rethinking self-training reports gains at every data size with strong augmentation (R); canonical KD reports a logit-KD student with 20k unlabelled images at 99% of its teacher and 2.7 mIoU above the best supervised run (R). Soft targets also allow geometric and photometric perturbation that our hard 1 to 2 px labels do not survive (the house augmentation is label-safe only, E). A frozen ensemble with D4 views is a better pool labeller than the EMA teacher, and the student sees about 20x more distinct cell images.

**How it differs from existing arms.** `ens_kd_jml` and `oof_soft_distill` distil on the about 425 labelled training cells of a fold; this arm keeps the house loss on labelled cells unchanged and adds only the pool term. If `ens_kd_jml` passes, this arm asks whether pool volume adds to it; if `ens_kd_jml` recovers under a third of the ensemble gain (its drop rule), P022 and P061 say function matching needs many more inputs than the labelled set, which is exactly what this arm supplies. `mic_halfcell` uses an EMA teacher, hard thresholded labels and half-cells only; this arm uses a frozen ensemble, soft targets and all pool cell types.

### 1.1 Pool list (shared with arm 2 and arm 3)
- Source: `data/splits/external_unlabeled.txt` (11,938 stems, E handbook 03 section 6) and `external_unlabeled_meta.csv`.
- Exclude every stem whose image id (module) occurs in: P532, legacy test 50, E1 106, F51, H36, F19, the 17 unused `_rf`, the 7 `CSIR_00300` `_rf` cells (E: 1,979 / 196 / 88 pool cells share modules with train / val / test). Exclude every pool cell whose image md5 equals any labelled or evaluation image md5, and every pool cell flagged by T12's `dedup_embed.py` against any of those sets (when it exists; E T12 spec: 159k has about 2,400 byte-identical pairs under other ids, so duplicates in the 11.9k are plausible).
- Script `bench/pool/make_pool_list.py` writes `benchmark/splits/pool_t9.txt` and `pool_t9.meta.tsv` (stem, source, cell type, native size, per-image sd of content px) with md5. Expected size about 9,600 (S, 11,938 minus about 2,263 module matches, before dedup). Asserts fail closed: zero image-id overlap with every excluded set; count printed; md5 recorded.

### 1.2 Teacher labelling (offline, per fold)
- Teachers for fold k: two PF v1.1 runs on root `cv5v2_v11_f{k}`. On cv02 (table machine): **W1-C1 seeds 8 and 9**, students seeds 5 and 6, comparator W1-C1 seeds 5 and 6 (no seed shared between teacher and student). Fallback on gaint: W1-G seeds 5 and 6 as teachers, students seeds 5 and 6, comparator W1-G 5 and 6; seed coupling is stated in the card, and a pass is confirmed with student seeds 15 and 16.
- Assert per teacher: its `splits/train.txt` md5 equals the student root's (no teacher saw fold k).
- Inference with `scripts/bench_infer.py` on a new set `pool_t9` (pool stems only; the sealed-set guard is unchanged), bf16 allowed (targets, not dumps), D4 views: if T7's `bench/tta.py` exists, `--tta d4`; otherwise the same 8-view loop (flip x rot90, exact inverse, probability average) in `bench/pool/label_pool.py`.
- Per cell: `P = mean over 2 teachers x 8 views of softmax` (24, 512, 512). Write `pool_soft/f{k}/<stem>.npz` with `qc = round(255 * P[14])` uint8, `qi = round(255 * P[11])` uint8, `oth = argmax over the 22 other classes of P` uint8, and `dis = round(255 * |p_crack(t1) - p_crack(t2)|)` uint8 (seed disagreement, for later filters only, not used in the loss). Assert `qc + qi <= 255 + 2` on every pixel; a 512 -> 512 resize is a no-op.
- Cost (S): about 9.6k cells x 5 folds x 2 teachers x 8 views = 0.77M forwards; at about 150 images/s (house forward, bf16, A6000) about 1.5 GPU-h. Storage about 0.2 MB per cell-fold compressed, about 10 GB.

### 1.3 Student training: exact change
Card `bench/methods/pool_ens_distill_pf_v11.yaml`, `diff_ref: house_r34_unetpp_pf_v11`. New keys (all absent = house PF, bit-identical):
```yaml
pool_kd:
  enabled: true
  pool_list: splits/pool_t9.txt          # copied into each root; md5 asserted
  soft_dir: pool_soft/f{fold}            # resolved per root by the job builder; teacher md5s in the run manifest
  pool_batch: 8
  stream_id: 7                           # labelled stream untouched
  lambda: 1.0
  ramp: [2000, 4000]                     # 0 before step 2000 (after the 1k PF freeze), linear to lambda at 4000
  bn: separate_frozen_running            # see below
  jml_classes: [14, 11]
  jml_weight: 1.0
  aug:                                   # pool images only; labelled cells keep the house label-safe aug
    d4: true
    affine: {scale: [0.8, 1.25], rot_deg: 10, translate: 0.05}
    gamma: [0.7, 1.4]
    brightness_contrast: 0.3
    blur_sigma: [0.0, 0.7]               # p 0.3; capped below 1 px so 1-2 px cracks keep about 60% or more of their dip (S)
    noise_sigma: [0.0, 0.03]             # p 0.3, on [0,1] intensities before normalisation
    cutmix_p: 0.5                        # between pool cells; targets mixed with the same box
```
Pool loader: extend the existing `data.unlabeled_pool: external` path (train.py l.391-405, its clash assert against labelled stems kept) with a `PoolSoftDataset` that returns `image` (1, 512, 512) float and `soft` (3, 512, 512) uint8 (qc, qi, oth), D4 applied identically by index-based transforms; the other perturbations run on the GPU in `src/data/pool_aug.py` with a `torch.Generator` seeded from (seed, stream 7, batch index), so the labelled `BatchStream` and its RNG are untouched.

GPU warp (file `src/data/pool_aug.py`):
```
def warp(x, s, g):                                  # x (B,1,H,W) float; s (B,3,H,W) uint8 -> float
    A = random_affine(B, scale, rot, translate, g)  # (B,2,3)
    grid = affine_grid(A, x.shape, align_corners=False)
    x  = grid_sample(x, grid, mode="bilinear", padding_mode="zeros")
    qc, qi = grid_sample(s[:, :2].float()/255, grid, mode="bilinear")   # soft maps bilinear
    oth = grid_sample(s[:, 2:].float(), grid, mode="nearest").long()
    w  = grid_sample(ones_like(x), grid, mode="nearest")              # 0 outside the source image
    return x, qc, qi, oth, w
```
then gamma, brightness / contrast, blur, noise on `x` only; CutMix pastes a box of cell j into cell i for `x`, `qc`, `qi`, `oth`, `w` alike; finally the house normalisation (mean 0.5, sd 0.25).

Loss on pool pixels (file `src/losses/pool_kd.py`, reusing `jml1` from `src/losses/soft_ce_jml.py`):
```
def pool_kd_loss(z, qc, qi, oth, w, jml_classes=(14, 11), jml_weight=1.0):   # z (B,24,H,W) float32, autocast off
    logp = log_softmax(z, 1); p = logp.exp()
    qo = (1 - qc - qi).clamp(min=0)
    ce_px = -(qc * logp[:,14] + qi * logp[:,11] + qo * logp.gather(1, oth[:,None])[:,0])
    ce = (ce_px * w).sum() / w.sum().clamp(min=1)
    j = mean(jml1(p[:,c] * w, q_c * w, smooth=1.0) for c, q_c in ((14, qc), (11, qi)))
    return ce + jml_weight * j
```
Trainer step (`src/trainers/trainer.py`, a marked `pool_kd` block, off by default):
```
l_lab = sup_criterion(model(x_lab), m_lab)                  # house CE + Dice, unchanged, BN in train mode as now
if pool_kd.enabled and t >= ramp[0]:
    x, qc, qi, oth, w = pool_aug(next(pool_iter))
    with bn_running_frozen(model):                         # momentum 0 on every BN: batch stats used, running stats untouched
        z = model(x)
    loss = l_lab + lam(t) * pool_kd_loss(z, qc, qi, oth, w)
else:
    loss = l_lab
```
Two forwards (labelled, then pool) instead of one concatenated batch: the eval-time BN running statistics stay those of the labelled distribution, as in the baseline (E: joint BN with this pool made crack worse on the pool's own sources in P10 / P12; the pool's native-512 cells have about half the labelled contrast).

**Unit tests** (`tests/test_pool_kd.py`):
1. Flag off: 5-step CPU identity IDENTICAL for the house and PF cards.
2. Pool list: zero overlap with every excluded image id and image md5; count and md5 printed.
3. Labelling: a constant-output fake model gives P equal to its softmax (D4 round trip exact); uint8 error <= 1/510; `qc + qi <= 1 + 2/255`.
4. Warp: identity affine leaves `x`, `qc`, `qi`, `oth` bit-identical and `w = 1`; a 90 degree affine equals `torch.rot90` on interior pixels within 1e-5; pixels mapped from outside get `w = 0`.
5. Loss: with qc in {0, 1}, qi = 0 and oth the hard label, `pool_kd_loss` equals `SoftCEJMLLoss(soft_target=None)` on the equivalent hard mask within 1e-6; an all-zero `w` returns 0, not NaN.
6. BN: after a pool forward under `bn_running_frozen`, every `running_mean`, `running_var`, `num_batches_tracked` is bit-identical; the labelled forward updates them as in the baseline.
7. Streams: the labelled batch sequence of a 50-step run with the flag on equals the baseline's (stem lists hashed).
8. Teacher asserts fail closed on a mismatched root md5; no held-out stem of fold k appears in `pool_t9.txt` (trivially true, asserted anyway).

### 1.4 CPU pre-checks
**P1, ensemble edge and seed complementarity (CPU, W1-G dumps of tonight, 10 PF runs with `logp`; about 1 build h, minutes of CPU).** Shares its first part with gate G5(b) of `ens_kd_jml`; run once.
- (a) OOF 2-seed ensemble (mean softmax from `logp`, argmax) minus the mean of the two single seeds, through `crossfit_op`: strict crack IoU and relF1@2 at OP-A and OP-W, inactive IoU, mIoU-R13, width ratio.
- (b) Seed complementarity: for GT crack components >= 20 px, P(missed by seed 6 | missed by seed 5) (any-hit within 2 px, OP-A), pooled and per source; the same for inactive regions >= 100 px.
- (c) Per-source table of (a).
- **Rule (fixed now):** if (a) gives less than +0.005 on both strict crack IoU and relF1@2 at OP-W, the teacher has no measurable edge over the student in CV: arm 1 is parked (it would repeat the closed same-strength self-training) unless D4 views (from T7 `msc_tta` dumps of the same models) add at least +0.005 on top of the ensemble, in which case the teacher is "ensemble + D4" and the arm runs. If (b) is above 0.9, the ensemble does not find components the single model misses; arm 1 still runs (its route is consistency on boundaries) but its expected gain is set to the low end and relR@2 is not expected to move.

**P2, pool teacher sanity (inside the labelling job, read before any student run; 0 extra GPU).** Per source x cell type x native size (512 vs 1200 px): mean teacher crack px per cell (p_crack >= 0.5), share of cells with >= 20 crack px, mean seed disagreement; beside them the same numbers on the CV5 held-out crack cells and the 303 crack-free cells from the W1 dumps.
- **Rule:** if native-512 pool cells (about 57% of the pool, half the labelled contrast, E) get under 0.3x the crack-cell share of native-1200 cells of the same source and type, the teacher is blind on them and would teach "no crack" there: restrict the pool to cells whose per-image sd lies inside the 5th to 95th percentile of the labelled cells of that source (variant `pool_t9_hc`, list md5 recorded) before the screen. If the half-cell crack-cell share exceeds 3x the full-cell share of the same source, the teacher's half-cell labels are dominated by false alarms (busbar / cut-edge lines): drop half-cells from the pool for this arm (T7's arm owns them).

### 1.5 Pathfinder and screen
- **Smoke:** 1,000 steps on fold 0 seed 5: peak memory (S estimate 9 to 11 GB, two sequential forwards of 8), step time (S: about 2x the house step), the pool / labelled loss ratio, share of valid pool px.
- **Pathfinder:** fold 0, seed 5, 20k steps (about 2.2 GPU-h). Kill before the screen if fold-0 OOF predicted crack px is outside 0.75x to 1.3x the baseline's same fold-seed, or the pool loss does not fall between steps 4k and 20k.
- **Screen:** cv5v2, folds 0 to 4, student seeds 5 and 6, 10 runs, about 22 GPU-h, on the machine of its comparator. Dumps with `logp` (so the student can later be an ensemble member and a teacher).
- **Reads:** primary as above; guards 1 to 12 of WAVE2 section 5; F51 crack any-hit recall and inactive IoU (paired over the 10 models, read ledger, promotion only); T7's U-dev reads if built; per-cell-type table.

### 1.6 What it should move, and the drop rule
- R: Naive-Student student 82.5 -> 85.7 Cityscapes val mIoU at full labels with about 109k unlabelled frames (backbone also changed, so not a clean estimate); canonical KD: pure logit KD + 20k unlabelled = 79.0 against best supervised 76.3; Depth Anything: perturbation is what turns pseudo-labelled data from 0 into a gain.
- E: ensemble gain on test +0.014 to +0.018 crack IoU, relF1@2 0.881 -> 0.897; P16 Sx100 (same pool, EMA teacher) n.d.
- S: strict crack IoU +0.000 to +0.012 at OP-A; relF1@2 +0.000 to +0.012; inactive IoU -0.01 to +0.03 (inactive is data-limited and the pool has inactive cells the labelled set lacks); F51 crack any-hit recall 0 to +0.03.
- **Drop rule:** primary delta < M or interval includes 0 at OP-A, or the gain is absent at OP-W, or a WAVE2 guard trips (width outside 0.85 to 1.15x, crack-free false alarms above the guard), or the student recovers less than a third of the OOF 2-seed ensemble's own strict-IoU gain from P1(a). A pass promotes to seeds 7 to 9 against W1-C1 (16.5 GPU-h when run on cv02 with student seeds 15 to 17).
- **After a pass, in order (each its own row, not stacked now):** decomposition run with `aug` off except D4 (is perturbation the active part?); online function-matching variant (P061); hetero teacher (P298: any T6 / T11 model that passed becomes the labeller, 1 build h); round 2 with the student as teacher (P180); `ens_kd_jml` + pool stack only if both singles passed.

### 1.7 Cost and needs
- Build about 11 h: pool list and asserts 1.5; labelling script + npz writer + P2 table 2.5 (1.5 if T7 `tta.py` exists); `PoolSoftDataset` on the external-pool loader 1.5; GPU aug 1.5; loss 1; trainer block + BN context manager 1.5; tests 1.5; card and per-fold job builder 0.5. P1 script 1 h (shared with G5).
- GPU about 26: labelling 1.5, pathfinder 2.2, screen 22.
- Needs: nothing installed; pool PNGs (`data/unlabeled/images_512/`, 11,938 files on gaint) copied to the training machine (pool cells are not sealed); W1 teacher checkpoints kept unslimmed (seeds 8, 9 on cv02 must be relayed before a reboot wipes `/tmp`).

### 1.8 Risks and how it could mislead
- **Width inflation:** the ensemble predicts wider cracks than single models (E: test pixel P / R 0.621 / 0.703 v 0.644 / 0.642, W about 1.13). Soft targets carry that width into the student; relR@2 then rises for free. Guard: OP-W, width band, relF1@1 beside relF1@2.
- **Operating-point shift:** soft targets lower peak confidence; at argmax crack can shrink (relP@2 up, relR@2 down) and look like a precision gain. Guard: OP-W and the frontier read.
- **Leakage:** a teacher that saw fold k would label pool images with knowledge of held-out labels only indirectly, but a pool image of a held-out module would be a transductive leak. Guards: teacher root md5 assert; module and md5 exclusion of every evaluation set from the pool.
- **Contrast mismatch:** native-512 pool cells have half the labelled contrast (E); a blind teacher teaches background on real cracks. P2 handles it.
- **BN:** batch statistics of pool batches differ from labelled ones; with running statistics frozen during the pool forward, train-time pool normalisation (batch stats) and eval (labelled running stats) differ for pool-like test cells. If F51 or U-dev degrade while CV holds, this is the first suspect; a variant with a separate BN set for pool batches (P13's separate BN, E) is the fix, not a new arm.
- **A dev instrument that does not transfer:** CV5 has no half-cut and no scuff cells; any E1 effect of the pool's half-cells is invisible until the final opening. Do not sell an F51 change as an E1 change.

---

## Arm 2. `ad_prior`: a reference-based anomaly map from DINOv2 patch kNN, first as a CPU stacking test and the benchmark's AD track, then as an input prior

**Papers:** P325 AnomalyDINO (scoring), P266 SuperADD (bank augmentation and coverage), P112 WeakREST (stage B, residual into a supervised segmenter). AD track rows: P495 PatchCore, P440 Dinomaly2, P441 Dinomaly, P479 EfficientAD, P267 INP-Former, P272 MuSc.
**Problem:** crack (in-distribution primary, with the unseen-module reading beside it) and benchmark_row (the AD track). Anomaly-detection priors are on BRIEF's never-tried list (E).
**Primary (pre-declared):** stage A: cross-fitted stacked model minus PF alone, crack relF1@2 at OP-W (CV5 pooled OOF). Stage B: crack relF1@2 at OP-A, arm minus PF (must also hold at OP-W).

**Hypothesis (S).** The house model is blind to crack pixels it has not learned to see (E: 70% of E1 crack px get p < 0.001; 42% of crack GT below p 0.001 in an earlier audit, PROTOCOL 5.1). A kNN distance to normal patches of the same source does not depend on the 478 labels and should flag faint or unusual dark lines and region anomalies (inactive) that the supervised model misses. If the map carries information beyond the PF logits on the misses, it should first show in a cross-fitted late fusion, before any training.

### 2.1 Stage A (CPU only, 0 GPU-h): AD maps, the AD track row, and the decisive stacking test
Script `bench/ad/knn_map.py` (torch CPU, numpy):
- **Features:** DINOv2 ViT-S/14 from the local torch-hub file `dinov2_vits14_pretrain.pth` (E DESIGN 1.10) loaded into timm `vit_small_patch14_dinov2` with `strict=True` (the same loader T12's `dedup_embed.py` uses; reuse it). Input: grey cell, house normalisation replaced by ImageNet statistics on the 3-channel copy, resized 512 -> 672 (48 x 48 patches, about 10.7 px of the 512 image per patch; AnomalyDINO compares 448 and 672 for ViT-S/14, R README). Features = last block patch tokens, L2-normalised (384-d).
- **Bank for fold k (leak-free, uses training labels only):** all patches of fold k's training cells whose 14 px footprint, mapped to 512 px and dilated by 4 px, contains no crack (14), inactive (11) or ignore (255) label pixel (v1.1 training masks). Each bank patch keeps its source and module group id. Intensity-augmented copies of the bank cells (gamma 0.8 and 1.25, P266's idea against contrast shift) are added. Subsample to 300k patches by greedy k-centre coreset on a random projection to 128-d (PatchCore / SuperADD coverage idea; S: random subsampling as fallback if coreset time exceeds 1 CPU-h).
- **Score:** for each query patch, `a = 1 - max cosine` over bank patches from a **different module group** (so training cells can be scored the same way for stage B without self-matching). Map 48 x 48 -> bilinear to 512 -> Gaussian smoothing sigma 4 px. Store `ad/f{k}/<stem>.npz` as float16.
- **Query sets:** fold k held-out cells (so every P532 cell gets one OOF map), F51 and H36 with the fold-0 bank (dev reads, logged in the read ledger), pool half-cells (descriptive). Sealed sets are never queried.
- Cost (S): about 200 GFLOP per image forward, about 1,200 images + bank augmentations, and chunked matmuls of about 250k x 300k x 384 per fold: about 1 to 2 CPU-h on gaint in total.

Reads (all CV5 pooled over folds, using the W1-G PF dumps for the PF side):
1. **AD track row (benchmark):** pixel AUROC for crack (GT dilated 2 px against non-crack, non-ignore px) and inactive; AU-PRO to 30% FPR; crack relF1@2 and inactive IoU at a threshold cross-fitted on the other four folds; cell-level AUROC for "crack >= 20 px" and "inactive >= 0.5%". Per source.
2. **Missed-defect flags:** threshold `t95` = the 95th percentile, over the 303 crack-free cells, of each cell's maximum `a` (5% of crack-free cells would raise an alarm). Share of PF-missed GT crack components >= 20 px (any-hit miss at OP-A, both seeds) whose max `a` > `t95`; same for PF-missed inactive regions >= 100 px. F51 reported beside (promotion only).
3. **Stacking (decisive):** per fold k, a logistic regression (sklearn, present) fitted on the other four folds' pixels (all GT crack px dilated 1 px + a 2% random sample of other px; class-balanced weights off) with features `[clip(m_crack, -20, 20), a, a * 1(m_crack < -5)]`, predicting crack-vs-rest on fold k. The stacked crack margin replaces `m_crack` in a copy of the PF dump (other classes untouched), written with `bench/dumpfmt.py` and scored with `bench_read_w1.py` / `crossfit_op` at OP-F and OP-W against the PF dump scored the same way. Same for inactive with `m_inact` on a second copy.
- **Pass rule for stage B (fixed now):** (i) crack: stacked minus PF relF1@2 at OP-W >= +0.005 with bootstrap interval above 0, width ratio within 0.85 to 1.15; or (ii) inactive: stacked minus PF inactive IoU >= +0.01 with interval above 0; or (iii) read 2 flags >= 30% of PF-missed crack components at `t95` on CV5 **and** on F51. Pass on (i) or (ii) opens stage B with that class as primary. Pass on (iii) alone opens stage B as an unseen-module candidate (primary stays CV crack relF1@2 at OP-A as a non-inferiority read; F51 is promotion only, X9). None: park stage B; the AD track row stays (BENCH_ONLY).
- Build about 5.5 h: feature loader (reuse T12) 0.5, bank + coreset + group masking 1.5, kNN scorer and npz writer 1, stacking + dump writer 1.5, reads 1-2 + table 1.

### 2.2 Stage B (GPU, only on a stage A pass): inject the map into the PF U-Net++
Files: `src/models/ad_inject.py`; factory option `model.ad_inject.enabled` on `smp_unetpp`; data hook `extra_maps` (T3's `oof_soft_distill` hook if built, else 1.5 h here) loading `ad/f{k}/<stem>.npz` as a float mask so flips / rot90 apply identically and brightness / contrast does not touch it.
```
class ADInject(nn.Module):        # wraps the house smp.UnetPlusPlus; parameter names start with "adproj." (not "encoder."), so PF gives them full lr
    def __init__(self, base, chans=(1, 64, 64, 128, 256, 512), levels=(1, 2, 3)):   # smp resnet34 feature list: index 0 = input, 1..5 = strides 2..32; levels 1,2,3 = 64,64,128 ch at strides 2,4,8
        self.base = base
        self.adproj = ModuleDict({str(i): Conv2d(1, chans[i], 1) for i in levels})   # weights and biases zero-initialised
    def forward(self, x, ad):                                  # x (B,1,512,512); ad (B,1,512,512) in [0,1] after a fixed per-fold scale (t99 of crack-free cells -> 1)
        f = self.base.encoder(x)                               # smp features: strides 1,2,4,8,16,32
        for i in levels: f[i] = f[i] + self.adproj[str(i)](adaptive_avg_pool2d(ad, f[i].shape[-2:]))
        return self.base.segmentation_head(self.base.decoder(f))   # smp 0.5.0 decoder call signature to be checked by the engineer
```
- Train-cell maps come from the same fold-k bank with same-group patches masked (2.1), so train and held-out maps are produced by the same procedure.
- Config: `model.ad_inject: {enabled: true, levels: [1, 2, 3], dir: ad/f{fold}, scale: t99}`; everything else = `house_r34_unetpp_pf_v11`.
- **Unit tests:** flag off IDENTICAL (5-step CPU, house and PF); with zero-init `adproj`, the forward equals the house forward bit for bit for any `ad`; every `adproj` parameter receives a gradient after one step; PF puts `adproj.*` in the full-lr group; the map loader refuses a held-out stem whose map was built with a bank containing its own fold (bank manifest lists the fold's train md5); flips / rot90 move `ad` with the image (round-trip test).
- **Pathfinder:** fold 0 seed 5 (about 1.2 GPU-h; S: about 5% over the house step time, maps read from disk). **Screen:** 10 runs, about 11.5 GPU-h.
- Build about 4 h (module 1.5, hook 1.5 or 0 if built, tests 1).

### 2.3 What it should move, and the drop rule
- R: WeakREST reports supervised AP 87.6 against a prior best 86.0 on MVTec AD with residual features (no thin-structure evidence); AnomalyDINO one-shot MVTec AD AUROC 93.1 to 96.6; SuperADD MVTec AD 2 segmentation F1 62.61 / 57.42 / 54.35 (public / private / private-mixed). None reports thin 1 to 2 px defects at our scale.
- S: in-distribution crack relF1@2 0 to +0.01; inactive IoU 0 to +0.02; the main hope is recall on unseen layouts, which CV5 cannot show. Expected stage A outcome: the kNN map separates inactive well and thin cracks weakly (one 14 px patch holds a 1 to 2 px crack as about 10% of its pixels).
- **Drop (stage B):** primary delta < M or interval includes 0 at OP-A or absent at OP-W; or crack-free false alarms up beyond the guard (dark grain boundaries, BMRK padding and edge_dark are natural kNN anomalies); or width outside the band.

### 2.4 Needs and risks
- Needs: nothing installed (timm, torch, sklearn, scipy present, E DESIGN 1.10); local DINOv2 ViT-S/14 file. Optional: DINOv3 ViT-S/16 (local) as a second backbone row in the AD track. No gated weights. Other AD track rows need an isolated venv: anomalib (PatchCore, EfficientAD) and the Dinomaly2 repo (licences: Dinomaly Apache-2.0 verified; others unverified).
- **Leakage:** the bank uses training labels of fold k only; held-out cells, their modules and every evaluation set are never in a bank; same-group masking applies to train cells. Pool cells enter banks only through `pool_t9.txt` (arm 1 exclusions).
- **Source shortcut:** BMRK cells are downscaled ELPV crops with padding (E); their patches can be "anomalous" against a mixed bank. The bank is per fold over all sources and the nearest neighbour is usually same-source (S), but read 1 is printed per source; stage B must pass the per-source false-alarm guard.
- **Operating point:** a stacked margin is a new decision rule. Only OP-F and OP-W are read in stage A (OP-A has no meaning for a logistic output), so the stage A rule uses OP-W.
- **Instrument transfer:** if stage B passes only through (iii), its value is an E1 bet that CV5 cannot confirm; F51 is promotion only.

---

## Arm 3. `fm_align_pool`: align the ResNet-34 student's stride-16 features to a frozen foundation model on pool cells (gated)

**Papers:** P080 Depth Anything (feature-alignment loss with tolerance margin), P395 RS-MTDF (frozen VFM feature teachers in SSL).
**Gate:** T6 `vfm_ctx_r34_pf` passes its screen (a frozen DINOv2 ViT-L context helps at inference), or arm 1 passes (the pool is a usable input stream). If T6's arm fails and arm 1 fails, this arm stays parked: the BRIEF's frozen linear probes showed no sign of a gain (E), so there is no evidence the FM carries what we need.
**Problem:** inactive (T6's hypothesis: region-level context). **Primary:** inactive IoU at OP-A, arm minus PF, CV5 pooled OOF (T6's primary, so the two read as a pair: does R34 + alignment keep T6's gain without the ViT at inference?).

**Hypothesis (S).** If DINOv2-L context helps inactive decisions, a ResNet-34 trained to reproduce the ViT's patch geometry on about 10k pool cells can carry part of that context at no inference cost. R: Depth Anything Table 9, feature loss adds 0.081 -> 0.076 AbsRel on top of perturbed self-training; margin alpha 0.85 best (0.175 mean AbsRel against 0.188 at 1.00 and 0.178 at 0.70).

**Exact change.** Files `src/losses/feat_align.py`, a marked `fm_align` block in the trainer (shares arm 1's pool loader and GPU aug; no soft targets used).
```
teacher = timm "vit_large_patch14_dinov2" (public DINOv2-L weights, download URL unverified; T6 uses the same file), frozen, eval, bf16
proj = Conv2d(256, 1024, 1)                       # named "fmproj.", full lr; R34 layer3 output (B,256,32,32) at 512 px
on each pool batch x (B,1,512,512), after arm 1's perturbation for the student input:
    with no_grad: ft = teacher.forward_features(rgb3(resize(x_clean, 448)))  -> patch tokens (B,1024,32,32), L2-normalised
    fs = normalize(proj(layer3(x_pert)), dim=1)                                   # same geometry: x_pert = geometric aug of x_clean; ft warped by the same affine
    cos = (fs * ft).sum(1)                                                        # (B,32,32)
    keep = cos < 0.85                                                             # tolerance margin (R)
    l_feat = (1 - cos)[keep].mean() if keep.any() else 0
loss = l_lab + lam(t) * l_feat,  lam ramps 0 -> 0.1 over steps 2000 to 4000      # scout's weight; S
```
Config `fm_align: {enabled: true, teacher: dinov2_vitl14, layer: layer3, margin: 0.85, lambda: 0.1, ramp: [2000, 4000], pool_list: splits/pool_t9.txt}`; the projector is dropped at inference (dump uses `model` only, asserted).
**Unit tests:** flag off IDENTICAL; teacher has no grad and is not in the optimizer; `keep` empty returns 0; projector not in the exported weights; the labelled stream unchanged; teacher features of a D4-transformed image equal the D4-transformed features within patch-grid rounding (documents the alignment of geometry).
**Pathfinder and screen:** 1,000-step smoke (S: ViT-L forward on 8 images per step about doubles the step cost, 12 to 16 GB); fold 0 seed 5 (about 2.6 GPU-h); screen 10 runs about 26 GPU-h.
**Should move (S):** inactive IoU 0 to +0.03 if T6 passed; crack flat. **Drop:** primary < M or interval includes 0; or crack relF1@2 worse than -M at OP-A or OP-W.
**Build:** about 5 h after arm 1's loader (teacher wrapper and geometry 2, loss 1, tests 1.5, card 0.5). **Needs:** DINOv2 ViT-L/14 public weights (not gated; T6 lists the same download). DINOv3 L is gated (user's OK) and is not needed.
**Risks:** the alignment can pull layer3 away from what PF preserves (log encoder cosine per stage with `enc_probe`, E BUILD_LOG x1); a gain on inactive bought with crack loss is not a pass; the pool's CSIR/ARTS-only content means the alignment never sees CFVS / BMRK / SDLE cells.

---

## 4. Pool-side benchmark tracks worth having (S)

1. **Anomaly-detection track (label-free), from arm 2 stage A.** Rows: kNN-DINOv2 (ours, AnomalyDINO-style), SuperADD (DINOv3 bank; DINOv3 ViT-S/16 is local), PatchCore and EfficientAD (anomalib), Dinomaly2 (or Dinomaly v1), INP-Former (no external references: the most relevant row for unseen layouts), MuSc (zero-shot, transductive within a module group). Training data: clean pool cells (`pool_t9.txt`) plus crack-free labelled cells of the training folds for sources the pool lacks. Scored on CV5 held-out folds (OOF by construction) and, at the final opening only, on the U-test. Metrics: pixel AUROC, AU-PRO, crack relF1@2 and inactive IoU at a cross-fitted threshold, cell-level AUROC and recall at a 5% cell false-alarm rate (P624), latency (T4 track). Printed beside the supervised PF row so the gap is explicit. MVTec AD 2 (P623) is the template for hidden labels and shift splits.
2. **Pool declaration rule (PROTOCOL).** Any method that uses unlabelled cells must ship its pool list with md5, the module and byte-md5 exclusions against every evaluation set, and the count removed (E: 1,979 / 196 / 88 pool cells share modules with train / val / test; the 159k holds 315 labelled cells by id, 21 of them test cells, and about 2,400 byte-identical pairs). Without it, a pool method can train on twins of test cells.
3. **Distillation and deployment (PROTOCOL, with T4 of PROTOCOL 6):** a distilled single model is reported beside the ensemble it came from, at each one's inference cost; the ensemble's own row is never omitted.
4. **Calibration (P603):** ECE on crack and inactive pixels beside accuracy for every SSL, KD and foundation-model row.
5. **Pretraining table (P574, P607, P576):** same backbone and fine-tune; ImageNet, in-domain SSL from scratch, and continued SSL on a foundation model as separate rows; each at its pretraining resolution and normalisation; our MIM100-PF and DDeP rows enter as they are.

## 5. What the lead must know (S)
- Arm 1 needs teacher checkpoints that are not student seeds: on cv02, W1-C1 seeds 8 and 9 for folds 0 to 4 must be relayed off `/tmp` before any reboot. If arm 1 must run on gaint first, seed coupling is accepted for the screen and fixed at confirmation.
- P1 (CPU, about 1 h build) can kill arm 1 tonight; it is the same computation as G5(b) for `ens_kd_jml`; build it once.
- Arm 2 stage A is CPU only and yields the benchmark's AD track row whatever the outcome; it can run on gaint CPU in parallel with any GPU queue.
- The pool list with module and md5 exclusions (`pool_t9.txt`) should be the one list for every pool-using arm (T7 `mic_halfcell`, arms 1 to 3), so that exclusions are not re-derived three ways.
- Arm 3 is not worth building unless T6's frozen-ViT arm passes.
