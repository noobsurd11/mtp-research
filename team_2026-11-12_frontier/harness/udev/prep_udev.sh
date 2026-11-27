#!/bin/bash
# Unseen-module block (integrator udev, 15 Nov 2026): PREPARE one gaint queue dir in the bench_setup.sh layout. Arms nothing,
# starts no tmux session, no GPU. Usage: bash prep_udev.sh {loso2|infer|tta_path|tta|tta_f51}
#   loso2    -> /home/noob/work/bq/udev_loso2   jobs.txt = stage B loso2 list (12 runs) unchanged; dump/jobs.txt = the
#               12 held-out dumps with --logp added (canonical fp32 + float16 logp); MAXC 2, dump/MAXC 1
#   infer    -> /home/noob/work/bq/udev_infer   jobs.txt = jobs_v2 udev_infer list (174 dump-only lines) unchanged; MAXC 1
#   tta_path -> /home/noob/work/bq/udev_tta_path jobs.txt = line 1 of the B5 TTA list (pathfinder); MAXC 1
#   tta      -> /home/noob/work/bq/udev_tta     jobs.txt = B5 TTA lines 2-65 + B5 pool list (16) = 80 lines; MAXC 1;
#               TTA_GATE=<MiB> (optional, >= 6200) sets field 5 of every line (after the pathfinder's peak is read)
#   tta_f51  -> /home/noob/work/bq/udev_tta_f51 jobs.txt = B5 F51 list (20 lines; paired read needs stage A7's plain F51
#               dumps); MAXC 1; TTA_GATE as for tta
# Every list is re-rendered at REPO (= DEPLOY, clean) by the stage B generators into a fresh temp dir and must be byte-equal
# to the pinned stage B list; the derived list is checked against its source line by line. Job files are made read-only,
# a launch.sh with the md5 pins is written into the queue dir, and the md5s are printed.
set -eu
WHAT=${1:?loso2|infer|tta_path|tta|tta_f51}
REPO=/home/noob/work/bench_wt_udev; DEPLOY=ae4dd1094972d00bb55000d76f94598b946a1b68
P=/home/noob/work/el-fault-detection/.venv/bin/python; BQ=/home/noob/work/bq; B=/home/noob/work/bench_udev
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
die(){ echo "prep_udev: REFUSED: $*"; exit 1; }
md5(){ md5sum < "$1" | cut -c1-32; }
[ "$(git -C $REPO rev-parse HEAD)" = "$DEPLOY" ] || die "$REPO HEAD != $DEPLOY"
[ -z "$(git -C $REPO status --porcelain -uno)" ] || die "$REPO has tracked changes"
declare -A PIN=([udev:loso2/jobs.txt]=6c07b4db98137a4881a18c8ac3879307 [udev:loso2/dump/jobs.txt]=33c2af8a10ee1fd15f2a895bbc9b2053
  [udev:udev_infer/jobs.txt]=1bcb077e456e59dab65a54ad4e23ba55 [tta:tta/jobs.txt]=b0ef79e7cf535ac4742e05b11bcc3990
  [tta:tta/pool/jobs.txt]=ecccf3b6ede8463ad2e329ab9bd86f56 [tta:tta/f51/jobs.txt]=ea13248c07eed960558aa80b5cbdba06)
TMP=$(mktemp -d /home/noob/work/bench_int_io/prep_XXXXXX)
(cd $REPO && nice -n 19 $P scripts/bench_udev_jobs.py --out $TMP/udev --repo $REPO > $TMP/udev.out && \
             nice -n 19 $P scripts/bench_tta_jobs.py --out $TMP/tta --repo $REPO > $TMP/tta.out) || die "generator failed ($TMP)"
for k in "${!PIN[@]}"; do f=$TMP/${k%%:*}/${k#*:}
  [ "$(md5 $f)" = "${PIN[$k]}" ] || die "re-rendered $k md5 $(md5 $f) != pinned ${PIN[$k]}"
  case $k in udev:*) s=$B/jobs_v2/${k#*:};; tta:*) s=$B/jobs_tta/${k#*:};; esac
  [ "$(md5 $s)" = "${PIN[$k]}" ] || die "stage B file $s md5 != pinned"; done
gate_set(){  # file -> file with field 5 = TTA_GATE (if set)
  if [ -n "${TTA_GATE:-}" ]; then case "$TTA_GATE" in *[!0-9]*) die "TTA_GATE not a number";; esac
    [ "$TTA_GATE" -ge 6200 ] || die "TTA_GATE < 6200"; awk -F'|' -v OFS='|' -v g=$TTA_GATE '{$5=g; print}' "$1"; else cat "$1"; fi; }
