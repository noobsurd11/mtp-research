# ALHVR port audit (and the shared SSL loop)

Scope: local copy of gaint `el-fault-detection` at `fa59d7a`, against the reference `refs/ALHVR/train_ALHVR/code/`.
Read-only. Logged numbers are from `experiments/alhvr_20pct_s{0,1}/train.log` and `experiments/mt_20pct_s0/train.log` on gaint,
and `~/noob/el_results/cv02.md` on cv02. Nothing was run.

Labels: **BUG** (code does not do what it says), **MISCONFIG** (a setting or design choice in our code that weakens the
unlabelled signal), **FAITHFUL-BUT-HARMFUL** (matches the reference but hurts in our setting), **OK**.

Paths below are relative to the repo root; `REF/` = `refs/ALHVR/train_ALHVR/code/`.

---

## Summary, ranked by how much each could explain "unlabelled loss has no effect"

| # | Finding | Label | Confidence | Affects |
|---|---|---|---|---|
| 1 | λ ramp over the whole run combined with Adam + cosine-to-zero LR: lr-weighted mean λ is 0.0156 against 0.0393 in the reference (2.5× weaker). Only 8% of our LR mass falls where λ ≥ 0.05, against 37% of the reference's iterations | FAITHFUL ramp + MISCONFIG LR | high (arithmetic from config and logs) | ALHVR |
| 2 | Our "SemiCE" is neither PV-S3's SemiCE nor Mean Teacher's consistency. It is per-class BCE-with-logits on **softmax logits**, with thresholds on **raw logits** (t_pos = 0.5·freq ≈ 0 for rare classes) and a mean over all active (pixel, class) pairs. Per pixel the pseudo-label gradient is diluted about 24× | MISCONFIG (arguably BUG against the cited method) | high that it deviates; medium that it explains the MT null | Mean Teacher (BenchmarkEL, and UCF if it uses semi_ce) |
| 3 | The MT "strong" view is mild: blur p 0.3, brightness/contrast p 0.4, noise p 0.3, no CutMix and no colour or scale change. 29% of unlabelled samples get exactly the teacher's input | MISCONFIG | medium | Mean Teacher |
| 4 | Elementwise sharpening with T = 0.1 over 24 classes: any class with p < 0.5 is sent to about 0. Where the winner's max prob is below 0.5, the DTCT target is about the zero vector, so the MSE pushes the perturbed softmax toward uniform while the entropy terms push it toward one-hot | FAITHFUL-BUT-HARMFUL (much worse with K = 24 than ACDC's K = 4) | high on the mechanism; size unmeasured | ALHVR DTCT |
| 5 | CG-CPCL CE is 71 to 81% of the unlabelled loss value and sits near an irreducible floor (cosine logits with scale 1: floor 1.41 at K = 24, 0.34 at K = 4). The loss value overstates its useful gradient | FAITHFUL-BUT-HARMFUL | high | ALHVR CPCL |
| 6 | Decoder BN running stats are updated by both the clean and the perturbed pass (decoder runs twice in train mode). Network A is then evaluated with these mixed stats | FAITHFUL-BUT-HARMFUL | medium (not measured for ALHVR; BN recal was done on SL only) | ALHVR vs SL comparisons (not on/off, same forward) |
| 7 | Gradient path, sign, float32 loss, masks, γ, regions, two optimisers and two schedulers, gradient into both networks, loss-off control: all correct | OK | high | — |

No finding of a dropped term, a detached path or a sign error. The ALHVR losses are wired correctly. They are simply
too small for most of training and partly self-cancelling (items 1, 4, 5).

---

## 1. λ schedule × optimizer (ALHVR)

**Code.** `src/losses/alhvr.py:58-61` `unsup_weight = λmax·exp(−5(1 − t/T)²)`, T = `total_steps` (20,000), λmax 0.1
(`configs/base.yaml:236`). Used at `src/trainers/alhvr_trainer.py:82-85`.
LR: `configs/base.yaml:192-197` Adam 1e-3, warm-up 200, cosine to 0 (`src/trainers/trainer.py:82-103`).

