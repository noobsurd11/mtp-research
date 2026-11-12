# SKR2C build v3 (runner, 3 Nov 2026): queue + data root + auto-stop watcher, against protocol_SKR2C v1 LOCKED 91b76abd

Status: nothing has trained and nothing is armed. `/home/noob/work/s2c` does not exist.

gaint writes so far, none on the GPU:
- the data root `/home/noob/work/s2c_root` (the protocol's path, per coach);
- its check dir `/home/noob/work/s2c_check`;
- the scratch test dir `/home/noob/work/runner_s2c_dry`.

v3 answers judge's review b0d866a4 (G1-G8) and coach's v1 §2b items.

## 1. Files (`scripts/s2c/`; gaint copies md5-checked)
| file | md5 | role |
|---|---|---|
| `s2c_lib.sh` | 4edcae9e7c487f1b0c3e0ee67568661d | shared functions, sourced by the queue and the watcher (§4) |
| `s2c_guard.sh` | 334742d69104799b0f5535bb838e9870 | auto-stop watcher v2 |
| `s2c_queue.sh` | de31c533118ace064fa94bf24dc0bd5d | queue v3 (from s2q_queue_v3 928742a0; diff `diff_queue_vs_s2q_v3_928742a0.diff` d913d251) |
| `s2c_gpumem.sh` | 06791cddd4dd8d9b3eaa4a4031bcd744 | 1 s GPU log, every nvidia-smi under `timeout 5` (diff 6b51f983) |
| `s2c_make_jobs.sh` | e7d20e79a22c0bd050edf3c9eb194058 | jobs + exp files |
| `s2c_make_root.sh` / `s2c_rootcheck.sh` / `s2c_databuild_check.py` | 133ad184 / 6561c9e1 / d0ff0f41 | root build and verification |
| `s2c_cfg_dry.sh` | 4d10070438641a6e08f7ca56141c6a2e | the queue's cfgcheck rule on real / root configs |
| `s2c_guard_dry.sh` / `s2c_queue_unit.sh` | f0782bbe / 40dc50fa | watcher passes 1-5 / queue unit tests |

**Guard md5 note.** The first v3 run (`results/s2c_dry/v2/`) used guard d8a8eb75. 334742d6 differs from it by one token: `TRIG=""` on a failed read. This is display only; that run's pass 1 trigger line had listed 5 samples across an ERR reset.

**The whole suite was then re-run on the exact final code**, 02:57:40-03:04:05, in fresh dirs `g2_final` / `qu_final`:
- guard 334742d6, lib 4edcae9e;
- harness 8ee6beaa / unit 5c12b297, whose only change is TAG-suffixed scratch dirs.

All results are as in §7, and pass 1's trigger line now lists exactly its 3 samples.

**Logs:**
- final-code run: `results/s2c_dry/final/` (md5s in `results/s2c_dry_final_md5.txt`). harness ca64a8af; autostop_pass1 / 1b / 2 / 3 / 4 / 5 = 003c1aaf / d365c3d9 / 1981824a / 76c89b83 / e9606392 / ac2f12cd; queue_unit ea93ae6d.
- earlier runs: `results/s2c_dry/v2/` (first v3 run) and `results/s2c_dry/` (v1 dry).

## 2. Data root and identity (protocol §2a)
- **Root** `/home/noob/work/s2c_root`. `SPLITS.md5` **24568cdb**: train 842f27c4, val 9dcccf00, test 9dcccf00.
  - test.txt = a byte copy of val.txt.
  - `labeled` → `/home/noob/work/el-fault-detection/data/labeled`, idroot's target.
  - 0 forbidden stems (9bb4d919); 0 real-test stems.
  - The queue re-checks the md5s, test = val and the link target at arming.
- **rootcheck run 2:** `s2c_rootcheck.sh` 6561c9e1, gaint 02:33:29-02:37:24, rc 0. Log: `results/s2c_dry/rootcheck_run2.log` 229b731d.
- **Identity:** `identity_cpu.py` 962379a6, 5 CPU fp32 steps, the s5 opts, `--threads 8`, nice 19.
  - A = the tree's OWN `data.root=data`: el_f3/data for SUPPF; el_thin/data for SKR01, whose labeled dir also holds the 582 `masks_escdd_s` B3 masks plus their 3 meta files.
  - B = `data.root=/home/noob/work/s2c_root`.
  - **Compared fields:** the whole record except `opts` (asserted: B's = A's + `data.root=<root>`) and the per-step wall `sec`:
    - `code`, `loss_class`, `n_params`;
    - `init_state`, `class_counts_sha`;
    - `fixed_batch` {stems, image sha, mask sha, keys};
    - each step's {step, out {loss, loss_sup, loss_con, lambda} as exact repr, lr (all groups), state (param + buffer sha), logits (fixed-batch eval sha), logits_shape};
    - for SKR01 also `thin` {loss_srec}.

    This list ⊇ §2a's (init state, class counts, fixed batch, loss repr, lr, param sha, logits sha).
  - **SUPPF: IDENTICAL.** init 56a9ee7f, counts 262f92a5, fixed batch 0ebd1811 / f5513068, step-5 loss 4.154092311859131, state 4a216d9d, logits 429adeef. These equal B6 idchk5.
  - **SKR01: IDENTICAL.** init 56a9ee7f, counts 262f92a5, same fixed batch, step-5 loss 4.251284599304199, state 2e44cb4d, logits 73c627f1, including the per-step `loss_srec`. So SKR01 never reads the masks_escdd_s files the root lacks.
  - Records on gaint `s2c_check/idchk/`: SUPPF A 26c5bc44 / B cb7c4e41; SKR01 A e04efebe / B 4b91b584.
  - Run 1 differed only in `sec` (8.25 vs 8.18 s).
- **Data-build lines** (`s2c_databuild_check.py` d0ff0f41), both arms PASS:
  - control = the s5 run's train.log lines, and `yaml.safe_dump` = its config_used.yaml, text-identical;
  - root: `Labelled: 478 (/home/noob/work/s2c_root/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54`;
  - `CE class weights: none (plain CE)` and `Zero-pixel classes ...: none`, both = control;
  - counts = control; test stems = val stems;
  - config diff = `data.root` only.

## 3. Jobs and cfgcheck
- **Jobs** (dry make, same script and inputs at launch): **0839f34089bf76eec815e156410e66fa**. 10 lines, in order SKR01 sK then SUPPF sK, for K = 10..14. Names are `s2c_SKR01_100pct_sK` / `s2c_SUPPF_100pct_sK` (coach Q1).
  - Token diff vs pf2_SUPPF s5 = `seed`, `run_name` and `data.root=/home/noob/work/s2c_root`, plus `loss.skel_recall.weight=0.1` on SKR01.
- **exp files** (the queue-format config diff vs pf2_SUPPF_100pct_s5 config_used.yaml), each `cmp`-equal to the diff of the config train.py writes under the root:
  - exp_SUPPF **dc9c344a**: `<   root: /home/noob/work/s2c_root` / `>   root: data`;
  - exp_SKR01 **1343cca2**: those lines plus the skel lines.

  cfgcheck ignores run_name, seed and experiments_dir and asserts `seed: K`, so data.root is the only extra key.
- **cfg_dry** on the root-rendered configs:
  - each arm's own exp: OK;
  - crossed arms: FAIL;
  - the old no-root s6 configs: FAIL.

## 4. Shared functions (`s2c_lib.sh` 4edcae9e)
- `SMI` = `timeout 5 nvidia-smi` (G4). The queue's start line, `apps` and the watcher all use it; so does gpumem, inline.
- `verify NAME PID`: passes only if all of these hold:
  - the PID is not 6206;
  - `/proc/PID` exists;
  - the owner is noob;
  - `pids/NAME.cmdline` exists;
  - the live cmdline **equals** the recorded one (G1);
  - it holds `scripts/train.py` and the token `run_name=NAME`.

  Otherwise it prints the reason.
- `stop_verified NAME PID`: verify, then SIGTERM, then wait up to 30 s (calling the watcher's `tick` each second, which samples and logs free memory). If the PID is still alive, it re-verifies (owner + exact cmdline, G2), then sends SIGKILL and waits up to 10 s. Return codes: 0 stopped, 2 refused before any signal, 3 re-check failed (no SIGKILL), 4 alive after SIGKILL. With `DRY=1` it sends no signal.
- `outside`: compute apps that are not 6206, not one of our recorded trainer PIDs, and hold > 1,024 MiB (G5).
- `prestart`, before every start:
  - HOLD present → wait;
  - gpumem logger or watcher gone → `touch HOLD`;
  - outside process → wait (no HOLD file; re-checked every 60 s; one line per episode).
- `startcheck STDOUT WANT WAIT`: the first `Labelled:` line of the stdout, by `grep -m1` only, must equal WANT (G6).
- `launch_run NAME WT OPTS`: the queue's launch path.
  - `cd` first, then python as a plain background command, so `pids/NAME.pid` = `$!` = python.
  - After the exec it waits up to 20 s for a `scripts/train.py ... run_name=NAME` cmdline, then writes `pids/NAME.cmdline`.
  - The subshell writes `pids/NAME.rc` and the `trained` / `done` lines (grep counts of `step 20000/20000` and `Traceback`).

## 5. Queue v3 (`s2c_queue.sh` de31c533)
- **Arming:**
  - jobs md5; the data root re-check;
  - arms, deploys (c9bbb02 / e544133) and REVISION;
  - exp files;
  - gpumem logger and watcher alive.
- **Each start:**
  1. `prestart`;
  2. MAXC 2;
  3. `gate_try` (gate 9,100 / 9,000; >= 120 s apart);
  4. HOLD re-check after the gate pass;
  5. deploy check;
  6. `launch_run`;
  7. log the `ps -o pid,user,lstart,args` line and the cmdline md5;
  8. the live check before the next start: `cfgcheck` (config = exp) and `startcheck`, which must give `Labelled: 478 (/home/noob/work/s2c_root/splits/train.txt) ... val: 54  test: 54`.

  On a failure or a CONFIG FAIL: `touch HOLD`, then `stop_verified` on that run (G6), then log.
- **Never:** a restart. The queue skips an existing run dir, and HOLD stops new starts. The rerun rule (protocol) applies tomorrow.
- **No** scoring and no opening. The end line is `S2C ALL TRAINED (n rc 0 of 10)`.

## 6. Auto-stop watcher v2 (`s2c_guard.sh` 334742d6)
- **Process:** its own tmux window, own PID (`s2c/guard.pid`), own 1 s sampling (SMI). It does not depend on the queue or the gpumem logger.
- **Trigger:** free < 2,048 MiB on 3 consecutive samples.
  - A failed read is logged, not counted, and resets the count.
  - 10 consecutive failed reads → HOLD (G4).
- **On a trigger:**
  1. HOLD first.
  2. Log the 3 trigger samples, the last 30 samples and compute-apps.
  3. Candidates = `pids/<job name>.pid` without `.rc` and alive. Each is `verify`-ed; a failing one is REFUSED, logged and never signalled.
  4. Target = the newest verified (smallest etimes). Log the target's recorded cmdline, then call `stop_verified`. Its 30 wait samples are logged.
  5. Then 30 logged post-stop samples (G3), so >= 60 s of trace around the event: 30 before + wait + 30 after.
- **Stop limits:**
  - A 2nd stop needs a fresh trigger (3 new samples after the cool-down) and >= 30 s since the first signal (GAP).
  - Cap: MAXSTOPS 2, switchable by env (`MAXSTOPS=1` gives one stop only); later triggers are logged only.
- **Log:** `s2c/autostop.log`. It carries:
  - the PID and `ps -o pid,user,lstart,args` (before the action and after it);
  - the recorded cmdline;
  - the 3 trigger samples and the 60 s of trace;
  - compute-apps before and after;
  - each action with its rc and result.
- **FAKE** (free values from a file) is split from **DRY** (no signal) (G7).

## 7. Tests (gaint 02:48:00-02:55:11, re-run on the final code 02:57:40-03:04:05 with the same results; scratch dirs only; dummy processes only; no GPU allocation)
All dummies are started by the lib's own `launch_run`. Their `scripts/train.py` (a fake worktree) only sleeps. `DUMMY_MODE` is set in the environment, not on the cmdline: normal, ignterm (SIG_IGN on SIGTERM), or execswap (on SIGTERM, exec's into `sleep 600`: same PID, other cmdline).

Decoys, never signalled in any pass:
- `s2c_SUPPF_100pct_s11`, a live trainer-shaped dummy whose recorded cmdline was altered (the PID-reuse case);
- `s2c_SKR01_100pct_s11`, a plain sleep started last, with a fake record;
- 6206; PID 1 (root); a dead PID;
- a finished run (`.rc`);
- `stray.pid`.

| judge item | evidence (`results/s2c_dry/final/`; the first run is in `results/s2c_dry/v2/`) |
|---|---|
| (a) pid = python, not the subshell | harness.log: each launch shows pid file = LPID, a parent that is the bash subshell, the `ps -o pid,user,lstart,args` line, and recorded cmdline = live: yes |
| (b) 2 lows don't fire, 3 do | pass 1 / 2: `1/3, 2/3, >= 2048: count reset`, then `3/3 → TRIGGER`; ERR resets (pass 1, trigfix) |
| (c) verified before SIGTERM; re-verified before SIGKILL; TERM-ignoring dummy | pass 2: B (ignterm) gets SIGTERM, 30 wait samples, `re-check passed (owner noob, cmdline = recorded)`, SIGKILL, gone; its subshell logs `rc=137` |
| (c') re-check failure → no SIGKILL | pass 3: C (execswap) gets SIGTERM, its cmdline becomes `sleep 600`, `re-check FAILED ... no SIGKILL`, rc 3; C alive afterwards |
| (d) cmdline mismatch → no signal | every pass: decoys `REFUSED (cmdline differs from the one recorded at launch)`; pass 4: C refused, `no verified live S2C run to stop; no signal`; harness: decoys alive after the live passes |
| (e) HOLD written | every trigger: `HOLD set`; harness `HOLD file: present`; unit: HOLD after the live-check failure |
| (f) 2nd stop only on a fresh trigger >= 30 s later, newest remaining, no 3rd | pass 2: stop 1 03:00:34, stop 2 03:01:38 (64 s; first run 02:50:52 / 02:51:55, 63 s) to A, the newest remaining; trigger 3 `cap: 2 of 2 ... no signal`. Pass 1b: a trigger 9 s after stop 1 gives `only 9 s since the first stop (< 30): no signal` (first run: 8 s); a later fresh trigger reaches A |
| (g) HOLD / wait on outside > 1 GB, logger gone, watcher gone | queue_unit.log: outside() flags 1500 / 1025 MiB, not 900 / 1024 / 6206 / ours; prestart: all ok rc 0; outside gives a wait, no HOLD; gpumem dead gives HOLD; watcher dead gives HOLD; HOLD present gives `HOLD` |
| (h) autostop.log fields | pass 2: PID + ps line, recorded cmdline, 3 trigger samples, 30 before + 30 wait + 30 post samples, compute-apps before and after, each action's rc / result |
| G6 live check | queue_unit.log: startcheck OK on the root line; MISMATCH on the real-root `test: 50` line and on no line. A live dummy printing `test: 50` gets MISMATCH, then HOLD, `stop_verified`, SIGTERM, exit, `trained ... rc=143` |
| G4 failed reads | pass 5: 10 consecutive ERR gives `HOLD set` |
| cleanup | harness / unit: every dummy, decoy and fake-pid sleep `gone`; tmux s2cdry2 ended |

## 8. Launch (after coach APPROVED + judge sign-off)
1. Create `/home/noob/work/s2c` (refuse if it exists). Copy to `s2c/scripts/`: lib, guard, queue, gpumem, make_jobs. Check md5s on both ends.
2. Run make_jobs. Assert jobs 0839f340 and exp dc9c344a / 1343cca2. Run `echo 2 > s2c/MAXC`.
3. In tmux `s2c`, start the windows in order, each with a recorded PID:
   - `gm`: `nice -n 19 bash s2c/scripts/s2c_gpumem.sh`;
   - `guard`: `bash s2c/scripts/s2c_guard.sh`;
   - `q`: `JOBS_MD5=0839f34089bf76eec815e156410e66fa GATE_SKR01=9100 GATE_SUPPF=9000 bash s2c/scripts/s2c_queue.sh`.
4. For the first two runs, check:
   - armed / start / pid lines (python, its parent the subshell);
   - `config OK` and `startup line OK`;
   - pid = the GPU python PID (nvidia-smi);
   - `grep -c 'step 50/20000'` >= 1, counted only;
   - gpumem free; autostop.log quiet.

   Then send team-lead the PIDs, tmux and the ETA (~12.3-12.5 h). rwatch4 stays armed. No local waiter.
