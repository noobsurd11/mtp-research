#!/bin/bash
# elbench setup: arm one prepared queue dir in a new tmux session (windows gm = 1 s gpumem log, guard = auto-stop watcher,
# q = bench_chain.sh: the training queue, then the dump queue of Q/dump). Run by the launcher (reviewer), never by a job.
# Env (all required except REPO, DJOBS_MD5): Q (prepared dir with jobs.txt and MAXC), SES (session name, bench_q_*),
#   DEPLOY (full el_bench commit), JOBS_MD5, DJOBS_MD5 (required if Q/dump/jobs.txt exists), REPO (default el_bench).
# Refuses (one line, exit 1, nothing started) if: the session exists; Q or Q/dump is armed or used (queue.pid, gpumem.pid,
#   guard.pid, HOLD, pids/, a non-empty launch.log or chain.log); a jobs md5 differs; HEAD != DEPLOY or a tracked change;
#   MAXC missing; any job's experiments/<name> or .stdout already exists.
set -u
Q=${Q:?queue dir}; SES=${SES:?session}; DEPLOY=${DEPLOY:?commit}; JOBS_MD5=${JOBS_MD5:?jobs md5}
R=${REPO:-/home/noob/work/el_bench}; DQ=$Q/dump; HERE=$R/bench/q
no(){ echo "bench_setup: REFUSED: $*"; exit 1; }
case "$SES" in bench_q_*) ;; *) no "session name must start with bench_q_";; esac
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
[ -s $Q/jobs.txt ] && [ -s $Q/MAXC ] || no "$Q lacks jobs.txt or MAXC"
for d in $Q $DQ; do [ -d $d ] || continue
  for f in queue.pid gpumem.pid guard.pid HOLD pids; do [ -e $d/$f ] && no "$d/$f exists (armed or used)"; done
  for f in launch.log chain.log; do [ -s $d/$f ] && no "$d/$f not empty (armed or used)"; done; done
[ "$(md5sum < $Q/jobs.txt | cut -c1-32)" = "$JOBS_MD5" ] || no "$Q/jobs.txt md5 != JOBS_MD5"
if [ -e $DQ/jobs.txt ]; then [ -s $DQ/MAXC ] || no "$DQ lacks MAXC"
  [ "$(md5sum < $DQ/jobs.txt | cut -c1-32)" = "${DJOBS_MD5:-}" ] || no "$DQ/jobs.txt md5 != DJOBS_MD5"; fi
[ "$(git -C $R rev-parse HEAD)" = "$DEPLOY" ] || no "$R HEAD $(git -C $R rev-parse HEAD) != $DEPLOY"
[ -z "$(git -C $R status --short --untracked-files=no)" ] || no "$R has tracked changes"
for n in $(cut -d'|' -f1 $Q/jobs.txt; [ -e $DQ/jobs.txt ] && cut -d'|' -f1 $DQ/jobs.txt); do
  [ -e $R/experiments/$n ] || [ -e $R/experiments/$n.stdout ] && no "experiments/$n exists"; done
tmux new-session -d -s $SES -n gm "Q=$Q nice -n 19 bash $HERE/bench_gpumem.sh"
tmux new-window -t "=$SES:" -n guard "Q=$Q LIB=$HERE/bench_lib.sh bash $HERE/bench_guard.sh"
sleep 3
tmux new-window -t "=$SES:" -n q "CUDA_VISIBLE_DEVICES=0 Q=$Q JOBS_MD5=$JOBS_MD5 DJOBS_MD5=${DJOBS_MD5:-} DEPLOY=$DEPLOY REPO=$R SES=$SES bash $HERE/bench_chain.sh"
sleep 5
echo "bench_setup: $SES armed: gpumem $(cat $Q/gpumem.pid 2>/dev/null) guard $(cat $Q/guard.pid 2>/dev/null) queue $(cat $Q/queue.pid 2>/dev/null)"
tail -3 $Q/launch.log
