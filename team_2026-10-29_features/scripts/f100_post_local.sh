#!/bin/bash
# protocol_100 opening 1, local analysis: pull gaint el_f3/reports/f100/post_opening1/ (MD5 checked) to results/f100/opening1/raw,
# Track M rung analysis per contrast at tau 0 and tau 1 (recipe SUPPF - SUP, pool MIMPF - SUPPF, bottom line MIMPF - SUP),
# and the P-series rule cross-check on the rescore JSONs (f3_ run names mapped to p93_ for ssl_rules.py).
set -eu
cd /home/yugma/mtp/research/team_2026-10-29_features
D=results/f100/opening1; mkdir -p $D
rsync -a noob@172.18.22.20:/home/noob/work/el_f3/reports/f100/post_opening1/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "opening1 manifest OK $(wc -l < $D/raw/MANIFEST.md5) files"
M=$D/raw/m0; PY=/home/yugma/mtp/research/.venv/bin/python; R=../team_2026-10-24_go/trackM/scripts/m2_rung.py
run(){ lab=$1; a=$2; b=$3
  $PY $R --label $lab --a $M/f3_${a}_100pct_s{0,1,2,3,4}.json --b $M/f3_${b}_100pct_s{0,1,2,3,4}.json > $D/m2_rung_${lab}.txt 2>/dev/null
  $PY $R --label ${lab}_LA1 --a $M/f3_${a}_100pct_s{0,1,2,3,4}.tau1.json --b $M/f3_${b}_100pct_s{0,1,2,3,4}.tau1.json > $D/m2_rung_${lab}_tau1.txt 2>/dev/null; }
run recipe SUP SUPPF
run pool SUPPF MIMPF
run bottom SUP MIMPF
rm -rf $D/rules_in; mkdir -p $D/rules_in
for f in $D/raw/rescore/f3_*_100pct_s*.json; do
  sed 's/"\(test\|val\)\/f3_/"\1\/p93_/g' $f > $D/rules_in/$(basename $f | sed 's/^f3_/p93_/')
done
$PY ../scripts/ssl_rules.py --dirs $D/rules_in --arms p93:SUP_100pct p93:SUPPF_100pct p93:MIMPF_100pct \
  --pairs p93:SUPPF_100pct=p93:SUP_100pct p93:MIMPF_100pct=p93:SUPPF_100pct p93:MIMPF_100pct=p93:SUP_100pct > $D/ssl_rules_opening1.txt
echo "local analysis written to $D"
