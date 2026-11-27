#!/bin/bash
# c3x read MECHANICS (not a result): the c3x read's flag set (5 arms, the 6 pairs, --aa PF:5,6:7,8, 532 + 416 cells) on
# published cv5v2 SCREEN dumps only (no cv5v3 dump is read): PF = W1-C PF (cv02, 5 seeds), HRNET = rows2 HRNet (2 seeds),
# SWADBN = wave 2a swad_bn (2 seeds), COMBO = stand-in wave 2a rcs (2 seeds), COMBO_SWAD = wave 2a swad .swad (2 seeds).
set -u
O=${O:?}; RT=/home/noob/work/bench_wt_final; cd $RT || exit 1
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
W=/home/noob/work/bench_reads/w1c/links/elbench1; L=/home/noob/work/bench_reads/rows2_full/links/elbench1; WD=/home/noob/work/bench_dumps/w2a/elbench1
X=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python scripts/bench_read_w1.py \
  --arm "PF=$W/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9]" --arm "HRNET=$L/hrnet_w18_unetpp_pf_v11:r2_hrnet_w18_unetpp_pf_f[0-4]_s[56]" \
  --arm "SWADBN=$WD/swad_const_pf_v11:w2a_swad_f[0-4]_s[56]\.swad_bn" --arm "COMBO=$WD/rcs_pf_v11:w2a_rcs_f[0-4]_s[56]" \
  --arm "COMBO_SWAD=$WD/swad_const_pf_v11:w2a_swad_f[0-4]_s[56]\.swad" \
  --pair PF=COMBO --pair PF=COMBO_SWAD --pair HRNET=COMBO --pair HRNET=COMBO_SWAD --pair SWADBN=COMBO --pair SWADBN=COMBO_SWAD \
  --labels v11 --workers 8 --cache $O/cache_c --baseline PF --aa PF:5,6:7,8 --score-exclude $X --out $O/read
echo "read rc $?"
