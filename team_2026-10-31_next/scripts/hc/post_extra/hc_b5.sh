#!/bin/bash
# HC post_extra hook (hc_post.sh runs it with OUT, RUNS, GS set; reported only, non-fatal): calib's B5 operating points + cell-level
# metrics (protocol_HC §6 = protocol_PF2 §4.1-4.2: per-run OP and the arm-pooled OP), via calib's FROZEN hook files copied into
# /home/noob/work/nq/hc/post_extra/calib/ (calib_dump c172717e, el_metrics 6e73ff11, pf2_b5_hook e06dfc5f, pf2_b5_pooled 873591ff:
# the PF2 / THIN files). Adapted from thin_b5.sh (2dfaf915): paths, protocol name and arm only. One run per hook call, each dump behind
# the shared gate at GS. Device: PF2's mechanical decision (el_f3/reports/pf2/post_extra/B5_DEVICE = cuda, 4e7ff566), one setting for all
# runs; exits 2 (non-fatal, B5 not run, disclosed) if missing. Work dir el_hc/reports/hc/b5_work is OUTSIDE post/ (dumps stay on gaint).
# Then pf2_b5_pooled.sh once for the HC arm. The SUPPF comparator's per-run and pooled OPs: PF2's opening (post/b5/sum), reused.
set -u
cd /home/noob/work/el_hc
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
X=/home/noob/work/nq/hc/post_extra; W=/home/noob/work/el_hc/reports/hc/b5_work; F=0
DEVICE=$(cat /home/noob/work/el_f3/reports/pf2/post_extra/B5_DEVICE 2>/dev/null); case "$DEVICE" in cuda|cpu) export DEVICE;; *) echo "B5_DEVICE missing or invalid ('$DEVICE'): B5 not run"; exit 2;; esac
echo "[$(date)] B5 DEVICE=$DEVICE (PF2's mechanical decision) for all runs: $(echo $RUNS | wc -w)"
mkdir -p $W
for r in $RUNS; do
  gate_wait $GS "hc post b5 $r"
  bash $X/calib/pf2_b5_hook.sh protocol_HC /home/noob/work/el_hc $OUT/m0 $W $X/calib /home/noob/work/el_hc/experiments/$r || F=$((F+1))
  echo "[$(date)] b5 $r done (fails so far $F)"; done
AR=$(for r in $RUNS; do case $r in hc_HC_100pct_s*) echo $r;; esac; done)
if [ -n "$AR" ]; then
  bash $X/calib/pf2_b5_pooled.sh $W $X/calib $AR || F=$((F+1))
  echo "[$(date)] b5 pooled HC ($(echo $AR | wc -w) runs) done (fails so far $F)"; fi
mkdir -p $OUT/b5/rec $OUT/b5/sum
cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $OUT/b5/rec/ 2>/dev/null
cp -p $W/sum/*.json $OUT/b5/sum/ 2>/dev/null
cp -p $W/b5_hook.log $W/b5_pooled.log $OUT/b5/ 2>/dev/null
(cd $W/dump && md5sum *.npz) > $OUT/b5/dump_md5_on_gaint.txt 2>/dev/null
[ $F = 0 ]
