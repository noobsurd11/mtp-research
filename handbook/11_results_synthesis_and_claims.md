# 11. Results synthesis: what we know, what we can claim, what is still open

## What this covers
This file pulls the experiments together:
- **(a)** the evidence table: each claim the thesis could make, its evidence and its status;
- **(b)** the numbers worth remembering;
- **(c)** what can be claimed now and what cannot, with reasons;
- **(d)** how the conclusions changed over the project, and why supervised training beat SSL for so long;
- **(e)** what the two pending experiments (P15, P16) will decide, and how each possible outcome would move the claims;
- **(f)** where the proposal reframe and the mid-term deck outline stand.

It contains no new measurements. Every number points to the README or protocol it comes from.

The user's rule governs this file: "framing depends on final results, no presumptions, ever" (user message, 11 Oct 2026, 12:46 IST, in `docsrc/user_messages.md`; stable copy `sources/chat/user_messages_2026-10-07_to_11.md`, 07:16 UTC). So this file states evidence and open questions. It does not pick the thesis framing.

**Status at writing (11 Oct 2026, ~22:00 IST)**
- P1 to P14 and E1 are done.
- P15 (gaint, UCF-EL encoder) finished 22:26 IST and was analysed at about 22:40 IST (`results/p15/README.md`).
- P16 (cv02, SSL at 20/50/100%) is pending, about 03:00 to 04:30 IST on 12 Oct.

## Sources
- `to_human/results_2026-10-12.md`: the morning summary draft and its evidence table, section 3.
- `to_human/proposal_reframe_2026-10-11.md`.
- `to_human/midterm_deck_outline.md`.
- `to_human/directions_2026-10-10.md`.
- `results/p3_label_versions/README.md`.
- `results/p6/README.md`, `p7`, `p8`, `p9`, `p10`, `p11`, `p12`, `p13`, `p14` (each `README.md`).
- `results/p10/labelled_set_counts.txt`.
- `results/e1/README.md`, `e1_ext_v2.md`, `e1_p11.md`, `e1_p13.md`, `e1_p14.md`.
- Protocols `protocols/P13_cutmix_separate_bn.md` to `P16_label_fraction_curve.md`.
- The assistant's answer to the user on locked rules and design problems: 11 Oct ~17:30 IST, session transcript `~/.claude/projects/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5.jsonl`, line 6727.

## Reading conventions
- **Machines.** "cv02" and "gaint" are the two GPU servers. Results are never mixed across machines in a rule. gaint numbers are marked "(gaint)".
- **Old-era vs P-series.** Old-era numbers come from before the corrected baseline:
  - original 20211104 masks;
  - from-scratch U-Net++;
  - weighted CE;
  - batch 4 or 8;
  - SemiCE Mean Teacher.

  They sit in separate tables from P-series numbers (revised E-SCDD masks, L3 recipe). The terms are in `04_glossary_and_naming.md`.
- **Verdict wording.**
  - **passes / fails / n.d.** is the locked rule (P8 rule 1: Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on any primary, none worse).
  - **robust** means the 95% image-bootstrap CI excludes 0 and the sign survives removing the top-3 cells.
  - **Reading:** marks interpretation.
- **Primary metrics** (unless stated): test (50 cells), revised labels, argmax:
  - crack IoU;
  - inactive IoU;
  - crack relF1@2.

---

## (a) Evidence table
Rows 1 to 12 follow `to_human/results_2026-10-12.md` section 3, with wording tightened and evidence completed. Rows 13 and 14 are added here and are not yet in that file.

Where this table deliberately differs from that file:
- **Row 1:** that file says SSL effects are "≤ +0.023 at cv02 (P11, P12)". It predates P13; the largest cv02 SSL crack IoU effect is now BsM5's +0.036.
- **Row 2:** that file says "supported". After P13 (Cs5 − A5c crack +0.004 against a clean control) this table narrows it to inactive, with crack only against a joint-BN control.
- **Row 5:** adds P9's inactive pass (not robust).
- **Row 8:** that file says crack IoU "falls to ~1/3 for every model". That holds for L3 100% (0.471 → 0.152); other models fall further (L3 10% 0.396 → 0.080; A5c 0.304 → 0.045), so this table gives the numbers instead.
- **Row 12:** adds P7 to P10 (that file cites P13 only).
- That file's section 1 ETAs (P15 ~00:45, P16 ~07:00–09:30) are older than the ones used here.

