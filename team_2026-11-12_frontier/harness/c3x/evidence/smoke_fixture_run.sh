#!/bin/bash
# CPU fixture of the PATH smoke (after the lead's Q2 ruling): the smoke card's opts + tiny overrides that keep the ruled order
# of events (freeze 2, ramp 1 <= first probe 3 <= window start 4), real train.py of the c3x tree (archive of 852ed5c + c3x.patch),
# cv5v3 f0, then the slim step. Only for testing c3x_smoke_check.py on real formats. nice 19, 8 threads.
set -u
cd /tmp/claude-1003/-home-yugma-mtp/e0fe0a1b-de27-464f-816b-2df6724d18f1/scratchpad/t5 || exit 1
export CUDA_VISIBLE_DEVICES="" HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
N=smoke_c3x_path
O=$(/home/noob/work/el-fault-detection/.venv/bin/python -m bench.cards opts /home/yugma/mtp/research/team_2026-11-12_frontier/harness/c3x/smoke/smoke_c3x_hrnet_swad_path.yaml --seed 5 --run-name $N --data-root /home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0)
X="training.total_steps=6 training.enc_probe_every=3 training.weight_avg.swad.start=4 training.weight_avg.swad.end=6 training.encoder_pf.freeze=2 training.encoder_pf.ramp=1 model.input_size=128 data.input_size=128 training.labeled_batch_size=2 training.num_workers=2 training.log_every=1 logging.experiments_dir=/tmp/claude-1003/-home-yugma-mtp/e0fe0a1b-de27-464f-816b-2df6724d18f1/scratchpad/fx2/repo/experiments"
echo "[$(date '+%F %T')] train start"
nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python -u scripts/train.py --device cpu --config configs/supervised.yaml --opts $O $X > /tmp/claude-1003/-home-yugma-mtp/e0fe0a1b-de27-464f-816b-2df6724d18f1/scratchpad/fx2/repo/experiments/$N.stdout 2>&1; echo "train rc $?"
OMP_NUM_THREADS=2 nice -n 19 /home/noob/work/el-fault-detection/.venv/bin/python bench/q/cv02/slim_ckpt.py --run /tmp/claude-1003/-home-yugma-mtp/e0fe0a1b-de27-464f-816b-2df6724d18f1/scratchpad/fx2/repo/experiments/$N --keys swad_bn,swad; echo "slim rc $?"
echo "[$(date '+%F %T')] fixture done"
