#!/bin/bash
# w2b builder: read-only replica, for one prepared queue dir, of (a) bench_setup.sh's refusal checks (c57508e lines 15 to
# 27) with the env its launch.sh exports, and (b) bench_q.sh's arming checks (c57508e lines 50 to 76): card validate,
# weights md5 = card, job gate >= card gate (null only for smoke_*), data root splits (+ SPLITS.md5), extra only
# '--exit_after_step N' on smoke_* lines, dump commands carry '--bench-run <name>'; plus the rendered training command
# of every harness line (bench.cards opts). Starts nothing, writes nothing (stdout only).
# Usage: bash w2b_armcheck.sh <queue dir>      (pattern of the udev reviewer's rv_armcheck.sh)
set -u
Q0=${1:?queue dir}
eval "$(grep -E '^export |^  JOBS_MD5' $Q0/launch.sh | sed 's/\\$//' | tr '\n' ' ' | sed 's/^export //; s/^/export /')"
[ "$(readlink -f $Q0)" = "$(readlink -f $Q)" ] || echo "  note: launch.sh names Q=$Q, checked dir $Q0 (prepared copy); checks use $Q0"
Q=$Q0
R=${REPO:-/home/noob/work/el_bench}; DQ=$Q/dump; n=0; P=/home/noob/work/el-fault-detection/.venv/bin/python
no(){ echo "  WOULD REFUSE: $*"; n=$((n+1)); }
echo "$Q0: SES=$SES DEPLOY=${DEPLOY:0:7} JOBS_MD5=${JOBS_MD5:0:8} DJOBS_MD5=${DJOBS_MD5:-none} REPO=$R MAXH=$MAXH MAXC $(cat $Q/MAXC)$([ -e $DQ/MAXC ] && echo " dump MAXC $(cat $DQ/MAXC)")"
case "$SES" in bench_q_*) ;; *) no "session name";; esac
tmux has-session -t "=$SES" 2>/dev/null && no "tmux session $SES exists"
[ -s $Q/jobs.txt ] && [ -s $Q/MAXC ] || no "lacks jobs.txt or MAXC"
for d in $Q $DQ; do [ -d $d ] || continue
  for f in queue.pid gpumem.pid guard.pid HOLD pids; do [ -e $d/$f ] && no "$d/$f exists"; done
  for f in launch.log chain.log; do [ -s $d/$f ] && no "$d/$f not empty"; done; done
[ "$(md5sum < $Q/jobs.txt | cut -c1-32)" = "$JOBS_MD5" ] || no "jobs md5"
if [ -e $DQ/jobs.txt ]; then [ -s $DQ/MAXC ] || no "dump MAXC"; [ "$(md5sum < $DQ/jobs.txt | cut -c1-32)" = "${DJOBS_MD5:-}" ] || no "dump jobs md5"; fi
[ "$(git -C $R rev-parse HEAD)" = "$DEPLOY" ] || no "$R HEAD $(git -C $R rev-parse --short HEAD) != DEPLOY ${DEPLOY:0:7}"
[ -z "$(git -C $R status --short --untracked-files=no)" ] || no "tracked changes"
for x in $(cut -d'|' -f1 $Q/jobs.txt; [ -e $DQ/jobs.txt ] && cut -d'|' -f1 $DQ/jobs.txt); do
  { [ -e $R/experiments/$x ] || [ -e $R/experiments/$x.stdout ]; } && no "experiments/$x exists"; done
for J in $Q/jobs.txt $([ -e $DQ/jobs.txt ] && echo $DQ/jobs.txt); do
  while IFS='|' read -r name card seed root gate cmd extra; do
    [ -n "$name" ] && [ -n "$gate" ] || { no "bad line in $J"; continue; }
    case "$gate" in *[!0-9]*) no "$name gate";; esac
    [ -s $root/splits/train.txt ] && [ -s $root/splits/val.txt ] && [ -s $root/splits/test.txt ] || no "$name root splits"
    [ -e $root/SPLITS.md5 ] && { (cd $root && md5sum -c --quiet SPLITS.md5 >/dev/null 2>&1) || no "$name SPLITS.md5"; }
    if [ "$card" != - ]; then
      (cd $R && $P -m bench.cards validate $card >/dev/null) || no "$name card invalid"
      while read -r m f; do [ -n "$m" ] || continue; [ "$(md5sum < $f | cut -c1-32)" = "$m" ] || no "$name weights md5"; done < <(cd $R && $P -c 'import sys, yaml; [print(w["md5"], w["path"]) for w in yaml.safe_load(open(sys.argv[1]))["weights"] or []]' $card)
      cg=$(cd $R && $P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["memory"]["gate_mib"])' $card)
      if [ "$cg" = None ]; then case "$name" in smoke_*) ;; *) no "$name card gate null";; esac
      elif [ "$gate" -lt "$cg" ]; then no "$name gate $gate < card $cg"; fi
    fi
    if [ -z "$cmd" ]; then
      case "$extra" in ''|--exit_after_step\ [0-9]*) ;; *) no "$name extra '$extra'";; esac
      [ -z "$extra" ] || case "$name" in smoke_*) ;; *) no "$name extra on a non-smoke job";; esac
      o=$(cd $R && $P -m bench.cards opts $card --seed $seed --run-name $name --data-root $root) || no "$name opts"
      echo "  $name: train.py ${extra:+$extra }--opts ... ($(echo "$o" | wc -w) tokens, md5 $(echo "$o" | md5sum | cut -c1-8))"
    else
      case " $cmd " in *" --bench-run $name "*) ;; *) no "$name lacks --bench-run $name";; esac
    fi
  done < $J
done
[ $n = 0 ] && echo "  ARMCHECK PASS (bench_setup and bench_q's arming checks would pass)" || echo "  ARMCHECK: $n refusal(s)"
