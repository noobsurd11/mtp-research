# Session record, 1 Nov to 3 Nov 2026: A8 screen KILL, HC n.d., B6 n.d., SKR2 PASS, HC2 FAIL, SKR2E FAIL; Om's A1-A6; B2 agent raters

Covers the session after `SESSION_RECORD_2026-10-31_to_11-01.md` (which stops at 1 Nov ~21:40 IST; its last commit is 7118634). Status as of 3 Nov ~02:45 IST.
Team folder: `team_2026-10-31_next/` (brief `README.md`, append-only `log.md`, ledger `e1_openings.md`). Tags: E = measured (file), R = literature (id), S = judgement. "Clean" = the 50 test cells without `CSIR_00070_r8_c4`. Rule 1 = house rule, divisor 3. SUPPF = SUP100-PF (pf2_SUPPF s5-9, the shared comparator). Every verdict below is the pre-registered one; readings are kept apart and labelled.

## 0. In one screen
- **A8 screen (DINOv3 ConvNeXt-T vs IN-1k ConvNeXt-T under PF, 2 seeds, 4k steps; no test, no E1): KILL** (`verify_a8screen.md` 748be1ce; coach, judge CONFIRMED). F51 crack AP A8 − A8c −0.0243, module-bootstrap lower bound −0.0463. "Foundation encoder" (idea 8) is closed for the thesis by protocol §5. KILL means "no sign of a gain", not "DINOv3 is worse".
- **HC (synthetic half-cuts, 5 v 5; E1 opening #3): n.d.** (`verify_hc.md` 85db8111; coach, judge CONFIRMED). No co-primary moves. Mechanism passed in the simulator (SHV1 matched relR@2 +0.1233); F51 guard passed. judge's corrections: test inactive leans worse, seed-aware [−0.054, +0.005] (n.d.); the F51 crack AP gain (+0.067) comes from coverage on the 12 crack cells, not from fewer false alarms.
- **B6 (module-grouped 5-fold CV for PF's inactive gain, cv02 training, gaint scoring): n.d.** (`verify_b6.md` 1060d0e5; coach, judge CONFIRMED). Δ −0.0144, CI [−0.0977, +0.0570]. Realised SE 0.038 vs the planned 0.020, so power was ~6% at +0.017 (13% stated before the run). It does exclude an in-distribution gain the size of PF's E1 gain (CI hi +0.06 vs +0.19 / +0.21).
- **SKR2 (Skeleton Recall w 0.1; E1 opening #5): PASS, narrow.** E1 crack relF1@2 +0.0364 (thr 0.0351); the label is fragile, the effect is robust and not a bias shift. **HC2 (half-cuts with inactive → ignore in synthetic views): FAIL by G1** (test inactive −0.0256 / −0.0259); its mechanism failed. (`verify_skr2_hc2.md` d13cd6fa; judge CONFIRMED.) The user kept the HC route OPEN; only the (a2) ignore design is closed.
- **SKR2E (E-SKR2 vs E-PF as deployable ensembles; E1 opening #6): FAIL** by G2a + G2b at the headline pair (`verify_skr2e.md` 507e9e7a; judge CONFIRMED). The width flag decided it by 0.0015. The b 0 passes are not a confirmation. **E-PF at argmax stays the recommended deployable candidate (coach and judge, PF2E); the user's adoption is still open (handbook doc 15 §3d row 19); SKR2E did not displace it. FINAL 0.492 (cv02) is not comparable by rule.**
- **PF2 E1 inactive qualifier (judge, 1 Nov 23:46):** 3 source images hold 87% of E1 inactive px; without them PF2's +0.189 is +0.023.
- **Om's architecture ideas A1-A6 (`om_2026-11-01_arch.md`; agent `arch`, judge): all DROP, A4 PARK.**
- **B2 agent raters (`ideas/b2_agent_marking_prereg.md` v2.2): calibration FAIL.** Crack gate PASS (sens 20/20, spec 17/20); scuff gate FAIL (sens 1/8). No agent B2 marks; B2 is unmarked and back with the user.
- **Now (~02:45, 3 Nov):** SKR2C (SKR2 vs SUPPF on fresh seeds 10-14, training only tonight): protocol v1 LOCKED 02:37 (judge signed); data root verified; judge's stage-1 code review (02:38) found the guard / queue NOT READY (7 must-fixes), so coach holds APPROVED; runner is fixing; nothing launched. The opening (E1 #7, registered, not opened) waits for the user's OK (§12).

## 1. Timeline (IST)
| When | Event |
|---|---|
| 1 Nov 21:15-22:55 | A8 / A8c s0 and s1 trained (nq queue, 4k steps each) |
| 1 Nov 21:41-2 Nov 02:17:01 | HC s5-s9 trained (nq queue) |
| 1 Nov 21:36-23:28 | laptop restart by the user; all agents end; gaint jobs run on in tmux; runner, coach, builder, judge respawned 23:28 |
| 1 Nov 22:56:30-23:02:17 | A8 scoring (CPU, val + `_rf` only), rc 0 |
| 1 Nov 23:35-23:40 | **A8 screen KILL** (coach 23:35, judge CONFIRMED 23:40); relayed to the user 23:39 |
| 1 Nov 23:41-23:57 | B6 build reviewed (judge PASS for launch 23:47); run set FROZEN 807d4d03 (23:47); deploy addendum FROZEN 7b876eee (23:56) |
| 1 Nov 23:46 | judge: PF2's E1 inactive gain sits in 3 images (87%); +0.023 without them |
| 1 Nov 23:54 | **User decision:** B6 may use gaint for the scorer exact check and the 20-run scoring; training cv02 only |
| 2 Nov 01:23:44-01:23:55 | B6 scorer GPU exact check: EXACT PASS (54/54 val cells identical) |
| 2 Nov 01:29 | **B6 APPROVED** (coach; protocol_B6 b9581ac6); launch waits for ≥ 3 qualifying cv02 GPUs |
| 2 Nov 02:18:34-03:09:57 | **HC opening** (E1 opening #3), post rc 0 |
| 2 Nov 03:14-03:19 | **HC n.d.** (coach 03:14; judge CONFIRMED 03:18 with 4 fixes; fixes verified 03:19); relay to the user: see §11 item 7 |
| 2 Nov 11:18 | **User decisions:** next on gaint = SKR2 + HC2, one protocol and one opening; the user will mark B2 (sheets + blank `b2v2_marks.tsv` sent) |
| 2 Nov 11:19-11:44 | Om's A1-A6 forwarded; agent `arch` validates (CPU); judge reviews 11:43; all DROP, A4 PARK |
| 2 Nov 11:21-11:42 | HC2 design: half dose (11:21) → exclude variant (11:27) → retention rule (11:33) → (a2) ignore variant (11:42) (§6.1) |
| 2 Nov ~11:21, ~11:31 | B2 marking unit told to the user as the centre half-cell, then corrected to the whole 512 crop (team-lead's account (message to scribe and log 3 Nov 02:45); §11 item 6) |
| 2 Nov 11:26 | user asks why an agent cannot mark B2; team-lead spawns marker1 and marker2 |
| 2 Nov 11:34 | protocol_SKR2_HC2 **v1 LOCKED** (SKR2 + shared rules, 3b471576); **SKR2 APPROVED**; queue armed 11:34:49 |
| 2 Nov 11:46-12:26 | outside GPU processes on gaint (a Blender render, then a second process); **min free 2,078 MiB at 12:18:28** (§11) |
| 2 Nov 11:48-11:49 | both B2 raters' calibration marks logged; judge scores: **FAIL** (scuff gate) |
| 2 Nov 13:30-13:39 | cv02 qualifies (5 GPUs); B6 deploy, verify, A6000 identity PASS; B6 queue armed 13:39 |
| 2 Nov 14:03-16:39 | SKR2 s5-s9 trained rc 0 |
| 2 Nov 14:13-14:28 | HC2 GPU H0 IDENTICAL (1,000 steps) and smoke clean |
| 2 Nov 14:33 | protocol_SKR2_HC2 **v1.1 LOCKED** (HC2, 92ef5db6); **HC2 APPROVED**; HC2 queue + opening trigger armed |
| 2 Nov 17:00-19:59 | HC2 s5-s9 trained rc 0 |
| 2 Nov 17:58 | **User decision:** run HC2 as built; team-lead reports the B2 FAIL and the 12:18 near-miss; arch, marker1, marker2 stopped |
| 2 Nov ~18:00-21:29 | all agents ended (session); gaint and cv02 jobs run on; respawn 21:29 |
| 2 Nov 20:01:46-21:23:18 | **SKR2 + HC2 opening** (E1 opening #5), post rc 0 |
| 2 Nov 21:31 | B6 ALL TRAINED (20 rc 0 of 20) on cv02 (16:01:15 UTC) |
| 2 Nov 21:34-22:10:51 | B6 relay cv02 → gaint (124 files) |
| 2 Nov ~21:38-21:49 | **SKR2 PASS, HC2 FAIL** (coach ~21:38; judge CONFIRMED ~21:44; fixes verified 21:48) |
| 2 Nov 21:51 | **User decisions:** HC route stays OPEN ((a2) closed); next = SKR2E |
| 2 Nov 21:54-21:59 | protocol_SKR2E v0.9 → judge NOT READY → v1 signed and **LOCKED** (cbc3e015) |
| 2 Nov 22:11:25-22:13:45 | B6 scoring on gaint GPU, rc 0 |
| 2 Nov 22:15-22:20 | **B6 n.d.** (judge's own recompute 22:15; coach verify 22:18; judge CONFIRMED 22:19; fixes verified 22:20); relayed 22:19 |
| 2 Nov 22:19:52-22:23:15 | SKR2E gate dry check (val only), clean |
| 2 Nov 22:24 | **SKR2E APPROVED**; run 22:24:38-22:36:52 (E1 opening #6), rc 0 |
| 2 Nov ~22:25-23:28 | agents ended; the laptop was off campus; respawn 23:28 |
| 2 Nov 23:30-23:41 | **SKR2E FAIL** (pull ended 23:30; coach verify 23:37; judge CONFIRMED 23:39; fixes verified 23:41); relayed 23:41 |
| 3 Nov 02:21-02:25 | team-lead: user offline until 3 Nov; SKR2C protocol (training only tonight) with coach and judge; scribe respawned |
| 3 Nov 02:28-02:37 | protocol_SKR2C v0.9 → judge NOT READY (02:32) → v1 **LOCKED 02:37** (91b76abd; judge signed); data root verified (rootcheck run 2 rc 0, 02:37); E1 #7 registered, not opened |
| 3 Nov 02:38-02:43 | judge's stage-1 code review: guard / queue NOT READY (G1-G8); coach holds APPROVED; runner fixing |

## 2. Team, rules, infrastructure (changes this session)
- **Agents:** runner, coach, judge throughout; builder (B6 build until 2 Nov 01:30, then not reachable by message; respawned 11:27 for the HC2 code, idle from 12:04); `arch` (Om's A1-A6, 2 Nov 11:20-17:58); `marker1`, `marker2` (B2 agent raters, 11:27-17:59); scribe. calib, domain, found were not respawned.
- **Restarts:** laptop restart 1 Nov ~21:40 (respawn 23:28); agents ended 2 Nov ~18:00 (respawn 21:29); agents ended ~22:25 while the laptop was off campus (respawn 23:28). Every respawn read the README, the log and the files on disk; gaint and cv02 jobs ran on (tmux).
- **gaint GPU alerts:** the event watcher went v2 → v3 (11:35, adds the s2q logs) → **v4** (17:59, `rwatch_v4.sh` f839d6f4): early ALERT when free < 2,560 MiB on 2 polls (the < 2,048 hard alert kept), and OUTSIDE-LOW when free < 2,300 while a non-runner GPU process is present (§11).
- **Timestamps:** every log line from `date` (re-stated by coach and judge 2 Nov 21:49 after typed stamps ran ahead of the clock; §11).
- **No-test data root (D74 of the handbook):** used again for B6 (per-fold roots with val = test = the held-out fold).
- **Server rule kept:** cv02 per-process limit (no start on a GPU where another user's process holds > 4,096 MiB); B6 trained only there; gaint was used for B6 scoring by the user's decision.

## 3. Decisions by the user, with dates
| When | Decision | Logged |
|---|---|---|
| 1 Nov ~21:34 | An SKR follow-up is decided after the A8 screen and HC results | log 21:34 team-lead |
| 1 Nov 23:54 | **B6:** gaint for the scorer exact check (1-2 min) and the 20-run scoring (~30 min); training stays cv02 only; the cv02-scoring fallback dropped | log 23:54 team-lead |
| 2 Nov 11:18 | **Next on gaint = SKR2 (Skeleton Recall w 0.1) and HC2 (synthetic half-cuts + test-inactive guard)**, one protocol, one opening | log 11:18 |
| 2 Nov 11:18 | **The user will mark B2** (100 panels); sheets and a blank `b2v2_marks.tsv` sent | log 11:18 |
| 2 Nov ~11:20 | Forwarded Om's architecture ideas A1-A6 ("if you would like to think that direction") | `om_2026-11-01_arch.md` header; log 11:19 |
| 2 Nov 11:26 | Asked why an agent cannot do the B2 marks → agent raters tried; user marks optional | log 11:26 |
| 2 Nov 17:58 | **Run HC2 as built** ((a2), rather than an HC replicate on new seeds, a ConvNeXt check, or skipping) | log 17:58 |
| 2 Nov 21:51 | **HC route kept OPEN** (§7 (a2) formally triggered, not applied; the (a2) ignore design closed); **next = SKR2E**, the inference-only ensemble check of SKR2 vs SUPPF (E1 opening #6) | log 21:51 |
| 2 Nov ~21:5x | SKR2E go confirmed as the user's own ("Confirm SKR2 as deployable"): a go to run SKR2E, not an adoption of any model | log 22:17 runner; team-lead 3 Nov 02:45 |
| 3 Nov ~02:20 | "if theres anything else to do run this night, and close all the agents later" (user offline until 3 Nov) | log 02:22 team-lead |
- **No user ruling adopts a deployable model:** E-PF is the recommended candidate (coach and judge); adoption is open (handbook doc 15 §3d row 19; team-lead, log 3 Nov 02:45).
- team-lead's own calls (not user rulings): HC2 D1 and its pre-set retention rule (§6.1); the split lock (SKR2 v1, HC2 v1.1); SKR2C at MAXC 2 for the unattended night ("Blender vs lanes", §13).

## 4. A8 screen (`protocol_A8screen.md` v1.1; `verify_a8screen.md` 748be1ce; no test, no E1)
- **Runs (E):** A8 (DINOv3 ConvNeXt-T-PF) and A8c (IN-1k ConvNeXt-T-PF), seeds 0-1, 4k steps, el_f8 c280e8c2, data root `a8_root` (test.txt = val). Trained 1 Nov 21:15-22:55, all rc 0, config OK. Scoring a8_score.sh 75a57c9c 22:56:30-23:02:17, MANIFEST 3cdd7286. nq min free 2,880 MiB (22:16:46).
- **Validity:** both arms VALID (stage 2-3 cosine to init 0.98-0.999; A8 moved ~10x more than A8c). Val dump gate (pass 3b) PASS 4/4.

| GO term (seed means) | value | result |
|---|---|---|
| 1a F51 crack AP A8 − A8c > 0 | 0.5448 − 0.5691 = **−0.0243** | **FAIL** |
| 1b F51 36-module bootstrap lower bound > 0 | **−0.0463** [hi +0.0454] (coach own RNG −0.0476) | **FAIL** |
| 2 val crack AP A8 ≥ A8c − 0.02 | Δ −0.0041 | pass |
| 3 false alarms ≤ max(1.5x, +200 px), H36 / F51 crack-free | 92 vs 28 / 392 vs 201 | pass, only via the +200 px floor |
- **Verdict: KILL** (coach; judge CONFIRMED with own code, every term to 4-6 dp). Consequence by protocol §5: "foundation encoder" closed for the thesis, no larger download, no A8 full arm.
- **judge's readings (applied):** F51 is mostly one cell (`CSIR_00073_r9_c3_rf`, 76% of crack px); leave-one-crack-module-out negative for all 12; seed-aware bootstrap [−0.069, +0.047]; sign count 3 up / 5 down / 4 tied at 0 (module AP = prevalence); A8c's own seed spread (0.067) exceeds the arm gap; KILL = "no sign of a gain", not "worse".
- **Pitfall found:** with test.txt = val.txt, each run's metrics.json `test_final` / `test_best` hold val numbers under a test label (n_images 54). Never harvest them as test.

## 5. HC (`protocol_HC.md` v1.1; `verify_hc.md` 85db8111; E1 opening #3)
- **Runs and opening (E):** hc_HC_100pct_s5..9 (el_hc c2e6973, `data.synth_halfcut` p 0.35), trained 1 Nov 21:41 to 2 Nov 02:17:01, all rc 0, config OK. Opening hc_post.sh (FROZEN a23994c4) 02:18:34-03:09:57; MANIFEST d5c39e0d (190 files). Opening min free 20,692 MiB.

| co-primary (Δ HC − SUPPF; all 50 / clean; thr) | value | result |
|---|---|---|
| test crack IoU | +0.0092 / +0.0089 (0.0100) | n.d. |
| test crack relF1@2 | +0.0026 / +0.0023 | n.d. |
| test inactive IoU | −0.0228 / −0.0230 (0.0289 / 0.0290) | n.d. |
| E1 crack relF1@2 | +0.0135 (0.0429) | n.d. |
| E1 inactive IoU | −0.0002 (0.0572) | n.d. |
- **Verdict: n.d.** Mechanism **passed**: SHV1 matched relR@2 HC 0.8192 − SUPPF 0.6959 = **+0.1233** (kill < +0.05), seed ranges disjoint; the half-cut bias gap +1.1 → −0.5. **F51 harm guard passed:** crack AP 0.5371 vs 0.4702 (+0.0669), module bootstrap [+0.0125, +0.0867].
- **judge's corrections (applied, verdict unchanged):**
  1. **Test inactive:** n.d. by the locked rule. The fixed-prediction bootstraps exclude 0, but the **seed-aware two-stage bootstrap is [−0.054, +0.005], P(Δ < 0) 0.95**. The drop is broad (11 of 16 inactive cells down; leave-top-3-out −0.031). The unregistered "/n divisor WORSE" line was removed.
  2. **Test crack:** n.d., symmetric with inactive: every HC seed above every SUPPF seed; seed-aware [−0.002, +0.023], P 0.94; +5% predicted volume. No BETTER labels on unregistered subsets.
  3. **E1 half-cut without scuff:** +27% predicted volume on 11 GT components, detection +0.6 component per seed, n.d. E1 overall is not fattening (pred/GT 0.466 → 0.478; any-hit 0.381 → 0.377); its relF1@2 +0.0135 comes from precision (relP@2 +0.029).
  4. **F51:** the AP gain is **crack-cell coverage**: the 12 crack cells alone give +0.0597 (+0.055 with the other arm's negatives), at +25% volume (pred/GT 0.90 → 1.13), relP@2 unchanged. It is **not** the false-alarm drop. False alarms: H36 crack-free half-cuts 11 vs 278 px at b_rel, every seed (robust); F51 crack-free 122 vs 1,231 is fragile (one cell holds 71-96% of each SUPPF run's FA; ×2.5 at b 0).
- **Reading (S, coach and judge):** the simulator mechanism works; real E1 half-cuts do not move; HC rarely calls the real half-cut gap a crack (H36); test crack and test inactive lean ~0.02 in opposite directions (P ~0.95 each). Any follow-up needs a test-inactive guard. BEST unchanged.

## 6. SKR2 and HC2 (`protocol_SKR2_HC2.md` 2f6183b0; `verify_skr2_hc2.md` d13cd6fa; E1 opening #5)
### 6.1 HC2 design history (E, log 2 Nov 11:21-14:33)
1. **Half dose (v0.9, 11:21):** HC2 = HC at p 0.175 (half HC's synthetic dose), code-free; team-lead OK 11:22.
2. **Exclude variant (11:27, team-lead D1 (a)):** judge's review (11:25): a half dose cannot separate dose from cause, and val and SHV1 are one observation. HC2 became p 0.35 with inactive-bearing sources ineligible. The half-dose smoke never started (gate HOLD 11:27:49; script stopped by PID 11:29:59). builder's count (11:31): 35 of 353 sources hold inactive (not ~41).
3. **Retention rule (11:33, team-lead, pre-set before any HC2 number):** judge's W4: those 35 sources hold ~58% of the families' crack px, so excluding them would halve the synthetic crack dose. Rule: exclude if crack-px retention ≥ 60%; else ignore inactive px in synthetic views, if the loss supports an ignore index; else back to team-lead.
4. **(a2) ignore variant (11:42):** builder measured retention 0.399 (whole masks) / 0.359 (synthetic views) < 0.60; CEDiceLoss ignores 255. HC2 = all 353 sources, p 0.35, inactive → 255 in synthesised views only (~0.21% of synthetic px). Code el_hc2 branch hc2 0405151 (exclude key b28c284 kept, off); CPU identity chain IDENTICAL keys-off; 9-step pair differs first at the first ignored batch (as predicted); GPU H0 IDENTICAL over 1,000 steps (12da910c both); smoke clean (synthetic_inactive_px 0, ignored share 0.00218, peak 6,826 MiB). **v1.1 LOCKED 14:33** (92ef5db6).
5. **User (17:58):** run HC2 as built (a diagnostic for label vs dilution).

### 6.2 Runs and opening (E)
- SKR2 = el_thin c9bbb02 + `skel_recall.weight 0.1`, s5-9 trained 14:03-16:39; HC2 = el_hc2 0405151, s5-9 trained 17:00-19:59. All 10 rc 0, config OK, 0 Tracebacks. Opening s2_post (FROZEN fb5becd2) 20:01:46-21:23:18, MANIFEST bd671e26 (490 files). coach's armed recompute fired 21:24; judge recomputed independently; runner's local readout = coach to 4 dp.

| co-primary (Δ vs SUPPF; thr) | SKR2 | HC2 |
|---|---|---|
| test crack IoU (all / clean) | +0.0091 / +0.0088 (0.0100) n.d. | +0.0033 / +0.0064 n.d. |
| test crack relF1@2 | +0.0089 / +0.0085 n.d. | −0.0032 / +0.0006 n.d. |
| test inactive IoU | +0.0099 / +0.0102 n.d. | −0.0256 / −0.0259 (0.0277 / 0.0279) n.d. |
| B5 comp recall @ comp P ≥ 0.90 (wide grid) | +0.0169 / +0.0171 (0.0290) n.d. | (reported) |
| B5 relR@2 @ relP@2 ≥ 0.90 (wide grid) | +0.0094 / +0.0094 (0.0177) n.d. | (reported) |
| E1 crack relF1@2 | **+0.0364 (0.0351) BETTER** | +0.0074 (0.0483) n.d. |
| E1 any-hit comp recall | +0.0439 (0.0521) n.d. | (not a co-primary) |
| E1 inactive IoU | (not a co-primary) | −0.0795 (0.0830) n.d. |
| G1 test inactive ≤ −0.015 both sets | ok | **TRIP** |
| G2 test relP@2 < −0.03 or E1 crack-free px > ×1.5 | ok (−0.0121; ×0.97) | |
| G3 F51 AP upper bound < 0 | | ok (+0.0376 [+0.0022, +0.0869]) |
| **Verdict** | **PASS** | **FAIL (G1)** |

### 6.3 SKR2 (judge's readings, applied)
- **Label fragile:** margin 0.0013; leave-one-seed-out keeps BETTER in 5 of 10; leave-one-E1-image-out in 65 of 71.
- **Effect robust:** seed-aware [+0.004, +0.076], P 0.985; Δ +0.025 to +0.042 in every seed drop.
- **Not a bias shift:** SUPPF's best constant b on E1 reaches 0.4289 (E1-oracle, descriptive), below SKR2's 0.4567 at b 0; at equal E1 predicted volume SKR2 leads (relF1@2 +0.031, any-hit +0.024, fewer crack-free px).
- **w 0.1 vs w 1.0:** about a third of w 1.0's detection gain (any-hit +0.044 vs +0.142) and none of its false alarms (E1 crack-free px ×0.97 vs ×2.40; test relP@2 −0.012 vs −0.070).
- Claimable: "SKR w 0.1 passes: E1 crack relF1@2 BETTER (+0.036), no test cost, no precision-guard trip." Not claimable: "E1 detection BETTER" (any-hit n.d.), "test BETTER".

### 6.4 HC2
- **Mechanism FAILED** (coach's ruling on the frozen readout's "coach decides" case, judge agrees): pooled SHV1 relP@2 peaks at 0.776, so recall at relP@2 ≥ 0.90 does not exist. Post hoc split (descriptive): on the 11 inactive-bearing SHV1 views per run HC2 predicts almost no inactive (IoU 0.002 vs HC 0.386) and ×5.1 off-GT crack px; on the other 97 views HC2 ≈ HC (matched relR@2 0.845 vs SUPPF 0.784).
- **Label vs dilution: not decided** (judge's wording): HC2 − HC test inactive −0.003 against +0.023 for full recovery (P(full) 0.12); (a2) also lowers predicted inactive on test (0.557 vs HC 0.595 of GT inactive px) and on E1 (0.284 vs 0.562), so it cannot exclude the label cause. Dilution is not shown either.
- **§7 (a2) is formally triggered** ("mechanism failed at full crack dose → the HC route closes"). coach and judge recommended not applying it (post hoc reason: the failing quantity is an ignore-label artefact on 11 views). **User (21:51): not applied; HC route OPEN; the (a2) design closed.** A dilution-targeted variant would need the user's OK and keep G1.
- B5 comp recall +0.039 (reported) comes with test comp precision 0.728 vs 0.846 at that OP (all 50; clean 49: 0.889 vs 0.890, so the gap is the noisy cell).
- E1 inactive is a 3-image readout: top 3 images 87.0% of 9,158 GT px, effective n 3.3; leave-top-3-out HC2 −0.023.

## 7. SKR2E (`protocol_SKR2E.md` c4f36666; `verify_skr2e.md` 507e9e7a; E1 opening #6)
- **Design:** E-SKR2 (skr2_SKR01 s5-9) vs E-PF (pf2_SUPPF s5-9; PF2E's files), 5-member mean softmax, gaint CPU fp32. judge's review of v0.9 (NOT READY, 21:57): the verdict must use one shared b 0 for both arms; guards at b 0 and at the headline pair (each arm at its own D2 / width-flag b); G1t added. v1 LOCKED 21:59 (cbc3e015).
- **Run (E):** gate dry check 22:19:52-22:23:15 (val only); APPROVED 22:24; run 22:24:38-22:36:52, rc 0; val decisions 22:28:05 before test / E1 files 22:36:51. E-PF identity vs PF2E EXACT (0 of 520 cells differ). MANIFEST 9b43e636 (17 files). Readouts: runner fc41eeaa = coach 851403ca = judge 96f838d0 to 4 dp.
- **Val decisions:** E-PF D2 b 1.5, width drop +0.0753 > 0.05 → headline b 0. **E-SKR2 D2 b 1.0, width drop +0.0485 ≤ 0.05 → headline b 1.0.**

| At b 0 (verdict pair) | E-PF | E-SKR2 | Δ [CI] |
|---|---|---|---|
| test crack IoU | 0.4815 | 0.4917 | +0.0102 [+0.0031, +0.0197] pass |
| test crack relF1@2 | 0.8942 | 0.9046 | +0.0104 [+0.0016, +0.0232] pass |
| test inactive IoU | 0.4613 | 0.4662 | +0.0050 n.d. |
| E1 crack relF1@2 | 0.4345 | 0.4698 | +0.0353 [+0.0102, +0.0613] pass |
| E1 any-hit | 0.3446 (102/296) | 0.4122 (122/296) | +0.0676 [+0.0253, +0.1282] pass |

| Guard | b 0 pair | headline pair (E-PF b 0, E-SKR2 b 1.0) |
|---|---|---|
| G2a test relP@2 Δ < −0.03 | −0.0110 ok | **−0.0379 TRIP** |
| G2b E1 crack-free px > ×1.5 | ×1.06 ok | **5,358 vs 2,528, ×2.12 TRIP** |
| G1t test inactive ≤ −0.015 both sets | ok | ok |
| G1e E1 inactive CI below 0 | ok (−0.0418) | ok |
- **Verdict: FAIL** (a trip at either pair fails, protocol §3b). **E-PF at argmax stays the recommended deployable candidate (coach and judge, PF2E); the user's adoption is still open (handbook doc 15 §3d row 19); SKR2E did not displace it. FINAL 0.492 (cv02) is not comparable by rule.**
- **judge's points (applied):**
  1. **The width flag decided it by 0.0015:** had E-SKR2's drop exceeded 0.05, its headline b would be 0 and the verdict PASS. G2b trips for every E-SKR2 headline b ≥ 0.5 against E-PF at b 0 (×1.58 at 0.5); its CI [×1.70, ×2.58] lies above ×1.5. This asymmetry was accepted on purpose at lock.
  2. **The b 0 E1 passes are NOT a confirmation:** #6 re-measures #5's members; the opening failed.
  3. **Bias share:** on test, E-PF at b 1 equals E-SKR2 at b 0 (−0.0002 / −0.0013), so the test pass at b 0 is not distinguishable from a bias step; E-SKR2 keeps +0.012 relP@2 at less volume. On E1, relF1@2 is a curve shift (+0.024 at matched volume, bias share 33%); any-hit is 60% volume, all 20 extra hits in scuff + half-cut cells of 6 images (n_eff 3.6).
  4. The guard trips are volume, not an SKR2 precision defect (at equal b 1: relP@2 −0.015, crack-free ×0.87).
  5. E1 inactive −0.042 sits in 3 images (+0.0003 without them); PF2E's E1 inactive gain must not be assumed to carry over to an SKR2 ensemble.
- **For the user (coach §4):** (a) record the FAIL, E-PF stays (recommended); (b) an E-SKR2 at b 0 would be an operating point picked after test and E1 were opened twice (#5, #6); no unopened set exists to confirm it; (c) the 0.05 width-flag rule is a separate pre-registered question.

## 8. B6 (`protocol_B6.md` 8a89bc2c; `build_b6.md` 568990a2; `verify_b6.md` 1060d0e5)
- **Build and approval (E):** builder's 5 fold roots (ROOTS.md5 e4100381, 0 test / 0 E1 stems), scorer `b6_score.py` 981b5f29, verdict `b6_verdict.py` 6d807784; judge PASS for launch 1 Nov 23:47. Scorer GPU exact check on gaint 2 Nov 01:23 (54/54 val cells identical, 0 px changed). APPROVED 01:29.
- **Run (E):** cv02 qualified 13:30 (GPUs 0/1/5/6/7); deploy DEPLOY.md5 b8367e5c; A6000 identity PASS (step lines 20/20 equal); subshell-pid defect found and fixed before arming (§11; FROZEN_B6 → 607c1dcf); armed 13:39; 20 runs (2 arms × 5 folds × seeds 5 / 6), all rc 0, config OK, databuild OK, ALL TRAINED 21:31 IST. Relay 124 files (RELAY.md5 6e8806e9); one bf16 scoring pass on gaint 22:11:25-22:13:45 (peak 3,294 MiB, min free 22,504); scores MANIFEST 960ce11a. cv02 deploy removed after (22:16).
- **Primary:** pooled out-of-fold inactive IoU, house 0.4992 / 0.5193 vs PF 0.4996 / 0.4901 (s5 / s6); **Δ −0.0144**; two-stage CI (frozen, seed 0) **[−0.0977, +0.0570]** (coach [−0.0955, +0.0609], judge [−0.0901, +0.0622]). **Verdict: n.d.**
- **Power (judge's correction, applied):** the pre-registered SE 0.020 was judge's own estimate; the realised SE is 0.038-0.039: groups alone 0.031 (out-of-fold cells are scored by a different model pair per fold, which the estimate ignored) plus seeds ~0.022. **Realised power ~6% at +0.017** (stated 13%), 12% at +0.03, 26% at +0.05; 80% needs ~+0.11.
- **What it can say:** it cannot tell test's +0.017 from 0 or from −0.05. **It does exclude an in-distribution gain as large as PF's E1 gain** (CI hi +0.06 vs E1 +0.19 singles / +0.21 ensemble). PF's inactive gain stays an unseen-panel (E1) result; no in-distribution null is claimed.
- Reported: CFVS (78% of inactive px) flat (+0.0007); inactive components lean PF (recall +0.058, precision +0.106; no label); zero-train-px classes (belt_mark f0, rings f2, clamp f3) get 0 px predicted inactive in every run.

## 9. Om's architecture ideas A1-A6 (`om_2026-11-01_arch.md`; `ideas/arch_A1.md`-`arch_A6.md`, judge verdicts appended 11:43)
Om wrote them on 1 Nov, before the A8 KILL, THIN-B3 and HC results. CPU only; no test or E1 file opened by `arch`.
| Idea | Key evidence (E) | Verdict |
|---|---|---|
| A1 two-branch encoder (DINOv3 + high-res CNN) | = the A8 screen plus a hard freeze and gated fusion; idea 8 closed by A8's §5, idea 6 HR branch DROP. Side check ConvNeXt-T 4k vs R34-PF 20k is post hoc and confounded (architecture, schedule, 4k vs 20k, 2 vs 5 seeds, one F51 cell) | **DROP** |
| A2 IBN-Net style early layers | style premise contradicted on non-E1 data (E1 content brightness = train, AUROC 0.52; the "brighter" signal is the letterbox; idea 2); IBN-a R34 weights exist, not fetched | **DROP** |
| A3 geometry-aware input | HC already removes cut-line false alarms on real half-cuts (H36 cut-line / spacing FP at b_rel: SUPPF 123 vs HC 3 px/run); F51 FP is ≤ 3% structure classes; FN shows no structure enrichment | **DROP** |
| A4 structured crack head | fragments are 7% of val components (4.7% of GT px), ≤ 5% on F51; the unseen-module loss is whole-component misses; E1 partial share 0.153 is ~2x val's | **PARK behind SKR2** |
| A5 long-range context | lowest rank; no prior support | **DROP** |
| A6 cell gate + pixel head | val gate ~no-op; SKR's extra px are 99.6% inside crack cells, so a cell gate cannot recover its precision; the val-chosen threshold swings ~16 margin units across seeds | **DROP as an arm** (the optional reported gate line was withdrawn; it ran in the S2 opening labelled "unstable threshold") |
- A4's revival condition (S, `arch_A4.md` §7: SKR2 passes G2 and its E1 any-hit gain survives): SKR2 passed with G2 held, but its any-hit gain was n.d. (+0.044) and SKR2E failed. Nobody has proposed reviving A4.

## 10. B2 agent-rater calibration (`ideas/b2_agent_marking_prereg.md` v2.2 db787d03; log 2 Nov 11:26-17:59)
- **Why:** the user asked why an agent cannot do the B2 marks (11:26). team-lead spawned marker1 and marker2; the user's own marks became optional.
- **Plan as fixed (judge's pre-review `judge/review_b2_agent_marking_pre.md` 378e1ce2, team-lead's approval 11:31):** marking unit = the whole 512 crop; judge builds name-free random-ID bundles and holds the key (`b2_bundle/`, MANIFEST 1751950d; 72 calibration items, 100 B2 items); raters get PASS / FAIL only; two runs of one model = consistency, not independent reliability.
- **Acceptance rule (v2.2 §6, fixed before any mark):** gate A crack on 40 house-labelled CSIR train cells (20 crack, 20 none): sens ≥ 0.70, spec ≥ 0.70, BA bootstrap lower bound > 0.5; gate B weak scuff on 32 Hanifi pool half-cells: scuff sens ≥ 0.50, spec ≥ 0.70; unsure ≤ 14/72. Scorer `judge/b2_cal_score.py` 8f7106e8 fixed before marking.
- **Result (judge 11:49; marks md5-logged before scoring: marker1 68f3b3f1, marker2 e94bdb86):** both raters identical on the gates. **Gate A PASS:** sens 20/20, spec 17/20, BA lower bound 0.833. **Gate B FAIL:** scuff sens 1/8 (needs ≥ 4/8), spec 24/24. Unsure 5/72. Reported, not gated: on gate B's Hanifi half-cells the raters found 1 of 14 cracks (Hanifi crack labels are speck-level). Same mark on 68 of 72 items. → **FAIL; no agent B2 marks; both stopped.** B2 is unmarked and back with the user (options in §13).
- Disclosures (judge-recorded): both raters had read `b2v2_report.txt` (Hanifi base rates known; team-lead's brief told marker2 to, §11 item 5); marker1 had read the vetter's review section that names the 3 Hanifi B2 panel cells, so its B2 marks on those 3 would have been unblinded (moot: no B2 marks were made); marker1 also read columns 1-6 of `judge/out/rf_sets.tsv`.

## 11. Incidents and disclosures
1. **gaint near-miss, 2 Nov 12:18:28 (E, runner, log 12:05 and 16:39):** outside GPU processes ran beside finllm (5,876 MiB) and SKR2 s5-s7 (7,020 MiB each): a Blender render under account noob (PID 2238148, 2,224 MiB, from 11:46:41, `timeout 3600`) and a second process (PID 2404500, 2,594-2,642 MiB, ~12:17-12:24). **Minimum free 2,078 MiB at 12:18:28: the 2 GB floor held by 30 MiB**; free < 2,400 MiB on 45 samples; the watcher's < 2,048 alert never fired; finllm unaffected. runner reported the margin to team-lead at 12:05 (free 2,496) and touched nothing (not ours; the user's jobs have priority); the full episode was disclosed at 16:39. Fix (17:59): `rwatch_v4.sh` early alert at < 2,560 MiB and an OUTSIDE-LOW alert; render-vs-lanes options put to the user (§13).
2. **judge's tail of THIN stdouts (1 Nov ~18:49): a reminder, not a new incident.** It is disclosed in the previous record (§10 there), and the never-tail rule it produced bound this session. team-lead's account (message to scribe and log 3 Nov 02:45): there was no new tail after 1 Nov 21:30; log.md shows none.
3. **Hand-typed timestamps ran ahead of the clock:** runner (1 Nov: two lines stamped 23:46 and 00:02, real 23:34 / 23:36; fixed in place 23:36); judge (1 Nov: seven lines stamped 23:42 to 00:44, real 23:36 to 23:46; fixed in place 23:46); coach's header dates (verify_a8screen "2 Nov" → 1 Nov; protocol_B6 §9 "2026-11-02 ~00:00" → 23:42; dated correction lines 23:48); coach (2 Nov: nine lines stamped 21:33 to 22:58, all written 21:30-21:49; correction line 21:49, content unchanged); judge's verify_skr2_hc2 header 22:40 → ~21:44. runner's 2 Nov "21:40" line sits after coach's typed 22:xx lines in the log. Since 2 Nov 21:49 every stamp comes from `date`.
4. **coach's self-test printed a PF2E any-hit readout (2 Nov 22:25:11):** the self-test of `coach_skr2e.py` on PF2E's opened files printed E1 any-hit E-g 81/296 and E-PF 102/296 at b 0. This was during the #6 run, before any of its output (decisions 22:28:05), after lock and APPROVED. runner's boot self-test computed the difference but printed only a boolean. Nothing depended on it (SKR2E was locked). **E-g 81 vs E-PF 102 is not a PF2E result** and must not be cited as "PF lifts E1 any-hit".
5. **team-lead's brief told marker2 to read `b2v2_report.txt`** (marker1 read it too; log 11:27, 11:38, judge 11:43), a file the prereg later put on the do-not-open list: the raters knew the Hanifi addendum's aggregate base rates. Disclosed in the prereg (D1-D5) and `ideas/marker2/disclosures.md` c758607c; no labels or per-cell values.
6. **team-lead told the user "judge the centre cell" for B2, then corrected it.** team-lead's account (message to scribe and log 3 Nov 02:45): at 2 Nov ~11:21, with the marking instructions after the sheets, team-lead told the user to mark the centre half-cell (and to note "neighbour" for a defect in a neighbour). At ~11:31 team-lead corrected this to the user: judge the whole panel (the whole 512 crop), because the ranking scored the whole crop and only about a third of the Hanifi labelled crack px sit in the centre cell (judge's pre-review, 11:30). The user has marked nothing, so no marks are affected. In the log: judge's pre-review 11:30 and team-lead's 11:31 line ("user's earlier 'centre cell' instruction corrected").
7. **team-lead's HC readings needed judge corrections.** team-lead's account (message to scribe and log 3 Nov 02:45): the first relay to the user (2 Nov ~03:14) cited coach and judge before judge's four fixes (verify_hc 046c2c81 → 85db8111, 03:18-03:19), and a corrected version reached the user at ~11:18 (verdict unchanged, n.d.). No log line was written at ~03:14; the 11:18 log line's citation of 046c2c81 is a stale md5 (team-lead's slip; the relayed content followed 85db8111). The corrections:
   - (a) test inactive interval: team-lead had given −0.040 to −0.012 (cell bootstrap, no seed noise); the seed-aware interval is −0.054 to +0.005, with 11 of 16 test inactive cells down;
   - (b) the E1 crack +0.014 comes from fewer false alarms, not more cracks found (any-hit flat); the relR@2 +0.075 on the 29 half-cuts without scuff is mostly larger predicted areas on 11 cracks, n.d.;
   - (c) the F51 crack AP +0.067 comes from covering more of the 12 real cracks, not from fewer false alarms;
   - (d) the full-cell (F51) false-alarm drop rests on one cell (fragile); the real half-cut drop (H36 278 → 11 px) holds for every seed.
8. **Laptop memory pressure and agent restarts:** laptop restart 1 Nov ~21:40; agents ended 2 Nov ~18:00 and ~22:25 (laptop off campus); respawns 23:28 (1 Nov), 21:29 and 23:28 (2 Nov). runner kept at most one helper subagent (laptop 6.2 GB available at 11:26) and one local waiter; laptop disk at 98% (judge deleted its 171 MB scratch pull, 21:48; runner's SKR2E pull ~3.3 MB). builder was not reachable by message from 2 Nov 01:30 (its §9 append landed; nothing lost). No gaint or cv02 job was lost to a restart.
9. **Subshell-pid defects:** (a) B6 (2 Nov 13:34, runner): the frozen cv02 queue recorded the launching subshell's PID, not the child python's, so it would have counted our own runs as another user's > 4 GB process (fail-safe: one run per GPU) and the identity peak read 0 MiB; fixed before arming; coach re-froze (FROZEN_B6 607c1dcf; v1 807d4d03 kept). (b) s2q (found 3 Nov 02:33, runner): the SKR2 / HC2 queue's pid files also held the bash subshell PID (e.g. 2170515 vs GPU python 2170519), so a by-PID stop of an s2q run would have hit the subshell; no stop was needed; the SKR2C queue starts the trainer as a plain background command ($! = python), to be proven in the guard dry run.
10. **runner's opening-build helper ran a read-only `python3 -c` on gaint** (key names and arm means of the HC opening's `e1_coprim.json`, values = verify_hc), against its brief; nothing written (log 12:03).
11. **HC2 first start attempt refused itself** (12:05:05): DEPLOY held the full hash, the check compared 7 chars; nothing started; fixed with a 7-char runner stamp (9aba66b3).
12. **judge's inherited tool** `hc_gaint_recompute.py` prints "held" when the mechanism delta is NaN; the frozen opening printed UNDEFINED correctly; judge did not use that line. judge's first write of the HC section lost two backticked `_rf` strings to shell substitution (fixed in place).
13. **Other:** judge's own read-only checks on gaint (3 Nov 02:3x; ssh -a; md5sum / find / readlink of split files and the two `labeled` dirs; one temp dir `/tmp/jdg_lab.*` created and removed; no process left) found that el_thin's `data/labeled` is a separate copy (1,747 common files identical, plus 585 B3 `masks_escdd_s` files), so SKR2C's identity check uses el_thin's own data for SKR2. runner's HC pull first landed two post.log files under one name (re-pulled as nq_post / hc_post); marker1's prereg was approved as md5 dc84975b, an intermediate state of the file now on disk as db787d03 (status lines only differ).

## 12. Running and armed now (3 Nov ~02:45) and next steps
- **gaint:** GPU = finllm only (free 25,804 MiB at 02:22). Idle tmux sessions listed by runner, none killed. `rwatch4` alive. Disk /home/noob/work 476 GB free.
- **cv02:** nothing of ours; `/tmp/noob_el/el_b6` removed after B6.
- **SKR2C (state from log.md as of ~02:45):**
  - **Design (`protocol_SKR2C.md` v1, LOCKED 02:37, md5 91b76abd; judge's review and sign `judge/review_SKR2C_v09.md` 47f8e6f0):** SKR2 (w 0.1) vs SUPPF on fresh seeds 10-14 (s2c_{SUPPF,SKR01}_100pct_s10..14), 10 runs, gaint, **training only tonight**, MAXC 2 (team-lead's call for the unattended night). Two verdicts at the opening: R = SKR2_HC2's rule-1 singles set at argmax (7 co-primaries, G1 / G2); D = the ensembles at a shared b 0 (SKR2E's set, guards at b 0). R PASS and D PASS → recommend; either FAIL → SUP100-PF stays. The named replication claim needs a seed-aware two-stage bootstrap. Stated chances: R PASS ~35-65% (judge's Monte Carlo, `judge/out/skr2c_power_out.txt`: 0.90 / 0.64 / 0.34 / 0.05 if the true effects are 1 / 0.75 / 0.5 / 0 × #5's); seed-aware replication ~25-45%. Disclosed: chosen after SKR2E; a third look at test and E1 (same cells).
  - **No test read in training:** one data root `/home/noob/work/s2c_root` (test.txt = val; SPLITS.md5 24568cdb), verified 02:37 (rootcheck run 2 rc 0; data-build "Labelled: 478 ... val: 54 test: 54"; CPU identity IDENTICAL for both arms against their own data).
  - **Unattended safety:** locked gates GATE_SKR01 9,100 and GATE_SUPPF 9,000 MiB (measured peaks 7,020 / 6,830 + 2,048, rounded up; protocol_SKR2C §2b), ≥ 120 s apart, 1 s memory log; new starts HOLD while an outside GPU process holds > 1 GB; an own guard process stops only the newest running SKR2C run, by its verified python PID, if free < 2,048 MiB on 3 consecutive 1 s samples (SIGTERM; SIGKILL after 30 s only after re-verifying owner and command line; at most 2 stops), then HOLD. Default after a stop: rerun from scratch. runner's estimate: ~12.3 h wall.
  - **Not yet launched:** judge's stage-1 code review (02:38, `judge/review_s2c_stage1_code.md` b0d866a4) found the guard / queue drafts **NOT READY**, with 7 must-fixes (G1-G7) and one should-fix (G8). The outside-process HOLD and the live startup check ("Labelled ... val: 54 test: 54", stop on mismatch) were not in the code yet. The guard lacked the exact recorded-cmdline check and the owner re-check before SIGKILL; a second stop could fire ~23 s after the first; nvidia-smi had no timeout; and the dry run sent no real signal. coach agreed (02:38-02:42) and holds APPROVED until judge confirms the fixed code and dry passes 1-3. runner was building the fixes at 02:43 (the DRY=1 pass 1 at 02:37-02:39 was clean, but the code it ran is being replaced). **E1 opening #7 is registered, not opened; it waits for the user's OK.**
- **Next (S):** the user's call on §13.

## 13. Open decisions for the user
1. **Next step:** (a) pause GPU work and write up; (b) SKR2 on new seeds (SKR2C, training running or armed tonight; opening on your OK); (c) wait for B2.
2. **B2:** (a) the user marks (the sheets are with you; whole 512 crop is the unit); (b) a new agent prereg for crack only (the crack gate passed on house CSIR cells only; on Hanifi half-cells the raters found 1 of 14 cracks, so a crack-only prereg for the Hanifi B2 panels rests on a gate that did not test Hanifi cracks; the scuff gate failed); (c) skip B2.
3. **Blender renders vs gaint lanes:** outside renders took free memory to 2,078 MiB at 12:18 with 3 lanes; team-lead chose MAXC 2 for tonight. A standing rule is the user's call.
4. Carried: the D2 width-flag rule (decided SKR2E by 0.0015; any change is a new pre-registered question); a dilution-targeted HC variant (needs your OK, keeps G1); the HF sample; who rebooted gaint on 30 Oct; the 40-segment crack audit and 4 label questions; idle cv02 / gaint tmux shells.

## 14. Files
- **Brief, log, ledger:** `team_2026-10-31_next/README.md`, `log.md`, `e1_openings.md` 0b2ff129, `om_2026-11-01_arch.md`.
- **Protocols:** `protocol_A8screen.md`, `protocol_HC.md`, `protocol_B6.md`, `protocol_SKR2.md` (superseded sketch), `protocol_SKR2_HC2.md`, `protocol_SKR2E.md`.
- **Builds and reviews:** `build_b6.md`, `build_hc2.md`, `build_s2_runner.md`, `build_skr2e.md`; judge's `judge/review_SKR2_HC2_v09.md`, `review_SKR2E_v09.md`, `review_b2_agent_marking_pre.md`, recompute scripts and `judge/out/`.
- **Verifications:** `verify_a8screen.md` 748be1ce, `verify_hc.md` 85db8111, `verify_b6.md` 1060d0e5, `verify_skr2_hc2.md` d13cd6fa, `verify_skr2e.md` 507e9e7a (each with judge's section).
- **Ideas:** `ideas/arch_A1.md`-`arch_A6.md`, `ideas/arch_out/`; `ideas/b2_agent_marking_prereg.md`, `ideas/marker1/`, `ideas/marker2/`.
- **Results:** `results/a8/`, `results/hc/`, `results/b6/`, `results/s2/`, `results/skr2e/`, `results/s2c_dry/`. In git: the small text readouts (coach_v, runner readouts, launch / gpumem / relay logs, frozen md5 lists). Local only: raw pulls (`results/*/raw`, gitignored, with MANIFEST.md5) and B6's per-cell scores and metrics.json (`results/b6/scores/*.b6.json`, `results/b6/metrics/*.json`; MANIFEST.md5 / RELAY.md5 committed).
- **Servers:** gaint `el_f8` (A8), `el_hc` (HC), `el_hc2` (HC2, 0405151), `el_thin` (SKR2), `el_f3/reports/skr2e/`, `/home/noob/work/nq/`, `s2q/`, `a8_score/`, `b6/`, `b6_score/`, `cv02_noob_el/el_b6/` (B6 relay copy). cv02: none left.
