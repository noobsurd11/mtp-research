# 15. Status and remaining work

**What this covers.** The state of every experiment on 12 Oct 2026, about 05:30 IST (all P-series experiments finished), and the server state when the work session closed (13 Oct, about 01:30 IST). What ran overnight, what is left for part 1 of the thesis, which decisions are waiting on the user, and the housekeeping debts. Updated 13 Oct ~08:15 IST for P17 and P13 Amendment 2 (§1, §1c). This doc goes stale fastest: check `results/` and the git log of `~/mtp/research` for anything newer.

**Update 30 Oct 2026, ~12:00 IST (additive).** New §1 rows (Track D, Track M + FINAL, the two analysis teams, MIM5, AM, DDeP5, CP5, protocol_100), §1f (state on 30 Oct), §3b (decisions waiting on the user), §4b (ranked next items from `team_2026-10-29_features/coach_strategy.md`) and §7 rows. Sources: `SESSION_RECORD_2026-10-21_to_27.md`, `SESSION_RECORD_2026-10-28_to_30.md` (status as of 30 Oct 11:54 IST), the team folders, docs 18 and 19. **protocol_100 launched at 12:05 IST, just before this was finished: no result exists, and none is predicted here.**

**Update 31 Oct 2026, ~07:30 IST (additive).** New §1g (state on 31 Oct), §3c (decisions waiting on the user), §4c (ranked next items); dated notes on the protocol_100 row and §4b row A. Source: `SESSION_RECORD_2026-10-30_to_31.md`.

**Update 31 Oct 2026, afternoon (additive).** Om's answers of 31 Oct (`team_2026-10-31_next/om_2026-10-31.md` A and B; doc 12 D60, D61): dated "[Answered 31 Oct: ...]" notes on §3b rows 8 and 9 and §3c rows 12 to 16; new §1h (state when PF2 started). Nothing here predicts a PF2 result.

**Update 1 Nov 2026, ~21:00 IST (additive).** New §1i (state at ~20:30 IST 1 Nov), §3d (decisions waiting on the user), §4d (ranked next items with ETAs); dated "[1 Nov: ...]" notes on §3c row 16 and §4c rows 1 to 5; a §7 row. Sources: `SESSION_RECORD_2026-10-31_to_11-01.md`, `team_2026-10-31_next/`, doc 20. THIN-B3 had no verified result at writing; [added ~21:40: its verified result in §1i, §3d row 23 and §4d].

**Update 3 Nov 2026, ~02:40 IST (additive).** New §1j (state at ~02:40 IST 3 Nov), §3e (decisions waiting on the user), §4e (ranked next items); dated "[3 Nov: ...]" notes on §3d rows 19, 20, 22, 23 and §4d rows 2 to 5. Sources: `SESSION_RECORD_2026-11-01_to_11-03.md`, `team_2026-10-31_next/`, doc 21.

