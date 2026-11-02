#!/bin/bash
# runner (2 Nov 2026): SKR2E pull + local scoring, after 'skr2e full end rc=0' (protocol_SKR2E §6; PF2E's out/ layout).
# 1. gaint: refuse unless run.log ends with 'skr2e full end rc=0' and out/skr2e_checks.json exists; add the record copies to out/
#    (skr2e_infer.py, skr2e_run.sh, run.log, run_full.log, out_gate/skr2e_gate.txt as skr2e_gate_dryrun.txt, the 10 members'
#    latest.pth md5s) and write out/MANIFEST.md5 over every file in out/; md5sum -c it there.
# 2. laptop: rsync out/ -> results/skr2e/raw (refuse if it exists), md5sum -c, MANIFEST md5 equal on both ends.
# 3. laptop: skr2e_boot.py 7520afc0 (asserted) -> results/skr2e/skr2e_boot_runner.txt (+ .err); local_md5.txt. To coach; no verdict.
set -u
T=/home/yugma/mtp/research/team_2026-10-31_next; R=$T/results/skr2e; G=noob@172.18.22.20; W=/home/noob/work/el_f3/reports/skr2e
SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"; PY=/home/yugma/mtp/research/.venv/bin/python; B=$T/scripts/skr2e/skr2e_boot.py
CX=/home/yugma/mtp/research/team_2026-10-29_features/scripts/e1_context.tsv
die(){ echo "[$(date '+%F %T')] skr2e post_local FAIL: $*"; exit 1; }
[ "$(md5sum < $B | cut -c1-8)" = 7520afc0 ] || die "skr2e_boot.py md5"
[ "$(md5sum < $CX | cut -c1-8)" = 12bd1385 ] || die "e1_context md5"
[ ! -e $R/raw ] || die "$R/raw exists"
M=$($SG "set -u; cd $W || exit 1; tail -n 1 run.log | grep -q 'skr2e full end rc=0' || { echo NOTDONE; exit 0; }
  [ -e out/skr2e_checks.json ] && [ ! -e out/MANIFEST.md5 ] || { echo BADSTATE; exit 0; }
  cp skr2e_infer.py skr2e_run.sh run.log run_full.log out/ && cp out_gate/skr2e_gate.txt out/skr2e_gate_dryrun.txt
  for r in /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s{5..9} /home/noob/work/el_thin/experiments/skr2_SKR01_100pct_s{5..9}; do md5sum \$r/checkpoints/latest.pth; done > out/member_latest_md5.txt
  (cd out && md5sum \$(ls | grep -v '^MANIFEST.md5\$') > MANIFEST.md5 && md5sum -c --quiet MANIFEST.md5 && echo OK \$(wc -l < MANIFEST.md5) \$(md5sum < MANIFEST.md5 | cut -c1-32))") || die "gaint ssh"
set -- $M; [ "${1:-}" = OK ] || die "gaint: $M"; N=$2; MM=$3
mkdir -p $R && rsync -a -e "ssh -o BatchMode=yes" $G:$W/out/ $R/raw/ || die "rsync"
(cd $R/raw && md5sum -c --quiet MANIFEST.md5) || die "laptop MANIFEST -c"
[ "$(md5sum < $R/raw/MANIFEST.md5 | cut -c1-32)" = "$MM" ] || die "MANIFEST md5 differs between ends"
echo "[$(date '+%F %T')] pulled out/ -> $R/raw: MANIFEST $MM ($N files), md5sum -c OK on gaint and laptop"
nice -n 10 $PY -B $B $R/raw $CX --singles $T/results/pf2/raw/m0 $T/results/s2/raw/m0/SKR01 > $R/skr2e_boot_runner.txt 2> $R/skr2e_boot_runner.err; rc=$?
(cd $R && md5sum skr2e_boot_runner.txt skr2e_boot_runner.err raw/MANIFEST.md5 > local_md5.txt)
echo "[$(date '+%F %T')] skr2e_boot 7520afc0 rc=$rc -> $R/skr2e_boot_runner.txt (to coach; no verdict to team-lead)"
exit $rc
