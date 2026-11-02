#!/bin/bash
# runner DRAFT (1 Nov 2026; coach ruling 23:4x: B6 scoring on gaint's GPU after relaying the runs with md5 on both ends): relay the
# 20 B6 run dirs from cv02 to gaint THROUGH THE LAPTOP (tar stream ssh cv02 | ssh gaint; nothing stored on the laptop, ~10 GB;
# no key on cv02, never ssh -A). Run on the laptop, in the foreground or as a tracked background task.
# Steps (any failure stops with a FAIL line, nothing deleted anywhere):
#  1. cv02 (read-only): q/launch.log has 'B6 ALL TRAINED (20 rc 0 of 20)', no recorded B6 python pid alive and the gpumem
#     logger stopped (no writer);
#     writes q/RELAY.md5 = md5sum of every file under experiments/b6_{SUP,SUPPF}_f*_s* + experiments/b6_*.stdout + REVISION + q/*.log
#     + q/b6_jobs.txt (b6_id* identity runs excluded); prints its md5.
#  2. stream: cv02 'tar cf - <same files> q/RELAY.md5' | gaint 'tar xf - -C DD' (DD must not exist yet).
#  3. gaint: md5sum -c q/RELAY.md5 in DD (all files), md5 of RELAY.md5 equal on both ends, 20 latest.pth present.
#  Log: results/b6/relay.log (laptop). rc captured before $(date).
set -u
C=cv02@10.8.1.106; G=noob@172.18.22.20; RB=/tmp/noob_el/el_b6; DD=${DD:-/home/noob/work/cv02_noob_el/el_b6}
LOG=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/relay.log
SC="ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $C"; SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"
say(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
die(){ say "relay FAIL: $*"; exit 1; }
say "relay start (cv02 $RB -> gaint $DD)"
$SG "[ ! -e $DD ]" || die "gaint $DD exists (refuse to overwrite)"
R=$($SC "cd $RB && grep -q 'B6 ALL TRAINED (20 rc 0 of 20)' q/launch.log || { echo NOTDONE; exit 0; }
  for f in q/pids/b6_*.pid; do [ -e \"\$f\" ] && kill -0 \"\$(cat \$f)\" 2>/dev/null && { echo ALIVE \$f; exit 0; }; done
  [ -e q/gpumem.pid ] && kill -0 \"\$(cat q/gpumem.pid)\" 2>/dev/null && { echo GPUMEM_ALIVE; exit 0; }
  ls -d experiments/b6_SUP_f?_s? experiments/b6_SUPPF_f?_s? | wc -l > q/relay_ndirs.txt
  { find experiments -maxdepth 1 -name 'b6_S*.stdout'; find experiments/b6_SUP_f?_s? experiments/b6_SUPPF_f?_s? -type f; echo REVISION; echo q/b6_jobs.txt; ls q/*.log; } \
    | sort > q/relay_files.txt && xargs -d '\n' md5sum < q/relay_files.txt > q/RELAY.md5 && echo OK \$(cat q/relay_ndirs.txt) \$(wc -l < q/RELAY.md5) \$(md5sum < q/RELAY.md5 | cut -c1-32)") \
  || die "cv02 step 1 ssh failed"
set -- $R; [ "${1:-}" = OK ] || die "cv02 step 1: $R"
[ "$2" = 20 ] || die "cv02: $2 run dirs, expected 20"
NF=$3; M=$4; say "cv02 RELAY.md5 $M ($NF files, 20 run dirs)"
$SC "cd $RB && tar cf - -T q/relay_files.txt q/RELAY.md5" | $SG "mkdir -p $DD && tar xf - -C $DD"
rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || die "stream rc $rc (cv02 tar / gaint tar)"
say "stream done; verifying on gaint"
V=$($SG "cd $DD && md5sum -c --quiet q/RELAY.md5 >/dev/null 2>&1; r=\$?; echo \$r \$(md5sum < q/RELAY.md5 | cut -c1-32) \$(ls experiments/b6_S*_f?_s?/checkpoints/latest.pth | wc -l)")
set -- $V
[ "${1:-1}" = 0 ] || die "gaint md5sum -c rc ${1:-?}"
[ "${2:-}" = "$M" ] || die "RELAY.md5 differs on gaint (${2:-?} vs $M)"
[ "${3:-0}" = 20 ] || die "gaint has ${3:-0} latest.pth, expected 20"
say "relay done: rc=0 ($NF files, md5sum -c OK on gaint, RELAY.md5 $M both ends, 20 latest.pth)"
