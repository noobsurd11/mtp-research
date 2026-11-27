#!/bin/bash
# cv02 GPU memory log for cq.sh = b6_cv02_gpumem.sh (B6, 1 Nov) with the elbench labels. All 8 GPUs every INTERVAL s (default 2).
# Line: "HH:MM:SS | g<i> used/free ... | pid:gpu:MiB:<job name>|other:<user> ...". A job name = the run_name= / --bench-run
# token of a live PID in Q/pids (or its child). Every nvidia-smi under timeout 10.
# Stops 60 s after "BENCH CV02 Q ALL DONE" in Q/launch.log, on Q/GPUMEM_STOP, or after MAXH (168) h. PID in Q/gpumem.pid.
Q=${Q:?queue dir}; mkdir -p $Q; L=$Q/gpumem.log; SL=$Q/launch.log; touch $SL
MAXH=${MAXH:-168}; INTERVAL=${INTERVAL:-2}; T0=$(date +%s); END=0; N0=$(wc -l < $SL); echo $$ > $Q/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (${INTERVAL} s); cols: time | g<i> used/free | pid:gpu:MiB:job|other:user" >> $L
declare -A IDX; while IFS=, read -r i u; do IDX[$(echo $u | tr -d ' ')]=$(echo $i | tr -d ' '); done < <(timeout 10 nvidia-smi --query-gpu=index,uuid --format=csv,noheader)
RX='run_name=[A-Za-z0-9_.-]+|--bench-run [A-Za-z0-9_.-]+'
while :; do
  o=" $(for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; p=$(tr -dc 0-9 < $f); [ -n "$p" ] || continue; echo $p; ps -o pid= --ppid $p 2>/dev/null | tr -d ' '; done | tr '\n' ' ') "
  g=$(timeout 10 nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader,nounits | tr -d ' ' | awk -F, '{printf "g%s %s/%s ", $1, $2, $3}')
  a=$(timeout 10 nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r u p m; do
        case "$o" in *" $p "*) w=$(ps -o args= -p $p 2>/dev/null | grep -oE "$RX" | head -1 | sed 's/^run_name=//; s/^--bench-run //'); w=${w:-ours};;
          *) w="other:$(ps -o user= -p $p 2>/dev/null | tr -d ' ')";; esac; echo -n "$p:${IDX[$u]}:$m:$w "; done)
  echo "$(date +%T) | $g| $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $SL | grep -q "BENCH CV02 Q ALL DONE"; then END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  [ -e $Q/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f $Q/gpumem.pid $Q/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  sleep $INTERVAL
done
