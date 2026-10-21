#!/bin/bash
# SK1 queue (copy of gpu_queue.sh for /tmp/noob_el/el_sk1). Usage: gpu_queue_sk1.sh <session> <spec> <per-gpu> <gpu ...>
# Spec lines as launch_set_sk1.sh with gpu field "-". A GPU takes runs only when its used memory is < 1000 MiB (so never
# onto a GPU another user has taken); it then gets <per-gpu> runs at once. Training is deterministic per machine:
# packing changes speed only.
S=$1; SPEC=$2; K=$3; shift 3; GPUS="$@"
cd /tmp/noob_el/el_sk1; mkdir -p reports/$S
mapfile -t Q < <(grep -v '^\s*#' "$SPEC" | grep -v '^\s*$')
i=0
while [ $i -lt ${#Q[@]} ]; do
  for g in $GPUS; do
    [ $i -ge ${#Q[@]} ] && break
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
    if [ "$used" -lt 1000 ]; then
      : > reports/$S/queue_g$g.spec
      for k in $(seq 1 $K); do [ $i -lt ${#Q[@]} ] && { echo "${Q[$i]}" | awk -v g=$g '{$2=g; print}' >> reports/$S/queue_g$g.spec; i=$((i+1)); }; done
      echo "[$(date)] gpu $g free ($used MiB): launching $(wc -l < reports/$S/queue_g$g.spec) runs"
      bash /tmp/noob_el/el_sk1/launch_set_sk1.sh $S reports/$S/queue_g$g.spec
      GPUS=$(echo $GPUS | tr ' ' '\n' | grep -vx $g | tr '\n' ' ')
    fi
  done
  [ $i -lt ${#Q[@]} ] && sleep 60
done
echo "[$(date)] queue empty"
