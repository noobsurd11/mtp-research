#!/bin/bash
# c3swad relay start (run by the LEAD on gaint, after the merged queue is armed): a third relay for the swad runs.
# Same reviewed relay script as c3base and c3hrnet (stage copy of 89b9ea5, relay_w1c.sh 74a2ec3d), own relay dir, names
# ^c3s_ only, N 25. The two running relays are not touched: c3base takes ^c3_ (N 50) and c3hrnet ^c3h_ (N 25); a swad
# run under either pattern would count towards their N and end them early, so the swad names start with c3s_.
# A relayed swad run = RUN.md5 + config_used.yaml + slim.pth (swad_bn, swad) + LATEST.md5 + enc_probe.jsonl + two dump
# folders (<name>, <name>.swad), about 0.47 GB.
# Refuses: stage copy or relay script changed; session exists; relay dir exists (RESUME=1 continues an existing dir whose
# relay ended: finished runs keep their .ok and are skipped); gaint free space below FLOOR GB (default 25).
# SHOW=1 prints the command only. Stop: touch /home/noob/work/bench_relay/c3swad/STOP.
set -u
SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}; NEWQ=${NEWQ:-c3all2}
RD=/home/noob/work/bench_relay/c3swad; SES=bench_relay_c3swad
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
B=/tmp/noob_el/bench_89b9ea5; Q=/tmp/noob_el/bench_q/$NEWQ
CMD="B=$B Q=$Q RD=$RD N=25 NAMES_RX=^c3s_ POLL=300 bash $ST/bench/q/cv02/relay_w1c.sh"
[ $SHOW = 1 ] && { echo "tmux new-session -d -s $SES \"$CMD\""; exit 0; }
no(){ echo "REFUSED: $*"; exit 1; }
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "stage copy $ST: CODE.md5 check failed"
[ "$(md5sum < $ST/bench/q/cv02/relay_w1c.sh | cut -c1-32)" = 74a2ec3d48ad3cd989aa0c9b5ae69942 ] || no "relay_w1c.sh is not 74a2ec3d"
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
if [ $RESUME = 1 ]; then [ -d $RD/.ok ] || no "RESUME=1 but $RD is not a relay dir"
  p=$(cat $RD/relay.pid 2>/dev/null); [ -n "$p" ] && kill -0 $p 2>/dev/null && no "relay pid $p is alive"
  rm -f $RD/STOP
else [ -e $RD ] && no "$RD exists (RESUME=1 continues it)"; fi
a=$(df --output=avail -BG /home/noob/work | tail -1 | tr -dc 0-9); [ "${a:-0}" -ge "$FLOOR" ] || no "gaint free ${a:-?} GB < $FLOOR"
mkdir -p $RD && tmux new-session -d -s $SES "$CMD" && sleep 3
echo "started $SES (gaint free $a GB): $(tail -1 $RD/relay.log)"
