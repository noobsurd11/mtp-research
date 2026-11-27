#!/bin/bash
# c3x: render-only run of the REAL cq.sh of the c3x tree on gaint (= harness/c3swad/evidence/render_gaint.sh 5c616ea8 with
# B = QC = the c3x tree, as on cv02; the env.sh line and cvcard.py skipped as there: the cv02 weights path does not exist on
# gaint). cq.sh stops at the logger check. Then every rendered line is compared with cv02 c3all3's own jobs_rendered.txt:
#   train line of c3x f<k> s<s>  minus the 8 swad opts, run name -> c3h_hrnet_w18_unetpp_pf_f<k>_s<s>  ==  c3all3's HRNet line
#     (the 12 HRNet jobs still in c3all3: f3,f4 s7 and s8, s9);
#   both dump lines of c3x f<k> s<s>  with deploy dir, method dir, card and name mapped to the swad run  ==  c3all3's two swad
#     dump lines of c3s_swad_v11_f<k>_s<s> (all 25).
# Env: S (scratch dir), XT (archive of the c3x commit with REVISION and CODE.md5), X (full commit), JOBS (jobs.txt from
#   c3x_make_jobs.py), C3 (copy of cv02 c3all3 jobs_rendered.txt). Writes only under S/rx.
set -u
S=${S:?}; XT=${XT:?}; X=${X:?}; JOBS=${JOBS:?}; C3=${C3:?}; R=$S/rx; P0=/home/noob/work/el-fault-detection/.venv/bin/python
[ -e $R ] && { echo "REFUSED: $R exists"; exit 1; }
mkdir -p $R/data/meta $R/q; export CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1
cp -r $XT $R/B
sed -i 's#^\. /tmp/noob_el/env\.sh.*#:#' $R/B/bench/q/cv02/cq.sh
(cd $R/B && find . -type f -printf '%P\n' | grep -vx CODE.md5 | sort | xargs -d '\n' md5sum > CODE.md5)
ln -s /home/noob/work/bench_data/roots $R/data/roots; echo x > $R/data/meta/forbidden_v1.txt; (cd $R/data && md5sum meta/forbidden_v1.txt > DEPLOY.md5)
printf '#!/bin/bash\ncase "$1" in */cvcard.py) exit 0;; esac\nexec %s "$@"\n' $P0 > $R/python; chmod +x $R/python
sed 's#/tmp/noob_el/bench_data_v3b/#/home/noob/work/bench_data_v3b/#' $JOBS > $R/q/jobs.txt; echo 1 > $R/q/LPG
echo "[$(date '+%F %T')] render start: $(wc -l < $R/q/jobs.txt) jobs, B = QC = $R/B (REVISION $(cat $R/B/REVISION))"
B=$R/B Q=$R/q JOBS_MD5=$(md5sum < $R/q/jobs.txt | cut -c1-32) DEPLOY=$X DATA_MD5=$(md5sum < $R/data/DEPLOY.md5 | cut -c1-32) \
  DATA=$R/data DATA_V3=/home/noob/work/bench_data_v3b P=$R/python nice -n 19 bash $R/B/bench/q/cv02/cq.sh > $R/stdout 2>&1
echo "[$(date '+%F %T')] rc=$? last log line: $(tail -1 $R/q/launch.log | cut -c23-200)"
XD=/tmp/noob_el/bench_${X:0:7}
sed "s#$R/python#/tmp/noob_el/el-fault-detection/.venv/bin/python#g; s#$R/B/#$XD/#g; s#$R/data/#/tmp/noob_el/bench_data/#g; s#/home/noob/work/bench_data_v3b/#/tmp/noob_el/bench_data_v3b/#g" $R/q/jobs_rendered.txt > $R/rendered_cv02paths.txt
echo "rendered $(wc -l < $R/rendered_cv02paths.txt) lines (25 train + 25 dump + 25 dump .swad expected); --logp in $(grep -c -- ' --logp' $R/rendered_cv02paths.txt)"
OPTS8=" training.lr_scheduler=constant training.weight_avg.swad.mode=uniform training.weight_avg.swad.start=10000 training.weight_avg.swad.end=20000 training.weight_avg.ema_9998.mode=ema training.weight_avg.ema_9998.decay=0.9998 training.bn_recal=true training.enc_probe_every=2000"
nt=0; et=0; nd=0; ed=0; bad=0
for s in 5 6 7 8 9; do for k in 0 1 2 3 4; do n=c3x_hrnet_swad_v11_f${k}_s$s; h=c3h_hrnet_w18_unetpp_pf_f${k}_s$s; w=c3s_swad_v11_f${k}_s$s
  t=$(grep -F "$n|" $R/rendered_cv02paths.txt | grep "^$n|")
  case "$t" in *"$OPTS8 data.root="*) ;; *) echo "FAIL train line of $n lacks the 8 opts before data.root"; bad=$((bad+1));; esac
  ref=$(grep "^$h|" $C3)
  if [ -n "$ref" ]; then nt=$((nt+1)); m=${t//$OPTS8/}; m=${m//$n/$h}; [ "$m" = "$ref" ] && et=$((et+1)) || { echo "FAIL train $n vs $h"; bad=$((bad+1)); }; fi
  for sfx in "" ".swad"; do nd=$((nd+1))
    d=$(grep "^dump_$n$sfx|" $R/rendered_cv02paths.txt); ref=$(grep "^dump_$w$sfx|" $C3)
    m=${d//$XD\//\/tmp\/noob_el\/bench_89b9ea5\/}; m=${m//--method hrnet_w18_unetpp_swad_const_pf_v11/--method swad_const_pf_v11}
    m=${m//bench\/methods\/hrnet_w18_unetpp_swad_const_pf_v11.yaml/bench\/methods\/swad_const_pf_v11.yaml}; m=${m//$n/$w}
    [ -n "$ref" ] && [ "$m" = "$ref" ] && ed=$((ed+1)) || { echo "FAIL dump_$n$sfx vs dump_$w$sfx"; bad=$((bad+1)); }
  done; done; done
echo "train lines: $et of $nt c3x lines with an HRNet twin in c3all3 equal it after removing the 8 opts and renaming; all 25 hold the 8 opts before data.root"
echo "dump lines: $ed of $nd c3x dump lines equal c3all3's swad dump line of the same fold and seed after mapping deploy dir, method, card and name"
echo "cv02 c3all3 jobs_rendered.txt md5 $(md5sum < $C3 | cut -c1-8), $(wc -l < $C3) lines"
grep -E '^(dump_)?c3x_hrnet_swad_v11_f0_s5(\.swad)?\|' $R/rendered_cv02paths.txt
echo "render check: $bad FAIL"
