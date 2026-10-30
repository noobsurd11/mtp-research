#!/bin/bash
# Local watcher: exits (to wake runner) on a lane event in gaint f1g, or after MAXS seconds. Read-only ssh.
MAXS=${MAXS:-10800}; T0=$(date +%s)
SEEN=$(ssh -o BatchMode=yes noob@172.18.22.20 'wc -l < /home/noob/work/el_f1/reports/f1g/launch.log' 2>/dev/null || echo 0)
while :; do
  S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 noob@172.18.22.20 'cd /home/noob/work/el_f1; L=reports/f1g/launch.log; n=$(wc -l < $L); echo "N=$n"; tail -n +'"$((SEEN+1))"' $L; grep -c Traceback experiments/f1_mim_pre_s0.stdout; grep -E "step [0-9]+/36500" experiments/f1_mim_pre_s0.stdout | tail -1 | cut -c40-200' 2>/dev/null)
  NEW=$(echo "$S" | sed -n 's/^N=//p')
  if [ -n "$NEW" ] && [ "$NEW" -gt "$SEEN" ]; then
    EV=$(echo "$S" | sed -n '2,/^[0-9]*$/p')
    if echo "$EV" | grep -qE "rc=[1-9]|F2 |pretrain rc|FAIL"; then echo "EVENT:"; echo "$S"; exit 0; fi
    SEEN=$NEW
  fi
  if echo "$S" | grep -qx "[1-9][0-9]*"; then echo "TRACEBACK in pretrain"; echo "$S"; exit 0; fi
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT status:"; echo "$S"; exit 0; }
  sleep 300
done
