#!/bin/bash
# protocol_100 gate 6b, part 2 (replaces the decision half of f100_gate6b.sh, whose main process was stopped at 12:1x so
# the rule could gain coach's condition 3; the a1 / b2 resume subshells it started keep running). Waits for both resumes
# to reach 4k, reruns cp_decoy (same 248 cells / 553 components), then GO needs all three (coach, pre-stated before 4k):
#   (1) CP_decoy_4k <= 0.05; (2) CP_decoy_4k <= 2 x SUP_decoy_4k OR CP_decoy_4k <= 0.0094; (3) CP_decoy_4k / CP_real_4k <= 0.036
# else STOP. Writes CP_GO / CP_STOP, logs real/decoy/background of both runs, the three conditions and the decision, removes HOLD.
set -u
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
O=reports/f100/smoke; L=reports/f100/launch.log
echo "[$(date)] gate 6b part 2 started (rule now has coach's condition 3: CP decoy/real at 4k <= 3.6%); waiting for the a1/b2 4k resumes" >> $L
for n in a1_nosw_v500 b2_cp_v500; do
  until grep -q "exit_after_step=4000 reached" $O/${n}_4k.stdout; do
    if ! pgrep -f "run_name=$n logging.experiments_dir=$O" > /dev/null && ! grep -q "exit_after_step=4000 reached" $O/${n}_4k.stdout; then
      echo "[$(date)] gate 6b FAIL: $n resume ended without reaching 4k; HOLD kept" >> $L; exit 1; fi
    sleep 20; done
done
HF_HUB_OFFLINE=1 $P scripts/cp_decoy.py --runs $O/a1_nosw_v500 $O/b2_cp_v500 --labeled reports/f100/train_minus_cpexcl.txt \
  --out $O/decoy_4k.json > $O/decoy_4k.log 2>&1 || { echo "[$(date)] gate 6b FAIL: cp_decoy error; HOLD kept" >> $L; exit 1; }
D=$($P - <<'PY'
import json
r = json.load(open("reports/f100/smoke/decoy_4k.json")); a, c = r["runs"]["a1_nosw_v500"], r["runs"]["b2_cp_v500"]
assert a["step"] == 4000 and c["step"] == 4000 and r["n_cells"] == 248 and r["n_components"] == 553, (a["step"], c["step"], r["n_cells"], r["n_components"])
k1 = c["decoy"] <= 0.05; k2 = c["decoy"] <= 2 * a["decoy"] or c["decoy"] <= 0.0094; ratio = c["decoy"] / c["real"]; k3 = ratio <= 0.036
go = k1 and k2 and k3
print(f"{'GO' if go else 'STOP'} | SUP 4k real {a['real']:.4f} decoy {a['decoy']:.4f} bg {a['background']:.4f} | CP 4k real {c['real']:.4f} decoy {c['decoy']:.4f} bg {c['background']:.4f} | "
      f"(1) CP decoy <= 0.05: {k1}; (2) <= 2 x SUP ({2 * a['decoy']:.4f}) or <= 0.0094: {k2}; (3) CP decoy/real {ratio:.4f} <= 0.036: {k3} | cells {r['n_cells']} comps {r['n_components']}")
PY
) || { echo "[$(date)] gate 6b FAIL: decision script error; HOLD kept" >> $L; exit 1; }
case "$D" in GO*) touch reports/f100/CP_GO;; *) touch reports/f100/CP_STOP;; esac
echo "[$(date)] gate 6b (coach post-hoc amendment, 3 conditions): $D" >> $L
rm -f reports/f100/HOLD; echo "[$(date)] gate 6b: HOLD removed" >> $L