| # | Claim | Evidence (source) | Status |
|---|---|---|---|
| 1 | The label version moves crack IoU more than any SSL effect | P3 (old-era models, exploratory): re-scoring on revised labels +0.05 to +0.07 crack IoU (`results/p3_label_versions/README.md`). P14 (locked): training on revised vs old labels at 10%, L3 − L3o +0.082 [+0.046, +0.129]; holds on old-label scoring (0.351 vs 0.332) and on unseen modules (+0.030 [+0.012, +0.048]) (`results/p14/README.md`). Largest cv02 SSL crack IoU effect: +0.036 (P13 BsM5 − A5c, secondary) | supported |
| 2 | The pseudo-label loss itself helps (vs a loss-off control) | P11 10% Cm − Dm: inactive +0.071 [+0.020, +0.121], relF1@2 +0.018 (joint BN). P12 5% Cm5 − Dm5: crack +0.023 [+0.005, +0.036] (joint BN), replicated on gaint (+0.047). P13 5%, clean control: Cs5 − A5c inactive +0.105 [+0.025, +0.179], crack +0.004 (n.d.) | supported for inactive; for crack IoU only against a handicapped (joint-BN) control |
| 3 | SSL beats a step-matched supervised baseline | **P13 5% primary** (5 vs 5 seeds, separate BN + CutMix): CsM5 − A5c inactive +0.117 [+0.042, +0.189], relF1@2 +0.033 [+0.006, +0.055], crack IoU +0.014 n.d.; robust over cells. BsM5 (hard PL + CutMix, 3 seeds, secondary): crack IoU +0.036 [+0.021, +0.048] too. P11 10% Cm − A passes (inactive +0.071 not robust over cells; relF1@2 +0.013 robust). P12 5% (joint BN) Cm5 − A5c fails on cv02 (`results/p11`, `p12`, `p13`) | supported at 5% on inactive and crack relF1@2; crack IoU only with hard PL (secondary). 20/50/100% pending (P16) |
| 4 | Joint-BN Mean Teacher handicaps the student | Loss-off control vs supervised, crack IoU: P11 Dm − A −0.007 [−0.016, −0.001]; P12 Dm5 − A5c −0.017 [−0.024, −0.010]; gaint gDm5 − A5 −0.018. BN recalibration after training does not remove it (`results/p13_audit/`). P13 fix (separate BN): Cs5 − Cm5 inactive +0.084 [+0.030, +0.143]; unseen-module false alarms −0.095 [−0.141, −0.050]; crack equal | supported; grows as labels shrink. The fix helps inactive and false alarms, not crack IoU |
| 5 | An external unlabelled pool (11,938 CSIR/ARTS cells) helps | P9 Cx − Dx: inactive +0.056 passes, not robust (CI [−0.013, +0.117]). P10 Cx5 − Dx5: crack IoU −0.012 [−0.026, −0.001] (robust over cells, n.d. by seeds) and relF1@2 −0.027 (worse by the rule), concentrated on CSIR+ARTS (−0.065). P11 Cmx − Dmx fails. P12 Cmx5 − Dmx5 fails. All with joint BN | not supported (joint BN only; Sx100 in P16 is the first separate-BN test) |
| 6 | Offset tolerance helps human labels too | P14: recovers 0% of the label-noise gap (L3To − L3o −0.004). On revised labels L3T − L3 inactive +0.037 passes, not robust ([−0.016, +0.093]); crack unchanged; crack AP −0.020 | not supported for label noise; weak for inactive |
| 7 | Related labelled data (UCF-EL pretraining) beats ImageNet init | P15 (gaint, 3 seeds): gU5 − A5 n.d. on all three (crack +0.0096, thr 0.0100); gU10 − gA10 worse on all three (crack −0.012, inactive −0.086, relF1@2 −0.014), robust over cells (`results/p15/README.md`) | not supported for this recipe; MIM untested |
| 8 | Models transfer to unseen modules | E1 extension (106 cells, 67 modules): L3 100% crack IoU 0.471 → 0.152, tolF1 0.80 → 0.41; L3 10% crack IoU 0.396 → 0.080 (`results/e1/README.md`, `e1_ext_v2.md`) | not supported (a measured limit) |
| 9 | Per-cell metrics measure more stably | E1: crack per-cell metrics are not more sensitive than pooled IoU on test; inactive cell IoU separates more contrasts (test 9 vs 7, ext 17 vs 10) | partly (inactive yes, crack no) |
| 10 | SSL's benefit depends on the label fraction | 5%: P12 (joint BN) no; P13 (separate BN) yes. 10%: P11 (joint BN) yes. 20/50/100%: P16 pending (Cs recipe; CutMix off by val pick) | open |
| 11 | Mixing-based perturbation (CutMix) matters | P13 CsM5 − Cs5: n.d. by seeds; over cells crack +0.010 [+0.004, +0.017], relF1@2 +0.015 [+0.004, +0.029]; unlabelled/supervised loss ratio 0.46 → 0.77. P13 val ranked Cs5 above CsM5 | weak |
| 12 | Tolerant pseudo-labels beat hard ones | P7 (L0 base, pilot): C − B inactive IoU +0.056 [+0.022, +0.086], robust. P8 C − B n.d.; P9 Cx − Bx n.d.; P10 C5 − B5 n.d. P13 under CutMix: CsM5 − BsM5 crack IoU −0.022 [−0.031, −0.016] (tolerant worse, robust); inactive equal | not supported on the L3 base; tolerant only beat hard on the old L0 base |
| 13 | The supervised recipe matters more than the SSL loss | P6 (locked): label-safe augmentation helps (crack AP +0.020, inactive AP +0.028; crack IoU +0.048 [+0.003, +0.097]). Only the L3 recipe turns labels into gains: L3 10% → 100% crack IoU +0.075, inactive +0.135; L0 10% → 100% no detectable effect. AP is not comparable across losses (bin-0 saturation: L3 10% scores 42% of GT crack < 0.001) (`results/p6/README.md`) | supported |
| 14 | Rare-class pseudo-label collapse is real and visible in training logs | P10: seed 2 collapses under both B5 and C5 (crack ≈ 0.13, inactive ≈ 0). Its rare-class PL share stays about 5× lower from step 4,000. P13 (separate BN): no collapse in 8 logged runs, rare_frac 0.0064 to 0.0109 (`results/p10`, `p13`) | supported as a failure mode (one collapse event, seed 2, at 5%) |

