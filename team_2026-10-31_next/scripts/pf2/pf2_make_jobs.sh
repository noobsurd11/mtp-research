#!/bin/bash
# Writes the 15 PF2 job lines (reports/pf2/pf2_jobs.txt): "name|seed|arm|opts". The queue refuses to start unless the file's
# md5 equals the one recorded in protocol_PF2.md. Opts are protocol_100's (f100_queue.sh) + val off; RN50-PF = SUP100-PF + encoder.
cd /home/noob/work/el_f3
B="data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
RN="model.encoder_name=resnet50"
for k in 5 6 7 8 9; do
  echo "pf2_SUP_100pct_s$k|$k|SUP|seed=$k $B run_name=pf2_SUP_100pct_s$k"
  echo "pf2_SUPPF_100pct_s$k|$k|SUPPF|seed=$k $B $PF run_name=pf2_SUPPF_100pct_s$k"
  echo "pf2_RN50PF_100pct_s$k|$k|RN50PF|seed=$k $B $PF $RN run_name=pf2_RN50PF_100pct_s$k"
done > reports/pf2/pf2_jobs.txt
md5sum reports/pf2/pf2_jobs.txt
