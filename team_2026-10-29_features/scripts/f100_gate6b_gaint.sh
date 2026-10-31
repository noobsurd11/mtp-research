#!/bin/bash
# protocol_100 v1.1 gate 6b (coach, review_100_v1.md last section; post-hoc amendment, disclosed): one more pre-specified
# decoy point before any CP100 run and before opening 1. Resume a1 (SUP) and b2 (CP) from 2k to 4k (--resume, same opts),
# rerun cp_decoy on the same 248 held-out cells / 553 components, then:
#   GO   if CP_decoy_4k <= 0.05 AND (CP_decoy_4k <= 2 x SUP_decoy_4k OR CP_decoy_4k <= 0.0094)  -> touch reports/f100/CP_GO
#   STOP otherwise                                                                               -> touch reports/f100/CP_STOP
# The queue (launched alongside) starts its first fine-tune beside the two resumes; this script then sets reports/f100/HOLD
# so the next fine-tunes wait until the 4k decoy is scored, and removes HOLD afterwards. Lines go to reports/f100/launch.log.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; L=reports/f100/launch.log; mkdir -p reports/f100
export HF_HUB_OFFLINE=1 OMP_NUM_THREADS=4
B="seed=0 data.labeled_fraction=1.0 training.total_steps=20000 data.split_seed=0 training.labeled_batch_size=8 data.mask_subdir=labeled/masks_escdd model.name=smp_unetpp data.augmentation=labelsafe loss.supervised=ce_dice"
CPC="cp.lambda=1.0 cp.batch=4 cp.bg_pool_list=/home/noob/work/el_f1/reports/f1/mim_pool_v11.txt cp.heldout_list=/home/noob/work/el_f1/reports/f1/mim_monitor_v11.txt cp.library_exclude=reports/f100/cp100_library_exclude.txt"
for n in a1_nosw_v500 b2_cp_v500; do [ -e $O/$n/checkpoints/latest_2k.pth ] || cp -p $O/$n/checkpoints/latest.pth $O/$n/checkpoints/latest_2k.pth; done
echo "[$(date)] gate 6b: resume a1 (SUP) and b2 (CP) 2k -> 4k for the 4k decoy point" >> $L
flock reports/f100/gate.lock touch reports/f100/last_start
( $P -u scripts/train.py --config configs/supervised.yaml --resume --exit_after_step 4000 --opts $B run_name=a1_nosw_v500 \
    logging.experiments_dir=$O > $O/a1_nosw_v500_4k.stdout 2>&1; rc=$?; echo "[$(date)] gate 6b: a1 4k rc=$rc" >> $L ) & PA=$!
sleep 60
flock reports/f100/gate.lock touch reports/f100/last_start
( $P -u scripts/train.py --config configs/supervised.yaml --resume --exit_after_step 4000 --opts $B $CPC run_name=b2_cp_v500 \
    logging.experiments_dir=$O > $O/b2_cp_v500_4k.stdout 2>&1; rc=$?; echo "[$(date)] gate 6b: b2 4k rc=$rc" >> $L ) & PB=$!
until grep -q "start f3_SUP_100pct_s0" $L; do sleep 5; done
touch reports/f100/HOLD; echo "[$(date)] gate 6b: HOLD set after the first fine-tune start (next starts wait for the 4k decoy)" >> $L
wait $PA $PB
for n in a1_nosw_v500 b2_cp_v500; do grep -q "exit_after_step=4000 reached" $O/${n}_4k.stdout || { echo "[$(date)] gate 6b FAIL: $n did not reach 4k; HOLD kept" >> $L; exit 1; }; done
HF_HUB_OFFLINE=1 $P scripts/cp_decoy.py --runs $O/a1_nosw_v500 $O/b2_cp_v500 --labeled reports/f100/train_minus_cpexcl.txt \
  --out $O/decoy_4k.json > $O/decoy_4k.log 2>&1 || { echo "[$(date)] gate 6b FAIL: cp_decoy error; HOLD kept" >> $L; exit 1; }
D=$($P - <<'PY'
import json
r = json.load(open("reports/f100/smoke/decoy_4k.json")); a, c = r["runs"]["a1_nosw_v500"], r["runs"]["b2_cp_v500"]
assert a["step"] == 4000 and c["step"] == 4000 and r["n_cells"] == 248 and r["n_components"] == 553, (a["step"], c["step"], r["n_cells"], r["n_components"])
go = c["decoy"] <= 0.05 and (c["decoy"] <= 2 * a["decoy"] or c["decoy"] <= 0.0094)
print(f"{'GO' if go else 'STOP'} SUP 4k real {a['real']:.4f} decoy {a['decoy']:.4f} bg {a['background']:.4f} | CP 4k real {c['real']:.4f} decoy {c['decoy']:.4f} bg {c['background']:.4f} | cells {r['n_cells']} comps {r['n_components']}")
PY
) || { echo "[$(date)] gate 6b FAIL: decision script error; HOLD kept" >> $L; exit 1; }
case "$D" in GO*) touch reports/f100/CP_GO;; *) touch reports/f100/CP_STOP;; esac
echo "[$(date)] gate 6b (coach post-hoc amendment; GO if CP <= 0.05 and (CP <= 2 x SUP or CP <= 0.0094)): $D" >> $L
rm -f reports/f100/HOLD; echo "[$(date)] gate 6b: HOLD removed" >> $L
