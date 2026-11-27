# Wave 2a read: build notes (builder, 17 Nov 2026, gaint, user noob)

Task: build and run the three gates of `harness/LAUNCH_REQUEST_w2a.md` section 8 that were NOT BUILT, and write the read script. The final read was not run. No arm result was read or reported. Gate verdicts: `results/W2A_GATES.md`.
E = measured, S = judgement. Times are IST from `date` or from the logs named.

## 1. Files (md5 in section 6)
Code, all new, in `harness/w2a/read/`:
- `w2agate.py`: shared paths and helpers of the gates (log parsers, refuse-to-overwrite output).
- `gate_ema_hash.py`, `gate_swad_prescreen.py`, `gate_spd_mech.py`: the three gates. Each takes `--out <new folder>`, refuses unless `CUDA_VISIBLE_DEVICES=""` and `PYTHONDONTWRITEBYTECODE=1`, and writes `<gate>.txt`, `<gate>.json` and a one-line `VERDICT`.
- `run_read_w2a.sh`: the read script (for the lead, after review).
- `test_run_read_w2a.sh`: logic test of the read script on a synthetic fixture (37 checks; no dump, no metric, the read tool is never called).
- `preflight_now.sh`: shows which arms `run_read_w2a.sh` would read right now, against the real logs, manifests and gate verdicts, without running the read.
- `w2a_class_guard.py`: extra, not in the brief (section 5 below).

Outputs in `/home/noob/work/bench_reads/w2a_gates/` (G):
- `gate_ema_hash_r1/`, `gate_swad_prescreen_r1/` (with `b/`: fold-0 records of seed 5), `gate_swad_prescreen_r2/` (after the seed-6 dump, 04:59; `b/`: fold-0 records of seeds 5 and 6), `gate_spd_mech_r1/`, `gate_spd_mech_r2/`, `gate_swad_prescreen_t0_skipb/` (code test of parts a and c).
- `dry/`, `dry2/`, `dry3/`: the three dry runs of the read script (PF, PFAA, rcs seed 5; dry3 is the final script). They hold numbers of rcs seed 5. **Not a result; not opened by me** beyond the structure keys of read.json and the A/A margin of PF.
- `logs/`: console logs with start and end times.

