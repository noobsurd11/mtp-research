#!/bin/bash
# integrator c3base, runs ON cv02 (ssh -a ... "bash -s"). Render-only runs of cq.sh in scratch queue dirs under
# /tmp/noob_el/bench_c3_render (new): cq.sh arms up to Q/jobs_rendered.txt and stops at the gpumem-logger check (no logger
# runs, no GPU is read, nothing starts). (a) patched cq.sh (deploy a3cf85a) and (b) the deployed b12fca8 cq.sh (5f13e5ac,
# copy) on the reviewed rows 2 job list (87e0b608), both with B = the new deploy; (c) patched cq.sh on the c3base list.
# Needs W/jobs_rows2.txt, W/jobs_c3base.txt, W/cq_b12fca8.sh placed first (from gaint, md5-checked).
set -u
B=/tmp/noob_el/bench_a3cf85a; W=/tmp/noob_el/bench_c3_render; DEP=a3cf85ab4ae3417d8fb5e2808c2132f2d117f883; DM=d6063fd83d20e656612540edda702cbe
cd $W && md5sum jobs_rows2.txt jobs_c3base.txt cq_b12fca8.sh
run(){ local q=$W/$1 s=$2 j=$3; [ -e $q ] && { echo "REFUSED: $q exists"; return 1; }; mkdir -p $q; cp $j $q/jobs.txt; echo 1 > $q/LPG
  B=$B Q=$q JOBS_MD5=$(md5sum < $q/jobs.txt | cut -c1-32) DEPLOY=$DEP DATA_MD5=$DM nice -n 19 bash $s; echo "$1 rc=$? last: $(tail -1 $q/launch.log | cut -c23-)"; }
run q_new $B/bench/q/cv02/cq.sh $W/jobs_rows2.txt
run q_old $W/cq_b12fca8.sh $W/jobs_rows2.txt
run q_v3 $B/bench/q/cv02/cq.sh $W/jobs_c3base.txt
echo "rendered md5: new $(md5sum < q_new/jobs_rendered.txt | cut -c1-8) old $(md5sum < q_old/jobs_rendered.txt | cut -c1-8) lines $(wc -l < q_new/jobs_rendered.txt) / $(wc -l < q_old/jobs_rendered.txt); cmp new old: $(cmp -s q_new/jobs_rendered.txt q_old/jobs_rendered.txt && echo IDENTICAL || echo DIFF)"
echo "new with B -> bench_b12fca8: $(sed 's#/tmp/noob_el/bench_a3cf85a/#/tmp/noob_el/bench_b12fca8/#g' q_new/jobs_rendered.txt | md5sum | cut -c1-8) (deployed rows2 jobs_rendered.txt $(md5sum < /tmp/noob_el/bench_q/rows2/jobs_rendered.txt | cut -c1-8))"
echo "c3base rendered: $(wc -l < q_v3/jobs_rendered.txt) lines; dump lines with --set cv5v3_f<fold of root> $(awk -F'|' '/^dump_/ {n=$1; sub(/^dump_c3_[a-z]+_v11_f/,"",n); k=substr(n,1,1); if (index($2, " --set cv5v3_f" k " ") && index($2, " --logp ")) c++} END {print c+0}' q_v3/jobs_rendered.txt) of 50; any cv5v2 token $(grep -c cv5v2 q_v3/jobs_rendered.txt)"
ls $B/experiments $B/runs $B/dumps 2>/dev/null | head -3
