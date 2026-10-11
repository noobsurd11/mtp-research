# cv02 replicate block: report (2026-10-04, day + night)

Host `himtenduh` (cv02), 8× RTX A6000. Times are UTC (IST = UTC + 5:30). Workspace `/tmp/noob_el` (local NVMe, **wiped on reboot**).

## Summary

**Night block (17:51 UTC Oct 4 to 03:36 Oct 5; PV-S3 still training, see below):**
* Code updated to **fe79e19**: pytest gives 171 passed and 1 skipped, the pilot checkpoint as expected.
* **All 8 night runs finished rc 0, with no resumes.** All 18 cv02 runs are re-scored on CPU on val + test pooled, and synced.
* **Per arm**, final test (50 images) and val+test (104 images), mean ± sd over seeds:

  | arm | seeds | test defect_miou | val+test defect_miou |
  |---|---|---|---|
  | ALHVR | 4 | 0.3742 ± 0.0128 | 0.3483 ± 0.0138 |
  | MT-20 | 3 | 0.3648 ± 0.0071 | 0.3407 ± 0.0068 |
  | SA SL-20 | 3 | 0.3407 ± 0.0126 | 0.2943 ± 0.0243 |
  | SL-100 | 3 | 0.3402 ± 0.0057 | 0.2970 ± 0.0126 |
  | SL-20 | 5 | 0.3391 ± 0.0326 | 0.3145 ± 0.0228 |

  Both SSL arms are above all three supervised arms on both metrics (details under "Night-block observations").
* **Jha et al. PV-S3:**
  * Setup took about 12 min of the 2 h timebox.
  * Attempt 1 (Oct 4 20:02) and attempt 2 (Oct 5 05:05) each failed within about a minute, on fixable data / environment glue.
  * Through my error, attempt 1 was not relaunched overnight after its fix, so about 9 h of GPU time went unused.
  * Attempt 3 finished at 07:22 (results in "Morning of Oct 5" and "Jha et al.").

**Oct 6 (block E):**
* **UCF-EL label sweep**, 11 runs, all rc 0, 09:47–12:45. 4-class defect mean IoU on test:
  100 % 0.536 ± 0.004, 20 % 0.493 ± 0.005, 5 % 0.415 ± 0.002, 1 % 0.227 ± 0.002.
  * The 1 % subset has no corrosion; its 3-class mean is 0.302.
  * Crack AP: 0.851, 0.807, 0.766, 0.690.
* **`train.py` patch** for the `sl<N>` subsets, with a test. Diff synced in `results_to_sync/cv02_patches/`.
* **BatchNorm re-estimation:** numbers only, in Block E.
* **Reporting:** the headline is the default threshold, with the val-chosen crack bias and AP alongside (table under the results).
* **Cleanup:** stopped-run folders removed; final checkpoints kept.

**Oct 6 (block D):**
* **Pixel AP** for all 33 BenchmarkEL checkpoints. Crack AP is highest for SL-20 b8 (0.494). Inactive AP is 0.665–0.676 for every arm
  that passes unlabelled images through the forward pass (MT, ALHVR, with or without their unlabelled loss), against 0.616–0.637 for
  every supervised arm, SL-20 b8 included.
* **UCF label sweep:** stopped at the check. The code accepts only the `sl20` and `full` UCF subsets; see Block D.

**Evening Oct 5 – morning Oct 6 (blocks A–C):**
* **Precision diagnostic:** crack is over-predicted everywhere (P 0.30, R 0.72; most false positives lie within a few px of a true
  crack). A val-chosen crack bias adds +0.016–0.027 on test, except SL-100. The SSL lead survives it.
* **Block B, 12 runs, all done:** **SL-20 at batch 8 matches MT-20** (0.362 vs 0.365), and **ALHVR without its unlabelled loss
  matches MT-20 too** (0.364; ALHVR 0.374, Δ within noise).
* Every arm whose BatchNorm sees 8 images per step lands at 0.362–0.370; every arm with 4 lands at 0.339–0.343.
* ALHVR λ=0: λ = 0 and loss = sup exactly on all 1,200 logged steps.

**Morning of Oct 5:**
* **MT EMA control** `mt_20pct_lam0_s{0,1,2}_cv02` (unlabelled-loss weight 0; config diff = only the weight; `loss_con = 0` on all
  1,200 logged steps): **0.3653 ± 0.0183** on test, the same as MT-20's 0.3648 ± 0.0071.
  * Neither the unlabelled loss (paired λ 1.5 − λ 0 on the teacher: −0.000 ± 0.024) nor the EMA at the final step
    (teacher − student +0.000 ± 0.002) explains MT's gain over SL-20.
  * The remaining code-path difference is the mixed labelled + unlabelled BatchNorm batch (untested; see open items).
  * Section "MT EMA control".
* **PV-S3 done** (attempt 3, 05:07–07:22).
  * **As released it never predicts background**: `ignore_index=0` in their loss.
  * Standard defect mean IoU is **0.050**, and corrosion is predicted on 3.33M px against a GT of 102,570 (32×).
  * pvs3 convention: **0.828** (eval295) / 0.791 (native), which matches PV-S3's own validation log to 4 decimals.
  * Details are in "Jha et al.".
* **ALHVR prototype diagnostic** (no training): `reports/prototype_diagnostic.md`, on the cv02 ALHVR runs s1–s4. Gaint's
  `alhvr_20pct_s0` checkpoint is not here; the cv02 runs share its seed-0 split.
  * Ω3 true crack labelled background by the DTCT winner: **20.7 ± 0.2 %** (training-time logs: 32.4 % over the run).
  * Cross-network prototypes, as CG-CPCL uses them, are near-uninformative for defects: Ω3 crack 4.6 % vs 43–49 % with own
    prototypes.
  * The "prototype if the winner says background" rule is strongly net-negative: Ω3 +5 % crack against −25 % background.
* No cleanup until you say so.

**Day block:**

* **Done:** all 10 runs finished with **rc 0**. There were no crashes, no watchdog restarts and no resumes (`resumes: []` everywhere).
  The block ran from 06:12 to 15:54 UTC; the SL / SA runs were finished by 09:17 and the two ALHVR runs by 15:54.
* **Calibration:** `sl_20pct_s0_cv02` final `defect_miou` **0.3385** vs gaint 0.3059. That is **inside** gaint's SL-20 seed range of
  0.3059–0.3786, so cv02 is calibrated (informational only).
* **Per arm**, final-step test, mean ± sd over seeds, cv02 only:

  | arm | seeds | defect_miou |
  |---|---|---|
  | SL-20 | 5 | 0.3391 ± 0.0326 |
  | SA SL-20 | 3 | 0.3407 ± 0.0126 |
  | ALHVR | 2 | 0.3651 ± 0.0074 |
* **Results:** `/tmp/noob_el/results_to_sync/<run>/` (for your pull) and `~/noob/el_results/<run>/` (persistent; 3.7 MB of the 50 MB cap).
* **Rules kept:**
  * Nothing large under `~`: the only home writes are `~/noob/el_results/` (on your request) and two small Claude Code memory notes under
    `~/.claude/`. `~/.bashrc` and `~/.profile` md5 are unchanged, and `~/.cache` is unchanged.
  * The `amlc` and `main` tmux sessions and the rest of `~/noob` were not touched.
  * Each run kept latest + best checkpoints only (20 `.pth` for 10 runs).
  * Nothing was pushed to git (the tarball has no `.git`).
  * The repo code is unchanged from REVISION. All cv02 tooling lives in `/tmp/noob_el/tools/`.
* **Deviations, all approved by you:**
  * From 07:05, GPUs 0, 4 and 5 were used although they failed the idle rule, and the job cap went from 3 to 6.
  * `stringzilla` was pinned to gaint's 5.1.2.
  * The smp weights are in `HF_HOME`.

## Results (all runs)

All comparisons stay within this machine; gaint numbers appear only in the calibration line. The table below is generated from each run's
`metrics.json` (`test_final`).

<!-- cv02-results:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. Standard convention, final-step weights (step 20,000; MT = EMA teacher, ALHVR = network A). **test**: in-training final test, 50 images (primary). **val+test**: CPU re-score on val + test pooled, 104 images (`eval_final_valtest_cpu.json`)._

| arm | run | seed | GPU | state | test defect_miou | test crack | test inactive | val+test defect_miou | val+test crack | val+test inactive |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|
| SL-20 | `sl_20pct_s0_cv02` | 0 | 2 | done | 0.3385 | 0.2514 | 0.4256 | 0.3134 | 0.2378 | 0.3890 |
| SL-20 | `sl_20pct_s1_cv02` | 1 | 2 | done | 0.3467 | 0.2749 | 0.4185 | 0.3157 | 0.2501 | 0.3812 |
| SL-20 | `sl_20pct_s2_cv02` | 2 | 2 | done | 0.3709 | 0.2914 | 0.4505 | 0.3370 | 0.2655 | 0.4085 |
| SL-20 | `sl_20pct_s3_cv02` | 3 | 0 | done | 0.2848 | 0.1332 | 0.4365 | 0.2777 | 0.1478 | 0.4075 |
| SL-20 | `sl_20pct_s4_cv02` | 4 | 4 | done | 0.3546 | 0.2862 | 0.4229 | 0.3289 | 0.2587 | 0.3992 |
| SA SL-20 | `sa_sl_20pct_s0_cv02` | 0 | 0 | done | 0.3262 | 0.2778 | 0.3747 | 0.2927 | 0.2484 | 0.3371 |
| SA SL-20 | `sa_sl_20pct_s1_cv02` | 1 | 4 | done | 0.3463 | 0.2749 | 0.4177 | 0.2708 | 0.2412 | 0.3004 |
| SA SL-20 | `sa_sl_20pct_s2_cv02` | 2 | 5 | done | 0.3494 | 0.2749 | 0.4240 | 0.3193 | 0.2545 | 0.3841 |
| ALHVR | `alhvr_20pct_s1_cv02` | 1 | 6 | done | 0.3599 | 0.2840 | 0.4359 | 0.3332 | 0.2638 | 0.4026 |
| ALHVR | `alhvr_20pct_s2_cv02` | 2 | 7 | done | 0.3704 | 0.2894 | 0.4514 | 0.3440 | 0.2686 | 0.4194 |
| ALHVR | `alhvr_20pct_s3_cv02` | 3 | 6 | done | 0.3762 | 0.2962 | 0.4561 | 0.3500 | 0.2718 | 0.4282 |
| ALHVR | `alhvr_20pct_s4_cv02` | 4 | 7 | done | 0.3905 | 0.2914 | 0.4896 | 0.3661 | 0.2710 | 0.4612 |
| MT-20 | `mt_20pct_s0_cv02` | 0 | 0 | done | 0.3700 | 0.2776 | 0.4624 | 0.3446 | 0.2562 | 0.4330 |
| MT-20 | `mt_20pct_s1_cv02` | 1 | 4 | done | 0.3567 | 0.2778 | 0.4357 | 0.3328 | 0.2522 | 0.4135 |
| MT-20 | `mt_20pct_s2_cv02` | 2 | 5 | done | 0.3679 | 0.2750 | 0.4607 | 0.3447 | 0.2525 | 0.4369 |
| SL-100 | `sl_100pct_s0_cv02` | 0 | 5 | done | 0.3337 | 0.2666 | 0.4008 | 0.2849 | 0.2438 | 0.3259 |
| SL-100 | `sl_100pct_s1_cv02` | 1 | 5 | done | 0.3424 | 0.2697 | 0.4151 | 0.2961 | 0.2439 | 0.3483 |
| SL-100 | `sl_100pct_s2_cv02` | 2 | 5 | done | 0.3445 | 0.2758 | 0.4131 | 0.3101 | 0.2561 | 0.3640 |
| MT-20 λ=0 | `mt_20pct_lam0_s0_cv02` | 0 | 1 | done | 0.3451 | 0.2410 | 0.4493 | 0.3261 | 0.2341 | 0.4180 |
| MT-20 λ=0 | `mt_20pct_lam0_s1_cv02` | 1 | 2 | done | 0.3809 | 0.2847 | 0.4772 | 0.3490 | 0.2605 | 0.4375 |
| MT-20 λ=0 | `mt_20pct_lam0_s2_cv02` | 2 | 3 | done | 0.3698 | 0.2832 | 0.4563 | 0.3389 | 0.2572 | 0.4207 |
| SL-20 b8 | `sl_20pct_b8_s0_cv02` | 0 | 7 | done | 0.3691 | 0.2970 | 0.4412 | 0.3476 | 0.2729 | 0.4222 |
| SL-20 b8 | `sl_20pct_b8_s1_cv02` | 1 | 5 | done | 0.3541 | 0.2982 | 0.4101 | 0.3358 | 0.2732 | 0.3985 |
| SL-20 b8 | `sl_20pct_b8_s2_cv02` | 2 | 3 | done | 0.3635 | 0.2957 | 0.4313 | 0.3342 | 0.2720 | 0.3964 |
| SL-100 b8 | `sl_100pct_b8_s0_cv02` | 0 | 4 | done | 0.3500 | 0.2825 | 0.4174 | 0.3188 | 0.2619 | 0.3757 |
| SL-100 b8 | `sl_100pct_b8_s1_cv02` | 1 | 7 | done | 0.3412 | 0.2842 | 0.3982 | 0.3076 | 0.2591 | 0.3561 |
| SL-100 b8 | `sl_100pct_b8_s2_cv02` | 2 | 6 | done | 0.3393 | 0.2724 | 0.4063 | 0.3118 | 0.2533 | 0.3702 |
| SL-10 b8 | `sl_10pct_b8_s0_cv02` | 0 | 6 | done | 0.3421 | 0.2676 | 0.4165 | 0.3273 | 0.2535 | 0.4011 |
| SL-10 b8 | `sl_10pct_b8_s1_cv02` | 1 | 6 → 7 | done | 0.3428 | 0.2741 | 0.4114 | 0.3291 | 0.2572 | 0.4011 |
| SL-10 b8 | `sl_10pct_b8_s2_cv02` | 2 | 3 | done | 0.3743 | 0.3063 | 0.4422 | 0.3488 | 0.2764 | 0.4211 |
| ALHVR λ=0 | `alhvr_20pct_lam0_r2_s1_cv02` | 1 | 0 | done | 0.3757 | 0.2903 | 0.4612 | 0.3440 | 0.2632 | 0.4248 |
| ALHVR λ=0 | `alhvr_20pct_lam0_r2_s2_cv02` | 2 | 1 | done | 0.3708 | 0.2764 | 0.4651 | 0.3476 | 0.2562 | 0.4390 |
| ALHVR λ=0 | `alhvr_20pct_lam0_r2_s3_cv02` | 3 | 2 | done | 0.3461 | 0.2111 | 0.4810 | 0.3251 | 0.2115 | 0.4388 |

**Per arm: mean ± sd (sample sd, ddof = 1) over the finished seeds**

