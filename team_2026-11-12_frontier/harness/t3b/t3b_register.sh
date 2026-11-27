#!/bin/bash
# Registration of the T3b opening (E1 opening #9; T3B_RULE.md section 10). Run by the LEAD on gaint, ONCE, after the
# independent review and BEFORE any E1 file is staged, any T3b root built or any T3b queue placed. gaint only. CPU seconds.
# Reads E1 FILE HASHES only (md5sum; no mask, ignore or image is decoded) and copies the 106 E1 images into IO/stage.
# Writes IO (default /home/noob/work/bench_t3b_io; refuses if it exists):
#   jobs_train.txt / jobs_dump.txt (+ .md5)  = t3b_make_jobs.py --k K (33 training lines; 30 sealed dump lines)
#   stage/                 = images for the dump queue's DATA_S (no mask): e1_106/stems_eval.txt + e1_106/images/<106>.png,
#                            MANIFEST.md5 (md5sum of the 107 files, relative paths)
#   reg/e1_files.md5       = md5sum of images/, masks/, ignore/ <s>.png of the 106 E1 cells (318 lines; the builder's
#                            --e1-manifest: every E1 file the build decodes must be these bytes)
#   reg/zs.tsv             = the zero-shot comparator (opening #8 C2 seeds 5 to 7 on e1_106): per unit its relay .ok md5
#                            and the md5 of its relayed RUN.md5 (file hashes; the dumps are not opened)
#   reg/lists/             = copy of the frozen lists (LISTS.md5 pinned)
#   REGISTERED.txt         = the record (key value lines), REGISTERED.md5; everything made read-only. Its 'scripts' line
#                            (review round 1 B2) holds the reviewed md5 of every H3 script used after it: t3b_queue.sh,
#                            t3b_relay.sh, run_t3b_read.sh, t3b_verdict.py, t3b_rendercmp.py, diskguard8.sh, t3b_label_precheck.py;
#                            each refuses (the queue, relay and read for themselves, the read also for the verdict) unless
#                            its md5 is the one written there.
# Prints the md5 of REGISTERED.txt and the ledger row #9 and bullet for team_2026-10-31_next/e1_openings.md; the lead adds
# them BEFORE `t3b_queue.sh build` / `stage` (both refuse another REGISTERED.txt md5 than REG_MD5).
# Refuses: IO exists; T3B_RULE.md, t3b_make_jobs.py, LISTS.md5 or one of the 7 scripts above not the pinned md5 (and md5sum
#   -c of the lists); the ledger row would not fit the ledger table's header (checked BEFORE anything is written; N7); K not the
#   pinned commit with the pinned tree, F2 / G not its ancestors; the E1 list not 5266806b; an E1 file missing; opening #8's
#   REGISTERED.txt not 4c783a77; a ZS unit not relayed (no .ok, no 'relayed' line, RUN.md5 md5 != .ok).
# Test-only overrides (as opening_register.sh, review rounds 1 to 3): IO, EXT_DIR, RD_OPEN, OPEN_REG, REPO_K, K, SKIP_GIT,
#   RULE_MD5 other than the pin. If any is set the script refuses unless TEST_MODE=1; then REGISTERED.txt starts with a
#   'TEST MODE' line, which every later step refuses outside TEST_MODE. With TEST_MODE=1, IO, EXT_DIR, RD_OPEN and OPEN_REG
#   must be set, absolute, and resolve (symlinks followed) under /home/noob/work/bench_int_io, checked before any read,
#   hash or mkdir; no symlink inside those dirs may resolve outside it.
set -u
set -f
OV=""; for v in IO EXT_DIR RD_OPEN OPEN_REG REPO_K K SKIP_GIT; do [ -n "${!v+x}" ] && OV="$OV $v=${!v}"; done
RULE_PIN=0c006d4466f0312f4ca01184ea52a95a
[ -n "${RULE_MD5+x}" ] && [ "$RULE_MD5" != "$RULE_PIN" ] && OV="$OV RULE_MD5=$RULE_MD5"
if [ -n "$OV" ] && [ "${TEST_MODE:-0}" != 1 ]; then echo "REFUSED (register): test-only overrides set:$OV (unset them; TEST_MODE=1 only for dry runs)"; exit 1; fi
SCR_ROOT=/home/noob/work/bench_int_io
tm_no(){ echo "REFUSED (TEST_MODE guard): $*"; exit 1; }
tm_in(){ local r; case "$1" in /*) ;; *) tm_no "$1 is not an absolute path";; esac; r=$(readlink -m -- "$1"); case "$r/" in "$SCR_ROOT"/*/*) ;; *) tm_no "$1 resolves to $r, outside $SCR_ROOT";; esac; }
if [ "${TEST_MODE:-0}" = 1 ]; then
  for v in IO EXT_DIR RD_OPEN OPEN_REG; do [ -n "${!v+x}" ] && [ -n "${!v}" ] || tm_no "$v must be set explicitly to a path under $SCR_ROOT (its default is a production path)"; done
  for p in "$IO" "$EXT_DIR" "$EXT_DIR/stems_eval.txt" "$EXT_DIR/images" "$EXT_DIR/masks" "$EXT_DIR/ignore" "$RD_OPEN" "$OPEN_REG"; do tm_in "$p"; done
  for d in "$EXT_DIR" "$RD_OPEN"; do [ -d "$d" ] || continue
    for l in $(find "$d" -type l 2>/dev/null); do tm_in "$l"; done; done
