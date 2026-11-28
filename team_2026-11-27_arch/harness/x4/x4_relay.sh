#!/bin/bash
# x4 relay cv02 -> gaint = relay_w1c.sh (74a2ec3d, the reviewed relay) with two changes (lead, 27 Nov 2026: gaint disk at 98%):
#  (1) only what the read needs: files of RUN.md5 whose path matches SKIP_RX (default: checkpoints/slim.pth) are NOT pulled;
#      they and the full latest.pth stay on cv02 (cv02 /tmp is wiped on reboot: the weights are then gone; dumps are kept here).
#      Pulled: RUN.md5, config_used.yaml, LATEST.md5, enc_probe.jsonl, the dump folders. md5sum -c of the pulled subset on both
#      ends, RUN.md5 md5 equal on both ends, file count = pulled subset + 1.
#      READ_ONLY=1 (default): a run that has a <run>.swad dump also leaves its primary dump (card weights_key) on cv02: the x4
#      read uses only the swad readout. READ_ONLY=0 pulls both dumps.
#  (2) disk guard: before each run, gaint free bytes minus the run's pulled size must stay >= FLOOR GB (default 15); else the
#      relay writes RD/DISK_HOLD and stops (finished runs wait on cv02; restart with RESUME=1 after freeing space).
# Never writes or deletes on cv02 (ssh -n, read-only commands). No agent forwarding. rc captured before any $(date).
#  (3) several deploy dirs (cq_x4.sh): each poll lists runs/*/RUN.md5 in every dir of the queue's Q/deploys.txt and in B.
# Env: B (cv02 deploy, optional with cq_x4.sh queues), Q (cv02 queue dir), RD (gaint relay dir), N (runs expected), NAMES_RX, POLL (300), FLOOR (15),
#   SKIP_RX ('/checkpoints/slim\.pth$'; '^$' pulls everything). Ends at N runs, at the queue's end line with all RUN.md5
#   relayed, on RD/STOP, or on the disk guard. Log RD/relay.log; PID RD/relay.pid.
set -u
B=${B:-}; Q=${Q:?}; RD=${RD:?}; N=${N:?}; POLL=${POLL:-300}; NAMES_RX=${NAMES_RX:-.}; FLOOR=${FLOOR:-15}
SKIP_RX=${SKIP_RX:-/checkpoints/slim\\.pth\$}; READ_ONLY=${READ_ONLY:-1}
C=cv02@10.8.1.106
SC(){ ssh -n -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 $C "$1"; }
mkdir -p $RD/.part $RD/.ok; L=$RD/relay.log; echo $$ > $RD/relay.pid
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
declare -A NF=()
say "x4 relay start pid $$: cv02 ${B:-} + $Q/deploys.txt -> gaint $RD (N $N, names /$NAMES_RX/, skip /$SKIP_RX/, floor $FLOOR GB, poll $POLL s, script $(md5sum < $0 | cut -c1-8))"
relay_one(){ local n=$1 B=$2 r m k sz av got rc rx=$SKIP_RX has
  if [ "$READ_ONLY" = 1 ]; then has=$(SC "grep -c ' dumps/elbench1/[^/]*/$n\.swad/' $B/runs/$n/RUN.md5"); [ "${has:-0}" -gt 0 ] 2>/dev/null && rx="$SKIP_RX| dumps/elbench1/[^/]+/$n/"; fi
  [ -e $RD/$n ] && { say "$n: $RD/$n exists; refuse to overwrite (marking .ok/$n.refused)"; touch $RD/.ok/$n.refused; return 1; }
  r=$(SC "cd $B && grep -vE '$rx' runs/$n/RUN.md5 > /dev/null && grep -vE '$rx' runs/$n/RUN.md5 | md5sum -c --quiet - > /dev/null 2>&1 && echo OK \$(md5sum < runs/$n/RUN.md5 | cut -c1-32) \$(grep -vE '$rx' runs/$n/RUN.md5 | grep -c .) \$(grep -cE '$rx' runs/$n/RUN.md5) \$(grep -vE '$rx' runs/$n/RUN.md5 | awk '{print \$2}' | xargs -d '\n' du -cb | tail -1 | cut -f1) || echo BAD")
  set -- $r; [ "${1:-}" = OK ] || { say "$n: cv02 md5sum -c FAILED or ssh failed ($r)"; return 1; }
  m=$2; k=$3; sk=$4; sz=$(( $5 + ${GUARD_TEST_ADD:-0} ))   # GUARD_TEST_ADD: bytes, tests of the guard only
  av=$(df --output=avail -B1 $RD | tail -1 | tr -dc 0-9)
  if [ $(( (av - sz) / 1073741824 )) -lt $FLOOR ]; then
    say "DISK GUARD: $n needs $((sz / 1048576)) MB, gaint free $((av / 1073741824)) GB, would leave < $FLOOR GB; relay stops (DISK_HOLD)"
    touch $RD/DISK_HOLD; return 2; fi
  rm -rf $RD/.part/$n; mkdir -p $RD/.part/$n
  SC "cd $B && tar cf - runs/$n/RUN.md5 \$(grep -vE '$rx' runs/$n/RUN.md5 | awk '{print \$2}')" | tar xf - -C $RD/.part/$n
  rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || { say "$n: stream rc $rc (cv02 ssh+tar / gaint tar)"; return 1; }
  (cd $RD/.part/$n && grep -vE "$rx" runs/$n/RUN.md5 | md5sum -c --quiet - > /dev/null 2>&1); rc=$?
  [ $rc = 0 ] || { say "$n: gaint md5sum -c rc $rc"; return 1; }
  got=$(md5sum < $RD/.part/$n/runs/$n/RUN.md5 | cut -c1-32)
  [ "$got" = "$m" ] || { say "$n: RUN.md5 differs ($got on gaint, $m on cv02)"; return 1; }
  [ "$(find $RD/.part/$n -type f | wc -l)" = $((k + 1)) ] || { say "$n: file count $(find $RD/.part/$n -type f | wc -l) != $((k + 1))"; return 1; }
  mv $RD/.part/$n $RD/$n && echo "$(date '+%F %T') RUN.md5 $m files $k pulled, $sk left on cv02 (skip /$rx/)" > $RD/.ok/$n
  say "relayed $n: $k files + RUN.md5 ($sk left on cv02: /$rx/), md5sum -c OK on both ends, RUN.md5 $m both ends, $(du -sm $RD/$n | cut -f1) MB; gaint free $(df --output=avail -BG $RD | tail -1 | tr -dc 0-9) GB"; }
