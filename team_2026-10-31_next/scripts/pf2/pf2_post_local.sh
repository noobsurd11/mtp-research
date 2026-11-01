#!/bin/bash
# PF2 opening, local analysis (runner; coach recomputes independently): pull gaint el_f3/reports/pf2/post/ (MD5 checked) and
# gpumem.log to team_2026-10-31_next/results/pf2/, then
#   contrast PF2 = SUPPF - SUP (seeds 5-9) and RN = RN50PF - SUPPF: Track M m2_rung at tau 0 (verdict) and tau 1 (LA, reported);
#   ssl_rules cross-check on the rescore JSONs (pf2_ mapped to p93_ for ssl_rules.py);
#   E1 co-primaries, strata, crack precision, crack px on crack-free cells: pf2_e1_extra.py (md5 d404dd25, byte-checked successor);
#   E1 width-robust metrics (reported only, pf2_e1_width.py);
#   10-seed pooled descriptive table (seeds 0-9) for SUP / SUPPF: protocol_100 opening-1 m0 files + PF2.
set -eu
R=/home/yugma/mtp/research; T=$R/team_2026-10-31_next; D=$T/results/pf2; mkdir -p $D
PY=$R/.venv/bin/python; M2=$R/team_2026-10-24_go/trackM/scripts/m2_rung.py; CTX=$R/team_2026-10-29_features/scripts/e1_context.tsv
O1=$R/team_2026-10-29_features/results/f100/opening1/raw
rsync -a noob@172.18.22.20:/home/noob/work/el_f3/reports/pf2/post/ $D/raw/
(cd $D/raw && md5sum -c --quiet MANIFEST.md5) && echo "pf2 manifest OK $(wc -l < $D/raw/MANIFEST.md5) files"
rsync -a noob@172.18.22.20:/home/noob/work/el_f3/reports/pf2/gpumem.log noob@172.18.22.20:/home/noob/work/el_f3/reports/pf2/launch.log $D/
M=$D/raw/m0; ARMS=$(ls $M | grep -oE 'pf2_[A-Z0-9]+_100pct' | sort -u | sed 's/pf2_//; s/_100pct//' | tr '\n' ' ')
f(){ for k in 5 6 7 8 9; do echo $M/pf2_${1}_100pct_s$k$2.json; done; }
run(){ lab=$1 a=$2 b=$3
  $PY $M2 --label $lab --a $(f $a "") --b $(f $b "") > $D/m2_rung_${lab}.txt 2>/dev/null
  $PY $M2 --label ${lab}_LA1 --a $(f $a .tau1) --b $(f $b .tau1) > $D/m2_rung_${lab}_tau1.txt 2>/dev/null; }
run PF2 SUP SUPPF
case " $ARMS " in *" RN50PF "*) run RN SUPPF RN50PF;; esac
rm -rf $D/rules_in; mkdir -p $D/rules_in
for fj in $D/raw/rescore/pf2_*_100pct_s*.json; do
  sed 's/"\(test\|val\)\/pf2_/"\1\/p93_/g' $fj > $D/rules_in/$(basename $fj | sed 's/^pf2_/p93_/'); done
PAIRS="p93:SUPPF_100pct=p93:SUP_100pct"; AR="p93:SUP_100pct p93:SUPPF_100pct"
case " $ARMS " in *" RN50PF "*) PAIRS="$PAIRS p93:RN50PF_100pct=p93:SUPPF_100pct"; AR="$AR p93:RN50PF_100pct";; esac
$PY $R/scripts/ssl_rules.py --dirs $D/rules_in --arms $AR --pairs $PAIRS > $D/ssl_rules_pf2.txt
PREFIX=pf2 SEEDS="5 6 7 8 9" EXTRA=1 $PY $T/scripts/pf2/pf2_e1_extra.py $M $CTX $(for a in $ARMS; do echo $a=$M; done) > $D/pf2_e1_extra.txt
# E1 width-robust crack metrics (protocol_PF2 3b addendum; REPORTED ONLY): relR@2, relP@2, component recall / precision via
# Track M m0_analyze.agg (pf2_e1_width.py md5 241260db), per arm with rule-1 arithmetic for PF2 and RN, all 106 + strata.
# Predicted E1 crack width (area / skeleton) only if a frozen dump exists at the opening (calib); not computed here.
$PY $T/scripts/pf2/pf2_e1_width.py $M $CTX $ARMS --prefix pf2 --seeds 5 6 7 8 9 --contrasts SUPPF-SUP RN50PF-SUPPF > $D/pf2_e1_width.txt
# 10-seed pooled (descriptive): seeds 0-4 from protocol_100 opening 1 (f3_ names) + 5-9 (pf2_ names), via a renamed copy
P10=$D/pooled10_m0; rm -rf $P10; mkdir -p $P10
for a in SUP SUPPF; do for k in 0 1 2 3 4; do cp $O1/m0/f3_${a}_100pct_s$k.json $P10/p10_${a}_100pct_s$k.json; done
  for k in 5 6 7 8 9; do cp $M/pf2_${a}_100pct_s$k.json $P10/p10_${a}_100pct_s$k.json; done; done
PREFIX=p10 SEEDS="0 1 2 3 4 5 6 7 8 9" EXTRA=1 CONTRASTS="SUPPF-SUP" $PY $T/scripts/pf2/pf2_e1_extra.py $P10 $CTX SUP=$P10 SUPPF=$P10 > $D/pooled10_e1_descriptive.txt
echo "local analysis written to $D (verdicts only after coach's independent recompute)"
