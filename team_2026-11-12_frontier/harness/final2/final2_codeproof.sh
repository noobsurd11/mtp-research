#!/bin/bash
# fin2 code proof (incident of 21 Nov 2026): F (821dfad) -> F2 (9967d59) changes only the eval / monitor path of training,
# the guard of the final BN re-estimate (in-sample monitor), the cv02 queue's resume kind, and tests. Read only on the repository; scratch under SCR (default: mktemp). Prints OK/FAIL
# per item and a final count. The experiments (missing smoke F vs F2, resume exactness, training path bit-equal F vs F2,
# held-out root unchanged) are final2_smoke.sh; this script reads their summary if SMOKE_OUT is given.
# Usage: [SCR=<new dir>] [SMOKE_OUT=<final2_smoke.sh output>] bash final2_codeproof.sh
set -u
F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834; F2=${F2_TEST:-9967d59abaab03cef83c1e3014840b2359ef45d7}   # F2_TEST, REPO_TEST: negative tests only
REPO=${REPO_TEST:-/home/noob/work/bench_wt_fin2}; P=/home/noob/work/el-fault-detection/.venv/bin/python
SCR=${SCR:-$(mktemp -d)}; [ -e $SCR/fa ] && { echo "REFUSED: $SCR/fa exists"; exit 1; }
nf=0; ok(){ echo "OK   $*"; }; bad(){ echo "FAIL $*"; nf=$((nf+1)); }
echo "fin2 code proof: $F -> $F2 ($(date '+%F %T'); script $(md5sum < $0 | cut -c1-8))"
# 1. paths
want="M bench/q/cv02/cq.sh|M bench/q/cv02/cq_setup.sh|M scripts/train.py|M src/trainers/weight_avg.py|A tests/test_bench_cq_resume.py|A tests/test_bench_pool_eval.py"
got=$(git -C $REPO diff --name-status $F $F2 | tr '\t' ' ' | paste -sd'|')
[ "$got" = "$want" ] && ok "(1) git diff F F2: exactly 6 paths (train.py, weight_avg.py, cq.sh, cq_setup.sh, 2 new tests)" || bad "(1) paths: $got"
[ "$(git -C $REPO diff --name-only $F $F2 -- src configs data bench/methods bench/methods_cv02 bench/*.py scripts/bench_infer.py bench/tta.py)" = src/trainers/weight_avg.py ] \
  && ok "(1) nothing under configs/ data/ bench/methods*/ bench/*.py, bench_infer.py, tta.py changed; under src/ only src/trainers/weight_avg.py (item 2b)" || bad "(1) a training / dump module changed"
# 2b. weight_avg.py: exactly the overlap guard of train_fold_loader (the final BN re-estimate), one condition added
mkdir -p $SCR && git -C $REPO diff -U0 $F $F2 -- src/trainers/weight_avg.py > $SCR/wavg.diff
$P - $SCR/wavg.diff <<'PY' && ok "(2b) src/trainers/weight_avg.py: only the train_fold_loader overlap guard ('if set(stems) & held:' -> the same with 'and not held <= set(stems)', + 2 comment lines); the loader itself unchanged" || bad "(2b) weight_avg.py diff is not the guard only"
import sys
L = open(sys.argv[1]).read().splitlines()
rem = [l[1:] for l in L if l.startswith("-") and not l.startswith("---")]
add = [l[1:] for l in L if l.startswith("+") and not l.startswith("+++")]
ok = rem == ["    if set(stems) & held:"]
ok &= [a for a in add if not a.strip().startswith("#")] == ["    if set(stems) & held and not held <= set(stems):"]
ok &= sum(a.strip().startswith("#") for a in add) == 2 and sum(l.startswith("@@") for l in L) == 1
sys.exit(0 if ok else 1)
PY
# 2. train.py: the diff is the eval block of build_benchmark_data only
git -C $REPO diff -U0 $F $F2 -- scripts/train.py > $SCR/train.diff 2>/dev/null || mkdir -p $SCR && git -C $REPO diff -U0 $F $F2 -- scripts/train.py > $SCR/train.diff
$P - $SCR/train.diff <<'PY' && ok "(2) scripts/train.py: removed = the 2 val / test DataLoader lines; added = the same 2 lines with ', ignore_value=ev_ign' + the ev_ign block (comments, one assignment, one refusal); all in build_benchmark_data after 'weak_eval ='" || bad "(2) train.py diff is not the eval block only"
import re, sys
L = open(sys.argv[1]).read().splitlines()
rem = [l[1:] for l in L if l.startswith("-") and not l.startswith("---")]
add = [l[1:] for l in L if l.startswith("+") and not l.startswith("+++")]
hunks = [l for l in L if l.startswith("@@")]
ok = len(rem) == 2 and all('"val_loader"' in r or '"test_loader"' in r for r in rem)
ok &= sorted(a for a in add if "_loader" in a) == sorted(r.replace("weak_eval)", "weak_eval, ignore_value=ev_ign)") for r in rem)
rest = [a for a in add if "_loader" not in a]
ok &= all(a.strip().startswith("#") or a.strip().startswith("ev_ign = ") or a.strip().startswith("if ev_ign not in (None, 255):")
          or a.strip().startswith("raise ValueError(f\"in-sample val / test") for a in rest)
