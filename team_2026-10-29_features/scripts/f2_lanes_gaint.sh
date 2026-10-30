#!/bin/bash
# DDeP5 + CP5 lanes on gaint (protocol_ddep5 v1, protocol_cp5 v1; deploy commit 2751aa8; shared A5c-f1).
# tmux =f2g, el_f2, log reports/f2g/launch.log. Concurrency stays at 3 with the MIM5 lanes: each f2 lane starts only
# after one MIM5-experiment lane has launched its last run and finished it.
#   X (after f1g M2 done: f1_MIM_5pct_s3 rescored): CP smoke 2k -> decoy go/no-go (CP_PASS / CP_FAIL) ->
#       F2-DDeP gate (200-step fine-tune with decoder_final.pth, md5 match) -> DDeP5 s0, s2, s4
#   Y (after f1g M1 done: f1_MIM_5pct_s4 rescored): wait DDEP_PASS -> DDeP5 s1, s3 -> if CP_PASS: CP5 s0, s2
#   Z (after f1g A lane done: f1_A_5pct_s4 rescored): wait CP_PASS or CP_FAIL -> if CP_PASS: CP5 s1, s3, s4
# Every run waits for its own peak + 2 GB free (fine-tune 9 GB, CP 12 GB).
set -u
cd /home/noob/work/el_f2
S=f2g; G=reports/$S; L=$G/launch.log; F1L=/home/noob/work/el_f1/reports/f1g/launch.log
mkdir -p $G experiments
P=/home/noob/work/el-fault-detection/.venv/bin/python
DEC=/home/noob/work/cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/decoder_final.pth
CPO="cp.lambda=1.0 cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.bg_train_exclude=data/splits/d7_twin_train_cells.txt"
cat > $G/run_one.sh <<'EOS'
#!/bin/bash
# run_one.sh <run name> <seed> <free MiB gate> <extra opts...>: wait, train, rescore (rc captured before $(date))
set -u
cd /home/noob/work/el_f2
L=reports/f2g/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
name=$1; k=$2; gate=$3; shift 3
[ -e experiments/$name ] && { echo "[$(date)] skip $name (exists)" >> $L; exit 0; }
while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "$gate" ]; do sleep 60; done
echo "[$(date)] start $name (free $(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0) MiB)" >> $L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 $P -u scripts/train.py --overwrite --config configs/supervised.yaml --opts \
  seed=$k data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 \
  data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice \
  "$@" run_name=$name > experiments/$name.stdout 2>&1
rc=$?; echo "[$(date)] trained $name rc=$rc" >> $L
if [ $rc -eq 0 ]; then
  $P scripts/rescore_label_versions.py --runs $name --out reports/f2g/$name.json > experiments/$name.rescore.log 2>&1
  rc2=$?; echo "[$(date)] rescored $name rc=$rc2" >> $L
