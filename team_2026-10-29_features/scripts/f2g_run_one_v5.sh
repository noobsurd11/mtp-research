#!/bin/bash
# run_one.sh <run name> <seed> <free MiB gate> <extra opts...>: wait, train, rescore (rc captured before $(date))
set -u
cd /home/noob/work/el_f2
L=reports/f2g/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
name=$1; k=$2; gate=$3; shift 3
# v5 (runner 30 Oct 05:4x): CP gate from the measured peak: f2_CP_5pct_s1 held 9,526 MiB, constant over 16k steps incl.
# val/ckpt (memwatch 02:45-03:00 + nvidia-smi 05:43); + 2,048 = 11,574 -> 11,600. Lanes still pass the 12,000 pre-run estimate.
case "$name" in f2_CP_*) [ "$gate" -eq 12000 ] && gate=11600;; esac
[ -e experiments/$name ] && { echo "[$(date)] skip $name (exists)" >> $L; exit 0; }
# coach 29 Oct 20:3x: no f2 fine-tune starts before the f1g 'after' window is done (MIM5 post + val-only AM), so the
# post's m0_audit passes and AM never lose memory to an f2 run (x_gates' CP smoke / decoy / F2-DDeP gate not held)
until grep -q 'AFTER-RUNS DONE' /home/noob/work/el_f1/reports/f1g/launch.log; do sleep 60; done
# v3 (runner 30 Oct 02:4x): atomic gate. At 02:36 three lanes passed the gate within 17 s on the same free reading
# (free fell to 2.2 GB). Now check-and-stamp runs under a lock and needs >= 120 s since the last f2 start, so the
# previous run's allocation is visible before the next gate reading.
gate_wait(){  # $1 = MiB: atomic check-and-stamp under the lock, >= 120 s since the last f2 start
  while :; do
    ok=$(flock reports/f2g/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f2g/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f2g/last_start; echo 1; else echo 0; fi' _ "$1")
    [ "$ok" = 1 ] && break; sleep 60
  done
}
gate_wait "$gate"
echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts \
  seed=$k data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  "$@" run_name=$name > experiments/$name.stdout 2>&1
rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L
if [ $rc -eq 0 ]; then
  gate_wait 6000  # v4 (team-lead 30 Oct): end-of-run rescoring also through the gate (own peak ~3 GB + 2 GB)
  $P scripts/rescore_label_versions.py --runs $name --out reports/f2g/$name.json > experiments/$name.rescore.log 2>&1
  rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> $L
fi
