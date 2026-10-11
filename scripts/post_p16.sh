#!/bin/bash
# Post-process P16 (label-fraction curve, cv02; protocols/P16_label_fraction_curve.md + Amendment 1).
# Supervised references: el_p13/reports/p16 (p16_A_*), pooled with P6 L3 20%/100% s0-2. SSL arms: el_p16/reports/p16b.
# 1. pull re-score JSONs; 2. per-image + histogram scoring on cv02; 3. locked rules (S - A per fraction, 5 vs 5 seeds);
# 4. image bootstrap + source split; 5. E1 per-cell metrics (test + 106-cell extension); 6. bars and the label-fraction curve.
# Usage: bash scripts/post_p16.sh <cv02 gpu>
set -e
G=$1; R=~/mtp/research; O=$R/results/p16; PY=$R/.venv/bin/python; CV=cv02@10.8.1.106
A=/tmp/noob_el/el_p13; B=/tmp/noob_el/el_p16; PYR=/tmp/noob_el/el-fault-detection/.venv/bin/python
mkdir -p $O/raw
scp -q -o BatchMode=yes "$CV:$A/reports/p16/p16_A_*_s[0-9].json" $O/raw/
scp -q -o BatchMode=yes $CV:$A/reports/p16/launch.log $O/raw/launch_p16a.log
scp -q -o BatchMode=yes "$CV:$B/reports/p16b/p16_S*_s[0-9].json" $O/raw/
scp -q -o BatchMode=yes $CV:$B/reports/p16b/launch.log $O/raw/launch_p16b.log
scp -q -o BatchMode=yes $CV:$B/reports/p16b/selection.txt $CV:$B/reports/p16b/p16B_queue.spec $O/
na=$(ls $O/raw/p16_A_*_s[0-9].json | wc -l); ns=$(ls $O/raw/p16_S*_s[0-9].json | wc -l)
echo "p16: $na supervised, $ns SSL re-score JSONs"; [ "$na" -eq 9 ] && [ "$ns" -eq 15 ] || { echo "expected 9 + 15"; exit 1; }
ssh -o BatchMode=yes $CV "source /tmp/noob_el/env.sh; \
  cd $A; RA=\$(ls reports/p16/p16_A_*_s[0-9].json | xargs -n1 basename | sed 's/.json//' | tr '\n' ' '); \
  CUDA_VISIBLE_DEVICES=$G $PYR scripts/per_image_scores.py --runs \$RA --out reports/p16/per_image.json > reports/p16/per_image.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=$G $PYR scripts/score_histograms.py --runs \$RA --out reports/p16/hist_revised.npz > reports/p16/hist.log 2>&1; \
  cd $B; RS=\$(ls reports/p16b/p16_S*_s[0-9].json | xargs -n1 basename | sed 's/.json//' | tr '\n' ' '); \
  CUDA_VISIBLE_DEVICES=$G $PYR scripts/per_image_scores.py --runs \$RS --out reports/p16b/per_image.json > reports/p16b/per_image.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=$G $PYR scripts/score_histograms.py --runs \$RS --out reports/p16b/hist_revised.npz > reports/p16b/hist.log 2>&1; \
  tail -n 1 $A/reports/p16/per_image.log $A/reports/p16/hist.log reports/p16b/per_image.log reports/p16b/hist.log"
scp -q -o BatchMode=yes $CV:$A/reports/p16/per_image.json $O/per_image_A.json
scp -q -o BatchMode=yes $CV:$A/reports/p16/hist_revised.npz $O/hist_revised_A.npz
scp -q -o BatchMode=yes $CV:$B/reports/p16b/per_image.json $O/per_image_S.json
scp -q -o BatchMode=yes $CV:$B/reports/p16b/hist_revised.npz $O/hist_revised_S.npz
cd $R
M="p16:A20=p6:L3_20pct+p16:A_20pct p16:A100=p6:L3_100pct+p16:A_100pct"
$PY scripts/ssl_rules.py --dirs $O/raw results/p6/raw --merge $M \
  --arms p16:A20 p16:S_20pct p16:A_50pct p16:S_50pct p16:A100 p16:Sx_100pct \
  --pairs p16:S_20pct=p16:A20 p16:S_50pct=p16:A_50pct p16:Sx_100pct=p16:A100 p6:L3_20pct=p16:A_20pct p6:L3_100pct=p16:A_100pct \
  --ref p16:A100 | tee $O/p16_rules.txt
