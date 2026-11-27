#!/bin/bash
# integrator udev (15 Nov 2026): CPU proofs that the merge bench_udev changes nothing (task item 2). CPU only:
# CUDA_VISIBLE_DEVICES="", nice 19, OMP_NUM_THREADS=1 per process, at most 8 processes at once; dataloader workers 0.
# Never touches el_bench or any existing worktree: references are fresh `git archive`s under $IO.
# Group 1 (8 procs): flag-off 5-step identity (identity_cpu.py 962379a6) SUP, SUPPF, PFV11 x {ref 31c0c36, new bench_wt_udev};
#   skr01_pf_v11 5-step train.py smoke on the LOSO-2 root cvloso2_v11_f0 (cfgcheck, Labelled line, thin lines, nan count);
#   skr01 term check on the trainer's real path (int_skel.py) on cvloso2_v11_f0.
# Group 2 (<= 8 procs): identity compares; full pytest of bench_wt_udev; bench_infer plain path c57508e archive vs new on the
#   held-out fold cv5v2_f2 of w1g_pf_v11_f2_s5 (CPU fp32, without and with --logp); PF v11 5-step smoke on cvloso2_v11_f1
#   (control: 0 thin lines); rendered-config md5 comparisons (reviewed cards at their reviewed tree vs bench_udev).
# Log: $IO/check/run.log. Usage: bash int_check.sh  (run inside tmux bench_int_check)
set -u
IO=/home/noob/work/bench_int_io; OUT=$IO/check; mkdir -p $OUT/id $OUT/infer $OUT/render; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
H=/home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev
NEW=/home/noob/work/bench_wt_udev; R0=/home/noob/work/bench_data/roots/cv5v2_v11_f0
LR0=/home/noob/work/bench_udev/roots/cvloso2_v11_f0; LR1=/home/noob/work/bench_udev/roots/cvloso2_v11_f1
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $*" >> $L; }
arch() {  # commit -> $IO/arch_<commit> (fresh git archive + data symlinks); read-only use
  local c=$1 d=$IO/arch_$1
  if [ ! -d $d ]; then mkdir -p $d && git -C /home/noob/work/el_bench archive $c | tar -x -C $d && echo $c > $d/REVISION
    for x in labeled escdd_masks unlabeled; do ln -s "$(readlink $NEW/data/$x)" $d/data/$x; done
    log "archive $c -> $d ($(find $d -type f | wc -l) files)"; fi; }
log "start; new $NEW HEAD $(git -C $NEW rev-parse --short HEAD) tracked changes $(git -C $NEW status --porcelain -uno | wc -l); el_bench $(git -C /home/noob/work/el_bench rev-parse --short HEAD) changes $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l); identity_cpu $(md5sum < $ID | cut -c1-8); compare_id $(md5sum < $CMP | cut -c1-8); script $(md5sum < $0 | cut -c1-8)"
for c in 31c0c36 c57508e 52e3f14 b12fca8; do arch $c; done
REF=$IO/arch_31c0c36
HS="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
PFV11=$(cd $NEW && $P -m bench.cards opts bench/methods/house_r34_unetpp_pf_v11.yaml --seed 5 --run-name idud_pfv11 --data-root $R0 | tr '\n' ' ')
declare -A OPT=([SUP]="$HS" [SUPPF]="$HS $PF" [PFV11]="$PFV11")
E=$IO/exp; mkdir -p $E
S5="training.total_steps=5 training.val_every=5 training.checkpoint_every=5 training.num_workers=0 training.log_every=1 logging.experiments_dir=$E"
smoke() {  # name card root
  local name=$1 card=$2 root=$3 o rc cc
  o=$(cd $NEW && $P -m bench.cards opts bench/methods/$card.yaml --seed 5 --run-name $name --data-root $root) || { log "smoke $name: opts FAIL"; return; }
  (cd $NEW && nice -n 19 $P scripts/train.py --config configs/supervised.yaml --device cpu --opts $o $S5 > $E/$name.stdout 2>&1)
  rc=$?
  cc=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/$card.yaml --config $E/$name/config_used.yaml --seed 5 --run-name $name --data-root $root | sed -E "s#'$E'#E#g")
  log "smoke $name ($card, root $(basename $root)) rc=$rc Traceback $(grep -c Traceback $E/$name.stdout) nan-loss lines $(grep -ciE 'loss[^|]*nan' $E/$name/train.log) step-5 lines $(grep -c 'step 5/5' $E/$name/train.log) thin lines $(grep -c 'thin .* at step' $E/$name/train.log) thin lines with loss_srec $(grep -c 'thin loss_srec=' $E/$name/train.log) srec exactly 0 $(grep -cE 'thin loss_srec=0( |$)' $E/$name/train.log) latest.pth $(ls $E/$name/checkpoints/latest.pth 2>/dev/null | wc -l) | $(grep -o 'Labelled: .*test: [0-9]*' $E/$name/train.log | head -1) | want: Labelled: $(grep -c . $root/splits/train.txt) val $(grep -c . $root/splits/val.txt) test $(grep -c . $root/splits/test.txt) | cfgcheck vs card: $cc"
}
infer() {  # side(code dir) tag logp
  local code=$1 tag=$2 lp=$3
  (cd $code && nice -n 19 $P scripts/bench_infer.py --run /home/noob/work/el_bench/experiments/w1g_pf_v11_f2_s5 --set cv5v2_f2 \
    --dumps $OUT/infer/$tag --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml \
    --run-id w1g_pf_v11_f2_s5 --weights-key model --device cpu --precision fp32 --threads 1 --workers 0 --batch 8 $lp \
    > $OUT/infer/$tag.log 2>&1); local rc=$?
  log "infer $tag rc=$rc ($(grep -c Traceback $OUT/infer/$tag.log) Traceback)"
}
# ---------------- group 1
log "group 1 start"
for arm in SUP SUPPF PFV11; do for side in ref new; do
  code=$REF; [ $side = new ] && code=$NEW
  ( nice -n 19 $P $ID --code $code --out $OUT/id/${arm}_$side.json --steps 5 --threads 1 --opts ${OPT[$arm]} > $OUT/id/${arm}_$side.log 2>&1; rc=$?; log "id $arm $side rc=$rc" ) &
