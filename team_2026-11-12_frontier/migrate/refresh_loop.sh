#!/usr/bin/env bash
# Laptop side: first the full tree and fetched papers, then a refresh every 10 minutes until migrate/STOP_SYNC exists.
# The main session file, history and settings are not copied again (a session may already run on gaint).
cd /home/yugma/mtp/research/team_2026-11-12_frontier || exit 1
L=migrate/sync.log; H=noob@172.18.22.20; E="ssh -o BatchMode=yes -o ConnectTimeout=10"
n=0
while [ ! -e migrate/STOP_SYNC ]; do
  n=$((n+1)); t0=$(date '+%F %T')
  if bash migrate/sync_to_gaint.sh refresh > migrate/sync_last.out 2>&1; then
    $E $H "echo 'tree synced from the laptop: started $t0, ended $(date '+%F %T')' > /home/yugma/mtp/.last_sync_from_laptop"
    echo "[$(date '+%F %T')] refresh $n ok (started $t0)" >> $L
  else echo "[$(date '+%F %T')] refresh $n FAILED: $(tail -1 migrate/sync_last.out)" >> $L; fi
  if [ $n = 1 ] && [ -d /home/yugma/papers ]; then
    rsync -a --partial -e "$E" /home/yugma/papers/ $H:/home/yugma/papers/ && $E $H 'chmod 700 /home/yugma/papers' && echo "[$(date '+%F %T')] fetched papers copied" >> $L
  fi
  for i in $(seq 1 60); do [ -e migrate/STOP_SYNC ] && break; sleep 10; done
done
echo "[$(date '+%F %T')] loop stopped by STOP_SYNC" >> $L
