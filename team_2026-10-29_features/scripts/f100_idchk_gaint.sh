#!/bin/bash
# 100% identity smoke on gaint (team-lead 30 Oct): SUP100 opts (A5c opts with data.labeled_fraction=1.0), seed 0,
# --exit_after_step 1000, cwd el_f2 (same data for every code). Smoke only (no protocol run).
#   I1-100   el_m 1be64e1 (Track M SUP100 code)  vs  el_f2 2751aa8, no switch
#   I1f1-100 el_f1 603e0d5, no switch            vs  el_m
#   I2-100   el_f2 + model.encoder_init=mim_step0.pth (ImageNet start saved through the MIM path)  vs  el_f2 no switch
# Each start waits for 9,000 MiB free (own peak 6.8 GB + 2 GB) and 90 s after the previous start.
set -u
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=/home/noob/work/el_f2/reports/f100/idchk; mkdir -p $OUT
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
OPTS="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth
cd /home/noob/work/el_f2
md5sum $S0 > $OUT/status.txt; md5sum data/splits/train.txt /home/noob/work/el_m/data/splits/train.txt >> $OUT/status.txt
wfree(){ while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt 9000 ]; do sleep 30; done; }
run(){ name=$1; code=$2; shift 2; wfree
  $P $code/scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts $OPTS "$@" \
     run_name=$name logging.experiments_dir=$OUT > $OUT/$name.stdout 2>&1; echo "$name rc=$?" >> $OUT/status.txt; }
run i1_elm /home/noob/work/el_m & sleep 90
run i1_f2 /home/noob/work/el_f2 & sleep 90
run i2_f2_step0 /home/noob/work/el_f2 model.encoder_init=$S0 & sleep 90
run i1_f1 /home/noob/work/el_f1 &
wait
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//"; }
for n in i1_elm i1_f2 i2_f2_step0 i1_f1; do ext $OUT/$n.stdout > $OUT/$n.lines; done
echo "lines $(wc -l < $OUT/i1_elm.lines) $(wc -l < $OUT/i1_f2.lines) $(wc -l < $OUT/i2_f2_step0.lines) $(wc -l < $OUT/i1_f1.lines)" >> $OUT/status.txt
grep -h "Labelled:" $OUT/i1_elm.stdout | cut -c1-160 >> $OUT/status.txt
cmp -s $OUT/i1_elm.lines $OUT/i1_f2.lines && echo "I1-100 (el_m vs el_f2) IDENTICAL_1000" >> $OUT/status.txt || echo "I1-100 (el_m vs el_f2) DIFFER" >> $OUT/status.txt
cmp -s $OUT/i1_elm.lines $OUT/i1_f1.lines && echo "I1f1-100 (el_m vs el_f1) IDENTICAL_1000" >> $OUT/status.txt || echo "I1f1-100 (el_m vs el_f1) DIFFER" >> $OUT/status.txt
cmp -s $OUT/i1_f2.lines $OUT/i2_f2_step0.lines && echo "I2-100 (el_f2 vs el_f2+mim_step0) IDENTICAL_1000" >> $OUT/status.txt || echo "I2-100 DIFFER" >> $OUT/status.txt
grep -h "Encoder initialised" $OUT/i2_f2_step0.stdout | cut -c1-250 >> $OUT/status.txt
echo ALLDONE >> $OUT/status.txt
