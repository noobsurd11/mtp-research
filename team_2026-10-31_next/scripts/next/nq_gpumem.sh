#!/bin/bash
# runner (1 Nov 2026): GPU memory log on gaint for the HC + A8 queue (copy of thin_gpumem.sh 83feb47d; paths, labels and end lines
# changed). 1 s samples while a scoring process is on the GPU or /home/noob/work/gpu_gate/FAST exists; 10 s otherwise.
# Line: "HH:MM:SS free_MiB used_MiB | pid:label:MiB ...". Stops 60 s after an end line in /home/noob/work/nq/post.log
# ("nq scoring done" / "nq NOT scored"), or the GPUMEM_STOP file, or MAXH hours. PID in /home/noob/work/nq/gpumem.pid.
Q=/home/noob/work/nq; mkdir -p $Q; L=$Q/gpumem.log; LL=$Q/post.log; touch $LL
MAXH=${MAXH:-72}; T0=$(date +%s); END=0; N0=$(wc -l < $LL); GG=/home/noob/work/gpu_gate
echo $$ > $Q/gpumem.pid
echo "# start $(date '+%F %T') pid $$ (10 s; 1 s while scoring or FAST); cols: time free_MiB used_MiB | pid:label:MiB" >> $L
RX='run_name=[A-Za-z0-9_]+|rescore_label_versions|m0_audit_b3|m0_audit_tau|m0_audit|rescore_logit_adjust|scuff_train_iou|calib_dump|enc_cosine|pf2e_infer|finllm_chat'
SC=':(rescore_label_versions|m0_audit_b3|m0_audit_tau|m0_audit|rescore_logit_adjust|scuff_train_iou|calib_dump|enc_cosine):'
while :; do
  g=$(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  a=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
        lab=$(ps -o args= -p "$p" 2>/dev/null | grep -oE "$RX" | head -1); echo -n "$p:${lab:-other}:$m "; done)
  echo "$(date +%T) $g | $a" >> $L
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -qE "nq scoring done|nq NOT scored"; then
    END=$(date +%s); echo "# end line seen $(date '+%F %T'); stopping in 60 s" >> $L; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { echo "# stop $(date '+%F %T')" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  [ -e $Q/GPUMEM_STOP ] && { echo "# stop $(date '+%F %T') (GPUMEM_STOP)" >> $L; rm -f $Q/gpumem.pid $Q/GPUMEM_STOP; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { echo "# stop $(date '+%F %T') (MAXH ${MAXH} h)" >> $L; rm -f $Q/gpumem.pid; exit 0; }
  if [ -e $GG/FAST ] || echo "$a" | grep -qE "$SC"; then sleep 1; else sleep 10; fi
done
