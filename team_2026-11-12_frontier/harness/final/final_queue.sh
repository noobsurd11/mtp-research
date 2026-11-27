#!/bin/bash
# fin queue on cv02 (final package; LAUNCH_REQUEST_final.md section 4; run by the LEAD on gaint after the review, the deploy
# of F and the checks). Built from harness/c3x/c3x_queue.sh (2b4fe313): one NEW queue `fin` of 85 lines (final_make_jobs.py):
# 10 full-pool trainings and 75 dump-only D4 jobs. Armed only if every other live queue cannot start training (MAXC 0, all
# dispatched, or fixture only): never two queues that can start training. Lane rule v2 unchanged (cq.sh of F): SHARE_TRAIN
# 20480 and SHARE_DUMP 10240 (the user's floors), LPG 1 (one of our runs per GPU), MAXC 12 (8 trainings + up to 4 dump-only
# jobs beside them by the reviewed dump rule). B = QC = FB = the deploy of F (training, dumps, runs, queue code, cv02 card
# variants all from FB; its CODE.md5 equals bench_03375d4's except the 10 paths of final_codeproof.sh, checked on cv02).
# One step per call, in this order. Each step refuses rather than guess, and prints what it did.
#   build    gaint + cv02 READ ONLY: IO/jobs.txt from final_make_jobs.py; no name of it exists on cv02 (experiments, runs or a
#            dump dir of any deploy, any queue's pids) or in a gaint relay dir; the 50 source run dirs are complete.
#   root     cv02 WRITE (one new dir /tmp/noob_el/bench_data_fin): FB's scripts/bench_make_pool_root.py builds pool532_v11 from
#            cv02's pinned inputs, then --check; md5 pins of train.txt, test.txt, SPLITS.md5, DATA_MANIFEST.md5 (= the gaint
#            build and the builder's cv02 smoke); files made read-only (find -type f; no symlink is followed).
#   render   cv02 WRITE (a new scratch queue dir only; cq.sh also makes the empty dirs experiments/ runs/ dumps/ in FB, as at
#            arming): render-only run of FB's cq.sh on IO/jobs.txt (it stops at the logger check; nothing starts, no GPU is
#            read); the 85 rendered lines are checked by final_rendercmp.py (templates and semantics).
#   place    cv02 WRITE: queue dir /tmp/noob_el/bench_q/fin with jobs.txt (read-only), LPG 1, MAXC 12, SHARE_TRAIN 20480,
#            SHARE_DUMP 10240. Not armed.
#   guard    cv02 WRITE + START: disk guard 5 (diskguard5.sh; tmux bench_diskguard5; HOLD in fin below 20 GB free).
#   arm      cv02 START: FB's cq_setup.sh (session bench_q_fin, GAPSEC default 30) after the pre-checks below. Reports "armed"
#            only when the line 'cv02 q armed:' is in fin's launch.log (waits up to ARMWAIT s, default 300).
#   status   cv02 READ ONLY.
# DRY=1: every cv02 write or start is printed, not run; the read-only checks run.
# Env: F (full commit of F), FB (/tmp/noob_el/bench_<F 7 hex>; render, root, arm), IO (/home/noob/work/bench_fin_io), GAPSEC
#   (arm; whole seconds >= 30; default 30, the lead's choice: 85 jobs x up to 2 gaps each), MAXC (place; default 12),
#   DISK_OK=1 (arm: the lead accepts arming with less free space than the estimate; disk guard 5 then HOLDs fin at 20 GB free:
#   no new training start and no dump start).
set -u
STEP=${1:?step: build | root | render | place | guard | arm | status}
NEWQ=fin; IO=${IO:-/home/noob/work/bench_fin_io}; DRY=${DRY:-0}; F=${F:-}; FB=${FB:-}; GAPSEC=${GAPSEC:-30}; MAXC=${MAXC:-12}
ST=20480; SD=10240     # the user's floors (MiB) for SHARE_TRAIN and SHARE_DUMP; not to be lowered
BQ=/tmp/noob_el/bench_q; B03=/tmp/noob_el/bench_03375d4; B89=/tmp/noob_el/bench_89b9ea5; Q=$BQ/$NEWQ
DF=/tmp/noob_el/bench_data_fin; DFR=$DF/roots/pool532_v11
DATA_MD5=d6063fd83d20e656612540edda702cbe; FC=821dfadf49116cc6d5fdbd6697e263dd7cf0f834
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; PC=/tmp/noob_el/el-fault-detection/.venv/bin/python
# md5 pins in FB: queue code, dump code and root builder of F, the two cards and their cv02 variants
PINS="012e8e3f4f6d4df5cada8401a4e932d4  bench/q/cv02/cq.sh
54256ac9992fefffe039d8b7207cd857  bench/q/cv02/cq_setup.sh
204f9bce070e695df63de779becce287  bench/q/cv02/cq_rescue.sh
20712dd3af1e6b86720a9633b419de00  bench/q/cv02/slim_ckpt.py
f3affc80b21406644cedbc80d6e250ba  bench/q/cv02/cvcard.py
2a5f688160eb100eb0bc9784ffe06e7e  bench/q/cv02/cq_gpumem.sh
1af2ed69babf72e9d0d0aa789eb71121  bench/q/bench_lib.sh
32e0b67c2ad8073c33440b8347d77f57  scripts/bench_infer.py
801ff5228c14476968627bbdbff3253e  bench/tta.py
a479fdff1dc667b26d18ee05fac9f6eb  scripts/bench_make_pool_root.py
98f152de3ea7f8c88e892162e07b4450  bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
d7b207089f6cfeb484ca9ef96f734786  bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
a4a46a526cf14d649f3176edd53a9c32  bench/methods/house_r34_unetpp_pf_v11.yaml
bbdef88b2a5e6dde5e01ffaf23ba0d2b  bench/methods_cv02/house_r34_unetpp_pf_v11.yaml"
DW="<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/tta.py <scripts/bench_infer.py <tests/test_bench_cards_cv02.py <tests/test_bench_cq_cv5v3.py >bench/q/cv02/cq.sh >bench/q/cv02/cq_setup.sh >bench/tta.py >scripts/bench_infer.py >scripts/bench_make_pool_root.py >tests/test_bench_cards_cv02.py >tests/test_bench_cq_cv5v3.py >tests/test_bench_cq_final.py >tests/test_bench_pool_root.py >tests/test_bench_tta_pred.py "
ROOTPINS="d374fd843598f10fd4ba9101435986c8  splits/train.txt
79816ba63cca96e10265197eb4cfa905  splits/test.txt
cec1396e24b35c8bb0001de19f7d0c3b  SPLITS.md5
33e65b3f5ec964336d44583dcdfe6352  DATA_MANIFEST.md5"
GUARD_MD5=$(md5sum < $HERE/diskguard5.sh | cut -c1-32)
C=cv02@10.8.1.106
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }                       # read only
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
say(){ echo "[$(date '+%F %T')] $STEP: $*" | tee -a $IO/queue.log; }
mkdir -p $IO || exit 1
need_f(){ [ "$F" = $FC ] || no "F must be the full commit $FC"
  [ "$FB" = "/tmp/noob_el/bench_${F:0:7}" ] || no "FB must be /tmp/noob_el/bench_${F:0:7} (the deploy of F by c3_deploy.sh)"
  [ "$(git -C /home/noob/work/bench_wt_fin rev-parse $F^{tree} 2>/dev/null)" = 114d5469340e7bfd496f290c18dccb7d4f13bdd3 ] || no "F does not have the pinned tree"; }
