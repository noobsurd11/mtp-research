#!/bin/bash
# elbench GPU identity checks, ONE script, run only on the lead's word, inside tmux bench_gpuchk on gaint:
#   tmux has-session -t "=bench_gpuchk" || tmux new-session -d -s bench_gpuchk "bash /home/noob/work/bench_check/gpu/run_gpu_checks.sh"
# Each GPU pass waits on the shared gate (gpu_gate dir, free >= 9,900 MiB = GS, >= 120 s since any start). b6 scorer peak 3,292 MiB.
#   I1b: cuda bf16 dump of f3_SUPPF_100pct_s0 val54 == b6 GPU check record (= opening-1 m0 val block, build_b6 s9)   expect IDENTICAL
#   I2 : cuda bf16 dump of b6_SUP_f0_s5 on cv5v1_f0 == its b6_score record (b6_score/out)                              expect IDENTICAL
#   I1c: cuda fp32 (TF32 off) dump of f3_SUPPF_100pct_s0 val54 vs the bf16 one: DIFF counts only (size of the precision effect)
# Prints only IDENTICAL / DIFF with counts. rc captured before any $(date).
set -u
O=/home/noob/work/bench_check/gpu/out; mkdir -p $O; L=$O/run.log; DU=/home/noob/work/bench_dumps/gpu1
P=/home/noob/work/el-fault-detection/.venv/bin/python; R=/home/noob/work/el_bench
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
. $R/bench/q/bench_gate.sh
cd $R
gate(){ until gate_try 9900 "bench $1"; do sleep 30; done; echo "[$(date '+%F %T')] gate pass $1 (free $(timeout 5 nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L; }
infer(){ local tag=$1 run=$2 set=$3 card=$4 prec=$5 id=$6
  gate $tag
  nice -n 19 $P scripts/bench_infer.py --run $run --set $set --dumps $DU --method $(basename $card .yaml) --card $card --run-id $id \
    --device cuda --precision $prec --threads 4 --workers 4 --batch 8 > $O/$tag.infer.log 2>&1 &
  pp=$!; echo $pp > $O/$tag.pid; echo "[$(date '+%F %T')] $tag python pid $pp: $(tr '\0' ' ' < /proc/$pp/cmdline | cut -c1-200)" >> $L
  wait $pp; rc=$?; echo "[$(date '+%F %T')] $tag infer rc=$rc: $(tail -1 $O/$tag.infer.log)" >> $L
  nice -n 19 $P scripts/bench_score.py records --dumps $DU/elbench1/$(basename $card .yaml)/$id/$set --set $set --out $O/$tag.rec.json > $O/$tag.rec.log 2>&1
  rc=$?; echo "[$(date '+%F %T')] $tag records rc=$rc" >> $L; }
cmp_(){ local tag=$1 a=$2 b=$3 key=$4
  $P scripts/bench_score.py compare --a $a --b $b --b-cells $key > $O/$tag.cmp.txt 2>&1; rc=$?
  echo "[$(date '+%F %T')] $tag compare rc=$rc: $(cat $O/$tag.cmp.txt)" >> $L; }
GQ=$O/gm; mkdir -p $GQ; touch $GQ/launch.log
tmux new-window -t "=bench_gpuchk:" -n gm "Q=$GQ nice -n 19 bash $R/bench/q/bench_gpumem.sh"
sleep 3; echo "[$(date '+%F %T')] gpu checks start pid $$, el_bench $(git -C $R rev-parse --short HEAD), 1 s gpumem pid $(cat $GQ/gpumem.pid 2>/dev/null)" >> $L
infer I1b /home/noob/work/b6_build/check/runs/f3_SUPPF_100pct_s0 val54 bench/methods/house_r34_unetpp_pf.yaml bf16 f3_SUPPF_100pct_s0_bf16
cmp_ I1b $O/I1b.rec.json /home/noob/work/b6_build/check/out_gpu/f3_SUPPF_100pct_s0.check.json cells/heldout
infer I2 /home/noob/work/cv02_noob_el/el_b6/experiments/b6_SUP_f0_s5 cv5v1_f0 bench/methods/house_r34_unetpp.yaml bf16 b6_SUP_f0_s5_bf16
cmp_ I2 $O/I2.rec.json /home/noob/work/b6_score/out/b6_SUP_f0_s5.b6.json cells/heldout
infer I1c /home/noob/work/b6_build/check/runs/f3_SUPPF_100pct_s0 val54 bench/methods/house_r34_unetpp_pf.yaml fp32 f3_SUPPF_100pct_s0_fp32
cmp_ I1c_vs_bf16 $O/I1c.rec.json $O/I1b.rec.json cells
echo "[$(date '+%F %T')] gpu checks done; peak MiB per bench_infer pid: $(for t in I1b I2 I1c; do p=$(cat $O/$t.pid); echo -n "$t $(grep -oE " $p:[^ ]*:[0-9]+" $GQ/gpumem.log | awk -F: '{print $NF}' | sort -n | tail -1) "; done)" >> $L
echo "BENCH Q ALL DONE (gpu checks)" >> $GQ/launch.log
