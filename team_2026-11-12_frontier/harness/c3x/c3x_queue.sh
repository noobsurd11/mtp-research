#!/bin/bash
# c3x queue on cv02 (rulings C1, C3, C4; run by the LEAD on gaint, after the review, the commit, the smokes and the deploy).
# Built from harness/c3lane/c3lane_handover.sh (36450f6e) without freeze and carry: c3x is a NEW queue of 25 lines that does
# not take over another queue's jobs. It is armed only when c3all3 has dispatched ALL its jobs (its launch.log holds
# 'cv02 q: all jobs dispatched'), and only if every other live queue has MAXC 0, has dispatched everything, or holds only
# --fixture jobs: never two queues that can start training. Lane rule v2: SHARE_TRAIN 20480 and SHARE_DUMP 10240 (the user's
# floors), MAXC 8, LPG 1. B = QC = XB, the deploy of the c3x commit X (training, dumps, runs, queue code and cv02 card variants
# all from XB; its code equals bench_89b9ea5 except the 9 paths of c3x_codeproof.sh, checked here on cv02 itself).
# One step per call, in this order. Each step refuses rather than guess, and prints what it did.
#   build    gaint + cv02 READ ONLY: IO/jobs.txt from c3x_make_jobs.py --gate GATE; no name of it exists on cv02 (any
#            deploy's experiments or runs, any queue's pids) or in a gaint relay dir. GATE has no default (review N2): it must
#            equal the job gate of the RULE line in the smoke check's output file SMOKE_CHECK (default
#            /home/noob/work/bq/c3x_smoke/smoke_check.out, written by `c3x_smoke.sh check`), else build refuses.
#   render   cv02 WRITE (a new scratch queue dir only; cq.sh also makes the empty dirs experiments/ runs/ dumps/ in XB, as at
#            arming): render-only run of XB's cq.sh on IO/jobs.txt (it stops at the logger check; nothing starts, no GPU is
#            read); the 75 rendered lines are compared with c3all3's own jobs_rendered.txt (c3x_rendercmp.py).
#   place    cv02 WRITE: queue dir /tmp/noob_el/bench_q/c3x with jobs.txt (read-only), LPG 1, MAXC 8, SHARE_TRAIN 20480,
#            SHARE_DUMP 10240. Not armed.
#   guard    cv02 WRITE + START: disk guard 4 (diskguard4.sh; tmux bench_diskguard4; HOLD in c3x below 20 GB free).
#   arm      cv02 START: XB's cq_setup.sh (session bench_q_c3x) after the pre-checks below. Reports "armed" only when the line
#            'cv02 q armed:' is in c3x's launch.log (waits up to ARMWAIT s, default 300).
#   status   cv02 READ ONLY.
# DRY=1: every cv02 write or start is printed, not run; the read-only checks run.
# Env: X (full c3x commit), XB (/tmp/noob_el/bench_<X 7 hex>; render, guard, arm), GATE (build; required, = the RULE line of
#   SMOKE_CHECK), SMOKE_CHECK, IO (/home/noob/work/bench_c3_io/c3x), DISK_OK=1 (arm: the lead accepts arming with less free
#   space than the estimate; disk guard 4 then HOLDs c3x at 20 GB free until space is freed: no new training start and no
#   dump start, so finished c3x runs also wait undumped and unrelayed).
set -u
STEP=${1:?step: build | render | place | guard | arm | status}
NEWQ=c3x; IO=${IO:-/home/noob/work/bench_c3_io/c3x}; DRY=${DRY:-0}; GATE=${GATE:-}; X=${X:-}; XB=${XB:-}
SMOKE_CHECK=${SMOKE_CHECK:-/home/noob/work/bq/c3x_smoke/smoke_check.out}
ST=20480; SD=10240     # the user's floors (MiB) for SHARE_TRAIN and SHARE_DUMP; not to be lowered
BQ=/tmp/noob_el/bench_q; B89=/tmp/noob_el/bench_89b9ea5; Q=$BQ/$NEWQ
DATA_MD5=d6063fd83d20e656612540edda702cbe; BASE=852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python
# md5 pins in XB: queue code of 852ed5c (as QC bench_852ed5c of c3all3), the c3x card and its cv02 variant, the HRNet card
PINS="14d33b80b17b116ec68941f1b40c5951  bench/q/cv02/cq.sh
204f9bce070e695df63de779becce287  bench/q/cv02/cq_rescue.sh
630b1307a5b3cc99da251cd6eecc8672  bench/q/cv02/cq_setup.sh
20712dd3af1e6b86720a9633b419de00  bench/q/cv02/slim_ckpt.py
f3affc80b21406644cedbc80d6e250ba  bench/q/cv02/cvcard.py
2a5f688160eb100eb0bc9784ffe06e7e  bench/q/cv02/cq_gpumem.sh
1af2ed69babf72e9d0d0aa789eb71121  bench/q/bench_lib.sh
98f152de3ea7f8c88e892162e07b4450  bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
d7b207089f6cfeb484ca9ef96f734786  bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
c89314d8a707aa62f2db4edabc042dcb  bench/methods/hrnet_w18_unetpp_pf_v11.yaml"
DW="<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/q/cv02/slim_ckpt.py >bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/swad_const_pf_v11.yaml >bench/q/cv02/cq.sh >bench/q/cv02/cq_rescue.sh >bench/q/cv02/cq_setup.sh >bench/q/cv02/slim_ckpt.py >tests/test_bench_c3x_card.py >tests/test_bench_cq_readouts.py "
GUARD_MD5=$(md5sum < $HERE/diskguard4.sh | cut -c1-32)
C=cv02@10.8.1.106
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }                       # read only
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
say(){ echo "[$(date '+%F %T')] $STEP: $*" | tee -a $IO/queue.log; }
mkdir -p $IO || exit 1
need_x(){ echo "$X" | grep -qE '^[0-9a-f]{40}$' || no "X must be the full c3x commit"
  [ "$XB" = "/tmp/noob_el/bench_${X:0:7}" ] || no "XB must be /tmp/noob_el/bench_${X:0:7} (the deploy of X by c3_deploy.sh)"
  [ "$(git -C /home/noob/work/bench_wt_c3s rev-parse $X^ 2>/dev/null)" = $BASE ] || no "X is not a commit on 852ed5c"; }
