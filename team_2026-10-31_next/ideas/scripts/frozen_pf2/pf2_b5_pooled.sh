#!/bin/bash
# calib: arm-level pooled operating point (coach, 31 Oct): after pf2_b5_hook.sh has written records (with self-checks) for ALL
# seeds of one arm, choose ONE b per arm on the pooled val counts and report each seed's test / test_clean / ext value at it.
# CPU only (nice 19). THIN-B3 co-primaries use this variant; PF2 reports it beside the per-run OP.
# Usage: pf2_b5_pooled.sh OUT CALIBSCRIPTS RUN_NAME [RUN_NAME ...]   (OUT = the hook's OUT; RUN_NAMEs = the arm's run names)
set -u
OUT=$1; CS=$2; shift 2
PY=${PY:-/home/noob/work/el-fault-detection/.venv/bin/python}
LOG="$OUT/b5_pooled.log"; FAILS=0; mkdir -p "$OUT/sum"
md5sum "$CS/el_metrics.py" "$0" >> "$LOG"
PV=(); for N in "$@"; do PV+=("$OUT/rec/$N.val.json"); done
for N in "$@"; do
  for S in test ext; do
    nice -n 19 $PY "$CS/el_metrics.py" summary --val "$OUT/rec/$N.val.json" --pooled-val "${PV[@]}" --target "$OUT/rec/$N.$S.json" \
      --deployed-b 0 --out "$OUT/sum/$N.$S.pooled.json" >> "$LOG" 2>&1
    rc=$?; echo "[$(date)] b5 pooled summary $N $S rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && FAILS=$((FAILS+1))
  done
  nice -n 19 $PY "$CS/el_metrics.py" summary --val "$OUT/rec/$N.val.json" --pooled-val "${PV[@]}" --target "$OUT/rec/$N.test.json" \
    --deployed-b 0 --exclude CSIR_00070_r8_c4 --out "$OUT/sum/$N.test_clean.pooled.json" >> "$LOG" 2>&1
  rc=$?; echo "[$(date)] b5 pooled summary $N test_clean rc=$rc" >> "$LOG"; [ $rc -ne 0 ] && FAILS=$((FAILS+1))
done
echo "[$(date)] b5 pooled done ($*): fails=$FAILS" >> "$LOG"
[ $FAILS -eq 0 ]
