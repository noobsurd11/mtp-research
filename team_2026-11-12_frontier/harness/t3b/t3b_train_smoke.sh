#!/bin/bash
# Builder's training-path smoke for T3b (gaint CPU only, CUDA hidden, nice 19, OMP 6 threads), SYNTHETIC E1 data:
#   K's bench_make_t3b_roots.py builds the 11 roots from the real pool files and a synthetic ext117 (t3b_smoke_synth.py);
#   then the files of fold 0's 22 held-out E1 cells are DELETED from files/images and files/masks (a run that opened one
#   would fail); then train.py runs on root t3b_all_f0 exactly as cq.sh renders a T3b training line (card
#   hrnet_w18_unetpp_swad_const_pf_v11 opts + seed 5, run name, data.root) plus tiny overrides (last wins; as final2_smoke.sh):
#   total_steps 8, checkpoint_every 4, log_every 4, input_size 128, labeled_batch_size 2, eval_batch_size 4, encoder_pf
#   freeze 2 ramp 2, swad 2..8, enc_probe_every 4; val_every stays the card's (20000): the first validation is the last step.
#   T1 under K (git archive), T2 under F2 (git archive): both must end rc 0 (final validation on the in-sample monitor with
#   E1 255 labels in train, SWAD finalize, BN re-estimate, save, post-fit test eval); latest.pth compared tensor by tensor
#   (final2/ckcmp.py; only timing entries may differ): the training path of K is F2's on a T3b root.
# Prints only rc, the Labelled / step / saved / WAVG lines, the last error line; never a .stdout, train.log or metrics.json.
# Usage: bash t3b_train_smoke.sh <out dir>
set -u
OUT=${1:?out}; HERE=$(cd "$(dirname "$(readlink -f "$0")")" && pwd)
P=/home/noob/work/el-fault-detection/.venv/bin/python; KT=/home/noob/work/bench_wt_t3b; CK="$P $HERE/../final2/ckcmp.py"
[ "$(md5sum < $HERE/../final2/ckcmp.py | cut -c1-8)" = "$(md5sum < /home/yugma/mtp/research/team_2026-11-12_frontier/harness/final2/ckcmp.py | cut -c1-8)" ] || exit 1
KC=$(grep -m1 '^KC=' $HERE/t3b_queue.sh | cut -d= -f2 | cut -d';' -f1); F2=9967d59abaab03cef83c1e3014840b2359ef45d7
S=/home/noob/work/bench_int_io/t3b/train_$$; [ -e $S ] && exit 1; mkdir -p $S $OUT || exit 1
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
L=$OUT/train_smoke.log; say(){ echo "$*" | tee -a $L; }
say "t3b_train_smoke $(date '+%F %T'): K $KC, F2 $F2, script $(md5sum < $0 | cut -c1-8), ckcmp $(md5sum < $HERE/../final2/ckcmp.py | cut -c1-8)"
nice -n 19 $P $HERE/t3b_smoke_synth.py ext $S/ext117 | tee -a $L
(cd $S/ext117 && for s in $(grep . stems_eval.txt); do md5sum images/$s.png masks/$s.png ignore/$s.png; done) > $S/e1.md5
(cd $KT && nice -n 19 $P scripts/bench_make_t3b_roots.py --split /home/noob/work/bench_data_v3b/meta/cv5v3.json --forbidden /home/noob/work/bench_data_v3b/meta/forbidden_v1.txt \
  --legacy-splits $KT/data/splits --labeled /home/noob/work/el-fault-detection/data/labeled --train-masks /home/noob/work/bench_data/masks_v11/masks \
  --e1 $S/ext117 --e1-manifest $S/e1.md5 --lists $HERE/lists --out $S/DT) | tail -3 | tee -a $L
for s in $(grep . $HERE/lists/e1t3b_f0.txt); do rm -f $S/DT/files/images/$s.png $S/DT/files/masks/$s.png; done
say "deleted the files of fold 0's $(grep -c . $HERE/lists/e1t3b_f0.txt) held-out E1 cells from DT/files ($(ls $S/DT/files/masks | wc -l) masks left of 638)"
ROOT=$S/DT/roots/t3b_all_f0; N=t3b_smoke_all_f0_s5; CARD=bench/methods/hrnet_w18_unetpp_swad_const_pf_v11.yaml
OVER="training.total_steps=8 training.checkpoint_every=4 training.log_every=4 data.input_size=128 training.labeled_batch_size=2 training.eval_batch_size=4 training.encoder_pf.freeze=2 training.encoder_pf.ramp=2 training.weight_avg.swad.start=2 training.weight_avg.swad.end=8 training.enc_probe_every=4"
for t in K:$KC F2:$F2; do tn=${t%%:*}; c=${t#*:}; d=$S/tree_$tn
  mkdir -p $d && git -C $KT archive $c | tar -x -C $d && ln -s /home/noob/work/el-fault-detection/data/labeled $d/data/labeled || exit 1
  cfg=$(cd $d && $P -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["config"])' $CARD)
  opts=$(cd $d && $P -m bench.cards opts $CARD --seed 5 --run-name $N --data-root $ROOT) || exit 1
  t0=$(date +%s); (cd $d && nice -n 19 $P -u scripts/train.py --config $cfg --opts $opts $OVER > $d/$N.stdout 2>&1); rc=$?
  say "== T$([ $tn = K ] && echo 1 || echo 2) ($tn $c): rc $rc in $(( $(date +%s) - t0 )) s"
  grep -m1 -o "Labelled: [0-9]*.*val: [0-9]*  test: [0-9]*" $d/$N.stdout | sed 's#(.*)#(...)#' | sed 's/^/   /' | tee -a $L
  grep -E "step [0-9]+/8 |saved latest.pth|WAVG" $d/$N.stdout | sed -E 's/^.*(INFO|WARNING) [a-z_.]+ . //' | cut -c1-140 | sed 's/^/   /' | tee -a $L
  grep -E "^[A-Za-z]*Error|Traceback" $d/$N.stdout | tail -2 | cut -c1-200 | sed 's/^/   /' | tee -a $L
  [ -f $d/experiments/$N/checkpoints/latest.pth ] && $P -c 'import sys, torch; s = torch.load(sys.argv[1], map_location="cpu", weights_only=False); print("   latest.pth step", s["step"], "models", sorted(s["models"]))' $d/experiments/$N/checkpoints/latest.pth | tee -a $L
done
say "-- compare T2 (F2) with T1 (K), latest.pth:"
$CK pth $S/tree_F2/experiments/$N/checkpoints/latest.pth $S/tree_K/experiments/$N/checkpoints/latest.pth \
   --allow '^/trainer/train_time$' --allow '^/trainer/train_curve\[[0-9]+\]/steps_per_sec$' 2>&1 | tee -a $L
say "   rc ${PIPESTATUS[0]}"
say "t3b_train_smoke end $(date '+%F %T')"
chmod -R u+w $S; rm -rf $S
