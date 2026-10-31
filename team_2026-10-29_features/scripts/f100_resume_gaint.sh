#!/bin/bash
# protocol_100 recovery after the gaint reboot at 16:28 IST 30 Oct: resume the three wave-2 runs (s1) from their atomic
# checkpoints/latest.pth with train.py --resume (same opts as the queue, val off, no --overwrite), output appended to the run's
# stdout (pre-reboot copy kept as <run>.prereboot.stdout for the identity diff over the re-computed steps), "trained <run> rc=N"
# lines in reports/f100/launch.log (rc captured before $(date)) so the opening-1 trigger counts them. Each start through the
# f100 gate (flock, >= 9,000 MiB free, >= 120 s after the last start). After the three resumes have started, the queue
# (skips existing run dirs: continues with s2) and the opening trigger are restarted in their own tmux windows.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python; L=reports/f100/launch.log
B="data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
PF="training.encoder_pf.freeze=1000 training.encoder_pf.ramp=1000 training.encoder_pf.lr_mult=0.1 training.encoder_pf.wd=0"
ENC=/home/noob/work/el_f1/experiments/f1_mim_pre_s0/encoder_final.pth
VAL="training.val_every=20000"
[ "$(cat REVISION)" = e544133 ] && [ "$(git rev-parse --short HEAD)" = e544133 ] || { echo "[$(date)] resume: deploy check FAIL" >> $L; exit 1; }
gate_wait(){ while :; do
  ok=$(flock reports/f100/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f100/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f100/last_start; echo 1; else echo 0; fi' _ "$1")
  [ "$ok" = 1 ] && break; sleep 30; done; }
echo "[$(date)] runner: RECOVERY after the gaint reboot (16:28): resuming the wave-2 runs from latest.pth" >> $L
for j in "f3_SUP_100pct_s1|1|" "f3_SUPPF_100pct_s1|1|$PF" "f3_MIMPF_100pct_s1|1|$PF model.encoder_init=$ENC"; do
  IFS='|' read -r name k extra <<< "$j"
  [ -e experiments/$name.prereboot.stdout ] || cp -p experiments/$name.stdout experiments/$name.prereboot.stdout
  gate_wait 9000
  echo "[$(date)] resume $name from checkpoints/latest.pth (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
  echo "===== RESUME after the gaint reboot of 30 Oct 16:28 (train.py --resume from checkpoints/latest.pth) =====" >> experiments/$name.stdout
  ( HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --resume --config configs/supervised.yaml --opts seed=$k $B \
      $extra $VAL run_name=$name >> experiments/$name.stdout 2>&1
    rc=$?; echo "[$(date)] trained $name rc=$rc (resumed)" >> $L ) &
done
echo "[$(date)] runner: three resumes started; restarting the queue (skips existing run dirs) and the opening trigger" >> $L
tmux new-window -d -t "=f100r:" -n queue "cd /home/noob/work/el_f3; VAL=training.val_every=20000 MAXC=3 bash reports/f100_queue.sh; exec bash"
tmux new-window -d -t "=f100r:" -n post "bash /home/noob/work/el_f3/reports/f100_postwatch.sh; exec bash"
wait
