# Inference cost of the E1 candidates (gap G-N7)

infer_cost (builder), 22 Nov 2026; GPU section 3.4 added by the lead, 22 Nov 18:18 (run of 17:50 to 18:04 IST). E = measured (file or command cited); S = judgement.
Build dir `thesis/build/infer_cost/` (short: `B/`): scripts, raw outputs, `MD5.txt`.

## 1. Set-up
- E Rows (`FINAL_OPENING_READ.md`; `FINAL_RULE_ADDENDUM_1.md` item 5): C1 = PF, readout `model`, 1 view. C1-D4 = PF, D4. C2 = HRNet-W18 U-Net++ + SWAD, readout `swad`, D4 (8 views). C3 = 5 C2 seeds, D4 (40 forwards). E-PF = 5 PF seeds, 1 view each (5 forwards), the equal-count comparator of `verdict.txt` S2.
- E Code: clean worktree `/home/noob/work/bench_wt_t3b` (cba7fbd), imported read only: `src/models/model_factory.build_model`, `bench/tta.predict_tta`; `inference_model_cfg` copied 1:1 from `scripts/bench_infer.py`. Nothing written there (`git status` unchanged, `PYTHONDONTWRITEBYTECODE=1`).
- E Weights: the 10 fin2 checkpoints `/mnt/nas/noob_el_archive/bench_relay/fin2/fin_{pf,hrnet_swad}_v11_pool_s{5..9}/.../slim.pth`. Each loads strictly (0 missing, 0 unexpected keys) at step 20000 into the model built from its own config, and each file md5 equals its line in the NAS `RUN.md5` (`B/raw/verify.json`).
- E Inputs: random float32 tensors (B, 1, 512, 512), values (U(0,1) - 0.5) / 0.25 (the eval normalisation). No image, label or prediction of any set was read.
- E Software: Python 3.12.3, torch 2.14.1+cu130 (MKL 2024.2, oneDNN 3.12), smp 0.5.0, timm 1.0.30. fp32, no autocast.
- E Hardware: gaint CPU only, AMD Ryzen Threadripper 7960X, 24 cores / 48 threads, 156 GiB RAM. No GPU touched (`CUDA_VISIBLE_DEVICES=` empty). `nice -n 10`; `torch.set_num_threads` 1, 8, 16 (OMP / MKL env set to match), interop threads 1; threads not pinned to cores.
- E Shared host: other processes ran during the timings (details under the table in 3.1); load average before and after every config is in `B/raw/cpu/driver.log` and `B/raw/summary_timing.tsv`. `ps -p 5104` was logged before and after every config: 44 checks, all show root's `finllm_chat.py` running (`B/raw/cpu/driver.log`, `B/raw/ps5104.log`).
- E Latency per cell = wall time (`time.perf_counter`) of the whole predict for one batch (all members, all views, the D4 rotate / flip and its inverse, softmax, view and member average) divided by the batch size. It excludes image read, resize, normalise, argmax / dump maps and disk writes (section 4 has those). One process per config; warm-up batches are not timed.
- E **D4 views are not batched** in the deployed path: `bench/tta.py predict_tta` (every D4 dump) runs the 8 views one after another, each on the whole batch (E, `bench/tta.py` l61 to l81). One extra run (C2, batch 1) puts the 8 views into one forward of 8 images, for comparison.
- E Ensembles here run their members one after another in one process. The opening did it differently (E, `harness/final/opening/opening_make_jobs.py` l3 to l6): one cv02 dump job per member, with logp, and the mean softmax on gaint (`bench_ens_dump.py`).
- E Peak memory on CPU = peak resident set size of the process (`VmHWM`), weights, activations and the Python / torch runtime (about 0.8 GiB after model load).

