#!/bin/bash
# c3lane: sandbox tests of lane rule v2 (shared GPUs) in bench/q/cv02/cq.sh and of bench/q/cv02/cq_rescue.sh, on gaint.
# The queue scripts run for real to their end or to a timeout. Stubs stand in for everything outside them:
#   python (card calls, train.py, bench_infer.py, slim_ckpt.py: small text files, arguments logged), nvidia-smi (state
#   read from files per test: free MiB per GPU, compute apps), ps (owner of the FAKE compute pids only: 91xxxxx alice,
#   92xxxxx bob, 95xxxxx our own login, 99xxxxx no owner = "unknown"; every other call is the real ps), md5sum (real;
#   one test makes the deploy check of one old queue slow), `sleep` as gpumem logger. No GPU, no real python, nothing
#   outside the work dir. The only signals: the tool under test stops ITS verified chain PID; the test ends its own
#   `sleep` loggers by PID. The one edit to each script copy is the '. /tmp/noob_el/env.sh' line.
# Parts: A the reviewed chain test of c3swad on the new tree (strict rule unchanged: 34 of 34);
#        B sharing off (no SHARE files): queue 5437778 (cq 5222150b) against the new tree, same jobs: logs, RUN.md5, calls equal;
#        C shared training start and shared dump (lead's list of 17 Nov); D cq_rescue.sh.
# Usage: OLD=<tree at 89b9ea5> BASE=<tree at 5437778> NEW=<BASE + c3lane patch> nice -n 19 bash c3lane_test.sh <new work dir>
set -u
OLD=${OLD:?}; BASE=${BASE:?}; NEW=${NEW:?}; W=${1:?work dir (must not exist)}
[ -e "$W" ] && { echo "REFUSED: $W exists"; exit 1; }
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); CT=$HERE/../c3swad/c3swad_chain_test.sh
mkdir -p $W/bin || exit 1; W=$(cd $W && pwd); ENVL='. /tmp/noob_el/env.sh'; ME=$(id -un)
NP=0; NF=0
ck(){ if eval "$2"; then NP=$((NP+1)); echo "PASS $1"; else NF=$((NF+1)); echo "FAIL $1   [$2]"; fi; }
m5(){ md5sum < "$1" | cut -c1-32; }

cat > $W/bin/nvidia-smi <<'EOF'
#!/bin/bash
i=""; p=""; for x in "$@"; do [ "$p" = -i ] && i=$x; p=$x; done
case "$*" in *--query-gpu=uuid*) echo "GPU-stub-$i";; *--query-gpu=memory.free*) cat $NVD/free.$i 2>/dev/null || echo 48000;;
  *--query-gpu=name*) cat $NVD/name.$i 2>/dev/null || echo "FAKE A6000";; *--query-compute-apps=*) [ -f $NVD/apps ] && cat $NVD/apps; exit 0;; *) exit 1;; esac
EOF
cat > $W/bin/ps <<'EOF'
#!/bin/bash
p=${@: -1}
case "$*" in *"-o user="*) case "$p" in 91?????) echo " alice"; exit 0;; 92?????) echo " bob"; exit 0;; 95?????) echo " $(id -un)"; exit 0;; 99?????) exit 1;; esac;; esac
exec /usr/bin/ps "$@"
EOF
cat > $W/bin/md5sum <<'EOF'
#!/bin/bash
case "$*" in *CODE.md5*) [ -n "${SLOWMD5:-}" ] && [ -e "$SLOWMD5" ] && sleep 4;; esac
exec /usr/bin/md5sum "$@"
EOF
cat > $W/python <<'EOF'
#!/bin/bash
log(){ echo "$*" >> "$STUBLOG"; }
if [ "$1" = -m ]; then
  case "$3" in validate) exit 0;;
    opts) shift 4; s=""; n=""; r=""; while [ $# -gt 0 ]; do case "$1" in --seed) s=$2;; --run-name) n=$2;; --data-root) r=$2;; esac; shift 2; done
          echo "seed=$s run_name=$n data.root=$r"; exit 0;;
    cfgcheck) echo "config OK (= card)"; exit 0;; esac; exit 9
elif [ "$1" = -c ]; then
  case "$4" in memory.gate_mib) echo 9000;; config) echo configs/base.yaml;; name) echo stub_method;; weights_key) echo swad_bn;;
    readouts) echo "[{'name': 'raw', 'weights_key': 'model'}, {'name': 'swad', 'weights_key': 'swad'}, {'name': 'swad_bn', 'weights_key': 'swad_bn'}]";;
    *) exit 9;; esac; exit 0
elif [ "$2" = scripts/train.py ]; then
  n=""; r=""; for x in "$@"; do case "$x" in run_name=*) n=${x#run_name=};; data.root=*) r=${x#data.root=};; esac; done
  log "train cwd=$PWD gpu=$CUDA_VISIBLE_DEVICES $n"
  mkdir -p experiments/$n/checkpoints; echo "run_name: $n" > experiments/$n/config_used.yaml
  echo "Labelled: $(grep -c . $r/splits/train.txt) ($r/splits/train.txt)  unlabelled: 0 (-)  val: $(grep -c . $r/splits/val.txt)  test: $(grep -c . $r/splits/test.txt)"
  sleep 4; echo "latest of $n" > experiments/$n/checkpoints/latest.pth
  case "$n" in *swad*) echo '{"step": 20000}' > experiments/$n/enc_probe.jsonl;; esac
  echo "step 20000/20000"; exit 0
