#!/bin/bash
# U1 deciding read and the two per-source reads (commands of /home/noob/work/bench_udev/jobs_v2/PREP.md lines 54 to 69;
# rule: results/stageB/B3.md 1b rule 6 with the lead's additions of 15 Nov 16:07 / 16:14 / 17:58). Run by the lead, 17 Nov,
# gaint CPU, from bench_wt_udev at ae4dd10 (must stay clean). Output folders must not exist.
set -u
W=/home/noob/work/bench_wt_udev; P=/home/noob/work/el-fault-detection/.venv/bin/python; D=/home/noob/work/bench_udev/dumps/elbench1
[ "$(git -C $W rev-parse --short HEAD)" = ae4dd10 ] && [ "$(git -C $W status --porcelain -uno | wc -l)" = 0 ] || { echo "bench_wt_udev not clean at ae4dd10"; exit 1; }
for o in U1 U1_CSIR U1_BMRK; do [ -e /home/noob/work/bench_reads/stageB/$o ] && { echo "exists: $o"; exit 1; }; done
cat /home/noob/work/bench_udev/roots/cvloso2_v11_f{0,1}/splits/test.txt > /home/noob/work/bench_reads/stageB/U1_stems.txt
echo "U1 stems: $(grep -c . /home/noob/work/bench_reads/stageB/U1_stems.txt)"
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd $W || exit 1
echo "[$(date '+%F %T')] U1 pooled start"
nice -n 19 $P scripts/bench_udev_read.py --arm PF=$D/house_r34_unetpp_pf_v11:'udev_pf_loso_f[01]_s[5-8]' --arm SKR01=$D/skr01_pf_v11:'udev_skr01_loso_f[01]_s[56]' --baseline PF --stems /home/noob/work/bench_reads/stageB/U1_stems.txt --name U1 --labels v11 --out /home/noob/work/bench_reads/stageB/U1; echo "[$(date '+%F %T')] U1 pooled rc=$?"
nice -n 19 $P scripts/bench_udev_read.py --arm PF=$D/house_r34_unetpp_pf_v11:'udev_pf_loso_f0_s[5-8]' --arm SKR01=$D/skr01_pf_v11:'udev_skr01_loso_f0_s[56]' --baseline PF --stems /home/noob/work/bench_udev/roots/cvloso2_v11_f0/splits/test.txt --name U1_CSIR --labels v11 --out /home/noob/work/bench_reads/stageB/U1_CSIR; echo "[$(date '+%F %T')] U1_CSIR rc=$?"
nice -n 19 $P scripts/bench_udev_read.py --arm PF=$D/house_r34_unetpp_pf_v11:'udev_pf_loso_f1_s[5-8]' --arm SKR01=$D/skr01_pf_v11:'udev_skr01_loso_f1_s[56]' --baseline PF --stems /home/noob/work/bench_udev/roots/cvloso2_v11_f1/splits/test.txt --name U1_BMRK --labels v11 --out /home/noob/work/bench_reads/stageB/U1_BMRK; echo "[$(date '+%F %T')] U1_BMRK rc=$?"
echo "[$(date '+%F %T')] U1 READ ALL DONE; tracked changes in bench_wt_udev: $(git -C $W status --porcelain -uno | wc -l)"