## 2. Parameters and FLOPs (E, `B/raw/verify.json`, `B/raw/flops.json`)
- E Parameters: PF 26,075,672; HRNet-W18 U-Net++ 20,795,692 (as the card, `hrnet_w18_unetpp_swad_const_pf_v11.yaml`).
- E `torch.utils.flop_counter.FlopCounterMode` at 1 x 1 x 512 x 512 (fvcore, thop, ptflops are not installed): PF 147.98 GFLOPs, HRNet 218.06 GFLOPs per view. It counts only `aten.convolution` here, at 2 FLOPs per multiply-add (74.0 / 109.0 GMACs). Both equal the known figures: PF 148.0 (`PROTOCOL_v0.2.md` l161), HRNet 218 (`ROWS2_READ.md` l32). Note: `bench_rows1_io/probe/probe.py` prints the same count divided by 2e9 and labels it GMACs; the tables' "GFLOPs" are the count divided by 1e9.
- E One D4 cell through `predict_tta` counts exactly 8.0 x one view (both models).
- E Per cell: C1 148, E-PF 740, C1-D4 1,184, C2 1,744, C3 8,722 GFLOPs.
- S: "C3 costs 8 x E-PF" (`verdict.txt` l44) is true in forwards (40 v 5). In FLOPs it is 11.8 x (8,722 / 740), because an HRNet view costs 1.47 x a PF view. C2 against C1 is 8 x in forwards and 11.8 x in FLOPs.

## 3. Latency and memory
### 3.1 gaint CPU: AMD Ryzen Threadripper 7960X (24 cores), fp32, torch threads 1 / 8 / 16 (E, `B/raw/cpu/*.json`, `B/raw/summary_timing.tsv`)

| Row | Parameters (M) | GFLOPs per view | Forwards per cell | s per cell, batch 1, 1 thr: median (p90) [n] | s per cell, batch 1, 8 thr: median (p90) [n] | s per cell, batch 1, 16 thr: median (p90) [n] | s per cell, batch 8, 1 thr: median (p90) [n] | s per cell, batch 8, 8 thr: median (p90) [n] | s per cell, batch 8, 16 thr: median (p90) [n] | Peak memory (MiB) RSS b1 / b8, 16 thr |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 26.1 | 148.0 | 1 | 1.36 (1.38) [50] | 0.309 (0.322) [200] | 0.216 (0.233) [200] | 1.98 (1.99) [24] | 0.431 (0.451) [200] | 0.330 (0.358) [200] | 1285 / 3680 |
| C1-D4 | 26.1 | 148.0 | 8 | 10.9* (11.0*) | 2.47* (2.58*) | 2.23 (2.37) [30] | 15.8* (15.9*) | 3.45* (3.61*) | 2.81 (2.90) [24] | 1356 / 4273 |
| C2 | 20.8 | 218.1 | 8 | 16.3* (16.6*) | 4.38* (4.56*) | 3.88 (4.38) [30] | 25.7* (26.4*) | 5.76* (6.01*) | 4.56 (4.57) [24] | 1376 / 4382 |
| C3 | 104.0 (5 x 20.8) | 218.1 | 40 | 81.3* (82.9*) | 21.9* (22.8*) | 16.6 (19.2) [10] | 128.3* (132.2*) | 28.8* (30.0*) | 23.2* (24.6*) | 1884 / n.m. |
| E-PF | 130.4 (5 x 26.1) | 148.0 | 5 | 6.79* (6.90*) | 1.54* (1.61*) | 1.40 (1.48) [40] | 9.90* (9.95*) | 2.15* (2.25*) | 1.70 (1.72) [24] | 1718 / 4455 |

- E Seconds per cell = batch wall time / batch size; median and p90 over the timed batches; [n] = timed cells after warm-up. Peak memory = process peak RSS at 16 threads, from direct runs only (n.m. = not measured).
- \* = composed (S): forwards per cell x the unit forward of the same model, threads and batch (one PF or one HRNet view with its softmax, `UPF_*` / `UHR_*`); p90\* = forwards x unit p90, an upper bound. The additivity check (3.2) puts composed cells within about -5 % to +15 % of the direct runs.
- E Host load: the first unit runs (11:37 to 11:52) shared the CPU with one other user's process (about 1 core). From 11:51:51 another team job (`scripts/bench_read_w1.py`, 8 worker processes, nice 10) and from 11:58 another user's training (about 1.3 cores) also ran. So every whole-arm run and the batch-8 runs at 1 thread and partly at 8 threads ran on a busier host (1-min load average 13 to 23, our own 16 threads included, against 2 to 16 for the first unit runs; `B/raw/summary_timing.tsv`). The unit re-check (60 cells each, 12:09) under that load was 13 % (PF) and 8 % (HRNet) slower than the first unit runs. Composed cells use the first unit runs.

### 3.2 Additivity check (gaint CPU, 16 threads)

