#!/bin/bash
# Builder's local test of `opening_queue.sh unstage` (review round 1, N6 / N7) on gaint, nothing on cv02: a stub `ssh` first in
# PATH runs each cv02 command locally with /tmp/noob_el/ mapped into a scratch dir; synthetic "sealed" dumps (random bytes) laid
# out as on cv02 (GB/runs, GB/dumps) and as relayed (RD); a staged DS with 157 files + MANIFEST.md5.
# Cases: (1) relay not done -> refused, nothing removed; (2) one cv02 dump file differs from its relayed copy -> that dir is
# kept, the step refuses, DS kept; (3) all equal -> every dump dir and DS removed, runs/<job>/RUN.md5 kept, the removal log
# written. Usage: bash opening_unstage_smoke.sh <out dir>
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); mkdir -p $OUT
S=/home/noob/work/bench_int_io/opening/unstage_$$; [ -e $S ] && exit 1; mkdir -p $S/bin $S/noob_el
cat > $S/bin/ssh <<EOF
#!/bin/bash
c="\${@: -1}"; c=\${c//\/tmp\/noob_el\//$S/noob_el/}
exec bash -c "\$c"
EOF
chmod +x $S/bin/ssh
GB=$S/noob_el/bench_8bd1c27; DS=$S/noob_el/bench_data_sealed; RD=$S/relay; IO=$S/io; mkdir -p $RD/.ok $IO
head -3 $HERE/jobs/jobs_open_c1d4_no.txt > $IO/jobs.txt; md5sum < $IO/jobs.txt | cut -c1-32 > $IO/jobs.md5
mkdir -p $DS/e1_106/images $DS/legacy/images; echo s > $DS/e1_106/stems_eval.txt
for i in $(seq 1 106); do head -c 64 /dev/urandom > $DS/e1_106/images/c$i.png; done
for i in $(seq 1 50); do head -c 64 /dev/urandom > $DS/legacy/images/t$i.png; done
(cd $DS && find . -type f ! -name MANIFEST.md5 -printf '%P\n' | sort | xargs md5sum > MANIFEST.md5)
printf 'registered x\njobs %s 3 lines\nstage_manifest %s\n' $(cat $IO/jobs.md5) $(md5sum < $DS/MANIFEST.md5 | cut -c1-32) > $IO/REGISTERED.txt
md5sum < $IO/REGISTERED.txt | cut -c1-32 > $IO/REGISTERED.md5
for n in $(cut -d'|' -f1 $IO/jobs.txt); do
  d=dumps/elbench1/m/$n/e1_106; mkdir -p $GB/$d $GB/runs/$n
  for c in a b c; do head -c 2048 /dev/urandom > $GB/$d/$c.npz; done; echo '{}' > $GB/$d/manifest.json
  (cd $GB && find $d -type f | sort | xargs md5sum > runs/$n/RUN.md5)
  mkdir -p $RD/$n && (cd $GB && tar cf - runs/$n/RUN.md5 $d) | tar xf - -C $RD/$n
  echo "$(date '+%F %T') RUN.md5 $(md5sum < $GB/runs/$n/RUN.md5 | cut -c1-32) files 4" > $RD/.ok/$n
done
Q(){ PATH=$S/bin:$PATH IO=$IO RD=$RD bash $HERE/opening_queue.sh unstage 2>&1; }
echo "case 1 (relay not done): $(Q | tail -1)" | tee $OUT/unstage_smoke.out
echo "RELAY ALL DONE: 3 of 3 runs relayed" > $RD/relay.log
n2=$(sed -n 2p $IO/jobs.txt | cut -d'|' -f1); f=$GB/dumps/elbench1/m/$n2/e1_106/b.npz; printf x >> $f
echo "case 2 (one cv02 file differs): $(Q | grep -E 'SKIP|REMOVED_DUMPS|REFUSED' | tr '\n' ' ')" | tee -a $OUT/unstage_smoke.out
echo "  after case 2: dump dirs left $(ls -d $GB/dumps/elbench1/m/* 2>/dev/null | wc -l) (the tampered one: $([ -d $GB/dumps/elbench1/m/$n2 ] && echo kept || echo removed)); DS $([ -d $DS ] && echo kept || echo removed)" | tee -a $OUT/unstage_smoke.out
# restore the two removed dirs from the relayed copies and the tampered file, then the clean case
for n in $(cut -d'|' -f1 $IO/jobs.txt); do (cd $RD/$n && tar cf - dumps) | tar xf - -C $GB --skip-old-files 2>/dev/null; done
cp $RD/$n2/dumps/elbench1/m/$n2/e1_106/b.npz $f
echo "case 3 (all equal): $(Q | grep -E 'REMOVED|removed|REFUSED' | tr '\n' ' ' | cut -c1-300)" | tee -a $OUT/unstage_smoke.out
echo "  after case 3: dump dirs left $(ls -d $GB/dumps/elbench1/m/* 2>/dev/null | wc -l); runs/*/RUN.md5 kept $(ls $GB/runs/*/RUN.md5 | wc -l); DS $([ -d $DS ] && echo kept || echo removed); removal log lines $(grep -c removed $S/noob_el/removed_relayed_dumps_open.log)" | tee -a $OUT/unstage_smoke.out
chmod -R u+w $S; rm -rf $S
