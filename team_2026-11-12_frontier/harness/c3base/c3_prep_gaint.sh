#!/bin/bash
# integrator c3base: PREPARE (never arm) the gaint fallback queue /home/noob/work/bq/c3base in the bench_setup.sh layout
# (jobs.txt + MAXC, dump/jobs.txt + dump/MAXC, launch.sh carrying the pins, prep.log). Refuses if the dir exists, the deploy
# worktree is not at DEPLOY or has a tracked change, or any job's experiments/<name> exists. Job files chmod a-w.
# Usage: DEPLOY=<full commit> bash c3_prep_gaint.sh
set -u
DEPLOY=${DEPLOY:?full commit}; R=/home/noob/work/bench_wt_final; Q=/home/noob/work/bq/c3base
H=/home/yugma/mtp/research/team_2026-11-12_frontier/harness/c3base; P=/home/noob/work/el-fault-detection/.venv/bin/python
no(){ echo "prep: REFUSED: $*"; exit 1; }
[ -e $Q ] && no "$Q exists"
[ "$(git -C $R rev-parse HEAD)" = "$DEPLOY" ] || no "$R HEAD != $DEPLOY"
[ -z "$(git -C $R status --short --untracked-files=no)" ] || no "$R has tracked changes"
mkdir -p $Q/dump
$P $H/make_jobs.py gaint $Q/jobs.txt $Q/dump/jobs.txt || no "make_jobs failed"
for n in $(cut -d'|' -f1 $Q/jobs.txt $Q/dump/jobs.txt); do [ -e $R/experiments/$n ] || [ -e $R/experiments/$n.stdout ] && no "experiments/$n exists"; done
echo 2 > $Q/MAXC; echo 1 > $Q/dump/MAXC
J=$(md5sum < $Q/jobs.txt | cut -c1-32); DJ=$(md5sum < $Q/dump/jobs.txt | cut -c1-32)
cat > $Q/launch.sh <<EOF
#!/bin/bash
# cv5v3 baselines, gaint FALLBACK queue (prepared by harness/c3base/c3_prep_gaint.sh, integrator c3base, $(date '+%d %b %Y %H:%M')).
# Never arm it together with the cv02 queue /tmp/noob_el/bench_q/c3base (same run names c3_*). The lead arms it ONCE, only on
# a free gaint GPU slot (after the running gaint chains have written 'chain done'). bench_setup.sh refuses (nothing started) if
# the session exists, this dir is armed or used, an md5 or HEAD differs, a tracked change exists, or any experiments/<job> exists.
export Q=$Q SES=bench_q_c3base DEPLOY=$DEPLOY \\
  JOBS_MD5=$J DJOBS_MD5=$DJ REPO=$R MAXH=120
exec bash \$REPO/bench/q/bench_setup.sh
EOF
chmod a-w $Q/jobs.txt $Q/dump/jobs.txt $Q/launch.sh
LM=$(md5sum < $Q/launch.sh | cut -c1-32)
echo "prep c3base $(date '+%F %T') by harness/c3base/c3_prep_gaint.sh $(md5sum < $0 | cut -c1-8) + make_jobs.py $(md5sum < $H/make_jobs.py | cut -c1-8); REPO $R HEAD $DEPLOY clean
jobs.txt $J ($(grep -c . $Q/jobs.txt) lines) MAXC 2; dump/jobs.txt $DJ ($(grep -c . $Q/dump/jobs.txt) lines) dump/MAXC 1; launch.sh $LM" | tee $Q/prep.log
