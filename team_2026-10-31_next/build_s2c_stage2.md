# SKR2C stage 2 build (runner 12 Nov; runner2 13 Nov 17:1x; runner3 13 Nov 23:35 to 14 Nov): BUILT and FROZEN, NOT OPENED

Protocol: `protocol_SKR2C.md` 663de96d (v1 LOCKED 91b76abd + §9). Rulings: `rulings_s2c_stage2.md` (team-lead, 13 Nov 17:12). Tags: E = measured, S = judgement.

**State.** The opening set is built, staged on gaint `/home/noob/work/s2c/open/` (27 files) and frozen: **FROZEN.md5 `836be7e50c509339266097f4ba712f67`** (27 files; md5sum -c OK on gaint and on the laptop copy `scripts/s2c/opening/FROZEN.md5`; gaint files made read-only). Pre-opening gates on this exact set: **GATES PASS** (run 3, §4b). Registered (status: registered, NOT opened) in `e1_openings.md` (#7) and `../team_2026-11-12_frontier/benchmark/test_openings.md` (row 18). **Nothing was opened: no SKR2C test or E1 number exists.** No GPU was used. Next: independent review (coach role), then team-lead runs the command in §7.
- gaint writes, all by runner3: `s2c/open/` (the set + FROZEN.md5) and `s2c/open_check/` (gate outputs). No worktree, experiments dir, bench path or frozen set was written.
- Processes started on gaint (all ended, sessions gone): gates run 1 tmux `s2c_gates` (bash PID 1485249, its D python 1487555), run 2 `s2c_gates2` (bash PID 1545754), run 3 `s2c_gates3` (bash PID 1601068). Nothing of mine is running. Also one 1 s argparse test (`open_check/gates1/argtest.py`, CPU, nice 19).

## 1. First check (E, gaint, 12 Nov 20:10 to 20:25 IST): clean
- **Queue log** `s2c/launch.log` 5d2544a7 (read in full; it holds no metric): armed line with jobs 0839f340, lib 4edcae9e, SPLITS 24568cdb. For all 10 runs: `config OK` and `startup line OK ... val: 54  test: 54`, `trained <run> rc=0`, `done <run>: 'step 20000/20000' lines 1, Traceback lines 0`. End line `[Tue Nov  3 11:24:04 AM IST 2026] S2C ALL TRAINED (10 rc 0 of 10; pid 2345125, s2c_jobs.txt)`.
- **Auto-stop** `s2c/autostop.log` 38dd4f0b: guard start 03:05:59, `end line seen` 11:24:05, `guard stop (queue ended)` 11:25:05. No trigger. No `s2c/HOLD` file. All 10 `pids/*.rc` = 0.
- **Deployed md5s** unchanged: jobs 0839f340, exp_SKR01 1343cca2, exp_SUPPF dc9c344a, lib 4edcae9e, guard 334742d6, queue de31c533, gpumem 06791cdd, make_jobs e7d20e79.
- **Run dirs**, by counts only: `grep -c 'step 20000/20000'` = 1, `grep -c Traceback` = 0, `grep -c 'Labelled:'` = 1 in every stdout; `config_used.yaml` has `root: /home/noob/work/s2c_root` and `seed: K`; each has `checkpoints/latest.pth` and `best.pth`.
- **Training root**: `s2c_root/splits/test.txt` 9dcccf00 = val.txt. So every "test" number in the stdouts and `metrics.json` is a val number. Real test list: el_f3 and el_thin `data/splits/test.txt` a31fad14 (50 lines), val 9dcccf00 (54).
- **Worktrees**: el_thin HEAD = REVISION = c9bbb02, el_f3 HEAD = REVISION = e544133, 0 tracked changes in both.

## 2. Frozen sources (E): intact
- **R source**: gaint `/home/noob/work/s2q/open/FROZEN.md5` fb5becd2, `md5sum -c` 24 / 24 OK (re-checked 13 Nov 23:36). `s2_settings.sh` af791321 fetched from gaint (the laptop copy eed2fdcc is the placeholder version).
- **D source**: gaint `el_f3/reports/skr2e/skr2e_infer.py` 5ba3c597, `skr2e_run.sh` b2816cb3 (fetched 13 Nov, md5 equal); laptop `scripts/skr2e/skr2e_boot.py` 7520afc0.
- **Opened reference files** (md5 of MANIFEST.md5): PF2 post 3827f7c0, S2 post bd671e26, HC post d5c39e0d, THIN post 5d3f5b31, SKR2E out 9b43e636. All re-checked by gate A (§4b).

## 3. Key finding for the real-splits rule (E, code read on gaint)
Every frozen scorer takes its split from the worktree (`<code>/data/splits`), never from the run's `data.root`; config_used.yaml is read only for `model`, `mean`, `std`, `input_size`. So no frozen scorer needs a change to read the real test list; the protocol's assert is added around each pass (`s2c_realsplits.py`).

## 4. The opening set (E): gaint `/home/noob/work/s2c/open/`, laptop `scripts/s2c/opening/`, FROZEN.md5 836be7e5
| File | md5 | Kind | Source |
|---|---|---|---|
| s2c_settings.sh | 6766a6b0 | adapted | s2_settings.sh af791321 |
| s2c_post.sh | 2111dbef | adapted (verdict R driver) | s2_post.sh 039c1dc6 |
| s2c_e1_coprim.py | 7d40ba12 | adapted | s2_e1_coprim.py 6e08c084 |
| s2c_guards.py | 95312e8f | adapted (ruling 1) | s2_guards.py 0a8ea7dc |
| post_extra/s2c_b5w.sh | b80ca030 | adapted | s2_b5w.sh c4472057 |
| post_extra/s2c_scuffign.sh | 2baf71e5 | adapted | s2_scuffign.sh 662bf5dc |
| d/s2c_d_infer.py | 6fccdbdf | adapted (verdict D inference) | skr2e_infer.py 5ba3c597 |
| d/s2c_d_run.sh | 6f1d305f | adapted | skr2e_run.sh b2816cb3 |
| local/s2c_d_boot.py | 164ef377 | adapted (verdict D scorer, laptop) | skr2e_boot.py 7520afc0 |
| local/s2c_post_local.sh | 1da9a692 | adapted (pull + local readout) | s2_post_local.sh 0ec30d37 + skr2e_post_local.sh pull |
| s2c_opening.sh | fc809364 | new: the one driver (ruling 4) | |
| s2c_realsplits.py | 9af1af71 | new: real-splits assert | |
| s2c_named_boot.py | f227d00a | new: named claim condition 1 | pattern coach_s2_boot.py 7ea26cfb |
| s2c_ckpt_check.py | fab969ce | new: step / key-count gate | |
| s2c_gates.sh | ad0122f8 | new: pre-opening gates (not used by the opening) | |
| selftest_ref/coach_s2_boot.txt | 7ce0faa0 | reference copy | results/s2/coach_v/diag/boot.txt |
| s2_b5w_check.py 60423dde, s2_cellgate.py 0ed83bf5, calib_w/el_metrics_w.py 45b1df03, trackM/m0_analyze.py d5adbe6b, thin/thin_e1_relf1.py 98bcb979, post_extra/pf2_scuffign.py e3615fdb, post_extra/calib/{calib_dump.py c172717e, el_metrics.py 6e73ff11, pf2_b5_hook.sh e06dfc5f, pf2_b5_pooled.sh 873591ff}; s2c_copies.md5 1adcaeaa | = S2 frozen | byte copies | S2 set fb5becd2 |

Diff files (laptop only, not in the frozen set): `<file>.diff` next to each adapted file (unified diff vs its source).

### 4a. Every diff hunk and its reason (S2 / SKR2E sources; "labels" = docstrings, comments, output headers only)
- **s2c_settings.sh** (1 hunk, whole settings block): HC2 placeholders out (ruling 2); SUPPF becomes a settings arm with its own worktree el_f3 e544133, deploy file el_f3/REVISION, exp `s2c/exp_SUPPF.txt` dc9c344a, LA ec315d2e, rescore 1e41202b (protocol §6: both arms fresh); SKR exp -> `s2c/exp_SKR01.txt` 1343cca2; runs s10..14 for both; paths s2q -> s2c, plus DOUT / DLOG / OCHK; #5 S2 post (MANIFEST bd671e26) and #6 SKR2E out (9b43e636) as reference / self-test inputs; real-split, ext, training-root and launch.log md5s; HC syn / PF2 b5_work paths out (no comparator reuse); REQ = the SKR2C set; helpers without HC2; settings_check: names `s2c_<arm>_100pct_s10..14`, SUPPF fields filled.
- **s2c_post.sh** (6 hunks): (1) header + settings source + arms SKR01 / SUPPF + `rs()` real-splits helper + frozen_ok on s2c_copies.md5 + e1pass (fresh SUPPF m0, refs = #5 rows) + guardspass (no G3, no HC2) + new namedpass + cellgate 10 runs + b5rs / scrs; f51pass removed. (2) pass 0: REVISION message, FROZEN_s2c / settings copies, S2 and SKR2E MANIFESTs added, HC2 scorer lines -> SUPPF lines, rf / found md5s out (F51 gone), training root SPLITS and launch.log md5 added, launch.log conditions + no HOLD added, `rs pre` (real splits), PF2 / HC dump reuse checks out, pass 1b (HC2 synth) out; real-splits after pass 3. (3) m0 scorer for SUPPF = m0_audit d36f7438 + m0_audit_tau d77241bb (as PF2's own opening); real-splits after pass 4. (4) real-splits after pass 6. (5) b5 / scuffign renamed + real-splits after each; SHV1 (11) and F51 (12) passes out; guards; pass 14 named boot. (6) pre(): m0 dirs SKR01 / SUPPF; gpumem FAST touch out (no s2c logger runs now); `exit $rc` added (the driver starts D only on 0).
- **s2c_e1_coprim.py** (6 hunks): docstring note; arm runs s10..14 (refs stay s5..9); per arm run assert 74 crack-free cells and 296 GT comps (GT-only quantities); labels (2 hunks); a reported 10-seed view (s5-14 means, "5 of 10 seeds opened before", protocol §4). Self-test verbatim.
- **s2c_guards.py** (3 hunks): docstring note; runs s10..14; ruling 1: the SUPPF 3,931 refusal removed from the main path (it stays in the self-test, which still asserts mean 3,931), the G2 E1 bar is 1.5 x the fresh SUPPF mean (the existing ratio test), and the fixed 5,896 px bar printed as a reference line that decides nothing.
- **post_extra/s2c_b5w.sh** (6 hunks): header note; settings source; log line; both arms SKR01 + SUPPF through the frozen hook (no comparator reuse); "SUPPF remade from PF2 dumps" block and its `ops` check removed; table with `--old` for both arms; end label.
- **post_extra/s2c_scuffign.sh** (1 hunk): header note, settings source, arms SKR01 + SUPPF, gate label.
- **d/s2c_d_infer.py** (8 hunks): docstring; args `--esup` / `--m0ref-sup` / `--val-only` / `--id-ref` (no `--pf2e`, no `--gate-only`); b_mv grid -1.50..+0.50 step 0.05 and E1 sweep grid -1.5..3 step 0.25; arm keys E-SUPPF / E-SKR2 (E-PF / E-SKR2 in val-only); real-split md5s and an image-read log (`rd()`); refusal on a used out dir; run-name asserts per mode; gate (a) for each of the 10 members (was s5 only); no gate (c); D2 written as reported; b_mv on val with ruling 6 tie rule, written before any test / E1 read; val-only identity block vs #6 (ruling 5) that exits before any test / E1 read; per-cell files E-SUPPF b 0, E-SKR2 b 0 and b_mv; E1 sweep on the wider grid; checks: any-hit per arm + stems read == real lists (no E-PF identity vs PF2E).
- **d/s2c_d_run.sh** (1 hunk, short file): MODE idcheck | full; arms / m0 refs per mode; logs and PIDs outside the frozen dir (`s2c/` for full, `s2c/open_check/` for idcheck); refuses an existing out dir; PYTHONDONTWRITEBYTECODE; `exit $rc`.
- **local/s2c_d_boot.py** (11 hunks): docstring; labels LA_ / LB_ as module globals (defaults E-PF / E-SKR2 so the #4 / #6 self-tests stay verbatim) in pair / e1_concentration / matched (7 hunks); `dverdict()` with the SKR2C §3b wording; self-test (5) reproduces #6's b 0 pair block, E1 concentration block and matched-volume lines, (6) the wording on synthetic rows; main: one verdict pair at b 0, guards at that pair only, b_mv pair reported with CIs, E1 sweep lines, singles = fresh s10..14 m0, B5 line, `--json`.
- **local/s2c_post_local.sh** (1 hunk, rewrite of a short file): frozen-set check by the registered FROZEN md5; pull of post/ and d_out/ with MANIFEST md5sum -c on both ends; m2_rung tau 0 / tau 1 / scuffign on fresh SUPPF vs SKR01; collected outputs list of the SKR2C opening; s2c_d_boot.py run.

### 4b. Checks (E)
- **Local** (laptop python): `bash -n` 10 / 10 .sh; `python -m py_compile` 15 / 15 .py.
- **Local self-tests on opened files** (each prints PASS / FAIL lines, no unopened number): s2c_e1_coprim --selftest PASS (SUPPF s5-9 + HC s5-9); s2c_guards --selftest PASS (incl. SUPPF s5-9 crack-free mean 3,931); s2c_named_boot --selftest PASS (3 SKR01 - SUPPF lines == coach boot.txt 7ce0faa0 with RNG 20261102); s2c_d_boot --selftest PASS ((1) PF2E report 65 / 65 lines, (2)-(4) as SKR2E, (5) #6 b 0 pair block, concentration block and matched-volume lines verbatim, (6) wording).
- **Local wiring** (main paths on opened files renamed s10-14): e1_coprim co-primary + inactive lines == #5 e1_coprim.txt; guards G1 / G2 lines == #5 guards.txt; named boot (seed 20261102) == coach's 3 lines; d_boot verdict-pair block on #6's b 0 files == #6's block (labels mapped).
- **gaint gates** (`s2c_gates.sh`, CPU, nice 19, CUDA hidden):
  - run 1 (`open_check/gates1`, FROZEN 0db4877a, 23:50-23:57): A, B, C, D-identity, E PASS; C2 and D's real-splits step FAIL: gaint's python 3.12 `parse_args` refuses positional args after options (the laptop python accepts them). The same defect would have aborted R at pass 3 (`rs rescore`) after test numbers existed. Fixed by `parse_intermixed_args` (tested on gaint's python); `--wt` one value per flag (with nargs '+' it swallowed the DIR / run args). Run-1 D files kept in `open_check/gates1/run1_d`.
  - run 2 (`open_check/gates2`, FROZEN 1458bf19, 23:57-00:05): **GATES PASS**. Then the driver was changed (refusals no longer write opening.log, so a mistyped start can be corrected), tested locally with stubbed passes (bad arg / wrong md5 / existing post/: refused rc 2, no opening.log; R rc 1: D not run, end line R rc=1 D rc=-; R 0 + D 0: end line R rc=0 D rc=0 and d_out MANIFEST; D 3: rc 1), restaged.
  - **run 3 (`open_check/gates3`, FROZEN 836be7e5 = the final set, 14 Nov 00:05-00:12): GATES PASS** (A, B, C, C2, D, E as below). Run-1 / run-2 D files are kept in `open_check/gates{1,2}/run*_d`; run 3's in `open_check/d_val_identity` (+ copies in gates3/).
  - A integrity (= s2c_post.sh passes 0-2): worktrees, FROZEN + copies, 5 reference MANIFESTs, 22 / 22 external md5s, launch.log (10 config OK, 10 trained rc=0, ALL TRAINED, no HOLD), real splits pre, 'step 20000/20000' grep -c 1 x 10, config diff = exp file and seed K x 10.
  - B checkpoints: all 10 fresh runs step 20000, 350 state-dict keys, key set and shapes == pf2_SUPPF_100pct_s5 (prints step and key count only).
  - C R self-tests on gaint: e1_coprim, guards, named boot PASS. C2: every s2c_realsplits.py mode on the opened #5 (s2q/post, post_work) and #6 outputs.
  - Not exercised end-to-end (S, no defect known): `local/s2c_post_local.sh` (needs the opening's outputs; `bash -n` only, its D scorer and m2_rung are tested above) and the real GPU passes of `s2c_post.sh` (same frozen scorers and call forms as S2's opening; its pass 0-2 statements ran as gate A and every `rs` call form ran as gate C2).
  - D val-only identity (ruling 5) on the opened s5-9 members vs #6: gate (a) PASS for all 10 opened members (CPU fp32 vs GPU bf16 m0, tolerance 0.005 / 0.01); s5 gate lines, val cells at b 0 / 1 / 1.5 (54 each) and D2 sweep / bias / headline / drop == #6 exactly; read log: 108 reads, set val only, the 54 val stems (no test or E1 file opened); realsplits d --val-only: no E-* file written.

## 5. Design (S; built as designed, with the rulings)
Target on gaint: `/home/noob/work/s2c/open/`; R outputs `s2c/post/` (+ `post.log`, `post_pids.txt`, `post_pre.log`), work `s2c/post_work/` (B5 dumps), D outputs `s2c/d_out/` (+ `d_run.log`, `d_full.log`, PID files), driver log `s2c/opening.log`. Nothing goes into a worktree.
- R = S2's frozen set with the HC2 parts removed (SHV1, F51 / H36, G3, pass 1b; ruling 2; encoder cosines and the cell-gate line kept as reported), both arms scored fresh, the real-splits assert after every scoring pass, pass 14 = named claim condition 1 (seed-aware two-stage bootstrap, seed 0, 2,000, 71 clusters).
- Guards: G2 E1 bar = 1.5 x fresh SUPPF s10-14 mean; fixed 5,896 px bar as a reference line (ruling 1).
- Thin-term magnitudes: omitted; the verify carries "reported-only item of section 4 not produced: no frozen grep pattern existed; no verdict depends on it" (ruling 3).
- D = skr2e with one pair (b 0, b 0), b_mv (ruling 6 tie rule), no E-PF identity, E1 sweep from -1.5; gate (a) on all 10 members vs R's m0.
- Order: R (GPU passes through the shared gate, 9,900 MiB free each), then D on CPU only if R ends rc 0 (ruling 4). Then pull, local readout, coach's recompute.
- Dropped from S2: `s2_shv1.sh`, `s2_shv1_read.py`, `s2_f51.py`, `calib_syn/*`, `found/a8_screen_score.py`, `s2_postwatch.sh` (no watcher; manual start).
- **GPU memory** (E for S2's passes): one GPU process at a time, each needing 9,900 MiB free at its start; passes peak at about 4 to 6.5 GB. D is CPU only.
- **Wall time** (S): R about 70 to 80 min after the first gate pass (30 gated GPU starts at >= 120 s spacing; S2 took 82 min with the SHV1 / F51 passes); D about 20 to 30 min (the val-only identity run took 6.7 min; full adds 50 test + 106 E1 images x 10 models and a 19-point E1 sweep). Total about 1.5 to 2 h, plus any wait for free GPU memory (benchmark wave 1, tmux `bench_q_w1g`, holds the GPU until about 00:30 on 14 Nov).

## 6. Questions: all ruled (`rulings_s2c_stage2.md`, team-lead 13 Nov 17:12) and applied
1. G2 E1 bar = 1.5 x fresh SUPPF s10-14 mean; 5,896 printed as reference (s2c_guards.py). 2. HC2 parts dropped as listed; cosines and cell gate kept. 3. Thin-term magnitudes omitted and disclosed. 4. No watcher; one driver started by team-lead via the shared gate; `s2c/open/`. 5. D val-only identity on opened s5-9 members: done (gate D). 6. b_mv tie rule: nearer 0, then smaller b (s2c_d_infer.py).

## 7. Opening command list (for team-lead only, after the independent review; NOTHING here was run by the builder)
**Registered (14 Nov 00:13 IST):** FROZEN.md5 `836be7e50c509339266097f4ba712f67` (27 files). Lines added to `e1_openings.md` (#7) and `../team_2026-11-12_frontier/benchmark/test_openings.md` (row 18): registered, NOT opened; same 50 test and 106 E1 cells, 3rd look for this contrast.
1. Pre-check on gaint (read-only): `md5sum /home/noob/work/s2c/open/FROZEN.md5` = 836be7e50c509339266097f4ba712f67; `cd /home/noob/work/s2c/open && md5sum -c --quiet FROZEN.md5`; `ls -d /home/noob/work/s2c/{post,post_work,d_out,opening.log}` shows none; `tmux has-session -t "=s2c_open"` fails (no such session).
2. **Start (the one driver):** `tmux new-session -d -s s2c_open "bash /home/noob/work/s2c/open/s2c_opening.sh 836be7e50c509339266097f4ba712f67"`. It waits at the shared GPU gate for >= 9,900 MiB free before each GPU pass (so it may idle until benchmark wave 1 frees memory), runs R, and runs D (CPU) only if R ends rc 0. Driver PID in `s2c/opening.pid`, R python PIDs in `s2c/post_pids.txt`, D PIDs in `s2c/d_run_full.pid` / `s2c/d_py_full.pid`.
3. Watch: `tail -n 3 /home/noob/work/s2c/opening.log` (end line `s2c opening done: R rc=0 D rc=0`); R's end line in `s2c/post.log`; `s2c/post/decision_rc.txt` lists the decision passes.
4. Pull + local readout, on the laptop (crampbook, where `results/` lives; the script ssh's to gaint itself): `bash /home/yugma/mtp/research/team_2026-10-31_next/scripts/s2c/opening/local/s2c_post_local.sh 836be7e50c509339266097f4ba712f67` -> `results/s2c/{raw_r,raw_d,local}`; refuses unless the end line reads R rc=0 D rc=0.
5. Then coach's independent recompute of R and D before any verdict to team-lead; then judge.
- Expected wall time: about 1.5 to 2 h after the GPU has 9,900 MiB free.
- If R ends rc != 0: D is not run; the opening is not repeated without a ruling (post/ exists, so s2c_post.sh refuses a rerun).
