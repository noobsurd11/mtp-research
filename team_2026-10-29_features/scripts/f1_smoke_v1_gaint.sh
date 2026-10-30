#!/bin/bash
# F1 v1 smoke on gaint (review_mim5_v0 C3, S1-S3). 1) width timing 512 vs 256 (batch 16, encoder unfrozen, 100 steps);
# 2) S1: real schedule in steps (batch 16 with freeze/warmup 0.5 epoch = 343 steps = 2 epochs at batch 64), freeze +
#    ~200 steps (stop at 560), monitor every 280 steps; width chosen by the C3 rule (>= 1.6x samples/s -> 256).
set -u
cd /home/noob/work/el_f1
P=/home/noob/work/el-fault-detection/.venv/bin/python
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
R=reports/f1; L=$R/mim_pool_v1.txt; M=$R/mim_monitor_v1.txt
for w in 512 256; do
  $P scripts/pretrain_mim.py --list $L --data_root data --out $R/timing_w$w --batch 16 --width $w --freeze_enc_epochs 0 \
     --enc_warmup_steps 1 --max_steps 100 --log_every 50 --ckpt_every 100000 > $R/timing_w$w.stdout 2>&1
done
s512=$(grep "step 100/" $R/timing_w512.stdout | sed -E 's/.*samples\/s=([0-9.]+).*/\1/')
s256=$(grep "step 100/" $R/timing_w256.stdout | sed -E 's/.*samples\/s=([0-9.]+).*/\1/')
W=$(python3 -c "print(256 if $s256 >= 1.6 * $s512 else 512)")
echo "timing samples/s w512 $s512 w256 $s256 -> width $W" | tee $R/width_choice.txt
$P scripts/pretrain_mim.py --list $L --monitor_list $M --data_root data --out $R/smoke_v1 --batch 16 --width $W \
   --freeze_enc_epochs 0.5 --warmup_epochs 0.5 --enc_warmup_steps 1000 --max_steps 560 --log_every 20 \
   --monitor_every 280 --ckpt_every 100000 > $R/smoke_v1.stdout 2>&1
echo "smoke_v1 rc=$?" >> $R/width_choice.txt