a=$(( $(df --output=avail -B1 $RD | tail -1 | tr -dc 0-9) / 1073741824 )); [ "${a:-0}" -gt "$FLOOR" ] || { say "DISK GUARD at start: gaint free ${a:-?} GB <= $FLOOR; not relaying"; touch $RD/DISK_HOLD; rm -f $RD/relay.pid; exit 1; }
while :; do
  [ -e $RD/STOP ] && { say "STOP file seen; relay stops"; break; }
  L1=$(SC "for b in \$(cut -d' ' -f2 $Q/deploys.txt 2>/dev/null) $B; do [ -d \$b/runs ] && (cd \$b/runs && ls -d */RUN.md5 2>/dev/null | sed \"s#/RUN.md5# \$b#\"); done | sort -u; echo __END__ \$(grep -c 'BENCH CV02 Q ALL DONE' $Q/launch.log 2>/dev/null)") \
    || { say "cv02 list failed (ssh); retry in $POLL s"; sleep $POLL; continue; }
  endl=$(echo "$L1" | awk '/^__END__/{print $2}'); dg=0
  while read -r n nb; do [ -n "$n" ] || continue; echo "$n" | grep -qE "$NAMES_RX" || continue
    [ -e $RD/.ok/$n ] || [ -e $RD/.ok/$n.refused ] || [ "${NF[$n]:-0}" -ge 3 ] && continue
    relay_one $n $nb; rc=$?
    [ $rc = 2 ] && { dg=1; break; }
    [ $rc = 0 ] || { NF[$n]=$(( ${NF[$n]:-0} + 1 )); [ ${NF[$n]} -ge 3 ] && say "GIVE UP $n after 3 failures"; }
  done < <(echo "$L1" | grep -v '^__END__')
  [ $dg = 1 ] && break
  done_n=$(ls $RD/.ok | grep -vc '\.refused$')
  [ $done_n -ge $N ] && { say "RELAY ALL DONE: $done_n of $N runs relayed"; break; }
  if [ "${endl:-0}" -ge 1 ]; then
    left=$(for n in $(echo "$L1" | grep -v '^__END__' | cut -d' ' -f1 | grep -E "$NAMES_RX"); do [ -e $RD/.ok/$n ] || [ -e $RD/.ok/$n.refused ] || [ "${NF[$n]:-0}" -ge 3 ] || echo $n; done | wc -l)
    [ $left = 0 ] && { say "RELAY DONE: cv02 queue ended; $done_n of $N runs relayed (the rest wrote no RUN.md5)"; break; }
  fi
  sleep $POLL
done
rm -f $RD/relay.pid
