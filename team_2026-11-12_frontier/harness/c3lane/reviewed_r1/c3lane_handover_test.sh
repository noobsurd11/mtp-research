#!/bin/bash
# c3lane: c3lane_handover.sh (c3all2 -> c3all3) in a FAKE cv02 tree on gaint; method of harness/c3swad/c3swad_fix1_test.sh:
# the script is COPIED with mechanical edits only (ssh call -> local `bash -c`, prefix /tmp/noob_el -> the fake root, the
# data md5 pin -> the fake file's, the gaint relay root -> an empty dir); the copy must hold no ssh call. tmux is a stub.
# B = archive of 89b9ea5, QC = archive of 5437778 + c3lane.patch, each with REVISION and CODE.md5. The fake c3all2 holds the
# real job list of c3all2 (29388346) with one started job. Nothing reaches cv02. CPU only.
# Usage: nice -n 19 bash c3lane_handover_test.sh <new work dir>      (about 2 minutes)
set -u
W=${1:?work dir (must not exist)}; [ -e "$W" ] && { echo "REFUSED: $W exists"; exit 1; }
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); SWD=$HERE/../c3swad
mkdir -p $W/bin $W/c3lane $W/c3swad $W/io $W/relay_none || exit 1; W=$(cd $W && pwd); F=$W/fake; BQ=$F/bench_q; B=$F/bench_89b9ea5; QC=$F/bench_2222222
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
NP=0; NF=0
ck(){ if eval "$2"; then NP=$((NP+1)); echo "PASS $1"; else NF=$((NF+1)); echo "FAIL $1   [$2]"; fi; }
m5(){ md5sum < "$1" | cut -c1-32; }
cat > $W/bin/tmux <<'EOF'
#!/bin/bash
A=$TMUXALIVE; touch $A
name(){ local p=""; for x in "$@"; do [ "$p" = -t ] || [ "$p" = -s ] && { x=${x#=}; echo "${x%:}"; return; }; p=$x; done; }
case "$1" in
  has-session) grep -qx "$(name "$@")" $A;;
  new-session) n=$(name "$@"); echo "$n" >> $A; echo "new-session $n: ${@: -1}" >> $TMUXLOG;;
  new-window) echo "new-window $(name "$@"): ${@: -1}" >> $TMUXLOG
    q=$(echo "${@: -1}" | grep -oE 'Q=[^ ]+' | head -1); q=${q#Q=}
    case "${FAKE_ARM:-}" in armed) echo "[t] cv02 q armed: 61 jobs (md5 x), cq 4fc8d2c0; sharing (live files in $q; 0 = off): SHARE_TRAIN $(cat $q/SHARE_TRAIN) MiB, SHARE_DUMP $(cat $q/SHARE_DUMP) MiB" >> $q/launch.log;;
      strict) echo "[t] cv02 q armed: 61 jobs (md5 x), cq 4fc8d2c0; sharing (live files in $q; 0 = off): SHARE_TRAIN 0 MiB, SHARE_DUMP 0 MiB" >> $q/launch.log;; esac;;
  *) exit 0;;