---

## (b) Numbers to remember

### Supervised label curve (P-series, L3 recipe, test, revised labels)

| Labels (cells) | Machine | crack IoU | inactive IoU | crack relF1@2 | Source |
|---|---|---|---|---|---|
| 5% (23) | cv02, 5 seeds (A5c) | 0.304±0.008 | 0.253±0.037 | 0.720±0.014 | `results/p13/README.md` |
| 5% (23) | gaint, 3 seeds (A5) | 0.298±0.005 | 0.277±0.055 | 0.708±0.012 | `results/p10/README.md` |
| 10% (47) | cv02 (L3 10%) | 0.396±0.003 | 0.294±0.019 | 0.814±0.003 | `results/p6/README.md` |
| 10% (47) | gaint (gA10) | 0.400±0.007 | 0.351±0.046 | 0.820±0.010 | `results/p12/README.md` |
| 20% (95) | cv02 (L3 20%) | 0.398±0.002 | 0.347±0.043 | 0.822±0.008 | `results/p6/README.md` |
| 50% (239) | gaint (P10 A50) | 0.437 | 0.427 | not in README | `results/p10/README.md` (label-curve table) |
| 50% (239) | cv02 | pending (P16 A50) | | | `results/p16/` when present |
| 100% (478) | cv02 (L3 100%) | 0.471±0.001 | 0.429±0.011 | 0.876±0.003 | `results/p6/README.md` |

