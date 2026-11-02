#!/bin/bash
# coach (1 Nov, respawned): HC opening verification ON GAINT CPU (protocol_HC v1.1; E1 opening #3). Reads the opening's files in place
# (read-only) after md5sum -c of the HC post MANIFEST, the PF2 comparator MANIFEST and the SHV1 / rf dump md5 list. Own code:
# coach_verify.py b0456b28 (test two-set, tau 0 / 1), coach_hc.py (E1 co-primaries, SHV1 mechanism, F51 guard; selftest first).
# Training stdouts: grep -c counts only (never tail / cat). nice 19, 8 threads, CUDA hidden. Outputs (text) in coach_v/hc/out.
set -u
B=/home/noob/work/coach_v/bin; OUT=/home/noob/work/coach_v/hc/out; mkdir -p $OUT
G=/home/noob/work/el_hc; RAW=$G/reports/hc/post; W=$G/reports/hc/syn_work; P2=/home/noob/work/el_f3/reports/pf2/post
PY=/home/noob/work/el-fault-detection/.venv/bin/python; CTX=$B/e1_context.tsv; DEP=c2e6973
RF=/home/noob/work/calib/data/rf; RFS=/home/noob/work/found/t9/rf_sets.tsv; SHV1P=/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
while [ -e /home/noob/work/coach_v/hc/HOLD ]; do sleep 60; done   # runner may hold this recompute until his explicit window over
grep -qE 'nq scoring done: post rc=' /home/noob/work/nq/post.log && test -s $RAW/MANIFEST.md5 || { echo "HC opening not done: abort"; exit 1; }
{ grep -E 'nq scoring done|NOT scored' /home/noob/work/nq/post.log
  (cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "HC post md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files") || echo "HC post md5sum -c FAILED"
  (cd $P2 && md5sum -c --quiet MANIFEST.md5 && echo "PF2 comparator post md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) (expect 3827f7c0)") || echo "PF2 md5sum -c FAILED"
  (cd $W/dump && md5sum -c --quiet $RAW/shv1/dump_md5_on_gaint.txt && echo "syn_work dumps md5sum -c OK ($(wc -l < $RAW/shv1/dump_md5_on_gaint.txt))") || echo "dump md5sum -c FAILED"
  echo "coach code: $(cd $B && md5sum coach_verify.py coach_hc.py coach_thin.py e1_context.tsv | cut -c1-8 | tr '\n' ' ')"
  echo "rf_sets $(md5sum < $RFS | cut -c1-8) (expect 14771356); shv1p $(md5sum < $SHV1P | cut -c1-8) (expect 7f651fc7)"
  cd $G; echo "REVISION $(cat REVISION) HEAD $(git rev-parse --short HEAD) tracked-modified $(git status --short --untracked-files=no | wc -l)"
  for k in 5 6 7 8 9; do r=hc_HC_100pct_s$k; f=experiments/$r.stdout
    echo "$r hdr=$(grep -c 'INFO train — Run: ' $f) s20k=$(grep -c 'step 20000/20000' $f) tb=$(grep -c Traceback $f) pf=$(grep -c 'PF encoder lr' $f) synth=$(grep -c 'synth_halfcut' $f)"
    diff /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml experiments/$r/config_used.yaml | sed 's/^/   /'
    grep -E "(trained|config OK|CONFIG FAIL).*$r( |$)" /home/noob/work/nq/launch.log | sed 's/^/   /'
  done
  grep -E 'HOLD|FAIL' /home/noob/work/nq/launch.log
  echo "gpumem min free (nq log): $(grep -v '^#' /home/noob/work/nq/gpumem.log | awk '{print $2, $1}' | sort -n | head -1)"
  for f in decision_rc.txt secondary_rc.txt extra_rc.txt tau0_check.txt comparator_check.txt scorer_md5.txt; do echo "== $f"; cat $RAW/$f 2>/dev/null; done
  echo "== enc cosine 20k"; tail -12 $RAW/enc_cosine_20k.txt 2>/dev/null
  echo "== runner/scorer readouts (decision passes)"; tail -8 $RAW/e1_coprim.txt 2>/dev/null; tail -6 $RAW/shv1/shv1_readout.txt 2>/dev/null; tail -4 $RAW/f51/hc_f51.txt 2>/dev/null
} > $OUT/integrity.txt 2>&1
M=$RAW/m0; MB=$P2/m0
L(){ for k in 5 6 7 8 9; do echo -n $1/$2_100pct_s$k${3:-}.json,; done | sed 's/,$//'; }
nice -n 19 $PY -I $B/coach_verify.py --base $(L $MB pf2_SUPPF) --arm $(L $M hc_HC) --boot 2000 --e1ctx $CTX > $OUT/verify_HC_tau0.txt 2>&1; echo "verify tau0 rc=$?" >> $OUT/integrity.txt
nice -n 19 $PY -I $B/coach_verify.py --base $(L $MB pf2_SUPPF .tau1) --arm $(L $M hc_HC .tau1) --boot 2000 > $OUT/verify_HC_tau1.txt 2>&1; echo "verify tau1 rc=$?" >> $OUT/integrity.txt
nice -n 19 $PY -I $B/coach_hc.py selftest /home/noob/work/calib/out/rec /home/noob/work/calib/out/rec_shv1 > $OUT/coach_hc_selftest.txt 2>&1; echo "coach_hc selftest rc=$?" >> $OUT/integrity.txt
nice -n 19 $PY -I $B/coach_hc.py run $RAW $P2 $RAW/shv1/rec $W/dump $RF $RFS $CTX $SHV1P > $OUT/coach_hc.txt 2>&1; echo "coach_hc run rc=$?" >> $OUT/integrity.txt
echo "coach hc verify done $(date '+%H:%M:%S')" >> $OUT/integrity.txt
(cd $OUT && md5sum integrity.txt verify_HC_tau0.txt verify_HC_tau1.txt coach_hc_selftest.txt coach_hc.txt > MD5)