fi
EOS
cat > $G/x_gates.sh <<EOS
#!/bin/bash
# CP smoke + decoy go/no-go, then the F2-DDeP gate
set -u
cd /home/noob/work/el_f2
L=$L; P=$P; OUT=reports/f2/checks
wfree(){ while [ "\$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0)" -lt "\$1" ]; do sleep 30; done; }
OPTS="seed=0 data.labeled_fraction=0.05 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
wfree 12000; echo "[\$(date)] CP smoke start" >> \$L
HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 \$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 2000 --opts \$OPTS $CPO run_name=cpsmoke_s0 logging.experiments_dir=\$OUT > \$OUT/cpsmoke_s0.stdout 2>&1
echo "[\$(date)] CP smoke done: \$(grep 'step 2000/20000' \$OUT/cpsmoke_s0.stdout | cut -c1-420)" >> \$L
wfree 5000; HF_HUB_OFFLINE=1 \$P scripts/cp_decoy.py --runs \$OUT/i1f2_A_s0 \$OUT/cpsmoke_s0 --out \$OUT/decoy_2k.json > \$OUT/decoy_2k.log 2>&1
\$P - <<'PY' >> \$L 2>&1
import json, pathlib
r = json.load(open("reports/f2/checks/decoy_2k.json"))
a, c = r["runs"]["i1f2_A_s0"], r["runs"]["cpsmoke_s0"]
flag = c["decoy"] > 2 * a["decoy"] or c["decoy"] > 0.05
print(f"decoy go/no-go: A5c 2k real {a['real']:.4f} decoy {a['decoy']:.4f} bg {a['background']:.4f} | CP 2k real {c['real']:.4f} decoy {c['decoy']:.4f} bg {c['background']:.4f} | cells {r['n_cells']} comps {r['n_components']} -> {'FAIL (shortcut flag)' if flag else 'PASS'}")
pathlib.Path("reports/f2g/CP_FAIL" if flag else "reports/f2g/CP_PASS").touch()
PY
until [ -s $DEC ] && [ -s ${DEC%.pth}.md5 ]; do sleep 120; done
want=\$(cut -d" " -f1 ${DEC%.pth}.md5); have=\$(md5sum < $DEC | cut -c1-32)
[ "\$want" = "\$have" ] || { echo "[\$(date)] decoder_final md5 mismatch \$have vs \$want: STOP" >> \$L; exit 1; }
wfree 9000; HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4 \$P scripts/train.py --config configs/supervised.yaml --overwrite --exit_after_step 200 --opts \$OPTS model.decoder_init=$DEC run_name=f2ddep_gate_s0 logging.experiments_dir=\$OUT > \$OUT/f2ddep_gate_s0.stdout 2>&1
got=\$(grep -o "Decoder initialised from .*md5 [0-9a-f]*" \$OUT/f2ddep_gate_s0.stdout | grep -o "[0-9a-f]\{32\}\$")
nl=\$(grep -c "step [0-9]*/20000  loss=" \$OUT/f2ddep_gate_s0.stdout); bad=\$(grep -E "step [0-9]+/20000  loss=" \$OUT/f2ddep_gate_s0.stdout | grep -ciE "loss=(nan|inf)")
echo "[\$(date)] F2-DDeP want \$want got \$got loss lines \$nl nonfinite \$bad" >> \$L
if [ -n "\$got" ] && [ "\$got" = "\$want" ] && [ "\$nl" -ge 4 ] && [ "\$bad" -eq 0 ]; then touch reports/f2g/DDEP_PASS; echo "[\$(date)] F2-DDeP PASS" >> \$L; else echo "[\$(date)] F2-DDeP FAIL" >> \$L; exit 1; fi
EOS
chmod +x $G/run_one.sh $G/x_gates.sh
tmux has-session -t "=$S" 2>/dev/null && { echo "session $S exists; abort"; exit 1; }
tmux new-session -d -s $S -n ctl "bash"
R1="bash $G/run_one.sh"
tmux new-window -d -t "=$S:" -n X "cd /home/noob/work/el_f2; until grep -qE 'rescored f1_MIM_5pct_s3 |trained f1_MIM_5pct_s3 rc=[1-9]' $F1L; do sleep 120; done; bash $G/x_gates.sh || exit 1; for k in 0 2 4; do $R1 f2_DDeP_5pct_s\$k \$k 9000 model.decoder_init=$DEC; done; exec bash"
tmux new-window -d -t "=$S:" -n Y "cd /home/noob/work/el_f2; until grep -qE 'rescored f1_MIM_5pct_s4 |trained f1_MIM_5pct_s4 rc=[1-9]' $F1L; do sleep 120; done; until [ -e $G/DDEP_PASS ]; do sleep 120; done; for k in 1 3; do $R1 f2_DDeP_5pct_s\$k \$k 9000 model.decoder_init=$DEC; done; [ -e $G/CP_PASS ] && for k in 0 2; do $R1 f2_CP_5pct_s\$k \$k 12000 $CPO; done; exec bash"
tmux new-window -d -t "=$S:" -n Z "cd /home/noob/work/el_f2; until grep -qE 'rescored f1_A_5pct_s4 |trained f1_A_5pct_s4 rc=[1-9]' $F1L; do sleep 120; done; until [ -e $G/CP_PASS ] || [ -e $G/CP_FAIL ]; do sleep 120; done; [ -e $G/CP_PASS ] && for k in 1 3 4; do $R1 f2_CP_5pct_s\$k \$k 12000 $CPO; done; exec bash"
echo "[$(date)] f2g lanes X/Y/Z created (commit $(git rev-parse --short HEAD))" >> $L
tmux list-windows -t "=$S"
