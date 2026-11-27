#!/bin/bash
# Builder's local render smoke of the two T3b queues (gaint CPU; nothing on cv02; pattern of opening_render_smoke.sh): an archive
# of K as the deploy KB in a scratch dir; the T3b roots built by K's real builder on a synthetic ext117 (DATA_T, so cq.sh's
# ROOTS_t3b.md5 / MANIFEST.md5 / per-root SPLITS / DATA_MANIFEST checks run for real); the job lists of t3b_make_jobs.py with
# /tmp/noob_el/ mapped into the scratch dir; K's real cq.sh run render-only (it must stop at the logger check), card calls
# answered by the real python on KB's cards except cfgcheck / validate / cvcard.py (stubbed: the cv02 weights and run configs
# do not exist on gaint); the rendered lines mapped back and checked by t3b_rendercmp.py (templates + semantics).
#   t3b (33 training lines, no SEALED)       -> render compare --kind train
#   t3bopen (30 dump lines, SEALED e1t3b_*)  -> render compare --kind dump (30 fake run dirs hold config_used.yaml + latest.pth)
#   negatives: the dump list without SEALED and the training list with SEALED must be refused (no jobs_rendered.txt).
#   repair (review round 1 N1): a repair list of one fresh line (t3b_half_f2_s6) and one '--resume' line (t3b_deploy_s7, its run
#   dir holding config_used.yaml + latest.pth and no .stdout, as repair_aside leaves it) -> render compare --kind repair;
#   negative: the resume line without latest.pth is refused by cq.sh.
# Usage: bash t3b_render_smoke.sh <out dir>
set -u
OUT=${1:?out dir}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; KT=/home/noob/work/bench_wt_t3b
KC=$(grep -m1 '^KC=' $HERE/t3b_queue.sh | cut -d= -f2 | cut -d';' -f1); K7=${KC:0:7}
S=/home/noob/work/bench_int_io/t3b/render_$$; [ -e $S ] && exit 1; mkdir -p $S/noob_el $OUT || exit 1
B=$S/noob_el/bench_$K7; mkdir -p $B
git -C $KT archive $KC | tar -x -C $B && echo $KC > $B/REVISION
(cd $B && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
cat > $S/python <<EOF
#!/bin/bash
if [ "\$1" = -m ] && [ "\$2" = bench.cards ]; then case "\$3" in validate) exit 0;; cfgcheck) echo "cfgcheck \$*" >> $S/stub.log; echo "config OK (= card)"; exit 0;; esac; fi
case "\$1" in */cvcard.py) exit 0;; esac
exec $P "\$@"
EOF
chmod +x $S/python
D=$S/noob_el/bench_data; mkdir -p $D/meta $D/roots; echo x > $D/meta/forbidden_v1.txt
(cd $D && md5sum meta/forbidden_v1.txt > DEPLOY.md5); echo r > $D/roots/x; (cd $D/roots && md5sum x > ROOTS_cv5v2_v11.md5 && md5sum x > ROOTS_cv5v2_v1.md5)
nice -n 19 $P $HERE/t3b_smoke_synth.py ext $S/ext117 > /dev/null
(cd $S/ext117 && for s in $(grep . stems_eval.txt); do md5sum images/$s.png masks/$s.png ignore/$s.png; done) > $S/e1.md5
(cd $KT && nice -n 19 $P scripts/bench_make_t3b_roots.py --split /home/noob/work/bench_data_v3b/meta/cv5v3.json --forbidden /home/noob/work/bench_data_v3b/meta/forbidden_v1.txt \
  --legacy-splits $KT/data/splits --labeled /home/noob/work/el-fault-detection/data/labeled --train-masks /home/noob/work/bench_data/masks_v11/masks \
  --e1 $S/ext117 --e1-manifest $S/e1.md5 --lists $HERE/lists --out $S/noob_el/bench_data_t3b) | tail -2 | tee $OUT/render_smoke.out
$P $HERE/t3b_make_jobs.py --k $KC --train $S/jobs_train.txt --dump $S/jobs_dump.txt | tee -a $OUT/render_smoke.out
for r in $(cut -d'|' -f9 $S/jobs_dump.txt | awk '{print $2}' | xargs -n1 basename); do mkdir -p $B/experiments/$r/checkpoints
  echo "run_name: $r" > $B/experiments/$r/config_used.yaml; echo w > $B/experiments/$r/checkpoints/latest.pth; done