| arm | seeds done | test defect_miou | test crack | test inactive | val+test n | val+test defect_miou | val+test crack | val+test inactive |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **SL-20** | 5 of 5 | 0.3391 ± 0.0326 | 0.2474 ± 0.0657 | 0.4308 ± 0.0128 | 5 | 0.3145 ± 0.0228 | 0.2320 ± 0.0482 | 0.3971 ± 0.0118 |
| **SA SL-20** | 3 of 3 | 0.3407 ± 0.0126 | 0.2759 ± 0.0017 | 0.4055 ± 0.0268 | 3 | 0.2943 ± 0.0243 | 0.2480 ± 0.0067 | 0.3405 ± 0.0420 |
| **ALHVR** | 4 of 4 | 0.3742 ± 0.0128 | 0.2902 ± 0.0051 | 0.4582 ± 0.0226 | 4 | 0.3483 ± 0.0138 | 0.2688 ± 0.0036 | 0.4279 ± 0.0247 |
| **MT-20** | 3 of 3 | 0.3648 ± 0.0071 | 0.2768 ± 0.0015 | 0.4529 ± 0.0150 | 3 | 0.3407 ± 0.0068 | 0.2536 ± 0.0022 | 0.4278 ± 0.0125 |
| **SL-100** | 3 of 3 | 0.3402 ± 0.0057 | 0.2707 ± 0.0047 | 0.4097 ± 0.0078 | 3 | 0.2970 ± 0.0126 | 0.2480 ± 0.0071 | 0.3461 ± 0.0192 |
| **MT-20 λ=0** | 3 of 3 | 0.3653 ± 0.0183 | 0.2696 ± 0.0248 | 0.4609 ± 0.0145 | 3 | 0.3380 ± 0.0115 | 0.2506 ± 0.0144 | 0.4254 ± 0.0105 |
| **SL-20 b8** | 3 of 3 | 0.3623 ± 0.0076 | 0.2970 ± 0.0012 | 0.4276 ± 0.0159 | 3 | 0.3392 ± 0.0073 | 0.2727 ± 0.0006 | 0.4057 ± 0.0143 |
| **SL-100 b8** | 3 of 3 | 0.3435 ± 0.0057 | 0.2797 ± 0.0064 | 0.4073 ± 0.0097 | 3 | 0.3127 ± 0.0057 | 0.2581 ± 0.0044 | 0.3674 ± 0.0101 |
| **SL-10 b8** | 3 of 3 | 0.3530 ± 0.0184 | 0.2827 ± 0.0207 | 0.4234 ± 0.0165 | 3 | 0.3351 ± 0.0119 | 0.2624 ± 0.0123 | 0.4078 ± 0.0115 |
| **ALHVR λ=0** | 3 of 3 | 0.3642 ± 0.0159 | 0.2593 ± 0.0423 | 0.4691 ± 0.0105 | 3 | 0.3389 ± 0.0121 | 0.2436 ± 0.0280 | 0.4342 ± 0.0081 |

**Calibration** (informational only): `sl_20pct_s0_cv02` final defect_miou **0.3385** vs gaint `sl_20pct_s0` 0.3059 (+0.0326). Gaint's SL-20 seed range is 0.3059–0.3786 (s0 / s1 / s2 = 0.3059 / 0.3679 / 0.3786), so it lies **inside**: calibrated. Crack 0.2514 (gaint 0.204), inactive 0.4256 (gaint 0.408).

<!-- cv02-results:end -->

**Reporting (decision 2026-10-06):** the default threshold (argmax) is the headline. The val-chosen crack bias and pixel AP are shown
alongside it.

<!-- cv02-headline:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. **Headline: default threshold (argmax), final step, test.** Alongside it: test defect_miou with the crack-logit bias chosen on val only (`reports/precision_diagnostic.md`), and pixel AP (1,000 bins, `experiments/_ap_diagnostic`). mean ± sd over runs._

| arm | n | **test defect_miou (default)** | at val-chosen crack bias | chosen b (per run) | crack AP | inactive AP | mean AP |
|---|---:|---:|---:|---|---:|---:|---:|
| SL-20 | 5 | **0.3391 ± 0.0326** | 0.3575 ± 0.0445 | 1.5, 1.5, 1.5, 1.5, 1.5 | 0.464 ± 0.026 | 0.637 ± 0.018 | 0.550 ± 0.020 |
| SA SL-20 | 3 | **0.3407 ± 0.0126** | 0.3565 ± 0.0144 | 1.75, 1.5, 1.5 | 0.452 ± 0.014 | 0.627 ± 0.039 | 0.539 ± 0.021 |
| ALHVR | 4 | **0.3742 ± 0.0128** | 0.3927 ± 0.0118 | 1.25, 1.5, 1.25, 1 | 0.477 ± 0.004 | 0.676 ± 0.020 | 0.577 ± 0.011 |
| MT-20 | 3 | **0.3648 ± 0.0071** | 0.3810 ± 0.0107 | 1.5, 1.75, 1.75 | 0.470 ± 0.003 | 0.666 ± 0.017 | 0.568 ± 0.010 |
| SL-100 | 3 | **0.3402 ± 0.0057** | 0.3375 ± 0.0109 | 1.25, 1.5, 1 | 0.429 ± 0.013 | 0.616 ± 0.016 | 0.523 ± 0.013 |
| MT-20 λ=0 | 3 | **0.3653 ± 0.0183** | 0.3915 ± 0.0083 | 1.5, 1.5, 1.5 | 0.472 ± 0.002 | 0.665 ± 0.025 | 0.569 ± 0.013 |
| SL-20 b8 | 3 | **0.3623 ± 0.0076** | 0.3826 ± 0.0038 | 1.5, 1.75, 1.5 | 0.494 ± 0.004 | 0.618 ± 0.013 | 0.556 ± 0.006 |
| SL-100 b8 | 3 | **0.3435 ± 0.0057** | 0.3506 ± 0.0055 | 1, 1, 1.25 | 0.450 ± 0.001 | 0.632 ± 0.019 | 0.541 ± 0.010 |
| SL-10 b8 | 3 | **0.3530 ± 0.0184** | 0.3868 ± 0.0091 | 1.5, 1.5, 1.75 | 0.485 ± 0.012 | 0.619 ± 0.016 | 0.552 ± 0.014 |
| ALHVR λ=0 | 3 | **0.3642 ± 0.0159** | 0.3879 ± 0.0052 | 1.5, 1.5, 1.5 | 0.468 ± 0.016 | 0.668 ± 0.011 | 0.568 ± 0.010 |

<!-- cv02-headline:end -->

### Night-block observations (cv02 only; 50 test images, 3–5 seeds per arm, so read with care)

* **SSL vs SL-20:** ALHVR is **+0.035** on test (+0.034 on val+test) and MT-20 is **+0.026** (+0.026).
  * All 4 ALHVR seeds and all 3 MT seeds are above the SL-20 mean on both metrics.
  * The SL-20 sd is mostly its s3 outlier: without s3 it is 0.3527 ± 0.0138.
* **ALHVR vs MT-20:** +0.009 on test and +0.008 on val+test. That is the same size as the arms' sds (0.007–0.014), so with n = 4
  and 3 they cannot be separated.
* **SL-100 vs SL-20:** all 478 labels give no gain at 20k steps: +0.001 on test, −0.018 on val+test. Both SSL arms with 20 % labels
  beat SL-100, by +0.025 to +0.034 on test and +0.044 to +0.051 on val+test.
* **SA SL-20 vs SL-20:** equal on test (+0.002), lower on val+test (−0.020).
* **val+test vs test:** val+test is lower than test for every arm. The gap is −0.024 to −0.026 for SL-20, MT-20 and ALHVR, and
  −0.043 to −0.046 for SA SL-20 and SL-100, so those two do worse on the 54 val images.

### Day-block observations (cv02 only; one 50-image test set, 2–5 seeds per arm, so read with care)

* **ALHVR vs SL-20:** +0.026 `defect_miou` (0.3651 vs 0.3391), about 0.8 SL-20 sd.
  * Both ALHVR seeds (0.3599, 0.3704) are above the SL-20 mean.
  * ALHVR is higher on crack (0.287 vs 0.247) and on inactive (0.444 vs 0.431).
  * With n = 2 this is a direction, not an established gain.
* **SA SL-20 vs SL-20:** +0.002 (0.3407 vs 0.3391), no difference at this sample size.
  * SA has a tighter crack IoU (sd 0.002 vs 0.066) and a lower inactive IoU (0.406 vs 0.431).
* **SL-20 s3 is the low outlier** (0.2848). Its crack IoU is 0.133 while its inactive IoU of 0.437 is normal, and it accounts for most of
  the SL-20 spread.
  * Without s3, SL-20 is 0.3527 ± 0.0138.
  * Its best-val checkpoint was at step 4,500. Best-val selection is secondary, and the final step is primary.

### Day-block per-run details (secondary metrics, speed, memory)

Final step unless noted. "best-val" is the step with the best val `defect_miou` (54 images) and the test `defect_miou` of that checkpoint.
The ALHVR ensemble (A+B) is logged as secondary.

| run | GPU | train window (UTC) | steps/s | peak alloc / reserved GiB | 12-defect mIoU | 24-class mIoU | best-val step: test defect_miou | ensemble defect_miou | resumes | params |
|---|---|---|---:|---|---:|---:|---|---:|---:|---:|
| `sl_20pct_s0_cv02` | 2 | 06:12–06:59 | 7.18 | 4.8 / 9.0 | 0.2766 | 0.4782 | 18,500: 0.3410 | – | 0 | 4,981,368 |
| `sl_20pct_s1_cv02` | 2 | 06:59–07:47 | 7.18 | 4.8 / 9.0 | 0.2790 | 0.4779 | 17,000: 0.3363 | – | 0 | 4,981,368 |
| `sl_20pct_s2_cv02` | 2 | 07:47–08:34 | 7.18 | 4.8 / 9.0 | 0.2936 | 0.4845 | 13,500: 0.3516 | – | 0 | 4,981,368 |
| `sl_20pct_s3_cv02` | 0 | 08:15–09:02 | 7.19 | 4.8 / 9.0 | 0.2717 | 0.4940 | 4,500: 0.2571 | – | 0 | 4,981,368 |
| `sl_20pct_s4_cv02` | 4 | 08:24–09:17 | 6.35 | 4.8 / 9.0 | 0.2826 | 0.5040 | 18,000: 0.3467 | – | 0 | 4,981,368 |
| `sa_sl_20pct_s0_cv02` | 0 | 07:09–08:15 | 5.12 | 5.9 / 10.4 | 0.2498 | 0.4677 | 18,000: 0.3294 | – | 0 | 5,440,120 |
| `sa_sl_20pct_s1_cv02` | 4 | 07:09–08:23 | 4.54 | 5.9 / 10.4 | 0.2760 | 0.4784 | 18,500: 0.3421 | – | 0 | 5,440,120 |
| `sa_sl_20pct_s2_cv02` | 5 | 07:09–08:24 | 4.51 | 5.9 / 10.4 | 0.2774 | 0.4697 | 14,000: 0.3517 | – | 0 | 5,440,120 |
| `alhvr_20pct_s1_cv02` | 6 | 06:12–15:52 | 0.58 | 14.7 / 17.8 | 0.2890 | 0.5089 | 16,000: 0.3483 | 0.3733 | 0 | 4,981,368 (×2) |
| `alhvr_20pct_s2_cv02` | 7 | 06:14–15:54 | 0.58 | 14.7 / 17.5 | 0.2897 | 0.4865 | 16,000: 0.3603 | 0.3739 | 0 | 4,981,368 (×2) |

* **Training compute:** 26.8 GPU-hours.
* **Speeds:**
  * The smoke projections held: SL took 47 min (48 min projected) and ALHVR 9.6 h (9.7 h projected).
  * Runs on GPUs 4 and 5 ran 10–12 % slower, because they shared those GPUs with another user's light job (SL-20 s4: 6.35 vs 7.18 steps/s).
* **Configs:** pairwise diffs of `config_used.yaml` show only the intended differences:
  * `seed` and `run_name`;
  * the explicit `data.split_seed: 0` of the s≥1 runs, which equals s0's default, as on gaint;
  * `model.sa_gating` for SA.

## Night block (evening 2026-10-04)

**Code update.**
* `el_code_fe79e19.tgz` was unpacked over the repo; it excludes `data/labeled`, `data/ucf_el`, `.venv` and `experiments`, as stated.
* The previous code is backed up in `/tmp/noob_el/tmp/repo_code_dfa4fd67_backup.tgz`.
* The tarball's own `REVISION` file still said `dfa4fd67…`. As instructed, `REVISION` now reads `fe79e19`.
* The code really is newer than dfa4fd67. 15 files differ, and nothing was removed:
  * new `class_threshold_ce` loss, `configs/ucf_pvs3_v2_classthr.yaml` and `tests/test_class_threshold.py`;
  * a `valtest` split in `evaluate.py` / `runs.py`;
  * night-queue changes;
  * additive trainer checkpoint keys.
* SL / MT / ALHVR training paths are unchanged, and `src/utils/jobs.py` is unchanged, so the cv02 launcher works as-is.
* `__pycache__` was deleted. **pytest: 171 passed, 1 skipped** (the pilot checkpoint), 0 failed.

**Launches** (17:51–17:56, same launcher, watchdog and persistence as the day block, cap 6):
* Opts follow gaint's `night_queue.py` with the `_cv02` suffix:
  * `mt_20pct_s0` and `sl_100pct_s0` use gaint's `*PILOT` opts;
  * their s1/s2 and ALHVR s3/s4 use the seed-only pattern (`seed=k training.total_steps=20000 data.split_seed=0`);
  * MT uses `configs/ssl_mean_teacher.yaml` (`labeled_view: strong`).
* Only GPUs 6 and 7 passed the strict idle rule, because GPUs 0–5 all showed ~370 MiB and 17–26 % util from another user.
  * The approved extras 0, 4 and 5 (util < 50 %) gave five GPUs.
  * The SL-100 lane polls until a sixth qualifies, i.e. an MT GPU after MT ends.
  * GPUs 1–3 were not used: they were never approved.

| run | GPU (admitted by) | train window (UTC) | steps/s | peak alloc / reserved GiB | resumes |
|---|---|---|---:|---|---:|
| `alhvr_20pct_s3_cv02` | 6 (idle rule) | Oct 4 17:51 → Oct 5 03:31 | 0.58 | 14.7 / 17.8 | 0 |
| `alhvr_20pct_s4_cv02` | 7 (idle rule) | 17:53 → 03:32 | 0.58 | 14.7 / 18.7 | 0 |
| `mt_20pct_s0_cv02` | 0 (approved extra, util 28 %) | 17:55 → 20:04 | 2.59 | 9.1 / 10.3 | 0 |
| `mt_20pct_s1_cv02` | 4 (approved extra, util 32 %) | 17:55 → 20:01 | 2.67 | 9.1 / 10.3 | 0 |
| `mt_20pct_s2_cv02` | 5 (approved extra, util 29 %) | 17:55 → 20:01 | 2.67 | 9.1 / 10.3 | 0 |
| `sl_100pct_s0_cv02` | 5 (approved extra, after MT s2) | 20:02 → 20:57 | 6.15 | 4.8 / 9.0 | 0 |
| `sl_100pct_s1_cv02` | 5 | 20:57 → 21:51 | 6.31 | 4.8 / 9.0 | 0 |
| `sl_100pct_s2_cv02` | 5 | 21:51 → 22:45 | 6.31 | 4.8 / 9.0 | 0 |

Peak concurrency was 5 GPU processes: 5 runs from 17:55 to 20:01, then ALHVR ×2 + MT s0 + SL-100 + PV-S3 attempt 1 at 20:02.

**CPU re-score.** This is gaint's `night_queue.rescore_valtest`, exactly:

