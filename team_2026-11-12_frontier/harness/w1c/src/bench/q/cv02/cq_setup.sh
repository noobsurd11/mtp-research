#!/bin/bash
# cv02 setup: arm one prepared queue dir in a new tmux session on cv02 (window gm = cq_gpumem.sh, window q = cq.sh).
# Run ON cv02 by the launcher (reviewer), e.g. from gaint: ssh cv02@10.8.1.106 'B=... Q=... SES=... bash $B/bench/q/cv02/cq_setup.sh'.
# Env (required): B, Q, SES (bench_q_*), DEPLOY (full commit), JOBS_MD5, DATA_MD5. Optional: GPUS, DATA (passed to cq.sh).
# Refuses (one line, exit 1, nothing started) if: the session exists; Q is armed or used (queue.pid, gpumem.pid, HOLD, pids/,
#   a non-empty launch.log); jobs md5 differs; REVISION != DEPLOY or CODE.md5 fails; LPG not 1 or 2; any job's
#   experiments/<name> or .stdout exists (except dumptest_* fixtures, which must exist).
set -u
B=${B:?}; Q=${Q:?}; SES=${SES:?}; DEPLOY=${DEPLOY:?}; JOBS_MD5=${JOBS_MD5:?}; DATA_MD5=${DATA_MD5:?}
no(){ echo "cq_setup: REFUSED: $*"; exit 1; }
case "$SES" in bench_q_*) ;; *) no "session name must start with bench_q_";; esac
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
[ -s $Q/jobs.txt ] || no "$Q lacks jobs.txt"
for f in queue.pid gpumem.pid HOLD pids; do [ -e $Q/$f ] && no "$Q/$f exists (armed or used)"; done
[ -s $Q/launch.log ] && no "$Q/launch.log not empty (armed or used)"
[ "$(md5sum < $Q/jobs.txt | cut -c1-32)" = "$JOBS_MD5" ] || no "$Q/jobs.txt md5 != JOBS_MD5"
[ "$(cat $B/REVISION)" = "$DEPLOY" ] || no "REVISION $(cat $B/REVISION) != $DEPLOY"
(cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "CODE.md5 check failed"
case "$(cat $Q/LPG 2>/dev/null || echo 2)" in 1|2) ;; *) no "LPG must be 1 or 2";; esac
while IFS='|' read -r n c s r k g d l x; do
  case "$n" in dumptest_*) [ -d $B/experiments/$n ] || no "fixture $n missing";;
    *) [ -e $B/experiments/$n ] || [ -e $B/experiments/$n.stdout ] && no "experiments/$n exists";; esac; done < $Q/jobs.txt
H=$B/bench/q/cv02
tmux new-session -d -s "$SES" -n gm "Q=$Q nice -n 19 bash $H/cq_gpumem.sh"
sleep 3
tmux new-window -t "=$SES:" -n q "B=$B Q=$Q JOBS_MD5=$JOBS_MD5 DEPLOY=$DEPLOY DATA_MD5=$DATA_MD5 ${GPUS:+GPUS='$GPUS' }${DATA:+DATA=$DATA }bash $H/cq.sh"
sleep 8
echo "cq_setup: $SES armed: gpumem $(cat $Q/gpumem.pid 2>/dev/null) queue $(cat $Q/queue.pid 2>/dev/null)"
tail -3 $Q/launch.log
