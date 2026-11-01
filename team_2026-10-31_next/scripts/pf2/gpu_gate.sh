#!/bin/bash
# Shared GPU start gate on gaint (team 31 Oct, runner). Sourced by every runner-started GPU job (PF2 queue, PF2 post, smokes,
# builder's smokes), so all starts serialise on ONE lock: /home/noob/work/gpu_gate/gate.lock.
#   gate_wait MIB LABEL : wait until (under the flock) free GPU memory >= MIB and >= 120 s since the last start by anyone,
#                         then stamp last_start and log one line to gate.log. MIB = the job's measured peak + 2,048.
# HOLD: if /home/noob/work/gpu_gate/HOLD exists, nothing new starts (running jobs continue).
GG=/home/noob/work/gpu_gate; mkdir -p $GG
gate_wait(){ local need=$1 lab=${2:-job} ok
  while :; do
    [ -e $GG/HOLD ] && { sleep 60; continue; }
    ok=$(flock $GG/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y '$GG'/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch '$GG'/last_start; echo "1 $f"; else echo "0 $f"; fi' _ "$need")
    if [ "${ok%% *}" = 1 ]; then echo "$(date '+%F %T') pass $lab need $need free ${ok#* } pid $$" >> $GG/gate.log; break; fi
    sleep 30
  done; }
# gate_try MIB LABEL : one non-blocking attempt of the same check; returns 0 (and stamps / logs) if the start may go now.
gate_try(){ local need=$1 lab=${2:-job} ok
  [ -e $GG/HOLD ] && return 1
  ok=$(flock $GG/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y '$GG'/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch '$GG'/last_start; echo "1 $f"; else echo "0 $f"; fi' _ "$need")
  if [ "${ok%% *}" = 1 ]; then echo "$(date '+%F %T') pass $lab need $need free ${ok#* } pid $$" >> $GG/gate.log; return 0; fi
  return 1; }
