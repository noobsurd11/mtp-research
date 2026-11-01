#!/bin/bash
# calib: B5 operating-point + cell-level metrics hook for a pre-registered protocol opening (protocol_PF2 §4.1-4.2, coach A1-A5).
# Runner runs it INSIDE the opening, behind the shared GPU gate (one GPU process at a time; ~1-2 GB per model, bf16, batch 8).
# Usage: [DEVICE=cuda|cpu] pf2_b5_hook.sh PROTOCOL CODE M0DIR OUT CALIBSCRIPTS RUN_DIR [RUN_DIR ...]
#   PROTOCOL      e.g. protocol_PF2 (passed to calib_dump --opening; test cells are refused without it)
#   CODE          the protocol's worktree (data/, src/), e.g. /home/noob/work/el_pf2
#   M0DIR         the opening's m0 per-cell JSONs (<run>.json, default argmax, with cells val / test / ext)
#   OUT           output dir on gaint (dumps stay on gaint, coach A3)
#   CALIBSCRIPTS  dir holding the frozen calib_dump.py and el_metrics.py
# Per run: dump (val, test, ext) -> records with the b = 0 self-check vs m0 (written only on PASS; coach A4) -> summaries (test, ext).
# Status lines capture rc before any date. Exit non-zero if any step failed.
set -u
PROTO=$1; CODE=$2; M0=$3; OUT=$4; CS=$5; shift 5
PY=${PY:-/home/noob/work/el-fault-detection/.venv/bin/python}
# coach ruling (protocol_PF2 §4.1): DEVICE=cuda (default; self-check tol profile exact) or DEVICE=cpu for ALL runs of ALL arms
# (tol profile cpu). Never mix devices within one opening.
DEVICE=${DEVICE:-cuda}; case "$DEVICE" in cuda) TP=exact;; cpu) TP=cpu;; *) echo "DEVICE must be cuda or cpu" >&2; exit 2;; esac
mkdir -p "$OUT/dump" "$OUT/rec" "$OUT/sum"
LOG="$OUT/b5_hook.log"; FAILS=0
md5sum "$CS/calib_dump.py" "$CS/el_metrics.py" "$0" >> "$LOG"; echo "DEVICE=$DEVICE tol-profile=$TP" >> "$LOG"
for RUN in "$@"; do
  N=$(basename "$RUN")
  CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0} OMP_NUM_THREADS=8 nice -n 19 $PY "$CS/calib_dump.py" --code "$CODE" --out "$OUT/dump" \
    --sets val test ext --opening "$PROTO" --device "$DEVICE" --batch 8 --threads 8 --group "$N" "$RUN" >> "$LOG" 2>&1
  rc=$?; echo "[$(date)] b5 dump $N rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && { FAILS=$((FAILS+1)); continue; }
  ok=1
  for S in val test ext; do
    OMP_NUM_THREADS=1 nice -n 19 $PY "$CS/el_metrics.py" records --dump "$OUT/dump/$N.$S.npz" --set $S --code "$CODE" \
      --out "$OUT/rec/$N.$S.json" --m0 "$M0/$N.json" --m0-set $S --tol-profile $TP --procs 8 >> "$LOG" 2>&1
    rc=$?; echo "[$(date)] b5 records+selfcheck $N $S rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && { FAILS=$((FAILS+1)); ok=0; }
  done
  [ $ok -eq 1 ] || continue
  for S in test ext; do
    nice -n 19 $PY "$CS/el_metrics.py" summary --val "$OUT/rec/$N.val.json" --target "$OUT/rec/$N.$S.json" --deployed-b 0 \
      --out "$OUT/sum/$N.$S.json" >> "$LOG" 2>&1
    rc=$?; echo "[$(date)] b5 summary $N $S rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && FAILS=$((FAILS+1))
  done
  nice -n 19 $PY "$CS/el_metrics.py" summary --val "$OUT/rec/$N.val.json" --target "$OUT/rec/$N.test.json" --deployed-b 0 \
    --exclude CSIR_00070_r8_c4 --out "$OUT/sum/$N.test_clean.json" >> "$LOG" 2>&1
  rc=$?; echo "[$(date)] b5 summary $N test_clean rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && FAILS=$((FAILS+1))
done
echo "[$(date)] b5 hook done: fails=$FAILS" >> "$LOG"
[ $FAILS -eq 0 ]
