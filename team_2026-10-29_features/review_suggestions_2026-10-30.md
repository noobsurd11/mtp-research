# vetter: review of the 13 suggestions (30 Oct 2026)

Independent check of the user's 30 Oct suggestion list (items 1 to 12, plus item 13 added later) against repo files and local data. Tags: E measured (file or my recount), R literature (Research MCP id), S judgement.

**Scope.** Read-only. No test number computed, no protocol_100 output opened, no GPU touched. On gaint: one `ls`. No downloads.

**My recounts.** Scratch scripts, not in the repo:
- release stem diffs;
- mask class counts on the local release masks;
- the B2 v2 score scored against Hanifi labels on pool half-cells (pool cells only; descriptive).

## 0. Findings that change the picture
1. **The "Pratt 20221008 extras" are E1 (E).**
   - 20221008 minus our 582 is exactly 117 cells: 112 CSIR + 5 BMRK = ext117. 11 of them are in the pool, which leaves the 106 E1 cells.
   - 66 of the 117 are half-cut. Only 4 carry class 24 in 20221008 itself; the other 62 are half-cut only through E-SCDD's class 29.
   - So item 2 (train on them) and item 3 option B (split them) use up the only sealed unseen-module set. That set is where the half-cut + scuff failure was found.
2. **Hanifi half-cuts were already trained on once: R4 (E).**
   - R4 added 107 `_rf` cells, including the 43 half-cuts (24 with crack), with labels as released and scuff set to ignore. `trackM/results_r4.md`, `data_addendum.md`, 27 Oct `ideas.md` F4b, F9.
   - Test: n.d. E1 crack IoU 0.148 → 0.146. E1 half-cut recall 0.133 → 0.123 (−0.011, n.d.).
3. **The Hanifi half-cells are an unused validation set (E, descriptive).**
   - 35 of the 43 sit inside B2's 986 pool half-cells.
   - 3 are among the 100 panels already sent to the user:
     - `CSIR_00299_r7_c3`: 0 crack, 0 scuff;
     - `CSIR_00335_r20_c1`: 162 crack px;
     - `CSIR_00299_r22_c6`: 118 crack + 388 scuff px.
   - B2 v2 score against their labels (approximate 95% CI, Hanley-McNeil):

     | Label | Positives / negatives | AUROC |
     |---|---|---|
     | crack ≥ 20 px | 16 / 19 | 0.62 [0.42, 0.81] |
     | scuff | 9 / 26 | 0.70 [0.49, 0.91] |
     | crack or scuff | 18 / 17 | 0.64 |

   - The 27 Oct plan named exactly this check. The 30 Oct B2 validation used 4 to 9 train scuff cells instead (AUROC 0.384 / 0.437).
   - **Caveats:** Hanifi chose which cells to label, so the base rate here (18/35 crack or scuff) is not the pool's. Crack labels are speckled, which is why I used a ≥ 20 px presence cutoff.
4. **Module-family mismatch (E).**
   - Pool and Hanifi half-cells all come from CSIR modules 297 to 335 (8 modules).
   - E1's 58 half-cuts (`e1_context.tsv`) come from 43 modules in CSIR 1621 to 2328, plus 1 in CSIR_00300.
   - The pool's only cells from that later range (modules 2363 to 2382, 1,038 cells) are full cells (27 Oct F10).
   - So no labelled or mineable source matches E1's half-cut family. Lower the expected E1 gain from items 3A and 7 accordingly (S).
5. **The test-scuff relabel is not decided (E).**
   - The user decided "train scuff as its own class" (11:12 IST).
   - Test GT is open decision 8, and team-lead ruled "test masks not touched now".
6. **The Track D claim is measured, but narrower than item 7 states (E).**
   - Setting: 5% base + 12 cells, chosen with ground truth (oracle), 3 draws × 3 seeds (user-approved deviation from the 5-seed rule).
   - Tc − R: BETTER on relF1@2 (+0.030), marginal on IoU. Ts − Tc: n.d.
   - "Beats SSL" is descriptive (Ts 0.352 vs BsM5 0.331), not a rule contrast. On inactive, SSL leads (0.385 vs 0.33 to 0.35).
   - Never measured at 100%, or with a model-chosen list (`trackD/verify_labelset.md`).

**Where the newer data lives (E).**
- **Local:**
  - `~/mtp/datasets/BenchmarkEL_releases/dataset_20221008`: 695 cells (553/70/72);
  - `dataset_20220723`: 642;
  - E-SCDD at `~/mtp/datasets/escdd_full`: 903 files = 693 + 117 `_rf` + 93 synthetic. Mirror at `escdd_mirror_shivahanifi`.
