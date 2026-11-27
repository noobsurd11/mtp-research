#!/bin/bash
# c3x relay start (run by the LEAD on gaint, right after the c3x queue is armed) = harness/c3swad/c3swad_relay.sh (535a62a2)
# with: B = the c3x deploy dir XB (training, dumps and runs of c3x live there, not in bench_89b9ea5), Q = /tmp/noob_el/bench_q/c3x,
# relay dir bench_relay/c3x, names ^c3x_ only, N 25, session bench_relay_c3x. Same reviewed relay script (stage copy of
# 89b9ea5, relay_w1c.sh 74a2ec3d). The running relays read bench_89b9ea5/runs only, so a c3x run can never count for them;
# ^c3x_ is matched by none of their patterns (^c3_, ^c3h_, ^c3s_) either.
# A relayed c3x run = RUN.md5 + config_used.yaml + slim.pth (swad_bn, swad) + LATEST.md5 + enc_probe.jsonl + two dump folders
# (<name>, <name>.swad), about 0.43 GB.
# Refuses: stage copy or relay script changed; XB not /tmp/noob_el/bench_<7 hex> or = bench_89b9ea5; session exists; relay dir
# exists (RESUME=1 continues an existing dir whose relay ended: finished runs keep their .ok and are skipped); gaint free below
# FLOOR GB (default 25). SHOW=1 prints the command only. Stop: touch /home/noob/work/bench_relay/c3x/STOP.
set -u
SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}; XB=${XB:?c3x deploy dir /tmp/noob_el/bench_<7 hex>}
RD=/home/noob/work/bench_relay/c3x; SES=bench_relay_c3x
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
Q=/tmp/noob_el/bench_q/c3x
no(){ echo "REFUSED: $*"; exit 1; }
echo "$XB" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' && [ "$XB" != /tmp/noob_el/bench_89b9ea5 ] || no "XB must be the c3x deploy /tmp/noob_el/bench_<7 hex>, not bench_89b9ea5"
CMD="B=$XB Q=$Q RD=$RD N=25 NAMES_RX=^c3x_ POLL=300 bash $ST/bench/q/cv02/relay_w1c.sh"
[ $SHOW = 1 ] && { echo "tmux new-session -d -s $SES \"$CMD\""; exit 0; }
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
