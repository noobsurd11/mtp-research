#!/bin/bash
# cv02 disk guard (lead, 16 Nov 2026): the reviewed tick command of LAUNCH_REQUEST_c3base.md section 6, in a loop, so a gap in the
# orchestrator session cannot fill /tmp. Below 20 GB free it touches HOLD in our queue dirs (HOLD = no new start; running runs go on).
# It starts and stops nothing else and deletes nothing. Stop: touch /tmp/noob_el/bench_q/DISKGUARD_STOP.
set -u
L=/tmp/noob_el/bench_q/diskguard.log
echo "[$(date '+%F %T')] diskguard start pid $$ (floor 20 GB; queues c3base c3hrnet rows2)" >> $L
while [ ! -e /tmp/noob_el/bench_q/DISKGUARD_STOP ]; do
  a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt 20 ]; then
    for q in c3base c3hrnet rows2; do [ -d /tmp/noob_el/bench_q/$q ] && [ ! -e /tmp/noob_el/bench_q/$q/HOLD ] && touch /tmp/noob_el/bench_q/$q/HOLD && echo "[$(date '+%F %T')] HELD $q: free ${a} GB < 20" >> $L; done
  fi
  sleep 300
done
echo "[$(date '+%F %T')] diskguard stop file seen; exit" >> $L
