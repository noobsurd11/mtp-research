#!/bin/bash
# coach (2 Nov): SKR2 + HC2 opening verification ON GAINT CPU (protocol_SKR2_HC2 v1.1; E1 opening #5), after 's2q scoring done'.
# Reads the opening in place (read-only) after md5sum -c of its MANIFEST, the PF2 / HC comparator MANIFESTs and the syn dumps.
# Own code: coach_verify.py b0456b28 (test two-set, tau 0 / 1, per arm vs SUPPF), coach_s2.py (E1, B5 wide, guards, F51, SHV1;
# selftest first). Training stdouts: grep -c only. nice 19, 8 threads, CUDA hidden. Outputs (text) in coach_v/s2/out.
set -u
while [ -e /home/noob/work/coach_v/s2/HOLD ]; do sleep 60; done
B=/home/noob/work/coach_v/bin; OUT=/home/noob/work/coach_v/s2/out; mkdir -p $OUT
S2=/home/noob/work/s2q; P2=$S2/post; PF=/home/noob/work/el_f3/reports/pf2/post; HC=/home/noob/work/el_hc/reports/hc/post
HCSYN=/home/noob/work/el_hc/reports/hc/syn_work/dump; SYN=$S2/post_work/syn/dump; TH=/home/noob/work/el_thin/reports/thin/post
PY=/home/noob/work/el-fault-detection/.venv/bin/python; CTX=$B/e1_context.tsv; RF=/home/noob/work/calib/data/rf; RFS=/home/noob/work/found/t9/rf_sets.tsv
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
grep -qE 's2q scoring done: post rc=' $S2/post.log && test -s $P2/MANIFEST.md5 || { echo "S2 opening not done: abort"; exit 1; }
{ grep -E 's2q scoring done|NOT scored' $S2/post.log
  (cd $P2 && md5sum -c --quiet MANIFEST.md5 && echo "S2 post md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files") || echo "S2 post md5sum -c FAILED"
  (cd $PF && md5sum -c --quiet MANIFEST.md5 && echo "PF2 post OK $(md5sum < MANIFEST.md5 | cut -c1-8) (expect 3827f7c0)") || echo "PF2 md5sum -c FAILED"
  (cd $HC && md5sum -c --quiet MANIFEST.md5 && echo "HC post OK $(md5sum < MANIFEST.md5 | cut -c1-8) (expect d5c39e0d)") || echo "HC md5sum -c FAILED"
  (cd $HCSYN && md5sum -c --quiet $HC/shv1/dump_md5_on_gaint.txt && echo "HC syn dumps OK") || echo "HC syn dumps FAILED"
  [ -s $P2/shv1/dump_md5_on_gaint.txt ] && { (cd $SYN && md5sum -c --quiet $P2/shv1/dump_md5_on_gaint.txt && echo "S2 syn dumps OK ($(wc -l < $P2/shv1/dump_md5_on_gaint.txt))") || echo "S2 syn dumps FAILED"; }
  echo "FROZEN used: $(md5sum < $P2/FROZEN_s2.md5 | cut -c1-8) (expect fb5becd2)"
  echo "coach code: $(cd $B && md5sum coach_verify.py coach_s2.py coach_hc.py coach_thin.py e1_context.tsv | cut -c1-8 | tr '\n' ' ')"
  for W in el_thin:c9bbb02 el_hc2:0405151; do d=/home/noob/work/${W%%:*}; echo "${W%%:*} HEAD $(git -C $d rev-parse --short HEAD) REVISION $(cut -c1-7 $d/REVISION) tracked $(git -C $d status --short --untracked-files=no | wc -l) (expect ${W##*:})"; done
  for r in skr2_SKR01 hc2_HCig; do for k in 5 6 7 8 9; do n=${r}_100pct_s$k; case $r in skr2*) d=/home/noob/work/el_thin;; *) d=/home/noob/work/el_hc2;; esac; f=$d/experiments/$n.stdout
    echo "$n hdr=$(grep -c 'INFO train — Run: ' $f) s20k=$(grep -c 'step 20000/20000' $f) tb=$(grep -c Traceback $f) pf=$(grep -c 'PF encoder lr' $f)"
    diff /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml $d/experiments/$n/config_used.yaml | grep -E '^[<>]' | grep -vE 'run_name|seed:' | sed 's/^/   /'
    grep -E "(trained|config OK|CONFIG FAIL).*$n( |$)" $S2/launch.log | sed 's/^/   /'; done; done
  grep -E 'HOLD|FAIL' $S2/launch.log
  echo "gpumem min free: $(grep -v '^#' $S2/gpumem.log 2>/dev/null | awk '{print $2, $1}' | sort -n | head -1)"
  for f in decision_rc.txt extra_rc.txt hc2_synth_readout.txt; do echo "== $f"; cat $P2/$f 2>/dev/null; done
  echo "== opening readouts (decision passes)"; tail -12 $P2/e1_coprim.txt 2>/dev/null; cat $P2/guards.txt 2>/dev/null | tail -8; tail -8 $P2/shv1/shv1_readout.txt 2>/dev/null; tail -6 $P2/f51/s2_f51.txt 2>/dev/null
  tail -20 $P2/b5/b5w_table.txt 2>/dev/null
} > $OUT/integrity.txt 2>&1
L(){ for k in 5 6 7 8 9; do echo -n $1/$2_100pct_s$k${3:-}.json,; done | sed 's/,$//'; }
for a in SKR01:skr2_SKR01 HC2:hc2_HCig; do A=${a%%:*}; N=${a##*:}
  nice -n 19 $PY -I $B/coach_verify.py --base $(L $PF/m0 pf2_SUPPF) --arm $(L $P2/m0/$A $N) --boot 2000 --e1ctx $CTX > $OUT/verify_${A}_tau0.txt 2>&1; echo "verify $A tau0 rc=$?" >> $OUT/integrity.txt
  nice -n 19 $PY -I $B/coach_verify.py --base $(L $PF/m0 pf2_SUPPF .tau1) --arm $(L $P2/m0/$A $N .tau1) --boot 2000 > $OUT/verify_${A}_tau1.txt 2>&1; echo "verify $A tau1 rc=$?" >> $OUT/integrity.txt
done
nice -n 19 $PY -I $B/coach_s2.py selftest $PF $HC $HCSYN $TH $RF $RFS $CTX > $OUT/coach_s2_selftest.txt 2>&1; echo "coach_s2 selftest rc=$?" >> $OUT/integrity.txt
nice -n 19 $PY -I $B/coach_s2.py run $P2 $SYN $PF $HC $HCSYN $RF $RFS $CTX > $OUT/coach_s2.txt 2>&1; echo "coach_s2 run rc=$?" >> $OUT/integrity.txt
echo "coach s2 verify done $(date '+%H:%M:%S')" >> $OUT/integrity.txt
(cd $OUT && md5sum integrity.txt verify_*_tau*.txt coach_s2_selftest.txt coach_s2.txt > MD5)
