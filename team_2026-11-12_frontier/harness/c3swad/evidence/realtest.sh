#!/bin/bash
# c3swad real-tool dry test on gaint CPU (nice 19, no GPU): the patched slim_ckpt.py and the unpatched bench_infer.py
# (89b9ea5 archive) on the real 20k-step swad checkpoint of w2a_swad_f0_s5 (read through symlinks; nothing is written
# outside the scratch folder).
set -u
S=${S:?}; A=$S/a; Bt=$S/b; R=${R:-$S/real}; P=/home/noob/work/el-fault-detection/.venv/bin/python
SRC=/home/noob/work/bench_wt_w2/experiments/w2a_swad_f0_s5; n=w2a_swad_f0_s5
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1
[ -e $R ] && { echo "REFUSED: $R exists"; exit 1; }
lg(){ echo "[$(date '+%F %T')] $*"; }
mk(){ mkdir -p $R/$1/experiments/$n/checkpoints; ln -s $SRC/config_used.yaml $R/$1/experiments/$n/config_used.yaml; }
for v in old new keys; do mk $v; ln -s $SRC/checkpoints/latest.pth $R/$v/experiments/$n/checkpoints/latest.pth; done
lg "start; latest.pth $(stat -L -c %s $SRC/checkpoints/latest.pth) bytes"
(cd $R/old && nice -n 19 $P $A/bench/q/cv02/slim_ckpt.py --run experiments/$n > $R/slim_old.log 2>&1); lg "slim old (unpatched, all keys) rc=$?: $(cut -c1-200 $R/slim_old.log | tail -1)"
(cd $R/new && nice -n 19 $P $Bt/bench/q/cv02/slim_ckpt.py --run experiments/$n > $R/slim_new.log 2>&1); lg "slim new (patched, no --keys) rc=$?: $(cut -c1-200 $R/slim_new.log | tail -1)"
(cd $R/keys && nice -n 19 $P $Bt/bench/q/cv02/slim_ckpt.py --run experiments/$n --keys swad_bn,swad > $R/slim_keys.log 2>&1); lg "slim new --keys swad_bn,swad rc=$?: $(cut -c1-200 $R/slim_keys.log | tail -1)"
for v in old new keys; do f=$R/$v/experiments/$n/checkpoints/slim.pth; lg "slim $v: $(stat -c %s $f 2>/dev/null) bytes md5 $(md5sum < $f | cut -c1-32)"; done
# refusals of --keys, each in a FRESH run dir (review F9: in the first version this ran where slim.pth already existed,
# so it showed "refuse: slim.pth exists" and never reached the key check)
for v in badkey twice; do mk $v; ln -s $SRC/checkpoints/latest.pth $R/$v/experiments/$n/checkpoints/latest.pth; done
(cd $R/badkey && nice -n 19 $P $Bt/bench/q/cv02/slim_ckpt.py --run experiments/$n --keys swad_bn,nokey > $R/slim_badkey.log 2>&1); lg "slim --keys swad_bn,nokey (a key that does not exist) rc=$? (must be non-zero); slim.pth written: $(ls $R/badkey/experiments/$n/checkpoints/slim.pth 2>/dev/null | wc -l) (must be 0); last line: $(tail -1 $R/slim_badkey.log | cut -c1-160)"
(cd $R/twice && nice -n 19 $P $Bt/bench/q/cv02/slim_ckpt.py --run experiments/$n --keys swad,swad > $R/slim_twice.log 2>&1); lg "slim --keys swad,swad (a key twice) rc=$? (must be non-zero); slim.pth written: $(ls $R/twice/experiments/$n/checkpoints/slim.pth 2>/dev/null | wc -l) (must be 0); last line: $(tail -1 $R/slim_twice.log | cut -c1-160)"
# a run dir whose latest.pth is the 2-key slim (as on gaint after a relay): both dumps as cq.sh renders them, on CPU
mk slimrun; ln -s $R/keys/experiments/$n/checkpoints/slim.pth $R/slimrun/experiments/$n/checkpoints/latest.pth
C=bench/methods/swad_const_pf_v11.yaml
D="--run $R/slimrun/experiments/$n --set cv5v2_f0 --dumps $R/dumps --method swad_const_pf_v11 --card $C"
(cd $A && nice -n 19 $P -u scripts/bench_infer.py $D --run-id $n --device cpu --precision fp32 --threads 8 --workers 0 --batch 8 --bench-run dump_$n > $R/dump1.log 2>&1); lg "dump usual (key auto) rc=$? Traceback $(grep -c Traceback $R/dump1.log): $(grep '^dumped ' $R/dump1.log | cut -c1-150)"
(cd $A && nice -n 19 $P -u scripts/bench_infer.py $D --run-id $n.swad --weights-key swad --device cpu --precision fp32 --threads 8 --workers 0 --batch 8 --bench-run dump_$n.swad > $R/dump2.log 2>&1); lg "dump further (key swad) rc=$? Traceback $(grep -c Traceback $R/dump2.log): $(grep '^dumped ' $R/dump2.log | cut -c1-150)"
for d in $n $n.swad; do m=$R/dumps/elbench1/swad_const_pf_v11/$d/cv5v2_f0/manifest.json; lg "manifest $d: $($P -c 'import json,sys; m=json.load(open(sys.argv[1])); print({k: m[k] for k in ("run_id","weights_key","step","seed","fold","set","device","precision","n_cells")})' $m 2>&1) | $(du -sm $R/dumps/elbench1/swad_const_pf_v11/$d | cut -f1) MB, BENCH_START line: $(grep -m1 '^BENCH_START' $R/dump${d: -4}.log 2>/dev/null)"; done
lg "BENCH_START lines: $(grep -h -m1 'BENCH_START' $R/dump1.log) | $(grep -h -m1 'BENCH_START' $R/dump2.log)"
# which weight set did each CPU dump use? share of equal pred px against the gaint GPU dumps of the same run (pred only)
G=/home/noob/work/bench_dumps/w2a/elbench1/swad_const_pf_v11
nice -n 19 $P - $R/dumps/elbench1/swad_const_pf_v11 $G $n <<'PY' 2>&1 | while read -r l; do lg "$l"; done
import sys
from pathlib import Path
import numpy as np
mine, gpu, n = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
def agree(a, b):
    eq = tot = 0
    for f in sorted(a.glob("*.npz")):
        x = np.load(f)["pred"]; y = np.load(b / f.name)["pred"]
        eq += int((x == y).sum()); tot += x.size
    return eq / tot, tot
for m in (n, n + ".swad"):
    for g in (n + ".swad_bn", n + ".swad"):
        s, t = agree(mine / m / "cv5v2_f0", gpu / g / "cv5v2_f0")
        print(f"pred px equal, CPU dump {m} vs GPU dump {g}: {s:.6f} of {t}")
PY
lg "ALL DONE"
