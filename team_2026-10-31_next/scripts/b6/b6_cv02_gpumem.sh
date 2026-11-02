#!/bin/bash
# runner DRAFT (1 Nov 2026): GPU memory log on cv02 for B6, all 8 GPUs, every 10 s (1 s while the FAST file exists).
# Line: "HH:MM:SS | g<i> used/free | ... | pid:gpu:MiB:ours|other ...". "ours" = a pid in B/q/pids or B/q/score_pids.
# Stops on GPUMEM_STOP, or 60 s after "B6 ALL TRAINED" in B/q/launch.log (scoring is on gaint, coach 23:4x), or MAXH h.
# PID in B/q/gpumem.pid (gone when stopped; b6_relay.sh waits for that).
B=${B:-/tmp/noob_el/el_b6}; Q=$B/q; mkdir -p $Q; L=$Q/gpumem.log; SL=$Q/launch.log; touch $SL
MAXH=${MAXH:-48}; T0=$(date +%s); END=0; echo $$ > $Q/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (10 s; 1 s while FAST)" >> $L
declare -A IDX; while IFS=, read -r i u; do IDX[$(echo $u | tr -d ' ')]=$(echo $i | tr -d ' '); done < <(nvidia-smi --query-gpu=index,uuid --format=csv,noheader)
while :; do
  o=" $(for p in $(cat $Q/pids/*.pid $Q/score_pids/*.pid 2>/dev/null); do echo $p; ps -o pid= --ppid $p 2>/dev/null | tr -d ' '; done | tr '\n' ' ') "  # v2: + children (recorded pid = subshell)
  g=$(nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader,nounits | tr -d ' ' | awk -F, '{printf "g%s %s/%s ", $1, $2, $3}')
  a=$(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r u p m; do
        case "$o" in *" $p "*) w=ours;; *) w=other;; esac; echo -n "$p:${IDX[$u]}:$m:$w "; done)
  echo "$(date +%T) | $g| $a" >> $L
  [ $END = 0 ] && grep -q "B6 ALL TRAINED" $SL && { END=$(date +%s); echo "# end line seen $(date '+%F %T')" >> $L; }
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  [ -e $Q/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f $Q/gpumem.pid $Q/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH)" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  if [ -e $Q/FAST ]; then sleep 1; else sleep 10; fi
done
