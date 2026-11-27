#!/bin/bash
# Render smoke of the fin job list on cv02 itself (builder's pre-launch evidence; the lead's own render is final_queue.sh
# render on the real deploy). gaint drives; cv02 gets ONE new scratch dir of ours, W = /tmp/noob_el/bench_finsmoke_<stamp>,
# and nothing else is written there: (1) gaint stage = git archive of F + REVISION + CODE.md5 (as c3_deploy.sh) in SCR;
# (2) tar stream to W (refused if W exists), md5sum -c CODE.md5 on cv02; (3) cv02: W's scripts/bench_make_pool_root.py
# builds pool532_v11 under W/data_fin/roots from cv02's pinned inputs, then --check; (4) the job list with the full-pool root
# path mapped to W/data_fin placed as W/q/jobs.txt with LPG 1; (5) W's cq.sh run render-only (B = QC = W, DATA_F = W/data_fin;
# DATA, DATA_V3, DUMPOF_ROOT at their defaults, so the 50 source runs and their configs are the real ones, read only): it
# stops at the gpumem-logger check, no GPU is read, nothing starts; (6) W/q/jobs_rendered.txt and launch.log copied to OUT and
# compared by final_rendercmp.py (templates and semantics); (7) W removed (rm -rf of the one path, pattern-checked) unless KEEP=1.
# Usage: F=<full commit> JOBS=<jobs_fin.txt> SCR=<new gaint scratch dir> OUT=<new evidence dir> [KEEP=1] bash final_render_smoke.sh
set -u
F=${F:?full commit}; JOBS=${JOBS:?job list}; SCR=${SCR:?scratch}; OUT=${OUT:?evidence dir}; KEEP=${KEEP:-0}
HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); REPO=/home/noob/work/bench_wt_fin
C=cv02@10.8.1.106; DATA_MD5=d6063fd83d20e656612540edda702cbe; DF=/tmp/noob_el/bench_data_fin
W=/tmp/noob_el/bench_finsmoke_$(date +%m%d%H%M)
R(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 $C "$1"; }
no(){ echo "REFUSED: $*"; exit 1; }
[ -e $SCR ] && no "$SCR exists"; [ -e $OUT ] && no "$OUT exists"; mkdir -p $SCR/stage $OUT || exit 1
git -C $REPO archive $F | tar -x -C $SCR/stage && echo $F > $SCR/stage/REVISION || no "archive"
(cd $SCR/stage && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5 && md5sum -c --quiet CODE.md5) || no "stage md5"
echo "stage: REVISION $F, CODE.md5 $(md5sum < $SCR/stage/CODE.md5 | cut -c1-32)" | tee $OUT/smoke.log
R "test ! -e $W" || no "cv02 $W exists"
tar -C $SCR/stage -cf - . | ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "test ! -e $W && mkdir $W && tar -x -C $W"; rc=${PIPESTATUS[0]}${PIPESTATUS[1]}
[ "$rc" = 00 ] || no "stream rc $rc"
echo "cv02 scratch dir $W: $(R "cd $W && md5sum -c --quiet CODE.md5 && echo CODE_OK \$(cat REVISION)")" | tee -a $OUT/smoke.log
R "cd $W && nice -n 19 /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/bench_make_pool_root.py --split /tmp/noob_el/bench_data_v3b/meta/cv5v3.json --forbidden /tmp/noob_el/bench_data/meta/forbidden_v1.txt --legacy-splits $W/data/splits --labeled /tmp/noob_el/bench_data/labeled --train-masks /tmp/noob_el/bench_data/masks_v11/masks --out $W/data_fin/roots && nice -n 19 /tmp/noob_el/el-fault-detection/.venv/bin/python scripts/bench_make_pool_root.py --split /tmp/noob_el/bench_data_v3b/meta/cv5v3.json --forbidden /tmp/noob_el/bench_data/meta/forbidden_v1.txt --legacy-splits $W/data/splits --labeled /tmp/noob_el/bench_data/labeled --train-masks /tmp/noob_el/bench_data/masks_v11/masks --out $W/data_fin/roots --check; cd $W/data_fin/roots/pool532_v11 && md5sum splits/train.txt splits/test.txt SPLITS.md5 DATA_MANIFEST.md5" | tee $OUT/pool_root_cv02.out
sed "s#|$DF/#|$W/data_fin/#" $JOBS > $SCR/jobs_smoke.txt; J=$(md5sum < $SCR/jobs_smoke.txt | cut -c1-32)
[ "$(grep -c "|$W/data_fin/roots/pool532_v11|" $SCR/jobs_smoke.txt)" = 10 ] || no "root mapping"
ssh -a -o BatchMode=yes -o ConnectTimeout=20 $C "mkdir $W/q && cat > $W/q/jobs.txt && echo 1 > $W/q/LPG && md5sum < $W/q/jobs.txt | cut -c1-32" < $SCR/jobs_smoke.txt > $SCR/placed.md5 || no "place"
[ "$(cat $SCR/placed.md5)" = "$J" ] || no "placed md5"
t0=$(date +%s)
R "B=$W Q=$W/q JOBS_MD5=$J DEPLOY=$F DATA_MD5=$DATA_MD5 DATA_F=$W/data_fin nice -n 19 bash $W/bench/q/cv02/cq.sh; echo \"rc \$?; last line: \$(tail -1 $W/q/launch.log | cut -c23-)\"" | tee $OUT/render.out
echo "render took $(( $(date +%s) - t0 )) s" | tee -a $OUT/smoke.log
grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" $OUT/render.out || no "render did not reach the logger check (see $OUT/render.out)"
R "cat $W/q/jobs_rendered.txt" > $OUT/rendered.txt; R "cat $W/q/launch.log" > $OUT/launch.log
PYTHONDONTWRITEBYTECODE=1 /home/noob/work/el-fault-detection/.venv/bin/python $HERE/final_rendercmp.py --jobs $JOBS --rendered $OUT/rendered.txt \
  --b $W --df $DF=$W/data_fin --repo $REPO | tee $OUT/render_cmp.out
rc=${PIPESTATUS[0]}
if [ "$KEEP" != 1 ]; then echo "$W" | grep -qE '^/tmp/noob_el/bench_finsmoke_[0-9]{8}$' && R "rm -rf -- $W && echo removed $W" | tee -a $OUT/smoke.log; fi
echo "render smoke rc $rc" | tee -a $OUT/smoke.log; exit $rc
