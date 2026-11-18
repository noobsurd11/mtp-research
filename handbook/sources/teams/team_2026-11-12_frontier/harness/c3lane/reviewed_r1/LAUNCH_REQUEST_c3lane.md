# Launch request c3lane: cv02 lane rule v2 (shared GPUs), rescue tool for waiting dumps, handover c3all2 -> c3all3 (builder, 17 Nov 2026)

Status: files built and tested on gaint CPU. **Nothing launched, nothing written on cv02, no commit, no push, no deployed dir touched.** E = measured by my own command today, S = judgement. Built to the lead's rulings R1 to R10 (logged 13:24); section 6 names the points I would raise.
Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/c3lane, SW = T/harness/c3swad. B = cv02 /tmp/noob_el/bench_89b9ea5 (training and dump code, unchanged). Old QC = /tmp/noob_el/bench_5437778 (queue code of c3all2). QC = the new deploy (not there yet). cv02 was only read (`ssh -n -a -o BatchMode=yes`).

## 1. What changes
- One patch on 5437778, `H/c3lane.patch`: `bench/q/cv02/cq.sh` (5222150b -> 4fc8d2c0; 5 lines changed, 49 added) and the new `bench/q/cv02/cq_rescue.sh` (8710a732). No training, dump, card, data or read code. Rendered training and dump commands are unchanged (E: section 5).
- The strict lane code is untouched: from `# ---- lanes` to `logger_ok` the file equals 5222150b (E, check script). The new code is one block after it, one line in the dump wait, three in the main loop, one clause in the armed line.
- Without the files `SHARE_TRAIN` / `SHARE_DUMP` in the queue dir the queue behaves as 5222150b (E: the c3swad chain test still 34 of 34; same jobs under 5222150b and the new script give equal logs, RUN.md5 and calls).

## 2. The rule (as built; lead's R1 to R5)
- R1. At every look the strict rule is tried first on every GPU (no other user above 4,096 MiB in sum). Only if no GPU passes it is a shared lane looked for.
- R2. Shared TRAINING start on GPU g needs all of: `SHARE_TRAIN` on; free memory on g >= SHARE_TRAIN at a look that is at least 30 s after the first of an unbroken series of qualifying looks (so at two consecutive looks at least 30 s apart); no owner above 4,096 MiB is our own login (cv02), the bucket "unknown", or one with unreadable memory; fewer than LPG of our runs on g; free >= the job's gate. Among such GPUs the one with most free memory.
- R3. Shared DUMP on the run's GPU: `SHARE_DUMP` on; free >= SHARE_DUMP and >= the dump gate; any readable owner, our own login included; an unknown owner or unreadable memory blocks. A `--fixture` job (no training; the dump dry test) takes its lane by this rule.
- R4. The floors are read live from `Q/SHARE_TRAIN` and `Q/SHARE_DUMP` (MiB) at every look. Absent, empty, not a plain number, or below the user's floor (20480 / 10240) = off = the strict rule alone. The armed line ends with `sharing (live files in <Q>; 0 = off): SHARE_TRAIN <n> MiB, SHARE_DUMP <n> MiB`. **Switch off at once: remove the file.**
- R5. Log lines, all new, the old ones unchanged:
  - `SHARED start <name> on GPU g: beside <owner:MiB(pids)> ; free <f> MiB >= SHARE_TRAIN <floor> at two looks <s> s apart`, directly before the usual `start <name> on GPU g (card ...` line. Count shared starts with `grep -c '] SHARED start '`.
  - `SHARED dump <dump job> on GPU g: beside ...; free <f> MiB >= SHARE_DUMP <floor>`, directly before the usual `start dump_...` line.
  - `lane GPU g: shared candidate, first look (...)` and `lane GPU g: shared candidate lost`.
- R10. No auto-stop guard for shared GPUs is built.

