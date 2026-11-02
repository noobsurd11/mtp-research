#!/bin/bash
# runner v3 (3 Nov 2026): SKR2C training queue on gaint (protocol_SKR2C v1 91b76abd; TRAINING ONLY: no scoring, no opening trigger).
# From s2q_queue_v3.sh 928742a0: queue dir /home/noob/work/s2c; arms SKR01 (el_thin c9bbb02) and SUPPF (el_f3 e544133); gates
# GATE_SKR01 / GATE_SUPPF from env (measured peak + 2,048); MAXC default 2 (file MAXC); exp_<arm>.txt = the config diff vs
# pf2_SUPPF_100pct_s5 (data.root (+ skel_recall)); no AFTER / chained queue; own PID -> queue.pid; end line 'S2C ALL TRAINED'.
# v3 (judge review b0d866a4 G1, G4-G6; coach v1 §2b), functions from s2c_lib.sh:
#   - arming re-checks the data root (SPLITS.md5 -c, test.txt = val.txt, labeled link target) and that the gpumem logger and the
#     auto-stop watcher (guard.pid) are alive; before every start both are re-checked (gone -> HOLD + one line);
#   - prestart (lib): new starts wait (one line per episode, re-checked every 60 s) while a GPU process that is not finllm 6206 and not one of our
#     recorded trainer PIDs holds > 1,024 MiB; HOLD is re-checked after a gate pass;
#   - launch_run (lib): the trainer is a plain background command, so pids/<name>.pid = the python PID; after its exec the full /proc cmdline is written to
#     pids/<name>.cmdline (the watcher's identity record); the subshell writes pids/<name>.rc when the run ends;
#   - live check before the next start: config_used.yaml diff (cfgcheck) and the stdout's first 'Labelled:' line (grep -m1 only) must
#     equal the root's; on a mismatch that run is stopped by stop_verified (SIGTERM, 30 s, owner + cmdline re-check, SIGKILL) + HOLD;
#   - every nvidia-smi call has timeout 5; per-run 'done' line = grep counts of 'step 20000/20000' and 'Traceback' in its stdout.
set -u
Q=/home/noob/work/s2c; L=$Q/launch.log; J=$Q/s2c_jobs.txt; DR=/home/noob/work/s2c_root
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
. $Q/scripts/s2c_lib.sh
lg(){ echo "[$(date)] $*" >> $L; }
P=/home/noob/work/el-fault-detection/.venv/bin/python
JOBS_MD5=${JOBS_MD5:?}; mkdir -p $Q/pids; echo $$ > $Q/queue.pid
WANT="Labelled: 478 ($DR/splits/train.txt)  unlabelled: 0 (-)  val: 54  test: 54"
ARMS=$(cut -d'|' -f3 $J | sort -u | tr '\n' ' ')
declare -A WT=([SKR01]=/home/noob/work/el_thin [SUPPF]=/home/noob/work/el_f3) DEP=([SKR01]=c9bbb02 [SUPPF]=e544133) GATE=([SKR01]=${GATE_SKR01:-} [SUPPF]=${GATE_SUPPF:-})
R0=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
declare -A REF=([SKR01]=$R0 [SUPPF]=$R0)
deploy_ok(){ local w=$1 d=$2; [ "$(git -C $w rev-parse --short=7 HEAD)" = "$d" ] && [ -z "$(git -C $w status --short --untracked-files=no)" ]; }
gm_ok(){ kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null; }
gd_ok(){ kill -0 "$(cat $Q/guard.pid 2>/dev/null)" 2>/dev/null; }
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || { lg "s2c jobs file md5 FAIL"; exit 1; }
(cd $DR/splits && md5sum -c --quiet ../SPLITS.md5) && [ "$(md5sum < $DR/SPLITS.md5 | cut -c1-8)" = 24568cdb ] && cmp -s $DR/splits/test.txt $DR/splits/val.txt \
  && [ "$(readlink $DR/labeled)" = /home/noob/work/el-fault-detection/data/labeled ] || { lg "s2c: data root check FAIL ($DR)"; exit 1; }
for a in $ARMS; do
  case $a in SKR01|SUPPF) ;; *) lg "s2c: unknown arm $a in jobs file"; exit 1;; esac
  [ -n "${GATE[$a]}" ] || { lg "s2c: gate unset for arm $a"; exit 1; }
  deploy_ok ${WT[$a]} ${DEP[$a]} || { lg "s2c deploy check FAIL $a (${WT[$a]} != ${DEP[$a]} or tracked changes)"; exit 1; }
  [ -e $Q/exp_$a.txt ] || { lg "s2c: exp_$a.txt missing"; exit 1; }
  [ "$(cut -c1-7 ${WT[$a]}/REVISION)" = "${DEP[$a]}" ] || { lg "s2c: REVISION stamp FAIL $a"; exit 1; }; done