**Reference.** `REF/train_ALHVR_acdc.py:27-29,191` `consistency_weight = 0.1·sigmoid_rampup(iter_num // 150, 200)`.
The ramp ends at 150 × 200 = 30,000 = `max_iterations` (`:91`). So the ramp spans the whole run in the reference too,
and our translation is **not a units bug**. But the reference uses SGD 0.01, momentum 0.9, **constant LR** (`:155-156`,
no scheduler anywhere in the file).

**Measured interaction** (computed from the config, 20k steps):

| | lr-weighted mean λ | share of LR mass (or of iterations) with λ ≥ 0.05 |
|---|---:|---:|
| Ours (cosine to 0) | 0.0156 | 8.1% |
| Reference (constant) | 0.0393 | 37% |
| Our Mean Teacher, λ = 1.5 after 4k | 1.07 | — |

λ first reaches 0.05 at step 12,554, where our LR is already at 31% of peak.

**Logged loss shares** (`alhvr_20pct_s0/train.log`, network A; unsup = ce + cos + mse + ent before λ):

| step | λ | unsup_a | λ·unsup_a | sup_a | λ·unsup / sup | lr / lr_max |
|---:|---:|---:|---:|---:|---:|---:|
| 2,000 | 0.0017 | 3.685 | 0.0063 | 0.859 | 0.7% | 0.98 |
| 5,000 | 0.0059 | 3.496 | 0.0208 | 0.731 | 2.8% | 0.86 |
| 10,000 | 0.0285 | 3.138 | 0.0893 | 0.505 | 17.7% | 0.51 |
| 15,000 | 0.0729 | 2.911 | 0.2123 | 0.368 | 57.6% | 0.15 |
| 19,000 | 0.0987 | 2.827 | 0.2790 | 0.312 | 89.4% | 0.006 |

Seed 1 matches to the second digit. The unlabelled term becomes a meaningful share of the loss only when the LR is
below 15% of peak. These are loss-value shares, not gradient shares. Item 5 says the gradient share is lower still.

**Verdict:** FAITHFUL ramp + MISCONFIG optimizer/LR. The handoff's §9.1 is confirmed and quantified. The ALHVR
loss-off control (+0.005 ± 0.023) is close to a null by construction.

**Probe P1 (gradient share, about 2 min):** load `alhvr_20pct_s*` final weights (or any checkpoint), take 20
training batches in train mode, and compute separately for network A g_sup = ∇θ sup_a and g_u = ∇θ unsup_a (unweighted).
Report ‖g_u‖/‖g_sup‖, cos(g_sup, g_u), and per-term norms (ce, cos, mse, ent). Multiply by λ(t) to get the share at each step.
Optional: divide per parameter by `sqrt(exp_avg_sq)` from the Adam state in `latest.pth` for the Adam-effective share.
**Fix to test:** λ ramp over a fixed short horizon (e.g. full λ by step 2k to 4k, like MT), and/or constant LR for the
SSL arms *and* their SL control, and/or λmax raised so λ·‖g_u‖ ≈ 0.3 to 1 × ‖g_sup‖. Always paired with a λ = 0 control.

---

## 2. Our SemiCE is not PV-S3's SemiCE (Mean Teacher)

**Code.** `src/losses/semi_ce.py:56-108`. For every (pixel, class): positive BCE-with-logits(z_c, 1) where the teacher
**raw logit** z^T_c > t_pos[c]; negative BCE(z_c, 0) where z^T_c < −t_neg[c]; sum / n_active over all active
(pixel, class) pairs. Thresholds from `src/data/class_info.py:121-144`: t_pos = 0.5·freq, t_neg = 0.5·(1 − freq).
So t_pos ≈ 0.0009 for crack, 0.35 for background; t_neg ≈ 0.15 to 0.5. Used by MT: `src/losses/loss_factory.py:143-152`,
`configs/base.yaml:214-217`.

