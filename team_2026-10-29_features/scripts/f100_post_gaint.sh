#!/bin/bash
# protocol_100 scoring on gaint (el_f3 e544133), two pre-registered test openings (coach + team-lead, 30 Oct):
#   opening1: SUP100-g, SUP100-PF, MIM100-PF (15 runs), fired when all 15 trained rc 0. Out: reports/f100/post_opening1/
#   opening2: CP100 (5 runs), fired when all 5 trained rc 0 and opening1 is done; SUP100-g's opening-1 per-cell files are
#             the comparator, unchanged. Out: reports/f100/post_opening2/ (+ E3b decoy on the 20k checkpoints of CP100 and
#             SUP100-g with the CP100 library, crack px on crack-free cells).
# Each opening: completeness (step 20000 in the log), rescore_label_versions (per run), m0_audit default + tau 0/1 per-cell
# JSONs (val, test, ext106; el_f1 copies md5 d36f7438 / d77241bb), tau0 == default, LA tau 0/1 with the tau-0 check,
# encoder cosine table at 20k (CPU), MD5 manifest, then ONE final line in reports/f100/launch.log:
#   "[<date>] f3 opening<N> scoring done: post rc=<rc>"   (coach's watcher keys on it).
# Every GPU pass waits at the queue's gate (reports/f100/gate.lock, >= 6,000 MiB free, >= 120 s after the last start).
# Usage: f100_post_gaint.sh opening1|opening2
set -u
cd /home/noob/work/el_f3
N=$1; L=reports/f100/launch.log; OUT=reports/f100/post_$N
P=/home/noob/work/el-fault-detection/.venv/bin/python; F1=/home/noob/work/el_f1/reports/f1
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth; ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
case $N in
  opening1) RUNS=$(for a in SUP SUPPF MIMPF; do for k in 0 1 2 3 4; do echo f3_${a}_100pct_s$k; done; done);;
  opening2) RUNS=$(for k in 0 1 2 3 4; do echo f3_CP_100pct_s$k; done);;
  *) echo "usage: $0 opening1|opening2"; exit 2;;
esac
gate_wait(){ while :; do
  ok=$(flock reports/f100/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f100/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f100/last_start; echo 1; else echo 0; fi' _ "$1")
  [ "$ok" = 1 ] && break; sleep 30; done; }
post(){
  set -e
  mkdir -p $OUT/m0 $OUT/rescore
  [ "$(cat REVISION)" = e544133 ]
  md5sum $F1/m0_audit.py $F1/m0_audit_tau.py > $OUT/scorer_md5.txt
  grep -q d36f7438 $OUT/scorer_md5.txt && grep -q d77241bb $OUT/scorer_md5.txt
  for r in $RUNS; do grep -q "step 20000/20000" experiments/$r.stdout || { echo "INCOMPLETE $r"; return 1; }; done
  for r in $RUNS; do grep -hE "encoder_init|Encoder initialised|Decoder initialised" experiments/$r.stdout | sed -E 's/^[0-9-]+ [0-9:,]+ //' | sed "s/^/$r: /"; \
    grep -A6 "encoder_pf:" experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' ' | sed "s/^/$r cfg: /"; echo; \
    grep -A10 "^cp:" experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' '; echo; done > $OUT/init_check.txt
  gate_wait 6000
  for r in $RUNS; do HF_HUB_OFFLINE=1 $P scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$r.json > $OUT/rescore/$r.log 2>&1; done
  RD=$(for r in $RUNS; do echo /home/noob/work/el_f3/experiments/$r; done)
  gate_wait 6000
  HF_HUB_OFFLINE=1 $P $F1/m0_audit.py --code /home/noob/work/el_f3 --out $OUT/m0 --ext $F1/ext117 --no-logits --runs $RD > $OUT/m0_audit.log 2>&1
  for T in 0 1; do gate_wait 6000
    HF_HUB_OFFLINE=1 $P $F1/m0_audit_tau.py --code /home/noob/work/el_f3 --out $OUT/m0 --ext $F1/ext117 --no-logits --tau $T --runs $RD > $OUT/m0_audit_tau$T.log 2>&1; done
  $P - "$OUT" $RUNS > $OUT/tau0_check.txt <<'PY'
import json, sys
o, runs = sys.argv[1], sys.argv[2:]
bad = [r for r in runs if json.load(open(f"{o}/m0/{r}.json"))["cells"] != json.load(open(f"{o}/m0/{r}.tau0.json"))["cells"]]
meta = {r: {k: v for k, v in json.load(open(f"{o}/m0/{r}.json")).items() if k != "cells"} for r in runs}
assert all(m["step"] == 20000 and m["code_revision"] == "e544133" for m in meta.values()), meta
print("tau0 == default cells for all runs:", not bad, bad, "| step 20000 and code_revision e544133 for all", len(runs))
PY
  gate_wait 6000
  HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits test val --out $OUT/la.json --check $OUT/rescore > $OUT/la.log 2>&1
  PAIRS=(); for r in $RUNS; do case $r in f3_MIMPF_*) PAIRS+=(--pair "$r vs encoder_final" $ENC experiments/$r/checkpoints/latest.pth);;
    *) PAIRS+=(--pair "$r vs ImageNet" $S0 experiments/$r/checkpoints/latest.pth);; esac; done
  OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P reports/enc_cosine.py --out $OUT/enc_cosine_20k.json "${PAIRS[@]}" > $OUT/enc_cosine_20k.txt 2>&1
  if [ $N = opening2 ]; then
    O1=reports/f100/post_opening1
    test -s $O1/MANIFEST.md5 && (cd $O1 && md5sum -c --quiet MANIFEST.md5)        # comparator files unchanged since opening 1
    comm -23 <(sort data/splits/train.txt) <(sort reports/f100/cp100_library_exclude.txt) > $OUT/cp100_library_cells.txt
    gate_wait 6000
    HF_HUB_OFFLINE=1 $P scripts/cp_decoy.py --runs $(for k in 0 1 2 3 4; do echo experiments/f3_SUP_100pct_s$k; done) \
      $(for k in 0 1 2 3 4; do echo experiments/f3_CP_100pct_s$k; done) --labeled $OUT/cp100_library_cells.txt --out $OUT/decoy_final.json > $OUT/decoy_final.log 2>&1
    $P reports/f2_crackfree_fp.py --a $O1/m0 f3_SUP_100pct --b $OUT/m0 f3_CP_100pct --labels SUP100-g CP100 --out $OUT/crackfree_fp.json > $OUT/crackfree_fp.txt 2>&1
  fi
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
}
( post ) > $OUT.log 2>&1
rc=$?
echo "[$(date)] f3 $N scoring done: post rc=$rc" >> $L
