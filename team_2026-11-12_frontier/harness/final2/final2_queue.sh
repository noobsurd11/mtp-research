#!/bin/bash
# fin2 queue on cv02 (incident of 21 Nov 2026; LAUNCH_REQUEST_fin2.md; run by the LEAD on gaint after the review, the deploy
# of F2 and the checks). Built from harness/final/final_queue.sh (e574e25f): one NEW queue `fin2` of 10 lines
# (final2_make_jobs.py): the 10 full-pool runs of fin, each RESUMED under F2 from its step-18000 checkpoints/latest.pth.
# Armed only if every other live queue cannot start training (fin ended or all dispatched): never two cv02 queues that can
# start training. Lane rule v2 unchanged: SHARE_TRAIN 20480 (the user's floor), no SHARE_DUMP file (fin2 has no dump line;
# the lead's (a1) ruling), LPG 1 (one process of ours per GPU), MAXC 8, GAPSEC 30. B = QC = F2B = the deploy of F2 (resumed
# runs, queue code, cv02 card variants all from F2B; its CODE.md5 equals bench_821dfad's except the 6 paths of F -> F2).
# One step per call, in this order. Each step refuses rather than guess, and prints what it did.
#   build       gaint + cv02 READ ONLY: IO/jobs.txt from final2_make_jobs.py; no fin2 queue dir and no resume target yet.
#   resumecopy  cv02 WRITE (only new dirs F2B/experiments/<name>): for each of the 10 runs, only when fin has ended it
#               ('trained <name> rc=' in fin's launch.log and fin/pids/<name>.end): FB/experiments/<name> must hold
#               config_used.yaml and checkpoints/latest.pth with step 18000 (read by torch on cv02 CPU); cp -a of the run
#               dir (not its .stdout) to F2B/experiments/<name>; md5 of latest.pth equal on both sides; IO/resumecopy.tsv
#               records name, step, md5. The originals in FB stay untouched (the fallback).
#   render      cv02 WRITE (a new scratch queue dir only): render-only run of F2B's cq.sh on IO/jobs.txt (stops at the logger
#               check; nothing starts); final2_rendercmp.py must print 'render compare: 0 FAIL'.
#   place       cv02 WRITE: queue dir /tmp/noob_el/bench_q/fin2 with jobs.txt (read-only), LPG 1, MAXC 8, SHARE_TRAIN 20480
#               (no SHARE_DUMP file). Not armed.
#   guard       cv02 WRITE + START: disk guard 6 (diskguard6.sh; tmux bench_diskguard6; HOLD in fin2 below 20 GB free).
#   arm         cv02 START: F2B's cq_setup.sh (session bench_q_fin2, GAPSEC 30) after the pre-checks below. Reports "armed"
#               only when the line 'cv02 q armed:' is in fin2's launch.log (waits up to ARMWAIT s, default 300).
#   status      cv02 READ ONLY.
# DRY=1: every cv02 write or start is printed, not run; the read-only checks run.
# Env: F2 (full commit), F2B (/tmp/noob_el/bench_<F2 7 hex>), IO (/home/noob/work/bench_fin2_io), GAPSEC (default 30), MAXC
#   (default 8), DISK_OK=1 (arm below the disk estimate; disk guard 6 then HOLDs fin2 at 20 GB free).
set -u
STEP=${1:?step: build | resumecopy | render | place | guard | arm | status}
NEWQ=fin2; IO=${IO:-/home/noob/work/bench_fin2_io}; DRY=${DRY:-0}; F2=${F2:-}; F2B=${F2B:-}; GAPSEC=${GAPSEC:-30}; MAXC=${MAXC:-8}
ST=20480       # the user's floor (MiB) for SHARE_TRAIN; not to be lowered
BQ=/tmp/noob_el/bench_q; FB=/tmp/noob_el/bench_821dfad; QF=$BQ/fin; Q=$BQ/$NEWQ
DF=/tmp/noob_el/bench_data_fin; DFR=$DF/roots/pool532_v11
DATA_MD5=d6063fd83d20e656612540edda702cbe; FC2=9967d59abaab03cef83c1e3014840b2359ef45d7; TREE2=adcdf7ec59ff30e7a714808ca94dd46e4a63628f
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; PC=/tmp/noob_el/el-fault-detection/.venv/bin/python
NAMES="fin_hrnet_swad_v11_pool_s5 fin_hrnet_swad_v11_pool_s6 fin_hrnet_swad_v11_pool_s7 fin_hrnet_swad_v11_pool_s8 fin_hrnet_swad_v11_pool_s9 fin_pf_v11_pool_s5 fin_pf_v11_pool_s6 fin_pf_v11_pool_s7 fin_pf_v11_pool_s8 fin_pf_v11_pool_s9"
PINS="08d0c30884f07848e20aaecae2127d86  bench/q/cv02/cq.sh
9684c116ea35e8748fe861d15fdda8a7  bench/q/cv02/cq_setup.sh
6dc3a22ae3f419df077d4b511f971dda  scripts/train.py
7fe1004f5d2f0c6aa57c4945377c694d  src/trainers/weight_avg.py
204f9bce070e695df63de779becce287  bench/q/cv02/cq_rescue.sh
20712dd3af1e6b86720a9633b419de00  bench/q/cv02/slim_ckpt.py
f3affc80b21406644cedbc80d6e250ba  bench/q/cv02/cvcard.py
2a5f688160eb100eb0bc9784ffe06e7e  bench/q/cv02/cq_gpumem.sh
1af2ed69babf72e9d0d0aa789eb71121  bench/q/bench_lib.sh
32e0b67c2ad8073c33440b8347d77f57  scripts/bench_infer.py
a479fdff1dc667b26d18ee05fac9f6eb  scripts/bench_make_pool_root.py
98f152de3ea7f8c88e892162e07b4450  bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
d7b207089f6cfeb484ca9ef96f734786  bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
a4a46a526cf14d649f3176edd53a9c32  bench/methods/house_r34_unetpp_pf_v11.yaml
bbdef88b2a5e6dde5e01ffaf23ba0d2b  bench/methods_cv02/house_r34_unetpp_pf_v11.yaml"
DW="<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <scripts/train.py <src/trainers/weight_avg.py >bench/q/cv02/cq.sh >bench/q/cv02/cq_setup.sh >scripts/train.py >src/trainers/weight_avg.py >tests/test_bench_cq_resume.py >tests/test_bench_pool_eval.py "
ROOTPINS="d374fd843598f10fd4ba9101435986c8  splits/train.txt
79816ba63cca96e10265197eb4cfa905  splits/test.txt
cec1396e24b35c8bb0001de19f7d0c3b  SPLITS.md5
33e65b3f5ec964336d44583dcdfe6352  DATA_MANIFEST.md5"
GUARD_MD5=$(md5sum < $HERE/diskguard6.sh | cut -c1-32)
C=cv02@10.8.1.106
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }                       # read only
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
say(){ echo "[$(date '+%F %T')] $STEP: $*" | tee -a $IO/queue.log; }
mkdir -p $IO || exit 1
need_f(){ [ "$F2" = $FC2 ] || no "F2 must be the full commit $FC2"
  [ "$F2B" = "/tmp/noob_el/bench_${F2:0:7}" ] || no "F2B must be /tmp/noob_el/bench_${F2:0:7} (the deploy of F2 by c3_deploy.sh)"
  [ "$(git -C /home/noob/work/bench_wt_fin2 rev-parse $F2^{tree} 2>/dev/null)" = $TREE2 ] || no "F2 does not have the pinned tree"; }
