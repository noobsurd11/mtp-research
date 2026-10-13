# 10. Experiments P13 to P17, the P13 audit, and E1 (11 to 13 Oct 2026)

## What this covers
This file covers the last block of experiments before the mid-term:
- the audit that followed "supervised is beating SSL";
- P13: SSL with BatchNorm kept clean, plus CutMix;
- P14: an offset-tolerant loss on human labels;
- P15: UCF-EL encoder pretraining;
- P16: SSL at 20, 50 and 100% labels;
- P17 (13 Oct): SKCDF-style decoupled decoder on BsM5, and BsM5 seeds 3–4 (P13 Amendment 2);
- E1: the task-aligned per-cell evaluation and the 106-cell unseen-module extension.

Each experiment follows the same layout: Question, Why, Setup, Locked rules, Results, Verdicts, Robustness, Reading, Next. Earlier experiments (P1 to P12) are in `08_experiments_P1_P7_diagnostics.md` and `09_experiments_P8_P12_ssl_series.md`. Cross-experiment conclusions are in `11_results_synthesis_and_claims.md`.

**Status at writing (12 Oct 2026, ~05:30 IST)**

| Item | Status | Where the results are |
|---|---|---|
| P13 audit | done | `results/p13_audit/`, `protocols/P13_cutmix_separate_bn.md` |
| P13 | done (13 runs, cv02) | `results/p13/README.md` |
| P14 | done (9 runs, cv02) | `results/p14/README.md` |
| P15 | done (6 runs, gaint) | `results/p15/README.md` |
| P16 Part A (supervised references) | done (9 runs, cv02; last rescored 22:06 IST, all rc = 0) | `results/p16/README.md` |
| P16 Part B (SSL arms) | done (15 runs, cv02, 21:04 IST to 04:24 IST 12 Oct, all rc = 0); analysed 12 Oct ~05:00 IST | `results/p16/README.md` |
| P17 + P13 Amendment 2 | done (7 runs, cv02, 13 Oct 01:55–04:08 IST, all rc = 0); analysed 13 Oct ~08:00 IST | `results/p17/README.md`, `results/p13/README.md` |
| E1 | done for P6 to P17 checkpoints | `results/e1/README.md`, `results/e1/e1_*.md` |

## Sources
- Protocols:
  - `protocols/P13_cutmix_separate_bn.md` (with Amendment 1);
  - `protocols/P14_tolerant_supervision.md`;
  - `protocols/P15_ucf_encoder_transfer.md`;
  - `protocols/P16_label_fraction_curve.md` (Part A and Amendment 1);
  - `protocols/P17_decoupled_decoder.md`; P13 Amendment 2 in `protocols/P13_cutmix_separate_bn.md`.
- Results:
  - `results/p13/README.md`, `results/p13/p13_rules.txt`, `results/p13/per_image_test.txt`, `results/p13/fig_p13_bars.png`;
  - `results/p14/README.md`, `results/p14/p14_rules.txt`, `results/p14/per_image_test.txt`, `results/p14/fig_p14_bars.png`;
  - `results/p13_audit/bn_diag.py`, `bn_diag.log`, `bn_diag.json`, `smoke_gpu.log`;
  - `results/p17/README.md`, `p17_rules.txt`, `per_image_test.txt`, `sensitivity_excell.txt`, `decoder_u_secondary.txt`, `fig_p17_bars.png`.
- E1: `results/e1/README.md`, `results/e1/e1_ext_v2.md`, `results/e1/e1_p11.md`, `e1_p12.md`, `e1_p13.md`, `e1_p14.md`, `e1_p17.md`.
- Scripts:
  - `scripts/post_ssl.sh` (P13, P14 post-analysis);
  - `scripts/post_p15.sh`, `scripts/post_p16.sh`, `scripts/p16_curve.py`;
  - `scripts_cv02/p16b_auto.sh` (P16 automatic recipe pick and launch);
  - `scripts_cv02/e1_aggregate.py`.
- Server logs, read-only:
  - gaint `/home/noob/work/el_p14/reports/p15/launch_gaint.log`;
  - cv02 `/tmp/noob_el/el_p13/reports/p15_pre.log`;
  - cv02 `/tmp/noob_el/el_p16/reports/p16b/selection.txt`.
- The user's messages of 11 Oct, quoted from the session transcript (copies in `/tmp/claude-1003/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5/scratchpad/docsrc/user_messages.md`; stable byte-identical copy `sources/chat/user_messages_2026-10-07_to_11.md`, with UTC timestamps). Session summaries: `sources/chat/claude_session_summaries_2026-10-07_to_11.md`.
- Times: several protocol and README headers state clock times that disagree with git (some are earlier than the user message that prompted them, or later than the commit that contains them). This file gives git commit times (IST) and notes the header time.

---

## Terms used in this file (short versions; full list in `04_glossary_and_naming.md`)

**Models and training**
- **Mean Teacher (MT):** two copies of one network.
  - The student is trained by gradient descent.
  - The teacher's weights are an exponential moving average (EMA, 0.999) of the student's.
  - The teacher labels unlabelled images; the student is trained to agree.
  - The weights we evaluate are the teacher's final ones.
- **Pseudo-label (PL):** the teacher's predicted class for an unlabelled pixel, used as a training target.
- **Unlabelled loss weight (λ):** 0 for the first 2,000 steps, then ramped to 1.0 over the next 2,000.
- **Labelled view:** the augmentation applied to labelled images.
  - "Matched" or `ssl.labeled_aug=supervised` means the same label-safe view the supervised baseline uses (introduced in P11).

**Pseudo-label losses**
- **Tolerant PL (`tolerant_pl`):**
  - For rare classes (crack, inactive), the student is credited if it predicts that class anywhere within R = 2 px of the teacher's rare pixel.
  - Confident (≥ 0.95) head-class pixels outside a 2 px band around rare targets get ordinary cross-entropy.
  - Everything else gets no loss.
  - Defined in P7; `src/losses/tolerant_pl.py`.
- **Hard PL (`confidence_ce`):** ordinary cross-entropy on teacher pixels whose confidence is ≥ 0.95 (`t_pos`).

**BatchNorm and mixing**
- **BatchNorm (BN):** a layer that normalises activations with batch statistics during training and keeps running averages for test time.
- **Joint BN:** labelled and unlabelled images go through the student in one batch, so unlabelled images shape the BN statistics. The default up to P12.
- **Separate forward:** `ssl.student_forward=separate`.
  - The labelled batch goes forward first.
  - The unlabelled batch goes forward inside `frozen_bn_stats`, so it does not touch the running statistics.
- **CutMix (`ssl.cutmix_p=0.5`):**
  - For each unlabelled image, with probability 0.5, a box from the next image in the batch is pasted into the student's strong view.
  - The teacher's prediction gets the same box.
  - It copies pixels and never resamples them, so it does not blur 1 to 2 px cracks.

**Controls and rules**
- **Loss-off control:** the same SSL pipeline with λ = 0.
  - With the separate forward, the λ = 0 student is bit-identical to the supervised run, so the supervised run is the loss-off control.
- **P8 rule 1 (the "detectable" rule):** B beats A on a metric if
  `Δ > max(0.01, 2·√((sd_A² + sd_B²)/3))`,
  with sd the standard deviation over seeds. A comparison passes if at least one primary metric passes and none is worse by the same margin. With 3 vs 3 seeds this is about 2 standard errors (one-sided p ≈ 0.06). The divisor stays 3 with more seeds, so at 5 vs 5 (the P13 and P16 primaries) it is about 2.58 standard errors, a stricter bar (see `07_methodology_rules_and_statistics.md`).

**Metrics**
- **Primary metrics:** on the 50 test cells, scored against the revised (E-SCDD) masks, argmax prediction, final weights:
  - crack IoU;
  - inactive IoU;
  - crack relF1@2 (relaxed F1: precision and recall where a pixel counts if the other mask is within 2 px).
- **relP@2:** relaxed precision at 2 px.
  - The "width check": a drop > 0.05 flags masks getting fatter to win recall.
- **AP:** average precision over all score thresholds.
- **bin-0 share:** the share of ground-truth pixels whose predicted score for their class is < 0.001. A high value means confident misses.
- **Gap closed:** (X − A) / (A@100% − A). The share of the supervised gap to full labels that a method closes.

**Robustness checks**
- **Image bootstrap:** resample the 50 test cells with replacement 2,000 times, paired across arms; report the 95% interval of Δ.
- **Leave-top-3-out:** Δ recomputed without the 3 test cells holding the most ground-truth pixels of that class.
  - The top 3 hold 32% of crack and 59% of inactive test pixels.
- **Source split:** the test cells by origin, CSIR/ARTS (21 cells) vs CFVS/BMRK/SDLE (29 cells).

**Collapse logging**
- **rare_frac:** the share of unlabelled pixels that are pseudo-labelled crack or inactive.
- **conf_frac:** the share of confident pseudo-label pixels.
- Both are logged during training; a falling rare_frac is the collapse signal found in P10.

**Arm names in this file**

| Name | Meaning |
|---|---|
| A5c | supervised, 5% labels, cv02 |
| Cs5 | tolerant PL, separate BN |
| CsM5 | Cs5 + CutMix |
| BsM5 | hard PL, separate BN, CutMix |
| Cm5, Dm5 | P12 tolerant / loss-off with joint BN (m = matched labelled view) |
| L3, L3o, L3To, L3T | P14 supervised arms: o = old masks, T = tolerant loss |
| gU5, gU10 | P15 UCF-pretrained encoder, gaint |
| A5, gA10 | P15 references: gaint supervised at 5% and 10% |
| S20, S50, Sx100 | P16 SSL arms |
| A20, A50, A100 | P16 supervised references |

---

## Context: what was known before the audit, and what arrived while P13 ran
Details are in `09_experiments_P8_P12_ssl_series.md`. Commit times are from `git log` of `results/*/README.md`.

### Known before the audit (by 11:24 IST, 11 Oct)
**P8 (10% labels, joint BN, SSL labelled view; scored 10 Oct night)**
- No unlabelled loss passed against its loss-off control.
- The loss-off control was below supervised: D − A crack IoU −0.013 [−0.028, −0.001], inactive −0.101 [−0.171, −0.031] (`results/p8/README.md`).

