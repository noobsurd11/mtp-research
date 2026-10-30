#!/bin/bash
# F1 identity + encoder_init smoke on gaint (sequential, one GPU). 500 steps each (includes the step-500 val line).
# 1) el_m 1be64e1, A5c opts, seed 0;  2) el_f1 fe31831, same opts (switch off);  3) el_f1 + model.encoder_init (smoke encoder).
set -u
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=/home/noob/work/el_f1/reports/f1/idchk
mkdir -p $OUT
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
OPTS="seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
cd /home/noob/work/el_f1
$P - <<'PY'
import torch
st = torch.load("reports/f1/smoke_mim_b16/ckpt_latest.pth", map_location="cpu", weights_only=False)
sd = {k: v for k, v in st["model"].items() if k.startswith("encoder.")}
torch.save(sd, "reports/f1/idchk/smoke_encoder_step240.pth"); print("smoke encoder tensors", len(sd), "step", st["step"])
PY
cd /home/noob/work/el_m
$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 500 --opts $OPTS run_name=idchk_elm_A5_s0 logging.experiments_dir=$OUT > $OUT/idchk_elm_A5_s0.stdout 2>&1; echo "elm rc=$?" >> $OUT/status.txt
cd /home/noob/work/el_f1
$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 500 --opts $OPTS run_name=idchk_f1_A5_s0 logging.experiments_dir=$OUT > $OUT/idchk_f1_A5_s0.stdout 2>&1; echo "f1off rc=$?" >> $OUT/status.txt
$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 200 --opts $OPTS run_name=smoke_f1_MIMinit_s0 logging.experiments_dir=$OUT model.encoder_init=$OUT/smoke_encoder_step240.pth > $OUT/smoke_f1_MIMinit_s0.stdout 2>&1; echo "f1on rc=$?" >> $OUT/status.txt
echo ALLDONE >> $OUT/status.txt
