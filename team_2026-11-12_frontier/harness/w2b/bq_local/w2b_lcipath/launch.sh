#!/bin/bash
# Wave 2b (bench_q_w2b_lcipath): the lead runs this once, after the review of harness/LAUNCH_REQUEST_w2b.md.
# Arms /home/noob/work/bq/w2b_lcipath in tmux bench_q_w2b_lcipath from the bench_w2b worktree (REPO) at DEPLOY: the layered_ci pathfinder (1 training job, 20k steps), then 3 fold-0 dumps.
# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any
# GPU process that is not its own holds > 1,024 MiB. bench_setup.sh refuses (nothing started) if the session
# exists, the dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any experiments/<job> exists.
export Q=/home/noob/work/bq/w2b_lcipath SES=bench_q_w2b_lcipath DEPLOY=f678381b1906575a69403e54f9c823f5f02bee28 \
  JOBS_MD5=06752167e7dd291c053de9197c7ec667 DJOBS_MD5=b798b2a67007bb909f32254387d34073 REPO=/home/noob/work/bench_wt_w2b MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
