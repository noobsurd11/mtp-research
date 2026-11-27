# Wave 1 read: commands (builder x3, 13 Nov 2026)

CPU tools on prediction dumps. Code: worktree `/home/noob/work/bench_wt_x3`, branch `bench_x3` (commit in BUILD_LOG.md, section "Wave 2a, builder x3"); after the integrator merges, run the same commands from the merged worktree. Every command is one line, runs unattended, CPU only, and refuses to overwrite its outputs. Run each in its own tmux session (`tmux has-session -t "=bench_w1read" || tmux new-session -d -s bench_w1read '<command>'`). Nothing here reads a sealed set (the tools refuse test50 and e1_106) or a training stdout / metrics JSON.

## Common settings
```
cd /home/noob/work/bench_wt_x3
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
G="--arm PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[56] --labels v11 --workers 8 --cache /home/noob/work/bench_reads/w1g"
```
`--arm NAME=<method dir>:<run_id regex>`: every run dir under the method dir whose name matches; each must hold one set dir with a manifest (`bench_infer.py` output). The fold comes from the manifest; each (arm, seed) must have folds 0 to 4 (else the tool stops; `--allow-partial` reads what exists and says PARTIAL). `--cache` is shared by the four tools, so argmax records and bias sweeps are computed once.

## W1-G (gaint; 10 PF v1.1 runs, seeds 5 and 6). Start when all 10 dumps exist:
`ls -d /home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11/w1g_pf_v11_f*_s*/cv5v2_f*/manifest.json | wc -l` = 10.

1. Wave 1 read (OP-A / OP-F / OP-W, guards, subsets, frontier; A/A needs seeds 7, 8, so on W1-G it prints "no margin M"):
   `nice -n 19 $P scripts/bench_read_w1.py $G --baseline PF --out /home/noob/work/bench_reads/w1g/read`
2. src_calib (row "uses source metadata"):
   `nice -n 19 $P scripts/bench_src_calib.py $G --out /home/noob/work/bench_reads/w1g/src_calib`
3. dti_hysteresis:
   `nice -n 19 $P scripts/bench_dti.py $G --out /home/noob/work/bench_reads/w1g/dti`
4. D0 placement diagnostic:
   `nice -n 19 $P scripts/bench_d0.py $G --out /home/noob/work/bench_reads/w1g/d0`

Outputs: `<out>/{read,src_calib,dti,d0}.{json,txt}`; the .txt is the table to read. Time (S, from the dry run scaled to 532 x 2 cells): read about 10 to 20 min the first time (argmax records, 49-bias sweep, OP-F / OP-W records, 2,000 bootstrap draws per contrast); src_calib, dti and D0 about 5 to 15 min each after it.

## W1-C (cv02 sets, after the relay to gaint). Replace `<RELAY>` with the relayed dump root of each set:
```
C="--arm PF=<RELAY_C1>/elbench1/house_r34_unetpp_pf_v11:<C1 run regex> --arm HOUSE=<RELAY_C2>/elbench1/house_r34_unetpp_v11:<C2 run regex> --arm PFV1=<RELAY_C3>/elbench1/house_r34_unetpp_pf:<C3 run regex> --labels v11 --workers 8 --cache /home/noob/work/bench_reads/w1c"
nice -n 19 $P scripts/bench_read_w1.py $C --baseline PF --aa PF:5,6:7,8 --out /home/noob/work/bench_reads/w1c/read
```
- Contrasts: HOUSE - PF and PFV1 - PF (default: baseline against every other arm), all held-out cells scored on v1.1 strict + ignore (`--labels v11`), so the label-fix ablation compares models, not ground truths. A second read with `--labels v1` (and a new `--out`, same cache root is fine) gives the old-label view.
- The A/A null (PF seeds {5,6} against {7,8}) gives M(metric) = max(0.01, 2 x SE of the A/A difference) per metric at OP-A; printed with every contrast. A PASS* flag = delta >= M and CI low > 0 (a screen flag, never a result).
- src_calib, dti and D0 on W1-C: the same three commands with `$C` and the w1c output dirs.
- Machine rule: one read never mixes gaint and cv02 dumps (the tools refuse mixed precision or device types; the manifests carry the GPU name).

## Single-dump scoring (unchanged scorer, two new opt-in flags)
- `scripts/bench_score.py records ... --labels set|v11|v1|manifest` (default `set` = as before: cv5v2 sets score v1.1 masks with ignore px not scored). `manifest` takes the label set from the run's training root in the dump manifest (`cv5v2_v11_f*` -> v11; `cv5v2_v1_f*`, `b6_root_*` -> v1).
- `scripts/bench_score.py summary ... --cells-tsv /home/noob/work/bench_data/meta/cells.tsv` adds the subsets `meta:src:*`, `meta:type:*` (mono, multi, no_spacing, dogbone), `meta:crackfree`, `meta:crack`, `meta:-flagged`, `meta:flag:*`.

## What each table holds (WAVE2_REVIEW section 5)
- read.txt: per arm and operating point, mean (sd) over seeds of crack IoU, relF1@2, inactive IoU, mIoU-R13, relP@2, relR@2, relF1@1, width ratio, mean width (px per skeleton px), crack-free false-alarm share (>= 50 px) and px, component recall (50% and any-hit) and precision, inactive P / R / region precision; per source and cells.tsv subsets at OP-A and OP-W; the cross-fitted biases per fold; the frontier; the A/A block with M; contrasts with 95% CIs (two-stage: 330 groups of cv5v2_groups.tsv, then one seed per fold and arm).
- src_calib.txt: argmax / glob_bias / src_bias / src_morph rows, all cells and per source; width table (GT mean width, predicted at argmax and src_bias); b_src per fold and spread (> 1.0 = unstable); paired contrasts src_bias - glob_bias (primary), src_morph - argmax, glob_bias - argmax, and src_bias - glob_bias per source with >= 40 cells; flags (implicit conditioning, src_film gate, provisional per-source pass with M_src 0.03).
- dti.txt: argmax / OP-F / unguarded bias / DTI rows with relF1@2, relF1@1, strict IoU, width; the width guard (DTI <= 1.15 x OP-F); paired contrasts DTI - OP-F (primary), DTI - bias, DTI - argmax; chosen pairs per fold; frontier (best relR@2 at relP@2 >= 0.90 and >= the argmax relP@2, DTI grid and bias grid).
- d0.txt: prediction and GT shares within 1 px (and 0.5 px) of the ridge, pooled and per seed, per source; strict IoU against the labels (snapped labels only with `--snapped DIR`); mean p_crack by signed distance from the ridge; the fixed X5 reading.
