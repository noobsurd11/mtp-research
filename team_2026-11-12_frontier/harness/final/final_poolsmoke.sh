#!/bin/bash
# Full-pool root CPU smoke (final package, gaint, CPU only, nice 19): an archive of commit F, the pool532_v11 root built by
# F's scripts/bench_make_pool_root.py from gaint's pinned inputs into a scratch dir, then F's scripts/train.py started
# exactly as cq.sh renders a full-pool line (card opts with --data-root <root>) plus --exit_after_step 1 (rc 3 by design),
# with CUDA hidden. Checks, as cq.sh's live check does: cfgcheck of config_used.yaml against the card (seed, run name,
# root) and the first 'Labelled:' line = want_line(root) ("Labelled: 532 (...)  unlabelled: 0 (-)  val: 107  test: 107").
# Prints only the Labelled line and step lines of the run's stdout (never the rest). Writes only under SCR.
# Usage: F=<full commit> SCR=<new scratch dir> [CARD=bench/methods/house_r34_unetpp_pf_v11.yaml] bash final_poolsmoke.sh
set -u
F=${F:?full commit}; SCR=${SCR:?scratch dir (new)}; CARD=${CARD:-bench/methods/house_r34_unetpp_pf_v11.yaml}
REPO=/home/noob/work/bench_wt_fin; P=/home/noob/work/el-fault-detection/.venv/bin/python
META=/home/noob/work/bench_data_v3b/meta; LAB=/home/noob/work/el-fault-detection/data/labeled; MASKS=/home/noob/work/bench_data/masks_v11/masks
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
[ -e $SCR ] && { echo "REFUSED: $SCR exists"; exit 1; }
mkdir -p $SCR/tree && git -C $REPO archive $F | tar -x -C $SCR/tree || exit 1
cd $SCR/tree || exit 1
nice -n 19 $P scripts/bench_make_pool_root.py --split $META/cv5v3.json --forbidden $META/forbidden_v1.txt --legacy-splits data/splits \
  --labeled $LAB --train-masks $MASKS --out $SCR/roots || { echo "FAIL root build"; exit 1; }
nice -n 19 $P scripts/bench_make_pool_root.py --split $META/cv5v3.json --forbidden $META/forbidden_v1.txt --legacy-splits data/splits \
  --labeled $LAB --train-masks $MASKS --out $SCR/roots --check | head -1
R=$SCR/roots/pool532_v11; N=fin_smoke_pool_s5
cnt(){ grep -c . "$1"; }
WANT="Labelled: $(cnt $R/splits/train.txt) ($R/splits/train.txt)  unlabelled: 0 (-)  val: $(cnt $R/splits/val.txt)  test: $(cnt $R/splits/test.txt)"
cfgf=$($P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["config"])' $CARD)
OPTS=$($P -m bench.cards opts $CARD --seed 5 --run-name $N --data-root $R) || exit 1
echo "command: python -u scripts/train.py --exit_after_step 1 --config $cfgf --opts $OPTS"
t0=$(date +%s)
nice -n 19 $P -u scripts/train.py --exit_after_step 1 --config $cfgf --opts $OPTS > $SCR/$N.stdout 2>&1; rc=$?
echo "train.py rc $rc (3 = exit after step, by design) in $(( $(date +%s) - t0 )) s"
grep -m1 -o "Labelled: .*" $SCR/$N.stdout | sed 's/^/first Labelled line: /'
grep -E "step [0-9]+/[0-9]+" $SCR/$N.stdout | head -3 | cut -c1-160
GOT=$(grep -m1 -o "Labelled: .*" $SCR/$N.stdout)
[ "$GOT" = "$WANT" ] && echo "OK startup line = want_line(root)" || { echo "FAIL startup line"; echo "  want: $WANT"; }
m=$($P -m bench.cards cfgcheck $CARD --config experiments/$N/config_used.yaml --seed 5 --run-name $N --data-root $R) && echo "OK cfgcheck: $m" || echo "FAIL cfgcheck: $m"
grep -c Traceback $SCR/$N.stdout | sed 's/^/Traceback lines: /'
