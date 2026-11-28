#!/bin/bash
# x4 fallback (lead, 28 Nov 2026): at AT (default 11:00 IST, gaint clock) for every stage-P arm whose auto read has not
# finished: if exactly 4 of its 5 seed-5 runs are relayed, run a DESCRIPTIVE partial read of those 4 folds (arm s5 vs COMBO
# s5, same folds and cells on both sides, PF A/A on the same folds, same tool, all guards printed), header below. The full
# stage-P read (x4_auto_read.sh) still runs when the 5th fold lands. Output bench_reads/x4_<tag>_partial4/verdict.txt.
# Usage (tmux bench_x4_partial_at): bash x4_partial_at.sh "<tag>:<ARM>:<SHORT>:<METHOD>" ...   (queue w1, key swad)
set -u
H=$(dirname "$(readlink -f "$0")"); AT=${AT:-11:00}; L=$H/evidence/partial_at.log; RD=/home/noob/work/bench_relay/x4_w1
HDR="DESCRIPTIVE, 4 of 5 folds, not stage P; decides nothing under PATHFINDER_RULE.md"
echo "[$(date '+%F %T')] partial fallback armed for $AT: $*" >> $L
t=$(date -d "$AT" +%s); [ $t -le $(date +%s) ] && t=$(date -d "tomorrow $AT" +%s)
while [ $(date +%s) -lt $t ]; do sleep 60; done
for spec in "$@"; do IFS=: read -r tag arm sh me <<< "$spec"
  grep -q "AUTO READ DONE" $H/evidence/auto_$tag.log 2>/dev/null && { echo "[$(date '+%F %T')] $tag: full stage-P read already done; no partial read" >> $L; continue; }
  ok=""; miss=""; for k in 0 1 2 3 4; do [ -e $RD/.ok/x4_${sh}_f${k}_s5 ] && ok="$ok${ok:+,}$k" || miss="$miss$k"; done
  n=$(echo $ok | tr ',' '\n' | grep -c .)
  if [ "$n" != 4 ]; then echo "[$(date '+%F %T')] $tag: $n of 5 folds relayed (missing $miss); no partial read (rule: exactly 4)" >> $L; continue; fi
  echo "[$(date '+%F %T')] $tag: folds $ok relayed, $miss missing: DESCRIPTIVE partial read" >> $L
  bash $H/x4_queue.sh score w1 >> $L 2>&1
  SEEDS=5 FOLDS=$ok HEADER="$HDR (folds $ok; fold $miss not relayed at $AT IST)" bash $H/x4_read.sh ${tag}_partial4 "$arm=w1:$sh:$me:swad" > $H/evidence/read_${tag}_partial4.log 2>&1
  echo "[$(date '+%F %T')] $tag PARTIAL READ DONE rc=$?: /home/noob/work/bench_reads/x4_${tag}_partial4/verdict.txt" >> $L
  grep -E "^DESCRIPTIVE|^=>|^stageP" /home/noob/work/bench_reads/x4_${tag}_partial4/verdict.txt >> $L 2>/dev/null
done
