# 09. Experiments P8 to P12: the SSL series on the L3 base

## What this covers
This file covers the five semi-supervised (SSL) experiments run on 10 and 11 Oct 2026 on the corrected supervised recipe L3 (from P6). For each experiment:
- question;
- why it was run;
- setup;
- locked rules and the verdicts they gave;
- robustness checks;
- reading (interpretation, labelled);
- what it led to.

The series moves through four questions:
1. Does the tolerant pseudo-label loss help on a base that has label headroom (P8)?
2. Does a much larger unlabelled pool help (P9)?
3. Does SSL help more with fewer labels (P10)?
4. Is the Mean Teacher pipeline itself handicapping the student, and what remains once that is fixed (P11, P12)?

The main discovery of the series is the "pipeline handicap". With the unlabelled loss switched off, the Mean Teacher student was worse than plain supervised training. P11 traced most of it to the labelled view; P12 left a residual crack handicap consistent with BatchNorm mixing, which P13 then removed.

All numbers here are P-series (revised E-SCDD labels, L3 base). No old-era numbers appear.

## Sources
- Protocols: `protocols/P8_tolerant_pl_on_l3.md`, `P9_external_pool.md`, `P10_ssl_5pct.md` (with its B5 amendment), `P11_matched_pipeline.md`, `P12_matched_5pct.md`.
- Results: `results/p8/README.md`, `results/p9/README.md`, `results/p10/README.md` (and `labelled_set_counts.txt`), `results/p11/README.md`, `results/p12/README.md`, and the `*_rules.txt` and `per_image_test.txt` files next to them.
- Per-cell (E1) tables: `results/e1/e1_tables_p6_p10.md`, `results/e1/e1_p11.md`, `results/e1/e1_p12.md`; definitions in `results/e1/README.md`.
- Context: the conversation scratchpad (`docsrc/session_summaries.md`, `docsrc/user_messages.md`); byte-identical stable copies in `sources/chat/claude_session_summaries_2026-10-07_to_11.md` and `sources/chat/user_messages_2026-10-07_to_11.md`.
- Times: protocol texts sometimes state lock times that disagree with git. This file gives the git commit time (IST) and notes the protocol text where they differ.
- E1 extension numbers: `e1_tables_p6_p10.md` holds the **first-pass** extension scoring (before the amendment that ignores release classes 25 to 28). Where `e1_ext_v2.md` has the same contrast, the v2 value is given; otherwise the first-pass value is marked as such.
- Protocol lock commits (research repo, `git log`):

  | Protocol | Lock commit | Note |
  |---|---|---|
  | P8 | `da3d941` | |
  | P9 | `be69ace` | |
  | P10 | `9a85958` | B5 amendment `bf745e0` |
  | P11 | `38de062` | |
  | P12 | `7320bd4` | |

---

## 0. How P8 to P12 connect

### Reading guide: arm names in this series
(Full key in `04_glossary_and_naming.md`.)

