#!/bin/bash
# x4 queue driver (run on gaint; every cv02 command over ssh -a, BatchMode). Reuses the reviewed cv02 queue of the c3 waves
# (cq.sh / cq_setup.sh / cq_gpumem.sh / slim_ckpt.py of the x4 deploy XB; the only change from the COMBO commit 03375d4 is
# LPG up to 3), the reviewed relay (relay_w1c.sh 74a2ec3d from the gaint stage copy of the x4 commit) and the frozen scorer.
#   X4  = full x4 commit (default below); XB = /tmp/noob_el/bench_<X4 7 hex> on cv02 (made by c3base/c3_deploy.sh X4).
#   QN  = queue name; queue dir /tmp/noob_el/bench_q/x4_<QN> on cv02, tmux bench_q_x4_<QN> on cv02,
#         relay dir /home/noob/work/bench_relay/x4_<QN> and tmux bench_relay_x4_<QN> on gaint.
# Lane rule (cq.sh, checked live before EVERY start, training or dump): a GPU qualifies only if no other user holds more than
#   4,096 MiB on it in sum, fewer than LPG of our runs are on it, free >= the job's gate (measured peak + 2,048), 120 s since
#   our last start, no HOLD, MAXC not reached. Sharing (lane rule v2) stays OFF: no SHARE_TRAIN / SHARE_DUMP file is written.
#   PID files (python PID + cmdline) in pids/; stop only by recorded PID (see LAUNCH_REQUEST_x4.md).
# Subcommands:
#   place QN JOBS [LPG] [MAXC]  cv02 WRITE: queue dir with jobs.txt (read-only), LPG (default 3), MAXC (default 15). Not armed.
#   append QN JOBS              cv02 WRITE: Q/append/<time>_<file>.txt, then its .md5 (cq_x4.sh queues accept it, log
#                               "appended ..." or "append ... REFUSED"; this command waits up to 5 min for that line).
#   close QN                    cv02 WRITE: Q/CLOSE (cq_x4.sh: no more appends; the queue ends after its last run).
#   arm QN                      cv02 START: cq_setup.sh with CQ=cq_x4.sh (default; CQ=cq.sh for a closed list), QC = XB
#                               (session bench_q_x4_<QN>). Lists other live queues of ours (info only, team lane rule)
#                               on cv02 can still start training (never two queues that can start), or HOLD exists.
#   status QN                   cv02 read: starts, trainings, dumps, RUN.md5, open runs, HOLD, lanes; disk.
#   hold QN | unhold QN         cv02 WRITE: touch / rm the HOLD file (no new start; running runs go on).
#   guard                       cv02 START: disk guard (HOLD in every x4_* queue below 20 GB free on /tmp), tmux bench_diskguard_x4.
#   relay QN N                  gaint START: x4_relay.sh (relay_w1c.sh + skip slim.pth + disk guard 15 GB), tmux bench_relay_x4_<QN>.
#   score QN                    gaint CPU: frozen scorer bench_score.py records for every relayed dump folder (once per folder).
# DRY=1 prints cv02 writes / starts instead of doing them.
set -u
X4=${X4:-c4e604e64d426ad6c9013418086f665fda386175}; XB=/tmp/noob_el/bench_${X4:0:7}; BQ=/tmp/noob_el/bench_q
DATA_MD5=d6063fd83d20e656612540edda702cbe; C=cv02@10.8.1.106; DRY=${DRY:-0}
ST=/home/noob/work/bench_c3_io/stage/bench_${X4:0:7}; RLY=/home/noob/work/bench_relay; FLOOR=${FLOOR:-16}
P=/home/noob/work/el-fault-detection/.venv/bin/python; RT=/home/noob/work/bench_wt_final
R(){ ssh -n -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
no(){ echo "REFUSED: $*"; exit 1; }
cmd=${1:-}; QN=${2:-}
[ -n "$cmd" ] || { sed -n '2,25p' "$0"; exit 1; }
case "$cmd" in guard) ;; *) echo "$QN" | grep -qE '^[a-z0-9]+$' || no "queue name must be [a-z0-9]+";; esac
Q=$BQ/x4_$QN; SES=bench_q_x4_$QN
case "$cmd" in
place)
  J=${3:?jobs.tsv}; LPG=${4:-3}; MAXC=${5:-15}
  case "$LPG" in 1|2|3) ;; *) no "LPG 1, 2 or 3";; esac
  [ -s "$J" ] || no "$J empty"; JM=$(md5sum < $J | cut -c1-32)
  [ -f "$J.md5" ] && [ "$(head -1 $J.md5 | cut -c1-32)" = "$JM" ] || no "$J.md5 missing or not the md5 of $J (make it with x4_make_jobs.py)"
  if [ $DRY = 1 ]; then echo "DRY: mkdir $Q; jobs.txt md5 $JM ($(grep -c . $J) lines, r--r--r--); LPG $LPG; MAXC $MAXC; no SHARE files"; exit 0; fi
  o=$(ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $Q && mkdir -p $Q && cat > $Q/jobs.txt && chmod a-w $Q/jobs.txt && echo $LPG > $Q/LPG && echo $MAXC > $Q/MAXC && md5sum < $Q/jobs.txt | cut -c1-32" < $J) || no "placing failed (exists?)"
  [ "$o" = "$JM" ] || no "cv02 jobs.txt md5 $o != $JM"
  echo "placed $Q: jobs.txt md5 $JM, LPG $LPG, MAXC $MAXC, sharing off (not armed)";;
arm)
  o=$(R "for q in $BQ/*/; do n=\$(basename \$q); [ \$n = x4_$QN ] && continue; p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; [ \"\$(cat \$q/MAXC 2>/dev/null)\" = 0 ] && continue; grep -q 'cv02 q: all jobs dispatched' \$q/launch.log && continue; echo CAN_START \$n; done; true")
  [ -z "$o" ] || echo "INFO: other live queues of ours can start training: $o (team lane rule of cq_x4.sh: their runs count toward LPG, not as other users)"
  J=$(R "md5sum < $Q/jobs.txt | cut -c1-32; test -e $Q/HOLD && echo HOLD; true") || no "ssh failed"
  case "$J" in *HOLD*) no "$Q/HOLD exists";; esac
  A="B=$XB QC=$XB CQ=${CQ:-cq_x4.sh} Q=$Q SES=$SES DEPLOY=$X4 JOBS_MD5=$J DATA_MD5=$DATA_MD5 bash $XB/bench/q/cv02/cq_setup.sh"
  if [ $DRY = 1 ]; then echo "DRY: on cv02: $A"; exit 0; fi
  R "$A" | tee /tmp/x4_arm_$QN.out
  for t in 5 10 20 40; do sleep $t; a=$(R "grep -E 'cv02 q (\(x4, open until CLOSE\) )?armed:' $Q/launch.log | tail -1"); [ -n "$a" ] && break
    f=$(R "grep 'not starting' $Q/launch.log | tail -1"); [ -n "$f" ] && no "cq.sh refused: $f"; done
  [ -n "$a" ] && echo "ARMED: $a" || no "no 'cv02 q armed:' line in $Q/launch.log: look at it and at tmux $SES on cv02";;
