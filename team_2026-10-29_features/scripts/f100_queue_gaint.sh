#!/bin/bash
# protocol_100 launch queue on gaint (el_f3, deploy commit e544133). One ordered dispatcher (strict order, no skipping):
#   fine-tune waves by seed: SUP100-g sK, SUP100-PF sK, MIM100-PF sK for K = 0..4; then CP100 s0..s4.
# Each start: concurrency < MAXC, then the f3 gate (flock; free >= own peak + 2 GB: fine-tune 9,000 MiB, CP 11,600 MiB;
# >= 120 s after the previous start). Training only: no per-run rescoring (coach: score once, after all 20).
# Pause: touch reports/f100/HOLD (dispatch waits; running runs continue). Log: reports/f100/launch.log.
# Env: MAXC (default 3), VAL ("training.val_every=20000" if the val-off identity passed, else empty).
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
L=reports/f100/launch.log; mkdir -p reports/f100 experiments
MAXC=${MAXC:-3}; VAL=${VAL:-}
[ "$(cat REVISION)" = e544133 ] && [ "$(git rev-parse --short HEAD)" = e544133 ] && [ -z "$(git status --short --untracked-files=no)" ] \
  || { echo "[$(date)] deploy check FAIL (REVISION / HEAD / tracked changes)" >> $L; exit 1; }
B="data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
CPC="cp.lambda=1.0 cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.library_exclude=reports/f100/cp100_library_exclude.txt"
JOBS=()
for k in 0 1 2 3 4; do
  JOBS+=("f3_SUP_100pct_s$k|$k|9000|")
  JOBS+=("f3_SUPPF_100pct_s$k|$k|9000|$PF")
  JOBS+=("f3_MIMPF_100pct_s$k|$k|9000|$PF model.encoder_init=$ENC")
done
for k in 0 1 2 3 4; do JOBS+=("f3_CP_100pct_s$k|$k|11600|$CPC"); done
gate_wait(){ while :; do
  [ -e reports/f100/HOLD ] && { sleep 60; continue; }
  ok=$(flock reports/f100/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f100/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f100/last_start; echo 1; else echo 0; fi' _ "$1")
  [ "$ok" = 1 ] && break; sleep 30; done; }
PIDS=()
alive(){ n=0; for p in "${PIDS[@]}"; do kill -0 $p 2>/dev/null && n=$((n + 1)); done; echo $n; }
echo "[$(date)] queue start: ${#JOBS[@]} jobs, MAXC $MAXC, VAL '${VAL}', code $(cat REVISION)" >> $L
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k gate extra <<< "$j"
  if [ -e experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> $L; continue; fi
  while [ "$(alive)" -ge "$MAXC" ]; do sleep 30; done
  gate_wait $gate
  echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
  ( HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts seed=$k $B \
      $extra $VAL run_name=$name > experiments/$name.stdout 2>&1
    rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &  # rc captured before $(date) (a substitution resets $?)
  PIDS+=($!)
done
wait "${PIDS[@]}"
echo "[$(date)] ALL 20 TRAINED ($(grep -c 'trained f3_.* rc=0' $L) rc 0)" >> $L
