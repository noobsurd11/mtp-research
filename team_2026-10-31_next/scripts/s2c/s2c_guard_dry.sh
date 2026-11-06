#!/bin/bash
# runner v2 (3 Nov 2026): dry / live-signal tests of s2c_guard.sh v2 + s2c_lib.sh on gaint (judge b0d866a4 G7; coach v1 §2b).
# Scratch Q only ($D/g2$TAG; TAG env, default empty, for a re-run in fresh dirs); dummy processes only (a fake worktree whose scripts/train.py sleeps; no GPU, no training). Dummies are
# started with the lib's own launch_run (the queue's launch path): pids/<name>.pid = python, pids/<name>.cmdline recorded after exec.
# DUMMY_MODE (env, not in the cmdline): normal (exits on SIGTERM), ignterm (ignores SIGTERM), execswap (on SIGTERM exec's into
# 'sleep 600': same PID, other cmdline). FAKE = free values from a file; DRY=1 = no signal.
# Targets: A = s2c_SKR01_100pct_s10 (normal), B = s2c_SUPPF_100pct_s10 (ignterm, newer than A).
# Decoys (must never be signalled): s2c_SUPPF_100pct_s11 = a dummy trainer whose recorded cmdline was replaced (PID-reuse case; the
#   newest trainer-shaped process); s2c_SKR01_100pct_s11 = a plain sleep (started last) with a fake recorded cmdline; s2c_SKR01_100pct_s12
#   = 6206; s2c_SUPPF_100pct_s12 = PID 1 (root); s2c_SKR01_100pct_s13 = a dead PID; s2c_SUPPF_100pct_s13 = finished (.rc file);
#   stray.pid = not a job name.
# pass 1  FAKE+DRY, COOL 30: 2 lows no trigger; ERR resets; trigger 1 -> B; trigger 2 (fresh, >= 30 s) -> A; trigger 3 -> cap.
# pass 1b FAKE+DRY, COOL 5: trigger 2 at < 30 s after stop 1 -> no signal; a later fresh trigger -> A.
# pass 2  FAKE + LIVE signals, COOL 30: trigger 1 -> B: SIGTERM ignored, 30 s, owner + cmdline re-check, SIGKILL; trigger 2 (>= 30 s
#         later) -> A: exits on SIGTERM; trigger 3 -> cap; decoys alive after.
# pass 3  FAKE + LIVE: C = s2c_SKR01_100pct_s14 (execswap): SIGTERM -> its cmdline changes -> re-check fails -> no SIGKILL; HOLD.
# pass 4  FAKE+DRY: no verified live run -> no signal.   pass 5  FAKE+DRY: 12 failed reads -> HOLD at the 10th.
set -u
D=/home/noob/work/runner_s2c_dry; T=${TAG:-}; Q=$D/g2$T; W=$D/wt2$T; L=$Q/launch.log; P=/usr/bin/python3; J=${J:?jobs file}; LIB=$D/scripts/s2c_lib.sh
H=$Q/harness.log; lg(){ echo "$(date '+%F %T') $*" | tee -a $H; }
[ ! -e $Q ] && [ ! -e $W ] || { echo "$Q or $W exists"; exit 1; }
mkdir -p $Q/pids $W/scripts $W/experiments; cp $J $Q/s2c_jobs.txt; touch $L; . $LIB
cat > $W/scripts/train.py <<'PY'
import os, signal, time
m = os.environ.get("DUMMY_MODE", "normal")
if m == "ignterm":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if m == "execswap":
    signal.signal(signal.SIGTERM, lambda s, f: os.execv("/bin/sleep", ["sleep", "600"]))
if os.environ.get("DUMMY_LINE"):
    print(os.environ["DUMMY_LINE"], flush=True)
time.sleep(600)
PY
lg "harness start pid $$; jobs $(md5sum < $Q/s2c_jobs.txt | cut -c1-8); guard $(md5sum < $D/scripts/s2c_guard.sh | cut -c1-8); lib $(md5sum < $LIB | cut -c1-8)"
opt(){ grep "^$1|" $Q/s2c_jobs.txt | cut -d'|' -f4; }
run(){ local n=$1 mode=$2; export DUMMY_MODE=$mode; launch_run $n $W "$(opt $n)"; unset DUMMY_MODE
  lg "launched $n ($mode): pid file $(cat $Q/pids/$n.pid), LPID ${LPID:-none}, parent $(ps -o ppid= -p $LPID | tr -d ' ') ($(ps -o args= -p $(ps -o ppid= -p $LPID) | cut -c1-60)); ps: $(psl $LPID)"
  lg "  recorded cmdline ($(md5sum < $Q/pids/$n.cmdline | cut -c1-8)) = live: $([ "$(cat $Q/pids/$n.cmdline)" = "$(cmdl $LPID)" ] && echo yes || echo NO)"; }
