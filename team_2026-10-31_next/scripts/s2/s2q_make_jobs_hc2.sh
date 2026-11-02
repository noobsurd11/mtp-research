#!/bin/bash
# runner DRAFT (2 Nov 2026): HC2 jobs + expected config diff for the chained second s2q queue (protocol_SKR2_HC2 v1.1; HC2 = (a2)
# synth_halfcut_ignore_inactive at el_hc2 0405151, builder build_hc2.md acbe4352, coach ACCEPTED).
# Jobs -> /home/noob/work/s2q/s2q_jobs_hc2.txt, lines "name|seed|arm|opts", ORDER s5 .. s9 (5 lines), names hc2_HCig_100pct_sK, arm HC2.
# Opts = the pf2_SUPPF_100pct_sK line of el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f), run_name replaced, + the arm's change:
#   data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv data.synth_halfcut_ignore_inactive=true
# exp_HC2.txt = nq exp_HC.txt (01008fdf: synth_halfcut block, p 0.35 + pool) + the new key's line, in the queue's diff format. It must
# equal the HC2 smoke's real diff (runner_smk/s2/hc2_smk_HCig_s0.cfgdiff.txt); this script refuses otherwise (run it after the smoke).
set -eu
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; O=/home/noob/work/s2q; SD=/home/noob/work/runner_smk/s2/hc2_smk_HCig_s0.cfgdiff.txt
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ]
[ "$(md5sum < /home/noob/work/nq/exp_HC.txt | cut -c1-8)" = 01008fdf ]
[ ! -e $O/s2q_jobs_hc2.txt ] && [ ! -e $O/exp_HC2.txt ]
: > $O/s2q_jobs_hc2.txt
for k in 5 6 7 8 9; do
  base=$(grep "^pf2_SUPPF_100pct_s$k|" $J | cut -d'|' -f4 | sed "s/ run_name=pf2_SUPPF_100pct_s$k\$//"); [ -n "$base" ]
  echo "hc2_HCig_100pct_s$k|$k|HC2|$base data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv data.synth_halfcut_ignore_inactive=true run_name=hc2_HCig_100pct_s$k" >> $O/s2q_jobs_hc2.txt
done
[ "$(wc -l < $O/s2q_jobs_hc2.txt)" = 5 ]
{ cat /home/noob/work/nq/exp_HC.txt; echo '<   synth_halfcut_ignore_inactive: true'; } | sort > $O/exp_HC2.txt
[ -s $SD ] && [ "$(sort $SD)" = "$(cat $O/exp_HC2.txt)" ] || { echo "exp_HC2 != the HC2 smoke's real config diff ($SD)"; rm -f $O/s2q_jobs_hc2.txt $O/exp_HC2.txt; exit 1; }
md5sum $O/s2q_jobs_hc2.txt $O/exp_HC2.txt
