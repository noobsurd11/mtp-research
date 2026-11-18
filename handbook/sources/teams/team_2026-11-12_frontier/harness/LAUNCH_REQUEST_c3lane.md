# Launch request c3lane: cv02 lane rule v2 (shared GPUs), rescue tool for waiting dumps, handover c3all2 -> c3all3 (builder, 17 Nov 2026)

Status: files built and tested on gaint CPU. **Nothing launched, nothing written on cv02, no commit, no push, no deployed dir touched.** E = measured by my own command today, S = judgement. Built to the lead's rulings R1 to R10 (logged 13:24); section 6 names the points I would raise. **Fix round 1 (review notes N1 and N2, lead's message of 14:32): section 9; sections 1, 2, 3 (step 2), 5, 7 and 8 are updated to it.**
Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/c3lane, SW = T/harness/c3swad. B = cv02 /tmp/noob_el/bench_89b9ea5 (training and dump code, unchanged). Old QC = /tmp/noob_el/bench_5437778 (queue code of c3all2). QC = the new deploy (not there yet). cv02 was only read (`ssh -n -a -o BatchMode=yes`).

## 1. What changes
- One patch on 5437778, `H/c3lane.patch`: `bench/q/cv02/cq.sh` (5222150b -> 14d33b80; `diff`: 9 lines of 5222150b replaced, 60 new lines, 247 -> 298 lines) and the new `bench/q/cv02/cq_rescue.sh` (204f9bce, 174 lines). No training, dump, card, data or read code. Rendered training and dump commands are unchanged (E: section 5).
- The strict lane code is untouched: from `# ---- lanes` to `logger_ok` the file equals 5222150b (E, check script). The new code is one block after it, one line in the dump wait, the lane search of the main loop (8 lines), one clause in the armed line.
- Without the files `SHARE_TRAIN` / `SHARE_DUMP` in the queue dir the queue behaves as 5222150b (E: the c3swad chain test still 34 of 34; same jobs under 5222150b and the new script give equal logs, RUN.md5 and calls).

## 2. The rule (as built; lead's R1 to R5)
- R1. At every look the strict rule is tried first on every GPU (no other user above 4,096 MiB in sum). Only if no GPU passes it is a shared lane looked for.
- R2. Shared TRAINING start on GPU g needs all of: `SHARE_TRAIN` on; free memory on g >= SHARE_TRAIN at two looks at g that are at least 30 s and at most 120 s apart, each timed at the look itself, with no failed look at g between them and no pass of the main loop without a shared look between them (HOLD, MAXC full, logger gone, a strict lane found, a start; fix round 1, section 9); no owner above 4,096 MiB is our own login (cv02), the bucket "unknown", or one with unreadable memory; fewer than LPG of our runs on g; free >= the job's gate. Among such GPUs the one with most free memory.
- R3. Shared DUMP on the run's GPU: `SHARE_DUMP` on; free >= SHARE_DUMP and >= the dump gate; any readable owner, our own login included; an unknown owner or unreadable memory blocks. A `--fixture` job (no training; the dump dry test) takes its lane by this rule.
- R4. The floors are read live from `Q/SHARE_TRAIN` and `Q/SHARE_DUMP` (MiB) at every look. Absent, empty, not a plain number, or below the user's floor (20480 / 10240) = off = the strict rule alone. The armed line ends with `sharing (live files in <Q>; 0 = off): SHARE_TRAIN <n> MiB, SHARE_DUMP <n> MiB`. **Switch off at once: remove the file.**
- R5. Log lines, all new, the old ones unchanged:
  - `SHARED start <name> on GPU g: beside <owner:MiB(pids)> ; free <f> MiB >= SHARE_TRAIN <floor> at two looks <s> s apart`, directly before the usual `start <name> on GPU g (card ...` line. `<s>` is the real distance between the two looks in whole seconds (30 to 120). Count shared starts with `grep -c '] SHARED start '`.
  - `SHARED dump <dump job> on GPU g: beside ...; free <f> MiB >= SHARE_DUMP <floor>`, directly before the usual `start dump_...` line.
  - `lane GPU g: shared candidate, first look (...)` and `lane GPU g: shared candidate lost`.
  - `lane GPU g: shared candidate, the earlier look is <s> s old (more than 120 s): it does not count`, followed by a new `first look` line (fix round 1).