**Update 12 Nov 2026 (additive).** New §1k (state on 12 Nov: SKR2C trained, not opened; the thermal team's end state; the laptop after its OS reinstall), §3f (decisions waiting on the user and on Om), §4f (ranked next items); dated "[12 Nov: ...]" notes on §1j and §4e. Sources: `SESSION_RECORD_2026-11-03_to_11-04.md`, `team_2026-10-31_next/log.md`, `team_2026-11-04_thermal/`; docs 21, 22.

**Sources**
- Server check at session close, 13 Oct 01:21 IST (read-only: `tmux ls`, `nvidia-smi`, `ps`, `du`), for §1b.
- Launch logs on the servers, read at about 22:15 IST:
  - gaint `/home/noob/work/el_p14/reports/p15/launch_gaint.log`;
  - cv02 `/tmp/noob_el/el_p16/reports/p16b/launch.log` (UTC) and `el_p16/reports/p16b_auto.log` (Part B has no `queue.log`); Part A: `el_p13/reports/p16/launch.log`.
- `to_human/results_2026-10-12.md`.
- `to_human/proposal_reframe_2026-10-11.md` §5 and §7.
- `to_human/directions_2026-10-10.md`.
- `~/mtp/MTP_session_handoff_2026-10-07.md` §12 and §13.
- Protocols P15 and P16.
- `scripts/post_p15.sh`, `scripts/post_p16.sh`.

---

## 1. Experiment status

| Exp | Status | Where results are |
|---|---|---|
| P1 to P12 | Done | `results/p1` … `results/p12` (P3 to P5 under `p3_label_versions`, `p4_feature_probe`, `p5_region_pl`) |
| P13 audit | Done | `results/p13_audit/` |
| P13 | Done, 21:04 IST 11 Oct. The primary claim passes. | `results/p13/README.md` |
| P14 | Done, 19:34 IST 11 Oct | `results/p14/README.md` |
| E1 (task metrics, 106-cell extension) | Done for P6 to P17 | `results/e1/` |
| **P15** (gaint, UCF-EL encoder transfer) | **Done**, 6 runs rc = 0 (17:01 to 22:26 IST); analysed about 22:40 IST. **Fails:** 5% n.d. on all three; 10% worse on all three, robust over cells. | `results/p15/README.md`, `results/e1/e1_p15.md` |
| **P17** (cv02, SKCDF-style decoupled decoder on BsM5) + **P13 Amendment 2** (BsM5 s3–4) | **Done**, 7 runs (13 Oct 01:55 to 04:08 IST), all rc = 0; [Note 21 Oct: the launcher logged rc after a `$(date)` substitution, so this rc was always 0 (doc 14 §3.1). Completion is confirmed instead by other evidence: every run's log reaches step 20000/20000 and prints "TEST (final weights, step 20000)", `latest.pth` and `metrics.json` test_final are at step 20,000 (gaint copies and cv02 originals), and every re-score JSON has step 20,000; `results/rc_check/p13_p17_p18_completion.txt`.] analysed about 08:00 IST.<br>• **P17 rule 1 n.d.:** BsD5 − BsM5 −0.006 / +0.011 / −0.008 (thresholds about 40% of BsM5's gain). BsD5 − A5c passes on all three.<br>• **BsM5 on 5 seeds:** − A5c +0.029 / +0.107 / +0.045, passes; CsM5 − BsM5 now n.d.<br>• Post hoc (21 Oct, `team_2026-10-21/data/decision.md` D6), without the 7 twin test cells: BsD5 − BsM5 still n.d.; BsM5 − A5c +0.019 / +0.093 / +0.039 still passes (crack only just); CsM5 − A5c inactive only. | `results/p17/README.md`, `results/p13/README.md`, `results/e1/e1_p17.md` |
| **P19** (cv02, reproduction of Hanifi 2025, IEA/AIE) | **Done**, 8 runs (14 Oct 08:58 to 09:31 IST), all rc = 0. Their code, release split, no augmentation. VGG16-UNet features 0.678 vs 0.663, crack 0.352 vs 0.335; defects 0.246 vs 0.326 (our test lacks dead cell, belt mark) | `results/p19/README.md` |
| **P18** (cv02, EXPLORATORY: BsM recipe at 10% and 20%) | **Done**, 8 runs (13 Oct 17:31 to 19:40 IST), all rc = 0; [Note 21 Oct: the launcher logged rc after a `$(date)` substitution, so this rc was always 0 (doc 14 §3.1). Completion is confirmed instead by other evidence: every run's log reaches step 20000/20000 and prints "TEST (final weights, step 20000)", `latest.pth` and `metrics.json` test_final are at step 20,000 (gaint copies and cv02 originals), and every re-score JSON has step 20,000; `results/rc_check/p13_p17_p18_completion.txt`.] analysed about 19:50 IST.<br>• Arithmetic: BsM10 − A10 and BsM20 − A20 pass on inactive only (+0.132, +0.060); crack n.d.<br>• Without the noisy cell: BsM10 passes on all three; BsM20 inactive only (crack +0.013, thr 0.014).<br>• BsM20 s4 fails on the noisy cell (34k FP px).<br>• Post hoc (21 Oct, D6), without the 7 twin test cells: inactive still passes at both fractions (+0.146, +0.076); without twins and the noisy cell, both pass on all three. | `results/p18/README.md`, `results/e1/e1_p18.md` |
| **SK1 + S-a** (cv02, agent team 21–22 Oct; post hoc addition) | **Done; SKCDF track closed 22 Oct.** 20 runs (D7 twin-free pool), all at step 20,000, re-score rc logged correctly.<br>• SK1 primary BsDB5 − BsD5 n.d.; AB5 − A5c n.d.; band WORSE on crack.<br>• S-a (inference only): at 5% the SSL crack-IoU gains are n.d. against supervised + τ=1 logit bias; inactive gains survive.<br>• Next (not approved yet): labelling plan and the user's 1-h audit of 40 always-missed crack components (`team_2026-10-21/skcdf/labelling_plan.md`). | `team_2026-10-21/skcdf/results.md`, `null_diagnosis.md`, `results/sk1/la_sa.md` |
| **AL1 v2** (cv02, agent team 21–23 Oct; post hoc addition; D7 pool) | **Done; ALHVR track answered: no.** 35 runs (7 arms × 5 seeds), all at step 20,000, rc 0; critic recompute exact.<br>• Primary AL5 − A5 **WORSE** on all three primaries in all four cell sets.<br>• Routing (S1) and CG-CPCL (S2) n.d.; DTCT-only WORSE on inactive; CPS5 level with supervised; BsM5 re-run still beats supervised (descriptive).<br>• Pre-registered H-cm predictions held. The inactive damage (post hoc) was not predicted.<br>• Not scored: network B and ensemble. No follow-up proposed. | `team_2026-10-21/alhvr/results.md`, `verify_a2.md`, `results/al1/` |
| **Why-SOTA team** (24 Oct, no GPU; added 30 Oct) | **Done.** Diagnosis of why 2025 SOTA SSL fails on EL crack; 8 ranked directions. The user: "take the critics decisions, and go". | `team_2026-10-24_why/SYNTHESIS.md`; doc 18 §W |
| **Track D** (cv02, 24 Oct; added 30 Oct) | **Done, critic CONFIRMED.**<br>• Frozen probe: ImageNet ResNet-50 passes the BMRK crack-AP bar (test and pool), ConvNeXt-T on test only; MIM gated out.<br>• Inactive-edge re-score: +0.018 to +0.027 crack IoU at 5 to 10%, +0.007 at 100%; no SSL gap flips sign.<br>• Labelled set (27 runs): Tc − R BETTER (relF1@2 +0.030); Ts − Tc n.d.; Ts 0.352 vs BsM5 0.331 (oracle-selected). SSL on the Ts set not run (gate not met). | `team_2026-10-24_go/trackD/verify_*.md`; `results/trackD_*`; doc 18 §D1 to §D3 |
| **Track M** (cv02, 24 to 25 Oct; added 30 Oct) | **Done, MC VERIFIED.** R1 ensemble PASS; R2 WORSE; R2c, R4, R5 n.d.; R3 (ResNet-50) WORSE on inactive; all rungs val EXCLUDE. **FINAL** = SUP100 5-seed ensemble, crack bias +0.75: clean crack IoU 0.492 (single 0.474), PASS on crack IoU and relF1@2; bias 0 robust (0.488). [Qualified 30 Oct: R3's null holds under the house optimizer only (doc 19 §4).] | `team_2026-10-24_go/trackM/results_final.md`, `verify_final.md`; doc 18 §M0 to §M7 |
| **Unlabelled-data team** (27 Oct, no GPU; added 30 Oct) | **Done.** Pseudo-label SSL is a tight null at 20 to 100%; feature learning untested at the time; E1 crack gap = half-cut + scuff context; keep the 50 test cells, add the clean set; ranked plan (pool mining for labels first). | `team_2026-10-27_unlabelled/SYNTHESIS.md`; doc 18 §U |
| **MIM5 + AM** (gaint, 29 to 30 Oct; added 30 Oct) | **Done, coach VERIFIED.** MIM5 − A5c-f1 n.d. on all three, every estimate negative (crack −0.0116, thr 0.0186). AM (val only) KILL. [Qualified 30 Oct: the house fine-tune erased the layers MIM changed; 5% was the wrong fraction for the user's question.] | `team_2026-10-29_features/verify_mim5.md`; doc 19 §2, §3.1 |
| **DDeP5** (pretraining cv02, fine-tunes gaint, 29 to 30 Oct; added 30 Oct) | **Done, coach VERIFIED.** n.d. on all three, small positive (crack +0.0070, thr 0.0100), mostly a threshold shift; below the free bias. Closed; DDeP at 100% dropped. | `verify_ddep5.md`; doc 19 §3.2 |
| **CP5** (gaint, 30 Oct; added 30 Oct) | **Stopped 10:50 IST 30 Oct, not scored, no test opened.** Decoy gate PASS at 2k. s1, s3 finished; s0, s4 stopped mid-run; s2 cancelled. | `protocol_cp5.md`; doc 19 §3.3 |
| **protocol_100** (gaint, from 30 Oct; added 30 Oct) | **Launched 12:05:34 IST 30 Oct on v1.1 (md5 8dcb231b). No results yet.** 4 arms × 5 seeds at 100% labels: SUP100-g, SUP100-PF, MIM100-PF, CP100.<br>• Gates: identity IDENTICAL; G5 PASS (layer3/4 0.975 to 0.990 at 4k); no 4th lane; gate 6 (CP decoy) FLAG, so CP100 waits for gate 6b (CP_GO / CP_STOP), pending at 12:22 IST.<br>• Opening 1 (15 fine-tunes) about 00:00 to 01:00 IST 31 Oct; opening 2 (CP100, if GO) about 07:00 IST 31 Oct. | `team_2026-10-29_features/protocol_100.md` v1.1, `review_100_v1.md`; doc 19 §7 [Qualified 31 Oct: done. 20 runs rc 0; both openings scored and verified; every contrast n.d. (doc 19 §10)] |
| **B1 label audit** (gaint CPU, 30 Oct; added 30 Oct) | **Done.** Crack flags in 24 of 239 audited train cells (10.0 per 100), inactive 9 (3.8 per 100); three panel sheets sent to the user 11:37 IST, awaiting marks. | `team_2026-10-29_features/b1_audit/`; doc 19 §8.1 |
| **P16** (cv02, SSL vs supervised at 20/50/100%) | **Done.** Part A 9 runs (17:28 to 22:06 IST, 11 Oct); Part B 15 runs (21:04 IST to 04:24 IST, 12 Oct); all rc = 0; analysed about 05:00 IST.<br>• **Fails at all three fractions:** S20, S50, Sx100 − supervised n.d. on all three primaries (5 vs 5 seeds). CutMix off by the locked val pick.<br>• One noisy test cell (`CSIR_00070_r8_c4`) wrecked crack in 4 of 24 runs; without it every crack Δ is within ±0.003 (post hoc), so the verdict is unchanged. | `results/p16/README.md`, `results/e1/e1_p16.md` |

## 1b. Server state at session close (13 Oct, 01:21 IST)
- **Nothing of ours is running** on either server. No queue, watcher or training process.
- **cv02 GPUs** are taken by another user (`cv07`, one Jupyter kernel): 15.5 GB on GPU 0 and 2.4 GB each on GPUs 1 to 6, 0% use. The standing rule (never start on a GPU where another user holds > 4 GB) rules out GPU 0 while that kernel lives.
- **gaint GPU 0:** 6.5 GB held by a root process (`finllm_chat.py`), not ours.
- **Idle tmux sessions of ours, left open** (killing them needs the user's say-so):
  - cv02: `bndiag`, `e1`, `e1b`, `e1p11`, `e1v2`, `p6`, `p6hist`, `p6img`, `p7` to `p14`, `p15pre`, `p16`, `p16auto`, `p16b`;
  - gaint: `p10g`, `p12g`, `p15g`.
  - Not ours or older: cv02 `amlc` (26 Sep), `el` and `main` (4 Oct, phase 1 era); gaint `noob-0`.
- **cv02 `/tmp/noob_el`** holds 100 GB, including the P13 and P16 checkpoints (`el_p13/experiments` 15 GB, `el_p16/experiments` 8.8 GB). cv02 had been up 34 days; a reboot wipes `/tmp`, and checkpoints are not backed up (§7). Everything needed for the write-up (re-score JSONs, E1 per-cell JSONs, logs, the noisy-cell p(crack) maps) is already copied into `~/mtp/research/results/`.
- **gaint worktrees:** `el-fault-detection` (main, `24590fb`), `el_p13` (`bac5264`), `el_p14` (`be67787`), `el_p16` (`d51b60f`).

## 1c. Server state after P17 (13 Oct, ~08:00 IST)
- **Nothing of ours is running.** All 8 cv02 GPUs were free at 07:54 IST (the `cv07` kernel had gone).
- **New idle tmux sessions of ours on cv02:** `p13a2`, `p17run`, `p17smoke` (left open; closing needs the user's say-so).
- **cv02 `/tmp/noob_el` is copied to gaint** `/home/noob/work/cv02_noob_el/` (13 Oct, at the user's request before a cv02 restart):
  - pass 1, 01:37 to 03:49 IST: all `el_p*` dirs, `el-fault-detection`, `diag`, `ext117`, `results_to_sync` (no data, no `.venv`); 373 checkpoints, MD5 identical on both sides;
  - pass 2, 07:57 IST (interrupted by a session drop) and 16:28 to 16:33 IST: `el_p17`, BsM5 s3–4, `el_p13/reports/p13a2`, new E1 JSONs; 616 files including 18 checkpoints, MD5 identical on both sides.
  - Route: relayed through the user's laptop (cv02 is a shared lab login, so no agent forwarding or keys there).
- **gaint worktree added:** `el_p17` (branch `p17`, `f2f20d3`).

## 1d. Server state after P18 (13 Oct, ~20:00 IST)
- **Nothing of ours is running.** P18 ran on cv02 GPUs 0–7 (tmux `p18`, idle, left open).
- **Backup pass 3 (19:44–19:52 IST):** P18 run dirs, `el_p13/reports/p18`, the queue spec, `diag/student`, `diag/e1v2`, `diag/e1p18.log` copied to gaint `cv02_noob_el`; 264 files including 16 checkpoints, MD5 identical on both sides.

## 1e. Server state after P19 (14 Oct, ~09:40 IST)
- **Nothing of ours is running.** P19 lives in cv02 `/tmp/noob_el/hanifi` (venv 5.2 GB, runs 2.1 GB, data copy 122 MB); tmux `p19` idle.
- Backup pass 4 (09:33–09:36 IST): P19 runs, driver, their repo to gaint `cv02_noob_el/hanifi`; 101 files, MD5 identical on both sides.

## 1f. State on 30 Oct 2026, about 11:54 IST (added 30 Oct; from `SESSION_RECORD_2026-10-28_to_30.md` §0, §7 and `team_2026-10-29_features/log.md`, not a fresh server check)
- **gaint:** protocol_100 smokes at `el_f3` e544133 (tmux `f100`) and the G5 extension (PF smokes to 4k) running since 11:04 IST; gate table expected about 12:05 to 12:10, then v1.1, coach's re-check and launch. Root's `finllm_chat.py` (5.9 GB) shares the GPU; ≥ 2 GB must stay free (doc 14 §1.2b).
- **Update 12:22 IST (`team_2026-10-29_features/log.md`, `protocol_100.md` v1.1):** protocol_100 launched 12:05:34 IST (queue tmux `f100`; first run `f3_SUP_100pct_s0` started 12:08:34). Gate 6b (4k decoy for CP100) running beside it, decision pending. B2 pool mining running on gaint CPU since 12:09 (tmux `b2`).
- **cv02:** at 10:51 IST 0 of 8 GPUs qualified (other users' processes of 9 to 42 GB each). A watcher checks every 10 min; team-lead is told before anything moves.
- **Idle tmux shells on cv02:** still open from earlier sessions; closing them is an open housekeeping item for the user (session record 21 to 27 Oct §10).
- **Expected timing (protocol_100 v1.1, S):** fine-tune waves about 11.5 to 12 h, so opening 1 about 00:00 to 01:00 IST 31 Oct; CP100, if GO, about 6.5 h more, so opening 2 about 07:00 IST 31 Oct; then coach's recompute. (The session record's estimates, about 01:00 and 07:30, predate v1.1.) Check `el_f3/reports/f100/launch.log` for the line `f3 opening<N> scoring done`.
- **After launch:** B2 pool mining (candidates only), running since 12:09.

**Held, do not touch:** the gaint `extpool_20261007` night queue (old-era Mean Teacher runs with SemiCE). It was held by hand on 8 Oct, 01:18 IST (19:48 UTC on 7 Oct) while SemiCE was under audit, and P2 later showed SemiCE is invalid. The user's standing instruction is to leave it held and untouched. (Source: the user's command in `sources/chat/user_messages_2026-10-07_to_11.md`, 2026-10-07T19:48Z; session summaries.)

## 1g. State on 31 Oct 2026, about 07:30 IST (added 31 Oct; `SESSION_RECORD_2026-10-30_to_31.md`, `team_2026-10-29_features/log.md`)
- **gaint:** protocol_100 complete: all 20 runs rc 0; both openings scored rc 0 and recomputed by coach. No process of ours is running; root's `finllm_chat.py` (5,876 MiB) is alone on the GPU. tmux `f100r` windows are left with idle shells. The memory logger stopped itself at 07:08:34.
- **cv02:** unused all session (never 3 of 8 GPUs free); a 6 h watcher re-armed at 05:09.
- **Results:** every protocol_100 contrast n.d. (doc 19 §10). coach proposed PF2 at 07:15; not approved.


## 1h. State on 31 Oct 2026, about 14:40 IST (added 31 Oct; `team_2026-10-31_next/log.md`, `protocol_PF2.md`, `build_pf2.md`)
- **Om's answers** (pasted by the user ~13:45 IST): protocol_100 verdicts accepted, BEST = SUP100-PF, PF2 approved, B3 and the two thin-crack arms (Skeleton Recall, clDice) approved on coach's APPROVED; vetter's 11 questions answered (doc 12 D60, D61). The user: no budget limit, two more months, avoid manual labelling unless really needed. A new team (`team_2026-10-31_next/`) validates Om's 11 new ideas.
- **gaint:** PF2 running since 14:29 IST (coach APPROVED 14:28): SUP100-g / SUP100-PF / RN50-PF, seeds 5 to 9, deploy e544133 (no code change for RN50), the 10 ResNet-34 runs in 3-lane waves first, then the 5 ResNet-50 runs one at a time (1 RN50 + 2 R34 would breach the 2 GB finllm floor). Gates: R34 9,000 MiB, RN50 13,234 (smoke peak 11,186 + 2,048), scoring passes 7,900 (RN50 LA val peak 5,824 + 2,048). Smoke 14:03 to 14:27: SUP / SUPPF bit-identical to the protocol_100 s0 runs; RN50-PF layer3 / layer4 cosine to ImageNet 0.975 / 0.983 at 4k. ETA: all trained about 06:30 to 07:00 on 1 Nov, one scoring opening after. No PF2 number exists.
- **Handbook:** the B2 Hanifi panel cells are redacted in `handbook/sources/` until the user marks B2 (commit a076e54; `sync_sources.sh` applies it on every sync).

## 1i. State on 1 Nov 2026, about 20:30 IST (added 1 Nov; `SESSION_RECORD_2026-10-31_to_11-01.md` §11, `team_2026-10-31_next/log.md`)
- **Done since §1h:** PF2 (PASS; RN50-PF FAIL; doc 20 §4); PF2E (PASS on E1 inactive with qualifications, test n.d.; §5); the 11 idea validations (§2); routing pre-check FAIL, T9 FAIL (TTA closed), S10 PASS (method note), P8 probe runs 1 and 2 (§3). Item 13 closed (no pool download).
- **gaint, running:** THIN-B3's opening (E1 opening #2), started 19:40:18 (trigger PID 2926375, GS 9,900); ETA end ~21:45 to 22:00 (runner). All 15 THIN runs trained rc 0 (06:32 to 19:39). [~21:40: opening done 21:13:45, post rc 0; coach VERIFIED 21:21, judge CONFIRMED 21:29: no arm passes (SKR FAIL, CLD FAIL, B3 n.d., scuff not learned); BEST stays SUP100-PF (doc 20 §6.0). The nq queue started A8 s0 21:15 and A8c s0 21:17; HC s5 waits for a lane. builder respawned ~21:25 for B6.]
- **gaint, armed behind it:** nq queue (PID 1843760; jobs A8 s0, A8c s0, HC s5, A8 s1, A8c s1, HC s6 to s9; 3 lanes; gates HC 9,000, A8 11,400), starting on THIN's "thin scoring done: post rc=0"; A8 scoring (PID 1908697, CPU, val + rf only); HC opening trigger (PID 2122911, FROZEN a23994c4; E1 opening #3). Event watcher `rwatch_v2.sh` (PID 1914687).
- **cv02:** nothing of ours; read-only polls every 15 min (5 GPUs qualified at 18:50 and 19:02). B6 waits for builder's fold roots and scorer, runner's jobs and coach's APPROVED.
- **Team:** calib and domain finished (not respawned after 1 Nov's cap); found and builder stopped at 19:15 for laptop memory (builder returns after THIN's window for B6); runner, coach, judge active; scribe writing the record and this refresh.

## 1j. State on 3 Nov 2026, about 02:40 IST (added 3 Nov; `SESSION_RECORD_2026-11-01_to_11-03.md` §12, `team_2026-10-31_next/log.md`)
- **Done since §1i (all verified by coach and confirmed by judge):** A8 screen **KILL** (1 Nov 23:40; idea 8 closed); HC **n.d.** (2 Nov 03:18; E1 #3); B6 **n.d.**, realised power ~6% at +0.017 (22:19); SKR2 **PASS**, narrow, and HC2 **FAIL** by G1 (~21:44; E1 #5); SKR2E **FAIL** by G2a + G2b at the headline pair (23:39; E1 #6); Om's A1-A6 all DROP, A4 PARK (11:43); B2 agent raters calibration **FAIL** (scuff gate; 11:49). Doc 21.
- **Recommended deployable candidate:** E-PF at argmax (PF2E; coach and judge); SKR2E did not displace it; adoption is still the user's call (§3d row 19).
- **gaint:** GPU = finllm only (free 25,804 MiB at 02:22); `rwatch4` alive; idle tmux sessions listed, none killed; disk 476 GB free. SKR2C (SKR2 vs SUPPF, fresh seeds 10-14, 10 runs, training only, MAXC 2, ~12.3 h wall): protocol v1 locked 02:37 (judge signed), data root verified; judge's stage-1 code review (02:38) found the guard / queue NOT READY (7 must-fixes: outside-process HOLD and live startup check missing; exact command-line check, owner re-check before SIGKILL, ≥ 30 s between stops, nvidia-smi timeout, a dry run with real signals); coach holds APPROVED until judge confirms the fixes; runner launches training only after APPROVED. **The SKR2C opening (E1 #7) waits for the user's OK.**
- **cv02:** nothing of ours; B6's deploy removed.
- **Team:** runner, coach, judge active for SKR2C; scribe writing this refresh; builder, arch, marker1, marker2 stopped; all agents to be closed after tonight (the user's line, 3 Nov ~02:20).
- [12 Nov: SKR2C was launched 3 Nov 03:06 after judge accepted the fixed code (02:58) and finished training 11:24:04 (10 rc 0 of 10, no guard trigger); all agents were closed ~03:10. See §1k.]

## 1k. State on 12 Nov 2026 (added 12 Nov; `SESSION_RECORD_2026-11-03_to_11-04.md` §2, §7-12; no server access since 4 Nov)
- **SKR2C (doc 21 §10):** launched 3 Nov 03:06 (judge's stage-1 acceptance ddf09a9f, coach APPROVED, arming conditions met); **ALL TRAINED 3 Nov 11:24:04, 10 rc 0 of 10**; the auto-stop guard never fired; no HOLD (team-lead's 4 Nov read-only check, logged 12 Nov). **Nothing scored; stage 2 (the opening build) not started; E1 opening #7 registered, not opened.**
- **gaint / cv02:** not checked since 4 Nov. As of then: GPU = finllm only after SKR2C; SKR2C run dirs and `/home/noob/work/s2c/` (logs, pids) on gaint; nothing of ours on cv02. ssh keys may need re-setup after the laptop reinstall.
- **Thermal team (`team_2026-11-04_thermal/`, doc 22), end state 4 Nov ~13:50:** desk study done (SUMMARY final for Om); downloads A1 / A2 / A3 verified; pick 1 G0 v1 and v2 done (not a go, not a kill; recomputed by check); pick 3 A1 arm closed at T37 (option A), report checked; pick3b plan frozen and its discovery done. **Not done:** pick 1 A3 R1 / R2 / R3b; pick3b R1 / R2 / R3 (R4 not run by rule); the ADDENDUM is a DRAFT; **the report to the user and Om was not sent.** The session ended abruptly (doc 13 D55).
- **Laptop (doc 14 §1.1b):** OS reinstalled; 52 GB free; data, repo and `.venv` intact (thermal MANIFESTs re-verified, 0 failures); no agent or orchestrator tmux session survived.
- **Team:** none running before this documentation (scribe + verifier, 12 Nov).

## 2. What ran overnight, 11 to 12 Oct (all done)
A watcher (`scratchpad/watch.sh`) polled both servers every 2 minutes and fired on each finished set. It exited after P16 Part B; the script lived in a session scratchpad that no longer exists. What it triggered:
1. **P15 (done 11 Oct ~22:40 IST):** `bash scripts/post_p15.sh <cv02 gpu>`.
   - Locked rules: gU5 − A5 and gU10 − gA10.
   - E1 per-cell scoring on cv02.
   - Write `results/p15/README.md`, then commit.
2. **P16 (done 12 Oct ~05:00 IST):** `bash scripts/post_p16.sh <cv02 gpu>` (ran on GPU 0).
   - Locked rules: S20 − A20, S50 − A50 and Sx100 − A100, 5 vs 5 seeds.
   - Bootstrap, source split, E1, bars, and the label-fraction curve (`scripts/p16_curve.py`).
   - Added after the runs: the noisy-cell diagnostic (`scripts/p16_excell.py`, `scripts/cell_noise_rank.py`).
   - `results/p16/README.md` written and committed.
3. **Morning, 12 Oct:**
   - Done: `to_human/results_2026-10-12.md` finalised; this handbook refreshed (§6); commit `1bbe631`.
   - Done: one summary sent to the user at 04:48 IST (results per experiment against the locked rules, the noisy cell, six open decisions). Verbatim in `sources/chat/claude_session_summaries_2026-10-11_to_12.md`.
   - **Not done, on purpose:** `to_human/proposal_reframe_2026-10-11.md` and `midterm_deck_outline.md` were not touched. Any rewrite needs a framing, and framing is the user's call (§3 decisions 1 and 4). Both still predate the P13 to P16 results.
   - The user has not yet replied to the summary. Claude also offered to turn it into a shareable web page; no answer.

## 3. Decisions waiting on the user

| # | Decision | Why it is open | Source |
|---|---|---|---|
| 1 | Thesis framing (e.g. "SSL works once the pipeline is fixed" vs "a measurement and diagnosis study" vs a mix) | The user's rule: "framing depends on final results, no presumptions, ever". All results are now in (P15 and P16 read); the evidence table is doc 11 §(a). | user, 11 Oct |
| 2 | ~~Whether to run hard pseudo-labels + CutMix (the BsM recipe) at 20% or 50% labels~~ **Run at 10% and 20% as P18 (exploratory, 13 Oct, under the user's "experiment whatever you think useful"); see `results/p18/README.md`. 50% not run.** | P13's best crack arm was BsM5. P16 ran the Cs recipe (CutMix off by the locked val pick) and found nothing at 20 to 100%. A BsM arm at 20/50% would be chosen after seeing test results, so it can only be reported as exploratory. | `results/p13/README.md`, `results/p16/README.md`; chat 11 Oct |
| 2b | Whether to add "without `CSIR_00070_r8_c4`" as a standing robustness check | That test cell, the noisiest of 582, decides crack contrasts in about 1 run in 6 (P16) and caused P6's L0 10% s1 outlier. No locked rule mentions it; adding the check now is a methodology change the user should approve. | `results/p16/README.md` |
| 3 | Larger test set, and whether to use E-SCDD's extra labelled cells | The user said "conside rit" (11 Oct).<br>• Done: a 106-cell extension from BenchmarkEL modules we never trained on (E1).<br>• Done 12 Oct: full E-SCDD and BenchmarkEL `20221008` downloaded and audited (doc 17).<br>• Facts for the decision:<br>&nbsp;&nbsp;– 233 labelled real cells we never trained on, 111 of them in our external pool;<br>&nbsp;&nbsp;– E-SCDD's own test is unusable with our split;<br>&nbsp;&nbsp;– a 172-cell test (ours + E1 + 17 new) has 26 inactive cells with a top-3 share of 53.5%.<br>• Open: use any of it (new base, held-out selection set, larger test) or not. | `results/escdd_audit/README.md` §8; `results/e1/README.md` |
| 3b | Thesis wording for the revised labels | They are BenchmarkEL `20221008` crack/inactive labels obtained via E-SCDD (doc 17 §5.2) | `results/escdd_audit/README.md` §4 |
| 4 | Mid-term deck content | The outline predates P9 to P16, and the proposal reframe (11 Oct) predates P13 to P16. Neither was updated after the results (§2). The user said they would start on the deck after the one day of work (11 Oct). | `to_human/midterm_deck_outline.md`, `to_human/proposal_reframe_2026-10-11.md` |
| 5 | Identity, institute and report template for the MTP report | Inconsistent across sources (phase 1 handoff §1) | phase 1 handoff |

## 3b. Decisions waiting on the user, 30 Oct (added 30 Oct)

| # | Decision | Facts for it | Source |
|---|---|---|---|
| 6 | **B1:** mark each panel of the three sheets: label error / true hard case / unsure | 24 crack panels, 9 inactive, 15 scuff/star cells. Train crack flags (10.0 per 100) are below the val base rate (16.7 per 100 for crack FL), so many flags will be hard real cracks. No mask changes until the marks; fixes go to `masks_escdd_v2` with a change list, never to val or test without a separate decision | `team_2026-10-29_features/b1_audit/`; doc 19 §8.1 |
| 7 | **B2:** after the candidate sheets, whether to pixel-label 20 to 40 pool cells (crack + scuff) | 100 candidates being mined (70 half-cut, all CSIR from 7 modules; 30 full). Expected (S, 27 Oct): E1 crack recall +0.04 to +0.15, BMRK crack +0.02 to +0.05, pooled test ≤ +0.01. Human time: about 6 to 10 h for 20 to 40 pixel masks (27 Oct estimate) | doc 18 §U; doc 19 §8.3 |
| 8 | **Scuff test GT for B3:** (a) keep test GT (236 scuff px as crack) for the verdict, coach's recommendation for comparability; or (b) also report a test version with them ignored, descriptively [Answered 31 Oct: the verdict uses the current test masks; the version with the 236 px ignored is reported as descriptive this round; revisit after B3 (Om B2; doc 12 D61).] | The 236 px are 0.26% of test crack px. Changing test GT mid-series breaks comparability with FINAL and every P-series number | `spec_b3_scuff.md` §4; doc 17 §5.11 |
| 9 | **ELPV download** (~0.1 GB) for BMRK-like cells [Answered 31 Oct: no for now (Om B7).] | Must be deduped first: 10 BMRK test cells are ELPV images | session record 21 to 27 Oct §10 |
| 10 | **The 40-segment crack audit** (about 1 h) and **4 label-convention questions** (cracks on inactive edges, faint-crack width, tiny fragments, 236 restored old-mask px in `ARTS_00051_r3_c2`) | Default for all four: keep as labelled | `team_2026-10-21/skcdf/audit_sheet.csv`, `labelling_plan.md`; session record 21 to 27 Oct §10 |
| 11 | **Close the idle cv02 tmux shells** | Housekeeping; needs the user's say-so | session record 28 to 30 Oct §10 |

Decision 4 of the 21 to 27 Oct record ("the handbook refresh") is this update.

## 3c. Decisions waiting on the user, 31 Oct (added 31 Oct)

| # | Decision | Facts for it | Source |
|---|---|---|---|
| 12 | **PF as the base recipe** for follow-ups [Answered 31 Oct: yes, BEST = SUP100-PF (Om A; doc 12 D60).] | coach: BEST = SUP100-PF (equal on test by the rule; more robust on E1 and on the noisy cell) | `verify_100_o1.md` §5 |
| 13 | **PF E1 replication (PF2)** [Answered 31 Oct: approved as proposed, plus E1 strata reported and the 7,154 MiB gate for scoring beside finllm (Om A; D60). `team_2026-10-31_next/protocol_PF2.md`; launched 14:29 IST, see §1h.] | New seeds 5 to 9; SUP100-g / SUP100-PF / RN50-PF; E1 crack recall and E1 inactive IoU as pre-registered co-primaries for PF; ~15 to 17 h on gaint (coach). Needs row 15's Q1 first | `log.md` 31 Oct 07:15 |
| 14 | **RN50-PF** vs SUP100-PF [Answered 31 Oct: the third arm of PF2; bigger encoders are gated on SUP100-PF, ConvNeXt-T parked (Om B8; D61).] | D: RN50-5 +0.060 E1 target recall at cost 0.047, not ensemble size; R3 RN50 WORSE on test inactive | `verify_d.md` |
| 15 | **vetter §6, questions 1 to 11** [Answered 31 Oct: all 11, doc 12 D61.] | E1 still sealed? scuff test GT; Hanifi cells (validation now, training later); labelling hours; thin-crack metric; powered inactive CV (~40+ h); downloads (DINOv3, ELPV); gate bigger encoders on the recipe; pool download (moot, D58); pool module rule; pool subset | `review_suggestions_2026-10-30.md` §6 |
| 16 | **Marks** on the B1 sheets (3) and the B2 v2 sheets (4 x 25 panels) [Answered 31 Oct: B1 marks (about 1 h) and B2 marks (about 15 min) this week; B2 pixel masks and the Hanifi crack cleanup only if the Hanifi AUROC check and the marks show ranked > random (Om B4). Still waiting on the user's marks.] [1 Nov: optional (team-lead's reading of the user's 31 Oct ~13:45 line '…refrain from manual labelling unless very much needed', which overrides Om B4's 'now'); not done; not re-asked (doc 12 D77).] | B2: scuff / crack / both / neither / unsure; primary hit = scuff, crack or both | `b2_mining/v2/b2v2_report.txt` |
| 17 | **Delete the 293.6 MB HF pixel sample** (`~/mtp/datasets/scdd_unlabeled_sample/`, outside the repo) | No download is planned | `pool_large/pool_large_audit_2026-10-30.md` §5 |
| 18 | **Who rebooted gaint at 16:28 on 30 Oct?** | Orderly shutdown, console login at 16:29; runs need a warning if it may happen again | `protocol_100.md` v1.2 |

Still open from §3b: rows 10 (40-segment audit, 4 label questions) and 11 (idle cv02 shells). Row 7 is now row 16 (B2 sheets sent); row 8 is vetter Q2; row 9 (ELPV) is vetter Q7.

## 3d. Decisions waiting on the user, 1 Nov (added 1 Nov)

| # | Decision | Facts for it | Source |
|---|---|---|---|
| 19 | **The deployable model:** adopt E-PF (the PF 5-member ensemble at argmax) over the house ensemble? | coach and judge recommend E-PF: test n.d. on all three primaries with positive point estimates (relF1@2 +0.0121); E1 inactive IoU +0.2141, CI above 0 (10 cells / 7 images, borderline under Bonferroni); E1 crack precision lower (−0.05). FINAL (cv02, +0.75, 0.492) is not comparable by rule; E-PF's 0.4920 needs a bias the pre-registered val width flag rejected (val crack precision drop +0.0753 > 0.05) | `verify_pf2e.md`; doc 20 §5. [3 Nov: still open; SKR2E FAILED and did not displace E-PF as the recommended candidate (doc 21 §5).] |
| 20 | **D2 width flag:** both ensembles tripped it (val crack precision drop +0.0543 / +0.0753), so the headline is argmax. Change the D2 grid or the threshold for future protocols? | A pre-registered question for a later protocol, never a re-pick of PF2E (coach). [3 Nov: the flag also decided SKR2E, by 0.0015; now §3e row 27.] | `verify_pf2e.md` "What this decides" |
| 21 | **Half-cut routing (parked):** wanted enough to label half-cuts with E1-like context? | The offset exists only on E1's own labels (oracle b +5.4 vs −0.8); simulated half-cuts show no offset; H36 cleanup would likely not show it (judge); B2 masks or B3 + mining are the route; no manual labelling unless really needed | doc 20 §3.1; doc 13 A16, E30 |
| 22 | **A8 full arm** if the screen says GO (5 seeds, E1 co-primaries possible: one more GPU run set and an E1 opening) | Screen queued first after THIN-B3. [3 Nov: moot; the screen KILLED, doc 21 §1.] | `protocol_A8screen.md` §5 |
| 23 | **SKR follow-up?** (added ~21:40) | SKR FAILED by the rule (test crack IoU −0.0136, narrow: leave-top-3-out +0.010) but lifts E1 crack detection (relF1@2 +0.059 BETTER; any-hit component recall 0.381 → 0.523) at ~2x false-alarm px. A follow-up is a new protocol: weight 0.1 or a val OP on a wider grid, a precision guard as a co-primary, a width-insensitive E1 readout. [3 Nov: done as SKR2 (w 0.1): PASS, narrow; its ensemble check SKR2E FAILED; fresh-seed SKR2C pending, §3e row 24.] | `verify_thin_b3.md` (coach, judge) |

Still open: §3c rows 16 (marks: optional by team-lead's reading of the user's 31 Oct line; not done, not re-asked), 17 (HF sample), 18 (who rebooted gaint on 30 Oct); §3b rows 10 and 11.

## 3e. Decisions waiting on the user, 3 Nov (added 3 Nov)

| # | Decision | Facts for it | Source |
|---|---|---|---|
| 24 | **Next step:** (a) pause GPU work and write up; (b) SKR2 on new seeds (SKR2C: training tonight, opening = E1 #7 on your OK); (c) wait for B2 | SKR2's E1 relF1@2 pass is 0.0013 over its bar (label fragile, effect robust); SKR2E failed at its own OP; judge's P(PASS) for SKR2C 0.34 to 0.90 if the true effect is 0.5 to 1x #5's, ~0.05 if none | `verify_skr2_hc2.md`, `verify_skr2e.md`, `judge/out/skr2c_power_out.txt` |
| 25 | **B2:** (a) the user marks (sheets sent 2 Nov 11:18; whole 512 crop is the unit); (b) a new crack-only agent prereg (its crack gate passed on house CSIR cells only, not on Hanifi cracks); (c) skip B2 | Agent raters passed the crack gate (sens 20/20, spec 17/20) and failed the scuff gate (1/8); on gate B's Hanifi half-cells the raters found 1 of 14 cracks (speck-level labels; reported, not gated); B2's purpose is scuff / crack half-cell context | `ideas/b2_agent_marking_prereg.md`; log 2 Nov 11:49 |
| 26 | **Blender renders vs gaint lanes:** a standing rule when outside GPU jobs share gaint | Outside processes took free memory to 2,078 MiB with 3 lanes (2 Nov 12:18); team-lead chose MAXC 2 for the unattended night | doc 13 D46 |
| 27 | **D2 width flag (0.05 on val crack pixel precision):** keep, or pre-register a shared / matched-precision OP rule for future ensemble protocols | It sent both PF2E arms to argmax and passed E-SKR2 by 0.0015, which decided SKR2E | doc 13 C20, E34 |
| 28 | **HC route (open):** a dilution-targeted variant, or leave it | HC n.d.; HC2 FAIL (G1); label vs dilution undecided | `verify_skr2_hc2.md`; doc 13 E31 |

Still open: §3c rows 17 (HF sample), 18 (who rebooted gaint on 30 Oct); §3b rows 10 (40-segment audit, 4 label questions) and 11 (idle cv02 shells); §3d row 21 (half-cut labels for routing).

## 3f. Decisions waiting on the user, and on Om, 12 Nov (added 12 Nov)

| # | Decision | Facts for it | Source |
|---|---|---|---|
| 29 | **SKR2C opening (E1 #7):** OK the opening, or not | Training done (10 rc 0 of 10). The opening is a third look at the same test and E1 cells (#5, #6); stated chances R PASS ~35-65%, seed-aware replication ~25-45%; stage 2 must be built and frozen first; needs gaint access | `protocol_SKR2C.md` §3-7; doc 21 §10 |
| 30 | **Thermal:** resume picks 1 and 3b (CPU only, on the approved data), and send Om the report (SUMMARY final; ADDENDUM needs its datascout confirmation and the A3 results) | Remaining readouts are frozen and cheap (pick 1 R1 / R2 / R3b; pick3b R1 / R2 / R3); a dated pick3b amendment for the IR rule is needed first (plan v1 §5; the attempted v1.1 freeze is empty, content unknown; doc 13 D55) | doc 22 §11 |
| 31 | **For Om: E-PF inference location** (gaint CPU as PF2E did, or a local copy of the 5 checkpoints) | Held since 4 Nov; T26 / T27 / T39 ran only on EL proxies | `om_2026-11-04_decisions.md` (3) |
| 32 | **For Om: licences / release** (mixing CC BY 4.0 sets with BenchmarkEL, which has no licence file; a CC BY derivative release of a registered A1 set; terms for WattCycle images) | CC BY 4.0 allows an adapted release with credit and a note of changes (R, check S-26); E-PF predictions in a release carry BenchmarkEL's licence question | `synth/SUMMARY.md` §3 |
| 33 | **For Om: capture funding and the WattCycle questions** (Pi HQ low-cost EL kit ~₹25k + lens and filter; UV torch; optional ₹62k camera, NISE fees, phone IR; send Q1-Q20) | WattCycle has drone thermal only; EL rig 2-3 months away (4 Nov); pick 2's week plan has slipped (nothing sent) | `capture/replan_pick2.md`; `synth/SUMMARY.md` §4 |
| 34 | **For Om: the A1 extension** (0.55 GB; or all 157 A1 IR 0.26 GB, then ~2 GB EL) and other optional downloads | Dark IR on A1 / A2 is row / edge-level (G0); A1's IR crop is not the module (doc 13 A19); disk is no longer tight (52 GB) | `synth/SUMMARY.md` "Later asks" |

Still open: §3e rows 24 to 28; §3d row 19 (adopting E-PF); §3c rows 17, 18; §3b rows 10, 11; §3d row 21.

## 4. Remaining work for part 1 (training methodology)
Ordered roughly by information per cost. None of these is started; each would need its own locked protocol and the user's go-ahead.

| Item | What it answers | Rough cost | Source |
|---|---|---|---|
| A gaint replication of P13 (BsM5 seeds are done: 5 since Amendment 2) | BsM5's crack gain is +0.029 on 5 seeds (secondary). P13 had no gaint replication (Amendment 1). | 3 to 5 runs on gaint | `results/p13/README.md`, `results/p17/README.md` |
| In-domain self-supervised pretraining (masked image modelling) of the encoder | Uses unlabelled cells without pseudo-labels. Our directions report rates it the main "no-pseudo-label rival". [Qualified 30 Oct: run as MIM5 on 29 to 30 Oct, n.d. at 5% under the house fine-tune, which erased the MIM layers; MIM100-PF in protocol_100 tests it at 100% with an encoder-preserving fine-tune (doc 19).] | 1 to 2 GPU-days | `directions_2026-10-10.md` §4; proposal §5 E3 |
| Distillation into a 2 to 5M-parameter student | The deliverable model size | about 6 runs | proposal §5 E5 |
| Severity pipeline (components, skeleton, isolation, Köntges A/B/C) | The measurement WattCycle needs. It was lost in the reset and must be rebuilt. | CPU, 2 to 3 days | proposal §5 E6; phase 0 handoff "Subpath A" |
| Rare-class share floor and cap for pseudo-labels | Fixes the collapse at 5% (P10) and the over-prediction on UCF (phase 1) | a few runs | proposal §3 |
| More label subsets (split seeds 1, 2) or cross-validation over the 582 cells | Everything so far uses one labelled subset and one 50-cell test set | reruns | handoff §12.4 items 6 and 7 |
| Larger test set (data now local: doc 17) | Inactive is decided by about 3 test cells. The candidates add many crack cells but little inactive (A: +10 inactive cells, 9,158 px) | re-scoring existing checkpoints on the new cells (no training) | `results/escdd_audit/README.md` §8; E1 README |
| Tolerant Dice term; tuning the tolerance radius R | P14 tested only R = 2 with a tolerant CE term | a few runs | P14 "Not claimed" |

## 4b. Ranked next items, 30 Oct (added 30 Oct; `team_2026-10-29_features/coach_strategy.md` §2, S unless tagged)
Coach's order by expected test gain per cost. None beyond protocol_100 and B1/B2 is started; each needs its own protocol.

| Rank | Item | Condition | Named target | Source |
|---|---|---|---|---|
| A | Fix the fine-tune: SUP100-PF (in flight in protocol_100) | none | test primaries at 100% | `coach_strategy.md` §2 A; R arxiv:2202.10054 [Qualified 31 Oct: n.d. on test; E1 lead only (§4c)] |
| A2 | ResNet-50 and ConvNeXt-T under PF, one arm each vs SUP100-PF | only if SUP100-PF passes or shows a same-sign gain on clean cells | BMRK crack (Track D's frozen-feature signal) | §2 A |
| A3 | Weight average of the 5 PF seeds (model soup), inference only, val first | as A2 | a single-model alternative to the ensemble | §2 A; R arxiv:2203.05482 |
| B1 | Label audit of train | done; waiting on the user's marks (§3b row 6) | label errors in train | §2 B; doc 19 §8.1 |
| B2 | Mine pool half-cells for scuff + crack cells; the user labels 20 to 40 | candidate mining running (gaint CPU, 12:09 IST); labelling is a user decision (§3b row 7) | E1 crack recall, BMRK crack | §2 B; doc 18 §U item 1 |
| B3 | Scuff as its own class: BEST vs BEST+S, 5 v 5 | after protocol_100, on its winning recipe; test-GT choice (§3b row 8) | E1 crack false alarms on scuff, E1 crack precision | `spec_b3_scuff.md` |
| C | Thin-structure crack loss (Skeleton Recall; clDice the alternative), one arm at 100% on the best recipe | after A | relR@2 and component recall at matched relP@2 (goal 0.90 / 0.90) | §2 C; R doi:10.1007/978-3-031-72980-5_13, doi:10.1109/cvpr46437.2021.01629 |
| D | Inference-only E1 checks: BN re-estimation on pool half-cells; ResNet-34 + ResNet-50 ensemble members | any time the GPU queue is busy | E1, descriptive | §2 D; doc 18 §U item 4 |

**Stop (coach):** further pool representation learning (contrastive, clustering, diffusion, DDeP); pseudo-label SSL at ≥ 20% labels; 5% screens of label-consuming methods.

**If SUP100-PF is n.d. or worse (coach):** erasure is benign for this task; close the init / backbone / pretraining line "with a better reason than before".

## 4c. Ranked next items, 31 Oct (added 31 Oct; coach `verify_100_o2.md` §6 and vetter's shortlist, S unless tagged)

| Rank | Item | Condition | Source |
|---|---|---|---|
| 1 | PF2: replicate PF's E1 effect with pre-registered E1 co-primaries (RN50-PF as a third arm) [Done 1 Nov: PF2 PASS (E1 inactive replicated, test relF1@2 narrow); RN50-PF FAIL. doc 20 §4.] | user OK; vetter Q1 | `log.md` 31 Oct 07:15 |
| 2 | Hanifi `_rf` half-cells as the check for the B2 ranking and BN-HC's bias (CPU) [1 Nov: `_rf` used as a validation set (F51 for crack); the H36 half-cut crack labels proved unusable (doc 13 A16); T9 closed TTA (doc 20 §3.2).] | vetter Q3 | `review_suggestions_2026-10-30.md` §3 |
| 3 | B3 scuff class on BEST [1 Nov: in THIN-B3, opening running at writing.] | test-GT choice (vetter Q2) | `spec_b3_scuff.md` |
| 4 | Skeleton Recall loss on BEST [1 Nov: in THIN-B3 with clDice, opening running at writing.] | metric choice (vetter Q5) | vetter §3 item 4 |
| 5 | User labelling: B1 marks, then B2 masks if the marks support it [1 Nov: optional by team-lead's reading of the user's 31 Oct line "refrain from manual labelling unless very much needed"; not done, not re-asked (doc 12 D77).] | the marks | vetter §3 item 5 |

**Closed (E):** pool representation learning and crack copy-paste at 100% (n.d.); the large-pool download (condition failed, D58).

## 4d. Ranked next items, 1 Nov (added 1 Nov; ETAs are S, from runner's and the build files' estimates)

| Rank | Item | Condition | ETA | Source |
|---|---|---|---|---|
| 1 | THIN-B3 verify (runner local, coach on gaint CPU, judge on the laptop); fill the record's THIN section and docs 11 / 15 / 20 [Done 1 Nov 21:21-21:29: no arm passes; doc 20 §6.0.] | opening rc 0 | tonight, after ~22:00 | `protocol_thin_b3.md` |
| 2 | A8 screen (4 runs × 4k steps, then CPU scoring 15 to 30 min) | THIN's opening done | night of 1 to 2 Nov [Done: KILL, 1 Nov 23:40] | `protocol_A8screen.md`, `build_a8_runner.md` |
| 3 | HC (5 runs ≈ 12.5 lane-h, then an opening ~1.5 to 2 h; E1 opening #3) | THIN's opening done | 2 Nov, likely midday or later [Done: n.d., 2 Nov 03:18] | `protocol_HC.md`, `build_hc_runner.md` |
| 4 | B6 on cv02 (builder's fold roots + scorer ~2 to 3.5 h CPU; ~6.5 h on cv02) | ≥ 3 qualifying cv02 GPUs per wave; coach APPROVED | 2 Nov at the earliest [Done: n.d., 2 Nov 22:19] | `protocol_B6.md` |
| 5 | A8 full arm, if the screen says GO | the user (row 22) | after the screen [Moot: KILL] | `protocol_A8screen.md` §5 |

**Closed (E):** RN50 under PF (FAIL); TTA (T9); label-free per-panel thresholds; intensity normalisation; high resolution; appearance augmentation as an arm; the large-pool download (item 13). **Parked:** half-cut routing; the structure channel (ideas 3 + 4); scuff via SAM; trust-region crack cleanup.

## 4e. Ranked next items, 3 Nov (added 3 Nov; S unless tagged)

| Rank | Item | Condition | ETA | Source |
|---|---|---|---|---|
| 1 | SKR2C training (10 runs, seeds 10-14, MAXC 2) | judge confirms the guard / queue fixes (stage-1 review b0d866a4, G1-G8) and dry passes 1-3; then coach's APPROVED (protocol locked 02:37) | ~12.3 h wall from launch (runner's estimate) | log 3 Nov 02:23 [12 Nov: done 3 Nov 11:24:04, 10 rc 0 of 10; §1k] |
| 2 | SKR2C opening (E1 #7) | the user's OK (§3e row 24) | ~1.5 h after the last run (S; the S2 opening took 1 h 22 min) | `protocol_SKR2C.md` v1 (locked 02:37) |
| 3 | B2 marks or a crack-only agent prereg | the user (row 25) | user marks ~15 min (Om B4's estimate) | `ideas/b2_agent_marking_prereg.md` |
| 4 | Write-up of the session's negative and narrow results (A8 KILL, HC n.d., B6 n.d., SKR2 PASS narrow, HC2 / SKR2E FAIL) | the user (row 24a) | | doc 21, doc 11 rows 43 to 50 |

**Closed (E):** foundation encoder (A8 KILL); the HC2 (a2) ignore design; Om's A1, A2, A3, A5, A6. **Parked:** A4 (structured crack head) behind SKR2; half-cut routing; the structure channel (ideas 3 + 4). **Open:** the HC route (user, 2 Nov 21:51).

## 4f. Ranked next items, 12 Nov (added 12 Nov; S unless tagged)

| Rank | Item | Condition | ETA | Source |
|---|---|---|---|---|
| 1 | Re-establish read-only gaint access and re-check SKR2C's `launch.log`, `autostop.log` and run dirs | the user (ssh after the reinstall) | minutes | doc 14 §1.2f |
| 2 | SKR2C stage 2 (opening build, frozen md5s) and the opening (E1 #7) | the user's OK (§3f row 29) | stage 2 ~1-2 h (S); the S2 opening took 1 h 22 min | `protocol_SKR2C.md` §6 |
| 3 | Thermal pick 1 A3 R1 / R2 (module IR screen by defect class; screening recall of the EL dark area) | the user (§3f row 30); CPU, approved data | ~0.5-1 day (S) | `pick1/plan_pick1.md` Amendment 6 |
| 4 | pick3b amendment (IR rule), then 3b-R1 / R2 (FF loss vs EL dark proxy and drone IR) | after rank 3 (needs pick 1's A3 module table) | ~0.5 day (S) | `pick3/plan_pick3b_v1_FROZEN_eaec6f26.md` |
| 5 | pick 1 R3b + pick3b 3b-R3 (sunlit cell-level G0 by induced cause) | registration QA co-signed by a second agent before any number | ~1 day (S) | same |
| 6 | Finalise the thermal ADDENDUM and send the report to the user and Om | after ranks 3-5, or now as an interim | hours | `synth/ADDENDUM_2026-11-04.md` |
| 7 | Carried: B2 marks, write-up of the 1 to 3 Nov results, the D2 width-flag rule | the user (§3e) | | doc 15 §3e, §4e |

## 5. Parts 2 and 3 (after part 1)
- **Part 2, architecture.** Phase 0 ideas:
  - is the self-attention block in SA U-Net++ (`sigmoid(Q+K)*V`, an elementwise gate) worth anything (SA vs no-SA ablation);
  - native narrow models (base width 20 or 24, 1.79M or 2.58M parameters);
  - coarse non-local or axial attention;
  - thin-structure-preserving downsampling (check first whether cracks survive encoder pooling).

  Source: phase 0 handoff, Part 2.
- **Part 3, deployment.**
  - Latency harness on Jetson.
  - Compression: Torch-Pruning to about 2M, INT8 + TensorRT (the Jetson has no FP8).
  - Rerun the severity pipeline on every compressed model; Pareto plot.
  - About 0.2 s per cell is available (lit).

  Sources: phase 0 handoff "Subpath B"; `directions_2026-10-10.md` §1.5.
- **Power loss:** out of scope unless valid data appears (user, 11 Oct). Literature correlations exist (NREL crack-to-power-loss, Dhimish & Hu 2022, Kropp et al. 2018; links in the phase 0 handoff).

## 6. Keeping this handbook current
After any new result, update these docs (done for P15 and P16 on 12 Oct; P17 on 13 Oct, plus `00` and `16`):
- `10_experiments_P13_P16_E1.md`: P15 and P16 sections.
- `11_results_synthesis_and_claims.md`: evidence table rows 3, 7, 10.
- `13_problems_pitfalls_open_issues.md`: open questions.
- This file.
- `handbook/sources/`: re-run `bash handbook/sync_sources.sh`.
- (Added 30 Oct) For agent-team work: `18_experiments_trackD_trackM.md` (24 to 27 Oct) and `19_feature_learning_and_100pct_plan.md` (28 to 30 Oct); new rows in 11 (18 to 24), 12 (§4c), 13; and `sources/teams/`, `sources/session_records/` via `sync_sources.sh`. When protocol_100 is verified, add its results to doc 19 §7 and doc 11, and update 00 and this file.

## 7. Housekeeping debts

| Item | Note | Source |
|---|---|---|
| Rotate the Dropbox app secret | It was pasted in chat on 2 Oct; rotation not confirmed | phase 1 handoff §2.4 |
| cv02 `/tmp/noob_el` is wiped on reboot | Results are pulled into `~/mtp/research/results/` after each experiment. Checkpoints, P17 included, were copied to gaint `cv02_noob_el` on 13 Oct (§1c); runs after that need another pass | handoff §2.2 |
| GitHub | The research notes repo is local only. Push nothing without asking the user. | standing instruction |
| gaint shutdowns | Unexplained reboots on 2, 6 and 7 Oct; the queue resumes from `latest.pth` | handoff §2.1 |
| Idle tmux sessions | About 23 of ours on cv02 and 3 on gaint (§1b, §1c), all idle. Close them only on the user's say-so. | server check 13 Oct |
| Untracked files in `~/mtp/research` | `papers/` (paper PDFs: local only, never commit or redistribute) and `scripts/aggregate_runs.py` (a P6/P7 re-score aggregator, untracked since 10 Oct; its origin was not recorded). Both left as they are. | `git status`, 13 Oct |
| (Added 30 Oct) Untracked or modified files in `~/mtp/research` on 30 Oct | Untracked: `log.md`, `papers/`, `results/seipv_compare/`, `team_2026-10-21/alhvr/handbook_al1.diff`; modified: `team_2026-10-21/alhvr/log.md` (one appended line). Left as they are; the handbook commit touches only `handbook/` | `git status`, 30 Oct |
| (Added 30 Oct) Per-cell raw JSONs of MIM5, DDeP5, CP5 | About 240 MB, kept locally and on gaint with `MANIFEST.md5`, not in git | `SESSION_RECORD_2026-10-28_to_30.md` §11 |
| (Added 30 Oct) CP5 s1/s3 automatic rescore files | Exist, unopened; CP5 is not scored | doc 19 §3.3 |
| (Added 1 Nov) Quarantined test / E1-scuff outputs on gaint | `builder_scratch/quarantine_test_reads_2026-10-31` (chmod a-r, MANIFEST.md5 e367b101): keep unread; delete only on coach's or the user's word | doc 13 D35 |
| (Added 1 Nov) Large local per-cell files of the 31 Oct team | About 370 MB (raw pulls, calib records), gitignored, with `MANIFEST.md5`; laptop disk is tight | `team_2026-10-31_next/.gitignore` |
| (Added 3 Nov) B2 blinding files | `judge/b2_key/` (the bundle key) and `judge/b2_scores/` stay with judge and out of git; `b2_bundle/` (70 MB) is gitignored; the 3 Hanifi B2 panel cells stay redacted in `handbook/sources/` until the user marks B2 | log 2 Nov 11:38, 11:49 |
| (Added 3 Nov) Laptop disk at 98% | judge deleted its 171 MB scratch pull (2 Nov 21:48); raw pulls of A8, HC, S2, SKR2E, B6 are gitignored with MANIFESTs | log 2 Nov 21:48, 23:32 |

## Related docs
- `10_experiments_P13_P16_E1.md`: designs of P15 and P16
- `11_results_synthesis_and_claims.md`: what the pending results will decide
- `12_decisions_log.md`: decisions so far
- `13_problems_pitfalls_open_issues.md`: open issues in detail
- `14_code_and_infrastructure.md`: how runs and post-processing work
