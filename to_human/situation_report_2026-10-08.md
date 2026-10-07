# Situation report: training methodology for EL defect segmentation

Date: 8 Oct 2026, 00:30 IST. Scope: thesis part 1 (training methodology). Nothing new has been trained; this report rests on
code reading, the papers, a first-hand look at the data, and existing results. Tags: **measured** (a number in a file),
**inferred** (reasoned from measurements), **open** (not yet known).

Sources behind every claim:
- `analysis/alhvr_audit.md`: ALHVR port against the reference, plus the shared SSL loop
- `analysis/papers_metrics.md`: each paper's metric, recipe and numbers against ours
- `data_analysis/benchmark_el_report.md`: first-hand BenchmarkEL analysis, with figures in `data_analysis/figs/`
- `literature/survey.md`, `literature/reading_list.md`: 69 verified sources
- `protocols/P1_overfit_check.md`, `protocols/P2_semice_gradient_probe.md`: locked, not yet run

---

## 0. Bottom line

1. **On BenchmarkEL, strict crack IoU is already at the level where label noise dominates.**
   - **Agreement between annotations (measured):** one image appears twice in train, pixel-identical, with two independent masks. Their crack IoU is 0.257 (tolerance F1 0.82 at 2 px). A second pair gives 0.21, but its cracks are tiny.
   - **What a perfect mask scores (measured):** shifted by 1 px, 0.47–0.56.
   - **Our models (measured):** 0.27–0.35 on test.
   - **So (inferred):** strict-IoU differences of ±0.03 between methods cannot be interpreted for crack.
2. **"Crack can't be fitted on its own training images" is mostly explained by the labels and the loss (inferred; P1 will test it).**
   - Labels are a median 1.75 px wide, on a visible line about 4 px wide.
   - They sit within 1 px of the darkest pixel only 48% of the time.
   - They are dotted along continuous cracks in 22 images.
   - The class weights make the loss prefer crack whenever p(crack) > 0.05–0.06.
   - A model that covers the visible line gets exactly the measured profile: precision about 0.33, recall about 0.95.
3. **Neither SSL method has actually been tested (measured from the code).**
   - **ALHVR:** its unlabelled loss is close to zero for most of training under our learning-rate schedule.
   - **Mean Teacher:** uses a nonstandard consistency loss whose "confident" sets are thresholds on raw logits (≈ 0.001 for crack), with mild perturbation (CutMix exists but is never called).
   - "Unlabelled losses have no effect" is therefore not a finding.
4. **Inactive is the opposite problem.**
   - Its labels are consistent (duplicate pair: tolerance F1 0.92) and robust to jitter (1 px shift: 0.89–0.94).
   - It is memorised on train but generalises poorly, and it has a real label effect on unseen train images (0.34 at 10% → 0.46 at 20%).
   - The 50-image test set hides that effect: its inactive pixels come from few images.
   - So inactive is where a training method has measurable room on this dataset.
5. **The field's evaluation is weak in ways that matter.**
   - Test sets are hand-picked or reused for validation.
   - Metric conventions drop background or take per-image medians.
   - Test images appear in training lists.
   - Baselines are under-trained, results are single-run, and no thin-structure metric is used.
   - Our "reproduction gaps" are mostly these conventions; under Pratt's own rule there is no gap.

---

## 1. What the task really is (BenchmarkEL `dataset_20211104`)

| Fact | Value | Tag |
|---|---|---|
| Classes | 24, one label per pixel; background + padding 86.5% of train pixels | measured |
| Crack share of pixels | 0.19% (train) | measured |
| Crack label width | median 1.75 px (IQR 1.25–2.5); BMRK and SDLE about 3 px, others 1.5–1.75 px. The "2–3 px" in the handoff is wrong for most sources | measured |
| Visible crack width | median 4.0 px at half depth; wider than its label by ≥ 1 px at 77% of points | measured |
| Label position | within ±1 px of the darkest pixel 48% of the time, > 2 px away 36% (random background: 11% / 79%). ARTS best (75% within 1 px), BMRK worst (38%) | measured |
| Dotted labels along continuous cracks | 14 train, 3 val, 5 test images | measured |
| Visible crack left unlabelled | one clear case (`train/CSIR_00094_r16_c5`); the rate cannot be estimated automatically | visual |
| Very faint cracks | 7% of crack components are < 2% darker than their surroundings (CSIR 16%) | measured |
| Crack labels also trace the boundaries of inactive areas | visible in `figs/duplicate_pairs_masks.png` | visual |
| Inactive | always comes with a crack label; blob-shaped; labels consistent | measured |
| Test set | all 50 images contain crack; test cracks are darker (relative darkness 0.187 vs 0.140); 24/50 come from modules in train; one train/test cell is the same cell with different masks | measured |

