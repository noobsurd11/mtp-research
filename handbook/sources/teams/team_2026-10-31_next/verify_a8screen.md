# coach verify: protocol_A8screen v1.1 (A8 DINOv3 ConvNeXt-T-PF vs A8c IN-1k ConvNeXt-T-PF, 4k steps, seeds 0-1; gaint, el_f8 c280e8c2)

coach (respawned session), 1 Nov 2026 23:35 IST (judge's fixes applied 23:40, 1 Nov). Independent recompute. Tags: E (file), S (judgement). No test cell, no E1 cell read (by design: protocol §0 / §3, v1.1 §10).

## Verdict: **KILL** (GO rule terms 1a and 1b fail; validity and integrity hold)

## Inputs and code
- **Runs (E, nq/launch.log via `results/a8/launch.log`):** f8_A8_4k_s0 21:15-21:41, f8_A8c_4k_s0 21:17-21:45, f8_A8_4k_s1 21:45-22:14, f8_A8c_4k_s1 22:14-22:55; all `trained rc=0`, all `config OK ... seed K + A8 / A8c change only`. GPU floor held: min free 2,880 MiB (22:16:46, `results/a8/gpumem.log`; finllm + HC s5 / s6 + A8c s1).
- **Scoring:** a8_score.sh 75a57c9c (FROZEN 19:53), 22:56:30-23:02:17, `a8 scoring done: rc=0`, MANIFEST **3cdd7286** (31 files). Mechanical readout `a8_summary.txt`: KILL.
- **Where I recomputed (disclosed):** gaint CPU (nice 19, 8 threads, CUDA hidden), reading `/home/noob/work/a8_score/v1` in place after `md5sum -c` of the out MANIFEST (3cdd7286, OK), the 8 dumps (`dump_md5_on_gaint.txt`, OK) and the 4 init refs (OK). runner's local pull `results/a8/raw/` re-checked: `md5sum -c` OK (same MANIFEST). Text outputs: `results/a8/coach_v/` (MD5 file there).
- **Code (coach's own):** `scripts/coach/coach_verify_a8_gaint.sh` 580d05c5; `coach_a8.py` **2da944cd** (GO terms: own 1,000-bin AP, own b_rel on val records, own FA, own 36-module bootstrap with own RNG seed 20261101, so the bound differs from the scorer's in the 3rd decimal by design); `coach_a8_extra.py` **b7de8d5f** (validity from latest.pth vs the weights files themselves, own torchvision remap; val dump integrity at b 0 from the dumps' margin / oth).

## Integrity (E, `results/a8/coach_v/integrity.txt`)
- el_f8 HEAD c280e8c, 0 tracked changes. a8_root splits: train 842f27c4, val 9dcccf00, **test.txt 9dcccf00 = val** (no real test stem can be read by the trainer's end-of-run pass).
- Config diffs (own `diff` of config_used.yaml): A8 vs A8c = the 3 backbone keys only (+ run_name); s0 vs s1 = seed only. Schedule keys in both: total_steps 4000, warmup 200, PF freeze 200 / ramp 200 / lr_mult 0.1, val_every 4000, drop_path 0.0, root a8_root (the `ssl:` block's 2000 / 2000 keys are unused by supervised runs). Rest of the config = pf2_SUPPF_100pct_s5's (own filtered diff: empty).
- latest.pth step 4000 in all 4 (asserted). Val dump stems = el_f8 val.txt (54); rf dump stems = calib stems_eval (106): F51 51 / H36 36 / F19 19.

## Validity (protocol §3: stages 2-3 weight cosine to init ≥ 0.5, every run)
| run | scorer (enc_cosine_hr vs init.pth) stage2 / stage3 | coach (latest.pth vs weights file, float64 concat) stage2 / stage3 | coach min per-tensor stage2 / 3 |
|---|---|---|---|
| A8 s0 | 0.9869 / 0.9963 | 0.9879 / 0.9971 | 0.980 / 0.993 |
| A8 s1 | 0.9833 / 0.9970 | 0.9844 / 0.9973 | 0.977 / 0.995 |
| A8c s0 | 0.9971 / 0.9986 | 0.9972 / 0.9988 | 0.996 / 0.998 |
| A8c s1 | 0.9971 / 0.9984 | 0.9971 / 0.9986 | 0.996 / 0.998 |
- **Both arms VALID.** PF preserved both ConvNeXt encoders (LayerNorm cos ≥ 0.999, gammas ≥ 0.999, scorer). A8 moved more than A8c (stage1 0.966 vs 0.996). My first float32 pass printed one cosine > 1 (A8c stage3 1.0003: float32 accumulation over ~15M weights); the table uses the float64 rerun.

## Pass 3b gate (val dump at b 0 vs the trainer's metrics.json val_history[-1], |Δ| ≤ 0.005)
- Own computation from the dumps (pred = crack where margin > 0, else oth; pooled 54 cells): Δ crack IoU +0.0001 / +0.0001 / −0.0005 / −0.0006, Δ inactive IoU −0.0011 / −0.0007 / −0.0016 / +0.0013 (A8 s0, s1, A8c s0, s1). **PASS 4/4**, equal to the scorer's `a8_dump_integrity.txt` to 4 dp. So the CPU fp32 dumps are the trained models.

## GO rule (protocol §3, seed means; GO only if all hold)
| term | scorer (8eba76e5) | coach | result |
|---|---|---|---|
| 1a F51 crack AP: A8 − A8c > 0 | 0.5448 − 0.5691 = **−0.0243** | **−0.0243** | **FAIL** |
| 1b F51 module-bootstrap lower 95% bound > 0 (36 modules, 2,000) | **−0.0463** [hi +0.0454] (seed 0) | **−0.0476** [hi +0.0423] (own RNG) | **FAIL** |
| 2 val crack AP: A8 ≥ A8c − 0.02 | 0.5246 vs 0.5287 (Δ −0.0041) | Δ −0.0041 | pass |
| 3 FA px, H36 19 crack-free cells, at val b_rel: A8 ≤ max(1.5 × A8c, A8c + 200) | 92 vs 28 (bound 228) | 92 vs 28 | pass (only via the +200 px floor) |
| 3 FA px, F51 34 crack-free cells, at val b_rel | 392 vs 201 (bound 401) | 392 vs 201 | pass (only via the +200 px floor; margin 9 px) |
- **coach GO: False → KILL.** Every per-run AP (F51, val, H36, F19), every b_rel (A8 +2.9 / +2.8; A8c +1.0 / +2.7; all reachable at relP@2 ≥ 0.90) and every FA count equals the scorer's to 4 dp. **CONFIRMED vs runner's / the scorer's readout.**

## Reported (not in the rule)
- Per seed F51 AP: A8 0.548 / 0.542; A8c 0.536 / 0.602. The A8c seed spread (0.067) is larger than the arm gap; A8 beats A8c on seed 0 (+0.012) and loses on seed 1 (−0.061). F51 crack modules: **3 up, 5 down, 4 tied at exactly 0** (CSIR_00035 / 00038 / 00048 / 00083: every crack px in the lowest bin in all four runs, so module AP = prevalence; judge, coach-checked on the scorer's per-module dAP); CSIR_00031 / 00063 are near 0 too, so 6 of 12 crack modules decide nothing.
- F51 is mostly one cell (judge, E `judge/out/a8_recompute_out.txt`): `CSIR_00073_r9_c3_rf` holds 11,110 of 14,639 crack px (76%); without its module dF51 is −0.0047; leave-one-crack-module-out dF51 is negative for all 12 (−0.0283 … −0.0047). Seed-aware two-stage bootstrap (modules + a seed draw per arm): [−0.069, +0.047], P(d* > 0) 0.33. fp16-exact AP instead of 1,000 bins: dF51 −0.0286; the binned AP reads ~0.03 low and flips term 2's sign (−0.0041 binned, +0.0028 exact; passes either way).
- F19 (train-module `_rf` cells) crack AP: A8 0.350 vs A8c 0.220 (coach = scorer). F51 cell AUROC: A8 0.749 vs 0.671 (scorer; judge-recomputed; 0-px cells as negatives; 12 positives). F19's AP gain is small-n (9 crack cells, 37% of px in one cell, judge).
- Inactive IoU at b_rel (scorer; judge-recomputed, equal): val 0.376 vs 0.408; F51 0.222 vs 0.307; F19 0.061 vs 0.426. Trainer val at 4k: inactive 0.368 / 0.383 vs 0.438 / 0.372.
- False alarms are higher for A8 on both crack-free sets (H36 ×3.3, F51 ×1.95): **inside the bound only through the +200 px floor**; the ratio part fails on both sets. Not only A8's higher b_rel: at a common b 2.8, H36 88.5 vs 43.5 (×2.0), F51 386 vs 228 (×1.7); at argmax, ×2.4 / ×1.3 (judge). Few cells and seed-noisy (A8 H36 mean is mostly s0: 182 vs 2). Same direction as the frozen probe (DINOv3 H36 FA 20-90× R50).
- **Pitfall for the record (judge):** each run's metrics.json `test_final` / `test_best` equal `val_history[-1]` (n_images 54): with test.txt = val.txt these are val numbers under a test label. No table may harvest them as test.

## Reading (S)
- The pre-registered kill gate fails on its two binding terms: the point estimate is negative, every leave-one-module-out is negative, and the bootstrap interval sits around 0 (about −0.047 … +0.045; seed-aware −0.069 … +0.047). **KILL means "no sign of a gain", not "DINOv3 is worse"**: A8c's own seed spread (0.067) exceeds the arm gap and a full-schedule gain up to ~+0.045 F51 AP is not excluded. The 'for' signals are small-n (F19 AP, F51 cell AUROC); the 'against' signals are larger (inactive IoU at b_rel, FA ×2-3). Nothing here argues for a rescue run.
- The frozen-probe edge (DINOv3 − IN-1k ConvNeXt-T +0.053 F51 AP, probe run 2) did not carry to PF fine-tuning. Same pattern as Track D D1 (frozen-probe passes that did not carry to fine-tuning).
- **Consequence (protocol §5, fixed before the screen):** "foundation encoder" (idea 8) is **closed for this thesis**, reported as a negative result with D1; no larger variant is downloaded; no A8 full-arm protocol. The lane time reserved for an A8 full arm is free (B6 stays cv02-only per the user; SKR2 waits for the user's call after HC).
- What this does not test: ViT-S/16 + LoRA / HR branch (out by the probe pick), SAM2 Hiera-T (below the probe bar), IN-22k ConvNeXt comparators. None is proposed.

## judge: adversarial check (2026-11-01 23:40 IST; verify_a8screen as of md5 779c0518; a8_score v1 out MANIFEST 3cdd7286)
**KILL CONFIRMED.** Terms 1a and 1b fail; 2 and 3 pass; both arms are VALID; the val gate holds; no test cell or E1 cell was read. The protocol §5 consequence (idea 8 closed, no larger variant, no full arm) stands. Four readings need fixing (items 2-4 and 6 below).

Code (own; imports nothing from a8_screen_score, el_metrics, calib_dump, enc_cosine_hr or el_f8; gaint CPU, nice 19, CUDA hidden, PIDs 3145237 / 3148672, both exited rc 0):
- `judge/a8_recompute.py` cf3ebb0c (AP from per-cell fp16 histograms, own val OP with a 13-offset EDT<=2 disk, spot-checked against an explicit EDT, own FA, own bootstrap);
- `judge/a8_cos_check.py` 9070c75a.

Outputs: `judge/out/a8_recompute_out.txt` b0e7e1a6, `judge/out/a8_cos_check_out.txt` 2a7949ad.

### 1. The rule was applied exactly as pre-registered (E)
- Each term in the scorer's code matches the §3 text:
  - seed means;
  - 1,000-bin p(crack) AP over keep px;
  - a 36-module paired bootstrap (2,000 resamples, seed 0);
  - b_rel = max val relR@2 subject to relP@2 >= 0.90 (grid -4..+12, step 0.1);
  - FA = crack px (margin + b > 0, keep) on n_gt == 0 cells;
  - FA bound = max(1.5x, +200).
- Set facts:
  - F51: 51 cells, 36 modules, 12 crack cells, 14,639 crack px (= §2). There are also 5 ambiguous cells (1-19 px); FA uses the 34 crack-free cells.
  - H36: 19 crack-free cells.
- My numbers equal the scorer's:
  - every per-run AP (F51 / val / H36 / F19) to 6 dp;
  - b_rel 2.9 / 2.8 / 1.0 / 2.7 (all reachable);
  - FA H36 182 / 2 / 56 / 0 and FA F51 537 / 247 / 210 / 192;
  - bootstrap [-0.0463, +0.0454] with the same RNG stream;
  - with RNG seeds 1 / 2 the lower bound is -0.0462 / -0.0456.
- My recompute of the inactive IoU at b_rel and of the cell AUROC (marked "not recomputed" in the verify) equals the scorer's.

### 2. The F51 term is mostly one cell; the sign is still robust (E)
- `CSIR_00073_r9_c3_rf` holds 11,110 of the 14,639 F51 crack px (76%). Without its module, dF51 is -0.0047.
- Leave-one-crack-module-out dF51 is negative for all 12 modules (-0.0283 to -0.0047).
- The bootstrap is centred above the point estimate (mean -0.014, median -0.018; P(d* > 0) 0.16). This is because about 36% of resamples drop CSIR_00073.
- Robustness:
  - **Seed-aware two-stage bootstrap** (modules + a seed draw per arm): [-0.069, +0.047], P(d* > 0) 0.33.
  - fp16-exact AP instead of 1,000 bins: dF51 -0.0286, [-0.049, +0.048].
  - The 1,000-bin AP reads about 0.03 low and flips the val term's sign (-0.0041 binned, +0.0028 exact). Term 2 passes either way.
- **Fix the sign-count reading.** "3 / 12" is really 3 up, 5 down, and 4 missed by all four runs:
  - in CSIR_00035 / 00038 / 00048 / 00083 (37-83 crack px), every crack px sits in the lowest bin in every run, so module AP = prevalence and dAP is exactly 0;
  - CSIR_00031 / 00063 are near 0 in all runs too;
  - so 6 of 12 crack modules decide nothing.

### 3. False alarms: term 3 passes only on the +200 px floor (E)
- The ratio part of the bound fails on both sets:
  - H36: 92 vs 28 (x3.3);
  - F51: 392 vs 201 (x1.95; the bound is 401, so it passes by 9 px).
- The excess is not only A8's higher b_rel:

  | b | H36 A8 vs A8c | F51 A8 vs A8c |
  |---|---|---|
  | common b 2.8 | 88.5 vs 43.5 (x2.0) | 386 vs 228 (x1.7) |
  | argmax (b 0) | 51 vs 21 (x2.4) | 219 vs 169 (x1.3) |

- It is few-cell and seed-noisy:
  - crack-free cells with >= 20 FA px at b_rel: A8 H36 1 / 0, F51 3 / 3; A8c H36 1 / 0, F51 2 / 1;
  - the A8 H36 mean is mostly s0 (182 vs 2).
- This is the same direction as the frozen probe (DINOv3 fires more on crack-free cells). Write "inside the bound only through the +200 px floor" rather than just "inside the pre-registered bound".

### 4. No test cell, no E1 cell: confirmed with stronger evidence (E)
- In each of the 4 runs, metrics.json `test_final` (and `test_best`) equals `val_history[-1]` on all 7 scalars checked: crack / inactive IoU, mIoU, defect mIoU, pixel accuracy, n_images **54**, n_crack_free 31. The trainer's end-of-run TEST pass therefore scored the 54 val cells (real test has 50).
- `config_used.yaml` data.root = a8_root in all 4 runs. a8_root test.txt = val.txt (9dcccf00); real test.txt is a31fad14.
- The dump stems share 0 names with the real test.txt and 0 with the E1 stems_eval list (names only).
- **Pitfall for the record:** these metrics.json `test_*` blocks are val numbers under a test label. No table may harvest them as test.

### 5. Validity and the val gate (E)
- **Cosine (own; both per-tensor mean and concatenated):**
  - stage2 / 3: A8 0.983-0.988 / 0.996-0.997; A8c 0.997 / 0.998-0.999;
  - step 4000 in every latest.pth.
- **Arm-swap control:** A8 4k vs A8c init gives stage2 -0.001, stage3 0.002, the same as A8 init vs A8c init. So each arm trained from its own file; the one change took.
- **Init vs weight files:**
  - encoder init is identical across seeds within each arm;
  - A8 init = the DINOv3 safetensors by key (178 tensors, max|d| 0);
  - A8c init = the torchvision file by exact values (178/178) without el_f8's remap.
- A8 moved about 10x more than A8c under the same PF schedule (1 - cos 0.013-0.038 vs 0.003-0.004). This is reported only.
- **Val gate (own, pooled at b 0 from the dumps):**
  - dump vs metrics.json val_history[-1] (step 4000): crack IoU +0.0001 / +0.0001 / -0.0005 / -0.0006; inactive IoU -0.0010 / -0.0007 / -0.0016 / +0.0013;
  - max |d| 0.0016 <= 0.005: PASS 4/4 (= `a8_dump_integrity.txt`).

### 6. Reading (S)
- **The KILL means "no sign of a gain", not "DINOv3 is worse".**
  - A8c's own seed spread on F51 (0.067) exceeds the arm gap.
  - A full-schedule gain up to about +0.045 F51 AP is not excluded.
  - The screen was built so that only a clear win passes (§4 expected a KILL as plausible), and it found none:
    - the point estimate is negative;
    - every leave-one-module-out is negative;
    - P(d* > 0) is 0.16.
- **The "for" signals are small-n:**
  - F19 crack AP +0.13: 9 crack cells, 37% of px in `CSIR_00104_r3_c3_rf`;
  - F51 cell AUROC +0.08: 12 positives.
- **The reported "against" signals are larger:**
  - inactive IoU at b_rel: F19 0.061 vs 0.426, F51 0.222 vs 0.307, val 0.376 vs 0.408 (recomputed; equal to the scorer's);
  - FA x2-3 (item 3).
- Nothing here argues for a rescue run. Closing idea 8 by the pre-registered rule is right.
- **Small fix:** the verify header says 23:45. The file was written 23:35:41 (mtime), as coach's log line says 23:35.

- **Correction (coach, 2026-11-01 23:48 IST):** this header first read "judge's fixes applied 23:40, 2 Nov"; the fixes were applied 23:40 on **1 Nov** (clock-read; judge's flag). Header corrected in place at 23:48; no number or reading changed.
