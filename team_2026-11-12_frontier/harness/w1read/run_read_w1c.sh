#!/bin/bash
# W1-C read on gaint CPU (lead, 14 Nov 2026): harness/W1_READ.md commands, from the reviewed merged worktree bench_wt_w2 (c57508e).
# Inputs: the 45 relayed cv02 runs through a folder of symlinks (bench_reads/w1c/links). Outputs: bench_reads/w1c/{read,src_calib,dti,d0}.
set -u
cd /home/noob/work/bench_wt_w2 || exit 1
[ "$(git rev-parse --short HEAD)" = c57508e ] || { echo "worktree not at c57508e"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
L=/home/noob/work/bench_reads/w1c/links/elbench1; O=/home/noob/work/bench_reads/w1c
C="--arm PF=$L/house_r34_unetpp_pf_v11:w1c1_pf_v11_f[0-4]_s[5-9] --arm HOUSE=$L/house_r34_unetpp_v11:w1c2_house_v11_f[0-4]_s[56] --arm PFV1=$L/house_r34_unetpp_pf:w1c3_pf_v1_f[0-4]_s[56] --labels v11 --workers 8 --cache $O"
echo "[$(date '+%F %T')] read start"
nice -n 19 $P scripts/bench_read_w1.py $C --baseline PF --aa PF:5,6:7,8 --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
nice -n 19 $P scripts/bench_src_calib.py $C --out $O/src_calib; echo "[$(date '+%F %T')] src_calib rc=$?"
nice -n 19 $P scripts/bench_dti.py $C --out $O/dti; echo "[$(date '+%F %T')] dti rc=$?"
nice -n 19 $P scripts/bench_d0.py $C --out $O/d0; echo "[$(date '+%F %T')] d0 rc=$?"
echo "[$(date '+%F %T')] W1C READ ALL DONE; worktree status lines: $(git status --short | wc -l)"