**P9 (10%, 11,938-cell external pool; committed 06:42 IST)**
- Cx − Dx passed on inactive IoU (+0.056), but not robustly over cells.
- Cx did not beat hard PL (`results/p9/README.md`).

**P10 (5% labels; committed 07:53 IST)**
- No loss passed.
- One seed in three collapsed under both hard and tolerant PL.
- The loss-off control was far below supervised: D5 − A5 −0.055 crack IoU (`results/p10/README.md`, `to_human/directions_2026-10-10.md` §0.1).

At 05:54 UTC (11:24 IST) on 11 Oct the user wrote: "cant believe bro, supervised beating ssl, hows that possible, so many papers showed it, we doing something wrong? be skeptical ... look if anything wrong with our experiment" (`docsrc/user_messages.md`). That message started the audit below. P13 was locked at 11:51 IST (commit `78df5ea`).

### Arrived while P13 was locked and running
**P11 (10%, matched labelled view; runs 06:02 to 13:50 IST, committed 14:03 IST)**
- Cm − Dm passes on inactive IoU (+0.071) and crack relF1@2 (+0.018).
- Cm − A passes too: +0.071 and +0.013 (`results/p11/README.md`).

**P12 (5%, matched view; cv02 runs ended 16:09 IST, committed 16:17 IST)**
- Cm5 − Dm5 passes on crack: +0.023 crack IoU, +0.040 relF1@2.
- But Cm5 − A5c fails: +0.006 / +0.003 / +0.015.
- The loss-off control was below supervised on crack: Dm5 − A5c −0.017 [−0.024, −0.010] (`results/p12/README.md`).

---

## The P13 audit (11 Oct, morning)

### Question
Is something in the Mean Teacher implementation or design making SSL look worse than it is?

### What was checked in the code (no bug found)
Listed in `protocols/P13_cutmix_separate_bn.md`, "Why this exists":
- Teacher and student views share geometry (the same flips and rotations), so pseudo-labels line up with the student's input.
- The EMA update covers the BN buffers, not only the weights.
- The teacher is detached (no gradient) and in eval mode.
- The evaluated weights are the teacher's.
- No unlabelled image overlaps the test set.

### Two design deviations from the SSL methods that report gains

**1. Weak perturbation.**
- The student's strong view was only ±0.25 brightness/contrast jitter plus mild noise.
- The unlabelled loss stayed about 10× below the supervised loss through training: 0.004 vs 0.038 at step 20,000 in P10 C5 s0.
- The teacher was confident on 94 to 97% of unlabelled pixels, and the student already agreed there.
- French et al. (BMVC 2020) show that segmentation consistency needs mask-based mixing such as CutMix.

**2. Joint BN.**
- Unlabelled images shared the student's BN batch with labelled images.
- With the loss off, this alone cost the matched pipeline at 5% between −0.015 and −0.028 crack IoU against supervised (gaint gDm5 s3/s4 vs A5).
- Swapping only the unlabelled pool, still with the loss off, moved the control by up to 0.09 IoU (P9, P10).

### BN recalibration diagnostic (`results/p13_audit/bn_diag.py`, `bn_diag.log`, `bn_diag.json`)
**What it did.** Training was frozen; nothing was retrained. For each final checkpoint (teacher for MT runs), the BN running statistics were scored three ways:
- as trained ("orig");
- recomputed on the run's own labelled images ("own");
- recomputed on all 478 train images ("train").

Test, revised masks, argmax.

**Results.** Crack IoU / inactive IoU, mean of 3 seeds. These are the numbers the P13 protocol quotes; per-seed values are in `bn_diag.log`.

| Arm (checkpoint) | as trained | BN from all 478 train images |
|---|---|---|
| P10 A5 (supervised 5%, gaint) | 0.298 / 0.277 | 0.310 / 0.302 |
| P10 D5 (loss off, 5%) | 0.243 / 0.243 | 0.250 / 0.268 |
| P10 Dx5 (loss off, external pool) | 0.275 / 0.198 | 0.285 / 0.282 |

- Per seed, P6 L3 10% (supervised, cv02) barely moves: crack 0.394 / 0.399 / 0.394 as trained vs 0.396 / 0.401 / 0.393 recalibrated.
- "own" recalibration lowers scores slightly for A5, D5, C5 and P6 L3 10% (e.g. D5 s0 crack 0.238 → 0.218). For the external-pool arms it is mixed: Dx5 inactive rises (s0 0.174 → 0.246), Cx5 crack falls (`bn_diag.log`).

**Reading.**
- Recalibration lifts every arm by about +0.01 crack, but the D5 − A5 gap stays at about −0.06.
- So the handicap is in the trained weights, not in the statistics used at test time.
- Fixing BN after training cannot remove it; the forward pass during training has to change. Hence P13's separate forward.

### GPU smoke runs (`results/p13_audit/smoke_gpu.log`)
- 100-step runs of arms A, Ds, CsM and BsM on cv02 all returned rc = 0.
- The check: `student(Ds) == supervised(A) bitwise: True tensors differing: 0 of 350`.
  - With the separate forward and λ = 0, the SSL student is the supervised run, bit for bit.
  - This is why P13 Amendment 1 could drop the Ds5 arm and use the supervised run as the loss-off control.

---

## P13: separate-BN forward and CutMix, Mean Teacher at 5% labels

### Question
Once the two design deviations are removed, does Mean Teacher with tolerant pseudo-labels beat a step-matched supervised baseline at 5% labels (23 labelled cells)?

### Why
- The audit found no bug but two deviations from the literature (above).
- P12 had a loss effect on crack, but no net gain over supervised on cv02, and the two machines disagreed.

### Setup
**Protocol**
- Locked 11 Oct 11:51 IST (commit `78df5ea`; protocol text ~11:55), before any training run (only 100-step smoke runs had run).
- Amendment 1 at 12:51 IST (commit `8622f67`; protocol text ~13:00), before any P13 run (the first started 13:30 IST).

**Code:** commit `bac5264` (gaint branch `p13`; cv02 `/tmp/noob_el/el_p13`). This is P12's `24590fb` plus two opt-in switches:
- `ssl.student_forward=separate`;
- `ssl.cutmix_p=0.5`.

Box area is U(0.02, 0.4) of the image, aspect U(0.3, 3.33), as in UniMatch. Draws are a pure function of (seed, step). Tests: `tests/test_ssl_split.py`; 197 pass.

