#!/bin/bash
# runner (1 Nov 2026; team-lead option b; v2 19:55 adds the A8 scoring log; v3 2 Nov adds the SKR2 + HC2 s2q queue / opening / smoke
# logs, s2 Traceback counts and the s2q gpumem liveness check; v4 2 Nov 17:5x (team-lead): early-warning ALERT at free < 2,560 MiB on 2 polls
# (the < 2,048 hard alert kept) and an OUTSIDE-LOW ALERT at free < 2,300 while a non-runner process is on the GPU; ops only): ONE gaint-side watcher in tmux, recorded PID, writing event lines to ONE events file
# /home/noob/work/runner_events/events.log ("YYYY-MM-DD HH:MM:SS <source>: <line>"). Read-only on every job; never prints or reads
# a training stdout beyond counting Traceback lines (grep -ho | wc -l). Poll every 30 s.
# Sources (new lines only, filtered): THIN queue / opening log, PF2E run log, runner smoke log, the HC + A8 queue log and its
# opening log (once they exist). Checks: Tracebacks in THIN / nq run stdouts (count only), GPU free < 2,048 MiB on 2 polls in a
# row, THIN gpumem logger alive until THIN's end line, nq gpumem logger alive while the nq queue runs.
# PID in /home/noob/work/runner_events/rwatch.pid; stop only by that PID (or the STOP file in the same dir).
set -u
E=/home/noob/work/runner_events; mkdir -p $E/off; EV=$E/events.log; touch $EV; echo $$ > $E/rwatch.pid
ev(){ echo "$(date '+%F %T') $1: $2" >> $EV; }
declare -A SRC=(
  [thin]="/home/noob/work/el_thin/reports/thin/q/launch.log|trained|scoring|NOT scored|FAIL|HOLD|not starting|deploy check|ALL TRAINED"
  [pf2e]="/home/noob/work/el_f3/reports/pf2e/run.log|start|end rc"
  [smk]="/home/noob/work/runner_smk/runner_smk.log|start|end"
  [nq]="/home/noob/work/nq/launch.log|trained|start |CONFIG|HOLD|FAIL|ALL TRAINED|dispatching|not starting|armed|skip"
  [nqpost]="/home/noob/work/nq/post.log|done|FAIL|NOT scored|start"
  [a8s]="/home/noob/work/a8_score/v1/a8_score.log|start condition|FAIL|NOT scored|refused|done: rc|HOLD|missing|changed"
  [s2q]="/home/noob/work/s2q/launch.log|trained|start |CONFIG|HOLD|FAIL|ALL TRAINED|dispatching|not starting|armed|skip|unset|unknown arm"
  [s2qpost]="/home/noob/work/s2q/post.log|done|FAIL|NOT scored|start|armed"
  [s2smk]="/home/noob/work/runner_smk/s2/smoke.log|trained|GUARD|MISMATCH|FAIL|smokes done" )
