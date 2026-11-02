#!/bin/bash
# runner DRAFT v2 (2 Nov 2026): SKR2-ONLY jobs (coach: queue split after D1; HC2 = inactive-ineligible variant on builder's new
# deploy gets its own jobs file later; v1's 10-line file 1b6a642a and exp_HC2 450c0c7c are VOID, renamed *_VOID on gaint).
# Jobs -> /home/noob/work/s2q/s2q_jobs.txt, lines "name|seed|arm|opts", ORDER SKR2 s5 .. s9 (5 lines).
# Opts = the pf2_SUPPF_100pct_sK line of el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f), run_name replaced, + the arm's ONE change:
#   SKR01 (el_thin c9bbb02): loss.skel_recall.weight=0.1                                     names skr2_SKR01_100pct_sK
# exp_SKR01.txt = the expected config_used.yaml diff vs pf2_SUPPF_100pct_s5 (run_name / seed / experiments_dir ignored), in the
# queue's diff format: THIN's SKR diff with weight 1.0 -> 0.1 (checked on the SKR2 smoke's real config 11:29, 'config OK').
set -eu
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; O=/home/noob/work/s2q; mkdir -p $O
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ]
: > $O/s2q_jobs.txt
for k in 5 6 7 8 9; do
  base=$(grep "^pf2_SUPPF_100pct_s$k|" $J | cut -d'|' -f4 | sed "s/ run_name=pf2_SUPPF_100pct_s$k\$//"); [ -n "$base" ]
  echo "skr2_SKR01_100pct_s$k|$k|SKR01|$base loss.skel_recall.weight=0.1 run_name=skr2_SKR01_100pct_s$k" >> $O/s2q_jobs.txt
done
[ "$(wc -l < $O/s2q_jobs.txt)" = 5 ]
printf '%s\n' '<   skel_recall:' '<     weight: 0.1' > $O/exp_SKR01.txt
md5sum $O/s2q_jobs.txt $O/exp_SKR01.txt
