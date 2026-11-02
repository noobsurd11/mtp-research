#!/bin/bash
# runner DRAFT (1 Nov 2026; coach 23:5x, protocol_B6 §9 cv02 fallback; NOT frozen): after cv02's 'b6 scoring done: rc=0', relay
# cv02 B/score/{out/, score.log, gpumem.log} to gaint /home/noob/work/b6_score/ THROUGH THE LAPTOP (tar stream; no key on cv02,
# never ssh -A), md5 on both ends (SCORERELAY.md5), so b6_post_local.sh 08db9dbf runs unchanged (it reads gaint b6_score/out and
# the 'b6 scoring done: rc=0' line in gaint b6_score/score.log). The run dirs (metrics.json, RELAY.md5) go by b6_relay.sh a23ab50d
# as planned. Refuses if gaint b6_score/out or score.log exists. Log results/b6/fallback_relay.log. rc captured before $(date).
set -u
C=cv02@10.8.1.106; G=noob@172.18.22.20; W=/tmp/noob_el/el_b6/score; GW=/home/noob/work/b6_score
LOG=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/fallback_relay.log
SC="ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $C"; SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"
say(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
die(){ say "score relay FAIL: $*"; exit 1; }
say "score relay start (cv02 $W -> gaint $GW)"
$SG "[ ! -e $GW/out ] && [ ! -e $GW/score.log ]" || die "gaint $GW/out or score.log exists"
R=$($SC "cd $W && grep -q 'b6 scoring done: rc=0' score.log && [ ! -e wrapper.pid ] && (cd out && md5sum -c --quiet MANIFEST.md5) \
  && { find out -type f; echo score.log; echo gpumem.log; } | sort | xargs md5sum > SCORERELAY.md5 \
  && echo OK \$(wc -l < SCORERELAY.md5) \$(md5sum < SCORERELAY.md5 | cut -c1-32) \$(ls out/*.b6.json | wc -l)") || die "cv02 check / manifest failed"
set -- $R; [ "${1:-}" = OK ] || die "cv02: $R"; [ "${4:-0}" = 20 ] || die "cv02 has ${4:-0} score files"
NF=$2; M=$3; say "cv02 SCORERELAY.md5 $M ($NF files)"
$SC "cd $W && tar cf - out score.log gpumem.log SCORERELAY.md5" | $SG "mkdir -p $GW && tar xf - -C $GW"
rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || die "stream rc $rc"
V=$($SG "cd $GW && md5sum -c --quiet SCORERELAY.md5 >/dev/null 2>&1; r=\$?; echo \$r \$(md5sum < SCORERELAY.md5 | cut -c1-32)")
set -- $V; [ "${1:-1}" = 0 ] || die "gaint md5sum -c rc ${1:-?}"; [ "${2:-}" = "$M" ] || die "SCORERELAY.md5 differs on gaint"
say "score relay done: rc=0 ($NF files, md5sum -c OK on gaint, SCORERELAY.md5 $M both ends)"