fi
ME=$(readlink -f "$0"); HERE=$(dirname "$ME")
T=/home/yugma/mtp/research/team_2026-11-12_frontier
P=/home/noob/work/el-fault-detection/.venv/bin/python
IO=${IO:-/home/noob/work/bench_t3b_io}
EXT_DIR=${EXT_DIR:-/home/noob/work/el_f1/reports/f1/ext117}
RD_OPEN=${RD_OPEN:-/mnt/nas/noob_el_archive/bench_relay/open}
OPEN_REG=${OPEN_REG:-/home/noob/work/bench_open_io/REGISTERED.txt}
REPO_K=${REPO_K:-/home/noob/work/bench_wt_t3b}
# ---- pins (filled in by the build; the reviewer checks them)
RULE_MD5=${RULE_MD5:-$RULE_PIN}
MAKE_MD5=84649917b572e2201215cb8854de85ed
SCRIPT_PINS="run_t3b_read.sh=e4cda97aca7c3d2539bd3eecd14c845c t3b_verdict.py=7dee83d6634baba74c85df448d84f42f t3b_queue.sh=51a962379bd0399c2ae5a4c90b85bb7b t3b_relay.sh=2870fd4365c5d8b642119a37261d8b08 t3b_rendercmp.py=d6eec93f53818d3dbb0151845dac1ef4 diskguard8.sh=0fe96ad9b0208bf6381f2bc5ee7b60b4 t3b_label_precheck.py=214d087dbcca133768c1846913567113"
LISTS_MD5=5c86318a0d3c628bf3f9711fe7081fb5
K=${K:-cba7fbdf5df1579d6efb1168eb292e637bc9fad6}; K_TREE=b653389febe6fda63ce87e589859aa8605eef51f
F2=9967d59abaab03cef83c1e3014840b2359ef45d7; G=8bd1c2761c85f4721e444a8bf7124d2e5804973a; R=0c72cf942a5cc89accfcd02e1d2b443a033549d9
E1_LIST_MD5=5266806b559f74bcf9eae167bb076b95; OPEN8_REG=4c783a779208979ccbed8c13802950b2
ZS="fin_hrnet_swad_v11_pool_s5.swad.tta_d4.e1_106 fin_hrnet_swad_v11_pool_s6.swad.tta_d4.e1_106 fin_hrnet_swad_v11_pool_s7.swad.tta_d4.e1_106"
no(){ echo "REFUSED (register): $*"; exit 1; }
[ -e "$IO" ] && no "$IO exists (registration is made once)"
[ "$(md5sum < $HERE/T3B_RULE.md | cut -c1-32)" = "$RULE_MD5" ] || no "T3B_RULE.md is not the reviewed $RULE_MD5"
[ "$(md5sum < $HERE/t3b_make_jobs.py | cut -c1-32)" = "$MAKE_MD5" ] || no "t3b_make_jobs.py is not $MAKE_MD5"
for x in $SCRIPT_PINS; do [ "$(md5sum < $HERE/${x%%=*} | cut -c1-32)" = "${x#*=}" ] || no "${x%%=*} is not the reviewed ${x#*=}"; done
[ "$(md5sum < $HERE/lists/LISTS.md5 | cut -c1-32)" = "$LISTS_MD5" ] && (cd $HERE/lists && md5sum -c --quiet LISTS.md5 > /dev/null 2>&1) || no "lists are not LISTS.md5 $LISTS_MD5"
if [ "${SKIP_GIT:-0}" != 1 ]; then
  [ "$(git -C $REPO_K rev-parse "$K^{commit}" 2>/dev/null)" = "$K" ] && [ "$(git -C $REPO_K rev-parse "$K^{tree}")" = "$K_TREE" ] || no "K is not $K with tree $K_TREE"
  git -C $REPO_K merge-base --is-ancestor $F2 $K && git -C $REPO_K merge-base --is-ancestor $G $K || no "F2 and G must be ancestors of K"
