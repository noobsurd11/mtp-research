#!/bin/bash
# THIN-B3 launch queue on gaint (el_thin; protocol_thin_b3.md §7-8). 15 runs from reports/thin/q/thin_jobs.txt (md5 JOBS_MD5),
# strict list order (waves by seed: SKR sK, CLD sK, B3 sK). Starts only after PF2's "PF2 ALL TRAINED" line. MAXC 2 until PF2's
# "pf2 scoring done" line, then 3. Each start: shared gate (gpu_gate.sh: flock, free >= arm gate, >= 120 s since any start, HOLD):
# SKR 9,100, CLD 10,500, B3 9,000 MiB. After each start, config_used.yaml is diffed vs pf2_SUPPF_100pct_s5's (run_name, seed,
# experiments_dir ignored); the difference must be exactly the arm's one change, else reports/thin/q/HOLD + CONFIG FAIL line.
# python PIDs in reports/thin/q/pids/. Log reports/thin/q/launch.log. rc captured before $(date).
set -u
cd /home/noob/work/el_thin
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
Q=reports/thin/q; L=$Q/launch.log; J=$Q/thin_jobs.txt; PL=/home/noob/work/el_f3/reports/pf2/launch.log; mkdir -p $Q/pids experiments
DEPLOY=${DEPLOY:?}; JOBS_MD5=${JOBS_MD5:?}
[ "$(git rev-parse --short HEAD)" = "$DEPLOY" ] && [ "$(cat reports/thin/DEPLOY)" = "$DEPLOY" ] && [ "$(cat REVISION 2>/dev/null)" = "$DEPLOY" ] \
  && [ -z "$(git status --short --untracked-files=no)" ] || { echo "[$(date)] thin deploy check FAIL (HEAD / DEPLOY / REVISION / tracked changes)" >> $L; exit 1; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || { echo "[$(date)] thin jobs file md5 FAIL" >> $L; exit 1; }
kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || { echo "[$(date)] thin: gpumem logger not running, not starting" >> $L; exit 1; }
mapfile -t JOBS < $J
declare -A GATE=([SKR]=9100 [CLD]=10500 [B3]=9000)
declare -A EXP=([SKR]=$'<   skel_recall:\n<     weight: 1.0' [CLD]=$'<   cldice:\n<     iters: 10\n<     weight: 1.0' \
  [B3]=$'<   mask_subdir: labeled/masks_escdd_s\n<   num_classes: 25\n<   scuff_class: 24\n>   mask_subdir: labeled/masks_escdd\n>   num_classes: 24')
REF=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
cfgcheck(){ local name=$1 k=$2 arm=$3 c=experiments/$1/config_used.yaml t=0 d e
  while [ ! -s $c ] && [ $t -lt 180 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { echo "[$(date)] CONFIG FAIL $name: no config_used.yaml after 180 s; HOLD set" >> $L; touch $Q/HOLD; return; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(printf '%s\n' "${EXP[$arm]}" | sort)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "[$(date)] config OK $name vs pf2_SUPPF_100pct_s5: seed $k + $arm change only" >> $L
  else echo "[$(date)] CONFIG FAIL $name: [$(echo "$d" | tr '\n' ' ')] seed_ok $(grep -qx "seed: $k" $c && echo 1 || echo 0); HOLD set" >> $L; touch $Q/HOLD; fi; }
alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
echo "[$(date)] thin queue armed: ${#JOBS[@]} jobs (md5 $JOBS_MD5), deploy $DEPLOY, gates SKR 9100 / CLD 10500 / B3 9000, pid $$; waiting for PF2 ALL TRAINED" >> $L
until grep -q "PF2 ALL TRAINED" $PL; do
  grep -qE "pf2 NOT scored|PF2 .*FAIL" $PL && { echo "[$(date)] thin: PF2 failure line seen; not starting (decision needed)" >> $L; exit 1; }
  sleep 60; done
echo "[$(date)] thin: PF2 ALL TRAINED seen; dispatching" >> $L
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k arm opts <<< "$j"
  if [ -e experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> $L; continue; fi
  while :; do
    [ -e $Q/HOLD ] && { sleep 60; continue; }
    grep -q "pf2 scoring done" $PL && MAXC=3 || MAXC=2
    [ "$(alive)" -ge "$MAXC" ] && { sleep 30; continue; }
    gate_try ${GATE[$arm]} "thin $name" && break
    sleep 30
  done
  echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB; alive $(alive); MAXC $MAXC)" >> $L
  ( HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  sleep 3; echo "[$(date)] pid $name $(cat $Q/pids/$name.pid 2>/dev/null)" >> $L
  cfgcheck $name $k $arm
done
echo "[$(date)] thin queue: all jobs dispatched; waiting" >> $L
wait
echo "[$(date)] THIN ALL TRAINED ($(grep -c 'trained thin_.* rc=0' $L) rc 0)" >> $L
