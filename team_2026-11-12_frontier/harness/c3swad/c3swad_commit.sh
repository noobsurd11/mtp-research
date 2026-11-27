#!/bin/bash
# c3swad: put cq_c3swad.patch on top of 89b9ea5 as ONE commit in a NEW worktree (run by the lead or an integrator on
# gaint, only after the review of the patch). bench_wt_final stays at 89b9ea5 and untouched (the running queues, the
# relays' stage copy and every cv5v3 read use it). No push. Then deploy the commit with the reviewed deploy script:
#   bash harness/c3base/c3_deploy.sh <new commit>   -> stage bench_c3_io/stage/bench_<7 hex>, cv02 /tmp/noob_el/bench_<7 hex>
# That dir is the QC of c3swad_handover.sh: only its bench/q/cv02 scripts and bench/methods_cv02 are used there;
# training and dumps keep running from /tmp/noob_el/bench_89b9ea5.
# Refuses: worktree dir or branch exists; patch md5 differs; the patched files differ from the pinned md5s; a test fails.
# A run that fails AFTER the worktree was added (patch does not apply, md5 pins, a test) leaves the worktree and the branch
# behind, and a second run then refuses. Both hold nothing but this script's own work. Clean up by hand, then run again:
#   git -C /home/noob/work/el_bench worktree remove --force /home/noob/work/bench_wt_c3s
#   git -C /home/noob/work/el_bench branch -D bench_c3s
set -u
# R, WT, BR, BASE can be set from outside only for a test on a scratch repository.
R=${R:-/home/noob/work/el_bench}; WT=${WT:-/home/noob/work/bench_wt_c3s}; BR=${BR:-bench_c3s}; BASE=${BASE:-89b9ea5a12a37a87c16c4868cc4adf00794a7610}
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); PF=$HERE/cq_c3swad.patch
P=/home/noob/work/el-fault-detection/.venv/bin/python
PATCH_MD5=${PATCH_MD5:?md5 of the reviewed cq_c3swad.patch (from the review)}
no(){ echo "REFUSED: $*"; exit 1; }
[ "$(md5sum < $PF | cut -c1-32)" = "$PATCH_MD5" ] || no "patch md5 is not $PATCH_MD5"
[ -e $WT ] && no "$WT exists"
git -C $R rev-parse --verify -q refs/heads/$BR > /dev/null && no "branch $BR exists"
git -C $R worktree add -b $BR $WT $BASE || no "worktree add failed"
cd $WT || exit 1
git apply --check $PF && git apply $PF || no "patch does not apply"
echo "5222150ba40130d41a04af4f7d17dbfa  bench/q/cv02/cq.sh
630b1307a5b3cc99da251cd6eecc8672  bench/q/cv02/cq_setup.sh
20712dd3af1e6b86720a9633b419de00  bench/q/cv02/slim_ckpt.py
618cea2f57864ac4a916da00845da9da  bench/methods_cv02/swad_const_pf_v11.yaml
0216a2cf5ea2b3d3e627d80fb196f22c  tests/test_bench_cq_readouts.py" | md5sum -c --quiet - || no "patched files differ from the pinned md5s"
[ "$(git status --porcelain | wc -l)" = 5 ] || no "expected exactly 5 changed or new files: $(git status --porcelain | tr '\n' ' ')"
CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P -m pytest -q -p no:cacheprovider tests/test_bench_cq_readouts.py tests/test_bench_cq_cv5v3.py | tail -1 | tee /dev/stderr | grep -q "^20 passed" || no "queue tests did not give '20 passed'"
git add bench/q/cv02/cq.sh bench/q/cv02/cq_setup.sh bench/q/cv02/slim_ckpt.py bench/methods_cv02/swad_const_pf_v11.yaml tests/test_bench_cq_readouts.py
git commit -q -m "cv02 queue: further readouts per job, queue code dir QC, slim --keys; cv02 variant of swad_const_pf_v11

c3swad (harness/c3swad/cq_c3swad.patch): a 10th jobs.txt field names further weights keys to dump after the usual
dump (run id <name>.<key>); the slim checkpoint then keeps the dumped keys and RUN.md5 lists the further dump dirs
and enc_probe.jsonl. QC lets the queue scripts and bench/methods_cv02 come from another deploy dir while training and
dumps run in B. A job line without the field, and a queue without QC, behave as before. No training, dump or read
code is changed.

Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>" || no "commit failed"
C=$(git rev-parse HEAD)
echo "commit $C on branch $BR in $WT (parent $(git rev-parse HEAD^)); files: $(git diff --name-status HEAD^ HEAD | tr '\n' ' ')"
echo "next: full pytest if wanted (cd $WT && $P -m pytest -q tests), then: bash $HERE/../c3base/c3_deploy.sh $C"
