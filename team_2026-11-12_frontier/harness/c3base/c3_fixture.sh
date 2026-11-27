#!/bin/bash
# integrator c3base: dump-path proof on gaint CPU. (1) 300-step CPU fixture of PF v11 on cv5v3_v11_f0, seed 5 (as the rows2
# fixtures: 5-step fixtures fail dumpfmt's near-tie check); (2) bench_infer --set cv5v3_f0 (CPU fp32, --logp) from bench_wt_final;
# (3) read guard: bench_read_w1 on that dump with --groups bench_data_v3b/meta/cv5v3_groups.tsv must pass the guard, without
# --groups (default cv5v2 groups) and with cv5v2_groups.tsv must be refused. Only rc, Traceback counts and guard lines are
# logged; no metric file is opened. CPU only, nice 19, OMP 4. Log $IO/fix/run.log. Usage: bash c3_fixture.sh (tmux bench_c3_fix)
set -u
IO=/home/noob/work/bench_c3_io; F=$IO/fix; mkdir -p $F/exp $F/dumps $F/read; L=$F/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python; NEW=/home/noob/work/bench_wt_final
V0=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0; G3=/home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv
G2=/home/yugma/mtp/research/team_2026-11-12_frontier/benchmark/splits/cv5v2_groups.tsv
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $*" >> $L; }
n=fx300_c3_pf_v11_f0; C=bench/methods/house_r34_unetpp_pf_v11.yaml
log "start; new HEAD $(git -C $NEW rev-parse --short HEAD); script $(md5sum < $0 | cut -c1-8)"
if [ ! -e $F/exp/$n/checkpoints/latest.pth ]; then
  o=$(cd $NEW && $P -m bench.cards opts $C --seed 5 --run-name $n --data-root $V0)
  (cd $NEW && nice -n 19 $P scripts/train.py --config configs/supervised.yaml --device cpu --opts $o training.total_steps=300 training.val_every=300 training.checkpoint_every=300 training.num_workers=0 logging.experiments_dir=$F/exp > $F/exp/$n.stdout 2>&1)
  log "$n rc=$? Traceback $(grep -c Traceback $F/exp/$n.stdout) nan $(grep -ciE 'loss[^|]*nan' $F/exp/$n/train.log) step-300 lines $(grep -c 'step 300/300' $F/exp/$n/train.log) latest.pth $(ls $F/exp/$n/checkpoints/latest.pth 2>/dev/null | wc -l) | $(grep -o 'Labelled: .*test: [0-9]*' $F/exp/$n/train.log | head -1) | cfgcheck differs only in the overrides: $(cd $NEW && $P -m bench.cards cfgcheck $C --config $F/exp/$n/config_used.yaml --seed 5 --run-name $n --data-root $V0 | sed -E "s#'$F/exp'#E#g" | cut -c1-400)"
fi
(cd $NEW && nice -n 19 $P scripts/bench_infer.py --run $F/exp/$n --set cv5v3_f0 --dumps $F/dumps --method house_r34_unetpp_pf_v11 --card $C --run-id $n --device cpu --precision fp32 --threads 4 --workers 0 --batch 8 --logp --forbidden /home/noob/work/bench_data_v3b/meta/forbidden_v1.txt --bench-run dump_$n > $F/infer.log 2>&1)
log "bench_infer --set cv5v3_f0 rc=$? Traceback $(grep -c Traceback $F/infer.log): $(grep '^dumped ' $F/infer.log | cut -c1-200) | npz files $(find $F/dumps -name '*.npz' | wc -l)"
A="PF=$F/dumps/elbench1/house_r34_unetpp_pf_v11:$n"
rd() {  # tag extra-args
  (cd $NEW && nice -n 19 $P scripts/bench_read_w1.py --arm "$A" --baseline PF --labels v11 --out $F/read/$1 --workers 4 --boot 200 --allow-partial ${2:+$2} > $F/read/$1.log 2>&1)
  log "read $1 (${2:-no --groups}) rc=$? | guard refusal lines $(grep -c 'cv5v3 runs need the cv5v3 groups' $F/read/$1.log) | Traceback $(grep -c Traceback $F/read/$1.log) | last error: $(grep -E 'Error|assert' $F/read/$1.log | tail -1 | cut -c1-220)"; }
rd g3 "--groups $G3"
rd nog ""
rd g2 "--groups $G2"
log "ALL DONE"