elif [ "$2" = scripts/bench_infer.py ]; then
  all="$*"; shift 2; wk=auto; lp=0
  while [ $# -gt 0 ]; do case "$1" in --set) set=$2;; --dumps) dumps=$2;; --method) meth=$2;; --run-id) rid=$2;; --weights-key) wk=$2;; --bench-run) br=$2;; --logp) lp=1;; esac; shift; done
  echo "BENCH_START: run=$br"; log "dump cwd=$PWD gpu=$CUDA_VISIBLE_DEVICES run-id=$rid key=$wk logp=$lp bench-run=$br"; log "dumpargs $all"
  d=$dumps/elbench1/$meth/$rid/$set; [ -e $d ] && { echo "refuse: $d exists"; exit 1; }
  mkdir -p $d; echo "cell 0 of $rid key $wk logp $lp" > $d/c0.npz; echo "cell 1 of $rid key $wk" > $d/c1.npz
  echo "{\"run_id\": \"$rid\", \"weights_key\": \"$wk\"}" > $d/manifest.json
  sleep 3; echo "dumped $rid $set: 2 cells, key $wk"; exit 0
else
  case "$1" in */cvcard.py) exit 0;;
    */slim_ckpt.py) log "slim cwd=$PWD $*"; r=$3; [ -e $r/checkpoints/slim.pth ] && exit 1
      echo "slim of $(cat $r/checkpoints/latest.pth) keys ${5:-all}" > $r/checkpoints/slim.pth; echo "slim $r keys ${5:-all}"; exit 0;; esac
  exit 9
fi
EOF
chmod +x $W/bin/* $W/python; export PATH=$W/bin:$PATH
[ "$(command -v nvidia-smi)" = $W/bin/nvidia-smi ] && [ "$(command -v ps)" = $W/bin/ps ] || { echo "stubs are not first in PATH"; exit 1; }
mroot(){ local r=$1; mkdir -p $r/splits; printf 'a\nb\nc\n' > $r/splits/train.txt; printf 'd\ne\n' > $r/splits/val.txt; cp $r/splits/val.txt $r/splits/test.txt
  (cd $r && /usr/bin/md5sum splits/train.txt splits/val.txt splits/test.txt > SPLITS.md5 && /usr/bin/md5sum splits/train.txt > DATA_MANIFEST.md5); }
mkdir -p $W/data/meta $W/data/roots $W/data_v3/roots; echo x > $W/data/meta/forbidden_v1.txt
(cd $W/data && /usr/bin/md5sum meta/forbidden_v1.txt > DEPLOY.md5)
mroot $W/data/roots/cv5v2_v11_f0; mroot $W/data/roots/cv5v2_v1_f1; mroot $W/data_v3/roots/cv5v3_v11_f2
(cd $W/data/roots && /usr/bin/md5sum cv5v2_v11_f0/SPLITS.md5 cv5v2_v1_f1/SPLITS.md5 > ROOTS_cv5v2_v11.md5 && /usr/bin/md5sum cv5v2_v1_f1/SPLITS.md5 > ROOTS_cv5v2_v1.md5)
(cd $W/data_v3/roots && /usr/bin/md5sum cv5v3_v11_f2/SPLITS.md5 > ROOTS_cv5v3_v11.md5)
DEP=0000000000000000000000000000000000000000
code(){ local t=$1 d=$2 f; mkdir -p $d/bench/q/cv02 $d/bench/methods_cv02; cp $t/bench/q/bench_lib.sh $d/bench/q/
  for f in cq.sh cq_setup.sh cq_gpumem.sh cvcard.py slim_ckpt.py cq_rescue.sh; do [ -e $t/bench/q/cv02/$f ] && cp $t/bench/q/cv02/$f $d/bench/q/cv02/; done
  sed -i "s#^$ENVL.*#:#" $d/bench/q/cv02/cq.sh
  echo $DEP > $d/REVISION; (cd $d && find bench -type f | sort | xargs /usr/bin/md5sum > CODE.md5); }
ROOT=$W/data_v3/roots/cv5v3_v11_f2; CARD=bench/methods/swad_const_pf_v11.yaml
jl(){ echo "$1|$CARD|5|$ROOT|2|${2:-9000}|5262|${3:-0}|${4:-}${5:+|$5}"; }      # name gate logp extra readouts
PIDS=""
prep(){ mkdir -p $W/q_$1 $W/nv_$1; }
apps(){ local t=$1; shift; printf '%s\n' "$@" > $W/nv_$t/apps; }                 # lines "GPU-stub-<g>, <pid>, <MiB>"
# q TAG B GPUS TMAX [ENV=VAL ...] < job lines : starts the queue in the background
q(){ local tag=$1 b=$2 gpus=$3 tmax=$4 qd=$W/q_$1 lp a cqs=$2/bench/q/cv02/cq.sh; shift 4; cat > $qd/jobs.txt; echo 1 > $qd/LPG; echo 8 > $qd/MAXC
  for a in "$@"; do case "$a" in QC=*) cqs=${a#QC=}/bench/q/cv02/cq.sh;; esac; done      # with QC the queue code of QC is run, as cq_setup.sh does
  sleep 1800 & lp=$!; PIDS="$PIDS $lp"; echo $lp > $qd/gpumem.pid
  ( unset QC; export B=$b Q=$qd JOBS_MD5=$(m5 $qd/jobs.txt) DEPLOY=$DEP DATA_MD5=$(m5 $W/data/DEPLOY.md5) DATA=$W/data DATA_V3=$W/data_v3 P=$W/python \
      GPUS="$gpus" GAPSEC=1 POLL=2 LIVE_WAIT=30 STUBLOG=$W/stub_$tag.log NVD=$W/nv_$tag "$@"
    timeout $tmax bash $cqs > $qd/stdout 2>&1; echo $? > $qd/rc ) & }
at(){ local s=$1; shift; ( sleep $s; eval "$*" ) & }
LG(){ echo $W/q_$1/launch.log; }
# end of the test (also on an early exit): end the test's own processes by PID: the `sleep` loggers and whatever queue
# main process or chain subshell of a sandbox queue is still alive (a chain that waits for a lane loops for ever)
cleanup(){ local f p; for f in $W/q_*/queue.pid $W/q_*/pids/subshells.txt; do [ -e $f ] || continue
    for p in $(awk '{print $NF}' $f); do case "$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)" in *"$W/"*) kill $p 2>/dev/null;; esac; done; done
  # the `sleep` loggers: q() runs at the right end of a pipe, so their PIDs are read from the queue dirs, not from $PIDS
  for f in $W/q_*/gpumem.pid; do [ -e $f ] || continue; p=$(tr -dc 0-9 < $f)
    [ -n "$p" ] && [ "$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null)" = "sleep 1800 " ] && kill $p 2>/dev/null; done
  kill $PIDS 2>/dev/null; }
