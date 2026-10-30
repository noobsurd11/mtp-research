#!/bin/bash
# Local watcher for the cv02 DDeP pretraining (read-only ssh). On "ddep rc=0" it runs relay_ddep_cv02.sh (cv02 -> laptop
# -> gaint, md5 both hops) and exits; on rc != 0, a Traceback, the f2ddep tmux session gone, or MAXS seconds it exits.
MAXS=${MAXS:-14400}; T0=$(date +%s); CV=cv02@10.8.1.106
D=$(cd "$(dirname "$0")" && pwd); STG=${STG:?laptop staging dir}
Q='cd /tmp/noob_el/el_f2; echo "RC=$(grep -o "ddep rc=[0-9]*" reports/f2/ddep_cv02.log | tail -1 | cut -d= -f2)"; echo "TB=$(grep -c Traceback experiments/f2_ddep_pre_s0.stdout)"; tmux has-session -t "=f2ddep" 2>/dev/null && echo SESS=1 || echo SESS=0; grep -E "step [0-9]+/40000" experiments/f2_ddep_pre_s0.stdout | tail -1 | cut -c1-200'
while :; do
  S=$(ssh -o BatchMode=yes -o ConnectTimeout=20 $CV "$Q" 2>/dev/null)
  if [ -n "$S" ]; then
    RC=$(echo "$S" | sed -n 's/^RC=//p'); TB=$(echo "$S" | sed -n 's/^TB=//p'); SESS=$(echo "$S" | sed -n 's/^SESS=//p')
    if [ "$RC" = 0 ]; then echo "DDeP DONE $(date '+%H:%M')"; echo "$S"; bash $D/relay_ddep_cv02.sh "$STG"; exit 0; fi
    [ -n "$RC" ] && { echo "DDeP FAILED rc=$RC"; echo "$S"; exit 0; }
    [ "${TB:-0}" -gt 0 ] && { echo "DDeP TRACEBACK"; echo "$S"; exit 0; }
    [ "$SESS" = 0 ] && { echo "f2ddep tmux session GONE without rc"; echo "$S"; exit 0; }
  fi
  [ $(( $(date +%s) - T0 )) -ge $MAXS ] && { echo "TIMEOUT $(date '+%H:%M')"; echo "$S"; exit 0; }
  sleep 300
done