fi
# ---- E1 list and files (hashes only), opening #8 and the zero-shot comparator units (hashes only)
[ "$(md5sum < $EXT_DIR/stems_eval.txt | cut -c1-32)" = "$E1_LIST_MD5" ] || no "E1 stems_eval.txt is not $E1_LIST_MD5"
cmp -s $EXT_DIR/stems_eval.txt $HERE/lists/e1_106_stems.txt || no "E1 stems_eval.txt differs from lists/e1_106_stems.txt"
E1S=$(grep . $EXT_DIR/stems_eval.txt); [ "$(echo "$E1S" | wc -l)" = 106 ] || no "E1 list size"
for s in $E1S; do [ -f $EXT_DIR/images/$s.png ] && [ -f $EXT_DIR/masks/$s.png ] && [ -f $EXT_DIR/ignore/$s.png ] || no "E1 file missing for $s"; done
[ "$(md5sum < $OPEN_REG 2>/dev/null | cut -c1-32)" = "$OPEN8_REG" ] || no "opening #8 REGISTERED.txt $OPEN_REG is not $OPEN8_REG"
ZT=""
for n in $ZS; do
  m=$(awk '{print $4}' $RD_OPEN/.ok/$n 2>/dev/null)
  [ -n "$m" ] && grep -q "relayed $n:" $RD_OPEN/relay.log 2>/dev/null && [ "$(md5sum < $RD_OPEN/$n/runs/$n/RUN.md5 2>/dev/null | cut -c1-32)" = "$m" ] || no "zero-shot unit $n not relayed in $RD_OPEN (.ok, relayed line, RUN.md5 md5)"
  ZT="$ZT$n	$m	$(md5sum < $RD_OPEN/.ok/$n | cut -c1-32)