- **gaint:**
  - `/home/noob/work/datasets/BenchmarkELimages/dataset_20221008`;
  - `cv02_noob_el/ext117`;
  - `el-*/data/escdd_masks`.
- Nothing needs downloading for items 1 to 3.

## 1. Item table
Cost unit: lane-h = hours on one of the 3 gaint lanes (~2.4 h per 20k-step R34 run). A 5-run arm is about 12 lane-h, about 5 h wall when 3 lanes are free. MDE at 100% (clean): crack IoU 0.012, relF1@2 0.013, inactive IoU 0.032.

| # | Premise check | Status | Value at 100% (house rule) | Cost / risk | Depends on | Verdict |
|---|---|---|---|---|---|---|
| 1 Scuff class | Mostly E-correct (N1). Wrong: "relabel test as decided" (open, decision 8). Brightening and corrosion: 0 px in our 582; star 238 px in 3 train cells | Train side decided, spec ready (`spec_b3_scuff.md`), not run | Test primaries n.d. by design (649 of ~272k train crack px change). Value is E1 precision: crack-on-scuff FP −20 to −60% (spec, S) | 12 lane-h, 0 user h. A second test-mask version breaks continuity with FINAL and P/M numbers | Opening 1 (BEST); decision 8 | **DO AFTER opening 1.** Verdict on current GT; 236-px-ignored version descriptive |
| 2 Newer database | Core premise wrong (N2): the extras are E1. 66 Pratt / 43 Hanifi half-cut and 0 half-cut in our 582: counts correct | New as a base; the Hanifi part = R4 (n.d.); "drop remap" contains item 1 | Unknown on test; removes the only readout of the half-cut failure | Resets every baseline (12 lane-h + all comparators); FINAL, P, M, protocol_100 lose comparability; 3 classes with no train px | User decision on E1 | **REJECT as stated.** Keep the Hanifi non-E1 part under item 3 |
| 3 Unseen-cell training | A: E-correct (52 noisy crack cells). Hygiene gaps (N3). B: the 117 are E1. Boxes2Pixels exists, but its noise model differs | A done once as R4 (n.d.; E1 half-cut −0.011). B new | A as a training arm: test n.d. likely (R4), E1 gain doubtful (finding 4). A as a validation set: high information, no GPU | A-val: CPU minutes. A-train: 12 lane-h + 2 to 3 user h (clean 24 half-cut crack cells). B: halves a 32-crack-cell set | User OK on `_rf`; A-train after item 1 | **A-val DO NOW. A-train DO AFTER item 1, cleaned crack only. B REJECT** |
| 4 Thin-crack loss | S, sound. clDice and Skeleton Recall exist (R). Tolerance band partly tested: P14 tolerant CE, crack unchanged; band-ignore +0.007 at 100% | Planned (coach C) | S: relR@2 / component recall +0.01 to +0.03; crack IoU −0.01 to +0.01. Must be compared at matched precision and against LA τ 1 | 12 lane-h + ~0.5 day code; distance-map target is a head change (more) | Opening 1 (BEST); metric pre-registration (item 5) | **DO AFTER opening 1:** one arm, Skeleton Recall on BEST; clDice / distance map PARK |
| 5 Measurement | E: clean set is already a verdict set; relF1@2 is already a primary. Component recall and relR@2 at relP@2 ≥ 0.90 were recommended on 27 Oct (`eval.md` §6) but not adopted | Clean set done; metrics proposed; CV designed (`eval.md` §4), not run | No score change. CV: inactive MDE 0.037 → 0.017 to 0.029 (S, eval.md) | Metrics: CPU. CV: 25 runs/arm ≈ 60 lane-h ≈ 20+ h wall per arm, ≥ 2 arms; new base; uses 100 `_rf` cells as labelled | Metrics: none. CV: user wants an inactive claim | **Metrics DO NOW** (pre-register for every protocol after protocol_100). **CV PARK** unless Q6 = yes |
| 6 Inactive | S. Not found by the tools: DCA (repo note: a 3D class-group-expert SSL method, not region routing). The model already predicts crack and inactive jointly | DCA skipped 13 Oct (D36). R4's 10 extra inactive cells: +0.0085 n.d. | Unknown; test cannot resolve < 0.032 (16 inactive cells, top-3 59%). R3 RN50 was WORSE on inactive | DCA: large dev and pseudo-label SSL; labels: user hours | A bigger inactive eval (item 5 CV) | **PARK.** Free part: the 9 inactive B1 panels |
| 7 Targeted labelling | Partly wrong (N7): 11,938 is the raw pool (needs hygiene → 11,219); pool has 0 BMRK; Track D scoped (finding 6) | Running: B2 v2 sent; ranking failed its OOF check | S (27 Oct): E1 crack recall +0.04 to +0.15, pooled test ≤ +0.01; tempered by R4 and finding 4 | User ~15 min marks + 6 to 10 h masks (20 to 40 cells); 12 lane-h | Hanifi check (item 3 A-val); item 1 | **Check DO NOW** (finding 3, to be reproduced). **Masks DO AFTER item 1**, and only if the marks show ranked > random |
| 8 Bigger encoders | Condition mis-specified (N8): evidence ties the encoder to the recipe (SUP100-PF), not to the pool | Planned (coach A2, gated on SUP100-PF) | S: crack IoU n.d. to +0.01; E1 recall up (D: RN50-5 +0.060 at cost 0.047, narrow); inactive is the risk (R3 −0.025 WORSE) | RN50 ~1.8x R34 time → ~4 to 5 h/run, ~22 lane-h/arm, more memory, so possibly 2 lanes (S) | Opening 1 (SUP100-PF verdict) | **DO AFTER opening 1**, gated on SUP100-PF; RN50 first, ConvNeXt-T later (pilot below reference; LN mechanism not established) |
| 9 Confound note | Correct (E) (N9) | New write-up item | Thesis validity only | 0 | none | **DO NOW** |
| 10 Parked | E: P16 null at 20/50/100%. The cell-type-routed test already ran: D(c) BN-HC routed, target +0.174, failed cost 0.085 > 0.05 | Decided (coach stop list); routed test done | none | none | none | **AGREE.** Re-read BN-HC with its bias chosen on the 35 Hanifi half-cells (CPU, E1 descriptive) after item 3 A-val |
| 11 B1 audit | E: 24 crack cells (A50 OOF, 239 of 478 train cells; 15 FL, 10 ML), 9 inactive, 15 scuff/star; sheets delivered | Waiting on the user's marks | S: test gain likely below MDE: flagged crack px ≈ 5.3k ≈ 2% of train crack px (the +0.08 revision changed ~50%). Inactive flags 13.7k px may matter more | 1 user h; fixes go into the next data arm, not their own arm | none | **DO NOW (user)** |
| 12 SSL / DINOv3 | "Erased by ~2k": E, ResNet-34 house recipe only (N12). "Freeze / lower LR" = PF, already running. DINOv3 id correct (R); the related papers exist but none is EL / thin-crack / 100%-label evidence. Pool gap correct | PF running; DINOv3 / INSID3 new | Unknown. 16-px ViT patches vs 2 to 3 px cracks; Track D frozen DINOv2-S failed the BMRK bar (0.122 to 0.133 vs 0.215; R34 0.185) | Download (needs OK); 2 to 4 days dev; continued pretraining 10 to 30 GPU-h (S); memory beside finllm | Opening 1 (MIM100-PF, SUP100-PF) | **PF: running. DINOv3 / INSID3: PARK**; if wanted, a frozen probe first (Track D D1 design). The fallback "effort to 2, 3, 7" → 3A and 7 yes, 2 no |
| 13 Large pool (§6b) | Partly wrong (poolscout, E; my recount agrees). It is Pratt's pool (159,332 rows, 9 folders, CSIR + ARTS only). Its half-cells are the 1,152 we already hold. It has no BMRK, CFVS or SDLE cells and no CSIR module from 400 to 2,362, so E1's family is absent. "13x" is total rows; CSIR grows only 2.5x (22,931 vs 9,204) | New (audited, not downloaded) | Item 7: nothing new for half-cut, scuff, BMRK or E1. Item 12: unknown; prior evidence leans ≤ MDE (Torpey 2024 in-domain SSL on 22k EL < ImageNet at full labels; P9 pool size ≈ 0) | Download 76 GB (2 to 21 h, gaint bandwidth unmeasured), 93 GB disk on gaint, ~1 CPU-h dedupe; MIM at 100 epochs on ~155k ≈ 70+ h GPU; leakage needs a full content dedupe | Opening 1 (MIM100-PF − SUP100-PF); protocol_100 finished | **Download LATER and only if gated** (§6b). **Item 7 use: NEVER** for its stated aim. **DO NOW:** the thesis notes (no download) |

