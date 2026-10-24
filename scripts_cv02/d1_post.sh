#!/bin/bash
# Track D labelset post-processing on cv02 (protocol_labelset.md §8-9). Waits until every d1 run has a "trained ... rc=" line,
# then: completion check, per-cell scoring (standard + banded counts, tau 0/1, 24x24 confusion) for the 27 runs and the
# yardsticks, and E1 on the 27 runs. Read-only on checkpoints. Usage: d1_post.sh <gpu>
G=$1; PY=/tmp/noob_el/el-fault-detection/.venv/bin/python; cd /tmp/noob_el/el_d1; O=reports/d1post; mkdir -p $O
RUNS=$(grep -v '^\s*#' d1_queue.spec | awk 'NF{print $1}')
until [ "$(grep -c ' trained d1_' reports/d1/launch.log)" -ge 27 ]; do sleep 120; done
echo "[$(date)] all 27 trained" >> $O/post.log
for r in $RUNS; do
  s=$(grep -a "TEST (final weights, step 20000)" experiments/$r.stdout | wc -l); h=$(grep -ac "INFO train — Run:" experiments/$r.stdout)
  echo "$r test_final_lines=$s headers=$h rescore=$(test -s reports/d1/$r.json && echo ok || echo MISSING)" >> $O/completion.txt
done
source /tmp/noob_el/env.sh; export CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=4
Y="/tmp/noob_el/el_sk1/experiments/p12_A_5pct_s0 /tmp/noob_el/el_sk1/experiments/p12_A_5pct_s1 /tmp/noob_el/el_sk1/experiments/p12_A_5pct_s2 /tmp/noob_el/el_sk1/experiments/p13_A_5pct_s3 /tmp/noob_el/el_sk1/experiments/p13_A_5pct_s4 $(for s in 0 1 2 3 4; do echo /tmp/noob_el/el_alhvr/experiments/al1_BsM5_s$s; done) $(for s in 0 1 2; do echo /tmp/noob_el/el_sk1/experiments/p6_L3_10pct_s$s; done)"
echo "[$(date)] score" >> $O/post.log
$PY -u trackD_d1_score.py --code /tmp/noob_el/el_d1 --out /tmp/noob_el/el_d1/$O/d1_score.json --runs $(for r in $RUNS; do echo /tmp/noob_el/el_d1/experiments/$r; done) $Y > $O/score.log 2>&1
echo "[$(date)] score rc=$?" >> $O/post.log
echo "[$(date)] E1" >> $O/post.log
cd /tmp/noob_el/diag && PYTHONPATH=/tmp/noob_el/diag/pylib $PY e1_task_metrics_v2.py --code /tmp/noob_el/el_d1 --out /tmp/noob_el/diag/e1v2 --runs $(for r in $RUNS; do echo /tmp/noob_el/el_d1/experiments/$r; done) > /tmp/noob_el/el_d1/$O/e1.log 2>&1
echo "[$(date)] E1 rc=$?" >> /tmp/noob_el/el_d1/$O/post.log
echo "[$(date)] post done" >> /tmp/noob_el/el_d1/$O/post.log
