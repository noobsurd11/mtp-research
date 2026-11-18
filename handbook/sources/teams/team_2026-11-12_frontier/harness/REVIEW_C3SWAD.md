**Verdict, round 2 (17 Nov 2026, 10:45 IST): PASS** for the versions in the table "Versions reviewed, round 2" (section "Round 2" at the end of this file). The two blocking findings of round 1 (F1, F2) are closed. No blocking finding is open. Two small notes stay (R2-1, R2-2), neither blocks.

Round 1 verdict (10:09 IST, kept below as written): **FIX.** Two findings block the launch (F1, F2). Both are small script fixes in the launch path. The patch, the training-code claim, the logp claim, the read and the verdict tool pass.

# Review of LAUNCH_REQUEST_c3swad.md and harness/c3swad (reviewer c3swad_reviewer, 17 Nov 2026, written 10:09 IST)

E = measured by my own command today. S = judgement. T = /home/yugma/mtp/research/team_2026-11-12_frontier, H = T/harness/c3swad, B = cv02 /tmp/noob_el/bench_89b9ea5, QC = the new deploy dir (not there yet).
I launched nothing. cv02 was only read (ssh -n -a, BatchMode). On gaint I wrote only this file and my scratch folder. No worktree, relay dir, queue dir or harness file was changed (E 10:06: every md5 below still equal to the files on disk).
Scratch folder with every test and output: /tmp/claude-1003/-home-yugma-mtp/2f42a8b1-e6a3-43d3-94cf-a2e7c1c6c653/scratchpad/rev

## Versions reviewed
The verdict covers these md5s only. The builder changed seven files during the review. I reviewed the final versions (snapshot 09:51, unchanged at 10:06). For the three files I had read earlier in their first version (chain test, dump test, request) I reviewed the diff.

| File | md5 |
|---|---|
| harness/LAUNCH_REQUEST_c3swad.md | 80136f442699b5f88dfb11fe9f6f34e9 |
| cq_c3swad.patch | 524a70e64d2f8950ba98398f2f1423c6 |
| c3swad_commit.sh | 33c661eb89ae3fd9bf522def0ffcfcfa |
| c3swad_make_jobs.py | c8748ae68dc91e3fa9572d761fe63dc5 |
| c3swad_handover.sh | 6d397ca6f7e14577bdff33f9372c05ba |
| diskguard3.sh | 92794405dc207e4ecae8e47a620b52fb |
| c3swad_relay.sh | 535a62a239dbe3f47c863b9d6540a459 |
| c3swad_check.sh | 2213db46196d994a69a463f41e0db78e |
| c3swad_dumptest.sh | cdb377648867af2dc1838cc00e44b887 |
| run_read_c3swad.sh | c8efd03e69afe4990ba8177c57dd99b7 |
| c3swad_verdict.py | 7a48b1a18a0d34b8ca689722d2648a76 |
| c3swad_verdict_test.py | 2e1358528dc76ba4cbed6a0ef7169e28 |
| c3swad_class_guard.py | c9022bcc9ddb964298bcd38bf01ab375 |
| c3swad_chain_test.sh | cdb661c96f88a05bf52d7319269f00d6 |
| patched files (from the patch on a fresh archive of 89b9ea5, E): cq.sh | 5222150ba40130d41a04af4f7d17dbfa |
| cq_setup.sh | 630b1307a5b3cc99da251cd6eecc8672 |
| slim_ckpt.py | 20712dd3af1e6b86720a9633b419de00 |
| bench/methods_cv02/swad_const_pf_v11.yaml | 618cea2f57864ac4a916da00845da9da |
| tests/test_bench_cq_readouts.py | 0216a2cf5ea2b3d3e627d80fb196f22c |

Evidence files were read, not reviewed line by line. Where I rely on a number I re-measured it.

## Findings, most severe first

### Blocking

**F1. The dump dry test can wait without end, and then `arm` refuses while c3all is frozen.** (c3swad_handover.sh l.137-138; c3swad_dumptest.sh l.54-60; c3swad_check.sh l.68-69)
- State today (E 09:35 to 09:56): every cv02 GPU holds another user above 4 GB. Our open lanes are on GPUs 0, 5, 7 (c3all) and 2 (rows2). The dry test's `arm` step therefore passes `GPUS='1 3 4 6'` (E, builder's dry run, and the lane files I read). GPUs 1, 3, 4, 6 have been held by ds404_user13 with 22 to 45 GB since at least 16 Nov (log).
- Scenario: step 4 arms the smoke queue `c3swad_smoke`. No GPU of its fixed list qualifies, so the fixture job is never dispatched. The queue stays alive with MAXC 1 and no "all jobs dispatched" line. Then steps 6 to 9 run. `freeze` sets c3all to MAXC 0. `arm` step 1 prints `CAN_START c3swad_smoke` and refuses. Now no queue starts training on cv02 until someone ends the smoke queue by hand on the shared machine. The script has no step for that. The "way out" named in the request (l.134, `MODE=reorder`) is refused by the same test.
- The same waiting smoke queue makes `c3swad_check.sh` item "live queues that can still start training (at most one)" FAIL at step 5 (two names).
- A smoke queue whose only job is a `--fixture` line can never start a training run (cq.sh l.198-200 of 89b9ea5: training skipped). So the refusal protects nothing here.
- Smallest fix (either one is enough; both are better):
  1. In the remote loop of `arm` step 1 (handover l.137) and in check.sh l.66-68: a live queue whose jobs.txt has only `|--fixture` lines counts as ok ("fixture only, cannot train").
  2. Run the step-1 test also at the start of `freeze`, before the MAXC write, so c3all is never frozen while `arm` would refuse.
  Also wanted: a `stop` step in c3swad_dumptest.sh for a smoke queue that never got a lane (end its own tmux session by exact name, only when no `fixture ... on GPU` line exists in its launch.log).

