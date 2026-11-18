# Review of the wave 2a gates and read script (independent reviewer, 17 Nov 2026, 04:03 to 04:27 IST)

**Verdict: PASS for the versions listed below (`run_read_w2a.sh` 5aac565d), with three steps for the lead before the read (items 2 to 4).**
History: my first verdict (04:20, this file at md5 e681edf7) was FIX with one code item on `run_read_w2a.sh` b3862159. The builder made that change at 04:21:08. I re-reviewed it by diff and re-tested it (item 1). The verdict holds only for the md5s in the table; the builder was still writing at 04:22:45.
The three gates implement section 8 and their numbers reproduce. The read command (arms, regexes, pairs, flags) is correct. No gate verdict changes: ema PASS, spd FAIL, swad OPEN until the seed-6 dump. No arm result was read by me.

I built none of it. All checks are my own commands on gaint, CPU only (`CUDA_VISIBLE_DEVICES=""`, nice 19, at most 8 workers). E = measured, S = judgement.
G = `/home/noob/work/bench_reads/w2a_gates`, R = `harness/w2a/read`.

## Versions reviewed (the verdict applies to these md5s only)
The builder changed files after I started (04:03) and again after my first verdict. I pinned them by md5 (E, md5sum and `cmp` against my copies at 04:10:24, 04:18:20, 04:20:07, 04:20:46, 04:21:37, 04:25:15, 04:26:47; at the last one all ten files equal the md5s below). Sections A to H were done on the first set (copies in `G/reviewed_files_rv/`). The three files that changed after 04:20:46 were re-reviewed by diff against those copies (copies of the new versions in `G/reviewed_files2_rv/`).

| File | md5 | Last changed (stat) |
|---|---|---|
| `R/run_read_w2a.sh` | **5aac565df12c2d470e4d421788645196** | 04:21:08. Differs from b3862159 (04:03:39, the version of sections A to H) in lines 92 and 95 only (E, diff). 2195192f (04:02) was never reviewed by me |
| `R/test_run_read_w2a.sh` | **643133df0f9b40f9cc0e3615eca294da** | 04:21:44. Differs from 1fa99e7e (04:04:01) by the new tests 3b to 3g, 9 (r9 added), 16, 16b (E, diff) |
| `R/preflight_now.sh` | 97f63cb2efe4fc8dd094ce208b945fac | 03:56:48 |
| `R/gate_ema_hash.py` | dba4931ba9c5084dcf7b819e08d7e065 | 03:39:12 |
| `R/gate_swad_prescreen.py` | c611a5a02a3dcb379748c2f97fc3e1a8 | 03:40:41 |
| `R/gate_spd_mech.py` | 7cbde648653179389f90cbf41fdc8343 | 03:43:24 |
| `R/w2agate.py` | 724e35ffe5fe854d5f91cbdeeb31e62d | 03:39:12 |
| `R/w2a_class_guard.py` | 1859f91afacef94885aa055759f2b32b | 03:58:43 |
| `results/W2A_GATES.md` | ad55b2ddc853cb8691e943eecd14c921 | 04:04:59 (the first version I read, 7,548 bytes, lacked the swad note and the rulings line; section G is on ad55b2dd) |
| `R/BUILD_NOTES.md` | 14a5e62cdc6004954fdaf9e534d15fed | 04:22:45. Differs from 305b2a27 (04:09:17) by two rows of the command table (E, diff). I checked the command table and the output md5s of section 6, not every sentence. Its section 6 still lists the script and test md5s of 04:01:45 (2195192f, 38057d00), which are out of date |

Gate outputs reviewed: `G/gate_ema_hash_r1` (txt bbea890a, json 03381e2b), `G/gate_swad_prescreen_r1` (txt 91ca4656, json 8673fdd1), `G/gate_spd_mech_r2` (txt 361b33c8, json 39592ca3), `G/gate_spd_mech_r1` (txt 9d3e895e).
Not covered: anything written after 04:26:47. The builder plans a swad re-run when dump job 62 lands (`gate_swad_prescreen_r2`) and then new versions of `W2A_GATES.md` and `BUILD_NOTES.md`. Those need a look at the diff against my copies: for the two write-ups only the swad (b) lines and md5 lists should move. Any further change to a code file needs its own diff.

