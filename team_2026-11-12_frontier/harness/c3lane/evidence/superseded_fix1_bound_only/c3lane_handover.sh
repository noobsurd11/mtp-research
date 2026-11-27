#!/bin/bash
# c3lane handover c3all2 -> c3all3 (17 Nov 2026) = harness/c3swad/c3swad_handover.sh (0bb63159, the version reviewed after
# fix round 1 and used for c3all -> c3all2) with these changes only: defaults PREV c3all2, NEWQ c3all3, IO .../c3lane; the
# md5 pins of the queue code are those of c3lane.patch (cq.sh 564f05d3, cq_rescue.sh 204f9bce); the job builder and the disk
# guard file are read from ../c3swad (unchanged); `build` also needs c3all frozen; `render` compares EVERY rendered line with
# PREV's jobs_rendered.txt (all lines are carried, none is new); `place` writes SHARE_TRAIN 20480 and SHARE_DUMP 10240 (lane
# rule v2: the user's floors) and `arm` checks them; `guard` is not needed (disk guard 3 already runs and names c3all3).
# The text below is the c3swad header.
# c3swad handover (run by the LEAD on gaint, only after the review): freeze the running cv02 queue at a job boundary
# (MAXC 0, as c3base and c3hrnet on 16 Nov) and arm ONE successor queue that holds its not-started lines plus the 25
# swad_const lines (order: c3swad_make_jobs.py; default PF, swad, HRNet, HOUSE). Never two armed training queues: `arm` refuses unless every other live
# queue on cv02 has MAXC 0 or has dispatched all its jobs.
# One step per call, in this order. Each step refuses rather than guess, and prints what it did.
#   freeze   cv02 WRITE (one file, by rename of MAXC.new): PREV/MAXC <- 0. No running run or dump is touched (cq.sh reads
#            MAXC only before a new training start; the dump chain does not read it). Never raise that file again.
#            Before the write it runs the queue test of `arm` and refuses if any other live queue could start training.
#   build    cv02 READ ONLY. At least SETTLE s after freeze: fetch PREV's jobs.txt and its started set (pids/*.gpu),
#            build IO/jobs.txt, check that no name of it exists anywhere (cv02 experiments, runs, queue dirs; gaint relays).
#   render   cv02 WRITE (a new scratch dir only): render-only run of QC's cq.sh on IO/jobs.txt with B = the live deploy
#            (cq.sh stops at the logger check; nothing starts, no GPU is read). Carried lines must render byte-equal to
#            PREV's own jobs_rendered.txt; the swad lines are printed for one job.
#   place    cv02 WRITE: new queue dir NEWQ with jobs.txt (read-only), LPG 1, MAXC 8.
#   guard    cv02 WRITE + START: disk guard 3 (diskguard3.sh; tmux bench_diskguard3; HOLD in NEWQ below 20 GB free).
#   arm      cv02 START: QC's cq_setup.sh with B = the live deploy, after the pre-checks below. It reports "armed" only
#            when the line 'cv02 q armed:' is in the new queue's launch.log (waits up to ARMWAIT s, default 300).
#   status   cv02 READ ONLY.
# DRY=1: every cv02 write or start is printed, not run; the read-only checks run. DRY=1 build makes a PREVIEW of the
#   list from the queue as it is now (no freeze needed; files IO/preview_*; never used by place or arm).
# MODE=reorder: a successor WITHOUT swad lines (order PF, HRNet, HOUSE), armed with the unpatched queue code of the live
#   deploy (no QC, no render step): only carried, already reviewed lines; as c3all was built on 16 Nov. A later swad
#   handover then uses PREV=<that queue> NEWQ=<next name> and a new IO.
# BUILD_OPTS=--alternate: the other order of c3swad_make_jobs.py (swad and HRNet in turn; default: all swad seeds first).
# Env: QC (render, arm: cv02 deploy dir of the patched queue code, /tmp/noob_el/bench_<7 hex>), PREV (c3all),
#   NEWQ (c3all2), IO (/home/noob/work/bench_c3_io/c3swad), SETTLE (180), FLOOR (cv02 GB free needed to arm, 45),
#   PREV_JOBS_MD5 (c58f610b... for c3all).
set -u
STEP=${1:?step: freeze | build | render | place | guard | arm | status}
PREV=${PREV:-c3all2}; NEWQ=${NEWQ:-c3all3}; IO=${IO:-/home/noob/work/bench_c3_io/c3lane}; DRY=${DRY:-0}
ST=20480; SD=10240     # the user's floors (MiB) for SHARE_TRAIN and SHARE_DUMP of the new queue; not to be lowered
SETTLE=${SETTLE:-180}; FLOOR=${FLOOR:-45}; QC=${QC:-}; MODE=${MODE:-swad}; BUILD_OPTS=${BUILD_OPTS:-}
case $MODE in swad) ;; reorder) BUILD_OPTS=--no-swad;; *) echo "REFUSED: MODE must be swad or reorder"; exit 1;; esac
case "$BUILD_OPTS" in ""|--no-swad|--alternate) ;; *) echo "REFUSED: BUILD_OPTS"; exit 1;; esac
BQ=/tmp/noob_el/bench_q; B=/tmp/noob_el/bench_89b9ea5
DEPLOY=89b9ea5a12a37a87c16c4868cc4adf00794a7610; DATA_MD5=d6063fd83d20e656612540edda702cbe
[ $PREV = c3all2 ] && PREV_JOBS_MD5=${PREV_JOBS_MD5:-29388346e2176ce1f2f77a1136b0ab84}; PREV_JOBS_MD5=${PREV_JOBS_MD5:-}
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); SW=$HERE/../c3swad
P=/home/noob/work/el-fault-detection/.venv/bin/python
# md5 pins of the queue code in QC (cq_c3swad.patch on 89b9ea5) and of the card in B
PINS="564f05d372e67514226f12200ce9e348  bench/q/cv02/cq.sh
204f9bce070e695df63de779becce287  bench/q/cv02/cq_rescue.sh
630b1307a5b3cc99da251cd6eecc8672  bench/q/cv02/cq_setup.sh
20712dd3af1e6b86720a9633b419de00  bench/q/cv02/slim_ckpt.py
f3affc80b21406644cedbc80d6e250ba  bench/q/cv02/cvcard.py
2a5f688160eb100eb0bc9784ffe06e7e  bench/q/cv02/cq_gpumem.sh
1af2ed69babf72e9d0d0aa789eb71121  bench/q/bench_lib.sh
618cea2f57864ac4a916da00845da9da  bench/methods_cv02/swad_const_pf_v11.yaml
46fb5b02be9d59b4dc00a21dc216e86f  bench/methods/swad_const_pf_v11.yaml"
CARD_MD5=46fb5b02be9d59b4dc00a21dc216e86f; GUARD_MD5=$(md5sum < $SW/diskguard3.sh | cut -c1-32)
C=cv02@10.8.1.106
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }                       # read only
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
say(){ echo "[$(date '+%F %T')] $STEP: $*" | tee -a $IO/handover.log; }
case "$PREV$NEWQ" in *[!a-z0-9_]*) no "bad queue name";; esac
[ $PREV != $NEWQ ] || no "PREV = NEWQ"
mkdir -p $IO || exit 1
need_qc(){ echo "$QC" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' || no "QC must be /tmp/noob_el/bench_<7 hex> (the deploy of the patched queue code)"; [ "$QC" != "$B" ] || no "QC = B"; }
started(){ R "cd $BQ/$PREV/pids 2>/dev/null && ls | sed -n 's/\.gpu\$//p' | sort"; }
# qscan: one line per live queue on cv02 other than NEWQ. "ok <name> <why>" if it cannot start a training run: MAXC 0, or
#   all jobs dispatched, or every line of its jobs.txt is a --fixture job (a dump dry test; cq.sh skips training for it).
#   Else "CAN_START <name>". Used by `freeze` (before the MAXC write) and by `arm`.
qscan(){ R "for q in $BQ/*/; do n=\$(basename \$q); [ \$n = $NEWQ ] && continue; p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; [ \"\$(cat \$q/MAXC 2>/dev/null)\" = 0 ] && { echo \"ok \$n MAXC 0\"; continue; }; grep -q 'cv02 q: all jobs dispatched' \$q/launch.log && { echo \"ok \$n all dispatched\"; continue; }; [ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && { echo \"ok \$n fixture only, cannot train\"; continue; }; echo \"CAN_START \$n\"; done; true"; }
qc_check(){   # pins, CODE.md5 of QC, and QC against B: only the patch's files and REVISION may differ
  local out; out=$(R "cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"$PINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo PINS_OK; diff <(grep -v '  REVISION\$' $B/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || no "ssh failed"
  case "$out" in *CODE_OK*) ;; *) no "QC CODE.md5 check failed";; esac
  case "$out" in *PINS_OK*) ;; *) no "QC files do not match the pinned md5s of the reviewed patch";; esac
  local d; d=$(echo "$out" | tail -1)
  [ "$d" = "<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/q/cv02/slim_ckpt.py >bench/methods_cv02/swad_const_pf_v11.yaml >bench/q/cv02/cq.sh >bench/q/cv02/cq_rescue.sh >bench/q/cv02/cq_setup.sh >bench/q/cv02/slim_ckpt.py >tests/test_bench_cq_readouts.py " ] || no "QC differs from B in more than the patch's files: $d"
  echo "QC $QC: CODE.md5 OK, pinned md5s OK, differs from B only in cq.sh, cq_setup.sh, slim_ckpt.py (changed) and cq_rescue.sh, the cv02 card variant, the test file (added)"; }

