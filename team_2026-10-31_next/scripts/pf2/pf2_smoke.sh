#!/bin/bash
# PF2 smoke on gaint (el_f3, deploy e544133, seed 0, 100% opts, val off; out reports/pf2/smoke). Not scored on test or E1.
#  r1 pf2s_rn50pf_s0: RN50-PF to 2,000 steps, started alone beside finllm: peak memory alone, steps/s alone; then 2k -> 4k
#     with train.py --resume (2k checkpoint kept as latest_2k.pth): PF layer3/4 cosine to ImageNet at 2k and 4k
#  r2 pf2s_sup_s0 (SUP100-g) and r3 pf2s_suppf_s0 (SUP100-PF), 1,000 steps, started beside r1: packing speed, and the step /
#     PF-lr lines vs protocol_100's smokes b1_nosw_voff / c1_suppf (same commit, opts, seed) after the 30 Oct reboot
#  m  RN50 scoring peaks on r1's 2k checkpoint (copy in pf2s_rn50pf_s0_2k): m0_audit --sets val, rescore_logit_adjust --splits val
# Gates (shared lock gpu_gate.sh, >= 120 s between starts): r1 16,000 MiB (RN50 peak not yet measured: a generous guess, disclosed);
# r2 / r3 9,000 (R34 fine-tune measured ~7 GB + 2 GB), not before r1 has run 240 s (its peak is in the 1 s gpumem log);
# r1 resume at r1's measured peak + 2,048; scoring passes 12,000 (guess: R34 LA 5,106 MiB, RN50 unknown, + 2 GB).
set -u
cd /home/noob/work/el_f3
. reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; F1=/home/noob/work/el_f1/reports/f1
O=reports/pf2/smoke; mkdir -p $O; L=$O/status.txt
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
VOFF="training.val_every=20000"; RN="model.encoder_name=resnet50"
[ "$(cat REVISION)" = e544133 ] && [ "$(git rev-parse --short HEAD)" = e544133 ] && [ -z "$(git status --short --untracked-files=no)" ] \
  || { echo "[$(date +%T)] deploy check FAIL" >> $L; exit 1; }
touch $GG/FAST
echo "[$(date +%T)] PF2 smoke start, code $(cat REVISION) pid $$" >> $L
PIDS=()
run(){ name=$1 gate=$2 steps=$3; shift 3; gate_wait $gate "smoke $name"
  echo "[$(date +%T)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
  ( $P -u scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step $steps --opts $B "$@" \
      run_name=$name logging.experiments_dir=$O > $O/$name.stdout 2>&1
    rc=$?; echo "[$(date +%T)] $name rc=$rc (3 = exit_after_step $steps, as designed)" >> $L ) &
  PIDS+=($!); echo "$name subshell $!" >> $O/pids.log; }
peak(){ grep -v '^#' reports/pf2/gpumem.log | grep -oE ":run_name=$1:[0-9]+" | cut -d: -f3 | sort -n | tail -1; }
run pf2s_rn50pf_s0 16000 2000 $PF $VOFF $RN
R1=${PIDS[0]}
sleep 240
echo "[$(date +%T)] r1 peak after 240 s: $(peak pf2s_rn50pf_s0) MiB" >> $L
run pf2s_sup_s0 9000 1000 $VOFF
run pf2s_suppf_s0 9000 1000 $PF $VOFF
wait $R1
D=$O/pf2s_rn50pf_s0; S=$O/pf2s_rn50pf_s0_2k
cp -p $D/checkpoints/latest.pth $D/checkpoints/latest_2k.pth
mkdir -p $S/checkpoints; cp -p $D/config_used.yaml $S/; cp -p $D/checkpoints/latest.pth $S/checkpoints/latest.pth
md5sum $D/checkpoints/latest_2k.pth $S/checkpoints/latest.pth >> $O/ckpt_md5.txt
PK=$(peak pf2s_rn50pf_s0); echo "[$(date +%T)] r1 2k done; RN50-PF peak (1 s samples) ${PK} MiB" >> $L
gate_wait $(( ${PK:-14000} + 2048 )) "smoke r1 resume"
echo "[$(date +%T)] resume pf2s_rn50pf_s0 2k -> 4k (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
( $P -u scripts/train.py --config configs/supervised.yaml --resume --exit_after_step 4000 --opts $B $PF $VOFF $RN \
    run_name=pf2s_rn50pf_s0 logging.experiments_dir=$O > $O/pf2s_rn50pf_s0_4k.stdout 2>&1
  rc=$?; echo "[$(date +%T)] pf2s_rn50pf_s0 4k rc=$rc (3 = exit_after_step 4000, as designed)" >> $L ) &
PIDS+=($!); echo "pf2s_rn50pf_s0_4k subshell $!" >> $O/pids.log
gate_wait 12000 "smoke m0 val rn50"
echo "[$(date +%T)] start m0_audit --sets val on the RN50 2k copy" >> $L
mkdir -p $O/m0val
$P $F1/m0_audit.py --code /home/noob/work/el_f3 --out $O/m0val --ext $F1/ext117 --sets val --no-logits --runs /home/noob/work/el_f3/$S > $O/m0val.log 2>&1
rc=$?; echo "[$(date +%T)] m0_audit val rc=$rc" >> $L
gate_wait 12000 "smoke LA val rn50"
echo "[$(date +%T)] start rescore_logit_adjust --splits val on the RN50 2k copy" >> $L
$P scripts/rescore_logit_adjust.py --runs ../$S --taus 0 1 --splits val --out $O/la_val.json > $O/la_val.log 2>&1
rc=$?; echo "[$(date +%T)] LA val rc=$rc" >> $L
wait "${PIDS[@]}"
rm -f $GG/FAST; touch $O/ALLDONE; echo "[$(date +%T)] ALLDONE" >> $L
bash reports/pf2/scripts/pf2_smoke_eval.sh
