#!/bin/bash
# B5 msc_tta score-claim part 3 (rule results/stageB/B5_tta_module.md s1 item 3): pooled predicted crack px D4MS / PLAIN <= 1.5
# on H36 (36 cells, same 10 models) and on pool_half_p0..3 (models f0 s5, f1 s5). Commands = jobs_tta/PREP.md; D4 printed beside.
set -u
R=/home/noob/work/bench_wt_b; P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
T=/home/noob/work/bench_udev/tta; U=/home/noob/work/bench_udev; M=elbench1/house_r34_unetpp_pf_v11
O=/home/noob/work/bench_reads/stageB/B5; L=$O/part3_run.log
lg(){ echo "[$(date '+%F %T')] $*" | tee -a $L; }
[ "$(md5sum < $R/scripts/bench_labelfree.py | cut -c1-8)" = ca9af858 ] || { echo "REFUSED: tool md5"; exit 1; }
for d in h36 pool_p0 pool_p1 pool_p2 pool_p3; do [ -e $O/$d ] && { echo "REFUSED: $O/$d exists"; exit 1; }; done
lg "start pid $$; bench_wt_b $(git -C $R rev-parse --short HEAD); bench_labelfree ca9af858"
cd $R
nice -n 19 $P scripts/bench_labelfree.py --set h36 --arm PLAIN=$U/dumps_h36/$M:'w1g_pf_v11_f[0-4]_s[56]' \
  --arm D4=$T/dumps_h36/$M:'w1g_pf_v11_f[0-4]_s[56]\.tta_d4' --arm D4MS=$T/dumps_h36/$M:'w1g_pf_v11_f[0-4]_s[56]\.tta_d4ms' \
  --baseline PLAIN --crackfree $U/sets/lists/h36cf.txt --out $O/h36 --workers 8 >> $L 2>&1
lg "h36 rc=$?"
for k in 0 1 2 3; do
  nice -n 19 $P scripts/bench_labelfree.py --set pool_half_p$k --arm PLAIN=$U/dumps_pool_half_p$k/$M:'w1g_pf_v11_f[01]_s5' \
    --arm D4=$T/dumps_pool_half_p$k/$M:'w1g_pf_v11_f[01]_s5\.tta_d4' --arm D4MS=$T/dumps_pool_half_p$k/$M:'w1g_pf_v11_f[01]_s5\.tta_d4ms' \
    --baseline PLAIN --out $O/pool_p$k --workers 8 >> $L 2>&1
  lg "pool_p$k rc=$?"
done
( cd $O && md5sum h36/* pool_p*/* 2>/dev/null > part3_MD5.txt )
lg "done; tracked changes in bench_wt_b: $(git -C $R status --porcelain --untracked-files=no | wc -l)"
