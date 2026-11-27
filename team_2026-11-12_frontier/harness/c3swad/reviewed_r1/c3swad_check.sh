#!/bin/bash
# c3swad: checks before the launch (run by the LEAD on gaint; LAUNCH_REQUEST_c3swad.md section 8). READ ONLY on both
# machines: nothing is written on cv02, and on gaint only the output goes to the terminal. CPU only (a few card renders).
# Lines start with OK, FAIL or SKIP; the last line counts them. Run it before `c3swad_handover.sh freeze` and again
# before `arm`.
#   QC=<cv02 deploy dir of the patched queue code>   optional: without it the QC checks are SKIP (before the deploy)
#   IO=<handover folder>                             optional: with IO/rendered.txt (from `handover render`) the rendered
#                                                    swad jobs are compared with the card as rendered on gaint
set -u
QC=${QC:-}; IO=${IO:-/home/noob/work/bench_c3_io/c3swad}; NEWQ=${NEWQ:-c3all2}
T=/home/yugma/mtp/research/team_2026-11-12_frontier; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
W=/home/noob/work/bench_wt_final; W2=/home/noob/work/bench_wt_w2; R=/home/noob/work/el_bench
P=/home/noob/work/el-fault-detection/.venv/bin/python
B=/tmp/noob_el/bench_89b9ea5; BQ=/tmp/noob_el/bench_q; V3=/tmp/noob_el/bench_data_v3b
CARD=bench/methods/swad_const_pf_v11.yaml; CARD_MD5=46fb5b02be9d59b4dc00a21dc216e86f; CV_MD5=618cea2f57864ac4a916da00845da9da
export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
C(){ ssh -n -a -o BatchMode=yes -o ConnectTimeout=20 cv02@10.8.1.106 "$1"; }
NO=0; NFL=0; NS=0
ok(){ NO=$((NO+1)); echo "OK   $*"; }; bad(){ NFL=$((NFL+1)); echo "FAIL $*"; }; skip(){ NS=$((NS+1)); echo "SKIP $*"; }
ck(){ if eval "$2"; then ok "$1"; else bad "$1"; fi; }
echo "[$(date '+%F %T')] c3swad check (QC '${QC:-none}', IO $IO)"

echo "--- 1 card and code"
ck "gaint read and deploy tree $W at 89b9ea5, no tracked change" '[ "$(git -C $W rev-parse --short HEAD)" = 89b9ea5 ] && [ "$(git -C $W status --porcelain -uno | wc -l)" = 0 ]'
ck "card md5 $CARD_MD5 in bench_wt_final (89b9ea5) and in bench_wt_w2 (c57508e, the screen's tree)" '[ "$(md5sum < $W/$CARD | cut -c1-32)" = $CARD_MD5 ] && [ "$(md5sum < $W2/$CARD | cut -c1-32)" = $CARD_MD5 ]'
cv=$(C "md5sum < $B/$CARD | cut -c1-32; cat $B/REVISION; cd $B && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK") || cv=""
ck "card md5 on cv02 $B equal; REVISION 89b9ea5a; CODE.md5 OK" '[ "$(echo $cv)" = "$CARD_MD5 89b9ea5a12a37a87c16c4868cc4adf00794a7610 CODE_OK" ]'
SW="configs/base.yaml src/trainers/trainer.py src/trainers/weight_avg.py src/trainers/enc_probe.py scripts/bn_recalibration.py $CARD configs/supervised.yaml scripts/train.py bench/cards.py"
ck "swad code paths byte-equal c57508e..89b9ea5 (scheduler, weight_avg, bn_recal, enc_probe, card, cards.py, train.py)" 'git -C $R merge-base --is-ancestor c57508e 89b9ea5 && [ -z "$(git -C $R diff --name-only c57508e 89b9ea5 -- $SW)" ]'
ck "training code changed c57508e..89b9ea5 only in src/models/bench_models.py (deeplab pooling of bench_smp; not smp_unetpp)" '[ "$(git -C $R diff --name-only c57508e 89b9ea5 -- src configs scripts/train.py | tr "\n" " ")" = "src/models/bench_models.py " ] && [ "$(git -C $R diff c57508e 89b9ea5 -- src/models/bench_models.py | grep -c "^@@")" = 1 ]'
n=0; e=0
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do a="--seed $s --run-name c3s_swad_v11_f${k}_s$s --data-root $V3/roots/cv5v3_v11_f$k"
  x=$(cd $W && nice -n 19 $P -m bench.cards opts $CARD $a | md5sum); y=$(cd $W2 && nice -n 19 $P -m bench.cards opts $CARD $a | md5sum); n=$((n+1)); [ "$x" = "$y" ] && [ -n "$x" ] && e=$((e+1)); done; done