**F2. `c3swad_check.sh` shows a false FAIL after the dump dry test has run.** (c3swad_check.sh l.60-61)
- The item "no swad run name, no c3s_* run and no swad_const dump folder exists on cv02" lists `/tmp/noob_el/bench_*/dumps/elbench1/swad_const_pf_v11`. The dry test writes exactly that folder inside QC (`QC/dumps/elbench1/swad_const_pf_v11/dumptest_c3s_swad_f0` and `.swad`). The script has no clean step.
- Scenario: step 4 runs as ruled. Steps 5 and 8 then print `FAIL` for this item and exit 1, right before `arm`. E: the same `ls` on a fake tree with a dry-test folder gives a non-empty answer, so the item fails.
- Smallest fix: look for the dump folder in B only (`$B/dumps/elbench1/swad_const_pf_v11`). The loop over the 25 real names already covers every deploy dir.

### Not blocking

**F3. One training queue: holds. Two known side cases stay, and the request words one of them too strongly.** (request l.25)
- "The new queue ... never shares their GPU" is true only while the c3all run is in training. E (c3all gpumem.log, 33 training runs, 30 dumps): a training run is above 4,096 MiB 7 to 15 s after its start line and stays there (PF and HOUSE 5,736 to 5,740, HRNet 8,430). A dump peaks at 3,212 (PF, HOUSE) or 3,944 MiB (HRNet), never above 4,096. So c3all2 does not see a c3all or rows2 dump as "another user". It can start a training run beside such a dump (about 2 minutes). It can also take a GPU in the seconds between a c3all training end and its dump start; that dump then waits one training cycle (E in my sandbox test X5: the old queue's dump lost the GPU and ran when the new run's training had ended).
- Both cases were accepted on 16 Nov (log 17:57). Never two training runs: E in X5, and the lane section of cq.sh is byte-equal in old and patched file (md5 9a14ecb9 both).
- Concrete case now: the dump of `c3_pf_v11_f3_s7` waits for GPU 0 since 07:31. The c3swad read needs this PF run (seed 7 is in the A/A). After the handover it races c3all2 for GPU 0 each time the other user leaves.
- No fix needed. Correct the sentence. If the lead wants zero overlap: arm only after c3all's open lanes have ended.

**F4. `arm` reports "armed" even if cq.sh refused to arm.** (c3swad_handover.sh l.159)
- cq_setup.sh prints its "armed: gpumem .. queue .." line from the pid files. cq.sh writes queue.pid before its checks. If cq.sh then stops with "not starting" (for example the logger died), the handover still logs "armed".
- Scenario: the lead reads "armed", starts the relay, and c3all is frozen with no successor running. The tail of launch.log is printed, so a careful reader sees it.
- Smallest fix: also require the line `cv02 q armed:` in the printed tail, else REFUSED.

**F5. gaint has no automatic stop for the relays, and the request leaves gaint about 2 GB short.** (request section 5)
- E: gaint 70 GB free at 09:56, one filesystem. Sizes in section 5 are right (E: latest.pth 896 MiB and best.pth 99 MiB in 10 of 10 swad runs; slim with two sets 208,990,665 bytes; dump without logp 133 to 134 MB, 108 files; relayed PF run 1,092 MB).
- Scenario: a session gap like the 10 hours of 16 Nov falls into the HOUSE relays. Three relays keep pulling. The disk reaches 0. LOSO-2 trains on the same filesystem and fails at its next checkpoint. Nothing relayed is lost (the relay retries and never writes on cv02), but a gaint training run can be.
- Smallest fix (S): a gaint loop like diskguard3.sh that touches STOP in the relay dirs below 15 GB, started with the third relay. Or free the 20 GB named in the request before arming.

**F6. Request l.89: "a checkpoint is overwritten in place, so they add little" is not exact.** E: `atomic_save` (src/utils/checkpoint.py l.92-98) writes a temporary file and renames it. A swad lane needs about 0.9 GB more for some seconds at each of its 10 saves. With three swad lanes about 2.7 GB. Inside the 20 GB floor. A full disk at that moment ends the training run (rc not 0, no dump, the queue never restarts it); the last complete latest.pth stays.

**F7. The read script uses up its registered output folder when the manifest check refuses.** (run_read_c3swad.sh l.65 before l.70-89)
- E (my fake relay trees): on a wrong manifest the script refuses and starts no read, but `bench_reads/c3swad` then exists with links. The next run without TAG refuses ("output folder exists"), and the header says the read without TAG is the registered one.
- Smallest fix: run the manifest check before `mkdir`, or say in the header that a refused folder may be removed by the lead.

