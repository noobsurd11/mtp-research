#!/bin/bash
# Side GPU smokes in PF2's lone-RN50 phase (coach 31 Oct): (1) calib's B5 dump smoke, (2) builder's THIN / B3 smokes.
# Starts only when all 10 PF2 R34 runs trained rc 0 and none is alive (never beside 3 R34 runs). One job at a time, every start
# through the shared gate (/home/noob/work/gpu_gate: flock, free >= need, >= 120 s since any start; HOLD). 1 s gpumem logging
# while it runs (gpu_gate/FAST). Log: el_f3/reports/pf2/side/side.log. rc captured before $(date).
# Env: CALIB_DIR (dir with the frozen calib_dump.py / el_metrics.py), CALIB_MD5 ("<dump md5> <metrics md5>", checked first),
#      THIN_SMOKES (e.g. "S0 S1 S2 S3 S4"), THIN_ENV (extra env for builder's script, e.g. "S0_STEPS=2000 CLD_ITERS=10 S4_SCUFF=0"),
#      THIN_DEPLOY (expected el_thin reports/thin/DEPLOY), THIN_MD5 (expected md5 of scripts/thin/smoke_thin_b3.sh),
#      THIN_S4ID=1: run the S4 identity pass here (when builder's own S4 still carries a scuff pass on old runs).
set -u
cd /home/noob/work/el_f3
. reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; O=reports/pf2/side; mkdir -p $O; L=$O/side.log; LL=reports/pf2/launch.log
echo "[$(date)] side queue armed (pid $$): waiting for the 10 PF2 R34 runs" >> $L
r34alive(){ local n=0 f; for f in reports/pf2/pids/pf2_SUP*_100pct_s*.pid; do [ -e "$f" ] && kill -0 "$(cat $f)" 2>/dev/null && n=$((n+1)); done; echo $n; }
until [ "$(grep -oE 'trained pf2_(SUP|SUPPF)_100pct_s[5-9] rc=0' $LL | sort -u | wc -l)" -ge 10 ] && [ "$(r34alive)" = 0 ]; do
  grep -qE 'trained pf2_(SUP|SUPPF)_100pct_s[5-9] rc=[1-9]|pf2 NOT scored' $LL && { echo "[$(date)] side: PF2 R34 failure line seen; not starting" >> $L; exit 1; }
  sleep 60; done
echo "[$(date)] side: R34 phase done; starting" >> $L
touch $GG/FAST
# (1) calib B5 dump smoke: val only, f3_SUPPF_100pct_s0 (opening-1 m0 JSON as the self-check reference)
if [ -n "${CALIB_DIR:-}" ]; then
  R=/home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0; M=/home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json
  got="$(md5sum < $CALIB_DIR/calib_dump.py | cut -c1-32) $(md5sum < $CALIB_DIR/el_metrics.py | cut -c1-32)"
  if [ "$got" != "${CALIB_MD5:-}" ]; then echo "[$(date)] calib smoke SKIPPED: md5 '$got' != '${CALIB_MD5:-}'" >> $L; else
    mkdir -p $O/calib/dump $O/calib/rec
    gate_wait 7900 "side calib dump smoke"
    echo "[$(date)] start calib_dump --device cuda val f3_SUPPF_100pct_s0 (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0))" >> $L
    HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8 $P $CALIB_DIR/calib_dump.py --code /home/noob/work/el_f3 --out $O/calib/dump --sets val \
      --device cuda --batch 8 --threads 8 --group f3_SUPPF_100pct_s0 $R > $O/calib/dump.log 2>&1
    rc=$?; echo "[$(date)] calib dump rc=$rc" >> $L
    if [ $rc = 0 ]; then
      OMP_NUM_THREADS=1 nice -n 19 $P $CALIB_DIR/el_metrics.py records --dump $O/calib/dump/f3_SUPPF_100pct_s0.val.npz --set val \
        --code /home/noob/work/el_f3 --out $O/calib/rec/f3_SUPPF_100pct_s0.val.json --m0 $M --m0-set val --tol-profile exact --procs 8 > $O/calib/records.log 2>&1
      rc=$?; echo "[$(date)] calib records + selfcheck rc=$rc: $(head -c 600 $O/calib/rec/f3_SUPPF_100pct_s0.val.json.selfcheck.txt 2>/dev/null | tr '\n' ' ')" >> $L
    fi
    # B5 device, decided mechanically (coach, protocol_PF2 4.1): cuda iff the bf16 dump and records ran rc 0 and the self-check
    # file says tol profile exact + SELFCHECK PASS; else cpu. Written once to post_extra/B5_DEVICE; pf2_b5.sh reads it.
    SC=$O/calib/rec/f3_SUPPF_100pct_s0.val.json.selfcheck.txt
    if [ "$rc" = 0 ] && grep -q "tol profile exact" $SC 2>/dev/null && [ "$(tail -1 $SC)" = "SELFCHECK PASS" ]; then DEV=cuda; else DEV=cpu; fi
    [ -e reports/pf2/post_extra/B5_DEVICE ] && echo "[$(date)] B5_DEVICE already exists ($(cat reports/pf2/post_extra/B5_DEVICE)); not overwritten" >> $L \
      || { echo $DEV > reports/pf2/post_extra/B5_DEVICE; echo "[$(date)] B5_DEVICE = $DEV (rule: dump + records rc 0 and SELFCHECK PASS at tol profile exact -> cuda, else cpu)" >> $L; }
    # RN50 dump peak (memory only; the RN50-PF runs are dumped at the opening): house RN50 Track M m_r3_rn50_s1, val only
    gate_wait 7900 "side calib dump RN50 peak"
    echo "[$(date)] start calib_dump --device cuda val m_r3_rn50_s1 (RN50 peak only)" >> $L
    HF_HUB_OFFLINE=1 OMP_NUM_THREADS=8 $P $CALIB_DIR/calib_dump.py --code /home/noob/work/el_f3 --out $O/calib/dump_rn50 --sets val \
      --device cuda --batch 8 --threads 8 --group m_r3_rn50_s1 /home/noob/work/cv02_noob_el/el_mt/experiments/m_r3_rn50_s1 > $O/calib/dump_rn50.log 2>&1
    rc=$?; echo "[$(date)] calib dump RN50 rc=$rc" >> $L
  fi
