#!/bin/bash
# gaint relay guard (c3swad, review F5, 17 Nov 2026), modelled on diskguard3.sh. Run by the LEAD on gaint in tmux, started
# beside the third relay:  tmux new-session -d -s bench_relayguard "bash <this file>"
# Every 300 s it reads the free space of the filesystem that holds the relay dirs (gaint has one filesystem, / ).
# Below 15 GB free it touches STOP in the relay dir of every relay that is alive (relay.pid names a live process) among
# c3base, c3hrnet, rows2 and c3swad, and logs it. It does nothing else: it starts nothing, signals nothing, deletes
# nothing, and never touches cv02.
# What STOP does (relay_w1c.sh 74a2ec3d, the script of all four relays, l.38): the relay ends at the top of its next
# poll pass (every 300 s). Runs already listed in the running pass are still pulled (about 1 GB each), so stop early
# enough: hence 15 GB. Nothing is lost: runs not relayed stay on cv02. After space is freed the lead removes STOP and
# starts the relay again on the same dir (c3swad: RESUME=1 bash c3swad_relay.sh; a relay skips runs that have .ok).
# Stop this guard: touch /home/noob/work/bench_c3_io/RELAYGUARD_STOP. Log: /home/noob/work/bench_c3_io/relayguard.log.
# For tests only: RR (relay root), FLOOR (GB), LOGD (folder of log and stop file), ONCE=1 (one pass, no sleep).
set -u
RR=${RR:-/home/noob/work/bench_relay}; FLOOR=${FLOOR:-15}; LOGD=${LOGD:-/home/noob/work/bench_c3_io}; ONCE=${ONCE:-0}
L=$LOGD/relayguard.log
echo "[$(date '+%F %T')] relay guard start pid $$ (floor $FLOOR GB on the filesystem of $RR; relays c3base c3hrnet rows2 c3swad)" >> $L
while [ ! -e $LOGD/RELAYGUARD_STOP ]; do
  a=$(df --output=avail -BG $RR | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt "$FLOOR" ]; then
    for r in c3base c3hrnet rows2 c3swad; do d=$RR/$r
      [ -d $d ] && [ ! -e $d/STOP ] && kill -0 "$(cat $d/relay.pid 2>/dev/null)" 2>/dev/null && touch $d/STOP && echo "[$(date '+%F %T')] STOP set for relay $r: free ${a} GB < $FLOOR" >> $L; done
  fi
  [ $ONCE = 1 ] && break
  sleep 300
done
echo "[$(date '+%F %T')] relay guard ends (stop file or ONCE)" >> $L