qscan(){ R "for q in $BQ/*/; do n=\$(basename \$q); [ \$n = $NEWQ ] && continue; p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; [ \"\$(cat \$q/MAXC 2>/dev/null)\" = 0 ] && { echo \"ok \$n MAXC 0\"; continue; }; grep -q 'cv02 q: all jobs dispatched' \$q/launch.log && { echo \"ok \$n all dispatched\"; continue; }; [ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && { echo \"ok \$n fixture only, cannot train\"; continue; }; echo \"CAN_START \$n\"; done; true"; }
fb_check(){   # F2B: REVISION, CODE.md5, pins, and its CODE.md5 against bench_821dfad's (F): only the 6 paths of F -> F2 may differ
  local out d; out=$(R "cd $F2B && echo \"rev \$(cat REVISION)\"; md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"$PINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo PINS_OK; (cd $FB && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && echo FB_OK; diff <(grep -v '  REVISION\$' $FB/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || no "ssh failed"
  case "$out" in "rev $F2"*) ;; *) no "F2B REVISION is not F2";; esac
  case "$out" in *CODE_OK*) ;; *) no "F2B CODE.md5 check failed";; esac
  case "$out" in *PINS_OK*) ;; *) no "F2B files do not match the pinned md5s";; esac
  case "$out" in *FB_OK*) ;; *) no "bench_821dfad (F) CODE.md5 check failed";; esac
  d=$(echo "$out" | tail -1); [ "$d" = "$DW" ] || no "F2B differs from bench_821dfad in other paths than the 6 of F -> F2: $d"
  echo "F2B $F2B: REVISION F2, CODE.md5 OK, pins OK; differs from bench_821dfad (F) only in the 6 paths of F -> F2 (+ REVISION)"; }
