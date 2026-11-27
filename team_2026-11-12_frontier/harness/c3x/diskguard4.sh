#!/bin/bash
# cv02 disk guard 4 (c3x, 17 Nov 2026) = harness/c3swad/diskguard3.sh (92794405) with the queue name, stop file and log changed.
# Covers the queue dir c3x. Below 20 GB free on /tmp it touches HOLD there (HOLD = no new start, training or dump; running runs go on).
# It starts and stops nothing else and deletes nothing. Stop: touch /tmp/noob_el/bench_q/DISKGUARD4_STOP.
set -u
L=/tmp/noob_el/bench_q/diskguard4.log
echo "[$(date '+%F %T')] diskguard start pid $$ (floor 20 GB; queues c3x)" >> $L
while [ ! -e /tmp/noob_el/bench_q/DISKGUARD4_STOP ]; do
  a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt 20 ]; then
    for q in c3x; do [ -d /tmp/noob_el/bench_q/$q ] && [ ! -e /tmp/noob_el/bench_q/$q/HOLD ] && touch /tmp/noob_el/bench_q/$q/HOLD && echo "[$(date '+%F %T')] HELD $q: free ${a} GB < 20" >> $L; done
  fi
  sleep 300
done
echo "[$(date '+%F %T')] diskguard stop file seen; exit" >> $L
