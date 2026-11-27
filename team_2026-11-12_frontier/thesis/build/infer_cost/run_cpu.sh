#!/usr/bin/env bash
# G-N7 CPU timing driver (gaint, CPU only; never touches a GPU: CUDA_VISIBLE_DEVICES is empty).
# One process per config (clean peak-RSS), nice -n 10, torch threads capped via torch.set_num_threads + OMP / MKL env.
# Logs `ps -p 5104` (root's finllm_chat.py) and the load average before and after every config to raw/cpu/driver.log.
# Usage: bash run_cpu.sh   (from any directory; writes only under this directory's raw/cpu/)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/home/noob/work/el-fault-detection/.venv/bin/python
OUT="$HERE/raw/cpu"; mkdir -p "$OUT"; LOG="$OUT/driver.log"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1
p5104() { echo "$(date '+%F %T') ps5104: $(ps -p 5104 -o pid=,etime=,cmd= 2>&1 || echo 'NOT RUNNING') | load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"; }
run() {  # name threads args...
  local name="$1" th="$2"; shift 2
  p5104; echo "$(date '+%F %T') start $name threads $th: $*" >> "$LOG"
  OMP_NUM_THREADS=$th MKL_NUM_THREADS=$th nice -n 10 "$PY" "$HERE/infer_cost.py" time --threads "$th" "$@" \
     --out "$OUT/$name.json" >> "$LOG" 2>&1
  echo "$(date '+%F %T') end $name rc=$?" >> "$LOG"; p5104
}
echo "$(date '+%F %T') driver start pid $$" >> "$LOG"
# A: unit forwards (C1 = UPF), batch 1
for th in 16 8; do
  run UPF_b1_t$th $th --arm UPF --batch 1 --warmup 3 --cells 200
  run UHR_b1_t$th $th --arm UHR --batch 1 --warmup 3 --cells 200
done
run UPF_b1_t1 1 --arm UPF --batch 1 --warmup 2 --cells 50
run UHR_b1_t1 1 --arm UHR --batch 1 --warmup 2 --cells 50
# B: unit forwards, batch 8 (the dump batch)
for th in 16 8; do
  run UPF_b8_t$th $th --arm UPF --batch 8 --warmup 2 --cells 200
  run UHR_b8_t$th $th --arm UHR --batch 8 --warmup 2 --cells 200
done
run UPF_b8_t1 1 --arm UPF --batch 8 --warmup 1 --cells 24
run UHR_b8_t1 1 --arm UHR --batch 8 --warmup 1 --cells 24
# C: whole arms, direct, 16 threads
run EPF_b1_t16 16 --arm EPF --batch 1 --warmup 2 --cells 40
run C1D4_b1_t16 16 --arm C1D4 --batch 1 --warmup 2 --cells 30
run C2_b1_t16 16 --arm C2 --batch 1 --warmup 2 --cells 30
run C2vb_b1_t16 16 --arm C2 --views-batched --batch 1 --warmup 2 --cells 30
run C3_b1_t16 16 --arm C3 --batch 1 --warmup 1 --cells 10
run C2_b8_t16 16 --arm C2 --batch 8 --warmup 1 --cells 24
echo "$(date '+%F %T') driver ALL DONE" >> "$LOG"