ck "card renders the same options at c57508e and 89b9ea5 for the 25 swad jobs ($e of $n)" '[ $e = 25 ]'

echo "--- 2 queue code (QC) and the cv02 card variant"
if [ -z "$QC" ]; then skip "no QC given: patched queue code not deployed yet (pins, CODE.md5, variant, weights)"
else
  q=$(C "cd $QC && md5sum -c --quiet CODE.md5 > /dev/null 2>&1 && echo CODE_OK; md5sum < bench/q/cv02/cq.sh | cut -c1-32; md5sum < bench/methods_cv02/swad_const_pf_v11.yaml | cut -c1-32; diff $B/$CARD bench/methods_cv02/swad_const_pf_v11.yaml | grep -c '^[<>]'; f=\$(sed -n 's/^  - path: //p' bench/methods_cv02/swad_const_pf_v11.yaml); md5sum < \$f | cut -c1-32") || q=""
  ck "QC $QC: CODE.md5 OK, cq.sh 5222150b, cv02 variant $CV_MD5 = card except the weights path line, weights file f57b4305 on cv02" '[ "$(echo $q)" = "CODE_OK 5222150ba40130d41a04af4f7d17dbfa $CV_MD5 2 f57b430554b18e1238c4f92eac566544" ]'
fi

echo "--- 3 data roots on cv02 (all five folds)"
r=$(C "cd $V3/roots && md5sum -c --quiet ROOTS_cv5v3_v11.md5 > /dev/null 2>&1 && echo ROOTS_OK; for k in 0 1 2 3 4; do d=cv5v3_v11_f\$k; (cd \$d && md5sum -c --quiet SPLITS.md5 > /dev/null 2>&1 && md5sum -c --quiet DATA_MANIFEST.md5 > /dev/null 2>&1 && cmp -s splits/val.txt splits/test.txt && echo \"f\$k \$(grep -c . splits/train.txt)/\$(grep -c . splits/val.txt)\"); done; grep -v MASKLINKS ROOTS_cv5v3_v11.md5 | md5sum | cut -c1-32") || r=""
ck "cv02 roots: ROOTS_cv5v3_v11.md5 OK; per fold SPLITS + DATA_MANIFEST OK, test = val, train/held-out 425/107 422/110 429/103 431/101 421/111" '[ "$(echo $r | cut -d" " -f1-11)" = "ROOTS_OK f0 425/107 f1 422/110 f2 429/103 f3 431/101 f4 421/111" ]'
ck "cv02 root lists = gaint bench_data_v3b lists (ROOTS file without the MASKLINKS lines)" '[ "$(echo $r | cut -d" " -f12)" = "$(grep -v MASKLINKS /home/noob/work/bench_data_v3b/roots/ROOTS_cv5v3_v11.md5 | md5sum | cut -c1-32)" ]'

