#!/bin/bash
# x3 checks on gaint, CPU only (nice 19, <= 8 threads, CUDA_VISIBLE_DEVICES=""). Runs in tmux bench_x3_chk.
# 1 ref tree = git archive of 31c0c36 (el_bench untouched); 2 CPU identity 5 steps (identity_cpu.py 962379a6): SUP, SUPPF,
# and the two pp cards' rendered opts (= house_r34_unetpp_pf_v11 on cv5v2_v11_f0), ref vs bench_wt_x3; 3 pytest x3 + full;
# 4 scorer identity (default flags) vs the 31c0c36 dry records; 5 dry runs of the 4 tools on existing dumps.
set -u
IO=/home/noob/work/bench_x3_io; OUT=$IO/check; mkdir -p $OUT; L=$OUT/run.log
WT=/home/noob/work/bench_wt_x3; REF=$IO/ref_31c0c36
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $*" >> $L; }
log "x3 check start; bench_wt_x3 HEAD $(git -C $WT rev-parse --short HEAD); el_bench HEAD $(git -C /home/noob/work/el_bench rev-parse --short HEAD)"
if [ ! -d $REF ]; then
  mkdir -p $REF && git -C /home/noob/work/el_bench archive 31c0c36 | tar -x -C $REF
  for l in labeled escdd_masks unlabeled; do ln -s $(readlink /home/noob/work/el_bench/data/$l) $REF/data/$l; done
  log "ref tree $REF from git archive 31c0c36"
fi
H="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
R0=/home/noob/work/bench_data/roots/cv5v2_v11_f0
cd $WT
PPS=$($P -m bench.cards opts bench/methods/pp_src_calib_pf_v11.yaml --seed 5 --run-name x --data-root $R0 | tr ' ' '\n' | grep -v '^run_name=' | tr '\n' ' ')
PPD=$($P -m bench.cards opts bench/methods/pp_dti_pf_v11.yaml --seed 5 --run-name x --data-root $R0 | tr ' ' '\n' | grep -v '^run_name=' | tr '\n' ' ')
V11=$($P -m bench.cards opts bench/methods/house_r34_unetpp_pf_v11.yaml --seed 5 --run-name x --data-root $R0 | tr ' ' '\n' | grep -v '^run_name=' | tr '\n' ' ')
[ "$PPS" = "$V11" ] && [ "$PPD" = "$V11" ] && log "pp cards render the same opts as house_r34_unetpp_pf_v11: YES" || log "pp cards opts DIFFER from pf_v11"
declare -A OPT=([SUP]="$H" [SUPPF]="$H $PF" [PP_SRC]="$PPS" [PP_DTI]="$PPD")
for arm in SUP SUPPF PP_SRC PP_DTI; do
  for side in ref new; do
    code=$REF; [ $side = new ] && code=$WT
    nice -n 19 $P $ID --code $code --out $OUT/${arm}_$side.json --steps 5 --threads 8 --opts ${OPT[$arm]} > $OUT/${arm}_$side.log 2>&1
    rc=$?; log "$arm $side ($code) rc=$rc"
  done
  $P $CMP $OUT/${arm}_ref.json $OUT/${arm}_new.json > $OUT/${arm}_cmp.txt 2>&1
  rc=$?; log "$arm compare rc=$rc: $(cat $OUT/${arm}_cmp.txt)"
done
nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_x3.py > $OUT/pytest_x3.log 2>&1
rc=$?; log "pytest x3 rc=$rc: $(tail -1 $OUT/pytest_x3.log)"
nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1
rc=$?; log "pytest all rc=$rc: $(tail -1 $OUT/pytest_all.log)"
# scorer: default flags must reproduce the 31c0c36 records of the dry dump (cells compared, values never printed)
D=/home/noob/work/bench_dumps/w1g_dry/elbench1/house_r34_unetpp/b6_SUP_f0_s5_fp32/cv5v2_f0
rm -f $OUT/rec_default.json $OUT/rec_v11.json $OUT/rec_manifest.json $OUT/sum_cells.json
nice -n 19 $P scripts/bench_score.py records --dumps $D --set cv5v2_f0 --out $OUT/rec_default.json > $OUT/score.log 2>&1; log "records default rc=$?"
nice -n 19 $P scripts/bench_score.py records --dumps $D --set cv5v2_f0 --labels v11 --out $OUT/rec_v11.json >> $OUT/score.log 2>&1; log "records --labels v11 rc=$?"
nice -n 19 $P scripts/bench_score.py records --dumps $D --set cv5v2_f0 --labels manifest --out $OUT/rec_manifest.json >> $OUT/score.log 2>&1; log "records --labels manifest rc=$? (root b6_root_0 -> v1 labels)"
log "scorer default vs 31c0c36 dry records: $($P scripts/bench_score.py compare --a /home/noob/work/bench_check/w1g/dry_records_cv5v2_f0.json --b $OUT/rec_default.json 2>&1)"
log "scorer --labels v11 vs default: $($P scripts/bench_score.py compare --a $OUT/rec_default.json --b $OUT/rec_v11.json 2>&1)"
log "scorer --labels manifest (v1) vs default (v11), DIFF expected: $($P scripts/bench_score.py compare --a $OUT/rec_default.json --b $OUT/rec_manifest.json 2>&1 | cut -c1-60)"
nice -n 19 $P scripts/bench_score.py summary --records $OUT/rec_default.json --arms SUP='.*' --cells-tsv /home/noob/work/bench_data/meta/cells.tsv --out $OUT/sum_cells.json >> $OUT/score.log 2>&1
log "summary --cells-tsv rc=$? subsets: $($P -c "import json;print(sorted(json.load(open('$OUT/sum_cells.json'))['arms']['SUP']['subsets']))" | cut -c1-400)"
# dry runs of the four tools (pseudo folds over one 107-cell dump; the same dump as several seeds)
DRY=$IO/dry; rm -rf $DRY; mkdir -p $DRY
B=/home/noob/work/bench_dumps/gpu1/elbench1/house_r34_unetpp/b6_SUP_f0_s5_bf16/cv5v1_f0
printf "PF\t5\t$D\nPF\t6\t$D\nPF\t7\t$D\nPF\t8\t$D\nHOUSE\t5\t$B\nHOUSE\t6\t$B\n" > $DRY/runs.tsv
C="--runs-tsv $DRY/runs.tsv --labels v11 --pseudo-folds 5 --dry --workers 8 --boot 200 --cache $DRY"
nice -n 19 $P scripts/bench_read_w1.py $C --baseline PF --out $DRY > $DRY/read.log 2>&1; log "dry read_w1 rc=$? $(tail -1 $DRY/read.log)"
nice -n 19 $P scripts/bench_src_calib.py $C --out $DRY > $DRY/src.log 2>&1; log "dry src_calib rc=$? $(tail -1 $DRY/src.log)"
nice -n 19 $P scripts/bench_dti.py $C --out $DRY > $DRY/dti.log 2>&1; log "dry dti rc=$? $(tail -1 $DRY/dti.log)"
nice -n 19 $P scripts/bench_d0.py $C --out $DRY > $DRY/d0.log 2>&1; log "dry d0 rc=$? $(tail -1 $DRY/d0.log)"
log "dry tracebacks: $(cat $DRY/*.log | grep -c Traceback)"
log "x3 check done"