**Reading:**
- Crack is flat from 10% to 20% (+0.002).
- Inactive climbs until 50%.
- The crack gap from 10% to 100% is 0.075.
- At 5%, crack drops by about 0.1.

### Label-version gap

**P-series, locked (P14, trained at 10%, L3)**

| Comparison | crack IoU | crack relF1@2 |
|---|---|---|
| L3 (revised) − L3o (old), scored on revised | +0.082 [+0.046, +0.129] | +0.081 |
| scored on old labels: L3 vs L3o | 0.351 vs 0.332 | 0.791 vs 0.758 |
| unseen modules | +0.030 [+0.012, +0.048] | +0.068 [+0.021, +0.110] |

**Old-era, exploratory (P3: same old-recipe models, re-scored on old vs revised labels, test)**

| Model | crack IoU old → revised | crack AP old → revised |
|---|---|---|
| SL-10% b8 | 0.304 → 0.355 | 0.492 → 0.527 |
| SL-100% b8 | 0.283 → 0.339 | 0.457 → 0.541 |

The two label versions agree at crack IoU 0.745 on test, but 0.98 within 2 px (`results/p3_label_versions/README.md`).

### SSL effects by label fraction and recipe (cv02 only; Δ vs the named reference)

| Labels | Exp | Recipe | Contrast | crack IoU | inactive IoU | crack relF1@2 | Verdict |
|---|---|---|---|---|---|---|---|
| 10% | P8 | joint BN, SSL labelled view | C − D (loss off) | +0.009 | +0.059 | +0.015 | n.d. |
| 10% | P8 | same | D − A (supervised) | −0.013 | −0.101 | | handicap (bootstrap) |
| 10% | P9 | joint BN, external pool | Cx − Dx | +0.004 | +0.056 | +0.007 | passes (inactive), not robust |
| 10% | P11 | joint BN, matched view | Cm − Dm | +0.009 | +0.071 | +0.018 | passes |
| 10% | P11 | same | Cm − A | +0.002 | +0.071 | +0.013 | passes (credited) |
| 5% | P10 | joint BN, SSL labelled view | C5 − D5 | +0.003 | +0.007 | +0.001 | n.d. (one seed collapsed) |
| 5% | P10 | joint BN, external pool | Cx5 − Dx5 | −0.012 | +0.090 | −0.027 | fails (worse) |
| 5% | P12 | joint BN, matched view | Cm5 − Dm5 | +0.023 | +0.018 | +0.040 | passes |
| 5% | P12 | same | Cm5 − A5c | +0.006 | +0.003 | +0.015 | fails |
| 5% | P13 | separate BN + CutMix, tolerant | CsM5 − A5c (primary, 5 v 5) | +0.014 | +0.117 | +0.033 | passes, robust |
| 5% | P13 | separate BN, tolerant, no CutMix | Cs5 − A5c | +0.004 | +0.105 | +0.018 | passes (inactive) |
| 5% | P13 | separate BN + CutMix, hard PL | BsM5 − A5c | +0.036 | +0.113 | +0.052 | passes (secondary, 3 seeds) |
| 20% / 50% / 100% | P16 | separate BN, tolerant, no CutMix | S − A | pending | | | |

gaint, descriptive only:

| Contrast | crack IoU | inactive IoU | crack relF1@2 |
|---|---|---|---|
| P12 gCm5 − gDm5 | +0.047 | +0.077 | +0.078 |
| P12 gCm5 − A5 | +0.029 | +0.068 | +0.058 |

Sources: `results/p8` to `results/p13` READMEs.

### Unseen modules (E1 extension, 106 cells)