Interpretation: crack is a 1–2 px line annotation of a roughly 4 px visible line, placed with about ±1 px jitter, sometimes dotted,
sometimes merged with the boundary of an inactive area. Any loss or metric that treats the label as pixel-exact is fighting the annotation.

## 2. What the metric can and cannot see

| Perfect mask, perturbed | Crack IoU (dataset-level) | Inactive IoU |
|---|---|---|
| shifted 1 px (horizontal or vertical) | 0.47–0.56 | 0.89–0.94 |
| shifted 1 px diagonally | 0.36–0.43 | |
| dilated by 1 px | 0.41–0.46 | |
| same image, second annotation (n = 1 solid pair) | 0.257 | |
| per-image median (Pratt's convention), 1 px shift | 0.12 | |

Consequences:
- Strict crack IoU mostly measures label jitter. It can still rank grossly different models, but not fine method differences.
- Tolerance metrics fix the jitter but reward wider predictions ("What's Cracking?" §VI-B3), and over-prediction is exactly
  our failure. A defensible crack report needs **tolerance F1 at 1–2 px together with relaxed precision, a skeleton-based score
  (clDice) and threshold-free AP**.
- The real agreement between annotations should be estimated on more than one pair before it is quoted (open).

## 3. What our experiments actually tested

| Arm | What it really did | Tag |
|---|---|---|
| Supervised, weighted CE | crack weighted 15–19× background, so crack is predicted once p > 0.05–0.06. Crack and inactive each get only about 2% of the weighted loss; background and structural classes 80–88% (padding alone 17–25%). The zero-weight and capped classes change with the label fraction, so every fraction trains at a different operating point | measured |
| ALHVR | λ reaches 0.1 only at the last step while the learning rate decays to 0. Weighted by learning rate, λ is 2.5× weaker than the reference's. Elementwise sharpening gives near-zero targets with 24 classes where the winner's max-prob < 0.5; the prototype CE has a floor of 1.41. No wiring bug | measured (code + logs) |
| Mean Teacher (SemiCE) | per-class binary CE on softmax logits; positive if teacher logit > 0.5·freq (≈ 0.001 for crack), negative if < −0.5; averaged over all active (pixel, class) pairs. The student's view is mild (blur/brightness/noise only; CutMix never called; 29% of student/teacher pairs identical) | measured (code); effect size open (P2) |
| Loss-off controls | valid: same forward pass | measured |
| "4 + 4" inactive gain | appears with the loss on or off. BN running statistics are ruled out; BN statistics during training remain a candidate (published precedent: Yuan et al., ICCV 2021) | measured / open |

Also affected (measured from the configs): the external-pool MT queue on gaint (armed, `consistency: semi_ce`) and the UCF MT runs now on
cv02 (`ucf_mt_sl5_s0_cv02/config_used.yaml`: `consistency: semi_ce`, data-driven thresholds; at step 80,250 `loss_con` = 0.009 against
`loss_sup` = 0.027). Their MT-against-loss-off comparison tests this SemiCE, not Mean Teacher.

## 4. Our reproductions against the papers (detail in `analysis/papers_metrics.md`)

- **Pratt 2023:** IoU per image, then the median, with no background. Under the rule that fits their table, ours score 0.28–0.30 against their best of 0.28. No gap.
- **Fioresi 2022:** no IoU table, only P/R/F1. Converted to F1, we match or beat them (crack .81/.81, contact .65/.58, interconnect .50/.33, corrosion .80/.78).
  - Their abstract does state 57.3% mIoU. It is likely a 5-class mean including background (correcting my earlier claim).
- **PV-S3:** never predicts background, and its metric drops background pixels. Its released splits put test images in training. Its baseline is under-trained, and its code does not reproduce its paper.
- **SA-UNet++:** has no EL experiments. Our null result does not contradict it.

## 5. Where the field is (detail in `literature/survey.md`)

- **SSL on EL segmentation is almost unstudied.**
  - The one controlled study (Torpey, Pratt & Klein 2024, fully labelled): COCO pretraining 0.544 ≈ CCT 0.550 ≈ ImageNet-SimCLR. In-domain SimCLR 0.517; U2PL 0.448, which is below random init (0.486).
  - No EL paper reports a label-budget curve with step-matched baselines and loss-off controls.
- **Rare-class mechanisms with real evidence:**
  - rare-class-biased sampling and mixing (AEL: tail classes +10 to +22 IoU);
  - pseudo-label distribution alignment (DARS);
  - class weights driven by pseudo-label statistics (DHC: Synapse 33.6 → 48.6 Dice).
- **The gap for an ALHVR-inspired method:** no published method combines ALHVR-style routing of low-confidence regions with class awareness.
  **BUR** argues the opposite routing (labelled loss on uncertain regions, unlabelled loss only on confident ones) and is the rival hypothesis to test against.
- **Thin structures:** Skeleton Recall is the only thin-structure loss built for multiple classes. No SSL objective that is aware of skeletons or tolerances was found.

## 6. Questions for the training-methodology part (to discuss; nothing decided)

1. **Measurement first.** How should crack be scored, given about 0.26 agreement between annotations? Proposed: tolerance F1 at 1/2 px,
   relaxed precision, clDice, AP, plus strict IoU for comparison with the literature; inactive by IoU and AP. Re-score every existing
   checkpoint before drawing any further conclusion.
2. **Is the crack ceiling label geometry?** P1 tests it. If yes, a loss that tolerates 1–2 px misplacement may matter more for crack than any SSL.
3. **Does a correct SSL objective help at low label budgets?** Standard confidence-thresholded CE with real strong perturbation, and ALHVR with a fair
   schedule, against loss-off controls, step-matched baselines, several labelled splits, and an evaluation set larger than 50 images.
4. **Rare-class routing.** Within an ALHVR-like framework, should low-confidence regions be handled per class (γ_c per class,
   class-balanced Ω3 sampling, prototypes from labelled ground truth in a memory bank)? And how does that compare with BUR's opposite routing?
5. **Which dataset carries which claim.** UCF-EL has a clean label gap (0.54 → 0.23 from 100% to 1%) and wider cracks (median 9 px).
   It may be the better test bed for SSL. BenchmarkEL may be better for the annotation-noise and metric story. The same data analysis has not been done on UCF-EL yet.
6. **Crack against inactive.** One method, or class-specific treatment? Their failure modes are opposite: label-noise-limited
   against generalisation-limited.

## 7. Next steps, all waiting on the user

| Step | Needs |
|---|---|
| Hold the gaint external-pool queue (it starts about 01:08) | the user runs the hold command (blocked for me) |
| P2: SemiCE gradient probe on `mt_20pct_s0` | permission for compute on gaint |
| P1: overfit check, 5 arms, about 1 h | permission for compute on gaint |
| Re-score existing checkpoints with tolerance metrics | permission (reads checkpoints on gaint) |
| UCF-EL data analysis, same as BenchmarkEL | local |
| Reading: the top 10 in `literature/reading_list.md` | the user |

## 8. What I am not sure of

- The annotation-agreement figure rests on one solid duplicate pair.
- The P1 hypotheses are not separated yet; the explanation in 0.2 is inferred.
- How much of SemiCE's gradient is useless is not measured (P2).
- Whether the "4 + 4" inactive gain comes from BN statistics during training is untested.
- Whether UCF-EL's labels have the same jitter is unknown.