## Was "must fix before the read": fixed in 5aac565d and verified
1. **The gate verdict lookup took files it should not take (b3862159). FIXED at 04:21:08.** Where: `R/run_read_w2a.sh:92` and `:94-95` (`gate_ok`).
   - Check of the fix (E):
     - `diff G/reviewed_files_rv/run_read_w2a.sh R/run_read_w2a.sh`: lines 92 and 95 only, and they are the two lines given below.
     - `bash R/test_run_read_w2a.sh G/testrun2_rv` (test 643133df on script 5aac565d, 04:21:57): 45 tests, 0 failed; the copy differs in the 5 intended lines.
     - My own cases, each in its own fixture folder (`G/testrun2_rv/m_rv`, 04:25:06): seven wrongly named folders holding PASS (`_rv`, `_r2_rv`, `_rerun`, `_review`, `_r2.bak`, `_r3x`, `_r`) beside r1 and r2 FAIL: REFUSED on r2 FAIL. `gate_spd_mech_r3` holding only `PASS`, holding `gate_ema_hash PASS`, holding two lines, or empty: REFUSED. No verdict folder: REFUSED. A proper `gate_spd_mech_r3` with `gate_spd_mech PASS`: accepted. `GATE_ACK=spd` on an OPEN verdict: read, `GATE_ACK.txt` written, mark twice in run.log.
     - `SHOW=1`: the read command of 5aac565d is byte-equal to the one of b3862159 (E, cmp). So sections A to H stay valid for 5aac565d.
     - Preflight on the real state with 5aac565d (04:22:09): auto would read rcs only (10 dumps rc=0, 10 manifests pass); the other five arms incomplete; `bench_reads/w2a` not created.
   - Cosmetic, no change asked: when the refused file holds only `PASS` or another gate's line, the refusal text prints "gate gate_spd_mech PASS (...r3/VERDICT)" after "REFUSED, gate not passed". It refuses correctly; the word is confusing.
   - What was wrong in b3862159 (E, on the test fixture, folder `G/testrun_rv`): the lookup was `ls -d G/<gate>_r*/VERDICT | sort -V | tail -1`, then the second word of the file. So:
     - a folder `gate_spd_mech_rv` or `gate_spd_mech_r2_rv` holding PASS wins over `gate_spd_mech_r2` FAIL, and `ARMS=spd` is read without GATE_ACK;
     - "newest" is by name, not by time: `_rerun`, `_review`, `_rv` sort after every `_r<n>`;
     - a hand-made `gate_spd_mech_r3/VERDICT` holding only `PASS`, or holding `gate_ema_hash PASS`, passes spd.
   - Why it matters: my brief told me to write my re-runs into folders "with the suffix _rv". The natural names (`gate_swad_prescreen_rv`, `gate_spd_mech_rv`) match the glob and would have become the verdicts the read uses. I named mine `chk_*_rv` to avoid this. The next person may not.
   - The change I asked for, now in the file (first tested by me on a copy, `G/testrun_rv/run_copy_fix_rv.sh`):
     - line 92: `f=$(ls -d $GD/${g}_r[0-9]*/VERDICT 2>/dev/null | grep -E "/${g}_r[0-9]+/VERDICT\$" | sort -V | tail -1)`
     - line 95: `[ "$(cat $f)" = "$g PASS" ] && { echo "$a: gate $g PASS ($f)"; return 0; }`
   - Still worth one look before the read: `ls -d G/gate_*_r*/VERDICT; cat G/gate_*_r*/VERDICT`. A folder `<gate>_r<number>` made by hand with the exact line still counts; the script cannot know who wrote it.

## Must do before the read (no code change)
2. **Close the swad gate.** `G/gate_swad_prescreen_r1/VERDICT` is OPEN (seed-6 dump of fold 0 not written at 04:18; dump job 62, 42 of 161 done). Until `G/gate_swad_prescreen_r2/VERDICT` says PASS, auto mode skips swad. Command: `results/W2A_GATES.md`, section gate_swad_prescreen. Do not use `GATE_ACK=swad` in place of the closing run: that would mark a passed arm as "descriptive only".
3. **Run only the reviewed script, and only when the dumps are complete.** The script has had three versions this morning (2195192f until 04:03, b3862159 from 04:03:39, 5aac565d from 04:21:08). The lead's log line of 04:03 names 2195192f. Before the read: `md5sum R/run_read_w2a.sh` must give 5aac565df12c2d470e4d421788645196 (or `cmp R/run_read_w2a.sh G/reviewed_files2_rv/run_read_w2a.sh`). If it differs, diff it against that copy first.
   Auto mode reads whatever is complete. Started now it would read rcs alone and take the folder `bench_reads/w2a`, which the full read then cannot use (E, preflight 04:22:09). Run `bash R/preflight_now.sh <new dir>` first (with the `GATE_ACK` you intend) and start the read only when its "ARMS=auto -> ..." line names the arms you want.
