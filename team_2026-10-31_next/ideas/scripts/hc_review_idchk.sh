#!/bin/bash
# found (HC review, 1 Nov 2026): CPU identity of el_hc c2e6973 vs the e544133 export, builder's harness read-only
# (identity_cpu.py md5 962379a6); references = found's own e544133 records (f8_idchk A / C, same harness and machine).
set -u
B=/home/noob/work/builder_scratch; H=$B/identity_cpu.py; O=/home/noob/work/found/hc_review; P=/home/noob/work/el-fault-detection/.venv/bin/python
mkdir -p $O; export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES=""
HOUSE="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
SH0="data.synth_halfcut.p=0 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv"
SH35="data.synth_halfcut.p=0.35 data.synth_halfcut.pool=data/splits/synth_halfcut_pool_ap.tsv"
HC=/home/noob/work/el_hc
run(){ name=$1; shift; nice -n 19 $P $H --code $HC --out $O/$name.json --steps 5 --opts "$@" > $O/$name.log 2>&1; rc=$?; echo "[$(date +%T)] $name rc=$rc" >> $O/batch.log; }
echo "[$(date +%T)] start; el_hc HEAD $(git -C $HC rev-parse --short HEAD) tracked-dirty=$(git -C $HC status --short --untracked-files=no | wc -l); harness $(md5sum $H | cut -c1-8)" >> $O/batch.log
run HCa_house  $HOUSE
run HCb_pf     $HOUSE $PF
run HCc_pf_p0  $HOUSE $PF $SH0
run HCd_pf_p35 $HOUSE $PF $SH35
echo "[$(date +%T)] done" >> $O/batch.log
