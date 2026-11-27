#!/bin/bash
# MAXC window for the merged queue c3all2 (c3swad, review F12, 17 Nov 2026) = harness/c3base/c3all/maxc_window.sh (56ed9932,
# unchanged) with the queue changed to c3all2 and the awaited RUN.md5 files given as arguments. It acts on c3all2/MAXC only
# and NEVER writes into c3all/MAXC (c3all stays frozen at 0 for good).
# Use: a dump of another queue (e.g. the frozen c3all, or rows2) waits for its GPU and keeps losing it to the next c3all2
# start. The window writes 1 into c3all2/MAXC (cq.sh reads it live: no new c3all2 training start while one c3all2 lane is
# alive; running runs and c3all2's own dumps are not touched), waits until every given RUN.md5 exists or TMAX seconds,
# then ALWAYS writes 8 back (also on exit or a signal). Both writes go by rename of MAXC.new. Touches nothing else on cv02.
# Run on gaint in tmux, session name bench_maxc_window (c3swad_handover.sh freeze refuses while that session exists):
#   tmux new-session -d -s bench_maxc_window "bash <this file> /tmp/noob_el/bench_89b9ea5/runs/<run>/RUN.md5 [...] > <log> 2>&1"
# DRY=1: reads only; prints the writes it would make and exits.
set -u
H="ssh -n -a -o BatchMode=yes -o ConnectTimeout=15 cv02@10.8.1.106"
Q=/tmp/noob_el/bench_q/c3all2; TMAX=${TMAX:-1500}; DRY=${DRY:-0}
[ $# -ge 1 ] || { echo "usage: maxc_window_c3all2.sh <cv02 path of an awaited RUN.md5> [more]"; exit 1; }
for f in "$@"; do echo "$f" | grep -qE '^/tmp/noob_el/bench_[0-9a-f]{7}/runs/[A-Za-z0-9_.]+/RUN\.md5$' || { echo "REFUSED: not a cv02 RUN.md5 path: $f"; exit 1; }; done
F="$*"; NW=$#
lg(){ echo "[$(date '+%F %T')] $*"; }
SET=0
restore(){ [ $SET = 1 ] || return 0
  while :; do r=$($H "echo 8 > $Q/MAXC.new && mv $Q/MAXC.new $Q/MAXC && cat $Q/MAXC" 2>/dev/null); [ "$r" = 8 ] && break; lg "restore not confirmed ('$r'), retry"; sleep 15; done
  SET=0; lg "MAXC restored to 8"; }
trap restore EXIT
trap 'exit 1' INT TERM HUP
[ "$($H "cat $Q/MAXC")" = 8 ] || { lg "c3all2/MAXC is not 8; nothing changed"; exit 1; }
if [ $DRY = 1 ]; then lg "DRY: c3all2/MAXC reads 8; RUN.md5 present now: $($H "ls $F 2>/dev/null | wc -l") of $NW; would write 1 into $Q/MAXC, wait at most $TMAX s, then write 8 back"; exit 0; fi
SET=1
r=$($H "echo 1 > $Q/MAXC.new && mv $Q/MAXC.new $Q/MAXC && cat $Q/MAXC"); [ "$r" = 1 ] || { lg "write of 1 not confirmed ('$r')"; exit 1; }
lg "c3all2/MAXC set to 1 (window of at most $TMAX s)"
t0=$(date +%s); last=""
while :; do
  s=$($H "ls $F 2>/dev/null | wc -l" 2>/dev/null)
  [ "$s" != "$last" ] && lg "RUN.md5 present: ${s:-?} of $NW"; last=$s
  [ "$s" = $NW ] && break
  [ $(( $(date +%s) - t0 )) -ge $TMAX ] && { lg "timeout after $TMAX s"; break; }
  sleep 20
done
restore
