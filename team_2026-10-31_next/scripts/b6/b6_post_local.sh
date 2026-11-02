#!/bin/bash
# runner DRAFT (1 Nov 2026): B6 local verdict pass after gaint's 'b6 scoring done: rc=0' (build_b6 c81d35cc §7; protocol_B6 §4/§9).
# 1. pull gaint /home/noob/work/b6_score/out (20 *.b6.json + score.stdout + MANIFEST.md5) -> results/b6/scores, md5sum -c;
# 2. pull the 20 relayed runs' metrics.json (trainer's end-of-run TEST block = the held-out fold; judge item 7 cross-check)
#    -> results/b6/metrics/<run>.metrics.json, each md5 == its line in the relayed q/RELAY.md5;
# 3. b6_verdict.py 6d807784 (stdlib) with the pinned folds e2cafce1 / groups 5ff33e20 / forbidden 9bb4d919
#    -> results/b6/verdict/b6_verdict.* ; the output goes to coach for the independent recompute; no verdict to team-lead before it.
# Reads no test or E1 file. rc captured before $(date). Usage: bash b6_post_local.sh
set -u
T=/home/yugma/mtp/research/team_2026-10-31_next; R=$T/results/b6; G=noob@172.18.22.20; DD=/home/noob/work/cv02_noob_el/el_b6
SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"; V=$T/scripts/b6/b6_verdict.py; LOG=$R/post_local.log
say(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
die(){ say "b6 post_local FAIL: $*"; exit 1; }
[ "$(md5sum < $V | cut -c1-8)" = 6d807784 ] || die "b6_verdict.py md5"
[ "$(md5sum < $R/b6_folds.tsv | cut -c1-8)" = e2cafce1 ] && [ "$(md5sum < $T/judge/out/b6_groups.tsv | cut -c1-8)" = 5ff33e20 ] \
  && [ "$(md5sum < $R/b6_forbidden.txt | cut -c1-8)" = 9bb4d919 ] || die "folds / groups / forbidden md5"
[ ! -e $R/scores ] && [ ! -e $R/verdict ] || die "results/b6/scores or verdict exists"
$SG "grep -q 'b6 scoring done: rc=0' /home/noob/work/b6_score/score.log" || die "no 'b6 scoring done: rc=0' on gaint"
mkdir -p $R/scores $R/metrics $R/verdict
rsync -a -e "ssh -o BatchMode=yes" $G:/home/noob/work/b6_score/out/ $R/scores/; rc=$?; [ $rc = 0 ] || die "rsync scores rc $rc"
(cd $R/scores && md5sum -c --quiet MANIFEST.md5) || die "scores MANIFEST check"
[ "$(ls $R/scores/*.b6.json | wc -l)" = 20 ] || die "not 20 score files"
rsync -a -e "ssh -o BatchMode=yes" $G:$DD/q/RELAY.md5 $R/metrics/RELAY.md5 || die "rsync RELAY.md5"
M=()
for n in $(cut -d'|' -f1 $T/results/b6/jobs/b6_jobs.txt); do
  rsync -a -e "ssh -o BatchMode=yes" $G:$DD/experiments/$n/metrics.json $R/metrics/$n.metrics.json || die "rsync metrics $n"
  e=$(grep " experiments/$n/metrics.json\$" $R/metrics/RELAY.md5 | cut -c1-32); [ -n "$e" ] || die "$n metrics.json not in RELAY.md5"
  [ "$(md5sum < $R/metrics/$n.metrics.json | cut -c1-32)" = "$e" ] || die "$n metrics.json md5 != RELAY.md5"
  M+=($R/metrics/$n.metrics.json)
done
python3 -I $V --scores $R/scores --folds $R/b6_folds.tsv --groups $T/judge/out/b6_groups.tsv --forbidden $R/b6_forbidden.txt \
  --out $R/verdict/b6_verdict --metrics "${M[@]}" > $R/verdict/b6_verdict.stdout 2>&1; rc=$?
[ $rc = 0 ] || die "b6_verdict rc $rc (see verdict/b6_verdict.stdout)"
(cd $R/verdict && md5sum * > ../verdict_local_md5.txt)
say "b6 post_local done: rc=0 (scores MANIFEST $(md5sum < $R/scores/MANIFEST.md5 | cut -c1-8), 20 metrics.json = RELAY.md5, verdict files in results/b6/verdict) -> coach"
