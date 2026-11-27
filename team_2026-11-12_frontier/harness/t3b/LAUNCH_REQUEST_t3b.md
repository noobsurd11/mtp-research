# Launch request: T3b few-shot layout adaptation (E1 opening #9) (t3b_builder, 21 Nov 2026)

Status (AMENDMENT_1, 22 Nov 2026 about 02:45 IST: step 5 refused on a line-order bug in kb_check; fix, real-input audit and
re-registration plan in AMENDMENT_1.md and section 6c; round 1 fixes in section 6b): **built and tested on gaint CPU only with
synthetic data; the AMENDMENT_1 audit read real cv02 / NAS files read-only.** Nothing launched, no GPU used, no queue placed or armed, no
deploy made, nothing written on cv02 (read-only inspection: GPU memory, free disk, one run dir size, dir names), no E1 mask,
ignore pixel, E1 or test50 prediction or NAS dump opened, no commit pushed.** Commit K exists locally only (branch bench_t3b).
The opening happens only after an independent review and the lead's go.
Notation: T = /home/yugma/mtp/research/team_2026-11-12_frontier, H3 = T/harness/t3b, F2 = 9967d59a (bench_fin2), G = 8bd1c276
(bench_open_g), R = 0c72cf94 (bench_open_read), **K = cba7fbdf5df1579d6efb1168eb292e637bc9fad6** (tree b653389febe6fda63ce87e589859aa8605eef51f, worktree /home/noob/work/bench_wt_t3b, branch
bench_t3b), KB = cv02 /tmp/noob_el/bench_cba7fbd (the deploy of K), F2B = cv02 /tmp/noob_el/bench_9967d59, DT = cv02
/tmp/noob_el/bench_data_t3b (T3b roots), DS = cv02 /tmp/noob_el/bench_data_sealed (E1 images), IO = gaint
/home/noob/work/bench_t3b_io (made by the registration). E = measured by a command of this build (file cited); S = judgement.

## 0. What T3b does (one page)
- **Rule:** H3/T3B_RULE.md (written before any T3b number). Folds K = 5 by image id = the draft file's k5_fold, frozen with a
  deterministic half per fold (H3/lists, LISTS.md5 5c86318a). Arms ALL (pool532_v11 + the E1 cells of the other 4 folds) and
  HALF (+ a fixed half of those image ids); the exact C2 recipe (HRNet-W18 U-Net++ + SWAD, 20,000 steps, swad, D4, argmax);
  seeds 5 to 7; 30 fold models + 3 deployable models (532 + 106, never scored). In-sample monitor of 107 pool cells as in the
  full-pool runs; no held-out E1 cell is listed or linked in a fold root.
