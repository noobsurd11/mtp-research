# 16. FAQ: questions the user is likely to ask, with grounded answers

**What this covers.** Short answers to the questions a newcomer to this project tends to ask, each with its numbers and the doc or file to read next. The answers are as of 12 Oct 2026, about 05:30 IST, updated 13 Oct ~08:15 IST for P17 and P13 Amendment 2 (Q8, Q10, Q20b). All experiments, P17 included, are finished. Do not give a stronger answer than the one here without new evidence.

**Sources:** every answer names its own source. The main ones:
- `results/p1` to `results/p14` READMEs;
- `to_human/proposal_reframe_2026-10-11.md`;
- `to_human/midterm_deck_outline.md`;
- `to_human/situation_report_2026-10-08.md`;
- the handoffs in `sources/`.

---

## A. The problem

**Q1. What is this project, in one sentence?**
Learning to segment rare, thin defects (cracks, inactive areas) in EL images of solar cells from few and imprecise pixel labels. It asks whether unlabelled images (semi-supervised learning) or related data help, judged under strict, pre-locked rules. → `01_project_overview_and_scope.md`

**Q2. Why are crack IoU numbers so low (0.30 to 0.47)?**

Cracks are 1 to 2 px wide lines, so strict pixel IoU mostly measures label jitter:
- A perfect mask shifted by 1 px scores 0.47 to 0.56 IoU.
- Two annotations of the same cell agree at crack IoU 0.257.
- Old and revised labels agree at 0.73 to 0.81 IoU but 0.98 within 2 px.
- Real cracks are about 3.4 µm wide against about 300 µm per pixel, so any label width is a convention (lit).

That is why the project also reports **relaxed F1@2** (a hit counts within 2 px) and per-cell task metrics. The best supervised model (L3, 100% labels) reaches crack IoU 0.471 and relaxed F1@2 0.876.

Sources: `midterm_deck_outline.md` slide 2; `proposal_reframe` §1; `results/p3_label_versions/README.md`; `results/p6/README.md`. → `02`, `07`

**Q3. What did the user mean by "it trained on 47 images and tested on sam e47, to get 0.3 iou on cracks" (typos as written)?**

That was the user's worry on 7 Oct. It started the analysis-first restart:
- 47 cells is the 10% labelled subset.
- The old crack model could not even fit its own training images.
- P1 (overfit check) showed the old recipe was the cap: fitting rose from 0.38 to 0.86 with a better recipe.

Sources: `results/p1/README.md`; `proposal_reframe` §2. → `06_history_phase0_phase1.md`, `08_experiments_P1_P7_diagnostics.md`

**Q4. Why only two classes (crack, inactive) when the dataset has 24?**

These two drive severity and power loss. Gridline is noisy and was excluded from the headline metric in phase 0.

Several of the 24 classes are almost absent:
- 7 are missing from val and 8 from test;
- four have under 1,300 pixels in all of train.

Sources: phase 0 handoff; `~/mtp/MTP_session_handoff_2026-10-07.md` §3.1. → `03_datasets_and_splits.md`

## B. Semi-supervised learning and why it first "lost"

**Q5. What is Mean Teacher, in plain words?**

Two copies of the same network:
- The **teacher** is a slow moving average (EMA) of the student's weights.
- It labels unlabelled images; those labels are the "pseudo-labels".
- The **student** learns from the real labels plus the pseudo-labels, under stronger augmentation.

The teacher is the model that gets evaluated. → `04_glossary_and_naming.md`

**Q6. Why did supervised beat SSL for most of the project?**

Four reasons, all measured:
1. **The old SSL loss was invalid.** SemiCE is not a valid consistency loss (P2). Every pre-P2 Mean Teacher result is void.
2. **The Mean Teacher pipeline handicapped its own student.**
   - Labelled and unlabelled images shared BatchNorm batches.
   - With the loss switched off, the SSL arm was already below plain supervised: −0.007 crack IoU at 10% (P11), −0.017 at 5% (P12).
   - So the loss's gain only cancelled a handicap.
