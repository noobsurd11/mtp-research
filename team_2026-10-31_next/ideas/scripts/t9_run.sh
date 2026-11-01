#!/bin/bash
# T9 run (found, 31 Oct 2026): ideas/t9_prereg.md. gaint CPU only, nice 19, 8 threads. No E1, no test, no val adaptation.
# Steps: self-check (v0 on E-SCDD images == calib FINAL.rf.npz) -> smoke (1 module, unscored) -> dumps -> records -> rule.
set -u
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
PY=/home/noob/work/el-fault-detection/.venv/bin/python
T=/home/noob/work/found/t9; D=$T/dump; RC=$T/rec; CODE=/home/noob/work/el_f3; CAL=/home/noob/work/calib/out/dump
LOG=$T/t9.log
FINAL="/home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s0 /home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s1 /home/noob/work/cv02_noob_el/el_p6/experiments/p6_L3_100pct_s2 /home/noob/work/cv02_noob_el/el_p13/experiments/p16_A_100pct_s3 /home/noob/work/cv02_noob_el/el_p13/experiments/p16_A_100pct_s4"
SUPPF5="$CODE/experiments/f3_SUPPF_100pct_s0 $CODE/experiments/f3_SUPPF_100pct_s1 $CODE/experiments/f3_SUPPF_100pct_s2 $CODE/experiments/f3_SUPPF_100pct_s3 $CODE/experiments/f3_SUPPF_100pct_s4"
cd $T
N="nice -n 19"
st() { echo "[$(date '+%F %T')] $*" >> $LOG; }
md5sum t9_dump.py t9_score.py el_metrics.py >> $LOG
st "start (pid $$)"

# 1. self-check: v0 on the E-SCDD _rf images must reproduce calib's FINAL.rf.npz margins (max |d| <= 1e-2)
$N $PY -I t9_dump.py --code $CODE --out $T/selfcheck --mode v0 --img rf --group FINAL $FINAL --threads 8 >> $LOG 2>&1; rc=$?
st "selfcheck dump rc=$rc"
[ $rc -eq 0 ] || exit 1
$N $PY -I - >> $LOG 2>&1 <<EOF
import numpy as np, sys
a = np.load("$T/selfcheck/FINAL__V0rf.rf.npz"); b = np.load("$CAL/FINAL.rf.npz")
assert list(a["stems"]) == list(b["stems"]), "stem order differs"
d = float(np.abs(a["margin"].astype(np.float32) - b["margin"].astype(np.float32)).max())
o = float((a["oth"] != b["oth"]).mean())
print(f"SELFCHECK max|dmargin| {d:.5f} oth mismatch share {o:.2e}")
sys.exit(0 if d <= 1e-2 else 2)
EOF
rc=$?; st "selfcheck compare rc=$rc"
[ $rc -eq 0 ] || { st "SELFCHECK FAILED: stop before any T9 number"; exit 2; }

# 2. smoke: panel mode, 1 module, 1 member (files only, not scored)
$N $PY -I t9_dump.py --code $CODE --out $T/smoke --mode panel --limit-modules 1 --group SMOKE ${SUPPF5%% *} --threads 8 >> $LOG 2>&1; rc=$?
st "smoke rc=$rc"
[ $rc -eq 0 ] || exit 3
rm -rf $T/smoke

# 3. dumps (pool copies): V0, V1 (H36), V2+V3; plus the E-SCDD V0 sensitivity for SUPPF5 (FINAL's is the self-check dump)
cp $T/selfcheck/FINAL__V0rf.rf.npz $D/
for fam in FINAL SUPPF5; do
  RUNS=$([ $fam = FINAL ] && echo "$FINAL" || echo "$SUPPF5")
  for mode in v0 hc panel; do
    $N $PY -I t9_dump.py --code $CODE --out $D --mode $mode --group $fam $RUNS --threads 8 >> $LOG 2>&1; rc=$?
    st "dump $fam $mode rc=$rc"
    [ $rc -eq 0 ] || exit 4
  done
done
$N $PY -I t9_dump.py --code $CODE --out $D --mode v0 --img rf --group SUPPF5 $SUPPF5 --threads 8 >> $LOG 2>&1; rc=$?
st "dump SUPPF5 v0 rf rc=$rc"

# 4. records (ensembles only) with calib's el_metrics, unchanged
for f in $D/FINAL__V*.rf.npz $D/SUPPF5__V*.rf.npz; do
  b=$(basename $f .npz)
  case $b in *_m[0-9]*) continue;; esac
  $N $PY -I el_metrics.py records --dump $f --set rf --out $RC/$b.json --procs 4 >> $LOG 2>&1; rc=$?
  st "records $b rc=$rc"
done
# SUPPF5 val records for its fixed OP (A0: val OP-rel b), from calib's source-BN val dump
$N $PY -I el_metrics.py records --dump $CAL/SUPPF5.val.npz --set val --code $CODE --out $RC/SUPPF5.val.json --procs 4 >> $LOG 2>&1; rc=$?
st "records SUPPF5 val rc=$rc"

# 5. rule
$N $PY -I t9_score.py --rec $RC --fam FINAL --op 0.75 --fam SUPPF5 --val-rec SUPPF5=$RC/SUPPF5.val.json --out $T/t9_result.json > $T/t9_result.txt 2>&1; rc=$?
st "T9 score rc=$rc"
st "T9 DONE"
