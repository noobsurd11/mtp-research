#!/bin/bash
# runner (1 Nov 2026): A8 / A8c memory + speed smokes for protocol_A8screen §9 (300 steps of the 4k screen schedule each).
# Code el_f8 c280e8c2 (checked: HEAD = REVISION_f8, 0 tracked changes). Opts = idea08_runspec §2c exactly, seed 0,
# + --exit_after_step 300 + training.checkpoint_every=300 (smoke only: writes latest.pth at 300 so peak_reserved is
# recorded; no effect on the training math). One job at a time; each start through the shared gate (gpu_gate.sh).
# Memory guard: if GPU free < 2,200 MiB on 2 consecutive 1 s samples, the guard stops ONLY this smoke's own python PID
# (recorded; its command line is printed to the log first) to protect finllm's 2 GB floor. rc captured before $(date).
# Usage: bash smoke_a8.sh A8 A8c   (env GATE default 14000: S estimate 8-11 GB/run + 2,048 + margin; no measured peak yet)
set -u
cd /home/noob/work/el_f8 || exit 1
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
source /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=/home/noob/work/runner_smk/a8; mkdir -p $O; L=$O/smoke.log
GATE=${GATE:-14000}
if [ "$(git rev-parse HEAD)" != "$(cat REVISION_f8)" ] || [ "$(git rev-parse --short=8 HEAD)" != c280e8c2 ] \
   || [ -n "$(git status --short --untracked-files=no)" ]; then
  echo "[$(date)] deploy check FAIL (HEAD != c280e8c2 / REVISION_f8 or tracked changes)" >> $L; exit 1; fi
printf '%s\n' "abf904631bf1ba23642e60c46b20dc5e  /home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors" \
  "fcc1480a11e933010f4d7e0ccb7e33b1  /home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth" | md5sum -c --quiet \
  || { echo "[$(date)] weights md5 FAIL" >> $L; exit 1; }
B="data.labeled_fraction=1.0 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.supervised=ce_dice"
S4="training.total_steps=4000 training.warmup_steps=200 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 training.val_every=4000"
A8="model.name=hrstem_unetpp model.backbone=convnext_tiny.dinov3_lvd1689m model.backbone_weights=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors model.backbone_weights_format=timm model.backbone_drop_path=0.0"
A8C="model.name=hrstem_unetpp model.backbone=convnext_tiny model.backbone_weights=/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth model.backbone_weights_format=torchvision_convnext model.backbone_drop_path=0.0"
SMK="training.checkpoint_every=300"
guard(){ local pid=$1 mem=$2 low=0 f
  while kill -0 "$pid" 2>/dev/null; do
    f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
    echo "$(date +%T) free $f | $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ')" >> "$mem"
    if [ "$f" -lt 2200 ]; then low=$((low+1)); else low=0; fi
    if [ $low -ge 2 ]; then
      echo "[$(date)] GUARD: free $f < 2200 twice; stopping own smoke PID $pid: $(ps -o args= -p "$pid" | cut -c1-200)" >> $L
      kill "$pid"; low=0; fi
    sleep 1; done; }
train(){ local n=$1 pid rc; shift
  gate_wait "$GATE" "a8-smoke $n"
  echo "[$(date)] start $n (gate $GATE)" >> $L
  $P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 300 --opts "$@" run_name=$n \
    > experiments/$n.stdout 2>&1 &
  pid=$!; echo "$pid $n $(date +%T)" >> $O/pids.txt
  guard $pid $O/$n.gpumem.txt
  wait $pid; rc=$?
  echo "[$(date)] trained $n rc=$rc (3 = planned exit at 300)" >> $L
  $P /home/noob/work/runner_smk/smoke_a8_parse.py experiments/$n $O/$n.gpumem.txt $pid >> $L 2>&1
}
for s in "$@"; do case $s in
  A8)  train f8_smk_A8_s0  seed=0 $B $S4 $A8 $SMK;;
  A8c) train f8_smk_A8c_s0 seed=0 $B $S4 $A8C $SMK;;
  *) echo "unknown smoke $s" >> $L;;
esac; done
echo "[$(date)] smokes done: $*" >> $L
