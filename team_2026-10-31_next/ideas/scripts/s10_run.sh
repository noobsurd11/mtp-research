#!/bin/bash
# S10-inactive run (found, 31 Oct 2026): ideas/s10_prereg.md (judge APPROVED with A1). gaint CPU only.
set -u
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
S=/home/noob/work/found/s10; LOG=$S/s10.log; mkdir -p $S; cd $S
EL=/home/noob/work/el-fault-detection/.venv/bin/python; SAMPY=/home/noob/work/venv_sam2/bin/python
R=/home/noob/work/cv02_noob_el/el_p13/experiments
st() { echo "[$(date '+%F %T')] $*" >> $LOG; }
md5sum s10_inactive.py >> $LOG; st "start (pid $$)"
nice -n 19 $EL -I s10_inactive.py model --runs $R/p16_A_50pct_s0 $R/p16_A_50pct_s1 $R/p16_A_50pct_s2 $R/p16_A_50pct_s3 $R/p16_A_50pct_s4 --out $S >> $LOG 2>&1; rc=$?
st "model rc=$rc"; [ $rc -eq 0 ] || exit 1
nice -n 19 $SAMPY s10_inactive.py sam --out $S >> $LOG 2>&1; rc=$?
st "sam rc=$rc"; [ $rc -eq 0 ] || exit 2
nice -n 19 $EL -I s10_inactive.py score --out $S > $S/s10_rule.txt 2>> $LOG; rc=$?
st "score rc=$rc"
st "S10 DONE"
