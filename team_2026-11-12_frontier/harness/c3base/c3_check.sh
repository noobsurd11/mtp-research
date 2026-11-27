#!/bin/bash
# integrator c3base (16 Nov 2026): CPU proofs for the deploy tree bench_wt_final (bench_final). CPU only: CUDA_VISIBLE_DEVICES="",
# nice 19, OMP_NUM_THREADS=1 per process, at most 4 processes at once here (the 300-step fixture runs beside with 4 threads).
# References are fresh `git archive`s under $IO; no existing worktree is touched (el_bench/experiments/w1g_pf_v11_f2_s5 read only).
# 1. flag-off 5-step identity (identity_cpu.py 962379a6, compare_id.py 3b83b364) SUP, SUPPF, PFV11: archive 31c0c36 vs new.
# 2. 5-step CPU runs PF v11 and HOUSE v11 on cv5v3_v11_f0 (bench_data_v3b) and on cv5v2_v11_f0 (bench_data): rc, Traceback,
#    nan, Labelled line, cfgcheck vs card; config_used diff cv5v2 -> cv5v3; c3_rdiff.py on the 50 c3base tuples.
# 3. bench_infer plain path on a cv5v2 fold, archive ae4dd10 (deploy of the udev queues) vs new, w1g_pf_v11_f2_s5, --logp.
# 4. full pytest of bench_wt_final; render md5s of every reviewed card (c3_render.sh).
# Log: $IO/check/run.log. Usage: bash c3_check.sh (inside tmux bench_c3_check)
set -u
IO=/home/noob/work/bench_c3_io; OUT=$IO/check; mkdir -p $OUT/id $OUT/infer $OUT/render; L=$OUT/run.log
P=/home/noob/work/el-fault-detection/.venv/bin/python
ID=/home/noob/work/bench_check/identity_cpu.py; CMP=/home/noob/work/bench_check/compare_id.py
H=/home/yugma/mtp/research/team_2026-11-12_frontier/harness/c3base; HU=/home/yugma/mtp/research/team_2026-11-12_frontier/harness/udev
NEW=/home/noob/work/bench_wt_final; R0=/home/noob/work/bench_data/roots/cv5v2_v11_f0; V0=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
log() { echo "[$(date '+%F %T')] $*" >> $L; }
arch() { local c=$1 d=$IO/arch_$1
  if [ ! -d $d ]; then mkdir -p $d && git -C /home/noob/work/el_bench archive $c | tar -x -C $d && echo $c > $d/REVISION
    for x in labeled escdd_masks unlabeled; do ln -s "$(readlink $NEW/data/$x)" $d/data/$x; done
    log "archive $c -> $d ($(find $d -type f | wc -l) files)"; fi; }
log "start; new $NEW HEAD $(git -C $NEW rev-parse --short HEAD) tracked changes $(git -C $NEW status --porcelain -uno | wc -l); el_bench $(git -C /home/noob/work/el_bench rev-parse --short HEAD) changes $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l); identity_cpu $(md5sum < $ID | cut -c1-8); compare_id $(md5sum < $CMP | cut -c1-8); script $(md5sum < $0 | cut -c1-8)"
for c in 31c0c36 c57508e 52e3f14 b12fca8 ae4dd10; do arch $c; done
REF=$IO/arch_31c0c36
HS="seed=5 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice training.val_every=20000"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
PFV11=$(cd $NEW && $P -m bench.cards opts bench/methods/house_r34_unetpp_pf_v11.yaml --seed 5 --run-name idc3_pfv11 --data-root $R0 | tr '\n' ' ')
declare -A OPT=([SUP]="$HS" [SUPPF]="$HS $PF" [PFV11]="$PFV11")
E=$IO/exp; mkdir -p $E/v2 $E/v3
S5="training.total_steps=5 training.val_every=5 training.checkpoint_every=5 training.num_workers=0 training.log_every=1"
idrun() { local arm=$1 side=$2 code=$REF; [ $side = new ] && code=$NEW
  nice -n 19 $P $ID --code $code --out $OUT/id/${arm}_$side.json --steps 5 --threads 1 --opts ${OPT[$arm]} > $OUT/id/${arm}_$side.log 2>&1; log "id $arm $side rc=$?"; }
