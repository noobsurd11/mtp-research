#!/bin/bash
# gaint relay guard for the fin relay (final package, 21 Nov 2026) = harness/c3x/c3x_relayguard.sh (c221e73a) with the relay list (fin
# only), the log and the stop file changed; no other relay guard is touched.
# Run by the LEAD on gaint in tmux, started beside the fin relay:  tmux new-session -d -s bench_relayguard_fin "bash <this file>"
# Every 300 s it reads the free space of the filesystem that holds the relay dirs (gaint has one filesystem, / ). Below 15 GB
# free it touches STOP in bench_relay/fin if that relay is alive (relay.pid names a live process), and logs it. It does nothing
# else: it starts nothing, signals nothing, deletes nothing, and never touches cv02. STOP ends the relay at the top of its
# next poll pass (relay_w1c.sh 74a2ec3d l.38); runs not relayed stay on cv02. Restart after freeing: RESUME=1 FB=<dir> bash final_relay.sh.
# Stop this guard: touch /home/noob/work/bench_c3_io/RELAYGUARD_FIN_STOP. Log: /home/noob/work/bench_c3_io/relayguard_fin.log.
# For tests only: RR (relay root), FLOOR (GB), LOGD (folder of log and stop file), ONCE=1 (one pass, no sleep).
set -u
RR=${RR:-/home/noob/work/bench_relay}; FLOOR=${FLOOR:-15}; LOGD=${LOGD:-/home/noob/work/bench_c3_io}; ONCE=${ONCE:-0}
L=$LOGD/relayguard_fin.log
echo "[$(date '+%F %T')] relay guard start pid $$ (floor $FLOOR GB on the filesystem of $RR; relays fin)" >> $L
while [ ! -e $LOGD/RELAYGUARD_FIN_STOP ]; do
  a=$(df --output=avail -BG $RR | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt "$FLOOR" ]; then
    for r in fin; do d=$RR/$r
      [ -d $d ] && [ ! -e $d/STOP ] && kill -0 "$(cat $d/relay.pid 2>/dev/null)" 2>/dev/null && touch $d/STOP && echo "[$(date '+%F %T')] STOP set for relay $r: free ${a} GB < $FLOOR" >> $L; done
  fi
  [ $ONCE = 1 ] && break
  sleep 300
done
echo "[$(date '+%F %T')] relay guard ends (stop file or ONCE)" >> $L
