#!/bin/bash
# THIN-B3 launch gate 3 (coach 1 Nov): scorer identities on already-opened / val data, GPU through the shared gate (7,900).
#  (a) LA: el_thin scripts/rescore_logit_adjust.py vs el_f3's on f3_SUPPF_100pct_s0, val only, taus 0 1: JSON byte-identical
#      (same --runs string in both: ../../el_f3/experiments/f3_SUPPF_100pct_s0, which both ROOTs resolve to the same run).
#  (b) S4 at el_thin's current DEPLOY: m0_audit_b3.py without B3 flags on f3_SUPPF_100pct_s0 = opening-1 m0 JSON cells.
set -u
. /home/noob/work/el_f3/reports/pf2/scripts/gpu_gate.sh
P=/home/noob/work/el-fault-detection/.venv/bin/python; O=/home/noob/work/el_thin/reports/thin/idchk; mkdir -p $O; L=$O/idchk.log
R=../../el_f3/experiments/f3_SUPPF_100pct_s0
echo "[$(date)] thin idchk start: el_thin $(git -C /home/noob/work/el_thin rev-parse --short HEAD) (DEPLOY $(cat /home/noob/work/el_thin/reports/thin/DEPLOY)); LA md5 el_f3 $(md5sum < /home/noob/work/el_f3/scripts/rescore_logit_adjust.py | cut -c1-8) el_thin $(md5sum < /home/noob/work/el_thin/scripts/rescore_logit_adjust.py | cut -c1-8); m0_audit_b3 $(md5sum < /home/noob/work/el_thin/scripts/b3/m0_audit_b3.py | cut -c1-8)" >> $L
for W in el_f3 el_thin; do
  gate_wait 7900 "thin idchk LA $W"
  (cd /home/noob/work/$W && HF_HUB_OFFLINE=1 $P scripts/rescore_logit_adjust.py --runs $R --taus 0 1 --splits val --out $O/la_val_$W.json > $O/la_val_$W.log 2>&1)
  rc=$?; echo "[$(date)] LA val $W rc=$rc" >> $L
done
cmp $O/la_val_el_f3.json $O/la_val_el_thin.json && echo "[$(date)] (a) LA el_thin vs el_f3 on f3_SUPPF_100pct_s0 val: BYTE-IDENTICAL ($(md5sum < $O/la_val_el_f3.json | cut -c1-8))" >> $L \
  || echo "[$(date)] (a) LA el_thin vs el_f3: DIFFER" >> $L
gate_wait 7900 "thin idchk S4"
(cd /home/noob/work/el_thin && HF_HUB_OFFLINE=1 $P scripts/b3/m0_audit_b3.py --code /home/noob/work/el_thin --out $O/S4_m0 --ext /home/noob/work/el_f1/reports/f1/ext117 \
   --no-logits --runs /home/noob/work/el_f3/experiments/f3_SUPPF_100pct_s0 > $O/S4_m0.log 2>&1)
rc=$?; echo "[$(date)] (b) m0_audit_b3 rc=$rc" >> $L
$P - $O/S4_m0/f3_SUPPF_100pct_s0.json /home/noob/work/el_f3/reports/f100/post_opening1/m0/f3_SUPPF_100pct_s0.json >> $L 2>&1 <<'PY'
import json, sys
a, b = (json.load(open(f)) for f in sys.argv[1:3])
print("(b) S4 identity: m0_audit_b3 cells identical to opening-1 m0_audit.py:", a["cells"] == b["cells"], "| sets", sorted(a["cells"]), "| step", a["step"], b["step"])
PY
echo "[$(date)] thin idchk done" >> $L
