#!/bin/bash
# calib: PF2 §13 synthetic-val (domain's frozen V4) dump + records for ONE finished run. Not test, not E1, so it may run in runner's
# side queue before the opening, behind the shared GPU gate. Records have no m0 JSON, so their self-check file says UNCHECKED
# (expected; `el_metrics routing` accepts UNCHECKED for synval only).
# Usage: [DEVICE=cuda|cpu] pf2_synval.sh CODE SYNVAL_DIR OUT CALIBSCRIPTS RUN_DIR
#   SYNVAL_DIR = domain's frozen V4 dir (images/, masks/; stems <val stem>__V4h{0,1}); OUT = the B5 hook's OUT (writes OUT/dump, OUT/rec)
set -u
CODE=$1; SV=$2; OUT=$3; CS=$4; RUN=$5
PY=${PY:-/home/noob/work/el-fault-detection/.venv/bin/python}
DEVICE=${DEVICE:-cuda}
N=$(basename "$RUN"); LOG="$OUT/b5_synval.log"; mkdir -p "$OUT/dump" "$OUT/rec"
md5sum "$CS/calib_dump.py" "$CS/el_metrics.py" "$0" >> "$LOG"; echo "DEVICE=$DEVICE SYNVAL=$SV" >> "$LOG"
CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0} OMP_NUM_THREADS=8 nice -n 19 $PY "$CS/calib_dump.py" --code "$CODE" --out "$OUT/dump" \
  --sets synval --synval "$SV" --device "$DEVICE" --batch 8 --threads 8 --group "$N" "$RUN" >> "$LOG" 2>&1
rc=$?; echo "[$(date)] synval dump $N rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && exit $rc
OMP_NUM_THREADS=1 nice -n 19 $PY "$CS/el_metrics.py" records --dump "$OUT/dump/$N.synval.npz" --set synval --synval "$SV" \
  --out "$OUT/rec/$N.synval.json" --procs 8 >> "$LOG" 2>&1
rc=$?; echo "[$(date)] synval records $N rc=$rc" >> "$LOG"
exit $rc