case $STEP in
freeze)
  tmux has-session -t "=bench_maxc_window" 2>/dev/null && no "a MAXC window script is running on gaint (bench_maxc_window)"
  cur=$(R "cat $BQ/$PREV/MAXC") || no "ssh failed"
  case "$cur" in 8|0) ;; *) no "$PREV/MAXC reads '$cur' (expected 8, or 0 if already frozen)";; esac
  # the test of `arm` step 1, before the write: never freeze $PREV while `arm` would refuse
  o=$(qscan) || no "ssh failed"; echo "$o"
  oth=$(echo "$o" | awk -v p=$PREV '$1 == "CAN_START" && $2 != p {print $2}' | tr '\n' ' ')
  [ -z "$oth" ] || no "another live queue can start training ($oth); 'arm' would refuse, so $PREV is not frozen. End or freeze that queue first"
  echo "$o" | grep -qE "^(CAN_START|ok) $PREV( |\$)" || no "$PREV has no live queue process; 'arm' would refuse, so nothing is written"
  out=$(Wr "echo 0 > $BQ/$PREV/MAXC.new && mv $BQ/$PREV/MAXC.new $BQ/$PREV/MAXC && cat $BQ/$PREV/MAXC")
  [ $DRY = 1 ] && { echo "$out"; exit 0; }
  [ "$out" = 0 ] || no "write of 0 not confirmed ('$out')"
  [ -e $IO/freeze.time ] || date +%s > $IO/freeze.time
  say "$PREV/MAXC was $cur, now 0 (confirmed). Never raise it again. Run 'build' after $SETTLE s.";;
