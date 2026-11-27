#!/bin/bash
# c3x code-equality proof (ruling C3): every file that training or dumping can load is byte-equal between 89b9ea5 (the
# training, dump and read code of every cv5v3 run) and the c3x commit X, except the added card files. Read only; CPU; writes
# only into a new scratch dir OUT (default: mktemp under /tmp, removed at the end unless KEEP=1).
#   (1) git diff --name-status 89b9ea5 X lists exactly the 9 expected paths: the c3swad and c3lane queue changes already in
#       the deploys QC 5437778 / 852ed5c (bench/q/cv02/cq.sh, cq_setup.sh, slim_ckpt.py, cq_rescue.sh; the cv02 variant of
#       the swad card; one queue test) and the 3 files of the c3x commit (card, cv02 variant, card test). Everything else
#       of the tree, in particular scripts/, src/, configs/, data/, bench/*.py, bench/q/bench_lib.sh, is byte-equal.
#   (2) CODE.md5 of an archive of X (built the way c3_deploy.sh builds a deploy) against CODE.md5 of the 89b9ea5 stage copy
#       (= cv02 B's; compared when CV02=1): the differing paths are the same 9 plus REVISION.
#   (3) none of the 9 paths is under scripts/, src/, configs/ or is a Python module outside bench/q/cv02/ and tests/; no file
#       under scripts/, src/, bench/*.py names cq_ / slim_ckpt / methods_cv02 / test_bench_ (so training and dumping cannot
#       reach them); the dump reads bench/methods/<card>.yaml given on its command line: the added card.
#   (4) runtime trace: the repo files Python loads when scripts/train.py and scripts/bench_infer.py start (python -X importtime,
#       CPU, the archive of X; train.py with --help, bench_infer.py with arguments that fail after its imports): none of the 9.
# Usage: bash c3x_codeproof.sh <commit X>   (X must be in the el-fault-detection repo, e.g. after c3x_commit.sh)
set -u
RP=${REPO:-/home/noob/work/bench_wt_c3s}    # REPO: only for a test on a scratch clone
X=$(git -C $RP rev-parse --verify "${1:?commit}^{commit}") || exit 1
OLD=89b9ea5a12a37a87c16c4868cc4adf00794a7610; ST=/home/noob/work/bench_c3_io/stage/bench_89b9ea5
P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=${OUT:-$(mktemp -d /tmp/c3x_codeproof.XXXXXX)}; [ -z "$(ls -A $OUT 2>/dev/null)" ] || { echo "REFUSED: $OUT not empty"; exit 1; }
fails=0; ok(){ echo "OK   $*"; }; bad(){ echo "FAIL $*"; fails=$((fails+1)); }
echo "c3x code proof: 89b9ea5 -> $X ($(date '+%F %T'))"
WANT="A	bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
A	bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml
A	bench/methods_cv02/swad_const_pf_v11.yaml
M	bench/q/cv02/cq.sh
A	bench/q/cv02/cq_rescue.sh
M	bench/q/cv02/cq_setup.sh
M	bench/q/cv02/slim_ckpt.py
A	tests/test_bench_c3x_card.py
A	tests/test_bench_cq_readouts.py"
# (1)
GOT=$(git -C $RP diff --name-status $OLD $X)
[ "$GOT" = "$WANT" ] && ok "(1) git diff 89b9ea5 X: exactly the 9 expected paths" || { bad "(1) git diff 89b9ea5 X differs from the expected 9 paths:"; echo "$GOT"; }
git -C $RP diff --quiet $OLD $X -- scripts src configs data bench/cards.py bench/dumpfmt.py bench/sets.py \
  bench/w1read.py bench/crossfit_op.py bench/cellmeta.py bench/q/bench_lib.sh bench/methods/swad_const_pf_v11.yaml \
  bench/methods/hrnet_w18_unetpp_pf_v11.yaml bench/methods/house_r34_unetpp_pf_v11.yaml \
  && ok "(1) scripts/ src/ configs/ data/, the bench modules of training, dump and read, bench_lib.sh and the 3 source cards: byte-equal" \
  || bad "(1) a training, dump or read file differs"
