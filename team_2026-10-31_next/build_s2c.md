# SKR2C build v2 (runner, 3 Nov 2026): training queue + data root + overnight guard, for coach's review and judge's check

Status: DRAFT. Nothing has trained and nothing is armed. `/home/noob/work/s2c` does not exist. gaint writes so far, none on the GPU:
- the data root `/home/noob/work/s2c_root`;
- its check dir `/home/noob/work/s2c_check`;
- the scratch dry dir `/home/noob/work/runner_s2c_dry`.

v2 adds the data root and the guard, on team-lead's 3 Nov request (§3, §4). It also fixes the trainer PID record (§2).

## 1. Files (`scripts/s2c/`; gaint copies md5-checked)
| file | md5 | role |
|---|---|---|
| `s2c_make_jobs.sh` | e7d20e79a22c0bd050edf3c9eb194058 | jobs + exp files (from s2q_make_jobs 5591792f; diff e4983deb) |
| `s2c_queue.sh` | 5179dac409ee4c5c2546532e4a84ee29 | training queue (from s2q_queue_v3 928742a0; diff 03d4f2b8) |
| `s2c_gpumem.sh` | bee07e599feb254830b61bcd1a9b9ab0 | 1 s GPU log (from s2q_gpumem 084f6a42; diff f85bd27e) |
| `s2c_guard.sh` | 992919448c098f61aa7b2e0095e600a6 | overnight guard (new) |
| `s2c_make_root.sh` | 133ad1848498e6b8bffee32d51482811 | data root (new; B6 idroot layout) |
| `s2c_databuild_check.py` | d0ff0f41bd4b3ab01b41a1ec948049ee | per-arm CPU data-build check (from b6_databuild_check 061a3964) |
| `s2c_rootcheck.sh` | 6561c9e173e59218875d40d1f17d5b90 | root verification runner (v2) |
| `s2c_cfg_dry.sh` | 4d10070438641a6e08f7ca56141c6a2e | the queue's cfgcheck rule on real / root configs |
| `s2c_guard_dry.sh` | 18a5dc84a8ed22602b9a61d7bacb4f71 | guard dry-run harness |

Local copies of every dry / check output: `results/s2c_dry/` (md5s in `results/s2c_dry_md5.txt`).

## 2. Queue (training only)
- **Jobs:** 10 lines, in strict order. For each K = 10..14: SKR01 sK first, then SUPPF sK.
  - Opts are the pf2_SUPPF s5 line (pf2_jobs 210d0d6f) with `seed=K`, `data.root=/home/noob/work/s2c_root` and the new run_name.
  - SKR01 adds `loss.skel_recall.weight=0.1`, as s2q d6efb9af.
  - Names: `s2c_SKR01_100pct_sK` (el_thin), `s2c_SUPPF_100pct_sK` (el_f3).
  - Dry jobs: **0839f34089bf76eec815e156410e66fa**. The token diff of each line vs pf2 SUPPF s5 = seed, run_name and data.root, plus skel 0.1 on SKR01.
- **exp files** (the queue-format config diff vs pf2_SUPPF_100pct_s5 config_used.yaml). Each equals (`cmp`) rootcheck's diff of the config that train.py will write:
  - exp_SUPPF **dc9c344a**: `<   root: /home/noob/work/s2c_root` / `>   root: data`;
  - exp_SKR01 **1343cca2**: those two lines plus s2q's skel lines.
- **Arms:** SKR01 runs on el_thin c9bbb02, SUPPF on el_f3 e544133. Deploy and REVISION are checked at arming; the deploy again at each start.
- **Gates (peak + 2,048):** SKR01 9,100 (peak 7,020); SUPPF 9,000 (peak 6,830). Starts go through the shared gpu_gate 00fabfdd (>= 120 s apart, HOLD).
- **MAXC 2** (file `s2c/MAXC`).
- **v2 changes in the queue:**
  1. **Trainer PID fix.**
     - E: s2q's `( cd $w && python ... & ; pp=$! )` recorded the bash subshell, not the trainer. skr2_SKR01_100pct_s5's pid file holds 2170515; the GPU python was 2170519 (s2q/gpumem.log). pf2's queue matched (1676897).
     - s2c now runs `cd` first, then starts python as a plain background command, so `pids/<name>.pid` = python's PID.
     - Proven in the dry run (§4): pid file = the subshell's only child, with cmdline `scripts/train.py ... run_name=<name>`.
  2. The guard must be alive at arming. Before every start the queue checks the guard and the gpumem logger; if either is gone, it sets HOLD.
  3. HOLD is re-checked after a gate pass, and a set HOLD there means no start.