| Letter | Meaning |
|---|---|
| A | supervised reference: P6's L3 recipe, no unlabelled data |
| D | loss-off control: the full Mean Teacher pipeline with the tolerant loss at λ_final = 0, so everything is identical to C except that the unlabelled loss never acts |
| B | hard pseudo-labels: `confidence_ce`, teacher confidence ≥ 0.95 |
| C | tolerant pseudo-labels: `tolerant_pl`, R = 2 px; the proposed loss |
| x suffix | external unlabelled pool (11,938 cells) instead of the in-domain pool (the rest of the training cells with labels hidden) |
| m | matched labelled view: labelled images go through exactly the supervised arm's augmentation (`ssl.labeled_aug=supervised`, P11 on) |
| 5 | 5% labels (23 cells); no suffix means 10% (47 cells) |
| g prefix | the run is on gaint (RTX PRO 4500), not cv02 (RTX A6000) |
| A5c | supervised 5% on cv02 (the "c" separates it from P10's gaint A5) |

### The rule used in every contrast
"Rule 1" (from P6 and P8; details in `07_methodology_rules_and_statistics.md`):
- an arm "helps" if its mean minus the other arm's mean, on any primary metric, is > 0.01 **and** > 2·√((sd_A² + sd_B²)/3), over 3 seeds each;
- **and** no primary metric is worse by the same rule.

From P8 on, the primary metrics are test crack IoU, test inactive IoU and test crack relaxed F1@2, all at argmax with revised labels. AP became secondary because P6 showed that many true defect pixels sit at score < 0.001, where AP cannot rank them.

### The storyline

| Exp | Labels | Question | Locked answer | What it revealed |
|---|---|---|---|---|
| P8 | 10% | Do P7's arms help on L3, the base with headroom? | No loss passes (C − D n.d.) | **D < A**: the Mean Teacher pipeline with the loss off is worse than supervised (crack −0.013, inactive −0.101) |
| P9 | 10% | Does a 28× larger external pool help? | Cx − Dx passes on inactive (+0.056), not robust over cells; Cx does not beat Bx | Pool size does not amplify the loss effect. Swapping the pool moves the loss-off control |
| P10 | 5% | Does SSL help more with fewer labels? | No loss passes | In-domain seed 2 collapses under both pseudo-label losses. The external pool hurts crack on its own sources. D5 is far below supervised |
| P11 | 10% | With the labelled view matched to supervised, does the loss help, and does SSL beat supervised? | **Cm − Dm passes (robust). Cm − A passes the seed rule** | The matched view removes most of P8's handicap. A small crack handicap remains (Dm − A −0.007) |
| P12 | 5% | Same at 5%, with a cv02 supervised 5% reference and a gaint replication | Cm5 − Dm5 passes and replicates on gaint; **Cm5 − A5c fails** | The residual crack handicap is larger at 5% (Dm5 − A5c −0.017, robust), consistent with BatchNorm mixing. That led to P13 |

### Two cross-cutting lessons
1. **Always compare against both the loss-off control and plain supervised training.** P8 to P10 showed that a loss can "help" against a handicapped control without beating supervised training. From P11 on, "SSL beats supervised" is a separate rule, credited only if the loss also helps against its own control.
2. **Inactive is close to unmeasurable at 5 to 10% labels.**
   - Inactive appears in only 2 of 23 (5%) or 4 of 47 (10%) labelled cells (`results/p10/labelled_set_counts.txt`).
   - 3 test cells hold 59% of its test pixels (P6).
   - So most inactive results here are seed-noise or 3-cell effects. Every inactive claim must be read with the image bootstrap and leave-top-3-out.

---

## P8. P7's arms on the L3 base (mid-term "Experiment 2")

**Question.** Does the tolerant pseudo-label loss (C) help against its loss-off control (D), and does it beat hard pseudo-labels (B), on the base recipe that has label headroom (L3) at 10% labels? (`protocols/P8_tolerant_pl_on_l3.md`)

**Why it was run (a disclosed post-hoc choice).**
- P6 rule 2 had selected L0 as P7's base. P6 rule 3 then found that L0 has no headroom (pooled AP −0.001), so P7 could only be a pilot.
- L3 has a large gap from 10% to 100% labels: pooled AP +0.159, crack IoU +0.075, inactive IoU +0.135.
- The base was chosen after seeing P6's val and test results. The choice applies equally to every P8 arm, so it does not favour one arm.
- Launched on the user's "if the resources are free, we can fasten up" (10 Oct), co-located with P7.

**Setup.** P7's protocol verbatim except for the base.
- **Base:** `model.name=smp_unetpp loss.supervised=ce_dice` (P6 L3).
- **Data:** revised masks; seed-0 split; 10% labels (47 images); unlabelled = 431 train images with labels hidden; batch 8 + 8.
- **Mean Teacher:**
  - EMA 0.999;
  - weak teacher view;
  - label-safe strong student view, which the **labelled** images also receive (±0.25 jitter at p 0.8, plus noise at p 0.3).
- **λ schedule:** 0 for 2,000 steps, ramp over 2,000 steps to 1.0.
- **Training:** 20,000 steps; seeds 0 to 2; EMA teacher evaluated.
- **Hardware:** cv02 RTX A6000, at most 3 runs per GPU.
- **Code:** commit `0367079` (same as P7).
- **Runs:** 9 runs, 10 Oct 17:15 to 23:53 IST, all rc = 0.

| Arm | Unlabelled loss |
|---|---|
| A (reference, no new runs) | P6 L3 10%: pure supervised pipeline |
| B | `confidence_ce`, t_pos 0.95 |
| C (proposed) | `tolerant_pl`, t_pos 0.95, rare = {crack, inactive}, R = 2 px |
| D (loss-off control) | arm C with λ_final = 0 |

**Metrics, fixed before any run.**
- **Primary:** test crack IoU, inactive IoU, crack relF1@2 (argmax, revised labels).
- **Secondary:** AP with bin-0 share; val; old labels; relP@2.

**Locked rules:**
1. C helps if C − D passes rule 1 on any primary, no primary worse. B vs D the same.
2. C beats B under the same rule. If C helps but does not beat B, the claim is "a correct pseudo-label loss helps", not "tolerance helps".
3. Width check: crack relP@2 falling by > 0.05 against D is flagged.
4. Headroom: report the share of the gap closed, (C − D) / (L3@100% − D).

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p8/README.md`):

| Arm | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D: Mean Teacher, loss off | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| B: hard PL (conf ≥ 0.95) | 0.389±0.007 | 0.219±0.081 | 0.806±0.015 | 0.934±0.011 | 0.430±0.011 | 0.297±0.050 |
| C: tolerant PL (proposed) | 0.392±0.006 | 0.253±0.109 | 0.811±0.012 | 0.919±0.014 | 0.421±0.011 | 0.317±0.105 |
| L3 100% (P6) | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

**Verdict per rule** (difference, then the threshold in brackets):

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| C − D | +0.009 (0.010) | +0.059 (0.132) | +0.015 (0.017) | C does not help (no primary passes) |
| B − D | +0.007 (0.010) | +0.026 (0.102) | +0.010 (0.020) | B does not help |
| C − B | +0.003 (0.010) | +0.033 (0.157) | +0.005 (0.023) | C does not beat B |

- Width check: crack relP@2 C − D = +0.017, OK.
- Gap closed by C (descriptive only, since nothing passed): crack IoU 10%, inactive IoU 25%, relF1@2 18%. For B: 8% / 11% / 13%.

**Robustness** (image bootstrap, cells resampled, averaged over seeds):

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C − D, crack | +0.009 | +0.009 | [+0.002, +0.015] | 0.99 |
| C − D, inactive | +0.059 | +0.052 | [+0.020, +0.109] | 1.00 |
| B − D, crack | +0.007 | +0.006 | [−0.001, +0.013] | 0.96 |
| C − B, inactive | +0.033 | +0.032 | [−0.005, +0.095] | 0.93 |
| D − A, crack | −0.013 | −0.021 | [−0.028, −0.001] | 0.01 |
| D − A, inactive | −0.101 | −0.077 | [−0.171, −0.031] | 0.00 |

- Across test cells, C − D is small but consistent. Across seeds it is not separable.
- The inactive seed spread is large. C seed 0 and D seed 0 both collapse on inactive (IoU 0.13 and 0.15), with or without the loss. So that variance is training noise on a few inactive cells, not an effect of the loss.

**The key discovery: the pipeline handicap.**
- D − A is robustly negative: crack −0.013, inactive −0.101 (CIs exclude 0). The SSL pipeline with the loss switched off is worse than plain supervised L3.
- C recovers part of this but ends where A is: C − A = −0.004 crack IoU, −0.041 inactive IoU, −0.003 relF1@2.
- On L0 (P7) the same D was not worse than A (crack IoU +0.036).

**It is not the EMA teacher.** Student weights scored the same way (`per_image_student.json`, test IoU):

| Run set | Weights | crack IoU | inactive IoU |
|---|---|---|---|
| P8 D | student | 0.383 | 0.189 |
| P8 D | teacher | 0.383 | 0.194 |
| P8 C | student | 0.391 | 0.249 |
| P8 C | teacher | 0.392 | 0.253 |

Three things still differ between D and A in the training path:
1. **Labelled view.** Mean Teacher's label-safe "strong" view uses brightness/contrast ±0.25 at p = 0.8 plus noise at p = 0.3. The supervised label-safe pipeline uses ±0.2 at p = 0.4 and no noise.
2. **BatchNorm.** Statistics are computed over 8 labelled + 8 unlabelled images in one student forward pass.
3. **Data streams.** The random streams differ.

P8 cannot separate these. The README proposed a pipeline-matched control as the next step (that became P11).

**Bin-0 share** (test):

| Arm | crack | inactive |
|---|---|---|
| A (P6) | 0.422 | 0.648 |
| D | 0.419 | 0.758 |
| B | 0.397 | 0.632 |
| C | 0.400 | 0.627 |

On L3, pseudo-labels slightly reduce saturation against D, the opposite of L0 (P7).

**E1 per-cell** (descriptive; test rows from `results/e1/e1_tables_p6_p10.md`, ext rows from `results/e1/e1_ext_v2.md`), C − D:

| Set | Metric | Δ | 95% CI |
|---|---|---|---|
| test | crack tolF1 | +0.024 | [+0.000, +0.048] |
| test | inactive cell IoU | +0.069 | [+0.027, +0.119] |
| ext (unseen modules) | inactive cell IoU | +0.141 | [+0.006, +0.272] |
| ext | crack false alarm | +0.041 | [−0.000, +0.082] |

(First-pass ext values were +0.133 [+0.006, +0.261] and +0.045 [+0.000, +0.097].)

**Reading:**
- With 431 in-domain unlabelled cells at 10% labels on L3, no unlabelled loss passes the locked rule against its loss-off control.
- The larger problem: the Mean Teacher pipeline itself costs about −0.013 crack IoU and −0.10 inactive IoU against plain supervised training. The pseudo-label loss only wins that back.
- For the mid-term: no SSL gain on this split, and the obstacle was identified (labelled view and batch mixing, not the EMA teacher).

**Caveats.** One split; 3 seeds; 50 test cells. Inactive is dominated by 3 test cells and by seed collapse. The base was chosen post hoc (disclosed).

**What it led to.** P9 (external pool) and P10 (5% labels) test the other two levers with the same D-type control. P11 tests the matched pipeline.

---

## P9. P8's arms with the 11,938-cell external unlabelled pool

**Question.** Is P8's null caused by the method or by the size of the unlabelled pool? (`protocols/P9_external_pool.md`)

**Why it was run.**
- Interim P7 and P8 runs showed no detectable gain with the 431-cell in-domain pool.
- ALHVR-style methods are normally reported with unlabelled pools 10 to 100× larger.
- The external pool (11,938 CSIR/ARTS cells) had been prepared on 6 Oct (commits `0136855`, `46dfe92`). It was filtered against labelled cells, and its stems are checked disjoint from train/val/test at startup.
- The question was chosen after seeing interim P7/P8 numbers (disclosed). Drafted 10 Oct 22:31 IST (commit `be69ace`; the protocol text says 22:35), launched on the user's "go for p9 THEN, WE NEED TO FOCUS ON THE ssl AS WELL, NIGHT LONG WORKS FOR IT, USE ALL RESOURCES".

**Setup.** P8's protocol verbatim, except:
- `data.unlabeled_pool=external` (reads `data/splits/external_unlabeled.txt`);
- at most 2 runs per GPU.

Code commit `0367079`. 9 runs on cv02, 10 Oct 22:56 IST to 11 Oct 06:26 IST, all rc = 0.

| Arm | Unlabelled loss | Pool |
|---|---|---|
| A (reference) | none (P6 L3 10%) | – |
| Bx | `confidence_ce`, t_pos 0.95 | external |
| Cx (proposed) | `tolerant_pl`, R = 2 px | external |
| Dx (loss-off control) | Cx with λ_final = 0 | external |

Dx differs from P8's D only in what the unlabelled loader reads. It is run so that Cx − Dx is a clean paired contrast.

**Locked rules:**
1. Cx helps (Cx − Dx, rule 1); Bx vs Dx the same.
2. Cx beats Bx.
3. Width check.
4. Gap closed: (Cx − Dx) / (L3@100% − Dx).
5. Pool-size effect (secondary): (Cx − Dx) − (C − D) against P8.

Required reporting:
- the image bootstrap and leave-top-3-out on every rule-1 contrast;
- a source split. The pool is 77% CSIR and 23% ARTS, with no CFVS, BMRK or SDLE. Test has 21 CSIR+ARTS cells and 29 from other sources.

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p9/README.md`):

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D (P8), loss off | 431 | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| C (P8), tolerant PL | 431 | 0.392±0.006 | 0.253±0.109 | 0.811±0.012 | 0.919±0.014 | 0.421±0.011 | 0.317±0.105 |
| Dx, loss off | 11,938 | 0.380±0.003 | 0.287±0.032 | 0.792±0.008 | 0.895±0.024 | 0.399±0.003 | 0.282±0.028 |
| Bx, hard PL | 11,938 | 0.389±0.010 | 0.347±0.054 | 0.801±0.013 | 0.914±0.015 | 0.423±0.009 | 0.363±0.064 |
| Cx, tolerant PL | 11,938 | 0.384±0.007 | 0.344±0.023 | 0.799±0.009 | 0.893±0.017 | 0.419±0.004 | 0.364±0.019 |
| L3 100% (P6) | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