status)
  R "echo \"cv02 \$(date '+%F %T'); /tmp free \$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9) GB; HOLD \$(test -e $Q/HOLD && echo YES || echo no)\"
     L=$Q/launch.log; echo \"starts \$(grep -c '] start x4\\|] start smoke' \$L) configOK \$(grep -c 'config OK' \$L) startupOK \$(grep -c 'startup line OK: Labelled' \$L) trained_rc0 \$(grep -c 'trained .* rc=0 ' \$L) trained_other \$(grep 'trained ' \$L | grep -vc 'rc=0 ') dumped_rc0 \$(grep -c 'dumped dump_.* rc=0:' \$L) RUN.md5 \$(grep -c '^.*RUN.md5 .* rc=0' \$L) of \$(grep -c . $Q/jobs.txt) jobs; done line \$(grep -c 'BENCH CV02 Q ALL DONE' \$L)\"
     for f in $Q/pids/*.gpu; do [ -e \$f ] || continue; n=\$(basename \$f .gpu); [ -e $Q/pids/\$n.end ] || echo \"  open \$n GPU \$(cat \$f) pid \$(cat $Q/pids/\$n.pid 2>/dev/null) rc \$(cat $Q/pids/\$n.rc 2>/dev/null || echo running)\"; done
     grep -E 'FAIL|HOLD|Traceback|not starting' \$L | tail -3; tail -2 \$L
     nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader | tr '\n' ';'; echo";;
append)
  J=${3:?jobs file}; [ -s "$J" ] || no "$J empty"; JM=$(md5sum < $J | cut -c1-32)
  [ -f "$J.md5" ] && [ "$(head -1 $J.md5 | cut -c1-32)" = "$JM" ] || no "$J.md5 missing or not the md5 of $J (make it with x4_make_jobs.py)"
  tag=$(date +%Y%m%d_%H%M%S)_$(basename $J .tsv | tr -c 'a-z0-9_\n' '_')
  if [ $DRY = 1 ]; then echo "DRY: $Q/append/$tag.txt ($(grep -c . $J) lines, md5 $JM) then $tag.md5"; exit 0; fi
  o=$(ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test -d $Q/append && test ! -e $Q/CLOSE && test ! -e $Q/append/$tag.txt && cat > $Q/append/$tag.txt && chmod a-w $Q/append/$tag.txt && m=\$(md5sum < $Q/append/$tag.txt | cut -c1-32) && [ \$m = $JM ] && echo \$m > $Q/append/$tag.md5.tmp && mv $Q/append/$tag.md5.tmp $Q/append/$tag.md5 && echo \$m" < $J) || no "placing the append file failed (queue dir not a cq_x4 queue, CLOSE set, or md5 differs)"
  echo "placed $Q/append/$tag.txt md5 $o; waiting for the queue's verdict"
  for t in $(seq 1 30); do sleep 10; a=$(R "grep -E 'append(ed append/)? ?$tag' $Q/launch.log | tail -1"); [ -n "$a" ] && break; done
  echo "${a:-no verdict line within 5 min (the queue checks appends at each poll and while a job waits for a lane)}";;
close) [ $DRY = 1 ] && { echo "DRY: touch $Q/CLOSE"; exit 0; }; R "test -d $Q/append && touch $Q/CLOSE && echo CLOSE set in $Q";;
hold) [ $DRY = 1 ] && { echo "DRY: touch $Q/HOLD"; exit 0; }; R "test -d $Q && touch $Q/HOLD && echo HOLD set in $Q";;
unhold) [ $DRY = 1 ] && { echo "DRY: rm $Q/HOLD"; exit 0; }; R "test -d $Q && rm -f $Q/HOLD && echo HOLD removed in $Q";;
guard)
  s=$(R "tmux has-session -t '=bench_diskguard_x4' 2>/dev/null && echo RUNNING"); [ -z "$s" ] || no "bench_diskguard_x4 already runs"
  G='set -u; L=/tmp/noob_el/bench_q/diskguard_x4.log; echo "[$(date "+%F %T")] diskguard_x4 start pid $$ (floor 20 GB; queues x4_*)" >> $L
while [ ! -e /tmp/noob_el/bench_q/DISKGUARD_X4_STOP ]; do a=$(df --output=avail -BG /tmp | tail -1 | tr -dc 0-9)
  if [ -n "$a" ] && [ "$a" -lt 20 ]; then for q in /tmp/noob_el/bench_q/x4_*; do [ -d $q ] && [ ! -e $q/HOLD ] && touch $q/HOLD && echo "[$(date "+%F %T")] HELD $(basename $q): free ${a} GB < 20" >> $L; done; fi
  sleep 300; done; echo "[$(date "+%F %T")] stop file seen; exit" >> $L'
  [ $DRY = 1 ] && { echo "DRY: place $BQ/diskguard_x4.sh and start tmux bench_diskguard_x4"; exit 0; }
  printf '%s\n' "$G" | ssh -a -o BatchMode=yes $C "test ! -e $BQ/diskguard_x4.sh && cat > $BQ/diskguard_x4.sh && tmux new-session -d -s bench_diskguard_x4 'bash $BQ/diskguard_x4.sh' && sleep 2 && tail -1 $BQ/diskguard_x4.log" || no "guard start failed (script exists?)";;
relay)
  N=${3:?number of runs}; RD=$RLY/x4_$QN; RS=bench_relay_x4_$QN
  tmux has-session -t "=$RS" 2>/dev/null && no "tmux $RS exists"
  [ -e $RD ] && no "$RD exists"
  a=$(df --output=avail -BG /home/noob/work | tail -1 | tr -dc 0-9); [ "${a:-0}" -ge "$FLOOR" ] || no "gaint free ${a:-?} GB < $FLOOR"
  mkdir -p $RD && tmux new-session -d -s $RS "B=$XB Q=$Q RD=$RD N=$N NAMES_RX='^(x4|smoke_x4)_' POLL=${POLL:-120} FLOOR=${RFLOOR:-15} bash $(dirname $(readlink -f $0))/x4_relay.sh" && sleep 3
  echo "relay $RS started (gaint free $a GB): $(tail -1 $RD/relay.log)";;
score)
  RD=$RLY/x4_$QN; [ -d $RD/.ok ] || no "$RD is not a relay dir"
  for ok in $RD/.ok/*; do n=$(basename $ok); case "$n" in *.refused) continue;; esac
    for d in $RD/$n/dumps/elbench1/*/*/cv5v3_f[0-4]; do [ -d "$d" ] || continue; dn=$(basename $(dirname $d)); s=$(basename $d)
      o=$RD/$n/score/$dn.$s.rec.json; [ -e $o ] && continue; mkdir -p $RD/$n/score
      (cd $RT && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $P scripts/bench_score.py records --dumps $d --set $s --labels v11 --out $o > $o.log 2>&1); rc=$?
      echo "score $dn $s rc=$rc -> $o ($(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(len(d.get('cells', {})), 'cells')" $o 2>/dev/null))"; done; done;;
*) no "unknown subcommand $cmd";;
esac