# qscan: one line per live queue on cv02 other than c3x: "ok <name> <why>" if it cannot start a training run (MAXC 0, all jobs
#   dispatched, or only --fixture jobs), else "CAN_START <name>" (= c3lane_handover.sh's qscan with NEWQ c3x).
qscan(){ R "for q in $BQ/*/; do n=\$(basename \$q); [ \$n = $NEWQ ] && continue; p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; [ \"\$(cat \$q/MAXC 2>/dev/null)\" = 0 ] && { echo \"ok \$n MAXC 0\"; continue; }; grep -q 'cv02 q: all jobs dispatched' \$q/launch.log && { echo \"ok \$n all dispatched\"; continue; }; [ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && { echo \"ok \$n fixture only, cannot train\"; continue; }; echo \"CAN_START \$n\"; done; true"; }
xb_check(){   # XB: REVISION, CODE.md5, pins, and its CODE.md5 against bench_89b9ea5's: only the 9 paths of the proof may differ
  local out d; out=$(R "cd $XB && echo \"rev \$(cat REVISION)\"; md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"$PINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo PINS_OK; (cd $B89 && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && echo B89_OK; diff <(grep -v '  REVISION\$' $B89/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || no "ssh failed"
  case "$out" in "rev $X"*) ;; *) no "XB REVISION is not X";; esac
  case "$out" in *CODE_OK*) ;; *) no "XB CODE.md5 check failed";; esac
  case "$out" in *PINS_OK*) ;; *) no "XB files do not match the pinned md5s";; esac
  case "$out" in *B89_OK*) ;; *) no "bench_89b9ea5 CODE.md5 check failed";; esac
  d=$(echo "$out" | tail -1); [ "$d" = "$DW" ] || no "XB differs from bench_89b9ea5 in other paths than the 9 of the code proof: $d"
  echo "XB $XB: REVISION X, CODE.md5 OK, pins OK; differs from bench_89b9ea5 only in the 9 paths of the code proof (+ REVISION)"; }