build)
  m=$(R "cat $BQ/$PREV/MAXC $BQ/c3all/MAXC $BQ/c3base/MAXC $BQ/c3hrnet/MAXC | tr '\n' ' '")
  if [ $DRY = 1 ]; then echo "DRY: PREVIEW only ($PREV is not required to be frozen; MAXC of $PREV, c3all, c3base, c3hrnet reads '$m')"; rm -f $IO/preview_*; O=$IO/preview_
  else O=$IO/
    [ -e $IO/freeze.time ] || no "no freeze recorded in $IO (run 'freeze' first)"
    age=$(( $(date +%s) - $(cat $IO/freeze.time) )); [ $age -ge $SETTLE ] || no "only $age s since the freeze; wait $SETTLE s"
    [ -e $IO/jobs.txt ] && no "$IO/jobs.txt exists (a list was already built; use a new IO for a new handover)"
    [ "$m" = "0 0 0 0 " ] || no "MAXC of $PREV, c3all, c3base, c3hrnet reads '$m', expected '0 0 0 0 '"
  fi
  R "cat $BQ/$PREV/jobs.txt" > ${O}prev_jobs.txt || no "ssh failed"
  R "cat $BQ/$PREV/jobs_rendered.txt" > ${O}prev_rendered.txt || no "ssh failed"
  [ -z "$PREV_JOBS_MD5" ] || [ "$(md5sum < ${O}prev_jobs.txt | cut -c1-32)" = "$PREV_JOBS_MD5" ] || no "$PREV jobs.txt md5 != $PREV_JOBS_MD5"
  started > ${O}started.txt || no "ssh failed"; sleep 20; started > ${O}started2.txt || no "ssh failed"
  cmp -s ${O}started.txt ${O}started2.txt || no "the started set changed within 20 s (a start was in flight); remove ${O}started*.txt and run build again"
  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $SW/c3swad_make_jobs.py ${O}prev_jobs.txt ${O}started.txt ${O}jobs.txt $BUILD_OPTS | tee ${O}build.out
  [ -s ${O}jobs.txt ] || no "job builder failed"
  cut -d'|' -f1 ${O}jobs.txt > ${O}names.txt
  hit=$(R "for n in $(tr '\n' ' ' < ${O}names.txt); do for b in /tmp/noob_el/bench_*/; do [ -e \$b/experiments/\$n ] || [ -e \$b/experiments/\$n.stdout ] || [ -e \$b/runs/\$n ] && echo \"\$n in \$b\"; done; ls $BQ/*/pids/\$n.gpu 2>/dev/null; done; true") || no "ssh failed"
  [ -z "$hit" ] || no "names already used on cv02: $(echo "$hit" | head -3 | tr '\n' ' ')"
  for n in $(cat ${O}names.txt); do ls -d /home/noob/work/bench_relay/*/$n /home/noob/work/bench_relay/*/.ok/$n 2>/dev/null; done > ${O}relay_hits.txt
  [ ! -s ${O}relay_hits.txt ] || no "names already in a gaint relay dir: $(head -3 ${O}relay_hits.txt | tr '\n' ' ')"
  md5sum < ${O}jobs.txt | cut -c1-32 > ${O}jobs.md5
  say "built ${O}jobs.txt: $(wc -l < ${O}jobs.txt) lines, md5 $(cat ${O}jobs.md5); started in $PREV: $(wc -l < ${O}started.txt); no name in use on cv02 or in a gaint relay";;
