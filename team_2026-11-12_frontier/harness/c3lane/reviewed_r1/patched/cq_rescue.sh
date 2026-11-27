#!/bin/bash
# cq_rescue.sh (c3lane, 17 Nov 2026): run the WAITING DUMP of a finished training run of an OLDER cv02 queue under the
# shared-dump rule of cq.sh (lane rule v2), in place of that queue's own dump chain, which knows only the strict rule.
# Runs ON cv02 in tmux, from the new queue-code deploy:
#   OQ=<old queue dir> RQ=<rescue dir> bash <QC>/bench/q/cv02/cq_rescue.sh <run name> [<run name> ...]
#   DRYLIST=1 OQ=<old queue dir> bash <QC>/bench/q/cv02/cq_rescue.sh <finished run name>
#       read-only: prints "LIST OK" if the tool's RUN.md5 path list for that run equals the run's own RUN.md5, else the diff.
#   DRYLIST=1 LISTDIR=<dir with runs/<run>/RUN.md5 and the run's files, e.g. a relayed run on gaint> bash cq_rescue.sh <run>
#       the same check without a queue dir (the method is read from the RUN.md5 paths).
#   The list is compared in full (find on disk) when the run's dump folder is there. Where it was removed after the relay
#   (the practice on cv02) only the order is compared: the three fixed paths, then the listed dump paths as `sort` puts them.
# RQ (must exist): SHARE_DUMP (MiB, read live; absent or below 10240 = strict rule only), HOLD (while it exists no dump is
#   started), rescue.log, rescue.lock (one rescue at a time). Env: GPUS, OTHER_MAX (4096), GAPSEC (120), POLL (60),
#   LIVE_WAIT (300), RACE_WAIT (20), DATA, DATA_V3 (as cq.sh).
# Per run, in this order; any failure prints ONE line "RESCUE REFUSED <run>: ..." or "RESCUE FAILED <run>: ...", and the tool
# stops (no retry, no overwrite, later runs of the list are not touched):
#   0 refuses unless: the run is a 9-field line of OQ/jobs.txt (no extra, no further readouts: a swad line is REFUSED) with one
#     rendered dump line in OQ/jobs_rendered.txt; training rc 0 and a 'step 20000/20000' line; no .end; no RUN.md5, no runs/
#     dir, no slim.pth, no dump folder; no HOLD in OQ; the old deploy B checks (REVISION of the armed line, CODE.md5); the
#     run's chain subshell (PID from OQ/pids/subshells.txt) is alive, a child of OQ's main process (ps), both running the
#     old queue's cq.sh; and the tool's file list reproduces the RUN.md5 of a finished sibling run of OQ byte for byte.
#     (Resume: if an earlier call stopped the chain and wrote pids/<run>.rescued, and no dump was started, it goes on at c.)
#   a sets HOLD in OQ (so the old chain cannot start the dump), waits RACE_WAIT s, then
#   b if the old chain did start the dump in that moment: removes the HOLD, waits for the old chain to finish the run
#     (.end), reports it and starts NO dump; else: SIGTERM to the verified chain PID only, confirms it is gone, writes
#     pids/<run>.rescued, removes the HOLD;
#   c waits for a lane: the run's own GPU first, then other GPUS of the same model; strict rule or the shared-dump rule
#     (free >= SHARE_DUMP and >= the dump gate; no unknown owner, no unreadable memory); honours HOLD in RQ and in OQ and
#     the start gap of OQ;
#   d runs the dump command byte for byte as OQ rendered it, in OQ's B, with the environment of cq.sh / start_py, the same
#     pid, cmdline, rc and stdout files and the same BENCH_START check;
#   e slim checkpoint with the old queue's own slim_ckpt.py and RUN.md5 in the old queue's form (by rename);
#   f the old queue's usual log lines go into OQ/launch.log, with "RESCUE <run>: ..." marker lines (and "SHARED dump ..." if
#     the lane was shared);
#   g touches pids/<run>.end.
# Note: if the stopped chain was the last live part of a queue that had dispatched all its jobs (rows2), that queue's main
# process ends and writes its end line when the chain is stopped, before this dump: its gpumem logger stops 60 s later and
# its relay may end; restart that relay after the rescue.
set -u
DRYLIST=${DRYLIST:-0}; [ $DRYLIST = 1 ] && [ -n "${LISTDIR:-}" ] && OQ=${OQ:-/nonexistent}; OQ=${OQ:?old queue dir}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
GPUS=${GPUS:-0 1 2 3 4 5 6 7}; OTHER_MAX=${OTHER_MAX:-4096}; GAPSEC=${GAPSEC:-120}; POLL=${POLL:-60}; LIVE_WAIT=${LIVE_WAIT:-300}; RACE_WAIT=${RACE_WAIT:-20}
DATA=${DATA:-/tmp/noob_el/bench_data}; DATA_V3=${DATA_V3:-/tmp/noob_el/bench_data_v3b}
Q=$OQ; L=$OQ/launch.log; J=$OQ/jobs.txt; JR=$OQ/jobs_rendered.txt
[ $# -ge 1 ] || { echo "usage: OQ=<old queue dir> RQ=<rescue dir> cq_rescue.sh <run name> [...]"; exit 1; }
[ -n "${LISTDIR:-}" ] && [ $DRYLIST = 1 ] || { [ -s $J ] && [ -s $JR ] && [ -s $L ] && [ -d $OQ/pids ]; } || { echo "RESCUE REFUSED: $OQ is not a used cq.sh queue dir"; exit 1; }
olg(){ echo "[$(date '+%F %T')] $*" >> $L; }
# the file list of RUN.md5 in the old queues' form (cq.sh of b12fca8, 89b9ea5 and 5437778 for a line without readouts); cwd = B
runlist(){ echo experiments/$1/config_used.yaml; echo experiments/$1/checkpoints/slim.pth; echo runs/$1/LATEST.md5
  find dumps -path "dumps/*/$2/$1/*" -type f | sort; }
# samelist B RUN METHOD: 0 iff the list equals the paths of B/runs/RUN/RUN.md5; LMODE says how it was compared
samelist(){ local have; [ -s $1/runs/$2/RUN.md5 ] || return 1
  have=$(sed 's/^[0-9a-f]\{32\}  //' $1/runs/$2/RUN.md5)
  if [ -n "$(ls -d $1/dumps/*/$3/$2 2>/dev/null)" ]; then LMODE="files on disk"; [ "$(cd $1 && runlist $2 $3)" = "$have" ]
  else LMODE="order only, the dump folder is gone"
    [ "$(echo "$have" | grep -vc "^dumps/[^/]*/$3/$2/[^/]*/[^/]*\$")" = 3 ] && [ "$(echo "$have" | grep -c "^dumps/")" -ge 1 ] \
      && [ "$( (cd $1 && runlist $2 $3); echo "$have" | grep "^dumps/" | sort)" = "$have" ]; fi; }
# job N: sets DC (rendered dump command), B, PY, METH, DGATE, DUMPS from OQ's own files; returns 1 with WHY set
job(){ local n=$1 line; WHY=""
  [ "$(grep -c "^$n|" $J)" = 1 ] || { WHY="not exactly one line in $J"; return 1; }
  line=$(grep "^$n|" $J); IFS='|' read -r _n _card _seed _root _fold _gate DGATE _logp _extra _ro <<< "$line"
  [ -z "$_extra" ] || { WHY="job has extra '$_extra'"; return 1; }
  [ -z "$_ro" ] || { WHY="job has further readouts '$_ro' (a swad line): its chain makes two dumps and a slim with --keys; not handled by this tool"; return 1; }
  [ "$(grep -c "^dump_$n|" $JR)" = 1 ] || { WHY="not exactly one rendered dump line in $JR"; return 1; }
  DC=$(grep "^dump_$n|" $JR | cut -d'|' -f2-); PY=${DC%% *}
  B=$(echo "$DC" | sed -n "s#.* --run \([^ ]*\)/experiments/$n .*#\1#p"); METH=$(echo "$DC" | sed -n 's#.* --method \([^ ]*\) .*#\1#p')
  DUMPS=$(echo "$DC" | sed -n 's#.* --dumps \([^ ]*\) .*#\1#p')
  [ -n "$B" ] && [ -d "$B/experiments/$n" ] && [ -n "$METH" ] && [ "$DUMPS" = "$B/dumps" ] && [ -x "$PY" ] || { WHY="cannot read B, method, dumps dir or python from the rendered dump command"; return 1; }
  case "$DC" in *" --bench-run dump_$n") ;; *) WHY="rendered dump command does not end with --bench-run dump_$n"; return 1;; esac; }