## 3. Rescue tool `cq_rescue.sh` (lead's R7; runs on cv02 in tmux from QC; started by `H/c3lane_rescue.sh`)
Per run, in this order; any failure is one line `RESCUE REFUSED <run>: ...` (nothing changed) or `RESCUE FAILED <run>: ...`, then it stops:
0. Refuses unless: 9-field job line with one rendered dump line; training rc 0 and a `step 20000/20000` line; no `.end`, no RUN.md5, no runs dir, no slim.pth, no dump folder; no HOLD in the old queue; the old deploy checks; the chain subshell (PID from `pids/subshells.txt`) is alive, a child of the queue's main process (ps), both running that queue's cq.sh; and the tool's file list reproduces the RUN.md5 of a finished sibling run of that queue. **A run with further readouts (a 10-field swad line) is refused** (its chain makes two dumps and a slim with `--keys`).
1. (a, b) Sets HOLD in the old queue dir, waits 20 s. If the old chain started the dump in that moment: removes the HOLD, waits for the old chain to finish, starts no dump. Else: SIGTERM to the verified chain PID only, confirms it is gone, writes `pids/<run>.rescued`, removes the HOLD.
2. (c) Waits for a lane: the run's own GPU first, then other GPUs of the same model; strict rule, else R3 with the floor from the rescue dir's `SHARE_DUMP`. Honours HOLD in the rescue dir and in the old queue dir.
3. (d) Runs the dump command byte for byte as the old queue rendered it (from its `jobs_rendered.txt`), in the old queue's B, with the environment of cq.sh / start_py, the same pid, cmdline, rc and stdout files, the same BENCH_START check.
4. (e) Slim checkpoint with the old queue's own slim_ckpt.py (its B, or its QC if its armed line names one, as for c3all2); RUN.md5 in the old form, by rename.
5. (f, g) The old queue's usual lines go into its launch.log (`start dump_`, `pid`, `startup line OK`, `dumped ... rc=0`, `RUN.md5 <run> rc=0: N files`), with `RESCUE <run>: ...` marker lines; then `pids/<run>.end`.

