#!/bin/bash
# c3x: tests of smoke/c3x_smoke.sh (slim, check) and smoke/c3x_smoke_check.py on the CPU fixture run (evidence/
# smoke_fixture_run.sh: real train.py of the c3x tree in FX/repo, real latest.pth and enc_probe.jsonl) with SYNTHETIC queue
# logs, gpumem lines and dump lines/manifests in the exact formats of bench_q.sh / bench_lib.sh / bench_gpumem.sh /
# bench_infer.py. Steps: the slim step through `c3x_smoke.sh slim` (real slim_ckpt.py); the check (--fixture) positive;
# then tampered copies (hard-link copies; a tampered file is always replaced, never written in place), each must FAIL its
# point: the five of fix round 1, and (review B1) a missing slim.pth, a slim.pth without the dumped key swad, a failed slim
# step (rc of slim_ckpt.py returned); and `c3x_smoke.sh check` returns the check's rc and keeps smoke_check.out (review N2).
# Usage: FX=<fixture dir with repo/experiments/smoke_c3x_path> bash smoke_fixture_check.sh
set -u
FX=${FX:?}; H=$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd); P=/home/noob/work/el-fault-detection/.venv/bin/python
E=$FX/repo/experiments; RT=/home/noob/work/bench_data_v3b/roots/cv5v3_v11_f0
rm -rf $FX/q $FX/dumps $FX/n; mkdir -p $FX/q/dump
W="Labelled: 425 ($RT/splits/train.txt)  unlabelled: 0 (-)  val: 107  test: 107"
{ for n in smoke_c3x_mem_hrnet smoke_c3x_mem_combo; do echo "[2026-11-17 18:30:00] $n config OK (= card)"; echo "[2026-11-17 18:30:05] $n startup line OK: $W"; echo "[2026-11-17 18:33:00] trained $n rc=3"; done
  echo "[2026-11-17 18:40:00] smoke_c3x_path config OK (= card)"; echo "[2026-11-17 18:40:05] smoke_c3x_path startup line OK: $W"; echo "[2026-11-17 18:46:00] trained smoke_c3x_path rc=0"; } > $FX/q/launch.log
{ echo "[2026-11-17 18:50:00] trained dump_smoke_c3x_path rc=0"; echo "[2026-11-17 18:52:00] trained dump_smoke_c3x_path.swad rc=0"; } > $FX/q/dump/launch.log
{ echo "18:31:00 20000 12000 | 6206:finllm_chat:5876 111:run_name=smoke_c3x_mem_hrnet:9480 "; echo "18:31:01 20000 12000 | 111:run_name=smoke_c3x_mem_hrnet:9512 "; echo "18:36:00 20000 12000 | 222:run_name=smoke_c3x_mem_combo:9700 "; echo "18:44:00 1 1 | 333:run_name=smoke_c3x_path:9750 "; } > $FX/q/gpumem.log
echo "[2026-11-17 18:53:00] phase 2 (dump queue) exited rc=0; end line: 1; chain done" > $FX/q/chain.log
for n in smoke_c3x_mem_hrnet smoke_c3x_mem_combo; do printf 'x\n2026-11-17 18:33:00 WARNING src.trainers.trainer — exit_after_step=300 reached: hard exit (simulated crash)\n' > $E/$n.stdout; done
LM=$(md5sum < $E/smoke_c3x_path/checkpoints/latest.pth | cut -c1-32)
for rk in "smoke_c3x_path swad_bn dump_smoke_c3x_path" "smoke_c3x_path.swad swad dump_smoke_c3x_path.swad"; do set -- $rk
  d=$FX/dumps/elbench1/smoke_c3x_hrnet_swad_path/$1/cv5v3_f0; mkdir -p $d
  printf 'BENCH_START: run=%s\ndumped %s cv5v3_f0: 107 cells, 132.6 MiB, ties 0, key %s, step 6, cpu/fp32, 60s -> %s\n' $3 $1 $2 $d > $E/$3.stdout
  echo "{\"run_id\": \"$1\", \"weights_key\": \"$2\", \"step\": 6, \"set\": \"cv5v3_f0\", \"checkpoint_md5\": \"$LM\", \"device\": \"cpu\", \"train_code_revision\": \"synthetic\"}" > $d/manifest.json; done