| Direct run | median s per cell | forwards x unit median (first unit run) | ratio | forwards x unit median (re-check, same host load) | ratio |
|---|---|---|---|---|---|
| C1D4_b1_t16 | 2.23 | 1.72 | 1.291 | 1.95 | 1.143 |
| C1D4_b8_t16 | 2.81 | 2.64 | 1.067 | n.m. |  |
| C2_b1_t16 | 3.88 | 3.21 | 1.209 | 3.48 | 1.117 |
| C2_b8_t16 | 4.56 | 4.65 | 0.981 | n.m. |  |
| C2vb_b1_t16 (views batched) | 4.43 | 3.21 | 1.381 | 3.48 | 1.276 |
| C3_b1_t16 | 16.6 | 16.0 | 1.033 | 17.4 | 0.954 |
| EPF_b1_t16 | 1.40 | 1.08 | 1.295 | 1.22 | 1.146 |
| EPF_b8_t16 | 1.70 | 1.65 | 1.033 | n.m. |  |

- E Under the same host load (re-check columns) the direct runs are 0.95 to 1.15 x the sum of their unit forwards; C3 at batch 1 is 16.6 s direct against 16.0 to 17.4 s composed.
- E Batching the 8 D4 views into one forward (C2, batch 1, 8 images per forward) is slower on this CPU: 4.43 s against 3.88 s per cell for the deployed sequential path. Batch 8 is also slower per cell than batch 1 for every unit (PF 0.330 v 0.216 s, HRNet 0.581 v 0.401 s at 16 threads). S: on this CPU, batch 1 with sequential views is the fastest layout tried.
- E Thread scaling, one view, batch 1: 1 to 16 threads speeds PF up 6.3 x (1.36 to 0.216 s) and HRNet 5.1 x (2.03 to 0.401 s).

### 3.3 Headline (E from 3.1; gaint CPU, 16 threads, batch 1)
| Row | Forwards per cell | GFLOPs per cell | s per cell, median (p90) | x C1 time | Cells per hour, one CPU (S: 3600 / median) |
|---|---|---|---|---|---|
| C1 | 1 | 148 | 0.216 (0.233) | 1.0 | about 16,700 |
| E-PF | 5 | 740 | 1.40 (1.48) | 6.5 | about 2,600 |
| C1-D4 | 8 | 1,184 | 2.23 (2.37) | 10.3 | about 1,600 |
| C2 | 8 | 1,744 | 3.88 (4.38) | 18.0 | about 930 |
| C3 | 40 | 8,722 | 16.6 (19.2), 10 cells | 76.9 | about 220 |

- S: C3 / E-PF is 11.9 x in CPU time (16.6 / 1.40), close to the FLOP ratio 11.8 x, not the forward ratio 8 x. C2 / C1 is 18 x in CPU time against 11.8 x in FLOPs: an HRNet view takes 1.9 x a PF view on this CPU (0.401 v 0.216 s) while it has 1.47 x the FLOPs.
- S: Network time only; image decode, preprocessing and writing results are extra (on cv02 they dominate the job wall time, section 4). GPU numbers: section 3.4.

### 3.4 cv02 GPU: one RTX A6000, fp32, TF32 off (E, `B/raw/gpu/*.json`, `B/raw/tables.md`, `B/raw/summary_timing.tsv`)
| Row | Forwards per cell | s per cell, batch 1: median (p90) [n] | x C1 (b1) | s per cell, batch 8: median (p90) [n] | Peak GPU alloc b1 / b8 (MiB) | Cells per hour, one GPU, b1 (S: 3600 / median) |
|---|---|---|---|---|---|---|
| C1 | 1 | 0.0112 (0.0112) [200] | 1.0 | 0.0099 (0.0099) [200] | 374 / 2,289 | about 322,000 |
| E-PF | 5 | 0.0559 (0.0561) [200] | 5.0 | 0.0491 (0.0492) [200] | 825 / 3,076 | about 64,000 |
| C1-D4 | 8 | 0.0911 (0.0915) [200] | 8.2 | 0.0800 (0.0800) [200] | 448 / 2,873 | about 39,500 |
| C2 | 8 | 0.174 (0.177) [200] | 15.5 | 0.133 (0.134) [200] | 445 / 2,993 | about 20,700 |
| C2, 8 views in one batch | 8 | 0.134 (0.135) [200] | 12.0 | - | 2,242 / - | about 26,800 |
| C3 | 40 | 0.855 (0.862) [200] | 76.6 | 0.675 (0.675) [200] | 819 / 3,702 | about 4,200 |
| one HRNet view (unit) | 1 | 0.0256 (0.0271) [200] | 2.3 | - | 372 / - | - |

