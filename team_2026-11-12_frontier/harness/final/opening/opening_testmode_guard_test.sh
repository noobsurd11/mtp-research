#!/bin/bash
# Review round 2, B2: negatives (and one control each) for the TEST_MODE path guard of opening_register.sh and
# run_opening_read.sh. Synthetic scratch dirs only; the IO dirs are empty, so even a failed guard would refuse at the next
# check; the "real tree" paths used here do NOT exist (…/__no_such__), so no real file can be read whatever happens.
# Every case must print 'REFUSED (TEST_MODE guard)' (or, for the controls, a later refusal) and create nothing.
# Usage: bash opening_testmode_guard_test.sh <out file>
set -u
OUT=${1:?out file}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
S=/home/noob/work/bench_int_io/opening/tmguard_$$; [ -e $S ] && exit 1
mkdir -p $S/ext/images $S/ext/masks $S/ext/ignore $S/lab/images $S/lab/masks_coded $S/v11/masks $S/v11/ignore $S/relay $S/relay_fin $S/reads $S/io_read
echo s > $S/ext/stems_eval.txt; echo m > $S/v11/MANIFEST.md5; echo v > $S/fin.txt; printf 'stem\tcell_type\n' > $S/cells.tsv; echo l > $S/v11fc.md5
chk(){ # label, expected text, then the command output on stdin
  local o; o=$(cat); if echo "$o" | grep -qF "$2"; then echo "PASS  $1: $(echo "$o" | tail -1 | cut -c1-170)"; else echo "FAIL  $1: $(echo "$o" | tail -1 | cut -c1-170)"; fi; }