echo "     $(git -C $RP ls-tree -r --name-only $X | wc -l) files in X; tree $(git -C $RP rev-parse $X^{tree})"
# (2)
mkdir -p $OUT/x && git -C $RP archive $X | tar -x -C $OUT/x && echo $X > $OUT/x/REVISION
(cd $OUT/x && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
(cd $ST && md5sum -c --quiet CODE.md5 > /dev/null 2>&1) || bad "(2) stage copy $ST: CODE.md5 check failed"
D=$(diff <(grep -v '  REVISION$' $ST/CODE.md5) <(grep -v '  REVISION$' $OUT/x/CODE.md5) | grep '^[<>]' | awk '{print $1 $3}' | LC_ALL=C sort | tr '\n' ' ')
DW="<bench/q/cv02/cq.sh <bench/q/cv02/cq_setup.sh <bench/q/cv02/slim_ckpt.py >bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/hrnet_w18_unetpp_swad_const_pf_v11.yaml >bench/methods_cv02/swad_const_pf_v11.yaml >bench/q/cv02/cq.sh >bench/q/cv02/cq_rescue.sh >bench/q/cv02/cq_setup.sh >bench/q/cv02/slim_ckpt.py >tests/test_bench_c3x_card.py >tests/test_bench_cq_readouts.py "
[ "$D" = "$DW" ] && ok "(2) CODE.md5 of X against the 89b9ea5 deploy: only the 9 paths differ (+ REVISION); $(grep -c . $OUT/x/CODE.md5) against $(grep -c . $ST/CODE.md5) lines" || bad "(2) CODE.md5 differs in: $D"
if [ "${CV02:-0}" = 1 ]; then
  m=$(ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "md5sum < /tmp/noob_el/bench_89b9ea5/CODE.md5 | cut -c1-32")
  [ "$m" = "$(md5sum < $ST/CODE.md5 | cut -c1-32)" ] && ok "(2) cv02 B /tmp/noob_el/bench_89b9ea5/CODE.md5 = the stage copy's ($m)" || bad "(2) cv02 B CODE.md5 $m != stage copy"
fi
# (3)
n=$(echo "$WANT" | cut -f2 | grep -cE '^(scripts|src|configs|data)/')
[ "$n" = 0 ] && ok "(3) none of the 9 paths is under scripts/ src/ configs/ data/" || bad "(3) $n of the 9 paths under scripts/ src/ configs/ data/"
n=$(echo "$WANT" | cut -f2 | grep '\.py$' | grep -cvE '^(bench/q/cv02|tests)/')
[ "$n" = 0 ] && ok "(3) the only Python files among them are bench/q/cv02/slim_ckpt.py (queue step after the dumps) and two tests" || bad "(3) other Python files"
h=$(cd $OUT/x && grep -rlE 'cq_setup|cq_rescue|cq\.sh|slim_ckpt|methods_cv02|test_bench_c3x|test_bench_cq' scripts src configs bench/*.py 2>/dev/null | tr '\n' ' ')
[ -z "$h" ] && ok "(3) no file under scripts/ src/ configs/ bench/*.py names a queue script, slim_ckpt, methods_cv02 or the two tests" || bad "(3) referenced by: $h"
# (4)
cd $OUT/x || exit 1
CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 nice -n 19 $P -X importtime scripts/train.py --help > /dev/null 2> $OUT/train.imp
CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 nice -n 19 $P -X importtime scripts/bench_infer.py --run $OUT/none --set cv5v3_f0 --dumps $OUT/none --method m > /dev/null 2> $OUT/infer.imp
for f in train infer; do
  mods=$(grep -oE '\| +(src|bench|scripts)(\.[A-Za-z0-9_]+)*$' $OUT/$f.imp | awk '{print $2}' | sort -u)
  n=$(echo "$mods" | grep -c .)
  hit=$(echo "$mods" | grep -E 'cq|slim|methods' | tr '\n' ' ')
  [ "$n" -gt 0 ] && [ -z "$hit" ] && ok "(4) $f: $n repo modules imported at start, none of the 9 paths: $(echo $mods | tr ' ' ',' | cut -c1-300)" || bad "(4) $f: modules $n, hits '$hit'"
done
grep -q "Traceback" $OUT/infer.imp && echo "     (bench_infer.py stopped after its imports, as intended: $(grep -E 'Error|assert' $OUT/infer.imp | tail -1 | cut -c1-120))"
cd / ; [ "${KEEP:-0}" = 1 ] && echo "kept $OUT" || rm -rf $OUT
echo "c3x code proof: $fails FAIL"
exit $([ $fails = 0 ] && echo 0 || echo 1)
