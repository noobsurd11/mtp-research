#!/bin/bash
# Wave 2b (bench_q_w2b_smoke): the lead runs this once, after the review of harness/LAUNCH_REQUEST_w2b.md.
# Arms /home/noob/work/bq/w2b_smoke in tmux bench_q_w2b_smoke from the bench_w2b worktree (REPO) at DEPLOY: 3 smoke jobs (--exit_after_step 200, rc 3 by design, MAXC 1, gate 11000); no dumps.
# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any
# GPU process that is not its own holds > 1,024 MiB. bench_setup.sh refuses (nothing started) if the session
# exists, the dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any experiments/<job> exists.
export Q=/home/noob/work/bq/w2b_smoke SES=bench_q_w2b_smoke DEPLOY=f678381b1906575a69403e54f9c823f5f02bee28 \
  JOBS_MD5=973308a9f2dd5f384b2826930b4be23c REPO=/home/noob/work/bench_wt_w2b MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
