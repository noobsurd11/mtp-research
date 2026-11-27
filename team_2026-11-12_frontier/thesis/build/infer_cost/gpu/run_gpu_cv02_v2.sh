#!/usr/bin/env bash
# v2 of run_gpu_cv02.sh cd3282ad (lead 22 Nov 17:50): only change = sleep 15 s before each idle check in run(); v1 stopped at 12:20:07 UTC
# before C3_b1 on a false non-idle (7 MiB, util 21 %, no process: the utilisation of our own C2_b1 just ended).
#
# What it does: for each arm (C1, C1-D4, C2, C3, E-PF) at batch 1 and batch 8, plus C2 with the 8 D4 views batched, one
# python process (thesis/build/infer_cost/infer_cost.py `time`, --device cuda) times >= 200 cells after warm-up with CUDA
# events, canonical dump settings (fp32, TF32 off, cudnn deterministic, benchmark off: scripts/bench_infer.py l148-152),
# 4 CPU threads (as the dump jobs). Weights: the fin2 checkpoints on cv02 (strict load), or --no-weights if they are gone.
# Writes ONLY under $OUT. Never kills anything. Refuses to start, and stops between configs, if the GPU is not idle.
#
# Before running (the lead, on cv02):
#   1. No queue of ours may be armed on this GPU (the t3b queue must be ALL DONE, or GPU outside its GPUS list), because a
#      queue lane counts only its own jobs and could start a training on the GPU while this runs.
#   2. Copy two files to cv02 (from gaint):  mkdir -p /tmp/noob_el/infer_cost  and copy
#        thesis/build/infer_cost/infer_cost.py  and  thesis/build/infer_cost/gpu/run_gpu_cv02.sh  into it.
#   3. Pick an idle GPU g (nvidia-smi: no process, < 1 GiB used, util 0 %).
#
# Exact command (on cv02):
#   cd /tmp/noob_el/infer_cost && nohup bash run_gpu_cv02.sh <g> > run_gpu.nohup 2>&1 &
#   (optional 2nd/3rd args: CODE dir with src/ and bench/tta.py, default /tmp/noob_el/bench_9967d59;
#    CKROOT with experiments/fin_*_pool_s*/checkpoints/{slim,latest}.pth, default the same dir; 'none' = random init)
# Expected runtime: about 15 to 25 min (S: estimate; per view about 10 to 15 ms PF, 25 to 35 ms HRNet in fp32 without TF32,
#   bounded above by the fold dumps of queue fin: 40 to 51 s per 101 to 111 cells x 8 views including start-up; C3 at
#   batch 1 is the longest config, 200 cells x 40 forwards, about 3 to 5 min). Each config is capped at 600 s (--max-seconds).
# Afterwards: copy $OUT back to gaint thesis/build/infer_cost/raw/gpu/ and run
#   python thesis/build/infer_cost/summarise.py   (it picks up raw/gpu/*.json).
set -u
G="${1:?usage: run_gpu_cv02.sh <gpu index> [CODE dir] [CKROOT|none]}"
CODE="${2:-/tmp/noob_el/bench_9967d59}"
CKROOT="${3:-$CODE}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/tmp/noob_el/el-fault-detection/.venv/bin/python
OUT="$HERE/out_gpu$G"; mkdir -p "$OUT"; LOG="$OUT/driver.log"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES="$G" HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
export CUBLAS_WORKSPACE_CONFIG=:4096:8
W=(); [ "$CKROOT" = none ] && W=(--no-weights)
[ -f "$HERE/infer_cost.py" ] || { echo "infer_cost.py missing in $HERE"; exit 2; }
[ -f "$CODE/src/models/model_factory.py" ] && [ -f "$CODE/bench/tta.py" ] || { echo "CODE $CODE lacks src/ or bench/tta.py"; exit 2; }

idle() {  # GPU G: no compute process, < 1024 MiB used, utilisation <= 5 % in each of 5 samples 1 s apart
  local apps used util i
  apps=$(nvidia-smi -i "$G" --query-compute-apps=pid --format=csv,noheader | grep -c .)
  [ "$apps" -eq 0 ] || { echo "GPU $G: $apps compute process(es)"; return 1; }
  for i in 1 2 3 4 5; do
    read -r used util < <(nvidia-smi -i "$G" --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ',')
    [ "$used" -lt 1024 ] && [ "$util" -le 5 ] || { echo "GPU $G: used ${used} MiB, util ${util} %"; return 1; }
    sleep 1
  done
  return 0
}
snap() { echo "$(date '+%F %T') $1: $(nvidia-smi -i "$G" --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu,clocks.sm,power.draw --format=csv,noheader) | apps: $(nvidia-smi -i "$G" --query-compute-apps=pid,used_memory --format=csv,noheader | tr '\n' ' ') | load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"; }
run() {  # name args...  (v2, lead 22 Nov: sleep 15 s first, so our own just-ended config does not read as non-idle)
  local name="$1"; shift; sleep 15
  if ! msg=$(idle); then echo "$(date '+%F %T') STOP before $name: not idle ($msg)" >> "$LOG"; snap "stop"; exit 3; fi
  snap "before $name"
  "$PY" "$HERE/infer_cost.py" time --device cuda --threads 4 --code "$CODE" --ckroot "$CKROOT" ${W[@]+"${W[@]}"} \
      --max-seconds 600 "$@" --out "$OUT/$name.json" >> "$LOG" 2>&1
  echo "$(date '+%F %T') end $name rc=$?" >> "$LOG"; snap "after $name"
}
echo "$(date '+%F %T') start: GPU $G CODE $CODE CKROOT $CKROOT host $(hostname) pid $$" >> "$LOG"
nvidia-smi -i "$G" >> "$LOG" 2>&1
"$PY" -c "import torch, segmentation_models_pytorch as smp, timm; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'smp', smp.__version__, 'timm', timm.__version__)" >> "$LOG" 2>&1
for B in 1 8; do
  run C1_b$B   --arm C1   --batch $B --warmup 10 --cells 200
  run EPF_b$B  --arm EPF  --batch $B --warmup 5  --cells 200
  run C1D4_b$B --arm C1D4 --batch $B --warmup 5  --cells 200
  run C2_b$B   --arm C2   --batch $B --warmup 5  --cells 200
  run C3_b$B   --arm C3   --batch $B --warmup 3  --cells 200
done
run C2vb_b1 --arm C2 --views-batched --batch 1 --warmup 5 --cells 200
run UHR_b1  --arm UHR --batch 1 --warmup 10 --cells 200
echo "$(date '+%F %T') ALL DONE" >> "$LOG"
