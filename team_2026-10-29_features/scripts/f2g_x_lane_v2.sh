#!/bin/bash
# f2g lane X v2 (runner 29 Oct 20:3x; team-lead + coach rebalance: the MIM5 comparison first). X starts only after all
# 10 MIM5-experiment runs have launched, so it only takes slots MIM5 no longer needs; then as v1: CP smoke + decoy
# go/no-go, F2-DDeP gate, DDeP5 s0/2/4 (x_gates.sh md5 3a5f92bd unchanged).
cd /home/noob/work/el_f2
F1L=/home/noob/work/el_f1/reports/f1g/launch.log
until [ "$(grep -oE 'start f1_(A|MIM)_5pct_s[0-4] ' $F1L | sort -u | wc -l)" -ge 10 ]; do sleep 120; done
echo "[$(date)] lane X: all 10 MIM5-experiment runs launched; X proceeds" >> reports/f2g/launch.log
bash reports/f2g/x_gates.sh || exit 1
for k in 0 2 4; do bash reports/f2g/run_one.sh f2_DDeP_5pct_s$k $k 9000 model.decoder_init=/home/noob/work/cv02_noob_el/el_f2/experiments/f2_ddep_pre_s0/decoder_final.pth; done