## 2. Commands run (E)
All with `CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 HF_HUB_OFFLINE=1 nice -n 19`, python = `/home/noob/work/el-fault-detection/.venv/bin/python`, cwd `harness/w2a/read`.
| Time | Command | Result |
|---|---|---|
| 03:39:19 to 03:39:41 | `python gate_ema_hash.py --out G/gate_ema_hash_r1` | rc 0, PASS, 10 of 10 EQUAL |
| 03:41:14 | `python gate_swad_prescreen.py --skip-b --out G/gate_swad_prescreen_t0_skipb` | rc 0 (code test; (a) 10 of 10, (b) not run) |
| 03:42:34 to 03:42:51 | `python gate_spd_mech.py --out G/gate_spd_mech_r1` | rc 0, FAIL. In this run the C2 rule was "all 10 runs against the one control" (7 of 10, FAIL) |
| 03:43 to 03:43:38 | `python gate_spd_mech.py --out G/gate_spd_mech_r2` | rc 0, FAIL. C2 rule = the matched run fold 0 seed 5 (PASS), the 7 of 10 shown beside. All numbers equal r1 (checked: spd, pf, ctrl, checks blocks of the two json files are equal) |
| 03:47:22 to 03:47:35 | `python gate_swad_prescreen.py --out G/gate_swad_prescreen_r1` | rc 0, OPEN: (a) 10 of 10, (b) seed 5 PASS, seed 6 dump not there yet |
| 03:47:39 to 03:52:12 | `DRY=1 bash run_read_w2a.sh` (first version of the script) | read rc 0, 272 s. One script bug seen: the script's own md5 line (path taken after `cd`). Fixed |
| 03:53:33 to 03:58:03 | `DRY=1 TAG=2 bash run_read_w2a.sh` (script 2195192f) | read rc 0, 270 s; read.txt and read_x416.txt identical to the first dry run; read.json differs only in `seconds` |
| 03:54 | `bash test_run_read_w2a.sh <scratch>/rt1` | 27 tests, 0 failed (script 2195192f) |
| 04:04 | after the lead's rulings (GATE_ACK.txt and the descriptive mark; PF4 as a marked sensitivity read in its own folder): `bash test_run_read_w2a.sh <scratch>/rt2` | 37 tests, 0 failed (script b3862159, the final one) |
| 04:04:28 to 04:09:02 | `DRY=1 TAG=3 bash run_read_w2a.sh` (script b3862159) | read rc 0, 273 s; read.txt and read_x416.txt identical to dry2; no GATE_ACK.txt and no SENSITIVITY_PF4.txt in it, as it should be |
| 04:21 | review item 1 (`harness/REVIEW_W2A_READ.md` e681edf7): two lines of `gate_ok` changed (lines 92 and 95; only folders `<gate>_r<number>` count, highest number wins, the file must be exactly `<gate> PASS`). `bash test_run_read_w2a.sh <scratch>/rt3` | 45 tests, 0 failed (script 5aac565d, the final one). The same test against b3862159 fails 9 of 45, so the new cases catch the fault. `diff` of b3862159 against 5aac565d: lines 92 and 95 only |
| 04:22 | `bash preflight_now.sh <scratch>/pf2` (real logs, manifests, verdicts; no read) | auto would read rcs only (10 dumps rc=0, 10 manifests pass); the other five arms incomplete; rc 0; `bench_reads/w2a` not created |
| 04:59:09 to 04:59:35 | `python gate_swad_prescreen.py --out G/gate_swad_prescreen_r2` (after dump job 62 `dump_w2a_swad_f0_s6_swad_bn` ended rc=0 at 04:58:54) | rc 0, **PASS** under the stricter rule: (a) 10 of 10, (b) seed 5 PASS and seed 6 PASS. Parts (a) and (c) of the json equal r1 |
| 03:56:48 | `bash preflight_now.sh <scratch>/pf1` | "no arm to read" (no arm complete yet), rc 1, nothing written to bench_reads/w2a |
| 03:59 | `python w2a_class_guard.py --read G/dry2 --out <scratch>/class_guard_dry2.txt` | 29 lines; structure checked; inactive rows equal read.json (max difference 4.2e-05 at 4 decimals); values not opened |
| 04:00:59 | inline python: `bench.w1read.discover` + `check_comparable` + `assemble` of bench_wt_b on PF seed 5 and the seed-5 dumps `w2a_ema_f*_s5.raw_bn`, `.ema_9998_bn`, `w2a_swad_f*_s5.swad_bn` | the b5bf0ae loader accepts the readout suffix: 5 runs per arm, folds 0 to 4, right weights key, 532 common cells. No metric computed |