root_check(){ local o; o=$(R "cd $DFR 2>/dev/null && echo \"$ROOTPINS\" | md5sum -c --quiet - > /dev/null 2>&1 && (cd $DF/roots && md5sum -c --quiet ROOTS_pool532_v11.md5 > /dev/null 2>&1) && echo ROOT_OK") || no "ssh failed"
  [ "$o" = ROOT_OK ] || no "$DFR: pins or ROOTS_pool532_v11.md5 check failed"; echo "root $DFR: pins and ROOTS_pool532_v11.md5 OK"; }
copy_check(){ local o; [ -s $IO/resumecopy.tsv ] || no "no $IO/resumecopy.tsv (run 'resumecopy')"
  o=$(ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "cd $F2B/experiments 2>/dev/null || exit 0; while read n st m; do [ \"\$(md5sum < \$n/checkpoints/latest.pth | cut -c1-32)\" = \"\$m\" ] && [ -s \$n/config_used.yaml ] && [ ! -e \$n.stdout ] && echo OK \$n; done" < $IO/resumecopy.tsv | grep -c '^OK ')   # stdin = the tsv (no ssh -n)
  [ "$o" = 10 ] || no "only $o of 10 copied run dirs in F2B match resumecopy.tsv (latest.pth md5, config_used.yaml, no .stdout)"
  echo "10 copied run dirs in F2B: latest.pth md5 as recorded, config_used.yaml present, not started"; }

case $STEP in
build)
  [ -e $IO/jobs.txt ] && no "$IO/jobs.txt exists (use a new IO)"
  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $HERE/final2_make_jobs.py $IO/jobs.txt | tee $IO/build.out
  [ -s $IO/jobs.txt ] || no "job builder failed"
  R "test ! -e $Q && echo FREE" | grep -qx FREE || { rm -f $IO/jobs.txt; no "$Q exists on cv02"; }
  md5sum < $IO/jobs.txt | cut -c1-32 > $IO/jobs.md5
  say "built $IO/jobs.txt: $(wc -l < $IO/jobs.txt) lines, md5 $(cat $IO/jobs.md5)";;
