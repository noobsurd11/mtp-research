#!/bin/bash
# MIM5 local analysis: pull gaint post outputs (MD5 checked), Track M rung analysis (cell sets, per source, bootstrap,
# E1 ext), and the P-series rule cross-check on the rescore JSONs (run names mapped f1_ -> p91_ for ssl_rules.py).
set -eu
cd /home/yugma/mtp/research/team_2026-10-29_features
D=results/mim5; mkdir -p $D
rsync -a noob@172.18.22.20:/home/noob/work/el_f1/reports/f1/post/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "manifest OK"
M=$D/raw/m0
PY=/home/yugma/mtp/research/.venv/bin/python
$PY ../team_2026-10-24_go/trackM/scripts/m2_rung.py --label MIM5 \
  --a $M/f1_A_5pct_s{0,1,2,3,4}.json --b $M/f1_MIM_5pct_s{0,1,2,3,4}.json > $D/m2_rung_mim5.txt
mkdir -p $D/rules_in
for f in $D/raw/rescore/*.json; do sed 's/"\(test\|val\)\/f1_/"\1\/p91_/g' $f > $D/rules_in/$(basename $f | sed 's/^f1_/p91_/'); done
$PY ../scripts/ssl_rules.py --dirs $D/rules_in --arms p91:A_5pct p91:MIM_5pct --pairs p91:MIM_5pct=p91:A_5pct > $D/ssl_rules_mim5.txt
echo "local analysis written to $D"