**Fixed for all arms (P12's options verbatim)**
- Data and model: in-domain unlabelled pool (the rest of the train split, 455 cells at 5%); revised masks; split seed 0; L3 base (`smp_unetpp` = U-Net++ with an ImageNet ResNet-34 encoder, `ce_dice`).
- Batches and steps: labelled batch 8 + unlabelled batch 8; 20,000 steps; λ ramp as above; final EMA teacher weights.
- Options: `ssl.labeled_aug=supervised`; `ssl.student_forward=separate` in every arm.
- No tuning: `cutmix_p`, the box law and every other value were fixed in advance.

**Amendment 1** (driven by the user's one-day deadline and their own rule of ≥ 5 seeds for effects < 0.05):
- **Scope:** 5% only; the 10% arms dropped. Supervised crack moves only +0.002 from 10% to 20% (P6), so 10% has little crack headroom.
- **Ds5 dropped:** the separate-forward λ = 0 student equals supervised bit for bit. So A5c is the loss-off control, and rules 2 and 3 become the same contrast. The EMA-only effect is not measured.
- **No gaint arms:** gaint ran P15 instead.

**Arms**

| Arm | Run names | Unlabelled loss | CutMix | Seeds |
|---|---|---|---|---|
| A5c | `p12_A_5pct` s0–2 (P12, `24590fb`) + `p13_A_5pct` s3–4 | none (supervised) | – | 5 |
| Cs5 | `p13_Cs_5pct` | tolerant PL | no | 3 |
| CsM5 | `p13_CsM_5pct` | tolerant PL | 0.5 | 5 |
| BsM5 | `p13_BsM_5pct` | hard PL (≥ 0.95) | 0.5 | 3 |

**Runs**
- 13 on cv02 (RTX A6000), 11 Oct 13:30 to 21:04 IST.
- All 26 train/rescore steps returned rc = 0 (`results/p13/README.md`).
- The two halves of A5c agree: P12 seeds vs P13 seeds n.d. on all primaries (`results/p13/p13_rules.txt`).

### Locked rules (`protocols/P13_cutmix_separate_bn.md` + Amendment 1)
**Primary claim:** CsM5 − A5c on 5 vs 5 seeds, P8 rule 1.

Secondary, all reported:
- BsM5 − A5c and Cs5 − A5c;
- CsM5 − Cs5 (the CutMix effect, rule 4);
- CsM5 − BsM5 (tolerant vs hard under CutMix, rule 5);
- Cs5 − Cm5 (separate vs joint BN, rule 6, descriptive).

Also required:
- width check (relP@2 drop > 0.05);
- gap closed;
- image bootstrap and leave-top-3-out on every rule 2/3 contrast;
- the rare_frac collapse watch at steps 4,000 and 20,000;
- E1 per-cell metrics as secondary.

### Results
Test, revised labels, mean ± sd over seeds (`results/p13/README.md`):

| Arm | Seeds | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A5c: supervised 5% | 0–4 | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.892±0.016 | 0.287±0.007 | 0.253±0.041 |
| Cm5 (P12): tolerant PL, joint BN | 0–2 | 0.311±0.010 | 0.274±0.139 | 0.737±0.014 | 0.857±0.077 | 0.329±0.016 | 0.348±0.121 |
| Cs5: tolerant PL, separate BN | 0–2 | 0.308±0.007 | 0.359±0.042 | 0.737±0.008 | 0.878±0.035 | 0.312±0.011 | 0.388±0.052 |
| CsM5: Cs5 + CutMix | 0–4 | 0.317±0.011 | 0.370±0.026 | 0.752±0.016 | 0.874±0.036 | 0.329±0.014 | 0.420±0.028 |
| BsM5: hard PL, separate BN, CutMix | 0–2 | 0.340±0.004 | 0.366±0.007 | 0.771±0.008 | 0.903±0.017 | 0.373±0.010 | 0.433±0.013 |
| L3 10% (P6) | 0–2 | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6) | 0–2 | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

Per seed: every SSL seed's test inactive IoU (0.318 to 0.403) is above every A5c seed's (0.192 to 0.284). The per-seed table, with val numbers, is in `results/p13/README.md`.

### Verdicts (locked rules)
Each cell gives Δ, then the rule threshold in brackets (`results/p13/p13_rules.txt`).

| Contrast | Role | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| CsM5 − A5c (5 vs 5) | primary (rules 2 and 3) | +0.014 (0.016) | +0.117 (0.052) | +0.033 (0.025) | **passes**; width check relP@2 −0.019, ok |
| BsM5 − A5c | secondary | +0.036 (0.011) | +0.113 (0.043) | +0.052 (0.019) | passes on all three; width ok |
| Cs5 − A5c | secondary | +0.004 (0.012) | +0.105 (0.065) | +0.018 (0.019) | passes on inactive only |
| CsM5 − Cs5 (CutMix) | rule 4 | +0.010 (0.015) | +0.012 (0.057) | +0.015 (0.020) | n.d. |
| CsM5 − BsM5 (tolerant vs hard) | rule 5 | −0.022 (0.014) | +0.004 (0.031) | −0.019 (0.020) | tolerant **worse** on crack IoU |
| Cs5 − Cm5 (separate vs joint BN) | rule 6, descriptive | −0.003 (0.014) | +0.084 (0.167) | +0.001 (0.018) | n.d. (Cm5 inactive sd is 0.139) |

**Gap closed**, (X − A5c) / (L3 100% − A5c):

| Arm | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| CsM5 | 8% | 67% | 21% |
| BsM5 | 21% | 64% | 33% |
| Cs5 | 2% | 60% | 11% |

### Robustness
Paired image bootstrap (2,000 resamples). Each cell gives Δ, the 95% CI, then Δ without the top-3 cells (`results/p13/README.md`, `results/e1/e1_p13.md`).

| Contrast | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| CsM5 − A5c | +0.014 [−0.004, +0.027]; +0.003 | +0.117 [+0.042, +0.189]; +0.103 | +0.033 [+0.006, +0.055]; +0.020 |
| BsM5 − A5c | +0.036 [+0.021, +0.048]; +0.031 | +0.113 [+0.028, +0.201]; +0.107 | +0.052 [+0.030, +0.072]; +0.048 |
| Cs5 − A5c | +0.004 [−0.015, +0.018]; −0.009 | +0.105 [+0.025, +0.179]; +0.077 | +0.018 [−0.015, +0.043]; −0.003 |
| CsM5 − Cs5 | +0.010 [+0.004, +0.017]; +0.012 | +0.012 [−0.006, +0.038]; +0.026 | +0.015 [+0.004, +0.029]; +0.022 |
| CsM5 − BsM5 | −0.022 [−0.031, −0.016]; −0.027 | +0.004 [−0.022, +0.026]; −0.004 | −0.019 [−0.035, −0.008]; −0.029 |
| Cs5 − Cm5 | −0.003 [−0.014, +0.007]; −0.006 | +0.084 [+0.030, +0.143]; +0.079 | +0.001 [−0.023, +0.020]; −0.006 |

- **The primary claim's two passing metrics are robust over cells.** Both CIs are above 0, and both survive removal of the top 3 cells.
- **Source split, CsM5 − A5c:**
  - Inactive: CFVS/BMRK/SDLE +0.114 [+0.034, +0.190]. In CSIR/ARTS, all the inactive pixels sit in 3 cells.
  - Crack IoU: CFVS/BMRK/SDLE +0.020 [+0.004, +0.034]; CSIR/ARTS −0.022 [−0.048, +0.003].
- **BsM5's crack gain holds in both source groups:** CFVS/BMRK/SDLE +0.037 [+0.021, +0.051]; CSIR/ARTS +0.028 [−0.000, +0.047].
- **Cs5's crack is worse on CSIR/ARTS:** −0.041 [−0.071, −0.013].

### Collapse watch
Test of whether pseudo-labels for rare classes vanish during training, as in P10 seed 2 (`results/p13/README.md`).

| Run | step 4,000 conf_frac / rare_frac | step 20,000 conf_frac / rare_frac |
|---|---|---|
| Cs5 s0 / s1 / s2 | 0.862 / 0.0079; 0.866 / 0.0087; 0.865 / 0.0065 | 0.956 / 0.0083; 0.956 / 0.0082; 0.958 / 0.0071 |
| CsM5 s0 / s1 / s2 | 0.861 / 0.0079; 0.862 / 0.0084; 0.863 / 0.0066 | 0.953 / 0.0101; 0.949 / 0.0109; 0.954 / 0.0081 |
| CsM5 s3 / s4 | 0.857 / 0.0078; 0.869 / 0.0064 | 0.957 / 0.0081; 0.952 / 0.0070 |
| BsM5 s0 / s1 / s2 | 0.869; 0.874; 0.871 (rare_frac not logged by `confidence_ce`) | 0.965; 0.965; 0.965 |

- No collapse: rare_frac holds or rises in every logged run.
- **CutMix makes the unlabelled loss matter more.** Unlabelled / supervised loss ratio at step 20,000, seed 0:

  | Arm | Ratio |
  |---|---|
  | Cs5 | 0.46 |
  | CsM5 | 0.77 |
  | BsM5 | 0.98 |

  The audit's concern was a ratio of about 0.1 in P10.

### Secondary
**Bin-0 share** (ground-truth pixels scored < 0.001), crack / inactive:

| Arm | crack | inactive |
|---|---|---|
| A5 s3–4 | 0.572 | 0.729 |
| Cs5 | 0.528 | 0.497 |
| CsM5 | 0.500 | 0.449 |
| BsM5 | 0.440 | 0.442 |

SSL lowers confident misses, most for inactive.

**Validation disagrees with test on inactive.**

| Arm | val inactive IoU | val crack IoU |
|---|---|---|
| A5c | 0.106 | 0.278 |
| Cs5 | 0.098 | 0.283 |
| CsM5 | 0.081 | 0.272 |
| BsM5 | 0.061 | 0.300 |

- Val has 54 cells. Only 6 contain inactive, and 3 of them hold 89% of val's inactive pixels.
- Test has 16 inactive cells; 3 hold 59%.

**Across fractions (descriptive):**
- Every 5% SSL arm's test inactive IoU (0.36 to 0.37) is above supervised at 10% (0.294).
- On crack, every 5% arm stays well below supervised at 10% (0.308 to 0.340 vs 0.396).

**E1 per-cell metrics, secondary** (`results/e1/e1_p13.md`)

Test, CsM5 − A5c:

| Metric | Δ | 95% CI |
|---|---|---|
| inactive cell IoU | +0.119 | [+0.036, +0.211] |
| crack tolF1 | +0.008 | [−0.022, +0.034] |
| crack length error | −0.076 | [−0.155, +0.013] |

BsM5 − A5c, crack tolF1: +0.036 [+0.009, +0.064].

On the 106 unseen-module extension cells:

| Contrast | Metric | Δ | 95% CI |
|---|---|---|---|
| CsM5 − A5c | inactive cell IoU | +0.467 (A5c 0.033 → CsM5 0.500) | [+0.322, +0.592] |
| CsM5 − A5c | crack IoU | +0.001 | [−0.011, +0.012] |
| CsM5 − A5c | crack false alarm | +0.027 | [−0.024, +0.085] |
| BsM5 − A5c | crack IoU | +0.012 | [+0.004, +0.020] |
| BsM5 − A5c | crack relF1@2 | +0.046 | [+0.018, +0.072] |
| Cs5 − Cm5 | crack false alarm | −0.095 | [−0.141, −0.050] |

The last row: separate BN removes most of the false-alarm rise that joint-BN tolerant PL showed on unseen modules in P11 and P12.

### Reading
- **Primary claim passes and is robust over cells.** At 5% labels, Mean Teacher with tolerant PL, separate BN and CutMix beats a 5-seed supervised baseline on inactive IoU (+0.117) and crack relF1@2 (+0.033). Crack IoU is n.d. (+0.014).
- **Inactive.** Every separate-BN SSL arm gains +0.10 to +0.12 on test, robust over cells, and more on unseen modules. Val does not show it; val has 6 inactive cells.
- **Crack.**
  - Tolerant PL alone, against a clean control, adds about 0 (Cs5 − A5c +0.004).
  - P12's crack "loss helps" result (Cm5 − Dm5 +0.023) was measured against a joint-BN control sitting 0.017 below supervised, so it mostly offset that handicap.
  - CutMix adds about +0.010: robust over cells, n.d. on seeds.
  - Hard PL with CutMix (BsM5) gives the largest crack gain, +0.036, robust over cells and source groups. But it has 3 seeds and is a secondary contrast. Under CutMix, tolerant is worse than hard on crack (−0.022).
- **Update, 13 Oct (P13 Amendment 2, see P17 below):** with 5 seeds BsM5 − A5c is +0.029 / +0.107 / +0.045 and still passes; CsM5 − BsM5 is n.d. on all three.
- **Limits.** BsM5 had 3 seeds (5 since Amendment 2); there is no gaint replication; the EMA-only effect is not measured; one split.

### Next
P13's validation numbers fed P16's recipe choice (below). A hard-PL + CutMix arm at 20% or 50% was mentioned to the user as a possible exploratory follow-up. It would be test-informed, so it must be labelled exploratory, and nothing is launched without the user's go.

---

## P14: offset-tolerant supervised loss on human labels (E2; directions row 1)

### Question
Human crack labels have the same 1 to 2 px ambiguity as teacher pseudo-labels:
- old vs revised labels agree at 0.73 to 0.81 IoU but 0.98 within 2 px (P3);
- crack pseudo-labels are 0.59 precise pixel-exactly but 0.96 within 2 px (P5).

Does the tolerant rule help when applied to human labels?
- (a) Does it make training on the noisier old labels closer to training on the revised ones?
- (b) Does it help on the revised labels themselves?

### Why
- `to_human/proposal_reframe_2026-10-11.md` noted that five SSL protocols had run while none of the "strong, cheap" directions had: tolerance-aware supervision (row 1), pretraining without PL (row 3), transfer (row 5).
- P14 is row 1; P15 is rows 3 and 5.

### Setup
**Protocol and code**
- Locked 11 Oct 12:55 IST (commit `c9f5562`, together with P15), before any P14 run (the first started 14:42 IST). The protocol text says ~13:45, later than the commit that contains it.
- Code `be67787` (branch `p14`, cv02 `/tmp/noob_el/el_p14`).
- `loss.supervised=tol_dice` is `ce_dice` with its CE replaced by `TolerantPLLoss` applied to the ground truth:
  - rare-class labels (crack id 14, inactive id 11) are credited if the class is predicted within R = 2 px;
  - head-class pixels within 2 px of a rare label are not scored;
  - everything else is plain CE;
  - the Dice term stays pixel-exact.
- At R = 0 it equals `ce_dice` (tested); 205 tests pass.

**Arms:** cv02, 10% labels (47 cells), split seed 0, seeds 0–2, P6 L3 options verbatim, one change each.

| Arm | Run names | Training labels | Loss |
|---|---|---|---|
| L3 (reference, P6) | `p6_L3_10pct` | revised (E-SCDD) | `ce_dice` |
| L3o | `p14_L3o_10pct` | old (`masks_coded`, release 20211104) | `ce_dice` |
| L3To | `p14_L3To_10pct` | old | `tol_dice`, R = 2 |
| L3T | `p14_L3T_10pct` | revised | `tol_dice`, R = 2 |

**Runs:** 9, 11 Oct 14:42 to 19:34 IST, all rc = 0. Scored on the revised test labels.

### Locked rules
1. **Label-noise gap:** G = L3 − L3o on crack IoU and crack relF1@2. The gap exists if it passes rule-1 arithmetic.
2. **Recovery:** on a metric with a gap, all of:
   - L3To − L3o passes rule-1 arithmetic;
   - it is ≥ 0.5·G;
   - the relP@2 drop vs L3o is ≤ 0.05.
3. **Tolerance on revised labels:** L3T − L3 under rule 1, plus the width check.
4. **Robustness:** image bootstrap and leave-top-3-out on rules 2 and 3; inactive reported with the 3-cell caveat.

### Results (`results/p14/README.md`)

| Arm | Train labels | Loss | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|---|
| L3o | old | CE+Dice | 0.314±0.009 | 0.309±0.054 | 0.733±0.009 | 0.895±0.006 | 0.324±0.007 | 0.317±0.054 |
| L3To | old | tolerant | 0.310±0.009 | 0.319±0.003 | 0.728±0.005 | 0.921±0.003 | 0.300±0.011 | 0.311±0.009 |
| L3 (P6) | revised | CE+Dice | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3T | revised | tolerant | 0.398±0.005 | 0.331±0.016 | 0.816±0.007 | 0.907±0.008 | 0.380±0.006 | 0.336±0.021 |
| L3 100% (P6) | revised | CE+Dice | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

### Verdicts
Each cell gives Δ, then the threshold.

| Rule | Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| 1. gap G | L3 − L3o | +0.082 (0.011) | −0.015 (0.066) | +0.081 (0.011) | gap exists on crack IoU and relF1@2 |
| 2. recovery | L3To − L3o | −0.004 (0.015) | +0.010 (0.063) | −0.005 (0.012) | **fails**: 0% of G recovered (≥ 50%, i.e. +0.041, needed). relP@2 rises 0.027, so no width flag |
| 3. tolerance on revised | L3T − L3 | +0.003 (0.010) | +0.037 (0.028) | +0.002 (0.010) | **passes** on inactive IoU, none worse; width check −0.003, ok |

### Robustness (image bootstrap, 2,000 resamples)

| Contrast | Class | Δ | Without top-3 | 95% CI | P(Δ > 0) |
|---|---|---|---|---|---|
| L3 − L3o | crack | +0.082 | +0.100 | [+0.046, +0.129] | 1.00 |
| L3To − L3o | crack | −0.003 | −0.001 | [−0.013, +0.006] | 0.22 |
| L3T − L3 | crack | +0.003 | +0.006 | [−0.003, +0.010] | 0.82 |
| L3T − L3 | inactive | +0.037 | +0.028 | [−0.016, +0.093] | 0.88 |

- **The label-noise gap is robust** in both source groups: CSIR/ARTS +0.197 [+0.080, +0.241]; CFVS/BMRK/SDLE +0.062 [+0.030, +0.112].
- **The rule-3 inactive gain is not robust over cells.** Its CI includes 0, and in CSIR/ARTS all inactive pixels are in 3 cells (Δ without them 0.000).

### Secondary
- **Tolerance lowers crack AP and raises confident crack misses; argmax IoU does not change.**

  | | crack AP | crack bin-0 share |
  |---|---|---|
  | L3 → L3T | 0.400 → 0.380 | 0.422 → 0.441 |
  | L3o → L3To | 0.324 → 0.300 | 0.550 → 0.595 |

  The tolerant rule credits a prediction anywhere within 2 px, so the exact ground-truth pixel is pushed less.
- **Scored on the old labels, the revised-label model still wins:** L3 vs L3o crack IoU 0.351 vs 0.332, relF1@2 0.791 vs 0.758. The gap is not only "trained on the version it is scored on".
- **E1:**
  - Test: tolerance on old labels makes per-cell crack detection worse. L3To − L3o tolF1 −0.041 [−0.066, −0.020]; length error +0.079 [+0.011, +0.153].
  - Unseen modules: the label revision transfers (L3 − L3o crack IoU +0.030 [+0.012, +0.048], relF1@2 +0.068 [+0.021, +0.110]).
  - L3T − L3 there: inactive cell IoU +0.088 [+0.005, +0.193], crack false alarm +0.041 [−0.008, +0.091] (`results/e1/e1_p14.md`).

### Reading
- **(a) No.** The old vs revised gap (+0.082 crack IoU) is large and robust, and tolerance recovers none of it. So the old labels differ from the revised ones by more than a 1 to 2 px offset that a tolerant loss can absorb. The revision joined and widened dotted labels (P3), which is a change in what is labelled, not just where.
- **(b) Weak.** It passes the locked rule on inactive (+0.037), but is not robust over cells; crack is unchanged; crack AP is lower.

### Next
- Not claimed: tuning R, a tolerant Dice term, other fractions or splits.
- P14 strengthens claim 1 of the evidence table (label version matters more than any SSL effect; `11_results_synthesis_and_claims.md`).

---

## P15: UCF-EL-pretrained encoder vs ImageNet init (E3; directions rows 3 and 5). Done

### Question
Does an encoder further trained on UCF-EL's 9,562 labelled EL cells beat the ImageNet encoder when fine-tuned on BenchmarkEL with few labels?

### Why
P4's frozen-feature probe showed that pretrained features carry most of the crack and inactive signal:
- ImageNet ResNet-50 vs random: +0.30 crack AP;
- ImageNet ResNet-50 vs our own trained encoder: +0.08 (`protocols/P15_ucf_encoder_transfer.md`, `results/p4_feature_probe/README.md`).

A better starting encoder might be worth more than pseudo-labels.

### Setup
**Protocol:** locked 11 Oct 12:55 IST (commit `c9f5562`; protocol text ~13:45), before any fine-tuning run (the first started 17:01 IST, `launch_gaint.log`).

**Pretraining (one run, cv02):** `p15_ucf_pre_dlv3p_r34`, el_p13 `bac5264`.
- 11 Oct 07:20 to 08:39 UTC = 12:50 to 14:09 IST, rc = 0 (`/tmp/noob_el/el_p13/reports/p15_pre.log`).
- Recipe: `configs/ucf_deeplab.yaml` (the reproduced Fioresi UCF-EL recipe):
  - DeepLabV3+ with a ResNet-34 encoder (ImageNet init);
  - SGD 5e-3 poly, batch 16, 256 crop, CE with ignore 128;
  - 59,760 steps (100 epochs), all 9,562 UCF train cells, seed 0.
- DeepLabV3+ was used because it evaluates at UCF's variable image sizes. Its ResNet-34 encoder has the same 216 tensors as our U-Net++ encoder.
- Its UCF score is not used for any decision.

**Leakage check:** `results/p15/dedup.py`; 64×64 grayscale, 8 flips/rotations, normalised correlation. UCF train vs BenchmarkEL val + test: maximum 0.79, none ≥ 0.90.

**Transfer:** `model.encoder_init=<pretrained final model>` (commit `be67787`).
- Copies all 216 encoder tensors.
- Sums the first conv over its 3 input channels for our 1-channel model.
- Leaves the decoder fresh.
- On gaint the file is `pretrained/p15_ucf_pre_dlv3p_r34.pth` in worktree `/home/noob/work/el_p14`.

**Arms:** gaint, split seed 0, seeds 0–2, P6 L3 options plus `encoder_init`.

| Arm | Run names | Labels | Reference (gaint, ImageNet encoder) |
|---|---|---|---|
| gU5 | `p15_gU_5pct` | 5% (23) | P10 `p10_A_5pct` (A5) |
| gU10 | `p15_gU_10pct` | 10% (47) | P12 `p12_gA_10pct` (gA10) |

**Scheduling:** two sequential lanes on gaint's single GPU, each waiting for < 20,000 MiB used (`reports/p15/lane.sh`).

**Progress** (`launch_gaint.log`, read-only):
- All 6 runs trained and rescored with rc = 0, 11 Oct 17:01 to 22:26 IST.
- Each run took about 1 h 40 min.
- Post-analysis ran at 22:30 to 22:40 IST (`results/p15/README.md`, `results/e1/e1_p15.md`).

### Locked rules
1. **U helps:** U − reference under P8 rule 1 (any primary passes, none worse), plus the width check (relP@2 drop ≤ 0.05).
2. **Robustness:** image bootstrap and leave-top-3-out.
3. **Descriptive:**
   - gap closed against L3@100% (P6, cv02; cross-machine, descriptive only);
   - gU5 vs gA10: can UCF pretraining stand in for doubling the labels?

Not claimed: MIM or self-supervised pretraining, other UCF recipes, freezing schedules, pretraining length, pooling with cv02.

### Post-analysis (prepared; `scripts/post_p15.sh <cv02 gpu>`)
- Pulls the 6 JSONs.
- Runs `ssl_rules.py` with pairs gU5 = A5, gU10 = gA10, gU5 = gA10, gA10 = L3 10%.
- Copies slim checkpoints to cv02 for E1 scoring.
- Writes `results/e1/e1_p15.md`.

The gA10 = L3 10% pair is P12's rule-7 calibration: gaint and cv02 supervised 10% agree on crack within 0.004 to 0.006, and differ on inactive by about the seed noise (+0.056, threshold 0.057; `results/p12/README.md`).

### Results (`results/p15/README.md`, `p15_rules.txt`)
Test, revised labels, mean ± sd over seeds 0–2, gaint.

| Arm | Encoder init | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 |
|---|---|---|---|---|---|
| A5 (P10) | ImageNet | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 |
| gU5 | UCF-EL | 0.308±0.006 | 0.265±0.046 | 0.723±0.015 | 0.872±0.023 |
| gA10 (P12) | ImageNet | 0.400±0.007 | 0.351±0.046 | 0.820±0.010 | 0.903±0.010 |
| gU10 | UCF-EL | 0.389±0.006 | 0.265±0.023 | 0.806±0.006 | 0.898±0.016 |

The pretraining run itself scored UCF test crack IoU 0.666 and defect mIoU 0.487 (cv02 `experiments/p15_ucf_pre_dlv3p_r34/metrics.json`). Not used for any decision.

### Verdicts (locked rule 1; difference, then threshold in brackets)
| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| gU5 − A5 | +0.0096 (0.0100) | −0.012 (0.083) | +0.015 (0.022) | **fails**: n.d. on all three; crack misses by 0.0004 |
| gU10 − gA10 | −0.012 (0.011) | −0.086 (0.059) | −0.014 (0.013) | **fails: worse on all three** |

Rule 3, descriptive:
- gU5 − gA10: crack −0.092, inactive −0.086, relF1@2 −0.097. UCF pretraining does not stand in for doubling the labels.
- Gap closed against L3 100% (cross-machine): gU5 crack +6%; gU10 crack −16%, inactive −110%.

### Robustness (`results/e1/e1_p15.md`; image bootstrap, 2,000 resamples; Δ [95% CI]; Δ without top-3)
| Contrast | crack IoU | crack relF1@2 | inactive IoU |
|---|---|---|---|
| gU5 − A5 | +0.010 [+0.006, +0.014]; +0.010 | +0.015 [+0.007, +0.023]; +0.014 | −0.012 [−0.051, +0.035]; +0.018 |
| gU10 − gA10 | −0.012 [−0.026, −0.002]; −0.015 | −0.014 [−0.030, −0.004]; −0.020 | −0.086 [−0.135, −0.030]; −0.067 |

- The 10% harm is robust over cells on all three.
- The 5% crack effect is small and consistent over cells, but below the seed threshold, so it is not claimed.
- Unseen modules: gU5 − A5 inactive cell IoU +0.062 [+0.002, +0.122], crack tolF1 −0.034 [−0.068, −0.004]; gU10 − gA10 n.d. on every metric.

### Reading
- With this recipe, related labelled data used as encoder pretraining does not beat ImageNet init: equal at 5%, worse at 10%.
- Possible reasons are untested hypotheses:
  - scale: UCF cells are resized to 295 px and cropped to 256, and UCF crack labels are about 9 to 15 px wide, against about 2 px at 512 px here;
  - only the encoder transfers (DeepLabV3+ head, U-Net++ target);
  - the class definitions differ.
- Input normalisation is identical (mean 0.5, sd 0.25).
- MIM / self-supervised pretraining is still untested.

---

## P16: SSL at 20%, 50% and 100% labels (cv02). Done

### Question
Does SSL beat supervised once labels are not scarce: at 20% (95 cells), 50% (239) and 100% (478, external unlabelled pool only)?

### Why: the user's request
On 11 Oct, ~17:24 IST, the user wrote: "okay why we using 5 or 10% for ssl? they are really low and on phase0 as well they gave bad results, try 20, 50 and 100 of the 592 images ig, correct me if i am wrong" (`docsrc/user_messages.md`). The correction given: there are 582 cells, not 592 (478 train / 54 val / 50 test), and percentages are of the 478 train cells.

The reasoning at locking (`protocols/P16_label_fraction_curve.md`):
- P8 to P13 tested SSL only at 5% and 10%. There, inactive appears in just 2 or 4 labelled cells and the teacher is weakest, so inactive was unmeasurable by construction.
- Segmentation SSL benchmarks report 1/16 to 1/2 of the labels; we had no point above 10%.
- At 100% there is no in-domain unlabelled data, so SSL can only use the external pool (11,938 CSIR/ARTS cells). That asks whether extra unlabelled data helps a fully supervised model.

Counts seen at locking:

| Labels | Labelled cells | of which with inactive | In-domain unlabelled pool |
|---|---|---|---|
| 5% | 23 | 2 | 455 |
| 10% | 47 | 4 | 431 |
| 20% | 95 | 9 | 383 |
| 50% | 239 | 20 | 239 |
| 100% | 478 | – | 0 |

Supervised curve seen at locking (5% and 50% from gaint P10; others from cv02 P6):

| | 5% | 10% | 20% | 50% | 100% |
|---|---|---|---|---|---|
| crack IoU | 0.298 | 0.396 | 0.398 | 0.437 | 0.471 |
| inactive IoU | 0.277 | 0.294 | 0.347 | 0.427 | 0.429 |

### Setup: Part A, supervised references
- Locked 11 Oct 17:28 IST (commit `0d7374c`), before any P16 run (the first started 17:28:55 IST). The protocol text says ~16:50 and dates the user's prompt ~16:35; the transcript has the prompt at 17:24 IST, so those header times are about 35 to 50 min early (`12_decisions_log.md` D31).
- cv02 worktree `el_p13` at `bac5264`, P6's L3 options verbatim.
- P6's `config_used.yaml` for L3 20% equals P13's A5 config except seed and fraction (checked by diff), so P6 seeds 0–2 are pooled with the new seeds.

| Arm | Run names | Labels | New seeds | Pooled with |
|---|---|---|---|---|
| A20 | `p16_A_20pct` | 20% (95) | 3–4 | P6 `p6_L3_20pct` s0–2 |
| A50 | `p16_A_50pct` | 50% (239) | 0–4 | none (P10's A50 ran on gaint) |
| A100 | `p16_A_100pct` | 100% (478) | 3–4 | P6 `p6_L3_100pct` s0–2 |

Progress:
- A20 s3, A20 s4 and A50 s0 are rescored (GPU 5, started 17:28 IST).
- A50 s1–3 run on GPU 1 (from 18:15 IST); A50 s4 and A100 s3–4 on GPU 2 (from 18:42 IST).
- Logs: cv02 `/tmp/noob_el/el_p13/reports/p16/launch.log`, `queue.log`.

### Setup: Part B, SSL arms (Amendment 1)
- Locked 11 Oct 17:35 IST (commit `71ccf31`; protocol text ~17:40), before any P16 SSL run.
- At that point 3 of 13 P13 runs had finished, and none of their numbers had been opened.

**User's choice (between the user's 17:24 prompt and the Amendment commit at 17:35 IST; the protocol text says ~17:00):** "Pick on P13 val (Recommended)", an answer to a multiple-choice question from Claude (session summary 2026-10-11T13:25Z). CutMix on or off is decided by P13's validation numbers, never its test numbers.

**Code:** branch `p16` at `d51b60f` = `bac5264` plus one change: SSL at `labeled_fraction` 1.0 is allowed when `data.unlabeled_pool=external` (it used to raise an error).
- Partial-label paths are unchanged (`tests/test_p16_full_label_ssl.py`; full suite 204 passed).
- cv02 worktree `/tmp/noob_el/el_p16`.

**Automatic recipe selection** (`scripts_cv02/p16b_auto.sh`, in tmux `p16auto` on cv02):
- Waits until P13's CsM5 (s0–4) and Cs5 (s0–2) are rescored with rc = 0, and the Part A queue is empty.
- Score of an arm = mean over the three val primaries (crack IoU, inactive IoU, crack relF1@2) of the seed means.
- CutMix = 0.5 if score(CsM5) > score(Cs5), otherwise off.

**Selection outcome** (`el_p16/reports/p16b/selection.txt`, written ~21:05 IST):

| Arm | val crack IoU | val inactive IoU | val crack relF1@2 | Score |
|---|---|---|---|---|
| CsM5 (5 seeds) | 0.2724 | 0.0807 | 0.699 | 0.3507 |
| Cs5 (3 seeds) | 0.2826 | 0.098 | 0.7151 | 0.3652 |

Result: `CUTMIX=0`. P16 runs the Cs recipe:
- tolerant PL;
- separate BN;
- matched labelled view;
- no CutMix.

On P13 **test**, that was the weakest of the three SSL arms on crack. Test was not used for the choice, per the user's rule. P13 val has 6 inactive cells (see P13 above).

**SSL arms** (P13's Cs options verbatim except fraction and pool; seeds 0–4):

| Arm | Run names | Labels | Unlabelled pool | Supervised reference |
|---|---|---|---|---|
| S20 | `p16_S_20pct` | 20% (95) | in-domain (383) | A20 = `p6_L3_20pct` s0–2 + `p16_A_20pct` s3–4 |
| S50 | `p16_S_50pct` | 50% (239) | in-domain (239) | A50 = `p16_A_50pct` s0–4 |
| Sx100 | `p16_Sx_100pct` | 100% (478) | external (11,938) | A100 = `p6_L3_100pct` s0–2 + `p16_A_100pct` s3–4 |

- **Rules 2 and 3 coincide.** With the separate forward and λ = 0 the student is bit-identical to supervised (P13 smoke), so A is each arm's loss-off control.
- **Launch:** all 15 runs started 21:05 IST in one wave, 3 per GPU on GPUs 0, 3, 4, 5, 6. Each GPU had < 1,000 MiB used; other users had left. The launch log is `el_p16/reports/p16b/launch.log` (times in UTC); there is no `queue.log` for Part B, because the queue ran inside `p16b_auto.sh`, whose output is `el_p16/reports/p16b_auto.log`.
- **End:** the last run was rescored 04:24 IST, 12 Oct. All 30 train/rescore steps have rc = 0.

### Locked rules (as P13)
- **Primary:** S20 − A20, S50 − A50 and Sx100 − A100, each under P8 rule 1, 5 vs 5 seeds. All three reported.
- **Width check:** relP@2 drop > 0.05 flagged.
- **Gap closed:** (S − A) / (A100 − A).
- **Robustness:** image bootstrap (2,000) and leave-top-3-out on every primary contrast; E1 per-cell metrics and the 106-cell extension as labelled secondary.
- **Descriptive:** the SSL gain against label fraction, with P11 (10%), P12 (5%) and P13 (5%), within cv02 only.
- **Not claimed:** tuning at any fraction, other splits, pooling with gaint.

### Post-analysis (prepared, committed `f9f2783`)
- `scripts/post_p16.sh <cv02 gpu>`:
  - pulls 9 supervised and 15 SSL JSONs;
  - per-image and histogram scoring on cv02;
  - `ssl_rules.py` with merges `p16:A20=p6:L3_20pct+p16:A_20pct` and `p16:A100=p6:L3_100pct+p16:A_100pct`;
  - the pairs above, plus pooling checks P6 vs P16 seeds at 20% and 100%;
  - bootstrap and source split; bars; E1 scoring and aggregation to `results/e1/e1_p16.md`.
- `scripts/p16_curve.py`: plots supervised vs SSL by label fraction, with the 5% SSL point taken from P13 (Cs5, since CutMix is off). 10% has no separate-BN SSL arm, since P11's Cm used joint BN, a different recipe. It also prints a table.

### Results
Source: `results/p16/README.md`. Test, revised labels, mean ± sd over seeds 0–4.

| Arm | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 |
|---|---|---|---|---|
| A20 (P6 s0–2 + P16 s3–4) | 0.398±0.006 | 0.361±0.037 | 0.822±0.010 | 0.942±0.006 |
| S20 | 0.358±0.060 | 0.390±0.026 | 0.752±0.096 | 0.789±0.187 |
| A50 | 0.408±0.076 | 0.412±0.012 | 0.808±0.117 | 0.839±0.203 |
| S50 | 0.447±0.005 | 0.418±0.027 | 0.861±0.004 | 0.933±0.002 |
| A100 (P6 s0–2 + P16 s3–4) | 0.435±0.078 | 0.436±0.013 | 0.828±0.105 | 0.853±0.187 |
| Sx100 (external pool) | 0.463±0.013 | 0.439±0.017 | 0.868±0.013 | 0.925±0.035 |

The large sds (A50, A100, S20) come from one test cell; see "The noisy test cell" below.

### Verdicts (locked rules)
Each cell gives the difference, then the threshold in brackets.

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| **S20 − A20** | −0.040 (0.069) | +0.029 (0.052) | −0.070 (0.111) | **fails** (n.d. on all three); width flag relP@2 −0.153 |
| **S50 − A50** | +0.039 (0.088) | +0.006 (0.034) | +0.053 (0.135) | **fails** (n.d. on all three) |
| **Sx100 − A100** | +0.028 (0.091) | +0.003 (0.025) | +0.040 (0.122) | **fails** (n.d. on all three) |

- **Gap closed** is not informative for crack and relF1@2: failed seeds pull down A100's and A50's means. Without the noisy cell: S20 +3% / +38% / +0%, S50 +8% / +11% / −7% (crack / inactive / relF1@2).
- **Pooling check** (P6 vs P16 seeds of the same supervised arm): n.d. at 20% and 100%. At 100% the crack and relF1@2 verdicts are n.d. only because one P16 seed failed. Without the cell the halves agree on crack within 0.002.

### Robustness
- Image bootstrap: every CI includes 0. Crack: S20 −0.040 [−0.090, +0.011], S50 +0.039 [−0.003, +0.070], Sx100 +0.028 [−0.004, +0.047].
- Source split: in the 29 CFVS/BMRK/SDLE cells, crack Δ is +0.001, +0.001 and −0.003. All the crack movement is in CSIR/ARTS, which holds the noisy cell.
- Leave-top-3-out removes cells by GT area. It cannot catch this cell, whose damage is false positives.

### The noisy test cell (diagnostic, found after the runs)
- **What happens.** In 4 of the 24 runs (S20 s2 and s4, A50 s2, A100 s3), the model labels 15–31% of test cell `CSIR_00070_r8_c4` as crack.
  - That is 39k–80k false-positive pixels, against a true crack area of 787 px.
  - The run's pooled crack IoU drops by 0.11–0.18.
  - Sx100 s3 does it partly (8,093 px). Most other runs put 0 to about 1,200 px there.
- **The models are confident** (median p(crack) 0.92–0.99), the same in bf16 and fp32 (`results/p16/diag_csir70.txt`). The false crack follows the image grain.
- **The cell is the noisiest of all 582** (robust noise sigma 46.0; median 1.48; next unrelated cell 10.4). The only similar cell is a train cell from the same module, `CSIR_00070_r7_c2` (43.0) (`results/p16/cell_noise_rank.txt`).
- **It is not specific to SSL** (4 events, so only a count): 2 of 15 supervised and 2 of 15 SSL runs fail. Val is unaffected.
- **It has happened before.** P6 `p6_L0_10pct_s1` (71,376 FP px; crack IoU 0.261, or 0.360 without the cell). That outlier makes up most of P6's secondary bootstrap result "L1 − L0 crack IoU +0.048" (about +0.010 without it; doc 08). In P7 to P15 no run put more than 4,600 FP px there.
- **Post-hoc check without the cell (not a locked rule).**
  - S20 − A20: crack +0.002, inactive +0.029, relF1@2 +0.000.
  - S50 − A50: +0.002, +0.002, −0.001.
  - Sx100 − A100: −0.002, +0.002, −0.002.
  - All are n.d. with thresholds of 0.010 on crack. **The verdict does not change.**
  - Files: `results/p16/sensitivity_excell.txt` and `fig_p16_curve_excell.png`.

### Secondary
- **Unlabelled-loss share.** At step 20,000, loss_con / loss_sup is 2–7% at 20–100% labels, against 46% for P13 Cs5 at 5%. The consistency loss is about the same size; the supervised loss is 6–20× larger because there are more labelled cells to fit.
- **Collapse watch.** No collapse: rare_frac holds or rises. On the external pool it rises 6–49× from step 4,000 to 20,000.
- **E1, test.** Per-cell crack tolF1 and inactive cell IoU: n.d. for all three contrasts. One metric excludes 0: S50 − A50 inactive area error +0.189 pp [+0.056, +0.388], worse for SSL.
- **E1, unseen modules (106 cells):**
  - S20 − A20: inactive cell IoU +0.179 [+0.011, +0.385]; crack false alarms +0.046 [+0.018, +0.076] (worse).
  - S50 − A50: crack IoU +0.019 [+0.007, +0.031]; crack relF1@2 +0.047 [+0.019, +0.077]; inactive cell IoU +0.197 [+0.034, +0.403].
  - Sx100 − A100: n.d. on every metric.
- **Curve (descriptive, cv02 only),** SSL − supervised, all cells / without the noisy cell:

  | Labels | crack IoU | inactive IoU |
  |---|---|---|
  | 5% (P13 Cs5) | +0.004 / +0.007 | +0.105 / +0.109 |
  | 20% | −0.040 / +0.002 | +0.029 / +0.029 |
  | 50% | +0.039 / +0.002 | +0.006 / +0.002 |
  | 100% (external) | +0.028 / −0.002 | +0.003 / +0.002 |

### Reading
- **Under the locked rules, this SSL recipe does not beat supervised at 20%, 50% or 100% labels.** This holds with and without the noisy cell.
- **The inactive gain seen at 5% shrinks as labels grow** and is undetectable from 20% up. On unseen modules an inactive gain remains at 20% and 50% (secondary).
- **Crack:** nothing detectable on test at any fraction. Without the noisy cell (post hoc), every crack Δ is within ±0.003. S50 helps crack a little on unseen modules (secondary).
- **External pool at 100%:** n.d. on every primary, test and unseen modules. Earlier external-pool results were mixed: P9 inactive passed (not robust), P10 was worse on crack relF1@2, P11 gained unseen-module inactive, P12 had no effect.
- **Limits:**
  - one recipe (CutMix off by the locked val rule; hard PL not run at 20 to 100%);
  - λ fixed at 1, so the unlabelled term is small next to the supervised one at these fractions;
  - one split; no gaint replication.
- **Open (user decisions):**
  - whether to adopt "without `CSIR_00070_r8_c4`" as a standing robustness check;
  - whether to run an exploratory hard-PL + CutMix arm at 20% or 50%, which would be test-informed.

### Known wording mismatch
Amendment 1 says the selector writes `reports/p16/selection.txt`. The script writes `el_p16/reports/p16b/selection.txt`, and the post-analysis copies it to `results/p16/selection.txt`.

---

## P17: SKCDF-style decoupled decoder on BsM5 (5% labels, cv02). Done 13 Oct

### Question
P13's BsM5 (hard pseudo-labels, separate BN, CutMix) beats supervised at 5% on all three primaries. Does that gain need the labelled decoder to fit pseudo-labels, or does it enter through the encoder?

### Why
- On 13 Oct (~01:30 IST) the user asked: "how about we try the DCA paper and SKCDF? we still have 16hrs for experimenting, is there anything more important left".
- Claude recommended:
  - skip DCA (CVPR 2026): a 3D V-Net method with three expert decoders and a head/medium/tail class split, far from a 2D two-class setup, and too much to build and test in 16 h;
  - take SKCDF's (CVPR 2025) first component only, "data flow decoupling", which its own ablation credits with +12.74 of its +19.61 Dice on Synapse at 20%;
  - run it on BsM5, the strongest SSL recipe, and give BsM5 its missing seeds 3–4 (P13 Amendment 2).
- The user: "cool, go with ur calls" (13 Oct ~01:45 IST).

### Setup (`protocols/P17_decoupled_decoder.md`, locked 13 Oct 01:51 IST, commit `5919560`)
- **Code:** commit `f2f20d3` (gaint branch `p17`, worktree `/home/noob/work/el_p17`) = P13's `bac5264` plus one opt-in switch, `ssl.decouple_decoder=true`:
  - the student's unlabelled forward goes encoder → `decoder_u` → `head_u` (deep copies of the labelled decoder and head at step 0), so the unlabelled loss reaches the encoder and `decoder_u` only;
  - after each step `decoder_u ← 0.99 · decoder_u + 0.01 · decoder` (parameters; SKCDF Eq. 6);
  - `decoder_u` has its own optimizer, scheduler and gradient clip, all checkpointed;
  - pseudo-labels still come from the EMA teacher (encoder + labelled decoder), and test uses the teacher, as in P13.
  - Tests: +6 in `tests/test_ssl_split.py`; full suite 203 pass, 7 skipped.
- **Arm:** BsD5 = BsM5 options verbatim + `ssl.decouple_decoder=true`, seeds 0–4, cv02 GPUs 3–7, deployment `el_p17`.
- **References:** BsM5 seeds 0–4 (seeds 3–4 from P13 Amendment 2, run alongside on GPUs 1–2), A5c seeds 0–4.
- **Not taken from SKCDF:** the cross-attention module, auxiliary balanced heads, λ_u = 10, their optimizer, pseudo-labels from the student, inference through `decoder_u` as primary. Name: "SKCDF-style decoupling", never "SKCDF".
- **Built-in pipeline check:** λ = 0 until step 2,000, so BsD5 seed k must equal BsM5 seed k there. **Passed:** all 44 logged lines identical for each of the 5 seeds.
- Runs: 13 Oct 01:55–04:08 IST, all 14 train/rescore steps rc = 0.

### Locked rules
1. **Primary: BsD5 − BsM5** under P8 rule 1, 5 vs 5. Worse: the gain needs the labelled decoder to fit pseudo-labels. Better: keeping pseudo-labels out of it helps. n.d.: any decoder share is below the threshold, reported as a fraction of the BsM5 − A5c gain.
2. Secondary: BsD5 − A5c.
3. Descriptive: `decoder_u` path vs the teacher path.
4. Width check: relP@2 drop > 0.05 flagged.
- Robustness: bootstrap, leave-top-3-out, with and without `CSIR_00070_r8_c4`, collapse watch.

### Results (`results/p17/README.md`)
| Arm | Seeds | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A5c | 0–4 | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | 0.892±0.016 | 0.287±0.007 | 0.253±0.041 |
| BsM5 (s3–4 post hoc, P13 Am. 2) | 0–4 | 0.333±0.011 | 0.360±0.010 | 0.764±0.014 | 0.907±0.014 | 0.367±0.016 | 0.429±0.013 |
| **BsD5** | 0–4 | 0.327±0.003 | 0.371±0.036 | 0.756±0.006 | 0.888±0.012 | 0.310±0.005 | 0.357±0.036 |

BsM5 seeds 3–4 came in lower on crack (0.317, 0.327) than seeds 0–2 (0.335–0.343): the 5-seed mean is 0.333, not 0.340.

### Verdicts (difference, then threshold in brackets)
| Contrast | Role | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|
| **BsD5 − BsM5** | rule 1, primary | −0.006 (0.013) | +0.011 (0.043) | −0.008 (0.017) | **n.d.**; width ok (relP@2 −0.019) |
| BsD5 − A5c | rule 2 | +0.023 (0.010) | +0.117 (0.060) | +0.037 (0.018) | passes on all three |
| BsM5 − A5c (P13 Am. 2) | P13 secondary | +0.029 (0.016) | +0.107 (0.044) | +0.045 (0.023) | passes on all three |
| CsM5 − BsM5 (P13 Am. 2) | P13 rule 5 | −0.015 (0.018) | +0.010 (0.032) | −0.012 (0.024) | **n.d.** (on 3 BsM5 seeds it was "tolerant worse on crack") |

- Rule 1 thresholds as a share of the BsM5 − A5c gain: crack 44%, inactive 41%, relF1@2 39%. A decoder share below about 40% of the gain is not detectable with 5 seeds.
- Point estimates: BsD5 keeps 80% (crack), 110% (inactive), 82% (relF1@2) of BsM5's gain over A5c.

### Robustness
- BsD5 − BsM5 over cells: crack −0.006 [−0.011, +0.002], P(Δ > 0) = 0.06; relF1@2 −0.008 [−0.014, +0.000]; inactive +0.011 [−0.013, +0.038]. The crack lean sits in CSIR/ARTS (−0.020 [−0.028, −0.008]), not in CFVS/BMRK/SDLE (−0.003).
- BsD5 − A5c: all three CIs above 0; top-3 removal keeps +0.019 / +0.107 / +0.032.
- Noisy cell: BsM5 and BsD5 put at most 390 crack FP px on it; no P17 verdict changes without it. Post hoc, CsM5 − A5c crack IoU crosses its threshold without it (+0.016 vs 0.014).
- Collapse watch: conf_frac 0.86–0.87 at step 4,000, 0.96 at 20,000, as BsM5; `rare_frac` is not logged by `confidence_ce`.

### Secondary
- **`decoder_u` path (student encoder + `decoder_u`)**: crack 0.334±0.003, inactive 0.375±0.040. It is above the teacher on crack IoU in all 5 seeds (+0.005 to +0.009). Descriptive.
- **AP drops:** BsD5's teacher has crack AP 0.310 (BsM5 0.367) and inactive AP 0.357 (0.429); bin-0 share 0.526 / 0.544 vs BsM5 0.440 / 0.442. The labelled decoder that never fits pseudo-labels ranks pixels less well, while its argmax IoU stays close.
- **E1, unseen modules (ext), BsD5 − BsM5:** crack tolF1 +0.016 [+0.002, +0.033], crack false alarm +0.049 [+0.011, +0.089], inactive area error −0.065 pp [−0.117, −0.019] (`results/e1/e1_p17.md`).

### Reading
- **The decoupled recipe does as well as BsM5 on argmax metrics within what 5 seeds can resolve.** BsD5's labelled decoder never receives the unlabelled loss, yet BsD5 keeps most of the gain over supervised. So most of the gain reaches the teacher through the shared encoder, not through EMA averaging: at step 20,000 BsD5's EMA teacher and student score the same (within ±0.005; `results/ema_check/README.md`, added after P17). A decoder share below about 40% of the gain cannot be excluded, and crack leans slightly negative over cells.
- **The decoder does carry something:** AP and score histograms are worse when pseudo-labels stay out of the labelled decoder, and the `decoder_u` path is a little better on crack than the teacher.
- **BsM5 at 5 seeds is smaller than at 3** (crack +0.029 vs +0.036 over A5c) and still passes. The P13 rule-5 finding "tolerant worse than hard on crack" no longer holds by the seed rule at 5 vs 5, though the bootstrap still puts it below 0.
- **Limits:** one split, one fraction, cv02 only, no tuning of ω or λ, and SKCDF's other components are not tested.

### Next
Nothing launched. Open to the user: whether P17 enters the deck, and how to word the BsM5 5-seed update.

---

## P18 (EXPLORATORY): the BsM recipe at 10% and 20% labels (13 Oct; `results/p18/README.md`)

### Question and status
- Does the recipe that did best at 5% (BsM: hard PL ≥ 0.95, separate BN, CutMix) still beat supervised at 10% and 20%? Is P16's "no gain from 20% up" a property of the label fraction or of the Cs recipe?
- **Exploratory:** BsM was picked after seeing P13's test cells. Protocol `protocols/P18_bsm_label_fraction.md`, locked 17:31 IST (`a698ec8`) before any run. The user's go: "youve got 3hrs to wrap up ... experiment whatever you think useful".
- cv02, code `bac5264` (`el_p13`), BsM5's options with the fraction and seed changed. BsM20 5 seeds, BsM10 3 seeds; 17:31–19:40 IST, all rc = 0. Pipeline check passed (losses equal the supervised runs' up to step 2,000).

### Results (test, revised labels)
| Arm | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| A10 (P6, 3 seeds) | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 |
| BsM10 (3) | 0.408±0.011 | 0.426±0.021 | 0.827±0.014 |
| A20 (P6 + P16, 5) | 0.398±0.006 | 0.361±0.037 | 0.822±0.010 |
| S20 (P16 Cs recipe, 5) | 0.358±0.060 | 0.390±0.026 | 0.752±0.096 |
| BsM20 (5) | 0.392±0.042 | 0.422±0.024 | 0.804±0.064 |

| Contrast (exploratory arithmetic) | crack IoU | inactive IoU | crack relF1@2 | |
|---|---|---|---|---|
| BsM10 − A10 | +0.012 (0.013) | **+0.132** (0.032) | +0.013 (0.017) | passes, inactive only |
| BsM20 − A20 | −0.006 (0.049) | **+0.060** (0.051) | −0.018 (0.075) | passes, inactive only; width flag (s4) |
| without `CSIR_00070_r8_c4`: BsM10 − A10 | **+0.017** (0.010) | **+0.138** (0.033) | **+0.020** (0.010) | passes on all three |
| without that cell: BsM20 − A20 | +0.013 (0.014) | **+0.061** (0.052) | +0.012 (0.013) | passes, inactive only |
| without that cell: BsM20 − S20 (two changes) | +0.010 (0.013) | +0.032 (0.041) | **+0.011** (0.010) | relF1@2 only |

- **BsM20 s4 fails on the noisy cell** (34,265 crack FP px; crack IoU 0.320, the other seeds 0.397–0.422). Supervised seeds fail there too from 50% up (A50 s2, A100 s3); below 20% no run does.
- Bootstrap over cells: inactive at 10% +0.132 [+0.043, +0.235]; at 20% +0.060 [−0.018, +0.119]. Crack at 10% +0.012 [−0.002, +0.023]; at 20% without the cell +0.013 [−0.002, +0.034].
- Val inactive disagrees at 20% (BsM20 0.374 vs A20 0.452); it agrees at 10% (0.359 vs 0.300).
- Unseen modules (E1 ext, `results/e1/e1_p18.md`): inactive detection F1 +0.41 (10%) and +0.51 (20%), CIs above 0; crack tolF1 +0.05 / +0.07, with more cells falsely flagged as crack (+0.06).
- Figure: `results/p18/fig_p18_curve.png` (supervised, Cs recipe and BsM recipe over 5–100%).

### Reading
- The BsM recipe's inactive gain over supervised does not vanish at 10% or 20%. Its crack gain shrinks to about +0.012 to +0.017, at or just below the threshold.
- P16's "no gain from 20% up" therefore depends at least partly on the recipe, at least for inactive. Which of BsM's two differences from Cs matters is not identified.
- Exploratory; no locked verdict changes. 50% and 100% were not run with BsM.

---

## Follow-up checks after P17 (13 Oct, descriptive, not in any protocol)

### EMA teacher vs student (`results/ema_check/README.md`)
- **Question:** does scoring the EMA teacher instead of the trained student change the numbers? This is doc 13 C11; the P17 reading also depends on it.
- **Done:** the student and teacher weights of BsM5, CsM5 and BsD5 (15 runs, step 20,000) re-scored on test with `scripts_cv02/rescore_weights.py`. The teacher scores reproduce the official JSONs exactly.
- **Result:** teacher − student is within ±0.005 on every metric for every run (mean about −0.001). The cosine schedule ends at learning rate 0, so the EMA catches up with the student.
- **Reading:** the SSL gains are carried by the trained network itself. The EMA-only effect is very likely about 0 (inferred, not measured on Ds5).

### Qualitative panel (`results/qualitative/README.md`, `fig_qualitative_5pct.png`)
- **What:** A5c, CsM5, BsM5 and supervised 100% (seed 3) on the 2 largest-inactive and 2 largest-crack test cells, chosen by GT area before any prediction was looked at.
- **What it shows** (one seed, four cells):
  - on `CFVS_00114_r6_c5`, inactive IoU is 0.28 for A5c and 0.62 to 0.69 for the SSL models (supervised 100%: 0.60);
  - on the largest inactive cell, `BMRK_00073_cell0253`, every model misses most of the labelled inactive area (supervised 100%: 0.05).

### Our models in Pratt 2023's convention (`results/pratt_compare/README.md`)
- **What:** per-image IoU for crack, gridline and inactive, median over the 50 test cells, rule A (cells without the class left out), on the paper's old labels. 23 runs, read-only.
- **Result:** supervised 100% (L3, 5 seeds) 0.354 / 0.303 / 0.443, mean 0.367. The paper's headline 4c (DeepLabv3+) is 0.25 / 0.20 / 0.38, mean 0.28. A5c mean 0.167; BsM5 mean 0.239.
- **Caveats:**
  - the paper's rule is inferred and its numbers are read off Fig. 7;
  - the paper reports single runs, and which release it used is open;
  - our models were trained on the revised masks.
  - Not a like-for-like benchmark claim.

---

## E1: task-aligned, per-cell evaluation and the unseen-module extension

### Question
Do per-cell quantities that match the use case (crack length, false alarms, inactive area) measure method differences more stably than pooled pixel IoU? And how do models do on cells from modules they never saw?

### Why
- Pooled IoU and AP are dominated by a few cells: the top 3 test cells hold 59% of inactive pixels (P6).
- They also depend on the operating point and on saturation (P6, P8).
- The intended use (WattCycle: severity and power loss) needs per-cell quantities: crack length and connectivity, inactive area fraction. See `to_human/proposal_reframe_2026-10-11.md` §1.

### Setup (definitions fixed 11 Oct 12:59 IST, commit `21b5a8f`, before any E1 number; the README header says ~14:00; `results/e1/README.md`)

**Evaluation cells**
- **test:** the 50 BenchmarkEL test cells, against the E-SCDD revised masks.
- **ext:** 106 cells of BenchmarkEL release `20221008`.
  - Not among our 582 cells, and not in the external unlabelled pool (11 of 117 extra cells were in the pool and were dropped).
  - 101 CSIR, 5 BMRK; 32 contain crack, 10 contain inactive.
  - From 67 modules, only 1 of which has cells among our 582. So ext measures transfer to unseen modules.
  - Classes 24 to 28 are not in our 24-class taxonomy. 24 (sp mono halfcut) is remapped to sp mono. 25 to 28 (scuff, corrosion cell, brightening, star) are marked ignore after the amendment below.
  - Manifest: `ext117_manifest.csv`. Montage: `ext_montage.png`.
- Val is not used: it informed P6's base choice.

**Per-cell metrics** (prediction = argmax, final weights; teacher for MT runs)

| Metric | Definition | Over which cells |
|---|---|---|
| crack tolF1@2 | 2PR/(P+R): P = share of predicted crack px within 2 px of GT crack; R = share of GT crack px within 2 px of predicted crack; 0 if nothing predicted | cells with GT crack ≥ 20 px; mean |
| crack length error | \|L_pred − L_gt\| / L_gt, with L the skeleton pixel count (skimage `skeletonize`) | same cells; median |
| crack false alarm | share of cells with predicted crack ≥ 50 px | cells with GT crack < 20 px |
| inactive area error | \|a_pred − a_gt\| in percentage points; a = inactive px / non-padding px | all cells; mean |
| inactive detection F1 | a cell is positive if a ≥ 0.5% (GT and prediction separately) | all cells |
| inactive cell IoU | per-cell IoU | cells with GT inactive ≥ 0.5%; mean |

**Reporting**
- Arms are averaged over seeds; paired image bootstrap (2,000) and leave-top-3-out.
- The 95% CI half-width of each per-cell metric is compared with the pooled IoU's on the same cells.
- E1 is descriptive and enters P13 to P15 only as labelled secondary metrics.

**Code**
- `/tmp/noob_el/diag/e1_task_metrics_v2.py` on cv02 (local copy `scripts_cv02/e1_task_metrics.py`); output `results/e1/raw_v2/<run>.json`.
- `scripts_cv02/e1_aggregate.py`: `--merge NEW=ARM1+ARM2` pools seed sets; it also prints the leave-top-3-out table.

**Amendment, 13:16 IST (commit `f9ea897`, with the first pass; the v2 rescoring is commit `c3d9b01`, 14:03 IST; the README header says ~14:15), after first-pass ext numbers were seen**
- Release `20221008` labels four defect types our taxonomy lacks (25 to 28), in 95 of the 117 cells.
- The first pass mapped them to background, so a crack prediction on a "star" defect counted as a false alarm.
- The fix marks those pixels ignore, excludes them from the cell area, and records predictions on them separately.
- Disclosed because the first-pass numbers prompted it. The first pass is kept in `raw/`; test numbers are identical.

### Results (P6 to P12 checkpoints, 73 + 33 runs; `results/e1/README.md`)
Does a per-cell metric measure more stably? This counts the paired contrasts (23 picked for the protocols, so descriptive) whose 95% CI excludes 0, and gives the median |Δ| / CI half-width:

| Metric | test: CI excl. 0 | test: median \|Δ\|/hw | ext: CI excl. 0 | ext: median \|Δ\|/hw |
|---|---|---|---|---|
| crack IoU (pooled) | 13 | 0.93 | 4 | 0.57 |
| crack relF1@2 (pooled) | 11 | 0.86 | 6 | 0.62 |
| crack tolF1@2 (per cell) | 8 | 0.83 | 6 | 0.59 |
| crack length error | 6 | 0.63 | 8 | 0.67 |
| crack false alarm | 0 | – | 16 | 1.43 |
| inactive IoU (pooled) | 7 | 0.85 | 10 | 0.68 |
| inactive cell IoU | 9 | 0.80 | 17 | 1.45 |
| inactive area error | 1 | 0.41 | 11 | 0.86 |
| inactive detection F1 | 0 | 0.40 | 7 | 0.86 |

**The unseen-module drop** (`results/e1/README.md`, `results/e1/e1_ext_v2.md`):

| Model | crack IoU, test | crack IoU, ext | crack tolF1, test | crack tolF1, ext |
|---|---|---|---|---|
| L3 100% | 0.471 | 0.152 | 0.80 | 0.41 |
| L3 10% | 0.396 | 0.080 | 0.70 (`e1_tables_p6_p10.md`, 0.697) | 0.273 |

### Verdicts (against the criterion in `to_human/proposal_reframe_2026-10-11.md` E1: "adopt as primary if the per-cell CI is narrower")
- **Crack:** not met. Per-cell crack metrics are not more sensitive than pooled IoU or relF1@2 on test. Pooled IoU and relF1@2 stay primary.
- **Inactive:** per-cell IoU separates more contrasts than pooled IoU (test 9 vs 7; ext 17 vs 10). It is less dominated by a few large cells.
- **Crack false alarm:** uninformative on test (almost no arm fires on a crack-free test cell), but the most sensitive crack metric on ext.

### Reading
- **The extension is a different regime.** Every model loses most crack performance on unseen modules. This is a measured limit on transfer, not a method result.
- **A pattern across P11 and P12 (descriptive):** joint-BN tolerant PL raises crack false alarms on unseen modules by about 0.10 of crack-free cells, and improves inactive there.
  - P11: Cm − Dm false alarm +0.122 [+0.063, +0.191]; Cm − A +0.113 [+0.049, +0.186] (`results/p11/README.md`).
- **P13 (separate BN)** removes most of that false-alarm rise: Cs5 − Cm5 −0.095 [−0.141, −0.050].
- **On unseen modules, separate-BN SSL lifts inactive a lot:** CsM5 − A5c inactive cell IoU +0.467 (`results/e1/e1_p13.md`).

### Next
E1 scoring is built into `scripts/post_p15.sh` and `scripts/post_p16.sh`. The proposal's broader O1 measurement items (isolation, Köntges grade agreement, minimum detectable effect) are not done; see `15_status_remaining_work.md`.

---

## Related docs
- `00_START_HERE.md`: reading order and how to use the handbook.
- `04_glossary_and_naming.md`: every term and arm name.
- `07_methodology_rules_and_statistics.md`: rule 1, the standing rules, bootstrap, why the rules are lenient.
- `09_experiments_P8_P12_ssl_series.md`: P8 to P12, which P13 builds on.
- `11_results_synthesis_and_claims.md`: what P13 to P17 and E1 mean together.
- `13_problems_pitfalls_open_issues.md`: val/test disagreement, machine disagreement, inactive concentration.
- `14_code_and_infrastructure.md`: worktrees, commits, scripts, server paths.
- `15_status_remaining_work.md`: server state at session close and what is left.
