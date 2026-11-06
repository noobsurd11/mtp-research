#!/bin/bash
# runner v2 (3 Nov 2026): SKR2C auto-stop watcher on gaint (protocol_SKR2C v1 91b76abd §2b; judge review b0d866a4 G1-G4, G7).
# Own process (tmux window, own PID -> $Q/guard.pid); own 1 s free-memory sampling (timeout 5 nvidia-smi; FAKE=<file>: the next line of
# the file instead). It does not depend on the queue or the gpumem logger. Functions from s2c_lib.sh (verify / stop_verified).
# Trigger: free < THR (2,048) MiB on N (3) consecutive samples. A failed / non-numeric read is logged, not counted, resets the count;
# 10 consecutive failed reads -> HOLD + one line (G4).
# On a trigger: HOLD first ($Q/HOLD: the queue starts nothing new; a stopped run is never restarted). Log the 3 trigger samples, the
# last 30 samples, the compute-apps list. Candidates = $Q/pids/<name>.pid with <name> a jobs-file name, no <name>.rc (finished), PID
# alive; each is verified (owner + exact cmdline recorded at launch + tokens); a failing one is REFUSED (logged, never signalled).
# Target = the newest verified (smallest etimes). stop_verified: SIGTERM, wait <= 30 s (sampled + logged), re-verify, SIGKILL.
# Then COOL (30) logged samples (with the wait samples and the 30 before: >= 60 s of trace around the event), the count restarts.
# A 2nd stop needs a fresh trigger and >= GAP (30) s since the first signal; at most MAXSTOPS (2) stops, later triggers logged only.
# DRY=1: no signal at all (stop_verified logs 'would'). Ends 60 s after 'S2C ALL TRAINED' in launch.log, GUARD_STOP, or MAXH (24) h,
# or at the end of a FAKE file. Log: $Q/autostop.log. Env: Q FAKE DRY THR N COOL GAP MAXSTOPS MAXH SLEEP.
set -u
Q=${Q:-/home/noob/work/s2c}; . ${LIB:-$Q/scripts/s2c_lib.sh}
J=$Q/s2c_jobs.txt; G=$Q/autostop.log; LL=$Q/launch.log; touch $LL
FAKE=${FAKE:-}; DRY=${DRY:-0}; THR=${THR:-2048}; N=${N:-3}; COOL=${COOL:-30}; GAP=${GAP:-30}; MAXSTOPS=${MAXSTOPS:-2}; MAXH=${MAXH:-24}; SLEEP=${SLEEP:-1}
T0=$(date +%s); END=0; N0=$(wc -l < $LL)
echo $$ > $Q/guard.pid
lg(){ echo "$(date '+%F %T') $*" >> $G; }
NAMES=" $(cut -d'|' -f1 $J | tr '\n' ' ') "
lg "guard start pid $$ (v2; FAKE ${FAKE:-none}; DRY $DRY; THR $THR MiB x $N; COOL $COOL; GAP $GAP s; MAXSTOPS $MAXSTOPS; jobs $(md5sum < $J | cut -c1-8); lib $(md5sum < ${LIB:-$Q/scripts/s2c_lib.sh} | cut -c1-8); Q $Q)"
declare -a TR=(); low=0; cool=0; stops=0; i=0; fails=0; LAST=0; TRIG=""
sample(){ i=$((i+1))
  if [ -n "$FAKE" ]; then fr=$(sed -n "${i}p" "$FAKE"); [ -n "$fr" ] || { lg "end of FAKE trace after $((i-1)) samples; stops $stops"; rm -f $Q/guard.pid; exit 0; }
  else fr=$(SMI --query-gpu=memory.free --format=csv,noheader,nounits -i 0 | tr -d ' '); fi
  TR+=("$(date +%T):$fr"); [ ${#TR[@]} -gt 30 ] && TR=("${TR[@]:1}"); }
tick(){ sample; lg "  wait sample: free $fr MiB"; }
pick(){ local f n p e best="" be=999999999 why
  for f in $Q/pids/*.pid; do
    [ -e "$f" ] || continue; n=$(basename $f .pid); p=$(tr -dc 0-9 < $f)
    case "$NAMES" in *" $n "*) ;; *) lg "  candidate $n: ignored (not a jobs-file name)"; continue;; esac
    [ -e $Q/pids/$n.rc ] && { lg "  candidate $n pid $p: finished (rc $(cat $Q/pids/$n.rc))"; continue; }
    [ -n "$p" ] && [ -d /proc/$p ] || { lg "  candidate $n pid ${p:-?}: not alive"; continue; }
    [ "$DRY" = 1 ] && grep -qx "$p" $Q/pids/.dry_stopped 2>/dev/null && { lg "  candidate $n pid $p: already stopped in this DRY run (treated as gone)"; continue; }
    why=$(verify $n $p) || { lg "  candidate $n pid $p: REFUSED ($why); never signalled"; continue; }
    e=$(ps -o etimes= -p $p 2>/dev/null | tr -d ' '); [ -n "$e" ] || { lg "  candidate $n pid $p: not alive"; continue; }
    lg "  candidate $n pid $p: verified, elapsed ${e}s"
    [ "$e" -lt "$be" ] && { be=$e; best="$p $n"; }
  done; echo "$best"; }
while :; do
  [ -e $Q/GUARD_STOP ] && { lg "guard stop (GUARD_STOP file)"; rm -f $Q/GUARD_STOP $Q/guard.pid; exit 0; }
  [ $(( $(date +%s) - T0 )) -ge $(( MAXH * 3600 )) ] && { lg "guard stop (MAXH $MAXH h)"; rm -f $Q/guard.pid; exit 0; }
  if [ $END = 0 ] && tail -n +$((N0+1)) $LL | grep -q "S2C ALL TRAINED"; then END=$(date +%s); lg "end line seen; guard stops in 60 s"; fi
  [ $END != 0 ] && [ $(( $(date +%s) - END )) -ge 60 ] && { lg "guard stop (queue ended)"; rm -f $Q/guard.pid; exit 0; }
  sample
  case "$fr" in ''|*[!0-9]*) fails=$((fails+1)); lg "sample $i: free read failed ('$fr', $fails in a row); not counted, count reset"; low=0; TRIG=""
    [ $fails = 10 ] && { touch $Q/HOLD; lg "  10 consecutive failed reads: HOLD set ($Q/HOLD)"; }; sleep $SLEEP; continue;; esac
  fails=0
  if [ $cool -gt 0 ]; then cool=$((cool-1)); lg "  post-stop sample: free $fr MiB (cool-down $cool left)"; sleep $SLEEP; continue; fi
  if [ "$fr" -lt "$THR" ]; then low=$((low+1)); TRIG="$TRIG ${TR[-1]}"; lg "low sample: free $fr MiB < $THR ($low/$N)"
  else [ $low -gt 0 ] && lg "free $fr MiB >= $THR: count reset (was $low/$N)"; low=0; TRIG=""; fi
  if [ $low -ge $N ]; then
    low=0; lg "TRIGGER: free < $THR on $N consecutive samples:$TRIG"; TRIG=""
    lg "  free trace before (last ${#TR[@]}): ${TR[*]}"
    lg "  compute-apps: $(apps | tr '\n' ' ')"
    touch $Q/HOLD; lg "  HOLD set ($Q/HOLD): the queue starts nothing new"
    if [ $stops -ge $MAXSTOPS ]; then lg "  cap: $stops of $MAXSTOPS stops done; trigger logged only, no signal"; cool=$COOL; sleep $SLEEP; continue; fi
    if [ $stops -ge 1 ] && [ $(( $(date +%s) - LAST )) -lt $GAP ]; then lg "  only $(( $(date +%s) - LAST )) s since the first stop (< $GAP): no signal"; cool=$COOL; sleep $SLEEP; continue; fi
    t=$(pick)
    if [ -z "$t" ]; then lg "  no verified live S2C run to stop; no signal"; cool=$COOL; sleep $SLEEP; continue; fi
    set -- $t; lg "  TARGET (newest verified) $2 pid $1; recorded cmdline: $(cat $Q/pids/$2.cmdline)"
    [ "$DRY" = 1 ] || LAST=$(date +%s)
    stop_verified $2 $1; rc=$?; lg "  stop result $2 pid $1: rc $rc (0 stopped / 2 refused / 3 re-check failed, no SIGKILL / 4 alive after SIGKILL)"
    [ $rc = 2 ] || { stops=$((stops+1)); [ "$DRY" = 1 ] && { LAST=$(date +%s); echo "$1" >> $Q/pids/.dry_stopped; }; }
    lg "  after the action: compute-apps: $(apps | tr '\n' ' '); ps: $(psl $1)"
    cool=$COOL
  fi
  sleep $SLEEP
done
