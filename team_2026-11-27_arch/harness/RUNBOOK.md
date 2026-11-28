# RUNBOOK: the cv5v3 COMBO comparator and the x4 screening pipeline (harness engineer, 27 Nov 2026)

E = measured by command (source given), S = judgement. Paths: T = /home/yugma/mtp/research/team_2026-11-12_frontier (gaint),
H = /home/yugma/mtp/research/team_2026-11-27_arch/harness (gaint; copy on the laptop), X = H/x4. cv02 clock is UTC, gaint IST.
Hosts: gaint `ssh -o BatchMode=yes noob@172.18.22.20`; cv02 `ssh -n -a -o BatchMode=yes cv02@10.8.1.106` (shared lab login).

## 1. COMBO = HRNet-W18 U-Net++ + PF + SWAD, swad readout (the x4 comparator)
| Item | Value (E) | Source |
|---|---|---|
| el_bench commit | 03375d4c5e9ddde040603230eaca2b1c1139e14c (branch bench_c3s, parent 852ed5c, tree c860f1bc) | worktree /home/noob/work/bench_wt_c3s; T/harness/LAUNCH_REQUEST_c3x.md s4 |
| card | bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml md5 98f152de3ea7f8c88e892162e07b4450; cv02 variant bench/methods_cv02/... d7b207089f6cfeb484ca9ef96f734786 (weights path only) | LAUNCH_REQUEST_c3x.md s10 |
| encoder weights | timm hrnet_w18.ms_aug_in1k rev 7e2c5583, model.safetensors md5 e6bb005ddbe1b52bde05618fc6b4b8e3 (cv02: /tmp/noob_el/cache/hf/...) | card; cvcard.py |
| cv02 deploy | /tmp/noob_el/bench_03375d4 (REVISION 03375d4, md5 of CODE.md5 a8cc84a3a2535611de6185015275534a) | cv02 |
| queue | cv02 /tmp/noob_el/bench_q/c3x, jobs.txt md5 3304573e8cbdf3c1b26c2b5f3ab21957 (25 lines, seeds 5 to 9 x folds 0 to 4), rendered 2ebc9e38, cq.sh 14d33b80, LPG 1, MAXC 8, gate 11,510, dump gate 6,200, armed 2026-11-17 23:31 UTC | c3x/launch.log |
| job line (f0 s5) | `c3x_hrnet_swad_v11_f0_s5\|bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml\|5\|/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0\|0\|11510\|6200\|0\|\|swad` | c3x/jobs.txt |
| training command (cwd B) | `/tmp/noob_el/el-fault-detection/.venv/bin/python -u scripts/train.py --config configs/supervised.yaml --opts seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=masks_v11 data.mask_ignore_value=255 model.name=bench_smp model.decoder=unetplusplus model.encoder_name=tu-hrnet_w18 model.encoder_weights=imagenet data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000 training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 training.lr_scheduler=constant training.weight_avg.swad.mode=uniform training.weight_avg.swad.start=10000 training.weight_avg.swad.end=20000 training.weight_avg.ema_9998.mode=ema training.weight_avg.ema_9998.decay=0.9998 training.bn_recal=true training.enc_probe_every=2000 data.root=/tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f0 run_name=c3x_hrnet_swad_v11_f0_s5` (env CUDA_VISIBLE_DEVICES=<gpu> HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4, /tmp/noob_el/env.sh) | c3x/jobs_rendered.txt |
| dump commands | `python -u scripts/bench_infer.py --run B/experiments/<name> --set cv5v3_f<k> --dumps B/dumps --method hrnet_w18_unetpp_swad_const_pf_v11 --card bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml --run-id <name> --device cuda --precision fp32 --threads 4 --workers 4 --batch 8 --forbidden /tmp/noob_el/bench_data/meta/forbidden_v1.txt --bench-run dump_<name>` (key swad_bn), then the same with `--run-id <name>.swad --weights-key swad --bench-run dump_<name>.swad` (the comparator readout). Canonical fp32, TF32 off, held-out fold only; writer bench_infer.py afd9164264de4d91e43e258e6f8b1836 | jobs_rendered.txt; manifests |
| roots (v1.1) | cv02 /tmp/noob_el/bench_data_v3b/roots/cv5v3_v11_f{0..4}: train 425 / val = test = held-out fold (f0: 107); ROOTS_cv5v3_v11.md5 md5 c7bc65433ee7d3a7b7e1a9a32c0c5078; DATA (/tmp/noob_el/bench_data) DEPLOY.md5 md5 d6063fd83d20e656612540edda702cbe; train masks v1.1 with ignore 255, held-out masks strict | cq.sh arming checks |
| peak memory | training 9,386 MiB on cv02 in all 25 runs; dump 3,944 MiB | c3x/gpumem.log |
| run time | training median 155 min (116 to 269), dumps + slim median 4 min; LPG 1, 10 of 25 started on GPUs shared with other users | c3x/launch.log |
| relay | gaint /home/noob/work/bench_relay/c3x/<run>/ (RUN.md5, config_used.yaml, slim.pth, LATEST.md5, enc_probe.jsonl, dumps/elbench1/<method>/<run>{,.swad}/cv5v3_f<k>/), .ok/<run>; relay_w1c.sh 74a2ec3d (md5 on both ends) | T/harness/c3x/c3x_relay.sh |
| PF reference dumps | gaint /home/noob/work/bench_relay/c3base/c3_pf_v11_f<k>_s<s>/dumps/elbench1/house_r34_unetpp_pf_v11/... (seeds 5 to 9; key model; train code 89b9ea5) | run_read_c3x.sh |
| registered read | T/harness/c3x/run_read_c3x.sh (060e24a2) -> bench_wt_final 89b9ea5 scripts/bench_read_w1.py (fdb56b78), groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv (d880a769, 285 groups), score_exclude T/benchmark/splits/score_exclude_v3.txt (6d48dfbd, 416 clean cells), 2,000 draws, A/A PF:5,6:7,8; rule c3x_verdict.py (faa2a961); output /home/noob/work/bench_reads/c3x (read.json 47ba2005) | T/results/C3X_READ.md |
| margin M (PROTOCOL v1.0 s5.4 table) | cv02 cv5v3: 0.0100 on 532 cells AND 0.010 on the 416 clean cells. The 0.0111 in the table is cv02 **cv5v2** 416 clean, not cv5v3 | T/benchmark/PROTOCOL_v1.0.md l.183 to 187 |

