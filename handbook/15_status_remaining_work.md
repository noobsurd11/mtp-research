# 15. Status and remaining work

**What this covers.** The state of every experiment on 12 Oct 2026, about 05:30 IST (all P-series experiments finished), and the server state when the work session closed (13 Oct, about 01:30 IST). What ran overnight, what is left for part 1 of the thesis, which decisions are waiting on the user, and the housekeeping debts. Updated 13 Oct ~08:15 IST for P17 and P13 Amendment 2 (§1, §1c). This doc goes stale fastest: check `results/` and the git log of `~/mtp/research` for anything newer.

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
| **P17** (cv02, SKCDF-style decoupled decoder on BsM5) + **P13 Amendment 2** (BsM5 s3–4) | **Done**, 7 runs (13 Oct 01:55 to 04:08 IST), all rc = 0; analysed about 08:00 IST.<br>• **P17 rule 1 n.d.:** BsD5 − BsM5 −0.006 / +0.011 / −0.008 (thresholds about 40% of BsM5's gain). BsD5 − A5c passes on all three.<br>• **BsM5 on 5 seeds:** − A5c +0.029 / +0.107 / +0.045, passes; CsM5 − BsM5 now n.d. | `results/p17/README.md`, `results/p13/README.md`, `results/e1/e1_p17.md` |
| **P19** (cv02, reproduction of Hanifi 2025, IEA/AIE) | **Done**, 8 runs (14 Oct 08:58 to 09:31 IST), all rc = 0. Their code, release split, no augmentation. VGG16-UNet features 0.678 vs 0.663, crack 0.352 vs 0.335; defects 0.246 vs 0.326 (our test lacks dead cell, belt mark) | `results/p19/README.md` |
| **P18** (cv02, EXPLORATORY: BsM recipe at 10% and 20%) | **Done**, 8 runs (13 Oct 17:31 to 19:40 IST), all rc = 0; analysed about 19:50 IST.<br>• Arithmetic: BsM10 − A10 and BsM20 − A20 pass on inactive only (+0.132, +0.060); crack n.d.<br>• Without the noisy cell: BsM10 passes on all three; BsM20 inactive only (crack +0.013, thr 0.014).<br>• BsM20 s4 fails on the noisy cell (34k FP px). | `results/p18/README.md`, `results/e1/e1_p18.md` |
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

**Held, do not touch:** the gaint `extpool_20261007` night queue (old-era Mean Teacher runs with SemiCE). It was held by hand on 8 Oct, 01:18 IST (19:48 UTC on 7 Oct) while SemiCE was under audit, and P2 later showed SemiCE is invalid. The user's standing instruction is to leave it held and untouched. (Source: the user's command in `sources/chat/user_messages_2026-10-07_to_11.md`, 2026-10-07T19:48Z; session summaries.)

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

## 4. Remaining work for part 1 (training methodology)
Ordered roughly by information per cost. None of these is started; each would need its own locked protocol and the user's go-ahead.

| Item | What it answers | Rough cost | Source |
|---|---|---|---|
| A gaint replication of P13 (BsM5 seeds are done: 5 since Amendment 2) | BsM5's crack gain is +0.029 on 5 seeds (secondary). P13 had no gaint replication (Amendment 1). | 3 to 5 runs on gaint | `results/p13/README.md`, `results/p17/README.md` |
| In-domain self-supervised pretraining (masked image modelling) of the encoder | Uses unlabelled cells without pseudo-labels. Our directions report rates it the main "no-pseudo-label rival". | 1 to 2 GPU-days | `directions_2026-10-10.md` §4; proposal §5 E3 |
| Distillation into a 2 to 5M-parameter student | The deliverable model size | about 6 runs | proposal §5 E5 |
| Severity pipeline (components, skeleton, isolation, Köntges A/B/C) | The measurement WattCycle needs. It was lost in the reset and must be rebuilt. | CPU, 2 to 3 days | proposal §5 E6; phase 0 handoff "Subpath A" |
| Rare-class share floor and cap for pseudo-labels | Fixes the collapse at 5% (P10) and the over-prediction on UCF (phase 1) | a few runs | proposal §3 |
| More label subsets (split seeds 1, 2) or cross-validation over the 582 cells | Everything so far uses one labelled subset and one 50-cell test set | reruns | handoff §12.4 items 6 and 7 |
| Larger test set (data now local: doc 17) | Inactive is decided by about 3 test cells. The candidates add many crack cells but little inactive (A: +10 inactive cells, 9,158 px) | re-scoring existing checkpoints on the new cells (no training) | `results/escdd_audit/README.md` §8; E1 README |
| Tolerant Dice term; tuning the tolerance radius R | P14 tested only R = 2 with a tolerant CE term | a few runs | P14 "Not claimed" |

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

## 7. Housekeeping debts

| Item | Note | Source |
|---|---|---|
| Rotate the Dropbox app secret | It was pasted in chat on 2 Oct; rotation not confirmed | phase 1 handoff §2.4 |
| cv02 `/tmp/noob_el` is wiped on reboot | Results are pulled into `~/mtp/research/results/` after each experiment. Checkpoints, P17 included, were copied to gaint `cv02_noob_el` on 13 Oct (§1c); runs after that need another pass | handoff §2.2 |
| GitHub | The research notes repo is local only. Push nothing without asking the user. | standing instruction |
| gaint shutdowns | Unexplained reboots on 2, 6 and 7 Oct; the queue resumes from `latest.pth` | handoff §2.1 |
| Idle tmux sessions | About 23 of ours on cv02 and 3 on gaint (§1b, §1c), all idle. Close them only on the user's say-so. | server check 13 Oct |
| Untracked files in `~/mtp/research` | `papers/` (paper PDFs: local only, never commit or redistribute) and `scripts/aggregate_runs.py` (a P6/P7 re-score aggregator, untracked since 10 Oct; its origin was not recorded). Both left as they are. | `git status`, 13 Oct |

## Related docs
- `10_experiments_P13_P16_E1.md`: designs of P15 and P16
- `11_results_synthesis_and_claims.md`: what the pending results will decide
- `12_decisions_log.md`: decisions so far
- `13_problems_pitfalls_open_issues.md`: open issues in detail
- `14_code_and_infrastructure.md`: how runs and post-processing work