| Model | crack IoU test → ext | inactive cell IoU on ext |
|---|---|---|
| L3 100% | 0.471 → 0.152 | 0.175 |
| L3 10% | 0.396 → 0.080 | 0.086 |
| A5c | 0.304 → 0.045 | 0.033 |
| CsM5 | 0.317 → 0.046 | 0.500 |

Sources: `results/e1/e1_ext_v2.md`, `e1_p13.md`.

### Noise and concentration (why small effects are hard)

**Seed sd**, L3-recipe arms without collapse (`results/p6`, `p10`, `p12`, `p13`, `p14`):

| Metric | Range of sd |
|---|---|
| crack IoU | 0.001 to 0.016 (most arms 0.003 to 0.011) |
| inactive IoU | 0.003 to 0.139 |

Outside that set: the old L0 recipe at 10% has crack sd 0.051 (P6), and P10's collapsed-seed arms B5/C5 reach crack 0.090 to 0.104 and inactive 0.194 to 0.204.

**Where inactive pixels sit** (`results/p6/README.md`, `results/p13/README.md`):

| Split | Cells with inactive | Share held by the top 3 cells |
|---|---|---|
| test | 16 of 50 | 59% |
| val | 6 of 54 | 89% |

For crack, the top 3 test cells hold 32% of pixels.

**Labelled cells with inactive** (`results/p10/labelled_set_counts.txt`, `protocols/P16_label_fraction_curve.md`):

| Labels | Cells with inactive |
|---|---|
| 5% | 2 of 23 |
| 10% | 4 of 47 |
| 20% | 9 of 95 |
| 50% | 20 of 239 |

**Crack is rare:** 0.19% of train pixels (`to_human/midterm_deck_outline.md` slide 2).

---

## (c) What can be claimed now, and what cannot
These hold for one split (seed 0), the 50 BenchmarkEL test cells, cv02 and the L3 recipe, unless stated.

### Can be claimed
1. **The crack label version is the largest lever measured.**
   - Training on revised instead of old labels gives +0.082 crack IoU, robust (P14).
   - Re-scoring alone gives +0.05 to +0.07 (P3, exploratory).
2. **The supervised recipe matters, and AP misleads across losses** (P6, locked plus exploratory).
3. **At 5% labels, Mean Teacher with separate BN, tolerant PL and CutMix beats a step-matched, 5-seed supervised baseline** on inactive IoU (+0.117) and crack relF1@2 (+0.033), robust over test cells. Crack IoU is not detectably better (P13 primary).
4. **Sharing BatchNorm between labelled and unlabelled images handicaps the student.** The handicap grows as labels shrink, and post-hoc BN recalibration does not remove it (P11, P12, P13 audit).
5. **A tolerant loss does not recover old-vs-revised label noise** (P14 rule 2).
6. **The joint-BN external pool did not help** (P9 to P12).
7. **Every model loses most crack performance on unseen modules** (E1).
8. **Hard pseudo-labels with CutMix improve crack IoU at 5%** (+0.036, robust over cells and both source groups). This is a secondary contrast with 3 seeds: report it as such.

### Cannot be claimed (and why)
- **"SSL improves crack IoU" in general.** The primary arm is n.d. on crack IoU; only the secondary hard-PL arm passes.
- **"Tolerant pseudo-labels beat hard ones."** They are n.d. on L3 at 10% and 5%, and worse on crack under CutMix (P13). The only win is on the old L0 base (P7, pilot).
- **"Offset-tolerant objective for both human and pseudo labels" as a demonstrated method.**
  - P14 fails recovery.
  - P13 favours hard PL on crack.
  - The full ALHVR-style region routing was never run in the P-series; P5 is an offline probe.
- **Anything about SSL above 10% labels.** P16 is pending.
- **That related-data pretraining helps.** P15 says no for UCF-EL encoder transfer with this recipe (equal at 5%, worse at 10%), and the MIM/self-supervised rival was never run.
- **Inactive results as general facts.**
  - Test inactive rests on 16 cells, 3 holding 59%.
  - Validation disagrees on inactive in P13 (val 6 cells).
  - Inactive claims need the "few cells" caveat every time.
