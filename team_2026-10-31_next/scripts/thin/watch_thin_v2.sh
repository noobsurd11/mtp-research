#!/bin/bash
# v2 (1 Nov 19:06, team rule: never cat / tail a training .stdout): Traceback count via grep -ho | wc -l, no cat.
# Local watcher for THIN-B3 on gaint (copy of watch_pf2.sh c918d27b; read-only ssh): exits on a new el_thin reports/thin/q/launch.log line that is a
# failure or milestone, a new Traceback in any thin run, GPU free < 2048 MiB on two polls in a row, gpumem logger gone, or MAXS s.
MAXS=${MAXS:-10800}; T0=$(date +%s); GA=noob@172.18.22.20
Q='cd /home/noob/work/el_thin; echo "N=$(wc -l < reports/thin/q/launch.log)"; echo "TB=$(grep -ho Traceback experiments/thin_[SCB]*_100pct_s*.stdout 2>/dev/null | wc -l)"; echo "FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)"; echo "GM=$(kill -0 $(cat reports/thin/q/gpumem.pid 2>/dev/null) 2>/dev/null && echo 1 || echo 0)"'
PAT='trained thin_.* rc=[1-9]|post rc=[1-9]|FAIL|NOT scored|scoring done|ALL TRAINED|deploy check|not starting|dispatching|HOLD'
S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null); eval "$(echo "$S" | grep -E '^(N|TB)=')"; N0=${N:-0}; TB0=${TB:-0}; LOW=0
echo "start $(date '+%H:%M') N=$N0 TB=$TB0 pid $$ MAXS $MAXS"
while :; do
  sleep 180
  S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null) || continue; [ -z "$S" ] && continue
  eval "$(echo "$S" | grep -E '^(N|TB|FREE|GM)=')"
  NEWL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "tail -n +$((N0+1)) /home/noob/work/el_thin/reports/thin/q/launch.log" 2>/dev/null) || continue
  if echo "$NEWL" | grep -qE "$PAT"; then echo "EVENT $(date '+%H:%M'):"; echo "$NEWL" | cut -c1-400; exit 0; fi
  N0=$N
  [ "${TB:-0}" -gt "$TB0" ] && { echo "TRACEBACK $TB0 -> $TB $(date '+%H:%M')"; exit 0; }
  [ "${GM:-1}" = 0 ] && { echo "GPUMEM LOGGER GONE $(date '+%H:%M')"; exit 0; }
  if [ "${FREE:-99999}" -lt 2048 ]; then LOW=$((LOW+1)); else LOW=0; fi
  [ $LOW -ge 2 ] && { echo "LOW MEMORY: free $FREE MiB $(date '+%H:%M')"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M') free $FREE"; exit 0; }
done
