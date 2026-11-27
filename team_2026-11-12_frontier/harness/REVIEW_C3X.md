Verdict, round 2 (17 Nov): PASS for the set pinned in the round 2 section (round 1: FIX, B1 closed, B2 closed)

# Review of the c3x launch set (HRNet-W18 U-Net++ + swad_const, 25 runs on cv5v3, cv02), round 1

Reviewer: c3x_reviewer (fresh, adversarial). Review 18:14 to 18:29 IST, 17 Nov 2026 (times from `date`). E = shown by my own command, S = judgement.
Read and test only: CPU at nice 19, at most 8 threads; nothing on a GPU; cv02 read only (`ssh -n -a -o BatchMode=yes`); no file of the builder and no worktree changed (git clones and archives in my session scratch, removed at the end); no commit, no push; the only process I started (a CPU fixture, PID 1943710) ended by itself (rc 0); no sealed test set read.

**Short form:** the training-queue rule, the card, the code equality, the gate arithmetic, the read and the verdict rule all hold under my own tests. One blocking item, small: (B1) the PATH smoke check passes with "0 FAIL" when the slim step failed or was never run, and the slim step itself returns rc 0 on failure. With B1 fixed (two small edits, no change to c3x.patch) I would give PASS. (B2, the request md5 that differed from the 18:14 pin, is closed: the lead re-pinned e78278d2 by message after my report, see B2.)

## Files reviewed (md5 on disk 18:14:44 and again 18:27:22, unchanged during the review)