- R10. No auto-stop guard for shared GPUs is built.

## 3. Rescue tool `cq_rescue.sh` (lead's R7; runs on cv02 in tmux from QC; started by `H/c3lane_rescue.sh`)
Per run, in this order; any failure is one line `RESCUE REFUSED <run>: ...` (nothing changed) or `RESCUE FAILED <run>: ...`, then it stops:
0. Refuses unless: 9-field job line with one rendered dump line; training rc 0 and a `step 20000/20000` line; no `.end`, no RUN.md5, no runs dir, no slim.pth, no dump folder; no HOLD in the old queue; the old deploy checks; the chain subshell (PID from `pids/subshells.txt`) is alive, a child of the queue's main process (ps), both running that queue's cq.sh; and the tool's file list reproduces the RUN.md5 of a finished sibling run of that queue. **A run with further readouts (a 10-field swad line) is refused** (its chain makes two dumps and a slim with `--keys`).
1. (a, b) Sets HOLD in the old queue dir, waits 20 s. If the old chain started the dump in that moment: removes the HOLD, waits for the old chain to finish, starts no dump. Else: SIGTERM to the verified chain PID only, confirms it is gone, writes `pids/<run>.rescued`, removes the HOLD.
2. (c) Waits for a lane: first a strict pass over the candidates (the run's own GPU, then the other GPUs of the same model); only if none passes it, a pass by R3 in the same order, with the floor from the rescue dir's `SHARE_DUMP` (fix round 1). Honours HOLD in the rescue dir and in the old queue dir.
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
- `c3lane_test.sh`, sandbox with stub python, nvidia-smi and ps: **75 of 75** after fix round 1 (`c3lane_test_fix1.out`; the reviewed version: 65 of 65, `c3lane_test.out`). The 65 reviewed checks are unchanged in text and pass; 10 are new (section 9).
  - A: the reviewed c3swad chain test on the new tree: 34 of 34 (`chain_test_new_tree.out`).
  - B: sharing off, cq 5222150b against the new cq, one plain and one swad job: log lines, RUN.md5, stub calls and rendered commands equal; the only difference is the clause of the armed line.
  - C, training: free 20479 (no start); at the floor at one look only (candidate seen, lost, no start); at two looks (SHARED start, 30 s or more after the first look, usual start line unchanged); own-login owner, unknown owner, unreadable memory (no start); LPG full (second job does not start); gate not met; a strict lane beside a shared one, and one that appears between the looks (strict taken); three candidates (most free taken); file removed between the looks; value below the user's floor; value not a plain number; no files.
  - C, dump: 10239 waits, 10240 runs with the marker; unknown owner waits and runs strictly when it is gone; SHARE_DUMP 10239 = off; a `--fixture` job takes its lane by the dump rule.
  - D, rescue: 17 refusals, each one line with the old chain untouched (unknown run, not trained, rc 1, no final-step line, `.end`, runs dir, slim.pth, dump folder, HOLD, chain not a child, chain dead, main dead, no sibling, sibling list differs, no rescue dir, lock held, 10-field swad line); a rescue on the own GPU by the shared rule (one dump, command byte-equal to the rendered line, slim by the old tool, RUN.md5 in the sibling's form, the old chain's usual log lines, markers, pid files); HOLD in the rescue dir honoured, then the dump on another GPU of the same model by the strict rule; a queue that ran with its queue code in a QC dir (as c3all2); the race (the old chain starts the dump during the 20 s: the tool starts none and reports it). Fix round 1: own GPU passes only the shared rule, GPU 0 of the same model is strictly free: GPU 0 is taken, no SHARED line; a strictly free GPU of another model is no candidate.
  - U (fix round 1), unit test of the real `share_pick` cut out of the new cq.sh: the reviewer's retry case, the 120 s bound, a failed look between two qualifying looks.
  - C (fix round 1): HOLD, and MAXC full, between the two looks.
- File list (R7 required test), `drylist_gaint.out`, `drylist_cv02.out`: on cv02 every dump folder of a finished run has been removed after its relay (E: 0 folders), so the list cannot be rebuilt from disk there. Done instead: (1) on gaint, on the relayed copies with all files, the tool's list equals RUN.md5 byte for byte for c3_pf_v11_f2_s7, c3_house_v11_f4_s6, c3h_hrnet_w18_unetpp_pf_f0_s7, r2_segformer_mitb2_pf_f3_s6, r2_skr01_pf_v11_f0_s6; (2) on cv02, read only, with cv02's own locale: the three fixed paths and the order of the dump paths equal RUN.md5 for the same five runs. Two negative cases (two lines swapped; one file missing) give a diff. The tool makes the same check on a sibling before it writes anything.
- `c3lane_handover_test.sh`, fake cv02 tree (method of the c3swad fix round): **10 of 10** (`handover_test.out`): freeze by rename with a waiting fixture queue; build = the 61 not-started lines of c3all2, byte-equal, order PF, swad, HRNet, HOUSE; place with SHARE_TRAIN 20480 and SHARE_DUMP 10240; all pre-checks of arm incl. the pins of cq_rescue.sh; armed with the floors named; a floor below the user's, a missing floor file, or a changed cq_rescue.sh in QC: REFUSED; armed line without floors: WARNING. Again 10 of 10 with the new patch and pins (`handover_test_fix1.out`).
- pytest on the patched tree (`test_bench_cq_readouts.py`, `test_bench_cq_cv5v3.py`): 20 passed. Reviewed lane test `test_other_on.sh`: 13 of 13, output equal to 5222150b's. Both again on the tree of fix round 1: 20 passed; 13 of 13, output byte-equal to `lanetest_new.out`.
- `c3lane_commit.sh` on a scratch repository: wrong patch md5 refused; commit with 2 files; second run refused. Patch on a fresh archive of 5437778 = my tested tree (`diff -r` empty). Again with the new patch and pins (`commit_fix1.out`).
- Dry runs against the real cv02, read only (`dry_cv02.out`): check script 13 OK, 0 FAIL, 2 SKIP; rescue wrapper (`list` shows the four open lanes, three of them finished runs with verified chains); dump test; handover preview. After fix round 1 only the check script was run again (14:47 IST: 13 OK, 0 FAIL, 2 SKIP, `check_fix1.out`).

## 6. Points I would raise (built as ruled; none changed)
- N1 (R7 order). The tool stops the old chain first and then waits for a lane, as ruled. If no lane comes, the run depends on the tool's tmux session instead of the old chain. A tool that was ended can be run again (it goes on from `pids/<run>.rescued`; this path is not tested). The other order (find a lane, then stop the chain) would leave the old chain in place while nothing qualifies. Not built.
- N2 (rows2). The chain of r2_segformer_mitb2_pf_f4_s6 is the last live part of rows2. When it is stopped, rows2's main process ends and writes `BENCH CV02 Q ALL DONE` with 29 dumps, before the rescued dump (E in the sandbox). Its gpumem logger stops 60 s later. The rows2 relay (N 30, 29 relayed, alive) may see the end line with all present RUN.md5 relayed and end; step 8 starts it again (it skips relayed runs).
- N3 (HOLD for 20 s). The tool sets HOLD in the old queue dir for 20 s to close the race of R7 (b). Other waiting chains of that queue log one `waits: HOLD` line. A tick in that window sees one HOLD file; `arm` of the handover would refuse during it.
- N4 (R4). The armed line shows the floors at arming. A later change of a SHARE file is not logged by the queue; `cat` shows it, and each SHARED line names the floor used.
- N5 (R9). The dry test's default GPU list is the GPUs with no open lane of our queues (13:54: 1, 3, 4, 6; GPU 1 had 26 GB free). `ANYGPU=1` at `arm` passes all eight (R3 allows a dump beside our own login).
- N6 (R2, both floors). With the present free memory (13:54 IST, GB per GPU 0 to 7: 21.2, 25.6, 5.7, 2.9, 2.9, 0.1, 2.4, 6.7) only GPUs 0 and 1 pass 20 GB; whether a second training run fits beside the other user there later is not guarded (R10).

## 7. Not tested
- Anything on a real cv02 GPU: the shared start and dump, the rescue of a real run, the dump dry test under the new QC.
- The rescue tool: the resume path; a failed BENCH_START check; rows2's older queue code was read and its dump chain is byte-equal to 89b9ea5's, but no sandbox queue ran that file.
- The cv02-writing steps of the wrapper scripts: dry-run and fake tree only. `render` was not run in the fake tree.
- How the other users' memory moves in the 30 s between the two looks and after a shared start.

## 8. Files (H; md5)
`md5sum` at 14:49 IST, 17 Nov, after fix round 1. The reviewed versions (md5 of the review's table) are kept read-only in `H/reviewed_r1/`, the two reviewed patched files in `H/reviewed_r1/patched/`.
| File | md5 |
|---|---|
| c3lane.patch | 6262e355da16c5fceaeeeca0fd07de68 |
| c3lane_commit.sh | 51beca9c2ff057ea6bfd9fb69b0e63dc |
| c3lane_rescue.sh | 89fc00d8f41237c9d07cf21aa4a2075e |
| c3lane_handover.sh | 36450f6e4d32d2f97a3d8030790b748f |
| c3lane_dumptest.sh | 9dc30d14b57e3208add5ab5df9ae7828 (unchanged) |
| c3lane_check.sh | 3b55d21d38c5888b40cbfd336eaa25d1 |
| c3lane_test.sh | 2a53aa7d818cec028c4520ffb45973cd |
| c3lane_handover_test.sh | def3b2958890657dcb6b61a914561020 (unchanged) |
| fix1.diff | 126cd4ab1b7c074a6f14d1f405f6dc6c |
| fix1_harness.diff | 310f6ee4deb452296a742a6ee104f882 |
| evidence/c3lane_test_fix1.out | 6b084916654bbff1e6cf43596f8a7b32 |
| evidence/c3lane_test_fix1_on_reviewed_tree.out | 30a88083411134e030e7f288d249de1a |
| evidence/unit_fix1.out | 5b8d139d5b0fffb40cb980367114b870 |
| evidence/chain_test_new_tree_fix1.out | 51e6b0608fc624a29d33f2640c5f83e6 |
| evidence/handover_test_fix1.out | e44f787bf3f60aa08354d2342d73f5e3 |
| evidence/check_fix1.out | 8b6861b230d95729980d8689a0cdc18a |
| evidence/commit_fix1.out | 0c2ed4c148b3d25055cefcac9983c572 |
| evidence/c3lane_test.out | a8ad372c2d432d34aa7cb7ddfbeedd51 (of the reviewed version, unchanged) |
| evidence/chain_test_new_tree.out | 2e985f64a7d9e48e58d207606ca661ac (of the reviewed version, unchanged) |
| evidence/handover_test.out | a5f4845d764a15fd86c8decda99d2893 (of the reviewed version, unchanged) |
| evidence/drylist_gaint.out | e92867154d6f442e64957da21ab1919c (of the reviewed version, unchanged) |
| evidence/drylist_cv02.out | c0e4735ec033b7ebc2531ba1d3e168e8 (of the reviewed version, unchanged) |
| evidence/lanetest_new.out | 9eb7673eedd6b7ae1948031050f14bd0 (of the reviewed version, unchanged) |
| evidence/dry_cv02.out | 46b98816ee36507977e89ffd43017410 (of the reviewed version, unchanged) |
| reviewed_r1/REVIEWED.md5 | 9a0a5bdfa28b064a95f6af2c8c46d117 |
Inside the patch: bench/q/cv02/cq.sh 14d33b80b17b116ec68941f1b40c5951 (reviewed 4fc8d2c0f87c77b099e06164e6b513ea; 5437778 has 5222150ba40130d41a04af4f7d17dbfa), bench/q/cv02/cq_rescue.sh 204f9bce070e695df63de779becce287 (reviewed 8710a7321e060a68e49823f94f3a2b06; new file). Both new values are pinned in c3lane_commit.sh, c3lane_handover.sh, c3lane_rescue.sh and c3lane_check.sh; no old value is left in them (E: grep).
Reused unchanged from SW: c3swad_make_jobs.py c8748ae6, diskguard3.sh 92794405, c3swad_dumptest.sh 24281092 (step 5), c3swad_chain_test.sh cdb661c9 (part A of the test).
c3lane_handover.sh = SW/c3swad_handover.sh 0bb63159 with 50 differing lines; c3lane_dumptest.sh = SW/c3swad_dumptest.sh 24281092 with 18 differing lines (both listed in their headers; `diff` shows them).
Tests can be run again: `OLD=<archive of 89b9ea5> BASE=<archive of 5437778> NEW=<BASE + patch> bash H/c3lane_test.sh <new dir>` (about 3 minutes); `bash H/c3lane_handover_test.sh <new dir>`.

## 9. Fix round 1 (review notes N1 and N2; lead's message of 14:32; written 14:49 IST, 17 Nov)
Changed: in `cq.sh` the function `share_pick` with its comment, 6 lines of the main loop and one sentence of the header; in `cq_rescue.sh` 3 lines of the lane wait and one comment line; the pins in the four scripts; `c3lane_test.sh`. `H/fix1.diff` = the two patched files against the reviewed ones (46 changed lines). `H/fix1_harness.diff` = the five changed harness scripts against `H/reviewed_r1/` (72 changed lines). Not changed: `c3lane_dumptest.sh`, `c3lane_handover_test.sh`, every other line of the patched files; the strict lane code still equals 5222150b (E: check script). Review notes N3 to N7: nothing built, as ruled.

**FIX 1 (N1) as built.**
- (a) The time of a look is taken when `share_ok` for that GPU returns, in ms (`date +%s%3N`; works on cv02, E). `SH1[g]` holds the time of the earlier qualifying look at g. A start needs the present look at g to be 30.000 s or more after it.
- (b) Both rules are built, because each covers a case the other misses. (1) The main loop clears the times of all GPUs at every pass that makes no shared look: HOLD, logger gone, MAXC full, a strict lane found; and at every start, strict or shared, so the wait in the live checks carries no time over. (2) The bound of the review: an earlier look more than 120 s old does not count; the present look is then a first look again, with its own log line. The bound covers a pause that no branch sees (a stopped process, a very slow scan). The clears cover a HOLD or MAXC window shorter than 120 s, which the bound alone lets through. 120 s is a constant (two polls at POLL 60), not a multiple of POLL.
- The guarantee: a shared training start happens only if the same GPU qualified at two real looks 30 to 120 s apart, with no failed look at that GPU between them and no pass without a shared look between them.
- (c) The `SHARED start` line states that distance in whole seconds.
- S, the retry path (start gap not free, a look every 10 s): the distance to the earlier look grows there. The gap is 120 s from our last start and the times are cleared at that start, so the gap opens before the distance passes 120 s. If the bound did trip, the cost is one further wait of 30 s.
- By design, not a fault: a HOLD or MAXC window that begins and ends inside the 30 s sleep between two looks is never seen by the loop. The two looks are then still two real looks 30 s apart.

**FIX 2 (N2) as built.** The tool makes the candidate list once per pass (own GPU, then the other GPUs of the same model), tries the strict rule on all of them, and only if none passes tries the shared-dump rule on them in the same order.

**Tests (E).** `c3lane_test.sh`: 75 of 75 (`c3lane_test_fix1.out`). New checks:
| Check | Case | Result |
|---|---|---|
| U1 (2 checks) | The reviewer's unit case with the real `share_pick`: pass 1 slow, GPU 1 looked at 20 s after the start of the pass; pass 2 starts 30 s after pass 1. Real distance of the two looks 10 s. | No start. Third look 31 s after the first: start, line says `31 s apart`. |
| U2 | Earlier look 125 s old, nothing cleared it. | `the earlier look is 125 s old (more than 120 s): it does not count`, first look, no start. |
| U3 | Earlier look 119 s old. | Start, `119 s apart`. |
| U4 | A failed look between two qualifying looks. | `candidate lost`, then a first look, no start. |
| U ran | The unit script ended with rc 0 and 8 looks. | |
| C h1 | HOLD set at 15 s, removed at 45 s; the second look would have come at 31 s. | No start at the first look after the HOLD (a second `first look` line); start 30 s later, `30 s apart`. |
| C m1 | MAXC 0 from 15 s to 45 s. | Same. |
| D rl | Own GPU 1 passes only the shared rule (15,000 MiB free beside alice); GPU 0, same model, strictly free. | Dump on GPU 0, no `SHARED dump` line, RUN.md5 checks. |
| D rb, GPU 0 | GPU 0 strictly free but another model. | Not a candidate; dump on the own GPU 1, shared. |
- Control (`c3lane_test_fix1_on_reviewed_tree.out`): the same test file on the reviewed tree gives 67 of 75. The 8 failures are rl, h1, m1 and five checks of U. There U1 gives `at two looks 30 s apart` at a real distance of 10 s, and h1 starts at the first look after the HOLD with `46 s apart`: both findings of N1 reproduced. U2 to U4 write the stored time in ms, so their failure on the reviewed code (which counts in s) proves nothing.
- One setting changed in two reviewed cases, their checks unchanged: in rqa and rqe GPU 0 now reports another GPU model. Without that the fixed tool would take the strictly free GPU 0 there, and the checks "shared on its own GPU 1" would no longer describe the case. rqf is rqa's setting with GPU 0 of the same model.
- Also again: part A 34 of 34 (`chain_test_new_tree_fix1.out`); handover test 10 of 10; pytest 20 passed; lane test 13 of 13, byte-equal output; commit script on a scratch clone (wrong patch md5 refused, commit with 2 files, second run refused; the clone needed a test identity, the real worktree has user.name and user.email, E); check script 13 OK, 0 FAIL, 2 SKIP.
- No test process was left behind (E: `ps`, 0 `sleep 1800`, 0 processes of the work dirs).

**Not tested in this round.**
- The clears in the logger branch and after a strict lane was found: read only. They are the same statement `SH1=()` as in the tested HOLD and MAXC branches. The clear at a start is used in every sandbox queue but no check looks at it alone.
- The bound with real elapsed time: U2 and U3 set the stored time back by 125 s and 119 s; no test waits 120 s.
- The rescue tool with more than two candidate GPUs.
- The new pin in `c3lane_rescue.sh` against a deployed QC (there is none yet): `bash -n` only. The pins in `c3lane_handover.sh`: fake tree. The pins in `c3lane_check.sh` and `c3lane_commit.sh`: run for real on gaint (patch item OK, scratch clone).
- The dry runs against cv02 other than the check script were not repeated; those scripts changed only in the pin values.
- Anything on a real cv02 GPU, as before.

Left as they were, on purpose: the fake armed line in `c3lane_handover_test.sh` still prints `cq 4fc8d2c0` (a text of the stub, compared with nothing); the commit message in `c3lane_commit.sh` still says "at two looks 30 s apart".
