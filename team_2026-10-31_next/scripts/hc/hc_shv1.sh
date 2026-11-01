#!/bin/bash
# HC opening, mechanism pass (protocol_HC v1.1 §4 mechanism kill, §5 readouts) + the shared dumps of the F51 guard. DRAFT (runner's
# helper, 1 Nov 2026) for coach's FREEZE. hc_post.sh runs it with OUT set (absolute). Val-derived data and Hanifi _rf only: sets val (54),
# rf (106) and synval = SHV1 (108; MANIFEST 63dd5469); NO test (calib_dump refuses test without --opening, none passed), NO E1 (no ext).
# Device: CPU fp32 for ALL 10 runs (HC s5-9 and the comparator pf2_SUPPF s5-9, same device on both sides; CUDA hidden, nice 19,
# <= 8 threads); no GPU gate (reasons: build_hc_runner.md §4). Scorers: calib's synval-capable SUPERSET calib_dump 9694ad7d /
# el_metrics f40a0efe (copies in /home/noob/work/nq/hc/calib_syn/; NOT calib's frozen B5 pair; frozen for HC only by coach's FROZEN.md5).
# Passes: 0 md5 / size pre-checks (any failure: exit 2, nothing computed); 1 calib_dump --sets val rf synval per run (step 20000
# asserted by calib_dump) -> W/dump; 2 el_metrics records per run x set -> W/rec (UNCHECKED); 3 val records self-check vs the run's m0
# val cells, tol profile cpu (reported only; HC m0 from this opening, SUPPF m0 from PF2's opening); 4 hc_shv1_read --selftest on calib's
# routing pre-check records (must reproduce the published values), then the readout -> OUT/shv1/shv1_readout.{json,txt}; 5 copies of
# records + md5 lists into OUT/shv1. W (dumps, ~3.5 GB) stays on gaint, outside post/.
# exit: 0 all OK | 1 readout failed but dumps + records complete (W/DUMPS_OK; F51 can run) | 2 pre-check, dump or records failed.
# Every python pass: nice 19, PID in W/pids.txt, waited for. File el_hc/reports/hc/CPU_HOLD (runner-declared CPU window) pauses before
# each pass. rc captured before $(date).
set -u
H=/home/noob/work/nq/hc; C=$H/calib_syn; P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=${OUT:?}; O=$OUT/shv1; W=/home/noob/work/el_hc/reports/hc/syn_work; LOG=$O/hc_shv1.log; HOLDF=/home/noob/work/el_hc/reports/hc/CPU_HOLD
SV=/home/noob/work/domain_scratch/shv1; SVM=63dd5469cc4eeaf21025e98669d635e3; RF=/home/noob/work/calib/data/rf
SHV1P=/home/noob/work/domain_scratch/out/shv1p_stems_eval.txt; CAL=/home/noob/work/calib/out
PFM0=/home/noob/work/el_f3/reports/pf2/post/m0; HCM0=$OUT/m0
HC5=$(for k in 5 6 7 8 9; do echo hc_HC_100pct_s$k; done); SP5=$(for k in 5 6 7 8 9; do echo pf2_SUPPF_100pct_s$k; done)
export CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p $O || exit 2
[ -e $W ] && { echo "[$(date)] refused: $W exists (a rerun needs coach's word and a fresh dir)" >> $LOG; exit 2; }
mkdir -p $W/dump $W/rec || exit 2
log(){ echo "[$(date)] $*" >> $LOG; }
hold(){ [ -e $HOLDF ] && log "CPU_HOLD seen; waiting"; while [ -e $HOLDF ]; do sleep 60; done; }
run(){ local tag=$1 out=$2 pp; shift 2; hold; nice -n 19 "$@" >> "$out" 2>&1 & pp=$!; echo "$(date '+%F %T') $pp $tag" >> $W/pids.txt; wait $pp; }
code_of(){ case $1 in hc_HC_*) echo /home/noob/work/el_hc;; pf2_SUPPF_*) echo /home/noob/work/el_f3;; esac; }
m0_of(){ case $1 in hc_HC_*) echo $HCM0/$1.json;; pf2_SUPPF_*) echo $PFM0/$1.json;; esac; }
log "hc_shv1 start: pid $$; script md5 $(md5sum < "$0" | cut -c1-32); CPU fp32, CUDA hidden, nice 19, 8 threads"

# ---- 0. pre-checks (nothing computed on failure) ----
printf '%s\n' \
  "9694ad7d9e8528e7fc4542acaaf5b5b3  $C/calib_dump.py" \
  "f40a0efe0baa8f3ce419f0c55a70442e  $C/el_metrics.py" \
  "$SVM  $SV/MANIFEST.md5" \
  "f809683f33f7eac4593228a8614d0879  $SV/stems_eval.txt" \
  "7f651fc7348f4dcaa06d404645fa1951  $SHV1P" \
  "3a65c2fb0ecaf32e91377d4ad249029a  $RF/stems_eval.txt" \
  "9dcccf00662dfca750f0b46628f8d5bb  /home/noob/work/el_hc/data/splits/val.txt" \
  "9dcccf00662dfca750f0b46628f8d5bb  /home/noob/work/el_f3/data/splits/val.txt" \
  "6d038462ca3f2b68fb0dd2f0dd1e287f  $CAL/rec/FINAL.val.json" \
  "ed5365dd6f7cc612b778aaff118d6e7c  $CAL/rec_shv1/FINAL.synval.json" \
  "f089abce9f5d691996771e359c907231  $CAL/rec_shv1/MANIFEST.md5" \
  "e23b33aca620f9edff9b537380e0e317  $CAL/rec/SUPPF5_m0.val.json" \
  "fc2a9bf722b0855d48e94606fbc1fd81  $CAL/rec/SUPPF5_m1.val.json" \
  "29658f17187a54e7a633c1c540fea504  $CAL/rec/SUPPF5_m2.val.json" \
  "cabccfe994233fad44e124593f975c03  $CAL/rec/SUPPF5_m3.val.json" \
  "ebae273b82d09b751293a48a9883432d  $CAL/rec/SUPPF5_m4.val.json" > $O/expected_md5.txt
