#!/bin/bash
# elbench job queue for gaint = s2c_queue.sh de31c533 (runner v3, 3 Nov) generalised to method cards and any command.
# NOT ARMED in tranche 1 (lead, 12 Nov). Functions from bench_lib.sh (verify / stop_verified / launch_run / prestart /
# startcheck / outside) and bench_gate.sh (shared flock gate: free >= gate and >= 120 s since any start by anyone; HOLD).
#
# Env: Q (queue dir, required), JOBS_MD5 (required), DEPLOY (required: expected el_bench commit prefix, or 'skip' in dry tests),
#      REPO (el_bench, default /home/noob/work/el_bench; bench.cards and the cards are read from it), W (workdir of harness jobs,
#      default REPO), P (python, default the house venv), LIVE_WAIT (s, default 240), OUTSIDE_MIB (default 1024; 0 = off),
#      GG / GAPSEC / FAKEFREE (gate), FAKEAPPS, CUDA_VISIBLE_DEVICES (exported to jobs as given; default unset).
# Files in Q: jobs.txt, MAXC (default 2), HOLD, pids/, launch.log, gpumem.pid / guard.pid (logger and auto-stop watcher alive).
# jobs.txt, one job per line:  name|card|seed|data_root|gate_mib|cmd|extra
#   harness job: card = repo-relative bench/methods/<m>.yaml, cmd empty: the queue renders
#                "$P -u scripts/train.py <extra> --config <card.config> --opts <python -m bench.cards opts ...>" (run_name=name);
#                extra (optional) = train.py flags, e.g. '--exit_after_step 1000' for a smoke_* job (it then exits rc 3 by design).
#   other job:   card = '-' or a card, cmd = full command whose first word is python and which holds "--bench-run <name>".
# Arming (any failure: one line, exit 1): jobs md5; deploy (HEAD = DEPLOY, no tracked change); every card validates and every
#   weights file md5 matches the card; every data_root has splits/{train,val,test}.txt (and passes SPLITS.md5 if present);
#   gate_mib >= the card's memory.gate_mib (or the card's gate is null and the job name starts with smoke_); logger + guard alive.
# Each start: prestart -> MAXC -> gate_try -> HOLD re-check -> deploy check -> launch_run -> live check before the next start:
#   harness: cfgcheck (python -m bench.cards cfgcheck: config_used.yaml == the card's rendered config) and startcheck (the first
#   'Labelled:' line == the one implied by data_root's lists); other: startcheck on 'BENCH_START: run=<name>'.
#   A failure: HOLD + stop_verified on that job (SIGTERM, 30 s, owner + cmdline re-check, SIGKILL).
# Never: a restart, an overwrite (an existing experiments/<name> is skipped), a signal to a process that fails verify.
# End line: "BENCH Q ALL DONE (n rc 0 of N)".
set -u
Q=${Q:?queue dir}; L=$Q/launch.log; J=$Q/jobs.txt; JOBS_MD5=${JOBS_MD5:?}; DEPLOY=${DEPLOY:?commit prefix or skip}
REPO=${REPO:-/home/noob/work/el_bench}; W=${W:-$REPO}; P=${P:-/home/noob/work/el-fault-detection/.venv/bin/python}
LIVE_WAIT=${LIVE_WAIT:-240}
HERE=$(cd "$(dirname "$0")" && pwd)
. $HERE/bench_gate.sh
. $HERE/bench_lib.sh
lg(){ echo "[$(date '+%F %T')] $*" >> $L; }
mkdir -p $Q/pids; touch $L; echo $$ > $Q/queue.pid
deploy_ok(){ [ "$DEPLOY" = skip ] && return 0
  local h; h=$(git -C $REPO rev-parse HEAD) || return 1
  case "$h" in "$DEPLOY"*) ;; *) return 1;; esac
  [ -z "$(git -C $REPO status --short --untracked-files=no)" ]; }