case $STEP in
build)
  [ -e $IO/jobs.txt ] && no "$IO/jobs.txt exists (use a new IO for a new list)"
  case "$GATE" in ''|*[!0-9]*) no "GATE must be given explicitly as a whole number (the job gate of the RULE line in $SMOKE_CHECK)";; esac
  [ -s "$SMOKE_CHECK" ] || no "no smoke check output $SMOKE_CHECK (run 'c3x_smoke.sh check' after the smokes)"
  sg=$(grep -E $'^RULE\tgate\t' "$SMOKE_CHECK" | tail -1 | sed -nE 's/.*job gate = max\(11000, P \+ 2,048\) = ([0-9]+) MiB.*/\1/p')
  [ -n "$sg" ] || no "no RULE gate line in $SMOKE_CHECK"
  [ "$GATE" = "$sg" ] || no "GATE $GATE differs from the job gate $sg of the smoke check ($SMOKE_CHECK)"
  echo "GATE $GATE = the job gate of the smoke check's RULE line ($SMOKE_CHECK; its last line: $(tail -1 "$SMOKE_CHECK"))"
  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $HERE/c3x_make_jobs.py $IO/jobs.txt --gate $GATE | tee $IO/build.out
  [ -s $IO/jobs.txt ] || no "job builder failed"
  cut -d'|' -f1 $IO/jobs.txt > $IO/names.txt
  hit=$(R "for n in $(tr '\n' ' ' < $IO/names.txt); do for b in /tmp/noob_el/bench_*/; do [ -e \$b/experiments/\$n ] || [ -e \$b/experiments/\$n.stdout ] || [ -e \$b/runs/\$n ] && echo \"\$n in \$b\"; done; ls $BQ/*/pids/\$n.gpu 2>/dev/null; done; true") || no "ssh failed"
  [ -z "$hit" ] || { rm -f $IO/jobs.txt; no "names already used on cv02: $(echo "$hit" | head -3 | tr '\n' ' ')"; }
  for n in $(cat $IO/names.txt); do ls -d /home/noob/work/bench_relay/*/$n /home/noob/work/bench_relay/*/.ok/$n 2>/dev/null; done > $IO/relay_hits.txt
  [ ! -s $IO/relay_hits.txt ] || { rm -f $IO/jobs.txt; no "names already in a gaint relay dir: $(head -3 $IO/relay_hits.txt | tr '\n' ' ')"; }
  md5sum < $IO/jobs.txt | cut -c1-32 > $IO/jobs.md5
  say "built $IO/jobs.txt: $(wc -l < $IO/jobs.txt) lines, md5 $(cat $IO/jobs.md5), gate $GATE; no name in use on cv02 or in a gaint relay";;
render)
  need_x; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt (run 'build')"
  xb_check
  W=/tmp/noob_el/bench_c3x_render/$(date +%Y%m%d_%H%M%S); J=$(cat $IO/jobs.md5)
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $W/q, place jobs.txt (md5 $J) and LPG 1 there, B=$XB Q=$W/q JOBS_MD5=$J DEPLOY=$X DATA_MD5=$DATA_MD5 nice -n 19 bash $XB/bench/q/cv02/cq.sh"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir -p $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && md5sum < $W/q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/render_md5.txt || no "placing the scratch list failed"
  [ "$(cat $IO/render_md5.txt)" = "$J" ] || no "scratch jobs.txt md5 differs"
  R "B=$XB Q=$W/q JOBS_MD5=$J DEPLOY=$X DATA_MD5=$DATA_MD5 nice -n 19 bash $XB/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $IO/render.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $IO/render.out || no "render did not reach the logger check (see $IO/render.out)"
  R "cat $W/q/jobs_rendered.txt" > $IO/rendered.txt || no "ssh failed"
  R "cat $BQ/c3all3/jobs_rendered.txt" > $IO/c3all3_rendered.txt || no "ssh failed"
  PYTHONDONTWRITEBYTECODE=1 $P $HERE/c3x_rendercmp.py --rendered $IO/rendered.txt --c3all3 $IO/c3all3_rendered.txt --xb $XB | tee $IO/render_cmp.out
  [ ${PIPESTATUS[0]} = 0 ] || no "rendered lines do not match (see $IO/render_cmp.out)"
  say "render OK in cv02 $W: 75 lines; train lines = c3all3's HRNet lines + the 8 opts; dump lines = c3all3's swad dump lines in XB. First job:"
  grep -E '^(dump_)?c3x_hrnet_swad_v11_f0_s5(\.swad)?\|' $IO/rendered.txt | cut -c1-250;;
