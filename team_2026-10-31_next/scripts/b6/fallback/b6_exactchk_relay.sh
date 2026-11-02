#!/bin/bash
# runner DRAFT (1 Nov 2026; coach 23:5x, protocol_B6 §9 cv02 fallback; NOT frozen, NOT armed; only if the user says 'no gaint'):
# relay the inputs of builder's scorer exact check from gaint to cv02 THROUGH THE LAPTOP (tar stream; no key on cv02, never ssh -A).
# 1. gaint staging dir ST (fresh): runs/f3_SUPPF_100pct_s0/config_used.yaml = builder's check config (b6_build/check/runs/...) with
#    ONLY its '  root:' line changed to the cv02 check root (diff recorded); checkpoints/latest.pth = symlink to el_f3's file
#    (tar -h streams the content); valroot/splits/{train,val,test}.txt = builder's (842f27c4 / 9dcccf00 / 9dcccf00);
#    m0val_f3_SUPPF_100pct_s0.json = the opening-1 m0 file (d7e93dff) with cells reduced to the 'val' block (b6_valcmp indexes
#    only cells['val']), so no test / E1 cell reaches cv02; EXACTCHK.md5 over all of it.
# 2. stream gaint 'tar chf - -C ST .' | cv02 'tar xf - -C B/exactchk' (refuses if it exists); 3. cv02 md5sum -c EXACTCHK.md5 and
#    the EXACTCHK.md5 md5 equal on both ends. valroot/labeled -> B/b6_data/labeled (the deployed 532 stems) is made on cv02 by
#    b6_cv02_exactchk.sh. Log results/b6/fallback_relay.log. rc captured before $(date).
set -u
C=cv02@10.8.1.106; G=noob@172.18.22.20; B=/tmp/noob_el/el_b6; ST=/home/noob/work/runner_b6chk/cv02_stage
LOG=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/fallback_relay.log
SC="ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $C"; SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"
say(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
die(){ say "exactchk relay FAIL: $*"; exit 1; }
say "exactchk relay start"
$SC "[ ! -e $B/exactchk ] && [ -d $B/b6_data/labeled ]" || die "cv02: $B/exactchk exists or $B/b6_data/labeled missing (deploy first)"
R=$($SG "set -e; K=/home/noob/work/b6_build/check; M0=/home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json
  [ ! -e $ST ]; [ \"\$(md5sum < \$M0 | cut -c1-8)\" = d7e93dff ]
  [ \"\$(md5sum < \$K/valroot/splits/train.txt | cut -c1-8)\" = 842f27c4 ] && [ \"\$(md5sum < \$K/valroot/splits/val.txt | cut -c1-8)\" = 9dcccf00 ] && [ \"\$(md5sum < \$K/valroot/splits/test.txt | cut -c1-8)\" = 9dcccf00 ]
  mkdir -p $ST/runs/f3_SUPPF_100pct_s0/checkpoints $ST/valroot/splits
  cp \$K/valroot/splits/*.txt $ST/valroot/splits/
  sed 's|^  root: /home/noob/work/b6_build/check/valroot\$|  root: $B/exactchk/valroot|' \$K/runs/f3_SUPPF_100pct_s0/config_used.yaml > $ST/runs/f3_SUPPF_100pct_s0/config_used.yaml
  d=\$(diff \$K/runs/f3_SUPPF_100pct_s0/config_used.yaml $ST/runs/f3_SUPPF_100pct_s0/config_used.yaml | grep -c '^[<>]' || true); [ \"\$d\" = 2 ]
  diff \$K/runs/f3_SUPPF_100pct_s0/config_used.yaml $ST/runs/f3_SUPPF_100pct_s0/config_used.yaml > $ST/config_root.diff || true
  ln -s \$(readlink -f \$K/runs/f3_SUPPF_100pct_s0/checkpoints/latest.pth) $ST/runs/f3_SUPPF_100pct_s0/checkpoints/latest.pth
  python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); d[\"cells\"]={\"val\": d[\"cells\"][\"val\"]}; d[\"sets_scored\"]=[\"val\"]; json.dump(d, open(sys.argv[2], \"w\"))' \$M0 $ST/m0val_f3_SUPPF_100pct_s0.json
  cd $ST && find -L . -type f ! -name EXACTCHK.md5 | sort | xargs md5sum > EXACTCHK.md5
  echo OK \$(wc -l < EXACTCHK.md5) \$(md5sum < EXACTCHK.md5 | cut -c1-32) \$(md5sum < m0val_f3_SUPPF_100pct_s0.json | cut -c1-8) \$(md5sum < runs/f3_SUPPF_100pct_s0/checkpoints/latest.pth | cut -c1-8)") \
  || die "gaint staging failed"
set -- $R; [ "${1:-}" = OK ] || die "gaint staging: $R"
NF=$2; M=$3; say "gaint staged: EXACTCHK.md5 $M ($NF files; m0val $4; latest.pth $5)"
$SG "tar chf - -C $ST ." | $SC "mkdir -p $B/exactchk && tar xf - -C $B/exactchk"
rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || die "stream rc $rc"
V=$($SC "cd $B/exactchk && md5sum -c --quiet EXACTCHK.md5 >/dev/null 2>&1; r=\$?; echo \$r \$(md5sum < EXACTCHK.md5 | cut -c1-32); [ ! -L runs/f3_SUPPF_100pct_s0/checkpoints/latest.pth ] && echo REAL")
set -- $V; [ "${1:-1}" = 0 ] || die "cv02 md5sum -c rc ${1:-?}"; [ "${2:-}" = "$M" ] || die "EXACTCHK.md5 differs on cv02"
[ "${3:-}" = REAL ] || die "latest.pth arrived as a symlink"
say "exactchk relay done: rc=0 ($NF files, md5sum -c OK on cv02, EXACTCHK.md5 $M both ends)"
