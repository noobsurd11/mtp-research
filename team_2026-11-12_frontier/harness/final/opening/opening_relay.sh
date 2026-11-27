#!/bin/bash
# Relay of the sealed-opening queue `open` (run by the LEAD on gaint right after `opening_queue.sh arm`) = final_relay.sh
# (281469ba) with B = GB (the deploy of G, where the open queue writes dumps/ and runs/), Q = /tmp/noob_el/bench_q/open,
# RD = /mnt/nas/noob_el_archive/bench_relay/open (the NAS: default since review round 1, N6 / N7; gaint's / is shared with
# root's finllm and fin's relay), N = the registered job count, session bench_relay_open. Same reviewed relay
# script (stage copy of 89b9ea5, relay_w1c.sh 74a2ec3d), unchanged: a unit = RUN.md5 + the one sealed dump folder
# dumps/elbench1/<method>/<name>/<set>/ (E1 C1 / C2 with logp about 1.0 GB, others about 0.06 to 0.14 GB).
# Refuses: stage copy or relay script changed; G not the registered commit; session or RD exists (RESUME=1 continues);
# free space on RD's filesystem below FLOOR GB (default 25). RD (one variable name for opening_relay.sh, run_opening_read.sh and
# opening_queue.sh unstage) may be set to a gaint dir, e.g. RD=/home/noob/work/bench_relay/open, if the NAS is down; then pass
# the same RD to the read and to unstage. Its parent is made with mkdir -p. SHOW=1 prints the command. Stop: touch <RD>/STOP.
set -u
SHOW=${SHOW:-0}; RESUME=${RESUME:-0}; FLOOR=${FLOOR:-25}; G=${G:?full commit of G}
IO=${IO:-/home/noob/work/bench_open_io}; RD=${RD:-/mnt/nas/noob_el_archive/bench_relay/open}; SES=bench_relay_open
ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
Q=/tmp/noob_el/bench_q/open; GB=/tmp/noob_el/bench_${G:0:7}
no(){ echo "REFUSED: $*"; exit 1; }
grep -q "^commits F 821dfadf49116cc6d5fdbd6697e263dd7cf0f834 G $G " $IO/REGISTERED.txt 2>/dev/null || no "G is not the registered commit (or no registration in $IO)"
N=$(grep -c . $IO/jobs.txt)
CMD="B=$GB Q=$Q RD=$RD N=$N NAMES_RX=. POLL=300 bash $ST/bench/q/cv02/relay_w1c.sh"
[ $SHOW = 1 ] && { echo "tmux new-session -d -s $SES \"$CMD\""; exit 0; }
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "stage copy $ST: CODE.md5 check failed"
[ "$(md5sum < $ST/bench/q/cv02/relay_w1c.sh | cut -c1-32)" = 74a2ec3d48ad3cd989aa0c9b5ae69942 ] || no "relay_w1c.sh is not 74a2ec3d"
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
if [ $RESUME = 1 ]; then [ -d $RD/.ok ] || no "RESUME=1 but $RD is not a relay dir"
  p=$(cat $RD/relay.pid 2>/dev/null); [ -n "$p" ] && kill -0 $p 2>/dev/null && no "relay pid $p is alive"
  rm -f $RD/STOP
else [ -e $RD ] && no "$RD exists (RESUME=1 continues it)"; fi
mkdir -p "$(dirname $RD)" || no "cannot make $(dirname $RD)"
a=$(df --output=avail -BG $(dirname $RD) | tail -1 | tr -dc 0-9); [ "${a:-0}" -ge "$FLOOR" ] || no "free ${a:-?} GB on the filesystem of $RD < $FLOOR"
mkdir -p $RD && tmux new-session -d -s $SES "$CMD" && sleep 3
echo "started $SES (free $a GB, N $N): $(tail -1 $RD/relay.log)"
