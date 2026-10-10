#!/bin/bash
# Post-process a finished P7 or P8: pull re-score JSONs, run per-image + histogram scoring on cv02, apply locked rules,
# image-bootstrap check, figure. Usage: bash scripts/post_p78.sh p7|p8 [gpu]
set -e
E=$1; G=${2:-0}; R=~/mtp/research; O=$R/results/$E; PY=$R/.venv/bin/python
mkdir -p $O/raw
scp -q -o BatchMode=yes "cv02@10.8.1.106:/tmp/noob_el/el_p7/reports/$E/*" $O/raw/
n=$(ls $O/raw/${E}_*.json | wc -l); echo "$E: $n re-score JSONs"; [ "$n" -eq 9 ] || { echo "expected 9"; exit 1; }
ssh -o BatchMode=yes cv02@10.8.1.106 "source /tmp/noob_el/env.sh; cd /tmp/noob_el/el_p7; RUNS=\$(ls reports/$E/${E}_*.json | xargs -n1 basename | sed 's/.json//' | tr '\n' ' '); \
  CUDA_VISIBLE_DEVICES=$G /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/per_image_scores.py --runs \$RUNS --out reports/$E/per_image.json > reports/$E/per_image.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=$G /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/score_histograms.py --runs \$RUNS --out reports/$E/hist_revised.npz > reports/$E/hist.log 2>&1; tail -n 1 reports/$E/per_image.log reports/$E/hist.log"
scp -q -o BatchMode=yes cv02@10.8.1.106:/tmp/noob_el/el_p7/reports/$E/per_image.json cv02@10.8.1.106:/tmp/noob_el/el_p7/reports/$E/hist_revised.npz $O/
mv $O/raw/per_image.json $O/raw/hist_revised.npz $O/raw/*.log $O/ 2>/dev/null || true
cp $O/launch.log $O/raw/ 2>/dev/null || true
cd $R
$PY scripts/p78_rules.py $E $O/raw results/p6/raw | tee $O/${E}_rules.txt
B=$([ $E = p7 ] && echo L0 || echo L3)
$PY scripts/per_image_analysis.py --json $O/per_image.json results/p6/per_image.json --check $O/raw \
  --pairs $E:D_10pct=$E:C_10pct $E:D_10pct=$E:B_10pct $E:B_10pct=$E:C_10pct p6:${B}_10pct=$E:D_10pct | tee $O/per_image_test.txt
$PY scripts/p78_figure.py $E $O/raw results/p6/raw $O/hist_revised.npz | tee -a $O/${E}_rules.txt