- **Primary:** P = pooled out-of-fold crack relF1@2, ALL - ZS (ZS = opening #8's C2 seeds 5 to 7, re-scored), 106 cells, OP-A,
  seed-aware two-stage bootstrap (71 clusters x 3 seeds, 2,000 draws, Random(0)), M 0.010; guards false crack px on the 74
  crack-free cells <= 1.5 x ZS and mIoU-R13 >= -0.010; width ratio printed, not a guard. Beside: HALF - ZS, ALL - HALF,
  any-hit recall, strata, inactive, strict IoU (with band), per class, per seed.
- **Separation:** trained_on_e1 on every T3b dump and record; every T3 / E1-column scorer refuses it; only the T3b card
  (bench_open_read.py --t3b ZS) holds both, ZS labelled the zero-shot comparator.
- **Queues:** t3b (33 trainings, LPG 1, MAXC = free GPUs at arm, SHARE_TRAIN 20480, no SHARE_DUMP, disk guard 8), then t3bopen
  (30 sealed D4 dumps of held-out cells, strict lanes). **Read:** gaint CPU, K, once. **Unstage:** DS, DT and the 30 dump dirs
  leave cv02 (relayed copies md5-verified first).

## 1. Files (H3) and md5
See section 12.

## 2. Commit K (on F2, G and R; local only)
`git -C /home/noob/work/bench_wt_t3b log --format='%h %p %s' 9967d59..K`: 4710e9f = merge of G into F2 (cq.sh conflict only in
the header comment; both blocks kept); a8cea33, 9ee1f08, 232659d = R's 82ea81c, 19764b2, 0c72cf9 cherry-picked (-x; no
overlap with F's or F2's paths); 4ea4bf8 and cba7fbd = the T3b changes. K differs from F2 in 25 paths: G's 4, R's 9, T3b 17
(E, evidence/codeproof.out item 3). **Training path byte-equal to F2** (117 files: train.py, src/, configs/, cards, tta, queue
helpers; item 2). T3b paths:
| Path | Change |
|---|---|
| bench/sets.py, bench/dumpfmt.py | sealed sets e1t3b_f0..4 (pinned lists in bench/sets/, md5 = H3/lists; asserted inside ext117's E1 list in its order); images / masks / ignore of EXT as e1_106 |
| bench/sets/e1_106_stems.txt, e1t3b_f<k>.txt | the E1 list (= stems_eval.txt bytes, 5266806b) and the 5 held-out lists |
| bench/t3b_labels.py (new) | E1 training labels: class map (24 -> 2, 29 -> 1, 25..28 -> 255), ignore -> 255, equality with the scorer's view asserted per cell |
| scripts/bench_make_t3b_roots.py (new) | the T3b data dir: 11 roots (layout of bench_make_pool_root.py), pool part = pool532_v11's lists and bytes (pins), E1 files md5-checked against the registration before decoding, no held-out link, --check |
| bench/q/cv02/cq.sh | T3b root kinds (fold roots with fold k, deploy root fold 0; no dump in the chain; ROOTS_t3b.md5 + MANIFEST.md5 at arming); SEALED may name e1t3b_f0..4; a T3b set only from a run on its own fold's root; e1_106 / test50 only from pool532_v11 runs |
| scripts/bench_infer.py | trained_on_e1 / e1_train_cells in the manifest when the run's train list holds an E1 stem (no new key otherwise); e1t3b sets only from such runs |
| scripts/bench_score.py, bench/derived.py | records: a marked dump only on e1t3b sets (and e1t3b only from marked dumps), the mark copied; summary and derived dumps refuse marked inputs |
| scripts/bench_open_read.py | marked records refused unless --t3b ZS (ZS unmarked, other arms marked and out-of-fold; ZS labelled); model key cc_recany_20 (any-hit recall). Without --t3b, read.txt byte-equal to R's (item 6) |
| scripts/bench_t3b_oof.py (new) | the out-of-fold record of one arm and seed from its 5 fold records |
| tests/test_bench_t3b.py (new) | 41 tests (section 7) |

## 3. Lists (H3/lists; LISTS.md5 5c86318a0d3c628bf3f9711fe7081fb5)
t3b_make_lists.py (reads only benchmark/out/t3b_draft_folds.tsv 49e70413 and the E1 list): held-out 22 / 22 / 20 / 21 / 21
cells; half 42 / 42 / 43 / 42 / 43 cells, hard-stratum crack px shares 0.499 to 0.501 (E, lists/LISTS_REPORT.txt). A second run
into another dir gives the same LISTS.md5 (E, evidence/lists_rerun.out).

## 4. Job lines (made by the registration from t3b_make_jobs.py; NOT in any queue dir)
- t3b (33): `t3b_all_f0_s5|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml|5|/tmp/noob_el/bench_data_t3b/roots/t3b_all_f0|0|11510|6200|0||swad`
  ... `t3b_deploy_s7|...|/tmp/noob_el/bench_data_t3b/roots/t3b_deploy|0|11510|6200|0||swad` (gates as fin's C2 lines).
- t3bopen (30): `t3b_all_f0_s5.swad.tta_d4.e1t3b_f0|<card>|5|.../t3b_all_f0|0|11510|6200|0|--dumpof /tmp/noob_el/bench_cba7fbd/experiments/t3b_all_f0_s5 --key swad --tta d4 --set e1t3b_f0`.
- Render (E, evidence/render_smoke): K's real cq.sh renders 33 training commands (card opts + data.root, no dump) and 30 dumps
  (`--set e1t3b_f<k> --opening e1_open9_t3b --weights-key swad --tta d4`, no logp); render compare 0 FAIL each; the dump list
  without SEALED and the training list with SEALED are refused.

## 5. GPU, disk, timeline
- **GPU-h (S from E):** HRNet+SWAD on cv02 about 110 min per run at one run per GPU (E, log.md 21 Nov 06:11, fin HRNet s5 at
  step 8,600); steps are fixed (20,000), so the larger list does not lengthen a run. 33 x about 1.9 h = **about 63 GPU-h**; 30
  D4 dumps of 20 to 22 cells about 0.5 to 1 GPU-h. **Total about 64 GPU-h.**
- **Wall (S):** 33 runs in waves of MAXC: 8 free GPUs -> 5 waves, about 9.5 h; 6 -> about 11.5 h; 4 -> about 17 h (cv02 had
  8 of 8 GPUs free at 15:13 IST, E: nvidia-smi). Then t3bopen about 15 to 30 min, its relay a few min, the read about 5 min
  (gaint CPU). Example: armed 17:30 IST with 8 GPUs -> trainings end about 03:00 IST 22 Nov, read about 04:00.
- **Disk cv02:** a full-pool HRNet+SWAD run dir is 962 MB (E: fin_hrnet_swad_v11_pool_s5: latest 756 MB, slim 168 MB, best
  84 MB); 33 x 0.96 = 31.7 GB + DT 0.11 GB + DS 0.01 GB + 30 dumps about 0.8 GB (S) = **peak about 33 GB**; cv02 free 71 GB
  (E, 15:13). arm refuses below 55 GB (33 + the 20 GB floor, rounded); disk guard 8 HOLDs new starts below 20 GB.
- **Disk NAS / gaint:** relay t3b 33 x about 0.17 GB = 5.6 GB, + latest.pth of the 3 deployable models 3 x 0.76 GB = 2.3 GB
  (round 1 N10), t3bopen about 0.8 GB: **about 8.7 GB** (NAS 8.3 TB free, E); gaint IO about
  0.12 GB, read output < 0.3 GB.

## 6. Procedure (who runs what, in order)
| # | Who | Command / action | Stop path |
|---|---|---|---|
| 0 | reviewer | independent review of this request, T3B_RULE.md, K and the H3 scripts (section 8); PASS pinned to T3B_RULE.md's md5 | |
| 1 | lead | `bash H3/t3b_register.sh` from a clean shell (env -i; no override): IO/jobs_train.txt, jobs_dump.txt, stage/ (106 images + list, MANIFEST), reg/e1_files.md5 (hashes), reg/zs.tsv (hashes), reg/lists, REGISTERED.txt (read-only); prints its md5, ledger row #9 and bullet | refuses on any pin |
| 2 | lead | adds row #9 and the bullet to team_2026-10-31_next/e1_openings.md ("registered, NOT opened"; **E1 is training data for T3b models from this date**) and a log.md line, **before step 3** | |
| 3 | lead | `REG_MD5=<md5> bash H3/t3b_queue.sh build` (gaint; refuses unless the ledger holds row #9 with REG_MD5; t3b_label_precheck.py decodes and checks all 106 labels in memory, then K's builder writes IO/data, BUILD.txt) | refuses if IO/data exists; nothing written if the precheck fails |
| 4 | lead | `bash T/harness/c3base/c3_deploy.sh cba7fbdf5df1579d6efb1168eb292e637bc9fad6` (KB; prints CODE.md5 and CV02_CODE_OK) | refuses if KB exists |
| 5 | lead | `REG_MD5=... K=cba7fbdf5df1579d6efb1168eb292e637bc9fad6 bash H3/t3b_queue.sh check` (cv02 read-only: KB pins and its diff to F2B = K's paths; bench_data; 63 names free) | |
| 6 | lead | `... t3b_queue.sh stage` (DT <- IO/data, DS <- IO/stage; md5sum -c, link list, no mask dir in DS; read-only) | DT or DS exists: refused |
| 7 | lead | `... t3b_queue.sh render` (render-only cq.sh of KB on jobs_train.txt; render compare 0 FAIL) | nothing starts |
| 8 | lead | `... t3b_queue.sh guard`, `... place`, `DRY=1 ... arm`, then `GAPSEC=30 ... arm` (MAXC = GPUs free now unless MAXC is set lower) | `touch /tmp/noob_el/bench_q/t3b/HOLD`; a run by its recorded PID only |
| 9 | lead | `REG_MD5=... bash H3/t3b_relay.sh train` (NAS bench_relay/t3b; NAMES_RX = the 33 training names only) | `touch <RD1>/STOP` |
| 10 | lead | ticks `... t3b_queue.sh status`; MAXC may be raised by writing Q1/MAXC when more GPUs free up (cq.sh reads it live) | |
| 11a | lead | after t3b's ALL DONE and 'RELAY ALL DONE: 33 of 33': `REG_MD5=... bash H3/t3b_relay.sh deploy` (latest.pth of t3b_deploy_s5..7 into RD1, each md5sum -c against its LATEST.md5; 'DEPLOY LATEST DONE: 3 of 3') | |
| 11b | lead | `... t3b_queue.sh gate` (read-only: q1_done) then `... render2`, `... place2`, `DRY=1 ... arm2`, `... arm2`; `... t3b_relay.sh dump` (NAMES_RX = the 30 dump names only) | `touch /tmp/noob_el/bench_q/t3bopen/HOLD` |
| 12 | lead | after RELAY ALL DONE 30 of 30: `REG_MD5=<md5> bash H3/run_t3b_read.sh` in tmux from a clean shell, ONCE; output /home/noob/work/bench_reads/t3b_open9 (records, records/oof, read_t3b, verdict.txt, MD5.txt) | refuses before writing anything |
| 13 | lead | ledger "opened <start> to <end>" + the verdict line; `REG_MD5=... K=... bash H3/t3b_queue.sh unstage` (30 dump dirs after md5 checks, then DS, then DT) | |
**Repair path (round 1 N1; between steps 10 and 11), for a training that ended rc != 0** (gate / render2 refuse until it is
repaired): `RN=1 NAMES_R='<names>' KIND=fresh|resume ... t3b_queue.sh repair_register` (gaint: IO/repair1/jobs.txt = the same
lines, resume adds '--resume'; REPAIR.txt; prints the ledger amendment line) -> the lead adds that line to e1_openings.md (an
unregistered repair is refused by every later step and by q1_done) -> `RN=1 ... repair_aside` (fresh: the failed run dir and
stdout renamed *.failed1; resume: only the stdout) -> `RN=1 ... render_r`, `place_r`, `DRY=1 ... arm_r`, `arm_r` (queue
bench_q/t3brep1, LPG 1, SHARE_TRAIN 20480) -> after its ALL DONE `REG_MD5=... t3b_relay.sh trainrep 1` (and `deploy` if a deploy
run was repaired) -> `gate`. q1_done accepts a name trained rc=0 in t3b or in a registered repair queue that lists it.

## 6b. Round 1 (REVIEW_T3B.md ab5eb473, FIX: B1, B2) changes; K cba7fbd and LISTS 5c86318a unchanged
| Item | Change (file) |
|---|---|
| B1 | t3b_relay.sh: per-mode NAMES_RX (train `^t3b_(all\|half)_f[0-4]_s[5-7]$\|^t3b_deploy_s[5-7]$`, dump `^t3b_(all\|half)_f[0-4]_s[5-7]\.swad\.tta_d4\.e1t3b_f[0-4]$`), quoted in the tmux command; q1_done (gate, render2, place2, arm2) also needs RD1 'RELAY ALL DONE: 33 of 33' and, for t3b_deploy_s5..7, RD1/.ok, gaint md5sum -c of the relayed RUN.md5 and the relayed latest.pth; unstage matches the real '30 of 30' line; the chain smoke now runs the real relays through a stub ssh with both kinds of RUN.md5 present |
| B2 | t3b_register.sh pins the md5 of run_t3b_read.sh, t3b_verdict.py, t3b_queue.sh, t3b_relay.sh, t3b_rendercmp.py, diskguard8.sh, t3b_label_precheck.py and writes them as REGISTERED.txt's 'scripts' line; the queue, relay and read refuse unless their own md5 (read: also the verdict's) is registered; t3b_verdict.check_read refuses other run ids than ALL t3b_all_s5..7.oof, HALF t3b_half_s5..7.oof, ZS fin_hrnet_swad_v11_pool_s5..7.swad.tta_d4.e1_106 |
| N1 | repair path above (t3b_queue.sh repair_register / repair_aside / render_r / place_r / arm_r, t3b_relay.sh trainrep, t3b_rendercmp.py --kind repair); t3b_repair_smoke.sh |
| N2 / N3 | verdict tests with fixed-model != seed-aware intervals (mutant M9 fails); check_read refuses fa_cells != 74 (synthetic E1 now has exactly 32 crack cells) |
| N4 / N5 | run_t3b_read.sh: PINS_FILE only K= / F2= / W_K= / W_G= lines (checked before sourcing, path guarded); TAG only [a-z0-9_]+, 'REPEAT (TAG ...), not the registered read' in run.log and the verdict header |
| N6 / N7 / N8 | build and stage refuse without ledger row #9 holding REG_MD5; the register checks the ledger header before writing IO; build runs t3b_label_precheck.py (all 106 labels in memory) before K's builder writes |
| N9 | T3B_RULE.md section 6, one line (evidence/rule_edit_round1.diff): "label = where(ignore==0, mask, 255); the class map changes no output px"; rule md5 8e6df3d2 -> 0c006d44. K's bench/t3b_labels.py docstring still says the map "can then only act on ignore px" (K unchanged; the rule's line is the stated one) |
| N10 | t3b_relay.sh deploy relays checkpoints/latest.pth of t3b_deploy_s5..7 (slim.pth kept); to run one with bench_infer from the NAS, its config's data.root (/tmp/noob_el/bench_data_t3b/roots/t3b_deploy) must resolve to a copy of that root's splits (IO/data/roots/t3b_deploy on gaint) |
| N11 | no change: the lead sets MAXC at arm |
| N12 / N13 | disclosures (below; also printed by the verdict) |
**Disclosures added in round 1:** (N12) T3b records live only under /home/noob/work/bench_reads/t3b_open9; record readers other
than bench_open_read, bench_score summary and derived (e.g. bench_headres, bench_read_w1, bench_udev_read) do not check
trained_on_e1 and are never pointed at them. (N13) From staging to unstage, DT/files on the shared cv02 login holds the E1
training labels of all 106 cells (each fold's held-out labels present but not linked from its root; the deploy root needs
all 106); removed at unstage.

## 6c. AMENDMENT_1 (22 Nov 2026; AMENDMENT_1.md)
Step 5 (`check`) refused a correct KB: kb_check diffed two CODE.md5 files in different line orders (F2B: locale order, KB: C order).
Fix: kb_check sorts both by path; dt_check's gaint side sorted with LC_ALL=C too (audit). Registration 1 (fb2c424c) is superseded
by registration 2 before any E1 file reached cv02 (lead steps in AMENDMENT_1.md section 5). Unchanged: rule 0c006d44, LISTS
5c86318a, jobs d77f3a94 / 9423cb91, K cba7fbd, KB. **Real-input audit** (`bash H3/t3b_realinput_audit.sh`, evidence/amend1/realinput_audit.out;
read-only, nothing written on cv02, IO not read):
| Check | Result | Evidence |
|---|---|---|
| kb_check, registration-1 script (cad952c0) | refuses | REFUSED (check): KB differs from F2B in other paths than K's: <.gitignore <Makefile <README.md <bench/__init__... (123 path entries) |
| kb_check, amended script (sorted by path) | real-input OK | KB /tmp/noob_el/bench_cba7fbd: REVISION K, CODE.md5 OK, pins OK; differs from F2B only in K's paths (+ REVISION) |
| CODE.md5 line orders | info | 798 781 bench/aa.py bench/atlas.py .gitignore Makefile |
| data_check (bench_data DEPLOY.md5) | real-input OK | cv02 d6063fd83d20e656612540edda702cbe, pinned d6063fd83d20e656612540edda702cbe |
| names_check (63 names) | real-input OK | cv02 hits 0, relay hits 0; jobs md5 d77f3a94 / 9423cb91 |
| stage precondition (DT, DS absent) | real-input OK | FREE |
| dt_check | not testable before stage | DT does not exist yet; same commands passed on the chain smoke's staged copy (stub ssh); both sides now LC_ALL=C sorted |
| ds_check | not testable before stage | DS does not exist yet; compares md5 of the same MANIFEST.md5 bytes (tar copy) and md5sum -c (order-free) |
| render_q + t3b_rendercmp.py | not testable before stage | cq.sh arming checks DT's ROOTS_t3b.md5 / MANIFEST.md5 and render writes a scratch queue dir on cv02; rendercmp compares sets of lines (order-free); K's real cq.sh rendered 65 lines in the render smoke |
| arm_q queue-dir string (format, on the ended queue fin2) | real-input OK (format) | jobs 7efbf54cbdbaae747781089aadb056cd LPG 1 share 20480 0 sealed 0 used 2+log ses no |
| free_gpus / free disk (arm) | real-input OK | GPUs < 4096 MiB now: 1; cv02 /tmp free 71 GB (arm needs 55) |
| guard preconditions | real-input OK | bench_diskguard8 session and /tmp/noob_el/bench_q/diskguard8.sh absent: 'guard' will place and start it |
| place / arm / place2 / arm2 / render_r / place_r / arm_r | not testable now | they write or start on cv02 (forbidden here); the cq_setup.sh line they grep is the one fin2 / open printed |
| q1_done remote part + parser (fin2 sample) | real-input OK (format) | ALL DONE / state '1 ended'; names with 'trained <n> rc=0 ' and RUN.md5: 10 of 10; t3brep dirs: '' |
| relay.log / .ok / md5sum -c / LATEST.md5 formats (NAS fin2) | real-input OK (format) | 'RELAY ALL DONE: 10 of 10' lines 1; .ok field 4 = md5(RUN.md5) yes; md5sum -c OK; LATEST.md5 path experiments/fin_hrnet_swad_v11_pool_s5/checkpoints/latest.pth (q1_done / relay deploy use these) |
| unstage gaint-side checks (an open-set dump unit of fin) | real-input OK (format) | unit c3_pf_v11_f0_s5.tta_d4: .ok field 4 = md5(RUN.md5) yes; md5sum -c OK; dump-dir lines 108 of 108 |
| unstage cv02 part, relay deploy, the read | not testable before the runs / dumps | need KB/runs and KB/dumps of T3b (absent); same commands passed through the stub ssh in the chain smoke |
| relay preconditions (stage copy, relay_w1c.sh, NAS) | real-input OK | stage CODE.md5 OK; relay_w1c 74a2ec3d48ad3cd989aa0c9b5ae69942; RD1 / RD2 existing 0; NAS free 8258 GB |

## 7. Tests run (E; gaint CPU, nice 19; synthetic data only; round 1 reruns)
| Test | Result |
|---|---|
| pytest K full (cba7fbd, unchanged) | **938 passed, 5 skipped, 0 failed**, 606 s (evidence/pytest_full_K_cba7fbd_round1.log; round 0 run evidence/pytest_full_K_cba7fbd.log) |
| t3b_verdict_test.py | **27 passed** (evidence/t3b_verdict_test.out): round 0's 20 + N2 fixed-model != seed-aware (2 cases), B2 run ids (3 + swapped ALL / HALF), N3 fa_cells 74, N5 repeat header |
| verdict mutants (evidence/verdict_mutants.out) | M9 (primary from the fixed-model interval) "1 failed, 26 passed"; run-id check removed "4 failed"; fa_cells check removed "1 failed": each caught |
| t3b_codeproof.sh cba7fbd | **0 FAIL** (evidence/codeproof.out); NEG=1: exactly the 2 tampered items FAIL (evidence/codeproof_negative.out) |
| t3b_train_smoke.sh | T1 K rc 0, T2 F2 rc 0, 'Labelled: 616 ... val: 107 test: 107', fold 0's held-out files deleted; latest.pth K = F2: "differing paths: 3 (3 allowed, 0 not allowed)" over 12,360 model + 3,093 optimizer tensors, rng, best_payload (evidence/train_smoke/) |
| t3b_render_smoke.sh | "render compare: 0 FAIL" for 33 training, 30 dump and 2 repair lines (1 fresh, 1 '--resume'); refused: dump list without SEALED, training list with SEALED, resume line without latest.pth (evidence/render_smoke/) |
| t3b_testmode_guard_test.sh | **"guard test: 0 FAIL"** over 35 cases: register 7, queue 9 (+ LEDGER default), relay 6, read 13 (+ PINS_FILE with BENCH_EXT, PINS_FILE outside scratch, TAG '../../tmp_x', a K= PINS_FILE control) (evidence/testmode_guard_test.out) |
| t3b_repair_smoke.sh (N1) | **final gate rc 0**: t3b with 31 rc=0 + 2 failures -> relay train 'RELAY DONE: cv02 queue ended; 31 of 33' -> gate refused (both names, no 33 of 33) -> repair_register 1 (fresh) -> repair_aside refused while not in the ledger -> repair of a run that succeeded refused -> repair_register 2 (resume, line ends '--resume\|swad') -> an unregistered queue dir t3brep4 makes the gate refuse -> aside 1 (2 moved), aside 2 (stdout only) -> place_r 1, 2 -> gate refused (relay) -> trainrep 1 'RELAY ALL DONE: 33 of 33' -> deploy 'DEPLOY LATEST DONE: 3 of 3' -> gate "t3b complete: 33 of 33 ... (registered repairs: 1:t3b_half_f2_s6 2:t3b_deploy_s7)" (evidence/repair_smoke/) |
| t3b_chain_smoke.sh (B1c, B2, N5, N6, N8) | **read rc 0** (evidence/chain_smoke/): register (1 scripts line) -> build refused without ledger row #9 (IO/data not made) -> build ('label precheck: 106 of 106 ... in memory', 11 roots, CHECK OK) -> stage -> gate refused before the relay -> **real relay train "RELAY ALL DONE: 33 of 33", 0 dump units** -> deploy "DEPLOY LATEST DONE: 3 of 3" -> gate "t3b complete" -> 30 dumps (30 marked; 63 RUN.md5 in KB/runs) -> **real relay dump "RELAY ALL DONE: 30 of 30", 0 training units**, RD1 still 33 -> manifest check 33 OK -> zero-shot re-score IDENTICAL 3 of 3 -> verdict -> unstage "REMOVED_DUMPS 30", DS and DT removed. Refused, no output folder: wrong REG_MD5, tampered e1_train_cells, changed ZS npz, changed E1 mask, TAG '../x', overrides without TEST_MODE, unstage before the read, tampered copies of run_t3b_read.sh / t3b_verdict.py / t3b_queue.sh / t3b_relay.sh (each "is not the registered script"), an existing output; **the swapped ALL / HALF read: verdict "refuse: arm ALL run ids [t3b_half_s5..7.oof] != [t3b_all_s5..7.oof]; arm HALF ...", not written**; repeat read TAG=rep1 rc 0 with "REPEAT (TAG rep1), not the registered read" in run.log and the verdict header. Synthetic numbers stay near 0 (tiny random models). Round 1's first chain run found a bug in my own B2 fix (the 'scripts' match missed the first entry; fixed: fixed-string match) |
| lists rerun | LISTS.md5 5c86318a again, byte-equal (evidence/lists_rerun.out; unchanged since round 0) |
| AMENDMENT_1: t3b_kbcheck_smoke.sh | **"kb_check order smoke: 0 FAIL"** (evidence/amend1/kbcheck_smoke.out): registration-1 kb_check REFUSES an F2B CODE.md5 in 'en' order (first paths bench/aa.py bench/atlas.py, the real F2B order) and in reversed order; the amended kb_check PASSES both; amended negatives: an extra path in KB REFUSED, a changed README.md in KB REFUSED |
| AMENDMENT_1: t3b_realinput_audit.sh | section 6c table (amended kb_check real-input OK on the real KB / F2B; registration-1 version refuses with 123 entries) |
| AMENDMENT_1 reruns | guard test "guard test: 0 FAIL" (35 cases); repair smoke final gate rc 0; render smoke 0 FAIL for 33 / 30 / 2 lines; chain smoke "read rc 0" with the amended queue (all relay, gate, negative and repeat lines as above) |

## 8. Checks a reviewer should rerun (CPU, nice 19)
1. `bash H3/t3b_codeproof.sh cba7fbdf5df1579d6efb1168eb292e637bc9fad6 <out>` (0 FAIL) and `NEG=1 ...` (exactly the 2 tampered items FAIL); read the T3b hunks
   (`git -C /home/noob/work/bench_wt_t3b diff 4710e9f cba7fbdf5df1579d6efb1168eb292e637bc9fad6 -- bench scripts`).
2. `cd /home/noob/work/bench_wt_t3b && python -m pytest -q tests/test_bench_t3b.py tests/test_bench_cq_sealed.py tests/test_bench_cq_final.py tests/test_bench_opening_read.py`; `cd H3 && python -m pytest -q t3b_verdict_test.py`.
3. `bash H3/t3b_render_smoke.sh <dir>`, `bash H3/t3b_testmode_guard_test.sh <file>`, `bash H3/t3b_train_smoke.sh <dir>`,
   `bash H3/t3b_repair_smoke.sh <dir>` (about 1 min), `bash H3/t3b_chain_smoke.sh <dir>` (about 30 min).
4. `python -I H3/t3b_make_lists.py <draft> <E1 list> <new dir>`: LISTS.md5 5c86318a again; read the half algorithm.
5. The rule against the lead's design (brief of 21 Nov 14:40) and the proposal; the power numbers (section 11).
6. That nothing reads a sealed label or prediction before step 3 / step 12: grep H3 for masks / ignore / relay paths (register:
   md5sum only; build: after REG_MD5; read: after every refusal).

## 9. Points for the lead (my recommendation first; built as recommended)
1. **Interval with 3 seeds (lead's design):** each arm has 3 out-of-fold composites (5 fold models each); the seed-aware
   bootstrap resamples 3 per arm, so the interval is coarse. Kept as primary; the fixed-model interval is printed beside.
2. **Width reaches relF1@2 a little:** E1 labels are about 1.5 x wider; relR@2 can rise when a model predicts wider. It is
   much less width-sensitive than strict IoU. Any-hit recall (width-free) is printed beside. An any-hit co-guard was not built.
3. **ZS provenance:** ZS models ran steps 1 to 18,000 under F and the rest under F2 by resume (FINAL_RULE_ADDENDUM_1). T3b
   models run fresh under K, whose training path is byte-equal to F2. The difference is GPU atomics noise only (S). Disclosed.
4. **Label map:** as specified (24 -> 2, 29 -> 1, 25..28 -> 255, ignore -> 255). Every kept px is asserted < 24 (the scorer's own
   assert) and every ignore px is 255, so the label = where(ignore == 0, mask, 255) and the class map changes no output px.
5. **MAXC** (N11, lead's ruling): the lead decides MAXC at arm; arm refuses more than the GPUs with < 4096 MiB used then. The
   reviewer saw 1 such GPU at 01:0x (33 runs would take about 63 h at MAXC 1); Q1/MAXC can be raised live.
6. **Kept on cv02 after unstage:** the 33 run dirs (models, about 32 GB; no E1 file). Removing latest.pth is the lead's call.
7. **Registration** copies the 106 E1 images into IO/stage before the ledger row (as opening #8). No label is read before
   step 3.
8. **Half arm** is per fold (not a nested global half): ALL - HALF mixes "how many" with "which images" (descriptive only).

## 10. Not tested
- Anything on cv02 or a GPU: deploy of K, check / stage / render / arm / status / unstage against cv02 (stage, dt_check,
  ds_check and unstage ran through a stub ssh on scratch dirs in the chain smoke; render ran K's real cq.sh locally), GPU
  memory and time of a T3b run (same card and steps as fin's C2: 8,638 MiB on cv02, E log.md 18 Nov 05:49), the relays.
- The real registration, build, relays and read (they ran on synthetic dirs in TEST_MODE; the relays through a stub ssh).
- The repair path on cv02 (repair_aside, place_r ran through the stub; render_r / arm_r need KB's CODE.md5 and were not run;
  the repair line rendering ran through K's real cq.sh in the render smoke). The full 20,000-step training (the train
  smoke ran 8 steps at 128 px through every phase: averagers, final validation, finalize, BN re-estimate, save, test eval).

## 11. Evidence (H3/evidence; MD5_evidence.txt 3f5e24c0bcc8157df015014b44ddaf13, 87 files)
- pytest_full_K_cba7fbd_round1.log (938 passed; round 1), pytest_full_K_cba7fbd.log (round 0), pytest_full_K_4ea4bf8_superseded.log
- codeproof.out (0 FAIL), codeproof_negative.out (2 tampered items FAIL)
- t3b_verdict_test.out (27 passed), verdict_mutants.out (M9, run ids, fa_cells: each caught)
- train_smoke/, render_smoke/ (incl. rendered_repair.txt, jobs_repair.txt), testmode_guard_test.out (35 cases, 0 FAIL)
- repair_smoke/ (repair_smoke.out and the step outputs), chain_smoke/ (round 1: chain_smoke.out, relay_train.out, relay_deploy.out,
  relay_dump.out, gate outputs, negatives, verdict_synthetic.txt, read_t3b_synthetic.txt, MD5_synthetic.txt), chain_smoke_round0/
- rule_edit_round1.diff (the N9 line), lists_rerun.out
- amend1/ (AMENDMENT_1): t3b_queue.sh.reg1_cad952c0 and t3b_register.sh.reg1_547fc3a7 (the registration-1 scripts), their diffs to
  the amended ones, kbcheck_smoke.out, realinput_audit.out

## 12. Files and md5
| File | md5 | Role |
|---|---|---|
| T3B_RULE.md | 0c006d4466f0312f4ca01184ea52a95a | the rule (pin in the review; t3b_register.sh RULE_PIN); round 1: one line (N9) |
| t3b_make_lists.py | 47b1dbc64eee6f14d9c580da6005d495 | frozen fold / half lists (done; lists/) |
| lists/LISTS.md5 | 5c86318a0d3c628bf3f9711fe7081fb5 | md5 list of the 15 list files |
| t3b_make_jobs.py | 84649917b572e2201215cb8854de85ed | job lists (33 + 30) |
| t3b_rendercmp.py | d6eec93f53818d3dbb0151845dac1ef4 | render check (train, repair, dump) |
| t3b_register.sh | 8cecc85158c258d1462058a8fb1c23c3 | step 1: registration (pins the rule, job maker, lists and the 7 scripts; 'scripts' line) |
| t3b_queue.sh | 51a962379bd0399c2ae5a4c90b85bb7b | steps 3, 5 to 11, 13 and the repair path: build, check, stage, render, place, guard, arm, status, gate, render2, place2, arm2, unstage, repair_register, repair_aside, render_r, place_r, arm_r |
| t3b_label_precheck.py | 214d087dbcca133768c1846913567113 | N8: all 106 labels checked in memory before the build writes |
| diskguard8.sh | 0fe96ad9b0208bf6381f2bc5ee7b60b4 | cv02 disk guard 8 for t3b / t3bopen |
| t3b_relay.sh | 2870fd4365c5d8b642119a37261d8b08 | relays train / trainrep / deploy / dump (relay_w1c.sh 74a2ec3d unchanged; per-mode NAMES_RX) |
| run_t3b_read.sh | e4cda97aca7c3d2539bd3eecd14c845c | step 12: the read |
| t3b_verdict.py | 7dee83d6634baba74c85df448d84f42f | the rule applied to the read |
| t3b_verdict_test.py | 86769fac66228aa140793e6ff6075597 | verdict tests (27) |
| t3b_smoke_synth.py | 074eba73a9013c1cee4f2feea7e29859 | synthetic data for the smokes |
| t3b_chain_smoke.sh | d9532cb0f5f5dcd00296ff3efbceccf2 | builder's chain smoke (done) |
| t3b_repair_smoke.sh | 3f37412538eaeaeedaf002a0aa1e11bf | builder's repair / relay smoke (done) |
| t3b_render_smoke.sh | 44da6eee4e786bfc2be6bf5dda2971f1 | builder's render smoke (done) |
| t3b_train_smoke.sh | b999f9969ae6f718de1be271151b0aea | builder's training-path smoke (done) |
| t3b_testmode_guard_test.sh | 7209c8078be7e9b1424919141f59b127 | TEST_MODE guard negatives (done) |
| t3b_codeproof.sh | 2c9a073d69f8cdf4757a578560f930dd | code proof of K (done) |
| AMENDMENT_1.md | 937a6cbf5a1b6deebf46ce963723fb46 | AMENDMENT_1: kb_check line order, re-registration (registration 2), lead steps |
| t3b_kbcheck_smoke.sh | 61d0852b80f9bb9474d1d95911f01464 | AMENDMENT_1 order smoke (done) |
| t3b_realinput_audit.sh | bd84f5e7a9755f60aff868a71209f488 | AMENDMENT_1 read-only audit of the real cv02 / NAS inputs (done) |
| t3b_set_pins.py | c2230304a54f5285c37e56b4f43458cc | builder's pin writer (not part of the procedure) |
| evidence/ | 3f5e24c0bcc8157df015014b44ddaf13 (MD5_evidence.txt, 87 files) | outputs of section 7 |

Pinned inside the scripts: K and its tree (register, queue, relay, read), F2 / G / R (register, read), T3B_RULE.md, t3b_make_jobs.py, LISTS.md5 and the 7 scripts of the 'scripts' line (register), diskguard8.sh and t3b_rendercmp.py (queue, also via the 'scripts' line), PINS = 22 deployed files of KB and DW = KB's CODE.md5 diff to F2B (queue), K's bench_infer.py 149e2a63 and G's a3268638 (read), opening #8 REGISTERED.txt 4c783a77 (register), opening_verdict.py 433f61de (verdict), relay_w1c.sh 74a2ec3d (relay), bench_data DEPLOY.md5 d6063fd8 (queue), pool532_v11 pins d374fd84 / 79816ba6 / 33e65b3f (K's builder).
