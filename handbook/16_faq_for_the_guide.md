# 16. FAQ: questions the user is likely to ask, with grounded answers

**Update 30 Oct 2026 (additive):** section G (Q27 to Q33) covers 24 to 30 Oct: the best model, the unlabelled pool, encoder erasure, the 5% lesson, scuff labels and what is running. A dated qualifier is added to Q20 (P15).

**Update 1 Nov 2026, ~21:00 IST (additive):** section I (Q42 to Q51; Q51 added ~21:40 after THIN-B3) covers 31 Oct to 1 Nov: PF2, the PF ensemble (PF2E), Om's 11 unseen-panel ideas, the E1 policy and what is running. Dated "[Qualified 1 Nov: ...]" notes on Q27, Q35, Q36 and Q38.

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

**Q11b. Did ALHVR, the method the project started from, work once it was ported properly? (added 23 Oct)**

No. AL1 (cv02, 5 v 5, D7 pool) fixed the old port's problems:
- full λ from step 4k;
- the P-series base;
- noise-only perturbation, because the reference dropout erased the encoder;
- full-resolution prototypes;
- a bit-identical loss-off control.

Measured:
- ALHVR was **worse** than supervised on crack IoU, inactive IoU and crack relF1@2 (−0.017 / −0.132 / −0.031), in every cell set.
- Its routing (Ω1 mask) and prototype module are n.d. in one-change contrasts.
- The same two networks with plain cross pseudo-labels are level with supervised.
- The existing BsM5 recipe still beats supervised.
- Post hoc reading: ALHVR's losses halve inactive recall.

Sources: `team_2026-10-21/alhvr/results.md`, `verify_a2.md`. → `10` (AL1), `13` (B3, E11, A13)

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
  [Qualified 30 Oct: the fine-tune used for P15 erased encoder layer3/4 in every ResNet-34 run measured (Q29), so P15 likely tested little more than conv1/layer1 transfer (S; not measured on the P15 encoder). "No" holds for that recipe only.]
- **P16** (cv02), now **done**: does SSL (separate BN, tolerant PL, CutMix off) beat supervised at 20% and 50% labels (in-domain pool) and at 100% (external pool, the only unlabelled data left)? No. S20 − A20, S50 − A50 and Sx100 − A100 are n.d. on all three primaries (5 vs 5 seeds), and no arm is worse. Source: `results/p16/README.md`.

Each outcome changes different rows of the evidence table. → `10`, `11`

**Q20b. What was P17, and what did it decide?** (13 Oct)
- The user asked about trying two recent papers, DCA (CVPR 2026) and SKCDF (CVPR 2025). Claude advised skipping DCA (a 3D, three-expert-decoder method, too much to build in the 16 h left) and testing SKCDF's main component only: keep pseudo-labels out of the labelled decoder, and train a second decoder on them that follows the first by EMA. The user: "cool, go with ur calls".
- Question: does BsM5's gain need the labelled decoder to fit pseudo-labels?
- Result (5 vs 5, locked): BsD5 − BsM5 is n.d. on all three (−0.006 / +0.011 / −0.008), and BsD5 still beats supervised on all three. So most of the gain reaches the teacher without the decoder fitting pseudo-labels. The thresholds are about 40% of the gain, so a smaller decoder share is not excluded. The decoupled teacher has lower AP (crack 0.310 vs 0.367).
- It is "SKCDF-style decoupling", never "SKCDF": the other components were not run.

Source: `results/p17/README.md`, `protocols/P17_decoupled_decoder.md`. → `10` (P17), `11` row 16

**Q20c. What was P18?** (13 Oct, exploratory)
- The BsM recipe (best at 5%) run at 10% (3 seeds) and 20% (5 seeds), to see whether P16's "no gain from 20% up" was the label fraction or the Cs recipe. Exploratory, because BsM was picked after seeing P13's test results.
- Inactive IoU gain over supervised: +0.132 at 10% and +0.060 at 20% (rule arithmetic passes; the 20% CI over cells includes 0). Crack: +0.012 and −0.006, n.d.; one BsM20 seed failed on the noisy cell. Without that cell crack is +0.017 (passes) and +0.013 (just below).
- So the answer is "partly the recipe", for inactive. No locked verdict changes.

Source: `results/p18/README.md`, `protocols/P18_bsm_label_fraction.md`. → `10` (P18), `11` rows 3 and 10

**Q21. What can be said at the mid-term right now?**