- E Run: script `B/gpu/run_gpu_cv02_v2.sh` (6ee8e420) + `B/infer_cost.py` (a73868fa), on cv02 GPU 6 (RTX A6000, 49,140 MiB), 22 Nov 17:50:46 to 18:04:24 IST, all 13 configs rc 0, `ALL DONE` (`B/raw/gpu/driver.log`). Weights: the fin checkpoints in `/tmp/noob_el/bench_9967d59/experiments/fin_*_pool_s*/` (strict load; `weights: checkpoints` in every json). Inputs: random tensors of the real shape, as on CPU (no data read). torch 2.14.1+cu130, CUDA 13.0, smp 0.5.0, timm 1.0.30 (driver.log). Settings as the canonical dumps: fp32, TF32 off, cuDNN deterministic, benchmark off, 4 CPU threads. Timing: CUDA events + synchronize, 200 timed cells after warm-up per config.
- E Conditions: GPU 6 had no other process, 7 MiB and 0 % before every config (driver.log `before` lines). The host was shared: 1-min load average 13.0 to 18.0 on 64 CPUs during the run; four of our T3b trainings ran on GPUs 0, 1, 4, 5 and other users held GPU 0 (ds404_user14, lead log 17:47) and 2.5 GB on GPU 7 (nvidia-smi 17:47). S: host load can only make these numbers slower, so they are upper bounds for an idle A6000 at these settings.
- E Repeat check: the first attempt (`B/gpu/run_gpu_cv02.sh` cd3282ad, 17:48 to 17:50) measured C1, E-PF, C1-D4 and C2 at batch 1 before it stopped on a false not-idle reading (our own config had just ended; v2 only adds a 15 s pause before each idle check). v2 / v1 median ratio: 1.006, 1.003, 1.000, 1.006 (`B/raw/gpu_v1_partial/`).
- S: On the GPU an HRNet view costs 2.3 x a PF view (0.0256 v 0.0112 s), against 1.47 x the FLOPs and 1.9 x on the CPU. C2 / C1-D4 = 1.9 x; C3 / E-PF = 15.3 x on the GPU (11.9 x on the CPU). C2 per view in the 8-view loop is 21.7 ms, below the one-view config (25.6 ms), because the per-cell fixed cost is shared by 8 views; batching the 8 views gives 0.134 s per cell (-23 %).
- S: For deployment, C2 at batch 1 is about 0.17 s of network time per cell on one A6000, about 20,000 cells per hour; the E1 dump jobs took about 100 s for 106 cells (section 4), so network time (106 x 0.174 = 18 s) is under a fifth of the observed job time; the rest is start-up, data and writes.

## 4. Observed wall time on cv02 (E, dump logs; `B/raw/wall_jobs.tsv`, `B/raw/wall_summary.tsv`)
E Source: `/tmp/noob_el/bench_q/{open,fin}/launch.log` on cv02, read with `ssh -n -a -o BatchMode=yes cv02@10.8.1.106 cat ...`, copied to `B/raw/cv02_logs/`, parsed by `B/parse_launch_logs.py`. One job = one `scripts/bench_infer.py` process: start-up, CUDA init, checkpoint load, data load, inference (fp32, TF32 off, batch 8, D4 views sequential), dump writes, md5. Wall = 'start dump_...' line to 'dumped ... rc=0' line; the queue logs at about 10 s steps, so each wall time is +- 10 s. Log times are UTC (IST = UTC + 5:30).

