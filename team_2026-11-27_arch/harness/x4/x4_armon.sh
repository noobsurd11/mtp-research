#!/bin/bash
# x4 integrator: arm-on equality after a merge. identity_cpu.py (962379a6) 5 CPU steps with the ARM's card opts (seed 5,
# cv5v3 f0) on the builder's commit (git archive) and on the merged commit (git archive); compare_id.py must print IDENTICAL.
# Usage: bash x4_armon.sh <card> <builder commit> <merged commit>   (gaint, CPU, nice 19; tmux)
set -u
CARD=$1; BC=$2; MC=$3; IO=/home/noob/work/bench_x4_int; O=$IO/armon_${CARD}_${BC:0:7}_${MC:0:7}; mkdir -p $O
P=/home/noob/work/el-fault-detection/.venv/bin/python; ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
R0=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0; G=/home/noob/work/bench_wt_x4
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=12 MKL_NUM_THREADS=12 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
for c in $BC $MC; do T=$IO/tree_${c:0:7}; [ -d $T ] || { mkdir -p $T && git -C $G archive $c | tar -x -C $T; }; done
opts=$(cd $IO/tree_${MC:0:7} && $P -m bench.cards opts bench/methods/$CARD.yaml --seed 5 --run-name x --data-root $R0 | tr ' ' '\n' | grep -v '^run_name=' | tr '\n' ' ')
nice -n 19 $P $ID --code $IO/tree_${BC:0:7} --out $O/builder.json --steps 5 --threads 12 --opts $opts > $O/builder.log 2>&1 & p=$!
nice -n 19 $P $ID --code $IO/tree_${MC:0:7} --out $O/merged.json --steps 5 --threads 12 --opts $opts > $O/merged.log 2>&1; r2=$?; wait $p; r1=$?
echo "[$(date '+%F %T')] armon $CARD builder ${BC:0:7} rc $r1, merged ${MC:0:7} rc $r2: $($P $CMP $O/builder.json $O/merged.json 2>&1)" | tee -a $IO/armon.log
