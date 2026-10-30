#!/bin/bash
# Replacement dispatcher for the remaining protocol_100 smokes (the first dispatcher was stopped at 11:16:38 before b2/b3,
# coach URGENT: the CP100 library must also exclude the 6 train cells whose E-SCDD scuff px are crack in masks_escdd).
# Runs b2 (CP lambda 1, val 500, 2k), b3 (CP lambda 1, val off, 2k), d1 (expandable_segments, 1k) with
# cp.library_exclude = reports/f100/cp100_library_exclude.txt (7 D7 twins + 6 scuff stems). Same gates as the first
# dispatcher (fine-tune 9,000 / CP 11,600 MiB free, >= 90 s after the previous start). rc captured before $(date).
# At the end waits for every smoke training process (incl. b1, c1, c2 of the first dispatcher), then touches ALLDONE.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; L=$O/status.txt
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
CPC="cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.library_exclude=reports/f100/cp100_library_exclude.txt"
VOFF="training.val_every=20000"
LAST=$(date -d "$(grep 'start c2_mimpf' $L | sed -E 's/^\[([0-9:]+)\].*/\1/')" +%s)
PIDS=()
gate(){ while :; do f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  [ "$f" -ge "$1" ] && [ $(( $(date +%s) - LAST )) -ge 90 ] && break; sleep 20; done; LAST=$(date +%s); }
run(){ name=$1; g=$2; steps=$3; envx=$4; shift 4; gate $g; echo "[$(date +%T)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0))" >> $L
  ( env $envx $P -u scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step $steps --opts $B "$@" \
      run_name=$name logging.experiments_dir=$O > $O/$name.stdout 2>&1; rc=$?; echo "[$(date +%T)] $name rc=$rc (true rc)" >> $L ) & PIDS+=($!); }
echo "[$(date +%T)] dispatcher 2 start (library_exclude md5 $(md5sum < reports/f100/cp100_library_exclude.txt | cut -c1-8), $(wc -l < reports/f100/cp100_library_exclude.txt) stems)" >> $L
run b2_cp_v500 11600 2000 X=0 cp.lambda=1.0 $CPC
run b3_cp_voff 11600 2000 X=0 cp.lambda=1.0 $CPC $VOFF
run d1_nosw_expseg 9000 1000 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
wait "${PIDS[@]}"
while pgrep -f "run_name=(b1_nosw_voff|c1_suppf|c2_mimpf) logging.experiments_dir=$O" > /dev/null; do sleep 30; done
touch $O/ALLDONE; echo "[$(date +%T)] ALLDONE" >> $L
