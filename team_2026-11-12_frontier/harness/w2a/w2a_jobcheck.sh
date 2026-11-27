#!/bin/bash
# Read-only check of a prepared bench_q dir (the arming checks of bench_q.sh / bench_setup.sh, without arming anything):
# jobs md5, deploy (HEAD, tracked changes), per line: name token, gate number and >= card gate, root splits + SPLITS.md5,
# card validate + weights md5, rendered command, no existing experiments/<name>; dumps: --bench-run token, --run path in
# REPO/experiments, set = root fold, dump dir not existing. Prints one line per problem and a summary. Writes nothing.
# Usage: Q=... JOBS_MD5=... [DJOBS_MD5=...] DEPLOY=<sha> REPO=... bash w2a_jobcheck.sh
set -u
Q=${Q:?}; R=${REPO:?}; P=/home/noob/work/el-fault-detection/.venv/bin/python; bad=0
no(){ echo "PROBLEM: $*"; bad=$((bad+1)); }
[ "$(md5sum < $Q/jobs.txt | cut -c1-32)" = "${JOBS_MD5:?}" ] || no "jobs md5"
[ -e $Q/dump/jobs.txt ] && { [ "$(md5sum < $Q/dump/jobs.txt | cut -c1-32)" = "${DJOBS_MD5:?}" ] || no "dump jobs md5"; }
[ "$(git -C $R rev-parse HEAD)" = "${DEPLOY:?}" ] || no "HEAD $(git -C $R rev-parse HEAD) != $DEPLOY"
[ -z "$(git -C $R status --short --untracked-files=no)" ] || no "tracked changes in $R"
for f in queue.pid gpumem.pid guard.pid HOLD pids launch.log chain.log; do [ -e $Q/$f ] && no "$Q/$f exists"; [ -e $Q/dump/$f ] && no "$Q/dump/$f exists"; done
declare -A CG=()
n=0
while IFS='|' read -r name card seed root gate cmd extra; do
  n=$((n+1))
  case "$gate" in ''|*[!0-9]*) no "$name gate '$gate'"; continue;; esac
  [ -s $root/splits/train.txt ] && [ -s $root/splits/val.txt ] && [ -s $root/splits/test.txt ] || no "$name root $root splits"
  (cd $root && md5sum -c --quiet SPLITS.md5) || no "$name SPLITS.md5"
  [ -e $R/experiments/$name ] || [ -e $R/experiments/$name.stdout ] && no "$name experiments exists"
  if [ "$card" != - ]; then
    if [ -z "${CG[$card]:-}" ]; then
      (cd $R && $P -m bench.cards validate $card > /dev/null) || no "$card invalid"
      CG[$card]=$(cd $R && $P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["memory"]["gate_mib"])' $card)
      while read -r m f; do [ "$(md5sum < $f | cut -c1-32)" = "$m" ] || no "$card weights $f md5"; done < <(cd $R && $P -c 'import sys, yaml; [print(w["md5"], w["path"]) for w in yaml.safe_load(open(sys.argv[1]))["weights"] or []]' $card)
    fi
    [ "${CG[$card]}" = None ] && case "$name" in smoke_*) ;; *) no "$name card gate null";; esac
    [ "${CG[$card]}" != None ] && [ "$gate" -lt "${CG[$card]}" ] && no "$name gate $gate < card ${CG[$card]}"
    o=$(cd $R && $P -m bench.cards opts $card --seed $seed --run-name $name --data-root $root) || no "$name opts"
    case " $o " in *" run_name=$name "*) ;; *) no "$name rendered opts lack run_name=$name";; esac
    case " $o " in *" seed=$seed "*) ;; *) no "$name rendered opts lack seed=$seed";; esac
    case " $o " in *" data.root=$root "*) ;; *) no "$name rendered opts lack data.root=$root";; esac
  fi
done < $Q/jobs.txt
echo "training lines: $n; cards: ${!CG[*]}"
if [ -e $Q/dump/jobs.txt ]; then m=0
  while IFS='|' read -r name card seed root gate cmd extra; do m=$((m+1))
    case " $cmd " in *" --bench-run $name "*) ;; *) no "$name lacks --bench-run token";; esac
    run=$(echo " $cmd " | grep -o ' --run [^ ]*' | cut -d' ' -f3); set_=$(echo " $cmd " | grep -o ' --set [^ ]*' | cut -d' ' -f3)
    rid=$(echo " $cmd " | grep -o ' --run-id [^ ]*' | cut -d' ' -f3); meth=$(echo " $cmd " | grep -o ' --method [^ ]*' | cut -d' ' -f3)
    case "$run" in $R/experiments/*) ;; *) no "$name --run $run not in $R/experiments";; esac
    grep -q "^$(basename $run)|" $Q/jobs.txt || no "$name dumps a run not in jobs.txt"
    [ "$set_" = "cv5v2_f${root##*_f}" ] || no "$name set $set_ vs root $root"
    case " $cmd " in *" --logp "*) no "$name has --logp";; esac
    [ -e /home/noob/work/bench_dumps/w2a/elbench1/$meth/$rid ] && no "$name dump dir exists"
    [ "$gate" -ge 6200 ] || no "$name dump gate $gate"
  done < $Q/dump/jobs.txt
  echo "dump lines: $m"
fi
echo "names unique: $(cut -d'|' -f1 $Q/jobs.txt $( [ -e $Q/dump/jobs.txt ] && echo $Q/dump/jobs.txt) | sort | uniq -d | wc -l) duplicates"
echo "MAXC $(cat $Q/MAXC)$( [ -e $Q/dump/MAXC ] && echo ", dump MAXC $(cat $Q/dump/MAXC)")"
echo "JOBCHECK $([ $bad = 0 ] && echo PASS || echo "FAIL ($bad problems)")"
