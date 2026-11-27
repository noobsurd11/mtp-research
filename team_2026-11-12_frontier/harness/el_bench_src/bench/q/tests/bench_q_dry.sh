#!/bin/bash
# elbench queue / guard dry tests on gaint (tranche 1). Scratch dir only ($D); dummy processes only (a fake workdir whose
# scripts/train.py writes a config, prints a line and sleeps); no GPU, no training. Run inside tmux bench_qdry.
# Part G = s2c_guard_dry.sh passes 1-5 on bench_guard.sh + bench_lib.sh (decoys must never be signalled).
# Part U = s2c_queue_unit.sh cases on bench_lib.sh (outside / prestart / startcheck).
# Part Q = the whole bench_q.sh on 6 dummy jobs (incl. a smoke_* job with --exit_after_step): gate wait (FAKEFREE), outside-process wait (FAKEAPPS), MAXC 1, config OK,
#          CONFIG FAIL -> HOLD + stop, startup-line MISMATCH -> HOLD + stop, external job OK, end line. Own gate dir (never the
#          shared /home/noob/work/gpu_gate), GAPSEC 10; logger and guard (FAKE, DRY) in their own tmux windows.
set -u
TAG=${TAG:?tag}; D=/home/noob/work/bq/dry_$TAG; REPO=/home/noob/work/el_bench; QS=$REPO/bench/q; P=/home/noob/work/el-fault-detection/.venv/bin/python
[ ! -e $D ] || { echo "$D exists"; exit 1; }
mkdir -p $D; H=$D/harness.log; lg(){ echo "$(date '+%F %T') $*" | tee -a $H; }
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1
W=$D/wt; mkdir -p $W/scripts $W/experiments $D/dummy
cat > $W/scripts/train.py <<'PY'
import os, shutil, signal, sys, time
name = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("run_name=")), None)
if name is None and "--bench-run" in sys.argv:
    name = sys.argv[sys.argv.index("--bench-run") + 1]
d = os.environ.get("DUMMY_DIR", "")
m = os.environ.get("DUMMY_MODE", "normal")
if os.path.exists(f"{d}/{name}.mode"):
    m = open(f"{d}/{name}.mode").read().strip()
if m == "ignterm":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if m == "execswap":
    signal.signal(signal.SIGTERM, lambda s, f: os.execv("/bin/sleep", ["sleep", "600"]))
if os.path.exists(f"{d}/{name}.cfg"):
    os.makedirs(f"experiments/{name}", exist_ok=True)
    shutil.copy(f"{d}/{name}.cfg", f"experiments/{name}/config_used.yaml")
if os.path.exists(f"{d}/{name}.line"):
    print(open(f"{d}/{name}.line").read().rstrip("\n"), flush=True)
if os.environ.get("DUMMY_LINE"):
    print(os.environ["DUMMY_LINE"], flush=True)
time.sleep(float(open(f"{d}/{name}.sleep").read()) if os.path.exists(f"{d}/{name}.sleep") else 600)
PY
export DUMMY_DIR=$D/dummy
lg "dry harness start pid $$ TAG $TAG; bench_q $(md5sum < $QS/bench_q.sh | cut -c1-8) lib $(md5sum < $QS/bench_lib.sh | cut -c1-8) guard $(md5sum < $QS/bench_guard.sh | cut -c1-8) gate $(md5sum < $QS/bench_gate.sh | cut -c1-8) gpumem $(md5sum < $QS/bench_gpumem.sh | cut -c1-8)"
alivecheck(){ local p; for p in "$@"; do [ -d /proc/$p ] && lg "  pid $p ALIVE: $(tr '\0' ' ' < /proc/$p/cmdline | cut -c1-90)" || lg "  pid $p gone"; done; }
rep(){ local v=$1 n=$2; for x in $(seq $n); do echo $v; done; }

# ======================= Part G: guard =======================
Q=$D/g; L=$Q/launch.log; mkdir -p $Q/pids; touch $L
printf '%s\n' "g_A|-|0|-|0|" "g_B|-|0|-|0|" "g_R|-|0|-|0|" "g_S|-|0|-|0|" "g_6206|-|0|-|0|" "g_root|-|0|-|0|" "g_dead|-|0|-|0|" "g_fin|-|0|-|0|" "g_C|-|0|-|0|" > $Q/jobs.txt
. $QS/bench_lib.sh
gl(){ lg "[G] $*"; }
grun(){ local n=$1 mode=$2; echo $mode > $DUMMY_DIR/$n.mode; launch_run $n $W "$P -u scripts/train.py --opts run_name=$n"
  gl "launched $n ($mode): pid file $(cat $Q/pids/$n.pid), LPID ${LPID:-none}, parent $(ps -o ppid= -p $LPID | tr -d ' '); ps: $(psl $LPID)"
  gl "  recorded cmdline = live: $([ "$(cat $Q/pids/$n.cmdline)" = "$(cmdl $LPID)" ] && echo yes || echo NO)"; }