3. **The regime was hard.** At 5 to 10% labels, inactive appears in only 2 to 4 labelled cells. The teacher is weak, and one seed in three collapsed at 5% (P10).
4. **The perturbation was weak.** There was no CutMix, and the unlabelled loss stayed about 10x below the supervised loss (P13 audit).

When P13 removed reasons 2 and 4, SSL beat supervised at 5% (Q8).

Sources: `results/p11`, `p12`, `p13/README.md`; `protocols/P13_cutmix_separate_bn.md`. → `09`, `10`, `13`

**Q7. Why did we test SSL only at 5% and 10% labels? Isn't that self-sabotage?**

The reasoning at the time:
- SSL papers report gains when labels are scarce.
- Supervised crack IoU barely moves from 10% to 20% labels (+0.002, P6).
- So it looked like there was no room above 10%.

The user challenged this on 11 Oct ("they are really low ... try 20, 50 and 100"). Claude agreed, in part:
- at 5 to 10% inactive is unmeasurable by construction;
- segmentation SSL benchmarks use 1/16 to 1/2 of the labels.

P16 was added to cover 20/50/100%. Result (12 Oct): with P13's Cs recipe (CutMix off by the locked val pick), SSL is n.d. against supervised at every fraction. The inactive gain shrinks from +0.105 at 5% to +0.029, +0.006 and +0.003 (`results/p16/README.md`). On 11 Oct Claude also listed the design choices that worked against SSL: the 5 to 10% regime, the joint-BN handicap, 3 seeds, an untuned SSL recipe against a supervised recipe picked from a 4-step ladder (L3 was chosen on P6 val+test results; `protocols/P8_tolerant_pl_on_l3.md`), and small or mismatched pools.

Sources: `protocols/P16_label_fraction_curve.md`; session summaries. → `07`, `13`

**Q8. So does SSL beat supervised now?**

At 5% labels, yes on two of the three primary metrics:
- **P13 primary claim**, CsM5 − A5c (5 vs 5 seeds): inactive IoU +0.117, crack relaxed F1@2 +0.033. Both are robust over test cells. Crack IoU is +0.014, not detectable.
- **Secondary contrast**, hard pseudo-labels + CutMix (BsM5): with 5 seeds (seeds 3–4 added post hoc, P13 Amendment 2) it passes on all three: crack IoU +0.029, inactive +0.107, relF1@2 +0.045. On 3 seeds crack was +0.036.

At 20/50/100% (P16, Cs recipe, 5 vs 5 seeds): no. n.d. on all three primaries at every fraction, with or without the noisy test cell (Q26). On unseen modules (secondary) an inactive gain remains at 20% and 50%. Do not claim that SSL "cannot" help above 10%: only one recipe was tested there.

Source: `results/p13/README.md`, `results/p16/README.md`, `results/p17/README.md`. → `10`, `11`

**Q9. Is P12's "the loss helps crack" result still valid?**

The P12 rule outcome stands as computed. Its meaning changed after P13:
- P12's control was handicapped: the loss-off arm sat 0.017 below supervised on crack.
- Against P13's clean control, the tolerant loss alone adds about +0.004 on crack.
- So P12's +0.023 mostly undid the handicap.

Source: `results/p13/README.md` "Reading". → `11_results_synthesis_and_claims.md`

**Q10. Tolerant or hard pseudo-labels: which is better?**

It depends on the pipeline:
- **P7** (10%, old L0 base, joint BN): tolerant beat hard on inactive (+0.056 [+0.022, +0.086], robust). Hard pseudo-labels pushed missed defects to "certain background".
- **P13** (5%, L3 base, separate BN, with CutMix): on 3 hard-PL seeds, hard beat tolerant on crack IoU (−0.022 for tolerant, robust over cells). With 5 hard-PL seeds (Amendment 2) it is −0.015, n.d. by the seed rule, still below 0 over cells [−0.023, −0.009]. Inactive was equal.

So the "tolerant is better" premise is not supported under CutMix at 5%; "hard is better" holds over cells, not by seeds.

Sources: `results/p7/README.md`; `results/p13/README.md`.

