#!/bin/bash
# c3swad fix round 1 (review REVIEW_C3SWAD.md 5c8354e1): tests of the cv02-facing steps in a FAKE cv02 tree on gaint.
# Nothing reaches cv02: each script under test is COPIED into the work dir with mechanical edits (sed) only:
#   every ssh call -> `bash -c` (the "remote" command runs locally); the prefix /tmp/noob_el -> the fake root; the data
#   md5 pin -> the md5 of the fake data file; for run_read: relay and read folders -> the work dir, the read tool -> a stub.
# The test refuses to run a copy that still holds the word "ssh" (the message text "ssh failed" aside). A stub tmux (session list in a file) is first in PATH.
# Live "queue processes" are `sleep` children of this test; they are ended by PID at the end. CPU only, no GPU.
# Covers: F1 (queue test in freeze and arm, fixture-only queues, dumptest stop), F2 and the missing-MAXC case (check.sh),
#   F4 (armed line), F10 (freeze by rename), F11 (dumptest clean), F7 (read script refuses before the folder exists),
#   F5 (relay guard), F12 (MAXC window copy for c3all2), and the steps build, place, guard, arm that were only dry-run.
# Usage: nice -n 19 bash c3swad_fix1_test.sh <new work dir>      (about 5 minutes)
set -u
W=${1:?work dir (must not exist)}; [ -e "$W" ] && { echo "REFUSED: $W exists"; exit 1; }
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); T=/home/yugma/mtp/research/team_2026-11-12_frontier
mkdir -p $W/bin $W/s $W/io || exit 1; W=$(cd $W && pwd); F=$W/fake; BQ=$F/bench_q; B=$F/bench_89b9ea5; QC=$F/bench_1111111
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
NP=0; NF=0
ck(){ if eval "$2"; then NP=$((NP+1)); echo "PASS $1"; else NF=$((NF+1)); echo "FAIL $1   [$2]"; fi; }
m5(){ md5sum < "$1" | cut -c1-32; }

# ---- stub tmux: sessions alive = lines of $TMUXALIVE; new-window can play cq.sh's arming result into Q/launch.log
cat > $W/bin/tmux <<'EOF'
#!/bin/bash
A=$TMUXALIVE; touch $A
name(){ local p=""; for x in "$@"; do [ "$p" = -t ] || [ "$p" = -s ] && { x=${x#=}; echo "${x%:}"; return; }; p=$x; done; }
case "$1" in
  has-session) grep -qx "$(name "$@")" $A;;
  new-session) n=$(name "$@"); echo "$n" >> $A; echo "new-session $n: ${@: -1}" >> $TMUXLOG;;
  new-window) echo "new-window $(name "$@"): ${@: -1}" >> $TMUXLOG
    q=$(echo "${@: -1}" | grep -oE 'Q=[^ ]+' | head -1); q=${q#Q=}
    case "${FAKE_ARM:-}" in armed) echo "[t] cv02 q armed: 62 jobs (md5 x), rendered y" >> $q/launch.log;; refused) echo "[t] cv02 q: gpumem logger (cq_gpumem.sh) not running; not starting" >> $q/launch.log;; esac;;
  kill-session) n=$(name "$@"); grep -qx "$n" $A || exit 1; grep -vx "$n" $A > $A.tmp; mv $A.tmp $A; echo "kill-session $n" >> $TMUXLOG;;
  *) exit 0;;
esac
EOF
chmod +x $W/bin/tmux; export PATH=$W/bin:$PATH TMUXALIVE=$W/tmux_alive TMUXLOG=$W/tmux.log; : > $TMUXALIVE; : > $TMUXLOG
[ "$(command -v tmux)" = $W/bin/tmux ] || { echo "stub tmux is not first in PATH"; exit 1; }

