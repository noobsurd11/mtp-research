#!/bin/bash
# Fires the PF2 opening (pf2_post.sh) when all needed runs trained rc 0: 15, or the 10 R34 runs if gate 6 set RN_STOP.
# A needed run with rc != 0: "pf2 NOT scored (FAIL)" and stop (decision needed). No per-seed scoring.
set -u
cd /home/noob/work/el_f3
L=reports/pf2/launch.log; GS=${GS:?set GS}
need(){ [ -e reports/pf2/RN_STOP ] && echo 'SUP|SUPPF' || echo 'SUP|SUPPF|RN50PF'; }
cnt(){ grep -oE "trained pf2_($(need))_100pct_s[5-9] rc=0" $L | sort -u | wc -l; }
bad(){ grep -E "trained pf2_($(need))_100pct_s[5-9] rc=[1-9]" $L | head -1; }
tot(){ [ -e reports/pf2/RN_STOP ] && echo 10 || echo 15; }
echo "[$(date)] pf2 opening trigger armed (pid $$)" >> $L
until [ "$(cnt)" -ge "$(tot)" ]; do
  b=$(bad); [ -n "$b" ] && { echo "[$(date)] pf2 NOT scored (FAIL): $b" >> $L; exit 1; }; sleep 120; done
echo "[$(date)] pf2 scoring start ($(tot) runs trained rc 0)" >> $L
GS=$GS bash reports/pf2/scripts/pf2_post.sh
