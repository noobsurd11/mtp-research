#!/bin/bash
# runner: SKR2C verdict D launcher on gaint (protocol_SKR2C §3b, §6) = skr2e_run.sh b2816cb3 with the SKR2C arms / refs; CPU fp32,
# nice 19, 8 threads, CUDA hidden. MODE=idcheck (ruling 5: val-only identity on the OPENED s5-9 members vs #6; --val-only) or full (the
# opening, fresh s10-14, after R ends rc 0). Logs / PIDs go OUTSIDE the frozen open/ dir: full -> /home/noob/work/s2c/d_{run.log,full.log,
# run_full.pid,py_full.pid}, out /home/noob/work/s2c/d_out; idcheck -> /home/noob/work/s2c/open_check/d_*, out open_check/d_val_identity.
# Own PID -> run_<MODE>.pid; python PID -> py_<MODE>.pid. rc captured before $(date).
set -u
MODE=${1:?idcheck|full}
O=/home/noob/work/s2c/open; E=/home/noob/work/el_f3/experiments; ET=/home/noob/work/el_thin/experiments
case "$MODE" in
  full) L=/home/noob/work/s2c; OUT=$L/d_out; EXTRA=""
        ESU=$(for k in 10 11 12 13 14; do echo -n "$E/s2c_SUPPF_100pct_s$k "; done); ESK=$(for k in 10 11 12 13 14; do echo -n "$ET/s2c_SKR01_100pct_s$k "; done)
        MS=/home/noob/work/s2c/post/m0/SUPPF; MK=/home/noob/work/s2c/post/m0/SKR01;;
  idcheck) L=/home/noob/work/s2c/open_check; OUT=$L/d_val_identity; EXTRA="--val-only --id-ref /home/noob/work/el_f3/reports/skr2e/out"
        ESU=$(for k in 5 6 7 8 9; do echo -n "$E/pf2_SUPPF_100pct_s$k "; done); ESK=$(for k in 5 6 7 8 9; do echo -n "$ET/skr2_SKR01_100pct_s$k "; done)
        MS=/home/noob/work/el_f3/reports/pf2/post/m0; MK=/home/noob/work/s2q/post/m0/SKR01;;
  *) echo "MODE must be idcheck or full" >&2; exit 2;;
esac
[ ! -e $OUT ] || { echo "refused: $OUT exists" >&2; exit 2; }
mkdir -p $L
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1
echo $$ > $L/d_run_$MODE.pid
echo "[$(date '+%F %T')] s2c D $MODE start pid $$ (script md5 $(md5sum $O/d/s2c_d_infer.py | cut -c1-8))" >> $L/d_run.log
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python $O/d/s2c_d_infer.py --code /home/noob/work/el_f3 --tm /home/noob/work/el_f3/reports/d \
  --out $OUT --esup $ESU --eskr $ESK --m0ref-sup $MS --m0ref-skr $MK --threads 8 $EXTRA >> $L/d_$MODE.log 2>&1 &
py=$!; echo $py > $L/d_py_$MODE.pid; wait $py
rc=$?
echo "[$(date '+%F %T')] s2c D $MODE end rc=$rc" >> $L/d_run.log
exit $rc
