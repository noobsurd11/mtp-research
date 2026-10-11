# 08. Experiments P1 to P7: the diagnostics that rebuilt the baseline

## What this covers
This file covers the first seven experiments of the P-series (7 to 10 Oct 2026). For each one it explains:
- what question it asked and why;
- how it was set up;
- the rules that were locked before it ran, and what those rules decided;
- the robustness checks;
- what it means (marked "Reading:");
- what it led to.

Together these experiments replaced the old training recipe and evaluation labels with a corrected baseline (P6 "L3"). They also produced the measured motivation for the method under test, tolerant pseudo-labels (P5, P7).

Numbers are copied from the result files named in each section. Two kinds of numbers appear here and must not be mixed:
- **Old era:** original 20211104 masks, from-scratch 5M U-Net++, weighted CE, strong augmentation, SemiCE Mean Teacher. These appear in P1, P2, P3 and P4 only, in their own tables.
- **P-series:** E-SCDD revised masks, P6 recipes L0 to L3, re-scored with `scripts/rescore_label_versions.py`. These appear in P6 and P7.

## Sources
- Protocols: `protocols/P1_overfit_check.md`, `P2_semice_gradient_probe.md`, `P4_frozen_feature_probe.md`, `P5_region_pseudolabel_precision.md`, `P6_corrected_baseline.md`, `P7_tolerant_pl_pilot.md`. P3 has no protocol; it was exploratory.
- Results: `results/p1/README.md`, `results/p2/README.md`, `results/p3_label_versions/README.md`, `results/p4_feature_probe/README.md`, `results/p5_region_pl/README.md`, `results/p6/README.md`, `results/p6/p6_summary.md`, `results/p6/p6_rules.txt`, `results/p7/README.md`, `results/p7/p7_rules.txt`.
- Per-cell (E1) tables for P6 and P7 checkpoints: `results/e1/e1_tables_p6_p10.md`; definitions in `results/e1/README.md`.
- Context on why each experiment was run: the session summaries (`docsrc/session_summaries.md` in the conversation scratchpad; stable copy `sources/chat/claude_session_summaries_2026-10-07_to_11.md`), `to_human/directions_2026-10-10.md`. `docsrc/user_messages.md` below is copied as `sources/chat/user_messages_2026-10-07_to_11.md` (byte-identical).
- Protocol lock commits (research repo `~/mtp/research`, `git log`):

  | Protocol | Lock commit |
  |---|---|
  | P1, P2 | `f9708c0` |
  | P4 | `855b130` |
  | P5 | `fdc7198` |
  | P6 | `db76a8c` |
  | P7 | `37985d6` |

---

## 0. How P1 to P7 connect

**Starting point (7 Oct 2026).** The user came in with three doubts:
- "it trained on 47 images and tested on same 47, to get 0.3 iou on cracks, definitely something wrong";
- the unlabelled (SSL) losses seemed to have zero effect, and they suspected "minor misconfigurations";
- the published papers report metrics that did not match theirs.

The plan was analysis first: understand the data, the models and the issues before proposing a method (`docsrc/user_messages.md`, 7 Oct).

The first seven experiments answered those doubts one at a time:

| Exp | Date | Kind | Machine | Question | One-line answer |
|---|---|---|---|---|---|
| P1 | 8 Oct | small training runs (10 images) | gaint | Why can't the model fit crack even on its training images? | Not a bug. Augmentation and the loss cap the fit; CE + Dice fits crack to 0.861 IoU |
| P2 | 8 Oct | gradient probe, no training | gaint | Why does Mean Teacher with SemiCE equal its λ = 0 control? | SemiCE's targets are incoherent: every pixel has ≥ 2 "positive" classes. All old MT results are invalid as tests of Mean Teacher |
| P3 | 10 Oct | re-scoring old runs, exploratory | gaint | Does the label version (old vs E-SCDD revised) change the conclusions? | Yes. Crack IoU moves +0.05 to +0.07 for every model, more than any SSL effect seen |
| P4 | 10 Oct | linear probe on frozen features | gaint | Do pretrained features carry crack and inactive signal? | Yes: ImageNet CNN features beat random by about +0.30 AP. DINOv2 is worse for crack |
| P5 | 10 Oct | offline pseudo-label audit | gaint | Are rare-class pseudo-labels usable inside ALHVR's regions? | Crack pseudo-labels hit the right crack but miss the exact pixels (strict P 0.27 vs 0.64 within 2 px). Motivates a tolerant target |
| P6 | 10 Oct | 21 training runs | cv02 | How much of the low score is recipe and labels? Where is there room for SSL? | Label-safe augmentation helps. The L3 recipe (ImageNet encoder + CE+Dice) is the only one that turns extra labels into better scores |
| P7 | 10 Oct | 9 training runs | cv02 | Does a tolerant pseudo-label loss beat hard pseudo-labels and the loss-off control (on the rule-selected base L0)? | Pilot only (no label headroom on L0). The loss gives no gain; tolerant is clearly less harmful than hard pseudo-labels |

**The chain of reasoning:**
1. P1 cleared the code and data of bugs and pointed at the recipe.
2. P2 cleared the SSL code of the user's suspected "zero effect" bug in a different way: the old unlabelled loss (SemiCE) had a real gradient but was not a valid consistency loss.
3. P3 showed that the evaluation labels themselves were noisy enough to hide effects, so the project switched to the E-SCDD revised masks.
4. P4 justified an ImageNet-pretrained CNN encoder.
5. P5 measured why pixel-exact pseudo-labels fail on 1 to 2 px cracks, which became the "tolerant pseudo-label" idea.
6. P6 rebuilt the supervised baseline on revised labels, one change per step (L0 to L3).
7. P7 ran the first pilot of the tolerant loss. P6's rules selected L0 as its base, and L0 then turned out to have no label headroom, so P7 could only be a pilot.

That set up P8 (same arms on L3), covered in `09_experiments_P8_P12_ssl_series.md`.

**Terms used below** (full definitions in `04_glossary_and_naming.md`):
- IoU: intersection over union of predicted and true pixels of a class, pooled over all cells of the split.
- AP: pixel average precision from score histograms with 1,000 bins.
- relF1@2 / relP@2: relaxed F1 and precision, where a crack pixel counts as correct if it is within 2 px of the other mask.
- Bin-0 share: the share of true defect pixels that the model scores below 0.001, so AP cannot rank them.
- λ: the weight on the unlabelled loss.
- EMA teacher: the Mean Teacher's averaged copy of the student.
- Arms: the variants compared in one experiment.

---

## P1. Overfit check: can the model fit crack on its own training images?