## 2. Evidence notes per row
- **N1 (scuff, E):**
  - The two test cells are E-SCDD class 25: `ARTS_00047_r3_c1` 34 px, `ARTS_00051_r3_c2` 202 px. E-SCDD has 0 crack in both, so our 48 test crack cells become 46 under its masks.
  - Train: 12 cells, 3,246 scuff px, 649 of them labelled crack in 6 cells.
  - Star: 238 px in 3 train cells, 54 px as crack in `CFVS_00024_r3_c3`.
  - In the 117 extras (E1): scuff 38 cells, star 30, brightening 20, corrosion cell 10. All are ignore in E1 scoring, so they need deciding only if new data enters.
  - **Pitfall:** gaint `data/escdd_masks/test` already holds class 25 at those 2 cells (differs from cv02). Any corrected set must be a new, hashed directory.
- **N2 (release diff, E):**
  - 4 of our 582 are absent from 20221008: `ARTS_00057_r2_c5`, `CSIR_00178_r7_c1`, `CSIR_00179_r12_c4`, `CSIR_00179_r6_c1`.
  - The release split is reshuffled: 48 of our train cells are in its test, 38 of our test cells in its train (doc 03). So "move to the newer database" with its own split is a full reset.
  - Our 582: 0 cells with class 24 or 29 under 20221008 or E-SCDD masks. The 4 to 5 cells missing from those releases keep 20211104 masks, which have no half-cut class.
  - "0 half-cut" is a mask-class count, not a visual check.
