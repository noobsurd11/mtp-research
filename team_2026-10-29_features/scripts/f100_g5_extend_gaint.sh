#!/bin/bash
# protocol_100 v1 G5 (coach review_100_v1.md): extend the PF smokes c1 (SUP100-PF) and c2 (MIM100-PF) from 2,000 to 4,000
# steps by --resume (bit-identical continuation from latest.pth), keeping the 2k checkpoint as latest_2k.pth.
# Starts only after the smoke script's last start (d1) and after c1/c2 ended at 2k; gate 9,000 MiB free, 90 s apart.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; L=$O/status.txt
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
until grep -q "start d1_nosw_expseg" $L && grep -q "c1_suppf rc=" $L && grep -q "c2_mimpf rc=" $L; do sleep 30; done
LAST=0; PIDS=()
for n in c1_suppf c2_mimpf; do
  grep -q "exit_after_step=2000 reached" $O/$n.stdout || { echo "[$(date +%T)] G5: $n did not reach its 2k exit: no extension" >> $L; continue; }
  cp -p $O/$n/checkpoints/latest.pth $O/$n/checkpoints/latest_2k.pth
  extra=$PF; [ $n = c2_mimpf ] && extra="$PF model.encoder_init=$ENC"
  while :; do f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
    [ "$f" -ge 9000 ] && [ $(( $(date +%s) - LAST )) -ge 90 ] && break; sleep 20; done; LAST=$(date +%s)
  echo "[$(date +%T)] G5: resume $n 2k -> 4k (free $f)" >> $L
  ( $P -u scripts/train.py --config configs/supervised.yaml --resume --exit_after_step 4000 --opts $B $extra \
      run_name=$n logging.experiments_dir=$O > $O/${n}_4k.stdout 2>&1; rc=$?; echo "[$(date +%T)] G5: $n 4k rc=$rc" >> $L ) &
  PIDS+=($!)
done
wait "${PIDS[@]}"
touch $O/G5DONE; echo "[$(date +%T)] G5DONE" >> $L