```
OMP_NUM_THREADS=8 scripts/evaluate.py --run experiments/<run> --weights final --split valtest --device cpu \
    --out experiments/<run>/eval_final_valtest_cpu.json
```

* Weights are `latest.pth` at step 20,000 (MT: EMA teacher; ALHVR: network A), on val + test pooled (104 images), one run at a time.
* It takes about 1 min 40 s per run. `--device cpu` keeps it out of the GPU job count.
* tmux window `n-rescore` runs `/tmp/noob_el/tools/rescore_valtest.sh`, which does the 10 day runs and then each night run as it
  finishes.
* Each JSON (and its `.log`) is stored in the run dir and copied to `results_to_sync/<run>/` and `~/noob/el_results/<run>/`.
* The day block's checkpoints, which I had asked about deleting, made this re-score possible.
* Done 03:36 Oct 5: **18 of 18 runs re-scored, 0 failed** (`/tmp/noob_el/state/rescore.log`).

## Block F (2026-10-07): Mean Teacher on UCF-EL at 5 % and 1 %

**Decisions applied (from the last block).**
* **Logs:** `train.log` is no longer copied to `~/noob/el_results`. All 50 existing log copies there were removed, after checking that each
  has a gzipped copy in `results_to_sync/` (el_results 39 → 28 MB). Logs stay gzipped in `results_to_sync/` only; the launcher now
  writes `train.log.gz` there. Metrics, configs and reports still go to both. Three tiny smoke-run logs exist only in el_results and
  were kept.
* **UCF reporting:** the 4-class defect mean is the headline at every fraction, with the 3-class mean beside it. At 1 % corrosion is
  marked "no labelled examples".
* **Gaint's UCF 20 % runs:** recorded under the UCF table (0.501 / 0.486 / 0.487 vs cv02 0.498 / 0.489 / 0.492). No calibration runs.

**F0. BatchNorm re-estimation (earlier block): it ran.** All 16 variants finished on Oct 6 11:23. Numbers are in Block E.

**F1. Do the MT and ALHVR trainers run with the UCF DeepLab config as it is? No, neither does.**
`build_ucf_data` accepted only `supervised` and `pvs3`.
* **MT: small patch, applied.** In the trainer, `mean_teacher` and `pvs3` are one code path; they differ only in config and data
  pipeline. Patch (`results_to_sync/cv02_patches/cv02_ucf_mean_teacher_train.diff`, +6 / −4 lines, `build_ucf_data` only):
  * `mean_teacher` uses the same two-view UCF data path as `pvs3`;
  * the labelled class pixel counts are computed when the consistency loss is data-driven SemiCE (as BenchmarkEL MT uses).
  * Existing paths are unchanged: UCF supervised has no consistency loss; PV-S3 uses `confidence_ce` / `class_threshold_ce`.
  * New tests in `tests/test_ucf_subsets.py`: MT at 1 % gives 96 labelled + 9,466 unlabelled with 5-class counts (corrosion 0), and the
    PV-S3 path is unchanged. **pytest: 178 passed, 1 skipped.**
* **ALHVR: more than a small patch. Stopped, not run.** It would need:
  * a `forward_dual` for `DeepLabV3PlusWrapper` (clean and perturbed decoder passes on dropout / noise-perturbed encoder features,
    returning logits and a feature map), including **which DeepLab tensor plays U-Net++'s "deep" prototype feature**, a method
    decision;
  * an `alhvr` branch in `build_ucf_data` (single-view labelled and unlabelled streams, hidden masks);
  * adapting or disabling `alhvr_diagnostics.py`, which hard-codes BenchmarkEL crack = 14 and inactive = 11.
* **Unlabelled pools:** `unlabeled_sl5_seed0.txt` (9,084) and `unlabeled_sl1_seed0.txt` (9,466) = train minus the labelled list, in
  train order. That is the committed `unlabeled_sl20_seed0` convention, verified. Synced to `results_to_sync/cv02_patches/`.

**F2. MT recipe on UCF-EL** (`configs/ucf_deeplab.yaml` + `--opts`; the λ = 0 control differs only in `ssl.lambda_final=0`):

| item | value | why |
|---|---|---|
| labelled subset, steps, lr, labelled batch | `sl5` / `sl1`, 95,760 steps, SGD poly lr 0.005, **16** | identical to the SL runs of the same fraction |
| **unlabelled batch** | **16 (batch = 16 labelled + 16 unlabelled)** | the 1:1 ratio of BenchmarkEL MT (4 + 4). The student's BatchNorm batch is half labelled, half unlabelled, as in the BenchmarkEL MT arm, which matters given the Block B / D findings on BN. The UCF config's default of 8 was PV-S3's 2:1 choice, not MT's |
| unlabelled pool | train minus the labelled list | as instructed |
| consistency | SemiCE, data-driven thresholds from the labelled subset's class frequencies (β = γ = 0.5) | BenchmarkEL MT's loss |
| EMA, λ_final | 0.999, 1.5 | BenchmarkEL MT |
| warm-up, ramp | 9,576 + 9,576 steps, linear | the same 10 % + 10 % share of total steps as BenchmarkEL MT (2,000 + 2,000 of 20,000) |
| labelled view | `weak` = shorter side 295, random 256 crop, h/v flips | the UCF SL arms' augmentation (rule: the labelled loss sees the SL arm's augmentation) |
| unlabelled student view | `strong_aug=v2` (jitter p 0.8 ±50 %, grey p 0.2, blur p 0.5; geometry shared with the teacher) | gaint's corrected UCF strong view (v1 was a failed recipe) |
| teacher / evaluation | EMA teacher | as BenchmarkEL MT |

* **Checked:**
  * The supervised loss is plain CE (ignore 128) in MT, in its control and in the SL runs. The class counts only set the SemiCE
    thresholds.
  * The weak labelled view is exactly the SL training transform (same `ucf_geometric` ops, then normalisation).
* **What the λ = 0 control holds fixed:** the student still sees the concatenated 16 + 16 batch (`trainer.py:326`) and evaluation is
  still the EMA teacher. So **MT vs λ = 0 isolates the consistency loss**, while MT vs SL also includes the BN batch composition and
  the EMA weights.
* **SemiCE thresholds** (raw logits, `t_pos = 0.5·freq`, `t_neg = 0.5·(1 − freq)`):
  * 5 %: crack 0.030 / 0.470, contact 0.010 / 0.490, interconnect and corrosion 0.0002 / 0.4998.
  * 1 %: corrosion has freq 0, so t_pos 0 and t_neg 0.5: finite, but the corrosion targets come from a teacher that never saw a
    labelled corrosion pixel.
* **Smoke** (300 steps, GPU 0, alone): runs end to end, 7.9 steps/s, 3.3 / 3.5 GiB.
  The consistency loss is active after warm-up (λ 1.46 at step 100, loss_con 0.062). The smoke folder was removed afterwards;
  its console log is kept as `results_to_sync/smoke_ucf_mt_cv02/train_stdout.log.gz`.