for k in "${!SRC[@]}"; do f=${SRC[$k]%%|*}; [ -e $E/off/$k ] || { [ -e "$f" ] && wc -l < "$f" > $E/off/$k || echo 0 > $E/off/$k; }; done
tb(){ grep -ho Traceback "$@" 2>/dev/null | wc -l; }
TB_THIN0=$(tb /home/noob/work/el_thin/experiments/thin_[SCB]*_100pct_s*.stdout); TB_NQ0=$(tb /home/noob/work/el_hc/experiments/hc_HC_100pct_s*.stdout /home/noob/work/el_f8/experiments/f8_A8*_4k_s*.stdout)
S2G="/home/noob/work/el_thin/experiments/skr2_*.stdout /home/noob/work/el_hc2/experiments/hc2_*.stdout"; TB_S20=$(tb $S2G)
LOW=0; EW=0; OL=0; ev rwatch "start pid $$ (v4; TB thin $TB_THIN0, nq $TB_NQ0, s2 $TB_S20)"
while :; do
  [ -e $E/STOP ] && { ev rwatch "stop (STOP file)"; rm -f $E/STOP $E/rwatch.pid; exit 0; }
  for k in "${!SRC[@]}"; do
    f=${SRC[$k]%%|*}; pat=${SRC[$k]#*|}; [ -e "$f" ] || continue
    n=$(wc -l < "$f"); o=$(cat $E/off/$k)
    if [ "$n" -gt "$o" ]; then tail -n +$((o+1)) "$f" | head -n $((n-o)) | grep -E "$pat" | cut -c1-300 | while IFS= read -r l; do ev $k "$l"; done; echo $n > $E/off/$k; fi
  done
  t=$(tb /home/noob/work/el_thin/experiments/thin_[SCB]*_100pct_s*.stdout); [ "$t" -gt "$TB_THIN0" ] && { ev ALERT "THIN Traceback count $TB_THIN0 -> $t"; TB_THIN0=$t; }
  t=$(tb /home/noob/work/el_hc/experiments/hc_HC_100pct_s*.stdout /home/noob/work/el_f8/experiments/f8_A8*_4k_s*.stdout); [ "$t" -gt "$TB_NQ0" ] && { ev ALERT "nq Traceback count $TB_NQ0 -> $t"; TB_NQ0=$t; }
  t=$(tb $S2G); [ "$t" -gt "$TB_S20" ] && { ev ALERT "s2 Traceback count $TB_S20 -> $t"; TB_S20=$t; }
  fr=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  if [ "$fr" -lt 2048 ]; then LOW=$((LOW+1)); else LOW=0; fi
  [ $LOW = 2 ] && ev ALERT "GPU free $fr MiB < 2048 on 2 polls"
  if [ "$fr" -lt 2560 ]; then EW=$((EW+1)); else EW=0; fi
  [ $EW = 2 ] && ev ALERT "early warning: GPU free $fr MiB < 2560 on 2 polls"
  # outside = a GPU process that is not a run_name= trainer, finllm, or one of our scorers
  OUTS=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ' | while IFS=, read -r p m; do
      a=$(ps -o args= -p "$p" 2>/dev/null); echo "$a" | grep -qE 'run_name=|finllm_chat|rescore_label_versions|m0_audit|rescore_logit_adjust|calib_dump|el_metrics|b6_score|enc_cosine|pf2_scuffign|scuff_train_iou' \
        || echo -n "$p:${m}MiB:$(echo "$a" | cut -c1-60 | tr ' ' '_') "; done)
  if [ "$fr" -lt 2300 ] && [ -n "$OUTS" ]; then OL=$((OL+1)); else OL=0; fi
  [ $OL = 1 ] && ev ALERT "OUTSIDE-LOW: GPU free $fr MiB < 2300 with outside GPU process(es): $OUTS"
  if ! grep -qE "thin scoring done|thin NOT scored" /home/noob/work/el_thin/reports/thin/q/launch.log && ! kill -0 "$(cat /home/noob/work/el_thin/reports/thin/q/gpumem.pid 2>/dev/null)" 2>/dev/null; then
    [ -e $E/off/thin_gm_alert ] || { ev ALERT "THIN gpumem logger gone before THIN's end line"; touch $E/off/thin_gm_alert; }; fi
  if [ -e /home/noob/work/nq/launch.log ] && grep -q "nq queue armed" /home/noob/work/nq/launch.log && ! grep -qE "nq scoring done|nq NOT scored" /home/noob/work/nq/post.log 2>/dev/null \
     && ! kill -0 "$(cat /home/noob/work/nq/gpumem.pid 2>/dev/null)" 2>/dev/null; then
    [ -e $E/off/nq_gm_alert ] || { ev ALERT "nq gpumem logger gone while the nq queue runs"; touch $E/off/nq_gm_alert; }; fi
  if [ -e /home/noob/work/s2q/launch.log ] && grep -q "s2q queue armed" /home/noob/work/s2q/launch.log && ! grep -qE "s2q scoring done|s2q NOT scored" /home/noob/work/s2q/post.log 2>/dev/null \
     && ! kill -0 "$(cat /home/noob/work/s2q/gpumem.pid 2>/dev/null)" 2>/dev/null; then
    [ -e $E/off/s2q_gm_alert ] || { ev ALERT "s2q gpumem logger gone while the s2q queue runs"; touch $E/off/s2q_gm_alert; }; fi
  sleep 30
done
