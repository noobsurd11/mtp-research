#!/bin/bash
# cv02 disk guard 7 (final opening, review round 1 N7; renamed from 6 for fin2, REVIEW_FIN2 N2, 21 Nov 2026) = harness/final/diskguard5.sh (2719c5f7) with the queue name,
# stop file and log changed. Covers the queue dir open. Below 20 GB free on /tmp it touches HOLD there (HOLD = no new dump
# start; running dumps go on). It starts and stops nothing else and deletes nothing. Stop: touch /tmp/noob_el/bench_q/DISKGUARD7_STOP.
set -u
L=/tmp/noob_el/bench_q/diskguard7.log
echo "[$(date '+%F %T')] diskguard start pid $$ (floor 20 GB; queues open)" >> $L
while [ ! -e /tmp/noob_el/bench_q/DISKGUARD7_STOP ]; do
  a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt 20 ]; then
    for q in open; do [ -d /tmp/noob_el/bench_q/$q ] && [ ! -e /tmp/noob_el/bench_q/$q/HOLD ] && touch /tmp/noob_el/bench_q/$q/HOLD && echo "[$(date '+%F %T')] HELD $q: free ${a} GB < 20" >> $L; done
  fi
  sleep 300
done
echo "[$(date '+%F %T')] diskguard stop file seen; exit" >> $L
