#!/bin/bash
# fin2 relay start (run by the LEAD on gaint, right after fin2 is armed) = harness/final/final_relay.sh (281469ba) with:
# B = the F2 deploy F2B (the 10 resumed runs write their runs/ there), Q = /tmp/noob_el/bench_q/fin2, relay dir
# bench_relay/fin2, every name of the queue (NAMES_RX .), N 10, session bench_relay_fin2. Same reviewed relay script (stage copy
# of 89b9ea5, relay_w1c.sh 74a2ec3d), unchanged: it relays what RUN.md5 lists. Other relays read the runs/ of other deploys
# (bench_821dfad for fin, ...), so a fin2 unit can never count for them, nor theirs for this one.
# A relayed unit (10) = RUN.md5 + config_used.yaml + slim.pth (swad_bn and swad for the candidate; model for PF) + LATEST.md5
#   (+ enc_probe.jsonl for the candidate); about 0.17 / 0.10 GB. latest.pth stays on cv02 (the opening reads it there).
# Refuses: stage copy or relay script changed; F2B not /tmp/noob_el/bench_<7 hex> or one of the older deploys; session exists;
# relay dir exists (RESUME=1 continues an existing dir whose relay ended); gaint free below FLOOR GB (default 25).
# SHOW=1 prints the command only. Stop: touch /home/noob/work/bench_relay/fin2/STOP. RD may be set to a NAS dir.
set -u
SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}; FB=${F2B:?F2 deploy dir /tmp/noob_el/bench_<7 hex>}
RD=${RD:-/home/noob/work/bench_relay/fin2}; SES=bench_relay_fin2
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
Q=/tmp/noob_el/bench_q/fin2
no(){ echo "REFUSED: $*"; exit 1; }
echo "$FB" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' && [ "$FB" != /tmp/noob_el/bench_89b9ea5 ] && [ "$FB" != /tmp/noob_el/bench_03375d4 ] && [ "$FB" != /tmp/noob_el/bench_821dfad ] || no "F2B must be the F2 deploy /tmp/noob_el/bench_<7 hex>, not bench_89b9ea5, bench_03375d4 or bench_821dfad (F)"
CMD="B=$FB Q=$Q RD=$RD N=10 NAMES_RX=. POLL=300 bash $ST/bench/q/cv02/relay_w1c.sh"
[ $SHOW = 1 ] && { echo "tmux new-session -d -s $SES \"$CMD\""; exit 0; }
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "stage copy $ST: CODE.md5 check failed"
[ "$(md5sum < $ST/bench/q/cv02/relay_w1c.sh | cut -c1-32)" = 74a2ec3d48ad3cd989aa0c9b5ae69942 ] || no "relay_w1c.sh is not 74a2ec3d"
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
if [ $RESUME = 1 ]; then [ -d $RD/.ok ] || no "RESUME=1 but $RD is not a relay dir"
  p=$(cat $RD/relay.pid 2>/dev/null); [ -n "$p" ] && kill -0 $p 2>/dev/null && no "relay pid $p is alive"
  rm -f $RD/STOP
else [ -e $RD ] && no "$RD exists (RESUME=1 continues it)"; fi
a=$(df --output=avail -BG $(dirname $RD) | tail -1 | tr -dc 0-9); [ "${a:-0}" -ge "$FLOOR" ] || no "free ${a:-?} GB on the filesystem of $RD < $FLOOR"
mkdir -p $RD && tmux new-session -d -s $SES "$CMD" && sleep 3
echo "started $SES (free $a GB): $(tail -1 $RD/relay.log)"
