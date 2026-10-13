# P13: separate-BN forward and CutMix, Mean Teacher at 5% labels (23 cells), L3 base. Results

Protocol: `protocols/P13_cutmix_separate_bn.md`, locked before any run. Amendment 1: 5% only, no Ds5, no gaint arms, and A5c is the loss-off control.

**Runs**
- cv02 (RTX A6000): 13 runs, 11 Oct 13:30–21:04 IST. All 26 train/rescore steps have rc = 0. All are 20,000 steps; the EMA teacher's final weights are evaluated.
- Code: commit `bac5264`.
- A5c pools P12 `p12_A_5pct` s0–2 (`24590fb`) with P13 `p13_A_5pct` s3–4. The supervised path is identical in the two commits. The two halves agree: P12 − P13 seeds n.d. on all primaries.

**Files**
- `raw/`: re-score JSONs and `launch.log`.
- `p13_rules.txt`.
- `per_image_test.txt`: bootstrap and source split.
- `fig_p13_bars.png`.
- `per_image.json` and `hist_revised.npz`.
- E1: `../e1/e1_p13.md`.
- Reproduce with `bash scripts/post_ssl.sh p13 <gpu> 13`.

## Results
Test cells, revised labels, mean ± sd over seeds.

| Arm | Seeds | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| **A5c**: supervised 5% | 0–4 | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.892±0.016 | 0.287±0.007 | 0.253±0.041 |
| Cm5 (P12): tolerant PL, joint BN | 0–2 | 0.311±0.010 | 0.274±0.139 | 0.737±0.014 | 0.857±0.077 | 0.329±0.016 | 0.348±0.121 |
| **Cs5**: tolerant PL, separate BN | 0–2 | 0.308±0.007 | 0.359±0.042 | 0.737±0.008 | 0.878±0.035 | 0.312±0.011 | 0.388±0.052 |
| **CsM5**: Cs5 + CutMix | 0–4 | 0.317±0.011 | **0.370±0.026** | **0.752±0.016** | 0.874±0.036 | 0.329±0.014 | 0.420±0.028 |
| **BsM5**: hard PL (≥ 0.95), separate BN, CutMix | 0–2 | **0.340±0.004** | **0.366±0.007** | **0.771±0.008** | 0.903±0.017 | 0.373±0.010 | 0.433±0.013 |
| L3 10% (P6) | 0–2 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6) | 0–2 | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

### Per seed
| Run | test crack IoU | test inactive IoU | test crack relF1@2 | val crack IoU | val inactive IoU |
|---|---|---|---|---|---|
| A5c s0 (P12) | 0.311 | 0.279 | 0.733 | 0.283 | 0.122 |
| A5c s1 (P12) | 0.307 | 0.284 | 0.724 | 0.283 | 0.133 |
| A5c s2 (P12) | 0.297 | 0.251 | 0.707 | 0.274 | 0.073 |
| A5c s3 | 0.310 | 0.260 | 0.731 | 0.278 | 0.086 |
| A5c s4 | 0.292 | 0.192 | 0.702 | 0.273 | 0.118 |
| Cs5 s0 | 0.300 | 0.355 | 0.729 | 0.280 | 0.091 |
| Cs5 s1 | 0.314 | 0.403 | 0.744 | 0.285 | 0.107 |
| Cs5 s2 | 0.309 | 0.318 | 0.739 | 0.283 | 0.095 |
| CsM5 s0 | 0.306 | 0.365 | 0.733 | 0.279 | 0.080 |
| CsM5 s1 | 0.329 | 0.343 | 0.772 | 0.279 | 0.096 |
| CsM5 s2 | 0.327 | 0.394 | 0.764 | 0.274 | 0.071 |
| CsM5 s3 | 0.320 | 0.400 | 0.749 | 0.263 | 0.079 |
| CsM5 s4 | 0.306 | 0.349 | 0.745 | 0.267 | 0.077 |
| BsM5 s0 | 0.335 | 0.369 | 0.763 | 0.298 | 0.052 |
| BsM5 s1 | 0.343 | 0.358 | 0.775 | 0.308 | 0.069 |
| BsM5 s2 | 0.341 | 0.371 | 0.776 | 0.296 | 0.064 |

On test inactive IoU, every SSL seed (0.318–0.403) is above every A5c seed (0.192–0.284).

## Locked rules
Each cell gives the difference, then the threshold in brackets. Rules 2 and 3 are the same contrast: with the separate forward and λ = 0 the student is the supervised run, bit for bit.

| Contrast | Role | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| **CsM5 − A5c** (5 vs 5) | **primary** (rules 2 + 3) | +0.014 (0.016) | **+0.117** (0.052) | **+0.033** (0.025) | **passes**; width relP@2 −0.019, ok |
| BsM5 − A5c | secondary | **+0.036** (0.011) | **+0.113** (0.043) | **+0.052** (0.019) | passes on all three; width ok |
| Cs5 − A5c | secondary | +0.004 (0.012) | **+0.105** (0.065) | +0.018 (0.019) | passes on inactive only |
| CsM5 − Cs5 (CutMix) | rule 4 | +0.010 (0.015) | +0.012 (0.057) | +0.015 (0.020) | n.d. |
| CsM5 − BsM5 (tolerant vs hard) | rule 5 | **−0.022** (0.014) | +0.004 (0.031) | −0.019 (0.020) | tolerant **worse** on crack IoU |
| Cs5 − Cm5 (separate vs joint BN) | rule 6, descriptive | −0.003 (0.014) | +0.084 (0.167) | +0.001 (0.018) | n.d. (Cm5 inactive sd 0.139) |

