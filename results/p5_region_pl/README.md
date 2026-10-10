# P5 result: rare-class pseudo-label quality inside ALHVR regions (CONFIRMATORY against `protocols/P5_region_pseudolabel_precision.md`)

Run: 10 Oct 2026, about 10:00 IST, gaint, `scripts_gaint/p5_region_pl_precision.py`, read-only.
Models: `alhvr_20pct_s0` and `s1`, final weights, networks A and B.
Data: 378 unlabelled train images (seed-0 20% split, those with E-SCDD masks), pooled over both runs.
Thresholds: global γ ≈ 0.94 (per batch, as trained). Per-class γ_c: crack 0.70, inactive 0.77, background 0.95.

## Crack (14), revised labels (old labels in brackets for strict P)

| Rule | Region | Share of GT crack | Strict P | Relaxed P (2 px) | Recall |
|---|---|---|---|---|---|
| global γ | r1 (both sure) | 0.18 | 0.53 (0.45) | 0.90 | 0.69 |
| global γ | r2 (one sure) | 0.10 | 0.42 (0.36) | 0.76–0.81 | 0.63–0.69 |
| global γ | **r3 (both unsure)** | **0.72** | **0.27** (0.23) | **0.64** | 0.62 |
| per-class γ_c | r1 | 0.54 | 0.42 (0.36) | 0.83 | 0.84 |
| per-class γ_c | r2 | 0.14 | 0.22 (0.19) | 0.53–0.57 | 0.66–0.69 |
| per-class γ_c | **r3** | **0.32** | **0.17** (0.14) | **0.48** | **0.29** |
| reference: ensemble prob ≥ 0.95 | – | recall of all GT crack 0.08 | 0.59 (0.50) | 0.96 | – |

## Inactive (11), revised labels (differences from old labels are ≤ 0.01)

- Global γ: r3 holds 0.54 of GT inactive; P 0.53, recall 0.51. r1: P 0.86.
- Per-class γ_c: r3 holds 0.28; P 0.43, recall 0.37.
- Reference rule (≥ 0.95): P 0.88, recall 0.26.

## Locked decision rules

| Rule | Measured | Verdict |
|---|---|---|
| 1. Crack: Ω3 relaxed precision under γ_c (revised) < 0.5 → no hard pseudo-labels for crack in Ω3 | 0.48 (recall 0.29) | **Fires (borderline).** Use labelled anchoring or tolerance-aware consistency in Ω3, not winner pseudo-labels |
| 2. Inactive: Ω3 strict precision under γ_c < 0.5 → same | 0.43 | **Fires** |
| 3. γ_c must move ≥ 10 points of crack out of Ω3 at precision ≥ the global rule's | moves 40 points (0.72 → 0.32), but r1 precision falls (strict 0.53 → 0.42, relaxed 0.90 → 0.83) | **Not met.** Per-class thresholds trade Ω3 share for precision; they do not improve routing by themselves |

## Exploratory reading (not in the protocol)

- **Crack pseudo-labels point at the right crack but miss the pixels.**
  - In Ω3 under global γ: strict precision 0.27 vs relaxed 0.64.
  - At the confident end: 0.59 vs 0.96.
- So a target that tolerates 1–2 px offsets would keep most of the signal that a pixel-exact pseudo-label throws away. That is a concrete, measured motivation for combining row 1 (tolerance-aware) with row 2 (routing).
- The confident rule (≥ 0.95) is precise but covers only 8% of GT crack. This is the rare-class starvation measured in P2 (crack is 0.024% of confident pixels).
- **Caveats:**
  - eval-mode BatchNorm;
  - the unlabelled loss never reached full weight in these runs, so A and B are close to supervised models;
  - one labelled split; two runs.