# qscan: one line per live queue on cv02 other than fin: "ok <name> <why>" if it cannot start a training run (MAXC 0, all jobs
#   dispatched, or only --fixture jobs), else "CAN_START <name>" (= c3x_queue.sh's qscan with NEWQ fin).
qscan(){ R "for q in $BQ/*/; do n=\$(basename \$q); [ \$n = $NEWQ ] && continue; p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; [ \"\$(cat \$q/MAXC 2>/dev/null)\" = 0 ] && { echo \"ok \$n MAXC 0\"; continue; }; grep -q 'cv02 q: all jobs dispatched' \$q/launch.log && { echo \"ok \$n all dispatched\"; continue; }; [ -s \$q/jobs.txt ] && [ \"\$(cut -d'|' -f9 \$q/jobs.txt | sort -u)\" = --fixture ] && { echo \"ok \$n fixture only, cannot train\"; continue; }; echo \"CAN_START \$n\"; done; true"; }
fb_check(){   # FB: REVISION, CODE.md5, pins, and its CODE.md5 against bench_03375d4's: only the 10 paths of the proof may differ
  local out d; out=$(R "cd $FB && echo \"rev \$(cat REVISION)\"; md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"$PINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo PINS_OK; (cd $B03 && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && echo B03_OK; diff <(grep -v '  REVISION\$' $B03/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || no "ssh failed"
  case "$out" in "rev $F"*) ;; *) no "FB REVISION is not F";; esac
  case "$out" in *CODE_OK*) ;; *) no "FB CODE.md5 check failed";; esac
  case "$out" in *PINS_OK*) ;; *) no "FB files do not match the pinned md5s";; esac
  case "$out" in *B03_OK*) ;; *) no "bench_03375d4 CODE.md5 check failed";; esac
  d=$(echo "$out" | tail -1); [ "$d" = "$DW" ] || no "FB differs from bench_03375d4 in other paths than the 10 of the code proof: $d"
  echo "FB $FB: REVISION F, CODE.md5 OK, pins OK; differs from bench_03375d4 only in the 10 paths of the code proof (+ REVISION)"; }
