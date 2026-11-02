#!/bin/bash
# SKR2 + HC2 opening, pass 11: SHV1 mechanism (protocol_SKR2_HC2 v1.0.1 §3b decision for HC2; SKR2 context, §4) + the val / rf dumps
# of the F51 pass. DRAFT (runner's helper, 2 Nov 2026) for coach's FREEZE. From hc_shv1.sh (ba4c6c51, frozen HC): passes, devices,
# scorers, CPU_HOLD, PID records and exit codes kept; changed: the 10 NEW runs (SKR01 + HC2, two worktrees, code per run from
# s2_settings.sh) are dumped; SUPPF s5-9 (and HC s5-9, reference row) are NOT re-dumped: their records come from the HC opening's
# post/shv1/rec (HC MANIFEST d5c39e0d lines, md5sum -c here) and their dumps stay in HC's syn_work (checked in s2_post pass 0).
# s2_post.sh runs it (no env needed). Data: val (54), rf (106), synval = SHV1 (108; MANIFEST 63dd5469); NO test (calib_dump refuses test
# without --opening, none passed), NO E1 (no ext).
# Device: CPU fp32 for all 10 new runs (as HC's SUPPF / HC dumps: same device on both sides; CUDA hidden, nice 19, <= 8 threads); no GPU.
# Scorers: calib's synval-capable superset calib_dump 9694ad7d / el_metrics f40a0efe (copies in open/calib_syn/; frozen for HC by coach).
# Passes: 0 md5 / size pre-checks (any failure: exit 2, nothing computed); 1 calib_dump --sets val rf synval per new run (step 20000
# asserted by calib_dump) -> W/dump; 2 el_metrics records per run x set -> W/rec (UNCHECKED); 3 val records self-check vs the run's m0
# val cells, tol profile cpu (reported only); 4 s2_shv1_read --selftest (calib's pre-check records + HC opening records), then the
# readout -> post/shv1/shv1_readout.{json,txt}; 5 copies of the new records + md5 lists into post/shv1. W (~3.5 GB) stays on gaint.
# exit: 0 all OK | 1 readout failed but dumps + records complete (W/DUMPS_OK; F51 can run) | 2 pre-check, dump or records failed.
# Every python pass: nice 19, PID in W/pids.txt, waited for. File s2q/CPU_HOLD (runner-declared CPU window) pauses before each pass.
set -u
. /home/noob/work/s2q/open/s2_settings.sh || exit 2
H=$OPEN; C=$H/calib_syn
O=$S2_OUT/shv1; W=$WK/syn; LOG=$O/s2_shv1.log; HOLDF=$S2/CPU_HOLD
SV=/home/noob/work/domain_scratch/shv1; SVM=63dd5469cc4eeaf21025e98669d635e3; RF=/home/noob/work/calib/data/rf
SHV1P=/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt; CAL=/home/noob/work/calib/out
NEW="$SKR_RUNS $HC2_RUNS"
export CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p $O || exit 2
[ -e $W ] && { echo "[$(date)] refused: $W exists (a rerun needs coach's word and a fresh dir)" >> $LOG; exit 2; }
mkdir -p $W/dump $W/rec || exit 2
log(){ echo "[$(date)] $*" >> $LOG; }
hold(){ [ -e $HOLDF ] && log "CPU_HOLD seen; waiting"; while [ -e $HOLDF ]; do sleep 60; done; }
run(){ local tag=$1 out=$2 pp; shift 2; hold; nice -n 19 "$@" >> "$out" 2>&1 & pp=$!; echo "$(date '+%F %T') $pp $tag" >> $W/pids.txt; wait $pp; }
code_of(){ wt_of "$(arm_of $1)"; }
m0_of(){ echo $S2_OUT/m0/$(arm_of $1)/$1.json; }
log "s2_shv1 start: pid $$; script md5 $(md5sum < "$0" | cut -c1-32); CPU fp32, CUDA hidden, nice 19, 8 threads; new runs $(echo $NEW | wc -w)"
m=$(settings_check) || { log "PRE-CHECK FAIL: $m"; exit 2; }