grun g_A normal; A=$LPID; sleep 3
grun g_B ignterm; B=$LPID; sleep 3
grun g_R normal; R=$LPID; sed -i 's/run_name=g_R/run_name=g_R /' $Q/pids/g_R.cmdline
gl "decoy g_R pid $R: recorded cmdline altered (extra space), live cmdline unchanged"
sleep 2; sleep 600 & S=$!; echo $S > $Q/pids/g_S.pid; cp $Q/pids/g_A.cmdline $Q/pids/g_S.cmdline
echo 6206 > $Q/pids/g_6206.pid; echo 1 > $Q/pids/g_root.pid; echo 4194000 > $Q/pids/g_dead.pid
echo $S > $Q/pids/g_fin.pid; echo 0 > $Q/pids/g_fin.rc; echo $S > $Q/pids/stray.pid
gl "decoys: g_S -> sleep $S (newest; g_A's recorded cmdline), g_6206 -> 6206, g_root -> 1, g_dead -> 4194000, g_fin -> $S with .rc, stray -> $S"
gpass(){ local tag=$1; shift; : > $Q/autostop.log; rm -f $Q/HOLD $Q/pids/.dry_stopped; gl "pass $tag: $* ($(wc -l < $Q/fake_$tag.txt) samples)"
  env "$@" Q=$Q LIB=$QS/bench_lib.sh FAKE=$Q/fake_$tag.txt bash $QS/bench_guard.sh; gl "pass $tag guard rc=$?; HOLD file: $([ -e $Q/HOLD ] && echo present || echo absent)"
  cp $Q/autostop.log $Q/autostop_pass$tag.log; }
{ echo 12000; echo 1900; echo 1900; echo 2100; echo 1900; echo 2047; echo ERR; echo 1900; echo 1900; echo 1500; rep 12000 30
  rep 1900 3; rep 12000 30; rep 1900 3; rep 12000 30; echo 12000; echo 12000; } > $Q/fake_1.txt
gpass 1 DRY=1 COOL=30
gl "after pass 1 (DRY):"; alivecheck $A $B $R $S
{ echo 12000; rep 1900 3; rep 12000 5; rep 1900 3; rep 12000 5; rep 12000 20; rep 1900 3; rep 12000 5; echo 12000; } > $Q/fake_1b.txt
gpass 1b DRY=1 COOL=5
{ echo 12000; echo 1900; echo 1900; echo 2100; rep 1900 3; rep 12000 60; rep 1900 3; rep 12000 36; rep 1900 3; rep 12000 32; } > $Q/fake_2.txt
gpass 2 COOL=30
gl "after pass 2 (LIVE): A $A and B $B must be gone; decoys alive:"; alivecheck $A $B $R $S
grun g_C execswap; C=$LPID; sleep 2
{ echo 12000; rep 1900 3; rep 12000 34; echo 12000; } > $Q/fake_3.txt
gpass 3 COOL=3
gl "after pass 3 (LIVE): C $C must be alive as 'sleep 600' (no SIGKILL):"; alivecheck $C $R $S
{ echo 12000; rep 1900 3; rep 12000 4; } > $Q/fake_4.txt
gpass 4 DRY=1 COOL=3
{ echo 12000; rep ERR 12; echo 12000; } > $Q/fake_5.txt
gpass 5 DRY=1
gl "cleanup: stop own dummies / decoys by recorded PID (cmdline printed first)"
for p in $C $R $S; do [ -d /proc/$p ] && { gl "  stop $p: $(psl $p)"; kill -TERM $p; }; done; sleep 2
gl "left alive check:"; alivecheck $A $B $C $R $S
gl "launch.log: $(grep -E 'trained|done' $L | tr '\n' '|')"

