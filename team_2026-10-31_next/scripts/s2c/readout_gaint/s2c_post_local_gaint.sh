#!/bin/bash
# SKR2C opening (E1 opening #7), pull + readout ON GAINT (team-lead, 14 Nov 2026). NOT part of the frozen set.
# = the frozen scripts/s2c/opening/local/s2c_post_local.sh (1da9a692, FROZEN 836be7e5) with the changes that the move of the orchestrator
# from the laptop to gaint forces (review_s2c_stage2.md note N1: the frozen file must run on the laptop and stops at its first check here):
#  (1) transport: post/ and d_out/ are copied locally (rsync -a, no ssh); the same checks stay: end line, md5sum -c of both MANIFESTs at
#      the source and at the copy, MANIFEST md5s equal on both ends;
#  (2) python: the laptop venv does not exist here; the house venv python on gaint (3.12.3, numpy 2.5.2) is used, CUDA hidden, -B.
#      Checked before use (results/s2c/local/env_check.txt): s2c_d_boot.py --selftest = SELFTEST PASS (reproduces openings #4 and #6
#      line by line) and m2_rung on opening #5's files = byte-identical to the laptop outputs of 3 Nov (tau 0 and tau 1);
#  (3) N1: m1_analyze.py 8e566254 and m0_analyze.py d5adbe6b pinned too; the D self-test must print SELFTEST PASS or nothing is read;
#  (4) m2_rung stderr goes to .err files (the frozen file sent it to /dev/null, which hid a failure under set -e).
# Every scoring command (m2_rung calls, the collected-outputs block, the s2c_d_boot.py call) is the frozen file's, unchanged.
# The frozen s2c_d_boot.py (164ef377) and the frozen script itself are still md5-checked against FROZEN.md5.
# Usage: bash s2c_post_local_gaint.sh <FROZEN.md5 md5, 32 hex>
set -eu
R=/home/yugma/mtp/research; T=$R/team_2026-10-31_next; D=$T/results/s2c; RR=$D/raw_r; RD=$D/raw_d; O=$D/local; OP=$T/scripts/s2c/opening
G=/home/noob/work/s2c
PYB=/home/noob/work/el-fault-detection/.venv/bin/python
PY="env CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 $PYB"
M2=$R/team_2026-10-24_go/trackM/scripts/m2_rung.py; M1=$R/team_2026-10-24_go/trackM/scripts/m1_analyze.py; M0=$R/team_2026-10-24_go/trackM/scripts/m0_analyze.py
B=$OP/local/s2c_d_boot.py
CX=$R/team_2026-10-29_features/scripts/e1_context.tsv
FZ=${1:?registered FROZEN.md5 md5 (32 hex)}
die(){ echo "[$(date '+%F %T')] s2c post_local(gaint) FAIL: $*"; exit 1; }
[ "$(hostname)" = giant ] || die "this copy runs on gaint only"
[ "$(md5sum < $OP/FROZEN.md5 | cut -c1-32)" = "$FZ" ] || die "local FROZEN.md5 md5 != $FZ"
cmp -s $OP/FROZEN.md5 $G/open/FROZEN.md5 || die "project FROZEN.md5 != gaint open/FROZEN.md5"
(cd $OP && grep -E '  (local/s2c_post_local.sh|local/s2c_d_boot.py)$' FROZEN.md5 | md5sum -c --quiet) || die "local opening set != FROZEN.md5"
[ "$(md5sum < $M2 | cut -c1-8)" = 0ae9d505 ] || die "m2_rung.py md5"
[ "$(md5sum < $M1 | cut -c1-8)" = 8e566254 ] || die "m1_analyze.py md5 (N1)"
[ "$(md5sum < $M0 | cut -c1-8)" = d5adbe6b ] || die "m0_analyze.py md5 (N1)"
[ "$(md5sum < $CX | cut -c1-8)" = 12bd1385 ] || die "e1_context md5"
[ ! -e $RR ] && [ ! -e $RD ] && [ ! -e $O ] || die "$RR, $RD or $O exists (refuse to overwrite)"
tail -n 1 $G/opening.log | grep -q 's2c opening done: R rc=0 D rc=0$' || die "gaint: NOTDONE"
(cd $G/post && md5sum -c --quiet MANIFEST.md5) && (cd $G/d_out && md5sum -c --quiet MANIFEST.md5) || die "gaint: BADMANIFEST"
MR=$(md5sum < $G/post/MANIFEST.md5 | cut -c1-32); MD=$(md5sum < $G/d_out/MANIFEST.md5 | cut -c1-32)
mkdir -p $D
# N1: the D scorer's self-test on already-opened files (#4 PF2E, #6 SKR2E), before anything of this opening is read
ST=$D/env_check.txt
{ echo "[$(date '+%F %T')] env: $($PYB -c 'import sys, numpy; print("python", sys.version.split()[0], "numpy", numpy.__version__)') on $(hostname)"
  $PY -B $B --selftest $T/results/pf2e/raw $T/results/pf2e/pf2e_boot_runner.txt $CX $T/results/pf2/raw/m0 $T/results/skr2e/raw $T/results/skr2e/skr2e_boot_runner.txt; } > $ST 2> $D/env_check.err || die "s2c_d_boot --selftest rc != 0"