**Released PV-S3** (`/tmp/noob_el/pvs3/PV-S3/main/Utils/losses.py:35-90` on cv02): positive = **softmax CE against the
teacher argmax**, weighted by teacher max-prob, only where max-prob ≥ 0.6. Negative = −log(1 − p_student) on non-argmax
classes where teacher prob < threshold_neg. Plus `0.5·mean(softmax²)` (`EntireModel.py:73-75`). Thresholds are on
**probabilities**. The paper (Jha §3.2.2) describes the same softmax-based form. Our `ConfidenceCELoss` (PV-S3
reimplementation) is the softmax version. The MT arm's `semi_ce` is not.

**Why it weakens the signal:**

- (a) Softmax logits have a free per-pixel offset. A threshold on raw logits makes the positive and negative sets depend
  on that offset, not on the prediction. With t_pos ≈ 0 for rare classes, any class with a slightly positive logit
  becomes a "positive", so a pixel can have several positives, including wrong ones. If all logits drift negative, a
  pixel has no positive at all. The negatives alone can then be lowered by a constant shift that changes no prediction.
- (b) Normalisation by n_active over (pixel, class) pairs. With about 1 positive and up to 23 negatives per pixel, the
  per-pixel gradient on the pseudo-label class is about 1/24 of a per-pixel CE. With λ = 1.5 the effective per-pixel
  pseudo-label weight is about 1.5/24 ≈ 0.06 against 1 for supervised CE.
- (c) Logged `loss_con` falls from 0.246 at the ramp start to 0.050 at 6k and 0.031 at 20k (`mt_20pct_s0/train.log`),
  so λ·loss_con ≈ 0.05 to 0.07 against loss_sup 0.35 to 0.65. The loss is easily satisfied: saturated BCE gives
  vanishing gradients.

**Verdict:** MISCONFIG (it is a home-grown loss presented as SemiCE). High confidence that it deviates. Medium confidence
that it is why MT λ = 1.5 equals λ = 0, because the shared 4 + 4 BN forward and the weak views (item 3) also contribute.

**Probe P2 (seconds, no training):** on `mt_20pct_s0` final student + teacher and 10 unlabelled batches, report:
- the fraction of pixels with 0, 1, or ≥ 2 positive classes;
- the fraction where positive set = {teacher argmax};
- the mean n_active per pixel;
- for g = ∂L/∂z_student, the per-pixel share of ‖g‖² along the all-ones direction (the offset that changes no prediction);
- the ratio ‖∂(1.5·L_con)/∂θ‖ / ‖∂L_sup/∂θ‖.

**Unit test T2:** for random logits z, check `SemiCELoss(z + k, t) ≠ SemiCELoss(z, t)` while `softmax(z + k) = softmax(z)`.
This documents the offset dependence. Also check that the argmax-consistent pseudo-label CE (ConfidenceCE) is
offset-invariant.

**Fix to test:** MT with the softmax pseudo-label CE (`confidence_ce`, or plain CE on argmax with a probability
threshold), mean over pixels, plus its λ = 0 control.

---

## 3. Mild "strong" view (Mean Teacher)

`src/data/augmentations.py:54-59,132-147`; `scripts/train.py:311-316`. Student: GaussianBlur p 0.3,
RandomBrightnessContrast(±0.2) p 0.4, GaussNoise σ ≈ 3 to 7/255 p 0.3. Teacher: identical geometry, no photometric op.
P(no op) = 0.7·0.6·0.7 = 0.29, so 29% of unlabelled samples are identical for student and teacher (dropout aside). No
CutMix (`apply_cutmix` exists at `:154` but is never called), no colour or scale jitter, no feature perturbation. In
FixMatch/UniMatch-style SSL the strong view is what creates the gradient. With a teacher that is an EMA of the student
and a near-identical view, the consistency target is mostly already met.

**Verdict:** MISCONFIG, medium confidence. **Probe P3:** on a trained MT pair, report mean per-pixel KL(teacher‖student)
on the unlabelled batch for no-op samples against samples with photometric ops, and the same with CutMix applied.
**Fix:** CutMix (or the UniMatch feature-perturbation stream) on the student's unlabelled view, with its λ = 0 control.

