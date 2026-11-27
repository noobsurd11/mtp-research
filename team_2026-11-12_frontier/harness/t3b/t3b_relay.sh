#!/bin/bash
# Relays of the T3b queues (run by the LEAD on gaint) = opening_relay.sh (4f2a28a3) with B = KB (the deploy of K) and, per mode,
# the queue, relay dir, job count and a NAMES_RX of exactly that queue's job names (review round 1 B1: the dump relay must
# never take the 33 training units, which are in KB/runs when it starts). Same reviewed relay script (stage copy of 89b9ea5,
# relay_w1c.sh 74a2ec3d), unchanged.
#   train        Q = bench_q/t3b, RD1 = /mnt/nas/noob_el_archive/bench_relay/t3b, N 33, session bench_relay_t3b,
#                NAMES_RX '^t3b_(all|half)_f[0-4]_s[5-7]$|^t3b_deploy_s[5-7]$' (a unit = RUN.md5 + config_used.yaml + slim.pth
#                (swad_bn, swad) + LATEST.md5 + enc_probe.jsonl; about 0.17 GB)
#   trainrep R   the same relay continued (RESUME) after repair queue R (bench_q/t3brep<R>, t3b_queue.sh repair steps; N1)
#   deploy       (round 1 N10) after 'RELAY ALL DONE: 33 of 33': copies checkpoints/latest.pth of t3b_deploy_s5..7 from KB into
#                RD1/<run>/experiments/<run>/checkpoints/ (cv02 read-only tar), each checked on gaint by md5sum -c of the
#                relayed runs/<run>/LATEST.md5; inline, no tmux; prints 'DEPLOY LATEST DONE: 3 of 3' (about 2.3 GB)
#   dump         Q = bench_q/t3bopen, RD2 = /mnt/nas/noob_el_archive/bench_relay/t3bopen, N 30, session bench_relay_t3bopen,
#                NAMES_RX '^t3b_(all|half)_f[0-4]_s[5-7]\.swad\.tta_d4\.e1t3b_f[0-4]$' (a unit = RUN.md5 + the one sealed D4
#                dump folder of 20 to 22 held-out E1 cells, no logp; about 25 MB)
# Refuses: its own md5 not the registered one (REGISTERED.txt 'scripts' line; round 1 B2); stage copy or relay script changed;
# the registration (REG_MD5) or K not as registered; session or RD exists (RESUME=1 continues); free space on RD's filesystem
# below FLOOR GB (default 25). RD may be set to a gaint dir if the NAS is down; then pass the same RD1 / RD2 to t3b_queue.sh and
# run_t3b_read.sh. SHOW=1 prints the command. Stop: touch <RD>/STOP.
# Test-only overrides: IO, RD1, RD2, POLL, FG (1 = run relay_w1c.sh in the foreground, no tmux). If any is set the script refuses
# unless TEST_MODE=1; then IO, RD1 and RD2 must be set, absolute and resolve under /home/noob/work/bench_int_io, `ssh` must be a
# stub under that dir, and the registration must be a TEST MODE one (a real one refuses TEST_MODE).
# Usage: REG_MD5=<md5> bash t3b_relay.sh train | trainrep <R> | deploy | dump
set -u
MODE=${1:?mode: train | trainrep R | deploy | dump}; SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}
OV=""; for v in IO RD1 RD2 POLL FG; do [ -n "${!v+x}" ] && OV="$OV $v=${!v}"; done
if [ -n "$OV" ] && [ "${TEST_MODE:-0}" != 1 ]; then echo "REFUSED: test-only overrides set:$OV (TEST_MODE=1 only for dry runs)"; exit 1; fi
SCR_ROOT=/home/noob/work/bench_int_io
tm_no(){ echo "REFUSED (TEST_MODE guard): $*"; exit 1; }
tm_in(){ local r; case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac; r=$(readlink -m -- "$1"); case "$r/" in "$SCR_ROOT"/*/*) ;; *) tm_no "$1 resolves to $r, outside $SCR_ROOT";; esac; }
if [ "${TEST_MODE:-0}" = 1 ]; then
  for v in IO RD1 RD2; do [ -n "${!v+x}" ] && [ -n "${!v}" ] || tm_no "$v must be set explicitly to a path under $SCR_ROOT (its default is a production path)"; done
  for p in "$IO" "$RD1" "$RD2" "$(command -v ssh)"; do tm_in "$p"; done
fi
REG_MD5=${REG_MD5:?REG_MD5}; IO=${IO:-/home/noob/work/bench_t3b_io}; POLL=${POLL:-300}; FG=${FG:-0}
RD1=${RD1:-/mnt/nas/noob_el_archive/bench_relay/t3b}; RD2=${RD2:-/mnt/nas/noob_el_archive/bench_relay/t3bopen}
KC=cba7fbdf5df1579d6efb1168eb292e637bc9fad6; KB=/tmp/noob_el/bench_${KC:0:7}
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5; ME=$(readlink -f "$0")
RX_TRAIN='^t3b_(all|half)_f[0-4]_s[5-7]$|^t3b_deploy_s[5-7]$'; RX_DUMP='^t3b_(all|half)_f[0-4]_s[5-7]\.swad\.tta_d4\.e1t3b_f[0-4]$'
no(){ echo "REFUSED: $*"; exit 1; }
[ -s $IO/REGISTERED.txt ] && [ "$(md5sum < $IO/REGISTERED.txt | cut -c1-32)" = "$REG_MD5" ] || no "no registration $REG_MD5 in $IO"
if head -1 $IO/REGISTERED.txt | grep -q '^TEST MODE'; then [ "${TEST_MODE:-0}" = 1 ] || no "the registration is a TEST MODE dry run"
else [ "${TEST_MODE:-0}" != 1 ] || no "TEST_MODE=1 against a real registration"; fi
grep "^scripts " $IO/REGISTERED.txt | grep -qF " t3b_relay.sh=$(md5sum < $ME | cut -c1-32) " || no "t3b_relay.sh is not the registered script"
grep -q "^commits K $KC " $IO/REGISTERED.txt || no "K is not the registered commit"
case $MODE in
  train) Q=/tmp/noob_el/bench_q/t3b; RD=$RD1; N=33; SES=bench_relay_t3b; J=$IO/jobs_train.txt; RX=$RX_TRAIN;;
  trainrep) R=${2:-}; case "$R" in [1-9]) ;; *) no "trainrep needs a repair number 1 to 9";; esac
    [ -s $IO/repair$R/REPAIR.txt ] || no "no registered repair $R in $IO"
    Q=/tmp/noob_el/bench_q/t3brep$R; RD=$RD1; N=33; SES=bench_relay_t3b; J=$IO/jobs_train.txt; RX=$RX_TRAIN; RESUME=1;;
  dump) Q=/tmp/noob_el/bench_q/t3bopen; RD=$RD2; N=30; SES=bench_relay_t3bopen; J=$IO/jobs_dump.txt; RX=$RX_DUMP;;
  deploy) RD=$RD1; J=$IO/jobs_train.txt; N=33;;
  *) no "mode train, trainrep R, deploy or dump";; esac
[ "$(grep -c . $J)" = $N ] && [ "$(cut -d'|' -f1 $J | grep -cE "$([ $MODE = dump ] && echo "$RX_DUMP" || echo "$RX_TRAIN")")" = $N ] || no "$J does not hold $N lines matching the mode's NAMES_RX"
if [ $MODE = deploy ]; then   # round 1 N10: latest.pth of the 3 deployable models, beside their relayed units
  grep -q "RELAY ALL DONE: 33 of 33" $RD1/relay.log 2>/dev/null || no "the training relay in $RD1 has not relayed 33 of 33"
  k=0
  for n in t3b_deploy_s5 t3b_deploy_s6 t3b_deploy_s7; do
    [ -e $RD1/.ok/$n ] && (cd $RD1/$n && md5sum -c --quiet runs/$n/RUN.md5 > /dev/null 2>&1) || no "$n: relayed unit missing or md5sum -c failed"
    t=$RD1/$n/experiments/$n/checkpoints/latest.pth
    if [ -f $t ] && (cd $RD1/$n && md5sum -c --quiet runs/$n/LATEST.md5 > /dev/null 2>&1); then echo "$n: latest.pth already relayed"; k=$((k+1)); continue; fi
    [ ! -e $t ] || no "$t exists and differs from LATEST.md5"
    [ $SHOW = 1 ] && { echo "SHOW: ssh cv02 'cd $KB && tar cf - experiments/$n/checkpoints/latest.pth' | tar x -C $RD1/.part_latest/$n"; continue; }
    rm -rf $RD1/.part_latest/$n; mkdir -p $RD1/.part_latest/$n
    ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "cd $KB && tar cf - experiments/$n/checkpoints/latest.pth" | tar xf - -C $RD1/.part_latest/$n
    rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || no "$n: stream rc $rc"
    (cd $RD1/.part_latest/$n && md5sum -c --quiet $RD1/$n/runs/$n/LATEST.md5 > /dev/null 2>&1) || no "$n: copied latest.pth differs from the relayed LATEST.md5"
    mv $RD1/.part_latest/$n/experiments/$n/checkpoints/latest.pth $t && rm -rf $RD1/.part_latest/$n || no "$n: placing latest.pth"
    (cd $RD1/$n && md5sum -c --quiet runs/$n/LATEST.md5 > /dev/null 2>&1) || no "$n: latest.pth in place fails md5sum -c"
    echo "[$(date '+%F %T')] relayed latest.pth of $n ($(du -sm $t | cut -f1) MB), md5sum -c of runs/$n/LATEST.md5 OK" | tee -a $RD1/relay.log; k=$((k+1))
  done
  [ $SHOW = 1 ] && exit 0
  echo "[$(date '+%F %T')] DEPLOY LATEST DONE: $k of 3" | tee -a $RD1/relay.log; exit 0
fi
CMD="B=$KB Q=$Q RD=$RD N=$N NAMES_RX='$RX' POLL=$POLL bash $ST/bench/q/cv02/relay_w1c.sh"
[ $SHOW = 1 ] && { echo "tmux new-session -d -s $SES \"$CMD\""; exit 0; }
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "stage copy $ST: CODE.md5 check failed"
[ "$(md5sum < $ST/bench/q/cv02/relay_w1c.sh | cut -c1-32)" = 74a2ec3d48ad3cd989aa0c9b5ae69942 ] || no "relay_w1c.sh is not 74a2ec3d"
[ $FG = 1 ] || ! tmux has-session -t "=$SES" 2>/dev/null || no "tmux session $SES exists"
if [ $RESUME = 1 ]; then [ -d $RD/.ok ] || no "RESUME=1 but $RD is not a relay dir"
  p=$(cat $RD/relay.pid 2>/dev/null); [ -n "$p" ] && kill -0 $p 2>/dev/null && no "relay pid $p is alive"
  rm -f $RD/STOP
else [ -e $RD ] && no "$RD exists (RESUME=1 continues it)"; fi
mkdir -p "$(dirname $RD)" || no "cannot make $(dirname $RD)"
a=$(df --output=avail -BG $(dirname $RD) | tail -1 | tr -dc 0-9); [ "${a:-0}" -ge "$FLOOR" ] || no "free ${a:-?} GB on the filesystem of $RD < $FLOOR"
mkdir -p $RD
if [ $FG = 1 ]; then bash -c "$CMD"; echo "relay (foreground) ended: $(tail -1 $RD/relay.log)"; exit 0; fi
tmux new-session -d -s $SES "$CMD" && sleep 3
echo "started $SES (free $a GB, N $N, names /$RX/): $(tail -1 $RD/relay.log)"