esac
EOF
chmod +x $W/bin/tmux; export PATH=$W/bin:$PATH TMUXALIVE=$W/tmux_alive TMUXLOG=$W/tmux.log; : > $TMUXALIVE; : > $TMUXLOG
[ "$(command -v tmux)" = $W/bin/tmux ] || { echo "stub tmux is not first in PATH"; exit 1; }
mkdir -p $B $QC $BQ $F/bench_data
git -C /home/noob/work/el_bench archive 89b9ea5 | tar -x -C $B && git -C /home/noob/work/el_bench archive 5437778 | tar -x -C $QC || exit 1
(cd $QC && git apply $HERE/c3lane.patch) || { echo "patch does not apply"; exit 1; }
echo 89b9ea5a12a37a87c16c4868cc4adf00794a7610 > $B/REVISION; echo 2222222222222222222222222222222222222222 > $QC/REVISION
for d in $B $QC; do (cd $d && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5); mkdir -p $d/experiments $d/runs $d/dumps; done
echo fake > $F/bench_data/DEPLOY.md5; FMD5=$(m5 $F/bench_data/DEPLOY.md5)
PIDS=""
mkq(){ mkdir -p $BQ/$1/pids; echo "$2" > $BQ/$1/MAXC; echo 1 > $BQ/$1/LPG; : > $BQ/$1/launch.log; sleep 1800 & PIDS="$PIDS $!"; echo $! > $BQ/$1/queue.pid; }
mkq c3all 0; mkq c3base 0; mkq c3hrnet 0; mkq rows2 8; echo "[t] cv02 q: all jobs dispatched; waiting" >> $BQ/rows2/launch.log
mkq c3all2 8; cp $SWD/evidence/preview_jobs_default_20261117_0936.txt $BQ/c3all2/jobs.txt; echo "fake rendered" > $BQ/c3all2/jobs_rendered.txt; echo 5 > $BQ/c3all2/pids/c3_pf_v11_f0_s8.gpu
mkq c3lane_smoke 1; echo "dumptest_c3s_swad_f0|c|5|r|0|11000|5262|0|--fixture|swad" > $BQ/c3lane_smoke/jobs.txt
cp $SWD/diskguard3.sh $BQ/diskguard3.sh; echo bench_diskguard3 >> $TMUXALIVE
SED="s#ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#ssh -a -o BatchMode=yes -o ConnectTimeout=20 \\\$C#bash -c#g; s#/tmp/noob_el#$F#g; s#d6063fd83d20e656612540edda702cbe#$FMD5#g; s#/home/noob/work/bench_relay#$W/relay_none#g"
sed "$SED" $HERE/c3lane_handover.sh > $W/c3lane/c3lane_handover.sh; cp $SWD/c3swad_make_jobs.py $SWD/diskguard3.sh $W/c3swad/
sed 's/ssh failed//g' $W/c3lane/c3lane_handover.sh | grep -q "ssh\|tmp/noob_el" && { echo "REFUSED: the copy still holds an ssh call or /tmp/noob_el"; kill $PIDS 2>/dev/null; exit 1; }
HO(){ IO=$W/io bash $W/c3lane/c3lane_handover.sh "$@"; }
echo "[$(date '+%F %T')] fake tree ready: c3all2 live (MAXC 8, 62 jobs $(m5 $BQ/c3all2/jobs.txt | cut -c1-8), 1 started), c3all, c3base, c3hrnet frozen, rows2 dispatched, a fixture-only test queue alive"
DRY=1 HO freeze > $W/h1.out 2>&1
ck "H1 DRY freeze: defaults c3all2 -> c3all3, prints the write, changes nothing" 'grep -q "DRY, not run on cv02: echo 0 > $BQ/c3all2/MAXC.new && mv $BQ/c3all2/MAXC.new $BQ/c3all2/MAXC" $W/h1.out && [ "$(cat $BQ/c3all2/MAXC)" = 8 ]'
HO freeze > $W/h2.out 2>&1; rc=$?
ck "H2 freeze: c3all2 MAXC 0 by rename; c3all already frozen; the fixture-only queue does not block" '[ $rc = 0 ] && [ "$(cat $BQ/c3all2/MAXC)" = 0 ] && [ ! -e $BQ/c3all2/MAXC.new ] && grep -q "ok c3all MAXC 0" $W/h2.out && grep -q "ok c3lane_smoke fixture only, cannot train" $W/h2.out && [ "$(cat $BQ/c3all/MAXC)" = 0 ]'
SETTLE=0 HO build > $W/h3.out 2>&1; rc=$?
ck "H3 build: 61 lines = the 61 not-started lines of c3all2, byte-equal, no new line; order PF, swad, HRNet, HOUSE" '[ $rc = 0 ] && [ "$(wc -l < $W/io/jobs.txt)" = 61 ] && grep -q "new swad lines: 0; output: 61 lines = pf 9, swad 25, hrnet 12, house 15" $W/h3.out && [ "$(grep -cFxf $BQ/c3all2/jobs.txt $W/io/jobs.txt)" = 61 ] && cmp -s $W/io/jobs.txt <(tail -n +2 $BQ/c3all2/jobs.txt) && [ "$(head -1 $W/io/jobs.txt | cut -d"|" -f1)" = c3_pf_v11_f1_s8 ]'
HO place > $W/h4.out 2>&1; rc=$?
ck "H4 place: c3all3 with jobs.txt (read-only, md5 equal), LPG 1, MAXC 8, SHARE_TRAIN 20480, SHARE_DUMP 10240" '[ $rc = 0 ] && [ "$(m5 $BQ/c3all3/jobs.txt)" = "$(cat $W/io/jobs.md5)" ] && [ ! -w $BQ/c3all3/jobs.txt ] && [ "$(cat $BQ/c3all3/LPG) $(cat $BQ/c3all3/MAXC) $(cat $BQ/c3all3/SHARE_TRAIN) $(cat $BQ/c3all3/SHARE_DUMP)" = "1 8 20480 10240" ] && [ "$(LC_ALL=C ls $BQ/c3all3 | tr "\n" " ")" = "LPG MAXC SHARE_DUMP SHARE_TRAIN jobs.txt " ]'
cp -a $BQ/c3all3 $W/c3all3.placed; cp $TMUXALIVE $W/alive.placed
reset(){ chmod u+w $BQ/c3all3/jobs.txt 2>/dev/null; rm -rf $BQ/c3all3; cp -a $W/c3all3.placed $BQ/c3all3; cp $W/alive.placed $TMUXALIVE; rm -f $W/io/arm.out; }
DRY=1 QC=$QC HO arm > $W/h5.out 2>&1; rc=$?
ck "H5 DRY arm: all pre-checks pass (frozen c3all2, started set, queue dir with the SHARE floors, deploy, card, QC pins incl. cq_rescue.sh, QC against B, disk, guard 3), nothing started" '[ $rc = 0 ] && grep -q "ok c3all2 MAXC 0" $W/h5.out && grep -q "SHARE_TRAIN 20480, SHARE_DUMP 10240, unused" $W/h5.out && grep -q "differs from B only in cq.sh, cq_setup.sh, slim_ckpt.py (changed) and cq_rescue.sh" $W/h5.out && grep -q "DRY, pre-checks passed; not run on cv02: B=$B Q=$BQ/c3all3 SES=bench_q_c3all3 DEPLOY=89b9ea5a12a37a87c16c4868cc4adf00794a7610 JOBS_MD5=$(cat $W/io/jobs.md5) DATA_MD5=$FMD5 QC=$QC bash $QC/bench/q/cv02/cq_setup.sh" $W/h5.out && ! grep -q c3all3 $TMUXLOG'
FAKE_ARM=armed QC=$QC HO arm > $W/h6.out 2>&1; rc=$?
ck "H6 arm: armed, and the report names the floors of the armed line" '[ $rc = 0 ] && grep -q "arm: armed bench_q_c3all3 (.cv02 q armed:. line seen; sharing (live files in $BQ/c3all3; 0 = off): SHARE_TRAIN 20480 MiB, SHARE_DUMP 10240 MiB;" $W/h6.out && ! grep -q WARNING $W/h6.out && grep -q "new-window bench_q_c3all3: B=$B Q=$BQ/c3all3 .* QC=$QC bash $QC/bench/q/cv02/cq.sh" $TMUXLOG'
reset; echo 20479 > $BQ/c3all3/SHARE_TRAIN; n0=$(grep -c c3all3 $TMUXLOG); FAKE_ARM=armed QC=$QC HO arm > $W/h7.out 2>&1; rc=$?
ck "H7 a SHARE_TRAIN below the user's floor in the placed dir: arm REFUSED, nothing started" '[ $rc = 1 ] && grep -q "REFUSED (arm): queue dir or deploy check: .* share 20479/10240 " $W/h7.out && [ "$(grep -c c3all3 $TMUXLOG)" = "$n0" ]'
reset; rm -f $BQ/c3all3/SHARE_DUMP; FAKE_ARM=armed QC=$QC HO arm > $W/h8.out 2>&1; rc=$?
ck "H8 a missing SHARE_DUMP in the placed dir: arm REFUSED" '[ $rc = 1 ] && grep -q "REFUSED (arm): queue dir or deploy check" $W/h8.out'
reset; FAKE_ARM=strict QC=$QC HO arm > $W/h9.out 2>&1; rc=$?
ck "H9 armed line without the floors (sharing off): armed, with a WARNING" '[ $rc = 0 ] && grep -q "WARNING: the armed line does not show SHARE_TRAIN 20480 and SHARE_DUMP 10240" $W/h9.out'
reset; cp $QC/bench/q/cv02/cq_rescue.sh $W/keep.rescue; echo "# x" >> $QC/bench/q/cv02/cq_rescue.sh; DRY=1 QC=$QC HO arm > $W/h10.out 2>&1; rc=$?; cp $W/keep.rescue $QC/bench/q/cv02/cq_rescue.sh
ck "H10 a changed cq_rescue.sh in QC: arm REFUSED (CODE.md5 / pins)" '[ $rc = 1 ] && grep -q "REFUSED (arm): QC" $W/h10.out'
kill $PIDS 2>/dev/null; wait 2>/dev/null
echo "[$(date '+%F %T')] C3LANE HANDOVER TEST: $((NP+NF)) checks, $NP passed, $NF failed"
[ $NF = 0 ]
