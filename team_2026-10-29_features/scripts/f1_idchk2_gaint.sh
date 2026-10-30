#!/bin/bash
# F1 I1 (1,000 steps: el_m 1be64e1 vs el_f1 603e0d5, encoder_init unset) and I2 (el_f1 + encoder_init=mim_step0.pth,
# 1,000 steps) on gaint, sequential, cwd el_f1 (same data). A5c opts seed 0.
set -u
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=/home/noob/work/el_f1/reports/f1/idchk2
mkdir -p $OUT
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
OPTS="seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
cd /home/noob/work/el_f1
cp reports/f1/smoke_v1/mim_step0.pth $OUT/mim_step0.pth; md5sum $OUT/mim_step0.pth > $OUT/status.txt
$P /home/noob/work/el_m/scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts $OPTS run_name=i1_elm logging.experiments_dir=$OUT > $OUT/i1_elm.stdout 2>&1; echo "i1_elm rc=$?" >> $OUT/status.txt
$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts $OPTS run_name=i1_f1 logging.experiments_dir=$OUT > $OUT/i1_f1.stdout 2>&1; echo "i1_f1 rc=$?" >> $OUT/status.txt
$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 1000 --opts $OPTS run_name=i2_f1_step0 logging.experiments_dir=$OUT model.encoder_init=$OUT/mim_step0.pth > $OUT/i2_f1_step0.stdout 2>&1; echo "i2 rc=$?" >> $OUT/status.txt
ext(){ grep -E "src.trainers.trainer — (step|val @)" $1 | sed -E "s/^[0-9-]+ [0-9:,]+ //; s/ +steps_per_sec=[0-9.]+//"; }
ext $OUT/i1_elm.stdout > $OUT/i1_elm.lines; ext $OUT/i1_f1.stdout > $OUT/i1_f1.lines; ext $OUT/i2_f1_step0.stdout > $OUT/i2.lines
echo "lines $(wc -l < $OUT/i1_elm.lines) $(wc -l < $OUT/i1_f1.lines) $(wc -l < $OUT/i2.lines)" >> $OUT/status.txt
cmp -s $OUT/i1_elm.lines $OUT/i1_f1.lines && echo "I1 IDENTICAL_1000" >> $OUT/status.txt || echo "I1 DIFFER" >> $OUT/status.txt
cmp -s $OUT/i1_f1.lines $OUT/i2.lines && echo "I2 IDENTICAL_1000" >> $OUT/status.txt || echo "I2 DIFFER" >> $OUT/status.txt
grep "Encoder initialised" $OUT/i2_f1_step0.stdout | cut -c1-250 >> $OUT/status.txt
echo ALLDONE >> $OUT/status.txt
