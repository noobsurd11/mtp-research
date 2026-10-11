#!/bin/bash
# Post-process P15 (gaint, UCF-EL encoder transfer) and P12's gaint gA10 references.
# 1. pull re-score JSONs; 2. locked rules (scripts/ssl_rules.py); 3. E1 per-cell scoring on cv02 (slim checkpoint copies via
# this machine), which also gives the image bootstrap and leave-top-3-out (E1's pooled IoU equals the re-score exactly).
# Usage: bash scripts/post_p15.sh <cv02 gpu>
set -e
G=$1; R=~/mtp/research; O=$R/results/p15; PY=$R/.venv/bin/python
CV=cv02@10.8.1.106; GA=noob@172.18.22.20; GP14=/home/noob/work/el_p14; GEL=/home/noob/work/el-fault-detection
T=/tmp/claude-1003/-home-yugma/57bebbba-992f-43ae-8c6c-f7004d0f15c5/scratchpad/gimp
mkdir -p $O/raw $T
scp -q -o BatchMode=yes "$GA:$GP14/reports/p15/p15_*_s[0-9].json" $GA:$GP14/reports/p15/launch_gaint.log $O/raw/
scp -q -o BatchMode=yes "$GA:$GEL/reports/p12/p12_g*.json" $GA:$GEL/reports/p12/launch_gaint.log $R/results/p12/raw/
n=$(ls $O/raw/p15_*_s[0-9].json | wc -l); echo "p15: $n re-score JSONs"; [ "$n" -eq 6 ] || { echo "expected 6"; exit 1; }
cd $R
$PY scripts/ssl_rules.py --dirs $O/raw results/p12/raw results/p10/raw results/p6/raw \
  --arms p10:A_5pct p15:gU_5pct p12:gA_10pct p15:gU_10pct p6:L3_10pct p6:L3_100pct \
  --pairs p15:gU_5pct=p10:A_5pct p15:gU_10pct=p12:gA_10pct p15:gU_5pct=p12:gA_10pct p12:gA_10pct=p6:L3_10pct \
  --ref p6:L3_100pct | tee $O/p15_rules.txt
# E1: slim copies (config + final checkpoint) of the gaint runs to cv02, score, pull, aggregate
for r in p15_gU_5pct_s{0,1,2} p15_gU_10pct_s{0,1,2} p12_gA_10pct_s{0,1,2}; do
  [ $r = ${r#p15} ] && src=$GEL || src=$GP14
  ssh -o BatchMode=yes $CV "test -e /tmp/noob_el/diag/g_import/$r/checkpoints/latest.pth" && continue
  mkdir -p $T/$r/checkpoints
  scp -q -o BatchMode=yes $GA:$src/experiments/$r/config_used.yaml $T/$r/
  scp -q -o BatchMode=yes $GA:$src/experiments/$r/checkpoints/latest.pth $T/$r/checkpoints/
  scp -q -r -o BatchMode=yes $T/$r $CV:/tmp/noob_el/diag/g_import/ && rm -rf $T/$r
done
ssh -o BatchMode=yes $CV "source /tmp/noob_el/env.sh; cd /tmp/noob_el/diag; CUDA_VISIBLE_DEVICES=$G PYTHONPATH=/tmp/noob_el/diag/pylib \
  /tmp/noob_el/el-fault-detection/.venv/bin/python e1_task_metrics_v2.py --code /tmp/noob_el/el_p14 --out /tmp/noob_el/diag/e1v2 \
  --runs \$(ls -d /tmp/noob_el/diag/g_import/p15_* /tmp/noob_el/diag/g_import/p12_gA_10pct_*) > e1p15.log 2>&1; tail -n 3 e1p15.log"
scp -q -o BatchMode=yes "$CV:/tmp/noob_el/diag/e1v2/p15_*.json" "$CV:/tmp/noob_el/diag/e1v2/p12_gA_10pct_*.json" results/e1/raw_v2/
$PY scripts_cv02/e1_aggregate.py results/e1/raw_v2 --sets test ext --arms '^p15_' '^p10_A_5pct$' '^p12_gA_10pct$' '^p6_L3_10pct$' \
  --pairs p15_gU_5pct=p10_A_5pct p15_gU_10pct=p12_gA_10pct p15_gU_5pct=p12_gA_10pct p12_gA_10pct=p6_L3_10pct \
  2>/dev/null > results/e1/e1_p15.md
cat results/e1/e1_p15.md
