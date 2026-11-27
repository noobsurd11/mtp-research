#!/bin/bash
# c3x: put c3x.patch on top of 852ed5c as ONE commit on branch bench_c3s, in the existing worktree /home/noob/work/bench_wt_c3s
# (run by the LEAD on gaint, only after the review) = harness/c3lane/c3lane_commit.sh (51beca9c) with the base, the patch,
# the pinned files, the test list and the message changed. No push. The commit adds three files only: the card
# bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml, its cv02 variant bench/methods_cv02/<same name> and
# tests/test_bench_c3x_card.py (ruling C3). Next steps (request section 4): the gaint smokes from this worktree, then the
# deploy with the reviewed script:  bash harness/c3base/c3_deploy.sh <new commit>  -> cv02 /tmp/noob_el/bench_<7 hex> = B and
# QC of the c3x queue.
# Refuses: patch md5 differs; the worktree is not on bench_c3s at 852ed5c, has a tracked change, or holds one of the three
# files; the patched files differ from the pinned md5s; the tests do not give '27 passed' (7 card tests + the 20 queue
# tests of c3swad / c3lane). A run that fails AFTER the patch was applied leaves the three new files (untracked, or staged
# if `git commit` itself failed after `git add`, e.g. without a git identity); unstage first, then remove them, then run again:
#   git -C /home/noob/work/bench_wt_c3s reset -q -- bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml \
#      bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml tests/test_bench_c3x_card.py
#   rm /home/noob/work/bench_wt_c3s/bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml \
#      /home/noob/work/bench_wt_c3s/bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml \
#      /home/noob/work/bench_wt_c3s/tests/test_bench_c3x_card.py
set -u
# WT, BASE can be set from outside only for a test on a scratch repository.
WT=${WT:-/home/noob/work/bench_wt_c3s}; BASE=${BASE:-852ed5c411b967d7ea758ef2cd5dbe70ae4e50a1}; BR=bench_c3s
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); PF=$HERE/c3x.patch
P=/home/noob/work/el-fault-detection/.venv/bin/python
PATCH_MD5=${PATCH_MD5:?md5 of the reviewed c3x.patch (from the review)}
F1=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml; F2=bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
F3=tests/test_bench_c3x_card.py
no(){ echo "REFUSED: $*"; exit 1; }
[ "$(md5sum < $PF | cut -c1-32)" = "$PATCH_MD5" ] || no "patch md5 is not $PATCH_MD5"
cd $WT || exit 1
[ "$(git rev-parse HEAD)" = "$BASE" ] && [ "$(git rev-parse --abbrev-ref HEAD)" = $BR ] || no "$WT is not on $BR at $BASE"
[ "$(git status --porcelain -uno | wc -l)" = 0 ] && [ ! -e $F1 ] && [ ! -e $F2 ] && [ ! -e $F3 ] || no "tracked changes in $WT, or one of the three files exists"
git apply --check $PF && git apply $PF || no "patch does not apply"
echo "98f152de3ea7f8c88e892162e07b4450  $F1
d7b207089f6cfeb484ca9ef96f734786  $F2
501a6f95f90a3186401814f769eadf89  $F3" | md5sum -c --quiet - || no "patched files differ from the pinned md5s"
[ "$(git status --porcelain -- bench tests | grep -c .)" = 3 ] || no "expected exactly 3 new files under bench/ and tests/: $(git status --porcelain -- bench tests | tr '\n' ' ')"
CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 nice -n 19 $P -m pytest -q -p no:cacheprovider $F3 tests/test_bench_cq_readouts.py tests/test_bench_cq_cv5v3.py | tail -1 | tee /dev/stderr | grep -q "^27 passed" || no "tests did not give '27 passed'"
git add $F1 $F2 $F3
git commit -q -m "c3x: card hrnet_w18_unetpp_swad_const_pf_v11 (HRNet-W18 U-Net++ + swad_const), its cv02 variant, card test

c3x (lead's rulings C1 to C6 of 17 Nov 2026; harness/c3x/c3x.patch): the card is hrnet_w18_unetpp_pf_v11 with exactly
the changes that swad_const_pf_v11 makes to house_r34_unetpp_pf_v11: 8 opts (constant lr after warm-up, uniform average
of steps 10,000 to 20,000, EMA 0.9998, BN re-estimate at the end, encoder probe every 2,000 steps), weights_key swad_bn
and the 6 readouts. tests/test_bench_c3x_card.py proves that the two card diffs are equal and that the rendered config
differs from an HRNet run's only in those 8 keys. The cv02 variant differs in the weights path only. No training, dump,
queue or read code is changed.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || no "commit failed"
C=$(git rev-parse HEAD)
echo "commit $C on branch $BR in $WT (parent $(git rev-parse HEAD^)); files: $(git diff --name-status HEAD^ HEAD | tr '\n' ' ')"
echo "next: the gaint smokes (request section 4 step 3), then: bash $HERE/../c3base/c3_deploy.sh $C"