**Verdict per rule:**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Cx − Dx (rule 1) | +0.004 (0.010) | +0.056 (0.046) | +0.007 (0.014) | Cx helps (inactive passes; nothing worse) |
| Bx − Dx (rule 1) | +0.009 (0.012) | +0.060 (0.073) | +0.010 (0.017) | Bx does not help |
| Cx − Bx (rule 2) | −0.004 (0.014) | −0.004 (0.068) | −0.002 (0.018) | Cx does not beat Bx |

- **Rule 3 (width):** Cx − Dx relP@2 −0.003, OK.
- **Rule 4 (gap closed by Cx):** crack IoU 5%, inactive IoU 40%, relF1@2 9%.
- **Rule 5 (pool-size effect, (Cx − Dx) − (C − D)):** crack IoU −0.005, inactive −0.003, relF1@2 −0.007. The loss effect is the same with 431 or 11,938 cells.

**How to read the one pass.** Cx − Dx inactive (+0.056) is the same size as P8's C − D (+0.059). It passes here only because the seed spread is smaller (Cx sd 0.023 against C's 0.109); P8's seed-0 collapse does not recur. So the pass reflects lower variance, not a larger effect.

**Robustness:**

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| Cx − Dx, crack | +0.004 | +0.008 | [−0.003, +0.014] | 0.88 |
| Cx − Dx, inactive | +0.056 | +0.026 | [−0.013, +0.117] | 0.95 |
| Bx − Dx, crack | +0.009 | +0.009 | [+0.002, +0.016] | 1.00 |
| Bx − Dx, inactive | +0.060 | +0.010 | [−0.017, +0.119] | 0.95 |
| Cx − Bx, crack | −0.004 | −0.001 | [−0.009, +0.001] | 0.06 |
| Cx − Bx, inactive | −0.004 | +0.017 | [−0.028, +0.032] | 0.39 |

- The rule-1 pass is **not robust to the choice of test cells**: the CI covers 0, and without the 3 largest inactive cells the gain halves to +0.026.
- Source split, Cx − Dx crack IoU:
  - CSIR+ARTS: −0.003 [−0.019, +0.023];
  - other sources: +0.006 [−0.002, +0.016].
  So there is no in-source benefit on crack. The CSIR+ARTS test cells have almost no inactive pixels (top 3 cells hold 100%), so the inactive split is uninformative.

**Exploratory findings:**
1. **Swapping the pool changes the loss-off control.** With λ = 0, the pool acts only through BatchNorm statistics and data streams. Yet Dx − D (P8):
   - inactive IoU +0.094 [+0.003, +0.179], +0.024 without the top 3;
   - crack −0.003 [−0.010, +0.003].

   Dx's inactive (0.287) is back at supervised A's (0.294). So P8's inactive handicap depends on what shares the BatchNorm batch, not only on the labelled view.
2. **The external pool slightly hurts crack on its own sources.**
   - Cx − C (P8): crack IoU −0.007 [−0.015, −0.000] overall, and −0.019 [−0.041, −0.003] on CSIR+ARTS test cells.
   - Dx − D on CSIR+ARTS: −0.012 [−0.032, −0.001].
   - Plausible but untested: the external CSIR/ARTS cells differ in capture or preprocessing from the benchmark's own cells of those sources.
3. **Bin-0 share** (test):

   | Arm | crack | inactive |
   |---|---|---|
   | D (P8) | 0.419 | 0.758 |
   | C (P8) | 0.400 | 0.627 |
   | Dx | 0.418 | 0.648 |
   | Bx | 0.394 | 0.512 |
   | Cx | 0.392 | 0.517 |
4. **Rare-class pseudo-label share (`rare_frac`, from training logs).** In Cx it rises from about 0.001 at step 3,000 to 0.006 to 0.014 at step 20,000. In P8's C it stays flat at about 0.003. The external pool gives the teacher many more confident defect pixels.

**E1 per-cell** (descriptive, `results/e1/e1_tables_p6_p10.md`):

| Contrast | Set | Metric | Δ | 95% CI |
|---|---|---|---|---|
| Cx − Dx | test | inactive cell IoU | +0.096 | [+0.024, +0.186] |
| Cx − A | test | crack IoU | −0.011 | [−0.025, −0.001] |
| Cx − A | test | crack relF1@2 | −0.015 | [−0.033, −0.003] |
| Cx − Dx | ext (first pass) | inactive cell IoU | +0.307 | [+0.167, +0.414] |
| Cx − Dx | ext (first pass) | crack false alarm | +0.059 | [+0.000, +0.117] |

The two ext rows are first-pass values; `e1_ext_v2.md` has no Cx − Dx contrast. Its arm means point the same way (inactive cell IoU Cx 0.403 vs Dx 0.074; false alarm 0.176 vs 0.113).

**Reading:**
- **Locked result:** with the external pool at 10% labels on L3, tolerant pseudo-labels pass against their loss-off control on inactive IoU (+0.056). Crack shows no difference.
- **Three qualifications:**
  - the effect size is the same as P8, with less seed noise;
  - it is not robust over test cells (3 cells drive it);
  - tolerance does not beat hard pseudo-labels here (Cx − Bx ≈ 0). P7's tolerant-over-hard advantage on L0 does not carry over to L3 with this pool.
- A larger pool does not amplify the loss effect.
- Against plain supervised training (exploratory, not a P9 rule), Cx − A is crack IoU −0.011, inactive +0.049, relF1@2 −0.015. SSL had not beaten supervised L3 at 10% on crack.

