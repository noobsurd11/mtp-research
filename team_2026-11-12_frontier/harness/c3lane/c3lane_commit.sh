#!/bin/bash
# c3lane: put c3lane.patch on top of 5437778 as ONE commit on branch bench_c3s, in the existing worktree
# /home/noob/work/bench_wt_c3s (run by the lead or an integrator on gaint, only after the review). No push. Nothing on cv02
# uses that worktree (the queues run from deploy dirs; the relays from bench_c3_io/stage). Then deploy the commit with the
# reviewed deploy script:  bash harness/c3base/c3_deploy.sh <new commit>  -> cv02 /tmp/noob_el/bench_<7 hex> = the new QC.
# Refuses: patch md5 differs; the worktree is not on bench_c3s at 5437778 or has a tracked change or the new file; the patched
# files differ from the pinned md5s; a queue test fails. A run that fails AFTER the patch was applied leaves two files
# changed in the worktree; undo by hand, then run again:
#   git -C /home/noob/work/bench_wt_c3s checkout -- bench/q/cv02/cq.sh ; rm /home/noob/work/bench_wt_c3s/bench/q/cv02/cq_rescue.sh
set -u
# WT, BASE can be set from outside only for a test on a scratch repository.
WT=${WT:-/home/noob/work/bench_wt_c3s}; BASE=${BASE:-543777834e5c32896d817b1f3e719bd515f8e6f7}; BR=bench_c3s
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); PF=$HERE/c3lane.patch
P=/home/noob/work/el-fault-detection/.venv/bin/python
PATCH_MD5=${PATCH_MD5:?md5 of the reviewed c3lane.patch (from the review)}
no(){ echo "REFUSED: $*"; exit 1; }
[ "$(md5sum < $PF | cut -c1-32)" = "$PATCH_MD5" ] || no "patch md5 is not $PATCH_MD5"
cd $WT || exit 1
[ "$(git rev-parse HEAD)" = "$BASE" ] && [ "$(git rev-parse --abbrev-ref HEAD)" = $BR ] || no "$WT is not on $BR at $BASE"
[ "$(git status --porcelain -uno | wc -l)" = 0 ] && [ ! -e bench/q/cv02/cq_rescue.sh ] || no "tracked changes in $WT, or cq_rescue.sh exists"
git apply --check $PF && git apply $PF || no "patch does not apply"
echo "14d33b80b17b116ec68941f1b40c5951  bench/q/cv02/cq.sh
204f9bce070e695df63de779becce287  bench/q/cv02/cq_rescue.sh" | md5sum -c --quiet - || no "patched files differ from the pinned md5s"
[ "$(git status --porcelain | grep -c .)" = 2 ] || no "expected exactly 2 changed or new files: $(git status --porcelain | tr '\n' ' ')"
bash -n bench/q/cv02/cq.sh && bash -n bench/q/cv02/cq_rescue.sh || no "syntax"
CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cq_readouts.py tests/test_bench_cq_cv5v3.py | tail -1 | tee /dev/stderr | grep -q "^20 passed" || no "queue tests did not give '20 passed'"
git add bench/q/cv02/cq.sh bench/q/cv02/cq_rescue.sh
git commit -q -m "cv02 queue: lane rule v2 (shared GPUs by live floors SHARE_TRAIN / SHARE_DUMP), cq_rescue.sh for waiting dumps

c3lane (harness/c3lane/c3lane.patch; user's decision of 17 Nov 2026): when no GPU passes the strict lane rule, a
training run may start beside another user if at least SHARE_TRAIN MiB (floor 20480) are free at two looks 30 s apart
and no owner above the threshold is our own login, unknown, or unreadable; a dump may run beside another user if at
least SHARE_DUMP MiB (floor 10240) are free. The floors are read live from files in the queue dir; without them the
strict rule alone holds, as before. cq_rescue.sh runs the waiting dump of a finished run of an older queue under the
shared-dump rule, in that queue's own form. No training, dump, card or read code is changed.

Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>" || no "commit failed"
C=$(git rev-parse HEAD)
echo "commit $C on branch $BR in $WT (parent $(git rev-parse HEAD^)); files: $(git diff --name-status HEAD^ HEAD | tr '\n' ' ')"
echo "next: bash $HERE/../c3base/c3_deploy.sh $C"
