#!/bin/bash
# runner (3 Nov 2026): unit tests of the queue's new checks (judge b0d866a4 G8; G5 outside-process wait, G6 live startup check,
# prestart HOLD rules) on fake inputs, with s2c_lib.sh's own functions. Scratch Q only ($D/qu); dummies only; no GPU, no training.
#   outside(): FAKEAPPS lists -> flagged only for a non-6206, non-ours PID with > 1024 MiB.
#   prestart(): all OK -> 0; outside -> wait reason, no HOLD; gpumem.pid dead -> HOLD; guard.pid dead -> HOLD; HOLD present -> 'HOLD'.
#   startcheck(): the root line -> OK; the real-root line ('test: 50') -> MISMATCH; no line -> MISMATCH after the wait.
#   live-check failure path: a dummy trainer (launch_run) printing the real-root line -> MISMATCH -> HOLD + stop_verified -> rc=143.
set -u
D=/home/noob/work/runner_s2c_dry; T=${TAG:-}; Q=$D/qu$T; W=$D/wt2$T; L=$Q/launch.log; P=/usr/bin/python3; J=${J:?jobs file}; LIB=$D/scripts/s2c_lib.sh
H=$Q/unit.log; lg(){ echo "$(date '+%F %T') $*" | tee -a $H; }
[ ! -e $Q ] || { echo "$Q exists"; exit 1; }; [ -s $W/scripts/train.py ] || { echo "run s2c_guard_dry.sh first (fake worktree)"; exit 1; }
mkdir -p $Q/pids; cp $J $Q/s2c_jobs.txt; touch $L; . $LIB
DR=/home/noob/work/s2c_root; WANT="Labelled: 478 ($DR/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54"
REAL="Labelled: 478 (data/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 50"
lg "unit start pid $$; lib $(md5sum < $LIB | cut -c1-8)"
sleep 600 & G1=$!; echo $G1 > $Q/gpumem.pid; sleep 600 & G2=$!; echo $G2 > $Q/guard.pid; echo 777001 > $Q/pids/s2c_SKR01_100pct_s10.pid
lg "fake gpumem.pid $G1, guard.pid $G2 (sleep dummies); our recorded trainer pid 777001"
for case in "6206,5876|777001,7020" "6206,5876|777001,7020|99999,1500" "6206,5876|99998,900" "99997,1024" "99996,1025" "6206,9000"; do
  echo "$case" | tr '|' '\n' > $Q/apps.txt; lg "outside() on [$case]: '$(FAKEAPPS=$Q/apps.txt outside)'"; done
echo "6206,5876" > $Q/apps.txt; r=$(FAKEAPPS=$Q/apps.txt prestart); lg "prestart all ok: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
printf '6206,5876\n99999,1500\n' > $Q/apps.txt; r=$(FAKEAPPS=$Q/apps.txt prestart); lg "prestart outside 1500 MiB: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
echo "6206,5876" > $Q/apps.txt; echo 4194001 > $Q/gpumem.pid; r=$(FAKEAPPS=$Q/apps.txt prestart); lg "prestart gpumem.pid dead: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
r=$(FAKEAPPS=$Q/apps.txt prestart); lg "prestart with HOLD present: rc $? '$r'"; rm -f $Q/HOLD; echo $G1 > $Q/gpumem.pid
echo 4194002 > $Q/guard.pid; r=$(FAKEAPPS=$Q/apps.txt prestart); lg "prestart guard.pid dead: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"; rm -f $Q/HOLD; echo $G2 > $Q/guard.pid
printf '2026-11-03 03:00:00 INFO train — %s\nstep 50/20000\n' "$WANT" > $Q/so_ok.txt; printf '2026-11-03 03:00:00 INFO train — %s\n' "$REAL" > $Q/so_real.txt; : > $Q/so_none.txt
for f in so_ok so_real so_none; do r=$(startcheck $Q/$f.txt "$WANT" 4); lg "startcheck $f: rc $? $r"; done
export DUMMY_MODE=normal DUMMY_LINE="2026-11-03 03:00:00 INFO train — $REAL"; launch_run s2c_SUPPF_100pct_s10 $W "$(grep '^s2c_SUPPF_100pct_s10|' $Q/s2c_jobs.txt | cut -d'|' -f4)"; unset DUMMY_MODE DUMMY_LINE; pp=$LPID
lg "live-check dummy s2c_SUPPF_100pct_s10 pid $pp (prints the real-root line): $(psl $pp)"
m=$(startcheck $W/experiments/s2c_SUPPF_100pct_s10.stdout "$WANT" 20); rc=$?; lg "s2c_SUPPF_100pct_s10 $m (rc $rc)"
if [ $rc != 0 ]; then lg "live check FAILED: HOLD + stop by verified PID"; touch $Q/HOLD; stop_verified s2c_SUPPF_100pct_s10 $pp; lg "stop rc $?"; fi
sleep 2; lg "HOLD $([ -e $Q/HOLD ] && echo present || echo absent); launch.log: $(tr '\n' '|' < $L)"
kill -TERM $G1 $G2; wait 2>/dev/null; for p in $G1 $G2 $pp; do [ -d /proc/$p ] && lg "LEFT ALIVE $p" || lg "pid $p gone"; done; lg "unit end"