trap cleanup EXIT
code $NEW $W/BN; code $NEW $W/BN2; code $BASE $W/BB; code $BASE $W/BB2; code $OLD $W/BO; code $OLD $W/BO3; code $BASE $W/QB
A0="GPU-stub-0, 9100001, 30000"; A1="GPU-stub-1, 9100002, 30000"; A2="GPU-stub-2, 9100003, 30000"
echo "[$(date '+%F %T')] start; cq old $(m5 $OLD/bench/q/cv02/cq.sh | cut -c1-8), base $(m5 $BASE/bench/q/cv02/cq.sh | cut -c1-8), new $(m5 $NEW/bench/q/cv02/cq.sh | cut -c1-8), rescue $(m5 $NEW/bench/q/cv02/cq_rescue.sh | cut -c1-8)"

# ---- part A (in the background): the reviewed chain test, old tree against the new tree
( OLD=$OLD NEW=$NEW bash $CT $W/chain > $W/chain.out 2>&1; echo $? > $W/chain.rc ) &
# ---- part B: sharing off, base against new
for t in eqb eqn; do prep $t; done
{ jl e_p_f2_s5 9000 1; jl e_swad_f2_s5 11000 0 "" swad; } | q eqb $W/BB "0 1" 110
{ jl e_p_f2_s5 9000 1; jl e_swad_f2_s5 11000 0 "" swad; } | q eqn $W/BN2 "0 1" 110
# ---- part C: shared training
st(){ echo ${2:-20480} > $W/q_$1/SHARE_TRAIN; }; sd(){ echo ${2:-10240} > $W/q_$1/SHARE_DUMP; }; fr(){ echo $3 > $W/nv_$1/free.$2; }
prep s1; st s1; apps s1 "$A0"; fr s1 0 20479; jl s1 | q s1 $W/BN "0" 50
prep s2; st s2; apps s2 "$A0"; fr s2 0 30000; jl s2 | q s2 $W/BN "0" 50; at 10 fr s2 0 20000
prep s3; st s3; apps s3 "$A0"; fr s3 0 30000; jl s3 | q s3 $W/BN "0" 60
prep s4; st s4; apps s4 "GPU-stub-0, 9500001, 6000"; fr s4 0 30000; jl s4 | q s4 $W/BN "0" 50
prep s5; st s5; apps s5 "GPU-stub-0, 9900001, 6000"; fr s5 0 30000; jl s5 | q s5 $W/BN "0" 50
prep s6; st s6; apps s6 "GPU-stub-0, 9100001, [N/A]"; fr s6 0 30000; jl s6 | q s6 $W/BN "0" 50
prep s7; st s7; apps s7 "$A0"; fr s7 0 30000; { jl s7a; jl s7b; } | q s7 $W/BN "0" 110
prep s8; st s8; apps s8 "$A0"; fr s8 0 25000; jl s8 30000 | q s8 $W/BN "0" 50
prep s9; st s9; apps s9 "$A0"; fr s9 0 40000; jl s9 | q s9 $W/BN "0 1" 50
prep s9b; st s9b; apps s9b "$A0" "GPU-stub-1, 9200001, 30000"; fr s9b 0 40000; fr s9b 1 1000; jl s9b | q s9b $W/BN "0 1" 60; at 12 "apps s9b '$A0'; fr s9b 1 48000"
prep s10; st s10; apps s10 "$A0" "$A1" "$A2"; fr s10 0 21000; fr s10 1 30000; fr s10 2 25000; jl s10 | q s10 $W/BN "0 1 2" 60
prep l1; st l1; apps l1 "$A0"; fr l1 0 30000; jl l1 | q l1 $W/BN "0" 55; at 12 "rm -f $W/q_l1/SHARE_TRAIN"
prep l2; st l2 20479; apps l2 "$A0"; fr l2 0 40000; jl l2 | q l2 $W/BN "0" 45
prep l3; apps l3 "$A0"; fr l3 0 40000; jl l3 | q l3 $W/BN "0" 45
prep l4; echo "20480 MiB" > $W/q_l4/SHARE_TRAIN; apps l4 "$A0"; fr l4 0 40000; jl l4 | q l4 $W/BN "0" 45
# ---- part C: shared dump
prep d1; sd d1; jl d1 | q d1 $W/BN "0" 110; at 8 "apps d1 '$A0'; fr d1 0 10239"; at 50 fr d1 0 10240
prep d2; sd d2; jl d2 | q d2 $W/BN "0" 110; at 8 "apps d2 'GPU-stub-0, 9900001, 6000'; fr d2 0 30000"; at 50 "rm -f $W/nv_d2/apps"
prep d3; sd d3 10239; jl d3 | q d3 $W/BN "0" 70; at 8 "apps d3 '$A0'; fr d3 0 30000"
prep f1; sd f1; apps f1 "$A0"; fr f1 0 12000; mkdir -p $W/BN/experiments/dumptest_f1/checkpoints; echo c > $W/BN/experiments/dumptest_f1/config_used.yaml; echo l > $W/BN/experiments/dumptest_f1/checkpoints/latest.pth
jl dumptest_f1 11000 0 --fixture | q f1 $W/BN "0" 80
# ---- part D: old queues with a waiting dump chain (old cq.sh of 89b9ea5; rqd: cq 5222150b with a swad line). The second job
# of a queue starts about 10 s after the first (start gap), so the other user appears at 16 s, while both runs train or
# have trained; the chains look for their dump lane about 30 s after the start.
for t in rqa rqb rqc; do prep $t; done; prep rqd
{ jl ra; jl rb; } | q rqa $W/BO "0 1" 400; at 16 "apps rqa '$A1'; fr rqa 1 15000"
{ jl rc; jl rd; } | q rqb $W/BO "0 1" 400; at 16 "apps rqb '$A1'; fr rqb 1 5000"
{ jl re; jl rf; } | q rqc $W/BO "0 1" 400 SLOWMD5=$W/slow_rqc; at 16 "apps rqc '$A0'; fr rqc 0 15000"
{ jl rg; jl rh_swad 11000 0 "" swad; } | q rqd $W/BB2 "0 1" 400; at 16 "apps rqd '$A1'; fr rqd 1 15000"
prep rqe; { jl ri; jl rj; } | q rqe $W/BO3 "0 1" 400 QC=$W/QB; at 16 "apps rqe '$A1'; fr rqe 1 15000"      # a queue like c3all2: B = 89b9ea5, queue code from another dir
sleep 62
RS(){ local oq=$1 rq=$2 tag=$3; shift 3; OQ=$W/q_$oq RQ=$rq GPUS="0 1" GAPSEC=1 POLL=2 LIVE_WAIT=30 RACE_WAIT=${RACE_WAIT:-6} NVD=$W/nv_$oq STUBLOG=$W/stub_$oq.log DATA=$W/data DATA_V3=$W/data_v3 bash $W/BN/bench/q/cv02/cq_rescue.sh "$@" > $W/rs_$tag.out 2>&1; }
echo "--- D rescue tool: refusals (the waiting chain of rb must stay untouched)"
RA=$W/q_rqa; LA=$RA/launch.log; mkdir -p $W/rq_a; echo 10240 > $W/rq_a/SHARE_DUMP
ck "D0 setting: ra finished with RUN.md5, the chain of rb waits for GPU 1 (strict rule of the old queue)" '[ -s $W/BO/runs/ra/RUN.md5 ] && grep -q "dump dump_rb waits: GPU 1 does not qualify" $LA && [ ! -e $RA/pids/rb.end ]'
cpb=$(grep "^rb chain " $RA/pids/subshells.txt | cut -d" " -f3); L0=$(m5 $LA)
ref(){ local tag=$1 want=$2; shift 2; RS rqa $W/rq_a $tag "$@"; local rc=$?; ck "D refusal $tag" "[ $rc = 1 ] && [ \"\$(grep -c . $W/rs_$tag.out)\" = 1 ] && grep -q \"^RESCUE REFUSED.*$want\" $W/rs_$tag.out"; }
ref name "not exactly one line" zz
mv $RA/pids/rb.rc $W/keep.rc; ref notrained "training rc is ''" rb; echo 1 > $RA/pids/rb.rc; ref rc1 "training rc is '1'" rb; mv $W/keep.rc $RA/pids/rb.rc
mv $W/BO/experiments/rb.stdout $W/keep.stdout; ref nofinal "no 'step 20000/20000' line" rb; mv $W/keep.stdout $W/BO/experiments/rb.stdout
touch $RA/pids/rb.end; ref ended "chain has ended" rb; rm -f $RA/pids/rb.end
mkdir $W/BO/runs/rb; ref runsdir "runs/rb exists" rb; rmdir $W/BO/runs/rb
touch $W/BO/experiments/rb/checkpoints/slim.pth; ref slim "slim.pth exists" rb; rm -f $W/BO/experiments/rb/checkpoints/slim.pth
mkdir -p $W/BO/dumps/elbench1/stub_method/rb; ref dumpdir "a dump folder of the run exists" rb; rmdir $W/BO/dumps/elbench1/stub_method/rb
touch $RA/HOLD; ref hold "HOLD is set" rb; rm -f $RA/HOLD
cp $RA/pids/subshells.txt $W/keep.sub; echo "rb chain $(cat $RA/gpumem.pid)" >> $RA/pids/subshells.txt; ref notchild "is not alive as a child of the queue's main process" rb
echo "rb chain 999999999" >> $RA/pids/subshells.txt; ref chaindead "is not alive as a child" rb; cp $W/keep.sub $RA/pids/subshells.txt
cp $RA/queue.pid $W/keep.qp; echo 999999999 > $RA/queue.pid; ref maindead "is not alive as a child" rb; cp $W/keep.qp $RA/queue.pid
mv $W/BO/runs/ra/RUN.md5 $W/keep.run; ref nosibling "does not reproduce the RUN.md5 of a finished sibling" rb; mv $W/keep.run $W/BO/runs/ra/RUN.md5
touch $W/BO/dumps/elbench1/stub_method/ra/cv5v3_f2/extra.npz; ref siblingdiff "does not reproduce the RUN.md5 of a finished sibling" rb; rm -f $W/BO/dumps/elbench1/stub_method/ra/cv5v3_f2/extra.npz
OQ=$RA RQ=$W/nodir bash $W/BN/bench/q/cv02/cq_rescue.sh rb > $W/rs_norq.out 2>&1; rc=$?; ck "D refusal no rescue dir" '[ $rc = 1 ] && grep -q "^RESCUE REFUSED: rescue dir" $W/rs_norq.out'
( flock 9; sleep 6 ) 9> $W/rq_a/rescue.lock & sleep 1; ref lock "another cq_rescue.sh holds" rb; wait $! 2>/dev/null
mkdir -p $W/rq_d; echo 10240 > $W/rq_d/SHARE_DUMP; RS rqd $W/rq_d swad rh_swad
ck "D refusal 10-field swad line (cq 5222150b queue): refused, its chain untouched" 'grep -q "^RESCUE REFUSED rh_swad: job has further readouts .swad." $W/rs_swad.out && kill -0 $(grep "^rh_swad chain " $W/q_rqd/pids/subshells.txt | cut -d" " -f3) && [ ! -e $W/q_rqd/HOLD ]'
ck "D after all refusals: chain of rb alive, no HOLD, no dump started, launch.log of the old queue unchanged" 'kill -0 $cpb && [ ! -e $RA/HOLD ] && [ ! -e $RA/pids/dump_rb.pid ] && [ "$(m5 $LA)" = "$L0" ] && [ ! -e $RA/pids/rb.rescued ]'
echo "--- D rescue of rb: own GPU, shared-dump rule"
RS rqa $W/rq_a doneb rb; rc=$?; SA=$W/stub_rqa.log
ck "D rb done, one line, shared on its own GPU 1" '[ $rc = 0 ] && [ "$(grep -c . $W/rs_doneb.out)" = 1 ] && grep -q "^RESCUE rb: done (dump on GPU 1, shared: beside alice:30000MiB(9100002) ; free 15000 MiB >= SHARE_DUMP 10240; RUN.md5 6 files" $W/rs_doneb.out'
ck "D rb: the old chain was stopped (verified pid), HOLD removed, markers written" '! kill -0 $cpb 2>/dev/null && [ ! -e $RA/HOLD ] && [ -s $RA/pids/rb.rescued ] && [ -e $RA/pids/rb.end ]'
ck "D rb: exactly one dump, command byte-equal to the old queue's rendered line, run in the old B on GPU 1" '[ "$(grep -c "^dump .*run-id=rb " $SA)" = 1 ] && grep -q "^dump cwd=$W/BO gpu=1 run-id=rb key=auto logp=0 bench-run=dump_rb\$" $SA && [ "$W/python $(grep "^dumpargs .*--run-id rb " $SA | cut -d" " -f2-)" = "$(grep "^dump_rb|" $RA/jobs_rendered.txt | cut -d"|" -f2-)" ]'
ck "D rb: slim by the old queue's own slim tool, without --keys" 'grep -qx "slim cwd=$W/BO $W/BO/bench/q/cv02/slim_ckpt.py --run experiments/rb" $SA'
ck "D rb: RUN.md5 = the sibling's form (paths with the name swapped), and it checks" '[ "$(sed "s/^[0-9a-f]\{32\}  //; s/rb/ra/g" $W/BO/runs/rb/RUN.md5)" = "$(sed "s/^[0-9a-f]\{32\}  //" $W/BO/runs/ra/RUN.md5)" ] && (cd $W/BO && /usr/bin/md5sum -c --quiet runs/rb/RUN.md5) && [ ! -e $W/BO/runs/rb/RUN.md5.tmp ]'
nrm(){ sed -E "s/^\[[^]]*\] //; s/GPU [0-9]/GPU G/g; s/free [0-9]+ MiB/free F MiB/; s/pid (dump_[a-z]+) [0-9]+/pid \1 N/; s/parent [0-9]+/parent N/; s/\([0-9a-f]{8}\)/(M)/; s/md5 [0-9a-f]{8}/md5 M/"; }
ck "D rb: the usual log lines of the dump, slim and RUN.md5 are those of the old chain (ra), names aside" '[ "$(grep -E "\] (start dump_rb|pid dump_rb|dump_rb startup|dumped dump_rb|RUN.md5 rb )" $LA | nrm | sed "s/rb/ra/g")" = "$(grep -E "\] (start dump_ra|pid dump_ra|dump_ra startup|dumped dump_ra|RUN.md5 ra )" $LA | nrm)" ]'
ck "D rb: marker lines in the old launch.log, in order" '[ "$(grep -oE "\] (RESCUE rb: the waiting dump chain|SHARED dump dump_rb on GPU 1: beside alice|RESCUE rb: dump_rb is started by cq_rescue.sh on GPU 1|start dump_rb on GPU 1|dumped dump_rb rc=0|RUN.md5 rb rc=0: 6 files|RESCUE rb: done)" $LA | tr "\n" ";")" = "] RESCUE rb: the waiting dump chain;] SHARED dump dump_rb on GPU 1: beside alice;] RESCUE rb: dump_rb is started by cq_rescue.sh on GPU 1;] start dump_rb on GPU 1;] dumped dump_rb rc=0;] RUN.md5 rb rc=0: 6 files;] RESCUE rb: done;" ]'
ck "D rb: pid, cmdline, rc and stdout files as the chain writes them" '[ -s $RA/pids/dump_rb.pid ] && [ -s $RA/pids/dump_rb.cmdline ] && [ "$(cat $RA/pids/dump_rb.rc)" = 0 ] && grep -q "^BENCH_START: run=dump_rb" $RA/dlogs/dump_rb.stdout && [ -s $RA/dlogs/slim_rb.log ]'
sleep 3
ck "D rb: the old queue's main process ended when its last chain was stopped: its end line comes BEFORE the rescued dump and counts 1 dump (note for rows2 in the tool header)" 'grep -q "BENCH CV02 Q ALL DONE (2 trained rc 0, 1 dumped rc 0, " $LA && [ "$(grep -n "BENCH CV02 Q ALL DONE" $LA | cut -d: -f1)" -lt "$(grep -n "\] start dump_rb on GPU" $LA | cut -d: -f1)" ]'
ck "D rb again: refused (the chain has ended)" 'RS rqa $W/rq_a again rb; [ $? = 1 ] && grep -q "^RESCUE REFUSED rb: the run.s chain has ended" $W/rs_again.out'
echo "--- D rescue of rd: HOLD in the rescue dir is honoured; own GPU does not qualify, another GPU of the same model is taken (strict)"
RB=$W/q_rqb; mkdir -p $W/rq_b; echo 10240 > $W/rq_b/SHARE_DUMP; touch $W/rq_b/HOLD; cpd=$(grep "^rd chain " $RB/pids/subshells.txt | cut -d" " -f3)
( RS rqb $W/rq_b doned rd; echo $? > $W/rs_doned.rc ) & sleep 22
ck "D rd with HOLD: chain stopped, no dump started, the tool waits" '! kill -0 $cpd 2>/dev/null && [ -s $RB/pids/rd.rescued ] && [ ! -e $RB/pids/dump_rd.pid ] && grep -q "dump of rd waits: HOLD" $W/rq_b/rescue.log && [ ! -e $RB/HOLD ]'
rm -f $W/rq_b/HOLD; wait $! 2>/dev/null
ck "D rd done on GPU 0 by the strict rule (own GPU 1: 5,000 MiB free, below the floor); no SHARED line" '[ "$(cat $W/rs_doned.rc)" = 0 ] && grep -q "^RESCUE rd: done (dump on GPU 0; RUN.md5 6 files" $W/rs_doned.out && grep -q "^dump cwd=$W/BO gpu=0 run-id=rd " $W/stub_rqb.log && ! grep -q "SHARED dump dump_rd" $RB/launch.log && grep -q "RESCUE rd: dump_rd is started by cq_rescue.sh on GPU 0 (the run trained on GPU 1)" $RB/launch.log && (cd $W/BO && /usr/bin/md5sum -c --quiet runs/rd/RUN.md5)'
echo "--- D rescue of rj: an old queue that ran with its queue code in QC (as c3all2: B 89b9ea5, QC 5437778)"
mkdir -p $W/rq_e; echo 10240 > $W/rq_e/SHARE_DUMP; RS rqe $W/rq_e donej rj; rc=$?
ck "D rj done; the slim tool is the old queue's own (from its QC dir, read from its armed line), the dump ran in B" '[ $rc = 0 ] && grep -q "^RESCUE rj: done (dump on GPU 1, shared" $W/rs_donej.out && grep -q "queue code QC $W/QB " $W/q_rqe/launch.log && grep -qx "slim cwd=$W/BO3 $W/QB/bench/q/cv02/slim_ckpt.py --run experiments/rj" $W/stub_rqe.log && grep -q "^dump cwd=$W/BO3 gpu=1 run-id=rj " $W/stub_rqe.log && [ "$(sed "s/^[0-9a-f]\{32\}  //; s/rj/ri/g" $W/BO3/runs/rj/RUN.md5)" = "$(sed "s/^[0-9a-f]\{32\}  //" $W/BO3/runs/ri/RUN.md5)" ]'
echo "--- D race: the old chain starts the dump itself while the tool holds it (slow deploy check of the old queue)"
RC=$W/q_rqc; mkdir -p $W/rq_c; echo 10240 > $W/rq_c/SHARE_DUMP; touch $W/slow_rqc; rm -f $W/nv_rqc/apps; echo 48000 > $W/nv_rqc/free.0
t=0; while ! grep -q "lane GPU 0: qualifies" <(tail -n 3 $RC/launch.log) && [ $t -lt 20 ]; do sleep 0.2; t=$((t+1)); done; sleep 0.5
RACE_WAIT=10 RS rqc $W/rq_c race re; rc=$?; rm -f $W/slow_rqc
ck "D race: the tool starts no dump and reports that the old chain ran it" '[ $rc = 0 ] && grep -q "^RESCUE re: nothing to do, the old chain ran the dump itself (RUN.md5 re rc=0: 6 files" $W/rs_race.out && [ "$(grep -c "^dump .*run-id=re " $W/stub_rqc.log)" = 1 ]'
ck "D race: the tool had set HOLD and removed it; no rescue marker, chain not signalled, run complete" 'grep -q "re: HOLD set in $RC" $W/rq_c/rescue.log && [ ! -e $RC/HOLD ] && [ ! -e $RC/pids/re.rescued ] && ! grep -q "RESCUE re" $RC/launch.log && [ -e $RC/pids/re.end ] && [ -s $W/BO/runs/re/RUN.md5 ]'
kill $(cat $W/q_rqd/queue.pid) $(awk '{print $3}' $W/q_rqd/pids/subshells.txt) 2>/dev/null     # rqd's swad chain waits for ever (refused by the tool)
wait $(jobs -p | grep -v -x -F "$(echo $PIDS | tr ' ' '\n')") 2>/dev/null

