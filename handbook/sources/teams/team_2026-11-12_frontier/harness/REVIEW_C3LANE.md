**Verdict, round 2 (17 Nov 2026, 15:02 IST): PASS** for the set in the table "Versions reviewed, round 2" (section "Round 2" at the end; patch 6262e355, the "both rules" form of fix 1, restored on disk at 15:01). N1 and N2 are closed. No blocking finding. N3 to N7 stay as notes, not built, as ruled.

Round 1 verdict (kept below as written): **FIX** (changed at 14:39 IST from the PASS of 14:31, after the test of the stale first look), pinned to the md5s below. **One blocking finding: N1** (ruling R2 is not kept after a pause of the queue; a few lines in cq.sh). Everything else stands as written at 14:31: six notes (N2 to N7), none blocking.

# Review of LAUNCH_REQUEST_c3lane.md and harness/c3lane (reviewer c3swad_reviewer, 17 Nov 2026, written 14:31 IST, N1 rewritten 14:39 IST)

E = measured by my own command today. S = judgement. T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/c3lane.
cv02 was only read (ssh -n -a, BatchMode). Nothing launched, no commit, no push. On gaint I wrote this file and my scratch folder only. Every process my tests started was ended by its recorded PID; none is left (E).
Scratch: /tmp/claude-1003/-home-yugma-mtp/2f42a8b1-e6a3-43d3-94cf-a2e7c1c6c653/scratchpad/lane

## Versions reviewed (unchanged on disk at 14:29, E)
| File | md5 |
|---|---|
| harness/LAUNCH_REQUEST_c3lane.md | cab5516cdefbdc39cb14dbd087b94853 |
| c3lane.patch | b128ccbc74c2ec38fc5dbc5c64473bf1 |
| c3lane_commit.sh | e6c4a6b792d2c3f30bda77267d8d3dcc |
| c3lane_rescue.sh | 0ddf3839c5000246ca8eac45de7fd1e5 |
| c3lane_handover.sh | 2109f5c7e7204112f05e044d6ae12ead |
| c3lane_dumptest.sh | 9dc30d14b57e3208add5ab5df9ae7828 |
| c3lane_check.sh | d95441fe0cbee4801b6192d8828e10a2 |
| c3lane_test.sh | 6b48b566bca9bcc6260e39076628a952 |
| c3lane_handover_test.sh | def3b2958890657dcb6b61a914561020 |
| from the patch on a fresh archive of 5437778 (E): bench/q/cv02/cq.sh | 4fc8d2c0f87c77b099e06164e6b513ea |
| bench/q/cv02/cq_rescue.sh | 8710a7321e060a68e49823f94f3a2b06 |

Line numbers below are those of the patched files.

## Blocking

**N1. Ruling R2 ("two consecutive checks at least 30 s apart") is not kept in two cases.** (cq.sh l.124 to l.135 `share_pick`; l.258 and l.260 the HOLD and MAXC branches of the main loop, which make no look; l.270 the only reset besides a failing look, after a shared start)

