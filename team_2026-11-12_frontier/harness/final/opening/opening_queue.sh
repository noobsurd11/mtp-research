#!/bin/bash
# Sealed-set opening queue `open` on cv02 (OPENING_RULE.md section 9 step 4; run by the LEAD on gaint AFTER the review, the
# registration (opening_register.sh; ledger rows written) and the deploy of G). Pattern: harness/final/final_queue.sh (e574e25f).
# One NEW queue `open` of dump-only jobs only (20 or 30 lines, IO/jobs.txt of the registration): the full-pool runs' latest.pth
# (fin repaired by the resume queue fin2: run dirs in F2B = /tmp/noob_el/bench_9967d59, steps 1 to 18,000 under F, the rest
# under F2; FINAL_RULE_ADDENDUM_1.md) dumped on e1_106 and test50 by G's code (GB), cq.sh sealed-opening mode (Q/SEALED: the two
# opening names and the md5 of the staged images' MANIFEST). Strict lanes only (no SHARE file: one process of ours per GPU,
# our other queues count as another user), LPG 1, MAXC 4 (default), GAPSEC 30. It cannot start a training run (cq.sh refuses a
# training line in a sealed queue), so it never makes two queues that can train.
# One step per call, in this order. Each step refuses rather than guess, and prints what it did.
#   check   cv02 READ ONLY: GB = deploy of G (REVISION, CODE.md5, pins; its CODE.md5 differs from FB's only in G's 4 paths);
#           the 10 full-pool runs in F2B: config_used.yaml and latest.pth present, md5 of latest.pth = the LATEST.md5 of fin2's
#           relay (RF = /mnt/nas/noob_el_archive/bench_relay/fin2, 'RELAY ALL DONE: 10 of 10'), 'trained <run> rc=0' for all 10
#           and 'BENCH CV02 Q ALL DONE' in fin2's launch.log (the opening starts only after fin2 and its relay ended; REVIEW_FIN2
#           N3); FB (deploy of F) stays G's code reference; the pool root pins; no job name in use (GB dumps / runs, any queue's
#           pids, gaint relay dirs).
#   stage   cv02 WRITE (one new dir DS=/tmp/noob_el/bench_data_sealed): IO/stage (images and lists only) streamed by tar;
#           md5sum -c of MANIFEST.md5 on cv02, md5 of MANIFEST.md5 = the registered stage_manifest; files read-only.
#   render  cv02 WRITE (a new scratch queue dir): render-only run of GB's cq.sh on IO/jobs.txt with the SEALED file (it stops
#           at the logger check; nothing starts); opening_rendercmp.py must print 'render compare: 0 FAIL'.
#   place   cv02 WRITE: Q=/tmp/noob_el/bench_q/open with jobs.txt and SEALED (read-only), LPG 1, MAXC. Not armed.
#   guard   cv02 WRITE + START (review round 1, N7): disk guard 7 (diskguard7.sh = diskguard5.sh for queue open; tmux
#           bench_diskguard7; HOLD in open below 20 GB free; renamed from 6, which fin2 uses: REVIEW_FIN2 N2). fin's disk guard 5
#           and fin2's disk guard 6 are not touched.
#   arm     cv02 START: pre-checks (render passed; Q placed and unused; check passes again; DS manifest; disk guard 7 running
#           with the reviewed script; free >= 35 GB), then GB's cq_setup.sh (session bench_q_open, GAPSEC 30); 'armed' only
#           with the 'cv02 q armed:' line in Q/launch.log.
#   status  cv02 READ ONLY.
#   unstage cv02 WRITE (review round 1, N6 / N7), after RELAY ALL DONE (the read first, as the procedure says): (1) removes
#           the sealed dumps from GB/dumps: for every job, gaint checks its relayed copy in RD (md5sum -c of RUN.md5 and
#           md5(RUN.md5) = the .ok line), then on cv02 md5(GB/runs/<job>/RUN.md5) must equal it, md5sum -c of every listed
#           file must pass (each cv02 file = its verified relayed copy), and exactly one dump dir with exactly the listed file
#           count must exist; only then that dir is removed (pattern of harness/c3base/c3_f81_list.sh d640ffe8; log
#           /tmp/noob_el/removed_relayed_dumps_open.log); runs/<job>/RUN.md5 (hashes only) stays; (2) removes DS (only if it
#           holds exactly the files of its MANIFEST.md5). No sealed image or prediction then stays on cv02.
# DRY=1: every cv02 write or start is printed, not run; read-only checks run.
# Env: G (full commit of G), IO (default /home/noob/work/bench_open_io), MAXC (place; default 4), GAPSEC (arm; >= 30),
#   RD (unstage: the relay dir; default /mnt/nas/noob_el_archive/bench_relay/open, as opening_relay.sh and run_opening_read.sh).
set -u
STEP=${1:?step: check | stage | render | place | guard | arm | status | unstage}
NEWQ=open; IO=${IO:-/home/noob/work/bench_open_io}; DRY=${DRY:-0}; G=${G:-}; GAPSEC=${GAPSEC:-30}; MAXC=${MAXC:-4}
GC=8bd1c2761c85f4721e444a8bf7124d2e5804973a; FC=821dfadf49116cc6d5fdbd6697e263dd7cf0f834
FB=/tmp/noob_el/bench_821dfad; BQ=/tmp/noob_el/bench_q; Q=$BQ/$NEWQ; DS=/tmp/noob_el/bench_data_sealed
F2B=/tmp/noob_el/bench_9967d59; QF=$BQ/fin2   # the full-pool runs (fin2 resume deploy of F2 9967d59) and fin2's queue dir
DF=/tmp/noob_el/bench_data_fin; DFR=$DF/roots/pool532_v11; DATA_MD5=d6063fd83d20e656612540edda702cbe
RF=/mnt/nas/noob_el_archive/bench_relay/fin2   # fin2's relay (REVIEW_FIN2 N5): LATEST.md5 of the 10 full-pool runs
GUARD7_MD5=$(md5sum < $(dirname "$(readlink -f "$0")")/diskguard7.sh | cut -c1-32); [ "$GUARD7_MD5" = 1771e3fc339026387694cd3951bd5226 ] || { echo "REFUSED: diskguard7.sh is not 1771e3fc339026387694cd3951bd5226"; exit 1; }
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python
RUNS="fin_hrnet_swad_v11_pool_s5 fin_hrnet_swad_v11_pool_s6 fin_hrnet_swad_v11_pool_s7 fin_hrnet_swad_v11_pool_s8 fin_hrnet_swad_v11_pool_s9 fin_pf_v11_pool_s5 fin_pf_v11_pool_s6 fin_pf_v11_pool_s7 fin_pf_v11_pool_s8 fin_pf_v11_pool_s9"
PINS="6371dc5694dcb36665c989f27aaa5991  bench/q/cv02/cq.sh
54256ac9992fefffe039d8b7207cd857  bench/q/cv02/cq_setup.sh
2a5f688160eb100eb0bc9784ffe06e7e  bench/q/cv02/cq_gpumem.sh
f3affc80b21406644cedbc80d6e250ba  bench/q/cv02/cvcard.py
1af2ed69babf72e9d0d0aa789eb71121  bench/q/bench_lib.sh
a3268638d91937223433cd88d2d97df6  scripts/bench_infer.py
801ff5228c14476968627bbdbff3253e  bench/tta.py
2dd0eb57348eb8d35b4ca0b4ed62efc8  bench/sets.py
306b2c7b595fa8e3f45d6fc51bf7bf7e  bench/dumpfmt.py
98f152de3ea7f8c88e892162e07b4450  bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
d7b207089f6cfeb484ca9ef96f734786  bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
a4a46a526cf14d649f3176edd53a9c32  bench/methods/house_r34_unetpp_pf_v11.yaml
bbdef88b2a5e6dde5e01ffaf23ba0d2b  bench/methods_cv02/house_r34_unetpp_pf_v11.yaml"
DW="<bench/q/cv02/cq.sh <scripts/bench_infer.py >bench/q/cv02/cq.sh >scripts/bench_infer.py >tests/test_bench_cq_sealed.py >tests/test_bench_infer_sealed.py "
ROOTPINS="d374fd843598f10fd4ba9101435986c8  splits/train.txt
79816ba63cca96e10265197eb4cfa905  splits/test.txt
cec1396e24b35c8bb0001de19f7d0c3b  SPLITS.md5
33e65b3f5ec964336d44583dcdfe6352  DATA_MANIFEST.md5"
C=cv02@10.8.1.106
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
Wr(){ if [ $DRY = 1 ]; then echo "DRY, not run on cv02: $1"; else ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; fi; }
no(){ echo "REFUSED ($STEP): $*"; exit 1; }
say(){ echo "[$(date '+%F %T')] $STEP: $*" | tee -a $IO/queue.log; }
[ -s $IO/REGISTERED.txt ] && [ -s $IO/jobs.txt ] || no "no registration in $IO (run opening_register.sh first)"
[ "$(md5sum < $IO/REGISTERED.txt | cut -c1-32)" = "$(cat $IO/REGISTERED.md5)" ] || no "REGISTERED.txt md5 differs from REGISTERED.md5"
J=$(cat $IO/jobs.md5); [ "$(md5sum < $IO/jobs.txt | cut -c1-32)" = "$J" ] || no "jobs.txt md5 differs from the registration"
grep -q "^jobs $J " $IO/REGISTERED.txt || no "the registration names another job list"
SMAN=$(awk '/^stage_manifest /{print $2}' $IO/REGISTERED.txt)
NJ=$(grep -c . $IO/jobs.txt)
GB=/tmp/noob_el/bench_${GC:0:7}
need_g(){ [ "$G" = $GC ] || no "G must be the full commit $GC"
  grep -q "^commits F $FC G $GC " $IO/REGISTERED.txt || no "the registration names another G"
  [ "$(git -C /home/noob/work/bench_wt_openg rev-parse $G^1 2>/dev/null)" = $FC ] || no "G's parent is not F"; }