**Q11. Why didn't the big external unlabelled pool (11,938 cells) help?**

It is a different distribution:
- it comes only from CSIR/ARTS;
- 57% of it has half the contrast of the labelled images.

Measured:
- A 28x larger pool did not amplify the loss effect (P9).
- At 5% labels the external pool's crack pseudo-labels hurt crack on its own sources: −0.065 [−0.092, −0.026] (P10).
- The pool showed no loss effect in P11 or P12 either.

Sources: `results/p9`, `p10`, `p11`, `p12`; `proposal_reframe` §1. → `09`

## C. Rules, statistics, and trust

**Q12. What are the "locked rules", and are they too strict?**

Each experiment's protocol is committed before its runs. It fixes the arms, metrics and decision rules.

The main rule (P8 rule 1): an arm beats another if, on at least one primary metric:
- the gain exceeds max(0.01, 2·√((sd_A² + sd_B²)/3));
- and no primary metric is worse.

The rules are **not strict**:
- With 3 seeds, 2·√((sd_A² + sd_B²)/3) is about 2 standard errors, a one-sided p of about 0.06.
- A pass on any one of three metrics is lenient.
- With 5 vs 5 seeds (P13 primary, P16) the code still divides by 3, so the threshold is about 2.58 standard errors (one-sided p ≈ 0.016): stricter than at 3 seeds.

What looked like strictness was mostly noise: few seeds, and inactive decided by about 3 test cells. → `07_methodology_rules_and_statistics.md`

**Q13. Why final-step weights and not the best checkpoint on validation?**
- Val has 54 cells, and only 6 contain inactive (3 hold 89% of its inactive pixels).
- Selecting on val flipped signs in phase 1.
- In P13, val disagreed with test on inactive: SSL arms looked worse on val and better on test.

Sources: `results/p6/README.md` point 4; `results/p13/README.md`. → `07`

**Q14. Why never compare gaint numbers with cv02 numbers?**

Training is deterministic per machine, but different GPUs give different numbers. P12 rule 7 measured it with supervised 10% runs on both machines:
- crack agrees to about 0.004;
- inactive differs by 0.056, about the seed spread.

So a gaint result can replicate a cv02 one but never rescue it.

Source: `results/p12/README.md`. → `07`

**Q15. What does "robust over cells" mean?**

The 50 test cells are resampled with replacement 2,000 times, keeping the pairing across arms and seeds (image bootstrap). "Robust" means:
- the 95% interval excludes 0;
- the difference survives dropping the 3 cells with the most ground-truth pixels of that class (leave-top-3-out).

This checks something the seed rule does not: whether the result depends on which cells happen to be in the test set. → `07`

**Q16. Why do inactive results swing so much?**

Inactive appears in only 16 of 50 test cells (revised masks; 17 on the old masks), and 3 cells hold 59% of its pixels. On val it is 6 of 54, with 3 cells holding 89%. Most inactive differences before P13 shrank or flipped sign without the top 3 cells (e.g. `results/p6/README.md` point 5).

Sources: `results/p6/README.md` point 4; `results/p13/README.md`.

## D. Labels and the supervised baseline

**Q17. What are "old" and "revised" labels, and why does it matter so much?**

| | Old (`masks_coded`) | Revised (E-SCDD, `masks_escdd`) |
|---|---|---|
| Release | BenchmarkEL `dataset_20211104` | downloaded from E-SCDD (HuggingFace `snt-ubix/escdd`); for crack and inactive these are exactly BenchmarkEL's own `20221008` masks (audit 12 Oct, doc 17); covers 577 of our 582 cells |
| Crack labels | dotted along continuous cracks | dotted cracks joined and widened |

- Re-scoring the same models on revised labels raises crack IoU by +0.05 to +0.07 (P3).
- Training on revised instead of old labels gives +0.082 crack IoU at 10%, robust (P14).
- The revised-label model also wins when scored on the old labels.

From P6 on, everything trains and scores on revised labels. → `03`, `08`, `10`

**Q18. What is L3, and is it the best supervised model?**