*Case a, stale first look (the lead's question of 14:32; tested).* The first-look time of a GPU is cleared only by a failing look or by a shared start. The main loop makes no look while HOLD exists, while `lanes_all >= MAXC`, and while it waits in the live checks of a run it has just started (up to 600 s). A strict start does not clear the times either. After such a pause the old time is still there, and one fresh look is enough.
- E (my test, reviewed cq.sh, stub tools): one GPU beside another user, 25,000 MiB free, first look logged. Then HOLD for 135 s. During the HOLD free memory was 5,000 MiB for 120 s (below the floor, never looked at) and back at 25,000 before the HOLD was removed. Result at the first look after the HOLD: `SHARED start ja on GPU 0: ... at two looks 140 s apart`. The same with MAXC 0 in place of HOLD.
- When it happens on cv02: every release of a HOLD (the stop path of step 10, the disk guards), every MAXC window, and a slow live check after a strict start.
- The floor still holds at that one look. What is lost is the second observation: a job of the other user that is between two phases, or restarting, is taken for a stable 20 GB.

*Case b, the 30 s is measured from the start of each pass, not at the look.* `share_pick` takes one time stamp at its start and uses it for every GPU; the look at a later GPU happens some seconds after it. In the normal path a 30 s sleep lies between two passes, so the real distance is at least 30 s. In the retry path (`gap_take` fails, `sleep 10`, next pass) it can be shorter.
- E (unit test with the real `share_pick`, a slow first pass): log line `at two looks 30 s apart`, real distance between the two looks at that GPU 10 s. With cv02's real look time (about 1 s per GPU, E from the c3all log) the shortfall is a few seconds.

*Fix, tested on a scratch copy (20 changed lines in `share_pick`, nothing else):*
1. take the time at the look itself (after `share_ok` returns), for the first look and for every later one;
2. keep per GPU the time of the previous qualifying look; if the present look is more than 120 s after it, the series is broken: log it and treat this look as a first look;
3. clear both times on a failing look and after a shared start, as now.
- Is a bound on the age of the previous look the right fix? Yes (S). It covers every cause of a pause at once (HOLD, MAXC, the live-check wait, a slow nvidia-smi), where clearing the times in the HOLD and MAXC branches would miss the others.
- The value: a constant of 120 s ("two polls" at POLL 60), not a multiple of POLL. The tests run with POLL 2, and the normal distance between two looks at one GPU is 30 s plus the scan (about 40 to 60 s on cv02), so a bound tied to a small POLL would break every series. A HOLD shorter than one poll then still counts as the same series (at most about 100 s between the looks).
- E (scratch copy with this fix, same test): no start at the first look after the pause; `series broken (previous look 140 s ago)`, a new first look, and the shared start 30 s later, after HOLD and after MAXC 0. The builder's own test run against this scratch copy still gives 65 of 65, so the bound breaks none of the existing cases.
- After the fix the changed files need a diff review: the patch (new md5), the pins of cq.sh in c3lane_commit.sh, c3lane_handover.sh, c3lane_rescue.sh and c3lane_check.sh, and a test case for the pause in c3lane_test.sh.

## Notes, most important first (none blocks)

**N2. The rescue tool prefers its own GPU shared over another GPU by the strict rule.** (cq_rescue.sh l.132-134; ruling R1)
- The loop tries per GPU "strict, else shared", own GPU first. If the own GPU passes the shared rule and another GPU of the same model passes the strict rule, the dump runs beside the other user.
- Rare today (a strictly free GPU is taken by the training queue). Allowed by B (10 GB floor holds). Against R1's "a strict lane is always preferred".
- Smallest fix: two passes over the candidate GPUs, strict first.

**N3. If the rescue tool is ended after its dump has started, nothing finishes the run.** (cq_rescue.sh l.104, l.112)
- E (my test Y3): tool ended while the dump ran. Result: dump folder with manifest, no slim.pth, no RUN.md5, no `.end`, no `dumped` line in the old log. A second call says `RESCUE REFUSED rd: a dump folder of the run exists`. The old chain is gone. The run can then only be finished by hand.
- The request and the wrapper say "a tool that waits may be ended". That is right and tested (below). The rule for the lead: **do not end the session `bench_rescue_<queue>` once `start dump_<run>` is in the old launch.log** (about 2 minutes per run). A crash of cv02 in that window has the same effect, as it has for an old chain.
- Smallest fix: let a later call go on from a finished dump (rc file 0, `dumped` line, manifest present) with slim and RUN.md5.

**N4. The tool removes a HOLD in the old queue that someone else set during its 20 s wait.** (cq_rescue.sh l.116, l.117, l.121, l.123, l.126)
- A disk guard cannot set HOLD in that window: its line is `[ ! -e HOLD ] && touch HOLD`, the file is already there, so it does nothing and logs nothing. The tool then removes the file. The guard sets it at its next pass, up to 300 s later.
- A HOLD touched by hand in that window is removed. E (my test Y1d): HOLD touched 3 s into the wait, gone after the tool went on.
- Other exit paths (E, my tests): SIGTERM and SIGHUP during the wait: HOLD removed, chain alive, no `.rescued`. SIGKILL during the wait: **HOLD stays** in the old queue; remove it by hand. Every `no` and `bad` path after the HOLD removes it (code read).
- Smallest fix: note the mtime after the tool's own `touch`; remove the file only if the mtime is unchanged, else leave it and say so.

**N5. A 10-field swad line is refused by the tool** (stated in the request). Today no swad run of c3all2 has started (E 14:14: 2 of 62 started, both PF; eight PF lines come before the first swad line). If c3all2 is frozen after it reaches the swad lines, such a run waits for its two dumps under the strict rule only and cannot be rescued. So: hand over before c3all2 reaches `c3s_swad_v11_f0_s5`. The same holds for a later handover away from c3all3.

**N6. Small points of the tool.**
- After the tool is ended while it sleeps, its lock stays held by the orphaned `sleep` for up to 20 s (wait) or 60 s (lane poll). A new `run` in that time is refused as "a rescue runs" (E).
- If the chain is stopped in the first 30 s after the training ended, before it logged `trained <run> rc=0` and `done <run>`, those two lines never appear in the old launch.log (code read). Counts of "trained" lines are then one short. Fix: refuse unless the `trained <run> rc=0` line is there.
- For a queue with its queue code in a QC dir (c3all2) the tool runs that QC's slim_ckpt.py without checking QC/CODE.md5 (the old chain checked it before every start).
- On another GPU the tool's strict check does not see a training run of the same old queue (it is "ours" there), so the dump can run beside it with only the dump gate checked. No other user above 4 GB is on such a GPU, so at least 35 GB are free. Harmless; not marked SHARED.

**N7. Request wording.** Section 2 and the rulings in log.md number the "no auto-stop guard" ruling differently (R10 against R9). Section 4 step 8: the relay restart must come after `RESCUE ...: done`; started earlier it ends at once again (end line seen, nothing left to relay). The command itself is right (see point 5).

## The attack points

**1. No SHARE file = the old rule: PASS.** E: from `# ---- lanes` to `logger_ok` the patched file is byte-equal to 5222150b. By reading: with no file `share_floor` gives 0, `share_ok` returns before any nvidia-smi call, `share_pick` returns 1 with the old sleep, and the dump wait reduces to the old `! lane_ok`. This holds for training starts, dumps and fixture jobs. E (builder's part B, re-run): one plain and one swad job under 5222150b and under the new script give equal log lines, RUN.md5, stub calls and rendered commands; the only difference is the clause of the armed line. The c3swad chain test on the new tree: 34 of 34.

**2. Shared training start: FIX for the two-looks rule (N1); the rest passes.**
- Floor: `share_floor` returns 0 for an absent, empty, non-numeric, multi-line or below-floor value, and for a number too large for the shell. A value below 20480 cannot reach `share_ok` (code read; E builder cases l2, l4).
- File changed between the looks: removed or lowered below the floor gives "candidate lost", no start (E l1). Raised: the higher value is used at the next look. A start whose last look has passed (a few seconds before the start line) still happens.
- Owners: an owner above 4,096 MiB that is our own login, "unknown", or with unreadable memory blocks (E s4, s5, s6). Owners below 4,096 MiB are not looked at, as in the strict rule.
- LPG and gate are checked (E s7, s8). Strict is tried first at every pass and wins, also when it appears between the looks (E s9, s9b). Most free memory wins (E s10).
- Two training runs of ours on one GPU: I found no order of events that gives it. A c3all2 run in training is our own login above 4,096 MiB: strict fails, shared fails. c3all3's own runs are counted by LPG. The first seconds of another queue's run (below 4,096 MiB) are covered as before by the one-queue rule: freeze, 180 s, started set checked twice and again at `arm` (handover code unchanged there). The rescue tool and the dry test start dumps only.
- What can share a GPU: one training run of ours and a dump of ours (rescue, c3all2 chain, dry test), each under its own floor. Together at most about 12.3 GB.

**3. Shared dump: PASS.** One fresh look before every dump start; strict first, else free >= SHARE_DUMP and >= the dump gate; unknown owner or unreadable memory blocks; our own login is allowed, as ruled (E d1, d2, d3). A fixture job takes its lane by the dump rule at once (E f1). Below-floor or malformed SHARE_DUMP = off.

**4. Rescue tool: PASS, see N2, N3, N4, N6.**
- The PID: taken from the old queue's `pids/subshells.txt` (written at launch), must be alive, a child of the PID in `queue.pid`, and both must show that queue's cq.sh as command line. Checked before the HOLD and again after the wait. Only SIGTERM, only that PID, no second signal.
- Never two dumps: the old chain checks HOLD twice before a dump start; the tool sets HOLD, waits 20 s, and looks for the pid file or the `start dump_` line. E (builder's race test, re-run): the old chain started the dump in the wait; the tool started none and waited for it.
- Resume (untested by the builder): **tested, works.** E (my test Y2): chain stopped, no GPU qualified, tool ended by SIGHUP while it waited: no HOLD anywhere, no dump, no `.end`, `.rescued` present. A lane came, second call: `resume rb`, one dump, shared, command byte-equal to the rendered line, RUN.md5 in the sibling's form and checking, usual log lines once each. The resume path does not need the old main process, so it works for rows2 too.
- Dump command: read from the old queue's `jobs_rendered.txt`, run with cwd = that queue's B and the environment of `start_py` (CUDA_VISIBLE_DEVICES, HF_HUB_OFFLINE, OMP_NUM_THREADS 4, env.sh, the BENCH_ variables of cq.sh). E: the dump and read code reads only BENCH_*, OMP_NUM_THREADS and PYTHONHASHSEED from the environment. For rows2 the tool sets one variable more than rows2's own cq.sh did (BENCH_CV5V3_ROOTS); b12fca8 has no cv5v3 code (S: no effect).
- RUN.md5 form: the tool's list is the old chain's list (three fixed paths, then `find ... | sort`). E on gaint copies with all files: `LIST OK` for c3_pf_v11_f2_s7 (107 paths), c3_house_v11_f4_s6 (115), c3h_hrnet_w18_unetpp_pf_f0_s7 (111), r2_segformer_mitb2_pf_f3_s6 (108). On cv02 the tool checks the order on a finished sibling in its own locale before it changes anything; a different `sort` order would be a refusal.
- Another GPU of the same model: the dump manifest stores the device name only (E, keys of a relayed manifest; no index, no uuid). The read script, `bench_leak_did` and the relay use the name or nothing. The old log gets the line "the run trained on GPU g".

**5. rows2: PASS.** E: `chain_after` of b12fca8's cq.sh is byte-equal to 89b9ea5's (41 lines), so the HOLD checks, the log lines and the RUN.md5 list are the same; bench_lib.sh is the same file in all three trees (1af2ed69). When its last chain is stopped rows2's main process ends with its end line (E, builder's sandbox check, re-run). E: the running rows2 relay has B, Q, RD, N 30, NAMES_RX ^r2_, POLL 300 and the script path exactly as in the restart command of step 8.

**6. Handover: PASS.** The 50 differing lines against 0bb63159 are: names and defaults, the two pins (cq.sh 4fc8d2c0, cq_rescue.sh 8710a732) and the expected QC difference list, `build` also wants c3all at 0, `render` compares every line with c3all2's rendered list, `place` writes SHARE_TRAIN 20480 and SHARE_DUMP 10240, `arm` wants exactly these two values before it starts and warns if the armed line does not show them. The only MAXC write is to c3all2. E: builder's fake-tree test re-run, 10 of 10. E against the real cv02 (DRY, read-only): `freeze` would pass now (`ok c3swad_smoke fixture only`), the build preview carries 60 of 60 lines byte-equal to c3all2's list (29388346), 25 of them 10-field swad lines, order PF, swad, HRNet, HOUSE. c3lane_check.sh real run: 13 OK, 0 FAIL, 2 SKIP. cv02 after my reads: c3all2 MAXC 8, c3all 0, no HOLD, no MAXC.new.

**7. Dry test and step 5: PASS.** The 18 differing lines: queue dir and session name, SHARE_DUMP 10240 in the test dir, ANYGPU. `stop` and `clean` are the reviewed code with the new names. Step 5 uses the reviewed c3swad script on the waiting c3swad_smoke (E: alive, no lane taken), with QC = the running queue-code dir; `clean` removes nothing that CODE.md5 lists and checks it afterwards. With today's memory the new test would run at once on GPU 1 beside ds404_user13 (26 GB free).

**8. Stop paths: PASS.** Removing SHARE_TRAIN or SHARE_DUMP takes effect at the next look (read live at every look). A start between its two looks is lost (E l1). Writing the value back is safe: a half-written file reads as off. `hold` of the wrapper stops dump starts of the tool, not the stop of the old chain. HOLD in c3all3 stops starts and dumps as before.

**9. The tests: PASS.** c3lane_test.sh puts stub nvidia-smi, ps, md5sum and python first in PATH and checks it; it holds no ssh. c3lane_handover_test.sh runs a copy that must hold no ssh call and no /tmp/noob_el path, with a stub tmux. E: re-run in my scratch: 65 of 65 and 10 of 10 (both need the folder c3swad beside c3lane; my first run without it failed for that reason only). `sleep 1800` processes: 0 before, 0 after both tests, 0 after mine.

## Not verified
- Anything on a real cv02 GPU: a shared start, a shared dump, a rescue, the new dry test.
- How another user's job reacts to 5.7 to 8.4 GB more on its GPU, and how its memory moves after our start (no guard, as ruled).
- The cv02-writing steps of the wrappers (rescue `prep` and `run`, handover, dump test): DRY forms, fake tree and code read only. c3lane_commit.sh: code read only.
- The rescue of a run on a GPU of another model, and a failed BENCH_START check in the tool.

# Round 2

**Verdict, round 2: PASS.** N1 and N2 are closed in the set below. The diff holds nothing but the two fixes, the pins and the tests. No blocking finding.

Written 15:02 IST, 17 Nov 2026. Same rules as round 1. E = measured by my own command, S = judgement.
History of the set (E): I reviewed it from my snapshot of 14:51:26. From 14:53 the builder overwrote it in harness/c3lane with another form of fix 1 (bound only), on a second instruction of the lead. The lead decided for the 14:51 set and restored it at 15:01. At 15:02 I checked the restore: the eleven files below are byte-equal to my snapshot, the 14 evidence files too, `reviewed_r1/REVIEWED.md5` verifies, and `reviewed_r1` equals what I reviewed in round 1. The bound-only files in evidence/superseded_fix1_bound_only are not reviewed and not part of this verdict.

## Versions reviewed, round 2 (on disk at 15:02, E)
| File | md5 | against round 1 |
|---|---|---|
| harness/LAUNCH_REQUEST_c3lane.md | 8c2a366ead5bdef4bebc67685ae20a65 | changed |
| c3lane.patch | 6262e355da16c5fceaeeeca0fd07de68 | changed |
| c3lane_commit.sh | 51beca9c2ff057ea6bfd9fb69b0e63dc | pins only |
| c3lane_rescue.sh | 89fc00d8f41237c9d07cf21aa4a2075e | pins only |
| c3lane_handover.sh | 36450f6e4d32d2f97a3d8030790b748f | pins only (and the header comment that names them) |
| c3lane_check.sh | 3b55d21d38c5888b40cbfd336eaa25d1 | pins only |
| c3lane_test.sh | 2a53aa7d818cec028c4520ffb45973cd | 10 new checks, 2 settings changed |
| c3lane_dumptest.sh | 9dc30d14b57e3208add5ab5df9ae7828 | same |
| c3lane_handover_test.sh | def3b2958890657dcb6b61a914561020 | same |
| fix1.diff | 126cd4ab1b7c074a6f14d1f405f6dc6c | new |
| fix1_harness.diff | 310f6ee4deb452296a742a6ee104f882 | new |
| from the patch on a fresh archive of 5437778 (E): bench/q/cv02/cq.sh | 14d33b80b17b116ec68941f1b40c5951 | changed |
| bench/q/cv02/cq_rescue.sh | 204f9bce070e695df63de779becce287 | changed |

I read my own diff of the two patched files against the round 1 versions, not only fix1.diff (same 46 changed lines).

## 1. N1 (two looks at least 30 s apart): closed
As built (cq.sh l.129 to l.140, l.265 to l.269, l.276):
- the time of a look is taken when `share_ok` returns for that GPU, in ms; a start needs the present look 30 s or more, and 120 s or less, after the first look of the series at that GPU;
- a failed look ends the series of that GPU;
- every pass of the main loop that makes no shared look ends all series: HOLD, logger gone, MAXC full, a strict lane found; so does every start, strict or shared;
- a first look older than 120 s does not count; the present look is then a first look again, with its own log line.

The paths I named in round 1 (E, my tests on the fixed cq.sh, stub tools):
- HOLD release: HOLD for 135 s with 5,000 MiB free during it. No start at the first look after it, a second `first look` line, start 30 s later with `3x s apart`.
- MAXC window: MAXC 0 for 135 s. The same.
- The wait after a start: GPU 1 was a shared candidate, then job jc started on GPU 0 by the strict rule. The next job got a new first look at GPU 1 after that start and started shared 30 s after it.
- Retry path: the builder's unit case U1 is my round 1 case with the real `share_pick`; re-run by me: no start at a real distance of 10 s, start at 31 s, the line states 31 s.
- A HOLD of 30 s between the looks (builder's h1) and MAXC 0 for 30 s (m1): re-run, pass.

Never to start, or to start wrongly (S, with the tests above):
- A start needs two real qualifying looks at the same GPU, 30 to 120 s apart, with no failed look and no pass without a look between them. I found no path around it.
- No dead end: after any clear the next look is a first look and the loop sleeps 30 s, so the second look comes 30 s plus one scan later. In the retry path the distance to the first look grows; if it passes 120 s the series starts again and the start comes about 30 s later. Only an nvidia-smi so slow that one scan takes over 90 s would keep every series from completing; then no shared start is made, which is the safe side.
- A HOLD that begins and ends inside the 30 s sleep is never seen by the loop (E, my test with a HOLD of 8 s: one first look, start 30 s after it). The two looks are then real looks 30 s apart with no skipped pass. That is right.
- With no SHARE file nothing changes: the builder's part B (5222150b against the new script, sharing off) passes in my re-run.
- `date +%s%3N` gives 13 digits on cv02 and the arithmetic works there (E, read-only).

## 2. N2 (rescue tool: strict before shared): closed
cq_rescue.sh l.133 to l.135: the candidate list is built once per pass (own GPU, then GPUs of the same model), the strict rule is tried on all of them, and the shared-dump rule only if none passed, in the same order. E (builder's case rl, re-run): own GPU shareable, GPU 0 of the same model strictly free: the dump runs on GPU 0, no SHARED line. A strictly free GPU of another model is not a candidate (E, new check on rb). My round 1 rescue tests on the new tool: 9 of 9 (resume, HOLD on the exit paths, lock).

## 3. Nothing else in the diff
- cq.sh: one sentence of the header, the constant SHARE_STALE, `share_pick` with its comment, three branches and one line of the lane search in the main loop, the line after the lane is taken. The dump wait, the armed line, the rendering and `chain_after` are unchanged. From `# ---- lanes` to `logger_ok` the file is byte-equal to 5222150b (E).
- cq_rescue.sh: two comment lines and the three lines of the lane wait.
- c3lane_commit.sh, c3lane_rescue.sh, c3lane_handover.sh, c3lane_check.sh: only the two pinned md5s (and their short forms in two texts). No old value is left (E, grep).
- c3lane_dumptest.sh and c3lane_handover_test.sh: unchanged.

## 4. The tests and the two changed settings
- E, re-run in my scratch on the 14:51 set: c3lane_test.sh 75 of 75 on the fixed tree; the same file on the round 1 tree 67 of 75, the 8 failures being the new checks (rl, h1, m1, five of U), so they do test the fixes; handover test 10 of 10; check script, real run, 13 OK, 0 FAIL, 2 SKIP.
- The 65 round 1 checks are unchanged in text. In rqa and rqe GPU 0 now reports another GPU model. That is right: with the fix the tool would take the strictly free GPU 0 there, and the old checks describe "shared on the own GPU". rqf is the same setting with GPU 0 of the same model and gives the strict GPU.
- Test processes: at 14:57 there were 58 `sleep 1800`, 30 s old, with their working dir in the builder's session scratch (a test it was running). At 15:02: 0. None of mine was left at any time (E).

## 5. Launch steps
Section 4 of the request is unchanged and still right. Step 2 takes `PATCH_MD5=6262e355da16c5fceaeeeca0fd07de68`. Step 4 and step 10 expect the check script's 13 OK, 0 FAIL, 2 SKIP before the deploy (E today).
Three things to carry beside the steps, from the round 1 notes that were not built:
- N3: do not end the session `bench_rescue_<queue>` once `start dump_<run>` is in the old launch.log; before that it is safe.
- N4: a HOLD touched by hand in the old queue during the tool's 20 s wait is removed by the tool; a SIGKILL of the tool in that wait leaves its HOLD behind.
- N5: freeze c3all2 before it reaches `c3s_swad_v11_f0_s5` (E 14:59: 2 of 62 started, both PF).
Small text point: the commit message in c3lane_commit.sh still says "at two looks 30 s apart"; the rule is now 30 to 120 s.

## Not verified in round 2
- As in round 1: anything on a real cv02 GPU; the cv02-writing steps of the wrappers; c3lane_commit.sh and the deploy (code read only).
- The clear in the logger branch (the same statement as in the tested HOLD and MAXC branches; code read).
- The 120 s bound with real elapsed time in a running queue: in my tests the loop's clear acts first; the bound itself is shown by the builder's unit cases U2 and U3 (stored time set back by 125 s and 119 s), re-run by me.
- The new pin in c3lane_rescue.sh against a deployed QC (there is none yet).