| File | md5 (first 8) | lead's pin | |
|---|---|---|---|
| LAUNCH_REQUEST_c3x.md | e78278d2 (mtime 18:14:42.95) | 35321335, re-pinned e78278d2 by the lead after my report | = after the re-pin (B2, closed); I reviewed e78278d2 |
| c3x/evidence/smoke_fixture_check.sh (named by the lead's correction) | 358d708e (E 18:29) | 358d708e | = (read; I ran my own variant of it) |
| c3x/c3x.patch | 602178f0 | 602178f0 | = |
| c3x/c3x_commit.sh | 4c8aa8eb | 4c8aa8eb | = |
| c3x/c3x_codeproof.sh | 5e78fb44 | 5e78fb44 | = |
| c3x/c3x_make_card.py | 99c1bf23 | 99c1bf23 | = |
| c3x/c3x_make_jobs.py | 08ec8abe | 08ec8abe | = |
| c3x/c3x_rendercmp.py | a4fca225 | a4fca225 | = |
| c3x/c3x_queue.sh | fcf9a1c7 | fcf9a1c7 | = |
| c3x/c3x_check.sh | d134edd6 | d134edd6 | = |
| c3x/diskguard4.sh | eb929c57 | eb929c57 | = |
| c3x/c3x_relay.sh | b3bc1db9 | b3bc1db9 | = |
| c3x/c3x_relayguard.sh | c221e73a | c221e73a | = |
| c3x/run_read_c3x.sh | 4e80bf54 | 4e80bf54 | = |
| c3x/c3x_verdict.py | f7d90d01 | f7d90d01 | = |
| c3x/c3x_class_guard.py | c9022bcc | c9022bcc | = (byte-equal to c3swad_class_guard.py, E cmp) |
| c3x/c3x_verdict_test.py | f5d605ab | f5d605ab | = |
| c3x/c3x_read_test.sh | 28b5b017 | 28b5b017 | = |
| c3x/c3x_queue_test.sh | 3bc083d4 | 3bc083d4 | = |
| c3x/smoke/c3x_smoke.sh | 2a4edf8b | 2a4edf8b | = |
| c3x/smoke/c3x_smoke_check.py | 4eac38ea | 4eac38ea | = |
| c3x/smoke/c3x_smoke_card.py | b137f4dd | b137f4dd | = |
| c3x/smoke/smoke_c3x_hrnet_swad_path.yaml | 0f444c68 | 0f444c68 | = |

Worktrees at the end (E 18:27): bench_wt_c3s at 852ed5c, 0 tracked changes; bench_wt_final at 89b9ea5, 0 tracked changes.

## Blocking findings

**B1. The PATH smoke can "pass" without the slim step (smoke/c3x_smoke_check.py l.228-230; smoke/c3x_smoke.sh l.74).** (E)
- c3x_smoke_check.py reports a missing `experiments/smoke_c3x_path/checkpoints/slim.pth` as `SKIP P7 slim` (l.230, `say(None, ...)`), which is not counted, so the script prints `# 0 FAIL` and exits 0. Proof: my own CPU fixture of the path smoke (real train.py of the c3x tree with the smoke card plus the builder's tiny overrides; real latest.pth, enc_probe.jsonl, slim.pth; synthetic queue and dump lines as in evidence/smoke_fixture_check.sh), copy with slim.pth removed: `SKIP P7 slim ...`, `# 0 FAIL`, rc 0.
- `c3x_smoke.sh slim` runs slim_ckpt.py inside `( ... ) 2>&1 | tee ...` without pipefail, so its rc is tee's. Proof: Q_TEST/R_TEST pointing at a scratch dir without the run: slim_ckpt.py raised `FileNotFoundError: ... latest.pth`, `c3x_smoke.sh slim` returned rc 0.
- Together: a failed (or skipped) slim step followed by `check` gives exactly the request's step-4 criterion "0 FAIL". The lead's Q2 ruling puts the slim step with `--keys` in the path smoke, and attack point 3 asks that the check fail when any proving point is missing. This one does not.
- Fix (S): in c3x_smoke_check.py make a missing slim.pth a FAIL in normal mode (keep SKIP only under `--fixture` if wanted), and in c3x_smoke.sh `slim` return slim_ckpt.py's rc (`set -o pipefail` or `${PIPESTATUS[0]}`). Neither touches c3x.patch, the card or the code proof. Re-run the builder's fixture check plus the missing-slim case.

**B2 (CLOSED). The launch request on disk was not the pinned one.** (E) LAUNCH_REQUEST_c3x.md is e78278d2 (mtime 18:14:42.95), not 35321335 as pinned in log.md 17 Nov 18:14. Closed by the lead's message after my report (about 18:29): the builder's last report of 18:15 added one statement (why 600 steps of the path smoke are enough: 301 iterates in the window, the averager copies at its first iterate and blends from the second, the check requires swad != raw); the lead pins e78278d2 and the builder changes no file after that report. That statement is in the version I reviewed (section 3, (b) PATH) and agrees with what I measured: P3 on my fixture (window 4 to 6: n 3; swad != model) passed, and the check's `swad != model` item is real. E 18:29: request still e78278d2, the other 21 files unchanged, evidence/smoke_fixture_check.sh 358d708e. When the request is next edited (B1), also correct the stale text in N1.

## Notes (not blocking)

N1 (E, S) Stale text that contradicts the 17:35 rulings:
- Request section 5, "Known limits (4) The PATH smoke has a frozen encoder (probe cos 1.0)": wrong since Q2 (freeze 100, ramp 100; the check requires cos < 1, and on my fixture the jsonl cos was below 1 while the log printed 1.0000).
- The c3x card's `memory.source` (c3x.patch l.81 and l.165, into the commit) and c3x_make_jobs.py l.9-10 still give the superseded Q4 rule "job gate = peak + 2,048 if the peak is above 8,952". The smoke card's `memory.source` (l.76) says "the PATH smoke measures nothing for the gate", contrary to Q1 (P is the max over both smokes; the check script does use the path peak). The tools implement the 17:35 rule correctly; only the texts are old. Changing the card text changes 926782de, the patch md5 and the pins: the lead's call whether that is worth a re-cut.

N2 (S) The ruled job gate is not tied to the smoke result by the tools: `c3x_queue.sh build` uses `GATE=${GATE:-11000}` (l.27); if the lead forgets `GATE=<G>` the list carries 11,000 instead of max(11000, P + 2,048). Practical effect on 48 GB A6000s is small (strict lanes have at most 4 GB of others; shared lanes need 20 GB free anyway), but a `build` that requires an explicit GATE (or reads the RULE line of the smoke check output) would close it.

N3 (E) c3x_verdict.py: a null relF1@2 delta or CI end in a headline or secondary contrast stops with a Python TypeError (rc 1, no file written; a refusal, but not "in plain words"); a NaN CI low in a secondary contrast is silently labelled "loses" (conservative direction). Neither can change a verdict to a wrong pass.

N4 (S, E sizes) Disk: the request says disk guard 4 will "HOLD new starts"; a HOLD in c3x also stops the dumps of finished c3x runs (cq.sh chain_after waits on HOLD), so finished runs wait undumped and unrelayed until space is freed. The `.swad` dump dirs that c3_f81_list.sh leaves on cv02 (0.13 GB each, E: c3s_swad_v11_f0_s5.swad 131M) are not in the 1.03 GB per run "stay" figure: about 3.3 GB more for 25 runs. The rest of the estimate matches cv02 (E: c3s_swad latest.pth 940 MB, slim 209 MB, best 104 MB; c3h latest 335 MB, best 84 MB). The user's cv02 disk decision (log 18:08) is still open; `arm` refuses below the need without DISK_OK=1, which is right.

N5 (E) Stop paths not written down:
- c3x_commit.sh: if `git commit` fails after `git add` (I hit this on a scratch clone without a git identity), the three files are staged; the header's `rm` alone leaves `AD` entries and the next run still refuses. Recovery needs `git reset -q -- <the 3 files>` before the rm. The real worktree has user.email set (E), so unlikely.
- A refused `arm` (cq.sh fails at arming) leaves session bench_q_c3x with its gpumem window alive and the queue dir used; a new attempt needs that session ended and a new queue dir or IO. Not described.
- Smokes: MAXH=6 h for logger and guard; if the smoke waits more than 6 h behind LOSO-2 / w2a3 / the udev TTA waiter, the queue sets HOLD (safe, nothing starts); a retry needs a new Q (`place` refuses an existing one). Not described.

N6 (S) Pass criterion: P (max over the memory smoke and the path smoke, the latter with BN re-estimate and final evaluation) is compared with the plain HRNet peak of a 300-step smoke without evaluation. If evaluation is the peak, a spurious FAIL is possible; the error is in the safe direction (the lead looks).

N7 (S) The commit adds a third file, tests/test_bench_c3x_card.py, beyond "the card and its cv02 variant" (C3 wording); accepted by the lead at 18:14; not reachable from training or dumping (E, code proof (3) and (4)).

N8 (S) The one-training-queue rule is enforced at arming only. After c3x is armed, any later re-arm or rescue of a c3all3 *training* (cq_rescue.sh only dumps, E) would have to pass the same qscan rule by hand.

N9 (E, trivial) c3x_commit.sh's last line says "request section 4 step 3" for the smokes; they are step 4.

## What I verified (E unless marked)

Attack 1, one training queue, one training run per GPU:
- cq.sh (14d33b80) writes `cv02 q: all jobs dispatched; waiting` once, after the main loop over jobs.txt (l.295); after it only chains (dump, slim, RUN.md5) and `wait` run; no other script writes that string (grep of bench/q/cv02 and c3lane). A HOLD keeps the main loop spinning (no dispatched line); a HOLD set at the last job's live check exists after the line and `arm` refuses on any HOLD in any queue dir. Skipped lines are skipped, never started. cq_setup.sh refuses a non-empty launch.log, so c3all3 cannot be re-armed in its dir. cq_rescue.sh starts only dumps.
- `arm` requires the c3all3 line (grep rc, ssh failure refuses), then qscan over every live queue dir (MAXC 0 / dispatched / fixture-only, else CAN_START refuses); the builder's queue test covers not-dispatched, a CAN_START queue, a HOLD and the disk need (24/24 in evidence; read, not re-run).
- Lanes: "ours" in cq.sh is this queue's PIDs only, so c3all3's (or any lab member's) processes on the shared login count as user `cv02`; a strict lane refuses a GPU where they hold > 4,096 MiB, and a shared training lane refuses any GPU where our own login is above 4,096 MiB (`"$ME":*`). LPG 1 counts c3x's own open lanes (.gpu without .end), so c3x cannot put two of its own runs on one GPU. The only gap I see (S): a c3all3 run in its first seconds below 4,096 MiB; c3all3 has finished dispatching before `arm`, and its last start passed its live check (config and startup line) before the dispatched line, so this window is closed in practice.
- cv02 now (E 12:46 UTC): c3all3 alive, MAXC 8, dispatched 0, 15 of 59 started; c3all, c3all2, c3base, c3hrnet alive with MAXC 0; no HOLD; 8 x RTX A6000; /tmp 72 GB free; diskguard3 up. c3x_check.sh live: 14 OK, 0 FAIL, 7 SKIP, `c3all3 has NOT dispatched all its jobs: c3x must not be armed yet`.

Attack 2, card and code:
- c3x.patch applies to 852ed5c; the three files have the pinned md5s (926782de, a16ad31d, 501a6f95); tree 4cc92a275957f0d3c57311962c4b0b84f3c06f0c (both by my own apply-and-commit and by running c3x_commit.sh on a scratch clone).
- `diff` HRNet card -> c3x card and PF card -> swad card: the same 8 opt lines, weights_key model -> swad_bn, the same 6 readouts; the rest is name, papers, memory, diff_ref, notes and the added header. `bench.cards diff` of both pairs: the same 8 keys. `bench.cards opts` for seed 7, cv5v3 f2: c3x opts minus the 8 opts == HRNet opts. cv02 variant differs only in the weights path; cvcard.py rc 0; validate OK.
- `git diff --name-status 89b9ea5 X` = exactly the 9 paths; c3x_codeproof.sh on my clone (REPO, OUT in scratch, CV02=1): 0 FAIL, cv02 bench_89b9ea5 CODE.md5 = stage copy (7cde26e4), 39 / 19 repo modules at start of train.py / bench_infer.py, none of the 9. bench_wt_final and bench_wt_c3s share one repository (.git common dir), so run_read's C3X check can see X.
- pytest on the patched tree: 27 passed.
- c3x_commit.sh on a scratch clone: wrong md5 refused; right md5 commits 3 files on 852ed5c with tree 4cc92a27; second run refused; wrong branch refused (and N5).

Attack 3, smokes:
- c3x_smoke.sh arms only through bench_setup.sh (gpumem 1 s, auto-stop guard, bench_chain.sh) of the worktree at X; bench_q.sh takes the shared flock gate and the outside wait; bench_lib.sh PROTECT default 6206, `outside` excludes it, the guard picks only verified PIDs of this queue's job names. Gaint now (E): GPU 32,623 MiB, finllm 6206 at 5,876 MiB, two LOSO-2 runs at 6,826 MiB.
- Smoke card = c3x card with exactly the 6 ruled values (`bench.cards diff`); validates; gate 11000. log_every 50 (configs/base.yaml) gives a `PF encoder lr` line at step 50 (frozen) and at 200 (first probe).
- Check script on my CPU fixture: positive 0 FAIL, RULE line `P = max(9700, 9750) = 9750; job gate = max(11000, P + 2,048) = 11798` (arithmetic right). My tampered copies each FAIL at their point: dump .swad line missing; BN re-estimate line missing; final save line missing; WAVG line missing; probe lines missing (4 FAIL); path peak missing; path rc 1; step lines missing (2 FAIL); an `inf` in a probe log line. Missing slim.pth: SKIP, rc 0 (B1). The regexes match real cv02 lines (E: dumped ... key swad_bn, step 20000; WAVG; saved latest.pth; enc_probe.jsonl format) and gaint queue lines (trained ... rc=, config OK, startup line OK).

Attack 4, read and verdict:
- c3x_verdict_test.py: 41 of 41. My own 17 synthetic cases (built on the test's base document) all follow the ruled text: delta exactly M with CI low > 0 passes; CI low exactly 0 fails the headline; secondary CI low exactly -M gives "loses"; secondary delta exactly M with CI low > 0 everywhere gives "adds"; guards at their inclusive bounds (inactive = -M, mIoU = -M, width 0.85 and 1.15, false alarm 1.5 x) pass; a source with n 40 is judged, n 39 is not; carry by COMBO.swad when only per-source widths of COMBO fail and COMBO.swad is clean; no carry if COMBO.swad also fails a width or COMBO fails a pooled width; the final-model rule uses the carrying readout (COMBO "loses" against SWADBN but COMBO.swad "no loss" -> candidate when carried; carried but COMBO.swad "loses" against HRNET -> not candidate); missing run, duplicate run id, wrong A/A spec refused; null and NaN as N3.
- run_read_c3x.sh: c3x_read_test.sh 12 of 12 on my clone; bench_read_w1.py matches arms with re.fullmatch (w1read.py l.64), so COMBO does not swallow the `.swad` dirs; relayed manifests now (c3base 34, c3hrnet 13, c3swad 1): one device (RTX A6000), one writer (…6f8b1836), revision 89b9ea5, set_kind open, fp32; contrast names in the builder's mechanics read are "COMBO - HRNET" etc., as the verdict looks them up.

Attack 5, relay and disk:
- c3x_relay.sh: B = XB (not bench_89b9ea5, refused), ^c3x_, N 25, the reviewed relay_w1c.sh 74a2ec3d of the stage copy; the running relays read bench_89b9ea5/runs and ^c3_ / ^c3h_ / ^c3s_ / ^r2_ do not match c3x_. c3x_relayguard.sh and diskguard4.sh differ from their reviewed models only in names, list, log and stop file (E diff). Gaint free 101 to 114 GB (E).

## Not verified

- Anything on a GPU (both smokes, peaks, the queue on cv02).
- The `render` step on cv02 (it writes there); I checked the render claim only through the card opts equality above and read c3x_rendercmp.py.
- c3x_queue_test.sh was not re-run (needs a copy of cv02's DATA DEPLOY.md5); I read its cases and its evidence (24/24).
- The relay of a c3x run and c3_f81_list.sh on XB (reused, reviewed tools).
- c3x_make_card.py (the card is pinned by md5 in the patch; the generator is not used at launch).
- What changed in the request between 35321335 and e78278d2 beyond the lead's account (no copy of 35321335 exists; B2 closed on the lead's statement).

## For round 2

Changed files only: smoke/c3x_smoke_check.py and smoke/c3x_smoke.sh (B1), LAUNCH_REQUEST_c3x.md (new md5 for the B1 change; N1 text); c3x.patch unchanged unless the lead wants the card text of N1 corrected. I will re-run: the fixture check with the missing-slim and failed-slim cases, the builder's five negatives, the md5 table.

---

# Round 2 (17 Nov 2026, 18:48 to 18:57 IST): PASS

Fix round 2 by the builder (report 18:42 and grep addendum; the lead's checks at 18:48). Same limits as round 1: CPU at nice 19, at most 8 threads; nothing on a GPU; cv02 read only (two `cat` reads: bench_data/DEPLOY.md5 and c3all3/jobs_rendered.txt, the inputs of the queue test); no file of the builder and no worktree changed; no commit, no push; my clones, fixture and test dirs in my session scratch, removed at the end. Processes I started: one CPU fixture (PID 2072088, ended by itself rc 0) and the builder's queue test. The test's first run aborted because one input was missing (RCMP), leaving its 5 `sleep 1800` stand-ins. I stopped them by their recorded PIDs (queue.pid files of the fake tree, args checked = `sleep 1800`). The second run ended its own stand-ins. 0 left (E 18:55).

## Pinned set (md5 on disk 18:48:26 and 18:55:58, unchanged; = the lead's table)

| File (T/harness) | md5 | | File | md5 |
|---|---|---|---|---|
| LAUNCH_REQUEST_c3x.md | 25578e19 | | c3x/c3x_make_jobs.py | 2da3825d |
| c3x/c3x.patch | edd16aec | | c3x/c3x_rendercmp.py | a4fca225 (unchanged) |
| c3x/c3x_make_card.py | 67a68fbe | | c3x/c3x_queue.sh | 2b4fe313 |
| c3x/c3x_commit.sh | 9c5e3a61 | | c3x/diskguard4.sh | eb929c57 (unchanged) |
| c3x/c3x_codeproof.sh | 5e78fb44 (unchanged) | | c3x/c3x_relay.sh | b3bc1db9 (unchanged) |
| c3x/smoke/c3x_smoke.sh | c25ca2e1 | | c3x/c3x_relayguard.sh | c221e73a (unchanged) |
| c3x/smoke/c3x_smoke_check.py | ba38cd21 | | c3x/run_read_c3x.sh | 060e24a2 |
| c3x/smoke/c3x_smoke_card.py | 552c7eb5 | | c3x/c3x_verdict.py | faa2a961 |
| c3x/smoke/smoke_c3x_hrnet_swad_path.yaml | 7e74f668 | | c3x/c3x_class_guard.py | c9022bcc (unchanged) |
| c3x/c3x_check.sh | 9cb706bb | | c3x/c3x_verdict_test.py | 9d8efbf3 |
| c3x/c3x_read_test.sh | 28b5b017 (unchanged) | | c3x/c3x_queue_test.sh | 75cb9301 |
| c3x/evidence/smoke_fixture_check.sh | 9c2af38d | | | |

Patch contents: card 98f152de, cv02 variant d7b20708, test 501a6f95; tree of X c860f1bc243ff5262f8c23ffb1e551cfaea5ea79; commit with `PATCH_MD5=edd16aec962125832737e6924281e6de`. Worktrees (E 18:55): bench_wt_c3s 852ed5c, 0 tracked changes; bench_wt_final 89b9ea5, 0 tracked changes.

## Round 1 items

- **B1 closed (E).**
  - On my own new CPU fixture of the path smoke (real train.py of the re-cut tree with the new smoke card; the builder's evidence/smoke_fixture_check.sh run against it with only H set; my negatives on top):
    - check before the slim step: `FAIL P7 slim ... # 1 FAIL`;
    - `c3x_smoke.sh slim` rc 0 with the real slim_ckpt.py; a second slim refused (slim.pth exists);
    - positive: 0 FAIL, rc 0;
    - slim.pth removed: FAIL P7;
    - slim.pth without the key swad: FAIL P7 (`dumped keys missing: ['swad']`);
    - a failed slim step: rc 1 with `SLIM FAILED (slim_ckpt.py rc 1 ...)`;
    - `c3x_smoke.sh check` returns the check's rc (1 on a failing check) and keeps smoke_check.out.
  - No `say(None` is left in c3x_smoke_check.py (grep count 0), so nothing can SKIP.
  - My round-1 negatives on the new script each FAIL at their point: dump .swad line, BN re-estimate line, final save line, WAVG line, probe lines (4 FAIL), path peak, path rc 1, step lines (2 FAIL), inf in a probe log line.
  - New negatives: plain HRNet peak missing; the .swad dump manifest removed (separate dumps copy). Both FAIL.
  - The builder's five round-1 negatives also FAIL.
- **B2 closed** (round 1; request now re-pinned at 25578e19 by the lead).
- **N1 closed (E).**
  - Fresh apply of edd16aec on 852ed5c (my clone, c3x_commit.sh itself): tree c860f1bc, files 98f152de / d7b20708 / 501a6f95.
  - `diff` HRNet card -> new card is line for line the round-1 diff except the `memory.source` line, which now states the 17:35 rule: gate max(11,000, P + 2,048) over both smokes, pass criterion 1,024 MiB, nothing armed before the lead has looked.
  - `bench.cards diff` HRNet -> new card: the same 8 keys. cv02 variant: 2 differing lines (weights path); cvcard.py rc 0; validate OK.
  - c3x_make_card.py on an archive of 852ed5c regenerates 98f152de and d7b20708; c3x_smoke_card.py on that card regenerates 7e74f668.
  - Smoke card vs new card: the 6 ruled values plus name, header, source and notes.
  - make_jobs docstring states the 17:35 rule. No "8,952", "frozen encoder" or "measures nothing" is left in the request, the scripts or the smoke files.
  - Old pins: grep of H (without draft_1711/ and evidence/) and the request for 926782de, a16ad31d, 4cc92a27, 602178f0, 0f444c68, 2a4edf8b, 4eac38ea, b137f4dd, d134edd6, fcf9a1c7, 4e80bf54, f7d90d01, f5d605ab, 3bc083d4, 08ec8abe, 99c1bf23, 4c8aa8eb, 35321335, e78278d2: only in the request's sentence that lists them (section 10). New pins are present in c3x_commit.sh, c3x_check.sh, c3x_queue.sh (PINS: card and cv02 variant new, the 8 queue-code pins as in round 1), smoke/c3x_smoke.sh (SC_MD5 7e74f668, TREE c860f1bc) and run_read_c3x.sh (TREE).
- **Code equality after the re-cut (E).**
  - pytest 27 passed.
  - c3x_codeproof.sh on my commit: 0 FAIL, same 9 paths, cv02 B89 CODE.md5 = stage copy 7cde26e4.
  - c3x_read_test.sh with the new commit: 12 of 12.
  - Job list at gate 11000: md5 4a6873b4, byte-equal to round 1, so the job lines do not depend on the card text. That also means the render compare of round 1 still applies; rendercmp is unchanged.
- **N2 closed (E).**
  - `build` has no GATE default. It refuses without GATE, with GATE different from the RULE line's job gate, and without the smoke check file.
  - The RULE pattern parses the real check output: 11798 on the fixture.
  - c3x_queue_test.sh: 27 of 27 (T1 7 build cases incl. the 3 new; T2 XB pins with the new card; T4 need 54 GB with .swad, DISK_OK, real cq_setup.sh of my XB archive).
- **N3 closed (E).**
  - c3x_verdict_test.py: 50 of 50.
  - My 17 round-1 cases on faa2a961 give the same verdict, final-model sentence and used labels as on f7d90d01 for every case that ran. The rule did not move: delta = M passes; CI low = 0 fails; secondary CI low = -M loses; inclusive guard bounds; n 40 judged, n 39 not; all three carry variants; missing and duplicate run refused.
  - The two cases that crashed or said "loses" in round 1 now refuse in one line naming the contrast: null delta in the headline; NaN CI low in a secondary.
  - New cases of mine, all one-line refusals with rc 1: inf CI end in a secondary; NaN M(inactive); a string CI low; a bool delta; a null CI low under --mechanics.
  - A null per-seed value and a null summary mean in the information line print n/a with no effect on the verdict (rc 0).
- **N4 closed (E).**
  - Request section 5 and `arm` now include the 3.3 GB of .swad dirs: need 54 GB with 2 open c3all3 runs (queue test T4).
  - The text says a HOLD also stops the dumps of finished runs.
  - c3x_check.sh INFO shows 51 GB without open runs.
  - The deletion question is with the user (lead).
- **N5 closed (E).**
  - Commit recovery: on a scratch clone without a git identity, c3x_commit.sh refused with `commit failed` and the three files staged. The header's `git reset -q -- <3 files>` then `rm` gave 0 tracked changes, and the next run committed tree c860f1bc.
  - Refused arm: cq_gpumem.sh of 852ed5c stops on Q/GPUMEM_STOP (l.20). The moved-aside dir has no live queue.pid and no HOLD, so qscan and the HOLD check ignore it. IO keeps render_cmp.out for the next arm.
  - Smoke beyond MAXH: queue.pid is bench_q.sh's own PID; killing it ends bench_chain.sh's phase 1 without dumps.

## New notes, round 2 (not blocking)

R2-N1 (E) `c3x_queue.sh build` accepts a smoke check file that ended with a FAIL, as long as its RULE line is present. A file whose last line is `# 1 FAIL: pass criterion` (RULE 12948) built a 25-line list at gate 12948, rc 0. The script echoes that last line, the check itself exits 1, and the ruling leaves that case to the lead's look. To make the tool enforce it: refuse unless the last line is `# 0 FAIL`, with an explicit override for the lead.

R2-N2 (E, tests only) c3x_queue_test.sh's usage line names only CLONE. It also needs DATA_DEPLOY, C3R and RCMP. A missing RCMP aborts it at T4 (`set -u`) after it started its 5 `sleep 1800` stand-ins, which are then left running. They must be stopped by hand from the fake tree's queue.pid files, as I did.

R2-N3 (S) Smoke beyond MAXH: if the memory smokes already ran before the HOLD, `arm` on the new Q refuses because experiments/smoke_c3x_mem_* exist. The stop path should say: run `clean` (after the session has closed) before `place` and `arm`. The refusal itself is safe.

Round-1 notes N6 to N9 stand as written (not on the lead's list).

## Not verified in round 2

- Anything on a GPU.
- The render on cv02, and the builder's gaint render re-run with the re-cut card (I relied on the byte-equal job list and the unchanged rendercmp).
- c3x_check.sh with X and XB set (my commit exists only in my clone).
- The relay of a c3x run.
