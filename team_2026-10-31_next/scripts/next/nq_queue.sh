#!/bin/bash
# runner (1 Nov 2026): launch queue for HC (protocol_HC §9.3) and the A8 screen (protocol_A8screen §9) on gaint, behind THIN-B3's
# opening. Jobs file lines "name|seed|arm|opts" (md5 JOBS_MD5), strict list order. Per arm: worktree, deploy commit, start gate
# (measured peak + 2,048), reference config and the expected config difference (file exp_<arm>.txt, from that arm's smoke config).
# Start condition: THIN's "thin scoring done: post rc=0" line (or START_NOW file in the queue dir, set only on coach's word).
# MAXC lanes (file MAXC in the queue dir, default 3). Each start: shared gate (gpu_gate.sh: flock, free >= gate, >= 120 s since any
# start, HOLD). After each start config_used.yaml is diffed vs the arm's reference (run_name, seed, experiments_dir ignored): the
# difference must equal exp_<arm>.txt and seed must be K, else HOLD + CONFIG FAIL. python PIDs in pids/. rc captured before $(date).
set -u
Q=/home/noob/work/nq; L=$Q/launch.log; J=$Q/nq_jobs.txt; TL=/home/noob/work/el_thin/reports/thin/q/launch.log
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
JOBS_MD5=${JOBS_MD5:?}; mkdir -p $Q/pids
declare -A WT=([HC]=/home/noob/work/el_hc [A8]=/home/noob/work/el_f8 [A8c]=/home/noob/work/el_f8)
declare -A DEP=([HC]=c2e6973 [A8]=c280e8c [A8c]=c280e8c)
declare -A GATE=([HC]=${GATE_HC:?} [A8]=${GATE_A8:?} [A8c]=${GATE_A8c:?})
declare -A REF=([HC]=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml \
                [A8]=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml \
                [A8c]=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml)
deploy_ok(){ local w=$1 d=$2; [ "$(git -C $w rev-parse --short=7 HEAD)" = "$d" ] && [ -z "$(git -C $w status --short --untracked-files=no)" ]; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || { echo "[$(date)] nq jobs file md5 FAIL" >> $L; exit 1; }
for a in HC A8 A8c; do deploy_ok ${WT[$a]} ${DEP[$a]} || { echo "[$(date)] nq deploy check FAIL $a (${WT[$a]} != ${DEP[$a]} or tracked changes)" >> $L; exit 1; }
  [ -s $Q/exp_$a.txt ] || { echo "[$(date)] nq: exp_$a.txt missing" >> $L; exit 1; }; done
[ "$(cat /home/noob/work/el_hc/reports/hc/DEPLOY)" = c2e6973 ] && [ "$(cut -c1-7 /home/noob/work/el_f8/REVISION_f8)" = c280e8c ] \
  || { echo "[$(date)] nq: DEPLOY / REVISION stamp FAIL" >> $L; exit 1; }
kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || { echo "[$(date)] nq: own gpumem logger (nq_gpumem.sh) not running, not starting" >> $L; exit 1; }
mapfile -t JOBS < $J
cfgcheck(){ local name=$1 k=$2 arm=$3 c=${WT[$3]}/experiments/$1/config_used.yaml t=0 d e
  while [ ! -s $c ] && [ $t -lt 240 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { echo "[$(date)] CONFIG FAIL $name: no config_used.yaml after 240 s; HOLD set" >> $L; touch $Q/HOLD; return; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' ${REF[$arm]}) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(sort $Q/exp_$arm.txt)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "[$(date)] config OK $name vs pf2_SUPPF_100pct_s5: seed $k + $arm change only" >> $L
  else echo "[$(date)] CONFIG FAIL $name: [$(echo "$d" | tr '\n' ' ')] seed_ok $(grep -qx "seed: $k" $c && echo 1 || echo 0); HOLD set" >> $L; touch $Q/HOLD; fi; }
alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
echo "[$(date)] nq queue armed: ${#JOBS[@]} jobs (md5 $JOBS_MD5), gates HC ${GATE[HC]} / A8 ${GATE[A8]} / A8c ${GATE[A8c]}, pid $$; waiting for THIN's opening end" >> $L
until grep -q "thin scoring done: post rc=0" $TL || [ -e $Q/START_NOW ]; do
  grep -qE "thin NOT scored|thin scoring done: post rc=[1-9]|thin post FAIL" $TL && { echo "[$(date)] nq: THIN opening failure line seen; not starting (decision needed)" >> $L; exit 1; }
  sleep 60; done
echo "[$(date)] nq: start condition met ($(grep -q 'thin scoring done: post rc=0' $TL && echo 'THIN opening rc 0' || echo START_NOW)); dispatching" >> $L
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k arm opts <<< "$j"; w=${WT[$arm]}
  if [ -e $w/experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> $L; continue; fi
  while :; do
    [ -e $Q/HOLD ] && { sleep 60; continue; }
    MAXC=$(cat $Q/MAXC 2>/dev/null || echo 3)
    [ "$(alive)" -ge "$MAXC" ] && { sleep 30; continue; }
    gate_try ${GATE[$arm]} "nq $name" && break
    sleep 30
  done
  deploy_ok $w ${DEP[$arm]} || { echo "[$(date)] nq deploy check FAIL at start of $name; HOLD set" >> $L; touch $Q/HOLD; continue; }
  echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB; alive $(alive); MAXC $MAXC)" >> $L
  ( cd $w && HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  sleep 3; echo "[$(date)] pid $name $(cat $Q/pids/$name.pid 2>/dev/null)" >> $L
  cfgcheck $name $k $arm
done
echo "[$(date)] nq queue: all jobs dispatched; waiting" >> $L
wait
echo "[$(date)] NQ ALL TRAINED ($(grep -c 'trained .* rc=0' $L) rc 0)" >> $L