**F8. The verdict tool does not check which read it is given, and it crashes on an undefined value.** (c3swad_verdict.py l.126-133, l.67-71)
- It asserts M, A/A, the three arm names and one clean-cells block. It does not assert 25 runs per arm, seeds 5 to 9, cv5v3, or `aa_spec = PF:5,6:7,8`. E: on the cv5v2 screen read (2 seeds, A/A from another arm) it prints a verdict line.
- If a judged width mean is null it ends with a TypeError and writes no file (E, my case 27). That is safe. E: no judged subset has a null width in the screen read on the same 532 and 416 cells.
- Smallest fix: four asserts on read.json (`aa_spec`, 25 run ids per arm, seeds, set names start with cv5v3_f).

**F9. A test that does not test what it claims.** (evidence/realtest.sh l.18; request l.149 "a missing key is refused")
- The log line is `refuse: ... slim.pth exists`. The run dir already held a slim.pth, so the missing-key check was never reached.
- I ran it in a fresh dir (E): `--keys swad_bn,nokey` gives an AssertionError, rc 1, nothing written. `--keys swad,swad` is refused too. So the claim is true, the builder's test did not show it.

**F10. Freeze write is not atomic.** (c3swad_handover.sh l.71) `echo 0 > MAXC` truncates, then writes. A read by cq.sh in that instant gives an empty string; the MAXC test then errors and falls through, which equals a read just before the freeze. The 180 s wait and the two started-set checks cover it. If the write fails after the truncate (full disk), MAXC stays empty, c3all runs on as before, `freeze` says "not confirmed", and a second `freeze` refuses on the empty value. Smallest fix: write `MAXC.new`, then `mv`.

**F11. The dump dry test leaves its files.** (c3swad_dumptest.sh, no clean step) About 1.4 GB stay in QC on cv02 (fixture latest.pth 897 MiB, slim 199 MiB, two dumps 266 MiB) plus the queue dir `c3swad_smoke`. Its logger and tmux session end by themselves after the end line. A removal by hand must not touch any file listed in QC/CODE.md5: c3all2 checks QC before every start and HOLDs the whole merged queue if it fails (E: missing or changed QC gives "deploy check FAIL").

**F12. Small points.**
- c3swad_check.sh counts: the request's "23 OK, 0 FAIL, 2 SKIP" (l.117) needs an IO folder with a rendered.txt (the builder's scratch render). Run as the lead would run it before `render` it gives 21 OK, 3 SKIP. E: with my own render as IO I get 23 OK, 0 FAIL, 2 SKIP.
- c3swad_check.sh l.68: a live queue with no MAXC file (default 16) is not counted as able to start. All our queue dirs have the file (E). The handover's own test handles this case correctly.
- c3swad_commit.sh: if the patch or the tests fail after `worktree add`, the worktree and branch stay and a second run refuses. Cleanup by hand.
- c3all/maxc_window.sh is written for c3all and exits without change when c3all's MAXC is 0 (l.19). A starved dump after the handover needs a copy that acts on c3all2 and never writes into c3all/MAXC.
- Naming: on cv02 the folder `<name>` holds swad_bn. In the screen `<run>` held the raw model and `<run>.swad_bn` held swad_bn. The read script's manifest check (weights_key per folder) protects the read (E: swapped keys are refused).
- Comment lines still say 09:35 for the ruling; a stray `H/__pycache__`. Both named by the builder.

## The eleven points

**1. One training queue only: PASS, with F1 and F3.** Freeze (E by code): refuses unless MAXC reads 8 or 0 and no MAXC window session runs; confirms the write. A c3all start can still happen for some seconds after the write (MAXC is read before the lane scan); `build` refuses before 180 s, reads the started set twice 20 s apart, and `arm` compares it again. `arm` without `freeze`: refused (`CAN_START c3all`; E, c3all has no "all jobs dispatched" line and MAXC 8). `arm` twice: the second run is refused at step 3 (queue dir used, session exists), and cq_setup.sh refuses too. Freeze failing halfway: c3all keeps running, nothing else is armed (see F10). A c3all run mid-training at the freeze: finishes under c3all; c3all2 sees it as another user above 4,096 MiB and waits (E, X5). A c3all dump waiting for its GPU: can lose the GPU for one cycle (F3). LPG counts only the queue's own lanes; other queues are seen only through nvidia-smi memory. Another user above 4,096 MiB: lane rule unchanged, byte-equal.

