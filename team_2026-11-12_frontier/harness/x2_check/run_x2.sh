#!/bin/bash
# x2 checks on gaint, CPU only (nice 19, 8 threads, no GPU). Log /home/noob/work/bench_x2_io/check/run.log.
# 1. pytest: x2 tests + card tests, then the full suite of bench_wt_x2.
# 2. flag-off identity, 5 CPU steps (identity_cpu.py 962379a6): ref = git archive of el_bench 31c0c36
#    (bench_x2_io/ref_31c0c36; el_bench itself untouched), new = bench_wt_x2; arms SUP, SUPPF (legacy root, house
#    flags as bench_check/run_identity.sh) and PFV11 (card house_r34_unetpp_pf_v11 rendered on cv5v2_v11_f0).
# 3. 5-step CPU runs of the x2 arms on bench_wt_x2 (same script, records only): soft_band_jml, jml_hard (cards),
#    cc_dicece and scnp (PF v11 card + loss.cc.weight=1.0 / loss.scnp.enabled=true).
set -u
OUT=/home/noob/work/bench_x2_io/check; mkdir -p $OUT; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py
CMP=/home/noob/work/bench_check/compare_id.py
REF=/home/noob/work/bench_x2_io/ref_31c0c36; NEW=/home/noob/work/bench_wt_x2
ROOT0=/home/noob/work/bench_data/roots/cv5v2_v11_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $*" >> $L; }
log "start: ref $REF ($(cat $REF/REVISION)), new $NEW ($(git -C $NEW rev-parse --short HEAD), $(git -C $NEW status --porcelain | wc -l) changed paths), identity_cpu $(md5sum < $ID | cut -c1-8)"

cd $NEW
nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_x2_losses.py tests/test_x2_cards.py tests/test_bench_cards.py tests/test_bench_cards_v11.py > $OUT/pytest_x2.log 2>&1
rc=$?; log "pytest x2 + cards rc=$rc: $(tail -1 $OUT/pytest_x2.log)"

H="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
card_opts() { (cd $NEW && $P -m bench.cards opts bench/methods/$1.yaml --seed 5 --run-name idx2_$1 --data-root $ROOT0 | tr '\n' ' '); }
V11=$(card_opts house_r34_unetpp_pf_v11)
log "PFV11 opts: $V11"
declare -A OPT=([SUP]="$H" [SUPPF]="$H $PF" [PFV11]="$V11")
for arm in SUP SUPPF PFV11; do
  for side in ref new; do
    code=$REF; [ $side = new ] && code=$NEW
    nice -n 19 $P $ID --code $code --out $OUT/${arm}_$side.json --steps 5 --threads 8 --opts ${OPT[$arm]} > $OUT/${arm}_$side.log 2>&1
    rc=$?; log "$arm $side rc=$rc"
  done
  $P $CMP $OUT/${arm}_ref.json $OUT/${arm}_new.json > $OUT/${arm}_cmp.txt 2>&1
  rc=$?; log "$arm compare rc=$rc: $(cat $OUT/${arm}_cmp.txt)"
done

SB=$(card_opts soft_band_jml); JH=$(card_opts jml_hard)
declare -A AOPT=([soft_band_jml]="$SB" [jml_hard]="$JH" [cc_dicece]="$V11 loss.cc.weight=1.0" [scnp]="$V11 loss.scnp.enabled=true")
for arm in soft_band_jml jml_hard cc_dicece scnp; do
  nice -n 19 $P $ID --code $NEW --out $OUT/arm_$arm.json --steps 5 --threads 8 --opts ${AOPT[$arm]} > $OUT/arm_$arm.log 2>&1
  rc=$?; log "arm $arm 5 CPU steps rc=$rc loss_class=$(grep -o '"loss_class": "[A-Za-z]*"' $OUT/arm_$arm.json | cut -d'"' -f4) steps=$(grep -c '^{"step"' $OUT/arm_$arm.log) nan=$(grep -c -i 'nan' $OUT/arm_$arm.log) Traceback=$(grep -c Traceback $OUT/arm_$arm.log)"
done

nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1
rc=$?; log "pytest full suite bench_wt_x2 rc=$rc: $(tail -1 $OUT/pytest_all.log)"
log "x2 check run done"
