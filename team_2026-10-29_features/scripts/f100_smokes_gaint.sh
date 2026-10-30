#!/bin/bash
# protocol_100 smokes at the deploy commit (el_f3 e544133), gaint, seed 0, 100% opts (coach / team-lead 30 Oct):
#  A identity (val every 500): a1 no switch 2k (I1 vs el_m i1_elm 1k; val-on reference; SUP 2k ckpt for the decoy),
#    a2 PF neutral + encoder_init=mim_step0 1k, a3 CP lambda 0 1k
#  B a1 vs b1 (no switch, val off) 2k; b2 CP lambda 1 val 500 2k (CP smoke + decoy go/no-go) vs b3 CP val off 2k
#  C c1 SUP100-PF 2k, c2 MIM100-PF 2k (layer3/4 cosine gate; F2-100 md5)
#  D d1 no switch + PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True 1k (identity + reserved memory)
# Starts: gate own peak + 2 GB (fine-tune 9,000, CP 11,600 MiB) and >= 90 s after the previous start. mem.log every 30 s.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; mkdir -p $O; L=$O/status.txt
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
PFN="training.encoder_pf.freeze=0 training.encoder_pf.ramp=0 training.encoder_pf.lr_mult=1.0 training.encoder_pf.wd=0.0001"
CPC="cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.library_exclude=data/splits/d7_twin_train_cells.txt"
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
S0=/home/noob/work/el_f1/reports/f1/smoke_v1/mim_step0.pth
VOFF="training.val_every=20000"
echo "[$(date +%T)] smokes start, code $(cat REVISION) ($(git rev-parse --short HEAD))" > $L
( while [ ! -e $O/ALLDONE ]; do echo "$(date +%T) $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | tr '\n' ' ') | free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits)" >> $O/mem.log; sleep 30; done ) &
MEMPID=$!; PIDS=()
LAST=0
gate(){ while :; do f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)
  [ "$f" -ge "$1" ] && [ $(( $(date +%s) - LAST )) -ge 90 ] && break; sleep 20; done; LAST=$(date +%s); }
run(){ name=$1; g=$2; steps=$3; envx=$4; shift 4; gate $g; echo "[$(date +%T)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0))" >> $L
  ( env $envx $P -u scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step $steps --opts $B "$@" \
      run_name=$name logging.experiments_dir=$O > $O/$name.stdout 2>&1; echo "[$(date +%T)] $name rc=$?" >> $L ) & PIDS+=($!); }
run a1_nosw_v500 9000 2000 X=0
run a2_pfneutral_step0 9000 1000 X=0 $PFN model.encoder_init=$S0
run a3_cp_l0 9000 1000 X=0 cp.lambda=0 $CPC
run b1_nosw_voff 9000 2000 X=0 $VOFF
run c1_suppf 9000 2000 X=0 $PF
run c2_mimpf 9000 2000 X=0 $PF model.encoder_init=$ENC
run b2_cp_v500 11600 2000 X=0 cp.lambda=1.0 $CPC
run b3_cp_voff 11600 2000 X=0 cp.lambda=1.0 $CPC $VOFF
run d1_nosw_expseg 9000 1000 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
wait "${PIDS[@]}"
touch $O/ALLDONE; kill $MEMPID 2>/dev/null; echo "[$(date +%T)] ALLDONE" >> $L