echo "--- A chain test of c3swad on the new tree (strict rule; sharing off)"
ck "A 34 of 34" '[ "$(cat $W/chain.rc)" = 0 ] && grep -q "CHAIN TEST: 34 checks, 34 passed, 0 failed" $W/chain.out'
echo "--- B sharing off: cq 5222150b against the new cq, same two jobs (one plain, one with the swad readout)"
EB=$(LG eqb); EN=$(LG eqn)
ck "B both queues ended: 2 trained, 2 dumped, 2 RUN.md5" 'grep -q "ALL DONE (2 trained rc 0, 2 dumped rc 0, 2 RUN.md5 of 2 jobs" $EB && grep -q "ALL DONE (2 trained rc 0, 2 dumped rc 0, 2 RUN.md5 of 2 jobs" $EN'
nq(){ sed -E "s/^\[[^]]*\] //; s#$W/BB#B#g; s#$W/BN2#B#g; s/pid ((dump_)?[a-z_0-9.]+) [0-9]+/pid \1 N/; s/parent [0-9]+/parent N/; s/\([0-9a-f]{8}\)/(M)/; s/:  *PID .*//"; }
for n in e_p_f2_s5 e_swad_f2_s5; do
  ck "B $n: log lines equal (time, pids, md5 of cmdline aside)" '[ "$(grep -E "(dump_)?$n( |:|\.|\$)" $EB | nq)" = "$(grep -E "(dump_)?$n( |:|\.|\$)" $EN | nq)" ] && [ "$(grep -cE "(dump_)?$n( |:|\.|\$)" $EN)" -ge 9 ]'
  ck "B $n: RUN.md5 byte-equal" 'cmp -s $W/BB/runs/$n/RUN.md5 $W/BN2/runs/$n/RUN.md5'; done
