# P18 (EXPLORATORY): the BsM recipe at 10% and 20% labels, L3 base. Results

Protocol: `protocols/P18_bsm_label_fraction.md`, locked 13 Oct 17:31 IST (`a698ec8`) before any run. **Exploratory:** the BsM recipe was picked after seeing P13's test results. The rule-1 arithmetic below is reported as arithmetic. It is not a confirmatory verdict, and no claim rests on P18 alone.

**Runs**
- cv02 (RTX A6000), code `bac5264` (`el_p13`), no code change. Options are BsM5's (`scripts_cv02/p18_queue.spec`), with `data.labeled_fraction` and the seed changed.
- BsM20 `p18_BsM_20pct_s0..4` (GPUs 0–4), BsM10 `p18_BsM_10pct_s0..2` (GPUs 5–7). 13 Oct 17:31–19:40 IST. All 16 train/rescore steps have rc = 0.
- 20,000 steps, batch 8 + 8, EMA teacher's final weights, re-scored on revised labels.
- References (cv02): A20 = `p6_L3_20pct` s0–2 + `p16_A_20pct` s3–4; A10 = `p6_L3_10pct` s0–2; S20 = `p16_S_20pct` s0–4 (Cs recipe: tolerant PL, no CutMix).
- **Pipeline check: passed.** Up to step 2,000 (λ = 0), every seed's logged losses equal the matching supervised run's: `p16_A_20pct` s3–4 (same commit) and P6 (`824fab0`) for the other seeds.

**Files**
- `raw/`: re-score JSONs, `launch.log`.
- `p18_rules.txt`: rule-1 arithmetic, gap closed, width check, histograms.
- `per_image_test.txt`: image bootstrap, top-3, source split, without the noisy cell.
- `p18_curve.txt`: pooled metrics from E1 counts, rule-1 arithmetic with and without `CSIR_00070_r8_c4`, noisy-cell FP per seed.
- `fig_p18_curve.png`: the label-fraction curve (supervised, Cs recipe, BsM recipe); bottom row without the noisy cell.
- `fig_p18_bars.png`, `per_image.json`, `hist_revised.npz`.
- E1: `../e1/e1_p18.md`.
- Reproduce with `bash scripts/post_ssl.sh p18 <gpu> 8`.

## Results
Test cells, revised labels, mean ± sd over seeds.

| Arm | Seeds | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP | val crack IoU | val inactive IoU |
|---|---|---|---|---|---|---|---|---|---|
| A10: supervised 10% (P6) | 0–2 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 | 0.318±0.010 | 0.300±0.044 |
| **BsM10** | 0–2 | 0.408±0.011 | 0.426±0.021 | 0.827±0.014 | 0.913±0.019 | 0.452±0.010 | 0.484±0.034 | 0.327±0.007 | 0.359±0.009 |
| A20: supervised 20% (P6 + P16) | 0–4 | 0.398±0.006 | 0.361±0.037 | 0.822±0.010 | 0.942±0.006 | 0.434±0.007 | 0.352±0.040 | 0.317±0.003 | 0.452±0.021 |
| S20: Cs recipe 20% (P16) | 0–4 | 0.358±0.060 | 0.390±0.026 | 0.752±0.096 | 0.789±0.187 | 0.402±0.062 | 0.396±0.028 | 0.323±0.005 | 0.385±0.047 |
| **BsM20** | 0–4 | 0.392±0.042 | 0.422±0.024 | 0.804±0.064 | 0.870±0.136 | 0.453±0.046 | 0.443±0.033 | 0.333±0.010 | 0.374±0.027 |
| L3 100% (P6) | 0–2 | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 | 0.423±0.003 | 0.397±0.023 |

### Per seed
| Run | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP | val crack | val inactive | crack FP px on `CSIR_00070_r8_c4` |
|---|---|---|---|---|---|---|---|---|---|
| BsM10 s0 | 0.418 | 0.440 | 0.838 | 0.932 | 0.459 | 0.503 | 0.322 | 0.368 | 0 |
| BsM10 s1 | 0.397 | 0.403 | 0.811 | 0.893 | 0.440 | 0.444 | 0.324 | 0.350 | 3,752 |
| BsM10 s2 | 0.410 | 0.437 | 0.832 | 0.915 | 0.457 | 0.504 | 0.335 | 0.361 | 753 |
| BsM20 s0 | 0.420 | 0.407 | 0.838 | 0.939 | 0.483 | 0.437 | 0.334 | 0.389 | 0 |
| BsM20 s1 | 0.397 | 0.400 | 0.825 | 0.918 | 0.457 | 0.410 | 0.322 | 0.386 | 786 |
| BsM20 s2 | 0.403 | 0.431 | 0.832 | 0.935 | 0.472 | 0.450 | 0.324 | 0.336 | 34 |
| BsM20 s3 | 0.422 | 0.458 | 0.838 | 0.933 | 0.480 | 0.496 | 0.344 | 0.355 | 164 |
| **BsM20 s4** | **0.320** | 0.412 | **0.690** | **0.628** | 0.374 | 0.424 | 0.340 | 0.403 | **34,265** |