# ---- 0. pre-checks (nothing computed on failure) ----
printf '%s\n' \
  "9694ad7d9e8528e7fc4542acaaf5b5b3  $C/calib_dump.py" \
  "f40a0efe0baa8f3ce419f0c55a70442e  $C/el_metrics.py" \
  "$SVM  $SV/MANIFEST.md5" \
  "f809683f33f7eac4593228a8614d0879  $SV/stems_eval.txt" \
  "7f651fc7348f4dcaa06d404645fa1951  $SHV1P" \
  "3a65c2fb0ecaf32e91377d4ad249029a  $RF/stems_eval.txt" \
  "9dcccf00662dfca750f0b46628f8d5bb  $SKR_WT/data/splits/val.txt" \
  "9dcccf00662dfca750f0b46628f8d5bb  $HC2_WT/data/splits/val.txt" \
  "6d038462ca3f2b68fb0dd2f0dd1e287f  $CAL/rec/FINAL.val.json" \
  "ed5365dd6f7cc612b778aaff118d6e7c  $CAL/rec_shv1/FINAL.synval.json" \
  "f089abce9f5d691996771e359c907231  $CAL/rec_shv1/MANIFEST.md5" \
  "e23b33aca620f9edff9b537380e0e317  $CAL/rec/SUPPF5_m0.val.json" \
  "fc2a9bf722b0855d48e94606fbc1fd81  $CAL/rec/SUPPF5_m1.val.json" \
  "29658f17187a54e7a633c1c540fea504  $CAL/rec/SUPPF5_m2.val.json" \
  "cabccfe994233fad44e124593f975c03  $CAL/rec/SUPPF5_m3.val.json" \
  "ebae273b82d09b751293a48a9883432d  $CAL/rec/SUPPF5_m4.val.json" \
  "$MAN_HC  $HCP/MANIFEST.md5" > $O/expected_md5.txt
md5sum -c $O/expected_md5.txt >> $LOG 2>&1 || { log "PRE-CHECK FAIL: md5 (FAILED lines above); NOT computed"; exit 2; }
(cd $SV && md5sum -c --quiet MANIFEST.md5) >> $LOG 2>&1 || { log "PRE-CHECK FAIL: SHV1 files vs MANIFEST"; exit 2; }
(cd $CAL/rec_shv1 && md5sum -c --quiet MANIFEST.md5) >> $LOG 2>&1 || { log "PRE-CHECK FAIL: calib rec_shv1 vs MANIFEST"; exit 2; }
# SUPPF + HC records of the HC opening (reused): their lines of HC's post MANIFEST, md5sum -c (30 rec JSON + 30 selfcheck txt)
grep -E '  \./shv1/rec/(pf2_SUPPF|hc_HC)_100pct_s[5-9]\.(val|rf|synval)\.json(\.selfcheck\.txt)?$' $HCP/MANIFEST.md5 > $O/reused_rec_md5.txt
[ "$(wc -l < $O/reused_rec_md5.txt)" = 60 ] || { log "PRE-CHECK FAIL: HC MANIFEST lists $(wc -l < $O/reused_rec_md5.txt) of the 60 reused record files"; exit 2; }
(cd $HCP && md5sum -c --quiet $O/reused_rec_md5.txt) >> $LOG 2>&1 || { log "PRE-CHECK FAIL: reused SUPPF / HC records changed"; exit 2; }
[ "$(wc -l < $SHV1P)" = 80 ] || { log "PRE-CHECK FAIL: SHV1-p list size != 80"; exit 2; }
[ "$(wc -l < $SV/stems_eval.txt)" = 108 ] || { log "PRE-CHECK FAIL: SHV1 list size != 108"; exit 2; }
[ "$(wc -l < $RF/stems_eval.txt)" = 106 ] || { log "PRE-CHECK FAIL: rf list size != 106"; exit 2; }
for n in $NEW; do
  r=$(code_of $n)/experiments/$n
  for f in $r/checkpoints/latest.pth $r/config_used.yaml $(m0_of $n); do [ -s $f ] || { log "PRE-CHECK FAIL: $n: $f missing"; exit 2; }; done
  md5sum $r/checkpoints/latest.pth $r/config_used.yaml >> $O/inputs_md5.txt
