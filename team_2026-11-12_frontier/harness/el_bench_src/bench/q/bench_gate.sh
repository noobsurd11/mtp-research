#!/bin/bash
# elbench GPU start gate = gpu_gate.sh 00fabfdd (team 31 Oct) with two changes for dry tests only:
#   GG (env) = the gate dir (default the shared /home/noob/work/gpu_gate, so real starts serialise with every other queue);
#   FAKEFREE (env) = a file whose first line is used as free MiB instead of nvidia-smi; GAPSEC (env, default 120) = spacing.
# gate_try MIB LABEL: under flock GG/gate.lock: free >= MIB and >= GAPSEC s since the last start by anyone -> stamp, log, rc 0.
GG=${GG:-/home/noob/work/gpu_gate}; GAPSEC=${GAPSEC:-120}; mkdir -p $GG
_free(){ if [ -n "${FAKEFREE:-}" ]; then head -1 "$FAKEFREE"; else timeout 5 nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0 2>/dev/null | tr -d ' '; fi; }
gate_try(){ local need=$1 lab=${2:-job} ok f
  [ -e $GG/HOLD ] && return 1
  f=$(_free); case "$f" in ''|*[!0-9]*) return 1;; esac
  ok=$(flock $GG/gate.lock bash -c 'a=$(( $(date +%s) - $(stat -c %Y '$GG'/last_start 2>/dev/null || echo 0) )); '\
'if [ "$2" -ge "$1" ] && [ "$a" -ge "$3" ]; then touch '$GG'/last_start; echo "1 $2"; else echo "0 $2"; fi' _ "$need" "$f" "$GAPSEC")
  if [ "${ok%% *}" = 1 ]; then echo "$(date '+%F %T') pass $lab need $need free ${ok#* } pid $$" >> $GG/gate.log; return 0; fi
  return 1; }
