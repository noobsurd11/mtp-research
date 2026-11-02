#!/bin/bash
# runner (3 Nov 2026): SKR2C data root (team-lead 3 Nov: data-root trick, test.txt = val), the same layout as B6's identity root
# (b6_build/idroot): /home/noob/work/s2c_root/splits/{train,val}.txt = el_f3 data/splits copies (842f27c4 / 9dcccf00; = el_thin's),
# splits/test.txt = a copy of val.txt; labeled -> /home/noob/work/el-fault-detection/data/labeled (= el_f3's data/labeled target;
# el_thin's labeled/images and labeled/masks_escdd point into it too). SPLITS.md5 written and -c checked. Refuses if the root exists.
# Asserts: test = val byte-identical; train and val disjoint, no duplicates; 0 stems of b6_forbidden.txt (9bb4d919 = real test 50 u
# ext117) in train or val; 0 real test stems (el_f3 splits/test.txt) in the root's lists.
set -eu
R=/home/noob/work/s2c_root; S=/home/noob/work/el_f3/data/splits; T=/home/noob/work/el_thin/data; F=/home/noob/work/b6/b6_forbidden.txt
[ ! -e $R ] || { echo "$R exists"; exit 1; }
[ "$(md5sum < $S/train.txt | cut -c1-32)" = 842f27c418106a2095fa642daafec3fc ]
[ "$(md5sum < $S/val.txt | cut -c1-32)" = 9dcccf00662dfca750f0b46628f8d5bb ]
[ "$(md5sum < $F | cut -c1-32)" = 9bb4d919fc16b5b394ce6d71f53903a6 ]
cmp $S/train.txt $T/splits/train.txt; cmp $S/val.txt $T/splits/val.txt
L=$(readlink -f /home/noob/work/el_f3/data/labeled); [ "$L" = /home/noob/work/el-fault-detection/data/labeled ]
[ "$(readlink -f $T/labeled/images)" = $L/images ] && [ "$(readlink -f $T/labeled/masks_escdd)" = $L/masks_escdd ]
mkdir -p $R/splits; cp $S/train.txt $S/val.txt $R/splits/; cp $S/val.txt $R/splits/test.txt; ln -s $L $R/labeled
(cd $R/splits && md5sum train.txt val.txt test.txt > ../SPLITS.md5 && md5sum -c ../SPLITS.md5)
cmp $R/splits/test.txt $R/splits/val.txt
[ -z "$(sort $R/splits/train.txt $R/splits/val.txt | uniq -d)" ]
[ -z "$(sort -u $R/splits/train.txt $R/splits/val.txt $R/splits/test.txt | comm -12 - <(sort -u $F))" ]
[ -z "$(sort -u $R/splits/train.txt $R/splits/val.txt $R/splits/test.txt | comm -12 - <(sort -u $S/test.txt))" ]
echo "root $R: train $(wc -l < $R/splits/train.txt), val $(wc -l < $R/splits/val.txt), test = val $(wc -l < $R/splits/test.txt); labeled -> $(readlink $R/labeled); SPLITS.md5 $(md5sum < $R/SPLITS.md5 | cut -c1-8); 0 forbidden, 0 real test"
