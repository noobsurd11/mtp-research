#!/bin/bash
# Local watcher for PF2 on gaint (read-only ssh): exits (waking runner) on a new el_f3 reports/pf2/launch.log line that is a
# failure or milestone, a new Traceback in any pf2 run, GPU free < 2048 MiB on two polls in a row, gpumem logger gone, or MAXS s.
MAXS=${MAXS:-10800}; T0=$(date +%s); GA=noob@172.18.22.20
Q='cd /home/noob/work/el_f3; echo "N=$(wc -l < reports/pf2/launch.log)"; echo "TB=$(cat experiments/pf2_*.stdout 2>/dev/null | grep -c Traceback)"; echo "FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)"; echo "GM=$(kill -0 $(cat reports/pf2/gpumem.pid 2>/dev/null) 2>/dev/null && echo 1 || echo 0)"'
PAT='trained pf2_.* rc=[1-9]|post rc=[1-9]|FAIL|NOT scored|NOT READ|G6 |scoring done|ALL TRAINED|RN_STOP|deploy check|not starting'
S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null); eval "$(echo "$S" | grep -E '^(N|TB)=')"; N0=${N:-0}; TB0=${TB:-0}; LOW=0
echo "start $(date '+%H:%M') N=$N0 TB=$TB0 pid $$ MAXS $MAXS"
while :; do
  sleep 180
  S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null) || continue; [ -z "$S" ] && continue
  eval "$(echo "$S" | grep -E '^(N|TB|FREE|GM)=')"
  NEWL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "tail -n +$((N0+1)) /home/noob/work/el_f3/reports/pf2/launch.log" 2>/dev/null) || continue
  if echo "$NEWL" | grep -qE "$PAT"; then echo "EVENT $(date '+%H:%M'):"; echo "$NEWL" | cut -c1-400; exit 0; fi
  N0=$N
  [ "${TB:-0}" -gt "$TB0" ] && { echo "TRACEBACK $TB0 -> $TB $(date '+%H:%M')"; exit 0; }
  [ "${GM:-1}" = 0 ] && { echo "GPUMEM LOGGER GONE $(date '+%H:%M')"; exit 0; }
  if [ "${FREE:-99999}" -lt 2048 ]; then LOW=$((LOW+1)); else LOW=0; fi
  [ $LOW -ge 2 ] && { echo "LOW MEMORY: free $FREE MiB $(date '+%H:%M')"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M') free $FREE"; exit 0; }
done
