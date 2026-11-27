#!/bin/bash
# What would run_read_w2a.sh select and run right now? (builder, 17 Nov 2026)
# Runs a copy of run_read_w2a.sh against the REAL dump logs, manifests and gate verdicts, with two lines replaced: the
# output folder (under the work dir given here) and the call of bench_read_w1.py (one printed line). No read is
# computed and /home/noob/work/bench_reads/w2a is not created.
#   bash preflight_now.sh <work dir that does not exist yet> [VAR=value ...]     e.g. ARMS="rcs ema" or GATE_ACK=spd
set -u
S=${1:?usage: preflight_now.sh <new work dir> [VAR=value ...]}
[ -e $S ] && { echo "exists: $S"; exit 1; }
H=$(dirname $(readlink -f $0))
mkdir -p $S/out || exit 1
sed -e "s#else O=/home/noob/work/bench_reads/w2a#else O=$S/out/w2a#" \
    -e 's#^  nice -n 19 \$P scripts/bench_read_w1.py .*#  echo "WOULD RUN THE READ"; : \\#' $H/run_read_w2a.sh > $S/run_copy.sh
[ "$(diff $H/run_read_w2a.sh $S/run_copy.sh | grep -c '^>')" = 2 ] || { echo "setup fail: the copy must differ in 2 lines"; exit 1; }
shift
for v in "$@"; do case $v in DRY=*) echo "DRY is not for the preflight (its output folder is not under the work dir)"; exit 1;; esac; done
env "$@" bash $S/run_copy.sh
echo "preflight rc=$? (copy of run_read_w2a.sh $(md5sum < $H/run_read_w2a.sh | cut -c1-8); real read folder exists: $([ -e /home/noob/work/bench_reads/w2a ] && echo yes || echo no))"
