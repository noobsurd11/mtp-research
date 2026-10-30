#!/bin/bash
# gaint 5 s free-memory sampler (team-lead 30 Oct 02:4x): runs until the 3 current f2 runs (CP5 s1, DDeP5 s1, DDeP5 s0) all
# pass step 2050 (val@500/1000/1500/2000 + checkpoint@2000 each), at most 40 min. Logs reports/f2g/memwatch.log.
# If free < 2048 MiB on any sample: stop the newest lane at once (lane X: x_lane_v2.sh, its run_one.sh, DDeP5 s0 train.py),
# so nothing restarts in that slot, and log to launch.log (runner requeues by hand behind the v3 gate).
cd /home/noob/work/el_f2
O=reports/f2g/memwatch.log; L=reports/f2g/launch.log; T0=$(date +%s); MIN=999999
echo "[$(date)] memwatch start" >> $O
while :; do
  f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  [ "$f" -lt "$MIN" ] && MIN=$f
  s=""; n=0
  for r in f2_CP_5pct_s1 f2_DDeP_5pct_s1 f2_DDeP_5pct_s0; do
    st=$(grep -oE "step [0-9]+/20000" experiments/$r.stdout | tail -1 | grep -oE "^step [0-9]+" | grep -oE "[0-9]+")
    s="$s $r:${st:-0}"; [ "${st:-0}" -ge 2050 ] && n=$((n+1))
  done
  echo "$(date +%T) free $f min $MIN |$s | $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ')" >> $O
  if [ "$f" -lt 2048 ]; then
    XP=$(tmux display -p -t "=f2g:X" "#{pane_pid}"); LANE=$(pgrep -P $XP -f x_lane_v2.sh); RO=$(pgrep -P $LANE -f run_one.sh)
    PY=$(pgrep -P $RO -f train.py)
    kill $LANE $RO 2>/dev/null; kill $PY 2>/dev/null
    echo "[$(date)] memwatch TRIGGER (FAIL-SAFE): free $f MiB < 2048; stopped newest lane X (x_lane $LANE, run_one $RO, DDeP5 s0 train $PY); requeue by runner" | tee -a $O >> $L
    exit 0
  fi
  [ $n -ge 3 ] && { echo "[$(date)] memwatch DONE: min free $MIN MiB over val+ckpt of all 3 runs" >> $O; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge 2400 ] && { echo "[$(date)] memwatch TIMEOUT: min free $MIN MiB" >> $O; exit 0; }
  sleep 5
done
