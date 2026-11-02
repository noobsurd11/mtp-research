#!/bin/bash
# runner (1 Nov 2026): the 20 B6 job lines (protocol_B6 v1.0.1 §3), "name|seed|arm|fold|opts", in dispatch order.
# Opts = the pf2_SUP_100pct_s5 (house) / pf2_SUPPF_100pct_s5 (PF) lines of gaint el_f3/reports/pf2/pf2_jobs.txt (md5 210d0d6f),
#   with ONLY seed=<5|6>, + data.root=<ROOTBASE>/b6_root_<k>, and run_name replaced. Nothing else changes (re-diff vs pf2 s5 =
#   data.root + seed, as §3 requires; the queue re-checks this per run from config_used.yaml).
# Names b6_{SUP,SUPPF}_f<k>_s<seed>. Order: seed 5 folds 0-4, then seed 6 folds 0-4, each fold as SUP then SUPPF, so both arms of
#   a (fold, seed) start next to each other and a wave of 15 lanes holds both arms of every pair it starts.
# Usage: PF2_JOBS=<local copy of pf2_jobs.txt> ROOTBASE=<absolute cv02 dir holding b6_root_0..4> OUT=<file> bash b6_make_jobs.sh
set -eu
J=${PF2_JOBS:?}; RB=${ROOTBASE:?}; OUT=${OUT:?}
[ "$(md5sum < "$J" | cut -c1-32)" = 210d0d6fcc54c3effcc36893e0d51ad5 ] || { echo "pf2_jobs.txt md5 mismatch" >&2; exit 2; }
case "$RB" in /*) ;; *) echo "ROOTBASE must be absolute" >&2; exit 2;; esac
base() { # arm -> opts of pf2_<arm>_100pct_s5 without seed=5 and run_name
  local l; l=$(grep "^pf2_$1_100pct_s5|" "$J" | cut -d'|' -f4); [ -n "$l" ]
  l=${l#seed=5 }; l=${l% run_name=pf2_$1_100pct_s5}
  case " $l " in *" seed="*|*" run_name="*|*" data.root="*) echo "unexpected key left in $1 opts" >&2; exit 2;; esac
  echo "$l"
}
SUP=$(base SUP); SUPPF=$(base SUPPF)
: > "$OUT"
for s in 5 6; do for k in 0 1 2 3 4; do
  echo "b6_SUP_f${k}_s$s|$s|SUP|$k|seed=$s $SUP data.root=$RB/b6_root_$k run_name=b6_SUP_f${k}_s$s" >> "$OUT"
  echo "b6_SUPPF_f${k}_s$s|$s|SUPPF|$k|seed=$s $SUPPF data.root=$RB/b6_root_$k run_name=b6_SUPPF_f${k}_s$s" >> "$OUT"
done; done
[ "$(wc -l < "$OUT")" = 20 ] && [ "$(cut -d'|' -f1 "$OUT" | sort -u | wc -l)" = 20 ]
md5sum "$OUT"