gb_check(){ local out d; out=$(R "cd $GB && echo \"rev \$(cat REVISION)\"; md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; echo \"$PINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo PINS_OK; (cd $FB && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) && echo FB_OK; diff <(grep -v '  REVISION\$' $FB/CODE.md5) <(grep -v '  REVISION\$' CODE.md5) | grep '^[<>]' | awk '{print \$1 \$3}' | LC_ALL=C sort | tr '\n' ' '") || no "ssh failed"
  case "$out" in "rev $G"*) ;; *) no "GB $GB REVISION is not G";; esac
  case "$out" in *CODE_OK*) ;; *) no "GB CODE.md5 check failed";; esac
  case "$out" in *PINS_OK*) ;; *) no "GB files do not match the pinned md5s";; esac
  case "$out" in *FB_OK*) ;; *) no "FB (deploy of F) CODE.md5 check failed";; esac
  d=$(echo "$out" | tail -1); [ "$d" = "$DW" ] || no "GB differs from FB in other paths than G's 4: $d"
  echo "GB $GB: REVISION G, CODE.md5 OK, pins OK; differs from FB only in G's 4 paths (+ REVISION)"; }
fin_check(){ local o n bad=""; o=$(R "cd $F2B && for r in $RUNS; do printf '%s ' \$r; test -s experiments/\$r/config_used.yaml && md5sum < experiments/\$r/checkpoints/latest.pth | cut -c1-32 || echo MISSING; done; echo; for r in $RUNS; do grep -c \"trained \$r rc=0 \" $QF/launch.log; done | tr '\n' ' '; echo; grep -c 'BENCH CV02 Q ALL DONE' $QF/launch.log") || no "ssh failed"
  for n in $RUNS; do
    l=$(echo "$o" | awk -v n=$n '$1 == n {print $2}')
    w=$(awk '{print $1}' $RF/$n/runs/$n/LATEST.md5 2>/dev/null)
    [ -n "$w" ] && [ "$l" = "$w" ] || bad="$bad $n(cv02 ${l:-?} relay ${w:-none})"
  done
  [ -z "$bad" ] || no "full-pool runs: latest.pth in $F2B missing or not fin2's relayed LATEST.md5:$bad"
  [ "$(echo "$o" | tail -2 | head -1)" = "1 1 1 1 1 1 1 1 1 1 " ] || no "fin2 launch.log lacks 'trained <run> rc=0' for some run: $(echo "$o" | tail -2 | head -1)"
  [ "$(echo "$o" | tail -1)" = 1 ] || no "fin2 has not ended ('BENCH CV02 Q ALL DONE' not in $QF/launch.log)"
  grep -q "RELAY ALL DONE: 10 of 10" $RF/relay.log 2>/dev/null || no "fin2's relay in $RF has not relayed all 10 runs"
  echo "full-pool runs: 10 of 10 in $F2B with latest.pth = fin2's relayed LATEST.md5, 'trained rc=0', fin2 ALL DONE, fin2 relay ALL DONE"; }
