#!/bin/bash
# runner DRAFT v2 (2 Nov 2026): launch queue for SKR2 + HC2 (one protocol, one opening; user 11:18) on gaint. Copy of nq_queue.sh
# 156c6936 (coach-approved 1 Nov) with: queue dir /home/noob/work/s2q; arms SKR01 (el_thin c9bbb02) and HC2 (builder's new deploy:
# HC2_WT / HC2_DEP from env, required only when the jobs file holds HC2 lines); no predecessor to wait for. v2 (after D1, coach's
# queue split): the arm checks (deploy, exp file, REVISION stamp) run only for the arms present in the jobs file. Else unchanged.
# v3 (2 Nov, chained HC2 queue; coach's conditions 1-3): JOBS_FILE = jobs file (default s2q_jobs.txt); AFTER = a line to wait for in the
# shared launch.log before dispatching (the SKR queue's 's2q queue: all jobs dispatched'; chained-queue rule); same Q dir, pids/ and
# launch.log as the running queue, so alive() / MAXC 3 count both queues and the opening trigger reads one log; the gpumem logger must be
# alive at arming (as before); the ALL TRAINED line counts this queue's own jobs only.
# Jobs file lines "name|seed|arm|opts" (md5 JOBS_MD5), strict list order. Per arm: worktree, deploy commit, start gate
# (measured peak + 2,048), reference config and the expected config difference (file exp_<arm>.txt).
# MAXC lanes (file MAXC in the queue dir, default 3). Each start: shared gate (gpu_gate.sh: flock, free >= gate, >= 120 s since any
# start, HOLD). After each start config_used.yaml is diffed vs the arm's reference (run_name, seed, experiments_dir ignored): the
# difference must equal exp_<arm>.txt and seed must be K, else HOLD + CONFIG FAIL. python PIDs in pids/. rc captured before $(date).
set -u
Q=/home/noob/work/s2q; L=$Q/launch.log; J=${JOBS_FILE:-$Q/s2q_jobs.txt}; AFTER=${AFTER:-}
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
JOBS_MD5=${JOBS_MD5:?}; mkdir -p $Q/pids
ARMS=$(cut -d'|' -f3 $J | sort -u | tr '\n' ' ')
declare -A WT=([SKR01]=/home/noob/work/el_thin [HC2]=${HC2_WT:-}) DEP=([SKR01]=c9bbb02 [HC2]=${HC2_DEP:-}) GATE=([SKR01]=${GATE_SKR01:-} [HC2]=${GATE_HC2:-})
R0=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
declare -A REF=([SKR01]=$R0 [HC2]=$R0)
deploy_ok(){ local w=$1 d=$2; [ "$(git -C $w rev-parse --short=7 HEAD)" = "$d" ] && [ -z "$(git -C $w status --short --untracked-files=no)" ]; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || { echo "[$(date)] s2q jobs file md5 FAIL" >> $L; exit 1; }
for a in $ARMS; do
  case $a in SKR01|HC2) ;; *) echo "[$(date)] s2q: unknown arm $a in jobs file" >> $L; exit 1;; esac
  [ -n "${WT[$a]}" ] && [ -n "${DEP[$a]}" ] && [ -n "${GATE[$a]}" ] || { echo "[$(date)] s2q: worktree / deploy / gate unset for arm $a" >> $L; exit 1; }
  deploy_ok ${WT[$a]} ${DEP[$a]} || { echo "[$(date)] s2q deploy check FAIL $a (${WT[$a]} != ${DEP[$a]} or tracked changes)" >> $L; exit 1; }
  [ -s $Q/exp_$a.txt ] || { echo "[$(date)] s2q: exp_$a.txt missing" >> $L; exit 1; }
  [ "$(cut -c1-7 ${WT[$a]}/REVISION)" = "${DEP[$a]}" ] || { echo "[$(date)] s2q: REVISION stamp FAIL $a" >> $L; exit 1; }; done
kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || { echo "[$(date)] s2q: own gpumem logger (s2q_gpumem.sh) not running, not starting" >> $L; exit 1; }
mapfile -t JOBS < $J
cfgcheck(){ local name=$1 k=$2 arm=$3 c=${WT[$3]}/experiments/$1/config_used.yaml t=0 d e
  while [ ! -s $c ] && [ $t -lt 240 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { echo "[$(date)] CONFIG FAIL $name: no config_used.yaml after 240 s; HOLD set" >> $L; touch $Q/HOLD; return; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' ${REF[$arm]}) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(sort $Q/exp_$arm.txt)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "[$(date)] config OK $name vs pf2_SUPPF_100pct_s5: seed $k + $arm change only" >> $L
  else echo "[$(date)] CONFIG FAIL $name: [$(echo "$d" | tr '\n' ' ')] seed_ok $(grep -qx "seed: $k" $c && echo 1 || echo 0); HOLD set" >> $L; touch $Q/HOLD; fi; }
alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
echo "[$(date)] s2q queue armed: ${#JOBS[@]} jobs ($(basename $J), md5 $JOBS_MD5), arms $ARMS, gates SKR01 ${GATE[SKR01]:--} / HC2 ${GATE[HC2]:--}, pid $$; $([ -n "$AFTER" ] && echo "waiting for '$AFTER'" || echo dispatching)" >> $L
if [ -n "$AFTER" ]; then
  until grep -qF "$AFTER" $L; do sleep 60; done
  echo "[$(date)] s2q queue pid $$: '$AFTER' seen; dispatching" >> $L
fi
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k arm opts <<< "$j"; w=${WT[$arm]}
  if [ -e $w/experiments/$name ]; then echo "[$(date)] skip $name (exists)" >> $L; continue; fi
  while :; do
    [ -e $Q/HOLD ] && { sleep 60; continue; }
    MAXC=$(cat $Q/MAXC 2>/dev/null || echo 3)
    [ "$(alive)" -ge "$MAXC" ] && { sleep 30; continue; }
    gate_try ${GATE[$arm]} "s2q $name" && break
    sleep 30
  done
  deploy_ok $w ${DEP[$arm]} || { echo "[$(date)] s2q deploy check FAIL at start of $name; HOLD set" >> $L; touch $Q/HOLD; continue; }
  echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB; alive $(alive); MAXC $MAXC)" >> $L
  ( cd $w && HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  sleep 3; echo "[$(date)] pid $name $(cat $Q/pids/$name.pid 2>/dev/null)" >> $L
  cfgcheck $name $k $arm
done
echo "[$(date)] s2q queue: all jobs dispatched; waiting" >> $L
wait
NM=$(printf '%s\n' "${JOBS[@]}" | cut -d'|' -f1 | paste -sd'|')
echo "[$(date)] S2Q ALL TRAINED ($(grep -cE "trained ($NM) rc=0\$" $L) rc 0 of ${#JOBS[@]}; pid $$, $(basename $J))" >> $L
