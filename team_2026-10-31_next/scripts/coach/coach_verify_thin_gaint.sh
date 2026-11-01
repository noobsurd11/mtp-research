#!/bin/bash
# coach (1 Nov): THIN-B3 opening verification run ON GAINT CPU (laptop memory is short; team-lead 1 Nov ~19:10).
# Same checks as coach_verify_thin.sh, but reads the opening's files in place (read-only) after md5sum -c of both MANIFESTs,
# instead of a local pull. Code = copies of coach's own scripts in /home/noob/work/coach_v/bin (md5s printed).
# nice 19, 8 threads, CUDA hidden. Outputs (text only) in /home/noob/work/coach_v/thin/out; the laptop pulls only those.
set -u
B=/home/noob/work/coach_v/bin; OUT=/home/noob/work/coach_v/thin/out; mkdir -p $OUT
G=/home/noob/work/el_thin; RAW=$G/reports/thin/post; P2=/home/noob/work/el_f3/reports/pf2/post
PY=/home/noob/work/el-fault-detection/.venv/bin/python; CTX=$B/e1_context.tsv; DEP=c9bbb02
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8
grep -qE '^\[[^]]*\] thin scoring done: post rc=0$' $G/reports/thin/q/launch.log && test -s $RAW/MANIFEST.md5 || { echo "THIN opening not done (rc=0): abort"; exit 1; }
{ (cd $RAW && md5sum -c --quiet MANIFEST.md5 && echo "THIN post md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) $(wc -l < MANIFEST.md5) files")
  (cd $P2 && md5sum -c --quiet MANIFEST.md5 && echo "PF2 comparator post md5sum -c OK $(md5sum < MANIFEST.md5 | cut -c1-8) (= coach's 1 Nov PF2 pull 3827f7c0)")
  echo "coach code: $(cd $B && md5sum coach_verify.py coach_thin.py e1_context.tsv | cut -c1-8 | tr '\n' ' ')"
  cd $G
  echo "REVISION $(cat REVISION) HEAD $(git rev-parse --short HEAD) tracked-modified $(git status --short --untracked-files=no | wc -l)"
  for a in SKR CLD B3; do for k in 5 6 7 8 9; do r=thin_${a}_100pct_s$k; f=experiments/$r.stdout
    echo "$r hdr=$(grep -c 'INFO train — Run: ' $f) last=\"$(grep -oE 'step [0-9]+/20000' $f | tail -1)\" tb=$(grep -c Traceback $f) pf=$(grep -c 'PF encoder lr' $f) thin=$(grep -c ' thin ' $f) cfg=\"$(grep -E 'encoder_pf|freeze|lr_mult|val_every|^seed|num_classes|scuff_class|mask_subdir|skel_recall|cldice|weight:|iters:' experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' ')\""
    grep -E "(trained|config OK|CONFIG FAIL).*$r( |$)" reports/thin/q/launch.log | sed 's/^/   /'
  done; done
  grep -E 'HOLD|FAIL|thin scoring|all jobs dispatched' reports/thin/q/launch.log
  echo "gpumem min free over the THIN queue + opening: $(grep -v '^#' reports/thin/q/gpumem.log | awk '{print $2}' | sort -n | head -1) MiB"
  echo '# thin-term magnitudes (mean of logged values per 5k-step block)'
  for a in SKR CLD; do for k in 5 6 7 8 9; do r=thin_${a}_100pct_s$k
    grep ' thin ' experiments/$r.stdout | sed -E 's/.*=([0-9.eE+-]+) at step ([0-9]+).*/\2 \1/' | awk -v r=$r '{b=int(($1-1)/5000); s[b]+=$2; n[b]++} END{printf "%s", r; for(i=0;i<4;i++) printf " %d-%dk %.4f", i*5, (i+1)*5, s[i]/n[i]; printf "\n"}'
  done; done
  for f in comparator_check.txt tau0_check.txt secondary_rc.txt extra_rc.txt scorer_md5.txt; do echo "== $f"; cat $RAW/$f 2>/dev/null; done
  echo "== comparator_scuff_check / scuff_train_iou check"; cat $RAW/comparator_scuff_check.txt $RAW/scuff_train_iou/check.txt 2>/dev/null
  echo "== B5 selfchecks: $(grep -l 'SELFCHECK PASS' $RAW/b5/rec/*.selfcheck.txt 2>/dev/null | wc -l) PASS of $(ls $RAW/b5/rec/*.selfcheck.txt 2>/dev/null | wc -l)"
  echo "== enc cosine 20k"; cat $RAW/enc_cosine_20k.txt 2>/dev/null | tail -20
} > $OUT/integrity.txt 2>&1
M=$RAW/m0; MB=$P2/m0
L(){ for k in 5 6 7 8 9; do echo -n $1/$2_100pct_s$k${3:-}.json,; done | sed 's/,$//'; }
for a in SKR CLD B3; do
  nice -n 19 $PY -I $B/coach_verify.py --base $(L $MB pf2_SUPPF) --arm $(L $M thin_$a) --boot 2000 --e1ctx $CTX > $OUT/verify_${a}_tau0.txt 2>&1
  nice -n 19 $PY -I $B/coach_verify.py --base $(L $MB pf2_SUPPF .tau1) --arm $(L $M thin_$a .tau1) --boot 2000 > $OUT/verify_${a}_tau1.txt 2>&1
done
SI=/home/noob/work/coach_v/thin/scuffign_in; mkdir -p $SI
nice -n 19 $PY -I - $M $SI <<'PY'
import json, sys
m, o = sys.argv[1:3]
for a in ('SKR', 'CLD', 'B3'):
    for k in range(5, 10):
        d = json.load(open(f'{m}/thin_{a}_100pct_s{k}.json'))
        d['cells'] = {'test': d['cells']['test_noscuff']}
        json.dump(d, open(f'{o}/thin_{a}_100pct_s{k}.json', 'w'))
PY
for a in SKR CLD B3; do
  nice -n 19 $PY -I $B/coach_verify.py --base $(L $P2/m0_scuffign pf2_SUPPF .scuffign) --arm $(L $SI thin_$a) --boot 2000 > $OUT/verify_${a}_scuffign.txt 2>&1
done
rm -rf $SI
nice -n 19 $PY -I $B/coach_thin.py run $RAW $P2 $CTX $DEP > $OUT/thin_e1_b5_b3.txt 2>&1
(cd $OUT && md5sum *.txt > MD5)
echo "coach verify THIN written to $OUT"
