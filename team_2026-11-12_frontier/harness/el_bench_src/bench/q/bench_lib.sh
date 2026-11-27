#!/bin/bash
# elbench queue functions = s2c_lib.sh 4edcae9e generalised (any command; verify token per job). Caller sets Q (queue dir), L (launch
# log) and defines lg. Optional hook: tick (called each second while stop_verified waits). DRY=1: no signal ('would' lines).
# FAKEAPPS=<file>: compute-apps lines "pid,MiB" instead of nvidia-smi (tests). PROTECT (env): PIDs never touched (default 6206 finllm).
# Verify token of job NAME: its cmdline must hold "run_name=NAME" (harness trainer) or "--bench-run NAME" (external / infer jobs).
ME=${ME:-$(id -un)}; PROTECT=" ${PROTECT:-6206} "
SMI(){ timeout 5 nvidia-smi "$@" 2>/dev/null; }
apps(){ if [ -n "${FAKEAPPS:-}" ]; then cat "$FAKEAPPS"; else SMI --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' '; fi; }
cmdl(){ tr '\0' ' ' < /proc/$1/cmdline 2>/dev/null; }
owner(){ stat -c %U /proc/$1 2>/dev/null; }
psl(){ ps -o pid,user,lstart,args -p $1 2>/dev/null | tr '\n' '|' | sed 's/|$//'; }
has_token(){ case " $1 " in *" run_name=$2 "*|*" --bench-run $2 "*) return 0;; esac; return 1; }
# verify NAME PID: 0 iff alive, not protected, owned by $ME, live cmdline == the one recorded at launch, and it holds NAME's token.
verify(){ local n=$1 p=$2 c r u
  [ -n "$p" ] || { echo "empty PID"; return 1; }
  case "$PROTECT" in *" $p "*) echo "protected PID"; return 1;; esac
  [ -d /proc/$p ] || { echo "not alive"; return 1; }
  u=$(owner $p); [ "$u" = "$ME" ] || { echo "owner ${u:-?} != $ME"; return 1; }
  [ -s $Q/pids/$n.cmdline ] || { echo "no cmdline recorded at launch"; return 1; }
  c=$(cmdl $p); r=$(cat $Q/pids/$n.cmdline)
  [ "$c" = "$r" ] || { echo "cmdline differs from the one recorded at launch (now: $c)"; return 1; }
  has_token "$c" "$n" || { echo "cmdline lacks run_name=$n / --bench-run $n"; return 1; }
  return 0; }
# stop_verified NAME PID: verify -> SIGTERM -> wait <= 30 s -> if alive: verify again -> SIGKILL -> wait <= 10 s.
# rc 0 stopped, 2 refused before any signal, 3 re-check failed after SIGTERM (no SIGKILL), 4 alive after SIGKILL.
stop_verified(){ local n=$1 p=$2 why w=0
  why=$(verify $n $p) || { lg "  REFUSED $n pid $p: $why; no signal"; return 2; }
  lg "  verified $n pid $p (owner $ME, cmdline = recorded): $(psl $p)"
  if [ "${DRY:-0}" = 1 ]; then lg "  DRY: would send SIGTERM to $p, wait <= 30 s, re-verify, then SIGKILL $p only if alive and still verified"; return 0; fi
  kill -TERM $p; lg "  SIGTERM $p sent (rc $?)"
  while [ -d /proc/$p ] && [ $w -lt 30 ]; do sleep 1; w=$((w+1)); type tick >/dev/null 2>&1 && tick; done
  [ -d /proc/$p ] || { lg "  pid $p exited ${w}s after SIGTERM"; return 0; }
  why=$(verify $n $p) || { lg "  pid $p alive 30 s after SIGTERM but the re-check FAILED: $why; no SIGKILL"; return 3; }
  lg "  pid $p alive 30 s after SIGTERM; re-check passed (owner $ME, cmdline = recorded): $(psl $p)"
  kill -KILL $p; lg "  SIGKILL $p sent (rc $?)"; w=0
  while [ -d /proc/$p ] && [ $w -lt 10 ]; do sleep 1; w=$((w+1)); done
  [ -d /proc/$p ] && { lg "  pid $p STILL alive 10 s after SIGKILL"; return 4; }
  lg "  pid $p gone ${w}s after SIGKILL"; return 0; }