- **N3 (Hanifi hygiene, E):**
  - 117 `_rf` = 114 CSIR + 3 ARTS. 52 have crack; 10 have inactive.
  - 43 are half-cut, all from CSIR 297 to 301 and 333 to 335. 24 of those have crack and 11 have scuff.
  - 7 of the half-cuts are in CSIR_00300, a module with one E1 cell (0 crack).
  - 4 `_rf` cells share a module with our val/test cells.
  - 100 are in the raw 11,938 pool and 90 in `mim_pool_v11` (MIM pretraining and CP backgrounds). That is not a label leak, but it is a confound for any "pool vs labels" reading.
- **N7 (pool, E):**
  - 11,938 = `splits_benchmark/external_unlabeled.txt` (CSIR 9,204, ARTS 2,734). It includes:
    - the cells of every val, test and E1 module (−413 under rule R1);
    - 11 ext117 cells;
    - 50 near-duplicates.
  - After hygiene: 11,219, plus a 256-cell monitor. `mim_pool_v11` = 11,219 + 471 train = 11,690.
  - The pool has no BMRK, CFVS or SDLE cells, so BMRK-like cells need ELPV (decision 9, deduped against the 10 BMRK test cells).
  - Half-cells: 1,152 raw, 986 after hygiene, all from 7 CSIR modules.
- **N8 (encoders, E):**
  - **For RN50:**
    - Track D frozen RN50: BMRK crack AP 0.268 vs bar 0.215 (low-precision ranking signal).
    - R3 Part B: E1 crack recall +0.036.
    - D: RN50-5 passes the E1 read narrowly.
  - **Against:** R3 inactive −0.0251 (threshold 0.0227, clean).
  - **ConvNeXt-T pilot:** val 0.6318 vs reference 0.6398.
  - A gate on a pool-feature gain would also need new RN50 MIM pretraining, which is not budgeted.
- **N9 (confound, E):**
  - In the label-fraction curve, the in-domain pool shrinks as labels rise (P16: none at 100%; Sx100 uses the external pool), and the source changes (external CSIR + ARTS vs the in-domain mix).
  - Also note:
    - the raw external pool held 196 val-module and 88 test-module cells (doc 13 A7);
    - the init and pretraining screens ran under the erasing optimizer.
- **N12 (erasure, E):**
  - House smoke a1 at 2k steps: layer3/4 cosine 0.070 / 0.003. SUP100 final: 0.018 / 0.001, layer3/4 norms 9% / 6% of init (`review_100_v1.md`, `coach_100.md` §0).
  - Measured only on ResNet-34 runs: A5c-f1, MIM5, SUP100. Not measured on the P15 or R3 encoders; the mechanism for ConvNeXt is not established.
  - PF G5: 0.975 to 0.990 at 4k.

## 3. Ranked shortlist for the user's goal
1. **Item 3 A-val + item 7 check (CPU, now).**
   - Use the 35 Hanifi pool half-cells to validate the B2 ranking. That decides whether 6 to 10 h of masking pays off.
   - They also give BN-HC its out-of-E1 bias set.
   - This is the cheapest information on the table.
2. **Item 8, RN50 under PF**, gated on SUP100-PF.
   - The E1 signal is consistent across three sources (Track D, R3, D).
   - Inactive is the guard.
3. **Item 1, B3 scuff class on BEST.**
   - User-decided and ready.
   - Deployment precision on scuff streaks.