# ---- fake cv02 tree: B = archive of 89b9ea5, QC = the same + the patch, each with REVISION and CODE.md5 (as c3_deploy.sh)
mkdir -p $B $QC $BQ $F/bench_data
git -C /home/noob/work/el_bench archive 89b9ea5 | tar -x -C $B && git -C /home/noob/work/el_bench archive 89b9ea5 | tar -x -C $QC || exit 1
(cd $QC && git apply $HERE/cq_c3swad.patch) || { echo "patch does not apply"; exit 1; }
echo 89b9ea5a12a37a87c16c4868cc4adf00794a7610 > $B/REVISION; echo 1111111111111111111111111111111111111111 > $QC/REVISION
for d in $B $QC; do (cd $d && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5); mkdir -p $d/experiments $d/runs $d/dumps; done
echo fake > $F/bench_data/DEPLOY.md5; FMD5=$(m5 $F/bench_data/DEPLOY.md5); ln -s /home/noob/work/bench_data_v3b $F/bench_data_v3b
PIDS=""
live(){ sleep 1800 & PIDS="$PIDS $!"; echo $! > $1/queue.pid; }       # a live "queue process" for queue dir $1
mkq(){ mkdir -p $BQ/$1/pids; echo "$2" > $BQ/$1/MAXC; echo 1 > $BQ/$1/LPG; : > $BQ/$1/launch.log; live $BQ/$1; }
mkq c3all 8; cp $T/harness/c3base/c3all/jobs.txt $BQ/c3all/jobs.txt; echo "fake rendered" > $BQ/c3all/jobs_rendered.txt
i=0; for n in $(cut -d'|' -f1 $BQ/c3all/jobs.txt | head -33); do i=$((i+1)); echo $((i % 8)) > $BQ/c3all/pids/$n.gpu; [ $i -le 30 ] && touch $BQ/c3all/pids/$n.end; done
mkq c3base 0; mkq c3hrnet 0; mkq rows2 8; echo "[t] cv02 q: all jobs dispatched; waiting" >> $BQ/rows2/launch.log
N=dumptest_c3s_swad_f0; SM=$BQ/c3swad_smoke; M=dumps/elbench1/swad_const_pf_v11
smoke(){ rm -rf $SM; mkq c3swad_smoke 1; echo "$N|bench/methods/swad_const_pf_v11.yaml|5|$F/bench_data/roots/cv5v2_v11_f0|0|11000|5262|0|--fixture|swad" > $SM/jobs.txt; echo "[t] cv02 q armed: 1 jobs" >> $SM/launch.log; }

# ---- copies of the scripts under test
SED="s#ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#ssh -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106#bash -c#g; s#ssh -n -a -o BatchMode=yes -o ConnectTimeout=15 cv02@10.8.1.106#bash -c#g; s#/tmp/noob_el#$F#g; s#d6063fd83d20e656612540edda702cbe#$FMD5#g"
for f in c3swad_handover.sh c3swad_check.sh c3swad_dumptest.sh maxc_window_c3all2.sh; do sed "$SED" $HERE/$f > $W/s/$f; done
mkdir -p $W/relay_none; sed -i "s#/home/noob/work/bench_relay#$W/relay_none#g" $W/s/c3swad_handover.sh   # the name check of `build` must not depend on the real relays
cp $HERE/c3swad_make_jobs.py $HERE/diskguard3.sh $HERE/cq_c3swad.patch $W/s/
sed "s#/home/noob/work/bench_relay#$W/relay#g; s#/home/noob/work/bench_reads#$W/reads#g; s#nice -n 19 \$P scripts/bench_read_w1.py#sh -c 'echo STUB_READ_CALLED; exit 7' --#" $HERE/run_read_c3swad.sh > $W/s/run_read_c3swad.sh
cp $HERE/c3swad_class_guard.py $HERE/c3swad_verdict.py $W/s/
for f in c3swad_handover.sh c3swad_check.sh c3swad_dumptest.sh maxc_window_c3all2.sh run_read_c3swad.sh; do
  sed 's/ssh failed//g' $W/s/$f | grep -q "ssh" && { echo "REFUSED: copy of $f still holds 'ssh' (other than in the message 'ssh failed')"; kill $PIDS 2>/dev/null; exit 1; }; done
grep -c "tmp/noob_el" $W/s/c3swad_handover.sh $W/s/c3swad_dumptest.sh $W/s/c3swad_check.sh $W/s/maxc_window_c3all2.sh | grep -v ":0$" && { echo "REFUSED: a copy still names /tmp/noob_el"; kill $PIDS 2>/dev/null; exit 1; }
HO(){ IO=$W/io bash $W/s/c3swad_handover.sh "$@"; }
DT(){ QC=$QC bash $W/s/c3swad_dumptest.sh "$@"; }
echo "[$(date '+%F %T')] fake tree $F ready (B $(wc -l < $B/CODE.md5) files, QC $(wc -l < $QC/CODE.md5)); live fake queues: c3all (MAXC 8, 33 started), c3base 0, c3hrnet 0, rows2 (all dispatched)"

