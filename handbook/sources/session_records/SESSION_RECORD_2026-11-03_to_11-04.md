# Session record, 3 Nov to 4 Nov 2026 (state as of 12 Nov): SKR2C trained (not opened); the thermal (IR) desk study, downloads, pick 1 G0, pick 3 A1 arm stopped

Covers the session after `SESSION_RECORD_2026-11-01_to_11-03.md` (which stops at 3 Nov ~02:45 IST; its commit is 3604dc7), to the end of the 4 Nov session (~13:50 IST), plus the state on 12 Nov when this record was written. All times IST.
Team folders: `team_2026-10-31_next/` (SKR2C) and `team_2026-11-04_thermal/` (thermal desk study and picks 1 and 3). Each has a brief (`README.md`) and an append-only `log.md`.
Tags: **E** = measured (file), **R** = from a source (paper, dataset page or API; via the team's own citation), **S** = judgement. Every verdict below is the pre-registered one; readings are kept apart and labelled "Reading". Thermal claims keep the tag their owner gave them.

## 0. Scope, sources and one screen

**Sources.** `team_2026-10-31_next/log.md` (3 Nov 02:20 onward, plus team-lead's 12 Nov retrospective line), `protocol_SKR2C.md` 663de96d, `build_s2c.md` c6424c0f, `judge/review_SKR2C_v09.md` cc2a21be, `judge/review_s2c_stage1_code.md` ddf09a9f, `e1_openings.md` 365d62f3; every file in `team_2026-11-04_thermal/` named in §13; team-lead's brief to scribe (12 Nov) for the facts no file holds (§3). Where a log line and a result file disagree, the result file is used and the gap is listed in §11.

**In one screen**
- **SKR2C (SKR2 = Skeleton Recall w 0.1 vs SUP100-PF, fresh seeds 10-14, 10 runs, gaint, training only): TRAINED, NOT OPENED.** Locked 3 Nov 02:37 (91b76abd). judge's stage-1 code review found the guard / queue NOT READY (7 must-fixes + 1 should-fix); fixed and accepted 02:58. Launched 03:06; all 10 runs rc 0 by **11:24:04 on 3 Nov**; the auto-stop guard never fired; no HOLD. No test or E1 number exists (data root with test.txt = val). **E1 opening #7 is registered, not opened; it needs the user's explicit OK.** Source of the completion facts: team-lead's own 4 Nov read-only check, logged only on 12 Nov (§2.5).
- **Docs and agents (3 Nov):** scribe committed 3604dc7 at 02:49 (judge fact-checked); all agents closed ~03:10.
- **Move to laptop tmux `orch-mtp`** so the user can drive the session by voice through Herald; the permission classifier blocked team-lead's own launch, and the user ran it (team-lead's account; no file records it).
- **Thermal team (4 Nov 11:56 to ~13:50):** Om's brief (3 Nov, pasted 4 Nov) asked for public paired EL + thermal data, every way thermal could help, and whether WattCycle / IIT Mandi could capture pairs. Five agents (datascout, ideas, capture, synth, check). Findings:
  - **Data:** three open CC BY 4.0 sets have EL and IR of the same modules, ~215 modules with IR in all (A1 OSF csr6t 157, A2 OSF ar76v 15, A3 DTU 43); none has masks or pixel registration (R).
  - **Physics:** thermal sees electrical consequence (inactive / disconnected area, hot spots, shunts), not cracks that isolate nothing (R); scuff is probably thermally silent (S).
  - **Ideas:** 40 (T01-T40) + 14 drone-only (W01-W14); synth merged them to 58 ranked rows; top 3 = pick 1 (IR screening vs EL on open pairs), pick 2 (WattCycle drone thermal now, low-cost EL soon), pick 3 (physics labels for inactive).
  - **Om's decisions (4 Nov):** downloads for picks 1 + 3 approved (~1.2 GB, CPU only); WattCycle has drone thermal only, EL rig 2-3 months away, so pick 2 re-planned; three items still open for Om.
  - **Downloads:** A1 209 files, A2 47 files, A3 7z + README, all verified twice (datascout, check); A3 extracted (1,414 files). Re-verified 12 Nov by scribe: 0 failures (§7).
  - **Pick 1 G0 (does dark forward-bias IR flag EL-dark cells?): not a go, not a kill.** v1 (frozen): A2 AUROC 0.736 / ρ −0.550 "between", A1 0.689 / −0.285 null, pooled 0.708. v2 (post hoc instrument fix, co-signed QA): A2 0.732 / −0.515, A1 0.621 / −0.246, pooled 0.687, same verdicts. check recomputed both from raw files: MATCH. Reading (post hoc): the signal is row / edge-level, not cell-level.
  - **Pick 3 A1 arm: stopped at T37 (team-lead option A).** T15 PASS, narrow (robust SD 3.26 mV vs a 2.57 mV line). T37 v1 PASS at the line (3 / 10 excluded); T37 v2 FAIL (4 / 10 by the frozen rule). Likely cause (crop geometry E; its role S, check CR-5): the authors' A1 IR crop is a fixed 134 × 35 window, not the module. T02 / T12 never ran. Redirect: pick3b on A3, plan frozen 13:43 before extraction.
  - **Not done when the session ended (~13:50):** pick 1's A3 readouts (R1, R2, R3b); pick3b's readouts; the ADDENDUM to SUMMARY is still a DRAFT; **the report to the user and Om was never sent.**
- **12 Nov:** the laptop OS was reinstalled (disk 52 GB free, E); no agent survived; this documentation is the first work since. The 4 Nov session ended abruptly (~13:51, cause unknown): four files carry crash traces (NUL bytes, empty files), and an attempted pick3b v1.1 freeze is empty, its content unknown (§11 T1).

## 1. Timeline (IST)
| When | Event | Source |
|---|---|---|
| 3 Nov 02:21-02:22 | team-lead: the user is offline until tomorrow ("if theres anything else to do run this night, and close all the agents later"); SKR2C, training only, MAXC 2 | next log 02:21-02:22 |
| 3 Nov 02:24 | judge's power Monte Carlo (`judge/out/skr2c_power_out.txt` 2e15d408) | log 02:24 |
| 3 Nov 02:28-02:37 | protocol_SKR2C v0.9 (6958d22f) → judge NOT READY, M1-M5 (02:32) → v0.9.1 (91f875c9) signed conditionally L1-L4 (02:34) → v1 candidate 5995fcd5 SIGNED (02:36) → **v1 LOCKED 02:37 (91b76abd)**; E1 #7 registered, not opened | log 02:28-02:37 |
| 3 Nov 02:31-02:37 | data root built and verified: rootcheck run 1 rc 1 (wall `sec` compared by mistake), run 2 rc 0 (02:33:29-02:37:24) | log 02:31, 02:33, 02:37 |
| 3 Nov 02:33 | runner: the s2q queue's pid files held the bash subshell PID, not the trainer's | log 02:33 |
| 3 Nov 02:37:56-02:39:52 | first guard dry run (on the code judge then rejected), clean | log 02:41 |
| 3 Nov 02:38 | **judge's stage-1 code review: NOT READY** (G1-G7 must, G8 should; b0d866a4); coach holds APPROVED | log 02:38 |
| 3 Nov 02:44-02:48 | judge fact-checks the previous scribe's drafts (11 fixes), re-check OK | log 02:44, 02:48 |
| 3 Nov 02:48-02:55 | v2 / v3 code staged; watcher passes 1-5 + queue unit tests clean (02:48:00-02:55:11) | log 02:48, 02:56 |
| 3 Nov 02:49 | **docs commit 3604dc7** (previous scribe; 384 files) | log 02:49; git |
| 3 Nov 02:57:40-03:04:05 | dry suite re-run on the exact final md5s: clean | log 03:04 |
| 3 Nov 02:58-02:59 | **judge ACCEPTED stage-1 v3** (ddf09a9f) with 2 arming conditions; coach APPROVED effective; team-lead accepts residual 1 | log 02:58-02:59 |
| 3 Nov 02:59-03:05 | judge unreachable from ~02:59 (coach's message undeliverable 02:59; runner's send refused 03:05); coach checks the final re-run; GO | log 02:59, 03:05 |
| 3 Nov 03:05:56-03:08:22 | deploy; gpumem 03:05:56, guard 03:05:59, queue armed 03:06:11; run 1 (SKR01 s10) up 03:06:11, startup OK 03:06:16; run 2 (SUPPF s10) 03:08:17, OK 03:08:22 | log 03:06-03:09 |
| 3 Nov 03:09-03:10 | coach verifies the launch lines; team-lead: SKR2C LAUNCHED, all agents closed | log 03:09, 03:10 |
| 3 Nov 04:45 / 06:25 / 08:04 / 09:44 / 11:24 | SKR2C waves s10 / s11 / s12 / s13 / s14 done (both arms per wave) | team-lead 12 Nov retrospective (next log) |
| 3 Nov 11:24:04 | **S2C ALL TRAINED (10 rc 0 of 10)**; guard 'end line seen' 11:24:05, 'guard stop (queue ended)' 11:25:05; no trigger, no HOLD | same |
| between 3 Nov ~03:10 and 4 Nov 11:56 | session moved to laptop tmux `orch-mtp` (time not recorded) | team-lead's account |
| 4 Nov 11:56 | thermal team started from Om's brief (6677bc9f); datascout, ideas, capture spawned (11:57) | thermal log 11:56 |
| 4 Nov 12:02-12:15 | dataset table v1 → v2 (12:12); capture plan v1 (12:10); ideas_long v1.1, 40 ideas (12:15) | thermal log |
| 4 Nov 12:16-12:27 | synth and check start (12:16); ranked v1 43 rows (12:23); top3 + SUMMARY v1 (12:25); synth v1.1 DONE (12:27) | thermal log |
| 4 Nov 12:37 | check pass 1: 110 items, OK 73, FIX 31, UNVERIFIABLE 6 | thermal log 12:37 |
| 4 Nov 12:39 | **Om's decisions** logged by team-lead (downloads approved; WattCycle drone only; three items open) | thermal log 12:39 |
| 4 Nov 12:43 | downloads start (A3 first); drone_only.md v1, 14 ideas | thermal log 12:43 |
| 4 Nov 12:44-12:45 | check pass 2 on synth: 33 items, OK 13, FIX 18, UNVERIFIABLE 2 (corrected 12:45) | thermal log |
| 4 Nov 12:47-12:52 | capture replan_pick2 v1 → v1.2; ranked v1.4, 58 rows; check pass 3 | thermal log |
| 4 Nov 12:49-12:59 | download plan frozen (409481f7); A1 selection frozen (da419f33, 12:55); pick 1 plan v1 frozen (28b58cc9, 12:56); pick 3 plan v1 → v1.1 → v1.2 (2893a817, 12:59); synth closed (12:59) | thermal log |
| 4 Nov 12:55-13:07 | A1 dark I-V 159 / 159 verified (12:55); A2 47 / 47 (12:59); A1 images (13:04); `download_verified.md` (13:07) | thermal log |
| 4 Nov 13:00-13:01 | **T15 PASS, narrow** (ideas 13:00); check's independent recompute MATCH (13:01) | thermal log |
| 4 Nov 13:00-13:07 | pick 1 Amendments 1-3 (orientation; A1 is 3 × 12; primary rot180) | thermal log |
| 4 Nov 13:10-13:13 | **G0 v1** readout (13:10); check §22 review (13:13); **T37 v1** readout with a visual misregistration (13:13) | thermal log |
| 4 Nov 13:14-13:20 | Amendment 4; visual QA (13:15); interim G0 (13:17, not counted); check's raw-file G0 v1 recompute MATCH; frozen v1 output restored (13:20) | thermal log |
| 4 Nov 13:16-13:35 | cellreg v0.4 04fac77a → 95e0ca3e (13:27) → v0.5 91c3c81e withdrawn → **v0.4.1 7d9a9fe0 frozen** (13:35) | thermal log |
| 4 Nov 13:28 | **T37 v2 FAIL**; team-lead **decision (A)**: pick 3 A1 arm stops at T37 | thermal log 13:28, 13:35; team-lead retrospective |
| 4 Nov 13:35-13:45 | G0 v2 registration (13:35); QA table co-signed (13:41-13:42); **G0 v2** computed (13:42-13:43); check recompute MATCH (13:45) | thermal log |
| 4 Nov 13:36-13:39 | `PICK3_A1_REPORT.md` 2eb8400b → 55fcf923; check drafts `synth/ADDENDUM_2026-11-04.md` (13:39) | thermal log |
| 4 Nov 13:38-13:43 | pick3b plan v0.9 → v0.95 → **v1 frozen eaec6f26** (13:43); pick 1 Amendment 5 (d1e6777b) | thermal log |
| 4 Nov 13:46-13:48 | A3 archive verified; fully extracted (1,414 files); check re-verifies every file's size + CRC32 | thermal log |
| 4 Nov 13:48-13:50 | pick3b discovery (FF loss becomes the primary label; 3b-R4 not run); ADDENDUM 878e6bec (13:49); pick 1 Amendment 6 fd98e232 → **fb46b6dc** (13:50) | thermal log |
| 4 Nov 13:51:39-13:51:49 | last file writes: empty `A3_layout.tsv`, empty `plan_pick3b_v1.1_FROZEN_c8f57302.md`, `plan_pick3b.md` padded with NULs; the session ended | file mtimes (E) |
| 12 Nov | laptop OS reinstalled; disk 52 GB free; no agent survived; team-lead's retrospective lines (on disk 14:41, stamped 14:45, corrected 14:46); this documentation (scribe + verifier) | logs; `df` |

## 2. SKR2C: fresh-seed confirmation of SKR2 (`protocol_SKR2C.md` v1 + §9 launch record, 663de96d; lock copy `judge/out/protocol_SKR2C_v1_lock_91b76abd.md`)

### 2.1 Design (locked 3 Nov 02:37, md5 91b76abd)
- **Question:** with fresh seeds 10-14 (both arms), does SKR2 (Skeleton Recall at `loss.skel_recall.weight=0.1`, el_thin c9bbb02) beat SUP100-PF (el_f3 e544133) as single models (verdict R, house rule 1) and as 5-member ensembles at a shared b 0 (verdict D)?
- **Runs:** `s2c_SKR01_100pct_s10..14` and `s2c_SUPPF_100pct_s10..14`, 20,000 steps, batch 8, final weights. Config diff vs pf2_SUPPF_100pct_s5 = seed + run_name + data.root (+ skel_recall 0.1).
- **Verdict R:** S2's rule-1 set, 7 co-primaries (test crack IoU, crack relF1@2, inactive IoU at argmax, all 50 / clean 49; B5 on the wider grid; E1 crack relF1@2 and any-hit), guards G1 / G2. **Verdict D:** ensembles at a shared b 0 (SKR2E's primaries; guards G2a, G2b, G1t, G1e at b 0). **R PASS and D PASS** → E-SKR2' recommended over E-SUPPF'; **either FAIL** → the SUP100-PF ensemble stays.
- **Named claim (two tiers):** "replicated (seed-aware)" needs the seed-aware two-stage bootstrap of E1 relF1@2 on the 10 fresh singles wholly above 0, D's E1 primary passing, and no FAIL.
- **Stated chances (S, judge's Monte Carlo 2e15d408):** P(R PASS) 0.90 / 0.64 / 0.34 / 0.05 at 1 / 0.75 / 0.5 / 0 × #5's effects; realistic ~35-65%; seed-aware replication ~25-45%; ~15% combined that a true null fails through an inactive guard alone.
- **Disclosed at lock:** the design was chosen after SKR2E; it is a **third look at the same 50 test and 106 E1 cells** (#5, #6). Fresh seeds remove seed luck, not cell luck: a PASS is a seed-level replication on reused cells, not new-panel evidence.

### 2.2 No test or E1 number during training: the data root
- One root `/home/noob/work/s2c_root` (SPLITS.md5 24568cdb): train 842f27c4, val 9dcccf00, test.txt = a byte copy of val; `labeled` → `/home/noob/work/el-fault-detection/data/labeled`. 0 forbidden stems, 0 real-test stems (E, `build_s2c.md` §2).
- rootcheck run 2 (02:33:29-02:37:24, rc 0): data-build line for both arms "Labelled: 478 (/home/noob/work/s2c_root/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54"; CPU identity (5 steps, `identity_cpu.py` 962379a6) IDENTICAL on every field except wall `sec`: SUPPF step-5 loss 4.154092311859131 / state 4a216d9d (= B6 idchk5); SKR01 (A = el_thin's own data) 4.251284599304199 / 2e44cb4d. Run 1 had failed only because it compared `sec` (8.25 vs 8.18 s); judge ruled excluding it a comparator fix (§2a's list never included it).
- Consequence (pitfall, handbook doc 13 C21): each run's stdout end block and `metrics.json` "test" entries hold **val** numbers. Never harvest them as test.

### 2.3 Problems found before launch (E)
1. **judge's review of v0.9 (02:32, e146f83b): NOT READY, 5 must-fixes** M1 (auto-stop per team-lead's rules), M2 (rerun-from-scratch default), M3 (named claim needs a seed-aware bootstrap), M4 (fallback branch), M5 (B5 component definition), plus 5 should-fixes. All applied by v0.9.2; signed; locked 02:37 with 6 wording fixes and L1-L4.
2. **s2q subshell PID (runner, 02:33):** the SKR2 / HC2 queue's pid files held the bash subshell PID (e.g. 2170515 vs GPU python 2170519), so a by-PID stop of an s2q run would have hit the subshell (no stop was needed then). The SKR2C queue starts the trainer as a plain background command ($! = python) and records `/proc/<pid>/cmdline` after the exec.
3. **judge's stage-1 code review (02:38, b0d866a4): NOT READY, 7 must-fixes + 1 should-fix:**
   - G1 the guard tested "contains" instead of exact recorded-cmdline equality;
   - G2 no owner re-check before SIGKILL;
   - G3 a second stop could fire ~23 s after the first (ruling: ≥ 30 s);
   - G4 nvidia-smi without a timeout could freeze the guard silently;
   - G5 the outside-process > 1 GB HOLD was implemented nowhere;
   - G6 no live "Labelled ... val: 54 test: 54" check, and CONFIG FAIL only HOLDed, so a wrong-root run would have finished and evaluated the **real** test;
   - G7 the dry run sent no real signal, so the SIGTERM / 30 s / re-check / SIGKILL path was untested;
   - G8 (should) unit tests for the new queue gates.
   The first guard dry run (02:37:56-02:39:52, guard 99291944) was on this rejected code and did not count.
4. **Fixed code (E, `build_s2c.md` §1, §4-7):** `s2c_lib.sh` 4edcae9e (`timeout 5 nvidia-smi`; `verify` = alive + not 6206 + owner noob + exact cmdline = recorded + tokens; `stop_verified` = SIGTERM, ≤ 30 s, re-verify, SIGKILL), guard 334742d6 (COOL 30, GAP 30 s, cap 2, 10 failed reads → HOLD; FAKE split from DRY), queue de31c533 (root re-check, outside-process wait, live cfgcheck + startcheck with a verified stop), gpumem 06791cdd.
5. **Tests (dummies only, no GPU):** v3 run 02:48:00-02:55:11 (`results/s2c_dry/v2/`, md5 list de5dbd1b) and the re-run on the exact final md5s 02:57:40-03:04:05 (`results/s2c_dry/final/`, md5 list 345c825e): a SIGTERM-ignoring dummy got SIGKILL only after the re-check passed (rc 137); a normal dummy exited on SIGTERM 63-64 s later (rc 143); the 3rd trigger was cap-only; an exec-swapped dummy failed the re-check, so no SIGKILL; a trigger 8-9 s after a stop gave no signal; 10 failed reads gave HOLD; decoys (altered cmdline, sleep, 6206, PID 1, dead, finished, stray) were never signalled; a startup line with "test: 50" gave MISMATCH → HOLD → stop rc 143.
6. **judge ACCEPTED (02:58, ddf09a9f)** with 2 arming conditions: exact md5s at both ends, start order gpumem → guard → queue with no env overrides; the queue's armed line and the first run's "config OK" + "startup line OK" before the 2nd start. Residuals (non-blocking, S): a run whose cmdline is not recorded within 20 s would be unprotected (team-lead accepted, 02:59); the shared gpu_gate's own nvidia-smi has no timeout (fails safe).

### 2.4 Launch (E, protocol §9; log 03:06-03:10)
- Deployed lib 4edcae9e / guard 334742d6 / queue de31c533 / gpumem 06791cdd / make_jobs e7d20e79; jobs 0839f340 (10 lines; coach parsed every diff), exp files dc9c344a / 1343cca2; gates SKR01 9,100 / SUPPF 9,000 MiB (measured peaks 7,020 / 6,830 + 2,048 = 9,068 / 8,878, rounded up to the earlier queues' gates: s2q 9,100, pf2 9,000; runner 02:23); MAXC 2; ≥ 120 s between starts.
- gpumem PID 2343574 (03:05:56), guard 2343958 (start line "FAKE none; DRY 0; THR 2048 MiB x 3; COOL 30; GAP 30 s; MAXSTOPS 2", 03:05:59), queue 2345125 (armed 03:06:11).
- Run 1 `s2c_SKR01_100pct_s10` python 2345199 (start 03:06:11, gate free 25,804; config OK and startup OK 03:06:16); run 2 `s2c_SUPPF_100pct_s10` python 2359341 (03:08:17; OK 03:08:22). GPU: finllm 5,876 + 7,018 + 6,826 MiB, free 11,947 at 03:08:54. /proc cmdlines = recorded; owner noob; no HOLD. Arming conditions 1-2 MET (coach 03:09).
- judge was unreachable from ~02:59 (its 02:58 line: all items for the night closed, no process running; coach's message undeliverable at 02:59; runner's send refused at 03:05); coach checked the final re-run logs against judge's acceptance.

### 2.5 Training result (state as of 12 Nov; source: team-lead's retrospective line, next log, stamped "2026-11-12 14:45", written ~14:41)
- Per team-lead's own **4 Nov** read-only check of gaint (no 4 Nov log line was written; no server access since): `launch.log` shows all 10 runs "done ... step 20000/20000 lines 1, Traceback lines 0"; waves done s10 04:45, s11 06:25, s12 08:04, s13 09:44, s14 11:24 (both arms per wave); **"[Tue Nov 3 11:24:04 AM IST 2026] S2C ALL TRAINED (10 rc 0 of 10; pid 2345125, s2c_jobs.txt)"**.
- `autostop.log`: only the guard start line (03:05:59), "end line seen" 11:24:05 and "guard stop (queue ended)" 11:25:05. **No trigger, no HOLD, no stop**, so the protocol's rerun rule never applied. GPU after: finllm 6206 only.
- Wall ~1 h 40 per wave, ~8 h 18 in all (S arithmetic from the stamps), faster than the stated ~2 h 28 per run / ~12.3 h.
- Not checked (team-lead's line): the morning greps for "no train.py cmdline" / CONFIG FAIL / live check FAILED beyond the done lines; none appeared in the grep used (HOLD|CONFIG FAIL|FAILED|no train.py cmdline).
- **Not done:** stage 2 (the opening build: R's scoring passes, D's ensemble inference, the seed-aware bootstrap, frozen md5s before any S2C number) has not started. **Nothing has been scored. E1 opening #7 is registered, NOT OPENED** (`e1_openings.md` 365d62f3), and opens only on the user's explicit OK.
- **Reading (S):** the training half of SKR2C ran clean and unattended under the guard; its value now depends on the opening. The chances stated at lock still apply (§2.1).

## 3. Docs commit, agent closures, the tmux move
- **3604dc7** (3 Nov 02:49, previous scribe; 384 files): `SESSION_RECORD_2026-11-01_to_11-03.md`, handbook doc 21 and additive updates, team folder text. judge's fact-check (11 fixes F1-F11) was applied and re-checked OK at 02:48. It records SKR2C as of ~02:45 (nothing launched). Files that changed after it (protocol_SKR2C §9, build_s2c v3, the stage-1 review's re-review, the s2c scripts and dry logs) are committed now (§13).
- **Agents closed:** team-lead closed scribe, judge, coach and runner at ~03:10 (log 03:10), per the user's line. judge had been unreachable since ~02:59.
- **Move to `orch-mtp` (team-lead's account, message to scribe 12 Nov; no log line or file records it):** the session moved into a laptop tmux session `orch-mtp`, so the user can drive the orchestrator by voice through Herald (the user's chat-to-Claude-Code bridge). The permission classifier blocked team-lead's own tmux launch as a persistence action, so the user ran the command themselves. The time is not recorded; it lies between 3 Nov ~03:10 and 4 Nov 11:56. On 12 Nov no `orch-mtp` session exists (`tmux ls` shows only `claude-swarm`, created 12 Nov 14:42; E).

## 4. The thermal team: brief, roles, rules, outputs (`team_2026-11-04_thermal/README.md` 45ca3b69)
- **Om's brief (`om_2026-11-04_thermal.md` 6677bc9f, verbatim, written 3 Nov, pasted by the user 4 Nov):** launch OPTIMISTIC, generative agents on integrating thermal (IR) imaging: (1) public datasets with paired or co-registered EL and thermal (also EL + PL / UVF / RGB), with size, resolution, labels, licence and cell-level alignment; (2) every way thermal could help our EL segmentation (fusion, cross-modal pretraining or distillation, weak labels for inactive and hotspots, EL-to-thermal synthesis, unseen-panel generalisation, the industrial pipeline: drone IR to screen, EL for detail); (3) whether WattCycle or IIT Mandi could capture paired EL + thermal. "Look for ways to make it work"; tag E / R / S; read-only servers, no downloads and no GPU without Om's OK. Deliverable: a team folder with a dataset table, a ranked idea list and a top 3 with first steps.
- **Roles (README):** datascout (Om's 1) → `datasets/`; ideas (2) → `ideas/ideas_long.md`, 25+ ideas; capture (3) → `capture/capture_plan.md`; synth (after those three) → `synth/ranked_ideas.md`, `top3.md`, `SUMMARY.md`; check (after synth, in practice in parallel) → `check/factcheck.md`, correcting facts and tags without killing ideas. team-lead orchestrates and relays.
- **Rules (README):** no downloads (pages, metadata and abstracts only; full text for a short list); servers not needed, no ssh; no GPU without Om's OK; no outside contact (questions go into the outputs for Om); no manual labelling asks; do not name the 3 Hanifi B2 panel cells or open the B2 files; no test or E1 reads; no pattern kills; log with `date` stamps; plain English, no em-dashes.
- **After Om's decisions (team-lead 12:39-12:40, log and retrospective):** datascout = download + verify, then pick 1 executor; ideas = `drone_only.md`, then pick 3 executor; capture = pick 2 re-plan; synth = integrate; check = plan reviews, download check, re-plan fact-check. Download scope = exactly `synth/top3.md` l.29-42; disk floor 4.0 GB free; targets `~/mtp/datasets/thermal_public/<set>/` in new empty dirs, `python -I`, nothing run from inside data dirs.
- **Outputs (md5 at session end):** `datasets/dataset_table.md` 7a48fc3b, `notes.md` 66a25beb, `download_plan.md` 409481f7, `download_selection_A1.tsv` da419f33, `download_verified.md` 645d7cfc; `ideas/ideas_long.md` ba9c0038 (v1.2), `drone_only.md` 50a13aeb (v1.1); `capture/capture_plan.md` 66d2270b (v1.3), `replan_pick2.md` 9d6a4885 (v1.2); `synth/ranked_ideas.md` d36d70f7, `top3.md` fa6da29f, `SUMMARY.md` 00f17af7 (final for Om), `ADDENDUM_2026-11-04.md` 878e6bec (**DRAFT**); `check/factcheck.md` 879f35fa; pick 1 and pick 3 files (§8, §9).

## 5. Desk-study findings

### 5.1 Datasets (`datasets/dataset_table.md` v3; check pass 1 D-items applied). Licences and counts are R unless tagged.
| # | Set | Modalities and pairing | Size | Labels | Licence |
|---|---|---|---|---|---|
| A1 | UCF DPV, OSF `csr6t`: 10-year Florida rooftop, Shell M55 mono Al-BSF (paper: Colvin et al., IEEE JPV 2023, doi:10.1109/jphotov.2023.3238278) | EL bias sweep (6 currents; Nikon NEF), indoor forward-bias IR at 3.392-3.393 A (~1 × Isc), 180 s by file names (Colvin says 5 min; unresolved), UVF, I-V, EL-derived per-cell dark I-V; module-level pairing by serial | 156 modules characterised; IR for 157 (473 files, 0.26 GB); EL folder 1,044 files, 14.95 GB; UVF 159 jpg, 2.01 GB; dark I-V 158 txt + 1 xls, 3.8 MB. 36 cells, **3 × 12** (E) | none as masks; per-cell dark I-V | CC BY 4.0 |
| A2 | UCF DPV, OSF `ar76v`: 19-year Orange County Convention Center, SolarWorld mono Al-BSF | EL at 6 currents; forward-bias IR at 5.289 A, 60 s (one module 5.089 A); module-level | 42 modules; IR 16 captures of 15 modules (0.02 GB; "the camera suddenly failed"); EL 270 NEF, 3.82 GB. 72 cells, 6 × 12 (E) | none | CC BY 4.0 |
| A3 | DTU drone IRT dataset (figshare 10.11583/DTU.29665346; EPJ PV 2025, doi:10.1051/epjpv/2025020) | drone IR (DJI Mavic 3T) at 8 / 10 / 14 / 20 m and 200-1000 W/m², EL, STC I-V; module-level, folder per defect | 43 modules = 31 degraded + 12 soiled (slides); cracks 8 (69 cracked cells, 4-5% loss), interconnects 8 (98 cells, 3-14%), PID 6, bypass diode 7, glass 2, soiling 6 + 6; archive 642.6 MB | module class by folder | CC BY 4.0 |
- **Others:** B (EL + PL) 5 rows (B1 csr6t close-ups; B2 Redondo-Plaza outdoor EL / PL; B3 NREL BEST; B4 PLatypus field PL; B5 856 half-cut PL images); C (EL + visible / NIR) 4 rows, of which only C1 (Polenghi et al., 84 progressive damage stages, pixel-aligned EL + NIR + HDR, CC BY 4.0, ~1.38 GB) pairs the same cell; D (thermal-only with labels) 12 rows (e.g. D1 Raptor Maps 20,000 crops, MIT; D4 PVF-10; D11 Indian-plant drone thermal ~19.1 GB; D12 sUAS IR 3,675 crops); E (in papers, not released) 12 rows. The DuraMAT Data Hub was unreachable on 4 Nov.
- **Bottom line (S, datascout):** no public set gives pixel-registered EL + thermal at cell level with crack / inactive masks. About 215 modules have IR (A1 157, A2 15, A3 43; check D-24); about 203 have both EL and IR, since A3's 12 soiled modules have IR but no EL (A3 counts 31; E, discovery 13:48). Enough for a feasibility study of cross-modal weak labels and a demo pipeline, not for training a fusion model at scale. A1 / A2 are old mono Al-BSF full cells; A3 has half-cut bifacial PERC modules only in its diode, glass and soiling groups, none in its crack group; no set is known to show scuff.
- **Where they live now (E, 12 Nov):** `~/mtp/datasets/thermal_public/` (§7).

### 5.2 Physics: what thermal shows vs EL for our classes (ideas §0, synth §0; tags as given)
- **Crack that isolates nothing** (Köntges mode A by mapping, S): no hot spot in Dhimish 2021 / 2022 (R: doi:10.1038/s41598-021-03498-z, doi:10.1038/s41598-022-16546-z); in drone IR "modules with cell cracks are difficult to distinguish from healthy ones" (R: DTU EPJ PV 2025); cracked cells differ by at most ~1 °C (R: DTU 2025 via capture). Only active methods (e.g. ultrasound lock-in) heat the crack itself (R).
- **Inactive / isolated area:** carries no current, so under forward bias in the dark it should read cooler, and in sunlight warmer (S, device physics); in Dhimish 2021 temperature rose from 25 °C to 100 °C for crack modes 3 / 4 and up to 105 °C at 40-60% shading (R, abstract, check P-1). Disconnected interconnects are visible from 600 W/m² (R, DTU).
- **Scuff:** no physical description in our files (E, handbook doc 17 §5.11); if it is a surface mark it should be thermally silent (S, untested). So thermal alone cannot split scuff from a thin crack; UVF (crack lines in aged encapsulant, R), PL (isolated regions still emit, S) and RGB carry that split.
- **Seen directly by thermal (R):** shunts and pre-breakdown sites, solder-bond failures as point-like heating, series-resistance defects, PID-shunted cells, hot diodes / substrings.
- **Calibration (R, JRC 2017 via check D-46):** dark IR gives "few local information"; illuminated IR separates damage classes in line with EL. So a weak dark-IR result is expected and is not a kill for illuminated IR.
- **Resolution (R):** drone IR at ≤ 3 cm/px is a cell-level signal (~5 × 5 to 16+ px per cell); indoor and lock-in IR are finer.
- **Net (S, ideas and synth):** thermal is a strong cell-level signal for inactive area, hot spots and severity, and a weak or null pixel-level signal for cracks and scuff. Its value for our segmenter is as a training-time teacher, weak label, triage stage or severity output, not a crack-pixel input. BenchmarkEL, test and E1 have no thermal (E), so any benchmark gain must come from an EL-only model trained with paired data.

### 5.3 Ideas: 40 + 14 (`ideas/ideas_long.md` v1.2; `ideas/drone_only.md` v1.1)
- **T01-T40 in 8 families:** fusion (T01-T05), cross-modal pretraining / distillation (T06-T11), weak labels (T12-T16), synthesis (T17-T21), unseen-panel generalisation (T22-T25), industrial pipeline (T26-T30), other modalities (T31-T36), data / benchmark / evaluation (T37-T40). Each has mechanism, targets (SC scuff + half-cut, UR unseen recall, IN inactive, DE deployment, SV severity), data, cost, first experiment, kill and E / R / S tags.
- **Shared gate G0 (ideas §1.1):** is there a thermal signal at cell level? Kill for the fusion / weak-label families only if |ρ| < 0.3 and AUROC < 0.7 in **both** dark (A1 / A2) and sunlit (A3) conditions; go if AUROC ≥ 0.8 with the predicted sign in either.
- **Honest limits (ideas §3):** no direct fix for scuff + half-cut crack recall; no gain on test or E1 from thermal inputs; pretraining routes start with a weak prior (E: A8 KILL, MIM n.d., P15 null); cell-level, not pixel-level.
- **E check (ideas, reproduced by check):** UCF-EL annotations hold 373 module ids, 201 with exactly 60 cells (not A1's 36-cell modules); 172 partial, 109 of them with highest position ≤ 36, so a UCF-EL ↔ A1 link (T38) is not excluded.
- **Drone-only W01-W14 (after Om's decision):** IR-ranked EL queue with pre-registered predictions (W01), module ID map + half-cut survey (W02), physics-rule baseline (W03), public-trained IR model (W04), A3 irradiance / altitude normalisation (W05), repeat-flight noise floor (W06), IR → expected-EL mapper (W07), operating-point differential IR (W08), shading test (W09), close-range IR (W10), UV-torch UVF (W11), RGB (W12), soiling filter (W13), natural transients (W14).

### 5.4 Ranking and the top 3 (`synth/ranked_ideas.md` v1.4 d36d70f7; `top3.md` fa6da29f; `SUMMARY.md` 00f17af7)
- **Score (all S):** V × P / √effort. 58 rows after merging: 38 T (T22 / T34 merged into X1) + 7 X (X1-X7, from datascout and capture) + 13 W (W07 merged into T19). No idea dropped.
- **Top of the table:** 1 T26 (drone / forward-bias IR screening, then EL), 2 T37 (registered A1 cell-level EL + IR + UVF set), 3 T15 (A1 dark I-V as a physics label), 4 W03, 5 T27, 6 W02, 7 W01, 8 T02, 9 X3 (Polenghi C1 severity check), 10 W11.
- **Physics reshaped the order (S):** up = screening, severity, inactive, and the scuff arbiter with UVF; down, not killed = crack-pixel fusion and thermal pretraining.
- **Top 3 (S picks, spread over risk):**
| Pick | What | Data / cost | Kill if (pre-stated) |
|---|---|---|---|
| 1 | What thermal catches: IR screening vs EL on A3 / A2 / A1 (T26 + G0 + T27 + T39) | public ~1.2 GB; ~6-7 dev d CPU; 0 GPU | top 20% IR-ranked modules hold ≤ 20% of EL dark area; G0 null in both conditions |
| 2 | WattCycle drone thermal now, low-cost EL soon (W02, W03, W01, W08, W11; X6 → X1 / X2) | 1 visit day + 1 night; ~8-10 dev d; ~₹27k-30k kit | module re-ID < 90%; no UVF lines on aged modules; X6 cracks not visible at ≤ 120 s stacked |
| 3 | Inactive from physics labels: T15 → T02 → T12, T37 as output | same download; ~9-10 dev d; ~5.5 GPU-h only if gated | valid cells < 50% or no spread; < 50 flagged cells or purity < 70% |

### 5.5 Capture plan and re-plan (`capture/capture_plan.md` v1.3; `replan_pick2.md` v1.2)
- **WattCycle (R, capture §1.1):** WattCycle Sustainable Solutions Pvt Ltd, founded June 2025 by an IIT Mandi associate professor, registered office Kamand, Mandi; PV-recycling startup; site lists drone thermal + RGB monitoring, a digital-twin platform (Atlas) and a recycling service (ReVive). Om confirmed the company on 4 Nov. (capture first flagged a conflict with the local docs' "solar asset-management company" wording, doc 01; check C-5 resolved it toward a match via the Atlas manual, with a caveat: the Atlas app runs on demo seed data, so it does not show that real drone IR archives exist.) IIT Mandi's central facility list shows no IR camera, EL rig or solar simulator (R).
- **Original P0 (before Om's decision):** 1 day, 5-6 recycler modules (≥ 2 half-cut, ≥ 2 with scuff-like streaks, 1 inactive, 1 healthy): EL at 0.1 and 1.0 × Isc, dark IR under the same bias (256 × 192 phone microbolometer), UVF, RGB, Al-tape fiducials + homography; ~₹45k-55k of new kit if an EL rig exists; no labels needed. P1: 4-5 days, 15-20 modules (bias sweep, low-cost lock-in, reverse bias on 2-3 sacrificial modules, outdoor / drone IR, I-V). 16 questions for Om.
- **Re-plan after Om's decision (WattCycle has drone thermal only; EL rig 2-3 months away):**
  - drone IR is a triage and pairing tool, not a crack labeller (R: DTU 2025: cracks ≤ ~1 °C; interconnect breaks from 600 W/m²; diodes / soiling > 10 °C even at 200 W/m²);
  - now: a fixed flight protocol (≥ 600 W/m², wind < 28 km/h, ≤ 3 cm/px survey, ~10 m cell passes, radiometric R-JPEG), a module ID map with a half-cut survey, physics-rule scores calibrated on A3, a frozen pre-registered EL queue, ground tests on end-of-life modules (operating-point IR, shading, close-range IR, night UVF with a ₹2k-5k torch);
  - EL sooner (S): Raspberry Pi HQ camera (IR-cut filter removed) + Pi 5 + C-mount lens + 850 nm long-pass + 300 W OWON supply, ~₹25k plus lens and filter, bench test in W2, first EL night W3-4 (Si sensitivity near 1,150 nm unconfirmed); fallback ZWO ASI678MM ₹62,145; NISE Gurugram per-module EL + STC (fee not public); drone EL needs a SWIR camera (~€10k-15k), so no;
  - 20 questions Q1-Q20 for WattCycle / IIT Mandi plus U1-U3 for dataset authors (SUMMARY §4).
- Weeks used: W1 = 4-10 Nov ... W7 = 16-22 Dec (synth's reading of team-lead's "about 7 weeks left"). On 12 Nov (W2) none of the pick 2 steps had started, because the questions were never sent (§12).

### 5.6 Fact-check counts (`check/factcheck.md` 879f35fa, §1-37; there is no §16 or §19)
- **Pass 1 (datasets, ideas, capture):** 110 items: OK 73, FIX 31, UNVERIFIABLE 6. Key upgrade: A1's IR is bias-matched forward-bias IR on ~157 modules at 3.39 A with EL at the same current; A1's paper is Colvin 2023, not Li 2024 (a separate 9-module study). All FIX items applied and re-checked (§8).
- **Pass 2 (synth v1.1):** 33 items: OK 13, FIX 18, UNVERIFIABLE 2 (the 12:44 log line said 14 / 17; corrected 12:45). Sizes recomputed from listings: picks 1 + 3 = 1.19 GB.
- **Pass 3 and later (§10-36):** plan reviews (pick 3 v0.9 / v0.95, pick 1 v0.9, pick3b v0.95), drone_only and replan fact-checks, the pick 3 v1.1 audit (§17), independent recomputes (T15 §20; G0 v1 from cell tables §22 and from raw files §24; G0 v2 §36), download verification (§23; A3 in the log 13:48), cellreg reviews (§25, §28, §30, §32), QA co-signs (§26, §34), the Colvin 2023 full text (§31), the A1 report review (§33). §37 "Still to come" and §9 were not updated before the session ended.

## 6. Om's decisions (4 Nov; `om_2026-11-04_decisions.md` b5f143bb, verbatim)
1. **DOWNLOAD APPROVED** for picks 1 and 3: A3, the A2 subset, the A1 subset with dark I-V; about 1.2 GB, CPU only, check disk space first. The later 0.55 GB A1 extension still needs Om's OK. Start picks 1 and 3.
2. **WattCycle** is confirmed as WattCycle Sustainable Solutions, but it has ONLY a drone thermal setup now; its EL rig is 2-3 months away. Re-plan pick 2: P0 paired capture is not possible soon. Ask the team what can be done now with drone thermal alone, and whether there is a realistic low-cost way to get EL sooner. Update the WattCycle question list.
3. **Still open for Om:** E-PF inference location (gaint CPU vs local); licences / release; capture funding. E-PF inference was therefore HELD; picks 1 and 3 ran on EL-only proxies.
- Om asked for a report "when the downloads are verified and the re-plan is written". Both conditions were met by ~13:48, but **the report was never sent** (team-lead's end-state line, 12 Nov).

## 7. Downloads (`datasets/download_plan.md` 409481f7; `download_verified.md` 645d7cfc; check §23 and log 13:48)
| Set | Local dir | Files | Bytes | Verification |
|---|---|---|---|---|
| A1 OSF csr6t | `~/mtp/datasets/thermal_public/A1_osf_csr6t/{darkIV,EL,IR,UVF}` | 209 (darkIV 159 incl. `diode_fit_outputs.xls`; 10 modules × 5 files) | 286,886,436 | size + md5 + sha256 vs OSF published hashes: 209 / 209 (datascout; check independently) |
| A2 OSF ar76v | `.../A2_osf_ar76v/{IR,EL}` | 47 (IR 32 = 16 captures; EL 15 NEF at each module's IR current) | 237,009,189 (IR 15,706,079 + EL 221,303,110) | 47 / 47 (both) |
| A3 DTU figshare 29665346 | `.../A3_dtu/{archive,extracted}` | `IRT DATASET.7z` + README; extracted 1,414 files in 94 dirs (640 IR `.raw`, 31 EL `.nef`, 640 `.png`, 33 I-V `.csv`, 12 `.jpg`, 57 `.db`, 1 `.md`) | 642,610,942 + 1,161; unpacked 1,162,474,935 | figshare supplied = computed md5 (7z 2ca8adbc..., README 8dd0b5ce...); 7z CRC on extraction; check re-verified every file's size + CRC32 |
- **A1 selection rule (frozen da419f33 before any image download):** eligibility on listings (155 of 158 dark-I-V modules); severity s = median − min of the EL-derived cell voltage at ~3.393 A; 5 quintile bins × 2 with `default_rng(20261104)`; bin 5 always takes the max-s module. Picked: 6330431031, 6330431038 (bin 1), 6330431484, 6330431480 (2), 6320427398, 6330431479 (3), 6320427793, 6320427802 (4), 6320427439 (max, s 19.32 mV), 6320427227 (5). Bins (mV): 2.6-4.9 / 4.9-5.8 / 5.8-6.9 / 7.0-8.4 / 8.4-19.3.
- **Disk:** 6.9 GB free at 12:43; 4.6 GB at 13:39 (other sessions' scratch; ideas pruned 542 MB and check 171 MB by explicit path); 5.586 GB before A3 extraction (`df -B1`); 4.423 GB after (4,415,332,352 B in check's ADDENDUM; datascout's later df reading "4.2 GB"), above the 4.0 GB floor, so full extraction (team-lead's rule).
- **Not downloaded:** the A1 extension (0.55 GB; and ideas' proposal of all 157 A1 IR, 0.26 GB, then ~2 GB EL), W04 drone-IR sets, Polenghi C1, A1 close-ups. All need Om's OK.
- **12 Nov re-check (E, scribe, read-only):** `md5sum -c` of each `MANIFEST.md5` (A1 210 lines, A2 48, A3 1,416): **0 failures**; 1,677 files, 2.2 GB (`du`). The data survived the OS reinstall. The analysis venv (`~/mtp/research/.venv`, Python 3.12.16, numpy 2.5.3, scipy 1.18.1, skimage 0.26.0) still runs; system `7z` is present.

## 8. Pick 1: what dark IR catches (`pick1/plan_pick1.md` fb46b6dc = v1 + Amendments 1-6; owner datascout)

### 8.1 Plan and amendments (all frozen by md5 in the log before the numbers they govern)
- **v1** ff541f0e → 28b58cc9 (12:56; one wording fix, before any data value): readouts R1 (A3 module IR screen by defect class), R2 (A3 screening recall of the EL dark area), R3 (G0 on A2, then A1, cell-level), R3b (sunlit G0 on A3), R4 (T27 / T39, held: need E-PF). Disclosed priors: 3 dark I-V values seen while writing the download plan; the DTU abstract and slide ΔTmax values.
- **Amendment 1** a15275a5 (13:00): grids are symmetric, so EL ↔ IR orientation is ambiguous; primary = identity, 4-orientation robustness with a best-of-4 permutation null; "orientation unresolved" if another beats it by > 0.15 AUROC with p < 0.01.
- **Amendment 2** 18b60398 (13:02): cellreg v0.2 c8b4343a; one IR capture per module (nearest in time to EL).
- **Amendment 3** e9f5376c → 8983bc9d (13:05-13:07): A1 is 3 × 12; the authors' `_cropped.txt` is exactly the raw IR window rotated 180° for 10 / 10 modules; primary orientation **rot180** for A1 (from the authors' crop) and A2 (same lab and IR rig, S); decided from non-outcome evidence only.
- **Amendment 4** 85270857 (13:14): row / column-centred ΔT secondary (pre-stated for A3; post hoc for A1 / A2); visual overlay QA of every module, blind to per-module G0; G0 to be recomputed with cellreg v0.4.
- **Amendment 5** d1e6777b (13:43): "module-rectified" A3 IR is S; R3b quad = Otsu outline + detected grid + v2 QA; border-vs-outline offsets logged at discovery.
- **Amendment 6** fd98e232 → fb46b6dc (13:50; after A3 discovery, before any R1 / R2 / R3b number): A3 IR arrays are 605 × 363 portrait °C, 16 frames per degraded module (4 altitudes × bins 200 / 600 / 800 / "abv800" W/m²), 12 for soiling; **the module fills the array, so Otsu finds hot regions, not the edge (offsets 10-537 px)**: R1 uses the whole array with a 3% inset; R2 counts unlit diode cells as dark; R3b on the 24 full-EL modules (cracks, interconnects, PID, glass) with `--quad-ir full`, IR turned 90°, all 4 orientations, best of 4 vs a permutation null; predicted sunlit sign = EL-dark cells warmer. Layouts from EL: 60-cell 6 × 10 (cracks, interconnects, PID), half-cut 6 × 24 (glass); diode EL shows only the lit substrings.

### 8.2 G0 v1 (frozen; `pick1/out/G0.md` 8aa10e14, `G0_v1_frozen.json` 1da5ae53; cellreg v0.2, `g0_stats` 27f7bff1)
- Features: ΔT = inner-80% median minus the module median of cell medians; EL dark fraction = inner-90% share < 0.5 × module median (after an opening); positive = dark fraction ≥ 5%. QA: exclude a module if EL or IR residual > 5% of a cell side. EL = NEF embedded JPEG preview (tone-mapped, 8-bit), so dark fractions are approximate.

| Set | Modules kept | Cells / EL-dark | ρ(ΔT, dark) | AUROC (cooler) | Inner: n / pos / ρ / AUROC | Verdict (frozen R3) |
|---|---|---|---|---|---|---|
| A2 (6 × 12, 5.289 A / 60 s) | 9 / 15 | 648 / 230 | −0.550 | 0.736 | 360 / 96 / −0.554 / 0.757 | between (predicted sign, below the 0.8 go bar) |
| A1 (3 × 12, 3.39 A / 180 s) | 7 / 10 | 252 / 50 | −0.285 | 0.689 | 70 / 13 / +0.042 / 0.528 | null |
| Pooled | 16 | 900 / 280 | −0.451 | 0.708 | 430 / 109 / −0.475 / 0.718 | between |
- Orientation: A2 id 0.446, fliph 0.433, flipv 0.762, rot180 0.736 (best of 4 p 0.001, null q95 0.555); A1 0.619 / 0.595 / 0.710 / 0.689 (p 0.001). Not "unresolved". A2's second capture of 409001724: 0.731 / −0.544.
- QA exclusions: A2 6 / 15 (40%); A1 3 / 10, including the most severe module 6320427439 (EL 7.59 / IR 7.30%). Failures hit degraded modules more (S).
- **check:** recomputed from cell tables (§22) and independently from the raw NEF + IR files with its own reader and warp (§24, `g0_recompute.py` 706862a5): **MATCH** on every value; QA gate applied as frozen. Wording fix accepted: **the dark condition is not null overall (A2, pooled), so G0 cannot be killed by A3**, whatever A3 shows.
- **Interim re-run (13:17, NOT COUNTED; QA not co-signed):** A2 8 / 15 AUROC 0.705; A1 4 / 10 0.756 (< 5 inner positives, edge-sensitive); pooled 0.704 (`G0_results_visualqa_v02.json`).

### 8.3 The post hoc row / column finding (check §22 G0-3, 13:13; labelled post hoc for the dark arm by team-lead)
- Subtracting each row's median within a module makes all orientations agree on A2 (ρ −0.42 / −0.44 / −0.46), so the orientation dependence is top-bottom structure.
- **Subtracting row and column medians removes the signal everywhere:** A2 ρ −0.07 to 0.00, AUROC 0.49-0.52; A1 ρ −0.17 to +0.05, AUROC 0.52-0.57 (E).
- **Reading (S):** the dark-IR signal is carried by row and edge patterns, not single cells. That fits real string / edge degradation, and equally fits shared artefacts (convection gradient, EL top-bottom gradient, frame heat-sinking, vignetting).

### 8.4 G0 v2: post hoc instrument fix (`pick1/out/G0v2.md` 06d1970b; `G0v2_primary.json` f1e904e7, `G0v2_sensB.json` efe6f4ee; `G0v2_run.md`)
- **What changed (instrument only):** frozen reviewed cellreg v0.4.1 (`scripts/frozen/cellreg_7d9a9fe0.py`), no UVF; QA = residual ≤ 5% + written visual criteria (`qa_v04/visual_qa_v04_criteria.md` fae36d53, written 13:23 before any v0.4 run, addendum 13:26) + a numeric edge check (0.25 cell vs the set median); calls from overlays / reg.json only (`visual_qa_v04.tsv` 8557c658), co-signed blind by check (§34; one flag accepted: A2 409001724 EL borderline); keep lists frozen before computing (`keep_v2_primary.tsv` 484fa349, `keep_v2_sensB.tsv` db548f73); stats `scripts/frozen/g0_stats_0190cba5.py`.

| Set | Modules | Cells / EL-dark | ρ | AUROC (cooler) | Inner: n / pos / ρ / AUROC | Row/col-centred ρ / AUROC (post hoc for the dark arm) | Verdict |
|---|---|---|---|---|---|---|---|
| A2 | 4 / 15 | 288 / 75 | −0.515 | 0.732 | 160 / 38 / −0.501 / 0.739 | −0.021 / 0.525 | between |
| A1 | 4 / 10 | 144 / 36 | −0.246 | 0.621 | 40 / 7 / +0.168 / 0.394 | +0.231 / 0.343 | null (inner agrees) |
| Pooled | 8 | 432 / 111 | −0.403 | 0.687 | 200 / 45 / −0.369 / 0.681 | (check: 0.462) | between |
- Sensitivity B (keep + 6 borderline modules; no verdict): A2 8 modules 0.737; A1 6 modules 0.659; pooled 14: 0.706, ρ −0.431.
- Orientation: A2 flipv 0.760 vs rot180 0.732; A1 id 0.709 vs rot180 0.621 (gap 0.088 < 0.15); p 0.001 both; not unresolved. A1's best orientation moved from flipv (v1) to id (v2): weakly determined (S, check §36).
- **check §36 recomputed every value from raw files (`g0v2_recompute.py` f5499938): MATCH.**
- **Verdict:** same as v1: **not a go, not a kill.** Readings (S unless tagged): not cell-level on A2 (centred AUROC 0.53), so the v1 finding was not a misregistration artefact; on A1 (post hoc) the centred AUROC(cooler) 0.343 means EL-dark cells read slightly **warmer** than their row / column peers, which fits A1's resistive current crowding (R, Colvin 2023) and is the expected sign for series-resistance defects, opposite to the inactive expectation (4 modules, 36 positives; descriptive only). Consistent with Colvin 2023 Fig. 5 (module SD of dark-IR temperature vs power-loss rate, R² 0.429; R via check §31): dark IR carries module- and row-level information on these sets, not a cell-level inactive flag.

### 8.5 A3 discovery (structure only; log 13:47-13:50; Amendment 6)
- 43 modules by folder: cracks 8, interconnects 8, PID 6, glass 2, diode 7, soiling 6 + 6. IR 640 float32 arrays (605 × 363 portrait, °C). EL 31 NEF (one per degraded module, previews 6000 × 4000; exposures 2 s × 5, 5 s × 24, 6 s × 2, no current in names). I-V `Mod<n>_IV_<defect>.csv`, columns V, I only (~522 rows; README: mean of 3 at STC). No module type in names, README or I-V files. `A3_border_vs_outline.tsv` a8be5b7e holds the offsets.
- **Not computed before the session ended:** R1 (module IR screen), R2 (screening recall), R3b (sunlit cell-level G0), the A3 module table that pick3b needs, and R4 (held: E-PF). `pick1/out/discovery/A3_layout.tsv` is an empty file (13:51:39).

## 9. Pick 3: physics labels for inactive (`pick3/plan_pick3.md` v1.2 2893a817; notes 3679075c; `pick3/out/PICK3_A1_REPORT.md` 55fcf923; owner ideas)

### 9.1 Plan freezes (all before any data value was read by ideas, apart from the 3 dark I-V values quoted in datascout's download plan, disclosed)
- v1 edb8ae37 (12:53, removed within a minute to fix hand-typed times) → v1 5c272fe9 → **v1.1 6e9d9af2** (12:56: post hoc self-test criteria, disclosed) → **v1.2 2893a817** (12:59: §7 disclosure of the v1.1 timing and the post hoc bars). Notes N1-N8 add disclosures and procedures without rule changes (N7: the T37 v2 rule, post hoc; N8: tool status, the label-direction finding, the ordering route).

### 9.2 T15: A1's EL-derived per-cell dark I-V as a physics label (E: `t15_summary.json` 320ad9e9, `t15_cells.tsv` c365ce09)
- Format discovery: 158 txt files, each 36 (voltage, current) column pairs × 7 rows (6 currents + a zero row; check §20); P = the cell's voltage at the highest current (3.392-3.393 A); d = module median P − P.
- **Rule (frozen, plan §3.1):** kill if coverage < 50%, or "no spread" = robust SD(d) < 0.1 V_t (2.57 mV) **and** < 1% of cells with d ≥ 1 V_t. The second clause was met by construction (datascout's module maximum 19.3 mV < 1 V_t was on record before the read; notes N3, plan §7), so the kill rested on the SD clause alone.
- **Result: coverage 5,688 / 5,688 = 1.00; robust SD(d) 3.26 mV (0.127 V_t); share d ≥ 1 V_t = 0 → PASS, narrow** (0.69 mV over the line; ideas first wrote 0.66 / 2.6, corrected 13:39). check's independent recompute (`t15_check.py` 972c7210): 3.258 mV, 569 D90 cells: MATCH; plan v1.2 frozen 12:59:20 before the readout files (12:59:28-12:59:49).
- Labels: D90 = d ≥ 4.23 mV, 569 cells; DVt = d ≥ 1 V_t, 0 cells (by construction: the selection capped d below 1 V_t, disclosed before the read).
- Descriptive (`t15_descriptive.json` 00919df8): d p50 / p75 / p90 / p95 / p99 / max = 0.0 / 2.13 / 4.23 / 5.61 / 8.62 / 19.32 mV; D90 cells in 144 of 158 modules; top 10 modules hold 18.6%. Reading (S, ideas): D90 marks each module's dimmest ~10% of cells at ~1.18× EL dimming, a diffuse label that may include measurement noise.

### 9.3 T37: registered A1 cell set (10 modules)
- **v1 (cellreg v0.3 cb9ad392; `t37_v03_summary.json` fbd466d2):** rule = exclude a module if EL or IR inner residual > 5% of a cell; pick kill if > 30% excluded. 3 / 10 excluded (6320427439 EL 7.59 / IR 6.81; 6330431480 IR 8.12; 6320427398 IR 9.73) = 30% → **PASS at the line.** Visual QA (S): 6320427227's EL grid was stretched past the module edge at a passing 4.49% residual, so the residual measured fit consistency, not true error. UVF: 9 / 10 over 5% → the UVF part fails as built.
- **v2 "post hoc instrument fix" (cellreg v0.4 95e0ca3e; `t37_v04_summary.json` 0d60bd16):** the frozen 5% rule excludes **4 / 10 = 40%** (IR 6320427227 6.66, 6320427398 7.22, 6320427439 5.40, 6320427802 7.57) → over the 30% line; N7's grid-vs-outline rule (≤ 20%) excludes 10 / 10 (EL 23.9-35.4%, IR 44.6-81.7%) → **FAIL on both** (check CR-3; CR-4: the N7 bar is miscalibrated, the Otsu outline sits off real grid corners).
- **Likely root cause (check §28 CR-5; the crop geometry is E, its role in the IR residual rise is S, CR-5's "likely cause"):** the authors' `<serial>_cropped.txt` is a **fixed 134 × 35 px window** of the raw 240 × 320 IR (cols 90-223, rows 137-171) for 9 of 10 modules, rotated 180°; the module's warm region is ~144-146 × 36-37 px, so the crop trims ~0.9 cell horizontally (6330431480 misses ~0.9 row). With `--quad-ir full`, 12 columns were forced into 134 px (~7% pitch error), and v0.4's anchoring locked it in. ideas' N5 premise ("the crop is the module") was false. Fix for any future A1 work: raw-frame registration with the Otsu outline (as pick 1 does).
- **Label direction (R, Colvin 2023 §II.A / §III.B, verified in full text by check §31):** each cell's voltage comes from "a bright pixel from each cell", and "cells with bright spots in high injection EL show higher RS values"; so a degraded high-RS cell may show a **higher** EL-derived voltage, and the frozen "lower = worse" direction may be inverted for A1 (S, CV-6). The frozen D90 stays; it reads as "dimmest bright-pixel voltage", not "degraded".

### 9.4 Decision (A) and the A1 report
- **team-lead decision (A), 13:28 (team-lead's retrospective, from its message timestamps; the report says "~13:3x"):** the A1 arm stops at T37 as pre-registered; T02, T12 and R34 are **not run** (no value ever computed); redirect to pick3b on A3 under a new plan frozen before extraction. Option B (a third, post hoc registration v3 on the authors' crop) was not taken: it rested on the false crop premise and would add a forking path for a likely null (team-lead; check §29).
- `PICK3_A1_REPORT.md` 2eb8400b (13:36) → 12b21653 → **55fcf923** (13:39, check's §33 fixes). Its readings (S with R): the T15 label is a diffuse small resistive deficit, not inactive area (A1 losses "primarily resistive", R), so the A1 arm cannot speak to inactive; dark IR tracks rows and edges (pick 1).

### 9.5 pick3b on A3 (`plan_pick3b_v1_FROZEN_eaec6f26.md`, frozen 13:43 before A3 extraction)
- **Readouts:** 3b-R1, does the EL dark proxy track measured power loss (module level; label-valid if ρ ≥ 0.5 with CI lower bound > 0; label-invalid if ρ < 0.3); 3b-R2, does drone IR (pick 1's S_IR) track power loss and add to EL (proxy if ρ ≥ 0.5; adds if ΔR² ≥ 0.10 with CI lower > 0); 3b-R4, a two-current EL label (persistent-dark vs resistive-dark), only if two EL currents exist; 3b-R3, cell-level +ΔT AUROC stratified by induced cause (interconnect primary: success AUROC ≥ 0.8 and centred ≥ 0.7; kill < 0.7 and centred < 0.6), reusing pick 1's QA-passing R3b cells, no re-registration. Diode modules can drive ρ alone, so every module readout is also reported without them; known before the freeze and disclosed: per-class power losses (cracks 4-5%, interconnects 3-14%, PID 5%, diodes 33-66%, glass < 1%), so a non-diode ρ < 0.3 reads "label range too narrow".
- **Discovery (13:48-13:49, structure only):** 31 non-soiling modules with exactly 1 EL each, no current in names → **3b-R4 NOT RUN** by the frozen rule; no module type anywhere → ΔP vs nameplate not computable, so by the frozen fallback **FF loss (1 − FF / median FF over non-soiling modules) is the primary label**; soiling: 2 modules with field I-V, no EL (excluded). `scripts/pick3b_r12.py` dac5842b written and smoke-tested on synthetic data only; not run on A3.
- **Conflict left open (E):** pick3b v1 §5 reuses pick 1's R3b cells only if pick 1 registers A3 IR with the Otsu outline, "else a dated amendment, written before any 3b-R3 value". pick 1's Amendment 6 (13:50) dropped Otsu for A3 (`--quad-ir full`). A v1.1 freeze was attempted at 13:51:49 (`plan_pick3b_v1.1_FROZEN_c8f57302.md`, **0 bytes**; content lost and unknown), and `plan_pick3b.md` is v1 plus 3,370 NUL bytes (stripped, it hashes to eaec6f26). **pick3b's governing plan is v1 eaec6f26.** Before any 3b-R3 value, the dated amendment that v1 §5 requires must be written.
- **No pick3b statistic was computed.**

## 10. What we learned (synthesis)

### 10.1 Verdicts (pre-registered rules only)
| Item | Verdict | Source |
|---|---|---|
| SKR2C training | 10 / 10 rc 0, no guard trigger; **not opened, no verdict** | team-lead retrospective; `e1_openings.md` #7 |
| Thermal G0 v1 (dark IR, A1 + A2) | A2 between; A1 null; pooled between; **not go, not kill**; cannot be killed by A3 | `G0.md`; check §22, §24 |
| Thermal G0 v2 (post hoc instrument fix) | same as v1 | `G0v2.md`; check §36 |
| T15 (A1 dark I-V label) | PASS, narrow | `PICK3_A1_REPORT.md`; check §20 |
| T37 v1 / v2 (A1 registration) | PASS at the line / FAIL | same; check §28 |
| T02, T12, R34; pick 1 R1, R2, R3b, R4; pick3b R1-R3 | not run; 3b-R4 not run by rule | logs; team-lead end state |

### 10.2 Readings (S unless tagged; each owner's)
1. **Thermal's role is set by physics, not by the data volume:** it is an electrical-consequence signal (inactive / disconnected area, hot spots, shunts, Rs), not a crack-line or scuff signal (R, several sources). So it cannot fix the E1 scuff + half-cut crack gap directly, and any route to test or E1 must go through an EL-only model trained with paired data.
2. **Dark forward-bias IR on public pairs is a row / module-level signal, not a cell-level inactive flag** (a post hoc reading of G0 v1 and v2, both recomputed: the row / column-centred AUROC is ~0.5 on A2 (v1 0.49-0.52, v2 0.525) and on A1 v1 (0.52-0.57); on A1 v2 it is 0.343, i.e. EL-dark cells slightly warmer). This matches Colvin 2023's module-level R² 0.429 (R) and the JRC calibration that dark IR gives little local information (R). The sunlit (A3) arm is the fairer test for inactive-like defects and has not been read.
3. **A1 is a series-resistance set more than an inactive set** (R: Colvin 2023; E: T15's diffuse ~1.18× dimming; post hoc centred G0 sign), so A1-based inactive labels are weak; its bright-pixel cell voltage may even invert the "degraded" direction (R + S).
4. **Instrument lessons:** a passing residual can hide a drifted grid; an author-made crop is not necessarily the module; tone-mapped NEF previews limit dark fractions; post hoc QA changes must be written down and co-signed before outcomes. The process mostly held: every verdict rule was frozen before its numbers; T15 and G0 v1 / v2 were recomputed independently from raw files; T37 was checked from the registration outputs (reg.json), not re-registered, and its v2 rule (N7) was post hoc.
5. **Deployment value (S, synth):** drone IR is a triage and pairing tool. The highest-value near-term output is a measured screening-recall table by defect mode on A3 (pick 1 R1 / R2), for the deployment chapter, plus WattCycle drone work that pre-registers the first WattCycle EL as a prospective unseen-module test.

## 11. Process incidents and disclosures (all; with sources)

### 11.1 SKR2C (3 Nov)
- S1. **Pre-launch defects found and fixed:** judge's v0.9 review (5 must-fixes) and stage-1 code review (7 must-fixes + 1 should-fix, §2.3); the s2q subshell-PID defect (no stop was ever needed on s2q). No run started on defective code.
- S2. **rootcheck run 1 rc 1** compared wall `sec`; judge ruled the exclusion a comparator fix, not a relaxation (log 02:34).
- S3. **The first guard dry run used rejected code** (99291944 / 5179dac4); it did not clear G1-G8 (judge 02:45).
- S4. **The v3 passes ran on guard d8a8eb75;** the final 334742d6 adds one display token (`TRIG=""` on a failed read); the whole suite was re-run on the exact final md5s (03:04). Test-harness md5s changed across re-runs (f0782bbe → 8ee6beaa; 40dc50fa → 5c12b297, TAG-suffixed dirs only); not deployed.
- S5. **judge unreachable from ~02:59** (coach's message undeliverable 02:59; runner's send refused 03:05): the final-code re-run was checked by coach only, against judge's written acceptance; team-lead confirmed. Residual 1 (unprotected run if its cmdline is not recorded within 20 s) accepted by team-lead (02:59).
- S6. **The completion facts rest on team-lead's 4 Nov read-only check, logged only on 12 Nov;** no 4 Nov log line was written; no fresh server check was possible on 12 Nov (no ssh; keys may be gone after the reinstall). team-lead's line was stamped "2026-11-12 14:45" by hand but was on disk by 14:41:07; team-lead logged a correction at 14:46 (both logs).
- S7. **Stale state in committed docs:** 3604dc7's record, doc 15 §1j and doc 21 §10 say SKR2C was not launched (true at ~02:45). Updated additively in this refresh.

### 11.2 Thermal (4 Nov), from the log and check/factcheck.md
- T1. **The session ended abruptly ~13:51, cause unknown, before the OS reinstall (E: file mtimes and bytes):** `pick3/plan_pick3b.md` = frozen v1 + 3,370 NUL bytes (13:51:49; with the NULs stripped it hashes to eaec6f26, so it is v1 plus crash padding); `pick3/plan_pick3b_v1.1_FROZEN_c8f57302.md` is 0 bytes (13:51:49): a v1.1 freeze was attempted, no log line records it, and its content is lost and unknown; `pick1/out/discovery/A3_layout.tsv` is 0 bytes (13:51:39); `log.md` line 149 begins with 965 NUL bytes (use `grep -a`). The last surviving 4 Nov log lines are stamped 13:50; lines written after that may be lost (S). pick3b's governing plan is v1 eaec6f26 (intact read-only copy). No readout file and no frozen copy is affected (the empty `A3_layout.tsv` is a discovery output that Amendment 6 does not cite). Nothing was restored or edited. Logged first by verifier (12 Nov 14:45) and by team-lead (14:46); scribe's scan agrees.
- T2. **Hand-typed times ahead of the clock:** pick 1 plan v1's header "~13:00 IST", written by 12:56 (check §17 AU-5); ideas' plan header "12:45-13:05" (real 12:44-12:53) and version string "12:58" (written ~12:50), fixed by re-freezing (edb8ae37 removed → 5c272fe9); datascout's message "A3 ~40% at 13:20" sent at 13:11 (corrected 13:11; log stamps always from `date`); ideas' report "~13:4x" typed at 13:36 (corrected 13:39). check confirmed all log stamps monotonic (§24).
- T3. **Self-test criteria set post hoc:** cellreg's self-test failed pick 3's stated criteria (corners within 1 px; IR residual < 1%); ideas' 12:50 "PASS" used looser in-script thresholds; criteria then set from synthetic results (EL corner < 5%, IR < 10% of a cell); the script's EL bar later moved 3% → 5% (13:27). Disclosed in plan §6A / §7 and the report.
- T4. **pick 3 v1.1 froze ~1 min after datascout's 12:55 dark I-V numbers were in the log;** ideas had not read them (notes N1; check §17); no threshold changed.
- T5. **Priors seen before freezes (disclosed):** datascout saw the header and 3 values of one A1 dark I-V file (download plan); the DTU slide ΔTmax and per-class power losses were known before pick 1 and pick3b froze.
- T6. **G0 script fixes after a first run whose output was seen** (NaN parsing; NaN cells in the permutation null, which had printed −1); point estimates unaffected (check §22 G0-5).
- T7. **`G0_results.json` overwritten at 13:16:54** with post hoc fields; the frozen v1 output was rebuilt byte-exact (1da5ae53) from a reconstructed frozen script (27f7bff1) at 13:20; rule since: post hoc outputs go to new files.
- T8. **Interim G0 computed with QA not co-signed** (13:17); labelled "INTERIM, QA NOT CO-SIGNED", not counted.
- T9. **cellreg v0.4 95e0ca3e ran on real A1 data (13:27:10-13:27:20) before check's review** (registration only; ideas viewed 2 EL and all 10 IR overlays); ideas' first v0.4 real run was stopped by TaskStop with no output read. cellreg changed after review (04fac77a → 95e0ca3e) without a version bump (check CR-1); v0.5 91c3c81e was frozen, announced and withdrawn (never reviewed or run on real data; archived as `pick3/out/archive/cellreg_v0.5_91c3c81e_UNREVIEWED_not_for_use.py`). The release v0.4.1 7d9a9fe0 = reviewed 95e0ca3e + the version string (1-line diff, check §30). notes N8.3 still cite the withdrawn 91c3c81e (moot under decision A).
- T10. **Visual QA miss:** datascout's v0.2 visual QA missed A1 6320427793's IR misregistration (top line ~0.6 cell inside); caught by check (§26).
- T11. **Log-line slips:** ideas' T37 v2 line says "3 modules > 5%" but lists four (check §29); ideas' pick3b discovery said "5 s exposure" (real 2-6 s; corrected 13:49); check's pass-2 counts line (corrected 12:45); check's "doc 14 l.322" miscount (corrected); check's "listed twice" note retracted (13:31).
- T12. **False premise N5** (the authors' A1 crop is the module): the likely cause (S) of T37 v2's IR residual rise (§9.3).
- T13. **cellreg UVF bugs:** portrait UVF merged with a transposed index (27 extra UVF-only rows on 6330431031; EL / IR unaffected); UVF grids transposed on 6 of 10 under v0.4 (check CR-6). UVF fails in every version.
- T14. **Tool side effect:** a WebFetch of a repository link auto-saved the Mantel et al. SPIE 2019 PDF under the session tool-results folder; datascout did not read or move it (notes §3). No dataset file was downloaded during the desk study (one 1 KB DTU README was read).
- T15. **Disk pressure:** free space reached 4.6 GB at 13:39 (other sessions' scratch); pruned by explicit path (ideas 542 MB, check 171 MB). Floor held (4.42 GB after A3 extraction).
- T16. **Unfinished paperwork at the end:** the ADDENDUM (878e6bec) is still marked DRAFT (ideas confirmed §3; datascout's §1-2 confirmation never arrived), and it says A3 R1 and R3b are "running, results to follow" (§2) and pick3b results "to follow" (§3): none ran, so that wording must change before it goes to Om; check §37 "Still to come" and §9 "pending" are stale; synth's top3 / ranked headers still say "waiting for check's re-check" although check closed them (12:59); **the report to the user and Om was never sent.**
- T17. **Stale section number:** check §31 corrected Colvin 2023's methods section to §II.A, but `datasets/dataset_table.md` (A1 row) and datascout's log line 13:40 still cite "§II.B" for the camera facts (left as written; owner's file).
- T18. **Brief wording:** the thermal README calls E-PF the "Best model" with "crack IoU ~0.49". The handbook's standing wording is "recommended deployable candidate; the user's adoption is still open" (doc 15 §3d row 19), and E-PF's test crack IoU at argmax is 0.4815 (SKR2E table); 0.492 is FINAL (cv02, not comparable). No agent output depends on it.
- T19. **Decision (A) time:** team-lead's retrospective gives 13:28 (from its message timestamps); the report says "~13:3x". The messages themselves are not in the folder.
- T20. **WattCycle identity question:** capture's web search (log 12:07) found an IIT Mandi PV-recycling startup, which conflicted with the local docs calling WattCycle "a solar asset-management company" (doc 01); flagged for Om. check C-5 resolved it toward a match (the Atlas manual: "a comprehensive solar asset management platform"; menu "Asset Management") with the caveat that the Atlas app runs on demo seed data, so real drone IR archives are not shown. Om confirmed the company on 4 Nov.
- T21. **Scope slip caught before any download (check RN-1, log 12:52):** ideas' G0 step 1 used all 157 A1 IR modules, but Om approved only the 10-module A1 subset; ideas rescoped to the approved set at 12:52 and sent the 157-module step to synth as a proposal for Om. Nothing extra was downloaded (check §23).

### 11.3 12 Nov
- D1. The laptop OS was reinstalled; no agent survived; `orch-mtp` no longer exists; the data, the venv and the repo survived (E, §7).
- D2. team-lead's retrospective lines in both logs were stamped 14:45 by hand and written ~14:41 (corrected by team-lead 14:46).

## 12. Open items, decisions for the user and Om, and how to resume

### 12.1 For the user
1. **SKR2C opening (E1 opening #7): your explicit OK is needed.** Before it: stage 2 (runner builds, coach reviews, frozen md5s before any S2C number), which needs working gaint access (ssh keys may need re-setup after the reinstall; no agent should ssh before that). It is a third look at the same test and E1 cells. Stated chances: R PASS ~35-65%, seed-aware replication ~25-45% (§2.1).
2. **Carried from 3 Nov** (handbook doc 15 §3e): rows 24 (next step: write-up / SKR2C / B2), 25 (B2 marking), 26 (Blender renders vs gaint lanes), 27 (D2 width flag), 28 (HC route); §3d row 19 (adopting E-PF, still open).
3. **Thermal:** whether to resume picks 1 and 3 (§12.3) and send Om the report (the SUMMARY is final; the ADDENDUM needs its datascout confirmation, which a new agent can do against the files).

### 12.2 For Om (via the user)
1. E-PF inference location (gaint CPU vs a local copy of the 5 checkpoints): held since 4 Nov, so T26 / T27 / T39 run only on EL proxies.
2. Licences / release: mixing CC BY 4.0 sets with BenchmarkEL (no licence file, E); releasing a registered A1 cell set as a CC BY derivative (T37); terms for WattCycle images.
3. Capture funding for pick 2 (Pi HQ kit ~₹25k + lens and filter; UV torch ₹1.8k-4.5k; optional ₹62k camera, NISE fees, phone IR).
4. The A1 extension (0.55 GB; or ideas' steps: all 157 A1 IR 0.26 GB, then ~2 GB EL) and other optional downloads.
5. Whether to send the WattCycle question list Q1-Q20 (and U1-U3 to dataset authors). Pick 2's week plan (W2 = 11-17 Nov) has slipped because nothing was sent.

### 12.3 How to resume the thermal work (S, in the order the plans set)
1. Read `team_2026-11-04_thermal/README.md`, `log.md` (note the NUL bytes at line 149), `synth/SUMMARY.md`, `synth/ADDENDUM_2026-11-04.md`, this record §7-9.
2. Data check: `md5sum -c` of each `~/mtp/datasets/thermal_public/*/MANIFEST.md5` (0 failures on 12 Nov). Disk is no longer tight (52 GB free); the 4.0 GB floor was a 4 Nov rule.
3. Tools (frozen; use only these md5s): `scripts/frozen/cellreg_7d9a9fe0.py`, `scripts/frozen/g0_stats_0190cba5.py`; `scripts/a3_frames.py` d94b7a89; `scripts/pick3b_r12.py` dac5842b (smoke-tested only); venv `~/mtp/research/.venv/bin/python -I`.
4. pick 1: R1 and R2 under Amendment 6 (fb46b6dc) → `pick1/out/A3_module_table.tsv` and `R1_R2.md`; then R3b registration, the v2 visual QA, a co-sign by a second agent before any R3b number.
5. pick3b (governing plan v1 eaec6f26): first write the dated amendment v1 §5 requires (the IR rule after Amendment 6; whether 3b-R3 reuses pick 1's `--quad-ir full` cells; the attempted v1.1 is empty, content unknown), frozen before any 3b-R3 value; then 3b-R1 / R2 on FF loss (3b-R4 stays not run).
6. Then finalise the ADDENDUM with A3 results, and send the report (SUMMARY + ADDENDUM) to the user and Om.

## 13. File index (md5, first 8 hex; E at 12 Nov unless noted)
**This session, SKR2C (`team_2026-10-31_next/`)**
- `protocol_SKR2C.md` 663de96d (v1 locked 91b76abd + §9 launch record; lock copy `judge/out/protocol_SKR2C_v1_lock_91b76abd.md` 91b76abd); `build_s2c.md` c6424c0f; `e1_openings.md` 365d62f3; `log.md` 7482b29e (12 Nov, after team-lead's lines); `README.md` d1942ba9.
- judge: `review_SKR2C_v09.md` cc2a21be; `review_s2c_stage1_code.md` ddf09a9f; `out/skr2c_power_out.txt` 2e15d408.
- Scripts (`scripts/s2c/`, deployed md5s): `s2c_lib.sh` 4edcae9e, `s2c_guard.sh` 334742d6, `s2c_queue.sh` de31c533, `s2c_gpumem.sh` 06791cdd, `s2c_make_jobs.sh` e7d20e79; root / check scripts and diffs beside them.
- Dry-run logs: `results/s2c_dry/` (md5 list `results/s2c_dry_md5.txt` 1f251254), `results/s2c_dry/v2/` (`s2c_dry_v2_md5.txt` de5dbd1b), `results/s2c_dry/final/` (`s2c_dry_final_md5.txt` 345c825e).
- On gaint (not pulled): `/home/noob/work/s2c/` (launch.log, autostop.log, pids/), `s2c_root/`, run dirs `el_thin/experiments/s2c_SKR01_100pct_s1{0..4}`, `el_f3/experiments/s2c_SUPPF_100pct_s1{0..4}`.

**Thermal (`team_2026-11-04_thermal/`)**
- Brief and log: `README.md` 45ca3b69; `om_2026-11-04_thermal.md` 6677bc9f; `om_2026-11-04_decisions.md` b5f143bb; `log.md` (append-only; contains 965 NUL bytes at line 149).
- datasets: `dataset_table.md` 7a48fc3b; `notes.md` 66a25beb; `download_plan.md` 409481f7; `download_selection_A1.tsv` da419f33; `download_verified.md` 645d7cfc.
- ideas: `ideas_long.md` ba9c0038; `drone_only.md` 50a13aeb. capture: `capture_plan.md` 66d2270b; `replan_pick2.md` 9d6a4885.
- synth: `ranked_ideas.md` d36d70f7; `top3.md` fa6da29f; `SUMMARY.md` 00f17af7; `ADDENDUM_2026-11-04.md` 878e6bec (DRAFT).
- check: `factcheck.md` 879f35fa; `cellreg_95e0ca3e.py` 95e0ca3e (reference copy); self-test JSONs.
- pick 1: `plan_pick1.md` fb46b6dc; `out/G0.md` 8aa10e14; `out/G0_v1_frozen.json` 1da5ae53; `out/G0v2.md` 06d1970b; `out/G0v2_primary.json` f1e904e7; `out/G0v2_sensB.json` efe6f4ee; `out/qa_v04/visual_qa_v04_criteria.md` fae36d53, `visual_qa_v04.tsv` 8557c658, `visual_qa_v04_cosigned.tsv` a9a3f454, `keep_v2_primary.tsv` 484fa349, `keep_v2_sensB.tsv` db548f73; `out/discovery/A3_border_vs_outline.tsv` a8be5b7e; `out/discovery/A3_layout.tsv` (0 bytes). Per-module tables / logs in `out/G0_A*`, `out/G0v2_A*`; overlays (png) local only.
- pick 3: `plan_pick3.md` 2893a817 (= `plan_pick3_v1.2_FROZEN_2893a817.md`); `plan_pick3_v1_FROZEN_5c272fe9.md`, `plan_pick3_v1.1_FROZEN_6e9d9af2.md`; `plan_pick3_notes.md` 3679075c; `plan_pick3b_v1_FROZEN_eaec6f26.md` eaec6f26; `plan_pick3b.md` (v1 + 3,370 NULs); `plan_pick3b_v1.1_FROZEN_c8f57302.md` (0 bytes); `out/PICK3_A1_REPORT.md` 55fcf923; `out/t15_summary.json` 320ad9e9; `out/t15_cells.tsv` c365ce09; `out/t15_descriptive.json` 00919df8; `out/t37_v03_summary.json` fbd466d2; `out/t37_v04_summary.json` 0d60bd16.
- scripts: `frozen/cellreg_7d9a9fe0.py` 7d9a9fe0 (= `cellreg.py`); `frozen/g0_stats_27f7bff1.py` 27f7bff1 (v1); `frozen/g0_stats_0190cba5.py` 0190cba5 (v2; = `g0_stats.py`); `pick3b_r12.py` dac5842b; `a3_frames.py` d94b7a89; `select_a1.py` d40cf6d1; listings in `scripts/listings/`.
- Data (local only, not in git): `~/mtp/datasets/thermal_public/A1_osf_csr6t/` (MANIFEST 5a272616), `A2_osf_ar76v/` (8a5c7520), `A3_dtu/` (23a3c83a).

**Handbook (this refresh):** new doc 22 (`handbook/22_thermal_desk_study.md`); additive updates to 00, 03, 11, 12, 13, 14, 15, 16, 21; sources synced.
