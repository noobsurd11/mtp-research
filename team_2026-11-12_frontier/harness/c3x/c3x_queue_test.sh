#!/bin/bash
# c3x: test of c3x_queue.sh in a FAKE cv02 tree on gaint (method of harness/c3swad/c3swad_fix1_test.sh: a copy of the script
# with the ssh calls replaced by a local `bash -c` and /tmp/noob_el by the fake root; a stub tmux first in PATH; fake queue
# processes are `sleep` children of this test, stopped by their recorded PIDs at the end). B89 = archive of 89b9ea5, XB =
# archive of the c3x commit (from a scratch clone), each with REVISION and CODE.md5 (as c3_deploy.sh). The real cq_setup.sh of
# XB runs; the stub tmux plays cq.sh's arming line into Q/launch.log. `render` runs DRY only here (the real render ran on gaint:
# evidence/render_gaint.log; render_cmp.out for `arm` is that run's compare output). df of /tmp is read from a file (FAKEDF).
# Usage: CLONE=<scratch clone at the c3x commit> bash c3x_queue_test.sh <new work dir>
set -u
W=${1:?work dir}; CLONE=${CLONE:?}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
[ -e $W ] && { echo "REFUSED: $W exists"; exit 1; }
mkdir -p $W/bin $W/s $W/io || exit 1; W=$(cd $W && pwd); F=$W/fake; BQ=$F/bench_q
X=$(git -C $CLONE rev-parse HEAD); XB=$F/bench_${X:0:7}; B89=$F/bench_89b9ea5
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
NP=0; NF=0
ck(){ if eval "$2"; then NP=$((NP+1)); echo "PASS $1"; else NF=$((NF+1)); echo "FAIL $1   [$2]"; fi; }
cat > $W/bin/tmux <<'EOF'
#!/bin/bash
A=$TMUXALIVE; touch $A
name(){ local p=""; for x in "$@"; do [ "$p" = -t ] || [ "$p" = -s ] && { x=${x#=}; echo "${x%:}"; return; }; p=$x; done; }
case "$1" in
  has-session) grep -qx "$(name "$@")" $A;;
  new-session) n=$(name "$@"); echo "$n" >> $A; echo "new-session $n: ${@: -1}" >> $TMUXLOG;;
  new-window) echo "new-window $(name "$@"): ${@: -1}" >> $TMUXLOG
    q=$(echo "${@: -1}" | grep -oE 'Q=[^ ]+' | head -1); q=${q#Q=}
    case "${FAKE_ARM:-}" in armed) echo "[t] cv02 q armed: 25 jobs (md5 x), sharing (live files in $q; 0 = off): SHARE_TRAIN 20480 MiB, SHARE_DUMP 10240 MiB" >> $q/launch.log;;
      refused) echo "[t] cv02 q: gpumem logger (cq_gpumem.sh) not running; not starting" >> $q/launch.log;; esac;;
  *) exit 0;;