4. **Decide what the swad VERDICT file means (ruling 4), only if the closing run is not PASS.** The gate scripts check all 10 runs and state the fold 0 seed 5 verdict, as ruled. But the VERDICT file, which is what the read script uses, holds the stricter rule: swad = (a) on all 10 runs and (b) on both fold-0 seeds (`gate_swad_prescreen.py:161-173`); spd = C1 and C3 on all 10 runs, C2 on the matched run (`gate_spd_mech.py:186-192`). The two rules agree for spd (FAIL both). For swad they differ now (file OPEN, fold 0 seed 5 PASS) and would differ if seed 6 fails (b). The stricter rule can only block more, never pass more. If r2 says PASS, nothing to decide.

## A. Gate definitions against section 8
| Section 8 sentence | Code | Implements it | Builder's interpretation |
|---|---|---|---|
| ema: raw `models[model]` of w2a_ema_f<k>_s<s> = w1g_pf_v11_f<k>_s<s> bit for bit, hash of two checkpoints, no metric | `gate_ema_hash.py:99-108`, `w2agate.py:80-85` | Yes (E). All 10 pairs, `latest.pth`, step 20000 asserted, bytes of every tensor, plus one sha256 per state dict | None |
| swad (a): training loss over 15k-20k not above PF's at 10k | `gate_swad_prescreen.py:48-64` | Yes (E). Mean of the 100 log lines N = 15050 to 20000 <= PF's log line at N = 10000, same fold and seed. Direction right | S: "over 15k-20k" read as the mean; "PF's at 10k" read as one 50-step line. Under the reading "no 50-step line above PF's line" runs would fail: 0 to 16 of 100 lines lie above, per run (E, json). I accept the mean: the spec (T1 line 98) wants to catch divergence, and one PF line moves by 0.045 to 0.089 |
| swad (b): swad_bn fold-0 crack relF1@2 >= PF raw - 0.05 | `gate_swad_prescreen.py:91-117` | Yes (E). `bench_score.py records --labels v11` on `w2a_swad_f0_s<s>.swad_bn/cv5v2_f0` and `w1g_pf_v11_f0_s<s>/cv5v2_f0` (weights key model), `summary`, key `arms.<arm>.subsets.all.relF1_2.mean`, test `d >= -0.05` | Argmax; all 107 fold-0 cells (not the 416 clean subset); both fold-0 seeds |
| swad (c): report layer3 / layer4 cosine at 20k | `:127-144` | Yes (E). Not pass / fail | None |
| spd C1: layer3 / layer4 cosine to init >= 0.8 at 20k | `gate_spd_mech.py:172` | Yes (E). Both stages, all 10 runs | None |
| spd C2: >= 0.1 above w2a_spdctrl_f0_s5 | `:173-174`, `:190` | Yes (E). spd minus control, both stages | S: both stages must clear 0.1; rule on the matched run (ruling) |
| spd C3: conv1 / layer1 deviation > PF's | `:175` | Yes (E). Probe's `dev` = \|\|W - W0\|\| / \|\|W0\|\|, PF of the same fold and seed, strict > | S: "deviation" = `dev`; 1 - cosine gives the same 10 of 10 |
| rcs, soft_band_jml, jml_hard | no gate script | Status taken from section 8 (builders x1, x2) | E, mine: the sampler line of the 10 trained rcs runs: `px_mult inactive` 2.34 to 2.79 (>= 1.5), `max_cell_mult` 2.86 to 3.31 (<= 5), kept 13 of 13 classes, never_drawn 0 |

Thresholds 0.8, 0.1, 0.05 and the windows are the ones of section 8, `cards/T1_recipes_spec.md` lines 98 and 131, and `cards/WAVE2_REVIEW.md` lines 59 and 60 (E, read).