cards_py(){ (cd $REPO && $P -m bench.cards "$@"); }
cnt(){ grep -c . "$1"; }
want_line(){ local r=$1; echo "Labelled: $(cnt $r/splits/train.txt) ($r/splits/train.txt)  unlabelled: 0 (-)  val: $(cnt $r/splits/val.txt)  test: $(cnt $r/splits/test.txt)"; }
card_gate(){ (cd $REPO && $P -c 'import sys, yaml; m = yaml.safe_load(open(sys.argv[1]))["memory"]; print(m["gate_mib"])' "$1"); }
card_weights(){ (cd $REPO && $P -c 'import sys, yaml; [print(w["md5"], w["path"]) for w in yaml.safe_load(open(sys.argv[1]))["weights"] or []]' "$1"); }
fail(){ lg "bench q: $1; not starting"; exit 1; }

# ---- arming
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || fail "jobs md5 FAIL"
deploy_ok || fail "deploy check FAIL ($REPO HEAD != $DEPLOY or tracked changes)"
mapfile -t JOBS < $J
declare -A CMD=()
for j in "${JOBS[@]}"; do
  IFS='|' read -r name card seed root gate cmd extra <<< "$j"
  [ -n "$name" ] && [ -n "$gate" ] || fail "bad job line: $j"
  case "$gate" in *[!0-9]*) fail "$name: gate '$gate' not a number";; esac
  [ -d "$root/splits" ] && [ -s $root/splits/train.txt ] && [ -s $root/splits/val.txt ] && [ -s $root/splits/test.txt ] || fail "$name: data root $root lacks splits"
  [ -e $root/SPLITS.md5 ] && { (cd $root && md5sum -c --quiet SPLITS.md5) || fail "$name: $root SPLITS.md5 check FAIL"; }
  if [ "$card" != - ]; then
    cards_py validate $card > /dev/null || fail "$name: card $card invalid"
    while read -r m f; do [ -n "$m" ] || continue; [ "$(md5sum < $f | cut -c1-32)" = "$m" ] || fail "$name: weights $f md5 != card"; done < <(card_weights $card)
    cg=$(card_gate $card)
    if [ "$cg" = None ]; then case "$name" in smoke_*) ;; *) fail "$name: card $card has no measured gate (smoke first)";; esac
    elif [ "$gate" -lt "$cg" ]; then fail "$name: gate $gate < card gate $cg"; fi
  fi
  if [ -z "$cmd" ]; then
    [ "$card" != - ] || fail "$name: no card and no command"
    cfgf=$(cd $REPO && $P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["config"])' $card)
    case "$extra" in ''|--exit_after_step\ [0-9]*) ;; *) fail "$name: extra '$extra' not allowed (only --exit_after_step N)";; esac
    [ -z "$extra" ] || case "$name" in smoke_*) ;; *) fail "$name: extra args only for smoke_* jobs";; esac
    CMD[$name]="$P -u scripts/train.py ${extra:+$extra }--config $cfgf --opts $(cards_py opts $card --seed $seed --run-name $name --data-root $root)"
  else
    has_token "$cmd" "$name" || fail "$name: command lacks --bench-run $name / run_name=$name"
    CMD[$name]=$cmd
  fi
done
for n in "${!CMD[@]}"; do echo "$n|${CMD[$n]}"; done | sort > $Q/jobs_rendered.txt
kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null || fail "gpumem logger (bench_gpumem.sh) not running"
kill -0 "$(cat $Q/guard.pid 2>/dev/null)" 2>/dev/null || fail "auto-stop watcher (bench_guard.sh) not running"
lg "bench q armed: ${#JOBS[@]} jobs (md5 $JOBS_MD5), rendered $(md5sum < $Q/jobs_rendered.txt | cut -c1-8), deploy $DEPLOY, MAXC $(cat $Q/MAXC 2>/dev/null || echo 2), lib $(md5sum < $HERE/bench_lib.sh | cut -c1-8), gate $(md5sum < $HERE/bench_gate.sh | cut -c1-8) (GG $GG, gap $GAPSEC s), outside > ${OUTSIDE_MIB:-1024} MiB waits, gpumem $(cat $Q/gpumem.pid), guard $(cat $Q/guard.pid), pid $$"

alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; [ -e "${f%.pid}.rc" ] && continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
LASTR=""
for j in "${JOBS[@]}"; do
  IFS='|' read -r name card seed root gate cmd extra <<< "$j"
  if [ -e $W/experiments/$name ] || [ -e $W/experiments/$name.stdout ]; then lg "skip $name (exists)"; continue; fi
  GW=0
  while :; do
    r=$(prestart) || { case "$r" in HOLD) ;; *) [ "$r" != "$LASTR" ] && lg "bench q: $r (before start of $name); new starts wait";; esac; LASTR=$r; sleep ${POLL:-60}; continue; }
    [ -n "$LASTR" ] && [ "$LASTR" != HOLD ] && lg "bench q: start conditions clear again"; LASTR=""
    MAXC=$(cat $Q/MAXC 2>/dev/null || echo 2)
    [ "$(alive)" -ge "$MAXC" ] && { sleep 10; continue; }
    if ! gate_try $gate "bench $name"; then [ $GW = 0 ] && lg "bench q: $name waits for the gate (need $gate MiB free and >= $GAPSEC s since the last start)"; GW=1; sleep 10; continue; fi
    [ -e $Q/HOLD ] && { lg "bench q: HOLD seen after the gate pass for $name; not starting"; continue; }
    break
  done
  deploy_ok || { lg "bench q: deploy check FAIL at start of $name; HOLD set"; touch $Q/HOLD; continue; }
  lg "start $name (card $card, seed $seed, root $root, gate $gate; alive $(alive); MAXC $MAXC)"
  launch_run $name $W "${CMD[$name]}"; pp=$LPID
  if [ -n "$pp" ]; then lg "pid $name $pp (python; parent $(ps -o ppid= -p $pp | tr -d ' ')); cmdline recorded ($(md5sum < $Q/pids/$name.cmdline | cut -c1-8)): $(psl $pp)"
  else lg "bench q: no cmdline with $name's token within 20 s (pid file $(cat $Q/pids/$name.pid 2>/dev/null)); HOLD set"; touch $Q/HOLD; continue; fi
  ok=1
  if [ -z "$cmd" ]; then
    c=$W/experiments/$name/config_used.yaml; t=0
    while [ ! -s $c ] && [ $t -lt $LIVE_WAIT ]; do sleep 5; t=$((t+5)); done
    if [ -s $c ]; then m=$(cards_py cfgcheck $card --config $c --seed $seed --run-name $name --data-root $root) || ok=0
    else m="no config_used.yaml after $LIVE_WAIT s"; ok=0; fi
    lg "$name $m"
    if [ $ok = 1 ]; then m=$(startcheck $W/experiments/$name.stdout "$(want_line $root)" $LIVE_WAIT) || ok=0; lg "$name $m"; fi
  else
    m=$(startcheck $W/experiments/$name.stdout "BENCH_START: run=$name" $LIVE_WAIT) || ok=0; lg "$name $m"
  fi
  if [ $ok = 0 ]; then lg "bench q: live check FAILED for $name: HOLD + stop by verified PID"; touch $Q/HOLD; stop_verified $name "$pp"; rc=$?; lg "bench q: stop of $name rc $rc"; fi
done
lg "bench q: all jobs dispatched; waiting"
wait
NM=$(printf '%s\n' "${JOBS[@]}" | cut -d'|' -f1 | paste -sd'|')
lg "BENCH Q ALL DONE ($(grep -cE "trained ($NM) rc=0\$" $L) rc 0 of ${#JOBS[@]}; pid $$)"
