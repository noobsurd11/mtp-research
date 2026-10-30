#!/bin/bash
# f2 local analysis (DDeP5 or CP5 vs the shared A5c-f1): pull gaint el_f2/reports/f2/post_<label>/ (MD5 checked), Track M rung
# analysis at tau 0 and tau 1 (A arm = the md5-verified MIM5 pull results/mim5/raw/m0/f1_A_5pct_s*.json: same scorer copies,
# masks and ext117), and the P-series rule cross-check on the rescore JSONs (f1_/f2_ run names mapped to p92_ for ssl_rules.py).
# Usage: f2_post_local.sh <label: ddep5|cp5> <B run prefix: f2_DDeP_5pct|f2_CP_5pct>
set -eu
cd /home/yugma/mtp/research/team_2026-10-29_features
LBL=$1; BR=$2; ARM=${BR#f2_}
D=results/$LBL; mkdir -p $D
(cd results/mim5/raw && md5sum -c --quiet MANIFEST.md5) && echo "A arm (MIM5 pull) manifest OK"
rsync -a noob@172.18.22.20:/home/noob/work/el_f2/reports/f2/post_$LBL/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "$LBL manifest OK $(wc -l < $D/raw/MANIFEST.md5) files"
A=results/mim5/raw/m0; B=$D/raw/m0
PY=/home/yugma/mtp/research/.venv/bin/python
$PY ../team_2026-10-24_go/trackM/scripts/m2_rung.py --label $LBL \
  --a $A/f1_A_5pct_s{0,1,2,3,4}.json --b $B/${BR}_s{0,1,2,3,4}.json > $D/m2_rung_$LBL.txt 2>/dev/null
$PY ../team_2026-10-24_go/trackM/scripts/m2_rung.py --label ${LBL}_LA1 \
  --a $A/f1_A_5pct_s{0,1,2,3,4}.tau1.json --b $B/${BR}_s{0,1,2,3,4}.tau1.json > $D/m2_rung_${LBL}_tau1.txt 2>/dev/null
rm -rf $D/rules_in; mkdir -p $D/rules_in
for f in results/mim5/raw/rescore/f1_A_5pct_s*.json $D/raw/rescore/${BR}_s*.json; do
  sed 's/"\(test\|val\)\/f[12]_/"\1\/p92_/g' $f > $D/rules_in/$(basename $f | sed 's/^f[12]_/p92_/')
done
$PY ../scripts/ssl_rules.py --dirs $D/rules_in --arms p92:A_5pct p92:$ARM --pairs p92:$ARM=p92:A_5pct > $D/ssl_rules_$LBL.txt
echo "local analysis written to $D"