**Caveats.** One split; 3 seeds; 50 test cells. Inactive is in only 4 of the 47 labelled cells. The P8 arms ran in a different launch batch; co-location affects speed only, because training is deterministic.

**What it led to.** P10 (fewer labels) and P11 (fix the pipeline).

---

## P10. SSL at 5% labels, in-domain and external pools

**Question.** Semi-supervised gains usually grow as labels shrink. At 5% labels (23 cells), does the unlabelled loss help against its loss-off control, with either pool? (`protocols/P10_ssl_5pct.md`)

**Why it was run.**
- At 10% labels, interim P8 showed no gain. Halving the labels to the committed `seed0/labeled_5pct.txt` should enlarge the label gap.
- Crossed with the two pools: in-domain (455 hidden-label training cells) and external (11,938).
- Locked 10 Oct 22:56 IST (commit `9a85958`), before any P10 run; the first run started 22:57 IST. The protocol text says ~23:05, which is later than the first run, so the git time is the one to use. The question was chosen after seeing interim P7/P8 numbers (disclosed). The user had approved overnight SSL on all resources.

**Setup.** P8's protocol verbatim except `data.labeled_fraction=0.05`:
- code `0367079`;
- L3 base; label-safe views; revised masks; seed-0 split; batch 8 + 8;
- λ ramp as P8; 20,000 steps; seeds 0 to 2; EMA teacher evaluated.

Runs:
- 15 SSL runs on cv02, 10 Oct 22:57 IST to 11 Oct 07:34 IST.
- 6 supervised references on gaint (RTX PRO 4500), 10 Oct 22:58 IST to 11 Oct 03:57 IST: A5 ×3 and A50 ×3.
- All rc = 0.

| Arm | Unlabelled loss | Pool | Hardware |
|---|---|---|---|
| A5 (reference only) | none: P6 L3 options at 5% | – | gaint, so not used in any rule |
| D5 | `tolerant_pl`, λ_final = 0 | in-domain (455) | cv02 |
| C5 | `tolerant_pl`, R = 2 px | in-domain (455) | cv02 |
| Dx5 | `tolerant_pl`, λ_final = 0 | external (11,938) | cv02 |
| Cx5 | `tolerant_pl`, R = 2 px | external (11,938) | cv02 |
| B5 (amendment) | `confidence_ce`, t_pos 0.95 | in-domain (455) | cv02 |

**Amendment** (10 Oct 23:04 IST, commit `bf745e0`; protocol text ~23:10; before any B5 run, the first of which started 23:11 IST; no P10 results seen):
- B5 was added to fill the third slot on GPUs 0 to 2.
- Rule: C5 beats B5 is tested with rule 1 on C5 − B5.

**Locked rules:**
1. C5 helps (C5 − D5); Cx5 helps (Cx5 − Dx5); both by rule 1.
2. Width check against the matching D arm.
3. Gap closed against P6's L3@100%.
4. Label-budget interaction (secondary): (C5 − D5) against P8's (C − D), and (Cx5 − Dx5) against P9's (Cx − Dx).