done
log "pre-checks OK ($(wc -l < $O/expected_md5.txt) md5s, SHV1 + calib rec_shv1 MANIFESTs, 60 reused HC-opening record files, list sizes, 10 runs' inputs)"

# ---- 1. dumps: val + rf + SHV1, CPU fp32 (new runs only) ----
F=0
for n in $NEW; do
  run dump_$n $W/dump.log env OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 $P -B $C/calib_dump.py --code $(code_of $n) \
    --out $W/dump --group $n $(code_of $n)/experiments/$n --sets val rf synval --synval $SV --synval-manifest $SVM --rf $RF --device cpu --threads 8
  rc=$?; log "pass 1 dump $n (val 54, rf 106, SHV1 108; CPU fp32) rc=$rc"
  for s in val rf synval; do [ -s $W/dump/$n.$s.npz ] || rc=9; done; [ $rc = 0 ] || F=$((F + 1))
done
[ $F = 0 ] || { log "pass 1 failed for $F runs; stop"; exit 2; }

# ---- 2. records (8 procs x 1 thread) ----
for n in $NEW; do for s in val rf synval; do
  run rec_${n}_$s $W/rec.log env OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 $P -B $C/el_metrics.py records \
    --dump $W/dump/$n.$s.npz --set $s --code $(code_of $n) --rf $RF --synval $SV --synval-manifest $SVM --out $W/rec/$n.$s.json --procs 8
  rc=$?; log "pass 2 records $n $s rc=$rc"
  [ $rc = 0 ] || F=$((F + 1)); [ -s $W/rec/$n.$s.json ] || F=$((F + 1))
done; done
[ $F = 0 ] || { log "pass 2 failed for $F record files; stop"; exit 2; }
touch $W/DUMPS_OK

# ---- 3. val records vs the m0 val cells at b 0 (tol profile cpu; reported, non-deciding) ----
for n in $NEW; do
  run sc_$n $O/val_selfcheck.txt $P -B $C/el_metrics.py selfcheck --rec $W/rec/$n.val.json --m0 $(m0_of $n) --m0-set val --tol-profile cpu
  rc=$?; echo "$n val selfcheck (cpu profile) rc=$rc" >> $O/val_selfcheck_rc.txt
done
log "pass 3 val self-checks: $(grep -c 'rc=0$' $O/val_selfcheck_rc.txt)/10 rc 0 (reported only)"

# ---- 4. readout: self-test (calib pre-check records + HC opening records), then the s2 readout ----
R=0
run shv1_selftest $O/shv1_selftest.txt $P -B $H/s2_shv1_read.py --selftest --el-metrics $C --st-val $CAL/rec --st-syn $CAL/rec_shv1 --st-hc $HCP/shv1/rec
rc=$?; log "pass 4a s2_shv1_read --selftest rc=$rc"
if [ $rc = 0 ]; then
  run shv1_read $O/shv1_readout.txt $P -B $H/s2_shv1_read.py --el-metrics $C --arm SUPPF $HCP/shv1/rec $CMP_RUNS --arm HC2 $W/rec $HC2_RUNS \
    --arm SKR01 $W/rec $SKR_RUNS --arm HC $HCP/shv1/rec $HC_RUNS --base SUPPF --test HC2 SKR01 --decide HC2 --ref-arm HC \
    --shv1p $SHV1P --ref FINAL $CAL/rec/FINAL.val.json $CAL/rec_shv1/FINAL.synval.json 0.75 --out $O/shv1_readout.json
  rc=$?; log "pass 4b SHV1 readout rc=$rc: $(grep '^MECHANISM \[DECISION\]' $O/shv1_readout.txt 2>/dev/null)"; [ $rc = 0 ] || R=1
else R=1; log "pass 4b skipped (self-test failed)"; fi

# ---- 5. copies (records are val / rf / SHV1 only) + md5 lists ----
mkdir -p $O/rec && cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $O/rec/
(cd $W/dump && md5sum *.npz) > $O/dump_md5_on_gaint.txt
md5sum -c --quiet $O/inputs_md5.txt >> $LOG 2>&1 || { log "inputs changed during the pass"; R=1; }
cp -p $W/pids.txt $O/
log "s2_shv1 done: readout fail flag $R"
exit $R