## 4. Launch steps for the lead (all on gaint; write H and SW out in full). Order: rescue, dry test, handover
| # | Command | Stop path |
|---|---|---|
| 1 | Review of this request and of `c3lane.patch`. | |
| 2 | `PATCH_MD5=<md5 of the reviewed patch> bash H/c3lane_commit.sh` : one commit on bench_c3s in /home/noob/work/bench_wt_c3s; prints X. | Before the commit it refuses and says why. If it fails after applying: the two undo commands are in its header. |
| 3 | `bash T/harness/c3base/c3_deploy.sh <X>` : QC = /tmp/noob_el/bench_<X7>. | Refuses if the dir exists. A deploy dir nobody uses is harmless. |
| 4 | `QC=<QC> bash H/c3lane_check.sh` (today without QC: 13 OK, 0 FAIL, 2 SKIP). | Read only. |
| 5 | Old dry test away: `QC=/tmp/noob_el/bench_5437778 bash SW/c3swad_dumptest.sh stop`, then the same with `clean`. | `stop` ends nothing if the fixture took a lane. `DRY=1` prints only. |
| 6 | `QC=<QC> bash H/c3lane_rescue.sh prep` ; `... list` (must print `LIST OK` for one finished run of c3all, c3all2 if it has one, rows2; and the waiting runs with `alive-child-of-main`). | `prep` only makes the rescue dir. |
| 7 | `QC=<QC> bash H/c3lane_rescue.sh run c3all c3_pf_v11_f3_s7 c3h_hrnet_w18_unetpp_pf_f1_s7` ; `... look` until both print `RESCUE <run>: done`. | `... hold` (no dump starts; a running dump goes on); remove `c3rescue/SHARE_DUMP` = strict rule only. A tool that waits can be ended with its session `bench_rescue_c3all`; a later `run` goes on from `pids/<run>.rescued`. |
| 8 | `QC=<QC> bash H/c3lane_rescue.sh run rows2 r2_segformer_mitb2_pf_f4_s6` ; `look`. Then, if `tmux has-session -t =bench_relay_rows2` fails: `tmux new-session -d -s bench_relay_rows2 "B=/tmp/noob_el/bench_b12fca8 Q=/tmp/noob_el/bench_q/rows2 RD=/home/noob/work/bench_relay/rows2 N=30 NAMES_RX=^r2_ POLL=300 bash /home/noob/work/bench_rows2_io/stage/bench_b12fca8/bench/q/cv02/relay_w1c.sh"` (see section 6, N2). | as 7 |
| 9 | New dry test: `QC=<QC> bash H/c3lane_dumptest.sh place` ; `arm` ; `look`. Expected: `SHARED lane (fixture) dumptest_c3s_swad_f0 on GPU g`, `SHARED dump dump_dumptest_c3s_swad_f0 ...`, both `dumped ... rc=0`, `RUN.md5 dumptest_c3s_swad_f0 rc=0: 220 files`. Then `clean`. | `stop` (only if the fixture has no lane), `clean`; remove `c3lane_smoke/SHARE_DUMP` = strict only. |
| 10 | Handover: `bash H/c3lane_handover.sh freeze` ; wait 180 s ; `bash H/c3lane_handover.sh build` ; `QC=<QC> bash H/c3lane_handover.sh render` ; `bash H/c3lane_handover.sh place` ; `QC=<QC> bash H/c3lane_check.sh` ; `QC=<QC> bash H/c3lane_handover.sh arm`. `guard` is not needed: disk guard 3 runs and names c3all3 (E). | `freeze` refuses, without writing, if another queue could start. After `freeze`, c3all2 stays frozen: if a later step refuses, fix and repeat that step; nothing else has started. After `arm`: `touch /tmp/noob_el/bench_q/c3all3/HOLD`. |
| 11 | Sharing off at any time: `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 'rm /tmp/noob_el/bench_q/c3all3/SHARE_TRAIN'` (training) and/or `.../SHARE_DUMP` (dumps). On again: write 20480 / 10240 back. | |
| 12 | Runs of c3all2 that train at the freeze finish there. If such a dump waits: `QC=<QC> bash H/c3lane_rescue.sh run c3all2 <run>`. | as 7 |
What `arm` prints: `armed bench_q_c3all3 ('cv02 q armed:' line seen; sharing (live files in /tmp/noob_el/bench_q/c3all3; 0 = off): SHARE_TRAIN 20480 MiB, SHARE_DUMP 10240 MiB; ...`. A `WARNING` instead means the queue runs by the strict rule only.
Relays (R8): no change is right. c3base (`^c3_`), c3hrnet (`^c3h_`) and c3swad (`^c3s_`) read B/runs by name, whichever queue trained the run (E: all three alive at 13:54; the c3swad relay names c3all2 only for its end-line test and ends at N 25).

## 5. Tests (E; CPU only; outputs in H/evidence)
- `c3lane_test.sh`, sandbox with stub python, nvidia-smi and ps: **65 of 65** (`c3lane_test.out`).
  - A: the reviewed c3swad chain test on the new tree: 34 of 34 (`chain_test_new_tree.out`).
  - B: sharing off, cq 5222150b against the new cq, one plain and one swad job: log lines, RUN.md5, stub calls and rendered commands equal; the only difference is the clause of the armed line.
  - C, training: free 20479 (no start); at the floor at one look only (candidate seen, lost, no start); at two looks (SHARED start, 30 s or more after the first look, usual start line unchanged); own-login owner, unknown owner, unreadable memory (no start); LPG full (second job does not start); gate not met; a strict lane beside a shared one, and one that appears between the looks (strict taken); three candidates (most free taken); file removed between the looks; value below the user's floor; value not a plain number; no files.
  - C, dump: 10239 waits, 10240 runs with the marker; unknown owner waits and runs strictly when it is gone; SHARE_DUMP 10239 = off; a `--fixture` job takes its lane by the dump rule.
  - D, rescue: 17 refusals, each one line with the old chain untouched (unknown run, not trained, rc 1, no final-step line, `.end`, runs dir, slim.pth, dump folder, HOLD, chain not a child, chain dead, main dead, no sibling, sibling list differs, no rescue dir, lock held, 10-field swad line); a rescue on the own GPU by the shared rule (one dump, command byte-equal to the rendered line, slim by the old tool, RUN.md5 in the sibling's form, the old chain's usual log lines, markers, pid files); HOLD in the rescue dir honoured, then the dump on another GPU of the same model by the strict rule; a queue that ran with its queue code in a QC dir (as c3all2); the race (the old chain starts the dump during the 20 s: the tool starts none and reports it).
