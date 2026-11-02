#!/bin/bash
# runner (1 Nov 2026): start builder's B6 scorer GPU exact-match check (protocol_B6 s8.2; scorechk_gpu.sh a7322114) on gaint behind
# the shared start gate (gpu_gate.sh, flock, >= 120 s since any start) at 9,900 MiB free (m0-type pass; scoring gate).
# While it runs: FAST file (nq_gpumem samples every 1 s) if absent before, and our own 1 s peak of the scorer's python process.
# Event lines -> /home/noob/work/runner_events/events.log (wakes runner's local waiter). rc captured before $(date).
set -u
D=/home/noob/work/runner_b6chk; mkdir -p $D; EV=/home/noob/work/runner_events/events.log; GG=/home/noob/work/gpu_gate
S=/home/noob/work/b6_build/scripts; C=/home/noob/work/b6_build/check
ts(){ date '+%F %T'; }
if [ "$(md5sum < $S/scorechk_gpu.sh | cut -c1-8)" != a7322114 ] || [ "$(md5sum < $S/b6_score.py | cut -c1-8)" != 981b5f29 ] \
   || [ "$(md5sum < $S/b6_valcmp.py | cut -c1-8)" != 1ad95d68 ]; then echo "$(ts) b6chk: script md5 FAIL, not started" >> $EV; exit 1; fi
echo $$ > $D/wrapper.pid
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
echo "$(ts) b6chk: armed pid $$; waiting for gate 9900" >> $EV
gate_wait 9900 "b6 scorechk_gpu"
F0=0; [ -e $GG/FAST ] && F0=1; touch $GG/FAST
echo "$(ts) b6chk: gate pass (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB); start scorechk_gpu.sh" >> $EV
bash $S/scorechk_gpu.sh > $D/scorechk.out 2>&1 &
cp=$!; echo $cp > $D/scorechk.pid
pk=0; mf=999999
while kill -0 $cp 2>/dev/null; do
  kids=" $(ps -o pid= --ppid $cp | tr -d ' ' | tr '\n' ' ') "
  while IFS=, read -r p m; do case "$kids" in *" $p "*) [ "$m" -gt $pk ] && pk=$m;; esac; done \
    < <(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' ')
  f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0 | tr -d ' '); [ "$f" -lt $mf ] && mf=$f
  sleep 1
done
wait $cp; rc=$?
[ $F0 = 0 ] && rm -f $GG/FAST
echo "$(ts) b6chk: done rc=$rc (scorer python peak ${pk} MiB; min free ${mf} MiB); $(grep -E 'score_gpu rc=|valcmp_gpu rc=' $C/batch.log | tail -2 | tr '\n' ' ')" >> $EV
rm -f $D/wrapper.pid
