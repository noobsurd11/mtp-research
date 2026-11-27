#!/usr/bin/env bash
# G-N7 CPU extra (after run_cpu.sh): unit re-check at 16 threads under the later host load, then direct batch-8 runs of
# C1-D4 and E-PF at 16 threads (latency + peak RSS). Same rules.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/home/noob/work/el-fault-detection/.venv/bin/python
OUT="$HERE/raw/cpu"; mkdir -p "$OUT"; LOG="$OUT/driver.log"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= HF_HUB_OFFLINE=1
p5104() { echo "$(date '+%F %T') ps5104: $(ps -p 5104 -o pid=,etime=,cmd= 2>&1 || echo 'NOT RUNNING') | load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$LOG"; }
run() {
  local name="$1" th="$2"; shift 2
  p5104; echo "$(date '+%F %T') start $name threads $th: $*" >> "$LOG"
  OMP_NUM_THREADS=$th MKL_NUM_THREADS=$th nice -n 10 "$PY" "$HERE/infer_cost.py" time --threads "$th" "$@" \
     --out "$OUT/$name.json" >> "$LOG" 2>&1
  echo "$(date '+%F %T') end $name rc=$?" >> "$LOG"; p5104
}
echo "$(date '+%F %T') extra driver start pid $$" >> "$LOG"
# unit forwards again, under the host load of the whole-arm runs (another team job started 11:51:51), for the additivity check
run UPF_b1_t16_recheck 16 --arm UPF --batch 1 --warmup 3 --cells 60
run UHR_b1_t16_recheck 16 --arm UHR --batch 1 --warmup 3 --cells 60
run C1D4_b8_t16 16 --arm C1D4 --batch 8 --warmup 1 --cells 24
run EPF_b8_t16 16 --arm EPF --batch 8 --warmup 1 --cells 24
echo "$(date '+%F %T') extra driver ALL DONE" >> "$LOG"