- A stopped run is never restarted: the queue skips a run dir that exists, and HOLD stops all new starts. The end line is `S2C ALL TRAINED (n rc 0 of 10)`. No scoring and no opening trigger.

## 3. Data root (team-lead: data-root trick, test.txt = val), verified as for B6 §2-4
- **Root** `/home/noob/work/s2c_root`. `SPLITS.md5` **24568cdb**: train 842f27c4, val 9dcccf00, test 9dcccf00.
  - `splits/train.txt` = el_f3 data/splits/train.txt (478; byte-equal to el_thin's).
  - `splits/val.txt` = val (54).
  - `splits/test.txt` = a copy of val.
  - `labeled` → `/home/noob/work/el-fault-detection/data/labeled`: el_f3's data/labeled target. el_thin's labeled/images and labeled/masks_escdd point there too.
  - Asserts:
    - 0 stems of b6_forbidden 9bb4d919 (test 50 ∪ ext117);
    - 0 real test stems;
    - train and val disjoint, no duplicates.
- **Data build** (s2c_databuild_check, both arms, the s5 opts): PASS.
  - **Control** (data.root=data): the Labelled / CE / zero lines equal the s5 run's train.log. `yaml.safe_dump` of the config is text-identical to its config_used.yaml.
  - **Root:** `Labelled: 478 (/home/noob/work/s2c_root/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54`.
    - CE none / zero none;
    - class counts 262f92a5 = control;
    - test stems = val stems (54, same order);
    - config diff = `data.root` only.
- **Identity** (identity_cpu.py 962379a6 = judge B6-4's harness = el_thin scripts/thin/identity_cpu.py): 5 CPU fp32 steps per arm, A data.root=data vs B the root. **IDENTICAL** on every field except the wall seconds per step.
  - Fields compared: init state, class counts, fixed batch, and at each step loss repr, lr, state sha, logits sha.
  - SUPPF: init 56a9ee7f; step-5 loss 4.154092311859131; state 4a216d9d. These equal B6's idchk5.
  - SKR01: step-5 loss 4.251284599304199; state 2e44cb4d.
  - Run 1 ended rc 1 only because it also compared the wall time (`sec` 8.25 vs 8.18). Run 2 excludes it. Both logs are in results/s2c_dry.
- **Effect (S):** the trainer's end-of-run TEST block reads val, never the real test, so training reads no test or E1 cell. Every later score of these runs is done by the opening scorer on the real test / E1 lists.

## 4. Overnight guard (team-lead (a)-(d); coach specifies)
- **Sampling:** one process in tmux window `guard`, own PID in `s2c/guard.pid`. It reads `nvidia-smi` free memory every 1 s, independently of the gpumem logger.
- **Trigger:** free < 2,048 MiB on 3 consecutive samples. A failed or non-numeric read is logged, not counted, and resets the count.
- **On a trigger:**
  1. `touch s2c/HOLD` first.
  2. Target = our newest live SKR2C run, by recorded PID only. Each `s2c/pids/<name>.pid` must pass all of:
     - the name is a jobs-file name;
     - the PID is alive;
     - the owner is noob;
     - it is not 6206;
     - its /proc cmdline holds `scripts/train.py` and the token `run_name=<name>`.
     Other pid files are refused, with the reason logged. Newest = the smallest `ps etimes`.
  3. Log the PID, name, full cmdline, the last 30 free samples and the GPU process list. Then `kill -TERM <PID>`; after 30 s, `kill -KILL <PID>` only if it is alive with the same cmdline.
  4. Log 20 post-stop samples as a cool-down, then re-arm. At most 2 stops (MAXSTOPS = MAXC); later triggers are logged only.
- **Never:** a pattern kill, or any PID that is not in s2c/pids. finllm 6206 is refused explicitly.
- **End:** 60 s after `S2C ALL TRAINED`, on GUARD_STOP, or at 24 h.
- **Dry run** (gaint 02:37:56-02:39:52, scratch Q, `DRY=1`: fake free values from a file, no signal):
  - **Setup:**
    - two dummy trainers (a fake `scripts/train.py` that only sleeps), started with the queue's exact launch lines and real job names / opts: SKR01 s10, then SUPPF s10 5 s later;
    - decoys: s11 → a plain `sleep` started last (newest, wrong cmdline), 6206, PID 1 (root), a dead PID, `stray.pid`.
  - **Pass 1** (78 samples; `results/s2c_dry/guard_pass1.log` 8626f20a):
    - The count reset on 2,100 and on a failed read (`ERR`). 2,047 counted as low.
    - Trigger 1 → TARGET `s2c_SUPPF_100pct_s10` (newest valid, 14 s).
    - Trigger 2 → `s2c_SKR01_100pct_s10`.
    - Trigger 3 → `MAXSTOPS 2 reached: no stop`.
    - Decoys refused every time: wrong cmdline, finllm PID, owner root, not alive, not a jobs name.
    - 20 logged post-stop samples after each trigger. HOLD file set.
  - **After pass 1:** both dummies were alive (no signal sent).
  - **Harness stop:** the harness then stopped its own dummies by recorded PID, with the cmdline printed first. Their subshells logged `trained <name> rc=143`, which is the stop path the real guard takes.
  - **Pass 2** (`guard_pass2.log` 7c7e1dd2): trigger → `no valid live SKR2C run to stop`.
  - **Cleanup:** all 5 dummy / decoy PIDs and the guard PIDs are gone; tmux s2cdry ended.
  - Harness log: `results/s2c_dry/harness.log` bd66d601.

## 5. Launch (after coach APPROVED + judge sign-off)
1. Create `/home/noob/work/s2c` (refuse if it exists). Copy the scripts to `s2c/scripts/` and check md5s on both ends. Re-verify the root: `SPLITS.md5 -c`, test = val, labeled link.
2. Run make_jobs. The jobs md5 must = 0839f340 and the exp files dc9c344a / 1343cca2. Run `echo 2 > s2c/MAXC`.
3. Create tmux `s2c`: window `gm` (`nice -n 19 bash s2c_gpumem.sh`), then window `guard` (`bash s2c_guard.sh`). Check both PIDs are alive.
4. Start window `q`: `JOBS_MD5=0839f340... GATE_SKR01=9100 GATE_SUPPF=9000 bash s2c_queue.sh`. Record queue.pid.
5. Check, for the first two runs:
   - start / pid / `config OK` lines;
   - pid file = the GPU python PID (nvidia-smi);
   - `grep -c 'step 50/20000'` >= 1, counted only;
   - free memory in gpumem.log;
   - guard.log quiet.
   Then send team-lead the PIDs, tmux, ETA. No local waiter.

## 6. Cost / ETA (S)
- ~2h28 per run at 2 alive, so 5 waves take ~12.3-12.5 h from the first start. ~25 GPU-h; ~5 GB disk.

## 7. Questions for coach
1. Names `s2c_*`? Gates 9,100 / 9,000?
2. Guard parameters:
   - trigger 2,048 x 3;
   - TERM, then KILL after 30 s;
   - 20-sample cool-down;
   - MAXSTOPS 2 (a second stop only if free stays low after the cool-down);
   - HOLD set on the queue only (`s2c/HOLD`), not the global `gpu_gate/HOLD`.
3. gpumem or guard gone before a start: HOLD (proposed)?
4. No smoke (same commits / opts apart from seed and data.root; root identity at 5 steps for both arms)?