resumecopy)
  need_f; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; [ -e $IO/resumecopy.tsv ] && no "$IO/resumecopy.tsv exists"
  fb_check
  o=$(R "for n in $NAMES; do grep -q \"trained \$n rc=\" $QF/launch.log && [ -e $QF/pids/\$n.end ] && echo ENDED \$n; done" | grep -c '^ENDED ') || no "ssh failed"
  [ "$o" = 10 ] || no "only $o of the 10 fin trainings have ended ('trained <name> rc=' and pids/<name>.end in fin): wait"
  o=$(R "for n in $NAMES; do [ -e $F2B/experiments/\$n ] && echo EXISTS \$n; [ -s $FB/experiments/\$n/config_used.yaml ] && [ -s $FB/experiments/\$n/checkpoints/latest.pth ] || echo MISSING \$n; done; true") || no "ssh failed"
  [ -z "$o" ] || no "$(echo "$o" | head -3 | tr '\n' ' ')"
  S=$(R "cd $FB/experiments && for n in $NAMES; do echo \"\$n \$(CUDA_VISIBLE_DEVICES= nice -n 19 $PC -c 'import sys, torch; print(int(torch.load(sys.argv[1], map_location=\"cpu\", weights_only=False)[\"step\"]))' \$n/checkpoints/latest.pth) \$(md5sum < \$n/checkpoints/latest.pth | cut -c1-32)\"; done") || no "ssh failed"
  echo "$S"; [ "$(echo "$S" | awk '$2 == 18000' | wc -l)" = 10 ] || no "not every source latest.pth is at step 18000 (see above)"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir -p $F2B/experiments; for each name: cp -a $FB/experiments/<name> $F2B/experiments/<name>; md5 of latest.pth on both sides"; exit 0; fi
  R "mkdir -p $F2B/experiments && cd $FB/experiments && for n in $NAMES; do test ! -e $F2B/experiments/\$n && cp -a \$n $F2B/experiments/\$n || exit 1; done && echo COPIED" | grep -qx COPIED || no "copy failed (look at $F2B/experiments)"
  echo "$S" > $IO/resumecopy.tsv
  copy_check
  say "copied the 10 run dirs (step 18000) from $FB to $F2B; md5s in $IO/resumecopy.tsv; originals untouched";;
render)
  need_f; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"
  fb_check; root_check; copy_check
  W=/tmp/noob_el/bench_fin2_render/$(date +%Y%m%d_%H%M%S); J=$(cat $IO/jobs.md5)
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $W/q, jobs.txt (md5 $J), LPG 1; B=$F2B Q=$W/q JOBS_MD5=$J DEPLOY=$F2 DATA_MD5=$DATA_MD5 nice -n 19 bash $F2B/bench/q/cv02/cq.sh"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir -p $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && md5sum < $W/q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/render_md5.txt || no "placing the scratch list failed"
  [ "$(cat $IO/render_md5.txt)" = "$J" ] || no "scratch jobs.txt md5 differs"
  R "B=$F2B Q=$W/q JOBS_MD5=$J DEPLOY=$F2 DATA_MD5=$DATA_MD5 nice -n 19 bash $F2B/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $IO/render.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $IO/render.out || no "render did not reach the logger check (see $IO/render.out)"
  R "cat $W/q/jobs_rendered.txt" > $IO/rendered.txt || no "ssh failed"
  PYTHONDONTWRITEBYTECODE=1 $P $HERE/final2_rendercmp.py --jobs $IO/jobs.txt --rendered $IO/rendered.txt | tee $IO/render_cmp.out
  [ ${PIPESTATUS[0]} = 0 ] || no "rendered lines do not match (see $IO/render_cmp.out)"
  say "render OK in cv02 $W: 10 resume lines, templates and semantics 0 FAIL";;