**2. The patch: PASS.** E: the patch applies to a fresh archive of 89b9ea5 and gives the five pinned md5s. Pytest 20 passed; the new test file on the unpatched script 13 failed, 1 passed, as claimed. Chain test first version 32 of 32, final version 34 of 34, both re-run by me. The tests do test what they claim, with one exception outside the patch (F9). For a 9-field line I read every changed line: render, start, dump, slim call, RUN.md5 list and all failure paths are the same; the only differences are that the card variant, cvcard.py and slim_ckpt.py are read from QC, that `deploy_ok` also checks QC, and one more clause in the armed line. E: unpatched and patched slim_ckpt.py without `--keys` give byte-equal files on the real 20k checkpoint (md5 6fac3b9a, 626,981,021 bytes). E (my test X6): a plain line with a HOLD between training and dump gives the same launch.log lines and a byte-equal RUN.md5 in old and patched script. E: the 74 carried rendered lines of today's merged list are byte-equal to lines of c3all's own jobs_rendered.txt (97bb83fc), rendered by the patched script with the real card code.
For a swad line (E, my tests X1 to X4 and the builder's T3): first dump fails: second dump is not started, no slim, no RUN.md5, lane released, latest.pth kept. Second dump fails: the same; the first dump folder stays. Slim fails: both dump folders and latest.pth stay, no RUN.md5. HOLD between the dumps: the second dump waits and nothing else takes the lane; it runs after the HOLD is removed. GPU taken between the dumps: the second dump waits for its GPU, lane held, then runs on the same GPU. Nothing is deleted or overwritten by the patch (no delete in any added line). `--keys` drops four weight sets from the slim copy only (model, raw_bn, ema_9998, ema_9998_bn); they stay in cv02's latest.pth and nowhere else (ruling Q3). The relay and the read need none of them.

**3. QC split: PASS.** With QC != B the patched cq.sh takes cq.sh, cq_setup.sh, cq_gpumem.sh, cvcard.py, slim_ckpt.py and bench/methods_cv02 from QC, and bench_lib.sh, bench.cards, the cards, train.py and bench_infer.py from B (code read; builder's T4 and my render). E: the real cvcard.py from the patched tree accepts all four card variants of the merged list. `deploy_ok` keeps its B checks and adds QC's CODE.md5. cq.sh does not pin QC's revision; the handover pins eight file md5s and requires that QC differs from B only in the patch's files (cv02 shell is bash 5.1, so the process substitution works, E). QC missing: "deploy check FAIL", nothing rendered (E). QC = B: the swad card variant is missing in B, arming fails. QC forgotten: the unpatched script refuses the 10-field line (E). All fail safe.

**4. Training code: PASS.** E: c57508e is an ancestor of 89b9ea5. Between them the only modified file under src, configs and scripts/train.py is src/models/bench_models.py, one hunk inside `build_bench_smp` for deeplab decoders; the card uses `model.name=smp_unetpp`, another branch of model_factory.py. trainer.py, weight_avg.py, enc_probe.py, bn_recalibration.py, train.py, both configs, cards.py and the card are not in the diff. Card md5 46fb5b02 in both gaint trees and on cv02 B. My archive of 89b9ea5 plus REVISION gives CODE.md5 7cde26e4, equal to cv02 B's, so B is that commit. The options rendered for `c3s_swad_v11_f0_s5` equal those rendered for the screen run by c57508e, data.root and run_name aside; check.sh confirms 25 of 25. The cv02 variant differs from the card in the weights path line only, the same line as in the PF variant.

**5. logp: PASS.** E by code: the read loads cells with `dumpfmt.read_cell` (logp optional) and uses `pred` at argmax, `m_crack` and `oth` for every bias and width-matched candidate (crossfit_op.py l.73-91), and `p_crack` in the records. Guards, per-source tables and the class guard come from those records. No line of bench_read_w1.py, w1read.py, crossfit_op.py or score_ext.py names logp. E: the screen's swad dumps hold `pred, oth, m_crack, p_crack, p_inact` only, and the wave 2a read ran on them; 0 of 161 dump lines there carry `--logp`. E: 0 of 75 rendered swad lines carry `--logp`. I found no registration for these runs that needs logp (this request, the wave 2a request and gates, WAVE2_REVIEW). Later uses that would need it: seed ensembles, class-bias operating points, stride-head studies, teacher use (bench/derived.py, classbias.py, headres.py). Those would need a new dump from cv02's latest.pth, or from the relayed two-set slim on gaint (another GPU model).

**6. Names, relay, removal: PASS.** E: the running relays use `^c3_` (N 50), `^c3h_` (N 25) and `^r2_`; none matches `c3s_`. `^c3s_` matches no PF, HOUSE or HRNet name. c3_f81_list.sh on a swad run counts and removes only the folder `<name>`; `<name>.swad` stays (E on the sandbox RUN.md5: 3 of the 6 dump lines counted, one directory matched). The read uses `re.fullmatch` (w1read.py l.64), so SWADBN does not take the `.swad` folders and SWAD takes only them; the two arms are in another method dir than PF. Relay of a run with two dump folders and enc_probe.jsonl: the relay tars every path of RUN.md5 and compares checksums and the file count. E: I ran its tar, `md5sum -c` and count steps locally on the sandbox swad run: OK, count equal, both dump dirs and the probe file present. Not run over ssh.

**7. Disk: PASS on the numbers, see F5, F6, F11.** Sizes and totals of section 5 reproduce (E, listed in F5; cv02 83 GB free, gaint 70 GB). cv02 when space runs out: below 20 GB the guards set HOLD (no new start, dumps wait). A full disk during a checkpoint save ends that training run; during a dump or slim the step fails, no RUN.md5 is written, latest.pth stays, a partial dump folder or `slim.pth.tmp` stays and needs removal by hand before a rescue. RUN.md5 is written by rename, so the relay never sees a half file. gaint: the relay's tar fails, the run is retried three times, `.part/<name>` is replaced; nothing is written on cv02. diskguard3.sh is diskguard2.sh (6672f858, the file running on cv02) with the queue names, log and stop file changed (E, diff: 7 lines). It only touches HOLD in c3all2 and c3all3. Correct and harmless.

**8. Read and verdict tool: PASS, see F7, F8.** E: `SHOW=1` prints the command of section 7 word for word. E (11 fake relay trees, read tool stubbed): the script starts the read only on a complete set; it refuses a missing `.swad` dump, an empty enc_probe.jsonl, a missing `.ok` file or relay line, swapped weights keys, a second GPU model, another train code revision, a seed mismatch, step 19999, bf16, cpu dumps, and an existing output folder. E: relayed PF manifests have key `model`, RTX A6000, 89b9ea5, fp32, step 20000; all eight cv02 GPUs are RTX A6000. M has no free choice: `--aa PF:5,6:7,8` is fixed in the script, M = max(0.01, 2 x SE) at OP-A is in the tool (crossfit_op.py l.328-330), computed once per cell set, with a fixed bootstrap seed and 2,000 draws.
Verdict tool against the rule text of 09:30: the text is in the request and in the docstring word for word (E, grep). E: 27 of my own synthetic cases give the verdict the text gives. Covered: all pass; only a per-source width fails at OP-A; only at OP-W; several per-source widths on both cell sets; pooled width; per-source plus pooled; false alarms; headline failing on each of the four values; headline failing beside a per-source width; secondary failing a guard, the headline, or the false-alarm guard; primary passing with a failing secondary; inactive IoU; mIoU-R13; all bounds at equality (inclusive); a source below 40 cells; a source at exactly 40; OP-F ignored; PF with 0 false px; no margin, no clean block, or a missing arm (refused). The builder's own test gives 15 of 15 (E). **I found no case where text and tool differ.**
What the text leaves open and the tool decides (S; write one line each into section 7): (a) "width ratio (arm / PF)" is the ratio of the two seed-mean width ratios, not a mean of per-seed ratios; (b) "at least 40 cells" is counted per cell set; (c) guards have no interval, so 1.1501 fails and 1.1499 passes; (d) "passes the headline at both operating points" means all four values, also for swad.
For the write-up (S): the carry was widened with the screen's ARTS values known (1.147 at OP-W), on the same 532 cells. The rule predates every cv5v3 swad number, but the width guard is not tested on independent cells.
Mechanics on the screen read reproduce W2A_READ.md (E: +0.0135 [+0.0051, +0.0221]; ARTS 1.203 and 1.218 at OP-A, 1.132 and 1.147 at OP-W). c3swad_class_guard.py differs from the reviewed w2a_class_guard.py (1859f91a) in one line and gives the lead's class_guard.txt byte for byte (cb98b8ff, E).

**9. Dump dry test: PASS on safety, FIX on procedure (F1, F2, F11).** It can never start a training run: the job is a `--fixture` line, allowed only for `dumptest_*` names, and cq.sh skips training for it. `arm` passes only GPUs without an open lane of any of our queues; the queue's own lane rule then refuses a GPU where another user, or a training run of another of our queues, holds more than 4,096 MiB, before each of the two dumps. The gap the builder names is real (a c3all training start on that GPU in the 7 to 15 s before a dump's check). `place` refuses if the fixture or the queue dir exists, if QC is B, or below 30 GB free; it writes only `QC/experiments/dumptest_c3s_swad_f0` and the queue dir. E: a fresh deploy has an `experiments` folder, so the tar step works. There is no clean step, so it cleans nothing, its own files included.

**10. Check script: PASS, see F2 and F12.** E: a real run gives 23 OK, 0 FAIL, 2 SKIP. In a scratch copy with tampered inputs and canned cv02 answers, 19 of 19 tampered items print FAIL: card md5 in the screen tree, card on cv02, 25 renders, QC pins, roots (two items), train line, `--logp`, wrong fold, names on cv02, a c3s run in another relay dir, a wider relay pattern, two queues able to start, LPG 2, two runs on one GPU, cv02 free 44 GB, a dead guard, a dead relay, a patch that does not apply, another A/A split in the read script. Not tampered (they read the real repo or disk): tree at 89b9ea5, the two git diff items, gaint free space, "no read folder yet".

**11. Stated as measured, not reproduced as stated.** "A missing key is refused" (F9). "23 OK, 2 SKIP" needs the builder's IO (F12). HRNet run time 117.5 min (n 7): I get 122.3 (n 8), one more run has ended. Everything else I re-measured agrees: PF 64.0 min (n 13, 59 to 82), HOUSE 65.4 (n 10), dump 1.7 min, wait to dump start 3.2 min mean (median 0.0, max 54: the mean comes from the starved dumps); gaint swad 99.3 min against 97.6, 98.1, 99.8; peaks 7,154 (10 of 10), 6,830, 7,068 MiB on gaint, 5,740 and 3,212 on cv02; the default list 29388346 (62 lines: PF 10, swad 25, HRNet 12, HOUSE 15; order PF s8, s9, swad s5 to s9, HRNet s7 rest, s8, s9, HOUSE s7 to s9, as ruled); no logp field on the swad lines.

## Not verified
- The patched chain on a cv02 GPU, and the real relay over ssh of a run with two dump folders (the dry test and the first swad run will show both).
- Every cv02-writing step of the handover and of the dump test (freeze, render, place, guard, arm): code read and the builder's dry output only.
- c3swad_commit.sh and c3_deploy.sh with the new commit: code read only (I was not to commit or deploy).
- `test_other_on.sh` on the patched file: not re-run; I compared the lane section instead (byte-equal).
- swad run time and peak memory on cv02 (estimates from gaint), and how many lanes the other users will leave. At 10:00 no cv02 GPU qualifies.
- That a later re-dump of other readouts is ever wanted (it would need cv02's latest.pth, which lives under /tmp on a shared disk at 96%).

## What blocks the launch
Exactly two findings: **F1** (a waiting dump dry test makes `arm` refuse while c3all is frozen; fixture-only queues must count as ok, or the test must run at `freeze`) and **F2** (check.sh item 5 fails after the dry test). After these two fixes the changed files (c3swad_handover.sh, c3swad_check.sh, c3swad_dumptest.sh if a stop step is added) need a diff review. F3 to F12 do not block; F4, F5 and F8 are worth doing in the same round.

# Round 2

**Verdict, round 2: PASS.** F1 and F2 are closed. Every other change does what section 14 of the request says and nothing more. No blocking finding. Two notes (R2-1, R2-2) are listed below; the lead can launch without them.

Written 10:45 IST, 17 Nov 2026. Same rules as round 1: cv02 only read, nothing launched, nothing changed outside this file and my scratch folder. E = measured by my own command, S = judgement.
`reviewed_r1` is what I reviewed in round 1 (E): its 14 files and the request are byte-equal to my own snapshot of 09:51, and `REVIEWED.md5` checks. So each change is the diff against it, and I read every diff.

## Versions reviewed, round 2
The round 2 verdict covers these md5s only (snapshot 10:34, unchanged at 10:42, E).

| File | md5 | against round 1 |
|---|---|---|
| harness/LAUNCH_REQUEST_c3swad.md | 2dc215f015f178b79b01a542768621cf | changed |
| c3swad_handover.sh | 0bb63159b26b1cdf0c2f5fc4cb69798d | changed |
| c3swad_check.sh | ecf56c5cec6c8d9272f65a162eddd9fe | changed |
| c3swad_dumptest.sh | 242810922385e4ef0f45fb5205ea4944 | changed |
| run_read_c3swad.sh | 10ed79a6d536135f4fbdde6a0d02c276 | changed |
| c3swad_verdict.py | 61ce4ba0bb7cfa1e01922f281a3b67b2 | changed |
| c3swad_verdict_test.py | 26db76b4380b3812f11a63e1e0ddb7d5 | changed |
| c3swad_commit.sh | f70ded517ac7aa85e0720d551ac51d0d | changed, 4 comment lines only (E, diff) |
| evidence/realtest.sh | 5516bea0b3ace5bf49b7fe03a64cdae6 | changed |
| c3swad_relayguard.sh | 65b63ea7df6e06ece4ecaa9291f12e77 | new |
| maxc_window_c3all2.sh | 34f9d507980c1563ec0d74b591b328cd | new |
| c3swad_fix1_test.sh | 355d26fef3300739d4c27894ed927a84 | new |
| cq_c3swad.patch | 524a70e64d2f8950ba98398f2f1423c6 | same |
| c3swad_make_jobs.py | c8748ae68dc91e3fa9572d761fe63dc5 | same |
| diskguard3.sh | 92794405dc207e4ecae8e47a620b52fb | same |
| c3swad_relay.sh | 535a62a239dbe3f47c863b9d6540a459 | same |
| c3swad_class_guard.py | c9022bcc9ddb964298bcd38bf01ab375 | same |
| c3swad_chain_test.sh | cdb661c96f88a05bf52d7319269f00d6 | same |

## 1. F1 and F2

**F1: closed.** Three changes, each tested.
- `qscan` (c3swad_handover.sh l.60-63), used by `freeze` and `arm`: a live queue counts as unable to train if MAXC is 0, or all jobs are dispatched, or field 9 of every line of its jobs.txt is `--fixture`. E (the remote command run on a fake queue tree): fixture-only lists with 10 fields, 9 fields and two lines give `ok ... fixture only`; a list with a training line beside a fixture line, a blank line, a smoke line (`--exit_after_step`), an empty list, or no MAXC file gives `CAN_START`; a dead queue and NEWQ are not listed. All wrong guesses go to the safe side. cq.sh skips training for a `--fixture` line, so such a queue cannot train.
- `freeze` (l.77-81) runs `qscan` before the write and refuses, writing nothing, if another queue could start or if the queue to freeze has no live process.
- The walk again: the smoke queue is armed and never gets a lane. Check script: item 6 does not count it. `freeze`: prints `ok c3swad_smoke fixture only, cannot train`, then writes. `arm` step 1: the same line, no refusal. E: the builder's fake-tree test (T3, T5), re-run by me, and `DRY=1 freeze` against the real cv02 (the new remote command parses there; c3all/MAXC still 8 with its mtime of 16 Nov).
- `stop` (c3swad_dumptest.sh l.73-83): refuses unless the test's session is alive and the state is exactly "no lane, no .gpu file, no HOLD". Then, on cv02: HOLD in the test's own queue dir, 20 s wait, the same check again, `tmux kill-session -t '=bench_q_c3swad_smoke'`, HOLD removed. If the fixture took a lane in those 20 s it ends nothing and removes its HOLD. The session name is a constant and is matched exactly (`=`), so it cannot end another session. It signals no process by PID or pattern. It writes only the HOLD file in its own queue dir.
- `clean` (l.84-95): the list is five fixed paths built from the validated QC (`/tmp/noob_el/bench_<7 hex>`, not B) and constants. It refuses while the test's session or queue process is alive, and unless `grep` finds 0 lines of QC/CODE.md5 inside those folders. After the removal it runs `md5sum -c` on QC and says so. It cannot break QC's check: it removes only paths that CODE.md5 does not list. E (fix test T8): every other file of QC and all of B unchanged, CODE.md5 still checks.

**F2: closed.** c3swad_check.sh l.60 looks for the swad dump folder in B only. E: with canned cv02 answers the item is OK after a dry test and FAIL with a folder in B; the real run of the new script gives 23 OK, 0 FAIL, 2 SKIP with my render as IO.

## 2. Every other change

- **`qscan`, freeze pre-test:** above. No other effect.
- **MAXC by rename (l.82):** `echo 0 > MAXC.new && mv MAXC.new MAXC && cat MAXC`. A reader never sees an empty file. If the write fails, MAXC is untouched and `freeze` says "not confirmed". F10 closed.
- **`arm` waits for the armed line (l.171-178):** after cq_setup.sh's line it polls launch.log every 10 s, up to ARMWAIT (300 s), for the first line that holds `cv02 q armed:` or `; not starting`. Only the first gives the log line "armed". E (fix test T5): armed, refused, and no line at all behave as stated. F4 closed.
  State after a timeout: c3all frozen; the session bench_q_c3all2 exists; cq.sh is either still in its checks or gone; the handover has printed REFUSED and logged nothing. A second `arm` is refused (queue dir used). If the armed line comes later, the queue runs normally and only the handover's log line is missing. If cq.sh logged `; not starting`, c3all2 is dead and its dir is used up: the way on is a new handover with `NEWQ=c3all3` and a new IO (c3all is already 0; the dead c3all2 is skipped by `qscan`; diskguard3.sh covers c3all3). That path is not written in the request (S: one line in section 9).
- **Check script:** l.60 (F2); l.66 shows MAXC and LPG defaults 16 and 2 when the file is missing and adds `fixture_only`; l.68 uses it; l.87 lists three more md5s. E: tampered copy: two startable queues (one printed with MAXC 16), LPG 2, a mixed job list, a folder in B each print FAIL. See R2-1.
- **Read script:** the manifest block is the same text, moved before `mkdir`, its output kept and written into run.log later. E (my fake relay trees, read tool stubbed): complete set: read started, folder created; ten wrong inputs (missing dump, empty probe file, swapped key, second GPU model, other code revision, seed, step, a manifest without `device`, a broken manifest): refused and **no output folder**. `SHOW=1` prints the same command as in round 1, byte for byte. The verdict tool is called without `--mechanics`. F7 closed.
- **Verdict tool:** the verdict branches are unchanged (diff: only the mark is added to the line under `--mechanics`). New: `check_read` and plain refusals. E: my 27 round 1 cases give the same verdicts on a read of the registered shape, and 13 new cases pass (40 of 40): refused without `--mechanics` for another A/A arm, another split in the clean block, 24 runs, a run id twice, a missing seed, a cv5v2 set, a 2-seed read; plain refusal, no file, for PF width 0 on a judged source and for null false px; a source below 40 cells with PF width 0 is still skipped; other arms beside the three do not disturb. The builder's test: 23 of 23 (E).
  `--mechanics`: can a real verdict be made with it on? No: the first line and the verdict line both carry "MECHANICS TEST, NOT A VERDICT", also on a registered read (E). Can a mechanics run pass as a verdict? Not without editing the file by hand. Without the switch the screen read is refused (E). One behaviour change to know: PF width exactly 0 on a judged source is now a refusal, before it was a failing width item. It cannot be judged either way.
- **Commit script:** 4 comment lines. **realtest.sh:** the two `--keys` refusals now run in fresh dirs; the new log shows the AssertionError and no slim.pth for both (F9 closed).

## 3. The two new scripts that act on live things

**c3swad_relayguard.sh: PASS.**
- It only touches `STOP` in a relay dir, and only if all of these hold: free space of the relay filesystem below the floor, the dir is one of the four names, no STOP yet, `relay.pid` names a live process. E (fake relay dirs): above the floor nothing; below it STOP for the live relays only; a dead pid, a dir without pid and another dir untouched; an existing STOP not rewritten; the fake relay process still alive after the pass.
- Does the running relay honour STOP? E: both stage copies of relay_w1c.sh are 74a2ec3d and l.38 is the STOP check at the top of the poll loop. I ran that file with a scratch relay dir and a stub ssh: with STOP present it logs "STOP file seen; relay stops", makes 0 ssh calls and removes relay.pid; with STOP placed during its wait it ends at the next pass.
- Can it stop a relay wrongly? Only when `df` shows less than 15 GB, which is its purpose. Can it fail to? Two cases (S): a relay pulls every run already listed in its running pass before it sees STOP (about 1 GB each); and if `df` fails the guard does nothing and logs nothing. With the default path `df` works (E: 67 GB at 10:39).
- A stopped relay stays stopped until the lead removes STOP and starts it again (the request says so).

**maxc_window_c3all2.sh: PASS, see R2-2.**
- It names c3all2 only: no line outside comments holds another queue path (E, grep). Arguments must match a RUN.md5 path pattern; they are only listed, never written. So it cannot write into c3all/MAXC. E (fix test T9): c3all/MAXC stayed 0, c3all2 went 1 then 8, no MAXC.new left.
- It refuses unless c3all2/MAXC reads 8 (E against the real cv02: no such file yet, "nothing changed"). It restores 8 on a normal end, on timeout and on INT, TERM, HUP. After SIGKILL or a lost gaint session c3all2 stays at 1, the safe side.
- Both writes go by rename.

## 4. c3swad_fix1_test.sh
E: re-run in my scratch folder: **45 of 45**, the same PASS lines as evidence/fix1_test.out. The copies under test hold no ssh command (only the words "ssh failed" in messages) and no `/tmp/noob_el` path, so nothing can reach cv02. I checked its fake tree after the run (MAXC values, the single `kill-session` of the test's own session, the handover log). It tests what it claims. Its limits, which the request states too: tmux is a stub, so the real cq.sh never runs there and "armed" or "not starting" is played by the stub; `render` is not run; the read tool is a stub.

## 5. Request text
Sections 2, 3, 5, 7, 8, 9, 13, 14 read against my findings: F3 and F6 are corrected as I wrote them; the four definitions and the limitation line are in section 7; the check counts (21 and 3 before `render`, 23 and 2 with a render) are right (E); HRNet time updated; section 14 matches the diffs line by line. Nothing of round 1 is left out. Two lines are missing (S, both small): the way on after `arm` reports "did NOT arm" (new NEWQ, new IO; see point 2), and what to expect from the dry test today (below).

## Notes, not blocking

**R2-1. The check item "no GPU carries two of our training runs now" counts an open dry-test lane as a training run.** (c3swad_check.sh l.66, the second loop)
- A fixture job has a `.gpu` file and never a `<name>.rc`, so it is listed until its chain ends. E (fake tree, one live queue): a dry-test lane and one training run of ours on the same GPU give `FAIL`; without the dry-test lane `OK`.
- When it can happen: the test's fixture takes a GPU, c3all (or later c3all2) starts a training run beside its 3.2 GB dump (the accepted case), and the test's next dump then waits for that run to end. Likely today if the test gets a lane at all, because c3all waits for any qualifying GPU. The check then shows this FAIL at step 5 or 8 until the test's chain ends.
- How to read it: the two lines are printed just above the item; one of them is `dumptest_c3s_swad_f0`. That is one training run and one dry-test lane, not two training runs.
- Smallest fix: in that loop skip names that start with `dumptest_`.
- Side remark: if no queue at all were alive the item would always print OK (the `sed` range removes the whole list). Not the case on cv02 (four live queues).

**R2-2. The window script writes 1 and later 8 without looking at the value again.** (maxc_window_c3all2.sh l.21, l.28)
- Only matters if c3all2 is itself frozen by a later handover in the seconds between the script's read of 8 and its write of 1, with the script run outside the tmux session `bench_maxc_window`. In every other order `freeze` refuses (it sees that session, or it reads 1).
- Then the script would write 1 and later 8 over the 0.
- Smallest fix: make each write conditional inside the same remote command (write 1 only if the file reads 8; write 8 only if it reads 1). Until then: run it only in the named session, as its header says.

**What to expect from the dry test today (S).** At 10:41 its GPU list would again be 1, 3, 4, 6, all held by other users. If one frees, c3all wants it too. So the test may not start for hours, or may run its first dump and then wait behind a c3all run for its second (then R2-1 shows, `stop` rightly refuses, `clean` waits). None of this blocks the handover any more. Whether to wait for the test result before `freeze` is the lead's call.

## Not verified in round 2
- As in round 1: the patched chain on a cv02 GPU, the relay over ssh, the cv02-writing steps on the real cv02 (now run in the fake tree and as DRY forms against cv02), the commit and deploy scripts.
- `stop` and `clean` against a real tmux and a real queue process (stub tmux in the fake tree; DRY forms against cv02 gave the expected refusals).
- The time cq.sh needs on cv02 for its arming checks against the 300 s wait (on gaint the same checks took 18 s for 62 jobs).