4. **Item 4, Skeleton Recall on BEST.**
   - The "catch almost all cracks" metric (relR@2, component recall at fixed precision).
5. **Items 11 + 7, user labelling.**
   - B1 marks now (1 h).
   - B2 masks plus Hanifi crack cleanup only if the check and the marks support it.

Free alongside:
- item 5 metric pre-registration;
- the item 9 note;
- item 13 uses A + B: the pool composition as a thesis finding, and the provenance disclosure. Neither needs a download.

Item 13 is not in the top 5: the pool adds nothing for the failure contexts, and its pretraining use is gated on opening 1.

## 4. Sequencing
1. **Now until opening 1 (~03:00 to 03:30 IST 31 Oct). GPU busy, CPU only.**
   - runner: reproduce the Hanifi-cell AUROC (finding 3) and add it to `b2v2_report.txt`. Flag the 3 panels that already carry Hanifi masks; the user's marks on them give a small inter-annotator check.
   - runner, code only:
     - B3 mask build + 25-class head;
     - Skeleton Recall loss;
     - RN50-PF config;
     - a Hanifi hygiene list (drop the 7 CSIR_00300 cells and the 4 val/test-module cells).
   - coach: pre-register the post-protocol_100 metric set: component recall at val-fixed component precision ≥ 0.90, and relR@2 at relP@2 ≥ 0.90, next to IoU. Existing verdicts keep their locked metrics.
   - user: B1 marks; the question batch in §6.
2. **After opening 1:**
   - BEST = SUP100-g or SUP100-PF by its own verdict.
   - Write the B3 protocol.
   - Gate RN50-PF on SUP100-PF.
   - Decide item 13 C on MIM100-PF − SUP100-PF. If gated and the user agrees, download to gaint only after protocol_100 finishes (§13.4).
3. **After opening 2 (CP100), when lanes free:**
   - wave 1: B3, 5 runs;
   - wave 2: RN50-PF (if gated), or Skeleton Recall.
   - One change per arm, same commit and machine.
4. **After user labels:** BEST+S + cleaned Hanifi half-cells + B2 masks. BN-HC bias chosen on the Hanifi set. E1 reported as two readouts.
5. **Final:**
   - combine the components that passed into one val-chosen candidate;
   - ensemble it;
   - one test opening against FINAL (coach rule 4).
   - Every arm adds a test opening; disclose the multiplicity.
6. **Parked:** 2, 3B, the 6 methods, 10, DINOv3 / INSID3, CV (unless Q6 = yes), and the item 13 download (unless gated).

## 5. Conflicts and inconsistencies
1. **Items 2 and 3B vs 3A and 5:** the Pratt extras are E1. Training on them or splitting them contradicts "keep E1 held out" and "build a bigger held-out set".
2. **Item 1 vs open decision 8:** "relabel as decided" contradicts open decision 8 and team-lead's "test masks not touched now".
3. **Item 6 vs item 10 and D36:** DCA is a pseudo-label SSL method, which item 10 parks at ≥ 20% labels and D36 skipped.
4. **Items 8 and 12 vs coach A2:** they gate bigger encoders on a pool-feature gain; coach A2 gates them on SUP100-PF. Under erasure the recipe is the relevant gate.
5. **Item 12, "protect the encoder":** duplicates PF, already running in protocol_100.
6. **Item 7's pool:** "11,938" ignores hygiene R1 to R4, and "BMRK-like" cells cannot come from a pool with 0 BMRK.
7. **Item 4, "judge on cracks caught":** this departs from the house primaries. It needs pre-registration before any run, and component metrics have 2 to 3x the IoU threshold.
8. **Item 3A, "ignore Hanifi crack px":** removes the 24 half-cut crack examples, which are the reason to add the cells.
9. **Item 12's fallback:** "effort into 2, 3, 7" includes item 2 (rejected here) and 3B (rejected).
10. **Item 5 CV vs item 3A:** CV counts 100 `_rf` cells as labelled; if 3A trains on them, their role must be fixed first.
11. **Item 2 vs item 1:** "drop the 24-class remap" contains item 1 and adds brightening, corrosion and half-cut spacing classes that have no train px in our 582. Star has 238.
12. **Item 13 vs its own aim (E):** it proposes the pool for item 7's half-cut / BMRK-like search, but the pool has no new half-cells, no BMRK / CFVS and no E1 module family.
13. **Item 13's dedupe list vs item 3 A-val:** it lists the 17 `_rf` cells. Item 3 A-val uses all 117 `_rf` cells as a validation set, so all 117 must be excluded (poolscout's D0 already does this).
14. **Item 13 / 12 vs the item 9 confound:** a 13x pool changes size and source together (84% one ARTS type). A scaling claim needs a source-controlled subset (CSIR-complete) beside "all".

