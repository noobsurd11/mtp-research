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
| C11 | EMA-only effect unmeasured; bit-identity checked for 100 steps | open | low |
| C12 | Seeds pooled across commits and protocols | mitigated (diff checks) | low |
| C13 | Effort concentrated on SSL | open | medium (strategic) |
| D1–D19 | Infrastructure incidents | mostly resolved | low for results, one high (gaint reset) |
| E1–E16 | Open questions | open (E1, E2 answered) | see section (e) |

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

---

## (b) Past results that are invalid or were misread

None of these may be quoted as a method result. Old-era numbers stay in separate tables from the P-series (standing rule; memory `mtp-el-ssl-project.md`). History: `06_history_phase0_phase1.md`.

| ID | Result | Why it is invalid or misread | Source |
|---|---|---|---|
| B1 | Every Mean Teacher result with **SemiCE**: BenchmarkEL MT-20, UCF MT 1%/5% on cv02, the held gaint external-pool queue | SemiCE thresholds raw logits. 100% of unlabelled pixels have ≥ 2 "positive" classes (background on 98.9%, crack on 20.3% vs a true 0.19%). The target is incoherent | `results/p2/README.md` |
| B2 | "MT beats SL-20" (+0.023, p 0.095 test; +0.028, p 0.004 val+test) | MT with λ = 0 scores the same (paired −0.000 ± 0.024). The EMA adds nothing because the learning rate ends at 0 (teacher − student +0.000 ± 0.002) | handoff 7 Oct §6.1–6.2 |
| B3 | "ALHVR beats SL-20" (+0.029, p 0.045) and "ALHVR modules do nothing" | ALHVR equals its loss-off control (+0.005 ± 0.023). But its λ follows a sigmoid over the whole run and reaches 0.1 only at the last step, while our cosine learning rate reaches 0. So the loss was barely applied: neither a gain nor a null is shown. The measured prototype failure (cross-network prototypes 4.6% correct on Ω3 crack) still stands | handoff 7 Oct §6.2, §6.8, §9.1 |
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

### C11. The EMA-only effect is unmeasured; bit-identity checked for 100 steps (open, low)
- **What:**
  - In P13/P16, A (supervised) is the loss-off control. But SSL arms are scored on the EMA teacher, while A has no EMA.
  - Ds5 (separate forward, λ = 0, teacher evaluated) was dropped in Amendment 1.
  - The bit-identity of the λ = 0 student and supervised training was verified on GPU for 100 steps (`results/p13_audit/smoke_gpu.log`).
- **Evidence that the EMA effect is small:**
  - phase 1: teacher − student +0.000 ± 0.002 with cosine LR to 0;
  - P8: student = teacher (crack 0.383 vs 0.383).
- **Impact:** CsM5 − A5c contains the loss effect, CutMix and any EMA effect. Probably negligible, but not measured in P13. The same holds for P17's BsD5 − A5c: the gain that reaches the teacher without the decoder fitting pseudo-labels comes through the encoder or the EMA.
- **Mitigation:** run Ds5 at 3–5 seeds if this ever matters.

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

---

## (e) Open questions, and what would resolve each

| ID | Question | Current evidence | What would resolve it |
|---|---|---|---|
| E1 | Does SSL beat supervised once labels are not scarce (20/50/100%)? | P13 at 5%: yes on inactive and crack relF1@2 (CsM5). P11 at 10%: rule passes, inactive not robust. **P16 (done): no** for the Cs recipe, n.d. at 20/50/100% with and without the noisy cell (A11) | Answered for this recipe; a BsM-style arm at 20/50% would be exploratory (C6) |
| E2 | Is a UCF-EL-trained encoder better than ImageNet init at 5%/10%? | P4: pretrained ≫ random. **P15 (done): no.** n.d. at 5%; worse on all three primaries at 10% | Answered for this recipe; MIM / self-supervised pretraining untested (E12) |
| E3 | Hard vs tolerant pseudo-labels under CutMix: is hard really better for crack? | P13 BsM5 − A5c crack +0.029 on 5 seeds (+0.036 on 3). CsM5 − BsM5 on 5 vs 5 (Amendment 2): −0.015, n.d. by seeds; over cells −0.015 [−0.023, −0.009] | Over cells yes, by seeds not shown. More seeds, or the same contrast at 10–20% |
| E4 | Does CutMix matter? | P13 CsM5 − Cs5: n.d. on seeds; crack +0.010 over cells; unlabelled loss share 0.46 → 0.77 | More seeds; P16 cannot answer (CutMix off) |
| E5 | Why do val and test disagree on inactive? | Val has 6 inactive cells (A4) | A larger selection set (held-out train cells or cross-validation) |
| E6 | Would the cv02 vs gaint disagreement on P12 survive more seeds? | gaint passes, cv02 fails (C7) | 5+ seeds per machine on the same contrast |
| E7 | Do conclusions hold on other labelled splits? | Only split 0 used (A9) | Rerun key contrasts on splits 1 and 2 |
| E8 | Can models transfer to unseen modules? | Crack IoU 0.471 → 0.152 (A6) | Pretraining (P15, MIM), more diverse labelled data, a domain-shift-aware evaluation |
| E9 | Is the external pool useless, or just mismatched? | Source-specific crack harm (A7) | Re-walk the Dropbox listing; harmonise contrast; a matched pool |
| E10 | Would more labelled cells (E-SCDD) change the picture? | Downloaded and audited 12 Oct (doc 17).<br>• 233 labelled real cells new to us: 87 crack, 20 inactive.<br>• 111 of them are in our external pool and 105 are E1's set.<br>• Mostly CSIR from unseen modules.<br>• E-SCDD's train also has 93 synthetic images. | The user decides whether to use them; doing so means a new base recipe, not an extension of the P-series |
| E11 | Does ALHVR (or DTCT alone) help with a fair loss schedule? | Never fairly tested (B3); prototypes dead | A port with λ at full strength early, plus a loss-off control |
| E12 | Is in-domain self-supervised pretraining (MIM) worth it? | Untested; directions row 3 | Protocol + 1–2 GPU-days |
| E13 | Severity grading (Köntges A/B/C) and the per-cell quantities | Post-processing lost in the reset (D1); power loss out of scope (user, 11 Oct) | Rebuild components / skeleton / isolation; grade agreement (κ) on GT vs predicted masks (proposal E6) |
| E14 | Admin inputs never confirmed | Mid-term date (assumed ~14 Oct); report template and page limit; whether MoE is required by the advisor; target model size (~2M vs ~4M; "not a constraint" for now) | Ask the user (phase-1 §17 items 9–10; deck outline §17) |
| E16 | How much of BsM5's gain needs the labelled decoder to fit pseudo-labels? | P17: BsD5 − BsM5 n.d. (−0.006 / +0.011 / −0.008); thresholds about 40% of the gain; decoupled teacher AP lower (crack 0.310 vs 0.367) | More seeds (the threshold scales with seed sd), or a larger test set for the over-cell lean on crack (P(Δ > 0) = 0.06) |
| E15 | Why does the model sometimes call a very noisy cell crack, and how often would it happen on real field images? | P16 A11: seed-dependent, confident, both supervised and SSL; the matching train cell (`CSIR_00070_r7_c2`) is unlabelled below 100% | Noise augmentation or a noise-aware input check; count noisy cells in the external pool and in WattCycle-like data; a larger test set with more noisy cells |

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