root_check(){ local o; o=$(R "cd $DFR 2>/dev/null && echo \"$ROOTPINS\" | md5sum -c --quiet - > /dev/null 2>&1 && (cd $DF/roots && md5sum -c --quiet ROOTS_pool532_v11.md5 > /dev/null 2>&1) && echo ROOT_OK") || no "ssh failed"
  [ "$o" = ROOT_OK ] || no "$DFR: pins (train.txt d374fd84, test.txt 79816ba6, SPLITS.md5 cec1396e, DATA_MANIFEST.md5 33e65b3f) or ROOTS_pool532_v11.md5 check failed (run 'root')"
  echo "root $DFR: pins and ROOTS_pool532_v11.md5 OK"; }
src_check(){ local o; o=$(R "n=0; for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do for d in $B03/experiments/c3x_hrnet_swad_v11_f\${k}_s\$s $B89/experiments/c3_pf_v11_f\${k}_s\$s; do [ -s \$d/config_used.yaml ] && [ -s \$d/checkpoints/latest.pth ] && n=\$((n+1)) || echo \"MISSING \$d\"; done; done; done; echo \"complete \$n\"") || no "ssh failed"
  [ "$(echo "$o" | tail -1)" = "complete 50" ] || no "source run dirs incomplete: $(echo "$o" | head -3 | tr '\n' ' ')"
  echo "source runs: 50 of 50 complete (config_used.yaml + checkpoints/latest.pth; 25 c3x in bench_03375d4, 25 c3_pf_v11 in bench_89b9ea5)"; }

case $STEP in
build)
  [ -e $IO/jobs.txt ] && no "$IO/jobs.txt exists (use a new IO for a new list)"
  CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $HERE/final_make_jobs.py $IO/jobs.txt | tee $IO/build.out
  [ -s $IO/jobs.txt ] || no "job builder failed"
  cut -d'|' -f1 $IO/jobs.txt > $IO/names.txt
  hit=$(R "for n in $(tr '\n' ' ' < $IO/names.txt); do for b in /tmp/noob_el/bench_*/; do [ -e \$b/experiments/\$n ] || [ -e \$b/experiments/\$n.stdout ] || [ -e \$b/runs/\$n ] && echo \"\$n in \$b\"; ls -d \$b/dumps/elbench1/*/\$n 2>/dev/null; done; ls $BQ/*/pids/\$n.gpu 2>/dev/null; done; true") || no "ssh failed"
  [ -z "$hit" ] || { rm -f $IO/jobs.txt; no "names already used on cv02: $(echo "$hit" | head -3 | tr '\n' ' ')"; }
  for n in $(cat $IO/names.txt); do ls -d /home/noob/work/bench_relay/*/$n /home/noob/work/bench_relay/*/.ok/$n 2>/dev/null; done > $IO/relay_hits.txt
  [ ! -s $IO/relay_hits.txt ] || { rm -f $IO/jobs.txt; no "names already in a gaint relay dir: $(head -3 $IO/relay_hits.txt | tr '\n' ' ')"; }
  src_check
  md5sum < $IO/jobs.txt | cut -c1-32 > $IO/jobs.md5
  say "built $IO/jobs.txt: $(wc -l < $IO/jobs.txt) lines, md5 $(cat $IO/jobs.md5); no name in use on cv02 or in a gaint relay; 50 source runs complete";;