**Question.** Why does a supervised U-Net++ that saw 47 labelled images about 3,400 times each still score only 0.325 crack IoU on those same 47 images, while inactive reaches 0.88? (`protocols/P1_overfit_check.md`; the 0.325 comes from `reports/fit_vs_generalise.md` on gaint for run `sl_10pct_b8_s0`)

**Why it was run.** The user's first doubt (7 Oct): "trained on 47 images and tested on same 47, to get 0.3 iou on cracks, definitely something wrong". A 5M-parameter network should memorise 47 images. The protocol lists four hypotheses:

| ID | Hypothesis | Prediction if true |
|---|---|---|
| H1 | Operating point: √-inverse-frequency class weights make "crack" the cheaper error, so predictions are dilated | Plain CE, no aug (B) memorises: crack IoU ≥ 0.8. Weighted, no aug (A) has AP ≥ 0.9 but precision < 0.6 |
| H2 | Augmentation (±5° rotation, blur, noise) stops memorisation of 2 to 3 px lines | Weighted with standard aug (E) stays near IoU 0.3 to 0.4 and AP < 0.8; A clearly higher AP |
| H3 | Labels are inconsistent at the 1 to 2 px level | Even B plateaus below about 0.6 crack IoU while inactive > 0.9; relaxed IoU much higher than strict |
| H4 | Pipeline bug (bf16 numerics, image/mask misalignment, model output path) | fp32 (D) differs materially from B; or every arm fails including inactive; or the step-0 overlays show misalignment |

**Setup** (old era; `results/p1/README.md`).
- **Code and time:** gaint, 8 Oct 2026, 00:46 to 01:52 IST, `scripts/overfit_check.py --arm {A..E}` (copy in `scripts_gaint/`). Code commits on gaint `28686c0` (P1 and P2) and `4474d04` (replicates).
- **Images:** 10 train images that contain crack, the first 10 (sorted) of `labeled_10pct` seed 0: ARTS ×4, BMRK ×2, CFVS ×4. One is from module `CFVS_00114`, which has dotted labels.
- **Training:** batch 8 with replacement, 3,000 steps (about 2,400 passes per image), Adam 1e-3, constant after a 200-step warm-up.
- **Model:** the SL-run model (U-Net++, 32 filters, dropout 0.2, from scratch).
- **Scoring:** on the same 10 images, evaluation transform.
- **Step 0 (no training):** loader mask vs raw PNG overlays.

| Arm | Loss | Augmentation | Precision |
|---|---|---|---|
| A | weighted CE (weights of the 10% subset) | none | bf16 autocast |
| B | plain CE | none | bf16 |
| C | plain CE + soft Dice (crack, inactive) | none | bf16 |
| D | plain CE | none | fp32 |
| E | weighted CE | standard training augmentation | bf16 |

Seeds: one run per arm, except B and D, which got 3 seeds as replicates for H4 (added 8 Oct, 02:55 IST).

**Deviation disclosed.** Arm D's first attempt ran out of memory while sharing the GPU. It was rerun alone with the protocol unchanged, and the failed log is kept.

**Locked rules** (protocol):
- B ≥ 0.8 and A < 0.6 with A's AP ≥ 0.9 → H1 (the class weights are the cap).
- A's AP high and E's AP low → H2 (augmentation geometry must be reconsidered).
- B < 0.6 with high relaxed IoU → H3 (switch to a tolerance-aware crack metric).
- |D − B| > 0.05, or step 0 misaligned → H4 (fix the pipeline first).

**Results** (old era, step 3,000, `results/p1/README.md`):

| Arm | Setting | Crack IoU | P | R | AP | relaxed F1 1 px / 2 px | Inactive IoU | Inactive AP |
|---|---|---:|---:|---:|---:|---|---:|---:|
| A | weighted CE, no aug, bf16 | 0.612 | 0.618 | 0.985 | 0.929 | 0.938 / 0.981 | 0.979 | 1.000 |
| B | plain CE, no aug, bf16 | 0.677 | 0.811 | 0.804 | 0.884 | 0.942 / 0.962 | 0.956 | 0.998 |
| C | plain CE + soft Dice, no aug, bf16 | 0.861 | 0.942 | 0.909 | 0.953 | 0.970 / 0.971 | 0.985 | 0.997 |
| D | plain CE, no aug, fp32 | 0.605 | 0.792 | 0.719 | 0.838 | 0.898 / 0.928 | 0.913 | 0.995 |
| E | weighted CE, training augmentation, bf16 | 0.381 | 0.426 | 0.782 | 0.587 | 0.743 / 0.848 | 0.751 | 0.973 |
| original `sl_10pct_b8_s0` (20k steps, aug, its 47 images) | | 0.325 | 0.33 | 0.95 | 0.64 | | 0.881 | 0.99 |

Replicates for H4:

| Arm | seed 0 | seed 1 | seed 2 | mean ± sd crack IoU | crack AP | relaxed F1 1 px | inactive IoU |
|---|---:|---:|---:|---|---|---|---|
| B bf16 | 0.677 | 0.694 | 0.634 | 0.668 ± 0.031 | 0.885 ± 0.006 | 0.937 ± 0.016 | 0.940 ± 0.023 |
| D fp32 | 0.605 | 0.661 | 0.701 | 0.656 ± 0.048 | 0.869 ± 0.033 | 0.927 ± 0.026 | 0.923 ± 0.033 |

All arms except E were still improving at step 3,000.

**Verdict per rule** (`results/p1/README.md`):

| Hypothesis | Measured | Verdict |
|---|---|---|
| H4, misalignment | loader mask identical to the raw PNG in 10/10 images; image difference 4e-6 | Refuted |
| H4, bf16 | seed 0 gap 0.072; over 3 seeds B 0.668 ± 0.031 vs D 0.656 ± 0.048 | Refuted (the seed-0 gap was run-to-run spread) |
| H1, class weights | B 0.677, A 0.612, A's AP 0.929 | Not met as written. Partial support: weighting costs precision (0.62 vs 0.81) but is not the main cap |
| H2, augmentation | A AP 0.929 vs E 0.587; IoU 0.612 vs 0.381 | Met. Augmentation is the largest single factor |
| H3, label inconsistency caps fitting | B 0.677; C reaches 0.861 | Refuted as a cap on fitting |

No locked prediction covered arm C. CE + soft Dice fits crack far better than CE alone (0.861 vs 0.677).

**Robustness.** Seed sd of crack IoU is 0.03 to 0.05 here (B and D). So A vs B (0.61 vs 0.68) is within noise; C (0.86) and E (0.38) are far outside it.

**Reading:**
- The "0.3 on its own training images" is not a code or data bug. It comes from the training recipe:
  - augmentation: blur kernels of 3 to 7 px and ±5° rotations applied to labels a median 1.75 px wide;
  - loss: weighted CE dilates predictions.
