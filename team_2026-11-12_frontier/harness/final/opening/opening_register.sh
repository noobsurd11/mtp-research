#!/bin/bash
# Registration of the sealed-set opening (OPENING_RULE.md section 9 step 3). Run by the LEAD on gaint, ONCE, after the
# independent review and BEFORE any sealed dump. gaint only; nothing on cv02. CPU seconds.
# Writes IO (default /home/noob/work/bench_open_io; refuses if it exists):
#   jobs.txt (+ jobs.md5)  = opening_make_jobs.py --c1d4 yes|no, decided by the fin CV5 TTA verdict (FINAL_RULE row (a)):
#                            'B5 TTA RESULT REPLICATED ON CV5V3 / CV02' -> yes; 'B5 TTA RESULT NOT REPLICATED' -> no; else refused
#   stage/                 = the sealed IMAGES for cv02 (no mask): e1_106/stems_eval.txt + e1_106/images/<106>.png,
#                            legacy/images/<50 test>.png, MANIFEST.md5 (md5sum of every file, relative paths)
#   reg/e1_masks.md5       = md5sum of ext117 masks/<s>.png and ignore/<s>.png of the 106 E1 cells (file hashes; no pixel read)
#   reg/masks_v0_test50.md5= md5sum lines '<md5>  <stem>.png' of labeled/masks_coded for the 50 test cells (cellmeta v0 format)
#   reg/t50_nolink.txt     = copy of the pinned list of the 16 test cells without a pool cell in their module
#   REGISTERED.txt         = the record (key value lines) and its md5 in REGISTERED.md5; everything made read-only.
# Prints the md5 of REGISTERED.txt and the two ledger rows; the lead adds them to e1_openings.md (#8) and test_openings.md (#19)
# as "registered, not opened" BEFORE deploying G or staging anything (the read refuses another REGISTERED.txt md5).
# Refuses: IO exists; OPENING_RULE.md, opening_make_jobs.py or t50_nolink.txt not the pinned md5; G or R not the pinned
#   commits with the pinned tree; the fin verdict missing or ambiguous; a FLAG D4 / FLAG C2 line in the fin verdict without
#   FLAGS_RULED (the lead's record of the lead's and user's ruling, e.g. 'keep: user 21 Nov hh:mm, candidates as approved');
#   a list md5 differs (E1 stems 5266806b, test.txt a31fad14); a sealed image or mask file missing; masks_v11 MANIFEST.md5 not 9c0e0687.
# Env: RULE_MD5 (= the pinned value below; any other value is a test-only override), FLAGS_RULED. Test-only overrides (review
#   round 1, N11): IO, FIN_VERDICT, G, R, EXT_DIR, LABELED_DIR, MASKS_V11_DIR, REPO_G, SKIP_GIT, RULE_MD5 other than the pin.
#   If any is set the script refuses, unless TEST_MODE=1: then REGISTERED.txt starts with a 'TEST MODE' line naming them,
#   which run_opening_read.sh refuses outside TEST_MODE (so a dry run can never stand for the registration). A fin verdict
#   with MECHANICS (test) lines is refused outside TEST_MODE. Round 2 (B2): with TEST_MODE=1, IO, FIN_VERDICT, EXT_DIR,
#   LABELED_DIR and MASKS_V11_DIR must all be set and resolve under /home/noob/work/bench_int_io (guard below).
# Ledger rows (N10): printed in the column format of the table they go into, each checked against that table's header row
#   (e1_openings.md: 7 columns; test_openings.md section B "Counted openings": 6 columns; section E "Benchmark openings": 7).
set -u
set -f
OV=""; for v in IO FIN_VERDICT G R EXT_DIR LABELED_DIR MASKS_V11_DIR REPO_G SKIP_GIT; do [ -n "${!v+x}" ] && OV="$OV $v=${!v}"; done
[ -n "${RULE_MD5+x}" ] && [ "$RULE_MD5" != 065a7dddfff2efd4897503561955093f ] && OV="$OV RULE_MD5=$RULE_MD5"
if [ -n "$OV" ] && [ "${TEST_MODE:-0}" != 1 ]; then echo "REFUSED (register): test-only overrides set:$OV (unset them; TEST_MODE=1 only for dry runs)"; exit 1; fi
# B2 (review round 2): under TEST_MODE every label, mask, ignore, image, relay, output and fin-verdict path must be set
#   explicitly and resolve (readlink -m, symlinks followed) under the scratch root SCR_ROOT, and no symlink inside those scratch
#   dirs may resolve outside it; checked here, before any read, hash or mkdir. A dry run can never reach the real data.
SCR_ROOT=/home/noob/work/bench_int_io
tm_no(){ echo "REFUSED (TEST_MODE guard): $*"; exit 1; }
tm_in(){ local r; case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac; r=$(readlink -m -- "$1"); case "$r/" in "$SCR_ROOT"/*/*) ;; *) tm_no "$1 resolves to $r, outside $SCR_ROOT";; esac; }   # B3: absolute paths only
if [ "${TEST_MODE:-0}" = 1 ]; then
  for v in IO FIN_VERDICT EXT_DIR LABELED_DIR MASKS_V11_DIR; do [ -n "${!v+x}" ] && [ -n "${!v}" ] || tm_no "$v must be set explicitly to a path under $SCR_ROOT (its default is a production path)"; done
  for p in "${IO:-}" "${FIN_VERDICT:-}" "${EXT_DIR:-}" "${EXT_DIR:-}/stems_eval.txt" "${EXT_DIR:-}/images" "${EXT_DIR:-}/masks" "${EXT_DIR:-}/ignore" "${LABELED_DIR:-}" "${LABELED_DIR:-}/images" "${LABELED_DIR:-}/masks_coded" "${MASKS_V11_DIR:-}" "${MASKS_V11_DIR:-}/MANIFEST.md5"; do tm_in "$p"; done
  for d in "$EXT_DIR" "$LABELED_DIR" "$MASKS_V11_DIR"; do [ -d "$d" ] || continue
    for l in $(find "$d" -type l 2>/dev/null); do tm_in "$l"; done; done
fi
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
P=/home/noob/work/el-fault-detection/.venv/bin/python
IO=${IO:-/home/noob/work/bench_open_io}
FIN_VERDICT=${FIN_VERDICT:-/home/noob/work/bench_reads/final_tta/verdict.txt}
EXT_DIR=${EXT_DIR:-/home/noob/work/el_f1/reports/f1/ext117}
LABELED_DIR=${LABELED_DIR:-/home/noob/work/el-fault-detection/data/labeled}
MASKS_V11_DIR=${MASKS_V11_DIR:-/home/noob/work/bench_data/masks_v11}
REPO_G=${REPO_G:-/home/noob/work/bench_wt_openg}
# ---- pins (filled in by the build; the reviewer checks them)
RULE_MD5=${RULE_MD5:-065a7dddfff2efd4897503561955093f}
MAKE_MD5=6ad871e03b78199de5cda704afe9b517
NOLINK_MD5=66f48dc371fbdf8bf95eb66287e74283
G=${G:-8bd1c2761c85f4721e444a8bf7124d2e5804973a}; G_TREE=38a8cdfdfd739e631547792e63dc4c1e707d21bb
R=${R:-0c72cf942a5cc89accfcd02e1d2b443a033549d9}; R_TREE=57eaeef9669ebb89524a3b960967b455490760e5
F=821dfadf49116cc6d5fdbd6697e263dd7cf0f834
F2=9967d59abaab03cef83c1e3014840b2359ef45d7; F2_TREE=adcdf7ec59ff30e7a714808ca94dd46e4a63628f   # fin2 resume deploy of the full-pool runs
E1_LIST_MD5=5266806b559f74bcf9eae167bb076b95; T50_LIST_MD5=a31fad14fa27ee28e2a2319b8976aba3; V11_MAN=9c0e0687
no(){ echo "REFUSED (register): $*"; exit 1; }
[ -e "$IO" ] && no "$IO exists (registration is made once)"
[ "$(md5sum < $HERE/OPENING_RULE.md | cut -c1-32)" = "$RULE_MD5" ] || no "OPENING_RULE.md is not the reviewed $RULE_MD5"
[ "$(md5sum < $HERE/opening_make_jobs.py | cut -c1-32)" = "$MAKE_MD5" ] || no "opening_make_jobs.py is not $MAKE_MD5"
[ "$(md5sum < $HERE/t50_nolink.txt | cut -c1-32)" = "$NOLINK_MD5" ] || no "t50_nolink.txt is not $NOLINK_MD5"
if [ "${SKIP_GIT:-0}" != 1 ]; then
  [ "$(git -C $REPO_G rev-parse "$G^{commit}" 2>/dev/null)" = "$G" ] && [ "$(git -C $REPO_G rev-parse "$G^{tree}")" = "$G_TREE" ] || no "G is not $G with tree $G_TREE"
  [ "$(git -C $REPO_G rev-parse "$R^{commit}" 2>/dev/null)" = "$R" ] && [ "$(git -C $REPO_G rev-parse "$R^{tree}")" = "$R_TREE" ] || no "R is not $R with tree $R_TREE"
  [ "$(git -C $REPO_G rev-parse "$G^1")" = "$F" ] || no "G's parent is not F"
  [ "$(git -C $REPO_G rev-parse "$F2^{commit}" 2>/dev/null)" = "$F2" ] && [ "$(git -C $REPO_G rev-parse "$F2^{tree}")" = "$F2_TREE" ] || no "F2 is not $F2 with tree $F2_TREE"
fi
# ---- the fin CV5 TTA verdict decides C1-D4 (FINAL_RULE section 4 row (a)); FLAGs need a recorded ruling
[ -s "$FIN_VERDICT" ] || no "fin verdict $FIN_VERDICT missing (the fin CV5 TTA read comes first)"
ya=$(grep -c "B5 TTA RESULT REPLICATED ON CV5V3 / CV02" "$FIN_VERDICT"); na=$(grep -c "B5 TTA RESULT NOT REPLICATED" "$FIN_VERDICT")
if [ "$ya" = 1 ] && [ "$na" = 0 ]; then C1D4=yes; elif [ "$ya" = 0 ] && [ "$na" = 1 ]; then C1D4=no; else no "fin verdict: row (a) decision not found exactly once"; fi
FL=$(grep -E "^(=> )?FLAG (D4|C2)|FLAG D4:|FLAG C2:" "$FIN_VERDICT" | head -3 | cut -c1-200)
if grep -q MECHANICS "$FIN_VERDICT" && [ "${TEST_MODE:-0}" != 1 ]; then no "fin verdict $FIN_VERDICT holds MECHANICS (test) lines"; fi
if [ -n "$FL" ] && [ -z "${FLAGS_RULED:-}" ]; then no "fin verdict holds a FLAG ($FL): set FLAGS_RULED to the recorded ruling of the lead and the user"; fi
# ---- lists
[ "$(md5sum < $EXT_DIR/stems_eval.txt | cut -c1-32)" = "$E1_LIST_MD5" ] || no "E1 stems_eval.txt is not $E1_LIST_MD5"
TL=$REPO_G/data/splits/test.txt
[ "$(md5sum < $TL | cut -c1-32)" = "$T50_LIST_MD5" ] || no "test.txt is not $T50_LIST_MD5"
[ "$(md5sum < $MASKS_V11_DIR/MANIFEST.md5 | cut -c1-8)" = "$V11_MAN" ] || no "masks_v11 MANIFEST.md5 is not $V11_MAN"
E1S=$(grep . $EXT_DIR/stems_eval.txt); T5S=$(grep . $TL | sort)
[ "$(echo "$E1S" | wc -l)" = 106 ] && [ "$(echo "$T5S" | wc -l)" = 50 ] || no "list sizes"
for s in $E1S; do [ -f $EXT_DIR/images/$s.png ] && [ -f $EXT_DIR/masks/$s.png ] && [ -f $EXT_DIR/ignore/$s.png ] || no "E1 file missing for $s"; done
for s in $T5S; do [ -f $LABELED_DIR/images/$s.png ] && [ -f $LABELED_DIR/masks_coded/$s.png ] || no "test50 file missing for $s"; done
# ---- write
mkdir -p $IO/reg $IO/stage/e1_106/images $IO/stage/legacy/images || no "mkdir $IO"
CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $HERE/opening_make_jobs.py --c1d4 $C1D4 $IO/jobs.txt || no "job list"
md5sum < $IO/jobs.txt | cut -c1-32 > $IO/jobs.md5
cp $EXT_DIR/stems_eval.txt $IO/stage/e1_106/stems_eval.txt
for s in $E1S; do cp $EXT_DIR/images/$s.png $IO/stage/e1_106/images/; done
for s in $T5S; do cp $LABELED_DIR/images/$s.png $IO/stage/legacy/images/; done
(cd $IO/stage && find . -type f ! -name MANIFEST.md5 -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' md5sum > MANIFEST.md5 && md5sum -c --quiet MANIFEST.md5) || no "stage MANIFEST"
[ "$(grep -c . $IO/stage/MANIFEST.md5)" = 157 ] || no "stage MANIFEST must list 157 files (1 list + 106 + 50 images)"
(cd $EXT_DIR && for s in $E1S; do md5sum masks/$s.png ignore/$s.png; done) > $IO/reg/e1_masks.md5
(cd $LABELED_DIR/masks_coded && for s in $T5S; do md5sum $s.png; done) > $IO/reg/masks_v0_test50.md5
cp $HERE/t50_nolink.txt $IO/reg/t50_nolink.txt
m(){ md5sum < $1 | cut -c1-32; }
{ [ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run, NOT a registration; overrides:${OV:- none})"
  echo "registered $(date '+%F %T %Z') by $(whoami)@$(hostname)"
  echo "opening_e1 E1 opening #8 e1_open8_final (e1_106, 106 cells)"
  echo "opening_t50 test50 opening #19 t50_open19_final (test50, 50 cells)"
  echo "rule OPENING_RULE.md $RULE_MD5"
  echo "jobs $(cat $IO/jobs.md5) $(grep -c . $IO/jobs.txt) lines"
  echo "c1d4 $C1D4 (fin verdict $(m $FIN_VERDICT))"
  echo "flags ${FL:-none} | ruled: ${FLAGS_RULED:-not needed}"
  echo "commits F $F G $G R $R"
  echo "runs F2 $F2 (deploy /tmp/noob_el/bench_9967d59: the 10 full-pool runs, steps 1 to 18,000 under F, the rest under F2 by the fin2 resume; FINAL_RULE_ADDENDUM_1.md)"
  echo "stage_manifest $(m $IO/stage/MANIFEST.md5)"
  echo "e1_masks $(m $IO/reg/e1_masks.md5)"
  echo "v0_test50 $(m $IO/reg/masks_v0_test50.md5)"
  echo "t50_nolink $(m $IO/reg/t50_nolink.txt)"
  echo "lists e1 $E1_LIST_MD5 t50 $T50_LIST_MD5 masks_v11 $(m $MASKS_V11_DIR/MANIFEST.md5)"
} > $IO/REGISTERED.txt
m $IO/REGISTERED.txt > $IO/REGISTERED.md5
find $IO -type f -exec chmod a-w {} +
REG=$(cat $IO/REGISTERED.md5)
cat $IO/REGISTERED.txt
echo
echo "REGISTERED.txt md5 $REG  (IO $IO; nothing sealed is read beyond file hashes and the image copies)"
D=$(date '+%-d %b %Y %H:%M'); L1=$T/../team_2026-10-31_next/e1_openings.md; L2=$T/benchmark/test_openings.md
X=$([ $C1D4 = yes ] && echo ', C1-D4')
E1ROW="| 8 | OPENING_RULE.md $RULE_MD5 (harness/final/opening) | C1 fin_pf_v11_pool_s5..9 (model, plain); C2 fin_hrnet_swad_v11_pool_s5..9 (swad, D4) = the final model; C3 = mean softmax of the 5 C2; beside: E-PF$X | primary: E1 crack relF1@2, C2 - C1, seed-aware two-stage bootstrap (71 clusters x seeds), M 0.010; guards width (pooled, CSIR), false crack px x1.5, mIoU-R13 -0.010; inactive reported | registered $D (REGISTERED.txt $REG, jobs $(cat $IO/jobs.md5)) | **registered, NOT opened** | |"
T5B="| 19 | final opening, test50 public table (harness/final/opening, rule $RULE_MD5; REGISTERED.txt $REG) | C1 fin_pf_v11_pool_s5..9 (plain), C2 fin_hrnet_swad_v11_pool_s5..9 (swad, D4)$X | public table only, decides nothing: Pratt median IoU rules A/B/C, PV-S3 both background rules, SEiPV family on v0; protocol card on v1.1 (all 50, clean 49, 16 without module link); C2 - C1 relF1@2 secondary | registered $D, **NOT opened** | |"
T5E="| 19 | final opening, test50 public table (harness/final/opening, rule $RULE_MD5) | C1 fin_pf_v11_pool_s5..9 (plain), C2 fin_hrnet_swad_v11_pool_s5..9 (swad, D4)$X | test50 (v0 and v1.1): public table only, decides nothing; C2 - C1 relF1@2 secondary | $D (REGISTERED.txt $REG) | **NOT opened** | |"
ncol(){ echo "$1" | awk -F'|' '{print NF}'; }
hdr(){ grep -m1 -F "$2" "$1" 2>/dev/null; }
for x in "E1ROW|$L1|| # | protocol | models |" "T5B|$L2|| # | Protocol (team) | Models |" "T5E|$L2|| # | Protocol | Models | Sets and primaries |"; do
  n=${x%%|*}; r=${x#*|}; f=${r%%||*}; h=$(hdr "$f" "${r#*||}")
  [ -n "$h" ] && [ "$(ncol "$h")" = "$(ncol "${!n}")" ] || no "ledger row $n does not have the column count of its table header in $f"
done
echo "ledger row (7 columns), team_2026-10-31_next/e1_openings.md, 'Registered E1 openings':"
echo "$E1ROW"
echo "ledger row (6 columns), benchmark/test_openings.md section B 'Counted openings' (where #1 to #18 are):"
echo "$T5B"
echo "the same as a section E 'Benchmark openings' row (7 columns), if the lead puts #19 there:"
echo "$T5E"
