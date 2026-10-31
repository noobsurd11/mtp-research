#!/bin/bash
# Local watcher for protocol_100 on gaint (read-only ssh): wakes runner on a new el_f3 reports/f100/launch.log line that is a
# failure or milestone, a new Traceback in any f3 run, GPU free < 2048 MiB on two polls in a row, or MAXS seconds.
MAXS=${MAXS:-10800}; T0=$(date +%s); GA=noob@172.18.22.20
Q='cd /home/noob/work/el_f3; echo "N=$(wc -l < reports/f100/launch.log)"; echo "TB=$(cat experiments/f3_*.stdout 2>/dev/null | grep -c Traceback)"; echo "FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)"'
PAT='trained f3_.* rc=[1-9]|post rc=[1-9]|FAIL|NOT scored|gate 6b \(coach|scoring done|ALL 20 TRAINED|CP_STOP|not run'
S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null); eval "$(echo "$S" | grep -E '^(N|TB)=')"; N0=${N:-0}; TB0=${TB:-0}; LOW=0
echo "start $(date '+%H:%M') N=$N0 TB=$TB0 pid $$ MAXS $MAXS"
while :; do
  sleep 180
  S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null) || continue; [ -z "$S" ] && continue
  eval "$(echo "$S" | grep -E '^(N|TB|FREE)=')"
  NEWL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "tail -n +$((N0+1)) /home/noob/work/el_f3/reports/f100/launch.log" 2>/dev/null) || continue
  if echo "$NEWL" | grep -qE "$PAT"; then echo "EVENT $(date '+%H:%M'):"; echo "$NEWL"; exit 0; fi
  N0=$N
  [ "${TB:-0}" -gt "$TB0" ] && { echo "TRACEBACK $TB0 -> $TB $(date '+%H:%M')"; exit 0; }
  if [ "${FREE:-99999}" -lt 2048 ]; then LOW=$((LOW+1)); else LOW=0; fi
  [ $LOW -ge 2 ] && { echo "LOW MEMORY: free $FREE MiB $(date '+%H:%M')"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M') free $FREE"; exit 0; }
done