- Fitting is not generalisation. Generalisation has a separate ceiling: two independent annotations of the same image agree only about 0.26 crack IoU (`data_analysis/`, one solid pair; see `03_datasets_and_splits.md`).

**What it led to:**
- Label-safe augmentation (flips and 90° rotations plus brightness/contrast; no blur, no small-angle rotation of labels). This became P6's L1 step.
- Trying Dice-type losses on held-out data. This became P6's L3 step.
- The rule "fix the supervised recipe before measuring SSL on it".

---

## P2. Does the SemiCE consistency term actually move the student?

**Question.** Old-era Mean Teacher on BenchmarkEL with λ = 1.5 scored the same as its λ = 0 control (paired −0.000 ± 0.024). Is the unlabelled loss doing anything? (`protocols/P2_semice_gradient_probe.md`)

**Why it was run.** The user suspected "bugs in the training (minor misconfigurations) causing the unlabelled losses having zero effect". Code reading showed that the loss (`src/losses/semi_ce.py`, `src/data/class_info.py:121-144`) is not standard Mean Teacher:
- it applies per-class binary cross-entropy to the logits of a softmax network;
- it chooses "confident" sets on raw logits (positive if `teacher_logit[c] > 0.5·freq[c]`, about 0.001 for crack; negative if `< −0.5·(1 − freq[c])`);
- softmax ignores a constant added to all logits of a pixel, so these sets have no fixed meaning.

**Hypothesis (mine, written into the protocol).** SemiCE gives little gradient that changes class decisions:
- most of its logit-gradient lies along the per-pixel class-mean direction (share > 0.5);
- and/or its gradient norm is < 0.1× the supervised term;
- and/or its positive sets are incoherent.

**Setup** (old era).
- Model: `experiments/mt_20pct_s0`, final weights (student and EMA teacher).
- Data: 40 training batches built exactly as in training.
- Forward and backward only, no optimiser step.
- Run on gaint, 8 Oct 2026, 00:44 IST: `scripts/probe_semice_gradient.py --run experiments/mt_20pct_s0 --batches 40`.
- Raw output: `results/p2/p2_semice_mt_20pct_s0.json`.

**Locked rule.** Any one of the following means SemiCE as implemented is not a valid consistency loss, and every MT result with it says nothing about Mean Teacher itself:
- offset share > 0.5;
- ‖λ∇ loss_con‖ < 0.1 ‖∇ loss_sup‖;
- > 20% of unlabelled pixels with ≥ 2 positive classes.

**Results and verdict** (`results/p2/README.md`):

| Prediction | Measured (40 batches, mean ± sd) | Verdict |
|---|---|---|
| Offset share of the logit-gradient > 0.5 | 0.041 ± 0.009 | Refuted: the gradient is not wasted on a common shift |
| ‖∇ λ·loss_con‖ < 0.1 ‖∇ loss_sup‖ | 0.25 ± 0.35 (per batch 0.02 to 1.93) | Not met: the term is not negligible |
| > 20% of unlabelled pixels with ≥ 2 positive classes | 100% of pixels | Met, strongly. **The rule fires** |

What the positive sets contain:

| Class | t_pos | Unlabelled px flagged positive | Flagged negative |
|---|---:|---:|---:|
| background | 0.330 | 98.9% | 1.0% |
| padding | 0.105 | 92.1% | 7.3% |
| crack | 0.0013 | 20.3% (true crack is about 0.19% of pixels) | 78.6% |
| inactive | 0.0010 | 2.9% | 96.8% |

Further measurements:
- The gradient is nearly orthogonal to the supervised gradient (cosine 0.07 ± 0.40).
- The logged ratio λ·loss_con / loss_sup sat at 0.10 to 0.15 from step 3,000 to the end, so the term was active throughout.

**Side finding (measured).** A standard pseudo-label rule (teacher max-prob ≥ 0.95) covers 77% of unlabelled pixels. Of those confident pixels:

| Class | Share |
|---|---|
| background | 66.7% |
| padding | 22.8% |
| crack | 0.024% (about 8× under its labelled share of about 0.19%) |
| inactive | 0.042% |

This is the rare-class starvation problem of confidence-thresholded SSL, measured on this data.

**Reading:**
- My own hypothesis (the gradient is wasted on a common shift) was wrong.
- The gradient is real, but its target pushes background, padding and crack up at the same time, so it does not encode the teacher's prediction. Its net effect is about zero, as the λ = 0 control showed.
- Therefore every old Mean Teacher result is a test of this loss, not of Mean Teacher. That covers BenchmarkEL MT-20, the external-pool queue and UCF-EL MT on cv02. The project memory records them as invalid (`06_history_phase0_phase1.md`).

**Caveat.** At the final weights the learning rate is about 0, the student is about the teacher (argmax disagreement 3.4%), and the model was evaluated in train mode. The structural findings do not depend on this.

**What it led to:**
- A correct hard pseudo-label loss (`confidence_ce`, used as arm B from P7 on).
- The rare-class problem as the central SSL difficulty.
- The external-pool queue on gaint was held by the user (7 to 8 Oct) and stays held.

---

## P3. Does the label version change the conclusions? (EXPLORATORY, no protocol)

**Question.** BenchmarkEL has two label versions for the same images:
- "old": our `dataset_20211104` masks;
- "new": the E-SCDD masks (HuggingFace `snt-ubix/escdd`, MIT licence, built on BenchmarkEL `20221008` and described as having "refined pixel-level annotations").

If the same models are scored against each version, do the conclusions change? (`results/p3_label_versions/README.md`)

**Why it was run.** The directions work on 10 Oct found the revised release. Earlier label analysis had shown that crack labels are thin and noisy (see `03_datasets_and_splits.md`). There was no protocol, so every statement here is exploratory.

**Setup.**
- gaint, 10 Oct 2026, about 09:50 IST, read-only inference with `scripts_gaint/rescore_label_versions.py`.
- Models: final-step `latest.pth` of existing old-era runs.
- Scored on our test (50) and val (54) stems.
- Images are pixel-identical between the versions (576/577 checked, `compare.py`).

**How the labels differ** (`compare.py`, `per_img.json`):
- E-SCDD contains 577 of our 582 images; 185 of them are in a different split there.
- 361 of the 577 masks are identical. 129 of the 281 crack images have a changed crack mask, including 34 of the 50 test images.
- Changed crack masks have a median 1.67× more crack pixels, and are almost entirely within 2 px of the old labels (relaxed agreement 0.98 / 0.98). So this is a cleaning (dotted labels joined, widened), not an independent re-annotation.
- Crack IoU between the two versions: test 0.745, val 0.732, train 0.81. Inactive: 0.93 to 0.96.

**Results** (old-era models, crack, dataset-level, mean ± sd over 3 seeds):

