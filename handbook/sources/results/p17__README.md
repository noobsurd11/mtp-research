# P17: SKCDF-style decoupled decoder on BsM5, 5% labels (23 cells), L3 base. Results

Protocol: `protocols/P17_decoupled_decoder.md`, locked before any run (smoke excepted). BsM5 seeds 3–4 come from P13 Amendment 2 (post hoc, disclosed there).

**Runs**
- cv02 (RTX A6000): BsD5 `p17_BsD_5pct_s0..4`, GPUs 3–7, 13 Oct 01:55–04:04 IST. BsM5 s3–4 (`el_p13`, `bac5264`), GPUs 1–2, 02:00–04:08 IST. All 14 train/rescore steps have rc = 0. All are 20,000 steps; the EMA teacher's final weights are evaluated.
- Code: commit `f2f20d3` (= `bac5264` + `ssl.decouple_decoder`), deployment `el_p17`.
- **Built-in pipeline check: passed.** For every seed, the logged losses and validation numbers up to step 2,000 (λ = 0) are identical to BsM5's for the same seed (44 log lines each).

**Files**
- `raw/`: re-score JSONs and `launch.log`. BsM5 s3–4: `../p13/raw/` (`launch_a2.log`), per-image `../p13/per_image_a2.json`.
- `p17_rules.txt`, `per_image_test.txt` (bootstrap, source split, without the noisy cell), `fig_p17_bars.png`, `per_image.json`, `hist_revised.npz`.
- `decoder_u_secondary.txt`: student encoder + `decoder_u` vs teacher, from each run's `metrics.json`.
- `sensitivity_excell.txt`: rule-1 arithmetic with and without `CSIR_00070_r8_c4` (`scripts/p17_excell.py`).
- E1: `../e1/e1_p17.md`.
- Reproduce with `bash scripts/post_ssl.sh p17 <gpu> 5`, then `scripts/p17_excell.py`.

## Results
Test cells, revised labels, mean ± sd over seeds.

| Arm | Seeds | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| **A5c**: supervised 5% | 0–4 | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.892±0.016 | 0.287±0.007 | 0.253±0.041 |
| **BsM5**: hard PL, separate BN, CutMix (s3–4 post hoc, P13 Am. 2) | 0–4 | 0.333±0.011 | 0.360±0.010 | 0.764±0.014 | 0.907±0.014 | 0.367±0.016 | 0.429±0.013 |
| **BsD5**: BsM5 + decoupled decoder | 0–4 | 0.327±0.003 | 0.371±0.036 | 0.756±0.006 | 0.888±0.012 | 0.310±0.005 | 0.357±0.036 |
| CsM5 (P13) | 0–4 | 0.317±0.011 | 0.370±0.026 | 0.752±0.016 | 0.874±0.036 | 0.329±0.014 | 0.420±0.028 |
| L3 10% (P6) | 0–2 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6) | 0–2 | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

### Per seed
| Run | test crack IoU | test inactive IoU | test crack relF1@2 | crack AP | val crack IoU | val inactive IoU |
|---|---|---|---|---|---|---|
| BsM5 s0 | 0.335 | 0.369 | 0.763 | 0.364 | 0.298 | 0.052 |
| BsM5 s1 | 0.343 | 0.358 | 0.775 | 0.372 | 0.308 | 0.069 |
| BsM5 s2 | 0.341 | 0.371 | 0.776 | 0.383 | 0.296 | 0.064 |
| BsM5 s3 (Am. 2) | 0.317 | 0.345 | 0.742 | 0.342 | 0.287 | 0.071 |
| BsM5 s4 (Am. 2) | 0.327 | 0.357 | 0.764 | 0.375 | 0.293 | 0.061 |
| BsD5 s0 | 0.322 | 0.327 | 0.746 | 0.301 | 0.289 | 0.048 |
| BsD5 s1 | 0.330 | 0.391 | 0.762 | 0.312 | 0.295 | 0.104 |
| BsD5 s2 | 0.327 | 0.390 | 0.760 | 0.313 | 0.291 | 0.094 |
| BsD5 s3 | 0.329 | 0.408 | 0.756 | 0.313 | 0.278 | 0.072 |
| BsD5 s4 | 0.326 | 0.338 | 0.757 | 0.312 | 0.301 | 0.081 |

BsM5 seeds 3–4 are below seeds 0–2 on crack IoU (0.317 and 0.327 vs 0.335–0.343). The 5-seed BsM5 mean is 0.333, not the 3-seed 0.340.

## Locked rules (5 vs 5, P8 rule 1)
Each cell gives the difference, then the threshold in brackets.

| Contrast | Role | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| **BsD5 − BsM5** | **rule 1, primary** | −0.006 (0.013) | +0.011 (0.043) | −0.008 (0.017) | **n.d.**; width relP@2 −0.019, ok |
| BsD5 − A5c | rule 2, secondary | **+0.023** (0.010) | **+0.117** (0.060) | **+0.037** (0.018) | passes on all three; width ok |

**Rule 1 reading as locked:** any share of the BsM5 gain that needs the labelled decoder to fit pseudo-labels is below the detection threshold. Thresholds as a share of the BsM5 − A5c gain (5 vs 5): crack IoU 44%, inactive IoU 41%, relF1@2 39%. A decoder share smaller than about 40% of the gain cannot be detected with 5 seeds.

Point estimates, BsD5's gain over A5c as a share of BsM5's: crack IoU 80%, inactive IoU 110%, relF1@2 82%.