Number of contrasts: 1 primary and 5 secondary, all reported.

### Amendment 2: BsM5 with 5 seeds (13 Oct; s3–4 added post hoc)
BsM5 s3–4 ran 13 Oct 02:00–04:08 IST (`bac5264`, `el_p13`, session `p13a2`); per-seed numbers and the full analysis are in `../p17/README.md`. The tables above keep the 3-seed numbers as first reported.

| | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 |
|---|---|---|---|---|
| BsM5 s3 / s4 | 0.317 / 0.327 | 0.345 / 0.357 | 0.742 / 0.764 | 0.917 / 0.911 |
| **BsM5, 5 seeds** | 0.333±0.011 | 0.360±0.010 | 0.764±0.014 | 0.907±0.014 |

| Contrast (5 vs 5) | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| BsM5 − A5c (secondary) | **+0.029** (0.016) | **+0.107** (0.044) | **+0.045** (0.023) | passes on all three; width ok |
| CsM5 − BsM5 (rule 5) | −0.015 (0.018) | +0.010 (0.032) | −0.012 (0.024) | **n.d.** (was: tolerant worse on crack IoU) |

- Bootstrap: BsM5 − A5c crack +0.029 [+0.014, +0.041], inactive +0.107 [+0.028, +0.188]. CsM5 − BsM5 crack −0.015 [−0.023, −0.009]: still negative over cells, no longer by the seed rule.
- Without `CSIR_00070_r8_c4` (post hoc): BsM5 − A5c still passes on all three. CsM5 − A5c crack IoU becomes +0.016 (0.014), over the threshold; with the cell it is +0.014 (0.016). `../p17/sensitivity_excell.txt`.
- Gap closed by BsM5, 5 seeds: crack 17%, inactive 61%, relF1@2 29%.

**Gap closed** (X − A5c) / (L3 100% − A5c):

| Arm | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| CsM5 | 8% | 67% | 21% |
| BsM5 | 21% | 64% | 33% |
| Cs5 | 2% | 60% | 11% |

## Robustness
Paired image bootstrap over the 50 test cells (2,000 resamples), then the Δ without the top-3 cells.

| Contrast | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| **CsM5 − A5c** | +0.014 [−0.004, +0.027]; +0.003 | **+0.117 [+0.042, +0.189]; +0.103** | **+0.033 [+0.006, +0.055]; +0.020** |
| BsM5 − A5c | +0.036 [+0.021, +0.048]; +0.031 | +0.113 [+0.028, +0.201]; +0.107 | +0.052 [+0.030, +0.072]; +0.048 |
| Cs5 − A5c | +0.004 [−0.015, +0.018]; −0.009 | +0.105 [+0.025, +0.179]; +0.077 | +0.018 [−0.015, +0.043]; −0.003 |
| CsM5 − Cs5 | +0.010 [+0.004, +0.017]; +0.012 | +0.012 [−0.006, +0.038]; +0.026 | +0.015 [+0.004, +0.029]; +0.022 |
| CsM5 − BsM5 | −0.022 [−0.031, −0.016]; −0.027 | +0.004 [−0.022, +0.026]; −0.004 | −0.019 [−0.035, −0.008]; −0.029 |
| Cs5 − Cm5 | −0.003 [−0.014, +0.007]; −0.006 | +0.084 [+0.030, +0.143]; +0.079 | +0.001 [−0.023, +0.020]; −0.006 |

- **The primary claim's passing metrics are robust over cells.** Inactive and relF1@2 both have CIs above 0 and survive top-3 removal.
- **Source split for CsM5 − A5c:**
  - Inactive: CFVS/BMRK/SDLE +0.114 [+0.034, +0.190]. In CSIR/ARTS all inactive pixels sit in 3 cells.
  - Crack IoU: CFVS/BMRK/SDLE +0.020 [+0.004, +0.034]; CSIR/ARTS −0.022 [−0.048, +0.003].
- **BsM5's crack gain** holds in both groups: CFVS/BMRK/SDLE +0.037 [+0.021, +0.051]; CSIR/ARTS +0.028 [−0.000, +0.047].
- **Cs5's crack** in CSIR/ARTS is worse: −0.041 [−0.071, −0.013].

## Collapse watch (rule: rare_frac at steps 4,000 and 20,000)
`rare_frac` is the share of unlabelled pixels pseudo-labelled crack or inactive. `conf_frac` is the share of confident pixels.

