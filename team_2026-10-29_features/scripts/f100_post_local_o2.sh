#!/bin/bash
# protocol_100 opening 2, local analysis: pull gaint el_f3/reports/f100/post_opening2/ (MD5 checked) to results/f100/opening2/raw,
# re-check the local opening-1 comparator files (SUP100-g) against their manifest, then the CP contrast with Track M m2_rung:
#   C1 = CP100 - SUP100-g at tau 0 (default argmax), C2 = both arms at tau 1 (LA), C3 = CP100 tau 0 vs SUP100-g tau 1 (reported);
# ssl_rules cross-check on the rescore JSONs (f3_ mapped to p93_); E1 split + crack px on crack-free cells (f100_o1_extra.py);
# gpumem.log pulled for the m0 pass peak (finllm alone).
set -eu
cd /home/yugma/mtp/research/team_2026-10-29_features
D=results/f100/opening2; O1=results/f100/opening1; mkdir -p $D
rsync -a noob@172.18.22.20:/home/noob/work/el_f3/reports/f100/post_opening2/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "opening2 manifest OK $(wc -l < $D/raw/MANIFEST.md5) files"
(cd $O1/raw && md5sum -c --quiet MANIFEST.md5) && echo "opening1 comparator manifest OK (local copy unchanged)"
rsync -a noob@172.18.22.20:/home/noob/work/el_f3/reports/f100/gpumem.log $D/gpumem.log
A=$O1/raw/m0; B=$D/raw/m0; PY=/home/yugma/mtp/research/.venv/bin/python; R=../team_2026-10-24_go/trackM/scripts/m2_rung.py
S=(0 1 2 3 4)
fa(){ for k in "${S[@]}"; do echo $A/f3_SUP_100pct_s$k$1.json; done; }
fb(){ for k in "${S[@]}"; do echo $B/f3_CP_100pct_s$k$1.json; done; }
$PY $R --label C1_tau0 --a $(fa "") --b $(fb "") > $D/m2_rung_C1.txt 2>/dev/null
$PY $R --label C2_tau1 --a $(fa .tau1) --b $(fb .tau1) > $D/m2_rung_C2.txt 2>/dev/null
$PY $R --label C3_cp0_vs_supLA --a $(fa .tau1) --b $(fb "") > $D/m2_rung_C3.txt 2>/dev/null
rm -rf $D/rules_in; mkdir -p $D/rules_in
for f in $O1/raw/rescore/f3_SUP_100pct_s*.json $D/raw/rescore/f3_CP_100pct_s*.json; do
  sed 's/"\(test\|val\)\/f3_/"\1\/p93_/g' $f > $D/rules_in/$(basename $f | sed 's/^f3_/p93_/')
done
$PY ../scripts/ssl_rules.py --dirs $D/rules_in --arms p93:SUP_100pct p93:CP_100pct --pairs p93:CP_100pct=p93:SUP_100pct > $D/ssl_rules_opening2.txt
$PY scripts/f100_o1_extra.py $A scripts/e1_context.tsv SUP=$A CP=$B > $D/o2_extra.txt
echo "local analysis written to $D"