run s2c_SKR01_100pct_s10 normal; A=$LPID; sleep 3
run s2c_SUPPF_100pct_s10 ignterm; B=$LPID; sleep 3
run s2c_SUPPF_100pct_s11 normal; R=$LPID; sed 's/seed=11/seed=99/' $Q/pids/s2c_SUPPF_100pct_s11.cmdline > $Q/x && mv $Q/x $Q/pids/s2c_SUPPF_100pct_s11.cmdline
lg "decoy s2c_SUPPF_100pct_s11 pid $R: recorded cmdline replaced (seed=11 -> seed=99), live cmdline unchanged"
sleep 2; sleep 600 & S=$!; echo $S > $Q/pids/s2c_SKR01_100pct_s11.pid; cp $Q/pids/s2c_SUPPF_100pct_s11.cmdline $Q/pids/s2c_SKR01_100pct_s11.cmdline
echo 6206 > $Q/pids/s2c_SKR01_100pct_s12.pid; echo 1 > $Q/pids/s2c_SUPPF_100pct_s12.pid; echo 4194000 > $Q/pids/s2c_SKR01_100pct_s13.pid
echo $S > $Q/pids/s2c_SUPPF_100pct_s13.pid; echo 0 > $Q/pids/s2c_SUPPF_100pct_s13.rc; echo $S > $Q/pids/stray.pid
lg "decoys: SKR01_s11 -> sleep $S (newest; fake recorded cmdline), SKR01_s12 -> 6206, SUPPF_s12 -> 1, SKR01_s13 -> 4194000 (dead), SUPPF_s13 -> $S with .rc (finished), stray -> $S"
rep(){ local v=$1 n=$2; for x in $(seq $n); do echo $v; done; }
gpass(){ local tag=$1; shift; : > $Q/autostop.log; rm -f $Q/HOLD $Q/pids/.dry_stopped; lg "pass $tag: $* ($(wc -l < $Q/fake_$tag.txt) samples)"
  env "$@" Q=$Q LIB=$LIB FAKE=$Q/fake_$tag.txt bash $D/scripts/s2c_guard.sh; lg "pass $tag guard rc=$?; HOLD file: $([ -e $Q/HOLD ] && echo present || echo absent)"
  cp $Q/autostop.log $Q/autostop_pass$tag.log; }
alivecheck(){ local p; for p in "$@"; do [ -d /proc/$p ] && lg "  pid $p ALIVE: $(cmdl $p | cut -c1-80)" || lg "  pid $p gone"; done; }
{ echo 12000; echo 1900; echo 1900; echo 2100; echo 1900; echo 2047; echo ERR; echo 1900; echo 1900; echo 1500; rep 12000 30
  rep 1900 3; rep 12000 30; rep 1900 3; rep 12000 30; echo 12000; echo 12000; } > $Q/fake_1.txt
gpass 1 DRY=1 COOL=30
lg "after pass 1 (DRY):"; alivecheck $A $B $R $S
{ echo 12000; rep 1900 3; rep 12000 5; rep 1900 3; rep 12000 5; rep 12000 20; rep 1900 3; rep 12000 5; echo 12000; } > $Q/fake_1b.txt
gpass 1b DRY=1 COOL=5
{ echo 12000; echo 1900; echo 1900; echo 2100; rep 1900 3; rep 12000 60; rep 1900 3; rep 12000 36; rep 1900 3; rep 12000 32; } > $Q/fake_2.txt
gpass 2 COOL=30
lg "after pass 2 (LIVE): A $A and B $B must be gone; decoys alive:"; alivecheck $A $B $R $S; sleep 2; lg "  launch.log: $(tr '\n' '|' < $L)"
run s2c_SKR01_100pct_s14 execswap; C=$LPID; sleep 2
{ echo 12000; rep 1900 3; rep 12000 34; echo 12000; } > $Q/fake_3.txt
gpass 3 COOL=3
lg "after pass 3 (LIVE): C $C must be alive as 'sleep 600' (no SIGKILL):"; alivecheck $C $R $S
{ echo 12000; rep 1900 3; rep 12000 4; } > $Q/fake_4.txt
lg "pass 4 setup: C $C now runs 'sleep 600' (cmdline differs from its record) -> must be REFUSED"
gpass 4 DRY=1 COOL=3
{ echo 12000; rep ERR 12; echo 12000; } > $Q/fake_5.txt
gpass 5 DRY=1
lg "cleanup: harness stops its own dummies / decoys by recorded PID (cmdline printed first)"
for p in $C $R $S; do [ -d /proc/$p ] && { lg "  stop $p: $(psl $p)"; kill -TERM $p; }; done; wait 2>/dev/null; sleep 1
lg "left alive check:"; alivecheck $A $B $C $R $S; lg "launch.log: $(tr '\n' '|' < $L)"; lg "harness end"
