#!/bin/bash
# elbench queue for cv02 (shared lab account, 8 GPUs) = b6_cv02_queue.sh 56f9e72d lanes + bench_q.sh live checks + bench_lib.sh
# verify / stop_verified / startcheck, with a per-run chain: train -> dump the held-out fold on the SAME GPU (fp32, TF32 off)
# -> slim checkpoint (CPU) -> runs/<name>/RUN.md5 (the relay on gaint pulls a run once its RUN.md5 exists).
#
# Env (required): B (deploy dir = git archive + REVISION + CODE.md5), Q (queue dir), JOBS_MD5, DEPLOY (full commit),
#   DATA_MD5 (md5 of DATA/DEPLOY.md5). Optional: DATA (/tmp/noob_el/bench_data), GPUS ("0 1 2 3 4 5 6 7"), OTHER_MAX (4096),
#   GAPSEC (120), POLL (60), LIVE_WAIT (300), P (house venv python). Dumps go to B/dumps, slim checkpoints to
#   B/experiments/<name>/checkpoints/slim.pth, RUN.md5 to B/runs/<name>/ (paths relative to B).
# Files in Q: jobs.txt, LPG (our runs per GPU, default 2, max 2), MAXC (our runs alive in total, default 16), HOLD,
#   pids/ (<job>.pid = python PID, <job>.cmdline, <job>.rc, <job>.gpu, <job>.end), dlogs/ (dump stdouts), launch.log.
# jobs.txt, one job per line:  name|card|seed|data_root|fold|gate_mib|dump_gate_mib|logp|extra
#   card = bench/methods/<m>.yaml (rendered, cfgchecked and named in the dump exactly as on gaint); its weights files are
#   md5-checked at the paths of bench/methods_cv02/<m>.yaml, which must equal the card except weights paths (cvcard.py).
#   logp 1 = dump with --logp. extra = only '--exit_after_step N', only for smoke_* jobs (rc 3 by design; no dump), or
#   '--fixture', only for dumptest_* jobs: no training; B/experiments/<name>/ is a placed finished run (config_used.yaml +
#   checkpoints/latest.pth) and the chain runs from the dump step on (dry test of dump, slim, RUN.md5 and relay).
#   Optional 10th field (c3swad): name|...|logp|extra|readouts = comma list of further weights keys of the card's readouts
#   (not its weights_key). After the usual dump (run id <name>, the card's weights_key) each key K is dumped the same way
#   (same GPU, same gate, same waits) with --run-id <name>.K --weights-key K (job dump_<name>.K). All dumps must end rc 0.
#   The slim checkpoint then keeps only the dumped keys, and RUN.md5 also lists the further dump dirs and
#   experiments/<name>/enc_probe.jsonl if present. A line without the field behaves exactly as before.
# QC (optional env, default B): the deploy dir that holds the queue code (this script, cvcard.py, slim_ckpt.py) and
#   bench/methods_cv02. With QC != B, training and dumps still run in B from B's code; QC/CODE.md5 is checked like B's.
# Lane rule (per GPU g, checked live before every start, training or dump): no other user holds > OTHER_MAX MiB on g in
#   sum over the compute processes on g that are not ours ("ours" = live PIDs in Q/pids/*.pid and their children; the
#   account is shared; owner unreadable = one bucket "unknown"; unreadable memory = over); fewer than LPG
#   of our runs on g (a run holds its lane from start until its chain ends); free on g >= the job's gate; >= GAPSEC s since
#   our last start (flock Q/start.lock); no HOLD. A GPU taken by another user is skipped (logged), never contested; the
#   queue waits and takes GPUs as they qualify. A dump waits for ITS run's GPU to qualify again (lane rule, dump gate).
# Lane rule v2 (c3lane, user's decision of 17 Nov 2026): SHARED GPUs, only when the strict rule above gives no lane.
#   Floors in MiB are read LIVE from two files in Q: SHARE_TRAIN and SHARE_DUMP. A file that is absent, empty, not a number,
#   or below the user's floor (20480 / 10240) switches that kind of sharing off: then the strict rule alone holds.
#   Shared TRAINING start on GPU g (one pass over all GPUs with the strict rule comes first, at every look): free memory
#   on g >= SHARE_TRAIN at two looks at g that are at least 30 s and at most 120 s apart (the time is taken at each look),
#   with no failed look at g and no pass without a look (HOLD, MAXC full, logger gone, a strict lane found, a start)
#   between them; none of the owners above OTHER_MAX is our own login
#   (a run of another of our queues, a lab member on the shared login), the bucket "unknown", or one with unreadable
#   memory; fewer than LPG of our runs on g; free >= the job's gate. Among such GPUs the one with most free memory.
#   Shared DUMP on the run's GPU: free memory >= SHARE_DUMP and >= the dump gate; any readable owner, our own login
#   included; an unknown owner or unreadable memory blocks. A --fixture job (no training) takes its lane by the dump rule.
#   Log: "SHARED start <name> on GPU g: beside <owners>; free <f> MiB >= SHARE_TRAIN <floor> ..." before the usual start
#   line, "SHARED dump <dump job> on GPU g: ..." before the usual dump start line; the usual lines are unchanged.
# Arming (any failure: one line, exit 1): jobs md5; REVISION = DEPLOY and CODE.md5; DATA/DEPLOY.md5 md5 = DATA_MD5 and
#   md5sum -c; roots ROOTS_cv5v2_*.md5, and per job root SPLITS.md5 + DATA_MANIFEST.md5, test.txt = val.txt, name _f<fold>;
#   every card valid, its cv02 variant differs only in weights paths, weights md5 OK; job gate >= card gate; logger alive.
# Live check per training start (before the next start): cfgcheck (config_used.yaml == the card's rendered config) and the
#   first 'Labelled:' line == the one implied by the root's lists; per dump: 'BENCH_START: run=dump_<name>'.
#   Failure: HOLD + stop_verified (SIGTERM, 30 s, owner + cmdline re-check, SIGKILL) of that PID only.
# Never: a restart, an overwrite (existing experiments/<name> is skipped), a pattern kill, a signal to an unverified PID.
# End line: "BENCH CV02 Q ALL DONE (...)". rc captured before any $(date).
set -u
B=${B:?deploy dir}; Q=${Q:?queue dir}; JOBS_MD5=${JOBS_MD5:?}; DEPLOY=${DEPLOY:?full commit}; DATA_MD5=${DATA_MD5:?}
DATA=${DATA:-/tmp/noob_el/bench_data}; DATA_V3=${DATA_V3:-/tmp/noob_el/bench_data_v3b}; GPUS=${GPUS:-0 1 2 3 4 5 6 7}; OTHER_MAX=${OTHER_MAX:-4096}; GAPSEC=${GAPSEC:-120}
POLL=${POLL:-60}; LIVE_WAIT=${LIVE_WAIT:-300}; P=${P:-/tmp/noob_el/el-fault-detection/.venv/bin/python}; DUMPS=$B/dumps
L=$Q/launch.log; J=$Q/jobs.txt; QC=${QC:-$B}; HERE=$QC/bench/q/cv02
. /tmp/noob_el/env.sh   # HF_HOME / TORCH_HOME / TMPDIR under /tmp/noob_el (as every earlier cv02 run)
. $B/bench/q/bench_lib.sh   # verify, stop_verified, startcheck, has_token, cmdl, psl
export BENCH_LABELED=$DATA/labeled BENCH_CV5V2_ROOTS=$DATA/roots BENCH_CV5V3_ROOTS=$DATA_V3/roots BENCH_MASKS_V11=$DATA/masks_v11 BENCH_LEGACY_SPLITS=$B/data/splits
lg(){ echo "[$(date '+%F %T')] $*" >> $L; }
fail(){ lg "cv02 q: $1; not starting"; exit 1; }
mkdir -p $Q/pids $Q/dlogs $B/experiments $B/runs $DUMPS; touch $L $Q/start.lock; echo $$ > $Q/queue.pid
cards_py(){ (cd $B && $P -m bench.cards "$@"); }
cnt(){ grep -c . "$1"; }
want_line(){ local r=$1; echo "Labelled: $(cnt $r/splits/train.txt) ($r/splits/train.txt)  unlabelled: 0 (-)  val: $(cnt $r/splits/val.txt)  test: $(cnt $r/splits/test.txt)"; }
yget(){ (cd $B && $P -c 'import sys, yaml; c = yaml.safe_load(open(sys.argv[1]))
for k in sys.argv[2].split("."): c = c[k]
print(c)' "$1" "$2"); }
deploy_ok(){ [ "$(cat $B/REVISION 2>/dev/null)" = "$DEPLOY" ] && (cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) \
  && { [ "$QC" = "$B" ] || (cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1); }; }
# dcmd2 CMD NAME KEY: the dump command of a further readout KEY, made from the job's own dump command CMD
dcmd2(){ local c=${1/ --run-id $2 / --run-id $2.$3 --weights-key $3 }; echo "${c/%--bench-run dump_$2/--bench-run dump_$2.$3}"; }

# ---- lanes
uuid(){ timeout 10 nvidia-smi --query-gpu=uuid --format=csv,noheader -i $1 2>/dev/null | tr -d ' '; }
gfree(){ timeout 10 nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '; }
ours(){ local f p; for f in $Q/pids/*.pid; do [ -e "$f" ] || continue; p=$(tr -dc 0-9 < $f); [ -n "$p" ] && kill -0 $p 2>/dev/null || continue
  echo $p; ps -o pid= --ppid $p 2>/dev/null | tr -d ' '; done; }
# other_on G: "user:MiB(pid,..) " for every user whose compute processes on GPU G that are not ours hold > OTHER_MAX MiB
#   IN SUM (owner from ps; no readable owner -> one bucket "unknown"; a non-numeric used_memory such as [N/A], or a
#   non-numeric pid, counts as over: "+N/A"). rc 2 if nvidia-smi fails.
other_on(){ local u o gu p m a w; local -A S=() X=() PL=(); u=$(uuid $1); [ -n "$u" ] || return 2; o=" $(ours | tr '\n' ' ') "
  a=$(timeout 10 nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits 2>/dev/null) || return 2
  while IFS=, read -r gu p m; do gu=$(echo $gu | tr -d ' '); p=$(echo $p | tr -d ' '); m=$(echo $m | tr -d ' ')
    [ "$gu" = "$u" ] || continue
    case "$p" in ''|*[!0-9]*) w=unknown; X[$w]=1; PL[$w]="${PL[$w]:+${PL[$w]},}$p"; continue;; esac
    case "$o" in *" $p "*) continue;; esac
    w=$(ps -o user= -p $p 2>/dev/null | tr -d ' '); w=${w:-unknown}; PL[$w]="${PL[$w]:+${PL[$w]},}$p"
    case "$m" in ''|*[!0-9]*) X[$w]=1;; *) S[$w]=$(( ${S[$w]:-0} + m ));; esac; done <<< "$a"
  for w in $(printf '%s\n' "${!PL[@]}" | sort); do
    [ -n "${X[$w]:-}" ] || [ "${S[$w]:-0}" -gt "$OTHER_MAX" ] && echo -n "$w:${S[$w]:-0}${X[$w]:++N/A}MiB(${PL[$w]}) "; done; return 0; }
lanes_on(){ local f n=0; for f in $Q/pids/*.gpu; do [ -e "$f" ] || continue; [ -e "${f%.gpu}.end" ] && continue
  [ "$(cat $f)" = "$1" ] && n=$((n + 1)); done; echo $n; }
lanes_all(){ local f n=0; for f in $Q/pids/*.gpu; do [ -e "$f" ] && [ ! -e "${f%.gpu}.end" ] && n=$((n + 1)); done; echo $n; }
LPG(){ local v; v=$(cat $Q/LPG 2>/dev/null || echo 2); case "$v" in 1|2) echo $v;; *) echo 2;; esac; }
# lane_ok G GATE [SELF]: 0 iff GPU G qualifies now (SELF = 1: the caller already holds a lane on G, i.e. a dump)
declare -A WHY
lane_ok(){ local g=$1 gate=$2 self=${3:-0} o f r
  o=$(other_on $g); r=$?
  if [ $r != 0 ]; then r="nvidia-smi read failed"
  elif [ -n "$o" ]; then r="another user > $OTHER_MAX MiB: $o"
  elif [ $self = 0 ] && [ "$(lanes_on $g)" -ge "$(LPG)" ]; then r="our runs on GPU = LPG $(LPG)"
  else f=$(gfree $g); case "$f" in ''|*[!0-9]*) r="free unreadable";; *) [ "$f" -ge "$gate" ] && r="" || r="free $f < $gate";; esac; fi
  if [ "${WHY[$g]:-}" != "$r" ]; then lg "lane GPU $g: ${r:-qualifies}"; WHY[$g]=$r; fi
  [ -z "$r" ]; }
gap_take(){ flock $Q/start.lock bash -c 'a=$(( $(date +%s) - $(stat -c %Y '$Q'/last_start 2>/dev/null || echo 0) )); [ $a -ge '$GAPSEC' ] && touch '$Q'/last_start'; }
logger_ok(){ kill -0 "$(cat $Q/gpumem.pid 2>/dev/null)" 2>/dev/null; }
# ---- lane rule v2: shared GPUs (see the header). SQ = the dir of the SHARE files (the queue dir; cq_rescue.sh sets its own).
SHARE_TRAIN_MIN=20480; SHARE_DUMP_MIN=10240; SHARE_WAIT=30; SHARE_STALE=120; SQ=${SQ:-$Q}
share_floor(){ local v; v=$(cat $SQ/$1 2>/dev/null); case "$v" in ''|*[!0-9]*) echo 0;; *) [ "$v" -ge "$2" ] && echo "$v" || echo 0;; esac; }
# share_ok G train|dump GATE: 0 iff GPU G may be shared now. Sets SHF (free MiB), SHO (owners above OTHER_MAX), SHL (floor).
share_ok(){ local g=$1 kind=$2 gate=$3 fl o t f
  [ $kind = train ] && fl=$(share_floor SHARE_TRAIN $SHARE_TRAIN_MIN) || fl=$(share_floor SHARE_DUMP $SHARE_DUMP_MIN)
  [ "$fl" -gt 0 ] || return 1
  o=$(other_on $g) || return 1
  for t in $o; do case "$t" in unknown:*|*+N/AMiB\(*) return 1;; esac
    [ $kind = train ] && case "$t" in "$ME":*) return 1;; esac; done
  [ $kind = train ] && [ "$(lanes_on $g)" -ge "$(LPG)" ] && return 1
  f=$(gfree $g); case "$f" in ''|*[!0-9]*) return 1;; esac
  [ "$f" -ge "$fl" ] && [ "$f" -ge "$gate" ] || return 1
  SHF=$f; SHO=$o; SHL=$fl; return 0; }
# share_pick GATE DGATE FIX: (main loop, only when the strict pass found no GPU) the shared lane for the next job. A training
# job takes a GPU only at a look that is SHARE_WAIT to SHARE_STALE s after an earlier qualifying look at the same GPU, with
# no failed look between the two; a fixture job (dumps only) by the dump rule at once. Most free memory wins.
# SH1[g] = time in ms of that earlier look, taken when share_ok returned (not at the start of the pass). It is cleared by
# a failed look, and for all GPUs by the main loop at every pass that makes no shared look (HOLD, logger gone, MAXC full,
# a strict lane found) and at every start. An earlier look older than SHARE_STALE s does not count: the present look is
# then a first look again. Sets SHG (GPU or ''), SHARED (log text), SHSLEEP.
declare -A SH1=()
share_pick(){ local gate=$1 dgate=$2 fix=$3 c t p d bf=-1 pend=0; SHG=""; SHARED=""; SHSLEEP=$POLL
  for c in $GPUS; do
    if [ "$fix" = 1 ]; then share_ok $c dump $dgate || continue
      [ "$SHF" -gt "$bf" ] && { bf=$SHF; SHG=$c; SHARED="beside $SHO; free $SHF MiB >= SHARE_DUMP $SHL"; }
    elif share_ok $c train $gate; then t=$(date +%s%3N); p=${SH1[$c]:-}; d=$(( (t - ${p:-0}) / 1000 ))
      [ -n "$p" ] && [ $d -gt $SHARE_STALE ] && { lg "lane GPU $c: shared candidate, the earlier look is $d s old (more than $SHARE_STALE s): it does not count"; p=""; }
      if [ -z "$p" ]; then SH1[$c]=$t; pend=1; lg "lane GPU $c: shared candidate, first look (free $SHF MiB >= SHARE_TRAIN $SHL; beside $SHO)"
      elif [ $d -lt $SHARE_WAIT ]; then pend=1
      elif [ "$SHF" -gt "$bf" ]; then bf=$SHF; SHG=$c; SHARED="beside $SHO; free $SHF MiB >= SHARE_TRAIN $SHL at two looks $d s apart"; fi
    else [ -z "${SH1[$c]:-}" ] || lg "lane GPU $c: shared candidate lost"; SH1[$c]=""; fi
  done
  [ -n "$SHG" ] && return 0
  [ $pend = 1 ] && SHSLEEP=$SHARE_WAIT; return 1; }

# ---- arming
[ "$(md5sum < $J | cut -c1-32)" = "$JOBS_MD5" ] || fail "jobs md5 FAIL"
deploy_ok || fail "deploy check FAIL (REVISION != $DEPLOY, or CODE.md5 of B or of QC $QC)"
[ "$(md5sum < $DATA/DEPLOY.md5 | cut -c1-32)" = "$DATA_MD5" ] || fail "DATA/DEPLOY.md5 md5 != DATA_MD5"
(cd $DATA && md5sum -c --quiet DEPLOY.md5 > /dev/null 2>&1) || fail "DATA DEPLOY.md5 check FAIL"
(cd $DATA/roots && md5sum -c --quiet ROOTS_cv5v2_v11.md5 ROOTS_cv5v2_v1.md5 > /dev/null 2>&1) || fail "ROOTS_cv5v2_*.md5 check FAIL"
if grep -q "|$DATA_V3/roots/cv5v3_" $J; then (cd $DATA_V3/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 > /dev/null 2>&1) || fail "ROOTS_cv5v3_v11.md5 check FAIL"; fi
[ "$(LPG)" = "$(cat $Q/LPG 2>/dev/null || echo 2)" ] || fail "LPG must be 1 or 2"
mapfile -t JOBS < $J
declare -A TCMD=() DCMD=(); R2=()
for j in "${JOBS[@]}"; do
  IFS='|' read -r name card seed root fold gate dgate logp extra ro <<< "$j"
  [ -n "$name" ] && [ -n "$card" ] && [ -n "$dgate" ] || fail "bad job line: $j"
  for v in "$seed" "$fold" "$gate" "$dgate"; do case "$v" in ''|*[!0-9]*) fail "$name: '$v' not a number";; esac; done
  case "$logp" in 0|1) ;; *) fail "$name: logp must be 0 or 1";; esac
  case "$root" in $DATA/roots/cv5v2_*_f$fold) set=cv5v2_f$fold;; $DATA_V3/roots/cv5v3_v11_f$fold) set=cv5v3_f$fold;;
    *) fail "$name: root $root is not DATA/roots/cv5v2_*_f$fold or DATA_V3/roots/cv5v3_v11_f$fold";; esac
  (cd $root && md5sum -c --quiet SPLITS.md5 > /dev/null 2>&1 && md5sum -c --quiet DATA_MANIFEST.md5 > /dev/null 2>&1) || fail "$name: $root SPLITS / DATA_MANIFEST check FAIL"
  cmp -s $root/splits/val.txt $root/splits/test.txt || fail "$name: $root test.txt != val.txt"
  cards_py validate $card > /dev/null || fail "$name: card $card invalid"
  cv=$QC/bench/methods_cv02/$(basename $card)
  W=$(cd $B && $P $HERE/cvcard.py $card $cv) || fail "$name: $cv: $W"
  while read -r m f; do [ -n "$m" ] || continue; [ "$(md5sum < $f | cut -c1-32)" = "$m" ] || fail "$name: weights $f md5 != card"; done <<< "$W"
  cg=$(yget $card memory.gate_mib); [ "$cg" != None ] && [ "$gate" -ge "$cg" ] || fail "$name: gate $gate < card gate $cg"
  case "$extra" in '') ;; --exit_after_step\ [0-9]*) case "$name" in smoke_*) ;; *) fail "$name: extra only for smoke_* jobs";; esac;;
    --fixture) case "$name" in dumptest_*) ;; *) fail "$name: --fixture only for dumptest_* jobs";; esac
      [ -s $B/experiments/$name/config_used.yaml ] && [ -s $B/experiments/$name/checkpoints/latest.pth ] || fail "$name: fixture run dir incomplete";;
    *) fail "$name: extra '$extra' not allowed";; esac
  if [ -n "$ro" ]; then   # further readouts (10th field): keys of the card's readouts, not its weights_key, each once
    case "$extra" in ''|--fixture) ;; *) fail "$name: readouts not allowed with extra '$extra'";; esac
    pk=$(yget $card weights_key); rl=$(yget $card readouts 2>/dev/null); seen=" $pk "
    for k in ${ro//,/ }; do
      case "$k" in *[!a-z0-9_]*|[!a-z]*) fail "$name: bad readout key '$k'";; esac
      case "$seen" in *" $k "*) fail "$name: readout '$k' is the card's weights_key or is listed twice";; esac
      case "$rl" in *"'weights_key': '$k'"*) ;; *) fail "$name: readout '$k' is not in the card's readouts";; esac
      seen="$seen$k "; done
    [ "$seen" != " $pk " ] || fail "$name: readouts field '$ro' names no key"
  fi
  cfgf=$(yget $card config); method=$(yget $card name)
  [ "$extra" = --fixture ] && x="" || x=$extra
  TCMD[$name]="$P -u scripts/train.py ${x:+$x }--config $cfgf --opts $(cards_py opts $card --seed $seed --run-name $name --data-root $root)"
  DCMD[$name]="$P -u scripts/bench_infer.py --run $B/experiments/$name --set $set --dumps $DUMPS --method $method --card $card --run-id $name --device cuda --precision fp32 --threads 4 --workers 4 --batch 8$([ $logp = 1 ] && echo ' --logp') --forbidden $DATA/meta/forbidden_v1.txt --bench-run dump_$name"
  has_token "${TCMD[$name]}" "$name" && has_token "${DCMD[$name]}" "dump_$name" || fail "$name: token missing in a command"
  for k in ${ro//,/ }; do d2=$(dcmd2 "${DCMD[$name]}" $name $k)
    has_token "$d2" "dump_$name.$k" && case "$d2" in *" --run-id $name.$k --weights-key $k "*) true;; *) false;; esac || fail "$name: readout $k: dump command not formed"
    R2+=("dump_$name.$k|$d2"); done
done
{ for n in "${!TCMD[@]}"; do echo "$n|${TCMD[$n]}"; echo "dump_$n|${DCMD[$n]}"; done; [ ${#R2[@]} = 0 ] || printf '%s\n' "${R2[@]}"; } | sort > $Q/jobs_rendered.txt
logger_ok || fail "gpumem logger (cq_gpumem.sh) not running"
lg "cv02 q armed: ${#JOBS[@]} jobs (md5 $JOBS_MD5), rendered $(md5sum < $Q/jobs_rendered.txt | cut -c1-8), deploy $DEPLOY (CODE.md5 OK), data $DATA_MD5 (OK), roots OK, GPUS '$GPUS', LPG $(LPG), MAXC $(cat $Q/MAXC 2>/dev/null || echo 16), other-user max $OTHER_MAX MiB, gap $GAPSEC s, lib $(md5sum < $B/bench/q/bench_lib.sh | cut -c1-8), cq $(md5sum < $0 | cut -c1-8), gpumem $(cat $Q/gpumem.pid), pid $$; nproc $(nproc), loadavg $(cut -d' ' -f1-3 /proc/loadavg)$([ "$QC" = "$B" ] || echo "; queue code QC $QC ($(cut -c1-7 $QC/REVISION 2>/dev/null), CODE.md5 OK)"); sharing (live files in $Q; 0 = off): SHARE_TRAIN $(share_floor SHARE_TRAIN $SHARE_TRAIN_MIN) MiB, SHARE_DUMP $(share_floor SHARE_DUMP $SHARE_DUMP_MIN) MiB"

# start_py NAME GPU STDOUT CMD: python as a plain background child of a subshell, so pids/NAME.pid = the python PID;
# the subshell waits, writes pids/NAME.rc, then exits. Waits <= 20 s for a cmdline with NAME's token -> pids/NAME.cmdline.
# Sets SPID (python PID or '') and SSUB (subshell PID).
start_py(){ local n=$1 g=$2 out=$3 cmd=$4 t=0 pp
  ( cd $B || exit 1; set -f; export CUDA_VISIBLE_DEVICES=$g HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
    $cmd > $out 2>&1 &
    pp=$!; echo $pp > $Q/pids/$n.pid
    wait $pp; rc=$?; echo $rc > $Q/pids/$n.rc ) &
  SSUB=$!; SPID=""
  while [ $t -lt 20 ]; do pp=$(cat $Q/pids/$n.pid 2>/dev/null)
    [ -n "$pp" ] && has_token "$(cmdl $pp)" "$n" && { SPID=$pp; break; }; sleep 1; t=$((t+1)); done
  [ -n "$SPID" ] && cmdl $SPID > $Q/pids/$n.cmdline; }

# chain_after NAME GPU FOLD METHOD SSUB: (background) wait for training, then dump on the same GPU, slim, RUN.md5.
# Env RO (further readout keys, space list; may be empty) and PK (the card's weights_key; used only with RO).
chain_after(){ local n=$1 g=$2 sub=$5 rc d dn=dump_$1 w=0 lw="" drc dc k dok=1 SHD=""
  if [ "${FIX:-0}" = 1 ]; then rc=0; lg "fixture $n: no training (dump step dry test)"
  else
    while kill -0 $sub 2>/dev/null; do sleep 30; done
    rc=$(cat $Q/pids/$n.rc 2>/dev/null || echo none)
    lg "trained $n rc=$rc (GPU $g)"
    lg "done $n: final-step lines $(grep -c 'step 20000/20000' $B/experiments/$n.stdout), Traceback lines $(grep -c Traceback $B/experiments/$n.stdout)"
  fi
  if [ "$rc" != 0 ]; then lg "no dump for $n (training rc $rc)"; touch $Q/pids/$n.end; return; fi
  for dn in dump_$n $(for k in ${RO:-}; do echo dump_$n.$k; done); do   # the usual dump, then one per further readout
  [ $dn = dump_$n ] && dc=$DC || dc=$(dcmd2 "$DC" $n ${dn#dump_$n.}); lw=""
  while :; do
    if [ -e $Q/HOLD ]; then w="HOLD"
    elif ! logger_ok; then touch $Q/HOLD; w="gpumem logger gone; HOLD set"
    elif ! { lane_ok $g $DG 1 && SHD=""; } && ! { share_ok $g dump $DG && SHD="beside $SHO; free $SHF MiB >= SHARE_DUMP $SHL"; }; then w="GPU $g does not qualify"
    elif ! gap_take; then w=""; sleep 10; continue
    elif [ -e $Q/HOLD ]; then w="HOLD"
    else break; fi
    [ "$w" != "$lw" ] && lg "dump $dn waits: $w"; lw=$w; sleep $POLL
  done
  deploy_ok || { lg "deploy check FAIL before $dn; HOLD set"; touch $Q/HOLD; touch $Q/pids/$n.end; return; }
  [ -z "$SHD" ] || lg "SHARED dump $dn on GPU $g: $SHD"
  lg "start $dn on GPU $g (free $(gfree $g) MiB, dump gate $DG)"
  start_py $dn $g $Q/dlogs/$dn.stdout "$dc"; d=$SPID
  if [ -z "$d" ]; then lg "no cmdline with $dn's token within 20 s (pid file $(cat $Q/pids/$dn.pid 2>/dev/null)); HOLD set"; touch $Q/HOLD $Q/pids/$n.end; return; fi
  lg "pid $dn $d (python; parent $(ps -o ppid= -p $d | tr -d ' ')); cmdline recorded ($(md5sum < $Q/pids/$dn.cmdline | cut -c1-8))"
  m=$(startcheck $Q/dlogs/$dn.stdout "BENCH_START: run=$dn" $LIVE_WAIT) || {
    lg "$dn $m; live check FAILED: HOLD + stop by verified PID"; touch $Q/HOLD; stop_verified $dn $d; lg "stop of $dn rc $?"; }
  [ -n "${m:-}" ] && case "$m" in "startup line OK"*) lg "$dn $m";; esac
  while kill -0 $SSUB 2>/dev/null; do sleep 10; done
  drc=$(cat $Q/pids/$dn.rc 2>/dev/null || echo none)
  lg "dumped $dn rc=$drc: 'dumped' lines $(grep -c '^dumped ' $Q/dlogs/$dn.stdout), Traceback lines $(grep -c Traceback $Q/dlogs/$dn.stdout)"
  [ "$drc" = 0 ] && grep -q '^dumped ' $Q/dlogs/$dn.stdout || { dok=0; break; }
  done
  if [ $dok = 1 ]; then
    (cd $B && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $P $HERE/slim_ckpt.py --run experiments/$n${RO:+ --keys $PK,${RO// /,}} > $Q/dlogs/slim_$n.log 2>&1); rc=$?
    if [ $rc = 0 ]; then
      mkdir -p $B/runs/$n
      (cd $B && md5sum experiments/$n/checkpoints/latest.pth > runs/$n/LATEST.md5 \
        && { echo experiments/$n/config_used.yaml; echo experiments/$n/checkpoints/slim.pth; echo runs/$n/LATEST.md5
             if [ -n "${RO:-}" ] && [ -f experiments/$n/enc_probe.jsonl ]; then echo experiments/$n/enc_probe.jsonl; fi
             { find dumps -path "dumps/*/$METH/$n/*" -type f; for k in ${RO:-}; do find dumps -path "dumps/*/$METH/$n.$k/*" -type f; done; } | sort; } | xargs -d '\n' md5sum > runs/$n/RUN.md5.tmp \
        && mv runs/$n/RUN.md5.tmp runs/$n/RUN.md5); rc=$?
      lg "RUN.md5 $n rc=$rc: $(wc -l < $B/runs/$n/RUN.md5 2>/dev/null) files, md5 $(md5sum < $B/runs/$n/RUN.md5 2>/dev/null | cut -c1-8)"
    else lg "slim checkpoint FAILED for $n (rc $rc; dlogs/slim_$n.log); no RUN.md5"; fi
  fi
  touch $Q/pids/$n.end; }

LASTW=""
for j in "${JOBS[@]}"; do
  IFS='|' read -r name card seed root fold gate dgate logp extra ro <<< "$j"
  fix=0; [ "$extra" = --fixture ] && fix=1
  if [ $fix = 0 ] && { [ -e $B/experiments/$name ] || [ -e $B/experiments/$name.stdout ]; }; then lg "skip $name (exists)"; continue; fi
  if [ -e $Q/pids/$name.gpu ]; then lg "skip $name (already started by this queue dir)"; continue; fi
  while :; do
    if [ -e $Q/HOLD ]; then SH1=(); sleep $POLL; continue; fi          # SH1=(): a pass without a shared look ends every series of looks
    logger_ok || { SH1=(); touch $Q/HOLD; lg "cv02 q: gpumem logger gone; HOLD set"; continue; }
    [ "$(lanes_all)" -ge "$(cat $Q/MAXC 2>/dev/null || echo 16)" ] && { SH1=(); sleep 10; continue; }
    g=""; SHARED=""; for c in $GPUS; do lane_ok $c $gate && { g=$c; break; }; done
    if [ -n "$g" ]; then SH1=(); else share_pick $gate $dgate $fix && g=$SHG; fi   # a shared lane only when no GPU passes the strict rule
    if [ -z "$g" ]; then [ "$LASTW" != "$name" ] && lg "cv02 q: $name waits for a qualifying lane"; LASTW=$name; sleep ${SHSLEEP:-$POLL}; continue; fi
    gap_take || { sleep 10; continue; }
    [ -e $Q/HOLD ] && { lg "cv02 q: HOLD seen after the gap pass for $name; not starting"; continue; }
    deploy_ok || { lg "cv02 q: deploy check FAIL before $name; HOLD set"; touch $Q/HOLD; continue; }
    break
  done
  echo $g > $Q/pids/$name.gpu; SH1=()
  if [ -n "$SHARED" ]; then [ $fix = 1 ] && lg "SHARED lane (fixture) $name on GPU $g: $SHARED" || lg "SHARED start $name on GPU $g: $SHARED"; fi
  if [ $fix = 1 ]; then lg "fixture $name on GPU $g: training skipped"
    FIX=1 DG=$dgate DC="${DCMD[$name]}" RO="${ro//,/ }" PK=$([ -n "$ro" ] && yget $card weights_key) METH=$(yget $card name) chain_after $name $g $fold x 0 &
    echo "$name chain $!" >> $Q/pids/subshells.txt; continue; fi
  lg "start $name on GPU $g (card $card, seed $seed, root $root, gate $gate; free $(gfree $g) MiB; our lanes on GPU $(lanes_on $g), all $(lanes_all))"
  start_py $name $g $B/experiments/$name.stdout "${TCMD[$name]}"; pp=$SPID
  if [ -z "$pp" ]; then lg "cv02 q: no cmdline with $name's token within 20 s (pid file $(cat $Q/pids/$name.pid 2>/dev/null)); HOLD set"; touch $Q/HOLD $Q/pids/$name.end; continue; fi
  lg "pid $name $pp (python; parent $(ps -o ppid= -p $pp | tr -d ' ')); cmdline recorded ($(md5sum < $Q/pids/$name.cmdline | cut -c1-8)): $(psl $pp)"
  DG=$dgate DC="${DCMD[$name]}" RO="${ro//,/ }" PK=$([ -n "$ro" ] && yget $card weights_key) METH=$(yget $card name) chain_after $name $g $fold x $SSUB &
  echo "$name chain $!" >> $Q/pids/subshells.txt
  ok=1; c=$B/experiments/$name/config_used.yaml; t=0
  while [ ! -s $c ] && [ $t -lt $LIVE_WAIT ]; do sleep 5; t=$((t+5)); done
  if [ -s $c ]; then m=$(cards_py cfgcheck $card --config $c --seed $seed --run-name $name --data-root $root) || ok=0
  else m="no config_used.yaml after $LIVE_WAIT s"; ok=0; fi
  lg "$name $m"
  if [ $ok = 1 ]; then m=$(startcheck $B/experiments/$name.stdout "$(want_line $root)" $LIVE_WAIT) || ok=0; lg "$name $m"; fi
  if [ $ok = 0 ]; then lg "cv02 q: live check FAILED for $name: HOLD + stop by verified PID"; touch $Q/HOLD; stop_verified $name "$pp"; lg "cv02 q: stop of $name rc $?"; fi
done
lg "cv02 q: all jobs dispatched; waiting"
wait
NM=$(printf '%s\n' "${JOBS[@]}" | cut -d'|' -f1 | paste -sd'|')
lg "BENCH CV02 Q ALL DONE ($(grep -cE "trained ($NM) rc=0 " $L) trained rc 0, $(grep -cE "dumped dump_($NM) rc=0:" $L) dumped rc 0, $(ls $B/runs/*/RUN.md5 2>/dev/null | wc -l) RUN.md5 of ${#JOBS[@]} jobs; pid $$)"
