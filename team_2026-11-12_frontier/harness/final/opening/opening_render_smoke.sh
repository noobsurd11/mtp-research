#!/bin/bash
# Builder's local render smoke of the sealed-opening queue (gaint CPU; nothing on cv02): an archive of G as the deploy B in a
# scratch dir, the real job lists (both C1-D4 variants) with /tmp/noob_el/ mapped into the scratch dir, G's real cq.sh run
# render-only (it must stop at the logger check), card calls answered by the real python on B's cards except cfgcheck /
# validate / cvcard.py (stubbed: the cv02 weights files and run configs do not exist on gaint), then the rendered lines are
# mapped back to the cv02 paths and checked by opening_rendercmp.py (templates + semantics). Also a negative: the same list
# without Q/SEALED must be refused. Usage: bash opening_render_smoke.sh <G commit> <out dir>
set -u
G=${1:?G commit}; OUT=${2:?out dir}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python
S=/home/noob/work/bench_int_io/opening/render_smoke_$$; [ -e $S ] && exit 1
mkdir -p $S/noob_el $OUT || exit 1
B=$S/noob_el/bench_${G:0:7}; mkdir -p $B
git -C /home/noob/work/bench_wt_openg archive $G | tar -x -C $B && echo $G > $B/REVISION
(cd $B && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
cat > $S/python <<EOF
#!/bin/bash
# stub: bench.cards validate / cfgcheck answered OK (logged); cvcard.py prints no weights; everything else is the real python
if [ "\$1" = -m ] && [ "\$2" = bench.cards ]; then case "\$3" in validate) exit 0;; cfgcheck) echo "cfgcheck \$*" >> $S/stub.log; echo "config OK (= card)"; exit 0;; esac; fi
case "\$1" in */cvcard.py) exit 0;; esac
exec $P "\$@"
EOF
chmod +x $S/python
D=$S/noob_el/bench_data; mkdir -p $D/meta $D/roots; echo x > $D/meta/forbidden_v1.txt
(cd $D && md5sum meta/forbidden_v1.txt > DEPLOY.md5); echo r > $D/roots/x; (cd $D/roots && md5sum x > ROOTS_cv5v2_v11.md5 && md5sum x > ROOTS_cv5v2_v1.md5)
F=$S/noob_el/bench_data_fin/roots/pool532_v11; mkdir -p $F/splits
for f in train val test; do echo "c_$f" > $F/splits/$f.txt; done; cp $F/splits/val.txt $F/splits/test.txt
(cd $F && md5sum splits/train.txt splits/val.txt splits/test.txt > SPLITS.md5 && md5sum splits/train.txt > DATA_MANIFEST.md5)
(cd $S/noob_el/bench_data_fin/roots && md5sum pool532_v11/SPLITS.md5 > ROOTS_pool532_v11.md5)
for r in fin_hrnet_swad_v11_pool_s{5..9} fin_pf_v11_pool_s{5..9}; do mkdir -p $S/noob_el/bench_9967d59/experiments/$r/checkpoints
  echo "run_name: $r" > $S/noob_el/bench_9967d59/experiments/$r/config_used.yaml; echo w > $S/noob_el/bench_9967d59/experiments/$r/checkpoints/latest.pth; done
DS=$S/noob_el/bench_data_sealed; mkdir -p $DS/e1_106/images $DS/legacy/images; echo s > $DS/e1_106/stems_eval.txt
(cd $DS && find . -type f ! -name MANIFEST.md5 -printf '%P\n' | sort | xargs md5sum > MANIFEST.md5); SMAN=$(md5sum < $DS/MANIFEST.md5 | cut -c1-32)
rc_all=0
for v in no yes; do
  J=$HERE/jobs/jobs_open_c1d4_$v.txt; Q=$S/q_$v; mkdir -p $Q
  sed "s#/tmp/noob_el/#$S/noob_el/#g" $J > $Q/jobs.txt; echo 1 > $Q/LPG
  printf 'e1_106 e1_open8_final\ntest50 t50_open19_final\nmanifest %s\n' $SMAN > $Q/SEALED
  sed 's#^\. /tmp/noob_el/env.sh.*#:#' $B/bench/q/cv02/cq.sh > $S/cq.sh
  B=$B Q=$Q JOBS_MD5=$(md5sum < $Q/jobs.txt | cut -c1-32) DEPLOY=$G DATA_MD5=$(md5sum < $D/DEPLOY.md5 | cut -c1-32) DATA=$D \
    DATA_V3=$S/noob_el/bench_data_v3b DATA_F=$S/noob_el/bench_data_fin DUMPOF_ROOT=$S/noob_el DATA_S=$DS P=$S/python bash $S/cq.sh
  echo "c1d4 $v: cq.sh rc $?; last line: $(tail -1 $Q/launch.log | cut -c23-)" | tee -a $OUT/render_smoke.out
  grep -q "gpumem logger (cq_gpumem.sh) not running; not starting" <(tail -1 $Q/launch.log) || rc_all=1
  sed -e "s#$S/python#/tmp/noob_el/el-fault-detection/.venv/bin/python#g" -e "s#$S/noob_el/#/tmp/noob_el/#g" $Q/jobs_rendered.txt > $OUT/rendered_c1d4_$v.txt
  $P $HERE/opening_rendercmp.py --jobs $J --rendered $OUT/rendered_c1d4_$v.txt --b /tmp/noob_el/bench_${G:0:7} | tee -a $OUT/render_smoke.out
  [ ${PIPESTATUS[0]} = 0 ] || rc_all=1
  echo "cfgcheck calls: $(grep -c cfgcheck $S/stub.log)" | tee -a $OUT/render_smoke.out; : > $S/stub.log
  # negative: the same list without SEALED is refused
  Qn=$S/qn_$v; mkdir -p $Qn; cp $Q/jobs.txt $Q/LPG $Qn/
  B=$B Q=$Qn JOBS_MD5=$(md5sum < $Qn/jobs.txt | cut -c1-32) DEPLOY=$G DATA_MD5=$(md5sum < $D/DEPLOY.md5 | cut -c1-32) DATA=$D \
    DATA_V3=$S/noob_el/bench_data_v3b DATA_F=$S/noob_el/bench_data_fin DUMPOF_ROOT=$S/noob_el DATA_S=$DS P=$S/python bash $S/cq.sh
  echo "negative (no SEALED) c1d4 $v: rc $?; $(tail -1 $Qn/launch.log | cut -c23-)" | tee -a $OUT/render_smoke.out
  [ -e $Qn/jobs_rendered.txt ] && rc_all=1
done
echo "render smoke rc $rc_all" | tee -a $OUT/render_smoke.out
rm -rf $S
exit $rc_all