## B. gate_ema_hash: PASS
- E: re-run into `G/chk_ema_hash_rv` (04:05:24 to 04:05:49, rc 0): txt equal to `gate_ema_hash_r1` except the two time lines; json equal except `seconds`. 10 of 10 EQUAL, verdict PASS.
- E, my own script (not using the builder's code): the two files of each pair are different files (different inode, 418 MB against 940 MB, no symlink, different md5); `cfg` run names are `w1g_pf_v11_f<k>_s<s>` and `w2a_ema_f<k>_s<s>`, same seed, step 20000 both; 350 keys in the same order, 292 float tensors, 26,096,530 elements; bytes equal in all 10 pairs; a second digest (unsorted keys) equal. The file md5s equal the ones in the builder's json.
- E: `model` is the raw readout. Inside each ema checkpoint `raw_bn` differs from `model` in 174 tensors (BN running statistics only), `ema_9998` in 292, `ema_9998_bn` in 350.
- E: `scripts/bench_infer.py:152` dumps from `checkpoints/latest.pth`, the file compared.
- Can it say EQUAL for different weights? S: no. No path fallback (`w2agate.py:83`). Keys in only one dict make the pair DIFFERENT (`gate_ema_hash.py:38,55`). The hash and the key comparison must agree (`:108`). The self-test finds one float step in one element.
- Note: if a 0-dimension tensor (`num_batches_tracked`) ever differed, line 48 would raise (E: numpy refuses the view). The gate then writes no VERDICT, so it fails closed.
- Limit: the checkpoint md5 is tied to dump manifests for the 10 PF dumps and the 10 seed-5 ema dumps only; the seed-6 ema dumps did not exist yet.

## C. gate_spd_mech: PASS (the gate verdict FAIL stands)
- E: re-run into `G/chk_spd_mech_rv` (04:05:59 to 04:06:20, rc 0): txt equal to `gate_spd_mech_r2` except the time lines; json equal except `seconds`. r1 and r2 have equal `spd`, `pf`, `ctrl`, `checks` blocks; only the C2 rule differs.
- Same function: `stage_stats` and `encoder_weights` are imported from `bench_wt_w2/src/trainers/enc_probe.py` (a431e5d3; tree at c57508e, 0 tracked changes). The trainer calls the same function (`enc_probe.py`, `maybe_log`).
- Same init, same tensors (E, my own script): I took W0 from the SPD anchors that the training run `w2a_spd_f0_s5` stored in its checkpoint (108 encoder parameters, 36 with 2 or more dimensions), not from a rebuilt model, and computed cosine and deviation with my own numpy code. Result: the 20 PF rows equal the builder's json within 1.2e-13; the 10 spd rows equal each run's own step-20000 probe row within 1.6e-14; the control within 1.9e-14. So the claim "reproduces the 21 probe rows" holds, and the PF pass is the same quantity.
- E: control config: `adam_spd`, lambda 0.0, lr_mult 1.0. spd config: lambda 1.0, lr_mult 1.0.
- C1, C2, C3 from my numbers: C1 0 of 10; C2 7 of 10, fold 0 seed 5 passes (+0.1568 / +0.1069); C3 10 of 10. Same per-run flags as the builder (E).
- Verdict logic (`:186-192`): FAIL if any of C1, C2, C3 fails. C1 fails on every run by more than 0.2, so no reading of the rule changes the verdict (S).

## D. gate_swad_prescreen: PASS for (a) and (c); (b) seed 6 left OPEN
- Parsing (E): the trainer writes one line per 50 steps, `step N/20000  loss=X ...`, X = mean of the 50 steps since the last line (`trainer.py:843-861`, window reset at 861). Both logs hold 400 such lines. The regex cannot match the `PF encoder lr` or `ENC probe` lines.
- Window (E): 100 lines N = 15050 to 20000 = steps 15,001 to 20,000, equal weights. PF side: line N = 10000.
- E, my own computation from `metrics.json` `train_curve` only: same 10 verdicts and the same full-precision values as the builder's json. swad mean 0.299 to 0.319; PF at 10k 0.317 to 0.375; swad minus PF -0.059 to -0.018 (closest fold 3 seed 6); against PF's 1,000-step mean -0.046 to -0.035. swad lr is 0.001 at 10k and 20k; PF's is 0.00051 at 10k and 0 at 20k. No run has a resume.
- (b) (E, code read): cells = the 107 cells of `cv5v2_f0`; operating point = the dump's argmax; key `relF1_2` = pooled crack relF1@2 (`bench/score_ext.py`, `summarize`); arm regexes are full matches (`bench_score.py:199`). A dump is scored only if its job has `rc=0` in the dump log and its manifest exists. The txt prints PASS / FAIL / OPEN and "value not shown".
- (b) seed 6: the dump `w2a_swad_f0_s6.swad_bn` did not exist at 04:18. Not run by me. OPEN.
- Note: `G/gate_swad_prescreen_r1/b/sum_f0_s5.json` holds the fold-0 values of swad_bn seed 5 and PF. The gate does not print them, but the file is on disk. I did not open it.
- Note: `w2agate.py:103` would raise on a run with a non-empty `resumes` list (E: `int(list)`). No run has one. Fails closed.

## E. run_read_w2a.sh (checks run on b3862159; 5aac565d differs in `gate_ok` only and gives the same read command, see item 1)
- Flags (E, against `parse()` of `bench_read_w1.py` fdb56b78): `--arm`, `--pair`, `--labels v11`, `--workers 8`, `--cache`, `--baseline PF`, `--aa`, `--score-exclude`, `--out` all exist. No `--dry`, no `--allow-partial`. Same options as `run_read_rows2.sh`, plus explicit pairs.
- Regexes (E, `re.fullmatch` as `bench/w1read.py:64` uses, against the 161 run ids of `bq/w2a2/dump/jobs.txt` and the one of `bq/w2a3/dump/jobs.txt`): each of the 12 wave 2a arms selects exactly 10 run ids, one weights key, 10 distinct (set, seed). `w2a_ema_f[0-4]_s[56]` does not match `w2a_ema_f0_s5.raw_bn`; `...\.raw_bn` does not match `w2a_ema_f0_s5`; `\.swad` does not match `.swad_bn`; `\.ema_9998` does not match `.ema_9998_bn`; `\.ema_9998_bn` does not match `.ema_999_bn`; `w2a_spd_...` does not match `w2a_spdctrl_f0_s5`. PF selects 10 of the 20 PF run folders (seeds 5, 6), PFAA all 20.
- Pairs (E, SHOW=1): PF=RCS, RAWBN=EMA, PF=JMLHARD, JMLHARD=SOFTBAND, PF=SWADBN, SWADRAWBN=SWADBN, PF=SWADRAW, PF=SWADRAWBN, PF=SWAD, PF=SWADEMABN, PF=SWADEMA, PF=SPD. `--pair A=B` is B minus A (`bench_read_w1.py:173-177`). These are the pairs of section 8; RAWBN=EMA is the pre-declared one (`WAVE2_REVIEW.md` line 58).
- Rulings: (1) PF = seeds 5, 6; PFAA only in `--aa PFAA:5,6:7,8`; `PF4=1` goes to `w2a_pf4<_TAG>` with `SENSITIVITY_PF4.txt` and two lines in run.log. (2) auto mode skips an arm whose verdict is not PASS; GATE_ACK reads it, writes `GATE_ACK.txt` and marks run.log at start and end. (3) JMLHARD=SOFTBAND; softband alone is refused. All E (builder's test and my runs). (4): see item 4.
- Builder's test (E): `bash R/test_run_read_w2a.sh G/testrun_rv`: 37 tests, 0 failed, 04:10:36 to 04:10:46 (test 1fa99e7e on b3862159). Again at 04:21:57 into `G/testrun2_rv`: 45 tests, 0 failed (test 643133df on 5aac565d). The copy differs from the script in the 5 intended lines both times.
- Completeness (E): missing dump, dump job with last line rc != 0, no `trained` line, symlinked run folder, wrong weights key in a manifest: all refused in the test. The job-name grep cannot confuse `dump_w2a_ema_f0_s5` with `dump_w2a_ema_f0_s5_raw_bn` (the name must be followed by ` rc=`). A stopped run: its dump fails on the step assert (rc != 0), and the manifest check asks for step 20000.
- Preflight (E, 04:11:47, real logs and verdicts): "no arm to read", every arm incomplete, rc 1, `bench_reads/w2a` not created. At 04:22:09 rcs had become complete: auto would read rcs alone (item 3). Named arms (`ARMS=spd`, `"jmlhard softband"`, `softband`): REFUSED, incomplete. `DRY=1` is refused by the preflight.
- Output folder (E): the real script with `DRY=1 TAG=2` stops with "output folder exists: G/dry2", rc 1.
- Worktree check (E, lines 47-49): HEAD b5bf0ae, 0 tracked changes, `bench_read_w1.py` fdb56b78. `bench_wt_b` has 0 untracked files that are not ignored.
- CPU only (E): `CUDA_VISIBLE_DEVICES=""`, `OMP_NUM_THREADS=1`, `PYTHONDONTWRITEBYTECODE=1` exported at line 51; nice 19; 8 workers.
- Exclude list (E): `benchmark/splits/score_exclude_v3.txt` 6d48dfbd, checked at line 53; in the DRY run 532 -> 416 stems, 116 left out.
- cv02 (E): dump roots are fixed gaint paths; run folder and set folder must not be symlinks; one device string over PF and the arms. At 04:12 all 39 wave 2a manifests name a checkpoint under `/home/noob/work/bench_wt_w2/experiments/` and no folder on the three levels is a symlink. Note: the method folder itself is not checked for a symlink.
- DRY (E): `DRY=1 TAG=_rv`, 04:11:58 to 04:16:21, read rc 0, output `G/dry_rv` (113 MB). read.txt and read_x416.txt have the md5s of the builder's dry3; read.json equals dry3 except `seconds`. 35 runs: PF 10, PFAA 20, RCS 5. One contrast, three operating points, 2,000 draws, 330 groups. `x416` block present. No note lines. I printed structure and equalities only, no metric.
- A/A (E): `M` and the A/A block at OP-A and OP-F of the DRY read equal those of the four-seed read `bench_reads/w1g4` exactly. The A/A block at OP-W does not. Reason (E, `bench_read_w1.py:138`): PFAA seeds 7 and 8 are width-matched to the mean width of PF seeds 5, 6, not to their own. M is taken at OP-A (`:186`), so M is not affected.

## F. w2a_class_guard.py
- E: it imports `summarize` from `bench_wt_b/bench/score_ext.py`, the function the read's `guards()` calls (`crossfit_op.py:231`). Cells: the argmax records in the read's own cache, one file per run, pooled per arm and seed; it asserts the cell count equals `n_stems`; the clean set uses the stems in read.json. Classes 13 material, 16 splice, 20 edge_dark, 11 inactive (E, `bench.atlas.NAME`).
- E, run on `G/dry_rv`: 162 files before and after, md5 of the whole tree equal, so it changes no file of the read. A second run to the same output is refused. The 6 inactive rows equal read.json (`inact_iou`, `inact_prec`, `inact_rec`) within 4.2e-05 at 4 printed decimals. I did not open the table.
- Notes: argmax only, no interval, no pass flag (as its header says). It has no check of `PYTHONDONTWRITEBYTECODE`; `__pycache__` is git-ignored in bench_wt_b, so this cannot dirty the tree.

## G. results/W2A_GATES.md (ad55b2dd)
- E: every number checked against the gate txt / json files and against my own computations: 350 tensors, 292 of 350; 10 PF and 10 ema manifests; swad loss ranges, -0.059 to -0.018, fold 3 seed 6, -0.046 to -0.035, 0.045 to 0.089; bench_score.py f096aff7; job 62; swad layer3 0.827 to 0.832, layer4 0.782 to 0.810, 7 of 10; PF layer3 0.927 to 0.929, layer4 0.926 to 0.946; spd 1.2e-13; C1 0.584 to 0.598 and 0.526 to 0.564; control 0.441 / 0.443; +0.157 / +0.107; 7 of 10; +0.084 to +0.121, mean +0.105; C3 0.038 to 0.045 against 0.023 to 0.025, 0.79 to 0.82 against 0.189 to 0.191; 0.037; 36 tensors. All agree. The md5s of the gate outputs in BUILD_NOTES section 6 agree.
- It holds no arm result (E): training loss, encoder cosine and one PASS / OPEN on fold 0 only.
- One sentence is stronger than the evidence (S): "the ema arm's raw readout is PF itself, and the primary contrast ema_9998_bn minus raw_bn is a within-run contrast on PF's own weights". The gate shows this for `model`. The read's RAWBN arm is `raw_bn`, the same weights with recalculated BN statistics (174 buffers differ, E). So RAWBN is not the PF dump. The read has no PF=RAWBN and no PF=EMA pair; that follows the pre-declared contrast.

## H. Side effects
- E (04:13:05, 04:20:07 and at the end): `git status --porcelain -uno | wc -l` = 0 for bench_wt_w2 (c57508e), bench_wt_b (b5bf0ae), el_bench (31c0c36), bench_wt_final (89b9ea5).
- E: files newer than 03:33 in the project folder: only `R/*`, `results/W2A_GATES.md` and the lead's `log.md`. None in bench_wt_b, el_bench, bench_wt_final, or bench_wt_w2 outside `experiments/`; in `experiments/` only the dump queue's `dump_w2a_*.stdout`. Under `bq/` only the dump queue's own log, gpumem log and pid files.
- E: `/home/noob/work/bench_reads/w2a` does not exist.

## Note only (no change asked)
- N1. Within-run pairs get a wide interval. The tool draws the seed of each arm independently per fold (`paired_seeds False` in read.json; `crossfit_op.boot_pair`). For RAWBN=EMA and SWADRAWBN=SWADBN both arms are the same runs, so the interval holds seed noise that a paired draw would cancel. The flag is conservative: a null on the ema contrast is weaker evidence than it looks. The reviewed tool has no option for paired draws.
- N2. PFAA is an extra row in every table. Its OP-W rows and the A/A block at OP-W are not the values of the four-seed read (section E). Quote M only.
- N3. swad has 7 contrasts and each can print PASS*. Only PF=SWADBN is the pre-declared one (T1 spec, arm 3); the other six are descriptive. Carry the layer4 note of W2A_GATES beside any swad result.
- N4. The GATE_ACK mark is in run.log and `GATE_ACK.txt`, not in read.txt or read.json. If tables are copied to `results/`, the mark must be copied by hand.
- N5. A failed manifest check (`:162`) comes after `mkdir` (`:149`). The output folder then exists with run.log only, and the next run without TAG is refused.
- N6. Completeness asks for all 6 readouts of ema (60 dumps); the read uses 2. One failed dump of an unread readout would block ema. Fails closed.
- N7. The guards of section 8 are not applied by the script: rcs crack judged at OP-F / OP-W only, crack-free false alarms, inactive precision and region precision, width. They are read off the tables by hand, as in earlier reads. Pairing of rcs with PF is not assumed by the bootstrap (seed draws are independent).
- N8. `G/dry`, `dry2`, `dry3`, `dry_rv` hold numbers of rcs seed 5; `G/gate_swad_prescreen_r1/b/` holds fold-0 values of swad_bn seed 5. Not results. Nobody should open them before the read.
- N9. After the dumps end, `gate_ema_hash.py --out G/gate_ema_hash_r2` (25 s) would tie the compared checkpoints to all 60 ema dump manifests. Worth doing. With 5aac565d its folder name `gate_ema_hash_r2` makes it the verdict the read uses, which is intended.

## Open items and limits
- swad (b), seed 6: OPEN (item 2). I did not run the closing command; the dump was not there.
- soft_band_jml: one run to retrain (queue w2a3); read later with `TAG=softband ARMS="jmlhard softband"`. I checked this path on the fixture only.
- I did not run the final read and did not look at any arm metric. The DRY read and the class-guard table were checked by structure and equality only.
- The read tool itself (`bench_read_w1.py`, `bench/w1read.py`, `bench/crossfit_op.py` at b5bf0ae) was read for the flags and the paths this script uses, not re-reviewed as a whole.
- S: expected run time of the real read with 5 arms (140 runs): about 20 to 30 min at 8 workers; cache about 0.5 GB.
- My files: this file; `G/chk_ema_hash_rv`, `G/chk_spd_mech_rv`, `G/testrun_rv`, `G/testrun2_rv`, `G/preflight_rv`, `G/preflight2_rv` to `G/preflight7_rv`, `G/dry_rv`, `G/reviewed_files_rv`, `G/reviewed_files2_rv` (about 120 MB in total). No folder of mine matches `G/<gate>_r*`. Own scripts and logs are in the session scratchpad only. No queue, tmux session or file under `bq/` was touched. No GPU, no network.
- Against "delete nothing": inside my own fixture `G/testrun_rv/fx/gates` I removed and rewrote fake verdict folders that I had made myself a moment before (04:11 and 04:17), to run the next case. No file of anyone else was deleted or overwritten. A later clean-up of the same kind in `G/testrun2_rv` was stopped by the session's safety check and not done; I used separate folders instead.
