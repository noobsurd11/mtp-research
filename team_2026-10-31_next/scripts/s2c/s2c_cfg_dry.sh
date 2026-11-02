#!/bin/bash
# runner (3 Nov 2026): CPU-only dry check of s2c_queue.sh's cfgcheck rule on existing configs (no GPU, no training). Same diff
# command as s2c_queue.sh cfgcheck(): expect 'config OK' for pf2_SUPPF_100pct_s6 vs s5 with exp_SUPPF (empty) and seed 6, and for
# skr2_SKR01_100pct_s6 with exp_SKR01 (3fa67569) and seed 6; and expect FAIL for the crossed pairs (SKR01 config vs exp_SUPPF etc.).
# v2 (data root): with ROOTCFG=<s2c_check/databuild>, the checks run on the configs train.py will write under the root (seed 5):
# expect OK for each arm's own root config with its v2 exp file, FAIL for the crossed pairs and for the old no-root s6 configs.
D=${1:?dry dir with exp_SKR01.txt / exp_SUPPF.txt}; R0=/home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml
chk_f(){ local c=$1 k=$2 arm=$3 lab=$4 d e
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $R0) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(sort $D/exp_$arm.txt)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "OK   $lab as $arm seed $k"; else echo "FAIL $lab as $arm seed $k: [$(echo "$d" | tr '\n' ' ')]"; fi; }
chk(){ local c=$1 k=$2 arm=$3 d e
  d=$(diff <(grep -vE '^(run_name|seed):|^  experiments_dir:' $c) <(grep -vE '^(run_name|seed):|^  experiments_dir:' $R0) | grep -E '^[<>]' | sed -E 's/ +$//' | sort)
  e=$(sort $D/exp_$arm.txt)
  if [ "$d" = "$e" ] && grep -qx "seed: $k" $c; then echo "OK   $(basename $(dirname $c)) as $arm seed $k"; else echo "FAIL $(basename $(dirname $c)) as $arm seed $k: [$(echo "$d" | tr '\n' ' ')]"; fi; }
if [ -n "${ROOTCFG:-}" ]; then
  for c in SUPPF SKR01; do for arm in SUPPF SKR01; do chk_f $ROOTCFG/${c}_root_config.yaml 5 $arm "$c root config"; done; done
  chk /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s6/config_used.yaml 6 SUPPF
  chk /home/noob/work/el_thin/experiments/skr2_SKR01_100pct_s6/config_used.yaml 6 SKR01
  exit 0; fi
chk /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s6/config_used.yaml 6 SUPPF
chk /home/noob/work/el_thin/experiments/skr2_SKR01_100pct_s6/config_used.yaml 6 SKR01
chk /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s6/config_used.yaml 6 SKR01
chk /home/noob/work/el_thin/experiments/skr2_SKR01_100pct_s6/config_used.yaml 6 SUPPF
chk /home/noob/work/el_f3/experiments/pf2_SUPPF_100pct_s6/config_used.yaml 7 SUPPF