Only what the evidence table marks supported, with its scope. The user's rule is "framing depends on final results, no presumptions, ever". → `11_results_synthesis_and_claims.md`

**Q21b. How do we compare with the published BenchmarkEL results?** (13 Oct)
In the paper's own convention (per-image IoU, median over test cells, rule A as inferred) and on its labels, our supervised recipe at 100% labels scores crack 0.354, gridline 0.303, inactive 0.443 (mean 0.367). Pratt 2023's headline DeepLabv3+ scores 0.25 / 0.20 / 0.38 (mean 0.28). Do not call it a like-for-like benchmark win: the rule is inferred, the paper's numbers are read off a figure and come from single runs, and the release is uncertain. Source: `results/pratt_compare/README.md`.

**Q21c. Does evaluating the EMA teacher (not the student) inflate SSL results?** (13 Oct)
No. At step 20,000 teacher and student score the same within ±0.005 (BsM5, CsM5, BsD5; 15 runs). The learning rate ends at 0, so the EMA has caught up. Source: `results/ema_check/README.md`.

**Q21d. Did we reproduce Hanifi et al. 2025 (the 29-class Keras baseline)?** (14 Oct, P19)
- Yes, with their released code on the release split (their own split and augmentation are not public). VGG16-UNet: features 0.678 ± 0.020 (paper 0.663), crack 0.352 (0.335), gridline 0.316 (0.297), inactive 0.469 (0.550).
- The defect mean is lower (0.246 vs 0.326) mostly because the release test split has no dead cell or belt mark, which their metric scores as 0. The paper's model ranking is within seed noise.
- It is a public baseline on a different split, metric and label set from ours, so it is not compared with P-series numbers.

Source: `results/p19/README.md`, `protocols/P19_hanifi2025_reproduction.md`. → `11` ("Hanifi 2025 reproduced"), `05` §16

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

## G. 24 to 30 Oct: the best model, the unlabelled pool, and the move to 100% (added 30 Oct)

**Q27. What is the best model now?**
FINAL (25 Oct, Track M): the 5-seed mean-softmax ensemble of the 100%-label L3 recipe (U-Net++, ImageNet ResNet-34, CE + Dice on crack and inactive, label-safe augmentation, 512 px), with +0.75 added to the crack logit (chosen on val).
- Clean test (49 cells): crack IoU **0.492** (one model: 0.474), crack recall 0.703 at precision 0.621, relF1@2 0.897, crack components found 0.834, inactive IoU 0.456, mIoU_rob 0.583.
- Without the bias (bias 0): crack IoU 0.488. This is the robust choice: with +0.75 the ensemble calls 10,867 crack px on the corrupted test cell, at bias 0 it calls 2.
- "Almost all cracks" (relaxed recall ≥ 0.90 at relaxed precision ≥ 0.90) is not reached: 0.866 at 0.930. On unseen modules crack recall is 0.215.
- No single-model training change tried at 100% beat it (Dice on more classes, ResNet-50, +107 E-SCDD cells, 2× resolution), all under the house optimizer (Q29).
- protocol_100 (running from 30 Oct 12:05 IST) may change this; it has no result yet. [Qualified 31 Oct: it did not; every contrast n.d. (Q34, Q35)] [Qualified 1 Nov: still FINAL by rule; the PF ensemble does not match it on test at its pre-registered operating point (Q42).]

Sources: `team_2026-10-24_go/trackM/results_final.md`, `verify_final.md`. → `18` §M7, `11` row 18

**Q28. Does the unlabelled pool help?**
It depends on how it is used and at what label fraction. What is measured:
- **Pseudo-labels / consistency (label propagation):** yes at 5% (BsM5 crack IoU +0.029, inactive +0.107), not detectably at 20 to 100%. At 100% a crack gain of +0.01 or more is excluded (clean cells, Cs recipe). Sources: docs 10, 11; `team_2026-10-27_unlabelled/SYNTHESIS.md`.
- **Feature learning from the pool, at 5% labels:** no detectable gain. MIM5 n.d., every estimate negative; DDeP5 n.d., a small shift equal to a free bias; AM killed. Sources: `team_2026-10-29_features/verify_mim5.md`, `verify_ddep5.md`.
- **Not yet answered:** feature learning (MIM) with a fine-tune that keeps it, and crack copy-paste onto pool cells, both at 100% labels. That is protocol_100 (no result yet). [Qualified 31 Oct: answered, no for both (Q34)]
- **The pool's proven use so far:** choosing what to label. Track D: 12 crack-containing cells beat 12 random cells and the best SSL arm, for crack (oracle-selected).
- **Why the pool cannot fix the main unseen-module failure:** 75% of E1 crack sits in half-cut cells with scuff streaks, a context the pool barely contains.