J="--json $O/per_image_A.json $O/per_image_S.json results/p6/per_image.json --check $O/raw --merge $M"
P="p16:A20=p16:S_20pct p16:A_50pct=p16:S_50pct p16:A100=p16:Sx_100pct"
$PY scripts/per_image_analysis.py $J --pairs $P | tee $O/per_image_test.txt
for k in '^(CSIR|ARTS)_' '^(CFVS|BMRK|SDLE)_'; do
  echo -e "\nSource split, cells matching $k:" | tee -a $O/per_image_test.txt
  $PY scripts/per_image_analysis.py $J --pairs $P --keep "$k" | tee -a $O/per_image_test.txt
done
$PY scripts/ssl_figure.py --dirs $O/raw results/p6/raw --out $O/fig_p16_bars.png \
  --title "P16: SSL (tolerant PL, separate BN, CutMix $(grep -oP 'CUTMIX=\K\S+' $O/selection.txt)) vs supervised at 20/50/100% labels" \
  --arms "p6:L3_20pct=A20 s0-2 (P6)" "p16:A_20pct=A20 s3-4" "p16:S_20pct=S20 (383)" "p16:A_50pct=A50" "p16:S_50pct=S50 (239)" \
    "p6:L3_100pct=A100 s0-2 (P6)" "p16:A_100pct=A100 s3-4" "p16:Sx_100pct=Sx100 (12k)" \
  --hist $O/hist_revised_A.npz $O/hist_revised_S.npz | tee -a $O/p16_rules.txt
$PY scripts/p16_curve.py --out $O/fig_p16_curve.png | tee $O/p16_curve.txt
# E1: per-cell metrics on test and the unseen-module extension (A runs with P13 code, S runs with P16 code)
ssh -o BatchMode=yes $CV "source /tmp/noob_el/env.sh; cd /tmp/noob_el/diag; \
  CUDA_VISIBLE_DEVICES=$G PYTHONPATH=/tmp/noob_el/diag/pylib $PYR e1_task_metrics_v2.py --code $A --out /tmp/noob_el/diag/e1v2 \
    --runs \$(ls -d $A/experiments/p16_A_*_s[0-9]) > e1p16a.log 2>&1 && \
  CUDA_VISIBLE_DEVICES=$G PYTHONPATH=/tmp/noob_el/diag/pylib $PYR e1_task_metrics_v2.py --code $B --out /tmp/noob_el/diag/e1v2 \
    --runs \$(ls -d $B/experiments/p16_S*_s[0-9]) > e1p16s.log 2>&1; tail -n 1 e1p16a.log e1p16s.log"
scp -q -o BatchMode=yes "$CV:/tmp/noob_el/diag/e1v2/p16_*.json" results/e1/raw_v2/
$PY scripts_cv02/e1_aggregate.py results/e1/raw_v2 --sets test ext \
  --merge p16_A20=p6_L3_20pct+p16_A_20pct p16_A100=p6_L3_100pct+p16_A_100pct \
  --arms '^p16_A20$' '^p16_S_20pct$' '^p16_A_50pct$' '^p16_S_50pct$' '^p16_A100$' '^p16_Sx_100pct$' \
  --pairs p16_S_20pct=p16_A20 p16_S_50pct=p16_A_50pct p16_Sx_100pct=p16_A100 2>/dev/null > results/e1/e1_p16.md
cat results/e1/e1_p16.md
