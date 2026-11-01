#!/bin/bash
# PF2 launch queue on gaint (el_f3, deploy e544133; protocol_PF2.md). One dispatcher for the 15 runs in reports/pf2/pf2_jobs.txt
# (md5 must equal JOBS_MD5). Order: waves by seed (SUP100-g sK, SUP100-PF sK, RN50-PF sK, K = 5..9).
#   POLICY=strict : list order, no skipping (protocol_100).
#   POLICY=twohead: two ordered heads, R34 jobs (SUP / SUPPF in list order) and RN50 jobs (in list order); each dispatch starts
#                   the earliest-listed head whose gate passes, so an RN50 job waiting for memory does not idle an R34 lane.
# Each start: < MAXC of ours alive, < MAXRN RN50 alive, then the shared gate (gpu_gate.sh: flock, free >= peak + 2,048 MiB,
# >= 120 s since any start): R34 G34 (9,000), RN50 GRN (RN50-PF smoke peak + 2,048). Training only, no per-run scoring.
# HOLD: /home/noob/work/gpu_gate/HOLD (all starts) or reports/pf2/HOLD (this queue). RN_STOP (gate 6 fail): RN50 jobs skipped.
# After each start the run's config_used.yaml is diffed against protocol_100's s0 config of its arm (expected: seed only;
# RN50-PF: seed + encoder_name); any other difference -> reports/pf2/HOLD + a CONFIG FAIL line (running runs continue).
# python PIDs in reports/pf2/pids/<run>.pid. Log reports/pf2/launch.log. rc captured before $(date).
set -u
cd /home/noob/work/el_f3
. reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python
L=reports/pf2/launch.log; J=reports/pf2/pf2_jobs.txt; mkdir -p reports/pf2/pids experiments
MAXC=${MAXC:-3}; MAXRN=${MAXRN:-1}; G34=${G34:-9000}; GRN=${GRN:?set GRN = RN50-PF peak + 2048}; POLICY=${POLICY:-twohead}; JOBS_MD5=${JOBS_MD5:?}
[ "$(cat REVISION)" = e544133 ] && [ "$(git rev-parse --short HEAD)" = e544133 ] && [ -z "$(git status --short --untracked-files=no)" ] \
  || { echo "[$(date)] pf2 deploy check FAIL (REVISION / HEAD / tracked changes)" >> $L; exit 1; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || { echo "[$(date)] pf2 jobs file md5 FAIL" >> $L; exit 1; }
[ -e reports/pf2/gpumem.pid ] && kill -0 "$(cat reports/pf2/gpumem.pid)" 2>/dev/null || { echo "[$(date)] pf2: gpumem logger not running, not starting" >> $L; exit 1; }
mapfile -t JOBS < $J
declare -A REF=([SUP]=experiments/f3_SUP_100pct_s0/config_used.yaml [SUPPF]=experiments/f3_SUPPF_100pct_s0/config_used.yaml [RN50PF]=experiments/f3_SUPPF_100pct_s0/config_used.yaml)
cfgcheck(){ local name=$1 k=$2 arm=$3 c=experiments/$1/config_used.yaml t=0 d
  while [ ! -s $c ] && [ $t -lt 180 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { echo "[$(date)] CONFIG FAIL $name: no config_used.yaml after 180 s; HOLD set" >> $L; touch reports/pf2/HOLD; return; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  encoder_name: resnet50$' $c) <(grep -vE '^(run_name|seed):' ${REF[$arm]}) | grep -E '^[<>]' | tr '\n' ' ')
  local okseed=0 okenc=0; grep -qx "seed: $k" $c && okseed=1
  if [ $arm = RN50PF ]; then grep -qx "  encoder_name: resnet50" $c && okenc=1; else grep -q "encoder_name" $c || okenc=1; fi
  if [ -z "$d" ] && [ $okseed = 1 ] && [ $okenc = 1 ]; then echo "[$(date)] config OK $name vs ${REF[$arm]}: seed $k$([ $arm = RN50PF ] && echo ' + encoder_name resnet50') only" >> $L
  else echo "[$(date)] CONFIG FAIL $name: [$d] seed_ok $okseed enc_ok $okenc; HOLD set" >> $L; touch reports/pf2/HOLD; fi; }
alive(){ local n=0 f; for f in reports/pf2/pids/*.pid; do [ -e "$f" ] || continue; case "$f" in *"$1"*) ;; *) continue;; esac
  kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
start(){ local name=$1 k=$2 arm=$3 opts=$4
  echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB; alive $(alive pf2_) incl. RN50 $(alive RN50))" >> $L
  ( HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > reports/pf2/pids/$name.pid
    wait $pp; rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L ) &  # subshell PID tracked below; python PID in pids/
  echo "$name subshell $!" >> reports/pf2/pids/subshells.txt
  sleep 3; echo "[$(date)] pid $name $(cat reports/pf2/pids/$name.pid 2>/dev/null)" >> $L
  cfgcheck $name $k $arm; }
echo "[$(date)] pf2 queue start: ${#JOBS[@]} jobs (md5 $JOBS_MD5), POLICY $POLICY, MAXC $MAXC, MAXRN $MAXRN, gates R34 $G34 / RN50 $GRN MiB, code $(cat REVISION), pid $$" >> $L
declare -A DONE=()
for j in "${JOBS[@]}"; do n=${j%%|*}; [ -e experiments/$n ] && { DONE[$n]=1; echo "[$(date)] skip $n (exists)" >> $L; }; done
next(){ local want=$1 j n a; for j in "${JOBS[@]}"; do IFS='|' read -r n _ a _ <<< "$j"; [ -n "${DONE[$n]:-}" ] && continue
  case $want in any) echo "$j"; return;; r34) [ $a != RN50PF ] && { echo "$j"; return; };; rn) [ $a = RN50PF ] && { echo "$j"; return; };; esac; done; }
idx(){ local i=0 j; for j in "${JOBS[@]}"; do [ "$j" = "$1" ] && { echo $i; return; }; i=$((i+1)); done; echo 999; }
while :; do
  [ -n "$(next any)" ] || break
  if [ -e reports/pf2/HOLD ]; then sleep 60; continue; fi
  if [ "$(alive pf2_)" -ge "$MAXC" ]; then sleep 30; continue; fi
  if [ $POLICY = strict ]; then C=("$(next any)"); else
    a=$(next r34); b=$(next rn); C=()
    if [ -n "$a" ] && [ -n "$b" ]; then if [ $(idx "$a") -lt $(idx "$b") ]; then C=("$a" "$b"); else C=("$b" "$a"); fi
    elif [ -n "$a" ]; then C=("$a"); else C=("$b"); fi; fi
  started=0
  for c in "${C[@]}"; do IFS='|' read -r n k a o <<< "$c"
    if [ $a = RN50PF ] && [ -e reports/pf2/RN_STOP ]; then DONE[$n]=1; echo "[$(date)] skip $n (RN_STOP: gate 6)" >> $L; started=1; break; fi
    if [ $a = RN50PF ]; then [ "$(alive RN50)" -ge "$MAXRN" ] && continue; need=$GRN; else need=$G34; fi
    if gate_try $need "pf2 $n"; then DONE[$n]=1; start "$n" "$k" "$a" "$o"; started=1; break; fi
  done
  [ $started = 1 ] || sleep 30
done
echo "[$(date)] pf2 queue: all jobs dispatched; waiting" >> $L
wait
echo "[$(date)] PF2 ALL TRAINED ($(grep -c 'trained pf2_.* rc=0' $L) rc 0)" >> $L