- **Cross-machine statements.**
  - gaint replications are descriptive.
  - The machines disagreed on P12's SSL-vs-supervised verdict (cv02 fail, gaint pass).
  - P13 has no gaint replication.
- **Generality beyond one split and BenchmarkEL.** UCF-EL was not used in the P-series except as P15's pretraining data.
- **Anything about severity or power loss.** Not measured. The user: "not part of this project unless we get some valid data" (11 Oct).
- **Old-era SSL results** (SemiCE Mean Teacher; ALHVR-20 over SL-20) are invalid.
  - SemiCE's target is incoherent (P2).
  - ALHVR-20 equals its λ = 0 control, so its gain did not come from the ALHVR losses. BatchNorm batch composition was the leading explanation but was "not yet shown" (phase 1 handoff, `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`).
  - See `06_history_phase0_phase1.md`.

---

## (d) How the conclusions changed, and why supervised beat SSL for so long

### Timeline

| When | What was believed | What changed it |
|---|---|---|
| Phase 0/1 (before 7 Oct) | "Unlabelled losses have zero effect" (Mean Teacher λ = 1.5 equals λ = 0); ALHVR-20 beats SL-20; "label count does not move BenchmarkEL" (SL-100 ≈ SL-20) | P2: the SemiCE target marks ≥ 2 classes positive on 100% of unlabelled pixels, so it was never a valid consistency loss. ALHVR-20 = its λ = 0 control. P3/P6: the old recipe does not use labels, and part of the label-count result was label-version noise (`06_history_phase0_phase1.md`, `08_experiments_P1_P7_diagnostics.md`) |
| 7 to 8 Oct | The training pipeline may have bugs | P1: the pipeline is exact. Blur and rotation on 1 to 2 px labels destroy crack fitting (AP 0.929 → 0.587 on train images); CE+Dice fits crack far better |
| 10 Oct | SSL with tolerant PL should help at 10% (directions report §1.2) | P7/P8: no loss passes at 10%. The SSL pipeline with the loss off is below supervised (D − A crack −0.013, inactive −0.101) |
| 11 Oct morning | Maybe more unlabelled data or fewer labels shows the effect | P9: a 28× pool does not amplify. P10: no gain at 5%, a collapse in one seed, handicap −0.055. User: "supervised beating ssl, hows that possible" → audit, P13 locked |
| 11 Oct afternoon | Fix the labelled view (P11) | P11: matched view removes the handicap at 10% (Dm − A n.d. by seeds), and Cm beats supervised (inactive, relF1@2). P12 at 5%: the loss helps crack vs its joint-BN control, but there is no net gain over supervised on cv02; gaint disagrees |
| 11 Oct ~17:24 IST | SSL tested only at 5 to 10% | User: "why we using 5 or 10% for ssl? ... try 20, 50 and 100". P16 locked |
| 11 Oct evening | Tolerance may fix human label noise; P12's crack gain is a real loss effect | P14: tolerance recovers 0% of the label-noise gap. P13: with separate BN, SSL beats supervised at 5% (inactive, relF1@2). Tolerant PL alone adds about 0 on crack against the clean control, so P12's +0.023 mostly offset the joint-BN handicap. Hard PL + CutMix is best on crack |

### Why supervised beat SSL for so long
From the assistant's answer to the user on 11 Oct (transcript line 6728) and the P13 audit. The user asked "are we self-sabotaging?"; the answer was "The rules, no. The design, yes."