render)
  [ $MODE = swad ] || no "MODE=reorder needs no render (unpatched queue code, carried lines only)"
  need_qc; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt (run 'build')"
  qc_check
  W=/tmp/noob_el/bench_c3s_render/$(date +%Y%m%d_%H%M%S); J=$(cat $IO/jobs.md5)
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $W/q, place jobs.txt (md5 $J) and LPG 1 there, B=$B Q=$W/q QC=$QC JOBS_MD5=$J DEPLOY=$DEPLOY DATA_MD5=$DATA_MD5 nice -n 19 bash $QC/bench/q/cv02/cq.sh"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir -p $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && md5sum < $W/q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/render_md5.txt || no "placing the scratch list failed"
  [ "$(cat $IO/render_md5.txt)" = "$J" ] || no "scratch jobs.txt md5 differs"
  R "B=$B Q=$W/q QC=$QC JOBS_MD5=$J DEPLOY=$DEPLOY DATA_MD5=$DATA_MD5 nice -n 19 bash $QC/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $IO/render.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $IO/render.out || no "render did not reach the logger check (see $IO/render.out)"
  R "cat $W/q/jobs_rendered.txt" > $IO/rendered.txt || no "ssh failed"
  cp $IO/rendered.txt $IO/rendered_carried.txt      # c3lane: every line of the list is carried from $PREV, the swad lines included
  nc=$(grep -c . $IO/rendered_carried.txt); nx=$(grep -cFxf $IO/prev_rendered.txt $IO/rendered_carried.txt)
  [ "$nc" = "$nx" ] && [ "$nc" = $(( 2 * $(grep -cvE '^c3s_swad_' $IO/jobs.txt) + 3 * $(grep -cE '^c3s_swad_' $IO/jobs.txt) )) ] || no "carried lines: $nx of $nc rendered lines are byte-equal to $PREV's jobs_rendered.txt"
  ns=$(grep -cE '^(dump_)?c3s_swad_' $IO/rendered.txt); [ "$ns" = $(( 3 * $(grep -cE '^c3s_swad_' $IO/jobs.txt) )) ] || no "swad lines rendered: $ns"
  say "render OK in cv02 $W: $nc carried lines byte-equal to $PREV's jobs_rendered.txt; $ns swad lines (train, dump, dump .swad per job). First swad job:"
  grep -E '^(dump_)?c3s_swad_v11_f0_s5' $IO/rendered.txt | sed -n 1,3p;;
