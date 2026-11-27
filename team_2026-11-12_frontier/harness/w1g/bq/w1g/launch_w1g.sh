#!/bin/bash
# W1-G launch (13 Nov): the reviewer runs this once, after all 8 checklist items of LEAD_INSTRUCTIONS.md pass.
# Arms /home/noob/work/bq/w1g in tmux bench_q_w1g (gm = 1 s gpumem log, guard = auto-stop watcher, q = bench_chain.sh:
# 10 training jobs, MAXC 3, gate 9,000, then 10 held-out dumps, MAXC 1, gate 6,200). Pinned: el_bench commit, both job md5s.
# bench_setup.sh refuses (nothing started) if the session exists, this dir is armed or used, an md5 or HEAD differs,
# a tracked change exists, or any experiments/<job> exists.
export Q=/home/noob/work/bq/w1g SES=bench_q_w1g DEPLOY=31c0c368ee65742893a36523bcf48e366ea948ed \
  JOBS_MD5=4f5a55350ea253cea794cf465fa11aa5 DJOBS_MD5=240890b5ee3150c62f8c3102b23bda44 REPO=/home/noob/work/el_bench
exec bash $REPO/bench/q/bench_setup.sh
