#!/bin/bash
# Unseen-module block waiter (= the lead's bq/w1g2 and the w2a reviewer's wait_then_launch.sh pattern). NOT STARTED by the
# integrator. Waits until the previous gaint chain has written 'chain done' in its chain.log, sleeps 150 s, re-checks the
# pinned md5 of the next queue's launch.sh, then runs it once. Reason (REVIEW_W2A 4): an armed queue starts in the first
# moment no outside GPU process holds > 1,024 MiB, e.g. between the previous queue's training phase and its dump phase.
# Usage: PREV=/home/noob/work/bq/<prev> Q=/home/noob/work/bq/<next> PIN=<md5 of Q/launch.sh> bash wait_then_arm.sh
# Run inside tmux: tmux new-session -d -s bench_wait_<next> "PREV=... Q=... PIN=... bash <this file>"
# Stop the wait: touch $Q/NOSTART. Log: $Q/wait.log. Starts no GPU job itself. A previous chain that ends without
# 'chain done' (e.g. 'dumps not started', HOLD) never triggers the launch: a person looks first.
set -u
PREV=${PREV:?previous queue dir}; Q=${Q:?next queue dir}; PIN=${PIN:?md5 of next launch.sh}
L=$Q/wait.log; C=$PREV/chain.log
lg(){ echo "[$(date '+%F %T')] $*" >> $L; }
lg "wait start pid $$ (launch.sh md5 $(md5sum < $Q/launch.sh | cut -c1-8), MAXC $(cat $Q/MAXC)); waits for 'chain done' in $C"
while :; do
  [ -e $Q/NOSTART ] && { lg "NOSTART file; exit"; exit 0; }
  grep -q "chain done" $C 2>/dev/null && break
  sleep 60
done
lg "previous chain ended: $(grep 'chain done' $C | tail -1 | cut -c1-200)"
sleep 150
[ -e $Q/NOSTART ] && { lg "NOSTART file; exit"; exit 0; }
[ "$(md5sum < $Q/launch.sh | cut -c1-32)" = "$PIN" ] || { lg "launch.sh md5 != $PIN; not launching"; exit 1; }
bash $Q/launch.sh >> $L 2>&1; rc=$?
lg "launch rc=$rc"
