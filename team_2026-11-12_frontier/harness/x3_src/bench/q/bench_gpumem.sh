#!/bin/bash
# elbench GPU memory log = s2c_gpumem.sh 06791cdd with: queue dir from Q; label regex run_name= / --bench-run / finllm; end line
# "BENCH Q ALL DONE". 1 s samples; every nvidia-smi under timeout 5. Line: "HH:MM:SS free used | pid:label:MiB ...".
# Stops 60 s after the end line, on Q/GPUMEM_STOP, or after MAXH (24) h. PID in Q/gpumem.pid. FAKE (env): no nvidia-smi (dry tests).
Q=${Q:?queue dir}; mkdir -p $Q; L=$Q/gpumem.log; LL=$Q/launch.log; touch $LL
MAXH=${MAXH:-24}; T0=$(date +%s); END=0; N0=$(wc -l < $LL)
echo $$ > $Q/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (1 s); cols: time free_MiB used_MiB | pid:label:MiB" >> $L
RX='run_name=[A-Za-z0-9_.-]+|--bench-run [A-Za-z0-9_.-]+|finllm_chat'
while :; do
  if [ -n "${FAKE:-}" ]; then g="fake"; a=""; else
  g=$(timeout 5 nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  a=$(timeout 5 nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
        lab=$(ps -o args= -p "$p" 2>/dev/null | grep -oE "$RX" | head -1 | tr ' ' '='); echo -n "$p:${lab:-other}:$m "; done); fi
  echo "$(date +%T) $g | $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -q "BENCH Q ALL DONE"; then
    END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  [ -e $Q/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f $Q/gpumem.pid $Q/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  sleep 1
done