# outside: "pid:MiB" for every compute app not protected, not one of our recorded PIDs, holding > OUTSIDE_MIB (default 1024).
outside(){ local ours="$PROTECT" f lim=${OUTSIDE_MIB:-1024}
  [ "$lim" = 0 ] && return 0
  for f in $Q/pids/*.pid; do [ -e "$f" ] && ours="$ours$(tr -dc 0-9 < $f) "; done
  apps | while IFS=, read -r p m; do [ -n "$p" ] || continue; case "$ours" in *" $p "*) continue;; esac
    case "$m" in ''|*[!0-9]*) continue;; esac; [ "$m" -gt "$lim" ] && echo -n "$p:${m}MiB "; done; }
# startcheck STDOUT EXPECTED WAIT: 0 iff the first line of STDOUT matching the expected line's prefix (up to the first ':')
# equals EXPECTED within WAIT s (grep -m1 only; nothing else of the stdout is read).
startcheck(){ local f=$1 want=$2 t=0 got pre=${2%%:*}
  while [ $t -lt $3 ]; do got=$(grep -m1 -o "$pre: .*" "$f" 2>/dev/null); [ -n "$got" ] && break; sleep 2; t=$((t+2)); done
  if [ "$got" = "$want" ]; then echo "startup line OK: $got"; return 0; fi
  echo "startup line MISMATCH: got '${got:-none within $3 s}', want '$want'"; return 1; }
# prestart: 0 iff a start may be attempted now; logger / watcher gone -> HOLD; outside process -> wait (no HOLD).
prestart(){ local o
  [ -e $Q/HOLD ] && { echo "HOLD"; return 1; }
  kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || { touch $Q/HOLD; echo "gpumem logger gone; HOLD set"; return 1; }
  kill -0 "$(cat $Q/guard.pid 2>/dev/null)" 2>/dev/null || { touch $Q/HOLD; echo "auto-stop watcher gone; HOLD set"; return 1; }
  o=$(outside); [ -n "$o" ] && { echo "outside GPU process(es) > ${OUTSIDE_MIB:-1024} MiB: $o"; return 1; }
  return 0; }
# launch_run NAME WORKDIR CMD: start CMD (word-split, globbing off; its first word must be the python binary) as a plain
# background command in a subshell, so pids/NAME.pid = the python PID; stdout+stderr -> WORKDIR/experiments/NAME.stdout;
# env HF_HUB_OFFLINE=1, OMP_NUM_THREADS=JOB_THREADS (4).
# The subshell writes pids/NAME.rc and the 'trained' / 'done' lines (rc captured before any $(date)). Waits <= 20 s for a
# cmdline with NAME's token, records it in pids/NAME.cmdline (the guard's identity record). Sets LPID ('' if none).
launch_run(){ local name=$1 w=$2 cmd=$3 t=0 pp=""
  ( cd $w || exit 1; set -f; export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=${JOB_THREADS:-4}   # as s2c launch_run's inline env
    $cmd > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo $rc > $Q/pids/$name.rc; echo "[$(date '+%F %T')] trained $name rc=$rc" >> $L
    echo "[$(date '+%F %T')] done $name: final-step lines $(grep -c "${DONE_RX:-step 20000/20000}" experiments/$name.stdout), Traceback lines $(grep -c Traceback experiments/$name.stdout)" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  LPID=""
  while [ $t -lt 20 ]; do pp=$(cat $Q/pids/$name.pid 2>/dev/null)
    [ -n "$pp" ] && has_token "$(cmdl $pp)" "$name" && { LPID=$pp; break; }; sleep 1; t=$((t+1)); done
  [ -n "$LPID" ] && cmdl $LPID > $Q/pids/$name.cmdline; }
