#!/bin/bash
# fin incident (21 Nov 2026): the missing full-pool smoke and the resume-exactness proof, gaint CPU only (CUDA hidden,
# nice 19, OMP 6 threads). Trees: git archives of F (821dfad) and F2 (9967d59 = 9330f8b + the BN re-estimate guard); PATCH=1 adds to the F2 trees the candidate
# second fix (src/trainers/weight_avg.py train_fold_loader: the in-sample monitor, val/test all train cells, is allowed;
# see final2_patch_bnrecal.py) and names them F2P. Root pool532_v11 built by F2's builder from gaint inputs.
# Every run starts train.py as cq.sh renders a full-pool line: --config <card config> --opts <card opts> + tiny overrides
# (last wins): total_steps 8, checkpoint_every 4, log_every 4, input_size 128, labeled_batch_size 2, eval_batch_size 4;
# encoder_pf freeze 2 ramp 2 (both cards); candidate also swad 2..8, enc_probe_every 4. val_every stays the card's (20000),
# so the first validation is the last step, as in production.
#   R1 F  uninterrupted 8 steps (expected: dies at the step-8 validation; latest.pth = step 4)
#   R2 F2 uninterrupted 8 steps (expected rc 0; latest.pth step 8; metrics.json with test_final)
#   R3 R1's crashed run dir copied, resumed under F2 with --resume; compared with R2
#   R4 F2 with --exit_after_step 4 (rc 3); compared with R1's step-4 latest.pth (training path F vs F2)
#   R5 PF card on the held-out root bench_data_v3b/roots/cv5v3_v11_f0, 4 steps, F and F2: compared
# Prints only rc, Labelled / step / RESUMED / saved latest / PF encoder lr / WAVG lines and the last error line of each run;
# never a .stdout, train.log or metrics.json in full; metrics.json compared by path only (ckcmp.py).
# Usage: SCR=<new scratch dir> OUT=<new evidence dir> [CARDS="combo pf"] [PATCH=0|1] [R5=1] bash final2_smoke.sh
set -u
SCR=${SCR:?scratch}; OUT=${OUT:?evidence dir}; CARDS=${CARDS:-combo pf}; PATCH=${PATCH:-0}; R5=${R5:-1}
F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834; F2=9967d59abaab03cef83c1e3014840b2359ef45d7
REPO=/home/noob/work/bench_wt_fin2; P=/home/noob/work/el-fault-detection/.venv/bin/python
H2=$(cd "$(dirname "$(readlink -f "$0")")" && pwd); CK="$P $H2/ckcmp.py"
META=/home/noob/work/bench_data_v3b/meta; LAB=/home/noob/work/el-fault-detection/data/labeled; MASKS=/home/noob/work/bench_data/masks_v11/masks
V3=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1
[ -e $SCR ] && { echo "REFUSED: $SCR exists"; exit 1; }; [ -e $OUT ] && { echo "REFUSED: $OUT exists"; exit 1; }
mkdir -p $SCR $OUT || exit 1
L=$OUT/smoke.log; say(){ echo "$*" | tee -a $L; }
T2=F2; [ "$PATCH" = 1 ] && T2=F2P
say "final2_smoke $(date '+%F %T'): F $F, F2 $F2 (trees $T2), cards '$CARDS', R5 $R5, script $(md5sum < $0 | cut -c1-8), ckcmp $(md5sum < $H2/ckcmp.py | cut -c1-8)"
tree(){ # name commit -> $SCR/<name>
  mkdir -p $SCR/$1 && git -C $REPO archive $2 | tar -x -C $SCR/$1 && ln -s $LAB $SCR/$1/data/labeled || exit 1
  if [ "$2" = $F2 ] && [ "$PATCH" = 1 ]; then $P $H2/final2_patch_bnrecal.py $SCR/$1/src/trainers/weight_avg.py || exit 1; fi; }
tree rootbuild $F2
(cd $SCR/rootbuild && nice -n 19 $P scripts/bench_make_pool_root.py --split $META/cv5v3.json --forbidden $META/forbidden_v1.txt \
   --legacy-splits data/splits --labeled $LAB --train-masks $MASKS --out $SCR/roots | tail -2 | tee -a $L)
ROOT=$SCR/roots/pool532_v11; N=fin_smoke_pool_s5
CX=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml; CP=bench/methods/house_r34_unetpp_pf_v11.yaml
COMMON="training.total_steps=8 training.checkpoint_every=4 training.log_every=4 data.input_size=128 training.labeled_batch_size=2 training.eval_batch_size=4 training.encoder_pf.freeze=2 training.encoder_pf.ramp=2"
XO="training.weight_avg.swad.start=2 training.weight_avg.swad.end=8 training.enc_probe_every=4"
run(){ # tag tree card name root flags over...
  local tag=$1 tn=$2 t=$SCR/$2 card=$3 name=$4 root=$5 flags=$6; shift 6
  local cfg opts rc t0
  cfg=$(cd $t && $P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["config"])' $card)
  opts=$(cd $t && $P -m bench.cards opts $card --seed 5 --run-name $name --data-root $root) || { say "$tag: opts failed"; return 1; }
  t0=$(date +%s)
  (cd $t && nice -n 19 $P -u scripts/train.py $flags --config $cfg --opts $opts "$@" > $t/$name.$tag.stdout 2>&1); rc=$?
  say "== $tag ($tn, $(basename $card .yaml), flags '${flags}'): rc $rc in $(( $(date +%s) - t0 )) s"
  grep -m1 -o "Labelled: [0-9]*.*val: [0-9]*  test: [0-9]*" $t/$name.$tag.stdout | sed 's#(.*)#(...)#' | sed 's/^/   /' | tee -a $L
  grep -E "RESUMED|step [0-9]+/8 |saved latest.pth|PF encoder lr|WAVG BN recal|exit_after_step" $t/$name.$tag.stdout | sed -E 's/^.*(INFO|WARNING) [a-z_.]+ . //' | cut -c1-150 | sed 's/^/   /' | tee -a $L
  grep -E "^[A-Za-z]*Error|^FileNotFound|Traceback" $t/$name.$tag.stdout | tail -2 | cut -c1-260 | sed 's/^/   /' | tee -a $L
  return 0; }