done; done
smoke ud_skr01_loso_f0 skr01_pf_v11 $LR0 &
SKO=$(cd $NEW && $P -m bench.cards opts bench/methods/skr01_pf_v11.yaml --seed 5 --run-name ud_skel_loso_f0 --data-root $LR0)
( nice -n 19 $P $H/int_skel.py $NEW 5 $SKO > $OUT/skel_skr01_loso_f0.txt 2>&1; rc=$?; log "int_skel skr01 cvloso2_v11_f0 rc=$rc: $(grep -c 'srec term present True finite True >0 True' $OUT/skel_skr01_loso_f0.txt) of 5 steps term present+finite+>0; $(grep -c 'tube px on ignore 0 ' $OUT/skel_skr01_loso_f0.txt) of 5 steps 0 tube px on ignore; $(grep -o 'non-finite total loss steps: .*' $OUT/skel_skr01_loso_f0.txt); $(head -2 $OUT/skel_skr01_loso_f0.txt | tr '\n' ' ')" ) &
wait
log "group 1 done"
# ---------------- group 2
log "group 2 start"
for arm in SUP SUPPF PFV11; do $P $CMP $OUT/id/${arm}_ref.json $OUT/id/${arm}_new.json > $OUT/id/${arm}_cmp.txt 2>&1; rc=$?; log "id $arm compare (ref 31c0c36 archive vs bench_udev) rc=$rc: $(cat $OUT/id/${arm}_cmp.txt)"; done
( cd $NEW && nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1; rc=$?; log "pytest full suite bench_wt_udev rc=$rc: $(tail -1 $OUT/pytest_all.log)" ) &
infer $IO/arch_c57508e c57_plain "" &
infer $NEW udev_plain "" &
infer $IO/arch_c57508e c57_logp --logp &
infer $NEW udev_logp --logp &
smoke ud_pfv11_loso_f1 house_r34_unetpp_pf_v11 $LR1 &
( bash $H/int_render.sh >> $L 2>&1 ) &
wait
for t in plain logp; do
  $P $H/int_dumpcmp.py $OUT/infer/c57_$t $OUT/infer/udev_$t > $OUT/infer/cmp_$t.txt 2>&1; rc=$?
  log "bench_infer $t: c57508e archive vs bench_udev, w1g_pf_v11_f2_s5 on cv5v2_f2 (CPU fp32) rc=$rc: $(cat $OUT/infer/cmp_$t.txt)"
done
log "group 2 done; new HEAD $(git -C $NEW rev-parse --short HEAD) tracked changes $(git -C $NEW status --porcelain -uno | wc -l) untracked $(git -C $NEW status --porcelain | grep -c '^??'); el_bench changes $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l)"
log "ALL DONE"