echo "--- 4 rendered jobs against the card"
if [ -s $IO/rendered.txt ]; then n=0; e=0
  for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do nm=c3s_swad_v11_f${k}_s$s; n=$((n+1))
    want="$nm|/tmp/noob_el/el-fault-detection/.venv/bin/python -u scripts/train.py --config configs/supervised.yaml --opts $(cd $W && nice -n 19 $P -m bench.cards opts $CARD --seed $s --run-name $nm --data-root $V3/roots/cv5v3_v11_f$k)"
    [ "$(grep "^$nm|" $IO/rendered.txt)" = "$want" ] && grep -q "^dump_$nm|.* --set cv5v3_f$k .* --run-id $nm --device cuda --precision fp32 .*--bench-run dump_$nm\$" $IO/rendered.txt \
      && grep -q "^dump_$nm\.swad|.* --set cv5v3_f$k .* --run-id $nm\.swad --weights-key swad --device cuda --precision fp32 .*--bench-run dump_$nm\.swad\$" $IO/rendered.txt && e=$((e+1)); done; done
  ck "cv02 render: train line = the card as rendered on gaint 89b9ea5, dump lines for <name> and <name>.swad on the run's own fold ($e of $n)" '[ $e = 25 ]'
  ck "cv02 render: no swad dump line carries --logp" '[ "$(grep -E "^dump_c3s_swad" $IO/rendered.txt | grep -c -- " --logp")" = 0 ]'
else skip "no $IO/rendered.txt yet (made by 'c3swad_handover.sh render'); at each start cq.sh itself logs 'config OK (= card)'"; fi

echo "--- 5 names"
names=$(for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do echo -n "c3s_swad_v11_f${k}_s$s "; done; done)
h=$(C "for n in $names; do for b in /tmp/noob_el/bench_*/; do [ -e \$b/experiments/\$n ] || [ -e \$b/experiments/\$n.stdout ] || [ -e \$b/runs/\$n ] && echo \$n; done; ls $BQ/*/pids/\$n.gpu 2>/dev/null; done; ls -d /tmp/noob_el/bench_*/experiments/c3s_* /tmp/noob_el/bench_*/dumps/elbench1/swad_const_pf_v11 2>/dev/null; echo END") || h=""
ck "no swad run name, no c3s_* run and no swad_const dump folder exists on cv02 (experiments, runs, queue dirs, dumps)" '[ "$h" = END ]'
ck "no c3s_* run in a gaint relay dir; relay dir c3swad not yet there or holding only c3s_ runs" '[ -z "$(ls -d /home/noob/work/bench_relay/c3base/c3s_* /home/noob/work/bench_relay/c3hrnet/c3s_* /home/noob/work/bench_relay/rows*/c3s_* 2>/dev/null)" ] && [ -z "$(ls /home/noob/work/bench_relay/c3swad 2>/dev/null | grep -v "^c3s_\|^relay\.")" ]'
ck "the running relays cannot pick the swad names up (^c3_ and ^c3h_ do not match c3s_)" '! echo c3s_swad_v11_f0_s5 | grep -qE "^c3_" && ! echo c3s_swad_v11_f0_s5 | grep -qE "^c3h_" && head -1 /home/noob/work/bench_relay/c3base/relay.log | grep -q "names /^c3_/" && head -1 /home/noob/work/bench_relay/c3hrnet/relay.log | grep -q "names /^c3h_/"'

echo "--- 6 queues on cv02 (one training queue; LPG 1)"
s=$(C "for q in $BQ/*/; do n=\$(basename \$q); p=\$(cat \$q/queue.pid 2>/dev/null); [ -n \"\$p\" ] && kill -0 \$p 2>/dev/null || continue; echo \"\$n MAXC \$(cat \$q/MAXC 2>/dev/null) LPG \$(cat \$q/LPG 2>/dev/null) dispatched \$(grep -c 'cv02 q: all jobs dispatched' \$q/launch.log) HOLD \$(ls \$q/HOLD 2>/dev/null | wc -l)\"; done; echo ---; for f in $BQ/*/pids/*.gpu; do n=\${f%.gpu}; [ -e \$n.end ] || [ -e \$n.rc ] || echo \"GPU \$(cat \$f) \$(basename \$n)\"; done | sort") || s=""
echo "$s" | sed 's/^/     /'
live=$(echo "$s" | sed '/^---$/,$d'); can=$(echo "$live" | awk '$3 != 0 && $7 == 0 {print $1}' | tr '\n' ' ')
ck "live queues that can still start training: '$can' (at most one)" '[ "$(echo $can | wc -w)" -le 1 ]'
ck "LPG is 1 in every live queue" '[ -z "$(echo "$live" | awk "\$5 != 1")" ]'
ck "no GPU carries two of our training runs now" '[ -z "$(echo "$s" | sed "1,/^---\$/d" | cut -d" " -f2 | sort | uniq -d)" ]'

