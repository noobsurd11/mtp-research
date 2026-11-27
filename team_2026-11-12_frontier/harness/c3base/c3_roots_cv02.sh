#!/bin/bash
# integrator c3base, runs ON cv02 (piped by ssh -a ... "bash -s" from gaint; reads only, except /tmp/noob_el/bench_data_v3b/roots).
# Builds the five cv5v3 roots with the deployed root builder from the meta copied to /tmp/noob_el/bench_data_v3b/meta, then
# --check, md5sum -c, a read-only walk (links resolve, DATA_MANIFEST and SPLITS check per root). Existing cv5v2 data untouched.
set -u
B=__B__; D=/tmp/noob_el/bench_data_v3b; P=/tmp/noob_el/el-fault-detection/.venv/bin/python; X=/tmp/noob_el/bench_data
cd $D/meta && md5sum -c --quiet META.md5 && echo "META_OK $(md5sum < META.md5 | cut -c1-8)" || { echo "META FAIL"; exit 1; }
cmp -s $D/meta/forbidden_v1.txt $X/meta/forbidden_v1.txt && echo "forbidden_v1 = bench_data/meta copy" || echo "forbidden_v1 DIFFERS"
[ -e $D/roots ] && { echo "REFUSED: $D/roots exists"; exit 1; }
cd $B && md5sum -c --quiet CODE.md5 && echo "CODE_OK $(cat REVISION)" || { echo "CODE FAIL"; exit 1; }
A="--split $D/meta/cv5v3.json --groups $D/meta/cv5v3_groups.tsv --forbidden $D/meta/forbidden_v1.txt --legacy-splits data/splits --labeled $X/labeled --out $D/roots --tag v11 --train-masks $X/masks_v11/masks --heldout-masks $X/masks_v11/masks_strict --link-dir masks_v11"
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 $P scripts/bench_make_roots.py $A > /tmp/noob_el/bench_data_v3b/build_v11.out 2>&1; echo "build rc=$?"
cat /tmp/noob_el/bench_data_v3b/build_v11.out
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 $P scripts/bench_make_roots.py $A --check 2>&1 | tail -3; echo "check rc=${PIPESTATUS[0]}"
cd $D/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 && echo "ROOTS_OK $(md5sum < ROOTS_cv5v3_v11.md5)"
for k in 0 1 2 3 4; do r=$D/roots/cv5v3_v11_f$k
  (cd $r && md5sum -c --quiet SPLITS.md5 && md5sum -c --quiet DATA_MANIFEST.md5) && s=OK || s=FAIL
  echo "f$k splits+manifest $s; train $(grep -c . $r/splits/train.txt) val $(grep -c . $r/splits/val.txt) test $(grep -c . $r/splits/test.txt); test=val $(cmp -s $r/splits/val.txt $r/splits/test.txt && echo yes || echo no); links $(ls $r/masks_v11 | wc -l), dangling $(find $r/masks_v11 -xtype l | wc -l); labeled -> $(readlink $r/labeled)"; done
chmod -R a-w $D/roots $D/meta && echo "roots, meta read-only"
df -h /tmp | tail -1