| Split | Run | IoU old → new | AP old → new | relaxed P@2 old → new |
|---|---|---|---|---|
| test | SL-10% b8 | 0.304±0.005 → 0.355±0.005 | 0.492±0.004 → 0.527±0.001 | 0.73 → 0.77 |
| test | SL-100% b8 | 0.283±0.003 → 0.339±0.006 | 0.457±0.006 → 0.541±0.001 | 0.70 → 0.76 |
| val | SL-10% b8 | 0.228±0.006 → 0.292±0.007 | 0.348±0.010 → 0.427±0.005 | 0.66 → 0.70 |
| val | SL-100% b8 | 0.224±0.001 → 0.290±0.001 | 0.371±0.007 → 0.478±0.001 | 0.64 → 0.70 |

Single runs show the same pattern: SL-20% b8 s0 test IoU 0.230 → 0.280; MT-20% s0 test IoU 0.270 → 0.325. Inactive changes little: test IoU within ±0.03, val within ±0.002.

**Reading (exploratory):**
- The label version alone moves crack IoU by +0.05 to +0.07 for every model. That is larger than any SSL-vs-supervised difference measured before or since.
- The effect of label count depends on the label version:
  - old labels: 10% beats 100% on test crack AP (0.49 vs 0.46);
  - revised labels: 100% beats 10% (0.54 vs 0.53 test; 0.48 vs 0.43 val).
  So part of the earlier finding "label count does not move BenchmarkEL" may be noise in the evaluation labels.
- **Caveats:**
  - Revised crack labels are wider, which flatters over-predicting models.
  - The AP ranking change is the more robust signal.
  - E-SCDD's annotation provenance is not documented.
  - Training still used the old labels here.

**What it led to.** From P6 on, every experiment trains and scores on the revised masks (`data.mask_subdir=labeled/masks_escdd`). Old-label scores are kept as secondary. P14 later measured the label effect under training (see `10_experiments_P13_P16_E1.md`).

---

## P4. Frozen-feature linear probe: do pretrained features carry the signal?

**Question.** Do frozen pretrained features carry crack and inactive information better than random features? This decided whether two directions were worth 1 to 2 GPU-days (`protocols/P4_frozen_feature_probe.md`; rows from `to_human/directions_2026-10-10.md` §4):
- row 3: MIM pretraining;
- row 6: foundation-teacher distillation.

**Setup.**
- Locked 10 Oct (commit `855b130`). Run on gaint, about 5 min in total: `scripts_gaint/p4_feature_probe.py`.
- **Encoders (frozen):** ResNet-50 random init; ImageNet ResNet-50; ImageNet ConvNeXt-Tiny; DINOv2 ViT-S/14. Reference only: our old-era supervised U-Net++ encoder from `sl_100pct_b8_s0`. DINOv3 was skipped because its weights are gated behind a licence the user must accept.
- **Features:** stride-4 and stride-8 stages; ViT patch tokens at 518 px input.
- **Probe:** a linear 1×1 conv per stage, upsampled and summed; 24 classes; plain CE.
- **Training:** 47 images (`labeled_10pct` seed 0) with old masks; Adam 1e-3; 2,000 steps; batch 8; no augmentation; 2 probe seeds.
- **Evaluation:** val (54) + test (50), pooled (104), against old and revised masks; dataset-level pixel AP, argmax IoU, relaxed F1@2.

**Locked rules** (decision metric: pooled val+test AP, revised labels, mean of 2 probe seeds):
1. If the best pretrained encoder reaches at least random AP + 0.10 on crack or inactive, rows 3 and 6 stay.
2. If DINOv2's crack AP is below ImageNet ResNet-50's, drop ViT-patch features for crack and keep them for region classes only.
3. If no pretrained encoder beats random by at least 0.05 AP on either class, downgrade rows 3 and 6.

**Results** (`results/p4_feature_probe/README.md`; probe seed spread ≤ 0.011):

| Encoder (frozen) | Crack AP, pooled, revised | Inactive AP, pooled, revised | Crack AP test old/rev | Crack AP val old/rev | Crack relaxed P@2 / R@2 |
|---|---|---|---|---|---|
| ResNet-50, random init | 0.029 | 0.097 | 0.039 / 0.045 | 0.010 / 0.014 | 0.28 / 0.02 |
| ResNet-50, ImageNet | 0.321 | 0.423 | 0.324 / 0.353 | 0.223 / 0.258 | 0.78 / 0.35 |
| ConvNeXt-T, ImageNet | 0.331 | 0.383 | 0.328 / 0.371 | 0.226 / 0.251 | 0.87 / 0.26 |
| DINOv2 ViT-S/14 | 0.183 | 0.384 | 0.175 / 0.197 | 0.122 / 0.155 | 0.50 / 0.13 |
| ref.: our U-Net++ encoder, SL-100 (old era) | 0.244 | 0.266 | 0.246 / 0.281 | 0.137 / 0.175 | 0.80 / 0.27 |
| ref.: full SL-10% model (not a probe; old era) | – | – | 0.492 / 0.527 | 0.348 / 0.427 | – |

**Verdict:**
1. Rule 1 fires: best pretrained beats random by +0.30 crack AP and +0.33 inactive AP. Rows 3 and 6 stay.
2. Rule 2 fires: DINOv2 crack AP 0.183 < ImageNet ResNet-50 0.321. ViT-patch features are dropped for crack and kept for region classes.
3. Rule 3 does not fire.

**Robustness and caveats (exploratory).** The random-init probe is close to degenerate (BN statistics at init), but rule 1's margin is far too large for that to matter.

**Reading:**
- Convolutional stride-4/8 ImageNet features separate crack linearly better than our own supervised encoder's, with high relaxed precision (0.78 to 0.87) and low recall.
- ImageNet ResNet-50 features alone reach inactive AP 0.42.

**What it led to:**
- The ImageNet-initialised CNN encoder became P6's L2 step (`smp_unetpp`, resnet34 ImageNet).
- A CNN rather than ViT teacher for thin cracks.
- P15 later tested a domain-trained (UCF-EL) encoder against ImageNet init (see `10_experiments_P13_P16_E1.md`).

---

## P5. Are rare-class pseudo-labels usable inside ALHVR's regions?