SM(){ Q_TEST=$1 R_TEST=$2 D_TEST=$FX/dumps X=x bash $H/smoke/c3x_smoke.sh "${@:3}"; }
CK(){ CUDA_VISIBLE_DEVICES="" PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 nice -n 19 $P $H/smoke/c3x_smoke_check.py --q $1 --repo $2 --dumps $FX/dumps --card $H/smoke/smoke_c3x_hrnet_swad_path.yaml --fixture; }
rm -f $E/smoke_c3x_path/checkpoints/slim.pth
echo "=== check before the slim step (B1: missing slim.pth must FAIL): $(CK $FX/q $FX/repo | grep -E '^FAIL|^# [0-9]' | tr '\n' ' ')"
echo "=== slim step through c3x_smoke.sh slim (real slim_ckpt.py of the c3x tree)"; SM $FX/q $FX/repo slim; echo "slim step rc $?"
out=$(SM $FX/q $FX/repo slim 2>&1); rc=$?; echo "=== slim step again (slim.pth exists): $(echo "$out" | tail -1); rc $rc"
echo "=== positive"; CK $FX/q $FX/repo; echo "rc $?"
cpx(){ local d=$FX/n/$1; mkdir -p $d; cp -r $FX/q $d/q; mkdir -p $d/repo; cp -al $FX/repo/experiments $d/repo/experiments; }
neg(){ # name, tamper command (cwd = the copy; replace files, never write in place)
  cpx $1; (cd $FX/n/$1 && eval "$2"); echo "=== negative $1: $(CK $FX/n/$1/q $FX/n/$1/repo | grep -E '^FAIL|^# [0-9]' | tr '\n' ' ')"; }
J=repo/experiments/smoke_c3x_path/enc_probe.jsonl; SL=repo/experiments/smoke_c3x_path/checkpoints/slim.pth
neg delta_1088 "sed -i 's/smoke_c3x_path:9750/smoke_c3x_path:10600/' q/gpumem.log"
neg loss_nan "sed -i '0,/ step 2\/6  loss=[0-9.]*/s// step 2\/6  loss=nan/' repo/experiments/smoke_c3x_path.stdout"
neg probe_cos_1 "python3 -c \"import json; r=[json.loads(x) for x in open('$J')]; r[0]['stages']['model']['cos']=1.0; open('$J.new','w').write(''.join(json.dumps(x)+'\n' for x in r))\" && mv $J.new $J"
neg lr_at_probe_0 "sed -i 's/PF encoder lr=[0-9.e-]* at step 3$/PF encoder lr=0 at step 3/' repo/experiments/smoke_c3x_path.stdout"
neg order_freeze_1000 "sed -i 's/^    freeze: 2$/    freeze: 1000/' repo/experiments/smoke_c3x_path/config_used.yaml"
neg slim_missing "rm $SL"
neg slim_without_swad "$P -c \"import torch; s=torch.load('$SL', map_location='cpu', weights_only=False); del s['models']['swad']; torch.save(s, '$SL.new')\" && mv $SL.new $SL"
# B1: a failed slim step returns slim_ckpt.py's rc (a run dir without latest.pth)
F=$FX/n/slim_fails; mkdir -p $F/repo/bench/q/cv02 $F/repo/experiments/smoke_c3x_path $F/q; cp $FX/repo/bench/q/cv02/slim_ckpt.py $F/repo/bench/q/cv02/; cp $FX/q/chain.log $F/q/
out=$(SM $F/q $F/repo slim 2>&1); rc=$?; echo "=== failed slim step: rc $rc; $(echo "$out" | grep -E 'Error|SLIM FAILED' | tail -2 | tr '\n' ' ')"
# N2: `c3x_smoke.sh check` (normal mode on this fixture: the 600-step schedule FAILs) returns the check's rc, keeps the output
cpx check_rc; out=$(SM $FX/n/check_rc/q $FX/n/check_rc/repo check 2>&1); rc=$?
echo "=== c3x_smoke.sh check: rc $rc; $(echo "$out" | tail -1); smoke_check.out $(test -s $FX/n/check_rc/q/smoke_check.out && echo kept); RULE gate read by c3x_queue.sh's pattern: $(grep -E $'^RULE\tgate\t' $FX/n/check_rc/q/smoke_check.out | tail -1 | sed -nE 's/.*job gate = max\(11000, P \+ 2,048\) = ([0-9]+) MiB.*/\1/p')"
