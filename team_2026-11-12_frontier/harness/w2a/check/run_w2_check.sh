#!/bin/bash
# Wave 2a integrator CPU checks on gaint (CPU only, nice 19, CUDA_VISIBLE_DEVICES=""; two lanes of 4 threads = 8).
# Never touches el_bench (ref = git archive of 31c0c36). Log /home/noob/work/bench_w2_io/check/run.log.
# Lane A: flag-off 5-step identity (identity_cpu.py 962379a6), ref 31c0c36 vs bench_wt_w2: SUP, SUPPF, SKR01, A8 (legacy
#   flags as x1), PFV11 and HV11 (cards house_r34_unetpp_pf_v11 / house_r34_unetpp_v11 rendered on cv5v2_v11_f0); then the
#   baseline card checks (render md5 at ref = at new for the 10 W1-G jobs; cfgcheck of the 10 W1-G config_used.yaml at new);
#   then the full pytest of bench_wt_w2.
# Lane B: 5-step train.py runs on cv5v2_v11_f0 seed 5 of the PF v11 card (ref and new code) and of every wave 2a card
#   (new code), then w2_smoke_check.py (raw-weight hashes, checkpoint keys; IDENTICAL / DIFF only).
set -u
LANE=${1:?lane A or B}
IO=/home/noob/work/bench_w2_io; OUT=$IO/check; mkdir -p $OUT; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
REF=$IO/ref_31c0c36; NEW=/home/noob/work/bench_wt_w2
R0=/home/noob/work/bench_data/roots/cv5v2_v11_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $LANE: $*" >> $L; }
log "start; new $NEW HEAD $(git -C $NEW rev-parse --short HEAD) changed $(git -C $NEW status --porcelain -uno | wc -l); el_bench $(git -C /home/noob/work/el_bench rev-parse --short HEAD) changed $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l); identity_cpu $(md5sum < $ID | cut -c1-8)"
if [ "$LANE" = A ]; then
  if [ ! -d $REF ]; then
    mkdir -p $REF && git -C /home/noob/work/el_bench archive 31c0c36 | tar -x -C $REF && echo 31c0c36 > $REF/REVISION
    for d in labeled escdd_masks unlabeled; do ln -s "$(readlink $NEW/data/$d)" $REF/data/$d; done
    log "ref made: git archive 31c0c36 -> $REF (+ data symlinks)"
  fi
  touch $OUT/ref.ready
else
  t=0; while [ ! -e $OUT/ref.ready ] && [ $t -lt 600 ]; do sleep 5; t=$((t+5)); done
fi
H="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
A8="seed=0 data.labeled_fraction=1.0 training.total_steps=4000 training.warmup_steps=200 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=4000 training.encoder_pf.freeze=200 training.encoder_pf.ramp=200 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0 model.name=hrstem_unetpp model.backbone=convnext_tiny.dinov3_lvd1689m model.backbone_weights=/home/noob/work/weights/dinov3_convnext_tiny_lvd1689m_timm.safetensors model.backbone_weights_format=timm model.backbone_drop_path=0.0"
card_opts() { (cd $NEW && $P -m bench.cards opts bench/methods/$1.yaml --seed 5 --run-name idw2_$1 --data-root $R0 | tr '\n' ' '); }