**The rules were not the problem.**
- Rule 1 is lenient: about 2 standard errors, roughly one-sided p ≈ 0.06 with 3 seeds. A two-sided 95% test would need 2.8. (At 5 vs 5 seeds the same threshold is about 2.58 standard errors, so P13's primary faced a stricter bar.)
- SSL was credited whenever the gain was there (P11 rules 2 and 3; P12 rule 2).

**The design was. Five things:**
1. **Regime.** We ran at 5 to 10% labels, where inactive is in only 2 or 4 labelled cells and the teacher is weakest. Addressed by P16 (running).
2. **A handicap built into every SSL arm until P13.**
   - First a stronger labelled view (removed in P11).
   - Then joint BN: −0.007 crack IoU at 10%, −0.017 at 5%, before the loss did anything.
   - Fixed by P13's separate forward.
3. **3 seeds for effects of 0.01 to 0.02**, against the user's own ≥ 5 rule. Fixed for the P13 and P16 primary contrasts (5 vs 5); P13's secondary arms (BsM5, Cs5), P14 and P15 still use 3.
4. **Tuning asymmetry.** The supervised recipe (L3) was picked by a 4-step ladder on val. The SSL hyperparameters (λ, thresholds, R) were fixed in advance and never tuned.
5. **Small in-domain pool, mismatched external pool.**
   - The in-domain pool is 239 to 455 cells.
   - The external pool is two sources, and half of it is low-contrast.

**Plus the audit's other finding: weak perturbation.** The unlabelled loss was about 10× smaller than the supervised loss. CutMix raised the ratio to 0.77 (P13).

---

## (e) What P15 and P16 will decide
No outcome is presumed. These are the possible results under the locked rules, and how each would move the evidence table.

### P15 (gaint): UCF-EL-pretrained encoder vs ImageNet init
**Outcome (added 11 Oct ~22:40 IST):** gU5 n.d. on all three; gU10 worse on all three (the "a primary is worse" row below). See `results/p15/README.md`. The table is kept as written before the result.

Arms: gU5 vs A5 at 5% labels; gU10 vs gA10 at 10%. 3 seeds each, rule 1 plus the width check (`protocols/P15_ucf_encoder_transfer.md`).

| Outcome | Effect on claims |
|---|---|
| Both gU5 and gU10 pass | Claim 7 supported (on gaint). Related labelled data used as pretraining is a lever comparable with SSL. Descriptive check: does gU5 reach gA10, i.e. stand in for doubling the labels? |
| Only one fraction passes | Claim 7 partly supported, fraction-dependent; report both |
| Neither passes (n.d.) | Claim 7 not supported: ImageNet init stays the default. P4's frozen-feature gap did not translate to fine-tuning gains with this recipe |
| A primary is worse | Negative transfer. Plausible cause to check, not presume: UCF-EL labels crack as a region class, so class definitions differ |

Caveats:
- gaint only, so comparisons with cv02 results (e.g. P13) are cross-machine and descriptive.
- 3 seeds.
- One pretraining recipe (DeepLabV3+, Fioresi schedule).
- The self-supervised (MIM) rival is not tested.

### P16 (cv02): SSL at 20%, 50% and 100%
Arms S20 − A20, S50 − A50, Sx100 − A100, 5 vs 5 seeds, rule 1 (`protocols/P16_label_fraction_curve.md`). The recipe is P13's Cs: tolerant PL, separate BN, no CutMix (chosen on P13 val).

| Outcome | Effect on claims |
|---|---|
| S20 passes | SSL's benefit extends beyond the scarcest labels. 20% has 9 labelled inactive cells and supervised crack is flat from 10% to 20%, so a crack gain there would be informative. Claim 10 gets a shape |
| S20 and S50 n.d. | The SSL gain at this recipe is confined to the scarcest labels (5%). Claim 10 "depends on fraction" is then supported in the direction the literature reports. Caveat: Cs was the weakest P13 arm on crack test |
| Sx100 passes | Extra unlabelled data helps a fully labelled model, with the external pool under separate BN. That would revise claim 5, whose evidence was all joint BN |
| Sx100 n.d. | Consistent with claim 5 (the external pool does not help) |
| Any S arm worse on a primary | SSL hurts at that fraction; report it as a negative result |

The descriptive label-fraction curve (`scripts/p16_curve.py`) puts these next to P13's 5% point within cv02. 10% has no separate-BN SSL arm; P11 used joint BN.

---

## (f) Where the proposal reframe and the mid-term deck stand

### `to_human/proposal_reframe_2026-10-11.md` (written 11 Oct, before P13 and P14 results)

**What it argues**
- The problem is "thin-structure and region segmentation, from few labels with imprecise geometry, with a long-tailed class distribution, several image sources, and a small test set, whose real output is a measurement". SSL is one tool, not the core.
- An effect-size budget ranks the levers: labels and measurement, then the supervised recipe, then label quantity. The unlabelled loss comes last.
- Our lead: rigour (locked protocols, loss-off controls, bootstrap); a measured mechanism for thin rare classes (offset tolerance); measured failure modes with candidate fixes.
- Goal and objectives:
  - O1 measurement;
  - O2 learning from imprecise thin labels (one offset-tolerant objective plus rarity routing);
  - O3 using unlabelled data, compared fairly (SSL vs pretraining/transfer vs distillation);
  - O4 a 2 to 5M-parameter deliverable with a severity pipeline.
- Experiments E1 to E6, and a "mistakes we own" table.

**Status of its experiments**

| Item | Status |
|---|---|
| E1 (task metrics) | done: crack no, inactive yes |
| E2 = P14 | done: recovery fails |
| E3 = P15 (UCF transfer part) | done: not supported (5% n.d., 10% worse); MIM part not run |
| E4 = P13 | done: primary passes |
| E5 (distillation) | not started |
| E6 (severity pipeline) | not started |

**Statements newer evidence touches** (for the morning neutral update; the parent agent owns that update):
- **§2's budget row "Unlabelled loss (SSL): crack ≈ 0 to +0.01; inactive +0.05 (fragile)"** predates P13. With separate BN at 5%: inactive +0.117 robust, crack relF1@2 +0.033 robust, and hard PL + CutMix crack IoU +0.036.
- **§2's "BN mixing" row** is now tested: the fix is in P13.
- **§3 point 2 and O2's "one offset-tolerant objective for both kinds of target"** are weakened:
  - P14 shows tolerance does not recover human label noise;
  - P13 shows tolerant PL is not better than hard PL under CutMix.

**The user's rule:** framing depends on final results. The reframe is a draft to be revised from this evidence table, not a fixed position.

### `to_human/midterm_deck_outline.md` (draft of 10 Oct, 17 slides; slide 14 last updated 11 Oct 07:54 IST with P9/P10, commit `65a9f06`)

**Structure**
- Title (part 1 of 3: training methodology).
- Problem, data and label revision (P3).
- What existed (EL segmentation papers; SSL methods with ALHVR as inspiration).
- What we inherited (P2), diagnosis (P1), probes (P4, P5).
- P6 baseline, proposed method (rarity-routed offset-tolerant PL).
- P7/P8 design and results.
- Discipline, further work, timeline.

**What is outdated**
- Slide 14 stops at P8 to P10 and lists P11/P12 as "running now". P11 to P14 and E1 results are not in it.
- Slide 12 presents "rarity-routed, offset-tolerant pseudo-labels" as the proposed method. Claims 6 and 12 above now weaken the tolerance part.
- The timeline (slide 17) predates P13 to P16.

**Plan stated by the user:** the user starts the PPT after one day of work (11 Oct message, point 6: "youve 1 day for the work then ill startr on ppt"). The mid-term date was "about 14 Oct (confirm the date)" in the outline.

---

## Related docs
- `00_START_HERE.md`: how to use the handbook.
- `06_history_phase0_phase1.md`: the old-era results and why some are invalid.
- `07_methodology_rules_and_statistics.md`: the rules, seeds, bootstrap and leniency.
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md`: per-experiment detail.
- `12_decisions_log.md`: who decided what and why.
- `13_problems_pitfalls_open_issues.md`: open problems behind the caveats here.
- `15_status_remaining_work.md`: what remains after P15 and P16.
- `16_faq_for_the_guide.md`: short answers to likely questions.
