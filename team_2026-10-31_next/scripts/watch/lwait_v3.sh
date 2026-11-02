#!/bin/bash
# runner (1 Nov 2026; team-lead option b; v2 2 Nov: + read-only B6 launch.log watch on cv02; v3: routine "trained rc=0" lines no longer wake): the ONE local waiter. Every 300 s: ssh-read new lines of gaint's
# /home/noob/work/runner_events/events.log; exit (= wake runner) on any new line. Every 3rd loop (15 min): one read-only cv02 poll
# (gaint cannot reach cv02: no key there, as it should be), appended to results/b6/cv02_polls.log; exit when the qualifying count
# (GPUs with no process > 4 GB) crosses 3 either way. Exit after MAXS s (default 6 h) or 3 failed gaint reads in a row.
# v2: on each cv02 poll, also the new lines of cv02 /tmp/noob_el/el_b6/q/launch.log (offset in results/b6/cv02_launch_off.txt); exits on a
# line matching FAIL|HOLD|rc=[1-9]|ALL TRAINED|b6q:|GUARD (not on rc=0 trained / start / config OK / databuild OK / lane skip lines).
# Usage: N0=<events line count already seen> bash lwait.sh
set -u
MAXS=${MAXS:-21600}; T0=$(date +%s); G=noob@172.18.22.20; EV=/home/noob/work/runner_events/events.log
N0=${N0:?}; PREV=${PREV:-QUAL}; i=0; gf=0
LOG=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/cv02_polls.log
Q='nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader,nounits; echo ===; nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits'
echo "start $(date '+%H:%M') pid $$ N0 $N0 cv02 prev $PREV"
while :; do
  sleep 300; i=$((i+1))
  if n=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $G "wc -l < $EV" 2>/dev/null); then gf=0
    [ "$n" -gt "$N0" ] && { echo "EVENTS $(date '+%H:%M') ($N0 -> $n):"; ssh -o BatchMode=yes $G "tail -n +$((N0+1)) $EV | head -40"; exit 0; }
  else gf=$((gf+1)); [ $gf -ge 3 ] && { echo "GAINT READ FAILED 3x $(date '+%H:%M')"; exit 0; }; fi
  if [ $((i % 3)) = 0 ]; then
    if s=$(ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$Q" 2>/dev/null); then
      r=$(echo "$s" | awk -F', *' '/^===/{p=1; next} !p{idx[$2]=$1; used[$1]=$3; mx[$1]=0; n++} p{g=idx[$1]; if ($3+0 > mx[g]) mx[g]=$3+0}
        END{q=""; c=0; d=""; for (j=0; j<n; j++){ if (mx[j] <= 4096){ c++; q=q j " " }; d=d sprintf("g%d %d/%d ", j, used[j], mx[j]) }; printf "%d|%s|%s\n", c, q, d}')
      IFS='|' read -r c ids det <<< "$r"; echo "$(date '+%F %T') | qualifying $c (ids ${ids% }) | used/maxproc MiB: $det" >> $LOG
      st=$([ "$c" -ge 3 ] && echo QUAL || echo NOT)
      [ "$st" != "$PREV" ] && { echo "CV02 CHANGE $(date '+%H:%M'): $PREV -> $st ($c GPUs)"; exit 0; }
    else echo "$(date '+%F %T') | poll failed" >> $LOG; fi
    OFF=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/cv02_launch_off.txt; o2=$(cat $OFF 2>/dev/null || echo 0)
    if b6=$(ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "f=/tmp/noob_el/el_b6/q/launch.log; [ -e \$f ] && { wc -l < \$f; tail -n +$((o2+1)) \$f | grep -E 'FAIL|HOLD|rc=[1-9]|ALL TRAINED|b6q:|GUARD' | cut -c1-250; }" 2>/dev/null) && [ -n "$b6" ]; then
      n2=$(echo "$b6" | head -1); hits=$(echo "$b6" | tail -n +2); echo $n2 > $OFF
      [ -n "$hits" ] && { echo "B6 CV02 $(date '+%H:%M'):"; echo "$hits"; exit 0; }
    fi
  fi
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M')"; exit 0; }
done
