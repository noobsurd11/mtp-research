#!/bin/bash
# runner DRAFT (3 Nov 2026): SKR2C jobs (protocol_SKR2C, coach drafting): fresh seeds 10-14, two arms, TRAINING ONLY.
# Jobs -> /home/noob/work/s2c/s2c_jobs.txt, lines "name|seed|arm|opts", ORDER per seed K = 10..14: SKR01 sK, then SUPPF sK (10 lines).
# Opts = the pf2_SUPPF_100pct_s5 line of el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f) with seed=5 -> seed=K and run_name replaced,
# + data.root=/home/noob/work/s2c_root (v2, team-lead 3 Nov: data-root trick, test.txt = val; s2c_rootcheck.sh verified it):
#   SUPPF (el_f3 e544133): no other change                                          names ${PS}_sK
#   SKR01 (el_thin c9bbb02): + loss.skel_recall.weight=0.1 (as s2q_jobs d6efb9af)  names ${PK}_sK
# Asserts: pf2 SUPPF s6..s9 lines = the s5 line with seed / run_name substituted (seed is the only per-seed opt); the s2q SKR01 s5
#   line (d6efb9af) = this recipe at K=5 (same recipe as the opened SKR2 runs).
# exp_<arm>.txt = the queue-format config diff vs pf2_SUPPF_100pct_s5: SUPPF = the data.root lines; SKR01 = s2q's exp_SKR01 3fa67569 lines
# + the data.root lines. Each must equal s2c_check/exp_<arm>_derived.txt (rootcheck's diff of the config train.py will write).
# O = output dir (default /home/noob/work/s2c; a scratch dir for the dry check).
set -eu
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; S=/home/noob/work/s2q; O=${O:-/home/noob/work/s2c}; mkdir -p $O
PS=${PS:-s2c_SUPPF_100pct}; PK=${PK:-s2c_SKR01_100pct}
[ "$(md5sum < $J | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ]
[ "$(md5sum < $S/s2q_jobs.txt | cut -c1-32)" = d6efb9af81e5bc98101cbf674c20d5f2 ]
[ "$(md5sum < $S/exp_SKR01.txt | cut -c1-32)" = 3fa67569be40c0da4ab48fa538378416 ]
DR=/home/noob/work/s2c_root; C=/home/noob/work/s2c_check
(cd $DR/splits && md5sum -c --quiet ../SPLITS.md5) && cmp -s $DR/splits/test.txt $DR/splits/val.txt
[ ! -e $O/s2c_jobs.txt ] || { echo "s2c_jobs.txt exists"; exit 1; }
b5=$(grep "^pf2_SUPPF_100pct_s5|" $J | cut -d'|' -f4)
case "$b5" in "seed=5 "*" run_name=pf2_SUPPF_100pct_s5") ;; *) echo "s5 line form"; exit 1;; esac
core=${b5#seed=5 }; core=${core% run_name=pf2_SUPPF_100pct_s5}
for k in 6 7 8 9; do [ "$(grep "^pf2_SUPPF_100pct_s$k|" $J | cut -d'|' -f4)" = "seed=$k $core run_name=pf2_SUPPF_100pct_s$k" ]; done
[ "$(grep '^skr2_SKR01_100pct_s5|' $S/s2q_jobs.txt | cut -d'|' -f4)" = "seed=5 $core loss.skel_recall.weight=0.1 run_name=skr2_SKR01_100pct_s5" ]
: > $O/s2c_jobs.txt
for k in 10 11 12 13 14; do
  echo "${PK}_s$k|$k|SKR01|seed=$k $core loss.skel_recall.weight=0.1 data.root=$DR run_name=${PK}_s$k" >> $O/s2c_jobs.txt
  echo "${PS}_s$k|$k|SUPPF|seed=$k $core data.root=$DR run_name=${PS}_s$k" >> $O/s2c_jobs.txt
done
[ "$(wc -l < $O/s2c_jobs.txt)" = 10 ]
RL=$(printf '%s\n' "<   root: $DR" '>   root: data')
{ echo "$RL"; cat $S/exp_SKR01.txt; } | sort > $O/exp_SKR01.txt; echo "$RL" | sort > $O/exp_SUPPF.txt
cmp $O/exp_SKR01.txt $C/exp_SKR01_derived.txt; cmp $O/exp_SUPPF.txt $C/exp_SUPPF_derived.txt
md5sum $O/s2c_jobs.txt $O/exp_SKR01.txt $O/exp_SUPPF.txt