place)
  [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  R "test ! -e $Q && echo FREE" | grep -qx FREE || no "$Q exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $Q; jobs.txt (md5 $J, $(wc -l < $IO/jobs.txt) lines, r--r--r--); LPG 1; MAXC 8; SHARE_TRAIN $ST; SHARE_DUMP $SD"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && echo 1 > $Q/LPG && echo 8 > $Q/MAXC && echo $ST > $Q/SHARE_TRAIN && echo $SD > $Q/SHARE_DUMP && md5sum < $Q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/place_md5.txt || no "placing failed"
  [ "$(cat $IO/place_md5.txt)" = "$J" ] || no "placed jobs.txt md5 differs"
  say "placed $Q: jobs.txt md5 $J, LPG 1, MAXC 8, SHARE_TRAIN $ST, SHARE_DUMP $SD (not armed)";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard4' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard4.sh && md5sum < $BQ/diskguard4.sh | cut -c1-32")
  case "$s" in *RUNNING*) no "tmux bench_diskguard4 already runs on cv02";; esac
  [ -z "$s" ] || [ "$s" = "$GUARD_MD5" ] || no "cv02 $BQ/diskguard4.sh exists with another md5 ($s)"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: place $BQ/diskguard4.sh (md5 $GUARD_MD5), tmux new-session -d -s bench_diskguard4 'bash $BQ/diskguard4.sh'"; exit 0; fi
  if [ -z "$s" ]; then ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $BQ/diskguard4.sh && cat > $BQ/diskguard4.sh" < $HERE/diskguard4.sh || no "placing diskguard4.sh failed"; fi
  [ "$(R "md5sum < $BQ/diskguard4.sh | cut -c1-32")" = "$GUARD_MD5" ] || no "cv02 diskguard4.sh md5 differs"
  Wr "tmux new-session -d -s bench_diskguard4 'bash $BQ/diskguard4.sh' && sleep 2 && tail -1 $BQ/diskguard4.log"
  say "disk guard 4 started (covers c3x; stop file $BQ/DISKGUARD4_STOP)";;