place)
  [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5); Q=$BQ/$NEWQ
  R "test ! -e $Q && echo FREE" | grep -qx FREE || no "$Q exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $Q; jobs.txt (md5 $J, $(wc -l < $IO/jobs.txt) lines, r--r--r--); LPG 1; MAXC 8; SHARE_TRAIN $ST; SHARE_DUMP $SD"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && echo 1 > $Q/LPG && echo 8 > $Q/MAXC && echo $ST > $Q/SHARE_TRAIN && echo $SD > $Q/SHARE_DUMP && md5sum < $Q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/place_md5.txt || no "placing failed"
  [ "$(cat $IO/place_md5.txt)" = "$J" ] || no "placed jobs.txt md5 differs"
  say "placed $Q: jobs.txt md5 $J, LPG 1, MAXC 8, SHARE_TRAIN $ST, SHARE_DUMP $SD (not armed)";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard3' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard3.sh && md5sum < $BQ/diskguard3.sh | cut -c1-32")
  case "$s" in *RUNNING*) no "tmux bench_diskguard3 already runs on cv02";; esac
  grep -qE "for q in ([a-z0-9_]+ )*$NEWQ( [a-z0-9_]+)*;" $SW/diskguard3.sh || no "diskguard3.sh does not name $NEWQ"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: place $BQ/diskguard3.sh (md5 $GUARD_MD5), tmux new-session -d -s bench_diskguard3 'bash $BQ/diskguard3.sh'"; exit 0; fi
  if [ -z "$s" ]; then ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $BQ/diskguard3.sh && cat > $BQ/diskguard3.sh" < $SW/diskguard3.sh || no "placing diskguard3.sh failed"; fi
  [ "$(R "md5sum < $BQ/diskguard3.sh | cut -c1-32")" = "$GUARD_MD5" ] || no "cv02 diskguard3.sh md5 differs"
  Wr "tmux new-session -d -s bench_diskguard3 'bash $BQ/diskguard3.sh' && sleep 2 && tail -1 $BQ/diskguard3.log"
  say "disk guard 3 started (covers $NEWQ; stop file $BQ/DISKGUARD3_STOP)";;