place)
  [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  case "$MAXC" in ''|*[!0-9]*) no "MAXC must be a whole number";; esac
  R "test ! -e $Q && echo FREE" | grep -qx FREE || no "$Q exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $Q; jobs.txt (md5 $J, r--r--r--); LPG 1; MAXC $MAXC; SHARE_TRAIN $ST; no SHARE_DUMP"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && echo 1 > $Q/LPG && echo $MAXC > $Q/MAXC && echo $ST > $Q/SHARE_TRAIN && md5sum < $Q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/place_md5.txt || no "placing failed"
  [ "$(cat $IO/place_md5.txt)" = "$J" ] || no "placed jobs.txt md5 differs"
  say "placed $Q: jobs.txt md5 $J, LPG 1, MAXC $MAXC, SHARE_TRAIN $ST, no SHARE_DUMP (not armed)";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard6' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard6.sh && md5sum < $BQ/diskguard6.sh | cut -c1-32")
  case "$s" in *RUNNING*) no "tmux bench_diskguard6 already runs on cv02";; esac
  [ -z "$s" ] || [ "$s" = "$GUARD_MD5" ] || no "cv02 $BQ/diskguard6.sh exists with another md5 ($s)"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: place $BQ/diskguard6.sh (md5 $GUARD_MD5), tmux new-session -d -s bench_diskguard6 'bash $BQ/diskguard6.sh'"; exit 0; fi
  if [ -z "$s" ]; then ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $BQ/diskguard6.sh && cat > $BQ/diskguard6.sh" < $HERE/diskguard6.sh || no "placing diskguard6.sh failed"; fi
  [ "$(R "md5sum < $BQ/diskguard6.sh | cut -c1-32")" = "$GUARD_MD5" ] || no "cv02 diskguard6.sh md5 differs"
  Wr "tmux new-session -d -s bench_diskguard6 'bash $BQ/diskguard6.sh' && sleep 2 && tail -1 $BQ/diskguard6.log"
  say "disk guard 6 started (covers fin2; stop file $BQ/DISKGUARD6_STOP)";;