echo "--- T1 freeze refuses while another queue could start training (F1.2), and writes nothing"
mkq other 8; echo "x|bench/methods/house_r34_unetpp_pf_v11.yaml|5|r|0|9000|5262|1|" > $BQ/other/jobs.txt
HO freeze > $W/t1.out 2>&1; rc=$?
ck "T1 refused, names the queue" '[ $rc = 1 ] && grep -q "REFUSED (freeze): another live queue can start training (other )" $W/t1.out'
ck "T1 c3all/MAXC still 8, no MAXC.new, no freeze recorded" '[ "$(cat $BQ/c3all/MAXC)" = 8 ] && [ ! -e $BQ/c3all/MAXC.new ] && [ ! -e $W/io/freeze.time ]'
rm -f $BQ/other/MAXC; HO freeze > $W/t1b.out 2>&1
ck "T1 a live queue without a MAXC file (default 16) is also seen as able to start" 'grep -q "CAN_START other" $W/t1b.out && [ "$(cat $BQ/c3all/MAXC)" = 8 ]'
kill $(cat $BQ/other/queue.pid); sleep 1
echo "--- T2 freeze refuses when the queue to freeze has no live process"
p0=$(cat $BQ/c3all/queue.pid); echo 999999999 > $BQ/c3all/queue.pid; HO freeze > $W/t2.out 2>&1; rc=$?; echo $p0 > $BQ/c3all/queue.pid
ck "T2 refused, nothing written" '[ $rc = 1 ] && grep -q "c3all has no live queue process" $W/t2.out && [ "$(cat $BQ/c3all/MAXC)" = 8 ]'
echo "--- T3 freeze with a waiting fixture-only dump test queue (F1.1): passes; write by rename (F10)"
smoke; echo bench_q_c3swad_smoke >> $TMUXALIVE
DRY=1 HO freeze > $W/t3d.out 2>&1
ck "T3 DRY freeze prints the write and changes nothing" 'grep -q "DRY, not run on cv02: echo 0 > $BQ/c3all/MAXC.new && mv $BQ/c3all/MAXC.new $BQ/c3all/MAXC" $W/t3d.out && [ "$(cat $BQ/c3all/MAXC)" = 8 ]'
HO freeze > $W/t3.out 2>&1; rc=$?
ck "T3 freeze done: fixture-only queue counted ok, MAXC 0, no MAXC.new left, freeze recorded" '[ $rc = 0 ] && grep -q "ok c3swad_smoke fixture only, cannot train" $W/t3.out && grep -q "CAN_START c3all" $W/t3.out && [ "$(cat $BQ/c3all/MAXC)" = 0 ] && [ ! -e $BQ/c3all/MAXC.new ] && [ -s $W/io/freeze.time ]'
ck "T3 a second freeze is harmless (MAXC stays 0)" 'HO freeze > $W/t3b.out 2>&1 && [ "$(cat $BQ/c3all/MAXC)" = 0 ] && grep -q "ok c3all MAXC 0" $W/t3b.out'
echo "--- T4 build, place, guard (steps that were only dry-run before)"
SETTLE=0 HO build > $W/t4.out 2>&1; rc=$?
ck "T4 build: 62 lines = 37 carried + 25 swad, default order, md5 recorded" '[ $rc = 0 ] && [ "$(wc -l < $W/io/jobs.txt)" = 62 ] && [ "$(grep -c "^c3s_swad_" $W/io/jobs.txt)" = 25 ] && [ "$(sed -n 11p $W/io/jobs.txt | cut -d"|" -f1)" = c3s_swad_v11_f0_s5 ] && [ "$(cat $W/io/jobs.md5)" = "$(m5 $W/io/jobs.txt)" ]'
ck "T4 build twice is refused" '! SETTLE=0 HO build > $W/t4b.out 2>&1 && grep -q "jobs.txt exists" $W/t4b.out'
HO place > $W/t4p.out 2>&1; rc=$?
ck "T4 place: queue dir with read-only jobs.txt (md5 equal), LPG 1, MAXC 8, nothing else" '[ $rc = 0 ] && [ "$(m5 $BQ/c3all2/jobs.txt)" = "$(cat $W/io/jobs.md5)" ] && [ ! -w $BQ/c3all2/jobs.txt ] && [ "$(cat $BQ/c3all2/LPG)$(cat $BQ/c3all2/MAXC)" = 18 ] && [ "$(LC_ALL=C ls $BQ/c3all2 | tr "\n" " ")" = "LPG MAXC jobs.txt " ]'
ck "T4 place twice is refused" '! HO place > $W/t4q.out 2>&1 && grep -q "exists on cv02" $W/t4q.out'
HO guard > $W/t4g.out 2>&1; rc=$?
ck "T4 guard: reviewed diskguard3.sh placed, session started" '[ $rc = 0 ] && cmp -s $BQ/diskguard3.sh $HERE/diskguard3.sh && grep -qx bench_diskguard3 $TMUXALIVE && grep -q "new-session bench_diskguard3: bash $BQ/diskguard3.sh" $TMUXLOG'
cp -a $BQ/c3all2 $W/c3all2.placed; cp $TMUXALIVE $W/alive.placed
reset(){ chmod u+w $BQ/c3all2/jobs.txt 2>/dev/null; rm -rf $BQ/c3all2; cp -a $W/c3all2.placed $BQ/c3all2; cp $W/alive.placed $TMUXALIVE; rm -f $W/io/arm.out; }
echo "--- T5 arm (F1.1, F4): every pre-check runs in the fake tree; cq_setup.sh of QC is the real file, tmux is the stub"
DRY=1 QC=$QC HO arm > $W/t5d.out 2>&1; rc=$?
ck "T5 DRY arm: fixture-only queue ok, all pre-checks pass (queue dir, deploy, card, QC pins and QC against B, disk, guard), nothing started" '[ $rc = 0 ] && grep -q "ok c3swad_smoke fixture only, cannot train" $W/t5d.out && grep -q "ok c3all MAXC 0" $W/t5d.out && grep -q "differs from B only in cq.sh, cq_setup.sh, slim_ckpt.py" $W/t5d.out && grep -q "DRY, pre-checks passed; not run on cv02: B=$B Q=$BQ/c3all2 SES=bench_q_c3all2 DEPLOY=89b9ea5a12a37a87c16c4868cc4adf00794a7610 JOBS_MD5=$(cat $W/io/jobs.md5) DATA_MD5=$FMD5 QC=$QC bash $QC/bench/q/cv02/cq_setup.sh" $W/t5d.out && ! grep -q c3all2 $TMUXLOG'
FAKE_ARM=armed QC=$QC HO arm > $W/t5a.out 2>&1; rc=$?
ck "T5 arm with the 'cv02 q armed:' line in launch.log: reports armed" '[ $rc = 0 ] && grep -q "arm: armed bench_q_c3all2 (.cv02 q armed:. line seen" $W/t5a.out && grep -q "new-window bench_q_c3all2: B=$B Q=$BQ/c3all2 .* QC=$QC bash $QC/bench/q/cv02/cq.sh" $TMUXLOG'
ck "T5 a second arm is refused (queue dir used)" '! FAKE_ARM=armed QC=$QC HO arm > $W/t5a2.out 2>&1 && grep -q "REFUSED (arm): queue dir or deploy check" $W/t5a2.out'
reset; FAKE_ARM=refused QC=$QC HO arm > $W/t5b.out 2>&1; rc=$?
ck "T5 arm when cq.sh logs 'not starting': REFUSED and says so (F4)" '[ $rc = 1 ] && grep -q "REFUSED (arm): cq.sh did NOT arm: .cv02 q: gpumem logger (cq_gpumem.sh) not running; not starting.. c3all is frozen and no successor runs" $W/t5b.out && ! grep -q "arm: armed" $W/t5b.out'
reset; ARMWAIT=20 QC=$QC HO arm > $W/t5c.out 2>&1; rc=$?
ck "T5 arm when launch.log gets no line at all: REFUSED after the wait (F4)" '[ $rc = 1 ] && grep -q "REFUSED (arm): no .cv02 q armed:. line in $BQ/c3all2/launch.log after 20 s: arming is NOT confirmed" $W/t5c.out'
reset; mkq other2 8; echo "x|c|5|r|0|9000|5262|1|" > $BQ/other2/jobs.txt; n0=$(grep -c "bench_q_c3all2" $TMUXLOG); FAKE_ARM=armed QC=$QC HO arm > $W/t5e.out 2>&1; rc=$?
ck "T5 arm with another queue able to start: REFUSED at step 1, nothing started" '[ $rc = 1 ] && grep -q "CAN_START other2" $W/t5e.out && grep -q "another queue can still start training" $W/t5e.out && [ "$(grep -c "bench_q_c3all2" $TMUXLOG)" = "$n0" ] && [ ! -e $BQ/c3all2/launch.log ]'
kill $(cat $BQ/other2/queue.pid); sleep 1; rm -rf $BQ/other2
reset; echo "x|c|5|r|0|9000|5262|1|" >> $SM/jobs.txt; QC=$QC DRY=1 HO arm > $W/t5f.out 2>&1; rc=$?
ck "T5 a dump test queue that also holds a training line is NOT counted as fixture only" '[ $rc = 1 ] && grep -q "CAN_START c3swad_smoke" $W/t5f.out'
smoke
echo "--- T6 check.sh items 5 and 6 (F2, F1.1) on the fake tree"
mkdir -p $QC/$M/$N $QC/$M/$N.swad $QC/experiments/$N/checkpoints $QC/runs/$N
echo d > $QC/$M/$N/c0.npz; echo d > $QC/$M/$N.swad/c0.npz; echo l > $QC/experiments/$N/checkpoints/latest.pth; echo r > $QC/runs/$N/RUN.md5
NEWQ=c3all2 IO=$W/io bash $W/s/c3swad_check.sh > $W/t6a.out 2>&1
ck "T6 after a dump test (its dump folders in QC, its queue still alive): item 5 OK" 'grep -q "^OK   no swad run name and no c3s_\* run exists on cv02" $W/t6a.out'
ck "T6 fixture-only queue not counted: one queue (c3all2 would be the next; here none can start) " 'grep -q "^OK   live queues that can still start training: .. (at most one" $W/t6a.out && grep -q "c3swad_smoke MAXC 1 LPG 1 dispatched 0 HOLD 0 fixture_only 1" $W/t6a.out'
mkdir -p $B/$M/c3s_x; NEWQ=c3all2 IO=$W/io bash $W/s/c3swad_check.sh > $W/t6b.out 2>&1; rmdir $B/$M/c3s_x $B/$M
ck "T6 a swad_const dump folder in the live deploy B: item 5 FAIL" 'grep -q "^FAIL no swad run name and no c3s_\* run exists on cv02" $W/t6b.out'
mkq q1 8; rm -f $BQ/q1/MAXC; echo "x|c|5|r|0|9000|5262|1|" > $BQ/q1/jobs.txt; mkq q2 3; echo "x|c|5|r|0|9000|5262|1|" > $BQ/q2/jobs.txt
NEWQ=c3all2 IO=$W/io bash $W/s/c3swad_check.sh > $W/t6c.out 2>&1
ck "T6 two queues able to start (one without a MAXC file): item 6 FAIL and both named" 'grep -q "^FAIL live queues that can still start training: .q1 q2 ." $W/t6c.out && grep -q "q1 MAXC 16 LPG 1" $W/t6c.out'
kill $(cat $BQ/q1/queue.pid) $(cat $BQ/q2/queue.pid); sleep 1; rm -rf $BQ/q1 $BQ/q2
echo "--- T7 dumptest stop (F1.3)"
grep -qx bench_q_c3swad_smoke $TMUXALIVE || echo bench_q_c3swad_smoke >> $TMUXALIVE
DRY=1 DT stop > $W/t7d.out 2>&1
ck "T7 DRY stop prints the command, changes nothing" 'grep -q "DRY, not run on cv02: touch $SM/HOLD; sleep 20; .* tmux kill-session -t .=bench_q_c3swad_smoke." $W/t7d.out && [ ! -e $SM/HOLD ] && grep -qx bench_q_c3swad_smoke $TMUXALIVE'
echo "[t] fixture $N on GPU 3: training skipped" >> $SM/launch.log; DT stop > $W/t7a.out 2>&1; rc=$?
ck "T7 the fixture has a lane: nothing stopped, no HOLD left" '[ $rc = 1 ] && grep -q "REFUSED (stop): the fixture took a lane" $W/t7a.out && grep -qx bench_q_c3swad_smoke $TMUXALIVE && [ ! -e $SM/HOLD ] && ! grep -q "kill-session" $TMUXLOG'
smoke; ( sleep 6; echo "[t] fixture $N on GPU 3: training skipped" >> $SM/launch.log; echo 3 > $SM/pids/$N.gpu ) & DT stop > $W/t7b.out 2>&1; rc=$?; wait $! 2>/dev/null
ck "T7 the fixture takes a lane during the 20 s: nothing stopped, the HOLD is removed again" '[ $rc = 1 ] && grep -q "TOOK_LANE" $W/t7b.out && grep -qx bench_q_c3swad_smoke $TMUXALIVE && [ ! -e $SM/HOLD ] && ! grep -q "kill-session" $TMUXLOG'
smoke; DT stop > $W/t7c.out 2>&1; rc=$?
ck "T7 no lane taken: only the test's own session is ended, by exact name; HOLD removed" '[ $rc = 0 ] && grep -q "^stopped: tmux session bench_q_c3swad_smoke ended" $W/t7c.out && ! grep -qx bench_q_c3swad_smoke $TMUXALIVE && [ "$(grep -c "kill-session" $TMUXLOG)" = 1 ] && grep -qx "kill-session bench_q_c3swad_smoke" $TMUXLOG && [ ! -e $SM/HOLD ] && grep -qx bench_diskguard3 $TMUXALIVE'
ck "T7 stop without a live session is refused" '! DT stop > $W/t7e.out 2>&1 && grep -q "is not alive on cv02 (nothing to stop)" $W/t7e.out'
echo "--- T8 dumptest clean (F11)"
snapQC(){ (cd $QC && find . -type f -not -path "./experiments/$N/*" -not -path "./$M/$N/*" -not -path "./$M/$N.swad/*" -not -path "./runs/$N/*" | LC_ALL=C sort | xargs -d '\n' md5sum | md5sum | cut -c1-32); }
Q0=$(snapQC); B0=$(cd $B && find . -type f | LC_ALL=C sort | xargs -d '\n' md5sum | md5sum | cut -c1-32)
have(){ ls -d $QC/experiments/$N $QC/$M/$N $QC/$M/$N.swad $QC/runs/$N $SM 2>/dev/null | wc -l; }
DT clean > $W/t8a.out 2>&1; rc=$?
ck "T8 the test's queue process is alive: refused, nothing removed" '[ $rc = 1 ] && grep -q "QUEUE_ALIVE" $W/t8a.out && [ "$(have)" = 5 ]'
kill $(cat $SM/queue.pid); sleep 1
DRY=1 DT clean > $W/t8d.out 2>&1; rc=$?
ck "T8 DRY clean: prints the five folders and the command, removes nothing" '[ $rc = 0 ] && [ "$(grep -c "^have " $W/t8d.out)" = 5 ] && grep -q "DRY, not run on cv02: for d in $QC/experiments/$N $QC/$M/$N $QC/$M/$N.swad $QC/runs/$N $SM; do" $W/t8d.out && [ "$(have)" = 5 ]'
cp $QC/CODE.md5 $W/code.keep; echo "00000000000000000000000000000000  experiments/$N/checkpoints/latest.pth" >> $QC/CODE.md5; DT clean > $W/t8b.out 2>&1; rc=$?; cp $W/code.keep $QC/CODE.md5
ck "T8 a path of QC/CODE.md5 inside a folder of the list: refused, nothing removed" '[ $rc = 1 ] && grep -q "listed 1" $W/t8b.out && grep -q "nothing is removed" $W/t8b.out && [ "$(have)" = 5 ]'
DT clean > $W/t8c.out 2>&1; rc=$?
ck "T8 clean: the five folders are gone, list printed first, QC/CODE.md5 still checks" '[ $rc = 0 ] && [ "$(have)" = 0 ] && [ "$(grep -c "^removed " $W/t8c.out)" = 5 ] && [ "$(grep -n "^have " $W/t8c.out | head -1 | cut -d: -f1)" -lt "$(grep -n "^removed " $W/t8c.out | head -1 | cut -d: -f1)" ] && grep -q "clean done" $W/t8c.out'
ck "T8 every other file of QC and all of B unchanged" '[ "$(snapQC)" = "$Q0" ] && [ "$(cd $B && find . -type f | LC_ALL=C sort | xargs -d "\n" md5sum | md5sum | cut -c1-32)" = "$B0" ] && (cd $QC && md5sum -c --quiet CODE.md5)'
ck "T8 clean again: nothing to remove" 'DT clean > $W/t8e.out 2>&1 && grep -q "nothing to remove" $W/t8e.out'
echo "--- T9 MAXC window copy for c3all2 (F12)"
RM=$B/runs/c3_pf_v11_f3_s7/RUN.md5; mkdir -p $(dirname $RM); echo 8 > $BQ/c3all2/MAXC
DRY=1 bash $W/s/maxc_window_c3all2.sh $RM > $W/t9d.out 2>&1
ck "T9 DRY: reads only" 'grep -q "DRY: c3all2/MAXC reads 8; RUN.md5 present now: 0 of 1" $W/t9d.out && [ "$(cat $BQ/c3all2/MAXC)" = 8 ]'
( sleep 5; cat $BQ/c3all2/MAXC > $W/t9.mid; touch $RM ) & TMAX=120 bash $W/s/maxc_window_c3all2.sh $RM > $W/t9.out 2>&1; rc=$?; wait $! 2>/dev/null
ck "T9 window: 1 while waiting, 8 restored, c3all/MAXC never touched (still 0), no MAXC.new left" '[ $rc = 0 ] && [ "$(cat $W/t9.mid)" = 1 ] && [ "$(cat $BQ/c3all2/MAXC)" = 8 ] && [ "$(cat $BQ/c3all/MAXC)" = 0 ] && grep -q "MAXC restored to 8" $W/t9.out && [ ! -e $BQ/c3all2/MAXC.new ] && [ ! -e $BQ/c3all/MAXC.new ]'
echo 5 > $BQ/c3all2/MAXC; bash $W/s/maxc_window_c3all2.sh $RM > $W/t9b.out 2>&1; rc=$?
ck "T9 MAXC not 8: nothing changed" '[ $rc = 1 ] && grep -q "is not 8; nothing changed" $W/t9b.out && [ "$(cat $BQ/c3all2/MAXC)" = 5 ]'
echo "--- T10 read script (F7): a refused manifest check leaves no output folder"
MP=house_r34_unetpp_pf_v11; MS=swad_const_pf_v11; mkdir -p $W/relay/c3base/.ok $W/relay/c3swad/.ok
man(){ mkdir -p $1; echo "{\"run_id\": \"$2\", \"fold\": $3, \"seed\": $4, \"weights_key\": \"$5\", \"step\": 20000, \"set\": \"cv5v3_f$3\", \"precision\": \"fp32\", \"set_kind\": \"open\", \"train_code_revision\": \"89b9ea5a12a37a87c16c4868cc4adf00794a7610\", \"device\": \"NVIDIA RTX A6000\"}" > $1/manifest.json; }
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do
  r=c3_pf_v11_f${k}_s$s; man $W/relay/c3base/$r/dumps/elbench1/$MP/$r/cv5v3_f$k $r $k $s model; touch $W/relay/c3base/.ok/$r; echo "[t] relayed $r: 111 files" >> $W/relay/c3base/relay.log
  r=c3s_swad_v11_f${k}_s$s; man $W/relay/c3swad/$r/dumps/elbench1/$MS/$r/cv5v3_f$k $r $k $s swad_bn; man $W/relay/c3swad/$r/dumps/elbench1/$MS/$r.swad/cv5v3_f$k $r.swad $k $s swad
  mkdir -p $W/relay/c3swad/$r/experiments/$r; echo '{"step": 20000}' > $W/relay/c3swad/$r/experiments/$r/enc_probe.jsonl; touch $W/relay/c3swad/.ok/$r; echo "[t] relayed $r: 220 files" >> $W/relay/c3swad/relay.log