arm)
  need_x; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  [ -s $IO/render_cmp.out ] && grep -q "render compare: 0 FAIL" $IO/render_cmp.out || no "no passed 'render' in $IO"
  # 1. c3all3 has dispatched ALL its jobs; no other live queue can start training
  d3=$(R "grep -m1 'cv02 q: all jobs dispatched' $BQ/c3all3/launch.log") || no "c3all3 has not dispatched all its jobs (no 'cv02 q: all jobs dispatched' line): c3x is not armed"
  echo "c3all3: ${d3:0:60}"
  o=$(qscan) || no "ssh failed"
  echo "$o"; case "$o" in *CAN_START*) no "another queue can still start training";; esac
  # 2. the placed queue dir, the deploy, the data
  o=$(R "cd $Q && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) LPG \$(cat LPG) MAXC \$(cat MAXC) share \$(cat SHARE_TRAIN 2>/dev/null)/\$(cat SHARE_DUMP 2>/dev/null) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_$NEWQ' 2>/dev/null && echo yes || echo no) data \$(md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32)\"") || no "ssh failed"
  [ "$o" = "jobs $J LPG 1 MAXC 8 share $ST/$SD used 0 ses no data $DATA_MD5" ] || no "queue dir or data check: $o"
  echo "queue dir $Q: jobs md5, LPG 1, MAXC 8, SHARE_TRAIN $ST, SHARE_DUMP $SD, unused; data $DATA_MD5"
  xb_check
  # 3. disk, its guard, no HOLD anywhere
  o=$(R "a=\$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); open=0; for f in $BQ/c3all3/pids/*.gpu; do [ -e \$f ] && [ ! -e \${f%.gpu}.end ] && open=\$((open+1)); done; echo \"free \$a guard \$(tmux has-session -t '=bench_diskguard4' 2>/dev/null && echo yes || echo no) \$(md5sum < $BQ/diskguard4.sh 2>/dev/null | cut -c1-32) hold \$(ls $BQ/*/HOLD 2>/dev/null | wc -l) open3 \$open\"") || no "ssh failed"
  set -- $o; echo "cv02: $o"
  [ "${4:-}" = yes ] && [ "${5:-}" = "$GUARD_MD5" ] || no "disk guard 4 is not running with the reviewed script (run 'guard')"
  [ "${7:-}" = 0 ] || no "a HOLD file exists in a cv02 queue dir"
  need=$(awk -v o="${9:-0}" 'BEGIN { printf "%d", 25 * 1.03 + 3.3 + 8 * 0.27 + o * 1.2 + 20 + 0.999 }')
  echo "disk need (S): 25 c3x runs x 1.03 GB that stay + 3.3 GB of .swad dump dirs that stay (c3_f81_list.sh removes the swad_bn dir only) + 8 x 0.27 GB dumps in transit + ${9:-0} open c3all3 runs x 1.2 GB + the 20 GB guard floor = about $need GB; free ${2:-?} GB"
  if [ "${2:-0}" -lt "$need" ] 2>/dev/null; then
    [ "${DISK_OK:-0}" = 1 ] || no "cv02 /tmp free ${2:-?} GB < $need GB needed to finish c3x without a HOLD (free space first, or DISK_OK=1: disk guard 4 then HOLDs c3x at 20 GB free, which stops new training starts AND the dumps of finished c3x runs)"
    echo "DISK_OK=1: arming with ${2:-?} GB free < $need GB; disk guard 4 will HOLD c3x at 20 GB free (no training start and no dump start; finished runs wait undumped)"
  fi
  A="B=$XB Q=$Q SES=bench_q_$NEWQ DEPLOY=$X JOBS_MD5=$J DATA_MD5=$DATA_MD5 bash $XB/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, pre-checks passed; not run on cv02: $A"; exit 0; fi
  R "$A" | tee $IO/arm.out
  grep -q "cq_setup: bench_q_$NEWQ armed: gpumem [0-9]* queue [0-9]*" $IO/arm.out || no "arming not confirmed (see $IO/arm.out)"
  t=0; a=""
  while [ $t -lt ${ARMWAIT:-300} ]; do a=$(R "grep -m1 -E 'cv02 q armed:|; not starting' $Q/launch.log" 2>/dev/null); [ -n "$a" ] && break; sleep 10; t=$((t+10)); done
  echo "$a" | cut -c1-400
  case "$a" in *"cv02 q armed:"*) ;;
    *"; not starting"*) no "cq.sh did NOT arm: '${a#*] }'. Nothing of c3x runs; see $Q/launch.log";;
    *) no "no 'cv02 q armed:' line in $Q/launch.log after $t s: arming is NOT confirmed; look at $Q/launch.log and the tmux session bench_q_$NEWQ";; esac
  echo "$a" | grep -q "SHARE_TRAIN $ST MiB, SHARE_DUMP $SD MiB" || echo "WARNING: the armed line does not show SHARE_TRAIN $ST and SHARE_DUMP $SD: the queue runs by the strict rule only"
  say "armed bench_q_$NEWQ ('cv02 q armed:' line seen; $(echo "$a" | grep -o "sharing .*"); $Q; jobs $J; B = QC = $XB). Owed: at the first start 'c3x_hrnet_swad_v11_f0_s5 config OK (= card)' and 'startup line OK: Labelled: 425 ...'; relay: XB=$XB bash $HERE/c3x_relay.sh";;
status)
  R "echo \"cv02 \$(date -u '+%F %T') UTC; free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD files: \$(ls $BQ/*/HOLD 2>/dev/null | tr '\n' ' ')\"; for q in c3all3 $NEWQ; do d=$BQ/\$q; [ -d \$d ] || { echo \"\$q: no dir\"; continue; }; echo \"\$q: MAXC \$(cat \$d/MAXC 2>/dev/null) started \$(ls \$d/pids/*.gpu 2>/dev/null | wc -l) ended \$(ls \$d/pids/*.end 2>/dev/null | wc -l) of \$(grep -c . \$d/jobs.txt) dispatched-all \$(grep -c 'all jobs dispatched' \$d/launch.log 2>/dev/null)\"; for f in \$d/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$d/pids/\$n.end ] || echo \"  open: \$n GPU \$(cat \$f) training rc \$(cat \$d/pids/\$n.rc 2>/dev/null || echo running)\"; done; done; true";;
*) no "unknown step";;
esac
