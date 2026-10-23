#!/usr/bin/env bash
# Relay finished AL1 runs (cv02 /tmp/noob_el/el_alhvr) to gaint cv02_noob_el/el_alhvr via the laptop, then MD5-verify.
# Model: relay_cv02_21oct.sh. Usage: relay_cv02_al1.sh <path relative to el_alhvr> ...  (run dirs, their .stdout/.rescore.log, reports)
set -uo pipefail
CV="ssh -o BatchMode=yes cv02@10.8.1.106"; GA="ssh -o BatchMode=yes noob@172.18.22.20"
SRC=/tmp/noob_el/el_alhvr; DST=/home/noob/work/cv02_noob_el/el_alhvr
p="$*"
echo "== el_alhvr $(date +%H:%M): $(echo $p | wc -w) paths"
$GA "mkdir -p $DST"
$CV "cd $SRC && tar cf - $p" | $GA "cd $DST && tar xf -" || { echo "tar FAILED"; echo "RELAY HAD ERRORS"; exit 1; }
a=$($CV "cd $SRC && find $p -type f -print0 | sort -z | xargs -0 md5sum" | md5sum)
b=$($GA "cd $DST && find $p -type f -print0 | sort -z | xargs -0 md5sum" | md5sum)
n=$($GA "cd $DST && find $p -type f | wc -l"); m=$($CV "cd $SRC && find $p -type f | wc -l")
if [ "$a" = "$b" ] && [ "$n" = "$m" ]; then echo "el_alhvr: $n files, MD5 manifest IDENTICAL"; echo "RELAY OK $(TZ=Asia/Kolkata date '+%d %b %H:%M IST')"
else echo "el_alhvr: MD5 MISMATCH ($m src files, $n dst files)"; echo "RELAY HAD ERRORS"; exit 1; fi
