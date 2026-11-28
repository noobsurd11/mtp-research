#!/bin/bash
# x4 OOM recovery (lead, 28 Nov 2026). Runs on gaint in tmux bench_x4_oomwatch; reads cv02 only through ssh (read-only),
# except that it places / appends job files through x4_queue.sh.
# Every POLL s: for each "trained <name> rc=<rc>" line of cv02 x4_w1 or x4_w1r with name x4_* and rc not 0 (a failed real
# training run, not yet handled in evidence/resumes.tsv):
#   - stdout B/experiments/<name>.stdout (B from the job's start line "deploy <7 hex>"): count of lines matching
#     "CUDA out of memory|OutOfMemoryError" (count only); checkpoints/latest.pth present or not.
#   - OOM and latest.pth present: resume line = the job's own line from harness/x4/jobs/*.tsv with field 9 = --resume
#     -> jobs/resume_<name>_<k>.tsv (+ .md5) -> queue x4_w1r (placed and armed with the first one, LPG 2, MAXC 4; appended
#     after). The resumed run writes into the same deploy dir; the x4_w1 relay (deploys.txt) relays it (keep x4_w1 open).
#   - otherwise: recorded as "FAILED, not resumed (reason)" for the lead.
# Record: evidence/resumes.tsv (time, name, attempt, rc, oom count, latest present, action, jobs file md5). Stop: touch
# evidence/OOMWATCH_STOP. GPU resume is reproducible only up to atomic-accumulation nondeterminism (F2 resume, 21 Nov).
set -u
H=$(dirname "$(readlink -f "$0")"); R=$H/evidence/resumes.tsv; POLL=${POLL:-120}; P=/home/noob/work/el-fault-detection/.venv/bin/python
SC(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
touch $R; echo "$(date '+%F %T')	-	-	-	-	-	watch start pid $$	-" >> $R
while [ ! -e $H/evidence/OOMWATCH_STOP ]; do
  L=$(SC "grep -h 'trained x4_' /tmp/noob_el/bench_q/x4_w1/launch.log /tmp/noob_el/bench_q/x4_w1r/launch.log 2>/dev/null | grep -v ' rc=0 '") || { sleep $POLL; continue; }
  while read -r l; do [ -n "$l" ] || continue
    n=$(echo "$l" | grep -oE 'trained x4_[a-z0-9_]+' | cut -d' ' -f2); rc=$(echo "$l" | grep -oE 'rc=[^ ]+' | cut -d= -f2)
    k=$(( $(grep -c "	$n	" $R) + 1 )); key="$(echo "$l" | cut -c2-20)"
    grep -q "	$n	.*	$key$" $R && continue
    d=$(SC "grep -h '\] start $n on GPU' /tmp/noob_el/bench_q/x4_w1/launch.log /tmp/noob_el/bench_q/x4_w1r/launch.log 2>/dev/null | tail -1 | grep -oE 'deploy [0-9a-f]{7}' | cut -d' ' -f2")
    B=/tmp/noob_el/bench_$d
    o=$(SC "grep -cE 'CUDA out of memory|OutOfMemoryError' $B/experiments/$n.stdout 2>/dev/null; test -s $B/experiments/$n/checkpoints/latest.pth && echo LATEST || echo NOLATEST")
    oc=$(echo "$o" | head -1); lt=$(echo "$o" | tail -1)
    if [ "${oc:-0}" -gt 0 ] && [ "$lt" = LATEST ]; then
      src=$(grep -h "^$n|" $H/jobs/w1_*.tsv | head -1)
      [ -n "$src" ] || { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$n" "$k" "$rc" "$oc" "$lt" "OOM but no job line found; not resumed" "$key" >> $R; continue; }
      f=$H/jobs/resume_${n}_$k.tsv
      echo "$src" | awk -F'|' 'BEGIN{OFS="|"} {$9="--resume"; print}' > $f
      { echo "$(md5sum < $f | cut -c1-32)  $(basename $f)"; echo "# resume of $n (attempt $k; trained rc $rc; OOM lines $oc; latest.pth present)"; } > $f.md5
      if SC "test -d /tmp/noob_el/bench_q/x4_w1r"; then a=$(bash $H/x4_queue.sh append w1r $f 2>&1 | tail -1)
      else a=$(bash $H/x4_queue.sh place w1r $f 2 4 2>&1 | tail -1; bash $H/x4_queue.sh arm w1r 2>&1 | grep -E 'ARMED|REFUSED' | tail -1); fi
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$n" "$k" "$rc" "$oc" "$lt" "RESUME queued: $(echo $a | cut -c1-160) (file md5 $(head -c 8 $f.md5))" "$key" >> $R
    else
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$n" "$k" "$rc" "${oc:-?}" "$lt" "FAILED, not resumed (not an OOM or no latest.pth): lead decides" "$key" >> $R
    fi
  done <<< "$L"
  sleep $POLL
done
echo "$(date '+%F %T')	-	-	-	-	-	watch stop (OOMWATCH_STOP)	-" >> $R
