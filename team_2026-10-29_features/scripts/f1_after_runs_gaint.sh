#!/bin/bash
# After all 10 MIM5-experiment runs are rescored: MIM5 scoring (f1_post_gaint.sh), then the val-only AM check
# (protocol_am v0.1). Gates: >= 6 GB free before each (own peak about 3-4 GB + 2 GB). Logs in reports/f1/.
set -u
cd /home/noob/work/el_f1
L=/home/noob/work/el_f1/reports/f1g/launch.log  # v2: absolute (v1 relative path broke after cd el_f2 / cd post, 30 Oct)
P=/home/noob/work/el-fault-detection/.venv/bin/python
until [ "$(grep -cE 'rescored f1_(A|MIM)_5pct_s[0-4] rc=0' $L)" -ge 10 ]; do sleep 120; done
wfree(){ while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "$1" ]; do sleep 30; done; }
echo "[$(date)] all 10 rescored; MIM5 post start" >> $L
wfree 6000; bash reports/f1/f1_post_gaint.sh > reports/f1/post.log 2>&1; echo "[$(date)] MIM5 post rc=$?" >> $L
wfree 6000
cd /home/noob/work/el_f2
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8 $P scripts/am_map.py --mim_ckpt /home/noob/work/el_f1/experiments/f1_mim_pre_s0/ckpt_latest.pth \
  --mim_args /home/noob/work/el_f1/experiments/f1_mim_pre_s0/args.json \
  --a5 $(for k in 0 1 2 3 4; do echo /home/noob/work/el_f1/experiments/f1_A_5pct_s$k; done) \
  --sup /home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s{0,1,2} /home/noob/work/cv02_noob_el/el_p13/experiments/p16_A_100pct_s{3,4} \
  --out /home/noob/work/el_f1/reports/f1/post/am_val.json > /home/noob/work/el_f1/reports/f1/am.log 2>&1
echo "[$(date)] AM rc=$?" >> $L
cd /home/noob/work/el_f1/reports/f1/post && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5
echo "[$(date)] AFTER-RUNS DONE" >> $L