root)
  need_f; fb_check
  R "test ! -e $DF && echo FREE" | grep -qx FREE || no "$DF exists on cv02 (check it with 'arm' pre-checks or move it aside by hand)"
  A="cd $FB && nice -n 19 $PC scripts/bench_make_pool_root.py --split /tmp/noob_el/bench_data_v3b/meta/cv5v3.json --forbidden /tmp/noob_el/bench_data/meta/forbidden_v1.txt --legacy-splits $FB/data/splits --labeled /tmp/noob_el/bench_data/labeled --train-masks /tmp/noob_el/bench_data/masks_v11/masks --out $DF/roots"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $A; then the same with --check; then find $DF -type f -exec chmod a-w {} +"; exit 0; fi
  R "$A && $A --check && find $DF -type f -exec chmod a-w {} +" | tee $IO/root.out
  root_check
  say "built $DFR on cv02 (train 532 = the pool, val = test = cv5v3 fold-0 held-out list as an in-sample monitor; no sealed stem)";;
render)
  need_f; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt (run 'build')"
  fb_check; root_check
  W=/tmp/noob_el/bench_fin_render/$(date +%Y%m%d_%H%M%S); J=$(cat $IO/jobs.md5)
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $W/q, place jobs.txt (md5 $J) and LPG 1 there, B=$FB Q=$W/q JOBS_MD5=$J DEPLOY=$F DATA_MD5=$DATA_MD5 nice -n 19 bash $FB/bench/q/cv02/cq.sh"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir -p $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && md5sum < $W/q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/render_md5.txt || no "placing the scratch list failed"
  [ "$(cat $IO/render_md5.txt)" = "$J" ] || no "scratch jobs.txt md5 differs"
  R "B=$FB Q=$W/q JOBS_MD5=$J DEPLOY=$F DATA_MD5=$DATA_MD5 nice -n 19 bash $FB/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $IO/render.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $IO/render.out || no "render did not reach the logger check (see $IO/render.out)"
  R "cat $W/q/jobs_rendered.txt" > $IO/rendered.txt || no "ssh failed"
  PYTHONDONTWRITEBYTECODE=1 $P $HERE/final_rendercmp.py --jobs $IO/jobs.txt --rendered $IO/rendered.txt --b $FB | tee $IO/render_cmp.out
  [ ${PIPESTATUS[0]} = 0 ] || no "rendered lines do not match (see $IO/render_cmp.out)"
  say "render OK in cv02 $W: 85 lines (10 training, 75 dump-only); templates and semantics 0 FAIL. First lines:"
  grep -E '^(fin_hrnet_swad_v11_pool_s5|dump_c3x_hrnet_swad_v11_f0_s5\.swad\.tta_d4)\|' $IO/rendered.txt | cut -c1-260;;
