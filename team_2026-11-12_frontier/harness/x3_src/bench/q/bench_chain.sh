#!/bin/bash
# elbench chain: training queue, then the dump queue, in one tmux window, unattended (started by bench_setup.sh).
# Phase 1: bench_q.sh on Q (training jobs; logger + guard of Q started by bench_setup.sh). It returns after its end line
#   "BENCH Q ALL DONE"; a queue held by HOLD never returns (by design: then nothing more starts until a person looks).
# Phase 2 (only if DQ/jobs.txt exists and phase 1 wrote its end line): new tmux windows dgm (1 s gpumem log of DQ) and
#   dguard (auto-stop watcher of DQ) in session SES, then bench_q.sh on DQ: every line is an 'other' job whose command is
#   scripts/bench_infer.py ... --bench-run <name> (verify token; it prints 'BENCH_START: run=<name>', the start check), so
#   dumps go through the same gate, MAXC, PID record, live check and guard as training. A dump of a run that failed
#   stops on bench_infer's own asserts (no latest.pth, or step != total_steps) and is logged as rc != 0; nothing else waits.
# Env: Q, JOBS_MD5, DEPLOY, SES (tmux session, without '='), DQ (default Q/dump), DJOBS_MD5 (required if DQ/jobs.txt),
#      REPO (default /home/noob/work/el_bench); passed through to bench_q.sh: P, W, LIVE_WAIT, OUTSIDE_MIB, GG, GAPSEC.
# Log: Q/chain.log. rc captured before any $(date).
set -u
Q=${Q:?queue dir}; SES=${SES:?tmux session}; DQ=${DQ:-$Q/dump}; R=${REPO:-/home/noob/work/el_bench}
HERE=$(cd "$(dirname "$0")" && pwd); C=$Q/chain.log
cl(){ echo "[$(date '+%F %T')] $*" >> $C; }
cl "chain start pid $$ (Q $Q, DQ $DQ, session $SES, bench_q $(md5sum < $HERE/bench_q.sh | cut -c1-8), chain $(md5sum < $0 | cut -c1-8))"
bash $HERE/bench_q.sh; rc=$?
cl "phase 1 (training queue) exited rc=$rc; end line: $(grep -c 'BENCH Q ALL DONE' $Q/launch.log)"
[ $rc = 0 ] && grep -q "BENCH Q ALL DONE" $Q/launch.log || { cl "phase 1 did not end cleanly; dumps not started"; exit 1; }
[ -s $DQ/jobs.txt ] || { cl "no $DQ/jobs.txt; chain done"; exit 0; }
DJOBS_MD5=${DJOBS_MD5:?dump jobs md5}
for f in queue.pid gpumem.pid guard.pid HOLD; do [ -e $DQ/$f ] && { cl "$DQ/$f exists (dump queue already armed or held); dumps not started"; exit 1; }; done
tmux new-window -t "=$SES:" -n dgm "Q=$DQ nice -n 19 bash $HERE/bench_gpumem.sh"
tmux new-window -t "=$SES:" -n dguard "Q=$DQ LIB=$HERE/bench_lib.sh bash $HERE/bench_guard.sh"
t=0; while [ $t -lt 30 ] && ! { kill -0 "$(cat $DQ/gpumem.pid 2>/dev/null)" 2>/dev/null && kill -0 "$(cat $DQ/guard.pid 2>/dev/null)" 2>/dev/null; }; do sleep 1; t=$((t+1)); done
cl "phase 2: dump logger pid $(cat $DQ/gpumem.pid 2>/dev/null), dump guard pid $(cat $DQ/guard.pid 2>/dev/null) (after ${t}s)"
Q=$DQ JOBS_MD5=$DJOBS_MD5 DONE_RX='^dumped ' bash $HERE/bench_q.sh; rc=$?
cl "phase 2 (dump queue) exited rc=$rc; end line: $(grep -c 'BENCH Q ALL DONE' $DQ/launch.log); chain done"
