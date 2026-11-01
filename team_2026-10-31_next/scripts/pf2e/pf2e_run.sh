#!/bin/bash
# runner: PF2E launcher on gaint (protocol_PF2E v1 §6): CPU fp32, nice 19, 8 threads, CUDA hidden. MODE=gate (val only) or full.
set -u
cd /home/noob/work/el_f3/reports/pf2e
MODE=${1:?gate|full}; OUT=$([ "$MODE" = gate ] && echo out_gate || echo out)
E=/home/noob/work/el_f3/experiments
EG=$(for k in 5 6 7 8 9; do echo -n "$E/pf2_SUP_100pct_s$k "; done); EPF=$(for k in 5 6 7 8 9; do echo -n "$E/pf2_SUPPF_100pct_s$k "; done)
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
EXTRA=$([ "$MODE" = gate ] && echo --gate-only)
echo "[$(date '+%F %T')] pf2e $MODE start pid $$ (script md5 $(md5sum pf2e_infer.py | cut -c1-8))" >> run.log
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python pf2e_infer.py --code /home/noob/work/el_f3 --tm /home/noob/work/el_f3/reports/d \
  --out $OUT --eg $EG --epf $EPF --m0ref /home/noob/work/el_f3/reports/pf2/post/m0 --threads 8 $EXTRA >> run_$MODE.log 2>&1
rc=$?
echo "[$(date '+%F %T')] pf2e $MODE end rc=$rc" >> run.log