done; done
bad=$W/relay/c3swad/c3s_swad_v11_f2_s7/dumps/elbench1/$MS/c3s_swad_v11_f2_s7.swad/cv5v3_f2/manifest.json; cp $bad $W/man.keep; sed -i 's/"weights_key": "swad"/"weights_key": "swad_bn"/' $bad
bash $W/s/run_read_c3swad.sh > $W/t10a.out 2>&1; rc=$?
ck "T10 one wrong weights key: refused by the manifest check, output folder NOT created" '[ $rc = 1 ] && grep -q "manifest check: 75 dumps, device \[.NVIDIA RTX A6000.\]: FAIL" $W/t10a.out && grep -q "REFUSED: manifest check failed (nothing written" $W/t10a.out && [ ! -e $W/reads/c3swad ] && ! grep -q STUB_READ_CALLED $W/t10a.out'
cp $W/man.keep $bad; rm -rf $W/relay/c3swad/c3s_swad_v11_f0_s5/experiments; bash $W/s/run_read_c3swad.sh > $W/t10b.out 2>&1; rc=$?
ck "T10 one run without enc_probe.jsonl: refused as not complete, no output folder" '[ $rc = 1 ] && grep -q "REFUSED: 1 of 50 runs not relayed" $W/t10b.out && [ ! -e $W/reads/c3swad ]'
mkdir -p $W/relay/c3swad/c3s_swad_v11_f0_s5/experiments/c3s_swad_v11_f0_s5; echo '{"step": 20000}' > $W/relay/c3swad/c3s_swad_v11_f0_s5/experiments/c3s_swad_v11_f0_s5/enc_probe.jsonl
bash $W/s/run_read_c3swad.sh > $W/t10c.out 2>&1; rc=$?
ck "T10 complete and correct: folder created, 75 links, manifest line in run.log, the read is started (stub)" '[ $rc = 7 ] && [ "$(find $W/reads/c3swad/links -type l | wc -l)" = 75 ] && grep -q "manifest check: 75 dumps, device \[.NVIDIA RTX A6000.\]: OK" $W/reads/c3swad/run.log && grep -q STUB_READ_CALLED $W/reads/c3swad/run.log && [ "$(wc -l < $W/reads/c3swad/expected_dumps.tsv)" = 75 ]'
ck "T10 a second run is refused (output folder exists)" '! bash $W/s/run_read_c3swad.sh > $W/t10d.out 2>&1 && grep -q "output folder exists" $W/t10d.out'
echo "--- T11 gaint relay guard (F5)"
RR=$W/rr; mkdir -p $RR/c3base $RR/c3hrnet $RR/rows2 $RR/c3swad $RR/other $W/lg
sleep 600 & PIDS="$PIDS $!"; lp=$!; echo $lp > $RR/c3base/relay.pid; echo $lp > $RR/c3swad/relay.pid; echo $lp > $RR/other/relay.pid; echo 999999999 > $RR/c3hrnet/relay.pid
RR=$RR LOGD=$W/lg FLOOR=0 ONCE=1 bash $HERE/c3swad_relayguard.sh
ck "T11 free space above the floor: no STOP anywhere" '[ -z "$(ls $RR/*/STOP 2>/dev/null)" ]'
RR=$RR LOGD=$W/lg FLOOR=100000 ONCE=1 bash $HERE/c3swad_relayguard.sh
ck "T11 below the floor: STOP only for live relays among the four names (c3base, c3swad); dead (c3hrnet), no pid (rows2) and other dirs untouched" '[ "$(ls $RR/*/STOP | tr "\n" " ")" = "$RR/c3base/STOP $RR/c3swad/STOP " ] && [ "$(grep -c "STOP set for relay" $W/lg/relayguard.log)" = 2 ]'
ck "T11 nothing else written in the relay dirs" '[ "$(find $RR -type f | wc -l)" = 6 ]'
touch $W/lg/RELAYGUARD_STOP; RR=$RR LOGD=$W/lg FLOOR=100000 bash $HERE/c3swad_relayguard.sh
ck "T11 the stop file ends the guard at once" 'grep -q "relay guard ends" $W/lg/relayguard.log'
kill $PIDS 2>/dev/null; wait 2>/dev/null
echo "[$(date '+%F %T')] FIX1 TEST: $((NP+NF)) checks, $NP passed, $NF failed"
[ $NF = 0 ]
