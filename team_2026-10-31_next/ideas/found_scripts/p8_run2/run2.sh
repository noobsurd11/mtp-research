#!/bin/bash
# found: P8 probe run 2 (protocol_A8screen §2): the three DINOv3 rows (route B files, 1 Nov). CPU only. Final pick = run1 refs + run2 rows (p8_merge.py).
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 HF_HUB_OFFLINE=1
cd /home/noob/work/found/p8
echo "[$(date "+%F %T")] start (pid $$) $(md5sum p8_probe.py)" >> run2.log
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -I p8_probe.py --out run2 --encoders dinov3_cnx_t dinov3_vits16_512 dinov3_vits16_1024 >> run2.log 2>&1; rc=$?
echo "[$(date "+%F %T")] P8 run2 rc=$rc" >> run2.log