# ======================= Part U: unit =======================
Q=$D/u; L=$Q/launch.log; mkdir -p $Q/pids; touch $L; ul(){ lg "[U] $*"; }
sleep 600 & G1=$!; echo $G1 > $Q/gpumem.pid; sleep 600 & G2=$!; echo $G2 > $Q/guard.pid; echo 777001 > $Q/pids/u_x.pid
ul "fake gpumem.pid $G1, guard.pid $G2 (sleep dummies); our recorded pid 777001"
for case in "6206,5876|777001,7020" "6206,5876|777001,7020|99999,1500" "6206,5876|99998,900" "99997,1024" "99996,1025" "6206,9000"; do
  echo "$case" | tr '|' '\n' > $Q/apps.txt; ul "outside() on [$case]: '$(FAKEAPPS=$Q/apps.txt outside)'"; done
echo "99996,1025" > $Q/apps.txt; ul "outside() OUTSIDE_MIB=0 on [99996,1025]: '$(OUTSIDE_MIB=0 FAKEAPPS=$Q/apps.txt outside)'"
echo "6206,5876" > $Q/apps.txt; r=$(FAKEAPPS=$Q/apps.txt prestart); ul "prestart all ok: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
printf '6206,5876\n99999,1500\n' > $Q/apps.txt; r=$(FAKEAPPS=$Q/apps.txt prestart); ul "prestart outside 1500 MiB: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
echo "6206,5876" > $Q/apps.txt; echo 4194001 > $Q/gpumem.pid; r=$(FAKEAPPS=$Q/apps.txt prestart); ul "prestart gpumem.pid dead: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"
r=$(FAKEAPPS=$Q/apps.txt prestart); ul "prestart with HOLD present: rc $? '$r'"; rm -f $Q/HOLD; echo $G1 > $Q/gpumem.pid
echo 4194002 > $Q/guard.pid; r=$(FAKEAPPS=$Q/apps.txt prestart); ul "prestart guard.pid dead: rc $? '$r'; HOLD $([ -e $Q/HOLD ] && echo present || echo absent)"; rm -f $Q/HOLD; echo $G2 > $Q/guard.pid
R0=/home/noob/work/b6/b6_root_0; WANT="Labelled: 425 ($R0/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107"
printf '2026-11-12 20:00:00 INFO train — %s\nstep 50/20000\n' "$WANT" > $Q/so_ok.txt; printf '2026-11-12 20:00:00 INFO train — %s\n' "${WANT/test: 107/test: 50}" > $Q/so_real.txt; : > $Q/so_none.txt
for f in so_ok so_real so_none; do r=$(startcheck $Q/$f.txt "$WANT" 4); ul "startcheck $f: rc $? $r"; done
printf 'x BENCH_START: run=e1\n' > $Q/so_ext.txt; r=$(startcheck $Q/so_ext.txt "BENCH_START: run=e1" 4); ul "startcheck external line: rc $? $r"
kill -TERM $G1 $G2; sleep 1; alivecheck $G1 $G2

