# P5 protocol: are rare-class pseudo-labels usable inside ALHVR's regions, with global vs per-class thresholds?

Locked 10 Oct 2026, before running. Decides direction row 2 in `to_human/directions_2026-10-10.md`. Offline, read-only, no training.

## Setup
- **Models:** `alhvr_20pct_s0` and `alhvr_20pct_s1`, final `latest.pth`, networks A and B.
  - Eval mode (BatchNorm running statistics); this deviates from training, where BN used batch statistics.
  - Main and perturbed pass via `forward_dual` (random feature dropout or noise; Python `random` seeded 0).
  - Caveat: the unlabelled loss was ineffective in these runs (weight never reached full strength), so A and B are close to two supervised models. Early in a real ALHVR run, teacher quality would be lower.
- **Data:** seed-0 `unlabeled_20pct` stems (383 train images), evaluation transform, batch 4 (as in training).
  - Labels: the hidden 20211104 masks ("old") and the E-SCDD revised masks ("new"), for stems present in both.

## Region rules
- **Global threshold (as trained):** γ = mean of the lowest 80% of (con_a2 + con_b2)/2 over each batch.
  - r3 = both below γ; r2a = A ≤ γ < B; r2b = B ≤ γ < A; r1 = the rest.
- **Per-class threshold:** γ_c = mean of the lowest 80% of (con_a2 + con_b2)/2 over all unlabelled pixels whose main-pass ensemble argmax is c (dataset-level).
  - Network X counts as sure if conX2 > γ_{argmax of X}; regions are built as above from sure_A and sure_B.
- **Targets (ALHVR):**
  - r2a: pl_b;
  - r2b: pl_a;
  - r3: the winner's label (higher main-pass confidence);
  - r1: the agreed label (reference only; ALHVR puts no loss there).
- **Reference rule:** standard pseudo-label, ensemble mean probability max ≥ 0.95.

## Measures (crack 14, inactive 11; per region, per label version, pooled over images and both runs)
- GT share: the fraction of GT-c pixels that fall in the region.
- Precision of target c: strict, and for crack also relaxed (target pixel within 2 px of GT crack).
- Recall: the share of the region's GT-c pixels whose target is c.

## Decision rules
1. **Crack.** If relaxed 2-px precision of crack targets in Ω3 under per-class γ_c (revised labels) is below 0.5, hard pseudo-labels for crack in Ω3 are unusable. The method should then use labelled anchoring or tolerance-aware consistency in Ω3, not winner pseudo-labels.
   - If precision ≥ 0.5 and recall ≥ 0.5, per-class routing with pseudo-labels is viable.
2. **Inactive.** The same rule with strict precision.
3. **Per-class thresholds.** If γ_c does not move ≥ 10 points of GT-crack share out of Ω3 (into r1/r2), at precision ≥ the global rule's, per-class thresholds do not help routing for crack.
