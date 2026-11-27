#!/bin/bash
# fig_maker_A: rebuild F2, F5, F6, F10 to F17, F19 (CPU only, no GPU, nice 10, no bytecode files).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=/home/noob/work/el-fault-detection/.venv/bin/python
for n in 13 14 15 16 17 10 11 12 19 2 5 6; do
  CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 10 "$PY" "src/make_F${n}.py"
done
