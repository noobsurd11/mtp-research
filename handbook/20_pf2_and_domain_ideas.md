# 20. PF2, the PF ensemble, and Om's 11 unseen-panel ideas (31 Oct to 1 Nov 2026)

## What this covers
This file covers the session of 31 Oct ~07:30 to 1 Nov ~20:30 IST (THIN-B3's verified result added ~21:40), after `19_feature_learning_and_100pct_plan.md`:
- **The ask (31 Oct ~13:45):** Om's answers to the protocol_100 follow-up and 11 new ideas aimed at unseen panels (E1), pasted by the user with "work on this direction further, no budget boundaries, we have 2 more months ... refrain from manual labelling unless very much needed".
- **The 11 ideas:** each validated by one agent (calib, domain or found) and reviewed by judge. Three pass to a protocol (5, 7, 8); the rest are dropped or parked, two by a pre-registered CPU check (TTA, half-cut routing).
- **PF2:** the PF recipe replicated on new seeds 5 to 9 with E1 co-primaries; RN50 under PF.
- **PF2E:** PF vs house as 5-member ensembles (the deployable object).
- **Protocols written and armed:** THIN-B3 (Skeleton Recall, clDice, scuff class; no arm passes), HC (synthetic half-cuts), A8 screen (DINOv3 encoder), B6 (module-grouped CV for inactive).
- **The E1 policy:** E1 became a second test set with one read per registered opening.

Added 1 Nov 2026 (handbook refresh). **Tags.** E = measured (file), R = literature (Research MCP id), S = judgement. "Clean" = the 50 test cells without `CSIR_00070_r8_c4`. Rule 1 = house rule, divisor 3 (doc 07, doc 19 §0).

**Status at writing (1 Nov 2026, ~20:30 IST)**

| Item | Status | Where |
|---|---|---|
| 11 idea validations | all reviewed by judge (31 Oct 14:13 to 17:36) | `team_2026-10-31_next/ideas/` |
| Routing pre-check | FAIL (31 Oct 18:03) | `ideas/routing_precheck.md` |
| T9 (per-panel BN) | FAIL: TTA closed (31 Oct 21:13) | `ideas/t9_prereg.md` |
| S10 (SAM inactive) | PASS by its rule; method note (31 Oct 18:05) | `ideas/s10_prereg.md`, `idea10_ai_labelling.md` §6b |
| P8 probe | runs 1 and 2 done; descriptive | `ideas/idea08_foundation.md` §4c-4d |
| PF2 | PASS (E1 inactive replicated; test relF1@2 narrow); RN FAIL | `verify_pf2.md` |
| PF2E | PASS on E1 inactive (with qualifications); test n.d. | `verify_pf2e.md` |
| THIN-B3 | opened 1 Nov 19:40-21:13; **no arm passes** (SKR FAIL, CLD FAIL, B3 n.d.: scuff not learned); coach VERIFIED, judge CONFIRMED (added ~21:40) | `verify_thin_b3.md` |
| HC | locked, smoked, queued; opening trigger armed | `protocol_HC.md` |
| A8 screen | locked, smoked, queued; scoring armed | `protocol_A8screen.md` |
| B6 | design locked; cv02 only; build open | `protocol_B6.md` |

## Sources
- `SESSION_RECORD_2026-10-31_to_11-01.md` (master for this session).
- `team_2026-10-31_next/`: `README.md`, `om_2026-10-31.md`, append-only `log.md`, `e1_openings.md`; protocols `protocol_PF2.md`, `protocol_PF2E.md`, `protocol_thin_b3.md`, `protocol_HC.md`, `protocol_A8screen.md`, `protocol_B6.md`; verifications `verify_pf2.md`, `verify_pf2e.md`; builds `build_*.md`; reviews `review_hc.md`, `review_f8_wrapper.md`, `judge/review_B6_v0.md`; `ideas/*.md` (each with judge's verdict appended).
- `team_2026-10-29_features/pool_large/CLOSED.md` (item 13 close-out).
- Copies of the markdown files: `sources/teams/team_2026-10-31_next/`; the session record: `sources/session_records/`.

Where a session record and a verify or idea file disagree, the verify or idea file is used.

---

## 0. Terms used here
- **E1 (second test set from 31 Oct ~15:00, user):** the 106 unseen-module cells. A protocol may pre-register E1 co-primaries, read once at its single opening, never for tuning, selection or thresholds. Every opening is listed in `e1_openings.md` (§8).
- **`_rf` sets (Hanifi cells after hygiene: 117 − 7 CSIR_00300 − 4 val/test-module = 106):** **F51** = 51 full cells from modules not in train (12 crack cells, 36 modules), the `_rf` crack decision set; **H36** = 36 half-cuts, false alarms only (crack labels unusable, §2.1); F19 = full cells from train modules.
- **SHV1:** domain's frozen synthetic half-cut val set: 108 images = 54 val cells × 2 halves (MANIFEST 63dd5469, generator 6e702c36, seed 20261031). Val-derived, so selection on it is allowed.
- **B5 operating points (Om B5, calib's scorer `el_metrics.py`):** component recall at component precision ≥ 0.90, and relR@2 at relP@2 ≥ 0.90, at a crack bias b chosen on val. "Arm-level pooled OP": one b per arm from the pooled 5-seed val counts (steadier than per-run b).
- **Headline b (PF2E):** FINAL's D2 rule: the smallest b in 0..3 (step 0.25) with val relR@2 ≥ 0.90, used if its val relP@2 ≥ 0.90, else the b with max val relF1@2; b = 0 if that b drops val crack precision by > 0.05 (the val width flag).

## 1. The ask, the team, the rules
- **Om (S):** the remaining failure is domain generalisation to unseen panels, not data quantity: every pool route was n.d., while PF moved E1 strongly with test n.d.
- **Team (`README.md`):** team-lead; runner (gaint GPU owner); coach (protocols, APPROVED, recompute); builder (code); calib (ideas 1, 2, 7); domain (3, 4, 5, 11, item 13); found (6, 8, 9, 10); judge (adversarial review of every idea; recomputes every E claim).
- **Pipeline:** report → judge verdict → coach protocol → GPU only on coach's APPROVED; GPU work not approved by Om needs the user's OK.
- **Standing rules added:** B5 co-primaries in every protocol; never tail a training stdout (doc 13 D40); per-run data roots where a run must read no test cell (doc 14 §1.2d).

## 2. The 11 ideas
| # | Idea (owner) | Main evidence (E) | judge verdict |
|---|---|---|---|
| 1 | E1 threshold / calibration (calib) | E1 PR curve below val at every bias (relP@2 ≥ 0.70: val relR@2 0.954, E1 0.226). Label-free per-module rules lose on F51 and E1. Oracle with E1's own labels: per-module FINAL relF1@2 0.432 → 0.610; two biases (half-cut / full) 0.432 → 0.518 | DROP label-free per-panel thresholds; diagnostic KEEP; half-cut routing PARKED |
| 2 | Per-module intensity normalisation (calib) | E1 content brightness = train (median 143 vs 138, AUROC 0.52); the whole-image gap is the white letterbox of 55 / 58 E1 half-cuts; recall vs brightness ρ −0.03; test-time mappings lower val relF1@2 by 0.02 to 0.06 | DROP |
| 3 | Neighbour-reference channel (domain) | 50% of E1 cells (62% of E1 half-cuts) have no same-module file anywhere; FINAL's val crack FPs: 90% plain background, 2% ribbons, 0% spacing | Om's version DROP; in-crop variant PARK |
| 4 | Periodic-structure removal (domain) | works at pixel level, but the model already ignores busbars; crack vs scuff AUROC ≤ 0.45; axis-parallel lines lose visibility | DROP standalone; 3 and 4 jointly PARKED |
| 5 | Synthetic half-cuts (domain) | val cells made into half-cuts: FINAL crack recall 0.706 → 0.563, relR@2 0.887 → 0.774; matches E1's half-cut-without-scuff level, not scuff + half-cut | **PASS (narrowed)** → HC (§6.1) |
| 6 | Higher resolution (found) | 2x already run (Track M R5): n.d. at 4x compute; E1 cracks are labelled wider, not thinner | DROP |
| 7 | Cell-level and operating-point metrics (calib) | scorer validated; per-run b_comp unstable (seed sd 1.1 to 2.8) → arm-level pooled OP | PASS (in every protocol) |
| 8 | Foundation encoder (found) | P8 probe (§3.4); wrapper `hrstem_unetpp` | **PASS** (probe descriptive; 2-seed PF screen is the kill gate) → A8 screen (§6.2) |
| 9 | Test-time adaptation (found) | BN-HC's gain is mostly a calibration shift; TENT expected to move crack the wrong way | TENT DROP; T9 → FAIL, **TTA closed** (§3.2) |
| 10 | AI-assisted labelling (found) | `_rf` crack labels: 75% of components < 5 px (Pratt 4%); SAM fails on cracks | crack DROP / trust-region PARK; scuff PARK; inactive S10 → PASS, method note (§3.3) |
| 11 | Appearance augmentation (domain) | E1 brightness / contrast inside house-jitter reach; histogram shape outside the train envelope for 60% of E1 half-cuts (descriptive) | no arm |

### 2.1 Data facts found on the way (E)
- **E1 crack labels are about 1.5x wider than train:** area / skeleton 3.66 px vs train 2.41 (judge, `judge/crack_width.py`); val 2.46 (judge recompute 1 Nov, log 21:01). Pixel E1 crack recall is partly a width readout, so protocols report width-robust E1 metrics (relR@2, component recall).
- **Hanifi H36 half-cut crack labels are unusable** (judge, 31 Oct 14:23): 1,792 px over 17 cells, 48% within 10 px of spacing / border / cut line; FINAL relR@2 0.036 (1 of 17 cells). **No labelled half-cut crack set exists outside E1.** R4 (Track M) trained on these cells, which may explain its null (protocol_HC §2, S).
- **Where E1's crack is:** 75% of E1 crack px are in the 29 scuff + half-cut cells; 5% in the 40 plain full cells.
- **The letterbox:** E1's "brighter" statistic is the white frame (padding fraction 0.40 vs train 0.17); on content px E1 matches train (mean of cell means 137.3 vs 136.5).
- **Within E1 strata the crack failure is ranking, not threshold;** across strata there is a large cell-type offset on E1's own labels (half-cut b +5.4 vs full −0.8, oracle, descriptive). It is not reproduced by simulation (§3.1).

## 3. Pre-registered CPU checks
### 3.1 Half-cut routing pre-check: FAIL (`ideas/routing_precheck.md`; rule and cross-fit term R1 written before any number)
| Model | b_V0 | b_SHV1 | Δb (≥ 1.0) | G (≥ 0.02) | G_cf (≥ 0.01) | max relR@2 at relP@2 ≥ 0.90, V0 vs SHV1 |
|---|---|---|---|---|---|---|
| FINAL | +1.1 | +1.5 | +0.4 | +0.008 | +0.002 | 0.892 vs 0.730 |
| SUP100-PF s0-4 pooled | +2.9 | +3.8 | +0.9 | +0.001 | −0.003 | 0.876 vs 0.694 |
- On simulated half-cuts the models lose ranking, not calibration. A synthetic-val selector would pick about the full-cell bias, so PF2's routed E1 readout (§13) was declared void and never computed. Routing is PARKED behind a labelled half-cut set with E1-like context (judge: a cleaned H36 would likely not show the offset either).
- domain's label-free half-cut detector (R1 failed its FP target; R2b frozen, MANIFEST b8badda4) is parked with it; held-out FP on val 5.6%, so not a deployable router.

### 3.2 T9: per-panel BN statistics on `_rf` panels: FAIL, TTA closed (`ideas/t9_prereg.md`)
| Family | Variant | ΔAP on P (36 cells, 24 modules) | H36 crack-free FA px |
|---|---|---|---|
| FINAL (+0.75) | V2 all BN | +0.010 | 580 → 1,769 |
| FINAL | V3 shallow | +0.015 | 580 → 427 |
| SUPPF5 (val OP) | V2 | −0.000 | 31 → 2,214 |
| SUPPF5 | V3 | +0.016 | 31 → 319 (bound 231) |
- Every variant fails the +0.03 term; the module-bootstrap and sign terms fail too. Re-running D's BN-HC on H36 raises false alarms again (FINAL 580 → 1,810). Thesis line (judge): test-time BN adaptation, global (D) or per panel (T9), does not improve unseen-panel crack ranking and raises false alarms; entropy-minimisation TTA was not run (literature and A13).

### 3.3 S10: SAM inactive masks (A50 out-of-fold, 239 cells, 22 with inactive): PASS by its rule
- SAM masks prompted by the model vs the model's own masks, against Pratt labels: pooled IoU 0.4925 → 0.5653 (+0.073, paired cell bootstrap [+0.013, +0.135]); model AND SAM −0.006 (FAIL). Recall 0.542 → 0.669 at precision 0.842 → 0.785; boundary F1 flat; false area on cells without inactive +28%; val (6 cells, report-only) −0.039.
- Reading (found, judge): SAM is a region expander, not a sharpener. A50 only, 2 comparisons uncorrected. Method note; no training arm.

### 3.4 P8 probe: frozen encoders + linear probe (descriptive; no test, no E1; `idea08_foundation.md` §4c-4d)
| Encoder | F51 crack AP | val crack AP | H36 crack-free FA px |
|---|---|---|---|
| IN R50 | **0.444** | 0.36 | 3-11 |
| DINOv3 ConvNeXt-T | 0.363 | 0.35 | 216-282 |
| IN-1k ConvNeXt-T | 0.310 | 0.33 | 95-167 |
| SUP100-PF s0 encoder | 0.295 | 0.27 | 1,030-1,097 |
| SUP100-g s0 encoder | 0.274 | 0.25 | 352-495 |
| DINOv3 ViT-S/16 (1024 px) | 0.212 | 0.31 | 53-143 |
| SAM2 Hiera-T | 0.198 | 0.25-0.26 | 698-921 |
| DINOv2-S/14 | 0.173 | 0.17 | 0 |
| IN R34 (house) | 0.158 | 0.20 | 1,432-1,700 |
| DINOv3 ViT-S/16 (512 px) | 0.147 | 0.19-0.21 | 0 |
- Pick rule (bar 0.424): nothing qualifies; DINOv3 ConvNeXt-T enters the screen by rule as Om's named encoder; SAM2 and ViT out. DINOv3 CNX-T beats IN-1k CNX-T by +0.053 (seed ranges disjoint), with more false alarms. Frozen-probe gains have not carried to fine-tuning before (D1 → R3); the screen is the test.

## 4. PF2: the PF recipe on new seeds (E, `verify_pf2.md`; coach recompute, runner CONFIRMED to 4 dp)
**Design.** SUP100-g / SUP100-PF / RN50-PF, seeds 5 to 9, 20k steps, all 478 labels, gaint e544133. PF2 contrast: 5 co-primaries (3 test, two-set rule; E1 crack recall and E1 inactive IoU, direction stated). RN contrast: 3 test primaries. Ran 31 Oct 14:29 to 1 Nov 06:32 (15 rc 0); opened 06:33 to 08:26 (E1 opening #1).

| Contrast | Metric | Δ (thr) | Read |
|---|---|---|---|
| SUP100-PF − SUP100-g | E1 inactive IoU | 0.0481 → 0.2371, +0.1890 (0.0433) | **BETTER** |
| | E1 crack recall | 0.1715 → 0.1986, +0.0271 (0.0370) | n.d. |
| | test crack relF1@2 (all 50 / clean) | +0.0117 / +0.0120 (0.0100) | **BETTER, narrow** |
| | test crack IoU | −0.0011 / −0.0009 | n.d. |
| | test inactive IoU | +0.0173 / +0.0171 (~0.029) | n.d. |
| RN50-PF − SUP100-PF | test inactive IoU | −0.0289 (0.0251) both sets | **WORSE: FAIL** |
| | test crack IoU / relF1@2 | −0.0056 / −0.0028 | n.d. |

- **PF2 PASS.** "PF lifts E1 inactive IoU, replicated on new seeds, same E1 cells"; E1 crack recall not replicated (same sign). PF 5 / 5 seeds 0.207-0.279 vs house 0.025-0.089 on E1 inactive; the gain is concentrated on half-cuts (58 cells: 0.162 → 0.537).
- **The test relF1@2 pass is narrow:** bootstrap +0.0117 [−0.0034, +0.0292], P(Δ > 0) 0.93; leave-top-3-out +0.0015. Supporting: relR@2 at relP@2 ≥ 0.90 (B5) +0.034 in both sets; seeds 0 to 4 had the same sign.
- **RN closed:** the pre-stated risk (Track M R3 −0.025 inactive) repeated. D's house-RN50 E1 lead did not carry over under PF (scuff + half-cut recall −0.0225 singles, −0.025 ensembles at +0.75).
- **Anomaly (descriptive):** RN50-PF s5's layer4 hardly trained (cosine 0.998, norm ratio 1.00 at 20k vs 1.10-1.12 for s6-9), same schedule; not an inactive outlier.
- **Decides (S):** BEST stays SUP100-PF; the encoder gate is closed for RN50 under PF.

## 5. PF2E: PF vs house as deployable ensembles (E, `verify_pf2e.md`; E1 opening #4)
- Inference only (gaint CPU fp32), E-PF = pf2_SUPPF s5-9 vs E-g = pf2_SUP s5-9, mean softmax. The verdict uses each ensemble's headline b; clarified 19:04:56 IST with the output folder empty, before the val decisions file (19:05:49). D2 chose b 1.25 / 1.5; both tripped the val width flag (val crack precision drop +0.0543 / +0.0753), so **the verdict is at b 0 (argmax)**.

| Primary | E-g | E-PF | Δ [95% CI] | Read |
|---|---|---|---|---|
| test crack IoU | 0.4788 | 0.4815 | +0.0027 [−0.0146, +0.0159] | n.d. |
| test relF1@2 | 0.8821 | 0.8942 | +0.0121 [−0.0048, +0.0309] | n.d. |
| test inactive IoU | 0.4376 | 0.4613 | +0.0237 [−0.0310, +0.0971] | n.d. |
| E1 crack relF1@2 (71-cluster bootstrap) | 0.3990 | 0.4345 | +0.0355 [−0.0232, +0.0912] | n.d. |
| **E1 inactive IoU** | 0.0665 | 0.2807 | **+0.2141 [+0.0303, +0.3820]** | **PASS** |

- **judge's qualifications (go with the result everywhere):**
  1. E1 inactive GT: 9,158 px in 10 cells, 7 source images, n_eff 3.3.
  2. Half the gain is recall (0.304 → 0.627), half fewer false inactive px on module-border / frame-edge px of edge cells (32,654 → 11,315; three consecutive CSIR images).
  3. Leave-one-cluster-out Δ +0.138 to +0.277; family clustering keeps the LB > 0.
  4. Bonferroni 99% LB ≈ 0.000: borderline under correction.
  5. E1 crack precision falls (0.547 → 0.495); crack-free E1 px +18%.
- **Wording:** "fewer false inactive calls on module edges plus twice the inactive recall on E1". Not a broad unseen-panel inactive capability; not independent of PF2 (same members, same E1 cells).
- **FINAL:** E-PF reaches clean crack IoU 0.4920 (= FINAL's 0.492) only at its D2 b 1.5, which the pre-registered val width flag rejected (val crack precision drop +0.0753 > 0.05; on test, crack precision 0.670 → 0.584). At the verdict b it is 0.4846. **No "matches FINAL" claim;** FINAL is another machine and commit, descriptive only.
- **B5 (reported):** at val OPs, test component recall +0.032 and relR@2 +0.038 (E-PF over E-g), same direction as PF2's singles.
- **Recommendation (S, coach and judge):** E-PF is the better deployable candidate than E-g. The user decides.

## 6. Protocols armed at writing
### 6.0 THIN-B3 (`protocol_thin_b3.md` v1, locked 1 Nov 00:25, APPROVED 00:38)
- Three arms on SUP100-PF, seeds 5-9, comparator PF2's SUPPF s5-9 (bit-identity shown over 2,000 steps): **SKR** (Skeleton Recall, w 1; its r-2 tube covers 99.2% of train crack px, so it acts as a soft crack-recall term), **CLD** (soft-clDice, w 1, k 10), **B3** (scuff as its own class; scuff IoU 0.0 at 2k, so "not learned" is a stated risk).
- Co-primaries: test 3; for SKR / CLD also the two B5 OPs at the arm-pooled val OP; for all, E1 crack relF1@2 (E1 opening #2).
- 15 runs trained 06:32 to 19:39 1 Nov (rc 0); opened 19:40:18 to 21:13:45 (E1 opening #2).
- **Results (added 1 Nov ~21:40; `verify_thin_b3.md`, coach recompute, judge CONFIRMED with corrected readings): no arm passes; BEST stays SUP100-PF.**

| Co-primary (Δ vs SUP100-PF; all / clean) | SKR | CLD | B3 |
|---|---|---|---|
| test crack IoU (thr 0.0100) | **−0.0136 / −0.0140 WORSE** | −0.0041 / −0.0042 n.d. | +0.0009 / +0.0016 n.d. |
| test crack relF1@2 | +0.0028 / +0.0028 n.d. | −0.0020 / −0.0018 n.d. | −0.0008 / +0.0001 n.d. |
| test inactive IoU | −0.0170 / −0.0161 n.d. | −0.0114 / −0.0106 n.d. | −0.0099 / −0.0095 n.d. |
| B5 comp recall at comp P ≥ 0.90 | **+0.0413 / +0.0417 BETTER** (thr 0.032) | −0.0180 / −0.0182 n.d. | (reported) |
| B5 relR@2 at relP@2 ≥ 0.90 | +0.0114 / +0.0116 n.d. (OP unreachable on val) | **−0.0374 / −0.0376 WORSE** (thr 0.015) | (reported) |
| E1 crack relF1@2 | **+0.0590 BETTER** (thr 0.0392) | +0.0367 n.d. | +0.0013 n.d. |
| Verdict | **FAIL** | **FAIL** | **n.d.** |

  - **SKR:** the test WORSE is narrow (bootstrap [−0.036, +0.012]; leave-top-3-out +0.010). Mechanism (judge): precision from wider predictions (test pred/GT 0.95 → 1.54; relP@2 flag −0.070), concentrated on the largest cracks; not twins in the comparator (CLD shows the same split, and both arms trained on the same twins). On E1 it is the first clear crack-detection lift: relF1@2 +0.059, any-hit component recall 0.381 → 0.523, relR@2 +0.142. Its price: crack px on crack-free E1 cells ×2.4, crack on E1 scuff ×2.0, relP@2 −0.059. E1 pixel recall and IoU are not quoted: SKR's ~1.5x wider masks meet E1's ~1.5x wider labels (doc 13 A17).
  - **CLD:** no better at matched precision. The B5 WORSE comes from a val-chosen operating point that does not transfer (over-precise on test: relP@2 0.932 vs 0.900); at matched test precision 0.868 vs 0.873 (descriptive).
  - **B3:** the scuff class is not learned (train scuff IoU 0.000, all 5 seeds; never predicted). The arm is a 649-px crack → background relabel; its E1 crack-on-scuff drop (−7.3%) is not scuff-specific (crack off the scuff in the same cells −32%). Closed as spec'd.
  - **Next (S):** an SKR follow-up is the user's call: a new protocol with weight 0.1 or a val OP on a wider grid, a precision guard as a co-primary, and a width-insensitive E1 detection readout.
### 6.1 HC: synthetic half-cuts (`protocol_HC.md` v1.1)
- HC − SUP100-PF, seeds 5-9; loader transform at p 0.35 per eligible sample (~26% of views) from 353 train cells with a realistic gap band. Co-primaries: test 3, E1 crack relF1@2, E1 inactive IoU (E1 opening #3). Mechanism kill: SHV1 relR@2 at relP@2 ≥ 0.90 gain < +0.05. Harm guard on F51.
- Code reviewed independently (found: PASS); smoke H0 identical to SUP100-PF over 2,000 steps. Queued after THIN-B3; opening trigger armed.
### 6.2 A8 screen: DINOv3 ConvNeXt-T under PF (`protocol_A8screen.md` v1.1)
- A8 (DINOv3 weights) vs A8c (IN-1k weights), same wrapper, 2 seeds, complete 4k schedule. GO only if F51 crack AP gains with a module-bootstrap LB > 0, val crack AP not worse by > 0.02, false alarms bounded. No test, no E1 (a per-run data root makes the trainer's end-of-run test pass score val). KILL closes "foundation encoder" for the thesis.
- DINOv3 weights fetched by the user's route B ("B: I accept, fetch timm"; licence accepted by the user).
### 6.3 B6: module-grouped CV for inactive (`protocol_B6.md`; v1.0.1 = the v1 design locked at judge's sign-off, plus two asserts / notes)
- PF − house inactive IoU on held-out physical modules: 5 folds over train + val (532 cells), 2 seeds, 20 runs; groups merge CFVS time-series twins (judge found image-id folds leak them and favour PF).
- **Power, stated before any run:** ~13% at Δ +0.017, 80% at ~+0.055. n.d. is likely. The user: run only on cv02 if ≥ 3 GPUs qualify; never on gaint; reported as low-powered.

## 7. Item 13 closed (`team_2026-10-29_features/pool_large/CLOSED.md`)
No download of the 159k HF pool. Use A (thesis negative result): the pool has no E1 module family, no new half-cells, 84% of new rows one ARTS mono type, so unlabelled-data methods cannot close the unseen-panel gap through it. Use B (provenance): byte copies under other IDs, test cells in it by ID, no licence; ID rules alone are not a dedupe.

## 8. The E1 openings ledger (`e1_openings.md`)
| # | Protocol | E1 co-primaries | Opened | Result |
|---|---|---|---|---|
| 1 | PF2 | E1 crack recall, E1 inactive IoU | 1 Nov 06:33-08:26 | inactive BETTER; crack n.d. |
| 2 | THIN-B3 | E1 crack relF1@2 | 1 Nov 19:40-21:13 | SKR +0.059 BETTER; CLD, B3 n.d. (no arm passes overall) |
| 3 | HC | E1 crack relF1@2, E1 inactive IoU | armed | |
| 4 | PF2E | E1 crack relF1@2, E1 inactive IoU | 1 Nov 19:02-19:13 | inactive PASS; relF1@2 n.d. |
- **Multiplicity:** co-primaries are uncorrected within each protocol (disclosed) and across openings; #4 repeats #1's models and cells. Reusing PF2's opened comparator files in #2 and #3 is not a new read. FINAL and protocol_100 seeds 0-4 are not blind on E1.

## 9. Incidents
In doc 13 D34 to D45: PF2's LA scoring peak (7,758 MiB; min free 2,635, floor held), builder's quarantined test / E1-scuff read and GPU-context slip, judge's tail of THIN stdouts, test images touched for structure, usage-cap respawns, laptop memory pressure, `set -e` chained checks, smaller slips.

---

## Related docs
- `19_feature_learning_and_100pct_plan.md` §10: protocol_100 and D, the starting point.
- `11_results_synthesis_and_claims.md`: rows 30 to 42.
- `12_decisions_log.md`: §4f, D62 to D78.
- `13_problems_pitfalls_open_issues.md`: A16, A17, C18, C19, D34 to D45, E26 to E30.
- `14_code_and_infrastructure.md` §1.2d, §5c.
- `15_status_remaining_work.md` §1i, §3d, §4d.
- `16_faq_for_the_guide.md` section I (Q42 to Q51).
