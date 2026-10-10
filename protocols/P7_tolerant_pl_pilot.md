# P7 protocol (Experiment 2 for the mid-term): pilot of rarity-routed, offset-tolerant pseudo-labels

Locked 10 Oct 2026, before any P7 run. It depends on P6 only through P6 rule 2, the base recipe selected on val.

## Question
At 10% labels, does an unlabelled loss that routes rare classes (crack, inactive) to an offset-tolerant target beat:
- (a) a correct hard pseudo-label loss (FixMatch-style CE at confidence ≥ 0.95), and
- (b) the identical training with the unlabelled loss off?

## Motivation (measured; P5)
Teacher crack pseudo-labels hit the right crack but the wrong pixels:
- doubly-unsure region: strict precision 0.27 vs 0.64 within 2 px;
- confidence ≥ 0.95: 0.59 vs 0.96, and the threshold keeps only 8% of GT crack.

## Fixed for all arms
- **Base recipe:** model, supervised loss and mask set of the P6 rule-2 arm (expected `smp_unetpp` + `ce_dice`, but whichever val selects).
- **Labels:** revised masks (`data.mask_subdir=labeled/masks_escdd`).
- **Data:** seed-0 split. Labelled = `labeled_10pct` (47 images), batch 8. Unlabelled = `unlabeled_10pct` (431 train images, labels hidden), batch 8.
- **Mean Teacher:**
  - EMA 0.999; the teacher sees the weak view (normalise only).
  - The student sees the label-safe strong view: shared flips/90° rotations, then brightness/contrast ±0.25 (p 0.8) + mild Gaussian noise (p 0.3), no blur. The labelled images take the same strong view.
  - Consistency on unlabelled images only.
  - λ: 0 for 2,000 steps, linear ramp over 2,000 steps to λ_final = 1.0.
- **Training:** 20,000 steps, optimiser and schedule as P6. The evaluated model is the trainer's default (identical for all arms).
- Training seeds 0, 1, 2. Hardware: cv02 A6000, at most 3 runs per GPU. Code: one commit, recorded in `REVISION`.

## Arms

| Arm | Unlabelled loss |
|---|---|
| A (reference, no new runs) | none: P6 rule-2 arm, pure supervised pipeline |
| B | `confidence_ce`, t_pos 0.95: hard pseudo-label CE, normalised by all unlabelled pixels |
| C (proposed, minimal) | `tolerant_pl`, t_pos 0.95, rare = {crack 14, inactive 11}, R = 2 px (`src/losses/tolerant_pl.py`) |
| D (loss-off control) | arm C with λ_final = 0; identical forward pass, augmentation and streams |

9 new runs.

**How C routes each pixel:**
- **Rare-class teacher argmax, confident or not:** −p_t[r] · log(max-pool over 5×5 of p_s[r]).
- **Confident head-class pixel outside a 2 px band around rare targets:** CE.
- **Everything else:** no loss.

## Evaluation
As P6: `scripts/rescore_label_versions.py` on final weights.
- **Primary:** test crack AP and inactive AP, revised labels.
- **Secondary:** val; IoU; relaxed F1@2 with relaxed precision@2; old labels.
- **Logged:** the trainer's pseudo-label class shares.

## Decision rules
1. **C helps** if mean(C) − mean(D) on test crack AP or inactive AP is > 0.01 **and** > 2 × √((sd_C² + sd_D²)/3). B vs D uses the same rule.
2. **C beats B** under the same rule for C − B. If C helps but does not beat B, the claim reduces to "a correct pseudo-label loss helps", not "tolerance helps".
3. **Width check:** if C's gain comes with relaxed precision@2 falling by > 0.05 against D, flag it as possible fattening.
4. **Underpowered case:** if P6 rule 3 found SSL headroom < 0.02, all P7 outcomes are reported as a pilot regardless of rules 1–2.

## Not claimed
- The full ALHVR-style two-network routing (further work).
- Results beyond this split and dataset.
- Any tuning of R, t_pos or λ.
