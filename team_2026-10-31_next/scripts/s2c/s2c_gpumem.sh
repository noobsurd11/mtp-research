#!/bin/bash
# runner DRAFT (3 Nov 2026): GPU memory log on gaint for the SKR2C queue. Copy of s2q_gpumem.sh 084f6a42 with: queue dir
# /home/noob/work/s2c; 1 s samples always (team-lead 3 Nov: unattended overnight); stop 60 s after 'S2C ALL TRAINED' in s2c/launch.log,
# or the GPUMEM_STOP file, or MAXH hours (default 24); label regex = run_name / finllm only (no scorers tonight).
# v2 (judge G4): every nvidia-smi call has timeout 5 (a hung call yields an empty sample line, not a frozen logger).
# Line: "HH:MM:SS free_MiB used_MiB | pid:label:MiB ...". PID in /home/noob/work/s2c/gpumem.pid.
Q=/home/noob/work/s2c; mkdir -p $Q; L=$Q/gpumem.log; LL=$Q/launch.log; touch $LL
MAXH=${MAXH:-24}; T0=$(date +%s); END=0; N0=$(wc -l < $LL)
echo $$ > $Q/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (1 s); cols: time free_MiB used_MiB | pid:label:MiB" >> $L
RX='run_name=[A-Za-z0-9_]+|finllm_chat'
while :; do
  g=$(timeout 5 nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  a=$(timeout 5 nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
        lab=$(ps -o args= -p "$p" 2>/dev/null | grep -oE "$RX" | head -1); echo -n "$p:${lab:-other}:$m "; done)
  echo "$(date +%T) $g | $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -q "S2C ALL TRAINED"; then
    END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  [ -e $Q/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f $Q/gpumem.pid $Q/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  sleep 1
done
