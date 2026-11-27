#!/bin/bash
# Stage B U2 / U4 reads on udev_infer's dumps (commands = /home/noob/work/bench_udev/jobs_v2/PREP.md lines 72 to 81; rule
# results/stageB/B3.md: U2 is an upper bound, gamed for scale-changing arms; U4 H36 crack-free false alarms and pool half-cell
# volume ratios are guards). PF = W1-G seeds 5 to 8 (pool: f0, f1 s5); arms = the wave 2a seed-5 run-keys.
set -u
R=/home/noob/work/bench_wt_b; P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
U=/home/noob/work/bench_udev; O=/home/noob/work/bench_reads/stageB; L=$O/u2u4_run.log
lg(){ echo "[$(date '+%F %T')] $*" | tee -a $L; }
for d in U2 U4_h36 U4_pool_p0 U4_pool_p1 U4_pool_p2 U4_pool_p3; do [ -e $O/$d ] && { echo "REFUSED: $O/$d exists"; exit 1; }; done
lg "start pid $$; bench_wt_b $(git -C $R rev-parse --short HEAD); bench_udev_read $(md5sum < $R/scripts/bench_udev_read.py | cut -c1-8); bench_labelfree $(md5sum < $R/scripts/bench_labelfree.py | cut -c1-8)"
cd $R
arms(){ # $1 = dump root, $2 = fold class
  echo --arm EMA=$1/ema_wise_posthoc_pf_v11:"w2a_ema_f[$2]_s5" --arm EMABN=$1/ema_wise_posthoc_pf_v11:"w2a_ema_f[$2]_s5\\.ema_9998_bn" \
       --arm JMLHARD=$1/jml_hard:"w2a_jmlhard_f[$2]_s5" --arm RCS=$1/rcs_pf_v11:"w2a_rcs_f[$2]_s5" \
       --arm SOFTBAND=$1/soft_band_jml:"w2a_softband_f[$2]_s5" --arm SWAD=$1/swad_const_pf_v11:"w2a_swad_f[$2]_s5" \
       --arm SWADBN=$1/swad_const_pf_v11:"w2a_swad_f[$2]_s5\\.swad_bn"
}
E=$U/dumps_shvoof/elbench1
nice -n 19 $P scripts/bench_udev_read.py --arm PF=$E/house_r34_unetpp_pf_v11:'w1g_pf_v11_f[0-4]_s[5-8]' $(arms $E 0-4) --baseline PF \
  --stems $U/build_shvoof_v2/sets/shvoof/stems_eval.txt --name U2 --labels set --out $O/U2 >> $L 2>&1
lg "U2 rc=$?"
E=$U/dumps_h36/elbench1
nice -n 19 $P scripts/bench_labelfree.py --set h36 --arm PF=$E/house_r34_unetpp_pf_v11:'w1g_pf_v11_f[0-4]_s[5-8]' $(arms $E 0-4) \
  --baseline PF --crackfree $U/sets/lists/h36cf.txt --out $O/U4_h36 --workers 8 >> $L 2>&1
lg "U4_h36 rc=$?"
for k in 0 1 2 3; do
  E=$U/dumps_pool_half_p$k/elbench1
  nice -n 19 $P scripts/bench_labelfree.py --set pool_half_p$k --arm PF=$E/house_r34_unetpp_pf_v11:'w1g_pf_v11_f[01]_s5' $(arms $E 01) \
    --baseline PF --out $O/U4_pool_p$k --workers 8 >> $L 2>&1
  lg "U4_pool_p$k rc=$?"
done
( cd $O && md5sum U2/* U4_*/* 2>/dev/null > u2u4_MD5.txt )
lg "done; tracked changes in bench_wt_b: $(git -C $R status --porcelain --untracked-files=no | wc -l)"