root_check(){ local o; o=$(R "cd $DFR 2>/dev/null && echo \"$ROOTPINS\" | md5sum -c --quiet - > /dev/null 2>&1 && echo ROOT_OK") || no "ssh failed"
  [ "$o" = ROOT_OK ] || no "$DFR pins failed"; echo "root $DFR: pins OK"; }
names_check(){ local hit; cut -d'|' -f1 $IO/jobs.txt > $IO/names.txt
  hit=$(R "for n in $(tr '\n' ' ' < $IO/names.txt); do ls -d /tmp/noob_el/bench_*/dumps/elbench1/*/\$n /tmp/noob_el/bench_*/runs/\$n $BQ/*/pids/\$n.gpu 2>/dev/null; done; true") || no "ssh failed"
  [ -z "$hit" ] || no "names already used on cv02: $(echo "$hit" | head -3 | tr '\n' ' ')"
  for n in $(cat $IO/names.txt); do ls -d /home/noob/work/bench_relay/*/$n 2>/dev/null; done > $IO/relay_hits.txt
  [ ! -s $IO/relay_hits.txt ] || no "names already in a gaint relay dir: $(head -3 $IO/relay_hits.txt | tr '\n' ' ')"
  echo "names: $NJ, none in use on cv02 or in a gaint relay"; }
ds_check(){ local o; o=$(R "cd $DS 2>/dev/null && md5sum -c --quiet MANIFEST.md5 > /dev/null 2>&1 && echo \"OK \$(md5sum < MANIFEST.md5 | cut -c1-32) \$(find . -type f | wc -l) \$(find . \\( -name masks -o -name ignore -o -name 'masks_*' \\) | wc -l)\"") || no "ssh failed"
  [ "$o" = "OK $SMAN 158 0" ] || no "cv02 $DS: manifest check, md5 (want $SMAN), 158 files and no mask dir expected; got '$o'"
  echo "DS $DS: 157 files + MANIFEST.md5 ($SMAN), md5sum -c OK, no mask or ignore dir"; }
sealed_file(){ printf 'e1_106 e1_open8_final\ntest50 t50_open19_final\nmanifest %s\n' "$SMAN"; }

case $STEP in
check)
  need_g; gb_check; fin_check; root_check; names_check
  say "check OK: GB, 10 fin runs, root, $NJ names free";;
stage)
  need_g; [ -s $IO/stage/MANIFEST.md5 ] || no "no $IO/stage"
  [ "$(md5sum < $IO/stage/MANIFEST.md5 | cut -c1-32)" = "$SMAN" ] || no "IO/stage/MANIFEST.md5 is not the registered $SMAN"
  (cd $IO/stage && md5sum -c --quiet MANIFEST.md5) || no "IO/stage md5sum -c failed"
  [ -z "$(find $IO/stage \( -name masks -o -name ignore -o -name 'masks_*' \) -print -quit)" ] || no "IO/stage holds a mask dir"
  R "test ! -e $DS && echo FREE" | grep -qx FREE || no "$DS exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: tar of $IO/stage (157 images and lists + MANIFEST.md5) into $DS, md5sum -c, chmod a-w"; exit 0; fi
  tar -C $IO/stage -cf - . | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $DS && mkdir $DS && tar -x -C $DS && find $DS -type f -exec chmod a-w {} +"; rc=${PIPESTATUS[0]}${PIPESTATUS[1]}
  [ "$rc" = 00 ] || no "stream rc $rc"
  ds_check; say "staged the sealed images on cv02 $DS (images and lists only; manifest $SMAN)";;
render)
  need_g; gb_check; ds_check
  W=/tmp/noob_el/bench_open_render/$(date +%Y%m%d_%H%M%S)
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $W/q; jobs.txt (md5 $J), LPG 1, SEALED; B=$GB Q=$W/q JOBS_MD5=$J DEPLOY=$G DATA_MD5=$DATA_MD5 nice -n 19 bash $GB/bench/q/cv02/cq.sh"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir -p $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && printf 'e1_106 e1_open8_final\ntest50 t50_open19_final\nmanifest $SMAN\n' > $W/q/SEALED && md5sum < $W/q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/render_md5.txt || no "placing the scratch list failed"
  [ "$(cat $IO/render_md5.txt)" = "$J" ] || no "scratch jobs.txt md5 differs"
  R "B=$GB Q=$W/q JOBS_MD5=$J DEPLOY=$G DATA_MD5=$DATA_MD5 nice -n 19 bash $GB/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $IO/render.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $IO/render.out || no "render did not reach the logger check (see $IO/render.out)"
  R "cat $W/q/jobs_rendered.txt" > $IO/rendered.txt || no "ssh failed"
  PYTHONDONTWRITEBYTECODE=1 $P $HERE/opening_rendercmp.py --jobs $IO/jobs.txt --rendered $IO/rendered.txt --b $GB | tee $IO/render_cmp.out
  [ ${PIPESTATUS[0]} = 0 ] || no "rendered lines do not match (see $IO/render_cmp.out)"
  say "render OK in cv02 $W: $NJ dump-only lines; templates and semantics 0 FAIL (the scratch dir may be removed: rm -r $W)";;
place)
  case "$MAXC" in ''|*[!0-9]*) no "MAXC must be a whole number";; esac; [ "$MAXC" -ge 1 ] && [ "$MAXC" -le 8 ] || no "MAXC 1 to 8"
  R "test ! -e $Q && echo FREE" | grep -qx FREE || no "$Q exists on cv02"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: mkdir $Q; jobs.txt (md5 $J, $NJ lines, r--r--r--); SEALED (r--r--r--: $(sealed_file | tr '\n' ' ')); LPG 1; MAXC $MAXC; no SHARE file"; exit 0; fi
  ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && printf 'e1_106 e1_open8_final\ntest50 t50_open19_final\nmanifest $SMAN\n' > $Q/SEALED && chmod a-w $Q/SEALED && echo 1 > $Q/LPG && echo $MAXC > $Q/MAXC && md5sum < $Q/jobs.txt | cut -c1-32" < $IO/jobs.txt > $IO/place_md5.txt || no "placing failed"
  [ "$(cat $IO/place_md5.txt)" = "$J" ] || no "placed jobs.txt md5 differs"
  say "placed $Q: jobs.txt md5 $J, SEALED (2 openings, manifest $SMAN), LPG 1, MAXC $MAXC, strict lanes (no SHARE file); not armed";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard7' 2>/dev/null && echo RUNNING; test -e $BQ/diskguard7.sh && md5sum < $BQ/diskguard7.sh | cut -c1-32")
  case "$s" in *RUNNING*) no "tmux bench_diskguard7 already runs on cv02";; esac
  [ -z "$s" ] || [ "$s" = "$GUARD7_MD5" ] || no "cv02 $BQ/diskguard7.sh exists with another md5 ($s)"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: place $BQ/diskguard7.sh (md5 $GUARD7_MD5), tmux new-session -d -s bench_diskguard7 'bash $BQ/diskguard7.sh'"; exit 0; fi
  if [ -z "$s" ]; then ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $BQ/diskguard7.sh && cat > $BQ/diskguard7.sh" < $HERE/diskguard7.sh || no "placing diskguard7.sh failed"; fi
  [ "$(R "md5sum < $BQ/diskguard7.sh | cut -c1-32")" = "$GUARD7_MD5" ] || no "cv02 diskguard7.sh md5 differs"
  Wr "tmux new-session -d -s bench_diskguard7 'bash $BQ/diskguard7.sh' && sleep 2 && tail -1 $BQ/diskguard7.log"
  say "disk guard 7 started (covers open; stop file $BQ/DISKGUARD7_STOP)";;
arm)
  need_g
  case "$GAPSEC" in ''|*[!0-9]*) no "GAPSEC must be a whole number";; esac; [ "$GAPSEC" -ge 30 ] || no "GAPSEC below 30"
  [ -s $IO/render_cmp.out ] && grep -q "render compare: 0 FAIL" $IO/render_cmp.out || no "no passed 'render' in $IO"
  o=$(R "cd $Q && echo \"jobs \$(md5sum < jobs.txt | cut -c1-32) sealed \$(md5sum < SEALED | cut -c1-32) LPG \$(cat LPG) MAXC \$(cat MAXC) share \$(ls SHARE_TRAIN SHARE_DUMP 2>/dev/null | wc -l) used \$(ls -d queue.pid gpumem.pid pids HOLD 2>/dev/null | wc -l)\$(test -s launch.log && echo +log) ses \$(tmux has-session -t '=bench_q_$NEWQ' 2>/dev/null && echo yes || echo no) data \$(md5sum < /tmp/noob_el/bench_data/DEPLOY.md5 | cut -c1-32)\"") || no "ssh failed"
  [ "$o" = "jobs $J sealed $(sealed_file | md5sum | cut -c1-32) LPG 1 MAXC $MAXC share 0 used 0 ses no data $DATA_MD5" ] || no "queue dir or data check: $o"
  gb_check; fin_check; root_check; ds_check
  g=$(R "tmux has-session -t '=bench_diskguard7' 2>/dev/null && echo yes || echo no; md5sum < $BQ/diskguard7.sh 2>/dev/null | cut -c1-32; test -e $Q/HOLD && echo HOLD || echo nohold") || no "ssh failed"
  [ "$(echo $g)" = "yes $GUARD7_MD5 nohold" ] || no "disk guard 7 not running with the reviewed script, or $Q/HOLD exists (run 'guard'): $(echo $g)"
  a=$(R "df --output=avail -BG /tmp | tail -1 | tr -dc 0-9") || no "ssh failed"
  echo "disk need (S): E1 10 logp dumps x about 1.0 GB + up to 10 other dumps x 0.14 GB + 20 GB floor = about 32 GB; free $a GB"
  [ "${a:-0}" -ge 35 ] || no "cv02 /tmp free ${a:-?} GB < 35 GB"
  A="B=$GB Q=$Q SES=bench_q_$NEWQ DEPLOY=$G JOBS_MD5=$J DATA_MD5=$DATA_MD5 GAPSEC=$GAPSEC bash $GB/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY, pre-checks passed; not run on cv02: $A"; exit 0; fi
  R "$A" | tee $IO/arm.out
  grep -q "cq_setup: bench_q_$NEWQ armed: gpumem [0-9]* queue [0-9]*" $IO/arm.out || no "arming not confirmed (see $IO/arm.out)"
  t=0; a=""
  while [ $t -lt ${ARMWAIT:-300} ]; do a=$(R "grep -m1 -E 'cv02 q armed:|; not starting' $Q/launch.log" 2>/dev/null); [ -n "$a" ] && break; sleep 10; t=$((t+10)); done
  echo "$a" | cut -c1-400
  case "$a" in *"cv02 q armed:"*) ;;
    *"; not starting"*) no "cq.sh did NOT arm: '${a#*] }'. Nothing of open runs; see $Q/launch.log";;
    *) no "no 'cv02 q armed:' line in $Q/launch.log after $t s: arming is NOT confirmed";; esac
  echo "$a" | grep -q "SHARE_TRAIN 0 MiB, SHARE_DUMP 0 MiB" || echo "WARNING: the armed line does not show sharing off"
  say "armed bench_q_$NEWQ ($Q; jobs $J; B = QC = $GB; strict lanes). Owed: 'dump-only fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106 on GPU g', 'dumped dump_... rc=0', 'RUN.md5 ... (dump-only)'; relay: G=$G bash $HERE/opening_relay.sh";;
status)
  R "echo \"cv02 \$(date -u '+%F %T') UTC; free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD: \$(test -e $Q/HOLD && echo yes || echo no)\"; d=$Q; [ -d \$d ] || { echo 'open: no dir'; exit 0; }; echo \"open: MAXC \$(cat \$d/MAXC 2>/dev/null) started \$(ls \$d/pids/*.gpu 2>/dev/null | wc -l) ended \$(ls \$d/pids/*.end 2>/dev/null | wc -l) of \$(grep -c . \$d/jobs.txt) dumped-rc0 \$(grep -c 'dumped dump_.* rc=0:' \$d/launch.log 2>/dev/null) RUN.md5 \$(ls $GB/runs/*/RUN.md5 2>/dev/null | wc -l)\"; grep -E 'FAIL|HOLD|not starting|Traceback lines [1-9]' \$d/launch.log 2>/dev/null | tail -3; true";;