## 3. What the reviewer should check first
1. **PF and the A/A (lead's ruling, 17 Nov 04:03: keep as built).** The brief asks for "baseline PF = W1-G seeds 5, 6" and `--aa PF:5,6:7,8`. E: `bench_read_w1.py` takes both A/A seed sets from one arm (`set(s1 + s2) <= set(arms[arm_aa])`), so with a two-seed PF arm it prints "A/A seeds missing; no margin M". The script gives the PF folder twice: arm `PF` = seeds 5, 6 (the registered comparator, section 3; baseline of every PF pair) and arm `PFAA` = seeds 5 to 8 (used only by `--aa PFAA:5,6:7,8`). PFAA appears as an extra row in the tables. `PF4=1` makes PF the four-seed arm with `--aa PF:5,6:7,8` (as `run_read_w1g4.sh`); by the ruling that is a sensitivity read, never the verdict: it goes to its own folder `bench_reads/w2a_pf4<_TAG>`, and run.log (start and end) and `SENSITIVITY_PF4.txt` say so.
   Evidence that M from PFAA equals the M of the four-seed read (E; both at argmax, 532 cells, seeds {5,6} against {7,8}, 2,000 bootstrap draws). Files: `/home/noob/work/bench_reads/w2a_gates/dry2/read/read.json` (531965f5; `--aa PFAA:5,6:7,8`, tool fdb56b78 at b5bf0ae) and `/home/noob/work/bench_reads/w1g4/read/read.json` (59b367ff; `--aa PF:5,6:7,8`, tool b5c46550 at c57508e). Keys `M` and `aa/OP-A/metrics/<metric>/se`. M = max(0.01, 2 x SE). Every value is equal to the last digit:

   | Metric | M, dry2 (PFAA) | M, w1g4 (PF) | A/A SE, dry2 | A/A SE, w1g4 |
   |---|---|---|---|---|
   | crack_iou | 0.01 | 0.01 | 0.003778357285225381 | 0.003778357285225381 |
   | relF1_2 | 0.01 | 0.01 | 0.0031406447932049307 | 0.0031406447932049307 |
   | inact_iou | 0.054250748368647864 | 0.054250748368647864 | 0.027125374184323932 | 0.027125374184323932 |
   | miou_rob | 0.01 | 0.01 | 0.003226802541945905 | 0.003226802541945905 |
   | relP2 | 0.011533180703166545 | 0.011533180703166545 | 0.005766590351583272 | 0.005766590351583272 |
   | relR2 | 0.011285128633152258 | 0.011285128633152258 | 0.005642564316576129 | 0.005642564316576129 |
   | relF1_1 | 0.01 | 0.01 | 0.0035423438878292735 | 0.0035423438878292735 |
   | width_ratio | 0.037617607569998726 | 0.037617607569998726 | 0.018808803784999363 | 0.018808803784999363 |
   | fa_share50 | 0.011753772458395704 | 0.011753772458395704 | 0.005876886229197852 | 0.005876886229197852 |

   The delta, lo and hi of the A/A block at OP-A are equal too (largest difference 0.0). These are PF against PF values (the noise margin), not an arm result. On the 416 clean cells the dry read gives M of 0.01 for crack_iou, relF1_2, miou_rob and 0.0597 for inact_iou; w1g4 was run without `--score-exclude`, so there is nothing to compare that with.
2. **Gate enforcement in the read script (my addition; accepted by the lead, 17 Nov 04:03).** In auto mode an arm whose newest gate verdict is not PASS is skipped with a line in run.log; a named arm is refused. `GATE_ACK="spd"` reads it anyway. Such an arm is descriptive only: run.log says so at its start and end ("DESCRIPTIVE ONLY, NOT A SCREEN VERDICT" with the arm, gate, verdict and verdict file) and the output folder gets `GATE_ACK.txt` with the same lines. Reason (S): section 8 says the gates must pass before an arm's result may be read, and gate_spd_mech is FAIL. Arms without a gate here (rcs, jmlhard, softband) are not checked; their section 8 status comes from builders x1 and x2.
3. **Explicit pairs.** `--pair` switches off the tool's default "every arm against the baseline". So every contrast is listed in the script (header and lines 128 to 138): PF=RCS; RAWBN=EMA; PF=JMLHARD; JMLHARD=SOFTBAND; PF=SWADBN, SWADRAWBN=SWADBN, PF=SWADRAW, PF=SWADRAWBN, PF=SWAD, PF=SWADEMABN, PF=SWADEMA; PF=SPD. E: each arm regex matches exactly 10 run ids of `bq/w2a2/dump/jobs.txt` with one weights key (checked with SHOW=1 and re.fullmatch).
4. **Completeness rule.** An arm needs every dump job of the arm (all readouts: ema 60, swad 60, others 10) with `rc=0` as its last `trained` line over `bq/w2a2/dump/launch.log` and `bq/w2a3/dump/launch.log`, plus a manifest with the expected run id, fold, seed, weights key, step 20000, commit c57508e, fp32, and one device string over PF and the arms. So ema and swad become readable only when the second dump block has ended.
5. **gate_swad_prescreen (a): my reading of "PF's at 10k".** One log line (step 10000, a 50-step mean) against the swad mean of steps 15,001 to 20,000. The longer PF window is shown beside.
6. **gate_spd_mech C2.** Only one control run exists. r1 and r2 differ in the C2 rule only; the overall verdict is FAIL in both.
7. `gate_swad_prescreen_r*/b/` holds per-cell record files of the fold-0 dumps (PF raw and swad_bn). The gate prints pass / fail only.

## 4. Section 8 items that could not be done as written, and assumptions
- `--aa PF:5,6:7,8` with a two-seed PF arm: see 3.1.
- Section 8 writes the swad and spd pre-screens for fold 0, seed 5. All 10 runs exist, so the gates check every run and also state the fold 0 seed 5 verdict. The swad VERDICT is PASS only if (a) holds for all 10 runs and (b) for both fold-0 seeds (assumption).
- "Deviation" in C3 is taken as the probe's `dev` = ||W - W0|| / ||W0|| per stage; 1 - cosine gives the same verdicts (assumption).
- rcs read guard "per-class IoU splice / edge_dark / material": `bench_read_w1.py` at b5bf0ae prints no per-class IoU (E: GUARD_KEYS has inact_prec and in_cc_prec only). Not patched. See section 5.
- soft_band_jml "at OP-A and OP-W with per-source width": the tool's OP-W matches each arm's width to PF (the baseline), not to jml_hard. The pair JMLHARD=SOFTBAND is computed at OP-A, OP-F and OP-W as the tool defines them. Per-source width is in the per-source table of each arm, not in the contrast.
- The four other ema readouts (model, ema_999_bn, ema_9998, ema_999) and the one-run control w2a_spdctrl_f0_s5 are not arms of the read. To add an ema readout: one `--arm` and one `--pair` in the `ema)` line.
- soft_band_jml cannot be read until w2a_softband_f1_s6 is retrained and dumped (queue w2a3). Then: `TAG=softband ARMS="jmlhard softband" bash run_read_w2a.sh` (new folder `bench_reads/w2a_softband`; PF=JMLHARD is repeated there).
- The dump log of the retrain is assumed to be `/home/noob/work/bq/w2a3/dump/launch.log` (from `bq/w2a3/launch.sh`: Q=/home/noob/work/bq/w2a3).

## 5. Extra: `w2a_class_guard.py` (not asked; S)
Section 8 names a per-class IoU guard for rcs that the read tool does not print. The script tabulates IoU, precision and recall of classes 13 (material), 16 (splice), 20 (edge_dark), 11 (inactive) per arm from the argmax records in a finished read's cache, with the read tree's own `bench.score_ext.summarize`. It runs after the read and needs review like the rest. E: on the dry read its inactive rows equal read.json's inact_iou, inact_prec, inact_rec for all three arms on both cell sets (4 decimals). If the lead does not want it, it can be ignored; nothing else depends on it.

## 6. md5 and state (E, 05:00:06, final)
Code in `harness/w2a/read/`:
```
724e35ffe5fe854d5f91cbdeeb31e62d  w2agate.py
dba4931ba9c5084dcf7b819e08d7e065  gate_ema_hash.py
c611a5a02a3dcb379748c2f97fc3e1a8  gate_swad_prescreen.py
7cbde648653179389f90cbf41fdc8343  gate_spd_mech.py
5aac565df12c2d470e4d421788645196  run_read_w2a.sh        (the version to run; lead, 04:23. Earlier: 2195192f, b3862159)
643133df0f9b40f9cc0e3615eca294da  test_run_read_w2a.sh   (45 checks)
97f63cb2efe4fc8dd094ce208b945fac  preflight_now.sh
1859f91afacef94885aa055759f2b32b  w2a_class_guard.py
```
Outputs in `/home/noob/work/bench_reads/w2a_gates/`:
```
bbea890ada1003aba691d67d3d7be633  gate_ema_hash_r1/gate_ema_hash.txt
03381e2ba6d3743369d7a1ab2530fc44  gate_ema_hash_r1/gate_ema_hash.json
91ca465652793506e3d69a8068f8e37c  gate_swad_prescreen_r1/gate_swad_prescreen.txt
8673fdd11e0c0af75a05691e3ffa905b  gate_swad_prescreen_r1/gate_swad_prescreen.json
d165b825ddf54f320f5353bc9c60bd09  gate_swad_prescreen_r2/gate_swad_prescreen.txt
275d69e660b4a465e890b2f0e7e9fc28  gate_swad_prescreen_r2/gate_swad_prescreen.json
9d3e895e0cb69511416d4b1883b8c1d9  gate_spd_mech_r1/gate_spd_mech.txt
361b33c8da59c200c3e6a5ba3c7b359a  gate_spd_mech_r2/gate_spd_mech.txt
39592ca3fb1300e4bb5ee9fca99ee6d4  gate_spd_mech_r2/gate_spd_mech.json
7af3fe575ccf883a51f09ad0d5da73d7  dry3/run.log
9c0d97667dc2834fe9e2f242f5cf90d9  dry3/MD5.txt
```
VERDICT files (whole content): gate_ema_hash_r1 `gate_ema_hash PASS`; gate_spd_mech_r1 `gate_spd_mech FAIL`; gate_spd_mech_r2 `gate_spd_mech FAIL`; gate_swad_prescreen_r1 `gate_swad_prescreen OPEN`; gate_swad_prescreen_r2 `gate_swad_prescreen PASS`. The read script uses, per gate, the folder `<gate>_r<number>` with the highest number: ema r1 PASS, swad r2 PASS, spd r2 FAIL.
Inputs used: `bench_wt_b/scripts/bench_read_w1.py` fdb56b78, `scripts/bench_score.py` f096aff7, `bench_wt_w2/src/trainers/enc_probe.py` a431e5d3, `src/models/model_factory.py` b403024d, `benchmark/splits/score_exclude_v3.txt` 6d48dfbd, `bq/w2a2/dump/jobs.txt` 0bcef536.

Worktrees after the work (05:00), `git -C <tree> status --porcelain -uno | wc -l`: bench_wt_w2 (c57508e) **0**; bench_wt_b (b5bf0ae) **0**; el_bench (31c0c36) 0; bench_wt_final (89b9ea5) 0. No file newer than 03:33 exists in bench_wt_b, or in bench_wt_w2 outside `experiments/` (which the dump queue writes) (`find -newermt`, 05:00: 0 and 0).
Disk: my folders under `/home/noob/work/bench_reads/w2a_gates` hold 350 MB in total (three dry caches of 113 MB each are most of it). `/home/noob/work/bench_reads/w2a` does not exist. No GPU use: every command ran with `CUDA_VISIBLE_DEVICES=""`; torch reported `cuda available False`; the only GPU-related command was one read-only `nvidia-smi --query-compute-apps` at 04:01 (it showed PID 6206 only). No queue, tmux session, waiter or file under `bq/` was touched (read only: `jobs.txt`, `launch.log`, `launch.sh`). The one background process of mine was a wait loop that read `bq/w2a2/dump/launch.log` every 10 s until job 62 had ended; it has exited. No network, no ssh, no pip. Scratch files (test fixtures, one dry class-guard table, kept copies of earlier script versions) are only in the session scratchpad.

## 7. Open
- gate_swad_prescreen: closed at 04:59 (r2 PASS). Nothing open in the three gates.
- soft_band_jml: its dump job `dump_w2a_softband_f1_s6` ended rc=1 at 04:40:20, as expected for the stopped run. One run to retrain (queue w2a3); its read comes later with `TAG=softband ARMS="jmlhard softband"`.
- Decided by the lead (04:03, 04:23): PF = seeds 5, 6 with PFAA for the A/A; `PF4=1` only as a marked sensitivity read; spd is read under `GATE_ACK="spd"`, descriptive only; swad is not to be read under GATE_ACK; `run_read_w2a.sh` 5aac565d is not to be changed again.
- Optional after the dumps end: `python gate_ema_hash.py --out G/gate_ema_hash_r2` (22 s) repeats the hash and checks the checkpoint md5 against all 60 ema dump manifests (r1 could check the 10 that existed). Its VERDICT then becomes the one the read script uses for ema.