Queue `open` (E1 opening #8 and test50 opening #19), armed 21 Nov 05:55:25, ALL DONE 06:28:14 UTC (32 min 49 s), 30 dump-only jobs, MAXC 4, LPG 1:

| Job | Arm | Set | logp written | Jobs | Cells per job | Wall s, median (range) | s per cell, median |
|---|---|---|---|---|---|---|---|
| HRNet+SWAD `swad`, D4 | C2 (one C3 member each) | E1 | yes | 5 | 106 | 100 (100 to 101) | 0.94 |
| PF `model`, plain | C1 (one E-PF member each) | E1 | yes | 5 | 106 | 90 (90 to 91) | 0.85 |
| PF `model`, D4 | C1-D4 | E1 | no | 5 | 106 | 40 (40 to 41) | 0.38 |
| HRNet+SWAD `swad`, D4 | C2 | test50 | no | 5 | 50 | 30 (30 to 30) | 0.60 |
| PF `model`, plain | C1 | test50 | no | 5 | 50 | 20 (20 to 21) | 0.40 |
| PF `model`, D4 | C1-D4 | test50 | no | 5 | 50 | 20 (20 to 30) | 0.40 |

Queue `fin` (the 75 CV5 out-of-fold D4 dumps of the cv5v3 runs; 21 Nov 00:56 to 02:23 UTC; no logp, E `harness/final/evidence/render_smoke/rendered.txt`: `--batch 8 --threads 4 --workers 4 --precision fp32 --tta d4`):

| Job | Arm | Jobs | Cells per job | Wall s, median (range) | s per cell, median |
|---|---|---|---|---|---|
| c3x HRNet+SWAD `swad`, D4 | C2 recipe, fold models | 25 | 101 to 111 | 50 (40 to 51) | 0.45 |
| c3 PF `model`, D4 | C1-D4 recipe, fold models | 25 | 101 to 111 | 40 (40 to 41) | 0.37 |
| c3x HRNet+SWAD `swad_bn`, D4 | information only | 25 | 101 to 111 | 41 (40 to 51) | 0.41 |

- E logp: the E1 C1 and C2 jobs also wrote float16 log-probabilities, 24 x 512 x 512 per cell (12.6 MB; 1.33 GB per job), because they were ensemble members (`opening_make_jobs.py` l3 to l6, job field 8). A PF job with 8 views and no logp (40 s) finished faster than a PF job with 1 view and logp (90 s).
- E C3 and E-PF were never run as one job: C3 on E1 = 5 C2 jobs (5 x 100 s = 500 GPU-s, 4.7 GPU-s per cell), E-PF = 5 C1 jobs (450 GPU-s, 4.2 GPU-s per cell), then the mean softmax on gaint (`bench_ens_dump.py`; its time is not in these logs).
- E Sharing: cv02 is shared with other users. During `open`, another user held 15,050 to 27,556 MiB on each of GPUs 0, 1, 4, 5 (249 log lines). Our dumps ran on GPUs 2, 3, 6, 7 (20, 7, 2, 1 jobs), each with 48,536 MiB free at its start, and no other-user process above 4,096 MiB was logged on those GPUs (the queue logs other users only above 4,096 MiB, so smaller processes are not excluded). During `fin` the dumps ran on GPUs 0, 1, 5, 6 while trainings of `fin` ran on other GPUs (the 5 HRNet trainings until 01:48 UTC; up to 7 of our other jobs running at a dump start, none on the same GPU; free memory at start 48,536 or 48,500 MiB). CPU, disk and PCIe were shared in both queues.
- S: these wall times are dominated by fixed costs (process start, CUDA init, checkpoint and data load, dump writes, md5), not by the network: 8 forwards per cell (C1-D4) and 1 forward (C1, test50) both take about 0.4 s per cell. They give only an upper bound on GPU time per forward, all overheads included: about 50 / (107 x 8) = 58 ms per HRNet view, 40 / (107 x 8) = 47 ms per PF view. A deployment number per cell needs the GPU script (section 6).

## 5. Not measured, and why
- E GPU: measured on one cv02 A6000 only (section 3.4), fp32 batch 1 and 8; not on the gaint GPU (excluded: root's `finllm_chat.py`, PID 5104). Peak memory is `torch.cuda.max_memory_allocated`, not the process total.
- E CPU, 1 thread: 50 cells at batch 1 and 24 cells at batch 8 per unit, not 200 (S: 200 HRNet cells at 1 thread alone take about 7 min per config; the budget was about 1.5 h on a shared host).
- E CPU, whole arms timed directly only at 16 threads (C3: 10 cells, about 16 s each; the others 24 to 40 cells). Every other cell of the CPU table is composed (marked *) from the unit forward of the same model, threads and batch; the additivity check under the table compares the two where both exist.
- E Peak memory: given only for configs run directly; not for composed cells.
- E Pre- and post-processing (PNG read, resize, normalise, argmax, dump maps, disk writes) not timed on CPU; on cv02 they are inside the job wall times of section 4.
- E Ensemble merge on gaint (`bench_ens_dump.py`) and the NAS relay: not in the two logs, not measured.
- E Only 512 x 512 input, fp32. bf16 / TF32 / `torch.compile` / ONNX were not tried (not the deployed path).

## 6. GPU latency script (run 22 Nov, section 3.4)
- E Script: `B/gpu/run_gpu_cv02.sh` (driver, cd3282ad) + `B/infer_cost.py` (same timing code as the CPU runs, `--device cuda`). Run by the lead as `B/gpu/run_gpu_cv02_v2.sh` (6ee8e420: the same plus a 15 s pause before each idle check) on cv02 GPU 6; the text below is the pre-run description.
- E What it runs on ONE GPU: C1, E-PF, C1-D4, C2, C3 at batch 1 and batch 8, C2 with the 8 views batched (batch 1), and one HRNet view (unit), 200 timed cells each after warm-up, CUDA events + synchronize; peak `torch.cuda.max_memory_allocated`. Settings as the canonical dumps: fp32, TF32 off, cuDNN deterministic, benchmark off (`scripts/bench_infer.py` l148 to l152), 4 CPU threads. Weights: fin2 checkpoints on cv02 (strict load), or random init with `none` (same compute).
- E Guard: before every config it requires the chosen GPU to have no compute process, under 1,024 MiB used and at most 5 % utilisation in 5 samples 1 s apart; otherwise it stops (rc 3) and kills nothing. Each config is capped at 600 s. It writes only to `/tmp/noob_el/infer_cost/out_gpu<g>/`.
- S Before running: no queue of ours may be armed on that GPU (a queue lane counts only its own jobs, so it could start a training there mid-run); the T3b queue must be ALL DONE, or the GPU outside its GPUS list. Then copy two files from gaint to cv02 `/tmp/noob_el/infer_cost/`: `B/infer_cost.py` and `B/gpu/run_gpu_cv02.sh`.
- E Exact command, on cv02, with g = an idle GPU index:
  `cd /tmp/noob_el/infer_cost && nohup bash run_gpu_cv02.sh <g> > run_gpu.nohup 2>&1 &`
  Defaults: code and checkpoints from `/tmp/noob_el/bench_9967d59` (the F2 deploy that holds `experiments/fin_*_pool_s*/checkpoints/`); 2nd / 3rd arguments override them; 3rd = `none` for random init if `/tmp` was wiped.
- S Expected runtime: about 15 to 25 min. Basis: an A6000 view in fp32 without TF32 is about 10 to 15 ms (PF) and 25 to 35 ms (HRNet) by FLOPs, and at most 47 / 58 ms by the `fin` dump jobs (section 4); the longest config is C3 at batch 1 (200 cells x 40 forwards, about 3 to 5 min).
- E Afterwards: copy `out_gpu<g>/*.json` to gaint `B/raw/gpu/` and run `python B/summarise.py`; it adds the GPU table to `B/raw/tables.md`.
- S Not checked: the smp / timm / torch versions of the cv02 venv (`/tmp/noob_el/el-fault-detection/.venv`); the driver prints them into its log first.

## 7. Files (E)
- `B/infer_cost.py`: verify (strict loads, md5), flops (FlopCounterMode), time (one config per process; CPU or CUDA).
- `B/run_cpu.sh`, `B/run_cpu_extra.sh`: the CPU drivers that produced `B/raw/cpu/` (nice 10, `ps -p 5104` around every config).
- `B/parse_launch_logs.py`: section 4 from `B/raw/cv02_logs/{open,fin}_launch.log` to `B/raw/wall_jobs.tsv`, `B/raw/wall_summary.tsv`.
- `B/summarise.py`: `B/raw/tables.md`, `B/raw/summary_timing.tsv` (re-run it after the GPU json files are copied to `B/raw/gpu/`).
- `B/gpu/run_gpu_cv02.sh`: the GPU driver (first attempt, stopped after 4 configs); `B/gpu/run_gpu_cv02_v2.sh`: the run of section 3.4.
- `B/raw/gpu/*.json` + `driver.log` (v2, 13 configs), `B/raw/gpu_v1_partial/` (first attempt, 4 configs).
- `B/raw/verify.json`, `B/raw/flops.json`, `B/raw/cpu/*.json` (every timed batch in `times_s`), `B/raw/cpu/driver.log`, `B/raw/ps5104.log`, `B/raw/probe/` (4 short planning probes, 5 cells each, not used in the tables).
- `B/MD5.txt`: md5 of every file above and of this file.
