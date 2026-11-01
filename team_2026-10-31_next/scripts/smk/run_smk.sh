#!/bin/bash
# runner (1 Nov): wrapper for one smoke script at a time. 1 s gpumem via gpu_gate/FAST (THIN gpumem logger reads it).
# FAST is removed at the end only if the THIN opening is not in progress (thin_post.sh owns FAST during its opening).
# Usage: bash run_smk.sh <label> <workdir> <command...>
set -u
lab=$1; wd=$2; shift 2
GG=/home/noob/work/gpu_gate; LL=/home/noob/work/el_thin/reports/thin/q/launch.log; RL=/home/noob/work/runner_smk/runner_smk.log
touch $GG/FAST
echo "[$(date "+%F %T")] $lab start (pid $$): $*" >> $RL
cd "$wd" && "$@"; rc=$?
if grep -q "thin scoring start" $LL && ! grep -qE "thin scoring done|thin NOT scored|thin post FAIL" $LL; then keep=1; else keep=0; fi
[ $keep = 0 ] && rm -f $GG/FAST
echo "[$(date "+%F %T")] $lab end rc=$rc (FAST kept=$keep)" >> $RL
