#!/bin/bash
# x4 step 2 positive control (gaint CPU only, nice 19, 8 workers): re-run the c3x read code path on the existing cv5v3 dumps.
#  (a) 5 seeds: PF, COMBO (swad_bn), COMBO_SWAD (swad), seeds 5 to 9, pairs PF=COMBO and PF=COMBO_SWAD, A/A PF:5,6:7,8:
#      must reproduce bench_reads/c3x/read/read.json for these arms and contrasts (IDENTICAL / DIFF by x4_posctl_cmp.py).
#  (b) 2 seeds: the same arms with seeds 5, 6; PFAA = PF seeds 5 to 8 only for the margin M.
#  (c) the x4 read as it will run: arm PFX = PF seeds 5, 6 against base COMBO = COMBO_SWAD seeds 5, 6 (PFAA for M).
# Outputs /home/noob/work/bench_reads/x4_posctl_{a,b,c}; shared cache /home/noob/work/bench_reads/x4_cache.
set -u
H=$(dirname "$(readlink -f "$0")"); . $H/x4_arms.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; R=/home/noob/work/bench_reads; C=$R/x4_cache
echo "[$(date '+%F %T')] posctl start"
$P $H/read_x4.py --out $R/x4_posctl_a --base PF --cache $C --verdict COMBO,COMBO_SWAD \
  --arm "PF=$PF_T:5,6,7,8,9:model" --arm "COMBO=$COMBO_BN_T:5,6,7,8,9:swad_bn" --arm "COMBO_SWAD=$COMBO_T:5,6,7,8,9:swad" \
  --pair PF=COMBO --pair PF=COMBO_SWAD --aa PF:5,6:7,8; ra=$?
echo "[$(date '+%F %T')] (a) rc=$ra"
$P $H/read_x4.py --out $R/x4_posctl_b --base PF --cache $C --verdict COMBO,COMBO_SWAD \
  --arm "PF=$PF_T:5,6:model" --arm "COMBO=$COMBO_BN_T:5,6:swad_bn" --arm "COMBO_SWAD=$COMBO_T:5,6:swad" \
  --arm "PFAA=$PF_T:5,6,7,8:model" --pair PF=COMBO --pair PF=COMBO_SWAD --aa PFAA:5,6:7,8; rb=$?
echo "[$(date '+%F %T')] (b) rc=$rb"
$P $H/read_x4.py --out $R/x4_posctl_c --base COMBO --cache $C --verdict PFX \
  --arm "COMBO=$COMBO_T:5,6:swad" --arm "PFX=$PF_T:5,6:model" --arm "PFAA=$PF_T:5,6,7,8:model" \
  --pair COMBO=PFX --aa PFAA:5,6:7,8; rc_=$?
echo "[$(date '+%F %T')] (c) rc=$rc_"
$P $H/x4_posctl_cmp.py | tee $H/evidence/posctl_cmp.out
echo "[$(date '+%F %T')] POSCTL ALL DONE a=$ra b=$rb c=$rc_"