echo "--- 7 disk and guards"
d=$(C "df --output=avail -BG /tmp | tail -1 | tr -dc 0-9; echo; for g in bench_diskguard bench_diskguard2 bench_diskguard3; do tmux has-session -t \"=\$g\" 2>/dev/null && echo \"\$g up\" || echo \"\$g down\"; done") || d=""
cf=$(echo "$d" | head -1); gf=$(df --output=avail -BG /home/noob/work | tail -1 | tr -dc 0-9)
echo "     cv02 /tmp free ${cf:-?} GB; gaint free $gf GB; guards: $(echo "$d" | tail -n +2 | tr '\n' ';')"
ck "cv02 /tmp free >= 45 GB (arm floor)" '[ "${cf:-0}" -ge 45 ]'
ck "gaint free >= 25 GB (relay start floor)" '[ "$gf" -ge 25 ]'
ck "cv02 disk guards 1 and 2 alive" 'echo "$d" | grep -qx "bench_diskguard up" && echo "$d" | grep -qx "bench_diskguard2 up"'
if echo "$d" | grep -qx "bench_diskguard3 up"; then ok "cv02 disk guard 3 alive (covers $NEWQ)"; else skip "cv02 disk guard 3 not started yet ('c3swad_handover.sh guard'; 'arm' refuses without it)"; fi
ck "relays c3base and c3hrnet alive on gaint" 'kill -0 $(cat /home/noob/work/bench_relay/c3base/relay.pid 2>/dev/null) 2>/dev/null && kill -0 $(cat /home/noob/work/bench_relay/c3hrnet/relay.pid 2>/dev/null) 2>/dev/null'

echo "--- 8 harness files"
ck "patch applies to 89b9ea5 (git apply --check on a fresh archive)" 'x=$(mktemp -d) && git -C $R archive 89b9ea5 | tar -x -C $x && (cd $x && git apply --check $HERE/cq_c3swad.patch); rc=$?; rm -rf $x; [ $rc = 0 ]'
ck "read script prints its command (SHOW=1) with the three arms, two pairs, --aa PF:5,6:7,8, cv5v3 groups and the exclude list" 'SHOW=1 bash $HERE/run_read_c3swad.sh | grep -q -- "--pair PF=SWADBN --pair PF=SWAD --labels v11 --workers 8 --cache /home/noob/work/bench_reads/c3swad/cache_c --baseline PF --aa PF:5,6:7,8 --groups /home/noob/work/bench_data_v3b/meta/cv5v3_groups.tsv --score-exclude $T/benchmark/splits/score_exclude_v3.txt"'
ck "no read folder bench_reads/c3swad yet" '[ ! -e /home/noob/work/bench_reads/c3swad ]'
(cd $HERE && md5sum cq_c3swad.patch c3swad_make_jobs.py c3swad_handover.sh diskguard3.sh c3swad_relay.sh run_read_c3swad.sh c3swad_verdict.py c3swad_verdict_test.py c3swad_class_guard.py c3swad_commit.sh c3swad_dumptest.sh c3swad_chain_test.sh c3swad_check.sh | sed 's/^/     /')
echo "[$(date '+%F %T')] C3SWAD CHECK: $NO OK, $NFL FAIL, $NS SKIP"
[ $NFL = 0 ]