- File list (R7 required test), `drylist_gaint.out`, `drylist_cv02.out`: on cv02 every dump folder of a finished run has been removed after its relay (E: 0 folders), so the list cannot be rebuilt from disk there. Done instead: (1) on gaint, on the relayed copies with all files, the tool's list equals RUN.md5 byte for byte for c3_pf_v11_f2_s7, c3_house_v11_f4_s6, c3h_hrnet_w18_unetpp_pf_f0_s7, r2_segformer_mitb2_pf_f3_s6, r2_skr01_pf_v11_f0_s6; (2) on cv02, read only, with cv02's own locale: the three fixed paths and the order of the dump paths equal RUN.md5 for the same five runs. Two negative cases (two lines swapped; one file missing) give a diff. The tool makes the same check on a sibling before it writes anything.
- `c3lane_handover_test.sh`, fake cv02 tree (method of the c3swad fix round): **10 of 10** (`handover_test.out`): freeze by rename with a waiting fixture queue; build = the 61 not-started lines of c3all2, byte-equal, order PF, swad, HRNet, HOUSE; place with SHARE_TRAIN 20480 and SHARE_DUMP 10240; all pre-checks of arm incl. the pins of cq_rescue.sh; armed with the floors named; a floor below the user's, a missing floor file, or a changed cq_rescue.sh in QC: REFUSED; armed line without floors: WARNING.
- pytest on the patched tree (`test_bench_cq_readouts.py`, `test_bench_cq_cv5v3.py`): 20 passed. Reviewed lane test `test_other_on.sh`: 13 of 13, output equal to 5222150b's.
- `c3lane_commit.sh` on a scratch repository: wrong patch md5 refused; commit with 2 files; second run refused. Patch on a fresh archive of 5437778 = my tested tree (`diff -r` empty).
- Dry runs against the real cv02, read only (`dry_cv02.out`): check script 13 OK, 0 FAIL, 2 SKIP; rescue wrapper (`list` shows the four open lanes, three of them finished runs with verified chains); dump test; handover preview.

## 6. Points I would raise (built as ruled; none changed)
- N1 (R7 order). The tool stops the old chain first and then waits for a lane, as ruled. If no lane comes, the run depends on the tool's tmux session instead of the old chain. A tool that was ended can be run again (it goes on from `pids/<run>.rescued`; this path is not tested). The other order (find a lane, then stop the chain) would leave the old chain in place while nothing qualifies. Not built.
- N2 (rows2). The chain of r2_segformer_mitb2_pf_f4_s6 is the last live part of rows2. When it is stopped, rows2's main process ends and writes `BENCH CV02 Q ALL DONE` with 29 dumps, before the rescued dump (E in the sandbox). Its gpumem logger stops 60 s later. The rows2 relay (N 30, 29 relayed, alive) may see the end line with all present RUN.md5 relayed and end; step 8 starts it again (it skips relayed runs).
- N3 (HOLD for 20 s). The tool sets HOLD in the old queue dir for 20 s to close the race of R7 (b). Other waiting chains of that queue log one `waits: HOLD` line. A tick in that window sees one HOLD file; `arm` of the handover would refuse during it.
- N4 (R4). The armed line shows the floors at arming. A later change of a SHARE file is not logged by the queue; `cat` shows it, and each SHARED line names the floor used.
- N5 (R9). The dry test's default GPU list is the GPUs with no open lane of our queues (13:54: 1, 3, 4, 6; GPU 1 had 26 GB free). `ANYGPU=1` at `arm` passes all eight (R3 allows a dump beside our own login).
- N6 (R2, both floors). With the present free memory (13:54 IST, GB per GPU 0 to 7: 21.2, 25.6, 5.7, 2.9, 2.9, 0.1, 2.4, 6.7) only GPUs 0 and 1 pass 20 GB; whether a second training run fits beside the other user there later is not guarded (R10).

