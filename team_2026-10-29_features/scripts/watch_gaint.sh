#!/bin/bash
# Local watcher (read-only ssh), exits to wake runner on: a new f1g/f2g launch.log line that is a failure or a milestone
# (rc!=0, FAIL, mismatch, STOP, INCOMPLETE, decoy go/no-go, F2-DDeP, post/AM rc, AFTER-RUNS DONE); a new Traceback in
# any f1/f2 run or check stdout; GPU free < 2048 MiB on two polls in a row (standing >= 2 GB rule); or MAXS seconds.
MAXS=${MAXS:-10800}; T0=$(date +%s); GA=noob@172.18.22.20
Q='cd /home/noob/work; A=el_f1/reports/f1g/launch.log; B=el_f2/reports/f2g/launch.log; echo "NA=$(wc -l < $A) NB=$(wc -l < $B)"; echo "TB=$(cat el_f1/experiments/f1_*_5pct_s*.stdout el_f2/experiments/f2_*.stdout el_f2/reports/f2/checks/*.stdout 2>/dev/null | grep -c Traceback)"; echo "FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)"'
get(){ ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "$Q" 2>/dev/null; }
S=$(get); eval "$(echo "$S" | tr ' ' '\n' | grep -E '^(NA|NB|TB)=')"; NA0=${NA:-0}; NB0=${NB:-0}; TB0=${TB:-0}; LOW=0
echo "start $(date '+%H:%M') NA=$NA0 NB=$NB0 TB=$TB0"
PAT='rc=[1-9]|FAIL|mismatch|STOP|INCOMPLETE|NO RESCORE|decoy go/no-go|F2-DDeP|E3b decoy final|AM rc|AFTER-RUNS DONE'
while :; do
  sleep 300
  S=$(get) || continue; [ -z "$S" ] && continue
  eval "$(echo "$S" | tr ' ' '\n' | grep -E '^(NA|NB|TB|FREE)=')"
  NEWL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $GA "tail -n +$((NA0+1)) /home/noob/work/el_f1/reports/f1g/launch.log; tail -n +$((NB0+1)) /home/noob/work/el_f2/reports/f2g/launch.log" 2>/dev/null) || continue
  if echo "$NEWL" | grep -qE "$PAT"; then echo "EVENT $(date '+%H:%M'):"; echo "$NEWL"; exit 0; fi
  NA0=$NA; NB0=$NB
  if [ "${TB:-0}" -gt "$TB0" ]; then echo "TRACEBACK count $TB0 -> $TB $(date '+%H:%M')"; exit 0; fi
  if [ "${FREE:-99999}" -lt 2048 ]; then LOW=$((LOW+1)); else LOW=0; fi
  [ $LOW -ge 2 ] && { echo "LOW MEMORY: free $FREE MiB on 2 polls $(date '+%H:%M')"; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M') (free $FREE MiB; new lines since start of this poll:)"; echo "$NEWL"; exit 0; }
done
