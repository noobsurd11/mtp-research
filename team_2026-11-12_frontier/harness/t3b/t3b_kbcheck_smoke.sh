#!/bin/bash
# AMENDMENT_1 smoke of kb_check (gaint CPU; nothing on cv02): stub deploys in a scratch dir, KB = git archive of K with a C-sorted
# CODE.md5 (as c3_deploy.sh in a clean shell), F2B = git archive of F2 with its CODE.md5 in ANOTHER line order (sorted by the
# en_US.UTF-8 locale, as F2's deploy shows on cv02, and reversed); kb_check is taken verbatim from each script (function, PINS,
# DW, KB lines) and run with R() executing locally with /tmp/noob_el/ mapped into the scratch dir.
#   registration-1 kb_check (evidence/amend1/t3b_queue.sh.reg1_cad952c0): must REFUSE both orders
#   amended kb_check (t3b_queue.sh): must PASS both orders
#   negatives for the amended one: one extra path in KB; one changed file outside K's paths in KB: each must REFUSE
# Usage: bash t3b_kbcheck_smoke.sh <out file>
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); KT=/home/noob/work/bench_wt_t3b
NEWQ=$HERE/t3b_queue.sh; OLDQ=$HERE/evidence/amend1/t3b_queue.sh.reg1_cad952c0
KC=$(grep -m1 '^KC=' $NEWQ | cut -d= -f2 | cut -d';' -f1); F2=9967d59abaab03cef83c1e3014840b2359ef45d7
S=/home/noob/work/bench_int_io/t3b/kbsmoke_$$; [ -e $S ] && exit 1; mkdir -p $S/noob_el
dep(){ # commit dir order
  mkdir -p $2 && git -C $KT archive $1 | tar -x -C $2 && echo $1 > $2/REVISION
  (cd $2 && find . -type f -printf '%P\n' | grep -vx CODE.md5 | case $3 in C) LC_ALL=C sort;; en) LC_ALL=en_US.UTF-8 sort;; rev) LC_ALL=C sort -r;; esac | xargs -d '\n' md5sum > CODE.md5); }
kbx(){ # script -> the kb_check result line
  { echo 'set -u'; grep -m1 '^KC=' $1; grep -m1 '^KB=' $1; sed -n '/^PINS="/,/"$/p' $1; grep -m1 '^DW=' $1
    echo "STEP=check; R(){ c=\${1//\\/tmp\\/noob_el\\//$S/noob_el/}; bash -c \"\$c\"; }; no(){ echo \"REFUSED (\$STEP): \$*\"; exit 1; }"
    sed -n '/^kb_check(){/,/echo "KB \$KB: REVISION K/p' $1; echo 'kb_check'; } > $S/kbx.sh
  bash $S/kbx.sh 2>&1 | tail -1 | cut -c1-150; }
nf=0; ck(){ case "$2" in REFUSED*) r=REFUSES;; *) r=PASSES;; esac; [ "$r" = "$3" ] && echo "OK    $1: $2" || { echo "FAIL  $1 (expected $3): $2"; nf=$((nf+1)); }; }
{
echo "t3b kb_check order smoke $(date '+%F %T'): K $KC, queue $(md5sum < $NEWQ | cut -c1-8), old $(md5sum < $OLDQ | cut -c1-8), script $(md5sum < $0 | cut -c1-8)"
dep $KC $S/noob_el/bench_${KC:0:7} C
for o in en rev; do rm -rf $S/noob_el/bench_9967d59; dep $F2 $S/noob_el/bench_9967d59 $o
  echo "-- F2B CODE.md5 order '$o' (first paths: $(head -2 $S/noob_el/bench_9967d59/CODE.md5 | awk '{print $2}' | tr '\n' ' ')), KB C order (first: $(head -2 $S/noob_el/bench_${KC:0:7}/CODE.md5 | awk '{print $2}' | tr '\n' ' '))"
  ck "registration-1 kb_check, order $o" "$(kbx $OLDQ)" REFUSES
  ck "amended kb_check, order $o" "$(kbx $NEWQ)" PASSES
done
KB=$S/noob_el/bench_${KC:0:7}
echo x > $KB/bench/t3b_extra.py; (cd $KB && find . -type f -printf '%P\n' | grep -vx CODE.md5 | LC_ALL=C sort | xargs -d '\n' md5sum > CODE.md5)
ck "amended kb_check, one extra path in KB" "$(kbx $NEWQ)" REFUSES
rm $KB/bench/t3b_extra.py; echo "# x" >> $KB/README.md; (cd $KB && find . -type f -printf '%P\n' | grep -vx CODE.md5 | LC_ALL=C sort | xargs -d '\n' md5sum > CODE.md5)
ck "amended kb_check, README.md changed in KB (outside K's paths)" "$(kbx $NEWQ)" REFUSES
echo "kb_check order smoke: $nf FAIL"
} 2>&1 | tee $OUT
rm -rf $S
grep -q "^kb_check order smoke: 0 FAIL" $OUT
