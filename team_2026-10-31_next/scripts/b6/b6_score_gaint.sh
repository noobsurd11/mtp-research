#!/bin/bash
# runner DRAFT (1 Nov 2026; coach ruling 23:4x): B6 scoring, ONE bf16 GPU pass on gaint for all 20 relayed runs, behind the shared
# start gate at the scoring gate. Runs in gaint tmux; coach FREEZES this file (+ b6_score.py 981b5f29) before any B6 run trains.
# Inputs: relayed runs DD=/home/noob/work/cv02_noob_el/el_b6 (b6_relay.sh; q/RELAY.md5); code el_f3 at e544133 (HEAD, 0 tracked
#   changes; the same --code as builder's GPU exact check); b6_score.py 981b5f29; b6_forbidden.txt 9bb4d919; b6_folds.tsv e2cafce1.
# data.root in each run's config_used.yaml is cv02's /tmp/noob_el/el_b6/b6_roots/b6_root_k: on gaint that path is made a symlink
#   to builder's roots /home/noob/work/b6 (ROOTS.md5 e4100381; labeled -> el-fault-detection/data/labeled) and every root is
#   md5sum -c'd through it (SPLITS.md5 + DATA_MANIFEST.md5 = the files cv02 trained on), so the scorer's own asserts (stems ==
#   <data.root>/splits/test.txt == val.txt, train.txt = other 4 folds, no forbidden stem, step 20000) read the same lists.
#   Configs are not edited (config_md5 goes into every output).
# GATE = max(9,900, builder's b6chk measured scorer peak + 2,048) (env, refused below 9,900). FAST on while it runs (if absent
#   before); own 1 s peak of the scorer python + min free; a line every 1 s to W/gpumem.log ("time free used | scorer MiB"). Output O=/home/noob/work/b6_score/out/<run>.b6.json + MANIFEST.md5.
# End line "b6 scoring done: rc=N" in O/../score.log and events.log. No test / E1 cell: the scorer refuses forbidden stems.
set -u
DD=/home/noob/work/cv02_noob_el/el_b6; W=/home/noob/work/b6_score; O=$W/out; SL=$W/score.log; EV=/home/noob/work/runner_events/events.log
CODE=/home/noob/work/el_f3; S=/home/noob/work/b6_build/scripts/b6_score.py; FB=/home/noob/work/b6/b6_forbidden.txt
FO=/home/noob/work/b6_build/inputs/b6_folds.tsv; RL=/tmp/noob_el/el_b6/b6_roots; RT=/home/noob/work/b6; GG=/home/noob/work/gpu_gate
P=/home/noob/work/el-fault-detection/.venv/bin/python; GATE=${GATE:?}
mkdir -p $W; ts(){ date '+%F %T'; }
say(){ echo "[$(ts)] $*" >> $SL; echo "$(ts) b6s: $*" >> $EV; }
die(){ say "b6 NOT scored: $*"; exit 1; }
[ "$GATE" -ge 9900 ] 2>/dev/null || die "GATE '$GATE' < 9900"
[ ! -e $O ] || die "$O exists (refuse to overwrite)"
[ "$(md5sum < $S | cut -c1-8)" = 981b5f29 ] || die "b6_score.py md5"
[ "$(md5sum < $FB | cut -c1-8)" = 9bb4d919 ] && [ "$(md5sum < $FO | cut -c1-8)" = e2cafce1 ] || die "forbidden / folds md5"
[ "$(git -C $CODE rev-parse --short=7 HEAD)" = e544133 ] && [ -z "$(git -C $CODE status --short --untracked-files=no)" ] || die "el_f3 != e544133 clean"
(cd $DD && md5sum -c --quiet q/RELAY.md5) || die "RELAY.md5 check FAIL"
[ "$(cut -c1-7 $DD/REVISION)" = e544133 ] || die "relayed REVISION != e544133"
[ -L $RL ] || [ ! -e $RL ] || die "$RL exists and is not a symlink"
mkdir -p /tmp/noob_el/el_b6; [ -L $RL ] || ln -s $RT $RL; [ "$(readlink $RL)" = $RT ] || die "$RL -> $(readlink $RL), not $RT"
(cd $RL && md5sum -c --quiet ROOTS.md5) || die "ROOTS.md5 check via $RL FAIL"
for k in 0 1 2 3 4; do (cd $RL/b6_root_$k && md5sum -c --quiet SPLITS.md5 && md5sum -c --quiet DATA_MANIFEST.md5) || die "root $k check via $RL FAIL"; done
RUNS=(); STEMS=()
while IFS='|' read -r name k arm f opts; do
  r=$DD/experiments/$name; [ -s $r/checkpoints/latest.pth ] && [ -s $r/config_used.yaml ] || die "$name missing latest.pth / config"
  grep -qx "  root: $RL/b6_root_$f" $r/config_used.yaml || die "$name data.root != $RL/b6_root_$f"
  RUNS+=($r); STEMS+=($RL/b6_root_$f/splits/test.txt)
done < $DD/q/b6_jobs.txt
[ ${#RUNS[@]} = 20 ] || die "${#RUNS[@]} runs in b6_jobs.txt, expected 20"
echo $$ > $W/wrapper.pid
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
say "armed pid $$ (20 runs, checks OK); waiting for gate $GATE"
gate_wait $GATE "b6 scoring"
F0=0; [ -e $GG/FAST ] && F0=1; touch $GG/FAST
say "gate pass (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB); scoring start"
( cd $W && OMP_NUM_THREADS=4 HF_HUB_OFFLINE=1 nice -n 19 $P $S --code $CODE --out $O --forbidden $FB --folds $FO --mode b6 --device cuda \
    --runs "${RUNS[@]}" --stems "${STEMS[@]}" > $W/score.stdout 2>&1 ) &
cp=$!; echo $cp > $W/score.pid; pk=0; mf=999999
while kill -0 $cp 2>/dev/null; do
  kids=" $cp $(ps -o pid= --ppid $cp | tr -d ' ' | tr '\n' ' ') $(for q in $(ps -o pid= --ppid $cp); do ps -o pid= --ppid $q; done | tr -d ' ' | tr '\n' ' ') "
  sm=0; while IFS=, read -r p m; do case "$kids" in *" $p "*) sm=$((sm + m)); [ "$m" -gt $pk ] && pk=$m;; esac; done \
    < <(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ')
  read -r f u < <(nvidia-smi --query-gpu=memory.free,memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ' | tr ',' ' ')
  [ "$f" -lt $mf ] && mf=$f
  # coach 23:5x (README: log free memory every 10 s while our jobs share the GPU): own log, every 1 s sample, independent of nq
  echo "$(date +%T) free $f used $u | scorer $sm MiB" >> $W/gpumem.log
  sleep 1
done
wait $cp; rc=$?
[ $F0 = 0 ] && rm -f $GG/FAST
n=$(ls $O/*.b6.json 2>/dev/null | wc -l)
[ $rc = 0 ] && [ "$n" = 20 ] || { say "b6 NOT scored: scorer rc=$rc, $n of 20 outputs (peak ${pk} MiB, min free ${mf} MiB)"; rm -f $W/wrapper.pid; exit 1; }
cp $W/score.stdout $O/ && (cd $O && md5sum *.b6.json score.stdout > MANIFEST.md5)
say "b6 scoring done: rc=0 (20 outputs, MANIFEST $(md5sum < $O/MANIFEST.md5 | cut -c1-8); scorer peak ${pk} MiB, min free ${mf} MiB)"
rm -f $W/wrapper.pid