# ======================= Part Q: the whole queue on dummy jobs =======================
Q=$D/q; L=$Q/launch.log; mkdir -p $Q/pids $Q/gg; touch $L; ql(){ lg "[Q] $*"; }
R0=/home/noob/work/b6/b6_root_0; R1=/home/noob/work/b6/b6_root_1
C0=bench/methods/house_r34_unetpp.yaml; C1=bench/methods/house_r34_unetpp_pf.yaml
cat > $Q/jobs.txt <<JOBS
dq_ok1|$C0|1|$R0|9000|
dq_ok2|$C1|2|$R1|9000|
dq_badcfg|$C0|3|$R0|9000|
dq_badline|$C0|4|$R0|9000|
dq_ext|-|0|$R0|4000|$P -u scripts/train.py --bench-run dq_ext
smoke_dq|$C0|5|$R0|9000||--exit_after_step 1000
JOBS
want(){ echo "Labelled: $(grep -c . $1/splits/train.txt) ($1/splits/train.txt)  unlabelled: 0 (-)  val: $(grep -c . $1/splits/val.txt)  test: $(grep -c . $1/splits/test.txt)"; }
render(){ (cd $REPO && $P -m bench.cards render $1 --seed $2 --run-name $3 --data-root $4); }
render $C0 1 dq_ok1 $R0 > $DUMMY_DIR/dq_ok1.cfg; echo "2026-11-12 x INFO train — $(want $R0)" > $DUMMY_DIR/dq_ok1.line; echo 25 > $DUMMY_DIR/dq_ok1.sleep
render $C1 2 dq_ok2 $R1 > $DUMMY_DIR/dq_ok2.cfg; echo "2026-11-12 x INFO train — $(want $R1)" > $DUMMY_DIR/dq_ok2.line; echo 8 > $DUMMY_DIR/dq_ok2.sleep
render $C0 3 dq_badcfg $R0 | sed 's/^  lr: 0.001$/  lr: 0.002/' > $DUMMY_DIR/dq_badcfg.cfg; echo "2026-11-12 x INFO train — $(want $R0)" > $DUMMY_DIR/dq_badcfg.line
render $C0 4 dq_badline $R0 > $DUMMY_DIR/dq_badline.cfg; echo "2026-11-12 x INFO train — $(want $R0 | sed 's/test: 107/test: 50/')" > $DUMMY_DIR/dq_badline.line
echo "x BENCH_START: run=dq_ext" > $DUMMY_DIR/dq_ext.line; echo 5 > $DUMMY_DIR/dq_ext.sleep
render $C0 5 smoke_dq $R0 > $DUMMY_DIR/smoke_dq.cfg; echo "2026-11-12 x INFO train — $(want $R0)" > $DUMMY_DIR/smoke_dq.line; echo 4 > $DUMMY_DIR/smoke_dq.sleep
ql "badcfg config differs from the card in: $(diff <(render $C0 3 dq_badcfg $R0) $DUMMY_DIR/dq_badcfg.cfg | grep -c '^[<>]') lines"
echo 1 > $Q/MAXC; echo 3000 > $Q/free.txt; echo "6206,5876" > $Q/apps.txt
export GG=$Q/gg GAPSEC=10 FAKEFREE=$Q/free.txt FAKEAPPS=$Q/apps.txt POLL=5 LIVE_WAIT=30 OUTSIDE_MIB=1024
rep 20000 2000 > $Q/guard_fake.txt
tmux new-window -t "=bench_qdry:" -n gm "Q=$Q FAKE=1 bash $QS/bench_gpumem.sh"
tmux new-window -t "=bench_qdry:" -n guard "Q=$Q LIB=$QS/bench_lib.sh FAKE=$Q/guard_fake.txt DRY=1 bash $QS/bench_guard.sh"
sleep 3; ql "gpumem pid $(cat $Q/gpumem.pid 2>/dev/null), guard pid $(cat $Q/guard.pid 2>/dev/null)"
JM=$(md5sum < $Q/jobs.txt | cut -c1-32)
( Q=$Q JOBS_MD5=$JM DEPLOY=skip REPO=$REPO W=$W P=$P bash $QS/bench_q.sh; echo "$(date '+%F %T') bench_q exit rc=$?" >> $H ) &
QP=$!; ql "queue started (subshell $QP); free 3000 < gate 9000 for 20 s"
sleep 20; echo 20000 > $Q/free.txt; ql "free -> 20000"
for i in $(seq 60); do grep -q "start dq_ok1" $L && break; sleep 1; done
printf '6206,5876\n99999,5000\n' > $Q/apps.txt; ql "outside process 99999 5000 MiB present for 20 s"
sleep 20; echo "6206,5876" > $Q/apps.txt; ql "outside process gone"
for i in $(seq 240); do grep -q "stop of dq_badcfg rc" $L && break; sleep 1; done
sleep 3; ql "after dq_badcfg: HOLD $([ -e $Q/HOLD ] && echo present || echo absent); removing HOLD"; rm -f $Q/HOLD
for i in $(seq 240); do grep -q "stop of dq_badline rc" $L && break; sleep 1; done
sleep 3; ql "after dq_badline: HOLD $([ -e $Q/HOLD ] && echo present || echo absent); removing HOLD"; rm -f $Q/HOLD
for i in $(seq 300); do grep -q "BENCH Q ALL DONE" $L && break; sleep 1; done
sleep 2; ql "launch.log:"; sed 's/^/    /' $L | tee -a $H
for i in $(seq 90); do [ -e $Q/guard.pid ] || [ -e $Q/gpumem.pid ] || break; sleep 1; done
ql "guard / gpumem stopped by themselves after the end line: guard.pid $([ -e $Q/guard.pid ] && echo present || echo gone), gpumem.pid $([ -e $Q/gpumem.pid ] && echo present || echo gone)"
ql "shared gate untouched: /home/noob/work/gpu_gate/gate.log lines with 'bench ': $(grep -c 'bench ' /home/noob/work/gpu_gate/gate.log 2>/dev/null)"
lg "dry harness end"
