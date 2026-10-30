#!/bin/bash
# run_one.sh <run name> <seed> <extra opts...>: wait for >= 7,000 MiB free, train, rescore
set -u
cd /home/noob/work/el_f1
S=f1g; L=reports/$S/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
name=$1; k=$2; shift 2
[ -e experiments/$name ] && { echo "[$(date)] skip $name (exists)" >> $L; exit 0; }
case "$name" in f1_A_*) while [ -e reports/$S/HOLD_A ]; do sleep 60; done;; esac  # runner 18:37: A-lane-only hold (f2 checks take the A slot); MIM5 never held
while :; do
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  [ "$free" -ge 9000 ] && break; sleep 60  # team-lead 13:3x: own peak (6.8 GB) + 2 GB free
done
echo "[$(date)] start $name (free $free MiB)" >> $L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts \
  seed=$k data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  "$@" run_name=$name > experiments/$name.stdout 2>&1
rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L
if [ $rc -eq 0 ]; then
  $P scripts/rescore_label_versions.py --runs $name --out reports/$S/$name.json > experiments/$name.rescore.log 2>&1
  rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> $L
fi