## 2. x4 pipeline (commit X4 = 399f9635a23da1152df6b60ba70b30f813dc3fac, branch bench_x4, worktree /home/noob/work/bench_wt_x4)
X4 = 03375d4 + 69609c1 (cq.sh / cq_setup.sh accept LPG 3) + 23717a7 (smoke card, 50 steps) + 399f963 (smoke card 600 steps). Training,
dump, slim code byte-equal to COMBO's (git diff and cv02 CODE.md5 diff: 4 paths + REVISION). cv02 deploy XB = /tmp/noob_el/bench_399f963
(CODE.md5 md5 08a4cddc). Relay: X/x4_relay.sh (relay_w1c.sh + skip slim.pth + READ_ONLY: a run with a .swad dump leaves its primary
dump on cv02 + gaint disk guard 15 GB). Sizes (E, fold 0, 107 cells): full run 463 MB = slim 168 + primary dump 151 + .swad dump 144;
x4 relay pulls 139 MB; cv02 keeps about 1.25 GB per run (latest.pth 756 MB). Read cache about 5.6 MB per dump.
| Step | Command (gaint, in X unless stated) |
|---|---|
| card | add bench/methods/<m>.yaml + bench/methods_cv02/<m>.yaml (weights paths only differ) in bench_wt_x4, commit, re-deploy: `bash T/harness/c3base/c3_deploy.sh <new commit>` and run `X4=<new commit> ...` below |
| jobs | `python x4_make_jobs.py --out jobs/<qn>.tsv bench/methods/<m>.yaml=<short>@<peak MiB>` (seeds 5, 6, folds 0 to 4; gate = max(card gate, peak + 2,048); 10th field swad when the card has a swad readout); writes jobs/<qn>.tsv.md5 |
| place | `bash x4_queue.sh place <qn> jobs/<qn>.tsv 3 15` (cv02 /tmp/noob_el/bench_q/x4_<qn>; LPG 3, MAXC 15; no SHARE files) |
| guard | `bash x4_queue.sh guard` (once; cv02 tmux bench_diskguard_x4, HOLD below 20 GB) |
| arm | `bash x4_queue.sh arm <qn>` (cv02 tmux bench_q_x4_<qn>; refuses if another live queue of ours can start) |
| relay | `bash x4_queue.sh relay <qn> <N runs>` (gaint tmux bench_relay_x4_<qn> -> /home/noob/work/bench_relay/x4_<qn>; x4_relay.sh; per-run floor 15 GB, DISK_HOLD; `READ_ONLY=0` also pulls the primary dump, `SKIP_RX='^$'` everything) |
| score | `bash x4_queue.sh score <qn>` (frozen scorer bench_score.py records per relayed dump folder, CPU) |
| read | `tmux new-session -d -s bench_x4_read_<tag> "bash X/x4_read.sh <tag> <ARM>=<qn>:<short>:<method>:swad > X/evidence/read_<tag>.log 2>&1"` -> /home/noob/work/bench_reads/x4_<tag>/verdict.txt |
| status / stop | `bash x4_queue.sh status <qn>`; `bash x4_queue.sh hold <qn>` (no new start); a running job: on cv02 compare `ps -o args= -p $(cat /tmp/noob_el/bench_q/x4_<qn>/pids/<job>.pid)` with `pids/<job>.cmdline`, then `kill` that PID only |
