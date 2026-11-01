#!/bin/bash
# Fires the THIN-B3 opening (thin_post.sh) when all 15 THIN runs trained rc 0 AND PF2's opening ended rc 0 (its SUPPF s5-9
# per-cell files are the comparator). A THIN run with rc != 0 or a PF2 opening FAIL: "thin NOT scored (FAIL)" and stop.
set -u
cd /home/noob/work/el_thin
L=reports/thin/q/launch.log; PL=/home/noob/work/el_f3/reports/pf2/launch.log; GS=${GS:?}; DEPLOY=${DEPLOY:?}; M0B3=${M0B3:?}
cnt(){ grep -oE "trained thin_(SKR|CLD|B3)_100pct_s[5-9] rc=0" $L | sort -u | wc -l; }
bad(){ grep -E "trained thin_(SKR|CLD|B3)_100pct_s[5-9] rc=[1-9]" $L | head -1; }
echo "[$(date)] thin opening trigger armed (pid $$)" >> $L
until [ "$(cnt)" -ge 15 ] && grep -q "pf2 scoring done: post rc=0" $PL; do
  b=$(bad); [ -n "$b" ] && { echo "[$(date)] thin NOT scored (FAIL): $b" >> $L; exit 1; }
  grep -qE "pf2 scoring done: post rc=[1-9]|pf2 NOT scored" $PL && { echo "[$(date)] thin NOT scored (FAIL): PF2 opening did not end rc 0" >> $L; exit 1; }
  sleep 120; done
echo "[$(date)] thin scoring start (15 runs trained rc 0; PF2 opening rc 0)" >> $L
GS=$GS DEPLOY=$DEPLOY M0B3=$M0B3 bash reports/thin/scripts/thin_post.sh