arm)
  need_f; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  case "$GAPSEC" in ''|*[!0-9]*) no "GAPSEC must be a whole number";; esac; [ "$GAPSEC" -ge 30 ] || no "GAPSEC below 30"
  [ -s $IO/render_cmp.out ] && grep -q "render compare: 0 FAIL" $IO/render_cmp.out || no "no passed 'render' in $IO"
  o=$(qscan) || no "ssh failed"
  echo "$o"; case "$o" in *CAN_START*) no "another queue can still start training";; esac
  o=$(R "cd $Q && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) LPG \$(cat LPG) MAXC \$(cat MAXC) share \$(cat SHARE_TRAIN 2>/dev/null)/\$(cat SHARE_DUMP 2>/dev/null) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_$NEWQ' 2>/dev/null && echo yes || echo no) data \$(md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32)\"") || no "ssh failed"
  [ "$o" = "jobs $J LPG 1 MAXC $MAXC share $ST/ used 0 ses no data $DATA_MD5" ] || no "queue dir or data check: $o"
  echo "queue dir $Q: jobs md5, LPG 1, MAXC $MAXC, SHARE_TRAIN $ST, no SHARE_DUMP, unused; data $DATA_MD5"
  fb_check; root_check; copy_check
  o=$(R "a=\$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); echo \"free \$a guard \$(tmux has-session -t '=bench_diskguard6' 2>/dev/null && echo yes || echo no) \$(md5sum < $BQ/diskguard6.sh 2>/dev/null | cut -c1-32) hold \$(test -e $Q/HOLD && echo 1 || echo 0)\"") || no "ssh failed"
  set -- $o; echo "cv02: $o"
  [ "${4:-}" = yes ] && [ "${5:-}" = "$GUARD_MD5" ] || no "disk guard 6 is not running with the reviewed script (run 'guard')"
  [ "${7:-}" = 0 ] || no "$Q/HOLD exists"
  need=26
  echo "disk need (S): the 10 resumed runs grow from their copied step-18000 state (3.6 GB, already on disk) to about 5 x 1.0 + 5 x 0.62 GB (latest with the six readouts, best, slim) = +4.5 GB, plus the 20 GB guard floor = about $need GB; free ${2:-?} GB"
  if [ "${2:-0}" -lt "$need" ] 2>/dev/null; then
    [ "${DISK_OK:-0}" = 1 ] || no "cv02 /tmp free ${2:-?} GB < $need GB"
    echo "DISK_OK=1: arming with ${2:-?} GB free < $need GB; disk guard 6 will HOLD fin2 at 20 GB free"
  fi
  A="B=$F2B Q=$Q SES=bench_q_$NEWQ DEPLOY=$F2 JOBS_MD5=$J DATA_MD5=$DATA_MD5 GAPSEC=$GAPSEC bash $F2B/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, pre-checks passed; not run on cv02: $A"; exit 0; fi
  R "$A" | tee $IO/arm.out
  grep -q "cq_setup: bench_q_$NEWQ armed: gpumem [0-9]* queue [0-9]*" $IO/arm.out || no "arming not confirmed (see $IO/arm.out)"
  t=0; a=""
  while [ $t -lt ${ARMWAIT:-300} ]; do a=$(R "grep -m1 -E 'cv02 q armed:|; not starting' $Q/launch.log" 2>/dev/null); [ -n "$a" ] && break; sleep 10; t=$((t+10)); done
  echo "$a" | cut -c1-400
  case "$a" in *"cv02 q armed:"*) ;;
    *"; not starting"*) no "cq.sh did NOT arm: '${a#*] }'. Nothing of fin2 runs; see $Q/launch.log";;
    *) no "no 'cv02 q armed:' line in $Q/launch.log after $t s: arming is NOT confirmed";; esac
  echo "$a" | grep -q "SHARE_TRAIN $ST MiB, SHARE_DUMP 0 MiB" || echo "WARNING: the armed line does not show SHARE_TRAIN $ST and SHARE_DUMP 0"
  echo "$a" | grep -q "gap $GAPSEC s" || echo "WARNING: the armed line does not show gap $GAPSEC s"
  say "armed bench_q_$NEWQ ($Q; jobs $J; B = QC = $F2B). Owed at the first start: 'fin_hrnet_swad_v11_pool_s5 config OK (= card)', 'startup line OK: Labelled: 532 ...', and in its stdout 'RESUMED from ... at step 18000/20000'; relay: F2B=$F2B bash $HERE/final2_relay.sh";;
status)
  R "echo \"cv02 \$(date -u '+%F %T') UTC; free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD in fin2: \$(test -e $Q/HOLD && echo yes || echo no); SHARE_DUMP in fin2: \$(test -e $Q/SHARE_DUMP && echo PRESENT || echo absent)\"; d=$Q; [ -d \$d ] || { echo \"$NEWQ: no dir\"; exit 0; }; echo \"$NEWQ: MAXC \$(cat \$d/MAXC 2>/dev/null) started \$(ls \$d/pids/*.gpu 2>/dev/null | wc -l) ended \$(ls \$d/pids/*.end 2>/dev/null | wc -l) of \$(grep -c . \$d/jobs.txt) trained-rc0 \$(grep -c 'trained fin_.* rc=0 ' \$d/launch.log 2>/dev/null) RUN.md5 \$(ls $F2B/runs/*/RUN.md5 2>/dev/null | wc -l) RESUMED \$(grep -l 'RESUMED from' $F2B/experiments/fin_*.stdout 2>/dev/null | wc -l)\"; for f in \$d/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$d/pids/\$n.end ] || echo \"  open: \$n GPU \$(cat \$f) rc \$(cat \$d/pids/\$n.rc 2>/dev/null || echo running)\"; done; grep -E 'FAIL|HOLD|not starting|Traceback lines [1-9]|rc=[1-9]' \$d/launch.log 2>/dev/null | tail -3; true";;
*) no "unknown step";;
esac
