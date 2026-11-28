#!/bin/bash
# x4 integrator (gaint, CPU only, nice 19). Merges one builder's handed-over commit into bench_x4 and proves keys-off identity.
# Usage: bash x4_integrate.sh ref                      once: COMBO 5-step CPU record at 03375d4 (the commit that trained COMBO)
#        bash x4_integrate.sh merge <id> <commit> <card>[,<card>...]   (run in tmux bench_x4_int_<id>; log OUT/<id>/run.log)
# merge: (1) bench_wt_x4 must be clean; git merge --no-ff <commit> (refused on conflict: merge aborted, nothing changed).
#  (2) keys-off identity: identity_cpu.py (962379a6) 5 steps, COMBO card opts (seed 5, cv5v3 f0), merged tree vs the 03375d4
#      record, compare_id.py: must print IDENTICAL; otherwise the merge is undone (git reset --hard to the previous HEAD of
#      bench_x4, our own branch) and the arm is REFUSED.
#  (3) each named card: bench.cards validate, cvcard.py vs its cv02 variant, bench.cards diff vs the COMBO card (printed).
#  (4) pytest -q of the tests the merge added or changed, plus tests/test_bench_c3x_card.py.
#  (5) code class: if the merge touches scripts/train.py, src/ (trainer, models, losses, data) or configs/, the line
#      "GPU 1000-step identity owed" is printed (the cv02 check of the integrator's step 4 is then run before the arm's jobs).
# Nothing is deployed here; after INTEGRATED: c3_deploy.sh <new HEAD>.
set -u
WT=/home/noob/work/bench_wt_x4; IO=/home/noob/work/bench_x4_int; REFC=03375d4c5e9ddde040603230eaca2b1c1139e14c
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
R0=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0; COMBO=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=12 MKL_NUM_THREADS=12 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
[ "$(md5sum < $ID | cut -c1-8)" = 962379a6 ] || { echo "identity_cpu.py is not 962379a6"; exit 1; }
mkdir -p $IO
opts(){ (cd $1 && $P -m bench.cards opts $COMBO --seed 5 --run-name x --data-root $R0) | tr ' ' '\n' | grep -v '^run_name=' | tr '\n' ' '; }
case "${1:-}" in
ref)
  RT=$IO/tree_${REFC:0:7}; [ -e $IO/COMBO_ref.json ] && { echo "exists: $IO/COMBO_ref.json"; exit 0; }
  [ -d $RT ] || { mkdir -p $RT && git -C $WT archive $REFC | tar -x -C $RT; }
  nice -n 19 $P $ID --code $RT --out $IO/COMBO_ref.json --steps 5 --threads 12 --opts $(opts $RT) > $IO/COMBO_ref.log 2>&1
  echo "[$(date '+%F %T')] ref rc=$? ($IO/COMBO_ref.json, tree $RT)";;
merge)
  id=${2:?id}; C=${3:?commit}; CARDS=${4:?cards}; O=$IO/$id/$(date +%H%M%S); mkdir -p $O; L=$O/run.log
  say(){ echo "[$(date '+%F %T')] $*" | tee -a $L; }
  [ -s $IO/COMBO_ref.json ] || { say "no reference record; run: x4_integrate.sh ref"; exit 1; }
  cd $WT || exit 1
  [ -z "$(git status --porcelain -uno)" ] || { say "REFUSED: $WT has tracked changes"; exit 1; }
  PRE=$(git rev-parse HEAD); C=$(git rev-parse --verify "$C^{commit}") || { say "REFUSED: unknown commit $3"; exit 1; }
  say "merge $id $C into bench_x4 $PRE"
  if ! git merge --no-ff -q -m "x4 integrate $id: merge ${C:0:7} ($CARDS)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" $C >> $L 2>&1; then git merge --abort 2>/dev/null; say "REFUSED $id: merge conflict (merge aborted; bench_x4 stays $PRE)"; exit 1; fi
  NEW=$(git rev-parse HEAD); say "merged: $NEW; changed paths: $(git diff --name-only $PRE $NEW | tr '\n' ' ')"
  undo(){ git reset -q --hard $PRE && say "bench_x4 reset to $PRE (merge undone)"; }
  nice -n 19 $P $ID --code $WT --out $O/COMBO_new.json --steps 5 --threads 12 --opts $(opts $WT) > $O/COMBO_new.log 2>&1; r=$?
  c=$($P $CMP $IO/COMBO_ref.json $O/COMBO_new.json 2>&1); say "identity keys off (COMBO card, 5 CPU steps, ${REFC:0:7} vs merged) rc=$r: $c"
  case "$c" in IDENTICAL*) ;; *) say "REFUSED $id: keys-off identity is not IDENTICAL"; undo; exit 1;; esac
  bad=0
  for cd in ${CARDS//,/ }; do f=bench/methods/$cd.yaml
    v=$($P -m bench.cards validate $f 2>&1 | tail -1); w=$($P bench/q/cv02/cvcard.py $f bench/methods_cv02/$cd.yaml 2>&1); wr=$?
    d=$($P -m bench.cards diff $COMBO $f 2>&1 | tr -d '\n ')
    say "card $cd: validate '$v'; cvcard rc $wr; diff vs COMBO $d"
    case "$v" in OK*) ;; *) bad=1;; esac; [ $wr = 0 ] || bad=1; done
  T=$(git diff --name-only $PRE $NEW -- 'tests/*.py' | tr '\n' ' ')
  nice -n 19 $P -m pytest -q -p no:cacheprovider $T tests/test_bench_c3x_card.py > $O/pytest.log 2>&1; r=$?
  say "pytest ($T tests/test_bench_c3x_card.py) rc=$r: $(tail -1 $O/pytest.log)"; [ $r = 0 ] || bad=1
  [ $bad = 0 ] || { say "REFUSED $id: card or test check failed"; undo; exit 1; }
  if git diff --name-only $PRE $NEW | grep -qE '^(scripts/train\.py|src/|configs/)'; then say "code class: trainer/model/data code changed: GPU 1000-step identity owed"; else say "code class: no trainer/model/data change"; fi
  say "INTEGRATED $id: bench_x4 $NEW (deploy next: c3_deploy.sh $NEW)";;
*) sed -n 2,14p "$0"; exit 1;;
esac
