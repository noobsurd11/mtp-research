#!/bin/bash
# post_extra hook (pf2_post.sh runs it behind the GS gate with OUT, RUNS set): scuff-ignored test pass, descriptive (protocol_PF2 4.3).
set -eu
cd /home/noob/work/el_f3
P=/home/noob/work/el-fault-detection/.venv/bin/python
HF_HUB_OFFLINE=1 $P reports/pf2/post_extra/pf2_scuffign.py --code /home/noob/work/el_f3 --m0 $OUT/m0 --out $OUT/m0_scuffign \
  --runs $(for r in $RUNS; do echo /home/noob/work/el_f3/experiments/$r; done)