## 6. Questions only the user can answer
1. Is E1 (the 117 Pratt extras, 106 scored) still the sealed unseen-module set? Recommended: yes. This decides items 2 and 3B.
2. Scuff test GT (decision 8): verdict on the current GT plus a descriptive version with the 236 px ignored? Or a switch?
3. Hanifi `_rf` cells:
   - OK to use them now as a validation set (B2 ranking, BN-HC bias; no training)?
   - Later as training data, with cleaned crack labels (about 2 to 3 h for the 24 half-cut crack cells)?
4. Labelling hours this week. Options:
   - B1 marks (1 h);
   - B2 marks (~15 min) and pixel masks (6 to 10 h);
   - Hanifi crack cleanup (2 to 6 h).

   Which?
5. Primary metric for the thin-crack work: keep crack IoU / relF1@2 / inactive IoU, or pre-register component recall at precision ≥ 0.90 and relR@2 at relP@2 ≥ 0.90?
6. Does the thesis need a powered inactive claim at 100%? That means module-grouped CV, about 40+ h wall on gaint for 2 arms.
7. Downloads (DINOv3 weights, ELPV): still no?
8. Gate bigger encoders on SUP100-PF (the recipe) instead of a pool-feature gain?
9. **Large pool download (poolscout Q1).** Recommended: not now. Download to gaint after protocol_100 only if opening 1 gives a MIM100-PF gain and you want the pool-size question answered. If yes:
   - bandwidth cap: suggest 20 MB/s;
   - keep the sha256 manifest;
   - delete raw shards after conversion.
10. **Module exclusion rule for the large pool (poolscout Q2):** ID-wide (recommended; IDs collide across folders) or folder-qualified?
11. **Pretraining subset, if downloaded (poolscout Q4):** CSIR-complete (~22.9k, recommended first), source-balanced, or all 159k?

Answered here, not for the user:
- poolscout Q3 (near-duplicate metric): reconcile poolscout's r_hp with agent 4's on the D7 twins first, then use one metric with 0.95 for held-out sets.
- Q5 (item 7 search): nothing new to mine for half-cut / scuff / BMRK.
- Q6 (past claims): add a disclosure line only. Agent 4's 21 Oct content screen and R3 already cover val/test copies in the old pool.

## 6b. Item 13: the large unlabelled pool (HF `sasan/scdd-unlabeled`)
Sources:
- `pool_large/pool_large_audit_2026-10-30.md` (poolscout; metadata of all 159,332 rows plus a 566-row random pixel sample);
- my recount from its `manifest.tsv` (md5 25a553f1): rows, folders, sources, ID overlaps (271 / 23 / 21 / 117 `_rf` / 11 ext117) and 0 CSIR modules in 400 to 2,362 all match;
- my look at `out/montage_random24.png`.

### 13.1 Premise check
- **"Pratt's Dropbox pool, 150k cells, ~13x ours": correct by rows (E).**
  - HF = Pratt's 9 folders. All 11,993 cells of our 6 Oct download are in it under the same folder.
  - 147,394 new rows. "Hanifi's 151,700" = Pratt's 150,000 + their ~1,700 synthetic images, not a separate pool.
  - The growth is in rows only: CSIR goes 9,204 → 22,931 (2.5x); ARTS goes 2,734 → 136,401 (50x).
- **"Profile for half-cut, BMRK-like, CFVS, panel overlap with E1": answered from metadata (E).**
  - Half-cells: the 1,152 we already hold.
  - BMRK / CFVS / SDLE: 0.
  - CSIR modules 400 to 2,362: 0. E1's half-cut family (1621 to 2328) is absent.
  - E1 cells: 0. The one shared module, CSIR_00300, is already in our pool and excluded by R1.
  - New bulk: 124,467 ARTS mono 5-busbar rows (84%), mostly native 512 px, bright and low-contrast (median mean 205, sd 24, vs labelled ARTS 133, 41).
  - The 24 random cells in the montage look mostly defect-free (new 2018 modules; S, 24 cells only).
- **"Dedupe against the 582, E1, the 17 `_rf` and the 11,938": necessary, but ID rules are not enough (E).**
  - 315 of our 582 IDs are in it, including 21 test and 23 val cells, and all 117 `_rf` cells.
  - About 2,400 byte-identical copies sit under other module IDs (95% bounds 1,400 to 9,500), mostly in `multi/ribbons_3`. That folder holds 186 of our labelled IDs, including ARTS test cells.
  - 192 stems collide across folders.
  - One val ID (`CSIR_00127_r11_c5`) is a different image under the same ID.
  - Fix: dedupe against all 117 `_rf`, not only the 17, because item 3 A-val uses the `_rf` cells as a validation set.