L3 is the P6 recipe:
- U-Net++ with an ImageNet ResNet34 encoder;
- CE+Dice loss;
- label-safe augmentation;
- revised masks.

It was chosen because it is the only recipe that turns more labels into better scores: 10% → 100% gives crack IoU +0.075, inactive +0.135. The old recipe L0 gave none.

It is not best on every metric:
- At 10%, L1 (no ImageNet, weighted CE) has higher inactive IoU, 0.473 vs 0.294. That difference is mostly decided by 3 cells: without them the L1→L2 and L2→L3 inactive drops shrink from −0.089 each to −0.005 and −0.019. L1 at 10% even beats L3 at 100% on inactive (0.473 vs 0.429), and that comparison flips sign without the top 3 cells (−0.044 → +0.088), so it is not a finding.
- L3's AP is saturated: many ground-truth pixels score below 0.001.

Source: `results/p6/README.md`. → `08`

**Q19. Does a loss that tolerates 1 to 2 px offsets fix noisy human labels? (P14)**

No:
- It recovered 0% of the old-vs-revised gap (+0.082).
- On revised labels it passes the rule on inactive (+0.037), but that is not robust over cells.
- It lowers crack AP by about 0.02.

Source: `results/p14/README.md`.

## E. P15, P16 and the mid-term: what to say

**Q20. What did P15 and P16 decide?**
- **P15** (gaint), now **done**: does an encoder trained on UCF-EL labels beat ImageNet initialisation at 5% and 10% labels? No. gU5 − A5 is n.d. on all three primaries (crack +0.0096 vs threshold 0.0100). gU10 − gA10 is worse on all three (crack −0.012, inactive −0.086, relF1@2 −0.014), robust over cells. Source: `results/p15/README.md`.
- **P16** (cv02), now **done**: does SSL (separate BN, tolerant PL, CutMix off) beat supervised at 20% and 50% labels (in-domain pool) and at 100% (external pool, the only unlabelled data left)? No. S20 − A20, S50 − A50 and Sx100 − A100 are n.d. on all three primaries (5 vs 5 seeds), and no arm is worse. Source: `results/p16/README.md`.

Each outcome changes different rows of the evidence table. → `10`, `11`

**Q20b. What was P17, and what did it decide?** (13 Oct)
- The user asked about trying two recent papers, DCA (CVPR 2026) and SKCDF (CVPR 2025). Claude advised skipping DCA (a 3D, three-expert-decoder method, too much to build in the 16 h left) and testing SKCDF's main component only: keep pseudo-labels out of the labelled decoder, and train a second decoder on them that follows the first by EMA. The user: "cool, go with ur calls".
- Question: does BsM5's gain need the labelled decoder to fit pseudo-labels?
- Result (5 vs 5, locked): BsD5 − BsM5 is n.d. on all three (−0.006 / +0.011 / −0.008), and BsD5 still beats supervised on all three. So most of the gain reaches the teacher without the decoder fitting pseudo-labels. The thresholds are about 40% of the gain, so a smaller decoder share is not excluded. The decoupled teacher has lower AP (crack 0.310 vs 0.367).
- It is "SKCDF-style decoupling", never "SKCDF": the other components were not run.

Source: `results/p17/README.md`, `protocols/P17_decoupled_decoder.md`. → `10` (P17), `11` row 16

**Q21. What can be said at the mid-term right now?**

Only what the evidence table marks supported, with its scope. The user's rule is "framing depends on final results, no presumptions, ever". → `11_results_synthesis_and_claims.md`

**Q21b. How do we compare with the published BenchmarkEL results?** (13 Oct)
In the paper's own convention (per-image IoU, median over test cells, rule A as inferred) and on its labels, our supervised recipe at 100% labels scores crack 0.354, gridline 0.303, inactive 0.443 (mean 0.367). Pratt 2023's headline DeepLabv3+ scores 0.25 / 0.20 / 0.38 (mean 0.28). Do not call it a like-for-like benchmark win: the rule is inferred, the paper's numbers are read off a figure and come from single runs, and the release is uncertain. Source: `results/pratt_compare/README.md`.

