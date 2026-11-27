#!/bin/bash
# Wave 2b (bench_q_w2b_lace): the lead runs this once, after the review of harness/LAUNCH_REQUEST_w2b.md.
# Arms /home/noob/work/bq/w2b_lace in tmux bench_q_w2b_lace from the bench_w2b worktree (REPO) at DEPLOY: 10 la_ce training jobs (MAXC 2), then 10 held-out dumps (MAXC 1).
# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any
# GPU process that is not its own holds > 1,024 MiB. bench_setup.sh refuses (nothing started) if the session
# exists, the dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any experiments/<job> exists.
export Q=/home/noob/work/bq/w2b_lace SES=bench_q_w2b_lace DEPLOY=f678381b1906575a69403e54f9c823f5f02bee28 \
  JOBS_MD5=f89627eb2034c22a3af2ed3c5e594e23 DJOBS_MD5=3759e8249fa4a112493f0258e11e9adb REPO=/home/noob/work/bench_wt_w2b MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