### P13 contrasts at 5 vs 5 (Amendment 2)
| Contrast | Role in P13 | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| BsM5 − A5c | secondary | **+0.029** (0.016) | **+0.107** (0.044) | **+0.045** (0.023) | passes on all three (3 seeds: +0.036 / +0.113 / +0.052) |
| CsM5 − BsM5 | rule 5 | −0.015 (0.018) | +0.010 (0.032) | −0.012 (0.024) | **n.d.** (3 seeds of BsM5: tolerant worse on crack IoU) |

**Changed by the added seeds:** P13 rule 5 said "tolerant worse on crack IoU" on 5 vs 3. On 5 vs 5 it is n.d.: BsM5's sd rose from 0.004 to 0.011. The image bootstrap still puts CsM5 − BsM5 crack IoU below 0 (below).

## Robustness
Paired image bootstrap over the 50 test cells (2,000 resamples); Δ without the top-3 cells.

| Contrast | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| **BsD5 − BsM5** | −0.006 [−0.011, +0.002]; −0.003 | +0.011 [−0.013, +0.038]; +0.022 | −0.008 [−0.014, +0.000]; −0.004 |
| BsD5 − A5c | +0.023 [+0.009, +0.035]; +0.019 | +0.117 [+0.051, +0.187]; +0.107 | +0.037 [+0.018, +0.055]; +0.032 |
| BsM5 − A5c | +0.029 [+0.014, +0.041]; +0.021 | +0.107 [+0.028, +0.188]; +0.085 | +0.045 [+0.024, +0.065]; +0.037 |
| CsM5 − BsM5 | −0.015 [−0.023, −0.009]; −0.018 | +0.010 [−0.008, +0.029]; +0.018 | −0.012 [−0.025, −0.002]; −0.017 |

(relF1@2 bootstrap from E1, `../e1/e1_p17.md`.)

- **BsD5 − BsM5 crack IoU leans negative over cells** (P(Δ > 0) = 0.06; relF1@2 0.03). The lean sits in CSIR/ARTS: −0.020 [−0.028, −0.008]. In CFVS/BMRK/SDLE it is −0.003 [−0.009, +0.006].
- BsD5 − A5c crack IoU: CFVS/BMRK/SDLE +0.028 [+0.015, +0.040]; CSIR/ARTS −0.005 [−0.027, +0.007].

### Without test cell `CSIR_00070_r8_c4` (post hoc, as P16)
- Crack FP pixels on that cell are small for BsM5 (0–38) and BsD5 (3–390). It does not drive any P17 contrast.
- BsD5 − BsM5 without it: −0.006 (0.013) / +0.012 (0.046) / −0.008 (0.017), n.d. BsD5 − A5c: passes on all three.
- **CsM5 − A5c** (P13 primary) without it: crack IoU +0.016 (0.014), which crosses the threshold (with it: +0.014 (0.016)). CsM5 s0 puts 4,481 crack FP px on that cell. Post hoc, not a verdict.

## Secondary decoder (descriptive): student encoder + `decoder_u` vs teacher
Trainer evaluator, test, final weights. The teacher numbers equal the re-score.

| Path | crack IoU | inactive IoU |
|---|---|---|
| teacher (encoder EMA + labelled decoder) | 0.327±0.003 | 0.371±0.036 |
| student encoder + `decoder_u` (SKCDF's inference path) | 0.334±0.003 | 0.375±0.040 |
| `decoder_u` − teacher, per seed | +0.007, +0.005, +0.007, +0.006, +0.009 | +0.006, +0.012, +0.008, +0.001, −0.008 |

`decoder_u` is above the teacher on crack IoU in all 5 seeds, by 0.005–0.009. It is not a locked contrast.

## Collapse watch
`confidence_ce` does not log `rare_frac` (as P13 BsM5). conf_frac at steps 4,000 / 20,000:
- BsD5 s0–4: 0.864 / 0.963; 0.870 / 0.963; 0.866 / 0.962; 0.858 / 0.963; 0.869 / 0.961.
- BsM5 s3–4: 0.865 / 0.966; 0.874 / 0.962.

No sign of collapse: conf_frac rises as in BsM5 s0–2 (0.869–0.874 / 0.965).

## Score histograms (secondary)
Bin-0 share (GT px scored < 0.001), test, crack / inactive: BsD5 0.526 / 0.544; BsM5 s0–2 0.440 / 0.442; A5 s3–4 0.572 / 0.729 (`../p13/README.md`). BsD5's teacher leaves more GT pixels at near-zero score than BsM5's, in line with its lower AP (crack 0.310 vs 0.367, inactive 0.357 vs 0.429).

## E1 per-cell metrics (secondary, `../e1/e1_p17.md`)
- **Test, BsD5 − BsM5:** crack tolF1 +0.001 [−0.014, +0.018], inactive area error −0.045 pp [−0.116, +0.014]. No per-cell CI excludes 0.
- **Extension (106 cells, unseen modules), BsD5 − BsM5:**
  - crack tolF1 +0.016 [+0.002, +0.033];
  - crack false alarm +0.049 [+0.011, +0.089] (more cells with false crack);
  - inactive area error −0.065 pp [−0.117, −0.019];
  - inactive detection F1 +0.143 [−0.008, +0.280].
- All descriptive; the extension measures transfer to unseen modules.

## EMA check (added 13 Oct, descriptive; `../ema_check/README.md`)
At step 20,000 BsD5's EMA teacher and its student score the same (teacher − student: crack IoU −0.0008, inactive −0.0008, mean over seeds; all within ±0.005). The student is the encoder trained with pseudo-labels plus the labelled decoder trained on labelled data only. So BsD5's gain over A5c sits in the encoder, not in EMA averaging.

## Not claimed
- SKCDF itself, or any comparison with its published numbers.
- That the decoder plays no role: rule 1 is n.d. with thresholds near 40% of the gain.
- Tuning of ω, λ or anything else; other label fractions; gaint replication; other split seeds.
