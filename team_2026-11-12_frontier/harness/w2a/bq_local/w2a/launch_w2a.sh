#!/bin/bash
# Wave 2a (bench_q_w2a): the reviewer runs this once, after the checklist in harness/LAUNCH_REQUEST_w2a.md passes.
# Arms w2a in tmux bench_q_w2a from the bench_w2 worktree (REPO) at DEPLOY: 61 training jobs (MAXC 3, gate 11000), then 161 held-out dumps (MAXC 1, gate 6200).
# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any
# GPU process that is not its own holds > 1,024 MiB (W1-G), so arming it while W1-G runs is safe.
# bench_setup.sh refuses (nothing started) if the session exists, this dir is armed or used, an md5 or HEAD differs,
# a tracked change exists, or any experiments/<job> exists. MAXH: logger and guard lifetime in h (default 24 is too short).
export Q=/home/noob/work/bq/w2a SES=bench_q_w2a DEPLOY=c57508ec458b54d935a8c3ffcfe722ff2acadb38 \
  JOBS_MD5=d8be4f16c79a499ebff2d822068f4870 DJOBS_MD5=0bcef5368e50b5df75326359edcb6da3 REPO=/home/noob/work/bench_wt_w2 MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