place)
  [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  case "$MAXC" in ''|*[!0-9]*) no "MAXC must be a whole number";; esac
  R "test ! -e $Q && echo FREE" | grep -qx FREE || no "$Q exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $Q; jobs.txt (md5 $J, $(wc -l < $IO/jobs.txt) lines, r--r--r--); LPG 1; MAXC $MAXC; SHARE_TRAIN $ST; SHARE_DUMP $SD"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && echo 1 > $Q/LPG && echo $MAXC > $Q/MAXC && echo $ST > $Q/SHARE_TRAIN && echo $SD > $Q/SHARE_DUMP && md5sum < $Q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/place_md5.txt || no "placing failed"
  [ "$(cat $IO/place_md5.txt)" = "$J" ] || no "placed jobs.txt md5 differs"
  say "placed $Q: jobs.txt md5 $J, LPG 1, MAXC $MAXC, SHARE_TRAIN $ST, SHARE_DUMP $SD (not armed)";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard5' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard5.sh && md5sum < $BQ/diskguard5.sh | cut -c1-32")
  case "$s" in *RUNNING*) no "tmux bench_diskguard5 already runs on cv02";; esac
  [ -z "$s" ] || [ "$s" = "$GUARD_MD5" ] || no "cv02 $BQ/diskguard5.sh exists with another md5 ($s)"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: place $BQ/diskguard5.sh (md5 $GUARD_MD5), tmux new-session -d -s bench_diskguard5 'bash $BQ/diskguard5.sh'"; exit 0; fi
  if [ -z "$s" ]; then ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $BQ/diskguard5.sh && cat > $BQ/diskguard5.sh" < $HERE/diskguard5.sh || no "placing diskguard5.sh failed"; fi
  [ "$(R "md5sum < $BQ/diskguard5.sh | cut -c1-32")" = "$GUARD_MD5" ] || no "cv02 diskguard5.sh md5 differs"
  Wr "tmux new-session -d -s bench_diskguard5 'bash $BQ/diskguard5.sh' && sleep 2 && tail -1 $BQ/diskguard5.log"
  say "disk guard 5 started (covers fin; stop file $BQ/DISKGUARD5_STOP)";;
