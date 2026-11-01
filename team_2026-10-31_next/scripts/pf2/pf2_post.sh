#!/bin/bash
# PF2 scoring on gaint (el_f3 e544133), the ONE pre-registered opening (protocol_PF2.md section 8), fired by pf2_postwatch.sh
# when all 15 runs (10 if gate 6 set RN_STOP) trained rc 0. Out: reports/pf2/post/. Each GPU pass through the shared gate
# (gpu_gate.sh: flock, free >= GS MiB, >= 120 s after any start); GS = max(7,154, RN50 scoring peak + 2,048), set at launch.
# Passes: completeness (step 20000), init / config record, rescore_label_versions per run (test, val), m0_audit default + tau 0 / 1
# (val, test, ext117; el_f1 scorers md5 d36f7438 / d77241bb), tau0 == default + step / revision check, LA tau 0 / 1 (test, val)
# with the tau-0 check, encoder cosine table at 20k (CPU; R34 vs ImageNet R34 = mim_step0.pth, RN50 vs ImageNet RN50 step 0),
# then the frozen extra passes in reports/pf2/post_extra/ (B5 / cell-level / scuff-ignored), each only if its md5 is listed in
# post_extra/FROZEN.md5 (md5sum -c) before the opening; extra passes are non-fatal (rc in post/extra_rc.txt); MD5 manifest; ONE final line in reports/pf2/launch.log:
#   "[<date>] pf2 scoring done: post rc=<rc>"
set -u
cd /home/noob/work/el_f3
. reports/pf2/scripts/gpu_gate.sh
L=reports/pf2/launch.log; OUT=reports/pf2/post; GS=${GS:?set GS}
P=/home/noob/work/el-fault-detection/.venv/bin/python; F1=/home/noob/work/el_f1/reports/f1
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth; R0=reports/pf2/cpucheck/rn50_imagenet_step0.pth
ARMS="SUP SUPPF RN50PF"; [ -e reports/pf2/RN_STOP ] && ARMS="SUP SUPPF"
RUNS=$(for a in $ARMS; do for k in 5 6 7 8 9; do echo pf2_${a}_100pct_s$k; done; done)
post(){
  set -e
  mkdir -p $OUT/m0 $OUT/rescore
  [ "$(cat REVISION)" = e544133 ]
  echo "arms: $ARMS; GS $GS" > $OUT/post_settings.txt
  md5sum $F1/m0_audit.py $F1/m0_audit_tau.py > $OUT/scorer_md5.txt
  grep -q d36f7438 $OUT/scorer_md5.txt && grep -q d77241bb $OUT/scorer_md5.txt
  for r in $RUNS; do grep -q "step 20000/20000" experiments/$r.stdout || { echo "INCOMPLETE $r"; return 1; }; done
  for r in $RUNS; do echo "$r: $(grep -m1 -oE 'Model smp_unetpp: [0-9,]+ parameters' experiments/$r.stdout) | $(grep -A5 'encoder_pf:' experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' ') | $(grep -E 'encoder_name|^seed' experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' ') | Tracebacks $(grep -c Traceback experiments/$r.stdout || true)"; done > $OUT/init_check.txt
  # one gate per GPU process (another job of ours may start between processes)
  for r in $RUNS; do
    gate_wait $GS "pf2 post rescore $r"
    HF_HUB_OFFLINE=1 $P scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$r.json > $OUT/rescore/$r.log 2>&1; done
  RD=$(for r in $RUNS; do echo /home/noob/work/el_f3/experiments/$r; done)
  gate_wait $GS "pf2 post m0"
  HF_HUB_OFFLINE=1 $P $F1/m0_audit.py --code /home/noob/work/el_f3 --out $OUT/m0 --ext $F1/ext117 --no-logits --runs $RD > $OUT/m0_audit.log 2>&1
  for T in 0 1; do gate_wait $GS "pf2 post m0 tau$T"
    HF_HUB_OFFLINE=1 $P $F1/m0_audit_tau.py --code /home/noob/work/el_f3 --out $OUT/m0 --ext $F1/ext117 --no-logits --tau $T --runs $RD > $OUT/m0_audit_tau$T.log 2>&1; done
  $P - "$OUT" $RUNS > $OUT/tau0_check.txt <<'PY'
import json, sys
o, runs = sys.argv[1], sys.argv[2:]
bad = [r for r in runs if json.load(open(f"{o}/m0/{r}.json"))["cells"] != json.load(open(f"{o}/m0/{r}.tau0.json"))["cells"]]
meta = {r: {k: v for k, v in json.load(open(f"{o}/m0/{r}.json")).items() if k != "cells"} for r in runs}
assert all(m["step"] == 20000 and m["code_revision"] == "e544133" for m in meta.values()), meta
print("tau0 == default cells for all runs:", not bad, bad, "| step 20000 and code_revision e544133 for all", len(runs))
PY
  gate_wait $GS "pf2 post LA"
  HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits test val --out $OUT/la.json --check $OUT/rescore > $OUT/la.log 2>&1
  PAIRS=(); for r in $RUNS; do case $r in pf2_RN50PF_*) PAIRS+=(--pair "$r vs ImageNet RN50" $R0 experiments/$r/checkpoints/latest.pth);;
    *) PAIRS+=(--pair "$r vs ImageNet" $S0 experiments/$r/checkpoints/latest.pth);; esac; done
  OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P reports/enc_cosine.py --out $OUT/enc_cosine_20k.json "${PAIRS[@]}" > $OUT/enc_cosine_20k.txt 2>&1
  X=reports/pf2/post_extra
  if [ -s $X/FROZEN.md5 ] && (cd $X && md5sum -c --quiet FROZEN.md5); then
    # top-level hooks only (calib/ files are inputs to a hook, not hooks)
    for s in $(cd $X && awk '{print $2}' FROZEN.md5 | grep -v / | grep '\.sh$'); do
      gate_wait $GS "pf2 post extra $s"
      # extra passes are reported only: non-fatal (coach 14:28); rc logged, then on to the next pass and the manifest
      xrc=0; OUT=$OUT RUNS="$RUNS" GS=$GS bash $X/$s > $OUT/extra_${s%.sh}.log 2>&1 || xrc=$?
      echo "extra $s rc=$xrc" >> $OUT/extra_rc.txt; done
    cp -p $X/FROZEN.md5 $OUT/extra_FROZEN.md5
  else echo "no frozen extra passes at the opening (B5 / cell-level / scuff-ignored computed later from saved outputs, disclosed)" > $OUT/extra_none.txt; fi
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
}
touch $GG/FAST   # 1 s gpumem samples for the whole opening (short passes such as one B5 dump take ~7 s; 10 s sampling can miss them)
( post ) > $OUT.log 2>&1
rc=$?
rm -f $GG/FAST
echo "[$(date)] pf2 scoring done: post rc=$rc" >> $L
