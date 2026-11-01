# 13. Problems, pitfalls and open issues

## What this covers
Everything that went wrong, could go wrong, or is still unknown. It has five groups:
- **(a) Data:** problems with the data itself.
- **(b) Past invalid results:** results that are invalid, and why.
- **(c) Design weaknesses:** weaknesses in how our experiments are designed and judged.
- **(d) Infrastructure:** incidents with the servers and tooling.
- **(e) Open questions:** what is still unresolved, and what would resolve it.

Each item gives:
- **What:** the problem in plain words.
- **Evidence:** numbers, with the source file.
- **Impact:** what it does to our conclusions.
- **Mitigation:** what was done, or what could be done.

Each item also has a **status**:
- **resolved:** fixed, or shown harmless;
- **mitigated:** reduced or worked around, but still there;
- **open:** nothing done yet.

Use it when the user asks "why can't we just say X?" or "what is wrong with this result?". The decisions taken in response are in `12_decisions_log.md`.

Status date: 12 Oct 2026, ~05:30 IST, updated 13 Oct ~16:30 IST for P17 and P13 Amendment 2 (C2, C6, C10, C11, D3, D19, E3, E16). All P-series experiments (P1 to P17) are done. A11 and E15 were added after P16.

Update 30 Oct 2026, ~12:00 IST (handbook refresh for 24 to 30 Oct; additive). New items A14, A15, C14, C15, D20 to D27, E18 to E22. Dated "[Qualified 30 Oct: ...]" notes on A12, A5, C13, E2, E8 and E12. Sources: `SESSION_RECORD_2026-10-21_to_27.md`, `SESSION_RECORD_2026-10-28_to_30.md`, `team_2026-10-29_features/` (`log.md`, `coach_100.md`, `spec_b3_scuff.md`, `verify_*.md`), docs 18 and 19.

Update 1 Nov 2026, ~21:00 IST (handbook refresh for 31 Oct to 1 Nov; additive). New items A16, A17, C18, C19, D34 to D45, E26 to E30 and summary rows for them. (~21:40: THIN-B3 notes on A17 and E27.) Dated "[Qualified 1 Nov: ...]" / "[Answered 1 Nov: ...]" notes on C17, E23 and E24. Sources: `SESSION_RECORD_2026-10-31_to_11-01.md`, `team_2026-10-31_next/` (`log.md`, verifications, `ideas/`); doc 20.

## Sources
- `results/*/README.md` (P1–P17, E1), `protocols/*.md`.
- `to_human/situation_report_2026-10-08.md`, `to_human/directions_2026-10-10.md`, `to_human/proposal_reframe_2026-10-11.md`, `to_human/results_2026-10-12.md`, `to_human/midterm_deck_outline.md`.
- `data_analysis/benchmark_el_report.md`, `data_analysis/ucf_el_report.md`.
- `~/mtp/MTP_session_handoff_2026-10-07.md` ("handoff 7 Oct").
- Phase 0 / phase 1 handoffs and the phase-1 answers: scratchpad `docsrc/phase0_phase1_handoffs.md` ("phase-1 §n").
- Session summaries 8–11 Oct: scratchpad `docsrc/session_summaries.md` ("session summary <UTC time>").
- Byte-identical stable copies of the scratchpad files: `sources/chat/phase0_phase1_handoffs_pasted_2026-10-11.md`, `sources/chat/claude_session_summaries_2026-10-07_to_11.md`, `sources/chat/user_messages_2026-10-07_to_11.md`.
- `scripts/ssl_rules.py` (the rule-1 code).
- Memory notes `~/.claude/projects/-home-yugma/memory/*.md`.

---

## Summary table

| ID | Problem | Status | Weight for conclusions |
|---|---|---|---|
| A1 | Tiny labelled set; rare classes in very few cells | open (structural) | high |
| A2 | Inactive lives in ~3 cells of test and val | mitigated (bootstrap, top-3, E1 cell IoU) | high |
| A3 | Test set is hand-picked, not representative | open (structural) | medium |
| A4 | Val and test disagree (inactive) | open | high for P16 |
| A5 | Crack labels are a convention (1–2 px ambiguity; old vs revised) | mitigated (revised labels, relF1@2) | high |
| A6 | Models collapse on unseen modules | open (measured limit) | high for deployment |
| A7 | External unlabelled pool is mismatched | open | medium |
| A8 | UCF-EL leakage and a different crack definition | open (re-split never done) | medium |
| A9 | One labelled split only | open | medium |
| A10 | Class-taxonomy quirks (absent classes, release classes 25–28) | mitigated | low |
| A11 | One very noisy test cell (`CSIR_00070_r8_c4`) can wreck a run's crack score | open (found after P16; post-hoc check only) | high for crack contrasts |
| A14 | E-SCDD scuff labelled crack in 6 train cells (649 px) and 2 test cells (236 px) by the P6 remap (added 30 Oct) | open (B3 decided; test-GT version a user decision) | medium for crack near scuff streaks and E1 |
| A15 | gaint `data/escdd_masks/test` differs from cv02 at 2 cells (added 30 Oct) | resolved for scoring (symlinks to `labeled/masks_escdd`) | low |
| B1–B14 | Past invalid or misread results | resolved (identified; kept out of P-series tables) | high for history |
| C1 | Rule 1 is lenient and per-metric | open (by design) | high |
| C2 | 3 seeds in most contrasts | partly mitigated (5 in P13/P16/P17 primaries and BsM5) | high |
| C3 | 5–10% regime | resolved for the Cs recipe (P16: no gain at 20/50/100%) | high |
| C4 | Joint-BN handicap in SSL arms (P8–P12) | resolved from P13 (separate forward) | high for P8–P12 |
| C5 | Untuned SSL recipe vs laddered supervised recipe | open | medium |
| C6 | CutMix for P16 picked on a val set with 6 inactive cells | open | medium |
| C7 | cv02 and gaint disagree | mitigated (within-machine rule) | medium |
| C8 | Many contrasts, no multiplicity correction | open | medium |
| C9 | AP saturation; metric changes across protocols | mitigated | medium |
| C10 | Post-hoc experiment choices | mitigated (disclosed) | low–medium |
| C11 | EMA-only effect unmeasured; bit-identity checked for 100 steps | mostly resolved (teacher = student at step 20,000, 13 Oct) | low |
| C12 | Seeds pooled across commits and protocols | mitigated (diff checks) | low |
| C13 | Effort concentrated on SSL | open | medium (strategic) |
| C14 | The 5% screen for pool-feature methods was chosen without checking the user's question (added 30 Oct) | resolved 30 Oct (moved to 100%) | high for MIM5/DDeP5/CP5 scope |
| C15 | The house optimizer was never varied, and it erases ResNet-34 encoder layer3/4 for both inits measured (added 30 Oct) | open (protocol_100 tests PF) | high for every init/pretraining/backbone null |
| D1–D19 | Infrastructure incidents | mostly resolved | low for results, one high (gaint reset) |
| D20–D27 | Infrastructure incidents, 29 to 30 Oct (added 30 Oct) | resolved; verdicts unaffected | low |
| E1–E16 | Open questions | open (E1, E2 answered) | see section (e) |
| E18–E22 | Open questions from 24 to 30 Oct (added 30 Oct) | open | see section (e) |
| A16 | Hanifi `_rf` half-cut (H36) crack labels are unusable; no labelled half-cut crack set exists outside E1 (added 1 Nov) | open (structural) | high for any half-cut claim or selector |
| A17 | E1 crack labels are about 1.5x wider than train (added 1 Nov) | mitigated (width-robust E1 metrics reported) | medium for E1 crack recall |
| C18 | The trainer evaluates the test split at the end of every run (added 1 Nov) | mitigated per protocol (data roots for A8, B6) | high for test hygiene |
| C19 | Multiplicity across E1 openings (added 1 Nov) | open (ledger, disclosure) | medium |
| D34–D45 | Infrastructure incidents and disclosures, 31 Oct to 1 Nov (added 1 Nov) | resolved or disclosed; verdicts unaffected | low |
| E26–E30 | Open questions from 31 Oct to 1 Nov (added 1 Nov) | open | see section (e) |

---

## (a) Data problems

### A1. Tiny labelled set; rare classes in very few labelled cells (open, structural)
- **What:**
  - BenchmarkEL `dataset_20211104` has 582 labelled cells: 478 train, 54 val, 50 test.
  - Label fractions are taken from the 478 train cells (the user once wrote "592 images"; the correct count is 582).
  - Crack is ~0.19% of train pixels.
- **Evidence:**

  | Labels | Labelled cells | Cells with inactive | Cells with crack | Source |
  |---|---|---|---|---|
  | 5% | 23 | 2 | 9 | `results/p10/README.md`, `labelled_set_counts.txt` |
  | 10% | 47 | 4 | 19 | `results/p10/README.md`, `labelled_set_counts.txt` |
  | 20% | 95 | 9 | – | `protocols/P16_label_fraction_curve.md` |
  | 50% | 239 | 20 | – | `protocols/P16_label_fraction_curve.md` |

  - Pixel shares: `data_analysis/benchmark_el_report.md`; handoff 7 Oct §3.1.
- **Impact:**
  - At 5–10% the model sees 2–4 inactive examples. Inactive results there say more about which cells were drawn than about the method.
  - Seed sd for inactive IoU reaches 0.14 at 5% (P12 Cm5 inactive 0.274±0.139), and 0.20 when one seed collapses (P10 B5 0.238±0.204).
- **Mitigation:**
  - P16 adds 20/50/100%.
  - The structural fix is more labelled cells. The full E-SCDD set was downloaded on 12 Oct: it has 20 inactive cells among 233 real cells new to us (doc 17; see E10).

### A2. Inactive pixels sit in ~3 cells of the test and val sets (mitigated)
- **What:** dataset-level inactive IoU and AP are decided by a handful of cells.
- **Evidence (revised labels):**

  | Split | Cells with inactive | Share held by the top 3 | Largest single cell |
  |---|---|---|---|
  | test | 16 of 50 | 59% | `BMRK_00073_cell0253`, 23% |
  | val | 6 of 54 | 89% | – |

  - For comparison, crack is in 48 of 50 test cells and the largest cell holds 12%.
  - On the old labels phase 1 counted inactive in 17 of 50 test cells (phase-1 §5).
  - Source: `results/p6/README.md` exploratory 4.
- **Impact:**
  - The P6 "inactive puzzle" (L1 10% beats L3 100% on inactive) flips sign without the top 3 cells, so it is not a finding.
  - Several later inactive "passes" are not robust over cells: P9 Cx − Dx, P11 Cm − A, P14 L3T − L3.
- **Mitigation:**
  - Every protocol from P9 on must report an image bootstrap (2,000 resamples) and leave-top-3-out.
  - E1 adds a per-cell inactive IoU, which proved more sensitive than the pooled one (`results/e1/README.md`).
  - Still needs more test cells; the 106-cell extension has only 10 cells with inactive.