st(){ $P -c 'import sys, torch; s = torch.load(sys.argv[1], map_location="cpu", weights_only=False); w = s.get("weight_avg") or {}
print("   latest.pth step", s["step"], "models", sorted(s["models"]), "averager n", {k: (v.get("n") if isinstance(v, dict) else None) for k, v in w.items()}, "lr", [g["lr"] for g in s["optimizers"]["model"]["param_groups"]])' $1 | tee -a $L; }
for c in $CARDS; do
  case $c in combo) card=$CX; over="$COMMON $XO";; pf) card=$CP; over="$COMMON";; *) say "unknown card $c"; exit 1;; esac
  tree F_R1_$c $F; tree ${T2}_R2_$c $F2; tree ${T2}_R3_$c $F2; tree ${T2}_R4_$c $F2
  run R1 F_R1_$c $card $N $ROOT "" $over;            st $SCR/F_R1_$c/experiments/$N/checkpoints/latest.pth
  run R2 ${T2}_R2_$c $card $N $ROOT "" $over;         [ -f $SCR/${T2}_R2_$c/experiments/$N/checkpoints/latest.pth ] && st $SCR/${T2}_R2_$c/experiments/$N/checkpoints/latest.pth
  say "   R2 metrics.json: $([ -s $SCR/${T2}_R2_$c/experiments/$N/metrics.json ] && $P -c 'import json, sys; m = json.load(open(sys.argv[1])); print("present; keys test_final", "test_final" in m, "test_best", "test_best" in m, "val_history", len(m.get("val_history", [])))' $SCR/${T2}_R2_$c/experiments/$N/metrics.json || echo absent)"
  mkdir -p $SCR/${T2}_R3_$c/experiments && cp -a $SCR/F_R1_$c/experiments/$N $SCR/${T2}_R3_$c/experiments/ \
    && say "   R3: copied R1's crashed run dir (latest.pth md5 $(md5sum < $SCR/F_R1_$c/experiments/$N/checkpoints/latest.pth | cut -c1-8))"
  run R3 ${T2}_R3_$c $card $N $ROOT "--resume" $over; [ -f $SCR/${T2}_R3_$c/experiments/$N/checkpoints/latest.pth ] && st $SCR/${T2}_R3_$c/experiments/$N/checkpoints/latest.pth
  run R4 ${T2}_R4_$c $card $N $ROOT "--exit_after_step 4" $over
  say "-- compare R3 (F crash + F2 resume) with R2 (F2 uninterrupted), latest.pth:"
  $CK pth $SCR/${T2}_R2_$c/experiments/$N/checkpoints/latest.pth $SCR/${T2}_R3_$c/experiments/$N/checkpoints/latest.pth \
     --allow '^/trainer/train_time$' --allow '^/trainer/train_curve\[[0-9]+\]/steps_per_sec$' --allow '^/trainer/resumes' 2>&1 | tee -a $L
  say "   rc ${PIPESTATUS[0]}"
  say "-- compare R3 with R2, metrics.json (paths only):"
  $CK json $SCR/${T2}_R2_$c/experiments/$N/metrics.json $SCR/${T2}_R3_$c/experiments/$N/metrics.json \
     --allow '^/timing/' --allow '^/resumes' --allow '^/train_curve\[[0-9]+\]/steps_per_sec$' 2>&1 | tee -a $L
  say "   rc ${PIPESTATUS[0]}"
  say "-- compare R4 (F2, step 4) with R1 (F, step 4), latest.pth:"
  $CK pth $SCR/F_R1_$c/experiments/$N/checkpoints/latest.pth $SCR/${T2}_R4_$c/experiments/$N/checkpoints/latest.pth \
     --allow '^/trainer/train_time$' --allow '^/trainer/train_curve\[[0-9]+\]/steps_per_sec$' 2>&1 | tee -a $L
  say "   rc ${PIPESTATUS[0]}"
done
if [ "$R5" = 1 ]; then
  tree F_R5 $F; tree ${T2}_R5 $F2; N5=fin_smoke_cv5v3_s5
  O5="training.total_steps=4 training.checkpoint_every=4 training.log_every=4 data.input_size=128 training.labeled_batch_size=2 training.eval_batch_size=4 training.encoder_pf.freeze=2 training.encoder_pf.ramp=2"
  run R5F F_R5 $CP $N5 $V3 "" $O5; run R5F2 ${T2}_R5 $CP $N5 $V3 "" $O5
  say "-- compare R5 F2 with F (held-out root), latest.pth and metrics.json:"
  $CK pth $SCR/F_R5/experiments/$N5/checkpoints/latest.pth $SCR/${T2}_R5/experiments/$N5/checkpoints/latest.pth \
     --allow '^/trainer/train_time$' --allow '^/trainer/train_curve\[[0-9]+\]/steps_per_sec$' 2>&1 | tee -a $L; say "   rc ${PIPESTATUS[0]}"
  $CK json $SCR/F_R5/experiments/$N5/metrics.json $SCR/${T2}_R5/experiments/$N5/metrics.json \
     --allow '^/timing/' --allow '^/train_curve\[[0-9]+\]/steps_per_sec$' 2>&1 | tee -a $L; say "   rc ${PIPESTATUS[0]}"
fi
say "final2_smoke end $(date '+%F %T')"
