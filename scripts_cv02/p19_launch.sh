#!/bin/bash
# P19 (Hanifi 2025 reproduction): 8 runs, one per cv02 GPU. Run inside tmux session p19 from /tmp/noob_el/hanifi.
cd /tmp/noob_el/hanifi && source env_p19.sh
L=runs/launch.log; mkdir -p runs
RUNS=("vgg_unet 0" "mobilenet_unet 0" "resnet50_unet 0" "vgg_segnet 0" "mobilenet_segnet 0" "resnet50_segnet 0" "vgg_unet 1" "vgg_unet 2")
for g in "${!RUNS[@]}"; do
  set -- ${RUNS[$g]}; n=${1}_s$2
  echo "[$(date -u)] start $n gpu $g" >> $L
  ( CUDA_VISIBLE_DEVICES=$g venv/bin/python hanifi_run.py --arch $1 --seed $2 --repo /tmp/noob_el/hanifi/pv-defect-segmentation \
      --data /tmp/noob_el/hanifi/data --out runs/$n > runs/$n.log 2>&1; echo "[$(date -u)] done $n rc=$?" >> $L ) &
  sleep 3
done
wait
echo "[$(date -u)] all done" >> $L
