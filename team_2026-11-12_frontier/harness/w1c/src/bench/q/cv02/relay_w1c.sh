#!/bin/bash
# Relay cv02 -> gaint, per finished run (runs on gaint in tmux, session bench_relay_*). Never deletes or writes anything on cv02
# (ssh -n, read-only commands: md5sum -c, tar cf -, ls, grep). No agent forwarding (ssh -a), BatchMode.
# A run is ready when cv02 B/runs/<name>/RUN.md5 exists (cq.sh writes it last, by rename). RUN.md5 lists (paths relative to B):
#   experiments/<name>/config_used.yaml, experiments/<name>/checkpoints/slim.pth, runs/<name>/LATEST.md5 (md5 of the full
#   latest.pth, which stays on cv02), and every file of the run's dump dir dumps/elbench1/<method>/<name>/<set>/.
# Per run: (1) cv02: md5sum -c runs/<name>/RUN.md5 and md5 of RUN.md5; (2) stream tar cf - (RUN.md5 + its files) into
#   RD/.part/<name>; (3) gaint: md5sum -c, md5 of RUN.md5 equal on both ends, file count equal; then rename to RD/<name> and
#   write RD/.ok/<name>. Refuses to overwrite RD/<name>. A failed run is retried at the next poll (RD/.part/<name> is ours and
#   is replaced); after 3 failures the run is left alone with a GIVE UP line.
# Env: B (cv02 deploy dir), Q (cv02 queue dir), RD (gaint relay dir), N (number of jobs expected), NAMES_RX (optional regex of run
#   names to relay, default all), POLL (300 s). Ends when N runs are relayed, or when cv02's launch.log has the end line and every
#   RUN.md5 there is relayed, or on RD/STOP. Log RD/relay.log; PID RD/relay.pid. rc captured before any $(date).
set -u
B=${B:?}; Q=${Q:?}; RD=${RD:?}; N=${N:?}; POLL=${POLL:-300}; NAMES_RX=${NAMES_RX:-.}
C=cv02@10.8.1.106
SC(){ ssh -n -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 $C "$1"; }
mkdir -p $RD/.part $RD/.ok; L=$RD/relay.log; echo $$ > $RD/relay.pid
say(){ echo "[$(date '+%F %T')] $*" >> $L; }
declare -A NF=()
say "relay start pid $$: cv02 $B -> gaint $RD (N $N, names /$NAMES_RX/, poll $POLL s, script $(md5sum < $0 | cut -c1-8))"
relay_one(){ local n=$1 r m k got rc
  [ -e $RD/$n ] && { say "$n: $RD/$n exists; refuse to overwrite (marking .ok/$n.refused)"; touch $RD/.ok/$n.refused; return 1; }
  r=$(SC "cd $B && md5sum -c --quiet runs/$n/RUN.md5 > /dev/null 2>&1 && echo OK \$(md5sum < runs/$n/RUN.md5 | cut -c1-32) \$(grep -c . runs/$n/RUN.md5) || echo BAD")
  set -- $r; [ "${1:-}" = OK ] || { say "$n: cv02 md5sum -c FAILED or ssh failed ($r)"; return 1; }
  m=$2; k=$3
  rm -rf $RD/.part/$n; mkdir -p $RD/.part/$n
  SC "cd $B && tar cf - runs/$n/RUN.md5 \$(awk '{print \$2}' runs/$n/RUN.md5)" | tar xf - -C $RD/.part/$n
  rc=${PIPESTATUS[0]}${PIPESTATUS[1]}; [ "$rc" = 00 ] || { say "$n: stream rc $rc (cv02 ssh+tar / gaint tar)"; return 1; }
  (cd $RD/.part/$n && md5sum -c --quiet runs/$n/RUN.md5 > /dev/null 2>&1); rc=$?
  [ $rc = 0 ] || { say "$n: gaint md5sum -c rc $rc"; return 1; }
  got=$(md5sum < $RD/.part/$n/runs/$n/RUN.md5 | cut -c1-32)
  [ "$got" = "$m" ] || { say "$n: RUN.md5 differs ($got on gaint, $m on cv02)"; return 1; }
  [ "$(find $RD/.part/$n -type f | wc -l)" = $((k + 1)) ] || { say "$n: file count $(find $RD/.part/$n -type f | wc -l) != $((k + 1))"; return 1; }
  mv $RD/.part/$n $RD/$n && echo "$(date '+%F %T') RUN.md5 $m files $k" > $RD/.ok/$n
  say "relayed $n: $k files + RUN.md5, md5sum -c OK on both ends, RUN.md5 $m both ends, $(du -sm $RD/$n | cut -f1) MB"; }
while :; do
  [ -e $RD/STOP ] && { say "STOP file seen; relay stops"; break; }
  L1=$(SC "cd $B/runs 2>/dev/null && ls -d */RUN.md5 2>/dev/null | sed 's#/RUN.md5##'; echo __END__ \$(grep -c 'BENCH CV02 Q ALL DONE' $Q/launch.log 2>/dev/null)") \
    || { say "cv02 list failed (ssh); retry in $POLL s"; sleep $POLL; continue; }
  endl=$(echo "$L1" | awk '/^__END__/{print $2}')
  for n in $(echo "$L1" | grep -v '^__END__' | grep -E "$NAMES_RX"); do
    [ -e $RD/.ok/$n ] || [ -e $RD/.ok/$n.refused ] || [ "${NF[$n]:-0}" -ge 3 ] && continue
    relay_one $n || { NF[$n]=$(( ${NF[$n]:-0} + 1 )); [ ${NF[$n]} -ge 3 ] && say "GIVE UP $n after 3 failures"; }
  done
  done_n=$(ls $RD/.ok | grep -vc '\.refused$')
  [ $done_n -ge $N ] && { say "RELAY ALL DONE: $done_n of $N runs relayed"; break; }
  if [ "${endl:-0}" -ge 1 ]; then
    left=$(for n in $(echo "$L1" | grep -v '^__END__' | grep -E "$NAMES_RX"); do [ -e $RD/.ok/$n ] || [ -e $RD/.ok/$n.refused ] || [ "${NF[$n]:-0}" -ge 3 ] || echo $n; done | wc -l)
    [ $left = 0 ] && { say "RELAY DONE: cv02 queue ended; $done_n of $N runs relayed (the rest wrote no RUN.md5)"; break; }
  fi
  sleep $POLL
done
rm -f $RD/relay.pid
