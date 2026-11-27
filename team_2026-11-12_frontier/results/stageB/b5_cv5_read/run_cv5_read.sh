#!/bin/bash
# B5 msc_tta CV5 read (rule: results/stageB/B5_tta_module.md section 1, written 15 Nov before any TTA number).
# Commands = /home/noob/work/bench_udev/jobs_tta/PREP.md "Reads after the jobs", run from bench_wt_b (tools equal to the deploy:
# bench_read_w1.py fdb56b78, bench_ens_dump.py 80f93914). 532 cells decide (registered); the 416 clean cells are printed beside.
set -u
R=/home/noob/work/bench_wt_b; P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
T=/home/noob/work/bench_udev/tta; M=elbench1/house_r34_unetpp_pf_v11; G=/home/noob/work/bench_dumps/w1g/$M
O=/home/noob/work/bench_reads/stageB/B5; L=$O/cv5_run.log
XCL=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/score_exclude_v3.txt
lg(){ echo "[$(date '+%F %T')] $*" | tee -a $L; }
[ -e $O/cv5 ] && { echo "REFUSED: $O/cv5 exists"; exit 1; }
[ "$(git -C $R status --porcelain --untracked-files=no | wc -l)" = 0 ] || { echo "REFUSED: tracked change in $R"; exit 1; }
[ "$(md5sum < $R/scripts/bench_read_w1.py | cut -c1-8)" = fdb56b78 ] || { echo "REFUSED: read tool md5"; exit 1; }
lg "start pid $$; bench_wt_b $(git -C $R rev-parse --short HEAD); read tool fdb56b78; ens tool $(md5sum < $R/scripts/bench_ens_dump.py | cut -c1-8)"
cd $R
if [ ! -d $T/ens/elbench1/pf_v11_d4ens3 ]; then
  nice -n 19 $P scripts/bench_ens_dump.py --arm D4=$T/dumps_cv5/$M:'w1g_pf_v11_f[0-4]_s[567]\.tta_d4' --seeds 5,6,7 --seed-id 567 \
      --method pf_v11_d4ens3 --run-prefix w1g_pf_v11_d4ens3_s567 --dumps $T/ens --workers 8 >> $L 2>&1
  lg "ens rc=$?"
fi
ARMS=(--arm PLAIN=$G:'w1g_pf_v11_f[0-4]_s[56]'
      --arm D4=$T/dumps_cv5/$M:'w1g_pf_v11_f[0-4]_s[56]\.tta_d4' --arm D4MS=$T/dumps_cv5/$M:'w1g_pf_v11_f[0-4]_s[56]\.tta_d4ms'
      --arm D4ENS3=$T/ens/elbench1/pf_v11_d4ens3:'w1g_pf_v11_d4ens3_s567_f[0-4]'
      --baseline PLAIN --pair PLAIN=D4MS --pair PLAIN=D4 --pair D4=D4MS --pair D4ENS3=D4MS --labels v11 --workers 8)
nice -n 19 $P scripts/bench_read_w1.py "${ARMS[@]}" --out $O/cv5 >> $L 2>&1
lg "read 532 rc=$?"
nice -n 19 $P scripts/bench_read_w1.py "${ARMS[@]}" --score-exclude $XCL --out $O/cv5_x416 >> $L 2>&1
lg "read 416 (printed beside) rc=$?"
( cd $O && md5sum cv5/* cv5_x416/* 2>/dev/null > cv5_MD5.txt )
lg "done; tracked changes in bench_wt_b: $(git -C $R status --porcelain --untracked-files=no | wc -l)"
