#!/bin/bash
# THIN-B3 opening, local analysis (runner; coach recomputes independently; no verdict to team-lead before that). Pattern of
# pf2_post_local.sh 3d4bd4ed. Pull gaint el_thin/reports/thin/post/ (MANIFEST checked) + launch.log / gpumem.log to
# results/thin/, then per arm (SKR, CLD, B3) vs the comparator SUPPF (PF2's opening m0 files, already pulled in results/pf2/raw/m0,
# reused unchanged): Track M m2_rung at tau 0 (verdict primaries) and tau 1 (LA, reported); E1 co-primary crack relF1@2 by the
# frozen thin_e1_relf1.py 98bcb979 (all 106, argmax, rule 1 /3 vs SUPPF).
set -eu
R=/home/yugma/mtp/research; T=$R/team_2026-10-31_next; D=$T/results/thin; mkdir -p $D
PY=$R/.venv/bin/python; M2=$R/team_2026-10-24_go/trackM/scripts/m2_rung.py; PM=$T/results/pf2/raw/m0
rsync -a noob@172.18.22.20:/home/noob/work/el_thin/reports/thin/post/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "thin manifest OK $(wc -l < $D/raw/MANIFEST.md5) files"
rsync -a noob@172.18.22.20:/home/noob/work/el_thin/reports/thin/q/launch.log noob@172.18.22.20:/home/noob/work/el_thin/reports/thin/q/gpumem.log $D/
(cd $PM && md5sum pf2_SUPPF_100pct_s*.json) > $D/comparator_m0_md5.txt
M=$D/raw/m0
[ "$(md5sum < $T/scripts/thin/thin_e1_relf1.py | cut -c1-8)" = 98bcb979 ]
for a in SKR CLD B3; do
  $PY $M2 --label ${a}_vs_SUPPF --a $(for k in 5 6 7 8 9; do echo $PM/pf2_SUPPF_100pct_s$k.json; done) \
    --b $(for k in 5 6 7 8 9; do echo $M/thin_${a}_100pct_s$k.json; done) > $D/m2_rung_${a}.txt 2>/dev/null
  $PY $M2 --label ${a}_vs_SUPPF_LA1 --a $(for k in 5 6 7 8 9; do echo $PM/pf2_SUPPF_100pct_s$k.tau1.json; done) \
    --b $(for k in 5 6 7 8 9; do echo $M/thin_${a}_100pct_s$k.tau1.json; done) > $D/m2_rung_${a}_tau1.txt 2>/dev/null
done
$PY $T/scripts/thin/thin_e1_relf1.py --arm SUPPF $PM pf2 --arm SKR $M thin --arm CLD $M thin --arm B3 $M thin \
  --rev SUPPF e544133 --rev SKR c9bbb02 --rev CLD c9bbb02 --rev B3 c9bbb02 --base SUPPF > $D/thin_e1_relf1.txt
md5sum $D/m2_rung_*.txt $D/thin_e1_relf1.txt > $D/local_md5.txt
echo "local analysis written to $D (verdicts only after coach's independent recompute)"
