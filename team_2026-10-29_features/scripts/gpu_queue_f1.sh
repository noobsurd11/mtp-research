#!/bin/bash
# F1 queue (copy of gpu_queue_sk1.sh for /tmp/noob_el/el_f1). Usage: gpu_queue_f1.sh <session> <spec> <per-gpu> <gpu ...>
# Spec lines as launch_set_f1.sh with gpu field "-". A GPU takes runs only when its used memory is < 1000 MiB (so never
# onto a GPU another user holds, far below the 4 GB rule); it then gets <per-gpu> runs at once. Polls every 60 s.
# A GPU is not removed after use: once our runs on it finish it is free again and takes the next batch. After a launch
# the queue waits until that GPU shows >= 1000 MiB (max 300 s) so it is not counted free twice.
# Training is deterministic per machine: packing changes speed only.
S=$1; SPEC=$2; K=$3; shift 3; GPUS="$@"
cd /tmp/noob_el/el_f1; mkdir -p reports/$S
mapfile -t Q < <(grep -v '^\s*#' "$SPEC" | grep -v '^\s*$')
i=0
while [ $i -lt ${#Q[@]} ]; do
  for g in $GPUS; do
    [ $i -ge ${#Q[@]} ] && break
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
    if [ "$used" -lt 1000 ]; then
      QS=reports/$S/queue_g${g}_i$i.spec; : > $QS
      for k in $(seq 1 $K); do [ $i -lt ${#Q[@]} ] && { echo "${Q[$i]}" | awk -v g=$g '{$2=g; print}' >> $QS; i=$((i+1)); }; done
      echo "[$(date)] gpu $g free ($used MiB): launching $(wc -l < $QS) runs ($QS)"
      bash /tmp/noob_el/el_f1/launch_set_f1.sh $S $QS
      for w in $(seq 1 30); do
        u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g); [ "$u" -ge 1000 ] && break; sleep 10
      done
    fi
  done
  [ $i -lt ${#Q[@]} ] && sleep 60
done
echo "[$(date)] queue empty"