DS=$S/noob_el/bench_data_sealed; mkdir -p $DS/e1_106/images; cp $HERE/lists/e1_106_stems.txt $DS/e1_106/stems_eval.txt
(cd $DS && find . -type f ! -name MANIFEST.md5 -printf '%P\n' | sort | xargs md5sum > MANIFEST.md5); SMAN=$(md5sum < $DS/MANIFEST.md5 | cut -c1-32)
sed 's#^\. /tmp/noob_el/env.sh.*#:#' $B/bench/q/cv02/cq.sh > $S/cq.sh
rq(){ # list sealed(0|1) qdir
  local Q=$3; mkdir -p $Q; sed "s#/tmp/noob_el/#$S/noob_el/#g" $1 > $Q/jobs.txt; echo 1 > $Q/LPG
  [ $2 = 1 ] && { for k in 0 1 2 3 4; do echo "e1t3b_f$k e1_open9_t3b"; done; echo "manifest $SMAN"; } > $Q/SEALED
  B=$B Q=$Q JOBS_MD5=$(md5sum < $Q/jobs.txt | cut -c1-32) DEPLOY=$KC DATA_MD5=$(md5sum < $D/DEPLOY.md5 | cut -c1-32) DATA=$D \
    DATA_V3=$S/noob_el/bench_data_v3b DATA_F=$S/noob_el/bench_data_fin DATA_T=$S/noob_el/bench_data_t3b DUMPOF_ROOT=$S/noob_el DATA_S=$DS P=$S/python bash $S/cq.sh
  echo "rc $?; last line: $(tail -1 $Q/launch.log | cut -c23-)"; }
rc_all=0
for kind in train dump; do
  sl=0; [ $kind = dump ] && sl=1
  echo "$kind: cq.sh $(rq $S/jobs_$kind.txt $sl $S/q_$kind)" | tee -a $OUT/render_smoke.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" <(tail -1 $S/q_$kind/launch.log) || rc_all=1
  sed -e "s#$S/python#/tmp/noob_el/el-fault-detection/.venv/bin/python#g" -e "s#$S/noob_el/#/tmp/noob_el/#g" $S/q_$kind/jobs_rendered.txt > $OUT/rendered_$kind.txt
  $P $HERE/t3b_rendercmp.py --kind $kind --jobs $S/jobs_$kind.txt --rendered $OUT/rendered_$kind.txt --b /tmp/noob_el/bench_$K7 --repo $KT | tee -a $OUT/render_smoke.out
  [ ${PIPESTATUS[0]} = 0 ] || rc_all=1
  echo "cfgcheck calls ($kind): $(grep -c cfgcheck $S/stub.log 2>/dev/null)" | tee -a $OUT/render_smoke.out; : > $S/stub.log
done
grep '^t3b_half_f2_s6|' $S/jobs_train.txt > $S/jobs_repair.txt; grep '^t3b_deploy_s7|' $S/jobs_train.txt | awk -F'|' 'BEGIN{OFS="|"} {$9="--resume"; print}' >> $S/jobs_repair.txt
mkdir -p $B/experiments/t3b_deploy_s7/checkpoints; echo "run_name: t3b_deploy_s7" > $B/experiments/t3b_deploy_s7/config_used.yaml; echo w > $B/experiments/t3b_deploy_s7/checkpoints/latest.pth
echo "repair: cq.sh $(rq $S/jobs_repair.txt 0 $S/q_repair)" | tee -a $OUT/render_smoke.out
grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" <(tail -1 $S/q_repair/launch.log) || rc_all=1
sed -e "s#$S/python#/tmp/noob_el/el-fault-detection/.venv/bin/python#g" -e "s#$S/noob_el/#/tmp/noob_el/#g" $S/q_repair/jobs_rendered.txt > $OUT/rendered_repair.txt
$P $HERE/t3b_rendercmp.py --kind repair --jobs $S/jobs_repair.txt --rendered $OUT/rendered_repair.txt --b /tmp/noob_el/bench_$K7 --repo $KT | tee -a $OUT/render_smoke.out
[ ${PIPESTATUS[0]} = 0 ] || rc_all=1
grep -c -- ' --resume --config ' $OUT/rendered_repair.txt | sed 's/^/rendered --resume lines: /' | tee -a $OUT/render_smoke.out
rm $B/experiments/t3b_deploy_s7/checkpoints/latest.pth
echo "negative resume line without latest.pth: cq.sh $(rq $S/jobs_repair.txt 0 $S/qn_repair)" | tee -a $OUT/render_smoke.out; [ -e $S/qn_repair/jobs_rendered.txt ] && rc_all=1
cp $S/jobs_repair.txt $OUT/
echo "negative dump list without SEALED: cq.sh $(rq $S/jobs_dump.txt 0 $S/qn_dump)" | tee -a $OUT/render_smoke.out; [ -e $S/qn_dump/jobs_rendered.txt ] && rc_all=1
echo "negative training list with SEALED: cq.sh $(rq $S/jobs_train.txt 1 $S/qn_train)" | tee -a $OUT/render_smoke.out; [ -e $S/qn_train/jobs_rendered.txt ] && rc_all=1
cp $S/jobs_train.txt $S/jobs_dump.txt $OUT/
echo "render smoke rc $rc_all" | tee -a $OUT/render_smoke.out
rm -rf $S
exit $rc_all