Required reporting: bootstrap and leave-top-3-out; P9 source split; how many of the 23 labelled cells contain inactive.

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p10/README.md`):

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A5: supervised (gaint, reference only) | – | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 | 0.282±0.003 | 0.270±0.050 |
| D5, loss off | 455 | 0.243±0.005 | 0.243±0.006 | 0.629±0.014 | 0.855±0.030 | 0.232±0.009 | 0.251±0.008 |
| B5, hard PL | 455 | 0.247±0.104 | 0.238±0.204 | 0.618±0.177 | 0.898±0.019 | 0.284±0.098 | 0.272±0.221 |
| C5, tolerant PL | 455 | 0.246±0.090 | 0.250±0.194 | 0.630±0.162 | 0.887±0.011 | 0.262±0.085 | 0.307±0.155 |
| Dx5, loss off | 11,938 | 0.275±0.005 | 0.198±0.021 | 0.683±0.005 | 0.848±0.001 | 0.266±0.003 | 0.197±0.017 |
| Cx5, tolerant PL | 11,938 | 0.263±0.012 | 0.288±0.017 | 0.656±0.020 | 0.783±0.054 | 0.264±0.016 | 0.310±0.039 |

Supervised label curve (descriptive; 5% and 50% on gaint, the rest on cv02):

| Labels | crack IoU | inactive IoU |
|---|---|---|
| 5% | 0.298 | 0.277 |
| 10% | 0.396 | 0.294 |
| 20% | 0.398 | 0.347 |
| 50% | 0.437 | 0.427 |
| 100% | 0.471 | 0.429 |

**Verdict per rule:**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| C5 − D5 (rule 1) | +0.003 (0.104) | +0.007 (0.224) | +0.001 (0.188) | C5 does not help |
| Cx5 − Dx5 (rule 1) | −0.012 (0.014) | +0.090 (0.031) | −0.027 (0.024), worse | Cx5 does not help (a primary is worse) |
| B5 − D5 (amendment) | +0.005 (0.120) | −0.005 (0.236) | −0.011 (0.205) | B5 does not help |
| C5 − B5 (amendment) | −0.002 (0.159) | +0.012 (0.325) | +0.012 (0.277) | C5 does not beat B5 |

- **Rule 2 (width):** Cx5 − Dx5 crack relP@2 −0.065, flagged as possible fattening.
- **Rule 3 (gap closed):** C5 1% / 4% / 0%; Cx5 −6% / 39% / −14%.
- **Rule 4 (effect at 5% minus effect at 10%):**
  - (C5 − D5) − (C − D): crack −0.006, inactive −0.052, relF1@2 −0.014;
  - (Cx5 − Dx5) − (Cx − Dx): −0.016 / +0.034 / −0.035.
  The loss effect did not grow when labels were halved.
- **Required count:** inactive is in 2 of the 23 labelled cells (20,517 px); crack in 9 of 23 (`labelled_set_counts.txt`).

**Robustness:**

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| C5 − D5, crack | +0.003 | +0.003 | [−0.012, +0.016] | 0.66 |
| C5 − D5, inactive | +0.007 | +0.036 | [−0.048, +0.086] | 0.61 |
| C5 − B5, inactive | +0.012 | +0.037 | [−0.033, +0.071] | 0.63 |
| Cx5 − Dx5, crack | −0.012 | −0.017 | [−0.026, −0.001] | 0.01 |
| Cx5 − Dx5, inactive | +0.090 | +0.003 | [−0.019, +0.157] | 0.95 |

- With the external pool, tolerant PL is robustly worse on crack and predicts fatter cracks (relP@2 0.85 → 0.78; seed 2 reaches 0.73). Its inactive gain disappears without the top-3 cells.
- **Source split, Cx5 − Dx5 crack IoU:**
  - CSIR+ARTS (21 cells): −0.065 [−0.092, −0.026];
  - others (29 cells): −0.001 [−0.010, +0.007].
  The crack loss sits on the pool's own sources, as P9 showed at 10%.
- In-domain C5 − D5 shows no source pattern.

**Exploratory finding 1: seed collapse.** Per seed, test IoU (crack / inactive):

| Seed | D5 | B5 | C5 | Cx5 |
|---|---|---|---|---|
| 0 | 0.238 / 0.238 | 0.302 / 0.369 | 0.294 / 0.358 | 0.253 / 0.303 |
| 1 | 0.247 / 0.241 | 0.313 / 0.341 | 0.302 / 0.366 | 0.275 / 0.270 |
| 2 | 0.244 / 0.249 | 0.128 / 0.003 | 0.142 / 0.027 | 0.261 / 0.292 |

- Seed 2 collapses under both hard and tolerant pseudo-labels, but not under the same seed's loss-off control or with the external pool. That points to that seed's in-domain data stream and early teacher.
- In C5 seed 2, `rare_frac` stays at 0.001 to 0.002 from step 4,000, against 0.007 to 0.009 in seeds 0 and 1. The teacher stops predicting defects and the student is trained toward "all background". This is confirmation-bias collapse, visible during training without labels. B5 does not log this quantity.
- At 10% (P8) the same aggregate signal did not separate C's inactive-only collapse in seed 0; a per-class version would be needed.
- **Healthy seeds only (0 and 1; post hoc, not a rule):** B5 and C5 average about crack 0.30 and inactive 0.36, which is about +0.06 crack and +0.12 inactive over D5. That is level with supervised A5 on crack (0.298) and above it on inactive (0.277; gaint).

**Exploratory finding 2: the P8-style pipeline is far below supervised at 5%.**
- D5 − A5: crack IoU −0.055, relF1@2 −0.079 (cross-hardware, descriptive). At 10% it was −0.013 (P8).
- Swapping the pool again moves the loss-off control: Dx5 − D5 = crack +0.032, inactive −0.045.

**Bin-0 share** (test):

| Arm | crack | inactive |
|---|---|---|
| D5 | 0.636 | 0.699 |
| B5 | 0.572 | 0.629 |
| C5 | 0.597 | 0.608 |
| Dx5 | 0.576 | 0.746 |
| Cx5 | 0.555 | 0.504 |

**E1 per-cell** (descriptive, `results/e1/e1_tables_p6_p10.md`):

| Contrast | Set | Metric | Δ | 95% CI |
|---|---|---|---|---|
| Cx5 − Dx5 | test | inactive cell IoU | +0.124 | [+0.065, +0.179] |
| C5 − D5 | ext (v2) | crack relF1@2 | +0.023 | [+0.003, +0.042] |
| C5 − D5 | ext (v2) | inactive cell IoU | +0.287 | [+0.106, +0.495] |
| Cx5 − Dx5 | ext (first pass) | crack false alarm | +0.126 | [+0.027, +0.221] |
| Cx5 − Dx5 | ext (first pass) | inactive area error | +0.667 pp | [+0.396, +0.986] (over-prediction) |

The C5 − D5 ext rows are from `e1_ext_v2.md` (first pass: +0.019 and +0.265). `e1_ext_v2.md` has no Cx5 − Dx5 contrast; its arm means point the same way (false alarm Cx5 0.351 vs Dx5 0.185; inactive area error 0.864 vs 0.171 pp).

**Reading:**
- **Locked result:** at 5% labels on the P8-style pipeline, no unlabelled loss passes against its loss-off control.
- In-domain, both pseudo-label arms are dominated by a same-seed collapse (sd about 0.1).
- External pool: tolerant PL gains inactive but loses crack, robustly, with wider crack predictions. The loss is concentrated on test cells from the pool's own sources (−0.065). The external pool is not a safe source of crack pseudo-labels.
- Not confirmed: "SSL helps more as labels shrink".
- Carried forward:
  - when pseudo-labelling does not collapse, it lifts the handicapped control to about supervised level on crack;
  - the pipeline itself (D5 vs A5) is the larger problem at 5%;
  - collapse is a concrete, detectable failure mode, a candidate target for a rare-class-aware method (pseudo-label quotas or thresholds).

**Caveats.** One split; 3 seeds. Inactive has 2 labelled examples at 5%; 3 test cells hold 59% of its test pixels. A5 and A50 ran on different hardware, so they are reference only. The healthy-seed reading is post hoc.

**What it led to.**
- P12 (the matched pipeline at 5%, with a cv02 A5).
- P16 (later, on the user's question "why we using 5 or 10% for ssl?").

---

## P11. Pipeline-matched Mean Teacher at 10% labels

**Question.** With the labelled view made identical to the supervised arm's:
- is the loss-off control still worse than supervised?
- does the unlabelled loss help against its own control?
- and does SSL beat **plain supervised training**?

(`protocols/P11_matched_pipeline.md`)

**Why it was run (post hoc, disclosed).** P8 found D below A (crack −0.013 [−0.028, −0.001]; inactive −0.101 [−0.171, −0.031]), and the EMA teacher was ruled out. Of the three remaining differences (labelled view, BatchNorm mixing, data streams), P11 removes the first.

**Code.** Commit `24590fb` adds the opt-in switch `ssl.labeled_aug=supervised`:
- it feeds labelled images through exactly the supervised arm's `get_labelsafe_augmentation`;
- it leaves the unlabelled two-view pipeline unchanged;
- it has unit tests and a CPU smoke run;
- it equals `0367079` otherwise.

cv02 path: `/tmp/noob_el/el_p11`.

**Setup.** P8's protocol verbatim plus `ssl.labeled_aug=supervised`:
- L3 base; revised masks; seed-0 split; 10% labels (47);
- batch 8 + 8; λ ramp as P8; 20,000 steps; seeds 0 to 2; EMA teacher evaluated;
- cv02 RTX A6000, ≤ 3 runs per GPU, `OMP_NUM_THREADS=4` (speed only).

Locked 11 Oct 00:11 IST (commit `38de062`; protocol text ~00:15). 12 runs, 11 Oct 06:02 to 13:50 IST, all rc = 0.

| Arm | Unlabelled loss | Pool |
|---|---|---|
| A (reference) | P6 L3 10%, supervised | – |
| Dm | `tolerant_pl`, λ_final = 0 | in-domain (431) |
| Cm | `tolerant_pl`, R = 2 px | in-domain (431) |
| Dmx | `tolerant_pl`, λ_final = 0 | external (11,938) |
| Cmx | `tolerant_pl`, R = 2 px | external (11,938) |

**Locked rules:**
1. **Pipeline check (descriptive, not a gate):** Dm − A with the image bootstrap. Dm ≈ A means the labelled view explained P8's D < A; otherwise BatchNorm/batch composition remains a candidate.
2. **Cm helps:** Cm − Dm by rule 1. Cmx helps: Cmx − Dmx.
3. **SSL beats supervised:** Cm − A and Cmx − A by the same rule. This is the claim the thesis needs. **Credited only if rule 2 also holds for that arm.**
4. **Width check:** relP@2 drop > 0.05 against the matching D arm.
5. **Gap closed:** (C − A) / (L3@100% − A).

**Results** (test, revised labels, mean ± sd over seeds 0 to 2; `results/p11/README.md`):

| Arm | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|
| A: L3 10%, supervised (P6) | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| D (P8): loss off, SSL labelled view | 431 | 0.383±0.003 | 0.194±0.034 | 0.796±0.008 | 0.903±0.009 | 0.402±0.008 | 0.201±0.034 |
| Dm: loss off, matched view | 431 | 0.389±0.002 | 0.295±0.023 | 0.809±0.004 | 0.907±0.010 | 0.395±0.002 | 0.300±0.018 |
| Cm: tolerant PL, matched view | 431 | 0.398±0.010 | 0.365±0.055 | 0.827±0.010 | 0.917±0.012 | 0.416±0.012 | 0.401±0.056 |
| Dmx: loss off, matched, external | 11,938 | 0.396±0.005 | 0.300±0.049 | 0.815±0.005 | 0.905±0.013 | 0.401±0.004 | 0.301±0.044 |
| Cmx: tolerant PL, matched, external | 11,938 | 0.398±0.009 | 0.355±0.038 | 0.819±0.010 | 0.910±0.010 | 0.413±0.010 | 0.398±0.035 |
| L3 100% (P6) | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

**Verdict per rule:**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Dm − A (rule 1, pipeline check) | −0.007 (0.010) | +0.000 (0.034) | −0.005 (0.010) | No detectable handicap by the seed rule |
| Cm − Dm (rule 2) | +0.009 (0.012) | +0.071 (0.069) | +0.018 (0.013) | **Cm helps** |
| Cmx − Dmx (rule 2) | +0.002 (0.013) | +0.054 (0.072) | +0.004 (0.013) | Cmx does not help |
| Cm − A (rule 3) | +0.002 (0.012) | +0.071 (0.067) | +0.013 (0.012) | **Cm beats supervised** (credited: rule 2 holds) |
| Cmx − A (rule 3) | +0.003 (0.011) | +0.061 (0.049) | +0.005 (0.012) | Passes the arithmetic, **not credited** (rule 2 fails for Cmx) |

- Width check: relP@2 does not drop in any contrast (+0.000 to +0.010).
- Gap closed by Cm: crack IoU 3%, inactive IoU 53%, relF1@2 21%.

**Robustness** (image bootstrap, paired, test IoU):

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| Dm − A, crack | −0.007 | −0.010 | [−0.016, −0.001] | 0.01 |
| Dm − A, inactive | +0.000 | −0.042 | [−0.092, +0.083] | 0.48 |
| Cm − Dm, crack | +0.009 | +0.014 | [+0.003, +0.016] | 1.00 |
| Cm − Dm, inactive | +0.071 | +0.070 | [+0.020, +0.121] | 1.00 |
| Cmx − Dmx, inactive | +0.054 | +0.014 | [+0.011, +0.074] | 0.99 |
| Cm − A, crack | +0.002 | +0.004 | [−0.004, +0.008] | 0.73 |
| Cm − A, inactive | +0.071 | +0.028 | [−0.009, +0.158] | 0.91 |
| Dm − D (P8), inactive | +0.101 | +0.035 | [+0.014, +0.188] | 1.00 |

- **The loss effect is robust.**
  - Cm − Dm holds over test cells on both classes, and the inactive gain survives leaving out the 3 largest inactive cells (+0.070).
  - It holds in both source groups: crack on CSIR+ARTS +0.022 [+0.015, +0.033]; inactive on CFVS/BMRK/SDLE +0.073 [+0.016, +0.127].
  - This is the first unlabelled-loss effect in P7 to P12 that survives both the seed rule and the cell bootstrap.
- **SSL vs supervised is a seed-level pass only.**
  - Cm − A inactive is not robust over cells (CI covers 0; +0.028 without the top 3).
  - Crack IoU is level.
  - The relF1@2 pass is narrow (+0.013 against 0.012).
- **The matched view removed most of P8's handicap** (Dm − D inactive +0.101).
- **A small crack handicap remains:** Dm − A = −0.007 [−0.016, −0.001], consistent with BatchNorm mixing. About 0.007 of Cm's crack gain over Dm only offsets it.

**Bin-0 share** (test):

| Arm | crack | inactive |
|---|---|---|
| Dm | 0.429 | 0.653 |
| Cm | 0.402 | 0.508 |
| Dmx | 0.419 | 0.639 |
| Cmx | 0.404 | 0.531 |

Dmx ≈ Dm: with the matched view, the external pool no longer moves the loss-off control as it did in P9.

**E1 addendum** (11 Oct, after the locked analysis; descriptive; `results/e1/e1_p11.md`):

| Contrast | Set | crack relF1@2 (pooled) | crack tolF1 (per cell) | crack false alarm | inactive cell IoU |
|---|---|---|---|---|---|
| Cm − Dm | test | +0.018 [+0.010, +0.032] | +0.039 [+0.015, +0.067] | 0 vs 0 | +0.076 [+0.014, +0.172] |
| Cm − A | test | +0.013 [+0.005, +0.024] | +0.036 [+0.014, +0.061] | 0 vs 0 | +0.028 [−0.005, +0.072] |
| Cm − Dm | ext | +0.012 [−0.018, +0.044] | +0.035 [+0.009, +0.063] | +0.122 [+0.063, +0.191] (worse) | +0.020 [−0.068, +0.120] |
| Cm − A | ext | −0.013 [−0.047, +0.021] | +0.012 [−0.017, +0.043] | +0.113 [+0.049, +0.186] (worse) | +0.071 [+0.001, +0.166] |
| Cmx − A | ext | +0.020 [−0.030, +0.065] | +0.021 [−0.013, +0.058] | +0.068 [+0.004, +0.135] (worse) | +0.218 [+0.072, +0.367] |

- The relF1@2 part of rule 3 is robust over test cells (Cm − A CI excludes 0); the inactive part is not.
- On unseen modules, Cm raises crack false alarms: the share of crack-free extension cells with ≥ 50 predicted crack px rises from 0.13 (A) to 0.24 (Cm). No arm has any on the test set.
- Cmx improves inactive on unseen modules (cell IoU +0.22). Only 1 of the 106 extension cells comes from a module with cells in the external pool, so this is not a module leak.

**Reading:**
- At 10% labels, on a pipeline whose labelled view matches supervised training, the tolerant pseudo-label loss helps robustly against its own control. SSL beats supervised by the locked seed rule (inactive IoU, relF1@2).
- Over test cells, only the relF1@2 part of "beats supervised" is robust.
- The remaining small crack handicap points at BatchNorm mixing.

**Caveats.** One split; 3 seeds; 50 test cells. Inactive is in 4 of 47 labelled cells. The P6 reference ran in a different launch batch.

**What it led to.** P12 (the same at 5%) and P13 (separate BatchNorm forward).

---

## P12. Pipeline-matched SSL at 5% labels, a cv02 supervised 5% reference, and a gaint replication

**Question.** At 5% labels, where the label gap is largest:
- does the matched pipeline still carry a handicap?
- does the loss help?
- does SSL beat a supervised 5% reference trained on the same hardware?
- does the key contrast replicate on the other machine?

(`protocols/P12_matched_5pct.md`)

**Why it was run.**
- P10 tested 5% on the handicapped P8-style pipeline. P11 fixed the labelled view at 10%. P12 crosses them.
- P10's A5 ran on gaint, so it could not enter a cv02 rule. P12 adds a cv02 A5 ("A5c").
- gaint was idle after its P10 references (~04:00), so it ran fresh seeds of the key contrast, hardware-matched to gaint's own A5.
- **Seen at locking (11 Oct 01:37 IST, commit `7320bd4`; protocol text ~02:00):** no P9, P10 (cv02) or P11 result; only P10's gaint A5 (crack IoU 0.298±0.005, inactive 0.277±0.055, relF1@2 0.708±0.012). This is disclosed.

**Setup.** SSL arms: P11's protocol verbatim except `data.labeled_fraction=0.05`:
- labelled = `seed0/labeled_5pct.txt` (23 cells); in-domain pool = the other 455 training cells;
- code `24590fb` with `ssl.labeled_aug=supervised`;
- L3 base; revised masks; batch 8 + 8; λ ramp; 20,000 steps; EMA teacher; `OMP_NUM_THREADS=4`.

Supervised runs use P6's L3 options verbatim. The supervised code path is unchanged between `824fab0` and `24590fb`; a diff shows additions only.

| Arm | Run names | Unlabelled loss | Pool | Seeds | Hardware |
|---|---|---|---|---|---|
| A5c | `p12_A_5pct` | none (supervised) | – | 0–2 | cv02 |
| Dm5 | `p12_Dm_5pct` | `tolerant_pl`, λ_final = 0 | in-domain (455) | 0–2 | cv02 |
| Cm5 | `p12_Cm_5pct` | `tolerant_pl`, R = 2 px | in-domain (455) | 0–2 | cv02 |
| Dmx5 | `p12_Dmx_5pct` | `tolerant_pl`, λ_final = 0 | external (11,938) | 0–2 | cv02 |
| Cmx5 | `p12_Cmx_5pct` | `tolerant_pl`, R = 2 px | external (11,938) | 0–2 | cv02 |
| gDm5 | `p12_gDm_5pct` | `tolerant_pl`, λ_final = 0 | in-domain (455) | 3–5 | gaint |
| gCm5 | `p12_gCm_5pct` | `tolerant_pl`, R = 2 px | in-domain (455) | 3–5 | gaint |
| gA10 | `p12_gA_10pct` | none (supervised, 10%) | – | 0–2 | gaint |

gaint SSL arms use fresh seeds 3 to 5 and are never pooled with cv02 seeds.

**Scheduling** (protocol):
- **cv02:**
  - chained after the P11 queue had launched, plus 5 minutes (to avoid an earlier queue race);
  - ≤ 3 runs per GPU, only on a GPU with < 1,000 MiB used (never on another user's GPU).
- **gaint:** two sequential lanes, each run waiting for < 20,000 MiB used.

Run windows:
- cv02: 15 runs, 11 Oct 06:30 to 16:09 IST.
- gaint SSL: 6 runs, 03:57 to 15:21 IST.
- gaint gA10: 3 runs, finished 11 Oct 17:59 IST.
- All rc = 0.

**Locked rules** (cv02 unless stated):
1. **Pipeline check (descriptive):** Dm5 − A5c and Dm5 − D5 (P10), with the bootstrap.
2. **Cm5 helps:** Cm5 − Dm5 by rule 1. Cmx5 helps: Cmx5 − Dmx5.
3. **SSL beats supervised at 5%:** Cm5 − A5c and Cmx5 − A5c, credited only if rule 2 holds for that arm.
4. **Width check:** relP@2 drop > 0.05 against the matching Dm arm.
5. **Gap closed:** (C − A5c) / (L3@100% − A5c).
6. **gaint replication (descriptive):** gCm5 − gDm5, and gCm5 − A5 (P10's gaint reference).
   - A cv02 claim is "replicated" if the gaint contrast has the same sign and at least half the size on each metric that passed.
   - **gaint never rescues a cv02 rule that failed.**
7. **Calibration (descriptive):** gA10 − P6 L3 10% (cv02), to see how far gaint references can be read next to cv02 numbers.

**Results** (test, revised labels, mean ± sd; `results/p12/README.md`):

| Arm | HW | Pool | crack IoU | inactive IoU | crack relF1@2 | crack relP@2 | crack AP | inactive AP |
|---|---|---|---|---|---|---|---|---|
| A5c: supervised 5% | cv02 | – | 0.305±0.007 | 0.271±0.018 | 0.721±0.013 | 0.891±0.020 | 0.287±0.004 | 0.270±0.019 |
| D5 (P10): loss off, SSL labelled view | cv02 | 455 | 0.243±0.005 | 0.243±0.006 | 0.629±0.014 | 0.855±0.030 | 0.232±0.009 | 0.251±0.008 |
| Dm5: loss off, matched view | cv02 | 455 | 0.288±0.016 | 0.257±0.092 | 0.696±0.019 | 0.888±0.004 | 0.276±0.018 | 0.248±0.086 |
| Cm5: tolerant PL, matched view | cv02 | 455 | 0.311±0.010 | 0.274±0.139 | 0.737±0.014 | 0.857±0.077 | 0.329±0.016 | 0.348±0.121 |
| Dmx5: loss off, matched, external | cv02 | 11,938 | 0.305±0.002 | 0.270±0.074 | 0.727±0.005 | 0.879±0.022 | 0.291±0.001 | 0.256±0.065 |
| Cmx5: tolerant PL, matched, external | cv02 | 11,938 | 0.295±0.014 | 0.256±0.040 | 0.714±0.027 | 0.835±0.031 | 0.300±0.011 | 0.319±0.054 |
| A5 (P10) | gaint | – | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | 0.890±0.014 | 0.282±0.003 | 0.270±0.050 |
| gDm5 | gaint | 455 | 0.280±0.009 | 0.269±0.030 | 0.688±0.017 | 0.906±0.011 | 0.270±0.008 | 0.261±0.028 |
| gCm5 | gaint | 455 | 0.327±0.009 | 0.345±0.091 | 0.766±0.011 | 0.888±0.008 | 0.352±0.009 | 0.400±0.048 |
| gA10: supervised 10% | gaint | – | 0.400±0.007 | 0.351±0.046 | 0.820±0.010 | 0.903±0.010 | 0.407±0.003 | 0.359±0.038 |
| L3 10% (P6) | cv02 | – | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | 0.910±0.006 | 0.400±0.004 | 0.302±0.018 |
| L3 100% (P6) | cv02 | – | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | 0.939±0.003 | 0.593±0.003 | 0.420±0.018 |

**Verdict per rule:**

| Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|
| Dm5 − A5c (rule 1, descriptive) | −0.017 (0.020) | −0.015 (0.109) | −0.025 (0.027) | n.d. by the seed rule; the bootstrap shows a crack handicap (below) |
| Dm5 − D5 (rule 1, descriptive) | +0.045 (0.019) | +0.014 (0.107) | +0.068 (0.027) | The matched view removes most of P10's handicap |
| Cm5 − Dm5 (rule 2) | +0.023 (0.022) | +0.018 (0.192) | +0.040 (0.027) | **Cm5 helps** |
| Cmx5 − Dmx5 (rule 2) | −0.010 (0.016) | −0.013 (0.097) | −0.013 (0.031) | Cmx5 does not help |
| Cm5 − A5c (rule 3) | +0.006 (0.014) | +0.003 (0.161) | +0.015 (0.022) | **Fails: SSL does not beat supervised at 5% on cv02** |
| Cmx5 − A5c (rule 3) | −0.010 (0.018) | −0.015 (0.051) | −0.008 (0.034) | Fails |
| gCm5 − gDm5 (rule 6) | +0.047 (0.015) | +0.077 (0.111) | +0.078 (0.024) | **Replicates** rule 2 |
| gCm5 − A5 gaint (rule 6) | +0.029 (0.012) | +0.068 (0.123) | +0.058 (0.019) | Passes the arithmetic; cannot rescue the failed cv02 rule 3 |
| gA10 − L3 10% (rule 7, calibration) | +0.004 (0.010) | +0.056 (0.057) | +0.006 (0.012) | n.d.: gaint and cv02 supervised agree on crack within 0.006; inactive differs by seed-noise size |

- **Width check (rule 4, against the matching Dm):** relP@2 drops 0.031 (Cm5) and 0.044 (Cmx5); neither exceeds 0.05.
- **A disclosed script/protocol mismatch:** against A5c, Cmx5 drops 0.056. The script flags this, but the protocol's check is against Dm.
- **Gap closed by Cm5:** crack IoU 3%, inactive 2%, relF1@2 10%.
- **Interaction with 10% (descriptive):** (Cm − Dm) at 5% minus at 10% is crack IoU +0.014, inactive −0.053, relF1@2 +0.022. The loss moves crack more at 5% and inactive less.
- **Required count:** inactive is in 2 of the 23 labelled cells.

**Robustness** (image bootstrap, paired, test IoU, cv02 runs):

| Contrast | Δ, all cells | Δ without top-3 | 95% CI | P(Δ>0) |
|---|---|---|---|---|
| Dm5 − A5c, crack | −0.017 | −0.013 | [−0.024, −0.010] | 0.00 |
| Dm5 − A5c, inactive | −0.015 | −0.018 | [−0.039, +0.011] | 0.11 |
| Dm5 − D5, crack | +0.045 | +0.041 | [+0.035, +0.056] | 1.00 |
| Cm5 − Dm5, crack | +0.023 | +0.009 | [+0.005, +0.036] | 0.99 |
| Cm5 − Dm5, inactive | +0.018 | +0.004 | [−0.051, +0.073] | 0.71 |
| Cmx5 − Dmx5, crack | −0.010 | −0.018 | [−0.023, +0.000] | 0.03 |
| Cm5 − A5c, crack | +0.006 | −0.004 | [−0.009, +0.015] | 0.80 |
| Cm5 − A5c, inactive | +0.003 | −0.014 | [−0.067, +0.060] | 0.54 |
| Cmx5 − A5c, crack | −0.010 | −0.017 | [−0.021, −0.002] | 0.01 |

Source split for Cm5 − Dm5, crack:
- CSIR+ARTS (21 cells): −0.025 [−0.061, +0.004];
- CFVS/BMRK/SDLE (29 cells): +0.032 [+0.016, +0.044].

**Bin-0 share** (test):

| Arm | crack | inactive |
|---|---|---|
| A5c | 0.567 | 0.661 |
| Dm5 | 0.588 | 0.686 |
| Cm5 | 0.491 | 0.534 |
| Dmx5 | 0.561 | 0.651 |
| Cmx5 | 0.546 | 0.498 |

**E1 addendum** (after the locked analysis, descriptive; `results/e1/e1_p12.md`):

| Contrast | Set | crack relF1@2 (pooled) | crack false alarm | inactive IoU (pooled) | inactive cell IoU |
|---|---|---|---|---|---|
| Cm5 − Dm5 | test | +0.040 [+0.015, +0.061] | 0 vs 0 | +0.018 [−0.051, +0.073] | +0.049 [−0.007, +0.110] |
| Cm5 − A5c | test | +0.015 [−0.005, +0.030] | 0 vs 0 | +0.003 [−0.067, +0.060] | +0.043 [−0.024, +0.116] |
| gCm5 − A5 (gaint) | test | +0.058 [+0.037, +0.079] | 0 vs 0 | +0.068 [+0.022, +0.130] | +0.101 [+0.040, +0.176] |
| Cm5 − A5c | ext | +0.000 [−0.039, +0.038] | +0.095 [+0.035, +0.162] (worse) | +0.065 [+0.014, +0.128] | +0.212 [+0.065, +0.351] |
| Cmx5 − A5c | ext | −0.068 [−0.098, −0.041] | +0.234 [+0.142, +0.329] (worse) | +0.008 [−0.041, +0.036] | +0.130 [+0.079, +0.188] |
| gCm5 − A5 (gaint) | ext | +0.022 [−0.014, +0.056] | +0.104 [+0.046, +0.169] (worse) | +0.126 [+0.029, +0.246] | +0.445 [+0.218, +0.631] |

- On cv02 test, the crack relF1@2 gain of Cm5 over Dm5 is robust over cells; over A5c it is not.
- On gaint, gCm5 beats gaint's A5 on crack relF1@2 and on inactive, robustly over cells. At the time it was the clearest SSL-over-supervised result, but it is on gaint (seeds 3 to 5 vs A5's 0 to 2), and the locked rules give gaint no say.
- On unseen modules, the same pattern as P11: tolerant PL raises crack false alarms (by about 0.10 of crack-free cells) and improves inactive. The external-pool arm over-predicts inactive there (area error +0.69 pp) and loses crack.

**Reading:**
- **The loss effect on crack holds at 5% and replicates on gaint.**
  - Cm5 − Dm5 passes the seed rule and the cell bootstrap on cv02.
  - It shrinks to +0.009 without the top 3 cells, and it comes from the CFVS/BMRK/SDLE cells.
  - On gaint (fresh seeds) the same contrast is about twice as large.
- **Inactive is not measurable at 5%.** Seed sd reaches 0.14, and only 2 of 23 labelled cells contain it.
- **The loss-off control is below supervised on crack, robustly.**
  - Dm5 − A5c = −0.017 [−0.024, −0.010], in both source groups. That is larger than at 10% (P11: −0.007). gaint shows the same size descriptively (gDm5 − A5: −0.018).
  - The matched view already removed the labelled-view part (Dm5 − D5 = +0.045), so what remains is consistent with BatchNorm mixing.
- **SSL vs supervised at 5%: no on cv02.**
  - Cm5's crack gain over Dm5 (+0.023) about cancels the Dm5 handicap (−0.017), leaving +0.006 against A5c, not detectable.
  - On gaint the same comparison passes the arithmetic (+0.029).
  - The two machines disagree on the net verdict with 3 seeds each. That is why P13's primary contrast uses 5 seeds.
- **The external pool does not help at 5%.** Cmx5 ≈ Dmx5, and Cmx5 is below A5c on crack in the bootstrap (−0.010 [−0.021, −0.002]). Unlike Dm5, Dmx5 shows no crack handicap against A5c (0.305 vs 0.305).
- **Calibration (rule 7):** gaint and cv02 supervised 10% agree on crack within 0.006, so gaint's crack references can be read next to cv02's. Inactive cannot.

**Caveats.** One split; 3 seeds per arm; 50 test cells. Inactive is in 2 of 23 labelled cells. gaint arms use seeds 3 to 5 and gaint's A5 uses 0 to 2; never pooled with cv02.

**What it led to.** P13 (`10_experiments_P13_P16_E1.md`). It tests the BatchNorm explanation directly at 5% with a separate forward pass for unlabelled images (`ssl.student_forward=separate`, BN statistics frozen for them). It also adds CutMix, a hard-pseudo-label arm and 5 seeds for the primary contrast. With the separate forward and λ = 0 the student is bit-identical to supervised training, so A5c becomes the exact loss-off control.

---

## Summary across P8 to P12

| Exp | Labels | Loss vs its loss-off control | SSL vs plain supervised | Loss-off control vs supervised (the pipeline handicap) |
|---|---|---|---|---|
| P8 | 10% | C − D n.d. (crack +0.009 robust over cells only) | C − A −0.004 crack (not a rule) | D − A crack −0.013, inactive −0.101 (robust) |
| P9 | 10%, external | Cx − Dx passes on inactive +0.056 (not robust over cells) | Cx − A crack −0.011 (not a rule) | Dx inactive back at A level |
| P10 | 5% | none pass; in-domain seed 2 collapses; Cx5 loses crack on its own sources | not a rule (A5 on gaint) | D5 − A5 crack −0.055 (cross-hardware) |
| P11 | 10%, matched | **Cm − Dm passes, robust (inactive +0.071, relF1@2 +0.018)** | **Cm − A passes by seed rule** (inactive +0.071, relF1@2 +0.013); relF1@2 robust over cells, inactive not | Dm − A crack −0.007 (robust, small) |
| P12 | 5%, matched | **Cm5 − Dm5 passes (crack +0.023, relF1@2 +0.040)**, replicated on gaint | **Cm5 − A5c fails** (+0.006); gaint passes arithmetic but has no say | Dm5 − A5c crack −0.017 (robust) |

Status of these results inside the overall evidence: see `11_results_synthesis_and_claims.md`.

## Related docs
- `08_experiments_P1_P7_diagnostics.md`: how L3, the tolerant loss and the metrics were arrived at.
- `10_experiments_P13_P16_E1.md`: P13 (separate BN + CutMix), P14, P15, P16, E1.
- `07_methodology_rules_and_statistics.md`: rule 1, rules 2/3 crediting, bootstrap, leave-top-3-out, seeds, step matching.
- `04_glossary_and_naming.md`: arm-name key and metric definitions.
- `03_datasets_and_splits.md`: the 5% and 10% labelled sets, the in-domain and external pools, the test source mix.
- `13_problems_pitfalls_open_issues.md`: inactive measurability, machine disagreement, seed collapse.
- `11_results_synthesis_and_claims.md`, `12_decisions_log.md`, `14_code_and_infrastructure.md`.
