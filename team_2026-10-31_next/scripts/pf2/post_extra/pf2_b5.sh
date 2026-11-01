#!/bin/bash
# post_extra hook (pf2_post.sh runs it with OUT, RUNS, GS set; non-fatal): calib's B5 operating points + cell-level metrics
# (protocol_PF2 4.1-4.2), via calib's frozen pf2_b5_hook.sh with the frozen calib_dump.py / el_metrics.py copied into
# reports/pf2/post_extra/calib/ (md5s in FROZEN.md5). One run per hook call, each dump behind the shared gate at GS (one GPU
# process at a time; another job of ours may start between dumps). Records / summaries on CPU at nice 19 (calib's hook).
# Work dir reports/pf2/b5_work/ is OUTSIDE post/ (coach A3: the ~4 GB of npz dumps stay on gaint, never in the MANIFEST or
# the laptop pull); afterwards only rec/*.json, rec/*.selfcheck.txt, sum/*.json and b5_hook.log are copied into $OUT/b5/.
set -u
cd /home/noob/work/el_f3
. reports/pf2/scripts/gpu_gate.sh
X=reports/pf2/post_extra; W=/home/noob/work/el_f3/reports/pf2/b5_work; F=0
# calib hook device, ONE setting for ALL runs of ALL arms (coach, protocol_PF2 4.1), read once from post_extra/B5_DEVICE, which
# the lone-RN50-phase smoke writes mechanically (cuda iff its bf16 self-check passed at tol profile exact, else cpu). No hand choice.
DEVICE=$(cat $X/B5_DEVICE 2>/dev/null); case "$DEVICE" in cuda|cpu) export DEVICE;; *) echo "B5_DEVICE missing or invalid ('$DEVICE'): B5 not run"; exit 2;; esac
echo "[$(date)] B5 DEVICE=$DEVICE (from $X/B5_DEVICE) for all runs: $(echo $RUNS | wc -w)"
mkdir -p $W
for r in $RUNS; do
  gate_wait $GS "pf2 post b5 $r"
  bash $X/calib/pf2_b5_hook.sh protocol_PF2 /home/noob/work/el_f3 $OUT/m0 $W /home/noob/work/el_f3/$X/calib \
    /home/noob/work/el_f3/experiments/$r || F=$((F+1))
  echo "[$(date)] b5 $r done (fails so far $F)"; done
# arm-level pooled-val operating point (calib's frozen pf2_b5_pooled.sh; CPU, nice 19): one call per arm with its run names,
# after all of that arm's runs went through the hook (records + self-checks). Arms present in RUNS only (RN50PF absent on RN_STOP).
for arm in SUP SUPPF RN50PF; do
  AR=$(for r in $RUNS; do case $r in pf2_${arm}_100pct_s*) echo $r;; esac; done)
  [ -n "$AR" ] || continue
  bash $X/calib/pf2_b5_pooled.sh $W /home/noob/work/el_f3/$X/calib $AR || F=$((F+1))
  echo "[$(date)] b5 pooled $arm ($(echo $AR | wc -w) runs) done (fails so far $F)"; done
mkdir -p $OUT/b5/rec $OUT/b5/sum
cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $OUT/b5/rec/ 2>/dev/null
cp -p $W/sum/*.json $OUT/b5/sum/ 2>/dev/null
cp -p $W/b5_hook.log $W/b5_pooled.log $OUT/b5/ 2>/dev/null
(cd $W/dump && md5sum *.npz) > $OUT/b5/dump_md5_on_gaint.txt 2>/dev/null
[ $F = 0 ]