### 13.2 How the thesis could benefit
| Use | What it buys | Evidence / expected (S unless tagged) | Cost | Verdict |
|---|---|---|---|---|
| **A. Negative result for the thesis** (no download) | A documented reason why unlabelled data cannot close the deployment gap: no public EL pool holds E1's half-cut family, scuff-rich CSIR modules, BMRK, CFVS or SDLE. The failure contexts must come from labels or other sources (ELPV for BMRK) | E (metadata, all rows). Strengthens the "labels, not pools" narrative of `coach_strategy.md` §1 | ~0.5 h writing | **DO NOW** |
| **B. Data-provenance finding** (no download) | Methods-section facts: IDs are not unique keys (192 collisions, ~2,400 cross-ID byte copies, a val ID that is a different image), and the 6 Oct download was capped at 2,500 per folder. That cap explains our pool's skew (0 CSIR mono 5-busbar). Add a disclosure line to the P9 to P16 "x" arms | E. Past claims are covered by agent 4's 21 Oct content screen of the 11,938 against val/test (decision.md D4: no confirmed copy; a byte copy would score r ≈ 1) and by R3 for `mim_pool_v11`. No re-run needed | ~0.5 h | **DO NOW** (a note, not a re-run) |
| **C. Item 12: MIM / DINOv3 pretraining at larger size** | Answers "does more unlabelled data help once the encoder is preserved?" as a pool-size / source ablation, with item 9's confound declared | Unknown. R: Torpey et al. 2024 (arxiv:2402.17611; repo note E01), in-domain SimCLR on 22k EL images, gave 0.517 mIoU vs ImageNet-SimCLR 0.534 at full labels (contrastive, full fine-tune). E: P9 pool size ≈ 0 for pseudo-labels. Both predate PF. The new rows match neither the weak sources nor E1. Expected test gain from scaling ≤ the MIM100-PF gain itself; E1 gain without basis | Download + dedupe (below). MIM at 100 epochs: CSIR-complete subset (~22k) ≈ 10 h; all ~155k ≈ 70+ h on a free GPU, more beside f100 / finllm. DINOv3 adds a weight download and 2 to 4 days dev | **LATER, only if** opening 1 shows MIM100-PF − SUP100-PF BETTER or a same-sign gain on the clean set, and the user wants the scaling question. Start with the CSIR-complete subset, not all 159k |
| **D. Item 7: targeted labelling search** (INSID3 or the B2 proposer) | Its stated aim (half-cut, scuff, BMRK-like) has nothing new to find: the half-cells are the 986 already mined | E (composition) | none | **NEVER for the stated aim** |
| **D'. ARTS mono 5-busbar crack search** | ARTS crack labels from a new cell type | S: low. ARTS is not the weakest source (BMRK, CFVS are), and the new ARTS cells are contrast-mismatched (sd 24 vs 41). Few defects visible in the sample | Download + user hours | **PARK** |
| **E. CSIR mono 5-busbar (8,340 rows our pool never sampled)** | A CSIR cell type our pool lacks, for a CSIR-weighted pretraining subset | E (count); value unknown | Part of C | Fold into C |

### 13.3 Risks
1. **Leakage into test or val (E).**
   - 21 test and 23 val cells are in the pool by ID, and copies sit under other IDs.
   - Any SSL or pretraining use without the full D0 to D4 dedupe (poolscout §6.5) is transductive on test.
   - Use the conservative module rule: ID-wide, since IDs collide across folders.
   - Use one near-duplicate metric. poolscout's r_hp and agent 4's `neardup.py` differ by up to 0.17, so reconcile them on the 7 D7 twins and known pairs before thresholds are fixed.
2. **E1 (E).** 0 E1 cells and 1 E1 module, already excluded. E1 stays clean if R1 is kept.
3. **Source mismatch (E/S).**
   - 84% of the new rows are one ARTS cell type with different intensity statistics.
   - Under PF, pretrained features survive the fine-tune, so a mismatched pretraining set matters more than it did under the erasing recipe (S).
   - A CSIR-weighted or source-balanced subset limits this.
4. **Comparability (S).** Any pool change confounds pool size with pool source (item 9). It needs its own arm, separate from protocol_100 (handbook 03 §6), with MIM100-PF on `mim_pool_v11` as the comparator.
5. **Cost and operations (E/S).**
   - 76 GB download; gaint bandwidth unmeasured (2 to 21 h for 1 to 10 MB/s). Do a one-shard timed test first.
   - 93 GB on gaint (578 GB free); the laptop cannot hold it.
   - The download competes with f100 I/O, so run it after protocol_100 with nice / ionice and a bandwidth cap.