**Question.** ALHVR (the paper the user's method is inspired by; see `05_literature_and_baselines.md`) splits unlabelled pixels into regions by how sure its two networks are:
- r1 / Ω1: both sure;
- r2 / Ω2: one sure;
- r3 / Ω3: both unsure.

It puts pseudo-label targets in r2 and r3. P5 asked how precise those targets are for crack and inactive, and whether per-class thresholds γ_c route rare classes better than ALHVR's single global γ (`protocols/P5_region_pseudolabel_precision.md`). This decided direction row 2 (rarity-aware routing).

**Setup.**
- Locked 10 Oct (commit `fdc7198`). Offline, read-only, no training. Run on gaint, 10 Oct about 10:00 IST: `scripts_gaint/p5_region_pl_precision.py`.
- **Models:** old-era runs `alhvr_20pct_s0` and `s1`, final weights, networks A and B, in eval mode (a disclosed deviation: training used batch statistics).
- **Data:** 378 unlabelled train images (seed-0 20% split, those with E-SCDD masks), pooled over both runs.
- **Region rules:**
  - global γ ≈ 0.94 per batch, as trained;
  - per-class γ_c: crack 0.70, inactive 0.77, background 0.95.
- **Targets as in ALHVR:** r2a gets pl_b; r2b gets pl_a; r3 gets the winner's label.
- **Reference rule:** ensemble probability ≥ 0.95.
- **Caveat stated in the protocol:** the unlabelled loss was ineffective in these ALHVR runs (its weight never reached full strength), so A and B are close to two supervised models.

**Locked rules:**
1. **Crack.** If relaxed 2-px precision of crack targets in Ω3 under per-class γ_c (revised labels) is < 0.5, hard pseudo-labels for crack in Ω3 are unusable; use labelled anchoring or tolerance-aware consistency there. If precision ≥ 0.5 and recall ≥ 0.5, per-class routing with pseudo-labels is viable.
2. **Inactive.** The same rule with strict precision.
3. **Per-class thresholds.** If γ_c does not move ≥ 10 points of GT-crack share out of Ω3 at precision ≥ the global rule's, per-class thresholds do not help routing for crack.

**Results, crack** (revised labels; old labels in brackets for strict P; `results/p5_region_pl/README.md`):

| Rule | Region | Share of GT crack | Strict P | Relaxed P (2 px) | Recall |
|---|---|---|---|---|---|
| global γ | r1 (both sure) | 0.18 | 0.53 (0.45) | 0.90 | 0.69 |
| global γ | r2 (one sure) | 0.10 | 0.42 (0.36) | 0.76–0.81 | 0.63–0.69 |
| global γ | r3 (both unsure) | 0.72 | 0.27 (0.23) | 0.64 | 0.62 |
| per-class γ_c | r1 | 0.54 | 0.42 (0.36) | 0.83 | 0.84 |
| per-class γ_c | r2 | 0.14 | 0.22 (0.19) | 0.53–0.57 | 0.66–0.69 |
| per-class γ_c | r3 | 0.32 | 0.17 (0.14) | 0.48 | 0.29 |
| reference: ensemble prob ≥ 0.95 | – | recall of all GT crack 0.08 | 0.59 (0.50) | 0.96 | – |

**Results, inactive** (revised; differences from old labels ≤ 0.01):

| Rule | Region | Share of GT inactive | P | Recall |
|---|---|---|---|---|
| global γ | r3 | 0.54 | 0.53 | 0.51 |
| global γ | r1 | – | 0.86 | – |
| per-class γ_c | r3 | 0.28 | 0.43 | 0.37 |
| reference (≥ 0.95) | – | – | 0.88 | 0.26 |

**Verdict per rule:**

| Rule | Measured | Verdict |
|---|---|---|
| 1. Crack | Ω3 relaxed P under γ_c = 0.48 (recall 0.29) | Fires (borderline): no winner pseudo-labels for crack in Ω3 |
| 2. Inactive | Ω3 strict P under γ_c = 0.43 | Fires |
| 3. Per-class γ_c | moves 40 points (0.72 → 0.32), but r1 precision falls (strict 0.53 → 0.42, relaxed 0.90 → 0.83) | Not met: per-class thresholds trade Ω3 share for precision |

**Reading (exploratory):**
- **Crack pseudo-labels point at the right crack but miss the exact pixels.**
  - Ω3 under global γ: strict 0.27 vs relaxed 0.64.
  - At the confident end: 0.59 vs 0.96.
- A target that tolerates 1 to 2 px offsets would keep most of the signal that a pixel-exact target throws away. This is the measured motivation for the tolerant pseudo-label loss (`tolerant_pl`).
- The confident rule is precise but covers only 8% of GT crack: the same starvation P2 measured.
- Figure: `results/p5_region_pl/fig_p5_offset.png`.

**What it led to.** The `tolerant_pl` loss (code commit `0367079`). In one sentence (P7 protocol): rare-class pixels are credited if the student predicts the class anywhere within R = 2 px; confident head-class pixels away from rare targets get ordinary CE; everything else gets no loss. Tested first in P7.

---

## P6. Corrected supervised baseline: a one-change-per-step ladder (mid-term "Experiment 1")

**Question.** How much of the low crack and inactive score comes from the recipe and the labels? How much room is left for SSL at 10% labels under a corrected recipe? (`protocols/P6_corrected_baseline.md`)

**Why it was run.**
- On 10 Oct the user asked which two experiments would give the best mid-term material in 4 days. The answer was: Experiment 1 = P6 (corrected baseline), Experiment 2 = P7 (tolerant-PL pilot).
- P1 and P3 had shown that recipe and labels mattered more than anything else measured.

**Setup.**
- **Lock and code:** locked 10 Oct before any run (commit `db76a8c`). Code: gaint repo `el-fault-detection` at commit `824fab0`, deployed to cv02 (recorded in each run's `REVISION`).
- **Labels:** E-SCDD revised masks (`data/labeled/masks_escdd`) for 577/582 stems, with the old mask for 5 train stems absent from E-SCDD (none in the 10% subset). E-SCDD classes 24 to 29 are mapped back to the old label at those pixels.
- **Training:** 20,000 steps; batch 8 labelled; Adam 1e-3 with weight decay 1e-4; 200-step warm-up then cosine to 0; grad clip 1; bf16; `deterministic: true`; seeds 0, 1, 2.
- **Checkpoint:** final step.
- **Hardware:** cv02 (RTX A6000), at most 3 runs per GPU.
- **Run window:** 21 runs, 10 Oct 11:46 to 15:32 IST, all rc = 0.

| Arm | Model | Augmentation | Loss | Labels |
|---|---|---|---|---|
| L0 | `unetpp` (5M, from scratch) | `strong` (flips/rot90 + ±5° rotation + blur + noise + brightness/contrast) | weighted CE (√inv-freq, cap 10) | 10%, 100% |
| L1 | `unetpp` | `labelsafe` (flips/rot90 + brightness/contrast only) | weighted CE | 10% |
| L2 | `smp_unetpp` (resnet34 ImageNet, 26M) | `labelsafe` | weighted CE | 10% |
| L3 | `smp_unetpp` | `labelsafe` | CE + soft Dice (crack, inactive) | 10%, 20%, 100% |

Evaluation: `scripts/rescore_label_versions.py` (read-only) on final weights, test (50) and val (54), revised labels primary, old labels secondary.
- Primary metrics: crack AP and inactive AP.
- Secondary: crack IoU, relaxed F1@1/2, relaxed precision@2, inactive IoU.

**Locked rules:**
1. A ladder step helps if the mean change (3 seeds, test, revised) in crack AP or inactive AP is > 0.01 and > 2·√((sd_a² + sd_b²)/3). This formula, "rule 1", is reused in every later experiment; see `07_methodology_rules_and_statistics.md`.
2. The base for Experiment 2 is the 10% arm with the highest val mean of (crack AP + inactive AP)/2. Selected on val, reported on test.
3. SSL headroom = base@100% − base@10% on pooled val+test, mean of (crack AP + inactive AP)/2. If < 0.02, Experiment 2 is a pilot.

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p6/README.md`):

| Arm | crack AP | inactive AP | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | val crack AP | val inactive AP |
|---|---|---|---|---|---|---|---|---|
| L0 10% (old recipe) | 0.553±0.015 | 0.621±0.003 | 0.319±0.051 | 0.439±0.015 | 0.746±0.078 | 0.690±0.126 | 0.466±0.006 | 0.494±0.054 |
| L1 10% (+label-safe aug) | 0.574±0.006 | 0.649±0.017 | 0.368±0.004 | 0.473±0.014 | 0.806±0.004 | 0.803±0.015 | 0.478±0.002 | 0.349±0.159 |
| L2 10% (+ImageNet resnet34) | 0.519±0.003 | 0.477±0.018 | 0.392±0.003 | 0.383±0.024 | 0.806±0.003 | 0.838±0.009 | 0.394±0.003 | 0.397±0.025 |
| L3 10% (+CE+Dice) | 0.400±0.004 | 0.302±0.018 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.288±0.011 | 0.303±0.050 |
| L3 20% | 0.433±0.004 | 0.335±0.042 | 0.398±0.002 | 0.347±0.043 | 0.822±0.008 | 0.939±0.006 | 0.309±0.003 | 0.462±0.019 |
| L0 100% | 0.545±0.003 | 0.612±0.006 | 0.337±0.004 | 0.391±0.008 | 0.782±0.008 | 0.744±0.010 | 0.484±0.006 | 0.597±0.026 |
| L3 100% | 0.593±0.003 | 0.420±0.018 | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.511±0.004 | 0.413±0.020 |

Old-label columns (test crack AP / IoU, old labels) are in `results/p6/p6_summary.md`: for example L3 100% 0.510±0.015 / 0.416±0.006 and L0 10% 0.458±0.011 / 0.254±0.042.

**Verdict, rule 1** (test AP; thresholds from `results/p6/p6_rules.txt`):

| Step | crack AP | inactive AP | Verdict |
|---|---|---|---|
| L0 → L1, label-safe augmentation | +0.020 (thr 0.019) | +0.028 (thr 0.020) | Helps both |
| L1 → L2, ImageNet encoder | −0.054 (thr 0.010) | −0.172 (thr 0.029) | Hurts both |
| L2 → L3, CE+Dice | −0.119 (thr 0.010) | −0.174 (thr 0.029) | Hurts both |
| L0 10% → 100% labels | −0.009 | −0.009 | No detectable effect |
| L3 10% → 100% labels | +0.193 | +0.117 | Helps |
| L3 10% → 20% labels | +0.033 (thr 0.010) | +0.032 (thr 0.053) | crack AP helps; inactive n.d. |

Secondary, at the argmax operating point (`p6_rules.txt`):
- L1 → L2: crack IoU +0.024 (helps), inactive IoU −0.089 (hurts).
- L2 → L3: crack IoU +0.004 (n.d.), inactive IoU −0.089 (hurts).

**Verdict, rule 2.** Val mean of (crack AP + inactive AP)/2 picks **L0**:

| Arm | Val score |
|---|---|
| L0 | 0.480 |
| L1 | 0.414 (seed 2 collapsed on val inactive: 0.324) |
| L2 | 0.396 |
| L3 | 0.296 |

So P7 ran on L0's model and loss.

**Verdict, rule 3** (computed literally as AP on pooled val+test pixels):
- L0@100% = 0.5591, L0@10% = 0.5601, so the headroom is **−0.001 < 0.02**.
- Experiment 2 (P7) is therefore a pilot.

**Disclosed correction and a source conflict.** An interim figure of +0.026 averaged the per-split APs, which is not "pooled". The README replaces it with the pooled −0.001. Val has 12k inactive GT pixels against test's 92k, so the split mean over-weights val.

Note that `results/p6/p6_rules.txt` still prints the interim numbers ("headroom (split-mean): +0.0256", "n-weighted +0.0270"). The README's pooled −0.001 is the one the later protocols (P7, P8) use.

**Exploratory findings** (not covered by the locked rules; `results/p6/README.md`):

1. **AP is not comparable across these loss and encoder changes.** The ImageNet and Dice arms push many GT pixels to softmax < 0.001, where AP cannot rank them. Bin-0 share (test, mean over seeds, `hist_analysis.txt`):

   | Arm | GT crack px < 0.001 | GT inactive px < 0.001 |
   |---|---|---|
   | L0 10% | 3% | 19% |
   | L1 10% | 5% | 19% |
   | L2 10% | 19% | 41% |
   | L3 10% | 42% | 65% |
   | L3 100% | 20% | 40% |

   So rule 1's "hurts" for L2 and L3 is partly a calibration (ranking) effect. At argmax:
   - crack IoU rises L1 → L2 and is flat L2 → L3;
   - crack relaxed precision@2 rises 0.80 → 0.84 → 0.91.

   The inactive drop is real at every operating point: IoU 0.473 → 0.383 → 0.294.

   This is why P8 onward switched the primary metrics to argmax IoU and relF1@2.

2. **The label-efficiency gap depends on the recipe:**

   | Recipe, 10% → 100% labels | pooled AP | crack IoU | inactive IoU |
   |---|---|---|---|
   | L0 | −0.001 | +0.017 (n.d.) | −0.048 |
   | L3 | +0.159 | +0.075 | +0.135 |

   L0 does not convert extra labels into better test scores; L3 does. SSL can only close a gap that exists, so L3 is the base with room. This motivated P8.

3. **Inactive pixels sit in a few cells** (revised labels; `data/escdd_masks/{test,val}`):

   | Split | Cells with any inactive | Share held by the top 3 | Largest single cell |
   |---|---|---|---|
   | test | 16 of 50 | 59% | BMRK_00073_cell0253, 23% |
   | val | 6 of 54 | 89% | CFVS_00143_r4_c3, 35% |

   Crack, by contrast, appears in 48 of 50 test cells, and the largest single cell holds 12%. Any dataset-level inactive metric is decided by about 3 cells.

   An apparent "inactive puzzle" (L1 at 10% had the best inactive IoU of any arm, 0.473, above L3 at 100%, 0.429) is resolved by this: it flips sign without the top-3 cells.

**Robustness** (image bootstrap over test cells, 2,000 resamples, plus leave-top-3-out; `per_image_test.txt`):

| Comparison (test IoU) | Δ, all cells | Δ without top-3 | 95% CI |
|---|---|---|---|
| L1 − L0, crack | +0.048 | +0.052 | [+0.003, +0.097] |
| L1 − L0, inactive | +0.034 | −0.078 | [−0.082, +0.136] |
| L2 − L1, inactive | −0.089 | −0.005 | [−0.152, +0.002] |
| L3 − L2, inactive | −0.089 | −0.019 | [−0.158, +0.006] |
| L3 100% − L3 10%, crack | +0.075 | +0.124 | [+0.029, +0.128] |
| L3 100% − L3 10%, inactive | +0.135 | +0.112 | [+0.049, +0.205] |
| L3 100% − L1 10%, crack | +0.103 | +0.105 | [+0.074, +0.129] |
| L3 100% − L1 10%, inactive | −0.044 | +0.088 | [−0.125, +0.106] |

- Crack differences are robust to the cell sample.
- Most inactive differences are decided by about 3 cells.
- L3's inactive gain from more labels holds on test without the top 3 (+0.112). On val without its top 3 it is +0.000; val has only 6 inactive cells, so val inactive cannot settle anything.
- The seed-based rule stands as defined, but its inactive verdicts measure training noise on a fixed set of cells. From P7 on, every inactive result is reported with this check.

**E1 per-cell metrics (added 11 Oct, descriptive;** `results/e1/e1_tables_p6_p10.md`**).**

Test set:

| Contrast | crack tolF1 | crack IoU (pooled) | inactive cell IoU | inactive IoU (pooled) |
|---|---|---|---|---|
| L1 − L0 | −0.017 [−0.046, +0.008] | +0.048 [+0.003, +0.097] | −0.016 [−0.099, +0.067] | +0.034 [−0.082, +0.136] |
| L3 − L2 | −0.001 [−0.023, +0.021] | +0.004 [−0.020, +0.026] | −0.064 [−0.109, −0.022] | −0.089 [−0.158, +0.006] |
| L3 100% − L3 10% | +0.105 [+0.046, +0.164] | +0.075 [+0.029, +0.128] | +0.101 [+0.002, +0.215] | +0.135 [+0.049, +0.205] |

On the 106-cell unseen-module extension, L3 at 100% falls from test crack IoU 0.471 to 0.152 (`results/e1/README.md`).

**Reading:**
- Label-safe augmentation is the one ladder step that clearly helps on the old metric.
- The ImageNet encoder and Dice change calibration (more saturated scores) more than segmentation for crack, and they cost inactive.
- The deciding finding for the SSL plan: only L3 turns more labels into better scores (crack IoU 0.396 → 0.471 from 10% to 100%). L3 is therefore where SSL has something to close.
- The supervised label curve continued in P10 and P16: 5% and 50% points.

**Figures.** `fig_ladder.png`, `fig_label_scaling.png`, `fig_saturation.png`, `fig_overlays.png` in `results/p6/`.

**Caveats.** One split (seed 0), 3 seeds, 50 test images. AP uses 1,000 uniform bins (as all earlier work). The bin-0 tie effect is a property of the metric on these models, not a bug: the histogram AP reproduces the rescore JSON exactly.

**What it led to:**
- P7 on L0, as locked.
- P8 on L3, a disclosed post-hoc choice.
- L3 (`smp_unetpp` + `ce_dice` + label-safe, revised masks, 20,000 steps, batch 8) is the supervised reference "A" for every later SSL experiment.

---

## P7. Tolerant pseudo-labels on the L0 base (mid-term "Experiment 2", pilot)

**Question.** At 10% labels, does an unlabelled loss that routes rare classes (crack, inactive) to an offset-tolerant target beat:
- (a) a correct hard pseudo-label loss (FixMatch-style CE at confidence ≥ 0.95), and
- (b) the identical training with the unlabelled loss off?

(`protocols/P7_tolerant_pl_pilot.md`)

**Why it was run.** P5 measured that crack pseudo-labels hit the right crack but the wrong pixels. P7 was the first test of a loss built on that.

**Setup.**
- **Lock and code:** locked 10 Oct before any P7 run (commit `37985d6`). It depends on P6 only through P6 rule 2 (the val-selected base, which turned out to be L0: `unetpp`, weighted CE). Code commit `0367079` (adds label-safe SSL views, `tolerant_pl`, `rare_frac` logging).
- **Labels and pools:** revised masks; seed-0 split. Labelled = `labeled_10pct` (47 images), batch 8. Unlabelled = `unlabeled_10pct` (431 train images, labels hidden), batch 8.
- **Mean Teacher:**
  - EMA 0.999;
  - the teacher sees the weak view (normalise only);
  - the student sees the label-safe strong view: shared flips/90° rotations, brightness/contrast ±0.25 (p 0.8) and mild Gaussian noise (p 0.3), no blur;
  - **the labelled images take the same strong view** (this detail matters in P8 and P11);
  - consistency on unlabelled images only.
- **λ schedule:** 0 for 2,000 steps, linear ramp over 2,000 steps to λ_final = 1.0.
- **Training:** 20,000 steps; optimiser and schedule as P6; seeds 0 to 2; EMA teacher evaluated.
- **Runs:** 9 on cv02 (RTX A6000), 10 Oct 15:34 to 23:13 IST, all rc = 0.

| Arm | Unlabelled loss |
|---|---|
| A (reference, no new runs) | none: P6 L0 10%, plain supervised pipeline |
| B | `confidence_ce`, t_pos 0.95: hard pseudo-label CE, normalised by all unlabelled pixels |
| C (proposed) | `tolerant_pl`, t_pos 0.95, rare = {crack 14, inactive 11}, R = 2 px |
| D (loss-off control) | arm C with λ_final = 0; identical forward pass, augmentation and data streams |

How C routes each pixel (protocol):
- **Rare-class teacher argmax, confident or not:** −p_t[r] · log(max-pool over 5×5 of p_s[r]). The student gets credit for predicting the rare class anywhere within 2 px.
- **Confident head-class pixel outside a 2 px band around rare targets:** CE.
- **Everything else:** no loss.

**Locked rules** (primary: test crack AP and inactive AP, revised labels):
1. C helps if mean(C) − mean(D) on either primary is > 0.01 and > 2·√((sd_C² + sd_D²)/3). B vs D uses the same rule.
2. C beats B under the same rule for C − B. If C helps but does not beat B, the claim is "a correct pseudo-label loss helps", not "tolerance helps".
3. Width check: if C's gain comes with relaxed precision@2 falling by > 0.05 against D, flag possible fattening.
4. If P6 rule 3 found headroom < 0.02, all P7 outcomes are a pilot.

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p7/README.md`):

| Arm | crack AP | inactive AP | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 |
|---|---|---|---|---|---|---|
| A: L0 10%, supervised (P6) | 0.553±0.015 | 0.621±0.003 | 0.319±0.051 | 0.439±0.015 | 0.746±0.078 | 0.690±0.126 |
| D: Mean Teacher, loss off | 0.551±0.004 | 0.618±0.004 | 0.355±0.006 | 0.453±0.001 | 0.782±0.007 | 0.788±0.018 |
| B: hard PL (conf ≥ 0.95) | 0.527±0.004 | 0.521±0.015 | 0.359±0.003 | 0.381±0.022 | 0.768±0.007 | 0.848±0.005 |
| C: tolerant PL (proposed) | 0.551±0.001 | 0.585±0.005 | 0.363±0.004 | 0.437±0.007 | 0.790±0.003 | 0.819±0.006 |
| L0 100% (P6) | 0.545±0.003 | 0.612±0.006 | 0.337±0.004 | 0.391±0.008 | 0.782±0.008 | 0.744±0.010 |

**Verdict per rule** (thresholds from `results/p7/p7_rules.txt`):

| Contrast | crack AP | inactive AP | Verdict |
|---|---|---|---|
| C − D | +0.000 (thr 0.010, n.d.) | −0.032 (thr 0.010, worse) | C does not help |
| B − D | −0.024 (thr 0.010, worse) | −0.097 (thr 0.018, worse) | B does not help; it hurts both |
| C − B | +0.024 (thr 0.010, better) | +0.064 (thr 0.018, better) | C beats B |

- Width check: crack relP@2 C − D = +0.031. C predicts thinner cracks, not fatter.
- Rule 4: **pilot**. P6 rule 3 found no headroom on L0 (pooled AP −0.001).

**Robustness** (image bootstrap and leave-top-3-out, test IoU, `per_image_test.txt`):

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C − D, crack | +0.007 | +0.011 | [−0.001, +0.018] | 0.94 |
| C − D, inactive | −0.016 | +0.050 | [−0.063, +0.059] | 0.31 |
| B − D, inactive | −0.072 | +0.001 | [−0.135, +0.018] | 0.06 |
| C − B, inactive | +0.056 | +0.049 | [+0.022, +0.086] | 1.00 |
| D − A, crack | +0.036 | +0.035 | [−0.013, +0.085] | 0.75 |

The only robust contrast is C over B on inactive.

**Bin-0 share** (GT pixels scored < 0.001, test):

| Arm | crack | inactive |
|---|---|---|
| D | 0.061 | 0.205 |
| C | 0.088 | 0.284 |
| B | 0.129 | 0.354 |

The order is D < C < B for both classes.

**E1 per-cell (descriptive;** `results/e1/e1_tables_p6_p10.md`**):**
- Test, C − D: crack tolF1 +0.020 [−0.002, +0.046]; inactive cell IoU −0.004 [−0.057, +0.059].
- Unseen-module extension, C − D: crack false alarm −0.099 [−0.169, −0.031] (fewer false alarms); inactive pooled IoU −0.016 [−0.039, −0.004]. These two are from the **first-pass** extension scoring (`e1_tables_p6_p10.md`, commit `f9ea897`), before the amendment that ignores release classes 25 to 28. The corrected `e1_ext_v2.md` has no P7 contrast; its arm means point the same way (false alarm C 0.554 vs D 0.676; inactive pooled IoU 0.132 vs 0.150).

**Reading:**
- On L0 at 10% labels, the unlabelled loss gives no measurable gain. Hard pseudo-labels hurt (mostly inactive); tolerant pseudo-labels are close to neutral.
- This is the expected outcome on a base with no label headroom.
- The one robust positive finding is about how to use pseudo-labels: routing rare classes through a tolerant target is less harmful than hard confidence thresholding (C − B inactive IoU +0.056, CI [+0.022, +0.086]).
- **Mechanism (plausible, not tested):** confirmation bias. Where the teacher misses a defect, a confident-background pseudo-label trains the student to be sure it is background. B applies that pressure everywhere; C exempts a 2-px band around rare targets.
- D − A (EMA teacher plus label-safe views, no unlabelled loss) is about +0.036 crack IoU, the same order as P6's L1 − L0 label-safe gain (+0.048). The unlabelled loss adds nothing on top.

**Caveats.** Pilot (no headroom). One split; 3 seeds; 50 test cells. Inactive is dominated by 3 test cells (59% of GT pixels). AP saturates.

**What it led to.** P8: the same four arms on the L3 base, which has headroom (`09_experiments_P8_P12_ssl_series.md`).

---

## Summary table: what each of P1 to P7 settled

| Exp | Settled | Status of the claim |
|---|---|---|
| P1 | No pipeline bug; augmentation and loss cap crack fitting | Locked rules (H2 met, H1 partial, H3/H4 refuted) |
| P2 | Old SemiCE Mean Teacher results are invalid; confident pseudo-labels starve rare classes | Locked rule fired |
| P3 | Revised labels move crack IoU +0.05 to +0.07 | Exploratory |
| P4 | ImageNet CNN features carry the signal; DINOv2 not for crack | Locked rules |
| P5 | Crack pseudo-labels are offset by 1 to 2 px; winner pseudo-labels unusable in Ω3 | Locked rules (1, 2 fire; 3 not met) |
| P6 | Label-safe aug helps; L3 is the only recipe with label headroom; L0 has none | Locked rules plus robust exploratory |
| P7 | No SSL gain on L0 (pilot); tolerant less harmful than hard pseudo-labels on inactive | Pilot |

## Related docs
- `09_experiments_P8_P12_ssl_series.md`: the next five experiments, on the L3 base.
- `10_experiments_P13_P16_E1.md`: P13 to P16 and the E1 evaluation.
- `07_methodology_rules_and_statistics.md`: rule 1, the bootstrap and leave-top-3-out in detail.
- `04_glossary_and_naming.md`: metric and arm-name definitions.
- `03_datasets_and_splits.md`: label versions, splits, inactive concentration.
- `05_literature_and_baselines.md`: ALHVR, FixMatch, Mean Teacher and related methods.
- `06_history_phase0_phase1.md`: the old-era results that P1 to P3 re-examined.
- `11_results_synthesis_and_claims.md`, `12_decisions_log.md`, `13_problems_pitfalls_open_issues.md`.
