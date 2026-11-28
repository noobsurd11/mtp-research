#!/bin/bash
# x4: wait until every run of one arm stage is relayed in the queue's relay dir, then score it on CPU and run its read.
# Usage (gaint, in tmux bench_x4_auto_<tag>): bash x4_auto_read.sh <tag> <QN> <ARM> <SHORT> <METHOD> <KEY> <STAGE P|S>
#   Stage P: seed 5 runs, folds 0 to 4, read against COMBO seed 5 (PATHFINDER_RULE.md 26474b34); stage S: seeds 5 and 6.
#   Waits for /home/noob/work/bench_relay/x4_<QN>/.ok/x4_<SHORT>_f<k>_s<s> of every needed run (poll 120 s; stops on
#   relay GIVE UP / DISK GUARD of that run or after MAXH hours, default 30). Then: x4_queue.sh score <QN>; x4_read.sh <tag>.
#   Output: /home/noob/work/bench_reads/x4_<tag>/verdict.txt; status line in X/evidence/auto_<tag>.log ("AUTO READ DONE").
set -u
H=$(dirname "$(readlink -f "$0")")
TAG=${1:?}; QN=${2:?}; ARM=${3:?}; SH=${4:?}; ME_=${5:?}; KEY=${6:?}; ST=${7:?}; MAXH=${MAXH:-30}
case "$ST" in P) SEEDS=5;; S) SEEDS=5,6;; *) echo "stage P or S"; exit 1;; esac
RD=/home/noob/work/bench_relay/x4_$QN; L=$H/evidence/auto_$TAG.log; T0=$(date +%s)
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
need(){ local s k; for s in ${SEEDS//,/ }; do for k in 0 1 2 3 4; do echo x4_${SH}_f${k}_s$s; done; done; }
say "auto read $TAG: arm $ARM = x4_$SH ($ME_, key $KEY), stage $ST, seeds $SEEDS, relay $RD"
while :; do
  miss=$(for n in $(need); do [ -e $RD/.ok/$n ] || echo $n; done)
  [ -z "$miss" ] && break
  if grep -qE "GIVE UP ($(need | paste -sd'|'))|DISK GUARD" $RD/relay.log 2>/dev/null; then say "STOPPED: relay gave up or hit the disk guard; read not run"; exit 1; fi
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { say "STOPPED: MAXH $MAXH h; missing: $(echo $miss | tr '\n' ' ')"; exit 1; }
  sleep 120
done
say "all $(need | wc -l) runs relayed; scoring"
bash $H/x4_queue.sh score $QN >> $L 2>&1
say "read start"
SEEDS=$SEEDS STAGE=$ST bash $H/x4_read.sh $TAG "$ARM=$QN:$SH:$ME_:$KEY" > $H/evidence/read_$TAG.log 2>&1; rc=$?
say "AUTO READ DONE rc=$rc: verdict /home/noob/work/bench_reads/x4_$TAG/verdict.txt"
grep -E "^=>|^stageP" /home/noob/work/bench_reads/x4_$TAG/verdict.txt >> $L 2>/dev/null
