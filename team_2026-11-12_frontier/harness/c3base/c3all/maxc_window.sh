#!/bin/bash
# One-off window (lead, 16 Nov 2026) for the two dumps that wait for cv02 GPU 0 and keep losing it to the next c3all start:
#   c3hrnet: dump of c3h_hrnet_w18_unetpp_pf_f2_s5;  rows2: dump of r2_skr01_pf_v11_f3_s6.
# Writes 1 into c3all/MAXC (cq.sh reads it live: no new c3all training start while one c3all lane is alive; running runs and
# c3all's own dumps are not touched), waits until both runs have RUN.md5 or TMAX seconds, then ALWAYS writes 8 back
# (also on exit or a signal). Touches nothing else on cv02. Run on gaint in tmux; log = stdout.
set -u
H="ssh -n -a -o BatchMode=yes -o ConnectTimeout=15 cv02@10.8.1.106"
Q=/tmp/noob_el/bench_q/c3all; TMAX=${TMAX:-1500}
A=/tmp/noob_el/bench_89b9ea5/runs/c3h_hrnet_w18_unetpp_pf_f2_s5/RUN.md5
R=/tmp/noob_el/bench_b12fca8/runs/r2_skr01_pf_v11_f3_s6/RUN.md5
lg(){ echo "[$(date '+%F %T')] $*"; }
SET=0
restore(){ [ $SET = 1 ] || return 0
  while :; do r=$($H "echo 8 > $Q/MAXC && cat $Q/MAXC" 2>/dev/null); [ "$r" = 8 ] && break; lg "restore not confirmed ('$r'), retry"; sleep 15; done
  SET=0; lg "MAXC restored to 8"; }
trap restore EXIT
trap 'exit 1' INT TERM HUP
[ "$($H "cat $Q/MAXC")" = 8 ] || { lg "MAXC is not 8; nothing changed"; exit 1; }
SET=1
r=$($H "echo 1 > $Q/MAXC && cat $Q/MAXC"); [ "$r" = 1 ] || { lg "write of 1 not confirmed ('$r')"; exit 1; }
lg "MAXC set to 1 (window of at most $TMAX s)"
t0=$(date +%s); last=""
while :; do
  s=$($H "ls $A $R 2>/dev/null | wc -l" 2>/dev/null)
  [ "$s" != "$last" ] && lg "RUN.md5 present: ${s:-?} of 2"; last=$s
  [ "$s" = 2 ] && break
  [ $(( $(date +%s) - t0 )) -ge $TMAX ] && { lg "timeout after $TMAX s"; break; }
  sleep 20
done
restore