arm)
  [ $MODE = reorder ] || need_qc; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5); Q=$BQ/$NEWQ
  if [ $MODE = reorder ]; then [ "$(grep -c "^c3s_swad_" $IO/jobs.txt)" = 0 ] || no "MODE=reorder but the list holds swad lines"
  else [ "$(grep -c "^c3s_swad_" $IO/jobs.txt)" -ge 1 ] || no "MODE=swad but the list holds no swad line"; fi
  # 1. only one queue may start training: every other live queue has MAXC 0, has dispatched all its jobs, or holds only --fixture jobs
  o=$(qscan) || no "ssh failed"
  echo "$o"; case "$o" in *CAN_START*) no "another queue can still start training (freeze it first)";; esac
  echo "$o" | grep -qx "ok $PREV MAXC 0" || no "$PREV is not frozen (MAXC 0) or its queue is gone"
  # 2. no start in PREV since the list was built
  started > $IO/started_arm.txt || no "ssh failed"; cmp -s $IO/started.txt $IO/started_arm.txt || no "$PREV's started set changed since 'build'"
  # 3. the placed queue dir, the live deploy, the card, the queue code
  o=$(R "cd $Q && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) LPG \$(cat LPG) MAXC \$(cat MAXC) share \$(cat SHARE_TRAIN 2>/dev/null)/\$(cat SHARE_DUMP 2>/dev/null) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_$NEWQ' 2>/dev/null && echo yes || echo no) rev \$(cat $B/REVISION) code \$(cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo OK || echo FAIL) card \$(md5sum < $B/bench/methods/swad_const_pf_v11.yaml | cut -c1-32) data \$(md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32)\"") || no "ssh failed"
  [ "$o" = "jobs $J LPG 1 MAXC 8 share $ST/$SD used 0 ses no rev $DEPLOY code OK card $CARD_MD5 data $DATA_MD5" ] || no "queue dir or deploy check: $o"
  echo "queue dir $Q: jobs md5, LPG 1, MAXC 8, SHARE_TRAIN $ST, SHARE_DUMP $SD, unused; deploy $B = $DEPLOY, CODE.md5 OK; swad card $CARD_MD5; data $DATA_MD5"
  [ $MODE = reorder ] || qc_check
  # 4. disk and its guard
  o=$(R "a=\$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); echo \"free \$a guard \$(tmux has-session -t '=bench_diskguard3' 2>/dev/null && echo yes || echo no) \$(md5sum < $BQ/diskguard3.sh 2>/dev/null | cut -c1-32) hold \$(ls $BQ/*/HOLD 2>/dev/null | wc -l)\"") || no "ssh failed"
  set -- $o; echo "cv02: $o"
  [ "${2:-0}" -ge "$FLOOR" ] 2>/dev/null || no "cv02 /tmp free ${2:-?} GB < $FLOOR"
  [ "${4:-}" = yes ] && [ "${5:-}" = "$GUARD_MD5" ] || no "disk guard 3 is not running with the reviewed script (run 'guard')"
  [ "${7:-}" = 0 ] || no "a HOLD file exists in a cv02 queue dir"
  A="B=$B Q=$Q SES=bench_q_$NEWQ DEPLOY=$DEPLOY JOBS_MD5=$J DATA_MD5=$DATA_MD5 QC=$QC bash $QC/bench/q/cv02/cq_setup.sh"
  [ $MODE = reorder ] && A="B=$B Q=$Q SES=bench_q_$NEWQ DEPLOY=$DEPLOY JOBS_MD5=$J DATA_MD5=$DATA_MD5 bash $B/bench/q/cv02/cq_setup.sh"
  need=$(awk -F"|" '{ if ($1 ~ /^c3s_swad_/) s += 1.5; else if ($1 ~ /^c3h_/) s += 0.5; else s += 0.6 } END { printf "%d", s + 24.5 }' $IO/jobs.txt)
  echo "disk note: about $need GB free are needed to finish all $(wc -l < $IO/jobs.txt) jobs without a HOLD (per run 0.6 PF or HOUSE, 0.5 HRNet, 1.5 swad; + 4 for dumps in transit + the 20 GB guard floor), if relayed --logp dumps are removed as now; free now ${2:-?} GB"
  if [ $DRY = 1 ]; then echo "DRY, pre-checks passed; not run on cv02: $A"; exit 0; fi
  R "$A" | tee $IO/arm.out
  grep -q "cq_setup: bench_q_$NEWQ armed: gpumem [0-9]* queue [0-9]*" $IO/arm.out || no "arming not confirmed (see $IO/arm.out)"
  # cq_setup.sh prints its line from the pid files; cq.sh itself is armed only when its own line is in launch.log
  t=0; a=""
  while [ $t -lt ${ARMWAIT:-300} ]; do a=$(R "grep -m1 -E 'cv02 q armed:|; not starting' $Q/launch.log" 2>/dev/null); [ -n "$a" ] && break; sleep 10; t=$((t+10)); done
  echo "$a" | cut -c1-400
  case "$a" in *"cv02 q armed:"*) ;;
    *"; not starting"*) no "cq.sh did NOT arm: '${a#*] }'. $PREV is frozen and no successor runs; see $Q/launch.log";;
    *) no "no 'cv02 q armed:' line in $Q/launch.log after $t s: arming is NOT confirmed. $PREV is frozen; look at $Q/launch.log and the tmux session bench_q_$NEWQ";; esac
  echo "$a" | grep -q "SHARE_TRAIN $ST MiB, SHARE_DUMP $SD MiB" || echo "WARNING: the armed line does not show SHARE_TRAIN $ST and SHARE_DUMP $SD: the queue runs by the strict rule only"
  say "armed bench_q_$NEWQ ('cv02 q armed:' line seen; $(echo "$a" | grep -o "sharing .*"); $Q; jobs $J; B $B; QC $QC). Owed: first-start lines 'config OK (= card)' and 'startup line OK' in $Q/launch.log; relay c3swad_relay.sh";;
status)
  R "echo \"cv02 \$(date -u '+%F %T') UTC; free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD files: \$(ls $BQ/*/HOLD 2>/dev/null | tr '\n' ' ')\"; for q in $PREV $NEWQ; do d=$BQ/\$q; [ -d \$d ] || { echo \"\$q: no dir\"; continue; }; echo \"\$q: MAXC \$(cat \$d/MAXC 2>/dev/null) started \$(ls \$d/pids/*.gpu 2>/dev/null | wc -l) ended \$(ls \$d/pids/*.end 2>/dev/null | wc -l) of \$(grep -c . \$d/jobs.txt)\"; for f in \$d/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$d/pids/\$n.end ] || echo \"  open: \$n GPU \$(cat \$f) training rc \$(cat \$d/pids/\$n.rc 2>/dev/null || echo running)\"; done; done; true";;
*) no "unknown step";;
esac
