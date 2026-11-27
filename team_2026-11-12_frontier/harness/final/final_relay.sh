#!/bin/bash
# fin relay start (run by the LEAD on gaint, right after the fin queue is armed) = harness/c3x/c3x_relay.sh (b3bc1db9) with:
# B = the F deploy FB (all 85 jobs of the queue fin write their runs/ and dumps/ there), Q = /tmp/noob_el/bench_q/fin, relay dir
# bench_relay/fin, every name of the queue (NAMES_RX .), N 85, session bench_relay_fin. Same reviewed relay script (stage copy
# of 89b9ea5, relay_w1c.sh 74a2ec3d), unchanged: it relays what RUN.md5 lists. The other relays read the runs/ of other deploys
# (bench_89b9ea5, bench_03375d4, ...), so a fin unit can never count for them, nor theirs for this one.
# A relayed unit = RUN.md5 + its files:
#   dump-only job (75): the one D4 dump folder dumps/elbench1/<method>/<name>/cv5v3_f<k>/ (107 to 111 cells, about 0.13 GB);
#   full-pool run (10): config_used.yaml + slim.pth (swad_bn and swad for the candidate; model for PF) + LATEST.md5
#     (+ enc_probe.jsonl for the candidate); about 0.17 / 0.10 GB. latest.pth stays on cv02 (the opening reads it there).
# Refuses: stage copy or relay script changed; FB not /tmp/noob_el/bench_<7 hex> of F; session exists; relay dir exists
# (RESUME=1 continues an existing dir whose relay ended: finished units keep their .ok and are skipped); gaint free below
# FLOOR GB (default 25). SHOW=1 prints the command only. Stop: touch /home/noob/work/bench_relay/fin/STOP.
# RD (default /home/noob/work/bench_relay/fin) may be set to a NAS dir (/mnt/nas/noob_el_archive/bench_relay/fin) if gaint is
# short of space; run_read_final.sh then needs RELAY_FIN=<that dir> (see LAUNCH_REQUEST_final.md section 5).
set -u
SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}; FB=${FB:?F deploy dir /tmp/noob_el/bench_<7 hex>}
RD=${RD:-/home/noob/work/bench_relay/fin}; SES=bench_relay_fin
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
Q=/tmp/noob_el/bench_q/fin
no(){ echo "REFUSED: $*"; exit 1; }
echo "$FB" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}$' && [ "$FB" != /tmp/noob_el/bench_89b9ea5 ] && [ "$FB" != /tmp/noob_el/bench_03375d4 ] || no "FB must be the F deploy /tmp/noob_el/bench_<7 hex>, not bench_89b9ea5 or bench_03375d4"
CMD="B=$FB Q=$Q RD=$RD N=85 NAMES_RX=. POLL=300 bash $ST/bench/q/cv02/relay_w1c.sh"
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
