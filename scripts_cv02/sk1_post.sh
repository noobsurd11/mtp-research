#!/bin/bash
# SK1 post-run scoring on cv02 (read-only inference), GPU given as $1. Outputs in reports/sk1post/.
G=$1; cd /tmp/noob_el/el_sk1; source /tmp/noob_el/env.sh
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python; O=reports/sk1post; mkdir -p $O/check
export CUDA_VISIBLE_DEVICES=$G
SK=$(ls -d experiments/sk1_*_s[0-9] | xargs -n1 basename | tr '\n' ' ')
A5="p12_A_5pct_s0 p12_A_5pct_s1 p12_A_5pct_s2 p13_A_5pct_s3 p13_A_5pct_s4"
BSD="sk1_BsD_5pct_s0 sk1_BsD_5pct_s1 sk1_BsD_5pct_s2 sk1_BsD_5pct_s3 sk1_BsD_5pct_s4"
for r in $SK; do ln -sfn ../../sk1/$r.json $O/check/$r.json; done
for r in p12_A_5pct_s0 p12_A_5pct_s1 p12_A_5pct_s2; do ln -sfn /tmp/noob_el/el_p11/reports/p12/$r.json $O/check/$r.json; done
for r in p13_A_5pct_s3 p13_A_5pct_s4; do ln -sfn /tmp/noob_el/el_p13/reports/p13/$r.json $O/check/$r.json; done
echo "[$(date)] per_image"; $PY scripts/per_image_scores.py --runs $SK --out $O/per_image.json > $O/per_image.log 2>&1; echo "rc=$?"
echo "[$(date)] hist"; $PY scripts/score_histograms.py --runs $SK --out $O/hist_revised.npz > $O/hist.log 2>&1; echo "rc=$?"
echo "[$(date)] LA test"; $PY scripts/rescore_logit_adjust.py --runs $BSD $A5 --taus 0 1 --splits test --check $O/check --out $O/la_test.json > $O/la_test.log 2>&1; echo "rc=$?"
echo "[$(date)] LA val grid"; $PY scripts/rescore_logit_adjust.py --runs $BSD $A5 --taus 0 0.25 0.5 0.75 1 1.5 2 --splits val --check $O/check --out $O/la_val.json > $O/la_val.log 2>&1; echo "rc=$?"
echo "[$(date)] E1"; cd /tmp/noob_el/diag && PYTHONPATH=/tmp/noob_el/diag/pylib $PY e1_task_metrics_v2.py --code /tmp/noob_el/el_sk1 --out /tmp/noob_el/diag/e1v2 --runs $(for r in $SK; do echo /tmp/noob_el/el_sk1/experiments/$r; done) > /tmp/noob_el/el_sk1/$O/e1.log 2>&1; echo "rc=$?"
echo "[$(date)] done"