| Run | step 4,000 conf / rare | step 20,000 conf / rare |
|---|---|---|
| Cs5 s0 / s1 / s2 | 0.862 / 0.0079; 0.866 / 0.0087; 0.865 / 0.0065 | 0.956 / 0.0083; 0.956 / 0.0082; 0.958 / 0.0071 |
| CsM5 s0 / s1 / s2 | 0.861 / 0.0079; 0.862 / 0.0084; 0.863 / 0.0066 | 0.953 / 0.0101; 0.949 / 0.0109; 0.954 / 0.0081 |
| CsM5 s3 / s4 | 0.857 / 0.0078; 0.869 / 0.0064 | 0.957 / 0.0081; 0.952 / 0.0070 |
| BsM5 s0 / s1 / s2 | 0.869; 0.874; 0.871 (no rare_frac logged) | 0.965; 0.965; 0.965 |

- No collapse: rare_frac holds or rises.
- `confidence_ce` does not log rare_frac, so BsM5 has conf_frac only.
- **CutMix raises the unlabelled loss share.** At step 20,000, s0, the unlabelled / supervised loss ratio is:

  | Arm | ratio |
  |---|---|
  | Cs5 | 0.46 |
  | CsM5 | 0.77 |
  | BsM5 | 0.98 |

  The audit's concern was a loss about 10× below supervised (P10, joint BN).

## Secondary
- **Bin-0 share** (GT pixels scored < 0.001), crack / inactive:

  | Arm | crack | inactive |
  |---|---|---|
  | A5 (s3–4) | 0.572 | 0.729 |
  | Cs5 | 0.528 | 0.497 |
  | CsM5 | 0.500 | 0.449 |
  | BsM5 | 0.440 | 0.442 |

- **Validation disagrees with test on inactive.** Val inactive IoU: A5c 0.106, Cs5 0.098, CsM5 0.081, BsM5 0.061.
  - Val has 54 cells, only 6 contain inactive, and 3 of them hold 89% of its inactive pixels.
  - Test has 16 inactive cells; 3 of them hold 59%.
  - Val crack IoU: BsM5 0.300, Cs5 0.283, A5c 0.278, CsM5 0.272.
- **P16's CutMix pick used these val numbers, as locked** (`el_p16/reports/p16b/selection.txt`):
  - CsM5 scored 0.351, Cs5 0.365, so CutMix is **off** in P16.
  - On test, CsM5 − Cs5 is n.d. under the seed rule but positive over cells on crack: +0.010 [+0.004, +0.017].
- **Descriptive, across fractions:** every 5% SSL arm's test inactive IoU (0.36–0.37) is above supervised at 10% (0.294). On crack all stay well below it (0.308–0.340 vs 0.396).

## E1 per-cell metrics (secondary; `../e1/e1_p13.md`)
**Test, CsM5 − A5c**

| Metric | Δ | 95% CI |
|---|---|---|
| inactive cell IoU | +0.119 | [+0.036, +0.211] |
| crack tolF1 | +0.008 | [−0.022, +0.034] |
| crack length error | −0.076 | [−0.155, +0.013] |

BsM5 − A5c crack tolF1: +0.036 [+0.009, +0.064].

**Unseen-module extension (106 cells)**

| Contrast | Metric | Δ | 95% CI |
|---|---|---|---|
| CsM5 − A5c | inactive cell IoU | +0.467 (0.033 → 0.500) | [+0.322, +0.592] |
| CsM5 − A5c | crack IoU | +0.001 | [−0.011, +0.012] |
| CsM5 − A5c | crack false alarm | +0.027 | [−0.024, +0.085] |
| BsM5 − A5c | crack IoU | +0.012 | [+0.004, +0.020] |
| BsM5 − A5c | crack relF1@2 | +0.046 | [+0.018, +0.072] |
| Cs5 − Cm5 | crack false alarm | −0.095 | [−0.141, −0.050] |

The last row means separate BN removes most of the false-alarm rise that joint-BN tolerant pseudo-labels showed in E1.

## Reading
- **Primary claim: passes, and robust over cells.** At 5% labels, Mean Teacher with tolerant pseudo-labels, separate BN and CutMix beats a 5-seed supervised baseline on inactive IoU (+0.117) and crack relF1@2 (+0.033). Crack IoU is n.d. (+0.014).
- **Inactive.** Every separate-BN SSL arm gains +0.10 to +0.12 on test, robust over cells, and larger on unseen modules. Val does not show it; val has 6 inactive cells.
- **Crack.**
  - Tolerant PL alone, against a clean control, adds about 0 (Cs5 +0.004).
  - P12's crack gain of the loss (Cm5 − Dm5 +0.023) was measured against a joint-BN control that sat 0.017 below supervised. So it mostly offset that handicap.
  - CutMix adds about +0.010 (robust over cells, n.d. on seeds).
  - Hard pseudo-labels with CutMix (BsM5, 3 seeds) give the largest crack gain, +0.036, robust. Tolerant is worse than hard under CutMix (−0.022).
- **Limits.**
  - BsM5 has 3 seeds and is secondary.
  - No gaint replication (Amendment 1).
  - The EMA-only effect is not measured.
  - One split.