esac
EOF
chmod +x $W/bin/tmux; export PATH=$W/bin:$PATH TMUXALIVE=$W/tmux_alive TMUXLOG=$W/tmux.log; : > $TMUXALIVE; : > $TMUXLOG
[ "$(command -v tmux)" = $W/bin/tmux ] || { echo "stub tmux is not first in PATH"; exit 1; }
# ---- fake cv02 tree
mkdir -p $B89 $XB $BQ $F/bench_data
git -C /home/noob/work/bench_wt_final archive 89b9ea5 | tar -x -C $B89 && git -C $CLONE archive $X | tar -x -C $XB || exit 1
echo 89b9ea5a12a37a87c16c4868cc4adf00794a7610 > $B89/REVISION; echo $X > $XB/REVISION
for d in $B89 $XB; do (cd $d && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5); done
cp ${DATA_DEPLOY:?copy of cv02 bench_data/DEPLOY.md5} $F/bench_data/DEPLOY.md5
echo 100 > $W/fakedf
PIDS=""
live(){ sleep 1800 & PIDS="$PIDS $!"; echo $! > $1/queue.pid; }
mkq(){ mkdir -p $BQ/$1/pids; echo "$2" > $BQ/$1/MAXC; echo 1 > $BQ/$1/LPG; : > $BQ/$1/launch.log; live $BQ/$1; }
mkq c3all 0; mkq c3all2 0; mkq c3base 0; mkq c3hrnet 0; mkq c3all3 8
sed "s#/tmp/noob_el/#$F/#g" ${C3R:?copy of c3all3 jobs_rendered.txt} > $BQ/c3all3/jobs_rendered.txt
for i in 1 2 3; do echo $i > $BQ/c3all3/pids/run$i.gpu; done; touch $BQ/c3all3/pids/run1.end      # 2 open c3all3 lanes
# ---- the script under test (copy) and its helpers
SED="s#ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#ssh -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#/tmp/noob_el#$F#g; s#/home/noob/work/bench_wt_c3s#$CLONE#g; s#df --output=avail -BG /tmp | tail -1#cat $W/fakedf#g"
sed "$SED" $HERE/c3x_queue.sh > $W/s/c3x_queue.sh; cp $HERE/c3x_make_jobs.py $HERE/c3x_rendercmp.py $HERE/diskguard4.sh $W/s/
grep -v 'ssh failed' $W/s/c3x_queue.sh | grep -q ssh && { echo "REFUSED: the copy still calls ssh"; exit 1; }
SC=$W/smoke_check.out; printf "RULE\tgate\tP = max(9700, 9750) = 9750 MiB; job gate = max(11000, P + 2,048) = 11798 MiB (lead's Q1 ruling); job list: GATE=11798\n# 0 FAIL\n" > $SC
HO(){ X=$X XB=$XB IO=$W/io SMOKE_CHECK=$SC GATE=${G-11798} bash $W/s/c3x_queue.sh "$@"; }
echo "--- T1 build"
ck "T1 build without GATE is refused (no default)" '! G= HO build > $W/t1x.out 2>&1 && grep -q "GATE must be given explicitly" $W/t1x.out && [ ! -e $W/io/jobs.txt ]'
ck "T1 GATE 11000 against the smoke RULE line 11798 is refused" '! G=11000 HO build > $W/t1y.out 2>&1 && grep -q "GATE 11000 differs from the job gate 11798 of the smoke check" $W/t1y.out && [ ! -e $W/io/jobs.txt ]'
ck "T1 without the smoke check file build is refused" '! X=$X XB=$XB IO=$W/io SMOKE_CHECK=$W/none GATE=11798 bash $W/s/c3x_queue.sh build > $W/t1z.out 2>&1 && grep -q "no smoke check output" $W/t1z.out && [ ! -e $W/io/jobs.txt ]'
HO build > $W/t1.out 2>&1; rc=$?
ck "T1 build with GATE = the RULE line (11798): 25 lines, that gate, md5 file" '[ $rc = 0 ] && [ "$(grep -c . $W/io/jobs.txt)" = 25 ] && [ "$(cut -d"|" -f6 $W/io/jobs.txt | sort -u)" = 11798 ] && [ -s $W/io/jobs.md5 ]'
ck "T1 a second build is refused" '! HO build > $W/t1b.out 2>&1 && grep -q "jobs.txt exists" $W/t1b.out'
mkdir -p $B89/experiments/c3x_hrnet_swad_v11_f3_s8
ck "T1 a name in use on cv02 is refused and no list is left" '! IO=$W/io2 X=$X XB=$XB SMOKE_CHECK=$SC GATE=11798 bash $W/s/c3x_queue.sh build > $W/t1c.out 2>&1 && grep -q "names already used on cv02: c3x_hrnet_swad_v11_f3_s8" $W/t1c.out && [ ! -e $W/io2/jobs.txt ]'
rmdir $B89/experiments/c3x_hrnet_swad_v11_f3_s8
printf "RULE\tgate\tP = max(9000, 8000) = 9000 MiB; job gate = max(11000, P + 2,048) = 11048 MiB (lead's Q1 ruling)\n# 0 FAIL\n" > $W/smoke_check2.out
ck "T1 another smoke result (RULE 11048) with GATE=11048 gives that job gate" 'GATE=11048 SMOKE_CHECK=$W/smoke_check2.out IO=$W/io3 X=$X XB=$XB bash $W/s/c3x_queue.sh build > $W/t1d.out 2>&1 && [ "$(cut -d"|" -f6 $W/io3/jobs.txt | sort -u)" = 11048 ]'
echo "--- T2 render (DRY) and the XB checks"
ck "T2 DRY render: XB checks pass, command printed" 'DRY=1 HO render > $W/t2.out 2>&1 && grep -q "differs from bench_89b9ea5 only in the 9 paths" $W/t2.out && grep -q "DRY, not run on cv02: .*B=$XB .*bash $XB/bench/q/cv02/cq.sh" $W/t2.out'
ck "T2 wrong XB name refused" '! XB=$F/bench_0000000 X=$X IO=$W/io bash $W/s/c3x_queue.sh render > $W/t2b.out 2>&1 && grep -q "XB must be" $W/t2b.out'
cp $XB/scripts/train.py $W/train.py.keep; echo "# x" >> $XB/scripts/train.py; (cd $XB && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
ck "T2 XB with a changed training file (CODE.md5 renewed) is refused" '! DRY=1 HO render > $W/t2c.out 2>&1 && grep -q "differs from bench_89b9ea5 in other paths than the 9 of the code proof: .*scripts/train.py" $W/t2c.out'
cp $W/train.py.keep $XB/scripts/train.py; echo x >> $XB/bench/q/cv02/cq.sh; (cd $XB && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
ck "T2 XB with another cq.sh is refused (pins)" '! DRY=1 HO render > $W/t2d.out 2>&1 && grep -q "do not match the pinned md5s" $W/t2d.out'
git -C $CLONE show $X:bench/q/cv02/cq.sh > $XB/bench/q/cv02/cq.sh; echo y >> $XB/bench/methods/house_r34_unetpp_pf_v11.yaml
ck "T2 XB with a file not in CODE.md5 changed is refused (CODE.md5)" '! DRY=1 HO render > $W/t2e.out 2>&1 && grep -q "XB CODE.md5 check failed" $W/t2e.out'
git -C $CLONE show $X:bench/methods/house_r34_unetpp_pf_v11.yaml > $XB/bench/methods/house_r34_unetpp_pf_v11.yaml; (cd $XB && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
ck "T2 restored XB passes again" 'DRY=1 HO render > $W/t2f.out 2>&1'
echo "--- T3 place, guard"
ck "T3 place: queue dir with jobs (read-only), LPG 1, MAXC 8, SHARE 20480 / 10240" 'HO place > $W/t3.out 2>&1 && [ "$(cat $BQ/c3x/LPG $BQ/c3x/MAXC $BQ/c3x/SHARE_TRAIN $BQ/c3x/SHARE_DUMP | tr "\n" " ")" = "1 8 20480 10240 " ] && [ ! -w $BQ/c3x/jobs.txt ] && cmp -s $BQ/c3x/jobs.txt $W/io/jobs.txt'
ck "T3 a second place is refused" '! HO place > $W/t3b.out 2>&1 && grep -q "exists on cv02" $W/t3b.out'
ck "T3 guard: script placed, session started" 'HO guard > $W/t3c.out 2>&1 && cmp -s $BQ/diskguard4.sh $HERE/diskguard4.sh && grep -qx bench_diskguard4 $TMUXALIVE'
ck "T3 a second guard is refused" '! HO guard > $W/t3d.out 2>&1 && grep -q "already runs" $W/t3d.out'
echo "--- T4 arm"
ck "T4 arm without a passed render is refused" '! HO arm > $W/t4a.out 2>&1 && grep -q "no passed .render." $W/t4a.out'
cp ${RCMP:?compare output of the gaint render} $W/io/render_cmp.out
ck "T4 c3all3 not dispatched all: refused, nothing started" '! FAKE_ARM=armed HO arm > $W/t4b.out 2>&1 && grep -q "c3all3 has not dispatched all its jobs" $W/t4b.out && ! grep -q "bench_q_c3x" $TMUXLOG'
echo "[t] cv02 q: all jobs dispatched; waiting" >> $BQ/c3all3/launch.log
echo 8 > $BQ/c3all2/MAXC
ck "T4 another live queue can start (c3all2 MAXC 8): refused" '! FAKE_ARM=armed HO arm > $W/t4c.out 2>&1 && grep -q "CAN_START c3all2" $W/t4c.out && grep -q "another queue can still start training" $W/t4c.out'
echo 0 > $BQ/c3all2/MAXC; touch $BQ/c3base/HOLD
ck "T4 a HOLD in a queue dir: refused" '! FAKE_ARM=armed HO arm > $W/t4d.out 2>&1 && grep -q "a HOLD file exists" $W/t4d.out'
rm $BQ/c3base/HOLD; echo 50 > $W/fakedf
ck "T4 free 50 GB < need (25 x 1.03 + 3.3 .swad + 8 x 0.27 + 2 open x 1.2 + 20 = 54): refused" '! FAKE_ARM=armed HO arm > $W/t4e.out 2>&1 && grep -q "about 54 GB; free 50 GB" $W/t4e.out && grep -q "50 GB < 54 GB needed" $W/t4e.out'
ck "T4 DRY with DISK_OK=1: pre-checks pass, command printed" 'DRY=1 DISK_OK=1 HO arm > $W/t4f.out 2>&1 && grep -q "DISK_OK=1: arming with 50 GB free" $W/t4f.out && grep -q "DRY, pre-checks passed; not run on cv02: B=$XB Q=$BQ/c3x SES=bench_q_c3x DEPLOY=$X" $W/t4f.out'
echo 100 > $W/fakedf
ck "T4 cq.sh refuses at arming (played): REFUSED" '! FAKE_ARM=refused ARMWAIT=10 HO arm > $W/t4g.out 2>&1 && grep -q "cq.sh did NOT arm" $W/t4g.out'
rm -f $BQ/c3x/queue.pid $BQ/c3x/gpumem.pid; : > $BQ/c3x/launch.log; sed -i '/bench_q_c3x/d' $TMUXALIVE
ck "T4 arm: real cq_setup.sh of XB, armed line seen, sharing shown" 'FAKE_ARM=armed HO arm > $W/t4h.out 2>&1 && grep -q "armed bench_q_c3x (.cv02 q armed:. line seen; sharing (live files in $BQ/c3x; 0 = off): SHARE_TRAIN 20480 MiB, SHARE_DUMP 10240 MiB" $W/t4h.out && grep -q "new-window bench_q_c3x: B=$XB Q=$BQ/c3x JOBS_MD5=$(cat $W/io/jobs.md5) DEPLOY=$X DATA_MD5=d6063fd83d20e656612540edda702cbe bash $XB/bench/q/cv02/cq.sh" $TMUXLOG'
ck "T4 a second arm is refused (session or queue dir used)" '! FAKE_ARM=armed HO arm > $W/t4i.out 2>&1 && grep -q "queue dir or data check" $W/t4i.out'
echo "--- T5 status"
ck "T5 status lists c3all3 and c3x" 'HO status > $W/t5.out 2>&1 && grep -q "^c3all3: MAXC 8 started 3 ended 1 of" $W/t5.out && grep -q "^c3x: MAXC 8" $W/t5.out'
for p in $PIDS; do kill $p 2>/dev/null; done; wait 2>/dev/null
echo "c3x queue test: $NP PASS, $NF FAIL"
