#!/bin/bash
# Wave 2a (bench_q_w2a_smoke): the reviewer runs this once, after the checklist in harness/LAUNCH_REQUEST_w2a.md passes.
# Arms w2a_smoke in tmux bench_q_w2a_smoke from the bench_w2 worktree (REPO) at DEPLOY: 6 smoke jobs (--exit_after_step 50, rc 3 by design, MAXC 1, gate 11000); no dumps.
# The queue shares the gpu_gate with every other queue (free >= gate, 120 s since any start) and waits while any
# GPU process that is not its own holds > 1,024 MiB (W1-G), so arming it while W1-G runs is safe.
# bench_setup.sh refuses (nothing started) if the session exists, this dir is armed or used, an md5 or HEAD differs,
# a tracked change exists, or any experiments/<job> exists. MAXH: logger and guard lifetime in h (default 24 is too short).
export Q=/home/noob/work/bq/w2a_smoke SES=bench_q_w2a_smoke DEPLOY=c57508ec458b54d935a8c3ffcfe722ff2acadb38 \
  JOBS_MD5=51cb712fdeda2fd91bd6ca445ca06f7e REPO=/home/noob/work/bench_wt_w2 MAXH=120
exec bash $REPO/bench/q/bench_setup.sh
