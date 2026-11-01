#!/bin/bash
# THIN-B3 jobs (protocol_thin_b3.md §3, §8.1): 15 lines "name|seed|arm|opts" in el_thin/reports/thin/q/thin_jobs.txt.
# opts = the pf2_SUPPF opts of el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f) for seed K, with run_name replaced, + the arm's one change.
set -eu
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; O=/home/noob/work/el_thin/reports/thin/q; mkdir -p $O
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ]
declare -A CH=([SKR]="loss.skel_recall.weight=1.0" [CLD]="loss.cldice.weight=1.0 loss.cldice.iters=10" \
               [B3]="data.scuff_class=24 model.num_classes=25 data.mask_subdir=labeled/masks_escdd_s")
for k in 5 6 7 8 9; do
  base=$(grep "^pf2_SUPPF_100pct_s$k|" $J | cut -d'|' -f4 | sed "s/ run_name=pf2_SUPPF_100pct_s$k\$//")
  [ -n "$base" ]
  for a in SKR CLD B3; do echo "thin_${a}_100pct_s$k|$k|$a|$base ${CH[$a]} run_name=thin_${a}_100pct_s$k"; done
done > $O/thin_jobs.txt
md5sum $O/thin_jobs.txt
