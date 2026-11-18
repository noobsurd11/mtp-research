# HANDOVER from the laptop copy to the gaint copy (session 149c5b71, written 14 Nov 2026, 01:11 IST)

You (the gaint copy) were resumed from a transcript that ends about 23:55 on 13 Nov. This file covers everything since. After reading it you are the only orchestrator. The laptop is powered off after this file is confirmed on gaint; its copy of the project is stale from now on.

## 1. What runs unattended right now (do not disturb)
| Where | tmux | What | Ends about |
|---|---|---|---|
| gaint | `bench_q_w1g2` | W1-G2: PF v1.1, cv5v2 folds 0-4, **seeds 7 and 8** (10 runs, then 10 dumps), queue `/home/noob/work/bq/w1g2`, el_bench 31c0c36 (must stay untouched). Started 00:00:58 by its waiter | 09:00 to 10:30 |
| gaint | `s2c_open` | **SKR2C opening** (sealed test + E1, the user's OK of 12 Nov, coach APPROVED 00:20): driver `s2c_opening.sh`, FROZEN 836be7e5, started 00:22:45; waits at the shared gate for 9,900 MiB free. I set `bq/w1g2/MAXC` to **2** so a lane stays free for it | 1.5 to 2 h after the first free lane (about 02:20) |
| gaint | `bench_wait_w2a` | waiter that launches wave 2a (61 runs + 161 dumps) after the W1-G2 chain ends | starts about 09:30 to 10:30 |
| gaint | `bench_relay_w1c` | pulls finished W1-C runs from cv02 into `/home/noob/work/bench_relay/w1c` | with the cv02 queue |
| cv02 | `bench_q_w1c` | W1-C: 45 runs (C1 PF v1.1 seeds 5-9, C2 house v1.1 seeds 5-6, C3 PF v1 labels seeds 5-6), LPG 1. cv02 became free of other users in the evening | morning of 14 Nov |
Two gaint queues block each other through the "outside process" rule in `bench_lib.sh` (a queue will not start a run while a GPU process that is not its own holds more than 1 GB), so queues on gaint run in series. A w2a queue armed now simply waits until W1-G2 has no run alive.

## 2. What finished since your context ends
- **W1-G done** (10 runs + dumps, 23:57) and **first read done** (00:03): `results/W1G_FIRST_READ.md` (read it; numbers and the lead's rulings: baseline crack relF1@2 0.842, strict IoU 0.362, inactive IoU 0.498, mIoU-R13 0.612; dti_hysteresis and src_calib show no gain; D0 placement 0.604, placement arms keep their prior). Tables: `results/w1g_read/`. Provisional until the tools pass the w2a review.
- **Second batch of method teams complete**: `cards/T6..T13_*_{family,spec}.md`, ledgers `cards/ledger/T6..T13.tsv` and `T1b..T5b.tsv`, critic's review **`cards/WAVE3_REVIEW.md`** (47 items: 25 GO, 13 FIX, 9 DROP; an ordered 10-day plan in its section 4; 12 questions for the lead and 7 for the user in section 7). Master ledger `cards/ledger/MASTER.tsv`: 639 papers, 0 open (RUN_NOW 44, RUN_AFTER_GATE 57, BENCH_ONLY 78, PROTOCOL 61, PROMOTE 10, PARKED 392, VOID 2). The 10 PROMOTE papers (from the sweepers) have no card yet.
- **SKR2C stage 2 built, frozen, reviewed (APPROVED)**: `../team_2026-10-31_next/build_s2c_stage2.md`, `review_s2c_stage2.md`, rulings `rulings_s2c_stage2.md`. Opening started (table above).
- **Wave 2a**: merged, reviewed PASS and armed behind W1-G2; see section 3.
- **cv02**: W1-C launched 17:02 by the lead after review PASS (a reviewer subagent's launch command was refused by the permission classifier; the same command from the lead session went through. Expect the same for any queue launch by a subagent).
- **Move**: user's decisions and the layout are in `migrate/README.md`. Done: `/home/yugma` on gaint, tree + Claude state synced, two-account layout, aliases `claude-oth` / `claude-nb`, helpers run locally on gaint, paper-mcp venv and unit files, the user's secret copies, second-account login. See section 6 for the MCP.

## 3. Wave 2a state at handover
- Merged and reviewed: worktree `/home/noob/work/bench_wt_w2`, branch `bench_w2`, commit **c57508e** (x1 b725f17 + x2 0f509e9 + x3 69a60f5 on 31c0c36, plus fcc2bc6 card gates and c57508e MAXH pass-through). Flag-off identity IDENTICAL for 6 arms, pytest 446 passed, baseline card renders equal at both commits. Review: **`harness/REVIEW_W2A.md` PASS for all 7 cards** (rcs, ema_wise_posthoc, soft_band_jml, jml_hard, swad_const, encoder_spd, encoder_spd_ctrl). Request: `harness/LAUNCH_REQUEST_w2a.md`.
- **Armed by the lead at 01:09** through the reviewer's waiter: tmux `bench_wait_w2a` (pid 2066007) runs `bq/w2a/launch_w2a.sh` 150 s after `chain done` appears in `bq/w1g2/chain.log`. Then tmux `bench_q_w2a`: 61 training runs (seed 5 of every arm first, then seed 6) and 161 dumps to `/home/noob/work/bench_dumps/w2a`, about 50 h. **MAXC 2** (no GPU peak is measured for the new cards; SKR2C needs a lane). Stop before it starts: `touch /home/noob/work/bq/w2a/NOSTART`. The worktree must stay at c57508e and clean while the queue runs.
- No GPU smoke was run for the 6 new cards. The first job of each arm is its smoke: check `bq/w2a/launch.log` for `config OK` and `startup line OK`, and the first step lines for NaN, when it starts (about 09:30 to 10:30). If a peak is under 8,000 MiB on all arms, MAXC may go to 3.
- The critic's order is w2a seed-5 block, then the U-dev block (LOSO-2 roots, not built yet), then w2a seed 6. To interleave, `touch bq/w2a/HOLD` when the seed-5 block is done and remove it after the U-dev block.
- Not built (integrator's list): the ema bit-identity hash against W1-G, the swad fold-0 pass / fail script, the PF encoder-deviation pass the spd gate needs, WiSE readout dumps, F51 / H36 dumps.
- The read tools (crossfit_op, read_w1, src_calib, dti, d0) are now reviewed inside `bench_wt_w2`; run every later read from there (not from `bench_wt_x3`).
- Scratch that can be deleted: `/home/noob/work/bench_x1_io` (4 GB), `/home/noob/work/bench_w2_io/exp` (5.5 GB).

## 4. First actions, in order
1. Sanity: `hostname` is `giant`; `scripts/gssh.sh 'hostname'` prints `giant`; `cat /home/yugma/mtp/.last_sync_from_laptop`.
2. Wave 2a: act on section 3.
3. SKR2C: when `/home/noob/work/s2c/opening.log` has its end line, set `bq/w1g2/MAXC` back to 3. Then do review note N1 first (`s2c_d_boot.py --selftest`, `m1_analyze.py` md5 8e566254), then the local readout (`scripts/s2c/opening/local/s2c_post_local.sh 836be7e5...`; it was written to run on the laptop and has only had `bash -n`: read it before running, it now runs on gaint where the helpers are local). Then an independent coach recompute, verdicts R and D per `protocol_SKR2C.md` section 3, the registry lines (`e1_openings.md` #7, `benchmark/test_openings.md` row 18), handbook.
4. When W1-G2 dumps exist (10 manifests for seeds 7, 8): rerun the read with all four seeds and the A/A split (`harness/W1_READ.md`; `--arm ... w1g_pf_v11_f[0-4]_s[5-8]`, `--aa PF:5,6:7,8`) from the reviewed merged worktree. That gives margin M on gaint.
5. When W1-C is complete and relayed (45 runs): the W1-C read (same file), house vs PF, label-fix ablation, A/A on cv02.
6. Start the critic's plan, `cards/WAVE3_REVIEW.md` section 4, block A (CPU analyses on existing dumps) and block C (config-only benchmark rows on cv02, which is free now). Rulings in section 5 below. Keep agent counts low: the 5-hour usage window that began 23:32 has already carried about 4.5 M subagent tokens.
7. Morning: put the user's questions (section 7) to the user in one batch, with the first numbers.
8. Owed, lower priority: handbook refresh with the new protocol and first numbers; cards for the 10 PROMOTE papers; benchmark `PROTOCOL_v0.2.md` from T12's spec; N0 nested teachers; the pathfinder cards.

## 5. Lead's rulings on the wave 3 critic's questions (L1 to L12)
L1 R0 allowed with the Y2 fixes and a ledger line. L2 the duplicate tool may read sealed images (pixels only, pair lists out, no label or prediction). L3 decision layers are a labelled entry class; OP-C is the comparator for prior-shifting arms. L4 inactive policy Y1 accepted. L5 `skr01_pf_v11` anchor arm added; SKR2C is being opened first. L6 seed rule for table rows accepted. L7 headline stability Y13 accepted. L8 gaint order: w2a seed-5 block, U-dev block, w2a seed-6 block; all LOSO runs on gaint. L9 the six wave-2 deferrals accepted (they stay open in the ledger, not void). L10 one registered E1 opening near the end, at most 3 candidates, by the proposed rule; confirm with the user in the last week. L11 one pool list and one stream-id registry: yes. L12 capacity: plan to the 80-hour cut line.

## 6. Research MCP: already moved, do not start it again
- Laptop: `paper-mcp` and `researchmcp-tunnel` stopped and disabled at 01:09.
- gaint: both enabled and started at 01:10 as user services (`systemctl --user status paper-mcp researchmcp-tunnel`). Server on 127.0.0.1:8765, tunnel registered, `https://researchmcp.noobsurd.space/` answers through gaint (404 at the root path is the server answering). Code `/home/yugma/paper-mcp`, library database copied, fetched PDFs in `/home/yugma/papers` (private). The `.env` and the tunnel credential were copied by the user; never print them.
- The connector still has to be signed in once in this gaint session: the user runs `/mcp`. Until then agents fall back to web tools (the prompts already say how).

## 7. Open with the user (ask in one batch in the morning)
- U1 train on UCF-EL / MultiSolSegment (no licence stated) for the thesis and a no-redistribution "extra data" track? U2 must the final model be commercially usable by WattCycle? U3 download ELPVPower for a last-week severity check? U4 AI-assisted labelling of about 24 pool half-cut + scuff cells (accept / delete / extend, 2 to 3 h), development reads only: the critic's one case where labelling looks truly needed. U5 PVEL-AD signed form: send or leave parked? U6 no gated weights needed now. U7 if cv02 fills up again, may table rows run on gaint?
- The cv02 lane rule question from 13 Nov (allow a run on a GPU where another user holds a small stable amount) is moot while cv02 is free; keep the 4 GB rule.
- First account on gaint: `claude-nb`, then `/login`, after its weekly reset (16 Nov 05:30).
- The user should run `/mcp` once in the gaint session to sign the Research MCP connector in.

## 8. Things that bit today
- Usage: one 5-hour window carries roughly 6 to 8 M Opus subagent tokens; four family teams at once used 1.8 M in 20 minutes. Run two heavy agents at a time.
- Workflow scripts can only be loaded from the working directory (`log/*.js`), not from the session's own scripts folder.
- A workflow agent sometimes sees the user's latest chat message and takes it for its task; the prompts in `log/workflow_T2_family_teams.js` carry a line that prevents it. Reuse it.
- `bench_gpumem.sh` and `bench_guard.sh` stop after 24 h by default (integrator's finding, BUILD_LOG 23:53); long queues need `MAXH`.