**Q21c. Does evaluating the EMA teacher (not the student) inflate SSL results?** (13 Oct)
No. At step 20,000 teacher and student score the same within ±0.005 (BsM5, CsM5, BsD5; 15 runs). The learning rate ends at 0, so the EMA has caught up. Source: `results/ema_check/README.md`.

**Q22. What is E1?**

A re-scoring of every checkpoint with per-cell task metrics:
- crack tolerance-F1, length error, false alarms;
- inactive area error, detection F1, cell IoU.

It also uses a 106-cell extension from modules never trained on. Findings:
- Per-cell crack metrics are not more sensitive than pooled ones; per-cell inactive IoU is.
- Every model loses most crack performance on unseen modules (L3 100%: 0.471 → 0.152).

Source: `results/e1/README.md`. → `10`

**Q22b. What did the E-SCDD audit find, in one breath?** (12 Oct; `results/escdd_audit/README.md`, doc 17)
- **Crack and inactive labels.** E-SCDD's are pixel-identical to BenchmarkEL `20221008`'s, so the "revised labels" effect (P3, P14) is BenchmarkEL's own correction.
- **Contents.** The release has 903 labelled files (693 + 117 new + 93 synthetic in train), not the paper's 1,000.
- **Overlap with our pool.** 100 of the 117 new cells are in our external unlabelled pool.
- **E-SCDD's test.** It shares 48 cells with our train and has only 9 inactive cells.
- **What changes.** No result changes; the attribution wording and the data available for a larger test or more labels do.
- **Decisions** for the user are in doc 15.

**Q22c. Should we switch to E-SCDD's split or add its cells?**
That is the user's decision. The facts:
- its test overlaps our train;
- 233 new labelled cells exist, 111 of which the x-arms saw as unlabelled data;
- adding labels means a new base recipe, not an extension of P6–P16.

→ `17`, `15`

## F. Practical

**Q23. How long does a run take, and where?**
- cv02: SSL about 1.0 step/s with 3 runs per GPU, so about 5.5 to 7.5 h for 20,000 steps. Supervised is faster.
- gaint P15 runs: about 1 h 40 min each.

→ `14_code_and_infrastructure.md`

**Q24. How can a number be checked independently?**

Every results folder has:
- `raw/` re-score JSONs, with keys `test/<run>` → `new_escdd` → class → metric;
- `*_rules.txt`;
- a reproduce command (e.g. `bash scripts/post_ssl.sh p13 <gpu> 13`).

→ `14_code_and_infrastructure.md` "How to find X"

**Q25. Which old results must never be quoted as findings?**
- Anything using SemiCE (all old Mean Teacher runs).
- ALHVR-20 versus supervised: it equals its loss-off control, so the gain did not come from the ALHVR losses (BatchNorm batch composition is the leading hypothesis, never shown).
- Pre-GaussNoise-fix numbers.
- Pilot-era runs.
- Any SSL-vs-supervised gain with mismatched optimizer steps (the 8x mismatch gave a fake +7.4).

Sources: memory note `mtp-el-ssl-project.md`; phase 0 handoff. → `06`, `13`


**Q26. Why do some P16 runs have crack IoU near 0.29 when the others are near 0.45?**

One test cell. `CSIR_00070_r8_c4` is the noisiest of the 582 labelled cells (noise sigma 46.0; median 1.48). In 4 of the 24 P16 runs (two supervised, two SSL), the model calls 15 to 31% of it crack. That is 39k to 80k false-positive pixels against a true crack area of 787 px, and the run's crack IoU drops by 0.11 to 0.18.
- Val is normal. The failure is not specific to SSL: it hit 2 supervised and 2 SSL runs.
- It also hit P6 `L0_10pct_s1`, which makes most of P6's L1 − L0 crack IoU gain (+0.048) an artefact (about +0.010 without the cell).
- The P16 README reports every contrast with and without the cell (post hoc). The verdict is the same both ways.
- Whether to make that a standing check is the user's call.

Source: `results/p16/README.md` "One test cell". → `13` A11

## Related docs
All of them; start from `00_START_HERE.md`.
