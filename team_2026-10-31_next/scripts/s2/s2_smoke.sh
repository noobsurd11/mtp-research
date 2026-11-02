#!/bin/bash
# runner DRAFT (2 Nov 2026): SKR2 / HC2 smokes (protocol_SKR2_HC2 v0.9 §6), 1,000 steps each of the real 20k schedule, seed 0
# (names skr2_smk_SKR01_s0 / hc2_smk_HC0175_s0, never a protocol seed), one at a time, each start through the shared gate
# (gpu_gate.sh: flock, free >= gate, >= 120 s since any start, HOLD); gates SKR01 9,100 / HC2 9,000 (= the queue's).
# Opts = s2q_jobs.txt line of the arm's s5 with seed=0 and the smoke name (no other change), + --exit_after_step 1000 (hard exit
# before any TEST block). Checks per smoke (s2_smoke_parse.py, step / thin / synth lines only, never the rest of the stdout):
# finite losses, 0 Tracebacks, SKR01 'thin ... at step' lines present, HC2 live synthetic share and eligible share (expected ~0.13 /
# ~0.74), nvidia-smi peak of its own pid (1 s), min free; and its config_used.yaml diff vs pf2_SUPPF_100pct_s5 == exp_<arm>.txt.
# Memory guard as smoke_a8.sh: free < 2,200 MiB on 2 consecutive 1 s samples stops ONLY this smoke's own python PID (command line
# printed to the log first). rc captured before $(date). Usage: bash s2_smoke.sh SKR01 HC2
set -u
source /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
export CUDA_VISIBLE_DEVICES=0 HF_HUB_OFFLINE=1
P=/home/noob/work/el-fault-detection/.venv/bin/python; Q=/home/noob/work/s2q; O=/home/noob/work/runner_smk/s2; mkdir -p $O; L=$O/smoke.log
REF=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
declare -A WT=([SKR01]=/home/noob/work/el_thin [HC2]=/home/noob/work/el_hc) DEP=([SKR01]=c9bbb02 [HC2]=c2e6973) GATE=([SKR01]=9100 [HC2]=9000)
declare -A NM=([SKR01]=skr2_smk_SKR01_s0 [HC2]=hc2_smk_HC0175_s0) S5=([SKR01]=skr2_SKR01_100pct_s5 [HC2]=hc2_HC0175_100pct_s5)
guard(){ local pid=$1 mem=$2 low=0 f
  while kill -0 "$pid" 2>/dev/null; do
    f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
    echo "$(date +%T) free $f | $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ')" >> "$mem"
    if [ "$f" -lt 2200 ]; then low=$((low+1)); else low=0; fi
    if [ $low -ge 2 ]; then
      echo "[$(date)] GUARD: free $f < 2200 twice; stopping own smoke PID $pid: $(ps -o args= -p "$pid" | cut -c1-200)" >> $L
      kill "$pid"; low=0; fi
    sleep 1; done; }
for a in "$@"; do
  w=${WT[$a]:-}; [ -n "$w" ] || { echo "[$(date)] unknown arm $a" >> $L; continue; }
  n=${NM[$a]}; cd $w || exit 1
  if [ "$(git rev-parse --short=7 HEAD)" != "${DEP[$a]}" ] || [ "$(cut -c1-7 REVISION)" != "${DEP[$a]}" ] || [ -n "$(git status --short --untracked-files=no)" ]; then
    echo "[$(date)] deploy check FAIL $a ($w != ${DEP[$a]} or tracked changes)" >> $L; exit 1; fi
  [ ! -e experiments/$n ] || { echo "[$(date)] $n exists; refusing" >> $L; exit 1; }
  opts=$(grep "^${S5[$a]}|" $Q/s2q_jobs.txt | cut -d'|' -f4 | sed -e "s/^seed=5 /seed=0 /" -e "s/ run_name=${S5[$a]}\$/ run_name=$n/")
  case "$opts" in "seed=0 "*" run_name=$n") ;; *) echo "[$(date)] opts derivation FAIL $a" >> $L; exit 1;; esac
  gate_wait ${GATE[$a]} "s2-smoke $n"
  echo "[$(date)] start $n (gate ${GATE[$a]})" >> $L
  $P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts $opts > experiments/$n.stdout 2>&1 &
  pid=$!; echo "$pid $n $(date +%T)" >> $O/pids.txt
  guard $pid $O/$n.gpumem.txt
  wait $pid; rc=$?
  echo "[$(date)] trained $n rc=$rc (3 = planned exit at 1000)" >> $L
  c=experiments/$n/config_used.yaml
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $REF) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  if [ "$d" = "$(sort $Q/exp_$a.txt)" ] && grep -qx "seed: 0" $c; then echo "  config OK $n: diff vs pf2_SUPPF_100pct_s5 = exp_$a.txt, seed 0" >> $L
  else echo "  CONFIG MISMATCH $n: [$(echo "$d" | tr '\n' ' ')]" >> $L; fi
  $P -I /home/noob/work/runner_smk/s2_smoke_parse.py $a experiments/$n $O/$n.gpumem.txt $pid >> $L 2>&1
done
echo "[$(date)] s2 smokes done: $*" >> $L
