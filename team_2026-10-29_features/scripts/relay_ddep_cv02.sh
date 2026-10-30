#!/bin/bash
# Relay the finished DDeP pretraining run cv02 -> laptop -> gaint (README: no ssh -A, no key on cv02; MD5 on both hops).
# Source: cv02 /tmp/noob_el/el_f2/{experiments/f2_ddep_pre_s0/, experiments/f2_ddep_pre_s0.stdout, reports/f2/ddep_cv02.log, REVISION}
# Dest:   gaint /home/noob/work/cv02_noob_el/el_f2/<same paths> (= lane X's DEC path and the cv02 backup).
# Placement is an atomic dir rename after the hop-2 md5 check, so lane X never sees a partial decoder_final.pth.
# Usage: relay_ddep_cv02.sh <laptop staging dir>
set -uo pipefail
STG=${1:?staging dir}
CV=cv02@10.8.1.106; GA=noob@172.18.22.20; SSH="ssh -o BatchMode=yes -o ConnectTimeout=30"
SRC=/tmp/noob_el/el_f2; DST=/home/noob/work/cv02_noob_el/el_f2
P="experiments/f2_ddep_pre_s0 experiments/f2_ddep_pre_s0.stdout reports/f2/ddep_cv02.log REVISION"
die(){ echo "RELAY FAIL: $*"; exit 1; }
# 0) source checks: rc 0, DONE at 40000, decoder md5 file matches the file
$SSH $CV "cd $SRC && grep -q 'ddep rc=0' reports/f2/ddep_cv02.log && grep -q 'DONE step 40000/40000' experiments/f2_ddep_pre_s0.stdout && cd experiments/f2_ddep_pre_s0 && md5sum -c decoder_final.md5" || die "source checks"
mkdir -p $STG && [ -z "$(ls -A $STG)" ] || die "staging $STG not empty"
# manifest computed on cv02 (source of truth)
$SSH $CV "cd $SRC && find $P -type f -print0 | sort -z | xargs -0 md5sum" > $STG/RELAY_f2_ddep_pre_s0.md5 || die "manifest"
N=$(wc -l < $STG/RELAY_f2_ddep_pre_s0.md5); [ "$N" -ge 5 ] || die "manifest has $N files"
# hop 1: cv02 -> laptop
rsync -a -e "$SSH" --relative $(for p in $P; do echo "$CV:$SRC/./$p"; done) $STG/ || die "hop1 rsync"
(cd $STG && md5sum -c --quiet RELAY_f2_ddep_pre_s0.md5) || die "hop1 md5"
echo "hop1 cv02->laptop: $N files md5 OK"
# hop 2: laptop -> gaint staging on the same filesystem, check, then atomic placement
T=$DST/.relay_tmp_$(date +%s)
$SSH $GA "test ! -e $DST/experiments/f2_ddep_pre_s0 && mkdir -p $T $DST/experiments $DST/reports/f2" || die "gaint dest exists or mkdir failed"
rsync -a -e "$SSH" $STG/ $GA:$T/ || die "hop2 rsync"
$SSH $GA "cd $T && md5sum -c --quiet RELAY_f2_ddep_pre_s0.md5" || die "hop2 md5"
echo "hop2 laptop->gaint: md5 OK"
$SSH $GA "set -e; cd $T; mv experiments/f2_ddep_pre_s0.stdout $DST/experiments/; mv reports/f2/ddep_cv02.log $DST/reports/f2/; mv REVISION $DST/REVISION; mv RELAY_f2_ddep_pre_s0.md5 $DST/; mv experiments/f2_ddep_pre_s0 $DST/experiments/; cd $DST && md5sum -c --quiet RELAY_f2_ddep_pre_s0.md5 && find $T -depth -type d -empty -delete" || die "placement"
$SSH $GA "cd $DST/experiments/f2_ddep_pre_s0 && md5sum -c decoder_final.md5 && cat decoder_final.md5" || die "final decoder check"
echo "RELAY OK $(TZ=Asia/Kolkata date '+%d %b %H:%M IST'): $N files at $GA:$DST"
