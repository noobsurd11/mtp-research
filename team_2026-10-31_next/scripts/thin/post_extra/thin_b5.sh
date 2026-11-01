#!/bin/bash
# THIN-B3 post_extra hook (thin_post.sh runs it with OUT, RUNS, GS set; non-fatal): calib's B5 operating points + cell-level
# metrics (protocol_thin_b3 §4: SKR / CLD B5 co-primaries at the arm-level pooled OP; B3 reported), via calib's frozen hook files
# copied into reports/thin/post_extra/calib/ (md5s in FROZEN.md5). One run per hook call, each dump behind the shared gate at GS.
# Device: the mechanical PF2 smoke decision (el_f3/reports/pf2/post_extra/B5_DEVICE), one setting for all runs; exits 2
# (non-fatal, B5 not run, disclosed) if missing. Work dir reports/thin/b5_work is OUTSIDE post/ (dumps stay on gaint).
# Then pf2_b5_pooled.sh once per arm (SKR, CLD, B3) on its 5 runs; only rec / selfcheck / sum JSONs and logs are copied into post/b5.
set -u
cd /home/noob/work/el_thin
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
X=reports/thin/post_extra; W=/home/noob/work/el_thin/reports/thin/b5_work; F=0
DEVICE=$(cat /home/noob/work/el_f3/reports/pf2/post_extra/B5_DEVICE 2>/dev/null); case "$DEVICE" in cuda|cpu) export DEVICE;; *) echo "B5_DEVICE missing or invalid ('$DEVICE'): B5 not run"; exit 2;; esac
echo "[$(date)] B5 DEVICE=$DEVICE (PF2's mechanical decision) for all runs: $(echo $RUNS | wc -w)"
mkdir -p $W
for r in $RUNS; do
  gate_wait $GS "thin post b5 $r"
  bash $X/calib/pf2_b5_hook.sh protocol_thin_b3 /home/noob/work/el_thin $OUT/m0 $W /home/noob/work/el_thin/$X/calib \
    /home/noob/work/el_thin/experiments/$r || F=$((F+1))
  echo "[$(date)] b5 $r done (fails so far $F)"; done
for arm in SKR CLD B3; do
  AR=$(for r in $RUNS; do case $r in thin_${arm}_100pct_s*) echo $r;; esac; done)
  [ -n "$AR" ] || continue
  bash $X/calib/pf2_b5_pooled.sh $W /home/noob/work/el_thin/$X/calib $AR || F=$((F+1))
  echo "[$(date)] b5 pooled $arm ($(echo $AR | wc -w) runs) done (fails so far $F)"; done
mkdir -p $OUT/b5/rec $OUT/b5/sum
cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $OUT/b5/rec/ 2>/dev/null
cp -p $W/sum/*.json $OUT/b5/sum/ 2>/dev/null
cp -p $W/b5_hook.log $W/b5_pooled.log $OUT/b5/ 2>/dev/null
(cd $W/dump && md5sum *.npz) > $OUT/b5/dump_md5_on_gaint.txt 2>/dev/null
[ $F = 0 ]