ok &= sum(a.strip().startswith("ev_ign = ") for a in rest) == 1
print(f"   train.py diff: {len(hunks)} hunks, {len(rem)} removed, {len(add)} added lines")
sys.exit(0 if ok else 1)
PY
lo=$(git -C $REPO show $F2:scripts/train.py | grep -n "^def build_benchmark_data" | cut -d: -f1); hi=$(git -C $REPO show $F2:scripts/train.py | awk -v s=$lo 'NR > s && /^def /{print NR; exit}')
w=$(git -C $REPO show $F2:scripts/train.py | grep -n "weak_eval = get_weak_augmentation" | cut -d: -f1)
inr=$(git -C $REPO diff -U0 $F $F2 -- scripts/train.py | grep '^@@' | sed -E 's/.*\+([0-9]+)(,([0-9]+))?.*/\1 \3/' | awk -v a=$w -v b=$hi '{n=($2==""?1:$2); if ($1 < a || $1 + n - 1 >= b) bad=1} END{print bad+0}')
[ "$inr" = 0 ] && ok "(2) every changed train.py line lies after 'weak_eval =' (l.$w) and before the next def (l.$hi) of build_benchmark_data (l.$lo)" || bad "(2) a changed line outside the eval block"
# 3. deploy archive
for c in F F2; do mkdir -p $SCR/$c; git -C $REPO archive ${!c} | tar -x -C $SCR/$c; echo ${!c} > $SCR/$c/REVISION
  (cd $SCR/$c && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5); done
d=$(diff <(grep -v '  REVISION$' $SCR/F/CODE.md5) <(grep -v '  REVISION$' $SCR/F2/CODE.md5) | grep '^[<>]' | awk '{print $1 $3}' | LC_ALL=C sort | tr '\n' ' ')
[ "$d" = "<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <scripts/train.py <src/trainers/weight_avg.py >bench/q/cv02/cq.sh >bench/q/cv02/cq_setup.sh >scripts/train.py >src/trainers/weight_avg.py >tests/test_bench_cq_resume.py >tests/test_bench_pool_eval.py " ] \
  && ok "(3) deploy CODE.md5 F2 against F: only the 6 paths (+ REVISION); F2 CODE.md5 md5 $(md5sum < $SCR/F2/CODE.md5 | cut -c1-32) ($(grep -c . $SCR/F2/CODE.md5) lines; c3_deploy.sh F2 must print it)" || bad "(3) CODE.md5 diff: $d"
# 4. queue: lines without --resume render byte-equal to F's cq.sh; the resume kind; the eval path tests
ln -sfn /home/noob/work/el-fault-detection/data/labeled $SCR/F2/data/labeled
r=$(cd $SCR/F2 && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cq_resume.py tests/test_bench_pool_eval.py tests/test_bench_cq_final.py 2>&1 | tail -1)
case "$r" in *" passed"*) case "$r" in *failed*|*error*) bad "(4) $r";; *) ok "(4) queue and eval tests in the archive of F2: $r (byte-equal render of non-resume lines against F's cq.sh needs the git repo: run in the worktree)";; esac;; *) bad "(4) $r";; esac
r=$(cd $REPO && CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cq_resume.py -k byte_equal 2>&1 | tail -1)
case "$r" in "1 passed"*) ok "(4) lines without --resume render byte-equal to F's cq.sh (worktree test): $r";; *) bad "(4) byte-equal render: $r";; esac
# 5. experiments
if [ -n "${SMOKE_OUT:-}" ]; then   # final2_smoke.sh log: per-run rc lines and the ckcmp comparisons ('N allowed, 0 not allowed')
  $P - $SMOKE_OUT $F2 <<'PY' && ok "(5) final2_smoke.sh ($SMOKE_OUT): R1 (F) rc 1 with the 255 ValueError, R2 / R3 (F2) rc 0, R4 rc 3, R5 F and F2 rc 0, for each card; every comparison 0 not-allowed differences" || bad "(5) final2_smoke.sh result ($SMOKE_OUT)"
import re, sys
t = open(sys.argv[1]).read()
ok = f"F2 {sys.argv[2]}" in t and "final2_smoke end " in t
for card in ("combo", "pf"):
    for run, rc in (("R1", "1"), ("R2", "0"), ("R3", "0"), ("R4", "3")):
        ok &= re.search(rf"^== {run} \(F2?_{run}_{card}, .*\): rc {rc} in", t, re.M) is not None
ok &= re.search(r"^== R5F \(.*\): rc 0 in", t, re.M) is not None and re.search(r"^== R5F2 \(.*\): rc 0 in", t, re.M) is not None
ok &= t.count("mask values must be in 0..23") >= 2
cmp = re.findall(r"\((\d+) allowed, (\d+) not allowed\)", t)
ok &= len(cmp) == 8 and all(n == "0" for _, n in cmp)   # combo: R3 latest + metrics, R4; pf: the same; R5: latest + metrics
ok &= "models 12360" in t
sys.exit(0 if ok else 1)
PY
else echo "SKIP (5) experiments: give SMOKE_OUT=<final2_smoke.sh output>"; fi
echo "fin2 code proof: $nf FAIL"
exit $((nf > 0))