* **GPU rule:** up to two of our runs on a GPU no other user is on (other users' memory < 0.1 GiB), otherwise one per GPU; never where
  another user holds > 4 GiB; cap 8.
* **Order and launch:** a strict-order dispatcher (`tools/dispatch_strict.sh`, queue `queue_ucf_mt.txt`) runs MT 5 % with its λ = 0
  control, paired by seed, then MT 1 % with its control. Each launcher starts only after the previous run is running.
* **At 12:33:** GPUs 1–7 each had another user holding 12–45 GiB, so only GPU 0 was usable. MT 5 % s0 and its control s0 run there,
  stacked, at 4.8 steps/s each: **expected finish ≈ 18:05–18:15 UTC Oct 7**.
* The other 10 runs start as GPUs qualify. If GPU 0 stays the only usable GPU, the two slots each run their remaining runs back to back
  at ≈ 5.6 h per run, so the **last run ends ≈ Oct 8 22:00–22:30 UTC**. Every other GPU that frees up shortens this.
* Post-processing (tmux `mt-post`): crack AP from the EMA teacher, sync, table refresh.

**F3. ALHVR at 5 %: not run.** Step 1 does not allow it (see F1). Nothing was queued.

**F4. MT on UCF-EL: differences** (the main values are in the UCF table above).

<!-- cv02-ucfdiff:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. IoU differences on UCF-EL test, MT arm minus reference. **paired**: same training seed and labelled list, mean ± sd of the per-seed differences (n pairs). **unpaired**: difference of the arm means. At 1 %, judge on the 3-class mean and per class (corrosion has no labelled examples)._

| MT arm | vs | | 4-class mean | 3-class mean | crack | contact | interconnect | corrosion |
|---|---|---|---:|---:|---:|---:|---:|---:|
| UCF MT 5 % | UCF SL 5 % | paired | -0.0913 ± 0.0362 (n 3) | -0.0507 ± 0.0366 (n 3) | -0.0481 ± 0.0162 (n 3) | -0.0386 ± 0.0075 (n 3) | -0.0653 ± 0.0945 (n 3) | -0.2130 ± 0.0845 (n 3) |
| | | unpaired | -0.0913 | -0.0507 | -0.0481 | -0.0386 | -0.0653 | -0.2130 |
| UCF MT 5 % | UCF MT 5 % λ=0 | paired | -0.0688 ± 0.0531 (n 3) | -0.0349 ± 0.0407 (n 3) | -0.0458 ± 0.0175 (n 3) | -0.0345 ± 0.0042 (n 3) | -0.0245 ± 0.1062 (n 3) | -0.1704 ± 0.1008 (n 3) |
| | | unpaired | -0.0688 | -0.0349 | -0.0458 | -0.0345 | -0.0245 | -0.1704 |
| UCF MT 5 % λ=0 | UCF SL 5 % | paired | -0.0225 ± 0.0173 (n 3) | -0.0157 ± 0.0113 (n 3) | -0.0023 ± 0.0048 (n 3) | -0.0041 ± 0.0045 (n 3) | -0.0408 ± 0.0257 (n 3) | -0.0426 ± 0.0560 (n 3) |
| | | unpaired | -0.0225 | -0.0157 | -0.0023 | -0.0041 | -0.0408 | -0.0426 |
| UCF MT 1 % | UCF SL 1 % | paired | -0.0742 ± 0.0275 (n 3) | -0.0990 ± 0.0367 (n 3) | -0.1745 ± 0.0570 (n 3) | -0.1165 ± 0.0438 (n 3) | -0.0059 ± 0.0239 (n 3) | n/a |
| | | unpaired | -0.0742 | -0.0990 | -0.1745 | -0.1165 | -0.0059 | n/a |
| UCF MT 1 % | UCF MT 1 % λ=0 | paired | -0.0521 ± 0.0216 (n 3) | -0.0694 ± 0.0288 (n 3) | -0.1100 ± 0.0342 (n 3) | -0.0820 ± 0.0485 (n 3) | -0.0163 ± 0.0170 (n 3) | n/a |
| | | unpaired | -0.0521 | -0.0694 | -0.1100 | -0.0820 | -0.0163 | n/a |
| UCF MT 1 % λ=0 | UCF SL 1 % | paired | -0.0222 ± 0.0074 (n 3) | -0.0295 ± 0.0099 (n 3) | -0.0645 ± 0.0270 (n 3) | -0.0344 ± 0.0055 (n 3) | +0.0103 ± 0.0076 (n 3) | n/a |
| | | unpaired | -0.0222 | -0.0295 | -0.0645 | -0.0344 | +0.0103 | n/a |

<!-- cv02-ucfdiff:end -->

## Block E (2026-10-06): UCF-EL label sweep, BN re-estimation, reporting, cleanup

**E1. Code patch (the only change to fe79e19's code).**
* `scripts/train.py`: `build_ucf_data` now gets its split files from a new helper, `ucf_subset_files(splits, subset, split_seed)`.
  * `full` → `train.txt`, no unlabelled pool.
  * `sl<N>` → `sl<N>_seed<k>.txt`, with the unlabelled pool `unlabeled_sl<N>_seed<k>.txt` (read by PV-S3 only).
  * Anything else raises.
  * Plus `import re`. The diff is +11 / −7 lines.
* New test `tests/test_ucf_subsets.py`:
  * `sl20` and `full` resolve to the same files as before the patch, and those files still hold the committed lists
    (manifest sha256 and n);
  * `sl<N>` resolution, and the error cases;
  * the 1 % ⊂ 5 % ⊂ 20 % nesting.
* **End-to-end check:** the original and patched `build_ucf_data`, run on the real config, load identical image lists for `sl20`
  supervised (1,912), `sl20` PV-S3 (1,912 + 7,650 unlabelled) and `full` (9,562), all with the same 2,289 test images.
* **pytest: 176 passed, 1 skipped** (the pilot checkpoint).
* **Synced for gaint** in `results_to_sync/cv02_patches/`: `cv02_ucf_subsets_train.diff`, `cv02_test_ucf_subsets.diff`, the two
  lists, `manifest_cv02_subsets.json` and `make_ucf_subsets.py`.

**E2. Nested 5 % / 1 % lists** (`/tmp/noob_el/tools/make_ucf_subsets.py`, written to `data/splits/ucf_el/`).
* 5 % = round(0.05 × 9,562) = 478 images, drawn from `sl20_seed0` (1,912). 1 % = 96 images, drawn from the 5 % list.
* Seed 0, stratified on the per-image defect-presence signature with `stratified_sample`, the same method as `sl20`. Recomputing
  `sl20` this way reproduces its committed sha256 and signature counts.
* Class content before training (full-resolution pixels; images containing the class in brackets):

| list | images | crack | contact | interconnect | corrosion |
|---|---:|---:|---:|---:|---:|
| `train.txt` (100 %) | 9,562 | 53,863,674 (3,788) | 19,900,851 (8,052) | 898,681 (203) | 506,274 (55) |
| `sl20_seed0` (20 %) | 1,912 | 11,171,802 (757) | 4,353,358 (1,609) | 77,259 (41) | 73,115 (11) |
| `sl5_seed0` (5 %) | 478 | 2,749,344 (188) | 883,138 (402) | 16,898 (10) | 22,483 (3) |
| `sl1_seed0` (1 %) | 96 | 553,644 (38) | 132,176 (81) | 1,170 (2) | **0 (0)** |

* **The 1 % list has no corrosion.** Corrosion occurs in 0.6 % of train images, so a stratified 96-image draw expects 0.55
  corrosion images, and rounding gives 0. Its corrosion IoU will be ≈ 0, so the UCF table also reports a 3-class mean.

**E3. UCF-EL label sweep at gaint's step-matched spec:** `configs/ucf_deeplab.yaml`
`seed=k data.labeled_subset=<subset> training.total_steps=95760 training.lr=0.005`, labelled batch 16, seed-0 split lists.
* **GPU rule:** one run per GPU over GPUs 0–7 (GPU 5 included, since "at most 8 at a time"), no stacking, cap 8, never where another
  user holds > 4 GiB. At launch others held 0–1.0 GiB.
* Queue `queue_ucf.txt` on 8 lanes (tmux `u1`–`u8`).
* **Wave 1** was launched 09:47–09:49 on GPUs 0–7: 100 % s0, s1; 5 % s0–s2; 1 % s0–s2. Speeds were 17–20 steps/s, so
  **expected finish ≈ 11:08–11:24 UTC**.
* **Wave 2** (20 % s0–s2) takes the first GPUs to free; **expected finish ≈ 12:30–12:50 UTC**.
* Post-processing (tmux `ucf-post`): CPU AP per run, synced; the table refreshes when each run lands.

<!-- cv02-ucf:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. UCF-EL test (2,289 images, shorter side 295), final step (95,760 steps). IoU / P / R: in-training test, standard convention (ignore 128). Crack AP: `tools/ucf_ap.py`, CPU fp32, 1,000 bins (MT = EMA teacher). **Headline: 4-class defect mean IoU** (crack, contact, interconnect, corrosion) at every label fraction; the **3-class mean** (crack, contact, interconnect) beside it. At 1 % corrosion has **no labelled examples**. mean ± sd over runs._

| arm | labelled | n | **4-class mean** | 3-class mean | crack | contact | interconnect | corrosion | crack P | crack R | crack AP | state |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| UCF SL 100 % | 9,562 | 2 of 2 | **0.5364 ± 0.0042** | 0.4951 ± 0.0017 | 0.675 ± 0.000 | 0.479 ± 0.003 | 0.332 ± 0.002 | 0.660 ± 0.022 | 0.813 ± 0.000 | 0.799 ± 0.000 | 0.851 ± 0.002 | done; done |
| UCF SL 20 % | 1,912 | 3 of 3 | **0.4932 ± 0.0045** | 0.4461 ± 0.0055 | 0.651 ± 0.000 | 0.442 ± 0.001 | 0.245 ± 0.016 | 0.635 ± 0.011 | 0.813 ± 0.001 | 0.766 ± 0.001 | 0.807 ± 0.001 | done; done; done |
| UCF SL 5 % | 478 | 3 of 3 | **0.4146 ± 0.0017** | 0.3953 ± 0.0035 | 0.618 ± 0.003 | 0.404 ± 0.002 | 0.165 ± 0.012 | 0.472 ± 0.013 | 0.801 ± 0.005 | 0.729 ± 0.004 | 0.766 ± 0.002 | done; done; done |
| UCF SL 1 % | 96 | 3 of 3 | **0.2265 ± 0.0017** | 0.3021 ± 0.0023 | 0.529 ± 0.004 | 0.351 ± 0.003 | 0.026 ± 0.007 | no labelled examples | 0.793 ± 0.002 | 0.614 ± 0.006 | 0.690 ± 0.004 | done; done; done |
| UCF MT 5 % | 478 | 3 of 3 | **0.3233 ± 0.0344** | 0.3446 ± 0.0347 | 0.569 ± 0.019 | 0.365 ± 0.007 | 0.100 ± 0.087 | 0.259 ± 0.072 | 0.796 ± 0.007 | 0.666 ± 0.021 | 0.738 ± 0.021 | done; done; done |
| UCF MT 5 % λ=0 | 478 | 3 of 3 | **0.3921 ± 0.0189** | 0.3796 ± 0.0094 | 0.615 ± 0.004 | 0.400 ± 0.003 | 0.124 ± 0.023 | 0.430 ± 0.055 | 0.798 ± 0.006 | 0.729 ± 0.010 | 0.760 ± 0.003 | done; done; done |
| UCF MT 1 % | 96 | 3 of 3 | **0.1523 ± 0.0265** | 0.2031 ± 0.0353 | 0.355 ± 0.055 | 0.235 ± 0.046 | 0.020 ± 0.018 | no labelled examples | 0.543 ± 0.141 | 0.518 ± 0.022 | 0.511 ± 0.077 | done; done; done |
| UCF MT 1 % λ=0 | 96 | 3 of 3 | **0.2044 ± 0.0058** | 0.2725 ± 0.0078 | 0.465 ± 0.024 | 0.317 ± 0.002 | 0.036 ± 0.001 | no labelled examples | 0.661 ± 0.038 | 0.610 ± 0.009 | 0.628 ± 0.020 | done; done; done |

**UCF SL 20 % on two machines (same spec, no calibration runs):** gaint `ucf_sl20_stepmatched_s0–s2` 4-class mean 0.501, 0.486, 0.487 (mean 0.491); cv02 0.498, 0.489, 0.492 (mean 0.493 ± 0.004).

<!-- cv02-ucf:end -->

**E4. BatchNorm re-estimation (no training): numbers only.**

<!-- cv02-bn:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC from `experiments/_bn_recal/` (`/tmp/noob_el/tools/bn_recal.py`) and `experiments/_ap_diagnostic/` (unmodified). Final-step weights frozen; BatchNorm running statistics re-estimated by forward passes only (cumulative average, evaluation view, BN layers alone in train mode) on (a) the run's own 95 labelled images or (b) all 478 train images. CPU fp32; AP over 1,000 bins. mean ± sd over runs._

**test**

| arm | BN statistics | n | defect_miou | crack IoU | inactive IoU | crack AP | inactive AP |
|---|---|---:|---:|---:|---:|---:|---:|
| SL-20 b8 | unmodified | 3 | 0.3615 ± 0.0081 | 0.296 ± 0.001 | 0.427 ± 0.017 | 0.494 ± 0.004 | 0.618 ± 0.013 |
| SL-20 b8 | re-estimated, own 95 labelled | 3 | 0.3623 ± 0.0070 | 0.293 ± 0.006 | 0.432 ± 0.017 | 0.495 ± 0.004 | 0.623 ± 0.011 |
| SL-20 b8 | re-estimated, 478 train | 3 | 0.3577 ± 0.0083 | 0.284 ± 0.006 | 0.431 ± 0.018 | 0.492 ± 0.004 | 0.613 ± 0.014 |
| SL-20 | unmodified | 5 | 0.3388 ± 0.0328 | 0.247 ± 0.066 | 0.430 ± 0.013 | 0.464 ± 0.026 | 0.637 ± 0.018 |
| SL-20 | re-estimated, own 95 labelled | 5 | 0.3463 ± 0.0264 | 0.246 ± 0.060 | 0.447 ± 0.018 | 0.466 ± 0.021 | 0.652 ± 0.015 |
| SL-20 | re-estimated, 478 train | 5 | 0.3454 ± 0.0272 | 0.243 ± 0.061 | 0.448 ± 0.019 | 0.464 ± 0.022 | 0.641 ± 0.015 |
| MT-20 λ=0 (unmodified, reference) | unmodified | 3 | 0.3648 ± 0.0181 | 0.269 ± 0.025 | 0.461 ± 0.014 | 0.472 ± 0.002 | 0.665 ± 0.025 |

**val+test**

| arm | BN statistics | n | defect_miou | crack IoU | inactive IoU | crack AP | inactive AP |
|---|---|---:|---:|---:|---:|---:|---:|
| SL-20 b8 | unmodified | 3 | 0.3392 ± 0.0073 | 0.273 ± 0.001 | 0.406 ± 0.014 | 0.459 ± 0.001 | 0.589 ± 0.006 |
| SL-20 b8 | re-estimated, own 95 labelled | 3 | 0.3338 ± 0.0060 | 0.267 ± 0.006 | 0.401 ± 0.017 | 0.459 ± 0.001 | 0.586 ± 0.019 |
| SL-20 b8 | re-estimated, 478 train | 3 | 0.3213 ± 0.0095 | 0.256 ± 0.006 | 0.387 ± 0.024 | 0.457 ± 0.002 | 0.565 ± 0.028 |
| SL-20 | unmodified | 5 | 0.3145 ± 0.0228 | 0.232 ± 0.048 | 0.397 ± 0.012 | 0.434 ± 0.020 | 0.599 ± 0.013 |
| SL-20 | re-estimated, own 95 labelled | 5 | 0.3051 ± 0.0186 | 0.226 ± 0.042 | 0.384 ± 0.009 | 0.433 ± 0.016 | 0.595 ± 0.009 |
| SL-20 | re-estimated, 478 train | 5 | 0.2918 ± 0.0209 | 0.220 ± 0.041 | 0.364 ± 0.008 | 0.431 ± 0.016 | 0.573 ± 0.010 |
| MT-20 λ=0 (unmodified, reference) | unmodified | 3 | 0.3380 ± 0.0115 | 0.251 ± 0.014 | 0.425 ± 0.011 | 0.440 ± 0.003 | 0.630 ± 0.019 |

<!-- cv02-bn:end -->

**E6. Cleanup:** removed only the five stopped folders (`alhvr_20pct_lam0_s{1,2,3}_cv02_stopped`,
`sl_10pct_b8_s{0,1}_cv02_stopped_prio`, 157 MB). All 33 final checkpoints are kept.

## Block D (2026-10-06): average precision, UCF-EL label sweep

**D1. Pixel-level average precision** (no training) for every finished BenchmarkEL checkpoint on cv02: 33 runs over 10 arms.
The 200-step smoke runs are excluded; their checkpoints were deleted on Oct 4.

<!-- cv02-ap:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC from `experiments/_ap_diagnostic/<run>.json` (`/tmp/noob_el/tools/ap_diagnostic.py`). Final-step weights (MT = EMA teacher, ALHVR = network A), CPU fp32. AP from the softmax probability of the class, PR curve over 1,000 equal probability bins. The binned AP is slightly low against exact AP (checked on `sl_20pct_s0_cv02`: crack −0.001, inactive −0.005). Crack IoU / P / R are at argmax (standard convention). mean ± sd over runs, n = runs._

**test (50 images)**

| arm | n | crack AP | inactive AP | mean AP | crack IoU | crack P | crack R |
|---|---:|---:|---:|---:|---:|---:|---:|
| SL-20 | 5 | 0.464 ± 0.026 | 0.637 ± 0.018 | 0.550 ± 0.020 | 0.247 ± 0.066 | 0.276 ± 0.079 | 0.717 ± 0.013 |
| SA SL-20 | 3 | 0.452 ± 0.014 | 0.627 ± 0.039 | 0.539 ± 0.021 | 0.275 ± 0.002 | 0.314 ± 0.004 | 0.690 ± 0.012 |
| ALHVR | 4 | 0.477 ± 0.004 | 0.676 ± 0.020 | 0.577 ± 0.011 | 0.289 ± 0.005 | 0.328 ± 0.007 | 0.710 ± 0.005 |
| MT-20 | 3 | 0.470 ± 0.003 | 0.666 ± 0.017 | 0.568 ± 0.010 | 0.276 ± 0.002 | 0.309 ± 0.005 | 0.725 ± 0.015 |
| SL-100 | 3 | 0.429 ± 0.013 | 0.616 ± 0.016 | 0.523 ± 0.013 | 0.270 ± 0.005 | 0.305 ± 0.008 | 0.707 ± 0.016 |
| MT-20 λ=0 | 3 | 0.472 ± 0.002 | 0.665 ± 0.025 | 0.569 ± 0.013 | 0.269 ± 0.025 | 0.302 ± 0.031 | 0.715 ± 0.008 |
| SL-20 b8 | 3 | 0.494 ± 0.004 | 0.618 ± 0.013 | 0.556 ± 0.006 | 0.296 ± 0.001 | 0.333 ± 0.002 | 0.728 ± 0.008 |
| SL-100 b8 | 3 | 0.450 ± 0.001 | 0.632 ± 0.019 | 0.541 ± 0.010 | 0.279 ± 0.006 | 0.310 ± 0.007 | 0.734 ± 0.010 |
| SL-10 b8 | 3 | 0.485 ± 0.012 | 0.619 ± 0.016 | 0.552 ± 0.014 | 0.281 ± 0.021 | 0.316 ± 0.025 | 0.721 ± 0.009 |
| ALHVR λ=0 | 3 | 0.468 ± 0.016 | 0.668 ± 0.011 | 0.568 ± 0.010 | 0.258 ± 0.042 | 0.287 ± 0.051 | 0.724 ± 0.004 |

**val+test (104 images)**

| arm | n | crack AP | inactive AP | mean AP | crack IoU | crack P | crack R |
|---|---:|---:|---:|---:|---:|---:|---:|
| SL-20 | 5 | 0.434 ± 0.020 | 0.599 ± 0.013 | 0.516 ± 0.013 | 0.232 ± 0.048 | 0.256 ± 0.057 | 0.721 ± 0.013 |
| SA SL-20 | 3 | 0.421 ± 0.015 | 0.549 ± 0.057 | 0.485 ± 0.036 | 0.248 ± 0.007 | 0.278 ± 0.007 | 0.698 ± 0.011 |
| ALHVR | 4 | 0.445 ± 0.003 | 0.642 ± 0.021 | 0.544 ± 0.011 | 0.269 ± 0.004 | 0.302 ± 0.005 | 0.710 ± 0.006 |
| MT-20 | 3 | 0.438 ± 0.006 | 0.630 ± 0.015 | 0.534 ± 0.010 | 0.254 ± 0.002 | 0.280 ± 0.005 | 0.728 ± 0.019 |
| SL-100 | 3 | 0.400 ± 0.010 | 0.583 ± 0.019 | 0.491 ± 0.014 | 0.248 ± 0.007 | 0.275 ± 0.011 | 0.715 ± 0.018 |
| MT-20 λ=0 | 3 | 0.440 ± 0.003 | 0.630 ± 0.019 | 0.535 ± 0.008 | 0.251 ± 0.014 | 0.278 ± 0.018 | 0.716 ± 0.007 |
| SL-20 b8 | 3 | 0.459 ± 0.001 | 0.589 ± 0.006 | 0.524 ± 0.003 | 0.273 ± 0.001 | 0.303 ± 0.001 | 0.729 ± 0.004 |
| SL-100 b8 | 3 | 0.421 ± 0.002 | 0.610 ± 0.015 | 0.515 ± 0.008 | 0.258 ± 0.004 | 0.284 ± 0.004 | 0.740 ± 0.012 |
| SL-10 b8 | 3 | 0.448 ± 0.007 | 0.591 ± 0.012 | 0.519 ± 0.009 | 0.262 ± 0.012 | 0.294 ± 0.014 | 0.711 ± 0.009 |
| ALHVR λ=0 | 3 | 0.437 ± 0.011 | 0.635 ± 0.005 | 0.536 ± 0.003 | 0.244 ± 0.028 | 0.268 ± 0.033 | 0.726 ± 0.006 |

<!-- cv02-ap:end -->

**D1 observations** (test; val+test agrees in direction; 3–5 runs per arm, 50 test images):
* **Crack AP:** SL-20 b8 is the highest (0.494 ± 0.004), then SL-10 b8 (0.485) and ALHVR (0.477). MT-20, MT λ=0 and ALHVR λ=0 are at
  0.468–0.472 and SL-20 at 0.464. SL-100 is lowest (0.429), and SL-100 b8 is at 0.450.
  * For crack, a larger *labelled* batch helps the ranking quality at least as much as the SSL pipelines do.
* **Inactive AP separates the arms differently.** Every arm whose BatchNorm batch contains unlabelled images is at 0.665–0.676:
  MT-20, MT λ=0, ALHVR and ALHVR λ=0. Every supervised arm is at 0.616–0.637, **including SL-20 b8 (0.618)**.
  * The gain survives λ = 0, so it does not come from the unlabelled loss.
  * It also does not come from batch size alone: SL-20 b8 has BN batch 8 and does not get it.
  * It goes with **unlabelled images passing through the forward pass**, in BatchNorm statistics or in the two-stream data pipeline.
    This refines the Block B reading (BN batch 8 explains the argmax defect_miou gain), which held for crack and the headline but
    not for inactive.
* **Mean AP:** ALHVR 0.577 > MT λ=0 0.569 ≈ MT-20 0.568 ≈ ALHVR λ=0 0.568 > SL-20 b8 0.556 > SL-10 b8 0.552 > SL-20 0.550 >
  SL-100 b8 0.541 > SA SL-20 0.539 > SL-100 0.523.
* **SL-100 stays lowest on both APs.** More labels do not help at 20k steps, as with defect_miou.

**D2. UCF-EL label sweep: stopped at the prerequisite check, as instructed. Nothing was launched.**

| needed | on cv02 |
|---|---|
| UCF-EL data | present: `data/ucf_el` → `/tmp/noob_el/datasets/UCF-EL-Defect/training` (9,562 train / 2,289 test); committed split lists and `manifest.json`, all sha256 verified on Oct 4 |
| UCF config | present: `configs/ucf_deeplab.yaml` (smp DeepLabV3+ R50, ImageNet; SGD momentum 0.9, wd 1e-4, poly 0.9; shorter side 295 → random 256 crop; h/v flips; CE, ignore 128). The R50 ImageNet weights are in `HF_HOME` |
| gaint `ucf_sl20_stepmatched` budget | present, in `scripts/night_queue.py`: `seed=k data.labeled_subset=sl20 training.total_steps=95760 training.lr=0.005`, **labelled batch 16** (config), seeds 0–2, 1,912 labelled images |
| **100 % runs** | supported (`data.labeled_subset=full`, `train.txt`, 9,562) |
| **5 % and 1 % subsets** | **not supported by the code.** `scripts/train.py` `build_ucf_data` accepts only `labeled_subset` ∈ {`sl20`, `full`} (lines 354–361) and raises otherwise. No 5 % / 1 % list exists |

The gaint `ucf_sl20_stepmatched` results (the 20 % point of the sweep) are not on cv02, so a within-machine sweep would also need them.

## Block A/B/C (2026-10-05 evening): precision diagnostic, batch-size and loss-off controls

**A. Precision diagnostic** (no training, CPU, 17:31–18:00): `reports/precision_diagnostic.md`, on all 18 existing final checkpoints.
Synced to `results_to_sync/precision_diagnostic/` and `~/noob/el_results/precision_diagnostic/`.
* **Crack is over-predicted in every arm.** On test, precision is 0.30 ± 0.04 at recall 0.72, and relaxed precision (2 px) is 0.67.
  Of the false-positive crack pixels, 85 % are GT background, 53 % lie within 2 px of a true crack and 78 % within 5 px.
* **A crack-logit bias chosen on val** (b = 1–1.75) raises test defect_miou in 15 of 18 runs:
  SL-20 +0.019, MT-20 +0.016, MT-20 λ=0 +0.027, ALHVR +0.020, but SL-100 −0.003.
  * At that bias the order is ALHVR 0.393 ≈ MT λ=0 0.392 > MT 0.381 > SL-20 0.358 > SL-100 0.338.
  * The SSL arms' lead over SL-20 survives calibration.
* **An inactive bias chosen on val lowers test in every arm** (−0.010 to −0.033). This is a val/test mismatch: at b = 0, inactive
  precision is 0.31 on val against 0.66 on test.
* **The joint log-weight adjustment** gives +0.004 to +0.013.

**B. Training: 12 runs in a priority queue** (`/tmp/noob_el/state/queue_b.txt`, tmux windows `b1`–`b6`), all at 20,000 steps on
the seed-0 split. The order follows your priority:

| # | arm | runs | opts beyond the paired reference run |
|---|---|---|---|
| 1 | **ALHVR λ=0** (B4) | `alhvr_20pct_lam0_s{1,2,3}_cv02` | `alhvr.lambda_max=0`, otherwise the `alhvr_20pct_sK_cv02` opts |
| 2 | **SL-20 batch 8** (B1) | `sl_20pct_b8_s{0,1,2}_cv02` | `training.labeled_batch_size=8`, otherwise `sl_20pct_sK_cv02` |
| 3 | **SL-100 batch 8** (B1) | `sl_100pct_b8_s{0,1,2}_cv02` | `training.labeled_batch_size=8`, otherwise `sl_100pct_sK_cv02` |
| 4 | **SL-10 batch 8** (B2) | `sl_10pct_b8_s{0,1,2}_cv02` | `data.labeled_fraction=0.1 training.labeled_batch_size=8`, otherwise SL-20 |

* **Seeds:** ALHVR λ=0 uses training seeds 1–3, so each run pairs with an existing cv02 ALHVR seed (cv02 has ALHVR s1–s4, no s0).
  The SL batch-8 arms use seeds 0–2, pairing with SL-20 / MT-20 s0–s2.
* **"The same strong labelled view the MT student uses":** it is already the SL arms' training augmentation.
  * `get_strong_augmentation` = `_geometric_ops` + `_strong_photometric_ops(p_blur 0.3, p_jitter 0.4, p_noise 0.3)` + normalise.
  * The MT student's labelled view = `get_geometric_augmentation` (the same `_geometric_ops`) followed by `get_strong_photometric`
    (the same `_strong_photometric_ops`).
  * The labelled batch stream is the same function of (seed, step).
  * So B1/B2 change only the batch size, and **B3 (SL-20, batch 4, that view) is the existing SL-20 arm**
    (`sl_20pct_s0..s4_cv02`). It was not re-run (your answer: priority list only).
* **ALHVR λ=0: the unlabelled images still go through the forward pass exactly as in the normal ALHVR runs. Only the loss weight
  changes.**
  * `ALHVRTrainer.compute_losses` runs `forward_dual` (clean + perturbed pass) of **both** networks on the concatenated
    4 labelled + 4 unlabelled batch in train mode, and computes `alhvr_unsup_losses` (γ, regions, CG-CPCL, DTCT) whatever the weight.
  * The weight enters only as `loss_x = sup_x + λ(t) · unsup_x`, with λ(t) = `lambda_max` · exp(−5 (1 − t/T)²) = 0 for
    `lambda_max = 0`. There is no short-circuit on λ in the code.
  * So BatchNorm statistics, the perturbations and the region diagnostics (`regions.csv`) are as in ALHVR.
  * The **logged** `ce/cos/mse/ent` are the raw, unweighted terms and stay non-zero by design, which shows they are still computed.
    What is exactly 0 is λ and the weighted contribution `loss_x − sup_x`, for both networks. The automatic check is at the end of
    the differences block below.
* **GPUs** (your rule for this block):
  * GPUs 6 and 7 are approved, with up to two of our runs each when memory fits. They hold another user's 7.0 / 4.7 GB with bursty
    load, so they are admitted at util < 90 % at launch.
  * GPUs 0–5 are added when relatively idle: util < 10 % at launch, other users' memory allowed.
  * Gaint's memory guard (free ≥ peak + 2 GiB) and the cap of 6 apply. Each GPU gets its own launch queue (`launch_cv02.py
    --stack 6:2,7:2 --util_idle_only --extra_gpus 6,7 --extra_max_util 90`).
* **Placement at 17:27–17:35 UTC:**
  * GPU 6: ALHVR λ=0 s1 + s2;
  * GPU 7: ALHVR λ=0 s3 + SL-20 b8 s0;
  * lanes 5–6 (SL-20 b8 s1, s2) wait for a free slot.
* **Measured speeds (17:47), stacked:** ALHVR λ=0 0.24 steps/s each (0.58 alone), SL-20 b8 1.53 steps/s.
* **Expected finish (UTC):**
  * ALHVR λ=0 s1 / s2 / s3 ≈ Oct 6 16:10 / 16:25 / 16:05;
  * SL-20 b8 s0 ≈ 21:15 today.
  * If GPUs 0–5 stay busy, the 9 SL batch-8 runs share GPU 7's second slot at ≈ 3.6 h each and end ≈ Oct 7 03:00. Any of GPUs
    0–5 that drops below 10 % util is taken at once (lanes 5–6 poll every 60 s).
  * About 42 GPU-hours of work on 2 GPUs.

**Restart record (19:10–19:25 UTC, your decisions at ≈ 19:05).** No run was resumed from a checkpoint.
* **GPU rules from 19:12:**
  * GPUs 0–4 are approved with one of our runs each, no stacking. GPUs 6 and 7 are approved with two each.
  * **Never start a run where another user holds more than 4 GiB.** This is enforced in the launcher (`--max_other_gib 4`): other
    users' memory = `memory.used` minus our processes' `used_memory`. At 19:10 another user held 0.41 GiB on each of GPUs 0–5 and
    ≈ 0 on 6 and 7.
  * The global cap of 6 cannot hold under this allocation: the three old copies plus three relaunches plus two SL runs is 8 during
    the overlap. Your per-GPU allocation, 9 slots (0–4 + 2 × 6 + 2 × 7), replaces it (`--max_jobs 9`).
* **ALHVR λ=0 relaunched fresh, one per GPU:** `alhvr_20pct_lam0_r2_s{1,2,3}_cv02` on GPUs 0, 1, 2, from 19:12–19:15, with
  identical opts.
  * At step 200 they ran at 0.50 steps/s, projecting ≈ Oct 6 06:15 / 06:12 / 06:20.
  * The original copies, stacked two per GPU on GPUs 6 and 7, ran at 0.24 steps/s, projecting ≈ Oct 6 16:10.
  * **The relaunches won by ≈ 10 h**, so the originals were stopped at 19:23 at steps 1,700 / 1,650 / 1,600 (SIGTERM through the
    launcher, no restart, nothing synced).
  * The originals are kept as `experiments/alhvr_20pct_lam0_s{1,2,3}_cv02_stopped`. They had no `latest.pth`, only an early
    `best.pth`, so they cannot be resumed.
  * **The ALHVR λ=0 arm is the `_r2_` runs.**
* **The old block-B lanes were stopped** (only their bash loops; their running runs continue):
  * SL-20 b8 s0 continues on GPU 7 and SL-20 b8 s1 on GPU 5.
  * GPU 5 was taken at ≈ 18:00 under the previous rule ("relatively idle"). It is not in the new approved list, so it gets no new
    runs.
  * SL-20 b8 s2's launcher was still waiting and never started a run; it was stopped and the run requeued.
* **Remaining batch-8 runs** (queue `queue_b2.txt`, tmux windows `q2-1`–`q2-6`, GPUs 3, 4, 6, 7): SL-20 b8 s2 → GPU 3 (19:12),
  SL-100 b8 s0 → GPU 4 (19:12), SL-100 b8 s1 and s2 → GPU 6 (19:23, stacked). SL-10 b8 s0–s2 follow as slots free.

**Priority correction (19:35).**
* The six pull-lanes polled independently, so when GPU 6/7 slots opened at 19:23, **SL-10 b8 s0 and s1 started ahead of SL-100 b8
  s0 and s2**, against your priority. SL-100 b8 s0 was also held at the cap on an idle GPU 4.
* Both SL-10 runs (≈ step 1,100–1,200, only an early `best.pth`) were stopped and archived as `sl_10pct_b8_s{0,1}_cv02_stopped_prio`.
* The lane loops were stopped. SL-100 b8 s0 started on GPU 4 at 19:36 and s2 on GPU 6 at 19:36.
* SL-10 b8 s0 → s1 → s2 now come from a strict-order dispatcher (`/tmp/noob_el/tools/dispatch_sl10.sh`). Each launcher starts only
  after the previous run is running. **The SL-10 runs start fresh; nothing is resumed.**

**Placement and expected finish (UTC), measured at 19:37:**

| GPU | run | steps/s | expected finish |
|---|---|---:|---|
| 0 | `alhvr_20pct_lam0_r2_s1_cv02` | 0.50 | Oct 6 ≈ 06:17 |
| 1 | `alhvr_20pct_lam0_r2_s2_cv02` | 0.50 | Oct 6 ≈ 06:16 |
| 2 | `alhvr_20pct_lam0_r2_s3_cv02` | 0.50 | Oct 6 ≈ 06:23 |
| 5 | `sl_20pct_b8_s1_cv02` (started under the previous rule) | 3.2 | ≈ 19:53 |
| 7 | `sl_20pct_b8_s0_cv02` (stacked with SL-100 b8 s1) | 1.7 | ≈ 21:00 |
| 3 | `sl_20pct_b8_s2_cv02` | 3.1 | ≈ 21:05 |
| 4 | `sl_100pct_b8_s0_cv02` | 3.3 | ≈ 21:15 |
| 7 | `sl_100pct_b8_s1_cv02` (stacked until ≈ 21:00) | 1.7 | ≈ 22:00–22:40 |
| 6 | `sl_100pct_b8_s2_cv02` (SL-10 b8 s0 will stack here) | 3.7 → ≈ 1.7 | ≈ 21:10–22:30 |
| next | `sl_10pct_b8_s0..s2_cv02` (strict order, as slots free) | 1.7–3.3 | ≈ 23:00 – Oct 6 00:30 |

**Block B is expected to complete ≈ Oct 6 06:25 UTC**, bound by the three ALHVR λ=0 runs.

**Block B result** (all 12 runs finished rc 0 between 19:53 Oct 5 and 06:18 Oct 6; no restarts; all re-scored on val+test and synced).
Test defect_miou, mean ± sd over 3 seeds; val+test in brackets:

| arm | gradient batch | BN batch (images per forward) | unlabelled loss | test (val+test) |
|---|---:|---|---|---|
| SL-20 (batch 4, 5 seeds) | 4 | 4 labelled | – | 0.3391 ± 0.0326 (0.3145) |
| **SL-20 b8** | 8 | 8 labelled | – | **0.3623 ± 0.0076** (0.3392) |
| SL-10 b8 | 8 | 8 labelled | – | 0.3530 ± 0.0184 (0.3351) |
| SL-100 (batch 4) | 4 | 4 labelled | – | 0.3402 ± 0.0057 (0.2970) |
| SL-100 b8 | 8 | 8 labelled | – | 0.3435 ± 0.0057 (0.3127) |
| MT-20 λ=0, student (CPU) | 4 | 4 labelled + 4 unlabelled | 0 | 0.3696 ± 0.0133 (0.3416) |
| MT-20 λ=0, teacher | 4 | 4 + 4 | 0 | 0.3653 ± 0.0183 (0.3380) |
| MT-20 | 4 | 4 + 4 | yes | 0.3648 ± 0.0071 (0.3407) |
| **ALHVR λ=0** | 4 | 4 + 4, two networks | 0 | **0.3642 ± 0.0159** (0.3389) |
| ALHVR | 4 | 4 + 4, two networks | yes | 0.3742 ± 0.0128 (0.3483) |

* **Batch 8 reproduces MT-20.** SL-20 b8 vs MT-20 (paired, seeds 0–2): −0.0026 ± 0.0017 on test, −0.0015 ± 0.0078 on val+test.
  Against SL-20 batch 4 it is +0.023 on test (unpaired; paired over seeds 0–2, without the s3 outlier: +0.010 ± 0.019).
* **ALHVR's unlabelled loss adds little.** ALHVR λ=0 vs ALHVR (paired, seeds 1–3): −0.0046 ± 0.0234 on test, −0.0035 ± 0.0189 on
  val+test; unpaired −0.010. ALHVR λ=0 sits with MT-20 and SL-20 b8.
* **The common factor is the BatchNorm batch of 8, not the gradient batch or the unlabelled loss.**
  * The MT λ=0 student has a gradient batch of 4 but a BN batch of 8 (4 unlabelled images forward-only). It reaches 0.370, the same
    as SL-20 b8 (gradient 8, BN 8), MT-20, MT λ=0 and ALHVR λ=0 (0.362–0.370).
  * Every arm with a BN batch of 4 is at 0.339–0.343: SL-20, SL-100 and SA SL-20.
  * Untested alternative: the BN batch's *content* (more images) rather than its *size* (see open items).
* **SL-10 b8** (47 labelled images) is at or above SL-20 batch 4 (95): +0.001 ± 0.004 test / +0.013 ± 0.001 val+test, paired.
* **SL-100 b8 gains little from batch 8** (+0.003 test, +0.016 val+test, unpaired), unlike SL-20/SL-10. It stays below MT-20 by
  −0.021 ± 0.007 test (paired). Not explained here.
* **Caveats:** 3 seeds per arm and 50 test images. ALHVR's +0.010 over ALHVR λ=0 is within one sd.

**C.** The per-arm table at the top now includes the new arms. Their differences against SL-20 (batch 4), MT-20 and ALHVR follow:

<!-- cv02-diff:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. defect_miou differences, new arm minus reference arm. **paired**: same training seed (same seed-0 split), mean ± sd of the per-seed differences over the common seeds (n pairs); shown when n >= 2. **unpaired**: difference of the arm means, with each arm's sd and n (new / reference)._

**test (50 images, in-training final step)**

| new arm | vs | paired: mean ± sd (n) | unpaired: Δ means (sd new / sd ref, n new / n ref) |
|---|---|---:|---:|
| SL-20 b8 | SL-20 | +0.0102 ± 0.0192 (n 3; seeds 0,1,2) | +0.0232 (0.0076 / 0.0326, n 3 / 5) |
| SL-20 b8 | MT-20 | -0.0026 ± 0.0017 (n 3; seeds 0,1,2) | -0.0026 (0.0076 / 0.0071, n 3 / 3) |
| SL-20 b8 | ALHVR | -0.0063 ± 0.0008 (n 2; seeds 1,2) | -0.0120 (0.0076 / 0.0128, n 3 / 4) |
| SL-100 b8 | SL-20 | -0.0085 ± 0.0217 (n 3; seeds 0,1,2) | +0.0044 (0.0057 / 0.0326, n 3 / 5) |
| SL-100 b8 | MT-20 | -0.0214 ± 0.0066 (n 3; seeds 0,1,2) | -0.0214 (0.0057 / 0.0071, n 3 / 3) |
| SL-100 b8 | ALHVR | -0.0249 ± 0.0087 (n 2; seeds 1,2) | -0.0307 (0.0057 / 0.0128, n 3 / 4) |
| SL-10 b8 | SL-20 | +0.0010 ± 0.0042 (n 3; seeds 0,1,2) | +0.0139 (0.0184 / 0.0326, n 3 / 5) |
| SL-10 b8 | MT-20 | -0.0118 ± 0.0172 (n 3; seeds 0,1,2) | -0.0118 (0.0184 / 0.0071, n 3 / 3) |
| SL-10 b8 | ALHVR | -0.0066 ± 0.0149 (n 2; seeds 1,2) | -0.0212 (0.0184 / 0.0128, n 3 / 4) |
| ALHVR λ=0 | SL-20 | +0.0300 ± 0.0307 (n 3; seeds 1,2,3) | +0.0251 (0.0159 / 0.0326, n 3 / 5) |
| ALHVR λ=0 | MT-20 | +0.0110 ± 0.0114 (n 2; seeds 1,2) | -0.0007 (0.0159 / 0.0071, n 3 / 3) |
| ALHVR λ=0 | ALHVR | -0.0046 ± 0.0234 (n 3; seeds 1,2,3) | -0.0100 (0.0159 / 0.0128, n 3 / 4) |

**val+test (104 images, CPU re-score)**

| new arm | vs | paired: mean ± sd (n) | unpaired: Δ means (sd new / sd ref, n new / n ref) |
|---|---|---:|---:|
| SL-20 b8 | SL-20 | +0.0172 ± 0.0187 (n 3; seeds 0,1,2) | +0.0247 (0.0073 / 0.0228, n 3 / 5) |
| SL-20 b8 | MT-20 | -0.0015 ± 0.0078 (n 3; seeds 0,1,2) | -0.0015 (0.0073 / 0.0068, n 3 / 3) |
| SL-20 b8 | ALHVR | -0.0036 ± 0.0088 (n 2; seeds 1,2) | -0.0091 (0.0073 / 0.0138, n 3 / 4) |
| SL-100 b8 | SL-20 | -0.0093 ± 0.0153 (n 3; seeds 0,1,2) | -0.0018 (0.0057 / 0.0228, n 3 / 5) |
| SL-100 b8 | MT-20 | -0.0280 ± 0.0043 (n 3; seeds 0,1,2) | -0.0280 (0.0057 / 0.0068, n 3 / 3) |
| SL-100 b8 | ALHVR | -0.0289 ± 0.0047 (n 2; seeds 1,2) | -0.0356 (0.0057 / 0.0138, n 3 / 4) |
| SL-10 b8 | SL-20 | +0.0130 ± 0.0011 (n 3; seeds 0,1,2) | +0.0205 (0.0119 / 0.0228, n 3 / 5) |
| SL-10 b8 | MT-20 | -0.0056 ± 0.0108 (n 3; seeds 0,1,2) | -0.0056 (0.0119 / 0.0068, n 3 / 3) |
| SL-10 b8 | ALHVR | +0.0004 ± 0.0062 (n 2; seeds 1,2) | -0.0133 (0.0119 / 0.0138, n 3 / 4) |
| ALHVR λ=0 | SL-20 | +0.0288 ± 0.0184 (n 3; seeds 1,2,3) | +0.0244 (0.0121 / 0.0228, n 3 / 5) |
| ALHVR λ=0 | MT-20 | +0.0070 ± 0.0059 (n 2; seeds 1,2) | -0.0018 (0.0121 / 0.0068, n 3 / 3) |
| ALHVR λ=0 | ALHVR | -0.0035 ± 0.0189 (n 3; seeds 1,2,3) | -0.0094 (0.0121 / 0.0138, n 3 / 4) |

**ALHVR λ=0 log check** (weighted unlabelled contribution = loss − sup; every logged step): `alhvr_20pct_lam0_r2_s1_cv02`: 400 logged steps (full precision, `metrics.json` train_curve): lambda = 0, loss_a − sup_a = 0 and loss_b − sup_b = 0 exactly at all but **0**; raw unlabelled terms (ce/cos/mse/ent, unweighted) non-zero at 400 of 400 (computed as in normal ALHVR, weight 0); `alhvr_20pct_lam0_r2_s2_cv02`: 400 logged steps (full precision, `metrics.json` train_curve): lambda = 0, loss_a − sup_a = 0 and loss_b − sup_b = 0 exactly at all but **0**; raw unlabelled terms (ce/cos/mse/ent, unweighted) non-zero at 400 of 400 (computed as in normal ALHVR, weight 0); `alhvr_20pct_lam0_r2_s3_cv02`: 400 logged steps (full precision, `metrics.json` train_curve): lambda = 0, loss_a − sup_a = 0 and loss_b − sup_b = 0 exactly at all but **0**; raw unlabelled terms (ce/cos/mse/ent, unweighted) non-zero at 400 of 400 (computed as in normal ALHVR, weight 0).

<!-- cv02-diff:end -->

## MT EMA control and teacher / student split (2026-10-05)

**Question:** how much of MT-20's gain over SL-20 comes from the EMA teacher, and how much from the unlabelled loss?

**λ = 0 control:** `mt_20pct_lam0_s{0,1,2}_cv02`, launched 06:11 on GPUs 1, 2, 3 (strict idle rule) with the same launcher, watchdog and
persistence.
* The opts are exactly those of `mt_20pct_sK_cv02` plus `ssl.lambda_final=0`. The consistency weight is then 0 at every step: the
  2,000-step warm-up and the 2,000-step ramp both scale `lambda_final`.
* **Config check:** `diff experiments/mt_20pct_sK_cv02/config_used.yaml experiments/mt_20pct_lam0_sK_cv02/config_used.yaml` shows only
  `run_name` and `ssl.lambda_final: 1.5 → 0`, for K = 0, 1, 2.
* With λ = 0 the trainer skips the consistency term (`loss_con` is logged as exactly 0). The automatic check below covers every logged
  step.
* **Caveat: λ = 0 is not "labelled images only" in every respect.**
  * The student's forward pass runs on the concatenated batch of 4 labelled (strong view) + 4 unlabelled (strong view) images, in
    train mode.
  * So BatchNorm batch statistics and running stats still include the unlabelled images; only their loss is gone.
  * The teacher still runs on the unlabelled weak views, but its output is unused at λ = 0.
  * The λ = 0 student is therefore not identical to an SL-20 run, which also differs in the labelled view and the class-weight subset.

**Scores:** for all six MT runs, the teacher (EMA) and student (raw) final weights are scored on CPU on test and on val+test, by tmux
window `n-mteval` (`/tmp/noob_el/tools/mt_split_eval.sh`).
* The teacher test is re-scored on CPU so that all four numbers per run come from the same fp32 code path. The in-training GPU (bf16)
  number differs by ≤ 0.001.
* A weight diff confirms that student and teacher are different weights (`mt_teacher_student_weightdiff.json`; e.g. s0: max |Δ| 0.257,
  0 of 77 tensors identical).
* Files are stored per run and synced to `results_to_sync/<run>/` and `~/noob/el_results/<run>/`:
  `eval_final_{test,valtest}_cpu.json`, `eval_final_student_{test,valtest}_cpu.json`, `mt_teacher_student_weightdiff.json`.

**Result** (λ = 0 runs: 06:11 → 07:58–08:00, rc 0, no resumes; scoring done 08:13):
* **The unlabelled loss adds nothing measurable at this budget.**
  * MT-20 λ=0 scores **0.3653 ± 0.0183** on test and 0.3380 ± 0.0115 on val+test, against MT-20's 0.3648 ± 0.0071 and
    0.3407 ± 0.0068.
  * The paired same-seed difference λ 1.5 − λ 0 on the teacher is −0.0002 ± 0.0240 on test and +0.0027 ± 0.0175 on val+test.
* **The EMA adds nothing at the final step.**
  * Inside MT, teacher − student is +0.0000 ± 0.0019 on test: the cosine LR reaches 0, so at the end the teacher averages an almost
    still student.
  * At λ = 0 the teacher is slightly behind the student: −0.0048 ± 0.0048 on test, −0.0036 ± 0.0035 on val+test.
* **What then gives MT-20 its gain over SL-20 (+0.026)?** λ = 0 reproduces it, so it lies in what λ = 0 shares with MT but not with
  SL-20.
  * In the code path that is the **mixed 4 + 4 BatchNorm batch**: the student's forward runs on 4 labelled + 4 unlabelled images,
    so BN batch statistics and running stats include unlabelled images, over a batch of 8 instead of 4.
  * The labelled view (strong), the class weights, the optimizer and the schedule are the same.
  * This is a hypothesis, not tested here (see open items).
  * Part of the gap is SL-20's s3 outlier: against SL-20 without s3 (0.3527), MT-20 is +0.012 and MT-20 λ=0 is +0.013.
* **Caveat:** 3 seeds per arm and 50 test images. The λ = 0 spread (sd 0.018) is larger than MT's (0.007).

<!-- cv02-mt:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC. `defect_miou`, final-step weights from `latest.pth`, all on CPU (fp32): teacher = EMA weights (`scripts/evaluate.py --weights final`), student = raw weights (`/tmp/noob_el/tools/eval_student.py`, the same code path with `models["model"]`). The in-training GPU (bf16) teacher test number is shown for reference._

| run | λ_final | teacher test (in-training, GPU) | teacher test (CPU) | student test (CPU) | teacher val+test (CPU) | student val+test (CPU) |
|---|---:|---:|---:|---:|---:|---:|
| `mt_20pct_s0_cv02` | 1.5 | 0.3700 | 0.3691 | 0.3697 | 0.3446 | 0.3458 |
| `mt_20pct_s1_cv02` | 1.5 | 0.3567 | 0.3563 | 0.3541 | 0.3328 | 0.3302 |
| `mt_20pct_s2_cv02` | 1.5 | 0.3679 | 0.3684 | 0.3698 | 0.3447 | 0.3467 |
| `mt_20pct_lam0_s0_cv02` | 0 | 0.3451 | 0.3449 | 0.3549 | 0.3261 | 0.3326 |
| `mt_20pct_lam0_s1_cv02` | 0 | 0.3809 | 0.3802 | 0.3807 | 0.3490 | 0.3487 |
| `mt_20pct_lam0_s2_cv02` | 0 | 0.3698 | 0.3692 | 0.3732 | 0.3389 | 0.3434 |

| arm | teacher test | student test | teacher val+test | student val+test |
|---|---:|---:|---:|---:|
| **MT-20 (λ 1.5)** | 0.3646 ± 0.0072 (n 3) | 0.3645 ± 0.0090 (n 3) | 0.3407 ± 0.0068 (n 3) | 0.3409 ± 0.0092 (n 3) |
| **MT-20 λ=0** | 0.3648 ± 0.0181 (n 3) | 0.3696 ± 0.0133 (n 3) | 0.3380 ± 0.0115 (n 3) | 0.3416 ± 0.0082 (n 3) |

**Paired differences** (same training seed, mean ± sd over seeds):

| effect | test | val+test |
|---|---:|---:|
| EMA effect without unlabelled loss: teacher − student, λ=0 | -0.0048 ± 0.0048 (n 3) | -0.0036 ± 0.0035 (n 3) |
| EMA effect inside MT: teacher − student, λ 1.5 | +0.0000 ± 0.0019 (n 3) | -0.0002 ± 0.0024 (n 3) |
| unlabelled-loss effect on the teacher: λ 1.5 − λ 0 | -0.0002 ± 0.0240 (n 3) | +0.0027 ± 0.0175 (n 3) |
| unlabelled-loss effect on the student: λ 1.5 − λ 0 | -0.0050 ± 0.0207 (n 3) | -0.0006 ± 0.0162 (n 3) |

**λ=0 log check** (every logged training step): `mt_20pct_lam0_s0_cv02`: 400 logged steps (last 20000), loss_con or lambda non-zero on **0**; `mt_20pct_lam0_s1_cv02`: 400 logged steps (last 20000), loss_con or lambda non-zero on **0**; `mt_20pct_lam0_s2_cv02`: 400 logged steps (last 20000), loss_con or lambda non-zero on **0**.

<!-- cv02-mt:end -->

## ALHVR prototype diagnostic (2026-10-05)

See **`reports/prototype_diagnostic.md`**. It is generated by `/tmp/noob_el/tools/prototype_report.py` from
`/tmp/noob_el/tools/prototype_diagnostic.py`, with one JSON per run in `experiments/_prototype_diagnostic/`, and is synced to
`results_to_sync/prototype_diagnostic/` and `~/noob/el_results/prototype_diagnostic/`.
* No training. One GPU, about 1.5 min per run.
* The request named `alhvr_20pct_s0`, whose checkpoint exists only on gaint. The diagnostic ran on `alhvr_20pct_s1..s4_cv02`: same
  config, same seed-0 split (95 labelled, 383 held-out), different training seed.
* The script takes `--run`, so it can be run on s0 here or on gaint.

## Jha et al. (PV-S3) on UCF-EL

**Code.**
* https://github.com/abj247/PV-S3 at `e062f81` (`/tmp/noob_el/pvs3/PV-S3`), built on PS-MT.
* Setup ran 17:55–18:07 UTC, inside the 2 h timebox.
* The full glue log is `/tmp/noob_el/pvs3/glue/PATCHES.md`, also synced with the run.
* `git diff` on their repo is **empty**. Every change is an untracked addition (symlinks, data, backbone file) or a CLI flag. No
  algorithm change.

**Environment.**
* `/tmp/noob_el/pvs3_env`: CPython 3.8.20 and **torch 1.8.1+cu111 / torchvision 0.9.1+cu111**.
* PV-S3 ships no requirements file. Python 3.8 comes from its committed cp38 bytecode, and torch / CUDA from PS-MT's install doc (the
  CUDA ≥ 11 branch; cu111 has `sm_86`).
* The other packages are pinned to PS-MT's `ps-mt.yml` where it lists them.
* Verified on an A6000: an fp16 conv and a matmul run.
* A private `HOME` and offline wandb keep their `wandb login` and gdown from writing under `~`.

**Data: our lists, not theirs.**
* Their shipped splits cover 16,327 names. 5,194 of those are not in the public UCF-EL release.
* They also put 1,769 of the 2,289 public test images into their labelled / unlabelled training lists, and 437 more into their val
  list.
* So the run uses our `sl20_seed0` (1,912 labelled) and `unlabeled_sl20_seed0` (7,650), with our `test.txt` (2,289) as their
  `val` split.
* Glue:
  * symlinks with index names, because UCF names contain spaces and dots that their parser splits on;
  * masks 128 → 0, their `ignore_index`;
  * one all-zero mask for every unlabelled image, so unlabelled ground truth is never read. Their code reads it only for logging.

**Configuration as released** (`configs/config_deeplab_v3+.json`).
* Model: DeepLabV3+ R50 with a deep stem, one student and two EMA teachers (keep rate 0.996), with 125.3M params in total. The
  released ImageNet backbone covers all 275 tensors.
* Data: batch **16 labelled + 16 unlabelled**, 224 crops from a 299 base with random scale.
* Optimizer: SGD, **lr 1e-2**, momentum 0.9, wd 1e-4, Poly schedule.
* Consistency: `semi_ce` with thresholds 0.6 / 0.0, weight 1.5 after a 12-epoch cosine ramp-up; warm-up 0.
* Length: **30 epochs** over the unlabelled loader. **n_labeled = 1,912**: the released config says 2,614, which belongs to their
  split. **Optimizer steps: 30 × 479 = 14,370.**
* `main.py`'s CLI defaults would override this JSON (epochs 0, batch 2, lr 1e-3, 2 GPUs with DDP and lr × 2). The run passes flags
  that reproduce the JSON on one GPU.

**Supervised-only mode: not run.**
* The `model.semi=false` flag exists, but the released code cannot run it. `_train_epoch` unpacks the zipped batch as a 3-tuple and
  then calls `.detach()` on `None`, and `forward` always needs unlabelled input.
* Making it run would change their code.

**Run.** tmux window `n-pvs3`, `/tmp/noob_el/tools/pvs3_runner.py`:
* **Start:** it waits for the first MT run to finish, then claims a GPU with the launcher's own rules and claims, and requires fewer
  than 6 of our GPU jobs and ≥ 20 GiB free.
* **Training:** it keeps only the newest checkpoint. There is no watchdog, because PV-S3 has no resume.
* **Predictions:** it predicts the 2,289 test images exactly as PV-S3's `_valid_epoch` does: both teachers' logits averaged at full
  resolution, under fp16. As a secondary head it also writes teacher 1 alone, as their `inference.py` does.
* **Scoring:** our metrics module scores the predictions against the original masks (128 ignored), in the standard and pvs3
  conventions, per class.
* **Sync:** results go to `results_to_sync/pvs3_ssl20_cv02/` and `~/noob/el_results/pvs3_ssl20_cv02/`. These hold `train.log`,
  `runner.log`, `cmd.txt`, `pvs3_config_used.json`, `pvs3_test_scores.{json,txt}`, `PATCHES.md` and `test_predictions.tgz`.
* **Pre-flight on CPU:**
  * their loaders on our data gave 1,912 / 7,650 / 2,289 images and 479 iterations per epoch;
  * the model built and a teacher forward pass ran;
  * the prediction path ran on 3 images;
  * the scoring alignment check, with ground truth fed back as predictions, gave IoU 1.0000 on all classes over 2,289 images.

**Attempts.** Every log is kept in the run folder and synced.

| attempt | start (UTC) | GPU | outcome | fix (glue / environment only) |
|---|---|---|---|---|
| 1 | Oct 4 20:02 | 4 (approved extra) | failed after about 1 min in their data loader: `h, w, _ = image.shape`. 247 UCF-EL training images are single-channel, and PV-S3 never converts them | lossless RGB PNG copies of those 247 images (`PIL .convert("RGB")`, as our UCF loader does). A CPU pass over every item of their 3 datasets then passed. **Through my error the run was not relaunched after this fix (about 20:20), so about 9 h of GPU time went unused** |
| 2 | Oct 5 05:05 | 0 (idle rule) | failed at iteration 0: wandb 0.12.21's offline mode still queries api.wandb.ai when logging images (401) | wandb 0.13.11, which checks offline first; tested offline before the relaunch |
| 3 | Oct 5 05:07 | 0 (idle rule) | **done**: training rc 0 at 07:22 (2.25 h, 30 epochs, 14,370 steps, about 1.8 it/s; GPU util about 25 % because their CPU augmentation is the bottleneck, as released). Predictions, scoring and sync were done by 07:25. Only `1912_model_e30.pth` is kept | – |

**Findings** (numbers in the generated block below):
* **PV-S3 as released never predicts background.** On both grids, 0 of the background-GT pixels (184M on eval295, 215M native) are
  predicted as background, by either head.
  * Their CE loss uses `ignore_index=0` (`main.py`, `EntireModel`, `Dataloader/pvs3.py`), so class 0 never receives a gradient.
  * The pseudo-labels are argmax-ed over all 5 classes, but the student is never pushed toward background either.
  * At argmax, every background pixel goes to one of the 4 defect classes.
  * This is their code as released. Our glue only mapped UCF's 128 to their ignore index; background was already 0 in UCF's masks.
* **Standard convention (global confusion matrix, our headline for UCF):** defect mean IoU **0.050** on eval295, with precision 0.050
  and recall 0.908. Corrosion is predicted on **3.33M px against a GT of 102,570 (32×)** with the teacher mean, and 3.46M (34×) with
  teacher 1.
* **pvs3 convention (GT-background pixels dropped):** defect mean IoU **0.828** on eval295 and **0.791** native.
  * Per class on eval295: crack 0.915, contact 0.739, interconnect 0.787, corrosion 0.873.
  * This convention cannot see false positives on background, which here are every background pixel. That is the effect gaint's
    probes found ("pvs3 rewards fat predictions").
* **Cross-check of our scoring glue:** PV-S3's own end-of-training validation on the same 2,289 images (its `_valid_epoch`, teachers
  mean, native resolution, ignore 0) logged per-class IoU crack 0.9133, contact 0.7806, interconnect 0.5959, corrosion 0.8735, and
  background 0.
  * These equal our **pvs3 / native** numbers to 4 decimals.
  * So the prediction path, id alignment and class order are right, and PV-S3's own metric is the pvs3 convention.
* **Teacher 1 vs teacher mean:** within 0.002 IoU per class. Teacher 1 over-predicts corrosion slightly more (34× vs 32×).

<!-- cv02-pvs3:start -->

_Generated by `/tmp/noob_el/tools/cv02_table.py` at 2026-10-08 10:10 UTC._

Run: GPU 0, training rc 0, 2.25 h, 30 epochs x 479 = 14,370 optimizer steps; 2289 UCF-EL test images, UCF ignore (128) excluded.

* **Heads:** `teachers mean` = both EMA teachers' logits averaged (PV-S3's own `_valid_epoch`, **primary**); `teacher 1` = PV-S3's `inference.py` (secondary).
* **Grids:** **eval295** = our UCF evaluation grid (shorter side 295, prediction and GT resized together, nearest), comparable to every el-fault-detection UCF number (test corrosion GT 102,570 px); **native** = full resolution, PV-S3's own protocol (corrosion GT 109,478 px).
* **Conventions:** `standard` = global confusion matrix; `pvs3` = pixels whose GT is background dropped.

**eval295 grid (comparable to our UCF runs)**

| class | std IoU | std P | std R | pvs3 IoU | pvs3 P | pvs3 R | teacher 1: std IoU | teacher 1: pvs3 IoU |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| crack | 0.1168 | 0.1176 | 0.9460 | 0.9147 | 0.9652 | 0.9460 | 0.1162 | 0.9141 |
| contact | 0.0411 | 0.0414 | 0.8799 | 0.7392 | 0.8222 | 0.8799 | 0.0415 | 0.7385 |
| interconnect | 0.0129 | 0.0130 | 0.8621 | 0.7866 | 0.8998 | 0.8621 | 0.0128 | 0.7863 |
| corrosion | 0.0291 | 0.0291 | 0.9450 | 0.8731 | 0.9199 | 0.9450 | 0.0281 | 0.8682 |
| **defect mean** | 0.0500 | 0.0503 | 0.9082 | 0.8284 | 0.9018 | 0.9082 | 0.0497 | 0.8268 |

| class | GT pixels | predicted, teachers mean | predicted, teacher 1 |
|---|---:|---:|---:|
| background | 183,610,065 | 0 | 0 |
| crack | 13,281,479 | 106,868,718 | 107,239,360 |
| contact | 3,815,036 | 81,163,187 | 80,573,341 |
| interconnect | 144,345 | 9,593,914 | 9,683,694 |
| corrosion | 102,570 | 3,327,676 | 3,457,100 |

Corrosion (eval295): predicted **3,327,676** px (teachers mean; teacher 1: 3,457,100) vs GT **102,570** px, i.e. 32.44x (33.70x).

**native full resolution (PV-S3 protocol)**

| class | std IoU | std P | std R | pvs3 IoU | pvs3 P | pvs3 R | teacher 1: std IoU | teacher 1: pvs3 IoU |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| crack | 0.1146 | 0.1154 | 0.9454 | 0.9133 | 0.9642 | 0.9454 | 0.1141 | 0.9126 |
| contact | 0.0399 | 0.0401 | 0.9058 | 0.7806 | 0.8496 | 0.9058 | 0.0402 | 0.7800 |
| interconnect | 0.0167 | 0.0168 | 0.6340 | 0.5959 | 0.9085 | 0.6340 | 0.0168 | 0.6012 |
| corrosion | 0.0298 | 0.0298 | 0.9466 | 0.8735 | 0.9188 | 0.9466 | 0.0289 | 0.8702 |
| **defect mean** | 0.0503 | 0.0505 | 0.8579 | 0.7909 | 0.9103 | 0.8579 | 0.0500 | 0.7910 |

| class | GT pixels | predicted, teachers mean | predicted, teacher 1 |
|---|---:|---:|---:|
| background | 214,954,316 | 0 | 0 |
| crack | 13,124,228 | 107,516,867 | 107,933,499 |
| contact | 4,994,839 | 112,796,092 | 112,230,508 |
| interconnect | 256,205 | 9,650,927 | 9,686,528 |
| corrosion | 109,478 | 3,475,180 | 3,588,531 |

Corrosion (native): predicted **3,475,180** px (teachers mean; teacher 1: 3,588,531) vs GT **109,478** px, i.e. 31.74x (32.78x).

<!-- cv02-pvs3:end -->

_Sections 1–8 below document the day block (setup, environment, checks, smoke tests, launches, calibration, timeline, files)._

## 1. Code, data, splits

* **REVISION:** `dfa4fd67fc55b8bb42960aa2a472376c4cc8f7bf` (from `el_code.tgz`; no `.git` in the tarball).
* **Changes to the unpacked tree** (no code changes):
  * `data/ucf_el` re-pointed to `/tmp/noob_el/datasets/UCF-EL-Defect/training` (was the gaint path).
  * `data/labeled` replaced with `bench_labeled.tgz` (the shipped one was 1,164 symlinks to gaint-only paths).
  * The tarball's gaint-compiled `__pycache__/` (9 dirs) and `.pytest_cache/` were deleted. The first pytest run had used that stale
    bytecode (its paths were `/home/noob/work/...`), so the tests were rerun on fresh bytecode.
* **UCF-EL manifest** (`data/splits/ucf_el/manifest.json`): all 7 sha256 match. These are `train_images.csv`, `test_images.csv`,
  `train.txt` (9,562), `test.txt` (2,289), `val957_seed0.txt` (957), `sl20_seed0.txt` (1,912) and `unlabeled_sl20_seed0.txt` (7,650).
  Every list file has a manifest entry and the counts match.
* **BenchmarkEL** (`data/labeled`):
  * 1,164 regular files, 0 symlinks.
  * Every name in `data/splits/{train,val,test}.txt` and `seed{0,1,2}/{labeled,unlabeled}_{10,20,50}pct.txt` (21 lists) resolves to an image
    and a mask.
  * Official 478 / 54 / 50, pairwise disjoint. For every seed, labelled 47 / 95 / 239 are nested (10 ⊂ 20 ⊂ 50), and labelled ∪ unlabelled = train,
    disjoint.
  * All 582 pairs load through `BenchmarkELDataset`: 512×512, mask values 0..23.
  * `scripts/split_class_stats.py` rerun on these masks gives a CSV **byte-identical** to the committed
    `reports/split_class_pixel_counts.csv`, so per-split class pixel counts equal gaint's.
  * `test_splits.py::test_stratification_matches_meta` passes for seeds 0–2.
  * Content fingerprint (sha256 over sorted name + bytes, images then masks): `cc28d9b46a953efcc996cb8b5a41b89b3b99bc2bcd688ea2b60685f0cd5bebf4`.

## 2. Environment

| | cv02 (`himtenduh`) | gaint (from `reports/setup_check.md`) |
|---|---|---|
| GPU | 8× NVIDIA RTX A6000 48 GiB, cc 8.6 (Ampere) | RTX PRO 4500 Blackwell, cc 12.0 |
| driver | 580.105.08 (CUDA 13.0) | 590.48.01 |
| CPU / OS | AMD EPYC 9124, 64 threads; Ubuntu 22.04.5 | – |
| Python | CPython 3.12.15 (uv-managed, `/tmp/noob_el/python`) | 3.12 (patch level not recorded) |
| tools | uv 0.12.23 (`/tmp/noob_el/bin`), venv seeded with pip 26.2.1 | – |

* `/tmp/noob_el/env.sh` holds the seven exports as specified. Every shell, smoke and tmux lane sources it.
* uv was installed from the GitHub release tarball (`uv`, `uvx` copied into `/tmp/noob_el/bin`), not with the install script, so no shell profile or
  `~/.config` was written.
* Install order:
  1. `torch==2.14.1+cu130 torchvision==0.29.1+cu130` from `https://download.pytorch.org/whl/cu130`;
  2. `requirements.txt` from PyPI.
* Sizes: `.venv` 5.9 GB; caches 0.7 GB.

### `pip freeze` vs `freeze_gaint.txt`

**One difference:** `stringzilla==5.2.0` here vs `stringzilla==5.1.2` on gaint. It is a dependency of `albucore`; PyPI has a newer release than
when gaint installed. I pinned it to **5.1.2** to match gaint, and you confirmed keeping it. After that, `pip freeze` has the same 84 lines as `freeze_gaint.txt`, and
`pip check` passes. Not visible in a freeze: the Python patch level, the GPU architecture and the driver.

## 3. Checks

* **CUDA:** visible, 1 device per job. The device is an `NVIDIA RTX A6000` (cc 8.6), `sm_86` is in `get_arch_list()`, cuDNN 9.24.
* **bf16 matmul** 4096×4096 on GPU: finite, relative error vs fp32 1.66e-3. A bf16-autocast conv forward + backward also runs.
* **pytest -q tests:** **167 passed, 1 skipped**, 0 failed.
  * The skip is `test_sa_gating.py::test_flag_off_loads_pilot_checkpoint_strictly` ("pilot checkpoint not on disk"): it needs the gaint-only
    `experiments/pilot_sl_20pct_s0/checkpoints/best.pth`.
* **smp ImageNet weights:**
  * resnet50 (DeepLabV3+, 26,678,613 params) and vgg16 (U-Net, 23,750,424 params, as in `configs/pratt_unet.yaml`) download and build.
  * smp 0.5.0 fetches them from the HF Hub, so they are in **`HF_HOME`** (`/tmp/noob_el/cache/hf`, 655 MB), **not `TORCH_HOME`**, which stays empty.
  * Neither SL-20 nor ALHVR uses them: U-Net++ trains from scratch. You confirmed `HF_HOME` is fine.

## 4. Smoke tests (200 steps, one idle GPU, alone on it)

Opts are the production runs' opts with `training.total_steps=200`. Warmup is 200 steps, so the LR over these 200 steps equals the first 200
steps of a 20k run. Steps/s is the trainer's `timing.steps_per_sec` (training time only).

| config (opts) | GPU | steps/s | peak alloc / reserved (torch) | peak `nvidia-smi` | projected 20k steps |
|---|---|---|---|---|---|
| SL-20 (`supervised.yaml seed=0 data.labeled_fraction=0.2`) | 2 | **7.05** | 4.84 / 9.03 GiB | 9.9 GiB | 47 min train + ~40 val × 1 s ≈ **48 min** |
| ALHVR (`alhvr.yaml seed=1 data.split_seed=0 data.labeled_fraction=0.2`) | 2 | **0.574** | 14.73 / 17.78 GiB | 18.7 GiB | 9.7 h train + ~40 val × 3 s ≈ **9.7 h** |

* **Comparison with gaint:**
  * SL 9.03 GiB reserved equals gaint's pilot SL measurement.
  * ALHVR 17.78 GiB reserved vs 17.5 on gaint.
  * Gaint ran ALHVR at 0.70 steps/s alone (≈ 7.9 h), so the A6000 is about 18 % slower on it.
* **Losses at steps 50 / 100 / 150 / 200**, for comparison with the first lines of gaint's `train.log`:
  * SL-20 s0: 3.303 / 2.32 / 2.024 / 1.753.
  * ALHVR s1: 7.183 / 5.246 / 4.595 / 4.49.
* **Not bitwise run-to-run:** a first ALHVR smoke was killed at step ~100 when my Claude Code session restarted. It was a background task of the
  session, not a code problem; it was rerun detached. Its step-50/100 losses were 7.186 / 5.241, against 7.183 / 5.246 in the rerun: same seed,
  same GPU model.
  * `training.deterministic: true` (cuDNN deterministic, not `strict`) is not bitwise across runs here.
  * So the calibration run can differ from gaint's `sl_20pct_s0` even apart from the hardware change.

Smoke checkpoints were deleted on your request. Their logs (`train.log`, `metrics.json`, `config_used.yaml`, `regions.csv`, `nvsmi_samples.csv`, stdout) remain in `experiments/smoke_*` and are copied to `~/noob/el_results/smoke_*`.

## 5. Launches

**Launcher:** `/tmp/noob_el/tools/launch_cv02.py`, outside the repo, so the repo stays at REVISION. It imports `src/utils/jobs.py` and calls
gaint's `run_job` unchanged: memory guard (free ≥ peak + 2 GiB), FIFO queue and launch lock, and a resume-once watchdog (`--max_restarts 1`,
`--resume` from `latest.pth`). On top of that:
* **Job cap:** `MAX_JOBS` = 3 at first, and **6 from 07:08**, after your 07:05 decision (gaint uses 2).
* **GPU pick before every launch, watchdog restarts included:**
  * The GPU must be idle over 5 samples 1 s apart: memory.used < 1 GiB and utilization < 10 %.
  * It must not be claimed by another cv02 launcher (claim files in `/tmp/noob_el/state/gpu_claims`).
  * The launcher sets `CUDA_VISIBLE_DEVICES`, for both the memory guard and the run.
  * The last-used GPU is preferred. If no GPU is available, the launcher polls every 60 s.
* **Approved extra GPUs** (`--extra_gpus`, from 07:08): GPUs 0, 4 and 5, which failed the idle rule.
  * When you approved them at 07:05, GPU 0 held 14.8 GiB of another user's memory at 0 % util, and GPUs 4 and 5 were at 12–24 % util.
  * They were re-checked before every launch and admitted only while their max util over the samples stayed below 50 %.
  * Gaint's memory guard still applied on top, and the launch log records which rule admitted each GPU.
* **On rc 0:**
  * `metrics.json`, `config_used.yaml`, `train.log` and `regions.csv` (ALHVR only) are copied to `/tmp/noob_el/results_to_sync/<run>/`, and nothing else.
  * That folder is then copied to `~/noob/el_results/<run>/` by `/tmp/noob_el/tools/persist_cv02.py`. The helper checks the total first and
    writes nothing if it would reach 50 MB; its log is `/tmp/noob_el/state/persist.log`.
  * The results table in this report is regenerated (`/tmp/noob_el/tools/cv02_table.py --write`).
* **Old-code launchers:** the three runs launched before 06:45 (`sl_20pct_s0_cv02` and both ALHVR runs) ran the older launcher code, without
  the persist and table steps. Two tmux waiters, `persist` and `refresh`, did those steps when each run ended.
* **Tested before the launches:** a 100-step SL run was hard-exited at step 50, right after `latest.pth`.
  * The watchdog relaunched it 30 s later and re-picked the GPU.
  * The run resumed from step 50 (`resumes: [{from_step: 50}]`), finished rc 0, and the copy step ran.
  * The test outputs were deleted.

**tmux session `el`.** The opts are gaint's `scripts/night_queue.py` opts, in the same order, with only `run_name` changed. Logs are
`/tmp/noob_el/state/lane_*.log`, and every launch's GPU is in `/tmp/noob_el/state/launches.log`.

| window | runs | opts | peak (gaint value) |
|---|---|---|---|
| `a` | `sl_20pct_s0_cv02` → `s1` → `s2` | s0: `configs/supervised.yaml seed=0 training.total_steps=20000 data.labeled_fraction=0.2`; s*k*: `seed=k training.total_steps=20000 data.split_seed=0 data.labeled_fraction=0.2` | 10 GiB |
| `d`, `e`, `f` (from 07:08; extra GPUs 0, 4, 5) | pull from the queue `/tmp/noob_el/state/queue_a.txt`: `sa_sl_20pct_s0..s2_cv02`, then `sl_20pct_s3_cv02`, `s4`. Each run is claimed once (`mkdir state/run_claims/<run>`) | SA: SL-20 opts + `model.sa_gating=true` (gaint `sa_sl_20pct_s0`); s3/s4: as SL-20 s*k* | SA 11, SL 10 GiB |
| `a2` | lane a, continued: after `a` exited (08:34) it pulled from the same queue on the strict idle rule. The queue was already empty | – | – |
| `b` | `alhvr_20pct_s1_cv02` | `configs/alhvr.yaml seed=1 training.total_steps=20000 data.split_seed=0 data.labeled_fraction=0.2` | 18.5 GiB |
| `c` | `alhvr_20pct_s2_cv02` | as `b`, `seed=2` | 18.5 GiB |
| `persist`, `refresh` | waiters for the three old-code launchers (above) | – | – |

Lane a was extended with separate scripts rather than by editing the running `lane_a.sh`, which bash reads incrementally. The first,
sequential version of `a2` never started a run and was replaced at 07:08 (`lane_a2.sh.superseded`).

**Every launch** (all `fresh`; there were no restarts):

| time (UTC) | run | GPU | admitted by |
|---|---|---|---|
| 06:12:21 | `sl_20pct_s0_cv02` | 2 | idle rule (idle: 2, 6, 7) |
| 06:12:29 | `alhvr_20pct_s1_cv02` | 6 | idle rule (2 claimed) |
| 06:12:37 | `alhvr_20pct_s2_cv02` | 7 | idle rule (2, 6 claimed) |
| 06:59:47 | `sl_20pct_s1_cv02` | 2 | idle rule |
| 07:08:57 | `sa_sl_20pct_s0_cv02` | 0 | approved extra (util 0 %, 14.8 GiB of another user's) |
| 07:09:02 | `sa_sl_20pct_s1_cv02` | 4 | approved extra (util ≤ 23 %) |
| 07:09:07 | `sa_sl_20pct_s2_cv02` | 5 | approved extra (util ≤ 23 %) |
| 07:47:15 | `sl_20pct_s2_cv02` | 2 | idle rule |
| 08:15:08 | `sl_20pct_s3_cv02` | 0 | approved extra (util 0 %, 14.9 GiB of another user's) |
| 08:23:54 | `sl_20pct_s4_cv02` | 4 | approved extra (util ≤ 28 %) |

Peak concurrency was 6 of our jobs, from 07:09 to 08:24.

## 6. Calibration: `sl_20pct_s0_cv02` vs gaint `sl_20pct_s0`

* **Criterion (yours):** calibrated if the final `defect_miou` lies inside gaint's SL-20 seed range, 0.3059–0.3786.
  * Gaint's seeds: s0 0.3059, s1 0.3679, s2 0.3786 (mean 0.351, sd 0.039).
  * It is informational only; all comparisons stay within one machine.
* **Result:** **0.3385**, which is +0.0326 over gaint s0 and **inside** the range, so cv02 is calibrated.

  | | cv02 | gaint s0 |
  |---|---|---|
  | crack IoU | 0.2514 | 0.204 |
  | inactive IoU | 0.4256 | 0.408 |
  | 24-class mIoU | 0.4782 | 0.4805 |
* **Context:** the cv02 SL-20 mean over 5 seeds (0.3391 ± 0.0326) is within 0.012 of gaint's 3-seed mean (0.351).
  * The hardware differs: Ampere A6000 here, Blackwell on gaint.
  * Same-seed runs are not bitwise here (section 4).

## 7. Timeline (UTC)

| time | event |
|---|---|
| 05:38–05:41 | `el_code.tgz` and `ucf_training.tgz` present. `env.sh` written; code and UCF unpacked; UCF manifest 7/7 sha256 OK; BenchmarkEL found missing, and you were asked |
| 05:41–05:53 | uv installed; Python 3.12.15 venv created; torch cu130 and requirements installed |
| 05:48–05:55 | your `bench_labeled.tgz` arrived; `data/labeled` replaced; all 21 split lists resolve; pixel counts byte-identical to gaint's |
| 05:53–05:58 | freeze diff (`stringzilla` pinned); CUDA, A6000 and bf16 checks; pytest 167 passed / 1 skipped; smp weights downloaded |
| 05:59 | SL-20 smoke: 7.05 steps/s |
| 06:00–06:03 | first ALHVR smoke, killed at step ~100 by my session restart (not a code problem) |
| 06:05–06:11 | ALHVR smoke rerun detached: 0.574 steps/s. Launcher crash / resume test passed |
| 06:12–06:14 | `sl_20pct_s0_cv02` and both ALHVR runs launched on GPUs 2, 6, 7 |
| 06:44 | your section-7 answers applied: persistence, smoke-checkpoint deletion, lane a extension, one results table |
| 06:59 | calibration run landed: 0.3385, inside the range |
| 07:05–07:09 | your approval for GPUs 0, 4, 5 and cap 6; SA SL-20 s0–s2 launched there |
| 08:34 / 09:02 / 09:17 | last SL-20 runs done (s2, s3, s4); lanes a, d, e, f empty |
| 15:52 / 15:54 | `alhvr_20pct_s1_cv02` / `s2_cv02` done; synced, persisted, table refreshed. **Block complete** |

## 8. Files

| path | content |
|---|---|
| `/tmp/noob_el/results_to_sync/<run>/` | 10 runs: `metrics.json`, `config_used.yaml`, `train.log` (+ `regions.csv` for ALHVR). Nothing else |
| `~/noob/el_results/` | the same 10 run folders, 3 smoke-log folders (`smoke_sl20_cv02`, `smoke_alhvr_cv02`, `smoke_alhvr_cv02_killed`) and a copy of this report (`cv02.md`). 3.7 MB of 50 MB |
| `/tmp/noob_el/el-fault-detection/experiments/<run>/` | full run dirs, including `checkpoints/{best,latest}.pth` (1.2 GB in total), `launch.log` and `.stdout` |
| `/tmp/noob_el/tools/` | `launch_cv02.py`, `persist_cv02.py`, `cv02_table.py`, the lane scripts and the waiters |
| `/tmp/noob_el/state/` | `launches.log`, `lane_*.log`, `persist.log`, `queue_a.txt`, run and GPU claims |
| `/tmp/noob_el/env.sh` | environment for every shell |

Workspace total: 8.6 GB on `/tmp`. The tmux session `el` still exists, but only idle shells are left in its windows.

## 9. Open items, for your decision

0. **`~/noob/el_results` is at 39.9 MB of the 50 MB cap**, after the UCF `train.log` files. The next block will not fit. Options:
   raise the cap; stop persisting `train.log` (keep it in `results_to_sync/` only); or prune older folders.
1. **Job cap** (superseded for Block E by your "at most 8"): from 19:12 Oct 5 to Block E the launcher used 9 slots, your per-GPU allocation (0–4 one each, 6 and 7 two each), instead of
   the earlier cap of 6. Keep 9, or return to 6?
2. **BatchNorm: size vs content.** Every BN-batch-8 arm is at 0.362–0.370 and every BN-batch-4 arm at 0.339–0.343. Possible
   controls to separate BN batch size from what the extra images are:
   * SL-20 batch 4 with GroupNorm or frozen BN statistics;
   * SL-20 with 4 labelled + 4 duplicated labelled images forward-only;
   * MT at batch 2 + 2.
3. **Crack threshold:** a val-chosen crack-logit bias adds +0.016–0.027 test defect_miou in 4 of 5 arms
   (`reports/precision_diagnostic.md`). Report results at b = 0 only (current), or also at the val-chosen b?
4. **PV-S3 comparability** and **prototype diagnostic on `alhvr_20pct_s0`**: unchanged from earlier.
5. **Cleanup:** `/tmp/noob_el` holds the PV-S3 env (≈ 3 GB) and data, plus all run checkpoints. The tmux session `el` holds idle
   windows. Clean up once you have pulled `results_to_sync/`?
