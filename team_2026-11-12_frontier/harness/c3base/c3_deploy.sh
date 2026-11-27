#!/bin/bash
# integrator c3base: deploy one bench_final commit to cv02 (= bench_rows2_io/deploy.sh with paths changed). gaint stage
# /home/noob/work/bench_c3_io/stage/bench_<short> = git archive + REVISION + CODE.md5 (every file but CODE.md5, incl. REVISION);
# tar stream to cv02 /tmp/noob_el/bench_<short> (refused if it exists on either end); md5sum -c CODE.md5 and md5 of CODE.md5
# on both ends. Never forwards an agent. Usage: c3_deploy.sh <commit>
set -u
C=$(git -C /home/noob/work/bench_wt_final rev-parse --verify "${1:?commit}^{commit}") || exit 1
S=${C:0:7}; ST=/home/noob/work/bench_c3_io/stage/bench_$S; R=/tmp/noob_el/bench_$S
SC(){ ssh -a -o ForwardAgent=no -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$@"; }
[ -e $ST ] && { echo "REFUSED: $ST exists"; exit 1; }
mkdir -p $ST && git -C /home/noob/work/bench_wt_final archive $C | tar -x -C $ST && echo $C > $ST/REVISION || exit 1
(cd $ST && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5 && md5sum -c --quiet CODE.md5) || { echo "stage md5 FAIL"; exit 1; }
G=$(md5sum < $ST/CODE.md5 | cut -c1-32); N=$(grep -c . $ST/CODE.md5)
echo "stage $ST: REVISION $C, CODE.md5 $G ($N lines)"
SC -n "test ! -e $R" || { echo "REFUSED: cv02 $R exists"; exit 1; }
tar -C $ST -cf - . | SC "test ! -e $R && mkdir $R && tar -x -C $R"; rc=${PIPESTATUS[0]}${PIPESTATUS[1]}
[ "$rc" = 00 ] || { echo "stream rc $rc"; exit 1; }
SC -n "cd $R && md5sum -c --quiet CODE.md5 && echo CV02_CODE_OK \$(cat REVISION) \$(md5sum < CODE.md5 | cut -c1-32) \$(find . -type f | wc -l) files; df -h /tmp | tail -1"