### A3. The test set is hand-picked and not representative (open, structural)
- **What:**
  - All 50 test images contain crack (41–43% in train and val).
  - Inactive is over-represented in test.
  - 24 of 50 test images come from modules that also have train images.
  - Test cracks are darker and easier (test crack AP 0.46–0.49 vs 0.31–0.38 on val and unseen train).
- **Evidence:** handoff 7 Oct §3.1, §6.7; `to_human/situation_report_2026-10-08.md` §1.
- **Impact:**
  - Test scores flatter crack.
  - Module sharing means test is partly in-distribution.
  - The "label effect" on inactive seen on unseen train cells (0.34 → 0.46 from 10% to 20%) was invisible on test (handoff 7 Oct §6.7).
- **Mitigation:** E1's 106-cell extension from 67 unseen modules is a second view (A6). Cross-validated splits were proposed but never run.

### A4. Val and test disagree on inactive (open; matters for P16)
- **What:** on P13 the val set ranks the arms in the opposite order from test on inactive.
- **Evidence:**

  | | val inactive IoU | test inactive IoU |
  |---|---|---|
  | A5c (supervised) | 0.106 | 0.253 |
  | Cs5 | 0.098 | – |
  | CsM5 | 0.081 | 0.370 |
  | BsM5 | 0.061 | – |

  - Val has 6 inactive cells, and 3 of them hold 89% of the inactive pixels.
  - Source: `results/p13/README.md` Secondary.
  - Earlier: L3's inactive label-scaling gain was +0.000 on val without its top 3 cells but +0.112 on test (`results/p6/README.md` exploratory 5).
- **Impact:**
  - Any choice made on val that involves inactive is close to noise.
  - The P16 CutMix choice (C6) used val by the user's decision.
- **Mitigation:** none yet. Options are a larger val (pool val with held-out train cells) or selecting on crack-only metrics.

### A5. Crack labels are a convention, and they changed between versions (mitigated)
- **What:** a crack is about 3.4 µm wide physically; one pixel is about 300 µm (`to_human/directions_2026-10-10.md` §2, Haase 2018). The dark line seen is ~4 px of optical spread.
- **Evidence:**
  - **Labels:** median 1.75 px wide; within ±1 px of the darkest pixel only 48% of the time; dotted in 22 images (`data_analysis/benchmark_el_report.md`; situation report §1).
  - **One duplicate image with two independent masks:** crack IoU 0.257 between them (situation report §0).
  - **A perfect mask shifted by 1 px:** 0.47–0.56 IoU (situation report §2).
  - **Old (`20211104`) vs revised (E-SCDD):**
    - 34 of 50 test crack masks changed;
    - IoU 0.73–0.81 between versions, but 0.98 within 2 px;
    - re-scoring the same models raises crack IoU by +0.05 to +0.07 (`results/p3_label_versions/README.md`).
  - **Training on old vs revised labels (P14):** +0.082 crack IoU [+0.046, +0.129]. The revised-label model also wins when scored on the old labels (0.351 vs 0.332). An offset-tolerant supervised loss recovers 0% of that gap (`results/p14/README.md`).
- **Impact:**
  - Strict crack IoU partly measures label jitter. Differences of ±0.01–0.03 between methods are hard to interpret.
  - The label version is a bigger lever than any SSL effect measured.
- **Mitigation:**
  - From P6 on, all training and scoring use the revised masks.
  - Crack relaxed F1@2 is a primary metric.
  - Where the revised labels come from: for crack and inactive they are BenchmarkEL's own `20221008` corrections, which E-SCDD redistributes unchanged (audit 12 Oct, doc 17 §5.2). How those corrections were made is not documented. Wider revised labels flatter over-predicting models (P3 caveat).
  - P6's remap of scuff/star pixels put back 236 old crack pixels (0.26%) in 2 test cells. Negligible, but it is why our test counts 48 crack cells against E-SCDD's 46 (doc 17 §5.3).
  - [Qualified 30 Oct: in train the same remap labels 649 px of E-SCDD scuff as crack in 6 cells (plus 54 star px in 1 cell), including `ARTS_00051_r6_c2`, the only ARTS crack cell at 5%. Negligible for test, not for what the model learns about scuff streaks (A14; doc 17 §5.11).]
  - Inconsistency in sources: phase 1 quoted a crack label width of 2.0 px median, against 1.75 px measured here.

### A6. Models collapse on cells from unseen modules (open; a measured limit)
- **What:** on 106 BenchmarkEL release-`20221008` cells from 67 modules we never trained on, every model loses most of its crack performance.
- **Evidence:**
  - L3 100% crack IoU 0.471 (test) → 0.152 (extension).
  - Tolerant pseudo-labels raise crack false alarms there by about 0.10 of crack-free cells (P11 Cm − A ext +0.113 [+0.049, +0.186]; P12 gCm5 − A5 ext +0.104).
  - Separate BN removes most of that rise (P13 Cs5 − Cm5 false alarm −0.095 [−0.141, −0.050]).
  - Sources: `results/e1/README.md`; `results/p11/README.md`; `results/p12/README.md`; `results/p13/README.md`.
- **Impact:** in-distribution test scores overstate deployment performance. WattCycle's cells would be another unseen source.
- **Mitigation:**
  - None yet; it is reported as a limit.
  - The extension is 101 CSIR + 5 BMRK cells (32 with crack, 10 with inactive), so it measures transfer to one source mainly.
  - The proposal draft counted 117 extension cells (112 CSIR, 5 BMRK; 35 with crack). E1 dropped the 11 that are in the external pool, leaving 106.

### A7. The external unlabelled pool does not match the labelled data (open)
- **What:** 11,938 cells downloaded from the dataset's Dropbox link.
- **Evidence (handoff 7 Oct §3.3; `results/p10/README.md`):**
  - Only CSIR (9,204) and ARTS (2,734). 43% of labelled train cells are CFVS, BMRK or SDLE, with no counterpart in the pool.
  - 57% of the pool has about half the contrast of the labelled images.
  - ARTS pool cells are brighter (170 vs 134).
  - No harmonisation was applied.
  - 196 pool cells come from val modules and 88 from test modules (only exact cell matches were dropped).
  - External-pool tolerant PL hurts crack on its own sources: P10 Cx5 − Dx5 on CSIR+ARTS −0.065 [−0.092, −0.026], with the width check flagged (relP@2 −0.065).
  - Pool size alone gives no gain (P9: pool-size effect ≈ 0).
- **Impact:**
  - "External data does not help" cannot be separated from "this external data is the wrong data".
  - P16's Sx100 arm (100% labels plus the external pool) inherits this problem.
- **Mitigation:**
  - The source split is reported for every external-pool contrast.
  - Untested ideas:
    - re-walk the Dropbox listing (no downloads) to see whether other cell types exist (phase-1 answers item 5);
    - harmonise contrast;
    - match the pool to the target source.

### A8. UCF-EL: leaky split and a different crack definition (open)
- **What:**
  - The official UCF-EL code validates on test.
  - The split is by cell, not module: 25–44% of test cells have the same physical cell (another stress stage) in train.
  - UCF "crack" is a region class, roughly BenchmarkEL crack ∪ inactive, with a 1-px IoU ceiling of 0.95.
- **Evidence:**
  - `data_analysis/ucf_el_report.md`; situation report §9.
  - Jha's released split lists put 1,769 of the 2,289 public test images into training (handoff 7 Oct §3.4).
- **Impact:**
  - No label-efficiency claim on UCF-EL is defensible on the official split.
  - UCF's clean label gap (0.536 / 0.493 / 0.415 / 0.227 at 100/20/5/1%; handoff 7 Oct §6.9) cannot be used for SSL without a re-split.
- **Mitigation:**
  - All P-series SSL work moved to BenchmarkEL.
  - UCF-EL is used only as a pretraining source in P15, after a near-duplicate check against BenchmarkEL val/test (maximum correlation 0.79; `protocols/P15_ucf_encoder_transfer.md`).
- **Source conflict on UCF crack width:**
  - phase 1: 15.2 px median;
  - handoff 7 Oct: 9 px train / 7 px test at shorter side 295;
  - UCF report: by crack type (closed 3.5–5 px, resistive 21–24 px, isolated ~11 px).

  They use different measurements; quote with the definition.

### A9. One labelled split for everything (open)
- **What:** every run uses split seed 0. Splits 1 and 2 exist (`data/splits/seed1`, `seed2`) but were never used. The "seed" in a run name is the training seed only.
- **Evidence:** handoff 7 Oct §3.2, §8 item 3; every protocol's "Not claimed: other splits".
- **Impact:**
  - All conclusions are conditional on one draw of 23/47/95 cells.
  - At 5% the draw decides whether the model sees 2 or more inactive cells.
- **Mitigation:** none. Re-running key contrasts on splits 1 and 2 is the fix.

### A10. Class-taxonomy quirks (mitigated)
- **What:**
  - 24 classes, but 7 are absent from val and 8 from test, so "mIoU over 24 classes" covers different sets (handoff 7 Oct §3.1).
  - In the old recipe, absent classes got weight 0: at 2% labels, 12 classes were never taught (handoff 7 Oct §9.2).
  - Release `20221008` has classes 25–28 that our taxonomy lacks. E1 first mapped them to background and then ignored them (disclosed amendment, `results/e1/README.md`).
- **Mitigation:** from P6 on, the metrics are per-class (crack 14, inactive 11) and the loss is CE+Dice without class weights (L3).

### A11. One very noisy test cell can wreck a run's crack score (open; found after P16)
- **What:** test cell `CSIR_00070_r8_c4` is the noisiest of the 582 labelled cells. Its robust pixel-noise sigma is 46.0, against a median of 1.48 and a 95th percentile of 4.45 (`results/p16/cell_noise_rank.txt`). The only similar cell is `CSIR_00070_r7_c2` (43.0, train, same module). In some training seeds the model calls large parts of it crack.
- **Evidence** (`results/p16/README.md`, "One test cell"):
  - P16: 4 of 24 runs (S20 s2, S20 s4, A50 s2, A100 s3) put 39k–80k false-positive crack px on it (15–31% of the cell; true crack 787 px). Their pooled test crack IoU drops by 0.11–0.18 and relP@2 to 0.48–0.59. Val is normal. Sx100 s3 does it partly (8,093 px).
  - P6: `p6_L0_10pct_s1` (71,376 px). Its crack IoU is 0.261, or 0.360 without the cell. `p6_L0_10pct_s0` had a partial case (8,980 px). This outlier makes up most of P6's secondary "L1 − L0 crack IoU +0.048 [+0.003, +0.097]" (about +0.010 without it).
  - P7 to P15: no run above 4,600 px on this cell.
  - The failing models are confident (median p(crack) 0.92–0.99), the same in bf16 and fp32 (`results/p16/diag_csir70.txt`).
  - The failure is seed-dependent and hits supervised and SSL alike.
- **Impact:**
  - One cell can move a 5-seed crack mean by 0.039–0.046 and inflate its crack IoU sd 10–31×. That widens rule-1 thresholds until nothing passes, or could make a difference appear.
  - The usual robustness checks miss it. Leave-top-3-out drops cells by GT area, and this cell's damage is false positives.
  - E1's crack false-alarm metric skips it, because it has crack GT.
