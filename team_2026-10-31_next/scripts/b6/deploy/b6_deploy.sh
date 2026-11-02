#!/bin/bash
# runner DRAFT (1 Nov 2026): B6 cv02 deploy (coach's launch order: qualifying snapshot -> THIS (deploy + md5s) -> A6000 identity PASS
# -> arm queue; any failed step stops B6). Runs on the laptop. No key on cv02, never ssh -A; everything cv02-bound is relayed
# gaint -> laptop -> cv02 as a tar stream (nothing stored on the laptop beyond the 15 small frozen files already here).
# 0. laptop: md5sum -c results/b6/FROZEN_B6.md5 (807d4d03) + b6_valcmp.py 1ad95d68.
# 1. cv02 read-only snapshot: >= 3 GPUs with no process > 4,096 MiB (else stop: B6 not run); B absent; env.sh + venv present.
# 2. laptop -> gaint: the frozen files (+ exp/*.txt, b6_valcmp.py) at their relative paths into R/frozen_in (R/frozen_in absent);
#    b6_stage_gaint.sh + b6_verify_cv02.sh into R; gaint runs b6_stage_gaint.sh (prints OK n md5).
# 3. stream gaint 'tar cf - -C ST .' | cv02 'tar xf - -C B'.
# 4. cv02 runs B/bin/b6_verify_cv02.sh: DEPLOY.md5 -c (same md5 as gaint's), CODE / FROZEN / EXP / ROOTS / per-root SPLITS +
#    DATA_MANIFEST -c, labeled symlinks, 0 forbidden stems, R34 weights md5, venv. Log results/b6/deploy.log. rc before $(date).
set -u
T=/home/yugma/mtp/research/team_2026-10-31_next; D=$T/scripts/b6/deploy; LOG=$T/results/b6/deploy.log
C=cv02@10.8.1.106; G=noob@172.18.22.20; B=/tmp/noob_el/el_b6; R=/home/noob/work/runner_b6deploy; ST=$R/el_b6
SC="ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $C"; SG="ssh -o BatchMode=yes -o ConnectTimeout=20 $G"
say(){ echo "[$(date '+%F %T')] $*" | tee -a $LOG; }
die(){ say "deploy FAIL: $*"; exit 1; }
say "deploy start"
cd $T || die "cd $T"
[ "$(md5sum < results/b6/FROZEN_B6.md5 | cut -c1-8)" = 807d4d03 ] && md5sum -c --quiet results/b6/FROZEN_B6.md5 || die "laptop FROZEN_B6 check"
(cd results/b6/jobs && md5sum -c --quiet exp/EXP.md5) && [ "$(md5sum < scripts/b6/b6_valcmp.py | cut -c1-8)" = 1ad95d68 ] || die "laptop exp / valcmp check"
Q='nvidia-smi --query-gpu=index,uuid --format=csv,noheader,nounits; echo ===; nvidia-smi --query-compute-apps=gpu_uuid,used_memory --format=csv,noheader,nounits'
s=$($SC "$Q") || die "cv02 snapshot ssh"
q=$(echo "$s" | awk -F', *' '/^===/{p=1; next} !p{idx[$2]=$1; mx[$1]=0; n++} p{g=idx[$1]; if ($2+0 > mx[g]) mx[g]=$2+0}
  END{c=0; ids=""; for (j=0; j<n; j++) if (mx[j] <= 4096) {c++; ids=ids j " "}; print c "|" ids}')
say "cv02 snapshot: qualifying ${q%%|*} (ids ${q#*|})"
[ "${q%%|*}" -ge 3 ] || die "cv02 not qualifying (${q%%|*} < 3): B6 not deployed"
$SC "[ ! -e $B ] && [ -f /tmp/noob_el/env.sh ] && [ -x /tmp/noob_el/el-fault-detection/.venv/bin/python ]" || die "cv02: $B exists or env / venv missing"
$SG "[ ! -e $R/frozen_in ] && [ ! -e $ST ] && mkdir -p $R/frozen_in" || die "gaint $R/frozen_in or $ST exists"
tar cf - results/b6/FROZEN_B6.md5 $(awk '{print $2}' results/b6/FROZEN_B6.md5) results/b6/jobs/exp/*.txt scripts/b6/b6_valcmp.py \
  | $SG "tar xf - -C $R/frozen_in"; rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || die "frozen files -> gaint rc $rc"
scp -q -o BatchMode=yes $D/b6_stage_gaint.sh $D/b6_verify_cv02.sh $G:$R/ || die "scp stage / verify scripts"
o=$($SG "nice -n 19 bash $R/b6_stage_gaint.sh 2>&1 | tail -n 3"); set -- $o
[ "${1:-}" = OK ] || die "gaint staging: $o"
NF=$2; M=$3; say "gaint staged $ST: DEPLOY.md5 $M ($NF files)"
$SG "tar cf - -C $ST ." | $SC "mkdir -p $B && tar xf - -C $B"; rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || die "stream rc $rc"
v=$($SC "bash $B/bin/b6_verify_cv02.sh"); set -- $v
[ "${1:-}" = OK ] || die "cv02 verify: $v"; [ "${2:-}" = "$M" ] || die "DEPLOY.md5 differs on cv02 (${2:-?} vs $M)"
say "deploy done: rc=0 (cv02 $B = gaint $ST, DEPLOY.md5 $M both ends, $NF files; all cv02 checks OK)"