gm_ok || { lg "s2c: own gpumem logger (s2c_gpumem.sh) not running, not starting"; exit 1; }
gd_ok || { lg "s2c: auto-stop watcher (s2c_guard.sh) not running, not starting"; exit 1; }
mapfile -t JOBS < $J
cfgcheck(){ local name=$1 k=$2 arm=$3 c=${WT[$3]}/experiments/$1/config_used.yaml t=0 d e
  while [ ! -s $c ] && [ $t -lt 240 ]; do sleep 5; t=$((t+5)); done
  [ -s $c ] || { lg "CONFIG FAIL $name: no config_used.yaml after 240 s"; return 1; }
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' ${REF[$arm]}) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(sort $Q/exp_$arm.txt)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then lg "config OK $name vs pf2_SUPPF_100pct_s5: seed $k + $arm diff (exp_$arm) only"; return 0; fi
  lg "CONFIG FAIL $name: [$(echo "$d" | tr '\n' ' ')] seed_ok $(grep -qx "seed: $k" $c && echo 1 || echo 0)"; return 1; }
alive(){ local n=0 f; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; [ -e "${f%.pid}.rc" ] && continue; kill -0 "$(cat $f)" 2>/dev/null && n=$((n + 1)); done; echo $n; }
lg "s2c queue armed (v3): ${#JOBS[@]} jobs ($(basename $J), md5 $JOBS_MD5), arms $ARMS, gates SKR01 ${GATE[SKR01]:--} / SUPPF ${GATE[SUPPF]:--}, MAXC $(cat $Q/MAXC 2>/dev/null || echo 2), root $DR (SPLITS 24568cdb), lib $(md5sum < $Q/scripts/s2c_lib.sh | cut -c1-8), gpumem $(cat $Q/gpumem.pid), guard $(cat $Q/guard.pid), pid $$; dispatching"
LASTR=""
for j in "${JOBS[@]}"; do
  IFS='|' read -r name k arm opts <<< "$j"; w=${WT[$arm]}
  if [ -e $w/experiments/$name ]; then lg "skip $name (exists)"; continue; fi
  while :; do
    r=$(prestart) || { case "$r" in HOLD) ;; *) [ "$r" != "$LASTR" ] && lg "s2c: $r (before start of $name); new starts wait";; esac; LASTR=$r; sleep 60; continue; }
    [ -n "$LASTR" ] && [ "$LASTR" != HOLD ] && lg "s2c: start conditions clear again"; LASTR=""
    MAXC=$(cat $Q/MAXC 2>/dev/null || echo 2)
    [ "$(alive)" -ge "$MAXC" ] && { sleep 30; continue; }
    gate_try ${GATE[$arm]} "s2c $name" || { sleep 30; continue; }
    [ -e $Q/HOLD ] && { lg "s2c: HOLD seen after the gate pass for $name; not starting"; continue; }
    break
  done
  deploy_ok $w ${DEP[$arm]} || { lg "s2c deploy check FAIL at start of $name; HOLD set"; touch $Q/HOLD; continue; }
  lg "start $name (free $(SMI --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB; alive $(alive); MAXC $MAXC)"
  launch_run $name $w "$opts"; pp=$LPID
  if [ -n "$pp" ]; then lg "pid $name $pp (python; parent $(ps -o ppid= -p $pp | tr -d ' ')); cmdline recorded ($(md5sum < $Q/pids/$name.cmdline | cut -c1-8)): $(psl $pp)"
  else lg "s2c: no train.py cmdline for $name within 20 s (pid file $(cat $Q/pids/$name.pid 2>/dev/null)); HOLD set (the watcher cannot verify this run)"; touch $Q/HOLD; fi
  ok=1; cfgcheck $name $k $arm || ok=0
  if [ $ok = 1 ]; then m=$(startcheck $w/experiments/$name.stdout "$WANT" 240) || ok=0; lg "$name $m"; fi
  if [ $ok = 0 ]; then lg "s2c: live check FAILED for $name: HOLD + stop by verified PID"; touch $Q/HOLD; stop_verified $name "$pp"; lg "s2c: stop of $name rc $?"; fi
done
lg "s2c queue: all jobs dispatched; waiting"
wait
NM=$(printf '%s\n' "${JOBS[@]}" | cut -d'|' -f1 | paste -sd'|')
lg "S2C ALL TRAINED ($(grep -cE "trained ($NM) rc=0\$" $L) rc 0 of ${#JOBS[@]}; pid $$, $(basename $J))"
