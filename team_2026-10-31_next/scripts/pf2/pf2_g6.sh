#!/bin/bash
# PF2 gate 6 (protocol_PF2.md section 9.6, G5 rule, val-blind): RN50-PF s5's own checkpoint at step 4,000, copied during the run;
# layer3 / layer4 mean conv-weight cosine to ImageNet RN50 >= 0.8 -> "G6 PASS". Else "G6 FAIL": RN_STOP (the queue skips the
# remaining RN50 jobs) and every running RN50-PF python process is stopped by its recorded PID (reports/pf2/pids/; command line
# printed and checked for run_name=pf2_RN50PF first), as pre-registered. CPU only for the cosine.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python; L=reports/pf2/launch.log; O=reports/pf2/g6; mkdir -p $O
R=pf2_RN50PF_100pct_s5; D=experiments/$R; R0=reports/pf2/cpucheck/rn50_imagenet_step0.pth
until [ -e experiments/$R.stdout ] && grep -q "step 4050/20000" experiments/$R.stdout; do
  grep -qE "trained $R rc=" $L && { echo "[$(date)] G6 NOT READ: $R ended before step 4,050 ($(grep -E "trained $R rc=" $L | tail -1))" >> $L; exit 1; }
  sleep 20; done
cp -p $D/checkpoints/latest.pth $D/checkpoints/latest_4k.pth
st=$($P -c "import torch,sys; print(torch.load(sys.argv[1], map_location='cpu', weights_only=False)['step'])" $D/checkpoints/latest_4k.pth 2>/dev/null)
md5sum $D/checkpoints/latest_4k.pth > $O/latest_4k.md5
[ "$st" = 4000 ] || { echo "[$(date)] G6 NOT READ: copied checkpoint is step '$st', not 4000" >> $L; exit 1; }
OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" nice -n 10 $P reports/enc_cosine.py --out $O/enc_cosine_4k.json \
  --pair "RN50-PF s5 4k vs ImageNet RN50" $R0 $D/checkpoints/latest_4k.pth > $O/enc_cosine_4k.txt 2>&1
v=$($P -c "import json,sys; r=json.load(open(sys.argv[1]))['RN50-PF s5 4k vs ImageNet RN50']; print(r['layer3']['cos'], r['layer4']['cos'])" $O/enc_cosine_4k.json)
read -r c3 c4 <<< "$v"
if $P -c "import sys; sys.exit(0 if float(sys.argv[1]) >= 0.8 and float(sys.argv[2]) >= 0.8 else 1)" "$c3" "$c4"; then
  echo "[$(date)] G6 PASS: $R step 4000 layer3 $c3 layer4 $c4 (>= 0.8; md5 $(cut -c1-8 $O/latest_4k.md5))" >> $L
else
  touch reports/pf2/RN_STOP
  echo "[$(date)] G6 FAIL: $R step 4000 layer3 $c3 layer4 $c4 (< 0.8): RN_STOP set; stopping running RN50-PF runs by recorded PID" >> $L
  for f in reports/pf2/pids/pf2_RN50PF_*.pid; do p=$(cat $f); a=$(ps -o args= -p $p 2>/dev/null)
    if echo "$a" | grep -q "run_name=pf2_RN50PF_100pct_s[5-9]"; then echo "[$(date)] G6 stop PID $p: $a" | cut -c1-400 >> $L; kill $p; fi; done
fi