unstage)
  RD=${RD:-/mnt/nas/noob_el_archive/bench_relay/open}
  grep -q "RELAY ALL DONE: $NJ of $NJ" $RD/relay.log 2>/dev/null || no "the relay in $RD has not relayed all $NJ dumps"
  ds_check
  # (1) the sealed dumps in GB/dumps: gaint verifies each relayed copy, cv02 verifies its own files against the same RUN.md5
  LIST=""
  for n in $(cut -d'|' -f1 $IO/jobs.txt); do
    m=$(awk '{print $4}' $RD/.ok/$n 2>/dev/null)
    [ -n "$m" ] && [ "$(md5sum < $RD/$n/runs/$n/RUN.md5 | cut -c1-32)" = "$m" ] || no "$n: relayed RUN.md5 missing or not the .ok md5"
    (cd $RD/$n && md5sum -c --quiet runs/$n/RUN.md5 > /dev/null 2>&1) || no "$n: gaint md5sum -c of the relayed copy failed"
    k=$(grep -cE "  dumps/elbench1/[A-Za-z0-9_]+/$n/" $RD/$n/runs/$n/RUN.md5)
    [ "$k" -gt 0 ] && [ "$k" = "$(grep -c . $RD/$n/runs/$n/RUN.md5)" ] || no "$n: RUN.md5 lists other files than its one dump dir"
    LIST="$LIST$n $m $k
