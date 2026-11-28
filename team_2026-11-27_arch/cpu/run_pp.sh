#!/bin/bash
# Task 1 runner (gaint CPU, nice 19): sweep + cross-fit choice -> derived dumps -> read_x4 (COMBO vs PPCC, seeds 5, 6; PFAA for M).
set -u
H=/home/yugma/mtp/research/team_2026-11-27_arch/cpu; X=/home/yugma/mtp/research/team_2026-11-27_arch/harness/x4
P=/home/noob/work/el-fault-detection/.venv/bin/python; O=/home/noob/work/bench_reads/x4_cpu
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1
. $X/x4_arms.sh
cd $H
echo "[$(date "+%F %T")] pp start"
nice -n 19 $P pp_sweep.py --seeds 5,6 --workers 8; rc=$?; echo "[$(date "+%F %T")] sweep rc=$rc"; [ $rc = 0 ] || exit $rc
nice -n 19 $P pp_write.py --seeds 5,6 --workers 8; rc=$?; echo "[$(date "+%F %T")] write rc=$rc"; [ $rc = 0 ] || exit $rc
PP_T="$O/pp_dumps/elbench1/hrnet_w18_unetpp_swad_const_pf_v11/c3x_hrnet_swad_v11_f{k}_s{s}.swad.ppcc"
nice -n 19 $P $X/read_x4.py --out $O/read_pp --base COMBO --cache $O/cache \
  --arm "COMBO=$COMBO_T:5,6:swad" --arm "PPCC=$PP_T:5,6:swad" --arm "PFAA=$PF_T:5,6,7,8:model" \
  --pair COMBO=PPCC --aa PFAA:5,6:7,8 --verdict PPCC; rc=$?
echo "[$(date "+%F %T")] read rc=$rc"
echo "[$(date "+%F %T")] PP ALL DONE rc=$rc"