- **Mitigation:**
  - P16's README reports every contrast with and without the cell (post hoc, labelled as such). P16's verdict is the same both ways.
  - Earlier experiments other than P6 are essentially unaffected (≤ 4,600 px).
  - Whether to add "without this cell" as a standing check is open for the user (doc 15, decision 2b). Doing so after seeing P16 is a methodology change and must be disclosed.

### A12. Half of test crack is a confident miss, concentrated in faint and inactive-edge cracks (open; found 22 Oct, post hoc)
- **What** (`team_2026-10-21/skcdf/null_diagnosis.md` §2; ALHVR critic's pool probe `skcdf/probe_a2/`):
  - In every 5% arm, 42–57% of test GT crack px get p(crack) < 0.001.
  - About 34% of test crack (BsD5) and 37.8% of the unlabelled pool's crack are more than 2 px from any predicted crack ("true misses"), not offset.
  - Predicted/GT crack px on test is 0.59–0.74.
- **Where:**
  - faint cracks: relaxed recall 0.42 in the faintest third vs 0.80 in the darkest;
  - cracks on inactive-region edges, 12% of test crack px: recall 0.44 vs 0.69;
  - the ARTS and BMRK sources: 0.30 and 0.40 vs CFVS 0.80. The 5% labelled set holds only 47 ARTS crack px.
    [Qualified 30 Oct: those 47 px, in `ARTS_00051_r6_c2`, are E-SCDD scuff that P6's remap labelled crack. So the 5% set holds no real ARTS crack (A14; doc 17 §5.11).]
  - 40 components (5.4% of crack px) are missed by every arm.
- **Not fixed by SSL pseudo-labels.** Removing the confident-background PLs recovers only about 12% of true misses: BsDBn5 0.332 vs BsD5 0.378 on the pool probe, even though 70.5% of BsD5's true misses carry such a PL.
- **Not fixed by a prior shift** either: LA τ = 1 cuts that PL coverage to 46%, yet true misses stay at 0.359. SKCDF's balanced head does not fix them.
- **Next** (`skcdf/labelling_plan.md`):
  - a 1-hour human audit (real crack vs label artefact) of the 40 components;
  - label-convention questions for inactive-edge and faint cracks;
  - a retrospective label-budget test (needs approval).

---

### A13. ALHVR-style losses suppress inactive (post hoc reading; found 23 Oct, AL1, D7 pool)
- **What:**
  - In AL1, every arm with ALHVR's DTCT loss (AL5, ALd5, ALdh5) lowers test inactive IoU by 0.11–0.15 against supervised (rule 1 WORSE).
  - Inactive recall falls from 0.276 to 0.108–0.154 while precision stays about the same (0.77–0.83).
  - The same two-network pipeline with cross pseudo-labels (CPS5) raises recall to 0.400.
- **Reading (not tested by a one-change arm):** the sharpened-MSE plus entropy-minimisation targets on uncertain regions push minority-class pixels toward background.
  - In the ALHVR arms, 56–60% of unlabelled GT inactive sits in Ω1 (no loss) and only 10–17% in Ω3.
- **Impact:**
  - A warning for any confidence-routed or entropy-minimising SSL loss on rare EL classes.
  - No follow-up is proposed (`team_2026-10-21/alhvr/verify_a2.md`).

### A14. E-SCDD scuff is labelled crack in some train and test cells (open; found 30 Oct)
- **What:** P6 built `masks_escdd` by putting the old label back wherever E-SCDD says scuff (25) or star (28) (doc 17 §5.3). Where the old label was crack, scuff became crack.
- **Evidence (E, `team_2026-10-29_features/spec_b3_scuff.md` §1; doc 17 §5.11):**
  - Train: 12 cells carry scuff (3,246 px); our masks call 1,207 background, 1,390 material and **649 crack in 6 cells**.
  - The 5% "ARTS crack cell" `ARTS_00051_r6_c2` (47 px) is scuff labelled crack.
  - Test: 2 cells, 236 scuff px, all crack (`ARTS_00047_r3_c1`, `ARTS_00051_r3_c2`). Val: none. E1: scuff is in the ignore masks.
  - Star: `CFVS_00024_r3_c3` has 54 px of E-SCDD star labelled crack.
- **Impact:**
  - The 27 Oct statements that training "always ignored scuff" were wrong for train; only E1 scoring ignores it (doc 18 §U note).
  - (S) Crack labels on streaks may teach "streak = crack", the E1 failure mode (75% of E1 crack sits in half-cut + scuff cells, recall 0.126). Not tested.
  - It would have put scuff into the CP100 paste library as crack; caught before the CP smokes.
  - On test it is 0.26% of crack px.
- **Mitigation:**
  - CP100 excludes the 6 cells (13-stem list md5 903293c9).
  - The user decided (30 Oct 11:12) to train scuff as its own class (B3, `spec_b3_scuff.md`), after protocol_100.
  - Open user decision: keep test GT as is for the B3 verdict (coach's recommendation) or also report a version with the 236 px ignored (doc 15 §3b).
  - Never edit test masks without a separate decision.

### A15. gaint test masks differ from cv02 at 2 cells (resolved for scoring; found 29 Oct)
- **What:** gaint `data/escdd_masks/test` holds class 25 (scuff) at `ARTS_00047_r3_c1` (34 px) and `ARTS_00051_r3_c2` (202 px), where cv02's `escdd_masks` and `labeled/masks_escdd` hold crack (14). cv02's `escdd_masks` equals `labeled/masks_escdd` pixel for pixel.
- **Evidence:** `team_2026-10-29_features/log.md` 29 Oct 12:48 and 13:01; `SESSION_RECORD_2026-10-28_to_30.md` §2.
- **Impact:** a gaint score read from `data/escdd_masks` would differ from every cv02 P-series and Track M number on those 236 px.
- **Mitigation:** gaint `el_f1/data/escdd_masks` was replaced by per-stem symlinks to `labeled/masks_escdd` (val 54, test 50; pixel md5 8bcd3691 = cv02); `el_f2` and `el_f3` link to the same. All 29 to 30 Oct scoring uses `labeled/masks_escdd`. `coach_strategy.md` (B1 appendix) notes `el_m/data/escdd_masks` still holds class 25 for test.

### A16. Hanifi half-cut crack labels are unusable; no labelled half-cut crack set outside E1 (open, structural; added 1 Nov)
- **What:** the 36 Hanifi `_rf` half-cuts (H36) hold 1,792 crack px over 17 cells, median ~70 px per cell; 48% lie within 10 px of spacing, border or the cut line; 75% of `_rf` crack components are < 5 px (Pratt labels 4%). FINAL finds 1 of 17 (relR@2 0.036).
- **Evidence:** `team_2026-10-31_next/ideas/idea05_synthetic_halfcut.md` §1.6, `t9_prereg.md` judge review, `idea10_ai_labelling.md` §1 (`label_geometry.txt`); judge's ruling 31 Oct 14:23.
- **Impact:** no non-E1 set can choose a half-cut bias or validate a half-cut crack method. H36 is used for false alarms on its 19 crack-free cells only; F51 (51 unseen-module full cells) decides on `_rf`. R4's null (Track M) may partly reflect these labels (S). Half-cut routing is parked for this reason (doc 20 §3.1).
- **Resolution:** labelled half-cuts with E1-like context (B2 masks, or B3 + mining); cleaning H36 (~2 to 3 h, the user's call) would likely not show E1's offset (judge, S).

### A17. E1 crack labels are about 1.5x wider than train (mitigated; added 1 Nov)
- **What:** area / skeleton length: E1 3.66 px, train 2.41 (2·EDT median 4.0 vs 2.0); val 2.46 (judge recompute 1 Nov, log 21:01; train / val masks only).
- **Evidence:** `judge/crack_width.py` (md5 87f57a58); `protocol_PF2.md` §3b.
- **Impact:** pixel E1 crack recall is partly a width readout (a train-width prediction centred on every crack caps near 0.66), and E1 "faintness" over GT px is partly dilution by edge px.
- **Mitigation:** every protocol since PF2 reports width-robust E1 metrics (relR@2, relP@2, component recall / precision, predicted width); THIN-B3, HC and PF2E use E1 crack relF1@2 as the co-primary. [1 Nov ~21:40, THIN-B3: Skeleton Recall widens predictions ~1.5x (test pred/GT 0.95 → 1.54), so its E1 pixel recall (0.199 → 0.369) and crack IoU are inflated by this width match; judge quotes any-hit component recall (0.381 → 0.523) and relF1@2 instead.]

## (b) Past results that are invalid or were misread

None of these may be quoted as a method result. Old-era numbers stay in separate tables from the P-series (standing rule; memory `mtp-el-ssl-project.md`). History: `06_history_phase0_phase1.md`.

| ID | Result | Why it is invalid or misread | Source |
|---|---|---|---|
| B1 | Every Mean Teacher result with **SemiCE**: BenchmarkEL MT-20, UCF MT 1%/5% on cv02, the held gaint external-pool queue | SemiCE thresholds raw logits. 100% of unlabelled pixels have ≥ 2 "positive" classes (background on 98.9%, crack on 20.3% vs a true 0.19%). The target is incoherent | `results/p2/README.md` |
| B2 | "MT beats SL-20" (+0.023, p 0.095 test; +0.028, p 0.004 val+test) | MT with λ = 0 scores the same (paired −0.000 ± 0.024). The EMA adds nothing because the learning rate ends at 0 (teacher − student +0.000 ± 0.002) | handoff 7 Oct §6.1–6.2 |
| B3 | "ALHVR beats SL-20" (+0.029, p 0.045) and "ALHVR modules do nothing" | ALHVR equals its loss-off control (+0.005 ± 0.023). But its λ follows a sigmoid over the whole run and reaches 0.1 only at the last step, while our cosine learning rate reaches 0. So the loss was barely applied: neither a gain nor a null is shown. The measured prototype failure (cross-network prototypes 4.6% correct on Ω3 crack) still stands **Update 23 Oct (AL1, D7 pool):** a fair port, with full λ from step 4k and a loss-off control, is WORSE than supervised on all three primaries (doc 10 AL1); the dead-prototype cause is now known (1/8-resolution prototypes of two networks are orthogonal) | handoff 7 Oct §6.2, §6.8, §9.1 and `team_2026-10-21/alhvr/results.md` |
| B4 | An early SSL "+7.4" gain | 8× optimiser-step mismatch between SSL and SL | phase-0 doc |
| B5 | "SA SSL raised IoU" (the user's 11 Oct recollection) and best-val numbers | Best-val selection on 54 val cells flips comparison signs. SA-SL-20 seed 0 was 0.338 at the final step and 0.301 at the best-val step. Pooled over 4 seeds, SA shows no effect (0.3399 vs 0.3435) | phase-1 answers item 1; handoff 7 Oct §6.11; session summary 2026-10-11T09:36Z §5 |
| B6 | "Reproduction gaps" against papers | Metric-convention mismatches:<br>• Fioresi 57.3 is likely a 5-class mean incl. background;<br>• Pratt uses per-image medians with absent class = 0;<br>• PV-S3 drops background-GT pixels.<br>Under matched conventions Fioresi and Pratt reproduce | phase-1 §5, §7; situation report §4; `analysis/papers_metrics.md` |
| B7 | PV-S3 (Jha) headline numbers | The released code uses `ignore_index = 0` (background), so the model never predicts background: standard 4-class IoU 0.050 vs 0.828 on its own metric. Its splits put most public test images into training. Its supervised baseline is under-trained (30 epochs) | phase-1 §7c; handoff 7 Oct §6.10 |
| B8 | The old SA ablation ("removing SA helps", 0.2028 vs 0.1792) and the old SSL sweep (20%: 0.2580) | Predate the GaussNoise fix. albumentations 2.x ignored `var_limit`, giving sigma ~68 instead of ~4 (0–255), which erased cracks | phase-0 doc; phase-1 §8 item 1 |
| B9 | All "pilot" runs of 2 Oct | Coupled augmentation (flips always together, blur with noise) from a worker-seed bug | handoff 7 Oct §4.3; phase-1 §8 items 7–8 |
| B10 | Old class weights | Computed over train + val + test (a test leak); changed with the labelled subset, so fractions were compared at different operating points | phase-1 §4; handoff 7 Oct §6.3 |
| B11 | "Crack IoU 0.3 on its own 47 training images means a bug" | Not a bug (P1): masks are aligned exactly and bf16 = fp32. Augmentation (blur and ±5° rotation on 1.75 px labels) caps fitting (AP 0.93 → 0.59). CE+Dice fits to 0.861 | `results/p1/README.md` |
| B12 | "Labels don't help on BenchmarkEL" (SL-100 = SL-20) | Partly label noise in the evaluation masks: on revised labels 100% beats 10% on crack AP (P3). Partly the old recipe: L0 does not use extra labels, L3 does (P6) | `results/p3_label_versions/README.md`; `results/p6/README.md` |
| B13 | The old PV-S3 reimplementation "SSL 46.4" | Not reproduced by the rebuilt code (v1 0.200, v2 0.276/0.283). The collapse is corrosion pseudo-labels at 23× the labelled share | phase-1 §7b; handoff 7 Oct §6.10 |
| B14 | Batch-8 / BatchNorm conclusions from phase 1 | Machines disagreed (gaint 0.346, cv02 0.362 on SL-20-b8). Phase 1 first said batch size was ruled out, then took it back | handoff 7 Oct §6.3, §10 item 6 |

**Overclaims made and corrected during 8–11 Oct** (kept here so they are not repeated):
- **P6 rule 3 headroom.** An interim +0.026 (split mean) was reported, then corrected to −0.001 (pooled pixels) (`results/p6/README.md`).
- **P10 README.** It first said the source split changes nothing. It changes crack by −0.065 on CSIR+ARTS (session summary 2026-10-11T03:19Z §4).
- **"AP hides a gain".** P8 had already shown AP saturation confounds.
- **The "0.250 vs 0.310" BN gap.** It was cross-machine; within-machine it is −0.015 to −0.028.
- **The half-cut hypothesis for the extension.** Refuted: only 3 cells are > 5% half-cut (session summary 2026-10-11T09:36Z §4).
- **"Co-location is nearly free".** P7 slowed once P8's loss ramped (session summary 2026-10-10T15:56Z §4).
- **P2's own hypothesis.** "The offset absorbs the gradient" was refuted (offset share 0.041) (`results/p2/README.md`).

---

## (c) Weaknesses in our experimental design

### C1. Rule 1 is lenient, per-metric, and its strictness depends on seed count (open, by design)
- **What:** the locked rule is
  - Δ > max(0.01, 2·√((sd_A² + sd_B²)/3)) on **any** of three primaries (test crack IoU, inactive IoU, crack relF1@2);
  - with none of the three worse;
  - `scripts/ssl_rules.py`, function `cmp`.
- **Reading (arithmetic):**
  - **With 3 seeds per arm.** √((sd_A² + sd_B²)/3) is exactly the standard error of the difference of means, so the rule is "Δ > 2 SE". With 3 vs 3 seeds (t with about 4 degrees of freedom) that is a one-sided p of about 0.06. This is what Claude told the user on 11 Oct (session summary 2026-10-11T13:25Z §5).
  - **With 5 seeds per arm.** The divisor stays 3, so the threshold is 2·√(5/3) ≈ 2.6 SE. 5-seed contrasts (P13 primary, P16) are held to a **stricter** bar than 3-seed ones.
  - **Any of three metrics.** This raises the chance that at least one passes by luck, roughly up to 3× per contrast.
  - **The 0.01 floor.** Effects ≤ 0.01 never pass, however small the noise.
- **Impact:**
  - A single 3-seed "pass" is weak evidence on its own.
  - The rule ignores test-cell sampling; the bootstrap covers that (C2).
- **Mitigation:**
  - Every rule-2/3 contrast also gets the image bootstrap and leave-top-3-out (rule 7), and verdicts are read together with them.
  - P13's primary used 5 vs 5 seeds and passed, with CIs above 0 on both passing metrics.

### C2. Too few seeds for the effect sizes (partly mitigated)
- **What:** most contrasts use 3 seeds. The user's own standing rule asks for ≥ 5 seeds (5–8 in phase 1) for effects < 0.05. Nearly every SSL effect measured is < 0.05 on crack.
- **Evidence:**
  - L3-recipe arms without collapse (P6, P10, P12, P13, P14): crack sd 0.001–0.016, inactive sd 0.003–0.139;
  - P10's collapsed-seed arms B5/C5: crack sd 0.090–0.104, inactive 0.194–0.204;
  - the proposal's effect-size budget (`to_human/proposal_reframe_2026-10-11.md` §2).
- **Impact:** most 3-seed contrasts land inside their thresholds, and inactive sds of ~0.1 make inactive contrasts nearly untestable at 3 seeds.
- **Mitigation:**
  - P13 primary: 5 vs 5 (A5c pools P12 s0–2 and P13 s3–4).
  - P16: 5 vs 5 at every fraction.
  - P17: 5 vs 5; BsM5 raised to 5 seeds by P13 Amendment 2 (post hoc).
  - Still 3 seeds: Cs5 (P13 secondary), P14, P15.
- **A measured case of the risk:** BsM5's crack IoU sd was 0.004 on seeds 0–2 and 0.011 on 0–4. The 3-seed verdict "tolerant worse than hard on crack" (CsM5 − BsM5 −0.022, thr 0.014) became n.d. on 5 vs 5 (−0.015, thr 0.018) (`results/p17/README.md`).

### C3. The 5–10% label regime (mitigated by P16)
- **What:** P7–P13 tested SSL only at 5% and 10%.
- **Evidence:**
  - At 5–10% inactive appears in 2–4 labelled cells (A1), and the teacher is weakest.
  - Segmentation SSL benchmarks usually report 1/16 to 1/2 of the labels (`protocols/P16_label_fraction_curve.md` "Why this exists").
  - The user challenged it: "why we using 5 or 10% for ssl? they are really low".
- **Impact:** inactive was unmeasurable by construction in that regime, and "SSL fails" there may not generalise.
- **Mitigation:** P16 tested 20/50/100% (5 vs 5 seeds). With the Cs recipe SSL is n.d. against supervised at every fraction; the inactive gain shrinks from +0.105 (5%) to +0.029, +0.006, +0.003 (`results/p16/README.md`). Other recipes were not tested above 10%.

### C4. The joint-BN handicap in Mean Teacher arms (resolved from P13; affects P8–P12)
- **What:** the student forwarded labelled and unlabelled images in one batch, so BatchNorm statistics mixed them. In P8–P10 the labelled images also got the stronger SSL view.
- **Evidence:**

  | Experiment | Contrast | crack IoU | inactive IoU | Source |
  |---|---|---|---|---|
  | P8 (10%) | D − A | −0.013 [−0.028, −0.001] | −0.101 [−0.171, −0.031] | `results/p8/README.md` |
  | P11 (10%, matched view) | Dm − A | −0.007 [−0.016, −0.001] | – | `results/p11/README.md` |
  | P12 (5%, matched view) | Dm5 − A5c | −0.017 [−0.024, −0.010] | – | `results/p12/README.md` |

  - P12's contrast is n.d. by the seed rule but robust over cells.
  - Swapping only the pool, with the loss off, moved the control: P9 Dx − D inactive +0.094.
  - **Caution:** the often-quoted "−0.055 at 5%" (P10 D5 − A5) is **cross-machine** (D5 on cv02, A5 on gaint) and includes the labelled-view handicap, so it is not a clean measure.
- **Impact:**
  - In P8–P12 the "loss-off control" was itself handicapped.
  - "Loss helps" (rule 2) partly measured recovery of the handicap. P13 showed tolerant PL alone adds about 0 crack against a clean control (Cs5 − A5c +0.004), so P12's Cm5 − Dm5 crack gain (+0.023) mostly offset the 0.017 handicap (`results/p13/README.md` Reading).
- **Mitigation:** P13 onward uses `ssl.student_forward=separate`. With λ = 0 the student is bit-identical to supervised, so A is the exact loss-off control.

### C5. Untuned SSL recipe against a laddered supervised recipe (open)
- **What:**
  - The supervised base (L3) came out of a four-step recipe ladder (P6).
  - The SSL hyperparameters were never tuned: λ_final 1.0, t_pos 0.95, R = 2 px, warm-up 2,000 + ramp 2,000, EMA 0.999, CutMix p 0.5.
  - Every SSL protocol lists "Not claimed: tuning of R, t_pos, λ".
- **Impact:** a null or small SSL effect may be a recipe problem, not a method limit. Claude named this as one of the five self-inflicted handicaps (session summary 2026-10-11T13:25Z §5).
- **Mitigation:** none yet. Tuning would need a protocol and val-based selection, and val is weak for inactive (A4).

### C6. P16's CutMix setting was picked on a val set with 6 inactive cells (open)
- **What:** by the user's choice ("Pick on P13 val"), P16's SSL recipe used CutMix only if P13 val favoured it.
- **Evidence:**
  - Val scores: CsM5 0.3507, Cs5 0.3652, so CutMix is off (`el_p16/reports/p16b/selection.txt` on cv02; `results/p13/README.md`).
  - On test, CsM5 − Cs5 is n.d. on seeds but positive over cells on crack (+0.010 [+0.004, +0.017]).
  - Hard PL + CutMix (BsM5) was best on crack (+0.036 vs A5c on 3 seeds; +0.029 on 5). Tolerant was worse than hard under CutMix on 3 BsM5 seeds (−0.022); on 5 vs 5 it is n.d. by seeds, still negative over cells.
  - So P16 runs the recipe that was weakest on crack in P13's test.
- **Impact:** P16's SSL arms may understate what SSL can do at 20–100%. P16 answers "does *this* recipe help with more labels". Its answer was no at every fraction (12 Oct).
- **Mitigation:**
  - Kept as locked; choosing on test would contaminate P16.
  - A BsM-style arm at 20%/50% would be a test-informed, exploratory addition, and needs the user's go-ahead (`12_decisions_log.md` D32).

### C7. cv02 and gaint disagree (mitigated by the within-machine rule)
- **What:** the two machines (RTX A6000 vs RTX PRO 4500) give different numbers for the same configuration.
- **Evidence:**
  - **P12:** on cv02 Cm5 − A5c fails (+0.006 crack). On gaint gCm5 − A5 passes the arithmetic (crack +0.029, inactive +0.068, relF1@2 +0.058).
  - **Calibration gA10 − cv02 L3 10%:** crack +0.004 (agree), inactive +0.056 (threshold 0.057).
  - **Phase 1:** SL-20-b8 0.346 (gaint) vs 0.362 (cv02).
  - Sources: `results/p12/README.md`; handoff 7 Oct §6.3.
- **Impact:** with 3 seeds each, the machines can tell different stories, so a positive result on one machine is not robust.
- **Mitigation:**
  - Arms are never compared across machines.
  - gaint replications are descriptive and "never rescue a failed cv02 rule".
  - Calibration runs when crossing (P12 rule 7).

### C8. Many contrasts, no multiplicity correction (open)
- **What:**
  - P12 reports 9 rule pairs.
  - P13 has 1 primary and 5 secondary contrasts.
  - E1 scored 23 contrasts.
  - Each contrast checks three metrics.
  - Phase 1 ran 38 tests of which only one survives Bonferroni (handoff 7 Oct §9.2).
- **Impact:** some passes will be false positives.
- **Mitigation:**
  - Each protocol names one primary claim; the count of contrasts is disclosed (P13 README).
  - No formal correction is applied.

### C9. AP saturation, and metric changes between protocols (mitigated)
- **What:** with an ImageNet encoder and CE+Dice, many ground-truth pixels score < 0.001 (bin 0 of 1,000). There they tie with ≥ 98.5% of background, so AP cannot rank them.
- **Evidence:**
  - L3 10%: 42% of GT crack and 65% of GT inactive in bin 0.
  - L0: 3% / 19%.
  - Source: `results/p6/README.md` exploratory 1.
- **Impact:**
  - P6's rule-1 "hurts" for L2/L3 is partly a calibration effect.
  - AP is not comparable across loss or encoder changes.
  - The primary metrics changed from AP (P6, P7) to IoU/IoU/relF1@2 (P8 onward). The change was locked before P8 ran, but P6/P7 verdicts are on a different metric.
- **Mitigation:** AP is secondary and always reported with the bin-0 share.

### C10. Experiments chosen after seeing interim results (mitigated by disclosure)
- **What:**
  - P8 (base switched to L3 after P6);
  - P9 and P10 (chosen after interim P7/P8 nulls);
  - P11 (after P8's D < A);
  - P12 (after seeing gaint A5);
  - P16 (after P11–P12);
  - P13 Amendment 2 (BsM5 seeds 3–4, added after seeing the 3-seed result, with a fixed 5-seed stopping rule);
  - P17 (after P13; prompted by the user's question about two papers).
- **Impact:** the sequence is adaptive. Each protocol still fixes its rules before its own runs, and the motivation applies equally to all arms of that protocol.
- **Mitigation:** each protocol has a "What I had seen" or "post hoc; disclosed" section.

### C11. The EMA-only effect is unmeasured; bit-identity checked for 100 steps (mostly resolved 13 Oct)
- **What:**
  - In P13/P16, A (supervised) is the loss-off control. But SSL arms are scored on the EMA teacher, while A has no EMA.
  - Ds5 (separate forward, λ = 0, teacher evaluated) was dropped in Amendment 1.
  - The bit-identity of the λ = 0 student and supervised training was verified on GPU for 100 steps (`results/p13_audit/smoke_gpu.log`).
- **Evidence that the EMA effect is small:**
  - phase 1: teacher − student +0.000 ± 0.002 with cosine LR to 0;
  - P8: student = teacher (crack 0.383 vs 0.383).
- **Impact:** CsM5 − A5c contains the loss effect, CutMix and any EMA effect. Probably negligible, but not measured in P13. The same holds for P17's BsD5 − A5c: the gain that reaches the teacher without the decoder fitting pseudo-labels comes through the encoder or the EMA.
- **13 Oct check** (`results/ema_check/README.md`, descriptive): at step 20,000 the EMA teacher and the student of BsM5, CsM5 and BsD5 (15 runs) score the same, within ±0.005 on every metric (mean about −0.001). The cosine schedule ends at learning rate 0, so the EMA catches up with the student. A λ = 0 run's teacher would therefore match its student, which is bit-identical to A. The EMA-only effect is very likely about 0 (inferred, not measured on Ds5).
- **Mitigation:** run Ds5 at 3–5 seeds if a reviewer needs a direct measurement.

### C12. Seeds pooled across commits and protocols (mitigated)
- **What:**
  - **A5c** = P12 `p12_A_5pct` s0–2 (commit `24590fb`) + P13 `p13_A_5pct` s3–4 (`bac5264`).
  - **P16 A20 and A100** pool P6 s0–2 (`824fab0`) with new s3–4 (`bac5264`).
- **Evidence:**
  - Code diffs show the supervised path unchanged; configs differ only in seed and fraction.
  - The P12 vs P13 halves agree (n.d. on all primaries; `results/p13/README.md`).
- **Impact:** small, but a reviewer may ask.

### C13. Effort concentrated on SSL after the evidence pointed elsewhere (open, strategic)
- **What:** the effect-size budget ranks the levers as: label version and supervised recipe ≫ label quantity ≫ unlabelled loss.
- **Evidence:**
  - Five SSL protocols (P8–P13) ran before any of the three directions rated strong and cheap: tolerance-aware supervision, pretraining without pseudo-labels, cross-dataset transfer.
  - Source: `to_human/proposal_reframe_2026-10-11.md` §2, which calls this allocation "the main thing to correct".
- **Mitigation:**
  - P14 (tolerant supervision) and P15 (UCF encoder transfer) were added on 11 Oct.
  - MIM pretraining and distillation are still untested.
  - [Qualified 30 Oct: MIM was run on 29 to 30 Oct as MIM5 (5% labels, house fine-tune): n.d., every estimate negative (`team_2026-10-29_features/verify_mim5.md`). Under the house optimizer the MIM features in layer2 to layer4 were erased (C15), so MIM under an encoder-preserving fine-tune is still untested; protocol_100's MIM100-PF arm tests it at 100% (doc 19). Distillation is still untested.]

### C14. The 5% screen for pool-feature methods was chosen without checking the user's question (resolved 30 Oct; added 30 Oct)
- **What:** on 28 Oct the user asked whether feature learning from the ~11.7k unlabelled cells improves the model trained on **all** labels. MIM5, DDeP5 and CP5 were all run at 5% labels. The 5% choice was copied from the 27 Oct synthesis (doc 18 §U, item 3) without checking it against the question.
- **Evidence:** `SESSION_RECORD_2026-10-28_to_30.md` §0 and §5; the user, 30 Oct ~10:45: "why 5%? I asked about adding the pool to 100% labels."
- **Impact:**
  - The overnight gaint runs of 29 to 30 Oct (MIM5, DDeP5, CP5) answered a 5% question the user had not asked.
  - The 5% nulls carry to 100% only for methods that do not consume labels and only when the 5% estimate is tight (doc 19 §5). They do not carry for copy-paste, and not for MIM once the optimizer is changed (C15). CP5 was stopped unscored.
  - 100% is better powered than 5%: clean MDE crack 0.012 vs 0.019, inactive 0.032 vs 0.084 (`diag_5pct_to_100pct.md` §2).
- **Mitigation:** CP5 stopped (10:50 IST 30 Oct); protocol_100 at 100% labels. Feedback memory saved: pool ideas are tested on top of 100% labels unless the user asks otherwise. Coach's rule: test a method at the label fraction where its mechanism lives (`coach_strategy.md` §3).

### C15. The house optimizer was never varied, and it erases the deep encoder (open; added 30 Oct)
- **What:** the house fine-tune (Adam lr 1e-3, coupled L2 weight decay 1e-4, 200-step warmup and cosine, 20k steps, batch 8) ends ResNet-34 U-Net++ encoder layer3/4 at cosine about 0 to their init, for both inits tried (ImageNet, MIM), at 5% and at 100% labels.
- **Evidence (E, `team_2026-10-29_features/coach_100.md` §0; re-derived by runner in `protocol_100.md`):** cosine final vs init, layer3 0.005 to 0.018, layer4 −0.001 to 0.001 (A5c-f1, MIM5, SUP100); layer3/4 norms end at 2 to 9% of init; two SUP100 seeds agree at layer4 only at cosine 0.007. Full table: doc 19 §4.
- **It is early (E, `protocol_100.md` v1.1 gate table):** in the house-recipe smoke at 100%, layer3/4 are at cosine 0.070 / 0.003 at step 2,000, with norms still 0.33 / 0.21. The direction is lost during warmup and the peak lr, before the norm collapse; not a slow drift.
- **Impact:**
  - Every "init / pretraining / backbone does not help" result was obtained under this recipe: P15 (claim 7), MIM5, DDeP5, Track M R3 (ResNet-50; EfficientNet-B4 and ConvNeXt-T pilots).
  - Measured vs inferred: erasure was measured only on ResNet-34 U-Net++ runs (A5c-f1, MIM5, SUP100). That P15's UCF-EL encoder and the R3 encoders were erased too is likely but not measured (S). For ConvNeXt (LayerNorm, not BatchNorm) the mechanism is not established.
  - The frozen-probe signal for ResNet-50 / ConvNeXt on BMRK crack (doc 18 §D1) was never tested under a fine-tune that keeps those features.
  - Mechanism (S): BN-followed convs are scale-invariant, so the direction turns freely early on; coupled L2 then shrinks the norms.
- **Mitigation:** protocol_100's SUP100-PF and MIM100-PF arms (encoder-preserving fine-tune), with gate G5 (layer3/4 cosine ≥ 0.8 at 4k steps). G5 passed: 0.975 / 0.985 (SUP100-PF) and 0.986 / 0.990 (MIM100-PF) at 4k (smokes, training only). protocol_100 launched 30 Oct 12:05 IST; no result yet. Coach's proposed house rule: report the per-stage encoder cosine to init with every init or pretraining result (`coach_strategy.md` §3).
- [Qualified 31 Oct] protocol_100 reproduced the erasure on 5 fresh SUP100-g seeds; PF kept layer3/4 at 0.93 to 0.96 at 20k and changed nothing on test (`verify_100_o1.md`). Erasure does not explain the pool and recipe nulls at 100%.

### C16. A decoy gate read early can miss a late shortcut (open; added 31 Oct)
- **What:** gate 6b judged CP100's seam sensitivity at 4k from a falling trend (0.0076 → 0.0039 from 2k to 4k). At 20k the decoy rate was 0.0125, 4.41x SUP100-g's (FLAG; `verify_100_o2.md` §3).
- **Impact:** none on a verdict (CP100 n.d.). A positive CP result would have carried the caveat. CP also doubled false crack on crack-free val cells (178 → 389 px).
- **Mitigation:** read the end-of-training trend (E3b) as part of any decoy go/no-go where compute allows (coach, `review_100_v1.md`).

### C17. E1 has been read many times (open; added 31 Oct)
- **What:** E1 (106 cells) is the only sealed unseen-module set, and every protocol reports it. PF's E1 gain is the largest yet (crack recall 0.169 → 0.213, inactive IoU 0.041 → 0.245) but was not a pre-registered primary. Its crack-recall gain sits in the 29 scuff + half-cut cells (0.094 → 0.152; the other 77 lose crack IoU 0.261 → 0.238); the inactive gain is in both groups (0.088 → 0.566 and 0.028 → 0.104).
- **Impact:** a PF E1 claim needs new seeds with E1 co-primaries stated before the runs, or an independent unseen-module set. Training on the "Pratt extras" would use E1 up (vetter finding 1).
- **Status:** open; the user's call (vetter §6 Q1). [Qualified 1 Nov: the user made E1 a second test set (31 Oct ~15:00): pre-registered co-primaries, one read per opening, never for selection; ledger `team_2026-10-31_next/e1_openings.md`. PF2 replicated the inactive gain on new seeds (doc 11 row 30); cell selection is still not controlled (same E1 cells).]

### C18. The trainer evaluates the test split at the end of every run (mitigated per protocol; added 1 Nov)
- **What:** `trainer.py` l.857-880 (e544133, and el_f8) runs a TEST pass after the final step (and on `best.pth`) and prints it to the stdout and the results payload; no option turns it off (`train.py` always builds the test loader).
- **Impact:** every training run computes test numbers before its protocol's opening. Reading a stdout's tail shows them (D40). For protocols that must read no test cell (A8 screen, B6) a run would compute them anyway.
- **Mitigation:** never tail a stdout (doc 12 D76); for A8 and B6 a per-run `data.root` whose `splits/test.txt` is the held-out list (A8: a copy of val.txt; B6: the held-out fold), checked by md5 and a CPU data-build line (doc 12 D74). No code change. The verdict files never use the trainer's TEST block.

### C19. Multiplicity across E1 openings (open; added 1 Nov)
- **What:** four registered E1 openings by 1 Nov (PF2, THIN-B3, HC armed, PF2E), each with uncorrected co-primaries (PF2 5, THIN SKR / CLD 6, B3 4, HC 5, PF2E 5). PF2E repeats PF2's members and cells.
- **Impact:** a single E1 pass is weaker than it looks: PF2E's E1 inactive pass is borderline under Bonferroni (99% LB ≈ 0.000).
- **Mitigation:** `e1_openings.md` lists every opening and the pre-policy reads; comparator files are reused, not re-read; a pre-declared no-op readout is dropped rather than read (routing, doc 20 §3.1). The paper reports every opening.

---

## (d) Infrastructure incidents

| ID | Incident | Effect | Fix or status | Source |
|---|---|---|---|---|
| D1 | gaint `noob` account reset (before 2 Oct) | Phase-0 code, reproduction code, the UCF val split, Subpath A post-processing (57 tests), splits and predictions lost. Only notes and the poster survive | Repo rebuilt as `el-fault-detection`; rule "push after every step". **Severity post-processing is still lost** | phase-0 doc; phase-1 §0, §17; handoff 7 Oct §1 |
| D2 | gaint instability: OS shutdown 2 Oct 21:34 (killed the ALHVR pilot at step 13,600); reboots 6 Oct ~18:22 and 7 Oct ~10:30 | Lost runs; hardware clock in IST read as UTC | Resume from `latest.pth` after reboot (commit `95dda7c`). Who shut it down is unknown (needs sudo) | handoff 7 Oct §2.1 |
| D3 | cv02 is shared (~186 users); `/tmp/noob_el` is wiped on reboot; home is 100% full | Speed varies about 2×; checkpoints at risk | Small results synced; never write large files under `~`; never start on a GPU where another user holds > 4 GB. Since 13 Oct, run dirs and checkpoints are copied to gaint `cv02_noob_el` (manifest + MD5). The `cv02` login is shared by many lab members, so no ssh agent forwarding and no keys there; copies are relayed through the user's laptop | phase-1 §3; handoff 7 Oct §2.2; memory `cv02-shared-account-backup.md` |
| D4 | GPU queue race (10 Oct): two queues polling "GPU free" | The main queue would have waited ~6 h | Claude killed both of its queue loops and relaunched one; rule: chain queues, one per machine | session summary 2026-10-10T19:37Z §4; memory |
| D5 | `tmux has-session -t p13` matched `p13smoke` | Nothing launched | Use `-t "=name"` | memory `server-runs-tmux-parallel.md` |
| D6 | Watcher bugs: grep exit code 1 read as failure; ssh timeouts (network blip); `grep -c` on missing files shifted fields | False alarms or missed events | Robust local polling loop; `cat file \| grep -c` form; `; true` endings | session summaries 2026-10-10T19:37Z, 2026-10-11T03:19Z, 2026-10-11T13:25Z |
| D7 | `train.py` refused SSL at `labeled_fraction` 1.0 (no in-domain pool left) | Blocked P16's Sx100 | Patch `d51b60f`: allowed only with `data.unlabeled_pool=external`; 3 tests | session summary 2026-10-11T13:25Z §4 |
| D8 | Auto-mode classifier denials: killing the gaint queue and editing crontab (8 Oct); an auto-start waiter for P8 (10 Oct); preparing the P9 launcher before approval | Actions blocked | Not worked around. The user ran the hold themselves; Claude asked before launching | session summaries 2026-10-08T07:54Z, 2026-10-10T15:56Z, 2026-10-10T19:37Z |
| D9 | `git archive` with a missing `pyproject.toml` gave an empty tarball; printed log lines corrupted tar streams; an extracted `data/` made `data/data` symlinks | Broken deployments, caught before runs | Explicit file lists; strip the first line; `rm -rf data && ln -s` | session summaries 2026-10-10T19:37Z, 2026-10-11T09:36Z |
| D10 | `frozen_bn_stats` used `copy_` and broke autograd | P13 code error, caught in tests | Rebind the BN buffers instead | session summary 2026-10-11T09:36Z §4 |
| D11 | UNet++ cannot evaluate UCF-EL's variable image sizes | P15 pretraining blocked | Pretrained DeepLabV3+ ResNet-34 instead (same 216 encoder tensors) | `protocols/P15_ucf_encoder_transfer.md` |
| D12 | scikit-image missing on cv02 (no sudo) | E1 scorer blocked | `pip --target /tmp/noob_el/diag/pylib` | session summary 2026-10-11T09:36Z §4 |
| D13 | P1 arm D (fp32) ran out of memory next to arm C | One arm delayed | Rerun alone; failed log kept | `results/p1/README.md` |
| D14 | `pkill` / `pgrep -f` matched Claude's own ssh shell; a `cd dir && cmd &` backgrounded the `cd` | Hangs | Avoid self-matching patterns; `cd dir; (cmd &)` | session summary 2026-10-10T09:17Z §4 |
| D15 | P12 script flagged a width check against A5c; the protocol's check is against Dm | Wrong flag | Disclosed in the P12 README (−0.044 vs Dm, OK) | session summary 2026-10-11T13:25Z §4 |
| D16 | `post_ssl.sh p10` counted 18 JSONs instead of 15 (gaint references in the same dir) | Script abort | Exclude `/p10_A_` in the count | session summary 2026-10-11T03:19Z §4 |
| D17 | Several protocol and README headers give times that disagree with git: P14/P15 say ~13:45, commit at 12:55; P16 says prompt ~16:35, lock ~16:50, while the transcript has the prompt at 17:24 and git the lock at 17:28; P10 says ~23:05, commit at 22:56 and first run at 22:57; P1/P2 say 8 Oct 00:15, commit at 7 Oct 23:59; the E1 README says ~14:00 and ~14:15, commits at 12:59 and 13:16 | Cosmetic; the order of events is the same, and every lock commit precedes its runs | Use git and transcript times (`12_decisions_log.md`, `09_`, `10_`) | git log; `protocols/P1*`, `P2*`, `P10*`, `P14*`, `P15*`, `P16*`; `results/e1/README.md` |
| D19 | A Claude Code session drop (13 Oct, ~08:00 IST) killed a background laptop-relay copy part-way (BsM5 s3 half copied, s4 missing on gaint) and left two background waiters stopped | A partial backup that looked done from its log start | Redone 16:28–16:33 IST and verified by MD5 of every file; check that a relay finished before trusting it | `15_status_remaining_work.md` §1c |
| D18 | A third-party app credential was pasted in chat on 2 Oct | Security hygiene | Should be rotated; not confirmed done (handoff 7 Oct §2.4). Never copy it anywhere | handoff 7 Oct §2.4; standing constraint |
| D20 | **The `rc=$?` after `$(date)` bug recurred on 29 to 30 Oct** (added 30 Oct), despite the 21 Oct note (doc 14 §3.1, commit 16128f7). Five status lines recorded date's exit code: MIM pretrain, MIM5 post, DDeP5 post, cv02 DDeP, and the f100 smoke status lines. The first G5 extender required rc=3 and would have skipped | No verdict affected. Training-run rc lines (`run_one.sh`, all versions) and `f2_postC` were correct. Each affected run was confirmed complete by its DONE line, md5 manifests and 0 Tracebacks; coach's watchers required POST DONE + manifest, not the rc line | Smoke lines and the staged f100 queue fixed (rc captured before `date`; md5 60499c90); G5 extender restarted with a stdout check; f100 opening triggers use rc captured before `date`. Lesson: a note in the handbook did not stop a new script from repeating the bug | `SESSION_RECORD_2026-10-28_to_30.md` §9; `team_2026-10-29_features/log.md` 30 Oct 11:16, 11:20, 11:21 |
| D21 | Relative log path (added 30 Oct): `f1_after_runs_gaint.sh` wrote its 'AM rc' and 'AFTER-RUNS DONE' lines to a relative path after a `cd`, so the f2 gate would never have opened | The DDeP5/CP5 release line never appeared | runner wrote the end line by hand at 02:36 IST 30 Oct (AM output verified complete: `am.log` 11 lines, 0 Tracebacks; `am_val.json` in the manifest); v2 uses an absolute path (md5 bf7692fd); other lane scripts checked | `log.md` 30 Oct 02:36, 02:50; `verify_mim5.md` §6 |
| D22 | Simultaneous-start memory race on gaint (added 30 Oct): at 02:36 IST three f2 runs (CP5 s1, DDeP5 s1, DDeP5 s0) started on one free-memory reading, because new allocations were not yet visible | Free memory 2,234 MiB, close to the 2 GB floor kept for root's `finllm_chat.py` | A 5 s memory watch over vals and checkpoints (182 samples, 02:45 to 03:00) showed a constant minimum of 2,232 MiB, so the runs were kept. Starts now take a flock check-and-stamp gate and are spaced ≥ 120 s apart (f2g `run_one.sh` v3, md5 8453c0e5; v4, md5 176ea9c9, also gates end-of-run rescoring); the CP start gate was set from the measured peak (9,526 + 2,048 = 11,600 MiB, v5). Earlier, free memory fell to 308 MiB at 13:30 on 29 Oct (log; the session record says 0.8 GB headroom "at one point"), which led to the ≥ 2 GB rule | `log.md` 29 Oct 13:31, 30 Oct 02:37, 03:01, 05:46; session record §9 |
| D23 | Log timestamps ahead of the clock (added 30 Oct): runner stamped some lines up to 11 min (29 Oct) and up to 38 min (30 Oct) ahead; coach up to about 75 min (a 12:20 stamp written at 11:06; coach's own figure; the session record says "up to ~1 h") | A reader could misorder events | Corrected from git, file and log stamps. Coach re-stamped its 09:45 to 12:20 lines, marked estimates with "~" and kept a pre-edit copy. Rule: stamps come from `date`, never estimates | `log.md` 29 Oct 13:28; 30 Oct 11:05, 11:08 |
| D24 | cv02 gate-parse bug (added 30 Oct): a good DDeP smoke was marked FAIL because the grep also matched the STOPPED line | GPU 1 was lost to another user; the full DDeP run waited until GPU 0 freed at 19:43 IST | Fixed (v2, md5 1f2016e6); smoke reused; queue re-armed | `log.md` 29 Oct 16:26, 19:47 |
| D25 | Shared HOLD file (added 30 Oct): a HOLD meant to pause the A lane also blocked the MIM5 lanes, since all lanes call `run_one.sh` | Delayed MIM5 starts | Replaced by an A-lane-only `HOLD_A` (`run_one.sh` md5 6f6fe611), 29 Oct 18:39 | `log.md` 29 Oct 18:39 |
| D26 | Laptop reboot (added 30 Oct), 29 Oct ~20:16 IST, killed the local teammates and their watchers | Server tmux unaffected | runner and coach respawned (scout no longer needed); watchers re-armed | session record §1, §9; `log.md` 29 Oct 20:22 |
| D27 | Critical-path slip (added 30 Oct): the A lane ran its seeds serially | The last 5% run would have ended about 05:00 | Rebalanced with an extra window and atomic per-run claim dirs (f1g `run_one.sh` v3, md5 969f7676); last run 02:21 | session record §9; `log.md` 29 Oct 20:25 |
| D28 | Opening-1 scoring memory (added 31 Oct): the 6,000 MiB scoring gate assumed a ~3 GB pass. Measured peaks (opening 2, finllm alone): rescore 4,398, m0 4,002, LA 5,106 MiB. With CP s0/s1 running (6,609 to 6,612 MiB free), the LA pass (01:27:47 to 01:33:19 31 Oct) likely left about 1.5 GB free | An estimated breach of the 2 GB finllm floor for about 5.5 min. finllm (PID 6206) survived; no out-of-memory error. runner's first answer ("~2.2 to 2.6 GB") missed the LA pass | 10 s free-memory log during overlaps (`gpumem.log`; CP overlap minimum 6,609 MiB); concurrent gate = measured peak + 2,048 MiB (7,154 for scoring); disclosed in `protocol_100.md` | `log.md` 31 Oct 01:43, 07:11; `protocol_100.md` |
| D29 | Crossed approvals (added 31 Oct): CP s1 stop approved by coach, declined by team-lead (user's rule); B2 v2 sheets sent seconds before coach's formal OK (team-lead's account; no team file records the send time); coach's final B2 v2 rule crossed runner's first v2 launch; B2 v2 and D restarted after the reboot before coach's "wait" message; runner gave team-lead the R34-10 reading before coach's verify | No run stopped, no number changed; each disclosed | Act on a formal OK only; when messages cross, disclose and offer to undo | session record 30 to 31 Oct §10 |
| D30 | Duplicate watchers from a bare `&` (added 31 Oct): runner twice started an untracked duplicate watcher | Double wakes; risk of acting twice | Each stopped by exact PID after printing its command (PID 1355033 the second time); watchers now only as tracked jobs with the PID logged | `log.md` 31 Oct 01:04 |
| D31 | gaint reboot, 30 Oct 16:28 (added 31 Oct): orderly shutdown, cause unknown (a console login at 16:29) | Wave-2 runs stopped at checkpoints 16k / 12k / 12k; B2 v2 and D stopped | Resumed from `latest.pth`, overlap bit-identical, runs count (v1.2). Who rebooted it is a question for the user | `protocol_100.md` v1.2 |
| D32 | awk slip (added 31 Oct): the first resume identity check read the wrong field and selected 0 lines | A false "DIFFER or incomplete" | Fixed and re-run before any decision; disclosed in v1.2 | `protocol_100.md` v1.2 |
| D33 | poolscout's venv and `pkill` (added 31 Oct): a pip install into a throwaway venv completed (first reported as aborted); its `pkill -f` on the laptop matched only its own shell (poolscout's report to team-lead) | Traffic about 0.51 GB, over the 0.5 GB cap if tooling counts; nothing else changed | venv deleted unused; the PID-only rule now covers the laptop | `pool_large/pool_large_audit_2026-10-30.md` §5 |
| D34 | builder's GPU context (added 1 Nov): pytest on gaint without `CUDA_VISIBLE_DEVICES=""` (31 Oct ~14:12 to 14:15, 14:32) | 254 MiB on the GPU beside finllm (margin then 7.2 GB); finllm unaffected | Every gaint command: CUDA hidden, nice 19, ≤ 8 threads; GPU smokes only through runner's gate | `team_2026-10-31_next/log.md` 31 Oct 14:15, 14:34 |
| D35 | builder's test / E1-scuff read outside an opening (added 1 Nov): a CPU batch (31 Oct 14:46 to 14:54) ran `m0_audit_b3 --test-scuff --ext-scuff` on the already-opened f3_SUPPF s0 and p6_L3 s0, before coach's ruling reached it | Test (incl. test_noscuff) and E1-scuff numbers computed; not used, not reported | Quarantined unread on gaint (`builder_scratch/quarantine_test_reads_2026-10-31`, chmod a-r, MANIFEST.md5 e367b101); disclosed in protocol_thin_b3 §0 | log 31 Oct 17:32, 17:34 |
| D36 | A gate inside a comment (added 1 Nov): `pf2_post.sh` a82ad566 put the extra-pass `gate_wait` in a trailing comment | Extra hooks would have run ungated | coach found it (14:40); fixed 14:41 (0b5fe17b), each GPU call checked for a live gate | log 31 Oct 14:40, 14:41 |
| D37 | Usage caps and respawns (added 1 Nov): 31 Oct 14:54 to 17:30 (all agents paused); 1 Nov ~14:36 to 18:40 (all agents ended) | THIN ran unattended; the HC / A8 smoke slot after THIN's last dispatch was missed; PF2E's build finished after the respawn | Respawned from disk state (runner, coach, found, builder, judge; calib and domain done); state on disk in log and build files | log 31 Oct 17:31; 1 Nov 18:40 |
| D38 | Smoke peak below the real scoring peak (added 1 Nov): PF2's LA pass (15 runs, test + val) peaked at 7,758 MiB at 07:45:13 1 Nov; the gate (7,900) assumed the smoke's 5,824 (one run, val only) | Min free 2,635 MiB (< 3,000 for ~30 s): the 2 GB floor held by 587 MiB; finllm unaffected | THIN opening gate 9,900 before any THIN number; rule max(smoke, last real peak) + 2 GB | log 1 Nov 08:28, 08:30; `verify_pf2.md` |
| D39 | Test images touched for structure (added 1 Nov): domain's half-cut detector feature runs (R1, R2b) included the 50 test images; calib read test images for appearance stats and the max class id of the test masks; judge read test masks for padding class 7 | No labels, scores or predictions read; nothing chosen | Test dropped from every detector set (coach 18:21); mask-format checks on train / val only | log 31 Oct 18:21, 18:28; 1 Nov 00:27; `idea02_intensity.md` judge note 2 |
| D40 | Training stdout tails (added 1 Nov): judge printed the last ~150 chars of 13 trained THIN stdouts (~18:49 1 Nov); builder and runner tailed HC smoke stdouts | judge saw per-run TEST crack / inactive IoU of 13 THIN runs before the opening; not recorded, no comparator, nothing chosen (protocol locked). The smokes exit before any TEST block | Rule: never tail / cat / less a training stdout; grep step lines (team-lead 19:02); watchers count Tracebacks with `grep -ho \| wc -l` | log 1 Nov 18:58, 18:55, 19:02, 19:05 |
| D41 | Laptop memory pressure (added 1 Nov, 19:10): 544 MB available of 15.6 GB, swap full (mostly the user's own apps) | Claude Code stopped runner's 4 local background tasks (THIN and cv02 watchers, two waits) | Watchers moved to gaint (one event watcher, `rwatch.sh`, tmux rwatch); one local waiter for cv02 polls; at most one helper agent; found and builder stopped after logging state | log 1 Nov 19:11, 19:15, 19:28, 19:43 |
| D42 | `set -e` chained checks (added 1 Nov): `[ a ] && [ b ]` under `set -e` does not stop on an early failing term, so integrity checks in `thin_post.sh` / `pf2_post.sh` could pass silently | None found: THIN re-verified directly (HEAD = DEPLOY = REVISION c9bbb02, comparator MANIFEST, scorer md5s) | Separate checks with explicit exits in new scripts; coach's verify re-checks independently | log 1 Nov 20:19, 20:20 |
| D43 | Hand-written timestamps (added 1 Nov): coach (31 Oct 14:10), runner (14:13), found's version headers, judge (31 Oct 14:30; 1 Nov four lines stamped 18:51 / 18:58 / 19:20 / 19:36 for events at ~18:49-18:54, the furthest ~42 min ahead) | Wrong order in the log for a few minutes | coach's and runner's lines corrected in place; found's and judge's 31 Oct headers set to log.md times; judge's four 1 Nov lines stand as written, followed by a correction line at 18:55 (only the sign-off header in `judge/review_B6_v0.md` corrected in place). Stamps from `date` only | log 31 Oct 14:13, 14:30; 1 Nov 18:55 |
| D44 | Small slips caught before any number (added 1 Nov): coach printed `$(md5sum ...)` literally; judge's unquoted heredoc lost backtick paths; runner closed its own idle tmux window by name; the 7 s R34 B5 dump fell between memory samples; runner's ssh heredoc partly ran on the laptop (stopped at the deploy check) | None | Corrected and disclosed in the log | log 31 Oct 14:28, 14:41, 14:49, 23:34; 1 Nov 18:45 |
| D45 | PF2E copy slips (added 1 Nov): `pf2e_b5.sh` copied records and summaries into one folder and lost the test / ext summaries; a relative path broke runner's first local scoring | Summaries on gaint only for ~10 min; FileNotFoundError before any output | Fixed (out_b5 MANIFEST 6ea19679); rerun with an absolute path | log 1 Nov 19:16, 19:39, 19:46 |

---

## (e) Open questions, and what would resolve each

| ID | Question | Current evidence | What would resolve it |
|---|---|---|---|
| E1 | Does SSL beat supervised once labels are not scarce (20/50/100%)? | P13 at 5%: yes on inactive and crack relF1@2 (CsM5). P11 at 10%: rule passes, inactive not robust. **P16 (done): no** for the Cs recipe, n.d. at 20/50/100% with and without the noisy cell (A11) | Answered for this recipe; a BsM-style arm at 20/50% would be exploratory (C6) |
| E2 | Is a UCF-EL-trained encoder better than ImageNet init at 5%/10%? | P4: pretrained ≫ random. **P15 (done): no.** n.d. at 5%; worse on all three primaries at 10% | Answered for this recipe; MIM / self-supervised pretraining untested (E12). [Qualified 30 Oct: "this recipe" includes the house optimizer, which erased encoder layer3/4 in every ResNet-34 run measured (C15), so P15 likely tested little more than conv1/layer1 transfer (S; not measured on the P15 encoder). Open under an encoder-preserving fine-tune (E18).] |
| E3 | Hard vs tolerant pseudo-labels under CutMix: is hard really better for crack? | P13 BsM5 − A5c crack +0.029 on 5 seeds (+0.036 on 3). CsM5 − BsM5 on 5 vs 5 (Amendment 2): −0.015, n.d. by seeds; over cells −0.015 [−0.023, −0.009] | Over cells yes, by seeds not shown. More seeds, or the same contrast at 10–20% |
| E4 | Does CutMix matter? | P13 CsM5 − Cs5: n.d. on seeds; crack +0.010 over cells; unlabelled loss share 0.46 → 0.77 | More seeds; P16 cannot answer (CutMix off) |
| E5 | Why do val and test disagree on inactive? | Val has 6 inactive cells (A4) | A larger selection set (held-out train cells or cross-validation) |
| E6 | Would the cv02 vs gaint disagreement on P12 survive more seeds? | gaint passes, cv02 fails (C7) | 5+ seeds per machine on the same contrast |
| E7 | Do conclusions hold on other labelled splits? | Only split 0 used (A9) | Rerun key contrasts on splits 1 and 2 |
| E8 | Can models transfer to unseen modules? | Crack IoU 0.471 → 0.152 (A6) | Pretraining (P15, MIM), more diverse labelled data, a domain-shift-aware evaluation. [Qualified 30 Oct: the 27 Oct team traced 75% of E1 crack to 20 half-cut + scuff cells (FINAL recall 0.126), a context missing from training (doc 18 §U). FINAL reaches E1 crack recall 0.215. MIM5 did not move the scuff + half-cut gap (0.0295 → 0.0268). Labels for that context (B2) and a scuff class (B3) are the current routes (doc 19 §8).] |
| E9 | Is the external pool useless, or just mismatched? | Source-specific crack harm (A7) | Re-walk the Dropbox listing; harmonise contrast; a matched pool [Qualified 31 Oct: the 159k-row HF pool is the same Pratt pool, CSIR + ARTS only, no new half-cells (`pool_large/`)] |
| E10 | Would more labelled cells (E-SCDD) change the picture? | Downloaded and audited 12 Oct (doc 17).<br>• 233 labelled real cells new to us: 87 crack, 20 inactive.<br>• 111 of them are in our external pool and 105 are E1's set.<br>• Mostly CSIR from unseen modules.<br>• E-SCDD's train also has 93 synthetic images. | The user decides whether to use them; doing so means a new base recipe, not an extension of the P-series |
| E11 | Does ALHVR (or DTCT alone) help with a fair loss schedule? | Never fairly tested (B3); prototypes dead (**answered 23 Oct by AL1, D7 pool: no**; ALHVR-EL and DTCT-only are WORSE than supervised on inactive, routing and CG-CPCL n.d.) | A port with λ at full strength early, plus a loss-off control |
| E12 | Is in-domain self-supervised pretraining (MIM) worth it? | Untested; directions row 3 | Protocol + 1–2 GPU-days. [Qualified 30 Oct: MIM5 (5%, house fine-tune) n.d., every estimate negative; the house fine-tune erased the layers MIM changed (C15). Open at 100% under PF: protocol_100 MIM100-PF − SUP100-PF (E19).] [Qualified 31 Oct: MIM100-PF − SUP100-PF n.d. at 100% with the encoder kept (`verify_100_o1.md`); closed] |
| E13 | Severity grading (Köntges A/B/C) and the per-cell quantities | Post-processing lost in the reset (D1); power loss out of scope (user, 11 Oct) | Rebuild components / skeleton / isolation; grade agreement (κ) on GT vs predicted masks (proposal E6) |
| E14 | Admin inputs never confirmed | Mid-term date (assumed ~14 Oct); report template and page limit; whether MoE is required by the advisor; target model size (~2M vs ~4M; "not a constraint" for now) | Ask the user (phase-1 §17 items 9–10; deck outline §17) |
| E16 | How much of BsM5's gain needs the labelled decoder to fit pseudo-labels? | P17: BsD5 − BsM5 n.d. (−0.006 / +0.011 / −0.008); thresholds about 40% of the gain; decoupled teacher AP lower (crack 0.310 vs 0.367) | More seeds (the threshold scales with seed sd), or a larger test set for the over-cell lean on crack (P(Δ > 0) = 0.06) |
| E17 | Does the BsM recipe beat supervised at 20%+ in a confirmatory test? | P18 (exploratory): inactive +0.060 at 20% (CI includes 0), crack n.d.; 50% not run | A locked BsM arm on a fresh split, or E-SCDD's extra test cells |
| E15 | Why does the model sometimes call a very noisy cell crack, and how often would it happen on real field images? | P16 A11: seed-dependent, confident, both supervised and SSL; the matching train cell (`CSIR_00070_r7_c2`) is unlabelled below 100% | Noise augmentation or a noise-aware input check; count noisy cells in the external pool and in WattCycle-like data; a larger test set with more noisy cells |
| E18 | (added 30 Oct) Does an encoder-preserving fine-tune (PF) beat the house fine-tune at 100% labels? | Encoder erasure under the house recipe (C15); frozen ResNet-50 / ConvNeXt rank BMRK crack better than our fine-tuned encoder (doc 18 §D1). Pre-stated expectation crack −0.01 to +0.02, sign uncertain (S) | protocol_100 SUP100-PF − SUP100-g, 5 v 5 on gaint (running; no result yet) [Qualified 31 Oct: answered on test, n.d. (`verify_100_o1.md`); E1 lead only (E23)] |
| E19 | (added 30 Oct) Does MIM pretraining on the pool help when the fine-tune keeps it? | MIM5 n.d. at 5% under the house fine-tune; unknown under PF (S) | protocol_100 MIM100-PF − SUP100-PF (running) [Qualified 31 Oct: answered, no (n.d. both sets, tau 0 and 1)] |
| E20 | (added 30 Oct) Does crack copy-paste onto pool cells help at 100%? | CP5 stopped unscored; diag: 5% is the wrong test for a label-dosed method. Pre-stated crack 0 to +0.015 vs MDE 0.012 (S) | protocol_100 CP100 − SUP100-g with the LA co-condition (running) [Qualified 31 Oct: answered, no (n.d.; E3b decoy FLAG, C16)] |
| E21 | (added 30 Oct) How many train masks are wrong? | B1: crack flags in 24 of 239 audited cells (10.0 per 100), below the val base rate (16.7 per 100 for crack FL) | The user's marks on the three B1 sheets; then a `masks_escdd_v2` with a change list |
| E22 | (added 30 Oct) Does a scuff class reduce E1 crack false alarms on streaks without losing crack? | 8.7k crack px per run on streaks (L3 100%); scuff labelled crack in 6 train cells (A14). Expected test n.d. (S) | B3 (`spec_b3_scuff.md`), stronger with B2 mined labels |
| E23 | (added 31 Oct) Is PF's E1 gain real? | E1 crack recall 0.169 → 0.213, inactive IoU 0.041 → 0.245; the crack gain only in 29 scuff + half-cut cells; E1 read many times (C17) | PF2: new seeds 5 to 9 with E1 co-primaries pre-registered (coach's proposal; needs the user and vetter Q1) [Answered 1 Nov: PF2 on seeds 5 to 9: E1 inactive replicated (+0.1890, BETTER); E1 crack recall not (+0.0271, n.d.); doc 11 rows 30, 32.] |
| E24 | (added 31 Oct) Does ResNet-50 help at 100% under PF? | D: RN50-5 passes the E1 read narrowly (+0.060, cost 0.047), not an ensemble-size effect (R34-10 +0.001); Track M R3 RN50 WORSE on test inactive | RN50-PF vs SUP100-PF, 5 v 5, test primaries plus an E1 secondary [Answered 1 Nov: no. RN50-PF test inactive WORSE (−0.0289); closed (doc 11 row 33).] |
| E25 | (added 31 Oct) Does the B2 ranking find scuff / crack half-cells? | Train-scuff AUROC 0.384 / 0.437 (n_pos 4 / 9); against Hanifi labels 0.62 to 0.70 (35 cells) | The user's marks: 90 ranked vs 10 random panels (≥ 25 / 38 / 48 ranked hits at 0 / 1 / 2 random hits) |
| E26 | (added 1 Nov) Is PF's inactive gain also in-distribution? | Test inactive +0.017 n.d. (16 cells, n_eff 7.2); E1 +0.19 (10 cells) | B6 (module-grouped CV, cv02 only; power ~13% at +0.017, 80% at ~+0.055) |
| E27 | (added 1 Nov) Do thin-crack losses or a scuff class help on BEST? | Smokes only; B3 scuff IoU 0 at 2k | THIN-B3 opening (running at writing) [Answered 1 Nov ~21:40: no arm passes (SKR FAIL, CLD FAIL, B3 n.d.: scuff not learned); SKR lifts E1 crack detection at a precision cost (doc 11 rows 40 to 42).] |
| E28 | (added 1 Nov) Does training on synthetic half-cuts help E1? | Val made into half-cuts loses 0.14 recall; the SHV1 loss is ranking | HC (queued), E1 opening #3 |
| E29 | (added 1 Nov) Does a foundation encoder help under PF? | Frozen probe: IN R50 0.444 > DINOv3 CNX-T 0.363 > IN-1k CNX-T 0.310 (F51 AP) | A8 screen (A8 vs A8c, 2 seeds, 4k), then a full arm if GO |
| E30 | (added 1 Nov) Can E1's half-cut offset be chosen without E1? | Oracle on E1: b +5.4 half-cut vs −0.8 full; simulated half-cuts show +0.4 / +0.9 (pre-check FAIL); no labelled non-E1 half-cut crack set (A16) | Labelled half-cuts with E1-like context (B2 masks, B3 + mining) |

## Related docs
- `00_START_HERE.md`
- `03_datasets_and_splits.md` (A1–A10 in data terms)
- `06_history_phase0_phase1.md` (B1–B14 in context)
- `07_methodology_rules_and_statistics.md` (the rules behind C1–C2)
- `08_experiments_P1_P7_diagnostics.md`, `09_experiments_P8_P12_ssl_series.md`, `10_experiments_P13_P16_E1.md`
- `11_results_synthesis_and_claims.md`
- `12_decisions_log.md`
- `14_code_and_infrastructure.md` (D1–D18 in system terms)
- `15_status_remaining_work.md` (E1–E14 as work items)
- `16_faq_for_the_guide.md`
