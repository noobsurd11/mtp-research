#!/bin/bash
# CP5 post on gaint (protocol_cp5): after all five CP5 runs are rescored rc 0, (1) f2_post_gaint.sh cp5 (m0 default + tau 0/1,
# LA, manifest), (2) decoy diagnostic E3b on the final checkpoints of both arms (A5c-f1 s0-4 at el_f1, CP5 s0-4), same
# held-out cells and thresholds as the 2k go/no-go, step 20000 asserted, (3) re-manifest. Gate as run_one.sh (6,000 MiB).
set -u
cd /home/noob/work/el_f2
L=/home/noob/work/el_f2/reports/f2g/launch.log; P=/home/noob/work/el-fault-detection/.venv/bin/python
OUT=reports/f2/post_cp5
until [ "$(grep -cE 'rescored f2_CP_5pct_s[0-4] rc=0' $L)" -ge 5 ] || grep -qE 'trained f2_CP_5pct_s[0-4] rc=[1-9]|rescored f2_CP_5pct_s[0-4] rc=[1-9]' $L; do sleep 120; done
if [ "$(grep -cE 'rescored f2_CP_5pct_s[0-4] rc=0' $L)" -lt 5 ]; then echo "[$(date)] f2 CP5 scoring not started: a CP5 run FAIL" >> $L; exit 1; fi
bash reports/f2/f2_post_gaint.sh cp5 f2_CP_5pct_s0 f2_CP_5pct_s1 f2_CP_5pct_s2 f2_CP_5pct_s3 f2_CP_5pct_s4 > reports/f2/post_cp5.log 2>&1
rc=$?; echo "[$(date)] f2 CP5 scoring done: post rc=$rc" >> $L; [ $rc -eq 0 ] || exit 1
gate_wait(){ while :; do ok=$(flock reports/f2g/gate.lock bash -c 'f=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i 0); '\
'a=$(( $(date +%s) - $(stat -c %Y reports/f2g/last_start 2>/dev/null || echo 0) )); '\
'if [ "$f" -ge "$1" ] && [ "$a" -ge 120 ]; then touch reports/f2g/last_start; echo 1; else echo 0; fi' _ "$1"); [ "$ok" = 1 ] && break; sleep 60; done; }
gate_wait 6000
HF_HUB_OFFLINE=1 $P scripts/cp_decoy.py --runs $(for k in 0 1 2 3 4; do echo /home/noob/work/el_f1/experiments/f1_A_5pct_s$k; done) \
  $(for k in 0 1 2 3 4; do echo experiments/f2_CP_5pct_s$k; done) --out $OUT/decoy_final.json > $OUT/decoy_final.log 2>&1
rc=$?
$P - <<'PY' >> $OUT/decoy_final.log 2>&1
import json
r = json.load(open("reports/f2/post_cp5/decoy_final.json"))["runs"]
assert all(v["step"] == 20000 for v in r.values()), {k: v["step"] for k, v in r.items()}
A = [r[f"f1_A_5pct_s{k}"]["decoy"] for k in range(5)]; C = [r[f"f2_CP_5pct_s{k}"]["decoy"] for k in range(5)]
ma, mc = sum(A) / 5, sum(C) / 5
print(f"E3b final decoy rate: A5c-f1 mean {ma:.4f} {[round(x, 4) for x in A]} | CP5 mean {mc:.4f} {[round(x, 4) for x in C]} -> "
      f"{'FLAG' if mc > 2 * ma or mc > 0.05 else 'no flag'} (CP > 2x A5c-f1 or > 0.05; reported, not a verdict)")
PY
(cd $OUT && find . -type f ! -name MANIFEST.md5 -print0 | sort -z | xargs -0 md5sum > MANIFEST.md5)
echo "[$(date)] f2 CP5 E3b decoy final rc=$rc: $(tail -1 $OUT/decoy_final.log | cut -c1-200)" >> $L