"
done
# ---- the ledger row's shape against the table header, BEFORE anything is written (round 1 N7)
D=$(date '+%-d %b %Y %H:%M'); L1=$T/../team_2026-10-31_next/e1_openings.md
mkrow(){ echo "| 9 | T3B_RULE.md $RULE_MD5 (harness/t3b) | T3b: ALL = t3b_all_f0..4_s5..7, HALF = t3b_half_f0..4_s5..7 (C2 recipe HRNet-W18 U-Net++ + SWAD, swad, D4; trained on pool532_v11 + the E1 cells of the other 4 folds / a fixed half of them; out-of-fold dumps); beside: ZS = opening #8 C2 seeds 5 to 7 (zero-shot); t3b_deploy_s5..7 (532 + 106) never scored | primary: pooled OOF crack relF1@2 ALL - ZS, seed-aware two-stage bootstrap (71 clusters x 3 seeds), M 0.010; guards false crack px x1.5, mIoU-R13 -0.010; width reported | registered $D (REGISTERED.txt $1, jobs $2 / $3) | **registered, NOT opened** | |"; }
h=$(grep -m1 -F "| # | protocol | models |" "$L1" 2>/dev/null)
[ -n "$h" ] && [ "$(echo "$h" | awk -F'|' '{print NF}')" = "$(mkrow x y z | awk -F'|' '{print NF}')" ] || no "ledger row does not have the column count of the table header in $L1 (nothing written)"
# ---- write
mkdir -p $IO/reg/lists $IO/stage/e1_106/images || no "mkdir $IO"
CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 nice -n 19 $P $HERE/t3b_make_jobs.py --k $K --train $IO/jobs_train.txt --dump $IO/jobs_dump.txt || no "job lists"
md5sum < $IO/jobs_train.txt | cut -c1-32 > $IO/jobs_train.md5; md5sum < $IO/jobs_dump.txt | cut -c1-32 > $IO/jobs_dump.md5
cp $EXT_DIR/stems_eval.txt $IO/stage/e1_106/stems_eval.txt
for s in $E1S; do cp $EXT_DIR/images/$s.png $IO/stage/e1_106/images/; done
(cd $IO/stage && find . -type f ! -name MANIFEST.md5 -printf '%P\n' | LC_ALL=C sort | xargs -d '\n' md5sum > MANIFEST.md5 && md5sum -c --quiet MANIFEST.md5) || no "stage MANIFEST"
[ "$(grep -c . $IO/stage/MANIFEST.md5)" = 107 ] || no "stage MANIFEST must list 107 files (1 list + 106 images)"
(cd $EXT_DIR && for s in $E1S; do md5sum images/$s.png masks/$s.png ignore/$s.png; done) > $IO/reg/e1_files.md5
printf 'name\tok_md5_field\tok_file_md5\n%s' "$ZT" > $IO/reg/zs.tsv
for f in LISTS.md5 $(awk '{print $2}' $HERE/lists/LISTS.md5); do cp $HERE/lists/$f $IO/reg/lists/ || no "copy lists/$f"; done   # set -f: no glob
(cd $IO/reg/lists && md5sum -c --quiet LISTS.md5) && [ "$(md5sum < $IO/reg/lists/LISTS.md5 | cut -c1-32)" = "$LISTS_MD5" ] || no "reg/lists copy"
m(){ md5sum < $1 | cut -c1-32; }
{ [ "${TEST_MODE:-0}" = 1 ] && echo "TEST MODE (dry run, NOT a registration; overrides:${OV:- none})"
  echo "registered $(date '+%F %T %Z') by $(whoami)@$(hostname)"
  echo "opening_e1 E1 opening #9 e1_open9_t3b (T3b few-shot layout adaptation; E1 is training data of T3b models from this date)"
  echo "rule T3B_RULE.md $RULE_MD5"
  echo "lists LISTS.md5 $LISTS_MD5"
  echo "jobs_train $(cat $IO/jobs_train.md5) $(grep -c . $IO/jobs_train.txt) lines"
  echo "jobs_dump $(cat $IO/jobs_dump.md5) $(grep -c . $IO/jobs_dump.txt) lines"
  echo "commits K $K F2 $F2 G $G R $R"
  echo "stage_manifest $(m $IO/stage/MANIFEST.md5)"
  echo "e1_files $(m $IO/reg/e1_files.md5)"
  echo "zs $(m $IO/reg/zs.tsv) (opening #8 REGISTERED $OPEN8_REG; C2 seeds 5 6 7 on e1_106; relay $RD_OPEN)"
  echo "lists_e1 $E1_LIST_MD5"
  echo "scripts $SCRIPT_PINS "
} > $IO/REGISTERED.txt
m $IO/REGISTERED.txt > $IO/REGISTERED.md5
find $IO -type f -exec chmod a-w {} +
REG=$(cat $IO/REGISTERED.md5)
cat $IO/REGISTERED.txt
echo
echo "REGISTERED.txt md5 $REG  (IO $IO; nothing sealed is read beyond file hashes and the image copies)"
ROW=$(mkrow $REG $(cat $IO/jobs_train.md5) $(cat $IO/jobs_dump.md5))
echo "ledger row (7 columns), team_2026-10-31_next/e1_openings.md, 'Registered E1 openings' (after row 8):"
echo "$ROW"
echo "ledger bullet (after the #8 bullets):"
echo "- **#9 registered, NOT opened** (lead, $D IST): \`team_2026-11-12_frontier/harness/t3b/t3b_register.sh\` ($(m $ME | cut -c1-8)); gaint \`$IO/REGISTERED.txt\` **$REG**; rule T3B_RULE.md $RULE_MD5. **From this date E1 is training data for T3b models** (user, 21 Nov 2026 about 14:35 IST: \"run T3b on free GPUs\"); no later zero-shot claim on E1 by this team. Same 106 E1 cells: 5th look at the set; the zero-shot comparator is opening #8's C2 (seeds 5 to 7), re-scored, not re-dumped."
