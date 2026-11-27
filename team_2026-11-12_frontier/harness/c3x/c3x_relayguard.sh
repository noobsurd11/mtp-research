#!/bin/bash
# gaint relay guard for the c3x relay (17 Nov 2026) = harness/c3swad/c3swad_relayguard.sh (65b63ea7) with the relay list (c3x
# only), the log and the stop file changed; the running guard bench_relayguard (c3base, c3hrnet, rows2, c3swad) is not touched.
# Run by the LEAD on gaint in tmux, started beside the c3x relay:  tmux new-session -d -s bench_relayguard_c3x "bash <this file>"
# Every 300 s it reads the free space of the filesystem that holds the relay dirs (gaint has one filesystem, / ). Below 15 GB
# free it touches STOP in bench_relay/c3x if that relay is alive (relay.pid names a live process), and logs it. It does nothing
# else: it starts nothing, signals nothing, deletes nothing, and never touches cv02. STOP ends the relay at the top of its
# next poll pass (relay_w1c.sh 74a2ec3d l.38); runs not relayed stay on cv02. Restart after freeing: RESUME=1 XB=<dir> bash c3x_relay.sh.
# Stop this guard: touch /home/noob/work/bench_c3_io/RELAYGUARD_C3X_STOP. Log: /home/noob/work/bench_c3_io/relayguard_c3x.log.
# For tests only: RR (relay root), FLOOR (GB), LOGD (folder of log and stop file), ONCE=1 (one pass, no sleep).
set -u
RR=${RR:-/home/noob/work/bench_relay}; FLOOR=${FLOOR:-15}; LOGD=${LOGD:-/home/noob/work/bench_c3_io}; ONCE=${ONCE:-0}
L=$LOGD/relayguard_c3x.log
echo "[$(date '+%F %T')] relay guard start pid $$ (floor $FLOOR GB on the filesystem of $RR; relays c3x)" >> $L
while [ ! -e $LOGD/RELAYGUARD_C3X_STOP ]; do
  a=$(df --output=avail -BG $RR | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt "$FLOOR" ]; then
    for r in c3x; do d=$RR/$r
      [ -d $d ] && [ ! -e $d/STOP ] && kill -0 "$(cat $d/relay.pid 2>/dev/null)" 2>/dev/null && touch $d/STOP && echo "[$(date '+%F %T')] STOP set for relay $r: free ${a} GB < $FLOOR" >> $L; done
  fi
  [ $ONCE = 1 ] && break
  sleep 300
done
echo "[$(date '+%F %T')] relay guard ends (stop file or ONCE)" >> $L
