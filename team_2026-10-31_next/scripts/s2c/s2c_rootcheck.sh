#!/bin/bash
# runner (3 Nov 2026): SKR2C data-root verification on gaint CPU (as B6 §2-4; no GPU, no training run, nothing in s2c/).
# 1. s2c_make_root.sh -> /home/noob/work/s2c_root (refuses if it exists).
# 2. s2c_databuild_check.py per arm (SUPPF el_f3 / SKR01 el_thin): control lines + config text = the s5 run's; root lines / counts /
#    test = val / config diff = data.root only.
# 3. identity_cpu.py 962379a6 (judge B6-4 harness; = el_thin scripts/thin/identity_cpu.py), 5 CPU fp32 steps per arm,
#    A data.root=data vs B data.root=<root>, the s5 opts: the records must be equal apart from 'opts'.
# 4. The queue's cfgcheck diff of each <arm>_root_config.yaml vs pf2_SUPPF_100pct_s5 config_used.yaml = the exp_<arm>.txt to use.
# v2: an existing root is verified, not rebuilt; per-step wall 'sec' is excluded from the identity compare (timing).
# nice 19, 8 threads, CUDA hidden. Own PID -> <O>/rootcheck.pid; log <O>/rootcheck.log; rc captured before $(date).
set -u
O=/home/noob/work/s2c_check; S=$O/scripts; R=/home/noob/work/s2c_root; P=/home/noob/work/el-fault-detection/.venv/bin/python
R0=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml; L=$O/rootcheck.log
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
echo $$ > $O/rootcheck.pid; lg(){ echo "[$(date '+%F %T')] $*" >> $L; }
lg "start pid $$"
[ "$(md5sum < $S/identity_cpu.py | cut -c1-8)" = 962379a6 ] || { lg "identity_cpu md5 FAIL"; exit 1; }
if [ -e $R ]; then  # v2: re-run on the existing root: verify it instead of rebuilding
  (cd $R/splits && md5sum -c --quiet ../SPLITS.md5) && cmp $R/splits/test.txt $R/splits/val.txt && [ "$(readlink $R/labeled)" = /home/noob/work/el-fault-detection/data/labeled ]; rc=$?
  lg "existing root verified (SPLITS.md5 $(md5sum < $R/SPLITS.md5 | cut -c1-8) -c, test = val, labeled link) rc=$rc"; [ $rc = 0 ] || exit 1
else nice -n 19 bash $S/s2c_make_root.sh >> $L 2>&1; rc=$?; lg "make_root rc=$rc"; [ $rc = 0 ] || exit 1; fi
for arm in SUPPF SKR01; do
  nice -n 19 $P $S/s2c_databuild_check.py --arm $arm --root $R --out $O/databuild --threads 8 >> $L 2>&1; rc=$?; lg "databuild $arm rc=$rc"; [ $rc = 0 ] || exit 1
done
J=/home/noob/work/el_f3/reports/pf2/pf2_jobs.txt; JS=/home/noob/work/s2q/s2q_jobs.txt
declare -A CODE=([SUPPF]=/home/noob/work/el_f3 [SKR01]=/home/noob/work/el_thin)
declare -A OPTS=([SUPPF]="$(grep '^pf2_SUPPF_100pct_s5|' $J | cut -d'|' -f4)" [SKR01]="$(grep '^skr2_SKR01_100pct_s5|' $JS | cut -d'|' -f4)")
mkdir -p $O/idchk
for arm in SUPPF SKR01; do
  nice -n 19 $P $S/identity_cpu.py --code ${CODE[$arm]} --out $O/idchk/${arm}_A_data.json --steps 5 --threads 8 --opts ${OPTS[$arm]} > $O/idchk/${arm}_A.log 2>&1; rc=$?; lg "identity $arm A (data.root=data) rc=$rc"; [ $rc = 0 ] || exit 1
  nice -n 19 $P $S/identity_cpu.py --code ${CODE[$arm]} --out $O/idchk/${arm}_B_root.json --steps 5 --threads 8 --opts ${OPTS[$arm]} data.root=$R > $O/idchk/${arm}_B.log 2>&1; rc=$?; lg "identity $arm B (data.root=$R) rc=$rc"; [ $rc = 0 ] || exit 1
  $P -I -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); oa=a.pop("opts"); ob=b.pop("opts")
assert ob == oa + ["data.root=" + sys.argv[3]], "opts"
sa = [x.pop("sec") for x in a["steps"]]; sb = [x.pop("sec") for x in b["steps"]]  # wall seconds per step: timing, not compared
assert a == b, sorted(k for k in a if a[k] != b.get(k))
s = a["steps"][-1]; print("IDENTICAL (all fields but wall sec/step: A %s, B %s) over %d steps: init %s, counts %s, fixed batch %s / %s, step-%d loss %s, state %s, logits %s" % (sa, sb, len(a["steps"]), a["init_state"], a["class_counts_sha"], a["fixed_batch"]["image"], a["fixed_batch"]["mask"], s["step"], s["out"].get("loss"), s["state"], s["logits"]))' \
    $O/idchk/${arm}_A_data.json $O/idchk/${arm}_B_root.json $R >> $L 2>&1; rc=$?; lg "identity $arm compare rc=$rc"; [ $rc = 0 ] || exit 1
done
for arm in SUPPF SKR01; do
  c=$O/databuild/${arm}_root_config.yaml
  diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $R0) | grep -E '^[<>]' | sed -E 's/ +$//' | sort > $O/exp_${arm}_derived.txt
  lg "cfgcheck diff $arm vs pf2_SUPPF_100pct_s5 (-> exp_${arm}): $(tr '\n' '|' < $O/exp_${arm}_derived.txt) md5 $(md5sum < $O/exp_${arm}_derived.txt | cut -c1-8)"
done
lg "rootcheck end rc=0"
