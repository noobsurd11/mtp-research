#!/bin/bash
# CPU identity of el_bench vs the source worktrees (5 steps, identity_cpu.py 962379a6). CPU only, nice 19, 8 threads.
set -u
OUT=/home/noob/work/bench_check/id; mkdir -p $OUT; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
H="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
A8="seed=0 data.labeled_fraction=1.0 training.total_steps=4000 training.warmup_steps=200 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=4000 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 model.name=hrstem_unetpp model.backbone=convnext_tiny.dinov3_lvd1689m model.backbone_weights=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors model.backbone_weights_format=timm model.backbone_drop_path=0.0"
declare -A REF=([SUP]=/home/noob/work/el_f3 [SUPPF]=/home/noob/work/el_f3 [SKR01]=/home/noob/work/el_thin [A8]=/home/noob/work/el_f8)
declare -A OPT=([SUP]="$H" [SUPPF]="$H $PF" [SKR01]="$H $PF loss.skel_recall.weight=0.1" [A8]="$A8")
for arm in SUP SUPPF SKR01 A8; do
  for side in ref bench; do
    code=${REF[$arm]}; [ $side = bench ] && code=/home/noob/work/el_bench
    nice -n 19 $P $ID --code $code --out $OUT/${arm}_$side.json --steps 5 --threads 8 --opts ${OPT[$arm]} > $OUT/${arm}_$side.log 2>&1
    rc=$?; echo "[$(date '+%F %T')] $arm $side ($code) rc=$rc" >> $L
  done
  $P /home/noob/work/bench_check/compare_id.py $OUT/${arm}_ref.json $OUT/${arm}_bench.json > $OUT/${arm}_cmp.txt 2>&1
  rc=$?; echo "[$(date '+%F %T')] $arm compare rc=$rc: $(cat $OUT/${arm}_cmp.txt)" >> $L
done
cd /home/noob/work/el_bench && nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_bench.log 2>&1
rc=$?; echo "[$(date '+%F %T')] pytest el_bench rc=$rc: $(tail -1 $OUT/pytest_bench.log)" >> $L
echo "[$(date '+%F %T')] identity run done" >> $L