## 7. Not tested
- Anything on a real cv02 GPU: the shared start and dump, the rescue of a real run, the dump dry test under the new QC.
- The rescue tool: the resume path; a GPU of another model; a failed BENCH_START check; rows2's older queue code was read and its dump chain is byte-equal to 89b9ea5's, but no sandbox queue ran that file.
- The cv02-writing steps of the wrapper scripts: dry-run and fake tree only. `render` was not run in the fake tree.
- How the other users' memory moves in the 30 s between the two looks and after a shared start.

## 8. Files (H; md5)
`md5sum` at 14:02 IST, 17 Nov.
| File | md5 |
|---|---|
| c3lane.patch | b128ccbc74c2ec38fc5dbc5c64473bf1 |
| c3lane_commit.sh | e6c4a6b792d2c3f30bda77267d8d3dcc |
| c3lane_rescue.sh | 0ddf3839c5000246ca8eac45de7fd1e5 |
| c3lane_handover.sh | 2109f5c7e7204112f05e044d6ae12ead |
| c3lane_dumptest.sh | 9dc30d14b57e3208add5ab5df9ae7828 |
| c3lane_check.sh | d95441fe0cbee4801b6192d8828e10a2 |
| c3lane_test.sh | 6b48b566bca9bcc6260e39076628a952 |
| c3lane_handover_test.sh | def3b2958890657dcb6b61a914561020 |
| evidence/c3lane_test.out | a8ad372c2d432d34aa7cb7ddfbeedd51 |
| evidence/chain_test_new_tree.out | 2e985f64a7d9e48e58d207606ca661ac |
| evidence/handover_test.out | a5f4845d764a15fd86c8decda99d2893 |
| evidence/drylist_gaint.out | e92867154d6f442e64957da21ab1919c |
| evidence/drylist_cv02.out | c0e4735ec033b7ebc2531ba1d3e168e8 |
| evidence/lanetest_new.out | 9eb7673eedd6b7ae1948031050f14bd0 |
| evidence/dry_cv02.out | 46b98816ee36507977e89ffd43017410 |
Inside the patch: bench/q/cv02/cq.sh 4fc8d2c0f87c77b099e06164e6b513ea (was 5222150ba40130d41a04af4f7d17dbfa), bench/q/cv02/cq_rescue.sh 8710a7321e060a68e49823f94f3a2b06 (new). Both values are pinned in c3lane_commit.sh, c3lane_handover.sh, c3lane_rescue.sh and c3lane_check.sh.
Reused unchanged from SW: c3swad_make_jobs.py c8748ae6, diskguard3.sh 92794405, c3swad_dumptest.sh 24281092 (step 5), c3swad_chain_test.sh cdb661c9 (part A of the test).
c3lane_handover.sh = SW/c3swad_handover.sh 0bb63159 with 50 differing lines; c3lane_dumptest.sh = SW/c3swad_dumptest.sh 24281092 with 18 differing lines (both listed in their headers; `diff` shows them).
Tests can be run again: `OLD=<archive of 89b9ea5> BASE=<archive of 5437778> NEW=<BASE + patch> bash H/c3lane_test.sh <new dir>` (about 3 minutes); `bash H/c3lane_handover_test.sh <new dir>`.