6. **Licence (D).**
   - No licence on the Dropbox, the HF mirror or the GitHub repo.
   - Research use with citation of Pratt et al. 2023 (doi:10.1016/j.sasc.2023.200048).
   - Do not redistribute images or a derived pool.

### 13.4 Download now, later or never?
- **Not now.**
  - Protocol_100 is running, and nothing on the shortlist needs the pool.
  - Use A and B need no download.
- **Later, conditional.** Download to gaint only after protocol_100 has finished, and only if both:
  1. opening 1 gives MIM100-PF − SUP100-PF BETTER, or a same-sign gain on the clean set;
  2. the user wants the scaling ablation (C).
- **If yes, the order is:**
  1. one-shard bandwidth test;
  2. full download with a bandwidth cap;
  3. sha256 checks against the HF LFS oids;
  4. byte-compare with our 11,993 raw files;
  5. D0 to D4 dedupe with a count per rule;
  6. CSIR-complete MIM first.
  - Keep the per-shard sha256 manifest. Raw shards can be deleted after conversion, because the pinned revision `7c4e73d8` can be re-downloaded.
- **Never** for item 7's half-cut / scuff / BMRK search.
- **If opening 1 shows no MIM100-PF gain:** do not download. Close item 13 with A + B.

## 7. References
**Tool-verified (Research MCP get_paper / search_papers):**
- arxiv:2604.11162. Lendering et al., Boxes2Pixels (2026): box → SAM pseudo-masks, frozen DINOv2, one-sided self-correction; wind-turbine inspection. Matches "noisy SAM masks"; not human pixel-label noise.
- arxiv:2508.10104. Siméoni et al., DINOv3, TMLR 2026. Matches.
- arxiv:2601.08078. Xu et al., DINOv3 features for few-shot medical segmentation (DINO-AugSeg). Matches; few-shot only.
- arxiv:2603.28297. Tang et al., DinoDental: a DINOv3 benchmark comparing frozen, full fine-tune and LoRA. Matches.
- arxiv:2603.28480. Cuttano et al., INSID3: training-free in-context (one-shot) segmentation with frozen DINOv3. Matches.
- doi:10.1016/j.knosys.2026.116085. Li et al., fractal-guided diffusion representation learning for self-supervised pavement crack segmentation (no labels). Matches; pavement, not EL.
- doi:10.1080/10589759.2025.2595520. Cheng et al., self-supervised weld defect segmentation (X-ray, object-level masking). Matches.
- doi:10.1109/cvpr46437.2021.01629. Shit et al., clDice.
- doi:10.1007/978-3-031-72980-5_13. Kirchhoff et al., Skeleton Recall loss (thin tubular structures, incl. concrete cracks).
- arxiv:2402.17611. Torpey, Pratt, Klein 2024: an evaluation of pretraining for EL defect segmentation, including in-domain SSL on 22k unlabelled EL images. Numbers via repo note `literature/notes/E01_pretraining_no_pseudolabels.md`.
- doi:10.1016/j.sasc.2023.200048. Pratt, Mattheus, Klein 2023: the BenchmarkEL dataset paper, cited for the Dropbox pool.

**Not found by the tools:** DCA (two queries).
- The repo note `literature/notes/F01_rareclass_ssl_2024_2026.md` l.35 gives: Liu et al., "Divide, Conquer, and Aggregate: Asymmetric Experts for Class-Imbalanced Semi-Supervised Medical Segmentation", CVPR 2026 (CVF link).
- Not verified here. Per that note it routes by class group, not by region.

**Repo sources:**
- `SESSION_RECORD_2026-10-28_to_30.md`;
- `handbook/03`, `11`, `13`, `15`, `17`, `18`, `19`;
- `team_2026-10-29_features/`:
  - `spec_b3_scuff.md`, `coach_strategy.md`, `coach_100.md`, `diag_5pct_to_100pct.md`;
  - `d_prereg.md`, `verify_d.md`, `review_100_v1.md`;
  - `b1_audit/b1_coverage.txt`, `b2_mining/v2/`;
- `team_2026-10-27_unlabelled/eval.md`, `ideas.md`;
- `team_2026-10-29_features/pool_large/pool_large_audit_2026-10-30.md` (poolscout) and its `out/manifest.tsv`;
- `team_2026-10-24_go/trackD/verify_labelset.md`, `trackM/results_r4.md`, `data_addendum.md`, `protocol_r4.md`.
