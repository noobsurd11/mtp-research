# Review of the T3b launch package (E1 opening #9), round 1

Round 1 (22 Nov 2026, 00:50 to 01:15 IST): **FIX, two blocking items (B1 relay, B2 script pins).** Both fixes are in H3 only;
the rule, the lists and K need no change (S). Pinned to the md5s in section 1.

Reviewer: t3b_reviewer2 (independent; I did not build this package). Tags: E = shown by my own command (output quoted below or
in my scratch), S = judgement. T = /home/yugma/mtp/research/team_2026-11-12_frontier, H3 = T/harness/t3b, K = cba7fbd.
Limits kept: gaint CPU only, nice 19 (at most 6 + 4 threads at once); no GPU; nothing registered, staged or armed; cv02 read
only (two `ssh -n -a -o BatchMode=yes` calls: df, ls -d, md5sum -c of F2B's CODE.md5, du, ls of one checkpoints dir,
nvidia-smi, queue dir flags); no file of H3, K or any worktree changed (K worktree: no file newer than my session start, E
`find -newer`; bench_wt_openg / bench_wt_open status clean); K exported by `git archive` into my scratch
/tmp/claude-1003/-home-noob/149c5b71-58ef-4f40-bd7c-5742a5e4643f/scratchpad/t3b_review; smokes in
/home/noob/work/bench_int_io/t3b (removed by the scripts). **No E1 or test50 pixel, label or prediction was opened, decoded or
summarised**: I read stem lists, the draft folds file, ledger and log text, relay .ok / relay.log lines and RUN.md5 hashes of the
3 zero-shot units (counts and md5 only), and file names under bench_relay/fin2 and bench_reads/open_final. finllm_chat.py
(PID 5104) untouched.

## 1. Pins (all E: md5sum)
| Item | md5 | = request section 12 |
|---|---|---|
| LAUNCH_REQUEST_t3b.md | 6cd81eaa767701d451e9ebc481ef75ea | (the request) |
| T3B_RULE.md | 8e6df3d23c43074f0c472bb45f0b1aa5 | = (and = RULE_PIN in t3b_register.sh) |
| lists/LISTS.md5 | 5c86318a0d3c628bf3f9711fe7081fb5 | = ; `md5sum -c` of the 15 list files OK |
| K | cba7fbdf5df1579d6efb1168eb292e637bc9fad6, tree b653389febe6fda63ce87e589859aa8605eef51f | = |
| t3b_make_lists.py | 47b1dbc64eee6f14d9c580da6005d495 | = |
| t3b_make_jobs.py | 84649917b572e2201215cb8854de85ed | = |
| t3b_rendercmp.py | ed18484e56878a481685516d86f201d0 | = |
| t3b_register.sh | 4e7b002dfd3fe74e1014d1ba73be684f | = |
| t3b_queue.sh | 00ce598f352caf94dfeeb0c3f1704a24 | = |
| diskguard8.sh | 0fe96ad9b0208bf6381f2bc5ee7b60b4 | = |
| t3b_relay.sh | 1696373c4148cfa9ab69fa0bacb8371f | = |
| run_t3b_read.sh | 3fc6df2f028225dd48697392c404247d | = |
| t3b_verdict.py | 7de5bcb60bbe4600fd8c6b1e8062df58 | = |
| t3b_verdict_test.py | 4a88192c93e9977569cfacc57f145ea3 | = |
| t3b_smoke_synth.py | b69ef1bbe8c1bc8b4660ccaca15e56ab | = |
| t3b_chain_smoke.sh | eee81ea1ed1b498e6802ce95b9395c05 | = |
| t3b_render_smoke.sh | fef0c79341e8c2e30a5f3072f2660eb6 | = |
| t3b_train_smoke.sh | b999f9969ae6f718de1be271151b0aea | = |
| t3b_testmode_guard_test.sh | e544e28353b9013d99c5fb096a16973b | = |
| t3b_codeproof.sh | 2c9a073d69f8cdf4757a578560f930dd | = |
| t3b_set_pins.py | 54f4ce1bb3e95a3fac81f13bfe80dfdf | = (not in the procedure) |
| evidence/MD5_evidence.txt | 78836707ec5c6fa94631ade3a5e2aac7 | = ; `md5sum -c`: 64 of 64 OK |

## 2. Blocking items

**B1. The dump relay relays the 33 training units and stops before any dump; unstage can then never pass (E).**
- Code: t3b_relay.sh runs relay_w1c.sh (74a2ec3d) with `B=$KB ... N=$N NAMES_RX=.` in both modes. relay_w1c.sh lists every
  `$B/runs/*/RUN.md5`, relays each name matching NAMES_RX, and ends when `ls RD/.ok | wc -l >= N`. When the dump relay
  starts (procedure step 11), KB/runs already holds the 33 training RUN.md5 (q1_done requires them).
- My simulation (stub ssh running each command locally, synthetic B with 33 training + 30 dump RUN.md5, the reviewed
  relay_w1c.sh, N 30, NAMES_RX=.): `RELAY ALL DONE: 63 of 30 runs relayed`; `units relayed: 63; of which dumps: 30; training
  units: 33`. With the real order (training units ready at the first poll, dumps not yet) the first poll relays the 33
  training units, `done_n 33 >= 30`, the relay ends with no dump relayed; a RESUME=1 run ends at once for the same reason.
  The same run with `NAMES_RX='\.e1t3b_f[0-4]$'`: `RELAY ALL DONE: 30 of 30 runs relayed`, `dumps: 30 training: 0`.
- Consequences: run_t3b_read.sh refuses (dumps not relayed); `t3b_queue.sh unstage` greps `RELAY ALL DONE: 30 of 30`, which
  cannot match `33 of 30` or `63 of 30`, so DS (E1 images), DT (E1 labels) and the 30 dumps stay on cv02 until a hand fix.
  Also: nothing gates t3bopen on the training relay, so a training relay still polling would take dump units into RD1; and
  no step checks that the 3 deployable units (the deliverable) reached RD1.
- Fix wanted: (a) per-mode NAMES_RX in t3b_relay.sh, train `^t3b_(all|half)_f[0-4]_s[5-7]$|^t3b_deploy_s[5-7]$`, dump
  `^t3b_(all|half)_f[0-4]_s[5-7]\.swad\.tta_d4\.e1t3b_f[0-4]$`, quoted so the tmux command string keeps them; (b) q1_done (so
  render2, place2, arm2) also requires RD1/relay.log `RELAY ALL DONE: 33 of 33` and, for t3b_deploy_s5..7, RD1/.ok present and
  a gaint `md5sum -c` of the relayed RUN.md5; (c) a relay smoke through a stub ssh with both kinds of RUN.md5 present, showing
  33 units in RD1, 30 in RD2, `30 of 30`, and unstage passing on that RD2.

