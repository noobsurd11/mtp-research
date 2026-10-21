#!/usr/bin/env bash
# Relay finished cv02 outputs (21 Oct) to gaint cv02_noob_el via laptop, then MD5-verify.
set -uo pipefail
CV="ssh -o BatchMode=yes cv02@10.8.1.106"; GA="ssh -o BatchMode=yes noob@172.18.22.20"
DST=/home/noob/work/cv02_noob_el
declare -A SETS
SETS[el_alhvr]="REVISION reports experiments/al1_A5_s0 experiments/al1_A5_s1 experiments/al1_A5_s2 experiments/al1_BsM5_s0 experiments/al1_BsM5_s2 experiments/c1_A5_s0 experiments/c1_AL5_s0 experiments/c2_BsM5_s0 experiments/c3_AL5_s0 experiments/c3_CPS5_s0"
SETS[el_sk1]="REVISION REVISION.note d7_twin_train_cells.txt lanes_sk1.sh sk1_queue_d7yes.spec reports experiments/chk_A_5pct_s0 experiments/chk_A_5pct_s3 experiments/chk_BsD_5pct_s0 experiments/chk_off_metrics experiments/smoke_AB experiments/smoke_BsDB experiments/smoke_BsDB_lowema experiments/smoke_BsDB_lowthr experiments/smoke_BsDB_t0 experiments/smoke_BsDBx experiments/sk1_AB_5pct_s0 experiments/sk1_AB_5pct_s1"
ok=1
for d in el_alhvr el_sk1; do
  p=${SETS[$d]}
  echo "== $d $(date +%H:%M)"
  $GA "mkdir -p $DST/$d"
  $CV "cd /tmp/noob_el/$d && tar cf - $p" | $GA "cd $DST/$d && tar xf -" || { echo "tar FAILED $d"; ok=0; }
  a=$($CV "cd /tmp/noob_el/$d && find $p -type f -print0 | sort -z | xargs -0 md5sum" | md5sum)
  b=$($GA "cd $DST/$d && find $p -type f -print0 | sort -z | xargs -0 md5sum" | md5sum)
  n=$($GA "cd $DST/$d && find $p -type f | wc -l")
  if [ "$a" = "$b" ]; then echo "$d: $n files, MD5 manifest IDENTICAL"; else echo "$d: MD5 MISMATCH"; ok=0; fi
done
[ $ok = 1 ] && echo "RELAY OK $(date '+%d %b %H:%M IST')" || echo "RELAY HAD ERRORS"