---

## 4. DTCT elementwise sharpening with 24 classes (ALHVR)

`src/losses/alhvr.py:89-98` (elementwise, T = 0.1), `:229-239`. Reference `REF/train_ALHVR_acdc.py:38-41,203-209`, identical.

f(p) = p¹⁰/(p¹⁰ + (1−p)¹⁰) maps p < 0.5 to about 0 and p > 0.5 to about 1, per class, without renormalising. In Ω3
(both networks' perturbed confidence below γ ≈ 0.85 to 0.91), whenever the winner's max prob is below 0.5, every class
target is about 0. Σ_c (q_c − 0)² over a softmax q is minimised at uniform q (value 1/24 = 0.042). So for those pixels
the MSE pushes the perturbed branch toward **maximum entropy**, while `ent_a` (entropy of the clean and perturbed
outputs on Ω3) pushes toward minimum entropy. Because the target is not detached (`dtct_detach_target: false`,
reference also not detached), the MSE also pulls the winner's clean output. With K = 4 (ACDC) a max prob < 0.5 is much
rarer than with K = 24.

**Verdict:** FAITHFUL-BUT-HARMFUL. Mechanism certain, size unknown.

**Probe P4 (seconds):** on final weights and the 383 held-out train images in train-mode forward_dual, report:
- the share of Ω3 pixels with winner max-prob < 0.5;
- Σ_c target_c for those pixels;
- the per-class breakdown for crack and inactive.

**Unit test T4:** `sharpen(p)` for a 24-class softmax with max 0.4 gives Σ < 0.01.

**Fix to test:** `alhvr.sharpening: softmax` (flag already exists), or argmax one-hot target.

---

## 5. CG-CPCL dominates the loss value but sits on a floor (ALHVR)

`src/losses/alhvr.py:140-177,213-224`; reference `REF/train_ALHVR_acdc.py:66-85,227-237`, `REF/utils/Generate_Prototype.py:86-146`.

- Cosine logits in [−1, 1] with scale 1 (`prototype_scale: 1.0`). The minimum CE is log(1 + (K−1)e⁻²): 1.41 at K = 24,
  0.80 at K = 10 present classes, 0.34 at ACDC's K = 4. Our port drops absent classes (`:168-169`, documented), so the
  floor is about 0.8 to 1.4.
- Logged `ce_a` is 2.25 to 2.63 throughout, which is 71 to 81% of unsup_a. Roughly half of that value is irreducible.
  The loss value therefore overstates the useful gradient.
- Prototypes are rebuilt per batch from the *other* network's argmax on 4 images. The cross-network prototypes carry
  almost no crack information (handoff §6.8: 4.6% crack accuracy).
- `cos` term: `((1 − cos)·mask).mean()` over B·K·H·W (`:172-174`; reference `:82-83` same normalisation), so it scales
  with the Ω2 fraction (about 8 to 10%).

**Verdict:** FAITHFUL-BUT-HARMFUL (K = 24, scale 1, two independent feature spaces). Not a bug.
**Probe:** included in P1 (per-term gradient norms).

---

## 6. BN running stats contaminated by the perturbed pass (ALHVR)

`src/models/sa_unetpp.py:252-271`: one encoder pass, then `decode(feats)` and `decode(perturb_features(feats))`, both in
train mode. Every decoder BN running mean/var is updated twice per step, once with clean and once with perturbed (dropout
or ×(1 ± 0.3) noise) statistics, and over the whole 8-image batch (labelled + unlabelled). Network A is evaluated in
eval mode with these stats (`alhvr_trainer.py:148-159`, `trainer.py:534`). Reference same (`REF/networks/unet.py:215-224`).
The λ = 0 control shares the forward pass, so this does **not** affect the on/off comparison. It does confound ALHVR
against SL.

**Probe P6 (1 min):** recompute decoder BN running stats of ALHVR network A with clean-only `forward` passes over the 478
train images (as in `scripts/bn_recalibration.py`), re-evaluate test and val, and compare to the stored metrics.

---

## 7. Checked and correct (OK)

- **Loss assembly:** `alhvr_trainer.py:84-86`. `loss_a = sup_a + λ·unsup_a`, `loss_b` likewise, `loss = loss_a + loss_b`.
  The same `loss` is backpropagated (`:102-105`). Logged `loss_a − sup_a` equals λ·unsup_a in the logs above. Sign is
  correct (all terms are minimised).
- **No gradient cut:** `alhvr_unsup_losses` uses no `no_grad` and no `.detach()` except on γ, the region masks, the
  argmax labels and the diagnostics (`alhvr.py:66,209,246-251`). This matches the reference, where masks are int tensors
  and argmax carries no grad. Prototypes (`fb1`) and the DTCT target are not detached, as in the reference, so the
  unsupervised terms of A also send gradient into B and vice versa.
- **Precision:** network forward in bf16 autocast (`alhvr_trainer.py:75-79`). Unsup losses are computed outside autocast
  in float32 (`.float()` at `alhvr.py:202-203,216`). Sharpening p¹⁰ in float32 underflows to 0 for p < about 1e-4, then
  0/(0 + about 1) = 0, so there is no NaN. Entropy uses the +1e-6 log epsilon, the same as the reference.
- **γ and regions:** `alhvr.py:64-82` match the reference (`REF:31-36,197-201`), including the ≤/< asymmetry and the
  perturbed confidences. Logged fractions are never empty: Ω2 is 15 to 25% and Ω3 is 14 to 28% across training.
- **DTCT:** winner from clean confidences, ties to B (`alhvr.py:231-232` ≡ `REF:203`). MSE is summed over classes and
  averaged over Ω3 pixels; entropy is averaged over all pixels. Both are as in the reference (`REF:206-225`).
- **Perturbations:** `src/models/perturbations.py` ≡ `REF/networks/unet.py:215-261`: one coin per forward, the same
  perturbation for all levels, dropout threshold one U(0.7, 0.9) draw per level, noise of shape (C, H, W) shared across
  the batch. Our decoder additionally has Dropout2d(0.2) in every node (`sa_unetpp.py:79-84`), which is active in both
  passes. That is extra noise, not a bug. The reference decoder has dropout 0.
- **Two optimisers and schedulers:** `scripts/train.py:238-240` builds `optimizer_b` over `model_b.parameters()`.
  `alhvr_trainer.py:53-56,103-113`: zero_grad both, clip each network separately, step both, step both schedulers.
  Network B: different init (`train.py:221-224`).
- **Unlabelled stream:** a distinct split file, its own augmentation instance, its own stream id
  (`scripts/train.py:331-338`). `hidden_mask` never reaches a loss (`alhvr_trainer.py:93-101`).
- **Gradient checkpointing:** `sa_unetpp.py:225-229` uses `use_reentrant=False`, which preserves the RNG state by default
  (dropout masks are replayed), and `_frozen_bn_stats` stops double BN updates. Correct.
- **Loss-off control:** `alhvr.lambda_max=0` (cv02.md:568-587). It keeps the forward pass, and the logs show
  loss − sup = 0 exactly at all 400 logged steps (cv02.md:730). The control is valid; it only tests the near-zero loss
  of item 1.

## Deviations already documented (not new)

- Supervised loss is weighted CE, against the reference's unweighted CE + Dice (`REF:182-189`). Dice gives rare thin
  classes a region-level gradient. This is relevant to crack fitting, which is outside this audit.
- Batch 4 + 4 against 8 + 8; prototypes and γ from 4 images.
- Prototype feature: X[3][1] (256 channels, 1/8 resolution) against the reference's 1/8-resolution conv1x1 feature
  (64 channels).

## Out of scope, noted

The crack-fit failure (IoU 0.33 on the 47 training images) is a supervised problem. It is not caused by anything in the
SSL losses: SL has no unlabelled term and shows it too.
