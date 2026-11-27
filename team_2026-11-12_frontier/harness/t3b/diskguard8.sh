#!/bin/bash
# cv02 disk guard 8 (T3b, 21 Nov 2026) = harness/final/opening/diskguard7.sh (1771e3fc) with the queue names, stop file and log
# changed. Covers the queue dirs t3b and t3bopen. Below 20 GB free on /tmp it touches HOLD there (HOLD = no new start;
# running jobs go on). It starts and stops nothing else and deletes nothing. Stop: touch /tmp/noob_el/bench_q/DISKGUARD8_STOP.
set -u
L=/tmp/noob_el/bench_q/diskguard8.log
echo "[$(date '+%F %T')] diskguard start pid $$ (floor 20 GB; queues t3b t3bopen)" >> $L
while [ ! -e /tmp/noob_el/bench_q/DISKGUARD8_STOP ]; do
  a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt 20 ]; then
    for q in t3b t3bopen; do [ -d /tmp/noob_el/bench_q/$q ] && [ ! -e /tmp/noob_el/bench_q/$q/HOLD ] && touch /tmp/noob_el/bench_q/$q/HOLD && echo "[$(date '+%F %T')] HELD $q: free ${a} GB < 20" >> $L; done
  fi
  sleep 300
done
echo "[$(date '+%F %T')] diskguard stop file seen; exit" >> $L
