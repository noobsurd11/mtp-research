#!/bin/bash
# runner (3 Nov 2026): SKR2C shared functions, sourced by s2c_queue.sh and s2c_guard.sh (protocol_SKR2C v1 91b76abd §2b; judge
# review_s2c_stage1_code b0d866a4 G1-G6). Caller sets Q (queue dir) and defines lg (one log line). Optional caller hook: tick (called
# once per second while stop_verified waits; the guard samples free memory there). DRY=1: no signal is ever sent ('would' lines).
# FAKEAPPS=<file>: compute-apps lines "pid,MiB" read from the file instead of nvidia-smi (unit tests).
ME=${ME:-$(id -un)}
SMI(){ timeout 5 nvidia-smi "$@" 2>/dev/null; }                      # G4: no nvidia-smi call may hang a loop
apps(){ if [ -n "${FAKEAPPS:-}" ]; then cat "$FAKEAPPS"; else SMI --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr -d ' '; fi; }
cmdl(){ tr '\0' ' ' < /proc/$1/cmdline 2>/dev/null; }
owner(){ stat -c %U /proc/$1 2>/dev/null; }
psl(){ ps -o pid,user,lstart,args -p $1 2>/dev/null | tr '\n' '|' | sed 's/|$//'; }
# verify NAME PID: 0 iff PID alive, not 6206, owned by $ME, its cmdline == the one recorded at launch ($Q/pids/NAME.cmdline) and
# holding scripts/train.py + the token run_name=NAME. Else prints the reason, returns 1. (G1 exact equality; G2 owner)
verify(){ local n=$1 p=$2 c r u
  [ -n "$p" ] || { echo "empty PID"; return 1; }
  [ "$p" = 6206 ] && { echo "finllm PID"; return 1; }
  [ -d /proc/$p ] || { echo "not alive"; return 1; }
  u=$(owner $p); [ "$u" = "$ME" ] || { echo "owner ${u:-?} != $ME"; return 1; }
  [ -s $Q/pids/$n.cmdline ] || { echo "no cmdline recorded at launch"; return 1; }
  c=$(cmdl $p); r=$(cat $Q/pids/$n.cmdline)
  [ "$c" = "$r" ] || { echo "cmdline differs from the one recorded at launch (now: $c)"; return 1; }
  case " $c " in *scripts/train.py*" run_name=$n "*) ;; *) echo "cmdline lacks scripts/train.py + run_name=$n"; return 1;; esac
  return 0; }
# stop_verified NAME PID: verify -> SIGTERM -> wait <= 30 s (tick each s) -> if alive: verify again (owner + exact cmdline) -> SIGKILL
# -> wait <= 10 s. Returns 0 stopped, 2 refused before any signal, 3 re-check failed after SIGTERM (no SIGKILL), 4 alive after SIGKILL.
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
# outside: prints "pid:MiB" for every compute app that is not 6206, not one of our recorded trainer PIDs, and holds > 1024 MiB (G5).
outside(){ local ours=" 6206 " f
  for f in $Q/pids/*.pid; do [ -e "$f" ] && ours="$ours$(tr -dc 0-9 < $f) "; done
  apps | while IFS=, read -r p m; do [ -n "$p" ] || continue; case "$ours" in *" $p "*) continue;; esac
    case "$m" in ''|*[!0-9]*) continue;; esac; [ "$m" -gt 1024 ] && echo -n "$p:${m}MiB "; done; }
# startcheck STDOUT EXPECTED WAIT: 0 iff the first 'Labelled:' line of STDOUT (grep -m1 only; G6) equals EXPECTED within WAIT s.
startcheck(){ local f=$1 want=$2 t=0 got
  while [ $t -lt $3 ]; do got=$(grep -m1 -o 'Labelled: .*' "$f" 2>/dev/null); [ -n "$got" ] && break; sleep 2; t=$((t+2)); done
  if [ "$got" = "$want" ]; then echo "startup line OK: $got"; return 0; fi
  echo "startup line MISMATCH: got '${got:-none within $3 s}', want '$want'"; return 1; }
# prestart: 0 iff a start may be attempted now, else prints the reason. Logger / watcher gone -> also touches $Q/HOLD (G4/G5 rules).
prestart(){ local o
  [ -e $Q/HOLD ] && { echo "HOLD"; return 1; }
  kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || { touch $Q/HOLD; echo "gpumem logger gone; HOLD set"; return 1; }
  kill -0 "$(cat $Q/guard.pid 2>/dev/null)" 2>/dev/null || { touch $Q/HOLD; echo "auto-stop watcher gone; HOLD set"; return 1; }
  o=$(outside); [ -n "$o" ] && { echo "outside GPU process(es) > 1024 MiB: $o"; return 1; }
  return 0; }
# launch_run NAME WORKTREE OPTS: start the trainer (subshell; python as a plain background command, so pids/NAME.pid = its PID;
# pids/NAME.rc + 'trained' / 'done' lines in $L at its end), then wait <= 20 s for the exec and record /proc cmdline in
# pids/NAME.cmdline (the watcher's identity record). Uses globals P, L, Q. Sets LPID (empty if no train.py cmdline within 20 s).
launch_run(){ local name=$1 w=$2 opts=$3 t=0 pp=""
  ( cd $w || exit 1
    HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts $opts > experiments/$name.stdout 2>&1 &
    pp=$!; echo $pp > $Q/pids/$name.pid
    wait $pp; rc=$?; echo $rc > $Q/pids/$name.rc; echo "[$(date)] trained $name rc=$rc" >> $L
    echo "[$(date)] done $name: 'step 20000/20000' lines $(grep -c 'step 20000/20000' experiments/$name.stdout), Traceback lines $(grep -c Traceback experiments/$name.stdout)" >> $L ) &
  echo "$name subshell $!" >> $Q/pids/subshells.txt
  LPID=""
  while [ $t -lt 20 ]; do pp=$(cat $Q/pids/$name.pid 2>/dev/null)
    [ -n "$pp" ] && case " $(cmdl $pp) " in *scripts/train.py*" run_name=$name "*) LPID=$pp; break;; esac; sleep 1; t=$((t+1)); done
  [ -n "$LPID" ] && cmdl $LPID > $Q/pids/$name.cmdline; }