[ "$(tail -n 1 $ST)" = "SELFTEST PASS" ] || die "s2c_d_boot --selftest did not end with SELFTEST PASS"
rsync -a $G/post/ $RR/ || die "rsync post/"
rsync -a $G/d_out/ $RD/ || die "rsync d_out/"
(cd $RR && md5sum -c --quiet MANIFEST.md5) || die "project raw_r MANIFEST -c"
(cd $RD && md5sum -c --quiet MANIFEST.md5) || die "project raw_d MANIFEST -c"
[ "$(md5sum < $RR/MANIFEST.md5 | cut -c1-32)" = "$MR" ] && [ "$(md5sum < $RD/MANIFEST.md5 | cut -c1-32)" = "$MD" ] || die "MANIFEST md5 differs between ends"
echo "[$(date '+%F %T')] copied post/ -> $RR (MANIFEST $MR) and d_out/ -> $RD (MANIFEST $MD); md5sum -c OK at source and copy"
mkdir -p $O
mv $ST $D/env_check.err $O/
md5sum $M2 $B $CX $M1 $M0 > $O/tools_md5.txt
A=$(for k in 10 11 12 13 14; do echo $RR/m0/SUPPF/s2c_SUPPF_100pct_s$k.json; done)
B_SKR=$(for k in 10 11 12 13 14; do echo $RR/m0/SKR01/s2c_SKR01_100pct_s$k.json; done)
$PY -B $M2 --label SKR01_vs_SUPPF --a $A --b $B_SKR > $O/m2_rung_SKR01.txt 2> $O/m2_rung_SKR01.err
$PY -B $M2 --label SKR01_vs_SUPPF_LA1 --a $(echo $A | sed 's/\.json/.tau1.json/g') --b $(echo $B_SKR | sed 's/\.json/.tau1.json/g') > $O/m2_rung_SKR01_tau1.txt 2> $O/m2_rung_SKR01_tau1.err
$PY -B $M2 --label SKR01_vs_SUPPF_scuffign --a $(echo $A | sed 's#/m0/SUPPF/\(.*\)\.json#/m0_scuffign/SUPPF/\1.scuffign.json#g') \
  --b $(echo $B_SKR | sed 's#/m0/SKR01/\(.*\)\.json#/m0_scuffign/SKR01/\1.scuffign.json#g') > $O/m2_rung_SKR01_scuffign.txt 2> $O/m2_rung_SKR01_scuffign.err || echo "scuffign m2_rung rc != 0 (reported only)"
{
  echo "# SKR2C opening (E1 opening #7; same 50 test and 106 E1 cells as #5 / #6, 3rd look): opening outputs collected by runner (frozen opening code wrote them; runner did not recompute these)"
  echo "# raw_r MANIFEST $MR; raw_d MANIFEST $MD; $(date '+%F %T')"
  for f in decision_rc.txt extra_rc.txt comparator_check.txt init_check.txt realsplits.txt e1_coprim_selftest.txt e1_coprim.txt b5/b5w_table.txt \
           guards_selftest.txt guards.txt named_boot_selftest.txt named_boot.txt enc_cosine_20k.txt cellgate/s2_cellgate.txt tau0_check_SKR01.txt tau0_check_SUPPF.txt; do
    echo; if [ -e $RR/$f ]; then echo "=================== $f ($(md5sum < $RR/$f | cut -c1-8))"; cat $RR/$f; else echo "=================== $f MISSING"; fi
  done
  for f in s2c_d_gate.txt s2c_d_checks.txt d_realsplits.txt; do
    echo; if [ -e $RD/$f ]; then echo "=================== D $f ($(md5sum < $RD/$f | cut -c1-8))"; cat $RD/$f; else echo "=================== D $f MISSING"; fi
  done
} > $O/opening_outputs.txt
rc=0; nice -n 10 $PY -B $B $RD $CX --singles $RR/m0/SUPPF $RR/m0/SKR01 --json $O/d_verdict.json > $O/d_boot.txt 2> $O/d_boot.err || rc=$?
(cd $O && md5sum $(ls *.txt *.json 2>/dev/null)) > $D/local_md5.txt
echo "[$(date '+%F %T')] local readout written to $O (s2c_d_boot rc=$rc; verdicts only after coach's independent recompute)"
exit $rc
