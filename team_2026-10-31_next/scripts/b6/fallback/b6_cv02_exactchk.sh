#!/bin/bash
# runner DRAFT (1 Nov 2026; coach 23:5x, protocol_B6 §9 cv02 fallback; NOT frozen, NOT armed): builder's scorer exact check ON cv02.
# b6_score.py 981b5f29 --mode check --device cuda (bf16, TTA off) on f3_SUPPF_100pct_s0 latest.pth (54 val stems), then
# b6_valcmp.py 1ad95d68 --expect exact vs the val-only m0 extract. PASS = rc 0 of both (all 54 per-cell records identical).
# No tolerance fallback: a FAIL goes to team-lead + the user (coach). Runs in cv02 tmux after deploy + b6_exactchk_relay.sh.
# Lane rules = the queue's: GPU G from the qualifying snapshot; refuses if any other user's process (pid not ours) > 4,096 MiB on G
# or free < GATE (9,900; peak unknown on A6000, m0-type pass). 1 s memory log on G (exactchk/gpumem.log). rc captured before $(date).
# Usage (cv02): G=<gpu id> bash b6_cv02_exactchk.sh
set -u
. /tmp/noob_el/env.sh
B=/tmp/noob_el/el_b6; X=$B/exactchk; S=$B/b6s; P=/tmp/noob_el/el-fault-detection/.venv/bin/python; L=$X/exactchk.log
G=${G:?}; GATE=${GATE:-9900}; OTHER_MAX=4096
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
die(){ say "exactchk NOT run: $*"; exit 1; }
[ ! -e $X/out ] || die "$X/out exists"
[ "$(md5sum < $S/b6_score.py | cut -c1-8)" = 981b5f29 ] && [ "$(md5sum < $S/b6_valcmp.py | cut -c1-8)" = 1ad95d68 ] \
  && [ "$(md5sum < $S/b6_forbidden.txt | cut -c1-8)" = 9bb4d919 ] || die "b6s script / list md5"
[ "$(cut -c1-7 $B/REVISION)" = e544133 ] && (cd $B && md5sum -c --quiet CODE.md5) || die "code != e544133 archive"
(cd $X && md5sum -c --quiet EXACTCHK.md5) || die "EXACTCHK.md5 check FAIL"
[ -L $X/valroot/labeled ] || ln -s $B/b6_data/labeled $X/valroot/labeled
[ "$(readlink $X/valroot/labeled)" = $B/b6_data/labeled ] || die "valroot/labeled -> $(readlink $X/valroot/labeled)"
(cd $B/b6_roots/b6_root_0 && md5sum -c --quiet DATA_MANIFEST.md5) || die "DATA_MANIFEST (532 stems incl. the 54 val) check FAIL"
u=$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $G | tr -d ' ')
o=$(nvidia-smi --query-compute-apps=gpu_uuid,used_memory --format=csv,noheader,nounits | tr -d ' ' | awk -F, -v u=$u -v m=$OTHER_MAX '$1==u && $2>m' | wc -l)
[ "$o" = 0 ] || die "GPU $G: another user's process > $OTHER_MAX MiB"
f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $G | tr -d ' '); [ "$f" -ge $GATE ] || die "GPU $G free $f < $GATE"
say "start on GPU $G (free $f MiB; nproc $(nproc), loadavg $(cut -d' ' -f1-3 /proc/loadavg)); pid $$"
( cd $X && CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=4 HF_HUB_OFFLINE=1 nice -n 19 $P $S/b6_score.py --code $B --out $X/out --forbidden $S/b6_forbidden.txt \
    --mode check --device cuda --runs $X/runs/f3_SUPPF_100pct_s0 --stems $X/valroot/splits/test.txt > $X/score_gpu.log 2>&1 ) &
cp=$!; echo $cp > $X/score.pid; pk=0
while kill -0 $cp 2>/dev/null; do
  kids=" $cp $(ps -o pid= --ppid $cp | tr -d ' ' | tr '\n' ' ') "
  sm=0; while IFS=, read -r gu p m; do [ "$gu" = "$u" ] || continue; case "$kids" in *" $p "*) sm=$((sm + m)); [ "$m" -gt $pk ] && pk=$m;; esac; done \
    < <(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | tr -d ' ')
  echo "$(date +%T) g$G $(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i $G | tr -d ' ' | tr ',' ' ') | scorer $sm MiB" >> $X/gpumem.log
  sleep 1
done
wait $cp; rc=$?
say "score_gpu rc=$rc (peak ${pk} MiB)"
[ $rc = 0 ] || { say "exactchk FAIL: scorer rc $rc"; exit 1; }
$P -I $S/b6_valcmp.py --b6 $X/out/f3_SUPPF_100pct_s0.check.json --m0 $X/m0val_f3_SUPPF_100pct_s0.json --expect exact > $X/valcmp_gpu.txt 2>&1; rc=$?
(cd $X && md5sum out/*.json valcmp_gpu.txt score_gpu.log > RESULT.md5)
if [ $rc = 0 ]; then say "exactchk PASS: valcmp_gpu rc=0 (all 54 records identical; A6000 vs gaint m0)"; else say "exactchk FAIL: valcmp_gpu rc=$rc (no tolerance fallback; to team-lead + user)"; fi
exit $rc
