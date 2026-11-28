#!/bin/bash
# Task 4 runner (gaint CPU, nice 19): ext sweep + cross-fit -> derived dumps -> read_x4 (COMBO vs EXT, seeds 5, 6; PFAA for M).
set -u
H=/home/yugma/mtp/research/team_2026-11-27_arch/cpu; X=/home/yugma/mtp/research/team_2026-11-27_arch/harness/x4
P=/home/noob/work/el-fault-detection/.venv/bin/python; O=/home/noob/work/bench_reads/x4_cpu
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1
. $X/x4_arms.sh
cd $H
echo "[$(date "+%F %T")] ext start"
nice -n 19 $P ext.py sweep --seeds 5,6 --workers 8; rc=$?; echo "[$(date "+%F %T")] sweep rc=$rc"; [ $rc = 0 ] || exit $rc
nice -n 19 $P ext.py write --seeds 5,6 --workers 8; rc=$?; echo "[$(date "+%F %T")] write rc=$rc"; [ $rc = 0 ] || exit $rc
EXT_T="$O/ext/dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}.swad.ext"
nice -n 19 $P $X/read_x4.py --out $O/read_ext --base COMBO --cache $O/cache \
  --arm "COMBO=$COMBO_T:5,6:swad" --arm "EXT=$EXT_T:5,6:swad" --arm "PFAA=$PF_T:5,6,7,8:model" \
  --pair COMBO=EXT --aa PFAA:5,6:7,8 --verdict EXT; rc=$?
echo "[$(date "+%F %T")] read rc=$rc"
echo "[$(date "+%F %T")] EXT ALL DONE rc=$rc"