arm)
  need_f; [ -s $IO/jobs.txt ] || no "no $IO/jobs.txt"; J=$(cat $IO/jobs.md5)
  case "$GAPSEC" in ''|*[!0-9]*) no "GAPSEC must be a whole number";; esac; [ "$GAPSEC" -ge 30 ] || no "GAPSEC below 30"
  [ -s $IO/render_cmp.out ] && grep -q "render compare: 0 FAIL" $IO/render_cmp.out || no "no passed 'render' in $IO"
  # 1. no other live queue can start training
  o=$(qscan) || no "ssh failed"
  echo "$o"; case "$o" in *CAN_START*) no "another queue can still start training";; esac
  # 2. the placed queue dir, the deploy, the data, the full-pool root, the source runs
  o=$(R "cd $Q && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) LPG \$(cat LPG) MAXC \$(cat MAXC) share \$(cat SHARE_TRAIN 2>/dev/null)/\$(cat SHARE_DUMP 2>/dev/null) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_$NEWQ' 2>/dev/null && echo yes || echo no) data \$(md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32)\"") || no "ssh failed"
  [ "$o" = "jobs $J LPG 1 MAXC $MAXC share $ST/$SD used 0 ses no data $DATA_MD5" ] || no "queue dir or data check: $o"
  echo "queue dir $Q: jobs md5, LPG 1, MAXC $MAXC, SHARE_TRAIN $ST, SHARE_DUMP $SD, unused; data $DATA_MD5"
  fb_check; root_check; src_check
  # 3. disk and its guard; no HOLD in fin (HOLD files of finished queues are theirs and are not touched)
  o=$(R "a=\$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9); echo \"free \$a guard \$(tmux has-session -t '=bench_diskguard5' 2>/dev/null && echo yes || echo no) \$(md5sum < $BQ/diskguard5.sh 2>/dev/null | cut -c1-32) hold \$(test -e $Q/HOLD && echo 1 || echo 0)\"") || no "ssh failed"
  set -- $o; echo "cv02: $o"
  [ "${4:-}" = yes ] && [ "${5:-}" = "$GUARD_MD5" ] || no "disk guard 5 is not running with the reviewed script (run 'guard')"
  [ "${7:-}" = 0 ] || no "$Q/HOLD exists"
  need=39
  echo "disk need (S): 5 candidate runs x 1.0 GB + 5 PF runs x 0.62 GB that stay (latest.pth for the opening) + 75 D4 dumps x 0.14 GB until relayed and removed + the 20 GB guard floor = about $need GB; free ${2:-?} GB"
  if [ "${2:-0}" -lt "$need" ] 2>/dev/null; then
    [ "${DISK_OK:-0}" = 1 ] || no "cv02 /tmp free ${2:-?} GB < $need GB needed to finish fin without a HOLD (free space first, or DISK_OK=1: disk guard 5 then HOLDs fin at 20 GB free, which stops new training starts AND dump starts)"
    echo "DISK_OK=1: arming with ${2:-?} GB free < $need GB; disk guard 5 will HOLD fin at 20 GB free"
  fi
  A="B=$FB Q=$Q SES=bench_q_$NEWQ DEPLOY=$F JOBS_MD5=$J DATA_MD5=$DATA_MD5 GAPSEC=$GAPSEC bash $FB/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, pre-checks passed; not run on cv02: $A"; exit 0; fi
  R "$A" | tee $IO/arm.out
  grep -q "cq_setup: bench_q_$NEWQ armed: gpumem [0-9]* queue [0-9]*" $IO/arm.out || no "arming not confirmed (see $IO/arm.out)"
  t=0; a=""
  while [ $t -lt ${ARMWAIT:-300} ]; do a=$(R "grep -m1 -E 'cv02 q armed:|; not starting' $Q/launch.log" 2>/dev/null); [ -n "$a" ] && break; sleep 10; t=$((t+10)); done
  echo "$a" | cut -c1-400
  case "$a" in *"cv02 q armed:"*) ;;
    *"; not starting"*) no "cq.sh did NOT arm: '${a#*] }'. Nothing of fin runs; see $Q/launch.log";;
    *) no "no 'cv02 q armed:' line in $Q/launch.log after $t s: arming is NOT confirmed; look at $Q/launch.log and the tmux session bench_q_$NEWQ";; esac
  echo "$a" | grep -q "SHARE_TRAIN $ST MiB, SHARE_DUMP $SD MiB" || echo "WARNING: the armed line does not show SHARE_TRAIN $ST and SHARE_DUMP $SD: the queue runs by the strict rule only"
  echo "$a" | grep -q "gap $GAPSEC s" || echo "WARNING: the armed line does not show gap $GAPSEC s"
  say "armed bench_q_$NEWQ ('cv02 q armed:' line seen; $(echo "$a" | grep -o "sharing .*"); $Q; jobs $J; B = QC = $FB). Owed: at the first start 'fin_hrnet_swad_v11_pool_s5 config OK (= card)' and 'startup line OK: Labelled: 532 ...  val: 107  test: 107'; relay: FB=$FB bash $HERE/final_relay.sh";;
status)
  R "echo \"cv02 \$(date -u '+%F %T') UTC; free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD in fin: \$(test -e $Q/HOLD && echo yes || echo no)\"; d=$Q; [ -d \$d ] || { echo \"$NEWQ: no dir\"; exit 0; }; echo \"$NEWQ: MAXC \$(cat \$d/MAXC 2>/dev/null) started \$(ls \$d/pids/*.gpu 2>/dev/null | wc -l) ended \$(ls \$d/pids/*.end 2>/dev/null | wc -l) of \$(grep -c . \$d/jobs.txt) dispatched-all \$(grep -c 'all jobs dispatched' \$d/launch.log 2>/dev/null) RUN.md5 \$(ls $FB/runs/*/RUN.md5 2>/dev/null | wc -l) dumped-rc0 \$(grep -c 'dumped dump_.* rc=0:' \$d/launch.log 2>/dev/null) trained-rc0 \$(grep -c 'trained fin_.* rc=0 ' \$d/launch.log 2>/dev/null)\"; for f in \$d/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e \$d/pids/\$n.end ] || echo \"  open: \$n GPU \$(cat \$f) rc \$(cat \$d/pids/\$n.rc 2>/dev/null || echo running)\"; done; grep -E 'FAIL|HOLD|not starting|Traceback lines [1-9]' \$d/launch.log 2>/dev/null | tail -3; true";;
*) no "unknown step";;
esac
