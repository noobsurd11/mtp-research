#!/bin/bash
# runner (1 Nov 2026): read-only cv02 GPU watcher for B6 (team-lead / user: B6 runs only on cv02, as one whole experiment, if >= 3
# GPUs qualify = no other user's process > 4 GB on that GPU). Every POLL s: ssh -a (no agent forwarding), BatchMode, nvidia-smi
# queries only; nothing is started or written on cv02. One line per poll to results/b6/cv02_polls.log:
#   time | qualifying GPUs (count, ids) | per GPU used MiB and max process MiB.
# Exits (an event) when the qualifying count crosses the threshold 3 in either direction, after 3 failed polls in a row, or MAXS s.
set -u
POLL=${POLL:-900}; MAXS=${MAXS:-21600}; T0=$(date +%s); H=cv02@10.8.1.106
LOG=/home/yugma/mtp/research/team_2026-10-31_next/results/b6/cv02_polls.log; mkdir -p "$(dirname $LOG)"
Q='nvidia-smi --query-gpu=index,uuid,memory.used --format=csv,noheader,nounits; echo ===; nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits'
poll(){ local s; s=$(ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 $H "$Q" 2>/dev/null) || return 1
  echo "$s" | awk -F', *' '/^===/{p=1; next} !p{idx[$2]=$1; used[$1]=$3; mx[$1]=0; n++} p{g=idx[$1]; if ($3+0 > mx[g]) mx[g]=$3+0}
    END{q=""; c=0; d=""; for (i=0; i<n; i++){ if (mx[i] <= 4096){ c++; q=q i " " }; d=d sprintf("g%d %d/%d ", i, used[i], mx[i]) }
        printf "%d|%s|%s\n", c, q, d}'; }
ok=0; prev=""; fails=0
echo "start $(date '+%F %T') pid $$ POLL $POLL MAXS $MAXS" >> $LOG
while :; do
  if r=$(poll) && [ -n "$r" ]; then fails=0; c=${r%%|*}
    IFS='|' read -r _ ids det <<< "$r"; echo "$(date '+%F %T') | qualifying $c (ids ${ids% }) | used/maxproc MiB: $det" >> $LOG
    st=$([ "$c" -ge 3 ] && echo QUAL || echo NOT)
    [ -z "$prev" ] && { prev=$st; echo "first poll $(date '+%H:%M'): $st ($c GPUs)"; }
    [ "$st" != "$prev" ] && { echo "CHANGE $(date '+%H:%M'): $prev -> $st ($c GPUs): $r"; exit 0; }
  else fails=$((fails+1)); echo "$(date '+%F %T') | poll failed ($fails)" >> $LOG
    [ $fails -ge 3 ] && { echo "POLL FAILED 3x $(date '+%H:%M')"; exit 0; }; fi
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M') last: $prev ($c GPUs)"; exit 0; }
  sleep $POLL
done