if [ $DRYLIST = 1 ]; then rc=0
  for n in "$@"; do
    if [ -n "${LISTDIR:-}" ]; then B=$LISTDIR; METH=$(sed -n 's#^[0-9a-f]\{32\}  dumps/[^/]*/\([^/]*\)/.*#\1#p' $B/runs/$n/RUN.md5 2>/dev/null | head -1)
      [ -n "$METH" ] || { echo "LIST REFUSED $n: no RUN.md5 with dump paths under $B/runs/$n"; rc=1; continue; }
    else job $n || { echo "LIST REFUSED $n: $WHY"; rc=1; continue; }; fi
    if samelist $B $n $METH; then echo "LIST OK $n: $(grep -c . $B/runs/$n/RUN.md5) paths equal to $B/runs/$n/RUN.md5 (method $METH; $LMODE)"
    else echo "LIST DIFF $n (${LMODE:-no RUN.md5}):"; (cd $B && diff <(runlist $n $METH) <(sed 's/^[0-9a-f]\{32\}  //' runs/$n/RUN.md5 2>/dev/null) | head -5); rc=1; fi; done
  exit $rc; fi

RQ=${RQ:?rescue dir}; [ -d $RQ ] || { echo "RESCUE REFUSED: rescue dir $RQ does not exist"; exit 1; }
RL=$RQ/rescue.log; lg(){ echo "[$(date '+%F %T')] $*" >> $RL; }      # lane status lines of lane_ok go to the rescue log
exec 9> $RQ/rescue.lock; flock -n 9 || { echo "RESCUE REFUSED: another cq_rescue.sh holds $RQ/rescue.lock"; exit 1; }
[ -r /tmp/noob_el/env.sh ] && . /tmp/noob_el/env.sh
MAIN=$(cat $OQ/queue.pid 2>/dev/null); ARMED=$(grep 'cv02 q armed:' $L | tail -1)
DEPLOY=$(echo "$ARMED" | sed -n 's/.* deploy \([0-9a-f]\{40\}\) .*/\1/p')
OQC=$(echo "$ARMED" | sed -n 's/.*; queue code QC \([^ ]*\) .*/\1/p')
MYHOLD=0; trap '[ $MYHOLD = 1 ] && rm -f $OQ/HOLD' EXIT
no(){ echo "RESCUE REFUSED $n: $*"; lg "REFUSED $n: $*"; exit 1; }
bad(){ echo "RESCUE FAILED $n: $*"; lg "FAILED $n: $*"; olg "RESCUE $n: FAILED: $*"; exit 1; }
cmdof(){ tr '\0' ' ' < /proc/$1/cmdline 2>/dev/null; }
for n in "$@"; do
  # ---- 0 checks (nothing is changed before all of them hold)
  job $n || no "$WHY"
  . $B/bench/q/bench_lib.sh                                  # verify, stop_verified, startcheck, has_token, cmdl (the old queue's own)
  . <(sed -n '/^# ---- lanes/,/^# ---- arming/p' $HERE/cq.sh)  # uuid, gfree, ours, other_on, lane_ok, gap_take, share_floor, share_ok
  SQ=$RQ                                                     # the SHARE_DUMP file of the rescue dir
  export BENCH_LABELED=$DATA/labeled BENCH_CV5V2_ROOTS=$DATA/roots BENCH_CV5V3_ROOTS=$DATA_V3/roots BENCH_MASKS_V11=$DATA/masks_v11 BENCH_LEGACY_SPLITS=$B/data/splits
  SLIM=${OQC:-$B}/bench/q/cv02/slim_ckpt.py; [ -s $SLIM ] || no "the old queue's slim tool $SLIM is missing"
  [ -n "$DEPLOY" ] && [ "$(cat $B/REVISION 2>/dev/null)" = "$DEPLOY" ] && (cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || no "old deploy $B does not check (REVISION of the armed line, CODE.md5)"
  [ ! -e $OQ/HOLD ] || no "HOLD is set in $OQ"
  [ "$(cat $OQ/pids/$n.rc 2>/dev/null)" = 0 ] || no "training rc is '$(cat $OQ/pids/$n.rc 2>/dev/null)' (not finished, or failed)"
  [ "$(grep -c 'step 20000/20000' $B/experiments/$n.stdout 2>/dev/null)" -ge 1 ] 2>/dev/null || no "no 'step 20000/20000' line in $B/experiments/$n.stdout"
  [ ! -e $OQ/pids/$n.end ] || no "the run's chain has ended (pids/$n.end exists)"
  [ ! -e $B/runs/$n ] || no "$B/runs/$n exists"
  [ ! -e $B/experiments/$n/checkpoints/slim.pth ] && [ -s $B/experiments/$n/checkpoints/latest.pth ] && [ -s $B/experiments/$n/config_used.yaml ] || no "slim.pth exists, or latest.pth or config_used.yaml is missing"
  [ -z "$(ls -d $DUMPS/*/$METH/$n 2>/dev/null)" ] || no "a dump folder of the run exists"
  g=$(cat $OQ/pids/$n.gpu 2>/dev/null); case "$g" in [0-9]|[0-9][0-9]) ;; *) no "no GPU recorded in pids/$n.gpu";; esac
  sib=""; for x in $(grep -v "^$n|" $J | cut -d'|' -f1); do [ -s $B/runs/$x/RUN.md5 ] && grep -q "^dump_$x|.* --method $METH " $JR && { sib=$x; break; }; done
  [ -n "$sib" ] && samelist $B $sib $METH || no "the file list does not reproduce the RUN.md5 of a finished sibling run of this queue (sibling '${sib:-none}')"
  cp=$(grep "^$n chain " $OQ/pids/subshells.txt 2>/dev/null | tail -1 | cut -d' ' -f3)
  started(){ [ -e $OQ/pids/dump_$n.pid ] || grep -q "\] start dump_$n on GPU" $L; }
  chain_ok(){ case "$cp$MAIN" in ''|*[!0-9]*) return 1;; esac; kill -0 $cp 2>/dev/null && kill -0 $MAIN 2>/dev/null \
      && [ "$(ps -o ppid= -p $cp | tr -d ' ')" = "$MAIN" ] && case "$(cmdof $MAIN)" in *"/bench/q/cv02/cq.sh "*) [ "$(cmdof $cp)" = "$(cmdof $MAIN)" ];; *) false;; esac; }
  if [ -e $OQ/pids/$n.rescued ] && ! kill -0 "${cp:-x}" 2>/dev/null && ! started; then lg "resume $n: the chain was stopped by an earlier call ($(cat $OQ/pids/$n.rescued))"
  else
    chain_ok || no "the run's chain subshell (pid '${cp:-none}') is not alive as a child of the queue's main process (pid '${MAIN:-none}') running the old cq.sh"
    # ---- a, b: keep the old chain from starting the dump, then stop it, or let it finish if it had just started
    if ! started; then touch $OQ/HOLD; MYHOLD=1; lg "$n: HOLD set in $OQ for $RACE_WAIT s (old chain pid $cp, main $MAIN)"; sleep $RACE_WAIT; fi
    if started; then rm -f $OQ/HOLD; MYHOLD=0; lg "$n: the old chain started the dump itself; waiting for it to finish"
      while [ ! -e $OQ/pids/$n.end ] && kill -0 $cp 2>/dev/null; do sleep 5; done
      [ -e $OQ/pids/$n.end ] || bad "the old chain ended without pids/$n.end after starting the dump itself"
      echo "RESCUE $n: nothing to do, the old chain ran the dump itself ($(grep "RUN.md5 $n rc=" $L | tail -1 | cut -d' ' -f3-))"; lg "$n: old chain finished by itself"; continue; fi
    chain_ok || { rm -f $OQ/HOLD; MYHOLD=0; no "the chain is no longer verified after the wait"; }
    kill -TERM $cp; t=0; while kill -0 $cp 2>/dev/null && [ $t -lt 20 ]; do sleep 1; t=$((t+1)); done
    kill -0 $cp 2>/dev/null && { rm -f $OQ/HOLD; MYHOLD=0; bad "the chain pid $cp is still alive 20 s after SIGTERM (no further signal sent)"; }
    echo "$(date '+%F %T') chain pid $cp stopped by cq_rescue.sh" > $OQ/pids/$n.rescued
    olg "RESCUE $n: the waiting dump chain (pid $cp) was stopped by cq_rescue.sh $(md5sum < $0 | cut -c1-8); the dump is run under the shared-dump rule (rescue dir $RQ)"
    rm -f $OQ/HOLD; MYHOLD=0
  fi
  # ---- c: a lane
  gm=$(timeout 10 nvidia-smi --query-gpu=name --format=csv,noheader -i $g 2>/dev/null); lw=""
  while :; do h=""; SHD=""
    if [ -e $RQ/HOLD ] || [ -e $OQ/HOLD ]; then w="HOLD"
    else for c in $g $(for x in $GPUS; do [ $x = $g ] || echo $x; done); do
        [ $c = $g ] || [ "$(timeout 10 nvidia-smi --query-gpu=name --format=csv,noheader -i $c 2>/dev/null)" = "$gm" ] || continue
        if lane_ok $c $DGATE 1; then h=$c; break; elif share_ok $c dump $DGATE; then h=$c; SHD="beside $SHO; free $SHF MiB >= SHARE_DUMP $SHL"; break; fi; done
      if [ -z "$h" ]; then w="no GPU qualifies (own GPU $g, strict rule or SHARE_DUMP $(share_floor SHARE_DUMP $SHARE_DUMP_MIN))"
      elif ! gap_take; then sleep 10; continue
      elif [ -e $RQ/HOLD ] || [ -e $OQ/HOLD ]; then w="HOLD"
      else break; fi; fi
    [ "$w" != "$lw" ] && lg "dump of $n waits: $w"; lw=$w; sleep $POLL
  done
  # ---- d: the dump, as chain_after / start_py of the old queue
  (cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || bad "old deploy $B does not check before the dump"
  dn=dump_$n
  [ -z "$SHD" ] || olg "SHARED dump $dn on GPU $h: $SHD"
  olg "RESCUE $n: $dn is started by cq_rescue.sh on GPU $h (the run trained on GPU $g)"
  olg "start $dn on GPU $h (free $(gfree $h) MiB, dump gate $DGATE)"
  ( cd $B || exit 1; set -f; export CUDA_VISIBLE_DEVICES=$h HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
    $DC > $OQ/dlogs/$dn.stdout 2>&1 &
    pp=$!; echo $pp > $OQ/pids/$dn.pid
    wait $pp; rc=$?; echo $rc > $OQ/pids/$dn.rc ) &
  SSUB=$!; d=""; t=0
  while [ $t -lt 20 ]; do pp=$(cat $OQ/pids/$dn.pid 2>/dev/null); [ -n "$pp" ] && has_token "$(cmdl $pp)" "$dn" && { d=$pp; break; }; sleep 1; t=$((t+1)); done
  [ -n "$d" ] || { touch $RQ/HOLD; bad "no cmdline with $dn's token within 20 s; HOLD set in $RQ"; }
  cmdl $d > $OQ/pids/$dn.cmdline
  olg "pid $dn $d (python; parent $(ps -o ppid= -p $d | tr -d ' ')); cmdline recorded ($(md5sum < $OQ/pids/$dn.cmdline | cut -c1-8))"
  m=$(startcheck $OQ/dlogs/$dn.stdout "BENCH_START: run=$dn" $LIVE_WAIT) || { touch $RQ/HOLD; olg "$dn $m; live check FAILED: stop by verified PID"; stop_verified $dn $d; bad "$dn $m; the dump was stopped; HOLD set in $RQ"; }
  olg "$dn $m"
  while kill -0 $SSUB 2>/dev/null; do sleep 5; done
  drc=$(cat $OQ/pids/$dn.rc 2>/dev/null || echo none)
  olg "dumped $dn rc=$drc: 'dumped' lines $(grep -c '^dumped ' $OQ/dlogs/$dn.stdout), Traceback lines $(grep -c Traceback $OQ/dlogs/$dn.stdout)"
  [ "$drc" = 0 ] && grep -q '^dumped ' $OQ/dlogs/$dn.stdout || { touch $OQ/pids/$n.end; bad "the dump ended rc $drc; no slim, no RUN.md5; lane released (as the old chain does)"; }
  # ---- e: slim checkpoint and RUN.md5, in the old queue's form
  (cd $B && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $PY $SLIM --run experiments/$n > $OQ/dlogs/slim_$n.log 2>&1); rc=$?
  if [ $rc = 0 ]; then mkdir -p $B/runs/$n
    (cd $B && md5sum experiments/$n/checkpoints/latest.pth > runs/$n/LATEST.md5 \
      && runlist $n $METH | xargs -d '\n' md5sum > runs/$n/RUN.md5.tmp && mv runs/$n/RUN.md5.tmp runs/$n/RUN.md5); rc=$?
    olg "RUN.md5 $n rc=$rc: $(wc -l < $B/runs/$n/RUN.md5 2>/dev/null) files, md5 $(md5sum < $B/runs/$n/RUN.md5 2>/dev/null | cut -c1-8)"
  else olg "slim checkpoint FAILED for $n (rc $rc; dlogs/slim_$n.log); no RUN.md5"; fi
  touch $OQ/pids/$n.end
  [ $rc = 0 ] || bad "slim or RUN.md5 failed (rc $rc); lane released"
  olg "RESCUE $n: done by cq_rescue.sh (dump on GPU $h${SHD:+, shared}; RUN.md5 $(wc -l < $B/runs/$n/RUN.md5) files); lane released"
  echo "RESCUE $n: done (dump on GPU $h${SHD:+, shared: $SHD}; RUN.md5 $(wc -l < $B/runs/$n/RUN.md5) files, md5 $(md5sum < $B/runs/$n/RUN.md5 | cut -c1-8))"; lg "$n: done on GPU $h"
done