"
  done
  echo "relayed copies verified on gaint: $(printf '%s' "$LIST" | grep -c .) of $NJ"
  SCR="B=$GB; n0=0; while read n m k; do f=\$B/runs/\$n/RUN.md5
  [ -f \$f ] && [ \"\$(md5sum < \$f | cut -c1-32)\" = \$m ] || { echo \"SKIP RUN.md5 \$n\"; continue; }
  (cd \$B && md5sum -c --quiet runs/\$n/RUN.md5 > /dev/null 2>&1) || { echo \"SKIP md5sum -c \$n\"; continue; }
  d=\$(ls -d \$B/dumps/elbench1/*/\$n 2>/dev/null); [ -n \"\$d\" ] && [ \"\$(echo \"\$d\" | wc -l)\" = 1 ] || { echo \"SKIP nodir \$n\"; continue; }
  [ \"\$(find \"\$d\" -type f | wc -l)\" = \$k ] || { echo \"SKIP count \$n\"; continue; }
  rm -rf -- \"\$d\" && n0=\$((n0+1)) && echo \"\$(date -u +%FT%T) removed \$d (\$k files = the verified relayed copy, RUN.md5 \$m)\" >> /tmp/noob_el/removed_relayed_dumps_open.log
  done; echo REMOVED_DUMPS \$n0"
  if [ $DRY = 1 ]; then echo "DRY, not run on cv02: per job md5(RUN.md5) = gaint's, md5sum -c, one dump dir with $NJ x its file count, then rm -rf of that dir; then rm -rf $DS"; exit 0; fi
  o=$(printf '%s' "$LIST" | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "bash -c '$SCR'") || no "ssh failed"
  echo "$o" | tail -5
  echo "$o" | grep -qx "REMOVED_DUMPS $NJ" || no "not every sealed dump dir was removed from $GB/dumps (see above; nothing else was touched)"
  # (2) the staged sealed images
  Wr "cd $DS && [ \"\$(find . -type f | wc -l)\" = 158 ] && cd /tmp && chmod -R u+w $DS && rm -rf $DS && echo REMOVED $DS"
  say "removed $NJ sealed dump dirs from $GB/dumps (each = its verified relayed copy in $RD) and the sealed images ($DS) from cv02";;
*) no "unknown step";;
esac