**B2. Between review and use only the rule, the job maker and the lists are pinned; the read, the verdict, the queue and the
relay scripts are not (E).**
- Code: t3b_register.sh checks RULE_MD5, MAKE_MD5 and LISTS_MD5; REGISTERED.txt records no md5 of t3b_queue.sh,
  t3b_relay.sh, run_t3b_read.sh, t3b_verdict.py (the decision: M, CONFIRMED rule, guards), t3b_rendercmp.py or diskguard8.sh.
  run_t3b_read.sh checks the rule's md5 against the registration but neither its own nor t3b_verdict.py's (both are only
  written to MD5.txt after the verdict). t3b_queue.sh (SHARE_TRAIN 20480, MAXC rule, unstage order) and t3b_relay.sh check
  nothing about themselves. The lead's requirement 7 ("pins every script md5 ... refuses on any mismatch") is not met.
- Why it matters (E, my synthetic end-to-end, section 4 check 9): swapping the ALL and HALF record lists in the read call
  gives `CONFIRMED; Delta +0.0407` (HALF's effect) with no refusal; an unreviewed edit of run_t3b_read.sh or t3b_verdict.py
  would change the outcome silently.
- Fix wanted: t3b_register.sh holds the reviewed md5 of every H3 script used after it (t3b_queue.sh, t3b_relay.sh,
  run_t3b_read.sh, t3b_verdict.py, t3b_rendercmp.py, diskguard8.sh; the rule, t3b_make_jobs.py, LISTS.md5 as now), refuses on a
  mismatch, and writes a `scripts` line into REGISTERED.txt; t3b_queue.sh, t3b_relay.sh and run_t3b_read.sh refuse, before any
  write, unless their own md5 (for the read also t3b_verdict.py's) is the registered one. Suggested in the same edit:
  t3b_verdict.check_read also checks the arm run ids (ALL = t3b_all_s5..7.oof, HALF = t3b_half_s5..7.oof, ZS = the three
  fin_hrnet_swad_v11_pool_s5..7.swad.tta_d4.e1_106).

Round 2 wanted: the diffs of the fixed H3 files, new md5s, the relay smoke of B1(c), a rerun of the guard test and of the chain
smoke (or the parts the fix touches). Nothing in K, the rule or the lists should change.

## 3. Non-blocking notes
- **N1. The stated repair path for a failed run is not implementable as built (E code).** A training with rc != 0 gets no
  slim / RUN.md5 and the queue goes on (cq.sh chain_after); q1_done then refuses, so t3bopen is blocked (fail closed, as the
  rule says). But "a re-run of exactly that line in a repair queue" cannot pass: cq.sh skips an existing experiments/<name>
  (line 379), and q1_done counts `trained <n> rc=0` only in Q1's launch.log. Any failure therefore needs new H3 code and a
  review. Consider adding now a reviewed repair mode (a `--resume` line, cq.sh's RES kind, in a registered repair queue that
  q1_done accepts). A deploy-run failure also blocks t3bopen, though the read needs only the 30 fold runs (consistent with
  the rule).
- **N2. Verdict test gap (E).** My mutant M9 (primary taken from the fixed-model interval instead of the seed-aware one)
  passes all 20 tests, because the test documents set fixed = seed_aware. The code is right; add a test with different
  fixed and seed-aware values.
- **N3.** t3b_verdict.py does not assert fa_cells = 74 (the crack-free count of the rule); it only prints it. Add the check.
- **N4. TEST_MODE: PINS_FILE is sourced after the path guard in run_t3b_read.sh (E).** A PINS_FILE that sets
  `BENCH_EXT=/home/noob/work/el_f1/reports/f1/__no_such__` passed the guard (`PINS_FILE sourced: BENCH_EXT=...`, then the
  ordinary refusal `no .../REGISTERED.txt`). Needs a hand-written file, so low risk; re-run tm_in on every path after sourcing,
  or allow only W_K / W_G / K / F2 assignments.
- **N5.** A TAG read is not labelled as a repeat in run.log or verdict.txt, and TAG is not validated (`TAG=../../tmp_x` gives
  out `/home/noob/work/bench_reads/t3b_open9_../../tmp_x`, E SHOW=1). Restrict TAG to `[a-z0-9_]+` and print "REPEAT, not the
  registered read" in the verdict header.
- **N6.** No step checks that ledger row #9 is written before build / stage; the lead adds it by hand (as opening #8).
  Cheap check: build and stage grep e1_openings.md for a `| 9 |` row holding REG_MD5.
- **N7.** t3b_register.sh checks the ledger header's column count after IO is written and made read-only; a refusal there
  would leave a registration that cannot be redone. It passes today (E: header 9 fields, row 9 fields).
- **N8. If map_e1 refuses on real data (check 4):** the build stops after the registration, nothing reaches cv02, #9 stays
  "registered, NOT opened"; IO/data is left half written and `build` refuses a rerun; a fix needs a new K, a review and a
  dated amendment. Risk is low (opening #8 scored all 106 cells, so every kept px is < 24, E); a value outside 0..29 / 255 on
  an ignore px would still refuse. Suggest: decode and check all 106 labels in memory before writing anything.
- **N9. Wording (rule section 6, t3b_labels.py).** With every kept px asserted < 24 and every ignore px set to 255, the class
  map changes no output px at all; "acts only on ignore px" overstates it. The label equals where(ignore == 0, mask, 255).
- **N10. Deliverable format.** The relay keeps slim.pth (swad_bn, swad) + LATEST.md5; latest.pth stays on cv02 /tmp (a shared
  machine). bench_infer reads checkpoints/latest.pth only. If the user wants the 3 deployable models runnable by bench_infer
  from the NAS, also relay their latest.pth (3 x 756 MB) or document loading the swad key from slim.pth.
- **N11. Wall time (E cv02 nvidia-smi 01:0x):** only GPU 3 was under 4096 MiB, so MAXC would be 1 and 33 runs take about 63 h
  unless the lead raises Q1/MAXC. The request's 9.5 h assumes 8 free GPUs.
- **N12.** Only bench_open_read, bench_score summary and derived refuse trained_on_e1; other record readers (bench_headres,
  bench_read_w1, bench_udev_read, ...) do not check it (E grep). Keep T3b records under bench_reads/t3b_open9 only, or add
  the check later.
- **N13.** DT/files holds the E1 training labels of all 106 cells (each fold's held-out labels present but unlinked) on the
  shared cv02 login for the whole training; needed by the deploy root; removed at unstage. S: acceptable since E1 becomes
  training data at registration; worth one line in the disclosures.
- **N14. The builder's `head -3` of ext117/manifest.csv (check 12).** S: it does not matter. It showed crack / inactive px
  counts of 2 cells; the draft folds file already holds crack px of all 106 cells and was used openly by design; no list,
  recipe or threshold depends on it (lists rerun byte-equal from the draft file alone, E). PNG header reads (mode, size) were
  also made by the opening #8 reviewer (REVIEW_OPENING.md round 1). Nothing else in H3 or evidence reads E1 / test50 pixels or
  predictions before registration (E grep of H3 and evidence for ext117 / masks / ignore / bench_relay / manifest.csv: only
  the defaults and the guard test's `__no_such__` paths).

## 4. Checks, what I reran, exact output
1. **Rule vs design: PASS (E text, S).** Arms ALL / HALF, seeds 5, 6, 7 (user 15:01 "3 seeds is fine"), C2 recipe, primary P =
   mean over seeds ALL OOF minus ZS, relF1@2 OP-A, 106 cells, seed-aware two-stage 71-cluster bootstrap, 2,000 draws, M 0.010,
   CONFIRMED iff Delta >= M and lo > 0; G1 false crack px on the crack-free cells <= 1.5 x ZS (inclusive), G2 mIoU-R13 >=
   -0.010; width printed only; beside rows; separation; 3 deployable models never scored; ledger bullet "E1 is training data
   for T3b models from this date" (t3b_register.sh). Order rule met (ledger row 8 "opened 21 Nov 11:25:30 to 12:06:09", no row
   9 yet, E). Nothing is chosen on E1 outcomes: the half uses crack px counts from the draft file (labels, not predictions),
   as the proposal's folds do. No pool image id is an E1 image id (E: 354 pool ids, 71 E1 ids, `comm -12` empty).
2. **Lists: PASS (E).** `python -I t3b_make_lists.py <draft> <stems_eval> <new dir>`: `LISTS.md5 5c86318a0d3c628bf3f9711fe7081fb5`;
   `diff -r` vs H3/lists: `LISTS_BYTE_EQUAL`. My own check: `held-out total 106 distinct 106 max count 1 ==E1 True`;
   `ids 71 ids spanning folds 0`; `folds.tsv == draft k5 True 106`; per fold held-out 22/22/20/21/21, half 42/42/43/42/43 cells
   (whole image ids, inside the training side, E1 order); `strata == draft True Counter({'full': 36, 'halfcut': 33,
   'halfcut+scuff': 29, 'full+scuff': 8})`. The half algorithm is deterministic (no random draw) and reads only the draft
   file's columns.
3. **Roots: PASS (E code + smokes).** bench_make_t3b_roots.py lists and links only train.txt stems (pool 532 + the root's E1
   cells); val = test = the 107-cell monitor (pinned 79816ba6, inside the pool); asserts no held-out or legacy-test stem listed
   or linked, re-read from disk. train.py (= F2) reads masks only as root/masks_v11/<stem> for train / val / test stems; the eval
   ignore fix needs val and test inside train; weight_avg.train_fold_loader reads train.txt only; best.pth is never read by
   bench_infer (latest.pth, key swad). train.py imports only src/ (E grep), so the 117-file training path is closed. Train
   smoke with fold 0's 22 held-out files deleted: rc 0 under K and F2. Deploy root: `t3b_deploy: train 638 (pool 532 + E1 106)`.
4. **Labels: PASS (E code, S).** map_e1: kept px must be < 24 (the scorer's own assert, m0core.cell_stats), ignore px -> 255,
   equality with the scoring view asserted per cell; the builder reads mask and ignore with np.array(Image.open()) like
   bench_score.load_gt (keep = ignore == 0). Failure on real data: N8.
5. **Recipe: PASS (E).** My render smoke: the 33 rendered training lines differ from fin's rendered C2 line
   (harness/final/evidence/render_smoke/rendered.txt, fin_hrnet_swad_v11_pool_s5) only in run_name, seed and data.root:
   `train lines 33, differing from fin C2 (modulo name, seed, root): 0`. Job gates 11510 / 6200, logp 0, readout field swad
   = fin's line. Dumps: `--set e1t3b_f<k> --opening e1_open9_t3b --weights-key swad --tta d4`, no logp, fold model of the same
   fold and seed. Pred is argmax log(p + 1e-12) from bench/tta.py cell_maps with or without --logp (E code), so the ZS dumps
   (made with --logp --ens-member) and the T3b dumps share the decision rule. Code proof rerun: `t3b code proof: 0 FAIL`
   (items 1 to 6, `OK    2: training path byte-equal to F2 (117 files)`); `NEG=1`: `FAIL  2: differs from F2: src`,
   `FAIL  5a: lines removed: scripts/bench_infer.py(-1)`, `t3b code proof: 2 FAIL`. My own negatives on the same 117-file
   comparison: `NEG card steps 20001: FAIL differs: bench/methods`; `NEG configs/supervised.yaml +1 line: FAIL differs:
   configs`; `NEG new file in src: FAIL differs: src`.
6. **Queues: PASS except B1 (E code, cv02 read only).** LPG 1, MAXC <= GPUs under 4096 MiB at arm, SHARE_TRAIN written 20480 and
   checked at arm, never lowered by any step; SHARE_DUMP checked absent; t3bopen strict lanes; q1_done needs t3b's ALL DONE,
   33 rc 0, 33 RUN.md5 and the queue pid gone, so t3b and t3bopen never overlap; t3bopen cannot train (sealed queue refuses
   training lines, render smoke negative). Disk guard 8 = disk guard 7 up to names (E diff). Frozen queues: no H3 step writes
   outside Q1 / Q2 / DT / DS / KB / the render scratch; cv02 now: c3all, c3all2, c3base, c3hrnet alive (pids 1548874, 573285,
   647026, 1142062) with HOLD and MAXC 0. Failed run: N1. Queue PINS: `PINS_OK_vs_K` (22 files); read writer pins
   149e2a63 (K) / a3268638 (G) = the files. cv02 F2B: `F2B_CODE_OK`, 83 tests/ lines in its CODE.md5 (so the DW list's tests
   paths are expected).
7. **Register: FAIL (B2); rest PASS (E code).** Refuses an existing IO, rule / make_jobs / lists mismatch, K or tree mismatch, F2
   or G not ancestors, E1 list or files, opening #8 REGISTERED.txt (E: `4c783a779208979ccbed8c13802950b2`), ZS units (E: for
   s5, s6, s7 `.ok present yes; relayed lines 1; .ok md5 == RUN.md5 md5: yes`). Ledger row and bullet printed, not written
   (N6, N7). Clean shell: `env -i bash` gives `PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`; git
   rev-parse of K's tree, the ancestry check, whoami, hostname, md5sum all work (E).
8. **Relay and keep: FAIL (B1).** relay_w1c.sh verifies md5 on both ends and refuses overwrites (E code, 74a2ec3d; stage copy
   CODE.md5 OK). Unstage order: each dump dir only after gaint md5sum -c of the relayed copy and cv02 md5sum -c, then DS, then
   DT (queues ended); run dirs (models) stay. Keep of the deployable models: B1(b), N10.
9. **Read and verdict: PASS (E).** ZS = the 3 opening #8 C2 units, pinned by .ok / RUN.md5 md5 in reg/zs.tsv, md5sum -c at the
   read, manifest check (e1_open8_final, ens_member, writer G, revision F2, checkpoint = fin2 LATEST.md5; all three fin2
   LATEST.md5 present, E). OOF merge refuses missing / doubled folds, wrong arm / seed / set / list, and asserts the 5 folds
   partition E1. Bootstrap = R's `boot` unchanged (code proof item 6: read.txt byte-equal to R's without --t3b). Verdict tests:
   `20 passed in 0.25s`. My mutants (each a copy of t3b_verdict.py run against the 20 tests): M1 flip the sign `14 failed`;
   M2 primary HALF - ZS `11 failed`; M3 accept a missing seed `1 failed`; M4a M 0.011 `2 failed`; M4b M 0.009 `2 failed`;
   M4c Delta > M `1 failed`; M5 lo >= 0 `1 failed`; M6 G1 strict `1 failed`; M7 FA_X 1.6 `2 failed`; M8 G2 from HALF - ZS `2
   failed`; M9 primary from the fixed-model interval `20 passed` (N2); M10 G1 inverted `2 failed`; M11 G2 strict `1 failed`;
   M12 primary relF1@1 `13 failed`; M13 bootstrap check off `1 failed`; M14 width as a guard `1 failed`. My synthetic
   end-to-end (records with known effects on the real E1 stem list, K's bench_open_read with run_t3b_read.sh's exact
   arguments, --boot 2000, then t3b_verdict.py): positive `independent: ... ALL - ZS +0.1121` / `read.json ALL - ZS delta
   +0.1121 [+0.0977, +0.1262]; n_cells 106 clusters 71` / `CONFIRMED`; null `-0.0054 [-0.0205, +0.0095]` / `NOT CONFIRMED (the
   interval holds 0; Delta <= 0)`; negative `-0.1475 [-0.1634, -0.1313]` / `NOT CONFIRMED (WORSE: ...)`; false crack px x3
   on crack-free cells `+0.0908` / `GAIN, FAILING GUARDS NAMED`; pair reversed (`--pair ALL=ZS`) `refuse: contrast ALL - ZS
   missing`; ALL and HALF lists swapped `CONFIRMED; Delta +0.0407` (not detected: B2). Read once: an existing output refuses
   (chain smoke); TAG repeats: N5.
10. **TEST_MODE guards: PASS with N4 (E).** `t3b_testmode_guard_test.sh`: 24 PASS, `guard test: 0 FAIL`, `IO made by any register
    case: no`, `output folder made by any read case: no`. My attempts: IO `$W/../../../bench_t3b_io_x` -> `REFUSED (TEST_MODE
    guard): ... resolves to /home/noob/work/bench_t3b_io_x, outside /home/noob/work/bench_int_io`; ssh as an exported bash
    function -> `REFUSED (TEST_MODE guard): ssh is not an absolute path`; a scratch ssh symlinked to /usr/bin/ssh ->
    `REFUSED (TEST_MODE guard): .../bin/ssh resolves to /usr/bin/ssh`; production defaults without TEST_MODE -> `REFUSED
    (build): no registration in /home/noob/work/bench_t3b_io`; PINS_FILE bypass: N4.
11. **Smokes: PASS, reproduced (E).** Train smoke: `== T1 (K cba7fbd...): rc 0 in 109 s`, `== T2 (F2 9967d59...): rc 0 in 102 s`,
    both `Labelled: 616 (...)  val: 107  test: 107`, `WAVG BN recal: ... on 616 train cells`, `differing paths: 3 (3 allowed, 0
    not allowed)`, `rc 0`; log equal to the builder's except timings. Render smoke: `render compare: 0 FAIL (33 rendered train
    lines; 33 expected)`, `render compare: 0 FAIL (30 rendered dump lines; 30 expected)`, both negatives refused (`... takes
    only sealed dump-only lines; not starting`, `dump-only extra must be ...; not starting`), `render smoke rc 0`;
    rendered_train.txt, rendered_dump.txt, jobs_train.txt, jobs_dump.txt byte-equal to the builder's evidence. Chain smoke:
    `register rc 0`, `build rc 0 (ROOTS_t3b.md5 f9a4d24b...; 11 roots; CHECK OK ...)`, `stage rc 0`, `T3b dumps: 30 of 30 in 268
    s; manifests marked trained_on_e1: 30`, the 6 negatives refused with no output folder, `read rc 0`, zero-shot re-score
    `IDENTICAL: 106 cells` x 3, 6 OOF records `(22, 22, 20, 21, 21)`, `T3B VERDICT: ... NOT CONFIRMED (the interval holds 0;
    Delta <= 0); Delta -0.0000 [-0.0001, +0.0000]`, `unstage rc 0 (REMOVED_DUMPS 30 ...)`, `dump dirs left 0; runs/*/RUN.md5
    kept 30; DS removed; DT removed`; verdict_synthetic.txt and read_t3b_synthetic.txt equal to the builder's except the
    registration line. The chain smoke's synthetic models predict almost no crack (Delta 0), so it does not test the decision
    wiring; my end-to-end in check 9 does. It also fakes the relays, which is why it missed B1. Targeted pytest in a `git
    archive` copy of K (test_bench_t3b, test_bench_cq_sealed, test_bench_cq_final, test_bench_opening_read): `115 passed, 2
    skipped, 6 warnings in 105.79s`.
12. **Sealed-data hygiene: PASS (S, E grep).** N14.
13. **Cost and disk: PASS (E, S).** cv02 free `71G`; fin_hrnet_swad_v11_pool_s5 run dir `962` MB (latest 755,789,984 B, slim
    168,049,885 B, best 84,154,973 B), so 33 dirs = 31.7 GB; plus DT / DS / dumps < 1 GB and transient checkpoint writes (S, at
    most about 6 GB at 8 concurrent runs): peak under 40 GB, free stays above 30 GB, above the 20 GB guard. Arm floor 55 GB <=
    71 GB free. GPU-h: steps fixed at 20,000; about 110 min per run alone on a GPU (log 21 Nov 06:11), 33 runs about 61 to 63
    GPU-h plus dumps under 1 GPU-h (S); wall time: N11. NAS relay about 5.6 + 0.8 GB (S).

# Round 2

Round 2 (22 Nov 2026, 02:04 to 02:25 IST): **PASS.** B1 and B2 are closed; no blocking item remains. Round 1 text above is
unchanged (md5 ab5eb473 before this section). Same limits as round 1: gaint CPU, nice 19; synthetic data only; nothing on cv02;
nothing registered; no E1 or test50 pixel, label or prediction opened. My scratch probe dir under bench_int_io was removed; the
K worktree is unchanged (HEAD cba7fbd, tree b653389f, `git status --porcelain -uno` empty).

## R2.1 Pins (all E: md5sum; equal to the lead's list of 02:03)
| Item | md5 | Note |
|---|---|---|
| LAUNCH_REQUEST_t3b.md | f97c4ccdbd243a1e3a1e33ac62e41ac2 | section 6b lists the round 1 changes |
| T3B_RULE.md | 0c006d4466f0312f4ca01184ea52a95a | = RULE_PIN of t3b_register.sh. Only change: the N9 line. E: `patch -R` of evidence/rule_edit_round1.diff on the new rule gives md5 8e6df3d23c43074f0c472bb45f0b1aa5, the round 1 rule |
| K | cba7fbdf5df1579d6efb1168eb292e637bc9fad6, tree b653389febe6fda63ce87e589859aa8605eef51f | unchanged; code proof rerun `t3b code proof: 0 FAIL` |
| lists/LISTS.md5 | 5c86318a0d3c628bf3f9711fe7081fb5 | unchanged; `md5sum -c` OK |
| diskguard8.sh | 0fe96ad9b0208bf6381f2bc5ee7b60b4 | unchanged |
| t3b_register.sh | 547fc3a769c1039671269f469584095f | changed |
| t3b_queue.sh | cad952c0c5fa95c4a305bf822436944d | changed |
| t3b_relay.sh | 2870fd4365c5d8b642119a37261d8b08 | changed |
| run_t3b_read.sh | e4cda97aca7c3d2539bd3eecd14c845c | changed |
| t3b_verdict.py | 7dee83d6634baba74c85df448d84f42f | changed (diffed against my round 1 copy 7de5bcb6: run-id check, fa_cells 74, --repeat header, 2 disclosures; nothing else) |
| t3b_rendercmp.py | d6eec93f53818d3dbb0151845dac1ef4 | changed (--kind repair) |
| t3b_label_precheck.py | 214d087dbcca133768c1846913567113 | new |
| t3b_verdict_test.py | 86769fac66228aa140793e6ff6075597 | changed |
| t3b_chain_smoke.sh / t3b_repair_smoke.sh | d9532cb0f5f5dcd00296ff3efbceccf2 / 3f37412538eaeaeedaf002a0aa1e11bf | changed / new |
| t3b_render_smoke.sh / t3b_testmode_guard_test.sh | 44da6eee4e786bfc2be6bf5dda2971f1 / 7209c8078be7e9b1424919141f59b127 | changed |
| t3b_smoke_synth.py / t3b_set_pins.py | 074eba73a9013c1cee4f2feea7e29859 / c2230304a54f5285c37e56b4f43458cc | changed (not in the procedure) |
| t3b_make_jobs.py, t3b_make_lists.py, t3b_train_smoke.sh, t3b_codeproof.sh | 84649917, 47b1dbc6, b999f996, 2c9a073d | unchanged |
| evidence/MD5_evidence.txt | c9b3287f440e7333f3ebcac61012a467 | 80 of 81 entries pass `md5sum -c`; the 81st is the list's own line (empty-file md5 d41d8cd9; R2-N3) |

The builder kept no round-1 copies, and H3 is untracked in git. I diffed t3b_verdict.py and t3b_verdict_test.py against my
round-1 copies and checked the rule by reverse patch. I read the other changed scripts whole.

## R2.2 Blocking items of round 1
**B1 closed (E).**
- t3b_relay.sh: NAMES_RX per mode. Train is `^t3b_(all|half)_f[0-4]_s[5-7]$|^t3b_deploy_s[5-7]$`; trainrep R uses the
  same. Dump is `^t3b_(all|half)_f[0-4]_s[5-7]\.swad\.tta_d4\.e1t3b_f[0-4]$`. Single-quoted inside the tmux / FG command. The
  job list must hold N lines that match the mode's regex.
- My probe: a TEST_MODE registration made by the real t3b_register.sh; synthetic KB holding all 63 RUN.md5 (33 training + 30
  dump) at once, so even the wrong order cannot mix them; the real relay_w1c.sh through t3b_relay.sh FG=1 with a stub ssh;
  the dump relay run first.
  - `RELAY ALL DONE: 30 of 30 runs relayed`, `RD2 units: 30; dumps 30; training 0`.
  - Then the train relay: `RELAY ALL DONE: 33 of 33 runs relayed`, `RD1 units: 33; dumps 0; training 33; deploy units 3`.
  - Then `deploy`: `DEPLOY LATEST DONE: 3 of 3`, and `t3b_deploy_s5..7 latest.pth in RD1 = LATEST.md5` (md5sum -c).
  - A second `deploy` is idempotent (`3 of 3`).
- q1_done (gate, render2, place2, arm2) requires all of these:
  - the RD1 line `RELAY ALL DONE: 33 of 33`;
  - for t3b_deploy_s5..7: RD1/.ok, gaint md5sum -c of the relayed RUN.md5, and latest.pth present and equal to LATEST.md5;
  - `DEPLOY LATEST DONE: 3 of 3`.
- Gate results in my probe:
  - all present: `t3b complete: 33 of 33 ... the 3 deployable units and their latest.pth verified on gaint`;
  - t3b_deploy_s6 latest.pth moved away: `REFUSED (gate): ... t3b_deploy_s6 latest.pth not relayed`;
  - one byte appended to that file: the same refusal.
- Unstage greps `RELAY ALL DONE: 30 of 30`; the real line is `RELAY ALL DONE: 30 of 30 runs relayed` (1 match, E). Chain
  smoke, rerun by me: relay train `33 of 33 ... of which dump units 0`; relay dump `30 of 30 ... of which training units 0;
  RD1 still 33`; unstage `REMOVED_DUMPS 30`, DS and DT removed.

**B2 closed (E).**
- t3b_register.sh checks the 7 script pins before writing anything and writes `scripts <7 x name=md5> ` into REGISTERED.txt.
  The line ends with a space, so a fixed-string ` name=md5 ` match works for the first entry and the last one. In my
  TEST_MODE registration: `7 entries; first run_t3b_read.sh=e4cda97a...`, `last t3b_label_precheck.py=214d087d...`, last
  char a space, every entry equal to its file.
- On tampered copies (one line appended, the other scripts exact, same registration):
  - queue copy: `REFUSED (gate): t3b_queue.sh is not the registered script`;
  - last entry, t3b_label_precheck.py tampered: `REFUSED (gate): t3b_label_precheck.py is not the registered script`;
  - t3b_rendercmp.py tampered: `REFUSED: t3b_rendercmp.py is not the pinned md5`;
  - first entry, the read's own copy: `REFUSED: run_t3b_read.sh is not the registered script`;
  - verdict tampered next to an exact read: `REFUSED: t3b_verdict.py is not the registered script`;
  - relay copy: `REFUSED: t3b_relay.sh is not the registered script`.
- The genuine scripts pass this check and stop later: the gate at `queue ... not ended`, the read at `30 T3b dumps not
  relayed`. The genuine relay started relaying, and I stopped it with its STOP file. No read output folder was created.
- t3b_verdict.check_read refuses arm run ids other than ALL t3b_all_s5..7.oof, HALF t3b_half_s5..7.oof, ZS the three
  fin_..._s5..7 names. My round-1 swapped ALL/HALF read (synthetic records on the real E1 stem list, K's bench_open_read,
  --boot 2000) is now `refuse: arm ALL run ids ['t3b_half_s5.oof', ...] != ['t3b_all_s5.oof', ...]; arm HALF ...` and no
  verdict.txt is written. The chain smoke shows the same (`verdict written: no`).
- The same end-to-end with the right lists still decides correctly:
  - positive `Delta +0.1125 [+0.0905, +0.1309]` -> `CONFIRMED`;
  - negative `-0.1321` -> `NOT CONFIRMED (WORSE ...)`;
  - false crack px x3 -> `GAIN, FAILING GUARDS NAMED`.

## R2.3 The lead's other points
3. **N1 repair path: PASS (E code, smokes).**
   - repair_register needs t3b ended and refuses a name with a `trained rc=0` line or a RUN.md5.
   - fresh = the same jobs_train line; resume = the same line with `--resume` in field 9.
   - Render smoke (K's real cq.sh): `render compare: 0 FAIL (2 rendered repair lines; 2 expected)`. The fresh repair line
     equals the training line; the resume line equals the training line plus ` --resume` (F2's resume template). `resume
     line without latest.pth` is refused.
   - repair_aside renames experiments/<n> and <n>.stdout for fresh, only <n>.stdout for resume. It refuses if the run's PID
     is alive, a RUN.md5 exists, a *.failed target exists, or (resume) latest.pth is missing.
   - A repair counts only when IO/repair<R>/REPAIR.txt = REPAIR.md5 and the ledger holds that md5. Every later step and
     q1_done call rep_regs, which refuses otherwise.
     - My probe gate with a repair record not in the ledger: `REFUSED (gate): repair 1 (REPAIR.txt e18c587c...) is not in
       the ledger ...: not registered`.
     - Once its md5 is in the ledger, the gate looks for that queue (`queue .../t3brep1 not ended`).
     - An unregistered cv02 dir t3brep7: `unregistered repair queue /tmp/noob_el/bench_q/t3brep7`.
   - Repair smoke rerun, all lines as the builder's: `gate with 2 failed runs: rc 1`; `negative repair_aside 1 before its
     ledger line: rc 1`; `negative repair of a run that succeeded: rc 1`; t3brep4 refused; `relay trainrep 1: ... RELAY ALL
     DONE: 33 of 33`; final `gate ... rc 0 (t3b complete: 33 of 33 ... registered repairs: 1:t3b_half_f2_s6
     2:t3b_deploy_s7)`.
   - **render_r / arm_r not run against cv02: does not block (S).** Both are thin calls of the same render_q / arm_q that
     render, arm, render2 and arm2 use on the main path, which the lead runs on cv02 before any repair can exist. The repair
     lines' rendering and render compare ran through K's real cq.sh. arm_r adds only a check that no other T3b queue is alive
     (E code) and checks the file render_q writes for its tag (render_cmp_repair<R>.out, E code). Any fault there refuses.
4. **N8: PASS (E).**
   - t3b_label_precheck.py run on a synthetic E1 with the build's env prints `106 of 106 ... nothing written` and leaves 0
     files newer than my marker in the probe dir, the K copy and H3.
   - In H3 it is called only by `t3b_queue.sh build`, after: REG_MD5 = REGISTERED.txt, the scripts pins, e1_files registered,
     K clean, and ledger row #9 (E grep and code order).
   - My probe registered a synthetic E1 with a 24 on a kept px and a 200 on an ignore px.
     - Build without row #9: `REFUSED (build): the ledger ... holds no '| 9 |' row ...`; neither precheck.out nor IO/data
       was made.
     - With the row: `label precheck: 2 of 106 cells refused (nothing written), e.g. ['...: a scored px holds 24 ...', '...:
       E1 mask values outside the class map: [200]']`, `REFUSED (build): label precheck failed`, IO/data absent.
   - t3b_register.sh still only hashes E1 files (md5sum) and copies images; nothing else in H3 decodes an E1 label (E grep).
5. **N2 to N7, N9, N10, N12, N13: PASS (E).**
   - N2: my mutant M9 now fails (`1 failed, 26 passed`). Rerun against the new code and tests, all 19 of my verdict mutants
     fail at least one test. Round 1's 16 give the same counts, now with M9 caught. New: M15 run-id check off `4 failed`,
     M16 fa_cells check off `1 failed`, M17 ALL / HALF run ids swapped `4 failed`. Verdict tests `27 passed in 0.84s`.
   - N3: check_read refuses fa_cells != 74 (my first synthetic set, with 36 crack-free cells, would now be refused; rerun
     with 74).
   - N4: my PINS_FILE that sets BENCH_EXT and one with `K=$(touch /tmp/x)` are both `REFUSED: PINS_FILE holds other lines
     than K=, F2=, W_K=, W_G=`; PINS_FILE is path-guarded before sourcing.
   - N5: `TAG=../../tmp_x` gives `REFUSED: TAG must be [a-z0-9_]+`; the chain smoke's repeat read prints `REPEAT (TAG rep1),
     not the registered read` in run.log and the verdict header.
   - N6: build and stage call ledger_row (E code; build tested above).
   - N7: the register checks the ledger header before `mkdir $IO` (E code order).
   - N9: rule line as approved.
   - N10: latest.pth of the 3 deploy runs relayed and checked (B1 above).
   - N12, N13: in the request and in the verdict's disclosures (E diff).
   - Guard test rerun: 35 PASS, `guard test: 0 FAIL`, including the relay cases and D10 to D13.

## R2.4 Reruns (E)
- `t3b_chain_smoke.sh`: `read rc 0`, the same lines as the builder's evidence after normalising paths, times and hashes;
  verdict_synthetic.txt equal except the registration line.
- `t3b_repair_smoke.sh`: `final gate rc 0`.
- `t3b_render_smoke.sh`: `render smoke rc 0`; rendered_train / dump / repair and jobs_repair byte-equal to the evidence;
  rendered_train.txt byte-equal to my round 1 render.
- `t3b_testmode_guard_test.sh`: 0 FAIL / 35.
- t3b_verdict_test.py: 27 passed.
- `t3b_codeproof.sh cba7fbd`: 0 FAIL.
- Not rerun: the train smoke and K's pytest, because K, train.py and the train smoke are unchanged since my round 1 reruns.

## R2.5 Non-blocking notes (round 2)
- **R2-N1.** render_r and arm_r have not been exercised against cv02 (see 3). If a repair happens, read render_r's output
  before arm_r.
- **R2-N2.** t3b_label_precheck.py has no registration check of its own. Run by hand, it would decode E1 labels against any
  hash file. Only `build` calls it, after every registration check, so the risk is low (S). It could take REGISTERED.txt
  and check its e1_files line.
- **R2-N3.** evidence/MD5_evidence.txt lists itself with the empty-file md5; the other 80 entries pass. Cosmetic.
- **R2-N4.** K's bench/t3b_labels.py docstring still says the map "can only act on ignore px". The rule's line is the
  correct one; this is disclosed in request 6b and K stays unchanged (S: acceptable).
- Round 1 notes N11 (MAXC, the lead's call at arm) and N14 (no action) stand as written.

# Round 3

Round 3 (22 Nov 2026, 02:52 to 03:12 IST), AMENDMENT_1: **PASS.** No blocking item. Rounds 1 and 2 above are unchanged (md5
2d066285 before this section). Limits as before. On cv02: two read-only ssh calls (cat of the KB and F2B CODE.md5 hash lists,
md5sum -c, cat REVISION, find | wc, locale), nothing written. On gaint: nothing read in IO/data or IO/stage, only the root
records REGISTERED.txt and BUILD.txt of IO 1. No E1 label or prediction opened. My scratch under bench_int_io was removed.

## R3.1 Pins (all E: md5sum; equal to the lead's list of 02:50)
- **AMENDMENT_1.md:** 937a6cbf5a1b6deebf46ce963723fb46.
- **LAUNCH_REQUEST_t3b.md:** a1ff0c842a9f14d9c9a03f14a3bae9e2 (section 6c added).
- **evidence/MD5_evidence.txt:** 3f5e24c0bcc8157df015014b44ddaf13.
- **t3b_queue.sh:** 51a962379bd0399c2ae5a4c90b85bb7b, was cad952c0.
- **t3b_register.sh:** 8cecc85158c258d1462058a8fb1c23c3, was 547fc3a7.
- **New:** t3b_kbcheck_smoke.sh 61d0852b80f9bb9474d1d95911f01464, t3b_realinput_audit.sh bd84f5e7a9755f60aff868a71209f488.
- **Unchanged:** T3B_RULE.md 0c006d44, LISTS.md5 5c86318a, K cba7fbd (tree b653389f), run_t3b_read.sh e4cda97a, t3b_relay.sh
  2870fd43, t3b_verdict.py 7dee83d6, t3b_rendercmp.py d6eec93f, diskguard8.sh 0fe96ad9, t3b_label_precheck.py 214d087d.
- run_t3b_read.sh and t3b_relay.sh carry 02:32 mtimes, but their md5s are the round 2 pins: rewritten, content unchanged.
- The registration-1 copies in evidence/amend1 have md5 cad952c0 and 547fc3a7, the files I reviewed in round 2.

## R3.2 Point 1: the two diffs (E: my own `diff` of the registration-1 copies against the amended files)
- **t3b_queue.sh changes in exactly 3 places:** a 3-line header comment; kb_check, where `| LC_ALL=C sort -k2` is added after
  each `grep -v '  REVISION$'`, so both CODE.md5 lists are sorted by path before the diff; dt_check, where the gaint side's
  `md5sum < $IO/data/LINKS.tsv` becomes `LC_ALL=C sort $IO/data/LINKS.tsv | md5sum`. Nothing else.
- **t3b_register.sh changes in 1 place:** the t3b_queue.sh entry of SCRIPT_PINS, cad952c0 -> 51a96237. Nothing else.
- **The sort cannot hide a difference (E, S).** Both lists are sorted by the same key, so the diff still reports every
  (md5, path) line found in one list and not the other; a path's md5 change shows as a `<p` / `>p` pair. The result must
  still equal DW exactly. On the real files (cv02 hash lists, recomputed on gaint): sorted diff = DW, 33 entries; unsorted
  diff, the registration-1 logic, 123 entries. My negatives on the real lists, each **refused**:
  - one K path (bench/derived.py) set back to F2's md5;
  - the md5s of README.md and Makefile swapped;
  - a K-only path (bench/t3b_labels.py) missing from KB.

  The real KB lines reversed or shuffled still **pass**. The builder's order smoke, rerun by me, gives `kb_check order
  smoke: 0 FAIL`: registration-1 refuses the 'en' and reversed orders; the amended check passes both and refuses an extra
  path and a changed README.md.
- **KB itself (E).** KB's CODE.md5 on cv02 equals a CODE.md5 I computed from `git archive cba7fbd` + REVISION: 799 paths,
  every md5 equal. `KB_CODE_OK`, REVISION K, `find . -type f | wc -l` 800, `md5sum < CODE.md5` fe36b04e. So KB is exactly
  K, including the K paths that PINS does not cover.
- **dt_check.** The change compares LINKS.tsv with the cv02 link list as sorted multisets, so it cannot hide a missing or
  retargeted link. My isolated test (dt_check taken verbatim from each script, stub R() running under LANG=en_GB.UTF-8,
  mixed-case link names):

  | Case | registration-1 dt_check | amended dt_check |
  |---|---|---|
  | as staged | passes | passes |
  | gaint LINKS.tsv lines reversed | refuses | passes |
  | one link retargeted on the cv02 copy | | refuses |
  | one link missing on the cv02 copy | | refuses |

  The builder's file is Python-sorted, which is C order for these ASCII names, so today the change does nothing (S). BUILD.txt's
  `links` md5 (the unsorted file) is unchanged, so the rebuild identity check in step 7 still covers it.

## R3.3 Point 2: the amendment path (AMENDMENT_1 section 5): complete and fail-closed (E code, S)
- **IO 1 now (E).** /home/noob/work/bench_t3b_io, REGISTERED.txt fb2c424c; its scripts line pins t3b_queue.sh=cad952c0, so
  the amended queue refuses registration 1 and a new registration is required. BUILD.txt: data_manifest 7ab27f32, roots
  d7d5cae6, links 88f18fb4, e1_labels 74539540. No superseded1 dir yet. Ledger row #9 holds REGISTERED.txt fb2c424c; the #9
  bullet names register 547fc3a7.
- **Step 2 (mv + chmod -R a-w).** Required: t3b_register.sh refuses while IO exists. No script refers to fb2c424c or to
  bench_t3b_io.superseded1 (E grep of H3 scripts).
- **Every later step reads only the default IO path and REG_MD5 from the environment:**
  - queue, relay and read all check REG_MD5 against the new IO/REGISTERED.txt;
  - build and stage also need a `| 9 |` row holding REG_MD5;
  - repair records embed REG_MD5.

  So a leftover REG1 refuses everywhere, and nothing points at IO 1.
- **Step 4 (registration 2 under `env -i HOME PATH`).** Every line other than 'registered' is deterministic:
  - stage MANIFEST built with `find | LC_ALL=C sort`;
  - e1_files in E1 list order;
  - zs.tsv in a fixed order;
  - job lists from t3b_make_jobs.py;
  - scripts from the hard-coded SCRIPT_PINS (8cecc851).

  The identity diff of step 5 enforces the first four against registration 1.
- **Step 7 (rebuild).** The builder is deterministic: Python-sorted listings, no timestamps in hashed files, PIL encoding. E
  from round 1: the builder's and my separate runs on the same synthetic data gave the same ROOTS f9a4d24b / MANIFEST
  eb5e3797. The BUILD.txt diff (data_manifest, roots, links, e1_labels) is the stop condition. The precheck runs again
  before anything is written.
- **Step 8 (check against the existing KB).** No redeploy is needed or possible (c3_deploy refuses an existing KB). KB = K
  file by file (R3.2), and the amended kb_check passes on it (my recomputation and the builder's audit). Nothing in T3b pins
  KB's CODE.md5 md5 fe36b04e or its line order: cq.sh deploy_ok and cq_setup.sh use `md5sum -c` only (E grep).
- **Fail-closed.** Each step either refuses in code (register: IO exists; build/stage: ledger row; every step: REG_MD5 and
  scripts pins; check: kb_check) or has a stated stop (steps 5 and 7 "must print nothing ... stop"). The two manual diffs
  are the only procedural gates; both are one-line commands with a clear pass condition.

## R3.4 Point 3: real-input audit and "not testable before stage" (E grep, S)
- **Audit.** It is read-only as written: cv02 ssh -n with cat / md5sum / diff / ls / test / grep / df / nvidia-smi / tmux
  has-session; gaint reads fin2 / fin relay hash files only; no IO read. Its rows match my own read-only results: the
  kb_check rows, 798 / 781 lines, first paths .gitignore / bench/aa.py.
- **cv02's locale is the risk class.** A non-interactive ssh shell on cv02 has `LANG=en_GB.UTF-8` (E), so an unpinned `sort`
  or `ls` order there differs from gaint's and is invisible to the stub smokes, which run both sides on gaint.
- **Every `sort` in t3b_queue.sh, t3b_relay.sh, run_t3b_read.sh and t3b_register.sh is `LC_ALL=C`:**
  - kb_check: three sorts;
  - dt_check: both sides;
  - register: stage MANIFEST;
  - read: arm lists.
- **Every other cross-machine comparison is order-free:**
  - `md5sum -c`: PINS, CODE.md5, MANIFEST, ROOTS, RUN.md5, LATEST.md5;
  - md5 of the same bytes on both ends: MANIFEST.md5 and ROOTS_t3b.md5 after tar, jobs.txt after cat, RUN.md5 after the
    relay;
  - counts: ds_check, arm_q's queue-dir string, unstage file counts, names_check;
  - set comparison of rendered lines (t3b_rendercmp.py) and q1_done's parsed lines.

  cq.sh on cv02 writes RUN.md5 with a locale `sort`, but those bytes are only md5sum -c'ed and compared to themselves after
  the relay.
- **Verdict on point 3.** I find no remaining order- or locale-sensitive comparison that the stub smokes cannot catch. The
  stage-time items (dt_check, ds_check, render, place / arm, deploy relay, unstage's cv02 part, the read) use only the order-free
  forms above.
- **c3_deploy.sh (2d9fdbb3) unpinned `sort`.** It no longer matters for T3b: KB is deployed and verified file by file, and
  every consumer of a CODE.md5 is now order-free. Leaving it is acceptable; pin it (`LC_ALL=C sort`) before the next deploy
  of any queue (R3-N3).

## R3.5 Reruns (E)
- `t3b_kbcheck_smoke.sh`: `kb_check order smoke: 0 FAIL` (6 OK lines).
- `t3b_testmode_guard_test.sh`: 35 PASS, `guard test: 0 FAIL`.
- `t3b_repair_smoke.sh`: rc 0, final gate `t3b complete: 33 of 33 ... registered repairs: 1:t3b_half_f2_s6
  2:t3b_deploy_s7`.
- `t3b_chain_smoke.sh`, with the amended queue and register (its TEST_MODE register checks SCRIPT_PINS with queue
  51a96237): `stage rc 0 (DT ...: MANIFEST.md5, ROOTS_t3b.md5 and the link list = IO/data ...)` through the amended dt_check;
  relays 33 of 33 / 30 of 30 with no mixing; `read rc 0`; unstage `REMOVED_DUMPS 30`, DS and DT removed. chain_smoke.out is
  the same as the evidence after normalising paths, times and hashes.

## R3.6 Non-blocking notes (round 3)
- **R3-N1.** Step 5's identity diff drops the whole 'scripts' line. Also check that it differs only in the queue entry:
  `diff <(grep '^scripts ' <IO1>/REGISTERED.txt | tr ' ' '\n') <(grep '^scripts ' <IO2>/REGISTERED.txt | tr ' ' '\n')` must show
  only `t3b_queue.sh=cad952c0...` -> `t3b_queue.sh=51a96237...`. This is implied by the reviewed SCRIPT_PINS, so it is a
  belt-and-braces check.
- **R3-N2.** The step list adds the amendment bullet (written before REG2 exists) and replaces row #9. Also add the #9
  bullet that registration 2 prints, so the ledger bullets name REG2 the same way they name fb2c424c.
- **R3-N3.** c3_deploy.sh: use `LC_ALL=C sort` before the next deploy of any queue (not needed for T3b; see R3.4).
- **R3-N4.** bench_t3b_io.superseded1 keeps a second gaint copy of the E1 images (stage) and E1 training labels (data),
  read-only, on the machine where E1 already lives. Worth one line in the disclosures; delete it when T3b is closed, if the
  lead wishes.
- **R3-N5.** The lead disclosed one temporary file written and removed on cv02 during the diagnosis (log 02:26). It holds
  nothing of E1 (a path list) and needs no action.
