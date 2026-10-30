#!/bin/bash
# F1 / MIM5 on cv02 (run in tmux =f1ctl). Chained, never racing:
#  1) wait for a free GPU (< 1000 MiB used) among $GPUS, launch the MIM pretraining there (tmux =f1pre), wait until
#     that GPU holds memory;
#  2) A5c-f1 queue (reports/f1/f1a.spec, 3 runs per free GPU) via gpu_queue_f1.sh, session =f1a;
#  3) wait for experiments/f1_mim_pre_s0/encoder_final.md5 and check it;
#  4) MIM5 queue (reports/f1/f1b.spec) via gpu_queue_f1.sh, session =f1b.
# Pretraining arguments come from reports/f1/mim_args_cv02.txt (batch 64; frozen with the approved protocol v1).
set -u
GPUS="${GPUS:-0 1 2 3 4 5 6 7}"
cd /tmp/noob_el/el_f1
R=reports/f1; LOG=$R/orchestrate.log
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
PRE=experiments/f1_mim_pre_s0
MIMARGS=$(grep -v "^#" $R/mim_args_cv02.txt | tr '\n' ' ')
echo "[$(date)] orchestrate start; gpus $GPUS; mim args: $MIMARGS" >> $LOG
if [ ! -e $PRE ]; then
  G=""
  while [ -z "$G" ]; do
    for g in $GPUS; do
      u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g)
      if [ "$u" -lt 1000 ]; then G=$g; break; fi
    done
    [ -z "$G" ] && sleep 60
  done
  echo "[$(date)] pretrain on gpu $G ($u MiB)" >> $LOG
  tmux new-session -d -s f1pre -n pre "source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_f1; export CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=8; $PY -u scripts/pretrain_mim.py --list $R/mim_pool_v1.txt --monitor_list $R/mim_monitor_v1.txt --data_root data --out $PRE $MIMARGS > $PRE.stdout 2>&1; rc=\$?; echo \"[\$(date)] pretrain rc=\$rc\" >> $LOG; exec bash"
  for w in $(seq 1 60); do
    u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G); [ "$u" -ge 1000 ] && break; sleep 10
  done
  echo "[$(date)] pretrain gpu $G now $u MiB" >> $LOG
else
  echo "[$(date)] $PRE exists: pretraining not relaunched" >> $LOG
fi
bash /tmp/noob_el/el_f1/gpu_queue_f1.sh f1a $R/f1a.spec 3 $GPUS >> $LOG 2>&1
until [ -s $PRE/encoder_final.md5 ]; do sleep 120; done
(cd $PRE && md5sum -c encoder_final.md5) >> $LOG 2>&1 || { echo "[$(date)] encoder md5 check FAILED; stop" >> $LOG; exit 1; }
bash /tmp/noob_el/el_f1/gpu_queue_f1.sh f1b $R/f1b.spec 3 $GPUS >> $LOG 2>&1
echo "[$(date)] orchestration done (all runs launched)" >> $LOG