fi
# (2) builder's THIN / B3 smokes (el_thin), its own script, our lock and stamp
if [ -n "${THIN_SMOKES:-}" ]; then
  T=/home/noob/work/el_thin
  if [ "$(cat $T/reports/thin/DEPLOY)" != "${THIN_DEPLOY:-}" ] || [ "$(md5sum < $T/scripts/thin/smoke_thin_b3.sh | cut -c1-32)" != "${THIN_MD5:-}" ]; then
    echo "[$(date)] thin smokes SKIPPED: DEPLOY $(cat $T/reports/thin/DEPLOY) / script md5 not as expected" >> $L
  else
    echo "[$(date)] start thin smokes $THIN_SMOKES (DEPLOY $THIN_DEPLOY, env '${THIN_ENV:-}')" >> $L
    (cd $T && env ${THIN_ENV:-} LOCK=$GG/gate.lock STAMP=$GG/last_start bash scripts/thin/smoke_thin_b3.sh $THIN_SMOKES)
    rc=$?; echo "[$(date)] thin smokes script rc=$rc; its log: el_thin/reports/thin/smoke/smoke.log" >> $L
  fi
fi
# (3) S4 identity only (coach 31 Oct: no scuff pass on old runs): builder's m0_audit_b3.py without B3 flags on el_f3
#     f3_SUPPF_100pct_s0 must reproduce the opening-1 m0 JSON exactly (already-opened numbers; nothing new)
if [ "${THIN_S4ID:-0}" = 1 ]; then
  T=/home/noob/work/el_thin; R=/home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0; S4=/home/noob/work/el_f3/reports/pf2/side/thin_S4_m0
  gate_wait 7154 "side thin S4 identity"
  echo "[$(date)] start S4 identity: el_thin m0_audit_b3.py (no B3 flags) on f3_SUPPF_100pct_s0" >> $L
  (cd $T && HF_HUB_OFFLINE=1 $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $S4 --ext /home/noob/work/el_f1/reports/f1/ext117 \
     --no-logits --runs $R > $S4.log 2>&1)
  rc=$?; echo "[$(date)] S4 m0_audit_b3 rc=$rc" >> $L
  $P - $S4/f3_SUPPF_100pct_s0.json /home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json >> $L 2>&1 <<'PY'
import json, sys
a, b = (json.load(open(f)) for f in sys.argv[1:3])
print("S4 identity: m0_audit_b3 cells identical to opening-1 m0_audit.py:", a["cells"] == b["cells"], "| sets", sorted(a["cells"]), "| step", a["step"], b["step"])
PY
fi
rm -f $GG/FAST; echo "[$(date)] side queue done" >> $L
