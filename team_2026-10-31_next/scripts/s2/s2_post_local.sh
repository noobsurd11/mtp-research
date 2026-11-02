#!/bin/bash
# SKR2 + HC2 opening, runner's LOCAL readout (2 Nov 2026; respawned runner). Pattern of thin_post_local.sh a6369600.
# The pull is done already (results/s2/raw, MANIFEST bd671e26, md5sum -c OK on gaint and laptop; logs in results/s2/logs).
# This script only reads the pulled files. coach recomputes on his own; no verdict to team-lead before that.
# 1. re-check raw/ against its MANIFEST (expected md5 bd671e26) and record the md5s of the comparator m0 files;
# 2. test co-primaries per arm vs SUPPF (PF2's opened m0, results/pf2/raw/m0, reused unchanged): Track M m2_rung at tau 0
#    (verdict primaries; default .json = tau0, see raw/tau0_check_*.txt) and tau 1 (LA, reported). HC2 - HC (tau 0) as a
#    descriptive reference row (protocol §4);
# 3. collect the opening's frozen decision / reported text outputs, as written by the opening, into one readout file
#    (E1 co-primaries, B5 wide, guards G1-G3, SHV1 mechanism, F51, HC2 live synth readout, cosines, cell gate, scuff-ignored).
# Output results/s2/local/ + local_md5.txt. Reads no file outside results/{s2,pf2,hc}/raw and Track M's scripts.
set -eu
R=/home/yugma/mtp/research; T=$R/team_2026-10-31_next; D=$T/results/s2; RAW=$D/raw; O=$D/local
PY=$R/.venv/bin/python; M2=$R/team_2026-10-24_go/trackM/scripts/m2_rung.py; PM=$T/results/pf2/raw/m0; HM=$T/results/hc/raw/m0
[ "$(md5sum < $RAW/MANIFEST.md5 | cut -c1-8)" = bd671e26 ] || { echo "raw MANIFEST md5 != bd671e26"; exit 1; }
(cd $RAW && md5sum -c --quiet MANIFEST.md5) && echo "raw manifest OK $(wc -l < $RAW/MANIFEST.md5) files"
[ ! -e $O ] || { echo "$O exists (refuse to overwrite)"; exit 1; }
mkdir -p $O
md5sum $M2 > $O/tools_md5.txt
(cd $PM && md5sum pf2_SUPPF_100pct_s*.json) > $O/comparator_m0_md5.txt
(cd $HM && md5sum hc_HC_100pct_s*.json) > $O/hc_ref_m0_md5.txt
A=$(for k in 5 6 7 8 9; do echo $PM/pf2_SUPPF_100pct_s$k.json; done)
A1=$(for k in 5 6 7 8 9; do echo $PM/pf2_SUPPF_100pct_s$k.tau1.json; done)
B_SKR=$(for k in 5 6 7 8 9; do echo $RAW/m0/SKR01/skr2_SKR01_100pct_s$k.json; done)
B_HC2=$(for k in 5 6 7 8 9; do echo $RAW/m0/HC2/hc2_HCig_100pct_s$k.json; done)
$PY $M2 --label SKR01_vs_SUPPF --a $A --b $B_SKR > $O/m2_rung_SKR01.txt 2>/dev/null
$PY $M2 --label SKR01_vs_SUPPF_LA1 --a $A1 --b $(echo $B_SKR | sed 's/\.json/.tau1.json/g') > $O/m2_rung_SKR01_tau1.txt 2>/dev/null
$PY $M2 --label HC2_vs_SUPPF --a $A --b $B_HC2 > $O/m2_rung_HC2.txt 2>/dev/null
$PY $M2 --label HC2_vs_SUPPF_LA1 --a $A1 --b $(echo $B_HC2 | sed 's/\.json/.tau1.json/g') > $O/m2_rung_HC2_tau1.txt 2>/dev/null
$PY $M2 --label HC2_vs_HC_descriptive --a $(for k in 5 6 7 8 9; do echo $HM/hc_HC_100pct_s$k.json; done) --b $B_HC2 \
  > $O/m2_rung_HC2_vs_HC.txt 2>/dev/null
{
  echo "# SKR2 + HC2 opening: opening outputs collected by runner (frozen opening code wrote them; runner did not recompute these)"
  echo "# raw MANIFEST bd671e26; $(date '+%F %T')"
  for f in decision_rc.txt extra_rc.txt comparator_check.txt init_check.txt hc2_synth_readout.txt e1_coprim.txt b5/b5w_table.txt \
           guards.txt shv1/shv1_readout.txt f51/s2_f51.txt enc_cosine_20k.txt cellgate/s2_cellgate.txt tau0_check_SKR01.txt tau0_check_HC2.txt; do
    echo; echo "=================== $f ($(md5sum < $RAW/$f | cut -c1-8))"; cat $RAW/$f
  done
} > $O/opening_outputs.txt
(cd $O && md5sum *.txt) > $D/local_md5.txt
echo "local readout written to $O (verdicts only after coach's independent recompute)"
