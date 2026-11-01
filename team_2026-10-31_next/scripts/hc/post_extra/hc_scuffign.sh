#!/bin/bash
# HC post_extra hook (hc_post.sh runs it behind the GS gate with OUT, RUNS set; reported only, non-fatal): scuff-ignored test pass,
# descriptive (protocol_HC §6 = protocol_PF2 §4.3, Om B2). PF2's frozen pf2_scuffign.py (e3615fdb, copy in nq/hc/post_extra/) with
# --code el_hc (as pf2_scuffign.sh 2abfae02, paths only). Self-check first: the 2 cells' stats must equal this opening's m0 JSONs.
set -eu
cd /home/noob/work/el_hc
P=/home/noob/work/el-fault-detection/.venv/bin/python
HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 $P /home/noob/work/nq/hc/post_extra/pf2_scuffign.py --code /home/noob/work/el_hc --m0 $OUT/m0 \
  --out $OUT/m0_scuffign --runs $(for r in $RUNS; do echo /home/noob/work/el_hc/experiments/$r; done)