**BsM20 s4 fails on the noisy cell.** It predicts 34,265 crack pixels on `CSIR_00070_r8_c4` (the other BsM20 seeds: 0–786). This seed alone drives BsM20's crack sd (0.042) and the width flag below.

The same failure hits supervised and SSL seeds alike from 20% labels up. Runs with > 30,000 crack FP px on that cell:

| Arm | Runs |
|---|---|
| A50 | s2 (80,060) |
| A100 | `p16_A_100pct` s3 (75,217) |
| S20 | s2 (39,994), s4 (38,928) |
| BsM20 | s4 (34,265) |
| Below 20% labels (A5c, BsM5, CsM5, A10, BsM10) | none (max 4,481, CsM5 s0) |

## Rule-1 arithmetic (exploratory, P8 rule 1)
Each cell gives Δ, then the threshold in brackets.

**All 50 test cells (as scored):**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Arithmetic | relP@2 Δ |
|---|---|---|---|---|---|
| **BsM20 − A20** (5 v 5) | −0.006 (0.049) | **+0.060** (0.051) | −0.018 (0.075) | passes (inactive only) | −0.071, **width flag** |
| **BsM10 − A10** (3 v 3) | +0.012 (0.013) | **+0.132** (0.032) | +0.013 (0.017) | passes (inactive only) | +0.004 |
| BsM20 − S20 (5 v 5, two changes) | +0.034 (0.084) | +0.031 (0.040) | +0.053 (0.133) | n.d. | +0.081 |
| *BsM5 − A5c (P13 Am. 2, for the curve)* | +0.029 (0.016) | +0.107 (0.044) | +0.045 (0.023) | passes on all three | +0.015 |

**Without test cell `CSIR_00070_r8_c4` (post hoc, as P16 and P17):**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Arithmetic | relP@2 Δ |
|---|---|---|---|---|---|
| **BsM20 − A20** | +0.013 (0.014) | **+0.061** (0.052) | +0.012 (0.013) | passes (inactive only; crack just below) | −0.013, ok |
| **BsM10 − A10** | **+0.017** (0.010) | **+0.138** (0.033) | **+0.020** (0.010) | passes on all three | +0.022 |
| BsM20 − S20 | +0.010 (0.013) | +0.032 (0.041) | **+0.011** (0.010) | passes (relF1@2 only, by 0.001) | −0.010 |
| S20 − A20 (P16, for reference) | +0.002 (0.010) | +0.029 (0.054) | +0.000 (0.014) | n.d. | −0.003 |

Gap closed toward supervised 100%, as scored: inactive IoU 0.98 at 10% and 0.89 at 20%; crack IoU 0.16 at 10% and −0.08 at 20% (s4).

**Width check (as scored):** BsM20 − A20 crack relP@2 −0.071 is flagged (> 0.05). It is driven by s4: without the noisy cell it is −0.013.

## Robustness
Paired image bootstrap over the test cells (2,000 resamples); Δ without the top-3 cells; P(Δ > 0).

| Contrast | Class | All 50 cells: Δ [95% CI] (P) | Without top-3 | Without noisy cell: Δ [95% CI] (P) |
|---|---|---|---|---|
| BsM20 − A20 | crack | −0.006 [−0.032, +0.027] (0.47) | +0.011 | +0.013 [−0.002, +0.034] (0.95) |
| BsM20 − A20 | inactive | +0.060 [−0.018, +0.119] (0.93) | +0.042 | +0.061 [−0.023, +0.123] (0.93) |
| BsM10 − A10 | crack | +0.012 [−0.002, +0.023] (0.96) | +0.013 | +0.017 [+0.009, +0.024] (1.00) |
| BsM10 − A10 | inactive | **+0.132 [+0.043, +0.235]** (1.00) | +0.099 | +0.138 [+0.046, +0.243] (1.00) |
| BsM20 − S20 | crack | **+0.034 [+0.005, +0.061]** (1.00) | +0.043 | +0.010 [+0.003, +0.021] (1.00) |
| BsM20 − S20 | inactive | +0.031 [−0.002, +0.066] (0.96) | +0.024 | +0.032 [−0.005, +0.068] (0.96) |

- **Inactive at 20%:** the cell bootstrap CI includes 0 ([−0.018, +0.119]), although the seed arithmetic crosses the threshold. Top-3 cells hold 59% of test inactive GT pixels.
- **Source split, crack:**
  - CFVS/BMRK/SDLE (29 cells): BsM20 − A20 +0.013 [−0.003, +0.038]; BsM10 − A10 +0.018 [+0.009, +0.025].
  - CSIR/ARTS (21 cells, includes the noisy cell): BsM20 − A20 −0.039 [−0.049, +0.013].

