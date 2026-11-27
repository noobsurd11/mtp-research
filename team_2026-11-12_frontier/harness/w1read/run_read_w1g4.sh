#!/bin/bash
# W1-G + W1-G2 four-seed read on gaint CPU (lead, 15 Nov 2026): PF v1.1 seeds 5 to 8, A/A {5,6} v {7,8} = margin M on gaint.
set -u
cd /home/noob/work/bench_wt_w2 || exit 1
[ "$(git rev-parse --short HEAD)" = c57508e ] || { echo "worktree not at c57508e"; exit 1; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
O=/home/noob/work/bench_reads/w1g4
G="--arm PF=/home/noob/work/bench_dumps/w1g/elbench1/house_r34_unetpp_pf_v11:w1g_pf_v11_f[0-4]_s[5-8] --labels v11 --workers 8 --cache $O"
echo "[$(date '+%F %T')] w1g4 read start"
nice -n 19 $P scripts/bench_read_w1.py $G --baseline PF --aa PF:5,6:7,8 --out $O/read; echo "[$(date '+%F %T')] read rc=$?"
echo "[$(date '+%F %T')] W1G4 READ ALL DONE; tracked changes in worktree: $(git status --porcelain -uno | wc -l)"