ck "B stub calls equal" '[ "$(sed "s#$W/BB#B#g" $W/stub_eqb.log | sort)" = "$(sed "s#$W/BN2#B#g" $W/stub_eqn.log | sort)" ]'
ck "B rendered commands equal" '[ "$(sed "s#$W/BB#B#g" $W/q_eqb/jobs_rendered.txt)" = "$(sed "s#$W/BN2#B#g" $W/q_eqn/jobs_rendered.txt)" ]'
ck "B no SHARED line, no shared candidate; the armed line of the new cq names sharing as off" '! grep -qi "shared" <(grep -v "cv02 q armed" $EN) && grep -q "cv02 q armed: 2 jobs .*; sharing (live files in $W/q_eqn; 0 = off): SHARE_TRAIN 0 MiB, SHARE_DUMP 0 MiB\$" $EN && ! grep -q sharing $EB'
echo "--- C shared training start (SHARE_TRAIN 20480 unless said; one job; another user holds 30,000 MiB on GPU 0)"
nost(){ ! grep -q "\] start $1 on GPU" $(LG $1); }
ck "C s1 free 20479 (below the floor): no start, no candidate" 'nost s1 && ! grep -q "shared candidate" $(LG s1)'
ck "C s2 at the floor at one look only (then 20000): candidate seen and lost, no start" 'nost s2 && grep -q "lane GPU 0: shared candidate, first look (free 30000 MiB >= SHARE_TRAIN 20480; beside alice:30000MiB(9100001) )" $(LG s2) && grep -q "lane GPU 0: shared candidate lost" $(LG s2)'
ck "C s3 at the floor at two looks 30 s apart: shared start, marked, usual start line unchanged after it" 'grep -qE "\] SHARED start s3 on GPU 0: beside alice:30000MiB\(9100001\) ; free 30000 MiB >= SHARE_TRAIN 20480 at two looks (3[0-9]|4[0-9]) s apart\$" $(LG s3) && [ "$(grep -n "\] start s3 on GPU 0 (card $CARD, seed 5, root $ROOT, gate 9000; free 30000 MiB; our lanes on GPU 1, all 1)" $(LG s3) | cut -d: -f1)" = $(( $(grep -n "SHARED start s3" $(LG s3) | cut -d: -f1) + 1 )) ]'
ck "C s3 the start came at least 30 s after the first look" '[ $(( $(date -d "$(grep "SHARED start s3" $(LG s3) | cut -c2-20)" +%s) - $(date -d "$(grep "shared candidate, first look" $(LG s3) | cut -c2-20)" +%s) )) -ge 30 ]'
ck "C s4 an owner above 4,096 MiB is our own login: no start, no candidate" 'nost s4 && ! grep -q "shared candidate" $(LG s4) && grep -q "lane GPU 0: another user > 4096 MiB: $ME:6000MiB" $(LG s4)'
ck "C s5 unknown owner: no start, no candidate" 'nost s5 && ! grep -q "shared candidate" $(LG s5) && grep -q "unknown:6000MiB" $(LG s5)'
ck "C s6 unreadable memory: no start, no candidate" 'nost s6 && ! grep -q "shared candidate" $(LG s6) && grep -q "+N/AMiB" $(LG s6)'
ck "C s7 LPG 1: the first job starts shared, the second does not start while the first holds the lane (its dump waits: SHARE_DUMP is off)" 'grep -q "SHARED start s7a on GPU 0" $(LG s7) && ! grep -q "\] start s7b on GPU" $(LG s7) && [ ! -e $W/q_s7/pids/s7a.end ] && grep -q "dump dump_s7a waits: GPU 0 does not qualify" $(LG s7) && [ "$(grep -c "^train " $W/stub_s7.log)" = 1 ]'
ck "C s8 job gate 30000 not met (free 25000 >= floor): no start, no candidate" 'nost s8 && ! grep -q "shared candidate" $(LG s8)'
ck "C s9 a strict lane exists (GPU 1) beside a shared one (GPU 0): strict taken at once, no SHARED line" 'grep -q "\] start s9 on GPU 1 " $(LG s9) && ! grep -q "SHARED" $(LG s9)'
ck "C s9b a strict lane appears between the two looks: it is taken, not the shared GPU" 'grep -q "shared candidate, first look" $(LG s9b) && grep -q "\] start s9b on GPU 1 " $(LG s9b) && ! grep -q "SHARED" $(LG s9b)'
ck "C s10 three shared candidates (21000, 30000, 25000 free): the one with most free memory" 'grep -q "SHARED start s10 on GPU 1: .*free 30000 MiB" $(LG s10) && [ "$(grep -c "shared candidate, first look" $(LG s10))" = 3 ]'
ck "C l1 SHARE_TRAIN removed between the two looks: no start" 'nost l1 && grep -q "shared candidate, first look" $(LG l1) && grep -q "shared candidate lost" $(LG l1)'
ck "C l2 SHARE_TRAIN 20479 (below the user's floor) = off" 'nost l2 && ! grep -q "shared candidate" $(LG l2) && grep -q "SHARE_TRAIN 0 MiB" $(LG l2)'
ck "C l3 no SHARE files, another user on the GPU: strict rule, no start" 'nost l3 && ! grep -q "shared candidate" $(LG l3)'
ck "C l4 SHARE_TRAIN not a plain number ('20480 MiB') = off" 'nost l4 && ! grep -q "shared candidate" $(LG l4)'
ck "C armed line prints the floors in use" 'grep -q "sharing (live files in $W/q_s3; 0 = off): SHARE_TRAIN 20480 MiB, SHARE_DUMP 0 MiB\$" $(LG s3) && grep -q "SHARE_TRAIN 0 MiB, SHARE_DUMP 10240 MiB\$" $(LG d1)'
echo "--- C shared dump (SHARE_DUMP 10240; the run started on a free GPU, then another user took 30,000 MiB)"
ck "C d1 free 10239: the dump waits; at 10240 it runs, marked, usual lines unchanged" '[ "$(grep -oE "\] (dump dump_d1 waits: GPU 0 does not qualify|SHARED dump dump_d1 on GPU 0: beside alice:30000MiB\(9100001\) ; free 10240 MiB >= SHARE_DUMP 10240|start dump_d1 on GPU 0 \(free 10240 MiB, dump gate 5262\)|dumped dump_d1 rc=0|RUN.md5 d1 rc=0: 6 files)" $(LG d1) | tr "\n" ";")" = "] dump dump_d1 waits: GPU 0 does not qualify;] SHARED dump dump_d1 on GPU 0: beside alice:30000MiB(9100001) ; free 10240 MiB >= SHARE_DUMP 10240;] start dump_d1 on GPU 0 (free 10240 MiB, dump gate 5262);] dumped dump_d1 rc=0;] RUN.md5 d1 rc=0: 6 files;" ]'
ck "C d1 the dump did not start before the free memory reached the floor (50 s)" '[ $(( $(date -d "$(grep "SHARED dump dump_d1" $(LG d1) | cut -c2-20)" +%s) - $(date -d "$(grep "cv02 q armed" $(LG d1) | cut -c2-20)" +%s) )) -ge 48 ]'
ck "C d2 unknown owner: the dump waits although 30,000 MiB are free; it runs by the strict rule when that owner is gone" 'grep -q "dump dump_d2 waits: GPU 0 does not qualify" $(LG d2) && ! grep -q "SHARED" $(LG d2) && grep -q "dumped dump_d2 rc=0" $(LG d2) && [ $(( $(date -d "$(grep "\] start dump_d2" $(LG d2) | cut -c2-20)" +%s) - $(date -d "$(grep "cv02 q armed" $(LG d2) | cut -c2-20)" +%s) )) -ge 48 ]'
ck "C d3 SHARE_DUMP 10239 (below the user's floor) = off: the dump waits" 'grep -q "dump dump_d3 waits: GPU 0 does not qualify" $(LG d3) && ! grep -q "start dump_d3" $(LG d3)'
ck "C f1 a --fixture job takes its lane by the dump rule (12,000 MiB free, SHARE_TRAIN off) and dumps shared" '[ "$(grep -oE "\] (SHARED lane \(fixture\) dumptest_f1 on GPU 0: beside alice:30000MiB\(9100001\) ; free 12000 MiB >= SHARE_DUMP 10240|fixture dumptest_f1 on GPU 0: training skipped|SHARED dump dump_dumptest_f1 on GPU 0|dumped dump_dumptest_f1 rc=0|RUN.md5 dumptest_f1 rc=0)" $(LG f1) | tr "\n" ";")" = "] SHARED lane (fixture) dumptest_f1 on GPU 0: beside alice:30000MiB(9100001) ; free 12000 MiB >= SHARE_DUMP 10240;] fixture dumptest_f1 on GPU 0: training skipped;] SHARED dump dump_dumptest_f1 on GPU 0;] dumped dump_dumptest_f1 rc=0;] RUN.md5 dumptest_f1 rc=0;" ]'
cleanup; trap - EXIT; wait 2>/dev/null
echo "[$(date '+%F %T')] C3LANE TEST: $((NP+NF)) checks, $NP passed, $NF failed"
[ $NF = 0 ]