if [ "$LANE" = A ]; then
  declare -A OPT=([SUP]="$H" [SUPPF]="$H $PF" [SKR01]="$H $PF loss.skel_recall.weight=0.1" [A8]="$A8"
                  [PFV11]="$(card_opts house_r34_unetpp_pf_v11)" [HV11]="$(card_opts house_r34_unetpp_v11)")
  mkdir -p $OUT/id
  for arm in SUP SUPPF SKR01 A8 PFV11 HV11; do
    for side in ref new; do
      code=$REF; [ $side = new ] && code=$NEW
      nice -n 19 $P $ID --code $code --out $OUT/id/${arm}_$side.json --steps 5 --threads 4 --opts ${OPT[$arm]} > $OUT/id/${arm}_$side.log 2>&1
      rc=$?; log "id $arm $side rc=$rc"
    done
    $P $CMP $OUT/id/${arm}_ref.json $OUT/id/${arm}_new.json > $OUT/id/${arm}_cmp.txt 2>&1
    rc=$?; log "id $arm compare rc=$rc: $(cat $OUT/id/${arm}_cmp.txt)"
  done
  # baseline card: rendered config at 31c0c36 == at bench_w2 for the 10 W1-G jobs; W1-G's own config_used.yaml passes cfgcheck at bench_w2
  nr=0; ns=0; nc=0
  for k in 0 1 2 3 4; do for s in 5 6; do
    n=w1g_pf_v11_f${k}_s$s; r=/home/noob/work/bench_data/roots/cv5v2_v11_f$k
    a=$(cd $REF && $P -m bench.cards render bench/methods/house_r34_unetpp_pf_v11.yaml --seed $s --run-name $n --data-root $r | md5sum | cut -c1-32)
    b=$(cd $NEW && $P -m bench.cards render bench/methods/house_r34_unetpp_pf_v11.yaml --seed $s --run-name $n --data-root $r | md5sum | cut -c1-32)
    nr=$((nr+1)); [ "$a" = "$b" ] && ns=$((ns+1))
    c=/home/noob/work/el_bench/experiments/$n/config_used.yaml
    if [ -s $c ]; then m=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/house_r34_unetpp_pf_v11.yaml --config $c --seed $s --run-name $n --data-root $r); [ "$m" = "config OK (= card)" ] && nc=$((nc+1)); log "baseline cfgcheck at bench_w2 $n: $m"; fi
  done; done
  log "baseline card house_r34_unetpp_pf_v11 rendered config md5 at 31c0c36 == at bench_w2: $ns of $nr; W1-G config_used.yaml cfgcheck OK at bench_w2: $nc of 10"
  log "card md5 house_r34_unetpp_pf_v11: ref $(md5sum < $REF/bench/methods/house_r34_unetpp_pf_v11.yaml | cut -c1-8) new $(md5sum < $NEW/bench/methods/house_r34_unetpp_pf_v11.yaml | cut -c1-8); configs/ diff: $(diff -rq $REF/configs $NEW/configs | wc -l) files"
  (cd $NEW && OMP_NUM_THREADS=4 nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1)
  rc=$?; log "pytest full suite bench_wt_w2 rc=$rc: $(tail -1 $OUT/pytest_all.log)"
  log "lane A done"
fi

if [ "$LANE" = B ]; then
  E=$IO/exp; mkdir -p $E
  S="training.total_steps=5 training.val_every=5 training.checkpoint_every=5 training.num_workers=2 training.log_every=1 logging.experiments_dir=$E"
  smoke() {  # name code card extra...
    local name=$1 code=$2 card=$3; shift 3
    local o; o=$(cd $NEW && $P -m bench.cards opts bench/methods/$card.yaml --seed 5 --run-name $name --data-root $R0) || { log "smoke $name: opts FAIL"; return; }
    (cd $code && nice -n 19 $P scripts/train.py --config configs/supervised.yaml --device cpu --opts $o $S "$@" > $E/$name.stdout 2>&1)
    rc=$?
    local cc; cc=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/$card.yaml --config $E/$name/config_used.yaml --seed 5 --run-name $name --data-root $R0 | grep -o "^[A-Za-z ]*[0-9]*" | head -1)
    log "smoke $name ($card, code $(basename $code)) rc=$rc tracebacks $(grep -c Traceback $E/$name.stdout) nan $(grep -ci 'loss.*nan' $E/$name/train.log) $(grep -o 'Labelled: [0-9]*' $E/$name/train.log | head -1) | cfgcheck vs card (5-step overrides expected): $cc | $(grep -o 'RCS: T.*' $E/$name/train.log | head -1) $(grep -o 'WAVG BN recal: .*cells' $E/$name/train.log | head -1) probe lines $(grep -c 'ENC probe step' $E/$name/train.log)"
  }
  smoke w2s_pf_ref $REF house_r34_unetpp_pf_v11
  smoke w2s_pf_new $NEW house_r34_unetpp_pf_v11
  smoke w2s_rcs $NEW rcs_pf_v11
  smoke w2s_sbj $NEW soft_band_jml
  smoke w2s_jmlh $NEW jml_hard
  smoke w2s_spd $NEW encoder_spd_pf_v11
  smoke w2s_spd_ctrl $NEW encoder_spd_ctrl_pf_v11
  smoke w2s_ema $NEW ema_wise_posthoc_pf_v11
  smoke w2s_swad $NEW swad_const_pf_v11 training.weight_avg.swad.start=2 training.weight_avg.swad.end=4 training.enc_probe_every=2
  (cd $NEW && nice -n 19 $P $IO/w2_smoke_check.py $E) > $OUT/smoke_check.txt 2>&1
  rc=$?; log "smoke check rc=$rc: $(tr '\n' ';' < $OUT/smoke_check.txt)"
  log "lane B done"
fi
