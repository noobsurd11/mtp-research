#!/bin/bash
# SKR2C opening driver: the ONE pre-registered opening of protocol_SKR2C (v1 LOCKED 91b76abd + §9; §3, §6; rulings_s2c_stage2.md 4),
# E1 opening #7 (same 50 test and 106 E1 cells as #5 / #6, 3rd look). New file (build_s2c_stage2.md §5: one manual driver, no watcher).
# Started ONLY by team-lead, in a gaint tmux session named s2c_open, with the registered FROZEN.md5 md5 as the only argument:
#   tmux new-session -d -s s2c_open "bash /home/noob/work/s2c/open/s2c_opening.sh <FROZEN.md5 md5, 32 hex>"
# Steps (each refusal / failure writes the end line and stops):
#   1. refuse (rc 2; one line in s2c/opening_refused.log; opening.log NOT written, so a corrected start is possible) unless: the
#      argument = md5 of open/FROZEN.md5; md5sum -c FROZEN.md5 passes; post/, post_work/, d_out/ and opening.log do not exist.
#   2. verdict R: GS=9900 bash s2c_post.sh (every GPU process waits at the shared gate gpu_gate.sh for >= 9,900 MiB free and >= 120 s
#      since any start; HOLD honoured). R's rc = its exit code AND its end line 's2c scoring done: post rc=<rc>' in post.log.
#   3. verdict D, ONLY if R ended rc 0: bash d/s2c_d_run.sh full (CPU fp32, CUDA hidden, nice 19, 8 threads), then the real-splits
#      assert on d_out (s2c_realsplits.py d), then record copies (D script / launcher md5s, d logs, the 10 members' latest.pth md5s)
#      and d_out/MANIFEST.md5.
#   4. ONE end line in /home/noob/work/s2c/opening.log: '[<date>] s2c opening done: R rc=<r> D rc=<d>' (D rc '-' if D did not run).
# PIDs: this script -> s2c/opening.pid; R's python PIDs -> s2c/post_pids.txt; D's -> s2c/d_run_full.pid, s2c/d_py_full.pid.
# To stop: the python PID first (post_pids.txt / d_py_full.pid), then its parent; the end line then carries rc != 0.
set -u
O=/home/noob/work/s2c/open; S=/home/noob/work/s2c; LOG=$S/opening.log
P=/home/noob/work/el-fault-detection/.venv/bin/python; X1=/home/noob/work/el_f1/reports/f1/ext117
CPU=(env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 nice -n 19)
FZ=${1:-}
end(){ echo "[$(date)] s2c opening done: R rc=$1 D rc=$2" >> $LOG; exit $3; }
no(){ echo "[$(date)] refused (nothing started, opening.log not written): $*" | tee -a $S/opening_refused.log >&2; exit 2; }
[ ! -e $LOG ] || no "$LOG exists (the opening is read once)"
echo "$FZ" | grep -qE '^[0-9a-f]{32}$' || no "argument must be the registered FROZEN.md5 md5 (32 hex)"
[ "$(md5sum < $O/FROZEN.md5 | cut -c1-32)" = "$FZ" ] || no "md5 of $O/FROZEN.md5 != $FZ"
(cd $O && md5sum -c --quiet FROZEN.md5) || no "md5sum -c FROZEN.md5 failed"
for d in $S/post $S/post_work $S/d_out; do [ ! -e $d ] || no "$d exists"; done
echo $$ > $S/opening.pid
echo "[$(date)] s2c opening start pid $$; FROZEN.md5 $FZ: md5sum -c OK ($(wc -l < $O/FROZEN.md5) files); R starts (GS 9900)" >> $LOG
# ---- 2. verdict R ----
GS=9900 bash $O/s2c_post.sh; r=$?
tail -n 1 $S/post.log 2>/dev/null | grep -q "s2c scoring done: post rc=$r\$" || { echo "R: exit $r but post.log end line differs" >> $LOG; [ $r = 0 ] && r=9; }
echo "[$(date)] R ended rc=$r" >> $LOG
[ $r = 0 ] || { echo "R rc != 0: D NOT run (protocol order: R's passes, then D)" >> $LOG; end $r - 1; }
# ---- 3. verdict D (CPU only) ----
bash $O/d/s2c_d_run.sh full; d=$?
echo "[$(date)] D ended rc=$d" >> $LOG
if [ $d = 0 ]; then
  echo "== $(date '+%F %T') realsplits d" > $S/d_realsplits.txt
  "${CPU[@]}" $P $O/s2c_realsplits.py d --wt /home/noob/work/el_f3 --ext $X1 $S/d_out >> $S/d_realsplits.txt 2>&1 || d=8
  echo "[$(date)] D real-splits assert rc=$([ $d = 0 ] && echo 0 || echo 1) (d_realsplits.txt)" >> $LOG
fi
if [ -d $S/d_out ]; then
  cp -p $O/d/s2c_d_infer.py $O/d/s2c_d_run.sh $S/d_out/ 2>/dev/null
  cp -p $S/d_run.log $S/d_full.log $S/d_out/ 2>/dev/null; [ -e $S/d_realsplits.txt ] && cp -p $S/d_realsplits.txt $S/d_out/
  for k in 10 11 12 13 14; do md5sum /home/noob/work/el_f3/experiments/s2c_SUPPF_100pct_s$k/checkpoints/latest.pth \
    /home/noob/work/el_thin/experiments/s2c_SKR01_100pct_s$k/checkpoints/latest.pth; done > $S/d_out/member_latest_md5.txt
  (cd $S/d_out && md5sum $(ls | grep -v '^MANIFEST.md5$') > MANIFEST.md5) || d=10
  echo "[$(date)] d_out/MANIFEST.md5 $(md5sum < $S/d_out/MANIFEST.md5 | cut -c1-32) ($(wc -l < $S/d_out/MANIFEST.md5) files)" >> $LOG
fi
end 0 $d $([ $d = 0 ] && echo 0 || echo 1)