md5sum -c $O/expected_md5.txt >> $LOG 2>&1 || { log "PRE-CHECK FAIL: md5 (FAILED lines above); NOT computed"; exit 2; }
(cd $SV && md5sum -c --quiet MANIFEST.md5) >> $LOG 2>&1 || { log "PRE-CHECK FAIL: SHV1 files vs MANIFEST"; exit 2; }
(cd $CAL/rec_shv1 && md5sum -c --quiet MANIFEST.md5) >> $LOG 2>&1 || { log "PRE-CHECK FAIL: calib rec_shv1 vs MANIFEST"; exit 2; }
[ "$(wc -l < $SHV1P)" = 80 ] && [ "$(wc -l < $SV/stems_eval.txt)" = 108 ] && [ "$(wc -l < $RF/stems_eval.txt)" = 106 ] \
  || { log "PRE-CHECK FAIL: list sizes (SHV1-p 80, SHV1 108, rf 106)"; exit 2; }
for n in $HC5 $SP5; do
  r=$(code_of $n)/experiments/$n
  [ -s $r/checkpoints/latest.pth ] && [ -s $r/config_used.yaml ] && [ -s $(m0_of $n) ] || { log "PRE-CHECK FAIL: $n checkpoint / config / m0 JSON missing"; exit 2; }
  md5sum $r/checkpoints/latest.pth $r/config_used.yaml >> $O/inputs_md5.txt
done
log "pre-checks OK ($(wc -l < $O/expected_md5.txt) md5s, SHV1 + calib rec_shv1 MANIFESTs, list sizes, 10 runs' inputs)"

# ---- 1. dumps: val + rf + SHV1, CPU fp32 ----
F=0
for n in $HC5 $SP5; do
  run dump_$n $W/dump.log env OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 $P -B $C/calib_dump.py --code $(code_of $n) \
    --out $W/dump --group $n $(code_of $n)/experiments/$n --sets val rf synval --synval $SV --synval-manifest $SVM --rf $RF --device cpu --threads 8
  rc=$?; log "pass 1 dump $n (val 54, rf 106, SHV1 108; CPU fp32) rc=$rc"
  for s in val rf synval; do [ -s $W/dump/$n.$s.npz ] || rc=9; done; [ $rc = 0 ] || F=$((F + 1))
done
[ $F = 0 ] || { log "pass 1 failed for $F runs; stop"; exit 2; }

# ---- 2. records (8 procs x 1 thread) ----
for n in $HC5 $SP5; do for s in val rf synval; do
  run rec_${n}_$s $W/rec.log env OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 $P -B $C/el_metrics.py records \
    --dump $W/dump/$n.$s.npz --set $s --code $(code_of $n) --rf $RF --synval $SV --synval-manifest $SVM --out $W/rec/$n.$s.json --procs 8
  rc=$?; log "pass 2 records $n $s rc=$rc"; [ $rc = 0 ] && [ -s $W/rec/$n.$s.json ] || F=$((F + 1))
done; done
[ $F = 0 ] || { log "pass 2 failed for $F record files; stop"; exit 2; }
touch $W/DUMPS_OK

# ---- 3. val records vs the m0 val cells at b 0 (tol profile cpu; reported, non-deciding) ----
for n in $HC5 $SP5; do
  run sc_$n $O/val_selfcheck.txt $P -B $C/el_metrics.py selfcheck --rec $W/rec/$n.val.json --m0 $(m0_of $n) --m0-set val --tol-profile cpu
  rc=$?; echo "$n val selfcheck (cpu profile) rc=$rc" >> $O/val_selfcheck_rc.txt
done
log "pass 3 val self-checks: $(grep -c 'rc=0$' $O/val_selfcheck_rc.txt)/10 rc 0 (reported only)"

# ---- 4. readout: self-test on calib's pre-check records, then the HC readout ----
R=0
run shv1_selftest $O/shv1_selftest.txt $P -B $H/hc_shv1_read.py --selftest --el-metrics $C --st-val $CAL/rec --st-syn $CAL/rec_shv1
rc=$?; log "pass 4a hc_shv1_read --selftest rc=$rc"
if [ $rc = 0 ]; then
  run shv1_read $O/shv1_readout.txt $P -B $H/hc_shv1_read.py --el-metrics $C --rec $W/rec --arm SUPPF $SP5 --arm HC $HC5 --base SUPPF --test HC \
    --shv1p $SHV1P --ref FINAL $CAL/rec/FINAL.val.json $CAL/rec_shv1/FINAL.synval.json 0.75 --out $O/shv1_readout.json
  rc=$?; log "pass 4b SHV1 readout rc=$rc: $(grep '^MECHANISM' $O/shv1_readout.txt 2>/dev/null)"; [ $rc = 0 ] || R=1
else R=1; log "pass 4b skipped (self-test failed)"; fi

# ---- 5. copies (records are val / rf / SHV1 only) + md5 lists ----
mkdir -p $O/rec && cp -p $W/rec/*.json $W/rec/*.selfcheck.txt $O/rec/
(cd $W/dump && md5sum *.npz) > $O/dump_md5_on_gaint.txt
md5sum -c --quiet $O/inputs_md5.txt >> $LOG 2>&1 || { log "inputs changed during the pass"; R=1; }
cp -p $W/pids.txt $O/
log "hc_shv1 done: readout fail flag $R"
exit $R
