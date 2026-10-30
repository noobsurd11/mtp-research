#!/bin/bash
# DDeP pretraining on cv02 (team-lead amendment: pretraining may run on any free GPU). tmux =f2ddep, deployment
# /tmp/noob_el/el_f2 (REVISION 2751aa8). Waits for a GPU with < 1,000 MiB used (never one another user holds),
# runs the 500-step smoke (protocol_ddep5 v1) with an automatic gate (finite, step-500 loss < 1.0, monitor at 500 below
# step 0) and a data gate (pool image-bytes manifest md5 = gaint's, REVISION 2751aa8), then the full run with the protocol's arguments into experiments/f2_ddep_pre_s0. Log: reports/f2/ddep_cv02.log.
# Not started if a STOP file exists (runner may move the run to gaint instead): reports/f2/DDEP_CV02_STOP.
set -u
cd /tmp/noob_el/el_f2
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
R=reports/f2; LOG=$R/ddep_cv02.log
GPUS="${GPUS:-0 1 2 3 4 5 6 7}"
ARGS="--list $R/mim_pool_v11.txt --monitor_list $R/mim_monitor_v11.txt --data_root data --steps 40000 --batch 32 --crop 256 --gamma 0.95 --lr 1e-4 --warmup_steps 500 --clip 1.0 --log_every 50 --ckpt_every 1000 --monitor_every 2000 --seed 0"
echo "[$(date)] waiting for a free GPU among $GPUS" >> $LOG
G=""
while [ -z "$G" ]; do
  [ -e $R/DDEP_CV02_STOP ] && { echo "[$(date)] STOP file: exit" >> $LOG; exit 0; }
  for g in $GPUS; do
    u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
    if [ "$u" -lt 1000 ]; then G=$g; break; fi
  done
  [ -z "$G" ] && sleep 120
done
source /tmp/noob_el/env.sh
export CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=8
if grep -q "STOPPED at step 500/40000" $R/ddep_smoke_cv02.stdout 2>/dev/null; then
  echo "[$(date)] gpu $G free ($u MiB): smoke already done (reused, gate re-evaluated)" >> $LOG
else
  echo "[$(date)] gpu $G free ($u MiB): smoke" >> $LOG
  $PY -u scripts/pretrain_ddep.py $ARGS --out $R/ddep_smoke_cv02 --max_steps 500 --monitor_every 250 > $R/ddep_smoke_cv02.stdout 2>&1
  echo "[$(date)] smoke rc=$?" >> $LOG
fi
# v2 (16:3x IST): match only the step line ("step 500/40000 ep"); v1 also matched the STOPPED line and failed to parse
l500=$(grep -E "step 500/40000 ep" $R/ddep_smoke_cv02.stdout | sed -E 's/.*loss=([0-9.naife]+).*/\1/')
m0=$(grep "monitor step 0 loss" $R/ddep_smoke_cv02.stdout | sed -E 's/.*loss=([0-9.]+).*/\1/')
m500=$(grep "monitor step 500 loss" $R/ddep_smoke_cv02.stdout | sed -E 's/.*loss=([0-9.]+).*/\1/')
grep -E "step (50|250|500)/|monitor|DDeP:|samples" $R/ddep_smoke_cv02.stdout | tail -6 >> $LOG
ok=$(python3 -c "import math; l=float('$l500' or 'nan'); a=float('$m0' or 'nan'); b=float('$m500' or 'nan'); print(int(math.isfinite(l) and l < 1.0 and math.isfinite(b) and b < a))")
echo "[$(date)] smoke gate: loss500 $l500 monitor0 $m0 monitor500 $m500 -> $([ "$ok" = 1 ] && echo PASS || echo FAIL)" >> $LOG
[ "$ok" = 1 ] || exit 1
# coach gate: image-bytes manifest of the pool on cv02 must equal gaint's (855daabd...), and the deployment is 2751aa8
man=$(md5sum < $R/ddep_smoke_cv02/pool_files.md5 | cut -c1-32)
rev=$(cat REVISION)
echo "[$(date)] data gate: pool image-bytes manifest $man (gaint 855daabd3ce2899c8f423a384e71ce23), REVISION $rev" >> $LOG
[ "$man" = 855daabd3ce2899c8f423a384e71ce23 ] && [ "$rev" = 2751aa8 ] || { echo "[$(date)] data gate FAIL: abort" >> $LOG; exit 1; }
[ -e $R/DDEP_CV02_STOP ] && { echo "[$(date)] STOP file after smoke: exit" >> $LOG; exit 0; }
echo "[$(date)] full DDeP pretraining on gpu $G" >> $LOG
$PY -u scripts/pretrain_ddep.py $ARGS --out experiments/f2_ddep_pre_s0 > experiments/f2_ddep_pre_s0.stdout 2>&1
echo "[$(date)] ddep rc=$?" >> $LOG
cat experiments/f2_ddep_pre_s0/decoder_final.md5 >> $LOG 2>&1