### E1 per-cell metrics (secondary, `../e1/e1_p18.md`)
| Contrast | Split | crack tolF1 | crack false alarm | inactive det F1 | inactive cell IoU | inactive area err (pp) |
|---|---|---|---|---|---|---|
| BsM20 − A20 | test | **+0.045 [+0.023, +0.068]** | 0 | +0.053 [−0.062, +0.220] | +0.031 [−0.025, +0.087] | −0.142 [−0.487, +0.141] |
| BsM10 − A10 | test | **+0.039 [+0.013, +0.067]** | 0 | **+0.079 [+0.012, +0.191]** | **+0.089 [+0.028, +0.160]** | **−0.147 [−0.265, −0.051]** |
| BsM20 − A20 | ext (106 cells) | **+0.065 [+0.039, +0.095]** | +0.062 [+0.018, +0.104] | **+0.507 [+0.152, +0.733]** | **+0.434 [+0.226, +0.622]** | +0.083 [−0.019, +0.211] |
| BsM10 − A10 | ext | **+0.048 [+0.016, +0.081]** | +0.063 [+0.017, +0.113] | **+0.407 [+0.074, +0.700]** | **+0.353 [+0.162, +0.518]** | +0.002 [−0.046, +0.050] |
| BsM20 − S20 | ext | **+0.057 [+0.025, +0.093]** | +0.016 [−0.022, +0.053] | +0.295 [−0.022, +0.604] | **+0.255 [+0.050, +0.459]** | +0.063 [−0.007, +0.148] |

- On the extension (unseen modules), BsM finds more of the inactive cells than supervised at both 10% and 20%. On crack it finds more length (tolF1), but flags false crack in more cells (false alarm +0.06).
- On test, crack tolF1 is above supervised at both fractions, even with s4.

### Collapse watch and histograms
- conf_frac at steps 4,000 / 20,000:
  - BsM10 s0–2: 0.843 / 0.940; 0.846 / 0.944; 0.839 / 0.944.
  - BsM20 s0–4: 0.819 / 0.900; 0.821 / 0.904; 0.823 / 0.903; 0.829 / 0.904; 0.833 / 0.903.
  - Both rise steadily, as BsM5 does (0.87 / 0.965). No sign of collapse.
- Bin-0 share (GT px scored < 0.001), crack / inactive: BsM10 0.357 / 0.462; BsM20 0.351 / 0.400.

## Reading (exploratory; kept apart from the arithmetic)
1. **Inactive:** the BsM recipe's inactive IoU gain over supervised does not vanish at 10% or 20% labels.
   - Gains: +0.132 at 10% and +0.060 at 20%.
   - Both clear the rule-1 threshold, with or without the noisy cell.
   - At 10% the cell bootstrap excludes 0. At 20% it does not.
   - BsM10's test inactive IoU (0.426) is close to supervised 100% (0.429, P6).
   - Two cautions: test inactive is concentrated in 3 cells, and val inactive disagrees at 20% (BsM20 0.374 vs A20 0.452).
2. **Crack:** at 10% and 20%, BsM's crack IoU and relF1@2 gains are small: +0.012 to +0.020, at or near the threshold.
   - As scored, BsM20's crack mean is pulled down by one seed (s4) that fails on the noisy cell.
   - Supervised seeds fail on that cell too at 50% and 100% (A50 s2, A100 s3), so the failure is not specific to SSL.
   - Without that cell, BsM10 clears the threshold on crack IoU and relF1@2. BsM20 falls just short on both (0.013 vs 0.014; 0.012 vs 0.013).
3. **P16's "no SSL gain from 20% up":**
   - At 20% it partly depends on the recipe. Without the noisy cell, BsM20 − A20 is +0.013 crack / +0.061 inactive, where S20 − A20 is +0.002 / +0.029.
   - BsM20 − S20 changes two things (hard vs tolerant PL, CutMix on vs off), so the difference cannot be attributed to either.
   - 50% and 100% were not tested with BsM.
4. **Unseen modules (extension):** the inactive detection gain is large for both fractions. On crack, the gain in found length (tolF1) comes with more cells flagged falsely.
5. **None of this changes a locked verdict.** P18 is exploratory: the recipe choice used P13's test results.

## Not claimed
- Any confirmatory verdict; BsM at 50% or 100%; tuning of λ, t_pos or CutMix; gaint replication; other split seeds.
- Which of BsM's two differences from Cs (hard PL, CutMix) matters at 20%.
- That the noisy-cell failure is caused or prevented by SSL.
