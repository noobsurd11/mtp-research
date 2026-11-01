#!/bin/bash
# runner (1 Nov 2026): PF2E reported-only B5 operating points + cell-level (protocol_PF2E §4; coach ruling option (b): calib's frozen
# calib_dump.py c172717e group ensembles, no new dump code). Runs on gaint CPU fp32 AFTER pf2e_infer's verdict files exist and are
# pulled (MANIFEST). Never changes a verdict. CPU only (CUDA hidden), nice 19, <= 8 threads; not inside a runner-declared window.
#   1. calib_dump --group E-g <SUP s5-9> --group E-PF <SUPPF s5-9> --no-members --sets val test ext --opening protocol_PF2E
#      --device cpu (mean softmax = pf2e_infer's ensembles) -> b5_work/dump/E-*.{val,test,ext}.npz (outside out/; stay on gaint)
#   2. el_metrics 6e73ff11 records per ensemble and set, b = 0 self-check vs PF2E's own out/E-*.b0.json (cells val / test / ext),
#      tol profile exact; only if exact FAILS, a second try with the cpu profile, disclosed in b5_selfcheck_profile.txt
#   3. el_metrics summary per ensemble on test, test_clean (-CSIR_00070_r8_c4) and ext, OPs from val, --deployed-b = that
#      ensemble's headline b from out/pf2e_val_decisions.json (cell_b0 is reported by el_metrics too)
# Copies rec/*.json, rec/*.selfcheck.txt, sum/*.json and the log into out_b5/ (pulled). rc captured before $(date).
set -u
cd /home/noob/work/el_f3/reports/pf2e
CS=/home/noob/work/el_f3/reports/pf2/post_extra/calib; W=/home/noob/work/el_f3/reports/pf2e/b5_work; O=out_b5
P=/home/noob/work/el-fault-detection/.venv/bin/python; E=/home/noob/work/el_f3/experiments; LOG=$W/b5.log; F=0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
printf '%s\n' "c172717e5989edb8e0b7b312096f9180  $CS/calib_dump.py" "6e73ff11aaa6171a52b5a5404877ab46  $CS/el_metrics.py" | md5sum -c --quiet \
  || { echo "frozen calib md5 FAIL"; exit 1; }
[ -s out/pf2e_val_decisions.json ] && [ -s out/E-g.b0.json ] && [ -s out/E-PF.b0.json ] || { echo "PF2E verdict files missing"; exit 1; }
mkdir -p $W/dump $W/rec $W/sum $O
md5sum $CS/calib_dump.py $CS/el_metrics.py "$0" out/pf2e_val_decisions.json out/E-g.b0.json out/E-PF.b0.json >> $LOG
EG=$(for k in 5 6 7 8 9; do echo -n "$E/pf2_SUP_100pct_s$k "; done); EPF=$(for k in 5 6 7 8 9; do echo -n "$E/pf2_SUPPF_100pct_s$k "; done)
nice -n 19 $P $CS/calib_dump.py --code /home/noob/work/el_f3 --out $W/dump --group E-g $EG --group E-PF $EPF --no-members \
  --sets val test ext --opening protocol_PF2E --device cpu --threads 8 >> $LOG 2>&1
rc=$?; echo "[$(date)] b5 dump rc=$rc" >> $LOG; [ $rc -ne 0 ] && exit 1
for N in E-g E-PF; do
  for S in val test ext; do
    TP=exact
    OMP_NUM_THREADS=1 nice -n 19 $P $CS/el_metrics.py records --dump $W/dump/$N.$S.npz --set $S --code /home/noob/work/el_f3 \
      --out $W/rec/$N.$S.json --m0 out/$N.b0.json --m0-set $S --tol-profile exact --procs 8 >> $LOG 2>&1
    rc=$?
    if [ $rc -ne 0 ]; then
      TP=cpu
      OMP_NUM_THREADS=1 nice -n 19 $P $CS/el_metrics.py records --dump $W/dump/$N.$S.npz --set $S --code /home/noob/work/el_f3 \
        --out $W/rec/$N.$S.json --m0 out/$N.b0.json --m0-set $S --tol-profile cpu --procs 8 >> $LOG 2>&1
      rc=$?; fi
    echo "$N $S self-check profile $TP rc=$rc" >> $O/b5_selfcheck_profile.txt
    echo "[$(date)] b5 records+selfcheck $N $S profile $TP rc=$rc" >> $LOG; [ $rc -ne 0 ] && F=$((F+1))
  done
  HB=$($P -c "import json; print(json.load(open('out/pf2e_val_decisions.json'))['$N']['headline_bias'])")
  for T in test ext; do
    nice -n 19 $P $CS/el_metrics.py summary --val $W/rec/$N.val.json --target $W/rec/$N.$T.json --deployed-b $HB --out $W/sum/$N.$T.json >> $LOG 2>&1
    rc=$?; echo "[$(date)] b5 summary $N $T (deployed b $HB) rc=$rc" >> $LOG; [ $rc -ne 0 ] && F=$((F+1)); done
  nice -n 19 $P $CS/el_metrics.py summary --val $W/rec/$N.val.json --target $W/rec/$N.test.json --deployed-b $HB --exclude CSIR_00070_r8_c4 \
    --out $W/sum/$N.test_clean.json >> $LOG 2>&1
  rc=$?; echo "[$(date)] b5 summary $N test_clean (deployed b $HB) rc=$rc" >> $LOG; [ $rc -ne 0 ] && F=$((F+1))
done
cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $W/sum/*.json $LOG $O/ 2>/dev/null
(cd $W/dump && md5sum *.npz) > $O/dump_md5_on_gaint.txt
(cd $O && md5sum $(ls | grep -v MANIFEST) > MANIFEST.md5)
echo "[$(date)] pf2e b5 done fails=$F" >> $LOG; [ $F = 0 ]
