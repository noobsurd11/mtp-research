#!/bin/bash
# SKR2C opening (E1 opening #7), LOCAL pull + readout on the laptop, after the driver's end line '... s2c opening done: R rc=0 D rc=0'.
# = s2_post_local.sh 0ec30d37 (readout part) + skr2e_post_local.sh (pull pattern), minimal diff: arms SKR01 vs SUPPF, BOTH fresh (s10-14,
# from this opening's m0, no comparator reuse); HC2 rows out; the pull of post/ and d_out/ (MANIFEST md5sum -c on gaint and laptop, equal
# md5s both ends); scuff-ignored m2_rung (reported); the collected file list of the SKR2C opening; the D scorer local/s2c_d_boot.py.
# Usage: bash s2c_post_local.sh <FROZEN.md5 md5, 32 hex>   (the registered one; the local copy scripts/s2c/opening/FROZEN.md5 must match)
# 1. local frozen check: md5 of the local FROZEN.md5 = the argument; md5sum -c of the local opening set (this script, s2c_d_boot.py);
#    m2_rung 0ae9d505 and e1_context 12bd1385 asserted;
# 2. gaint: refuse unless opening.log's last line is 's2c opening done: R rc=0 D rc=0'; md5sum -c post/MANIFEST.md5 and d_out/MANIFEST.md5;
# 3. laptop: rsync post/ -> results/s2c/raw_r, d_out/ -> results/s2c/raw_d (refuse if either exists), md5sum -c, MANIFEST md5s equal;
# 4. test co-primaries SKR01 vs SUPPF (fresh): Track M m2_rung at tau 0 (verdict primaries; default .json = tau0, see raw_r/tau0_check_*)
#    and tau 1 (LA, reported), scuff-ignored (reported);
# 5. the opening's frozen decision / reported text outputs, as written by the opening, collected into one readout file;
# 6. verdict D: s2c_d_boot.py on raw_d (+ --singles = R's fresh m0, --json). Output results/s2c/local/ + local_md5.txt.
# coach recomputes on his own; no verdict to team-lead before that.
set -eu
R=/home/yugma/mtp/research; T=$R/team_2026-10-31_next; D=$T/results/s2c; RR=$D/raw_r; RD=$D/raw_d; O=$D/local; OP=$T/scripts/s2c/opening
PY=$R/.venv/bin/python; M2=$R/team_2026-10-24_go/trackM/scripts/m2_rung.py; B=$OP/local/s2c_d_boot.py
CX=$R/team_2026-10-29_features/scripts/e1_context.tsv
FZ=${1:?registered FROZEN.md5 md5 (32 hex)}
die(){ echo "[$(date '+%F %T')] s2c post_local FAIL: $*"; exit 1; }
[ "$(md5sum < $OP/FROZEN.md5 | cut -c1-32)" = "$FZ" ] || die "local FROZEN.md5 md5 != $FZ"
(cd $OP && grep -E '  (local/s2c_post_local.sh|local/s2c_d_boot.py)$' FROZEN.md5 | md5sum -c --quiet) || die "local opening set != FROZEN.md5"
[ "$(md5sum < $M2 | cut -c1-8)" = 0ae9d505 ] || die "m2_rung.py md5"
[ "$(md5sum < $CX | cut -c1-8)" = 12bd1385 ] || die "e1_context md5"
[ ! -e $RR ] && [ ! -e $RD ] && [ ! -e $O ] || die "$RR, $RD or $O exists (refuse to overwrite)"
G=""; for h in noob@172.18.22.20 ssh.noobsurd.info; do ssh -n -o BatchMode=yes -o ConnectTimeout=20 $h true 2>/dev/null && { G=$h; break; }; done
[ -n "$G" ] || die "gaint not reachable"
M=$(ssh -n -o BatchMode=yes $G "set -u; cd /home/noob/work/s2c || exit 1
  tail -n 1 opening.log | grep -q 's2c opening done: R rc=0 D rc=0\$' || { echo NOTDONE; exit 0; }
  (cd post && md5sum -c --quiet MANIFEST.md5) && (cd d_out && md5sum -c --quiet MANIFEST.md5) || { echo BADMANIFEST; exit 0; }
  echo OK \$(md5sum < post/MANIFEST.md5 | cut -c1-32) \$(md5sum < d_out/MANIFEST.md5 | cut -c1-32)") || die "gaint ssh"
set -- $M; [ "${1:-}" = OK ] || die "gaint: $M"; MR=$2; MD=$3
mkdir -p $D
rsync -a -e "ssh -o BatchMode=yes" $G:/home/noob/work/s2c/post/ $RR/ || die "rsync post/"
rsync -a -e "ssh -o BatchMode=yes" $G:/home/noob/work/s2c/d_out/ $RD/ || die "rsync d_out/"
(cd $RR && md5sum -c --quiet MANIFEST.md5) || die "laptop raw_r MANIFEST -c"
(cd $RD && md5sum -c --quiet MANIFEST.md5) || die "laptop raw_d MANIFEST -c"
[ "$(md5sum < $RR/MANIFEST.md5 | cut -c1-32)" = "$MR" ] && [ "$(md5sum < $RD/MANIFEST.md5 | cut -c1-32)" = "$MD" ] || die "MANIFEST md5 differs between ends"
echo "[$(date '+%F %T')] pulled post/ -> $RR (MANIFEST $MR) and d_out/ -> $RD (MANIFEST $MD); md5sum -c OK on gaint and laptop"
mkdir -p $O
md5sum $M2 $B $CX > $O/tools_md5.txt
A=$(for k in 10 11 12 13 14; do echo $RR/m0/SUPPF/s2c_SUPPF_100pct_s$k.json; done)
B_SKR=$(for k in 10 11 12 13 14; do echo $RR/m0/SKR01/s2c_SKR01_100pct_s$k.json; done)
$PY -B $M2 --label SKR01_vs_SUPPF --a $A --b $B_SKR > $O/m2_rung_SKR01.txt 2>/dev/null
$PY -B $M2 --label SKR01_vs_SUPPF_LA1 --a $(echo $A | sed 's/\.json/.tau1.json/g') --b $(echo $B_SKR | sed 's/\.json/.tau1.json/g') > $O/m2_rung_SKR01_tau1.txt 2>/dev/null
$PY -B $M2 --label SKR01_vs_SUPPF_scuffign --a $(echo $A | sed 's#/m0/SUPPF/\(.*\)\.json#/m0_scuffign/SUPPF/\1.scuffign.json#g') \
  --b $(echo $B_SKR | sed 's#/m0/SKR01/\(.*\)\.json#/m0_scuffign/SKR01/\1.scuffign.json#g') > $O/m2_rung_SKR01_scuffign.txt 2>/dev/null || echo "scuffign m2_rung rc != 0 (reported only)"
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