REGB="TEST_MODE=1 IO=$S/io_reg FIN_VERDICT=$S/fin.txt EXT_DIR=$S/ext LABELED_DIR=$S/lab MASKS_V11_DIR=$S/v11"
reg(){ env -u IO -u FIN_VERDICT -u EXT_DIR -u LABELED_DIR -u MASKS_V11_DIR "$@" bash $HERE/opening_register.sh 2>&1; }
{
echo "== opening_register.sh"
reg $(echo $REGB | sed "s# FIN_VERDICT=$S/fin.txt##") | chk "R1 TEST_MODE, FIN_VERDICT left at its default" "REFUSED (TEST_MODE guard): FIN_VERDICT must be set explicitly"
reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=/home/noob/work/ext117/__no_such__#") | chk "R2 TEST_MODE, EXT_DIR inside the real tree" "REFUSED (TEST_MODE guard): /home/noob/work/ext117/__no_such__ resolves to"
mkdir -p $S/ext2/images $S/ext2/ignore; echo s > $S/ext2/stems_eval.txt; ln -s /home/noob/work/ext117/__no_such__ $S/ext2/masks
reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=$S/ext2#") | chk "R3 TEST_MODE, a scratch EXT_DIR whose masks dir is a symlink into the real tree" "REFUSED (TEST_MODE guard): $S/ext2/masks resolves to /home/noob/work/ext117/__no_such__"
mkdir -p $S/lab2/images $S/lab2/masks_coded; ln -s /home/noob/work/el-fault-detection/data/labeled/masks_coded/__no_such__.png $S/lab2/masks_coded/X.png
reg $(echo $REGB | sed "s#LABELED_DIR=$S/lab#LABELED_DIR=$S/lab2#") | chk "R4 TEST_MODE, one mask file in a scratch dir is a symlink into the real tree" "REFUSED (TEST_MODE guard): $S/lab2/masks_coded/X.png resolves to"
(cd $S && reg $(echo $REGB | sed "s#EXT_DIR=$S/ext#EXT_DIR=ext#")) | chk "R7 TEST_MODE, a relative EXT_DIR (B3; run from the scratch dir, where it would resolve inside it)" "REFUSED (TEST_MODE guard): ext is not an absolute path"
reg $(echo $REGB | sed "s#FIN_VERDICT=$S/fin.txt#FIN_VERDICT=$S/no_fin.txt#") SKIP_GIT=1 | chk "R5 control: all paths scratch -> the guard passes, a later check refuses" "REFUSED (register): fin verdict $S/no_fin.txt missing"
reg $(echo $REGB | sed "s#FIN_VERDICT=$S/fin.txt#FIN_VERDICT=$S/no_fin.txt#") | chk "R6 control with the git pins checked (G, R, F2 with their trees): the guard passes, a later check refuses" "REFUSED (register): fin verdict $S/no_fin.txt missing"
echo "   IO made by any register case: $([ -e $S/io_reg ] && echo YES || echo no)"
echo "== run_opening_read.sh"
RB="TEST_MODE=1 REG_MD5=0 IO=$S/io_read RD=$S/relay RF=$S/relay_fin READ_ROOT=$S/reads BENCH_EXT=$S/ext BENCH_LABELED=$S/lab BENCH_MASKS_V11=$S/v11 CELLS_TSV=$S/cells.tsv FIN_VERDICT=$S/fin.txt V11_FILECHECK_MANIFEST=$S/v11fc.md5"
rd(){ env -u IO -u RD -u RF -u READ_ROOT -u BENCH_EXT -u BENCH_LABELED -u BENCH_MASKS_V11 -u CELLS_TSV -u FIN_VERDICT -u V11_FILECHECK_MANIFEST "$@" bash $HERE/run_opening_read.sh 2>&1; }
rd $(echo $RB | sed "s# READ_ROOT=$S/reads##") | chk "D1 TEST_MODE, READ_ROOT left at its default" "REFUSED (TEST_MODE guard): READ_ROOT must be set explicitly"
rd $(echo $RB | sed "s# BENCH_MASKS_V11=$S/v11##") | chk "D2 TEST_MODE, BENCH_MASKS_V11 left at its default" "REFUSED (TEST_MODE guard): BENCH_MASKS_V11 must be set explicitly"
rd $(echo $RB | sed "s#BENCH_LABELED=$S/lab#BENCH_LABELED=/home/noob/work/el-fault-detection/data/labeled/__no_such__#") | chk "D3 TEST_MODE, BENCH_LABELED inside the real tree" "REFUSED (TEST_MODE guard): /home/noob/work/el-fault-detection/data/labeled/__no_such__ resolves to"
rd $(echo $RB | sed "s#RD=$S/relay#RD=/mnt/nas/noob_el_archive/bench_relay/__no_such__#") | chk "D4 TEST_MODE, RD on the real relay tree" "REFUSED (TEST_MODE guard): /mnt/nas/noob_el_archive/bench_relay/__no_such__ resolves to"
mkdir -p $S/relay2; ln -s /home/noob/work/bench_relay/__no_such__ $S/relay2/unit
rd $(echo $RB | sed "s#RD=$S/relay#RD=$S/relay2#") | chk "D5 TEST_MODE, a scratch RD holding a symlink into the real relay tree" "REFUSED (TEST_MODE guard): $S/relay2/unit resolves to /home/noob/work/bench_relay/__no_such__"
mkdir -p $S/data/labeled/images $S/data/labeled/masks_coded
(cd $S && rd $(echo $RB | sed "s#BENCH_LABELED=$S/lab#BENCH_LABELED=data/labeled#")) | chk "D7 TEST_MODE, a relative BENCH_LABELED=data/labeled (B3; the read cds to RT, whose data/labeled is the real data)" "REFUSED (TEST_MODE guard): data/labeled is not an absolute path"
(cd $S && rd $(echo $RB | sed "s#READ_ROOT=$S/reads#READ_ROOT=reads#")) | chk "D8 TEST_MODE, a relative READ_ROOT (B3)" "REFUSED (TEST_MODE guard): reads is not an absolute path"
rd $RB | chk "D6 control: all paths scratch -> the guard passes, a later check refuses" "REFUSED: no $S/io_read/REGISTERED.txt"
echo "   output folder made by any read case: $([ -n "$(ls -A $S/reads)" ] && echo YES || echo no)"
} | tee $OUT
echo "guard test: $(grep -c '^FAIL' $OUT) FAIL" | tee -a $OUT
rm -rf $S
grep -q "^guard test: 0 FAIL" $OUT
