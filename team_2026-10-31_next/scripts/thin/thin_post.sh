#!/bin/bash
# THIN-B3 scoring on gaint (el_thin, deploy $DEPLOY), the ONE pre-registered opening (protocol_thin_b3.md §4-5, §8.3-8.4), fired by
# thin_postwatch.sh when all 15 runs trained rc 0 and PF2's opening ended rc 0. Out: el_thin/reports/thin/post/.
# Every GPU pass through the shared gate (gpu_gate.sh: flock, free >= GS MiB, >= 120 s after any start), one gate per GPU process;
# gpumem at 1 s for the whole opening (gpu_gate/FAST). Passes:
#   PF2 comparator files unchanged (el_f3/reports/pf2/post MANIFEST, md5sum -c); completeness; init record; scorer md5s;
#   rescore_label_versions (1e41202b) per run; m0_audit_b3 (M0B3) default + tau 0 / 1, all 15 runs, sets val / test / ext,
#   --ext-scuff (E1 crack-on-scuff) and --test-scuff (test_noscuff, descriptive); tau0 == default + step / revision check;
#   m0_audit_b3 --sets ext --ext-scuff on the comparator pf2_SUPPF_100pct_s5..9 (pre-registered B3 secondary), with its ext cells
#   checked equal to PF2's opening m0 JSONs; LA tau 0 / 1 (el_thin 419486b1; 25-class prior for B3) with the tau-0 check;
#   scuff_train_iou f6d77562 (CPU fp32; B3 s5-9 and comparator pf2_SUPPF s5-9; 20k; 12 train cells); 20k encoder cosines (CPU); frozen extra passes in reports/thin/post_extra
#   (calib B5 hook + pooled; only if listed in its FROZEN.md5 and md5sum -c passes; non-fatal); MANIFEST; ONE final line in
#   reports/thin/q/launch.log: "[<date>] thin scoring done: post rc=<rc>"
set -u
cd /home/noob/work/el_thin
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
L=reports/thin/q/launch.log; OUT=reports/thin/post; GS=${GS:?}; DEPLOY=${DEPLOY:?}; M0B3=${M0B3:?}  # GS: scoring gate, set at arming
P=/home/noob/work/el-fault-detection/.venv/bin/python; X1=/home/noob/work/el_f1/reports/f1/ext117
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth; PF=/home/noob/work/el_f3/reports/pf2/post
RUNS=$(for k in 5 6 7 8 9; do for a in SKR CLD B3; do echo thin_${a}_100pct_s$k; done; done)
CMP=$(for k in 5 6 7 8 9; do echo /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s$k; done)
post(){
  set -e
  mkdir -p $OUT/m0 $OUT/rescore $OUT/m0_comparator_scuff $OUT/scuff_train_iou
  [ "$(git rev-parse --short HEAD)" = "$DEPLOY" ] && [ "$(cat REVISION)" = "$DEPLOY" ] && [ -z "$(git status --short --untracked-files=no)" ]
  (cd $PF && md5sum -c --quiet MANIFEST.md5) && echo "PF2 comparator files unchanged (MANIFEST $(md5sum < $PF/MANIFEST.md5 | cut -c1-8))" > $OUT/comparator_check.txt
  md5sum scripts/rescore_label_versions.py scripts/rescore_logit_adjust.py scripts/b3/m0_audit_b3.py scripts/b3/scuff_train_iou.py > $OUT/scorer_md5.txt
  grep -q ^1e41202b $OUT/scorer_md5.txt && grep -q ^419486b1 $OUT/scorer_md5.txt && grep -q ^$M0B3 $OUT/scorer_md5.txt && grep -q ^f6d77562 $OUT/scorer_md5.txt
  for r in $RUNS; do grep -q "step 20000/20000" experiments/$r.stdout || { echo "INCOMPLETE $r"; return 1; }; done
  for r in $RUNS; do echo "$r: $(grep -m1 -oE 'Model smp_unetpp: [0-9,]+ parameters' experiments/$r.stdout) | $(grep -E '^seed|num_classes|scuff_class|mask_subdir|skel_recall|cldice|weight:|iters:' experiments/$r/config_used.yaml | tr -s ' ' | tr '\n' ' ') | thin lines $(grep -c ' thin ' experiments/$r.stdout || true) | Tracebacks $(grep -c Traceback experiments/$r.stdout || true)"; done > $OUT/init_check.txt
  for r in $RUNS; do
    gate_wait $GS "thin post rescore $r"
    HF_HUB_OFFLINE=1 $P scripts/rescore_label_versions.py --runs $r --out $OUT/rescore/$r.json > $OUT/rescore/$r.log 2>&1; done
  RD=$(for r in $RUNS; do echo /home/noob/work/el_thin/experiments/$r; done)
  FL="--ext $X1 --no-logits --ext-scuff data/ext_scuff --test-scuff data/test_scuff"
  gate_wait $GS "thin post m0_audit_b3"
  HF_HUB_OFFLINE=1 $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $OUT/m0 $FL --runs $RD > $OUT/m0_audit_b3.log 2>&1
  for T in 0 1; do
    gate_wait $GS "thin post m0_audit_b3 tau$T"
    HF_HUB_OFFLINE=1 $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $OUT/m0 $FL --tau $T --runs $RD > $OUT/m0_audit_b3_tau$T.log 2>&1; done
  $P - "$OUT" "$DEPLOY" $RUNS > $OUT/tau0_check.txt <<'PY'
import json, sys
o, dep, runs = sys.argv[1], sys.argv[2], sys.argv[3:]
bad = [r for r in runs if json.load(open(f"{o}/m0/{r}.json"))["cells"] != json.load(open(f"{o}/m0/{r}.tau0.json"))["cells"]]
meta = {r: {k: v for k, v in json.load(open(f"{o}/m0/{r}.json")).items() if k != "cells"} for r in runs}
assert all(m["step"] == 20000 and m["code_revision"] == dep for m in meta.values()), meta
sets = {r: sorted(json.load(open(f"{o}/m0/{r}.json"))["cells"]) for r in runs}
print("tau0 == default cells for all runs:", not bad, bad, "| step 20000 and code_revision", dep, "for all", len(runs), "| sets", sets[runs[0]])
PY
  gate_wait $GS "thin post comparator ext-scuff"
  # B3 secondaries below are reported only: non-fatal (rc to secondary_rc.txt), so they cannot block the verdict files or the manifest
  srun(){ local lab=$1; shift; local xrc=0; "$@" || xrc=$?; echo "$lab rc=$xrc" >> $OUT/secondary_rc.txt; }
  srun comparator_ext_scuff env HF_HUB_OFFLINE=1 $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $OUT/m0_comparator_scuff \
    --ext $X1 --no-logits --sets ext --ext-scuff data/ext_scuff --runs $CMP > $OUT/m0_comparator_scuff.log 2>&1
  srun comparator_cells_check $P - $OUT/m0_comparator_scuff $PF/m0 > $OUT/comparator_scuff_check.txt <<'PY'
import json, sys
a, b = sys.argv[1:3]; ok = True
for k in range(5, 10):
    r = f"pf2_SUPPF_100pct_s{k}"
    x = json.load(open(f"{a}/{r}.json"))["cells"]["ext"]; y = json.load(open(f"{b}/{r}.json"))["cells"]["ext"]
    ok &= {s: {kk: vv for kk, vv in c.items() if kk != "scuff"} for s, c in x.items()} == y
print("comparator ext cells (scuff key removed) equal PF2's opening m0 ext cells for s5-9:", ok)
assert ok
PY
  gate_wait $GS "thin post LA"
  HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $RUNS --taus 0 1 --splits test val --out $OUT/la.json --check $OUT/rescore > $OUT/la.log 2>&1
  # B3 train-cell readout at 20k (coach 1 Nov): CPU fp32 for B3 s5-9 AND the comparator pf2_SUPPF s5-9 (same device on both
  # sides: bf16 GPU vs fp32 CPU differ slightly); 12 train scuff cells only (no val / test / E1); nice 19, 8 threads, no GPU
  for r in $(for k in 5 6 7 8 9; do echo /home/noob/work/el_thin/experiments/thin_B3_100pct_s$k /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s$k; done); do
    n=$(basename $r)
    srun scuff_train_iou_$n env CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 HF_HUB_OFFLINE=1 nice -n 19 $P scripts/b3/scuff_train_iou.py \
      --run $r --device cpu --out $OUT/scuff_train_iou/$n.json > $OUT/scuff_train_iou/$n.log 2>&1; done
  srun scuff_train_iou_check $P - $OUT/scuff_train_iou > $OUT/scuff_train_iou/check.txt <<'PY'
import json, sys, glob
fs = sorted(glob.glob(sys.argv[1] + "/*.json")); st = {f.split("/")[-1]: json.load(open(f))["step"] for f in fs}
assert len(fs) == 10 and all(v == 20000 for v in st.values()), st
print("scuff_train_iou: 10 runs (B3 s5-9 + pf2_SUPPF s5-9), CPU fp32, all step 20000")
PY
  PAIRS=(); for r in $RUNS; do PAIRS+=(--pair "$r vs ImageNet" $S0 experiments/$r/checkpoints/latest.pth); done
  OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES="" $P /home/noob/work/el_f3/reports/enc_cosine.py --out $OUT/enc_cosine_20k.json "${PAIRS[@]}" > $OUT/enc_cosine_20k.txt 2>&1
  X=reports/thin/post_extra
  if [ -s $X/FROZEN.md5 ] && (cd $X && md5sum -c --quiet FROZEN.md5); then
    # top-level hooks only (subdirectory files are inputs to a hook)
    for s in $(cd $X && awk '{print $2}' FROZEN.md5 | grep -v / | grep '\.sh$'); do
      gate_wait $GS "thin post extra $s"
      # extra passes are reported only: non-fatal; rc logged, then on to the next pass and the manifest
      xrc=0; OUT=$OUT RUNS="$RUNS" GS=$GS bash $X/$s > $OUT/extra_${s%.sh}.log 2>&1 || xrc=$?
      echo "extra $s rc=$xrc" >> $OUT/extra_rc.txt; done
    cp -p $X/FROZEN.md5 $OUT/extra_FROZEN.md5
  else echo "no frozen extra passes at the opening (disclosed)" > $OUT/extra_none.txt; fi
  (cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
}
touch $GG/FAST   # 1 s gpumem samples for the whole opening
( post ) > $OUT.log 2>&1
rc=$?
rm -f $GG/FAST
echo "[$(date)] thin scoring done: post rc=$rc" >> $L
