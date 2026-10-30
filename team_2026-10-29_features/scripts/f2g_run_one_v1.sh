#!/bin/bash
# run_one.sh <run name> <seed> <free MiB gate> <extra opts...>: wait, train, rescore (rc captured before $(date))
set -u
cd /home/noob/work/el_f2
L=reports/f2g/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
name=$1; k=$2; gate=$3; shift 3
[ -e experiments/$name ] && { echo "[$(date)] skip $name (exists)" >> $L; exit 0; }
while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "$gate" ]; do sleep 60; done
echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts \
  seed=$k data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  "$@" run_name=$name > experiments/$name.stdout 2>&1
rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L
if [ $rc -eq 0 ]; then
  $P scripts/rescore_label_versions.py --runs $name --out reports/f2g/$name.json > experiments/$name.rescore.log 2>&1
  rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> $L
fi