case $WHAT in
  loso2)    Q=$BQ/udev_loso2; SES=bench_q_udev_loso2; MAXC=2; DMAXC=1;;
  infer)    Q=$BQ/udev_infer; SES=bench_q_udev_infer; MAXC=1; DMAXC=;;
  tta_path) Q=$BQ/udev_tta_path; SES=bench_q_udev_tta_path; MAXC=1; DMAXC=;;
  tta)      Q=$BQ/udev_tta; SES=bench_q_udev_tta; MAXC=1; DMAXC=;;
  tta_f51)  Q=$BQ/udev_tta_f51; SES=bench_q_udev_tta_f51; MAXC=1; DMAXC=;;
  *) die "unknown $WHAT";; esac
[ ! -e $Q ] || die "$Q exists"
for n in $(case $WHAT in loso2) cut -d'|' -f1 $TMP/udev/loso2/jobs.txt $TMP/udev/loso2/dump/jobs.txt;; infer) cut -d'|' -f1 $TMP/udev/udev_infer/jobs.txt;;
           tta_path|tta) cut -d'|' -f1 $TMP/tta/tta/jobs.txt $TMP/tta/tta/pool/jobs.txt;; tta_f51) cut -d'|' -f1 $TMP/tta/tta/f51/jobs.txt;; esac); do
  [ -e $REPO/experiments/$n ] || [ -e $REPO/experiments/$n.stdout ] && die "experiments/$n exists"; done
mkdir -p $Q
case $WHAT in
  loso2)
    cp $TMP/udev/loso2/jobs.txt $Q/jobs.txt; mkdir -p $Q/dump
    sed 's/ --bench-run / --logp --bench-run /' $TMP/udev/loso2/dump/jobs.txt > $Q/dump/jobs.txt
    [ "$(grep -c -- ' --precision fp32 .* --logp --bench-run ' $Q/dump/jobs.txt)" = 12 ] || die "logp not on every dump line"
    [ "$(sed 's/ --logp --bench-run / --bench-run /' $Q/dump/jobs.txt | md5sum | cut -c1-32)" = 33c2af8a10ee1fd15f2a895bbc9b2053 ] || die "dump list differs beyond --logp"
    echo $DMAXC > $Q/dump/MAXC;;
  infer)    cp $TMP/udev/udev_infer/jobs.txt $Q/jobs.txt;;
  tta_path) head -n 1 $TMP/tta/tta/jobs.txt > $Q/jobs.txt
            case "$(cut -d'|' -f1 $Q/jobs.txt)" in ttapath_d4ms_cv5v2_f0_w1g_pf_v11_f0_s5) ;; *) die "line 1 is not the pathfinder";; esac;;
  tta)      { tail -n +2 $TMP/tta/tta/jobs.txt; cat $TMP/tta/tta/pool/jobs.txt; } > $TMP/tta_rest.txt; gate_set $TMP/tta_rest.txt > $Q/jobs.txt
            [ "$(wc -l < $Q/jobs.txt)" = 80 ] || die "tta rest != 80 lines";;
  tta_f51)  gate_set $TMP/tta/tta/f51/jobs.txt > $Q/jobs.txt; [ "$(wc -l < $Q/jobs.txt)" = 20 ] || die "f51 != 20 lines";;
esac
echo $MAXC > $Q/MAXC
grep -qE -- '--set (test50|e1_106)|sealed' $Q/jobs.txt $( [ -e $Q/dump/jobs.txt ] && echo $Q/dump/jobs.txt ) && die "sealed set name in a list"
J=$(md5 $Q/jobs.txt); DJ=; [ -e $Q/dump/jobs.txt ] && DJ=$(md5 $Q/dump/jobs.txt)
chmod a-w $Q/jobs.txt; [ -e $Q/dump/jobs.txt ] && chmod a-w $Q/dump/jobs.txt
cat > $Q/launch.sh <<EOF
#!/bin/bash
# Unseen-module block, queue $WHAT (prepared by harness/udev/prep_udev.sh, integrator udev, $(date '+%d %b %Y %H:%M')). The lead arms
# it ONCE, only after the previous gaint chain has written 'chain done' (LAUNCH_REQUEST_udev.md). bench_setup.sh refuses
# (nothing started) if the session exists, this dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any
# experiments/<job> exists.
export Q=$Q SES=$SES DEPLOY=$DEPLOY \\
  JOBS_MD5=$J${DJ:+ DJOBS_MD5=$DJ} REPO=$REPO MAXH=120
exec bash \$REPO/bench/q/bench_setup.sh
EOF
chmod a-w $Q/launch.sh
{ echo "prep $WHAT $(date '+%F %T') by harness/udev/prep_udev.sh $(md5 $0 | cut -c1-8); REPO $REPO HEAD $DEPLOY clean; generators re-rendered all six stage B lists byte-equal (tmp $TMP)"
  echo "jobs.txt $J ($(wc -l < $Q/jobs.txt) lines) MAXC $MAXC${DJ:+; dump/jobs.txt $DJ ($(wc -l < $Q/dump/jobs.txt) lines) dump/MAXC $DMAXC}; launch.sh $(md5 $Q/launch.sh)"; } | tee $Q/prep.log
rm -rf $TMP
