#!/bin/bash
# AL1 post-run scoring on cv02 (read-only inference, network A of latest.pth = step 20,000), GPU given as $1.
# Outputs in /tmp/noob_el/el_alhvr/reports/al1post/. Model: sk1_post.sh (no LA step).
G=$1; cd /tmp/noob_el/el_alhvr; source /tmp/noob_el/env.sh
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python; O=reports/al1post; mkdir -p $O
export CUDA_VISIBLE_DEVICES=$G
RUNS=$(ls -d experiments/al1_*_s[0-9] | xargs -n1 basename | tr '\n' ' ')
echo "[$(date)] runs: $(echo $RUNS | wc -w)"
echo "[$(date)] per_image"; $PY scripts/per_image_scores.py --runs $RUNS --out $O/per_image.json > $O/per_image.log 2>&1; echo "rc=$?"
echo "[$(date)] hist"; $PY scripts/score_histograms.py --runs $RUNS --out $O/hist_revised.npz > $O/hist.log 2>&1; echo "rc=$?"
echo "[$(date)] E1"; cd /tmp/noob_el/diag && PYTHONPATH=/tmp/noob_el/diag/pylib $PY e1_task_metrics_v2.py --code /tmp/noob_el/el_alhvr --out /tmp/noob_el/diag/e1v2 --runs $(for r in $RUNS; do echo /tmp/noob_el/el_alhvr/experiments/$r; done) > /tmp/noob_el/el_alhvr/$O/e1.log 2>&1; echo "rc=$?"
echo "[$(date)] done"
