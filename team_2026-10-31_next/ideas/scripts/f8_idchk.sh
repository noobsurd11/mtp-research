#!/bin/bash
# found, 31 Oct 2026: CPU bit-identity + flag-on sanity for el_f8 (hrstem_unetpp wrapper), with builder's harness read-only
# (builder_scratch/identity_cpu.py md5 962379a6). Reference records: builder's A_e544133_house.json / C_e544133_pf.json
# (e544133 export) are re-run here as well, so the comparison is same-day, same machine. nice 19, 8 threads, CPU only.
set -u
B=/home/noob/work/builder_scratch; H=$B/identity_cpu.py; O=/home/noob/work/found/f8_idchk; P=/home/noob/work/el-fault-detection/.venv/bin/python
mkdir -p $O; export OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 CUDA_VISIBLE_DEVICES=""
HOUSE="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
SHORT="training.total_steps=4000 training.warmup_steps=200 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
F8=/home/noob/work/el_f8; E=$B/e544133; N=5
run(){ name=$1; code=$2; n=$3; shift 3; nice -n 19 $P $H --code $code --out $O/$name.json --steps $n --opts "$@" > $O/$name.log 2>&1; rc=$?; echo "[$(date +%T)] $name rc=$rc" >> $O/batch.log; }
echo "[$(date +%T)] start; el_f8 HEAD $(git -C $F8 rev-parse --short HEAD) dirty=$(git -C $F8 status --short | wc -l); harness $(md5sum $H | cut -c1-8)" >> $O/batch.log
run A_e544133_house $E $N $HOUSE
run B_f8_house      $F8 $N $HOUSE
run C_e544133_pf    $E $N $HOUSE $PF
run D_f8_pf         $F8 $N $HOUSE $PF
run X_f8_cnx_tv_short $F8 3 $HOUSE $SHORT model.name=hrstem_unetpp model.backbone=convnext_tiny model.backbone_weights=/home/noob/.cache/torch/hub/checkpoints/convnext_tiny-983f1562.pth model.backbone_weights_format=torchvision_convnext
run Y_f8_hiera_short  $F8 2 $HOUSE $SHORT model.name=hrstem_unetpp model.backbone=sam2_hiera_tiny model.backbone_weights=/home/noob/work/weights/timm_sam2_hiera_tiny_fb_r896.safetensors
echo "[$(date +%T)] done" >> $O/batch.log