smoke() {  # name card root expdir
  local name=$1 card=$2 root=$3 ed=$4 o rc cc
  o=$(cd $NEW && $P -m bench.cards opts bench/methods/$card.yaml --seed 5 --run-name $name --data-root $root) || { log "smoke $name: opts FAIL"; return; }
  (cd $NEW && nice -n 19 $P scripts/train.py --config configs/supervised.yaml --device cpu --opts $o $S5 logging.experiments_dir=$ed > $ed/$name.stdout 2>&1)
  rc=$?
  cc=$(cd $NEW && $P -m bench.cards cfgcheck bench/methods/$card.yaml --config $ed/$name/config_used.yaml --seed 5 --run-name $name --data-root $root | sed -E "s#'$ed'#E#g")
  log "smoke $name ($card, root $root) rc=$rc Traceback $(grep -c Traceback $ed/$name.stdout) nan-loss lines $(grep -ciE 'loss[^|]*nan' $ed/$name/train.log) step-5 lines $(grep -c 'step 5/5' $ed/$name/train.log) latest.pth $(ls $ed/$name/checkpoints/latest.pth 2>/dev/null | wc -l) | $(grep -o 'Labelled: .*test: [0-9]*' $ed/$name/train.log | head -1) | want: Labelled: $(grep -c . $root/splits/train.txt) ($root/splits/train.txt) val $(grep -c . $root/splits/val.txt) test $(grep -c . $root/splits/test.txt) | cfgcheck vs card: $cc"; }
infer() {  # code tag
  (cd $1 && nice -n 19 $P scripts/bench_infer.py --run /home/noob/work/el_bench/experiments/w1g_pf_v11_f2_s5 --set cv5v2_f2 \
    --dumps $OUT/infer/$2 --method house_r34_unetpp_pf_v11 --card bench/methods/house_r34_unetpp_pf_v11.yaml \
    --run-id w1g_pf_v11_f2_s5 --weights-key model --device cpu --precision fp32 --threads 1 --workers 0 --batch 8 --logp \
    > $OUT/infer/$2.log 2>&1); log "infer $2 rc=$? ($(grep -c Traceback $OUT/infer/$2.log) Traceback)"; }
log "group 1 start (identity SUP, SUPPF)"
idrun SUP ref & idrun SUP new & idrun SUPPF ref & idrun SUPPF new & wait
log "group 2 start (identity PFV11; 5-step PF / HOUSE on cv5v3_v11_f0)"
idrun PFV11 ref & idrun PFV11 new &
smoke c3s_pf house_r34_unetpp_pf_v11 $V0 $E/v3 & smoke c3s_house house_r34_unetpp_v11 $V0 $E/v3 & wait
log "group 3 start (5-step PF / HOUSE on cv5v2_v11_f0; bench_infer ae4dd10 vs new)"
smoke c3s_pf house_r34_unetpp_pf_v11 $R0 $E/v2 & smoke c3s_house house_r34_unetpp_v11 $R0 $E/v2 &
infer $IO/arch_ae4dd10 ae4_logp & infer $NEW new_logp & wait
for arm in SUP SUPPF PFV11; do $P $CMP $OUT/id/${arm}_ref.json $OUT/id/${arm}_new.json > $OUT/id/${arm}_cmp.txt 2>&1; log "id $arm compare (ref 31c0c36 archive vs bench_final) rc=$?: $(cat $OUT/id/${arm}_cmp.txt)"; done
for n in c3s_pf c3s_house; do log "$n config_used cv5v2_v11_f0 -> cv5v3_v11_f0: $($P $H/c3_rdiff.py $NEW --pair $E/v2/$n/config_used.yaml $E/v3/$n/config_used.yaml 2>&1)"; done
log "c3_rdiff (50 c3base tuples, expected_config at bench_final): $(cd $NEW && $P $H/c3_rdiff.py $NEW 2>&1) rc=$?"
$P $HU/int_dumpcmp.py $OUT/infer/ae4_logp $OUT/infer/new_logp > $OUT/infer/cmp_logp.txt 2>&1
log "bench_infer --logp: ae4dd10 archive vs bench_final, w1g_pf_v11_f2_s5 on cv5v2_f2 (CPU fp32) rc=$?: $(cat $OUT/infer/cmp_logp.txt)"
log "group 4 start (full pytest; render)"
( cd $NEW && nice -n 19 $P -m pytest -q -p no:cacheprovider tests > $OUT/pytest_all.log 2>&1; log "pytest full suite bench_wt_final rc=$?: $(tail -1 $OUT/pytest_all.log)" ) &
( bash $H/c3_render.sh >> $L 2>&1 ) &
wait
log "done; new HEAD $(git -C $NEW rev-parse --short HEAD) tracked changes $(git -C $NEW status --porcelain -uno | wc -l) untracked $(git -C $NEW status --porcelain | grep -c '^??'); el_bench changes $(git -C /home/noob/work/el_bench status --porcelain -uno | wc -l)"
log "ALL DONE"