→ `18` §U, `19` §2, §3, §7

**Q29. What is encoder erasure?**
Our standard fine-tune (Adam lr 1e-3, coupled weight decay 1e-4, 20k steps) ends the deep encoder layers (ResNet-34 layer3 and layer4) almost orthogonal to where they started: cosine 0.005 to 0.018 and −0.001 to 0.001 to their initial weights, with norms at 2 to 9% of init. It happens for both starts tried (ImageNet, MIM), at 5% and at 100% labels. Two seeds even end unrelated at layer4 (cosine 0.007).
- **It is early:** at step 2,000 layer3/4 are already at cosine 0.070 / 0.003 while their norms are still 0.33 / 0.21 of init. The direction goes during warmup and the peak learning rate, before the weights shrink.
- **So:** only conv1 and part of layer1 keep anything of the pretrained init. The deep features are re-learned from labels.
- **Consequence:** every "pretraining / init / backbone does not help" result so far (P15, MIM5, Track M's ResNet-50) was obtained under this one optimizer, which was never varied. Erasure was measured on ResNet-34 runs; for P15's and Track M's other encoders it is likely, not measured (S), and for ConvNeXt (LayerNorm) the mechanism is not established.
- **Likely cause (S):** BatchNorm makes the conv weights scale-invariant, so their direction can turn freely; coupled weight decay then shrinks them.
- **The test:** protocol_100's encoder-preserving fine-tune (PF: encoder frozen 1k steps, then 0.1× lr, encoder weight decay 0). In its smokes PF keeps layer3/4 at cosine 0.975 to 0.990 at 4k steps (training only, no test result).

Sources: `team_2026-10-29_features/coach_100.md` §0; re-derived in `protocol_100.md`. → `19` §4, `13` C15

**Q30. Why was 5% the wrong test for the pool question?**
- The user asked about adding the pool to a model trained on **all** labels (28 Oct). The 5% screen was copied from the 27 Oct plan without checking it against that question. The user caught it on 30 Oct: "why 5%? I asked about adding the pool to 100% labels."
- 5% does not buy power. 100% is better powered: clean MDE crack 0.012 vs 0.019; inactive 0.032 vs 0.084 (only 2 training cells have inactive at 5%).
- 5% only buys a larger effect, and only for methods whose effect shrinks as labels grow.
- For copy-paste the 5% test is wrong in kind: its "dose" is the labelled cracks (20 components at 5%, 554 in the frozen 100% library).

Sources: `diag_5pct_to_100pct.md`; `SESSION_RECORD_2026-10-28_to_30.md` §0, §5. → `19` §5, `13` C14

**Q31. When does a null at low labels carry over to full labels?**
A working rule (S, `diag_5pct_to_100pct.md` §4), not a theorem. Two things must hold:
1. the method does not consume labels (pretraining, a decoder init), and
2. the low-label estimate is tight on the target class.

Copy-paste and loss changes fail (1); inactive at 5% fails (2). Our own data has a case where a 5% null did not carry: joint-BN Mean Teacher was n.d. at 5% and passed at 10%. And the rule assumes the optimizer keeps what the method learned; under encoder erasure (Q29) a pretraining null says little either way. The team now tests pool ideas on top of 100% labels unless the user asks otherwise. → `19` §5, `11` row 24

**Q32. Is scuff ever labelled crack?** (30 Oct)
Yes, in our masks. P6 put the old label back on E-SCDD's scuff pixels. In train, 649 of 3,246 scuff px (6 cells) became crack, including `ARTS_00051_r6_c2`, the only ARTS crack cell at 5% labels. In test, 2 cells hold 236 scuff px labelled crack. E1 scoring ignores scuff. The user decided to train scuff as its own class (B3, after protocol_100). Whether test GT keeps those 236 px as crack is an open user decision. → `17` §5.11, `13` A14

**Q33. What is running, and what is waiting on the user?** (30 Oct, ~12:00 IST)
- Running: protocol_100 on gaint (4 arms × 5 seeds at 100% labels), launched 12:05 IST 30 Oct. First answer (the 15 fine-tunes) about 00:00 to 01:00 IST 31 Oct. CP100 is held behind a decoy gate (pending at 12:22 IST); if it goes, its answer comes about 07:00 IST 31 Oct. No result exists yet. [Qualified 31 Oct: done; see Q41]
- Also running: B2 pool mining (candidates only), gaint CPU.
- Waiting on the user: marks on the B1 label-audit sheets; whether to pixel-label mined pool cells (B2); the scuff test-GT option; ELPV download; the 40-segment audit; closing idle cv02 shells.

→ `15` §1f, §3b

## H. 30 to 31 Oct: protocol_100 results (added 31 Oct)

**Q34. Does the unlabelled pool help at 100% labels?**
No, for both routes tested (protocol_100, gaint, 5 v 5, all 478 train labels; both openings recomputed by coach):
- **Learned encoder features:** MIM100-PF − SUP100-PF, crack IoU +0.0048 (thr 0.0113) on all 50 / −0.0017 (0.0100) without the noisy cell; relF1@2 and inactive IoU n.d. too. The fine-tune kept the MIM encoder (layer3/4 cosine 0.96 at 20k), so this is a fair test.
- **Pasted cracks on pool backgrounds:** CP100 − SUP100-g, crack +0.0076 (0.0307) / +0.0003 (0.0100); n.d. with and without logit adjustment.
- Power: clean MDE crack 0.012. Conditions: one split, 50 test cells, ResNet-34 U-Net++, these two methods. Sources: `verify_100_o1.md`, `verify_100_o2.md`. → `19` §10, `11` rows 25, 26

**Q35. Did keeping the encoder (PF) help?**
Not on test: SUP100-PF − SUP100-g n.d. on all three primaries in both sets (crack −0.0012 / −0.0061). It trades a little crack recall for precision. On E1 it is the largest change any arm has made (crack recall 0.169 → 0.213, inactive IoU 0.041 → 0.245), but that is descriptive (Q36). coach recommends it as the base recipe anyway: equal on test, more robust out of distribution. → `11` row 27
[Qualified 1 Nov: on new seeds 5 to 9 (PF2) PF is BETTER on test crack relF1@2, narrowly (+0.0117 / +0.0120 vs floor 0.0100), with crack IoU and inactive IoU n.d., and its E1 inactive gain replicated (+0.1890). Q44.]

**Q36. Why is PF's E1 gain not a result?**
- E1 has been read by every protocol and is never for selection (`13` C17).
- The crack-recall gain sits in the 29 scuff + half-cut cells (0.094 → 0.152); on the other 77 cells crack IoU falls (0.261 → 0.238; `results/f100/opening1/o1_extra.txt`).
- A claim needs new seeds with E1 co-primaries stated before the runs (coach's PF2 proposal) or an independent unseen-module set.
[Qualified 1 Nov: PF2 replicated the inactive part on new seeds with pre-registered E1 co-primaries (+0.1890 BETTER); the crack-recall part did not replicate (+0.0271 n.d.). Same E1 cells, so cell selection is still not controlled. Q44, Q46.]

**Q37. What does the CP100 decoy flag mean?**
The decoy test pastes nothing on real test cells; it asks whether the model learns to call paste seams crack. At 20k steps CP100 fired on decoys 4.41x as often as SUP100-g (0.0125 vs 0.0028), and its rate had tripled since 4k. Gate 6b let CP100 run because the rate was falling at 4k; that did not hold. It changes no conclusion, because CP100 is n.d. anyway; CP also doubled false crack px on crack-free val cells (178 → 389). → `13` C16

**Q38. Does a bigger encoder (ResNet-50) help?**
Only a descriptive lead. In the inference-only D checks (val + E1, no test), a 5-model RN50 ensemble passed the pre-registered E1 read narrowly (+0.060 target recall at precision cost 0.047; limits +0.05 / 0.05), and doubling a ResNet-34 ensemble did not move the target (+0.001), so it is not ensemble size. Track M R3's RN50 was WORSE on test inactive. Next would be RN50-PF vs SUP100-PF. → `11` row 28, `verify_d.md`
[Qualified 1 Nov: no. Under PF, RN50-PF − SUP100-PF is WORSE on test inactive (−0.0289, thr 0.0251, both sets), and the E1 scuff + half-cut lead turned negative (−0.0225; ensembles −0.025). RN50 is closed under PF. Q45.]

**Q39. Should we download the 159k-image Hugging Face pool?**
No. poolscout showed it is Pratt's own pool: CSIR + ARTS only, no new half-cells, no BMRK / CFVS, none of E1's half-cut module family; 21 of our 50 test cells are in it by ID and about 2,400 byte-identical copies sit under other IDs. vetter's condition for a download (a MIM gain at opening 1) failed. → `11` row 29, `12` D58

**Q40. Was gaint's 2 GB memory floor for root's finllm kept?**
Not everywhere, most likely. Opening-1 scoring ran beside two CP runs under a gate that assumed ~3 GB passes; the logit-adjustment pass (5,106 MiB, measured later) probably left about 1.5 GB free for about 5.5 min (estimate, not a reading). finllm survived and no log shows an out-of-memory error. Since then free memory is logged every 10 s during any overlap (minimum over the CP overlap 6,609 MiB) and concurrent gates use measured peaks + 2 GB. → `13` D28, `14` §1.2c

**Q41. What is running, and what is waiting on the user?** (31 Oct, ~07:30 IST)
- Running: nothing of ours on gaint or cv02.
- Waiting on the user: PF as the base; PF2 (needs vetter Q1); RN50-PF; vetter's 11 questions; B1 and B2 marks; deleting the HF sample; who rebooted gaint; the 40-segment audit and 4 label questions; the idle cv02 shells.

→ `15` §1g, §3c, §4c

## I. 31 Oct to 1 Nov: PF2, the PF ensemble, Om's 11 ideas (added 1 Nov)

**Q42. Is the PF ensemble better than FINAL?**
No claim either way.
- At its pre-registered operating point (argmax, because D2's bias tripped the val width flag), the PF ensemble E-PF has clean-test crack IoU 0.4846 vs FINAL's 0.492.
- E-PF reaches 0.4920 only at bias 1.5, which the pre-registered val width flag rejected (val crack precision drop +0.0753 > 0.05; on test, crack precision 0.670 → 0.584). That is not a "matches FINAL" result.
- FINAL ran on cv02 with other commits and bias +0.75; PF2E ran on gaint. They are not compared by rule.
- What PF2E does show: E-PF vs the house ensemble E-g, test n.d. on all three primaries (all point estimates positive) and E1 inactive IoU +0.2141 (CI above 0). coach and judge recommend E-PF over E-g as the deployable candidate; the user decides.
Sources: `team_2026-10-31_next/verify_pf2e.md`. → `20` §5, `11` row 34

**Q43. Did any unseen-panel idea work?**
Not yet on a verdict, apart from PF's inactive effect.
- Dropped or closed: per-panel thresholds (idea 1), intensity normalisation (2: E1's "brighter" look is a white letterbox), high resolution (6: a repeat of R5), appearance augmentation (11), test-time BN adaptation (9: T9 FAIL; entropy TTA / TENT dropped without a run), SAM on cracks (10).
- Parked: neighbour reference and periodic removal (3, 4: the model does not confuse busbars with cracks), half-cut routing (the pre-check on synthetic half-cuts failed).
- Running or queued: thin-crack losses and a scuff class (THIN-B3), synthetic half-cuts (HC, idea 5), a DINOv3 encoder screen (A8, idea 8). [Qualified 1 Nov ~21:40: THIN-B3 is verified: no arm passes; Skeleton Recall lifts E1 crack detection at a precision cost (Q51). HC and A8 still queued.]
- Method note: SAM fills partly found inactive regions (S10), at 50% labels.
→ `20` §2, §3, `11` rows 35 to 39

**Q44. Is PF now better than the house recipe?**
On these numbers, yes for inactive on E1's cells (10 inactive cells in 7 images), narrowly for test crack relF1@2, and no difference on test crack IoU or inactive IoU.
- PF2 (seeds 5 to 9): E1 inactive IoU 0.048 → 0.237 (BETTER, replicated); test relF1@2 +0.0117 / +0.0120 (BETTER by 0.0017 / 0.0020; leave-top-3-out +0.0015); E1 crack recall n.d.
- PF2E (ensembles): E1 inactive +0.214 with CI above 0, test n.d.
- judge's reading of the E1 inactive gain: "fewer false inactive calls on module edges plus twice the inactive recall on E1", on 10 cells in 7 images; borderline under Bonferroni.
→ `20` §4-5, `11` rows 30 to 34

**Q45. What did ResNet-50 under PF show?**
A FAIL: test inactive IoU 0.4557 → 0.4269 (−0.0289, thr 0.0251) in both sets, the same risk Track M's R3 showed. D's E1 lead (+0.060 under the house recipe) became −0.025 under PF. RN50 is closed under PF; the foundation-encoder question moved to the A8 screen. → `20` §4, `11` row 33

**Q46. What is E1 now, and how often has it been read?**
Since 31 Oct ~15:00 (user) E1 is a second test set: a protocol may pre-register E1 co-primaries, read once at its opening, never for tuning or selection. Openings so far: #1 PF2 (1 Nov 06:33), #2 THIN-B3 (running at writing), #3 HC (armed), #4 PF2E (1 Nov 19:02). Before the policy E1 was read many times, so FINAL and protocol_100 seeds 0 to 4 are "not blind" on E1. Co-primaries are not corrected for multiplicity (disclosed). Ledger: `team_2026-10-31_next/e1_openings.md`. → `20` §8, `13` C17, C19

**Q47. Is the E1 failure a threshold problem?**
Not within each cell type: the E1 precision-recall curve lies below val's at every bias, and label-free per-panel thresholds lose. Across cell types there is a large offset on E1's own labels (best half-cut bias +5.4 vs full −0.8, oracle), but simulated half-cuts do not show it (+0.4 / +0.9), so it cannot be chosen without labelled half-cuts that look like E1's. → `20` §2.1, §3.1, `11` row 35

**Q48. Why is there no labelled half-cut set to tune on?**
Our 582 labelled cells hold no half-cuts. Hanifi's 36 half-cuts have unusable crack labels (1,792 px over 17 cells, 48% within 10 px of spacing, border or the cut line; FINAL finds 1 of 17). E1's 58 half-cuts are the only good half-cut labels, and E1 is a test set. → `13` A16

**Q49. Did gaint's 2 GB memory floor hold in PF2?**
Yes, by 587 MiB. PF2's logit-adjustment pass over 15 runs peaked at 7,758 MiB (the smoke said 5,824), taking free memory to 2,635 MiB for about 30 s beside two THIN runs and finllm. The scoring gate was raised to 9,900 MiB before any THIN number. → `13` D38

**Q50. What is running, and what is waiting on the user?** (1 Nov, ~20:30 IST)
- Running: THIN-B3's opening on gaint (started 19:40). Armed behind it: the A8 screen and HC runs, A8 scoring, the HC opening. B6 waits for cv02 (≥ 3 free GPUs) and its build.
- Waiting on the user: the deployable model (E-PF?), the D2 width flag for future protocols, whether half-cut labels are wanted, the A8 full arm if the screen says GO; still open: the HF sample, the 30 Oct gaint reboot, the 40-segment audit; the B1 / B2 marks are optional (team-lead's reading of the user's 31 Oct line on manual labelling; not done, not re-asked).
→ `15` §1i, §3d, §4d
[Qualified 1 Nov ~21:40: THIN-B3's opening ended 21:13 and is verified (Q51); the A8 screen runs started at 21:15; the SKR follow-up is a new open question for the user.]

**Q51. Did the thin-crack losses or the scuff class help?** (added ~21:40)
No arm passes its pre-registered rule (THIN-B3, gaint, seeds 5 to 9 vs SUP100-PF; coach VERIFIED, judge CONFIRMED):
- **Skeleton Recall: FAIL.** Test crack IoU −0.0136 / −0.0140 (WORSE; narrow: leave-top-3-out +0.010), from wider predictions on the largest cracks (relP@2 −0.070). But at matched val precision it finds more test crack components (+0.041, BETTER), and on E1 it is the first arm that clearly lifts crack detection: relF1@2 +0.059 (BETTER), any-hit component recall 0.381 → 0.523, at ~2x the false-alarm px (crack-free E1 cells ×2.4, scuff ×2.0). E1 pixel recall and IoU are inflated by width and not quoted.
- **clDice: FAIL** (relR@2 at matched val precision WORSE, −0.037); no better at matched test precision.
- **Scuff class (B3): n.d.;** the class was never learned (train scuff IoU 0.000, all 5 seeds), so the arm only relabelled 649 train px.
- BEST stays SUP100-PF. An SKR follow-up (weight 0.1 or a wider OP grid, a precision guard) is the user's call. → `20` §6.0, `11` rows 40 to 42

## Related docs
All of them; start from `00_START_HERE.md`.
