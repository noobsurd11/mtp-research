# 21. A8 screen, HC, B6, SKR2 / HC2, SKR2E, Om's A1-A6 and the B2 agent raters (1 Nov to 3 Nov 2026)

## What this covers
This file covers 1 Nov ~21:40 to 3 Nov ~02:40 IST, after `20_pf2_and_domain_ideas.md`:
- **A8 screen:** DINOv3 ConvNeXt-T vs IN-1k ConvNeXt-T under PF (idea 8's kill gate): KILL.
- **HC:** training on synthetic half-cuts (idea 5): n.d.; E1 opening #3.
- **B6:** is PF's inactive gain also in-distribution? Module-grouped CV on cv02: n.d., and weaker than planned.
- **SKR2 and HC2:** Skeleton Recall at w 0.1 (PASS, narrow) and half-cuts with inactive ignored in synthetic views (FAIL); E1 opening #5.
- **SKR2E:** the SKR2 ensemble vs the PF ensemble as deployable models: FAIL; E-PF stays the recommended candidate; E1 opening #6.
- **Om's architecture ideas A1-A6:** validated on CPU; all DROP, A4 PARK.
- **B2 agent raters:** two agent raters tried to replace the user's B2 marks: calibration FAIL on scuff.
- **SKR2C:** SKR2 on fresh seeds 10-14: protocol locked 3 Nov 02:37; training only tonight once APPROVED; opening on the user's OK.

Added 3 Nov 2026. **Tags.** E = measured (file), R = literature (Research MCP id), S = judgement. "Clean" = the 50 test cells without `CSIR_00070_r8_c4`. Rule 1 = house rule, divisor 3. SUPPF = SUP100-PF, seeds 5-9 (PF2's files, the shared comparator). **Verdicts are the pre-registered ones; readings are labelled and kept apart.**

**Status at writing (3 Nov 2026, ~02:40 IST)**

| Item | Verdict | Where |
|---|---|---|
| A8 screen | **KILL** (coach 1 Nov 23:35; judge CONFIRMED 23:40) | `team_2026-10-31_next/verify_a8screen.md` |
| HC (E1 #3) | **n.d.**; mechanism passed; F51 guard passed (coach 2 Nov 03:14; judge CONFIRMED 03:18) | `verify_hc.md` |
| B6 | **n.d.**; realised power ~6% at +0.017 (coach 22:18; judge CONFIRMED 22:19) | `verify_b6.md` |
| SKR2 (E1 #5) | **PASS**, narrow (E1 crack relF1@2) | `verify_skr2_hc2.md` |
| HC2 (E1 #5) | **FAIL** by G1 (test inactive); mechanism failed | `verify_skr2_hc2.md` |
| SKR2E (E1 #6) | **FAIL** by G2a + G2b at the headline pair; E-PF stays the recommended candidate | `verify_skr2e.md` |
| A1-A6 | all DROP, A4 PARK (judge 2 Nov 11:43) | `ideas/arch_A1.md` to `arch_A6.md` |
| B2 agent raters | calibration FAIL (scuff gate); no agent marks | `ideas/b2_agent_marking_prereg.md`, log 2 Nov 11:49 |
| SKR2C | protocol v1 LOCKED 02:37 (judge signed); guard / queue code NOT READY at judge's stage-1 review (02:38), APPROVED held; training only tonight; E1 #7 registered, not opened | `protocol_SKR2C.md`, `judge/review_s2c_stage1_code.md`, log 3 Nov 02:21-02:43 [12 Nov: launched 03:06 after judge accepted the fixed code (02:58, ddf09a9f); ALL TRAINED 11:24:04, 10 rc 0 of 10, no guard trigger; not scored; E1 #7 still not opened] |

## Sources
- `SESSION_RECORD_2026-11-01_to_11-03.md` (master for this session).
- `team_2026-10-31_next/`: `log.md` (from 1 Nov 21:30), `e1_openings.md`, `om_2026-11-01_arch.md`; protocols `protocol_A8screen.md`, `protocol_HC.md`, `protocol_B6.md`, `protocol_SKR2_HC2.md`, `protocol_SKR2E.md` (and the superseded sketch `protocol_SKR2.md`); builds `build_b6.md`, `build_hc2.md`, `build_s2_runner.md`, `build_skr2e.md`; verifications `verify_a8screen.md`, `verify_hc.md`, `verify_b6.md`, `verify_skr2_hc2.md`, `verify_skr2e.md` (each with judge's section); judge's reviews `judge/review_SKR2_HC2_v09.md`, `judge/review_SKR2E_v09.md`, `judge/review_b2_agent_marking_pre.md`; `ideas/arch_A*.md`, `ideas/b2_agent_marking_prereg.md`.
- Copies of the markdown files: `sources/teams/team_2026-10-31_next/`; the session record: `sources/session_records/`.

Where a session record and a verify file disagree, the verify file is used.

---

## 0. Terms used here
- **Headline b:** an ensemble's deployed crack bias. The D2 rule picks b on val; if that b trips the **val width flag** (val crack pixel precision drops by > 0.05), the headline b is 0 (argmax).
- **Any-hit component recall:** share of GT crack components ≥ 20 px with ≥ 1 predicted px within 2 px. Width-insensitive, unlike pixel recall (E1 labels are ~1.5x wider than train, doc 13 A17).
- **SHV1:** domain's frozen synthetic half-cut val set (108 images from the 54 val cells), used as HC's non-E1 mechanism check (doc 20 §3.1).
- **F51 / H36:** Hanifi `_rf` unseen-module full cells (51; 12 crack cells) and half-cuts (36; false alarms on 19 crack-free cells only, doc 13 A16).
- **Seed-aware two-stage bootstrap:** resample clusters (modules or E1 images), then draw seeds with replacement per arm. It includes seed noise, unlike a bootstrap with the trained models fixed.
- **Guards (G1, G2, G3):** pre-registered FAIL rules in protocol_SKR2_HC2 and SKR2E; any trip fails the arm whatever else passes.

## 1. A8 screen: DINOv3 under PF (`protocol_A8screen.md` v1.1; `verify_a8screen.md`)
- **Design (E):** A8 (DINOv3 ConvNeXt-T-PF) vs A8c (IN-1k ConvNeXt-T-PF), seeds 0-1, 4k steps, el_f8 c280e8c2; no test, no E1 (data root with test.txt = val). Trained 1 Nov 21:15-22:55; CPU scoring 22:56-23:02 (MANIFEST 3cdd7286). Both arms VALID (encoder stages 2-3 cosine to init 0.98-0.999).
- **GO rule and result:**

| Term (seed means) | Value | Result |
|---|---|---|
| F51 crack AP A8 − A8c > 0 | 0.5448 − 0.5691 = **−0.0243** | FAIL |
| F51 36-module bootstrap lower bound > 0 | **−0.0463** [hi +0.0454] | FAIL |
| val crack AP ≥ A8c − 0.02 | Δ −0.0041 | pass |
| false alarms ≤ max(1.5x, +200 px) on H36 / F51 crack-free | 92 vs 28 / 392 vs 201 | pass, only via the +200 px floor |

- **Verdict: KILL.** By protocol §5 (fixed before the screen), "foundation encoder" is closed for the thesis: no larger download, no A8 full arm.
- **Reading (judge, S with E):** KILL means "no sign of a gain", not "DINOv3 is worse". F51 is 76% one cell (`CSIR_00073_r9_c3_rf`); leave-one-crack-module-out is negative for all 12; seed-aware bootstrap [−0.069, +0.047]; A8c's own seed spread (0.067) exceeds the arm gap. The frozen-probe edge of DINOv3 over IN-1k (+0.053 F51 AP, doc 20 §3.4) did not carry into PF fine-tuning.
- **Pitfall:** with test.txt = val.txt, each run's metrics.json `test_*` blocks are val numbers under a test label (doc 13 C21).

## 2. HC: synthetic half-cuts (`protocol_HC.md` v1.1; `verify_hc.md`; E1 opening #3)
- **Runs (E):** HC = SUPPF + `data.synth_halfcut` p 0.35 (353 rule_p sources; ~26% synthetic views), el_hc c2e6973, seeds 5-9, trained 1 Nov 21:41 to 2 Nov 02:17. Opening 2 Nov 02:18:34-03:09:57 (MANIFEST d5c39e0d).

| Co-primary (Δ HC − SUPPF; all 50 / clean; thr) | Value | Result |
|---|---|---|
| test crack IoU | +0.0092 / +0.0089 (0.0100) | n.d. |
| test crack relF1@2 | +0.0026 / +0.0023 | n.d. |
| test inactive IoU | −0.0228 / −0.0230 (0.0289) | n.d. |
| E1 crack relF1@2 | +0.0135 (0.0429) | n.d. |
| E1 inactive IoU | −0.0002 (0.0572) | n.d. |

- **Verdict: n.d.** Mechanism passed: SHV1 matched relR@2 at relP@2 ≥ 0.90, HC 0.8192 vs SUPPF 0.6959 (+0.1233; kill < +0.05), seed ranges disjoint; the half-cut bias gap +1.1 → −0.5. F51 harm guard passed (crack AP 0.5371 vs 0.4702, +0.0669, module bootstrap [+0.0125, +0.0867]).
- **judge's corrections (in the verify):**
  - **Test inactive leans worse, n.d.:** the fixed-model bootstraps exclude 0, but the **seed-aware two-stage bootstrap is [−0.054, +0.005]**, P(Δ < 0) 0.95; broad (11 of 16 inactive cells down).
  - **Test crack leans better, n.d.:** seed-aware [−0.002, +0.023], P 0.94; +5% predicted volume. No BETTER labels on unregistered subsets.
  - **The F51 crack AP gain is coverage on the 12 crack cells** (+0.0597 from them alone; pred/GT 0.90 → 1.13; relP@2 unchanged), **not fewer false alarms.**
  - **False alarms:** H36 crack-free half-cuts 11 vs 278 px at b_rel, every seed (robust); F51 crack-free 122 vs 1,231 is fragile (one cell holds 71-96% of each SUPPF run's FA).
  - **E1:** the relF1@2 +0.0135 is precision-led (relP@2 +0.029; any-hit 0.381 → 0.377); half-cuts without scuff gain volume (+27%) on 11 components, detection +0.6 component per seed (n.d.).
- **Reading (S):** the simulator mechanism works, real E1 half-cuts do not move, and test crack and test inactive lean ~0.02 in opposite directions. Any follow-up needs a test-inactive guard (which became SKR2_HC2's G1).

## 3. B6: is PF's inactive gain in-distribution? (`protocol_B6.md`; `build_b6.md`; `verify_b6.md`)
- **Design (E):** PF vs house, 5-fold CV over train + val (532 cells) grouped by judge's physical-module groups (CFVS twins merged), 2 seeds, 20 runs; per-fold data roots so the trainer's test pass sees only the held-out fold. Training on cv02 only; scoring on gaint (user, 1 Nov 23:54). Primary: pooled out-of-fold inactive IoU; two-stage bootstrap (groups, then seed per (fold, arm)); PASS = lower bound > 0 and Δ ≥ 0.01.
- **Build and run (E):** fold roots 0 test / 0 E1 stems; scorer GPU exact check 54/54 identical (2 Nov 01:23); APPROVED 01:29; cv02 qualified 13:30; A6000 identity PASS; 20 runs rc 0 (ALL TRAINED 21:31 IST); relay to gaint; one bf16 scoring pass 22:11-22:13 (MANIFEST 960ce11a).
- **Result:** house 0.4992 / 0.5193 vs PF 0.4996 / 0.4901 (seeds 5 / 6); **Δ −0.0144, CI [−0.0977, +0.0570]: n.d.**
- **Power, as realised (judge's correction):** the planned SE 0.020 (judge's own estimate) became **0.038-0.039**: groups alone 0.031 (out-of-fold cells are scored by a different model pair in each fold, which the estimate ignored) plus seeds ~0.022. **Realised power ~6% at +0.017** (13% stated before the run), 26% at +0.05; 80% needs ~+0.11.
- **What it says:** it cannot tell test's +0.017 from 0 or from −0.05, but it **does exclude an in-distribution gain as large as PF's E1 gain** (CI hi +0.06 vs +0.19 singles / +0.21 ensemble). So PF's inactive advantage stays an unseen-panel (E1) result; no in-distribution null is claimed.
- Reported: CFVS (78% of inactive px) flat (+0.0007); inactive components lean PF (recall +0.058, precision +0.106; two seeds, no label); classes absent from a fold's training set get 0 px predicted inactive.

## 4. SKR2 and HC2 (`protocol_SKR2_HC2.md`; `verify_skr2_hc2.md`; E1 opening #5)
### 4.1 The two arms and the guards
- **SKR2** = SUPPF + Skeleton Recall at **w 0.1** (THIN-B3's SKR was w 1.0: it failed on test through wider masks but lifted E1 detection, doc 20 §6.0). el_thin c9bbb02. 7 co-primaries: test 3, B5 component recall and relR@2 on a wider bias grid (−8 to +12), E1 crack relF1@2, E1 any-hit.
- **HC2** = HC with inactive px set to ignore (255) in synthetic views only (el_hc2 0405151). 5 co-primaries as HC; mechanism kill as HC.
- **Guards:** G1 test inactive Δ ≤ −0.015 in both sets (both arms); G2 test relP@2 Δ < −0.03 or E1 crack px on the 74 crack-free cells > 1.5x SUPPF (SKR2); G3 F51 AP upper bound < 0 (HC2).
- **HC2's design history (E, 2 Nov 11:21-14:33):** (1) half HC's dose, p 0.175 (coach v0.9); (2) judge: a half dose cannot separate dose from cause → exclude inactive-bearing sources (35 of 353), p 0.35 (team-lead D1); (3) judge: those sources hold ~58% of the crack px of their families → team-lead's pre-set rule: exclude only if crack-px retention ≥ 60%, else ignore inactive px in synthetic views; (4) builder measured retention 0.399 / 0.359 → **(a2) ignore variant**, ~0.21% of synthetic px relabelled. GPU H0 identical over 1,000 steps; smoke clean; v1.1 locked 14:33. The user then chose "run HC2 as built" (17:58).

### 4.2 Results
| Co-primary (Δ vs SUPPF; thr) | SKR2 | HC2 |
|---|---|---|
| test crack IoU (all / clean) | +0.0091 / +0.0088 (0.0100) n.d. | +0.0033 / +0.0064 n.d. |
| test crack relF1@2 | +0.0089 / +0.0085 n.d. | −0.0032 / +0.0006 n.d. |
| test inactive IoU | +0.0099 / +0.0102 n.d. | −0.0256 / −0.0259 n.d. |
| B5 comp recall / relR@2 (wide grid) | +0.0169 / +0.0094 n.d. | (reported) |
| E1 crack relF1@2 | **+0.0364 (0.0351) BETTER** | +0.0074 n.d. |
| E1 any-hit | +0.0439 (0.0521) n.d. | |
| E1 inactive IoU | | −0.0795 (0.0830) n.d. |
| Guards | G1 ok; G2 ok (relP@2 −0.0121; E1 crack-free ×0.97) | **G1 TRIP**; G3 ok (+0.0376) |
| **Verdict** | **PASS** | **FAIL (G1)** |

### 4.3 SKR2: a narrow pass, a robust effect (judge)
- **The BETTER label is fragile:** margin 0.0013; leave-one-seed-out keeps it in 5 of 10 drops, leave-one-E1-image-out in 65 of 71.
- **The effect is robust:** seed-aware [+0.004, +0.076], P 0.985.
- **It is not a bias shift:** SUPPF's best constant bias on E1 (E1-oracle, descriptive) reaches 0.4289, below SKR2's 0.4567 at b 0; at equal E1 predicted volume SKR2 leads (relF1@2 +0.031, any-hit +0.024) with fewer false-alarm px.
- **w 0.1 vs w 1.0:** about a third of the detection gain (any-hit +0.044 vs +0.142), none of the false alarms (E1 crack-free px ×0.97 vs ×2.40; test relP@2 −0.012 vs −0.070).
- Claimable: "SKR w 0.1 passes: E1 crack relF1@2 BETTER (+0.036), no test cost, no precision-guard trip." Not claimable: "E1 detection BETTER" (any-hit n.d.), "test BETTER".

### 4.4 HC2: why it failed, and what stays open
- **G1 trip:** test inactive −0.0256 / −0.0259 (HC was −0.0228 / −0.0230). HC2 − HC −0.003, against +0.023 for full recovery (P(full) 0.12).
- **Mechanism FAILED:** HC2 never reaches relP@2 0.90 on SHV1 (max 0.776), so the registered matched recall does not exist (coach's ruling on the frozen "coach decides" case; judge agrees). Post hoc descriptive readout: on the 11 SHV1 views per run that hold inactive, HC2 predicts almost no inactive (IoU 0.002 vs HC 0.386) and ×5.1 off-GT crack px; on the other 97 views HC2 ≈ HC. The cause is not shown (judge: "no support, cannot exclude" for the label reading).
- **Label vs dilution is not decided:** (a2) also lowers predicted inactive on test and E1, so it cannot exclude the synthetic-label cause; dilution is not shown either.
- **§7 (a2) was formally triggered** ("mechanism failed at full crack dose → the HC route closes"); coach and judge recommended not applying it (a post hoc reason). **The user kept the HC route OPEN; only the (a2) ignore design is closed** (2 Nov 21:51).
- **E1 inactive is a 3-image readout:** the top 3 source images hold 87% of 9,158 GT px (effective n 3.3).

## 5. SKR2E: the SKR2 ensemble as a deployable model (`protocol_SKR2E.md`; `verify_skr2e.md`; E1 opening #6)
- **Design (E):** E-SKR2 (SKR2 s5-9) vs E-PF (SUPPF s5-9; PF2E's ensemble, identity-checked), mean softmax, gaint CPU. judge's review made the verdict use a **shared b 0** for both arms, with every guard also checked at the **headline pair** (each arm at its own headline b); any trip fails. Locked 2 Nov 21:59; run 22:24:38-22:36:52.
- **Val decisions:** E-PF D2 b 1.5, width drop 0.0753 → headline b 0. **E-SKR2 D2 b 1.0, width drop 0.0485 ≤ 0.05 → headline b 1.0.**

| At b 0 | E-PF | E-SKR2 | Δ [CI] |
|---|---|---|---|
| test crack IoU | 0.4815 | 0.4917 | +0.0102 [+0.0031, +0.0197] pass |
| test crack relF1@2 | 0.8942 | 0.9046 | +0.0104 [+0.0016, +0.0232] pass |
| test inactive IoU | 0.4613 | 0.4662 | +0.0050 n.d. |
| E1 crack relF1@2 | 0.4345 | 0.4698 | +0.0353 [+0.0102, +0.0613] pass |
| E1 any-hit | 102/296 | 122/296 | +0.0676 pass |

- **Guards at the headline pair (E-PF b 0 vs E-SKR2 b 1.0):** G2a test relP@2 **−0.0379** (< −0.03) TRIP; G2b E1 crack-free px **5,358 vs 2,528 (×2.12)** TRIP. At b 0 no guard trips.
- **Verdict: FAIL.** E-PF at argmax stays the recommended deployable candidate (coach and judge, PF2E); the user's adoption is still open (doc 15 §3d row 19); SKR2E did not displace it. FINAL 0.492 (cv02) is not comparable by rule.
- **judge's points:**
  - **The width flag decided it by 0.0015.** With a drop above 0.05, E-SKR2's headline b would have been 0 and the verdict PASS. Against E-PF at b 0, G2b trips for every E-SKR2 headline b ≥ 0.5. This asymmetry was accepted at lock on purpose (it penalises a bias step).
  - **The b 0 passes are not a confirmation:** #6 re-measures #5's models; the opening failed.
  - **Bias share:** on test, E-PF at b 1 equals E-SKR2 at b 0 (−0.0002 / −0.0013), so the test pass is not distinguishable from a bias step. On E1, relF1@2 is a curve shift (+0.024 at matched volume); any-hit is 60% volume, and all 20 extra hits sit in scuff + half-cut cells of 6 images (n_eff 3.6).
  - E1 inactive −0.042 sits in 3 images; PF2E's E1 inactive gain (+0.214) must not be assumed for an SKR2 ensemble.
- **Reading (S, coach and judge):** at matched volume SKR2 adds a small, real-looking E1 relF1@2 gain concentrated in scuff + half-cut cells. Deploying E-SKR2 at b 0 would be an operating point picked after test and E1 were opened twice; no unopened set can confirm it. A change to the 0.05 width rule is a separate pre-registered question.

## 6. PF2's E1 inactive gain sits in 3 images (judge, 1 Nov 23:46)
- E1 inactive ground truth (9,158 px, 10 cells) lies in 7 source images; the top 3 (`CSIR_01637` 4 half-cut cells, `CSIR_01101`, `CSIR_01647`) hold **87%**.
- PF2's +0.189 (singles) shrinks to **+0.023 without them**; image-cluster 95% CI for the full gain [+0.023, +0.354] (E, `judge/out/hc_smoke_width_pf2.txt`, descriptive).
- Read every E1 inactive claim (PF2 row 30, PF2E row 34 in doc 11) with "a 3-image readout".

## 7. Om's architecture ideas A1-A6 (`om_2026-11-01_arch.md`; `ideas/arch_A*.md`)
Om wrote them on 1 Nov, before the A8 KILL, THIN-B3 and HC results. Agent `arch` checked each on CPU (val / `_rf` records; no test or E1 file opened); judge reproduced the key numbers.
| Idea | Why (E) | Verdict |
|---|---|---|
| A1 two-branch encoder (DINOv3 + high-res CNN) | the A8 screen plus a freeze and fusion; idea 8 closed by A8; HR branch = idea 6 DROP; its only side check is post hoc and confounded | DROP |
| A2 instance norm in early layers (IBN-Net) | the style premise is contradicted on non-E1 data (idea 2: content brightness = train) | DROP |
| A3 geometry-aware input | HC already removes cut-line false alarms on real half-cuts (H36 cut-line / spacing FP 123 → 3 px/run, SUPPF vs HC); no structure enrichment in misses | DROP |
| A4 structured crack head (centreline + direction + width) | fragments are ≤ 5-7% of non-E1 components; unseen-module loss is whole-component misses; E1 partial share 0.153 (~2x val) | PARK behind SKR2 |
| A5 long-range context | lowest rank, no support | DROP |
| A6 cell gate + pixel head | a cell gate cannot recover SKR's precision (its extra px are 99.6% inside crack cells); the val threshold is unstable across seeds | DROP as an arm |
- A4's revival condition (SKR2 passes G2 and keeps its E1 any-hit gain): SKR2 passed with G2 held, but any-hit was n.d. and SKR2E failed (S: not revived).

## 8. B2 agent raters (`ideas/b2_agent_marking_prereg.md` v2.2)
- **Why:** the user asked (2 Nov 11:26) why an agent cannot do the B2 marks (100 half-cell panels ranked for scuff / crack, doc 19 §8). Two agent raters were set up; the user's marks became optional.
- **Rules (judge, fixed before any mark):** whole 512 crop as the unit; name-free random-ID bundles with judge holding the key; calibration on 72 items: gate A crack on 40 house-labelled CSIR train cells (sens and spec ≥ 0.70, balanced-accuracy bootstrap lower bound > 0.5), gate B scuff on 32 Hanifi pool half-cells (sens ≥ 0.50, spec ≥ 0.70); raters see PASS / FAIL only. Two runs of one model measure consistency, not independent reliability.
- **Result:** both raters identical on the gates: **crack gate PASS** (sens 20/20, spec 17/20, BA lower bound 0.833) on house CSIR cells; **scuff gate FAIL** (sens 1/8, needs ≥ 4/8). Reported, not gated: on gate B's Hanifi half-cells the raters found 1 of 14 cracks (speck-level labels; reported, not gated). **No agent B2 marks.** B2 is unmarked and back with the user (doc 15 §3e). A crack-only agent prereg for the Hanifi B2 panels would rest on a gate that did not test Hanifi cracks.
- The 3 Hanifi B2 panel cells stay unnamed in `sources/` until the user marks B2 (`sync_sources.sh`).

## 9. The E1 openings ledger, continued (`e1_openings.md`)
| # | Protocol | E1 co-primaries | Opened | Result |
|---|---|---|---|---|
| 3 | HC | crack relF1@2, inactive IoU | 2 Nov 02:18-03:10 | both n.d. |
| 5 | SKR2_HC2 | SKR2: relF1@2, any-hit; HC2: relF1@2, inactive | 2 Nov 20:01-21:23 | SKR2 relF1@2 +0.0364 BETTER; others n.d. |
| 6 | SKR2E | relF1@2, any-hit at shared b 0 (+ guards at b 0 and the headline pair) | 2 Nov 22:24-22:36 | both pass at b 0; the opening FAILS by guards at the headline pair |
- **Multiplicity (S):** six registered openings so far, each with uncorrected co-primaries. #4 repeats #1's members; #6 repeats #5's. SKR2's single pass is 0.0013 over its bar; read it with the ~10% family-wise false-BETTER rate over its 7 co-primaries. SKR2C (fresh seeds 10-14) would be the first fresh-seed replication of a passing E1 crack result (same 106 E1 cells: it replicates seeds, not cells), as E1 opening #7, if the user OKs it.

## 10. SKR2C (state at writing, from `log.md` 3 Nov 02:21-02:37; `protocol_SKR2C.md` v1, locked 02:37)
- **Question:** does SKR2's E1 gain hold on **fresh seeds 10-14** (SKR2 w 0.1 vs SUPPF, 10 runs on gaint)? It replicates seeds, not cells: test and E1 are the same cells as #5 and #6 (a third look, disclosed).
- **Verdicts at the opening:** R = SKR2_HC2's rule-1 singles set at argmax (7 co-primaries, G1 / G2); D = the two ensembles at a shared b 0 (SKR2E's set). Both PASS → recommend; either FAIL → SUP100-PF stays. The named replication claim needs a seed-aware two-stage bootstrap. Stated chances: R PASS ~35-65% (judge's Monte Carlo: 0.90 / 0.64 / 0.34 / 0.05 if the true effects are 1 / 0.75 / 0.5 / 0 times #5's); seed-aware replication ~25-45%.
- **Training reads no test cell:** one data root (`/home/noob/work/s2c_root`, test.txt = val), verified 02:37 by a data-build line and a CPU identity check for both arms.
- **Unattended safety:** at most 2 lanes (team-lead's call), gate = measured peak + 2,048 MiB, ≥ 120 s apart, 1 s memory log; new starts HOLD while an outside GPU process holds > 1 GB; a guard stops only the newest running SKR2C run, by its verified python PID, if free < 2,048 MiB on 3 consecutive 1 s samples (at most 2 stops), then HOLD; default after a stop: rerun from scratch.
- **Not launched at writing:** judge's stage-1 code review (02:38, `judge/review_s2c_stage1_code.md`) found the guard and queue NOT READY (7 must-fixes): the outside-process HOLD and the live startup check were missing; the guard lacked the exact command-line check and the owner re-check before SIGKILL, could fire a second stop ~23 s after the first, had no nvidia-smi timeout, and its dry run sent no real signal. coach holds APPROVED until judge confirms the fixed code and dry passes 1-3; runner was fixing at 02:43. E1 opening #7 is registered, not opened; it needs the user's OK.

- **[12 Nov update: launched and trained, not opened.]** runner fixed the guard and queue (shared lib `s2c_lib.sh` 4edcae9e, guard 334742d6, queue de31c533, gpumem 06791cdd); the tests (dummies only) showed SIGKILL only after an owner + cmdline re-check, no second stop within 30 s, a cap of 2, HOLD after 10 failed reads, decoys never signalled, and a "test: 50" startup line stopped and held. judge ACCEPTED (02:58, `judge/review_s2c_stage1_code.md` ddf09a9f) with 2 arming conditions; coach APPROVED; the suite was re-run on the exact final md5s (03:04). Launched **03:06** (tmux `s2c`; queue PID 2345125, guard 2343958, gpumem 2343574); the arming conditions were met (coach 03:09); all agents were closed ~03:10. **ALL TRAINED 3 Nov 11:24:04: 10 rc 0 of 10** (waves done 04:45 / 06:25 / 08:04 / 09:44 / 11:24, ~1 h 40 each); the guard never fired; no HOLD (team-lead's 4 Nov read-only check, logged 12 Nov). **Nothing scored; stage 2 not started; E1 opening #7 registered, NOT opened; it needs the user's explicit OK.** Details: `SESSION_RECORD_2026-11-03_to_11-04.md` §2; doc 14 §1.2f.

## 11. Incidents (details: doc 13 D46 to D54)
- **gaint near-miss (2 Nov 12:18:28):** outside GPU processes (a Blender render under the noob account, then a second ~2.6 GB process) beside finllm and three SKR2 lanes took free memory to **2,078 MiB**; the 2 GB floor held by 30 MiB. New early alerts (doc 14 §1.2e).
- Hand-typed timestamps ahead of the clock (runner, judge, coach; corrected); coach's self-test printed a PF2E any-hit readout during the #6 run; the B2 raters' brief had them read the B2 report; the B2 "centre cell" instruction to the user (~11:21) was corrected to the whole 512 crop at ~11:31, before any mark (team-lead's account (message to scribe and log 3 Nov 02:45)); the first HC relay (~03:14) came before judge's fixes and a corrected version reached the user at ~11:18 (team-lead's account (message to scribe and log 3 Nov 02:45); the 11:18 log line's md5 is stale); laptop restarts and agent respawns (no server job lost); the B6 queue's subshell-pid defect (fixed before arming).

## Related docs
- `20_pf2_and_domain_ideas.md` (the protocols as armed; PF2, PF2E).
- `22_thermal_desk_study.md` (added 12 Nov: the 4 Nov thermal study; §13 SKR2C state).
- `11_results_synthesis_and_claims.md` rows 43 to 50; `12_decisions_log.md` D79 to D92; `13_problems_pitfalls_open_issues.md` A18, C20 to C23, D46 to D54, E31 to E34; `14_code_and_infrastructure.md` §1.2e, §5d; `15_status_remaining_work.md` §1j, §3e, §4e; `16_faq_for_the_guide.md` section J.
