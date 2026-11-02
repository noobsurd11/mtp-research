#!/bin/bash
# runner DRAFT (1 Nov 2026; coach 23:5x, protocol_B6 §9 cv02 fallback; NOT frozen, NOT armed; only if the user says 'no gaint' AND
# b6_cv02_exactchk.sh PASSED): B6 scoring ON cv02, ONE bf16 b6_score.py 981b5f29 invocation for all 20 runs, after
# 'B6 ALL TRAINED (20 rc 0 of 20)'. Same asserts as b6_score_gaint.sh e6f1259d, minus the gaint symlink (the configs' data.root is
# native here): b6_score / forbidden / folds md5; code = the e544133 archive B (REVISION + CODE.md5 -c; REVISION sits in the runs'
# grandparent B, so the scorer records it); ROOTS.md5 + per-root SPLITS + DATA_MANIFEST -c; each config's root line == its fold;
# 20 latest.pth; refuses to overwrite. Lane = the queue's rules: first GPU of GPUS with no other user's process > 4,096 MiB and
# free >= GATE (9,900, or the exact check's peak + 2,048 if higher); polls every 60 s until one qualifies (HOLD file pauses).
# 1 s memory log on that GPU (W/gpumem.log); pid also in q/score_pids/ (the B6 gpumem logger tags it 'ours' if still running).
# Output W/out/*.b6.json + score.stdout + MANIFEST.md5; end line 'b6 scoring done: rc=N' / 'b6 NOT scored: ...' in W/score.log.
# Then b6_score_relay.sh (out/ + logs -> gaint b6_score/) and b6_relay.sh (run dirs -> gaint), and b6_post_local.sh unchanged.
# Usage (cv02 tmux): GPUS="<ids>" GATE=<MiB> bash b6_score_cv02.sh
set -u
. /tmp/noob_el/env.sh
B=/tmp/noob_el/el_b6; Q=$B/q; W=$B/score; O=$W/out; SL=$W/score.log; S=$B/b6s; RT=$B/b6_roots
P=/tmp/noob_el/el-fault-detection/.venv/bin/python; GPUS=${GPUS:?}; GATE=${GATE:?}; OTHER_MAX=4096
mkdir -p $W $Q/score_pids; ts(){ date '+%F %T'; }
say(){ echo "[$(ts)] $*" >> $SL; }
die(){ say "b6 NOT scored: $*"; exit 1; }
[ "$GATE" -ge 9900 ] 2>/dev/null || die "GATE '$GATE' < 9900"
[ ! -e $O ] || die "$O exists (refuse to overwrite)"
grep -q 'B6 ALL TRAINED (20 rc 0 of 20)' $Q/launch.log || die "no 'B6 ALL TRAINED (20 rc 0 of 20)'"
grep -q 'exactchk PASS' $B/exactchk/exactchk.log 2>/dev/null || die "cv02 exact check has not PASSED"
[ "$(md5sum < $S/b6_score.py | cut -c1-8)" = 981b5f29 ] || die "b6_score.py md5"
[ "$(md5sum < $S/b6_forbidden.txt | cut -c1-8)" = 9bb4d919 ] && [ "$(md5sum < $S/b6_folds.tsv | cut -c1-8)" = e2cafce1 ] || die "forbidden / folds md5"
[ "$(cut -c1-7 $B/REVISION)" = e544133 ] && (cd $B && md5sum -c --quiet CODE.md5) || die "code != e544133 archive"
(cd $RT && md5sum -c --quiet ROOTS.md5) || die "ROOTS.md5 check FAIL"
for k in 0 1 2 3 4; do (cd $RT/b6_root_$k && md5sum -c --quiet SPLITS.md5 && md5sum -c --quiet DATA_MANIFEST.md5) || die "root $k check FAIL"; done
RUNS=(); STEMS=()
while IFS='|' read -r name k arm f opts; do
  r=$B/experiments/$name; [ -s $r/checkpoints/latest.pth ] && [ -s $r/config_used.yaml ] || die "$name missing latest.pth / config"
  grep -qx "  root: $RT/b6_root_$f" $r/config_used.yaml || die "$name data.root != $RT/b6_root_$f"
  RUNS+=($r); STEMS+=($RT/b6_root_$f/splits/test.txt)
done < $Q/b6_jobs.txt
[ ${#RUNS[@]} = 20 ] || die "${#RUNS[@]} runs in b6_jobs.txt, expected 20"
echo $$ > $W/wrapper.pid
say "armed pid $$ (20 runs, checks OK); GPUS '$GPUS', gate $GATE"
ours(){ cat $Q/pids/*.pid $Q/score_pids/*.pid 2>/dev/null | tr '\n' ' '; }
lane(){ local g u o f; for g in $GPUS; do u=$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $g | tr -d ' ')
    o=$(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | tr -d ' ' \
        | awk -F, -v u=$u -v m=$OTHER_MAX -v ours=" $(ours) " '$1==u && $3>m && index(ours, " "$2" ")==0' | wc -l)
    f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $g | tr -d ' ')
    [ "$o" = 0 ] && [ "$f" -ge $GATE ] && { echo $g; return 0; }; done; return 1; }
while :; do [ -e $W/HOLD ] && { sleep 60; continue; }; G=$(lane) && break; sleep 60; done
U=$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $G | tr -d ' ')
say "lane GPU $G (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $G | tr -d ' ') MiB; loadavg $(cut -d' ' -f1-3 /proc/loadavg)); scoring start"
( cd $W && CUDA_VISIBLE_DEVICES=$G OMP_NUM_THREADS=4 HF_HUB_OFFLINE=1 nice -n 19 $P $S/b6_score.py --code $B --out $O --forbidden $S/b6_forbidden.txt \
    --folds $S/b6_folds.tsv --mode b6 --device cuda --runs "${RUNS[@]}" --stems "${STEMS[@]}" > $W/score.stdout 2>&1 ) &
cp=$!; echo $cp > $W/score.pid; echo $cp > $Q/score_pids/score.pid; pk=0; mf=999999
while kill -0 $cp 2>/dev/null; do
  kids=" $cp $(ps -o pid= --ppid $cp | tr -d ' ' | tr '\n' ' ') "
  for q in $kids; do echo $q; done > $Q/score_pids/score.pid
  sm=0; while IFS=, read -r gu p m; do [ "$gu" = "$U" ] || continue; case "$kids" in *" $p "*) sm=$((sm + m)); [ "$m" -gt $pk ] && pk=$m;; esac; done \
    < <(nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits | tr -d ' ')
  read -r f u < <(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i $G | tr -d ' ' | tr ',' ' ')
  [ "$f" -lt $mf ] && mf=$f
  echo "$(date +%T) g$G free $f used $u | scorer $sm MiB" >> $W/gpumem.log
  sleep 1
done
wait $cp; rc=$?
rm -f $Q/score_pids/score.pid
n=$(ls $O/*.b6.json 2>/dev/null | wc -l)
[ $rc = 0 ] && [ "$n" = 20 ] || { say "b6 NOT scored: scorer rc=$rc, $n of 20 outputs (peak ${pk} MiB, min free ${mf} MiB)"; rm -f $W/wrapper.pid; exit 1; }
cp $W/score.stdout $O/ && (cd $O && md5sum *.b6.json score.stdout > MANIFEST.md5)
say "b6 scoring done: rc=0 (20 outputs, MANIFEST $(md5sum < $O/MANIFEST.md5 | cut -c1-8); GPU $G; scorer peak ${pk} MiB, min free ${mf} MiB)"
rm -f $W/wrapper.pid
